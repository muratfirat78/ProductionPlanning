
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

gitfolder = 'https://raw.githubusercontent.com/muratfirat78/ProductionPlanning/refs/heads/main/'
module_files =  ['stochastic.py','simulationobjects.py','simulator.py','visual.py','controller.py', 'productionobjects.py','productionalgs.py','productiondata.py','productionmain.py','MILPScheduling.py'
                , 'logisticsobjects.py','logisticsalgs.py','logisticsmain.py','logisticsdata.py']

source_directory ='/content/'
usecase_files =  ['Production_Decisions.csv','Production_EventTypes.csv','Production_PrecedenceInfo.csv']
input_files =  ['Resources_2026-09-14.csv','Production Orders_2026-09-14.csv']

downloads = dict(); downloads[gitfolder+'src/'] =  module_files; downloads[gitfolder+'usecases/'] =  usecase_files
downloads[gitfolder+'Production/'] =  input_files

