# -*- coding: utf-8 -*-

##### import ipywidgets as widgets
from IPython.display import clear_output
from IPython import display
from ipywidgets import *
from datetime import timedelta,date,datetime,time
import matplotlib.pyplot as plt
import warnings
import seaborn as sns
import os
import pandas as pd
import warnings
import sys
import numpy as np
import math as mth
from PlanningObjects import *
from Visual import *
from Data import *
from GreedyInsertion import *
import simpy
from numpy import random
import pandas as pd 
import numpy as np
import math
import datetime
import time
from datetime import timedelta,date

#######################################################################################################################

class Task(object):
    def __init__(self,mytype,myname,evtime): 
        self.type = mytype
        self.name = myname
        self.processstime = 0 # to be updated
        self.plannedtime = evtime
        self.assignedresource = None

    def SampleProcessTime(self):
       processtime = 0
       # use some sampling here
       return processtime
        
        

def SystemClock(env):
   
    while True:

        unit_time = 0.01 # this is one minute 
        
        yield env.timeout(unit_time)
        
        
    return 


class SimulationManager(object):
    def __init__(self): 

        self.DataManager = None
        self.VisualManager = None
        self.PlanningManager = None
        self.SchedulingManager = None
        self.TaskList = [] # Tasks are included in the list with some priority ordering

    def getVisualManager(self):
        return self.VisualManager
    def setVisualManager(self,myvm):
        self.VisualManager = myvm
        return

        

    def RunSimulation(self):

        self.getVisualManager().getPSchScheRes().value+="Simulation starts.."+"\n"

        env = simpy.Environment()

        st = time.time() # get the start time
        planninghorizon = 5 # days
        weekno = 38
        d = "2025-W"+str(weekno)
        weekstart = datetime.datetime.strptime(d + '-1', "%Y-W%W-%w")

        self.getVisualManager().getPSchScheRes().value+="Simulation week start"+str(weekstart)+"\n"

        completiontime = 1440*planninghorizon   # Sim time in minutes

    
        env.process(SystemClock(env))

        self.getVisualManager().getPSchScheRes().value+="Simulation before run.."+"\n"
 
        # Execute
        env.run(until = completiontime)
        infotxt = '-> Execution time: '+str(round(time.time() - st,2))+' seconds'
     
        return infotxt


#------------------------------------------------------------------------------------------        
       
class SimMachine(object):
    def __init__(self, env, name,speed):
        self.env = env
        self.name = name
        self.speed = speed
        self.location = None 
        self.inputbuffer = None
        self.outputbuffer = None

    
    def ProcessTask(self,env,task):
        # make status change idle->busy
        # register start of task
        # determine/sample task process time
        # register completion of task
        return



class SimProduct(object):   
    def __init__(self,env,PN,Order,SN):
        self.env = env
        self.Order = PO
        self.SN = SN
        self.PN = PN
        self.Tray = None

    

class SimOperator(object):
    def __init__(self, env,name,myid):
        self.env = env
        self.name = name
        self.ID = myid     
        self.efficiency = 1
        self.operationexecutions = []
        self.location = None 
        self.status = 'idle'
        self.currentexecution = None
        self.availability = dict() #  key: day, value: activeperiod. 
        print('name: ',self.name,' comptence ',self.competence)
        
    def StartTask(self,env,task):
        # make status change idle->busy
        # sample proccess time
        # input buffer -> machine
        
        return
        
    def ProcessTask(self,env,task):
        # make status change idle->busy
        # register start of task
        # determine/sample task process time
        # register completion of task
        return

    def CompleteTask(self,env,task):
        # make status change: busy->idle
        # sample proccess time
        # update location of items in the task: machine->output buffer
        return
        

class Buffer(object):   
    def __init__(self,env,name,capacity,out,start,end):
        self.env = env
        self.name = name
        self.capacity = capacity
        self.items = []
        self.out = out
        self.end = end
        # historical capacity use
        self.capacityuse = [] # list of pairs (time,capacityuse)
        self.capacityuse.append((env.now,0))


class Tray(object):
    def __init__(self,myid): 
        self.ID = myid
        self.Box = None
        self.products = []

class Box(object):
    def __init__(self,myid): 
        self.ID = myid
        self.trays = []
        self.location = None # buffer
        

       


  
