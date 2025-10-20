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

          
        if env.now in self.getSimulationManager().getEventQueue():
            for event in self.getSimulationManager().getEventQueue()[env.nov]:
                
        
      
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
            ProdSystem.getTrolleys().append(self.getSimulationManager().createOperator(env,"Trolley_"+str(i)))
            

        self.getSimulationManager().getVisualManager().getPSchScheRes().value+=ProdSystem.print()+"\n"


       

        for name,order in self.getSimulationManager().getDataManager().getCustomerOrders().items():
            #self.getVisualManager().getPSchScheRes().value+="Customer order.."+str(name)+"\n"
            for job in order.getMyJobs():
                #self.getVisualManager().getPSchScheRes().value+="job..Q"+str(job.getQuantity())+"\n"
                if len(job.getPredecessors())  == 0:
                    for prd in range(int(job.getQuantity())):
                        simprod = self.getSimulationManager().createProduct(env,job,self.getSimulationManager().getProdSN())
                       
                        simprod.setLocation(CentralBuffer)
                        firstevent = simprod.setcurrentjob(0,job)
                        if not 0 in self.getSimulationManager().getEventQueue():
                            self.getSimulationManager().getEventQueue()[0] = []

                        self.getSimulationManager().getEventQueue()[0].append(firstevent)  
                        CentralBuffer.getProducts().append(simprod)

        Progress.value+="Event Queue: ."+str(len(self.getSimulationManager().getEventQueue()[0]))+"\n"


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
       

  
