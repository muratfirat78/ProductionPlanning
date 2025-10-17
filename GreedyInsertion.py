from PlanningObjects import *

class GreedyInsertionAlg:
    def __init__(self):
        self.timelimit = 60
        self.name = "SimpleGreedy"

    def CheckFTEAvailability(self,res,job,jobstarttime,startshift,ScheduleMgr):

        if res!= "Machine":
            return True

        if res.getProcessType() != "Metal forming":
            return True

        #Progress.value+="FTE availability check..."+"\n"

        curr_time = jobstarttime
        processtime = job.getJob().getQuantity()*job.getJob().getOperation().getProcessTime()
        curr_shift = startshift
      
        while processtime > 0: 

            fte_use = ScheduleMgr.CalculateFTEUse(res,curr_shift)  
            ftecapacity = ScheduleMgr.getDataManager().getFTECapacity(res.getProcessType(),shift)
            
      
            timeinshift =  curr_shift.getEndTime()+1 - curr_time
            if timeinshift < processtime:
                processtime = processtime - timeinshift
                fte_use += timeinshift/(curr_shift.getEndTime()-curr_shift.getStartTime()+1)
            else:
                curr_time = curr_time + processtime
                fte_use += processtime/(curr_shift.getEndTime()-curr_shift.getStartTime()+1)
                processtime = 0

            if fte_use > ftecapacity:
                return False

            if processtime > 0:
                curr_shift=curr_shift.getNext()
                curr_time = curr_shift.getStartTime()
                
                while not curr_shift.getNumber() in res.getAvailableShifts(): 
                    curr_shift = curr_shift.getNext()
                    if curr_shift == None:
                        return False
                    curr_time = curr_shift.getStartTime()
 
        return True



    def CheckSlot(self,resource,job,Progress,ScheduleMgr):

        #Progress.value+=" checking slot, job "+str(job.getJob().getName())+"\n"
        time =  job.getLatestPredecessorCompletion()


        if resource.getName().find("OUT -") != -1:
            slot = resource.getEmptySlots()[0]
            return ((slot,slot[1]),(time,0))

        
        for slot in resource.getEmptySlots():    
            if slot[0][1] < job.getJob().getQuantity()*job.getJob().getOperation().getProcessTime():
                continue
            if (slot[1].getNext() == None) and (slot[1].getEndTime() < time):
                return None
   
            length = slot[0][1]; curr_shift = slot[1]; curr_time = slot[0][0]

            #Progress.value+=" checking slot, Shift: "+str(curr_shift.getDay())+"-"+str(curr_shift.getNumber())+"\n"
            #Progress.value+=" slot start "+str(curr_time)+", length "+str(length)+"> "+", LPCT "+str(time)+"\n"


            unusedtime = 0

            reasonstr =" Shift: "+str(curr_shift.getDay())+"-"+str(curr_shift.getNumber())+" r: "
            proper = (curr_shift.getEndTime() >= time)
            if not proper: 
                reasonstr+=" Time > shift end.."
            #Progress.value+=" 1: "+reasonstr+"\n"
            
            if not curr_shift.getNumber() in resource.getAvailableShifts():
                reasonstr+=" resource not available.."
            #Progress.value+=" 2: "+reasonstr+"\n"
            proper = (proper) and (curr_shift.getNumber() in resource.getAvailableShifts())
            if resource.getType() == "Machine": 
                if (resource.getShiftOperatingModes()[curr_shift] == "Self-Running"):
                    reasonstr+=" self-running, job cannot start.."
                proper = proper and (not (resource.getShiftOperatingModes()[curr_shift] == "Self-Running"))
            #Progress.value+=" 3: "+reasonstr+"\n"
            if not self.CheckFTEAvailability(resource,job,curr_time,curr_shift,ScheduleMgr):
                reasonstr+="+  fte unavailable.."
            proper = proper and (self.CheckFTEAvailability(resource,job,curr_time,curr_shift,ScheduleMgr))
            #Progress.value+=" 4: "+reasonstr+", proper: "+str(proper)+"\n"

                    
            while not proper: 
          
                #Progress.value+=reasonstr+"\n"
                if (curr_shift.getNext() == None):
                    return None
                length -= (curr_shift.getEndTime()+1-curr_time)
                unusedtime += (curr_shift.getEndTime()+1-curr_time)
                curr_shift = curr_shift.getNext()    
                curr_time = curr_shift.getStartTime()

                if length < job.getJob().getQuantity()*job.getJob().getOperation().getProcessTime(): 
                    #Progress.value+="Length did not survive: "+str(length)+"\n"
                    break

                reasonstr =" Shift: "+str(curr_shift.getDay())+"-"+str(curr_shift.getNumber())+" r: "
                proper = (curr_shift.getEndTime() >= time)
                if not proper: 
                    reasonstr+=" Time > shift end.."
                    continue
                  
                if not curr_shift.getNumber() in resource.getAvailableShifts():
                    reasonstr+="+ resource not available.."
                proper = (proper) and (curr_shift.getNumber() in resource.getAvailableShifts())
                        
                if not proper: 
                    continue 
                            
                if resource.getType() == "Machine": 
                    if (resource.getShiftOperatingModes()[curr_shift] == "Self-Running"):
                        reasonstr+="+self-running, job cannot start.."
                    proper = proper and (not (resource.getShiftOperatingModes()[curr_shift] == "Self-Running"))
                    if not proper: 
                        continue

                
                if not self.CheckFTEAvailability(resource,job,curr_time,curr_shift,ScheduleMgr):
                    reasonstr+="+  fte unavailable.."
                proper = proper and (self.CheckFTEAvailability(resource,job,curr_time,curr_shift,ScheduleMgr))
                
            if not proper: 
                if length < job.getJob().getQuantity()*job.getJob().getOperation().getProcessTime(): 
                    continue 
                    
            unusedtime += max(time-curr_time,0)
            length -= max(time-curr_time,0)


            #Progress.value+="unused: "+str(unusedtime)+", length "+str(length)+"\n"
        
            if length < job.getJob().getQuantity()*job.getJob().getOperation().getProcessTime(): 
                continue 
                   
            jobstarttime = max(time, curr_time)

            #Progress.value+="jobstarttime: "+str(jobstarttime)+"\n"
        
            return ((slot,curr_shift),(jobstarttime, unusedtime))
    
        return None  # meaning that the resource cannot process the job due to fully scheduled… 


    def ScheduleJob(self,res,job,jobstarttime,unusedtime,emptyslot,startshift,Progress,schedulesol):
        
        Progress.value+=" Scheduling job "+str(job.getJob().getID())+"\n"
        job.SetScheduled()
        job.setScheduledResource(res)
        job.setScheduledShift(startshift)
        job.setStartTime(jobstarttime)  

        Progress.value+="Main assignments done.."+"\n"

        Progress.value+=" >>> "+str(res.getName())+"\n"

        Progress.value+=" emptyslot >>> "+str(emptyslot)+"\n"

        if emptyslot != None: 
            Progress.value+=" Sh:("+str(emptyslot[1].getDay())+","+str(emptyslot[1].getNumber())+"), hrs: ["+str(emptyslot[1].getStartTime())+"-"+str(emptyslot[1].getEndTime())+"]\n" 
                    
      
        if res.getName().find("OUT -") != -1:
            
            #Progress.value+=">>> "+str(job.getStartTime())+"  -  "+str(job.getJob().getOperation().getProcessTime())+"\n"
            job.setCompletionTime(job.getStartTime()+job.getJob().getOperation().getProcessTime())
            
            #Progress.value+=" In Schedule? >>> "+str(emptyslot[1] in res.getCurrentSchedule())+"\n"
            res.getCurrentSchedule()[emptyslot[1]].append(job)
            return
        
        curr_time = emptyslot[0][0]

       

        curr_time = jobstarttime
        processtime = job.getJob().getQuantity()*job.getJob().getOperation().getProcessTime()
        curr_shift = startshift
      
        #find completion time of the job

        Progress.value+="finding completion..."+"\n"
        while processtime > 0: 

            Progress.value+=" currshift in sch of res? "+str(curr_shift in res.getCurrentSchedule())+"\n"

            if not curr_shift in res.getCurrentSchedule():
                Progress.value+=" currsch of res has "+str(len())+" shifts"+"\n"
              
            res.getCurrentSchedule()[curr_shift].append(job)
            timeinshift =  curr_shift.getEndTime()+1 - curr_time

           
            
            if timeinshift < processtime - 0.00001:
                processtime = processtime - timeinshift
            else:
                Progress.value+=" Scheduling filled as job completed.. "+str(curr_shift in schedulesol.getResourceSchedules()[res.getName()])+"\n"
          
                schedulesol.getResourceSchedules()[res.getName()][curr_shift][job] = (curr_time,curr_time + processtime)
                
                curr_time = curr_time + processtime
                processtime = 0

            if processtime > 0:
                Progress.value+=" process time left "+str(processtime)+"\n"

                Progress.value+=" Scheduling soln has the resource? "+str(res.getName() in schedulesol.getResourceSchedules())+"\n"

                Progress.value+=" Scheduling soln has shift? "+str(curr_shift in schedulesol.getResourceSchedules()[res.getName()])+"\n"

                schedulesol.getResourceSchedules()[res.getName()][curr_shift][job] = (curr_time,curr_shift.getEndTime()+1)


                Progress.value+=" curr hisft next? "+str(curr_shift.getNext())+"\n"
                
            
                curr_shift=curr_shift.getNext()
                curr_time = curr_shift.getStartTime()


                Progress.value+=" currshift available? "+str(curr_shift.getNumber() in res.getAvailableShifts())+"\n"
                while not curr_shift.getNumber() in res.getAvailableShifts():
                    curr_shift = curr_shift.getNext()
                    if curr_shift == None:
                        return None
                    curr_time = curr_shift.getStartTime()

                Progress.value+=" Sh:("+str(emptyslot[1].getDay())+","+str(curr_shift.getNumber())+"), hrs: ["+str(curr_shift.getStartTime())+"-"+str(emptyslot[1].getEndTime())+"]\n" 
                    

                Progress.value+=" currshift in avail of res? "+str(curr_shift.getNumber() in res.getAvailableShifts())+"\n"
                Progress.value+=" currshift in sch of res? "+str(curr_shift in res.getCurrentSchedule())+"\n"
                
        job.setCompletionTime(curr_time)
        Progress.value+=" job completiontime "+str(job.getCompletionTime())+"\n"

        slotindex = res.getEmptySlots().index(emptyslot)
        if unusedtime > 0: # here a hole occurred in timeline, so create an empty slot
            newslot = ((emptyslot[0][0], unusedtime),emptyslot[1])
            res.getEmptySlots().insert(res.getEmptySlots().index(emptyslot),newslot) # insert this just before into the index of empyslot.
            slotindex+=1


        job.setScheduledCompShift(curr_shift)
      

        res.getEmptySlots().remove(emptyslot)
        newmeptyslot= ((curr_time, emptyslot[0][1] - (unusedtime+job.getJob().getQuantity()*job.getJob().getOperation().getProcessTime())),curr_shift)
        res.getEmptySlots().insert(slotindex,newmeptyslot)

        Progress.value+="Done..."+"\n"

        return newmeptyslot

    def SolveScheduling(self,AllJobs,ScheduleMgr,Progress):

        #initialize schedule solution object
        sch_sol = ScheduleSolution(self.name)
        for resname,res in ScheduleMgr.getDataManager().getResources().items():
            sch_sol.getResourceSchedules()[resname] = dict()
            for shift,jobs in res.getCurrentSchedule().items():
                sch_sol.getResourceSchedules()[resname][shift] = dict()

        SchedulableJobs= [] 

        Progress.value+=" Simple greedy insertion starts.., all jobs "+str(len(AllJobs))+"\n"  

        for job in AllJobs: 
            if job.IsSchedulable():
                SchedulableJobs.append(job)

        

        while len(SchedulableJobs) >0:
            Progress.value+=" SchedulableJobs... "+str(len(SchedulableJobs))+"\n"  
            ScheduledJobs = []
            JobsToRemove = []
            nrscheduled = 0
            
            for j in SchedulableJobs:
                prednames = ""

                for pred in j.getJob().getPredecessors():
                    prednames+="-"+pred.getName()
           
                currentStarttime = None
                myresource = None
                currentslot = None
                for resource in j.getJob().getOperation().getRequiredResources():

                    Progress.value+=" checking slot for job ... "+str(j.getJob().getName())+" in res "+str(resource.getName())+"\n"  
                    slotreturn = self.CheckSlot(resource,j,Progress,ScheduleMgr)
                    
                    if slotreturn != None: 
                        if currentStarttime is None:
                            currentStarttime = slotreturn[1][0]
                            myresource = resource
                            currentslot = slotreturn
                        else:
                            if slotreturn[1][0] < currentStarttime:
                                currentStarttime = slotreturn[1][0]
                                myresource = resource
                                currentslot = slotreturn
               
                if myresource == None: 
                    JobsToRemove.append(j)
                    continue
                    
                schreturn = currentslot
                if schreturn == None: 
                    JobsToRemove.append(j)
                    continue
                else: 
                    slotinfo,scheinfo = schreturn 
                    slot,startshift = slotinfo
                    jobstarttime, unusedtime = scheinfo 
                    
                    newslot = self.ScheduleJob(myresource,j,jobstarttime,unusedtime,slot,startshift,Progress,sch_sol)
                    ScheduledJobs.append(j)
                    
                    for successor in j.getJob().getSuccessors():
                        if successor.IsBatched():
                            continue
                        if successor.getSchJob().IsSchedulable():
                            SchedulableJobs.append(successor.getSchJob())
 
            for j in ScheduledJobs:
                SchedulableJobs.remove(j)
            for j in JobsToRemove:
                SchedulableJobs.remove(j)
            
 
        Progress.value+="Scheduling completed.. "+"\n"   
        return sch_sol
        
        