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
        self.CurrentShift = None

        self.CustOrdersCheck = None
        self.ResourcesCheck = None

        self.CustomerOrderList = None
        self.ResourceList = None

        self.ResShiftLbl = None
        self.ResShifts = None
        self.SelectedResource = None
        self.SelectedShift = None
        self.SelectedOrder = None

        self.ProgressSlider = None

        self.ProgressMode =  None
        self.ProgressItem = None

        self.ResShftJobsLbl = None
        self.JobList = None
        self.JobInfo = None
        self.JobInfo2 = None
        self.JobInfo3 = None  
        self.JobInfo4 = None
        self.JobInfo5 = None
        self.ShiftInfo = None
        self.ShiftTime = None
        self.ShiftTimeLbl = None

        self.OrderInfo = None
        self.OrderInfo2 = None
        self.OrderInfo3 = None  
        self.OrderInfo4 = None

        self.JobStartBtn = None
        self.JobCompleteBtn = None
        self.CurrentJob = None

        self.PProgReport = None
        self.resords = None   
        self.weekradio = None
        self.infotype = "Customer Orders"

        self.resshifts = None
        self.currentshifts = []
        self.currentshift = None
        self.jobinfo = None

        self.ResDropDown = None
        self.reslabel = None
        self.orderbox = None
        self.jobinfobox = None
        self.JobGernerateButton = None
        
      
        return

    def setJobGernerateButton(self,myit):
        self.JobGernerateButton= myit
        return
        
    def getJobGernerateButton(self):
        return self.JobGernerateButton
    


    def setCurrentShift(self,myit):
        self.CurrentShift = myit
        return
        
    def getCurrentShift(self):
        return self.CurrentShift
    

    def setReslabel(self,myit):
        self.reslabel = myit
        return
        
    def getReslabel(self):
        return self.reslabel


    
    def setShiftTimeLbl(self,myit):
        self.ShiftTimeLbl = myit
        return
        
    def getShiftTimeLbl(self):
        return self.ShiftTimeLbl


    def setShiftInfo(self,myit):
        self.ShiftInfo = myit
        return
        
    def getShiftInfo(self):
        return self.ShiftInfo

    def setShiftTime(self,myit):
        self.ShiftTime = myit
        return
        
    def getShiftTime(self):
        return self.ShiftTime



    def setResDropDown(self,myit):
        self.ResDropDown = myit
        return
        
    def getResDropDown(self):
        return self.ResDropDown

        
    def setOrderInfo(self,myit):
        self.OrderInfo = myit
        return
        
    def getOrderInfo(self):
        return self.OrderInfo

    def setProgressSlider(self,myit):
        self.ProgressSlider = myit
        return
        
    def getProgressSlider(self):
        return self.ProgressSlider


    def setProgressMode(self,myit):
        self.ProgressMode = myit
        return
        
    def getProgressMode(self):
        return self.ProgressMode

    def setProgressItem(self,myit):
        self.ProgressItem = myit
        return
        
    def getProgressItem(self):
        return self.ProgressItem

    
    def setOrderInfo2(self,myit):
        self.OrderInfo2 = myit
        return
        
    def getOrderInfo2(self):
        return self.OrderInfo2

    def setOrderInfo3(self,myit):
        self.OrderInfo3 = myit
        return
        
    def getOrderInfo3(self):
        return self.OrderInfo3

    def setOrderInfo4(self,myit):
        self.OrderInfo4 = myit
        return
        
    def getOrderInfo4(self):
        return self.OrderInfo4
        
        

    def getResShifts(self):
        return self.resshifts


        
    def getResords(self):
        return self.resords

    def setInfoType(self,mytp):
        self.infotype = mytp
        return
    def getInfoType(self):
        return self.infotype 
 

    def getWeekRadio(self):
        return self.weekradio

    def setJobInfo5(self,myit):
        self.JobInfo5= myit
        return
        
    def getJobInfo5(self):
        return self.JobInfo5


    def setJobInfo4(self,myit):
        self.JobInfo4= myit
        return
        
    def getJobInfo4(self):
        return self.JobInfo4

    def setJobInfo3(self,myit):
        self.JobInfo3= myit
        return
        
    def getJobInfo3(self):
        return self.JobInfo3

    def setJobInfo2(self,myit):
        self.JobInfo2= myit
        return
        
    def getJobInfo2(self):
        return self.JobInfo2

    def setJobInfo(self,myit):
        self.JobInfo= myit
        return
        
    def getJobInfo(self):
        return self.JobInfo

    def setPProgReport(self,myit):
        self.PProgReport= myit
        return
        
    def getPProgReport(self):
        return self.PProgReport

    def setSelectedOrder(self,myit):
        self.SelectedOrder= myit
        return
        
    def getSelectedOrder(self):
        return self.SelectedOrder


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

    def ShowShiftTime(self,event):


        #change_new = event["new"]
 
       
        return

###############################################################################################################################################
    def ShowInformation(self,event):

        if not 'index' in event['new']:
            return
            
        if event['new']['index'] < 0:
            return

        selected = self.getCustomerOrderList().options[event['new']['index']]


        self.ShowItemInformation(selected)
            

        return

