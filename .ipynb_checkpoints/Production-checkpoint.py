from Simulator import *
from datetime import timedelta,date


class Inventory(Resource):
    
    def __init__(self,mycap,sim,workmngr):
        super().__init__("Inventory",mycap,sim,workmngr)
        self.InputBuffer = Buffer("Input",None,1000,sim,workmngr)
        self.OutputBuffer = Buffer("Output",None,1000,sim,workmngr)

        self.InputBuffer.setLocation(self)
        self.OutputBuffer.setLocation(self)


    def getInputBuffer(self):
        return self.InputBuffer 
    def getOutputBuffer(self):
        return self.OutputBuffer 
       
#_________________________________________________________________________
class Buffer(Resource):
    def __init__(self,buftype,mach,mycap,sim,workmngr):
        super().__init__("Buffer",mycap,sim,workmngr)
        self.BufferType = buftype
        self.machine = mach
        self.LoadingEvent = None

    def getMachine(self):
        return self.machine
        
    def isInputType(self):   
        if self.BufferType == "Input":
            return True
        return False

    def getLoadingEvent(self):
        return self.LoadingEvent
    def setLoadingEvent(self,myev):
        self.LoadingEvent = myev
        return 

    def addItem(self,myitem):  
        
        self.generateEvent()
        self.getItems().append(myitem)
        myitem.setLocation(self.getLocation())
        
        return
        
    def removeItem(self,myit):  
        self.getItems().remove(myit) 
        return
  
    def generateEvent(self):

        print(" > "+str(self.getSimulator().getTime())+": "+self.getName()," event to generate...")

        if len(self.getItems()) == 0:
            return
 
        if self.getLoadingEvent() != None:
            return

        if not self.isInputType():
            load_event_type = self.getWorkMgr().getEventTypes()["Trailer Loading"]    
            self.setLoadingEvent(Event(self.getLocation(),"Pending",1,self.getSimulator(),load_event_type)) 
            self.getSimulator().ScheduleEvent(self.getLoadingEvent(),"Pending")
          
          
        else: # input buffer
            if self.getMachine() != None:   
                if len(self.getMachine().getItems()) == 0:
                    if self.getMachine().IsAutomated():
                        load_event_type = self.getWorkMgr().getEventTypes()["Machine Loading Automated"]
                        self.setLoadingEvent(Event(self.getLocation(),self.getSimulator().getTime(),1,self.getSimulator(),load_event_type))
                        self.getLoadingEvent().setEquipment(self.getLocation()); self.getLoadingEvent().setResource(self.getLocation())
                        self.getSimulator().ScheduleEvent(self.getLoadingEvent(),self.getSimulator().getTime())
                        
                        
                    else:
                        load_event_type = self.getWorkMgr().getEventTypes()["Machine Loading Manual"]
                        self.setLoadingEvent(Event(self.getLocation(),self.getSimulator().getTime(),1,self.getSimulator(),load_event_type))
                        self.getSimulator().getEventQueue()["Pending"].append(self.getLoadingEvent()) 
            else:
                return

     
        if self.getLoadingEvent()!= None: 
            print(" > "+str(self.getSimulator().getTime())+": "+self.getLoadingEvent().print()+" generated.")
            self.getLoadingEvent().setLoadUnloadPlace(self)
            self.getLoadingEvent().setItemSource(self)

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
        self.PriorityScoringFunctions = dict() # key: priority criterion, val: specific function
        self.AlgorithmSetting = dict() # key: Decision Point, val: Algorithm Name

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

        bringEquipment.setSuccessor(trailerLoading)
        bringEquipment.getPrecendenceDict()[trailerLoading.getName()] = ['Equipment','Resource','Destination','Event']
        trailerLoading.setSuccessor(trailerTransport)
        trailerLoading.getPrecendenceDict()[trailerTransport.getName()] = ['Equipment','Resource','Items']
        trailerLoading.getDecisionsDict()[trailerTransport.getName()] = "Trailer Destination"
        trailerTransport.setSuccessor(trailerUnloading)
        trailerTransport.getPrecendenceDict()[trailerUnloading.getName()] = ['Equipment','Resource','ItemSource']
        

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

        # Machine Loading -> Processing -> Machine Unloading

        # Outputbuffer: Items change, it creates pending trailer loading event. 
        
        machineLoadingAutomated.setSuccessor(machineProcessingAutomated)
        machineLoadingAutomated.getPrecendenceDict()[machineProcessingAutomated.getName()] = ['Equipment','Resource','Items']
        machineProcessingAutomated.setSuccessor(machineUnloadingAutomated)
        machineProcessingAutomated.getPrecendenceDict()[machineUnloadingAutomated.getName()] = ['Equipment','Resource','Items']

        machineLoadingManual.setSuccessor(machineProcessing)
        machineProcessing.setSuccessor(machineUnloadingManual)
        
      
        


        

    def getAlgorithmSetting(self):
        return self.AlgorithmSetting 

    
    def getPriorityScoringFunctions(self):
        return self.PriorityScoringFunctions


    def setPriorityFunctions(self):

        self.getPriorityScoringFunctions()["Trailer Loading"] = dict()
        self.getPriorityScoringFunctions()["Trailer Loading"]['FindMostCommon'] = self.findTrailerLoadScores
        
        self.getPriorityScoringFunctions()["Machine Loading Automated"] = dict()
        self.getPriorityScoringFunctions()["Machine Loading Automated"]['HighestNoItems'] = self.findMachineLoadAutoHighestItems

        self.getPriorityScoringFunctions()["Trailer Destination"] = dict()
        self.getPriorityScoringFunctions()["Trailer Destination"]['MostDemanded'] = self.findTrailerDestinationMostDemanded

        self.getPriorityScoringFunctions()["Trailer Unloading"] = dict()
        self.getPriorityScoringFunctions()["Trailer Unloading"]['UnloadFeasible'] = self.findTrailerUnloadFeasible

        
        return
    
    def printDemand(self,demand):
        print("Demand: Ref.No ",demand.getReferenceNo(),", Oprs: ",[(x.getAlternativeMachines()[0].getName(),x.getProcessTime()) for x in demand.getOperations()])

