from simulator import *
from datetime import timedelta,date
from productionobjects import *
from productionalgs import *

from datetime import timedelta,date,datetime
import numpy as np
from os import walk

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

        self.getOperationsManager().getSimulator().saveLog("REPORT: "+str(os.path.dirname(os.path.realpath(__file__))))

        self.getOperationsManager().getSimulator().saveLog("REPORT: "+str(self.getOperationsManager().getSimulator().getController().getUseCase()))

        usecase = self.getOperationsManager().getSimulator().getController().getUseCase()
        simulator = self.getOperationsManager().getSimulator() 
        
        abs_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
            usecase
        )

        source_directory = '/content/'

        latestfiledate = None
        filename = None

        if not self.getOperationsManager().getSimulator().getController().isOnline(): 

            self.getOperationsManager().getSimulator().saveLog(abs_file_path)
    
            
    
            for root, dirs, files in os.walk(abs_file_path):
                for file in files: 
                    self.getOperationsManager().getSimulator().saveLog(file)
                    if ".csv" in file:                  
                        try: 
                            if file.find("Resources_") > -1:
                                datestring = file[file.find("Resources_")+len("Resources_"):-4]
                                filedate = datetime.strptime(datestring,"%Y-%m-%d")
                                if latestfiledate == None:
                                    latestfiledate = filedate
                                    filename = file
                                else:
                                    if latestfiledate < filedate:
                                        latestfilsedate = filedate
                                        filename = file
                   
                        except Exception as e:
                            self.getOperationsManager().getSimulator().saveLog("ERROR: in reading file : "+str(e)+", file: "+str(file))

        else:
            for file in os.listdir(source_directory):
                if ".csv" in file:  
                    try: 
                        if file.find("Resources_") > -1:
                            datestring = file[file.find("Resources_")+len("Resources_"):-4]
                            filedate = datetime.strptime(datestring,"%Y-%m-%d")
                            if latestfiledate == None:
                                latestfiledate = filedate
                                filename = file
                            else:
                                if latestfiledate < filedate:
                                    latestfilsedate = filedate
                                    filename = file
                    except Exception as e:
                            self.getOperationsManager().getSimulator().saveLog("ERROR: in online reading file : "+str(e)+", file: "+str(file))

    
        if latestfiledate != None:
            if not self.getOperationsManager().getSimulator().getController().isOnline(): 
                Resources_df = pd.read_csv(abs_file_path+'/'+filename)
            else:
                print("filename: "+filename)
                Resources_df = pd.read_csv(source_directory+'/'+filename)
           

            #self.getOperationsManager().getSimulator().saveLog(str(Resources_df.info()))
            for i,r in Resources_df.iterrows():
                if r['ResourceType'] == 'Operator':
                    AvlShifts = [1]  
                    try: 
                        AvlShifts = r['AvailableShifts'].split("_")
                        AvlShifts = [int(s) for s in AvlShifts]
                    except Exception as e:
                        self.getOperationsManager().getSimulator().saveLog("Error in reading available shifts of operator "+str(r['Name']))
                    #myname,avshifts,mycap,sim,workmngr
                    optr = Operator(r['Name'],AvlShifts,1,self.getSimulator(),self.getOperationsManager())
                    optr.setLocation(self.getOperationsManager().getCentralInventory().getLocation())
                    optr.setProcessType(r['ProcessType'])
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
                    
                    machloc = Location(r['Name']+"_Location",len(self.getOperationsManager().getLayout().getLocations()))
                    self.getOperationsManager().getLayout().getLocations().append(machloc)
                    NoProcessors = 1000 if r['Name'] == "OUT - Outsourced activity_(OUT - Outsourced)" else 1
            
                    mach = Machine(mcode,r['ID'],NoProcessors,machloc,r['Name'],OperatingShifts,r['ProcessType'],r['Automated'],50000,Alternatives,int(r['SetupTime']),float(r['OperatingEffort']),self.getSimulator(),self.getOperationsManager())
                    mach.setProcessType(r['ProcessType'])
                    self.getOperationsManager().getResources().append(mach)

                    #if r['Name'] == "OUT - Outsourced activity_(OUT - Outsourced)":
                    #    self.getOperationsManager().getSimulator().saveLog("REPORT: OUTSource available shifts: : "+str(mach.getAvailableShifts())+", type: "+str(type(mach)))      
                    
            
            self.getOperationsManager().getSimulator().saveLog("REPORT: No resources: "+str(len(self.getOperationsManager().getResources())))      
           
        return
        
