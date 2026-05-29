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
        self.inputdate = None

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
        machineSetup.getDecisions().append(('Handle','Select Items'))
        machineSetup.getDecisions().append(('Handle','Assign Resource'))
     
        
        self.getEventTypes()["Machine Setup"]= machineSetup

        machineLoading = EventType("Machine Loading","Operator","Machine",True,True,False,False)
        machineLoading.getDecisions().append(('Handle','Assign Resource'))
        machineLoading.getDecisions().append(('Resume','Assign Resource'))
        machineLoading.setPreemptable(True)  
        self.getEventTypes()["Machine Loading"]= machineLoading
        machineLoading.setItemDirection(True) # True: Place -> Equipment, False: Equipment -> Place
        
        machineProcessing = EventType("Processing","Machine","Machine",True,False,True,False)
        machineProcessing.getDecisions().append(('Handle','Assign Equipment'))
        machineProcessing.getDecisions().append(('Resume','Assign Equipment'))
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
            self.createDemandItems(prodorder[1],prodorder[1].getFinalProduct())
            self.getSimulator().saveLog("REPORT:  Selected "+prodorder[1].printOrder()+" items created.")
            self.getSelectedOrders().append(prodorder[1])

        
        self.getSimulator().saveLog(">> Creating instance finished.. ")      
   
        return self.getSelectedOrders()

#_____________________________________________________________________
    def createDemandItems(self,demand,product): # Physical products
        self.getSimulator().saveLog("Item creation starts")
        if len(product.getPredecessors()) == 0:
            for itm in range(demand.getQuantity()):
                
                myitem = Item(demand,self.giveItemID())
                #self.getSimulator().saveLog("ERROR check: "+str(myitem.getID()))
              
                self.getCentralInventory().getOutputBuffer().addItem(myitem) # generate trailer loading event.
                demand.getItems().append(myitem)
        else:
            for preddemnd in demand.getDemandType().getPredecessors():
                self.createDemandItems(demand,preddemnd)
               

        return
#______________________________________________________________________
############################################################################
    def applyShiftChange(self,weekendjump):

        self.getSimulator().saveLog(" Apply Shift Change starts..") 

        preevs = [ev for ev in self.getSimulator().getEventQueue()["Preemptables"]]

         ##############################################################################################################
        for event in preevs:
            self.getSimulator().saveLog("  Suspending preemptable event "+event.getName()+"["+str(event.getID())+"]")
            event.setInActive()
     
            try: 
                lastgrstrt = 0 ; lastres = None
                totalprogress = 0
                for resource,proglist in event.getProgressDict().items():
                    totalprogress+= sum([(p[1]-p[0]) for p in proglist if p[1] != 0])
                    if lastgrstrt < proglist[-1][0]:
                        lastgrstrt = proglist[-1][0]
                        lastres = resource
                    self.getSimulator().saveLog(" Res "+resource.getName()+"Progresses of "+event.getName()+"["+str(event.getID())+"]"+": "+str([(p[0],p[1]) for p in proglist])+" total progrss: "+str(totalprogress)+", proctime: "+str(event.getProcessTime()))
                    if sum([1 for p in proglist if p[1] == 0]) > 1:
                        self.getSimulator().saveLog("ERROR: Res "+resource.getName()+" has more than one progress of "+event.getName()+"["+str(event.getID())+"]"+" ending with zero")
              
                if totalprogress < event.getProcessTime():

                    if event.getProgressDict()[lastres][-1][1] > 0:
                        continue # this event suspended before and no need to suspend it again.
                    
                    event.getProgressDict()[lastres] = event.getProgressDict()[lastres][:-1]
                    # close the last open progress.
                    event.getProgressDict()[lastres].append( (lastgrstrt,self.getSimulator().getTime()-weekendjump))

                if event in event.getEquipment().getProcessMatch():
                    del event.getEquipment().getProcessMatch()[event]
                    self.getSimulator().saveLog("  processor match of "+event.getName()+"["+str(event.getID())+"]"+" is removed.")
                else:
                    self.getSimulator().saveLog("WARNING: event "+event.getName()+"["+str(event.getID())+"]"+" is not in process match of equip "+event.getEquipment().getName()) 

                if event.getEventType().isProcess():
                    event.setEquipment(None) # process events only suspend if the machine gets unavailable, resource is defaulty the equipment.  
                    

                
                if event in event.getResource().getMyEvents():
                    event.getResource().getMyEvents().remove(event)
                else:
                    self.getSimulator().saveLog("WARNING: event "+event.getName()+"["+str(event.getID())+"]"+" is not in myevents of its resource "+event.getResource().getName()) 
                
                event.setResource(None) # cases of machine loading anf unloading: equipment is machine, but operators should be reassigned.
               
                
            except Exception as e:
                self.getSimulator().saveLog("ERROR: in suspending preemptable event progress update "+event.getName()+": "+str(e)) 

         
          

        ##############################################################################################################
        avalable_res = [] 
        for res in self.getResources():
            if isinstance(res,Machine) or isinstance(res,Operator):
                res.setAvailable(self.getSimulator().getCurrentShift() in res.getAvailableShifts())
                res.setIdle(True)
                if res.isAvailable():
                    avalable_res.append(res.getName())
            else:
                res.setAvailable(True)
                res.setIdle(True)

            
        self.getSimulator().saveLog(" available res: "+str(avalable_res)) 


        for event in self.getSimulator().getEventQueue()["Preemptables"]:
            # make process events get assigned to their equipments if they become available. 
            if event.getEventType().isProcess():
                # now find its last equipment to immediately start..
                lastgrstrt = 0 ; lastres = None
                for resource,proglist in event.getProgressDict().items():
                    totalprogress+= sum([(p[1]-p[0]) for p in proglist if p[1] != 0])
                    if lastgrstrt < proglist[-1][0]:
                        lastgrstrt = proglist[-1][0]
                        lastres = resource

                if lastres!=None:
                    self.getSimulator().saveLog(" process event: "+str(event.print())+", lastres: "+str(lastres.getName())+("" if lastres == None else " av? "+str(lastres.isAvailable()))) 
                if lastres!= None:
                    if lastres.isAvailable(): 
                        processr = lastres.getProcessor()
                        self.getSimulator().saveLog(" processor found ? "+str(processr != None)) 
                        if processr!= None:
                            event.getProgressDict()[lastres].append((self.getSimulator().getTime(),0)) # make an open progress
                            lastres.getProcessMatch()[event] = processr
                            event.setEquipment(lastres)  # make assignments..
                            event.setResource(lastres) # make assignments..
                            if not event in lastres.getMyEvents():
                                lastres.getMyEvents().append(event)
                         
                            event.setActive()

        self.getSimulator().saveLog(" Apply Shift Change completed..") 
        return
