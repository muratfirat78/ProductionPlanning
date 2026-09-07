from datetime import timedelta,date,datetime
from simulationobjects import *
import random
import pandas as pd
import os 
from timeit import default_timer as timer
from pathlib import Path
import logging


class SimulatorLogHandler(logging.Handler):
    """Store simulation records and forward visible records to the dashboard."""

    def __init__(self, simulator):
        super().__init__()
        self.simulator = simulator
        self._productionplanning_simulator_handler = True

    def emit(self, record):
        message = self.format(record)
        simulation_time = self.simulator.getTime()

        if simulation_time not in self.simulator.MyLog:
            self.simulator.MyLog[simulation_time] = []
        self.simulator.MyLog[simulation_time].append(message)

        if record.levelno >= logging.ERROR:
            self.simulator.Errors.append(str(simulation_time) + ": " + message)
            self.simulator.addError()

        if record.levelno >= logging.INFO and self.simulator.LogDisplay is not None:
            self.simulator.LogDisplay(
                str(simulation_time) + "[" + str(self.simulator.getRealTime()) + "]: " + message
            )


class Simulator(object):
    def __init__(self):
        
        self.EventData = [] # [{"EventID':...,"EventName":...,'Location Name/ID':...,"Equipment Name/ID":...,"Resource Name/ID":...,"Items":...}]
        self.ExecutionData = [] # [{"EventID':...,"EventName":...,'Status':...}]
        self.LocationData = [] 
        self.BufferData = [] 
        self.queue = {} #key: time (start/completion times of events) , val: [event]
        self.time = 0
        self.eventno = 0
     
        self.queue["Pending"] = [] # list of pending events, to be hanlded
    
        self.DataTypes = dict() # key: dataset name, val: dataframe objects. 
        self.startday = None 
        self.shiftmapping = {0:3,8:1,16:2}
        self.shiftlength = timedelta(hours = 7)+ timedelta(minutes = 59)
        self.currentDay = None # will be updated dynamically
        self.currentShift = None #will be updated dynamically 

        currentdate =  datetime.now()
        startday = datetime(currentdate.year, currentdate.month, currentdate.day)
        self.shifthours = 8 
        self.shiftsperday = 3 
        self.weekdays = 5
        self.shift_minutes = 60*self.shifthours
        self.TimeLimit =  None
        self.MyLog = dict() #key: sim time, val: [events]
        self.Controller = None
        self.RunErrors = 0
        self.Errors = []
        self.LogDisplay = None
        self.logger = logging.getLogger("productionplanning")
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False

        for handler in self.logger.handlers[:]:
            if getattr(handler, "_productionplanning_simulator_handler", False):
                self.logger.removeHandler(handler)

        handler = SimulatorLogHandler(self)
        handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        self.logger.addHandler(handler)

        self.setStartDay(startday+timedelta(hours= 24))

        print("Start day: ",self.getStartDay().date()," weekday: ",self.getStartDay().weekday(), " day: ",self.getStartDay().strftime("%A"),", TimeLimit: ",self.TimeLimit)

    def getErrors(self):
        return self.Errors 
        

    def addError(self):
        self.RunErrors+=1
        return
        
    def getNoErrors(self):
        return self.RunErrors
        
    def setController(self,contr):
        self.Controller = contr
        return
    def getController(self):
        return self.Controller
        
    def getMyLog(self):
        return self.MyLog

    def setLogDisplay(self, callback):
        self.LogDisplay = callback
        return

    def saveLog(self,info):
        """Compatibility wrapper for legacy logging; new code should use module loggers."""
        if "ERROR" in info:
            self.logger.error(info)
        elif "REPORT" in info:
            self.logger.info(info)
        else:
            self.logger.debug(info)
        return
        
    def saveTitleLog(self,title,info):
        
        if not title in self.MyLog:
            self.MyLog[title] = []
        self.MyLog[title].append(info)
        return
        
    def setRunWeeks(self,weeks):
        self.TimeLimit =  weeks*60*self.shifthours*self.shiftsperday*self.weekdays

        return

    def getTimelimit(self):
        return self.TimeLimit

        

    def getShiftMinutes(self):
        return self.shift_minutes

    def getShift(self,hour):
        if hour in self.shiftmapping:
            return self.shiftmapping[hour]
        else:
            return 0
        
    def setStartDay(self,myday):
        self.startday = myday
        return
    def getStartDay(self):
        return self.startday

    def setCurrentShift(self,shft):
        self.currentShift = shft
        return 
    def getCurrentShift(self):
        return self.currentShift

    def getShiftSimTime(self,simtime):
        return self.getShift(self.checkRealTime(simtime).hour)

    def setCurrentDay(self,day):
        self.currentDay = day
        return
        
    def getCurrentDay(self):
        return self.currentDay 

    def getDataTypes(self):
        return self.DataTypes

    def getEventData(self):
        return self.EventData
    def getExecutionData(self):
        return self.ExecutionData

    def getLocationData(self):
        return self.LocationData

    def getBufferData(self):
        return self.BufferData
          
    def getTimeLimit(self):
        return self.TimeLimit

    def getRealTime(self):
        return self.getStartDay()+timedelta(minutes = self.getTime())

    def checkRealTime(self,time):
        return self.getStartDay()+timedelta(minutes = time)

