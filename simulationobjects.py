from datetime import timedelta,date
import random
import pandas as pd
from stochastic import *


class EventType(object):
    def __init__(self,myname,restype,equiptype,static,loading,process,myset):
        self.Name = myname
        self.ResourceType = restype # to help assigning 
        self.EquipmentType = equiptype # to help selecting    
     
        self.precendenceDict = dict() #key: successor event name, val: properties directly transformed to successor event
        self.decisionsDict = dict() #key: successor event name, val: decision to be made before the successor event scheduled
        self.static = static
        self.loading = loading # if static is False, this is not relevant. If static True and Loading false, then this is unloading. 
        self.process = process
        self.setup = myset
        self.successortype = None
        self.predecessortype = None
        self.preemptable = False
        self.decisions = [] # of tuples (stage,type). 
                            # Stage: handle, start, or complete. Type: SelectItems, SelectDestination, Assign Equipment, Assign Resource. 

        self.itemdirection = True # Place -> Equipment, False means Equipment -> Place


    def isSetup(self):
        return self.setup
        
    def setItemDirection(self,myst):
        self.itemdirection = myst
        return

    def getItemDirection(self):
        return self.itemdirection

    def getDecisions(self):
        return self.decisions

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

    def setPreemptable(self,status):
        self.preemptable = status
        return

    def isPreemptable(self):
        return self.preemptable 

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
        self.CompletionTime = None
        self.active = False    
        self.InfoDictionary = dict() # processing: ("operation",operation obj)
        self.ItemSource = None # this is where items will be selected
        self.Simulator = sim
        self.Resource = None 
        self.Equipment = None
        self.Items = []
        self.Place = None
        self.successor = None
        self.predecessor = None
        # events: ML,MU resources are operators and Processing resources are machines.  
        self.definedsuccessors = dict() #key: successor type, val: successor event defined
        self.ProgressDict = dict() # key: resource, val: [(start,end)], all in simtime

        self.precedencetypes = dict() # key: successor or predecessor, val: "F2S", "SS", "SF"

        self.startdelay = 0
        self.logisticevents = []
        

    def getLogisticEvents(self):
        return self.logisticevents
    def getStartDelay(self):
        return self.startdelay

    def increaseStartDelay(self):
        self.startdelay+=1
        return 
        
    def getPrecedenceTypes(self):
        return self.precedencetypes

    def getProgressDict(self):
        return self.ProgressDict
        
    def setProcessTime(self,mytime):
        self.ProcessTime = mytime
        return

    def getDefinedSuccessors(self):
        return self.definedsuccessors


    def setCompletionTime(self,mytime):
        self.CompletionTime = mytime
        return

    def getCompletionTime(self):
        return self.CompletionTime 
        
    
    def setPlace(self,myown):
        self.Place = myown
        return
    def getPlace(self):
        return self.Place


    def getTotalProgress(self):

        totalprogress = 0; openprogresses = 0

        if len(self.getLogisticEvents()) > 0:
            return totalprogress
        
        if self.getEventType().isPreemptable():

            for resource,proglist in self.getProgressDict().items():
                totalprogress+= sum([((p[1] if p[1] != 0 else self.getSimulator().getTime())-p[0]) for p in proglist])
                openprogresses+=sum([1 for p in proglist if p[1] == 0])
                
            if openprogresses > 1:
                self.getSimulator().saveLog("ERROR: Premeptable Event "+self.getName()+"["+str(self.getID())+"]"+" has more than one open progresses..")
                for resource,proglist in self.getProgressDict().items():
                    self.getSimulator().saveLog("REPORT: Res "+resource.getName()+"Progresses of "+self.getName()+"["+str(self.getID())+"]"+": "+str([(p[0],p[1]) for p in proglist]))

            pred = self.getPredecessor()
            
            if pred!= None:
                for nextevent,prectype in pred.getPrecedenceTypes().items(): 
                    if prectype == 'Simultaneous Start' and nextevent == self:
                        totalprogress-= pred.getStartDelay()
                        break

       
            for nextevent,prectype in self.getPrecedenceTypes().items(): 
                if prectype == 'Simultaneous Finish':
                    totalprogress-= nextevent.getStartDelay()
                    break

        else:
            totalprogress+=min(self.getSimulator().getTime(),self.getCompletionTime()) - self.getStartTime()
           

        return totalprogress

    
    def setPredecessor(self,myev):
        self.predecessor = myev
        return
    def getPredecessor(self):
        return self.predecessor
    def setSuccessor(self,mysucc):
        self.successor = mysucc
        if mysucc.getPredecessor() == None:
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

        try: 
            equip = "Pending" if self.getEquipment() == None else self.getEquipment().getName()+"("+str(len(self.getEquipment().getItems()))+")"
    
            res = "Pending" if self.Resource == None else self.Resource.getName()
    
            loc_str = ""
            
            if isinstance(self.getLocation(),tuple):
                loc_str =("no location" if self.getLocation()[0] == None else self.getLocation()[0].getName())
                loc_str +="->"+("no location" if self.getLocation()[1] == None else self.getLocation()[1].getName())
               
            else:
                loc_str = "no location" if self.getLocation() == None else self.getLocation().getName()
    
    
            return str(self.getName())+"("+str(self.getID())+"): loc "+loc_str+(" no place " if self.getPlace() == None else ", place  "+self.getPlace().getName()+"("+str(len(self.getPlace().getItems()))+")")+", equip: "+equip+", res: "+res+", "+str(len(self.getItems()))+" items, proctime: "+str(self.ProcessTime)
        except Exception as e:
            self.getSimulator().saveLog("ERROR in event printing: "+str(e))
        
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
        self.Available = False # changes with shift availability
        self.Idle = False # changes with event executions
        self.MyEvents = []
        self.AssignedEvents = []
        self.ID = workmgr.giveResouceID()
        if myname == None: 
            self.Name = mytype+"_"+str(self.ID)
        else:
            self.Name = myname
        self.Itemcriteria = dict()
        self.processtype = None

    def getProcessType(self):
        return self.processtype
    def setProcessType(self,mypr):
        self.processtype = mypr
        return

    def getLocationData(self):
        return self.LocationData
        
    def getItemCriteria(self):
        return self.Itemcriteria


    def generateEvent(self):
        # overwritten by subclassess
        return


    def checkShiftChange(self,shift):
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

     
   

    
    def setAvailable(self,status):
        self.Available = status
        return
    def isAvailable(self):
        return self.Available

    def setIdle(self,status):
        self.Idle = status
        return
    def isIdle(self):
        return self.Idle 
   
    def getWorkMgr(self):
        return self.WorkMgr

        
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

    def setLocationData(self,event,sim):

        if event != None: 

            actual_comp = sim.getRealTime()

            locid = None; locname = None

            if event.getLocation() != None:
                if isinstance(event.getLocation(),tuple):
                    locid =  str(event.getLocation()[0].getID())+"->"+str(event.getLocation()[1].getID())
                    locname = event.getLocation()[0].getName()+"->"+event.getLocation()[1].getName()
                else:
                    locid =  event.getLocation().getID()
                    locname = event.getLocation().getName()
            else:
                sim.saveLog("ERROR location is None of event "+event.getName()+"["+str(event.getID())+"]")
            
            location_update = {"Entity":self.getName(),"EntityID":self.getID(),"EventName":event.getName(),"EventID":event.getID(),"LocationID":locid,"LocationName":locname,"Time":actual_comp}  
            self.getLocationData().append(location_update)
          

        return 
        
