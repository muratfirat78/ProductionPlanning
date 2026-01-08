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
from MILPGreedyInsertion import *
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
        self.CurrentscheduleEnd = None
        self.MyShifts = dict()  # key: date, val: [shifts] 
        self.MyCurrentSchedule = None
        self.myschedules = []


    def getMySchedules(self):
        return self.myschedules

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

    def getShiftofTime(self,time):

        for date,shifts in self.getMyShifts().items(): 
            for shift in shifts:
                if (time >= shift.getStartTime()) and (time <= shift.getEndTime()):
                    return shift

        return None
    def getShiftofTime(self,time):

        for date,shifts in self.getMyShifts().items():
            
            for shift in shifts:
                #Progress.value+=" check date  "+str(date)+", shft st "+str(shift.getStartTime())+", end "+str(shift.getEndTime())+"\n"
                if (time >= shift.getStartTime()) and (time <= shift.getEndTime()):
                    return shift

        return None 
      

#######################################################################################################################################
    def ExtendShifts(self,extdate):

        earliestdate = min([x for x in self.getMyShifts().keys()])

        earliestdate = datetime(earliestdate.year, earliestdate.month,earliestdate.day)

        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="Shift extension.. earliestdate "+str(earliestdate)+"\n"
        
        curr_date = datetime(extdate.year, extdate.month,extdate.day)
        
        prev_dayshift = None 
  
        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=str(type(curr_date))+">>> "+str(type(earliestdate))+"\n"

     

        while curr_date < earliestdate:
            curr_hour = 8

            self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=str(curr_date)+">>> "+str(curr_date.date() in self.getMyShifts())+"\n"
            
            self.getMyShifts()[curr_date.date()] = []

            self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="Shifts being created for date "+str(curr_date.date())+"\n"
       
            
            for i in range(1,4):
                currenshift = Shift(curr_date,i,prev_dayshift)
                currenshift.setStartHour(curr_date + timedelta(hours=curr_hour))
                currenshift.setEndHour(curr_date + timedelta(hours=curr_hour+7)+ timedelta(minutes=59))

                self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=currenshift.String(" Ext shift :")+"\n"
    
                self.getMyShifts()[curr_date.date()].append(currenshift)  
              
                prev_dayshift = currenshift

                 
                curr_hour+=8
                for resname, res in self.getDataManager().getResources().items():
                    self.getMyCurrentSchedule().getResourceSchedules()[resname][currenshift] = dict() # key: job, vaL: (st,cp)
                    if currenshift.getNumber() in res.getAvailableShifts():
                        res.getSchedule()[currenshift] = []
                    if res.getType() == "Machine":
                        if currenshift.getNumber() == 3:
                            res.getShiftOperatingModes()[currenshift] = "Self-Running"
                        else:
                            res.getShiftOperatingModes()[currenshift] = "Operated"

               

            curr_date = curr_date+timedelta(days=1)
            
            if curr_date == earliestdate:
                self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=self.getMyShifts()[curr_date.date()][0].String(" Cnnt shift :")+"\n"
                currenshift.setNext(self.getMyShifts()[curr_date.date()][0])
                self.getMyShifts()[curr_date.date()][0].setPrevious(currenshift)


        return 
