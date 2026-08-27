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
        self.getAlgorithmSetting()[TrailerUnloading.getName()] = {"Select Items":'UnloadFeasible','Assign Resource':"Straight Available","Select Destination":'MostDemanded' }  
        self.getEventTypes()[TrailerUnloading.getName()]= TrailerUnloading


        #-------------------------------------------
        #  Machine Setup -> Machine Loading -> Machine Processing -> Machine Unloading
        MachineSetup = SimEvent(self.getSimulator(),"Machine Setup","Setup","Operator","Machine",False)
        MachineSetup.getDecisionsDict()['Handle'] = ['Assign Processor','Assign Resource','Select Items']
        self.getAlgorithmSetting()[MachineSetup.getName()] = {'Assign Resource':"Straight Available","Assign Processor":"Straight Available",'Select Items':"EDDOrder"}
        self.getEventTypes()[MachineSetup.getName()]= MachineSetup

        #-------------------------------------------
        MachineLoading = SimEvent(self.getSimulator(),"Machine Loading","Loading","Operator","Machine",True)   
        MachineSetup.getSuccessorDict()[MachineLoading] = "Finish to Start" # Precedence settings: MS -> ML
        MachineSetup.getPrecendenceDict()[MachineLoading.getName()] = ['EquipmentInput->FromLocation','Equipment->ToLocation','Equipment','Item Reservation','Items','Processor']
        MachineLoading.getDecisionsDict()['Handle'] = ['Assign Resource']
        self.getAlgorithmSetting()[MachineLoading.getName()] = {'Assign Resource':"Straight Available"}
        self.getEventTypes()[MachineLoading.getName()]= MachineLoading

        #-------------------------------------------
        MachineProcessing = SimEvent(self.getSimulator(),"Machine Processing","Processing",None,"Machine",True)        
        MachineLoading.getSuccessorDict()[MachineProcessing] = "Finish to Start" # Precedence settings: ML -> Proc
        MachineLoading.getPrecendenceDict()[MachineProcessing.getName()] = ['Equipment->Resource','Equipment','Items','Processor']
        MachineProcessing.getDecisionsDict()['Handle'] = ['Assign Processor']
       
        self.getEventTypes()[MachineProcessing.getName()]= MachineProcessing

        #-------------------------------------------
        MachineUnloading = SimEvent(self.getSimulator(),"Machine Unloading","Unloading","Operator","Machine",True)
        MachineProcessing.getSuccessorDict()[MachineUnloading] = "Finish to Start"   # Precedence settings: Proc -> MU
        MachineProcessing.getPrecendenceDict()[MachineUnloading.getName()] = ['Equipment->FromLocation','EquipmentOutput->ToLocation','Equipment','Items','Processor']    
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

    def getInputDate(self):
        return self.inputdate
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
            #self.getSimulator().saveLog("__________________________________________________________")
            #self.getSimulator().saveLog("REPORT: Selected production order release "+str(prodorder[1].getReleaseDate())+", deadline: "+str(prodorder[1].getDeadline()))

            
            try: 
                self.getSimulator().saveLog("Item creation starts")
                self.createDemandItems(prodorder[1],prodorder[1].getFinalProduct())
                #self.getSimulator().saveLog("REPORT: >>>> items ["+(str(prodorder[1].getItems()[0].getID()) if len(prodorder[1].getItems())>0 else '')+"-"+(str(prodorder[1].getItems()[-1].getID()) if len(prodorder[1].getItems())>0 else 'no item')+"]")
            except Exception as e:
                self.getSimulator().saveLog("ERROR in item creation: "+str(e))

            #self.getSimulator().saveLog("REPORT:  Selected "+prodorder[1].printOrder()+" items created.")
            self.getSelectedOrders().append(prodorder[1])

        self.getSimulator().saveLog("REPORT:  Selected orders:  "+str(len(self.getSelectedOrders()))+".")
        self.getSimulator().saveLog("REPORT:>> Creating instance finished.. ")      
   
        return self.getSelectedOrders()

#_____________________________________________________________________
    def createDemandItems(self,demand,product): # Physical products
        self.getSimulator().saveLog("Item creation starts")
        if len(product.getPredecessors()) == 0:
            for itm in range(demand.getQuantity()):
                
                myitem = Item(demand,self.giveItemID())
                self.getCentralInventory().getOutputBuffer().getItems().append(myitem) # generate trailer loading event.
                demand.getItems().append(myitem)
            self.getCentralInventory().getOutputBuffer().generateEvent(False)
        else:
            for preddemnd in demand.getDemandType().getPredecessors():
                self.createDemandItems(demand,preddemnd)

        buffer_data = {"BufferName": self.getCentralInventory().getOutputBuffer().getName(),"Machine":  self.getCentralInventory().getOutputBuffer().getMachine().getName() if  self.getCentralInventory().getOutputBuffer().getMachine()!= None else "Central Inventory","Time":self.getSimulator().getTime(),"No.Items":len(self.getCentralInventory().getOutputBuffer().getItems())}  
        self.getSimulator().getBufferData().append(buffer_data)

        return
