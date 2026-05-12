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

        #EventType(myname,restype,equiptype,static,loading,process)

        machineSetup = EventType("Machine Setup","Operator","Machine",True,False,False)
        self.getEventTypes()["Machine Setup"]= machineSetup

        machineLoading = EventType("Machine Loading","Operator","Machine",True,True,False)
        self.getEventTypes()["Machine Loading"]= machineLoading
        
        machineProcessing = EventType("Processing","Machine","Machine",True,False,True)
        self.getEventTypes()["Processing"]= machineProcessing
        
        machineUnloading = EventType("Machine Unloading","Operator","Machine",True,False,False) 
        self.getEventTypes()["Machine Unloading"]= machineUnloading

        # Machine Loading -> Processing -> Machine Unloading (manual and automated)

        # Outputbuffer: Items change, it creates pending trailer loading event. 

        machineLoading.setPredecessorType(machineSetup)
        machineSetup.getPrecendenceDict()[machineLoading.getName()] = ['Equipment']

        machineProcessing.setPredecessorType(machineLoading)
        machineLoading.getPrecendenceDict()[machineProcessing.getName()] = ['Equipment','Items']

        machineUnloading.setPredecessorType(machineProcessing)
        machineProcessing.getPrecendenceDict()[machineUnloading.getName()] = ['Equipment','Items']

 

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

        self.DataManager.ReadResources()
   
        for trailer in range(5):
            trlr = Trailer(5000,self.getSimulator(),self); 
            trlr.setLocation(self.getCentralInventory())
            self.getResources().append(trlr)

        for res in self.getResources():
            if isinstance(res,Inventory):
                print("Resource",res.getType(),'id: ',res.getID(),"code",res.getMachineCode(),"automated",res.IsAutomated(),",",("" if res.getInputBuffer() == None else res.getInputBuffer().getName()),",",("" if res.getOutputBuffer() == None else res.getOutputBuffer().getName())," created.")
            if isinstance(res,Machine) :
                print("Resource",res.getType(),'id: ',res.getID(),"code",res.getMachineCode(),"automated",res.IsAutomated()," setup: ",res.getSetupTime(),",",("" if res.getInputBuffer() == None else res.getInputBuffer().getName()),",",("" if res.getOutputBuffer() == None else res.getOutputBuffer().getName())," created.")
                 
            else:
                print("Resource",res.getType(),'id: ',res.getID()," created.")

        
        self.DataManager.ReadDemandFile() # production orders created...

        #now choose soonest production orders to simulate..
        prodorders = []

        for prodordid,prodorder in self.getProductionOrders().items():
            prodorders.append((prodorder.getDeadline(),prodorder))
            

        prodorders.sort(key=lambda x: x[0], reverse=False)

        selectedOrders = []

        for prodorder in prodorders[:min(self.getNoOrders(),len(prodorders))]:

            if prodorder[1].CheckProperness():
                print("__________________________________________________________")
                print("Selected production order deadline: ",prodorder[1].getDeadline())
                self.createDemandItems(prodorder[1],prodorder[1].getFinalProduct())
                print("Selected production order has: ",len(prodorder[1].getItems())," items created.")
                oprseq = prodorder[1].getFinalProduct().getOperationSequences()[prodorder[1].getID()]
                print("Product ",prodorder[1].getFinalProduct().getName()," has ",len(oprseq),"Operations")
                for op in oprseq:
                    print(" Operation ",op.getName()+" Proctime: ",op.getRandVar().sampleValue()," Resources: ",[alt.getMachineCode() for alt in op.getAlternativeResources()])
                print("Status ",prodorder[1].getOperationsStatus())
                prodorder[1].applyStatus()
                selectedOrders.append(prodorder[1])

            
        
                
   
        return selectedOrders
