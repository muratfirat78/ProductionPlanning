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
        self.EventUpdateData = [] # [{"Time":...,"EventID":...,"Field":...,"OldValue":...,"NewValue":...}]
        self.allEvents = []
        self.completedEvents = []
        self.queue = {} #key: time (start/completion times of events) , val: [event]
        self.time = 0
        self.eventno = 0
        self.locationDf = pd.DataFrame(columns=["PN","Q","Deadline", "LocationFrom", "LocationTo"])
        self.processingDf = pd.DataFrame(columns=["PN", "Q", "Deadline", "Operation", "StartTime", "ProcessTime", "ExpectedEnd", "SimEnd", "Status"])
        self.orderOverviewDf = pd.DataFrame(columns =["PN", "Q", "Deadline", "Operation", "StartTime", "ProcessTime", "ExpectedEnd", "SimEnd", "Status", "LocationFrom", "LocationTo"])
        self.successorDf = pd.DataFrame(columns=["Time", "EventID", "Event", "SuccessorID", "Successor", "DefinedSuccessors", "PrecedenceTypes", "Place", "Equipment", "Resource", "ItemIDs", "ProgressState"])
        self.eventUpdateDf = pd.DataFrame(columns=["Time", "RealTime", "EventID", "Event", "Field", "OldValue", "NewValue", "Active", "ProgressState", "Equipment", "Resource", "Location"])
        self.eventStatusDf = pd.DataFrame(columns=["CreationTime", "OrderID", "Product", "Quantity", "Deadline", "EventID", "Event", "EventType", "Status", "Active", "StartTime", "CompletionTime", "ProcessTime", "Place", "Equipment", "Resource", "Location", "ItemIDs", "Successor", "DefinedSuccessors", "PrecedenceTypes"])
        self.orderTraceDf = pd.DataFrame(columns=["OrderID", "Product", "Quantity", "Deadline", "CreationTime", "EventID", "Event", "EventType", "Status", "Active", "StartTime", "CompletionTime", "ProcessTime", "Place", "Equipment", "Resource", "Location", "ItemIDs", "Successor", "DefinedSuccessors", "PrecedenceTypes"])
        self.validationDf = pd.DataFrame(columns=["OrderID", "Product", "Quantity", "Deadline", "EventID", "Event", "EventType", "Status", "IssueLevel", "Issue", "Expected", "Actual", "CreationTime", "StartTime", "CompletionTime", "Place", "Equipment", "Resource", "Location", "ItemIDs", "Successor", "DefinedSuccessors", "PrecedenceTypes"])
    
     
        self.queue["Pending"] = [] # list of pending events, to be hanlded
        self.queue["Preemptables"] = [] # list of ongoing process events
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

        
        if info.find("ERROR")> -1 or info.find("REPORT")> -1 : 
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

    def getEventUpdateData(self):
        return self.EventUpdateData

    def getSuccessorDf(self):
        return self.successorDf

    def getEventStatusDf(self):
        return self.eventStatusDf

    def getOrderTraceDf(self):
        return self.orderTraceDf

    def getValidationDf(self):
        return self.validationDf

    def getEventOrderInfo(self,event):
        order = None
        if len(event.getItems()) > 0:
            order = event.getItems()[0].getDemand()

        if order == None:
            return (None, "", None, None)

        product = order.getFinalProduct()
        return (order.getID(), product.getPN(), order.getQuantity(), order.getDeadline())

    def recordCreatedEvent(self,event):
        if event not in self.allEvents:
            self.allEvents.append(event)

    def recordEventUpdate(self,event,field,old_value,new_value):
        if event == None:
            return

        def format_value(value):
            if value == None:
                return "None"
            if hasattr(value, "getName") and hasattr(value, "getID"):
                return value.getName()+"["+str(value.getID())+"]"
            if isinstance(value, tuple):
                return "->".join([format_value(part) for part in value])
            return str(value)

        location = event.getLocation()
        if isinstance(location, tuple):
            location_text = "->".join([location[0].getName() if location[0] != None else "None", location[1].getName() if location[1] != None else "None"])
        elif location == None:
            location_text = ""
        else:
            location_text = location.getName()

        self.EventUpdateData.append({
            "Time": self.getTime(),
            "RealTime": self.getRealTime(),
            "EventID": event.getID(),
            "Event": event.getName(),
            "Field": field,
            "OldValue": format_value(old_value),
            "NewValue": format_value(new_value),
            "Active": event.IsActive(),
            "ProgressState": event.progressState,
            "Equipment": "" if event.getEquipment() == None else event.getEquipment().getName(),
            "Resource": "" if event.getResource() == None else event.getResource().getName(),
            "Location": location_text,
        })

    def recordSuccessorTrace(self,event):
        successor = event.getSuccessor()

        defined_successors = []
        for succ_type, succ_event in event.getDefinedSuccessors().items():
            succ_type_text = succ_type.getName() if succ_type != None else "None"
            succ_event_text = "None" if succ_event == None else succ_event.getName()+"["+str(succ_event.getID())+"]"
            defined_successors.append(succ_type_text+"->"+succ_event_text)

        precedence_types = []
        for succ_event, precedence_type in event.getPrecedenceTypes().items():
            succ_event_text = "None" if succ_event == None else succ_event.getName()+"["+str(succ_event.getID())+"]"
            precedence_types.append(succ_event_text+":"+str(precedence_type))

        place = event.getPlace()
        equipment = event.getEquipment()
        resource = event.getResource()

        self.successorDf.loc[len(self.successorDf)] = [
            self.getTime(),
            event.getID(),
            event.getName(),
            None if successor == None else successor.getID(),
            None if successor == None else successor.getName(),
            "; ".join(defined_successors),
            "; ".join(precedence_types),
            "" if place == None else place.getName(),
            "" if equipment == None else equipment.getName(),
            "" if resource == None else resource.getName(),
            ",".join([str(item.getID()) for item in event.getItems()]),
            event.progressState,
        ]

    def buildEventStatusDf(self):
        event_status_df = pd.DataFrame(columns=["CreationTime", "OrderID", "Product", "Quantity", "Deadline", "EventID", "Event", "EventType", "Status", "Active", "StartTime", "CompletionTime", "ProcessTime", "Place", "Equipment", "Resource", "Location", "ItemIDs", "Successor", "DefinedSuccessors", "PrecedenceTypes"])

        for event in self.allEvents:
            successor = event.getSuccessor()
            order_id, product, quantity, deadline = self.getEventOrderInfo(event)

            defined_successors = []
            for succ_type, succ_event in event.getDefinedSuccessors().items():
                succ_type_text = succ_type.getName() if succ_type != None else "None"
                succ_event_text = "None" if succ_event == None else succ_event.getName()+"["+str(succ_event.getID())+"]"
                defined_successors.append(succ_type_text+"->"+succ_event_text)

            precedence_types = []
            for succ_event, precedence_type in event.getPrecedenceTypes().items():
                succ_event_text = "None" if succ_event == None else succ_event.getName()+"["+str(succ_event.getID())+"]"
                precedence_types.append(succ_event_text+":"+str(precedence_type))

            place = event.getPlace()
            equipment = event.getEquipment()
            resource = event.getResource()
            location = event.getLocation()

            if isinstance(location, tuple):
                location_text = location[0].getName()+"->"+location[1].getName()
            elif location == None:
                location_text = ""
            else:
                location_text = location.getName()

            event_status_df.loc[len(event_status_df)] = [
                event.getCreationTime(),
                order_id,
                product,
                quantity,
                deadline,
                event.getID(),
                event.getName(),
                event.getEventType().getName(),
                event.progressState,
                event.IsActive(),
                event.getStartTime(),
                event.getCompletionTime(),
                event.getProcessTime(),
                "" if place == None else place.getName(),
                "" if equipment == None else equipment.getName(),
                "" if resource == None else resource.getName(),
                location_text,
                ",".join([str(item.getID()) for item in event.getItems()]),
                None if successor == None else successor.getName()+"["+str(successor.getID())+"]",
                "; ".join(defined_successors),
                "; ".join(precedence_types),
            ]

        self.eventStatusDf = event_status_df.sort_values(by=["CreationTime","EventID"])

    def buildEventUpdateDf(self):
        event_update_df = pd.DataFrame(self.EventUpdateData, columns=["Time", "RealTime", "EventID", "Event", "Field", "OldValue", "NewValue", "Active", "ProgressState", "Equipment", "Resource", "Location"])

        if len(event_update_df) > 0:
            self.eventUpdateDf = event_update_df.sort_values(by=["Time", "EventID"])
        else:
            self.eventUpdateDf = event_update_df
        

    def buildOrderTraceDf(self):
        order_trace_df = pd.DataFrame(columns=["OrderID", "Product", "Quantity", "Deadline", "CreationTime", "EventID", "Event", "EventType", "Status", "Active", "StartTime", "CompletionTime", "ProcessTime", "Place", "Equipment", "Resource", "Location", "ItemIDs", "Successor", "DefinedSuccessors", "PrecedenceTypes"])

        for event in self.allEvents:
            successor = event.getSuccessor()
            order_id, product, quantity, deadline = self.getEventOrderInfo(event)

            if order_id == None:
                continue

            defined_successors = []
            for succ_type, succ_event in event.getDefinedSuccessors().items():
                succ_type_text = succ_type.getName() if succ_type != None else "None"
                succ_event_text = "None" if succ_event == None else succ_event.getName()+"["+str(succ_event.getID())+"]"
                defined_successors.append(succ_type_text+"->"+succ_event_text)

            precedence_types = []
            for succ_event, precedence_type in event.getPrecedenceTypes().items():
                succ_event_text = "None" if succ_event == None else succ_event.getName()+"["+str(succ_event.getID())+"]"
                precedence_types.append(succ_event_text+":"+str(precedence_type))

            place = event.getPlace()
            equipment = event.getEquipment()
            resource = event.getResource()
            location = event.getLocation()

            if isinstance(location, tuple):
                location_text = location[0].getName()+"->"+location[1].getName()
            elif location == None:
                location_text = ""
            else:
                location_text = location.getName()

            order_trace_df.loc[len(order_trace_df)] = [
                order_id,
                product,
                quantity,
                deadline,
                event.getCreationTime(),
                event.getID(),
                event.getName(),
                event.getEventType().getName(),
                event.progressState,
                event.IsActive(),
                event.getStartTime(),
                event.getCompletionTime(),
                event.getProcessTime(),
                "" if place == None else place.getName(),
                "" if equipment == None else equipment.getName(),
                "" if resource == None else resource.getName(),
                location_text,
                ",".join([str(item.getID()) for item in event.getItems()]),
                None if successor == None else successor.getName()+"["+str(successor.getID())+"]",
                "; ".join(defined_successors),
                "; ".join(precedence_types),
            ]

        self.orderTraceDf = order_trace_df.sort_values(by=["OrderID","CreationTime","EventID"])

    def buildValidationDf(self):
        validation_df = pd.DataFrame(columns=["OrderID", "Product", "Quantity", "Deadline", "EventID", "Event", "EventType", "Status", "IssueLevel", "Issue", "Expected", "Actual", "CreationTime", "StartTime", "CompletionTime", "Place", "Equipment", "Resource", "Location", "ItemIDs", "Successor", "DefinedSuccessors", "PrecedenceTypes"])

        def add_issue(event, issue_level, issue, expected, actual):
            order_id, product, quantity, deadline = self.getEventOrderInfo(event)

            successor = event.getSuccessor()
            defined_successors = []
            for succ_type, succ_event in event.getDefinedSuccessors().items():
                succ_type_text = succ_type.getName() if succ_type != None else "None"
                succ_event_text = "None" if succ_event == None else succ_event.getName()+"["+str(succ_event.getID())+"]"
                defined_successors.append(succ_type_text+"->"+succ_event_text)

            precedence_types = []
            for succ_event, precedence_type in event.getPrecedenceTypes().items():
                succ_event_text = "None" if succ_event == None else succ_event.getName()+"["+str(succ_event.getID())+"]"
                precedence_types.append(succ_event_text+":"+str(precedence_type))

            place = event.getPlace()
            equipment = event.getEquipment()
            resource = event.getResource()
            location = event.getLocation()

            if isinstance(location, tuple):
                location_text = location[0].getName()+"->"+location[1].getName()
            elif location == None:
                location_text = ""
            else:
                location_text = location.getName()

            validation_df.loc[len(validation_df)] = [
                order_id,
                product,
                quantity,
                deadline,
                event.getID(),
                event.getName(),
                event.getEventType().getName(),
                event.progressState,
                issue_level,
                issue,
                expected,
                actual,
                event.getCreationTime(),
                event.getStartTime(),
                event.getCompletionTime(),
                "" if place == None else place.getName(),
                "" if equipment == None else equipment.getName(),
                "" if resource == None else resource.getName(),
                location_text,
                ",".join([str(item.getID()) for item in event.getItems()]),
                None if successor == None else successor.getName()+"["+str(successor.getID())+"]",
                "; ".join(defined_successors),
                "; ".join(precedence_types),
            ]

        for event in self.allEvents:
            event_type = event.getEventType()
            status = event.progressState

            if status not in ["Created", "Pending"]:
                if event_type.getEquipmentType() != None and event.getEquipment() != None and event.getEquipment().getType() != event_type.getEquipmentType():
                    add_issue(event, "Error", "Equipment type mismatch", event_type.getEquipmentType(), event.getEquipment().getType())

                if event_type.getResourceType() != None and event.getResource() != None and event.getResource().getType() != event_type.getResourceType():
                    add_issue(event, "Error", "Resource type mismatch", event_type.getResourceType(), event.getResource().getType())

                if event.getEquipment() == None:
                    add_issue(event, "Error", "Missing equipment", "Assigned equipment", "None")

                if event.getResource() == None:
                    add_issue(event, "Error", "Missing resource", "Assigned resource", "None")

            if status in ["Started", "Progressed", "Completed"] and event.getEventType().isStatic() and event.getPlace() == None:
                add_issue(event, "Error", "Missing place for static event", "Assigned place", "None")

            if event.getEventType().getName() in ["Machine Loading", "Trailer Loading", "Trailer Unloading", "Machine Unloading", "Processing"]:
                if len(event.getItems()) == 0:
                    add_issue(event, "Error", "No items assigned", "At least one item", "0 items")

            if event.getEventType().getName() == "Processing":
                if event.getEquipment() != None and event.getResource() != None and event.getResource() != event.getEquipment():
                    add_issue(event, "Warning", "Process resource and equipment differ", event.getEquipment().getName(), event.getResource().getName())

            if event.getEventType().getSuccessorType() != None and event.getSuccessor() == None and status not in ["Created", "Pending"]:
                add_issue(event, "Warning", "Missing successor for wired event", event.getEventType().getSuccessorType().getName(), "None")

            if event.getEventType().isPreemptable() and event.getEventType().isProcess() and status in ["Started", "Progressed", "Completed"] and len(event.getProgressDict()) == 0:
                add_issue(event, "Warning", "Missing progress tracking for preemptable process", "ProgressDict entry", "Empty")

        self.validationDf = validation_df.sort_values(by=["IssueLevel", "OrderID", "EventID"], kind="stable")
          
    def getTimeLimit(self):
        return self.TimeLimit

    def getRealTime(self):
        return self.getStartDay()+timedelta(minutes = self.getTime())

    def checkRealTime(self,time):
        return self.getStartDay()+timedelta(minutes = time)

