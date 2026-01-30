from PlanningObjects import *
import time
from ortools.linear_solver import pywraplp
import os
import math


class MILPGreedyInsertionAlg:
    def __init__(self):
        self.timelimit = 60
        self.jobmachmatches = 1
        self.name = "MILPGreedy"
        self.EST = None
        self.LST = None
        self.solutiontime = 0

    
    def setEST(self,est):
        self.EST = est
        return

    def getSolutionTime(self):
        return self.solutiontime

    def setSolutionTime(self,mytime):
        self.solutiontime+=mytime
        return 

    def setNoMatches(self,nomtch):
        self.jobmachmatches = nomtch
        return

    def getJobMachineMatches(self):
        return self.jobmachmatches
           
    def setLST(self,lst):
        self.LST = lst
        return

    def getEST(self):
        return self.EST
     
    def getLST(self):
        return self.LST
        
    

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
########################################################################################################################
    def checkMatch(self,ScheduleMgr,Progress,job,job_lpc,mach,sch_sol):
        """
        job_lpc: time in half hours from the start of scheduling horizon. 
        
        """

        #Progress.value+=" check match starts...for "+str(job.getJob().getName())+" with "+str(mach.getName())+"\n"
    
        processtime = math.ceil(2*(job.getJob().getQuantity()*job.getJob().getOperation().getProcessTime('hour')))
    
        matches = []
        sttime = 0
           
        for slot in sch_sol.getResourceSlots()[mach]:   
            sttime = max(slot[0],job_lpc)

            while len(matches) < self.getJobMachineMatches():
                curr_strt = sttime
                curr_shift = ScheduleMgr.getShiftofTime(curr_strt)
                        
                if mach.getShiftOperatingModes()[curr_shift]== "Self-Running":
                    curr_shift = curr_shift.getNext()
                    curr_strt = curr_shift.getStartTime()

                if slot[1] - curr_strt >= processtime:
                    compreturn = self.getCompletionTime(mach,curr_strt,processtime,curr_shift)
                            
                    if compreturn != None:
                        start = curr_strt
                        compshift,completion = compreturn
                        matches.append((start,completion)) 
                    else:
                        break
                else:
                    break

                sttime+=1
                
            if len(matches) >= self.getJobMachineMatches():
                break

       
            
        #rogress.value+=" found matches: "+str(matches)+"\n" 
        return matches

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

        selectedtype = processtypes[0]

        machines_conflict_cons = dict() # key: machine, val: [constraints]
        jobs_cons = dict() # key: job, val: constraints
        job_vars = dict() # key: job, val: [matchvar]
        shift_fte_cons = dict()  #key: shift, val: ftecons
        precedence_cons = dict() # key: ((pred,var),succ), val: (cons1,cons2)


        
        matchvars = dict() #key: (mach,job), val: [x_mj]
        startcomps = dict() #key: ((mach,job),var), val: (st_mj,cp_mj)
       
        machines = [res for resname,res in ScheduleMgr.getDataManager().getResources().items() if res.getType() in ["Machine","Outsourced"] ]


        solverType = "SCIP";
        solver = pywraplp.Solver.CreateSolver(solverType)
        Progress.value+="Solver "+str(solver)+"\n"
        
        if not solver:
            return

        epsilon = 0.001

        
        infinity = solver.infinity(); objective = solver.Objective(); objective.SetMaximization()

        for date,shifts in ScheduleMgr.getMyShifts().items():
            for shift in shifts:
                if not shift.inScheduling():
                    continue
                if shift.getNumber() == 3: 
                    continue
                
                ftecapacity = ScheduleMgr.getDataManager().getFTECapacity(selectedtype,shift) # no.man
                ftecapacity*=(shift.getEndTime()-shift.getStartTime()+1) # no. man-halfhour
                shift_fte_cons[shift] = solver.Constraint(0,ftecapacity,str(shift.getDay())+'_'+str(shift.getNumber())+'_cons')

        for mach in machines:
            machines_conflict_cons[mach] = []

        bigM = max([y.getEndTime() for x in ScheduleMgr.getMyShifts().values() for y in x if y.inScheduling()])+8

        Progress.value+="Preparations done.. "+"\n"
    #**********************************************************************************   
        for job in JobsinModel: 
            jobs_cons[job]  = solver.Constraint(0,1,job.getJob().getName()+'_cons')

            alternatives = ScheduleMgr.getAlternativeResources(job.getJob())
            alternatives = [res for res in alternatives if res in machines]

            job_lpc=  0
            if len(job.getJob().getPredecessors()) > 0:
                job_lpc = 0
                for x in job.getJob().getPredecessors():

                    if x.getMySch().getActualStart() != None:
                        #Progress.value+="predecessor actually started:  "+x.getName()+"\n"
                        if x.getMySch().getActualCompletion() != None:
                            #Progress.value+="predecessor actually completed:  "+x.getName()+"\n"
                            continue
                            
                        if not x.getMySch().getScheduledCompShift().inScheduling():
                            continue
                        predcomp = x.getMySch().getScheduledCompletion()
                        cpshift = x.getMySch().getScheduledCompShift()
                        Progress.value+=cpshift.String("compshift:  ")+"\n"
                        if cpshift.inScheduling():
                            Progress.value+="completion:  "+str(predcomp)+"\n"
                            comptime = cpshift.getStartTime()+math.ceil((predcomp-cpshift.getStartHour()).total_seconds()/1800)
                            Progress.value+="comptime:  "+str(comptime)+"\n"
                            job_lpc = max(job_lpc,comptime)

                    else: 
                        if x.getMySch().getCompletionTime() != None:
                            job_lpc = max(job_lpc,x.getMySch().getCompletionTime())
                        
                   
                        
                        
                
               


            for mach in alternatives:

                matchreturn = self.checkMatch(ScheduleMgr,Progress,job,job_lpc,mach,schedulesol)

                for matchtuple in matchreturn:
                    start,completion = matchtuple
                    matchvar =  solver.IntVar(0.0,1,'x_'+str(mach.getID())+'_'+str(job.getJob().getName()))  # x_{m,j}
       
                    if not job in job_vars:
                        job_vars[job] = []
                    job_vars[job].append(matchvar)
    
                    if not (mach,job) in matchvars:
                        matchvars[(mach,job)]=[]
                    matchvars[(mach,job)].append(matchvar)
                    jobs_cons[job].SetCoefficient(matchvar,1)
                    startcomps[((mach,job),matchvar)] = (start,completion)
                    objective.SetCoefficient(matchvar,1)
    
                    if mach.getProcessType() == "Metal forming":
                        currshift = ScheduleMgr.getShiftofTime(start)
                        compshift = ScheduleMgr.getShiftofTime(completion)

                        while currshift!= None:  
                            if currshift in shift_fte_cons:
                                shstarttime = max(currshift.getStartTime(),start)
                                shendtime = min(currshift.getEndTime(),completion)
                                shift_fte_cons[currshift].SetCoefficient(matchvar,mach.getOperatingEffort()*(shendtime-shstarttime))
    
                            if currshift == compshift:
                                break
                            currshift = currshift.getNext()

        curr_jobs = [x for x in job_vars.keys()]
        for myjob in curr_jobs:
            mvars = job_vars[myjob]
            for successor in myjob.getJob().getSuccessors():
                if len([x for x in successor.getPredecessors() if x.getMySch() == None]) > 0:
                    continue
                if len([x for x in successor.getPredecessors() if (x != myjob.getJob()) and (x.getMySch().getCompletionTime()== None) ]) > 0:
                    continue
                if len([x for x in successor.getPredecessors() if x.getMySch() in job_vars ]) != 1:
                    continue
                for myvar in mvars:
                    succ_lpc = max([x.getMySch().getCompletionTime() if x.getMySch().getCompletionTime()!= None else 0 for x in successor.getPredecessors()])
                    tuples = [] 
                    for machjob,mjvars in matchvars.items():
                        for x in mjvars:  
                            if x.name() == myvar.name():
                                tuples.append(machjob)
                                break
                    mytuple = tuples[0]
                    succ_lpc = max(startcomps[(mytuple,myvar)][1],succ_lpc)
            
                    alternatives = ScheduleMgr.getAlternativeResources(successor)

                    for mach in alternatives:
                        
                        condmatchreturn = self.checkMatch(ScheduleMgr,Progress,successor.getMySch(),succ_lpc,mach,schedulesol)

                        for matchtuple in condmatchreturn:
     
                            start,completion = matchtuple
                            
                            condmatch =  solver.IntVar(0.0,1,'x_'+myjob.getJob().getName()+"_"+successor.getName()+"_"+myvar.name()+"_"+str(mach.getID())) 
                            condtuple = ((myjob,myvar),successor.getMySch())
                                
                            if not condtuple in precedence_cons:
                                cons1  = solver.Constraint(0,epsilon,myjob.getJob().getName()+"_"+successor.getName()+"_"+myvar.name()+'_prec_cons1')
                                cons2  = solver.Constraint(0,bigM,myjob.getJob().getName()+"_"+successor.getName()+"_"+myvar.name()+'_prec_cons2')
                                precedence_cons[condtuple] = (cons1,cons2)
                                precedence_cons[condtuple][0].SetCoefficient(myvar,-1)
                                precedence_cons[condtuple][1].SetCoefficient(myvar,startcomps[(mytuple,myvar)][1])

                            precedence_cons[condtuple][0].SetCoefficient(condmatch,1)
                            precedence_cons[condtuple][1].SetCoefficient(condmatch,(1-start))
    
                                
                            if not successor.getMySch() in job_vars:
                                job_vars[successor.getMySch()] = []
                            job_vars[successor.getMySch()].append(condmatch)
    
                            if not (mach,successor.getMySch()) in matchvars:
                                matchvars[(mach,successor.getMySch())]=[]
                            matchvars[(mach,successor.getMySch())].append(condmatch)
    
                            if not successor.getMySch() in jobs_cons:
                                jobs_cons[successor.getMySch()]  = solver.Constraint(0,1,successor.getName()+'_cons')
                            jobs_cons[successor.getMySch()].SetCoefficient(condmatch,1)
                                
                 
                            startcomps[((mach,successor.getMySch()),condmatch)] = (start,completion)
                            objective.SetCoefficient(condmatch,1)
    
                            if mach.getProcessType() == "Metal forming":
                                currshift = ScheduleMgr.getShiftofTime(start)
                                compshift = ScheduleMgr.getShiftofTime(completion)
                                    
                                while currshift!= None:
                                    if currshift in shift_fte_cons:
                                        shstarttime = max(currshift.getStartTime(),start)
                                        shendtime = min(currshift.getEndTime(),completion)
                                        shift_fte_cons[currshift].SetCoefficient(condmatch,mach.getOperatingEffort()*(shendtime-shstarttime))
    
                                    if currshift == compshift:
                                        break
                                    currshift = currshift.getNext()
   
        # startcomps #key: ((mach,job),var), val: (st_mj,cp_mj)
        # check for conflicting matches: 

        mach_no = 1
        for mach in machines:
            machmatches = [(matchtuple[0],(matchtuple[1],times)) for matchtuple,times in startcomps.items() if matchtuple[0][0] == mach]
        
            for mytuple in machmatches:
                ((machne,mjob),(mvar,(start,comp))) = mytuple   # ((mach,job), (x_mj,(st_mj,cp_mj)))

                for mytuple2 in machmatches:
                    if mytuple == mytuple2:
                        continue
                    ((machne2,mjob2),(mvar2,(start2,comp2))) = mytuple2
                        
                    # st2 >= cp1 or cp2 <= st1 
                    if (comp <= start2) or (comp2 <= start) :
                        continue
 
                    confcons = solver.Constraint(0,1,mach.getName()+'_'+mjob.getJob().getName()+'_'+mjob2.getJob().getName()+'_conf')
                    machines_conflict_cons[mach].append(confcons)
                    confcons.SetCoefficient(mvar,1)
                    confcons.SetCoefficient(mvar2,1)
   
    
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
          
            Progress.value+='Optimal Objective value = '+str(solver.Objective().Value())+"\n"
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

        Progress.value+="Model run "+str(modelno)+", #variables ="+str(solver.NumVariables())+', constraints ='+str(solver.NumConstraints())+"\n"

        Progress.value+= "Status: "+StatusText+", no solutions: "+str(nrsolutions)+"\n"

        scheduledjobs = []

        # matchvars,  #key: (mach,job), val: [x_mj]
        # startcomps #key: ((mach,job),var), val: (st_mj,cp_mj)

        scheduled_resources = [] 

        for matchtuple,myvars in matchvars.items():
            for var in myvars:
                if var.solution_value() > 0:
                    job = matchtuple[1]
                    machine = matchtuple[0]
                    
                    if not machine in scheduled_resources:
                        scheduled_resources.append(machine)
                    
                    if job in JobsinModel:
                        scheduledjobs.append(job)
                        
                    starttime,completiontime = startcomps[((machine,job),var)]
    
                    ScheduleMgr.ScheduleJob(job,machine,starttime,completiontime,schedulesol,Progress)

    
                    matchtuple[0].UpdateLatestJobCompletion(job,completiontime)
                    matchtuple[0].UpdateTotalJobProcessing(2*job.getJob().getQuantity()*job.getJob().getOperation().getProcessTime('hour'))

        # updating resource slots..
        for resource in scheduled_resources:
            schedulesol.getResourceJobs()[resource].sort(key=lambda x: x.getStartTime())
            schedulesol.getResourceSlots()[resource].clear()

            curr_st =  self.getEST()
            
            for job in schedulesol.getResourceJobs()[resource]:
                if curr_st < job.getStartTime():
                    curr_slot = (curr_st,job.getStartTime())
                    schedulesol.getResourceSlots()[resource].append(curr_slot)
                    
                curr_st = job.getCompletionTime()
                res_shift = ScheduleMgr.getShiftofTime(curr_st)
                if resource.getShiftOperatingModes()[res_shift]== "Self-Running":
                    res_shift = res_shift.getNext()
                    if res_shift != None:
                        curr_st = res_shift.getStartTime()
                    else:
                        curr_st = self.getLST()
                        break
                
            if curr_st < self.getLST():
                res_shift = ScheduleMgr.getShiftofTime(curr_st)
                if resource.getShiftOperatingModes()[res_shift]== "Self-Running":
                    res_shift = res_shift.getNext()
                    if res_shift != None:
                        curr_st = res_shift.getStartTime()
                        curr_slot = (curr_st,self.getLST())
                        schedulesol.getResourceSlots()[resource].append(curr_slot)
                else:
                    curr_slot = (curr_st,self.getLST())
                    schedulesol.getResourceSlots()[resource].append(curr_slot)
       
        return scheduledjobs

