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
        self.Weeks = dict() #key week no, val: list of days
    
    
   
    def setDataManager(self,DataMgr):
        self.DataManager = DataMgr 
        return

    def getJobs(self):
        return 

    def getWeeks(self):
        return self.Weeks
        
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

    def PlanProduction(self,order,delvdate,product,mydate,quantity,lvl,timecheck,delay):

        #calculate use of resource for production for every operation
        #assume: one workday includes 16 hours of two shifts. 
        #assume: all production is done sequential in operations, no batch concept 

        self.getVisualManager().getPLTBresult2exp().value+=" "+str(lvl)+" St ==> "+product.getName()+",Prs "+str(len(product.getMPredecessors()))+": "+str(mydate)+"\n"


        if not product in order.getOrderPlan()['Products']:
            order.getOrderPlan()['Products'][product] = dict()
        order.getOrderPlan()['Products'][product][mydate.date()] = quantity

        
        quantity = quantity/product.getStockBatch()

        #self.getVisualManager().getPLTBresult2exp().value+=" Q: "+str(quantity)+"\n"

        #self.getVisualManager().getPLTBresult2exp().value+=" resvlvls?: "+str(mydate.date() in product.getReservedStockLevels())+"\n"


        if mydate.date() in product.getReservedStockLevels():
            product.getReservedStockLevels()[mydate.date()]+=quantity
        else:
            product.getReservedStockLevels()[mydate.date()]=quantity

        #if len(product.getOperations()) == 0:
      
       
        #self.getVisualManager().getPLTBresult2exp().value+=str(type(mydate))+"  "+str(type(self.getPHStart()))+"\n"
        if mydate.date() < self.getPHStart():
            self.getVisualManager().getPLTBresult2exp().value+="XXXXX <  "+str(self.getPHStart())+"\n"
            order.getDelayReasons()[delvdate.date()]=str(product.getPN())+"-> Lead time "+str(mydate.date())
            return False

        
        #self.getVisualManager().getPLTBresult2exp().value+="not in past.. "+"\n"
        totaltime = 0   
        if len(product.getMPredecessors()) > 0: # bom case
            
            #self.getVisualManager().getPLTBresult2exp().value+="ops.. "+str(len(product.getOperations()))+"\n"
            prev_job = None
            reversedoprs = [p for p in product.getOperations()]
            reversedoprs = reversedoprs[::-1]
            for operation in reversedoprs: # doubkle-check that they are in reversed order!!!!
                

                # skip quantity when resource is outsourced:

                curr_quantity = quantity    
                for resource in operation.getRequiredResources():
                    myresource = resource
                    if isinstance(resource,list):
                        myresource = resource[0]
                    if myresource.IsOutsource():
                        curr_quantity = 1
                        break
     
                resource_use = curr_quantity*operation.getProcessTime() # in hours 
                
                
                resource_use =  int(resource_use)+int(resource_use-int(resource_use) > 0)

                #self.getVisualManager().getPLTBresult2exp().value+="op.. "+operation.getName()+", resuse: "+str(resource_use)+"\n"
                
                totaltime+=resource_use
                # self.getVisualManager().getPLTBresult2exp().value+=str(operation.getName())+">> "+str(len(operation.getRequiredResources()))+"\n"
                for resource in operation.getRequiredResources():

                    myresource = resource
                    if isinstance(resource,list):
                        myresource = resource[0] # here first one among alternatives is selected, if there are some..
                       
                    #self.getVisualManager().getPLTBresult2exp().value+="res.. "+myresource.getName()+", mydate"+str(mydate)+"\n"


                    totuse = 0; totres = 0
                    
                    #self.getVisualManager().getPLTBresult2exp().value+="res cap check.... "+myresource.getName()+", mydate "+str(mydate)+"\n"

                    if not myresource.IsOutsource():
                        for cust_ordr,usedict in myresource.getCapacityUsePlan().items():
                            for checkdate,useval in usedict.items():
                                if checkdate <= mydate.date():
                                    totuse+=useval
                        #self.getVisualManager().getPLTBresult2exp().value+="totuse.... "+str(totuse)+"\n"
                        if myresource in order.getOrderPlan()['Resources']:
                            for checkdate,useval in order.getOrderPlan()['Resources'][myresource].items():
                                if checkdate <= mydate.date():
                                    totres+=useval
                        #self.getVisualManager().getPLTBresult2exp().value+="totres.... "+str(totres)+"\n"
    
                        
                        
                        if myresource.getCapacityLevels()[mydate.date()] < totuse+totres+resource_use:
                            self.getLogData()["Log_"+str(len(self.getLogData()))]="Insufficient capacity for "
                            order.getDelayReasons()[delvdate.date()] = str(product.getPN())+"-> "+myresource.getName()+" Cap: "+str(mydate.date())
                            return False
                        else:
                            #self.getVisualManager().getPLTBresult2exp().value+="res cap ok ... "+myresource.getName()+", mydate"+str(mydate)+"\n"
                            if not myresource in order.getOrderPlan()['Resources']:
                                order.getOrderPlan()['Resources'][myresource] = dict()
                            order.getOrderPlan()['Resources'][myresource][mydate.date()] = resource_use
                            self.getLogData()["Log_"+str(len(self.getLogData()))]="Sufficient capacity for "
                            jobid = self.getVisualManager().getSchedulingManager().getJobID()
                            curr_job =  Job(jobid,"Job_"+str(jobid),product,operation,curr_quantity,mydate)
                            
                            if prev_job!= None:
                                prev_job.getSuccessors().append(curr_job)
                                curr_job.getPredecessors().append(prev_job)
                            prev_job = curr_job
                            curr_job.setCustomerOrder(order)
                                
                            order.getMyJobs().append(curr_job)
                             
                                    
  
            totalhours =  int(totaltime)+int(totaltime-int(totaltime) > 0)

            currentdate = mydate; remainedtime = totalhours
            
            while remainedtime > 0:
                #self.getVisualManager().getPLTBresult2exp().value+="remainedtime.. "+str(remainedtime)+"\n"

                if currentdate.hour == 0:
                    timeofday = 16
                else: 
                    timeofday = currentdate.hour - 8
                    
                currentdate = currentdate - timedelta(hours = min(timeofday,remainedtime))
                remainedtime = max(remainedtime - timeofday,0) 

                #self.getVisualManager().getPLTBresult2exp().value+="currentdate.. "+str(currentdate)+"\n"


                if currentdate.hour == 8:
                    currentdate = currentdate - timedelta(hours = 8)
                    #self.getVisualManager().getPLTBresult2exp().value+="drop 8 hours.. "+str(currentdate)+"\n"

                while currentdate.weekday() >= 5:
                    currentdate = currentdate- timedelta(days = 1)
                    #self.getVisualManager().getPLTBresult2exp().value+="drop weekend.. "+str(currentdate)+"\n"
      
            newdate = currentdate # set new date 

            if timecheck:
                self.getVisualManager().getPLTBresult2exp().value+="mydate.. "+str(mydate)+"\n"
                self.getVisualManager().getPLTBresult2exp().value+="totalhours.. "+str(totalhours)+"\n"
                self.getVisualManager().getPLTBresult2exp().value+="newdate.. "+str(newdate)+"\n"


            #self.getVisualManager().getPLTBresult2exp().value+=" End  ==> "+product.getName()+":"+str(newdate)+"\n"

            
            if newdate.date()  < self.getPHStart():
                order.getDelayReasons()[delvdate.date()] = str(product.getPN())+"-> Lead time "+str(newdate.date())
                return False

            if order.getLatestStart()== None:
                order.setLatestStart(newdate)
            else:
                if newdate < order.getLatestStart():
                    order.setLatestStart(newdate)                
       
      
        for predecessor,multiplier in product.getMPredecessors().items():
                #self.getVisualManager().getPLTBresult2exp().value+="predecessor.."+str(predecessor.getName())+"\n"
            if not self.PlanProduction(order,delvdate,predecessor,newdate,quantity*multiplier,lvl+1,timecheck,delay):    
                return False
    
        return True
        

    

    def MakeDeliveryPlan(self,b):
        ''' This function construct a delivery plan for every customer orders as follows: 
            - Customer Orders have priority due to their deadlines; i.e. the customer order with soonest deadline must be planned first. 
            - The primary goal is to plan customer orders without any delay. If the delivery of a customer order should be with some delay, then it loses itspriority compared to all other cutomer orders to be planned.  
            - The combined required capacity levels of planned customer orders should respect to the capacity levels of all resources.
            - Every raw material can be purchased at most certain amount in every week. The required raw material levels of planned customer orders should be feasible by possibly purchasing additional amount of raw materials for every week.  

            INPUT: 
            1) Customer orders, 2) Planning Period, 3) BOMs or products
            OUTPUT:
            1) Delivery date of Customer orders, 2) Target Levels of Products, 3) Capacity use plan of resources
            
        '''

        
        mydict = self.getDataManager().getCustomerOrders()
        sortedtuples = sorted(mydict.items(), key=lambda item: item[1].getDeadLine())
        mydict = {k: v for k, v in sortedtuples}
        self.getDataManager().setCustomerOrders(mydict)

        # determine planning horizon
        phstart = self.getPHStart()

        if phstart.weekday() > 0:
            phstart = phstart+timedelta(days=7-phstart.weekday())

        self.getVisualManager().getPLTBresult2exp().value+=">Planning start: "+str(phstart)+"\n"
 
        self.setPHStart(phstart) 

        self.getVisualManager().getPLTBresult2exp().value+=">Planning Horizon: "+str(self.getPHStart())+" <--> "+str(self.getPHEnd())+"\n"
 

        # Create time-dependant lists: Capacity levels of resources, stock levels of raw materials

        #self.getVisualManager().getPLTBresult2exp().value+=">> Resources capacities.. "+str(len(self.getDataManager().getResources().items()))+"\n"
        daterange = pd.date_range(self.getPHStart(),self.getPHEnd())
        self.getVisualManager().getPLTBresult2exp().value+=">: "+str(type(self.getPHStart()))+" <--> "+str(type(self.getPHEnd()))+"\n"
 
        for ordname,myord in self.getDataManager().getCustomerOrders().items():
            myord.resetPlannedDelivery()

        for resname,res in self.getDataManager().getResources().items():
            res.getCapacityLevels().clear()
            res.getCapacityUsePlan().clear()
          
            
            cumulative_capacity = 0

            
            for curr_date in daterange:
                if curr_date.weekday() < 5:
                    if resname.find("OUT - ") != -1:
                        cumulative_capacity+= int(100000)
                    else:
                        cumulative_capacity+= int(res.getDailyCapacity()*8)
                    
                res.getCapacityLevels()[curr_date.date()] = cumulative_capacity
               

        for prname,prod in self.getDataManager().getProducts().items():
            #prod.getDemandingOrders().clear()
            prod.getTargetLevels().clear()
            prod.getReservedStockLevels().clear()
            for curr_date in daterange:
                prod.TargetLevels[curr_date.date()] = 0
                
     
        # Start planning 
        self.getVisualManager().getPLTBresult2exp().value+=">> Start planning orders..  "+str(len(self.getDataManager().getCustomerOrders()))+"\n"

        planned = 0
      
        
        for ordname,myord in self.getDataManager().getCustomerOrders().items():

            self.getVisualManager().getPLTBresult2exp().value+="Order: "+str(myord.getName())+"\n"
            if myord.getComponentAvailable() == "Not Available":
                self.getVisualManager().getPLTBresult2exp().value+="Component not available.. "+"\n"
                continue # this order cannot start due to missing component

            start_date = self.getPHStart()+timedelta(days=1)

            if myord.getComponentAvailable().find("Exp") != -1:
                expected_date = myord.getComponentAvailable()
                expected_date = expected_date[expected_date.find("Exp")+4:]
                self.getVisualManager().getPLTBresult2exp().value+=">> expected_date..  "+str(expected_date)+"\n"
     
            

            mindeliverydate = max(myord.getDeadLine().date(),self.getPHStart())+timedelta(days=1)

            
            delay = 0
            for curr_deliverydate in pd.date_range(mindeliverydate,self.getPHEnd()):
                if curr_deliverydate.weekday() >= 5:
                    continue

                timecheck =  planned < 3
            
                #self.getVisualManager().getPLTBresult2exp().value+="delvdate iteration.. "+str(curr_deliverydate)+"\n"
              
   
                if self.PlanProduction(myord,curr_deliverydate,myord.getProduct(),curr_deliverydate,myord.getQuantity(),1,timecheck,delay):
                   
                    planned+=1
                    myord.setPlannedDelivery(curr_deliverydate)

                   # apply resource use plan: convert reserved capacity use to actual capacity use.

                    #self.getVisualManager().getPLTBresult2exp().value+="planned!!! "+str(curr_deliverydate)+"\n"
              
                   
                    for res,usedict in myord.getOrderPlan()['Resources'].items(): 
                        res.getCapacityUsePlan()[myord] = usedict
                
                    #self.getVisualManager().getPLTBresult2exp().value+="resources done.. "+str(curr_deliverydate)+"\n"
                     
                    #self.getVisualManager().getPLTBresult2exp().value+="update.... prods "+"\n"         
                    # update target stock levels: convert tentative stock levels to target stock levels. 

                    #self.getVisualManager().getPLTBresult2exp().value+="products "+str(len(myord.getOrderPlan()['Products']))+"\n"
                    for prod,usedict in myord.getOrderPlan()['Products'].items():
                        #self.getVisualManager().getPLTBresult2exp().value+="usedict "+str(len(usedict))+"\n"

                        
   
                        prod.getDemandingOrders()[myord]=sum([lvl for mydate,lvl in usedict.items()])
                        for mydate,val in usedict.items():
                            
                            #Eself.getVisualManager().getPLTBresult2exp().value+=str(mydate)+":"+str(val)+"\n"

                            #self.getVisualManager().getPLTBresult2exp().value+="range type: "+str(type(mydate))+"\n" #+str(type(self.getPHEnd()))+"\n"
                            
                            for curr_date in pd.date_range(mydate,self.getPHEnd()):

                                
                                if curr_date.date() in prod.getTargetLevels():
                                    prod.getTargetLevels()[curr_date.date()]+= val
                                else:
                                    self.getVisualManager().getPLTBresult2exp().value+=str(curr_date.date())+" is not in target levels"+"\n"
                    #self.getVisualManager().getPLTBresult2exp().value+="break.. "+"\n"
                    #self.getVisualManager().getPLTBresult2exp().value+="products done..."+"\n"
                    break
                else:
                    myord.resetOrderPlan()
                    myord.getMyJobs().clear()
                    delay+=1

        self.getVisualManager().getPLTBresult2exp().value+=">> Completed..  planned: "+str(planned)+"/"+str(len(self.getDataManager().getCustomerOrders()))+"\n"
        custordlist = [myord for myord in self.getDataManager().getCustomerOrders().values()]
        #custordlist_strd = sorted(custordlist, key=lambda x: (x.getPlannedDelivery()-max(x.getDeadLine().date(),self.getPHStart())).days, reverse=True)

        ops = []
        
        for x in custordlist:
            if x.getPlannedDelivery() != None:
                ops.append(x.getName()+": "+str((x.getPlannedDelivery().date()-max(x.getDeadLine().date(),self.getPHStart())).days-1))
            else:
                ops.append(x.getName()+": "+"XXXXXX")
        self.getVisualManager().getPLTBOrdlist().options = ops

        
        # END: here is your code to make planning 
        # self.getVisualManager().getPLTBresult2exp().value+=">> Deliveries"+"\n"
        for ordname,myord in self.getDataManager().getCustomerOrders().items():
            self.getVisualManager().getPLTBresult2exp().value+="   ->"+ordname+": deadline "+str(myord.getDeadLine())+", planned delivery: "+str(myord.getPlannedDelivery())+"\n"
        #self.getVisualManager().getPLTBresult2exp().value+=">> CapacityUsePlans"+"\n"


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


