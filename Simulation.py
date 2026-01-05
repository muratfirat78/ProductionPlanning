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

class SimEvent(object):
    def __init__(self, env,regtime,prod,frm,to,mytype):

        self.Regtime = regtime
        self.Type = mytype
        self.Start = None
        self.Completed = None
        self.From = frm
        self.To = to
        self.ProcessTime = None
        self.product = prod

    def getRegtime(self):
        return self.Regtime

    def getProduct(self):
        return self.product

    def setProcessTime(self,mytm):
        self.ProcessTime = mytm
        return
    def getProcessTime(self):
        return self.ProcessTime

    def getType(self):
        return self.Type


class SimMachine(object):
    def __init__(self, env,machine):
        self.env = env
        self.name = machine.getName()
        self.machine = machine
        self.type = 'Machine'
        self.FTERequirement = machine.FTERequirement
        self.coordinates = (0,0)
        self.inputbuffer = None
        self.outputbuffer = None
        self.Automated = machine.Automated
        self.SchedulableWindow = [(480,960),(960,1440)] #This is the window that allows jobs to start each day
        self.Resource = simpy.Resource(env,capacity=1)
  

    def getCoordinates(self):
        return self.coordinates 

    def getResource(self):
        return self.Resource
    
    def ProcessTask(self,env,task):
        # make status change idle->busy
        # register start of task
        # determine/sample task process time
        # register completion of task
        return

    def getName(self):
        return self.name

    def IsOpen(self,now):
        time = now % 1440 #Each day has 1440 minutes            
        return any(start<= time < end for start,end in self.SchedulableWindow)

    def getFTERequirement(self):
        if self.Automated == True:
            return 0.1
        else:
            return 0.3

class SimProduct(object):   
    def __init__(self,env,Job,SN):
        self.env = env
        self.Job = Job
        self.SN = SN
        self.Tray = None
        self.location = None
        self.currentjob = None

    def setLocation(self,lc):
        self.location = lc
        return
    def getLocation(self):
        return self.location

    def getJob(self):
        return self.Job

    def getSN(self):
        return self.SN

    def getcurrentjob(self):
        return self.currentjob
        
    def setcurrentjob(self,myjb):
        
        self.currentjob = myjb
        return

class SimBatch(object):   
    def __init__(self,env,Job,SN):
        self.env = env
        self.Job = Job
        self.SN = SN
        self.products=[]
        self.processtime=Job.getOperation().getProcessTime("min") #Processtime of 1 item in the batch
        self.capacity=10000
        self.Tray = None
        self.location = None
        self.currentjob = None
        self.timeremaining = 0
        self.process = None
        self.initialstarttime = None
        self.internalstarttime = None

    def setLocation(self,lc):
        self.location = lc
        return
    def getLocation(self):
        return self.location

    def getJob(self):
        return self.Job

    def getSN(self):
        return self.SN

    def getcurrentjob(self):
        return self.currentjob
        
    def setcurrentjob(self,myjb):        
        self.currentjob = myjb
        return

    def getProducts(self):
        return self.products

    def getCapacity(self):
        return self.capacity

    def getProcessTime(self):
        return self.processtime

    def setProcessTime(self,time):
        self.processtime = time
        return

    def setTimeRemaining(self,time):
        self.timeremaining = time
        return

    def getTimeRemaining(self):
        return self.timeremaining

    def getProcess(self):
        return self.process

    def setProcess(self,proc):
        self.process = proc
        return

    def getInitialStartTime(self):
        return self.initialstarttime

    def setInitialStartTime(self,time):
        self.initialstarttime = time
        return

    def getInternalStartTime(self):
        return self.internalstarttime

    def setInternalStartTime(self,time):
        self.internalstarttime = time
        return

class SimSubcontractor(object):
    def __init__(self,env,res):
        self.extres = res
        self.name = res.getName()
        self.type = 'Subcontractr'
        self.SchedulableWindow = [(480,960),(960,1440)]
        self.Resource= simpy.Resource(env, capacity=1000)
        self.Automated = res.Automated

    def getResource(self):
        return self.Resource

    def getName(self):
        return self.name
        
    def IsOpen(self,now):
        time = now % 1440 #Each day has 1440 minutes            
        return any(start<= time < end for start,end in self.SchedulableWindow)


       