######################################################################################################################################
    def ShowItemInformation(self,selected):

        self.getPProgReport().value+="Selected from list: "+str(selected)+" infotype: "+str(self.infotype)+"\n"

        if self.getProgressMode() == "Customer Orders":

            self.jobinfobox.layout.visibility = 'hidden'
            self.jobinfobox.layout.display = 'none'
            

            self.orderbox.layout.display = 'block'
            self.orderbox.layout.visibility = 'visible'

            
 
            # first find and set selected order
            ordername = selected[:selected.find(": Status | ")]
            self.getPProgReport().value+="ordername: "+str(ordername)+"\n"
            
            if ordername in self.getVisualManager().DataManager.getCustomerOrders():
                myorder = self.getVisualManager().DataManager.getCustomerOrders()[ordername]

                self.setProgressItem(myorder)
                self.setSelectedOrder(myorder)
                self.getPProgReport().value+="Selected Order "+str(myorder.getName())+" jobs: "+str(len(myorder.getMyJobs()))+"\n"

                self.getOrderInfo().layout.display = 'block'
                self.getOrderInfo().layout.visibility = 'visible'
                self.getOrderInfo2().layout.display = 'block'
                self.getOrderInfo2().layout.visibility = 'visible'
                self.getOrderInfo3().layout.display = 'block'
                self.getOrderInfo3().layout.visibility = 'visible'
                self.getOrderInfo4().layout.display = 'block'
                self.getOrderInfo4().layout.visibility = 'visible'
            
                
                self.getJobList().layout.display = 'block'
                self.getJobList().layout.visibility  = 'visible'
          
          
                self.getJobList().options = [job.getName() for job in myorder.getMyJobs()]
                self.getJobList().selectedindex = -1
                
                self.getOrderInfo().value = "Product: "+myorder.getProduct().getName()
                self.getOrderInfo2().value  = 'Quantity: '+str(myorder.getQuantity()) 
                self.getOrderInfo3().value = 'Component: '+str(myorder.getComponentAvailable())
                self.getOrderInfo4().value = 'Deadline: '+str(myorder.getDeadLine())

            
                #for job in myord.getMyJobs():
            else:
                self.setSelectedOrder(None)
                self.setProgressItem(None)
    

            
        if self.getProgressMode() == "Resources":

            
            self.orderbox.layout.visibility = 'hidden'
            self.orderbox.layout.display = 'none'
 
            self.jobinfobox.layout.visibility = 'hidden'
            self.jobinfobox.layout.display = 'none'

            self.getPProgReport().value+="start week: "+str(self.getVisualManager().DataManager.getScheduleStartWeek())+"\n"

            self.getJobList().options = []
            
            if self.getVisualManager().DataManager.getScheduleStartWeek() != None:
                stweek = self.getVisualManager().DataManager.getScheduleStartWeek()
                edweek = self.getVisualManager().DataManager.getScheduleEndWeek()

                self.getPProgReport().value+="Selected: "+str(selected)+"\n"

                for resname,res in self.getVisualManager().DataManager.getResources().items():
                    if resname == selected:
                        self.setSelectedResource(res)
                        self.setProgressItem(res)
                        break
                        

                self.getPProgReport().value+="sweek : "+str(stweek)+", endweek: "+str(edweek)+"\n"
                if stweek > edweek:
                    weeks = [x for x in range(stweek,52+1)]
                    weeks += [x for x in range(1,edweek+1)]
                    self.weekradio.options = ["Week "+str(x) for x in weeks]
                else:
                    self.weekradio.options = ["Week "+str(x) for x in range(stweek,edweek+1)]
                    
                self.weekradio.layout.display = 'block'
                self.weekradio.layout.visibility = 'visible'

                self.resshifts.layout.display = 'block'
                self.resshifts.layout.visibility = 'visible'
            
       

        if self.getProgressMode() == "Active Jobs":

            
            self.orderbox.layout.visibility = 'hidden'
            self.orderbox.layout.display = 'none'

            
                
            # self.getShiftInfo().value = 
            
            myjob = None
            for ordname,ordr in self.getVisualManager().DataManager.getCustomerOrders().items():
                for job in ordr.getMyJobs():
                    if job.getName() == selected:
                        self.setProgressItem(job)
                        break
                if myjob != None:
                    break
            myjob = self.getProgressItem()
            self.ShowJobStatus(myjob)
            
        
        return

    #def ShowWeekShifts(self,weekno):
        
