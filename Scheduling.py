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

    def DefineJobPrecedences(self):

        oprdict = dict() # key: operation, #val: set of jobs

     # Collect operations with jobs
        nrjobs = 0
        for prname,prod in self.getDataManager().getProducts().items():
            for opr in prod.getOperations():
                if not opr in oprdict:
                    oprdict[opr] = opr.getJobs()
                    nrjobs+= len(opr.getJobs())

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

        return nrjobs,oprdict

  

    def FineTuneOrderDeliveries(self):

        mydict = self.getDataManager().getCustomerOrders()
        sortedtuples = sorted(mydict.items(), key=lambda item: item[1].getDeadLine())
        mydict = {k: v for k, v in sortedtuples}
        self.getDataManager().setCustomerOrders(mydict)

        for ordname,myord in self.getDataManager().getCustomerOrders().items():
            curr_product = myord.getProduct()

            #while curr_product.getSuccessor != None:
                
                
                


        return 


    def UpdateJobLS(self,job,pushdays):

        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="push days: "+str(pushdays)+"\n"
        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" job->"+str(job.getName())+", LS: "+str(job.getLatestStart())+"\n"
        job.setLatestStart(job.getLatestStart().date()+timedelta(days = pushdays))
        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="*new LS->"+str(job.getLatestStart())+"\n"
        job.setDeadLine(job.getDeadLine().date()+timedelta(days = pushdays))
        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="*new D->"+str(job.getDeadLine())+"\n"
        
        for jsuccessor in job.getSuccessor():
            self.UpdateJobLS(jsuccessor,pushdays)

        return

    def JobLatestStarts(self,psstart):

        
        for oprname,opr in self.getDataManager().getOperations().items():
  
            for job in opr.getJobs():
                
                if len(job.getPredecessors()) == 0: # root job 
                   
                    if job.getLatestStart().date() < psstart:
                        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Root job->"+str(job.getName())+", LS: "+str(job.getLatestStart())+"\n"
                        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" types->"+str(type(psstart))+"-"+str(type(job.getLatestStart()))+"\n"
                        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" PSSTART->"+str(psstart)+"\n"

                        
                        pushdays = (psstart-job.getLatestStart().date()).days
                        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="to updatejobLS...push days "+str(pushdays)+"\n"
                        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="Successors.. "+str(len(job.getSuccessor()))+"\n"
                        self.UpdateJobLS(job,pushdays)
                                      
        return

    
    
    def CreateJobs(self,psstart,scheduleweeks,Orders):

        if self.isJobCreated():
            return


        pssend= psstart+timedelta(days=14*scheduleweeks)
        
        #grab the required products and their predecessors for the possible orders
        ListOfProd = []        
        for i in Orders:
            Product = i.getProduct()
            PredProduct = i.getProduct().getPredecessors()[0]
            ListOfProd.append(Product)
            ListOfProd.append(PredProduct)
            while PredProduct.getPredecessors() != []:
                PredProduct = PredProduct.getPredecessors()[0]
                ListOfProd.append(PredProduct)

        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="Creating jobs..."+"\n"
        opslist = []
        
        #for prname,prod in self.getDataManager().getProducts().items():
        for prod in ListOfProd:
            prod = self.getDataManager().getProducts()[prod.getName()]
          
            produced_level = 0
            orginalList = prod.getOperations()

            if len(orginalList) == 0:
                continue

            reversed_ops = orginalList[::-1]  

   
            #demandcurve = list([(ddate,amount) for ddate,amount in prod.getTargetLevels().items() if ddate <= pssend])
            demandcurve = list([(date,level) for date,level in prod.getTargetLevels().items() if pd.Timestamp(date) <= pd.Timestamp(pssend)])

            totaldmd = 0
            if len(demandcurve) > 0:
                totaldmd=[val for dt,val in demandcurve][-1]

            if totaldmd == 0:
                continue

            opslist.append(prod.getName()) 
            #self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Prod->"+str(prod.getName())+", dmd: "+str(totaldmd)+"\n"
            #self.getVisualManager().getPLTBresult2exp().value+=" Pr "+prod.getName()+", Trglvls: "+str(len(prod.getTargetLevels()))+", No.Ops: "+str(len(prod.getOperations()))+".."+", dmd: "+str(totaldmd)+", size: "+str(len(demandcurve))+"\n"

            #self.getVisualManager().getPLTBresult2exp().value+="Initial demand curve: "+str([val for dt,val in demandcurve])+"\n"

            prev_opr = None
            prodbatchsize = prod.getChosenBatchsize()
            #self.getVisualManager().getPLTBresult2exp().value+="HOI "+str(prod)+"\n"
            for operation in reversed_ops:

                oprbtchsize = operation.getBatchSize()
                prev_job = None
                # self.getVisualManager().getSchedulingTab().getPLTBresult2exp().value+="> Opr: "+str(operation.getName())+"\n"
          
                if not prev_opr is None:
                    orgjoblist = prev_opr.getJobs()
                    reversed_jobs = orgjoblist[::-1]  

                    totaljobsize = 0
                    cum_jobneed = 0
                    valiter = 0
                    for job in reversed_jobs:
                        valiter+=1
                        cum_jobneed+=job.getQuantity()

                        #self.getVisualManager().getSchedulingTab().getPLTBresult2exp().value+="SuccJob "+job.getName()+", q "+str(job.getQuantity())+", d "+str(job.getDeadLine())+"\n"
                        if (cum_jobneed - totaljobsize >= prodbatchsize) or ((valiter == len(reversed_jobs)) and (cum_jobneed - totaljobsize > 0 ) ):
                            jobsize =prodbatchsize*((cum_jobneed - totaljobsize)//prodbatchsize)+prodbatchsize*int((cum_jobneed - totaljobsize)%prodbatchsize > 0)   

                            deadline = job.getLatestStart()
                            #self.getVisualManager().getPLTBresult2exp().value+=" job to create "+operation.getName()+", "+str(val)+":"+str(totaljobsize)+", q: "+str(jobsize)+", BTCH: "+str(prodbatchsize)+", proctime "+str(operation.getProcessTime())+", iter: "+str(valiter)+", dl "+str(deadline)+"\n" 

                   
                            jobid = self.getDataManager().getJobID()
                            myjob =  Job(jobid,"Job_"+str(jobid),prod,operation,jobsize,deadline)

                            outsourced = False
                            for resource in operation.getRequiredResources():
                                myresource = resource
                                if isinstance(resource,list):
                                    myresource = resource[0]
                                if myresource.IsOutsource():
                                    outsourced = True
                                    break

                            if not outsourced:
                                myjob.setLatestStart(myjob.getDeadLine() - timedelta(hours = jobsize*operation.getProcessTime()))
                            else:
                                myjob.setLatestStart(myjob.getDeadLine() - timedelta(hours = operation.getProcessTime()))
                            #self.getVisualManager().getPSchScheRes().value+=" >> "+myjob.getName()+", q: "+str(myjob.getQuantity())+", d: "+str(myjob.getDeadLine())+"\n" 

                            totaljobsize+=jobsize
                            operation.getJobs().insert(0,myjob)
                         
         
                else:
                    valiter = 0
                    newdmdcurve = []
                    newval = 0
                    for mydate,val in demandcurve:
                        valiter+=1
                        totaljobsize = 0
                        
                        if len(operation.getJobs()) > 0:
                            totaljobsize = sum([jb.getQuantity() for jb in operation.getJobs()])
                            
    
                        if (val - totaljobsize >= prodbatchsize) or ((demandcurve[-1][1] == val) and (val - totaljobsize > 0 ) ):
    
                           
                            jobsize =prodbatchsize*((val - totaljobsize)//prodbatchsize)+prodbatchsize*int((val - totaljobsize)%prodbatchsize > 0)  
                            deadline = datetime.combine(mydate, time(0, 0, 0)) #hr/min/sec

                            
    
                            #self.getVisualManager().getPLTBresult2exp().value+=" job to create "+operation.getName()+", "+str(val)+":"+str(totaljobsize)+", q: "+str(jobsize)+", BTCH: "+str(prodbatchsize)+", proctime "+str(operation.getProcessTime())+", iter: "+str(valiter)+", dl "+str(deadline)+"\n" 
                            jobid = self.getDataManager().getJobID()
                            myjob =  Job(jobid,"Job_"+str(jobid),prod,operation,jobsize,deadline)

                            outsourced = False
                            for resource in operation.getRequiredResources():
                                myresource = resource
                                if isinstance(resource,list):
                                    myresource = resource[0]
                                if myresource.IsOutsource():
                                    outsourced = True
                                    break
     
                            if not outsourced:
                                #self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" deadline >"+str(myjob.getDeadLine())+"\n"
                                myjob.setLatestStart(myjob.getDeadLine() - timedelta(hours = jobsize*operation.getProcessTime()))
                                #self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" lateststart >"+str(myjob.getLatestStart())+"\n"
                            else: 
                                myjob.setLatestStart(myjob.getDeadLine() - timedelta(hours = operation.getProcessTime()))
                            #self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" >> "+myjob.getName()+", q: "+str(myjob.getQuantity())+", d: "+str(myjob.getDeadLine())+"\n" 
                            newval+=jobsize
    
                            #self.getVisualManager().getPLTBresult2exp().value+=" Job->"+str(prod.getName())+", "+str(operation.getName())+", Q:"+str(jobsize)+"\n"
                            operation.getJobs().append(myjob)
                            prev_job = myjob

                        
                    newdmdcurve.append((mydate,newval))

                
                demandcurve = newdmdcurve
                prev_opr = operation
                

        #self.getVisualManager().getPLTBCheckRaw().value = 
        # self.getVisualManager().getPLTBresult2exp().value+="-> Products"+str(len(opslist))+"\n"
        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="Job creation completed.."+"\n"
        #self.getVisualManager().getSchedulingTab().getPSchResources().options = [op.getName() for op in opslist]

        self.setJobCreated()             
        
        return

    def MakeSchedule(self,b):


        psstart = self.getSHStart()

        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="Scheduling starts..."+"\n"
       

        ScheduleWeeks = ((self.getSHEnd()-self.getSHStart()).days)//7 # weeks

        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="ScheduleWeeks..."+str(ScheduleWeeks)+"\n"
       
        
        pssend= self.getSHEnd()

        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="Scheduling period..."+str(psstart)+"-"+str(pssend)+"\n"

        #Determine customer orders with latest start within Scheduling
        SelectedOrders=[]
        for name,order in self.getDataManager().getCustomerOrders().items():
            if not order.getLatestStart() is None:
                if order.getLatestStart().date() <= pssend:
                    SelectedOrders.append(order)
                
        self.CreateJobs(psstart,ScheduleWeeks,SelectedOrders)

        

        for resname,res in self.getDataManager().getResources().items():
            res.getSchedule().clear()

        nrjobs,oprdict = self.DefineJobPrecedences()
           
        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" To schedule jobs: "+str(nrjobs)+"\n"

        self.JobLatestStarts(psstart)
      
         #Initialize shifts (example 30 days?)
        day = 7*ScheduleWeeks;
        
        i=1;
        shiftlistman=[]
        shiftlistaut=[]

        

        for scheduleday in pd.date_range(psstart,pssend):
            self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="Schedule day"+str(scheduleday)+", "+str(self.weekdays[scheduleday.weekday()])+"\n"
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
        AllJobs = dict()
        SchedulableJobs=[]
        self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="TEST"+str(SchedulableJobs)+"\n"
        ScheduledJobs=dict()
        for opr, jobs in oprdict.items():
            for job in jobs:
                if job.getPredecessors() == []:
                    SchedulableJobs.append(job)
                AllJobs[job.getName()]=job;
        counter = 0       
        #Initialize schedule for each Resource:
        for resname, res in self.getDataManager().getResources().items():
            if ((res.getAutomated() is None) or (res.getAutomated()==False)) and not res.getType()=='Outsourced':
                for i in shiftlistman:
                    res.getSchedule()[i]=[]
            else:
                for i in shiftlistaut:
                    res.getSchedule()[i]=[]
        
        #Create Schedule   
        while len(SchedulableJobs) >0:
            for j in SchedulableJobs:
                self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Scheduling job "+str(j.getName())+"\n"               
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

                            if shift.getDay() > day:
                                self.getVisualManager().getSchedulingTab().getPSchScheRes().value+=" Job "+str(j.getName())+" cannot be scheduled on resource "+str(r.getName())+" Within the scheduling horizon of "+ str(day)+" days. \n"
                                SchedulableJobs.remove(j) #Remove scheduled job
                                break
                            
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
        self.getVisualManager().getSchedulingTab().getPSchOperations().options = myops
        self.getVisualManager().getSchedulingTab().getPSchOrderlist().options = Orderstatus
            

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

        
       
      
        

    

  
