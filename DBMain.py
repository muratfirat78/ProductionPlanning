# -*- coding: utf-8 -*-

##### import ipywidgets as widgets
from IPython.display import clear_output
from IPython import display
from ipywidgets import *
from datetime import timedelta,date
import matplotlib.pyplot as plt
import warnings
import seaborn as sns
import os
import pandas as pd
import warnings
import sys
import numpy as np
from pathlib import Path
from Visual import *
from Data import *
from Planning import *

DataMgr = DataManager()
VisMgr = VisualManager()
VisMgr.setDataManager(DataMgr)
DataMgr.setVisualManager(VisMgr)
PlanningMgr = PlanningManager()
PlanningMgr.setDataManager(DataMgr)
PlanningMgr.setVisualManager(VisMgr)
VisMgr.setPlanningManager(PlanningMgr)
