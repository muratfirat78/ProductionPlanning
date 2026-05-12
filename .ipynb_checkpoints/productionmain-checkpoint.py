from Simulator import *
from datetime import timedelta,date
from productionobjects import *
from productionalgs import *
from productionChecker import *
from datetime import timedelta,date,datetime
import numpy as np



#################################################################################
class ShopFloorManager(OperationsManager): 
    def __init__(self,sim,demandtypename):
        super().__init__(sim,demandtypename)
        
        self.CentralInventory = Inventory(10000,sim,self) 
        self.all_pns = [str(x) for x in range(1000)]
        self.ProductionAlgManager = ProductionAlgManager(sim,self)
        self.DataManager = ProductionDataManager(sim,self)
        self.Checker = productionFeasibilityChecker(sim,self)
        self.Products = dict() # key: ID, val: object
        self.ProductionOrders = dict() # key: ID, val: object
        self.setUseCase("TBRM Machining BV")

        

        # Trailer Loading -> Trailer Transport -> Trailer Unloading

        # Inputbuffer: Items change, it creates pending machine loading event. 

        #EventType: (myname,restype,equiptype,static,loading,process)
        trailerLoading = EventType("Trailer Loading","Operator","Trailer",True,True,False)
        self.getEventTypes()["Trailer Loading"]= trailerLoading
        trailerTransport = EventType("Trailer Transport","Operator","Trailer",False,False,False)
        self.getEventTypes()["Trailer Transport"]= trailerTransport
        trailerUnloading = EventType("Trailer Unloading","Operator","Trailer",True,False,False);
        self.getEventTypes()["Trailer Unloading"]= trailerUnloading 
        bringEquipment = EventType("Bring Equipment","Operator","Trailer",False,False,False)
        self.getEventTypes()["Bring Equipment"]= bringEquipment 
        operatorMove = EventType("Operator Move","Operator","Operator",False,False,False)
        self.getEventTypes()["Operator Move"]= operatorMove 
   
   
        bringEquipment.getPrecendenceDict()[trailerLoading.getName()] = ['Equipment','Resource'] 
        trailerLoading.getPrecendenceDict()[trailerTransport.getName()] = ['Equipment','Resource','Items']
        trailerTransport.getPrecendenceDict()[trailerUnloading.getName()] = ['Equipment','Resource']

        bringEquipment.setSuccessorType(trailerLoading)
        trailerLoading.setSuccessorType(trailerTransport)
        trailerTransport.setSuccessorType(trailerUnloading)
        

        machineLoadingAutomated = EventType("Machine Loading Automated","Machine","Machine",True,True,False)
        self.getEventTypes()["Machine Loading Automated"]= machineLoadingAutomated  
        machineLoadingManual = EventType("Machine Loading Manual","Operator","Machine",True,True,False)
        self.getEventTypes()["Machine Loading Manual"]= machineLoadingManual
        machineProcessing = EventType("Processing","Machine","Machine",True,False,True)
        self.getEventTypes()["Processing"]= machineProcessing
        machineProcessingAutomated = EventType("Processing Automated","Machine","Machine",True,False,True)
        self.getEventTypes()["Processing Automated"]= machineProcessingAutomated
        machineUnloadingAutomated = EventType("Machine Unloading Automated","Machine","Machine",True,False,False)
        self.getEventTypes()["Machine Loading Automated"]= machineLoadingAutomated  
        machineUnloadingManual = EventType("Machine Unloading Manual","Operator","Machine",True,False,False)
        self.getEventTypes()["Machine Unloading Manual"]= machineUnloadingManual

        # Machine Loading -> Processing -> Machine Unloading (manual and automated)

        # Outputbuffer: Items change, it creates pending trailer loading event. 
        
        machineLoadingAutomated.setSuccessorType(machineProcessingAutomated)
        machineLoadingAutomated.getPrecendenceDict()[machineProcessingAutomated.getName()] = ['Equipment','Resource','Items']
        machineProcessingAutomated.setSuccessorType(machineUnloadingAutomated)
        machineProcessingAutomated.getPrecendenceDict()[machineUnloadingAutomated.getName()] = ['Equipment','Resource','Items']

        machineLoadingManual.setSuccessorType(machineProcessing)
        machineProcessing.setSuccessorType(machineUnloadingManual)


        self.DataManager.getObjectFeatures()["ProductionOrder"] = [("FinalProduct","Product")]
        self.DataManager.getObjectFeatures()["ProductionOrder"].append(("FinalProductID","Product/ID"))
        self.DataManager.getObjectFeatures()["ProductionOrder"].append(("ID","ID"))
        self.DataManager.getObjectFeatures()["ProductionOrder"].append(("DF_Index","Index"))
        self.DataManager.getObjectFeatures()["ProductionOrder"].append(("Quantity","Quantity To Produce"))
        self.DataManager.getObjectFeatures()["ProductionOrder"].append(("ProductUnit","Product Unit of Measure"))
        self.DataManager.getObjectFeatures()["ProductionOrder"].append(("State","State"))
        self.DataManager.getObjectFeatures()["ProductionOrder"].append(("DeadLine","Deadline"))
        self.DataManager.getObjectFeatures()["ProductionOrder"].append(("RawMaterial","Components/Product"))
        self.DataManager.getObjectFeatures()["ProductionOrder"].append(("RawMaterialID","Components/Product/ID"))
        self.DataManager.getObjectFeatures()["ProductionOrder"].append(("RawMaterialMultiplier","Components/Quantity To Consume"))



        self.DataManager.getObjectFeatures()["Product"] = [("ProductName","Product")]
        self.DataManager.getObjectFeatures()["Product"].append(("ID","Product/ID"))
        
        self.DataManager.getObjectFeatures()["RawMaterial"] = [("ProductName","Components/Product")]
        self.DataManager.getObjectFeatures()["RawMaterial"].append(("ID","Components/Product/ID"))

        

   
    def getChecker(self):
        return self.Checker
        
    def getDataManager(self):
        return self.DataManager

    def getProducts(self):
        return self.Products
     
    def getProductionOrders(self):
        return self.ProductionOrders
    
    def printDemand(self,demand):
        print("Demand: Ref.No ",demand.getPN(),", Oprs: ",[(x.getAlternativeMachines()[0].getName(),x.getProcessTime()) for x in demand.getOperations()])