class SimOperator(object):
    def __init__(self,env,Optr):
        self.env = env
        self.name = Optr.getName()
        self.type = 'Operator'
        self.operator = Optr
        self.efficiency = 1
        self.operationexecutions = []
        self.location = None 
        self.status = 'idle'
        self.currentexecution = None
        self.availability = dict() #  key: day, value: activeperiod.
        self.Resource = simpy.Resource(env,capacity=1)

    def getResource(self):
        return self.resource

    def getName(self):
        return self.name
        
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
        self.coordinates = (0,0)
        self.Container = simpy.Container(env, capacity=capacity)

    
        # historical capacity use
        #self.capacityuse = [] # list of pairs (time,capacityuse)
        #self.capacityuse.append((env.now,0))
    def getProducts(self):
        return self.products
    def getCapacity(self):
        return self.capacity

    def getContainer(self):
        return self.Container

    def getCoordinates(self):
        return self.coordinates 



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

class Trolley(object): 
    def __init__(self,env,name):

        self.env = env
        self.name = name
        self.capacity = 100
        self.products = [] # product
        self.job = None
        self.idle = True
        self.Resource = simpy.Resource(env, capacity=1) #This creates the simpy resource
        
    def IsIdle(self):
        return self.idle

    def getResource(self):
        return self.Resource

    def getJob(self):
        return self.job

    def setJob(self,job):
        self.job = job
        return        

    def setStatus(self,myidle):
        self.idle = myidle
        return
    def getName(self):
        return self.name

    def getProducts(self):
        return self.products
    def getCapacity(self):
        return self.capacity
      
        
class ProductionSystem(object): 
    def __init__(self,env,name):
        self.env = env
        self.name = name
        self.buffer = None
        self.machines = []
        self.operators = []
        self.subcontractors = []
        self.trolleys = []

    
    def getMachines(self):
        return self.machines

    def getOperators(self):
        return self.operators

    def getSubcontractors(self):
        return self.subcontractors

    def getTrolleys(self):
        return self.trolleys

    def setBuffer(self,bffr):
        self.buffer = bffr
        return

    def getBuffer(self):
        return self.buffer

    def print(self):
        return "Machines"+str(len(self.machines))+", Ops: "+str(len(self.operators))+", Sub: "+str(len(self.subcontractors))+", Trollys: "+str(len(self.trolleys))
        
class FloorShopManager(object):
    def __init__(self, env):
        self.env = env
        self.queue = []

    def add_batch(self,env,batch,Progress, envstart):
        Progress.value+= "Manager receives batch " + str(batch.getSN()) + " at "+ str(envstart[0] + env.now * envstart[1])+ "\n"
        self.queue.append(batch)

    def getQueue(self):
        return self.queue

            


