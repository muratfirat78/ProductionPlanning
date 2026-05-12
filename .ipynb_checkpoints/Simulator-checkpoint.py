from datetime import timedelta,date
import random
import pandas as pd


class Simulator(object):
    def __init__(self,timelimit):
        
        self.EventData = [] # [{"EventID':...,"EventName":...,'Location Name/ID':...,"Equipment Name/ID":...,"Resource Name/ID":...,"Items":...}]
        self.ExecutionData = [] # [{"EventID':...,"EventName":...,'Status':...}]
        self.queue = {} #key: time (start/completion times of events) , val: [event]
        self.time = 0
        self.eventno = 0
        self.TimeLimit = timelimit
        self.queue["Pending"] = []
        self.DataTypes = dict() # key: dataset name, val: dataframe objects. 

    def getDataTypes(self):
        return self.DataTypes

    def InsertDataRow(self,datatype,row):
        self.getDataTypes()[datatype].loc[len(self.getDataTypes()[datatype])] = row
        return

    def getEventData(self):
        return self.EventData
    def getExecutionData(self):
        return self.ExecutionData
        
   
    def getTimeLimit(self):
        return self.TimeLimit

    
    def RunSimulation(self,OperationsMgr): 

        while self.getTime() < self.getTimeLimit():
            self.updateTime()
            self.executeEvents(OperationsMgr)

        OperationsMgr.writeData()

        return
################################################################################################################        
    def executeEvents(self,workmgr):

        print(" > "+str(self.getTime())+": Pending events ",len(self.getEventQueue()["Pending"]))

        pending_events =[e for e in self.getEventQueue()["Pending"]]

        for event in pending_events: 
            if workmgr.handleEvent(event):
                self.getEventQueue()["Pending"].remove(event)
             

        if self.time in self.queue:
            ev_round = 1
            time_events =[e for e in self.queue[self.time]] # scheduled/started events

            
            while len(time_events) > 0: 
                print(" > "+str(self.getTime())+": Non-pending events ",len(time_events),"(",ev_round,")",[i.getName()+"("+str(i.getID())+")" for i in time_events])

                event_progress = 0
                for event in time_events:
                    if event.IsActive():  # completion of event
                        event_progress+=1
                        workmgr.commpleteEvent(event)
                        self.queue[self.time].remove(event)   
                    else:
                        workmgr.startEvent(event)    
                        self.queue[self.time].remove(event)
                        event_progress+=1          
                if event_progress== 0: 
                    print("All events pendig!!!")

                time_events =[e for e in self.queue[self.time]] # scheduled/started events
                ev_round+=1
            
     
        return
#############################################################################################################################          
    def ScheduleEvent(self,event, time):
    
        if not time in self.getEventQueue():
            self.getEventQueue()[time] = []
        print(" > "+str(self.getTime())+", "+event.print()+" in scheduled ? ",event in self.getEventQueue()[time])
        if not event in self.getEventQueue()[time]:
            self.getEventQueue()[time].append(event)
            print(" > "+str(self.getTime())+", "+event.print()+" scheduled start at time "+str(time))

        # schedule completion
        if time != "Pending":
            if not (time+event.getProcessTime()) in self.getEventQueue():
                self.getEventQueue()[time+event.getProcessTime()] = []
            
            if not event in self.getEventQueue()[time+event.getProcessTime()]:
                self.getEventQueue()[time+event.getProcessTime()].append(event)    
                print(" > "+str(self.getTime())+", "+event.print()+" scheduled completion at time "+str(time+event.getProcessTime()))
            

        return 
############################################################################################################################
        self.writeData()
    def updateTime(self):
        self.time+=1
        return
    def getTime(self):
        return self.time
    def getEventNo(self):
        self.eventno+=1
        return self.eventno
    def getEventQueue(self):
        return self.queue
#______________________________________________________________________________________


class EventType(object):
    def __init__(self,myname,restype,equiptype,static,loading,process):
        self.Name = myname
        self.ResourceType = restype # to help assigning 
        self.EquipmentType = equiptype # to help selecting    
     
        self.precendenceDict = dict() #key: successor event name, val: properties directly transformed to successor event
        self.decisionsDict = dict() #key: successor event name, val: decision to be made before the successor event scheduled
        self.static = static
        self.loading = loading # if static is False, this is not relevant. If static True and Loading false, then this is unloading. 
        self.process = process
        self.successortype = None
        self.predecesortype = None

    def setPredecessorType(self,myev):
        self.predecessortype = myev
        myev.setSuccessorType(self)
        return
    def getPredecessorType(self):
        return self.predecessortype
    def setSuccessorType(self,mysucc):
        self.successortype = mysucc
        return
    def getSuccessorType(self):
        return self.successortype
        

    def isStatic(self):
        return self.static

    def isLoading(self):
        return self.loading

    def isProcess(self):
        return self.process
    

    def getDecisionsDict(self):
        return self.decisionsDict

    def getPrecendenceDict(self):
        return self.precendenceDict
   

    def getName(self):
        return self.Name

    def getResourceType(self):
        return self.ResourceType
   
    def getEquipmentType(self):
        return self.EquipmentType

 


