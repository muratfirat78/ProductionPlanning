from simulator import *
from datetime import timedelta,date
from productionalgs import *
from productionChecker import *


class Inventory(Resource):
    
    def __init__(self,mycap,myloc,sim,workmngr):
        super().__init__("Central_Inventory","Inventory",mycap,sim,workmngr,None)
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
       
        super().__init__((mach.getName() if mach != None else "Central")+"_"+buftype,"Buffer",mycap,sim,workmngr,None)
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
       
        if "Work Orders/Start" in self.DataFrame.columns: 
            workmgr.getSimulator().saveLog("REPORT: Work Orders/Start column made datetime ")
            self.DataFrame["Work Orders/Start"] = pd.to_datetime(self.DataFrame["Work Orders/Start"], format="%Y-%m-%d %H:%M:%S")
        if "Work Orders/End" in self.DataFrame.columns:        
            workmgr.getSimulator().saveLog("REPORT: Work Orders/End column made datetime ")
            self.DataFrame["Work Orders/End"] = pd.to_datetime(self.DataFrame["Work Orders/End"], format="%Y-%m-%d %H:%M:%S")
        if "Deadline" in self.DataFrame.columns:     
            workmgr.getSimulator().saveLog("REPORT: Deadline column made datetime ")
            self.DataFrame["Deadline"] = pd.to_datetime(self.DataFrame["Deadline"], format="%Y-%m-%d %H:%M:%S")

        
        self.KPIDict = dict()
        self.Demands = dict() # demandid, demand obj
        self.DemandOperations = dict() #demandid, (operation,(res,(start,end))))
        self.ShiftSchedules = dict() #key: day, val: dict: key: shiftno, val: dict: key: machine, val: dataframe

        self.shiftsinfo = {3: [x for x in range(8)],1:[x for x in range(8,17)],2:[x for x in range(18,24)]}

        self.KPIDict["Tardiness"] = dict()  # key: demandid, val: TRUE/FALSE
        self.KPIDict["Completion"] = dict()  # key: demandid, val: TRUE/FALSE
        self.MinDate = None
        self.MaxDate = None
        self.MyWeeks = []
        self.MyDays = []

        machines_df = self.DataFrame[(self.DataFrame["Processing Machine"] != "-") & (self.DataFrame["Processing Machine"] != "OUT - Outsourced activity_(OUT - Outsourced)")]

        self.MaxDate =machines_df["Work Orders/End"].max()
        self.MinDate =machines_df["Work Orders/Start"].min()

        self.MinDate = self.MinDate.replace(hour=0, minute=0, second=0, microsecond=0)

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

            

        try:
            demands_df = self.DataFrame.groupby(["ID","Product","Product/ID","Quantity To Produce","Deadline","Reference"])[['Work Orders/Work Center','Work Orders/Work Center/ID','Processing Machine','Work Orders/Operation','Operation Order','Work Orders/Expected Duration','Work Orders/Start','Work Orders/End','Work Orders/Status']].agg(lambda x:list(x)).reset_index()
    

            
            for i,r in demands_df.iterrows():
            
                if r['ID'] in workmgr.getProductionOrders(): 
                    self.Demands[r['ID']] = workmgr.getProductionOrders()[r['ID']]
                    
                    opr_seq = self.Demands[r['ID']].getFinalProduct().getOperationSequences()[self.Demands[r['ID']].getID()]
                    self.DemandOperations[r['ID']] = dict()
                    curr_scheduled = False; order_comp = None
                   
                    for oprind in range(len(opr_seq)):
                        
                        if r['Work Orders/Status'][oprind] == "Scheduled":
                            
                            myopr = opr_seq[oprind]
                            curr_scheduled = True 
                            oprname = r['Work Orders/Operation'][oprind]
                            opr_start = r['Work Orders/Start'][oprind]
                            opr_completion = str(r['Work Orders/End'][oprind])
                            opr_machine =  r['Processing Machine'][oprind]
                            self.DemandOperations[r['ID']][myopr] = (opr_machine,(opr_start,opr_completion))
                            order_comp = r['Work Orders/End'][oprind]
                            
                        else:
                            order_comp = None; curr_scheduled = False

                    if curr_scheduled:
                        self.KPIDict["Tardiness"][r['ID']] = self.Demands[r['ID']].getDeadline() < order_comp
                        self.KPIDict["Completion"][r['ID']] =  True
                    else:
                        self.KPIDict["Completion"][r['ID']] =  False
 
                else:
                    workmgr.getSimulator().saveLog("ERROR: demand not found for ID "+str(r['ID']))


         
        except Exception as e:
            workmgr.getSimulator().saveLog("ERROR: In schedule reading.... "+str(e))

