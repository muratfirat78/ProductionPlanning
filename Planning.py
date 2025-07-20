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
from PlanningObjects import *
from Visual import *
from Data import *


#######################################################################################################################


        
class PlanningManager:
    def __init__(self): 

        self.DataManager = None
        self.VisualManager = None
        self.logdata = dict()
        self.PHStart = None
        self.PHEnd = None
    
    
   
    def setDataManager(self,DataMgr):
        self.DataManager = DataMgr 
        return

    def getJobs(self):
        return 

    
        
    def getPHStart(self):
        return self.PHStart 
        
    def setPHStart(self,mydt):
        self.PHStart = mydt
        return

    def getPHEnd(self):
        return self.PHEnd 
        
    def setPHEnd(self,mydt):
        self.PHEnd = mydt
        return


    def getDataManager(self):
        return self.DataManager

    def setVisualManager(self,VMgr):
        self.VisualManager = VMgr 
        return

    def getVisualManager(self):
        return self.VisualManager

    def getLogData(self):
        return self.logdata

    def ResetResourceReserved(self):
        
        return

    def PlanProduction(self,order,product,mydate,quantity):

        #calculate use of resource for production for every operation
        #assume: one workday includes 16 hours of two shifts. 
        #assume: all production is done sequential in operations, no batch concept 

        if not product in order.getOrderPlan()['Products']:
            order.getOrderPlan()['Products'].append(product)

        quantity = quantity/product.getStockBatch()

        
        if mydate in product.getReservedStockLevels():
            product.getReservedStockLevels()[mydate]+=quantity
        else:
            product.getReservedStockLevels()[mydate]=quantity

        #if len(product.getOperations()) == 0:
      
       
        # self.getVisualManager().getPLTBresult2exp().value+=str(type(mydate))+"  "+str(type(self.getPHStart()))+"\n"
        if mydate.date() < self.getPHStart():
            self.getVisualManager().getPLTBresult2exp().value+="XXXXX <  "+str(self.getPHStart())+"\n"
            order.getDelayReasons()[product] = ("lead time",mydate.date())
            return False
        
        totaltime = 0   
        if len(product.getMPredecessors()) > 0: # bom case
            
          
            for operation in product.getOperations():

                # skip quantity when resource is outsourced.
                if operation.getRequiredResources()[0].getType() == 'Outsourced':
                    resource_use = operation.getProcessTime()
                else:
                    resource_use = quantity*operation.getProcessTime() 
               
                
                totaltime+=resource_use
                # self.getVisualManager().getPLTBresult2exp().value+=str(operation.getName())+">> "+str(len(operation.getRequiredResources()))+"\n"
                for resource in operation.getRequiredResources():

                    myresource = resource
                    if isinstance(resource, list):
                        myresource = resource[0] # here first one among alternatives is selected, if there are some..
                       
                
                    totuse = 0
                    capsuff = True
                    for checkdate,useval in myresource.getCapacityUsePlan().items():
                        totuse+=useval
                        if checkdate < mydate:
                            continue   
                        totres = sum([resval for chdate,resval in myresource.getCapacityReserved().items() if chdate <= checkdate])  
                        if myresource.getCapacityLevels()[checkdate] < totuse+totres+resource_use:
                            capsuff = False
                            break
                   
                    if capsuff:
                        if not myresource in order.getOrderPlan()['Resources']:
                            order.getOrderPlan()['Resources'].append(myresource)
                                
                        if mydate in myresource.getCapacityReserved():
                            myresource.getCapacityReserved()[mydate]+=resource_use
                        else:
                            myresource.getCapacityReserved()[mydate] =resource_use
                     
                        #self.getVisualManager().getPLTBresult2exp().value+="capacitylevels ok.."+"\n"
                        self.getLogData()["Log_"+str(len(self.getLogData()))]="Sufficient capacity for "
                    else: 
                        self.getLogData()["Log_"+str(len(self.getLogData()))]="Insufficient capacity for "
                        order.getDelayReasons()[product] = (myresource.getName(),mydate.date())
                        return False
                            
    
            # calculate the change in date    
            workdays = totaltime//16 + int(totaltime%16 > 0)


            if mydate.weekday() - workdays < 0:
                workdays+=2
                
            
            newdate = mydate- timedelta(days = workdays)

            
            if newdate.date()  < self.getPHStart():
                order.getDelayReasons()[product] = (product.getName(),str(mydate.date())+"->"+str(newdate.date()))
                return False
     
                
                
       
        if len(product.getMPredecessors()) > 0:
            for predecessor,multiplier in product.getMPredecessors().items():
                #self.getVisualManager().getPLTBresult2exp().value+="predecessor.."+str(predecessor.getName())+"\n"
    
               
                if not self.PlanProduction(order,predecessor,newdate,quantity*multiplier):
                    return False
    
        return True
        

    

    def MakeDeliveryPlan(self,b):
        ''' This function construct a delivery plan for every customer orders as follows: 
            - Customer Orders have priority due to their deadlines; i.e. the customer order with soonest deadline must be planned first. 
            - The primary goal is to plan customer orders without any delay. If the delivery of a customer order should be with some delay, then it loses itspriority compared to all other cutomer orders to be planned.  
            - The combined required capacity levels of planned customer orders should respect to the capacity levels of all resources.
            - Every raw material can be purchased at most certain amount in every week. The required raw material levels of planned customer orders should be feasible by possibly purchasing additional amount of raw materials for every week.  
        '''

        PlanningWeeks = 24
        # START: here is your code to make planning 
        self.getVisualManager().getPLTBresult2exp().value+=">Planning weeks: "+str(PlanningWeeks)+"\n"
 
        mydict = self.getDataManager().getCustomerOrders()
        sortedtuples = sorted(mydict.items(), key=lambda item: item[1].getDeadLine())
        mydict = {k: v for k, v in sortedtuples}
        self.getDataManager().setCustomerOrders(mydict)

        # determine planning horizon
        phstart = date.today()+timedelta(days=1)

        if phstart.weekday() > 0:
            phstart = phstart+timedelta(days=7-phstart.weekday())

        self.getVisualManager().getPLTBresult2exp().value+=">Planning start: "+str(phstart)+"\n"
 
        self.setPHStart(phstart) 

      
        self.setPHEnd((phstart+timedelta(days=7*PlanningWeeks)))  

        self.getVisualManager().getPLTBresult2exp().value+=">Planning Horizon: "+str(self.getPHStart())+" <--> "+str(self.getPHEnd())+"\n"
 

        # Create time-dependant lists: Capacity levels of resources, stock levels of raw materials

        #self.getVisualManager().getPLTBresult2exp().value+=">> Resources capacities.. "+str(len(self.getDataManager().getResources().items()))+"\n"
        daterange = pd.date_range(self.getPHStart(),self.getPHEnd())

        for resname,res in self.getDataManager().getResources().items():
            res.getCapacityLevels().clear()
            res.getCapacityUsePlan().clear()
          
            
            cumulative_capacity = 0

            
            for curr_date in daterange:
                if curr_date.weekday() < 5:
                   cumulative_capacity+= int(res.getDailyCapacity())
                    
                res.getCapacityLevels()[curr_date] = cumulative_capacity
               

        for prname,prod in self.getDataManager().getProducts().items():
            #prod.getDemandingOrders().clear()
            prod.getTargetLevels().clear()
            prod.getReservedStockLevels().clear()
            for curr_date in daterange:
                prod.TargetLevels[curr_date] = 0
                
     
        # Start planning 
        self.getVisualManager().getPLTBresult2exp().value+=">> Start planning orders..  "+str(len(self.getDataManager().getCustomerOrders()))+"\n"

        for ordname,myord in self.getDataManager().getCustomerOrders().items():
            myord.resetOrderPlan()
            
            for curr_deliverydate in pd.date_range(max(myord.getDeadLine().date(),self.getPHStart()),self.getPHEnd()):
                if curr_deliverydate.weekday() >= 5:
                    continue
                    
      
                if self.PlanProduction(myord,myord.getProduct(),curr_deliverydate,myord.getQuantity()):
   
                    myord.setPlannedDelivery(curr_deliverydate)

                   # apply resource use plan: convert reserved capacity use to actual capacity use.
                    for res in myord.getOrderPlan()['Resources']: 
                        
                        for mydate,val in res.getCapacityReserved().items():
                           
                            if mydate in res.getCapacityUsePlan():
                                res.getCapacityUsePlan()[mydate]+=val
                            else: 
                                res.getCapacityUsePlan()[mydate]=val
                                
                            
                             
                    # update target stock levels: convert tentative stock levels to target stock levels. 
                    for prod in myord.getOrderPlan()['Products']:
                       
                        prod.getDemandingOrders()[myord]=sum([lvl for mydate,lvl in prod.getReservedStockLevels().items()])
                        for mydate,lvl in prod.getReservedStockLevels().items():
                            for curr_date in pd.date_range(mydate,self.getPHEnd()):
                                prod.getTargetLevels()[curr_date]+= lvl

                myord.resetOrderPlan()

                if myord.getPlannedDelivery() != None:
                    break
                
     
    
        # END: here is your code to make planning 
        # self.getVisualManager().getPLTBresult2exp().value+=">> Deliveries"+"\n"
        for ordname,myord in self.getDataManager().getCustomerOrders().items():
            self.getVisualManager().getPLTBresult2exp().value+="   ->"+ordname+": deadline "+str(myord.getDeadLine())+", planned delivery: "+str(myord.getPlannedDelivery())+"\n"
            if myord.getPlannedDelivery() is None:
                self.getVisualManager().getPLTBresult2exp().value+="Order "+myord.getName()+", not planned "+str(curr_deliverydate)+">>>> "+myord.getProduct().getName()+", reasons "+str(len(myord.getDelayReasons()))+"\n"
                for myprd,reason in myord.getDelayReasons().items():
                    self.getVisualManager().getPLTBresult2exp().value+="Prod "+myprd.getName()+", reason "+str(reason[0])+":"+str(reason[1])+"\n"

        #self.getVisualManager().getPLTBresult2exp().value+=">> CapacityUsePlans"+"\n"
        #for resame,myres in self.getDataManager().getResources().items():
            #if sum([x for x in myres.getCapacityUsePlan().values()]) > 0:
            #self.getVisualManager().getPLTBresult2exp().value+="   -> "+resame+": "+str([x for x in myres.getCapacityUsePlan().values()])+"\n"

        rawlist = []
        #self.getVisualManager().getPLTBresult2exp().value+=">> Required Stock levels"+"\n"
        sorteddict = dict(sorted(self.getDataManager().getProducts().items(), key=lambda item: -sum([x for x in item[1].getTargetLevels().values()])))
        for prodname,myprod in sorteddict.items():
            
            if len(myprod.getPredecessors()) == 0:
                rawlist.append(prodname)
                #self.getVisualManager().getPLTBresult2exp().value+="   -> Raw: "+prodname+", "+str([y for x,y in myprod.getTargetLevels().items()])+"\n"

        # self.getVisualManager().getPLTBrawlist().description = 'Raw Materials'
        self.getVisualManager().getPLTBrawlist().options = rawlist

        
        

        # self.getVisualManager().getPLTBresult2exp().value+=" Job creation starts.."+"\n"

        return


