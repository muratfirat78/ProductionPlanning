# -*- coding: utf-8 -*-

##### import ipywidgets as widgets
from IPython.display import clear_output
from IPython import display
from ipywidgets import *
from datetime import timedelta,date
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
   
    def setDataManager(self,DataMgr):
        self.DataManager = DataMgr 
        return

    def getDataManager(self):
        return self.DataManager

    def setVisualManager(self,VMgr):
        self.VisualManager = VMgr 
        return

    def getVisualManager(self):
        return self.VisualManager


    def MakeDeliveryPlan(self,b):
        ''' This function construct a delivery plan for every customer orders as follows: 
            - Customer Orders have priority due to their deadlines; i.e. the customer order with soonest deadline must be planned first. 
            - The primary goal is to plan customer orders without any delay. If the delivery of a customer order should be with some delay, then it loses itspriority compared to all other cutomer orders to be planned.  
            - The combined required capacity levels of planned customer orders should respect to the capacity levels of all resources.
            - Every raw material can be purchased at most certain amount in every week. The required raw material levels of planned customer orders should be feasible by possibly purchasing additional amount of raw materials for every week.  
        '''

        # START: here is your code to make planning 



        # END: here is your code to make planning 
        self.getVisualManager().getPLTBresult2exp().value+=">Deliveries"+"\n"
        for ordname,myord in self.getDataManager().getCustomerOrders().items():
            self.getVisualManager().getPLTBresult2exp().value+="  >"+ordname+": deadline "+str(myord.getDeadLine())+", planned delivery: "+str(myord.getPlannedDelivery())+"\n"

        self.getVisualManager().getPLTBresult2exp().value+=">CapacityUsePlans"+"\n"
        for resame,myres in self.getDataManager().getResources().items():
            self.getVisualManager().getPLTBresult2exp().value+=" > "+resame+": "+str(myres.getCapacityUsePlan())+"\n"

        self.getVisualManager().getPLTBresult2exp().value+=">Required Stock levels"+"\n"
        for prodname,myprod in self.getDataManager().getProducts().items():
            if len(myprod.getPredecessors()) == 0:
                self.getVisualManager().getPLTBresult2exp().value+=" > Raw: "+prodname+", "+str(myprod.getTargetLevels())+"\n"

        return 

        

