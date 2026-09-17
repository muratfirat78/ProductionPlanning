from simulator import *
from datetime import timedelta,date
from logisticsobjects import *
from logisticsalgs import *
from datetime import timedelta,date,datetime
import numpy as np
from os import walk

class LogisticsDataManager(DataManager): 
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
     
        abs_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
            self.getOperationsManager().getSimulator().getController().getUseCase()
        )


        self.getOperationsManager().getSimulator().saveLog(abs_file_path)

        latestfiledate = None
        filename = None

        for root, dirs, files in os.walk(abs_file_path):
            #self.getOperationsManager().getSimulator().saveLog("REPORT:  files: "+str(files))
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

        if latestfiledate != None:
            Resources_df = pd.read_csv(abs_file_path+'/'+filename)

            self.getOperationsManager().getSimulator().saveLog(str(Resources_df.info()))
            for i,r in Resources_df.iterrows():
            
                if r['ResourceType'] == 'Forklift':
                    # myname,myid,mycap,sim,workmngr
                    forklift = Forklift(r['Name'],r['ID'],1,self.getSimulator(),self.getOperationsManager())
                    self.getOperationsManager().getResources().append(forklift) 

                if r['ResourceType'] == 'PalletJack':
                    # myname,myid,mycap,sim,workmngr
                    palletjack = PalletJack(r['Name'],r['ID'],1,self.getSimulator(),self.getOperationsManager())
                    self.getOperationsManager().getResources().append(palletjack) 
                    
                    
                if r['ResourceType'] == 'Operator':
                    #myname,avshifts,mycap,sim,workmngr
                    AvlShifts = [1]  
                    try: 
                        AvlShifts = r['AvailableShifts'].split("_")
                        AvlShifts = [int(s) for s in AvlShifts]
                    except Exception as e:
                        self.getOperationsManager().getSimulator().saveLog("Error in reading available shifts of operator "+str(r['Name']))
      
                    optr = Operator(r['Name'],AvlShifts,1,self.getSimulator(),self.getOperationsManager())
                    optr.setLocation(self.getOperationsManager().getCentralInventory().getLocation())
                    optr.setProcessType(r['ProcessType'])
                    self.getOperationsManager().getResources().append(optr) 
                    
                if r['ResourceType'] == 'Machine':
                    
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
                            
                    if len(Alternatives) > 0:
                        self.getOperationsManager().getSimulator().saveLog(str(Alternatives))
                    
                    machloc = Location(r['Name']+"_Location",len(self.getOperationsManager().getLayout().getLocations()))
                    self.getOperationsManager().getLayout().getLocations().append(machloc)
                    NoProcessors = 1

                    # machcode,myid,myloc,myname,OprtingShifts,automated,mycap,Setup,sim,workmngr
                    mach = Machine(mcode,r['ID'],machloc,r['Name'],OperatingShifts,r['Automated'],50000,int(r['SetupTime']),self.getSimulator(),self.getOperationsManager())
                    self.getOperationsManager().getResources().append(mach)

                 
            self.getOperationsManager().getSimulator().saveLog("REPORT: No resources: "+str(len(self.getOperationsManager().getResources())))      
           
        return
        
