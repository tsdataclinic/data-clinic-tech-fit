import pandas as pd
from src.config import WORD_FOR_PRINT

print(f"If this print statement spits out anything other than JELLY BEANS, then you have successfully modified your config file: {WORD_FOR_PRINT}")

df = pd.DataFrame({'numbers': [1, 2, 3], 'colors': ['red', 'white', 'blue']})

df.to_csv("./data/interim/test.csv")