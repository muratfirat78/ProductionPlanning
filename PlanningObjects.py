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
        # PlANNING
        self.StockLevels = dict() #key: date, val: stocklevel value on the date / for raw materials
        self.TargetLevels = dict() #key: date, val: required stock value on the date /for products
        self.ReservedStockLevels = dict() #key: date, val: required stock value on the date /for products
        self.PurchaseLevels = dict() #key: first day of week, val: purchase amount / for raw materials
        

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
        
        self.batchsize = 50 # to be changed..
        self.Jobs = dict() # key: product, #val: list of job objects
        self.Schedule = dict()  #key: day, val: list of jobs

        # SCHEDULING 


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

    def getJobs(self):
        return self.Jobs 
    
class Operation():
    # Operation(r["OperationID"],r["Name"],r["ProcessTime"])
    def __init__(self,myid,myname,myproctime):
        self.ID = myid
        self.Name = myname
        self.ProcessTime = myproctime
        self.RequiredResources = []
        self.Jobs = []
        self.batchsize = 50 # to be changed..

        
    
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
        self.Successor = None
        self.LatestStart=  None


    # SCHEDULING
        self.StartTime = None

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

        # PlANNING
        self.PlannedDelivery = None
        self.RequiredCapacity = dict() #key: resourceid, val: (dict: #key: date, val: used capacity) 

    

    def getPlannedDelivery(self):
        return self.PlannedDelivery
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