#####################################################################################################################################
    def ReadDemandFile(self):

        self.getOperationsManager().getSimulator().saveLog("REPORT: demand to generate.. ")
        self.generateRandomDemands()
        self.getOperationsManager().getSimulator().saveLog("REPORT: demand generated.. ")

        latestfiledate = None
       
        
        
        abs_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
            self.getOperationsManager().getSimulator().getController().getUseCase()
        )
        
        self.getOperationsManager().getSimulator().saveLog(abs_file_path)

  
        
        filename = None

        check_str = "Demand_"

        for root, dirs, files in os.walk(abs_file_path):
            for file in files: 
                self.getOperationsManager().getSimulator().saveLog(file)
                     
                try: 
                    
                    fileindex = file.index(check_str)
                    if fileindex > -1:
                        fdate = file[fileindex+len(check_str):-4]
                        self.getOperationsManager().getSimulator().saveLog("REPORT: fdate: "+str(fdate))
                       
                        filedate = datetime.strptime(fdate,"%Y-%m-%d")
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
            try: 
                demand_df = pd.read_csv(abs_file_path+'/'+filename)

                batchid = 1; shipmentid = 1
                for shipmentbatch in demand_df["ShipmentBatch"].unique():
                    batch_df = demand_df[demand_df["ShipmentBatch"] == shipmentbatch]

                    myshipmentbatch = ShipmentBatch(batchid)

                    for i,r in batch_df.iterrows():
                        # mytype,myweight,mydestination,myid
                        shipment = Shipment(r['ShipmentType'],r['Weight'],r['Destination'],shipmentid)

                        myshipmentbatch.getShipments().append(shipment)
                        shipmentid+=1

                    self.getOperationsManager().getShipmentBatches().append(myshipmentbatch)

    
                    batchid+=1

                
                self.getOperationsManager().getSimulator().saveLog("REPORT: demand files size: "+str(len(demand_df)))
            except Exception as e: 
                self.getOperationsManager().getSimulator().saveLog("ERROR: In reading demand file "+str(e)+".")
                
        
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
    def ApplyUseCase(self,usecase):

        try: 
            for root, dirs, files in os.walk(os.getcwd()):
                self.getOperationsManager().getSimulator().saveLog("REPORT: files "+str(files))
                     
                for name in files:
                                    
                    if name.find(usecase+"_EventTypes.csv") > -1:
            
                        events_df = pd.read_csv(os.path.join(usecase+"_EventTypes.csv"))

                        for i,r in events_df.iterrows():
                            eventtype = SimEvent(self.getOperationsManager().getSimulator(),r['Name'],r['Type'],r["ResourceType"],r["EquipmentType"],bool(r["Preemptable"]))
                            self.getOperationsManager().getEventTypes()[eventtype.getName()]= eventtype
                            self.getOperationsManager().getSimulator().saveLog("REPORT: eventtype defined: "+str(eventtype.getName()))

                        self.getOperationsManager().getSimulator().saveLog("REPORT: eventtypes "+str(self.getOperationsManager().getEventTypes().keys()))
                        for eventtypename,eventtype in self.getOperationsManager().getEventTypes().items():
                            ev_df = events_df[events_df["Name"] == eventtypename]
                            self.getOperationsManager().getSimulator().saveLog("REPORT: eventtype df "+str(len(ev_df)))
                            for i,r in ev_df.iterrows():
                                if not pd.isna(r['Successor']):
                                    if r['Successor'] in self.getOperationsManager().getEventTypes():
                                        succ_event = self.getOperationsManager().getEventTypes()[r['Successor']]
                                        if not succ_event in eventtype.getSuccessorDict():
                                            eventtype.getSuccessorDict()[succ_event] = "Finish to Start"
                                            self.getOperationsManager().getSimulator().saveLog("REPORT: eventtype "+str(eventtypename)+" has successor  "+r['Successor'])
                                        else:
                                            self.getOperationsManager().getSimulator().saveLog("REPORT: successor  "+r['Successor']+" is not found in successordict...")
                                        
                                    else:
                                        self.getOperationsManager().getSimulator().saveLog("ERROR: successor  "+r['Successor']+" is not found in eventtypes...")
                                        
                                        
      

                        decisions_df = pd.read_csv(os.path.join(usecase+"_Decisions.csv"))
                        self.getOperationsManager().getSimulator().saveLog("REPORT: decisions_df "+str(len(decisions_df)))
                        for eventtypename,eventtype in self.getOperationsManager().getEventTypes().items():
                            event_df = decisions_df[decisions_df["EventType"] == eventtypename]
                            if not (eventtypename in self.getOperationsManager().getAlgorithmSetting()):
                                self.getOperationsManager().getAlgorithmSetting()[eventtypename] = dict()
                                
                            for i,r in event_df.iterrows():

                                self.getOperationsManager().getSimulator().saveLog("REPORT: eventtype "+str(eventtypename)+"  decisions case none? "+str(pd.isna(r['Case'])))
                                if not pd.isna(r['Case']):
                                    if not r['Case'] in eventtype.getDecisionsDict():
                                        eventtype.getDecisionsDict()[r['Case']] = []

                                    self.getOperationsManager().getSimulator().saveLog("REPORT: eventtype "+str(eventtypename)+" case "+str(r['Case'])+" decision "+str(r['DecisionType']))
                                    eventtype.getDecisionsDict()[r['Case']].append(r['DecisionType'])
                                self.getOperationsManager().getSimulator().saveLog("REPORT: decision type "+str(r['DecisionType'])+", alg: "+str(r['DecisionAlgorithm']))
                                self.getOperationsManager().getAlgorithmSetting()[eventtypename][r['DecisionType']]= r['DecisionAlgorithm']
                               
                        precedenceinfo_df = pd.read_csv(os.path.join(usecase+"_PrecedenceInfo.csv"))
                        #self.getOperationsManager().getSimulator().saveLog("REPORT: precedenceinfo_df size "+str(len(precedenceinfo_df)))
                        
                        for eventtypename,eventtype in self.getOperationsManager().getEventTypes().items():
                            event_df = precedenceinfo_df[precedenceinfo_df["Predecessor"] == eventtypename]

                            for i,r in event_df.iterrows():
                                if not r['Successor'] in eventtype.getPrecendenceDict():
                                    eventtype.getPrecendenceDict()[r['Successor']] = []
                                eventtype.getPrecendenceDict()[r['Successor']].append(r['PrecedenceInfo'])

                        #self.getOperationsManager().getSimulator().saveLog("REPORT: precedenceinfo_df applied ")

                            
       
        except Exception as e:
            #self.getSimulator().saveLog("ERROR: in reading use cases "+str(e))  
            display("ERROR: in reading use cases "+str(e))


        return