########################################################
    def createInstance(self,processtimedist):

        self.DataManager.ReadResources()
   
        for trailer in range(5):
            trlr = Trailer(5000,self.getSimulator(),self); 
            trlr.setLocation(self.getCentralInventory())
            self.getResources().append(trlr)

        for res in self.getResources():
            if isinstance(res,Machine) or isinstance(res,Inventory):
                print("Resource",res.getType(),'id: ',res.getID(),"code",res.getMachineCode(),"automated",res.IsAutomated(),",",("" if res.getInputBuffer() == None else res.getInputBuffer().getName()),",",("" if res.getOutputBuffer() == None else res.getOutputBuffer().getName())," created.")
            else:
                print("Resource",res.getType(),'id: ',res.getID()," created.")

        
        self.DataManager.ReadDemandFile(processtimedist) # production orders created...

        #now choose soonest production orders to simulate..
        prodorders = []

        for prodordid,prodorder in self.getProductionOrders().items():
            prodorders.append((prodorder.getDeadline(),prodorder))
            

        prodorders.sort(key=lambda x: x[0], reverse=False)

        for prodorder in prodorders[:min(2,len(prodorders))]:
            print("__________________________________________________________")
            print("Selected production order deadline: ",prodorder[1].getDeadline())
            self.createDemandItems(prodorder[1],prodorder[1].getFinalProduct())
            print("Selected production order has: ",len(prodorder[1].getItems())," items created.")
            oprseq = prodorder[1].getFinalProduct().getOperationSequences()[prodorder[1].getID()]
            print("Product ",prodorder[1].getFinalProduct().getName()," has ",len(oprseq),"Operations")
            for op in oprseq:
                print(" Operation ",op.getName()+" Proctime: ",op.getRandVar().sampleValue()," Resources: ",[alt.getMachineCode() for alt in op.getAlternativeResources()])
        
                
   
        return