#################################################################################################################################################
    def HandleSimEvent(self,event):

        keyword = ""

     
        self.getSimulator().saveLog(keyword+" Handling event.. "+str(event.getName())+"("+str(event.getID())+")"+",eqp none? "+str(event.getEquipment() == None)+", res none? "+str(event.getResource() == None))

        
        if event.getEquipment() == None or event.getResource() == None:
            for dectuple in event.getEventType().getDecisions():
                
                self.getSimulator().saveLog("dectuple.. "+str(dectuple[0])+"---- "+str(dectuple[1]))
                if dectuple[0] == 'Handle':
                    dec_type = dectuple[1]
                  
                    for seltuple in self.getProductionAlgManager().getAlgorithmSetting()[event.getName()]:
                        if seltuple[0] == dec_type:
                            if dec_type  == "Select Items" and len(event.getItems())>0:
                                continue
                            if dec_type  == "Assign Equipment" and event.getEquipment()!= None:
                                continue
                            if dec_type  == "Assign Resource" and event.getResource()!= None:
                                continue
                            decision_alg = seltuple[1]; decision_type = dec_type;
                            if event.getName() == 'Machine Setup':
                                self.getSimulator().saveLog(keyword+" -> "+decision_type+" and "+decision_alg+" exists??")
                            if (decision_type,decision_alg) in self.getProductionAlgManager().getPriorityScoringFunctions()[event.getName()]:
                                #self.getSimulator().saveLog("REPORT: -> "+decision_type+" and "+decision_alg+" exists..")
                                algorithm_function = self.getProductionAlgManager().getPriorityScoringFunctions()[event.getName()][(decision_type,decision_alg)]
                                alg_return = algorithm_function(event)

                                
                                self.getSimulator().saveLog(" -> alg_return none? "+str(alg_return == None)+" type "+str(type(alg_return)) )

                                #if event.getName() == 'Machine Loading':
                                #    self.getSimulator().saveLog("ERROR "+decision_type+" return none? "+str(alg_return == None))

                                if alg_return!= None:
                                    if decision_type == "Select Items":
                                        for item in alg_return:
                                            if len(event.getItems()) == event.getEquipment().getCapacity(): 
                                                break
                                            event.getItems().append(item)

                                       
                                        self.getSimulator().saveLog(" -> items "+str(len(event.getItems())) )
                                        event.setProcessTime(self.getProcessTime(event))
                                           
                                    if decision_type == "Assign Equipment":
                                        event.setEquipment(alg_return) # process: inserts this start into progress dict of equip     
                                        self.getSimulator().saveLog(keyword+" Equipment assigned: "+str(alg_return.getName())+event.print())
                                    if decision_type == "Assign Resource":
                                        event.setResource(alg_return) # preemptable: inserts resource into progress dict, adds event to events of the resource 
                                        self.getSimulator().saveLog("Resource assigned: "+str(alg_return.getName())+event.print())
                                        alg_return.getAssignedEvents().append(event)  
                                        if not event in event.getResource().getMyEvents():
                                            event.getResource().getMyEvents().append(event)
                                else:
                                    
                                    self.getSimulator().saveLog(" Handling not successful in "+decision_type)
                                    return False

        if event.getEquipment() == None or event.getResource() == None:
            event.increaseStartDelay()
            return False

        opr_move,brg_event = self.ProceedToScheduling(event) 
        #if event.getID() == 158:
        #    self.getSimulator().saveLog("REPORT: OPR_MOVE "+str(opr_move==None)+", brgev "+str(brg_event==None))
            
        
        self.getSimulator().ScheduleEvent((opr_move if opr_move != None else (brg_event if brg_event!= None else event)))
            
        if event.getID() == 158:
            self.getSimulator().saveLog(" "+event.print()+" handled.")
      
        return True
