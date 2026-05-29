from Simulator import *
from datetime import timedelta,date
from productionobjects import *
from productionalgs import *
from productionChecker import *
from datetime import timedelta,date,datetime
import numpy as np

class ProductionDataManager(DataManager): 
    def __init__(self,sim,workmgr):
        super().__init__(sim,workmgr) 
        self.res_process_df = None
        self.demand_process_df = None

    def getRes_process_df(self):
        return self.res_process_df


    def getDemand_process_df(self):
        return self.demand_process_df

###########################################################################################
    
    def ReadResources(self):
     
        rel_path = '/'+self.getOperationsManager().getUseCase()
        abs_file_path = os.path.dirname(os.path.realpath(__file__))+rel_path

        
        
        self.getOperationsManager().getSimulator().saveLog(abs_file_path)

        latestfiledate = None
        filename = None

        for root, dirs, files in os.walk(abs_file_path):
            for file in files: 
                self.getOperationsManager().getSimulator().saveLog(file)
                if ".csv" in file:                  
                    try: 
                        filedate = datetime.strptime(file[file.find("Resources_")+len("Resources_"):-5],"%Y-%m-%d")
                        if latestfiledate == None:
                            latestfiledate = filedate
                            filename = file
                        else:
                            if latestfiledate < filedate:
                                latestfilsedate = filedate
                                filename = file
               
                    except Exception as e:
                        pass

        if latestfiledate != None:
            self.getOperationsManager().getSimulator().saveLog("Latest Date resources file date: "+str(latestfiledate))
            TBRMResources_df = pd.read_csv(abs_file_path+'/'+filename)

            self.getOperationsManager().getSimulator().saveLog(str(TBRMResources_df.info()))
            for i,r in TBRMResources_df.iterrows():
                if r['ResourceType'] == 'Operator':
                    AvlShifts = [1]  
                    try: 
                        AvlShifts = r['AvailableShifts'].split("_")
                        AvlShifts = [int(s) for s in AvlShifts]
                    except Exception as e:
                        self.getOperationsManager().getSimulator().saveLog("Error in reading available shifts of operator "+str(r['Name']))
                    #myname,avshifts,mycap,sim,workmngr
                    optr = Operator(r['Name'],AvlShifts,1,self.getSimulator(),self.getOperationsManager())
                    optr.setLocation(self.getOperationsManager().getCentralInventory())
                    self.getOperationsManager().getResources().append(optr) 
                if r['ResourceType'] == 'Machine': #mycap,sim,workmngr  

                    mcode = r['Name'][r['Name'].find("(")+1:]
                    mcode = mcode[:mcode.find(")")]

                    #print("machine code",mcode)

                    OperatingShifts = [1]  
                    try: 
                        OperatingShifts = r['AvailableShifts'].split("_")
                        OperatingShifts = [int(s) for s in OperatingShifts]
                    except Exception as e:
                        self.getOperationsManager().getSimulator().saveLog("Error in reading operating shifts of machine "+str(r['Name']))

                    Alternatives = []
                    if not pd.isna(r['Alternatives']): 
                        try: 
                            Alternatives = r['Alternatives'].split("~")
                        except Exception as e:
                            self.getOperationsManager().getSimulator().saveLog("Error in reading alternatives of machine "+str(r['Name'])+":"+str(pd.isna(r['Alternatives'])))

                    #myname,machcode,OprtingShifts,processtype,automated,mycap,Alternatives,OprtingEffort,sim,workmngr
                    if len(Alternatives) > 0:
                        self.getOperationsManager().getSimulator().saveLog(str(Alternatives))
                    mach = Machine(mcode,r['Name'],OperatingShifts,r['ProcessType'],r['Automated'],50000,Alternatives,int(r['SetupTime']),float(r['OperatingEffort']),self.getSimulator(),self.getOperationsManager())
                
                    mach.setLocation(mach)
                    self.getOperationsManager().getResources().append(mach)
                    
            
            self.getOperationsManager().getSimulator().saveLog("No resources: "+str(len(self.getOperationsManager().getResources())))      
           
        return
        
