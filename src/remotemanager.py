
from google.colab import auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from IPython.utils.process import shutil
import os, json
import gdown
import warnings
import google.auth
from google.colab import files

import httplib2
from google.auth import default as get_default_credentials
from google_auth_httplib2 import AuthorizedHttp


gitfolder = 'https://raw.githubusercontent.com/muratfirat78/ProductionPlanning/refs/heads/main/usecases/'
source_directory ='/content/'

!wget https://raw.githubusercontent.com/muratfirat78/ProductionPlanning/refs/heads/main/src/stochastic.py
!wget https://raw.githubusercontent.com/muratfirat78/ProductionPlanning/refs/heads/main/src/simulationobjects.py
!wget https://raw.githubusercontent.com/muratfirat78/ProductionPlanning/refs/heads/main/src/productionobjects.py
!wget https://raw.githubusercontent.com/muratfirat78/ProductionPlanning/refs/heads/main/src/productionalgs.py
!wget https://raw.githubusercontent.com/muratfirat78/ProductionPlanning/refs/heads/main/src/productiondata.py
!wget https://raw.githubusercontent.com/muratfirat78/ProductionPlanning/refs/heads/main/src/MILPScheduling.py
!wget https://raw.githubusercontent.com/muratfirat78/ProductionPlanning/refs/heads/main/src/logisticsobjects.py
!wget https://raw.githubusercontent.com/muratfirat78/ProductionPlanning/refs/heads/main/src/logisticsalgs.py
!wget https://raw.githubusercontent.com/muratfirat78/ProductionPlanning/refs/heads/main/src/logisticsdata.py
!wget https://raw.githubusercontent.com/muratfirat78/ProductionPlanning/refs/heads/main/src/productionmain.py
!wget https://raw.githubusercontent.com/muratfirat78/ProductionPlanning/refs/heads/main/src/logisticsmain.py
!wget https://raw.githubusercontent.com/muratfirat78/ProductionPlanning/refs/heads/main/src/simulator.py
!wget https://raw.githubusercontent.com/muratfirat78/ProductionPlanning/refs/heads/main/src/visual.py
!wget https://raw.githubusercontent.com/muratfirat78/ProductionPlanning/refs/heads/main/src/controller.py


input_files =  ['Production_Decisions.csv','Production_EventTypes.csv','Production_PrecedenceInfo.csv']

for filename in input_files:
    if not filename in os.listdir(source_directory):
      !wget "{gitfolder}{filename}"