###########################################################################################################################################
    def startSimEvent(self,event):

        keyword = ""

        evloc = "No Location!!"
        #if event.getLocation()!= None:
        #    evloc = event.getLocation().getName() if not isinstance(event.getLocation(),tuple) else event.getLocation()[0].getName()+"->"+event.getLocation()[1].getName() 
       
   
        self.getSimulator().saveLog(" Start event.. "+str(event.getName())+"["+str(event.getID())+"], @ "+evloc+", q: "+str(len(event.getItems()))+", pt: "+str(event.getProcessTime())+"  res: "+event.getResource().getName()+", eq: "+event.getEquipment().getName())

        try: 

            if len(event.getLogisticEvents()) > 0:
                return True
       
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
    
                    
                                if decision_type == "Select Items":
                                    for item in alg_return:
                                        if len(event.getItems()) == event.getEquipment().getCapacity(): 
                                            break
                                        event.getItems().append(item) 
                                if decision_type == 'Select Destination':
                                    from_location = event.getLocation()
                                    event.setLocation((from_location,alg_return))
    
            if event.getEventType().isProcess():
                event.getItems()[0].getActiveOperation().setStart(self.getSimulator().getTime())
                
            event.getResource().setIdle(False)
            event.getEquipment().setIdle(False)
            event.setActive()
    
            ##############################################################################################################
            # event progress updates..
            if event.getEventType().isPreemptable():
                
                if event.getEventType().isProcess():
                    lastgrstrt = 0 ; lastres = None; totalprogress = 0; openprogresses = 0
                    for resource,proglist in event.getProgressDict().items():
                        totalprogress+= sum([(p[1]-p[0]) for p in proglist if p[1] != 0])
                        openprogresses+=sum([1 for p in proglist if p[1] == 0])
                        if lastgrstrt < proglist[-1][0]:
                            lastgrstrt = proglist[-1][0]; lastres = resource
             
                    if totalprogress == event.getProcessTime():
                        self.getSimulator().saveLog("ERROR: Premeptable Event "+event.getName()+"["+str(event.getID())+"]"+" has completed its proceess time, still starting..")
                    if openprogresses > 0:
                        self.getSimulator().saveLog("ERROR: Premeptable Event "+event.getName()+"["+str(event.getID())+"]"+" starting but still has open progress..")
        
                    if not event.getEquipment() in event.getProgressDict():
                        event.getProgressDict()[event.getEquipment()] = [] 
                    event.getProgressDict()[event.getEquipment()].append((self.getSimulator().getTime(),0))
                    
                else: # only types of machine laoding and machine unloading..
                    if not event.getResource() in event.getProgressDict():
                        event.getProgressDict()[event.getResource()] = []
                    event.getProgressDict()[event.getResource()].append((self.getSimulator().getTime(),0))
                    
                    
            else:
                event.setStartTime(self.getSimulator().getTime())
            #################################################################################################################
    
            # event precedence triggers..
            if event.getEventType().getSuccessorType()!= None:
                if 'Simultaneous Start' in event.getEventType().getPrecendenceDict()[event.getEventType().getSuccessorType().getName()]:
                    if not event.getEventType().getSuccessorType() in event.getDefinedSuccessors():
                        nextevent = self.defineNextEvent(event,'Simultaneous Start')
                        self.getSimulator().saveLog(" successor with precedence SS: "+nextevent.getName())
                        self.getSimulator().ScheduleEvent(nextevent)     
                  
                if 'Simultaneous Finish' in event.getEventType().getPrecendenceDict()[event.getEventType().getSuccessorType().getName()]:
                    if not event.getEventType().getSuccessorType() in event.getDefinedSuccessors():
                        nextevent = self.defineNextEvent(event,'Simultaneous Finish')
                        # this event will be checked each time for start.     
             #################################################################################################################
        except Exception as e: 
            self.getSimulator().saveLog("ERROR: In starting event "+str(e))
              
        self.getSimulator().saveLog("  "+event.print()+" started.")   
        
        return True

