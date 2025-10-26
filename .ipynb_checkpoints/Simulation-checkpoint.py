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

class SimEvent(object):
    def __init__(self, env,regtime,frm,to,mytype):

        self.Regtime = regtime
        self.Type = mytype
        self.Start = None
        self.Completed = None
        self.From = frm
        self.To = to
        self.ProcessTime = None

    def getRegtime(self):
        return self.Regtime

    def setProcessTime(self,mytm):
        self.ProcessTime = mytm
        return
    def getProcessTime(self):
        return self.ProcessTime

    def getType(self):
        return self.Type

    def ExecuteEvent(self):
        if self.getType == 'Transport':
            # Check operator availability

            #if event is done remove it from the queue
        
   
        

class SimMachine(object):
    def __init__(self, env,machine):
        self.env = env
        self.machine = machine
        self.location = None 
        self.inputbuffer = None
        self.outputbuffer = None
        self.XCoord = 0,0
        self.YCoord = 0,0


    def getLocation(self):
        return self.XCoord,self.YCoord

    
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
        self.currentjob = None

    def setLocation(self,lc):
        self.location = lc
        return
    def getLocation(self):
        return self.location

    def getcurrentjob(self):
        return self.currentjob
        
    def setcurrentjob(self,mytime,myjb):
        
        self.currentjob = myjb

        if myjb != None:
            res = myjb.getOperation().getRequiredResources()[0]
            simres = res.getSimResource()
            return SimEvent(self.env,mytime,self.getLocation(),simres,"Transport")
        else:
            return None


class SimSubcontractor(object):
    def __init__(self,env,res):
        self.extres = res


class SimTrolley(object):
    def __init__(self, env,name,myid):
        self.env = env
        self.name = name
        self.ID = myid  
        self.idle = True
        self.capacity = 100 # hard coded, funetune it!

    def isIdle(self):
        return self.idle
    def setIdle(self,idle):
        self.idle = idle
        return

    def getCapacity(self):
        return self.capacity
       
       
    

class SimOperator(object):
    def __init__(self,env,Optr):
        self.env = env 
        self.operator = Optr
        self.efficiency = 1
        self.operationexecutions = []
        self.location = None 
        self.status = 'idle'
        self.currentexecution = None
        self.availability = dict() #  key: day, value: activeperiod. 
        
        
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
        self.XCoord = 0,0
        self.YCoord = 0,0
      
        
        # historical capacity use
        #self.capacityuse = [] # list of pairs (time,capacityuse)
        #self.capacityuse.append((env.now,0))
    def getProducts(self):
        return self.products
    def getCapacity(self):
        return self.capacity


    def getLocation(self):
        return self.XCoord,self.YCoord
   


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
        self.products = [] # products
      
      
        
class ProductionSystem(object): 
    def __init__(self,env,name):
        self.env = env
        self.name = name
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

    def print(self):
        return "Machines"+str(len(self.machines))+", Ops: "+str(len(self.operators))+", Sub: "+str(len(self.subcontractors))+", Trollys: "+str(len(self.trolleys))
        
        


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
        self.simshifts = dict()
        self.EventQueue = dict() # key: simetime, val: Event
        self.prodsysterm = None

    def setProdSystem(self,systm):
        self.prodsysterm = systm
        return

    def getProdSystem(self,systm):
        return self.prodsysterm

    def getEventQueue(self):
        return self.EventQueue

    def getMyShifts(self):
        return self.simshifts


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



    def createProductionSystem(self,env,name):
        prodsys = ProductionSystem(env,name)
        self.setProdSystem(prodsys)
        return prodsys

    def createSubcontractor(self,env,res):
        return SimSubcontractor(env,res)

    def createBuffer(self,env,name,cap):
        return Buffer(env,name,cap)

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

    
    def CreateShifts(self,progress):

        dtstart = self.getSimStart()
        dtend = self.getSimEnd()

        progress.value+="Start shifts.."+str(dtstart)+str(dtend)+"\n"

        simperiod = pd.date_range(dtstart,dtend)
        
        
        self.getMyShifts().clear()

        progress.value+="period.."+str(simperiod)+"\n"
    
        i=1
        prev_dayshift = None 
        scheduletimehour = 1
        
        for curr_date in simperiod:

            self.getMyShifts()[curr_date] = []

            dayshifts = []

            progress.value+="date.."+str(curr_date)+"\n"
            
            shift1=Shift(curr_date,3,prev_dayshift)
            shift1.setStartTime(scheduletimehour) 

            
            shift1.setStartHour(curr_date + timedelta(hours=0))
            shift1.setEndHour(curr_date + timedelta(hours=7)+ timedelta(minutes=59))
          
            scheduletimehour+=8
            shift1.setEndTime(scheduletimehour-1)
            dayshifts.append(shift1)

        
            self.getMyShifts()[curr_date].append(shift1)   
            
         
            shift2=Shift(curr_date,1,shift1)
            shift2.setStartTime(scheduletimehour)   
            scheduletimehour+=8
            shift2.setEndTime(scheduletimehour-1)

            shift2.setStartHour(curr_date + timedelta(hours=8))
            shift2.setEndHour(curr_date + timedelta(hours=15)+timedelta(minutes=59))

            self.getMyShifts()[curr_date].append(shift2)   
                    
            dayshifts.append(shift2)
            
            
            shift3=Shift(curr_date,2,shift2)
            shift3.setStartTime(scheduletimehour)
            scheduletimehour+=8
            shift3.setEndTime(scheduletimehour-1)
            shift3.setStartHour(curr_date + timedelta(hours=16))
            shift3.setEndHour(curr_date + timedelta(hours=23)+ timedelta(minutes=59))

            self.getMyShifts()[curr_date].append(shift3)   
   
            prev_dayshift=shift3

            dayshifts.append(shift3)

            opno = 0

            progress.value+="resources.."+"\n"
            
            for resname, res in self.getDataManager().getResources().items():

                if res.getType() == "Machine":
                    
                    for currshift in dayshifts:
                        
                        if currshift.getNumber() in res.getAvailableShifts():
                            res.getCurrentSchedule()[currshift] = []

                            if currshift.getNumber() == 3:
                                res.getShiftOperatingModes()[currshift] = "Self-Running"
                            else:
                                res.getShiftOperatingModes()[currshift] = "Operated"

                if (res.getType() == "Manual") or (res.getType() == "Operator"):     
                    
                    for currshift in dayshifts:
                        if currshift.getNumber() in res.getAvailableShifts():
                            res.getCurrentSchedule()[currshift] = []
        
          
                if res.getType() == "Outsourced":
                    for currshift in dayshifts:
                        if currshift.getNumber() in res.getAvailableShifts():
                            res.getCurrentSchedule()[currshift] = []
                
                    
            i+=1        

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
       

  
