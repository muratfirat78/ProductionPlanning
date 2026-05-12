from datetime import timedelta,date
import random
import pandas as pd


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


        return str(self.getEventType().getName())+"("+str(self.getID())+"): "+loc_str+("" if self.getPlace() == None else ", place: "+self.getPlace().getName())+", equip: "+equip+", res: "+res+", "+str(len(self.getItems()))+" items, proctime: "+str(self.ProcessTime)
        
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
    def __init__(self,myname,mytype,mycap,sim,workmgr):
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
        if myname == None: 
            self.Name = mytype+"_"+str(self.ID)
        else:
            self.Name = myname
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

    def setID(self,myid):
        self.ID = myid
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
#____________________________________________________________________________________

    
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
    def __init__(self,myno,myid,name):
        
        self.PN = myno
        self.ID = myid
        self.Processes = [] # assumed sequential processes..
        self.Predecessors =  dict() # key: pred, val: multiplier
        self.Successors =  dict() # key: successor, val: multiplier
        self.Name = name

    def getID(self):
        return self.ID

    def getProcesses(self):
        return self.Processes

    def getName(self):
        return self.Name
        

    def getPredecessors(self):
        return self.Predecessors
        
 
    def getSuccessors(self):
        return self.Successors

    def getPN(self):
        return self.PN

    
#-------------------------------------------------------------------------------------------------------------------------     
class Demand(object):
    def __init__(self,ddline,myid,demtype,quantity):
        self.deadline = ddline
        self.Items = [] 
        self.InfoDictionary = dict()
        self.DemandType = demtype
        self.Quantity = quantity
        self.MyID = myid

    def getID(self):
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

    def getDeadline(self):
        return self.deadline

   
#_______________________________________________________________________        
class Item(object):
    def __init__(self,demand,myid):
       
        self.ProcessData= [] # {"ItemID","OperationName","ProcessID","ResourceID","Start","Completion"}   
        self.LocationData= [] # {"Entity":"Item","EntityID","EventName","EventID","LocationID","LocationName","Time"}   
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

        oprseq = self.getDemand().getFinalProduct().getOperationSequences()[self.getDemand().getID()]

        if len(self.getProcessData()) < len(oprseq):
            return oprseq[len(self.getProcessData())]
        else:
            return None

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

    
        