#################################################################################################################################################
    def ShowJobStatus(self,myjob):

     
        if myjob != None:

            
            self.jobinfobox.layout.display = 'block'
            self.jobinfobox.layout.visibility = 'visible'
            self.getResDropDown().options = []
        

            self.getJobInfo().value ="PN: "+str(myjob.getOperation().getProduct().getPN())
            self.getJobInfo2().value ="Progress: "#+str(myjob.getOperation().getName())
            self.getJobInfo3().value ="Quantity: "+str(myjob.getQuantity())
            self.getJobInfo5().value ="Status: "+myjob.getStatus()
            self.getShiftTimeLbl().value = "XXXXXXXXXXX"
            starttime = datetime.now()+timedelta(hours = 1)
            curr_shift = self.getVisualManager().DataManager.getSchedulingManager().getShiftgivenTime(starttime)
            self.getPProgReport().value+="current shift??...."+str(curr_shift)+"\n"
            self.setCurrentShift(curr_shift)
            shifthrs = []
            curr_time = self.getCurrentShift().getStartHour()

            self.getPProgReport().value+=curr_shift.String("current shift??....")+"\n"
        
            for halfhr in range(1,17):
                shifthrs.append(curr_time)
                curr_time = curr_time + timedelta(minutes = 30)

            self.getShiftTime().options =  shifthrs   
            
            if curr_shift != None: 
                self.getShiftInfo().value = curr_shift.String("Current shift: ")
                

            if myjob.getStatus().find("Pending") > -1: 
                if  self.getResDropDown().value!= None:
                    self.getResDropDown().value = None
                self.getResDropDown().disabled = False

                    
                lpc = myjob.getLPC()
                curr_time = self.getCurrentShift().getStartHour()
                shifthrs = []
                if lpc == None:
                    lpc = curr_time - timedelta(minutes = 1)
                for halfhr in range(1,17):
                    if curr_time >= lpc:
                        shifthrs.append(curr_time)
                            
                    curr_time = curr_time + timedelta(minutes = 30)

                self.getShiftTime().options =  shifthrs   

                self.getPProgReport().value+="Job has pending status...."+"\n"

                self.getReslabel().layout.display = 'block'
                self.getReslabel().layout.visibility = 'visible'

                self.getJobStartBtn().disabled = True
                self.getPProgReport().value+="Alternatives... "+str(len(self.getVisualManager().getSchedulingManager().getAlternativeResources(myjob)))+"\n"
                    
                self.getResDropDown().options =  [r.getName() for r in self.getVisualManager().getSchedulingManager().getAlternativeResources(myjob)]
                    
                try: 
                    self.getResDropDown().value = 'Select'
                except Exception as e: 
                    self.getPProgReport().value+="Error: "+str(e)+", val: "+str(self.getResDropDown())+"\n"
                        
                self.getResDropDown().layout.display = 'block'
                self.getResDropDown().layout.visibility = 'visible'
           
            self.getPProgReport().value+="job status: "+str(myjob.getStatus())+"\n" 

            if myjob.getStatus() == "In production": 
                shifthrs = []
                curr_time = self.getCurrentShift().getStartHour()+timedelta(minutes = 30)
                    
                for halfhr in range(1,16):
                    if curr_time > myjob.getMySch().getActualStart():
                        shifthrs.append(curr_time)

                    curr_time = curr_time + timedelta(minutes = 30)
                   

                self.getShiftTime().options =  shifthrs   
                self.getResDropDown().layout.display = 'block'
                self.getResDropDown().layout.visibility = 'visible'
                self.getJobInfo5().value +=", Started: "+str(myjob.getMySch().getActualStart())
                self.getResDropDown().options =  [myjob.getMySch().getScheduledResource().getName()]
                self.getResDropDown().value = myjob.getMySch().getScheduledResource().getName()
                self.getResDropDown().disabled = True
                  
            else: 
                if myjob.getStatus() == "Completed": 
                    self.getJobInfo5().value ="Completed: "+str(myjob.getMySch().getActualCompletion())
                    self.getResDropDown().options = [myjob.getMySch().getScheduledResource().getName()]
                    self.getResDropDown().value = myjob.getMySch().getScheduledResource().getName()
                    self.getResDropDown().disabled = True
                    
                            

            self.getPProgReport().value+="SCHJOB none ?  "+str(myjob.getMySch() == None)+"\n"

            self.setCurrentJob(myjob)

            
            if myjob.getMySch() == None:
                myjob.initializeMySch()
                
                
            if myjob.getMySch() != None:

                if myjob.getMySch().getScheduledStart()!= None: 
                    starttime =  myjob.getMySch().getScheduledStart(); endtime =  myjob.getMySch().getScheduledCompletion() 
    
                        
                    schstr = "  {:d}-{:02d}-{:02d} / {:02d}:{:02d} ".format(starttime.year,starttime.month,starttime.day,starttime.hour,starttime.minute) 
                    schstr+= " -> "+" {:d}-{:02d}-{:02d} / {:02d}:{:02d} ".format(endtime.year,endtime.month,endtime.day,endtime.hour,endtime.minute) 
                    schstr+=" @"+myjob.getMySch().getScheduledResource().getName()
      
                        
                    self.getJobInfo4().value ="Schedule: "+schstr
                else:
                    self.getJobInfo4().value =""

                if myjob.getStatus().find("Pending") > -1:
                    self.getJobStartBtn().layout.display  = 'block'
                    self.getJobStartBtn().layout.visibility  = 'visible'
                    self.getJobCompleteBtn().layout.visibility  = 'hidden'
                    self.getJobCompleteBtn().layout.display  = 'none'

                    self.getResDropDown().layout.visibility = 'visible'
                    self.getShiftTime().layout.visibility = 'visible'
                    self.getShiftInfo().layout.visibility = 'visible'
                        
                if myjob.getStatus() == "In production":
                    self.getJobCompleteBtn().layout.display  = 'block'
                    self.getJobCompleteBtn().layout.visibility  = 'visible'
                    self.getJobStartBtn().layout.visibility  = 'hidden'
                    self.getJobStartBtn().layout.display  = 'none'
                    self.getResDropDown().layout.visibility = 'visible'
                    self.getShiftTime().layout.visibility = 'visible'
                    self.getShiftInfo().layout.visibility = 'visible'

            else:
                self.getJobInfo4().value =""
                self.getResDropDown().options = []
                self.getResDropDown().layout.visibility = 'hidden'
                self.getShiftTime().layout.visibility = 'hidden'
                self.getShiftInfo().layout.visibility = 'hidden'
                if myjob.getStatus() == "Pending (all predecessors completed)":
                    self.getJobStartBtn().layout.display  = 'block'
                    self.getJobStartBtn().layout.visibility  = 'visible'
                    self.getJobCompleteBtn().layout.visibility  = 'hidden'
                    self.getJobCompleteBtn().layout.display  = 'none'
                        
          

        return 


