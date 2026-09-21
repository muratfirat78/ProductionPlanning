
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
module_files =  ['stochastic.py','simulationobjects.py','simulator.py','visual.py','controller.py'
                , 'productionobjects.py','productionalgs.py','productiondata.py','productionmain.py','MILPScheduling.py'
                , 'logisticsobjects.py','logisticsalgs.py','logisticsmain.py','logisticsdata.py']

srcfolder = gitfolder+'src/'
usecasefolder = gitfolder+'usecases/'
source_directory ='/content/'
input_files =  ['Production_Decisions.csv','Production_EventTypes.csv','Production_PrecedenceInfo.csv']



    return
    