#______________________________________________________________________
#################################################################################################################################################
    def applyShiftChange(self):
        avalable_res = [] 
        for res in self.getResources():    
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
        return
#################################################################################################################################################
#################################################################################################################################################  
    def ProgressEvent(self,event):
        # case can be one of the following: "handle","start","suspend","restart","complete"
        debugtimes = []; debugeventids =[]; debugmachines = []; eventdicases =[]
     
        case = self.determineProgressCase(event)

        if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:    
            self.reportEvent(event,case,"Beginning")
      
        if case == "Handle":  
            self.removeFromSchedule(event,self.getSimulator().getTime())
            if not self.checkNecessaryConditions(event,debugtimes,debugeventids):
                self.scheduleEvent(event,"Pending")
                return ## >>>> R  E  T  U  R   N: necessary conditions failed!

            event.sampleProcessTime(self)
  
            if not event.getEventType().isPreemptable(): 
                if  self.getSimulator().getTime()+event.getProcessTime() > self.getCurrentShiftEnd() - 1:
                    self.scheduleEvent(event,"Pending")
                    return ## >>>> R  E  T  U  R   N: non-preemtable event does not fit into current schedule!
     
        ######### MAKE NECESSARY DECISIONS  ########################################   
        casesuccess,success_decisions = self.makeCaseDecisions(event,case,debugtimes,debugeventids)
  
        if not casesuccess: # backtrack the decisions
            if case == "Handle":
                self.scheduleEvent(event,"Pending")
               
            self.resetDecisions(event,success_decisions,debugtimes,debugeventids)            
            return  ## >>>> R  E  T  U  R   N: all required assignments could not be done!
    
        ##########################  H  A  N  D  L  E #########################
        if case == "Handle": 
            feasible,operator_move,bring_equipment = self.checkLogisticalEvents(event,success_decisions,debugtimes,debugeventids)

            if feasible:
                first_logistical = operator_move if (operator_move!= None) else (bring_equipment if bring_equipment != None else None)
                if first_logistical!= None: # logistical event necessary 
                    if event.getType() == "Loading" and isinstance(event.getEquipment(),Trailer):
                        feasible = self.checkEventChainTime(event) 
                       
                    if feasible:
                        self.scheduleEvent(first_logistical,first_logistical.getProgressList()[-1][1][1]) 
                else: # no logistical event
                    progress_step = self.getProgress(event)   
                    if progress_step[1] > progress_step[0]: 
                        event.getProgressList().append((event.getResource(),progress_step)) 
                        self.scheduleEvent(event,progress_step[0]) # schedule progress start
                    else:
                        if progress_step[1] == progress_step[0]: 
                            feasible = False
            if feasible:
                self.removeFromSchedule(event,"Pending")    
            else:
                event.getLogisticalEvents().clear(); self.resetDecisions(event,success_decisions,debugtimes,debugeventids)
                self.scheduleEvent(event,"Pending");  return  ## >>>> R  E  T  U  R   N
        ##########################  H  A  N  D  L  E #########################

     
        ##########################  S  T  A  R  T  #########################
        if case == "Start":
            if event.getType() == "Unloading" and (isinstance(event.getEquipment(),Machine)):
                if not event.getItems()[0] in event.getFromLocation().getItems():
                    self.getSimulator().saveLog(" ERROR: start "+str(event.getName())+"("+str(event.getID())+") but first item not in from-location!!! "+str(event.getLocation().getName())) 
                
            if event.getType() == "Transport":               
                if not event.getItems()[0] in event.getEquipment().getItems():
                    self.getSimulator().saveLog(" ERROR: transport event "+event.getName()+"("+str(event.getID())+") first item is not in equipment!!") 
        ##########################  S  T  A  R  T  #########################

    
        ##########################  S  U  S  P  E  N  D  #########################
        if case == "Suspend": 

            ####  SIMSTART SUCCESSOR ###  event will be handled in the next shift and at restart the successor restart         
            if isinstance(event.getResource(),Operator): 
                event.setResource(None)
            self.removeFromSchedule(event,self.getSimulator().getTime())
            self.scheduleEvent(event,"Pending")
         ##########################  S  U  S  P  E  N  D  #########################

        ##########################  C  O  M  P  L  E  T  E  #########################
        if case == "Complete": 
            self.removeFromSchedule(event,event.getProgressList()[-1][1][1]) # remove the event from queue
            self.makeCompletionUpdates(event,debugtimes,debugeventids,debugmachines)  
        ##########################  C  O  M  P  L  E  T  E  #########################
        

        #########################  (R  E -) S  T  A  R  T    #########################
        if case in ["Start","Restart"]:  # schedule progress step end   
            self.removeFromSchedule(event,event.getProgressList()[-1][1][0]); self.scheduleEvent(event,event.getProgressList()[-1][1][1])
      #########################  (R  E -) S  T  A  R  T    #########################

       #################################### P  R  E  C  E  D  E  N  C  E ###############################
        if event.getType() != "Logistical":
            self.checkPrecedence(event,case,debugtimes,debugeventids)    
        else: # event is logistical
            successor_event = event.getSuccessor() 
            if case == "Complete":    
                if successor_event.getType() != "Logistical": #  OPrMove -> Event   OR   BringEquip->Event, schedule the re/start of the event
                    progress_start,progress_end = self.getProgress(successor_event)
                    if progress_end - progress_start > 0: 
                        successor_event.getProgressList().append((successor_event.getResource(),(progress_start,progress_end)))
                        self.scheduleEvent(successor_event,progress_start)
                    else:
                        if progress_end == progress_start: 
                            self.scheduleEvent(successor_event,"Pending")
                    for logev in successor_event.getLogisticalEvents():
                        successor_event.getLogisticalEvents().remove(logev)      
                else:
                    # OPrMove -> BringEquip
                    self.scheduleEvent(successor_event,successor_event.getProgressList()[-1][1][1])
        #################################### P  R  E  C  E  D  E  N  C  E ###############################
        
        if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids or ((event.getID(),case) in eventdicases):
            self.reportEvent(event,case,"End")
            

        return