#######################################################################################################################################
    def CreateShifts(self,psstart,pssend):


        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=str(type(psstart))+">>> "+str(type(pssend))+"\n"
        

        scheduleperiod = pd.date_range(psstart,pssend)

        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" shift creating starts... "+"\n"

        Progress = self.getVisualManager().getSchedulingTab().getPSchScheRes()

        prev_dayshift = None 
        scheduletimehour = 16 # time 08:00 in half hour granularity..
        
        for curr_date in scheduleperiod:

            if curr_date.date().weekday()>= 5: # skip weekends
                continue
  
            if not curr_date.date() in self.getMyShifts(): # if shifts are already defined, we do not create. 
                curr_hour = 8
                self.getMyShifts()[curr_date.date()] = [] 
                
                for i in range(1,4):
                    currenshift = Shift(curr_date,i,prev_dayshift)
                    currenshift.setStartTime(scheduletimehour) 
                    currenshift.setStartHour(curr_date + timedelta(hours=curr_hour))
                    currenshift.setEndHour(curr_date + timedelta(hours=curr_hour+7)+ timedelta(minutes=59))

                    scheduletimehour+=15
                    currenshift.setEndTime(scheduletimehour)
                    self.getMyShifts()[curr_date.date()].append(currenshift)  
                    prev_dayshift = currenshift
                 
                    curr_hour+=8
                    scheduletimehour+=1
  
                    
                    for resname, res in self.getDataManager().getResources().items():
                        if currenshift.getNumber() in res.getAvailableShifts():
                            res.getSchedule()[currenshift] = []
                        if res.getType() == "Machine":
                            if currenshift.getNumber() == 3:
                                res.getShiftOperatingModes()[currenshift] = "Self-Running"
                            else:
                                res.getShiftOperatingModes()[currenshift] = "Operated"
           
            else:
                prev_dayshift = self.getMyShifts()[curr_date.date()][-1]

            #Progress.value+=str(curr_date)+", day shifts: "+str(len(self.getMyShifts()[curr_date]))+"\n"

       
       
        return 

###############################################################################################################################
    def UpdateSchedule(self,job):

        # remove from current schedule..
        curr_shift = job.getScheduledShift()
        compshift = job.getScheduledCompShift()

        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" updating schedule.. "+"\n"

        if curr_shift == compshift:
            del self.getMyCurrentSchedule().getResourceSchedules()[job.getScheduledResource().getName()][curr_shift][job] 
          
        else:
            while curr_shift!= compshift:
               
                if (curr_shift.getEndHour() >= job.getScheduledShift().getEndHour()) and (curr_shift.getStartHour() <= compshift.getStartHour()):
                    self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=str(job in self.getMyCurrentSchedule().getResourceSchedules()[job.getScheduledResource().getName()][curr_shift])+"\n"
                    del self.getMyCurrentSchedule().getResourceSchedules()[job.getScheduledResource().getName()][curr_shift][job] 
                  
                curr_shift = curr_shift.getNext()
                if not curr_shift in job.getScheduledResource().getSchedule():
                    curr_shift = curr_shift.getNext()
                if curr_shift == None:
                    break

                    
            self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=compshift.String("comp shiftt: ")+"\n"
            #self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" check: "+str(job in self.getMyCurrentSchedule().getResourceSchedules()[job.getScheduledResource().getName()][compshift])+"\n"    
            if job in self.getMyCurrentSchedule().getResourceSchedules()[job.getScheduledResource().getName()][compshift]:
                del self.getMyCurrentSchedule().getResourceSchedules()[job.getScheduledResource().getName()][compshift][job] 
                self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=compshift.String("****rmv shiftt: ")+"\n"

        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" job removed from schedule.. "+"\n"

        

        curr_shift = job.getActualStartShift()
        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=curr_shift.String("curr shft: ")+"\n"

        processtime = math.ceil(job.getJob().getQuantity()*job.getJob().getOperation().getProcessTime('min')) 
    
        curr_time = job.getActualStart()

        while processtime > 0:
            self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=curr_shift.String("curr shft: ")+"\n"

            self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=str(type(curr_shift.getEndHour()))+" >> "+str(type(curr_time))+"\n"
            self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=str(curr_shift.getEndHour() - curr_time)+"\n"
            self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=str(processtime)+"\n"
            processinshift = min(processtime,(curr_shift.getEndHour() - curr_time).total_seconds()/60)
            self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="processinshift: "+str(processinshift)+"\n"
            start = int((curr_time - curr_shift.getStartHour()).total_seconds()/1800) 
            
            completion = None
            processtime-=processinshift
            if processtime > 0:
                completion = math.ceil((curr_shift.getEndHour() - curr_shift.getStartHour()).total_seconds()/1800) 
                self.getMyCurrentSchedule().getResourceSchedules()[job.getScheduledResource().getName()][curr_shift][job]= (start,completion)
                curr_shift=curr_shift.getNext()
                if not curr_shift in job.getScheduledResource().getSchedule():
                    curr_shift=curr_shift.getNext()
                curr_time=curr_shift.getStartHour()
            else: 
                completion = start+math.ceil(processinshift/30) 
                self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="===>>> start: "+str(start)+", completion: "+str(completion)+"\n"
                self.getMyCurrentSchedule().getResourceSchedules()[job.getScheduledResource().getName()][curr_shift][job]= (start,completion)
                
        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" job added to schedule.. "+"\n"       

        return 
