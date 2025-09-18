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
             


       
    def RunSimulation(self):

        self.getVisualManager().getPSchScheRes().value+="Simulation starts.."+"\n"

        self.getVisualManager().getPSchScheRes().value+="Simulation period"+str(self.getSimStart())+"-"+str(self.getSimEnd())+"\n"

        env = simpy.Environment()

        CentralBuffer = Buffer(env,"CentralBuffer",10000000)

        self.getVisualManager().getPSchScheRes().value+="Central buffer created with cap.."+str(CentralBuffer.getCapacity())+"\n"

        self.getDataManager().getSchedulingManager().CreateShifts(self.getSimStart(),self.getSimEnd(),False)

        self.getVisualManager().getPSchScheRes().value+="Customer orders.."+str(len(self.getDataManager().getCustomerOrders()))+"\n"

        for name,order in self.getDataManager().getCustomerOrders().items():
            #self.getVisualManager().getPSchScheRes().value+="Customer order.."+str(name)+"\n"
            for job in order.getMyJobs():
                #self.getVisualManager().getPSchScheRes().value+="job.."+str(job.getName())+"\n"
                job.initializeSimJob()
                #self.getVisualManager().getPSchScheRes().value+="job..Q"+str(job.getQuantity())+"\n"
                for prd in range(int(job.getQuantity())):
                    simprod = SimProduct(env,job,self.getProdSN())
                    job.getSimJob().getSimProducts().append(simprod)
                    simprod.setLocation(CentralBuffer)
                    CentralBuffer.getProducts().append(simprod)


        
        self.getVisualManager().getPSchScheRes().value+="Central buffer has "+str(len(CentralBuffer.getProducts()))+" products initially"+"\n"
            
           

        st = time.time() # get the start time
        planninghorizon = (self.getSimEnd() -self.getSimStart()).days  # days
        weekno = self.getSimStart().isocalendar()[1]
        #d = "2025-W"+str(weekno)
        #weekstart = datetime.datetime.strptime(d + '-1', "%Y-W%W-%w")

        self.getVisualManager().getPSchScheRes().value+="Simulation week start "+str(weekno)+", days: "+str(planninghorizon)+"\n"

        completiontime = 1440*planninghorizon   # Sim time in minutes

        env.process(SystemClock(env))
 
        # Execute
        env.run(until = completiontime)
        self.getVisualManager().getPSchScheRes().value+= '-> Execution time: '+str(round(time.time() - st,2))+' seconds'
     
        return infotxt


#------------------------------------------------------------------------------------------        
       

  