###############################################################################################################################################

    def getProgress(self,event):
        progress_start = self.getSimulator().getTime(); 
        progress_end = progress_start+(event.getProcessTime()-event.getTotalProgress())

        if event.getEventType().isPreemptable():
            progress_end = min(progress_end,self.getCurrentShiftEnd()-1)

        return progress_start,progress_end  
###################################################################################################################################################
    def getProgressStep(self,event,step_start):

        step_end = step_start+(event.getProcessTime() - event.getTotalProgress())
        if event.getEventType().isPreemptable():
            step_end = min(step_end,self.getCurrentShiftEnd()-1) 
       
        return (step_start,step_end)
###################################################################################################################################################
    def scheduleEvent(self,event,schtime):
        if not schtime in self.getSimulator().getEventQueue():
            self.getSimulator().getEventQueue()[schtime] = []
                                
        if not event in self.getSimulator().getEventQueue()[schtime]:   
            self.getSimulator().getEventQueue()[schtime].append(event) 

        return 
###################################################################################################################################################
    def removeFromSchedule(self,event,schtime):

        if schtime in self.getSimulator().getEventQueue():
            if event in self.getSimulator().getEventQueue()[schtime]:
                self.getSimulator().getEventQueue()[schtime].remove(event)   

        return 
###################################################################################################################################################  
    def checkPrecedence(self,event,case,debugtimes,debugeventids):

        for successor_type,precedence_type in event.getEventType().getSuccessorDict().items():

            if (case == "Complete" and precedence_type == "Finish to Start"):
 
                successor_event = ExecEvent(None,None,successor_type)
                self.applyPrecedence(event,successor_event,successor_type)

                event.setFinishToStartSuccessor(successor_event)
                successor_event.setFinishToStartPredecessor(event)

                if (successor_event.getEquipment() == None) or (successor_event.getResource() == None): 
                    self.scheduleEvent(successor_event,"Pending")
  
                else: # now progress step can be determined
                    if successor_event.getType() == "Transport": 
                        if successor_event.getToLocation()== None:
                            decision_type = "Select Destination"
                            algname = self.getAlgorithmSetting()[successor_event.getName()][decision_type]
                            algfunction = self.getProductionAlgManager().getDecisionAlgorithms()[decision_type][algname]
                            alg_return = algfunction(event)
                            if alg_return!= None:
                                successor_event.setToLocation(alg_return.getInputBuffer())
     
                    successor_event.sampleProcessTime(self); proctime = successor_event.getProcessTime() 
                    successor_start = self.getSimulator().getTime(); successor_end = successor_start+proctime

                    if successor_event.getEventType().isPreemptable():
                        successor_end = min(successor_end,self.getCurrentShiftEnd()-1) 
                    else:
                        if successor_end > self.getCurrentShiftEnd():
                            successor_start = self.getCurrentShiftEnd() # check handling in the next shift
                            successor_end = successor_start # zero progress step

                    if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                        self.getSimulator().saveLog(" REPORT: successor "+successor_event.getName()+"-"+str(successor_event.getID())+" has progress "+str((successor_start,successor_end))) 

                    if (successor_end - successor_start > 0): 
                        progress_step = (successor_start,successor_end)
                            
                        if successor_event.checkAllAssigned("Handle"): # successor can have progress step..
                            successor_event.getProgressList().append((successor_event.getResource(),progress_step))
                            self.scheduleEvent(successor_event,successor_start)  
                        else:
                            self.scheduleEvent(successor_event,"Pending")
                    else:
                        if successor_end == successor_start: 
                            self.scheduleEvent(successor_event,"Pending")

        return 


