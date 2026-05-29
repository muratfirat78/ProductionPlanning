from Simulator import *
from datetime import timedelta,date
from productionobjects import *
from productionalgs import *
from productionChecker import *
from productiondata import *
from datetime import timedelta,date,datetime
import numpy as np
import pandas as pd


class Job(object):
    def __init__(self,myopr):
    
        self.Operation = myopr
        self.Scheduled = False
        self.Matches = dict() # key: Mach, value: (start,comp)
        self.Predecessor = None # to be found after contsruction. 
        self.Successor = None # to be found after contsruction. 
        self.deadline = None


    def getOperation(self):
        return self.Operation
    def isScheduled(self):
        return self.Scheduled
    def setScheduled(self):
        self.Scheduled = True
        return

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

    def getMatches(self):
        return self.Matches

    def setDeadLine(self,dd):
        self.deadline = dd
        return 
    def getDeadLine(self,dd):
        return self.deadline 

    def isSchedulable(self):
        if self.getPredecessor() == None:
            return True
        else:
            if self.getPredecessor().isScheduled():
                return True
            else:
                return False
        
################################################################################
class SchMachine(object):
    def __init__(self,mymach):

        self.Machine = mymach
        self.Matches = dict() # key: job, value: (start,comp)
        self.Schedule = dict() # key: job, value: (start,comp)

    def getSchedule(self):
        return self.Schedule

    def getMachine(self):
        return self.Machine
    def getMatches(self):
        return self.Matches


################################################################################
    

#################################################################################
class ProductionMILPManager(MILPManager): 
    def __init__(self,sim):
        super().__init__(sim)

        self.Jobs = []
        self.Machines = [] 
        self.SchedulableJobs = []
        self.Operators = []
        self.TimeHorizon = None   
        self.shift_minutes = 480
        self.shiftmapping = {0:3,8:1,16:2}

    def getJobs(self):
        return self.Jobs
    def getMachines(self):
        return self.Machines
    def getOperators(self):
        return self.Operators
        
    def convertSimTimeToDate(self,mytime):    
        return self.getSimulator().getStartDay()+timedelta(minutes = mytime)

    def startFeasible(self,machine,starttime,job):


        # first check if the machine is available at start time
        if not self.getShiftNo(starttime) in machine.getMachine().getAvailableShifts():
            return False

        # second check start conflicting jobs      
        for job,jobsch in machine.getSchedule().items():
            if jobsch[0] <= starttime and jobsch[1] >= starttime:
                return False
                
        # tracking the start till the completion 
        currenttime = starttime
        procss_shft_strt = currenttime
        proctime = job.getOperation.getProcessTime()

        while proctime > 0: 
            
            curr_shiftstart = (currenttime//self.shift_minutes)*self.shift_minutes
            curr_shiftsend = curr_shiftstart+self.shift_minutes*int((currenttime%self.shift_minutes)>0)

            if not self.getShiftNo(currenttime) in machine.getMachine().getAvailableShifts():
                # machine not available, parameters updated, but no drop in processing time
                currenttime = curr_shiftsend
                procss_shft_strt = curr_shiftsend
            else:
                if proctime < curr_shiftsend - procss_shft_strt: 
                    # processing finishes in the current shift
                    currenttime = min(procss_shft_strt+proctime,curr_shiftsend)
                    proctime = 0
                    
                else: 
                    # remaining process time makes overflow to the next shift
                    currenttime = curr_shiftsend
                    proctime -= (curr_shiftsend - procss_shft_strt)
                    procss_shft_strt = curr_shiftsend
                    
        # currenttime is not completion time
        
        # check completion conflicting jobs
        for job,jobsch in machine.getSchedule().items():
            if jobsch[0] <= currenttime and jobsch[1] >= currenttime:
                return False

        # now only jobs that are processed between start and completions times are left. 
        for job,jobsch in machine.getSchedule().items():
            if jobsch[0] >= starttime and jobsch[1] <= currenttime:
                return False
                
        
        return True


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
        

##############################################################################
    def constructInstance(self):

        progress = self.getProgress()

        progress.value+=" Scheduling problem instance construction \n" 

       
        self.setTimeHorizon(self.getSimulator().getTimeLimit())

        try: 
            # iterate production orders to construct jobs. 
            for prodorder in self.getSimulator().getController().getWorkManager().getSelectedOrders():
    
                operation_sequence = prodorder.getFinalProduct().getOperationSequences()[prodorder.getID()]
    
                previous_job = None
                oprid = 1
                for operation in operation_sequence:
                    myjob = Job(operation)
                    if previous_job!= None:
                        previous_job.setSuccessor(myjob)
                        myjob.setPredecessor(previous_job)
                    self.getJobs().append(myjob)
                    if oprid == len(operation_sequence): # last job
                        myjob.setDeadLine(prodorder.getDeadline())
                        
                    oprid+=1
                    previous_job = myjob

            # iterate resources to construct Machines and get operators
            for resource in self.getSimulator().getController().getWorkManager().getResources():
                if isinstance(resource,Machine):
                    mymachine = SchMachine(resource)
                    self.getMachines().append(mymachine)  
                if isinstance(resource,Operator):
                    self.getOperators().append(resource)

             
             
            self.findSchedulables()

            progress.value+=" > Selected orders: "+str(len(self.getSimulator().getController().getWorkManager().getSelectedOrders()))+"\n"
            progress.value+=" > Time horizon: "+str(self.getTimeHorizon())+"\n"
            progress.value+=" > No Jobs: "+str(len(self.getJobs()))+ "\n" 
            progress.value+=" > No Machines: "+str(len(self.getMachines()))+", No Operators: "+str(len(self.getOperators()))+"\n"
            progress.value+=" > No Schedulables: "+str(len(self.getSchedulableJobs()))+ "\n"

            # time count: 

            mytime = 0

            while mytime < self.getTimeHorizon():
                
                progress.value+=" > Sch shift "+str(self.getShiftNo(mytime))+" on date "+str(self.convertSimTimeToDate(mytime))+ "\n"
                for mach in self.getMachines():
                    progress.value+=" > Machine "+mach.getMachine().getName()+" available: "+str(self.getShiftNo(mytime) in mach.getMachine().getAvailableShifts())+"\n"
                mytime+=self.shift_minutes
                progress.value+="_________________________________________________"+ "\n"
                
            
            
        except Exception as e:
            progress.value+="ERROR: MILP instance contruction "+str(e)+"\n"
            
        return
    
#############################################################################
    def FindMatches(self):

    
        for job in self.getJobs():
            job.getMatches().clear()
        for mach in self.getMachines():
            mach.getMatches().clear()

        self.findSchedulables()

        for job in self.getSchedulableJobs():
            for mach in job.getOperation().getAlternativeResources():
                if not mach in self.getMachines():
                    progress.value+="ERROR: MILP instance contruction "+str(e)+"\n"
        


        return 
############################################################################
    def createConstraints(self):

   
        return 

#_____________________________________________________________________
    def createObjective(self): 
    

        return
#______________________________________________________________________
############################################################################
    def solveProblem(self):

       

        return
#################################################################################################################################################
 