########################################################
    def createResources(self,res_dict):
  
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
            print("Resource",res.getType(),'id: ',res.getID()," created.")

        return
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
#___________________________________________________________________________  
    def createDemandTypes(self,notypes): # Product types

        for mytype in range(notypes):
            mydemandtype = DemandType(random.choice(self.all_pns),self.getDemandTypeName())
            self.all_pns.remove(mydemandtype.getReferenceNo())
            self.setOperations(mydemandtype)
            print("Demantype: ",[p.getName()+str([r.getName() for r in p.getAlternativeResources()])+"("+str(p.getRandVar().sampleValue())+")" for p in mydemandtype.getProcesses()])
            self.getDemandTypes().append(mydemandtype)

        return 
#___________________________________________________________________________  
    def createDemands(self,nodemands): # Production Orders

        deadline_min = date.today(); deadline_max = deadline_min+timedelta(days = 7)
        daterange = pd.date_range(deadline_min,deadline_max)
        
        for ordno in range(nodemands):
            dadlne = random.choice(daterange)
            myord = Demand(dadlne,self.giveDemandID(),random.choice(self.getDemandTypes()),1) #ddline,myid,demtype,quantity
            self.getDemands().append(myord)

        return

#____________________________________________________________________________
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
         
#______________________________________________________________________________
    def initializeSystem(self):
        # this is empty system initialization, all items start from central inventory..
        
        for myord in self.getDemands():
            self.createDemandItems(myord)
        return
