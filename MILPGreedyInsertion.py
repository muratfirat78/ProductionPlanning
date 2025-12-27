from PlanningObjects import *
import time
from ortools.linear_solver import pywraplp
import os
import math


class MILPGreedyInsertionAlg:
    def __init__(self):
        self.timelimit = 60
        self.name = "MILPGreedy"

   

    def getCompletionTime(self,res,start,proctime,startshift):

        curr_time = start
        processtime = proctime
        curr_shift = startshift
        
        while processtime > 0: 
            timeinshift =  curr_shift.getEndTime()+1 - curr_time
        
            if timeinshift < processtime - 0.00001:
                processtime = processtime - timeinshift
            else:
                curr_time = curr_time + processtime
                processtime = 0
        
            if processtime > 0:
                        
                curr_shift=curr_shift.getNext()
                curr_time = curr_shift.getStartTime()
        
                while not curr_shift.getNumber() in res.getAvailableShifts():
                    curr_shift = curr_shift.getNext()
                    if curr_shift == None:
                        return None
                    curr_time = curr_shift.getStartTime()
    
        return curr_shift,curr_time

    ##################################################################################################################################################
    def SolveMILP(self,JobsinModel,ScheduleMgr,modelno,Progress,schedulesol):
        
        st = time.time() # get the start time
        #print('> Solving MILP model: ',myinstance.Name)
        
        timelimitsecs = 60
        optimalitygap = 0.05
        writeMILP = True
        Progress.value+="+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"+"\n"
        Progress.value+="Constructing MILP model starts.."+"\n"

        processtypes = ScheduleMgr.getDataManager().getProcessTypes()


        Progress.value+="Process types "+str(processtypes)+"\n"
        selectedtype = processtypes[0]

        Progress.value+="Selected Process type for fte control "+str(selectedtype)+"\n"

        machines_conflict_cons = dict() # key: machine, val: [constraints]
        jobs_cons = dict() # key: job, val: constraints
        shift_fte_cons = dict()  #key: shift, val: ftecons
        precedence_cons = dict() # key: (pred,succ), val: (cons1,cons2)
        
        matchvars = dict() #key: (mach,job), val: x_mj
        startcomps = dict() #key: (mach,job), val: (st_mj,cp_mj)
       
        machines = [res for resname,res in ScheduleMgr.getDataManager().getResources().items() if res.getType() in ["Machine","Outsourced"] ]

        Progress.value+="Model run "+str(modelno)+", machines "+str(len(machines))+"\n"
   
        jobs = JobsinModel

        solverType = "SCIP";
        solver = pywraplp.Solver.CreateSolver(solverType)
        Progress.value+="Solver "+str(solver)+"\n"
        
        if not solver:
            return


        Progress.value+="Solver created.. "+"\n"
        
        infinity = solver.infinity()
        objective = solver.Objective()    
        objective.SetMaximization()

        Progress.value+="Shift list (date,shifts).. "+str(len(ScheduleMgr.getMyShifts()))+"\n"

        for date,shifts in ScheduleMgr.getMyShifts().items():
            for shift in shifts:
                if shift.getNumber() == 3: 
                    continue
                Progress.value+=" Sh:("+str(shift.getDay())+","+str(shift.getNumber())+"), hrs: ["+str(shift.getStartTime())+"-"+str(shift.getEndTime())+"]\n" 
                ftecapacity = ScheduleMgr.getDataManager().getFTECapacity(selectedtype,shift) # no.man
                Progress.value+="shift FTE capacity: "+str(ftecapacity)+"\n"
               
                ftecapacity*=(shift.getEndTime()-shift.getStartTime()+1) # no. man-halfhour
                Progress.value+="FTE capacity: "+str(ftecapacity)+"\n"
                shift_fte_cons[shift] = solver.Constraint(0,ftecapacity,str(shift.getDay())+'_'+str(shift.getNumber())+'_cons')
             
                
        Progress.value+="shift constraints created.. "+"\n"
        
        for mach in machines:
            machines_conflict_cons[mach] = []

        
             
    #**********************************************************************************   
        for job in JobsinModel: 
            jobs_cons[job]  = solver.Constraint(0,1,job.getJob().getName()+'_cons')


            alternatives = ScheduleMgr.getAlternativeResources(job)
            alternatives = [res for res in alternatives if res in machines]

            Progress.value+="job "+str(job.getJob().getName())+" has "+str(len(alternatives))+" alternatives ("+str(len(job.getJob().getOperation().getRequiredResources()))+")"+"\n"

            job_lpc=  0
            for pred in job.getJob().getPredecessors():
                Progress.value+="pred "+str(pred.getName())+" has comp "+str(pred.getMySch().getCompletionTime())+"\n"
                job_lpc = max(job_lpc,pred.getMySch().getCompletionTime())


            Progress.value+="job "+str(job.getJob().getName())+" has  job_lpc "+str(job_lpc)+"\n"
            
            for mach in alternatives:
                cmax = mach.getLatestJobCompletion() # half-hour granularity
                if mach.getTotalJobProcessing() == 0:
                    cmax*=2

                if mach.IsAutomated():
                    mach_shift = ScheduleMgr.getShiftofTime(cmax)
                    Progress.value+=mach_shift.String("mach sh")+"\n" 
                  
                    if mach.getShiftOperatingModes()[mach_shift] == "Self-Running":
                        mach_shift = mach_shift.getNext() # no start for automated machines in shift 3
                        if mach_shift == None:
                            continue
                        cmax = mach_shift.getStartTime()

                Progress.value+="mach "+str(mach.getName())+" has ljcp "+str(cmax)+"\n"

                try: 
                    if (job_lpc > cmax) and (cmax> 0):
                        Progress.value+="efficiency check.."+"\n"
                        if (job_lpc - cmax)/mach.getTotalJobProcessing() > 0.1:
                                continue
                except Exception as e: 
                    Progress.value+="error.."+str(e)+"\n"
             
                processtime = math.ceil((job.getJob().getQuantity()*job.getJob().getOperation().getProcessTime('hour'))/2)
                
                curr_shift = None
                
                if mach.getLatestJob() != None: 
                    curr_shift= mach.getLatestJob().getScheduledCompShift()
                else: 
                    curr_shift = ScheduleMgr.getShiftofTime(16)

                try: 
                    Progress.value+=curr_shift.String("Start sh")+"\n" 
                except Exception as e: 
                    Progress.value+="error.."+str(e)+"\n"
                
                start = max(job_lpc,cmax)

                if mach.IsAutomated():
                    mach_shift = ScheduleMgr.getShiftofTime(start)
                    Progress.value+=mach_shift.String("mach sh")+"\n" 
                  
                    if mach.getShiftOperatingModes()[mach_shift] == "Self-Running":
                        mach_shift = mach_shift.getNext() # no start for automated machines in shift 3
                        if mach_shift == None:
                            continue
                        start = mach_shift.getStartTime()
                        Progress.value+="match-start adjusted: "+str(start)+"\n"
                
                compreturn = self.getCompletionTime(mach,start,processtime,curr_shift)

                if compreturn == None:
                    continue
                else: 
                    compshift,completion = compreturn

                    Progress.value+="match-completion "+str(completion)+"\n"
                    Progress.value+=compshift.String("compshift sh")+"\n" 
                    
                    matchvar =  solver.IntVar(0.0,1,'x_'+str(mach.getID())+'_'+str(job.getJob().getName()))  # x_{m,j}
                    matchvars[(mach,job)] = matchvar
                    jobs_cons[job].SetCoefficient(matchvar,1)
                    startcomps[(mach,job)] = (start,completion)
                    objective.SetCoefficient(matchvar,1)

                    if mach.getProcessType() == "Metal forming":
                        currshift = ScheduleMgr.getShiftofTime(start)
                        compshift = ScheduleMgr.getShiftofTime(completion)
    
                        Progress.value+="match shift fte calculation starts... "+"\n" 
                        Progress.value+=currshift.String("start sh")+"\n" 
                        while currshift!= None: 
                            if currshift in shift_fte_cons:
                                Progress.value+="current shift has fte cons... "+"\n" 
                                # find start and end in this shift 
                                shstarttime = max(currshift.getStartTime(),start)
                                shendtime = min(currshift.getEndTime(),completion)
                                Progress.value+=currshift.String("curr sh")+"\n" 
                                Progress.value+="match st/cp: "+str(shstarttime)+"-"+str(shendtime)+"\n" 
                                Progress.value+="fte requirement: "+str(mach.getOperatingEffort()*(shendtime-shstarttime))+"\n" 
                                shift_fte_cons[currshift].SetCoefficient(matchvar,mach.getOperatingEffort()*(shendtime-shstarttime))
                                Progress.value+=" var inserted into constraint"+"\n" 
                            
                            if currshift == compshift:
                                break
                            currshift = currshift.getNext()
                                
                            
                        Progress.value+="match shift fte calculation done... "+"\n" 
                    

        # check for conflicting matches: 

        mach_no = 1
        for mach in machines:
            #Progress.value+="mach "+str(mach.getName())+" checking matches.."+"\n"
            machmatches = [((matchtuple,times),matchvars[matchtuple]) for matchtuple,times in startcomps.items() if matchtuple[0] == mach]
             
            #Progress.value+="mach "+str(mach.getName())+" has "+str(len(machmatches))+" matches"+"\n"

            for mytuple in machmatches:
                matchinfo,matchvar = mytuple

               
                for mytuple2 in machmatches:
                    if mytuple == mytuple2:
                        continue
                    matchinfo2,matchvar2 = mytuple2 
                    
                    # st2 >= cp1 
                    if (matchinfo[1][1] <= matchinfo2[1][0]):
                        continue
                    # cp2 <= st1 
                    if ( matchinfo2[1][1] <= matchinfo[1][0]):
                        continue
            
                    Progress.value+="matchinfo: job "+str(matchinfo[0][1].getJob().getName())+", times "+str(matchinfo[1])+"\n"
                    Progress.value+="check matchinfo: job "+str(matchinfo2[0][1].getJob().getName())+", times "+str(matchinfo2[1])+"\n"
                    Progress.value+=" Conflict!!!"+"\n"

                    confcons = solver.Constraint(0,1,mach.getName()+'_'+matchinfo[0][1].getJob().getName()+'_'+matchinfo2[0][1].getJob().getName()+'_conf')
                    machines_conflict_cons[mach].append(confcons)
                    confcons.SetCoefficient(matchvar,1)
                    confcons.SetCoefficient(matchvar2,1)
        
        Progress.value+='MILP done.. '+"\n"             
        
        Progress.value+='MILP: Number of variables ='+str(solver.NumVariables())+', constraints ='+str(solver.NumConstraints())+"\n"

        
    
        if writeMILP: 
            mystring = solver.ExportModelAsLpFormat(False)
            filename = 'MILP-model_'+str(modelno)+'.txt'
            textfile = open(filename, 'w')
            textfile.write(mystring)
            textfile.close()

        Progress.value+='MILP file writing done.. '+"\n"          
        #print(solver.ExportModelAsLpFormat(False).replace('\\', '').replace(',_', ','), sep='\n')
    
        #print(f'Solving with {solver.SolverVersion()}')
       
        solver.set_time_limit(timelimitsecs*1000) 
        solverParams = pywraplp.MPSolverParameters()  
        solverParams.SetDoubleParam(solverParams.RELATIVE_MIP_GAP,optimalitygap)
        status = solver.Solve(solverParams)

       
        StatusText = ''
        nrsolutions = 0

      
        if status == pywraplp.Solver.OPTIMAL:
            nrsolutions+=1
            #print('Optimal Objective value =', solver.Objective().Value())
            StatusText = 'Optimal'
            #AssignSolution(myinstance,solver,StatusText,solver.wall_time())
        if status == pywraplp.Solver.INFEASIBLE:
            StatusText = 'Infeasible'
        if status == pywraplp.Solver.FEASIBLE:
            StatusText = 'Feasible'
            count = 1
            while solver.NextSolution():     
                #if count == 1: best
                count+= 1  
                nrsolutions+=1
            
        if (status == pywraplp.Solver.UNBOUNDED):
            StatusText = 'Unbounded'
        if (status == pywraplp.Solver.ABNORMAL): 
            StatusText = 'Abnormal'
        if (status == pywraplp.Solver.NOT_SOLVED): 
            StatusText = 'Not solved'
            
        Progress.value+= "Status: "+StatusText+", no solutions: "+str(nrsolutions)+"\n"

        scheduledjobs = []

        for matchtuple,var in matchvars.items():
            if var.solution_value() > 0:
                job = matchtuple[1]
                machine = matchtuple[0]
                scheduledjobs.append(job)
                starttime,completiontime = startcomps[matchtuple]

                ScheduleMgr.ScheduleJob(job,machine,starttime,completiontime,schedulesol,Progress)

                matchtuple[0].UpdateLatestJobCompletion(job,completiontime)
                matchtuple[0].UpdateTotalJobProcessing(job.getJob().getQuantity()*job.getJob().getOperation().getProcessTime('hour'))
       
        return scheduledjobs

