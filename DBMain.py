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
from VisSchedule import *
from Visual import *
from Data import *
from Planning import *
from Scheduling import *

ScheduleTab = ScheduleTab()
DataMgr = DataManager()
VisMgr = VisualManager()
VisMgr.setDataManager(DataMgr)
VisMgr.setSchedulingTab(ScheduleTab)
ScheduleTab.setVisualManager(VisMgr)
DataMgr.setVisualManager(VisMgr)
PlanningMgr = PlanningManager()
PlanningMgr.setDataManager(DataMgr)
PlanningMgr.setVisualManager(VisMgr)
VisMgr.setPlanningManager(PlanningMgr)
SchedulingMgr = SchedulingManager()
SchedulingMgr.setDataManager(DataMgr)
SchedulingMgr.setVisualManager(VisMgr)
SchedulingMgr.setPlanningManager(PlanningMgr)
VisMgr.setSchedulingManager(SchedulingMgr)