#####################################################################################################################################
    def ReadDemandFile(self):

        usecase = self.getOperationsManager().getSimulator().getController().getUseCase()
        
        source_directory = '/content/'

  
        latestfiledate = None
        filename = None

        if not self.getOperationsManager().getSimulator().getController().isOnline(): 
            
            abs_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
            usecase
            )

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
                            self.getOperationsManager().getSimulator().saveLog("ERROR: in local reading resource file : "+str(e)+", file: "+str(file))
                            

        else:
            
            for file in os.listdir(source_directory):
                self.getOperationsManager().getSimulator().saveLog("REPORT: online file: "+str(file))
                if ".xlsx" in file:       
                    try: 
                        if file.find("Production Orders_") > -1:
                            filedate = datetime.strptime(file[file.find("Production Orders_")+18:-5],"%Y-%m-%d")
                            
                            if latestfiledate == None:
                                latestfiledate = filedate
                                filename = file
                            else:
                                if latestfiledate < filedate:
                                    latestfilsedate = filedate
                                    filename = file
                    except Exception as e:
                        self.getOperationsManager().getSimulator().saveLog("ERROR: in online reading resource file : "+str(e)+", file: "+str(file))



            
        if latestfiledate != None:

            demand_df = None

            if not self.getOperationsManager().getSimulator().getController().isOnline(): 
                self.getOperationsManager().getSimulator().saveLog("REPORT: Latest Date local input file date: "+str(latestfiledate))
                demand_df = pd.read_excel(abs_file_path+'/'+filename)
            else:
                self.getOperationsManager().getSimulator().saveLog("REPORT: Latest Date online input file date: "+str(latestfiledate))
                demand_df = pd.read_excel(source_directory+'/'+filename)
           
            
            
            demand_df["Deadline"] = demand_df["Deadline"].fillna(demand_df["Deadline"].max()+timedelta(days=7))
            demand_df["Components/Product"] = demand_df["Components/Product"].fillna("UnknownRawMaterial")
            demand_df["Components/Product/ID"] = demand_df["Components/Product/ID"].fillna("UnknownRawMaterialID")
            demand_df["Components/Quantity To Consume"] = demand_df["Components/Quantity To Consume"].fillna("UnknownRawMaterialQ")

            try: 
                lastdemandid = None
                for i,r in demand_df.iterrows():
                    if not pd.isna(r["ID"]):
                        lastdemandid = r["ID"]
                    else:
                        demand_df.iloc[i, demand_df.columns.get_loc('ID')] = lastdemandid
            except Exception as e:
                self.getOperationsManager().getSimulator().saveLog("ERROR: In filling order id "+str(e))
                

            machines = [r for r in self.getOperationsManager().getResources() if isinstance(r,Machine)] 
            
            MyOrders_df = demand_df.groupby(['ID'], dropna=True)[['Work Orders/Work Center','Work Orders/Work Center/ID','Work Orders/Operation','Work Orders/Expected Duration','Work Orders/Start','Work Orders/End','Work Orders/Status','Product/ID','Product','Deadline','Components/Product','Components/Product/ID','Components/Quantity To Consume','Quantity To Produce','Reference','Component Status']].agg(lambda x:list(x)).reset_index()

            

             
            for i,r in MyOrders_df.iterrows():

                prodorder = None
                try:
                    myproduct = self.defineProduct(r['Product'],r['Product/ID'])
                    myraw = self.defineProduct(r['Components/Product'],r['Components/Product/ID'])
      
                    myproduct.getPredecessors()[myraw] = r['Components/Quantity To Consume'][0]
                    myraw.getSuccessors()[myproduct] = r['Components/Quantity To Consume'][0]
        
                        
                    prodorder = ProductionOrder(r['Deadline'][0],r['ID'],myproduct,int(r['Quantity To Produce'][0])) #ddline,myid,demtype,quantity
                    self.getOperationsManager().getDemands()[r['ID']] = prodorder
                    prodorder.setReference(r['Reference'][0])

                    if str(r['Component Status'][0]) == "Available":
                        prodorder.setReleaseDate(self.getOperationsManager().getSimulator().getStartDay().date())
                    else:
                        if str(r['Component Status'][0]).find("Exp")> -1:
                            explanation = str(r['Component Status'][0])
                            explanation = explanation[explanation.find("Exp")+len("Exp")+1:]
                            try: 
                                release_date = datetime.strptime(explanation,"%d/%m/%Y")
                                prodorder.setReleaseDate(release_date.date())
                               
                            except Exception as e:
                                self.getOperationsManager().getSimulator().saveLog("ERROR: In reading release date"+str(e))

                    if prodorder.getReleaseDate() == None:
                        prodorder.setReleaseDate(self.getOperationsManager().getSimulator().getStartDay().date())

                          
                            
                           
                        
                    
                except Exception as e:
                    self.getOperationsManager().getSimulator().saveLog("ERROR: In reading creating product, raw, and order"+str(e))

                try: 

                    oprsequence = []
                    oprid = 0
                    
                    for opr in r['Work Orders/Work Center']:

                        if pd.isna(opr):
                            oprid+=1
                            continue

                        oprduration = max(r['Work Orders/Expected Duration'][oprid],1)
                        myopr = Operation(prodorder,(opr if not pd.isna(opr) else "Unknown"),self.getOperationsManager().giveProcessID(),oprduration,None,oprid) 

                        oprmachs = [m for m in machines if m.getID() ==  r['Work Orders/Work Center/ID'][oprid] ]
                        myopr.setReferenceName(r['Work Orders/Operation'][oprid])
    
                        if len(oprmachs) > 0:
                            #if oprmachs[0].getID() != r['Work Orders/Work Center/ID'][oprid]:
                            #    oprmachs[0].setID(r['Work Orders/Work Center/ID'][oprid]) # set precise ID of the resource..

                            
                                
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

                        myopr.setStatus("To do")
                        myopr.setOriginalStart(r['Work Orders/Start'][oprid])
                        myopr.setOriginalCompletion(r['Work Orders/End'][oprid])
                        myopr.setOriginalMachine(r['Work Orders/Work Center'][oprid])

                        

                        if pd.isna(opr) or r['Work Orders/Status'][oprid] == "Cancelled": 
                            myopr.setStart(datetime(2000, 1, 1))
                            myopr.setCompletion(datetime(2000, 1, 1))
                            myopr.setStatus("Cancelled")
    
                        if r['Work Orders/Status'][oprid] == "Cancelled": 
                            myopr.setCancelled()
                   
                        if r['Work Orders/Status'][oprid] in ["Finished","Completed"]:
                            myopr.setStart(r['Work Orders/Start'][oprid])
                            myopr.setCompletion(r['Work Orders/End'][oprid])
                            myopr.setFinished()
                            myopr.setStatus("Finished")

                       
    
                        oprsequence.append(myopr)        
                        oprid+=1
       
                    self.getOperationsManager().getDemands()[r['ID']].getFinalProduct().getOperationSequences()[r['ID']] = oprsequence

                except Exception as e:
                    self.getOperationsManager().getSimulator().saveLog("ERROR: In creating operations"+str(e))

                
            self.getOperationsManager().getSimulator().saveLog("REPORT: Size of input file: "+str(len(demand_df)))
  
        return latestfiledate
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

        process_df = pd.read_csv(os.path.join("..", "data", "simulation", "ProcessData.csv"))

        self.res_process_df = process_df.groupby(["ResourceID",'Resource','Start','Completion'])[['ItemID','Demand','Product']].agg(lambda x:list(x)).reset_index()
        self.demand_process_df = process_df.groupby(["Demand","Product","OperationName",'Start','Completion'])[['ItemID']].agg(lambda x:list(x)).reset_index()

        return

    def WriteLog(self):

        log_df= pd.DataFrame(columns=["Time","Info"])

        for time,infolist in self.getOperationsManager().getSimulator().getMyLog().items():
            for info in infolist:
                infodata = {"Time":time,"Info":info} 
                log_df.loc[len(log_df)]= infodata
        
        log_df.to_csv("data/logs/LogData.csv",index = False)

        return 

   
#########################################################################################################################
 
    def ReadSimulationEventData(self,schedule):

        inputdate =  schedule.getDataExportDate().date()
        consdate =  schedule.getConstuctionDate().date()
  
        data_df = pd.read_csv(os.path.join("..", "data", "simulation", str(inputdate)+"_EventExecutionData_"+str(consdate)+".csv"))




        return data_df

 

        #Eself.getSimulator().getController().getVisualManager().self.getFurtherText().options = [r for r in self.res_process_df["ResourceID"].unique()]
        
        #for res in demand_process_df["ResourceID"].unique():
            
        #    sub_df = demand_process_df[demand_process_df["ResourceID"] == res]
        #    sub_df['Start'] = pd.to_datetime(sub_df['Start'])
        #    sub_df = sub_df.sort_values(by ="Start")
            
        #    display(sub_df.head(25))

   