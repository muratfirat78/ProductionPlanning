
class AdvancedGreedyInsertionAlg:
    def __init__(self):
        self.timelimit = 60

    def SolveScheduling(self,AllJobs,ScheduleMgr,Progress):
 
        SchedulableJobs= [] 

        Progress.value+=" Simple greedy insertion starts.."+"\n"  

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
                
                Progress.value+=" Checking job "+str(j.getName())+", LPCT: "+str(j.getLatestPredecessorCompletion())+", p: "+str(j.getQuantity()*j.getOperation().getProcessTime())+", prd: "+prednames+"\n"  

                #Progress.value+=" Operation: "+str(j.getOperation().getName())+", res: "+str(len(j.getOperation().getRequiredResources()))+"\n"
              
                myresource = None
                for resource in j.getOperation().getRequiredResources():
                    myresource = resource
                    if isinstance(resource,list):
                        myresource = resource[0]
                        #Progress.value+=" ***res: "+str(myresource.getName())+"\n"
                        break
                if myresource == None: 
                    Progress.value+=" Op: "+str(j.getOperation().getName())+" has no resource.."+"\n"
                    JobsToRemove.append(j)
                    continue
                    
                Progress.value+="..Resource "+str(myresource.getName())+"\n"  
                schreturn = ScheduleMgr.CheckSlot(myresource,j)
                if schreturn == None: 
                    Progress.value+=str(j.getName())+" cannot be scheduled in "+myresource.getName()+"\n"
                    JobsToRemove.append(j)
                    continue
                else: 
                    Progress.value+=" Scheduling job "+str(j.getName())+"\n"  
                    slotinfo,scheinfo = schreturn 
                    slot,startshift = slotinfo
                    jobstarttime, unusedtime = scheinfo 
                    
                    Progress.value+=" jobstarttime "+str(jobstarttime)+", unusedtime: "+str(unusedtime)+"\n" 

                    Progress.value+=" Slot: St: "+str(slot[0][0])+", l: "+str(slot[0][1])+", Shft: ("+str(slot[1].getDay())+","+str(slot[1].getNumber())+")"+"\n" 

                    if not slot[1] in myresource.getSchedule():
                        Progress.value+=" Shift not in the sechdule!!!!!!!!!!"+"\n" 

                
                    newslot = ScheduleMgr.ScheduleJob(myresource,j,jobstarttime,unusedtime,slot,startshift)
                    #Progress.value+=str(j.getName())+"scheduled "+myresource.getName()+", st "+str(jobstarttime)+".. "+"\n"
                    Progress.value+=str(j.getName())+"scheduled ct: "+str(j.getCompletionTime())+", st: "+str(jobstarttime)+".. "+"\n"

                    Progress.value+=" NEW Slot: St: "+str(newslot[0][0])+", l: "+str(newslot[0][1])+", Shft: ("+str(newslot[1].getDay())+","+str(newslot[1].getNumber())+")"+"\n" 

                    if myresource.getMachineGroup() != None:
                        if myresource.getMachineGroup().getOperatingTeam() != None: 
                            fteuse = ScheduleMgr.CalculateFTEUse(myresource,newslot[1])
                            ftecapacity = sum([int(newslot[1] in opr.getShiftAvailability()) for opr in myresource.getMachineGroup().getOperatingTeam().getOperators()])
                            if fteuse > ftecapacity:
                                Progress.value+=" FTE use XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"+"\n"
                            Progress.value+=" FTE use in start shift: "+ str(fteuse)+", capacity: "+str(ftecapacity)+"\n"

                    #for myslot in resource.getEmptySlots(): 
                    #    Progress.value+=" **Slot: St: "+str(myslot[0][0])+", l: "+str(myslot[0][1])+", Sh: ("+str(myslot[1].getDay())+","+str(myslot[1].getNumber())+")"+"\n" 
                    
                    ScheduledJobs.append(j)
                    if j.getSuccessor() != None and j.getSuccessor().IsSchedulable():
                        SchedulableJobs.append(j.getSuccessor())
            for j in ScheduledJobs:
                SchedulableJobs.remove(j)
            for j in JobsToRemove:
                SchedulableJobs.remove(j)

            
        return 
        
        