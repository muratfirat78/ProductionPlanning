from Simulator import *
from datetime import timedelta,date
from productionobjects import *
from productionalgs import *
from productionChecker import *
from productiondata import *
from datetime import timedelta,date,datetime
import numpy as np



#################################################################################
class ShopFloorManager(OperationsManager): 
    def __init__(self,sim):
        super().__init__(sim)
        
        self.CentralInventory = Inventory(10000,sim,self) 
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

        # Trailer Loading -> Trailer Transport -> Trailer Unloading

        # Inputbuffer: Items change, it creates pending machine loading event. 

        #EventType: (myname,restype,equiptype,static,loading,process)
        trailerLoading = EventType("Trailer Loading","Operator","Trailer",True,True,False,False)
        trailerLoading.setItemDirection(True)  # Place -> Equipment, False means Equipment -> Place
        trailerLoading.getDecisions().append(('Handle','Assign Equipment'))
        trailerLoading.getDecisions().append(('Handle','Assign Resource'))
        trailerLoading.getDecisions().append(('Start','Select Items'))
        self.getEventTypes()["Trailer Loading"]= trailerLoading
        
        
        trailerTransport = EventType("Trailer Transport","Operator","Trailer",False,False,False,False)
        trailerTransport.getDecisions().append(('Start','Select Destination'))
        self.getEventTypes()["Trailer Transport"]= trailerTransport
        
        trailerUnloading = EventType("Trailer Unloading","Operator","Trailer",True,False,False,False);
        trailerUnloading.getDecisions().append(('Start','Select Items'))
        trailerUnloading.setItemDirection(False)  # Place -> Equipment, False means Equipment -> Place
        self.getEventTypes()["Trailer Unloading"]= trailerUnloading 

        
        bringEquipment = EventType("Bring Equipment","Operator","Trailer",False,False,False,False)
        self.getEventTypes()["Bring Equipment"]= bringEquipment 
        operatorMove = EventType("Operator Move","Operator","Operator",False,False,False,False)
        self.getEventTypes()["Operator Move"]= operatorMove 


        
        #EventType(myname,restype,equiptype,static,loading,process)

        machineSetup = EventType("Machine Setup","Operator","Machine",True,False,False,True)
        machineSetup.getDecisions().append(('Handle','Assign Equipment'))
        machineSetup.getDecisions().append(('Handle','Assign Resource'))
        machineSetup.getDecisions().append(('Handle','Select Items'))
        
        self.getEventTypes()["Machine Setup"]= machineSetup

        machineLoading = EventType("Machine Loading","Operator","Machine",True,True,False,False)
        machineLoading.getDecisions().append(('Handle','Assign Resource'))
        machineLoading.getDecisions().append(('Resume','Assign Resource'))
        machineLoading.setPreemptable(True)  
        self.getEventTypes()["Machine Loading"]= machineLoading
        machineLoading.setItemDirection(True) # True: Place -> Equipment, False: Equipment -> Place
        
        machineProcessing = EventType("Processing","Machine","Machine",True,False,True,False)
        machineProcessing.getDecisions().append(('Handle','Assign Equipment'))
        machineProcessing.setPreemptable(True)  
        self.getEventTypes()["Processing"]= machineProcessing
        
        machineUnloading = EventType("Machine Unloading","Operator","Machine",True,False,False,False) 
        machineUnloading.getDecisions().append(('Handle','Assign Resource'))
        machineUnloading.getDecisions().append(('Resume','Assign Resource'))
        machineUnloading.setItemDirection(False) # True: Place -> Equipment, False: Equipment -> Place
        machineUnloading.setPreemptable(True)  
        self.getEventTypes()["Machine Unloading"]= machineUnloading

        operatorMove.getPrecendenceDict()[trailerLoading.getName()] = ['Resource','Location','Finish to Start'] 
        bringEquipment.getPrecendenceDict()[trailerLoading.getName()] = ['Equipment','Resource','Location','Finish to Start'] 
        trailerLoading.getPrecendenceDict()[trailerTransport.getName()] = ['Equipment','Resource','Items','Location','Finish to Start']
        trailerTransport.getPrecendenceDict()[trailerUnloading.getName()] = ['Equipment','Resource','Location','Finish to Start']

        bringEquipment.setSuccessorType(trailerLoading)
        trailerLoading.setSuccessorType(trailerTransport)
        trailerTransport.setSuccessorType(trailerUnloading)

        

        # Machine Setup -> Machine Loading -> Processing -> Machine Unloading (manual and automated)

        # Outputbuffer: Items change, it creates pending trailer loading event. 
        machineSetup.setSuccessorType([machineLoading,machineProcessing])
        machineLoading.setPredecessorType(machineSetup)
        machineSetup.getPrecendenceDict()[machineLoading.getName()] = ['Equipment','Items','Location','Finish to Start']

        machineProcessing.setPredecessorType(machineLoading)
        machineLoading.getPrecendenceDict()[machineProcessing.getName()] = ['Equipment','Items','Location','Simultaneous Start']

        machineUnloading.setPredecessorType(machineProcessing)
        machineProcessing.getPrecendenceDict()[machineUnloading.getName()] = ['Equipment','Items','Location','Simultaneous Finish']

 

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

    def getSelectedOrders(self):
        return self.SelectedOrders
    
    
        

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
    
    def printDemand(self,demand):
        print("Demand: Ref.No ",demand.getPN(),", Oprs: ",[(x.getAlternativeMachines()[0].getName(),x.getProcessTime()) for x in demand.getOperations()])

