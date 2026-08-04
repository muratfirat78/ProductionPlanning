from Simulator import *
from datetime import timedelta,date
from productionalgs import *
from productionChecker import *


class Inventory(Resource):
    
    def __init__(self,mycap,myloc,sim,workmngr):
        super().__init__("Central_Inventory","Inventory",mycap,sim,workmngr)
        self.InputBuffer = Buffer("Input",None,1000,sim,workmngr)
        self.OutputBuffer = Buffer("Output",None,1000,sim,workmngr)
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
        #print(" > "+str(self.getSimulator().getTime())+": adding item to "+self.getName())
        self.getItems().append(myitem)
        self.generateEvent()
        myitem.setLocation(self.getLocation())
        
        return
        
    def removeItem(self,myit):  
        self.getItems().remove(myit)  
        return

    def getUnreservedItems(self):
        return [i for i in self.getItems() if i.getReservedEvent()== None]
##########################################################################################################  
    def generateEvent(self):
        
        if len(self.getUnreservedItems()) == 0 or self.getPendingEvent() != None:
            #self.getSimulator().saveLog("REPORT: Returning event generation at "+self.getName()+", items "+str(len(self.getItems()))+" unreserved items "+str(len(self.getUnreservedItems()))+", pend_ev none?  "+str(self.getPendingEvent() == None))
            if self.getPendingEvent() != None:
                self.getSimulator().saveLog(" pending event "+self.getPendingEvent().getName())
            return

        #self.getSimulator().saveLog("In generating event "+self.getName()+"@ loc none?"+str(self.getLocation() == None)+" output buffer? "+str(not self.isInputType()))
       
        
        #self.getSimulator().saveLog("In generating event "+self.getName()+"@"+self.getLocation().getName()+" output buffer? "+str(not self.isInputType()))
        
        if not self.isInputType(): #output buffer
            tl_event = ExecEvent(self,None,self.getWorkMgr().getEventTypes()["Trailer Loading"])        
            self.getSimulator().getEventQueue()["Pending"].append(tl_event)       
            tl_event.setPlace(self)
            self.setPendingEvent(tl_event)  
            self.getSimulator().saveLog("REPORT: Trailer loading from loc: "+str(self.getName()))
        else: # input buffer
            if self.getMachine() != None:
                event_name = "Machine Setup"; decision_type = 'Select Items'
                ms_event = ExecEvent(self,None,self.getWorkMgr().getEventTypes()[event_name])

                algname = self.getWorkMgr().getAlgorithmSetting()["Machine Setup"][decision_type]
                self.getSimulator().saveLog("REPORT: in generating.. finding items of event "+event_name+", algname: "+algname)
                algfunction = self.getWorkMgr().getProductionAlgManager().getDecisionAlgorithms()[decision_type][algname]
                alg_return = algfunction(ms_event)

                if alg_return!= None:
                    self.getSimulator().getEventQueue()["Pending"].append(ms_event) # for resource and equipment
                    ms_event.setEquipment(self.getMachine()) 
                    ms_event.setPlace(self)

                    for item in alg_return:
                        ms_event.getItems().append(item)
                        item.setReservedEvent(ms_event) 
                        #self.getSimulator().saveLog("REPORT: event item reservation set: "+str(ms_event.getName())+", it: "+str(item.getID()))   
      
                    if self.getMachine().getName() != "OUT - Outsourced activity_(OUT - Outsourced)":
                        self.setPendingEvent(ms_event)
                    else:
                        self.getSimulator().saveLog("REPORT: "+ms_event.getName()+"("+str(ms_event.getID())+")"+" generated at "+self.getName()+", pendings "+str(len(self.getSimulator().getEventQueue()["Pending"])))
                
            
        if self.getPendingEvent()!= None: 
            self.getSimulator().saveLog("REPORT: "+self.getPendingEvent().getName()+" generated, pendings "+str(len(self.getSimulator().getEventQueue()["Pending"])))

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

    def removeItem(self,myit):
        print(" > "+str(self.getSimulator().getTime())+": "+self.getName()," item removed, input buffer is triggered for loading ",len(self.getInputBuffer().getItems()))
        self.getItems().remove(myit)
        if len(self.getItems()) == 0 and len(self.getInputBuffer().getItems()) > 0:
            self.getInputBuffer().generateEvent()
        return

    def getAvailableShifts(self):
        return self.AvailableShifts

    def checkShiftChange(self,shift):
        self.Available = shift in self.getAvailableShifts()
        return

    def getAlternatives(self):
        return self.Alternatives
        
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

   
        return "Order "+self.getFinalProduct().getPN()+", Q: "+str(self.getQuantity())+", d: "+str(self.getDeadline())+", oprs: "+str([o.getName() for o in self.getFinalProduct().getOperationSequences()[self.getID()]])

   