class SimulationManager(object):
    def __init__(self): 

        self.DataManager = None
        self.VisualManager = None
        self.FloorShopManager = None
        self.SchedulingManager = None
        self.SimStart = None
        self.SimEnd = None
        self.TaskList = [] # Tasks are included in the list with some priority ordering
        self.ProdSN = 0
        self.simshifts = dict()
        self.EventQueue = dict() # key: simetime, val: Event
        self.AltEventQueue = [] #Jobs that are allowed to be scheduled
        self.prodsystem = None
        self.buffer = None
        self.FinishedTasks=[] #If job is finished

    def setProdSystem(self,systm):
        self.prodsystem = systm
        return

    def getProdSystem(self):
        return self.prodsystem

    def setBuffer(self,bffr):
        self.buffer = bffr
        return

    def getBuffer(self):
        return self.buffer

    def getEventQueue(self):
        return self.EventQueue

    def getAltEventQueue(self):
        return self.AltEventQueue

    def getMyShifts(self):
        return self.simshifts


    def getProdSN(self):
        self.ProdSN+=1
        return self.ProdSN

    def getFloorShopManager(self):
        return self.FloorShopManager
        
    def setFloorShopManager(self,myvm):
        self.FloorShopManager = myvm
        return

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

    def getFinishedTasks(self):
        return self.FinishedTasks

    def createBatch(self,env,job,SN):
        return SimBatch(env,job,SN)

    def createFloorShopManager(self,env):
        fsm = FloorShopManager(env)
        self.setFloorShopManager(fsm)
        return fsm
    
    def createProductionSystem(self,env,name):
        prodsys = ProductionSystem(env,name)
        self.setProdSystem(prodsys)
        return prodsys

    def createSubcontractor(self,env,res):
        return SimSubcontractor(env,res)

    def createBuffer(self,env,name,cap):
        buffer = Buffer(env,name,cap)
        self.setBuffer(buffer)
        return buffer

    def createMachine(self,env,machine):
        return SimMachine(env,machine)

    def createOperator(self,env,res):
        return SimOperator(env,res)

    def createJob(self,env,job):
        return SimJob(env,job)

    def createTrolley(self,env,name):
        return Trolley(env,name)

    def createProduct(self,env,job,SN):
        return SimProduct(env,job,SN)

    def CheckEventResource(self,event,Progress):

        if event.getType() == "Transport":
            # find a trolle that is idle: 

            Progress.value+=" trols: "+str(len(self.getProdSystem().getTrolleys()))+"\n"
            for trol in self.getProdSystem().getTrolleys():
                if trol.IsIdle():
                    Progress.value+=" trol found: "+str(trol.getName())+", used: "+str(len(trol.getProducts()) )+"\n"
                    if len(trol.getProducts()) < trol.getCapacity():
                        if len(trol.getProducts()) > 0: 
                            dest = trol.getProducts()[0].getcurrentjob().getOperation().getRequiredResources()[0]
                            if dest == event.getProduct().getcurrentjob().getOperation().getRequiredResources()[0]:
                                trol.getProducts().append(event.getProduct())
                                return True
                            else:
                                continue
                        else:
                            trol.getProducts().append(event.getProduct())
                            return True
        return False

    
    def CreateShifts(self,psstart,pssend,Progress):

        scheduleperiod = pd.date_range(psstart,pssend)

        Progress.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" shift creating starts... "+"\n"

        Progress = self.getVisualManager().getSchedulingTab().getPSchScheRes()

        prev_dayshift = None 
        scheduletimehour = 16 # time 08:00 in half hour granularity..
        
        for curr_date in scheduleperiod:

            if curr_date.date().weekday()>= 5:
                continue

            Progress.value+=str(curr_date)+"\n"

            if not curr_date in self.getMyShifts():
                curr_hour = 8
                self.getMyShifts()[curr_date] = [] 
                
                for i in range(1,4):
                    currenshift = Shift(curr_date,i,prev_dayshift)
                    currenshift.setStartTime(scheduletimehour) 
                    currenshift.setStartHour(curr_date + timedelta(hours=curr_hour))
                    currenshift.setEndHour(curr_date + timedelta(hours=curr_hour+7)+ timedelta(minutes=59))

                    scheduletimehour+=15
                    currenshift.setEndTime(scheduletimehour)
                    self.getMyShifts()[curr_date].append(currenshift)  
                    prev_dayshift = currenshift
                 
                    curr_hour+=8
                    scheduletimehour+=1
  
                    
                    for resname, res in self.getDataManager().getResources().items():
                        if currenshift.getNumber() in res.getAvailableShifts():
                            res.getSchedule()[currenshift] = []
                        if res.getType() == "Machine":
                            if currenshift.getNumber() == 3:
                                res.getShiftOperatingModes()[currenshift] = "Self-Running"
                            else:
                                res.getShiftOperatingModes()[currenshift] = "Operated"
           
            else:
                prev_dayshift = self.getMyShifts()[curr_date][-1]

            Progress.value+=str(curr_date)+", day shifts: "+str(len(self.getMyShifts()[curr_date]))+"\n"

       
       
        return 

    
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
       

  