#_____________________________________________________________________
    def createDemandItems(self,demand,product): # Physical products
        
        if len(product.getPredecessors()) == 0:
            for itm in range(demand.getQuantity()):
                myitem = Item(demand,self.giveItemID())
                #print("Item",myitem.getID()," of prod ",demand.getDemandType().getName(), demand.getDemandType().getPN(),' id ',demand.getID()," created.")
                self.getCentralInventory().getOutputBuffer().addItem(myitem) # generate trailer loading event.
                demand.getItems().append(myitem)
        else:
            for preddemnd in demand.getDemandType().getPredecessors():
                self.createDemandItems(demand,preddemnd)
               

        return
         
#______________________________________________________________________

    def handleEvent(self,event):

        if not self.handlePendingEvent(event):
            return False

        timedelay = 0
        opr_move = None
        if event.getEquipment().getLocation() != event.getLocation():
                            
            if event.getResource().getLocation() != event.getEquipment().getLocation():
                opr_move_event_type = self.getEventTypes()["Operator Move"]    
                loc_tuple = (event.getResource().getLocation(),event.getEquipment().getLocation())
                # loc,start,proctime,sim,eventype
                opr_move = Event(loc_tuple,self.getSimulator().getTime(),1,self.getSimulator(),opr_move_event_type)
                opr_move.setResource(event.getResource()); opr_move.setEquipment(event.getResource());  
                event.getResource().getAssignedEvents().append(opr_move)
                self.getSimulator().ScheduleEvent(opr_move,self.getSimulator().getTime())
                timedelay+=1
        
            loc_tuple = (event.getEquipment().getLocation(),event.getLocation())   
            bring_event_type = self.getEventTypes()["Bring Equipment"]    
            # loc,start,proctime,sim,eventype
            bring_event = Event(loc_tuple,self.getSimulator().getTime()+timedelay,1,self.getSimulator(),bring_event_type)
            bring_event.setEquipment(event.getEquipment()); bring_event.setResource(event.getResource())
            self.getSimulator().ScheduleEvent(bring_event,self.getSimulator().getTime()+timedelay)
            if opr_move != None:
                opr_move.setSuccessor(bring_event)
            bring_event.setSuccessor(event)
            timedelay+=1
        
        else: 
            if event.getLocation() != event.getResource().getLocation():
                opr_move_event_type = self.getEventTypes()["Operator Move"]    
                loc_tuple = (event.getResource().getLocation(),event.getLocation())
                opr_move = Event(loc_tuple,self.getSimulator().getTime(),1,self.getSimulator(),opr_move_event_type)
                opr_move.setSuccessor(event)
                timedelay+=1
        
        self.getSimulator().ScheduleEvent(event,self.getSimulator().getTime()+timedelay)
        print(" > "+str(self.getSimulator().getTime())+": "+event.print()+" handled.")

        return True


               
    def getProducts(self):
        return self.Products
        
    def getOrders(self):
        return self.Orders
        
    def getResources(self):
        return self.Resources 
        
    def setCentralInventory(self,mybuff):
        self.CentralInventory = mybuff
        return

    def getCentralInventory(self):
        return self.CentralInventory
        #################################################################################################################################
    def getProductionAlgManager(self):
        return  self.ProductionAlgManager 