##############################################################################################################################        
    def getAlternativeResources(self,job):

        alternatives = []

        for res in job.getJob().getOperation().getRequiredResources():
            alternatives.append(res) 
            for alt in res.getAlternatives():
                if not alt in alternatives:
                    alternatives.append(alt)

        return alternatives
##################################################################################################################################
    def ApplySchedule(self,myschedule):

        # reset job properties
        for resource,jobs in myschedule.getResourceJobs().items():
            for job in jobs:
                job.resetSchedule()
              
        # empty the current schedule..
        for resname, res in self.getDataManager().getResources().items():
            # get the schedule solution for this resource
            res_schedule = myschedule.getResourceSchedules()[resname]
            for shift in res.getSchedule().keys():
                #reset jobs in the shift
                res.getSchedule()[shift].clear()
                # get the jobs in the current shift of the schedule
                for job,timetuple in res_schedule[shift].items():
                    res.getSchedule()[shift].append(job)
                    job.updateScheduledStart(shift,timetuple[0])
                    job.updateScheduledCompletion(shift,timetuple[1])
                    
       
        self.getDataManager().setScheduleStartWeek(myschedule.getStartWeek())
        self.getDataManager().setScheduleEndWeek(myschedule.getEndWeek())
        self.setMyCurrentSchedule(myschedule) 

        return 
#################################################################################################################################
    def CheckScheduleFeasibility(self,myschedule):
        """
        Feasibility points checked:
        1- No job start in shift 3
        2- Machines process at most one job at any time
        3- A job is processed by at most one job, if scheduled. 
        4- Jobs are processed at compatible machines
        5- Job processings should respect FTE capacity in Shifts 1 and 2 
        6- Job precedences 
               
        """
        infeasibilities = [] # feasibility explanations
        jobassignnments = dict() #key: job, val: [resources] musdt be only one
        shiftjobs = dict() # key: shift, val: [jobs]

        selectedtype = self.getDataManager().getProcessTypes()[0]

        for currdate, shifts in self.getMyShifts().items():
            for shift in shifts: 
                shiftjobs[shift] = []

        # reset job properties
        for name,order in self.getDataManager().getCustomerOrders().items():
          
            for job in order.getMyJobs():
                if job.getMySch() != None:
                    if job.getMySch().IsScheduled():
                        for pred in job.getPredecessors():
                            if pred.getMySch() == None:
                                infeasibilities.append(">>Infeasibility 6: "+job.getName()+" has predecessor "+pred.getName()+" not schedule job intialized")
                            else:
                                if not pred.getMySch().IsScheduled():
                                    infeasibilities.append(">>Infeasibility 6: "+job.getName()+" has predecessor "+pred.getName()+" not scheduled")
                                else: 
                                    if pred.getMySch().getCompletionTime() > job.getMySch().getStartTime():
                                        infeasibilities.append(">>Infeasibility 6: "+job.getName()+" has predecessor completion  "+str(pred.getMySch().getCompletionTime())+" > job start "+str(job.getMySch().getStartTime()))
                                        
                            
                    if not job in jobassignnments:
                        jobassignnments[job.getMySch()] = []

        for resname, res in self.getDataManager().getResources().items():
            # get the schedule solution for this resource
            res_schedule = myschedule.getResourceSchedules()[resname]
            for shift in res.getSchedule().keys():
                for job,timetuple in res_schedule[shift].items():
                    
                    shiftjobs[shift].append(job)
                    if (shift.getNumber() == 3) and (job.getStartTime() >= shift.getStartTime()):
                        infeasibilities.append(">>Infeasibility 1: "+job.getJob().getName()+"("+str(timetuple)+")"+" starts in shift3 "+shift.String("shift3 ")+" at resource "+resname)
                    if not res in jobassignnments[job]:
                        jobassignnments[job].append(res)
                    for job2,timetuple2 in res_schedule[shift].items():
                        if job == job2: 
                            continue
                        if timetuple[1] <= timetuple2[0] or timetuple2[1] <= timetuple[0]:
                            continue
                        infeasibilities.append(">>Infeasibility 2: "+job.getJob().getName()+"("+str(timetuple)+")"+" processing has overlap with "+job2.getJob().getName()+"("+str(timetuple2)+")"+" in resource "+resname)
                        

   
        for job,resources in jobassignnments.items():
            if len(resources) > 1: 
                infeasibilities.append(">>Infeasibility 3: Job"+job.getJob().getName()+" is assigned to multiple resources: "+str(resources))
            else:
                if len(resources) == 1:
                    alternatives = self.getAlternativeResources(job)
                    machine = resources[0]
                    if not machine in alternatives:
                        infeasibilities.append(">>Infeasibility 4:"+job.getJob().getName()+" with op "+job.getJob().getOperation().getName()+"  is assigned to incompatible resource "+str(machine.getName()))

        for shift,jobsofshift in shiftjobs.items():
            if shift.getNumber() == 3:
                continue
           
            ftecapacity = self.getDataManager().getFTECapacity(selectedtype,shift) # no.man
            ftecapacity*=(shift.getEndTime()-shift.getStartTime()+1) # no. man-halfhour

            fteuse = 0

            for job in jobsofshift:
                shstarttime = max(shift.getStartTime(),job.getStartTime())
                shendtime = min(shift.getEndTime(),job.getCompletionTime())
                fteuse+= job.getScheduledResource().getOperatingEffort()*(shendtime-shstarttime)
            if fteuse > ftecapacity:
                infeasibilities.append(">>Infeasibility 5: Shift"+shift.String(" fte shift ")+" has fteuse "+str(fteuse)+" > ftecapacity "+str(ftecapacity))
            

        return infeasibilities