###############################################################################################################################################
    def isPerformanceRun(self):
        return self.PerformanceRun

#############################################################################################################################################
    def resumeSimEvent(self,event):

        keyword = ""
        evloc = "No Location!!"
        if event.getLocation()!= None:
            evloc = event.getLocation().getName() if not isinstance(event.getLocation(),tuple) else event.getLocation()[0].getName()+"->"+event.getLocation()[1].getName() 
       
            
         
        self.getSimulator().saveLog(" Resuming event.. "+str(event.getName())+"["+str(event.getID())+"], @ "+evloc+", q: "+str(len(event.getItems()))+", pt: "+str(event.getProcessTime())+"  res: "+(" None " if event.getResource() == None else event.getResource().getName())+", eq: "+("None " if event.getEquipment() == None else event.getEquipment().getName()))
        
        
        
        for dectuple in event.getEventType().getDecisions():
                #self.getSimulator().saveLog("dectuple: "+str(dectuple))
            if dectuple[0] == 'Resume':
                    
                self.getSimulator().saveLog(keyword+": "+str(dectuple))
                dec_type = dectuple[1]
                for seltuple in self.getProductionAlgManager().getAlgorithmSetting()[event.getName()]:
                    if seltuple[0] == dec_type:
                        if dec_type  == "Select Items" and len(event.getItems())>0:
                            continue
                        if dec_type  == "Assign Equipment" and event.getEquipment()!= None:
                            continue
                        if dec_type  == "Assign Resource" and event.getResource()!= None:
                            continue
                        decision_alg = seltuple[1]; decision_type = dec_type;
                        if (decision_type,decision_alg) in self.getProductionAlgManager().getPriorityScoringFunctions()[event.getName()]:
                            
                            algorithm_function = self.getProductionAlgManager().getPriorityScoringFunctions()[event.getName()][(decision_type,decision_alg)]
                            alg_return = algorithm_function(event)
   
                            self.getSimulator().saveLog(keyword+": alg RETURN NONE? "+str(alg_return == None))
                                
                            if alg_return!= None:
                                if decision_type == "Assign Resource":
                                    event.setResource(alg_return)
                                    self.getSimulator().saveLog("Resource assigned: "+str(alg_return.getName())+event.print())
                                    alg_return.getAssignedEvents().append(event)  
                                    if not event in event.getResource().getMyEvents():
                                        event.getResource().getMyEvents().append(event)
                                if decision_type == "Assign Equipment":
                                    event.setEquipment(alg_return) # process: inserts this start into progress dict of equip     
                                    self.getSimulator().saveLog("Equipment assigned: "+str(alg_return.getName())+event.print())
                            else:
                                return

        # check necessary conditions..

        if event.getEquipment() == None or event.getResource() == None:
            return False

        #self.getSimulator().saveLog("Proceeding...")
        opr_move,brg_event = self.ProceedToScheduling(event)

        if brg_event!= None:
            self.getSimulator().ScheduleEvent(brg_event)
        else:
            if opr_move!= None:
                self.getSimulator().ScheduleEvent(opr_move)
                return
            else:
                # no previous event necessary
                event.getResource().setIdle(False)
                event.setActive()
     
                if not event.getResource() in event.getProgressDict():
                    event.getProgressDict()[event.getResource()] = []
                event.getProgressDict()[event.getResource()] = [(self.getSimulator().getTime(),0)]

        self.getSimulator().saveLog("REPORT: "+event.print()+" resumed.")
       
        return 