########################################################################################################################
    def commpleteEvent(self,event):

        event.getResource().setIdle()
        event.getEquipment().setIdle()  
        
        if event in event.getEquipment().getMyEvents():
            event.getEquipment().getMyEvents().remove(event)

        
        if event.getEventType().isStatic():
            if not event.getEventType().isProcess():
                for item in event.getItems():
                    location_update = {"Entity":"Item","EntityID":item.getID(),"EventName":event.getName(),"EventID":event.getID(),"LocationID":event.getPlace().getID(),"LocationName":event.getPlace().getName(),"Time":self.getSimulator().getTime()}   
                    item.getLocationData().append(location_update)
                    if event.getEventType().isLoading():
                        event.getPlace().removeItem(item)
                        event.getEquipment().getItems().append(item)
   
                    else:
                        event.getEquipment().getItems().remove(item)
                        event.getPlace().addItem(item)
                     
                if not event.getEventType().isLoading() and isinstance(event.getPlace(),Buffer) and isinstance(event.getEquipment(),Machine):
                
                   
                    if len(event.getEquipment().getItems()) == 0:
                        event.getEquipment().getInputBuffer().generateEvent()

                
                if event.getPlace().getPendingEvent() == event:
                    event.getPlace().setPendingEvent(None)
                if (event.getLocation() != event.getEquipment()): # trailer
                    if event.getEventType().isLoading():
                        event.getPlace().generateEvent()
                else:
                    if isinstance(event.getLocation(),Machine):
                        if not event.getEventType().isLoading():
                            event.getLocation().getInputBuffer().generateEvent()
                        
                
    
            else:
                for item in event.getItems():
                    myprocessdata = {"ItemID":item.getID(),"Demand":item.getDemand().getID(),"OperationName":item.getActiveOperation().getName(),"ProcessID":event.getID(),"ResourceID":event.getResource().getID(),"Start":event.getStartTime(),"Completion":self.getSimulator().getTime()}                 
                    item.getProcessData().append(myprocessdata)
                    location_update = {"Entity":"Item","EntityID":item.getID(),"EventName":event.getName(),"EventID":event.getID(),"LocationID":event.getLocation().getID(),"LocationName":event.getLocation().getName(),"Time":self.getSimulator().getTime()}   
                    item.getLocationData().append(location_update)
                    
        else: # make location updates for dynamic event
            event.getResource().setLocation(event.getLocation()[1]) 
            evloc = event.getLocation()[0].getName()+"->"+event.getLocation()[1].getName()
            location_update = {"Entity":event.getResource().getName(),"EntityID":event.getResource().getID(),"EventName":event.getName(),"EventID":event.getID(),"LocationID":event.getLocation()[1].getID(),"LocationName":evloc,"Time":self.getSimulator().getTime()}  
            event.getResource().getLocationData().append(location_update)

            location_update = {"Entity":event.getEquipment().getName(),"EntityID":event.getEquipment().getID(),"EventName":event.getName(),"EventID":event.getID(),"LocationID":event.getLocation()[1].getID(),"LocationName":evloc,"Time":self.getSimulator().getTime()}  
            event.getEquipment().getLocationData().append(location_update)
            
            if event.getResource()!= event.getEquipment():
                event.getEquipment().setLocation(event.getLocation()[1])

            for item in event.getEquipment().getItems():
                location_update = {"Entity":"Item","EntityID":item.getID(),"EventName":event.getName(),"EventID":event.getID(),"LocationID":event.getLocation()[1].getID(),"LocationName":evloc,"Time":self.getSimulator().getTime()}   
                item.getLocationData().append(location_update)
          
        nexteventtype = event.getEventType().getSuccessorType() 

        
        if nexteventtype != None: 
            #print(" > "+str(self.getSimulator().getTime())+": successor event "+event.getEventType().getSuccessorType().getName()+", stc: "+str(nexteventtype.isStatic())) 

            
            proctime = 1
            if nexteventtype.isProcess():
                proctime = event.getItems()[0].getActiveOperation().getRandVar().sampleValue()

            nextloc = event.getLocation() if event.getEventType().isStatic() else event.getLocation()[1]
          

            if not isinstance(event.getEquipment(),Machine): # trailer
                if not event.getEventType().isStatic(): # trailer and current is TT, next TU 
                    nextloc = nextloc.getInputBuffer()
            else: # machine
                if event.getEventType().isProcess(): # machine and current is Proc, next MU
                    nextloc = nextloc.getOutputBuffer()
                else:
                    if not event.getEventType().isLoading():
                        event.getLocation().getInputBuffer().generateEvent()
                        
                    

            nextevent = event.getSuccessor() if event.getSuccessor()!= None else Event(nextloc,"Pending",proctime,self.getSimulator(),nexteventtype)        
            event.setSuccessor(nextevent)

            
            if 'Equipment' in event.getEventType().getPrecendenceDict()[nextevent.getEventType().getName()]:
                nextevent.setEquipment(event.getEquipment()); event.getEquipment().setAssigned()
            if 'Resource' in event.getEventType().getPrecendenceDict()[nextevent.getEventType().getName()]:
                nextevent.setResource(event.getResource()); event.getResource().setAssigned()
            if 'Items' in event.getEventType().getPrecendenceDict()[nextevent.getEventType().getName()]:
                for item in event.getItems():
                    nextevent.getItems().append(item)

            if (nextevent.getLocation() != nextevent.getEquipment()): # trailer
                if nextevent.getEventType().isStatic():
                    #print(" > "+str(self.getSimulator().getTime())+": setPlace>>>>>>>>>>>>>  "+nextevent.getLocation().getName()+".")
                    if nextevent.getPlace() == None: 
                        nextevent.setPlace(nextevent.getLocation())
     
            print(" > "+str(self.getSimulator().getTime())+": nextevent "+nextevent.print()+" defined.")
    

            if (nextevent.getEquipment() != None) and (nextevent.getResource() != None):
                nextevent.setStartTime(self.getSimulator().getTime())
                self.getSimulator().ScheduleEvent(nextevent,self.getSimulator().getTime())
            else: 
                self.getSimulator().ScheduleEvent(nextevent,"Pending")

        print(" > "+str(self.getSimulator().getTime())+": "+event.print()+" finalized.")
        
      
        return
        
    def getLocationDF(self):

        location_df= pd.DataFrame(columns=["Entity","EntityID","EventName","EventID","LocationID","LocationName","Time"])


        for orderid,order  in self.getProductionOrders().items():
            for item in order.getItems():
                for dt in item.getLocationData():
                     location_df.loc[len(location_df)] = dt
        for resource in self.getResources():
            for dt in resource.getLocationData():
                location_df.loc[len(location_df)] = dt

  
        return location_df
    
    def getProcessDF(self):

        process_df = pd.DataFrame(columns=["ItemID","Demand","OperationName","ProcessID","ResourceID","Start","Completion"])


        for orderid,order in self.getProductionOrders().items():
            for item in order.getItems():
                for dt in item.getProcessData():
                    process_df.loc[len(process_df)] = dt
              
  
        return process_df