############################################################################
    def applyShiftChange(self):

        self.getSimulator().saveLog("Apply Shift Change..")
        for res in self.getResources():
            if res.getType() == "Machine":
                for ev,progress in res.getProgressDict().items():

                    #completed ones..
                    if sum([(prgrtuple[1]-prgrtuple[0]) for prgrtuple in progress if prgrtuple[1] != 0]) == ev.getProcessTime():
                        continue
                    #stopped ones..
                    if (progress[-1][1] <= self.getSimulator().getTime() - self.getSimulator().getShiftMinutes()) and (progress[-1][1] > 0):
                        self.getSimulator().saveLog("Event "+ev.getName()+" passes.. "+str(progress[-1])+" shift start "+str(self.getSimulator().getTime() - self.getSimulator().getShiftMinutes()))
                        continue
                    
                    lastprogress = (progress[-1][0],self.getSimulator().getTime()) 
                    self.getSimulator().saveLog("Event "+ev.getName()+" has progress "+str(lastprogress))
                    res.getProgressDict()[ev] = res.getProgressDict()[ev][:-1]
                    res.getProgressDict()[ev].append(lastprogress)
                    
            if isinstance(res,Machine) or isinstance(res,Operator):
                res.checkShiftChange(self.getSimulator().getCurrentShift())
                if not res.IsIdle():
                    self.getSimulator().saveLog("Resource"+res.getName()+" not available in shift "+str(self.getSimulator().getCurrentShift()))
                else:
                    if res.getType() == "Machine":
                        for ev,progress in res.getProgressDict().items():
                            # completed ones..
                            if sum([(prgrtuple[1]-prgrtuple[0]) for prgrtuple in progress if prgrtuple[1] != 0]) == ev.getProcessTime():
                                continue
                                
                            self.getSimulator().saveLog("Event "+ev.getName()+" starts.. "+str(progress[-1]))
                            
                            progress.append((self.getSimulator().getTime(),0))
                        self.getSimulator().saveLog("Resource"+res.getName()+" available in shift "+str(self.getSimulator().getCurrentShift()))
                
           
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

        if event.getEquipment() == None: 

            selected_algorithm = self.getProductionAlgManager().getAlgorithmSetting()["Assign Event Equipment"]
            algorithm_function = self.getProductionAlgManager().getPriorityScoringFunctions()["Assign Event Equipment"][selected_algorithm]
            equip = algorithm_function(event)
            
            if equip == None:
                return False

        if event.getResource() == None:
            selected_algorithm = self.getProductionAlgManager().getAlgorithmSetting()["Assign Event Resource"]
            algorithm_function = self.getProductionAlgManager().getPriorityScoringFunctions()["Assign Event Resource"][selected_algorithm]
            res = algorithm_function(event)

            if res == None: 
                return False

        
        timedelay = 0
        opr_move = None
        if (event.getEquipment().getLocation() != event.getLocation()) and (not event.getName() in ["Machine Loading","Machine Unloading"]):
                            
            if event.getResource().getLocation() != event.getEquipment().getLocation():
                opr_move_event_type = self.getEventTypes()["Operator Move"]    
                loc_tuple = (event.getResource().getLocation(),event.getEquipment().getLocation())
                # loc,start,proctime,sim,eventype
                opr_move = Event(loc_tuple,self.getSimulator().getTime(),1,self.getSimulator(),opr_move_event_type)
                opr_move.setResource(event.getResource()); opr_move.setEquipment(event.getResource());  
                event.getResource().getAssignedEvents().append(opr_move)
                self.getSimulator().ScheduleEvent(opr_move,self.getSimulator().getTime(),self,True)
                timedelay+=1
        
            loc_tuple = (event.getEquipment().getLocation(),event.getLocation())   
            bring_event_type = self.getEventTypes()["Bring Equipment"]    
            # loc,start,proctime,sim,eventype
            bring_event = Event(loc_tuple,self.getSimulator().getTime()+timedelay,1,self.getSimulator(),bring_event_type)
            bring_event.setEquipment(event.getEquipment()); bring_event.setResource(event.getResource())
            self.getSimulator().ScheduleEvent(bring_event,self.getSimulator().getTime()+timedelay,self,True)
            if opr_move != None:
                opr_move.setSuccessor(bring_event)
            bring_event.setSuccessor(event)
            timedelay+=1
        
        else: 
            self.getSimulator().saveLog("Event:"+event.getName()+", location: "+event.getLocation().getName()+", resource location: "+event.getResource().getLocation().getName())
            if event.getLocation() != event.getResource().getLocation():
                opr_move_event_type = self.getEventTypes()["Operator Move"]    
                loc_tuple = (event.getResource().getLocation(),event.getLocation())
                opr_move = Event(loc_tuple,self.getSimulator().getTime(),1,self.getSimulator(),opr_move_event_type)
                opr_move.setSuccessor(event)
                timedelay+=1
                
       

        if event.getName() == "Machine Loading": 

          
            self.getSimulator().saveLog(" Machine Loading/getEquipment().getName() "+str(event.getEquipment().getName()))
            if event.getEquipment().getName() != "OUT - Outsourced activity_(OUT - Outsourced)":
                setupevent_type = event.getEventType().getPredecessorType() 
                setup_event = Event(event.getLocation(),self.getSimulator().getTime()+timedelay,event.getEquipment().getSetupTime(),self.getSimulator(),setupevent_type)
                setup_event.setEquipment(event.getEquipment())
                setup_event.setResource(event.getResource())
                setup_event.setPlace(event.getPlace())
                self.getSimulator().saveLog(setup_event.print()+" created.")
                self.getSimulator().ScheduleEvent(setup_event,self.getSimulator().getTime()+timedelay,self,True) # shedule setup  
        
                timedelay+=event.getEquipment().getSetupTime()

            processing_type = event.getEventType().getSuccessorType() 
            processing_event = Event(event.getLocation(),self.getSimulator().getTime()+timedelay,1,self.getSimulator(),processing_type)
            processing_event.setEquipment(event.getEquipment())
            processing_event.setResource(event.getEquipment())
            processing_event.setPlace(event.getPlace())


            if event.getPlace().getPendingEvent() == event:
                event.getPlace().setPendingEvent(None)
                
            for processorid,pevent in event.getEquipment().getProcessMatch().items():
                if pevent == event:
                    event.getEquipment().getProcessMatch()[processorid] = processing_event
                    break
            
                    
                    
            event.setSuccessor(processing_event)
            self.getSimulator().saveLog(processing_event.print()+" created.")
         
          

        if event.getName() == "Machine Loading": 
            self.getSimulator().ScheduleEvent(event,self.getSimulator().getTime()+timedelay,self,False)
        else:
            self.getSimulator().ScheduleEvent(event,self.getSimulator().getTime()+timedelay,self,True)
        self.getSimulator().saveLog(event.print()+" handled.")
      

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
    def startEvent(self,event):

        event.getResource().setBusy()
        event.getEquipment().setBusy()

        event.setActive()

        if event.getName() in self.getProductionAlgManager().getAlgorithmSetting(): 

            decision_name,selected_algorithm = self.getProductionAlgManager().getAlgorithmSetting()[event.getName()]
            self.getSimulator().saveLog(event.print()+" "+decision_name+"--"+selected_algorithm)
            
            # check if selecting items
            
            if decision_name == 'Select Items':    
                item_source = event.getEquipment() if not event.getEventType().isLoading() else event.getPlace()
                source_items = [i for i in item_source.getItems()]
                #print(" > "+str(self.getSimulator().getTime())+": ev",event.getName(),"decision_type ",decision_name,", selected_alg ",selected_algorithm) 
                #print(" > "+str(self.getSimulator().getTime())+": source items ",len(source_items))  
                algorithm_function = self.getProductionAlgManager().getPriorityScoringFunctions()[event.getName()][(decision_name,selected_algorithm)]
                sorted_items = algorithm_function(event,source_items)
                
                #print(" > "+str(self.getSimulator().getTime())+": sorted items ",[i.getID() for i in sorted_items], 'Equip cap ',event.getEquipment().getCapacity())  
                for item in sorted_items:
                    if event.getEventType().isLoading():
                        if len(event.getItems()) == event.getEquipment().getCapacity(): 
                            break
                    else:
                        if len(event.getItems()) == event.getPlace().getCapacity():
                            break
                            
                    event.getItems().append(item)
                if event.getName() == "Machine Loading":

                    event.setProcessTime(max(1,int(0.5*event.getEquipment().getOperatingEffort()*event.getItems()[0].getActiveOperation().getRandVar().sampleValue())))

                    
                    event_completion = event.getEquipment().getWorkMgr().getCompletionTime(event,self.getSimulator().getTime())

                    self.getSimulator().saveLog(event.print()+"  ******** completion scheduled at time "+str(event_completion))

                    if not event_completion in self.getSimulator().getEventQueue():
                        self.getSimulator().getEventQueue()[event_completion] = []
                        
                    self.getSimulator().getEventQueue()[event_completion].append(event)
                    
                    event.getSuccessor().setProcessTime(event.getItems()[0].getActiveOperation().getRandVar().sampleValue())
                        
                    self.getSimulator().ScheduleEvent(event.getSuccessor(),self.getSimulator().getTime()+max(1,int(0.25*event.getProcessTime())),self,True)
                    event.getSuccessor().setStartTime(self.getSimulator().getTime()+max(1,int(0.1*event.getProcessTime())))
                    self.getSimulator().saveLog(" successor "+event.getSuccessor().print()+"  ******** start scheduled at time "+str(self.getSimulator().getTime()+max(1,int(0.25*event.getProcessTime()))))
                    
                    # shedule processing 
                    
                    
            if decision_name == 'Select Destination':
                from_location = event.getLocation()
                self.getSimulator().saveLog(" trailer transport event location"+event.getLocation().getName())
                algorithm_function = self.getProductionAlgManager().getPriorityScoringFunctions()[event.getName()][(decision_name,selected_algorithm)]      
                self.getSimulator().saveLog(" decision_type "+decision_name+", selected_alg "+selected_algorithm)  
                destination = algorithm_function(event,event.getItems())
                self.getSimulator().saveLog(" destination"+destination.getName()) 
                event.setLocation((from_location,destination))
            
            #print(" > "+str(self.getSimulator().getTime())+":  event items ",[str(i.getID())  for i in event.getItems()])

        if event.IsActive():
            self.getSimulator().saveLog(" "+event.print()+" started.")

        
        if event.getName() == "Processing":
            if not event in event.getEquipment().getProgressDict():
                event.getEquipment().getProgressDict()[event] = []
            event.getEquipment().getProgressDict()[event].append((self.getSimulator().getTime(),0))
            
            
        return 

