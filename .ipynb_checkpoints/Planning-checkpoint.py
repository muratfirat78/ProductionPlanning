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

      

        self.getVisualManager().getPLTBresult2exp().value+="Planning production... for "+product.getName()+" -> Oprns "+str(len(product.getOperations()))+"\n"
       
        self.getVisualManager().getPLTBresult2exp().value+=str(type(mydate))+"  "+str(type(self.getPHStart()))+"\n"
        if mydate.date() < self.getPHStart():
            self.getVisualManager().getPLTBresult2exp().value+="XXXXX <  "+str(self.getPHStart())+"\n"
            return False
        
            
        
        if len(product.getMPredecessors()) == 0: # raw material case
            self.getVisualManager().getPLTBresult2exp().value+="Raw material... "+str(mydate in product.getTargetLevels())+"\n"        
            if mydate in product.getReservedStockLevels():
                product.getReservedStockLevels()[mydate]+=quantity
            else:
                product.getReservedStockLevels()[mydate]=quantity
        else:
            
            if mydate in product.getReservedStockLevels():
                product.getReservedStockLevels()[mydate]+=quantity
            else:
                product.getReservedStockLevels()[mydate]=quantity
            totaltime = 0 
            for operation in product.getOperations():
                
                resource_use = quantity*operation.getProcessTime() 
                self.getVisualManager().getPLTBresult2exp().value+="Oprn "+operation.getName()+" use " +str(resource_use)+"\n"
    
                
                totaltime+=resource_use
                self.getVisualManager().getPLTBresult2exp().value+=str(operation.getName())+">> "+str(len(operation.getRequiredResources()))+"\n"
                for resource in operation.getRequiredResources():
                    #self.getVisualManager().getPLTBresult2exp().value+="Resurce.. "+resource.getName()+"  "+str(mydate in resource.getCapacityLevels())+"\n"
    
                    if mydate in resource.getCapacityLevels():
                        self.getVisualManager().getPLTBresult2exp().value+="date in capacitylevels.."+"\n"

                        if mydate in resource.getCapacityReserved():
                            resource.getCapacityReserved()[mydate]+=resource_use
                        else:
                            resource.getCapacityReserved()[mydate] =resource_use

                        self.getVisualManager().getPLTBresult2exp().value+="cap reserved..."+str(resource.getName())+"-"+str(mydate)+str(resource.getCapacityReserved()[mydate])+":: "+str(resource_use)+"\n"

                        usedcapacity = 0
                        if mydate in resource.getCapacityUsePlan():
                            usedcapacity = resource.getCapacityUsePlan()[mydate]
                            
                            
                        if resource.getCapacityReserved()[mydate]+usedcapacity<= resource.getCapacityLevels()[mydate]:
                            #self.getVisualManager().getPLTBresult2exp().value+="capacitylevels ok.."+"\n"
                            self.getLogData()["Log_"+str(len(self.getLogData()))]="Sufficient capacity for "
                        else: 
                            self.getLogData()["Log_"+str(len(self.getLogData()))]="Insufficient capacity for "
                            return False
                    
            # calculate the change in date
           
            workdays = totaltime//16 + int(totaltime%16 > 0)
            self.getVisualManager().getPLTBresult2exp().value+="workdays.."+str(workdays)+"\n"
            newdate = mydate-  timedelta(days = workdays)
            self.getVisualManager().getPLTBresult2exp().value+="new date.."+str(newdate)+"\n"
            self.getVisualManager().getPLTBresult2exp().value+=">> "+str(newdate)+"--"+str(self.getPHStart())+"\n"
            if newdate.date()  < self.getPHStart():
                return False
                
        
     
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

        # START: here is your code to make planning 
        mydict = self.getDataManager().getCustomerOrders()
        sortedtuples = sorted(mydict.items(), key=lambda item: item[1].getDeadLine())
        mydict = {k: v for k, v in sortedtuples}
        self.getDataManager().setCustomerOrders(mydict)

        # determine planning horizon
        self.setPHStart(date.today()+timedelta(days=1)) 
        self.setPHEnd((sortedtuples[-1][1].getDeadLine()+timedelta(days=21)).date())  

        self.getVisualManager().getPLTBresult2exp().value+=">Planning Horizon: "+str(type(self.getPHStart()))+" <--> "+str(type(self.getPHEnd()))+"\n"
 

        self.getVisualManager().getPLTBresult2exp().value+=">Planning Horizon: "+str(self.getPHStart())+" <--> "+str(self.getPHEnd())+"\n"
 

        # Create time-dependant lists: Capacity levels of resources, stock levels of raw materials

        #self.getVisualManager().getPLTBresult2exp().value+=">> Resources capacities.. "+str(len(self.getDataManager().getResources().items()))+"\n"
        daterange = pd.date_range(self.getPHStart(),self.getPHEnd())

        for resname,res in self.getDataManager().getResources().items():
            res.getCapacityLevels().clear()
            
            cumulative_capacity = 0
          
            for curr_date in daterange:
                cumulative_capacity+= int(res.getDailyCapacity())
                res.getCapacityLevels()[curr_date] = cumulative_capacity
                res.getCapacityUsePlan()[curr_date] = 0

        for prname,prod in self.getDataManager().getProducts().items():
          
            prod.getTargetLevels().clear()
            prod.getReservedStockLevels().clear()
            for curr_date in daterange:
                prod.TargetLevels[curr_date] = 0
                
                
    
     
        # Start planning 
        #self.getVisualManager().getPLTBresult2exp().value+=">> Start planning orders..  "+str(len(self.getDataManager().getCustomerOrders()))+"\n"

        for ordname,myord in self.getDataManager().getCustomerOrders().items():

            
            for curr_deliverydate in pd.date_range(max(myord.getDeadLine().date(),self.getPHStart()),self.getPHEnd()):
           
               
                if self.PlanProduction(myord,myord.getProduct(),curr_deliverydate,myord.getQuantity()):
                    #self.getVisualManager().getPLTBresult2exp().value+="No issue in production for "+myord.getName()+"\n"
                    #self.getLogData()["Log_"+str(len(self.getLogData()))]="No issue in production for "+myord.getName()

                    #self.getVisualManager().getPLTBresult2exp().value+="Order "+myord.getName()+", planned "+str(curr_deliverydate)+">>>> "+myord.getProduct().getName()+"\n"
    
                    myord.setPlannedDelivery(curr_deliverydate)
               
                    # apply resource use plan
                    for resname,res in self.getDataManager().getResources().items():
                        #self.getVisualManager().getPLTBresult2exp().value+="res "+res.getName()+": "+str( res.getCapacityReserved().values())+"\n"
                        for mydate,val in res.getCapacityReserved().items():
                            #self.getVisualManager().getPLTBresult2exp().value+=str(mydate)+">>>"+str(self.getPHEnd())+"\n"
                            #self.getVisualManager().getPLTBresult2exp().value+="****list "+str([x for x in res.getCapacityUsePlan().keys()])+"\n"
                            for curr_date in pd.date_range(mydate,self.getPHEnd()):

                                if not curr_date in res.getCapacityUsePlan():
                                    self.getVisualManager().getPLTBresult2exp().value+="****date "+str(curr_date)+"\n"
                                    
                                res.getCapacityUsePlan()[curr_date]+=val
                           
                    # update target stock levels
                    #self.getVisualManager().getPLTBresult2exp().value+="stock levels... "+"\n"
                    for prname,prod in self.getDataManager().getProducts().items():
                    
                        for mydate,lvl in prod.getReservedStockLevels().items():
                            for curr_date in pd.date_range(mydate,self.getPHEnd()):
                                if not curr_date in prod.getTargetLevels():
                                    self.getVisualManager().getPLTBresult2exp().value+="****date "+str(curr_date)+"\n"
                                prod.getTargetLevels()[curr_date]+= lvl
                        prod.getReservedStockLevels().clear()
                    break
                                
                else:
                    #self.getLogData()["Log_"+str(len(self.getLogData()))]="Issue in production for "+myord.getName()
                    #self.getVisualManager().getPLTBresult2exp().value+="Issue in production for "+myord.getName()+"\n"
                    #self.getVisualManager().getPLTBresult2exp().value+="Order "+myord.getName()+", not planned "+str(curr_deliverydate)+">>>> "+myord.getProduct().getName()+"\n"
                    for resname,res in self.getDataManager().getResources().items():
                        res.getCapacityReserved().clear()
    
                    for prname,prod in self.getDataManager().getProducts().items():
                        if len(prod.getMPredecessors()) > 0: 
                            continue
                        prod.getReservedStockLevels().clear()
                
     
    
        # END: here is your code to make planning 
        self.getVisualManager().getPLTBresult2exp().value+=">> Deliveries"+"\n"
        for ordname,myord in self.getDataManager().getCustomerOrders().items():
            self.getVisualManager().getPLTBresult2exp().value+="   ->"+ordname+": deadline "+str(myord.getDeadLine())+", planned delivery: "+str(myord.getPlannedDelivery())+"\n"

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

        self.getVisualManager().getPLTBrawlist().description = 'Raw Materials'
        self.getVisualManager().getPLTBrawlist().options = rawlist

        
        

        self.getVisualManager().getPLTBresult2exp().value+=" Job creation starts.."+"\n"

        opslist = []
        
        for prname,prod in self.getDataManager().getProducts().items():
          
            produced_level = 0
            
        
            orginalList = prod.getOperations()

            if len(orginalList) == 0:
                continue

            reversed_ops = orginalList[::-1]  

            demandcurve = list(prod.getTargetLevels().items())

            totaldmd = 0
            if len(demandcurve) > 0:
                totaldmd=[val for dt,val in demandcurve][-1]

            if totaldmd == 0:
                continue

            opslist.append(prod.getName()) 
            self.getVisualManager().getPLTBresult2exp().value+=" Prod->"+str(prod.getName())+", dmd: "+str(totaldmd)+"\n"
            #self.getVisualManager().getPLTBresult2exp().value+=" Pr "+prod.getName()+", Trglvls: "+str(len(prod.getTargetLevels()))+", No.Ops: "+str(len(prod.getOperations()))+".."+", dmd: "+str(totaldmd)+", size: "+str(len(demandcurve))+"\n"

            #self.getVisualManager().getPLTBresult2exp().value+="Initial demand curve: "+str([val for dt,val in demandcurve])+"\n"

            prev_opr = None
            for operation in reversed_ops:

                oprbtchsize = operation.getBatchSize()
                prev_job = None
                self.getVisualManager().getPLTBresult2exp().value+="> Opr: "+str(operation.getName())+"\n"
          
                if not prev_opr is None:
                    orgjoblist = prev_opr.getJobs()
                    reversed_jobs = orgjoblist[::-1]  

                    totaljobsize = 0
                    cum_jobneed = 0
                    valiter = 0
                    for job in reversed_jobs:
                        valiter+=1
                        cum_jobneed+=job.getQuantity()

                        #self.getVisualManager().getPLTBresult2exp().value+="SuccJob "+job.getName()+", q "+str(job.getQuantity())+", d "+str(job.getDeadLine())+"\n"
                        if (cum_jobneed - totaljobsize >= oprbtchsize) or ((valiter == len(reversed_jobs)) and (cum_jobneed - totaljobsize > 0 ) ):
                            jobsize =oprbtchsize*((cum_jobneed - totaljobsize)//oprbtchsize)+oprbtchsize*int((cum_jobneed - totaljobsize)%oprbtchsize > 0)   

                            deadline = job.getLatestStart()
                            #self.getVisualManager().getPLTBresult2exp().value+=" job to create "+operation.getName()+", "+str(val)+":"+str(totaljobsize)+", q: "+str(jobsize)+", BTCH: "+str(oprbtchsize)+", proctime "+str(operation.getProcessTime())+", iter: "+str(valiter)+", dl "+str(deadline)+"\n" 

                   
                            jobid = self.getDataManager().getJobID()
                            myjob =  Job(jobid,"Job_"+str(jobid),prod,operation,jobsize,deadline)
                            myjob.setLatestStart(myjob.getDeadLine() - timedelta(hours = jobsize*operation.getProcessTime()))
                            self.getVisualManager().getPLTBresult2exp().value+=" >> "+myjob.getName()+", q: "+str(myjob.getQuantity())+", d: "+str(myjob.getDeadLine())+"\n" 

                            totaljobsize+=jobsize
                            operation.getJobs().insert(0,myjob)
                         
         
                else:
                    valiter = 0
                    newdmdcurve = []
                    newval = 0
                    for mydate,val in demandcurve:
                        valiter+=1
                        totaljobsize = 0
                        
                        if len(operation.getJobs()) > 0:
                            totaljobsize = sum([jb.getQuantity() for jb in operation.getJobs()])
                            
    
                        if (val - totaljobsize >= oprbtchsize) or ((demandcurve[-1][1] == val) and (val - totaljobsize > 0 ) ):
    
                           
                            jobsize =oprbtchsize*((val - totaljobsize)//oprbtchsize)+oprbtchsize*int((val - totaljobsize)%oprbtchsize > 0)  
                            deadline = datetime.combine(datetime.date(mydate), time(0, 0, 0)) #hr/min/sec
    
                            #self.getVisualManager().getPLTBresult2exp().value+=" job to create "+operation.getName()+", "+str(val)+":"+str(totaljobsize)+", q: "+str(jobsize)+", BTCH: "+str(oprbtchsize)+", proctime "+str(operation.getProcessTime())+", iter: "+str(valiter)+", dl "+str(deadline)+"\n" 
                            jobid = self.getDataManager().getJobID()
                            myjob =  Job(jobid,"Job_"+str(jobid),prod,operation,jobsize,deadline)
                            myjob.setLatestStart(myjob.getDeadLine() - timedelta(hours = jobsize*operation.getProcessTime()))
                            self.getVisualManager().getPLTBresult2exp().value+=" >> "+myjob.getName()+", q: "+str(myjob.getQuantity())+", d: "+str(myjob.getDeadLine())+"\n" 
                            newval+=jobsize
    
                            #self.getVisualManager().getPLTBresult2exp().value+=" Job->"+str(prod.getName())+", "+str(operation.getName())+", Q:"+str(jobsize)+"\n"
                            operation.getJobs().append(myjob)
                            prev_job = myjob

                        
                    newdmdcurve.append((mydate,newval))

                
                demandcurve = newdmdcurve
                prev_opr = operation
                

        #self.getVisualManager().getPLTBCheckRaw().value = 
        self.getVisualManager().getPLTBresult2exp().value+="-> Products"+str(len(opslist))+"\n"
        self.getVisualManager().getPSchResources().options = [op for op in opslist] 

        return 

    def MakeSchedule(self,b):  

        


        

        return