############################################################################################
    def RunSimulation(self,OperationsMgr): 

        try: 

            self.saveLog("simulation starts..")
            start = timer()
            try:
                self.getController().getVisualManager().updateSimProgress("Simulation starts ")
            except Exception as e:
                self.saveLog("ERROR in progress update: "+str(e))
    
            while self.getTime() < self.getTimeLimit():
    
                self.setCurrentDay(datetime(self.getRealTime().year, self.getRealTime().month, self.getRealTime().day))
    
                weekendjump = 0
                if self.getCurrentDay().weekday() >= self.weekdays:
                    self.saveLog("Weekend jump..")
       
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
                    weekendjump+=self.shiftsperday*self.shifthours*60
                            
    
                
                self.setCurrentShift(self.getShift(self.getRealTime().hour))
    
                if self.getTime() % self.shift_minutes == 0:
                    try:
                        self.saveLog(" >>>>>>>>>>>>>>>>>>  Shift start: "+str(self.getRealTime())+"<<<<<<<<<<<<<<<<<<<"+"hour: "+str(self.getRealTime().hour)+"shift: "+str(self.getShift(self.getRealTime().hour))+" sim time: "+str(self.getTime()))
                        self.saveLog(" >>>>>>>>>>>>>>>>>> Current day: "+str(self.getCurrentDay())+" shift: "+str(self.getCurrentShift()))
                        OperationsMgr.applyShiftChange(weekendjump)
                    except Exception as e:
                        self.saveLog("ERROR in shift change: "+str(e))
    
                self.updateTime(1)
                try: 
                    self.executeEvents()
                except Exception as e:
                    self.saveLog("ERROR in execute events: "+str(e))
                    
    
            end = timer()
            
            try:
                self.getController().getVisualManager().updateSimProgress("Simulation ended, run time "+str(round(end - start,2))+" seconds.")
            except Exception as e:
                self.saveLog("ERROR in progress update: "+str(e))
            start = timer()
            self.getController().getVisualManager().updateSimProgress("Writing data")
            OperationsMgr.writeData()
            OperationsMgr.writeDataTBRMOutPut()
            self.getController().getVisualManager().updateSimProgress("Hoi")
            self.locationDf = self.locationDf.sort_values(by=["PN"])
            self.getController().getVisualManager().updateSimProgress("Hoi2")
            self.processingDf = self.processingDf.sort_values(by=["PN","StartTime"])
            self.getController().getVisualManager().updateSimProgress("Hoi3")
            self.locationDf.to_csv('LocationTest.csv')
            self.getController().getVisualManager().updateSimProgress("Hoi4")
            self.processingDf.to_csv('processingTest.csv')
            self.getController().getVisualManager().updateSimProgress("Hoi5")
            self.orderOverview()
            self.orderOverviewDf.to_csv('orderOverviewTest.csv')
            self.getController().getVisualManager().updateSimProgress("Hoi6")
            self.successorDf = self.successorDf.sort_values(by=["Time","EventID"])
            self.buildEventStatusDf()
            self.buildEventUpdateDf()
            self.buildOrderTraceDf()
            self.buildValidationDf()
            with pd.ExcelWriter('SuccessorTrace.xlsx') as writer:
                self.successorDf.to_excel(writer, sheet_name='SuccessorTrace', index=False)
                self.eventStatusDf.to_excel(writer, sheet_name='EventStatus', index=False)
                self.eventUpdateDf.to_excel(writer, sheet_name='EventUpdates', index=False)
                self.orderTraceDf.to_excel(writer, sheet_name='OrderTrace', index=False)
                self.validationDf.to_excel(writer, sheet_name='ValidationReport', index=False)
            end = timer()
            self.getController().getVisualManager().updateSimProgress("Data writing time "+str(round(end - start,2))+" seconds.")

        except Exception as e:
            self.saveLog("ERROR in sim run: "+str(e))
            
        return

        
