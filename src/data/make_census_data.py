import requests
import os
from pathlib import Path
from zipfile import ZipFile
import geopandas as gpd
import json
import argparse
import pandas as pd

"""
Product: ACS 2020 5-year
Geographies: census tract, NECTA, PUMA, MCD

*Suffix definitions*
PE = “PE” refers to an estimate representing a percent
of the total.
PM = “PM” refers to the margin of error for a percentage. 
E = “E” refers to a numeric representation of the ACS
estimate. 
EA = estimate annotations
M = “M” refers to a numeric representation of the margin of error
MA = margin of error annotations

*Table Types*
Detailed Tables contain the most detailed cross-tabulations, some of which are published down to block groups. These data are population counts only. There are over 20,000 variables in this dataset.
Subject Tables provide an overview of the estimates available in a particular topic.  These data are presented as population counts and percentages.  There are over 18,000 variables in this dataset. 
Data Profiles contain broad social, economic, housing, and demographic information. The data are presented as population counts and percentages. There are over 1,000 variables in this dataset.
https://api.census.gov/data/2020/acs/acs5/subject/variables.json
https://www.census.gov/programs-surveys/acs/guidance/subjects.html
"""

def check_directory_structure_and_return_path(name: str):
    BasePath = Path(os.path.abspath(os.curdir)) / "data"
    DataRaw = BasePath / "raw" / name
    DataIntermediate = BasePath / "interim" / name
    DataProcessed = BasePath / "processed" / name
    for dir in [DataRaw, DataIntermediate, DataProcessed]:
        dir.mkdir(exist_ok=True, mode=0o777)
    return DataRaw, DataIntermediate, DataProcessed

def get_tiger_geoms_and_census_vars(group_id, geometry_level):
    raw_path, interim_path, processed_path = check_directory_structure_and_return_path(geometry_level)
    url = format_and_return_url(selection = geometry_level)
    file_name = "tiger_zip.zip"
    file_path = raw_path / file_name
    def get_vars():
        if does_path_exist(interim_path / f"{group_id}.csv") is True:
            print(f"{group_id} is already available in the project directory.")
        else:
            df = get_census_variables_group_call(group_id, geometry_level)
            df.to_csv(interim_path / f"{group_id}.csv")
            print(f"{group_id} now available in the project directory")
    if does_path_exist(raw_path / file_name) is True:
        print(f"{geometry_level} is already available in the project directory.")
        get_vars()
    else:
        print(f"Downloading {geometry_level} shape file...")
        with open((file_path), 'wb') as f:
            shapes = requests.get(url, verify=False)
            f.write(shapes.content)
        try:
            ZipFile(file_path).extractall(interim_path)
        except:
            print (f"Issue unziping raw tiger geometry file for {geometry_level}")
        shape_file = [p for p in interim_path.rglob('*.shp')][0]
        geoms = gpd.read_file(shape_file)
        geoms = geoms.to_crs("EPSG:4326").to_file(processed_path / f"census_geom_{geometry_level}.geojson",driver='GeoJSON')
        get_vars()

def does_path_exist(path):
    return os.path.exists(path)

def format_and_return_url(selection):
    if selection == "NECTA":
        url = "https://www2.census.gov/geo/tiger/TIGER2020/NECTA/tl_2020_us_necta.zip"
    elif selection == "PUMA":
        url = "https://www2.census.gov/geo/tiger/TIGER2020/PUMA/tl_2020_25_puma10.zip"
    elif selection == "tract":
        url = "https://www2.census.gov/geo/tiger/TIGER2020/TRACT/tl_2020_25_tract.zip"
    elif selection == "MCD":
        url = "https://www2.census.gov/geo/tiger/TIGER2020/COUSUB/tl_2020_25_cousub.zip"
    elif "place":
        url = "https://www2.census.gov/geo/tiger/TIGER2020/PLACE/tl_2020_25_place.zip"
    return url

def get_census_variables_group_call(group_id, geometry_level):
    switch_case = {
        "S" : "subject",
        "D" : "profile",
        "PUMA" : "public%20use%20microdata%20area:*&in=state:25",
        "tract" : "tract:*&in=state:25&in=county:*",
        "NECTA" : "new%20england%20city%20and%20town%20area:*",
        "place": "place:*&in=state:25",
        "MCD": "subminor%20civil%20division:*&in=state:25%20county:127%20county%20subdivision:*",
        }
    
    table_type = switch_case.get(group_id[0])
    if table_type is None:
        raise ValueError(f"You've provided an unsupported group table. The group id passed into the API call must belong to a subject or data profile table.")
    elif geometry_level is None:
        raise ValueError("You've provided an unsupported geography. Supported geographies are NECTA, PUMA, and tract.")
    else:
        geog = switch_case.get(geometry_level)
        api_call = f"https://api.census.gov/data/2020/acs/acs5/{table_type}?get=group({group_id})&for={geog}"
        r = requests.get(api_call).json()
        df = pd.DataFrame(r[1:],columns=r[0])
    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--group_id', type=str, required=True)
    parser.add_argument('--geometry_level', type=str, required=True)
    args = parser.parse_args()
    get_tiger_geoms_and_census_vars(args.group_id, args.geometry_level)