########################################################
    def createInstance(self):

        try: 
            self.DataManager.ReadResources()
        except Exception as e:
            self.getSimulator().saveLog("ERROR: In read resources "+str(e)+".")
   
        for trailer in range(5):
            trlr = Trailer(5000,self.getSimulator(),self); 
            trlr.setAvailable(True)
            trlr.setLocation(self.getCentralInventory())
            self.getResources().append(trlr)

        
        for res in self.getResources():
            if isinstance(res,Inventory):
                self.getSimulator().saveLog("Resource "+res.getType()+', id: '+str(res.getID())+", code"+res.getMachineCode()+"automated"+str(res.IsAutomated())+","+("" if res.getInputBuffer() == None else res.getInputBuffer().getName())+","+("" if res.getOutputBuffer() == None else res.getOutputBuffer().getName())+" created.")
            if isinstance(res,Machine) :
                self.getSimulator().saveLog("Resource "+res.getType()+', id: '+str(res.getID())+", code"+res.getMachineCode()+"automated"+str(res.IsAutomated())+", setup: "+str(res.getSetupTime())+","+("" if res.getInputBuffer() == None else res.getInputBuffer().getName())+","+("" if res.getOutputBuffer() == None else res.getOutputBuffer().getName())+" created.")
                 
            else:
                self.getSimulator().saveLog("Resource "+res.getType()+', id: '+str(res.getID())+" created.")

        try: 
            self.DataManager.ReadDemandFile() # production orders created...
        except Exception as e: 
            self.getSimulator().saveLog("ERROR: In reading demand file "+str(e)+".")

        #now choose soonest production orders to simulate..
        prodorders = []

        for prodordid,prodorder in self.getProductionOrders().items():
            prodorders.append((prodorder.getDeadline(),prodorder))
            

        prodorders.sort(key=lambda x: x[0], reverse=False)

        selectedOrders = []

        for prodorder in prodorders[:min(self.getNoOrders(),len(prodorders))]:

            if prodorder[1].CheckProperness():
                self.getSimulator().saveLog("__________________________________________________________")
                self.getSimulator().saveLog("Selected production order deadline: "+str(prodorder[1].getDeadline()))
                self.createDemandItems(prodorder[1],prodorder[1].getFinalProduct())
                self.getSimulator().saveLog("Selected production order has: "+str(len(prodorder[1].getItems()))+" items created.")
                oprseq = prodorder[1].getFinalProduct().getOperationSequences()[prodorder[1].getID()]
                self.getSimulator().saveLog("Product "+prodorder[1].getFinalProduct().getName()+" has "+str(len(oprseq))+" Operations")
                for op in oprseq:
                    self.getSimulator().saveLog(" Operation "+op.getName()+" Proctime: "+str(op.getRandVar().sampleValue())+" Resources: "+str([alt.getMachineCode() for alt in op.getAlternativeResources()]))
                self.getSimulator().saveLog("Status "+str(prodorder[1].getOperationsStatus()))
                prodorder[1].applyStatus()
                self.getSelectedOrders().append(prodorder[1])

            
        
                
   
        return self.getSelectedOrders()

