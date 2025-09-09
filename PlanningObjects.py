# -*- coding: utf-8 -*-

##### import ipywidgets as widgets
from IPython.display import clear_output
from IPython import display
from ipywidgets import *
from datetime import timedelta,date,datetime
import matplotlib.pyplot as plt
import warnings
import seaborn as sns
import os
import pandas as pd
import warnings
import sys
import numpy as np
from pathlib import Path

class Product():
    #newprod = Product(r["ProductID"],r["Name"],r["ProductNumber"],r["StockLevel"])
    def __init__(self,myid,myname,mypn,mystklvl):
        self.ID = myid
        self.Name = myname
        self.PN = mypn
        self.StockLevel= mystklvl
        self.Successor = None
        self.Operations = []
        self.Predecessors = []
        self.MPredecessors = dict()
        self.stockunit = "Pcs" # change to "mm" if in the data file so
        self.stockbatch = 1 # in case stock unit is piece, otherwise the length of bar. 
        # PlANNING
        self.StockLevels = dict() #key: date, val: stocklevel value on the date / for raw materials
        self.TargetLevels = dict() #key: date, val: required stock value on the date /for products
        self.ReservedStockLevels = dict() #key: date, val: required stock value on the date /for products
        self.PurchaseLevels = dict() #key: first day of week, val: purchase amount / for raw materials
        self.Batchsize = None #This will be the prescribed batchsize or the order size if no Batch is available.
        self.DemandingOrders = dict() #key: order,  #val: quantity
        

    def getStockUnit(self):
        return self.stockunit
    
    def setStockUnit(self,myit):
        self.stockunit = myit
        return

    def getStockBatch(self):
        return self.stockbatch
    
    def setStockBatch(self,myit):
        self.stockbatch = myit
        return
        
    def getDemandingOrders(self):
        return self.DemandingOrders

    def getTargetLevels(self):
        return self.TargetLevels

    def getReservedStockLevels(self):
        return self.ReservedStockLevels
        
    def getID(self):
        return self.ID
    def getName(self):
        return self.Name
    def getPN(self):
        return self.PN
    def getStockLevel(self):
        return self.StockLevel
    def setStockLevel(self,lvl):
        self.StockLevel = lvl
        return 
    def getPredecessors(self):
        return self.Predecessors
    def getMPredecessors(self):
        return self.MPredecessors
    def getOperations(self):
        return self.Operations
    def setSuccessor(self,succ):
        self.Successor = succ
        return
    def getSuccessor(self):
        return self.Successor
    def getBatchsize(self):
        return self.Batchsize
    def setBatchsize(self,size):
        self.Batchsize = size
        return


class MachineGroup():
    def __init__(self):
        self.Machines = []  
        self.OperatingTeam = None
        

    def getMachines(self):
        return self.Machines
        
    def getOperatingTeam(self):
        return self.OperatingTeam 
    def setOperatingTeam(self,opt):
        self.OperatingTeam = opt
        return 

class OperatingTeam():
    
    def __init__(self):
        self.Operators = []
        self.MachineGroup = None
        self.CapacityUse = dict() #key: Shift, val: fte use. 
        


    def getCapacityUse(self):
        return self.CapacityUse 
    def getOperators(self):
        return self.Operators 
        
    def getMachineGroup(self):
        return self.MachineGroup
    def setMachineGroup(self,mg):
        self.MachineGroup = mg
        return

    