#######################################################################################################################################################

#######################################################################################################################################################

    def SolveScheduling(self,AllJobs,ScheduleMgr,Progress,psstart,pssend):

        #initialize schedule solution object
        sch_sol = ScheduleSolution(self.name)
        for resname,res in ScheduleMgr.getDataManager().getResources().items():
            sch_sol.getResourceSchedules()[resname] = dict() # key: shift, value: dict following,
            for day,dayshifts in ScheduleMgr.getMyShifts().items():
                for shift in dayshifts:
                    sch_sol.getResourceSchedules()[resname][shift] = dict() # key: job, vaL: (st,cp)

        sch_sol.setStartWeek(psstart.isocalendar()[1])
        sch_sol.setEndWeek(pssend.isocalendar()[1])

        Progress.value+=" schedule weeks: start "+str(sch_sol.getStartWeek())+"-"+str(sch_sol.getEndWeek())+"\n"

        SchedulableJobs= [] 

        Progress.value+=" Simple greedy insertion starts.., all jobs "+str(len(AllJobs))+"\n"

        PreviouslyScheduled = []

      
        for job in AllJobs: 
            if job.getScheduledResource() != None:
                PreviouslyScheduled.append(job)
     
            
        Progress.value+="Simple greedy previously scheduled jobs "+str(len(PreviouslyScheduled))+"\n" 
        prev_size = len(PreviouslyScheduled)

       
        for job in AllJobs: 
            if job.IsSchedulable():
                SchedulableJobs.append(job)

        modelno = 1

        Progress.value+=" Schedulable jobs "+str(len(SchedulableJobs))+"\n"

        while len(SchedulableJobs) >0:

            scheduledjobs = self.SolveMILP(SchedulableJobs,ScheduleMgr,modelno,Progress,sch_sol)

            if len(scheduledjobs) == 0:
                break

            for j in scheduledjobs:
                SchedulableJobs.remove(j)
                for successor in j.getJob().getSuccessors():
                    if successor.getMySch().IsSchedulable():
                        SchedulableJobs.append(successor.getMySch())
            modelno+=1

        
        Progress.value+="Scheduling completed.. "+"\n"   
        return sch_sol
        
        