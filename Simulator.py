from datetime import timedelta,date,datetime
from simulationobjects import *
import random
import pandas as pd
import os 
from timeit import default_timer as timer
from pathlib import Path


class Simulator(object):
    def __init__(self):
        
        self.EventData = [] # [{"EventID':...,"EventName":...,'Location Name/ID':...,"Equipment Name/ID":...,"Resource Name/ID":...,"Items":...}]
        self.ExecutionData = [] # [{"EventID':...,"EventName":...,'Status':...}]
        self.queue = {} #key: time (start/completion times of events) , val: [event]
        self.time = 0
        self.eventno = 0
     
        self.queue["Pending"] = [] # list of pending events, to be hanlded
        self.queue["Preemptables"] = [] # list of ongoing process events
        self.DataTypes = dict() # key: dataset name, val: dataframe objects. 
        self.startday = None 
        self.shiftmapping = {0:3,8:1,16:2}
        self.shiftlength = timedelta(hours = 7)+ timedelta(minutes = 59)
        self.currentDay = None # will be updated dynamically
        self.currentShift = None #will be updated dynamically 

        currentdate =  datetime.now()-timedelta(days = 2)
        startday = datetime(currentdate.year, currentdate.month, currentdate.day)
        self.shifthours = 8 
        self.shiftsperday = 3 
        self.weekdays = 5
        self.shift_minutes = 60*self.shifthours
        self.TimeLimit =  None
        self.MyLog = dict() #key: sim time, val: [events]
        self.Controller = None

        self.setStartDay(startday+timedelta(hours= 24))

        print("Start day: ",self.getStartDay().date()," weekday: ",self.getStartDay().weekday(), " day: ",self.getStartDay().strftime("%A"),", TimeLimit: ",self.TimeLimit)

    def setController(self,contr):
        self.Controller = contr
        return
    def getController(self):
        return self.Controller
        
    def getMyLog(self):
        return self.MyLog

    def saveLog(self,info):
        if not self.getTime() in self.MyLog:
            self.MyLog[self.getTime()] = []
        self.MyLog[self.getTime()].append(info)
        if not self.getController().getWorkManager().isPerformanceRun():
            self.getController().getVisualManager().updateSimProgress(str(self.getTime())+": "+info)
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
          
    def getTimeLimit(self):
        return self.TimeLimit

    def getRealTime(self):
        return self.getStartDay()+timedelta(minutes = self.getTime())

    def checkRealTime(self,time):
        return self.getStartDay()+timedelta(minutes = time)

############################################################################################
    def RunSimulation(self,OperationsMgr): 

        start = timer()
        try:
            self.getController().getVisualManager().updateSimProgress("Simulation starts ")
        except Exception as e:
            self.saveLog("ERROR in progress update: "+str(e))
            
        while self.getTime() < self.getTimeLimit():
            
            self.setCurrentDay(datetime(self.getRealTime().year, self.getRealTime().month, self.getRealTime().day))
            self.setCurrentShift(self.getShift(self.getRealTime().hour))

            if self.getTime() % self.shift_minutes == 0:
                try:
                    self.saveLog(">>>>>>>>>>>>>>>>>>  Shift start: "+str(self.getRealTime())+"<<<<<<<<<<<<<<<<<<<"+"hour: "+str(self.getRealTime().hour)+"shift: "+str(self.getShift(self.getRealTime().hour))+" sim time: "+str(self.getTime()))
                    self.saveLog(">>>>>>>>>>>>>>>>>> Current day: "+str(self.getCurrentDay())+" shift: "+str(self.getCurrentShift()))
                    OperationsMgr.applyShiftChange()
                except Exception as e:
                    self.saveLog("ERROR in shift change: "+str(e))
                

            while self.getCurrentDay().weekday() >= self.weekdays:
                self.saveLog("Weekend jump..")
                self.setCurrentDay(self.getCurrentDay()+timedelta(days= 1))

                for res in OperationsMgr.getResources():
                    if res.getType() == "Machine":
                        self.saveLog("Res "+res.getName()+" progresses .."+str(len(res.getProgressDict())))
                        for ev,progress in res.getProgressDict().items():
                            self.saveLog("Res "+res.getName()+" ongoing event "+ev.print()+" proctime: "+str(progress))
                        
                
                move_dict = dict()
                for time,time_events in self.getEventQueue().items():
                    
                    if time in ["Pending","Preemptables"]:
                        continue
                    #self.saveLog("Time "+str(time)+", Events "+str(len(time_events)))
                    if time <= self.getTime():
                        continue
                    move_dict[time] = []
                    for ev in time_events:
                        move_dict[time].append(ev)
                        self.saveLog("Event "+ev.print()+" moved from time "+str(time)+" to time "+str(time+self.shiftsperday*self.shifthours*60))
                    self.getEventQueue()[time].clear()
                
                for time,time_events in move_dict.items():
                    self.getEventQueue()[time+self.shiftsperday*self.shifthours*60] = []
                    for ev in time_events:
                        self.getEventQueue()[time+self.shiftsperday*self.shifthours*60].append(ev)
                self.updateTime(self.shiftsperday*self.shifthours*60)
                        
             
            self.updateTime(1)
            
            self.executeEvents(OperationsMgr)

        end = timer()
        
        try:
            self.getController().getVisualManager().updateSimProgress("Simulation ended, run time "+str(round(end - start,2))+" seconds.")
        except Exception as e:
            self.saveLog("ERROR in progress update: "+str(e))
        start = timer()
        self.getController().getVisualManager().updateSimProgress("Writing data")
        OperationsMgr.writeData()
        end = timer()
        self.getController().getVisualManager().updateSimProgress("Data writing time "+str(round(end - start,2))+" seconds.")

        return

        