################################################################################################################################################
    def commpleteSimEvent(self,event):


        #evloc = "No Location!!"
        #if event.getLocation()!= None:
            #evloc = event.getLocation().getName() if not isinstance(event.getLocation(),tuple) else event.getLocation()[0].getName()+"->"+event.getLocation()[1].getName() 

    
        #self.getSimulator().saveLog(" Complete event.. "+str(event.getName())+"["+str(event.getID())+"], @ "+evloc+", q: "+str(len(event.getItems())))

        try: 

            self.getSimulator().saveLog("Finalizing event: "+event.getName()+"start time "+str(event.getStartTime())+" sim time "+str(self.getSimulator().getTime()))
    
            if event in event.getResource().getMyEvents():
                if len([ev for ev in event.getResource().getMyEvents() if ev == event]) > 1:
                    self.getSimulator().saveLog("ERROR: in event completion, event "+event.getName()+" is more than once in events list of res "+event.getResource().getName())
                event.getResource().getMyEvents().remove(event)
       
            else:
                self.getSimulator().saveLog("ERROR: event "+event.print()+" is not in myevents of its resource "+event.getResource().getName())
    
            self.getSimulator().saveLog("Resource has in myevents? :"+str(event in event.getResource().getMyEvents()))

            try: 
                if event.getEventType().isPreemptable():
                    if event in self.getSimulator().getEventQueue()["Preemptables"]:
                        
                        if len([ev for ev in self.getSimulator().getEventQueue()["Preemptables"] if ev == event]) > 1:
                            self.getSimulator().saveLog("ERROR: in event completion, preemptable event "+event.getName()+" is more than once in Preemptables list of simulator ")
                        self.getSimulator().getEventQueue()["Preemptables"].remove(event)
                    else:
                        self.getSimulator().saveLog("ERROR: Process event "+event.print()+" is not in Preemptables list of simulator in its completion..")
        
            except Exception as e:
                self.getSimulator().saveLog(" ERROR: in handling preemptable "+str(e))

            try: 
                if event.getEventType().isProcess():
                    if not event.getEquipment() in event.getProgressDict():
                        self.getSimulator().saveLog("ERROR: Preemptable event "+event.getName()+"["+str(event.getID())+"]"+" does not have eqp "+event.getEquipment().getName()+" in progressdict!")
                    for res,proglist in event.getProgressDict().items():
                        if res == event.getEquipment():
                            if proglist[-1][1] != 0:
                                self.getSimulator().saveLog("ERROR: Preemptable event "+event.getName()+"["+str(event.getID())+"]"+" has progress not ending with zero with eqp: "+event.getEquipment().getName())
                            else:
                                lastprogress =  (proglist[-1][0],self.getSimulator().getTime())
                                proglist = proglist[:-1]
                                proglist.append(proglist)
            except Exception as e:
                self.getSimulator().saveLog(" ERROR: in process "+str(e))

            
                #for item in event.getItems():
                #    item.setProcessData(event,event_start,item.getActiveOperation(),self.getSimulator())

            # make item moves..commpleteSimEvent

            try: 
                try: 
                    if not event.getEventType().isStatic(): # transport 
                        event.getResource().setLocation(event.getLocation()[1]) 
                        #event.getResource().setLocationData(event,self.getSimulator())
                        
                        event.getEquipment().setLocation(event.getLocation()[1])
                        #event.getEquipment().setLocationData(event,self.getSimulator())
                        
                        for item in event.getItems():
                            item.setLocation(event.getLocation()[1]) 
                            #item.setLocationData(event,self.getSimulator())
                except Exception as e:
                    self.getSimulator().saveLog(" ERROR: in location updates transport "+str(e))
                    
                else: # no transport
                    try: 
                        if (not event.getEventType().isSetup()) and (not event.getEventType().isProcess()):
                            self.getSimulator().saveLog("getItemDirection "+str(event.getEventType().getItemDirection()))

                            if event.getPlace() != None: 
                                if event.getEventType().getItemDirection(): # True: Place -> Equipment, False: Equipment -> Place
                                    for item in event.getItems():
                                        event.getPlace().getItems().remove(item)
                                        event.getEquipment().getItems().append(item)
                                else:
                                    for item in event.getItems():
                                        event.getEquipment().getItems().remove(item)  
                                        event.getPlace().addItem(item)
                                            
                                    # reset the pending event...
                                if event.getEventType().getName() in ["Machine Loading","Trailer Loading"]:
                                    if event.getPlace().getPendingEvent() != None:
                                        event.getPlace().setPendingEvent(None)
                                        event.getPlace().generateEvent()
                    except Exception as e:
                        self.getSimulator().saveLog(" ERROR: in location updates static"+str(e))
            except Exception as e:
                self.getSimulator().saveLog(" ERROR: in location updates "+str(e))
                        
            if event.getEventType().isProcess(): 
                self.getSimulator().saveLog(" event: "+event.getName()+"["+str(event.getID())+"], opr getting compltd "+(event.getItems()[0].getActiveOperation().getName() if event.getItems()[0].getActiveOperation()!= None else "Opr None.."))
                event.getItems()[0].getActiveOperation().setSimPlanned()
                event.getItems()[0].getActiveOperation().setExecutionData(event,self.getSimulator())
    
              
            # manage next event: if there is a direct successor just use it, otherwise use successor of eventtype

        ################################################################################################################
        ####### M A N A G I N G   N E X T   E V E N T 
            self.getSimulator().saveLog("Managing next event.. successor ? "+str(event.getSuccessor()!= None))
    
            nextevent = None
            # if next event is not preemptable and can be done in the current shift, then let the equipment stay busy.  
            if event.getSuccessor()!= None:
                
                nextevent = event.getSuccessor()

                if nextevent.getSuccessor()!= None:
                    if event in nextevent.getSuccessor().getLogisticEvents():
                        nextevent.getSuccessor().getLogisticEvents().remove(event)
                        self.getSimulator().saveLog(" Logistic event "+event.getName()+"["+str(event.getID())+"] is removed from loglist of succ-succ"+nextevent.getSuccessor().getName()+"["+str(nextevent.getSuccessor().getID())+"]")
                
                if event in nextevent.getLogisticEvents():
                    nextevent.getLogisticEvents().remove(event)
                    self.getSimulator().saveLog(" Logistic event "+event.getName()+"["+str(event.getID())+"] is removed from loglist of succ"+nextevent.getName()+"["+str(nextevent.getID())+"]")
                    if len(nextevent.getLogisticEvents()) == 0:
                        if len(nextevent.getProgressDict()) > 0:
                                    
                            nextevent.getResource().setIdle(False)
                            nextevent.setActive()
     
                            if not nextevent.getResource() in nextevent.getProgressDict():
                                nextevent.getProgressDict()[nextevent.getResource()] = []
                            nextevent.getProgressDict()[nextevent.getResource()] = [(self.getSimulator().getTime(),0)]
                                    
                        else:
                            self.getSimulator().ScheduleEvent(nextevent)
                else:
                    if nextevent.getEventType().isPreemptable():
                        if len(nextevent.getProgressDict()) > 0: 
                            if not nextevent in self.getSimulator().getEventQueue()["Preemptables"]:
                                self.getSimulator().getEventQueue()["Preemptables"].append(nextevent)
                                self.getSimulator().saveLog(" Direct successor.."+nextevent.getName()+" is added to preemptables")
                            nextevent.setActive()
                            if not nextevent.getResource() in nextevent.getProgressDict():
                                nextevent.getProgressDict()[nextevent.getResource()] = []
                            nextevent.getProgressDict()[nextevent.getResource()] = [(self.getSimulator().getTime(),0)]
                        else:
                            self.getSimulator().ScheduleEvent(nextevent)
                    else:
                        if nextevent in event.getPrecedenceTypes():
                            if not event.getPrecedenceTypes()[nextevent] in ['Simultaneous Start','Simultaneous Finish']:
                                self.getSimulator().ScheduleEvent(nextevent)
                        else:
                            self.getSimulator().ScheduleEvent(nextevent)
                                
                
                self.getSimulator().saveLog(" Direct successor.."+nextevent.getName()+"["+str(nextevent.getID())+"] is active? "+str(nextevent.IsActive())+" is prectypes? "+str(nextevent in event.getPrecedenceTypes()))
               
                
                 

                if isinstance(event.getEquipment(),Machine):
                    if event in event.getEquipment().getProcessMatch():
                        processor = event.getEquipment().getProcessMatch()[event]
                        del event.getEquipment().getProcessMatch()[event]
                        event.getEquipment().getProcessMatch()[nextevent] = processor
                        self.getSimulator().saveLog("Processor match of event "+event.getName()+"["+str(event.getID())+"]"+" updated with successor "+nextevent.getName()+"["+str(nextevent.getID())+"] res none? "+str(event.getResource() == None)+", eqp none? "+str(event.getEquipment() == None))
                        
             
                     
            else: # NO predfined successor event
                if event.getEventType().getSuccessorType()!= None:
                    if 'Finish to Start' in event.getEventType().getPrecendenceDict()[event.getEventType().getSuccessorType().getName()]:
                        nextevent = self.defineNextEvent(event,'Finish to Start')
                        # now replace the processor match
    
                        if isinstance(event.getEquipment(),Machine):
                            if event in event.getEquipment().getProcessMatch():
                                processor = event.getEquipment().getProcessMatch()[event]
                                del event.getEquipment().getProcessMatch()[event]
                                event.getEquipment().getProcessMatch()[nextevent] = processor
                                self.getSimulator().saveLog("Processor match of event "+event.getName()+"["+str(event.getID())+"]"+" updated with successor "+nextevent.getName()+"["+str(nextevent.getID())+"]")
                            
                        
                        self.getSimulator().saveLog(" scheduling next event...@"+str(self.getSimulator().getTime()))
                        self.getSimulator().getEventQueue()["Pending"].append(nextevent)
                else:
                    if isinstance(event.getEquipment(),Machine):
                        if event in event.getEquipment().getProcessMatch():
                            del event.getEquipment().getProcessMatch()[event]
                            self.getSimulator().saveLog("Processor match of event "+event.getName()+"["+str(event.getID())+"]"+" removed ")
             
                  
    
            if nextevent != None:
                if (nextevent.getEquipment() != event.getEquipment()):
                    event.getEquipment().setIdle(True)
                if (nextevent.getResource() != event.getResource()):
                    event.getResource().setIdle(True)
            else:
                event.getEquipment().setIdle(True)
                event.getResource().setIdle(True)
                
            self.getSimulator().saveLog(" "+event.print()+" finalized.")
            event.setInActive() 
            #self.getSimulator().saveLog(" ERROR check:  event completion "+event.getName()+"["+str(event.getID())+"]")
        except Exception as e:
            self.getSimulator().saveLog(" ERROR: in event completion "+str(e)+" event: "+event.getName()+"["+str(event.getID())+"] res none? "+str(event.getResource() == None)+", eqp none? "+str(event.getEquipment() == None))
            #self.getSimulator().saveLog("  ERROR: "+event.print())
      
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

