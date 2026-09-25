##### import ipywidgets as widgets
from IPython.display import clear_output
from IPython import display
from ipywidgets import *
from datetime import timedelta,date,datetime
import matplotlib.pyplot as plt
import warnings
import seaborn as sns
import os
import pandas as pd
import warnings
import sys
import random
import numpy as np
import re
from pathlib import Path
from IPython.display import display, HTML
from matplotlib import colormaps
from matplotlib.patches import Patch
import plotly.graph_objects as go
import plotly.express as px
warnings.filterwarnings("ignore")



class VisualManager():

    def __init__(self):  

        self.InputText = True
        self.CalculateButton = None
        self.OperationMenu = None
        self.ResultText = None
        self.MyController = None
        self.mainmenu = None
        self.EventTypeBox = None
        self.MainBox = None
        self.RunBox = None
        self.OrderBox = None
        self.ProcessOutput = None
        self.LogOutput = None
        self.ProgressOutput = None
        self.Orders = None
        self.SimOrders = None
        self.WeeksDrop = None
        self.ResourceDrop = None
        self.title = None
        self.prodorders = None
        self.AllBoxes = []
        self.BoxMatches = dict()
        self.readbutton = None
        self.LogSelect = None
        self.ShowLogButton = None
        self.LogBox = None
        self.ResultBox = None
        self.runbutton = None
        self.RunProgress = None
        self.ResultInfoText = None
        self.FurtherText = None
        self.ShowDiagButton = None
        self.DiagSelect = None
        self.DiagBox = None
        self.demandorderlist = dict()
        self.milpmainbox = None
        self.milpresultbox = None
        self.milpprogress = None
        self.milprunbutton = None
        self.milpresults = None
        self.milpresultinfo = None
        self.milpdetails = None
        self.milporders = dict()
        self.MILPJobs = None
        self.MILPParamTxt = None
        self.availablebutton = None
        self.ResourceSave = None
        self.ResAlternatives = None
        self.AlternativeRemove = None
        self.AlternativeAdd = None
        self.ResourceDrop2 = None
        self.SelectedSchedule = None
        self.ScheduleOutput = None
        self.KPIArea = None
        self.WeeksMenu = None
        self.SuspendedEvents = dict()
        self.SelectedEventsDict = dict()
        self.simbox = None
        self.selectdestinationalg = None
        self.MILPNoJobs = 20
        self.Machines = []
        self.DataSets = dict()
        self.simdisplaycheck = None
        self.simsuspendcheck = None
        self.timestep = None
        self.timeapply = None
        self.EventIDs = None
        self.ResourceBox = None
        self.EventsApply = None
        self.selectevent = None
        self.selectedevents = None
        self.UseCaseMenu = None
        self.EventTypes = None
        self.EventCases = None
        self.CaseDecisions = None
        self.DecisionAlgs = None
        self.UseCaseBox = None
        self.ResourceMenu = None
        self.AllBoxes = []
        self.BoxMatches = dict()
        self.readbutton = None
        self.LogSelect = None
        self.ShowLogButton = None
        self.LogBox = None
        self.ResultBox = None
        self.runbutton = None
        self.RunProgress = None
        self.ResultInfoText = None
        self.FurtherText = None

        self.ShowDiagButton = None
        self.DiagSelect = None
        self.DiagBox = None
        self.demandorderlist = dict()  # key: list order, val: demandid

        self.milpmainbox = None
        self.milpresultbox = None
        self.milpprogress = None
        self.milprunbutton = None
        self.milpresults = None
        self.milpresultinfo = None
        self.milpdetails = None
        self.milporders = dict()
        self.MILPJobs = None
        self.MILPParamTxt = None
        self.availablebutton  = None
        self.ResourceSave = None
        self.ResAlternatives = None
        self.AlternativeRemove = None
        self.AlternativeAdd = None
        self.ResourceDrop2 = None
        self.SelectedSchedule = None
        self.ScheduleOutput = None
        self.KPIArea = None
        self.WeeksMenu = None
        self.SuspendedEvents = dict()
        self.SelectedEventsDict = dict()

        self.simbox = None
        self.selectdestinationalg = None
        
        self.MILPNoJobs = 20

        self.Machines = []
        self.DataSets = dict()
        self.simdisplaycheck = None
        self.simsuspendcheck = None
        self.timestep = None
        self.timeapply = None
        self.EventIDs = None
        self.ResourceBox = None
        self.EventsApply = None
        self.selectevent = None
        self.selectedevents = None

        self.UseCaseMenu = None
        self.EventTypes = None
        self.EventCases = None
        self.CaseDecisions = None
        self.DecisionAlgs = None
        self.UseCaseBox = None
        self.ResourceMenu = None
        self.DecisionAlgorithms = None

    def getDecisionAlgorithms(self):
        return self.DecisionAlgorithms
    def setDecisionAlgorithms(self,dg):
        self.DecisionAlgorithms = dg
        return


    def setResourceMenu(self,fg):
        self.ResourceMenu =  fg
        return
    def getResourceMenu(self):
        return self.ResourceMenu 

    def setCombinedLastDay(self,dt):
        self.CombinedLastDay = dt
        return
    def getCombinedLastDay(self):
        return self.CombinedLastDay

    def setCombinedMachineFilter(self,dp):
        self.CombinedMachineFilter = dp
        return
    def getCombinedMachineFilter(self):
        return self.CombinedMachineFilter

    def setCombinedOperatorFilter(self,dp):
        self.CombinedOperatorFilter = dp
        return
    def getCombinedOperatorFilter(self):
        return self.CombinedOperatorFilter

    def setCombinedProductFilter(self,dp):
        self.CombinedProductFilter = dp
        return
    def getCombinedProductFilter(self):
        return self.CombinedProductFilter

    def setCombinedFilterBox(self,bx):
        self.CombinedFilterBox = bx
        return
    def getCombinedFilterBox(self):
        return self.CombinedFilterBox


    def setUseCaseMenu(self,df):
        self.UseCaseMenu = df
        return
        
    def setEventTypes(self,df):
        self.EventTypes = df
        return

    def setEventCases(self,df):
        self.EventCases = df
        return
        
    def setCaseDecisions(self,df):
        self.CaseDecisions = df
        return
    def setDecisionAlgs(self,df):
        self.DecisionAlgs = df
        return
       
    def setUseCaseBox(self,df):
        self.UseCaseBox = df
        return


    def getUseCaseMenu(self):
        return self.UseCaseMenu
        
        
    def getEventTypes(self):
        return self.EventTypes
        

    def getEventCases(self):
        return self.EventCases
        
    def getCaseDecisions(self):
        return self.CaseDecisions

    def getDecisionAlgs(self):
        return self.DecisionAlgs
       
    def getUseCaseBox(self):
        return self.UseCaseBox
        


    def setSelectedEvents(self,sl):
        self.selectedevents = sl
        return
        
    def getSelectedEvents(self):
        return self.selectedevents
        
    def setSelectEvent(self,bt):
        self.selectevent = bt
        return

    def getSelectEvent(self):
        return self.selectevent
        

    def getSelectedEventsDict(self):
        return self.SelectedEventsDict

    def getSuspendedEvents(self):
        return self.SuspendedEvents
        
    def setEventsApply(self,evid):
        self.EventsApply = evid
        return 

    def getEventsApply(self):
        return self.EventsApply 

        

    def setEventIDs(self,evid):
        self.EventIDs = evid
        return 

    def getEventIDs(self):
        return self.EventIDs 
        

    def setTimeApply(self,bt):
        self.timeapply = bt
        return

    def getTimeApply(self):
        return self.timeapply

    def setSimDisplayCheck(self,chk):
        self.simdisplaycheck = chk
        return
    def getSimDisplayCheck(self):
        return self.simdisplaycheck

    def setTimeStep(self,chk):
        self.timestep = chk
        return
    def getTimeStep(self):
        return self.timestep


    def setSimSuspendCheck(self,chk):
        self.simsuspendcheck = chk
        return
    def getSimSuspendCheck(self):
        return self.simsuspendcheck
    

    def setSimBox(self,bx):
        self.simbox = bx
        return
    def getSimBox(self):
        return self.simbox 

    
    def setSelectDestinationAlg(self,bx):
        self.selectdestinationalg = bx
        return
    def getSelectDestinationAlg(self):
        return self.selectdestinationalg 
        
        
    def setWeeksMenu(self,dp):
        self.WeeksMenu = dp
        return

    def getWeeksMenu(self):
        return self.WeeksMenu
        
    def getKPIArea(self):
        return self.KPIArea

    def setKPIArea(self,dt):
        self.KPIArea = dt
        return 

    def setScheduleOutput(self,dt):
        self.ScheduleOutput = dt
        return
    def getScheduleOutput(self):
        return self.ScheduleOutput

    def setSelectedSchedule(self,dt):
        self.SelectedSchedule = dt
        return
    def getSelectedSchedule(self):
        return self.SelectedSchedule


    def setAlternativeAdd(self,bt):
        self.AlternativeAdd = bt
        return

    def getAlternativeAdd(self):
        return self.AlternativeAdd

    def setAlternativeRemove(self,bt):
        self.AlternativeRemove = bt
        return

    def getAlternativeRemove(self):
        return self.AlternativeRemove

    def setResAlternatives(self,bt):
        self.ResAlternatives = bt
        return

    def getResAlternatives(self):
        return self.ResAlternatives



    def setResourceSave(self,bt):
        self.ResourceSave = bt
        return

    def getResourceSave(self):
        return self.ResourceSave

        

    def getAvailabilityCheck(self):
        return self.availablebutton 

    def setAvailabilityCheck(self,bttn):
        self.availablebutton = bttn
        return 

    

    def getMachines(self):
        return self.Machines

    def getDataSets(self):
        return self.DataSets

    def setResourceDrop(self,dr):
        self.ResourceDrop = dr
        return

    def getResourceDrop(self):
        return self.ResourceDrop

    def setResourceDrop2(self,dr):
        self.ResourceDrop2= dr
        return

    def getResourceDrop2(self):
        return self.ResourceDrop2
        

    def getMILPJobs(self):
        return self.MILPJobs

    def setMILPJobs(self,myjb):
        self.MILPJobs = myjb
        return 

    def setMILPParamTxt(self,txt):
        self.MILPParamTxt = txt
        return

    def getMILPParamTxt(self):
        return self.MILPParamTxt
        
        

    def setResourceBox(self,myres):
        self.ResourceBox = myres
        return
    def getResourceBox(self):
        return self.ResourceBox

    def setmilpdetails(self,myitem):
       self.milpdetails = myitem
       return 
    def getmilpdetails(self):
       return self.milpdetails

    def setMILPResultInfo(self,myitem):
       self.milpresultinfo = myitem
       return 
    def getMILPResultInfo(self):
       return self.milpresultinfo

    def setmilpresults(self,myitem):
       self.milpresults = myitem
       return 
    def getmilpresults(self):
       return self.milpresults
    
    def setmilpprogress(self,myitem):
       self.milpprogress = myitem
       return 
    def getmilpprogress(self):
       return self.milpprogress

    def setmilprunbutton(self,myitem):
       self.milprunbutton = myitem
       return 
    def getmilprunbutton(self):
       return self.milprunbutton

    def setmilpmainbox(self,myitem):
       self.milpmainbox = myitem
       return 
    def getmilpmainbox(self):
       return self.milpmainbox

    
    def setmilpresultbox(self,myitem):
       self.milpresultbox = myitem
       return 
    def getmilpresultbox(self):
       return self.milpresultbox
        
        
        