#######################################################################################################################################################

#######################################################################################################################################################

    def SolveScheduling(self,AllJobs,FixJobs,ScheduleMgr,Progress,psstart,pssend):

        #initialize schedule solution object

        start_time = time.time()

        Progress.value+="> MILP-based greedy alg: starts... "+"\n"
        sch_sol = ScheduleSolution(self.name)
        earliesttime = 10000000
        latesttime = 0
        notinscheduleshifts = dict()  # key: resname, val: dict (key: shift, val: dict( key: job, val: (st,cp) ))
        for resname,res in ScheduleMgr.getDataManager().getResources().items():
            sch_sol.getResourceSchedules()[resname] = dict() # key: shift, value: dict following,
            for day,dayshifts in ScheduleMgr.getMyShifts().items():
                for shift in dayshifts:
                    if not shift.inScheduling():
                        continue
                    sch_sol.getResourceSchedules()[resname][shift] = dict() # key: job, vaL: (st,cp)
                    #if shift in ScheduleMgr.getMyCurrentSchedule().getResourceSchedules()[resname]:
                    #    for job,jobtimes in ScheduleMgr.getMyCurrentSchedule().getResourceSchedules()[resname][shift]:
                    #        if job.getActualStart()!= None:
                    #            sch_sol.getResourceSchedules()[resname][shift][job] = jobtimes
                    
                    earliesttime = min(shift.getStartTime(),earliesttime)
                    latesttime = max(shift.getEndTime(),latesttime)

        
            #Progress.value+=" res slots "+str(res.getName())+"-"+str((earliesttime,latesttime))+"\n"

            # initializing scheduling slots for checking feasiblity in MILP matches.
            sch_sol.getResourceSlots()[res] = [(earliesttime,latesttime)]
        Progress.value+="> MILP-based greedy alg: New schedule created... "+"\n"
     
        self.setEST(earliesttime)
        self.setLST(latesttime)

        sch_sol.setStartWeek(psstart.isocalendar()[1])
        sch_sol.setEndWeek(pssend.isocalendar()[1])

        
        for job in FixJobs:
            Progress.value+="> MILP-based greedy alg: "+", fix job: "+job.getJob().getName()+"\n"
            for shift,jobtimes in ScheduleMgr.getMyCurrentSchedule().getResourceSchedules()[job.getScheduledResource().getName()].items():
                if shift.inScheduling():
                    #Progress.value+="> MILP-based greedy alg: "+shift.String("shft in sch: ")+"\n"
                    for mmjob,mmjobtimes in jobtimes.items():
                        Progress.value+="> MILP-based greedy alg: "+", job: "+mmjob.getJob().getName()+"\n"
                        if mmjob == job:
                            Progress.value+="> MILP-based greedy alg: "+", inserted times: "+str(mmjobtimes)+"\n"
                            sch_sol.getResourceSchedules()[job.getScheduledResource().getName()][shift][job] = mmjobtimes
                            
                            if job.getStartTime() == None:
                                job.setStartTime(shift.getStartTime()+mmjobtimes[0]) 
                                Progress.value+="> MILP-based greedy alg: "+", strt time: "+str(shift.getStartTime()+mmjobtimes[0])+"\n"
                            else:
                                if job.getStartTime() > shift.getStartTime()+mmjobtimes[0]:
                                    job.setStartTime(shift.getStartTime()+mmjobtimes[0]) 
                                    Progress.value+="> MILP-based greedy alg: "+", strt time: "+str(shift.getStartTime()+mmjobtimes[0])+"\n"
                            
                            if job.getCompletionTime() == None:
                                job.setCompletionTime(shift.getStartTime()+mmjobtimes[1]) 
                                Progress.value+="> MILP-based greedy alg: "+", comp time: "+str(shift.getStartTime()+mmjobtimes[1])+"\n"
                            else:
                                if job.getCompletionTime() < shift.getStartTime()+mmjobtimes[1]:
                                    job.setCompletionTime(shift.getStartTime()+mmjobtimes[1]) 
                                    Progress.value+="> MILP-based greedy alg: "+", comp time: "+str(shift.getStartTime()+mmjobtimes[1])+"\n"
                                

        Progress.value+="> MILP-based greedy alg: Fixed jobs handled... "+"\n"
        
        Progress.value+=" schedule weeks: start "+str(sch_sol.getStartWeek())+"-"+str(sch_sol.getEndWeek())+"\n"

        SchedulableJobs= [] 

        Progress.value+=" MILP-based greedy insertion starts.., no. jobs "+str(len(AllJobs))+"\n"

         

       
        for job in AllJobs: 
            if job.IsSchedulable():
                SchedulableJobs.append(job)

        modelno = 1

        Progress.value+=" Schedulable jobs "+str(len(SchedulableJobs))+"\n"

        while len(SchedulableJobs) >0:

            scheduledjobs = self.SolveMILP(SchedulableJobs,ScheduleMgr,modelno,Progress,sch_sol)

            #Progress.value+=" Scheduled jobs "+str(len(scheduledjobs))+"\n"

            if len(scheduledjobs) == 0:
                break

            for j in scheduledjobs:
                if j in SchedulableJobs:
                    SchedulableJobs.remove(j)
                #Progress.value+=" checking successors of  "+str(j.getJob().getName())+" > "+str(len(j.getJob().getSuccessors()))+"\n"
                for successor in j.getJob().getSuccessors():
                    #Progress.value+="  successor  "+str(successor.getName())+" schedulable "+str(successor.getMySch().IsSchedulable()) +"\n"
                    if successor.getMySch().IsSchedulable():
                        SchedulableJobs.append(successor.getMySch())
                    else:
                        if successor.getMySch().IsScheduled():
                            for successor2 in successor.getSuccessors():
                                if successor2.getMySch().IsSchedulable():
                                    SchedulableJobs.append(successor2.getMySch())
         
            modelno+=1


        
        Progress.value+="Schedule summary.. "+"\n"   
        Progress.value+="____________________________________________"+"\n"   
        for res,jobs in sch_sol.getResourceJobs().items():
            Progress.value+="Schedule of "+res.getName()+"\n"   
            for job in jobs:
                Progress.value+=job.getJob().getName()+"("+str(job.getStartTime())+"-"+str(job.getCompletionTime())+")"+"\n"   
        Progress.value+="____________________________________________"+"\n" 

        self.setSolutionTime(time.time()-start_time)
        Progress.value+="Solution time: "+str(round(self.getSolutionTime(),2))+" secs. \n"  


        for resname,res in ScheduleMgr.getDataManager().getResources().items():
            Progress.value+="res: "+resname+"\n" 
            for shift,jobtimes in ScheduleMgr.getMyCurrentSchedule().getResourceSchedules()[resname].items():
                if not shift.inScheduling():
                    Progress.value+=shift.String(" added shft: ")+", jobs: "+str(len(jobtimes))+"\n" 
                    sch_sol.getResourceSchedules()[resname][shift] = jobtimes
        Progress.value+="> MILP-based greedy alg: done... "+"\n"
        
        return sch_sol
        
        