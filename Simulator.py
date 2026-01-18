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
    
           
        

    # def Trolley_function(self,env,Trolley,job,end):
    #     Trolley.setStatus(False)
    #     if end.getName() == 'CentralBuffer':
    #         product = job.getProduct()
    #         quantity = job.getQuantity()            
    #         with Trolley.getResource().request() as req:
    #             yield req
    #             yield env.timeout(0.01) #Travel time to central buffer
    #             Trolley.setStatus(True)
    #             for prd in range(quantity):
    #                 simprod = self.getSimulationManager().createProduct(env,job,self.getSimulationManager().getProdSN())                      
    #                 simprod.setLocation(CentralBuffer)                    
    #                 CentralBuffer.getProducts().append(simprod)                
    #     else:
    #         Trolley.setJob(job)
    #         with Trolley.getResource().request() as req:
    #             yield req
    #             yield env.timeout(0.01) #Traveltime of trolley
    #             Trolley.setStatus(True)
    #             env.process(self.Machine_function(env,end,job))

    def FloorShopManagerExecutes(self,env,FSM,operators,Progress,envstart):
            while True:
                while not (env.now%1440) >= 480 and FSM.queue !=[]:
                    
                    for batch in FSM.queue:
                        if batch.process is not None and batch.getTimeRemaining() > 0 and batch.getcurrentjob().getOperation().getRequiredResources()[0].Automated == False:                            
                            batch.process.interrupt()
                            batch.process = None
                    Progress.value+= "\n" + "Machines are closed for receiving new jobs. Manager is waiting for the new day to dispatch the batches " + "\n"
                    yield env.timeout(480 - (env.now%1440))                    
                    
                if FSM.queue:
                    
                    for batch in FSM.queue:
                        if batch.getTimeRemaining() == 0:
                            FSM.queue.remove(batch)
                        if batch.process is None and batch.getTimeRemaining() > 0:                            
                            
                            Machine = batch.getcurrentjob().getOperation().getRequiredResources()[0].getSimResource()
                            Progress.value+= "Manager dispatches batch " + str(batch.getSN()) + " at time "+ str(envstart[0] + env.now * envstart[1]) + " to machine "+str(Machine.getName())+ "\n"
                            batch.setProcess(env.process(self.Batch_Proces(env,batch,Machine,operators,Progress,envstart)))
                            yield env.timeout(1) # check every time unit
                yield env.timeout(1)
                    
                     
                             
                            


                    
                    # Decision rule: pick shortest batch first
                    # batch = min(FSM.getQueue(), key=lambda b: b.getProcessTime())
                    #FSM.queue.remove(batch)
                    # Machine = batch.getcurrentjob().getOperation().getRequiredResources()[0].getSimResource()
                    ## Manager only dispatches jobs in the morning and evening shift, not the nightshift. For now we simulate a waittime of
                #     while not Machine.IsOpen(env.now):
                #         Progress.value+= "Machines are closed for receiving new jobs. Manager is waiting for the new day to dispatch the batches " + "\n"
                #         yield env.timeout(480 - (env.now%1440))
                #     Progress.value+= "Manager dispatches batch " + str(batch.getSN()) + " at time "+ str(envstart[0] + env.now * envstart[1]) + " to machine "+str(Machine.getName())+ "\n"
                    
                #     batch.process = env.process(self.Batch_Proces(env,batch,Machine,Progress,envstart))
                # yield env.timeout(1)  # check every time unit


                
    
    def Batch_Proces(self,env,batch,Machine,operators,Progress,envstart):
        fte_set = False
        try:            
            while not Machine.IsOpen(env.now):
                yield env.timeout(480-(env.now % 1440)) #Check again when new day starts
            
            with Machine.getResource().request() as req:                
                yield req
                if Machine.type == 'Machine':
                    yield operators.get(Machine.getFTERequirement()) # This is the fraction of FTE that gets consumed during the request
                    fte_set = True
                #Set start time
                if batch.initialstarttime == None:
                    batch.setInitialStartTime(env.now * envstart[1])
                    batch.setInternalStartTime(env.now)
                else:
                   batch.setInternalStartTime(env.now) 
                Progress.value+="Processing Batch "+str(batch.getSN()) +" at time: "+str(envstart[0] + env.now * envstart[1])+ " on machine: " + str(Machine.getName())+ "\n"    
                
                
                #This means that this batch can be finished on
                
                yield env.timeout(batch.getTimeRemaining())
                batch.setTimeRemaining(0) # This will only update if there is a successor job.
                batch.setProcess(None) #The operation is complete. The current process does no longer need to be able to be interrupted
    
                    
                Progress.value+="Done Processing products from batch "+str(batch.getSN()) +" at time: "+str(envstart[0] + env.now * envstart[1])+ " on machine: " + str(Machine.getName())+ "\n"
                
                successor = self.SuccessorCheck(batch)
                if successor == False:                
                    Progress.value+="This was the final job of the batch, moving finished products to buffer" + "\n"
                    for product in batch.getProducts():
                        self.getSimulationManager().getProdSystem().getBuffer().getProducts().append(product) #Product is finished --> Move to buffer
                    Progress.value+="Moved products from batch "+str(batch.getSN()) +" to buffer at time: "+str(envstart[0] + env.now * envstart[1])+"\n" + "\n"
                else:
                    batch.setcurrentjob(successor)
                    batch.setProcessTime(successor.getOperation().getProcessTime("min"))
                    Machine = batch.getcurrentjob().getOperation().getRequiredResources()[0].getSimResource()                
                    Progress.value+="Moving batch "+ str(batch.getSN())+" to Floorshopmanager for next operation. " + "\n" + "\n"
                    batch.setTimeRemaining(batch.getProcessTime()*len(batch.getProducts()))
                    self.getSimulationManager().getFloorShopManager().add_batch(env,batch,Progress,envstart)
                    # event = self.Batch_Proces(env,batch,Machine,Progress,envstart)
                    # env.process(event)
        except simpy.Interrupt:
            Progress.value+= "Manager interrupting batch " + str(batch.getSN()) + " at time "+ str(envstart[0] + env.now * envstart[1]) + " on machine "+str(Machine.getName())+ " due to schop closing."+ "\n"
            elapsed = env.now - batch.getInternalStartTime()
            batch.timeremaining -= elapsed
        finally:
            if fte_set and Machine.type=='Machine':
                operators.put(Machine.getFTERequirement())

        
    def SuccessorCheck(self, batch):
        if len(batch.getcurrentjob().getSuccessors()) == 0:
            return False
        else:
            return batch.getcurrentjob().getSuccessors()[0]
       
    def RunSimulation(self):

        Progress = self.getSimulationManager().getVisualManager().getPSchScheRes()

        datamgr = self.getSimulationManager().getDataManager()

        schedmgr = self.getSimulationManager().getSchedulingManager()

        Progress.value+="Simulation starts.."+"\n"

        Progress.value+="Simulation period "+str(self.getSimulationManager().getSimStart())+"-"+str(self.getSimulationManager().getSimEnd())+"\n"

        env = simpy.Environment()

        #self.getSimulationManager().getVisualManager().getPSchScheRes().value+="..."+str(env)+"\n"

        CentralBuffer = self.getSimulationManager().createBuffer(env,"CentralBuffer",10000000)

        Progress.value+="Central buffer created with cap.."+str(CentralBuffer.getCapacity())+"\n"
   
        
        self.getSimulationManager().CreateShifts(Progress)


        ###-------------------------Here we initialize the shifts based on the scheduling information------------------------------------###
        Progress.value+="Shifts initialized in days: "+str(len(self.schedmgr.getMyShifts()))+"\n"  

        ###-------------------------end initialize the shifts based on the scheduling information------------------------------------###

        Progress.value+="Customer orders.."+str(len(datamgr.getCustomerOrders()))+"\n"


        ProdSystem = self.getSimulationManager().createProductionSystem(env,"TBRM_Machine_BV")

        FloorShopManager = self.getSimulationManager().createFloorShopManager(env)

        for resname,res  in datamgr.getResources().items():
            if res.getType() == "Machine":

                simmach = self.getSimulationManager().createMachine(env,res)
                res.setSimResource(simmach)
                ProdSystem.getMachines().append(simmach)
            if res.getType() == "Outsourced":

                simsub = self.getSimulationManager().createSubcontractor(env,res)
                res.setSimResource(simsub)
                ProdSystem.getSubcontractors().append(simsub)               
                
            if res.getType() == "Operator":
                simop = self.getSimulationManager().createOperator(env,res)
                res.setSimResource(simop)
                ProdSystem.getOperators().append(simop)   
                
      

        
        for i in range(5):
            ProdSystem.getTrolleys().append(self.getSimulationManager().createTrolley(env,"Trolley_"+str(i)))
            

        self.getSimulationManager().getVisualManager().getPSchScheRes().value+=ProdSystem.print()+"\n"


        self.getSimulationManager().getEventQueue()[env.now] = []

        ####HERE ARE THE PARAMETERS WE SET FOR THE ENVIRONMENT######

        num_orders = 122

        ## This sets parameters for visualisation feedback to user
        start = datetime.datetime.combine(self.getSimulationManager().getSimStart(), datetime.datetime.min.time())
        scale = timedelta(minutes=1)
        eventStart = [start,scale]
        ######
       
        # Product creation for jobs that are first to do. 
        for name,order in islice(self.getSimulationManager().getDataManager().getCustomerOrders().items(),num_orders):
            if len(order.getMyJobs()) == 0:
                continue
            else:
                Progress.value+="Customer order.."+str(name)+" jobs "+str(len(order.getMyJobs()))+"\n"
                for job in order.getMyJobs():                                        
                    Progress.value+="job..Q"+str(job.getQuantity())+", preds: "+str(len(job.getPredecessors()))+"\n"
                    if len(job.getPredecessors()) == 0: #This means it is a schedulable first job
                        Batch = self.getSimulationManager().createBatch(env,job,len(FloorShopManager.getQueue()))
                        Batch.setcurrentjob(job)                        
                        for prd in range(int(job.getQuantity())):
                            if len(Batch.getProducts()) < Batch.getCapacity():
                                simprod = self.getSimulationManager().createProduct(env,job,self.getSimulationManager().getProdSN())
                                simprod.setLocation(CentralBuffer)                                                                                              
                                CentralBuffer.getProducts().append(simprod)
                                Batch.getProducts().append(simprod)
                            else:
                                FloorShopManager.add_batch(env,Batch,Progress,eventStart)
                                Batch = self.getSimulationManager().createBatch(env,job,len(FloorShopManager.getQueue()))
                                Batch.setcurrentjob(job)
                                simprod = self.getSimulationManager().createProduct(env,job,self.getSimulationManager().getProdSN())
                                simprod.setLocation(CentralBuffer)                                                                                              
                                CentralBuffer.getProducts().append(simprod)
                        Batch.setTimeRemaining(Batch.getProcessTime()*len(Batch.getProducts()))
                        FloorShopManager.add_batch(env,Batch,Progress,eventStart)
        ProdSystem.setBuffer(CentralBuffer)
        Progress.value+="Event Queue: ."+str(len(FloorShopManager.getQueue()))+"\n"


        self.getSimulationManager().getVisualManager().getPSchScheRes().value+="Central buffer has "+str(len(CentralBuffer.getProducts()))+" products initially"+"\n"
            
        st = time.time() # get the start time
        Progress.value+="Start time: ."+str(self.getSimulationManager().getSimStart())+"\n"
        Progress.value+="End time: ."+str(self.getSimulationManager().getSimEnd())+"\n"
        planninghorizon = (self.getSimulationManager().getSimEnd() - self.getSimulationManager().getSimStart()).days+1  # days
        weekno = self.getSimulationManager().getSimStart().isocalendar()[1]
        
        self.getSimulationManager().getVisualManager().getPSchScheRes().value+="Simulation week start "+str(weekno)+", days: "+str(planninghorizon)+"\n"

       
        
        completiontime = 1440*planninghorizon   # Sim time in minutes

        def shift_scheduler(env, machine):
            """Weekly calendar: 3 shifts per day, jobs only allowed in first 2."""
            day_length = 24
            shifts = [(8, 16), (16, 24),(0, 8)]  # three shifts per day
        
            while True:
                for start, end in shifts:
                    # Only allow jobs in first two shifts
                    if start >= 8:
                        machine.open = True

                    else:
                        machine.open = False

        
                    yield env.timeout(end - start)        

        #env.process(self.SystemClock(env,Progress))

        # for batch in self.getSimulationManager().getAltEventQueue():
        #         Machine = batch.getJob().getOperation().getRequiredResources()[0].getSimResource()            
        #         event = self.Batch_Proces(env,batch,Machine,Progress,eventStart)
        #         env.process(event)

        Operatorpool = simpy.Container(env,init=100)
        env.process(self.FloorShopManagerExecutes(env,FloorShopManager,Operatorpool,Progress,eventStart))
        # Execute
        env.run(until=completiontime)
        
        self.getSimulationManager().getVisualManager().getPSchScheRes().value+= '-> Execution time: '+str(round(time.time() - st,2))+' seconds'
     
        return 


#------------------------------------------------------------------------------------------        
       

  