########### get-set functions ########### 

    def setFurtherText(self,myitem):
       self.FurtherText = myitem
       return 
    def getFurtherText(self):
       return self.FurtherText

    def setDiagBox(self,myitem):
       self.DiagBox = myitem
       return 
    def getDiagBox(self):
       return self.DiagBox


    def setShowDiagButton(self,myitem):
       self.ShowDiagButton = myitem
       return 
    def getShowDiagButton(self):
       return self.ShowDiagButton

    def setDiagSelect(self,myitem):
       self.DiagSelect = myitem
       return 
    def getDiagSelect(self):
       return self.DiagSelect

    def setResultInfoText(self,myitem):
       self.ResultInfoText = myitem
       return 
    def getResultInfoText(self):
       return self.ResultInfoText

    def setShowLogButton(self,myitem):
       self.ShowLogButton = myitem
       return 
    def getShowLogButton(self):
       return self.ShowLogButton

    def setRunProgress(self,myitem):
       self.RunProgress = myitem
       return 
    def getRunProgress(self):
       return self.RunProgress


    def setResultBox(self,myitem):
       self.ResultBox = myitem
       return 
    def getResultBox(self):
       return self.ResultBox


    def setLogBox(self,myitem):
       self.LogBox = myitem
       return 
    def getLogBox(self):
       return self.LogBox
    
    

    def setLogSelect(self,myitem):
       self.LogSelect = myitem
       return 
    def getLogSelect(self):
       return self.LogSelect

    def getAllBoxes(self):
        return self.AllBoxes
        
    def setInputText(self,myitem):
       self.InputText = myitem
       return 
    def getInputText(self):
       return self.InputText

    def setOrders(self,myitem):
       self.Orders = myitem
       return 
    def getOrders(self):
       return self.Orders

    def setProdOrders(self,myitem):
       self.prodorders = myitem
       return 
    def getProdOrders(self):
       return self.prodorders


    def setReadButton(self,myitem):
       self.readbutton = myitem
       return 
    def getReadButton(self):
       return self.readbutton
        

    def setTitle(self,myitem):
       self.title = myitem
       return 
    def getTitle(self):
       return self.title

    
    def setWeeksDrop(self,myitem):
       self.WeeksDrop = myitem
       return 
    def getWeeksDrop(self):
       return self.WeeksDrop
    

    def setSimOrders(self,myitem):
       self.SimOrders = myitem
       return 
    def getSimOrders(self):
       return self.SimOrders


    def setEventTypeBox(self,myitem):
       self.EventTypeBox = myitem
       return 
    def getEventTypeBox(self):
       return self.EventTypeBox

    def setOrderBox(self,myitem):
       self.OrderBox = myitem
       return 
    def getOrderBox(self):
       return self.OrderBox



        

    def setMainBox(self,myitem):
       self.MainBox = myitem
       return 
    def getMainBox(self):
       return self.MainBox


    def setRunBox(self,myitem):
       self.RunBox = myitem
       return 
    def getRunBox(self):
       return self.RunBox

          

    def setMainmenu(self,myitem):
       self.mainmenu = myitem
       return 
    def getMainmenu(self):
       return self.mainmenu
          
    def setCalculateButton(self,myitem):
       self.CalculateButton = myitem
       return 
    def getCalculateButton(self):
       return self.CalculateButton

    def setCalculateButton(self,myitem):
       self.CalculateButton = myitem
       return 
    def getCalculateButton(self):
       return self.CalculateButton

    def setOperationMenu(self,myitem):
       self.OperationMenu = myitem
       return 
    def getOperationMenu(self):
       return self.OperationMenu

    def setResultText(self,myitem):
       self.ResultText= myitem
       return 
    def getResultText(self):
       return self.ResultText

    def setController(self,myitem):
       self.MyController = myitem
       return 
    def getController(self):
       return self.MyController

        

        
########### get-set functions ###########    

    def MakeOperation(self,event):

        inputvals = self.getInputText().value
        numbers = [int(x)  for x in inputvals.split(",")]
        result = self.getController().ExecuteOperation(str(self.getOperationMenu().value),numbers)

        self.getResultText().value = str(result)
        
        return 

#############################################################################################################################################    
    def RunSim(self,event):

 
        self.runbutton.disabled = True #not self.getController().getSimulator().isDisplayMode()
        
        self.getController().getSimulator().RunSimulation(self.getController().getWorkManager())
        

        if self.getController().getSimulator().getTime() == self.getController().getSimulator().getTimeLimit():

            self.demandorderlist.clear()
            self.demandorderlist = dict(enumerate(self.getController().getWorkManager().getDemands().keys()))
          
            self.getFurtherText().options = [self.getController().getWorkManager().getDemands()[x].getFinalProduct().getPN() for x in self.demandorderlist.values()]
        else:
            self.getController().getSimulator().saveLog("REPORT: suspend mode: "+str(self.getController().getSimulator().isSuspendMode())) 
            if self.getController().getSimulator().isSuspendMode():

                self.getSuspendedEvents().clear()
                self.getSelectedEventsDict().clear()
              
                for e in self.getController().getSimulator().getEventQueue()["Pending"]:
                    self.getSuspendedEvents()[e.getName()+"("+str(e.getID())+") - "+"[Pending]"] = e

                for schtime,events in self.getController().getSimulator().getEventQueue().items():
                    if schtime == "Pending": 
                        continue
                    if schtime < self.getController().getSimulator().getTime():
                        continue
                    else:
                        for e in events:
                            self.getSuspendedEvents()[e.getName()+"("+str(e.getID())+") - "+"["+str(schtime)+"]"] = e
                self.getEventIDs().options = [evstr for evstr,e in self.getSuspendedEvents().items()]
                self.getSelectedEvents().options = []
                    
                self.runbutton.description = "Run Simulation ("+str(self.getController().getSimulator().getTime())+")"
                self.runbutton.disabled = False 

        return 
