from Simulator import *
from productionmain import *
from productionalgs import *


class productionFeasibilityChecker():
    def __init__(self,Simulator,ShopFloorMgr):
        
        self.Simulator = Simulator
        self.OperationsManager = ShopFloorMgr

        
    def getOperationsManager(self):
        return self.OperationsManager

    def getSimulator(self):
        return self.Simulator

        
    def CheckFeasibility(self,location_df,process_df):

        # Check for every item:
        #            if the processes are completed in proces data, 
        #               start and completion times of operations respect precedence ordering
        #               finally items come back to inventory or not (if simulation times allows. 


        # Check for every entity:
        #            if the routing is continous.
        #               start and completion times of operations respect precedence ordering
        



        return True
        

    
       
#_________________________________________________________________________
class Buffer(Resource):
    def __init__(self,buftype,mach,mycap,sim,workmngr):
        super().__init__("Buffer",mycap,sim,workmngr)
        self.BufferType = buftype
        self.machine = mach
        self.PendingEvent = None

    def getMachine(self):
        return self.machine
        
    def isInputType(self):   
        if self.BufferType == "Input":
            return True
        return False

    def getPendingEvent(self):
        return self.PendingEvent

    def setPendingEvent(self,myev):
        self.PendingEvent = myev
        return 
        
        

    def addItem(self,myitem):     
        print(" > "+str(self.getSimulator().getTime())+": adding item to "+self.getName())
        self.getItems().append(myitem)
        self.generateEvent()
        myitem.setLocation(self.getLocation())
        
        return
        
    def removeItem(self,myit):  
        self.getItems().remove(myit)  
        return
  
    def generateEvent(self):
        
        if len(self.getItems()) == 0 or self.getPendingEvent() != None:
            return

        if not self.isInputType(): #output buffer
            load_event_type = self.getWorkMgr().getEventTypes()["Trailer Loading"]    
            self.setPendingEvent(Event(self.getLocation(),"Pending",1,self.getSimulator(),load_event_type)) 
            self.getSimulator().ScheduleEvent(self.getPendingEvent(),"Pending")
      
        else: # input buffer
            if self.getMachine() != None:   
                if len(self.getMachine().getItems()) == 0:
                    if self.getMachine().IsAutomated():
                        print(" > "+str(self.getSimulator().getTime())+": "+self.getName()," automated loading generated..")
                        load_event_type = self.getWorkMgr().getEventTypes()["Machine Loading Automated"]
                        self.setPendingEvent(Event(self.getLocation(),self.getSimulator().getTime(),1,self.getSimulator(),load_event_type))
                        self.getPendingEvent().setEquipment(self.getMachine()); self.getPendingEvent().setResource(self.getMachine())
                        self.getSimulator().ScheduleEvent(self.getPendingEvent(),self.getSimulator().getTime())
   
                    else:
                        load_event_type = self.getWorkMgr().getEventTypes()["Machine Loading Manual"]
                        self.setPendingEvent(Event(self.getLocation(),self.getSimulator().getTime(),1,self.getSimulator(),load_event_type))
                        self.getSimulator().getEventQueue()["Pending"].append(self.getPendingEvent()) 
                        self.getPendingEvent().setEquipment(self.getMachine())
            else:
                return

     
        if self.getPendingEvent()!= None: 
            print(" > "+str(self.getSimulator().getTime())+": "+self.getPendingEvent().print()+" generated.")
            self.getPendingEvent().setPlace(self)
            self.getPendingEvent().setItemSource(self)

        return
        
    
#_______________________________________________________________________  
class Machine(Resource):
    
    def __init__(self,mycap,sim,workmngr):
        super().__init__("Machine",mycap,sim,workmngr)
        self.InputBuffer = Buffer("Input",self,1000,sim,workmngr)
        self.OutputBuffer = Buffer("Output",self,1000,sim,workmngr)
        self.automated = True

        self.InputBuffer.setLocation(self)
        self.OutputBuffer.setLocation(self)
   
        
    def getInputBuffer(self):
        return self.InputBuffer 
    def getOutputBuffer(self):
        return self.OutputBuffer 
    def IsAutomated(self):
        return self.automated

    def removeItem(self,myit):
        print(" > "+str(self.getSimulator().getTime())+": "+self.getName()," item removed, input buffer is triggered for loading ",len(self.getInputBuffer().getItems()))
        self.getItems().remove(myit)
        if len(self.getItems()) == 0 and len(self.getInputBuffer().getItems()) > 0:
            self.getInputBuffer().generateEvent()
        return
        
#___________________________________________________________________________________________
class Operator(Resource):
    
    def __init__(self,avshift,mycap,sim,workmngr):
        super().__init__("Operator",mycap,sim,workmngr)
        self.AvailableShift = avshift
      
        
        
    def GetAvailableShift(self):
        return self.AvailableShift

