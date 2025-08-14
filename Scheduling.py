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
from AdvancedGreedyInsertion import *
from SimpleBatching import *

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

    def CalculateFTEUse(self,res,shift):

        totalfte = 0

        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" fte calculations..  "+res.getName()+"> "+str(res.getType())+"\n"

            
        machine = res

        if machine.getMachineGroup() == None:
            return totalfte
        if machine.getMachineGroup().getOperatingTeam() == None:
            return totalfte
            
        for mach in machine.getMachineGroup().getMachines():
            if shift in mach.getSchedule():
                for job in mach.getSchedule()[shift]:
                    machhrprocesstime = min(shift.getEndTime()+1,job.getCompletionTime())-max(shift.getStartTime(),job.getStartTime()) #mach-hours
                    manhourprocesstime = machhrprocesstime*mach.getOperatingEffort()
                    totalfte+=manhourprocesstime/(shift.getEndTime()-shift.getStartTime()+1)

        return totalfte

   

    def MakeSchedule(self,schedulealg,batchingalg):
      

        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="Scheduling  : "+str(batchingalg)+"\n"

        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="Batching  : "+str(batchingalg)+"\n"

        
        psstart = self.getSHStart()

        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="Scheduling starts..."+"\n"
       

        ScheduleWeeks = ((self.getSHEnd()-self.getSHStart()).days)//7 # weeks

        #self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="ScheduleWeeks..."+str(ScheduleWeeks)+"\n"
       
        
        pssend= self.getSHEnd()

        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="Scheduling period..."+str(psstart)+"-"+str(pssend)+"\n"

        scheduleperiod = pd.date_range(psstart,pssend)
        
        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="Scheduling period length: "+str(len(scheduleperiod))+"\n"

        
      
        oprdict = dict()
        nrjobs = 0

        #Determine customer orders with latest start within Scheduling
        SelectedOrders=[]
        for name,order in self.getDataManager().getCustomerOrders().items():
            if order.getLatestStart() != None:
                if order.getLatestStart().date() < pssend:
                    nrjobs+=len(order.getMyJobs())
                    for job in order.getMyJobs():
                        if not job.getOperation() in oprdict:
                            oprdict[job.getOperation()] = []
                        oprdict[job.getOperation()].append(job)
                        
                    SelectedOrders.append(order)
                    #self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="Order: "+order.getName()+": "+str(len(order.getMyJobs()))+"\n"

        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" To schedule (order-based) jobs: "+str(nrjobs)+"\n"

        if batchingalg == "Simple Merge":
            batchalg = BaselineBatchingAlg()
            oprdict = batchalg.SolveBatching(oprdict,self,self.getVisualManager().getSchedulingTab().getPSchScheRes())

            nrjobs = 0
    
            for opr,jobs in oprdict.items():
                nrjobs+=len(jobs)
                
            self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" To schedule (batched) jobs: "+str(nrjobs)+"\n"
            
            
        #self.CreateJobs(psstart,ScheduleWeeks,SelectedOrders)

        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="Orders in scheduling: "+str(len(SelectedOrders))+"\n"

        for resname,res in self.getDataManager().getResources().items():
            res.getSchedule().clear()

        #nrjobs,oprdict = self.DefineJobPrecedences(SelectedOrders)
           
       
         #Initialize shifts (example 30 days?)
        scheduldays = 7*ScheduleWeeks;
   
        #for scheduleday in pd.date_range(psstart,pssend):
            #self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="Schedule day"+str(scheduleday)+", "+str(self.weekdays[scheduleday.weekday()])+"\n"
        

        #Initialize Schedulable Jobs

        AllJobs = []
        SchedulableJobs= [] 

        # Fill the Schedulable Jobs List
        for opr, jobs in oprdict.items():
            for job in jobs:
                AllJobs.append(job)
                if job.IsSchedulable():
                    SchedulableJobs.append(job)
                else:
                    if len(job.getPredecessors()) == 0:
                        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="No-sch job: "+str(len(opr.getName()))+"\n"

        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="SchedulableJobs: "+str(len(SchedulableJobs))+"\n"

       
              
        i=1
        prev_dayshift = None 
        scheduletimehour = 1
        
        for curr_date in scheduleperiod:
            
            shift1=Shift(curr_date,3,prev_dayshift)
            shift1.setStartTime(scheduletimehour)  

            shift1.setStartHour(curr_date + timedelta(hours=0))
            shift1.setEndHour(curr_date + timedelta(hours=7)+ timedelta(minutes=59))
          
            scheduletimehour+=8
            shift1.setEndTime(scheduletimehour-1)
            shift2=Shift(curr_date,1,shift1)
            shift2.setStartTime(scheduletimehour)   
            scheduletimehour+=8
            shift2.setEndTime(scheduletimehour-1)

            shift2.setStartHour(curr_date + timedelta(hours=8))
            shift2.setEndHour(curr_date + timedelta(hours=15)+timedelta(minutes=59))

            
            shift3=Shift(curr_date,2,shift2)
            shift3.setStartTime(scheduletimehour)
            scheduletimehour+=8
            shift3.setEndTime(scheduletimehour-1)
            shift3.setStartHour(curr_date + timedelta(hours=16))
            shift3.setEndHour(curr_date + timedelta(hours=23)+ timedelta(minutes=59))
            
            prev_dayshift=shift3

            opno = 0
            for resname, res in self.getDataManager().getResources().items():

                #self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=str(curr_date)+", res.. "+str(res.getName())+"\n"

                if res.getType() == "Machine":

                    res.getShiftAvailability()[shift1] = res.IsAutomated() 
                    #self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=str(curr_date)+"shift1 - available: "+str( res.getShiftAvailability())+"\n"
                    if res.getShiftAvailability()[shift1]:
                        res.getSchedule()[shift1] = []
                        res.getShiftOperatingModes()[shift1] = "Self-Running"

                    
                    res.getShiftAvailability()[shift2] = True
                   
                    res.getSchedule()[shift2] = []
                    res.getShiftOperatingModes()[shift2] = "Operated"
                    
                    res.getShiftAvailability()[shift3] = True
                    
                    res.getSchedule()[shift3] = []
                    res.getShiftOperatingModes()[shift3] = "Operated"
                  

                if res.getType() == "Manual":
                    res.getShiftAvailability()[shift1] = False
                    res.getShiftAvailability()[shift2] = True
                    res.getSchedule()[shift2] = []
                    res.getShiftAvailability()[shift3] = True
                    res.getSchedule()[shift3] = []
                    
                if res.getType() == "Operator":
                    res.getShiftAvailability()[shift1] = False
                    
                    res.getShiftAvailability()[shift2] = True
                    res.getSchedule()[shift2] = []
                    res.getShiftAvailability()[shift3] = True
                    res.getSchedule()[shift3] = []

                 
          
                if res.getType() == "Outsourced":
                    res.getShiftAvailability()[shift1] = True
                    res.getSchedule()[shift1] = []
                    res.getShiftAvailability()[shift2] = True
                    res.getSchedule()[shift2] = []
                    res.getShiftAvailability()[shift3] = True
                    res.getSchedule()[shift3] = []
                    
                 
                
                # for slot in res.getEmptySlots():
                #     self.getVisualManager().getSchedulingTab().getPSchScheRes().value+= res.getName()+str(slot[0][0])+","+slot[0][1]+"\n"  
                    
            i+=1        

        #self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="shift creation completed.."+"\n"
        for resname, res in self.getDataManager().getResources().items():
            if res.getName() == "M4-01 - Accuwell -  4axis - Conveyor automation (FR4_01)":
                for shift,jobs in res.getSchedule().items():
                    self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Sh:("+str(shift.getDay())+","+str(shift.getNumber())+"), hrs: ["+str(shift.getStartTime())+"-"+str(shift.getEndTime())+"]\n" 
                    
                displayed = True

            #self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="initializing empty slots for "+res.getName()+"\n"
            res.InitializeEmptySlot()
            for slot in res.getEmptySlots():  
                self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="Res:"+res.getName()+", Slot: St: "+str(slot[0][0])+", l: "+str(slot[0][1])+", Shft: ("+str(slot[1].getDay())+","+str(slot[1].getNumber())+")"+"\n" 
                
        #Create Schedule; we start by checking if there are still jobs that can be scheduled  
        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" starting... "+"\n"  
      

        if schedulealg == "Simple Greedy Insertion":
            greedyalg = GreedyInsertionAlg()
            greedyalg.SolveScheduling(AllJobs,self,self.getVisualManager().getSchedulingTab().getPSchScheRes())
        if schedulealg == "Advanced Greedy Insertion":
            advncdgreedyalg = AdvancedGreedyInsertionAlg()
            advncdgreedyalg.SolveScheduling(AllJobs,self,self.getVisualManager().getSchedulingTab().getPSchScheRes())
            

        Orderstatus = []
        scheduledords = 0
        for order in SelectedOrders:
            self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=str(order.getName())+": "+str(order.getStatus())+"\n"
            if order.getStatus() == "Scheduled":
                scheduledords+=1
                
            Orderstatus.append(str(order.getName())+": "+str(order.getStatus()))
        #myops =  [i.getName() for i in oprdict.keys()]
        #myres = [i for i in self.getDataManager().getResources().keys()]
        #self.getVisualManager().getSchedulingTab().getPSchOperations().options = myops
        self.getVisualManager().getSchedulingTab().getPSchOrderlist().options = Orderstatus
        #self.getVisualManager().getSchedulingTab().getPSchResources().options = myres

        


        self.getVisualManager().getSchedulingTab().getPSchSolProps().value = "Scheduled jobs: "+str(sum([int(j.IsScheduled()) for j in AllJobs]))+"/"+str(len(AllJobs))+"\n"
        self.getVisualManager().getSchedulingTab().getPSchSolProps().value += "Scheduled orders: "+str(scheduledords)+"/"+str(len(SelectedOrders))+"\n"
        
        self.getVisualManager().getSchedulingTab().getPSchSolProps().value += "Machine Utilizations: "+"\n"
        
        for resname,res  in self.getDataManager().getResources().items():
            if res.getType() == "Machine":
                #self.getVisualManager().getSchedulingTab().getPSchSolProps().value += resname+":"+"\n"
                avg_util = 0
                nr_shfits = 0
                for shift,jobs in res.getSchedule().items():
                    #self.getVisualManager().getSchedulingTab().getPSchSolProps().value+=" Shift: ("+str(shift.getDay())+","+str(shift.getNumber())+"): "+str(shift.getStartTime())+"-"+str(shift.getEndTime())+"\n" 
                    job_process = 0
                    for job in jobs:
                        #self.getVisualManager().getSchedulingTab().getPSchSolProps().value+=job.getName()+" > "+str(job.getStartTime())+"-"+str(job.getCompletionTime())+"\n" 
                      

                        shiftprocess =  min(job.getCompletionTime(),shift.getEndTime()+1)-max(job.getStartTime(),shift.getStartTime())
                        
                        #self.getVisualManager().getSchedulingTab().getPSchSolProps().value+=" Proc: "+str(shiftprocess)+"\n" 
                        
                        job_process +=  shiftprocess
                        
                        
                    rel_job_process = job_process/(shift.getEndTime()-shift.getStartTime()+1)
                    #self.getVisualManager().getSchedulingTab().getPSchSolProps().value+=" rel_job_process: "+str(round(rel_job_process,2))+"\n" 
    
                    avg_util = (avg_util*nr_shfits+rel_job_process)/(nr_shfits+1)
    
                    nr_shfits+=1
                self.getVisualManager().getSchedulingTab().getPSchSolProps().value += resname+":"+str(round(100*avg_util,2))+"%"+"\n"
                
        self.getVisualManager().getSchedulingTab().getPSchSolProps().value += "FTE Use of Machine Groups: "+"\n"

        nrgroup = 1
        for machgroup in self.getDataManager().getMachineGroups():
            
            autmach = None
            for checkmach in machgroup.getMachines():
                self.getVisualManager().getSchedulingTab().getPSchSolProps().value += checkmach.getName()+": "+str(checkmach.IsAutomated())+"\n"
                if checkmach.IsAutomated():
                    autmach = checkmach
                    

            if autmach != None: 
                self.getVisualManager().getSchedulingTab().getPSchSolProps().value += " Machine Group "+str(nrgroup)+"("+str(len(machgroup.getMachines()))+" machines )"+"\n"
                for shift in autmach.getSchedule():
                    totalfte = 0
                    for mach in machgroup.getMachines():
                        if shift in mach.getSchedule():
                            for job in mach.getSchedule()[shift]:
                                machhrprocesstime = min(shift.getEndTime()+1,job.getCompletionTime())-max(shift.getStartTime(),job.getStartTime()) 
                                manhourprocesstime = machhrprocesstime*mach.getOperatingEffort()
                                totalfte+=manhourprocesstime/(shift.getEndTime()-shift.getStartTime()+1)
                    ftecapacity = sum([int(shift in opr.getShiftAvailability()) for opr in machgroup.getOperatingTeam().getOperators()])
                    self.getVisualManager().getSchedulingTab().getPSchSolProps().value += "Shift ["+str(shift.getDay())+","+str(shift.getNumber())+"]: "+str(round(totalfte,2))+"/"+str(ftecapacity)+"\n"     
                        
                    
            
           
            

        
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


        self.getVisualManager().getProductionProgressTab().getResourceList().options = [name for name,myres in self.getDataManager().getResources().items() ]

        self.getVisualManager().getProductionProgressTab().getCustomerOrderList().options = Orderstatus

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

        
       
      
        

    

  