#############################################################################################################################################    
    
    def ReadInput(self,event):

        try: 
            selectedOrders = self.getController().getWorkManager().createInstance()
        except Exception as e:
            self.getController().getSimulator().saveLog("ERROR: in reading input "+str(e))  
           
        
        orderopts = []
        for prodorder in selectedOrders:
            orderopts.append("PN: "+prodorder.getFinalProduct().getPN()+", Q: "+str(len(prodorder.getItems()))+", Deadline: "+str(prodorder.getDeadline()))

        self.getProdOrders().options = orderopts
        
        self.getReadButton().disabled = True
        self.getOrders().disabled = True
        self.getUseCaseMenu().disabled = True

        
            


        self.getResourceDrop().options = [ res.getName() for res in self.getController().getWorkManager().getResources()]
        self.getResourceDrop2().options = [ res.getName() for res in self.getController().getWorkManager().getResources() if res.getType() == "Machine"]

        self.getResourceDrop().value = self.getResourceDrop().options[0]
        self.getResourceDrop2().value = self.getResourceDrop2().options[0]

        return 

        
    def setDropSimOrders(self,event):

        if self.getController().getWorkManager()!= None:
            self.getController().getWorkManager().setNoOrders(self.getOrders().value)
    
            self.getTitle().value = 'TimeLimit: '+str(self.getController().getSimulator().getTimelimit())+", Orders: "+str(self.getController().getWorkManager().getNoOrders())
        return  

    def setDropSimWeeks(self,event):

        if self.getController().getWorkManager()!= None:
        
            self.getController().getSimulator().setRunWeeks(self.getWeeksDrop().value)
            self.getTitle().value = 'TimeLimit: '+str(self.getController().getSimulator().getTimelimit())+", Orders: "+str(self.getController().getWorkManager().getNoOrders())+", Use Case: "+self.getController().getUseCase()
        
        return 

    def ShowDiag(self,event):
        # Here feasibility checks

        self.getDiagSelect().options = ["Feasibility"]
        

        return
    

    def ShowLog(self,event):

        self.getShowLogButton().disabled = True

      
        #allinfo = []
        
        #for time,infolist in self.getController().getSimulator().getMyLog().items():

        #    for info in infolist:
        #        allinfo.append(str(time)+": "+str(info))

       

        #self.getLogSelect().options = allinfo

        return

    def menu_click(self,event):  

        menuitem = self.getMainmenu().value

        #self.getController().getSimulator().saveLog("REPORT: menu item "+menuitem+" in boxmatches? "+str(menuitem in self.BoxMatches))

        if menuitem in self.BoxMatches:
            self.ViewBoxes(self.BoxMatches[menuitem])
            if menuitem == "Schedules":
                if len(self.getController().getWorkManager().getDemands()) > 0:
                    if len(self.getController().getWorkManager().getMySchedules()) == 0:
                        self.getController().getWorkManager().ReadSchedules()
    
                        self.getResultText().options = [str(sch.getDataExportDate().date())+"_"+sch.getAlgorithmName()+"_"+str(sch.getConstuctionDate().date()) for sch in self.getController().getWorkManager().getMySchedules()]

                
            

        return

    def ViewBoxes(self,boxtoshow):

        for box in self.getAllBoxes():
            if box == boxtoshow:
                box.layout.display = 'block'
                box.layout.visibility = 'visible'
            else:
                box.layout.visibility = 'hidden'
                box.layout.display = 'none'

        return 

    def ViewResults(self,event):

        #getRes_process_df(self):
        #getDemand_process_df(self):

        
        if self.getMainmenu().value == "Schedules":
            for sch in self.getController().getWorkManager().getMySchedules():
                if self.getResultText().value == str(sch.getDataExportDate().date())+"_"+sch.getAlgorithmName()+"_"+str(sch.getConstuctionDate().date()):
                    self.setSelectedSchedule(sch)
                    self.getController().getSimulator().saveLog("REPORT: selected schedule input date: "+str(sch.getDataExportDate().date())) 
                    self.getController().getSimulator().saveLog("REPORT: selected schedule algorithm : "+sch.getAlgorithmName()) 
                    self.getController().getSimulator().saveLog("REPORT: selected schedule construction date: "+str(sch.getConstuctionDate().date())) 
                    break
            if self.getSelectedSchedule()!=None:
                
                inpdate = str(self.getSelectedSchedule().getDataExportDate().date())
                algname = self.getSelectedSchedule().getAlgorithmName()
                consdate = str(self.getSelectedSchedule().getConstuctionDate().date())

                self.getKPIArea().value = "Completed demands: "+str(self.getSelectedSchedule().getCompletedDemands())+"/ "+str(len(self.getSelectedSchedule().getDemands()))+ "\n"
                self.getKPIArea().value += "Tardy demands: "+str(self.getSelectedSchedule().getTardyDemands())+"/ "+str(self.getSelectedSchedule().getCompletedDemands())+ "\n"

                self.getWeeksMenu().options = [str(d.date()) for d in self.getSelectedSchedule().getMyDays()]
                
                #self.showMachineSchedule(self.getSelectedSchedule().getMinDate(),self.getSelectedSchedule().getMinDate()+timedelta(days =5))
                  

        return 