#_____________________________________________________________________
    def createDemandItems(self,demand,product): # Physical products
        self.getSimulator().saveLog("Item creation starts")
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
############################################################################
    def applyShiftChange(self):

        
        self.getSimulator().saveLog("Apply Shift Change..") 

        for res in self.getResources():
            if isinstance(res,Machine) or isinstance(res,Operator):
                res.setAvailable(self.getSimulator().getCurrentShift() in res.getAvailableShifts())
                if not res.isAvailable():
                    self.getSimulator().saveLog("Resource "+res.getName()+" not available in shift "+str(self.getSimulator().getCurrentShift())) 
                else:
                    self.getSimulator().saveLog("Resource "+res.getName()+" available in shift "+str(self.getSimulator().getCurrentShift()))
                    res.setIdle(True)
            else:
                res.setAvailable(True)
                res.setIdle(True)
                

        preevs = [e for e in self.getSimulator().getEventQueue()["Preemptables"]]


        for event in preevs:
            if (not event.getResource().isAvailable()) or (not event.getEquipment().isAvailable()):
                self.getSimulator().getEventQueue()["Pending"].append(event)
                self.getSimulator().getEventQueue()["Preemptables"].remove(event)
                self.getSimulator().saveLog("Suspending preemptable event "+event.getName()+"("+str(event.getID())+")"+" eqp av? "+str(event.getEquipment().isAvailable())+" res av? "+str(event.getResource().isAvailable()))
                event.setInActive()

                try: 
                    if (not event.getResource().isAvailable()):
                        
                        if event in event.getEquipment().getProgressDict():
                            progress = event.getEquipment().getProgressDict()[event]
                            if sum([(prgrtuple[1]-prgrtuple[0]) for prgrtuple in progress if prgrtuple[1] != 0]) < event.getProcessTime():
                                lastprogress = (progress[-1][0],self.getSimulator().getTime()) 
                                self.getSimulator().saveLog("(Equip progress) Event "+event.getName()+" has last progress "+str(lastprogress))
                                event.getEquipment().getProgressDict()[event] = event.getEquipment().getProgressDict()[event][:-1]
                                event.getEquipment().getProgressDict()[event].append(lastprogress)
                            
                            
                        event.getResource().getMyEvents().remove(event)
                        event.setResource(None)
                except Exception as e:
                    self.getSimulator().saveLog("ERROR in suspending preemptable event  "+event.getName()+": "+str(e)) 

                try: 
                    if (not event.getEquipment().isAvailable()):
                        pocessortodel = None
                        for processor,proevent in event.getEquipment().getProcessMatch().items():
                            if proevent == event:
                                pocessortodel = processor
                                break
    
                        if pocessortodel != None:
                            del event.getEquipment().getProcessMatch()[pocessortodel]
                        self.getSimulator().saveLog("Equpment is set to None")
                        event.setEquipment(None) # note that equipment is always the same, only may become unavailable.  
                except Exception as e:
                    self.getSimulator().saveLog("ERROR in suspending preemptable event 2 "+event.getName()+": "+str(e)) 

                try: 
                    for resource,proglist in event.getProgressDict().items():
                        lastprogress = (proglist[-1][0],self.getSimulator().getTime()) 
                        self.getSimulator().saveLog("(Event-progress) Event "+event.getName()+" has last progress "+str(lastprogress))
                        event.getProgressDict()[resource] = event.getProgressDict()[resource][:-1]
                        event.getProgressDict()[resource].append(lastprogress)
                        break
                except Exception as e:
                    self.getSimulator().saveLog("ERROR in suspended event progress update: "+str(e))           
                    
       
        return
#################################################################################################################################################
    def HandleSimEvent(self,event):

        self.getSimulator().saveLog("Handling event.. "+str(event.getName())+"("+str(event.getID())+")"+",eqp none? "+str(event.getEquipment() == None)+", res none? "+str(event.getResource() == None))
        
        if event.getEquipment() == None or event.getResource() == None:
            for dectuple in event.getEventType().getDecisions():
                self.getSimulator().saveLog("dectuple.. "+str(dectuple[0])+"---- "+str(dectuple[1]))
                if dectuple[0] == 'Handle':
                    dec_type = dectuple[1]
                    for seltuple in self.getProductionAlgManager().getAlgorithmSetting()[event.getName()]:
                        if seltuple[0] == dec_type:
                            if dec_type  == "Assign Equipment" and event.getEquipment()!= None:
                                continue
                            if dec_type  == "Assign Resource" and event.getResource()!= None:
                                continue
                            decision_alg = seltuple[1]; decision_type = dec_type;
                            self.getSimulator().saveLog("-> "+decision_type+" and "+decision_alg+" exists??")
                            if (decision_type,decision_alg) in self.getProductionAlgManager().getPriorityScoringFunctions()[event.getName()]:
                                self.getSimulator().saveLog("-> "+decision_type+" and "+decision_alg+" exists..")
                                algorithm_function = self.getProductionAlgManager().getPriorityScoringFunctions()[event.getName()][(decision_type,decision_alg)]
                                alg_return = algorithm_function(event)

                                if alg_return!= None:
                                    if decision_type == "Select Items":
                                        for item in alg_return:
                                            if len(event.getItems()) == event.getEquipment().getCapacity(): 
                                                break
                                            event.getItems().append(item)
                                            event.setProcessTime(self.getProcessTime(event))
                                    if decision_type == "Assign Equipment":
                                        event.setEquipment(alg_return) # process: inserts this start into progress dict of equip     
                                        self.getSimulator().saveLog("Equipment assigned: "+str(alg_return.getName())+event.print())
                                    if decision_type == "Assign Resource":
                                        event.setResource(alg_return) # preemptable: inserts resource into progress dict, adds event to events of the resource 
                                        self.getSimulator().saveLog("Resource assigned: "+str(alg_return.getName())+event.print())
                                        alg_return.getAssignedEvents().append(event)  
                                else:
                                    #self.getSimulator().saveLog("Handling not successful...")
                                    return False

        if event.getEquipment() == None or event.getResource() == None:
            return False

        #self.getSimulator().saveLog("Proceeding...")

        opr_move,brg_event = self.ProceedToScheduling(event)
        
        self.getSimulator().ScheduleEvent((opr_move if opr_move != None else (brg_event if brg_event!= None else event)),self.getSimulator().getTime(),self)
       
        self.getSimulator().saveLog(event.print()+" handled.")
      
        return True
