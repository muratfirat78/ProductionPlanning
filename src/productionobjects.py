from simulator import *
from datetime import timedelta,date
from productionalgs import *
from productionChecker import *


class Inventory(Resource):
    
    def __init__(self,mycap,myloc,sim,workmngr):
        super().__init__("Central_Inventory","Inventory",mycap,sim,workmngr)
        self.InputBuffer = Buffer("Input",None,1000000,sim,workmngr)
        self.OutputBuffer = Buffer("Output",None,1000000,sim,workmngr)
        self.setLocation(myloc)
        self.InputBuffer.setLocation(myloc)
        self.OutputBuffer.setLocation(myloc)


    def getInputBuffer(self):
        return self.InputBuffer 
    def getOutputBuffer(self):
        return self.OutputBuffer 
       
#_________________________________________________________________________
class Buffer(Resource):
    def __init__(self,buftype,mach,mycap,sim,workmngr):
       
        super().__init__((mach.getName() if mach != None else "Central")+"_"+buftype,"Buffer",mycap,sim,workmngr)
        self.BufferType = buftype
        self.machine = mach


    def getMachine(self):
        return self.machine
        
    def isInputType(self):   
        if self.BufferType == "Input":
            return True
        return False

 
    def addItem(self,myitem):     
        #print(" > "+str(self.getSimulator().getTime())+": adding item to "+self.getName())
        self.getItems().append(myitem)
        
        myitem.setLocation(self.getLocation())
        
        return
        
    def removeItem(self,myit):  
        self.getItems().remove(myit)  
        return

    def getUnreservedItems(self):
        return [i for i in self.getItems() if i.getReservedEvent() == None]
##########################################################################################################  
    def generateEvent(self,display):

        unreserved_items = [i for i in self.getItems() if i.getReservedEvent() == None]
        if display: 
            self.getSimulator().saveLog("REPORT: event generation at "+self.getName()+", items: "+(("["+str(self.getItems()[0].getID()) if len(self.getItems()) >0 else '')+"-"+(str(self.getItems()[-1].getID())+"]" if len(self.getItems())>0 else ''))+", unreserved items: "+(("["+str(self.getUnreservedItems()[0].getID()) if len(self.getUnreservedItems()) >0 else '')+"-"+(str(self.getUnreservedItems()[-1].getID())+"]" if len(self.getUnreservedItems())>0 else 'No unreserved items!')))
        
        if len(unreserved_items) == 0:
            if display: 
                self.getSimulator().saveLog("REPORT: Returning event generation at "+self.getName()+", items: "+str(len(self.getItems())))
                self.getSimulator().saveLog("REPORT: Returning event generation at "+self.getName()+", items: "+("["+str(self.getItems()[0].getID())+"-"+str(self.getItems()[-1].getID())+"]" if len(self.getItems())>0 else ''))
                self.getSimulator().saveLog("REPORT: Returning event generation at "+self.getName()+", items: "+(("["+str(self.getItems()[0].getID()) if len(self.getItems()) >0 else '')+"-"+(str(self.getItems()[-1].getID())+"]" if len(self.getItems())>0 else ''))+", unreserved items: "+(("["+str(self.getUnreservedItems()[0].getID()) if len(self.getUnreservedItems()) >0 else '')+"-"+(str(self.getUnreservedItems()[-1].getID())+"]" if len(self.getUnreservedItems())>0 else 'No unreserved items!')))
                                            
            return
        if (self.isInputType() and self.getMachine() == None):
            return

       
        event_type = "Machine Setup" if self.isInputType() else "Trailer Loading"
        generated_event = ExecEvent((None if self.isInputType() else self),None,self.getWorkMgr().getEventTypes()[event_type])        
        self.getSimulator().getEventQueue()["Pending"].append(generated_event)       

        if display: 
            self.getSimulator().saveLog("REPORT: In generating event "+self.getName()+"@"+self.getLocation().getName()+" output buffer? "+str(not self.isInputType())+", event: "+generated_event.getName()+"("+str(generated_event.getID())+"), unreserved items: "+str(len(unreserved_items)))

        # reserve items till selection
        for item in unreserved_items:
            item.setReservedEvent(generated_event) 
        
        generated_event.setEquipment(self.getMachine() if event_type == "Machine Setup" else None) 
              
        return
############################################################################################################        
    