#################################################################################################################################################

    
    def ShowResShift(self,event):

        if not 'index' in event['new']:
            return
            
        if event['new']['index'] < 0:
            return
    
        selected = self.getResShifts().options[event['new']['index']]

        with self.getPPrgOrdOutput():
            clear_output() 
            plt.show()    

        self.getJobStartBtn().layout.visibility  = 'hidden'
        self.getJobCompleteBtn().layout.visibility  = 'hidden'
        self.getJobInfo().value = ''
        self.getJobInfo2().value = ''
        self.getJobInfo3().value = ''
        self.getJobInfo4().value = ''
        self.getJobInfo5().value = ''
         
         
        if selected == None:
            return

        if selected == '':
            return

        self.getPProgReport().value+="Selected: "+str(selected)+"\n"


        for shift,jobs in self.getSelectedResource().getSchedule().items():
            if str(shift.getDay().date())+": "+str(shift.getStartHour().strftime("%H:%M"))+" | "+str(shift.getEndHour().strftime("%H:%M")) == selected:
                self.getPProgReport().value+="Selected found.. , Jobs: "+str(len(jobs))+"\n"
                
                self.setSelectedShift(shift)
                self.getJobList().layout.visibility  = 'visible'

                
                self.getJobList().options = [job.getJob().getName() for job in jobs]
                self.getJobList().selectedindex = -1

               

                with self.getPPrgOrdOutput():
                    clear_output() 

                    
                    plt.style.use('ggplot')

                 
                    source = pd.DataFrame(columns=["Job","Start","End"])

                    for job in jobs:
                        
                        self.getPProgReport().value+="Shft strt "+str(shift.getStartHour())+"-> Jobstrt: "+str(job.getScheduledStart())+"\n"


                        starttime = job.getScheduledStart() if shift == job.getScheduledCompShift() else shift.getStartHour()
                        endtime = job.getScheduledCompletion() if shift == job.getScheduledCompShift() else shift.getEndHour()

                        
                        row = pd.DataFrame([{"Job":job.getJob().getName(), "Start":starttime,"End":endtime}])
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
                    ax.set_title(self.getSelectedResource().getName()+" ~ "+selected)
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

        
        with self.getPPrgOrdOutput():
            clear_output() 
            plt.show()  
    
        selected = self.getResourceList().options[event['new']['index']]

        self.getJobList().layout.visibility = 'hidden'
        self.getJobStartBtn().layout.visibility  = 'hidden'
        self.getJobCompleteBtn().layout.visibility  = 'hidden'
        self.getJobInfo().value = ''
        self.getJobInfo2().value = ''
        self.getJobInfo3().value = ''
        self.getJobInfo4().value = ''
        self.getJobInfo5().value = ''
       
         
        if selected == None:
            return

        if selected == '':
            return

        if selected in self.getVisualManager().DataManager.getResources():
            selected_res = self.getVisualManager().DataManager.getResources()[selected]

            self.setSelectedResource(selected_res)
            self.setSelectedOrder(None)

            nojobs = sum([len(x) for x in selected_res.getSchedule().values()])

            self.getPProgReport().value+=" Resource "+selected+" has "+str(nojobs)+" jobs scheduled"+"\n"
            shftops = []
            for shift,jobs in selected_res.getSchedule().items():
                shftops.append(str(shift.getDay().date())+": "+str(shift.getStartHour().strftime("%H:%M"))+" | "+str(shift.getEndHour().strftime("%H:%M")))

            self.getResShifts().options = shftops
            self.getResShifts().value = shftops[0]
        else:
            with self.getPPrgOrdOutput():
                clear_output() 
                plt.show() 
            self.getResShifts().options  = []
            
     
        return


    def ShowDescriptives2(self,event):

        self.getPProgReport().value +="Event "+str(event)+"\n"

        self.getPProgReport().value +="event new: "+str(event['new'])+"\n"
     
        selected = ''

        self.getPProgReport().value +="event name "+str(event['name'])+"\n"

        if event['name'] == 'label':
            selected = event['new']
        else: 
            if event['name'] == 'index':
                selected = self.resords.options[event['new']]
            else:
                return

        self.getReslabel().layout.visibility = 'hidden'
        self.getReslabel().layout.display = 'none'
        self.weekradio.layout.visibility = 'hidden'
        self.weekradio.layout.display = 'none'
        self.resshifts.layout.visibility = 'hidden'
        self.resshifts.layout.display = 'none'
        self.getJobList().layout.visibility = 'hidden'
        self.getJobList().layout.display = 'none'
        self.getOrderInfo().layout.visibility  = 'hidden'
        self.getOrderInfo().layout.display = 'none'
        self.getOrderInfo2().layout.visibility  = 'hidden'
        self.getOrderInfo2().layout.display = 'none'
        self.getOrderInfo3().layout.visibility  = 'hidden'
        self.getOrderInfo3().layout.display = 'none'
        self.getOrderInfo4().layout.visibility  = 'hidden'
        self.getOrderInfo4().layout.display = 'none'
        self.weekradio.layout.visibility = 'hidden'
        self.weekradio.layout.display = 'none'
        self.resshifts.layout.visibility = 'hidden'
        self.resshifts.layout.display = 'none'
        

        self.setProgressMode(selected)

        self.jobinfobox.layout.visibility = 'hidden'
        self.jobinfobox.layout.display = 'none'
        

        self.getPProgReport().value +="Selected: "+selected+", current info: "+str(self.infotype)+"\n"
      
        if self.getProgressMode() == 'Resources':

            self.getPProgReport().value +="visibility: "+str(self.weekradio.layout.visibility)+"\n"
            if self.infotype != selected:
                self.infotype = selected
                self.getCustomerOrderList().options = [resname for resname in self.getVisualManager().DataManager.getResources().keys()]
                
        
        if self.getProgressMode() == 'Customer Orders':

              
            

            self.getPProgReport().value +="visibility: "+str(self.weekradio.layout.visibility)+"\n"
            if self.infotype != selected:
                self.infotype = selected
                self.getCustomerOrderList().options = [ordname+": Status | "+myord.getStatus() for ordname,myord in self.getVisualManager().DataManager.getCustomerOrders().items()] 
          

        if self.getProgressMode() == 'Active Jobs':

            if self.infotype != selected:
                self.infotype = selected
            joblist = []
            for ordname,ordr in self.getVisualManager().DataManager.getCustomerOrders().items():
                self.getPProgReport().value +="ordr: "+str(ordname)+": "+str(len(ordr.getMyJobs()))+"\n"
                for job in ordr.getMyJobs():
                    self.getPProgReport().value +="   >>"+str(job.getName())+"\n"
                    self.getPProgReport().value +="   >> Status: "+str(job.getStatus())+"\n"
                    if (job.getStatus().find("Pending") > -1) or job.getStatus() == "In production": 
                        joblist.append(job.getName())
                        self.getPProgReport().value +="      >>> Inserted..."+"\n"

            self.getPProgReport().value +="   >> Active Jobs"+str(len(joblist))+"\n"
            self.getCustomerOrderList().options = [jname for jname in joblist]                                
               
            
     
        

        self.getPProgReport().value +="final info: "+str(self.infotype)+"\n"
      
           
        with self.getPPrgOrdOutput():
            clear_output() 
        
        return