##################################################################################################################################
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

############################################################################################################################
    def ScheduleJob(self,job,res,starttime,completiontime,schsol,Progress):

        """
        Scheduling a job involves the following points: 
          - set the following properties: resource, scheduled boolean as true, start time, completion time, scheduled start shift, scheduled completion shift.
          - place the job into relevant job lisft of the resource in the scheduling solution. 
          
        """
        
        Progress.value+= "Job: "+job.getJob().getName()+", scheduled on mach "+res.getName()+" st/cp "+str(starttime)+"/"+str(completiontime)+"\n" 
        
        job.SetScheduled()
        job.setScheduledResource(res)
                
        job.setStartTime(starttime) 
        stshift = self.getShiftofTime(starttime)
        
        job.setScheduledShift(stshift)
        job.setCompletionTime(completiontime)

        cpshift = self.getShiftofTime(completiontime)

        if not res in schsol.getResourceJobs():
            schsol.getResourceJobs()[res] = []
        
        schsol.getResourceJobs()[res].append(job)
        
        curr_shift = stshift
        while curr_shift!= None: 
            shiftst = max(starttime,curr_shift.getStartTime())-curr_shift.getStartTime()
            shiftcp = min(completiontime,curr_shift.getEndTime())-curr_shift.getStartTime()
            
            schsol.getResourceSchedules()[res.getName()][curr_shift][job] = (shiftst,shiftcp)
            if curr_shift == cpshift:
                break
                
            curr_shift = curr_shift.getNext()
            
            if curr_shift == None: 
                break
                
            if not curr_shift in res.getSchedule():
                curr_shift=curr_shift.getNext()
         
        job.setScheduledCompShift(cpshift)
                    

        return