####################################################################################################################################################
    def applyPrecedence(self,event,successor_event,successor_type):

        precedenceinfo = event.getEventType().getPrecendenceDict()[successor_type.getName()]

        # setEquipment
        if 'Equipment' in precedenceinfo: #  TL->TT, TT->TU, MS->Ml, ML->Proc
            successor_event.setEquipment(event.getEquipment())
        if 'FromLocation->Equipment' in precedenceinfo: # Proc->MU
            successor_event.setEquipment(event.getFromLocation())

        if event.getName() == "Machine Unloading":
            if event.getEquipment() == None:
                self.getSimulator().saveLog(" REPORT: event: "+str(event.getName())+str(event.getID())+", equip none $$$$$$$$$$$$ ") 
                

        if 'Processor' in precedenceinfo: # ML->MProc
            event_machine = event.getEquipment() 

            if event in event_machine.getProcessMatch():
                processor = event_machine.getProcessMatch()[event]
                del event_machine.getProcessMatch()[event]
                event_machine.getProcessMatch()[successor_event] = processor
                successor_event.setProcessor(processor)

        
            
                

        # setResource 
        if 'Resource' in precedenceinfo: # TL->TT,  TT->TU 
            successor_event.setResource(event.getResource())
            if event.getResource() == None:
                self.getSimulator().saveLog(" REPORT: successor: "+str(event.getName())+str(event.getID())+", resource none ") 
            event.getResource().setIdle(False)
        if 'Equipment->Resource' in precedenceinfo: # ML->Proc
            successor_event.setResource(event.getEquipment())

        if 'Items' in precedenceinfo:
            for item in event.getItems():
                successor_event.getItems().append(item)
                
        if 'Item Reservation' in precedenceinfo:
            for item in event.getItems():
                if item.getReservedEvent() == event:
                    item.setReservedEvent(successor_event)
            

        # set FromLocation: 
        if "FromLocation" in precedenceinfo: # TL->TT, Proc->MU
            successor_event.setFromLocation(event.getFromLocation())
        if "EquipmentInput->FromLocation" in precedenceinfo: #  MS->ML
            successor_event.setFromLocation(event.getEquipment().getInputBuffer())
        if 'ToLocation->FromLocation' in precedenceinfo: # ML -> Proc
            successor_event.setFromLocation(event.getToLocation())
        if 'Equipment->FromLocation' in precedenceinfo: # TT->TU
            successor_event.setFromLocation(event.getEquipment())
       
            
                        
        # set ToLocation:    
        if 'ToLocation' in precedenceinfo: # TT->TU
            successor_event.setToLocation(event.getToLocation())
        if 'Equipment->ToLocation' in precedenceinfo:  # MS->ML
            successor_event.setToLocation(event.getEquipment())
        if 'EquipmentOutput->ToLocation' in precedenceinfo: # Proc->MU
            successor_event.setToLocation(event.getEquipment().getOutputBuffer())


        return
                      
###############################################################################################################################################
    def reportEvent(self,event,case,stage):

        self.getSimulator().saveLog(" REPORT: _________________________________________________________________________________")
        self.getSimulator().saveLog(" REPORT: event: "+str(event.getName())+"("+str(event.getID())+")-["+(str(event.getItems()[0].getID())+"-"+str(event.getItems()[-1].getID()) if len(event.getItems())> 0 else '-')+"], case: "+case+", stage: "+stage) 
        self.getSimulator().saveLog(" REPORT: @ "+(event.getLocation().getName() if event.getLocation() != None else "No loc, ")+"| ("+(event.getFromLocation().getName() if event.getFromLocation()!=None else "")+")->("+(event.getToLocation().getName() if event.getToLocation()!=None else "")+")") 
        self.getSimulator().saveLog(" REPORT: Equipment: "+(event.getEquipment().getName() if event.getEquipment() != None else "None")+", Resource: "+(event.getResource().getName() if event.getResource() != None else "None")+(", Processor: "+str(event.getProcessor()) if event.getProcessor() != None else " ")) 
        self.getSimulator().saveLog(" REPORT: Active Operation: "+("No item " if len(event.getItems())==0 else (event.getItems()[0].getActiveOperation().getName() if event.getItems()[0].getActiveOperation()!= None else "No act opr"))) 
        self.getSimulator().saveLog(" REPORT: Processing Progress: "+str(["("+str(x[1][0])+"-"+str(x[1][1])+")" for x in event.getProgressList()])+", Total progress: "+str(event.getTotalProgress())+", Procestime: "+str(event.getProcessTime() if event.getProcessTime()!= None else "ProcTime None!" )) 
        
        if event.getSimStartSuccessor()!=None or event.getSimCompletionSuccessor()!= None or event.getFinishToStartSuccessor()!=None:
            successor = event.getSimStartSuccessor() if event.getSimStartSuccessor()!=None else None
            if successor == None:
                successor = event.getSimCompletionSuccessor() if event.getSimCompletionSuccessor()!=None else None
                if successor == None:
                    successor = event.getFinishToStartSuccessor() if event.getFinishToStartSuccessor()!=None else None
                
            self.getSimulator().saveLog(" REPORT: "+("| SimStartSuccessor : " +event.getSimStartSuccessor().getName()+"("+str(event.getSimStartSuccessor().getID())+")" if event.getSimStartSuccessor()!=None else '')+("| SimCompletionSuccessor: "+event.getSimCompletionSuccessor().getName()+"("+str(event.getSimCompletionSuccessor().getID())+"), " if event.getSimCompletionSuccessor()!= None else '')+("| FinishtoStart Successor: "+event.getFinishToStartSuccessor().getName()+"("+str(event.getFinishToStartSuccessor().getID())+"), " if event.getFinishToStartSuccessor()!=None else '')+(",  Progress: "+str(["("+str(x[1][0])+"-"+str(x[1][1])+")" for x in successor.getProgressList()])+", Total progress: "+str(successor.getTotalProgress())+", Procestime: "+str(successor.getProcessTime() if successor.getProcessTime()!= None else "ProcTime None!" ) if successor != None else ""))

        if len(event.getLogisticalEvents()) > 0:
            self.getSimulator().saveLog(" REPORT: logistical events "+str([str(o.getName())+"("+str(o.getID())+")" for o in event.getLogisticalEvents()])) 
        self.getSimulator().saveLog(" REPORT: Pending: "+str(event in self.getSimulator().getEventQueue()["Pending"]))


        self.getSimulator().saveLog(" REPORT: _________________________________________________________________________________")
        return
