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


    def SystemClock(self,env):
   
       while True:

        
      
        unit_time = 0.01 # this is one minute 
        
        yield env.timeout(unit_time)
           
        return
 

       
    def RunSimulation(self):

        Progress = self.getSimulationManager().getVisualManager().getPSchScheRes()

        datamgr = self.getSimulationManager().getDataManager()

        Progress.value+="Simulation starts.."+"\n"

        Progress.value+="Simulation period "+str(self.getSimulationManager().getSimStart())+"-"+str(self.getSimulationManager().getSimEnd())+"\n"

        env = simpy.Environment()

        #self.getSimulationManager().getVisualManager().getPSchScheRes().value+="..."+str(env)+"\n"

        CentralBuffer = self.getSimulationManager().createBuffer(env,"CentralBuffer",10000000)

        Progress.value+="Central buffer created with cap.."+str(CentralBuffer.getCapacity())+"\n"

              
        
        datamgr.getSchedulingManager().CreateShifts(self.getSimulationManager().getSimStart(),self.getSimulationManager().getSimEnd(),False)

        Progress.value+="Customer orders.."+str(len(datamgr.getCustomerOrders()))+"\n"


        ProdSystem = self.getSimulationManager().createProductionSystem(env,"TBRM_Machine_BV")

        Progress.value+="ress .."+str(len(datamgr.getResources()))+"\n"

        Progress.value+="mahsss .."+str(len(ProdSystem.getMachines()))+"\n"


        for resname,res  in datamgr.getResources().items():
            if res.getType() == "Machine":
                
                ProdSystem.getMachines().append(self.getSimulationManager().createMachine(env,res))
            if res.getType() == "Outsourced":
               
                ProdSystem.getSubcontractors().append(self.getSimulationManager().createSubcontractor(env,res))
            if res.getType() == "Operator":
               
                ProdSystem.getOperators().append(self.getSimulationManager().createOperator(env,res))
      
    

        for i in range(5):
            ProdSystem.getTrolleys().append(self.getSimulationManager().createOperator(env,"Trolley_"+str(i)))
            

        self.getSimulationManager().getVisualManager().getPSchScheRes().value+=ProdSystem.print()+"\n"

        for name,order in self.getSimulationManager().getDataManager().getCustomerOrders().items():
            #self.getVisualManager().getPSchScheRes().value+="Customer order.."+str(name)+"\n"
            for job in order.getMyJobs():
                #self.getVisualManager().getPSchScheRes().value+="job.."+str(job.getName())+"\n"
                simJob = self.getSimulationManager().createJob(env,job)
                #self.getVisualManager().getPSchScheRes().value+="job..Q"+str(job.getQuantity())+"\n"
                for prd in range(int(job.getQuantity())):
                    simprod = self.getSimulationManager().createProduct(env,job,self.getSimulationManager().getProdSN())
                    simJob.getProducts().append(simprod)
                    simprod.setLocation(CentralBuffer)
                    CentralBuffer.getProducts().append(simprod)


        self.getSimulationManager().getVisualManager().getPSchScheRes().value+="Central buffer has "+str(len(CentralBuffer.getProducts()))+" products initially"+"\n"
            
        st = time.time() # get the start time
        planninghorizon = (self.getSimulationManager().getSimEnd() -self.getSimulationManager().getSimStart()).days+1  # days
        weekno = self.getSimulationManager().getSimStart().isocalendar()[1]
        
        self.getSimulationManager().getVisualManager().getPSchScheRes().value+="Simulation week start "+str(weekno)+", days: "+str(planninghorizon)+"\n"

        completiontime = 1440*planninghorizon   # Sim time in minutes

        env.process(self.SystemClock(env))
 
        # Execute
        env.run(until = completiontime)
        self.getSimulationManager().getVisualManager().getPSchScheRes().value+= '-> Execution time: '+str(round(time.time() - st,2))+' seconds'
     
        return infotxt


#------------------------------------------------------------------------------------------        
       

  