#####################################################################################################################################
    def ReadDemandFile(self):
        rel_path = '/'+self.getOperationsManager().getUseCase()
        abs_file_path = os.path.dirname(os.path.realpath(__file__))+rel_path
        
        self.getOperationsManager().getSimulator().saveLog(abs_file_path)

  
        latestfiledate = None
        filename = None

        for root, dirs, files in os.walk(abs_file_path):
            for file in files: 
                self.getOperationsManager().getSimulator().saveLog(file)
                if ".xlsx" in file:                  
                    try: 
                        #print("Length: ","Production Orders_",len("Production Orders_"))
                        filedate = datetime.strptime(file[file.find("Production Orders_")+18:-5],"%Y-%m-%d")
                        if latestfiledate == None:
                            latestfiledate = filedate
                            filename = file
                        else:
                            if latestfiledate < filedate:
                                latestfiledate = filedate
                                filename = file
               
                    except Exception as e:
                        pass

        if latestfiledate != None:
           
            self.getOperationsManager().getSimulator().saveLog("Latest Date input file date: "+str(latestfiledate))
            TBRM_df = pd.read_excel(abs_file_path+'/'+filename)
            
            TBRM_df["Deadline"] = TBRM_df["Deadline"].fillna(TBRM_df["Deadline"].max()+timedelta(days=7))
            TBRM_df["Components/Product"] = TBRM_df["Components/Product"].fillna("UnknownRawMaterial")
            TBRM_df["Components/Product/ID"] = TBRM_df["Components/Product/ID"].fillna("UnknownRawMaterialID")
            TBRM_df["Components/Quantity To Consume"] = TBRM_df["Components/Quantity To Consume"].fillna("UnknownRawMaterialQ")

            try: 
                lastdemandid = None
                for i,r in TBRM_df.iterrows():
                    if not pd.isna(r["ID"]):
                        lastdemandid = r["ID"]
                    else:
                        TBRM_df.iloc[i, TBRM_df.columns.get_loc('ID')] = lastdemandid
            except Exception as e:
                self.getOperationsManager().getSimulator().saveLog("ERROR: In filling order id "+str(e))
                

            machines = [r for r in self.getOperationsManager().getResources() if isinstance(r,Machine)] 
            
            MyOrders_df = TBRM_df.groupby(['ID'], dropna=True)[['Work Orders/Work Center','Work Orders/Work Center/ID','Work Orders/Operation','Work Orders/Expected Duration','Work Orders/Start','Work Orders/End','Work Orders/Status','Product/ID','Product','Deadline','Components/Product','Components/Product/ID','Components/Quantity To Consume','Quantity To Produce']].agg(lambda x:list(x)).reset_index()

             
            for i,r in MyOrders_df.iterrows():

                prodorder = None
                try:
                    myproduct = self.defineProduct(r['Product'],r['Product/ID'])
                    myraw = self.defineProduct(r['Components/Product'],r['Components/Product/ID'])
      
                    myproduct.getPredecessors()[myraw] = r['Components/Quantity To Consume'][0]
                    myraw.getSuccessors()[myproduct] = r['Components/Quantity To Consume'][0]
        
                        
                    prodorder = ProductionOrder(r['Deadline'][0],r['ID'],myproduct,int(r['Quantity To Produce'][0])) #ddline,myid,demtype,quantity
                    self.getOperationsManager().getProductionOrders()[r['ID']] = prodorder
                    
                except Exception as e:
                    self.getOperationsManager().getSimulator().saveLog("ERROR: In reading creating product, raw, and order"+str(e))

                try: 

                    oprsequence = []
                    oprid = 0
                    
                    for opr in r['Work Orders/Work Center']:

                        if pd.isna(opr):
                            oprid+=1
                            continue
                        
                        myopr = Operation(prodorder,(opr if not pd.isna(opr) else "Unknown"),self.getOperationsManager().giveProcessID(),r['Work Orders/Expected Duration'][oprid],None) 
                        oprmachs = [m for m in machines if m.getMachineCode() in opr]
    
                        if len(oprmachs) > 0:
                            if oprmachs[0].getID() != r['Work Orders/Work Center/ID'][oprid]:
                                oprmachs[0].setID(r['Work Orders/Work Center/ID'][oprid]) # set precise ID of the resource..
                            myopr.getAlternativeResources().append(oprmachs[0])
                            for mach_alternative in oprmachs[0].getAlternatives():
                                altmachs = [m for m in machines if m.getMachineCode() == mach_alternative]
                                if len(altmachs) > 0: 
                                    myopr.getAlternativeResources().append(altmachs[0])
                        else:
                            self.getOperationsManager().getSimulator().saveLog("REPORT: Data Issue, Operation"+myopr.getName()+" has no machine, hence cancelled!")
                            self.getOperationsManager().getSimulator().saveLog("REPORT: All machines: "+str([m.getMachineCode() for m in machines]))
                            myopr.setName(myopr.getName()+"_ISSUE!")
                            myopr.setCancelled()
                           
                        

                        if pd.isna(opr) or r['Work Orders/Status'][oprid] == "Cancelled": 
                            myopr.setStart(datetime(2000, 1, 1))
                            myopr.setCompletion(datetime(2000, 1, 1))
    
                        if r['Work Orders/Status'][oprid] == "Cancelled": 
                            myopr.setCancelled()
                   
                        if r['Work Orders/Status'][oprid] in ["Finished","Completed"]:
                            myopr.setStart(r['Work Orders/Start'][oprid])
                            myopr.setCompletion(r['Work Orders/End'][oprid])
                            myopr.setFinished()

                        if pd.isna(opr) or r['Work Orders/Status'][oprid] in ["Finished","Completed","Cancelled"]:
                            myopr.setExecutionData(None,self.getOperationsManager().getSimulator())
    
                        oprsequence.append(myopr)        
                        oprid+=1
       
                    self.getOperationsManager().getProductionOrders()[r['ID']].getFinalProduct().getOperationSequences()[r['ID']] = oprsequence

                except Exception as e:
                    self.getOperationsManager().getSimulator().saveLog("ERROR: In creating operations"+str(e))

                
            self.getOperationsManager().getSimulator().saveLog("Size of input file: "+str(len(TBRM_df)))
  
        return
