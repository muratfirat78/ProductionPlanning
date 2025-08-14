
class GreedyInsertionAlg:
    def __init__(self):
        self.timelimit = 60

    def CheckFTEAvailability(self,res,job,jobstarttime,startshift,ScheduleMgr):

        if res!= "Machine":
            return True

        #Progress.value+="FTE availability check..."+"\n"

        curr_time = jobstarttime
        processtime = job.getQuantity()*job.getOperation().getProcessTime()
        curr_shift = startshift
      
        while processtime > 0: 

            fte_use = ScheduleMgr.CalculateFTEUse(res,curr_shift)
            ftecapacity = sum([int(curr_shift in opr.getShiftAvailability()) for opr in res.getMachineGroup().getOperatingTeam().getOperators()])
            
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
                
                while not res.getShiftAvailability()[curr_shift]: 
                    curr_shift = curr_shift.getNext()
                    if curr_shift == None:
                        return False
                    curr_time = curr_shift.getStartTime()
 
        return True



    def CheckSlot(self,resource,job,Progress,ScheduleMgr):
        time =  job.getLatestPredecessorCompletion()

        if resource.getName().find("OUT -") != -1:
            slot = resource.getEmptySlots()[0]
            return (slot,(time,0))

        
        for slot in resource.getEmptySlots():    
            if slot[0][1] < job.getQuantity()*job.getOperation().getProcessTime():
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
            
            if not (resource.getShiftAvailability()[curr_shift]):
                reasonstr+=" resource not available.."
            #Progress.value+=" 2: "+reasonstr+"\n"
            proper = (proper) and (resource.getShiftAvailability()[curr_shift])
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

                if length < job.getQuantity()*job.getOperation().getProcessTime(): 
                    #Progress.value+="Length did not survive: "+str(length)+"\n"
                    break

                reasonstr =" Shift: "+str(curr_shift.getDay())+"-"+str(curr_shift.getNumber())+" r: "
                proper = (curr_shift.getEndTime() >= time)
                if not proper: 
                    reasonstr+=" Time > shift end.."
                    continue
                  
                if not (resource.getShiftAvailability()[curr_shift]):
                    reasonstr+="+ resource not available.."
                proper = (proper) and (resource.getShiftAvailability()[curr_shift])
                        
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
                if length < job.getQuantity()*job.getOperation().getProcessTime(): 
                    continue 
                    
            unusedtime += max(time-curr_time,0)
            length -= max(time-curr_time,0)


            #Progress.value+="unused: "+str(unusedtime)+", length "+str(length)+"\n"
        
            if length < job.getQuantity()*job.getOperation().getProcessTime(): 
                continue 
                   
            jobstarttime = max(time, curr_time)

            #Progress.value+="jobstarttime: "+str(jobstarttime)+"\n"
        
            return ((slot,curr_shift),(jobstarttime, unusedtime))
    
        return None  # meaning that the resource cannot process the job due to fully scheduled… 


    def ScheduleJob(self,res,job,jobstarttime,unusedtime,emptyslot,startshift):
        job.SetScheduled()
        job.setScheduledResource(res)
        job.setScheduledShift(startshift)
        job.setStartTime(jobstarttime)  

        if res.getName().find("OUT -") != -1:
            job.setCompletionTime(job.getStartTime()+job.getOperation().getProcessTime())
            res.getSchedule()[emptyslot[1]].append(job)
            return
        
        curr_time = emptyslot[0][0]
        

        curr_time = jobstarttime
        processtime = job.getQuantity()*job.getOperation().getProcessTime()
        curr_shift = startshift
      
        #find completion time of the job

        #self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="finding completion..."+"\n"
        while processtime > 0: 
            res.getSchedule()[curr_shift].append(job)
            timeinshift =  curr_shift.getEndTime()+1 - curr_time
            #self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="time in Shft: "+str(curr_shift.getDay())+","+str(curr_shift.getNumber())+") "+str(timeinshift)+"\n"
            
            if timeinshift < processtime - 0.00001:
                processtime = processtime - timeinshift
            else:
                curr_time = curr_time + processtime
                processtime = 0
            #self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="remianed proc time"+ str(processtime)+"\n"

            if processtime > 0:
                curr_shift=curr_shift.getNext()
                curr_time = curr_shift.getStartTime()
                
                while not res.getShiftAvailability()[curr_shift]: 
                    curr_shift = curr_shift.getNext()
                    if curr_shift == None:
                        return None
                    curr_time = curr_shift.getStartTime()
 

        #self.getVisualManager().getSchedulingTab().getPSchScheRes().value+="completion time ..."+str(curr_time)+"\n"
        job.setCompletionTime(curr_time)

        slotindex = res.getEmptySlots().index(emptyslot)
        if unusedtime > 0: # here a hole occurred in timeline, so create an empty slot
            newslot = ((emptyslot[0][0], unusedtime),emptyslot[1])
            res.getEmptySlots().insert(res.getEmptySlots().index(emptyslot),newslot) # insert this just before into the index of empyslot.
            slotindex+=1


        job.setScheduledCompShift(curr_shift)

        res.getEmptySlots().remove(emptyslot)
        newmeptyslot= ((curr_time, emptyslot[0][1] - (unusedtime+job.getQuantity()*job.getOperation().getProcessTime())),curr_shift)
        res.getEmptySlots().insert(slotindex,newmeptyslot)

        return newmeptyslot

    def SolveScheduling(self,AllJobs,ScheduleMgr,Progress):
 
        SchedulableJobs= [] 

        #Progress.value+=" Simple greedy insertion starts.."+"\n"  

        for job in AllJobs:  
            if job.IsSchedulable():
                SchedulableJobs.append(job)
                

        while len(SchedulableJobs) >0:
            ScheduledJobs = []
            JobsToRemove = []
            nrscheduled = 0
            
            for j in SchedulableJobs:
                prednames = ""

                for pred in j.getPredecessors():
                    prednames+="-"+pred.getName()
                
                #Progress.value+=" Checking job "+str(j.getName())+", LPCT: "+str(j.getLatestPredecessorCompletion())+", p: "+str(j.getQuantity()*j.getOperation().getProcessTime())+", prd: "+prednames+"\n"  

                #Progress.value+=" Operation: "+str(j.getOperation().getName())+", res: "+str(len(j.getOperation().getRequiredResources()))+"\n"
              
                myresource = None
                for resource in j.getOperation().getRequiredResources():
                    myresource = resource
                    if isinstance(resource,list):
                        myresource = resource[0]
                        #Progress.value+=" ***res: "+str(myresource.getName())+"\n"
                        break
                if myresource == None: 
                    #Progress.value+=" Op: "+str(j.getOperation().getName())+" has no resource.."+"\n"
                    JobsToRemove.append(j)
                    continue
                    
                #Progress.value+="..Check slot res.. "+str(myresource.getName())+"\n"  
                schreturn = self.CheckSlot(myresource,j,Progress,ScheduleMgr)
                if schreturn == None: 
                    #Progress.value+=str(j.getName())+" cannot be scheduled in "+myresource.getName()+"\n"
                    JobsToRemove.append(j)
                    continue
                else: 
                   # Progress.value+=" Scheduling job "+str(j.getName())+"\n"  
                    slotinfo,scheinfo = schreturn 
                    slot,startshift = slotinfo
                    jobstarttime, unusedtime = scheinfo 
                    
                    #Progress.value+=" jobstarttime "+str(jobstarttime)+", unusedtime: "+str(unusedtime)+"\n" 

                    #Progress.value+=" Slot: St: "+str(slot[0][0])+", l: "+str(slot[0][1])+", Shft: ("+str(slot[1].getDay())+","+str(slot[1].getNumber())+")"+"\n" 

                    #if not slot[1] in myresource.getSchedule():
                        #Progress.value+=" Shift not in the sechdule!!!!!!!!!!"+"\n" 

                
                    newslot = self.ScheduleJob(myresource,j,jobstarttime,unusedtime,slot,startshift)
                    #Progress.value+=str(j.getName())+"scheduled "+myresource.getName()+", st "+str(jobstarttime)+".. "+"\n"
                    #Progress.value+=str(j.getName())+"scheduled ct: "+str(j.getCompletionTime())+", st: "+str(jobstarttime)+".. "+"\n"

                    #Progress.value+=" NEW Slot: St: "+str(newslot[0][0])+", l: "+str(newslot[0][1])+", Shft: ("+str(newslot[1].getDay())+","+str(newslot[1].getNumber())+")"+"\n" 

                    #if myresource.getMachineGroup() != None:
                        #if myresource.getMachineGroup().getOperatingTeam() != None: 
                            #fteuse = ScheduleMgr.CalculateFTEUse(myresource,newslot[1])
                            #ftecapacity = sum([int(newslot[1] in opr.getShiftAvailability()) for opr in myresource.getMachineGroup().getOperatingTeam().getOperators()])
                            #if fteuse > ftecapacity:
                                #Progress.value+=" FTE use XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"+"\n"
                            #Progress.value+=" FTE use in start shift: "+ str(fteuse)+", capacity: "+str(ftecapacity)+"\n"

                    #for myslot in resource.getEmptySlots(): 
                    #    Progress.value+=" **Slot: St: "+str(myslot[0][0])+", l: "+str(myslot[0][1])+", Sh: ("+str(myslot[1].getDay())+","+str(myslot[1].getNumber())+")"+"\n" 
                    
                    ScheduledJobs.append(j)
                    #Progress.value+=" sucessors "+str(len(j.getSuccessors()))+"\n"
                    for successor in j.getSuccessors():
                        #Progress.value+=" sucessor: "+ str(successor.getName())+", btch "+str(successor.IsBatched())+", schlbl "+str(successor.IsSchedulable())+"\n"
                        if successor.IsBatched():
                            continue
                        if successor.IsSchedulable():
                            SchedulableJobs.append(successor)
                    #Progress.value+=">>>>>>>>>>> SchedulableJobs: "+str(len(SchedulableJobs))+"\n"
            
            for j in ScheduledJobs:
                SchedulableJobs.remove(j)
            for j in JobsToRemove:
                SchedulableJobs.remove(j)
            

            
        return 
        
        