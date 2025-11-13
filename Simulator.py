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
from itertools import islice

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
            for prod in self.getSimulationManager().getAltEventQueue():
                Machine = prod.getJob().getOperation().getRequiredResources()[0].getSimResource()            
                event = self.Product_Proces(env,prod,Machine,Progress)
                env.process(event)
                yield env.timeout(0.01)
    
           
        

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

    def Product_Proces(self,env,product,Machine, Progress):
        with Machine.getResource().request() as req:
            yield req
            #Set start time
            Progress.value+="Processing product "+str(product.getSN()) +" at time: "+str(env.now)+ "\n"
            yield env.timeout(product.getJob().getOperation().getProcessTime("hour"))
            Progress.value+="Done Processing product "+str(product.getSN()) +" at time: "+str(env.now)+"\n"
            
            self.getSimulationManager().getProdSystem().getBuffer().getProducts().append(product) #Product is finished --> Move to buffer
            Progress.value+="Moved product "+str(product.getSN()) +" to buffer at time: "+str(env.now)+"\n"
            

       
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

        ####HERE ARE THE PARAMETERS WE SET FOR THE ENVIRONMENT######

        num_orders = 122
        num_jobs = 1
       
        # Product creation for jobs that are first to do. 
        for name,order in islice(self.getSimulationManager().getDataManager().getCustomerOrders().items(),num_orders):
            Progress.value+="Customer order.."+str(name)+" jobs "+str(len(order.getMyJobs()))+"\n"
            for i in range(0,num_jobs):
                if len(order.getMyJobs()) == 0:
                    continue
                job = order.getMyJobs()[i]
                Progress.value+="job..Q"+str(job.getQuantity())+", preds: "+str(len(job.getPredecessors()))+"\n"
                #if len(job.getPredecessors()) == 0: ### FOR NOW WE DO NOT CHECK PREDECESSORS                    
                for prd in range(int(job.getQuantity())):
                    simprod = self.getSimulationManager().createProduct(env,job,self.getSimulationManager().getProdSN())
                    self.getSimulationManager().getAltEventQueue().append(simprod)
                    simprod.setLocation(CentralBuffer)                                                                 
                    CentralBuffer.getProducts().append(simprod)
                    
        ProdSystem.setBuffer(CentralBuffer)
        Progress.value+="Event Queue: ."+str(len(self.getSimulationManager().getAltEventQueue()))+"\n"


        self.getSimulationManager().getVisualManager().getPSchScheRes().value+="Central buffer has "+str(len(CentralBuffer.getProducts()))+" products initially"+"\n"
            
        st = time.time() # get the start time
        planninghorizon = (self.getSimulationManager().getSimEnd() -self.getSimulationManager().getSimStart()).days+1  # days
        weekno = self.getSimulationManager().getSimStart().isocalendar()[1]
        
        self.getSimulationManager().getVisualManager().getPSchScheRes().value+="Simulation week start "+str(weekno)+", days: "+str(planninghorizon)+"\n"

        completiontime = 1440*planninghorizon   # Sim time in minutes

        

        #env.process(self.SystemClock(env,Progress))

        for prod in self.getSimulationManager().getAltEventQueue():
                Machine = prod.getJob().getOperation().getRequiredResources()[0].getSimResource()            
                event = self.Product_Proces(env,prod,Machine,Progress)
                env.process(event)
 
        # Execute
        env.run(until = completiontime)
        self.getSimulationManager().getVisualManager().getPSchScheRes().value+= '-> Execution time: '+str(round(time.time() - st,2))+' seconds'
     
        return 


#------------------------------------------------------------------------------------------        
       

  