########################################################################################################################################
    def defineProduct(self,dataprod,dataid):

        prodname = dataprod[0]
        prodpn = prodname
        
        if (prodname.find("[") > -1) and (prodname.find("]") > -1):
            prodpn = prodname[prodname.find("["):]
            prodpn = prodpn[:prodpn.find("]")+1]
        myproduct = None
        productid = dataid[0]
                        
        if not productid in self.getOperationsManager().getProducts():
            myproduct= Product(prodpn,str(productid),prodname)
            self.getOperationsManager().getProducts()[myproduct.getID()]= myproduct
        else:
            myproduct = self.getOperationsManager().getProducts()[str(productid)]

        return myproduct
#########################################################################################################################################
    def setResultDFs(self):

        process_df = pd.read_csv("ProcessData.csv")

        self.res_process_df = process_df.groupby(["ResourceID",'Resource','Start','Completion'])[['ItemID','Demand','Product']].agg(lambda x:list(x)).reset_index()
        self.demand_process_df = process_df.groupby(["Demand","Product","OperationName",'Start','Completion'])[['ItemID']].agg(lambda x:list(x)).reset_index()

        return

    def WriteLog(self):

        log_df= pd.DataFrame(columns=["Time","Info"])

        for time,infolist in self.getOperationsManager().getSimulator().getMyLog().items():
            for info in infolist:
                infodata = {"Time":time,"Info":info} 
                log_df.loc[len(log_df)]= infodata
        
        log_df.to_csv("LogData.csv",index = False)

        return 


        #Eself.getSimulator().getController().getVisualManager().self.getFurtherText().options = [r for r in self.res_process_df["ResourceID"].unique()]
        
        #for res in demand_process_df["ResourceID"].unique():
            
        #    sub_df = demand_process_df[demand_process_df["ResourceID"] == res]
        #    sub_df['Start'] = pd.to_datetime(sub_df['Start'])
        #    sub_df = sub_df.sort_values(by ="Start")
            
        #    display(sub_df.head(25))

        
