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
        self.SelectedOrder = None

        self.ResShftJobsLbl = None
        self.JobList = None
        self.JobInfo = None
        self.JobInfo2 = None
        self.JobInfo3 = None  
        self.JobInfo4 = None
        self.JobInfo5 = None

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
        
      
        return

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


    def ShowInformation(self,event):

        if not 'index' in event['new']:
            return
            
        if event['new']['index'] < 0:
            return
            
    
        selected = self.getCustomerOrderList().options[event['new']['index']]


        self.getPProgReport().value+="Selected from list: "+str(selected)+" infotype: "+str(self.infotype)+"\n"

        if self.infotype == "Customer Orders":
            self.weekradio.layout.visibility = 'hidden'
            self.weekradio.layout.display = 'none'
            self.resshifts.layout.visibility = 'hidden'
            self.resshifts.layout.display = 'none'
        
            
        if self.infotype == "Resources":
            if self.getVisualManager().DataManager.getScheduleStartWeek() != None:
                stweek = self.getVisualManager().DataManager.getScheduleStartWeek()
                edweek = self.getVisualManager().DataManager.getScheduleEndWeek()

                for resname,res in self.getVisualManager().DataManager.getResources().items():
                    if resname == selected:
                        self.setSelectedResource(res)
                        self.getPProgReport().value+="Selected res: "+str(res.getName())+"\n"
                        break
                        

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
                self.resshifts.options = []
                
        
        
        return

    #def ShowWeekShifts(self,weekno):
        
        

    
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
                self.getJobList().selectedindex = 0

                self.getJobInfo().value ="PN: "+str(jobs[0].getJob().getOperation().getProduct().getPN())
                self.getJobInfo2().value ="Operation: "+str(jobs[0].getJob().getOperation().getName())
                self.getJobInfo3().value ="Quantity: "+str(jobs[0].getJob().getQuantity())
                self.getJobInfo4().value ="Start: "+str(jobs[0].getStartTime())
                self.getJobInfo5().value ="Product: "+str(jobs[0].getJob().getOperation().getProduct().getName())
                if jobs[0].getJob().getActualStart() == None:
                    self.getJobStartBtn().layout.visibility  = 'visible'
                    self.getJobCompleteBtn().layout.visibility  = 'hidden'
                else:
                    self.getJobStartBtn().layout.visibility  = 'hidden'
                    self.getJobCompleteBtn().layout.visibility  = 'visible'
               

                with self.getPPrgOrdOutput():
                    clear_output() 

                    
                    plt.style.use('ggplot')

                 
                    source = pd.DataFrame(columns=["Job","Start","End"])

                    for job in jobs:
                        self.getPProgReport().value+=str(shift.getStartHour())+"-"+str(job.getStartTime())+"-"+str(shift.getStartTime())+"\n"
                        starttime = shift.getStartHour()+timedelta(hours = max(job.getStartTime(),shift.getStartTime())-shift.getStartTime())
                        endtime =  shift.getStartHour()+timedelta(hours = min(job.getCompletionTime(),shift.getEndTime()+1)-shift.getStartTime())
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


        self.getPProgReport().value +="Selected: "+selected+", current info: "+str(self.infotype)+"\n"
      
        if selected == 'Resources':

            self.getPProgReport().value +="visibility: "+str(self.weekradio.layout.visibility)+"\n"
            if self.infotype != selected:
                self.weekradio.layout.visibility = 'hidden'
                self.weekradio.layout.display = 'none'
                self.resshifts.layout.visibility = 'hidden'
                self.resshifts.layout.display = 'none'
                self.getJobList().layout.visibility = 'hidden'
                self.getJobList().layout.display = 'none'
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

                self.getJobList().options = []
              
                self.infotype = selected
                self.getCustomerOrderList().options = [resname for resname in self.getVisualManager().DataManager.getResources().keys()]
                
            
        
        
        if selected == 'Customer Orders':

            self.getPProgReport().value +="visibility: "+str(self.weekradio.layout.visibility)+"\n"
            if self.infotype != selected:
                self.infotype = selected
                self.weekradio.layout.visibility = 'hidden'
                self.weekradio.layout.display = 'none'
                self.resshifts.layout.visibility = 'hidden'
                self.resshifts.layout.display = 'none'
                self.getJobList().layout.visibility = 'hidden'
                self.getJobList().layout.display = 'none'
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
                self.getJobList().options = []
                self.getCustomerOrderList().options = [ordname for ordname in self.getVisualManager().DataManager.getCustomerOrders().keys()] 
               
            
     
        

        self.getPProgReport().value +="final info: "+str(self.infotype)+"\n"
      
           
        with self.getPPrgOrdOutput():
            clear_output() 
        
        return