#_______________________________________________________________________       
class Process(object):
    def __init__(self,demand,name,myid,dist):

        self.MyRandVar = RandomVar()
            
        if dist == 'LogNormal':
            self.MyRandVar = LogNormalVar()
        if dist == 'Normal':
            self.MyRandVar = NormalVar()
       

        self.ExecutionData= [] # {"OperationName","ProcessID","ResourceID","Resource","Start","Completion","DemandID","Product","NrItems"}      
        self.Name = name
        self.ID = myid
        self.AlternativeResources = []
        self.Cancelled = False
        self.Finished = False  # when read from input file.
        self.start = None  # from input file
        self.completion = None
        self.Demand = demand
        self.simplanned = False
        self.status = None
        self.ProcessMachine = None
        self.orgStart = None 
        self.orgCompletion = None
        self.orgMachine = None
        self.orgStatus = None

    def setOriginalStart(self,myst):
        self.orgStart = myst
        return
    def getOriginalStart(self):
        return self.orgStart 

    def setOriginalCompletion(self,myst):
        self.orgCompletion = myst
        return
    def getOriginalCompletion(self):
        return self.orgCompletion

    def setOriginalMachine(self,myst):
        self.orgMachine = myst
        return
    def getOriginalMachine(self):
        return self.orgMachine 


    



    def setStatus(self,myst):
        self.status = myst
        return

    def setProcessMachine(self,mymach):
        self.ProcessMachine = mymach
        return 

    def getProcessMachine(self):
        return self.ProcessMachine 
         

    def getStatus(self):
        return self.status
    


    def setSimPlanned(self):
        self.simplanned = True
        return
    def isSimPlanned(self):
        return self.simplanned
          
    
    def getDemand(self):
        return self.Demand
    def getExecutionData(self):
        return self.ExecutionData

    def setStart(self,mystrt,sim):
        self.start = sim.getRealTime()
        return
        
    def setExecutionData(self,event,sim):

        if event != None: 
            try: 
                actual_comp = sim.getRealTime()
                actual_start = actual_comp - timedelta(minutes = sim.getTime()-self.getStart()) 
                self.completion = sim.getTime()
                
                myexecutedata = {"OperationName":self.getName(),"ProcessID":self.getID(),"ResourceID":event.getResource().getID(),"Resource":event.getResource().getName(),"Start":actual_start,"Completion":actual_comp,"DemandID":self.getDemand().getID(),"Product":self.getDemand().getFinalProduct().getPN(),"NrItems":self.getDemand().getQuantity()}
                self.getExecutionData().append(myexecutedata)
                self.Finished = True
                
            except Exception as e:
                sim.saveLog("ERROR in executiondata "+str(e))

                
        else: # cases "cancelled" or "finished", start and completion are already registered is operation in realtime.
            try: 
                if self.isCancelled():
                    myexecutedata = {"OperationName":self.getName(),"ProcessID":self.getID(),"ResourceID":"Cancelled","Resource":"Cancelled","Start":self.getStart(),"Completion":self.getCompletion(),"DemandID":self.getDemand().getID(),"Product":self.getDemand().getFinalProduct().getPN(),"NrItems":self.getDemand().getQuantity()}
                    self.getExecutionData().append(myexecutedata)
                else:
                    myexecutedata = {"OperationName":self.getName(),"ProcessID":self.getID(),"ResourceID":"-","Resource":"-","Start":self.getStart(),"Completion":self.getCompletion(),"DemandID":self.getDemand().getID(),"Product":self.getDemand().getFinalProduct().getPN(),"NrItems":self.getDemand().getQuantity()}
                    self.getExecutionData().append(myexecutedata)
            except Exception as e:
                sim.saveLog("ERROR in executiondata "+str(e))
            
        return 

        
    def setStart(self,mytime):
        self.start = mytime
        return
    def getStart(self):
        return self.start

    def setFinished(self):
        self.Finished = True
        return

    def isFinished(self):
        return self.Finished 

    def setName(self,nm):
        self.Name = nm
        return
        
    def getStart(self):
        return self.start
    
    def setCompletion(self,mytime):
        self.completion = mytime
        return
    def getCompletion(self):
        return self.completion

        

    def setCancelled(self):
        self.Cancelled = True
        return

    def isCancelled(self):
        return self.Cancelled 
        

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

        for opr in oprseq:
            if opr.isCancelled() or opr.isFinished() or opr.getName() == "Unknown":
                continue
            return opr
                
        return None

    def setProcessData(self,event,strt,opr,sim):

        if event != None: 

            try: 
                
                actual_comp = sim.getRealTime()
                actual_start = actual_comp - timedelta(minutes = sim.getTime()-strt)
    
 #{"ItemID":item.getID(),"Demand":item.getDemand().getID(),"Product":self.getFinalProduct().getPN(),"OperationName":oprseq[oprid].getName(),"ProcessID":-1,"ResourceID":-1,"Start":strt,"Completion":comp}               
                
                myprocessdata = {"ItemID":self.getID(),"Demand":self.getDemand().getID(),"Product":self.getDemand().getFinalProduct().getPN(),"OperationName":opr.getName(),"ProcessID":event.getID(),"ResourceID":event.getResource().getID(),"Resource":event.getResource().getName(),"Start":actual_start,"Completion":actual_comp}
                self.getProcessData().append(myprocessdata)
            except Exception as e:
                sim.saveLog("ERROR in processdata "+str(e))

        return 

    def setLocationData(self,event,sim):

        if event != None: 

            actual_comp = sim.getRealTime()

            locid = None; locname = None
            if event.getLocation() != None:
                if isinstance(event.getLocation(),tuple):
                    locid =  str(event.getLocation()[0].getID())+"->"+str(event.getLocation()[1].getID())
                    locname = event.getLocation()[0].getName()+"->"+event.getLocation()[1].getName()
                else:
                    locid =  event.getLocation().getID()
                    locname = event.getLocation().getName()
            else:
                sim.saveLog("ERROR in location is None of event "+event.getName()+"["+str(event.getID()))
            
            location_update = {"Entity":"Item","EntityID":self.getID(),"EventName":event.getName(),"EventID":event.getID(),"LocationID":locid,"LocationName":locname,"Time":actual_comp}   
                
            self.getLocationData().append(location_update)
          

        return 



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

    
        

