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
        TrailerUnloading.getDecisionsDict()['Handle'] = ['Assign Resource']
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
        MachineSetup.getPrecendenceDict()[MachineLoading.getName()] = ['EquipmentInput->FromLocation','Equipment->ToLocation','Equipment','Items','Processor']
        MachineLoading.getDecisionsDict()['Handle'] = ['Assign Resource']
        self.getAlgorithmSetting()[MachineLoading.getName()] = {'Assign Resource':"Straight Available"}
        self.getEventTypes()[MachineLoading.getName()]= MachineLoading

        #-------------------------------------------
        MachineProcessing = SimEvent(self.getSimulator(),"Machine Processing","Processing",None,"Machine",True)        
        MachineLoading.getSuccessorDict()[MachineProcessing] = "Simultaneous Start"  # Precedence settings: ML -> Proc
        MachineLoading.getPrecendenceDict()[MachineProcessing.getName()] = ['ToLocation->FromLocation','ToLocation->Resource','Equipment','Items','Processor']
        MachineProcessing.getDecisionsDict()['Handle'] = ["Assign Processor"]
        self.getAlgorithmSetting()[MachineProcessing.getName()] = {"Assign Processor":"Straight Available"} 
        self.getEventTypes()[MachineProcessing.getName()]= MachineProcessing

        #-------------------------------------------
        MachineUnloading = SimEvent(self.getSimulator(),"Machine Unloading","Unloading","Operator","Machine",True)
        MachineProcessing.getSuccessorDict()[MachineUnloading] = "CompletionRatio Start"   # Precedence settings: Proc -> MU
        MachineProcessing.getPrecendenceDict()[MachineUnloading.getName()] = ['FromLocation','FromLocationOutput->ToLocation','Equipment','Items']    
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

        debugtimes = []
        debugeventids = []
        debugmachines = []
        specialcheck = False # event.getLocation().getName() == "PACK_(VERP_P)_Location" and event.getType() == "Setup"
        
  

        if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
            self.getSimulator().saveLog("REPORT: ==================================================================================================")
            self.getSimulator().saveLog("REPORT: event : "+str(event.getName())+"("+str(event.getID())+")"+", loc :"+event.getLocation().getName()+", res none? "+str(event.getResource() == None)+", processor none? "+str(event.getProcessor()== None)+", p: "+str(event.getProcessTime())+", in pendings? "+str(event in self.getSimulator().getEventQueue()["Pending"])+", pred? "+str(event.getPredecessor() != None)+","+str(len(event.getItems()))+" items ["+(str(event.getItems()[0].getID()) if len(event.getItems())>0 else '')+"-"+(str(event.getItems()[-1].getID()) if len(event.getItems())>0 else '')+"]")
            self.getSimulator().saveLog("REPORT: tot.prog: "+str(event.getTotalProgress())+str(["("+str(pr[0])+"-"+str(pr[1])+")" for r,pr in event.getProgressList()]))
            
                      
        case = self.determineProgressCase(event)

        if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids :
            self.getSimulator().saveLog("REPORT:m  event : "+str(event.getName())+"("+str(event.getID())+") case "+case)

        if (specialcheck and case == "Start"):
            self.getSimulator().saveLog("REPORT: ************************** event : "+str(event.getName())+"("+str(event.getID())+") case "+case+", p: "+str(event.getProcessTime()))

       

      
        if case == "Handle":
            if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                self.getSimulator().saveLog("REPORT: before nec. conds. , event type: "+str(event.getType())+", equip none? "+str(event.getEquipment() == None))
            if not self.checkNecessaryConditions(event):
                if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                    self.getSimulator().saveLog("REPORT: after nec. conds. ")
                if self.getSimulator().getTime() in self.getSimulator().getEventQueue():
                    if event in self.getSimulator().getEventQueue()[self.getSimulator().getTime()]:
                        self.getSimulator().getEventQueue()[self.getSimulator().getTime()].remove(event)
                if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                    self.getSimulator().saveLog("REPORT: before pending")
                if not event in self.getSimulator().getEventQueue()["Pending"]:
                    self.getSimulator().getEventQueue()["Pending"].append(event)
                
                return
            if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                self.getSimulator().saveLog("REPORT: after nec. conds. OK")
 
            if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                self.getSimulator().saveLog("REPORT:  event : "+str(event.getName())+"-"+str(event.getID()))
                oprseq = []
                if len(event.getItems()) < 0:
                    oprseq = event.getItems()[0].getDemand().getFinalProduct().getOperationSequences()[event.getItems()[0].getDemand().getID()]
                
                #self.getSimulator().saveLog("REPORT: event : "+str(event.getName())+"("+str(event.getID())+"), items "+str(len(event.getItems()))+", active opr none? "+("No item " if len(event.getItems())==0 else str(event.getItems()[0].getActiveOperation()== None))+" event loc "+event.getLocation().getName()+", item oprs "+str([str(o.isCancelled())+"--"+str(o.isFinished())+"--"+str(o.getName()) for o in oprseq])+", equip none? "+str(event.getEquipment() == None)+", tot.prog: "+str(event.getTotalProgress())+str(["("+str(pr[0])+"-"+str(pr[1])+")" for r,pr in event.getProgressList()])+", p: "+str(event.getProcessTime())+", case: "+case)

            if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                if isinstance(event.getEquipment(),Machine):
                    if event.getEquipment()!= None:
                        self.getSimulator().saveLog("REPORT: process time sampled.. equip automated ?"+str(event.getEquipment().IsAutomated()))
                if len(event.getItems()) > 0:
                    self.getSimulator().saveLog("REPORT: process time sampled.. items active opr none ?"+str(event.getItems()[0].getActiveOperation() == None))
            event.sampleProcessTime(self)
            if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                self.getSimulator().saveLog("REPORT: process time sampling done...  .case ")
    
            if not event.getEventType().isPreemptable():  # check if no time left in current shift for a non-preemtable event
                if  event.getProcessTime() + self.getSimulator().getTime() > self.getCurrentShiftEnd() - 1:
                    return
            if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                self.getSimulator().saveLog("REPORT: after check....")

        ######### MAKE NECESSARY DECISIONS  ########################################
        casesuccess = self.makeCaseDecisions(event,case,debugtimes,debugeventids)

        if (specialcheck and case == "Handle"):
            self.getSimulator().saveLog("REPORT: ???????????????????? event : "+str(event.getName())+"("+str(event.getID())+") case "+case+" equip available? "+str(event.getEquipment().isAvailable()))
       

        if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                self.getSimulator().saveLog("REPORT: casesuccess: "+str(casesuccess))



        if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
            self.getSimulator().saveLog("REPORT: event : "+str(event.getName())+"("+str(event.getID())+")"+", casesuccess :"+str(casesuccess))
       
        
        if not casesuccess:
            if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                self.getSimulator().saveLog("REPORT: Handling of pending event : "+str(event.getName())+" at "+str(event.getID())+" not successful")
            if case == "Handle":
                # add event to pending list and remove from time events.
                if self.getSimulator().getTime() in self.getSimulator().getEventQueue():
                    if event in self.getSimulator().getEventQueue()[self.getSimulator().getTime()]:
                        self.getSimulator().getEventQueue()[self.getSimulator().getTime()] = [x for x in self.getSimulator().getEventQueue()[self.getSimulator().getTime()] if x != event]
                if not event in self.getSimulator().getEventQueue()["Pending"]:
                    self.getSimulator().getEventQueue()["Pending"].append(event)

                if event.getSuspendedPredecessor() != None:
                    if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                        self.getSimulator().saveLog("REPORT: event : "+str(event.getName())+"("+str(event.getID())+") has suspended predecessor "+str(event.getSuspendedPredecessor().getName())+"("+str(event.getSuspendedPredecessor().getID())+")")
                    if event.getSuspendedPredecessor() in self.getSimulator().getEventQueue()["Pending"]:
                        self.getSimulator().getEventQueue()["Pending"].remove(event.getSuspendedPredecessor())

                #if event.getSuspendedSuccessor() != None:
                #    if self.getSimulator().getTime() in self.getSimulator().getEventQueue():
                #        if event.getSuspendedSuccessor() in self.getSimulator().getEventQueue()[self.getSimulator().getTime()]:
                #            self.getSimulator().getEventQueue()[self.getSimulator().getTime()].remove(event.getSuspendedSuccessor())
                #    if event.getSuspendedSuccessor() in self.getSimulator().getEventQueue()["Pending"]:
                #        self.getSimulator().getEventQueue()["Pending"].remove(event.getSuspendedSuccessor())
               
            return

        


             
        if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                self.getSimulator().saveLog("REPORT: Handling of pending event: "+str(event.getName())+"("+str(event.getID())+") successful with logistical events "+str([e.getName()+"("+str(e.getID())+"), "  for e in event.getLogisticalEvents()]))

        if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
            self.getSimulator().saveLog(" REPORT: event: "+str(event.getName())+"("+str(event.getID())+")-["+(str(event.getItems()[0].getID()) if len(event.getItems())>0 else '')+"-"+(str(event.getItems()[-1].getID()) if len(event.getItems())>0 else '')+"]"+", equip none? "+str(event.getEquipment() == None)+", active opr none? "+("No item " if len(event.getItems())==0 else (event.getItems()[0].getActiveOperation().getName() if event.getItems()[0].getActiveOperation()!= None else "No act opr"))+", loc "+(event.getLocation().getName() if event.getLocation() == None else "No loc")+", tot.prog: "+str(event.getTotalProgress())+", p: "+str(event.getProcessTime())+", succ event? none "+str(event.getSuspendedSuccessor() == None)+", case: "+case) 

            self.getSimulator().saveLog(" REPORT: event: "+str(event.getName())+"("+str(event.getID())+") , successor dict "+str(event.getEventType().getSuccessorDict().items()))

            if isinstance(event.getEquipment(),Trailer):
                if event.getEquipment() != None:
                    self.getSimulator().saveLog("REPORT: event : "+str(event.getName())+"("+str(event.getID())+") items "+str(len(event.getItems()))+", equipment "+event.getEquipment().getName()+", equip-items "+str(len(event.getEquipment().getItems())))

        if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
            for progress_id in range(len(event.getProgressList())):
                self.getSimulator().saveLog("REPORT: event: "+str(event.getName())+ "progress step: "+str(event.getProgressList()[progress_id][1]))
            self.getSimulator().saveLog("REPORT: event: "+str(event.getName())+", TotalProgress: "+str(event.getTotalProgress()))
       
        # PROGRESS UPDATES
        if case == "Suspend":
            if event.getType() == "Processing":
                if event in event.getEquipment().getProcessMatch():
                    del event.getEquipment().getProcessMatch()[event]    
            else:   
                if not event.getName() in ["Machine Unloading","Machine Loading"]:
                    if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                        self.getSimulator().saveLog(" REPORT: event : "+str(event.getName())+"("+str(event.getID())+") equip is made None!!~~")
                        self.getSimulator().saveLog(" REPORT: statement : "+str(event.getName() != "Machine Unloading" or event.getName() != "Machine Loading"))
                    event.setEquipment(None)               
                event.setResource(None)
            #self.getSimulator().saveLog(" REPORT: event in time list? "+str(event in self.getSimulator().getEventQueue()[self.getSimulator().getTime()])) 

            
            if event in self.getSimulator().getEventQueue()[self.getSimulator().getTime()]:
                self.getSimulator().getEventQueue()[self.getSimulator().getTime()].remove(event)
            #self.getSimulator().saveLog(" REPORT: event in time list? "+str(event in self.getSimulator().getEventQueue()[self.getSimulator().getTime()])) 
            #self.getSimulator().saveLog(" REPORT: event SuspendedSuccessor none? "+str(event.getSuspendedSuccessor() == None)) 


            if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                    self.getSimulator().saveLog(" REPORT: event has suspended predecessor?  "+str(event.getSuspendedPredecessor() != None)) 
            if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                    self.getSimulator().saveLog(" REPORT: event has suspended successor?  "+str(event.getSuspendedSuccessor() != None)) 
            
            if event.getSuspendedSuccessor() == None:
                if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                    self.getSimulator().saveLog(" REPORT: event to be added to pending list ? "+str(event in self.getSimulator().getEventQueue()["Pending"])+", equip none? "+str(event.getEquipment() == None)) 
                
                self.getSimulator().getEventQueue()["Pending"].append(event)
                if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                    self.getSimulator().saveLog(" REPORT: event added to pending list ? "+str(event in self.getSimulator().getEventQueue()["Pending"])+", equip none? "+str(event.getEquipment() == None)) 

            #if event.getSimStartSuccessor()!= None:
            #    if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
            #        self.getSimulator().saveLog(" REPORT: simstart successor removed from schedule "+event.getSimStartSuccessor().getName()+"("+str(event.getSimStartSuccessor().getID())+") ") 
            #    if event.getSimStartSuccessor() in self.getSimulator().getEventQueue()[self.getSimulator().getTime()]:
            #        self.getSimulator().getEventQueue()[self.getSimulator().getTime()].remove(event.getSimStartSuccessor())

                    
            

        if case == "Complete": 
            if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                self.getSimulator().saveLog(" REPORT: event: "+str(event.getName())+" completion updates start..") 
            self.makeCompletionUpdates(event,debugtimes,debugeventids,debugmachines)
            
            if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                self.getSimulator().saveLog(" REPORT: completion updates done.. res location: "+str(event.getResource().getLocation().getName())) 
                if isinstance(event.getEquipment(),Trailer):
                    if event.getEquipment() != None:
                        self.getSimulator().saveLog("REPORT: event : "+str(event.getName())+"("+str(event.getID())+"), equipment "+event.getEquipment().getName()+", equip-items "+str(len(event.getEquipment().getItems())))

            if event.getType() == "Unloading" and (isinstance(event.getEquipment(),Machine)):
                if not event.getItems()[0] in event.getToLocation().getItems():
                    self.getSimulator().saveLog(" ERROR: completion "+str(event.getName())+"("+str(event.getID())+") done but first item not in to-location!!! "+str(event.getLocation().getName())) 
                
        if (specialcheck and case == "Complete"):
            self.getSimulator().saveLog("REPORT: ************************** event : "+str(event.getName())+"("+str(event.getID())+") case "+case)
     


        
        if case == "Handle":  # register the progress

            # check necessary condition: 
            if event.getType() == "Loading" and isinstance(event.getEquipment(),Machine):
                if event.getEquipment().getNoProcessors() == 1:
                    if len(event.getEquipment().getItems()) > 0: 
                        self.getSimulator().saveLog("ERROR: processing event : "+str(event.getName())+"("+str(event.getID())+"), has equipment "+event.getEquipment().getName()+", equip-items "+str(len(event.getEquipment().getItems())))
            
            # remove from pending list, if event is in it.
            if event in self.getSimulator().getEventQueue()["Pending"]:
                self.getSimulator().getEventQueue()["Pending"].remove(event)
              
            # remove from the time events list, if event is in it.
            if self.getSimulator().getTime() in self.getSimulator().getEventQueue():
                if event in self.getSimulator().getEventQueue()[self.getSimulator().getTime()]:
                    self.getSimulator().getEventQueue()[self.getSimulator().getTime()].remove(event)   

            if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                self.getSimulator().saveLog(" REPORT: logs events: "+str(len(event.getLogisticalEvents()))) 
                
            if len(event.getLogisticalEvents()) == 0: 
                
                progress_start = self.getSimulator().getTime()
                progress_end = progress_start+(event.getProcessTime()-event.getTotalProgress())

                
                if event.getEventType().isPreemptable():
                    progress_end = min(progress_end,self.getCurrentShiftEnd()) 
                else:
                    if progress_end > self.getCurrentShiftEnd():
                        progress_end = progress_start # trick to make zer progress step
      
                if progress_end > progress_start:
                    progress_step = (progress_start,progress_end)
                    event.getProgressList().append((event.getResource(),progress_step))
                    if event.getType() == "Processing":
                        if event.getResource() != None:
                            event.getResource().getProgressList().append((event,progress_step))
                        

                    if event.getSuspendedPredecessor() != None:
                        if event.getSuspendedPredecessor().getResource()!= None: 
                            event.getSuspendedPredecessor().getProgressList().append((event.getSuspendedPredecessor().getResource(),progress_step))

                            if event.getSuspendedPredecessor().getType() == "Processing":
                                event.getSuspendedPredecessor().getResource().getProgressList().append((event.getSuspendedPredecessor(),progress_step))
                                
                        if not progress_step[1] in self.getSimulator().getEventQueue():
                            self.getSimulator().getEventQueue()[progress_step[1]] = []    

                        if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids or event.getEquipment().getName() in debugmachines:
                            self.getSimulator().saveLog(" REPORT: suspended predecessor "+event.getSuspendedPredecessor().getName()+"("+str(event.getSuspendedPredecessor().getID())+") scheduled  at "+str(progress_step[1])) 
                        self.getSimulator().getEventQueue()[progress_step[1]].append(event.getSuspendedPredecessor())
    
                    if not progress_step[0] in self.getSimulator().getEventQueue():
                        self.getSimulator().getEventQueue()[progress_step[0]] = []
                    if not event in self.getSimulator().getEventQueue()[progress_step[0]]:   
                        self.getSimulator().getEventQueue()[progress_step[0]].append(event) 
    

        ########################################   
        # SCHEDULE UPDATES   

         # remove progress step start and schedule the end of progress step
        if case == "Start":
            if event.getType() == "Unloading" and (isinstance(event.getEquipment(),Machine)):
                if not event.getItems()[0] in event.getFromLocation().getItems():
                    self.getSimulator().saveLog(" ERROR: start "+str(event.getName())+"("+str(event.getID())+") but first item not in from-location!!! "+str(event.getLocation().getName())) 
                
            if event.getType() == "Transport":               
                if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                    self.getSimulator().saveLog(" REPORT: checking transport event items "+event.getName()+"("+str(event.getID())+"), event items "+str(len(event.getItems()))+", equip items: "+str(len(event.getEquipment().getItems()))) 
                if not event.getItems()[0] in event.getEquipment().getItems():
                    self.getSimulator().saveLog(" ERROR: transport event "+event.getName()+"("+str(event.getID())+") first item is not in equipment!!") 

         
        if case == "Restart":
            
            if event.getSimStartSuccessor()!= None:
                #if not event.getSimStartSuccessor() in self.getSimulator().getEventQueue()[self.getSimulator().getTime()]:
                #    self.getSimulator().getEventQueue()[self.getSimulator().getTime()].append(event.getSimStartSuccessor())

                progress_start = self.getSimulator().getTime()
                #progress_end = progress_start+(event.getSimStartSuccessor().getProcessTime()-event.getSimStartSuccessor().getTotalProgress())

                #if event.getSimStartSuccessor().getEventType().isPreemptable():
                #    progress_end = min(progress_end,self.getCurrentShiftEnd()) 


                #progress_step = (progress_start,progress_end)

                if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                    self.getSimulator().saveLog(" REPORT: simstart successor also restarted "+event.getSimStartSuccessor().getName()+"("+str(event.getSimStartSuccessor().getID())+")  prog strt "+str(progress_start)) 

                #event.getSimStartSuccessor().getProgressList().append((event.getSimStartSuccessor().getResource(),progress_step))
        

                

        
        if case in ["Start","Restart"]:

            event.getReservedItems().clear() 
  
            progress_start = event.getProgressList()[-1][1][0]
            progress_end = event.getProgressList()[-1][1][1]
            
            if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                self.getSimulator().saveLog(" REPORT: event last progress: "+str(event.getProgressList()[-1][1])) 
                
            if event in self.getSimulator().getEventQueue()[progress_start]:
                self.getSimulator().getEventQueue()[progress_start] = [x for x in self.getSimulator().getEventQueue()[progress_start] if x != event]
            #self.getSimulator().saveLog(" REPORT: event in?: "+str(event in self.getSimulator().getEventQueue()[progress_start])) 
                
            if not progress_end in self.getSimulator().getEventQueue():
                self.getSimulator().getEventQueue()[progress_end] = []
            self.getSimulator().getEventQueue()[progress_end].append(event) # end of the progress step: suspend/complete

            if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                self.getSimulator().saveLog(" REPORT: event has suspended predecessor? : "+str(event.getSuspendedPredecessor() != None)) 
      
            if event.getSuspendedPredecessor() != None:
                if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                    self.getSimulator().saveLog(" REPORT: suspended predecessor last progress : "+str(event.getSuspendedPredecessor().getProgressList()[-1][1])) 
                
                if event.getSuspendedPredecessor().getProgressList()[-1][1][1] < progress_end: 
                    
                    progress_step = (progress_start,progress_end)
                    event.getSuspendedPredecessor().getProgressList().append((event.getSuspendedPredecessor().getResource(),progress_step))

                    if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                        self.getSimulator().saveLog(" REPORT: suspended predecessor last progress defined: "+str(progress_step)) 
                        self.getSimulator().saveLog(" REPORT: suspended predecessor allassigned? : "+str(event.getSuspendedPredecessor().checkAllAssigned("Handle"))) 

                        
                    
                    if event.getSuspendedPredecessor().getType()== "Processing":
                        if event.getSuspendedPredecessor().getResource()!= None:
                            event.getSuspendedPredecessor().getResource().getProgressList().append((event.getSuspendedPredecessor(),progress_step))
                        
                    if not progress_step[1] in self.getSimulator().getEventQueue():
                        self.getSimulator().getEventQueue()[progress_step[1]] = []


                    
                    if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                        self.getSimulator().saveLog(" REPORT: suspended predecessor " +event.getSuspendedPredecessor().getName()+"("+str(event.getSuspendedPredecessor().getID())+") scheduled at"+str(progress_step[1])) 
          
                    self.getSimulator().getEventQueue()[progress_step[1]].append(event.getSuspendedPredecessor())
        
       ########################################   
        
       # Check precedences
        if event.getType() != "Logistical":    
            for successor_type,precedence_type in event.getEventType().getSuccessorDict().items():
                create_successor = False; 
                if self.getSimulator().getTime() in debugtimes and event.getID() in debugeventids:
                    self.getSimulator().saveLog("REPORT: case "+case+", successor_type "+str(successor_type.getName())+", pred_type: "+precedence_type)
                    
                if (case == "Start" and precedence_type == "Simultaneous Start") or (case == "Complete" and precedence_type == "Finish to Start"):
                    create_successor = True
                if (case == "Start" or case == "Restart") and (precedence_type == "CompletionRatio Start"): 
                    create_successor = True

                if create_successor:
                    successor_event = ExecEvent(None,None,successor_type)

                    
                    if self.getSimulator().getTime() in debugtimes or successor_event.getID() in debugeventids: 
                        self.getSimulator().saveLog("REPORT: **** successor_event "+successor_event.getName()+"("+str(successor_event.getID())+")")
                        self.getSimulator().saveLog("REPORT: event : "+str(event.getName())+"("+str(event.getID())+")"+", loc :"+event.getLocation().getName()+", res none? "+str(event.getResource() == None)+", processor none? "+str(event.getProcessor()== None)+", p: "+str(event.getProcessTime())+", in pendings? "+str(event in self.getSimulator().getEventQueue()["Pending"])+", pred? "+str(event.getPredecessor() != None))
                        self.getSimulator().saveLog("REPORT: tot.prog: "+str(event.getTotalProgress())+str(["("+str(pr[0])+"-"+str(pr[1])+")" for r,pr in event.getProgressList()]))
                         
                    if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                        self.getSimulator().saveLog("REPORT: **** successor_event "+successor_event.getName()+"("+str(successor_event.getID())+")")
                    self.applyPrecedence(event,successor_event,successor_type)

                
                    
                    if self.getSimulator().getTime() in debugtimes or (event.getID() in debugeventids or successor_event.getID() in debugeventids) :
                        self.getSimulator().saveLog("REPORT: precendence info applied successor_event "+successor_event.getName()+"("+str(successor_event.getID())+")")

                        if successor_event.getType() == "Processing":
                            self.getSimulator().saveLog("REPORT: event : "+str(event.getName())+"("+str(event.getID())+") case "+case+", loc :"+event.getLocation().getName()+", res none? "+str(event.getResource() == None)+", processor none? "+str(event.getProcessor()== None)+", p: "+str(event.getProcessTime())+", in pendings? "+str(event in self.getSimulator().getEventQueue()["Pending"])+", pred? "+str(event.getPredecessor() != None))
                            self.getSimulator().saveLog(" REPORT: succ event : "+str(successor_event.getName())+"("+str(successor_event.getID())+") items ["+(str(successor_event.getItems()[0].getID()) if len(successor_event.getItems())>0 else '')+"-"+(str(successor_event.getItems()[-1].getID()) if len(successor_event.getItems())>0 else '')+"]")
                            self.getSimulator().saveLog(" REPORT: event machine items : "+str(event.getEquipment().getName())+", "+str(len(event.getEquipment().getItems()))+" items ["+(str(event.getEquipment().getItems()[0].getID())+"-"+str(event.getEquipment().getItems()[-1].getID()) if len(event.getEquipment().getItems())>0 else '')+"]")

       
                    if ((successor_event.getEquipment() == None) or (successor_event.getResource() == None)) and (successor_event.getName() != "Machine Processing" and successor_event.getName() != "Machine Unloading") : 
                        self.getSimulator().getEventQueue()["Pending"].append(successor_event)
                        if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                            self.getSimulator().saveLog("REPORT: succcessor pending ")
                                
                    else: # now progress step can be determined
                        if successor_event.getType() == "Transport": 
                            if successor_event.getToLocation()== None:
                                if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                                    self.getSimulator().saveLog("REPORT: succcessor destination to be selected.. ")
                                decision_type = "Select Destination"
                                algname = self.getAlgorithmSetting()[successor_event.getName()][decision_type]
                                algfunction = self.getProductionAlgManager().getDecisionAlgorithms()[decision_type][algname]
                                alg_return = algfunction(event)
                                if alg_return!= None:
                                    successor_event.setToLocation(alg_return.getInputBuffer())

                        if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                            self.getSimulator().saveLog("REPORT: succcessor event process sampling")
                             
                        successor_event.sampleProcessTime(self); proctime = successor_event.getProcessTime() 

                        if self.getSimulator().getTime() in debugtimes or successor_event.getID() in debugeventids:
                                self.getSimulator().saveLog("REPORT: event process time sampling  "+successor_event.getName()+"("+str(successor_event.getID())+") and pred event "+event.getName()+"("+str(event.getID()))
                        
                        if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                            self.getSimulator().saveLog("REPORT: succcessor event process time: "+str(proctime))

                        successor_start = self.getSimulator().getTime()  
                        successor_end = successor_start+proctime

                        if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                            self.getSimulator().saveLog("REPORT: precedence_type: "+str(precedence_type))
                            
                        if precedence_type == "CompletionRatio Start":
                            if len(event.getProgressList()) > 0:
                                
                                last_progress = event.getProgressList()[-1][1]
                                last_prog_len = last_progress[1]-last_progress[0]
                                remaining_time = event.getProcessTime() - event.getTotalProgress()
                                last_resource = event.getProgressList()[-1][0]
                                
                                if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                                    self.getSimulator().saveLog("REPORT: remaining_time: "+str(remaining_time))
                                    self.getSimulator().saveLog("REPORT: last_prog_len: "+str(last_prog_len))

                              
                                if (remaining_time + last_prog_len > proctime) and (remaining_time <= proctime):
                                    successor_start = last_progress[0] + (remaining_time + last_prog_len - proctime)
                                    successor_end = successor_start+proctime
                                else:
                                    if event.getProcessTime() == 1:
                                        successor_end = successor_start+1
                                    else:
                                        successor_end = successor_start-1 # do not activate successor, negative progress step.

                                if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                                    self.getSimulator().saveLog("REPORT: successor_start: "+str(successor_start))
                                   
                        if successor_event.getEventType().isPreemptable():
                            successor_end = min(successor_end,self.getCurrentShiftEnd()) 
                        else:
                            if successor_end > self.getCurrentShiftEnd():
                                successor_start = self.getCurrentShiftEnd() # check handling in the next shift
                                successor_end = successor_start # zero progress step

                        if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                            self.getSimulator().saveLog("REPORT: successor_start: "+str(successor_start)+", successor_end: "+str(successor_end))

                        
                        if (successor_end - successor_start > 0): 
                            progress_step = (successor_start,successor_end)

                            if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                                self.getSimulator().saveLog("REPORT: successor_ all assigned: "+str(successor_event.checkAllAssigned("Handle")))

                          
                            
                            if successor_event.checkAllAssigned("Handle"):
                                successor_event.getProgressList().append((successor_event.getResource(),progress_step))
                                if isinstance(successor_event.getResource(),Machine):
                                    successor_event.getResource().getProgressList().append((successor_event,progress_step))

                                    
                            if precedence_type == "CompletionRatio Start":
                                if len(event.getProgressList()) > 0:
                                    last_resource = event.getProgressList()[-1][0]
                                    last_progress = event.getProgressList()[-1][1]

                                    if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                                        self.getSimulator().saveLog("REPORT: event last progress end: "+str(last_progress[1])+", scheduled? "+str(last_progress[1] in self.getSimulator().getEventQueue()))
                                        self.getSimulator().saveLog("REPORT: event last progress start: "+str(last_progress[0])+", scheduled? "+str(last_progress[0] in self.getSimulator().getEventQueue()))
                                    
                                    if last_progress[1] in self.getSimulator().getEventQueue():
                                        if event in self.getSimulator().getEventQueue()[last_progress[1]]:
                                            self.getSimulator().getEventQueue()[last_progress[1]].remove(event)
                                            if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                                                self.getSimulator().saveLog("REPORT: event scheduled at time? (should be removed): "+str(event in self.getSimulator().getEventQueue()[last_progress[1]]))

                                    if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                                         self.getSimulator().saveLog("REPORT: event re-progressed: "+str((last_progress[0],successor_start)))
                                        
                                    event.getProgressList()[-1] = (last_resource,(last_progress[0],successor_start))
                                    
                                    if isinstance(last_resource,Machine):
                                        for resprogress_id in range(len(last_resource.getProgressList())):
                                            myevent,resprogress = last_resource.getProgressList()[resprogress_id]
                                            if resprogress[0] == last_progress[0] and resprogress[1] == last_progress[1]:
                                                if myevent == event:
                                                    last_resource.getProgressList()[resprogress_id]=(event,(last_progress[0],successor_start))
                                                    break
                                    successor_event.setSuspendedPredecessor(event)
                                    event.setSuspendedSuccessor(successor_event)

                            if self.getSimulator().getTime() in debugtimes or successor_event.getID() in debugeventids:
                                self.getSimulator().saveLog("REPORT: pred event  "+event.getName()+"("+str(event.getID())+") of event "+successor_event.getName()+"("+str(successor_event.getID()))

                            
                            if precedence_type == "Simultaneous Start":
                                event.setSimStartSuccessor(successor_event)
                                successor_event.setSimStartPredecessor(event)
                                
                           
                            if not successor_start in self.getSimulator().getEventQueue():
                                self.getSimulator().getEventQueue()[successor_start] = []
                            if not successor_event in self.getSimulator().getEventQueue()[successor_start]:
                                self.getSimulator().getEventQueue()[successor_start].append(successor_event)
                                if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                                    self.getSimulator().saveLog("REPORT: successor_event scheduled at time: "+str(successor_start)+", progs: "+str(len(successor_event.getProgressList())))

                           
                            
                          
                        else:
                            if successor_end == successor_start:

                                if precedence_type == "CompletionRatio Start":
                                    successor_event.setSuspendedPredecessor(event)
                                    event.setSuspendedSuccessor(successor_event)
                                
                                if not successor_start in self.getSimulator().getEventQueue():
                                    self.getSimulator().getEventQueue()[successor_start] = []
                                if not successor_event in self.getSimulator().getEventQueue()[successor_start]:
                                    self.getSimulator().getEventQueue()[successor_start].append(successor_event)
                                    
                                
  
        else:
            successor_event = event.getSuccessor()
            if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                self.getSimulator().saveLog("REPORT: logistical ev,  succcessor event "+str(successor_event.getName())+"("+str(successor_event.getID())+")")
     
            if case == "Complete":
                if successor_event.getType() != "Logistical":
                    if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                        self.getSimulator().saveLog("REPORT: logistical ev,  succcessor event progress steps "+str(len(successor_event.getProgressList())))
     
                    progress_start = self.getSimulator().getTime(); 
                    progress_end = progress_start+(successor_event.getProcessTime()-successor_event.getTotalProgress())

                    if successor_event.getEventType().isPreemptable():
                        progress_end = min(progress_end,self.getCurrentShiftEnd())

                    
                    if progress_end - progress_start > 0: #$ schedule start of successor event
                        successor_event.getProgressList().append((successor_event.getResource(),(progress_start,progress_end)))

                        if not progress_start in self.getSimulator().getEventQueue():
                            self.getSimulator().getEventQueue()[progress_start] = []
                                
                        if not successor_event in self.getSimulator().getEventQueue()[progress_start]:   
                            self.getSimulator().getEventQueue()[progress_start].append(successor_event) # start of the progress step: start/restart
                        

                    for event in successor_event.getLogisticalEvents():
                        successor_event.getLogisticalEvents().remove(event)
                        #self.getSimulator().saveLog("REPORT: >>> logistical event "+log_event.getName()+" is removed from event "+successor_event.getName())
                        
                else:

                    if self.getSimulator().getTime() in debugtimes or successor_event.getID() in debugeventids:
                        self.getSimulator().saveLog("REPORT: logistical ev, logistical succcessor event "+str(successor_event.getName())+"("+str(successor_event.getID())+"), progress "+str(successor_event.getProgressList()[-1][1]))
                        
                    progress_end = successor_event.getProgressList()[-1][1][1]
                    if not progress_end in self.getSimulator().getEventQueue():
                        self.getSimulator().getEventQueue()[progress_end] = []
                        
                    if not successor_event in self.getSimulator().getEventQueue()[progress_end]:   
                        self.getSimulator().getEventQueue()[progress_end].append(successor_event) 
    
                    #self.getSimulator().saveLog("REPORT: end of next logistical event "+successor_event.getName()+" is scheduled")
                    
       

        if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
            self.getSimulator().saveLog("REPORT: ______________________________________________________________________")

            if self.getSimulator().getTime() in self.getSimulator().getEventQueue():
                if event in self.getSimulator().getEventQueue()[self.getSimulator().getTime()]:
                    self.getSimulator().saveLog("REPORT: event in schedule of current time")

            if self.getSimulator().getTime()+1 in self.getSimulator().getEventQueue():
                if event in self.getSimulator().getEventQueue()[self.getSimulator().getTime()+1]:
                    self.getSimulator().saveLog("REPORT: event in schedule of current time+1")
                

        if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
            oprseq = []
            if len(event.getItems()) > 0:
                oprseq = event.getItems()[0].getDemand().getFinalProduct().getOperationSequences()[event.getItems()[0].getDemand().getID()]
                self.getSimulator().saveLog("REPORT: event : "+str(event.getName())+"("+str(event.getID())+"), items "+str(len(event.getItems()))+", active opr none? "+("No item " if len(event.getItems())==0 else str(event.getItems()[0].getActiveOperation()== None))+", in pendings? "+str(event in self.getSimulator().getEventQueue()["Pending"]))
                self.getSimulator().saveLog("REPORT: event : "+str(event.getName())+"("+str(event.getID())+"), items "+str(len(event.getItems()))+", active opr none? "+("No item " if len(event.getItems())==0 else str(event.getItems()[0].getActiveOperation()== None))+" event loc "+event.getLocation().getName()+", item oprs "+str([str(o.isCancelled())+"--"+str(o.isFinished())+"--"+str(o.getName()) for o in oprseq])+", equip none? "+str(event.getEquipment() == None)+", tot.prog: "+str(event.getTotalProgress())+", p: "+str(event.getProcessTime())+", case: "+case)
     
        return
