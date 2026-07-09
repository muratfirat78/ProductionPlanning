from Simulator import *
from datetime import timedelta,date
from productionobjects import *
from productionalgs import *
from productionChecker import *
from productiondata import *
import numpy as np
import pandas as pd
from ortools.linear_solver import pywraplp
from timeit import default_timer as timer

class Job(object):
    def __init__(self,myopr,mytype,preempt,myid):
    
        self.Operation = myopr
        self.Scheduled = False
        self.Predecessor = None # to be found after contsruction. 
        self.Successor = None # to be found after contsruction. 
        self.deadline = None
        self.Start = None
        self.Completion = None
        self.Type = mytype
        self.Preemptable = preempt
        self.Name = mytype+"_"+str(myid)+"_"+str(myopr.getDemand().getFinalProduct().getPN())
        self.ID = myid
        self.MILPConstraint = None # sum(x_jm) <= 1
        self.PrecedenceConstraint = None # sum(x_j'm) <= sum(x_jm) for j -> j'
        self.PrecedenceConstraint2 = None # sum(c_{jm}x_{jm}) <= sum(st_{j'm}x_{j'm})+M*(1-sum(x_j'm))  for j -> j'
        self.Matches = []

    def getMyMatches(self):
        return self.Matches

    def getPrecedenceConstraint(self):
        return self.PrecedenceConstraint

    def getPrecedenceConstraint2(self):
        return self.PrecedenceConstraint2

    def setPrecedenceConstraint(self,mycons):
        self.PrecedenceConstraint = mycons
        return 

    def setPrecedenceConstraint2(self,mycons):
        self.PrecedenceConstraint2 = mycons
        return 

    def getMILPConstraint(self):
        return self.MILPConstraint

    def getProduct(self):
        return self.getOperation().getDemand().getFinalProduct()
        

    def setMILPConstraint(self,mycons):
        self.MILPConstraint = mycons # sum_{j,m}x_jm <= 1


    def isPreemptable(self):
        return self.Preemptable
        
    def getType(self):
        return self.Type
        
    def getID(self):
        return self.ID
        
    def getName(self):
        return self.Name
        
    def setStart(self,myti):
        self.Start = myti
        return 
        
    def getProcessTime(self):

        return self.getOperation().getRandVar().sampleValue()  

        
    def getStart(self):
        return self.Start 

    def setCompletion(self,myti):
        self.Completion = myti
        return 
        
    def getCompletion(self):
        return self.Completion 
         

    def getOperation(self):
        return self.Operation
    def isScheduled(self):
        return self.Scheduled
        
    def setScheduled(self):
        self.getOperation().setStatus("Scheduled")
        self.Scheduled = True
        return
        
    def getEarliestStart(self,schjoblist):

        if self.getPredecessor() == None:
            return 0 
        else:
            if self.getPredecessor().isScheduled():
                return self.getPredecessor().getCompletion()
            else: 
                if self.getPredecessor().getOperation().isFinished() or self.getPredecessor().getOperation().isCancelled():
                    return 0
                else:
                    if self.getPredecessor() in schjoblist:
                        return 0
                    else:
                        return 100000
                    

    def setPredecessor(self,mypr):
        self.Predecessor= mypr
        return
        
    def getPredecessor(self):
        return self.Predecessor

    def setSuccessor(self,mypr):
        self.Successor= mypr
        return
        
    def getSuccessor(self):
        return self.Successor

 

    def setDeadLine(self,dd):
        self.deadline = dd
        return 
    def getDeadLine(self):
        return self.deadline 

    def isSchedulable(self):

        if self.isScheduled() or self.getOperation().isCancelled() or self.getOperation().isFinished():
            return False
        else:
            if self.getPredecessor() != None:
                return self.recursiveSchedulableCheck(self.getPredecessor())

        return True


    def recursiveSchedulableCheck(self,pred):

        if pred.isScheduled() or pred.getOperation().isCancelled() or pred.getOperation().isFinished():
            if pred.getPredecessor() == None:
                return True
            else:
                return self.recursiveSchedulableCheck(pred.getPredecessor())
        else:
            return False


        

##############################################################################
class SchOperator(object):
    def __init__(self,myoprtr):

        self.Operator = myoprtr
        self.Matches = dict() # key: job, value: (start,comp)
        self.Schedule = dict() # key: job, value: (start,comp)
        self.Shiftjobs = dict() # key: shift, value: [job] #setup jobs in the shift

    def getOperator(self):
        return self.Operator

    def getSchedule(self):
        return self.Schedule

    def getShiftjobs(self):
        return self.Shiftjobs
##################################################################################################
class MatchVar(object):
    def __init__(self,mach,job,start,stshift,comp):
        self.Machine = mach
        self.Job = job
        self.Start = start
        self.Completion = comp
        self.MILPVar = None
        self.StartShift = stshift
        self.ShiftUse = dict()  #key: shift, val: used man-hour capacity


    def getShiftUse(self):
        return self.ShiftUse

    def getStartShift(self):
        return self.StartShift

    def setMILPVar(self,myvar):
        self.MILPVar = myvar
        return

    def getMILPVar(self):
        return self.MILPVar

    def getMachine(self):
        return self.Machine 

    def getJob(self):
        return self.Job

    def getStart(self):
        return self.Start

    def getCompletion(self):
        return self.Completion 

    def printMatch(self):
        return " Match: "+self.getJob().getOperation().getName()+", mach  "+self.getMachine().getMachine().getName()+" start "+str(self.getStart())+" comp "+str(self.getCompletion())
        
################################################################################
class SchMachine(object):
    def __init__(self,mymach):

        self.Machine = mymach
        self.Matches = [] # key: slot, value: [match]
        self.Schedule = [] # ((startshift,starttime),(completeshift,completetime))
        self.JobStarts = [] # [(job,starttime)]
     
        self.Shiftjobs = dict() # key: shift, value: [job] , jobs that start in the shift
        self.MILPConstraints = [] # x_jm + x_j'm <= 1
        self.MyShifts = [] 

    def getMyShifts(self):
        return self.MyShifts

    def getMILPConstraints(self):
        return self.MILPConstraints

    def getJobStarts(self):
        return self.JobStarts 

    def getShift(self,mytime):

        for shift in self.getMyShifts():
            if shift.getStartTime() <= mytime and mytime<= shift.getEndTime():
                return shift

        return None
        

 

    def getSchedule(self):
        return self.Schedule

    def getMachine(self):
        return self.Machine
    def getMatches(self):
        return self.Matches

   

