from PlanningObjects import *


class BaselineBatchingAlg:
    def __init__(self):
        self.timelimit = 60


    def RecPredcount(self,job):
        
        curr_count = len(job.getPredecessors())
        
        for pred in job.getPredecessors():
            curr_count+=self.RecPredcount(pred)
     
        return curr_count

    def SolveBatching(self,OprDict,ScheduleMgr,Progress):

        Progress.value +="Batching...Oprs: "+str(len(OprDict))+"\n"
        precendences= []
        nrjobs = 0
        newoprdict = dict()
        for opr,jobs in OprDict.items():
            predno = 0
            nrjobs+=len(jobs)
            if opr.getProduct().getBatchsize() == None:
                newoprdict[opr] = jobs
                continue
            if len(jobs) == 0:
                continue
            for job in jobs: 
                predno+= self.RecPredcount(job)
            #Progress.value += opr.getName()+": "+str(predno/len(jobs))+"\n"
            precendences.append((opr,predno/len(jobs)))
        
        Progress.value +="Oprs....: "+str(len(precendences))+"\n" 
        predsorted = sorted(precendences, key=lambda x: x[1], reverse=False)
        Progress.value +="Sorted Oprs....: "+str(len(predsorted))+"\n" 

        nrbjobs = 0
        for oprinfo in predsorted:
            Progress.value += oprinfo[0].getName()+"\n"
            Progress.value += ".... "+str(oprinfo[1])+"\n"
            opr = oprinfo[0]
            jobs = OprDict[opr]
            jobs = sorted(jobs, key=lambda x: x.getDeadLine(), reverse=False)
        
            batchsize = opr.getProduct().getBatchsize()
            Progress.value += "operation... "+opr.getName()+", jobs: "+str(len(jobs))+", batchsize: "+str(batchsize)+"\n"
         

            BatchJobs = [] 
            nrbjobs+=1
            batchjob = Job(nrbjobs,"BatchJob_"+str(nrbjobs),opr.getProduct(),opr,0,None)  #myid,myname,myprod,myopr,myqnty,myddline
            BatchJobs.append(batchjob)
            Progress.value += "initial batchjob created... "+batchjob.getName()+"\n"
            for job in jobs: 
                Progress.value += "checking... "+job.getName()+" Q: "+str(job.getQuantity())+"\n"
                
                if (batchjob.getQuantity()+job.getQuantity())//batchsize <= 1:
                    
                    if not job.getCustomerOrder() in batchjob.getOrderJobs():
                        batchjob.getOrderJobs()[job.getCustomerOrder()] = []
                    batchjob.getOrderJobs()[job.getCustomerOrder()].append((job,job.getQuantity())) 
                    job.setBatched()
                    # update properties: precedences and deadlines 
                    for pred in job.getPredecessors():
                        if not pred in batchjob.getPredecessors():
                            batchjob.getPredecessors().append(pred)
                            Progress.value += "predecessor "+pred.getName()+" linked to batchjob.."+"\n"
                            if not batchjob in pred.getSuccessors():
                                pred.getSuccessors().append(batchjob)
                    for succ in job.getSuccessors():
                        if not succ in batchjob.getSuccessors():
                            batchjob.getSuccessors().append(succ)
                            Progress.value += "successor... "+succ.getName()+" linked to batchjob.."+"\n"
                    Progress.value += "batchjob Q... "+str(batchjob.getQuantity())+"\n"
                    if batchjob.getQuantity() == batchsize:
                        nrbjobs+=1
                        batchjob = Job(nrbjobs,"BatchJob_"+str(nrbjobs),opr.getProduct(),opr,0,None)
                        Progress.value += "batchjob created... "+batchjob.getName()+"\n"
                        BatchJobs.append(batchjob)
                 
                    Progress.value += "comp checking... "+job.getName()+" Q: "+str(job.getQuantity())+"\n"    
                    
                else:
                    
                    remainQuantity = job.getQuantity() 

                    while remainQuantity > 0: 
                        addQuantity = min(batchsize,remainQuantity)                                 
                        if not job.getCustomerOrder() in batchjob.getOrderJobs():
                            batchjob.getOrderJobs()[job.getCustomerOrder()] = []
                        batchjob.getOrderJobs()[job.getCustomerOrder()].append((job,addQuantity))
                        job.setBatched()
                        # update properties: precedences and deadlines 
                        for pred in job.getPredecessors():
                            if not pred in batchjob.getPredecessors():
                                batchjob.getPredecessors().append(pred)
                                if not batchjob in pred.getSuccessors():
                                    pred.getSuccessors().append(batchjob)
                                Progress.value += "predecessor "+pred.getName()+" linked to batchjob.."+"\n"
                        for succ in job.getSuccessors():
                            if not succ in batchjob.getSuccessors():
                                batchjob.getSuccessors().append(succ)
                                Progress.value += "successor... "+succ.getName()+" linked to batchjob.."+"\n"

                        if batchjob.getQuantity() == batchsize:
                            nrbjobs+1
                            batchjob = Job(nrbjobs,"BatchJob_"+str(nrbjobs),opr.getProduct(),opr,0,None)
                            Progress.value += "batchjob created... "+batchjob.getName()+"\n"
                            BatchJobs.append(batchjob)
                        remainQuantity = remainQuantity - addQuantity
                
                  
            if (batchjob.getQuantity() < batchsize) and (batchjob.getQuantity() > 0):
                nrbjobs+=1
                stock_job =  Job(nrbjobs,"StockJob_"+str(nrbjobs),opr.getProduct(),opr,(batchsize-batchjob.getQuantity()),None)
                Progress.value += "StockJob_ created... "+stock_job.getName()+", Q: "+str(stock_job.getQuantity())+"\n"
                batchjob.getOrderJobs()["Stock"] = []
                batchjob.getOrderJobs()["Stock"].append((stock_job,stock_job.getQuantity())) 

            newoprdict[opr] = BatchJobs           
               
        
        return newoprdict
            
                
            
            
   