################################################################################################################################################
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
    def makeCaseDecisions(self,event,case,debugtimes,debugeventids):
        casesuccess = True; success_decisions = []       
        if case in event.getEventType().getDecisionsDict():
           
            for decision_type in event.getEventType().getDecisionsDict()[case]:
                if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                    self.getSimulator().saveLog(" REPORT: decision_type "+decision_type) 
                    if event.getType() == "Loading":
                        select_dict = dict();orders = []
                        event_place = event.getFromLocation()  
                        if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                            self.getSimulator().saveLog(" REPORT: items "+str(len(event_place.getItems()))+", cap "+str(event_place.getCapacity())) 
                    if event.getType() == "Setup":
                        event_place = event.getEquipment().getInputBuffer()
                        if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                            self.getSimulator().saveLog(" REPORT: items "+str(len(event_place.getItems()))+", cap "+str(event_place.getCapacity())) 
                if decision_type == "Assign Processor": 
                    if event.getProcessor()!= None:
                        continue
                if decision_type == "Select Items": 
                    if len(event.getItems()) > 0:
                        continue
                algname = self.getAlgorithmSetting()[event.getName()][decision_type] 
                alg_return = self.getProductionAlgManager().getDecisionAlgorithms()[decision_type][algname](event) 
                if alg_return!= None:
                    if decision_type == "Select Items":
                        if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                            self.getSimulator().saveLog(" REPORT: return "+str(len(alg_return))) 
                        for item in alg_return:
                            event.getItems().append(item) 
                    if decision_type == "Assign Processor":  
                        event.getEquipment().getProcessMatch()[event] = alg_return 
                        event.setProcessor(alg_return)
                    if decision_type == 'Select Destination': 
                        event.setToLocation(alg_return.getInputBuffer())
                    if decision_type == "Assign Equipment":       
                        event.setEquipment(alg_return); event.setToLocation(alg_return) 
                        alg_return.setIdle(False)
                    if decision_type == "Assign Resource": 
                        event.setResource(alg_return) 
                        alg_return.setIdle(False)   
                    success_decisions.append(decision_type)
                else:
                    if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                        self.getSimulator().saveLog(" REPORT: failed decision"+str(decision_type)) 
                    casesuccess = False; break 
        return casesuccess,success_decisions
############################################################################################################################
    def resetDecisions(self,event,success_decisions,debugtimes,debugeventids):

        if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
            self.getSimulator().saveLog("REPORT: **** resetting decisions for event "+event.getName()+"("+str(event.getID())+"), decisions: "+str(success_decisions))
    
        for decision_type in success_decisions:
       
            if decision_type == "Assign Equipment":
                event.getEquipment().setIdle(True)
                if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                    self.getSimulator().saveLog("REPORT: **** event "+event.getName()+"("+str(event.getID())+"), equipment is made NONE NONE..")
                event.setEquipment(None)  
                
            if decision_type == "Assign Resource":
                event.getResource().setIdle(True)
                event.setResource(None)
            if decision_type == "Select Items":
                event.getItems().clear()

         

        return