##############################################################################################################################################
    def generateRandomDemands(self):
        
        demand_weight = 10000 # kg
        avg_batch_weight = 500 # kg per container
        no_batches = math.ceil(demand_weight/avg_batch_weight)
        bag_ratio = 0.6; bag_weight_range = range(10,15); box_weight_range = range(25,40) # in kg.
        nr_destinations = 15; priorities = [1,2,3]
        destinations = [str(x) for x in range(nr_destinations)]
        destination_probs = [random.random() for x in range(nr_destinations)]
        priority_probs = [random.random() for x in range(len(priorities))]
        prob_sum = sum(destination_probs); prio_sum = sum(priority_probs)
        destination_probs = [x/prob_sum for x in destination_probs]  # make sum to one. 
        priority_probs = [x/prio_sum for x in priority_probs]  # make sum to one. 
        destination_probs = np.cumsum(destination_probs); priority_probs = np.cumsum(priority_probs)

        arrival_date = self.getOperationsManager().getSimulator().getStartDay()
        
        remaining_weight = demand_weight
        
        def sampleFromProbList(itemlist,probabilitylist):
            prob_samp = random.random()
        
            for itemid in range(len(itemlist)):
                    if probabilitylist[itemid] > prob_samp:
                        return itemlist[itemid]
        
            return None
        
        
        print("Batches: ",no_batches)
        
        demand_df = pd.DataFrame(columns=["ShipmentBatch","ShipmentType","Arrival Date","Priority","Weight","Destination"])
        
        for batchid in range(no_batches): # here the atches for each container is created.
            batchweight = 0 
            while batchweight < avg_batch_weight:
                shiptype = "Bag" if  random.random() <= bag_ratio else "Box"
                shipweight = random.choice(bag_weight_range) if shiptype == "Bag" else random.choice(box_weight_range)    
                batchweight+=shipweight
                remaining_weight-= shipweight         
                shipmentdata = {"ShipmentBatch":batchid,"ShipmentType":shiptype,"Arrival Date":arrival_date,"Priority":sampleFromProbList(priorities,priority_probs)
                                ,"Weight":shipweight,"Destination":sampleFromProbList(destinations,destination_probs)} 
                demand_df.loc[len(demand_df)]= shipmentdata
        
            if remaining_weight <= 0:
                break
        
        print(demand_df["ShipmentBatch"].unique())
        print("remaining_weight: ",remaining_weight," total shipments: ",len(demand_df))
    
        consdate = (datetime.now()).date()
        
        demand_df.to_csv(os.path.join("..", self.getOperationsManager().getSimulator().getController().getUseCase(), "Demand_"+str(consdate)+".csv"),index = False)
    
        return
#############################################################################################################################################
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

   