###########################################################################################################################################
    def ProceedToScheduling(self,event):

        #self.getSimulator().saveLog("Proceeding...")
        timedelay = 0
        opr_move = None; brg_event = None
        
        #self.getSimulator().saveLog("->"+event.getEquipment().getLocation().getName()+"---"+event.getLocation().getName())
        if (event.getEquipment().getLocation() != event.getLocation()): #  eqwuipment must be brought. 
            
            #self.getSimulator().saveLog("->Eqp loc "+event.getEquipment().getLocation().getName()+", res loc: "+event.getResource().getLocation().getName())
            if event.getResource().getLocation() != event.getEquipment().getLocation():
                self.getSimulator().saveLog("->Opr Move before Brg Eqp")
                opr_move_event_type = self.getEventTypes()["Operator Move"] 
                loc_tuple = (event.getResource().getLocation(),event.getEquipment().getLocation())
                opr_move = Event(loc_tuple,self.getSimulator().getTime(),1,self.getSimulator(),opr_move_event_type)
                opr_move.setResource(event.getResource()); opr_move.setEquipment(event.getResource());  
                if not opr_move in opr_move.getResource().getMyEvents():
                    opr_move.getResource().getMyEvents().append(opr_move)
                timedelay+=1
                event.getLogisticEvents().append(opr_move)
          
            # (OM ->) BE 
            self.getSimulator().saveLog("-> Eqp")
            loc_tuple = (event.getEquipment().getLocation(),event.getLocation())   
            bring_event_type = self.getEventTypes()["Bring Equipment"]  
            brg_event = Event(loc_tuple,self.getSimulator().getTime()+timedelay,1,self.getSimulator(),bring_event_type)
            brg_event.setEquipment(event.getEquipment()); brg_event.setResource(event.getResource())
            if not brg_event in brg_event.getResource().getMyEvents():
                    brg_event.getResource().getMyEvents().append(brg_event)
            if opr_move != None:
                opr_move.setSuccessor(brg_event)
                opr_move.getPrecedenceTypes()[brg_event] = 'Finish to Start'
                
            brg_event.setSuccessor(event)
            brg_event.getPrecedenceTypes()[event] = 'Finish to Start'
            event.getLogisticEvents().append(brg_event)

        else: # Equipment is in place, but operator must come 
            #self.getSimulator().saveLog("->"+event.getResource().getLocation().getName()+"---"+event.getLocation().getName())
            if event.getLocation() != event.getResource().getLocation():
                opr_move_event_type = self.getEventTypes()["Operator Move"]    
                loc_tuple = (event.getResource().getLocation(),event.getLocation())
                #self.getSimulator().saveLog("Oonly opr move: "+event.getResource().getLocation().getName()+"-> "+event.getLocation().getName())
                opr_move = Event(loc_tuple,self.getSimulator().getTime(),1,self.getSimulator(),opr_move_event_type)
                opr_move.setResource(event.getResource()); opr_move.setEquipment(event.getResource()); 
                if not opr_move in opr_move.getResource().getMyEvents():
                    opr_move.getResource().getMyEvents().append(opr_move)
                opr_move.setSuccessor(event)
                opr_move.getPrecedenceTypes()[event] = 'Finish to Start'
                event.getLogisticEvents().append(opr_move)

        self.getSimulator().saveLog("->Opr Move none? "+str(opr_move == None)+"--Brg Eqp  none? "+str(brg_event == None))

        return opr_move,brg_event
