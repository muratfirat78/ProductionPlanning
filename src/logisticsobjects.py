from simulator import *
from datetime import timedelta,date
from productionalgs import *



class Inventory(Resource):
    
    def __init__(self,mycap,myloc,sim,workmngr):
        super().__init__("Central_Inventory",workmngr.giveResouceID(),"Inventory",mycap,sim,workmngr,None)
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
       
        super().__init__((mach.getName() if mach != None else "Central")+"_"+buftype,workmngr.giveResouceID(),"Buffer",mycap,sim,workmngr,None)
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
class Schedule(object):
    def __init__(self,datadate,constructiondate,algname,data_df,workmgr):

        self.DataExportDate = datadate
        self.ConstuctionDate = constructiondate
        self.AlgorithmName = algname
        self.DataFrame = data_df

        workmgr.getSimulator().saveLog("REPORT: Constructing schedule: "+str(algname)+", cons date"+str(constructiondate))
      
        self.KPIDict = dict()
        self.ShipmentBatches = dict() # batchid, batch obj
        self.ShiftSchedules = dict() #key: day, val: dict: key: shiftno, val: dict: key: machine, val: dataframe

        self.shiftsinfo = {3: [x for x in range(8)],1:[x for x in range(8,17)],2:[x for x in range(18,24)]}

        self.KPIDict["Completion"] = dict()  # key: shipmentbatch, val: TRUE/FALSE
     
        self.MinDate = None
        self.MaxDate = None
        self.MyWeeks = []
        self.MyDays = []


        #self.MaxDate =machines_df["Work Orders/End"].max()
        #self.MinDate =machines_df["Work Orders/Start"].min()

        #self.MinDate = self.MinDate.replace(hour=0, minute=0, second=0, microsecond=0)

        try:
            currentday = self.MinDate
            while currentday <= self.MaxDate:
                if currentday.weekday() < 5:
                    self.MyDays.append(currentday)
                if currentday.weekday() == 0:
                    self.MyWeeks.append(currentday)
                currentday = currentday+timedelta(minutes = 24*60)
        except Exception as e:
            workmgr.getSimulator().saveLog("ERROR: In finding weeks "+str(e))

    def getMyWeeks(self):
        return self.MyWeeks
    def getMyDays(self):
        return self.MyDays


    def getShiftsInfo(self):
        return self.shiftsinfo
        
    def getShiftSchedules(self):
        return self.ShiftSchedules

    def getMinDate(self):
        return self.MinDate
       
    def getMaxDate(self):
        return self.MaxDate  
        
    def getCompletedDemands(self):

        return sum([int(completed) for d,completed in self.KPIDict["Completion"].items()])
       
        
    def calculateKPIs(self):

        #no tardy orders
        
        return 

    def getDemands(self):
        return self.Demands

    def getDemandOperations(self):
        return self.DemandOperations

    def getKPIs(self):
        return self.KPIDict
            

    def getDataExportDate(self):
        return self.DataExportDate 
    def getConstuctionDate(self):
        return self.ConstuctionDate 

    def getAlgorithmName(self):
        return self.AlgorithmName
    def getDataFrame(self):
        return self.DataFrame


class SMConveyor(Resource):
    def __init__(self,mach,sim,workmngr):
        super().__init__(mach.getName()+"_Conveyor",workmngr.giveResouceID(),"Conveyor",sim,workmngr,None)
        self.machine = mach

    def getMachine(self):
        return self.machine

        
#_______________________________________________________________________  
class Machine(Resource): # sorting machine
    
    def __init__(self,machcode,myid,myloc,myname,OprtingShifts,automated,mycap,Setup,sim,workmngr):
        super().__init__(myname,myid,"Machine",mycap,sim,workmngr,OprtingShifts)
        
        self.InputBuffer = Buffer("Input",self,1000000,sim,workmngr)
        self.OutputBuffer = Buffer("Output",self,1000000,sim,workmngr)
        self.setLocation(myloc)
        myloc.getResources().append(self)
        self.InputBuffer.setLocation(myloc)
        self.OutputBuffer.setLocation(myloc)
        self.automated = automated
        self.MachineCode = machcode
        self.setuptime = Setup
    
     

    def getSetupTime(self):
        return self.setuptime

    def getMachineCode(self):
        return self.MachineCode
        
    def getInputBuffer(self):
        return self.InputBuffer 
    def getOutputBuffer(self):
        return self.OutputBuffer 
    def IsAutomated(self):
        return self.automated


    def checkShiftChange(self,shift):
        self.Available = shift in self.getAvailableShifts()
        return

    def getAlternatives(self):
        return self.Alternatives

   
#___________________________________________________________________________________________
class Operator(Resource):
    
    def __init__(self,myname,avshifts,mycap,sim,workmngr):
        super().__init__(myname,workmngr.giveResouceID(),"Operator",mycap,sim,workmngr,avshifts)
        
     
    def checkShiftChange(self,shift):
        if not shift in self.getAvailableShifts():
            self.Status = "Unavailable"
        else:
            self.Status = "Idle" # assuming that an operator only works in one shift during the day.
            
        return

#_________________________________________________________________________________________
class Container(Resource):
    def __init__(self,mycap,sim,workmngr):
        super().__init__(None,workmngr.giveResouceID(),"Container",mycap,sim,workmngr,None)  
        self.location = None
        self.capacity = mycap
        self.items = []

    def getLocation(self):
        return self.location

    def getCapacity(self):
        return self.capacity

    def getItems(self):
        return self.items

   
#_________________________________________________________________________________________
class PalletJack(Resource):
    def __init__(self,myname,myid,mycap,sim,workmngr):
        super().__init__(myname,myid,"PalletJack",mycap,sim,workmngr,None)  
        self.location = None
    def getLocation(self):
        return self.location
#############################################################################################
class Forklift(Resource):
    def __init__(self,myname,myid,mycap,sim,workmngr):
        super().__init__(myname,myid,"Forklift",mycap,sim,workmngr,None)  
        self.location = None
        self.destination = None
    
    def setDestination(self,mydest):
        self.destination = mydest
        return
    def getDestination(self):
        return self.destination
#______________________________________________________________________       
class Operation(Process):
    def __init__(self,demand,name,myid,proctime,processtimedist,order):
        super().__init__(demand,name,myid,processtimedist)
        self.SequenceOrder = order
        
        self.getRandVar().getSampling().append(proctime) 


    def getSequenceOrder(self):
        return self.SequenceOrder
#_______________________________________________________________________          
class Shipment(DemandType):
    def __init__(self,mytype,myweight,mydestination,myid):
        super().__init__(None,myid,"Shipment_"+str(myid))

        self.type = mytype
        self.myweight = myweight
        self.mydestination = mydestination

    def getType(self):
        return self.type

    def getWeight(self): 
        return self.myweight 

    def getDestination(self):
        return self.mydestination 
     
#_______________________________________________________________________  
class ShipmentBatch(Demand):
    def __init__(self,myid):
        super().__init__(None,myid,"DemandBatch",None)

        self.Shipments = []

    def getShipments(self):
        return self.Shipments
     
       


   