#______________________________________________________________________________

    def handlePendingEvent(self,event):

        #print(" > "+str(self.getSimulator().getTime())+": handling event start..",event.getName(),"("+str(event.getID())+")")

        if event.getEquipment() == None: 
            equip = self.assignEquipment(event)

            if equip == None:
                return False

            #print(" > "+str(self.getSimulator().getTime())+": equipment selected ",equip.getName(),"("+str(equip.getID())+")")

            if event.getResource() == None: 
                res = self.assignResource(event)

               
                if res == None:
                    return False
        else: 
            if event.getResource() == None:
                res = self.assignResource(event)
                if res == None: 
                    return False


        #print(" > "+str(self.getSimulator().getTime())+":  handling event proceed to scheduling...",event.getName(),"("+str(event.getID())+")")
        
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

    def PrintStart(self):
        
        for res in self.Resources:
            res.print()
           
        for prod in self.Products:
            prod.print()
        
        for myord in self.Orders:
            myord.print()

            

    def findTrailerDestinationScores(self,items):
        print(" > "+str(self.getSimulator().getTime())+": >>> Algorithm:  findTrailerDestinationScores function <<<")
        
        select_dict = dict()
        for item in items:  
            for mach in item.getActiveOperation().getAlternativeResources():
                if not mach in select_dict:
                    select_dict[mach] = 0
                select_dict[mach] += 1
      
        
        for item in items:
            item.setPriorityScore(sum([select_dict[m] for m in item.getActiveOperation().getAlternativeResources()]))

        items.sort(key=lambda x: x.getPriorityScore(), reverse=True)

        return items

    def findTrailerLoadScores(self,event,items):
        print(" > "+str(self.getSimulator().getTime())+": >>> Algorithm: findTrailerLoadScores function <<<")
        
        select_dict = dict()
        for item in items:  
            myopr = item.getActiveOperation()
            if myopr!= None: 
                for mach in myopr.getAlternativeResources():
                    if not mach in select_dict:
                        select_dict[mach] = 0
                    select_dict[mach] += 1
            else:
                if not self.getCentralInventory() in select_dict:
                    select_dict[self.getCentralInventory()] = 0
                select_dict[self.getCentralInventory()] += 1
                

        # item 1: Next operation machines:  Mach1, Mach2
        # item 2: Next operation machines:  Mach1, Mach3
        # item 3: Next operation machines:  Mach4, Mach5

        #Scores: Item1: 3, Item2: 3, Item3: 2
        
        for item in items:
            myopr = item.getActiveOperation()
            if myopr!= None: 
                item.setPriorityScore(sum([select_dict[m] for m in myopr.getAlternativeResources()]))
            else:
                item.setPriorityScore(select_dict[self.getCentralInventory()])

        items.sort(key=lambda x: x.getPriorityScore(), reverse=True)

        return items

    def findTrailerDestinationMostDemanded(self,event,items):
        print(" > "+str(self.getSimulator().getTime())+": >>> Algorithm: findTrailerDestinationMostDemanded function <<<")
        select_dict = dict()
        for item in items:
            myopr = item.getActiveOperation()
            if myopr!= None: 
                for mach in myopr.getAlternativeResources():
                    if not mach in select_dict:
                        select_dict[mach] = 0
                    select_dict[mach] += 1
            else:
                if not self.getCentralInventory() in select_dict:
                    select_dict[self.getCentralInventory()] = 0
                select_dict[self.getCentralInventory()] += 1

        for item in items:  
            myopr = item.getActiveOperation()
            if myopr!= None: 
                item.setPriorityScore(sum([select_dict[m] for m in myopr.getAlternativeResources()]))
            else:
                item.setPriorityScore(select_dict[self.getCentralInventory()])


        items.sort(key=lambda x: x.getPriorityScore(), reverse=True)

        mostdemanded = None; highestdemand = 0

        for mymach,demand in select_dict.items():
            if mostdemanded == None:
                mostdemanded = mymach
                highestdemand = demand
            else: 
                if highestdemand < demand:
                    mostdemanded = mymach
                    highestdemand = demand

        return mostdemanded

    def findTrailerUnloadFeasible(self,event,items):
        print(" > "+str(self.getSimulator().getTime())+": >>> Algorithm: findTrailerUnloadFeasible function <<<")

        items_to_unload = []

        for item in items:
            myopr = item.getActiveOperation()
            if myopr!= None: 
                if event.getLocation() in myopr.getAlternativeResources():
                    items_to_unload.append(item)
            else:
                if event.getLocation() == self.getCentralInventory():
                    items_to_unload.append(item)
   
        return items_to_unload

 
        
    def findMachineLoadAutoHighestItems(self,event,items):
        
        print(" > "+str(self.getSimulator().getTime())+": >>> Algorithm: findMachineLoadAutoHighestItems function <<<")
        select_dict = dict()
        for item in items:
            myopr = item.getActiveOperation()
            if not myopr in select_dict:
                select_dict[myopr] = 0
            select_dict[myopr] += 1

        for item in items:
            item.setPriorityScore(select_dict[item.getActiveOperation()])

        items.sort(key=lambda x: x.getPriorityScore(), reverse=True)

        return items


    def ChooseDestination(self,trailer):
   
        print(" > "+str(self.getSimulator().getTime())+": ",trailer.getName()," ("+trailer.getLocation().getName()+"->) will choose destination ")

        # select items
        criterionname = self.getAlgorithmSetting()["Trailer Destination"]
        event_items = [i for i in trailer.getItems()]
        destination,event_items =  self.getPriorityScoringFunctions()["Trailer Destination"][criterionname](event_items)

        print(" > "+str(self.getSimulator().getTime())+": ",trailer.getName()," ("+trailer.getLocation().getName()+"->) chooses destination "+destination.getName())

        print(" > "+str(self.getSimulator().getTime())+":  ordered items ",[str(i.getID())  for i in event_items])

        event = Event((trailer.getLocation(),destination),"Trailer Transport","Operator","Trailer",self.getSimulator().getTime(),1,self.getSimulator())
        event.setEquipment(trailer); event.getEquipment().getMyEvents().append(event)

        itemid = 0
         
        while (len(event.getItems()) <  event.getEquipment().getCapacity()) and (itemid < len(event_items)):
            event.getItems().append(event_items[itemid])
            itemid+=1

        print(" > "+str(self.getSimulator().getTime())+":  event items ",[str(i.getID())  for i in event.getItems()])
                  
        return event

    def finalizeEvent(self,event):

        return

    def startEvent(self,event):
   
        event.getResource().setBusy()
        event.getEquipment().setBusy()

        event.setActive()

        if event.getName() in self.getAlgorithmSetting(): #choose the items that will be affected by the event

            selected_alg = self.getAlgorithmSetting()[event.getName()]
            event_items = [i for i in event.getItemSource().getItems()]
            event_items =  self.getPriorityScoringFunctions()[event.getName()][selected_alg](event,event_items)
          

   
            for item in event_items:
                if event.getEventType().isLoading():
                    if len(event.getItems()) == event.getEquipment().getCapacity(): 
                        break
                else:
                    if len(event.getItems()) == event.getLoadUnloadPlace().getCapacity():
                        break
                        
                event.getItems().append(item)

            
            #print(" > "+str(self.getSimulator().getTime())+":  event items ",[str(i.getID())  for i in event.getItems()])

        print(" > "+str(self.getSimulator().getTime())+": "+event.print()+" started.")

        return 

    def commpleteEvent(self,event):

        event.getResource().setIdle()
        event.getEquipment().setIdle()  
        
        if event in event.getEquipment().getMyEvents():
            event.getEquipment().getMyEvents().remove(event)
 
        #print(" > "+str(self.getSimulator().getTime())+": ",event.getName()," event static ",event.getEventType().isStatic()," loading ",event.getEventType().isLoading()," Loadunload placE: ",(" " if event.getLoadUnloadPlace() == None else event.getLoadUnloadPlace().getName()),type(event.getLoadUnloadPlace()))
        
        if event.getEventType().isStatic():
            if not event.getEventType().isProcess():
                for item in event.getItems():
                    if event.getEventType().isLoading():
                        event.getLoadUnloadPlace().removeItem(item)
                        event.getEquipment().additem(item)
                        print(" > "+str(self.getSimulator().getTime())+": ","Item "+str(item.getID())+" is loaded to "+event.getEquipment().getName())
                    else:
                        event.getEquipment().removeItem(item)
                        event.getLoadUnloadPlace().additem(item)
                        print(" > "+str(self.getSimulator().getTime())+": ","Item "+str(item.getID())+" is unloaded to "+event.getLoadUnloadPlace().getName()) 
                        if item.getActiveOperation() == None:
                            print(" > "+str(self.getSimulator().getTime())+":"+" item_"+str(item.getID())+" completed!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            else:
                for item in event.getItems():
                    myprocessdata = {"ItemID":item.getID(),"OperationName":item.getActiveOperation().getName(),"ProcessID":event.getID(),"ResourceID":event.getResource().getID(),"Start":event.getStartTime(),"Completion":self.getSimulator().getTime()}                 
                    item.getProcessData().append(myprocessdata)
                    
        else:
            event.getResource().setLocation(event.getLocation()[1])      
            if event.getResource()!= event.getEquipment():
                event.getEquipment().setLocation(event.getLocation()[1])

        # apply precedence event: loc,start,proctime,sim,eventype):
        nexteventype = event.getEventType().getSuccessor() 
        
        if nexteventype != None: 
            print(" > "+str(self.getSimulator().getTime())+": successor event "+event.getEventType().getSuccessor().getName()+", stc: "+str(nexteventype.isStatic())) 

            destination = None     
            nextlocation = event.getResource().getLocation()

            
            if not nexteventype.isStatic(): # decide destination
                decision_type = event.getEventType().getDecisionsDict()[nexteventype.getName()]
                selected_alg = self.getAlgorithmSetting()[decision_type]
                #print(" > "+str(self.getSimulator().getTime())+": decision_type ",decision_type,", selected_alg ",selected_alg)  
                destination = self.getPriorityScoringFunctions()[decision_type][selected_alg](event,event.getItems())
                #print(" > "+str(self.getSimulator().getTime())+": destination",destination.getName()) 
                nextlocation = (nextlocation,destination)

            nextevent = None
            
            if 'Event' in event.getEventType().getPrecendenceDict()[nexteventype.getName()]:
                if nexteventype.isLoading():
                    nextevent = event.getResource().getLocation().getOutputBuffer().getLoadingEvent()
            else:
                proctime = 1
                if "Processing" in nexteventype.getName():
                    proctime = event.getItems()[0].getActiveOperation().getRandVar().sampleValue()
                nextevent = Event(nextlocation,"Pending",proctime,self.getSimulator(),nexteventype)
               
            if nextevent == None:
                print(" > "+str(self.getSimulator().getTime())+": next event None ",event.print())  
            
            if 'Equipment' in event.getEventType().getPrecendenceDict()[nextevent.getEventType().getName()]:
                nextevent.setEquipment(event.getEquipment()); event.getEquipment().setAssigned()
            if 'Resource' in event.getEventType().getPrecendenceDict()[nextevent.getEventType().getName()]:
                nextevent.setResource(event.getResource()); event.getResource().setAssigned()
            if 'Items' in event.getEventType().getPrecendenceDict()[nextevent.getEventType().getName()]:
                for item in event.getItems():
                    nextevent.getItems().append(item)
            if 'ItemSource' in event.getEventType().getPrecendenceDict()[nextevent.getEventType().getName()]:
                nextevent.setItemSource(event.getEquipment())

            if not nextevent.getEventType().isProcess():
                if nextevent.getEventType().isStatic():
                    if nextevent.getEventType().isLoading():
                        if isinstance(nextevent.getEquipment(),Machine): 
                            nextevent.setLoadUnloadPlace(nextevent.getLocation().getInputBuffer())
                        else:
                            nextevent.setLoadUnloadPlace(nextevent.getLocation().getOutputBuffer())
                    else:
                        if isinstance(nextevent.getEquipment(),Machine): 
                            nextevent.setLoadUnloadPlace(nextevent.getLocation().getOutputBuffer())
                        else:
                            nextevent.setLoadUnloadPlace(nextevent.getLocation().getInputBuffer())
                else:
                    if nextevent.getItemSource() == None:
                        nextevent.setItemSource(event.getEquipment())
                    
                
            print(" > "+str(self.getSimulator().getTime())+": nextevent "+nextevent.print()+" defined.")
    

            if (nextevent.getEquipment() != None) and (nextevent.getResource() != None):
                nextevent.setStartTime(self.getSimulator().getTime())
                self.getSimulator().ScheduleEvent(nextevent,self.getSimulator().getTime())

        print(" > "+str(self.getSimulator().getTime())+": "+event.print()+" finalized.")
        
        if event.getLoadUnloadPlace()!= None:
            event.getLoadUnloadPlace().setLoadingEvent(None)
            if len(event.getLoadUnloadPlace().getItems()) > 0:
                event.getLoadUnloadPlace().generateEvent()
       
        
        return

    def writeData(self):

        process_df = pd.DataFrame(columns=["ItemID","OperationName","ProcessID","ResourceID","Start","Completion"])

        for demand in self.getDemands():
            for item in demand.getItems():
                for dt in item.getProcessData():
                    process_df.loc[len(process_df)] = dt

        
        process_df.to_csv("ProcessData.csv",index = False)        

        return 

        

