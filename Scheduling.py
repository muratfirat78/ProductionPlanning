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
                    
                    numPredjobs = len(Predjobs)
                    k = 0;
                    while k < numPredjobs:
                        if Predjobs[k].getQuantity() < CapCurJob:
                            CapCurJob = CapCurJob - Predjobs[k].getQuantity();
                            CurJobs[i].getPredecessors().append(Predjobs[k]);
                            Predjobs[k].getSuccessor().append(CurJobs[i]);
                            k += 1;
                        else:
                            CurJobs[i].getPredecessors().append(Predjobs[k]);
                            Predjobs[k].getSuccessor().append(CurJobs[i]);
                            k +=1;
                            print(k);
                            if k == numPredjobs:
                                break
                            else:
                                Predjobs = Predjobs[k:];
                                break
        ## Initialize shifts (example 30 days?)
        shiftnum = 30;
        i=1;
        day=1;
        shiftlist=[]
        while i <= 30:
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
                if job.getPredecessor == []:
                    SchedulableJobs.append(job)
                AllJobs[job.getName()]=job;
        #Initialize schedule for each Resource:
        for resname, res in self.getDataManager.getResources.items():
            for i in shiftlist:
                res.getSchedule[i]=[]

        #Create Schedule
        while len(SchedulableJobs) >0:
            for j in SchedulableJobs:
                predecessorjobs = j.getPredecessors():
                if not (predecessorjobs ==[]):
                #Determine Earliest starttime
                    maxpredecessor = None:
                    for i in predecessorjobs:
                        completiontime = i.getStartTime + (i.getQuantity() * self.getDataManager.getOperations()[i.getOperation()].getProcessTime())
                        if maxpredecessor == None or completiontime >= maxpredecessor:
                            maxpredecessor = completiontime
                    EarliestStart = maxpredecessor;
                else:
                    EarliestStart = 0
                #Determine earliest available resource
                processtime = (j.getQuantity * self.getDataManager.getOperations()[j.getOperation()].getProcessTime())
                resources = j.getOperation().getRequiredResources()
                for r in resources:
                    for shift, jobtime in r.getSchedule.items():
                        completiontimeLatestJob = jobtime[::-1][1] + (jobtime[::-1][0].getQuantity * self.getDataManager.getOperations()[jobtime[::-1][0].getOperation()].getProcessTime())

                    ##Here we now have the completion time of the last job in a shift. Check if the to job to schedule fits in the shift. Else check next shift.
                    ## Also check operator availability.
                    
                        
                
        return

        
       
      
        

    

  
