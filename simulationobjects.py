from datetime import timedelta,date
import random
import pandas as pd
from stochastic import *




class Layout(object):
    def __init__(self,usecasename):
        self.Locations = []

    def getLocations(self):
        return self.Locations
        
    def getDistance(self,fromloc,toloc):
        return 1


class Location():
    def __init__(self,locname,locid):
        self.name = locname
        self.resources = []
        self.id = locid

        
    def getResources(self):
        return self.resources
    def getName(self):
        return self.name
    def getID(self):
        return self.id
        

class SimEvent(object):
    def __init__(self,sim,myname,mytype,restype,equiptype,preemptable):
        self.Name = myname
        self.type = mytype
        self.ResourceType = restype # to help assigning 
        self.EquipmentType = equiptype # to help selecting        
        self.precendenceDict = dict() #key: successor event name, val: properties directly transformed to successor event
        self.decisionsDict = dict() #key: progress case name, val: list of decision names
        self.successorDict = dict() #key: successor, val: preceence type, e.g. "Finish to Start" or "Simultaneous Start" or "Simultaneous Finish" 
        self.predecessorDict = dict() #key: predecessor, val: preceence type, e.g. "Finish to Start" or "Simultaneous Start" or "Simultaneous Finish"   
        self.preemptable = preemptable
        self.Simulator = sim
        
        
    def getSimulator(self):
        return self.Simulator

    def getType(self):
        return self.type # this can be "transport", "loading","unloading","process","logistical"

    def generateEvent(self):
        return

    def isPreemptable(self):
        return self.preemptable  

    def getDecisionsDict(self):
        return self.decisionsDict

    def getPrecendenceDict(self):
        return self.precendenceDict

    def getSuccessorDict(self):
        return self.successorDict

    def getPredecessorDict(self):
        return self.predecessorDict
        
    def getName(self):
        return self.Name

    def getResourceType(self):
        return self.ResourceType
   
    def getEquipmentType(self):
        return self.EquipmentType

############################################################################################################################
class ExecEvent(object):
    def __init__(self,fromloc,toloc,eventype):
        self.EventType = eventype    
        self.ID = eventype.getSimulator().getEventNo()   
        self.FromLocation = fromloc  
        self.ToLocation = toloc  
        self.ProcessTime = None
        self.StartTime = None  
        self.CompletionTime = None
        self.active = False    
        self.Operation = None
        self.Resource = None 
        self.Equipment = None
        self.Items = []
        self.successor = None
        self.predecessor = None
        self.ProgressList = [] #[(resource,(start,end))]
        self.status = "Pending"
        self.Place = None
        self.suspendedpredecessor = None
        self.suspendedsuccessor = None
        

        self.startdelay = 0
        self.logisticalevents = []

       #            Event  -  From       -   To           Equip        Resource    Event-loc         Equuipment Loc    Resource Loc
       #(OprMove)-> TL       OutputBuffer    Trailer        Trailer     Operator     From-loc           From-loc         From-loc 

    
       #            TT       OutputBuffer   InputBuffer     Trailer     Operator     Equipment          Equipment        Equipment

    
       #             TU        Trailer       InputBuffer     Trailer     Operator     To-loc             To-loc           To-loc

    
       # (OprMove)-> MS       InputBuffer      ---           Machine     Operator     From-loc            -----           From-loc
       # (OprMove)-> ML       InputBuffer     Machine        Machine     Operator     From-loc      	 From-loc         From-loc
       #             PROC       Machine        ---           Machine      ------        --------        ----------       ---------- 


    
       # (OprMove)-> MU         Machine      OutputBuffer    Machine     Operator     To-loc             To-loc           To-loc
  

    def setSuspendedSuccessor(self,succssr):
        self.suspendedsuccessor = succssr
        return

    def getSuspendedSuccessor(self):
        return self.suspendedsuccessor



    def getLocation(self):
        
        if self.getName() == "Trailer Transport":
            return self.getEquipment()
            
        if self.getName() == "Operator Move" or self.getName() == "Bring Equipment":
            return self.getToLocation()
        
        if self.getName() == "Trailer Unloading" or self.getName() == "Machine Unloading":
            return self.getToLocation().getLocation()

        # "Trailer Loading","Machine Setup","Machine Loading","Machine Processing"
        return self.getFromLocation().getLocation()

    def setSuspendedPredecessor(self,pr):
        self.suspendedpredecessor = pr
        return

    def getSuspendedPredecessor(self):
        return self.suspendedpredecessor 
        

    def setPlace(self,pl):
        self.Place = pl
        return
    def getPlace(self):
        return self.Place
        
    def getStatus(self):
        return self.status

    ######################################################################################
    def sampleProcessTime(self,workmgr):

        #workmgr.getSimulator().saveLog("REPORT: sample process time. "+str(self.getName())+", fl?: "+str(self.getFromLocation() == None)+", tl?: "+str(self.getToLocation()== None))

        
        if self.getName() == "Machine Setup":
            self.ProcessTime = self.getFromLocation().getMachine().getSetupTime()
        if self.getName() == "Machine Loading":
            self.ProcessTime = max(1,int(0.5*self.getFromLocation().getMachine().getOperatingEffort()*self.getItems()[0].getActiveOperation().getRandVar().sampleValue()))

        if self.getName() == "Machine Unloading":
            if not self.getFromLocation().IsAutomated():
                self.ProcessTime = max(1,int(0.5*self.getEquipment().getOperatingEffort()*self.getItems()[0].getActiveOperation().getRandVar().sampleValue()))


        if self.getName() == "Machine Processing":   
            self.ProcessTime = self.getItems()[0].getActiveOperation().getRandVar().sampleValue()

        if self.getName() in ["Trailer Loading","Trailer Unloading"]:
            self.ProcessTime = 1

        
        if self.getName() == "Trailer Transport" or self.getName() == "Operator Move" or self.getName() == "Bring Equipment":
            #workmgr.getSimulator().saveLog("REPORT: sample process time. "+str(self.getName())+", fl: "+str(self.getFromLocation().getName())+", tl: "+str(self.getToLocation().getName()))
            self.ProcessTime = workmgr.getLayout().getDistance(self.getFromLocation(),self.getToLocation())
        

        return
    #######################################################################################
   
        
    def setStatus(self,st):
        self.status = st

    def getLogisticalEvents(self):
        return self.logisticalevents
    def getStartDelay(self):
        return self.startdelay

    def increaseStartDelay(self):
        self.startdelay+=1
        return 
        
    def getProgressList(self):
        return self.ProgressList
        
    def setProcessTime(self,mytime):
        self.ProcessTime = mytime
        return

    def setCompletionTime(self,mytime):
        self.CompletionTime = mytime
        return

    def getCompletionTime(self):
        return self.CompletionTime    
   
   

    def getTotalProgress(self):
        return sum([(x[1][1] - x[1][0]) for x in self.getProgressList()])
 
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
        return
        
    def getProcessTime(self):
        return self.ProcessTime 

    def getFromLocation(self):
        return self.FromLocation
    
    def setFromLocation(self,myloc):
        self.FromLocation = myloc
        return 

    
    def getToLocation(self):
        return self.ToLocation
    
    def setToLocation(self,myloc):
        self.ToLocation = myloc
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

    def setCompletionTime(self,mystrt):
        self.CompletionTime = mystrt
    def getCompletionTime(self):
        return self.CompletionTime 

    def getName(self):
        return self.getEventType().getName()

    def getType(self):
        return self.getEventType().getType()
        
        
##################################################################################################################################      



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

    
        

