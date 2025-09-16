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
import time
import numpy as np
from pathlib import Path
from PlanningObjects import *
from IPython.display import display, HTML
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.collections import PolyCollection
import altair as alt

display(HTML("<style>.red_label { color:red }</style>"))
display(HTML("<style>.blue_label { color:blue }</style>"))


class SimulationTab():

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
        self.PSTBGanttOutput = None
        self.ScheduleVisual = None
        self.PSchSolProps = None
        self.ScheduleAlgs = None
        self.BatchingAlgs = None
        self.PSchTBsavesch_btn = None
        self.PSchTBschFileName = None
        self.PSchTBaccsch_btn = None
        
        return


    def setPSchTBaccsch_btn(self,myit):
        self.PSchTBaccsch_btn  = myit
        return
        
    def getPSchTBaccsch_btn(self):
        return self.PSchTBaccsch_btn

    def setBatchingAlgs(self,myit):
        self.BatchingAlgs  = myit
        return
        
    def getBatchingAlgs(self):
        return self.BatchingAlgs

    def setScheduleAlgs(self,myit):
        self.ScheduleAlgs  = myit
        return
        
    def getScheduleAlgs(self):
        return self.ScheduleAlgs


    def setPSchSolProps(self,myit):
        self.PSchSolProps  = myit
        return
        
    def getPSchSolProps(self):
        return self.PSchSolProps


    def setScheduleVisual(self,myit):
        self.ScheduleVisual  = myit
        return
        
    def getScheduleVisual(self):
        return self.ScheduleVisual 
        

    def setPSTBGanttOutput(self,myit):
        self.PSTBGanttOutput  = myit
        return
        
    def getPSTBGanttOutput(self):
        return self.PSTBGanttOutput
        

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

    def setPSchTBsavesch_btn(self,myitm):
        self.PSchTBsavesch_btn = myitm
        return
        
    def getPSchTBsavesch_btn(self):
        return self.PSchTBsavesch_btn

    def setPSchTBschFileName(self,myint):
        self.PSchTBschFileName = myint
        return

    def getPSchTBschFileName(self):
        return self.PSchTBschFileName


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
    def RecFindSelected(self,node,parent):
        
        selected = None 
        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="in recfindnode..."+node.name+"\n"
        if node.selected:
            selected = node  
        else: 
            for subnode in node.nodes: 
                selected = self.RecFindSelected(subnode) 
                if selected != None:
                    break       
        return selected


  
    

   
    
   
   
      
    def StartSimulation(self,b):

        infotxt = self.getVisualManager().getSimulationManager().RunSimulation()
        

        self.getPSchScheRes().value+=infotxt+"\n"
        
        return

   
        
        
    
    def generateSimTAB(self):
    

        self.setPSchScheRes(widgets.Textarea(value='', placeholder='',description='',disabled=True))
     
        self.getPSchScheRes().layout.height = '150px'
        self.getPSchScheRes().layout.width = '700px'

        self.setPSchTBmakesch_btn(widgets.Button(description="Run Simulation", icon = 'fa-gear'))
        self.getPSchTBmakesch_btn().on_click(self.StartSimulation)

      


        schpr = widgets.Label(value ='Simulation progress ')
        schpr.add_class("red_label")
     
       


        self.setPLTBPlanStart(widgets.DatePicker(description='Start',disabled=False))
        self.getPLTBPlanStart().observe(self.SetStart)

        
        self.setPLTBPlanEnd(widgets.DatePicker(description='End',disabled=False))
        self.getPLTBPlanEnd().observe(self.SetEnd)
     
      
   
        
        tab_sch = HBox(children = [ VBox(children = [
           
            HBox(children = [self.getPLTBPlanStart(),self.getPLTBPlanEnd(),self.getPSchTBmakesch_btn()]),
            HBox(children=[VBox(children= [schpr,self.getPSchScheRes()])])])])


       
        

        tab_sch.layout.height = '600px'
          
        return tab_sch


   

#############################################################################################################################################  







#############################################################################################################################################   




 