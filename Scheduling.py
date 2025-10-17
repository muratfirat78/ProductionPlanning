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
from GreedyInsertion import *
from CommonGreedyInsertion import *
from SimpleBatching import *
from AdvancedAlgorithmBryan import *

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
        self.CurrentscheduleEnd = None
        self.MyShifts = dict()  # key: date, val: [shifts] 
        self.MyCurrentSchedule = None


    def setMyCurrentSchedule(self,myitm):
        self.MyCurrentSchedule = myitm 
        return

    def getMyCurrentSchedule(self):
        return self.MyCurrentSchedule

    def getMyShifts(self):
        return self.MyShifts 

    def setCurrentscheduleEnd(self,myitm):
        self.CurrentscheduleEnd = myitm 
        return

    def getCurrentscheduleEnd(self):
        return self.CurrentscheduleEnd

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

    def CreateShifts(self,psstart,pssend,applied):

        scheduleperiod = pd.date_range(psstart,pssend)

        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" shift creating starts... "+"\n"

        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" applied... "+str(applied)+"\n"
        
        i=1
        prev_dayshift = None 
        scheduletimehour = 1
        
        for curr_date in scheduleperiod:

            dayshifts = []
            
            shift1=Shift(curr_date,3,prev_dayshift)
            shift1.setStartTime(scheduletimehour) 

            
            shift1.setStartHour(curr_date + timedelta(hours=0))
            shift1.setEndHour(curr_date + timedelta(hours=7)+ timedelta(minutes=59))
          
            scheduletimehour+=8
            shift1.setEndTime(scheduletimehour-1)
            dayshifts.append(shift1)

            
            if applied:
                if not curr_date in self.getMyShifts():
                    self.getMyShifts()[curr_date] = []
                else:
                    self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" applied but date is in shifts: "+str(curr_date)+"\n"

                self.getMyShifts()[curr_date].append(shift1)     
            else:
                if curr_date in self.getMyShifts():
                    shift1 = self.getMyShifts()[curr_date][0]
                else:
                    self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" not applied and date is not in shifts: "+str(curr_date)+"\n" 

            
            shift2=Shift(curr_date,1,shift1)
            shift2.setStartTime(scheduletimehour)   
            scheduletimehour+=8
            shift2.setEndTime(scheduletimehour-1)

            shift2.setStartHour(curr_date + timedelta(hours=8))
            shift2.setEndHour(curr_date + timedelta(hours=15)+timedelta(minutes=59))

            if applied:
                self.getMyShifts()[curr_date].append(shift2)   
            else:
                if curr_date in self.getMyShifts():
                    shift2 = self.getMyShifts()[curr_date][1]
                    
            dayshifts.append(shift2)
            
            
            shift3=Shift(curr_date,2,shift2)
            shift3.setStartTime(scheduletimehour)
            scheduletimehour+=8
            shift3.setEndTime(scheduletimehour-1)
            shift3.setStartHour(curr_date + timedelta(hours=16))
            shift3.setEndHour(curr_date + timedelta(hours=23)+ timedelta(minutes=59))

            if applied:
                self.getMyShifts()[curr_date].append(shift3)   
            else:
                if curr_date in self.getMyShifts():
                    shift3 = self.getMyShifts()[curr_date][2]
   
            prev_dayshift=shift3

            dayshifts.append(shift3)

            opno = 0
            for resname, res in self.getDataManager().getResources().items():

           
                if res.getType() == "Machine":
                    
                    for currshift in dayshifts:
                        
                        if currshift.getNumber() in res.getAvailableShifts():
                            if applied:
                                res.getSchedule()[currshift] = []
                            else:
                                if res.getName() == "M5-03 - Haas - 5axis - Manual (UMC750)":
                                    self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=", res.. "+str(res.getName())+"\n"
                                    self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Sh:("+str(currshift.getDay())+","+str(currshift.getNumber())+"), hrs: ["+str(currshift.getStartTime())+"-"+str(currshift.getEndTime())+"]\n" 
                    

                                res.getCurrentSchedule()[currshift] = []

                            if currshift.getNumber() == 3:
                                res.getShiftOperatingModes()[currshift] = "Self-Running"
                            else:
                                res.getShiftOperatingModes()[currshift] = "Operated"


                if (res.getType() == "Manual") or (res.getType() == "Operator"):                   
                    for currshift in dayshifts:
                        if currshift.getNumber() in res.getAvailableShifts():
                            if applied:
                                res.getSchedule()[currshift] = []
                            else:
                                res.getCurrentSchedule()[currshift] = []
        
          
                if res.getType() == "Outsourced":
                    for currshift in dayshifts:
                        if currshift.getNumber() in res.getAvailableShifts():
                            res.getCurrentSchedule()[currshift] = []
                
                    
            i+=1        

        return 

    def CalculateFTEUse(self,res,shift):

        totalfte = 0

        if res.getProcessType() == "Metal forming":
            
            self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" fte calculations..  "+res.getName()+"> "+str(res.getType())+"\n"
    
            for resname,myres in self.getDataManager().getResources().items():
                if myres.getProcessType()== res.getProcessType():
                    if shift in myres.getCurrentSchedule():
                        for job in mach.getCurrentSchedule()[shift]:
                            machhrprocesstime = min(shift.getEndTime()+1,job.getCompletionTime())-max(shift.getStartTime(),job.getStartTime()) #mach-hours
                            manhourprocesstime = machhrprocesstime*myres.getOperatingEffort()
                            totalfte+=manhourprocesstime/(shift.getEndTime()-shift.getStartTime()+1)

        return totalfte

    def MakeSchedule(self,schedulealg,batchingalg):
      

        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="Scheduling  : "+str(batchingalg)+"\n"

        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="Batching  : "+str(batchingalg)+"\n"

        
        psstart = self.getSHStart()
        psstart = psstart.replace(hour=0, minute=0, second=0, microsecond=0)+ timedelta(days=1)
        if psstart.weekday() > 0:
            psstart = psstart+timedelta(days=7-psstart.weekday())

        
        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="Scheduling starts..."+"\n"
       

        pssend = psstart+timedelta(days = (7*self.getSHEnd()-1) )

        if pssend.weekday() > 4:
            pssend = pssend-timedelta(days=pssend.weekday()-4)
      
        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="end weekday..."+str(pssend.weekday())+"\n" 

        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="Scheduling period..."+str(psstart)+"-"+str(pssend)+"\n"

        scheduleperiod = pd.date_range(psstart,pssend)
        
        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="Scheduling period length: "+str(len(scheduleperiod))+"\n"

        
        oprdict = dict()
        nrjobs = 0
        AllJobs = []

        #Determine customer orders with latest start within Scheduling
        SelectedOrders=[]
        for name,order in self.getDataManager().getCustomerOrders().items():
            
            if order.getLatestStart() != None: # planned ones..
              
                #if order.getLatestStart() < pssend.date():
                    
                nrjobs+=len(order.getMyJobs())
                    
                for job in order.getMyJobs():
                    job.initializeSchJob()
                    AllJobs.append(job.getSchJob())
                    if not job.getOperation() in oprdict:
                        oprdict[job.getOperation()] = []
                    oprdict[job.getOperation()].append(job.getSchJob())

                if len(order.getMyJobs()) > 0: 
                    SelectedOrders.append(order)
                    self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="Order: "+order.getName()+": "+str(len(order.getMyJobs()))+"\n"

        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" To schedule (order-based) jobs: "+str(nrjobs)+"\n"

                    
        #if batchingalg == "Simple Merge":
        #    batchalg = BaselineBatchingAlg()
        #    oprdict = batchalg.SolveBatching(oprdict,self,self.getVisualManager().getSchedulingTab().getPSchScheRes())

        #    nrjobs = 0
    
        #    for opr,jobs in oprdict.items():
        #        nrjobs+=len(jobs)
                
        #    self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" To schedule (batched) jobs: "+str(nrjobs)+"\n"
            
            
        #self.CreateJobs(psstart,ScheduleWeeks,SelectedOrders)

        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="Orders in scheduling: "+str(len(SelectedOrders))+"\n"

        for resname,res in self.getDataManager().getResources().items():
            res.getCurrentSchedule().clear()

   
        self.CreateShifts(psstart,pssend,False)

        for resname, res in self.getDataManager().getResources().items():
            res.InitializeEmptySlot()
    
        #Create Schedule; we start by checking if there are still jobs that can be scheduled  
        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="Applying shceduling algorithm... "+"\n"  
      

        if schedulealg == "Simple Greedy Insertion (Fixed)":
            greedyalg = GreedyInsertionAlg()
            self.setMyCurrentSchedule(greedyalg.SolveScheduling(AllJobs,self,self.getVisualManager().getSchedulingTab().getPSchScheRes()))
 
        if schedulealg == "Common Greedy Insertion":
            commongreedyalg = CommonGreedyInsertionAlg()
            self.setMyCurrentSchedule(commongreedyalg.SolveScheduling(AllJobs,self,self.getVisualManager().getSchedulingTab().getPSchScheRes()))

        if schedulealg == "MILP Schedule":
            algorithm = AdvancedMILPAlg()
            sch_sol = algorithm.SolveScheduling(AllJobs,self,self.getVisualManager().getSchedulingTab().getPSchScheRes())

        

        Orderstatus = []
        scheduledords = 0
        scheduledjobs = 0
        for order in SelectedOrders:
           
            jobsdone = 0
            for jb in order.getMyJobs():
                if jb.getSchJob().IsScheduled():
                    jobsdone+=1
                    scheduledjobs+=1
      
            status = "Unscheduled"
            if jobsdone == len(order.getMyJobs()):
                status = "Scheduled"
                scheduledords+=1
            else:
                if jobsdone > 0:
                    status = "Partly scheduled"
                
            
            self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=str(order.getName())+": "+str(status)+"\n"
        
            Orderstatus.append(str(order.getName())+": "+str(status))
        #myops =  [i.getName() for i in oprdict.keys()]
        #myres = [i for i in self.getDataManager().getResources().keys()]
        #self.getVisualManager().getSchedulingTab().getPSchOperations().options = myops
        self.getVisualManager().getSchedulingTab().getPSchOrderlist().options = Orderstatus
        #self.getVisualManager().getSchedulingTab().getPSchResources().options = myres


        self.getVisualManager().getSchedulingTab().getPSchSolProps().value = "Scheduled jobs: "+str(scheduledjobs)+"/"+str(len(AllJobs))+"\n"
        self.getVisualManager().getSchedulingTab().getPSchSolProps().value += "Scheduled orders: "+str(scheduledords)+"/"+str(len(SelectedOrders))+"\n"
        
        self.getVisualManager().getSchedulingTab().getPSchSolProps().value += "Machine Utilizations: "+"\n"
        
        for resname,res  in self.getDataManager().getResources().items():
            if res.getType() == "Machine":
                avg_util = 0
                nr_shfits = 0
                for shift,jobs in res.getCurrentSchedule().items():
                    job_process = 0
                    for job in jobs:
                        shiftprocess =  min(job.getCompletionTime(),shift.getEndTime()+1)-max(job.getStartTime(),shift.getStartTime())
                        job_process +=  shiftprocess
                    rel_job_process = job_process/(shift.getEndTime()-shift.getStartTime()+1)
                    avg_util = (avg_util*nr_shfits+rel_job_process)/(nr_shfits+1)
                    nr_shfits+=1
                self.getVisualManager().getSchedulingTab().getPSchSolProps().value += resname+":"+str(round(100*avg_util,2))+"%"+"\n"
                
       
        nrgroup = 1
       
                        
        self.getVisualManager().getSchedulingTab().getPSchSolProps().layout.display = 'block'
        self.getVisualManager().getSchedulingTab().getPSchSolProps().layout.visibility  = 'visible'
     

        self.getVisualManager().getSchedulingTab().getPSchOrderlist().layout.visibility  = 'hidden'
        self.getVisualManager().getSchedulingTab().getPSchOrderlist().layout.display = 'none'
       

        self.getVisualManager().getSchedulingTab().getPSTBOrdOutput().layout.visibility  = 'hidden'
        self.getVisualManager().getSchedulingTab().getPSTBOrdOutput().layout.display = 'none'
     
            
        self.getVisualManager().getSchedulingTab().getPSchResources().layout.visibility  = 'hidden'
        self.getVisualManager().getSchedulingTab().getPSchResources().layout.display = 'none'

        self.getVisualManager().getSchedulingTab().getPSTBResSchOutput().layout.visibility  = 'hidden'
        self.getVisualManager().getSchedulingTab().getPSTBResSchOutput().layout.display = 'none'

        self.getVisualManager().getSchedulingTab().getPSchResources().options = [name for name,myres in self.getDataManager().getResources().items() ]


        #self.getVisualManager().getProductionProgressTab().getResourceList().options = [name for name,myres in self.getDataManager().getResources().items() ]

        #self.getVisualManager().getProductionProgressTab().getCustomerOrderList().options = Orderstatus

        # Schedule_df = pd.DataFrame(columns = ["Resource Name","Day","Shift","Job","OperationName","Start in Shift","Completion in Shift"])
        # folder = 'UseCases'; casename = "TBRM_Volledige_Instantie"
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
        #                 jobs.sort(key=lambda x: x.getStartTime())
        #                 for job in jobs:
        #                     if job.getStartTime() >= shift.getStartTime() and job.getCompletionTime() <= shift.getEndTime():
        #                         Schedule_df.loc[len(Schedule_df)] = {"Resource Name":myres.getName(),"Day":shift.getDay(), "Shift":shift.getNumber(),"JobID":job.getID(),"OperationName":job.getOperation().getName(),"Start in Shift":job.getStartTime(),"Completion in Shift":job.getCompletionTime()}
        #                     if job.getStartTime() < shift.getStartTime() and job.getCompletionTime() <= shift.getEndTime():
        #                         Schedule_df.loc[len(Schedule_df)] = {"Resource Name":myres.getName(),"Day":shift.getDay(), "Shift":shift.getNumber(),"JobID":job.getID(),"OperationName":job.getOperation().getName(),"Start in Shift":shift.getStartTime(),"Completion in Shift":job.getCompletionTime()}
        #                     if job.getStartTime() < shift.getStartTime() and job.getCompletionTime() > shift.getEndTime():
        #                         Schedule_df.loc[len(Schedule_df)] = {"Resource Name":myres.getName(),"Day":shift.getDay(), "Shift":shift.getNumber(),"JobID":job.getID(),"OperationName":job.getOperation().getName(),"Start in Shift":shift.getStartTime(),"Completion in Shift":shift.getEndTime()}
        #                     if job.getStartTime() >= shift.getStartTime() and job.getCompletionTime() > shift.getEndTime():
        #                         Schedule_df.loc[len(Schedule_df)] = {"Resource Name":myres.getName(),"Day":shift.getDay(), "Shift":shift.getNumber(),"JobID":job.getID(),"OperationName":job.getOperation().getName(),"Start in Shift":job.getStartTime(),"Completion in Shift":shift.getEndTime()}
                    
        # filename = 'Schedules.csv'; path = folder+"\\"+casename+"\\"+filename;fullpath = os.path.join(Path.cwd(), path)
        # Schedule_df.to_csv(fullpath, index=False)                
        
        
            
        
                    
                       
                
        return 

        
       
      
        

    

  