############################################################################################################################
    def checkLogisticalEvents(self,event,success_decisions,debugtimes,debugeventids):
        
        feasible = True; operator_move = None; bring_equipment = None; OprMovPT = 0                  
        equipment_onlocation = (event.getEquipment().getLocation() == event.getLocation())            
        resource_onlocation =  (event.getResource().getLocation() == event.getLocation())

        if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
            self.getSimulator().saveLog("REPORT: event : "+event.getName()+"("+str(event.getID())+")"+", res on loc? "+str(resource_onlocation)+", equip on loc? "+str(equipment_onlocation)) 

        if not equipment_onlocation:
            
            bring_equipment = ExecEvent(event.getEquipment().getLocation(),event.getLocation(),self.getEventTypes()["Bring Equipment"])
            bring_equipment.sampleProcessTime(self)

            event.getLogisticalEvents().append(bring_equipment)
       
            if event.getResource().getLocation() != event.getEquipment().getLocation():
                operator_move = ExecEvent(event.getResource().getLocation(),event.getEquipment().getLocation(),self.getEventTypes()["Operator Move"])
                operator_move.setEquipment(None);operator_move.setResource(event.getResource())
                operator_move.sampleProcessTime(self); OprMovPT = operator_move.getProcessTime()
                event.getLogisticalEvents().append(operator_move)
            
            ###############################################################################################
            if self.getSimulator().getTime()+OprMovPT+bring_equipment.getProcessTime() > self.getCurrentShiftEnd()-1:
                if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                    if operator_move != None:
                        self.getSimulator().saveLog("REPORT: ******** Operator move + bring equipment) cannot be finished in same shift" )
                    else:
                        self.getSimulator().saveLog("REPORT: ******** bring equipment) cannot be finished in same shift" )
                feasible = False         
            else:  
                bring_equipment.setEquipment(event.getEquipment()); bring_equipment.setResource(event.getResource())
                bring_equipment.setSuccessor(event)
                
                if operator_move != None:
                    opr_progress_step = (self.getSimulator().getTime(),self.getSimulator().getTime()+OprMovPT)
                    operator_move.getProgressList().append((operator_move.getResource(),opr_progress_step))
                    operator_move.setSuccessor(bring_equipment)
                    
                progress_step = (self.getSimulator().getTime()+OprMovPT,self.getSimulator().getTime()+OprMovPT+bring_equipment.getProcessTime())
                                
                if self.getSimulator().getTime() in debugtimes:
                    self.getSimulator().saveLog("REPORT: bring_equipment process time: "+str(bring_equipment.getProcessTime())+", prog step "+str(progress_step)+" Opr Move none? "+str(operator_move == None))

                bring_equipment.getProgressList().append((bring_equipment.getResource(),progress_step))

                            
        # Only operator move needs to be scheduled
        if not resource_onlocation and equipment_onlocation:      
            operator_move = ExecEvent(event.getResource().getLocation(),event.getLocation(),self.getEventTypes()["Operator Move"])
            operator_move.setEquipment(None); operator_move.setResource(event.getResource())
            operator_move.setSuccessor(event); operator_move.sampleProcessTime(self)
            event.getLogisticalEvents().append(operator_move)
            
            if self.getSimulator().getTime()+operator_move.getProcessTime() > self.getCurrentShiftEnd()-1:
                feasible = False
            else: 
                progress_step = (self.getSimulator().getTime(),min(self.getSimulator().getTime()+operator_move.getProcessTime(),self.getCurrentShiftEnd()-1))
                operator_move.getProgressList().append((operator_move.getResource(),progress_step))

        if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
            self.getSimulator().saveLog("REPORT: logistical events : "+str(len(event.getLogisticalEvents()))) 
      
        return feasible,operator_move,bring_equipment