#########################################################################################################################
    def writeData(self):
        
        process_df = self.getProcessDF()
        location_df = self.getLocationDF()
        process_df.to_csv("ProcessData.csv",index = False)
        location_df.to_csv("LocationData.csv",index = False)  

        return 

        
#################################################################################################
class ProductionDataManager(DataManager): 
    def __init__(self,sim,workmgr):
        super().__init__(sim,workmgr) 

###########################################################################################
    def ReadResources(self):
     
        rel_path = '/'+self.getOperationsManager().getUseCase()
        abs_file_path = os.path.dirname(os.path.realpath(__file__))+rel_path
        
        print(abs_file_path)

        

        latestfiledate = None
        filename = None

        for root, dirs, files in os.walk(abs_file_path):
            for file in files: 
                print(file)
                if ".csv" in file:                  
                    try: 
                        filedate = datetime.strptime(file[file.find("Resources_")+len("Resources_"):-5],"%Y-%m-%d")
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
            print("Latest Date resources file date: ",latestfiledate)
            TBRMResources_df = pd.read_csv(abs_file_path+'/'+filename)

            print(TBRMResources_df.info())
            for i,r in TBRMResources_df.iterrows():
                if r['ResourceType'] == 'Operator':
                    AvlShifts = [1]  
                    try: 
                        AvlShifts = r['AvailableShifts'].split("_")
                        AvlShifts = [int(s) for s in AvlShifts]
                    except Exception as e:
                        print("Error in reading available shifts of operator ",r['Name'])
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
                        print("Error in reading operating shifts of machine ",r['Name'])

                    Alternatives = []
                    if not pd.isna(r['Alternatives']): 
                        try: 
                            Alternatives = r['Alternatives'].split("~")
                        except Exception as e:
                            print("Error in reading alternatives of machine ",r['Name'],":",pd.isna(r['Alternatives']))

                    #myname,machcode,OprtingShifts,processtype,automated,mycap,Alternatives,OprtingEffort,sim,workmngr
                    if len(Alternatives) > 0:
                        print(Alternatives)
                    mach = Machine(mcode,r['Name'],OperatingShifts,r['ProcessType'],r['Automated'],50000,Alternatives,r['OperatingEffort'],self.getSimulator(),self.getOperationsManager())
                    mach.setLocation(mach)
                    self.getOperationsManager().getResources().append(mach)
                    
            
            print("No resources: ",len(self.getOperationsManager().getResources()))         
           
        return
        