############################################################################################
    def RunSimulation(self,OperationsMgr): 

        try: 
            self.getController().getVisualManager().updateSimProgress("------------ SIMULATION START --------------")
            start = timer()
            remaining_events = []
    
            # Main simulator time progress 
            while self.getTime() < self.getTimeLimit():

              
                self.setCurrentDay(datetime(self.getRealTime().year, self.getRealTime().month, self.getRealTime().day))

            
                
                while self.getCurrentDay().weekday() >= self.weekdays:

                  

                    time_events = []
                    if self.getTime() in self.getEventQueue():
                        time_events =[e for e in self.getEventQueue()[self.getTime()]] # scheduled/started event
  
                        consdered_ev_ids = []
                        for ev_id in range(len(time_events)):
                            if ev_id in consdered_ev_ids:
                                continue
                            e = time_events[ev_id]
                            
                            case = OperationsMgr.determineProgressCase(e)

                            if case == "Suspend" or case == "Handle":
                                if e.getSuspendedSuccessor() == None:
                                    #self.saveLog(" REPORT: handle/suspend event "+e.getName()+"("+str(e.getID())+") moved from scheduled to pending")
                                    if e in self.getEventQueue()[self.getTime()]:
                                        self.getEventQueue()[self.getTime()].remove(e)
                                    if not e in self.getEventQueue()["Pending"]:
                                        self.getEventQueue()["Pending"].append(e)
                                else:
                                    successor = e.getSuspendedSuccessor()
                                    case = OperationsMgr.determineProgressCase(successor)
                                    if case == "Suspend" or case == "Handle":
                                        if successor in self.getEventQueue()[self.getTime()]:
                                            self.getEventQueue()[self.getTime()].remove(successor)
                                    if successor in time_events:
                                        consdered_ev_ids.append(time_events.index(successor))
                                        
                                    if not successor in self.getEventQueue()["Pending"]:
                                        self.getEventQueue()["Pending"].append(successor)

                    
                    self.updateTime(self.shiftsperday*self.shifthours*60)
                    self.setCurrentDay(datetime(self.getRealTime().year, self.getRealTime().month, self.getRealTime().day))
  
                self.setCurrentShift(self.getShift(self.getRealTime().hour))

                try:
                    if self.getTime() % self.getShiftMinutes() == 0:
                      
                        self.saveLog(" >>>>>>>>>>>>>>>>>>  Shift start: "+str(self.getRealTime())+"<<<<<<<<<<<<<<<<<<<"+"hour: "+str(self.getRealTime().hour)+"shift: "+str(self.getShift(self.getRealTime().hour))+" sim time: "+str(self.getTime()))
                        self.saveLog(" >>>>>>>>>>>>>>>>>> Current day: "+str(self.getCurrentDay())+" shift: "+str(self.getCurrentShift()))
                        OperationsMgr.applyShiftChange()
              
                except Exception as e:
                    self.saveLog("ERROR in shift change: "+str(e))
    

                try: 

                  
                    for event in self.getEventQueue()["Pending"]:
                        OperationsMgr.ProgressEvent(event)  

                    if self.getTime() in self.getEventQueue():
                        time_events =[e for e in self.getEventQueue()[self.getTime()]] # scheduled/started event
                        execround = 1
                        
                        while len(time_events) > 0:
                            for event in time_events:
                                OperationsMgr.ProgressEvent(event)
                            execround += 1
                            time_events =[e for e in self.getEventQueue()[self.getTime()]] # scheduled/started events
                            if execround > 10:
                                self.saveLog("REPORT: time "+str(self.getTime())+", time events "+str([e.getName()+"("+str(e.getID())+"), case: "+str(OperationsMgr.determineProgressCase(e)) for e in time_events]))
                             
                                for event in time_events:
                                    self.saveLog("REPORT: event "+str(event.getName())+"-"+str(event.getID())+", loc "+str(event.getLocation().getName()))
                                    for progress_id in range(len(event.getProgressList())):
                                        self.saveLog("REPORT: progress step: "+str(event.getProgressList()[progress_id][1]))
                                    self.saveLog("REPORT: TotalProgress: "+str(event.getTotalProgress())+", p: "+str(event.getProcessTime()))
                        
                except Exception as e:
                    self.saveLog("ERROR in execute events: "+str(e))

              
                self.updateTime(1)

         

            self.getController().getVisualManager().updateSimProgress("------------ SIMULATION END --------------")




            totaldemand = 0
            incompletequantity = 0

            for order in OperationsMgr.getSelectedOrders():

                totaldemand+=order.getQuantity()
                
                if order.getItems()[0].getActiveOperation() != None:
                    incompletequantity+=order.getQuantity()
                    #self.saveLog("REPORT: demand "+str(order.getFinalProduct().getPN())+", Q: "+str(order.getQuantity())+"["+(str(order.getItems()[0].getID()) if len(order.getItems())>0 else '')+"-"+(str(order.getItems()[-1].getID()) if len(order.getItems())>0 else 'no item')+"]"+" next opr: none?"+str(order.getItems()[0].getActiveOperation() == None))

            self.saveLog("REPORT: Returned items :"+str(len(OperationsMgr.getCentralInventory().getInputBuffer().getItems()))+", incomplete quantity: "+str(incompletequantity)+", sum "+str(len(OperationsMgr.getCentralInventory().getInputBuffer().getItems())+incompletequantity)+" <=> total demand: "+str(totaldemand))
            
                    

            for schtime,events in self.getEventQueue().items():
                if schtime == "Pending":
                    for e in events:
                        remaining_events.append(e)
                    continue
                if schtime >= int(self.getTimeLimit()-1):
                    for e in events:
                        remaining_events.append(e)
                   

            for res in OperationsMgr.getResources():    
                if len(res.getItems()) > 0:
                    self.saveLog("REPORT: "+str(res.getName())+" has "+str(len(res.getItems()))+ " items.")

                if res.getType() == "Machine": 
                    if len(res.getInputBuffer().getItems()) > 0:
                        self.saveLog("REPORT: "+str(res.getInputBuffer().getName())+" has "+str(len(res.getInputBuffer().getItems()))+ " items. ["+(str(res.getInputBuffer().getItems()[0].getID())+"-"+str(res.getInputBuffer().getItems()[-1].getID()) if len(res.getInputBuffer().getItems())>0 else '')+"]")
                    if len(res.getOutputBuffer().getItems()) > 0:
                        self.saveLog("REPORT: "+str(res.getOutputBuffer().getName())+" has "+str(len(res.getOutputBuffer().getItems()))+ " items.["+(str(res.getOutputBuffer().getItems()[0].getID())+"-"+str(res.getOutputBuffer().getItems()[-1].getID()) if len(res.getOutputBuffer().getItems())>0 else '')+"]")

                    
           

            if len(remaining_events) > 0:
                self.saveLog("REPORT: In-complete events: "+str(len(remaining_events)))
                #for event in remaining_events:
                    #self.saveLog(" REPORT: >>>>>>>>>> event: "+str(event.getName())+"("+str(event.getID())+")"+", loc: "+(event.getLocation().getName() if event.getLocation()!=None else "No Location")+", prog: "+str(event.getTotalProgress())+"-> "+str(["["+str(pr[1][0])+"-"+str(pr[1][1])+"]" for pr in event.getProgressList()])+", p: "+str(event.getProcessTime())+" items "+(str(len(event.getItems())) if len(event.getItems())>0 else "-")+" ["+(str(event.getItems()[0].getID())+"-"+str(event.getItems()[-1].getID()) if len(event.getItems())>0 else '')+"], reserved: ["+(str(event.getReservedItems()[0].getID())+"-"+str(event.getReservedItems()[-1].getID()) if len(event.getReservedItems())>0 else '')+"]")

                    #self.saveLog("REPORT:_____________________________________")
            
            end = timer()
            
            try:
                self.getController().getVisualManager().updateSimProgress("Simulation ended, run time "+str(round(end - start,2))+" seconds.")
                
                self.getController().getVisualManager().updateSimProgress("Simulation errors: "+str(self.getNoErrors()))
                for err in self.getErrors():
                    self.getController().getVisualManager().updateSimProgress(err)
            except Exception as e:
                self.saveLog("ERROR in progress update: "+str(e))
            start = timer()
            self.getController().getVisualManager().updateSimProgress("Writing data")
            OperationsMgr.writeData()
            #OperationsMgr.writeDataTBRMOutPut(1)
            end = timer()
            
            self.getController().getVisualManager().updateSimProgress("Data writing time "+str(round(end - start,2))+" seconds.")

        except Exception as e:
            self.saveLog("ERROR in sim run: "+str(e))
            
        return
 
