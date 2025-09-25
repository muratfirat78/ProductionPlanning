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
                
                    totuse = ((int(resource.IsOutsource())+quantity*(1-int(resource.IsOutsource())))*operation.getProcessTime())/60 # in hours
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

    def PlanProduction(self,order,delvdate,product,mydate,quantity,lvl,delay):

        #calculate use of resource for production for every operation
        #assume: one workday includes 16 hours of two shifts. 
        #assume: all production is done sequential in operations, no batch concept 

        #self.getVisualManager().getPLTBresult2exp().value+=" "+str(lvl)+" St ==> "+product.getName()+",Preds "+str(len(product.getMPredecessors()))+": "+str(mydate)+"\n"


        if not product in order.getOrderPlan()['Products']:
            order.getOrderPlan()['Products'][product] = dict()
        order.getOrderPlan()['Products'][product][mydate.date()] = quantity

        
        quantity = quantity/product.getStockBatch()

        self.getVisualManager().getPLTBresult2exp().value+=" Q: "+str(quantity)+"\n"

  
        if mydate.date() in product.getReservedStockLevels():
            product.getReservedStockLevels()[mydate.date()]+=quantity
        else:
            product.getReservedStockLevels()[mydate.date()]=quantity

      
        #self.getVisualManager().getPLTBresult2exp().value+="ops.. "+str(len(product.getOperations()))+"\n"
       
        #self.getVisualManager().getPLTBresult2exp().value+=str(type(mydate))+"  "+str(type(self.getPHStart()))+"\n"
        if mydate.date() < self.getPHStart().date():
            #self.getVisualManager().getPLTBresult2exp().value+="XXXXX <  "+str(self.getPHStart())+"\n"
            order.getDelayReasons()[delvdate.date()]=str(product.getPN())+"-> Lead time "+str(mydate.date())
            return False

        
        #self.getVisualManager().getPLTBresult2exp().value+="not in past.. "+"\n"
        totaltime = 0  
        
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

                    totuse = ((int(resource.IsOutsource())+quantity*(1-int(resource.IsOutsource())))*operation.getProcessTime())/60 # in hours 
                    
                    if (resource.IsOutsource()) and (len(operation.getRequiredResources()) == 1):
                        myresource = resource
                        resource_use = totuse
                        #self.getVisualManager().getPLTBresult2exp().value+="Op "+str(operation.getName())+", OUTres:  "+str(myresource.getName())+", use: "+str(resource_use)+"\n"
                        break
                    
                 
                    totuse =  int(totuse)+int(totuse-int(totuse) > 0)
                    
                    curr_use = totuse
                    
                    
                    for cust_ordr,usedict in resource.getCapacityUsePlan().items():
                        totuse+=sum([v for cd,v in usedict.items() if cd <= mydate.date()])
                    if resource in order.getOrderPlan()['Resources']:
                        totuse+=sum([v for cd,v in order.getOrderPlan()['Resources'][resource].items() if cd <= mydate.date()])


                  
                    if avlcapacity <= resource.getCapacityLevels()[mydate.date()] - totuse:
                        myresource = resource
                        avlcapacity = resource.getCapacityLevels()[mydate.date()] - totuse
                        resource_use = curr_use
                    
                        
                   
                if myresource == None:
                    #self.getVisualManager().getPLTBresult2exp().value+="No feasible res found for op "+str(operation.getName())+"\n" 
                    self.getLogData()["Log_"+str(len(self.getLogData()))]="Insufficient capacity for "
                    order.getDelayReasons()[delvdate.date()] = str(product.getPN())+"XXXX: No resource for op "+str(operation.getName())+" on "+str(mydate.date())
                    return False
                else:
                    #self.getVisualManager().getPLTBresult2exp().value+="Op "+str(operation.getName())+", alts: "+str(len(alternatives))+", res: "+str(myresource.getName())+", use: "+str(resource_use)+"\n"
                    pass

                if not myresource in order.getOrderPlan()['Resources']:
                    order.getOrderPlan()['Resources'][myresource] = dict()
                order.getOrderPlan()['Resources'][myresource][mydate.date()] = resource_use
                self.getLogData()["Log_"+str(len(self.getLogData()))]="Sufficient capacity for "

                jobid = self.getVisualManager().getSchedulingManager().getJobID()
                
                curr_job =  Job(jobid,"Job_"+str(jobid),product,operation,quantity,mydate)
                            
                if prev_job!= None:
                    prev_job.getSuccessors().append(curr_job)
                    curr_job.getPredecessors().append(prev_job)
                prev_job = curr_job
                curr_job.setCustomerOrder(order)       
                order.getMyJobs().append(curr_job)
                totaltime+=resource_use
                      
            #self.getVisualManager().getPLTBresult2exp().value+="total time...."+str(totaltime)+"\n" 
           
            #newdate = FindDateGivenHrDrop(mydate,int(totaltime),15)

            currentdate = mydate
            remainedtime = int(totaltime)
            #self.getVisualManager().getPLTBresult2exp().value+="mydate...."+str(mydate)+"\n" 
        
            while remainedtime > 15: 
                
                #self.getVisualManager().getPLTBresult2exp().value+="date...."+str(currentdate)+", remainedtime.. "+str(remainedtime)+"\n" 
                
                remainedtime-= 15
                currentdate = currentdate - timedelta(days = 1)
                 
                while currentdate.weekday() >= 5:
                    currentdate = currentdate- timedelta(days = 1)

                if currentdate < self.getPHStart():
                    #self.getVisualManager().getPLTBresult2exp().value+="XXXX: latest start in past...."+str(currentdate)+"\n" 
                    order.getDelayReasons()[delvdate.date()] = str(product.getPN())+"-> Lead time goes to past "
                    return False

            newdate = currentdate

            if newdate < self.getPHStart():
                #self.getVisualManager().getPLTBresult2exp().value+="XXXX: latest start in past...."+str(currentdate)+"\n" 
                order.getDelayReasons()[delvdate.date()] = str(product.getPN())+"-> Lead time goes to past "
                return False

           
            #self.getVisualManager().getPLTBresult2exp().value+="newdate...."+str(newdate)+"\n" 

       
        #self.getVisualManager().getPLTBresult2exp().value+="checking predecessors.. "+str(len(product.getMPredecessors()))+"\n" 
        for predecessor,multiplier in product.getMPredecessors().items():
                #self.getVisualManager().getPLTBresult2exp().value+="predecessor.."+str(predecessor.getName())+"\n"
            if not self.PlanProduction(order,delvdate,predecessor,newdate,quantity*multiplier,lvl+1,delay):    
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
        #self.getVisualManager().getPLTBresult2exp().value+=">: "+str(type(self.getPHStart()))+" <--> "+str(type(self.getPHEnd()))+"\n"
 
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
        OrderstoPlan = []

        for ordname,myord in self.getDataManager().getCustomerOrders().items():
            #self.getVisualManager().getPLTBresult2exp().value+="Order: "+str(myord.getName())+", av: "+str(myord.getComponentAvailable())+", d: "+str(myord.getDeadLine().date())+"\n"
            
            self.FindLS(myord)

            #self.getVisualManager().getPLTBresult2exp().value+="Order: "+str(myord.getName())+", d: "+str(myord.getDeadLine().date())+", ls: "+str(myord.getLatestStart())+"\n"
            #self.getVisualManager().getPLTBresult2exp().value+=">: "+str(type(myord.getLatestStart()))+" <--> "+str(type(self.getPHEnd()))+"\n"
 

            

            if not pd.isna(myord.getComponentAvailable()):
                if(myord.getComponentAvailable() == "Available") and (myord.getDeadLine() > self.getPHStart()):
                    if myord.getLatestStart() < self.getPHEnd().date():
                        OrderstoPlan.append(myord)        

        self.getVisualManager().getPLTBresult2exp().value+="Orders to plan>>>  "+str(len(OrderstoPlan))+"\n"
        
        for myord in OrderstoPlan:

            self.getVisualManager().getPLTBresult2exp().value+="__________________________________ "+"\n"

            self.getVisualManager().getPLTBresult2exp().value+="Order: "+str(myord.getName())+", d: "+str(myord.getDeadLine())+"\n"

            self.getVisualManager().getPLTBresult2exp().value+=" Component.. "+str(myord.getComponentAvailable())+"\n"
            

            exp_date = self.getPHStart().date()

            
            if myord.getComponentAvailable().find("Exp") != -1:
                expected_date = myord.getComponentAvailable()
                expected_date = expected_date[expected_date.find("Exp")+4:]
                self.getVisualManager().getPLTBresult2exp().value+=">> expected_date..  "+str(expected_date)+"\n"
                try: 
                    exp_date = datetime.strptime(expected_date,"%d/%m/%Y").date()
                except: 
                    pass

            self.getVisualManager().getPLTBresult2exp().value+=" expdate.. "+str(exp_date)+"\n"
            
            mindeliverydate = max(myord.getDeadLine().date(),exp_date)

            self.getVisualManager().getPLTBresult2exp().value+=" mindeliverydate.. "+str(mindeliverydate)+"\n"
   
            delay = 0
            for curr_deliverydate in pd.date_range(mindeliverydate,self.getPHEnd()):

                
                if curr_deliverydate.weekday() >= 5:
                    continue

                self.getVisualManager().getPLTBresult2exp().value+="---------------------------------------"+"\n"
    
                if self.PlanProduction(myord,curr_deliverydate,myord.getProduct(),curr_deliverydate,myord.getQuantity(),1,delay):
                   
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
        
        for x in OrderstoPlan:
            if x.getPlannedDelivery() != None:
                ops.append(x.getName()+": "+str((x.getPlannedDelivery().date()-x.getDeadLine().date()).days))
            else:
                ops.append(x.getName()+": "+"XXXXXX")
        self.getVisualManager().getPLTBOrdlist().options = ops

        
        # END: here is your code to make planning 
        # self.getVisualManager().getPLTBresult2exp().value+=">> Deliveries"+"\n"
        #for ordname,myord in self.getDataManager().getCustomerOrders().items():
            #self.getVisualManager().getPLTBresult2exp().value+="   ->"+ordname+": deadline "+str(myord.getDeadLine())+", planned delivery: "+str(myord.getPlannedDelivery())+"\n"
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