class Resource():
    # Resource(r["ResourceID"],r["ResourceType"],r["Name"],r["DailyCapacity"])
    def __init__(self,myid,mytype,myname,mydaycp):
        self.ID = myid
        self.Name = myname
        self.Type = mytype
        self.DayCapacity= int(mydaycp%8>0)+mydaycp//8
        self.Operations = []
        self.Outsource = False
        self.Automated = False  #Boolean Yes or No if Type is Machine, None if Type is Manual
        self.FTERequirement = 0.0 # per unit operating time. Mostly applied to machines. 
        # PlANNING
        self.CapacityLevels = dict() # key: date, val: cumulative capacity level on the date 
        self.CapacityUsePlan = dict() # #key: date, val: planned cumulative capacity use
        self.CapacityReserved = dict()
        self.OperatingTeam = None
        self.MachineGroup = None
       
   
        # PlANNING

        # SCHEDULING 
        
        self.batchsize = 12 # to be changed..
        self.Jobs = dict() # key: product, #val: list of job objects
        self.Schedule = dict()  #key: shift, val: []
        self.CurrentSchedule = dict()  #key: shift, val: []
        self.ShiftOperatingModes = dict() #key: shift val: one of "Operated", "Self". Self mode only can continue the started job, cannot start a job. 

        self.OperatingEffort = 0
        self.AvailableShift = None; #This is 1 or 2 for operator and All for Machines
        self.EmptySlots = [] # list of tuples ((starttime,length),startshift)
        self.ShiftAvailability = dict() #key: shift, val: boolena available/unavailable.  

        # SCHEDULING

    def getShiftOperatingModes(self):
        return self.ShiftOperatingModes
    

    def getMachineGroup(self):
        return self.MachineGroup
    
    def setMachineGroup(self,mg):
        self.MachineGroup = mg
        return
        
        
    def getOperatingTeam(self):
        return self.OperatingTeam
    def setOperatingTeam(self,tm):
        self.OperatingTeam = tm
        return
        
    def getEmptySlots(self):
        return self.EmptySlots

    def getShiftAvailability(self):
        return self.ShiftAvailability


    def setFTERequirement(self):
        self.FTERequirement = True
        return
    def getFTERequirement(self):
        return self.FTERequirement
    

    def setOutsource(self):
        self.Outsource = True
        return
    def IsOutsource(self):
        return self.Outsource

    def setName(self,name):
        self.Name = name
        return

    

    def GetTotalDemand(self):

        demand = 0
        for cust_ordr,usedict in self.getCapacityUsePlan().items():
            demand+=sum([useval for useval in usedict.values()])
        
        return demand
        
    def getBatchSize(self):
        return self.batchsize 
    def getCapacityLevels(self):
        return self.CapacityLevels
    def getCapacityReserved(self):
        return self.CapacityReserved

    def getSchedule(self):
        return self.Schedule

    def getCurrentSchedule(self):
        return self.CurrentSchedule


    def getCapacityUsePlan(self):
        return self.CapacityUsePlan

    def getID(self):
        return self.ID
    def getName(self):
        return self.Name

    
    def getType(self):
        return self.Type
    def getDailyCapacity(self):
        return self.DayCapacity
    def getOperations(self):
        return self.Operations
    def IsAutomated(self):
        return self.Automated
    def getOperatingEffort(self):
        return self.OperatingEffort
    def getAvailableShift(self):
        return self.AvailableShift
    def getJobs(self):
        return self.Jobs

    def setAutomated(self):
        self.Automated = True
        return 
    def setOperatingEffort(self,opef):
        self.OperatingEffort = opef
        return 
    def setAvailableShift(self,shift):
        self.AvailableShift = shift
        return 

    def InitializeEmptySlot(self):
        firstshift = None

        availablehours = 0

        
        
        for shift,jobs in self.getCurrentSchedule().items():
            availablehours+=(shift.getEndTime()-shift.getStartTime()+1)      

            
            anyprevinschedule = False
            curr_shift = shift.getPrevious() 
            while curr_shift != None:
                if curr_shift in self.getCurrentSchedule():
                    anyprevinschedule = True
                curr_shift = curr_shift.getPrevious()
                
            if not anyprevinschedule:                
                firstshift = shift
                 
                
        self.getEmptySlots().append(((firstshift.getStartTime(),availablehours),firstshift))
        
        return 
          

    

class Operation():
    # Operation(r["OperationID"],r["Name"],r["ProcessTime"])
    def __init__(self,myid,myname,myproctime):
        self.ID = myid
        self.Name = myname
        self.ProcessTime = myproctime
        self.RequiredResources = [] # Attention: How to handle alternative resources in this structure!!
        self.Jobs = []
        self.batchsize = 12 # to be changed..
        self.Predecessor = dict()
        self.Product = None

    def getProduct(self):
        return self.Product 

    def setProduct(self,prd):
        self.Product = prd
        return 
    
    def getID(self):
        return self.ID
    def getBatchSize(self):
        return self.batchsize
    def getJobs(self):
        return self.Jobs
        
    def getName(self):
        return self.Name
    def setName(self,myint):
        self.Name = myint
        return
    def getProcessTime(self):
        return self.ProcessTime
    def getRequiredResources(self):
        return self.RequiredResources

    def getPredecessor(self):
        return self.Predecessor
    def setPredecessor(self, pred):
        self.Predecessor = pred
        return

    
   
    


