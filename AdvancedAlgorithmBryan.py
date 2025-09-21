import pulp

class AdvancedMILPAlg:
    def __init__(self):
        self.timelimit = 60
        self.name = 'MILPSchedule'

    def SolveScheduling(self,AllJobs,ScheduleMgr,Progress):
 
        Jobs = []
        ProcessList = {} #dict that shows jobs with the available machines
        Resources = []

        Progress.value+=" MILP schedule starts.."+"\n"  

        for job in AllJobs:  
            Jobs.append(job.getJob())

        for res,name in ScheduleMgr.getDataManager().getResources().items():
            Resources.append(res)

        for j in Jobs:            
            processtime = j.getOperation().getProcessTime()
            ResourcesPerJob = {} #Dictionary for alternative machines
            for res in j.getOperation().getRequiredResources():
                ResourcesPerJob[res]= processtime
            ProcessList[j]=ResourcesPerJob

        #Initialize pulp model
        model = pulp.LpProblem("Flexible_Job_Shop",pulp.LpMinimize)

        #Decision Variables

        start = {j: pulp.LpVariable(f"start_{j}", lowBound=0) for j in Jobs}
        assign = {(j,m): pulp.LpVariable(f"x_{j}_{m}", cat='Binary') for j in Jobs for m in ProcessList[j]}
        C_max = pulp.LpVariable("makespan",lowBound=0)

        #Objective is to minimize makespan
        model += C_max

        #Assign a job to at most one machine
        for j in Jobs:
            model += pulp.lpSum(assign[j,m] for m in ProcessList[j]) == 1

        #Completion time constraint
        for j in Jobs:
            model += C_max >= start[j] + pulp.lpSum(assign[j,m] * ProcessList[j][m] for m in ProcessList[j])

        #Predecessor constraint
        for j in Jobs:            
            for pred in j.getPredecessors():
                model += start[j] >= start[pred] + pulp.lpSum(assign[pred,m]*ProcessList[pred][m] for m in ProcessList[pred])

        #No overlap on the same machine
        M = 1000
        for m in Resources:
            Available_jobs = [j for j in Jobs if m in ProcessList[j]]
            for i in Available_jobs:
                for j in Available_jobs:
                    if i != j:
                        y = pulp.LpVariable(f"y_{i}_{j}_{m}", cat='Binary')
                        model += start[i] + assign[i,m] * ProcessList[i][m] <= start[j] + M*(1-y)
                        model += start[j] + assign[j,m]*ProcessList[j][m] <= start[i] + M*y

        #Solve the model
        model.solve()

        #Results / progress

        Progress.value+=" Status: "+str(pulp.LpStatus[model.status])+"\n" 
        Progress.value+=" Makespan: "+str(C_max.varValue)+"\n"
        for j in Jobs:            
            Progress.value+=" Job "+str(j.getName())+" starts at "+str(start[j].varValue)+"\n"
            for m in ProcessList[j]:
                if assign[j,m].varValue == 1:                    
                    Progress.value+=" Assigned to machine "+str(m.getName())+"\n"         

            
        return 
        
        