###############################################################################    
    def getTimeLength(self,start,end):
        timelength = 0

        for shift in self.getMyShifts():
            if start > shift.getEndTime():
                continue
            if end < shift.getStartTime() :
                break
      
            timelength+=  min(shift.getEndTime(),end)-max(shift.getStartTime(),start)

           
     
        return timelength


################################################################################
class Shift(object):
    def __init__(self,mydate,shiftno,start,shiftmins):
        self.Date = mydate
        self.ShiftNo = shiftno
        self.Next = None
        self.Starttime = start
        self.Endtime = start+shiftmins

        self.MFCapconstraint = None
        self.BWCapconstraint = None
        self.FTEUse = dict() # key: process type, val: available man-hour in the shift. 

    def getFTEUse(self):
        return self.FTEUse

    def setMFCapconstraint(self,mycon):
        self.MFCapconstraint = mycon
        return

    def setBWCapconstraint(self,mycon):
        self.BWCapconstraint = mycon
        return

    def getMFCapconstraint(self):
        return self.MFCapconstraint 

    def getBWCapconstraint(self):
        return self.BWCapconstraint 

    def setNext(self,mysh):
        self.Next = mysh
        return 
    def getStartTime(self):
        return self.Starttime

    def getNext(self):
        return self.Next
        
         
    def getDay(self):
        return self.Date

    def getShiftNo(self):
        return self.ShiftNo

    def getEndTime(self):
        return self.Endtime

    def printShift(self,milpmgr):
        return str(self.getDay())+", no "+str(self.getShiftNo())+", times: "+str(self.getStartTime())+"-"+str(self.getEndTime())+", MF opr_cap: "+str(self.getOperatorCapacity("Metal forming",milpmgr))+", BW opr_cap: "+str(self.getOperatorCapacity("Benchwork",milpmgr))

    def getOperatorCapacity(self,processtype,milpmgr):

        operator_capacity = 0
        for oprtr in milpmgr.getOperators():
            if oprtr.getProcessType() == processtype:
                if self.getShiftNo() in oprtr.getAvailableShifts():
                    operator_capacity+=milpmgr.getShiftMinutes()

                    
        return operator_capacity
        
#############################################################################

#################################################################################
class ProductionMILPManager(MILPManager): 
    def __init__(self,sim):
        super().__init__(sim)

        self.Jobs = []
        self.Machines = [] 
        self.SchedulableJobs = []
        self.Operators = []
        self.Shifts = dict() # key: day, val: dict()  key: no, value: shift
        self.TimeHorizon = None   
        self.shift_minutes = 479
        self.shiftmapping = {0:3,1:3,2:3,3:3,4:3,5:3,6:3,7:3,8:1,9:1,10:1,11:1,12:1,13:1,14:1,15:1,16:2,17:2,18:2,19:2,20:2,21:2,22:2,23:2}
        self.CurrentJobID = 0
        self.matchesperslot = 3
        self.matchincrement = 30
        self.timelimitsecs = 600
        self.optimalitygap = 0.05
        self.machinedict = dict()
        self.MILPModel = None
        self.writeMILP = False
        self.deadlinemax = None
        self.deadlinemin = None
        self.modeljobs = 50 
        self.solverType = "SCIP"
        self.MILPRound = 1
        self.bigM = 100000000
        self.epsilon = 0.001
        self.OperationJobDict = dict()

    def getOperationJobDict(self):
        return self.OperationJobDict

    def getModelJobs(self):
        return self.modeljobs

    def setMaxDeadLine(self,dd):
        self.deadlinemax = dd
        return
    def setMinDeadLine(self,dd):
        self.deadlinemin = dd
        return

    def getMaxDeadLine(self):
        return self.deadlinemax 

    def getMinDeadLine(self):
        return self.deadlinemin
    
    def getMachineDict(self):
        return self.machinedict

    def getShiftMinutes(self):
        return self.shift_minutes

    def getMatchespershift(self):
        return self.matchespershift
        
    def getShifts(self):
        return self.Shifts

    def giveJobID(self):
        self.CurrentJobID+=1 
        return self.CurrentJobID

    def getJobs(self):
        return self.Jobs
    def getMachines(self):
        return self.Machines
    def getOperators(self):
        return self.Operators
    
    def convertSimTime(self,mydate):

        mindeadline = self.getMinDeadLine()
        new_date = mindeadline.replace(hour = 0,minute=0, second=0, microsecond=0)
        
        return 28800+mydate.hour*60+mydate.minute+1440*(mydate - new_date).days

    def convertSimTimeToLSTDate(self,mytime):
        mindeadline = self.getMinDeadLine()
        new_date = mindeadline.replace(hour = 0,minute=0, second=0, microsecond=0)

        return new_date+timedelta(minutes = mytime-28800)
        
    def convertSimTimeToDate(self,mytime):    
        return self.getSimulator().getStartDay()+timedelta(minutes = mytime)
 