######################################################################################################        
    def executeEvents(self):

        keyword = ""

        workmgr = self.getController().getWorkManager()

        # if an event is handled, then the return is true and does not stay in pending list.
        try: 
            self.getEventQueue()["Pending"] = [e for e in self.getEventQueue()["Pending"] if not workmgr.HandleSimEvent(e)]
        except Exception as e:
            self.saveLog("ERROR: Handling of lala pending events"+str(e))


        # continue with preemptable events...
        try: 
            for event in self.getEventQueue()["Preemptables"]:
                self.saveLog(keyword+": preemptable event "+event.print()+" to handle.. active? "+str(event.IsActive()))
                if not event.IsActive():
                    try: 
                        workmgr.resumeSimEvent(event)  
                    except Exception as e:
                        self.saveLog("ERROR: resuming event "+str(e))
                else:
                    
                    eventprogress = event.getTotalProgress()
                    event.setProgress(self.getTime(), "Progressed")
                    
                    self.saveLog(" preemptable event total progress .."+str(eventprogress))
                    for nextevent,prectype in event.getPrecedenceTypes().items(): # note that sim. finish event is already created in the start
                        nextproctime = workmgr.getProcessTime(nextevent)
                        if prectype ==  'Simultaneous Finish':
                            if not nextevent.IsActive():
                                if event.getProcessTime() - eventprogress  <= nextproctime:
                                    self.saveLog("REPORT: preemptable event "+event.getName()+"["+str(event.getID())+"]"+" SS event scheduling .."+nextevent.getName()+"["+str(nextevent.getID())+"]")
                        
                                    self.ScheduleEvent(nextevent)
                                    del event.getPrecedenceTypes()[nextevent]
                                    break
    
                    if eventprogress == event.getProcessTime():
                        self.completedEvents.append(event)
                        event.setProgress(self.getTime(), "Completed")
                        workmgr.commpleteSimEvent(event)   
        except Exception as e:
            self.saveLog("ERROR: Handling of preemptable events "+str(e))

       
        
        # continue with non-pending and non-preemptable events...
        try: 
            if self.time in self.queue:
                self.saveLog(" Handling of non/pending-preemptable events at "+str(self.time))
                ev_round = 1
                time_events =[e for e in self.queue[self.time]] # scheduled/started events
    
                self.saveLog("Handling of non/pending-preemptable events no "+str(len(time_events)))
                while len(time_events) > 0: 
                    self.saveLog(" Non-pending events "+str(len(time_events))+"("+str(ev_round)+")"+str([i.getName()+"("+str(i.getID())+")" for i in time_events]))
                    event_progress = 0
                    for event in time_events:
                        self.saveLog(" Event "+str(event.getName())+"["+str(event.getID())+"]"+", ACTIVE? "+str(event.IsActive()))
                        if event.IsActive():  # completion of event
                            if event in self.getEventQueue()[self.time]:
                                event_progress+=1
                                try: 
                                    workmgr.commpleteSimEvent(event)
                                except Exception as e:
                                    self.saveLog("ERROR: complete non/pending-preemptable events "+str(e))  

                                event.setProgress(self.getTime(), "Completed")
                                self.completedEvents.append(event)
                                self.queue[self.time].remove(event) 
                        else:
                            if event.getEquipment() == None or event.getResource() == None:
                                self.saveLog(" event moved to pending.. "+str(self.time))
                                self.getEventQueue()["Pending"].append(event)
                                self.getEventQueue()[self.getTime()].remove(event) 
                                event.setProgress(self.getTime(), "Pending")
                            else:
                                try: 
                                    if  workmgr.startSimEvent(event):
                                        if event.getEventType().isPreemptable():
                                            if not event in self.getEventQueue()["Preemptables"]:
                                                #self.saveLog(keyword+": event "+event.print()+" moved to preemptables..")
                                                self.getEventQueue()["Preemptables"].append(event)
                                
        
                                    self.queue[self.time].remove(event)
                                except Exception as e:
                                    self.saveLog("ERROR: start non/pending-preemptable events "+str(e))  
                                
                            event_progress+=1 
               
    
                    time_events =[e for e in self.queue[self.time]] # scheduled/started events
                    ev_round+=1
        
        except Exception as e:
            self.saveLog("ERROR: non/pending-preemptable events "+str(e))        
            
     
        return
