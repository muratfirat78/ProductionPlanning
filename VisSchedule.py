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


  
    

    def ShowShiftJobs(self,event):


        if not "new" in event:
            return
    
        if not "index" in event['new']:
            return

        selectedres = self.getPSchResources().options[event["new"]["index"]]
        
        if selectedres == None:
            return

        if selectedres == '':
            return


        if selectedres in self.getVisualManager().DataManager.getResources():
            selected_res = self.getVisualManager().DataManager.getResources()[selectedres]

            source = pd.DataFrame(columns=["Shift","Job","Start","End"])

            for shift,jobs in selected_res.getSchedule().items():
                
                row = pd.DataFrame([{"Shift": str(shift.getDay().date())+" | "+str(shift.getNumber()), "Job":".", "Start":1,"End":1.005}])
                source = pd.concat([source, row], axis=0, ignore_index=True)
                row = pd.DataFrame([{"Shift": str(shift.getDay().date())+" | "+str(shift.getNumber()), "Job":".", "Start":8.995,"End":9}])
                source = pd.concat([source, row], axis=0, ignore_index=True)
                for job in jobs:

                    starttime = max(job.getStartTime(),shift.getStartTime())-shift.getStartTime()+1+0.01
                    endtime =  min(job.getCompletionTime(),shift.getEndTime()+1)-shift.getStartTime()+1-0.01
                    row = pd.DataFrame([{"Shift": str(shift.getDay().date())+" | "+str(shift.getNumber()), "Job":job.getName(), "Start":starttime,"End":endtime}])
                    source = pd.concat([source, row], axis=0, ignore_index=True)
               
            with self.getPSTBGanttOutput():
                
                clear_output() 
                display(selected_res.getName())
      
                for shift in source["Shift"].unique():
                    shift_df = source[source["Shift"] == shift]
                    
                    bars = alt.Chart(shift_df).mark_bar(color='tan').encode(x='Start',x2='End',y=alt.Y('Shift', sort='-x'))
                    text = bars.mark_text(align='left',baseline='middle', dx=3).encode( text='Job')

                    display((bars + text).properties(height=100, width=200))

            restree = Tree()
         
            shiftnodes = []

            for shift,jobs in selected_res.getSchedule().items():
                jobnodes = []
               
                for job in jobs:
                    schstr = "st: "+str(round(job.getStartTime(),2))+"-cp: "+str(round(job.getCompletionTime(),2))
                    jobnode = Node(job.getName()+" > "+schstr,[], icon="cut", icon_style="success") 
                    jobnode.opened = False
                    jobnodes.append(jobnode)
                shiftnode = Node("Shift: "+str(shift.getDay().date())+" | "+str(shift.getNumber())+": "+str(shift.getStartTime())+"-"+str(shift.getEndTime()),jobnodes, icon="cut", icon_style="success")   
                shiftnode.opened = False
                shiftnodes.append(shiftnode)
        
            rootnode = Node(selected_res.getName(),shiftnodes, icon="cut", icon_style="success") 

            rootnode.opened = False
            restree.add_node(rootnode)

            self.setSchTree(restree)
            self.setSchTreeRootNode(restree)

            
         
            with self.getPSTBResSchOutput():
                clear_output()
                display(self.getSchTree())


       
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

            source = pd.DataFrame(columns=["Job","Start","End"])

            self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="order jobs..."+str(len(myord.getMyJobs()))+"\n"
            
            ordjobtree = Tree()
         
            jobnodes = []
            for job in myord.getMyJobs():
                schstr = "Unscheduled"
                if job.IsScheduled():
                    
                    row = pd.DataFrame([{"Job":job.getName(), "Start":job.getStartTime(),"End":job.getCompletionTime()}])
                    source = pd.concat([source, row], axis=0, ignore_index=True)
                    schstr = "st: "+str(round(job.getStartTime(),2))+"-cp: "+str(round(job.getCompletionTime(),2))
                    
                jobnode = Node(job.getName()+"> "+schstr,[], icon="cut", icon_style="success") 
                jobnodes.append(jobnode)

            with self.getPSTBGanttOutput():
                clear_output() 
                display(ordname)
                bars = alt.Chart(source).mark_bar(color='tan').encode(x='Start',x2='End',y=alt.Y('Job', sort='-x'))
                text = bars.mark_text(align='left',baseline='middle', dx=3).encode( text='Job')
                     
                display((bars + text).properties(height=100, width=200))
                
      

           
            rootnode = Node(myord.getName(),jobnodes, icon="cut", icon_style="success") 

            ordjobtree.add_node(rootnode)

            self.setMyOrdTree(ordjobtree)
            self.setOrdTreeRootNode(rootnode)
    
         
            with self.getPSTBOrdOutput():
                clear_output()
                display(self.getMyOrdTree())

       
        return

    def ShowDescriptives(self,event):

        if not 'index' in event['new']:
            return
            
        if event['new']['index'] < 0:
            return
    
        selected = self.getScheduleVisual().options[event['new']['index']]

        if selected == None:
            return

        if selected == '':
            return

        if selected == 'Solution Properties':

            self.getPSchSolProps().layout.display = 'block'
            self.getPSchSolProps().layout.visibility  = 'visible'
            
            
            self.getPSchResources().layout.visibility  = 'hidden'
            self.getPSchResources().layout.display = 'none'

            self.getPSTBResSchOutput().layout.visibility  = 'hidden'
            self.getPSTBResSchOutput().layout.display = 'none'
            
            self.getPSchOrderlist().layout.visibility  = 'hidden'
            self.getPSchOrderlist().layout.display = 'none'
            
            self.getPSTBOrdOutput().layout.visibility  = 'hidden'
            self.getPSTBOrdOutput().layout.display = 'none'

         

      
        if selected == 'Resources':
            
            self.getPSchResources().layout.display = 'block'
            self.getPSchResources().layout.visibility  = 'visible'
            
            self.getPSTBResSchOutput().layout.display = 'block'
            self.getPSTBResSchOutput().layout.visibility  = 'visible'
            
            self.getPSchOrderlist().layout.visibility  = 'hidden'
            self.getPSchOrderlist().layout.display = 'none'
            
            self.getPSTBOrdOutput().layout.visibility  = 'hidden'
            self.getPSTBOrdOutput().layout.display = 'none'

            self.getPSchSolProps().layout.visibility  = 'hidden'
            self.getPSchSolProps().layout.display = 'none'

        
        if selected == 'Customer Orders':

            self.getPSchOrderlist().layout.display = 'block'
            self.getPSchOrderlist().layout.visibility  = 'visible'

            self.getPSTBOrdOutput().layout.display = 'block'
            self.getPSTBOrdOutput().layout.visibility  = 'visible'
            
            self.getPSchResources().layout.visibility  = 'hidden'
            self.getPSchResources().layout.display = 'none'

            self.getPSTBResSchOutput().layout.visibility  = 'hidden'
            self.getPSTBResSchOutput().layout.display = 'none'

            self.getPSchSolProps().layout.visibility  = 'hidden'
            self.getPSchSolProps().layout.display = 'none'

        with self.getPSTBGanttOutput():
            clear_output()
       
        with self.getPSTBOrdOutput():
            clear_output()
          
        with self.getPSTBResSchOutput():
            clear_output()
          
    
        
        return
        
    def MakeSchedule(self,b):

        self.getVisualManager().getSchedulingManager().MakeSchedule(self.getScheduleAlgs().value,self.getBatchingAlgs().value)

        return

    def SaveSchedule(self,b):

        Schedule_df = pd.DataFrame(columns = ["Resource Name","Day","Shift","Job","OperationName","Start in Shift","Completion in Shift"])
        folder = 'UseCases'; casename = "TBRM_Volledige_Instantie"
        path = folder+"\\"+casename
        isExist = os.path.exists(path)
        
        if not isExist:
            os.makedirs(path)
        
        for name,myres in self.getVisualManager().DataManager.getResources().items():
            if name != 'Operator 1' and name != 'Operator 2' and name != 'Operator 3' and name != 'Manual workers':
                for shift, jobs in myres.getSchedule().items():
                    if jobs == []:
                        continue
                    else: 
                        jobs.sort(key=lambda x: x.getStartTime())
                        for job in jobs:
                            if job.getStartTime() >= shift.getStartTime() and job.getCompletionTime() <= shift.getEndTime():
                                Schedule_df.loc[len(Schedule_df)] = {"Resource Name":myres.getName(),"Day":shift.getDay(), "Shift":shift.getNumber(),"JobID":job.getID(),"OperationName":job.getOperation().getName(),"Start in Shift":job.getStartTime(),"Completion in Shift":job.getCompletionTime()}
                            if job.getStartTime() < shift.getStartTime() and job.getCompletionTime() <= shift.getEndTime():
                                Schedule_df.loc[len(Schedule_df)] = {"Resource Name":myres.getName(),"Day":shift.getDay(), "Shift":shift.getNumber(),"JobID":job.getID(),"OperationName":job.getOperation().getName(),"Start in Shift":shift.getStartTime(),"Completion in Shift":job.getCompletionTime()}
                            if job.getStartTime() < shift.getStartTime() and job.getCompletionTime() > shift.getEndTime():
                                Schedule_df.loc[len(Schedule_df)] = {"Resource Name":myres.getName(),"Day":shift.getDay(), "Shift":shift.getNumber(),"JobID":job.getID(),"OperationName":job.getOperation().getName(),"Start in Shift":shift.getStartTime(),"Completion in Shift":shift.getEndTime()}
                            if job.getStartTime() >= shift.getStartTime() and job.getCompletionTime() > shift.getEndTime():
                                Schedule_df.loc[len(Schedule_df)] = {"Resource Name":myres.getName(),"Day":shift.getDay(), "Shift":shift.getNumber(),"JobID":job.getID(),"OperationName":job.getOperation().getName(),"Start in Shift":job.getStartTime(),"Completion in Shift":shift.getEndTime()}
                                
                    
        filename = self.getPSchTBschFileName().value+".csv"; path = folder+"\\"+casename+"\\"+filename;fullpath = os.path.join(Path.cwd(), path)
        Schedule_df.to_csv(fullpath, index=False)  

        self.getVisualManager().getSchedulingTab().getPSchScheRes().value += "Schedule was saved in the file "+str(self.getPSchTBschFileName().value)+".csv. "+"\n"
                                                                                     
        return 


    def SaveTheSchedule(self,event):

        self.getVisualManager().getCaseInfo().value += ">>>  saving schedule....."+"\n" 
        schedule_df = pd.DataFrame(columns= ["JobID","Quantity","Deadline","OrderID","ProductID", "OperationID","ResourceID","SchDaySt","SchShiftSt","SchTimeSt","SchDayCp","SchShiftCp","SchTimeCp","ActDaySt","ActShiftSt","ActTimeSt","ActDayCp","ActShiftCp","ActTimeCp"])

        
        for name,order in self.getVisualManager().DataManager.getCustomerOrders().items():
            self.getVisualManager().getCaseInfo().value += ">>>  jobbb....."+"\n" 
            for job in order.getMyJobs(): 

                if job.IsScheduled(): 
                    starttime = job.getScheduledShift().getStartHour()+timedelta(hours = max(job.getStartTime(),job.getScheduledShift().getStartTime())-job.getScheduledShift().getStartTime())
                                                                             
                    #self.getVisualManager().getCaseInfo().value += ">>>  jobbb....."+str(job.getID())+"\n"  
                    
                    #self.getVisualManager().getCaseInfo().value += ">>>  deadline....."+str(job.getDeadLine())+"\n"  
                    
                   
                    endtime =  job.getScheduledCompShift().getStartHour()+timedelta(hours = min(job.getCompletionTime(),job.getScheduledCompShift().getEndTime()+1)-job.getScheduledCompShift().getStartTime())
                 
                    schres = job.getScheduledResource().getID()
                    sdayst = str(job.getScheduledShift().getDay().date())
                    sshftst = job.getScheduledShift().getNumber()
                    stst = str(starttime.strftime('%H:%M'))
                    sdaycp = str(job.getScheduledCompShift().getDay().date())
                    sshftcp = job.getScheduledCompShift().getNumber()
                    stcp = str(endtime.strftime('%H:%M'))
                else:
                    starttime = "NULL"
                    endtime ="NULL"
                    schres = "NULL"
                    sdayst = "NULL"
                    sshftst = "NULL"
                    stst = "NULL"
                    sdaycp = "NULL"
                    sshftcp = "NULL"
                    stcp = "NULL"
                    
                    
                schedule_df.loc[len(schedule_df)] = {"JobID":job.getID(),"Quantity":job.getQuantity(),
                                                         "Deadline":job.getDeadLine(),
                                                       "OrderID":job.getCustomerOrder().getID(),
                                                     "ProductID":job.getProduct().getID(),
                                                     "OperationID":job.getOperation().getID(),
                                                     "ResourceID":schres,
                                                     "SchDaySt":sdayst,
                                                     "SchShiftSt": sshftst,
                                                     "SchTimeSt":stst,
                                                     "SchDayCp":sdaycp,
                                                     "SchShiftCp":sshftcp,
                                                     "SchTimeCp":stcp,
                                                     "ActDaySt":"",
                                                     "ActShiftSt":"NULL","ActTimeSt":"NULL","ActDayCp":"NULL","ActShiftCp":"NULL","ActTimeCp":"NULL"
                                                     }

        
        folder = 'UseCases'; casename = "TBRM_Volledige_Instantie"
        path = folder+"\\"+casename
        isExist = os.path.exists(path)
        if not isExist:
            os.makedirs(path)

        self.getVisualManager().getCaseInfo().value += ">>>..... saving schedule 22...."+"\n"
        timestr = time.strftime("%Y%m%d-%H%M%S")
        filename = "ScheduleJobs_"+timestr+".csv"; 
        path = folder+"\\"+casename+"\\"+filename
        fullpath = os.path.join(Path.cwd(), path)
        schedule_df.to_csv(fullpath, index=False)
        self.getVisualManager().getCaseInfo().value += ">>>.... DONE....."+"\n"
         
     
        return
        
        
        
    
    def generatePSschTAB(self):
    

        self.setPSchScheRes(widgets.Textarea(value='', placeholder='',description='',disabled=True))
     
        self.getPSchScheRes().layout.height = '150px'
        self.getPSchScheRes().layout.width = '700px'

        self.setPSchTBmakesch_btn(widgets.Button(description="Make Schedule", icon = 'fa-gear'))
        self.getPSchTBmakesch_btn().on_click(self.MakeSchedule)

        self.setPSchTBsavesch_btn(widgets.Button(description="Export Schedule",icon = 'fa-file-excel-o'))
        self.getPSchTBsavesch_btn().on_click(self.SaveSchedule)

        self.setPSchTBaccsch_btn(widgets.Button(description="Accept Schedule",icon = 'fa-check-square'))
        self.getPSchTBaccsch_btn().on_click(self.SaveTheSchedule)
       

        self.setPSchTBschFileName(widgets.Text(description ='',value='filename..'))
        self.getPSchTBschFileName().layout.width = '150px'
 
        # schfile = widgets.Label(value ='Filename: ')
        # schfile.add_class("red_label")


        schpr = widgets.Label(value ='Scheduling procedure progress ')
        schpr.add_class("red_label")
     
        self.setPSchOrderlist(widgets.Select(options=[],description = ''))
        self.getPSchOrderlist().layout.height = '145px'
        self.getPSchOrderlist().layout.width = '400px'
        self.getPSchOrderlist().observe(self.ShowOrderStatus)


        self.setPLTBPlanStart(widgets.DatePicker(description='Start',disabled=False))
        self.getPLTBPlanStart().observe(self.SetStart)

        
        self.setPLTBPlanEnd(widgets.DatePicker(description='End',disabled=False))
        self.getPLTBPlanEnd().observe(self.SetEnd)
     
        self.setPSchResources(widgets.Select(options=[], description=''))
        self.getPSchResources().layout.height = '145px'
        self.getPSchResources().layout.width = '400px'
        self.getPSchResources().observe(self.ShowShiftJobs)

        self.setPSchSolProps(widgets.Textarea(value='', placeholder='',description='',disabled=True))
     
        self.getPSchSolProps().layout.height = '150px'
        self.getPSchSolProps().layout.width = '500px'

        
        OrdSchTree = Tree()
        rootnode = Node("Order Jobs",[], icon="cut", icon_style="success") 
        OrdSchTree.add_node(rootnode)
        self.setMyOrdTree(OrdSchTree)
        self.setOrdTreeRootNode(rootnode)
        self.setPSTBOrdOutput(widgets.Output())

        self.setPSTBOrdOutput(widgets.Output())

        MySchTree = Tree()
        rootnode = Node("Resource Shifts",[], icon="cut", icon_style="success") 
        MySchTree.add_node(rootnode)
        self.setSchTree(MySchTree)
        self.setSchTreeRootNode(rootnode)
        self.setPSTBResSchOutput(widgets.Output())

        self.setPSTBGanttOutput(widgets.Output())

        schdes = widgets.Label(value ='Schedule Information')
        schdes.add_class("red_label")

         

        schalg = widgets.Label(value ='Scheduling Algorithm')
        schalg.add_class("blue_label")

        
        bchalg = widgets.Label(value ='Batching Method')
        bchalg.add_class("blue_label")
        self.setScheduleAlgs(widgets.Dropdown(options=["Simple Greedy Insertion","Advanced Greedy Insertion"], description=''))
        self.getScheduleAlgs().layout.width = '185px'
        self.setBatchingAlgs(widgets.Dropdown(options=["Order size based","Simple Merge"], description=''))
        self.getBatchingAlgs().layout.width = '150px'


        self.setScheduleVisual(widgets.Dropdown(options=["Solution Properties","Resources", "Customer Orders"], description=''))
        self.getScheduleVisual().layout.width = '150px'
        self.getScheduleVisual().observe(self.ShowDescriptives)

        
        
        tab_sch = HBox(children = [ VBox(children = [
           
            HBox(children = [self.getPLTBPlanStart(),self.getPLTBPlanEnd(),self.getPSchTBmakesch_btn()]),
            HBox(children = [schalg,self.getScheduleAlgs(),bchalg,self.getBatchingAlgs()]),
            HBox(children=[schdes, self.getScheduleVisual(),self.getPSchTBschFileName(),self.getPSchTBsavesch_btn(),self.getPSchTBaccsch_btn()]),
            HBox(children=[self.getPSchSolProps()]),
            HBox(children=[VBox(children = [self.getPSchResources()]),VBox(children= [self.getPSTBResSchOutput()])]),
            HBox(children=[VBox(children= [self.getPSchOrderlist()]), VBox(children= [self.getPSTBOrdOutput()])]),
            HBox(children=[VBox(children= [schpr,self.getPSchScheRes()])])]),self.getPSTBGanttOutput()])


        with self.getPSTBGanttOutput():
            clear_output()
       
        with self.getPSTBOrdOutput():
            clear_output()
          
        with self.getPSTBResSchOutput():
            clear_output()

        self.getPSchSolProps().layout.visibility  = 'hidden'
        self.getPSchSolProps().layout.display = 'none'
          

        self.getPSchOrderlist().layout.visibility  = 'hidden'
        self.getPSchOrderlist().layout.display = 'none'
            
        self.getPSTBOrdOutput().layout.visibility  = 'hidden'
        self.getPSTBOrdOutput().layout.display = 'none'

        self.getPSchResources().layout.visibility  = 'hidden'
        self.getPSchResources().layout.display = 'none'

        self.getPSTBResSchOutput().layout.visibility  = 'hidden'
        self.getPSTBResSchOutput().layout.display = 'none'




        tab_sch.layout.height = '600px'
          
        return tab_sch


   

#############################################################################################################################################  







#############################################################################################################################################   




 