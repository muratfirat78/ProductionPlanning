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

    def getMILPConstraint(self):
        return self.MILPConstraint

    def getProduct(self):
        return self.getOperation().getDemand().getFinalProduct()
        

    def setMILPConstraint(self,mycons):
        self.MILPConstraint = mycons


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
    def getProcessTime(self,machine):

        if self.Type == "Machine Setup":
            return machine.getMachine().getSetupTime()
            
        if self.Type == "Processing":
            return self.getOperation().getRandVar().sampleValue()  

        return 1
        
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
        self.Scheduled = True
        return
        
    def getEarliestStart(self):
        return (0 if self.getPredecessor() == None else self.getPredecessor().getCompletion())

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
        if self.isScheduled():
            return False
        else:
            if self.getPredecessor() == None:
                return True
            else:
                if self.getPredecessor().isScheduled():
                    return True
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

    def updateCapacityConstraints(self,slotshifts,startshift,milpmgr):
        
       
       # tracking the start till the completion 
        currenttime = self.getStart()
        procss_shft_strt = currenttime
        proctime = self.getJob().getProcessTime(self.getMachine())
    
        shiftid = 0
            
        for slotshift in slotshifts:
            if slotshift == startshift:
                break
            shiftid+=1
    
        currentshift = slotshifts[shiftid]
        procss_shft_strt = self.getStart()
    
            
        while proctime > 0: 
            if proctime <= currentshift.getEndTime() - procss_shft_strt: 
                currenttime = proctime+procss_shft_strt
                if self.getMachine().getMachine().getProcessType() == "Metal forming":
                    currentshift.getMFCapconstraint().SetCoefficient(self.getMILPVar(),self.getMachine().getMachine().getOperatingEffort()*(proctime))
                if self.getMachine().getMachine().getProcessType() == "Benchwork":
                    currentshift.getBWCapconstraint().SetCoefficient(self.getMILPVar(),self.getMachine().getMachine().getOperatingEffort()*(proctime))
                    
                proctime = 0       
            else: 
                shiftid+=1
                proctime -= (currentshift.getEndTime() - procss_shft_strt)
                if self.getMachine().getMachine().getProcessType() == "Metal forming":
                    currentshift.getMFCapconstraint().SetCoefficient(self.getMILPVar(),self.getMachine().getMachine().getOperatingEffort()*(currentshift.getEndTime() - procss_shft_strt))
                if self.getMachine().getMachine().getProcessType() == "Benchwork":
                    currentshift.getBWCapconstraint().SetCoefficient(self.getMILPVar(),self.getMachine().getMachine().getOperatingEffort()*(currentshift.getEndTime() - procss_shft_strt))
       
                currentshift = slotshifts[shiftid]
                procss_shft_strt = currentshift.getStartTime()
                currenttime = procss_shft_strt

        return
        
        
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
        


    def assignJob(self,job,start,comp):
        self.Schedule[job] = (start,comp)
        

    def getSchedule(self):
        return self.Schedule

    def getMachine(self):
        return self.Machine
    def getMatches(self):
        return self.Matches

    def getActiveTimes(self,start,mymgr):
        activetimes = 0
        currenttime = start
        currentshift = mymgr.getShift(start)

        progress = mymgr.getProgress()

        if currentshift!= None:
            while not currentshift.getShiftNo() in self.getMachine().getAvailableShifts():
                currentshift = currentshift.getNext()
                if currentshift!= None:
                    currenttime = currentshift.getStartTime()
                else:
                    break

        while currentshift!= None:
            
            activetimes+= (currentshift.getStartTime()+mymgr.getShiftMinutes() - currenttime) 
            currentshift = currentshift.getNext()

            if currentshift!= None:
                while not currentshift.getShiftNo() in self.getMachine().getAvailableShifts():
                    currentshift = currentshift.getNext()
                    if currentshift == None:
                        break
            
            if currentshift!= None:
                currenttime = currentshift.getStartTime()

        return activetimes


    
    def getTimeLength(self,start,end):
        timelength = 0

        for shift in self.getMyShifts():
            if start > shift.getEndTime():
                continue
            if end < shift.getStartTime() :
                break
                
            if start <= shift.getEndTime() and start >= shift.getStartTime():
                timelength+=  min(shift.getEndTime(),end)-start

            if start < shift.getStartTime() and end <= shift.getEndTime():
                timelength+=  min(shift.getEndTime(),end)-shift.getStartTime()

           
     
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
        self.shiftmapping = {0:3,8:1,16:2}
        self.CurrentJobID = 0
        self.matchesperslot = 3
        self.matchincrement = 30
        self.timelimitsecs = 60
        self.optimalitygap = 0.05
        self.machinedict = dict()
        self.MILPModel = None
        self.writeMILP = False
        self.deadlinemax = None
        self.deadlinemin = None
        self.modeljobs = 50 
        self.solverType = "SCIP"
        self.MILPRound = 1
        self.epsilon = 0.001

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
        
    def convertSimTimeToDate(self,mytime):    
        return self.getSimulator().getStartDay()+timedelta(minutes = mytime)
 