####################################################################################################################################   
    def showMachineSchedule(self,mindate,maxdate):
        try: 

            pncolors = dict() 
            barcolors = ['tab:orange','tab:blue','tab:red','tab:green','tab:brown','tab:gray','tab:olive','tab:cyan','tab:purple']
            colorid = 0
            currentday = mindate
            currentday = currentday.replace(hour=0, minute=0, second=0, microsecond=0)

         
    
            with self.getScheduleOutput():
                clear_output()
                self.getController().getSimulator().saveLog("REPORT: Output started, current day: "+str(currentday)) 


                while currentday <= maxdate :

                    if currentday.weekday() >= 5: 
                        currentday = currentday+timedelta(minutes = 24*60)
                        continue
                        

                    if not currentday in self.getSelectedSchedule().getShiftSchedules():
                        self.getSelectedSchedule().findMachineShift(currentday,self.getController().getWorkManager())

                    self.getController().getSimulator().saveLog("REPORT: current day: "+str(currentday)+" in shedules? "+str(currentday in self.getSelectedSchedule().getShiftSchedules())) 
    

                    if currentday in self.getSelectedSchedule().getShiftSchedules():
                    
                        for shftno,shfthours in self.getSelectedSchedule().getShiftsInfo().items():
        
                            fig, gantts = plt.subplots(figsize=(23, 12),tight_layout=True)
                            gnt_no = 0; gantt_hrs = [x for x in shfthours]
                                
                            
                            shiftstart = currentday+timedelta(minutes = shfthours[0]*60);
                            shiftend = currentday+timedelta(minutes = shfthours[-1]*60+59);
                            x_labels = [datetime.strptime(str(currentday+timedelta(minutes = hr*60)),"%Y-%m-%d %H:%M:%S") for hr in gantt_hrs]
        
                            machinejobs = dict() 

                          
                            for mach,mach_df in self.getSelectedSchedule().getShiftSchedules()[currentday][shftno].items():
           
                                if not mach in machinejobs:
                                    machinejobs[mach] = []
        
                                for i,r in mach_df.iterrows():
                                    if (r["Work Orders/Start"] < shiftstart) & (r["Work Orders/End"] > shiftend):
                                        if shftno == 3:
                                            if not mach.IsAutomated():
                                                continue
                                        
                                    job_shft_start = max(r["Work Orders/Start"],shiftstart)
                                    job_shft_end= min(r["Work Orders/End"],shiftend)
                      
                                    jobstart = (job_shft_start -  shiftstart).total_seconds() / 3600; 
                                    jobend= (job_shft_end -  shiftstart).total_seconds() / 3600
                                    jobstr = mach.getName()+": "+str(r["Product"])+", Pr.ID: "+str(r["Product/ID"])+", Q: "+str(r["Quantity To Produce"])+", Ref: "+str(r["Reference"])
        
                                    if not r["Product"] in pncolors:
                                        pncolors[r["Product"]]  = barcolors[colorid]
                                        colorid+=1; colorid = 0 if colorid > len(barcolors)-1 else colorid
                                        
                                    machinejobs[mach].append(((jobstr,r["Product"]),(jobstart,jobend)))
        
                            gantts.set_ylim(0,10*(len(machinejobs)+1))       
                                    
                                # Setting X-axis limits
                            gantts.set_xlim(0,len(gantt_hrs))
                    
                                # Setting ticks on y-axis
                            gantts.set_yticks([10*x for x in range(len(machinejobs)+1)])
                            gantts.set_xticks([x for x in range(len(gantt_hrs))]) # hours per day
        
                                
                                # Labelling tickes of y-axis
                            y_labels = ['']
                            for mach,jobs in machinejobs.items():
                                y_labels.append(mach.getName())
    
                            self.getController().getSimulator().saveLog("REPORT: y_labels: "+str(y_labels)) 
                            self.getController().getSimulator().saveLog("REPORT: x_labels: "+str(x_labels)) 
                                
                            gantts.set_yticklabels(y_labels)
                            gantts.set_xticklabels(x_labels)
        
                                                
                                # Setting labels for x-axis and y-axis
                            gantts.set_xlabel('Time')
                            gantts.set_ylabel('Jobs of machines in shift  ')
                                # Setting graph attribute
                            gantts.grid(True)
        
                            machord = 1
        
                            for mach,jobs in machinejobs.items():
                                for jobtuple in jobs:
                                    gantts.broken_barh([(jobtuple[1][0],(jobtuple[1][1]-jobtuple[1][0]))], (10*machord-2.5, 5), facecolors = pncolors[jobtuple[0][1]],label=jobtuple[0][0],)
            
                                machord+=1
        
                            gantts.legend( bbox_to_anchor=(0, 1),loc='lower left', fontsize='small')
                            gantts.tick_params(rotation=45)
                            plt.show()
                                
                    currentday = currentday+timedelta(minutes = 24*60)
                
                    self.getController().getSimulator().saveLog("REPORT: Output started, current day: "+str(currentday)) 
 
        
        except Exception as e:
            self.getController().getSimulator().saveLog("ERROR: in showing schedule "+str(e))
    


        return 
    def showOperatorSchedule(self,scheduleday):

        # Read the simulation event file associated with the selected schedule.
        try:
            # Load all completed simulation events from the csv.
            simevent_df = self.getController().getWorkManager().getDataManager().ReadSimulationEventData(self.getSelectedSchedule())
            # Normalize the requested day to midnight.
            day_start = pd.Timestamp(scheduleday).normalize()
            # Define the exclusive end of the requested day.
            day_end = day_start + timedelta(days=1)
            # Strip whitespace before identifying human resources.
            resource_names = simevent_df["Resource"].astype(str).str.strip()
            # Keep only operators and manual workers.
            operator_df = simevent_df[
                simevent_df["Resource"].notna()
                & resource_names.str.contains(
                    r"operator|manual worker",
                    case=False,
                    regex=True,
                )
            ].copy()

            # Store one color for each event type.
            event_colors = dict()
            # Create a categorical palette for event types.
            color_palette = list(sns.color_palette("tab10").as_hex())
            # Store all intervals overlapping the selected day.
            intervals = []

            # Process each selected human-resource event.
            for _, event_row in operator_df.iterrows():
                # Read the event's serialized execution intervals.
                event_steps = event_row.get("ProgressSteps")
                # Prepare the parsed interval list.
                parsed_steps = []

                # Parse ProgressSteps when available.
                if pd.notna(event_steps) and str(event_steps).strip():
                    # Split multiple intervals at the '~' separator.
                    for step in str(event_steps).split("~"):
                        # Match complete start and end timestamps.
                        step_match = re.match(
                            r"^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})-"
                            r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]$",
                            step.strip(),
                        )
                        # Skip malformed intervals.
                        if step_match is None:
                            continue
                        # Extract the timestamp strings.
                        step_start, step_end = step_match.groups()
                        # Convert timestamps to datetime values.
                        parsed_steps.append(
                            (pd.to_datetime(step_start), pd.to_datetime(step_end))
                        )

                # Fall back to the overall event timestamps if necessary.
                if not parsed_steps:
                    fallback_start = pd.to_datetime(
                        event_row.get("Work Orders/Start"), errors="coerce"
                    )
                    fallback_end = pd.to_datetime(
                        event_row.get("Work Orders/End"), errors="coerce"
                    )
                    if pd.notna(fallback_start) and pd.notna(fallback_end):
                        parsed_steps.append((fallback_start, fallback_end))

                # Use the event name as the visual category.
                event_name = str(event_row.get("EventName", "Unknown event"))
                if event_name not in event_colors:
                    event_colors[event_name] = color_palette[
                        len(event_colors) % len(color_palette)
                    ]

                # Add every valid event segment to the chart data.
                for interval_start, interval_end in parsed_steps:
                    if interval_end <= day_start or interval_start >= day_end:
                        continue

                    interval_start = max(interval_start, day_start)
                    interval_end = min(interval_end, day_end)
                    if interval_end <= interval_start:
                        continue

                    intervals.append({
                        "Operator": str(event_row["Resource"]).strip(),
                        "Event": event_name,
                        "EventID": event_row.get("EventID", "-"),
                        "Start": interval_start,
                        "End": interval_end,
                        "Equipment": event_row.get("Equipment", "-"),
                        "Location": event_row.get("Location", "-"),
                        "Product": event_row.get("Product", "-"),
                        "Reference": event_row.get("Reference", "-"),
                    })
            
            # Render the result inside the notebook output widget.
            with self.getScheduleOutput():
                # Clear the previously displayed schedule.
                clear_output()

                # Handle days without matching activity.
                if not intervals:
                    display("No operator activity found for "+str(day_start.date()))
                    return

                # Preserve the first-seen resource ordering.
                operator_names = list(dict.fromkeys(
                    interval["Operator"] for interval in intervals
                ))
                # Assign each resource a y-axis position.
                operator_positions = {
                    operator: position
                    for position, operator in enumerate(operator_names)
                }
                # Scale the figure height with the number of resources.
                figure_height = max(5, 1.2 * len(operator_names))
                # Create the Gantt chart.
                fig, axes = plt.subplots(
                    figsize=(23, figure_height),
                    tight_layout=True
                )

                # Draw each activity interval.
                for interval in intervals:
                    # Convert the interval start to hours after midnight.
                    start_hour = (
                        interval["Start"] - day_start
                    ).total_seconds() / 3600
                    # Convert the interval length to hours.
                    duration_hours = (
                        interval["End"] - interval["Start"]
                    ).total_seconds() / 3600
                    # Find the resource row for this activity.
                    operator_position = operator_positions[interval["Operator"]]
                    # Build the activity detail label.
                    label = (
                        interval["Event"]
                        + " (ID: " + str(interval["EventID"])
                        + ", equipment: " + str(interval["Equipment"])
                        + ", location: " + str(interval["Location"])
                        + ", product: " + str(interval["Product"])
                        + ", ref: " + str(interval["Reference"])
                        + ")"
                    )
                    # Draw the activity bar on the resource row.
                    axes.broken_barh(
                        [(start_hour, duration_hours)],
                        (operator_position - 0.35, 0.7),
                        facecolors=event_colors[interval["Event"]],
                        edgecolors="black",
                        linewidth=0.5,
                        label=label,
                    )

                # Show the complete 24-hour day.
                axes.set_xlim(0, 24)
                # Keep the resource rows centered in the plot.
                axes.set_ylim(-0.75, len(operator_names) - 0.25)
                # Place one x-axis tick per hour.
                axes.set_xticks(range(25))
                # Format x-axis ticks as clock times.
                axes.set_xticklabels([
                    (day_start + timedelta(hours=hour)).strftime("%H:%M")
                    for hour in range(25)
                ])
                # Place one y-axis tick per resource.
                axes.set_yticks(range(len(operator_names)))
                # Label rows with operator and manual-worker names.
                axes.set_yticklabels(operator_names)
                # Label the timeline axis.
                axes.set_xlabel("Time")
                # Label the human-resource axis.
                axes.set_ylabel("Operators and manual workers")
                # Add the selected day to the title.
                axes.set_title("Operator schedule: " + str(day_start.date()))
                # Add vertical guides for the timeline.
                axes.grid(True, axis="x")

                # Build one legend entry per event type.
                legend_handles = [
                    Patch(facecolor=color, edgecolor="black", label=event_name)
                    for event_name, color in event_colors.items()
                    if any(interval["Event"] == event_name for interval in intervals)
                ]
                # Place the legend beside the chart.
                axes.legend(
                    handles=legend_handles,
                    bbox_to_anchor=(1.01, 1),
                    loc="upper left",
                    fontsize="small",
                )
                # Rotate clock labels for readability.
                axes.tick_params(axis="x", rotation=45)
                # Display the finished chart.
                plt.show()

            # Log visualization errors without breaking the dashboard.
        except Exception as e:
            self.getController().getSimulator().saveLog("ERROR: in showing operator schedule "+str(e))


        # This callback updates the output widget and returns no value.
        return

    def _updateDropdownOptions(self,dropdown,options):
        # Refresh a filter dropdown's options while keeping its selection when still valid.
        current_value = dropdown.value
        dropdown.options = options
        dropdown.value = current_value if current_value in options else options[0]
        return

    def _parseEventIntervals(self,event_row):
        """Return every valid execution interval recorded for one event."""
        # An event may contain several disjoint execution intervals in ProgressSteps.
        # Return every interval separately so gaps in an operator's work remain visible.
        parsed_steps = []
        event_steps = event_row.get("ProgressSteps")

        if pd.notna(event_steps) and str(event_steps).strip():
            for step in str(event_steps).split("~"):
                # Each step has the form [start-end]. Invalid steps are ignored.
                step_match = re.match(
                    r"^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})-"
                    r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]$",
                    step.strip(),
                )
                if step_match is None:
                    continue
                step_start, step_end = step_match.groups()
                parsed_steps.append((pd.to_datetime(step_start), pd.to_datetime(step_end)))

        if not parsed_steps:
            # Older or incomplete rows may not have ProgressSteps. Use their
            # work-order timestamps as a single interval when both are valid.
            fallback_start = pd.to_datetime(event_row.get("Work Orders/Start"), errors="coerce")
            fallback_end = pd.to_datetime(event_row.get("Work Orders/End"), errors="coerce")
            if pd.notna(fallback_start) and pd.notna(fallback_end):
                parsed_steps.append((fallback_start, fallback_end))

        return parsed_steps

    def showCombinedSchedule(self,scheduleday):
        """Display active machine jobs and operator activity for one calendar day."""

        try:
            selected_schedule = self.getSelectedSchedule()
            # The plan controls machine bars; the event log controls operator activity.
            simevent_df = self.getController().getWorkManager().getDataManager().ReadSimulationEventData(selected_schedule)
            schedule_df = selected_schedule.DataFrame.copy()
            day_start = pd.Timestamp(scheduleday).normalize()
            day_end = day_start + timedelta(days=1)

            # Normalize the schedule fields used by the filters and timeline.
            schedule_df["Work Orders/Start"] = pd.to_datetime(schedule_df["Work Orders/Start"], errors="coerce")
            schedule_df["Work Orders/End"] = pd.to_datetime(schedule_df["Work Orders/End"], errors="coerce")
            schedule_df["Work Orders/Status"] = schedule_df["Work Orders/Status"].fillna("").astype(str).str.strip()
            schedule_df["Processing Machine"] = schedule_df["Processing Machine"].fillna("").astype(str).str.strip()

            # Only jobs that are currently planned or in progress belong in this view.
            active_statuses = {"Scheduled", "In Progress"}
            valid_machine = ~schedule_df["Processing Machine"].isin({"", "-", "nan", "None"})
            active_job = schedule_df["Work Orders/Status"].isin(active_statuses)
            overlaps_day = (schedule_df["Work Orders/End"] > day_start) & (schedule_df["Work Orders/Start"] < day_end)
            machine_df = schedule_df[valid_machine & active_job & overlaps_day].copy()

            with self.getScheduleOutput():
                clear_output()

                if machine_df.empty:
                    display("No active machine jobs found for "+str(day_start.date()))
                    return

                # Clip jobs at the selected day's boundaries before converting to hours.
                machine_df["Start"] = machine_df["Work Orders/Start"].clip(lower=day_start)
                machine_df["End"] = machine_df["Work Orders/End"].clip(upper=day_end)
                machine_df["StartHour"] = (machine_df["Start"] - day_start).dt.total_seconds()/3600
                machine_df["DurationHours"] = (machine_df["End"] - machine_df["Start"]).dt.total_seconds()/3600
                machine_df = machine_df[machine_df["DurationHours"] > 0].copy()

                machine_names = sorted(machine_df["Processing Machine"].unique())
                product_names = sorted(p for p in machine_df["Product"].unique() if pd.notna(p))

                # Keep operator events separate from the machine plan. This data is
                # later used to draw the human activity lines on the same timeline.
                operator_resource_names = simevent_df["Resource"].astype(str).str.strip()
                event_names = simevent_df["EventName"].fillna("").astype(str).str.strip()
                operator_event_df = simevent_df[
                    simevent_df["Resource"].notna()
                    & operator_resource_names.str.contains(
                        r"operator|manual worker",
                        case=False,
                        regex=True,
                    )
                    & event_names.ne("Trailer Transport")
                ].copy()
                self._updateDropdownOptions(self.getCombinedMachineFilter(), ["All"]+machine_names)
                operator_names = sorted(operator_resource_names[operator_event_df.index].unique())
                self._updateDropdownOptions(self.getCombinedOperatorFilter(), ["All"]+operator_names)
                self._updateDropdownOptions(self.getCombinedProductFilter(), ["All"]+product_names)

                # Apply the dashboard filters independently to machines and operators.
                machine_sel = self.getCombinedMachineFilter().value
                operator_sel = self.getCombinedOperatorFilter().value
                product_sel = self.getCombinedProductFilter().value
                if machine_sel != "All":
                    machine_df = machine_df[machine_df["Processing Machine"] == machine_sel]
                if operator_sel != "All":
                    operator_event_df = operator_event_df[
                        operator_resource_names[operator_event_df.index] == operator_sel
                    ]
                if product_sel != "All":
                    machine_df = machine_df[machine_df["Product"] == product_sel]

                if machine_df.empty:
                    display("No active machine jobs match the selected filters for "+str(day_start.date()))
                    return

                # Events that do not map directly to a machine receive stable rows.
                central_row = "Central Buffer / Inventory"
                other_row = "Off-machine / Other"

                def location_to_row(location):
                    location = str(location).strip()
                    if location.startswith("CentralBuffer"):
                        return central_row
                    if location.endswith("_Location"):
                        location = location[:-len("_Location")]
                    return location if location in machine_names else other_row

                # Expand every ProgressSteps interval into one drawable action segment.
                operator_intervals = []
                for _, event_row in operator_event_df.iterrows():
                    for interval_start, interval_end in self._parseEventIntervals(event_row):
                        if interval_end <= day_start or interval_start >= day_end:
                            continue
                        interval_start = max(interval_start, day_start)
                        interval_end = min(interval_end, day_end)
                        if interval_end <= interval_start:
                            continue
                        operator_intervals.append({
                            "Operator": str(event_row["Resource"]).strip(),
                            "Event": str(event_row.get("EventName", "Unknown event")),
                            "EventID": event_row.get("EventID", "-"),
                            "Start": interval_start,
                            "End": interval_end,
                            "Row": location_to_row(event_row.get("Location", "-")),
                            "Location": event_row.get("Location", "-"),
                            "Equipment": event_row.get("Equipment", "-"),
                            "Product": event_row.get("Product", "-"),
                            "Reference": event_row.get("Reference", "-"),
                        })
                operator_intervals.sort(key=lambda interval: (interval["Operator"], interval["Start"]))

                # Use one stable color per product so the same product is recognizable.
                product_color_palette = px.colors.qualitative.Plotly
                product_color_map = {}
                for product in machine_df["Product"].unique():
                    product_color_map[product] = product_color_palette[len(product_color_map) % len(product_color_palette)]

                # Machine bars contain the requested planning information in their tooltips.
                hover_texts = []
                for _, row in machine_df.iterrows():
                    hover_texts.append(
                        "<b>"+str(row["Work Orders/Operation"])+"</b><br>"
                        + "Machine: "+str(row["Processing Machine"])+"<br>"
                        + "Product: "+str(row["Product"])+"<br>"
                        + "Reference: "+str(row["Reference"])+"<br>"
                        + "Operation order: "+str(row["Operation Order"])+"<br>"
                        + "Status: "+str(row["Work Orders/Status"])+"<br>"
                        + "Start: "+str(row["Start"])+"<br>"
                        + "End: "+str(row["End"])+"<br>"
                        + "Expected duration: "+str(row["Work Orders/Expected Duration"])
                    )

                # Build the combined Plotly figure: machine bars first, operator lines next.
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=machine_df["DurationHours"],
                    y=machine_df["Processing Machine"],
                    base=machine_df["StartHour"],
                    orientation="h",
                    marker=dict(color=[product_color_map[p] for p in machine_df["Product"]]),
                    hovertext=hover_texts,
                    hoverinfo="text",
                    name="Active machine jobs",
                    showlegend=False,
                ))

                # Each operator gets a separate line color across all of their actions.
                operator_color_palette = px.colors.qualitative.Dark24
                for operator_position, operator_name in enumerate(sorted({
                    interval["Operator"] for interval in operator_intervals
                })):
                    operator_rows = [
                        interval for interval in operator_intervals
                        if interval["Operator"] == operator_name
                    ]
                    operator_hours = []
                    operator_locations = []
                    start_hover_texts = []
                    for interval in operator_rows:
                        operator_hours.extend([
                            (interval["Start"] - day_start).total_seconds()/3600,
                            (interval["End"] - day_start).total_seconds()/3600,
                        ])
                        operator_locations.extend([interval["Row"], interval["Row"]])
                        event_details = (
                            operator_name+"<br>"
                            + "<b>"+interval["Event"]+"</b> (ID "+str(interval["EventID"])+")<br>"
                            + "Location: "+str(interval["Location"])+"<br>"
                            + "Equipment: "+str(interval["Equipment"])+"<br>"
                            + "Product: "+str(interval["Product"])+"<br>"
                            + "Reference: "+str(interval["Reference"])
                        )
                        start_hover_texts.append(event_details+"<br>Time: "+str(interval["Start"]))
                    # Draw the activity path without hover behavior. Hover belongs only
                    # to the start points, while end points remain quiet visual anchors.
                    fig.add_trace(go.Scatter(
                        x=operator_hours,
                        y=operator_locations,
                        mode="lines",
                        name=operator_name+" activity",
                        line=dict(
                            color=operator_color_palette[operator_position % len(operator_color_palette)],
                            width=3,
                            shape="hv",
                        ),
                        hoverinfo="skip",
                    ))
                    operator_color = operator_color_palette[operator_position % len(operator_color_palette)]
                    start_hours = operator_hours[::2]
                    end_hours = operator_hours[1::2]
                    start_locations = operator_locations[::2]
                    end_locations = operator_locations[1::2]
                    fig.add_trace(go.Scatter(
                        x=start_hours,
                        y=start_locations,
                        mode="markers",
                        name=operator_name+" action starts",
                        marker=dict(color=operator_color, size=8, symbol="circle"),
                        hovertext=start_hover_texts,
                        hoverinfo="text",
                        showlegend=False,
                    ))
                    fig.add_trace(go.Scatter(
                        x=end_hours,
                        y=end_locations,
                        mode="markers",
                        name=operator_name+" action ends",
                        marker=dict(color=operator_color, size=4, symbol="circle"),
                        hoverinfo="skip",
                        showlegend=False,
                    ))

                fig.update_yaxes(
                    title="Machines and operator activity locations",
                    categoryorder="array",
                    categoryarray=list(reversed(machine_names + [central_row, other_row])),
                )
                fig.update_xaxes(
                    title="Planned time",
                    range=[0, 24],
                    tickmode="array",
                    tickvals=list(range(25)),
                    ticktext=[(day_start+timedelta(hours=h)).strftime("%H:%M") for h in range(25)],
                    rangeslider=dict(visible=True, thickness=0.08),
                )
                fig.update_layout(
                    title="Active planned machine jobs and operator activity: "+str(day_start.date()),
                    height=max(500, 40*(len(machine_names)+2)+150)+120,
                    width=1400,
                    bargap=0.3,
                    dragmode="zoom",
                )

                fig.show(config=dict(scrollZoom=True, displaylogo=False))

        except Exception as e:
            self.getController().getSimulator().saveLog("ERROR: in showing active machine jobs "+str(e))

        return