###########################################################################################################################################
    def defineNextEvent(self,event,prectype):

        nexteventtype = event.getEventType().getSuccessorType() 
        nextevent = event.getSuccessor() if event.getSuccessor()!= None else Event(None,"Pending",1,self.getSimulator(),nexteventtype) 

        #self.getSimulator().saveLog("next event .."+nextevent.getName())
        event.setSuccessor(nextevent)
        event.getPrecedenceTypes()[nextevent] = prectype # here we can read what type of precedence relation is there. 

        
      
        if 'Equipment' in event.getEventType().getPrecendenceDict()[nextevent.getEventType().getName()]:
            #self.getSimulator().saveLog("Equipment goes to next event..")
            nextevent.setEquipment(event.getEquipment())
            
        if 'Resource' in event.getEventType().getPrecendenceDict()[nextevent.getEventType().getName()]:
            #self.getSimulator().saveLog("Resource goes to next event..")
            nextevent.setResource(event.getResource())
            if prectype != "Simultaneous Finish":
                if not nextevent in nextevent.getResource().getMyEvents():
                     nextevent.getResource().getMyEvents().append(nextevent)
            
        else:
            if nextevent.getEventType().isProcess():
                nextevent.setResource(nextevent.getEquipment())
                if prectype != "Simultaneous Finish":
                    if not nextevent in nextevent.getResource().getMyEvents():
                        nextevent.getResource().getMyEvents().append(nextevent)
                    
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

        self.getSimulator().saveLog(" Calculating completion of event"+event.print()+" at start "+str(starttime))

     
        while proctime > 0:

            # first get end of this shift
            curr_shiftstart = (currtime//self.getSimulator().getShiftMinutes())*self.getSimulator().getShiftMinutes()
            curr_shiftsend = curr_shiftstart+self.getSimulator().getShiftMinutes()*int((self.getSimulator().getTime()%self.getSimulator().getShiftMinutes())>0)
            
            shiftno = self.getSimulator().getShift((self.getSimulator().getStartDay()+timedelta(minutes = curr_shiftstart)).hour)

            self.getSimulator().saveLog(" START: curr_shiftstart"+str(curr_shiftstart)+" curr_shiftsend "+str(curr_shiftsend)+"shiftno"+str(shiftno)+"currtime"+str(currtime)+"proctime"+str(proctime))
 

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

        process_df = pd.DataFrame(columns=["OperationName","ProcessID","ResourceID","Resource","Start","Completion","DemandID","Product","NrItems"])

        for prodordid,prodorder in self.getProductionOrders().items():
            
            oprsequence = prodorder.getFinalProduct().getOperationSequences()[prodorder.getID()]

            oprid = 0
            for myopr in oprsequence:
                for excdata in myopr.getExecutionData():
                    process_df.loc[len(process_df)] = excdata
                    

        
        process_df.to_csv("ProcessData.csv",index = False)
        

    def writeDataTBRMOutPut(self):

        TBRM_df= pd.DataFrame(columns=["ID","Product","Product/ID","Quantity To Produce","Deadline","Work Orders/Work Center","Work Orders/Work Center/ID","Work Orders/Expected Duration","Work Orders/Start","Work Orders/End","Work Orders/Status","Simulation_Planned"])

        currentdate =  datetime.now()
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

                    #self.getSimulator().saveLog("REPORT: mystrt "+str(mystrt)+", mycomp "+str(mycomp))
                    
                    if  isinstance(mystrt,int) and mystrt!= None :
                        mystrt = startday+timedelta(minutes = mystrt)

                    if isinstance(mycomp,int) and mycomp!= None :
                         mycomp = startday+timedelta(minutes = mycomp)
                        
                    
                    if oprid == 0:
                         
                        myorddata = {"ID":prodorder.getID(),"Product":prodorder.getFinalProduct().getName(),"Product/ID":prodorder.getFinalProduct().getID(),"Quantity To Produce":prodorder.getQuantity(),"Deadline":prodorder.getDeadline(),"Work Orders/Work Center":myopr.getName(),"Work Orders/Work Center/ID":myopr.getAlternativeResources()[0].getID(),"Work Orders/Expected Duration":myopr.getRandVar().sampleValue(),"Work Orders/Start":mystrt,"Work Orders/End":mycomp,"Work Orders/Status":status,"Simulation_Planned":prodorder in self.getSelectedOrders()}
                    else:
                        myorddata = {"Work Orders/Work Center":myopr.getName(),"Work Orders/Work Center/ID":(myopr.getAlternativeResources()[0].getID() if len(myopr.getAlternativeResources()) > 0 else "-"),"Work Orders/Expected Duration":myopr.getRandVar().sampleValue(),"Work Orders/Start":mystrt,"Work Orders/End":mycomp,"Work Orders/Status":status,"Simulation_Planned":prodorder in self.getSelectedOrders()}

                    TBRM_df.loc[len(TBRM_df)] = myorddata
                    oprid+=1
                        
            inputdate = ""
            if self.inputdate !=None:
                inputdate = str(self.inputdate.date())
            
            TBRM_df.to_csv("TBRM_Plan_"+inputdate+".csv",index = False)
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

        
