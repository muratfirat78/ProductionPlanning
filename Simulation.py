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
from Simulator import *
from SimulatorM import *

#######################################################################################################################

class SimJob(object):
    def __init__(self,env,job): 
        self.env = env
        self.myJob = job
        self.processstime = 0 # to be updated
        self.assignedresource = None
        self.SimProducts = []

    def getJob(self):
        return self.myJob 

    def getProducts(self):
        return self.SimProducts

    def SampleProcessTime(self):
       processtime = 0
       # use some sampling here
       return processtime
        




class SimMachine(object):
    def __init__(self, env,machine):
        self.env = env
        self.machine = machine
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
    def __init__(self,env,Job,SN):
        self.env = env
        self.Job = Job
        self.SN = SN
        self.Tray = None
        self.location = None

    def setLocation(self,lc):
        self.location = lc
        return
    def getLocation(self):
        return self.location
    

    

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
    def __init__(self,env,name,capacity):
        self.env = env
        self.name = name
        self.capacity = capacity
        self.products = []
      
        
        # historical capacity use
        #self.capacityuse = [] # list of pairs (time,capacityuse)
        #self.capacityuse.append((env.now,0))
    def getProducts(self):
        return self.products
    def getCapacity(self):
        return self.capacity
   


class Box(object):
    def __init__(self,myid): 
        self.ID = myid
        self.products = []
        self.location = None # locations are buffers 
        self.capacity = 10000 # later to be changed with real value
        self.location = None # buffer
        
    def getProducts(self):
        return self.products

class ProductionManager(object):
    def __init__(self,name,ProdSystem):
        self.name = name
        self.prodsystem = ProdSystem
        self.ProdPlan = dict() # keys: Shift, values: [(PO,t)]
        self.Operators = dict() # key: Oprtr.ID, val: Operator


        
class ProductionSystem(object): 
    def __init__(self,name):
        self.name = name
        self.machines = []
        self.operators = []
        


class SimulationManager(object):
    def __init__(self): 

        self.DataManager = None
        self.VisualManager = None
        self.PlanningManager = None
        self.SchedulingManager = None
        self.SimStart = None
        self.SimEnd = None
        self.TaskList = [] # Tasks are included in the list with some priority ordering
        self.ProdSN = 0

    def getProdSN(self):
        self.ProdSN+=1
        return self.ProdSN

    def getVisualManager(self):
        return self.VisualManager
    def setVisualManager(self,myvm):
        self.VisualManager = myvm
        return
    def getDataManager(self):
        return self.DataManager
    def setDataManager(self,myvm):
        self.DataManager = myvm
        return

    def getSimStart(self):
        return self.SimStart
    def setSimStart(self,myvm):
        self.SimStart = myvm
        return
 
    def getSimEnd(self):
        return self.SimEnd
    def setSimEnd(self,myvm):
        self.SimEnd = myvm
        return

    def createBuffer(self,env,name,cap):
        return Buffer(env,name,cap)

    def createMachine(self,env,machine):
        return SimMachine(env,machine)

    def createJob(self,env,job):
        return SimJob(env,job)

    def createProduct(self,env,job,SN):
        return SimProduct(env,job,SN)
    
    def StartSimulation(self,simtype):

        if simtype == "SimCommon":
            SimLator = Simulator()
            SimLator.setSimulationManager(self)
            simreturn = SimLator.RunSimulation() 
        if simtype == "SimM":
            SimLator = SimulatorM()
            SimLator.setSimulationManager(self)
            simreturn = SimLator.RunSimulation() 

     
        return 


#------------------------------------------------------------------------------------------        
       

  