###########################################################################################################################################
    def startSimEvent(self,event):

        self.getSimulator().saveLog("Start event.. "+str(event.getName()))

        # check necessary conditions..
        if (not event.getResource().isAvailable()) or (not event.getEquipment().isAvailable()):
            return False

        for dectuple in event.getEventType().getDecisions():
            if dectuple[0] == 'Start':
                dec_type = dectuple[1]
                for seltuple in self.getProductionAlgManager().getAlgorithmSetting()[event.getName()]:
                    if seltuple[0] == dec_type:
                        decision_alg = seltuple[1]; decision_type = dec_type;
                        if (decision_type,decision_alg) in self.getProductionAlgManager().getPriorityScoringFunctions()[event.getName()]:
                            
                            algorithm_function = self.getProductionAlgManager().getPriorityScoringFunctions()[event.getName()][(decision_type,decision_alg)]
                            alg_return = algorithm_function(event)

                            #self.getSimulator().saveLog("decision_type "+decision_type)
 
                            if decision_type == "Select Items":
                                for item in alg_return:
                                    if len(event.getItems()) == event.getEquipment().getCapacity(): 
                                        break
                                    event.getItems().append(item) 
                                #self.getSimulator().saveLog(" Select items done: "+event.print())
                            if decision_type == 'Select Destination':
                                from_location = event.getLocation()
                                #self.getSimulator().saveLog(" trailer transport event location"+event.getLocation().getName())
                                #self.getSimulator().saveLog(" destination"+alg_return.getName()) 
                                event.setLocation((from_location,alg_return))
                            
        event.getResource().setIdle(False)
        event.getEquipment().setIdle(False)
        event.setActive() # progress is initiated if preemptable.
        
        event.setStartTime(self.getSimulator().getTime())
  
        # update processor match for processing event.
        if event.getEventType().isProcess():   
            setup_event = event.getPredecessor().getPredecessor()
            for processor,procevent in event.getLocation().getProcessMatch().items():
                if procevent == setup_event:
                    event.getLocation().getProcessMatch()[processor] = event
                    self.getSimulator().saveLog(" processor match updated..")
                    break

        

        #if event.getEventType().isPreemptable():
        #    for resource,proglist in event.getProgressDict().items():
        #        self.getSimulator().saveLog("Progress of res "+resource.getName()+": "+str(proglist))
              
        self.getSimulator().saveLog(" "+event.print()+" started.")   
        
        return True

