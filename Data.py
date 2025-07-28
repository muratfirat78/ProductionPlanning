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
        self.VisualManager = None
        self.colabpath = '/content/ProductionPlanning'
        self.onlineversion = False       
        
        return

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
        
        for root, dirs, files in os.walk(abs_file_path):
            for file in files:
                self.getVisualManager().getCaseInfo().value += ">>> file."+file+"\n" 
                
                if file == "Products.csv": 
                    prod_df = pd.read_csv(abs_file_path+'/'+file)
                    for i,r in prod_df.iterrows():
                        newprod = Product(r["ProductID"],r["Name"],r["ProductNumber"],r["StockLevel"])
                        newprod.setPrescribedBatchsize(r["PrescribedBatchsize"])
                        newprod.setChosenBatchsize(r["ChosenBatchsize"])
                        self.Products[r["Name"]]= newprod
                    self.getVisualManager().getCaseInfo().value += "Products created: "+str(len(self.getProducts()))+"\n"            
                   
                if file == "Operations.csv": 
                    opr_df = pd.read_csv(abs_file_path+'/'+file)
                    for i,r in opr_df.iterrows():
                        newopr = Operation(r["OperationID"],r["Name"],r["ProcessTime"])
                        self.Operations[r["Name"]]= newopr
                    self.getVisualManager().getCaseInfo().value += "Operations created: "+str(len(self.getOperations()))+"\n"            
       
                    
                if file == "Resources.csv": 
                    res_df = pd.read_csv(abs_file_path+'/'+file)
                    for i,r in res_df.iterrows():  #(self,myid,mytype,myname,mydaycp)
                        newres = Resource(r["ResourceID"],r["ResourceType"],r["Name"],r["DailyCapacity"])
                        if r["Automated"] is not None:
                            newres.setAutomated(r["Automated"])
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

            #self.getVisualManager().getCaseInfo().value += "opr: "+str(opr.getName())+">  res: "+str(res.getName())+"\n" 
            
            opr.getRequiredResources().append(res)
    
        
                   
     
    
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


            

   
