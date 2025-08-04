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
        
    
        
        
        #Initialize Schedulable Jobs
     
        SchedulableJobs= [] 
        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="TEST"+str(SchedulableJobs)+"\n"
        ScheduledJobs = dict() #key:Jobname, val: Job object

        # Fill the Schedulable Jobs List
        for opr, jobs in oprdict.items():
            for job in jobs:
                if len(job.getPredecessors()) == 0:
                    SchedulableJobs.append(job)


        # self.Schedule = dict()  #key: day, val: [(shift,[[jobs,Processed quantity]])]
               
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
                    
            i+=1        
                    
     
        #Create Schedule; we start by checking if there are still jobs that can be scheduled   
        while len(SchedulableJobs) >0:
            for j in SchedulableJobs:
                self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Scheduling job "+str(j.getName())+"\n"               
                predecessorjobs = j.getPredecessors()
                successorjob = j.getSuccessor()
                Quantity = j.getQuantity()
                PartialJob = False #Partial Job False is an indicator to check if a job could be completely scheduled during the shift
                EarliestStart = [1,1,0] # Initialize the earliest start [day,shift,starttime(i.e. completiontime of latest job)]
                if not (predecessorjobs ==[]):
                #Determine Earliest starttime if there are predecessor jobs
                    maxpredecessor = [None,None,None]
                    for i in predecessorjobs:
                        predecessor = [ScheduledJobs[i.getName()].getScheduledDay(),ScheduledJobs[i.getName()].getScheduledShift(),ScheduledJobs[i.getName()].getStartTime() + (i.getQuantity() * self.getDataManager().getOperations()[i.getOperation().getName()].getProcessTime())]
                        if maxpredecessor == [None,None,None]:
                            maxpredecessor = predecessor
                        if (predecessor[0] > maxpredecessor[0]) or (predecessor[0] == maxpredecessor[0] and predecessor[1] > maxpredecessor[1]) or (predecessor[0] == maxpredecessor[0] and predecessor[1] == maxpredecessor[1] and predecessor[2] > maxpredecessor[2] ):
                            maxpredecessor = predecessor
                    EarliestStart = maxpredecessor
                    
                #Determine earliest available resource
                processtime = (j.getQuantity() * self.getDataManager().getOperations()[j.getOperation().getName()].getProcessTime())
                resources = j.getOperation().getRequiredResources()
                for r in resources:
                    ##Here we implement first available resources when we have alternative machines implemented...
                    r = self.getDataManager().getResources()[r.getName()]
                    Automated = r.getAutomated()
                    opef = r.getOperatingEffort()
                    
                    restype = r.getType()
                    schedulableShift = [] #Here we track if we can schedule the job in the available shifts [day,shift]
                    completiontimeLatestJob = None #Here we track the completion time of the latest job

                                       

                    while schedulableShift == []: #Here we find the [day,shift] for when we can schedule the job
                        
                        for daynum, shiftjob in r.getSchedule().items():                          
                              
                            #Check which is the earliest shift that we are allowed to schedule also checking for effort availability of the operators
                            
                            if (daynum < EarliestStart[0]):
                                continue
                            if daynum >= EarliestStart[0]:
                                for shift in shiftjob: 
                                    if shift[0].getNumber() < EarliestStart[1]:
                                        
                                        continue
                                    if shift[0].getNumber() == EarliestStart[1]: #Check if latest job ends before the end of the shift
                                        if shift[1] == []: #Here we have an empty shift so we set this shift as 
                                            schedulableShift = [daynum, shift]
                                            completiontimeLatestJob = 0                                            
                                        if shift[1] != [] and shift[1][-1][0].getStartTime() + (shift[1][-1][1]*self.getDataManager().getOperations()[shift[1][-1][0].getOperation().getName()].getProcessTime()) >= shift[0].getCapacity():                                            
                                            continue
                                            
                                        #Check the availability of operators/manual workers if we have a machine or manual labour                                       
                                        effort = 0
                                        workershiftjobs = [] #Find the shift for effor to check
                                        if restype == 'Manual':
                                            SchedWorker = self.getDataManager().getResources()['Manual workers'].getSchedule()[daynum]
                                            for wrkshiftjob in SchedWorker:
                                                self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" shift check "+str(wrkshiftjob[0])+" and "+str(shift[0])+" \n"
                                                if wrkshiftjob[0].getNumber() == shift[0].getNumber():
                                                    workershiftjobs = wrkshiftjob[1]
                                            for workerjob in workershiftjobs: #Here we are calculating the effort of the shift already in use. workerjob is [job,processed quantity]
                                                effort += workerjob[0].getOperation().getRequiredResources()[0].getOperatingEffort()* workerjob[0].getOperation().getProcessTime()*workerjob[1]
                                            if (shift[0].getNumber()==1 and effort >= 24) or (shift[0].getNumber()==2 and effort>=21):
                                                continue
                                        if restype == 'Machine':
                                            if shift[0].getNumber() == 1:
                                                effort1 = 0
                                                effort2 = 0
                                                SchedWorker1 = self.getDataManager().getResources()['Operator 1'].getSchedule()[daynum][0]
                                                SchedWorker2 = self.getDataManager().getResources()['Operator 2'].getSchedule()[daynum][0]
                                                
                                                workershiftjobs1 = SchedWorker1[1]
                                                workershiftjobs2 = SchedWorker2[1]
                                                for workerjob in workershiftjobs1: #Here we are calculating the effort of the shift already in use. workerjob is [job,processed quantity]
                                                    effort1 += workerjob[0].getOperation().getRequiredResources()[0].getOperatingEffort()* workerjob[0].getOperation().getProcessTime()*workerjob[1]
                                                for workerjob in workershiftjobs2: #Here we are calculating the effort of the shift already in use. workerjob is [job,processed quantity]
                                                    effort2 += workerjob[0].getOperation().getRequiredResources()[0].getOperatingEffort()* workerjob[0].getOperation().getProcessTime()*workerjob[1]
                                                effort = min(effort1,effort2) #This checks the operator with the most effort available
                                                if effort >= 8:
                                                    continue
                                            if shift[0].getNumber() == 2:                                                
                                                SchedWorker = self.getDataManager().getResources()['Operator 3'].getSchedule()[daynum][0]
                                                workershiftjobs = SchedWorker[1]
                                                
                                                for workerjob in workershiftjobs: #Here we are calculating the effort of the shift already in use. workerjob is [job,processed quantity]
                                                    effort += workerjob[0].getOperation().getRequiredResources()[0].getOperatingEffort()* workerjob[0].getOperation().getProcessTime()*workerjob[1]
                                                
                                                if effort >= 7:
                                                    continue
                                        
                                        else:
                                            schedulableShift = [daynum,shift]
                                            if schedulableShift[1][1] == []:
                                                completiontimeLatestJob = 0
                                            else:
                                                
                                                completiontimeLatestJob = schedulableShift[1][1][-1][0].getStartTime() + (schedulableShift[1][1][-1][0].getQuantity()*self.getDataManager().getOperations()[schedulableShift[1][1][-1][0].getOperation().getName()].getProcessTime())
                                            break
                                if schedulableShift != []:
                                    break
                        if schedulableShift == []:
                            self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Job "+str(j.getName())+" cannot be scheduled on resource "+str(r.getName())+" Within the scheduling horizon of "+ str(day)+" days. \n"
                            break
                    if schedulableShift == []:
                            self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Job "+str(j.getName())+" cannot be scheduled on resource "+str(r.getName())+" Within the scheduling horizon of "+ str(day)+" days. \n"
                            SchedulableJobs.remove(j)
                            break
                    self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Deze shift is degene "+str(schedulableShift)
                    shiftday = schedulableShift[0]        
                    shiftcap = schedulableShift[1][0].getCapacity()
                    shiftnumber = schedulableShift[1][0].getNumber()

                    ##We have now determined the first shift that we can schedule in

                    
                    if restype == 'Manual':                   
                                                                                                                                        
                            j.setStartTime(completiontimeLatestJob)
                            if (completiontimeLatestJob + processtime) > shiftcap: #This means we can only schedule partially in this shift
                                PartialJob = True
                                fraction = shiftcap - completiontimeLatestJob
                                ProcessedQuantity = fraction/self.getDataManager().getOperations()[j.getOperation().getName()].getProcessTime()
                                Quantity = Quantity - ProcessedQuantity
                                
                                processtime = (Quantity * self.getDataManager().getOperations()[j.getOperation().getName()].getProcessTime())
                                r.getSchedule()[shiftday][shiftnumber-1][1].append([j,ProcessedQuantity])
                                self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Partially scheduled "+str(j.getName())+" on resource "+str(r.getName())+" During shift "+str(shiftnumber)+" On day "+str(shiftday)+"\n"+"Quantity remaining: "+str(Quantity)+"\n"
                                while PartialJob == True and shiftday <= day: #Also check if we are still in the scheduling horizon
                                    if shiftnumber == 1:
                                        shiftday = shiftday
                                        shiftcap = 7
                                        shiftnumber = 2
                                    if shiftnumber == 2:
                                        shiftday +=1
                                        shiftcap = 8
                                        shiftnumber = 1
                                        if shiftday > day: #This means we fall outside the planning horizon
                                            self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Job "+str(j.getName())+" cannot be fully scheduled on resource "+str(r.getName())+" Within the scheduling horizon of "+ str(day)+" days. \n"
                                            break
                                    if processtime > shiftcap:
                                        fraction = shiftcap
                                        ProcessedQuantity = fraction/self.getDataManager().getOperations()[j.getOperation().getName()].getProcessTime()
                                        Quantity = Quantity - ProcessedQuantity                                        
                                        processtime = (Quantity * self.getDataManager().getOperations()[j.getOperation().getName()].getProcessTime())
                                        self.getDataManager().getResources()['Manual workers'].getSchedule()[shiftday][shiftnumber-1][1].append([j,ProcessedQuantity])
                                        r.getSchedule()[shiftday][shiftnumber-1][1].append([j,ProcessedQuantity])
                                        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Partially scheduled "+str(j.getName())+" on resource "+str(r.getName())+" During shift "+str(shiftnumber)+" On day "+str(shiftday)+"\n"+"Quantity remaining: "+str(Quantity)+"\n"
                                        continue
                                    if processtime <= shiftcap:
                                        PartialJob = False
                                        ProcessedQuantity = fraction/self.getDataManager().getOperations()[j.getOperation().getName()].getProcessTime()
                                        Quantity = Quantity - ProcessedQuantity                                        
                                        processtime = (Quantity * self.getDataManager().getOperations()[j.getOperation().getName()].getProcessTime())
                                        self.getDataManager().getResources()['Manual workers'].getSchedule()[shiftday][shiftnumber-1][1].append([j,ProcessedQuantity])
                                        r.getSchedule()[shiftday][shiftnumber-1][1].append([j,ProcessedQuantity])
                                        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Completely scheduled "+str(j.getName())+" on resource "+str(r.getName())+" During shift "+str(shiftnumber)+" On day "+str(shiftday)+"\n"
                                        ScheduledJobs[j.getName()] = j
                                        j.setScheduledShift(shiftnumber)
                                        j.setScheduledDay(shiftday)
                                        SchedulableJobs.remove(j) #Remove scheduled job

                                        ## check if successor can be scheduled.
                                    
                                        Schedulable = True
                                        if successorjob is not None:
                                                for predjbs in successorjob.getPredecessors():
                                                    if predjbs in ScheduledJobs:
                                                        continue
                                                    else:
                                                        Schedulable = False;
                                        if Schedulable == True:
                                            if successorjob not in ScheduledJobs and successorjob is not None:
                                                SchedulableJobs.append(successorjob)
                                                    

                                break
                                
                                
                                
                            else:
                                ProcessedQuantity = Quantity
                                r.getSchedule()[shiftday][shiftnumber-1][1].append([j,ProcessedQuantity])
                                j.setScheduledShift(shiftnumber)
                                j.setScheduledDay(shift[0].getDay())
                                ScheduledJobs[j.getName()] = j
                                self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Completely scheduled "+str(j.getName())+" on resource "+str(r.getName())+" During shift "+str(shift[0].getNumber())+" On day "+str(shift[0].getDay())+"\n"
                                SchedulableJobs.remove(j) #Remove scheduled job
                                self.getDataManager().getResources()['Manual workers'].getSchedule()[shiftday][shiftnumber-1][1].append([j,ProcessedQuantity])
                            
                                                                                                                         
                                
                                ## check if successor can be scheduled.
                                    
                                Schedulable = True
                                if successorjob is not None:
                                        for predjbs in successorjob.getPredecessors():
                                            if predjbs in ScheduledJobs:
                                                continue
                                            else:
                                                Schedulable = False;
                                if Schedulable == True:
                                    if successorjob not in ScheduledJobs and successorjob is not None:
                                        SchedulableJobs.append(successorjob)
                            
                            
                            
                            
                            break                                  
                        
                                                                                                               
                        
                    
                    elif restype == 'Outsourced':                      
                                                            
                            j.setStartTime(completiontimeLatestJob)
                            if (completiontimeLatestJob + processtime) > shiftcap:
                                PartialJob = True
                                fraction = shiftcap - completiontimeLatestJob
                                processtime = processtime - shiftcap
                                r.getSchedule()[shiftday][shiftnumber-1][1].append([j,'-'])
                                self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Partially scheduled "+str(j.getName())+" on resource "+str(r.getName())+" During shift "+str(shift.getNumber())+" On day "+str(shift.getDay())+"\n"
                                while PartialJob == True and shiftday <= day: #Also check if we are still in the scheduling horizon
                                    if shiftnumber == 1:
                                        shiftday = shiftday
                                        shiftcap = 7
                                        shiftnumber = 2
                                    if shiftnumber == 2:
                                        shiftday +=1
                                        shiftcap = 8
                                        shiftnumber = 1
                                        if shiftday > day: #This means we fall outside the planning horizon
                                            self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Job "+str(j.getName())+" cannot be fully scheduled on resource "+str(r.getName())+" Within the scheduling horizon of "+ str(day)+" days. \n"
                                            break
                                    if processtime > shiftcap:
                                        fraction = shiftcap - completiontimeLatestJob
                                        processtime = processtime - shiftcap
                                        r.getSchedule()[shiftday][shiftnumber-1][1].append([j,'-'])
                                        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Partially scheduled "+str(j.getName())+" on resource "+str(r.getName())+" During shift "+str(shift.getNumber())+" On day "+str(shift.getDay())+"\n"
                                        continue
                                    if processtime <= shiftcap:
                                        PartialJob = False
                                        fraction = shiftcap - completiontimeLatestJob
                                        processtime = processtime - shiftcap
                                        r.getSchedule()[shiftday][shiftnumber-1][1].append([j,'-'])
                                        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Completely scheduled "+str(j.getName())+" on resource "+str(r.getName())+" During shift "+str(shiftnumber)+" On day "+str(shiftday)+"\n"
                                        ScheduledJobs[j.getName()] = j
                                        j.setScheduledShift(shiftnumber)
                                        j.setScheduledDay(shiftday)
                                        SchedulableJobs.remove(j) #Remove scheduled job

                                        ## check if successor can be scheduled.                                        
                                    
                                        Schedulable = True
                                        for predjbs in successorjob.getPredecessors():
                                            if predjbs in ScheduledJobs:
                                                continue
                                            else:
                                                Schedulable = False;
                                        if Schedulable == True:
                                            if successorjob not in ScheduledJobs and successorjob is not None:
                                                SchedulableJobs.append(successorjob)
                                break

                                                
                            else:
                                ProcessedQuantity = Quantity
                                r.getSchedule()[shiftday][shiftnumber-1][1].append([j,'-'])
                                j.setScheduledShift(shiftnumber)
                                j.setScheduledDay(shift[0].getDay())
                                ScheduledJobs[j.getName()] = j
                                self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Completely scheduled "+str(j.getName())+" on resource "+str(r.getName())+" During shift "+str(shift[0].getNumber())+" On day "+str(shift[0].getDay())+"\n"
                                SchedulableJobs.remove(j) #Remove scheduled job
                            
                            
                                                              
                                                            
                            
                                ## check if successor can be scheduled.
                                    
                                Schedulable = True
                                if successorjob is not None:
                                        for predjbs in successorjob.getPredecessors():
                                            if predjbs in ScheduledJobs:
                                                continue
                                            else:
                                                Schedulable = False;
                                if Schedulable == True:
                                    if successorjob not in ScheduledJobs and successorjob is not None:
                                        SchedulableJobs.append(successorjob)
                            
                            
                            
                            
                            break
                            
            
                                                                                                                                          
                        
                        
                    else:
                                                                                                          
                        j.setStartTime(completiontimeLatestJob)
                        if (completiontimeLatestJob + processtime) > shiftcap: #This means we can only schedule partially in this shift
                            PartialJob = True
                            fraction = shiftcap - completiontimeLatestJob
                            ProcessedQuantity = fraction/self.getDataManager().getOperations()[j.getOperation().getName()].getProcessTime()
                            Quantity = Quantity - ProcessedQuantity
                            
                            processtime = (Quantity * self.getDataManager().getOperations()[j.getOperation().getName()].getProcessTime())
                            r.getSchedule()[shiftday][shiftnumber-1][1].append([j,ProcessedQuantity])
                            self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Partially scheduled "+str(j.getName())+" on resource "+str(r.getName())+" During shift "+str(shiftnumber)+" On day "+str(shiftday)+"\n"+"Quantity remaining: "+str(Quantity)+"\n"
                            while PartialJob == True and shiftday <= day: #Also check if we are still in the scheduling horizon
                                if Automated == True:
                                    if shiftnumber == 1:
                                        shiftday = shiftday
                                        shiftcap = 7
                                        shiftnumber = 2
                                    if shiftnumber == 2:
                                        shiftday = shiftday
                                        shiftcap = 8
                                        shiftnumber = 3
                                    if shiftnumber == 3:
                                        shiftday +=1
                                        shiftcap = 8
                                        shiftnumber = 1
                                        if shiftday > day: #This means we fall outside the planning horizon
                                            self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Job "+str(j.getName())+" cannot be fully scheduled on resource "+str(r.getName())+" Within the scheduling horizon of "+ str(day)+" days. \n"
                                            break
                                else:
                                    if shiftnumber == 1:
                                        shiftday = shiftday
                                        shiftcap = 7
                                        shiftnumber = 2
                                    if shiftnumber == 2:
                                        shiftday +=1 
                                        shiftcap = 8
                                        shiftnumber = 1
                                        if shiftday > day: #This means we fall outside the planning horizon
                                            self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Job "+str(j.getName())+" cannot be fully scheduled on resource "+str(r.getName())+" Within the scheduling horizon of "+ str(day)+" days. \n"
                                            break
                                if processtime > shiftcap:
                                    fraction = shiftcap
                                    ProcessedQuantity = fraction/self.getDataManager().getOperations()[j.getOperation().getName()].getProcessTime()
                                    Quantity = Quantity - ProcessedQuantity                                        
                                    processtime = (Quantity * self.getDataManager().getOperations()[j.getOperation().getName()].getProcessTime())
                                    if shiftnumber == 1 and effort1 <= effort2:
                                        self.getDataManager().getResources()['Operator 1'].getSchedule()[shiftday][shiftnumber-1][1].append([j,ProcessedQuantity])
                                    elif shiftnumber == 1 and effort1 > effort2:
                                        self.getDataManager().getResources()['Operator 2'].getSchedule()[shiftday][shiftnumber-1][1].append([j,ProcessedQuantity])
                                    else:
                                        self.getDataManager().getResources()['Operator 3'].getSchedule()[shiftday][shiftnumber-1][1].append([j,ProcessedQuantity])
                                    r.getSchedule()[shiftday][shiftnumber-1][1].append([j,ProcessedQuantity])
                                    self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Partially scheduled "+str(j.getName())+" on resource "+str(r.getName())+" During shift "+str(shiftnumber)+" On day "+str(shiftday)+"\n"+"Quantity remaining: "+str(Quantity)+"\n"
                                    continue
                                if processtime <= shiftcap:
                                    PartialJob = False
                                    ProcessedQuantity = fraction/self.getDataManager().getOperations()[j.getOperation().getName()].getProcessTime()
                                    Quantity = Quantity - ProcessedQuantity                                        
                                    processtime = (Quantity * self.getDataManager().getOperations()[j.getOperation().getName()].getProcessTime())
                                    if shiftnumber == 1 and effort1 <= effort2:
                                        self.getDataManager().getResources()['Operator 1'].getSchedule()[shiftday][shiftnumber-1][1].append([j,ProcessedQuantity])
                                    elif shiftnumber == 1 and effort1 > effort2:
                                        self.getDataManager().getResources()['Operator 2'].getSchedule()[shiftday][shiftnumber-1][1].append([j,ProcessedQuantity])
                                    else:
                                        self.getDataManager().getResources()['Operator 3'].getSchedule()[shiftday][shiftnumber-1][1].append([j,ProcessedQuantity])
                                    r.getSchedule()[shiftday][shiftnumber-1][1].append([j,ProcessedQuantity])
                                    self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Completely scheduled "+str(j.getName())+" on resource "+str(r.getName())+" During shift "+str(shiftnumber)+" On day "+str(shiftday)+"\n"
                                    ScheduledJobs[j.getName()] = j
                                    j.setScheduledShift(shiftnumber)
                                    j.setScheduledDay(shiftday)
                                    SchedulableJobs.remove(j) #Remove scheduled job

                                    ## check if successor can be scheduled.
                                    
                                    Schedulable = True
                                    if successorjob is not None:
                                        for predjbs in successorjob.getPredecessors():
                                            if predjbs in ScheduledJobs:
                                                continue
                                            else:
                                                Schedulable = False;
                                    if Schedulable == True:
                                        if successorjob not in ScheduledJobs and successorjob is not None:
                                            SchedulableJobs.append(successorjob)
                                                

                            break
                            
                            
                            
                        else:
                            ProcessedQuantity = Quantity
                            r.getSchedule()[shiftday][shiftnumber-1][1].append([j,ProcessedQuantity])
                            j.setScheduledShift(shiftnumber)
                            j.setScheduledDay(shift[0].getDay())
                            ScheduledJobs[j.getName()] = j
                            self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Completely scheduled "+str(j.getName())+" on resource "+str(r.getName())+" During shift "+str(shift[0].getNumber())+" On day "+str(shift[0].getDay())+"\n"
                            SchedulableJobs.remove(j) #Remove scheduled job
                            if shiftnumber == 1 and effort1 <= effort2:
                                self.getDataManager().getResources()['Operator 1'].getSchedule()[shiftday][shiftnumber-1][1].append([j,ProcessedQuantity])
                            elif shiftnumber == 1 and effort1 > effort2:
                                self.getDataManager().getResources()['Operator 2'].getSchedule()[shiftday][shiftnumber-1][1].append([j,ProcessedQuantity])
                            else:
                                self.getDataManager().getResources()['Operator 3'].getSchedule()[shiftday][shiftnumber-1][1].append([j,ProcessedQuantity])                            
                                                        
                            
                            ## check if successor can be scheduled.
                                    
                            Schedulable = True
                            if successorjob is not None:
                                    for predjbs in successorjob.getPredecessors():
                                        if predjbs in ScheduledJobs:
                                            continue
                                        else:
                                            Schedulable = False;
                            if Schedulable == True:
                                if successorjob not in ScheduledJobs and successorjob is not None:
                                    SchedulableJobs.append(successorjob)
                        
                        
                        
                        
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

        
       
      
        

    

  