#_______________________________________________________________________  
class Machine(Resource):
    
    def __init__(self,machcode,nrprocessors,myloc,myname,OprtingShifts,processtype,automated,mycap,Alternatives,Setup,OprtingEffort,sim,workmngr):
        super().__init__(myname,"Machine",mycap,sim,workmngr)
        self.InputBuffer = Buffer("Input",self,1000000,sim,workmngr)
        self.OutputBuffer = Buffer("Output",self,1000000,sim,workmngr)
        self.setLocation(myloc)
        self.InputBuffer.setLocation(myloc)
        self.OutputBuffer.setLocation(myloc)
        self.automated = automated
        self.ProcessType = processtype
        self.OperatingEffort = OprtingEffort
        self.AvailableShifts = OprtingShifts
        self.Alternatives = Alternatives
        self.MachineCode = machcode
        self.setuptime = Setup
    
        self.ProgressDict = dict() # key: processevent, val: (start,end), all in simtime
        self.ProcessMatch = dict() #key: processorid  val: processevent
        self.NoProcessors = nrprocessors
        self.suspendedEvent = None
        self.ProgressList = [] # [(event,(st,cp))]
        self.suspendedevents = dict() # key: event, val: processor
   

    
    def getSuspendedEvents(self):
        return self.suspendedevents

        
    def getProgressList(self):
        return self.ProgressList
    
    def getSuspendedEvent(self):
        return self.suspendedEvent
    def setSuspendedEvent(self,myev):
        self.suspendedEvent = myev
        return

    def getProcessor(self):

        used_pocessors = [p for p in self.ProcessMatch.values()]

        available_processors = [p for p in range(self.NoProcessors) if not p in used_pocessors]

        if len(available_processors) > 0:
            return available_processors[0]
                
        return None

    def getProcessMatch(self):
        return self.ProcessMatch
            
    def getNoProcessors(self):
        return self.NoProcessors


    def getSetupTime(self):
        return self.setuptime


    def getOperatingEffort(self):
        return self.OperatingEffort

    def getMachineCode(self):
        return self.MachineCode
        
    def getInputBuffer(self):
        return self.InputBuffer 
    def getOutputBuffer(self):
        return self.OutputBuffer 
    def IsAutomated(self):
        return self.automated

    def getAvailableShifts(self):
        return self.AvailableShifts

    def checkShiftChange(self,shift):
        self.Available = shift in self.getAvailableShifts()
        return

    def getAlternatives(self):
        return self.Alternatives

    def getNextAvailableTime(self):

        if not self.isAvailable(): 
            return None

        sim_time = self.getSimulator().getTime()
        
        if self.getProcessor() is not None:
            return sim_time

        # All processors busy: check when the earliest active step finishes
        active_ends = []
        for _, pr in self.ProgressList:
            end_time = pr[1] if isinstance(pr, (tuple, list)) else pr #check if pr is a tuple/list (start, end) or just an end time
            if end_time >= sim_time: #filter out any already completed steps
                active_ends.append(end_time)
        return min(active_ends) if active_ends else sim_time
        

    def calculationUtilization(self):

        # machine processing events


        return 
        
#___________________________________________________________________________________________
class Operator(Resource):
    
    def __init__(self,myname,avshifts,mycap,sim,workmngr):
        super().__init__(myname,"Operator",mycap,sim,workmngr)
        self.AvailableShifts = avshifts
     


    def getAvailableShifts(self):
        return self.AvailableShifts

    def checkShiftChange(self,shift):
        if not shift in self.getAvailableShifts():
            self.Status = "Unavailable"
        else:
            self.Status = "Idle" # assuming that an operator only works in one shift during the day.
            
        return

#_________________________________________________________________________________________
class Trailer(Resource):
    def __init__(self,mycap,sim,workmngr):
        super().__init__(None,"Trailer",mycap,sim,workmngr)  
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
    def __init__(self,demand,name,myid,proctime,processtimedist):
        super().__init__(demand,name,myid,processtimedist)
        
        self.getRandVar().getSampling().append(proctime) 
        
#_______________________________________________________________________          
class Product(DemandType):
    def __init__(self,pn,myid,name):
        super().__init__(pn,myid,name)
        self.OperationSequences = dict() #key: Order_ID, val: [Operations]
       

    def getOperationSequences(self):
        return self.OperationSequences
#_______________________________________________________________________  
class ProductionOrder(Demand):
    def __init__(self,ddline,myid,demtype,quantity):
        super().__init__(ddline,myid,demtype,quantity)
       
     
    def getFinalProduct(self):
        return self.getDemandType() #converting terminology

    def printOrder(self):

   
        return "Order "+self.getFinalProduct().getPN()+", Q: "+str(self.getQuantity())+", d: "+str(self.getDeadline())+", oprs: "+str([o.getName()+"("+str(o.getRandVar().sampleValue())+")" for o in self.getFinalProduct().getOperationSequences()[self.getID()]])

   