class SchJob():
    # CustomerOrder(r["OrderID"],self.Products[r["ProductName"]],r["Name"],r["Quantity"],r["Deadline"])
    def __init__(self,myJob):

        self.job = myJob
        self.StartTime = None
        self.CompletionTime = None
        self.StartShift = None
        self.StartDay = None
        self.ScheduledDay=None
        self.ScheduledShift=None
        self.Scheduled = False
        self.ScheduledTime =None
        self.ScheduledResource = None
        self.ScheduledCompShift = None
    


        

    def getJob(self):
        return self.job
        
    def getStartTime(self):
        return self.StartTime

    def setStartTime(self,myst):
        self.StartTime = myst
        return

    def getCompletionTime(self):
        return self.CompletionTime

    def setCompletionTime(self,myst):
        
        self.CompletionTime = myst

        for job in self.getJob().getOrderJobs():
            maxcomp = 0
            allscheduled = True
            for bjob in self.getJob().getBatchJobs():
                if bjob.getSchJob().IsScheduled():
                    maxcomp = max(maxcomp,bjob.getSchJob().getCompletionTime())
                else: 
                    allscheduled = False

            if allscheduled and len(self.getJob().getBatchJobs()) > 0:
                job.getSchJob().setCompletionTime(myst)
       
        return

    def getStartShift(self):
        return self.StartShift

    def setStartShift(self,shift):
        self.StartShift = shift
        return

    def getStartDay(self):
        return self.StartDay

    def setStartDay(self,day):
        self.StartDay = day
        return

    def getScheduledDay(self):
        return self.ScheduledDay

    def setScheduledDay(self,day):
        self.ScheduledDay = day
        return

    def getScheduledShift(self):
        return self.ScheduledShift

    def setScheduledShift(self,shift):
        self.ScheduledShift = shift
        return


    def IsScheduled(self):
        return self.Scheduled
        
    def SetScheduled(self):
        if len(self.getJob().getOrderJobs()) > 0:
            self.Scheduled = True
        else: 
            if self.getJob().IsBatched():
                bscheduled = True
                for bjob in self.getJob().getBatchJobs():
                    bscheduled = bscheduled and bjob.getSchJob().IsScheduled()
                self.Scheduled = bscheduled
   
            else: 
                self.Scheduled = True
            
        return 

    def getScheduledTime(self):
        return self.ScheduledTime

    def setScheduledTime(self,myst):
        self.ScheduledTime = myst
        return

    def getScheduledResource(self):
        return self.ScheduledResource

    def setScheduledResource(self,myst):
        self.ScheduledResource = myst
        return

   

    def getScheduledCompShift(self):
        return self.ScheduledCompShift

    def setScheduledCompShift(self,myst):
        self.ScheduledCompShift = myst
        return

    def IsSchedulable(self):
        
        for pred in self.getJob().getPredecessors():
            if pred.IsBatched():
                continue

              
            if not pred.getSchJob().IsScheduled():
                return False
        return True

    def getLatestPredecessorCompletion(self):

        maxcomptime = 0

        for pred in self.getJob().getPredecessors():
            
            if pred.IsBatched():
                continue

            if not pred.getSchJob().IsScheduled():
                return -1 # not applicable to start
            else: 
                maxcomptime = max(maxcomptime,pred.getSchJob().getCompletionTime())

        return maxcomptime




class Job():
    # CustomerOrder(r["OrderID"],self.Products[r["ProductName"]],r["Name"],r["Quantity"],r["Deadline"])
    def __init__(self,myid,myname,myprod,myopr,myqnty,myddline):
        self.ID = myid
        self.Name = myname
        self.Operation = myopr
        self.Product = myprod
        self.Quantity = myqnty
        # PLANNING
        self.DeadLine = myddline
        self.Predecessors = []
        self.Successors = []
        self.LatestStart=  None
        self.CustomerOrder = None
        self.OrderJobs = dict() #key: customer order, val: [(job,Q)] of that order. 
        self.batched = False
        self.BatchJobs = []
       
        self.ActualStart = None
        self.ActualCompletion = None
        self.SchJob = None
        self.MySch = None


    # SCHEDULING

        
        self.OrderReserves = dict() # key: Order, val: quantity reserved for the order.

    
    def getMySch(self):
        return self.MySch

   
    def initializeMySch(self):
        self.MySch = SchJob(self)
        return

    def initializeSchJob(self):
        self.SchJob = SchJob(self)
        return

    def getSchJob(self):
        return self.SchJob

    
    def setBatched(self):
        self.batched = True
        return
    def IsBatched(self):
        return self.batched

    def getBatchJobs(self):
        return self.BatchJobs


    def getOrderJobs(self):
        return self.OrderJobs
 
    


    def setActualStart(self,co):
        self.ActualStart = co
        return

    
    def getActualStart(self):
        return self.ActualStart


    def setActualCompletion(self,co):
        self.ActualCompletion = co
        return

    
    def getActualCompletion(self):
        return self.ActualCompletion
    

    def setCustomerOrder(self,co):
        self.CustomerOrder = co
        return
    def getCustomerOrder(self):
        return self.CustomerOrder
        
        
    def getLatestStart(self):
        return self.LatestStart

    def setLatestStart(self,myst):
        self.LatestStart = myst
        return

    def setDeadLine(self,myst):
        self.DeadLine = myst
        return

    def IsBatchJob(self):
        return (len(self.getOrderJobs())>0)
   

    def getID(self):
        return self.ID
    def getName(self):
        return self.Name
    def getResource(self):
        return self.Resource
    def getProduct(self):
        return self.Product
    def getOperation(self):
        return self.Operation
    def getQuantity(self):
        if len(self.getOrderJobs()) == 0:
            return self.Quantity
        else:
            q = 0
            for order,joblist in self.getOrderJobs().items():
                for jobinfo in joblist:
                    q+=jobinfo[1]
            return q
    def getDeadLine(self):
        return self.DeadLine
    def getPredecessors(self):
        return self.Predecessors
    def getSuccessors(self):
        return self.Successors 
    def getOrderReserves(self):
        return self.OrderReserves
    
    
