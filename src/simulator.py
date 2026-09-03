from __future__ import annotations

from datetime import timedelta,date,datetime
from simulationobjects import *
import random
import pandas as pd
import os 
from timeit import default_timer as timer
from pathlib import Path
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from controller import Controller

class Simulator(object):
    def __init__(self) -> None:
        
        self.EventData: list[dict[str, Any]] = [] # [{"EventID':...,"EventName":...,'Location Name/ID':...,"Equipment Name/ID":...,"Resource Name/ID":...,"Items":...}]
        self.ExecutionData: list[dict[str, Any]] = [] # [{"EventID':...,"EventName":...,'Status':...}]
        self.LocationData: list[dict[str, Any]] = [] 
        self.BufferData: list[dict[str, Any]] = [] 
        self.queue: dict[Any, list[ExecEvent]] = {} #key: time (start/completion times of events) , val: [event]
        self.time: int = 0
        self.eventno: int = 0
     
        self.queue["Pending"] = [] # list of pending events, to be hanlded
    
        self.DataTypes: dict[str, pd.DataFrame] = dict() # key: dataset name, val: dataframe objects. 
        self.startday: datetime | None = None 
        self.shiftmapping: dict[int, int] = {0:3,8:1,16:2}
        self.shiftlength: timedelta = timedelta(hours = 7)+ timedelta(minutes = 59)
        self.currentDay: datetime | None = None # will be updated dynamically
        self.currentShift: int | None = None #will be updated dynamically 

        currentdate =  datetime.now()
        startday = datetime(currentdate.year, currentdate.month, currentdate.day)
        self.shifthours = 8 
        self.shiftsperday = 3 
        self.weekdays = 5
        self.shift_minutes = 60*self.shifthours
        self.TimeLimit: int | None =  None
        self.MyLog: dict[Any, list[str]] = dict() #key: sim time, val: [events]
        self.Controller: Controller | None = None
        self.RunErrors: int = 0
        self.Errors: list[str] = []

        self.setStartDay(startday+timedelta(hours= 24))

        print("Start day: ",self.getStartDay().date()," weekday: ",self.getStartDay().weekday(), " day: ",self.getStartDay().strftime("%A"),", TimeLimit: ",self.TimeLimit)

    def getErrors(self) -> list[str]:
        return self.Errors 
        

    def addError(self) -> None:
        self.RunErrors+=1
        return
        
    def getNoErrors(self) -> int:
        return self.RunErrors
        
    def setController(self, contr: Controller) -> None:
        self.Controller = contr
        return
    def getController(self) -> Controller | None:
        return self.Controller
        
    def getMyLog(self):
        return self.MyLog

    def saveLog(self,info):

        
        if not self.getTime() in self.MyLog:
            self.MyLog[self.getTime()] = []
        self.MyLog[self.getTime()].append(info)


        if info.find("ERROR")> -1:
            self.getErrors().append(str(self.getTime())+": "+info)
            self.addError()

        
        if info.find("ERROR")> -1 or info.find("REPORT")> -1 : 
            self.getController().getVisualManager().updateSimProgress(str(self.getTime())+"["+str(self.getRealTime())+"]: "+info)
        return
        
    def saveTitleLog(self,title,info):
        
        if not title in self.MyLog:
            self.MyLog[title] = []
        self.MyLog[title].append(info)
        return
        
    def setRunWeeks(self,weeks: int):
        self.TimeLimit =  weeks*60*self.shifthours*self.shiftsperday*self.weekdays

        return

    def getTimelimit(self) -> int | None:
        return self.TimeLimit

        

    def getShiftMinutes(self) -> int:
        return self.shift_minutes

    def getShift(self,hour: int) -> int:
        if hour in self.shiftmapping:
            return self.shiftmapping[hour]
        else:
            return 0
        
    def setStartDay(self,myday) -> None:
        self.startday = myday
        return
    def getStartDay(self) -> datetime:
        return self.startday

    def setCurrentShift(self,shft: int) -> None:
        self.currentShift = shft
        return 
    def getCurrentShift(self) -> int:
        return self.currentShift

    def getShiftSimTime(self,simtime):
        return self.getShift(self.checkRealTime(simtime).hour)

    def setCurrentDay(self,day: datetime) -> None:
        self.currentDay = day
        return
        
    def getCurrentDay(self) -> datetime:
        return self.currentDay 

    def getDataTypes(self) -> list:
        return self.DataTypes

    def getEventData(self) -> list:
        return self.EventData
    def getExecutionData(self) -> list:
        return self.ExecutionData

    def getLocationData(self) -> list:
        return self.LocationData

    def getBufferData(self) -> list:
        return self.BufferData
          
    def getTimeLimit(self) -> int | None:
        return self.TimeLimit

    def getRealTime(self) -> datetime:
        return self.getStartDay()+timedelta(minutes = self.getTime())

    def checkRealTime(self,time: int) -> datetime:
        return self.getStartDay()+timedelta(minutes = time)

############################################################################################
    def RunSimulation(self,OperationsMgr: OperationsManager) -> None: 

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







 