###############################################################################################################################################
    def isPerformanceRun(self):
        return self.PerformanceRun
    def resumeSimEvent(self,event):

        self.getSimulator().saveLog("Resuming.... Event "+str(event.getName())+"| resource? "+str(event.getResource()== None)+"| equip? "+str(event.getEquipment()== None))

        
        if event.getResource() == None:
            for dectuple in event.getEventType().getDecisions():
                #self.getSimulator().saveLog("dectuple: "+str(dectuple))
                if dectuple[0] == 'Resume':
                    dec_type = dectuple[1]
                    for seltuple in self.getProductionAlgManager().getAlgorithmSetting()[event.getName()]:
                        if seltuple[0] == dec_type:
                            decision_alg = seltuple[1]; decision_type = dec_type;
                            if (decision_type,decision_alg) in self.getProductionAlgManager().getPriorityScoringFunctions()[event.getName()]:
                                #self.getSimulator().saveLog(decision_type+" alg found.. ")
                                algorithm_function = self.getProductionAlgManager().getPriorityScoringFunctions()[event.getName()][(decision_type,decision_alg)]
                                alg_return = algorithm_function(event)
                                
                                if alg_return!= None:
                                    if decision_type == "Assign Resource":
                                        event.setResource(alg_return)
                                        self.getSimulator().saveLog("Resource assigned: "+str(alg_return.getName())+event.print())
                                    alg_return.getAssignedEvents().append(event)  
                                else:
                                    return

        # check necessary conditions..

        if event.getEquipment() == None or event.getResource() == None:
            return False

        #self.getSimulator().saveLog("Proceeding...")
        opr_move,brg_event = self.ProceedToScheduling(event)

        if brg_event!= None:
            self.getSimulator().ScheduleEvent(brg_event,self.getSimulator().getTime(),self)
        else:
            if opr_move!= None:
                self.getSimulator().ScheduleEvent(opr_move,self.getSimulator().getTime(),self)
                return
            else:
                # no previous event necessary
                event.getResource().setIdle(False)
                event.setActive()
     
                if not event.getResource() in event.getProgressDict():
                    event.getProgressDict()[event.getResource()] = []
                event.getProgressDict()[event.getResource()] = [(self.getSimulator().getTime(),0)]

                self.getSimulator().saveLog(" "+event.print()+" resumed.")
       
        return 
################################################################################################################################################
    def commpleteSimEvent(self,event):

        self.getSimulator().saveLog("Finalizing event: "+event.getName()+"start time "+str(event.getStartTime())+" sim time "+str(self.getSimulator().getTime()))

        if event in event.getResource().getMyEvents():
            if len([e for e in event.getResource().getMyEvents() if e == event]) > 1:
                self.getSimulator().saveLog("ERROR: in event completion, event "+event.getName()+" is more than once in events list of res "+event.getResource().getName())
            event.getResource().getMyEvents().remove(event)
   
        else:
            self.getSimulator().saveLog("ERROR: event "+event.print()+" is not in myevents of its resource "+event.getResource().getName())

        self.getSimulator().saveLog("Resource has in myevents? :"+str(event in event.getResource().getMyEvents()))

        if event.getEventType().isPreemptable():
            if event in self.getSimulator().getEventQueue()["Preemptables"]:
                
                if len([e for e in self.getSimulator().getEventQueue()["Preemptables"] if e == event]) > 1:
                    self.getSimulator().saveLog("ERROR: in event completion, preemptable event "+event.getName()+" is more than once in Preemptables list of simulator ")
                self.getSimulator().getEventQueue()["Preemptables"].remove(event)
            else:
                self.getSimulator().saveLog("ERROR: Process event "+event.print()+" is not in Preemptables list of simulator in its completion..")


        if event.getEventType().isProcess():   
            # register last progress step
            self.getSimulator().saveLog("event in progressdict? "+str(event in event.getEquipment().getProgressDict()))
            if event in event.getEquipment().getProgressDict():
                self.getSimulator().saveLog("event in progressdict len "+str(len(event.getEquipment().getProgressDict()[event])))
                newprogress = (event.getEquipment().getProgressDict()[event][-1][0],self.getSimulator().getTime())
                event.getEquipment().getProgressDict()[event][-1] = newprogress
            self.getSimulator().saveLog("remove from processor match. ")
            #remove from processor match.
            for processirid,processorevent in event.getEquipment().getProcessMatch().items():
                if processorevent == event: 
                    self.getSimulator().saveLog("found...")
                    del event.getEquipment().getProcessMatch()[processirid]
                    break

            # add to data process event
            
            event_start = event.getStartTime() 

            if event.getEventType().isPreemptable():
                for ev,progress in  event.getResource().getProgressDict().items():
                    if ev == event:
                        event_start = min([pr[0] for pr in progress])
                        break
                
                
            for item in event.getItems():
                item.setProcessData(event,event_start,item.getActiveOperation(),self.getSimulator())


        # make item moves..
     
        if not event.getEventType().isStatic(): # transport 
            event.getResource().setLocation(event.getLocation()[1]) 
            event.getResource().setLocationData(event,self.getSimulator())
            
            event.getEquipment().setLocation(event.getLocation()[1])
            event.getEquipment().setLocationData(event,self.getSimulator())
            
            for item in event.getItems():
                item.setLocation(event.getLocation()[1]) 
                item.setLocationData(event,self.getSimulator())
        
        else: # no transport
            if (not event.getEventType().isSetup()) and (not event.getEventType().isProcess()):
                self.getSimulator().saveLog("getItemDirection "+str(event.getEventType().getItemDirection()))
                try: 
                    if event.getEventType().getItemDirection(): # True: Place -> Equipment, False: Equipment -> Place
                        for item in event.getItems():
                            event.getPlace().getItems().remove(item)
                            event.getEquipment().getItems().append(item)
                    else:
                        for item in event.getItems():
                            event.getEquipment().getItems().remove(item)
                            event.getPlace().addItem(item)
                            
                    # reset the pending event...
                    if event.getPlace().getPendingEvent() != None:
                        if event.getPlace().getPendingEvent() == event or event.getPlace().getPendingEvent() == event.getPredecessor():
                            event.getPlace().setPendingEvent(None)
                    event.getPlace().generateEvent()
                    
                except Exception as e:
                    self.getSimulator().saveLog("ERROR: In complete event, applying item moves  "+str(e))
                    
          
        # manage next event: if there is a direct successor just use it, otherwise use successor of eventtype

        self.getSimulator().saveLog("Managing next event..")

        nextevent = None
        # if next event is not preemptable and can be done in the current shift, then let the equipment stay busy.  
        if event.getSuccessor()!= None:
            self.getSimulator().saveLog("Direct successor..")

            nextevent = event.getSuccessor()
            if not event.getPrecedenceTypes()[event.getSuccessor()] in ['Simultaneous Start','Simultaneous Finish']:
                
                if not event.getSuccessor().getEventType().isPreemptable():
                    self.getSimulator().ScheduleEvent(event.getSuccessor(),self.getSimulator().getTime(),self)
                else: 
                    # what to do if successor is preemtable: resume it. 
                    self.getSimulator().saveLog("Preemptable successor active? "+str(event.getSuccessor().IsActive()))
                    if not event.getSuccessor() in self.getSimulator().getEventQueue()["Preemptables"]:
                        self.getSimulator().saveLog("Inserting into preemptables")
                        self.getSimulator().getEventQueue()["Preemptables"].append(event.getSuccessor())
                        

            else:
                if event.getSuccessor().getEventType().isPreemptable():
                    self.getSimulator().saveLog("Direct successor.."+event.getSuccessor().getName()+" is active? "+str(event.getSuccessor().IsActive()))
                else:
                    self.getSimulator().ScheduleEvent(event.getSuccessor(),self.getSimulator().getTime(),self)
        
                 
        else:
            if event.getEventType().getSuccessorType()!= None:
                if 'Finish to Start' in event.getEventType().getPrecendenceDict()[event.getEventType().getSuccessorType().getName()]:
                    nextevent = self.defineNextEvent(event,'Finish to Start')
                    self.getSimulator().saveLog(" scheduling next event...@"+str(self.getSimulator().getTime()))
                    self.getSimulator().ScheduleEvent(nextevent,"Pending",self)
              

        if nextevent != None:
            if (nextevent.getEquipment() != event.getEquipment()):
                event.getEquipment().setIdle(True)
            if (nextevent.getResource() != event.getResource()):
                event.getResource().setIdle(True)
        else:
            event.getEquipment().setIdle(True)
            event.getResource().setIdle(True)
            
        self.getSimulator().saveLog(" "+event.print()+" finalized.")
        
      
        return