########################################################################################################################
    def commpleteEvent(self,event):

        event.getResource().setIdle()
        event.getEquipment().setIdle()  
        
        if event in event.getEquipment().getMyEvents():
            event.getEquipment().getMyEvents().remove(event)

       
        if event.getEventType().isStatic():
            if not event.getEventType().isProcess():
                self.getSimulator().saveLog(" "+event.getName()+" .........")
                for item in event.getItems():
                    item.setLocationData(event,self.getSimulator())
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
                self.getSimulator().saveLog("Finalizing event: "+event.getName()+"start time "+str(event.getStartTime())+" sim time "+str(self.getSimulator().getTime()))
                for item in event.getItems():
                    item.setProcessData(event,item.getActiveOperation(),self.getSimulator())
                    item.setLocationData(event,self.getSimulator())
                   
                    
        else: # make location updates for dynamic event
            event.getResource().setLocation(event.getLocation()[1]) 

            event.getResource().setLocationData(event,self.getSimulator())
            event.getEquipment().setLocationData(event,self.getSimulator())
            
            if event.getResource()!= event.getEquipment():
                event.getEquipment().setLocation(event.getLocation()[1])

            for item in event.getEquipment().getItems():
                item.setLocationData(event,self.getSimulator())
               
          
        nexteventtype = event.getEventType().getSuccessorType() 
        
        
        if nexteventtype != None and event.getName() != "Machine Setup" and event.getName() != "Bring Equipment": 
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

            if event.getName() != "Machine Loading":
                
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
                if event.getName() == "Machine Loading": 
                    nextevent.setResource(nextevent.getEquipment())
                    nextevent.setStartTime(self.getSimulator().getTime())

                if event.getName() == "Processing":
                    if event.getEquipment().IsAutomated():
                        nextevent.setResource(event.getEquipment())
                    else:
                        #print("Predecessor of processing: ",event.getPredecessor().getName())
                        nextevent.setProcessTime(event.getPredecessor().getProcessTime())
                        

                self.getSimulator().saveLog(" nextevent "+nextevent.print()+" defined.")
                  

                if (nextevent.getEquipment() != None) and (nextevent.getResource() != None):
                    nextevent.setStartTime(self.getSimulator().getTime())
                    if nextevent.getName() != "Machine Loading": 
                        self.getSimulator().ScheduleEvent(nextevent,self.getSimulator().getTime(),self,True)
                    else:
                        self.getSimulator().ScheduleEvent(nextevent,self.getSimulator().getTime(),self,False)
                else: 
                    self.getSimulator().ScheduleEvent(nextevent,"Pending",self,False)
            else: # machine loading directly tranfers the items..
                for item in event.getItems():
                    nextevent.getItems().append(item)

        if event.getName() == "Processing":
            if event in event.getEquipment().getProgressDict():
                newprogress = (event.getEquipment().getProgressDict()[event][-1][0],self.getSimulator().getTime())
                event.getEquipment().getProgressDict()[event] = event.getEquipment().getProgressDict()[event][:-1]
                event.getEquipment().getProgressDict()[event].append(newprogress)
                self.getSimulator().saveLog(" Progress steps: "+str(event.getEquipment().getProgressDict()[event]))
                removed = False
            for processirid,processorevent in event.getEquipment().getProcessMatch().items():
                self.getSimulator().saveLog(" Processor : "+str(processirid)+" event "+processorevent.print())
                if processorevent == event:
                    self.getSimulator().saveLog(" Processor : "+str(processirid)+ " match removed!!")
                    removed = True 
                    del event.getEquipment().getProcessMatch()[processirid]
                    break
            if not removed: 
                self.getSimulator().saveLog("Event not REMOVED!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                

        self.getSimulator().saveLog(" "+event.print()+" finalized.")
        
      
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

        process_df = pd.DataFrame(columns=["ItemID","Demand","Product","OperationName","ProcessID","ResourceID","Resource","Start","Completion"])


        for orderid,order in self.getProductionOrders().items():
            for item in order.getItems():
                for dt in item.getProcessData():
                    process_df.loc[len(process_df)] = dt
              
  
        return process_df
#########################################################################################################################
    def writeData(self):

        self.getDataManager().setResultDFs(self.getProcessDF())
        #process_df = self.getProcessDF()
        #location_df = self.getLocationDF()
        #process_df.to_csv("ProcessData.csv",index = False)
        #location_df.to_csv("LocationData.csv",index = False)  

        return 

        
