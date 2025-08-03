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
        day = 7*ScheduleWeeks;
        
        i=1;
        shiftlistman=[]
        shiftlistaut=[]

        

        #for scheduleday in pd.date_range(psstart,pssend):
            #self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="Schedule day"+str(scheduleday)+", "+str(self.weekdays[scheduleday.weekday()])+"\n"
        while i <= day+1:
            shift1 = Shift(i,1,8)
            shiftlistman.append(shift1)
            shiftlistaut.append(shift1)
            shift2=Shift(i,2,7)
            shiftlistman.append(shift2)
            shiftlistaut.append(shift2)
            shift3=Shift(i,3,8)
            shiftlistaut.append(shift3)
            i+=1
    
        
        
        #Initialize Schedulable Jobs
     
        SchedulableJobs= [] 
        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="TEST"+str(SchedulableJobs)+"\n"
        ScheduledJobs = dict() #key:Jobname, val: Job object

        # Fill the Schedulable Jobs List
        for opr, jobs in oprdict.items():
            for job in jobs:
                if len(job.getPredecessors()) == 0:
                    SchedulableJobs.append(job)


        # self.Schedule = dict()  #key: day, val: [(shift,[jobs])]
               
        counter = 0       
        #Initialize schedule for each Resource:
        while i <= day+1:
            shift1 = Shift(i,1,8)
            shift2=Shift(i,2,7)
            shift3=Shift(i,3,8)

            opno = 0
            for resname, res in self.getDataManager().getResources().items():

                if res.getType() == "Machine":
                    res.getSchedule()[i] = []
                    res.getSchedule()[i].append((shift1,[]))
                    res.getSchedule()[i].append((shift2,[]))
                    if not ((res.getAutomated() is None) or (res.getAutomated()==False)):
                        res.getSchedule()[i].append((shift3,[]))
                if res.getType() == "Manual":
                    res.getSchedule()[i] = []
                    res.getSchedule()[i].append((shift1,[]))
                    res.getSchedule()[i].append((shift2,[]))
                if res.getType() == "Operator":
                    res.getSchedule()[i] = []

                    if opno < 2:
                        res.getSchedule()[i].append((shift1,[]))
                        opno += 1
                    else:
                        res.getSchedule()[i].append((shift2,[]))
                if res.getType() == "Outsourced":
                    res.getSchedule()[i] = []
                    res.getSchedule()[i].append((shift1,[]))
                    res.getSchedule()[i].append((shift2,[]))
                    res.getSchedule()[i].append((shift3,[]))    
                        
                        
     
        #Create Schedule; we start by checking if there are still jobs that can be scheduled   
        while len(SchedulableJobs) >0:
            for j in SchedulableJobs:
                self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Scheduling job "+str(j.getName())+"\n"               
                predecessorjobs = j.getPredecessors()
                successorjobs = j.getSuccessor()
                Quantity = j.getQuantity()
                PartialJob = False #Partial Job False is an indicator to check if a job could be completely scheduled during the shift
                EarliestStart = [1,1,0] # Initialize the earliest start [day,shift,starttime(i.e. completiontime of latest job)]
                if not (predecessorjobs ==[]):
                #Determine Earliest starttime if there are predecessor jobs
                    maxpredecessor = [None,None,None]
                    for i in predecessorjobs:
                        predecessor = [ScheduledJobs[i.getName()].getScheduledDay(),ScheduledJobs[i.getName()].getScheduledShift(),ScheduledJobs[i.getName()].getStartTime() + (i.getQuantity() * self.getDataManager().getOperations()[i.getOperation().getName()].getProcessTime())]
                        if maxpredecessor == [None,None,None]
                            maxpredecessor = predecessor
                        if (predecessor[0] > maxpredecessor[0]) or (predecessor[0] == maxpredecessor[0] and predecessor[1] > maxpredecessor[1]) or (predecessor[0] == maxpredecessor[0] and predecessor[1] == maxpredecessor[1] and predecessor[2] > maxpredecessor[2] ):
                            maxpredecessor = predecessor
                    EarliestStart = maxpredecessor
                    
                #Determine earliest available resource
                processtime = (j.getQuantity() * self.getDataManager().getOperations()[j.getOperation().getName()].getProcessTime())
                resources = j.getOperation().getRequiredResources()
                for r in resources:
                    ##Here we implement first available resources when we have alternative machines implemented...
                    
                    Automated = r.getAutomated()
                    opef = r.getOperatingEffort()
                    
                    restype = r.getType()
                    
                    if restype == 'Manual':
                        schedulableShift = [] #Here we track if we can schedule the job in the available shifts [day,shift]
                        completiontimeLatestJob = None
                        

                        while schedulableShift == []: #Here we find the [day,shift] for when we can schedule the job 
                            for daynum, shiftjob in r.getSchedule().items():
                                #Check which is the earliest shift that we are allowed to schedule
                                
                                if (daynum < EarliestStart[0]):
                                    continue
                                if daynum >= EarliestStart[0]:
                                    for shift in shiftjob:
                                        if shift[0].getNumber() < EarliestStart[1]:
                                            continue
                                        if shift[0].getNumber() == EarliestStart[1]: #Check if latest job ends before the end of the shift
                                            if shift[1][-1].getStartTime() + (shift[1][-1].getQuantity()*self.getDataManager().getOperations()[shift[1][-1].getOperation().getName()].getProcessTime()) >= shift[0].getCapacity():
                                                continue
                                            else:
                                                schedulableShift = [daynum,shift]
                                                completiontimeLatestJob = shift[1][-1].getStartTime() + (shift[1][-1].getQuantity()*self.getDataManager().getOperations()[shift[1][-1].getOperation().getName()].getProcessTime())
                                                break
                                    if schedulableShift != []:
                                        break
                            if schedulableShift == []:
                                self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Job "+str(j.getName())+" cannot be scheduled on resource "+str(r.getName())+" Within the scheduling horizon of "+ str(day)+" days. \n"

    
                        shiftday = schedulableShift[0]        
                        shiftcap = schedulableShift[1].getCapacity()
                        shiftnumber = schedulableShift[1].getNumber()

                        
                        if shiftnumber == 1:
                            effort = 0                                                                   
                            SchedWorker = self.getDataManager().getResources()['Manual workers'].getSchedule();
                            for mach in SchedWorker[shift]:                                
                                effort += mach[1].getOperatingEffort()*(mach[0].getOperation().getProcessTime()*mach[2])                                  
                            
                            if shiftcap > (completiontimeLatestJob) and (effort <24): #This means we can schedule (partially) in first shift
                                j.setStartTime(completiontimeLatestJob)
                                if (completiontimeLatestJob + processtime) > 8:
                                    PartialJob = True
                                    fraction = 8 - completiontimeLatestJob
                                    ProcessedQuantity = fraction/self.getDataManager().getOperations()[j.getOperation().getName()].getProcessTime()
                                    Quantity = Quantity - ProcessedQuantity
                                    
                                    processtime = (Quantity * self.getDataManager().getOperations()[j.getOperation().getName()].getProcessTime())
                                    r.getSchedule()[shift].append((j,completiontimeLatestJob,ProcessedQuantity))
                                    self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Partially scheduled "+str(j.getName())+" on resource "+str(r.getName())+" During shift "+str(shift.getNumber())+" On day "+str(shift.getDay())+"\n"+"Quantity remaining: "+str(Quantity)+"\n"
                                    continue
                                else:
                                    ProcessedQuantity = Quantity
                                    r.getSchedule()[shift].append((j,completiontimeLatestJob,ProcessedQuantity))
                                    j.setScheduledShift(shiftnumber)
                                    j.setScheduledDay(shift.getDay())
                                    ScheduledJobs[j.getName()] = j
                                    self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Completely scheduled "+str(j.getName())+" on resource "+str(r.getName())+" During shift "+str(shift.getNumber())+" On day "+str(shift.getDay())+"\n"
                                    SchedulableJobs.remove(j) #Remove scheduled job
                                    
                                
                                SchedWorker[shift].append([j,r,ProcessedQuantity])                                    
                                                                
                                
                                ## check if successor can be scheduled.
                                for sucjob in successorjobs:
                                    Schedulable = True
                                    for predjbs in sucjob.getPredecessors():
                                        if predjbs in ScheduledJobs:
                                            continue
                                        else:
                                            Schedulable = False;
                                    if Schedulable == True:
                                        if sucjob not in ScheduledJobs:
                                            SchedulableJobs.append(sucjob)
                                
                                
                                
                                
                                break
                            else:
                                continue
        
                        if shiftnumber == 2:
                            effort = 0                                                                   
                            SchedWorker = self.getDataManager().getResources()['Manual workers'].getSchedule();
                            for mach in SchedWorker[shift]:                                
                                effort += mach[1].getOperatingEffort()*(mach[0].getOperation().getProcessTime()*mach[2])                                  
        
                            if shiftcap > (completiontimeLatestJob) and (effort <21): #This means we can schedule (partially) in first shift
                                j.setStartTime(completiontimeLatestJob)
                                if (completiontimeLatestJob + processtime) > 7:
                                    PartialJob = True
                                    fraction = 7 - completiontimeLatestJob
                                    ProcessedQuantity = fraction/self.getDataManager().getOperations()[j.getOperation().getName()].getProcessTime()
                                    Quantity = Quantity - ProcessedQuantity
                                    processtime = (Quantity * self.getDataManager().getOperations()[j.getOperation().getName()].getProcessTime())
                                    r.getSchedule()[shift].append((j,completiontimeLatestJob,ProcessedQuantity))
                                    self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Partially scheduled "+str(j.getName())+" on resource "+str(r.getName())+" During shift "+str(shift.getNumber())+" On day "+str(shift.getDay())+"\n"+"Quantity remaining: "+str(Quantity)+"\n"
                                    continue
                                else:
                                    ProcessedQuantity = Quantity
                                    r.getSchedule()[shift].append((j,completiontimeLatestJob,ProcessedQuantity))
                                    j.setScheduledShift(shiftnumber)
                                    j.setScheduledDay(shift.getDay())
                                    ScheduledJobs[j.getName()] = j
                                    self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Completely scheduled "+str(j.getName())+" on resource "+str(r.getName())+" During shift "+str(shift.getNumber())+" On day "+str(shift.getDay())+"\n"
                                    SchedulableJobs.remove(j) #Remove scheduled job
                                
                                
                                SchedWorker[shift].append([j,r,ProcessedQuantity])                                    
                                                                
                                
                                ## check if successor can be scheduled.
                                for sucjob in successorjobs:
                                    Schedulable = True
                                    for predjbs in sucjob.getPredecessors():
                                        if predjbs in ScheduledJobs:
                                            continue
                                        else:
                                            Schedulable = False;
                                    if Schedulable == True:
                                        if sucjob not in ScheduledJobs:
                                            SchedulableJobs.append(sucjob)
                                                                                                        
                                
                                break
                            else:
                                continue
                                                                                                               
                        
                        break
                    elif restype == 'Outsourced':
                        for shift, jobtime in r.getSchedule().items():
                            #Check which is the earliest shift that we are allowed to schedule
                            if (shift.getDay() < EarliestDay) or (shift.getDay() == EarliestDay and shift.getNumber() < EarliestShift):
                                continue
                            ##Here we now have the completion time of the last job in a shift. Check if the to job to schedule fits in the shift. Else check next shift.
                            
                            if (shift.getDay() == EarliestDay and shift.getNumber() == EarliestShift):
                                completiontimeLatestJob = EarliestStart #find the shift and 
                            elif (shift.getDay() == EarliestDay and shift.getNumber() > EarliestShift) or shift.getDay()>EarliestDay:
                                completiontimeLatestJob = 0
                            else:
                                continue
                            
                            shiftcap = shift.getCapacity()
                            shiftnumber = shift.getNumber()

                            if shift.getDay() > day:
                                self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Job "+str(j.getName())+" cannot be scheduled on resource "+str(r.getName())+" Within the scheduling horizon of "+ str(day)+" days. \n"
                                SchedulableJobs.remove(j) #Remove scheduled job
                                break
                            
                            if shiftnumber == 1:
                                time = 8
                            else:
                                time = 7
                                
                            if shiftcap > (completiontimeLatestJob): #This means we can schedule (partially) in first shift
                                j.setStartTime(completiontimeLatestJob)
                                if (completiontimeLatestJob + processtime) > time:
                                    PartialJob = True
                                    fraction = 8 - completiontimeLatestJob
                                    processtime = processtime - time
                                    r.getSchedule()[shift].append((j,completiontimeLatestJob,'-'))
                                    self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Partially scheduled "+str(j.getName())+" on resource "+str(r.getName())+" During shift "+str(shift.getNumber())+" On day "+str(shift.getDay())+"\n"+"Quantity remaining: "+str(Quantity)+"\n"
                                    continue
                                else:
                                    ProcessedQuantity = Quantity
                                    r.getSchedule()[shift].append((j,completiontimeLatestJob,'-'))
                                    j.setScheduledShift(shiftnumber)
                                    j.setScheduledDay(shift.getDay())
                                    ScheduledJobs[j.getName()] = j
                                    self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Completely scheduled "+str(j.getName())+" on resource "+str(r.getName())+" During shift "+str(shift.getNumber())+" On day "+str(shift.getDay())+"\n"
                                    SchedulableJobs.remove(j) #Remove scheduled job
                                
                                
                                                                  
                                                                
                                
                                ## check if successor can be scheduled.
                                for sucjob in successorjobs:
                                    Schedulable = True
                                    for predjbs in sucjob.getPredecessors():
                                        if predjbs in ScheduledJobs:
                                            continue
                                        else:
                                            Schedulable = False;
                                    if Schedulable == True:
                                        if sucjob not in ScheduledJobs:
                                                SchedulableJobs.append(sucjob)
                                
                                
                                
                                
                                break
                            else:
                                continue
            
                                                                                                                                          
                        
                        break
                    else:
                        for shift, jobtime in r.getSchedule().items():
                            
                            #Check which is the earliest shift that we are allowed to schedule
                            if (shift.getDay() < EarliestDay) or (shift.getDay() == EarliestDay and shift.getNumber() < EarliestShift):
                                continue
                            ##Here we now have the completion time of the last job in a shift. Check if the to job to schedule fits in the shift. Else check next shift.
                            if jobtime ==[]:
                                completiontimeLatestJob = 0;
                            else:
                                completiontimeLatestJob = jobtime[::-1][0][1] + (jobtime[::-1][0][0].getQuantity() * self.getDataManager().getOperations()[jobtime[::-1][0][0].getOperation().getName()].getProcessTime())
                            if (shift.getDay() == EarliestDay and shift.getNumber() == EarliestShift):
                                completiontimeLatestJob = max(completiontimeLatestJob,EarliestStart); #if in earliest shift/day
                            else:
                                completiontimeLatestJob = completiontimeLatestJob;
                            
                            shiftcap = shift.getCapacity()
                            shiftnumber = shift.getNumber()

                            if shift.getDay() > day:
                                self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Job "+str(j.getName())+" cannot be scheduled on resource "+str(r.getName())+" Within the scheduling horizon of "+ str(day)+" days. \n"
                                SchedulableJobs.remove(j) #Remove scheduled job
                                break
                            
                            if shiftnumber == 1:
                                effort = 0                                                                                         
                                CurOpeffOp1 = 0; ## Also check operator availability.
                                SchedOp1 = self.getDataManager().getResources()['Operator 1'].getSchedule();
                                CurOpeffOp2 = 0;
                                SchedOp2 = self.getDataManager().getResources()['Operator 2'].getSchedule();
                                for mach in SchedOp1[shift]:                                
                                    CurOpeffOp1 += mach[1].getOperatingEffort()*(mach[0].getOperation().getProcessTime()*mach[2])
                                for mach in SchedOp2[shift]:                                
                                    CurOpeffOp2 += mach[1].getOperatingEffort()*(mach[0].getOperation().getProcessTime()*mach[2])
                                effort = min(CurOpeffOp1,CurOpeffOp2)   
            
                                if shiftcap > (completiontimeLatestJob) and (effort <8): #This means we can schedule (partially) in first shift
                                    j.setStartTime(completiontimeLatestJob)
                                    if (completiontimeLatestJob + processtime) > 8:
                                        PartialJob = True
                                        fraction = 8 - completiontimeLatestJob
                                        ProcessedQuantity = fraction/self.getDataManager().getOperations()[j.getOperation().getName()].getProcessTime()
                                        
                                        
                                        Quantity = Quantity - ProcessedQuantity
                                        
                                        processtime = (Quantity * self.getDataManager().getOperations()[j.getOperation().getName()].getProcessTime())
                                        r.getSchedule()[shift].append((j,completiontimeLatestJob,ProcessedQuantity))
                                        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Partially scheduled "+str(j.getName())+" on resource "+str(r.getName())+" During shift "+str(shift.getNumber())+" On day "+str(shift.getDay())+"\n"+"Quantity remaining: "+str(Quantity)+"\n"
                                        continue
                                    else:
                                        ProcessedQuantity = Quantity
                                        r.getSchedule()[shift].append((j,completiontimeLatestJob,ProcessedQuantity))
                                        j.setScheduledShift(shiftnumber)
                                        j.setScheduledDay(shift.getDay())
                                        ScheduledJobs[j.getName()] = j
                                        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Completely scheduled "+str(j.getName())+" on resource "+str(r.getName())+" During shift "+str(shift.getNumber())+" On day "+str(shift.getDay())+"\n"
                                        SchedulableJobs.remove(j) #Remove scheduled job
                                    
                                    if (CurOpeffOp1 +opef <= 1):
                                       SchedOp1[shift].append([j,r,ProcessedQuantity])
                                    else:
                                        SchedOp2[shift].append([j,r,ProcessedQuantity])
                                                                    
                                    
                                    ## check if successor can be scheduled.
                                    for sucjob in successorjobs:
                                        Schedulable = True
                                        for predjbs in sucjob.getPredecessors():
                                            if predjbs in ScheduledJobs:
                                                continue
                                            else:
                                                Schedulable = False;
                                        if Schedulable == True:
                                            if sucjob not in ScheduledJobs:
                                                SchedulableJobs.append(sucjob)
                                    
                                    
                                    
                                    
                                    break
                                else:
                                    continue
            
                            if shiftnumber == 2:
                                CurOpeffOp3 = 0; ## Also check operator availability.
                                SchedOp3 = self.getDataManager().getResources()['Operator 3'].getSchedule();
                                
                                for mach in SchedOp3[shift]:                                
                                    CurOpeffOp3 += mach[1].getOperatingEffort()*(mach[0].getOperation().getProcessTime()*mach[2])
                                
                                if shiftcap > (completiontimeLatestJob) and (CurOpeffOp3 + opef<7): #This means we can schedule in second shift
                                    j.setStartTime(completiontimeLatestJob)
                                    if (completiontimeLatestJob + processtime) > 7:
                                        PartialJob = True
                                        fraction = 7 - completiontimeLatestJob
                                        ProcessedQuantity = fraction/self.getDataManager().getOperations()[j.getOperation().getName()].getProcessTime()
                                        Quantity = Quantity - ProcessedQuantity
                                        processtime = (Quantity * self.getDataManager().getOperations()[j.getOperation().getName()].getProcessTime())
                                        r.getSchedule()[shift].append((j,completiontimeLatestJob,ProcessedQuantity))
                                        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Partially scheduled "+str(j.getName())+" on resource "+str(r.getName())+" During shift "+str(shift.getNumber())+" On day "+str(shift.getDay())+"\n"+"Quantity remaining: "+str(Quantity)+"\n"
                                        continue
                                    else:
                                        ProcessedQuantity = Quantity
                                        r.getSchedule()[shift].append((j,completiontimeLatestJob,ProcessedQuantity))
                                        j.setScheduledShift(shiftnumber)
                                        j.setScheduledDay(shift.getDay())
                                        ScheduledJobs[j.getName()] = j
                                        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Completely scheduled "+str(j.getName())+" on resource "+str(r.getName())+" During shift "+str(shift.getNumber())+" On day "+str(shift.getDay())+"\n"
                                        SchedulableJobs.remove(j) #Remove scheduled job
                                        
                                    SchedOp3[shift].append([j,r,ProcessedQuantity])                                
                                    
                                    ## check if successors can be scheduled.
                                    for sucjob in successorjobs:
                                        Schedulable = True
                                        for predjbs in sucjob.getPredecessors():
                                            if predjbs in ScheduledJobs:
                                                continue
                                            else:
                                                Schedulable = False;
                                        if Schedulable == True:
                                            if sucjob not in ScheduledJobs:
                                                SchedulableJobs.append(sucjob)
                                    
                                    
                                    
                                    break
                                else:
                                    continue
                            if shiftnumber == 3 and PartialJob == True:                          
                                                           
                                
                                j.setStartTime(completiontimeLatestJob)
                                if (completiontimeLatestJob + processtime) > 8:
                                    PartialJob = True
                                    fraction = 8 - completiontimeLatestJob
                                    ProcessedQuantity = fraction/self.getDataManager().getOperations()[j.getOperation().getName()].getProcessTime()
                                    Quantity = Quantity - ProcessedQuantity
                                    processtime = (Quantity * self.getDataManager().getOperations()[j.getOperation().getName()].getProcessTime())
                                    r.getSchedule()[shift].append((j,completiontimeLatestJob,ProcessedQuantity))
                                    self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Partially scheduled "+str(j.getName())+" on resource "+str(r.getName())+" During shift "+str(shift.getNumber())+" On day "+str(shift.getDay())+"\n"+"Quantity remaining: "+str(Quantity)+"\n"
                                    
                                else:
                                    ProcessedQuantity = Quantity
                                    r.getSchedule()[shift].append((j,completiontimeLatestJob,ProcessedQuantity))
                                    j.setScheduledShift(shiftnumber)
                                    j.setScheduledDay(shift.getDay())
                                    ScheduledJobs[j.getName()] = j
                                    self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Completely scheduled "+str(j.getName())+" on resource "+str(r.getName())+" During shift "+str(shift.getNumber())+" On day "+str(shift.getDay())+"\n"
                                    SchedulableJobs.remove(j) #Remove scheduled job
                                
                                
                                
                                ## check if successors can be scheduled.
                                for sucjob in successorjobs:
                                    Schedulable = True
                                    for predjbs in sucjob.getPredecessors():
                                        if predjbs in ScheduledJobs:
                                            continue
                                        else:
                                            Schedulable = False;
                                    if Schedulable == True:
                                        if sucjob not in ScheduledJobs:
                                                SchedulableJobs.append(sucjob)                           
                                
                                
                                break
                                
                                                   
                        
                        break
                break
        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Scheduled: "+str(len(ScheduledJobs))+" of the total of "+str(nrjobs)+"\n"
        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Checking completed orders \n"

        for jobname, job in ScheduledJobs.items():
            Product = job.getProduct()
            Quant = job.getQuantity()
            CurStock = self.getDataManager().getProducts()[Product.getName()].getStockLevel()
            NewStock = CurStock + Quant
            self.getDataManager().getProducts()[Product.getName()].setStockLevel(NewStock)

        Orderstatus = []

        for orders in SelectedOrders:
            product = orders.getProduct()
            orderquant = orders.getQuantity()
            productstock = self.getDataManager().getProducts()[product.getName()].getStockLevel()
            if orderquant <= productstock:
                self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Order: "+str(orders.getName())+" of product "+str(product.getName())+" with a quantity of "+str(orderquant)+" was fully completed within the schedule horizon \n\n"
                
                productstock = productstock - orderquant
                self.getDataManager().getProducts()[product.getName()].setStockLevel(productstock)
                Orderstatus.append(str(orders.getName())+": Completed")
            elif orderquant > productstock and productstock>0:
                self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Order: "+str(orders.getName())+" of product "+str(product.getName())+" with a quantity of "+str(orderquant)+" was partially completed. "+str(productstock)+" out of "+str(orderquant)+" was created. \n\n"
                self.getDataManager().getProducts()[product.getName()].setStockLevel(0)
                Orderstatus.append(str(orders.getName())+": Partially Completed")
            else:
               self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Order: "+str(orders.getName())+" of product "+str(product.getName())+" with a quantity of "+str(orderquant)+" was not completed because there was no stock. \n\n"
               Orderstatus.append(str(orders.getName())+": Nothing completed")
        

        myops =  [i.getName() for i in oprdict.keys() if len(self.getDataManager().getOperations()[i.getName()].getJobs()) > 0 ]
        myres = [i for i in self.getDataManager().getResources().keys()]
        self.getVisualManager().getSchedulingTab().getPSchOperations().options = myops
        self.getVisualManager().getSchedulingTab().getPSchOrderlist().options = Orderstatus
        self.getVisualManager().getSchedulingTab().getPSchResources().options = myres
            

        # schedules_df = pd.DataFrame(columns= ["ResourceID","Shift","JobID","Starttime","Day"])
        # folder = 'UseCases'; casename = self.getVisualManager().getSchedulingTab().getCOTBcasename().value
        # path = folder+"\\"+casename
        # isExist = os.path.exists(path)
        
        # if not isExist:
        #     os.makedirs(path)
        
        # for name,myres in self.getDataManager().getResources().items():
        #     if name != 'Operator 1' and name != 'Operator 2' and name != 'Operator 3' and name != 'Manual workers':
        #         for shift, jobs in myres.getSchedule().items():
        #             if jobs == []:
        #                 continue
        #             else:                
        #                 for job in jobs:
        #                     schedules_df.loc[len(schedules_df)] = {"ResourceID":myres.getID(), "Shift":shift.getNumber(),"JobID":job[0].getID(),"Starttime":str(job[1]),"Day":shift.getDay()}
                    
        # filename = 'Schedules.csv'; path = folder+"\\"+casename+"\\"+filename;fullpath = os.path.join(Path.cwd(), path)
        # schedules_df.to_csv(fullpath, index=False)                
        
        
                    
                       
                
        return 

        
       
      
        

    

  