###############################################################################################################################################
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
        if 'ToLocation->Resource' in precedenceinfo: # ML->Proc
            successor_event.setResource(event.getToLocation())

        # setItems: TL->TT, MS->Ml, ML->Proc, Proc->MU
        if 'Items' in precedenceinfo:
            for item in event.getItems():
                if item.getReservedEvent() == event:
                    item.setReservedEvent(successor_event)
                successor_event.getItems().append(item)

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
        if 'FromLocationOutput->ToLocation' in precedenceinfo: # Proc->MU
            successor_event.setToLocation(event.getFromLocation().getOutputBuffer())


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
    def makeCaseDecisions(self,event,case,debugtimes,debugeventids):

         # MAKE NECESSARY DECISIONS...
        casesuccess = True; success_decisions = [] 
            
        if case in event.getEventType().getDecisionsDict():
            
            
            for decision_type in event.getEventType().getDecisionsDict()[case]:
                if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                    self.getSimulator().saveLog("REPORT: event : "+str(event.getName())+" decision "+str(decision_type)+", decision_type"+str(decision_type)+" items "+str(len(event.getItems())))
                

                if decision_type == "Assign Processor": 
                    if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                        self.getSimulator().saveLog("REPORT: event : "+str(event.getName())+" decision "+str(decision_type)+", processor none? "+str(event.getProcessor()== None)+" continued..")
                    if event.getProcessor()!= None:
                        continue
                if decision_type == "Select Items": 
                    if len(event.getItems()) > 0:
                        continue

                algname = self.getAlgorithmSetting()[event.getName()][decision_type] 
                algfunction = self.getProductionAlgManager().getDecisionAlgorithms()[decision_type][algname] 
                alg_return = algfunction(event)

                if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                    self.getSimulator().saveLog("REPORT: event : "+str(event.getName())+" alg_return none?"+str(alg_return== None))
       
                if alg_return!= None:
                    if decision_type == "Select Items":   # TL/TU/MS (handle)
                        if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                            self.getSimulator().saveLog("REPORT: event : "+str(event.getName())+" selected items ?"+str(len(alg_return)))
                        # apply selection
                        for item in alg_return:
                            event.getItems().append(item) 
                            item.setReservedEvent(event)
 
                    if decision_type == "Assign Processor":  # MS, MProc
                        event.getEquipment().getProcessMatch()[event] = alg_return # return is a processor of the equipment
                        event.setProcessor(alg_return)

                    if decision_type == 'Select Destination':  # MS, MProc
                        event.setToLocation(alg_return.getInputBuffer())
           
                    if decision_type == "Assign Equipment":  # TL/MS (handle), Proc(restart)        
                        event.setEquipment(alg_return) # process: inserts this start into progress dict of equip
                        if event.getName() == "Trailer Loading":
                            event.setToLocation(alg_return) 
                        alg_return.setIdle(False)

                        # Important: For Outsourced, how to handle operator requirement for Machine Loading and Unloading (Relax this requirement!)?
                       
                    if decision_type == "Assign Resource": # TL/MS/ML/MU (handle), ML/MU (resart)
                        event.setResource(alg_return) 
                        alg_return.setIdle(False)
                        
                    success_decisions.append(decision_type)
                else:
                    casesuccess = False # only can happen for assign equipment/resource
                    if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                        self.getSimulator().saveLog("REPORT: no success in handling decision type: "+decision_type)
                    break 
        if not casesuccess: # backtrack the decisions
            self.resetDecisions(event,success_decisions,debugtimes,debugeventids)
        else:
            if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                self.getSimulator().saveLog("REPORT: event"+str(event.getName())+"("+str(event.getID())+")"+" success in decisions: "+str(success_decisions)+", decisions: "+(str(event.getEventType().getDecisionsDict()[case]) if case in event.getEventType().getDecisionsDict() else ""))

            if "Handle" in event.getEventType().getDecisionsDict() and (not case in ["Suspend","Complete"]):
                if "Assign Resource" in event.getEventType().getDecisionsDict()["Handle"]:
                    if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                        self.getSimulator().saveLog("REPORT: event"+str(event.getName())+"("+str(event.getID())+") checking logistical events")
                    feasible,operator_move,bring_equipment = self.checkLogisticalEvents(event,success_decisions,debugtimes,debugeventids)

                    
                    if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                        self.getSimulator().saveLog("REPORT: event"+str(event.getName())+"("+str(event.getID())+") checking logistical events feas.: "+str(feasible))
    
                    if not feasible: 
                        self.resetDecisions(event,success_decisions,debugtimes,debugeventids)
                        casesuccess = False
                    else:

                        # now check if the event chain can stay in the same shift..
                        if case == "Handle" and event.getType() == "Loading" and isinstance(event.getEquipment(),Trailer):
                        # now check the complete time needed for the chain of events and if they will stay in the same shift. 

                            if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                                 self.getSimulator().saveLog("REPORT: >>>>>>>>> calculating total time : "+str(event.getName())+"("+str(event.getID())+")")
                            
                            totaltime =(operator_move.getProcessTime() if operator_move!= None else 0)
                            totaltime+=(bring_equipment.getProcessTime() if bring_equipment!= None else 0) 
                            totaltime+= event.getProcessTime()
                
                            if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                                 self.getSimulator().saveLog("REPORT: >>>>>>>>> calculating total time : "+str(event.getName())+"("+str(event.getID())+") t: "+str(totaltime))
                
                            # now check the successors of the event in the event chain.
                            current_event = event
                            successor_event = None
                
                            while current_event!= None:

                                if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                                    self.getSimulator().saveLog("REPORT: current event >>>>: "+str(current_event.getName())+"("+str(current_event.getID())+")  t: "+str(totaltime))
                                
                                for successor_type,precedence_type in current_event.getEventType().getSuccessorDict().items():
                                    if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                                        self.getSimulator().saveLog("REPORT: $$$$$$$ calculating total time : "+str(current_event.getName())+"("+str(current_event.getID())+")  successor_type "+str(successor_type.getName())+", precedence_type ("+str(precedence_type)+".")
                                    if precedence_type == "Finish to Start": # this is only for transport events for now
                                        successor_event = ExecEvent(None,None,successor_type)
                                        self.applyPrecedence(current_event,successor_event,successor_type)

                                        if successor_event.getFromLocation()!= None: 
                                            
                                            if successor_event.getToLocation() == None: 
                                                if successor_event.getName() in self.getAlgorithmSetting():
                                                   
                                                    mydecision_type = "Select Destination"
                                                    if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                                                        self.getSimulator().saveLog("REPORT: successor event >>>>: "+str(successor_event.getName())+"("+str(successor_event.getID())+")  finding algortihm., is mydecision in alg setting? "+str( mydecision_type in self.getAlgorithmSetting()[successor_event.getName()]))
                                                    if mydecision_type in self.getAlgorithmSetting()[successor_event.getName()]:
                                                        
                                                        algname = self.getAlgorithmSetting()[successor_event.getName()][mydecision_type]
                                                        if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                                                            self.getSimulator().saveLog("REPORT: successor event >>>>: "+str(successor_event.getName())+"("+str(successor_event.getID())+")  finding algortihm,  alg name "+str(algname)+" equip none? "+str(successor_event))
                                                        algfunction = self.getProductionAlgManager().getDecisionAlgorithms()[mydecision_type][algname]
                                                        alg_return = algfunction(successor_event)
                                                        if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                                                            self.getSimulator().saveLog("REPORT: successor event >>>>: "+str(successor_event.getName())+"("+str(successor_event.getID())+")  finding algortihm,  alg return none? "+str(alg_return == None))
                                                        if alg_return!= None:
                                                            successor_event.setToLocation(alg_return.getInputBuffer())

                                            if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                                                self.getSimulator().saveLog("REPORT: successor event >>>>: "+str(successor_event.getName())+"("+str(successor_event.getID())+")  tolocation none?: "+str(successor_event.getToLocation() == None))

                                            if successor_event.getToLocation() != None: 
                                                successor_event.sampleProcessTime(self)
                                                totaltime+=successor_event.getProcessTime()
                                                break
                                        else: 
                                            if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                                                self.getSimulator().saveLog("REPORT: calculating total time : "+str(current_event.getName())+"("+str(current_event.getID())+")  from location of successor "+str(successor_event.getName())+"("+str(successor_event.getID())+") is none!")
                                

                                if successor_event!= None:
                                     if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                                        self.getSimulator().saveLog("REPORT: calculating total time successor : "+str(successor_event.getName())+"("+str(successor_event.getID())+").")
                                current_event = successor_event
                                successor_event = None
                            if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                                if current_event!= None: 
                                    self.getSimulator().saveLog("REPORT: ~~~~~~~~~~~~ calculating total time : "+str(current_event.getName())+"("+str(current_event.getID())+") *t: "+str(totaltime)+", overflowing to next shift? "+str(self.getSimulator().getTime()+totaltime > self.getCurrentShiftEnd()-1))
                                
                            if self.getSimulator().getTime()+totaltime > self.getCurrentShiftEnd()-1:
                                casesuccess = False

                        if casesuccess:
                    
                            first_logistical = operator_move if (operator_move!= None) else (bring_equipment if bring_equipment != None else None)
                            if first_logistical!=None:
                                if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                                    self.getSimulator().saveLog("REPORT: logistical event : "+str(first_logistical.getName())+"("+str(first_logistical.getID())+")")
                                event.getLogisticalEvents().append(first_logistical)
                                progress_step = first_logistical.getProgressList()[-1][1]
                                if not progress_step[1] in self.getSimulator().getEventQueue():
                                    self.getSimulator().getEventQueue()[progress_step[1]] = []
                                self.getSimulator().getEventQueue()[progress_step[1]].append(first_logistical) 
                                if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                                 self.getSimulator().saveLog("REPORT: logistical scheduled completion at "+str(progress_step[1]))
    
                                if event in self.getSimulator().getEventQueue()["Pending"]:
                                    self.getSimulator().getEventQueue()["Pending"].remove(event)
                                    if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                                        self.getSimulator().saveLog("REPORT: event removed from pendings ? "+str(event in self.getSimulator().getEventQueue()["Pending"]))
                                    
                                if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                                    self.getSimulator().saveLog("REPORT: lprogress_step : "+str(progress_step))
            
                                if (bring_equipment != None) and (not bring_equipment in event.getLogisticalEvents()):
                                    event.getLogisticalEvents().append(bring_equipment)
                        
                              
        return casesuccess
        