##############################################################################################################
    def checkFeasibility(self,machine,slotlength,slotshifts,shift,starttime,job):

        Reason = ""
        completion = None

        progress = self.getProgress()

        if starttime < job.getEarliestStart():
            return (False,completion)

        if job.getProcessTime(machine) > slotlength:
            Reason+=" Slot has shorter length than job proceess time"
            return (False,completion)

        # check start conflicting jobs      
        for jobsch in machine.getSchedule():
            if jobsch[0][1] <= starttime and jobsch[1][1] >= starttime:
                return (False,completion) 

        # tracking the start till the completion 
        currenttime = starttime
        procss_shft_strt = currenttime
        proctime = job.getProcessTime(machine)

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
                proctime = 0       
            else: 
            
                shiftid+=1
                if shiftid >= len(slotshifts):
                    return (False,completion) 
                proctime -= (currentshift.getEndTime()+1 - procss_shft_strt)
                currentshift = slotshifts[shiftid]
                procss_shft_strt = currentshift.getStartTime()
                currenttime = procss_shft_strt

        # check completion conflicting jobs
        for jobsch in machine.getSchedule():
            if jobsch[0][1] <= currenttime and jobsch[1][1] >= currenttime:
                return (False,completion) 

        # now only jobs that are processed between start and completions times are left. 
        for jobsch in machine.getSchedule():
            if jobsch[0][1] >= starttime and jobsch[1][1] <= currenttime:
                return (False,completion) 

        completion = currenttime

        return (True,completion)     

#############################################################################################################################
 
