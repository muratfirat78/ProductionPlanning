from PlanningObjects import *
import time
from ortools.linear_solver import pywraplp
import os
import math


class MILPGreedyInsertionAlg:
    def __init__(self):
        self.timelimit = 60
        self.name = "MILPGreedy"
        self.EST = None
        self.LST = None

    
    def setEST(self,est):
        self.EST = est
        return
           
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

        Progress.value+=" check match starts...for "+str(job.getJob().getName())+" with "+str(mach.getName())+"\n"
        start = None
      
        if mach in sch_sol.getResourceJobs():
            Progress.value+=" -->>>> jobs of "+mach.getName()+": "+str(["("+str(x.getStartTime())+"-"+str(x.getCompletionTime())+")" for x in sch_sol.getResourceJobs()[mach]])+"\n"
        else:
            Progress.value+=" -->>>> there is no job in resource schedule "+"\n" 

        Progress.value+=" -->>>> available slots: "+str(sch_sol.getResourceSlots()[mach])+"\n" 

        Progress.value+="  processtime......"+str(job.getJob().getQuantity())+"\n"
        processtime = math.ceil(2*(job.getJob().getQuantity()*job.getJob().getOperation().getProcessTime('hour')))
        Progress.value+="  processtime."+str(processtime)+"\n"

        for slot in sch_sol.getResourceSlots()[mach]:   
            if slot[1]-slot[0] >= processtime:
                start = slot[0]
                break
                
        if start == None:
            Progress.value+=" return no feasible start"+"\n"
            return None
        
        curr_shift = ScheduleMgr.getShiftofTime(start)
       
        compreturn = self.getCompletionTime(mach,start,processtime,curr_shift)

        if compreturn == None:
            Progress.value+=" return no feasible completion"+"\n"
            return None
         
        compshift,completion = compreturn   
        
        return start,completion

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
        job_vars = dict() # key: job, val: [matchvar]
        shift_fte_cons = dict()  #key: shift, val: ftecons
        precedence_cons = dict() # key: ((pred,var),succ), val: (cons1,cons2)


        
        matchvars = dict() #key: (mach,job), val: [x_mj]
        startcomps = dict() #key: ((mach,job),var), val: (st_mj,cp_mj)
       
        machines = [res for resname,res in ScheduleMgr.getDataManager().getResources().items() if res.getType() in ["Machine","Outsourced"] ]

        Progress.value+="Model run "+str(modelno)+", machines "+str(len(machines))+"\n"

        solverType = "SCIP";
        solver = pywraplp.Solver.CreateSolver(solverType)
        Progress.value+="Solver "+str(solver)+"\n"
        
        if not solver:
            return

        epsilon = 0.001
        Progress.value+="Solver created.. "+"\n"
        
        infinity = solver.infinity(); objective = solver.Objective(); objective.SetMaximization()

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

        bigM = max([y.getEndTime() for x in ScheduleMgr.getMyShifts().values() for y in x])+8
        
        Progress.value+=">> bigM value: "+str(bigM)+"\n"
             
    #**********************************************************************************   
        for job in JobsinModel: 
            jobs_cons[job]  = solver.Constraint(0,1,job.getJob().getName()+'_cons')


            alternatives = ScheduleMgr.getAlternativeResources(job)
            alternatives = [res for res in alternatives if res in machines]

            Progress.value+="job "+str(job.getJob().getName())+" has "+str(len(alternatives))+" alternatives ("+str(len(job.getJob().getOperation().getRequiredResources()))+")"+"\n"

            job_lpc=  0
            if len(job.getJob().getPredecessors()) > 0:
                job_lpc = max([x.getMySch().getCompletionTime() for x in job.getJob().getPredecessors()])
            
            Progress.value+="job "+str(job.getJob().getName())+" has  job_lpc "+str(job_lpc)+"\n"
            
            for mach in alternatives:

                Progress.value+="   >> "+" check  for alt.. "+str(mach.getID())+"\n" 
                matchreturn = self.checkMatch(ScheduleMgr,Progress,job,job_lpc,mach,schedulesol)

                Progress.value+="   >> "+" return.. "+str(matchreturn)+"\n" 

                if matchreturn == None:
                    continue

                matchvar =  solver.IntVar(0.0,1,'x_'+str(mach.getID())+'_'+str(job.getJob().getName()))  # x_{m,j}
                start,completion = matchreturn
   
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

        
        Progress.value+=" conditional checking starts..  jobs "+str(len(job_vars))+"\n" 
        curr_jobs = [x for x in job_vars.keys()]
        for myjob in curr_jobs:
            mvars = job_vars[myjob]
            Progress.value+="   >> "+myjob.getJob().getName()+"... successors  "+str(len(myjob.getJob().getSuccessors()))+"\n" 
            for successor in myjob.getJob().getSuccessors():
                Progress.value+="   >> "+" checking successor.. "+successor.getName()+"\n" 
                if len([x for x in successor.getPredecessors() if x.getMySch() == None]) > 0:
                    Progress.value+="   >> "+"  at least one pred has no mysch "+"\n" 
                    continue
                if len([x for x in successor.getPredecessors() if (x != myjob.getJob()) and (x.getMySch().getCompletionTime()== None) ]) > 0:
                    Progress.value+="   >> "+"  at least one pred, not this job, has no completion time "+"\n" 
                    continue
                if len([x for x in successor.getPredecessors() if x.getMySch() in job_vars ]) != 1:
                    continue
                # now condtional match will be checked
                Progress.value+="   >> "+" vars.. "+str([x.name() for x in mvars])+"\n" 
                for myvar in mvars:
                    Progress.value+="   >> "+" base match.. "+myvar.name()+"\n" 
                    Progress.value+="   >> "+str([x.getMySch().getCompletionTime() if x.getMySch().getCompletionTime()!= None else 0 for x in successor.getPredecessors()])+"\n"  
                    succ_lpc = max([x.getMySch().getCompletionTime() if x.getMySch().getCompletionTime()!= None else 0 for x in successor.getPredecessors()])

                    tuples = [] 
                    for machjob,mjvars in matchvars.items():
                        Progress.value+="   >> "+" tuple.. "+str(machjob[0].getName())+"--"+str(machjob[1].getJob().getName())+"\n" 
                        Progress.value+="   >> "+" vars.. "+str([x.name() for x in mjvars])+"\n" 
                        Progress.value+="   >> "+" check var.. "+myvar.name()+"\n" 
                        for x in mjvars:  
                            if x.name() == myvar.name():
                                tuples.append(machjob)
                                break
                                
                        Progress.value+="   >> "+" var in?.. "+str(myvar in mjvars)+"\n" 
                    
                    #tuples = [machjob for machjob,mjvars in matchvars.items() if myvar in mjvars]
                    Progress.value+="   >> "+" tuples.. "+str(len(tuples))+"\n" 

                    for machjob in tuples:
                        Progress.value+="   >> "+" mach.. "+str(machjob[0].getName())+"-->"+str(machjob[1].getJob().getName())+"\n" 
                    
                    mytuple = tuples[0]
                    succ_lpc = max(startcomps[(mytuple,myvar)][1],succ_lpc)
                    Progress.value+=" succ_lpc..."+str(succ_lpc)+"\n" 
                    alternatives = ScheduleMgr.getAlternativeResources(successor.getMySch())
                    Progress.value+="   >> "+" alternatives.. "+str(len(alternatives))+"\n" 
                    
                    for mach in alternatives:
                        
                        condmatchreturn = self.checkMatch(ScheduleMgr,Progress,successor.getMySch(),succ_lpc,mach,schedulesol)
                            
                        if condmatchreturn == None:
                            continue

                        start,completion = condmatchreturn
                        Progress.value+="   >> "+" return.. "+str(condmatchreturn)+"\n"
                        condmatch =  solver.IntVar(0.0,1,'x_'+myjob.getJob().getName()+"_"+successor.getName()+"_"+myvar.name()+"_"+str(mach.getID())) 

                        Progress.value+="   >> "+" var created.. "+str(condmatch.name())+"\n"
                        condtuple = ((myjob,myvar),successor.getMySch())
                            
                        if not condtuple in precedence_cons:
                            cons1  = solver.Constraint(0,epsilon,myjob.getJob().getName()+"_"+successor.getName()+"_"+myvar.name()+'_prec_cons1')
                            cons2  = solver.Constraint(0,bigM,myjob.getJob().getName()+"_"+successor.getName()+"_"+myvar.name()+'_prec_cons2')
                            precedence_cons[condtuple] = (cons1,cons2)
                            precedence_cons[condtuple][0].SetCoefficient(myvar,-1)
                            precedence_cons[condtuple][1].SetCoefficient(myvar,startcomps[(mytuple,myvar)][1])

                        Progress.value+="   >> "+" cons created.. "+"\n"

                        precedence_cons[condtuple][0].SetCoefficient(condmatch,1)
                        precedence_cons[condtuple][1].SetCoefficient(condmatch,(1-start))

                            
                        if not successor.getMySch() in job_vars:
                            job_vars[successor.getMySch()] = []
                        job_vars[successor.getMySch()].append(condmatch)

                        Progress.value+="   >> "+" vars of succssr "+str(len(job_vars[successor.getMySch()]))+"\n"

                        if not (mach,successor.getMySch()) in matchvars:
                            matchvars[(mach,successor.getMySch())]=[]
                        matchvars[(mach,successor.getMySch())].append(condmatch)

                        Progress.value+="   >> "+" matchvars updated.. "+"\n"
                            
                        if not successor.getMySch() in jobs_cons:
                            jobs_cons[successor.getMySch()]  = solver.Constraint(0,1,successor.getName()+'_cons')
                        jobs_cons[successor.getMySch()].SetCoefficient(condmatch,1)
                            
                        Progress.value+="   >> "+" jobcons added.. "+"\n"
                            
                        startcomps[((mach,successor.getMySch()),condmatch)] = (start,completion)
                        objective.SetCoefficient(condmatch,1)

                        Progress.value+="   >> "+" shift ftes.... "+"\n"
                          
                        if mach.getProcessType() == "Metal forming":
                            currshift = ScheduleMgr.getShiftofTime(start)
                            compshift = ScheduleMgr.getShiftofTime(completion)
                                
                            while currshift!= None:
                                Progress.value+=currshift.String("curr sh")+"\n"
                                Progress.value+=" >>> ? "+str(currshift in shift_fte_cons)+"\n"
                                if currshift in shift_fte_cons:
                                    shstarttime = max(currshift.getStartTime(),start)
                                    shendtime = min(currshift.getEndTime(),completion)
                                    Progress.value+=" >>> "+str(shstarttime)+"--"+str(shendtime)+"\n"
                                    shift_fte_cons[currshift].SetCoefficient(condmatch,mach.getOperatingEffort()*(shendtime-shstarttime))

                                if currshift == compshift:
                                    Progress.value+=" >>> breaking..."+"\n"
                                    break
                                currshift = currshift.getNext()
                        
                        Progress.value+=" >>> continuing..."+str(len(jobs_cons))+"<-->"+str(len(shift_fte_cons))+"\n"
            
                        
        Progress.value+=" conditional checking done.."+"\n"           

        # startcomps #key: ((mach,job),var), val: (st_mj,cp_mj)
        # check for conflicting matches: 

        mach_no = 1
        for mach in machines:
            Progress.value+="mach "+str(mach.getName())+" checking matches.."+"\n"
            machmatches = [(matchtuple[0],(matchtuple[1],times)) for matchtuple,times in startcomps.items() if matchtuple[0][0] == mach]
             
            #Progress.value+="mach "+str(mach.getName())+" has "+str(len(machmatches))+" matches"+"\n"

            for mytuple in machmatches:
                ((machne,mjob),(mvar,(start,comp))) = mytuple   # ((mach,job), (x_mj,(st_mj,cp_mj)))

                for mytuple2 in machmatches:
                    if mytuple == mytuple2:
                        continue
                    ((machne2,mjob2),(mvar2,(start2,comp2))) = mytuple2
                        
                    # st2 >= cp1 
                    if (comp <= start2):
                        continue
                    # cp2 <= st1 
                    if (comp2 <= start):
                        continue
                    
                    Progress.value+="matchinfo: job "+str(mjob.getJob().getName())+", times "+str((start,comp))+"\n"
                    Progress.value+="check matchinfo: job "+str(mjob2.getJob().getName())+", times "+str((start2,comp2))+"\n"
                    Progress.value+=" Conflict!!!"+"\n"
        
                    confcons = solver.Constraint(0,1,mach.getName()+'_'+mjob.getJob().getName()+'_'+mjob2.getJob().getName()+'_conf')
                    machines_conflict_cons[mach].append(confcons)
                    confcons.SetCoefficient(mvar,1)
                    confcons.SetCoefficient(mvar2,1)
        
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

    def SolveScheduling(self,AllJobs,ScheduleMgr,Progress,psstart,pssend):

        #initialize schedule solution object
        
        sch_sol = ScheduleSolution(self.name)
        earliesttime = 10000000
        latesttime = 0
        for resname,res in ScheduleMgr.getDataManager().getResources().items():
            sch_sol.getResourceSchedules()[resname] = dict() # key: shift, value: dict following,
            for day,dayshifts in ScheduleMgr.getMyShifts().items():
                for shift in dayshifts:
                    sch_sol.getResourceSchedules()[resname][shift] = dict() # key: job, vaL: (st,cp)
                    earliesttime = min(shift.getStartTime(),earliesttime)
                    latesttime = max(shift.getEndTime(),latesttime)
            
            sch_sol.getResourceSlots()[res] = [(earliesttime,latesttime)]
            
        self.setEST(earliesttime)
        self.setLST(latesttime)

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
                Progress.value+=" scheduled job  "+str(j.getJob().getName())+"\n"
                for successor in j.getJob().getSuccessors():
                    Progress.value+=" check successor "+str(successor.getName())+"\n"
                    Progress.value+=" check successor "+str(successor.getName())+", schedulable: "+str(successor.getMySch().IsSchedulable())+"\n"
                    if successor.getMySch().IsSchedulable():
                        SchedulableJobs.append(successor.getMySch())
                    else:
                        if successor.getMySch().IsScheduled():
                            for successor2 in successor.getSuccessors():
                                Progress.value+=" check successor "+str(successor2.getName())+"\n"
                                Progress.value+=" check successor "+str(successor2.getName())+", schedulable: "+str(successor2.getMySch().IsSchedulable())+"\n"
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
            
        return sch_sol
        
        