# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 11:46:59 2024

@author: mfirat
"""

##### import ipywidgets as widgets
from IPython.display import clear_output
from IPython import display
from ipywidgets import *
from ipytree import Tree, Node
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
from IPython.display import display, HTML

display(HTML("<style>.red_label { color:red }</style>"))
display(HTML("<style>.blue_label { color:blue }</style>"))


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
        self.PSTBOrdOutput = None
        self.PSTBResSchOutput = None
        self.MyOrdTree = None
        self.SchTree = None
        self.SchTreeRootNode = None
        self.OrdTreeRootNode = None
        
        return

    def setSchTreeRootNode(self,myit):
        self.SchTreeRootNode  = myit
        return
        
    def getSchTreeRootNode(self):
        return self.SchTreeRootNode
        
    
    def setOrdTreeRootNode(self,myit):
        self.OrdTreeRootNode  = myit
        return
        
    def getOrdTreeRootNode(self):
        return self.OrdTreeRootNode

    def setMyOrdTree(self,myit):
        self.MyOrdTree  = myit
        return
        
    def getMyOrdTree(self):
        return self.MyOrdTree

    def setSchTree(self,myit):
        self.SchTree  = myit
        return
        
    def getSchTree(self):
        return self.SchTree
      


    def setPSTBResSchOutput(self,myit):
        self.PSTBResSchOutput = myit
        return
        
    def getPSTBResSchOutput(self):
        return self.PSTBResSchOutput
        

    def setPSTBOrdOutput(self,myit):
        self.PSTBOrdOutput  = myit
        return
        
    def getPSTBOrdOutput(self):
        return self.PSTBOrdOutput
      

    def setPLTBPlanStart(self,myit):
        self.PLTBPlanStart  = myit
        return
        
    def getPLTBPlanStart(self):
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

       
        if selectedord == None:
            return

        if selectedord == '':
            return

        
        ordname = selectedord[:selectedord.find(":")]

      
        if ordname in self.getVisualManager().DataManager.getCustomerOrders():
            myord = self.getVisualManager().DataManager.getCustomerOrders()[ordname]

            self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="order jobs..."+str(len(myord.getMyJobs()))+"\n"
            
            ordjobtree = Tree()
         
            jobnodes = []
            for job in myord.getMyJobs():
                schstr = "Unscheduled"
                if job.IsScheduled():
                    schstr = "st: "+str(round(job.getStartTime(),2))+"-cp: "+str(round(job.getCompletionTime(),2))
                jobnode = Node(job.getName()+"> "+schstr,[], icon="cut", icon_style="success") 
                jobnodes.append(jobnode)

           
            rootnode = Node(myord.getName(),jobnodes, icon="cut", icon_style="success") 

            ordjobtree.add_node(rootnode)

            self.setMyOrdTree(ordjobtree)
            self.setOrdTreeRootNode(rootnode)
    
         
            with self.getPSTBOrdOutput():
                clear_output()
                display(self.getMyOrdTree())

       
        return
        
    
    def generatePSschTAB(self):
    

        self.setPSchScheRes(widgets.Textarea(value='', placeholder='',description='',disabled=True))
     
        self.getPSchScheRes().layout.height = '150px'
        self.getPSchScheRes().layout.width = '700px'

        self.setPSchTBmakesch_btn(widgets.Button(description="Make Schedule"))
        self.getPSchTBmakesch_btn().on_click(self.getVisualManager().getSchedulingManager().MakeSchedule)

        ordl = widgets.Label(value ='Customer Orders')
        ordl.add_class("red_label")

        reslb = widgets.Label(value ='Resources')
        reslb.add_class("red_label")

        schpr = widgets.Label(value ='Scheduling procedure progress ')
        schpr.add_class("red_label")
     
        self.setPSchOrderlist(widgets.Select(options=[],description = ''))
        self.getPSchOrderlist().layout.height = '150px'
        self.getPSchOrderlist().layout.width = '400px'
        self.getPSchOrderlist().observe(self.ShowOrderStatus)


        self.setPLTBPlanStart(widgets.DatePicker(description='Start',disabled=False))
        self.getPLTBPlanStart().observe(self.SetStart)

        
        self.setPLTBPlanEnd(widgets.DatePicker(description='End',disabled=False))
        self.getPLTBPlanEnd().observe(self.SetEnd)
     
        self.setPSchResources(widgets.Select(options=[], description=''))
        self.getPSchResources().layout.height = '150px'
        self.getPSchResources().layout.width = '400px'
        self.getPSchResources().observe(self.ShowShiftJobs)

        
        ordtr = widgets.Label(value ='Order Schedule')
        ordtr.add_class("red_label")

        restr = widgets.Label(value ='Resource Schedule')
        restr.add_class("red_label")

        OrdSchTree = Tree()
        rootnode = Node("Order Jobs",[], icon="cut", icon_style="success") 
        OrdSchTree.add_node(rootnode)
        self.setMyOrdTree(OrdSchTree)
        self.setOrdTreeRootNode(rootnode)
        self.setPSTBOrdOutput(widgets.Output())

        MySchTree = Tree()
        rootnode = Node("Resource Shifts",[], icon="cut", icon_style="success") 
        MySchTree.add_node(rootnode)
        self.setSchTree(MySchTree)
        self.setSchTreeRootNode(rootnode)
        self.setPSTBResSchOutput(widgets.Output())


      
        tab_sch = VBox(children = [
            widgets.Label(Value ='Schedule Settings '),
            HBox(children = [self.getPLTBPlanStart(),self.getPLTBPlanEnd(),self.getPSchTBmakesch_btn()]),
            HBox(children=[VBox(children = [reslb,self.getPSchResources()]),VBox(children= [restr,self.getPSTBResSchOutput()])]),
            HBox(children=[VBox(children= [ordl,self.getPSchOrderlist()]), VBox(children= [ordtr,self.getPSTBOrdOutput()])]),
            HBox(children=[VBox(children= [schpr,self.getPSchScheRes()])])])


        
         
        with self.getPSTBOrdOutput():
            clear_output()
            display(self.getMyOrdTree())
        with self.getPSTBResSchOutput():
            clear_output()
            display(self.getSchTree())



        tab_sch.layout.height = '600px'
          
        return tab_sch


   

#############################################################################################################################################  







#############################################################################################################################################   




 