###############################################################################################################
    def getMyWeeks(self):
        return self.MyWeeks
    def getMyDays(self):
        return self.MyDays
        
    def findMachineShift(self,day,workmgr):

        try: 
            machines_df = self.DataFrame[(self.DataFrame["Processing Machine"] != "-") & (self.DataFrame["Processing Machine"] != "OUT - Outsourced activity_(OUT - Outsourced)")]
    
            currentday = day.replace(hour=0, minute=0, second=0, microsecond=0)

            if currentday < self.getMinDate() or currentday > self.getMaxDate():
                workmgr.getSimulator().saveLog("REPORT: schedule requested day "+str(currentday)+" not in schedule, min date: "+str(self.MinDate)+", max date: "+str(self.MaxDate)) 
                return None

            workmgr.getSimulator().saveLog("REPORT: schedule requested day "+str(currentday)+" in schedule? "+str(currentday in self.getShiftSchedules())) 
            if not currentday in self.getShiftSchedules():
    
                self.getShiftSchedules()[currentday] = dict()
    
                machines = dict()  # name, obj
                
                for res in workmgr.getResources():
                    if res.getType() == "Machine" and res.getProcessType() == "Metal forming":
                        machines[res.getName()] = res
    
                for shftno,shfthours in self.getShiftsInfo().items():
                    shiftstart = currentday+timedelta(minutes = shfthours[0]*60);
                    shiftend = currentday+timedelta(minutes = shfthours[-1]*60+59)

                    
                    self.getShiftSchedules()[currentday][shftno] = dict()
                    for machname,mach in machines.items():
                        if shftno == 3:
                            if not mach.IsAutomated():
                                continue
                        machine_df = machines_df[machines_df["Processing Machine"] == machname]
                        mach_shift_df = machine_df[(machine_df["Work Orders/End"] >=  pd.Timestamp(shiftstart)) & (machine_df["Work Orders/Start"] <= pd.Timestamp(shiftend))]
                        
                        self.getShiftSchedules()[currentday][shftno][mach] = mach_shift_df

            return self.getShiftSchedules()[currentday]
                    
        except Exception as e:
            workmgr.getSimulator().saveLog("ERROR: In finding shift schedules of machines for day "+str(currentday)+" -> "+str(e))
        
       

        return None
################################################################################################################    

##############################################################################################################

    def getShiftsInfo(self):
        return self.shiftsinfo
        
    def getShiftSchedules(self):
        return self.ShiftSchedules

    def getMinDate(self):
        return self.MinDate
       
    def getMaxDate(self):
        return self.MaxDate  
        
    def getTardyDemands(self):

        return sum([int(tardy) for d,tardy in self.KPIDict["Tardiness"].items()])

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


        
#_______________________________________________________________________  
class Machine(Resource):
    
    def __init__(self,machcode,nrprocessors,myloc,myname,OprtingShifts,processtype,automated,mycap,Alternatives,Setup,OprtingEffort,sim,workmngr):
        super().__init__(myname,"Machine",mycap,sim,workmngr,OprtingShifts)
        self.InputBuffer = Buffer("Input",self,1000000,sim,workmngr)
        self.OutputBuffer = Buffer("Output",self,1000000,sim,workmngr)
        self.setLocation(myloc)
        self.InputBuffer.setLocation(myloc)
        self.OutputBuffer.setLocation(myloc)
        self.automated = automated
        self.ProcessType = processtype
        self.OperatingEffort = OprtingEffort
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


    def checkShiftChange(self,shift):
        self.Available = shift in self.getAvailableShifts()
        return

    def getAlternatives(self):
        return self.Alternatives

    def getNextAvailableTime(self):

        if not self.isAvailable(): 
            return None

        sim_time = self.getSimulator().getTime()
        
        if self.getProcessor() != None:
            return sim_time

        # All processors busy: check when the earliest active step finishes
        remaining_times = []
        for event,processor in self.getProcessMatch().items():

            # (mach1,(480,960)),(mach1,(1440,1700)), current time: 1600
            actual_progress = 0 
            for progrtuple in event.getProgressList():
                if progrtuple[1][1] < self.getSimulator().getTime():
                    actual_progress+= progrtuple[1][1]-progrtuple[1][0]
                else:
                    actual_progress+= self.getSimulator().getTime()-progrtuple[1][0]
                
            remaining_time = event.getProcessTime() - actual_progress
            remaining_times.append(remaining_time)

   
        return min(remaining_times)+sim_time
        

    def calculationUtilization(self):

        # machine processing events


        return 
        
#___________________________________________________________________________________________
class Operator(Resource):
    
    def __init__(self,myname,avshifts,mycap,sim,workmngr):
        super().__init__(myname,"Operator",mycap,sim,workmngr,avshifts)
        
     
    def checkShiftChange(self,shift):
        if not shift in self.getAvailableShifts():
            self.Status = "Unavailable"
        else:
            self.Status = "Idle" # assuming that an operator only works in one shift during the day.
            
        return

#_________________________________________________________________________________________
class Trailer(Resource):
    def __init__(self,mycap,sim,workmngr):
        super().__init__(None,"Trailer",mycap,sim,workmngr,None)  
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
    def __init__(self,demand,name,myid,proctime,processtimedist,order):
        super().__init__(demand,name,myid,processtimedist)
        self.SequenceOrder = order
        
        self.getRandVar().getSampling().append(proctime) 


    def getSequenceOrder(self):
        return self.SequenceOrder
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

        self.SimExecutionData = []
       
     
    def getFinalProduct(self):
        return self.getDemandType() #converting terminology

    def getSimExecData(self):
        return self.SimExecutionData

    def printOrder(self):

   
        return "Order "+self.getFinalProduct().getPN()+", Q: "+str(self.getQuantity())+", d: "+str(self.getDeadline())+", oprs: "+str([o.getName()+"("+str(o.getRandVar().sampleValue())+")" for o in self.getFinalProduct().getOperationSequences()[self.getID()]])

   