##################################################################################################################################################
    def ViewMILPResults(self,event):

        #getRes_process_df(self):
        #getDemand_process_df(self):


        result = self.getmilpresults().value
        self.milporders.clear()


        OrdList = []
        
        if result == 'Orders': 
            for prodorder in self.getController().getWorkManager().getSelectedOrders():
                self.milporders[len(OrdList)]=  prodorder
                OrdList.append(prodorder.getFinalProduct().getPN()+"- Q: "+str(prodorder.getQuantity())+", d: "+str(prodorder.getDeadline()))
                
            self.getmilpdetails().options = [x for x in OrdList]

    
        if result == 'Machines':

            for res in self.getController().getWorkManager().getResources():
                OrdList.append(res.getName())
                try: 
                    if res.getType() == "Machine":
                        self.getMachines().append(res)
                except Exception as e:
                    self.getController().getSimulator().saveLog("ERROR: machine instance check "+res.getName()+" ... "+str(e))
                             

            self.getmilpdetails().options = [x for x in OrdList]
            #self.showMachineSchedule()
                              
        return 

    def ViewDetails(self,event):

       
                  

        return 

    def ViewMILPDetails(self,event):

        result_type = self.getmilpresults().value
        result_detail = self.getmilpdetails().value

        shifts = {3: [x for x in range(8)],1:[x for x in range(8,17)],2:[x for x in range(18,24)]}
        pncolors = dict() 
       
        

        try: 

            if result_type == 'Machines':
                pass
              
            if result_type == 'Orders':
                selectid = 0
                for x in self.getmilpdetails().options:
                    if self.getmilpdetails().options[selectid] == result_detail:
                        break
                    selectid+=1

                prodorder = self.getController().getWorkManager().getSelectedOrders()[selectid]
                with self.getMILPResultInfo():
                    clear_output()
                    display("Deadline: "+str(prodorder.getDeadline())+", completion: "+str(prodorder.getMILPCompletion()))

            
        
        except Exception as e:
            self.getController().getSimulator().saveLog("ERROR in plotting: "+str(e)) 
            
                                    

        
                            

    #  self.Schedule_df = pd.DataFrame(columns=["PN","Quantity","Work Orders/Start","Work Orders/End","Work Orders/Work Center","Work Orders/Expected Duration"])
                    
         

        return 

    def updateSimProgress(self,info):

        
        self.getRunProgress().value+=str(info)+ "\n"
        
        return
        
    def showResource(self,event):

        resname = self.getResourceDrop().value

        for res in self.getController().getWorkManager().getResources():
            if res.getName() == resname:
                av_str = ''
                for avshift in res.getAvailableShifts():
                    av_str+= ("," if len(av_str) > 0 else "")+str(avshift)
                self.getAvailabilityCheck().value = av_str

                if res.getType() == "Machine":
                    self.getResAlternatives().options = [alt for alt in res.getAlternatives()]
                else:
                    self.getResAlternatives().options = []
                
                

        return 

    def setSuspendMode(self,event):

        self.getController().getSimulator().setSuspendMode(self.getSimSuspendCheck().value)

        return 
    def setDisplayMode(self,event):

        self.getController().getSimulator().setDisplayMode(self.getSimDisplayCheck().value)

        return 

    def setSimTimeStep(self,event):

        try: 
            self.getController().getSimulator().setTimeIncrement(int(self.getTimeStep().value))
        except: 
            self.getController().getSimulator().saveLog("REPORT: time step is not proper integer!")  

        return 

    def addDebugEvent(self,event):

        selectedeventstr = self.getEventIDs().value

        if not selectedeventstr in self.getSelectedEventsDict():
            self.getSelectedEventsDict()[selectedeventstr] = self.getSuspendedEvents()[selectedeventstr]

            self.getController().getSimulator().getDisplayEvents().clear()

            for evstr,ev in self.getSelectedEventsDict().items():
                self.getController().getSimulator().getDisplayEvents().append(ev)

            self.getSelectedEvents().options = [ evstr for evstr,ev in self.getSelectedEventsDict().items()]
            


        return 

    def removeAlternative(self,event):

        altname = self.getResAlternatives().value

        self.getController().getSimulator().saveLog("REPORT: alt to remove: "+str(altname))  
        selected_res = None
            
        resname = self.getResourceDrop().value
        self.getController().getSimulator().saveLog("REPORT: resource name"+resname)    
        for res in self.getController().getWorkManager().getResources():
            if res.getName() == resname:
                selected_res = res
                self.getController().getSimulator().saveLog("REPORT: resource found!")    
                break

        if altname in selected_res.getAlternatives():
            self.getController().getSimulator().saveLog("REPORT: alt found in alts to remove: "+str(altname))
            selected_res.getAlternatives().remove(altname)

        self.getResAlternatives().options = [alt for alt in selected_res.getAlternatives()]
        

        return 

    def addAlternative(self,event):

        if self.getResourceDrop2().layout.visibility == 'hidden':
            self.getResourceDrop2().layout.visibility = 'visible'
            self.getAlternativeAdd().layout.width= "170px"
            self.getAlternativeAdd().description = "Add Selected"
        else:

            resname = self.getResourceDrop().value
            altname = self.getResourceDrop2().value


            selected_res = None
            for res in self.getController().getWorkManager().getResources():
                if res.getName() == resname:
                    selected_res = res; break

            if altname != resname:
                if not altname in selected_res.getAlternatives():
                    selected_res.getAlternatives().append(altname)
                    
                    self.getResAlternatives().options = [alt for alt in selected_res.getAlternatives()]
              
            
            self.getResourceDrop2().layout.visibility = 'hidden'
            self.getAlternativeAdd().layout.width= "80px"
            self.getAlternativeAdd().description = "Add"
            
 

        return 

    def showWeekSchedule(self,event):

        showweek = self.getWeeksMenu().value

        weekfirstday = pd.to_datetime(showweek, format='%Y-%m-%d')
  
        lastday = weekfirstday+timedelta(days = 6)

        self.getController().getSimulator().saveLog("REPORT: weekfirstday "+str(weekfirstday)+" lastday "+str(lastday))         


        self.showMachineSchedule(weekfirstday,lastday)

        #self.showSchedule(weekfirstday,lastday)

        return

        

    def applySelectDestination(self,event):

        for eventname,eventoj in self.getController().getWorkManager().getEventTypes().items():
            if eventname in self.getController().getWorkManager().getAlgorithmSetting():
                if "Select Destination" in self.getController().getWorkManager().getAlgorithmSetting()[eventname]:
                    self.getController().getWorkManager().getAlgorithmSetting()[eventname]["Select Destination"] = self.getSelectDestinationAlg().value
                    self.getController().getSimulator().saveLog("REPORT: select dest alg set to  "+self.getSelectDestinationAlg().value)  
                
       
        return



    def showDaySchedule(self,event):

        showday = self.getWeeksMenu().value

        daydatetime = pd.to_datetime(showday, format='%Y-%m-%d')
  
        #self.getController().getSimulator().saveLog("REPORT: weekfirstday "+str(weekfirstday)+" lastday "+str(lastday))         


        if self.getResourceMenu().value == "Machines":
            self.showMachineSchedule(daydatetime,daydatetime)
        if self.getResourceMenu().value == "Operators":
            if self.getSelectedSchedule().getAlgorithmName() == "Simulation":
                self.showOperatorSchedule(daydatetime)
                self.getController().getSimulator().saveLog("REPORT: Operator schedules should be shown")
            else:
                self.getController().getSimulator().saveLog("REPORT: Algortihm "+str(self.getSelectedSchedule().getAlgorithmName())+" doesn ot have operator schedule.")
        if self.getResourceMenu().value == "Combined":
            if self.getSelectedSchedule().getAlgorithmName() == "Simulation":
                self.setCombinedLastDay(daydatetime)
                self.showCombinedSchedule(daydatetime)
                self.getController().getSimulator().saveLog("REPORT: Combined schedule should be shown")
            else:
                self.getController().getSimulator().saveLog("REPORT: Algortihm "+str(self.getSelectedSchedule().getAlgorithmName())+" doesn ot have combined schedule.")
            

        #self.showSchedule(weekfirstday,lastday)

        return

    def resetSchedule(self,event):

        # Only expose the combined-view filters while that view is active.
        self.getCombinedFilterBox().layout.display = 'flex' if self.getResourceMenu().value == "Combined" else 'none'

        with self.getScheduleOutput():
            clear_output()

        return

    def applyCombinedFilters(self,event):

        if self.getResourceMenu().value == "Combined" and self.getCombinedLastDay() is not None:
            self.showCombinedSchedule(self.getCombinedLastDay())

        return

    
    def saveResources(self,event):

        self.getController().getSimulator().saveLog("REPORT: in saving resources...")         
        try: 
            selected_res = None
            
            resname = self.getResourceDrop().value
            self.getController().getSimulator().saveLog("REPORT: resource name"+resname)    
            for res in self.getController().getWorkManager().getResources():
                if res.getName() == resname:
                    selected_res = res
                    self.getController().getSimulator().saveLog("REPORT: resource found!")    
                    break
                    
    
            if selected_res!= None:
                res_avail = self.getAvailabilityCheck().value
                self.getController().getSimulator().saveLog("REPORT: in availability of resource "+selected_res.getName()+" "+": "+res_avail)    
                try: 
                    avail_shifts = res_avail.split(',')
    
                    selected_res.getAvailableShifts().clear()
                    for shft in avail_shifts:
                        selected_res.getAvailableShifts().append(shft)
                    
                    self.getController().getWorkManager().saveResources()
                except Exception as e:
                    self.getController().getSimulator().saveLog("ERROR: in availability format of resource "+str(e)+": "+selected_res.getName())    
        except Exception as e:
            self.getController().getSimulator().saveLog("ERROR: in saving resources "+str(e))    
        
     
        return 

    def RunMILP(self,event):

        self.getController().getMILPManager().constructSchedule()
        
        return 

    def applyCases(self,event):

        selected_eventtype = self.getEventTypes().value

        self.getEventCases().options = []

        if selected_eventtype in self.getController().getWorkManager().getEventTypes():
            eventtype = self.getController().getWorkManager().getEventTypes()[selected_eventtype]
            self.getEventCases().options = [c for c in eventtype.getDecisionsDict().keys()]
      


        return



    def checkDecisions(self,event):
        
        selected_eventtype = self.getEventTypes().value
        selected_case = self.getEventCases().value

        self.getCaseDecisions().options = []

        if selected_eventtype in self.getController().getWorkManager().getEventTypes():
            eventtype = self.getController().getWorkManager().getEventTypes()[selected_eventtype]
            if selected_case in eventtype.getDecisionsDict():
                self.getCaseDecisions().options = [d for d in eventtype.getDecisionsDict()[selected_case]]
       
        return


    def checkAlg(self,event):

        try: 
            selected_eventtype = self.getEventTypes().value
            selected_decison = self.getCaseDecisions().value

            if selected_eventtype == None or selected_decison == None:
                return
    
            self.getDecisionAlgs().options = []
    
            self.getController().getSimulator().saveLog("REPORT: event type in algsetting")    
    
            if selected_eventtype in self.getController().getWorkManager().getAlgorithmSetting():
                if selected_decison in self.getController().getWorkManager().getAlgorithmSetting()[selected_eventtype]:
                    self.getDecisionAlgs().options = [self.getController().getWorkManager().getAlgorithmSetting()[selected_eventtype][selected_decison]]


            if selected_decison in self.getController().getWorkManager().getAlgorithmManager().getDecisionAlgorithms():
                algsdict = self.getController().getWorkManager().getAlgorithmManager().getDecisionAlgorithms()[selected_decison]
                self.getDecisionAlgorithms().options =[x for x in algsdict.keys()]
                self.getDecisionAlgorithms().value = self.getDecisionAlgorithms().options[0]
            else:
                self.getDecisionAlgorithms().options =[]
                self.getDecisionAlgorithms().value = ''

        except Exception as e:
            self.getController().getSimulator().saveLog("ERROR: in finding decision alg "+str(e))    

        return 

    def changeAlg(self,event):

        selected_eventtype = self.getEventTypes().value
        selected_case = self.getEventCases().value
        selected_decison = self.getCaseDecisions().value


        if selected_eventtype in self.getController().getWorkManager().getAlgorithmSetting():
            self.getController().getWorkManager().getAlgorithmSetting()[selected_eventtype][selected_decison] = self.getDecisionAlgorithms().value
            self.getDecisionAlgs().options = [self.getController().getWorkManager().getAlgorithmSetting()[selected_eventtype][selected_decison]]

        

        

        return
  
      

    def applyUseCase(self,event):
  
        self.getController().setUseCase(self.getUseCaseMenu().value)
        self.getController().getWorkManager().setNoOrders(self.getOrders().value)
        self.getTitle().value = 'TimeLimit: '+str(self.getController().getSimulator().getTimelimit())+", Orders: "+str(self.getController().getWorkManager().getNoOrders())+", Use Case: "+self.getController().getUseCase()

        self.getEventTypes().options = [x for x in  self.getController().getWorkManager().getEventTypes().keys()]
     

        return 

    def GenerateMainTab(self):

        #print("Visual Manager: Generating dashboard")

        self.setInputText(widgets.Text(description ='Use Case: ',value=''))
     

        self.setWeeksDrop(widgets.Dropdown(options = [w for w in range(1,12)],value = 10,description = 'Weeks:'))
        self.setResourceDrop(widgets.Dropdown(options = [],description = 'Resources:'))
        self.getResourceDrop().observe(self.showResource,'value')
        self.getWeeksDrop().observe(self.setDropSimWeeks,'value')
        self.getWeeksDrop().layout.width = '300px'
        self.getResourceDrop().layout.width = '300px'
        self.getWeeksDrop().layout.height = '25px'

        self.setResourceDrop2(widgets.Dropdown(options = [],description = ''))


        self.getResourceDrop2().layout.visibility = 'hidden'
        self.getResourceDrop2().layout.width= '150px'

        self.setResourceSave(widgets.Button(description="Apply"))
        self.getResourceSave().on_click(self.saveResources)

        self.setResAlternatives(widgets.Select(options=[],description='Alternatives:',disabled=False))

        self.getResAlternatives().layout.width = '200px'

        self.setAlternativeRemove(widgets.Button(description="Remove"))
        self.getAlternativeRemove().layout.width = '80px'
        self.getAlternativeRemove().on_click(self.removeAlternative)

        self.setAlternativeAdd(widgets.Button(description="Add"))
        self.getAlternativeAdd().layout.width = '80px'
        self.getAlternativeAdd().on_click(self.addAlternative)



        self.setAvailabilityCheck(widgets.Text(value='',description='Availability:',disabled=False))
 
        
        self.getController().getSimulator().setRunWeeks(self.getWeeksDrop().value)
  

        self.ProcessOutput = widgets.Output()



       
       

        # Single Select
        select = widgets.Select(options=['Use Cases','Orders','Resources','Simulation Settings','Simulation Run','MILP Run','Log Information'
                                         ,'Schedules'],value='Resources',description='',disabled=False)

        select.observe(self.menu_click,'value')
        self.setMainmenu(select)
        self.getMainmenu().layout.width = '250px'
        self.getMainmenu().layout.height = '200px'

        
        

        mainbox = VBox(children=[self.getWeeksDrop(),self.getResourceDrop(),
                                 HBox(children=[self.getAvailabilityCheck(), VBox(children=[self.getResAlternatives(),
                                                                                            HBox(children=[self.getAlternativeRemove(),self.getAlternativeAdd()]),self.getResourceDrop2()
                                                                                           ])]),
                                 self.getResourceSave()])
        self.setMainBox(mainbox)

        self.getMainBox().layout.width = '50%'

        self.runbutton = widgets.Button(description="Run Simulation")
        self.runbutton.on_click(self.RunSim)

        self.runbutton.layout.width = '800px'

        self.setRunProgress(widgets.Textarea(value='', placeholder='',description='',disabled=True))

        self.getRunProgress().layout.width = '800px'
        self.getRunProgress().layout.height = '300px'

   
        runbox = VBox(children=[self.runbutton,self.getRunProgress()])
       
        self.setRunBox(runbox)


        orders = widgets.Dropdown(options = [w for w in range(1,250)],value = 249,description = 'Orders:')
        self.setOrders(orders)
        self.getOrders().observe(self.setDropSimOrders,'value')
      

        orders = widgets.Select(options=[],description='Orders:',disabled=False)
        readbutton = widgets.Button(description="Read Input")
        self.setReadButton(readbutton)
        self.getReadButton().on_click(self.ReadInput)
        self.setProdOrders(orders)

        self.getProdOrders().layout.width = '500px'
        self.getProdOrders().layout.height = '200px'
        

        orderbox = VBox(children=[HBox(children=[self.getOrders(),self.getReadButton()]),self.getProdOrders()])
        self.setOrderBox(orderbox)

        self.getOrderBox().layout.width = '75%'


        #selectalgs = [x for x in self.getController().getWorkManager().getProductionAlgManager().getDecisionAlgorithms()['Select Destination'].keys()]
 
        self.setSelectDestinationAlg(widgets.Dropdown(options = [],description = ''))

        selectdesttitle = widgets.Label(value="Select Destination:") 
        self.getSelectDestinationAlg().observe(self.applySelectDestination,'value')

      
        self.setSimSuspendCheck(widgets.Checkbox(value=False,description='Suspend Mode',disabled=False,indent=False))
        self.setSimDisplayCheck(widgets.Checkbox(value=False,description='Display Mode',disabled=False,indent=False))
        self.setTimeStep(widgets.Text(description ='Timestep: ',value=''))
        self.setTimeApply(widgets.Button(description="Apply Timestep"))
        self.setEventIDs(widgets.Select(options=[],description='Events:',disabled=False))
        self.setSelectEvent(widgets.Button(description=">> Debug >>"))
        self.setSelectedEvents(widgets.Select(options=[],description='',disabled=False))
        self.getSelectEvent().on_click(self.addDebugEvent)
      
        

        
        self.getSimSuspendCheck().observe(self.setSuspendMode,'value')
        self.getSimDisplayCheck().observe(self.setDisplayMode,'value')
        self.getTimeApply().on_click(self.setSimTimeStep)

        simbox = VBox(children=[HBox(children=[VBox(children=[self.getSimSuspendCheck(),self.getSimDisplayCheck(),HBox(children=[self.getTimeStep(),self.getTimeApply()]),HBox(children=[self.getEventIDs(),self.getSelectEvent(),self.getSelectedEvents()])])])])

        self.setSimBox(simbox)

        self.getController().getSimulator().saveLog("REPORT: checked.. use cases "+str(len(self.getController().getSimulator().getUseCases())))  
        
        self.setUseCaseMenu(widgets.Dropdown(options =[x for x in self.getController().getSimulator().getUseCases()],description = 'Use Cases'))

        self.getUseCaseMenu().observe(self.applyUseCase,'value')

       

        eventtypetitle = widgets.Label(value="Event Types:") 
        self.setEventTypes(widgets.Select(options=[],description='',disabled=False))
        casetitle = widgets.Label(value="Progress Cases:") 
        decisiontitle = widgets.Label(value="Decisions:") 
        algtitle = widgets.Label(value="Algorithm:") 
        self.setEventCases(widgets.Select(options=[],description='',disabled=False))
        self.setCaseDecisions(widgets.Select(options=[],description='',disabled=False))
        self.setDecisionAlgs(widgets.Select(options=[],description='',disabled=False))
        self.setDecisionAlgorithms(widgets.Dropdown(options = [],description = ''))

        
        self.getEventTypes().observe(self.applyCases,'value')
        self.getEventCases().observe(self.checkDecisions,'value')
        self.getCaseDecisions().observe(self.checkAlg,'value')
        self.getDecisionAlgorithms().observe(self.changeAlg,'value')
        

        self.getEventTypes().layout.width = '150px'
        self.getEventCases().layout.width = '125px'
        self.getCaseDecisions().layout.width = '125px'
        self.getDecisionAlgs().layout.width = '150px'
        self.getDecisionAlgs().layout.height = '25px'

        casebox = VBox(children=[self.getUseCaseMenu(),HBox(children=[
            VBox(children=[eventtypetitle,self.getEventTypes()]),
            VBox(children=[casetitle,self.getEventCases()]),
            VBox(children=[decisiontitle,self.getCaseDecisions()]),
            VBox(children=[algtitle,self.getDecisionAlgs(),self.getDecisionAlgorithms()])])])

        self.setUseCaseBox(casebox)
     
        

        self.setShowLogButton(widgets.Button(description="Show Log Information") )
        self.getShowLogButton().on_click(self.ShowLog)
        self.getShowLogButton().layout.width = '750px'
        self.setLogSelect(widgets.Select(options=[],description='',disabled=False))
        self.getLogSelect().layout.width = '800px'
        self.getLogSelect().layout.height = '300px'
        logbox = VBox(children=[self.getShowLogButton(),self.getLogSelect()])

        self.setLogBox(logbox)


        
        self.setResultText(widgets.Select(options=[],description='',disabled=False))
        self.getResultText().layout.width = '350px'
        self.getResultText().layout.height = '120px'
         

        self.setResultInfoText(widgets.Output())
        self.getResultInfoText().layout.width = '750px'
        self.getResultInfoText().layout.height = '250px'

        self.setKPIArea(widgets.Textarea(value='', placeholder='', description='KPIs:', disabled=True))

        self.setFurtherText(widgets.Select(options=[],description='',disabled=False))
        self.getFurtherText().layout.width = '150px'
        self.getFurtherText().layout.height = '120px'

        self.setWeeksMenu(widgets.Dropdown(options = [],description = 'Day:'))
        self.getWeeksMenu().observe(self.showDaySchedule,'value')

        self.setResourceMenu(widgets.Dropdown(options = ["Machines","Operators","Combined"],description = 'Resource:'))
        self.getResourceMenu().observe(self.resetSchedule,'value')

        self.setCombinedMachineFilter(widgets.Dropdown(options = ["All"],value = "All",description = 'Machine:'))
        self.setCombinedOperatorFilter(widgets.Dropdown(options = ["All"],value = "All",description = 'Operator:'))
        self.setCombinedProductFilter(widgets.Dropdown(options = ["All"],value = "All",description = 'Product:'))
        self.getCombinedMachineFilter().observe(self.applyCombinedFilters,'value')
        self.getCombinedOperatorFilter().observe(self.applyCombinedFilters,'value')
        self.getCombinedProductFilter().observe(self.applyCombinedFilters,'value')
        self.setCombinedFilterBox(HBox(children=[self.getCombinedMachineFilter(),self.getCombinedOperatorFilter(),self.getCombinedProductFilter()]))
        self.getCombinedFilterBox().layout.display = 'none'



        self.getKPIArea().layout.width = '400px'
        self.getKPIArea().layout.height = '100px'
 
        self.getResultText().observe(self.ViewResults,'value')

        self.getFurtherText().observe(self.ViewDetails,'value')
        self.setScheduleOutput(widgets.Output())
        self.getScheduleOutput().layout.height = '2000px'

        resultbox = VBox(children=[HBox(children=[self.getResultText(),self.getKPIArea()]),HBox(children=[self.getWeeksMenu(),self.getResourceMenu()]),self.getCombinedFilterBox(),self.getScheduleOutput()])
        
        self.setResultBox(resultbox)


        self.setmilprunbutton(widgets.Button(description="Run MILP"))
        self.getmilprunbutton().on_click(self.RunMILP)

        self.setmilpprogress(widgets.Textarea(value='', placeholder='',description='',disabled=True))

        self.getmilpprogress().layout.width = '750px'
        self.getmilpprogress().layout.height = '300px'

        self.setDiagSelect(widgets.Select(options=[],description='',disabled=False))
        self.getDiagSelect().layout.width = '750px'
        self.getDiagSelect().layout.height = '300px'
        diagbox = VBox(children=[self.getmilprunbutton(),self.getmilpprogress()])

        self.setDiagBox(diagbox)

     


        #self.setTitle(widgets.Label(value='TimeLimit: '+str(self.getController().getSimulator().getTimelimit())+", Orders: "+str(self.getController().getWorkManager().getNoOrders())))

        self.setTitle(widgets.Label(value='TimeLimit: '+str(self.getController().getSimulator().getTimelimit())+", Orders: "+str(0)))

        self.getAllBoxes().append(self.getMainBox())
        self.getAllBoxes().append(self.getUseCaseBox())
        self.getAllBoxes().append(self.getRunBox())
        self.getAllBoxes().append(self.getOrderBox())
        self.getAllBoxes().append(self.getLogBox())
        self.getAllBoxes().append(self.getResultBox())
        self.getAllBoxes().append(self.getDiagBox())
        self.getAllBoxes().append(self.getSimBox())


         # for first time, if nothing is selected extra..
        #display(self.getUseCaseMenu().value)
        self.getController().setUseCase(self.getUseCaseMenu().value)
        #display(self.getController().getUseCase())

        self.getController().getSimulator().saveLog("REPORT: controller workmanager none?" + str(self.getController().getWorkManager()== None))  
        
        if self.getController().getWorkManager()!= None:
            self.getController().getWorkManager().setNoOrders(self.getOrders().value)
            self.getTitle().value = 'TimeLimit: '+str(self.getController().getSimulator().getTimelimit())+", Orders: "+str(self.getController().getWorkManager().getNoOrders())+", Use Case: "+self.getController().getUseCase()

            self.getEventTypes().options = [x for x in  self.getController().getWorkManager().getEventTypes().keys()]

        


        self.BoxMatches['Use Cases'] =  self.getUseCaseBox()
        self.BoxMatches['Simulation Run'] =  self.getRunBox()
        self.BoxMatches['Orders'] =  self.getOrderBox()
        self.BoxMatches['Resources'] =  self.getMainBox()
        self.BoxMatches['Log Information'] = self.getLogBox()
        self.BoxMatches['Schedules'] = self.getResultBox()
        self.BoxMatches['MILP Run'] = self.getDiagBox()
        self.BoxMatches['Simulation Settings'] = self.getSimBox()
      

        for box in self.getAllBoxes():
            box.layout.visibility = 'hidden'
            box.layout.display = 'none'
       

        separator = widgets.Box(layout=widgets.Layout(border='solid 1px lightblue', width='99%', height='1px', margin='5px 0px',style={'background': "#C7EFFF"}))

        vseparator = widgets.Box(layout=widgets.Layout(border='solid 1px lightblue', width='1px', height='99%', margin='5px 0px',style={'background': "#C7EFFF"}))

        
        tab = VBox(children = [
                              self.getTitle(),separator,
                               HBox(children = [self.getMainmenu(),VBox(children = [vseparator]),self.getMainBox(),self.getUseCaseBox(),self.getRunBox(),self.getOrderBox(),self.getLogBox(),self.getResultBox(),self.getDiagBox(), self.getSimBox()])]
                  )    
        return tab 

    def applyvalue(self,value):
        


        return

 