############################################################################################################################
        self.writeData()
    def updateTime(self,timedelta):
        self.time+=timedelta
        return
    def getTime(self):
        return self.time
    def getEventNo(self):
        self.eventno+=1
        return self.eventno
    def getEventQueue(self):
        return self.queue
#__________________________________________________________________________________________________________________________________
class OperationsManager(object):
    def __init__(self,sim):
        self.Resources = []
        self.processid = 0
        self.itemid = 0
        self.resourceid = 0   
        self.demandid = 0
        self.Simulator = sim
        self.Demands = []  
        self.DemandTypes = []
        self.DemandTypeName = None
        self.EventTypes = dict()
        self.AlgorithmManager = AlgorithmManager(sim,self)
        self.usecase = ''
        self.layout = Layout("UseCase")

    def getLayout(self):
        return self.layout

    def setDemandType(self,demandname):
        self.DemandTypeName = demandname
        return
    

    def getAlgorithmManager(self):
        self.AlgorithmManager

    def setUseCase(self,mycase):
        self.usecase = mycase
        return

    def getUseCase(self):
        return self.usecase
    
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
        #overwritten by subclassess
        return 
#####################################################################################################################################################
    def startEvent(self,event):
       #overwritten by subclassess   
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
       
        self.simulator = sim
        self.OperationsManager = oprmgr

        
    def getOperationsManager(self):
        return self.OperationsManager
 
    def getPriorityScoringFunctions(self):
        return self.PriorityScoringFunctions

    def getSimulator(self):
        return self.simulator


############################################################################################################      
class MILPManager(object):
    def __init__(self,sim):
        
        self.simulator = sim
        self.OperationSchedules = dict() # key: job, val: (start,comp)
        self.MachJobAssignments = dict() # key: mach, val: [job]

   

    def getMachJobAssignments(self):
        return self.MachJobAssignments 
 
 
    def getMachJobAssignments(self):
        return self.MachJobAssignments

    def getSimulator(self):
        return self.simulator
#######################################################################################################

        
#######################################################################################################
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
        
####################################################################################
class DataManager(object):
    def __init__(self,sim,oprmgr):
        self.data_df = dict() # key: priority criterion, val: specific function
        self.ObjectFeatures = dict() # key: object type, val: columns of data_df of properties of objects
        self.simulator = sim
        self.OperationsManager = oprmgr

   
        

    def ReadData(self):
        #overwritten by subclassess
        return
    def ReadDemandFile(self):
        #overwritten by subclassess
        return

    def getObjectFeatures(self):
        return self.ObjectFeatures
        
    def getOperationsManager(self):
        return self.OperationsManager

    def getSimulator(self):
        return self.simulator







 