############################################################################

class Event(object):
    def __init__(self,loc,start,proctime,sim,eventype):
        self.EventType = eventype    
        self.ID = sim.getEventNo()   
        self.Location = loc  # static: resource, dynamic: (from buffer,to buffer)   
        self.StartTime = start
        self.ProcessTime = proctime     
        self.active = False    
        self.InfoDictionary = dict() # processing: ("operation",operation obj)
        self.ItemSource = None # this is where items will be selected
        self.Simulator = sim
        self.Resource = None 
        self.Equipment = None
        self.Items = []
        self.Place = None
        self.successor = None
        self.predecesor = None


    def setPlace(self,myown):
        self.Place = myown
        return
    def getPlace(self):
        return self.Place
        

    
    def setPredecessor(self,myev):
        self.predecessor = myev
        return
    def getPredecessor(self):
        return self.predecessor
    def setSuccessor(self,mysucc):
        self.successor = mysucc
        mysucc.setPredecessor(self)
        return
    def getSuccessor(self):
        return self.successor
    

    def getEventType(self):
        return self.EventType

    def getSimulator(self):
        return self.Simulator

    def getName(self):
        return self.EventType.getName()

    def setItemSource(self,myres):
        self.ItemSource = myres
        return 
        
    def getItemSource(self):
        return self.ItemSource

    def getItems(self):
        return self.Items

    def getResource(self):
        return self.Resource
    def setResource(self,myres):
        self.Resource = myres
        return 
    def getEquipment(self):
        return self.Equipment
    def setEquipment(self,myequip):
        self.Equipment = myequip
        return

    def print(self):

        equip = "Pending" if self.Equipment == None else self.Equipment.getName()

        res = "Pending" if self.Resource == None else self.Resource.getName()

        loc_str = ""
        
        if isinstance(self.getLocation(),tuple):
            loc_str= self.getLocation()[0].getName()+"->"+self.getLocation()[1].getName()
        else:
            loc_str = self.getLocation().getName()


        return str(self.getEventType().getName())+"("+str(self.getID())+"): "+loc_str+("" if self.getPlace() == None else ", place: "+self.getPlace().getName())+", equip: "+equip+", res: "+res+",  ["+ "-".join([str(i.getID()) for i in self.getItems()])+"], proctime: "+str(self.ProcessTime)
        
    def getProcessTime(self):
        return self.ProcessTime 

    def getInfoDict(self):
        return self.InfoDictionary

    def getLocation(self):
        return self.Location

    
    def setLocation(self,myloc):
        self.Location = myloc
        return 
    
        
    def getID(self):
        return self.ID
 
    def setActive(self):
        self.active = True
        return 
    def setInActive(self):
        self.active = False
        return 
        
    def IsActive(self):
        return self.active
         
    def setStartTime(self,mystrt):
        self.StartTime = mystrt
    def getStartTime(self):
        return self.StartTime 
  

##################################################################################################################################    
class Resource(object):
    def __init__(self,mytype,mycap,sim,workmgr):
        self.Simulator = sim
        self.WorkMgr = workmgr
        self.Type = mytype
        self.capacity = mycap
        self.Items = [] 
        self.LocationData= [] # [{"Entity": Name, "EntityID":...,"EventName":...,"EventID":...,"LocationID"",...,"LocationName":...,,"ArrivalTime":...,"}]

   
        self.location = None
        self.Status = "Idle" # or "Busy"
        
        self.MyEvents = []
        self.AssignedEvents = []
        self.ID = workmgr.giveResouceID()
        self.Name = mytype+"_"+str(self.ID)
        self.Itemcriteria = dict()

    def getLocationData(self):
        return self.LocationData
        
    def getItemCriteria(self):
        return self.Itemcriteria


    def generateEvent(self):
        # overwritten by subclassess
        return


    
    def getCapacity(self):
        return self.capacity

    def setItemCriteria(self,resource):
        return 

    def setLocation(self,myloc):
        self.location = myloc
        return
    def getLocation(self):
        return self.location
    def setBusy(self):
        self.Status = "Busy"
        return
    def setAssigned(self):
        self.Status = "Assigned"
        return
    def setIdle(self):
        self.Status = "Idle"
        return 
    def getWorkMgr(self):
        return self.WorkMgr
    def IsIdle(self):
        return self.Status == "Idle"


    def getID(self):
        return self.ID
       
    def getName(self):
        return self.Name  
    def getType(self):
        return self.Type
    def print(self):
        print("Res: ",self.Type,", cap: ",self.capacity)
    def getItems(self):
        return self.Items

    def removeItem(self):
        # overwritten by subclassess
        return
        
    def getSimulator(self):
        return self.Simulator

   
    
    def getMyEvents(self):
        return self.MyEvents

    def getAssignedEvents(self):
        return self.AssignedEvents

