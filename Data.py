"""
Created on Wed Apr  3 11:46:59 2024

@author: mfirat
"""

##### import ipywidgets as widgets
from IPython.display import clear_output
from IPython import display
from ipywidgets import *
from datetime import timedelta,date,datetime
import matplotlib.pyplot as plt
import warnings
import seaborn as sns
import os
import pandas as pd
import warnings
import sys
import numpy as np
from pathlib import Path
from PlanningObjects import *
from Visual import *
from io import BytesIO,StringIO
import time

warnings.filterwarnings("ignore")


class DataManager:
    def __init__(self):        
        # Lists..
        self.Resources = dict()  # key: ResourceName, val: ResourceObject
        self.Products = dict() # key: Productname, val: ProductObject
        self.CustomerOrders  = dict() # key: Ordername, val: OrderObject
        self.Operations = dict()  # key: OperationName, val: OperationObjec
        self.MachineGroups = [] 
        self.OperatingTeams = []
        self.VisualManager = None
        self.SimulationManager = None
        self.SchedulingManager = None
        
        self.colabpath = '/content/ProductionPlanning'
        self.onlineversion = False       
        self.UseCase = None
        self.MyFolder = None
        
        return
        
    def getSchedulingManager(self):
        return self.SchedulingManager

    def setSchedulingManager(self,myitm):
        self.SchedulingManager = myitm
        return 
    
    def setSimulationManager(self,myit):
        self.SimulationManager = myit
        return

    def getSimulationManager(self):
        return self.SimulationManager
       

    def setUseCase(self,usecase):
        self.UseCase = usecase
        return 

    
    def getUseCase(self):
        return self.UseCase

    def setMyFolder(self,usecase):
        self.MyFolder = usecase
        return 

    
    def getMyFolder(self):
        return self.MyFolder
        

    def getOperatingTeams(self):
        return self.OperatingTeams
        
    def getMachineGroups(self):
        return self.MachineGroups
        
    def setOnlineVersion(self,ver):
        self.onlineversion = ver
        return

    def isOnlineVersion(self):
        return self.onlineversion 
        
    def getProducts(self):
        return self.Products

    def getOperations(self):
        return self.Operations
    def getResources(self):
        return self.Resources
    def getCustomerOrders(self):
        return self.CustomerOrders

    def setCustomerOrders(self,mydict):
        self.CustomerOrders = mydict
        return

    def getVisualManager(self):
        return self.VisualManager
    def setVisualManager(self,myvm):
        self.VisualManager = myvm
        return


    def getJobID(self):

        jobid = 0

        for opname,opr in self.Operations.items():
            jobid+=len(opr.getJobs())

        return jobid
    def CreateOperation(self,info,oprlist):

        name, processtime = info

        self.Operations[name] = Operation(len(self.Operations),name,processtime)
        oprlist.options = [opname for opname in self.Operations.keys()]
        
        return


    def CreateResource(self,info,reslist):

        name,mytype,daycap = info
        # (self,myid,mytype,myname,mydaycp)
        self.Resources[name]=Resource(len(self.Resources),mytype,name,daycap)
        reslist.options = [resname for resname in self.Resources.keys()]
        
        return

    def CreateProduct(self,info,prodlist,prodlist2):

        name,mypn,stklvl = info
        
        self.Products[name]= Product(len(self.Products),name,mypn,stklvl)
        prodlist.options = [pname for pname in self.Products.keys()]
        prodlist2.options = [pname for pname in self.Products.keys()]
        
        return
        
    def MatchResourceOperation(self,resources,operations):


        self.getVisualManager().getCaseInfo().value += ">>>res-opr... "+"\n" 
        if (resources.value is None) or (operations.value is None):
            return

        Opr = self.Operations[operations.value]
        Res = self.Resources[resources.value]

        
                
        Res.getOperations().append(Opr)
        Opr.getRequiredResources().append(Res)

        self.getVisualManager().getCaseInfo().value += ">>>res-opr... "+str(Res.getName())+"-> "+str(Opr.getName())+"\n" 
        
        return
        
    

    def DefinePrecedence(self,prodlist,prodlist2):

        self.getVisualManager().getCaseInfo().value += ">>>precedence... "+"\n" 

        
        if (prodlist.value is None) or (prodlist2.value is None):
            return

        if prodlist.value == prodlist2.value:
            return

      
        Prod1 = self.Products[prodlist.value] 
        Prod2 = self.Products[prodlist2.value] 

        self.getVisualManager().getCaseInfo().value += ">>>precedence... "+str(Prod1.getName())+"-> "+str(Prod2.getName())+"\n" 


        Prod2.getPredecessors().append(Prod1)
        Prod1.setSuccessor(Prod2)

        return

    def AssignOperation(self,prodlist,oprlist):

        self.getVisualManager().getCaseInfo().value += ">>>assign prod-opr... "+"\n" 
        
        if (prodlist.value is None) or (oprlist.value is None):
            return

        Prod = self.Products[prodlist.value]  
        Opr =  self.Operations[oprlist.value]

        self.getVisualManager().getCaseInfo().value += ">>>assign prod-opr... "+str(Opr.getName())+"->"+str(Prod.getName())+"\n" 

        Prod.getOperations().append(Opr)

        return

    def CreateCustomerOrder(self,info):
    #(self,myid,myname,myprodid,myprodname,myqnty,myddline):  
        if (self.VisualManager.getPSTBProdList().value is None):
            return

        myname,myq,myddline = info

        Prod = self.Products[self.VisualManager.getPSTBProdList().value]  
      
        self.CustomerOrders[myname]=CustomerOrder(len(self.CustomerOrders),myname,Prod.getID(),Prod.getName(),myq,myddline)
        self.CustomerOrders[myname].setProduct(Prod)
        self.VisualManager.getCOTBorders().options = [myordname for myordname in self.CustomerOrders.keys()]

        return
        
  

    def SaveInstance(self,event):

        # Save Products.
        products_df = pd.DataFrame(columns= ["ProductID","ProductNumber","Name"])
        precedences_df = pd.DataFrame(columns= ["PredecessorID","SuccessorID","Multiplier"])
        prodrops_df = pd.DataFrame(columns= ["ProductID","OperationID","OperationIndex"])
        operations_df = pd.DataFrame(columns= ["OperationID","Name","ProcessTime"])
        opsres_df = pd.DataFrame(columns= ["OperationID","ResourceID"])
        resources_df = pd.DataFrame(columns= ["ResourceID","ResourceType","Name","DailyCapacity"])
        orders_df = pd.DataFrame(columns= ["OrderID","ProductID","ProductName","Name","Quantity","Deadline"])

        self.getVisualManager().getCaseInfo().value += ">>> save instance.."+"\n" 
        
        for name,myprod in self.Products.items():
            products_df.loc[len(products_df)] = {"ProductID":myprod.getID(), "ProductNumber":myprod.getPN(),"Name":myprod.getName(),"StockLevel":myprod.getStockLevel()}

            
            for pred in myprod.getPredecessors():
                precedences_df.loc[len(precedences_df)] = {"PredecessorID":pred.getID(),"SuccessorID":myprod.getID(),"Multiplier":1}
 
            oprind = 0
            for opr in myprod.getOperations():
                self.getVisualManager().getCaseInfo().value += ">>> prod-opr..Opr"+str(opr.getID())+"->Prod"+str(myprod.getID())+"\n" 
                prodrops_df.loc[len(prodrops_df)] = {"ProductID":myprod.getID(),"OperationID":opr.getID(),"OperationIndex":oprind}
                oprind+=1

        self.getVisualManager().getCaseInfo().value += ">>> save products done.."+str(len(products_df))+"\n" 

        for opname,opr in self.Operations.items():
            operations_df.loc[len(operations_df)]= {"OperationID":opr.getID(),"Name":opr.getName(),"ProcessTime":opr.getProcessTime()}
            
            for res in opr.getRequiredResources():
                self.getVisualManager().getCaseInfo().value += ">>> opr-ress.."+"\n" 
                opsres_df.loc[len(opsres_df)]= {"OperationID":opr.getID(),"ResourceID":res.getID()}
                

        self.getVisualManager().getCaseInfo().value += ">>> save operations done.."+str(len(operations_df))+"\n" 
        

        for resname,res in self.Resources.items():
            resources_df.loc[len(resources_df)] ={"ResourceID":res.getID(),"ResourceType":res.getType(),"Name":res.getName(),"DailyCapacity":res.getDailyCapacity()}

        self.getVisualManager().getCaseInfo().value += ">>> save resources done.."+str(len(resources_df))+"\n" 
        
        for ordname,ordr in self.CustomerOrders.items():
            orders_df.loc[len(orders_df)]={"OrderID":ordr.getID(),"ProductID":ordr.getProduct().getID(),"ProductName":ordr.getProduct().getName(),"Name":ordr.getName(),"Quantity":ordr.getQuantity(),"Deadline":ordr.getDeadLine()}

        self.getVisualManager().getCaseInfo().value += ">>> save orders done.."+str(len(orders_df))+"\n" 


        folder = 'UseCases'; casename = self.getVisualManager().getCOTBcasename().value
        path = folder+"\\"+casename
        isExist = os.path.exists(path)

        if not isExist:
            os.makedirs(path)
       
        
        filename = 'Products.csv'; path = folder+"\\"+casename+"\\"+filename;  fullpath = os.path.join(Path.cwd(), path)
        self.getVisualManager().getCaseInfo().value += ">>> products save folder.."+str(path)+"\n" 
        products_df.to_csv(path, index=False)
        filename = 'Precedences.csv';path = folder+"\\"+casename+"\\"+filename; fullpath = os.path.join(Path.cwd(), path)
        precedences_df.to_csv(fullpath, index=False)
        filename = 'ProductsOperations.csv'; path = folder+"\\"+casename+"\\"+filename; fullpath = os.path.join(Path.cwd(), path)
        prodrops_df.to_csv(fullpath, index=False)
        filename = 'ResourcesOperations.csv'; path = folder+"\\"+casename+"\\"+filename; fullpath = os.path.join(Path.cwd(), path)
        opsres_df.to_csv(fullpath, index=False)
        filename = 'Operations.csv'; path = folder+"\\"+casename+"\\"+filename; fullpath = os.path.join(Path.cwd(), path)
        operations_df.to_csv(fullpath, index=False)
        filename = 'Resources.csv'; path = folder+"\\"+casename+"\\"+filename; fullpath = os.path.join(Path.cwd(), path)
        resources_df.to_csv(fullpath, index=False)
        filename = 'CustomerOrders.csv'; path = folder+"\\"+casename+"\\"+filename;fullpath = os.path.join(Path.cwd(), path)
        orders_df.to_csv(fullpath, index=False)
        filename = 'OperatorsMachines.csv'; path = folder+"\\"+casename+"\\"+filename;fullpath = os.path.join(Path.cwd(), path)
        oprmch_df.to_csv(fullpath, index=False)

        return
    def ImportOrders2(self,b):

       
        if 'new' in b:
            if 'value' in b['new']:
                
                if 'name' in b['new']['value'][0]:
                   
                    content = BytesIO(b['new']['value'][0]['content'])
                    orders_df = pd.read_csv(content)
                    
                    
                    prev_size = len(self.CustomerOrders)

                    for i,r in orders_df.iterrows():
                        if not r["Name"] in self.CustomerOrders:
                            neworder = CustomerOrder(len(self.CustomerOrders),r["Name"],r["ProductID"],r["ProductName"],r["Quantity"],r["Deadline"])
                            if neworder.getProductName() in self.Products:
                                neworder.setProduct(self.Products[neworder.getProductName()])
                            else: 
                                self.getVisualManager().getDiagInfo().value += "Product"+str(neworder.getProductName())+" not found, so being created.."+"\n"
                                newprod = Product(len(self.Products),neworder.getProductName(),"XXXXXX",0)
                                self.Products[neworder.getProductName()]= newprod
                                neworder.setProduct(newprod)
                                
                            self.CustomerOrders[r["Name"]] = neworder   
                    
                    self.getVisualManager().getPSTBProdList().options = [prname for prname in self.Products.keys()]
                                
                    self.getVisualManager().getDiagInfo().value += "Orders updated.."+str(prev_size)+"->"+str(len(self.CustomerOrders))+"\n"     
            
                   
            
                    self.getVisualManager().getCOTBorders().options =  [myordname for myordname in self.CustomerOrders.keys()]



        #input_file = list(self.getVisualManager().getNewCustOrdrs_btn().value.values())[0]
        #content = input_file['content']
        #content = io.StringIO(content.decode('utf-8'))
        #df = pd.read_csv(content)


        #self.getVisualManager().getCaseInfo().value += ">>> File read, size: ..."+str(len(df))+" \n"
        return
    
    
   
    def ImportOrders(self,b):  

        rel_path = self.getVisualManager().getFolderNameTxt().value+'/'+self.getVisualManager().getCasesDrop().value+'/'+'input_files'
        orders_df = pd.DataFrame()

        if self.onlineversion:
            self.getVisualManager().getCaseInfo().value += ">>> Online version, aborted... \n"
            return
        else:
            abs_file_path = os.path.join(Path.cwd(), rel_path)

        filefound = False

        for root, dirs, files in os.walk(abs_file_path):
            for file in files:
                self.getVisualManager().getDiagInfo().value += ">>> reading file "+file+"... \n"
                if file.find("OrderDelta") != -1:
                    orders_df = pd.read_csv(abs_file_path+'/'+file)
                    self.getVisualManager().getDiagInfo().value += "Orders to imports.."+str(len(orders_df))+"\n"    
                    filefound = True
                    break
            if filefound:
                break

        prev_size = len(self.CustomerOrders)

        
        for i,r in orders_df.iterrows():
            if not r["Name"] in self.CustomerOrders:
                neworder = CustomerOrder(len(self.CustomerOrders),r["Name"],r["ProductID"],r["ProductName"],r["Quantity"],r["Deadline"])
                if neworder.getProductName() in self.Products:
                    neworder.setProduct(self.Products[neworder.getProductName()])
                else: 
                    self.getVisualManager().getDiagInfo().value += "Product"+str(neworder.getProductName())+" not found, so being created.."+"\n"
                    newprod = Product(len(self.Products),neworder.getProductName(),"XXXXXX",0)
                    self.Products[neworder.getProductName()]= newprod
                    neworder.setProduct(newprod)
                    
                self.CustomerOrders[r["Name"]] = neworder   
        
        self.getVisualManager().getPSTBProdList().options = [prname for prname in self.Products.keys()]
                    
        self.getVisualManager().getDiagInfo().value += "Orders updated.."+str(prev_size)+"->"+str(len(self.CustomerOrders))+"\n"     

       

        self.getVisualManager().getCOTBorders().options =  [myordname for myordname in self.CustomerOrders.keys()]


        return

    def SaveSchedule(self,myschedule):

        self.getVisualManager().getSchedulingTab().getPSchScheRes().value += ">>>  saving schedule....."+str(len(myschedule.getResourceSchedules()))+"\n" 
        schjobs_df = pd.DataFrame(columns= ["JobID","Quantity","Deadline","OrderID","ProductID", "OperationID"])
        jobpreds_df =  pd.DataFrame(columns= ["JobPredecessorID","JobSuccessorID"])
        
        for name,order in self.getCustomerOrders().items():
            for job in order.getMyJobs():
                schjobs_df.loc[len(schjobs_df)] = {"JobID":job.getID(),"Quantity":job.getQuantity(),"Deadline":job.getDeadLine(),
                                                    "OrderID":job.getCustomerOrder().getID(),"ProductID":job.getProduct().getID(),
                                                    "OperationID":job.getOperation().getID()}
                for pred in job.getPredecessors():
                    jobpreds_df.loc[len(jobpreds_df)] = {"JobPredecessorID":pred.getID(),"JobSuccessorID":job.getID(),}
                    

        #self.getVisualManager().getSchedulingTab().getPSchScheRes().value += ">>>  shcjobs "+str(len(schjobs_df))+"\n" 
        #self.getVisualManager().getSchedulingTab().getPSchScheRes().value += ">>>  jobpreds "+str(len(jobpreds_df))+"\n" 


        #self.getVisualManager().getSchedulingTab().getPSchScheRes().value += ">>>  folder "+str(self.getMyFolder())+", usecase "+str(self.getUseCase())+"\n" 

  
        timestr = time.strftime("%Y%m%d-%H%M%S")
        filename = myschedule.getName()+"-Jobs_"+timestr+".csv"; 
        #self.getVisualManager().getSchedulingTab().getPSchScheRes().value += ">>>  filename "+str(filename)+"\n" 

        
        path = self.getMyFolder()+"\\"+self.getUseCase()+"\\"+filename
        fullpath = os.path.join(Path.cwd(), path)
        schjobs_df.to_csv(fullpath, index=False)

        filename = myschedule.getName()+"-Jobpreds_"+timestr+".csv"; 
        #self.getVisualManager().getSchedulingTab().getPSchScheRes().value += ">>>  filename "+str(filename)+"\n" 

        path = self.getMyFolder()+"\\"+self.getUseCase()+"\\"+filename
        fullpath = os.path.join(Path.cwd(), path)
        jobpreds_df.to_csv(fullpath, index=False)

        
        

        schedule_df = pd.DataFrame(columns= ["ResourceID","Day","ShiftNo","JobID","SchStart", "SchCompletion"])
        for resname,res_schedule in myschedule.getResourceSchedules().items():
            #self.getVisualManager().getSchedulingTab().getPSchScheRes().value += ">>>  res "+resname+"\n"
            for shift,jobsdict in res_schedule.items():
                #self.getVisualManager().getSchedulingTab().getPSchScheRes().value += ">>>  shift "+str(shift.getDay())+"->"+str(shift.getNumber())+"->"+str(len(jobsdict))+"\n" 
                for job,jobtimes in jobsdict.items():
                    #self.getVisualManager().getSchedulingTab().getPSchScheRes().value += str(job.getJob().getID())+"\n"
                    schedule_df.loc[len(schedule_df)] = {"ResourceID":self.getResources()[resname].getID(),
                                                             "Day":shift.getDay(),
                                                             "ShiftNo":shift.getNumber(),
                                                             "JobID":job.getJob().getID(),
                                                             "SchStart":jobtimes[0],
                                                             "SchCompletion":jobtimes[1]}
                 



        timestr = time.strftime("%Y%m%d-%H%M%S")
        filename = myschedule.getName()+"-Schedule_"+timestr+".csv"; 
        path = self.getMyFolder()+"\\"+self.getUseCase()+"\\"+filename
        fullpath = os.path.join(Path.cwd(), path)
        schedule_df.to_csv(fullpath, index=False)


        self.getVisualManager().getSchedulingTab().getPSchScheRes().value += ">>> schedule saved....."+"\n" 


        return
        
    


    def read_dataset(self,b):  


        self.setUseCase(self.getVisualManager().getCasesDrop().value)
        self.setMyFolder(self.getVisualManager().getFolderNameTxt().value)
        rel_path = self.getMyFolder()+'/'+self.getUseCase()

        self.getVisualManager().getCaseInfo().value += ">>> rel_path "+rel_path+"... \n"


        if self.onlineversion:
            abs_file_path = self.colabpath+'/'+rel_path
        else:
            abs_file_path = os.path.join(Path.cwd(), rel_path)
          
        #self.getVisualManager().getCaseInfo().value += ">>> "+rel_path+"\n" 
        #self.getVisualManager().getCaseInfo().value += "***** "+abs_file_path+"\n" 
    
        prodopmatch_df = pd.DataFrame()
        precmatch_df = pd.DataFrame()
        oprsresources_df = pd.DataFrame()

        scheduledate = None
        jobdate = None
        jobprdate = None
        schfile = None
        jobprfile = None
        jobsfile = None
        
        for root, dirs, files in os.walk(abs_file_path):
            
            for file in files: 
                if (file.find("Schedule") != -1):
                    filedate = datetime.strptime(file[file.find("_")+1:-4],"%Y%m%d-%H%M%S")
          
                    if scheduledate == None: 
                        scheduledate = filedate
                        schfile = file
                        
                    else:
                        if filedate > scheduledate:
                            scheduledate = filedate
                            schfile = file


                if (file.find("Jobs") != -1):
                    filedate = datetime.strptime(file[file.find("_")+1:-4],"%Y%m%d-%H%M%S")
          
                    if jobdate == None: 
                        jobdate = filedate
                        jobsfile = file
                        
                    else:
                        if filedate > jobdate:
                            jobdate = filedate
                            jobsfile = file


                if (file.find("Jobpreds") != -1):
                    filedate = datetime.strptime(file[file.find("_")+1:-4],"%Y%m%d-%H%M%S")
          
                    if jobprdate == None: 
                        jobprdate = filedate          
                    else:
                        if filedate > jobprdate:
                            jobprdate = filedate
                          
            
            if scheduledate!= None:
                self.getVisualManager().getCaseInfo().value += ">>> Scheduledate..."+str(scheduledate)+"\n"  

            
            for file in files:
                self.getVisualManager().getCaseInfo().value += ">>> reading file "+file+"\n" 

                
                if file.find("Jobpreds") != -1:
                    filedate = datetime.strptime(file[file.find("_")+1:-4],"%Y%m%d-%H%M%S")
                    self.getVisualManager().getCaseInfo().value += "********jobprfile date .."+str(filedate)+"~"+str(jobprdate)+"~"+str(filedate == jobprdate)+"\n"     

                    if filedate == jobprdate:
                        jobprfile = file
                        self.getVisualManager().getCaseInfo().value += "*******jobprfile .."+str(file)+"\n"     
                        
                if file.find("Jobs") != -1:
                    filedate = datetime.strptime(file[file.find("_")+1:-4],"%Y%m%d-%H%M%S")

                    self.getVisualManager().getCaseInfo().value += "jobfile date .."+str(filedate)+"~"+str(jobdate)+"~"+str(filedate == jobdate)+"\n"     

                    if filedate == jobdate:
                        jobsfile = file
                        self.getVisualManager().getCaseInfo().value += "jobsfile .."+str(file)+"\n"         
   
   

                if file == "OperatorsMachines.csv": 
                    oprmch_df = pd.read_csv(abs_file_path+'/'+file)
                    self.getVisualManager().getCaseInfo().value += "OperatorsMachines read.."+str(len(oprmch_df))+"\n"            
                
                if file == "Products.csv": 
                    prod_df = pd.read_csv(abs_file_path+'/'+file)
                    for i,r in prod_df.iterrows():
                        newprod = Product(r["ProductID"],r["Name"],r["ProductNumber"],r["StockLevel"])
                        if not np.isnan(r["PrescribedBatchsize"]):
                            newprod.setBatchsize(r["PrescribedBatchsize"])
                        self.Products[r["Name"]]= newprod
                    self.getVisualManager().getCaseInfo().value += "Products created: "+str(len(self.getProducts()))+"\n"            
                   
                if file == "Operations.csv": 
                    opr_df = pd.read_csv(abs_file_path+'/'+file)
                    for i,r in opr_df.iterrows():
                        newopr = Operation(r["OperationID"],r["Name"],r["ProcessTime"])
                        newopr.setPredecessor(r["Predecessor"])
                        self.Operations[r["Name"]]= newopr
                    self.getVisualManager().getCaseInfo().value += "Operations created: "+str(len(self.getOperations()))+"\n"            
       
                    
                if file == "Resources.csv": 
                    res_df = pd.read_csv(abs_file_path+'/'+file)
                    for i,r in res_df.iterrows():  #(self,myid,mytype,myname,mydaycp)
                        newres = Resource(r["ResourceID"],r["ResourceType"],r["Name"],r["DailyCapacity"])
                        if not np.isnan(r["Automated"]):
                            if str(r["Automated"]) == "True":
                                newres.setAutomated() 
                            
                        newres.setOperatingEffort(r["OperatingEffort"])
                        if r["Shift"] is not None:
                            newres.setAvailableShift(r["Shift"])
                        self.Resources[r["Name"]]= newres
                        if r['Name'].find("OUT - ") != -1:
                            newres.setOutsource()

                    self.getVisualManager().getCaseInfo().value += "Resources created: "+str(len(self.getResources()))+"\n" 
                    
                if file == "CustomerOrders.csv": 
                    orders_df = pd.read_csv(abs_file_path+'/'+file)
                    for i,r in orders_df.iterrows():
                        #def __init__(self,myid,myname,myprodid,myprodname,myqnty,myddline):
                        neworder = CustomerOrder(r["OrderID"],r["Name"],r["ProductID"],r["ProductName"],r["Quantity"],r["Deadline"])
                        self.CustomerOrders[r["Name"]] = neworder
                    self.getVisualManager().getCaseInfo().value += "Customer Orders created: "+str(len(self.getCustomerOrders()))+"\n"  
    
    
                if file == "ProductsOperations.csv": 
                    prodopmatch_df = pd.read_csv(abs_file_path+'/'+file)
    
                if file == "Precedences.csv": 
                    precmatch_df = pd.read_csv(abs_file_path+'/'+file)

                if file == "ResourcesOperations.csv": 
                    oprsresources_df = pd.read_csv(abs_file_path+'/'+file)                    
                        
                    self.getVisualManager().getCaseInfo().value += "ResourcesOperations: "+str(len(oprsresources_df))+"\n"  

      
       
        self.getVisualManager().getCaseInfo().value += ">>> CustomerOrders.. "+str(len(self.CustomerOrders))+"\n" 
        for ordname,myord in self.CustomerOrders.items():
            #self.getVisualManager().getCaseInfo().value += ">>> Product"+myord.getProductName()+" in "+str(myord.getProductName() in self.Products)+"\n" 
            myord.setProduct(self.Products[myord.getProductName()])

       
        #initilize first machine group..
        self.getVisualManager().getCaseInfo().value += ">>> Machine groups and operating teams.. "+str(len(oprmch_df))+"\n" 

        operators =[op for op in oprmch_df["OperatorID"].unique()]

        self.getVisualManager().getCaseInfo().value += ">>> operators "+str(len(operators))+"\n" 

        for operatorID in operators:
            operator = [myres  for resname,myres in self.getResources().items() if myres.getID() == operatorID][0]
            oprmachines =[mhid for mhid in oprmch_df[oprmch_df["OperatorID"] == operatorID]["MachineID"]]

            self.getVisualManager().getCaseInfo().value += ">>> operator "+str(operator.getName())+" linked to "+str(oprmachines)+" machines.."+"\n" 
            
            mymachgroup = None
            for machineID in oprmachines:
                mach = [myres  for resname,myres in self.getResources().items() if myres.getID() == machineID ][0]
                # check if the machine included in the previously defined ones..
                commonmachine = False
                for machgroup in self.getMachineGroups():
                    if mach in machgroup.getMachines():
                        commonmachine = True
                        mymachgroup = machgroup
                        break
                if commonmachine:
                    break
                    
            if mymachgroup != None:
                
                mymachgroup.getOperatingTeam().getOperators().append(operator)
                operator.setOperatingTeam(mymachgroup.getOperatingTeam())
                

            else:
                machgroup = MachineGroup()
                operatingteam = OperatingTeam() # assumption every operator is in exactly one team
                machgroup.setOperatingTeam(operatingteam)
                operatingteam.setMachineGroup(machgroup)

                
                for machineID in oprmachines:
                    mach = [myres  for resname,myres in self.getResources().items() if myres.getID() == machineID ][0]
                    machgroup.getMachines().append(mach) 
                    mach.setMachineGroup(machgroup)
                    
     
                operator.setOperatingTeam(operatingteam) 
                operatingteam.getOperators().append(operator)

                self.getOperatingTeams().append(operatingteam)
                self.getMachineGroups().append(machgroup)    
            
        self.getVisualManager().getCaseInfo().value += ">>> Machine groups.. "+str(len(self.getMachineGroups()))+"\n"                  
        self.getVisualManager().getCaseInfo().value += ">>> Operating teams.. "+str(len(self.getOperatingTeams()))+"\n"    
   
                             
        self.getVisualManager().getCaseInfo().value += ">>> Precedences.. "+str(len(precmatch_df))+"\n" 
        for i,r in precmatch_df.iterrows():
    
            predecessor = [myprod  for pname,myprod in self.getProducts().items() if myprod.getID() == r["PredecessorID"]] [0]
            successor = [myprod  for pname,myprod in self.getProducts().items() if myprod.getID() == r["SuccessorID"]][0]

            #self.getVisualManager().getCaseInfo().value += "->"+predecessor.getName()+">>> "+successor.getName()+"\n" 
    
            predecessor.setSuccessor(successor)
            successor.getPredecessors().append(predecessor)
            successor.getMPredecessors()[predecessor] = r["Multiplier"]
            #self.getVisualManager().getCaseInfo().value += "successor: "+str(successor.getName())+" has "+str(len(successor.getPredecessors()))+"\n" 

        self.getVisualManager().getCaseInfo().value += ">>> Product-Operations... "+str(len(prodopmatch_df))+"\n" 
                
        for i,r in prodopmatch_df.iterrows():
            prodlst = [myprod  for pname,myprod in self.getProducts().items() if myprod.getID() == r["ProductID"]]

            if len(prodlst) > 0: 
                prod = prodlst[0]
                oprlst = [myopr for opname,myopr in self.getOperations().items() if myopr.getID() == r["OperationID"]]
                if len(oprlst) > 0:
                    opr = oprlst[0]
                    opr.setProduct(prod)
                    prod.getOperations().insert(r["OperationIndex"],opr)
                else:
                    self.getVisualManager().getCaseInfo().value += "XXXX: Operation not found: "+str(r["OperationID"])+"\n" 
                    self.getVisualManager().getCaseInfo().value += "Product: "+str(prod.getName())+"\n" 
            else:
                self.getVisualManager().getCaseInfo().value += "XXXX: Product not found: "+str(r["ProductID"])+"\n" 

        self.getVisualManager().getCaseInfo().value += ">>> Operation-Resources... "+str(len(oprsresources_df))+"\n" 

        opswithmoreres = 0

        for i,r in oprsresources_df.iterrows():
            opr = [myopr for opname,myopr in self.getOperations().items() if myopr.getID() == r["OperationID"]][0]
            res = [myres  for resname,myres in self.getResources().items() if myres.getID() == r["ResourceID"]][0]

            opr.getRequiredResources().append(res)
            
            # # check if the same type of resource is already in the required resources list of operation. 
            # resinserted = False
            # for oprres in opr.getRequiredResources():
            #     if isinstance(oprres,list): # we expect that this is always true, but for now let is check. 
            #         if oprres[0].getType() == res.getType():
            #             oprres.append(res)
            #             resinserted = True
            #             break
            # if not resinserted:
            #     opr.getRequiredResources().append([res])
          
            #if len(opr.getRequiredResources())>1:
               #self.getVisualManager().getCaseInfo().value += "opr: "+str(opr.getName())+", no.res: "+str(len(opr.getRequiredResources()))+"\n" 
        earliest = None
        latest = None

        self.getVisualManager().getCaseInfo().value += ">>>> Schedule file.."+str(schfile)+"\n" 
            
        if schfile != None:
            
            schedule_df = pd.read_csv(abs_file_path+'/'+schfile)
            self.getVisualManager().getCaseInfo().value += ">>>> Schedules.."+str(len(schedule_df))+"\n" 

            self.getVisualManager().getCaseInfo().value += ">>>> Jobs file .."+str(jobsfile)+"\n" 
            jobs_df =   pd.read_csv(abs_file_path+'/'+jobsfile)
            self.getVisualManager().getCaseInfo().value += ">>>> Jobs .."+str(len(jobs_df))+"\n" 
            
            jobprecs_df =   pd.read_csv(abs_file_path+'/'+jobprfile)
            self.getVisualManager().getCaseInfo().value += ">>>> Job precedences .."+str(len(jobprecs_df))+"\n" 

            alljobs = dict() # key job id, val: job object.

            
            self.getVisualManager().getCaseInfo().value += ">>>> Schedule file read, no job precedences.."+str(len(jobprecs_df))+"\n" 
            jobpreds = []

            # initialize jobs
            for i,r in jobs_df.iterrows():
                opr = [myopr for opname,myopr in self.getOperations().items() if myopr.getID() == r["OperationID"]][0]
                newjob = Job(r["JobID"],"Job_"+str(r["JobID"]),prod,opr,r["Quantity"],r["Deadline"])   
                alljobs[newjob.getID()]= newjob
                ords = [myord  for oname,myord in self.getCustomerOrders().items() if myord.getID() == r["OrderID"]] 
                if len(ords) > 0:
                    ords[0].getMyJobs().append(newjob)
                    

            self.getVisualManager().getCaseInfo().value += "#### no jobs.."+str(len(alljobs))+"\n" 

            #set the precedences of jobs
            for jobid,job in alljobs.items():
                job_df = jobprecs_df[jobprecs_df["JobSuccessorID"] == jobid]
                jobpreds.append(len(job_df))
                for predid in job_df["JobPredecessorID"]:
                    if predid in alljobs:
                        predjob = alljobs[predid]
                        job.getPredecessors().append(predjob)
                    else: 
                        self.getVisualManager().getCaseInfo().value += ">>>> pred of job "+str(job.getID())+" not in jobs.."+"\n" 
                
                
            # now create shifts of resources    
            for i,r in schedule_df.iterrows():
                stdate = datetime.strptime(r["Day"],'%Y-%m-%d')
               #self.getVisualManager().getCaseInfo().value += ">>>> SchDaySt.."+str(stdate)+"\n" 
                if earliest == None:
                    earliest = stdate
                else:
                    if earliest > stdate:
                        earliest = stdate
                #self.getVisualManager().getCaseInfo().value += ">>>> SchDayCp.."+str(r["SchDayCp"])+"\n" 
                if latest == None:
                    latest = stdate
                else:
                    if latest < stdate:
                        latest = stdate

            if (earliest!= None) and (latest!= None):
                self.getVisualManager().getCaseInfo().value += ">>>> Schedule earliest - latest .."+str(earliest)+":"+str(latest)+"\n" 
                self.getSchedulingManager().setCurrentscheduleEnd(latest)
                
                self.getSchedulingManager().CreateShifts(earliest,latest,True)

           
            self.getVisualManager().getCaseInfo().value += ">>>> shifts created .."+"\n"     
            insertedshifts = 0
            scheduleshiftsfound = 0
            scheduleds = 0

            for jobid,job in alljobs.items():

                #self.getVisualManager().getCaseInfo().value += ">>>> Job  .."+str(job.getName())+"\n"     
                
                job_df = schedule_df[schedule_df["JobID"] == jobid]
                if len(job_df)== 0:
                    continue

                if job.getMySch() == None:
                    job.initializeMySch() 
                    job.getMySch().SetScheduled()
                resid = [x for x in job_df["ResourceID"]][0]
                res = [myres  for resname,myres in self.getResources().items() if myres.getID() == resid][0]
                job.getMySch().setScheduledResource(res)

                #self.getVisualManager().getCaseInfo().value += ">>>> Job2  .."+str(job.getName())+"\n"     
                startime = None
                comptime = None
                strtshift = None
                for i,r in job_df.iterrows():
                    
                    shftday = datetime.strptime(r["Day"],'%Y-%m-%d')
                    shftno = r["ShiftNo"]

                    if startime == None:
                        startime = r["SchStart"]
                        
                      
                    else:
                        if r["SchStart"] < startime:
                            startime = r["SchStart"]

                    if comptime == None:
                        comptime = r["SchCompletion"]
                    else:
                        if r["SchCompletion"] > comptime:
                            comptime = r["SchCompletion"]
                        
                    shifts = [x for x in res.getSchedule().keys() if (x.getDay() == shftday) and (x.getNumber() == shftno)] 
                    
                    if len(shifts)  == 0:
                        self.getVisualManager().getCaseInfo().value += ">>>> Execution in  .."+str(shftday)+"--"+str(shftno)+"\n"         
                        self.getVisualManager().getCaseInfo().value += ">>>> Shifts found  .."+str(len(shifts))+"\n"
                    else:
                        res.getSchedule()[shifts[0]].append(job.getMySch())
                        if r["SchStart"] == startime:
                            job.getMySch().setScheduledShift(shifts[0])
                        if r["SchCompletion"] == comptime:
                            job.getMySch().setScheduledCompShift(shifts[0])

                if (startime != None) and (comptime!= None):
                    job.getMySch().setStartTime(startime)        
                    job.getMySch().setCompletionTime(comptime)   
                    #self.getVisualManager().getCaseInfo().value += ">>>> Job  .."+str(job.getName())+": "+str(job.getMySch().getStartTime())+"-"+str(job.getMySch().getCompletionTime())+"\n"     
                    
          

            #self.getVisualManager().getCaseInfo().value += ">>>> i2.."+str(i)+"\n" 
                
            #self.getVisualManager().getCaseInfo().value += ">>>> SchDaySt.."+str(r["SchDaySt"])+"\n" 
            

            
        self.getVisualManager().getCaseInfo().value += ">>>> Shifts and schedules created .."+"\n"     
                
                   
     
    
        self.getVisualManager().RefreshViews()

        self.getVisualManager().getUSTBCustomerOders().value = str(len(self.CustomerOrders))
        self.getVisualManager().getUSTBProducts().value = str(len(self.getProducts()))
        self.getVisualManager().getUSTBRawMaterials().value = str(len([prod for prod in self.getProducts().values() if len(prod.getMPredecessors()) == 0]))
        self.getVisualManager().getUSTBRawResources().value = str(len(self.getResources()))
                
        return

    def UpdateData(self,b):
        '''
        Tis function imports prodction orders including: 
        - Product: Final product
        - ID: Unque ID of the production order
        - Quantity To Produce  
        - Deadline
        - Components/Product: Raw material
        - Work Orders/Work Center: Operations to execute
        - Work Orders/Expected Duration: Process times
        - Work Orders/Subcontract Wo: Outsourced operation
        - Work Orders/Work Center/ID: Unique ID of the operation.
        '''
    
        if 'new' in b:
            if 'value' in b['new']:
                
                if 'name' in b['new']['value'][0]:
                   
                    content = BytesIO(b['new']['value'][0]['content'])
                    
                    if  self.getVisualManager().getNewCustOrdrs_btn().description == "Import orders":

                        self.getVisualManager().getNewCustOrdrs_btn().description = "Import resources"
                        self.getVisualManager().getNewCustOrdrs_btn().accept='.csv'
                      
                        TBRM_df = pd.read_excel(content)
    
                        self.getVisualManager().getDiagInfo().value += "No data lines to import "+str(len(TBRM_df))+"\n"  
           
                        self.getVisualManager().getDiagInfo().value += "Nan ID values: "+str(sum([int(pd.isna(x)) for x in TBRM_df["ID"]]))+"\n" 
                        self.getVisualManager().getDiagInfo().value += "Nan Product values: "+str(sum([int(pd.isna(x)) for x in TBRM_df["Product"]]))+"\n"  
                        self.getVisualManager().getDiagInfo().value += "Nan Operation values: "+str(sum([int(pd.isna(x)) for x in TBRM_df["Work Orders/Work Center"]]))+"\n"  
    
                        noorders = 0
                        nrproducts = 1
                        nroprs = 0
                        nrresources = 0
                        for i,r in TBRM_df.iterrows():
     
                            if (not pd.isna(r['Product'])) and (not (pd.isna(r['ID']))):
                                
                                noorders+=1
                                myorder = None
                                myprod = None
                                
                                
                                pnstr = r['Product'][r['Product'].find("[")+1:]
                                namestr = pnstr[pnstr.find("]")+1:]
                                pnstr =  pnstr[:pnstr.find("]")]
    
                                self.getVisualManager().getDiagInfo().value += "pn... "+str(pnstr)+"\n" 
    
                                pname =  "["+pnstr+"] "+namestr
        
                                if not pname in self.Products: 
                                    myprod = Product(nrproducts,pname,pnstr,0)
                                    myprod.setCreated(datetime.now())
                                    self.Products[pname]= myprod   
                                    nrproducts+=1
                                        
                                else:
                                    myprod = self.Products[pname]
                                    
    
                                #read the raw material: start
                                if not pd.isna(r['Components/Product']):
                                    rawpnstr = r['Components/Product'][r['Components/Product'].find("[")+1:]
                                    rawnamestr = rawpnstr[rawpnstr.find("]")+1:]
                                    rawpnstr =  rawpnstr[:rawpnstr.find("]")]
    
                                    myrawprod = None

                                    
    
                                    rawname = "["+rawpnstr+"] "+rawnamestr
                                    if not rawname in self.Products:
                                        myrawprod = Product(r['Components/Product/ID'],rawname,rawpnstr,0)
                                        myrawprod.setCreated(datetime.now())
                                        nrproducts+=1
                                        self.Products[rawname]= myrawprod 
                                    else:
                                        myrawprod = self.Products[rawname]
                                        
    
                                    if not myrawprod in myprod.getPredecessors():
                                        myprod.getPredecessors().append(myrawprod)
                                        if int(r['Components/Quantity To Consume']) == 0:
                                            myprod.getMPredecessors()[myrawprod] = 1
                                        else:
                                            myprod.getMPredecessors()[myrawprod] = int(r['Components/Quantity To Consume'])
                            
                                #read the raw material: end
                                
    
                                # creation of operations: start
                                if (not pd.isna(r['Work Orders/Work Center'])):
    
                                    prev_op = None
                                    oprind = 0
                                    myopr = None
    
                                    # create the very first operation..
                                    if not pd.isna(TBRM_df.loc[i,'Work Orders/Work Center']):
    
                                        myopr = None
                                        
                                        if not "["+pnstr+"] "+TBRM_df.loc[i,'Work Orders/Work Center'] in self.Operations:

                                            proctime = TBRM_df.loc[i,'Work Orders/Expected Duration']

                                            if TBRM_df.loc[i,'Work Orders/Work Center'].find("OUT -")== -1:
                                                proctime = float(proctime)/float(r['Quantity To Produce'])
                                                

                                            
                                            myopr = Operation(TBRM_df.loc[i,'Work Orders/Work Center/ID'] ,"["+pnstr+"] "+TBRM_df.loc[i,'Work Orders/Work Center'],proctime)
                                            nroprs+=1
                                            newres = None
                                            if not TBRM_df.loc[i,'Work Orders/Work Center'] in self.Resources:
                                                restype = "Machine"
                                                if TBRM_df.loc[i,'Work Orders/Work Center'].find("OUT - ") > -1:
                                                    restype = "Outsourced"
                                                    
                                                newres = Resource(nrresources,restype,TBRM_df.loc[i,'Work Orders/Work Center'] ,2)
                                                nrresources+1
                                                self.Resources[TBRM_df.loc[i,'Work Orders/Work Center']] = newres
                                            else:
                                                newres = self.Resources[TBRM_df.loc[i,'Work Orders/Work Center']]
    
                                            myopr.getRequiredResources().append(newres)
    
                                            prev_op = myopr
                                            self.Operations["["+pnstr+"] "+TBRM_df.loc[i,'Work Orders/Work Center']]= myopr
                                            myopr.setProduct(myprod)
                                            myopr.setOperationIndex(oprind)
                                            oprind+=1
                                            myprod.getOperations().append(myopr)
                                            
                                        else:
                                            myopr = self.Operations["["+pnstr+"] "+TBRM_df.loc[i,'Work Orders/Work Center']]
                                            prev_op = myopr
                                            
                                            
                                        
                                    lineno = i+1
                                    operations = [r['Work Orders/Work Center']]
    
                                  
                                    while pd.isna(TBRM_df.loc[lineno,'Product']):
                                        if pd.isna(TBRM_df.loc[lineno,'Work Orders/Work Center']):
                                            break
                                        self.getVisualManager().getDiagInfo().value += "oprtn "+str(TBRM_df.loc[lineno,'Work Orders/Work Center'])+"\n" 
    
                                        
                                        if not TBRM_df.loc[lineno,'Work Orders/Work Center'] in self.Operations:
                                            proctime = TBRM_df.loc[lineno,'Work Orders/Expected Duration']
                                            myopr = Operation(nroprs,"["+pnstr+"] "+TBRM_df.loc[lineno,'Work Orders/Work Center'],float(proctime)/float(r['Quantity To Produce']))
                                            nroprs+=1
    
                                            newres = None
                                            if not TBRM_df.loc[lineno,'Work Orders/Work Center'] in self.Resources:
                                                restype = "Machine"
                                                if TBRM_df.loc[lineno,'Work Orders/Work Center'].find("OUT - ") > -1:
                                                    restype = "Outsourced"    
                                                newres = Resource(nrresources,restype,TBRM_df.loc[lineno,'Work Orders/Work Center'] ,2)
                                                nrresources+1
                                                self.Resources[TBRM_df.loc[lineno,'Work Orders/Work Center']] = newres
                                            else:
                                                newres = self.Resources[TBRM_df.loc[lineno,'Work Orders/Work Center']]
    
                                            myopr.getRequiredResources().append(newres)
    
                                            
                                            if prev_op!= None:
                                                myopr.setPredecessor(prev_op)
                                            prev_op = myopr
                                            self.Operations["["+pnstr+"] "+TBRM_df.loc[lineno,'Work Orders/Work Center']]= myopr
                                            myopr.setProduct(myprod)
                                            myopr.setOperationIndex(oprind)
                                            oprind+=1
                                            myprod.getOperations().append(myopr)
                                            
                                        else:
                                            myopr = self.Operations[TBRM_df.loc[lineno,'Work Orders/Work Center']]
    
                                       
                                        operations.append(TBRM_df.loc[lineno,'Work Orders/Work Center'])
                                        lineno+=1
                                        if lineno >= len(TBRM_df):
                                            break
                                            
    
                                    self.getVisualManager().getDiagInfo().value += "No operations "+str(len(operations))+"\n" 
                                # creation of operations: end
                                
                                ordname = str(myprod.getName())+"_"+str(r['Quantity To Produce'])
                                self.getVisualManager().getDiagInfo().value += "ordname..."+str(ordname)+"\n" 
                                self.getVisualManager().getDiagInfo().value += "line "+str(i)+"\n"  
                                myorder = None
                                if not ordname in self.CustomerOrders:
                                    myDeadLine = datetime.strptime("2025-12-31 00:00:00","%Y-%m-%d %H:%M:%S")
                                    self.getVisualManager().getDiagInfo().value += "deadline null?..."+str(pd.isnull(r['Deadline']))+"\n" 
                                    if not pd.isnull(r['Deadline']) :
                                        myDeadLine = datetime.strptime(str(r['Deadline']),"%Y-%m-%d %H:%M:%S")   
                                    myorder = CustomerOrder(r['ID'],ordname,myprod.getID(),myprod.getName(),int(r['Quantity To Produce']),myDeadLine)
                                    myorder.setProduct(myprod)
                                   
                                    
                                    self.CustomerOrders[ordname] = myorder
                                else:
                                    myorder = self.CustomerOrders[ordname]

                                myorder.SetComponentAvailable(r['Component Status'])
                        
                      
                                    
                                        
                       
                            
                        self.getVisualManager().getDiagInfo().value += "Production orders "+str(noorders)+"\n"  
                            
                        self.getVisualManager().RefreshViews()  

                    else:
                        if self.getVisualManager().getNewCustOrdrs_btn().description == "Import resources":
                            self.getVisualManager().getNewCustOrdrs_btn().layout.visibility = 'hidden'
                            
                            resources_df = pd.read_csv(content)
                            
                            self.getVisualManager().getDiagInfo().value += "No resources "+str(len(resources_df))+"\n" 
                            
                            for i,r in resources_df.iterrows():
                                #ResourceID,ResourceType,Name,DailyCapacity,Automated,Alternatives,OperatingEffort,AvailableShifts
                                myres = None

                                res_code = r['Name'][:r['Name'].find("_")]
                                res_model = r['Name'][r['Name'].find("_")+1:]

                                self.getVisualManager().getDiagInfo().value += "Resource "+str(r['Name'])+"\n" 

                                matches = [r for rn,r in self.Resources.items() if (res_code in rn) and (res_model in rn)]

                                self.getVisualManager().getDiagInfo().value += "Matches"+str(len(matches))+"\n" 
                                
                                if len(matches) == 0:
                                    self.getVisualManager().getDiagInfo().value += "Restpye: "+str(r["ResourceType"])+"\n" 
                                    
                                    myres = Resource(r["ResourceID"],r["ResourceType"],r["Name"],r["DailyCapacity"])  
                                    self.Resources[r['Name']] = myres
                                    
                                else:

                                    
                                    myres = matches[0]
                                    

                                if not np.isnan(r["Automated"]):
                                    if str(r["Automated"]) == "True":
                                        myres.setAutomated()
                                myres.setOperatingEffort(float(r["OperatingEffort"]))
                                

                                if not r["AvailableShifts"] == None:
                                    myres.getAvailableShifts().clear()
                                    if str(r["AvailableShifts"]).find("_") != -1: 
                                        shifts = str(r["AvailableShifts"]).split("_")
                                        for shift in shifts:
                                            myres.getAvailableShifts().append(int(shift))
                                    else:
                                        myres.getAvailableShifts().append(int(r["AvailableShifts"]))

                                
                            for i,r in resources_df.iterrows():
                                myres = None

                                res_code = r['Name'][:r['Name'].find("_")]
                                res_model = r['Name'][r['Name'].find("_")+1:]

                                self.getVisualManager().getDiagInfo().value += "Resource "+str(r['Name'])+"\n" 

                                matches = [r for rn,r in self.Resources.items() if (res_code in rn) and (res_model in rn)]

                                self.getVisualManager().getDiagInfo().value += "Matches"+str(len(matches))+"\n" 
                                
                                if len(matches) == 0:
                                    
                                    myres = Resource(r["ResourceID"],r["ResourceType"],r["Name"],r["DailyCapacity"])  
                                    self.Resources[r['Name']] = myres
                                    
                                else:
                                    myres = matches[0]

                                if not pd.isnull(r["Alternatives"]):
                                    self.getVisualManager().getDiagInfo().value += "Alternatives"+str(r["Alternatives"])+" >> "+str(str(r["Alternatives"]).find("~"))+"\n" 
                                    if str(r["Alternatives"]).find("~") != -1:
                                        alters = str(r["Alternatives"]).split("~")
                                        for alter in alters:
                                            resources = [rs for rn,rs in self.Resources.items() if rn.find(alter) != -1]
                                            if len(resources) > 0:
                                                myres.getAlternatives().append(resources[0])
                                            else:
                                                self.getVisualManager().getDiagInfo().value += "XXX alter not found >>> "+str(alter)+"\n" 
                                    else:
                                        resources = [rs for rn,rs in self.Resources.items() if r["Alternatives"] in rn]
                                        self.getVisualManager().getDiagInfo().value += "resurces>>> "+str(len(resources))+"\n" 
                                        if len(resources) > 0:
                                            myres.getAlternatives().append(resources[0])
                                        else:
                                            self.getVisualManager().getDiagInfo().value += "XhhhhhXX alter not found >>> "+str(r["Alternatives"])+"\n" 
                                self.getVisualManager().getDiagInfo().value += "Resource "+str(r['Name'])+" has "+str(len(myres.getAlternatives()))+" alternatives "+"\n" 

                                 
                                
                            self.getVisualManager().RefreshViews()

                            savefile = False
                            
                            if savefile: 
                                usecase =  self.getVisualManager().getCasesDrop().value
        
                                # Save Products.
                                products_df = pd.DataFrame(columns= ["ProductID","ProductNumber","Name","Created"])
                                precedences_df = pd.DataFrame(columns= ["PredecessorID","SuccessorID","Multiplier"])
                                prodrops_df = pd.DataFrame(columns= ["ProductID","OperationID","OperationIndex"])
                                operations_df = pd.DataFrame(columns= ["OperationID","Name","ProcessTime"])
                                opsres_df = pd.DataFrame(columns= ["OperationID","ResourceID"])
                                resources_df = pd.DataFrame(columns= ["ResourceID","ResourceType","Name","DailyCapacity"])
                                orders_df = pd.DataFrame(columns= ["OrderID","ProductID","Name","Quantity","Deadline"])
                            
                                    
                                for name,myprod in self.Products.items():
                                    products_df.loc[len(products_df)] = {"ProductID":myprod.getID(), "ProductNumber":myprod.getPN(),"Name":myprod.getName(),"Created":myprod.getCreated()}
                             
                                    for predecessor,multiplier in myprod.getMPredecessors().items():
                                        precedences_df.loc[len(precedences_df)] = {"PredecessorID":predecessor.getID(),"SuccessorID":myprod.getID(),"Multiplier":multiplier}
                            
                                    for opr in myprod.getOperations():
                                        prodrops_df.loc[len(prodrops_df)] = {"ProductID":myprod.getID(),"OperationID":opr.getID(),"OperationIndex":opr.getOperationIndex()}
                                            
                            
                            
                                for opname,opr in self.Operations.items():
                                    operations_df.loc[len(operations_df)]= {"OperationID":opr.getID(),"Name":opr.getName(),"ProcessTime":opr.getProcessTime()}
                                        
                                       
                                   
                                for ordname,ordr in self.CustomerOrders.items():
                                    orders_df.loc[len(orders_df)]={"OrderID":ordr.getID(),"ProductID":ordr.getProduct().getID(),"Name":ordr.getName(),"Quantity":ordr.getQuantity(),"Deadline":ordr.getDeadLine()}
                            
                                
                            
                            
                                folder = 'UseCases'; casename = usecase
                                path = folder+"\\"+casename
                                isExist = os.path.exists(path)
                            
                                if not isExist:
                                    os.makedirs(path)
                            
                                timestr = time.strftime("%Y%m%d-%H%M%S")
                                   
                                    
                                filename = 'Products_'+timestr+'.csv'; path = folder+"\\"+casename+"\\"+filename;  fullpath = os.path.join(Path.cwd(), path)
                                self.getVisualManager().getCaseInfo().value += ">>> products save folder.."+str(path)+"\n" 
                                products_df.to_csv(path, index=False)
                                filename = 'Precedences_'+timestr+'.csv';path = folder+"\\"+casename+"\\"+filename; fullpath = os.path.join(Path.cwd(), path)
                                precedences_df.to_csv(fullpath, index=False)
                                filename = 'ProductsOperations_'+timestr+'.csv'; path = folder+"\\"+casename+"\\"+filename; fullpath = os.path.join(Path.cwd(), path)
                                prodrops_df.to_csv(fullpath, index=False)
                                filename = 'Operations_'+timestr+'.csv'; path = folder+"\\"+casename+"\\"+filename; fullpath = os.path.join(Path.cwd(), path)
                                operations_df.to_csv(fullpath, index=False)
                                filename = 'CustomerOrders_'+timestr+'.csv'; path = folder+"\\"+casename+"\\"+filename;fullpath = os.path.join(Path.cwd(), path)
                                orders_df.to_csv(fullpath, index=False)
           

                                

        #input_file = list(self.getVisualManager().getNewCustOrdrs_btn().value.values())[0]
        #content = input_file['content']
        #content = io.StringIO(content.decode('utf-8'))
        #df = pd.read_csv(content)

      
            

        #self.getVisualManager().getCaseInfo().value += ">>> File read, size: ..."+str(len(df))+" \n"
        return
        
    def on_submit_func(self,sender):    

        dtsetnames = [] 
        self.setMyFolder(self.getVisualManager().getFolderNameTxt().value)
          
        rel_path = self.getVisualManager().getFolderNameTxt().value 
        abs_file_path = os.path.join(Path.cwd(),rel_path)

        self.getVisualManager().getCaseInfo().value += "->"+abs_file_path+"\n"                            
        
        for root, dirs, files in os.walk(abs_file_path):
            for mydir in dirs:
                if (mydir.find("_checkpoints") > -1) or (mydir.find("input_files") > -1) :
                    continue
                dtsetnames.append(mydir)
    
    
        self.getVisualManager().getCasesDrop().options = [dst for dst in dtsetnames]
        if len(dtsetnames) > 0:
            self.getVisualManager().getCasesDrop().value = dtsetnames[0]
        return


            

   