#####################################################################################################################################
    def ReadDemandFile(self,processtimedist):
        rel_path = '/'+self.getOperationsManager().getUseCase()
        abs_file_path = os.path.dirname(os.path.realpath(__file__))+rel_path
        
        print(abs_file_path)

        

        latestfiledate = None
        filename = None

        for root, dirs, files in os.walk(abs_file_path):
            for file in files: 
                print(file)
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

           
            print("Latest Date input file date: ",latestfiledate)
            TBRM_df = pd.read_excel(abs_file_path+'/'+filename)

            #TBRM_df.info()
            TBRM_df["Index"] = [i for i in range(len(TBRM_df))]
           

            TBRM_df["Deadline"] = TBRM_df["Deadline"].fillna(TBRM_df["Deadline"].max()+timedelta(days=7))
            TBRM_df["Components/Product"] = TBRM_df["Components/Product"].fillna("UnknownRawMaterial")
            TBRM_df["Components/Product/ID"] = TBRM_df["Components/Product/ID"].fillna("UnknownRawMaterialID")
            TBRM_df["Components/Quantity To Consume"] = TBRM_df["Components/Quantity To Consume"].fillna("UnknownRawMaterialQ")
            
           
            #TBRM_df.info()
           
  
            print("Size of input file: ",len(TBRM_df))

            prodorder_aggrfeats = [x[1] for x in self.getOperationsManager().getDataManager().getObjectFeatures()["ProductionOrder"]]
            print("Prod order feats to aggregte: ",prodorder_aggrfeats)
     
            prodorders_df = TBRM_df.groupby(prodorder_aggrfeats).size().reset_index() 

            ####### PRODUCTS TO PRODUCE 
            prod_aggrfeats = [x[1] for x in self.getOperationsManager().getDataManager().getObjectFeatures()["Product"]]
            products_df = prodorders_df.groupby(prod_aggrfeats).size().reset_index()

            for i,r in products_df.iterrows():
                prodpn = None
                if "[" in r['Product']:
                    prodpn = r['Product'][r['Product'].find("[")-1:]
                    prodpn = r['Product'][:r['Product'].find("]")+1]
                else:
                    prodpn = r['Product']
                    
                myproduct= Product(prodpn,str(r['Product/ID']),r['Product'])
                self.getOperationsManager().getProducts()[myproduct.getID()]= myproduct
    
                #print(i,"Product created with PN:",myproduct.getPN())
                
           ####### RAW MATERIALS 
            rawmat_aggrfeats = [x[1] for x in self.getOperationsManager().getDataManager().getObjectFeatures()["RawMaterial"]]

            raw_materials_df = prodorders_df.groupby(rawmat_aggrfeats).size().reset_index()
            for i,r in raw_materials_df.iterrows():
                prodpn = None
                if "[" in r['Components/Product']:
                    prodpn = r['Components/Product'][r['Components/Product'].find("[")-1:]
                    prodpn = r['Components/Product'][:r['Components/Product'].find("]")+1]
                else:
                    prodpn = r['Components/Product']
                    
                myproduct= Product(prodpn,str(r['Components/Product/ID']),r['Components/Product'])
                self.getOperationsManager().getProducts()[myproduct.getID()]= myproduct
    
                #print(i,"Raw Material created with PN:",myproduct.getPN())

            prodorders = []

            ## Create Production Orders
            for i,r in prodorders_df.iterrows():
                props = [x[1] for x in self.getOperationsManager().getDataManager().getObjectFeatures()["ProductionOrder"]]
              
                myprod = self.getOperationsManager().getProducts()[str(r[props[1]])]

                if str(r[props[9]]) in self.getOperationsManager().getProducts():
                    myraw = self.getOperationsManager().getProducts()[str(r[props[9]])]
   
                    myprod.getPredecessors()[myraw] = r[props[10]]
                    myraw.getSuccessors()[myprod] = r[props[10]]
                    
                prodorder = ProductionOrder(r[props[7]],r[props[2]],myprod,int(r[props[4]]),r['Index']) #ddline,myid,demtype,quantity,dfindex

                self.getOperationsManager().getProductionOrders()[prodorder.getID()] = prodorder
                prodorders.append((r['Index'],prodorder))

            prodorders.sort(key=lambda x: x[0], reverse=False)
      
            #print(TBRM_df.head(25))

            ###### Read the operation sequences 
            prodordind = 0 
            for prodordind in range(len(prodorders)):
                #print(prodordind,"Production order created:",prodorders[prodordind][1].getID()," of prod id",prodorders[prodordind][1].getFinalProduct().getID(),"index ",prodorders[prodordind][0])

                if prodordind < len(prodorders)-1:
                    for i in range(prodorders[prodordind][0],prodorders[prodordind+1][0]):
                        TBRM_df.iloc[i, TBRM_df.columns.get_loc('ID')] = prodorders[prodordind][1].getID()
                
                prodordind+=1

            TBRM_Operations_df = TBRM_df.groupby(['ID'], dropna=True)[['Work Orders/Work Center','Work Orders/Work Center/ID','Work Orders/Operation','Work Orders/Expected Duration']].agg(lambda x:list(x)).reset_index()


            machines = [r for r in self.getOperationsManager().getResources() if isinstance(r,Machine)]

            print("The system has ",len(machines),"machines")

            for i,r in TBRM_Operations_df.iterrows():
                OprResources = r['Work Orders/Work Center']
                OprResourceIDs = r['Work Orders/Work Center/ID']
                OprProcTimes = r['Work Orders/Expected Duration']

                oprsequence = []
                
                for resid in range(len(OprResources)):
                    #first find the resource
                    oprres = OprResources[resid]
     
                    if not pd.isna(oprres): 
                        for mach in machines:
                            if mach.getMachineCode() in oprres:
                                if mach.getID() != OprResourceIDs[resid]:
                                    mach.setID(OprResourceIDs[resid])
                                myopr = Operation(oprres,self.getOperationsManager().giveProcessID(),OprProcTimes[resid],processtimedist) #name,myid,proctime
                                myopr.getAlternativeResources().append(mach)
                                for mach_alternative in mach.getAlternatives():
                                    for mymach in machines:
                                        if mymach.getMachineCode() == mach_alternative:
                                            myopr.getAlternativeResources().append(mymach)
                                            break
                                #if len(myopr.getAlternativeResources()) > 1: 
                                    #print("Opr",myopr.getName(),"has alternative resources: ",len(myopr.getAlternativeResources())-1)
                                oprsequence.append(myopr)
                    else:
                        myopr = Operation("UnknownOperation",self.getOperationsManager().giveProcessID(),0,processtimedist) #name,myid,proctime
                        oprsequence.append(myopr)

                
                prodorder = self.getOperationsManager().getProductionOrders()[r['ID']]

                prodorder.getFinalProduct().getOperationSequences()[r['ID']] = oprsequence

                #print("Product ", prodorder.getFinalProduct().getName()," has ",len(oprsequence),"Operations")

                #print(" Alt res: ",[op.getName()+" @"+str(alt.getMachineCode()) for op in oprsequence for alt in op.getAlternativeResources() ])

        return

        