#______________________________________________________________________________________________________
class RandomVar(object):
    def __init__(self):
        self.Sampling = []
        self.Parameters = dict()

    def getParameters(self):
        return self.Parameters

    def getSampling(self):
        return self.Sampling

    def sampleValue(self):
        return random.choice(self.getSampling())
    
#_______________________________________________________________________       
class Process(object):
    
    def __init__(self,name,myid):
        self.MyRandVar =  RandomVar()
        self.Name = name
        self.ID = myid
        self.AlternativeResources = []
        

    def getRandVar(self):
        return self.MyRandVar
    
    def getProcessTime(self): 
        return self.getRandVar().sampleValue()

    def getAlternativeResources(self):
        return self.AlternativeResources 
        
    def getName(self):
        return self.Name
    def getID(self):
        return self.ID
 
        
#------------------------------------------------------------------------------------------------------
class DemandType(object):
    def __init__(self,myno,typename):
        
        self.ReferenceNumber = myno
        self.Processes = [] # assumed sequential processes..
        self.Predecessors = []
        self.Successor =  None
        self.TypeName = typename

    def getProcesses(self):
        return self.Processes

    def getTypeName(self):
        return self.TypeName
        

    def getPredecessors(self):
        return self.Predecessors
        
    def setSuccessor(self,myscss):
        self.Successor = myscss
        return 
    def getSuccessor(self):
        return self.Successor

    def getReferenceNo(self):
        return self.ReferenceNumber

    
#-------------------------------------------------------------------------------------------------------------------------     
class Demand(object):
    def __init__(self,ddline,myid,demtype,quantity):
        self.deadline = ddline
        self.Items = [] 
        self.InfoDictionary = dict()
        self.DemandType = demtype
        self.Quantity = quantity
        self.MyID = myid

    def getMyID(self):
        return self.MyID

    def getDemandType(self):
        return self.DemandType
 
    def getInfoDictionary(self):
        return self.InfoDictionary

   
    def getQuantity(self):
        return self.Quantity
        

    def getMyType(self):
        return self.ItemType 
        
    def getItems(self):
        return self.Items
        
    def print(self):     
        return

   
#_______________________________________________________________________        
class Item(object):
    def __init__(self,demand,myid):
       
        self.ProcessData= [] # [{"ItemID":...,"ProcessID":...,"ResourceID"",...,"Start":...,"Completion":...}]
        self.LocationData= [] # [{"Entity": Item, "EntityID":...,"EventName":...,"EventID":...,"LocationID"",...,"LocationName":...,,"ArrivalTime":...,"}]
        self.location = None
        self.ID = myid
        self.Demand = demand
        self.InfoDictionary = dict()
        self.PriorityScore = 0

    def setPriorityScore(self,myscore):
        self.PriorityScore = myscore
        return
    def getPriorityScore(self):
        return self.PriorityScore
    
    def getActiveOperation(self):
        processnames = [pdt["OperationName"] for pdt in self.getProcessData()]
        nextprocess = None
        for process in self.getDemand().getDemandType().getProcesses():
            if not process.getName() in processnames:
                nextprocess = process
                break
        return nextprocess

    def getInfoDictionary(self):
        return self.InfoDictionary

    def getProcessData(self):
        return self.ProcessData 

    def getLocationData(self):
        return self.LocationData 


    def setLocation(self,myloc):
        self.location = myloc
        return
    def getDemand(self):
        return self.Demand

    def getLocation(self):
        return self.location
    def getID(self):
        return self.ID

    
#__________________________________________________________________________________________________________________________________
class OperationsManager(object):
    def __init__(self,sim,demandname):
        self.Resources = []
        self.processid = 0
        self.itemid = 0
        self.resourceid = 0   
        self.demandid = 0
        self.Simulator = sim
        self.Demands = []  
        self.DemandTypes = []
        self.DemandTypeName = demandname
        self.EventTypes = dict()
        self.AlgorithmManager = AlgorithmManager(sim,self)

    def getAlgorithmManager(self):
        self.AlgorithmManager
        
    
    def getEventTypes(self):
        return self.EventTypes
        
    def getDemandTypeName(self):
        return self.DemandTypeName 


    def createResources(self,res_dict):
        # overwritten by subclassess
        return

    def setOperations(self,demandtype):
        #overwritten by subclassess
        return

    def createDemandTypes(self,typename,notypes):      
        #overwritten by subclassess
        return 

    def createDemands(self,daterange,dtype):
        #overwritten by subclassess
        return 

    def initializeSystem(self):
        #overwritten by subclassess
        return 
        
    def handleEvent(self,event):
        #overwritten by subclassess
        return
    def writeData(self):
        #overwritten by subclassess
        return