###########################################################################################################################################
    def getProcessTime(self,event):

        proctime = 1

        if event.getName() == "Machine Setup":
            proctime = event.getEquipment().getSetupTime()
        if (event.getName() == "Machine Loading") or (event.getName() == "Machine Unloading" and not event.getEquipment().IsAutomated()):
            proctime = max(1,int(0.5*event.getEquipment().getOperatingEffort()*event.getItems()[0].getActiveOperation().getRandVar().sampleValue()))
        if event.getName() == "Processing":   
            proctime = event.getItems()[0].getActiveOperation().getRandVar().sampleValue()


        return proctime

##########################################################################################################################################
    def getEventProgress(self,event,precedence):

        progress_time = 0
        if event.getEventType().isPreemptable():

           
            for resource,proglist in event.getProgressDict().items():
                #self.getSimulator().saveLog("Progress of res "+resource.getName()+": "+str(proglist))
                progress_time+=sum([(prg[1]-prg[0]) if prg[1] != 0 else (self.getSimulator().getTime()-prg[0]) for prg in proglist ])
        
            if precedence: 
                if event.getEventType().getSuccessorType()!= None:
                   
                    if event.getEventType().getSuccessorType().getName() in event.getEventType().getPrecendenceDict():
                        #self.saveLog(" successor2 "+event.getEventType().getSuccessorType().getName())
                        if 'Simultaneous Finish' in event.getEventType().getPrecendenceDict()[event.getEventType().getSuccessorType().getName()]:
                            #self.saveLog(" SF successor "+event.getEventType().getSuccessorType().getName())
                            if not event.getEventType().getSuccessorType() in event.getDefinedSuccessors():
                                nextproctime = 1
                                if (event.getEventType().getSuccessorType().getName() == "Machine Unloading" and not event.getEquipment().IsAutomated()):
                                    nextproctime = max(1,int(0.5*event.getEquipment().getOperatingEffort()*event.getItems()[0].getActiveOperation().getRandVar().sampleValue()))

                                #self.getSimulator().saveLog(" For "+event.getName()+" Successor event "+event.getEventType().getSuccessorType().getName()+" nxtproctime "+str(nextproctime)+" time left to start:  proctime "+str(event.getProcessTime())+" - nextproctime " +str(nextproctime)+" - pogress "+str(progress_time)+"= "+str(event.getProcessTime()-nextproctime-progress_time) )
    
                                if event.getProcessTime() - progress_time  <= nextproctime:
                                    nextevent = self.defineNextEvent(event,'Simultaneous Finish')
                                    if nextevent.getEquipment() != None and nextevent.getResource() != None:
                                        self.getSimulator().ScheduleEvent(nextevent,self.getSimulator().getTime(),self)
                                    else:
                                        self.getSimulator().ScheduleEvent(nextevent,"Pending",self)
            
            return progress_time
        else:
            self.getSimulator().saveLog("WARNING: Progress of non-processing/preemptable event "+event.getName()+" is asked!")   
                    


        return event.getProcessTime()