###################################################################################################################  

    def ShowShifts(self,event):


        weekstr = self.weekradio.value

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

        self.resshifts.options = [s for s in myshifts]

        self.getJobList().options = []
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
                self.getJobList().selectedindex = 0
              
                
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

      
    def ShowJobInfo(self,event):
        
        jobname = self.getJobList().value

        self.getJobStartBtn().layout.visibility  = 'hidden'
        self.getJobStartBtn().layout.display = 'none'
        self.getJobCompleteBtn().layout.visibility  = 'hidden'
        self.getJobCompleteBtn().layout.display = 'none'

        self.getPProgReport().value+="Selected  Job: "+str(jobname)+"\n"

        for job in self.getSelectedResource().getSchedule()[self.currentshift]:
            if job.getJob().getName() == jobname:
                
                self.getPProgReport().value+=" Job found.. "+str(jobname)+"\n"
                self.setCurrentJob(job.getJob())
                
                if  self.getJobInfo().layout.display == 'none':  
                    self.getJobInfo().layout.display = 'block'       
                    self.getJobInfo().layout.visibility  = 'visible'
                    self.getJobInfo2().layout.display = 'block'       
                    self.getJobInfo2().layout.visibility  = 'visible'
                    self.getJobInfo3().layout.display = 'block'       
                    self.getJobInfo3().layout.visibility  = 'visible'
                    self.getJobInfo4().layout.display = 'block'       
                    self.getJobInfo4().layout.visibility  = 'visible'
                    self.getJobInfo5().layout.display = 'block'       
                    self.getJobInfo5().layout.visibility  = 'visible'
                    

                
                starttime = self.currentshift.getStartHour()+timedelta(hours = max(job.getStartTime(),self.currentshift.getStartTime())-self.currentshift.getStartTime())

                cpshift = job.getScheduledCompShift()

                if self.currentshift == cpshift:
                    endtime =  cpshift.getStartHour()+timedelta(hours = min(job.getCompletionTime(),cpshift.getEndTime()+1)-cpshift.getStartTime())
                else:
                    endtime =  self.currentshift.getEndHour()

                
                
                schstr =" {:d}:{:02d}".format(starttime.hour, starttime.minute)+" - {:d}:{:02d}".format(endtime.hour, endtime.minute)

                if self.currentshift  != cpshift:
                    jendtime =  cpshift.getStartHour()+timedelta(hours = min(job.getCompletionTime(),cpshift.getEndTime()+1)-cpshift.getStartTime())
                    schstr = schstr+" ( {:d}-{:02d}-{:02d} / {:02d}:{:02d} )".format(jendtime.year,jendtime.month, jendtime.day,jendtime.hour,jendtime.minute)  
                  
                    
                self.getJobInfo().value ="PN: "+str(job.getJob().getOperation().getProduct().getPN())
                self.getJobInfo2().value ="Operation: "+str(job.getJob().getOperation().getName())
                self.getJobInfo3().value ="Quantity: "+str(job.getJob().getQuantity())
                self.getJobInfo4().value ="Scheduled: "+str(schstr)
                if job.getJob().getActualStart() == None:
                    self.getJobInfo5().value ="Status: Pending"
                    self.getJobStartBtn().layout.display = 'block'
                    self.getJobStartBtn().layout.visibility  = 'visible'
    
                else:
                    if job.getJob().getActualCompletion() == None:
                        self.getJobInfo5().value ="Status: Started "+str(job.getJob().getActualStart())
                        self.getJobCompleteBtn().layout.display = 'block'
                        self.getJobCompleteBtn().layout.visibility  = 'visible'
               
                    else:
                        self.getJobInfo5().value ="Status: Completed "+str(job.getJob().getActualCompletion())
                        
                self.getPProgReport().value+="done.. "+"\n"
                break
                

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
                        if j.getJob().getName() == selected:
                            self.setCurrentJob(j.getJob())
                            if j != None: 
                                self.getJobInfo().value ="PN: "+str(j.getJob().getOperation().getProduct().getPN())
                                self.getJobInfo2().value ="Operation: "+str(j.getJob().getOperation().getName())
                                self.getJobInfo3().value ="Quantity: "+str(j.getJob().getQuantity())
                                self.getJobInfo4().value ="Start: "+str(j.getStartTime())
                                self.getJobInfo5().value ="Product: "+str(j.getJob().getOperation().getProduct().getName())
                                if j.getJob().getActualStart() == None:
                                    self.getJobStartBtn().layout.visibility  = 'visible'
                                    self.getJobCompleteBtn().layout.visibility  = 'hidden'
                                else:
                                    self.getJobStartBtn().layout.visibility  = 'hidden'
                                    self.getJobCompleteBtn().layout.visibility  = 'visible'
        if self.getSelectedOrder() != None: 
            for j in self.getSelectedOrder().getMyJobs():
                
                if j.getName() == selected:
                    self.getPProgReport().value+="Selected found.. , Job: "+str(j.getName())+"\n"
                    self.setCurrentJob(j)
                    self.getJobInfo().value ="PN: "+str(j.getOperation().getProduct().getPN())
                    self.getJobInfo2().value ="Operation: "+str(j.getOperation().getName())
                    self.getJobInfo3().value ="Quantity: "+str(j.getQuantity())
                    self.getJobInfo5().value ="Product: "+str(j.getOperation().getProduct().getName())
                    if j.getMySch() != None: 
                        self.getJobInfo4().value ="Start: "+str(j.getMySch().getStartTime())
                    else:
                        self.getJobInfo4().value ="Start: - "
                       
                        if j.getActualStart() == None:
                            self.getJobStartBtn().layout.visibility  = 'visible'
                            self.getJobCompleteBtn().layout.visibility  = 'hidden'
                        else:
                            self.getJobStartBtn().layout.visibility  = 'hidden'
                            self.getJobCompleteBtn().layout.visibility  = 'visible'
                    
     
        return

    def SetJobStarted(self,event):

        self.getPProgReport().value+=" Job "+str(self.getCurrentJob().getName())+" has started.."+"\n"
        self.getCurrentJob().setActualStart(datetime.now())
       
        self.getJobStartBtn().layout.visibility  = 'hidden'
        self.getJobStartBtn().layout.display  = 'none'

        self.getJobCompleteBtn().layout.display  = 'block'
        self.getJobCompleteBtn().layout.visibility  = 'visible'

        
        return

    def SetJobCompleted(self,event):

        self.getCurrentJob().setActualCompletion(datetime.now())

        
        return




    
    def generatePPrgTAB(self):
    


        self.setPProgReport(widgets.Textarea(value='', placeholder='',description='',disabled=True))
        self.getPProgReport().layout.height = '150px'
        self.getPProgReport().layout.width = '700px'
     

        self.setResShiftLbl(widgets.Label(value ='Shifts'))
        self.getResShiftLbl().add_class("red_label")


        self.setResShftJobsLbl(widgets.Label(value ='Jobs'))
        self.getResShftJobsLbl().add_class("red_label")
       
        self.setJobList(widgets.Select(options=[],desciption = ''))
        self.getJobList().observe(self.SetJob)


        self.resshifts = widgets.Select(options=[],desciption = 'Shifts')
        self.resshifts.observe(self.ShowJobs)
        

        self.getJobList().layout.height = "90%"
        self.getJobList().options = ["Jobs.."]
        self.getJobList().observe(self.ShowJobInfo)
        
       
      
        self.setJobInfo(widgets.Label(value =''))
        self.setJobInfo2(widgets.Label(value =''))
        self.setJobInfo3(widgets.Label(value =''))
        self.setJobInfo4(widgets.Label(value =''))
        self.setJobInfo5(widgets.Label(value =''))
  
        self.setJobStartBtn(widgets.Button(description = "Set Started",icon = 'fa-check-square'))
        self.getJobStartBtn().on_click(self.SetJobStarted)
        
        
        self.setJobCompleteBtn(widgets.Button(description = "SetCompleted",icon = 'fa-check-square'))
        self.getJobCompleteBtn().on_click(self.SetJobCompleted)

        self.resords = widgets.ToggleButtons(options=['Resources', 'Customer Orders'],description='',disabled=False, button_style='', 
                                             # 'success', 'info', 'warning', 'danger' or ''

                                             #     icons=['check'] * 3
                                  )

        check1  =  widgets.Checkbox(value=False,description='Resources', disabled=False)
        check2  =  widgets.Checkbox(value=False,description='Customer Orders', disabled=False)

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

       
        self.infotype = "Customer Orders"

        tab_sch = VBox( children = [
                         self.resords,self.getCustomerOrderList(),
                        HBox(  children =[ self.weekradio,self.resshifts,self.getJobList(),
                                          VBox( children = [self.getJobInfo(),self.getJobInfo2(),self.getJobInfo3(),self.getJobInfo4(),self.getJobInfo5(),self.getJobStartBtn(),self.getJobCompleteBtn()])
                                         
                                         ],layout = widgets.Layout(width = '95%',height='200px')),
                             self.getPPrgOrdOutput(),
                               self.getPProgReport()
                       ])              


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

        self.getJobStartBtn().layout.visibility  = 'hidden'
        self.getJobStartBtn().layout.display = 'none'

        self.getJobCompleteBtn().layout.visibility  = 'hidden'
        self.getJobCompleteBtn().layout.display = 'none'

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
        




        tab_sch.layout.height = '670px'
          
        return tab_sch


   

#############################################################################################################################################  







#############################################################################################################################################   




 