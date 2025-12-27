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
from difflib import SequenceMatcher

warnings.filterwarnings("ignore")


class DataManager:
    def __init__(self):        
        # Lists..
        self.Resources = dict()  # key: ResourceName, val: ResourceObject
        self.ResourcesID = dict()  # key: ResourceID, val: ResourceObject
        self.Products = dict() # key: Productname, val: ProductObject
        self.ProductsID = dict() # key: ProductID, val: ProductObject
        self.CustomerOrders  = dict() # key: Ordername, val: OrderObject
        self.CustomerOrdersID  = dict() # key: OrderID, val: OrderObject
        
        self.Operations = dict()  # key: OperationName, val: OperationObjec
        self.OperationsID = dict()  # key: OperationID, val: OperationObjec
        self.MachineGroups = [] 
        self.OperatingTeams = []
        self.VisualManager = None
        self.PlanningManager = None
        self.SimulationManager = None
        self.SchedulingManager = None
        
        self.colabpath = '/content/ProductionPlanning'
        self.onlineversion = False       
        self.UseCase = None
        self.MyFolder = None
        self.ScheduleStartWeek = None
        self.ScheduleEndWeek = None

        self.updatelog = pd.DataFrame(columns=['Info'])
        
        return

    def getUpdateLog(self):
        return self.updatelog

    def getPlanningManager(self):
        return self.PlanningManager

    def setPlanningManager(self,myitm):
        self.PlanningManager = myitm
        return 
    

    def getProductsID(self):
        return self.ProductsID
        
    def getResourcesID(self):
        return self.ResourcesID

    def getScheduleStartWeek(self):
        return self.ScheduleStartWeek

    def setScheduleStartWeek(self,mywk):
        self.ScheduleStartWeek = mywk
        return 
    
    def getScheduleEndWeek(self):
        return self.ScheduleEndWeek

    def setScheduleEndWeek(self,mywk):
        self.ScheduleEndWeek = mywk
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
    def getOperationsID(self):
        return self.OperationsID
    def getResources(self):
        return self.Resources
    def getCustomerOrders(self):
        return self.CustomerOrders

    def setCustomerOrders(self,mydict):
        self.CustomerOrders = mydict
        return


    def getCustomerOrdersID(self):
        return self.CustomerOrdersID

   

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
        self.Resources[name]=Resource(len(self.Resources),mytype,name,[1,2])
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
  
   
    
    def SaveSchedule(self,b):

        self.getVisualManager().getSchedulingTab().getPSchScheRes().value += ">>>  saving schedule....."+"\n" 
    
        myschedule = self.getSchedulingManager().getMyCurrentSchedule() 


        self.getVisualManager().getSchedulingTab().getPSchScheRes().value += ">>>  current schedule....."+str(myschedule)+"\n"  
        
        self.getVisualManager().getSchedulingTab().getPSchScheRes().value += ">>>  saving schedule....."+str(len(myschedule.getResourceSchedules()))+"\n" 
    

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
        alldates = []
        for resname,res_schedule in myschedule.getResourceSchedules().items():
            alldates = [x.getDay().date() for x in res_schedule.keys()]
            if len(alldates)>0:
                break
            
            
        self.getVisualManager().getSchedulingTab().getPSchScheRes().value += ">>> min shift: "+str(alldates)+"\n"     


        timestr = time.strftime("%Y%m%d-%H%M%S")
        filename = self.getUseCase()+"_Period_"+str(min(alldates))+"_"+str(max(alldates))+"-Schedule_"+str(timestr)+".csv"; 
        path = self.getMyFolder()+"\\"+self.getUseCase()+"\\"+filename
        fullpath = os.path.join(Path.cwd(), path)
        schedule_df.to_csv(fullpath, index=False)


        self.getVisualManager().getSchedulingTab().getPSchScheRes().value += ">>> schedule saved....."+"\n" 


        return
        
 

    def getFTECapacity(res,shift):

        #

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
        machalts_df =  pd.DataFrame()

        scheduledate = None
        jobdate = None
        jobprdate = None
        schfile = None
        jobprfile = None
        jobsfile = None
        
        for root, dirs, files in os.walk(abs_file_path):
            
            for file in files: 
                if (file.find("Schedule") != -1):
                    filedate = datetime.strptime(file[file.find("Schedule_")+9:-4],"%Y%m%d-%H%M%S")
          
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
   

                if file == "MachineAlternatives.csv": 
                    machalts_df = pd.read_csv(abs_file_path+'/'+file)
                    
              
                if file == "Products.csv": 
                    prod_df = pd.read_csv(abs_file_path+'/'+file)
                    for i,r in prod_df.iterrows():
                        newprod = Product(str(r["ProductID"]),r["Name"],r["ProductNumber"],0)
                        self.Products[r["Name"]]= newprod
                        self.getProductsID()[r["ProductID"]] = newprod
                    self.getVisualManager().getCaseInfo().value += "Products created: "+str(len(self.getProducts()))+"\n"            
                   
                if file == "Operations.csv": 
                    opr_df = pd.read_csv(abs_file_path+'/'+file)
                    for i,r in opr_df.iterrows():
                        newopr = Operation(r["OperationID"],r["Name"],r["ProcessTime"])
         
                        self.Operations[r["Name"]]= newopr
                        self.getOperationsID()[r["OperationID"]]= newopr
                        
                    self.getVisualManager().getCaseInfo().value += "Operations created: "+str(len(self.getOperations()))+"\n"            
       
                    
                if file == "Resources.csv": 
                    res_df = pd.read_csv(abs_file_path+'/'+file)
                    
                    for i,r in res_df.iterrows():  #(self,myid,mytype,myname,mydaycp)
                        shifts = [1]
                        if r["Shift"] is not None:
                            shifts = [int(s) for s in r["Shift"].replace('_', ' ').split()]
                        
                        newres = Resource(r["ResourceID"],r["ResourceType"],r["Name"],shifts)
                        self.getVisualManager().getCaseInfo().value += ">>>.. "+str(r["ProcessType"])+"\n"
                        newres.setProcessType(r["ProcessType"])
                        if not np.isnan(r["Automated"]):
                            if str(r["Automated"]) == "True":
                                newres.setAutomated() 
                            
                        newres.setOperatingEffort(r["OperatingEffort"])

                        
                        self.Resources[r["Name"]]= newres
                        self.getResourcesID()[r["ResourceID"]] = newres
                      

                    self.getVisualManager().getCaseInfo().value += "Resources created: "+str(len(self.getResources()))+"\n" 
                    
                if file == "CustomerOrders.csv": 
                    orders_df = pd.read_csv(abs_file_path+'/'+file)
                    for i,r in orders_df.iterrows():
                        neworder = CustomerOrder(r["OrderID"],r["Name"],r["ProductID"],r["ProductName"],r["Quantity"],r["Deadline"])
                        neworder.SetComponentAvailable(r["Component"])
                        
                        
                        
                        self.CustomerOrders[r["Name"]] = neworder
                        self.getCustomerOrdersID()[r["OrderID"]] = neworder
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
            if myord.getProductName() in self.Products:
                myord.setProduct(self.Products[myord.getProductName()])

        
          
                            
        self.getVisualManager().getCaseInfo().value += ">>> Precedences.. "+str(len(precmatch_df))+"\n" 
        for i,r in precmatch_df.iterrows():
            predecessor = [myprod  for pname,myprod in self.getProducts().items() if str(myprod.getID()) == str(r["PredecessorID"])] [0]
            successor = [myprod  for pname,myprod in self.getProducts().items() if str(myprod.getID()) == str(r["SuccessorID"])][0]

            predecessor.setSuccessor(successor)
            successor.getPredecessors().append(predecessor)
            successor.getMPredecessors()[predecessor] = r["Multiplier"]
            #self.getVisualManager().getCaseInfo().value += "successor: "+str(successor.getName())+" has "+str(len(successor.getPredecessors()))+"\n" 

        self.getVisualManager().getCaseInfo().value += ">>> Machine alternatvies .. "+str(len(machalts_df))+"\n" 
        for i,r in machalts_df.iterrows():
            res = [myres  for resname,myres in self.getResources().items() if myres.getID() == r["MachineID"]][0]
            alt = [myres  for resname,myres in self.getResources().items() if myres.getID() == r["AlternativeID"]][0]

            res.getAlternatives().append(alt)
            

        self.getVisualManager().getCaseInfo().value += ">>> Product-Operations... "+str(len(prodopmatch_df))+"\n" 
                
        for i,r in prodopmatch_df.iterrows():
            prodlst = [myprod  for pname,myprod in self.getProducts().items() if str(myprod.getID()) == str(r["ProductID"])]

            self.getVisualManager().getCaseInfo().value += ">>> op id"+str(r['OperationID'])+"\n" 
            
            if r["OperationID"] in self.getOperationsID():
                myopr = self.getOperationsID()[r["OperationID"]]

                myopr.getSequenceIndices()[r['OrderID']] = r['OperationIndex']


                if r['OrderID'] in self.getCustomerOrdersID():
                    myorder = self.getCustomerOrdersID()[r['OrderID']]

                    self.getVisualManager().getCaseInfo().value += ">>>> order id"+str(r['OrderID'])+"\n" 
           
    
                    if str(r["ProductID"]) in self.getProductsID():
                        myprod = self.getProductsID()[str(r["ProductID"]) ]

                        self.getVisualManager().getCaseInfo().value += ">>>>> product id"+str(r['ProductID'])+"\n" 

                        
                        if not myorder in myprod.getOperationSequences():
                            myprod.getOperationSequences()[myorder] = []

                        inserted = False

                        self.getVisualManager().getCaseInfo().value += ">>>>> opr index "+str(myopr.getOperationIndex())+"\n" 

                        for opsqid in range(len(myprod.getOperationSequences()[myorder])):
                            if myprod.getOperationSequences()[myorder][opsqid].getSequenceIndices()[r['OrderID']] > r['OperationIndex']:
                                myprod.getOperationSequences()[myorder].insert(opsqid,myopr)
                                inserted = True
                                break

                        if not inserted:
                            myprod.getOperationSequences()[myorder].append(myopr)
                            self.getVisualManager().getCaseInfo().value += ">>>>>> inserted"+"\n" 
    
      

            if len(prodlst) > 0: 
                prod = prodlst[0]
                oprlst = [myopr for opname,myopr in self.getOperations().items() if str(myopr.getID()) == str(r["OperationID"])]
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

        earliest = None
        latest = None

        self.getVisualManager().getCaseInfo().value += ">>>> Schedule file.."+str(schfile)+"\n" 
            
        if schfile != None:

            periodind = schfile.find("Period_")
            self.getVisualManager().getCaseInfo().value += ">>>> Schedule period:"+str(schfile[periodind+7:periodind+17])+"  -  "+str(schfile[periodind+18:periodind+28])+"\n" 

            periodstart = datetime.strptime(schfile[periodind+7:periodind+17],"%Y-%m-%d")

            periodend = datetime.strptime(schfile[periodind+18:periodind+28],"%Y-%m-%d")

            self.getVisualManager().getCaseInfo().value += ">>>> Schedule period:"+str(periodstart)+"  -  "+str(periodend)+"\n" 

            startweek = periodstart.isocalendar()[1]
            endweek = periodend.isocalendar()[1]

            self.getVisualManager().getCaseInfo().value += ">>>> Schedule period weeks:"+str(startweek)+"  -  "+str(endweek)+"\n" 

            self.ScheduleStartWeek = startweek
            self.ScheduleEndWeek = endweek

            self.getSchedulingManager().CreateShifts(periodstart,periodend)
            
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
                mydeadline = None
                try:
                    mydeadline = datetime.strptime(r["Deadline"],"%Y-%m-%d") 
                except: 
                    mydeadline = datetime.now()
                    
                newjob = Job(r["JobID"],"Job_"+str(r["JobID"]),prod,opr,r["Quantity"],mydeadline)   
                alljobs[newjob.getID()]= newjob
                
                ords = [myord  for oname,myord in self.getCustomerOrders().items() if myord.getID() == r["OrderID"]] 
                if len(ords) > 0:
                    ords[0].getMyJobs().append(newjob)
                    newjob.setCustomerOrder(ords[0])
                    

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

        ordstoplan = self.getPlanningManager().GetOrdersToPlan(self.getPlanningManager().GetPlanningStart())

        self.getVisualManager().getPLTBOrdlist().options =[ordr.getName()+": "+ordr.getStatus() for ordr in ordstoplan]

        
        return

    def UpdateData(self,b):
        '''
        This function imports prodction orders including: 
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

                        
                        self.getUpdateLog().drop(self.getUpdateLog().index, inplace=True)

                        
                        self.getVisualManager().getNewCustOrdrs_btn().description = "Import resources"
                        self.getVisualManager().getNewCustOrdrs_btn().accept='.csv'
                      
                        TBRM_df = pd.read_excel(content)
    
                        #self.getVisualManager().getDiagInfo().value += "No data lines to import "+str(len(TBRM_df))+"\n"  
                        self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"No data lines to import "+str(len(TBRM_df))}
                        
                        #self.getVisualManager().getDiagInfo().value += "Nan ID values: "+str(sum([int(pd.isna(x)) for x in TBRM_df["ID"]]))+"\n" 

                        self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"Nan ID values: "+str(sum([int(pd.isna(x)) for x in TBRM_df["ID"]]))}
                        
                        #self.getVisualManager().getDiagInfo().value += "Nan Product values: "+str(sum([int(pd.isna(x)) for x in TBRM_df["Product"]]))+"\n"
                        self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"Nan Product values: "+str(sum([int(pd.isna(x)) for x in TBRM_df["Product"]]))}
                        
                        #self.getVisualManager().getDiagInfo().value += "Nan Operation values: "+str(sum([int(pd.isna(x)) for x in TBRM_df["Work Orders/Work Center"]]))+"\n"  
                        self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"Nan Operation values: "+str(sum([int(pd.isna(x)) for x in TBRM_df["Work Orders/Work Center"]]))}

                        neworders=0;newproducts = 0;newoperations = 0;newresources=0;
                        noorders = 0
                        nrproducts = 1
                        nroprs = 0
                        nrresources = 0

                        oprids = [opr.getID() for opr in self.Operations.values()] 


                        ### INPUT FILE IS READ HERE!!###
                        for i,r in TBRM_df.iterrows():

                            myprod = None
                            #self.getVisualManager().getDiagInfo().value += " line "+str(i)+"\n"  
                            self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":" line "+str(i)}

                            #self.getVisualManager().getDiagInfo().value += " part1  "+str((not pd.isna(r['Product'])))+"\n"

                            self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":" part1  "+str((not pd.isna(r['Product'])))}
                            
                            #self.getVisualManager().getDiagInfo().value += " part2  "+str((not (pd.isna(r['Components/Product']))))+"\n" 

                            self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":" part2  "+str((not (pd.isna(r['Components/Product']))))}
                            
                            if (not pd.isna(r['Product'])) and (not (pd.isna(r['Components/Product']))):
                            
                                
                                noorders+=1
                                myorder = None

                                #self.getVisualManager().getDiagInfo().value += " line "+str(i)+" product "+str(r['Product'])+", raw "+r['Components/Product']+"\n" 

                                self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":" line "+str(i)+" product "+str(r['Product'])+", raw "+r['Components/Product']}
                           
          
                                pnstr = r['Product'][r['Product'].find("[")+1:]
                                namestr = pnstr[pnstr.find("]")+1:]
                                pnstr =  pnstr[:pnstr.find("]")]
    
                                #self.getVisualManager().getDiagInfo().value += "pn... "+str(pnstr)+"\n" 

                                self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"pn... "+str(pnstr)}
                           
    
                                pname =  "["+pnstr+"] "+namestr

                                ###### FINAL PRODUCT #####

                                prodid = str(r['Product/ID'])
                                
                                
                                if not prodid in self.getProductsID():

                                    myprod = Product(prodid,pname,pnstr,0)
                                    myprod.setCreated(datetime.now())
                                    self.Products[pname]= myprod   
                                    self.getProductsID()[prodid] = myprod
                                    nrproducts+=1
                                    newproducts+=1
                                    
                                else:
                                    myprod = self.getProductsID()[prodid]

                            
                                #self.getVisualManager().getDiagInfo().value += "prod handled... "+str(not pd.isna(r['Components/Product']))+"\n" 
                                self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"prod handled... "+str(not pd.isna(r['Components/Product']))}
                                ###### FINAL PRODUCT #####
                                    
    
                                
                                if not pd.isna(r['Components/Product']):
                                    ###### RAW PRODUCT #####
                                    rawpnstr = r['Components/Product'][r['Components/Product'].find("[")+1:]
                                    rawnamestr = rawpnstr[rawpnstr.find("]")+1:]
                                    rawpnstr =  rawpnstr[:rawpnstr.find("]")]

                                    #self.getVisualManager().getDiagInfo().value += "raw 1... "+"\n" 
                                    self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"raw 1... "}
                        
    
                                    myrawprod = None

                                    rawname = "["+rawpnstr+"] "+rawnamestr
                                    rawid = str(r['Components/Product/ID'])
                                    
                                    
                                    if not rawid in self.getProductsID():
                                        myrawprod = Product(rawid,rawname,rawpnstr,0)
                                        myrawprod.setCreated(datetime.now())
                                        nrproducts+=1
                                        
                                        self.Products[rawname]= myrawprod 
                                        self.getProductsID()[rawid] = myrawprod
                                        
                                        newproducts+=1
                                    else:
                                        myrawprod = self.getProductsID()[rawid]
                                    

                                    
    
                                    if not myrawprod in myprod.getPredecessors():
                                        myprod.getPredecessors().append(myrawprod)
                                        #self.getVisualManager().getDiagInfo().value += "raw added to predecesors... "+"\n" 
                                        self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"raw added to predecesors... "}
                                        if int(r['Components/Quantity To Consume']) == 0:
                                            myprod.getMPredecessors()[myrawprod] = 1
                                        else:
                                            myprod.getMPredecessors()[myrawprod] = int(r['Components/Quantity To Consume'])


                                     # check second raw material

                                    nextline = i+1
                                    secondraw = False

                                     

                                    if (pd.isna(TBRM_df.loc[nextline,'Product'])) and (not (pd.isna(TBRM_df.loc[nextline,'Components/Product']))):
                                        #self.getVisualManager().getDiagInfo().value += "second raw product!!... "+"\n"
                                        self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"second raw product!!... "}
                                        raw2pnstr = TBRM_df.loc[nextline,'Components/Product'][TBRM_df.loc[nextline,'Components/Product'].find("[")+1:]
                                        raw2namestr = raw2pnstr[raw2pnstr.find("]")+1:]
                                        raw2pnstr =  raw2pnstr[:raw2pnstr.find("]")]

                                        #self.getVisualManager().getDiagInfo().value += "secraw 1... "+"\n" 
                                        self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"secraw 1... "}
        
                                        myraw2prod = None
                                        secondraw = True
    
                                        raw2name = "["+raw2pnstr+"] "+raw2namestr
                                        raw2id = str(TBRM_df.loc[nextline,'Components/Product/ID'])
                                        
                                        
                                        if not raw2id in self.getProductsID():
                                            myraw2prod = Product(raw2id,raw2name,raw2pnstr,0)
                                            myraw2prod.setCreated(datetime.now())
                                            nrproducts+=1
                                            
                                            self.Products[raw2name]= myraw2prod 
                                            self.getProductsID()[raw2id] = myraw2prod
                                            
                                            newproducts+=1
                                        else:
                                            myraw2prod = self.getProductsID()[raw2id]
                                        
    
                                        #self.getVisualManager().getDiagInfo().value += "secraw 2... "+"\n" 
                                        self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"secraw 2... "}
        
                                        if not myraw2prod in myprod.getPredecessors():
                                            myprod.getPredecessors().append(myraw2prod)
                                            if int(TBRM_df.loc[nextline,'Components/Quantity To Consume']) == 0:
                                                myprod.getMPredecessors()[myraw2prod] = 1
                                            else:
                                                myprod.getMPredecessors()[myraw2prod] = int(TBRM_df.loc[nextline,'Components/Quantity To Consume'])
                                    else:
                                        #self.getVisualManager().getDiagInfo().value += "no second raw product... "+"\n"
                                        self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"no second raw product... "}
                                        
                                        
                                     ###### RAW PRODUCT #####

                                resid = r['Work Orders/Work Center/ID']
                                resname = r['Work Orders/Work Center']

                                #self.getVisualManager().getDiagInfo().value += "resid: "+str(resid)+", resname: "+str(resname)+"\n" 
                                self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"resid: "+str(resid)+", resname: "+str(resname)}
                            
                                operationlist = []
                                # creation of operations: start
                                if (not pd.isna(resid)):
    
                                    prev_op = None
                                    oprind = 0
                                    myopr = None

                                    #self.getVisualManager().getDiagInfo().value += "prod id: "+str(myprod.getID())+"\n"   
                                    self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"prod id: "+str(myprod.getID())}
                                    #self.getVisualManager().getDiagInfo().value += "prodp pn: "+str(myprod.getPN())+"\n"   
                                    self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"prodp pn: "+str(myprod.getPN())}

                                    opid = myprod.getID()+"-_-"+resid
                                    opname = "["+myprod.getPN()+"] "+resname


                                    #self.getVisualManager().getDiagInfo().value += " operation id... "+str(opid)+"\n"   
                                    self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":" operation id... "+str(opid)}

                                    # create the very first operation..

                                    
                                    if not pd.isna(resname):
    
                                        myopr = None

                                        
                                        if not opid in self.getOperationsID():

                                            #self.getVisualManager().getDiagInfo().value += " operation will be created.."+"\n" 
                                            self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":" operation will be created.."}

                                            proctime = TBRM_df.loc[i,'Work Orders/Expected Duration']

                                            if TBRM_df.loc[i,'Work Orders/Work Center'].find("OUT -")== -1:
                                                proctime = float(proctime)/float(r['Quantity To Produce'])
                                                

                                            while nroprs in oprids:
                                                nroprs+=1
                                            
                                            myopr = Operation(opid,opname,proctime)
                                            nroprs+=1
                                            newoperations+=1
                                            newres = None

     
                                            if not resid in self.getResourcesID():

                                                #self.getVisualManager().getDiagInfo().value += " resource not found.."+"\n"   
                                                self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":" resource not found.."}

                                                newres = Resource(resid,"Machine",resname,[1,2])
                                                newresources+=1
                                                nrresources+=1
                                                self.Resources[resname] = newres
                                                self.getResourcesID()[resid] = newres
                                                
                                            else:
                                                newres = self.getResourcesID()[resid]
                                                # check name change: 
                                                if newres.getName() != resname:
                                                       
                                                    #self.getVisualManager().getDiagInfo().value += "**************************"+"\n" 
                                                    self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"**************************"}
                                                    #self.getVisualManager().getDiagInfo().value += "curr_name: "+str(newres.getName())+"\n"
                                                    self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"curr_name: "+str(newres.getName())}
                                                    #self.getVisualManager().getDiagInfo().value += "input name: "+str(resname)+"\n"
                                                    self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"input name: "+str(resname)}
                                                    #self.getVisualManager().getDiagInfo().value += "**************************"+"\n"  
                                                    self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"**************************"}
                                            
                                                    newres.setName(resname)

                                            myopr.getRequiredResources().append(newres)

                                           
    
                                            prev_op = myopr
                                            self.Operations[opname]= myopr
                                            self.getOperationsID()[opid]= myopr
                                            myopr.setProduct(myprod)
                                            myopr.setOperationIndex(oprind)
                                            #myprod.getOperations().append(myopr)

                                            oprind+=1
                                            
                                        else:
                                            myopr = self.getOperationsID()[opid]
                                            prev_op = myopr
                                            
                                    operationlist.append(myopr) 

                                    
                                    #self.getVisualManager().getDiagInfo().value += "first operation passed... "+"\n"   
                                    self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"first operation passed... "}
                                    lineno = i+1+int(secondraw)
                                    operations = [r['Work Orders/Work Center']]
    
                                  
                                    while pd.isna(TBRM_df.loc[lineno,'Product']) and (not pd.isna(TBRM_df.loc[lineno,'Work Orders/Work Center'])):
                                        
                                        #self.getVisualManager().getDiagInfo().value += "oprtn "+str(TBRM_df.loc[lineno,'Work Orders/Work Center'])+"\n" 
                                        self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"oprtn "+str(TBRM_df.loc[lineno,'Work Orders/Work Center'])}


                                        resid = TBRM_df.loc[lineno,'Work Orders/Work Center/ID']
                                        resname = TBRM_df.loc[lineno,'Work Orders/Work Center']

                                        

                                        opname = "["+pnstr+"] "+resname
                                        opid = myprod.getID()+"-_-"+resid
                                        
                                        if not opid in self.getOperationsID():
                                            
                                            proctime = TBRM_df.loc[lineno,'Work Orders/Expected Duration']
                                            while nroprs in oprids:
                                                nroprs+=1

                                            if TBRM_df.loc[lineno,'Work Orders/Work Center'].find("OUT -")== -1:
                                                proctime = float(proctime)/float(TBRM_df.loc[i,'Quantity To Produce'])
                                                
                                            myopr = Operation(opid,opname,proctime)
                                            
                                            nroprs+=1
                                            newoperations+=1
                                            newres = None

                                            
                                            if not resid in self.getResourcesID():

                                                newres = Resource(resid,"Machine",resname,[1,2])
                            
                                                nrresources+=1
                                                newresources+=1
                                                self.Resources[resname] = newres
                                                self.getResourcesID()[resid]= newres
                                                
                                            else:
                                                newres = self.getResourcesID()[resid]
                                                
                                                if newres.getName() != resname:
                                                       
                                                    #self.getVisualManager().getDiagInfo().value += "**************************"+"\n" 
                                                    #self.getVisualManager().getDiagInfo().value += "curr_name: "+str(newres.getName())+"\n"
                                                    #self.getVisualManager().getDiagInfo().value += "input name: "+str(TBRM_df.loc[lineno,'Work Orders/Work Center'])+"\n"
                                                    #self.getVisualManager().getDiagInfo().value += "**************************"+"\n"

                                                    
                                                    self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"**************************"}
                                                    self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"curr_name: "+str(newres.getName())}
                                                    self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"input name: "+str(TBRM_df.loc[lineno,'Work Orders/Work Center'])}
                                                    self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"**************************"}

                                                    
                                                    newres.setName(TBRM_df.loc[lineno,'Work Orders/Work Center'])
                                            
    
                                            myopr.getRequiredResources().append(newres)
                                             
                                            if prev_op!= None:
                                                myopr.setPredecessor(prev_op)
                                            prev_op = myopr
                                            
                                            self.Operations[opname]= myopr
                                            self.getOperationsID()[opid]= myopr
                                            
                                            myopr.setProduct(myprod)
                                            myopr.setOperationIndex(oprind)
                                            oprind+=1
                                            #myprod.getOperations().append(myopr)
                                            
                                        else:
                                            
                                            myopr = self.getOperationsID()[opid]

                                        operationlist.append(myopr) 
    
                                       
                                        operations.append(TBRM_df.loc[lineno,'Work Orders/Work Center'])
                                        lineno+=1
                                        if lineno >= len(TBRM_df):
                                            break
                                            
                                   
                                    #self.getVisualManager().getDiagInfo().value += "No operations "+str(len(operations))+"\n" 
                                    self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"No operations "+str(len(operations))}
                                # creation of operations: end

                
                               
                                myorder = None

                                ordid = str(r['ID'])
                                ordname = str(myprod.getName())+"_"+str(r['Quantity To Produce'])+"["+str(ordid[len(ordid)-4:])+"]"
                                #self.getVisualManager().getDiagInfo().value += "ordname..."+str(ordname)+"\n" 
                                #self.getVisualManager().getDiagInfo().value += "line "+str(i)+"\n"  
                                #self.getVisualManager().getDiagInfo().value += "ordid.."+str(ordid)+"\n"
                                self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"ordname..."+str(ordname)}
                                self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"line "+str(i)}
                                self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"ordid.."+str(ordid)}

                                neworder = False
                                
                                if not ordid in self.getCustomerOrdersID():
                                    myDeadLine = datetime.strptime("2025-12-31 00:00:00","%Y-%m-%d %H:%M:%S")
                                    #self.getVisualManager().getDiagInfo().value += "deadline null?..."+str(pd.isnull(r['Deadline']))+"\n" 
                                    self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"deadline null?..."+str(pd.isnull(r['Deadline']))}
                                    if not pd.isnull(r['Deadline']) :
                                        #self.getVisualManager().getDiagInfo().value += "deadline..."+str(r['Deadline'])+"\n" 
                                        self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"deadline..."+str(r['Deadline'])}
                                        myDeadLine = datetime.strptime(str(r['Deadline']),"%Y-%m-%d %H:%M:%S") 
                                        #self.getVisualManager().getDiagInfo().value += "deadline formatted..."+str(myDeadLine)+"\n"
                                        self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"deadline formatted..."+str(myDeadLine)}
                                        
                                        
                                    myorder = CustomerOrder(ordid,ordname,myprod.getID(),myprod.getName(),int(r['Quantity To Produce']),myDeadLine)
                                    myorder.setProduct(myprod)
                                    
                                    neworder = True
                                    neworders+=1

                                    self.getCustomerOrdersID()[ordid] = myorder
                                    self.getCustomerOrders()[ordname] = myorder

                                    #self.getVisualManager().getDiagInfo().value += "order created and add with id "+str(ordid)+", total "+str(len(self.getCustomerOrdersID()))+"\n" 
                                    self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"order created and add with id "+str(ordid)+", total "+str(len(self.getCustomerOrdersID()))}
                                else:
                                    myorder = self.getCustomerOrdersID()[ordid]

                                

                                myDeadLine = datetime.strptime("2025-12-31 00:00:00","%Y-%m-%d %H:%M:%S")
                                #self.getVisualManager().getDiagInfo().value += "deadline null?..."+str(pd.isnull(r['Deadline']))+"\n" 
                                self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"deadline null?..."+str(pd.isnull(r['Deadline']))}
                                if not pd.isnull(r['Deadline']) :
                                    #self.getVisualManager().getDiagInfo().value += "deadline..."+str(r['Deadline'])+"\n" 
                                    self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"deadline..."+str(r['Deadline'])}
                                    myDeadLine = datetime.strptime(str(r['Deadline']),"%Y-%m-%d %H:%M:%S") 
                                    #self.getVisualManager().getDiagInfo().value += "deadline formatted..."+str(myDeadLine)+"\n"
                                    self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"deadline formatted..."+str(myDeadLine)}
                                    
                                    if not neworder:
                                        myorder.updateDeadLine(myDeadLine)
                            
                                myprod.getOperationSequences()[myorder] = operationlist
                                myorder.SetComponentAvailable(r['Component Status'])
                            else:
                                #self.getVisualManager().getDiagInfo().value += " line "+str(i)+""+"\n" 
                                self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":" line "+str(i)+""}
                                if (not pd.isna(r['Product'])) and (not pd.isna(r['Product/ID'])):
                                    
                                    pnstr = r['Product'][r['Product'].find("[")+1:]
                                    namestr = pnstr[pnstr.find("]")+1:]
                                    pnstr =  pnstr[:pnstr.find("]")]
        
                                    #self.getVisualManager().getDiagInfo().value += "no raw- pn... "+str(pnstr)+"\n" 
                                    self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"no raw- pn... "+str(pnstr)}
        
                                    pname =  "["+pnstr+"] "+namestr
    
                                    ###### FINAL PRODUCT #####
    
                                    prodid = str(r['Product/ID'])
                                    
                                    
                                    if not prodid in self.getProductsID():
    
                                        myprod = Product(prodid,pname,pnstr,0)
                                        myprod.setCreated(datetime.now())
                                        self.Products[pname]= myprod   
                                        self.getProductsID()[prodid] = myprod
                                        nrproducts+=1
                                        newproducts+=1
                                        
                                    else:
                                        myprod = self.getProductsID()[prodid]

                                    myorder = None

                                    ordid = str(r['ID'])
                                    ordname = str(myprod.getName())+"_"+str(r['Quantity To Produce'])+"["+str(ordid[len(ordid)-4:])+"]"
                                    #self.getVisualManager().getDiagInfo().value += "ordname..."+str(ordname)+"\n" 
                                    #self.getVisualManager().getDiagInfo().value += "line "+str(i)+"\n"  
                                    #self.getVisualManager().getDiagInfo().value += "ordid.."+str(ordid)+"\n" 

                                    self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"ordname..."+str(ordname)}
                                    self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"line "+str(i)}
                                    self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"ordid.."+str(ordid)}
                                    
                                    if not ordid in self.getCustomerOrdersID():
                                        myDeadLine = datetime.strptime("2025-12-31 00:00:00","%Y-%m-%d %H:%M:%S")
                                        #self.getVisualManager().getDiagInfo().value += "deadline null?..."+str(pd.isnull(r['Deadline']))+"\n" 
                                        self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"deadline null?..."+str(pd.isnull(r['Deadline']))}
                                        if not pd.isnull(r['Deadline']) :
                                            #self.getVisualManager().getDiagInfo().value += "deadline..."+str(r['Deadline'])+"\n" 
                                            self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"deadline..."+str(r['Deadline'])}
                                            myDeadLine = datetime.strptime(str(r['Deadline']),"%Y-%m-%d %H:%M:%S") 
                                            #self.getVisualManager().getDiagInfo().value += "deadline formatted..."+str(myDeadLine)+"\n"
                                            self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"deadline formatted..."+str(myDeadLine)}
                                            
                                            
                                        myorder = CustomerOrder(ordid,ordname,myprod.getID(),myprod.getName(),int(r['Quantity To Produce']),myDeadLine)
                                        myorder.setProduct(myprod)
                                        
    
                                        neworders+=1
    
                                        self.getCustomerOrdersID()[ordid] = myorder
                                        self.getCustomerOrders()[ordname] = myorder
    
                                        #self.getVisualManager().getDiagInfo().value += "order created and add with id "+str(ordid)+", total "+str(len(self.getCustomerOrdersID()))+"\n" 
                                        self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"order created and add with id "+str(ordid)+", total "+str(len(self.getCustomerOrdersID()))}
                                    else:
                                        myorder = self.getCustomerOrdersID()[ordid]


                                    if (not pd.isna(r['Component Status'])):
                                        myorder.SetComponentAvailable(r['Component Status'])

                  

                        #self.getVisualManager().getDiagInfo().value += "New orders:  "+str(neworders)+"\n" 
                        #self.getVisualManager().getDiagInfo().value += "New products:  "+str(newproducts)+"\n"                 
                        #self.getVisualManager().getDiagInfo().value += "New operations:  "+str(newoperations)+"\n"   
                        #self.getVisualManager().getDiagInfo().value += "New resources:  "+str(newresources)+"\n"

                        self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"New orders:  "+str(neworders)}
                        self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"New products:  "+str(newproducts)}
                        self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"New operations:  "+str(newoperations)}
                        self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"New resources:  "+str(newresources)}
                        
                            
                        self.getVisualManager().RefreshViews()  

                    else:
                        if self.getVisualManager().getNewCustOrdrs_btn().description == "Import resources":
                            self.getVisualManager().getNewCustOrdrs_btn().layout.visibility = 'hidden'
                            
                            resources_df = pd.read_csv(content)
                            
                            #self.getVisualManager().getDiagInfo().value += "No resources "+str(len(resources_df))+"\n" 
                            
                            for i,r in resources_df.iterrows():
                                #ResourceID,ResourceType,Name,DailyCapacity,Automated,Alternatives,OperatingEffort,AvailableShifts
                                myres = None

                                res_code = r['Name'][:r['Name'].find("_")]
                                res_model = r['Name'][r['Name'].find("_")+1:]

                                #self.getVisualManager().getDiagInfo().value += "Resource "+str(r['Name'])+"\n" 

                                matches = [r for rn,r in self.Resources.items() if (res_code in rn) and (res_model in rn)]

                                #self.getVisualManager().getDiagInfo().value += "res_code"+str(res_code)+", "+str(res_model)+"\n" 
                                self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"res_code"+str(res_code)+", "+str(res_model)}
                              
                                avshifts = []

                                if str(r["AvailableShifts"]).find("_") != -1: 
                                    avshifts = [int(x) for x in str(r["AvailableShifts"]).split("_")]   
                                    #self.getVisualManager().getDiagInfo().value += "Matches"+str(len(matches))+str(avshifts)+"\n" 
                                    self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"Matches"+str(len(matches))+str(avshifts)+", data: "+str(r["AvailableShifts"])}
                                else:
                                    avshifts.append(int(r["AvailableShifts"]))
                                
                                if len(matches) == 0:
                                    
                                    myres = Resource(r["ResourceID"],r["ResourceType"],r["Name"],avshifts)  
                                    self.Resources[r['Name']] = myres

                                else:
                                    myres = matches[0]
                                    
                                    #self.getVisualManager().getDiagInfo().value += " res "+str(myres.getName())+"\n"
                                    self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":" res "+str(myres.getName())}


                                #self.getVisualManager().getDiagInfo().value += "Shifts: "+str(myres.getAvailableShifts())+"\n" 
                                self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"Shifts: "+str(myres.getAvailableShifts())}

                                for x in avshifts:
                                    if not x in myres.getAvailableShifts():
                                        myres.getAvailableShifts().append(x)

                                

                                myres.setProcessType(r["ProcessType"])
                                #self.getVisualManager().getDiagInfo().value += "Processtype: "+str(r["ProcessType"])+"\n" 

                                #self.getVisualManager().getDiagInfo().value += "Automated: "+str(r["Automated"])+"\n" 
                                if not np.isnan(r["Automated"]):
                                    if str(r["Automated"]) == "True":
                                        myres.setAutomated()
                                #self.getVisualManager().getDiagInfo().value += "Automated: "+str(myres.IsAutomated())+"\n" 
                                myres.setOperatingEffort(float(r["OperatingEffort"]))

                           #self.getVisualManager().getDiagInfo().value += "First pass done.."+"\n" 
                            self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"First pass done.."}

                            
                            for i,r in resources_df.iterrows():
                                myres = None

                                res_code = r['Name'][:r['Name'].find("_")]
                                res_model = r['Name'][r['Name'].find("_")+1:]

                                matches = [r for rn,r in self.Resources.items() if (res_code in rn) and (res_model in rn)]
                                
                                if len(matches) == 0: 
                                    #self.getVisualManager().getDiagInfo().value += "NOT FOUND: Resource "+str(r['Name'])+"\n"
                                    self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"NOT FOUND: Resource "+str(r['Name'])}
                                    
                                else:
                                    myres = matches[0]

                                #self.getVisualManager().getDiagInfo().value += "Alternatives of res "+str(r['Name'])+str(r["Alternatives"])+"\n"
                                self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"Alternatives of res "+str(r['Name'])+str(r["Alternatives"])}

                                if not pd.isnull(r["Alternatives"]):
                                    if str(r["Alternatives"]).find("~") != -1:
                                        alters = str(r["Alternatives"]).split("~")
                                        for alter in alters:
                                            resources = [rs for rn,rs in self.Resources.items() if rn.find(alter) != -1]
                                            if len(resources) > 0:
                                                myres.getAlternatives().append(resources[0]) 
                                    else:
                                        resources = [rs for rn,rs in self.Resources.items() if r["Alternatives"] in rn]
                                        if len(resources) > 0:
                                            myres.getAlternatives().append(resources[0])


                            for rn,rs in self.Resources.items():
                                #$self.getVisualManager().getDiagInfo().value += "++ res... "+rs.getName()+" >>>> "+str(rs.getAvailableShifts())+"\n"
                                self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"++ res... "+rs.getName()+" >>>> "+str(rs.getAvailableShifts())}
                                       

                            #self.getVisualManager().getDiagInfo().value += "Second pass done.."+"\n"
                            self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"Second pass done.."}
                            
                            self.getVisualManager().RefreshViews()

                            #self.getVisualManager().getDiagInfo().value += "refreshing done.."+"\n"
                            self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"refreshing done.."}

                            #self.getVisualManager().getDiagInfo().value += "planning start.."+str(self.getPlanningManager().GetPlanningStart())+"\n"
                            self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"planning start.."+str(self.getPlanningManager().GetPlanningStart())}

                            ordstoplan = self.getPlanningManager().GetOrdersToPlan(self.getPlanningManager().GetPlanningStart())

                            self.getVisualManager().getPLTBOrdlist().options =[ordr.getName()+": "+ordr.getStatus() for ordr in ordstoplan]

                            savefile = True
                            
                            if savefile: 
                                #self.getVisualManager().getDiagInfo().value += "Saving file starts.."+"\n"
                                self.getUpdateLog().loc[len(self.getUpdateLog())] = {"Info":"Saving file starts.."}

                                self.SaveTheInstance()

                            
                            timestr = time.strftime("%Y%m%d-%H%M%S")
                            self.getUpdateLog().to_csv("UpdateLog_"+timestr+".csv")  

        #input_file = list(self.getVisualManager().getNewCustOrdrs_btn().value.values())[0]
        #content = input_file['content']
        #content = io.StringIO(content.decode('utf-8'))
        #df = pd.read_csv(content)

      
            

        #self.getVisualManager().getCaseInfo().value += ">>> File read, size: ..."+str(len(df))+" \n"
        return
        
    def SavePlanning(self):
      
        jobs_df = pd.DataFrame(columns= ["JobID","Quantity","Deadline","OrderID","ProductID", "OperationID"])
        jobpreds_df =  pd.DataFrame(columns= ["JobPredecessorID","JobSuccessorID"])

        self.getVisualManager().getPLTBresult2exp().value+="in saving planning..."+"\n"
        
        for name,order in self.getCustomerOrders().items():

            self.getVisualManager().getPLTBresult2exp().value+=name+" jobs "+str(len(order.getMyJobs()))+"\n"
            for job in order.getMyJobs():
                self.getVisualManager().getPLTBresult2exp().value+=str(job.getID())+", Quantity "+str(job.getQuantity())+", Deadline"+str(job.getDeadLine())+", OrderID "+str(job.getCustomerOrder())+", ProductID "+str(job.getProduct())+", OperationID "+str(job.getOperation())+"\n"
                jobs_df.loc[len(jobs_df)] = {"JobID":job.getID(),"Quantity":job.getQuantity(),"Deadline":job.getDeadLine(),
                                                    "OrderID":job.getCustomerOrder().getID(),"ProductID":job.getProduct().getID(),
                                                    "OperationID":job.getOperation().getID()}
                for pred in job.getPredecessors():
                    jobpreds_df.loc[len(jobpreds_df)] = {"JobPredecessorID":pred.getID(),"JobSuccessorID":job.getID(),}
                    
  
        timestr = time.strftime("%Y%m%d-%H%M%S")
        filename = "Jobs_"+timestr+".csv"; 
   
        
        path = self.getMyFolder()+"\\"+self.getUseCase()+"\\"+filename
        fullpath = os.path.join(Path.cwd(), path)
        jobs_df.to_csv(fullpath, index=False)

        filename = "Jobpreds_"+timestr+".csv"; 
     
        path = self.getMyFolder()+"\\"+self.getUseCase()+"\\"+filename
        fullpath = os.path.join(Path.cwd(), path)
        jobpreds_df.to_csv(fullpath, index=False)

       

        self.getVisualManager().getSchedulingTab().getPSchScheRes().value += ">>> plannig solution saved....."+"\n" 


        return
        
    def SaveTheInstance(self):

        Progress = self.getVisualManager().getDiagInfo()

        # Save Products.
        products_df = pd.DataFrame(columns= ["ProductID","ProductNumber","Name","Created"])
        precedences_df = pd.DataFrame(columns= ["PredecessorID","SuccessorID","Multiplier"])
        prodrops_df = pd.DataFrame(columns= ["OrderID","ProductID","OperationID","OperationIndex"])
        operations_df = pd.DataFrame(columns= ["OperationID","Name","ProcessTime"])
        opsres_df = pd.DataFrame(columns= ["OperationID","ResourceID"])
        resources_df = pd.DataFrame(columns= ["ResourceID","ResourceType","Name","ProcessType","DailyCapacity","Automated","OperatingEffort","Shift"])
        orders_df = pd.DataFrame(columns= ["OrderID","ProductID","ProductName","Name","Quantity","Deadline","Component"])
        machalters_df =  pd.DataFrame(columns= ["MachineID","AlternativeID"])

        Progress.value+= ">>> save instance.."+"\n" 

        Progress.value+= ">>>resources_df.."+str(len(resources_df))+"\n" 
        
        for name,myprod in self.Products.items():
            products_df.loc[len(products_df)] = {"ProductID":myprod.getID(), "ProductNumber":myprod.getPN(),"Name":myprod.getName(),"Created":myprod.getCreated()}

            
            for pred in myprod.getPredecessors():
                precedences_df.loc[len(precedences_df)] = {"PredecessorID":pred.getID(),"SuccessorID":myprod.getID(),"Multiplier":1}

            for order,opsseq in myprod.getOperationSequences().items():
                for oprid in range(len(opsseq)):
                    prodrops_df.loc[len(prodrops_df)] = {"OrderID":order.getID(),"ProductID":myprod.getID(),"OperationID":opsseq[oprid].getID(),"OperationIndex":oprid}
               
  
            #oprind = 0
            #for opr in myprod.getOperations():
                #Progress.value+= ">>> prod-opr..Opr"+str(opr.getID())+"->Prod"+str(myprod.getID())+"\n" 
            #    prodrops_df.loc[len(prodrops_df)] = {"ProductID":myprod.getID(),"OperationID":opr.getID(),"OperationIndex":oprind}
            #    oprind+=1

        Progress.value+= ">>>  products done.."+str(len(products_df))+"\n" 

        Progress.value+= ">>>  oprss"+str(len(self.Operations))+"\n" 

        for opname,opr in self.Operations.items():
            #Progress.value += ">>> opr.."+str(opr.getName())+"\n"
            #Progress.value += ">>> opr id.."+str(opr.getID())+"\n"
            #Progress.value += ">>> opr proc (min).."+str(opr.getProcessTime('min'))+"\n"
            operations_df.loc[len(operations_df)]= {"OperationID":opr.getID(),"Name":opr.getName(),"ProcessTime":opr.getProcessTime('min')}
            
            for res in opr.getRequiredResources():
                opsres_df.loc[len(opsres_df)]= {"OperationID":opr.getID(),"ResourceID":res.getID()}
                

        Progress.value+= ">>> operations done.."+str(len(operations_df))+"\n" 
        Progress.value+= ">>> Resources: "+str(len(self.Resources))+"\n" 

        for resname,res in self.Resources.items():
            Progress.value+= ">>> rrrres.."+str(res.getName())+", alts: "+str(len(res.getAlternatives()))+"\n" 

            Progress.value+= ">>> rrrres.."+str(res.getName())+", shifts: "+str(res.getAvailableShifts())+"\n" 

            resources_df.loc[len(resources_df)] ={"ResourceID":res.getID(),"ResourceType":res.getType(),"Name":res.getName(),"ProcessType":res.getProcessType(),"DailyCapacity":res.getDailyCapacity(),"Automated":res.IsAutomated(),"OperatingEffort":res.getOperatingEffort(),"Shift":'_'.join([str(x) for x in res.getAvailableShifts()])}

            for altres in res.getAlternatives():
                machalters_df.loc[len(machalters_df)] = {"MachineID":res.getID(),"AlternativeID":altres.getID()}

        Progress.value+= ">>> resources done.."+str(len(resources_df))+"\n" 
        
        for ordname,ordr in self.CustomerOrders.items():
            orders_df.loc[len(orders_df)]={"OrderID":ordr.getID(),"ProductID":ordr.getProduct().getID(),"ProductName":ordr.getProduct().getName(),"Name":ordr.getName(),"Quantity":ordr.getQuantity(),"Deadline":ordr.getDeadLine(),"Component":ordr.getComponentAvailable()}

        #Progress.value+=">>> orders done.."+str(len(orders_df))+"\n" 


        folder = 'UseCases'; casename = self.getVisualManager().getCOTBcasename().value
        path = folder+"\\"+casename
        isExist = os.path.exists(path)

        if not isExist:
            os.makedirs(path)

 
        filename = 'Products.csv'; 
        path = self.getMyFolder()+"\\"+self.getUseCase()+"\\"+filename;  
        fullpath = os.path.join(Path.cwd(), path)
        Progress.value+= ">>> products save folder.."+str(path)+"\n" 
        products_df.to_csv(path, index=False)
      
        filename = 'Precedences.csv'; path = self.getMyFolder()+"\\"+self.getUseCase()+"\\"+filename;   fullpath = os.path.join(Path.cwd(), path)
        precedences_df.to_csv(fullpath, index=False)
        filename = 'ProductsOperations.csv'; path = self.getMyFolder()+"\\"+self.getUseCase()+"\\"+filename;   fullpath = os.path.join(Path.cwd(), path)
        prodrops_df.to_csv(fullpath, index=False)
        filename = 'ResourcesOperations.csv'; path = self.getMyFolder()+"\\"+self.getUseCase()+"\\"+filename;  fullpath = os.path.join(Path.cwd(), path)
        opsres_df.to_csv(fullpath, index=False)
        filename = 'Operations.csv'; path = self.getMyFolder()+"\\"+self.getUseCase()+"\\"+filename;   fullpath = os.path.join(Path.cwd(), path)
        operations_df.to_csv(fullpath, index=False)
        filename = 'Resources.csv';  path = self.getMyFolder()+"\\"+self.getUseCase()+"\\"+filename;  fullpath = os.path.join(Path.cwd(), path)
        resources_df.to_csv(fullpath, index=False)
        filename = 'CustomerOrders.csv';  path = self.getMyFolder()+"\\"+self.getUseCase()+"\\"+filename;  fullpath = os.path.join(Path.cwd(), path)
        orders_df.to_csv(fullpath, index=False)
        filename = 'MachineAlternatives.csv';  path = self.getMyFolder()+"\\"+self.getUseCase()+"\\"+filename;   fullpath = os.path.join(Path.cwd(), path)
        machalters_df.to_csv(fullpath, index=False)
        
        return

    def getFTECapacity(self,processtype,shift):

        sumfte = 0
        for resname,res in self.Resources.items():
            if res.getType() == "Operator":
                if res.getProcessType() == processtype:
                    if shift.getNumber() in res.getAvailableShifts():
                        sumfte+=1
    
        return sumfte
        
    def getProcessTypes(self):
        types = []
        for resname,res in self.Resources.items():
            if res.getType() == "Machine":
                if not res.getProcessType() in types:
                    types.append(res.getProcessType())
    
        return types
        
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


            

   
