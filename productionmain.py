from Simulator import *
from datetime import timedelta,date
from productionobjects import *
from productionalgs import *
from productionChecker import *
from productiondata import *
from datetime import timedelta,date,datetime
import numpy as np
import pandas as pd



#################################################################################
class ShopFloorManager(OperationsManager): 
    def __init__(self,sim):
        super().__init__(sim)

        self.Layout = Layout("TBRM Machining BV")

        centralloc = Location("CentralBuffer_Location",len(self.Layout.getLocations()))
        self.Layout.getLocations().append(centralloc)
        
        self.CentralInventory = Inventory(10000,centralloc,sim,self) 
        self.all_pns = [str(x) for x in range(1000)]
        self.ProductionAlgManager = ProductionAlgManager(sim,self)
        self.DataManager = ProductionDataManager(sim,self)
        self.Checker = productionFeasibilityChecker(sim,self)
        self.Products = dict() # key: ID, val: object
        self.ProductionOrders = dict() # key: ID, val: object
        self.setUseCase("TBRM Machining BV")
        self.NoOrders = 5
        self.SelectedOrders = []
        self.PerformanceRun = True
        self.inputdate = None
        self.AlgorithmSetting = dict() # key: event name, val: (Decision name, Algorithm name)
        self.ProcessTimes = dict()  #key: event type name, val: 
        self.EventStatuses = dict() # key: status change, val: (prev_status,next_status)
        self.UnloadingCompletionTimes = dict()
       
        # SimEvent: sim,myname,mytype,restype,equiptype,preemptable


        
        # Trailer Loading -> Trailer Transport -> Trailer Unloading
        TrailerLoading = SimEvent(self.getSimulator(),"Trailer Loading","Loading","Operator","Trailer",False)
        TrailerLoading.getDecisionsDict()['Handle'] = ['Assign Resource','Assign Equipment','Select Items']

        self.getAlgorithmSetting()[TrailerLoading.getName()] = {"Select Items":'EDDOrder','Assign Resource':"Straight Available","Assign Equipment":"Straight Available"}
       
        self.getEventTypes()[TrailerLoading.getName()]= TrailerLoading
        #-------------------------------------------
        TrailerTransport= SimEvent(self.getSimulator(),"Trailer Transport","Transport","Operator","Trailer",False)
        TrailerLoading.getSuccessorDict()[TrailerTransport] = "Finish to Start"  # Precedence settings: TL -> TT
        TrailerLoading.getPrecendenceDict()[TrailerTransport.getName()] = ['FromLocation','Equipment','Resource','Items']
   
        self.getAlgorithmSetting()[TrailerTransport.getName()] = {"Select Destination":'MostDemanded' }
        self.getEventTypes()[TrailerTransport.getName()]= TrailerTransport
        #-------------------------------------------
        TrailerUnloading= SimEvent(self.getSimulator(),"Trailer Unloading","Unloading","Operator","Trailer",False)

        TrailerTransport.getSuccessorDict()[TrailerUnloading] = "Finish to Start"  # Precedence settings: TT -> TU
        TrailerTransport.getPrecendenceDict()[TrailerUnloading.getName()] = ['Equipment->FromLocation','ToLocation','Equipment','Resource']
  
        TrailerUnloading.getDecisionsDict()['Start'] = ['Select Items']

        self.getAlgorithmSetting()[TrailerUnloading.getName()] = {"Select Items":'UnloadFeasible' }  
        self.getEventTypes()[TrailerUnloading.getName()]= TrailerUnloading


         
        #-------------------------------------------
        #  Machine Setup -> Machine Loading -> Machine Processing -> Machine Unloading
        MachineSetup = SimEvent(self.getSimulator(),"Machine Setup","Setup","Operator","Machine",False)
        MachineSetup.getDecisionsDict()['Handle'] = ['Assign Resource',"Assign Equipment"]
        self.getAlgorithmSetting()[MachineSetup.getName()] = {'Assign Resource':"Straight Available","Assign Equipment":"Straight Available",'Select Items':"EDDOrder"}
        self.getEventTypes()[MachineSetup.getName()]= MachineSetup

        #-------------------------------------------
        MachineLoading = SimEvent(self.getSimulator(),"Machine Loading","Loading","Operator","Machine",True)   
        MachineSetup.getSuccessorDict()[MachineLoading] = "Finish to Start" # Precedence settings: MS -> ML
        MachineSetup.getPrecendenceDict()[MachineLoading.getName()] = ['FromLocation','FromLocationMachine->ToLocation','Equipment','Items','Processor']
        MachineLoading.getDecisionsDict()['Handle'] = ['Assign Resource']
        self.getAlgorithmSetting()[MachineLoading.getName()] = {'Assign Resource':"Straight Available"}
        self.getEventTypes()[MachineLoading.getName()]= MachineLoading

        #-------------------------------------------
        MachineProcessing = SimEvent(self.getSimulator(),"Machine Processing","Processing",None,"Machine",True)        
        MachineLoading.getSuccessorDict()[MachineProcessing] = "Simultaneous Start"  # Precedence settings: ML -> Proc
        MachineLoading.getPrecendenceDict()[MachineProcessing.getName()] = ['ToLocation->FromLocation','ToLocation->Resource','Equipment','Items','Processor']
        MachineProcessing.getDecisionsDict()['Handle'] = ["Assign Equipment"]
        self.getAlgorithmSetting()[MachineProcessing.getName()] = {"Assign Equipment":"Straight Available"} 
        self.getEventTypes()[MachineProcessing.getName()]= MachineProcessing

        #-------------------------------------------
        MachineUnloading = SimEvent(self.getSimulator(),"Machine Unloading","Unloading","Operator","Machine",True)
        MachineProcessing.getSuccessorDict()[MachineUnloading] = "CompletionRatio Start"   # Precedence settings: Proc -> MU
        MachineProcessing.getPrecendenceDict()[MachineUnloading.getName()] = ['FromLocation','FromLocationOutput->ToLocation','FromLocation->Equipment','Items']    
        MachineUnloading.getDecisionsDict()['Handle'] = ['Assign Resource']
        self.getAlgorithmSetting()[MachineUnloading.getName()] = {'Assign Resource':"Straight Available"}
        self.getEventTypes()[MachineUnloading.getName()]= MachineUnloading
        #-------------------------------------------

        
        SimOperatorMove = SimEvent(self.getSimulator(),"Operator Move","Logistical","Operator",None,False) 
        self.getEventTypes()[SimOperatorMove.getName()]= SimOperatorMove

        SimBringEquipment = SimEvent(self.getSimulator(),"Bring Equipment","Logistical","Operator","Trailer",False) 
        self.getEventTypes()[SimBringEquipment.getName()]= SimBringEquipment

    

        self.DataManager.getObjectFeatures()["ProductionOrder"] = [("FinalProduct","Product")]
        self.DataManager.getObjectFeatures()["ProductionOrder"].append(("FinalProductID","Product/ID"))
        self.DataManager.getObjectFeatures()["ProductionOrder"].append(("ID","ID"))
        self.DataManager.getObjectFeatures()["ProductionOrder"].append(("DF_Index","Index"))
        self.DataManager.getObjectFeatures()["ProductionOrder"].append(("Quantity","Quantity To Produce"))
        self.DataManager.getObjectFeatures()["ProductionOrder"].append(("ProductUnit","Unit"))
        self.DataManager.getObjectFeatures()["ProductionOrder"].append(("State","State"))
        self.DataManager.getObjectFeatures()["ProductionOrder"].append(("DeadLine","Deadline"))
        self.DataManager.getObjectFeatures()["ProductionOrder"].append(("RawMaterial","Components/Product"))
        self.DataManager.getObjectFeatures()["ProductionOrder"].append(("RawMaterialID","Components/Product/ID"))
        self.DataManager.getObjectFeatures()["ProductionOrder"].append(("RawMaterialMultiplier","Components/Quantity To Consume"))



        self.DataManager.getObjectFeatures()["Product"] = [("ProductName","Product")]
        self.DataManager.getObjectFeatures()["Product"].append(("ID","Product/ID"))
        
        self.DataManager.getObjectFeatures()["RawMaterial"] = [("ProductName","Components/Product")]
        self.DataManager.getObjectFeatures()["RawMaterial"].append(("ID","Components/Product/ID"))

    ###############################################################################

    def isPerformanceRun(self):
        return self.PerformanceRun


    def getCurrentShiftEnd(self):
        
        curr_shiftstart = (self.getSimulator().getTime()//self.getSimulator().getShiftMinutes())*self.getSimulator().getShiftMinutes()
 
        return curr_shiftstart+self.getSimulator().getShiftMinutes()

        
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

    def getSelectedOrders(self):
        return self.SelectedOrders

    def getLayout(self):
        return self.Layout
      

    def getChecker(self):
        return self.Checker

    def setNoOrders(self,orders):
        self.NoOrders = orders
        return
    def getNoOrders(self):
        return self.NoOrders 
        
        
    def getDataManager(self):
        return self.DataManager

    def getProducts(self):
        return self.Products
     
    def getProductionOrders(self):
        return self.ProductionOrders

    def getAlgorithmSetting(self):
        return self.AlgorithmSetting 
    
 
    

########################################################
    def createInstance(self):

        self.getSimulator().saveLog(">> Crating instance starts.. ")  

        try: 
            self.DataManager.ReadResources()
        except Exception as e:
            self.getSimulator().saveLog("ERROR: In read resources "+str(e)+".")
   
        for trailer in range(5):
            trlr = Trailer(5000,self.getSimulator(),self); 
            trlr.setAvailable(True)
            trlr.setLocation(self.getCentralInventory().getLocation())
            self.getResources().append(trlr)
   
        for res in self.getResources():
            if isinstance(res,Inventory):
                self.getSimulator().saveLog("Resource "+res.getType()+', id: '+str(res.getID())+", code"+res.getMachineCode()+"automated"+str(res.IsAutomated())+","+("" if res.getInputBuffer() == None else res.getInputBuffer().getName())+","+("" if res.getOutputBuffer() == None else res.getOutputBuffer().getName())+" created.")
            if isinstance(res,Machine) :
                self.getSimulator().saveLog("Resource "+res.getType()+', id: '+str(res.getID())+", code"+res.getMachineCode()+"automated"+str(res.IsAutomated())+", setup: "+str(res.getSetupTime())+","+("" if res.getInputBuffer() == None else res.getInputBuffer().getName())+","+("" if res.getOutputBuffer() == None else res.getOutputBuffer().getName())+" created.")
                 
            else:
                self.getSimulator().saveLog("Resource "+res.getType()+', id: '+str(res.getID())+" created.")

        try: 
            self.inputdate = self.DataManager.ReadDemandFile() # production orders created...
        except Exception as e: 
            self.getSimulator().saveLog("ERROR: In reading demand file "+str(e)+".")

        

        #now choose soonest production orders to simulate..
        prodorders = []

        for prodordid,prodorder in self.getProductionOrders().items():
            prodorders.append((prodorder.getDeadline(),prodorder))
            

        prodorders.sort(key=lambda x: x[0], reverse=False)

        selectedOrders = []

        for prodorder in prodorders[:min(self.getNoOrders(),len(prodorders))]:     
            self.getSimulator().saveLog("__________________________________________________________")
            self.getSimulator().saveLog("REPORT: Selected production order deadline: "+str(prodorder[1].getDeadline()))

            
            try: 
                self.getSimulator().saveLog("Item creation starts")
                self.createDemandItems(prodorder[1],prodorder[1].getFinalProduct())
                self.getSimulator().saveLog("REPORT: >>>> items ["+(str(prodorder[1].getItems()[0].getID()) if len(prodorder[1].getItems())>0 else '')+"-"+(str(prodorder[1].getItems()[-1].getID()) if len(prodorder[1].getItems())>0 else 'no item')+"]")
            except Exception as e:
                self.getSimulator().saveLog("ERROR in item creation: "+str(e))

            self.getSimulator().saveLog("REPORT:  Selected "+prodorder[1].printOrder()+" items created.")
            self.getSelectedOrders().append(prodorder[1])

        
        self.getSimulator().saveLog("REPORT:>> Creating instance finished.. ")      
   
        return self.getSelectedOrders()

#_____________________________________________________________________
    def createDemandItems(self,demand,product): # Physical products
        self.getSimulator().saveLog("Item creation starts")
        if len(product.getPredecessors()) == 0:
            for itm in range(demand.getQuantity()):
                
                myitem = Item(demand,self.giveItemID())
                self.getCentralInventory().getOutputBuffer().addItem(myitem) # generate trailer loading event.
                demand.getItems().append(myitem)
        else:
            for preddemnd in demand.getDemandType().getPredecessors():
                self.createDemandItems(demand,preddemnd)

        buffer_data = {"BufferName": self.getCentralInventory().getOutputBuffer().getName(),"Machine":  self.getCentralInventory().getOutputBuffer().getMachine().getName() if  self.getCentralInventory().getOutputBuffer().getMachine()!= None else "Central Inventory","Time":self.getSimulator().getTime(),"No.Items":len(self.getCentralInventory().getOutputBuffer().getItems())}  
        self.getSimulator().getBufferData().append(buffer_data)

        return
#______________________________________________________________________
############################################################################
    def applyShiftChange(self):

        printchange = False

        if printchange:
            self.getSimulator().saveLog("REPORT: Apply Shift Change starts..") 
        ##############################################################################################################
        avalable_res = [] 
        if printchange:
            self.getSimulator().saveLog("REPORT: current shift: "+str(self.getSimulator().getCurrentShift())+", simtime: "+str(self.getSimulator().getTime())) 
        for res in self.getResources():
            if isinstance(res,Operator):
                if printchange:
                    self.getSimulator().saveLog("REPORT: Res "+str(res.getName())+", avl shifts: "+str(res.getAvailableShifts())+", loc:  "+res.getLocation().getName()) 
            if isinstance(res,Trailer) or isinstance(res,Operator):
                if res.getLocation() != self.getCentralInventory().getLocation():
                    res.setLocation(self.getCentralInventory().getLocation())
                    if isinstance(res,Operator):
                        location_data = {"EntityName":res.getName(),"EntityID":res.getID(),"Time":self.getSimulator().getTime(),"LocationName":res.getLocation().getName(),"LocationID": (res.getLocation().getID() if res.getLocation()!= None else "-")}  
                        self.getSimulator().getLocationData().append(location_data)
                    
            if isinstance(res,Machine) or isinstance(res,Operator):
                res.setAvailable(self.getSimulator().getCurrentShift() in res.getAvailableShifts())
                res.setIdle(True)
                if res.isAvailable():
                    avalable_res.append(res.getName())
            else:
                res.setAvailable(True)
                res.setIdle(True)
       
        #self.getSimulator().saveLog("REPORT: available res: "+str(avalable_res)) 

        #self.getSimulator().saveLog(" REPORT: Shift Change completed..") 
        return
#################################################################################################################################################
    
    def ProgressEvent(self,event):
        # case can be one of the following: "handle","start","suspend","restart","complete"

        #if self.getSimulator().getTime() >= 5500 and self.getSimulator().getTime() <= 5550:
        #        self.getSimulator().saveLog("REPORT: event : "+str(event.getName()))
                      
        case = self.determineProgressCase(event)

        debugtimes = []
    
        if case == "Handle":
            if self.getSimulator().getTime() in debugtimes:
                oprseq = []
                if len(event.getItems()) > 0:
                    oprseq = event.getItems()[0].getDemand().getFinalProduct().getOperationSequences()[event.getItems()[0].getDemand().getID()]
                self.getSimulator().saveLog("REPORT: event : "+str(event.getName())+"("+str(event.getID())+"), items "+str(len(event.getItems()))+", active opr none? "+("No item " if len(event.getItems())==0 else str(event.getItems()[0].getActiveOperation()== None))+" event loc "+event.getLocation().getName()+", item oprs "+str([str(o.isCancelled())+"--"+str(o.isFinished())+"--"+str(o.getName()) for o in oprseq])+", tot.prog: "+str(event.getTotalProgress())+", p: "+str(event.getProcessTime())+", case: "+case)
                
                    
            event.sampleProcessTime(self)
            if not event.getEventType().isPreemptable():  # check if no time left in current shift for a non-preemtable event
                if self.getCurrentShiftEnd() - self.getSimulator().getTime() < event.getProcessTime():
                    return

   
        ######### MAKE NECESSARY DECISIONS  ########################################
        casesuccess = self.makeCaseDecisions(event,case,debugtimes)

        if not casesuccess:
            if case == "Handle":
                # add event to pending list and remove from time events.
                if self.getSimulator().getTime() in self.getSimulator().getEventQueue():
                    if event in self.getSimulator().getEventQueue()[self.getSimulator().getTime()]:
                        self.getSimulator().getEventQueue()[self.getSimulator().getTime()] = [x for x in self.getSimulator().getEventQueue()[self.getSimulator().getTime()] if x != event]
                        self.getSimulator().getEventQueue()["Pending"].append(event)  
            #if self.getSimulator().getTime() >= 950 and self.getSimulator().getTime() <= 1000:
            #    self.getSimulator().saveLog("REPORT: Handling of pending event : "+str(event.getName())+" at "+event.getFromLocation().getName()+" not successful")
                    
            return 

        if self.getSimulator().getTime() in debugtimes:
            self.getSimulator().saveLog(" REPORT: event: "+str(event.getName())+"("+str(event.getID())+")-["+(str(event.getItems()[0].getID()) if len(event.getItems())>0 else '')+"-"+(str(event.getItems()[-1].getID()) if len(event.getItems())>0 else '')+"]"+", active opr none? "+("No item " if len(event.getItems())==0 else (event.getItems()[0].getActiveOperation().getName() if event.getItems()[0].getActiveOperation()!= None else "No act opr"))+", loc "+(event.getLocation().getName() if event.getLocation() == None else "No loc")+", tot.prog: "+str(event.getTotalProgress())+", p: "+str(event.getProcessTime())+", succ event? none "+str(event.getSuspendedSuccessor() == None)+", case: "+case) 

            self.getSimulator().saveLog(" REPORT: event: "+str(event.getName())+"("+str(event.getID())+") , successor dict "+str(event.getEventType().getSuccessorDict().items()))

            if isinstance(event.getEquipment(),Trailer):
                if event.getEquipment() != None:
                    self.getSimulator().saveLog("REPORT: event : "+str(event.getName())+"("+str(event.getID())+"), equipment "+event.getEquipment().getName()+", items "+str(len(event.getEquipment().getItems())))

        if self.getSimulator().getTime() in debugtimes:
            for progress_id in range(len(event.getProgressList())):
                self.getSimulator().saveLog("REPORT: event: "+str(event.getName())+ "progress step: "+str(event.getProgressList()[progress_id][1]))
            self.getSimulator().saveLog("REPORT: event: "+str(event.getName())+", TotalProgress: "+str(event.getTotalProgress()))
       
        # PROGRESS UPDATES
        if case == "Suspend":
            if event.getType() == "Processing":
                if event in event.getEquipment().getProcessMatch():
                    del event.getEquipment().getProcessMatch()[event]    
            else:   
                if event.getName() != "Machine Unloading" and event.getName() != "Machine Loading":
                    event.setEquipment(None)               
                event.setResource(None)
            #self.getSimulator().saveLog(" REPORT: event in time list? "+str(event in self.getSimulator().getEventQueue()[self.getSimulator().getTime()])) 

            
            if event in self.getSimulator().getEventQueue()[self.getSimulator().getTime()]:
                self.getSimulator().getEventQueue()[self.getSimulator().getTime()].remove(event)
            #self.getSimulator().saveLog(" REPORT: event in time list? "+str(event in self.getSimulator().getEventQueue()[self.getSimulator().getTime()])) 
            #self.getSimulator().saveLog(" REPORT: event SuspendedSuccessor none? "+str(event.getSuspendedSuccessor() == None)) 
            
            if event.getSuspendedSuccessor() == None:
                self.getSimulator().getEventQueue()["Pending"].append(event)  

        if case == "Complete": 
            if self.getSimulator().getTime() in debugtimes:
                self.getSimulator().saveLog(" REPORT: event: "+str(event.getName())+" completion updates start..") 
            self.makeCompletionUpdates(event,debugtimes)
            
            if self.getSimulator().getTime() in debugtimes:
                self.getSimulator().saveLog(" REPORT: completion updates done.. res location: "+str(event.getResource().getLocation().getName())) 
                if isinstance(event.getEquipment(),Trailer):
                    if event.getEquipment() != None:
                        self.getSimulator().saveLog("REPORT: event : "+str(event.getName())+"("+str(event.getID())+"), equipment "+event.getEquipment().getName()+", items "+str(len(event.getEquipment().getItems())))


        
        if case == "Handle":  # register the progress
            # remove from pending list, if event is in it.
            if event in self.getSimulator().getEventQueue()["Pending"]:
                self.getSimulator().getEventQueue()["Pending"].remove(event)
                #self.getSimulator().saveLog(" REPORT: removed from pending list, pendings:  "+str(len(self.getSimulator().getEventQueue()["Pending"]))) 

            # remove from the time events list, if event is in it.
            if self.getSimulator().getTime() in self.getSimulator().getEventQueue():
                if event in self.getSimulator().getEventQueue()[self.getSimulator().getTime()]:
                    self.getSimulator().getEventQueue()[self.getSimulator().getTime()].remove(event)
                    #self.getSimulator().saveLog(" REPORT: removed from time events list ") 
 
            startdelay = 0
            for logistical_event in event.getLogisticalEvents():
                startdelay += logistical_event.getProcessTime()
            #self.getSimulator().saveLog(" REPORT: start delay: "+str(startdelay)) 
           
            processtime = event.getProcessTime() - event.getTotalProgress()
           
            progress_step = (startdelay+self.getSimulator().getTime(),min(self.getSimulator().getTime()+processtime+startdelay,self.getCurrentShiftEnd()))
            event.getProgressList().append((event.getResource(),progress_step))
            if event.getName() == "Machine Processing":
                event.getResource().getProgressList().append((event,progress_step))
            #self.getSimulator().saveLog(" REPORT: start delay: "+str(startdelay)+", prog_step "+str(progress_step)) 
       
            if len(event.getLogisticalEvents()) == 0:
                if not progress_step[0] in self.getSimulator().getEventQueue():
                    self.getSimulator().getEventQueue()[progress_step[0]] = []
                if not event in self.getSimulator().getEventQueue()[progress_step[0]]:   
                    self.getSimulator().getEventQueue()[progress_step[0]].append(event) 
                    #self.getSimulator().saveLog(" REPORT:added to time events list at "+str(progress_step[0])) 

            if event.getSuspendedPredecessor() != None:
                event.getSuspendedPredecessor().getProgressList().append((event.getSuspendedPredecessor().getResource(),progress_step))
                if event.getSuspendedPredecessor().getName() == "Machine Processing":
                    event.getSuspendedPredecessor().getResource().getProgressList().append((event.getSuspendedPredecessor(),progress_step))
                if not progress_step[1] in self.getSimulator().getEventQueue():
                    self.getSimulator().getEventQueue()[progress_step[1]] = []
                    
                self.getSimulator().getEventQueue()[progress_step[1]].append(event.getSuspendedPredecessor())

        ########################################   
        # SCHEDULE UPDATES   

         # remove progress step start and schedule the end of progress step
        if case in ["Start","Restart"]:
            progress_start = event.getProgressList()[-1][1][0]
            progress_end = event.getProgressList()[-1][1][1]
            #self.getSimulator().saveLog(" REPORT: event in?: "+str(event in self.getSimulator().getEventQueue()[progress_start])) 
            if event in self.getSimulator().getEventQueue()[progress_start]:
                self.getSimulator().getEventQueue()[progress_start] = [x for x in self.getSimulator().getEventQueue()[progress_start] if x != event]
            #self.getSimulator().saveLog(" REPORT: event in?: "+str(event in self.getSimulator().getEventQueue()[progress_start])) 
                
            if not progress_end in self.getSimulator().getEventQueue():
                self.getSimulator().getEventQueue()[progress_end] = []
            self.getSimulator().getEventQueue()[progress_end].append(event) # end of the progress step: suspend/complete
      
            if event.getSuspendedPredecessor() != None:
                if event.getSuspendedPredecessor().getProgressList()[-1][1][1] < progress_end: 
                    #self.getSimulator().saveLog(" REPORT: scheduling suspended predecessor: "+str(event.getSuspendedPredecessor().getName())) 
                    progress_step = (progress_start,progress_end)
                    event.getSuspendedPredecessor().getProgressList().append((event.getSuspendedPredecessor().getResource(),progress_step))
                    if event.getSuspendedPredecessor().getName() == "Machine Processing":
                        event.getSuspendedPredecessor().getResource().getProgressList().append((event.getSuspendedPredecessor(),progress_step))
                    if not progress_step[1] in self.getSimulator().getEventQueue():
                        self.getSimulator().getEventQueue()[progress_step[1]] = []
                        
                    self.getSimulator().getEventQueue()[progress_step[1]].append(event.getSuspendedPredecessor())
        
       ########################################   
        
       # Check precedences
        if event.getType() != "Logistical":    
            for successor_type,precedence_type in event.getEventType().getSuccessorDict().items():
                create_successor = False; 
                if self.getSimulator().getTime() in debugtimes:
                    self.getSimulator().saveLog("REPORT: case "+case+", successor_type "+str(successor_type.getName())+", pred_type: "+precedence_type)
                    
                if (case == "Start" and precedence_type == "Simultaneous Start") or (case == "Complete" and precedence_type == "Finish to Start"):
                    create_successor = True
                if (case == "Start" or case == "Restart") and (precedence_type == "CompletionRatio Start"): 
                    create_successor = True

                if create_successor:
                    successor_event = ExecEvent(None,None,successor_type)

                    if self.getSimulator().getTime() in debugtimes:
                        self.getSimulator().saveLog("REPORT: **** successor_event "+successor_event.getName()+"("+str(successor_event.getID())+")")
                    self.applyPrecedence(event,successor_event,successor_type)
       
                    if ((successor_event.getEquipment() == None) or (successor_event.getResource() == None)) and (successor_event.getName() != "Machine Processing" and successor_event.getName() != "Machine Unloading") : 
                        # ML/MU (resource) 
                       
                        self.getSimulator().getEventQueue()["Pending"].append(successor_event)
                        if self.getSimulator().getTime() in debugtimes:
                            self.getSimulator().saveLog("REPORT: succcessor pending ")
                                
                    else: # now progress step can be determined
                        if successor_event.getToLocation()== None:
                            decision_type = 'Select Destination'
                            if successor_event.getName() in self.getAlgorithmSetting():
                                if decision_type in self.getAlgorithmSetting()[successor_event.getName()]:
                                    algname = self.getAlgorithmSetting()[successor_event.getName()][decision_type]
                                    #self.getSimulator().saveLog("REPORT: **** finding destination of event "+successor_event.getName()+", algname: "+algname)
                                    algfunction = self.getProductionAlgManager().getDecisionAlgorithms()[decision_type][algname]
                                    alg_return = algfunction(successor_event)
                                    successor_event.setToLocation(alg_return.getInputBuffer())
                                    
                        successor_event.sampleProcessTime(self); proctime = successor_event.getProcessTime()
                        
                        if precedence_type == "CompletionRatio Start":
                            #self.getSimulator().saveLog("REPORT: completion ratio!!! ")
                          
                            totalprogress = 0; 
                                
                            for progress_id in range(len(event.getProgressList())):
                                res,progress = event.getProgressList()[progress_id]

                                curr_progress = totalprogress+(progress[1]-progress[0])
                                #self.getSimulator().saveLog("REPORT: event process time: "+str(event.getProcessTime()))
                                #self.getSimulator().saveLog("REPORT: proctime: "+str(proctime))
                                #self.getSimulator().saveLog("REPORT: curr_progress: "+str(curr_progress))
                                
                                if event.getProcessTime() - curr_progress > proctime:
                                    totalprogress+=(progress[1]-progress[0])    
                                else: #event.getProcessTime() - curr_progress <= proctime:  (event.getProcessTime() - proctime) - totalprogress
                                    successortime = progress[0] + (event.getProcessTime() - proctime) - totalprogress
                                    #self.getSimulator().saveLog("REPORT: successor handle time in completion ratio: "+str(successortime))
                                    if progress[1] in self.getSimulator().getEventQueue():
                                        self.getSimulator().getEventQueue()[progress[1]].remove(event) 
                                        
                                    #self.getSimulator().saveLog("REPORT: current progresss step: "+str(progress))
                                    event.getProgressList()[progress_id] = (res,(progress[0],successortime))
                                    
                                    if event.getName() == "Machine Processing":
                                        
                                        for resprogress_id in range(len(res.getProgressList())):
                                            myevent,resprogress = res.getProgressList()[resprogress_id]
                                            if resprogress[0] == progress[0] and resprogress[1] == progress[1]:
                                                if myevent == event:
                                                    res.getProgressList()[resprogress_id]=(event,(progress[0],successortime))
                                                    break
                                                    
                                    #self.getSimulator().saveLog("REPORT: new progresss step: "+str((progress[0],successortime)))
                                    if not successortime in self.getSimulator().getEventQueue():
                                        self.getSimulator().getEventQueue()[successortime] = []
                                    if not successor_event in self.getSimulator().getEventQueue()[successortime]:
                                        self.getSimulator().getEventQueue()[successortime].append(successor_event)
                                        #self.getSimulator().saveLog("REPORT: successor event : "+successor_event.getName()+" scheduled "+str(successortime))
                                    successor_event.setSuspendedPredecessor(event)
                                    event.setSuspendedSuccessor(successor_event)
                                    #self.getSimulator().saveLog("REPORT: CompletionRatio Start successor and predecessor added to check time: "+str(successortime))               
                                    break
                            if event.getSuspendedSuccessor() == None: # drop the items if successor event is not scheduled. 
                                for item in successor_event.getItems():
                                    item.setReservedEvent(None)
                                    


                        else: 
                            if successor_event.getEventType().isPreemptable():
                                progress_step = (self.getSimulator().getTime(),min(self.getSimulator().getTime()+proctime,self.getCurrentShiftEnd()))
                                successor_event.getProgressList().append((successor_event.getResource(),progress_step))
                                if successor_event.getName() == "Machine Processing":
                                    successor_event.getResource().getProgressList().append((successor_event,progress_step))
                                self.getSimulator().getEventQueue()[successor_event.getProgressList()[-1][1][0]].append(successor_event) # start of progress step
                                if self.getSimulator().getTime() in debugtimes:
                                    self.getSimulator().saveLog(" REPORT: successor: "+str(successor_event.getName())+", prog_step "+str(progress_step)) 
                                    self.getSimulator().saveLog("REPORT: succcessor progress step "+str(progress_step))
                                    
                            else: # non-prememptable event does not fit to the remaining time in current shift.  
                                if self.getSimulator().getTime()+proctime > self.getCurrentShiftEnd():
                                    for decision_type in successor_event.getEventType().getDecisionsDict()["Pending"]:
                                        if decision_type == "Assign Equipment":
                                            successor_event.getEquipment().setIdle(True)
                                            successor_event.setEquipment(None)
                                        if decision_type == "Assign Resource":
                                            successor_event.getResource().setIdle(True)
                                            successor_event.setResource(None)
      
                                    self.getSimulator().getEventQueue()["Pending"].append(successor_event)
                                else:
                                    progress_step = (self.getSimulator().getTime(),self.getSimulator().getTime()+proctime)
                                    successor_event.getProgressList().append((successor_event.getResource(),progress_step))
                                    if successor_event.getName() == "Machine Processing":
                                        successor_event.getResource().getProgressList().append((successor_event,progress_step))
                                    self.getSimulator().getEventQueue()[successor_event.getProgressList()[-1][1][0]].append(successor_event) #start of progress step
                                    if self.getSimulator().getTime() in debugtimes:
                                        self.getSimulator().saveLog("REPORT: succcessor progress step "+str(progress_step))
     
        else:
            successor_event = event.getSuccessor()

            if case == "Complete":
                if successor_event != "Logistical":
                    progress_start = successor_event.getProgressList()[-1][1][0]
                    if not progress_start in self.getSimulator().getEventQueue():
                        self.getSimulator().getEventQueue()[progress_start] = []
                            
                    if not successor_event in self.getSimulator().getEventQueue()[progress_start]:   
                        self.getSimulator().getEventQueue()[progress_start].append(successor_event) # start of the progress step: start/restart

                    for log_event in successor_event.getLogisticalEvents():
                        successor_event.getLogisticalEvents().remove(log_event)
                        #self.getSimulator().saveLog("REPORT: >>> logistical event "+log_event.getName()+" is removed from event "+successor_event.getName())
                        
                else:
                    progress_end = successor_event.getProgressList()[-1][1][1]
                    if not progress_end in self.getSimulator().getEventQueue():
                        self.getSimulator().getEventQueue()[progress_end] = []
                        
                    if not successor_event in self.getSimulator().getEventQueue()[progress_end]:   
                        self.getSimulator().getEventQueue()[progress_end].append(successor_event) 
    
                    #self.getSimulator().saveLog("REPORT: end of next logistical event "+successor_event.getName()+" is scheduled")
                    
       

        if self.getSimulator().getTime() in debugtimes:
            self.getSimulator().saveLog("REPORT: ______________________________________________________________________")

        if self.getSimulator().getTime() in debugtimes:
            oprseq = []
            if len(event.getItems()) > 0:
                oprseq = event.getItems()[0].getDemand().getFinalProduct().getOperationSequences()[event.getItems()[0].getDemand().getID()]
                self.getSimulator().saveLog("REPORT: event : "+str(event.getName())+"("+str(event.getID())+"), items "+str(len(event.getItems()))+", active opr none? "+("No item " if len(event.getItems())==0 else str(event.getItems()[0].getActiveOperation()== None))+" event loc "+event.getLocation().getName()+", item oprs "+str([str(o.isCancelled())+"--"+str(o.isFinished())+"--"+str(o.getName()) for o in oprseq])+", tot.prog: "+str(event.getTotalProgress())+", p: "+str(event.getProcessTime())+", case: "+case)
     
        return
###############################################################################################################################################
    def applyPrecedence(self,event,successor_event,successor_type):

        precedenceinfo = event.getEventType().getPrecendenceDict()[successor_type.getName()]

        # setEquipment
        if 'Equipment' in precedenceinfo: #  TL->TT, TT->TU, MS->Ml, ML->Proc
            successor_event.setEquipment(event.getEquipment())
        if 'FromLocation->Equipment' in precedenceinfo: # Proc->MU
            successor_event.setEquipment(event.getFromLocation())

        if 'Processor' in precedenceinfo:

            event_machine = event.getFromLocation() if isinstance(event.getFromLocation(),Machine) else event.getFromLocation().getMachine()

            if event in event_machine.getProcessMatch():
                processor = event_machine.getProcessMatch()[event]
                del event_machine.getProcessMatch()[event]
                event_machine.getProcessMatch()[successor_event] = processor
                #self.getSimulator().saveLog("REPORT: processor moved to successor..")

        # setResource 
        if 'Resource' in precedenceinfo: # TL->TT,  TT->TU 
            successor_event.setResource(event.getResource())
            event.getResource().setIdle(False)
        if 'ToLocation->Resource' in precedenceinfo: # ML->Proc
            successor_event.setResource(event.getToLocation())

        # setItems: TL->TT, MS->Ml, ML->Proc, Proc->MU
        if 'Items' in precedenceinfo:
            for item in event.getItems():
                if item.getReservedEvent() == event:
                    item.setReservedEvent(successor_event)
                successor_event.getItems().append(item)

        # set FromLocation: 
        if "FromLocation" in precedenceinfo: # TL->TT, MS->ML, Proc->MU
            successor_event.setFromLocation(event.getFromLocation())
        if 'ToLocation->FromLocation' in precedenceinfo: # ML -> Proc
            successor_event.setFromLocation(event.getToLocation())
        if 'Equipment->FromLocation' in precedenceinfo: # TT->TU
            successor_event.setFromLocation(event.getEquipment())

                        
        # set ToLocation:    
        if 'ToLocation' in precedenceinfo: # TT->TU
            successor_event.setToLocation(event.getToLocation())
        if 'FromLocationMachine->ToLocation' in precedenceinfo:  # MS->ML
            successor_event.setToLocation(event.getFromLocation().getMachine())
        if 'FromLocationOutput->ToLocation' in precedenceinfo: # Proc->MU
            successor_event.setToLocation(event.getFromLocation().getOutputBuffer())

        #if self.getSimulator().getTime() > 475:
            #self.getSimulator().saveLog("REPORT: event "+str(event.getName())+", eq none? "+str(event.getEquipment() == None)+", res none? "+str(event.getResource() == None)+", fl none? "+str(event.getFromLocation() == None))
            #self.getSimulator().saveLog("REPORT: succcessor created "+str(successor_event.getName())+"("+str(successor_event.getID())+")"+", eq none? "+str(successor_event.getEquipment() == None)+", res none? "+str(successor_event.getResource() == None)+", fl none? "+str(successor_event.getFromLocation() == None))


        return
                      
###############################################################################################################################################
    def determineProgressCase(self,event):
        
        case = "Handle" # default   
        
        if event.getTotalProgress() > 0:
            if (self.getSimulator().getTime() == event.getProgressList()[-1][1][0]):
                case = "Start" if len(event.getProgressList()) == 1 else "Restart"     
            if (self.getSimulator().getTime() == event.getProgressList()[-1][1][1]):
                if event.getTotalProgress() < event.getProcessTime():
                    case = "Suspend"
                else:
                    case = "Complete"

        return case
#######################################################################################################################################
    def makeCaseDecisions(self,event,case,debugtimes):

        logistical = True

         # MAKE NECESSARY DECISIONS...
        casesuccess = True; success_decisions = [] 
            
        if case in event.getEventType().getDecisionsDict():
            for decision_type in event.getEventType().getDecisionsDict()[case]:

                algname = self.getAlgorithmSetting()[event.getName()][decision_type]
                
                #if self.getSimulator().getTime() > 475:
                #    self.getSimulator().saveLog("REPORT: decision_type "+decision_type+", algname: "+algname)
                algfunction = self.getProductionAlgManager().getDecisionAlgorithms()[decision_type][algname]
                
                alg_return = algfunction(event)
                if self.getSimulator().getTime() in debugtimes:
                    self.getSimulator().saveLog("REPORT: event : "+str(event.getName())+" alg_return  none? "+str(alg_return == None))
                
                if alg_return!= None:
                    if decision_type == "Select Items":   # TL/TU/MS (handle)
                        #self.getSimulator().saveLog("REPORT: "+case+": "+", select items: "+str(len(alg_return)))
                        for item in alg_return:
                            event.getItems().append(item)  
                 
                    if decision_type == "Assign Equipment":  # TL/MS (handle), Proc(restart)        
                        if event.getName() == "Machine Setup":
                            event.getFromLocation().getMachine().getProcessMatch()[event] = alg_return # return is a processor of the equipment
                        else:
                            if event.getName() == "Machine Processing":
                                event.getFromLocation().getProcessMatch()[event] = alg_return # return is a processor of the equipmen
                                #self.getSimulator().saveLog("REPORT: "+case+": "+", processor assigned: "+str(alg_return)+", "+event.getName()+"-"+str(event.getID()))
                            else:
                                #self.getSimulator().saveLog("REPORT: "+case+": "+", equipment assigned: "+str(alg_return.getName())+", idle "+str(alg_return.isIdle())+", "+event.getName()+"-"+str(event.getID()))
                                event.setEquipment(alg_return) # process: inserts this start into progress dict of equip
                                if event.getName() == "Trailer Loading":
                                    event.setToLocation(alg_return) 
                                alg_return.setIdle(False)

                        # Important: For Outsourced, how to handle operator requirement for Machine Loading and Unloading (Relax this requirement!)?
                       
                    if decision_type == "Assign Resource": # TL/MS/ML/MU (handle), ML/MU (resart)
                        event.setResource(alg_return) 
                        alg_return.setIdle(False)
                        if self.getSimulator().getTime() in debugtimes:
                            self.getSimulator().saveLog("REPORT: "+case+" : "+", resource assigned: "+str(alg_return.getName())+", idle "+str(alg_return.isIdle())+", "+event.getName()+"-"+str(event.getID()))

                    success_decisions.append(decision_type)
                else:
                    casesuccess = False # only can happen for assign equipment/resource
                    if self.getSimulator().getTime() in debugtimes:
                        self.getSimulator().saveLog("REPORT: no success in handling decision type: "+decision_type)
                    break 
        if not casesuccess: # backtrack the decisions
            #if self.getSimulator().getTime() >= 2400:
                #self.getSimulator().saveLog("REPORT: no success in handling..")
            for decision_type in success_decisions:
                if decision_type == "Assign Equipment":
                    if event.getType() == "Processing":
                        if event in event.getEquipment().getProcessMatch():
                               del event.getEquipment().getProcessMatch()[event]
                    else:
                        event.getEquipment().setIdle(True)
                        event.setEquipment(None)  
                if decision_type == "Assign Resource":
                    event.getResource().setIdle(True)
                    event.setResource(None)
        else:
            if logistical:
                if event.getName() != "Machine Processing":
                    equipment_onlocation = True; resource_onlocation = True
                    
                    for decision_type in success_decisions:
                        if decision_type == "Assign Equipment":
                            if event.getName() != "Machine Setup":
                                equipment_onlocation = (event.getEquipment().getLocation() == event.getLocation())
                 
                        if decision_type == "Assign Resource":
                            resource_onlocation =  (event.getResource().getLocation() == event.getLocation())

                    if self.getSimulator().getTime() in debugtimes:
                        self.getSimulator().saveLog("REPORT: event : "+event.getName()+"("+str(event.getID())+")"+", res on loc? "+str(resource_onlocation)+", equip on loc? "+str(equipment_onlocation)) 
                    
                    #if not resource_onlocation and not equipment_onlocation:
                        #self.getSimulator().saveLog("REPORT:---------- decisions with success: "+str(success_decisions))
                        #self.getSimulator().saveLog("REPORT:---------- event location: "+event.getLocation().getName())
                        #self.getSimulator().saveLog("REPORT:---------- event resource location: "+event.getResource().getLocation().getName())
                        #self.getSimulator().saveLog("REPORT:---------- event Equipment location: "+event.getEquipment().getLocation().getName())
                   

                    if not equipment_onlocation:
                        bring_equipment = ExecEvent(event.getEquipment().getLocation(),event.getLocation(),self.getEventTypes()["Bring Equipment"])
                        bring_equipment.sampleProcessTime(self)
                    
                        operator_move = None
                        if event.getResource().getLocation() != event.getEquipment().getLocation():
                            operator_move = ExecEvent(event.getResource().getLocation(),event.getEquipment().getLocation(),self.getEventTypes()["Operator Move"])
                            if self.getSimulator().getTime() in debugtimes:
                                self.getSimulator().saveLog("REPORT: Operator move event (to bring equipment) created.." )
                            operator_move.setEquipment(None) 
                            operator_move.setResource(event.getResource())
                            
                            operator_move.sampleProcessTime(self)

                            if self.getSimulator().getTime()+operator_move.getProcessTime()+bring_equipment.getProcessTime() > self.getCurrentShiftEnd()-1:
                                # operator move and bring equipment cannot be done in current shift, backtrack all decisions..
                                self.getSimulator().saveLog("REPORT: ******** Operator move + bring equipment) cannot be finished in same shift" )
                                self.getSimulator().saveLog("REPORT: ******** Operator move + bring equipment) cannot be finished in same shift" )
                                casesuccess = False
                                for decision_type in success_decisions:
                                    if decision_type == "Assign Equipment":
                                        if event.getType() == "Processing":
                                            if event in event.getEquipment().getProcessMatch():
                                               del event.getEquipment().getProcessMatch()[event]
                                            else:
                                                event.getEquipment().setIdle(True)
                                                event.setEquipment(None)  
                                    if decision_type == "Assign Resource":
                                        event.getResource().setIdle(True)
                                        event.setResource(None)
                                    if decision_type == 'Select Items':
                                        for item in event.getItems():
                                            item.setReservedEvent(None) 
                                        event.getItems().clear()
                        

                                #if event.getEquipment() == None and event.getType() != "Setup":
                                self.getSimulator().saveLog("REPORT: ******** success decisions: "+str(success_decisions))
                                    
                                    
                                        
                                        
                                        
                                return casesuccess
                                
                            
                            if self.getSimulator().getTime() in debugtimes:
                                self.getSimulator().saveLog("REPORT: Operator move process time: "+str(operator_move.getProcessTime()))
                            progress_step = (self.getSimulator().getTime(),min(self.getSimulator().getTime()+operator_move.getProcessTime(),self.getCurrentShiftEnd()))
                            operator_move.getProgressList().append((operator_move.getResource(),progress_step))
                            if self.getSimulator().getTime() in debugtimes:
                                self.getSimulator().saveLog("REPORT: Operator move progress step: "+str(progress_step))
                            if not progress_step[1] in self.getSimulator().getEventQueue():
                                self.getSimulator().getEventQueue()[progress_step[1]] = []
                            # operator move is scheduled for its completion.
                            self.getSimulator().getEventQueue()[progress_step[1]].append(operator_move)
                            event.getLogisticalEvents().append(operator_move)
                        
                        
                        bring_equipment.setEquipment(event.getEquipment()) 
                        bring_equipment.setResource(event.getResource())
                       
                        bring_equipment.setSuccessor(event)
                        

                        progress_step = None
                        
                        if operator_move != None:
                            operator_move.setSuccessor(bring_equipment)
                            progress_step = (self.getSimulator().getTime()+operator_move.getProcessTime(),min(self.getSimulator().getTime()+operator_move.getProcessTime()+bring_equipment.getProcessTime(),self.getCurrentShiftEnd()))
                        else:
                            progress_step = (self.getSimulator().getTime(),min(self.getSimulator().getTime()+bring_equipment.getProcessTime(),self.getCurrentShiftEnd()))
                            
                        if self.getSimulator().getTime() in debugtimes:
                            self.getSimulator().saveLog("REPORT: bring_equipment process time: "+str(bring_equipment.getProcessTime())+", prog step "+str(progress_step)+" Opr Move none? "+str(operator_move == None))
    
                        bring_equipment.getProgressList().append((bring_equipment.getResource(),progress_step))

                        if operator_move == None:
                            if not progress_step[1] in self.getSimulator().getEventQueue():
                                self.getSimulator().getEventQueue()[progress_step[1] ] = []
                            self.getSimulator().getEventQueue()[progress_step[1]].append(bring_equipment)
                        event.getLogisticalEvents().append(bring_equipment)
                        
                        
                    if not resource_onlocation and equipment_onlocation: 
                        #self.getSimulator().saveLog("REPORT: >>>>>>>>> event location: "+event.getLocation().getName())
                        #self.getSimulator().saveLog("REPORT: >>>>>>>>> event resource location: "+event.getResource().getLocation().getName())
                        #self.getSimulator().saveLog("REPORT: >>>>>>>>> event Equipment location: "+event.getEquipment().getLocation().getName())
        
                        operator_move = ExecEvent(event.getResource().getLocation(),event.getLocation(),self.getEventTypes()["Operator Move"])
                        #self.getSimulator().saveLog("REPORT: Operator move event created.." )
                        operator_move.setEquipment(None) 
                        operator_move.setResource(event.getResource())
                        operator_move.setSuccessor(event)
                        operator_move.sampleProcessTime(self)
                        #self.getSimulator().saveLog("REPORT: Operator move process time: "+str(operator_move.getProcessTime()))
                        progress_step = (self.getSimulator().getTime(),min(self.getSimulator().getTime()+operator_move.getProcessTime(),self.getCurrentShiftEnd()))
                        operator_move.getProgressList().append((operator_move.getResource(),progress_step))
                        #self.getSimulator().saveLog("REPORT: Operator move progress step: "+str(progress_step))
                        if not progress_step[1] in self.getSimulator().getEventQueue():
                            self.getSimulator().getEventQueue()[progress_step[1]] = []
                        # operator move is scheduled for its completion.
                        self.getSimulator().getEventQueue()[progress_step[1]].append(operator_move)
                        event.getLogisticalEvents().append(operator_move)
                    

        return casesuccess

############################################################################################################################
    def makeCompletionUpdates(self,event,debugtimes):

      # update execution data of event...
        progrss_steps = ""; step_id = 0
        for res,prstep in event.getProgressList():
            progrss_steps+=("" if step_id == 0 else "~")+str(prstep[0])+"-"+str(prstep[1])
            step_id+=1
                
        ev_items = ""; item_id = 0
        for item in event.getItems():
            ev_items+=("" if item_id == 0 else "~")+str(item.getID())
            item_id+=1

        trailer_unloading_wait = ""
        machine_unloading_wait = ""
        event_start = event.getProgressList()[0][1][0]

        if event.getName() == "Machine Loading":
            completion_time = self.UnloadingCompletionTimes.pop(event.getFromLocation(), None)
            if completion_time is not None:
                trailer_unloading_wait = event_start-completion_time

        if event.getName() == "Trailer Loading":
            completion_time = self.UnloadingCompletionTimes.pop(event.getFromLocation(), None)
            if completion_time is not None:
                machine_unloading_wait = event_start-completion_time
                
        execution_data = {"EventName":event.getName(),"EventID":event.getID(),"ProgressSteps":progrss_steps,"Items":ev_items,"WaitAfterTrailerUnloading":trailer_unloading_wait,"WaitAfterMachineUnloading":machine_unloading_wait,"Resource":("-" if event.getResource() == None else event.getResource().getName()),"Equipment":("-" if event.getEquipment() == None else event.getEquipment().getName()),"Location":event.getLocation().getName(),"SimTime":self.getSimulator().getTime(),"Date":self.getSimulator().getRealTime()}  
        self.getSimulator().getExecutionData().append(execution_data)

        if event.getName() == "Trailer Unloading":
            self.UnloadingCompletionTimes[event.getToLocation()] = self.getSimulator().getTime()

        if event.getName() == "Machine Unloading":
            self.UnloadingCompletionTimes[event.getToLocation()] = self.getSimulator().getTime()

        if event.getResource()!= None: 
            if isinstance(event.getResource(),Operator):
                # "EntityName","EntityID","Time","LocationName","LocationID"
                location_data = {"EntityName":event.getResource().getName(),"EntityID":event.getResource().getID(),"Time":self.getSimulator().getTime(),"LocationName":event.getResource().getLocation().getName(),"LocationID": (event.getResource().getLocation().getID() if event.getResource().getLocation()!= None else "-")}  
                self.getSimulator().getLocationData().append(location_data)
               

     # update execution data of event...

    # update operation status in case machine processing
        if event.getName() == "Machine Processing":
            
            if len(event.getItems()) > 0:
                oprseq = event.getItems()[0].getDemand().getFinalProduct().getOperationSequences()[event.getItems()[0].getDemand().getID()]
                #for opr in oprseq:
                    #self.getSimulator().saveLog("REPORT: opr: "+opr.getName()+", can?"+str(opr.isCancelled())+", fin?"+str(opr.isFinished()))
                    
                if event.getItems()[0].getActiveOperation() != None:
                    #self.getSimulator().saveLog("REPORT: >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Finished!!!!!")
                    if self.getSimulator().getTime() in debugtimes:
                        for e in self.getSimulator().getEventQueue()[self.getSimulator().getTime()]:
                             self.getSimulator().saveLog(" REPORT: event: "+str(e.getName())+"("+str(e.getID())+")-["+(str(e.getItems()[0].getID()) if len(e.getItems())>0 else '')+"-"+(str(e.getItems()[-1].getID()) if len(e.getItems())>0 else '')+"]"+", active opr none? "+("No item " if len(e.getItems())==0 else (e.getItems()[0].getActiveOperation().getName() if e.getItems()[0].getActiveOperation()!= None else "No act opr"))+", loc "+(e.getLocation().getName() if event.getLocation() == None else "No loc")+", tot.prog: "+str(e.getTotalProgress())+", p: "+str(e.getProcessTime())+", succ event? none "+str(e.getSuspendedSuccessor() == None)) 

                   
                    #self.getSimulator().saveLog("REPORT: demand of removed one: "+str(event.getItems()[0].getDemand().getID()))   
                    event.getItems()[0].getActiveOperation().setFinished()
                    if self.getSimulator().getTime() in debugtimes:
                        for e in self.getSimulator().getEventQueue()[self.getSimulator().getTime()]:
                            if len(e.getItems())>0:
                                self.getSimulator().saveLog("REPORT: demand: "+str(e.getItems()[0].getDemand().getID()))   
                            self.getSimulator().saveLog(" REPORT: event: "+str(e.getName())+"("+str(e.getID())+")-["+(str(e.getItems()[0].getID()) if len(e.getItems())>0 else '')+"-"+(str(e.getItems()[-1].getID()) if len(e.getItems())>0 else '')+"]"+", active opr none? "+("No item " if len(e.getItems())==0 else (e.getItems()[0].getActiveOperation().getName() if e.getItems()[0].getActiveOperation()!= None else "No act opr"))+", loc "+(e.getLocation().getName() if event.getLocation() == None else "No loc")+", tot.prog: "+str(e.getTotalProgress())+", p: "+str(e.getProcessTime())+", succ event? none "+str(e.getSuspendedSuccessor() == None)) 

                            
                    
                if event in event.getFromLocation().getProcessMatch():
                    del event.getFromLocation().getProcessMatch()[event]
                    #self.getSimulator().saveLog("REPORT: processor match removed..")   

    # update operation status in case machine processing

        if event.getType() == "Transport":
            event.getEquipment().setLocation(event.getToLocation().getLocation())
            event.getResource().setLocation(event.getToLocation().getLocation())
            
        if event.getName() == "Operator Move":
            #self.getSimulator().saveLog("REPORT: event resource set location: "+str(event.getToLocation().getName()))   
            event.getResource().setLocation(event.getToLocation())
            #self.getSimulator().saveLog("REPORT: event resource  location: "+str(event.getResource().getLocation().getName()))   

        if event.getName() == "Bring Equipment":
            #self.getSimulator().saveLog("REPORT: event equip&resource set location: "+str(event.getToLocation().getName()))
            #self.getSimulator().saveLog("REPORT: successor event "+str(event.getSuccessor().getName())+"("+str(event.getSuccessor().getID())+")")   
            event.getResource().setLocation(event.getToLocation())
            event.getEquipment().setLocation(event.getToLocation())
            
            
                            
        if event.getType() in ["Loading","Unloading"]:

            #self.getSimulator().saveLog("REPORT: event : "+event.getName()+", event items: "+("None" if len(event.getItems()) == 0 else (str(event.getItems()[0].getID())+"-"+str(event.getItems()[-1].getID()))) )
            #self.getSimulator().saveLog("REPORT: event : from location items: "+("None" if len(event.getFromLocation().getItems()) == 0 else str(event.getFromLocation().getItems()[0].getID())+"-"+str(event.getFromLocation().getItems()[-1].getID()))  )
            
            for item in event.getItems():
                #if item.getReservedEvent() != None:
                    #if event.getItems()[0] == item:
                    #    self.getSimulator().saveLog("REPORT: item reserved to event: "+str(item.getReservedEvent().getName())+"("+str(item.getReservedEvent().getID())+")"+", it: "+str(item.getID()))   
                if item.getReservedEvent() == event:
                    item.setReservedEvent(None)
                    #self.getSimulator().saveLog("REPORT: event item reservation reset: "+str(event.getName())+", it: "+str(item.getID()))   
                event.getFromLocation().getItems().remove(item)
                event.getToLocation().getItems().append(item)

            if isinstance(event.getFromLocation(),Buffer):
                fromloc = event.getFromLocation()
                buffer_data = {"BufferName":fromloc.getName(),"Machine": fromloc.getMachine().getName() if fromloc.getMachine()!= None else "Central Inventory","Time":self.getSimulator().getTime(),"No.Items":len(fromloc.getItems())}  
                self.getSimulator().getBufferData().append(buffer_data)
            if isinstance(event.getToLocation(),Buffer): 
                toloc = event.getToLocation()
                buffer_data = {"BufferName":toloc.getName(),"Machine": toloc.getMachine().getName() if toloc.getMachine()!= None else "Central Inventory","Time":self.getSimulator().getTime(),"No.Items":len(toloc.getItems())}  
                self.getSimulator().getBufferData().append(buffer_data)

                
            if event.getName() == "Machine Unloading":
                # TU:Inputbuffer triggers Machine Setup
                if event.getFromLocation().getName() != "OUT - Outsourced activity_(OUT - Outsourced)":
                    event.getFromLocation().getInputBuffer().setPendingEvent(None)
                    event.getFromLocation().getInputBuffer().generateEvent() # MU: Inputbuffer triggers Machine Setup
              
                #self.getSimulator().saveLog("REPORT: event generation triggered at: "+event.getFromLocation().getInputBuffer().getName())
                
            if event.getName() == "Trailer Loading":
                
                if event.getFromLocation().getPendingEvent() == event:
                    event.getFromLocation().setPendingEvent(None)
                    event.getFromLocation().generateEvent() # TL: Outputbuffer triggers Trailer loading
                
         
            if event.getType() == "Unloading":         # TU:Inputbuffer triggers Machine Setup
                #self.getSimulator().saveLog("REPORT: event to generate at: "+event.getToLocation().getName())
                event.getToLocation().generateEvent()  # MU: Outputbuffer triggers Trailer loading
                #if event.getItems()[0].getActiveOperation() == None:
                #    self.getSimulator().saveLog("REPORT: Operations of the current item batch is completed!")
                event.getEquipment().setIdle(True)

        if event.getType() != "Logistical": 
            event.getResource().setIdle(True)
        
        # remove the event from queue
        if event.getProgressList()[-1][1][1] in self.getSimulator().getEventQueue():
            if event in self.getSimulator().getEventQueue()[event.getProgressList()[-1][1][1]]:
                self.getSimulator().getEventQueue()[event.getProgressList()[-1][1][1]].remove(event)
 
  
        return 
#######################################################################################################################################################

#########################################################################################################################
    def writeData(self):

        event_df = pd.DataFrame(columns=["EventName","EventID","ProgressSteps","Items","WaitAfterTrailerUnloading","WaitAfterMachineUnloading","Resource","Equipment","Location","SimTime","Date"])

        for eventdata in self.getSimulator().getExecutionData():
            event_df.loc[len(event_df)] = eventdata

        
        event_df.to_csv("EventExecutionData.csv",index = False)

        ######################################################################
        ## TO DO: Bryan ( Implementing the utilization ratio of machines

        utilization_data = []

        for eventname in event_df["EventName"].unique():
            if eventname == "Machine Processing":
                eventsub_df = event_df[event_df["EventName"] == eventname]
                for resource in eventsub_df["Resource"].unique():
                    eventmach_df = eventsub_df[eventsub_df["Resource"] == resource]
                    machine = None
                    
                    for res in self.getResources():
                        if res.getName() == resource:
                            machine = res
                            break

                    processtime = 0
                    availabletime = 0
                    if machine != None: 
                        for event,progress in machine.getProgressList():
                            if event.getName() == "Machine Processing":
                                processtime += progress[1]-progress[0]

                        available_shifts = set(machine.getAvailableShifts())
                        for simtime in range(self.getSimulator().getTime()):
                            realtime = self.getSimulator().checkRealTime(simtime)

                            if realtime.weekday() >= self.getSimulator().weekdays:
                                continue

                            if realtime.hour < 8:
                                shift = 3
                            elif realtime.hour < 16:
                                shift = 1
                            else:
                                shift = 2

                            if shift in available_shifts:
                                availabletime += 1

                        utilization_data.append({
                            "Machine": machine.getName(),
                            "ProcessTime": processtime,
                            "AvailableTime": availabletime,
                            "Utilization": (
                                processtime / availabletime
                                if availabletime > 0
                                else 0
                            )
                        })

        pd.DataFrame(utilization_data).to_csv("MachineUtilizationData.csv", index=False)

                    

        ## TO DO: Bryan ( Implementing the utilization ratio of machines
        ######################################################################


        location_df = pd.DataFrame(columns=["EntityName","EntityID","Time","LocationName","LocationID"])

        for locdata in self.getSimulator().getLocationData():
            location_df.loc[len(location_df)] = locdata

        location_df.to_csv("LocationData.csv",index = False)


        buffer_df = pd.DataFrame(columns=["BufferName","BufferID","Machine","Time","No.Items"])

      
        for bufferdata in self.getSimulator().getBufferData():
            buffer_df.loc[len(buffer_df)] = bufferdata

        
        buffer_df.to_csv("BufferData.csv",index = False)

        return
        
#########################################################################################################################
    def writeDataTBRMOutPut(self,myround):


        TBRM_df= pd.DataFrame(columns=["ID","Product","Product/ID","Quantity To Produce","Deadline","Work Orders/Work Center","Processing Machine","Work Orders/Work Center/ID","Work Orders/Expected Duration","Work Orders/Start(ORG)","Work Orders/Start","Work Orders/End(ORG)","Work Orders/End","Work Orders/Status","Scheduled"])

        currentdate =  datetime.now()
        currentdate = currentdate-timedelta(days = 2)
        startday = datetime(currentdate.year, currentdate.month, currentdate.day)

        try: 
            for prodordid,prodorder in self.getProductionOrders().items():
            
                oprsequence = prodorder.getFinalProduct().getOperationSequences()[prodorder.getID()]

                
                oprid = 0
                for myopr in oprsequence:
                    myorddata = None
                    
                    mystrt = myopr.getStart()
                    mycomp = myopr.getCompletion()
                    status = ("Finished" if mycomp!= None else ("In Progress" if mystrt!= None else "To Do"))

                    if myopr.isCancelled():
                        status = "Cancelled"

                    status = ("Scheduled" if myopr.getProcessMachine()!= None else status)

                    #self.getSimulator().saveLog("REPORT: mystrt "+str(mystrt)+", mycomp "+str(mycomp))
                    
                    if  isinstance(mystrt,int) and mystrt!= None :
                        mystrt = startday+timedelta(minutes = mystrt)

                    if isinstance(mycomp,int) and mycomp!= None :
                         mycomp = startday+timedelta(minutes = mycomp)
                        
                    
                    if oprid == 0:
                        myorddata = {"ID":prodorder.getID(),"Product":prodorder.getFinalProduct().getName(),"Product/ID":prodorder.getFinalProduct().getID(),"Quantity To Produce":prodorder.getQuantity(),"Deadline":prodorder.getDeadline(),"Work Orders/Work Center":myopr.getName(),"Work Orders/Work Center/ID":myopr.getAlternativeResources()[0].getID(),"Processing Machine":(myopr.getProcessMachine().getName() if myopr.getProcessMachine()!= None else "-"),"Work Orders/Expected Duration":myopr.getRandVar().sampleValue(),"Work Orders/Start(ORG)":myopr.getOriginalStart(),"Work Orders/Start":mystrt,"Work Orders/End(ORG)":myopr.getOriginalCompletion(),"Work Orders/End":mycomp,"Work Orders/Status":status,"Scheduled":prodorder in self.getSelectedOrders()}
                    else:
                        myorddata = {"Work Orders/Work Center":myopr.getName(),"Work Orders/Work Center/ID":(myopr.getAlternativeResources()[0].getID() if len(myopr.getAlternativeResources()) > 0 else "-"),"Processing Machine":(myopr.getProcessMachine().getName() if myopr.getProcessMachine()!= None else "-"),"Work Orders/Expected Duration":myopr.getRandVar().sampleValue(),"Work Orders/Start(ORG)":myopr.getOriginalStart(),"Work Orders/Start":mystrt,"Work Orders/End(ORG)":myopr.getOriginalCompletion(),"Work Orders/End":mycomp,"Work Orders/Status":status,"Scheduled":prodorder in self.getSelectedOrders()}

                    TBRM_df.loc[len(TBRM_df)] = myorddata
                    oprid+=1
                        
            inputdate = ""
            if self.inputdate !=None:
                inputdate = str(self.inputdate.date())

            TBRM_df["Work Orders/Start"] = pd.to_datetime(df["Work Orders/Start"]).dt.floor('s')
            TBRM_df["Work Orders/End"] = pd.to_datetime(df["Work Orders/End"]).dt.floor('s')
            
            TBRM_df.to_csv("TBRM_Plan_"+inputdate+"_R"+str(myround)+".csv",index = False)
        except Exception as e:
            self.getSimulator().saveLog("ERROR: in writing TBRM data "+str(e))
            


        return


       

        #log_df= pd.DataFrame(columns=["Time","Info"])

        #for time,infolist in self.getSimulator().getMyLog().items():
        #    for info in infolist:
        #        infodata = {"Time":time,"Info":info} 
        #        log_df.loc[len(log_df)]= infodata
        
        #log_df.to_csv("LogData.csv",index = False)


        return 

        

