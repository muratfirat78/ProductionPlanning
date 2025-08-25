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
import datetime as dt
from matplotlib.collections import PolyCollection
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import pandas as pd
import math

display(HTML("<style>.red_label { color:red }</style>"))
display(HTML("<style>.blue_label { color:blue }</style>"))


class ProductionProgressTab():

    def __init__(self):  
        
        self.VisualManager = None
        self.PPrgScheRes = None
        self.PPrgJoblist = None
        self.PPrgShiftJoblist = None
        self.PPrgResources = None
        self.PPrgOrderlist = None
        self.PPrgOrdProd = None
        self.PPrgOrdOutput = None
        self.PPrgResSchOutput = None
        self.MyOrdTree = None
        self.SchTree = None
        self.SchTreeRootNode = None
        self.OrdTreeRootNode = None
        self.PPrgGanttOutput = None
        self.ScheduleVisual = None

        self.CustOrdersCheck = None
        self.ResourcesCheck = None

        self.CustomerOrderList = None
        self.ResourceList = None

        self.ResShiftLbl = None
        self.ResShifts = None
        self.SelectedResource = None
        self.SelectedShift = None

        self.ResShftJobsLbl = None
        self.JobList = None

        self.JobStartBtn = None
        self.JobCompleteBtn = None
        self.CurrentJob = None
      
        return

    def setSelectedShift(self,myit):
        self.SelectedShift= myit
        return
        
    def getSelectedShift(self):
        return self.SelectedShift


    def setCurrentJob(self,myit):
        self.CurrentJob= myit
        return
        
    def getCurrentJob(self):
        return self.CurrentJob


    def setJobCompleteBtn(self,myit):
        self.JobCompleteBtn= myit
        return
        
    def getJobCompleteBtn(self):
        return self.JobCompleteBtn


    def setJobStartBtn(self,myit):
        self.JobStartBtn= myit
        return
        
    def getJobStartBtn(self):
        return self.JobStartBtn

    def setJobList(self,myit):
        self.JobList= myit
        return
        
    def getJobList(self):
        return self.JobList

    def setResShftJobsLbl(self,myit):
        self.ResShftJobsLbl= myit
        return
        
    def getResShftJobsLbl(self):
        return self.ResShftJobsLbl

    def setSelectedResource(self,myit):
        self.SelectedResource= myit
        return
        
    def getSelectedResource(self):
        return self.SelectedResource

    def setResShiftLbl(self,myit):
        self.ResShiftLbl= myit
        return
        
    def getResShiftLbl(self):
        return self.ResShiftLbl

    def setResShifts(self,myit):
        self.ResShifts= myit
        return
        
    def getResShifts(self):
        return self.ResShifts



    def setResourceList(self,myit):
        self.ResourceList = myit
        return
        
    def getResourceList(self):
        return self.ResourceList


    def setCustomerOrderList(self,myit):
        self.CustomerOrderList  = myit
        return
        
    def getCustomerOrderList(self):
        return self.CustomerOrderList


    def setCustOrdersCheck(self,myit):
        self.CustOrdersCheck  = myit
        return
        
    def getCustOrdersCheck(self):
        return self.CustOrdersCheck

    def setResourcesCheck(self,myit):
        self.ResourcesCheck  = myit
        return
        
    def getResourcesCheck(self):
        return self.ResourcesCheck

   
    def setScheduleVisual(self,myit):
        self.ScheduleVisual  = myit
        return
        
    def getScheduleVisual(self):
        return self.ScheduleVisual 
        

    def setPPrgGanttOutput(self,myit):
        self.PPrgGanttOutput  = myit
        return
        
    def getPPrgGanttOutput(self):
        return self.PPrgGanttOutput
        

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
      


    def setPPrgResSchOutput(self,myit):
        self.PPrgResSchOutput = myit
        return
        
    def getPPrgResSchOutput(self):
        return self.PPrgResSchOutput
        

    def setPPrgOrdOutput(self,myit):
        self.PPrgOrdOutput  = myit
        return
        
    def getPPrgOrdOutput(self):
        return self.PPrgOrdOutput
      

   
    
  

    def setVisualManager(self,myit):
        self.VisualManager = myit
        return


    def setPPrgScheRes(self,myitm):
        self.PPrgScheRes = myitm
        return
        
    def getPPrgScheRes(self):
        return self.PPrgScheRes



    def setPPrgJoblist(self,myitm):
        self.PPrgJoblist = myitm
        return
        
    def getPPrgJoblist(self):
        return self.PPrgJoblist

    def setvShiftJoblist(self,myitm):
        self.PPrgShiftJoblist = myitm
        return
        
    def getPPrgShiftJoblist(self):
        return self.PPrgShiftJoblist

    def setPPrgOrderlist(self,myitm):
        self.PPrgOrderlist = myitm
        return
        
    def getPPrgOrdProd(self):
        return self.PPrgOrdProd

    def setPPrgOrdProd(self,myitm):
        self.PPrgOrdProd = myitm
        return

    def getPPrgResources(self):
        return self.PPrgResources

    def setPPrgResources(self,myitm):
        self.PPrgResources = myitm
        return
        
        
    def getVisualManager(self):
        return self.VisualManager

    def setPPrgOperations(self,myitm):
        self.PPrgOperations = myitm
        return
        
    def getPPrgOperations(self):
        return self.PPrgOperations

    def timestr_to_num(self,timestr):
        return mdates.date2num(datetime.strptime(timestr, '%Y-%m-%d %H:%M:%S'))


    def ShowCustomerOrder(self,event):

        if not 'index' in event['new']:
            return
            
        if event['new']['index'] < 0:
            return
    
        selected = self.getCustomerOrderList().options[event['new']['index']]


        if selected == None:
            return

        if selected == '':
            return

        selected = selected[:selected.find(":")]

        if selected in self.getVisualManager().DataManager.getCustomerOrders():
            myord = self.getVisualManager().DataManager.getCustomerOrders()[selected]

            
            self.getJobList().options = [job.getName() for job in myord.getMyJobs()]

                

            with self.getPPrgOrdOutput():
                clear_output() 

                source = pd.DataFrame(columns=["Job","Start","End"])
    
                minshift = None
                maxshift = None
                xticklbls = []

                self.getJobList().layout.display = 'block'
                self.getJobList().layout.visibility  = 'visible'
                self.getJobList().layout.width = '250px'

                
                schldjobs = 0
                for job in myord.getMyJobs():
                    if job.IsScheduled(): 
                        schldjobs+=1
                        startshift = job.getScheduledShift()
                        if minshift == None: 
                            minshift = startshift  
                        else: 
                            if startshift.getStartHour() < minshift.getStartHour():
                                minshift = startshift
                        
                        
                        starttime = startshift.getStartHour()+timedelta(hours = max(job.getStartTime(),startshift.getStartTime())-startshift.getStartTime())
                        compshift = job.getScheduledCompShift()
                        if maxshift == None: 
                            maxshift = compshift
                        else: 
                            if compshift.getStartHour() > maxshift.getStartHour():
                                maxshift = compshift
    
                        endtime =  compshift.getStartHour()+timedelta(hours = min(job.getCompletionTime(),compshift.getEndTime()+1)-compshift.getStartTime())
                        row = pd.DataFrame([{"Job":job.getName(), "Start":starttime,"End":endtime}])
                        source = pd.concat([source, row], axis=0, ignore_index=True)
                        xticklbls.append(self.timestr_to_num(str(starttime)))
                        xticklbls.append(self.timestr_to_num(str(endtime)))
                        
                if minshift!= None and maxshift!= None:
                
                    fig, ax = plt.subplots(figsize=(5.5,2))
                            
                        #colors = plt.cm.tab10.colors  # get a list of 10 colors
                    cmap = plt.cm.get_cmap('plasma_r')
                    colors = [cmap(i/9) for i in range(10)]   # get a list of 10 colors
                            
                    previous_start = math.inf  # 'previous_start' helps to indicate we're starting again from the left
                    color_start = 0
                    for row in source.itertuples():
                        left = self.timestr_to_num(str(row.Start))
                        right = self.timestr_to_num(str(row.End))
                        if left <= previous_start:
                            color_start = row.Index
                        ax.barh(row.Index, left=left, width=right - left, height=1, color=colors[(row.Index - color_start) % len(colors)])
                        previous_start = left
                    ax.set_xlim(self.timestr_to_num(str(minshift.getStartHour())), self.timestr_to_num(str(maxshift.getEndHour())))
                    xticklbls.insert(0,str(minshift.getStartHour()))
                    xticklbls.append(str(maxshift.getEndHour()))
    
                    difference = maxshift.getEndHour() - minshift.getStartHour()

                    
                    totalhours = difference.total_seconds()//3600
            
                    #ax.set_xticks(np.arange(len(xticklbls)),xticklbls,rotation=45)  # Set label locations.          
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))  # display ticks as hours and minutes

                    intrvl = 1

                    if totalhours > 10:
                        intrvl = int(totalhours/10)
                    
                    ax.xaxis.set_major_locator(mdates.HourLocator(interval=intrvl))  # set a tick every hour
                    ax.set_xlabel('Time')
                    ax.set_ylabel('Jobs')
                    ax.set_ylim(len(source), -1)  # set the limits and reverse the order
                    
                                             
                      
                    #ax.xticks(np.arange(3), ['Tom', 'Dick', 'Sue'])  # Set text labels.
                    #ax.xticks([0, 1, 2], ['January', 'February', 'March'],rotation=20)  # Set text labels and properties.
                   
                    ax.set_yticks(range(len(source)))
                    ax.set_yticklabels(list(source['Job']))
                    plt.xticks(rotation=45)
                            
                    now = minshift.getStartHour()+timedelta(hours = 2)
                    ax.axvline(x=self.timestr_to_num(str(now)),color='r')
                            
                    plt.tight_layout()
                    plt.show()

                else:
                    display("No Scheduled jobs!! ")
        



        return

    
    def ShowResShift(self,event):

        if not 'index' in event['new']:
            return
            
        if event['new']['index'] < 0:
            return
    
        selected = self.getResShifts().options[event['new']['index']]

  
         
        if selected == None:
            return

        if selected == '':
            return


        for shift,jobs in self.getSelectedResource().getSchedule().items():
            if str(shift.getStartHour())+" | "+str(shift.getEndHour()) == selected:
                
                self.setSelectedShift(shift)

                self.getJobList().options = [job.getName() for job in jobs]

                with self.getPPrgOrdOutput():
                    clear_output() 
                    display(selected)
                    plt.style.use('ggplot')

                    source = pd.DataFrame(columns=["Job","Start","End"])

                    for job in jobs:
                        starttime = shift.getStartHour()+timedelta(hours = max(job.getStartTime(),shift.getStartTime())-shift.getStartTime())
                        endtime =  shift.getStartHour()+timedelta(hours = min(job.getCompletionTime(),shift.getEndTime()+1)-shift.getStartTime())
                        row = pd.DataFrame([{"Job":job.getName(), "Start":starttime,"End":endtime}])
                        source = pd.concat([source, row], axis=0, ignore_index=True)
                  
                
                    
                    fig, ax = plt.subplots(figsize=(5.5,2))
                    
                    #colors = plt.cm.tab10.colors  # get a list of 10 colors
                    cmap = plt.cm.get_cmap('plasma_r')
                    colors = [cmap(i/9) for i in range(10)]   # get a list of 10 colors
                    
                    previous_start = math.inf  # 'previous_start' helps to indicate we're starting again from the left
                    color_start = 0
                    for row in source.itertuples():
                        left = self.timestr_to_num(str(row.Start))
                        right = self.timestr_to_num(str(row.End))
                        if left <= previous_start:
                            color_start = row.Index
                        ax.barh(row.Index, left=left, width=right - left, height=1, color=colors[(row.Index - color_start) % len(colors)])
                        previous_start = left
                    ax.set_xlim(self.timestr_to_num(str(shift.getStartHour())), self.timestr_to_num(str(shift.getEndHour())))
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))  # display ticks as hours and minutes
                    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))  # set a tick every hour
                    ax.set_xlabel('Time')
                    ax.set_ylabel('Jobs')
                    ax.set_ylim(len(source), -1)  # set the limits and reverse the order
                    ax.set_yticks(range(len(source)))
                    ax.set_yticklabels(list(source['Job']))
                    
                    now = shift.getStartHour()+timedelta(hours = 2)
                    ax.axvline(x=self.timestr_to_num(str(now)),color='r')
                    
                    plt.tight_layout()
                    plt.show()



        return
        

    def ShowResourceShift(self,event):

        if not 'index' in event['new']:
            return
            
        if event['new']['index'] < 0:
            return
    
        selected = self.getResourceList().options[event['new']['index']]

        with self.getPPrgOrdOutput():
            clear_output() 
         
        if selected == None:
            return

        if selected == '':
            return

        if selected in self.getVisualManager().DataManager.getResources():
            selected_res = self.getVisualManager().DataManager.getResources()[selected]

            self.setSelectedResource(selected_res)

            shftops = []
            for shift,jobs in selected_res.getSchedule().items():
                shftops.append(str(shift.getStartHour())+" | "+str(shift.getEndHour()))

            self.getResShifts().options = shftops
     
        return


 

    def ShowDescriptives(self,event):

        if not 'index' in event['new']:
            return
            
        if event['new']['index'] < 0:
            return
    
        selected = self.getCustOrdersCheck().options[event['new']['index']]

        if selected == None:
            return

        if selected == '':
            return


      
        if selected == 'Resources':

            self.getResShftJobsLbl().value = "Resource Jobs"
            
            self.getResourceList().layout.display = 'block'
            self.getResourceList().layout.visibility  = 'visible'
            self.getResourceList().layout.width = '450px'
            self.getResourceList().layout.height = '150px'

            self.getResShifts().layout.display = 'block'
            self.getResShifts().layout.visibility  = 'visible'
        
            self.getResShiftLbl().layout.display = 'block'
            self.getResShiftLbl().layout.visibility  = 'visible'


            self.getJobList().layout.display = 'block'
            self.getJobList().layout.visibility  = 'visible'
            self.getJobList().layout.width = '250px'

            self.getJobStartBtn().layout.display = 'block'
            self.getJobStartBtn().layout.visibility  = 'visible'
            self.getJobCompleteBtn().layout.display = 'block'
            self.getJobCompleteBtn().layout.visibility  = 'visible'



            self.getCustomerOrderList().layout.visibility  = 'hidden'
            self.getCustomerOrderList().layout.display = 'none'


        
        if selected == 'Customer Orders':

            self.getResShftJobsLbl().value = "Order Jobs"

            self.getCustomerOrderList().layout.display = 'block'
            self.getCustomerOrderList().layout.visibility  = 'visible'
            self.getCustomerOrderList().layout.width = '300px'
            self.getCustomerOrderList().layout.height = '150px'

            self.getJobList().layout.display = 'block'
            self.getJobList().layout.visibility  = 'visible'
            self.getJobList().layout.width = '250px'
         
            self.getJobStartBtn().layout.display = 'block'
            self.getJobStartBtn().layout.visibility  = 'visible'
            self.getJobCompleteBtn().layout.display = 'block'
            self.getJobCompleteBtn().layout.visibility  = 'visible'

            
            self.getResourceList().layout.visibility  = 'hidden'
            self.getResourceList().layout.display = 'none'
            self.getResShifts().layout.visibility  = 'hidden'
            self.getResShifts().layout.display = 'none'
        
            self.getResShiftLbl().layout.visibility  = 'hidden'
            self.getResShiftLbl().layout.display = 'none'

           
        with self.getPPrgOrdOutput():
            clear_output() 
        
        return

    
    def SetJob(self,event):

        if not 'index' in event['new']:
            return
            
        if event['new']['index'] < 0:
            return
    
        selected = self.getJobList().options[event['new']['index']]

        if selected == None:
            return

        if selected == '':
            return

        if self.getSelectedResource() != None: 

            if self.getSelectedShift() != None: 

                if self.getSelectedShift() in self.getSelectedResource().getSchedule():

                    for j in self.getSelectedResource().getSchedule()[self.getSelectedShift()]:
                        if j.getName() == selected:
                            self.setCurrentJob(j)

                    
        
        return

    def SetJobStarted(self,event):

        self.getCurrentJob().setActualStart(datetime.now())

        if self.getSelectedResource() != None: 

            if self.getSelectedShift() != None: 

                if self.getSelectedShift() in self.getSelectedResource().getSchedule():

                    jops = []
                    for j in self.getSelectedResource().getSchedule()[self.getSelectedShift()]:
                        jobstr = j.getName()
                        if j.getActualStart() != None:
                            jobstr+=" (St: "+str(j.getActualStart())
                        else:
                            jobstr+=" (St: -"
                        if j.getActualCompletion() != None:
                            jobstr+=" (Cp: "+str(j.getActualCompletion())
                        else:
                            jobstr+=" (Cp: -"

                    self.getJobList().options = jops
        
        
        return

    def SetJobCompleted(self,event):

        self.getCurrentJob().setActualCompletion(datetime.now())

        if self.getSelectedResource() != None: 

            if self.getSelectedShift() != None: 

                if self.getSelectedShift() in self.getSelectedResource().getSchedule():

                    jops = []
                    for j in self.getSelectedResource().getSchedule()[self.getSelectedShift()]:
                        jobstr = j.getName()
                        if j.getActualStart() != None:
                            jobstr+=" (St: "+str(j.getActualStart())
                        else:
                            jobstr+=" (St: -"
                        if j.getActualCompletion() != None:
                            jobstr+=" (Cp: "+str(j.getActualCompletion())
                        else:
                            jobstr+=" (Cp: -"

                    self.getJobList().options = jops
        
        return




    
    def generatePPrgTAB(self):
    


        self.setCustOrdersCheck(widgets.Dropdown(options=['Customer Orders','Resources']))
        self.getCustOrdersCheck().layout.width = '150px'
        self.getCustOrdersCheck().observe(self.ShowDescriptives)

        self.setResShiftLbl(widgets.Label(value ='Resource Shifts'))
        self.getResShiftLbl().add_class("red_label")
        self.getResShiftLbl().layout.width = "120px"

        self.setResShftJobsLbl(widgets.Label(value ='Shift Jobs'))
        self.getResShftJobsLbl().add_class("red_label")
        self.getResShftJobsLbl().layout.width = "120px"
        self.setJobList(widgets.Select(options=[],desciption = ''))
        self.getJobList().observe(self.SetJob)
        self.getJobList().options = ["Jobs.."]
        self.getJobList().layout.width = "300px"

        self.setJobStartBtn(widgets.Button(desciption = "Set Started"))
        self.getJobStartBtn().on_click(self.SetJobStarted)
        self.setJobCompleteBtn(widgets.Button(desciption = "SetCompleted"))
        self.getJobCompleteBtn().on_click(self.SetJobCompleted)

        self.setResShifts(widgets.Dropdown(options=[]))
        self.getResShifts().observe(self.ShowResShift)

        self.setCustomerOrderList(widgets.Select(options=[],desciption = ''))
        self.getCustomerOrderList().options = ["Customer Order.."]
        self.getCustomerOrderList().layout.width = "300px"
        self.getCustomerOrderList().observe(self.ShowCustomerOrder)
        
        self.setResourceList(widgets.Select(options=[],desciption = ''))
        self.getResourceList().options = ["Resource.."]
        self.getResourceList().layout.width = "450px"
        self.getResourceList().observe(self.ShowResourceShift)
        
        schdes = widgets.Label(value ='Production Progress')
        schdes.add_class("red_label")
        schdes.layout.width = "120px"


        self.setPPrgOrdOutput(widgets.Output())

        with self.getPPrgOrdOutput():
            clear_output()
            display("Test")
        
        tab_sch = HBox(children =[ 
                       VBox(children = [schdes,self.getCustOrdersCheck(),self.getCustomerOrderList(),self.getResourceList()]),
                       VBox(children = [self.getResShiftLbl(),self.getResShifts(),self.getPPrgOrdOutput(),self.getResShftJobsLbl()
                                        ,HBox(children=[self.getJobStartBtn(),self.getJobList(),self.getJobCompleteBtn()])
                                       ])
                       ])
                                     

        self.getResourceList().layout.visibility  = 'hidden'
        self.getResourceList().layout.display = 'none'

        self.getResShifts().layout.visibility  = 'hidden'
        self.getResShifts().layout.display = 'none'
        
        self.getResShiftLbl().layout.visibility  = 'hidden'
        self.getResShiftLbl().layout.display = 'none'

       
        self.getJobList().layout.visibility  = 'hidden'
        self.getJobList().layout.display = 'none'

        self.getJobStartBtn().layout.visibility  = 'hidden'
        self.getJobStartBtn().layout.display = 'none'

        self.getJobCompleteBtn().layout.visibility  = 'hidden'
        self.getJobCompleteBtn().layout.display = 'none'




        tab_sch.layout.height = '600px'
          
        return tab_sch


   

#############################################################################################################################################  







#############################################################################################################################################   




 