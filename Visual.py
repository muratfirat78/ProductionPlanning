##### import ipywidgets as widgets
from IPython.display import clear_output
from IPython import display
from ipywidgets import *
from ipytree import Tree, Node
from datetime import timedelta,date,datetime
import matplotlib.pyplot as plt
import warnings
import seaborn as sns
import os
import pandas as pd
import warnings
import sys
import numpy as np
from pathlib import Path
from IPython.display import display, HTML
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
        self.demandorderlist = dict()  # key: list order, val: demandid

        self.milpmainbox = None
        self.milpresultbox = None
        self.milpprogress = None
        self.milprunbutton = None
        self.milpresults = None
        self.milpresultinfo = None
        self.milpdetails = None
        self.milporders = dict()

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

    
    def RunSim(self,event):


        self.runbutton.disabled = True
        self.getController().getSimulator().saveLog("Run clicked..")
        self.getController().getSimulator().RunSimulation(self.getController().getWorkManager())


        self.demandorderlist.clear()
   
        process_df = pd.read_csv("ProcessData.csv")
        demagrr = process_df.groupby(["DemandID","Product","NrItems"], dropna=True)[['OperationName']].agg(lambda x:list(x)).reset_index()

        for i,r in demagrr.iterrows():
            self.demandorderlist[len(self.demandorderlist)] = r["DemandID"]

        self.getFurtherText().options = [self.getController().getWorkManager().getProductionOrders()[x].getFinalProduct().getPN() for x in self.demandorderlist.values()]


        return 

    def ReadInput(self,event):

        selectedOrders = self.getController().getWorkManager().createInstance()

        orderopts = []
        for prodorder in selectedOrders:
            orderopts.append("PN: "+prodorder.getFinalProduct().getPN()+", Q: "+str(len(prodorder.getItems()))+", Deadline: "+str(prodorder.getDeadline()))

        self.getProdOrders().options = orderopts

        self.getReadButton().disabled = True
        self.getOrders().disabled = True

        return 

        
    def setDropSimOrders(self,event):
        
        self.getController().getWorkManager().setNoOrders(self.getOrders().value)

        self.getTitle().value = 'TimeLimit: '+str(self.getController().getSimulator().getTimelimit())+", Orders: "+str(self.getController().getWorkManager().getNoOrders())
        return  

    def setDropSimWeeks(self,event):
        
        self.getController().getSimulator().setRunWeeks(self.getWeeksDrop().value)
        self.getTitle().value = 'TimeLimit: '+str(self.getController().getSimulator().getTimelimit())+", Orders: "+str(self.getController().getWorkManager().getNoOrders())
        
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

        if menuitem in self.BoxMatches:
             self.ViewBoxes(self.BoxMatches[menuitem])

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
        result = self.getResultText().value

        self.demandorderlist.clear()
       

        process_df = pd.read_csv("ProcessData.csv")

       
        demagrr = process_df.groupby(["DemandID","Product","NrItems"], dropna=True)[['OperationName']].agg(lambda x:list(x)).reset_index()


        for i,r in demagrr.iterrows():
            self.demandorderlist[len(self.demandorderlist)] = r["DemandID"]
        
            
        if result == 'Order Progress': 
            self.getFurtherText().options = [self.getController().getWorkManager().getProductionOrders()[x].getFinalProduct().getPN() for x in self.demandorderlist.values()]
        if result == 'Resource Operations': 
            self.getFurtherText().options = [res for res in process_df["Resource"].unique()]
                  

        return 

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
                OrdList.append(res.getName()+" ["+str(res.getID())+"]")

            self.getmilpdetails().options = [x for x in OrdList]
                
          
            
        

        return 

    def ViewDetails(self,event):

        #getRes_process_df(self):
        #getDemand_process_df(self):
        result_type = self.getResultText().value
        result_detail = self.getFurtherText().value


        selectid = 0
        for x in self.getFurtherText().options:
            if self.getFurtherText().options[selectid] == result_detail:
                break
            selectid+=1
        
            

        

        process_df = pd.read_csv("ProcessData.csv")
    
        process_df=process_df.reset_index()

        if result_type == 'Order Progress': 

            prodord = self.demandorderlist[selectid]
            sub_df = process_df[process_df["DemandID"] == prodord]
            sub_df = sub_df[["OperationName","Resource","Start","Completion"]]
            
            sub_df['Start'] = pd.to_datetime(sub_df['Start'])
            sub_df = sub_df.sort_values(by ="Start")
            with self.getResultInfoText():
                clear_output()
                display(sub_df.head(50))
           
        if result_type == 'Resource Operations': 

            sub_df = process_df[process_df["Resource"] == result_detail]
            sub_df = sub_df[["Resource","Start","Completion","Product"]]
            sub_df['Start'] = pd.to_datetime(sub_df['Start'])
            sub_df = sub_df.sort_values(by ="Start")
            with self.getResultInfoText():
                clear_output()
                display(sub_df.head(50))
                  

        return 

    def ViewMILPDetails(self,event):

        result_type = self.getmilpresults().value
        result_detail = self.getmilpdetails().value

        selectid = 0
        for x in self.getmilpdetails().options:
            if self.getmilpdetails().options[selectid] == result_detail:
                break
            selectid+=1

        if selectid in self.milporders:
            prodorder =  self.milporders[selectid]

            if result_type == 'Orders': 
                
                order_df = pd.DataFrame(columns=["Operation","Alternatives","Status","Start","Completion","ProcessTime"])

                operation_sequence = prodorder.getFinalProduct().getOperationSequences()[prodorder.getID()]
                 
                for operation in operation_sequence:
                    infodata = {"Operation":operation.getName(),"Alternatives":len(operation.getAlternativeResources()),"Status":operation.getStatus(),"Start":operation.getStart(),"Completion":operation.getCompletion(),"ProcessTime":operation.getRandVar().sampleValue()  } 
                    order_df.loc[len(order_df)]= infodata

                with self.getMILPResultInfo():
                    clear_output()
                    display(order_df.head(50))
           
       

        return 

    def updateSimProgress(self,info):

        self.getRunProgress().value+=str(info)+ "\n"
        
        return

    def RunMILP(self,event):

        self.getController().getMILPManager().constructSchedule()

        
        return 

    def GenerateMainTab(self):

        print("Visual Manager: Generating dashboard")

        self.setInputText(widgets.Text(description ='Use Case: ',value=''))

        self.setWeeksDrop(widgets.Dropdown(options = [w for w in range(1,10)],value = 4,description = 'Weeks:'))
        self.getWeeksDrop().observe(self.setDropSimWeeks,'value')
        
        self.getController().getSimulator().setRunWeeks(self.getWeeksDrop().value)
  

        self.ProcessOutput = widgets.Output()

     
        # Single Select
        select = widgets.Select(options=['Orders','Main Settings','Run','Log Information'
                                         #'Define Event Type','Event Type Precedence'
                                         ,'Results','Diagnostics'],value='Main Settings',description='Select:',disabled=False)

        select.observe(self.menu_click,'value')
        self.setMainmenu(select)
        self.getMainmenu().layout.width = '200px'
        self.getMainmenu().layout.height = '200px'

        
        

        mainbox = VBox(children=[self.getInputText(),self.getWeeksDrop()])
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
        self.getController().getWorkManager().setNoOrders(self.getOrders().value)

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

        # event type box
        eventtypename = widgets.Text(description ='Name: ',value='')
        eventtyperes = widgets.Text(description ='Resource: ',value='')
        eventtypeequip = widgets.Text(description ='Equipment: ',value='')

        
        eventtypestatic = widgets.RadioButtons(options=['Yes', 'No'],description='Static:',disabled=False)
        eventtypeload = widgets.RadioButtons(options=['Yes', 'No'],description='Loading:',disabled=False)
        eventtypeproc= widgets.RadioButtons(options=['Yes', 'No'],description='Process:',disabled=False)

        eventtypebutton = widgets.Button(description="Save") 

        eventtypebox = VBox(children=[eventtypename,eventtyperes,eventtypeequip,HBox(children = [eventtypestatic,eventtypeload,eventtypeproc]),eventtypebutton])

        self.setEventTypeBox(eventtypebox)
        self.getEventTypeBox().layout.width = '50%'

        self.setShowLogButton(widgets.Button(description="Show Log Information") )
        self.getShowLogButton().on_click(self.ShowLog)
        self.getShowLogButton().layout.width = '750px'
        self.setLogSelect(widgets.Select(options=[],description='',disabled=False))
        self.getLogSelect().layout.width = '800px'
        self.getLogSelect().layout.height = '300px'
        logbox = VBox(children=[self.getShowLogButton(),self.getLogSelect()])

        self.setLogBox(logbox)


        self.setResultText(widgets.Select(options=['Order Progress','Resource Operations'],description='',disabled=False))
        self.getResultText().layout.width = '150px'
        self.getResultText().layout.height = '120px'
         

        self.setResultInfoText(widgets.Output())
        self.getResultInfoText().layout.width = '750px'
        self.getResultInfoText().layout.height = '250px'

        self.setFurtherText(widgets.Select(options=[],description='',disabled=False))
        self.getFurtherText().layout.width = '300px'
        self.getFurtherText().layout.height = '120px'

 
        self.getResultText().observe(self.ViewResults,'value')

        self.getFurtherText().observe(self.ViewDetails,'value')

        resultbox = VBox(children=[HBox(children=[self.getResultText(),self.getFurtherText()]),self.getResultInfoText()])
        self.setResultBox(resultbox)


        self.setShowDiagButton(widgets.Button(description="Show Diagnostics") )
        self.getShowDiagButton().on_click(self.ShowDiag)
        self.getShowDiagButton().layout.width = '750px'
        self.setDiagSelect(widgets.Select(options=[],description='',disabled=False))
        self.getDiagSelect().layout.width = '750px'
        self.getDiagSelect().layout.height = '300px'
        diagbox = VBox(children=[self.getShowDiagButton(),self.getDiagSelect()])

        self.setDiagBox(diagbox)

     


        self.setTitle(widgets.Label(value='TimeLimit: '+str(self.getController().getSimulator().getTimelimit())+", Orders: "+str(self.getController().getWorkManager().getNoOrders())))

        self.getAllBoxes().append(self.getMainBox())
        self.getAllBoxes().append(self.getEventTypeBox())
        self.getAllBoxes().append(self.getRunBox())
        self.getAllBoxes().append(self.getOrderBox())
        self.getAllBoxes().append(self.getLogBox())
        self.getAllBoxes().append(self.getResultBox())
        self.getAllBoxes().append(self.getDiagBox())


        self.BoxMatches['Run'] =  self.getRunBox()
        self.BoxMatches['Orders'] =  self.getOrderBox()
        self.BoxMatches['Main Settings'] =  self.getMainBox()
        self.BoxMatches['Log Information'] = self.getLogBox()
        self.BoxMatches['Results'] = self.getResultBox()
        self.BoxMatches['Diagnostics'] = self.getDiagBox()

        for box in self.getAllBoxes():
            box.layout.visibility = 'hidden'
            box.layout.display = 'none'
       
            

        tab = VBox(children = [self.getTitle(),
                               HBox(children = [self.getMainmenu(),self.getMainBox(),self.getEventTypeBox(),self.getRunBox(),self.getOrderBox(),self.getLogBox(),self.getResultBox(),self.getDiagBox()])]
                  )    
        return tab 

    def GenerateMILPTab(self):


        self.setmilprunbutton(widgets.Button(description="Run MILP"))
        self.setmilpmainbox(VBox(children=[self.getmilprunbutton()]))

        self.setmilpprogress(widgets.Textarea(value='', placeholder='',description='',disabled=True))

        self.getmilpprogress().layout.width = '850px'
        self.getmilpprogress().layout.height = '300px'

  
         # Single Select
        self.setmilpresults(widgets.Select(options=['Orders','Machines'],value='Orders',description='',disabled=False))
        self.setmilpdetails(widgets.Select(options=[],description='',disabled=False))

        
        
        self.getmilpresults().layout.width = '350px'
        self.getmilpresults().layout.height = '150px'
        self.getmilpdetails().layout.width = '350px'
        self.getmilpdetails().layout.height = '150px'

       

        self.getmilpresults().observe(self.ViewMILPResults,'value')
        self.getmilpdetails().observe(self.ViewMILPDetails,'value')

        self.setMILPResultInfo(widgets.Output())
        self.getMILPResultInfo().layout.width = '750px'
        self.getMILPResultInfo().layout.height = '250px'
        
        self.setmilpresultbox(VBox(children=[self.getmilpprogress()]))

        self.getmilprunbutton().on_click(self.RunMILP)

        
        tab = VBox(children = [self.getmilpmainbox(),self.getmilpresultbox(),HBox(children= [self.getmilpresults(),self.getmilpdetails()]),
                               self.getMILPResultInfo()])    

        return tab