##############################################################################################################
    def giveLST(self,job,comptime):

        progress = self.getProgress()

        currenttime = comptime
        processtime =  job.getProcessTime()

        if len(job.getOperation().getAlternativeResources()) == 0:
            return 50000

        
            
        jobmach =  job.getOperation().getAlternativeResources()[0]

        #progress.value+=" > lst func, machine "+jobmach.getName()+", proctime: "+str(processtime)+"\n"
       

        while processtime > 0:

            #progress.value+=" time "+str(currenttime)+", shiftno "+str(self.getShiftNo(currenttime))+" available shift "+str(self.getShiftNo(currenttime) in jobmach.getAvailableShifts())+"\n"
            if self.getShiftNo(currenttime) in jobmach.getAvailableShifts():
                
                currshiftstart = self.getShiftStart(currenttime)
                #progress.value+=" > currenttime"+str(currenttime)+", currshiftstart "+str(currshiftstart)+"\n"
                
                if currenttime - processtime >= currshiftstart:
                    currenttime= currenttime - processtime
                    processtime = 0
                    
                    #progress.value+=" > new currenttime "+str(currenttime)+" proctime: "+str(processtime)+"\n"
                else:
                    processtime-= (currenttime-currshiftstart)
                    currenttime= currshiftstart - 1

            else: 
                currenttime= currenttime - (self.shift_minutes+1)
                
            #progress.value+=" > currenttime "+str(currenttime)+" proctime: "+str(processtime)+"\n"

        return currenttime
##############################################################################################################
    def checkFeasibility(self,machine,slotlength,slotshifts,shift,starttime,job):

        Reason = ""
        completion = None
        progress = self.getProgress()
        shiftfteuse = dict()


        #progress.value+=" > feasibility check 1.."+str(job.getEarliestStart())+"\n"

        

        if starttime < job.getEarliestStart(self.getSchedulableJobs()):
            return (False,completion,shiftfteuse)

        #progress.value+=" > feasibility check 2.."+"\n"

        if job.getProcessTime() > slotlength:
            Reason+=" Slot has shorter length than job proceess time"
            return (False,completion,shiftfteuse)


        #progress.value+=" > feasibility check 3.."+"\n"

        if machine.getMachine().getName() != "OUT - Outsourced activity_(OUT - Outsourced)":
            # check start conflicting jobs      
            for jobsch in machine.getSchedule():
                if jobsch[0][1] <= starttime and jobsch[1][1] >= starttime:
                    return (False,completion,shiftfteuse) 


        #progress.value+=" > feasibility check finding completion time .."+"\n"
        
        # tracking the start till the completion 
        currenttime = starttime
        procss_shft_strt = currenttime
        proctime = job.getProcessTime()

        shiftid = 0
        
        for slotshift in slotshifts:
            if slotshift == shift:
                break
            shiftid+=1

        currentshift = slotshifts[shiftid]
        procss_shft_strt = starttime

        
        while proctime > 0: 
            if proctime <= currentshift.getEndTime() - procss_shft_strt: 
                currenttime = proctime+procss_shft_strt
                shiftfteuse[currentshift] = proctime
                proctime = 0       
            else: 
                shiftfteuse[currentshift] = (currentshift.getEndTime()+1 - procss_shft_strt)
                shiftid+=1
                if shiftid >= len(slotshifts):
                    return (False,completion) 
                proctime -= (currentshift.getEndTime()+1 - procss_shft_strt)
                currentshift = slotshifts[shiftid]
                procss_shft_strt = currentshift.getStartTime()
                currenttime = procss_shft_strt

        if machine.getMachine().getName() != "OUT - Outsourced activity_(OUT - Outsourced)":
        # check completion conflicting jobs
            for jobsch in machine.getSchedule():
                if jobsch[0][1] <= currenttime and jobsch[1][1] >= currenttime:
                    return (False,completion,shiftfteuse) 

        if machine.getMachine().getName() != "OUT - Outsourced activity_(OUT - Outsourced)":
        # now only jobs that are processed between start and completions times are left. 
            for jobsch in machine.getSchedule():
                if jobsch[0][1] >= starttime and jobsch[1][1] <= currenttime:
                    return (False,completion,shiftfteuse) 

        completion = currenttime

        return (True,completion,shiftfteuse)     

#############################################################################################################################
 