###################################################################################################################  

    def ShowShifts(self,event):


        self.getPProgReport().value +="event: "+str(event)+"\n"

        weekstr = self.weekradio.value

        if self.weekradio.value == "Week":
            return

        self.getPProgReport().value +="selected week : "+str(self.weekradio.value)+"\n"

        weekstr = weekstr[weekstr.find("Week")+5:]

        self.getPProgReport().value +="selected week : "+str(weekstr)+"\n"
    
        myshifts = []
        self.currentshifts = []
        for cdate,shifts in self.getVisualManager().DataManager.getSchedulingManager().getMyShifts().items():
            if str(cdate.isocalendar()[1]) == weekstr:
                for shift in shifts:
                    if shift in self.getSelectedResource().getSchedule():
                        myshifts.append("Shift: "+str(shift.getDay().date())+" | "+str(shift.getNumber())+": "+" , {:02d}:{:02d}".format(shift.getStartHour().hour, shift.getStartHour().minute)+"-"+" , {:02d}:{:02d}".format(shift.getEndHour().hour, shift.getEndHour().minute))
                        self.currentshifts.append(shift)
                    

        self.getPProgReport().value +="current shifts: "+str(len(self.currentshifts))+"\n"

        self.resshifts.layout.display = 'block' 
        self.resshifts.layout.visibility  = 'visible'
        self.resshifts.options = [s for s in myshifts]
        

       
        self.getJobInfo().layout.visibility  = 'hidden'
        self.getJobInfo().layout.display = 'none'

        
        self.getJobInfo2().layout.visibility  = 'hidden'
        self.getJobInfo2().layout.display = 'none'
        self.getJobInfo3().layout.visibility  = 'hidden'
        self.getJobInfo3().layout.display = 'none'
        self.getJobInfo4().layout.visibility  = 'hidden'
        self.getJobInfo4().layout.display = 'none'
        self.getJobInfo5().layout.visibility  = 'hidden'
        self.getJobInfo5().layout.display = 'none'
        self.getJobStartBtn().layout.visibility  = 'hidden'
        self.getJobStartBtn().layout.display = 'none'
        self.getJobCompleteBtn().layout.visibility  = 'hidden'
        self.getJobCompleteBtn().layout.display = 'none'
        
        self.resshifts.layout.height = '180px'

        return 

    def ShowJobs(self,event):

        self.currentshift = None

        self.getPProgReport().value +="event: "+str(event)+"\n"

        if self.getJobList().layout.display == 'none':
            self.getJobList().layout.display = 'block'
            self.getJobList().layout.visibility = 'visible'

        

        for i in range(len(self.resshifts.options)):
            if self.resshifts.options[i] == self.resshifts.value:
                self.currentshift = self.currentshifts[i]
                break
            

        if self.currentshift != None:
            self.getPProgReport().value +="selected shift day: "+str(self.currentshift.getDay())+"\n"

            
            if self.currentshift in self.getSelectedResource().getSchedule():
                jobs = self.getSelectedResource().getSchedule()[self.currentshift]
                self.getPProgReport().value+="Selected found.. , Jobs: "+str(len(jobs))+"\n"
                self.getJobList().options = [job.getJob().getName() for job in jobs]
                self.getJobList().selectedindex = -1
              
                
        self.getJobInfo().layout.visibility  = 'hidden'
        self.getJobInfo().layout.display = 'none'
        self.getJobInfo2().layout.visibility  = 'hidden'
        self.getJobInfo2().layout.display = 'none'
        self.getJobInfo3().layout.visibility  = 'hidden'
        self.getJobInfo3().layout.display = 'none'
        self.getJobInfo4().layout.visibility  = 'hidden'
        self.getJobInfo4().layout.display = 'none'
        self.getJobInfo5().layout.visibility  = 'hidden'
        self.getJobInfo5().layout.display = 'none'
        self.getJobStartBtn().layout.visibility  = 'hidden'
        self.getJobStartBtn().layout.display = 'none'
        self.getJobCompleteBtn().layout.visibility  = 'hidden'
        self.getJobCompleteBtn().layout.display = 'none'
           

        return
