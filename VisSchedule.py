# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 11:46:59 2024

@author: mfirat
"""

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
from PlanningObjects import *


class ScheduleTab():

    def __init__(self):  
        
        self.VisualManager = None
        self.PSchScheRes = None
        self.PSchTBmakesch_btn = None
        self.PSchJoblist = None
        self.PSchShiftJoblist = None
        self.PSchResources = None
        self.PLTBPlanStart  = None
        self.PLTBPlanEnd  = None
        self.PSchOrderlist = None
        self.PSchOrdProd = None
        self.PLTBPlanStartv = None
        
        return

      

    def setPLTBPlanStart(self,myit):
        self.PLTBPlanStart  = myit
        return
        
    def getPLTBPlanStart (self):
        return self.PLTBPlanStart

   
    
    def setPLTBPlanEnd(self,myit):
        self.PLTBPlanEnd  = myit
        return
        
    def getPLTBPlanEnd(self):
        return self.PLTBPlanEnd

    def setVisualManager(self,myit):
        self.VisualManager = myit
        return


    def setPSchScheRes(self,myitm):
        self.PSchScheRes = myitm
        return
        
    def getPSchScheRes(self):
        return self.PSchScheRes

    def setPSchTBmakesch_btn(self,myitm):
        self.PSchTBmakesch_btn = myitm
        return
        
    def getPSchTBmakesch_btn(self):
        return self.PSchTBmakesch_btn


    def setPSchJoblist(self,myitm):
        self.PSchJoblist = myitm
        return
        
    def getPSchJoblist(self):
        return self.PSchJoblist

    def setPSchShiftJoblist(self,myitm):
        self.PSchShiftJoblist = myitm
        return
        
    def getPSchShiftJoblist(self):
        return self.PSchShiftJoblist

    def setPSchOrderlist(self,myitm):
        self.PSchOrderlist = myitm
        return
        
    def getPSchOrdProd(self):
        return self.PSchOrdProd

    def setPSchOrdProd(self,myitm):
        self.PSchOrdProd = myitm
        return

    def getPSchResources(self):
        return self.PSchResources

    def setPSchResources(self,myitm):
        self.PSchResources = myitm
        return
        
    def getPSchOrderlist(self):
        return self.PSchOrderlist
        
    def getVisualManager(self):
        return self.VisualManager

    def setPSchOperations(self,myitm):
        self.PSchOperations = myitm
        return
        
    def getPSchOperations(self):
        return self.PSchOperations


    def SetStart(self,event):

        sel_start = self.getPLTBPlanStart().value 
        self.getVisualManager().getSchedulingManager().setSHStart(sel_start)
      
        return
        
    def SetEnd(self,event):

        sel_end = self.getPLTBPlanEnd().value
        self.getVisualManager().getSchedulingManager().setSHEnd(sel_end)
       
        return

    def ShowJobs(self,event):


        if not "new" in event:
            return
    
        if not "index" in event['new']:
            return

        selectedopr = self.getPSchOperations().options[event["new"]["index"]]
        
        if selectedopr == None:
            return

        if selectedopr == '':
            return


        
        joblist = [selectedopr]
        self.getPSchScheRes().value+=str(len(self.getVisualManager().DataManager.getProducts()))+"\n"

        if selectedopr in self.getVisualManager().DataManager.getOperations():
            selected_op = self.getVisualManager().DataManager.getOperations()[selectedopr]
            self.getPSchScheRes().value+="Jobs of the operation: "+str(len(selected_op.getJobs()))+"\n"
            for job in selected_op.getJobs():
                joblist.append(" >> "+job.getName()+", q: "+str(job.getQuantity())+", d: "+str(job.getDeadLine()))
            self.getPSchScheRes().value+=str("In the operations!!!!!!")+"\n"

            
        self.getPSchJoblist().options = [j for j in joblist]   
       
        return

    def ShowShiftJobs(self,event):


        if not "new" in event:
            return
    
        if not "index" in event['new']:
            return

        selectedopr = self.getPSchResources().options[event["new"]["index"]]
        
        if selectedopr == None:
            return

        if selectedopr == '':
            return


        
        joblist = [selectedopr]
        

        if selectedopr in self.getVisualManager().DataManager.getResources():
            selected_op = self.getVisualManager().DataManager.getResources()[selectedopr]
            
            for day, shiftjobs in selected_op.getSchedule().items():
                for shift in shiftjobs:
                    joblist.append(" >> Day: "+str(day)+" Shift "+str(shift[0].getNumber())+"\n")
                    for job in shift[1]:
                        joblist.append("   >> Job: "+str(job[0].getName())+", Processed Quantity: "+str(job[1])+" of Total Quantity: "+str(job[0].getQuantity())+"\n")
            

            
        self.getPSchShiftJoblist().options = [j for j in joblist]   
       
        return
    
    def ShowOrderStatus(self,event):

        #self.getPSchOrdProd().value = "Selected Order >>"+str(event)+"\n"

        if not "new" in event:
            return
    
        if not "index" in event['new']:
            return

        selectedord = self.getPSchOrderlist().options[event["new"]["index"]]

        self.getPSchOrdProd().value = "Selected Order >>"+str(selectedord)+"\n"
        
        if selectedord == None:
            return

        if selectedord == '':
            return

        
        ordname = selectedord[:selectedord.find(":")]

        self.getPSchOrdProd().value += str(ordname)+"\n"

        if ordname in self.getVisualManager().DataManager.getCustomerOrders():
            myord = self.getVisualManager().DataManager.getCustomerOrders()[ordname]

            if myord.getPlannedDelivery() != None:
                self.getPSchOrdProd().value = "Final Product: "+"\n"
                self.getPSchOrdProd().value += myord.getProduct().getName()+"\n"
              
                self.getPSchOrdProd().value += "Quantity: "+str(myord.getQuantity())+"\n"
                
                self.getPSchOrdProd().value += "Latest start: "+str(myord.getLatestStart())+"\n"
                
                
               
                
            else:
                self.getPSchOrdProd().value = "Not planned... "+"\n"
           
        else:
            self.getPSchOrdProd().value = "Order not found..."+"\n"
        
        

        
        return
        
    
    def generatePSschTAB(self):
    

        self.setPSchScheRes(widgets.Textarea(value='', placeholder='',description='Schedule',disabled=True))
     
        self.getPSchScheRes().layout.height = '150px'
        self.getPSchScheRes().layout.width = "90%"

        self.setPSchTBmakesch_btn(widgets.Button(description="Make Schedule"))
        self.getPSchTBmakesch_btn().on_click(self.getVisualManager().getSchedulingManager().MakeSchedule)

        self.setPSchJoblist(widgets.Select(options=[],description = 'Jobs'))
        self.getPSchJoblist().layout.height = '150px'
        self.getPSchJoblist().layout.width = '400px'

        self.setPSchOrderlist(widgets.Select(options=[],description = 'Orders'))
        self.getPSchOrderlist().layout.height = '150px'
        self.getPSchOrderlist().layout.width = '400px'
        self.getPSchOrderlist().observe(self.ShowOrderStatus)

        self.setPSchOrdProd(widgets.Textarea(options=[],description = 'Order information'))
        self.getPSchOrdProd().layout.height = '150px'
        self.getPSchOrdProd().layout.width = '400px'

        self.setPLTBPlanStart(widgets.DatePicker(description='Start',disabled=False))
        self.getPLTBPlanStart().observe(self.SetStart)

        
        self.setPLTBPlanEnd(widgets.DatePicker(description='End',disabled=False))
        self.getPLTBPlanEnd().observe(self.SetEnd)
     
        self.setPSchResources(widgets.Select(options=[], description='Resources:'))
        self.getPSchResources().layout.height = '150px'
        self.getPSchResources().layout.width = '400px'
        self.getPSchResources().observe(self.ShowShiftJobs)

        self.setPSchShiftJoblist(widgets.Select(options=[],description = 'Shift Jobs'))
        self.getPSchShiftJoblist().layout.height = '150px'
        self.getPSchShiftJoblist().layout.width = '400px'

        self.setPSchOperations(widgets.Select(options=[], description='Operations:'))
        self.getPSchOperations().layout.height = '150px'
        self.getPSchOperations().layout.width = '400px'
        self.getPSchOperations().observe(self.ShowJobs)
    
        tab_sch = VBox(children = [
            widgets.Label(Value ='Schedule Settings '),
            HBox(children = [self.getPLTBPlanStart(),self.getPLTBPlanEnd(),self.getPSchTBmakesch_btn()]),
                                   HBox(children=[self.getPSchOperations(),self.getPSchJoblist()]),HBox(children=[self.getPSchResources(),self.getPSchShiftJoblist()]),HBox(children=[self.getPSchOrderlist(), self.getPSchOrdProd()]),
            HBox(children=[self.getPSchScheRes()])])

        tab_sch.layout.height = '600px'
          
        return tab_sch


   

#############################################################################################################################################  







#############################################################################################################################################   




 