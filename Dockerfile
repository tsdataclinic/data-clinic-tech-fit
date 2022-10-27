FROM ubuntu:22.04
RUN apt-get -y update 
RUN apt-get install -y git 
RUN apt-get install -y wget 
RUN apt-get -y install make
RUN apt-get install -y libspatialindex-dev

RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash Miniconda3-latest-Linux-x86_64.sh -b -p /miniconda
ENV PATH=$PATH:/miniconda/pcondabin:/miniconda/bin

COPY src/ .
COPY data/ . 
COPY environment.yml .
COPY Makefile . 
COPY requirements.txt .

RUN conda env create -f environment.yml
# SHELL ["conda","run","-n","myenv","/bin/bash","-c"]
RUN conda init
RUN echo 'conda activate myenv' >> ~/.bashrc
RUN pip3 install -r requirements.txt
RUN rm Miniconda3-latest-Linux-x86_64.sh

EXPOSE 80
EXPOSE 8888

WORKDIR technical_test/