##########################################################################################################################################
    def StartEnable(self,event):

        if self.getResDropDown().value != None:
            self.getJobStartBtn().disabled = False
            

        return

##########################################################################################################################################      
    def ShowJobInfo(self,event):
  
        if not 'index' in event['new']:
            return
            
        if event['new']['index'] < 0:
            return
    
        jobname = self.getJobList().options[event['new']['index']]
        

        self.getPProgReport().value +=" job info event?? "+str(event)+"\n"

        if jobname == None:
            return


            

        self.getJobStartBtn().layout.visibility  = 'hidden'
        self.getJobStartBtn().layout.display = 'none'
        self.getJobCompleteBtn().layout.visibility  = 'hidden'
        self.getJobCompleteBtn().layout.display = 'none'

        self.getPProgReport().value+="Selected  Job: "+str(jobname)+"\n"

        jobfound = False
        selectedjob = None
        currshift = None

        jobresource = None
        if self.infotype == "Resources":
            jobresource = self.getSelectedResource()
            currshift = self.currentshift
        else: # find job from order
            for job in self.getSelectedOrder().getMyJobs():
                if job.getName() == jobname:
                    selectedjob = job
            self.ShowJobStatus(selectedjob)
                    
                   
           
            
                

        return
###############################################################################################################################################
    def SetJobStarted(self,event):

        starttime = self.getShiftTime().value

        schmangr = self.getVisualManager().DataManager.getSchedulingManager()

        self.getPProgReport().value+=" resource value..."+str(self.getResDropDown().value)+"\n"
      
        resname = self.getResDropDown().value

        if resname in self.getVisualManager().DataManager.getResources():
            res = self.getVisualManager().DataManager.getResources()[resname]
            self.getPProgReport().value+=" Resource found.."+"\n"
            
            dayshifts = self.getVisualManager().DataManager.getSchedulingManager().getMyShifts()[starttime.date()]
            for shift in dayshifts:
                if (shift.getStartHour()<= starttime) and (shift.getEndHour()>=starttime):
                    start = math.ceil((starttime - shift.getStartHour()).total_seconds()/1800) # relative in half hours..
                    processtime = math.ceil(self.getCurrentJob().getQuantity()*self.getCurrentJob().getOperation().getProcessTime('min')) # in mins..
                    processinshift = min(processtime,(shift.getEndHour() - starttime).total_seconds()/60) # in mins..
                    
                    
                    self.getPProgReport().value+=" start "+str(start)+", "+"\n"
                    self.getPProgReport().value+=" current schedule? "+str(schmangr.getMyCurrentSchedule())+"\n"
                    self.getPProgReport().value+=" res in current schedule? "+str(resname in schmangr.getMyCurrentSchedule().getResourceSchedules())+"\n"
                    self.getPProgReport().value+=" shift in schedule? "+str(shift in schmangr.getMyCurrentSchedule().getResourceSchedules()[resname])+"\n"
                    for schjob,timetuple in schmangr.getMyCurrentSchedule().getResourceSchedules()[resname][shift].items():
                        self.getPProgReport().value+=" time tuple:  "+str(timetuple)+"\n"
                        if timetuple[1] < start-0.0001 or timetuple[0]+0.0001 > start+math.ceil(processinshift/30):
                            continue
                        self.getPProgReport().value+=" Resource is currently busy, cannot start now!!"+"\n"
                        return

            # in case the job is only planned, or released from a schedule, create the schedule-job.
            if self.getCurrentJob().getMySch() == None:
                self.getCurrentJob().initializeMySch()
            self.getCurrentJob().getMySch().setScheduledResource(res)
            self.getCurrentJob().getMySch().setActualStart(starttime)
            self.getPProgReport().value+=">>>>>>>>>>>>> "+str(starttime)+"\n"
            self.getPProgReport().value+=">>>>>>>>>>>>> "+str(type(starttime))+"\n"
        
               
            

            self.getPProgReport().value+=" Job "+str(self.getCurrentJob().getName())+" has started.."+"\n"
    
            self.getPProgReport().value+=">>>>>>>> val: "+str(self.getResDropDown().value)+"\n"
    
            self.getVisualManager().DataManager.getSchedulingManager().ExtendShifts(self.getCurrentJob().getMySch().getActualStart().date())
    
            
            dayshifts = self.getVisualManager().DataManager.getSchedulingManager().getMyShifts()[starttime.date()]
            self.getPProgReport().value+="day shifts "+str(len(dayshifts))+"\n"
    
            for shift in dayshifts:
                self.getPProgReport().value+=" "+str(type(shift.getStartHour()))+", "+str(type(starttime))+"\n"
                self.getPProgReport().value+=" strt hr: "+str(shift.getStartHour())+", end hr: "+str(shift.getEndHour())+", job strt: "+str(starttime)+"\n"
                self.getPProgReport().value+="strt hr <= job strt "+str((shift.getStartHour()<= starttime))+"\n"
                self.getPProgReport().value+="end hr >= job strt "+str((shift.getEndHour()>=starttime))+"\n"
                
                if (shift.getStartHour()<= starttime) and (shift.getEndHour()>=starttime):               
                    self.getPProgReport().value+=" Job "+str(self.getCurrentJob().getName())+" gets act startshift..."+shift.String("act strt: ")+"\n"
                    self.getCurrentJob().getMySch().setActualStartShift(shift)
                    self.getPProgReport().value+=shift.String(" Actual start shift: ")+"\n"
                    break
    
                 
            # update from current schedule..
            self.getPProgReport().value+=" updating schedule...job sch? "+str(self.getCurrentJob().getMySch())+"\n"
            self.getVisualManager().DataManager.getSchedulingManager().UpdateSchedule(self.getCurrentJob().getMySch())
            self.getPProgReport().value+=self.getCurrentJob().getMySch().getScheduledShift().String(" Scheduled start shift: ")+"\n"
            self.getPProgReport().value+=self.getCurrentJob().getMySch().getScheduledCompShift().String(" Scheduled comp shift: ")+"\n"
            self.getVisualManager().DataManager.SaveCurrentSchedule()
         
    
            self.getPProgReport().value+=" dayshifts: "+str(dayshifts)+"\n"
        
        
            self.ShowJobStatus(self.getCurrentJob())
        
        return