####################################################################################################################################

    def getShift(self,mytime):

        mydate = self.convertSimTimeToDate(mytime)
        shftno = self.getShiftNo(mytime)

        return self.getShifts()[mydate][shftno]
        


    def getShiftStart(self,mytime):
        return  (mytime//(self.shift_minutes+1))*(self.shift_minutes+1)

    def getShiftEnd(self,mytime):
        return self.getShiftStart(mytime)+self.shift_minutes*int((mytime%self.shift_minutes)>0)

    def getShiftNo(self,mytime):
        
        return self.shiftmapping[self.convertSimTimeToDate(mytime).hour]


    def setTimeHorizon(self,th):
        self.TimeHorizon = th
        return
        
    def getTimeHorizon(self):
        return self.TimeHorizon 
        
    def findSchedulables(self):

        progress = self.getProgress()

        try: 

            allschedulables = [j for j in self.getJobs() if j.isSchedulable() and len(j.getOperation().getAlternativeResources()) > 0]
    
            EDDordered = sorted(allschedulables,key=lambda x: x.getDeadLine(), reverse= False)
    
            joblisttomatch = []
            
            #count jobs
            jobsinlist = 0
            for j in EDDordered:
                if jobsinlist < 50:
                    joblisttomatch.append(j)
                    jobsinlist+=1

            
            for job in joblisttomatch:
                progress.value+="  Operation "+str(job.getProduct().getPN())+" - "+job.getOperation().getName()+"-"+str(job.getOperation().getDemand().getID())+"  is schedulable"+"\n"
    
            succstartindex = len(joblisttomatch)
            # now add some successors
            for job in joblisttomatch:
                if job.getSuccessor()!= None:
                    succ = job.getSuccessor()
                    if jobsinlist < 70:
                        progress.value+=" Operation "+str(job.getProduct().getPN())+" - "+job.getOperation().getName()+"-"+str(job.getOperation().getDemand().getID())+"  is schedulable"+"\n"
                        progress.value+=" Sucessor  Operation "+str(succ.getProduct().getPN())+" - "+succ.getOperation().getName()+"-"+str(succ.getOperation().getDemand().getID())+"  is in model"+"\n"
                        joblisttomatch.append(succ)
                        jobsinlist+=1

           
    
            if len(joblisttomatch) > succstartindex:
                
               
                    
                listsize = len(joblisttomatch)
                for jobind in range(succstartindex,listsize):
                    job = joblisttomatch[jobind]
                    if job.getSuccessor()!= None:
                        succ = job.getSuccessor()
                        if jobsinlist < 80:
                            progress.value+=" Operation "+str(job.getProduct().getPN())+" - "+job.getOperation().getName()+"-"+str(job.getOperation().getDemand().getID())+"  is in model"+"\n"
                            progress.value+=" Sucessor-successor Operation "+str(succ.getProduct().getPN())+" - "+succ.getOperation().getName()+"-"+str(succ.getOperation().getDemand().getID())+"  is schedulable"+"\n"
                            joblisttomatch.append(succ)
                            jobsinlist+=1  

              
            
            self.SchedulableJobs = [j for j in joblisttomatch]  
            
        except Exception as e:
            progress.value+="ERROR: in finding jobstomatch "+str(e)+"\n" 
            

        return 
        

    def getSchedulableJobs(self):
        return self.SchedulableJobs
    def setSchedulableJobs(self,myli):
        self.SchedulableJobs = myli
        return

    def getProgress(self):
        return self.getSimulator().getController().getVisualManager().getmilpprogress()

#########################################################################################################################
#########################################################################################################################
    def constructSchedule(self):

        progress = self.getProgress()
        
        self.constructInstance()


        for date,noshiftdict in self.getShifts().items():
            for shiftno,myshift in noshiftdict.items():
                myshift.getFTEUse()["Metal forming"] = 0
                myshift.getFTEUse()["Benchwork"] = 0
       
        nrscheduled = 1

        while nrscheduled > 0: 
            
            self.MILPModel = pywraplp.Solver.CreateSolver(self.solverType)
            if not self.MILPModel:
                progress.value+=" > ERROR: Model could not be created.."+"\n"
            objective = self.MILPModel.Objective(); objective.SetMaximization()

            try: 
                for date,noshiftdict in self.getShifts().items():
                    for shiftno,myshift in noshiftdict.items():
                        capcons = self.MILPModel.Constraint(0,myshift.getOperatorCapacity("Metal forming",self),str(myshift.getDay())+"_"+str(shiftno)+"_MFcap")
                        myshift.setMFCapconstraint(capcons)
                        capcons2 = self.MILPModel.Constraint(0,myshift.getOperatorCapacity("Benchwork",self),str(myshift.getDay())+"_"+str(shiftno)+"_BWcap")
                        myshift.setBWCapconstraint(capcons2)
            except Exception as e:
                progress.value+="ERROR: in shift constraints "+str(e)+"\n"

            self.findSchedulables()
            progress.value+=" Schedulables found.. "+str(len(self.getSchedulableJobs()))+"\n"
            #for job in self.getSchedulableJobs():
            #    progress.value+="  Operation "+str(job.getProduct().getPN())+" - "+job.getOperation().getName()+"  is schedulable"+"\n"
            nrmatches = self.findMatches()
            progress.value+="Round "+str(self.MILPRound)+" no matches..."+str(nrmatches)+" \n"
            if nrmatches == 0:
                break # no match found to schedule..
            
            self.checkConflicts()
     
            progress.value+="Round "+str(self.MILPRound)+" starts solving... \n" 
      
            nrscheduled = self.solveProblem()
            progress.value+="Round "+str(self.MILPRound)+" no nrscheduled..."+str(nrscheduled)+" \n" 

            #if self.MILPRound > 1:
            #    break

            #self.getSimulator().getController().getWorkManager().writeDataTBRMOutPut(self.MILPRound)
         
            self.MILPRound+=1


         # check precedence feasibility:  
        for prodorder in self.getSimulator().getController().getWorkManager().getSelectedOrders():
            operation_sequence = prodorder.getFinalProduct().getOperationSequences()[prodorder.getID()]

            active_predecessor = None
            
            for oprind in range(len(operation_sequence)):
                operation = operation_sequence[oprind]
                if operation.isCancelled():
                    continue

                if operation.isFinished():
                    active_predecessor = operation
                    continue
                    
                if  not self.getOperationJobDict()[operation].isScheduled():
                    break

                
                if active_predecessor != None:
                    if active_predecessor.getCompletion() > operation.getStart():
                        progress.value+="Precedence violation: operation "+str(operation.getName())+" starts "+str(operation.getStart())+" before pred "+str(active_predecessor.getName())+" gets completed"+str(active_predecessor.getCompletion())+"\n"
                        
                active_predecessor = operation
    
        try: 
            self.getSimulator().getController().getWorkManager().writeDataTBRMOutPut(self.MILPRound+1)
        except Exception as e:
                progress.value+="ERROR: in writing the output "+str(e)+"\n"
        

        return 
#########################################################################################################################
#########################################################################################################################
    def constructInstance(self):

        progress = self.getProgress()

        progress.value+=" Scheduling problem instance construction \n" 

       
        self.setTimeHorizon(self.getSimulator().getTimeLimit())

        deadline_max = max([p.getDeadline() for p in self.getSimulator().getController().getWorkManager().getSelectedOrders()])
        deadline_min = min([p.getDeadline() for p in self.getSimulator().getController().getWorkManager().getSelectedOrders()])

        self.setMaxDeadLine(deadline_max)
        self.setMinDeadLine(deadline_min)

        try: 
            # iterate production orders to construct jobs. 
            for prodorder in self.getSimulator().getController().getWorkManager().getSelectedOrders():
    
                operation_sequence = prodorder.getFinalProduct().getOperationSequences()[prodorder.getID()]
    
                previous_job = None
                oprid = 1
                for operation in operation_sequence:
                    myjob = Job(operation,"Processing",True,self.giveJobID()) # args: myopr,mytype,preempt,myid

                    self.getOperationJobDict()[operation] = myjob
                   
                    self.getJobs().append(myjob);

                    #progress.value+=" job "+str(myjob.getOperation().getName())+" defined oprid "+str(oprid)+"\n" 
  
                    if previous_job!= None:
                        previous_job.setSuccessor(myjob)
                        myjob.setPredecessor(previous_job)
                    
                    if oprid == len(operation_sequence): # last job
                        myjob.setDeadLine(prodorder.getDeadline())

                        curr_deadline = self.convertSimTime(prodorder.getDeadline())

                        #progress.value+="  hour  "+str(prodorder.getDeadline().hour)+"min "+str(prodorder.getDeadline().minute)+", daymins "+str(1440*(prodorder.getDeadline() - self.getSimulator().getStartDay()).days)+"\n" 

                       
                       

                        #progress.value+=" last job "+str(myjob.getOperation().getName())+"deadline "+str(myjob.getDeadLine())+", simtime "+str(curr_deadline)+", proctime: "+str(myjob.getProcessTime())+"\n" 
                        #deadline = myjob.getDeadLine()-timedelta(minutes=myjob.getOperation().getRandVar().sampleValue())
                        successorlst = self.giveLST(myjob,curr_deadline)
                        predjob = myjob.getPredecessor()
                        preddepth = 1
                        while predjob!= None:
                            
                            predjob.setDeadLine(self.convertSimTimeToLSTDate(successorlst))
                            #progress.value+=" job "+str(predjob.getOperation().getName())+" in prec depth "+str(preddepth)+" has deadline "+str(predjob.getDeadLine())+" simtime "+str(successorlst)+", proctime: "+str(predjob.getProcessTime())+"\n" 
                            successorlst = self.giveLST(predjob,successorlst)
                            #deadline = deadline - timedelta(minutes=currentjob.getOperation().getRandVar().sampleValue())
                            predjob = predjob.getPredecessor()
                            preddepth+=1
      
                    oprid+=1
                    previous_job = myjob

            # iterate resources to construct Machines and get operators
            for resource in self.getSimulator().getController().getWorkManager().getResources():
                if isinstance(resource,Machine):
                    mymachine = SchMachine(resource)
                    self.getMachines().append(mymachine)  
                    self.getMachineDict()[resource] = mymachine
                if isinstance(resource,Operator):
                    self.getOperators().append(resource)
      
     
            progress.value+=" > Selected orders: "+str(len(self.getSimulator().getController().getWorkManager().getSelectedOrders()))+"\n"
            progress.value+=" > Time horizon: "+str(self.getTimeHorizon())+"\n"
            progress.value+=" > No Jobs: "+str(len(self.getJobs()))+ "\n" 
            progress.value+=" > No Machines: "+str(len(self.getMachines()))+", No Operators: "+str(len(self.getOperators()))+"\n"
         
            # time count: 

            progress.value+=" > Shift creation starts.. "+ "\n" 
            mytime = 0
            prev_shift = None
            myshift = None
        
            while mytime < self.getTimeHorizon():
                mydate = self.convertSimTimeToDate(mytime)
                shftno = self.shiftmapping[mydate.hour]
              
        
                while mydate.weekday() >= 5:
                    mytime+=self.shift_minutes+1
                    mydate = self.convertSimTimeToDate(mytime)
                    shftno = self.shiftmapping[mydate.hour]

                
                myshift = Shift(mydate.date(),shftno,mytime,self.shift_minutes)
                if not mydate.date() in self.getShifts():
                    self.getShifts()[mydate.date()] = dict()
                progress.value+=" >> Shift: "+myshift.printShift(self)+"\n"
                progress.value+=" >> date: "+str(mydate.date())+", shift no "+str(shftno)+"\n"
                
               
                self.getShifts()[mydate.date()][shftno] = myshift

                if prev_shift!= None:
                    prev_shift.setNext(myshift)

                prev_shift = myshift

                mytime+=self.shift_minutes+1

            
            progress.value+=" > Shift creation completed.. "+ "\n" 

            
            
            for mach in self.getMachines():  
                mytime = 0 
                mydate = self.convertSimTimeToDate(mytime)
                shftno = self.shiftmapping[mydate.hour]
        
                while mydate.weekday() >= 5:
                    mytime+=self.shift_minutes+1
                    mydate = self.convertSimTimeToDate(mytime)
                    shftno = self.shiftmapping[mydate.hour]

                #progress.value+=" first date.."+str(mydate)+"\n"

                if mydate.date() in self.getShifts():
                    #progress.value+=" shifts on first date .."+str([k for k in self.getShifts()[mydate.date()].keys()])+"\n"
                    currentshift = self.getShifts()[mydate.date()][3] # very first shift
                else:
                    progress.value+="ERROR: first date not in shifts.."+"\n"

                #progress.value+="first shift none? "+str(currentshift== None)+"\n"
                while currentshift!= None:
                    if currentshift.getShiftNo() in mach.getMachine().getAvailableShifts():
                        if mach.getMachine().IsAutomated():
                            if currentshift.getShiftNo() != 3 or len(mach.getMyShifts()) > 0:
                                mach.getMyShifts().append(currentshift)
                        else:
                            mach.getMyShifts().append(currentshift)
                            
                    currentshift = currentshift.getNext()


                progress.value+=" mach "+mach.getMachine().getName()+" no.slots: "+str(len(mach.getMyShifts()))+"\n"
                

            

        except Exception as e:
            progress.value+="ERROR: MILP instance construction "+str(e)+"\n"
            
        return
######################################################################################################################
    def findMatches(self):

        progress = self.getProgress()
        objective = self.MILPModel.Objective();
        nrmatches = 0

        for mach in self.getMachines():
            mach.getMatches().clear()

        progress.value+=" Finding mathes.."+"\n"

        try: 
            jobid = 0
            
            for job in self.getSchedulableJobs():
                 # sum(x_jm) <= 1
                job.setMILPConstraint(self.MILPModel.Constraint(0,1,job.getProduct().getPN()+"_"+job.getOperation().getName()+"_"+str(jobid)+'_cons'))
                job.setPrecedenceConstraint(None)
                job.setPrecedenceConstraint2(None)
                job.getMyMatches().clear()

                progress.value+="  Operation "+str(job.getProduct().getPN())+" - "+job.getOperation().getName()+"  is matchmodel"+"\n"

                ### precedence constraints
                if job.getSuccessor()!= None:
                    if job.getSuccessor() in self.getSchedulableJobs():
                        progress.value+="  Operation "+str(job.getProduct().getPN())+" - "+job.getOperation().getName()+" has successor "+job.getSuccessor().getOperation().getName()+" in matchmodel"+"\n"
                        # sum(x_j'm) <= sum(x_jm)+eps for j -> j'
                        job.setPrecedenceConstraint(self.MILPModel.Constraint(-1,self.epsilon,job.getProduct().getPN()+"_"+job.getOperation().getName()+"_"+str(jobid)+'_preccons1'))
                        # sum(c_{jm}x_{jm}) <= sum(st_{j'm}x_{j'm})+M*(1-sum(x_j'm)) for j -> j'
                        job.setPrecedenceConstraint2(self.MILPModel.Constraint(0,self.bigM,job.getProduct().getPN()+"_"+job.getOperation().getName()+"_"+str(jobid)+'_preccons2'))
                    
                ### precedence constraints
                
                jobid+=1
                matchid = 0
               

                
                if len(job.getOperation().getAlternativeResources()) == 0:
                    progress.value+=" CHECK: Operation "+job.getOperation().getName()+" has no alternative machine..."+"\n"

                progress.value+="Operation "+job.getOperation().getName()+" has alternative machines: "+str([m.getName() for m in job.getOperation().getAlternativeResources()])+"\n"
                
                for mach in job.getOperation().getAlternativeResources():
                    mymach = self.getMachineDict()[mach]

                    progress.value+="checking machine "+mach.getName()+"\n"

                    currentshift = mymach.getMyShifts()[0]
                    slotstart = currentshift.getStartTime()
             
                    currentslotshifts = []

                    if mach.getName() != "OUT - Outsourced activity_(OUT - Outsourced)":
                        for schid in range(len(mymach.getSchedule())):
                            
                            schtuple = mymach.getSchedule()[schid]
                            timelength = mymach.getTimeLength(slotstart,schtuple[0][1])
    
                            #progress.value+=" timelength ."+str(type(timelength))+"\n"
                            if timelength >= job.getProcessTime():
                                currentslotshifts = []
    
                                # collect shifts in the current slot
                                currentslotshifts.append(currentshift) 
                                
                                shftind = mymach.getMyShifts().index(currentshift)+1
                                if shftind < len(mymach.getMyShifts()):
                                    curr_shift = mymach.getMyShifts()[shftind]
                                    
                                while (curr_shift.getStartTime() < schtuple[1][0].getStartTime()) and (shftind < len(mymach.getMyShifts())):
                                    currentslotshifts.append(curr_shift)
                                    shftind+=1
                                    if (shftind < len(mymach.getMyShifts())):
                                        curr_shift = mymach.getMyShifts()[shftind]
                                               
            
                                if schtuple[0][0] != schtuple[1][0]:
                                    currentslotshifts.append(schtuple[1][0]) 
                                # collect shifts in the current slot    
    
                                nrmatches,matchid = self.findSlotMatches(objective,mymach,mach,job,timelength,currentslotshifts,slotstart,schtuple[0][1],nrmatches,matchid)
    
                             
                            slotstart = schtuple[1][1] 
                            currentshift = schtuple[1][0]  

                    lastshift = mymach.getMyShifts()[-1]

                    #progress.value+=">>> slotstart: "+str(slotstart)+", lastshift.getEndTime():"+str(lastshift.getEndTime())+"\n"
                    
                    timelength = mymach.getTimeLength(slotstart,lastshift.getEndTime())

                    #progress.value+=">>> timelength: "+str(timelength)+"\n"

                    if mach.getName() == "OUT - Outsourced activity_(OUT - Outsourced)":
                        progress.value+= "OUT - Outsourced activity_(OUT - Outsourced) >>> timelength: "+str(timelength)+"\n"
                    
                    if timelength >= job.getProcessTime():
                        currentslotshifts = []
                         # collect shifts in the current slot
                          
                        shftind = mymach.getMyShifts().index(currentshift)
                        curr_shift = mymach.getMyShifts()[shftind]
                       
                        while shftind < len(mymach.getMyShifts()):
                            currentslotshifts.append(curr_shift)
                            shftind+=1
                            if (shftind < len(mymach.getMyShifts())):
                                curr_shift = mymach.getMyShifts()[shftind]

                        # collect shifts in the current slot  
                        #if mach.getName() == "OUT - Outsourced activity_(OUT - Outsourced)":
                        #    progress.value+="  >>>>>>>> slot sart: "+str(slotstart)+", length: "+str(timelength)+", end: "+str(lastshift.getEndTime())+" shifts: "+str(len(currentslotshifts))+mach.getName()+"\n"
                        prev_matches = nrmatches
                        nrmatches,matchid = self.findSlotMatches(objective,mymach,mach,job,timelength,currentslotshifts,slotstart,lastshift.getEndTime(),nrmatches,matchid)
                        if mach.getName() == "OUT - Outsourced activity_(OUT - Outsourced)":
                            progress.value+="  >>>>>>>>OUT - Operation "+job.getOperation().getName()+" has "+str(nrmatches-prev_matches)+" matches at mach "+mach.getName()+"\n"
                            progress.value+="  >>>>>>>>OUT - timelength "+str(timelength)+", slotstart "+str(slotstart)+",end time  "+str(lastshift.getEndTime())+"\n"
                            #for match in mymach.getMatches():
                            #    progress.value+=">> Match: "+str(match.printMatch())+", job: "+str(job.getProduct().getPN())+"\n"
                                

         
        except Exception as e:
            progress.value+="ERROR: in find matches "+str(e)+"\n"
        

        return nrmatches


#______________________________________________________________________
######################################################################################################################
    def findSlotMatches(self,objective,mymach,mach,job,slotlength,currentslotshifts,slotstart,jobschstart,nrmatches,matchid):

        progress = self.getProgress()
        currentincrement = 15  
        
        try: 
                        
            for shiftid in range(len(currentslotshifts)):
    
                slotshift = currentslotshifts[shiftid]
                currentstart = max(slotstart,slotshift.getStartTime())
                if slotshift.getShiftNo() == 3:
                    continue
                currentincrement = (1+int(shiftid>0))*currentincrement

                #if mach.getName() == "OUT - Outsourced activity_(OUT - Outsourced)":
                    #progress.value+=">> currentstart: "+str(currentstart)+", slotshift.getEndTime(): "+str(slotshift.getEndTime())+", jobschstart: "+str(jobschstart)+" slotlength: "+str(slotlength)+", proctime: "+str(job.getProcessTime())+"\n"
                while currentstart <= min(slotshift.getEndTime(),jobschstart):
                    funcreturn = self.checkFeasibility(mymach,slotlength,currentslotshifts,slotshift,currentstart,job)
                    if funcreturn[0]:

                        #progress.value+=">> match is feasible...... "+"\n"
                            
                        nrmatches+=1
                        mymatch = MatchVar(mymach,job,currentstart,slotshift,funcreturn[1])
                        matchvar = self.MILPModel.IntVar(0.0,1,'x_'+str(mach.getMachineCode())+'_'+str(job.getID())+" "+str(job.getOperation().getDemand().getID())+" "+str(matchid))  # x_{m,j}
                        deadline_coeff =((self.getMaxDeadLine()-job.getDeadLine()).days) /((self.getMaxDeadLine() -self.getMinDeadLine()).days)
                        obj_coeff = 10*deadline_coeff+25*(self.getTimeHorizon()-funcreturn[1])/self.getTimeHorizon()+5*job.getProcessTime()/self.getTimeHorizon()
                        matchid+=1
   
                        job.getMILPConstraint().SetCoefficient(matchvar,1)
                        if job.getPrecedenceConstraint() != None:
                            job.getPrecedenceConstraint().SetCoefficient(matchvar,-1) # sum(x_j'm) <= sum(x_jm)+eps for j -> j'
                            job.getPrecedenceConstraint2().SetCoefficient(matchvar,funcreturn[1]) # sum(c_{jm}x_{jm}) <= sum(st_{j'm}x_{j'm})+M*(1-sum(x_j'm))   for j -> j'
                        if job.getPredecessor() != None:
                            #progress.value+="+++++ job  "+job.getOperation().getName()+" has predecessor "+job.getPredecessor().getOperation().getName()+"\n"
                            if job.getPredecessor() in self.getSchedulableJobs():
                                #progress.value+="+++++ job  "+job.getOperation().getName()+" has predecessor "+job.getPredecessor().getOperation().getName()+" in schedulable list \n"
                                if job.getPredecessor().getPrecedenceConstraint() != None:
                                    #progress.value+="++++++ job  "+job.getOperation().getName()+" has predecessor "+job.getPredecessor().getOperation().getName()+" has constraints \n"
                                    job.getPredecessor().getPrecedenceConstraint().SetCoefficient(matchvar,1)
                                    job.getPredecessor().getPrecedenceConstraint2().SetCoefficient(matchvar,(self.bigM-currentstart)) 


                        #progress.value+= "processtype "+str(mach.getProcessType())+", man-hour use : "+str(funcreturn[2])+" \n"
                        for shifttuple in funcreturn[2].items():
                            mymatch.getShiftUse()[shifttuple[0]] = shifttuple[1]
                            if shifttuple[0].getShiftNo() != 3: 
                                if mach.getProcessType() == "Metal forming":
                                    shifttuple[0].getMFCapconstraint().SetCoefficient(matchvar,mach.getOperatingEffort()*(shifttuple[1]))
                                if mach.getProcessType() == "Benchwork":
                                    shifttuple[0].getBWCapconstraint().SetCoefficient(matchvar,mach.getOperatingEffort()*(shifttuple[1]))
                                
                            
                        #mymatch.updateCapacityConstraints(currentslotshifts,slotshift,self)
                        objective.SetCoefficient(matchvar,obj_coeff)
                        
          
                        mymach.getMatches().append(mymatch)
                        job.getMyMatches().append(mymatch)
                        mymatch.setMILPVar(matchvar)
        
    
                        #if mach.getName() == "M3-01_(FR3_01)":
                        #    progress.value+=">> Match: "+str(mymatch.printMatch())+", job: "+str(job.getProduct().getPN())+"\n"
        
                    currentstart+=currentincrement

        except Exception as e:
            progress.value+="ERROR: in finding slot matches "+str(e)+"\n"

        return nrmatches,matchid
################################################################################################################################       
    def checkConflicts(self):

        try: 
            for mach in self.getMachines():

                confid = 0
                progress = self.getProgress()
        
                startordered = sorted(mach.getMatches(),key=lambda x: x.getStart(), reverse= False)
                completionordered = sorted(mach.getMatches(),key=lambda x: x.getCompletion(), reverse= False)
        
                progress.value+=" mach "+str(mach.getMachine().getName())+" has "+str(len(mach.getMatches()))+" matches "+"\n"
        

                if mach.getMachine().getName() != "OUT - Outsourced activity_(OUT - Outsourced)":
                    for matchid in range(len(mach.getMatches())):
                        mymatch = mach.getMatches()[matchid]
                        confcons = None
                        for matchid2 in range(matchid+1,len(mach.getMatches())):      
                            mymatch2 = mach.getMatches()[matchid2]
            
                            # st2 >= cp1 or cp2 <= st1 
                            if (mymatch.getCompletion() <= mymatch2.getStart()) or (mymatch2.getCompletion() <= mymatch.getStart()) :
                                continue
             
                            if confcons == None:
                                confcons = self.MILPModel.Constraint(0,1,mach.getMachine().getName()+'_'+mymatch.getJob().getOperation().getName()+"_"+str(confid)+'_conf')
                                confcons.SetCoefficient(mymatch.getMILPVar(),1)
                                confid+=1
                            else:
                                confcons.SetCoefficient(mymatch2.getMILPVar(),1)
                                
            
                progress.value+="Conflict constraints: mach "+str(mach.getMachine().getName())+": "+str(confid)+"\n"
        except Exception as e:
            progress.value+="ERROR: in conf constraints "+str(e)+"\n"


        return 
#############################################################################
############################################################################
    def solveProblem(self):


        progress = self.getProgress()
        
        nrscheduled = 0

        if self.writeMILP: 
            mystring = self.MILPModel.ExportModelAsLpFormat(False)
            filename = 'MILP-model_'+str(self.MILPRound)+'.txt'
            textfile = open(filename, 'w')
            textfile.write(mystring)
            textfile.close()


        try: 
            self.MILPModel.set_time_limit(self.timelimitsecs*1000) 
            solverParams = pywraplp.MPSolverParameters()  
            solverParams.SetDoubleParam(solverParams.RELATIVE_MIP_GAP,self.optimalitygap)
            start = timer()
            status = self.MILPModel.Solve(solverParams)
            end = timer()
            progress.value+=" model solved in "+str(end-start)+"\n"
    
            StatusText = ''
            nrsolutions = 0
            
    
          
            if status == pywraplp.Solver.OPTIMAL:
                nrsolutions+=1
              
                progress.value+='Optimal Objective value = '+str(self.MILPModel.Objective().Value())+"\n"
                StatusText = 'Optimal'
            if status == pywraplp.Solver.INFEASIBLE:
                StatusText = 'Infeasible'
            if status == pywraplp.Solver.FEASIBLE:
                StatusText = 'Feasible'
                count = 1
                while self.MILPModel.NextSolution(): 
                    nrsolutions+=1
                    if nrsolutions == 1:
                        nrscheduled+=self.readSolution()
                    
             
            if (status == pywraplp.Solver.UNBOUNDED):
                StatusText = 'Unbounded'
            if (status == pywraplp.Solver.ABNORMAL): 
                StatusText = 'Abnormal'
            if (status == pywraplp.Solver.NOT_SOLVED): 
                StatusText = 'Not solved'
    
            progress.value+="Model: #variables ="+str(self.MILPModel.NumVariables())+', constraints ='+str(self.MILPModel.NumConstraints())+"\n"
    
            progress.value+= "Status: "+StatusText+", no solutions: "+str(nrsolutions)+"\n"
    
            #progress.value+="Solution time: "+str(round(time.time()-start_time,2))+" secs. \n"

            if StatusText ==  'Optimal':
                nrscheduled+=self.readSolution()
                

        except Exception as e:
            progress.value+="ERROR: in model solving "+str(e)+"\n"

        return nrscheduled
#################################################################################################################################################
    def readSolution(self):

        progress = self.getProgress()          

        try: 
            nrscheduled = 0
            
            
            progress.value+= "Reading solution..."+"\n"
            for mach in self.getMachines():
                machschs = 0
                for mymatch in mach.getMatches():
                    
                    if mymatch.getMILPVar().solution_value() > 0.5:
                        nrscheduled+=1
                        machschs+=1
                        progress.value+= "Variable: "+str(mymatch.getJob().getProduct().getPN())+"\n"
                        progress.value+= "start: "+str(self.convertSimTimeToDate(mymatch.getStart()))+", completion: "+str(self.convertSimTimeToDate(mymatch.getCompletion()))+"\n"
                        progress.value+= "start: "+str(mymatch.getStart())+", completion: "+str(mymatch.getCompletion())+"\n"
                        currshift = mymatch.getStartShift()
                        while currshift.getEndTime() < mymatch.getCompletion():
                            currshift = currshift.getNext()

                        mymatch.getJob().getOperation().setStart(self.convertSimTimeToDate(mymatch.getStart()))
                        mymatch.getJob().getOperation().setCompletion(self.convertSimTimeToDate(mymatch.getCompletion()))
                       
                        mymatch.getJob().getOperation().setProcessMachine(mach.getMachine())
                        mach.getSchedule().append(((mymatch.getStartShift(),mymatch.getStart()),(currshift,mymatch.getCompletion())))
                        mach.getJobStarts().append((mymatch.getJob(),mymatch.getStart()))

                        mymatch.getJob().setStart(mymatch.getStart())
                        mymatch.getJob().setCompletion(mymatch.getCompletion())
                        mymatch.getJob().setScheduled()

                        processmachine = mach.getMachine()

                        #if processmachine.getProcessType() in  ["Metal forming","Benchwork"]:
                            #progress.value+= " Match selected at machine  "+str(processmachine.getName())+", job "+str(mymatch.getJob().getOperation().getName())+"\n"
                            
                            #for usetuple in mymatch.getShiftUse().items():
                            #    usetuple[0].getFTEUse()[processmachine.getProcessType()]+=processmachine.getOperatingEffort()*usetuple[1]

                        #self.scheduleJob(mymatch.getJob(),mymatch.getStart(),mymatch.getCompletion(),mach)
    
                mach.getSchedule().sort(key=lambda x:x[0][1], reverse=False)
                mach.getJobStarts().sort(key=lambda x: x[1], reverse=False)
                progress.value+= "Schedule of mach: "+mach.getMachine().getName()+"\n"
                for schid in range(len(mach.getJobStarts())):
                    schtuple = mach.getSchedule()[schid]; starttuple = mach.getJobStarts()[schid]
                    
                    progress.value+= "Job: "+starttuple[0].getProduct().getPN()+" ("+str(self.convertSimTimeToDate(schtuple[0][1]))+"-"+str(self.convertSimTimeToDate(schtuple[1][1]))+"), d: "+str(starttuple[0].getDeadLine())+", p: "+str(starttuple[0].getOperation().getRandVar().sampleValue())+"\n"
            unscheduleds = [job for job in self.getSchedulableJobs() if not job.isScheduled()]

            for job in unscheduleds:
                progress.value+= "Unscheduled Job: "+job.getProduct().getPN()+", opr: "+job.getOperation().getName()+" - "+str(job.getOperation().getDemand().getID())+", p: "+str(job.getProcessTime())+"\n"

                
                

            progress.value+="____________________________________________________________________"+"\n"

           
                 
        except Exception as e:
            progress.value+="ERROR: in reading the solution "+str(e)+"\n"

        return nrscheduled

