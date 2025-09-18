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
from VisSimulation import *
from VisProductionProgress import *
from Visual import *
from Data import *
from Planning import *
from Scheduling import *
from Simulation import *

ScheduleTab = ScheduleTab()
SimTab = SimulationTab()
ProductionProgressTab = ProductionProgressTab()
DataMgr = DataManager()
VisMgr = VisualManager()
SimMgr = SimulationManager()

VisMgr.setDataManager(DataMgr)
VisMgr.setSchedulingTab(ScheduleTab)
VisMgr.setSimulationTab(SimTab)
VisMgr.setProductionProgressTab(ProductionProgressTab)
VisMgr.setSimulationManager(SimMgr)

ScheduleTab.setVisualManager(VisMgr)
SimMgr.setVisualManager(SimTab)
SimTab.setVisualManager(VisMgr)
ProductionProgressTab.setVisualManager(VisMgr)
SimMgr.setDataManager(DataMgr)

DataMgr.setVisualManager(VisMgr)
DataMgr.setSimulationManager(SimMgr)


PlanningMgr = PlanningManager()
PlanningMgr.setDataManager(DataMgr)
PlanningMgr.setVisualManager(VisMgr)
VisMgr.setPlanningManager(PlanningMgr)
SchedulingMgr = SchedulingManager()
SchedulingMgr.setDataManager(DataMgr)
SchedulingMgr.setVisualManager(VisMgr)
SchedulingMgr.setPlanningManager(PlanningMgr)
VisMgr.setSchedulingManager(SchedulingMgr)
DataMgr.setSchedulingManager(SchedulingMgr)

