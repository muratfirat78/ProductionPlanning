# -*- coding: utf-8 -*-

##### import ipywidgets as widgets
from IPython.display import clear_output
from IPython import display
from ipywidgets import *
from datetime import timedelta,date,datetime,time
import matplotlib.pyplot as plt
import warnings
import seaborn as sns
import os
import pandas as pd
import warnings
import sys
import numpy as np
import math as mth
from PlanningObjects import *
from Visual import *
from Data import *


#######################################################################################################################


        
class SchedulingManager:
    def __init__(self): 

        self.DataManager = None
        self.VisualManager = None
        self.PlanningManager = None
        self.JobsCreated = False
        self.weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.SHStart = None
        self.SHEnd = None
        self.CurrentJobID = 0


    def getJobID(self):
        self.CurrentJobID+=1
        return self.CurrentJobID

    def resetJobID(self):
        self.CurrentJobID = 0
        return 


    def setSHStart(self,myitm):
        self.SHStart = myitm 
        return

    def getSHStart(self):
        return self.SHStart

    def setSHEnd(self,myitm):
        self.SHEnd = myitm 
        return

    def getSHEnd(self):
        return self.SHEnd


    def isJobCreated(self):
        return self.JobsCreated

    def setJobCreated(self):
        self.JobsCreated = True
        return  

    def setDataManager(self,DataMgr):
        self.DataManager = DataMgr 
        return

    def getDataManager(self):
        return self.DataManager


    def setPlanningManager(self,MyMgr):
        self.PlanningManager = MyMgr 
        return

    def getPlanningManager(self):
        return self.PlanningManager


    def setVisualManager(self,VMgr):
        self.VisualManager = VMgr 
        return

    def getVisualManager(self):
        return self.VisualManager

    def MakeSchedule(self,b):
        '''
        -	Class shift: (myday,number (1 or 2))
        -	Schedule: dict(key: shift, val: [(job,starttime)])  , this will be added to class resource as variable like myschedule. 
        -	Pseudocode of scheduling heuristic: 
            Initialize shifts for the scheduling period and link shifts with precedence relations Day1-Shift1->Day1-Shift2->Day2-Shift1….
            Initialize SchedulableJobs as jobs with no predecessor
            Initialize Schedules of all resources with created shifts

             While len(SchedulableJobs) > 0:
                   For job j in SchedulableJobs:
                        ES_j = max(maxpredecessor completion, 0) 
                        Check compatible and alternative resources that can process the job j and find the available 
                                                            earliest start time that is not smaller than ES_j.
                        Schedule job j to the resource where it can be processed with earliest start time. 
                     For successor s in Successors list of job j: 
                           If all predecessors of s is scheduled (possibly has other predecessors): 
                                Add s to SchedulableJobs. 

        '''

        psstart = self.getSHStart()

        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="Scheduling starts..."+"\n"
       

        ScheduleWeeks = ((self.getSHEnd()-self.getSHStart()).days)//7 # weeks

        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="ScheduleWeeks..."+str(ScheduleWeeks)+"\n"
       
        
        pssend= self.getSHEnd()

        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="Scheduling period..."+str(psstart)+"-"+str(pssend)+"\n"

     

        oprdict = dict()
        nrjobs = 0

        #Determine customer orders with latest start within Scheduling
        SelectedOrders=[]
        for name,order in self.getDataManager().getCustomerOrders().items():
            if not order.getLatestStart() is None:
                if order.getLatestStart().date() <= pssend:
                    nrjobs+=len(order.getMyJobs())
                    for job in order.getMyJobs():
                        if not job.getOperation() in oprdict:
                            oprdict[job.getOperation()] = []
                        oprdict[job.getOperation()].append(job)
                        
                    SelectedOrders.append(order)
                
        #self.CreateJobs(psstart,ScheduleWeeks,SelectedOrders)

        

        for resname,res in self.getDataManager().getResources().items():
            res.getSchedule().clear()

        #nrjobs,oprdict = self.DefineJobPrecedences(SelectedOrders)
           
        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" To schedule jobs: "+str(nrjobs)+"\n"

      
         #Initialize shifts (example 30 days?)
        scheduldays = 7*ScheduleWeeks;
   
        #for scheduleday in pd.date_range(psstart,pssend):
            #self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="Schedule day"+str(scheduleday)+", "+str(self.weekdays[scheduleday.weekday()])+"\n"
        

        #Initialize Schedulable Jobs
     
        SchedulableJobs= [] 

        # Fill the Schedulable Jobs List
        for opr, jobs in oprdict.items():
            for job in jobs:
                if job.IsSchedulable():
                    SchedulableJobs.append(job)

        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="SchedulableJobs: m"+str(len(SchedulableJobs))+"\n"
              
        i=1
        prev_dayshift = None 
        scheduletimehour = 1
        while i <= scheduldays:
            
            shift1=Shift(i,1,8,prev_dayshift)
            shift1.setStartTime(scheduletimehour)            
            scheduletimehour+=8
            shift1.setEndTime(scheduletimehour-1)
            shift2=Shift(i,2,7,shift1)
            shift2.setStartTime(scheduletimehour)                     
            scheduletimehour+=8
            shift2.setEndTime(scheduletimehour-1)
            shift3=Shift(i,3,8,shift2)
            shift3.setStartTime(scheduletimehour)
            scheduletimehour+=8
            shift3.setEndTime(scheduletimehour-1)
            prev_dayshift=shift3

            opno = 0
            for resname, res in self.getDataManager().getResources().items():

                if res.getType() == "Machine":
                    res.getShiftAvailability()[shift1] = True
                    res.getSchedule()[shift1] = []
                    res.getShiftAvailability()[shift2] = True
                    res.getSchedule()[shift2] = []
                    res.getShiftAvailability()[shift3] = not ((res.getAutomated() is None) or (res.getAutomated()==False))

                    if res.getShiftAvailability()[shift3]:
                        res.getSchedule()[shift3] = []
                    

                if res.getType() == "Manual":
                    res.getShiftAvailability()[shift1] = True
                    res.getSchedule()[shift1] = []
                    res.getShiftAvailability()[shift2] = True
                    res.getSchedule()[shift2] = []
                    res.getShiftAvailability()[shift3] = False
                    
                if res.getType() == "Operator":
                    res.getShiftAvailability()[shift3] = False

                    if opno < 2:
                        res.getShiftAvailability()[shift1] = True
                        res.getSchedule()[shift1] = []
                        res.getShiftAvailability()[shift2] = False
                        opno += 1
                    elif opno == 3:
                        if i ==1:
                            repshift = shift2
                            repshift.setPrevious(None)
                        res.getShiftAvailability()[shift1] = False
                        res.getShiftAvailability()[repshift] = True
                        res.getSchedule()[shift2] = []
                    else:
                        res.getShiftAvailability()[shift1] = True
                        res.getSchedule()[shift1] = []
                        res.getShiftAvailability()[shift2] = True
                        res.getSchedule()[shift2] = []
                   
                if res.getType() == "Outsourced":
                    res.getShiftAvailability()[shift1] = True
                    res.getSchedule()[shift1] = []
                    res.getShiftAvailability()[shift2] = True
                    res.getSchedule()[shift2] = []
                    res.getShiftAvailability()[shift3] = True
                    res.getSchedule()[shift3] = []
                if res.getName() != 'Operator 3':
                    res.InitializeEmptySlot()
                
                    
                
                # for slot in res.getEmptySlots():
                #     self.getVisualManager().getSchedulingTab().getPSchScheRes().value+= res.getName()+str(slot[0][0])+","+slot[0][1]+"\n"  
                    
            i+=1        
                    
     
        #Create Schedule; we start by checking if there are still jobs that can be scheduled   
        allscheduled = 0
        
        while len(SchedulableJobs) >0:
            ScheduledJobs = []
            JobsToRemove = []
            nrscheduled = 0
            for j in SchedulableJobs:
                self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Scheduling job "+str(j.getName())+"\n"  
                myresource = None
                for resource in j.getOperation().getRequiredResources():
                    myresource = resource
                    if isinstance(resource,list):
                        myresource = resource[0]
                    break
                if myresource == None: 
                    self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Op: "+str(j.getOperation().getName())+" has no resource.."+"\n"
                    JobsToRemove.append(j)
                    continue
                schreturn = myresource.CheckSlot(j)
                if schreturn == None: 
                    self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=str(j.getName())+" cannot be scheduled in "+resource.getName()+"\n"
                    JobsToRemove.append(j)
                    continue
                else: 
                    nrscheduled+=1
                    allscheduled+=1
                    slot,scheinfo = schreturn  
                    jobstarttime, unusedtime = scheinfo                    
                    myresource.ScheduleJob(j,jobstarttime,unusedtime,slot)
                    self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=str(j.getName())+"scheduled "+resource.getName()+", st "+str(jobstarttime)+".. "+"\n"
                    self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=str(j.getName())+"scheduled completion time "+str(j.getCompletionTime())+", st "+str(jobstarttime)+".. "+"\n"
                    ScheduledJobs.append(j)
                    if j.getSuccessor() != None and j.getSuccessor().IsSchedulable():
                        SchedulableJobs.append(j.getSuccessor())
            for j in ScheduledJobs:
                SchedulableJobs.remove(j)
            for j in JobsToRemove:
                SchedulableJobs.remove(j)

            if nrscheduled == 0:
                break # no job can be scheduled anymore.. 

        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Scheduled: "+str(allscheduled)+" of the total of "+str(nrjobs)+"\n"
        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Checking completed orders..."+"\n"

        Orderstatus = []
        for order in SelectedOrders:
            self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=str(order.getName())+": "+str(order.getStatus())+"\n"
            Orderstatus.append(str(order.getName())+": "+str(order.getStatus()))
        #myops =  [i.getName() for i in oprdict.keys()]
        #myres = [i for i in self.getDataManager().getResources().keys()]
        #self.getVisualManager().getSchedulingTab().getPSchOperations().options = myops
        self.getVisualManager().getSchedulingTab().getPSchOrderlist().options = Orderstatus
        #self.getVisualManager().getSchedulingTab().getPSchResources().options = myres
            

        Schedule_df = pd.DataFrame(columns = ["Resource Name","Day","Shift","Job","OperationName","Start in Shift","Completion in Shift"])
        folder = 'UseCases'; casename = "TBRM_Volledige_Instantie"
        path = folder+"\\"+casename
        isExist = os.path.exists(path)
        
        if not isExist:
            os.makedirs(path)
        
        for name,myres in self.getDataManager().getResources().items():
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
                    
        filename = 'Schedules.csv'; path = folder+"\\"+casename+"\\"+filename;fullpath = os.path.join(Path.cwd(), path)
        Schedule_df.to_csv(fullpath, index=False)                
        
        
            
        
                    
                       
                
        return 

        
       
      
        

    

  