###########################################################################################################################################
    def ProceedToScheduling(self,event):

        #self.getSimulator().saveLog("Proceeding...")
        timedelay = 0
        opr_move = None; brg_event = None
        self.getSimulator().saveLog("->"+event.getEquipment().getLocation().getName()+"---"+event.getLocation().getName())
        if (event.getEquipment().getLocation() != event.getLocation()): #  eqwuipment must be brought. 
            
            self.getSimulator().saveLog("->Eqp loc "+event.getEquipment().getLocation().getName()+", res loc: "+event.getResource().getLocation().getName())
            if event.getResource().getLocation() != event.getEquipment().getLocation():
                self.getSimulator().saveLog("->Opr Move before Brg Eqp")
                opr_move_event_type = self.getEventTypes()["Operator Move"] 
                loc_tuple = (event.getResource().getLocation(),event.getEquipment().getLocation())
                opr_move = Event(loc_tuple,self.getSimulator().getTime(),1,self.getSimulator(),opr_move_event_type)
                opr_move.setResource(event.getResource()); opr_move.setEquipment(event.getResource());  
                timedelay+=1
          
            # (OM ->) BE 
            self.getSimulator().saveLog("-> Eqp")
            loc_tuple = (event.getEquipment().getLocation(),event.getLocation())   
            bring_event_type = self.getEventTypes()["Bring Equipment"]  
            brg_event = Event(loc_tuple,self.getSimulator().getTime()+timedelay,1,self.getSimulator(),bring_event_type)
            brg_event.setEquipment(event.getEquipment()); brg_event.setResource(event.getResource())
            if opr_move != None:
                opr_move.setSuccessor(brg_event)
                opr_move.getPrecedenceTypes()[brg_event] = 'Finish to Start'
                
            brg_event.setSuccessor(event)
            brg_event.getPrecedenceTypes()[event] = 'Finish to Start'

        else: # Equipment is in place, but operator must come 
            self.getSimulator().saveLog("->"+event.getResource().getLocation().getName()+"---"+event.getLocation().getName())
            if event.getLocation() != event.getResource().getLocation():
                opr_move_event_type = self.getEventTypes()["Operator Move"]    
                loc_tuple = (event.getResource().getLocation(),event.getLocation())
                self.getSimulator().saveLog("Oonly opr move: "+event.getResource().getLocation().getName()+"-> "+event.getLocation().getName())
                opr_move = Event(loc_tuple,self.getSimulator().getTime(),1,self.getSimulator(),opr_move_event_type)
                opr_move.setResource(event.getResource()); opr_move.setEquipment(event.getResource());  
                opr_move.setSuccessor(event)
                opr_move.getPrecedenceTypes()[event] = 'Finish to Start'

        self.getSimulator().saveLog("->Opr Move none? "+str(opr_move == None)+"--Brg Eqp  none? "+str(brg_event == None))

        return opr_move,brg_event