######################################################################################################        
    def executeEvents(self,workmgr):

        self.getEventQueue()["Pending"] = [e for e in self.getEventQueue()["Pending"] if not workmgr.HandleSimEvent(e) ]

        
        for event in self.getEventQueue()["Preemptables"]:
            if not event.IsActive():
                workmgr.resumeSimEvent(event)   
            else:
              
                #self.saveLog(" completing event "+event.getName()+" ? "+str(workmgr.getEventProgress(event,False))+", proctime "+str(event.getProcessTime()))
                if workmgr.getEventProgress(event,True) == event.getProcessTime():
                    workmgr.commpleteSimEvent(event)
            
      
        if self.time in self.queue:
            ev_round = 1
            time_events =[e for e in self.queue[self.time]] # scheduled/started events

            
            while len(time_events) > 0: 
                self.saveLog(" Non-pending events "+str(len(time_events))+"("+str(ev_round)+")"+str([i.getName()+"("+str(i.getID())+")" for i in time_events]))
                event_progress = 0
                for event in time_events:
                    if event.IsActive():  # completion of event
                        if event in self.getEventQueue()[self.time]:
                            event_progress+=1
                            workmgr.commpleteSimEvent(event)
                            self.queue[self.time].remove(event) 
                    else:
                        if not workmgr.startSimEvent(event):
                            #self.saveLog(" starting not successful back to pending...")
                            self.getEventQueue()["Pending"].append(event)
                        else:
                            if event.getEventType().isPreemptable():
                                #self.saveLog(" adding preemptables...")
                                if not event in self.getEventQueue()["Preemptables"]:
                                    self.getEventQueue()["Preemptables"].append(event)

                        self.queue[self.time].remove(event)
                        event_progress+=1 
           

                time_events =[e for e in self.queue[self.time]] # scheduled/started events
                ev_round+=1
                
            
     
        return
#############################################################################################################################          
    def ScheduleEvent(self,event,time,workmgr):
        
        self.saveLog(" scheduling "+event.print()+" with start time "+str(time)+", preemptable "+str(event.getEventType().isPreemptable()))
      
        # if time = Pending, it will be handled, otherwise it will start
        if not time in self.getEventQueue():
            self.getEventQueue()[time] = []
        self.getEventQueue()[time].append(event)

        if (time == "Pending"):
            return
           

        if event.getEventType().getSuccessorType()!= None:
            if 'Simultaneous Start' in event.getEventType().getPrecendenceDict()[event.getEventType().getSuccessorType().getName()]:
                nextevent = workmgr.defineNextEvent(event,'Simultaneous Start')
                self.saveLog(" successor with precedence SS: "+nextevent.getName())
                self.getEventQueue()[time].append(nextevent) # let the SS precendence event stsrt at the same time..   

        if event.getEventType().isPreemptable():
            return

        # time is start time
        completion = workmgr.getCompletionTime(event,time)

        curr_shiftstart = (self.getTime()//self.getShiftMinutes())*self.getShiftMinutes()
        curr_shiftsend = curr_shiftstart+self.getShiftMinutes()*int((self.getTime()%self.getShiftMinutes())>0)

        
        if completion > curr_shiftsend: 
            # do not schedule event in this shift since it cannot finish..
            self.saveLog(" non-preemptable event cannot be completed in this shift, so kept pending.")
            self.getEventQueue()["Pending"].append(event)
            return
        else:
            self.saveLog(" "+event.print()+" completion time "+str(completion)+", event+proctime: "+str(time+event.getProcessTime()))
            event.setCompletionTime(completion)
                    
            if not (completion) in self.getEventQueue():
                self.getEventQueue()[completion] = []
                        
            if not event in self.getEventQueue()[completion]:
                self.getEventQueue()[completion].append(event)   
       
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