############################################################################################################################
    def checkLogisticalEvents(self,event,success_decisions,debugtimes,debugeventids):
        feasible = True; operator_move = None; bring_equipment = None; OprMovPT = 0          
        equipment_onlocation = True; resource_onlocation = True
                    
        for decision_type in success_decisions:
            if decision_type == "Assign Equipment":
                if event.getName() != "Machine Setup":
                    equipment_onlocation = (event.getEquipment().getLocation() == event.getLocation())
                 
            if decision_type == "Assign Resource":
                resource_onlocation =  (event.getResource().getLocation() == event.getLocation())

        if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
            self.getSimulator().saveLog("REPORT: event : "+event.getName()+"("+str(event.getID())+")"+", res on loc? "+str(resource_onlocation)+", equip on loc? "+str(equipment_onlocation)) 

        if not equipment_onlocation:
            
            bring_equipment = ExecEvent(event.getEquipment().getLocation(),event.getLocation(),self.getEventTypes()["Bring Equipment"])
            bring_equipment.sampleProcessTime(self)
       
            if event.getResource().getLocation() != event.getEquipment().getLocation():
                operator_move = ExecEvent(event.getResource().getLocation(),event.getEquipment().getLocation(),self.getEventTypes()["Operator Move"])
                operator_move.setEquipment(None);operator_move.setResource(event.getResource())
                operator_move.sampleProcessTime(self); OprMovPT = operator_move.getProcessTime()
            
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
            
            if self.getSimulator().getTime()+operator_move.getProcessTime() > self.getCurrentShiftEnd()-1:
                feasible = False
            else: 
                progress_step = (self.getSimulator().getTime(),min(self.getSimulator().getTime()+operator_move.getProcessTime(),self.getCurrentShiftEnd()))
                operator_move.getProgressList().append((operator_move.getResource(),progress_step))
      
        return feasible,operator_move,bring_equipment
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
#################################################################################################################################       
    def makeCompletionUpdates(self,event,debugtimes,debugeventids,debugmachines):

      # update execution data of event...
        progrss_steps = ""; step_id = 0
        for res,prstep in event.getProgressList():
            progrss_steps+=("" if step_id == 0 else "~")+str(prstep[0])+"-"+str(prstep[1])
            step_id+=1
                
        ev_items = ""; item_id = 0
        for item in event.getItems():
            ev_items+=("" if item_id == 0 else "~")+str(item.getID())
            item_id+=1
                
        execution_data = {"EventName":event.getName(),"EventID":event.getID(),"ProgressSteps":progrss_steps,"Items":ev_items,"Resource":("-" if event.getResource() == None else event.getResource().getName()),"Equipment":("-" if event.getEquipment() == None else event.getEquipment().getName()),"Location":event.getLocation().getName(),"SimTime":self.getSimulator().getTime(),"Date":self.getSimulator().getRealTime()}  
        self.getSimulator().getExecutionData().append(execution_data)

        if event.getResource()!= None: 
            if isinstance(event.getResource(),Operator):
                # "EntityName","EntityID","Time","LocationName","LocationID"
                location_data = {"EntityName":event.getResource().getName(),"EntityID":event.getResource().getID(),"Time":self.getSimulator().getTime(),"LocationName":event.getResource().getLocation().getName(),"LocationID": (event.getResource().getLocation().getID() if event.getResource().getLocation()!= None else "-")}  
                self.getSimulator().getLocationData().append(location_data)
               

     # update execution data of event...

    # update operation status in case machine processing
        if event.getType() == "Processing":
            if len(event.getItems()) > 0:
                oprseq = event.getItems()[0].getDemand().getFinalProduct().getOperationSequences()[event.getItems()[0].getDemand().getID()]
                #for opr in oprseq:
                    #self.getSimulator().saveLog("REPORT: opr: "+opr.getName()+", can?"+str(opr.isCancelled())+", fin?"+str(opr.isFinished()))
                    
                if event.getItems()[0].getActiveOperation() != None:
                    #self.getSimulator().saveLog("REPORT: >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Finished!!!!!")
                    if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                        for e in self.getSimulator().getEventQueue()[self.getSimulator().getTime()]:
                             self.getSimulator().saveLog(" REPORT: event: "+str(e.getName())+"("+str(e.getID())+")-["+(str(e.getItems()[0].getID()) if len(e.getItems())>0 else '')+"-"+(str(e.getItems()[-1].getID()) if len(e.getItems())>0 else '')+"]"+", active opr none? "+("No item " if len(e.getItems())==0 else (e.getItems()[0].getActiveOperation().getName() if e.getItems()[0].getActiveOperation()!= None else "No act opr"))+", loc "+(e.getLocation().getName() if event.getLocation() == None else "No loc")+", tot.prog: "+str(e.getTotalProgress())+", p: "+str(e.getProcessTime())+", succ event? none "+str(e.getSuspendedSuccessor() == None)) 

                   
                    #self.getSimulator().saveLog("REPORT: demand of removed one: "+str(event.getItems()[0].getDemand().getID()))   
                    event.getItems()[0].getActiveOperation().setFinished()
                    if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids:
                        for e in self.getSimulator().getEventQueue()[self.getSimulator().getTime()]:
                            if len(e.getItems())>0:
                                self.getSimulator().saveLog("REPORT: demand: "+str(e.getItems()[0].getDemand().getID()))   
                            self.getSimulator().saveLog(" REPORT: event: "+str(e.getName())+"("+str(e.getID())+")-["+(str(e.getItems()[0].getID()) if len(e.getItems())>0 else '')+"-"+(str(e.getItems()[-1].getID()) if len(e.getItems())>0 else '')+"]"+", active opr none? "+("No item " if len(e.getItems())==0 else (e.getItems()[0].getActiveOperation().getName() if e.getItems()[0].getActiveOperation()!= None else "No act opr"))+", loc "+(e.getLocation().getName() if event.getLocation() == None else "No loc")+", tot.prog: "+str(e.getTotalProgress())+", p: "+str(e.getProcessTime())+", succ event? none "+str(e.getSuspendedSuccessor() == None)) 

      
                if event in event.getEquipment().getProcessMatch():
                    del event.getEquipment().getProcessMatch()[event]
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
            event.getResource().setLocation(event.getToLocation())
            event.getEquipment().setLocation(event.getToLocation())

    
            
        if event.getType() in ["Loading","Unloading"]:

            
            if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids or event.getFromLocation().getName() in debugmachines:
                self.getSimulator().saveLog(" REPORT: ~~~ event : "+str(event.getName())+"("+str(event.getID())+") items ["+(str(event.getItems()[0].getID()) if len(event.getItems())>0 else '')+"-"+(str(event.getItems()[-1].getID()) if len(event.getItems())>0 else '')+"]")
                self.getSimulator().saveLog(" REPORT: ~~~ event.getFromLocation() : "+str(event.getFromLocation().getName())+", "+str(len(event.getFromLocation().getItems()))+" items ")


            itemno = 0

            if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids or event.getFromLocation().getName() in debugmachines:
                self.getSimulator().saveLog(" REPORT: item no: "+str(itemno)+" items in move place: "+str(len(event.getFromLocation().getItems()))+", tolocation: "+str(event.getToLocation().getName()))

    
            
            for myitem in event.getItems():   
                event.getFromLocation().getItems().remove(myitem)
                event.getToLocation().getItems().append(myitem)
                myitem.setReservedEvent(None)
                itemno+=1
                
            if self.getSimulator().getTime() in debugtimes or event.getID() in debugeventids or event.getFromLocation().getName() in debugmachines:
                self.getSimulator().saveLog(" REPORT: item move done...]")
                

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
                    event.getFromLocation().getInputBuffer().generateEvent(self.getSimulator().getTime() in debugtimes) # MU: Inputbuffer triggers Machine Setup
              
                #self.getSimulator().saveLog("REPORT: event generation triggered at: "+event.getFromLocation().getInputBuffer().getName())
                
            if event.getName() == "Trailer Loading":
                event.getFromLocation().generateEvent(self.getSimulator().getTime() in debugtimes) # TL: Outputbuffer triggers Trailer loading
                
         
            if event.getType() == "Unloading":         # TU:Inputbuffer triggers Machine Setup
                if self.getSimulator().getTime() in debugtimes:
                    self.getSimulator().saveLog("REPORT: >>> event to generate at: "+event.getToLocation().getName()+", input mach none? "+(str(event.getToLocation().getMachine() == None) if event.getToLocation().isInputType() else "no input") )
                event.getToLocation().generateEvent(self.getSimulator().getTime() in debugtimes)  # MU: Outputbuffer triggers Trailer loading
            
                if event.getEquipment() == None:
                    self.getSimulator().saveLog(" REPORT: event: "+str(event.getName())+str(event.getID())+", prog: "+str(event.getTotalProgress())+"-> "+str(["["+str(pr[1][0])+"-"+str(pr[1][1])+"]" for pr in event.getProgressList()])+", equip none 22 ") 
                event.getEquipment().setIdle(True)

        if event.getType() != "Logistical":
            if event.getResource() == None:
                self.getSimulator().saveLog(" REPORT: event: "+str(event.getName())+"("+str(event.getID())+"), resource none ") 
            event.getResource().setIdle(True)
        
        # remove the event from queue
        if event.getProgressList()[-1][1][1] in self.getSimulator().getEventQueue():
            if event in self.getSimulator().getEventQueue()[event.getProgressList()[-1][1][1]]:
                self.getSimulator().getEventQueue()[event.getProgressList()[-1][1][1]].remove(event)
 
  
        return 
#######################################################################################################################################################

#########################################################################################################################
    def writeData(self):

        event_df = pd.DataFrame(columns=["EventName","EventID","ProgressSteps","Items","Resource","Equipment","Location","SimTime","Date"])

        ######################################################################
        ## TO DO: Bryan ( Implementing the utilization ratio of machines
        """
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
                    if machine != None: 
                        for event,progress in machine.getProgressList():
                            processtime+= progress[1]-progress[0]

                    
        """
        ## TO DO: Bryan ( Implementing the utilization ratio of machines
        ######################################################################
        
                        
            
            

      
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
    def checkNecessaryConditions(self,event):

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

        