#___________________________________________________________________________________________________________________________
    def handlePendingEvent(self,event):
  
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
        else: 
            if event.getResource() == None:
                res = self.assignResource(event)
                if res == None: 
                    return False
                    
        return True
#####################################################################################################################################################
    def startEvent(self,event):
        event.getResource().setBusy()
        event.getEquipment().setBusy()

        event.setActive()

        if event.getName() in self.getProductionAlgManager().getAlgorithmSetting(): 

            decision_name,selected_algorithm = self.getProductionAlgManager().getAlgorithmSetting()[event.getName()]
            print(" > "+str(self.getSimulator().getTime())+": "+event.print()+" "+decision_name+"--"+selected_algorithm)
            # check if selecting items
            if decision_name == 'Select Items':
                
                item_source = event.getEquipment() if not event.getEventType().isLoading() else event.getPlace()
                source_items = [i for i in item_source.getItems()]
                print(" > "+str(self.getSimulator().getTime())+": ev",event.getName(),"decision_type ",decision_name,", selected_alg ",selected_algorithm) 
                print(" > "+str(self.getSimulator().getTime())+": source items ",[i.getID() for i in source_items])  
                algorithm_function = self.getProductionAlgManager().getPriorityScoringFunctions()[event.getName()][(decision_name,selected_algorithm)]
                sorted_items = algorithm_function(event,source_items)
                
                print(" > "+str(self.getSimulator().getTime())+": sorted items ",[i.getID() for i in sorted_items])  
                for item in sorted_items:
                    if event.getEventType().isLoading():
                        if len(event.getItems()) == event.getEquipment().getCapacity(): 
                            break
                    else:
                        if len(event.getItems()) == event.getPlace().getCapacity():
                            break
                            
                    event.getItems().append(item)

                    
            if decision_name == 'Select Destination':
                from_location = event.getResource().getLocation()
                algorithm_function = self.getProductionAlgManager().getPriorityScoringFunctions()[event.getName()][(decision_name,selected_algorithm)]      
                print(" > "+str(self.getSimulator().getTime())+": decision_type ",decision_name,", selected_alg ",selected_algorithm)  
                destination = algorithm_function(event,event.getItems())
                print(" > "+str(self.getSimulator().getTime())+": destination",destination.getName()) 
                event.setLocation((from_location,destination))
            
            #print(" > "+str(self.getSimulator().getTime())+":  event items ",[str(i.getID())  for i in event.getItems()])

        print(" > "+str(self.getSimulator().getTime())+": "+event.print()+" started.")
        return 
####################################################################################################################################################
    def commpleteEvent(self,event):
        #overwritten by subclassess
        return 
######################################################################################################################################################
######################################################################################################################################################

    
    def giveItemID(self):
        self.itemid+=1
        return self.itemid
        
    def giveDemandID(self):
        self.demandid+=1
        return self.demandid

    def giveProcessID(self):
        self.processid+=1
        return self.processid

        
    def giveResouceID(self):
        self.resourceid+=1
        return self.resourceid
        
    def getSimulator(self):
        return self.Simulator
    
    def getDemands(self):
        return self.Demands

    def getResources(self):
        return self.Resources

    def getDemandTypes(self):
        return self.DemandTypes
############################################################################################################      
class AlgorithmManager(object):
    def __init__(self,sim,oprmgr):
        self.PriorityScoringFunctions = dict() # key: priority criterion, val: specific function
        self.AlgorithmSetting = dict() # key: event name, val: (Decision name, Algorithm name)
        self.simulator = sim
        self.OperationsManager = oprmgr

    def getAlgorithmSetting(self):
        return self.AlgorithmSetting 
        
    def getOperationsManager(self):
        return self.OperationsManager
 
    def getPriorityScoringFunctions(self):
        return self.PriorityScoringFunctions

    def getSimulator(self):
        return self.simulator
################################################################################
class FeasibilityChecker():
    def __init__(self,Simulator,OprsMgr):
        
        self.Simulator = Simulator
        self.OperationsManager = OprsMgr

        
    def getOperationsManager(self):
        return self.OperationsManager

    def getSimulator(self):
        return self.Simulator

        
    def CheckFeasibility(self):
        #overwritten by subclassess
        return True
        

