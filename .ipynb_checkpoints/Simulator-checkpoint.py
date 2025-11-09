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

        Progress.value+=str(self.getSimulationManager().getAltEventQueue())+", now: "+str(env.now)+"\n"
        
        for job in self.getSimulationManager().getAltEventQueue():
            Machine = job.getOperation().getRequiredResources()[0].getSimResource()
            Trolley_check = False
            while Trolley_check is False:
                prodsystem = self.getSimulationManager().getProdSystem()
                trolleys = prodsystem.getTrolleys()
                for trolley in trolleys:
                    if trolley.IsIdle() == True:
                        Chosen_Trolley = trolley
                        Trolley_check = True
                        break
                if Trolley_check == False:
                    yield env.timeout(0.01) #Waiting because there is no trolley available
            event = self.Trolley_function(env,trolley,job,Machine)
            env.process(event)
           
            
      
        unit_time = 0.01 # this is one minute 
        
        yield env.timeout(unit_time)
           
        return

    def Trolley_function(self,env,Trolley,job,end):
        Trolley.setStatus(False)
        if end.getName() == 'CentralBuffer':
            product = job.getProduct()
            quantity = job.getQuantity()            
            with Trolley.getResource().request() as req:
                yield req
                yield env.timeout(0.01) #Travel time to central buffer
                Trolley.setStatus(True)
                for prd in range(quantity):
                    simprod = self.getSimulationManager().createProduct(env,job,self.getSimulationManager().getProdSN())                      
                    simprod.setLocation(CentralBuffer)                    
                    CentralBuffer.getProducts().append(simprod)                
        else:
            Trolley.setJob(job)
            with Trolley.getResource().request() as req:
                yield req
                yield env.timeout(0.01) #Traveltime of trolley
                Trolley.setStatus(True)
                env.process(self.Machine_function(env,end,job))

    def Machine_function(self,env,Mach,job):
        with Mach.getResource().request() as req:
            yield req
            #Set start time
            job.setActualStart(env.now())
            yield env.timeout(job.getProcessingTime()*job.getQuantity())
            #Set job end time
            job.setActualCompletion(env.now())            
            self.getSimulationManager().getFinishedTasks().append(job)
            self.getSimulationManager().getAltEventQueue().remove(job)
            if job.getSuccessor() != '': #This means that we need to move the product to a next machine
                successor = job.getSuccessor()
                Sched = True
                for i in successor.getPredecessors():
                    if i not in self.getSimulationManager().getFinishedTasks():
                        Sched = False
                if Sched == True:
                    self.getSimulationManager().getAltEventQueue().append(successor)
                NextMachine = successor.getOperation().getRequiredResources()[0].getSimResource()
                Trolley_check = False
                while Trolley_check is False:
                    prodsystem = self.getSimulationManager().getProdSystem()
                    trolleys = prodsystem.getTrolleys()
                    for trolley in trolleys:
                        if trolley.IsIdle() == True:
                            Chosen_Trolley = trolley
                            Trolley_check = True
                            break
                    if Trolley_check == False:
                        yield env.timeout(0.01) #Waiting because there is no trolley available                   
                env.process(self.Trolley_function(env,Chosen_Trolley,successor,NextMachine))
            else:
                #We now move the product to the central buffer
                Trolley_check = False
                while Trolley_check is False:
                    prodsystem = self.getSimulationManager().getProdSystem()
                    trolleys = prodsystem.getTrolleys()
                    for trolley in trolleys:
                        if trolley.IsIdle() == True:
                            Chosen_Trolley = trolley
                            Trolley_check = True
                            break
                    if Trolley_check == False:
                        yield env.timeout(0.01) #Waiting because there is no trolley available
                Next = self.getSimulationManager().getBuffer() #Product is finished --> Move to buffer
                env.process(self.Trolley_function(env,Chosen_Trolley,job,Next))
            

       
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
      

        
        for i in range(5):
            ProdSystem.getTrolleys().append(self.getSimulationManager().createTrolley(env,"Trolley_"+str(i)))
            

        self.getSimulationManager().getVisualManager().getPSchScheRes().value+=ProdSystem.print()+"\n"


        self.getSimulationManager().getEventQueue()[env.now] = []
       
        # Product creation for jobs that are first to do. 
        for name,order in self.getSimulationManager().getDataManager().getCustomerOrders().items():
            Progress.value+="Customer order.."+str(name)+" jobs "+str(len(order.getMyJobs()))+"\n"
            for job in order.getMyJobs():
                Progress.value+="job..Q"+str(job.getQuantity())+", preds: "+str(len(job.getPredecessors()))+"\n"
                if len(job.getPredecessors()) == 0:
                    self.getSimulationManager().getAltEventQueue().append(job)
                    for prd in range(int(job.getQuantity())):
                        simprod = self.getSimulationManager().createProduct(env,job,self.getSimulationManager().getProdSN())                      
                        simprod.setLocation(CentralBuffer)                      
                          
                     
                        CentralBuffer.getProducts().append(simprod)

        Progress.value+="Event Queue: ."+str(len(self.getSimulationManager().getAltEventQueue()))+"\n"


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
       

  
