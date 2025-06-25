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
        shiftnum = 1000;
        
        i=1;
        day=1;
        shiftlist=[]
        while i <= shiftnum:
            if i % 2 == 1:
                shift = Shift(i,1,8)
                shiftlist.append(shift)
                i+=1;
            else:
                shift=Shift(i,2,7)
                shiftlist.append(shift)
                i+=1
        
        #Initialize Schedulable Jobs
        AllJobs = dict()
        SchedulableJobs=[]
        
        ScheduledJobs=[]
        for opr, jobs in oprdict.items():
            for job in jobs:
                if job.getPredecessors() == []:
                    SchedulableJobs.append(job)
                AllJobs[job.getName()]=job;
        counter = 0       
        #Initialize schedule for each Resource:
        for resname, res in self.getDataManager().getResources().items():
            for i in shiftlist:
                res.getSchedule()[i]=[]
        
        #Create Schedule
        while len(SchedulableJobs) >0:
            for j in SchedulableJobs:
                predecessorjobs = j.getPredecessors()
                successorjobs = j.getSuccessor()
                if not (predecessorjobs ==[]):
                #Determine Earliest starttime
                    maxpredecessor = None;
                    for i in predecessorjobs:
                        completiontime = i.getStartTime() + (i.getQuantity() * self.getDataManager().getOperations()[i.getOperation().getName()].getProcessTime())
                        if maxpredecessor == None or completiontime >= maxpredecessor:
                            maxpredecessor = completiontime
                    EarliestStart = maxpredecessor;
                else:
                    EarliestStart = 0
                    
                #Determine earliest available resource
                processtime = (j.getQuantity() * self.getDataManager().getOperations()[j.getOperation().getName()].getProcessTime())
                resources = j.getOperation().getRequiredResources()
                for r in resources:
                    Automated = r.getAutomated()
                    opef = r.getOperatingEffort()
                    for shift, jobtime in r.getSchedule().items():
                        
                        ##Here we now have the completion time of the last job in a shift. Check if the to job to schedule fits in the shift. Else check next shift.
                        if jobtime ==[]:
                            completiontimeLatestJob = 0;
                        else:
                            completiontimeLatestJob = jobtime[::-1][0][1] + (jobtime[::-1][0][0].getQuantity() * self.getDataManager().getOperations()[jobtime[::-1][0][0].getOperation().getName()].getProcessTime())
                        
                        shiftcap = shift.getCapacity()
                        shiftnumber = shift.getNumber()
                        
                        if shiftnumber == 1:
                            CurOpeffOp1 = 0; ## Also check operator availability.
                            SchedOp1 = self.getDataManager().getResources()['Operator 1'].getSchedule();
                            CurOpeffOp2 = 0;
                            SchedOp2 = self.getDataManager().getResources()['Operator 2'].getSchedule();
                            for mach in SchedOp1[shift]:                                
                                CurOpeffOp1 += self.getDataManager().getResources()[mach].getOperatingEffort()
                            for mach in SchedOp2[shift]:                                
                                CurOpeffOp2 += self.getDataManager().getResources()[mach].getOperatingEffort()
        
                            if shiftcap > (completiontimeLatestJob + processtime) and (CurOpeffOp1 + opef <= 1 or CurOpeffOp2 + opef <=1): #This means we can schedule in first shift
                                j.setStartTime(completiontimeLatestJob)
                                if (CurOpeffOp1 +opef <= 1):
                                   SchedOp1[shift].append(r.getName())
                                else:
                                    SchedOp2[shift].append(r.getName())
                                r.getSchedule()[shift].append((j,completiontimeLatestJob))                                
                                ScheduledJobs.append(j)
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
                                
                                SchedulableJobs.remove(j) #Remove scheduled job
                                break
                            else:
                                continue
        
                        if shiftnumber == 2:
                            CurOpeffOp3 = 0; ## Also check operator availability.
                            SchedOp3 = self.getDataManager().getResources()['Operator 3'].getSchedule();
                            
                            for mach in SchedOp3[shift]:                                
                                CurOpeffOp3 += self.getDataManager().getResources()[mach].getOperatingEffort()
                            if  ((Automated is None) and processtime < 8) or Automated == False:
                                if shiftcap > (completiontimeLatestJob + processtime) and (CurOpeffOp3 + opef<=1): #This means we can schedule in second shift
                                    j.setStartTime(completiontimeLatestJob)
                                    SchedOp3[shift].append(r.getName())
                                    
                                    r.getSchedule()[shift].append((j,completiontimeLatestJob))                                
                                    ScheduledJobs.append(j)
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
                                    
                                    SchedulableJobs.remove(j) #Remove scheduled job
                                    break
                                else:
                                    continue
        
                            elif (Automated == True) or (Automated is None and processtime > 8):                        
                                if shiftcap >= (completiontimeLatestJob) and (CurOpeffOp3 + opef<=1): #This means we can schedule in second shift
                                    j.setStartTime(completiontimeLatestJob)
                                    SchedOp3[shift].append(r.getName())
                                    
                                    r.getSchedule()[shift].append((j,completiontimeLatestJob))                                
                                    ScheduledJobs.append(j)
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
                                    
                                    SchedulableJobs.remove(j) #Remove scheduled job
                                    break
                                else:
                                    continue                        
                    break             
        self.getVisualManager().getPSchScheRes().value+=" All jobs are scheduled: "+str(nrjobs)+"\n"                     
                            
        

                    
                        
                        
                
                        
                
        return

        
       
      
        

    

  