#############################################################################################################################################################
    def SetJobCompleted(self,event):

        completiontime = self.getShiftTime().value
        self.getCurrentJob().getMySch().setActualCompletion(completiontime)

        dayshifts = self.getVisualManager().DataManager.getSchedulingManager().getMyShifts()[completiontime.date()]

        for shift in dayshifts:
            if (shift.getStartHour()<= completiontime) and (shift.getEndHour()>=completiontime): 
                self.getCurrentJob().getMySch().setActualCompletionShift(shift)
                self.getPProgReport().value+=shift.String(" Actual completion shift: ")+"\n"
                self.getPProgReport().value+=" Actual start was: "+str(self.getCurrentJob().getMySch().getActualStart())+"\n"
                
        


        self.getJobCompleteBtn().layout.visibility  = 'hidden'
        self.getJobCompleteBtn().layout.display  = 'none'

        if self.getCurrentJob().getStatus() == "Completed": 
            self.getJobInfo5().value ="Started: "+str(self.getCurrentJob().getMySch().getActualStart())+", Completed: "+str(self.getCurrentJob().getMySch().getActualCompletion())
             
        self.getVisualManager().DataManager.getSchedulingManager().updateCompletedJob(self.getCurrentJob().getMySch())
        self.getVisualManager().DataManager.SaveCurrentSchedule()
    

        return

    def GenerateOrderJobs(self,event):

        self.getVisualManager().DataManager.getSchedulingManager().getPlanningManager().GenerateJobs(self.getSelectedOrder())

        self.getJobList().options = [job.getName() for job in self.getSelectedOrder().getMyJobs()]

        return 