#_________________________________________________________________________________________
class Trailer(Resource):
    def __init__(self,mycap,sim,workmngr):
        super().__init__("Trailer",mycap,sim,workmngr)  
        self.location = None
        self.outputbuffers = []  
        self.destination = None

        
    def getOutputbuffers(self):
        return self.outputbuffers
    
    def setDestination(self,mydest):
        self.destination = mydest
        return
    def getDestination(self):
        return self.destination


    
#_______________________________________________________________________       
class Operation(Process):
    def __init__(self,name,myid,proctime):
        super().__init__(name,myid)
        self.getRandVar().getSampling().append(proctime) 
        
#_______________________________________________________________________          
class Product(object):
    def __init__(self,pn):
        self.PN = pn
        self.Operations = []
        self.Predecessors = []
        self.Successor =  None
        
    def getOperations(self):
        return self.Operations

    def getActiveOperation(self,item):
        
        for opr in self.getOperations():
            if len([x[0][0] for x in item.getExecutions() if x[0][0] == opr]) == 0:
                return opr    
                
        return None
        

    def getPredecessors(self):
        return self.Predecessors
        
    def setSuccessor(self,myscss):
        self.Successor = myscss
        return 
        
    def getSuccessor(self):
        return self.Successor

   
        
    def getPN(self):
        return self.PN


        
#################################################################################
class ShopFloorManager(OperationsManager): 
    def __init__(self,sim,demandtypename):
        super().__init__(sim,demandtypename)
        
        self.CentralInventory = Inventory(10000,sim,self) 
        self.all_pns = [str(x) for x in range(1000)]
        self.ProductionAlgManager = ProductionAlgManager(sim,self)
    
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
        self.getEventTypes()["Machine Loading Manual"]= machineLoadingManual

        # Machine Loading -> Processing -> Machine Unloading (manual and automated)

        # Outputbuffer: Items change, it creates pending trailer loading event. 
        
        machineLoadingAutomated.setSuccessorType(machineProcessingAutomated)
        machineLoadingAutomated.getPrecendenceDict()[machineProcessingAutomated.getName()] = ['Equipment','Resource','Items']
        machineProcessingAutomated.setSuccessorType(machineUnloadingAutomated)
        machineProcessingAutomated.getPrecendenceDict()[machineUnloadingAutomated.getName()] = ['Equipment','Resource','Items']

        machineLoadingManual.setSuccessorType(machineProcessing)
        machineProcessing.setSuccessorType(machineUnloadingManual)
    
   

    
    def printDemand(self,demand):
        print("Demand: Ref.No ",demand.getReferenceNo(),", Oprs: ",[(x.getAlternativeMachines()[0].getName(),x.getProcessTime()) for x in demand.getOperations()])

########################################################
    def createInstance(self,res_dict,notypes,nodemands):
  
        for mytype,resinfo in res_dict.items():

            for resparam in resinfo:
                
                if mytype == "Machines":
                    mach = Machine(resparam,self.getSimulator(),self); mach.setLocation(mach)
                    self.getResources().append(mach)
                if mytype == "Operators":
                    optr = Operator(1,resparam,self.getSimulator(),self); optr.setLocation(self.getCentralInventory())
                    self.getResources().append(optr) # avshift,mycap,sim,workmngr
                if mytype == "Trailers":
                    trlr = Trailer(resparam,self.getSimulator(),self); trlr.setLocation(self.getCentralInventory())
                    self.getResources().append(trlr)

        for res in self.getResources():
            if isinstance(res,Machine) or isinstance(res,Inventory):
                print("Resource",res.getType(),'id: ',res.getID(),("" if res.getInputBuffer() == None else res.getInputBuffer().getName()),("" if res.getOutputBuffer() == None else res.getOutputBuffer().getName())," created.")
            else:
                print("Resource",res.getType(),'id: ',res.getID()," created.")

        for mytype in range(notypes):
            mydemandtype = DemandType(random.choice(self.all_pns),self.getDemandTypeName())
            self.all_pns.remove(mydemandtype.getReferenceNo())
            self.setOperations(mydemandtype)
            print("Demantype: ",[p.getName()+str([r.getName() for r in p.getAlternativeResources()])+"("+str(p.getRandVar().sampleValue())+")" for p in mydemandtype.getProcesses()])
            self.getDemandTypes().append(mydemandtype)


        deadline_min = date.today(); deadline_max = deadline_min+timedelta(days = 7)
        daterange = pd.date_range(deadline_min,deadline_max)
        
        for ordno in range(nodemands):
            dadlne = random.choice(daterange)
            myord = Demand(dadlne,self.giveDemandID(),random.choice(self.getDemandTypes()),1) #ddline,myid,demtype,quantity
            self.getDemands().append(myord)

        for myord in self.getDemands():
            self.createDemandItems(myord)

        return
#################################################################################################################################
    def getProductionAlgManager(self):
        return  self.ProductionAlgManager 
#########################################################
    def setOperations(self,demandtype):

        nooprs = random.choice(range(1,3))      
        machs = [x for x in self.getResources() if x.getType() == "Machine"]
        
        prevs= []
        
        for opr in range(1,nooprs+1):
            
            myopr = Operation(demandtype.getReferenceNo()+"_Opr_"+str(opr),self.giveProcessID(),random.choice(range(1,5)))
          
            mach = random.choice([x for x in machs if not x in prevs])
            myopr.getAlternativeResources().append(mach)
            prevs.append(mach)
            demandtype.getProcesses().append(myopr)      

        return