class CustomerOrder():
    # CustomerOrder(r["OrderID"],self.Products[r["ProductName"]],r["Name"],r["Quantity"],r["Deadline"])
    def __init__(self,myid,myname,myprodid,myprodname,myqnty,myddline):
        self.ID = myid
        self.Name = myname
        self.Product = None
        self.ProductID = myprodid
        self.ProductName = myprodname
        self.Quantity = myqnty
        self.DeadLine = datetime.strptime(myddline,"%Y-%m-%d")
        self.ReferenceNumber = 0
        self.DelayReasons = dict() # key: deldate, val: prodpn+resource cap./lead time+date
        self.OrderPlanDict = dict() # key: plan item type, value: list of tuples (item,(date,val))
     
        self.OrderPlanDict['Products'] = dict() # for target stock levels
        self.OrderPlanDict['Resources'] = dict() # for capacity levels

        # PlANNING
        self.PlannedDelivery = None
        self.LatestStart = None
        self.RequiredCapacity = dict() #key: resourceid, val: (dict: #key: date, val: used capacity) 
        self.MyJobs = [] # created during the planning, order batching convention 

    def getStatus(self):

        nojobscompleted  = 0
        
        for jb in order.getMyJobs():
            if jb.getSchJob().IsScheduled():
                nojobscompleted+=1
    
        if nojobscompleted == len(self.getMyJobs()):
            return "Scheduled"
        else:
            if nojobscompleted == 0:
                return "Unscheduled"
            else:
                return "Partly scheduled"
        
    def getMyJobs(self):
        return self.MyJobs

    def setMyJobs(self,myit):
        self.MyJobs = myit
        return 

    def getLatestStart(self):
        return self.LatestStart

    def setLatestStart(self,myit):
        self.LatestStart = myit
        return 
    
    def getDelayReasons(self):
        return self.DelayReasons

    def getOrderPlan(self):
        return self.OrderPlanDict
        
    def resetOrderPlan(self):
        for item,itemdict in self.OrderPlanDict.items():
            itemdict.clear()
        return

    def getPlannedDelivery(self):
        return self.PlannedDelivery
    def resetPlannedDelivery(self):
        self.PlannedDelivery = None
        return 
    def setPlannedDelivery(self,myval):
        self.PlannedDelivery = myval
        return 
    def getRequiredCapacity(self):
        return self.RequiredCapacity
    def getReferenceNumber(self):
        return self.ReferenceNumber 
    def setReferenceNumber(self,refno):
        self.ReferenceNumber = refno
        return 
    
        # PlANNING

    

    
    def isDelayed(self):
        return (self.DeadLine < self.PlannedDelivery)
    def getID(self):
        return self.ID
    def getName(self):
        return self.Name
    def setProduct(self,prod):
        self.Product = prod
        return
    def getQuantity(self):
        return self.Quantity
    def getProduct(self):
        return self.Product
    def getDeadLine(self):
        return self.DeadLine
    def getProductName(self):
        return self.ProductName

class Shift():
    def __init__(self,myday,number,previous):
        self.Day = myday
        self.Number = number
        self.StartTime = 0
        self.EndTime = 0
        self.StartHour = None
        self.EndHour = None
        self.next = None        
        if previous != None: 
            previous.setNext(self)
        
        self.previous = previous

    def setEndHour(self,time):
        self.EndHour = time
        return 

    def getEndHour(self):
        return self.EndHour

    def setStartHour(self,time):
        self.StartHour = time
        return 

    def getStartHour(self):
        return self.StartHour

    def setStartTime(self,time):
        self.StartTime = time
        return 

    def getStartTime(self):
        return self.StartTime

    def setNext(self,nt):
        self.next = nt
        return 

    def getNext(self):
        return self.next

    def getPrevious(self):
        return self.previous
     
    def setEndTime(self,time):
        self.EndTime= time
        return 

    def getEndTime(self):
        return self.EndTime
        

    def getDay(self):
        return self.Day

    def getNumber(self):
        return self.Number
        

class ScheduleSolution():
    def __init__(self,myname):
        self.name = myname
        self.resources_sch = dict()  #key: resname, #val: schdule: dict key: Shift, val: [(jobid,st,cp)]
        

    def getName(self):
        return self.name
    def getResourceSchedules(self):
        return self.resources_sch

    
 