########################################################################################################################################
    
    def generatePPrgTAB(self):
    


        self.setPProgReport(widgets.Textarea(value='', placeholder='',description='',disabled=True))
        self.getPProgReport().layout.height = '150px'
        self.getPProgReport().layout.width = '700px'
     

        self.setResShiftLbl(widgets.Label(value ='Shifts'))
        self.getResShiftLbl().add_class("red_label")


        self.setResShftJobsLbl(widgets.Label(value ='Jobs'))
        self.getResShftJobsLbl().add_class("red_label")
       
        self.setJobList(widgets.Select(options=[],desciption = ''))
      

        self.resshifts = widgets.Select(options=[],desciption = 'Shifts')
        self.resshifts.observe(self.ShowJobs)
        

        self.getJobList().layout.height='90%'
        self.getJobList().observe(self.ShowJobInfo)


        slider = widgets.IntSlider( value=0,min=0,max=100,step=5,description='',disabled=False,orientation='horizontal',readout=False)
        self.setProgressSlider(slider)

        myit = widgets.SelectionSlider(
            options=[str(x) for x in range(0,16)],
            description='Time:',
            orientation='horizontal',
            #
        )
        self.setShiftTime(myit)
        
        self.getShiftTime().layout.width = '400px'

        self.setResDropDown(widgets.Dropdown(options=[]))
        self.getResDropDown().observe(self.StartEnable)

 
      
        self.setJobInfo(widgets.Label(value =''))
        self.setJobInfo2(widgets.Label(value =''))
        self.setJobInfo3(widgets.Label(value =''))
        self.setJobInfo4(widgets.Label(value =''))
        self.setJobInfo5(widgets.Label(value =''))
        self.setShiftInfo(widgets.Label(value =''))
        
        


        self.setOrderInfo(widgets.Label(value =''))
        self.setOrderInfo2(widgets.Label(value =''))
        self.setOrderInfo3(widgets.Label(value =''))
        self.setOrderInfo4(widgets.Label(value =''))



     
  
        self.setJobStartBtn(widgets.Button(description = "Set Started",icon = 'fa-check-square'))
        self.getJobStartBtn().on_click(self.SetJobStarted)


        self.setJobGernerateButton(widgets.Button(description = "Generate Jobs",icon = 'fa-check-square'))
        self.getJobGernerateButton().on_click(self.GenerateOrderJobs)
        
        
        self.setJobCompleteBtn(widgets.Button(description = "SetCompleted",icon = 'fa-check-square'))
        self.getJobCompleteBtn().on_click(self.SetJobCompleted)

        self.resords = widgets.ToggleButtons(options=['Resources', 'Customer Orders','Active Jobs'],description='',disabled=False, button_style='')
        self.resords.index = 1   
        self.resords.observe(self.ShowDescriptives2)

     

        self.setResShifts(widgets.Dropdown(options=[]))
      
        self.getResShifts().observe(self.ShowResShift)
    
        self.setCustomerOrderList(widgets.Select(options=[],description = ''))
        self.getCustomerOrderList().options = ["..."]
        self.getCustomerOrderList().layout.width = "90%"
        self.getCustomerOrderList().layout.height = '170px'

        self.getCustomerOrderList().observe(self.ShowInformation)

        
        #self.getResourceList().observe(self.ShowResourceShift)
        
        schdes = widgets.Label(value ='Production Progress')
        schdes.add_class("red_label")
        #schdes.layout.width = "120px"

        start_date = datetime(2020, 2, 17)
        end_date = datetime(2020, 3, 27)
        dates = pd.date_range(start_date, end_date, freq='D')
        date = [(date.strftime(' %d %b %Y '), date) for date in dates]
        
        date_slider = widgets.SelectionSlider(options=date,orientation='horizontal',layout={'width': 'flex'})

       
      

        HTML('<style> .widget-text { width: auto; } </style>')


        self.setPPrgOrdOutput(widgets.Output())


       

        with self.getPPrgOrdOutput():
            clear_output()
          

        self.weekradio = widgets.RadioButtons( options=['Week'],description='',disabled=False)
        self.weekradio.observe(self.ShowShifts)


        self.setReslabel(widgets.Label(value='Resource: '))

        self.setShiftTimeLbl(widgets.Label(value=' '))
        self.getShiftTime().observe(self.ShowShiftTime)
        

       
        self.infotype = "Customer Orders"

        infobox = VBox( children = [self.getOrderInfo(),
                                                            self.getOrderInfo2(),
                                                            self.getOrderInfo3(),
                                                            self.getOrderInfo4()
                                                           ])
        infobox.layout.width = '49%'

        self.jobinfobox  = VBox( children = [self.getJobInfo(),
                                                            self.getJobInfo2(),
                                                            self.getProgressSlider(),
                                                            self.getJobInfo3(),
                                                            self.getJobInfo4(),
                                                            self.getJobInfo5(),
                                                            HBox(  children =[ 
                                                                               self.getReslabel(),
                                                                               self.getResDropDown()],
                                                                              layout =  widgets.Layout(height='50px')),
                                                           self.getShiftInfo(),
                                                           self.getShiftTime(),
                                                                             
                                                                              self.getJobStartBtn(),
                                                                               self.getJobCompleteBtn()
                                                           ])


        
        self.jobinfobox.layout.width='85%'

        self.orderbox = VBox(children =[self.getJobList(),self.getJobGernerateButton()])
        self.orderbox.layout.height='250px'
        self.orderbox.layout.width='25%'

        
        tab_sch = VBox( children = [
                                     self.resords,
                                     self.getCustomerOrderList(),
                            
                            
                            HBox(  children =[self.orderbox,self.weekradio,self.resshifts,self.jobinfobox
                                              ],layout = widgets.Layout(width = '95%',height='350px')),
            
                            self.getPPrgOrdOutput(),
                            self.getPProgReport()
                       ])              


        self.orderbox.layout.visibility = 'hidden'
        self.orderbox.layout.display = 'none'


        self.jobinfobox.layout.visibility = 'hidden'
        self.jobinfobox.layout.display = 'none'
        
  
    
        self.weekradio.layout.visibility = 'hidden'
        self.weekradio.layout.display = 'none'

        self.resshifts.layout.visibility = 'hidden'
        self.resshifts.layout.display = 'none'
        

        self.getResShifts().layout.visibility  = 'hidden'
        self.getResShifts().layout.display = 'none'
        
        self.getResShiftLbl().layout.visibility  = 'hidden'
        self.getResShiftLbl().layout.display = 'none'

       
        self.getJobList().layout.visibility  = 'hidden'
        self.getJobList().layout.display = 'none'

       
     
        self.getOrderInfo().layout.visibility  = 'hidden'
        self.getOrderInfo().layout.display = 'none'
        self.getOrderInfo2().layout.visibility  = 'hidden'
        self.getOrderInfo2().layout.display = 'none'
        self.getOrderInfo3().layout.visibility  = 'hidden'
        self.getOrderInfo3().layout.display = 'none'
        self.getOrderInfo4().layout.visibility  = 'hidden'
        self.getOrderInfo4().layout.display = 'none'
        




        tab_sch.layout.height = '750px'
          
        return tab_sch


   

#############################################################################################################################################  







#############################################################################################################################################   




 