#################################################################################################################################       
    def makeCompletionUpdates(self,event,debugtimes,debugeventids,debugmachines):

      # update execution data of event...
        progrss_steps = ""; step_id = 0
        for res,prstep in event.getProgressList():
            progrss_steps+=("" if step_id == 0 else "~")+str(prstep[0])+"-"+str(prstep[1])
            step_id+=1
                
    
        ev_items = (str(event.getItems()[0].getID())+"~"+str(event.getItems()[-1].getID()) if len(event.getItems())>0 else '-')

        opname = "-"; demandid = '';eventprod = ''
        if event.getType() == "Processing":
            if len(event.getItems()) > 0:
                if event.getItems()[0].getActiveOperation()!= None: 
                    opname = event.getItems()[0].getActiveOperation().getReferenceName()
                    demandid = event.getItems()[0].getActiveOperation().getDemand().getID()
                    eventprod = event.getItems()[0].getActiveOperation().getDemand().getFinalProduct().getName()


                    

        eventdate =  self.getSimulator().getRealTime().strftime("%Y-%m-%d %H:%M:%S")

        if event.getType() == "Unloading":
            if event.getLocation().getName() == "CentralBuffer_Location":
                if len(event.getItems()) > 0:
                    demandid = event.getItems()[0].getDemand().getID()
                    eventprod = event.getItems()[0].getDemand().getFinalProduct().getName()
          
        execution_data = {"EventName":event.getName(),"EventID":event.getID(),"ProgressSteps":progrss_steps,"ID":demandid,"Product":eventprod,"Work Orders/Operation":opname,"Items":ev_items,"Resource":("-" if event.getResource() == None else event.getResource().getName()),"Equipment":("-" if event.getEquipment() == None else event.getEquipment().getName()),"Location":event.getLocation().getName(),"SimTime":self.getSimulator().getTime(),"Date":eventdate}  
        self.getSimulator().getExecutionData().append(execution_data)

    
        if event.getResource()!= None: 
            if isinstance(event.getResource(),Operator):
                # "EntityName","EntityID","Time","LocationName","LocationID"
                location_data = {"EntityName":event.getResource().getName(),"EntityID":event.getResource().getID(),"Time":self.getSimulator().getTime(),"LocationName":event.getResource().getLocation().getName(),"LocationID": (event.getResource().getLocation().getID() if event.getResource().getLocation()!= None else "-")}  
                self.getSimulator().getLocationData().append(location_data)
          

      
    # update operation status in case machine processing
        if event.getType() == "Processing":
            if len(event.getItems()) > 0:
                  
                if event.getItems()[0].getActiveOperation() != None: 
                    event.getItems()[0].getActiveOperation().setFinished()
              
                if event in event.getEquipment().getProcessMatch():
                    del event.getEquipment().getProcessMatch()[event]
                  

    # update operation status in case machine processing

        if event.getType() == "Transport":
            event.getEquipment().setLocation(event.getToLocation().getLocation())
            event.getResource().setLocation(event.getToLocation().getLocation())
            
        if event.getName() == "Operator Move":
            #self.getSimulator().saveLog("REPORT: event resource set location: "+str(event.getToLocation().getName()))   
            event.getResource().setLocation(event.getToLocation())
            #self.getSimulator().saveLog("REPORT: event resource  location: "+str(event.getResource().getLocation().getName()))   

        if event.getName() == "Bring Equipment":
            event.getResource().setLocation(event.getToLocation())
            event.getEquipment().setLocation(event.getToLocation())


        if event.getType() in ["Loading","Unloading"]:
          
            for myitem in event.getItems():   
                event.getFromLocation().getItems().remove(myitem)
                event.getToLocation().getItems().append(myitem)
                myitem.setReservedEvent(None)
            if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                self.getSimulator().saveLog("REPORT: from location items  "+str(len(event.getFromLocation().getItems())))


            if isinstance(event.getFromLocation(),Buffer):
                fromloc = event.getFromLocation()
                buffer_data = {"BufferName":fromloc.getName(),"Machine": fromloc.getMachine().getName() if fromloc.getMachine()!= None else "Central Inventory","Time":self.getSimulator().getTime(),"No.Items":len(fromloc.getItems())}  
                self.getSimulator().getBufferData().append(buffer_data)
                
            if isinstance(event.getToLocation(),Buffer): 
                toloc = event.getToLocation()
                buffer_data = {"BufferName":toloc.getName(),"Machine": toloc.getMachine().getName() if toloc.getMachine()!= None else "Central Inventory","Time":self.getSimulator().getTime(),"No.Items":len(toloc.getItems())}  
                self.getSimulator().getBufferData().append(buffer_data)

            
            if event.getType() == "Loading":
                event.getFromLocation().generateEvent(self.getSimulator().getTime() in debugtimes) # TL: Outputbuffer triggers Trailer loading
    
            if event.getType() == "Unloading":
                if isinstance(event.getFromLocation(),Machine):
                    if event.getFromLocation().getName() != "OUT - Outsourced activity_(OUT - Outsourced)":
                        event.getFromLocation().getInputBuffer().generateEvent(self.getSimulator().getTime() in debugtimes) # MU: triggers Machine Setup
                if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                    self.getSimulator().saveLog("REPORT: About to generate event at "+event.getToLocation().getName()+" items "+str(len(event.getToLocation().getItems())))
                event.getToLocation().generateEvent(self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids)  # MU: Outputbuffer triggers Trailer loading
            
            event.getEquipment().setIdle(True)


        if event.getType() != "Logistical":
            event.getResource().setIdle(True)
        
      
  
        return 
#######################################################################################################################################################

#########################################################################################################################
    def writeData(self):

        event_df = pd.DataFrame(columns=["EventName","EventID","ProgressSteps","ID","Product","Work Orders/Operation","Items","Resource","Equipment","Location","SimTime","Date"])

        
      
        for eventdata in self.getSimulator().getExecutionData():
            event_df.loc[len(event_df)] = eventdata

        
        event_df.to_csv("EventExecutionData.csv",index = False)


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
    def checkEventChainTime(self,event):

         # now check the successors of the event in the event chain.
        current_event = event; successor_event = None; preemptable = False
        totaltime = 0

        for logevent in event.getLogisticalEvents():
            totaltime+=logevent.getProcessTime()

        if not event.getEventType().isPreemptable():
            totaltime+= event.getProcessTime()
            while (current_event!= None) and (not preemptable):
                for successor_type,precedence_type in current_event.getEventType().getSuccessorDict().items():
                    if precedence_type == "Finish to Start": # this is only for transport events for now
                        successor_event = ExecEvent(None,None,successor_type)
                        self.applyPrecedence(current_event,successor_event,successor_type)
                        if successor_event.getFromLocation()!= None:
                            if successor_event.getToLocation() == None: 
                                if successor_event.getName() in self.getAlgorithmSetting():
                                    mydecision_type = "Select Destination"
                                    if mydecision_type in self.getAlgorithmSetting()[successor_event.getName()]:
                                        algname = self.getAlgorithmSetting()[successor_event.getName()][mydecision_type]
                                        algfunction = self.getProductionAlgManager().getDecisionAlgorithms()[mydecision_type][algname]
                                        alg_return = algfunction(successor_event)
                                        if alg_return!= None:
                                            successor_event.setToLocation(alg_return.getInputBuffer())
    
                            if successor_event.getToLocation() != None: 
                                successor_event.sampleProcessTime(self)
                                if not successor_event.getEventType().isPreemptable():
                                    totaltime+=successor_event.getProcessTime()
                                else:
                                    preemptable = True
                                    totaltime+=1
                                break # for successordict
                                 
                current_event = successor_event; successor_event = None
        else:
            totaltime+=1
                    
       
        if self.getSimulator().getTime()+totaltime > self.getCurrentShiftEnd()-1:
            return False
        
        return True
