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
import collections


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

    def FindDateGivenHrDrop(self,cr_date,hours,daycapacity):

        currentdate = cr_date; remainedtime = hours
        
        while remainedtime > daycapacity:   
            
            remainedtime-= daycapacity
            currentdate = currentdate - timedelta(days = 1)
             
            while currentdate.weekday() >= 5:
                currentdate = currentdate- timedelta(days = 1)
 

        return currentdate
        
   

    
    def CheckProduction(self,order,product,mydate,quantity):

        if len(product.getMPredecessors()) > 0: # bom 

            #self.getVisualManager().getPLTBresult2exp().value+=" In checking operations.. "+order.getName()+"\n"
            
            prodoprs = [p for p in product.getOperations()]
            reversedoprs = prodoprs[::-1]
            totaltime = 0  
   
            for operation in reversedoprs:

                if len(operation.getRequiredResources())>0:
                    resource = operation.getRequiredResources()[0]
                
                    totuse = ((int(resource.IsOutsource())+quantity*(1-int(resource.IsOutsource())))*operation.getProcessTime('min'))/60 # in hours
                    totaltime+=totuse
           

            currentdate = mydate
            remainedtime = int(totaltime)
       
            while remainedtime > 15: 
        
                remainedtime-= 15
                currentdate = currentdate - timedelta(days = 1)
                 
                while currentdate.weekday() >= 5:
                    currentdate = currentdate- timedelta(days = 1)

            newdate = currentdate

            #self.getVisualManager().getPLTBresult2exp().value+=" new date... "+order.getName()+"\n"
           
            if order.getLatestStart()== None:
                order.setLatestStart(newdate)
            else:
                if newdate < order.getLatestStart():
                    order.setLatestStart(newdate)  

            #self.getVisualManager().getPLTBresult2exp().value+=" check predecessors... "+order.getName()+"\n"
            
            for predecessor,multiplier in product.getMPredecessors().items():
                #self.getVisualManager().getPLTBresult2exp().value+=" predecessor... "+predecessor.getName()+", newdate: "+str(newdate)+", x: "+str(multiplier)+"\n"
                self.CheckProduction(order,predecessor,newdate,quantity*multiplier)
                
        else:
            #self.getVisualManager().getPLTBresult2exp().value+=" no preds product.. "+order.getName()+"\n"
            if order.getLatestStart()== None:
                order.setLatestStart(mydate)
            else:
                if mydate < order.getLatestStart():
                    order.setLatestStart(mydate) 

        #self.getVisualManager().getPLTBresult2exp().value+=" DONE... "+order.getName()+"\n"
        
        return

    def FindLS(self,order):

        #self.getVisualManager().getPLTBresult2exp().value+=" Finding LS.. "+order.getName()+"\n"
        
        self.CheckProduction(order,order.getProduct(),order.getDeadLine().date(),order.getQuantity())

        #self.getVisualManager().getPLTBresult2exp().value+=" Found LS.. "+order.getName()+"\n"

        return

    def PlanProduction(self,order,delvdate,product,mydate,quantity):

        #calculate use of resource for production for every operation
        #assume: one workday includes 16 hours of two shifts. 
        #assume: all production is done sequential in operations, no batch concept 

        
        if len(product.getMPredecessors()) > 0: # bom case
            prev_job = None
            prodoprs = [p for p in product.getOperations()]
            reversedoprs = prodoprs[::-1]

            
            for operation in reversedoprs: 
  
                myresource = None # now choose the resource that has most capacity
                avlcapacity = 0
                resource_use = 0

                # now find the resource that has the most capacity on the needed date.

                alternatives = []
                
                for res in operation.getRequiredResources():
                    alternatives.append(res)
                    for alt in res.getAlternatives():
                        if not alt in alternatives:
                            alternatives.append(alt)

                
                for resource in alternatives:

                    # neded capacity at (mydate)
                    totuse = ((int(resource.IsOutsource())+quantity*(1-int(resource.IsOutsource())))*operation.getProcessTime('min'))/60 # in hours 
                    curr_use = totuse

                    prev_val = None
                    new_val = 0

                    alldates = [d for d in resource.getCapacityReserved().keys()] 
                    allvalues = [v for v in resource.getCapacityReserved().values()]
                    if len(resource.getCapacityReserved()) > 0:
                        dtindex = -1
                        prevval = 0 
 
                        if mydate.date() >=  min(alldates): 
                         
                            maxmindate = max([d for d in alldates if d <= mydate.date()])
                            if maxmindate == mydate: 
                                allvalues = [allvalues[i] if alldates[i] < mydate.date() else allvalues[i]+totuse for i in range(len(alldates))]
                            else: 
                                dtindex = alldates.index(maxmindate)+1
                                prevval = allvalues[alldates.index(maxmindate)]
                        else: 
                            dtindex = 0

                        if dtindex > -1:   
                            alldates.insert(dtindex,mydate.date())
                            allvalues.insert(dtindex,prevval)
                            allvalues = [allvalues[i] if i < dtindex else allvalues[i]+totuse for i in range(len(alldates))]
                    else: 
                        allvalues.append(totuse)
                        alldates.append(mydate.date())


                    # now find the min diff
                    mindiff = min([resource.getCapacityLevels()[alldates[i]]-allvalues[i] for i in range(len(alldates)) ])

                    if mindiff < 0:
                        continue
                    else: 
                        
                        if avlcapacity <= mindiff:
                            myresource = resource
                            avlcapacity = mindiff
                            resource_use = curr_use
                   
                   
                if myresource == None:
                    self.getLogData()["Log_"+str(len(self.getLogData()))]="Insufficient capacity for "
                    order.getDelayReasons().append(str(delvdate.date())+ " No res, op "+str(operation.getName()[:min(15,len(operation.getName())-1)]))
                    return False
           

                if not myresource in order.getOrderPlan():
                    order.getOrderPlan()[myresource] = dict()
                order.getOrderPlan()[myresource][mydate.date()] = resource_use
                self.getLogData()["Log_"+str(len(self.getLogData()))]="Sufficient capacity for "

                self.getVisualManager().getPLTBresult2exp().value+=">Resource to plan: "+str(myresource.getName())+" <--> "+str(operation.getName())+"\n"

                remainedtime = resource_use

                daycapacity = myresource.getDailyCapacity()

                
                while remainedtime > daycapacity: 
                    if mydate < self.getPHStart():
                        order.getDelayReasons().append(str(delvdate.date())+ "Lead time goes to past")
                        return False
                    remainedtime-= daycapacity
                    mydate = mydate - timedelta(days = 1)
                    while mydate.weekday() >= 5:
                        mydate = mydate- timedelta(days = 1)


                
                jobid = self.getVisualManager().getSchedulingManager().getJobID()
                
                curr_job =  Job(jobid,"Job_"+str(jobid),product,operation,quantity,mydate)

                curr_job.setPlan((myresource,mydate))
                            
                if prev_job!= None:
                    curr_job.getSuccessors().append(prev_job)
                    prev_job.getPredecessors().append(curr_job)
                prev_job = curr_job
                curr_job.setCustomerOrder(order)  
                self.getVisualManager().getPLTBresult2exp().value+=">Job created: "+str(curr_job.getName())+", no.jobs: "+str(len(order.getMyJobs()))+"\n"

                order.getMyJobs().insert(0,curr_job)
                      
        for predecessor,multiplier in product.getMPredecessors().items():
            if not self.PlanProduction(order,delvdate,predecessor,mydate,quantity*multiplier):    
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
 
        self.getVisualManager().getPLTBmakeplan_btn().disabled = True
        # Create time-dependant lists: Capacity levels of resources, stock levels of raw materials

        #self.getVisualManager().getPLTBresult2exp().value+=">> Resources capacities.. "+str(len(self.getDataManager().getResources().items()))+"\n"
        daterange = pd.date_range(self.getPHStart(),self.getPHEnd())
   
        for ordname,myord in self.getDataManager().getCustomerOrders().items():
            myord.resetPlannedDelivery()

        for resname,res in self.getDataManager().getResources().items():
            res.getCapacityLevels().clear()
            res.getCapacityUsePlan().clear()
            res.getCapacityReserved().clear()
          
            cumulative_capacity = 0

            
            for curr_date in daterange:
                if curr_date.weekday() < 5:
                    if resname.find("OUT - ") != -1:
                        cumulative_capacity+= int(100000)
                    else:
                        cumulative_capacity+= res.getDailyCapacity()
                    
                res.getCapacityLevels()[curr_date.date()] = cumulative_capacity
               
     
        # Start planning 
        self.getVisualManager().getPLTBresult2exp().value+=">> Start planning orders..  "+str(len(self.getDataManager().getCustomerOrders()))+"\n"

        planned = 0
        OrderstoPlan = []

        for ordname,myord in self.getDataManager().getCustomerOrders().items():
           
            self.FindLS(myord)

            if not pd.isna(myord.getComponentAvailable()):
                if(myord.getComponentAvailable() == "Available") and (myord.getDeadLine() > self.getPHStart()):
                    
                    #if myord.getLatestStart() < self.getPHEnd().date(): 
                        OrderstoPlan.append(myord)        

        self.getVisualManager().getPLTBresult2exp().value+="Orders to plan>>>  "+str(len(OrderstoPlan))+"\n"
        
        for myord in OrderstoPlan:

            exp_date = self.getPHStart().date()

            self.getVisualManager().getPLTBresult2exp().value+=">Order: "+str(myord.getName())+"\n"

            if myord.getComponentAvailable().find("Exp") != -1:
                
                expected_date = myord.getComponentAvailable()
                expected_date = expected_date[expected_date.find("Exp")+4:]

                
                self.getVisualManager().getPLTBresult2exp().value+=">compav: "+str(myord.getComponentAvailable())+"\n"
                
                try: 
                    exp_date = datetime.strptime(expected_date,"%d/%m/%Y").date()
                except: 
                    pass

            self.getVisualManager().getPLTBresult2exp().value+=">deadline: "+str(myord.getDeadLine())+"\n"
               

            mindeliverydate = max(myord.getDeadLine().date(),exp_date)

            delay = 0
            for curr_deliverydate in pd.date_range(mindeliverydate,self.getPHEnd()):

                if curr_deliverydate.weekday() >= 5:
                    continue
    
                if self.PlanProduction(myord,curr_deliverydate,myord.getProduct(),curr_deliverydate,myord.getQuantity()):
                   
                    planned+=1
                    myord.setPlannedDelivery(curr_deliverydate)

                    self.getVisualManager().getPLTBresult2exp().value+="Planned: "+myord.getName()+", Jobs "+str(len(myord.getMyJobs()))+", Ops "+str(len(myord.getProduct().getOperations()))+"\n"

                    # update the reserved capacitiy values of resources.
                    for res,usedict in myord.getOrderPlan().items(): 
                        res.getCapacityUsePlan()[myord] = usedict

                        for mydt,myval in usedict.items(): 
                            
                            if not mydt in res.getCapacityReserved():
                                prev_vals = [v for d,v in res.getCapacityReserved().items() if d < mydt]
                                prev_max = 0
                                if len(prev_vals) > 0:     
                                    prev_max = max(prev_vals)
 
                                res.getCapacityReserved()[mydt] = myval+prev_max

                                for mydtm in res.getCapacityReserved().keys():
                                    if mydtm > mydt:
                                        res.getCapacityReserved()[mydtm]+=myval
   
                            else: 
                                for mydtm in res.getCapacityReserved().keys():
                                    if mydtm >= mydt:
                                        res.getCapacityReserved()[mydtm]+=myval
   
                    break
                    
                else:
                    myord.getOrderPlan().clear()
                    myord.getMyJobs().clear()
                    delay+=1

        ops = []
        
        for x in OrderstoPlan:
            if x.getPlannedDelivery() != None:
                ops.append(x.getName()+": "+str((x.getPlannedDelivery().date()-x.getDeadLine().date()).days))
                self.getVisualManager().getPLTBresult2exp().value+=x.getName()+": Jobs "+str(len(x.getMyJobs()))+"\n"

            else:
                ops.append(x.getName()+": "+"XXXXXX")
        self.getVisualManager().getPLTBOrdlist().options = ops

        #self.getDataManager().SavePlanning()

        reslist = [res.getName() for res in self.getDataManager().getResources().values()] 
        self.getVisualManager().getPLTBrawlist().options = reslist

        return