############################################################################################################################
############################################################################################################################
    def MakeSchedule(self,schedulealg,batchingalg):
        
        psstart = self.getSHStart()
        psstart = psstart.replace(hour=0, minute=0, second=0, microsecond=0)+ timedelta(days=1)
        
        if psstart.weekday() > 0:
            psstart = psstart+timedelta(days=7-psstart.weekday())
 
        pssend = psstart+timedelta(days = (7*self.getSHEnd()-1) )

        if pssend.weekday() > 4:
            pssend = pssend-timedelta(days=pssend.weekday()-4)


        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="Scheduling period..."+str(psstart)+"-"+str(pssend)+"\n"

        scheduleperiod = pd.date_range(psstart,pssend)
    

        AllJobs = []; SelectedOrders=[]

        existings = 0
        for name,order in self.getDataManager().getCustomerOrders().items():
            
            if len(order.getMyJobs()) > 0:
                if order.getPlannedDelivery() != None: # planned ones..
                    self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="Planned order: "+str(name)+"\n"
    
                    for job in order.getMyJobs():
                        if job.getMySch()!= None:
                            if job.getMySch().getActualStart()!= None:
                                if job.getMySch().getActualCompletion()!= None:
                                    continue
                                #else: 
                                #    if job.getMySch().getActualStart()+timedelta()
                                    
                        job.backupSch()
                        AllJobs.append(job.getMySch()) #a clean sch inserted, previous one: job.getJob().getPrevSch()

                    SelectedOrders.append(order)
                    self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="Order: "+order.getName()+": "+str(len(order.getMyJobs()))+"\n"
                    self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="LS: "+str(order.getLatestStart())+"\n"

        prevscheduled = len([x for x in AllJobs if x.getJob().getPrevSch() != None])

        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Prev.scheduled jobs: "+str(prevscheduled)+"/"+str(len(AllJobs))+")"+"\n"           
        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="Orders in scheduling: "+str(len(SelectedOrders))+"\n"

        self.CreateShifts(psstart,pssend)

        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" shifts created.."+"\n"
            

        sch_sol = None
        if schedulealg == "MILP-based Greedy Insertion":
            algorithm = MILPGreedyInsertionAlg()
            algorithm.setNoMatches(5)
            sch_sol = algorithm.SolveScheduling(AllJobs,self,self.getVisualManager().getSchedulingTab().getPSchScheRes(),psstart,pssend)
            self.getMySchedules().append(sch_sol) 
            infeasibles = self.CheckScheduleFeasibility(sch_sol)
            self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="Feasibility check: Infeasibles "+str(len(infeasibles))+"\n" 
            for reason in infeasibles:
                 self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=reason+"\n" 
            
            if len(infeasibles) == 0:
                self.ApplySchedule(sch_sol)
        

        self.getVisualManager().getSchedulingTab().getPSchTBmakesch_btn().disabled = True
        self.getVisualManager().getSchedulingTab().getPSchTBaccsch_btn().disabled = False
        
       
        scheduledords = len([o for o in SelectedOrders if o.getStatus() == "Scheduled" ])
        scheduledjobs = len([j for o in SelectedOrders for j in o.getMyJobs() if j.getMySch().IsScheduled()])
        for order in SelectedOrders:
            self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=str(order.getName())+": "+str(order.getStatus())+"\n"

        self.getVisualManager().getSchedulingTab().getPSchOrderlist().options = [o.getStatus() for o in SelectedOrders]
        self.getVisualManager().getSchedulingTab().getPSchSolProps().value = "Scheduled jobs: "+str(scheduledjobs)+"/"+str(len(AllJobs))+"\n"
        self.getVisualManager().getSchedulingTab().getPSchSolProps().value += "Scheduled orders: "+str(scheduledords)+"/"+str(len(SelectedOrders))+"\n"
        
        self.getVisualManager().getSchedulingTab().getPSchSolProps().value += "Machine Utilizations: "+"\n"
        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="Calculating machine utilizations.. "+"\n" 
        
        for resname,res  in self.getDataManager().getResources().items():
            if res.getType() == "Machine":
                avg_util = 0
                nr_shfits = 0
                for shift,jobs in res.getSchedule().items():
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


        self.getVisualManager().getSchedulingTab().getPSchResources().options = [name for name,myres in self.getDataManager().getResources().items() ]
            
                
        return 

        
       
      
        

    

  