####################################################################################################################################

    def getShift(self,mytime):

        mydate = self.convertSimTimeToDate(mytime)
        shftno = self.getShiftNo(mytime)

        return self.getShifts()[mydate][shftno]
        


    def getShiftStart(self,mytime):
        return  (mytime//self.shift_minutes)*self.shift_minutes

    def getShiftEnd(self,mytime):
        return self.getShiftStart(mytime)+self.shift_minutes*int((mytime%self.shift_minutes)>0)

    def getShiftNo(self,mytime):
        
        return self.shiftmapping[self.convertSimTimeToDate(self.getShiftStart(mytime)).hour]


    def setTimeHorizon(self,th):
        self.TimeHorizon = th
        return
        
    def getTimeHorizon(self):
        return self.TimeHorizon 
        
    def findSchedulables(self):
        self.SchedulableJobs = [j for j in self.getJobs() if j.isSchedulable()]
        

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
         
            self.MILPRound+=1

        

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
                    self.getJobs().append(myjob);
  
                    if previous_job!= None:
                        previous_job.setSuccessor(myjob)
                        myjob.setPredecessor(previous_job)
                    
                    if oprid == len(operation_sequence): # last job
                        myjob.setDeadLine(prodorder.getDeadline())
                       

                        deadline = myjob.getDeadLine()-timedelta(minutes=myjob.getOperation().getRandVar().sampleValue())
                        currentjob = myjob.getPredecessor()
                        while currentjob!= None:
                            currentjob.setDeadLine(deadline)
                            deadline = deadline - timedelta(minutes=currentjob.getOperation().getRandVar().sampleValue())
                            currentjob = currentjob.getPredecessor()
      
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

                progress.value+=" first date.."+str(mydate)+"\n"

                if mydate.date() in self.getShifts():
                    progress.value+=" shifts on first date .."+str([k for k in self.getShifts()[mydate.date()].keys()])+"\n"
                    currentshift = self.getShifts()[mydate.date()][3] # very first shift
                else:
                    progress.value+="ERROR: first date not in shifts.."+"\n"

                progress.value+="first sfhit none? "+str(currentshift== None)+"\n"
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

        self.findSchedulables()
        progress.value+=" Schedulables found.. "+str(len(self.getSchedulableJobs()))+"\n"

        try: 
            jobid = 0
            
            for job in self.getSchedulableJobs():
                job.setMILPConstraint(self.MILPModel.Constraint(0,1,job.getOperation().getName()+"_"+str(jobid)+'_cons'))
                jobid+=1
                matchid = 0

                if len(job.getOperation().getAlternativeResources()) == 0:
                    progress.value+=" CHECK: Operation "+job.getOperation().getName()+" has no alternative machine..."+"\n"
                
                for mach in job.getOperation().getAlternativeResources():
                    mymach = self.getMachineDict()[mach]

                    currentshift = mymach.getMyShifts()[0]
                    slotstart = currentshift.getStartTime()
             
                    currentslotshifts = []
                    for schid in range(len(mymach.getSchedule())):
                        
                        schtuple = mymach.getSchedule()[schid]
                        timelength = mymach.getTimeLength(slotstart,schtuple[0][1])

                        if timelength >= job.getProcessTime(mymach):
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
                    timelength = mymach.getTimeLength(slotstart,lastshift.getEndTime())
                    
                    if timelength >= job.getProcessTime(mymach):
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
                        
                        nrmatches,matchid = self.findSlotMatches(objective,mymach,mach,job,timelength,currentslotshifts,slotstart,lastshift.getEndTime(),nrmatches,matchid)

         
        except Exception as e:
            progress.value+="ERROR: in find matches "+str(e)+"\n"
        

        return nrmatches


#______________________________________________________________________
######################################################################################################################
    def findSlotMatches(self,objective,mymach,mach,job,slotlength,currentslotshifts,slotstart,jobschstart,nrmatches,matchid):

        progress = self.getProgress()
        currentincrement = 15      
                        
        for shiftid in range(len(currentslotshifts)):

            slotshift = currentslotshifts[shiftid]
            currentstart = max(slotstart,slotshift.getStartTime())
            currentincrement = (1+int(shiftid>0))*currentincrement
                
            while currentstart <= min(slotshift.getEndTime(),jobschstart):
                funcreturn = self.checkFeasibility(mymach,slotlength,currentslotshifts,slotshift,currentstart,job)
                if funcreturn[0]:
                    
                        
                    nrmatches+=1
                    mymatch = MatchVar(mymach,job,currentstart,slotshift,funcreturn[1])
                    matchvar = self.MILPModel.IntVar(0.0,1,'x_'+str(mach.getMachineCode())+'_'+str(job.getID())+"_"+str(matchid))  # x_{m,j}
                    deadline_coeff =((self.getMaxDeadLine()-job.getDeadLine()).days) /((self.getMaxDeadLine() -self.getMinDeadLine()).days)
                    obj_coeff = 10*deadline_coeff+25*(self.getTimeHorizon()-funcreturn[1])/self.getTimeHorizon()+5*job.getProcessTime(mymach)/self.getTimeHorizon()
                    matchid+=1
                    
                   
                    job.getMILPConstraint().SetCoefficient(matchvar,1)
                    mymatch.updateCapacityConstraints(currentslotshifts,slotshift,self)
                    objective.SetCoefficient(matchvar,obj_coeff)
      
                    mymach.getMatches().append(mymatch)
                    mymatch.setMILPVar(matchvar)

                    if mach.getName() == "M3-01_(FR3_01)":
                        progress.value+=">> Match: "+str(mymatch.printMatch())+", job: "+str(job.getProduct().getPN())+"\n"
    
                currentstart+=currentincrement



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
        
                       
                for mymatch in mach.getMatches():
                    for mymatch2 in mach.getMatches():
        
                        if mymatch == mymatch2:
                            continue
        
                        if mymatch2.getStart() < mymatch.getStart():
                            continue
        
                        if mymatch2.getStart() > mymatch.getCompletion():
                            continue
        
                        # st2 >= cp1 or cp2 <= st1 
                        if (mymatch.getCompletion() <= mymatch2.getStart()) or (mymatch2.getCompletion() <= mymatch.getStart()) :
                            continue
         
                           
                        confcons = self.MILPModel.Constraint(0,1,mach.getMachine().getName()+'_'+mymatch.getJob().getOperation().getName()+'_'+mymatch2.getJob().getOperation().getName()+"_"+str(confid)+'_conf')
                        confid+=1
        
                                #if mach.getMachine().getName() == "M3-01_(FR3_01)":
                                #    progress.value+="Conflict "+"\n"
                                #    progress.value+=mymatch.printMatch()+"\n"
                                #    progress.value+=mymatch2.printMatch()+"\n"
                                #    progress.value+="Conflict "+"\n"
                               
                        confcons.SetCoefficient(mymatch.getMILPVar(),1)
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
                    
                    if mymatch.getMILPVar().solution_value() > 0:
                        nrscheduled+=1
                        machschs+=1
                        #progress.value+= "Variable: "+str(mymatch.getMILPVar().name)+", val: "+str(mymatch.getMILPVar().solution_value())+"\n"
                        currshift = mymatch.getStartShift()
                        while currshift.getEndTime() < mymatch.getCompletion():
                            currshift = currshift.getNext()

                        mymatch.getJob().getOperation().setStart(self.convertSimTimeToDate(mymatch.getStart()))
                        mymatch.getJob().getOperation().setCompletion(self.convertSimTimeToDate(mymatch.getCompletion()))
                        mach.getSchedule().append(((mymatch.getStartShift(),mymatch.getStart()),(currshift,mymatch.getCompletion())))
                        mach.getJobStarts().append((mymatch.getJob(),mymatch.getStart()))

                        mymatch.getJob().setStart(mymatch.getStart())
                        mymatch.getJob().setCompletion(mymatch.getCompletion())
                        mymatch.getJob().setScheduled()
                        
                        
                        #self.scheduleJob(mymatch.getJob(),mymatch.getStart(),mymatch.getCompletion(),mach)
    
                mach.getSchedule().sort(key=lambda x:x[1][1], reverse=False)
                mach.getJobStarts().sort(key=lambda x: x[1], reverse=False)
                progress.value+= "Schedule of mach: "+mach.getMachine().getName()+"\n"
                for schid in range(len(mach.getJobStarts())):
                    schtuple = mach.getSchedule()[schid]; starttuple = mach.getJobStarts()[schid]
                    
                    progress.value+= "Job: "+starttuple[0].getProduct().getPN()+" ("+str(self.convertSimTimeToDate(schtuple[0][1]))+"-"+str(self.convertSimTimeToDate(schtuple[1][1]))+"), d: "+str(starttuple[0].getDeadLine())+", p: "+str(starttuple[0].getOperation().getRandVar().sampleValue())+"\n"
                #if machschs > 0:
                
        except Exception as e:
            progress.value+="ERROR: in reading the solution "+str(e)+"\n"

        return nrscheduled

