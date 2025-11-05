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
from Simulation import *

#######################################################################################################################


class Simulator(object):
    
    def __init__(self): 
        self.SimulationManager = None
    
  
    def getSimulationManager(self):
        return self.SimulationManager
    def setSimulationManager(self,myvm):
        self.SimulationManager = myvm
        return

    def getMachines(self):
        
        return self.Machines


    def SystemClock(self,env,Progress):
   
       while True:

        Progress.value+=str(self.getSimulationManager().getEventQueue().keys())+", now: "+str(env.now)+"\n"
        for job in self.getSimulationManager().getAltEventQueue():
           for evid in range(len(self.getSimulationManager().getEventQueue()[env.now])):
               Progress.value+=" evid: "+str(evid)+", events: "+str(len(self.getSimulationManager().getEventQueue()[env.now]))+"\n"
               event = self.getSimulationManager().getEventQueue()[env.now][evid]
               if self.getSimulationManager().CheckEventResource(event,Progress):
                   evid-=1
                   self.getSimulationManager().getEventQueue()[env.now].remove(event)

        for trol in self.getProdSystem().getTrolleys():
            Progress.value+="Time: "+str(env.now)+" trolley "+str(trol.getName())+", used-cap: "+str(len(trol.getProducts()))+"\n"
            
      
        unit_time = 0.01 # this is one minute 
        
        yield env.timeout(unit_time)
           
        return

    def Trolley_function(env,Trolley,job,end):
        Trolley.setJob(job)
        with Trolley.getResource().request() as req:
            yield req
            yield env.timeout(1) #Traveltime of trolley
            Machine_function(env,end,job)

    def Machine_function(env,Mach,job):
        with Mach.getResource().request() as req:
            yield req
            #Set start time
            yield env.timeout(job.getProcessingTime())
            #Set job end time
            self.getSimulationManager().getFinishedTasks().append(job)
            self.getSimulationManager().getAltEventQueue().remove(job)
            successor = job.getSuccessor()
            Sched = True
            for i in successor.getPredecessors():
                if i not in self.getSimulationManager().getFinishedTasks():
                    Sched = False
            if Sched == True:
                self.getSimulationManager().getAltEventQueue().append(successor)
            

       
    def RunSimulation(self):

        Progress = self.getSimulationManager().getVisualManager().getPSchScheRes()

        datamgr = self.getSimulationManager().getDataManager()

        Progress.value+="Simulation starts.."+"\n"

        Progress.value+="Simulation period "+str(self.getSimulationManager().getSimStart())+"-"+str(self.getSimulationManager().getSimEnd())+"\n"

        env = simpy.Environment()

        #self.getSimulationManager().getVisualManager().getPSchScheRes().value+="..."+str(env)+"\n"

        CentralBuffer = self.getSimulationManager().createBuffer(env,"CentralBuffer",10000000)

        Progress.value+="Central buffer created with cap.."+str(CentralBuffer.getCapacity())+"\n"
   
        
        self.getSimulationManager().CreateShifts(Progress)

        Progress.value+="Shifts initialized in days: "+str(len(self.getSimulationManager().getMyShifts()))+"\n"  

        Progress.value+="Customer orders.."+str(len(datamgr.getCustomerOrders()))+"\n"


        ProdSystem = self.getSimulationManager().createProductionSystem(env,"TBRM_Machine_BV")


        for resname,res  in datamgr.getResources().items():
            if res.getType() == "Machine":

                simmach = self.getSimulationManager().createMachine(env,res)
                res.setSimResource(simmach)
                ProdSystem.getMachines().append(simmach)
            if res.getType() == "Outsourced":
               
                ProdSystem.getSubcontractors().append(self.getSimulationManager().createSubcontractor(env,res))
            if res.getType() == "Operator":
               
                ProdSystem.getOperators().append(self.getSimulationManager().createOperator(env,res))
      

        
        ProdSystem.getTrolleys().append(self.getSimulationManager().createTrolley(env,"Trolleys")
            

        self.getSimulationManager().getVisualManager().getPSchScheRes().value+=ProdSystem.print()+"\n"


        self.getSimulationManager().getEventQueue()[env.now] = []
       
        # Product creation for jobs that are first to do. 
        for name,order in self.getSimulationManager().getDataManager().getCustomerOrders().items():
            Progress.value+="Customer order.."+str(name)+" jobs "+str(len(order.getMyJobs()))+"\n"
            for job in order.getMyJobs():
                Progress.value+="job..Q"+str(job.getQuantity())+", preds: "+str(len(job.getPredecessors()))+"\n"
                if len(job.getPredecessors()) == 0:
                    for prd in range(int(job.getQuantity())):
                        simprod = self.getSimulationManager().createProduct(env,job,self.getSimulationManager().getProdSN())
                      
                        simprod.setLocation(CentralBuffer)
                       
                        self.getSimulationManager().getAltEventQueue().append(job)  
                     
                        CentralBuffer.getProducts().append(simprod)

        Progress.value+="Event Queue: ."+str(len(self.getSimulationManager().getEventQueue()[env.now]))+"\n"


        self.getSimulationManager().getVisualManager().getPSchScheRes().value+="Central buffer has "+str(len(CentralBuffer.getProducts()))+" products initially"+"\n"
            
        st = time.time() # get the start time
        planninghorizon = (self.getSimulationManager().getSimEnd() -self.getSimulationManager().getSimStart()).days+1  # days
        weekno = self.getSimulationManager().getSimStart().isocalendar()[1]
        
        self.getSimulationManager().getVisualManager().getPSchScheRes().value+="Simulation week start "+str(weekno)+", days: "+str(planninghorizon)+"\n"

        completiontime = 1440*planninghorizon   # Sim time in minutes

        env.process(self.SystemClock(env,Progress))
 
        # Execute
        env.run(until = completiontime)
        self.getSimulationManager().getVisualManager().getPSchScheRes().value+= '-> Execution time: '+str(round(time.time() - st,2))+' seconds'
     
        return infotxt


#------------------------------------------------------------------------------------------        
       

  