###########################################################################################################################################
    def defineNextEvent(self,event,prectype):

        nexteventtype = event.getEventType().getSuccessorType() 
        nextevent = event.getSuccessor() if event.getSuccessor()!= None else Event(None,"Pending",1,self.getSimulator(),nexteventtype) 

        #self.getSimulator().saveLog("next event .."+nextevent.getName())
        event.setSuccessor(nextevent)
        event.getPrecedenceTypes()[nextevent] = prectype

        
      
        if 'Equipment' in event.getEventType().getPrecendenceDict()[nextevent.getEventType().getName()]:
            #self.getSimulator().saveLog("Equipment goes to next event..")
            nextevent.setEquipment(event.getEquipment())
            
        if 'Resource' in event.getEventType().getPrecendenceDict()[nextevent.getEventType().getName()]:
            #self.getSimulator().saveLog("Resource goes to next event..")
            nextevent.setResource(event.getResource()); 
            
        else:
            if nextevent.getEventType().isProcess():
                nextevent.setResource(nextevent.getEquipment())
                    
        if 'Location' in event.getEventType().getPrecendenceDict()[nextevent.getEventType().getName()]:
            if isinstance(event.getLocation(),tuple):
                nextevent.setLocation(event.getLocation()[1])
            else:
                nextevent.setLocation(event.getLocation()) 
            #self.getSimulator().saveLog("location of next event..")
            # transport event destination is selected at start.
                
        if 'Items' in event.getEventType().getPrecendenceDict()[nextevent.getEventType().getName()]:
            #self.getSimulator().saveLog("Items go to next event..")
            for item in event.getItems():
                nextevent.getItems().append(item)
    
        nextevent.setProcessTime(self.getProcessTime(nextevent))
        #self.getSimulator().saveLog("process time found.., static? "+str(nextevent.getEventType().isStatic())+" loc none?"+str(nextevent.getLocation() == None))
         # set nextevent location and place
        if nextevent.getEventType().isStatic():
            if nextevent.getLocation() == nextevent.getEquipment():
                if nextevent.getEventType().getItemDirection():
                    nextevent.setPlace(nextevent.getLocation().getInputBuffer())
                else:
                    nextevent.setPlace(nextevent.getLocation().getOutputBuffer())
            else:
                if nextevent.getEventType().getItemDirection():
                    nextevent.setPlace(nextevent.getLocation().getOutputBuffer())
                else:
                    nextevent.setPlace(nextevent.getLocation().getInputBuffer())
                
        self.getSimulator().saveLog("Next event: "+nextevent.print()+" defined.")

        event.getDefinedSuccessors()[event.getEventType().getSuccessorType()] = nextevent

        return nextevent
#######################################################################################################################################################              
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

      ###################################################################################################################################
    def getCompletionTime(self,event,starttime):

        if event.getEquipment().getType()!= "Machine":
            return starttime+event.getProcessTime()
        
        currtime = starttime
        proctime = event.getProcessTime() 
        procss_shft_strt = currtime

        self.getSimulator().saveLog("Calculating completion of event"+event.print()+" at start "+str(starttime))

     
        while proctime > 0:

            # first get end of this shift
            curr_shiftstart = (currtime//self.getSimulator().getShiftMinutes())*self.getSimulator().getShiftMinutes()
            curr_shiftsend = curr_shiftstart+self.getSimulator().getShiftMinutes()*int((self.getSimulator().getTime()%self.getSimulator().getShiftMinutes())>0)
            
            shiftno = self.getSimulator().getShift((self.getSimulator().getStartDay()+timedelta(minutes = curr_shiftstart)).hour)

            self.getSimulator().saveLog("START: curr_shiftstart"+str(curr_shiftstart)+" curr_shiftsend "+str(curr_shiftsend)+"shiftno"+str(shiftno)+"currtime"+str(currtime)+"proctime"+str(proctime))
 

            if not shiftno in event.getEquipment().getAvailableShifts():
                currtime = curr_shiftsend
                procss_shft_strt = curr_shiftsend
                shiftjump = True
            else:
                if proctime < curr_shiftsend - procss_shft_strt:
                    currtime = min(procss_shft_strt+proctime,curr_shiftsend)
                    proctime = 0
                    
                else:
                    currtime = curr_shiftsend
                    proctime -= (curr_shiftsend - procss_shft_strt)
                    procss_shft_strt = curr_shiftsend
                    
                    
            self.getSimulator().saveLog("END: currtime"+str(currtime)+" procss_shft_strt "+str(procss_shft_strt)+"proctime"+str(proctime))

            
        return currtime
########################################################################################################################
        
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

        process_df = pd.DataFrame(columns=["ItemID","Demand","Product","OperationName","ProcessID","ResourceID","Resource","Start","Completion"])


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
        self.getDataManager().setResultDFs(self.getProcessDF())

        return 

        