#############################################################################################################################          
    def ScheduleEvent(self,event):

        workmgr = self.getController().getWorkManager()
        
        self.saveLog(" scheduling "+event.print()+", preemptable "+str(event.getEventType().isPreemptable()))
        
        if event not in self.allEvents:
            self.allEvents.append(event)
            
        try: 
            if event.getEquipment() == None or event.getResource() == None:
                if not event in self.getEventQueue()["Pending"]:
                    self.saveLog(" in pending  "+event.print())
                    self.getEventQueue()["Pending"].append(event)
                return 
          
            if not self.getTime() in self.getEventQueue():
                self.getEventQueue()[self.getTime()] = []
            self.getEventQueue()[self.getTime()].append(event)
    
            if event.getEventType().isPreemptable():
                return

            if event.getSuccessor()!= None:
                if event.getSuccessor() in self.getEventQueue()["Preemptables"]:
                    self.getEventQueue()["Preemptables"].remove(event.getSuccessor())
                    self.saveLog(" preemptable successor event "+event.getSuccessor().getName()+str(event.getSuccessor().getID())+" removed from preemptables..")
                                                                
    
            # time is start time
            completion = workmgr.getCompletionTime(event,self.getTime())
    
            curr_shiftstart = (self.getTime()//self.getShiftMinutes())*self.getShiftMinutes()
            curr_shiftsend = curr_shiftstart+self.getShiftMinutes()*int((self.getTime()%self.getShiftMinutes())>0)
    
            
            if completion > curr_shiftsend: 
                # do not schedule event in this shift since it cannot finish..
                self.saveLog(" non-preemptable event "+event.getName()+"["+str(event.getID())+"]"+" cannot be completed in this shift, so scheduled to shiftend.")
                try:
                    event.getResource().setIdle(True) 
                    event.setResource(None)
                    if not curr_shiftsend+1 in self.getEventQueue():
                        self.getEventQueue()[curr_shiftsend+1] = []
                    self.getEventQueue()[curr_shiftsend+1].append(event)
                    if event in self.getEventQueue()[self.getTime()]:
                        self.getEventQueue()[self.getTime()].remove(event) 
                    
                    self.saveLog("REPORT: done.")
                except Exception as e:
                    self.saveLog("ERROR: In scheduling end of shift non-preemptable event "+event.print()+str(e))
               
                return
            else:
                self.saveLog(" "+event.print()+" completion time "+str(completion)+", event+proctime: "+str(self.getTime()+event.getProcessTime()))
                event.setCompletionTime(completion)
                        
                if not (completion) in self.getEventQueue():
                    self.getEventQueue()[completion] = []
                            
                if not event in self.getEventQueue()[completion]:
                    self.getEventQueue()[completion].append(event)  
        except Exception as e:
            self.saveLog("ERROR: in scheduling event "+str(e))
            

        self.saveLog("scheduled event,  "+event.print())
       
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

    def orderOverview(self):
        locationsGrouped = self.locationDf.groupby(["PN","Q","Deadline"]).agg({"LocationFrom": list, "LocationTo": list}).reset_index()
        
        operationsGrouped = self.processingDf.groupby(["PN", "Q", "Deadline"]).agg({"Status": list}).reset_index()
        
        merged = pd.merge(operationsGrouped, locationsGrouped, on=["PN", "Q", "Deadline"], how="left")

        self.orderOverviewDf = pd.merge(operationsGrouped, locationsGrouped, on=["PN", "Q", "Deadline"], how="left")
        
        self.orderOverviewDf["CycleStatus"] = self.orderOverviewDf.apply(check_cycle, axis=1)
        return    
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

#########################################################################################

def check_cycle(row):
    statuses = row["Status"]
    loc_from = row["LocationFrom"]
    loc_to = row["LocationTo"]

    # Case 1: Not all operations completed
    if not all(s == "Completed" for s in statuses):
        return "Problem — operations incomplete"

    # Case 2: No moves recorded
    if loc_from is None or loc_to is None:
        return "Problem — no logistics cycle"

    # Case 3: Empty move lists
    if len(loc_from) == 0 or len(loc_to) == 0:
        return "Problem — empty logistics cycle"

    # Case 4: Cycle must start at Central
    if loc_from[0] != "Central_Inventory":
        return "Problem — cycle did not start at Central"

    # Case 5: Cycle must end at Central
    if loc_to[-1] != "Central_Inventory":
        return "Problem — cycle did not end at Central"

    return "OK"