#_____________________________________________________________________
    def createDemandItems(self,demand): # Physical products
        
        if len(demand.getDemandType().getPredecessors()) == 0:
            for itm in range(demand.getQuantity()):
                myitem = Item(demand,self.giveItemID())
                print("Item",myitem.getID()," of prod ",demand.getDemandType().getTypeName(), demand.getDemandType().getReferenceNo(),' id ',demand.getMyID()," created.")
                self.getCentralInventory().getOutputBuffer().addItem(myitem) # generate trailer loading event.
                demand.getItems().append(myitem)
        else:
            for preddemnd in demand.getDemandType().getPredecessors():
                self.createDemandItems(preddemnd)

        return
         
#______________________________________________________________________

    def handleEvent(self,event):

        if not self.handlePendingEvent(event):
            return False

        timedelay = 0
        opr_move = None
        if event.getEquipment().getLocation() != event.getLocation():
                            
            if event.getResource().getLocation() != event.getEquipment().getLocation():
                loc_tuple = (event.getResource().getLocation(),event.getEquipment().getLocation())
                opr_move = Event(loc_tuple,"Resource Move","Operator","Operator",self.getSimulator().getTime(),1,self.getSimulator())
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
                loc_tuple = (event.getResource().getLocation(),event.getLocation())
                opr_move = Event(loc_tuple,"Resource Move","Operator","Operator",self.getSimulator().getTime(),1,self.getSimulator())
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
                     
                            
                        if item.getActiveOperation() == None:
                            print(" > "+str(self.getSimulator().getTime())+":"+" item_"+str(item.getID())+" completed!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
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
                    myprocessdata = {"ItemID":item.getID(),"OperationName":item.getActiveOperation().getName(),"ProcessID":event.getID(),"ResourceID":event.getResource().getID(),"Start":event.getStartTime(),"Completion":self.getSimulator().getTime()}                 
                    item.getProcessData().append(myprocessdata)
                    location_update = {"Entity":"Item","EntityID":item.getID(),"EventName":event.getName(),"EventID":event.getID(),"LocationID":event.getLocation().getID(),"LocationName":event.getLocation().getName(),"Time":self.getSimulator().getTime()}   
                    item.getLocationData().append(location_update)
                    
        else: # make location updates for dynamic event
            event.getResource().setLocation(event.getLocation()[1]) 
            location_update = {"Entity":event.getResource().getName(),"EntityID":event.getResource().getID(),"EventName":event.getName(),"EventID":event.getID(),"LocationID":event.getLocation()[1].getID(),"LocationName":event.getLocation()[1].getName(),"Time":self.getSimulator().getTime()}  
            event.getResource().getLocationData().append(location_update)

            location_update = {"Entity":event.getEquipment().getName(),"EntityID":event.getEquipment().getID(),"EventName":event.getName(),"EventID":event.getID(),"LocationID":event.getLocation()[1].getID(),"LocationName":event.getLocation()[1].getName(),"Time":self.getSimulator().getTime()}  
            event.getEquipment().getLocationData().append(location_update)
            
            if event.getResource()!= event.getEquipment():
                event.getEquipment().setLocation(event.getLocation()[1])

            for item in event.getEquipment().getItems():
                location_update = {"Entity":"Item","EntityID":item.getID(),"EventName":event.getName(),"EventID":event.getID(),"LocationID":event.getLocation()[1].getID(),"LocationName":event.getLocation()[1].getName(),"Time":self.getSimulator().getTime()}   
                item.getLocationData().append(location_update)
          
        nexteventtype = event.getEventType().getSuccessorType() 

        
        if nexteventtype != None: 
            print(" > "+str(self.getSimulator().getTime())+": successor event "+event.getEventType().getSuccessorType().getName()+", stc: "+str(nexteventtype.isStatic())) 

            
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
                    print(" > "+str(self.getSimulator().getTime())+": setPlace>>>>>>>>>>>>>  "+nextevent.getLocation().getName()+".")
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

    def writeData(self):

        process_df = pd.DataFrame(columns=["ItemID","OperationName","ProcessID","ResourceID","Start","Completion"])
        location_df= pd.DataFrame(columns=["Entity","EntityID","EventName","EventID","LocationID","LocationName","Time"])

        for demand in self.getDemands():
            for item in demand.getItems():
                for dt in item.getProcessData():
                    process_df.loc[len(process_df)] = dt
                for dt in item.getLocationData():
                     location_df.loc[len(location_df)] = dt

        for resource in self.getResources():
            for dt in resource.getLocationData():
                location_df.loc[len(location_df)] = dt

        
        process_df.to_csv("ProcessData.csv",index = False)
        location_df.to_csv("LocationData.csv",index = False)  

        return 

        
#################################################################################################
