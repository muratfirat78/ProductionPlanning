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
        self.PrescribedBatchsize=None #If None then it is order dependent.
        self.ChosenBatchsize=None #This will be the prescribed batchsize or the order size if no prescribedBatch is available.
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
    def getPrescribedBatchsize(self):
        return self.PrescribedBatchsize
    def setPrescribedBatchsize(self,size):
        self.PrescribedBatchsize = size
        return
    def getChosenBatchsize(self):
        return self.ChosenBatchsize
    def setChosenBatchsize(self,size):
        self.ChosenBatchsize = size
        return

class Resource():
    # Resource(r["ResourceID"],r["ResourceType"],r["Name"],r["DailyCapacity"])
    def __init__(self,myid,mytype,myname,mydaycp):
        self.ID = myid
        self.Name = myname
        self.Type = mytype
        self.DayCapacity= int(mydaycp)
        self.Operations = []
        self.Automated = None #Boolean Yes or No if Type is Machine, None if Type is Manual
        # PlANNING
        self.CapacityLevels = dict() # key: date, val: cumulative capacity level on the date 
        self.CapacityUsePlan = dict() # #key: date, val: planned cumulative capacity use
        self.CapacityReserved = dict() 
        
        # PlANNING

        # SCHEDULING 
        
        self.batchsize = 12 # to be changed..
        self.Jobs = dict() # key: product, #val: list of job objects
        self.Schedule = dict()  #key: day, val: list of (jobs, starttimes)
        self.OperatingEffort = 0
        self.AvailableShift = None; #This is 1 or 2 for operator and All for Machines

        # SCHEDULING 

    def setName(self,name):
        self.Name = name
        return
   
        
    def getBatchSize(self):
        return self.batchsize 
    def getCapacityLevels(self):
        return self.CapacityLevels
    def getCapacityReserved(self):
        return self.CapacityReserved

    def getSchedule(self):
        return self.Schedule

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
    def getAutomated(self):
        return self.Automated
    def getOperatingEffort(self):
        return self.OperatingEffort
    def getAvailableShift(self):
        return self.AvailableShift
    def getJobs(self):
        return self.Jobs

    def setAutomated(self,aut):
        self.Automated = aut
        return 
    def setOperatingEffort(self,opef):
        self.OperatingEffort = opef
        return 
    def setAvailableShift(self,shift):
        self.AvailableShift = shift
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

    
    def getID(self):
        return self.ID
    def getBatchSize(self):
        return self.batchsize
    def getJobs(self):
        return self.Jobs
        
    def getName(self):
        return self.Name
    def getProcessTime(self):
        return self.ProcessTime
    def getRequiredResources(self):
        return self.RequiredResources

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
        self.Successor = []
        self.LatestStart=  None
        


    # SCHEDULING
        self.StartTime = None
        self.ScheduledDay=None
        self.ScheduledShift=None
        
    def getLatestStart(self):
        return self.LatestStart

    def setLatestStart(self,myst):
        self.LatestStart = myst
        return

    def getStartTime(self):
        return self.StartTime

    def setStartTime(self,myst):
        self.StartTime = myst
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
        return self.Quantity
    def getDeadLine(self):
        return self.DeadLine
    def getPredecessors(self):
        return self.Predecessors
    def getSuccessor(self):
        return self.Successor 
    
    
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
        self.DelayReasons = dict() # key: prod, value: (resource/lead time,date)
        self.OrderPlanDict = dict() # key: plan item type, value: list of items
       

        self.OrderPlanDict['Products'] = []  # for target stock levels
        self.OrderPlanDict['Resources'] = [] # for capacity levels

        # PlANNING
        self.PlannedDelivery = None
        self.LatestStart = None
        self.RequiredCapacity = dict() #key: resourceid, val: (dict: #key: date, val: used capacity) 


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
        for planitem,itemlist in self.OrderPlanDict.items():

            if planitem == 'Products':
                for prod in itemlist:
                    if len(prod.getMPredecessors()) > 0: 
                        continue
                    prod.getReservedStockLevels().clear()
            
            if planitem == 'Resources':
                for res in itemlist:
                    res.getCapacityReserved().clear()
            itemlist.clear()
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
    def __init__(self,myday,number,shiftcap):
        self.Day = myday
        self.Number = number
        self.Capacity = shiftcap
        

    def getDay(self):
        return self.Day

    def getNumber(self):
        return self.Number

    def getCapacity(self):
        return self.Capacity