#########################################################################################################################
    def checkNecessaryConditions(self,event,debugtimes,debugeventids):

      
        if event.getType() == "Setup":
            if event.getEquipment().getNoProcessors() == 1:
                if len(event.getEquipment().getItems()) > 0: 
                    return False
        if event.getType() == "Unloading" and event.getEquipment()!=None and len(event.getItems()) > 0:
            if event.getEquipment().getNoProcessors() == 1:
                if not event.getItems()[0] in event.getEquipment().getItems(): 
                    return False


        if event.getType() == "Loading" and event.getEquipment()!=None:
            if isinstance(event.getEquipment(),Machine):
                if event.getEquipment().getNoProcessors() == 1:
                    if len(event.getEquipment().getItems()) > 0: 
                        return False

        return True
#############################################################################################################
    def writeDataTBRMOutPut(self,myround):


        TBRM_df= pd.DataFrame(columns=["ID","Product","Product/ID","Quantity To Produce","Deadline","Reference","Work Orders/Work Center","Work Orders/Work Center/ID","Processing Machine","Work Orders/Operation","Work Orders/Expected Duration","Work Orders/Start(ORG)","Work Orders/Start","Work Orders/End(ORG)","Work Orders/End","Work Orders/Status","Tardy","Lateness (days)"])

        currentdate =  datetime.now()
        currentdate = currentdate-timedelta(days = 2)
        startday = datetime(currentdate.year, currentdate.month, currentdate.day)

        try: 
            for prodordid,prodorder in self.getProductionOrders().items():
            
                oprsequence = prodorder.getFinalProduct().getOperationSequences()[prodorder.getID()]

                tardy = "-"
                lateness = "-"

                if prodorder.getMILPCompletion()!= None: 
                    tardy = str(prodorder.getDeadline() < prodorder.getMILPCompletion())
                    if prodorder.getDeadline() < prodorder.getMILPCompletion():
                        lateness = str((prodorder.getMILPCompletion()-prodorder.getDeadline()).days)
                    else:
                        lateness = "0"

               

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

                    # repeat columns A-E for each operation!
                    # checlk material availability and set a release date for order. 
                    
                    if oprid == 0:
                        myorddata = {"ID":prodorder.getID(),"Product":prodorder.getFinalProduct().getName(),"Product/ID":prodorder.getFinalProduct().getID(),"Quantity To Produce":prodorder.getQuantity(),"Deadline":prodorder.getDeadline(),"Reference":prodorder.getReference(),"Work Orders/Work Center":myopr.getName(),"Work Orders/Work Center/ID":myopr.getAlternativeResources()[0].getID(),"Processing Machine":(myopr.getProcessMachine().getName() if myopr.getProcessMachine()!= None else "-"),"Work Orders/Operation":myopr.getReferenceName(),"Work Orders/Expected Duration":myopr.getRandVar().sampleValue(),"Work Orders/Start(ORG)":myopr.getOriginalStart(),"Work Orders/Start":mystrt,"Work Orders/End(ORG)":myopr.getOriginalCompletion(),"Work Orders/End":mycomp,"Work Orders/Status":status,"Tardy":tardy,"Lateness (days)":lateness}
                    else:
                        myorddata = {"ID":prodorder.getID(),"Product":prodorder.getFinalProduct().getName(),"Product/ID":prodorder.getFinalProduct().getID(),"Quantity To Produce":prodorder.getQuantity(),"Deadline":prodorder.getDeadline(),"Reference":prodorder.getReference(),"Work Orders/Work Center":myopr.getName(),"Work Orders/Work Center/ID":(myopr.getAlternativeResources()[0].getID() if len(myopr.getAlternativeResources()) > 0 else "-"),"Processing Machine":(myopr.getProcessMachine().getName() if myopr.getProcessMachine()!= None else "-"),"Work Orders/Operation":myopr.getReferenceName(),"Work Orders/Expected Duration":myopr.getRandVar().sampleValue(),"Work Orders/Start(ORG)":myopr.getOriginalStart(),"Work Orders/Start":mystrt,"Work Orders/End(ORG)":myopr.getOriginalCompletion(),"Work Orders/End":mycomp,"Work Orders/Status":status,"Scheduled":prodorder in self.getSelectedOrders(),"Tardy":tardy,"Lateness (days)":lateness}

                    TBRM_df.loc[len(TBRM_df)] = myorddata
                    oprid+=1
                        
            inputdate = ""
            if self.inputdate !=None:
                inputdate = str(self.inputdate.date())

            TBRM_df["Work Orders/Start"] = pd.to_datetime(TBRM_df["Work Orders/Start"]).dt.floor('s')
            TBRM_df["Work Orders/End"] = pd.to_datetime(TBRM_df["Work Orders/End"]).dt.floor('s')
            
            TBRM_df.to_csv("TBRM_Plan_"+inputdate+"_R"+str(myround)+"_"+str((datetime.now()).date())+".csv",index = False)
        except Exception as e:
            self.getSimulator().saveLog("ERROR: in writing TBRM data "+str(e))
        

        return


##########################################################################################################################################
    def writeSimulationMILPCommonfile(self,myround):








        return


