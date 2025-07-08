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

        self.getVisualManager().getPSchScheRes().value+="Scheduling starts..."+"\n"

        oprdict = dict() # key: operation, #val: set of jobs
        
        for resname,res in self.getDataManager().getResources().items():
            res.getSchedule().clear()
        
        # Collect operations with jobs
        nrjobs = 0
        for prname,prod in self.getDataManager().getProducts().items():
            for opr in prod.getOperations():
                if not opr in oprdict:
                    oprdict[opr] = opr.getJobs()
                    nrjobs+= len(opr.getJobs())
                    
        self.getVisualManager().getPSchScheRes().value+=" To schedule jobs: "+str(nrjobs)+"\n"
        revopdict = {k: oprdict[k] for k in sorted(oprdict, key=lambda x: list(oprdict.keys()).index(x), reverse=True)}
        
        
        for k1, k2 in zip(revopdict, list(revopdict)[1:]): #links pairs of keys together 
            if len(revopdict[k1]) > 0 and len(revopdict[k2]) >0:
                CurJobs = revopdict[k1][::-1];
                Predjobs = revopdict[k2][::-1];
                
                for i in range(0,len(CurJobs)):
                    CapCurJob = CurJobs[i].getQuantity();           
                              
                    
                    for k in Predjobs:
                        
                        if k.getQuantity() < CapCurJob:
                            CapCurJob = CapCurJob - k.getQuantity();
                            if k not in CurJobs[i].getPredecessors():
                                CurJobs[i].getPredecessors().append(k);
                            if CurJobs[i] not in k.getSuccessor():
                                k.getSuccessor().append(CurJobs[i]);
                            Predjobs.remove(k)
                        else:
                            if k not in CurJobs[i].getPredecessors():
                                CurJobs[i].getPredecessors().append(k);
                            
                            if CurJobs[i] not in k.getSuccessor():
                                k.getSuccessor().append(CurJobs[i]);
                            Predjobs.remove(k)                       
                            break
        ## Initialize shifts (example 30 days?)
        day = 1000;
        
        i=1;
        shiftlistman=[]
        shiftlistaut=[]
        while i <= day:
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
        AllJobs = dict()
        SchedulableJobs=[]
        
        ScheduledJobs=dict()
        for opr, jobs in oprdict.items():
            for job in jobs:
                if job.getPredecessors() == []:
                    SchedulableJobs.append(job)
                AllJobs[job.getName()]=job;
        counter = 0       
        #Initialize schedule for each Resource:
        for resname, res in self.getDataManager().getResources().items():
            if (res.getAutomated() is None) or (res.getAutomated()==False):
                for i in shiftlistman:
                    res.getSchedule()[i]=[]
            else:
                for i in shiftlistaut:
                    res.getSchedule()[i]=[]
        
        #Create Schedule
        while len(SchedulableJobs) >0:
            for j in SchedulableJobs:
                                
                predecessorjobs = j.getPredecessors()
                successorjobs = j.getSuccessor()
                Quantity = j.getQuantity()
                PartialJob = False
                EarliestDay = 1
                EarliestShift = 1
                EarliestStart = 0
                if not (predecessorjobs ==[]):
                #Determine Earliest starttime
                    maxpredecessorday = None;
                    maxpredecessorshift = None;
                    maxpredecessortime = None;
                    for i in predecessorjobs:
                        predecessorday = ScheduledJobs[i.getName()].getScheduledDay()
                        predecessorshift = ScheduledJobs[i.getName()].getScheduledShift()
                        completiontime = ScheduledJobs[i.getName()].getStartTime() + (i.getQuantity() * self.getDataManager().getOperations()[i.getOperation().getName()].getProcessTime())
                        if maxpredecessorday == None or predecessorday >= maxpredecessorday:
                            maxpredecessorday = predecessorday
                        if maxpredecessorshift == None or predecessorshift >= maxpredecessorshift:
                            maxpredecessorshift = predecessorshift
                        if maxpredecessortime == None or completiontime >= maxpredecessortime:
                            maxpredecessortime = completiontime
                    EarliestStart = maxpredecessor;
                    EarliestDay = maxpredecessorday;
                    EarliestShift = maxpredecessorshift;
                    
                #Determine earliest available resource
                processtime = (j.getQuantity() * self.getDataManager().getOperations()[j.getOperation().getName()].getProcessTime())
                resources = j.getOperation().getRequiredResources()
                for r in resources:
                    Automated = r.getAutomated()
                    opef = r.getOperatingEffort()
                    
                    restype = r.getType()
                    
                    if restype == 'Manual':
                        
                        
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
                                        continue
                                    else:
                                        ProcessedQuantity = Quantity
                                        r.getSchedule()[shift].append((j,completiontimeLatestJob,ProcessedQuantity))
                                        j.setScheduledShift(shiftnumber)
                                        j.setScheduledDay(shift.getDay())
                                        ScheduledJobs[j.getName()] = j
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
                                        continue
                                    else:
                                        ProcessedQuantity = Quantity
                                        r.getSchedule()[shift].append((j,completiontimeLatestJob,ProcessedQuantity))
                                        j.setScheduledShift(shiftnumber)
                                        j.setScheduledDay(shift.getDay())
                                        ScheduledJobs[j.getName()] = j
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
                                    continue
                                else:
                                    ProcessedQuantity = Quantity
                                    r.getSchedule()[shift].append((j,completiontimeLatestJob,'-'))
                                    j.setScheduledShift(shiftnumber)
                                    j.setScheduledDay(shift.getDay())
                                    ScheduledJobs[j.getName()] = j
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
                                        continue
                                    else:
                                        ProcessedQuantity = Quantity
                                        r.getSchedule()[shift].append((j,completiontimeLatestJob,ProcessedQuantity))
                                        j.setScheduledShift(shiftnumber)
                                        j.setScheduledDay(shift.getDay())
                                        ScheduledJobs[j.getName()] = j
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
                                        continue
                                    else:
                                        ProcessedQuantity = Quantity
                                        r.getSchedule()[shift].append((j,completiontimeLatestJob,ProcessedQuantity))
                                        j.setScheduledShift(shiftnumber)
                                        j.setScheduledDay(shift.getDay())
                                        ScheduledJobs[j.getName()] = j
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
                                    
                                else:
                                    ProcessedQuantity = Quantity
                                    r.getSchedule()[shift].append((j,completiontimeLatestJob,ProcessedQuantity))
                                    j.setScheduledShift(shiftnumber)
                                    j.setScheduledDay(shift.getDay())
                                    ScheduledJobs[j.getName()] = j
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
                                        SchedulableJobs.append(sucjob)                           
                                
                                
                                break
                                
                                                   
                        
                        break
                break
        self.getVisualManager().getPSchScheRes().value+=" All jobs are scheduled: "+str(nrjobs)+"\n"

        schedules_df = pd.DataFrame(columns= ["ResourceID","Shift","JobID","Starttime","Day"])
        folder = 'UseCases'; casename = self.getVisualManager().getCOTBcasename().value
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
                        for job in jobs:
                            schedules_df.loc[len(schedules_df)] = {"ResourceID":myres.getID(), "Shift":shift.getNumber(),"JobID":job[0].getID(),"Starttime":str(job[1]),"Day":shift.getDay()}
                    
        filename = 'Schedules.csv'; path = folder+"\\"+casename+"\\"+filename;fullpath = os.path.join(Path.cwd(), path)
        schedules_df.to_csv(fullpath, index=False)                
        

                    
                        
                        
                
                        
                
        return 

        
       
      
        

    

  
