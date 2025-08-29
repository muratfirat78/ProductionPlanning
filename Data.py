"""
Created on Wed Apr  3 11:46:59 2024

@author: mfirat
"""

##### import ipywidgets as widgets
from IPython.display import clear_output
from IPython import display
from ipywidgets import *
from datetime import timedelta,date
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
        self.colabpath = '/content/ProductionPlanning'
        self.onlineversion = False       
        
        return

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
        
    def CreateShifts(self,psstart,pssend):

        scheduleperiod = pd.date_range(psstart,pssend)
              
        i=1
        prev_dayshift = None 
        scheduletimehour = 1
        
        for curr_date in scheduleperiod:
            
            shift1=Shift(curr_date,3,prev_dayshift)
            shift1.setStartTime(scheduletimehour)  

            shift1.setStartHour(curr_date + timedelta(hours=0))
            shift1.setEndHour(curr_date + timedelta(hours=7)+ timedelta(minutes=59))
          
            scheduletimehour+=8
            shift1.setEndTime(scheduletimehour-1)
            shift2=Shift(curr_date,1,shift1)
            shift2.setStartTime(scheduletimehour)   
            scheduletimehour+=8
            shift2.setEndTime(scheduletimehour-1)

            shift2.setStartHour(curr_date + timedelta(hours=8))
            shift2.setEndHour(curr_date + timedelta(hours=15)+timedelta(minutes=59))

            
            shift3=Shift(curr_date,2,shift2)
            shift3.setStartTime(scheduletimehour)
            scheduletimehour+=8
            shift3.setEndTime(scheduletimehour-1)
            shift3.setStartHour(curr_date + timedelta(hours=16))
            shift3.setEndHour(curr_date + timedelta(hours=23)+ timedelta(minutes=59))
            
            prev_dayshift=shift3

            opno = 0
            for resname, res in self.getResources().items():

                if res.getType() == "Machine":

                    res.getShiftAvailability()[shift1] = res.IsAutomated() 
                   
                    if res.getShiftAvailability()[shift1]:
                        res.getSchedule()[shift1] = []
                        res.getShiftOperatingModes()[shift1] = "Self-Running"

                    res.getShiftAvailability()[shift2] = True
                   
                    res.getSchedule()[shift2] = []
                    res.getShiftOperatingModes()[shift2] = "Operated"
                    
                    res.getShiftAvailability()[shift3] = True
                    
                    res.getSchedule()[shift3] = []
                    res.getShiftOperatingModes()[shift3] = "Operated"
                  

                if res.getType() == "Manual":
                    res.getShiftAvailability()[shift1] = False
                    res.getShiftAvailability()[shift2] = True
                    res.getSchedule()[shift2] = []
                    res.getShiftAvailability()[shift3] = True
                    res.getSchedule()[shift3] = []
                    
                if res.getType() == "Operator":
                    res.getShiftAvailability()[shift1] = False
                    
                    res.getShiftAvailability()[shift2] = True
                    res.getSchedule()[shift2] = []
                    res.getShiftAvailability()[shift3] = True
                    res.getSchedule()[shift3] = []
                
          
                if res.getType() == "Outsourced":
                    res.getShiftAvailability()[shift1] = True
                    res.getSchedule()[shift1] = []
                    res.getShiftAvailability()[shift2] = True
                    res.getSchedule()[shift2] = []
                    res.getShiftAvailability()[shift3] = True
                    res.getSchedule()[shift3] = [] 
                    
            i+=1        

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
        products_df = pd.DataFrame(columns= ["ProductID", "ProductNumber","Name","StockLevel"])
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

    def read_dataset(self,b):  

       
        rel_path = self.getVisualManager().getFolderNameTxt().value+'/'+self.getVisualManager().getCasesDrop().value


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
        schfile = None
        jobprfile = None
        
        for root, dirs, files in os.walk(abs_file_path):
            
            for file in files: 

                if (file.find("ScheduleJobs") != -1) and (file.find("ScheduleJobsPrecs") == -1):
                    filedate = datetime.strptime(file[file.find("_")+1:-4],"%Y%m%d-%H%M%S")
          
                    if scheduledate == None: 
                        scheduledate = filedate
                        schfile = file
                        
                    else:
                        if filedate > scheduledate:
                            scheduledate = filedate
                            schfile = file
                            self.getVisualManager().getCaseInfo().value += "scheduledate..."+str(scheduledate)+"\n"  
                            
            for file in files:
                self.getVisualManager().getCaseInfo().value += ">>> reading file "+file+"... \n" 

                if file.find("ScheduleJobsPrecs") != -1:
                    filedate = datetime.strptime(file[file.find("_")+1:-4],"%Y%m%d-%H%M%S")

                    if filedate == scheduledate:
                        jobprfile = file
                        self.getVisualManager().getCaseInfo().value += "jobprfile .."+str(file)+"\n"         
   

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

        for i,r in oprsresources_df.iterrows():
            opr = [myopr for opname,myopr in self.getOperations().items() if myopr.getID() == r["OperationID"]][0]
            res = [myres  for resname,myres in self.getResources().items() if myres.getID() == r["ResourceID"]][0]

            opr.getRequiredResources().append([res])
            
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
          
                

            #self.getVisualManager().getCaseInfo().value += "opr: "+str(opr.getName())+">  res: "+str(res.getName())+"\n" 
        earliest = None
        latest = None

        self.getVisualManager().getCaseInfo().value += ">>>> Schedule file.."+str(schfile)+"\n" 
            
        if schfile != None:
            schedule_df = pd.read_csv(abs_file_path+'/'+schfile)
            jobprecs_df =   pd.read_csv(abs_file_path+'/'+jobprfile)

            self.getVisualManager().getCaseInfo().value += ">>>> Schedule jobs file.."+str(schfile)+"\n" 
            self.getVisualManager().getCaseInfo().value += ">>>> Schedule job precedences file.."+str(jobprfile)+"\n" 

            alljobs = dict() # key job id, val: job object.

            self.getVisualManager().getCaseInfo().value += ">>>> Schedule file read, no jobs.."+str(len(schedule_df))+"\n" 
            self.getVisualManager().getCaseInfo().value += ">>>> Schedule file read, no job precedences.."+str(len(jobprecs_df))+"\n" 
            jobpreds = []

            for i,r in schedule_df.iterrows():
                if str(r["SchDaySt"]) != 'nan':
                    stdate = datetime.strptime(r["SchDaySt"],'%Y-%m-%d')
                    #self.getVisualManager().getCaseInfo().value += ">>>> SchDaySt.."+str(stdate)+"\n" 
                    if earliest == None:
                        earliest = stdate
                    else:
                        if earliest > stdate:
                            earliest = stdate
                #self.getVisualManager().getCaseInfo().value += ">>>> SchDayCp.."+str(r["SchDayCp"])+"\n" 
                if str(r["SchDayCp"]) != 'nan':
                    cpdate = datetime.strptime(r["SchDayCp"],'%Y-%m-%d')
                    if latest == None:
                        latest = cpdate
                    else:
                        if latest < cpdate:
                            latest = cpdate

            if (earliest!= None) and (latest!= None):
                self.getVisualManager().getCaseInfo().value += ">>>> Schedule earliest - latest .."+str(earliest)+":"+str(latest)+"\n" 
                self.CreateShifts(earliest,latest)

            
            self.getVisualManager().getCaseInfo().value += ">>>> shifts created .."+"\n"     
            insertedshifts = 0
            scheduleshiftsfound = 0
            scheduleds = 0
            for i,r in schedule_df.iterrows():
               
                newjob = Job(r["JobID"],"Job_"+str(r["JobID"]),prod,opr,r["Quantity"],r["Deadline"])              
                opr = [myopr for opname,myopr in self.getOperations().items() if myopr.getID() == r["OperationID"]][0]
              
                res = None

              
                if str(r["ResourceID"]) != 'nan':
                    res = [myres  for resname,myres in self.getResources().items() if myres.getID() == r["ResourceID"]][0]
                    self.getVisualManager().getCaseInfo().value += ">>>> resource.."+str(res)+"\n" 
                    if res == None:
                        self.getVisualManager().getCaseInfo().value += ">>>> Resource of job (id)"+str(r["JobID"])+" not found with id: "+str(r["ResourceID"])+"\n" 
                    else:
                        scheduleds+=1
                        newjob.setScheduledResource(res)                
                     
                    
                prod = [myprod  for pname,myprod in self.getProducts().items() if myprod.getID() == r["ProductID"]] [0]
                #order = [myord  for oname,myord in self.getCustomerOrders().items() if myord.getID() == r["OrderID"]] [0]

                self.getVisualManager().getCaseInfo().value += ">>>> job.."+str(r["JobID"])+"\n"     
        
                alljobs[newjob.getID()]= newjob


                if res!= None:
                    stday =  datetime.strptime(r["SchDaySt"],'%Y-%m-%d')
                    
                    newjob.setScheduledDay(stday)  
                    newjob.setStartTime(r["SchTimeSt"])    
                    newjob.setCompletionTime(r["SchTimeCp"])
                   
                    
                    cpday =  datetime.strptime(r["SchDayCp"],'%Y-%m-%d')

                    lastshift = None
                    for shift,jobs in res.getSchedule().items():
                        if (shift.getDay() >= stday) and (shift.getDay() <= cpday):
                            jobs.append(newjob)
                            insertedshifts+=1

                        if (shift.getDay() == newjob.getScheduledDay()) and (shift.getNumber() == r["SchShiftSt"]):
                            newjob.setScheduledShift(shift)
                            scheduleshiftsfound+=1

                            if lastshift == None: 
                                lastshift = shift
                            else:
                                if shift.shift.getStartHour() >= lastshift.getStartHour():
                                    lastshift = shift

                    if lastshift != None:
                        newjob.setScheduledCompShift(shift)
                        scheduleshiftsfound+=1            


                
                
                #self.getVisualManager().getCaseInfo().value += ">>>> i2.."+str(i)+"\n" 
                #order.getMyJobs().append(newjob)
                #self.getVisualManager().getCaseInfo().value += ">>>> SchDaySt.."+str(r["SchDaySt"])+"\n" 
               
           

            self.getVisualManager().getCaseInfo().value += ">>>> Insertedshifts .."+str(insertedshifts)+"\n"
            self.getVisualManager().getCaseInfo().value += ">>>> Scheduled shifts found .."+str(scheduleshiftsfound)+"/"+str(scheduleds)+"\n"
            
            for jobid,job in alljobs.items():
                job_df = jobprecs_df[jobprecs_df["JobSuccessorID"] == job.getID()]
                jobpreds.append(len(job_df))
                for predid in job_df["JobPredecessorID"]:
                    if predid in alljobs:
                        predjob = alljobs[predid]
                        job.getPredecessors().append(predjob)
                    else: 
                        self.getVisualManager().getCaseInfo().value += ">>>> pred of job "+str(job.getID())+" not in jobs.."+"\n" 
            #self.getVisualManager().getCaseInfo().value += ">>>> job preds of job "+str(jobpreds)+"\n"
                        

                
        


            
            self.getVisualManager().getCaseInfo().value += ">>>> Shifts and schedules created .."+"\n"     
                
                   
     
    
        self.getVisualManager().RefreshViews()

        self.getVisualManager().getUSTBCustomerOders().value = str(len(self.CustomerOrders))
        self.getVisualManager().getUSTBProducts().value = str(len(self.getProducts()))
        self.getVisualManager().getUSTBRawMaterials().value = str(len([prod for prod in self.getProducts().values() if len(prod.getMPredecessors()) == 0]))
        self.getVisualManager().getUSTBRawResources().value = str(len(self.getResources()))
                
        return
        
    def on_submit_func(self,sender):    

        dtsetnames = [] 
          
        rel_path = self.getVisualManager().getFolderNameTxt().value
       
        abs_file_path = os.path.join(Path.cwd(),rel_path)

        self.getVisualManager().getCaseInfo().value += "->"+abs_file_path+"\n"                            
        
        for root, dirs, files in os.walk(abs_file_path):
            for mydir in dirs:
                dtsetnames.append(mydir)
    
    
        self.getVisualManager().getCasesDrop().options = [dst for dst in dtsetnames]
        if len(dtsetnames) > 0:
            self.getVisualManager().getCasesDrop().value = dtsetnames[0]
        return


            

   
