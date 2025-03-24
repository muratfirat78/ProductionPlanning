# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 11:46:59 2024

@author: mfirat
"""

##### import ipywidgets as widgets
from IPython.display import clear_output
from IPython import display
from ipywidgets import *
from datetime import timedelta,date
import matplotlib.pyplot as plt
import warnings
import seaborn as sns
import os
import pandas as pd
import warnings
import sys
import numpy as np
from pathlib import Path
from PlanningObjects import *

warnings.filterwarnings("ignore")

class VisualManager():

    def __init__(self):  



        self.EditMode = False
        self.DataManager = None
        self.PlanningManager = None
        self.ProdSystemTab = None
        
        self.PSTBResList = None
        self.PSTBNewResName = None
        self.PSTBNewResType = None
        self.PSTBNewResCap = None
        self.PSTBaddres_btn = None
        self.PSTBnewres_btn = None
        self.PSTBcanclres_btn = None
        self.PSTBres_lbl = None
        self.PSTBtyp_lbl =  None
        
        self.PSTBProdList = None
        self.PSTBProdList2 = None
        self.PSTBnewprd_btn = None
        self.PSTBNewProdName = None  
        self.PSTBNewProdPN= None
        self.PSTBNewProdStocklvl = None
        self.PSTBaddprod_btn = None
        self.PSTBcnclprod_btn = None
        self.PSTBprd_lbl = None
        self.PSTBpn_lbl = None



        self.COTBnewrdr_btn= None
        self.COTBNewOrderName= None
        self.COTBNewOrderQ= None
        self.COTBNewOrderDeadLine= None
        self.COTBaddord_btn= None
        self.COTBcnclord_btn= None
        self.COTBcasename= None
        self.COTBsave_bttn= None
        self.COTBorders= None
        self.COTBord_box= None


        self.PSTBoperations= None
        self.PSTBnewopr_btn= None
        self.PSTBNewOprName= None
        self.PSTBNewOprProcTime= None
        self.PSTBaddopr_btn= None
        self.PSTBcanclopr_btn= None
        self.PSTBmyopr_lbl= None
        self.PSTBopr_lbl= None
        self.PSTBoprtp_lbl= None

        self.PSTBresoprmt_btn= None
        self.PSTBprodoprmt_btn= None
        self.PSTBprec_btn= None



        self.PLTBres2lay = None
        self.PLTBresult2exp = None

       
        self.CaseInfo = None

        self.FolderNameTxt = None
        self.CasesDrop = None
        self.ReadFileBtn = None
        self.PLTBmakeplan_btn = None
  
        return

    def getPlanningManager(self):
        return self.PlanningManager

    def setPlanningManager(self,myitm):
        self.PlanningManager = myitm
        return 

    def getReadFileBtn(self):
        return self.ReadFileBtn

    def setReadFileBtn(self,myitm):
        self.ReadFileBtn = myitm
        return 

    def getCasesDrop(self):
        return self.CasesDrop

    def setCasesDrop(self,myitm):
        self.CasesDrop = myitm
        return 

    def getFolderNameTxt(self):
        return self.FolderNameTxt

    def setFolderNameTxt(self,myitm):
        self.FolderNameTxt = myitm
        return 

    def getCaseInfo(self):
        return self.CaseInfo

    def setCaseInfo(self,myitm):
        self.CaseInfo = myitm
        return 

    def getPLTBresult2exp(self):
        return self.PLTBresult2exp

    def setPLTBresult2exp(self,myitm):
        self.PLTBresult2exp = myitm
        return 

    def getPLTBres2lay(self):
        return self.PLTBres2lay

    def setPLTBres2lay(self,myitm):
        self.PLTBres2lay = myitm
        return 

    def IsEditMode(self):
        return self.EditMode


    def getCOTBord_box(self):
        return self.COTBord_box

    def setCOTBord_box(self,myitm):
        self.COTBord_box = myitm
        return 

    def getCOTBorders(self):
        return self.COTBorders

    def setCOTBorders(self,myitm):
        self.COTBorders = myitm
        return 


    def getCOTBsave_bttn(self):
        return self.COTBsave_bttn

    def setCOTBsave_bttn(self,myitm):
        self.COTBsave_bttn = myitm
        return 


    def getCOTBcasename(self):
        return self.COTBcasename

    def setCOTBcasename(self,myitm):
        self.COTBcasename = myitm
        return 


    def getCOTBcnclord_btn(self):
        return self.COTBcnclord_btn

    def setCOTBcnclord_btn(self,myitm):
        self.COTBcnclord_btn = myitm
        return 

    def getCOTBaddord_btn(self):
        return self.COTBaddord_btn

    def setCOTBaddord_btn(self,myitm):
        self.COTBaddord_btn = myitm
        return 
    def getCOTBNewOrderDeadLine(self):
        return self.COTBNewOrderDeadLine

    def setCOTBNewOrderDeadLine(self,myitm):
        self.COTBNewOrderDeadLine = myitm
        return 

    def getCOTBNewOrderQ(self):
        return self.COTBNewOrderQ

    def setCOTBNewOrderQ(self,myitm):
        self.COTBNewOrderQ = myitm
        return 

    def getCOTBNewOrderName(self):
        return self.COTBNewOrderName

    def setCOTBNewOrderName(self,myitm):
        self.COTBNewOrderName = myitm
        return 

    def getCOTBnewrdr_btn(self):
        return self.COTBnewrdr_btn

    def setCOTBnewrdr_btn(self,myitm):
        self.COTBnewrdr_btn = myitm
        return 

    

    def getPSTBpn_lbl(self):
        return self.PSTBpn_lbl

    def setPSTBpn_lbl(self,myitm):
        self.PSTBpn_lbl = myitm
        return 

    def getPSTBprec_btn(self):
        return self.PSTBprec_btn

    def setPSTBprec_btn(self,myitm):
        self.PSTBprec_btn = myitm
        return 


    def getPSTBprodoprmt_btn(self):
        return self.PSTBprodoprmt_btn

    def setPSTBprodoprmt_btn(self,myitm):
        self.PSTBprodoprmt_btn = myitm
        return 

    def getPSTBresoprmt_btn(self):
        return self.PSTBresoprmt_btn

    def setPSTBresoprmt_btn(self,myitm):
        self.PSTBresoprmt_btn = myitm
        return 

    def getPSTBoprtp_lbl(self):
        return self.PSTBoprtp_lbl

    def setPSTBoprtp_lbl(self,myitm):
        self.PSTBoprtp_lbl = myitm
        return 

    def getPSTBopr_lbl(self):
        return self.PSTBopr_lbl

    def setPSTBopr_lbl(self,myitm):
        self.PSTBopr_lbl = myitm
        return 

    def getPSTBmyopr_lbl(self):
        return self.PSTBmyopr_lbl

    def setPSTBmyopr_lbl(self,myitm):
        self.PSTBmyopr_lbl = myitm
        return 
        
    def getPSTBcanclopr_btn(self):
        return self.PSTBcanclopr_btn

    def setPSTBcanclopr_btn(self,myitm):
        self.PSTBcanclopr_btn = myitm
        return 

    def getPSTBaddopr_btn(self):
        return self.PSTBaddopr_btn

    def setPSTBaddopr_btn(self,myitm):
        self.PSTBaddopr_btn = myitm
        return 

    def getPSTBNewOprProcTime(self):
        return self.PSTBNewOprProcTime

    def setPSTBNewOprProcTime(self,myitm):
        self.PSTBNewOprProcTime = myitm
        return 


    
    def getPSTBNewOprName(self):
        return self.PSTBNewOprName

    def setPSTBNewOprName(self,myitm):
        self.PSTBNewOprName = myitm
        return 

    def getPSTBnewopr_btn(self):
        return self.PSTBnewopr_btn

    def setPSTBnewopr_btn(self,myitm):
        self.PSTBnewopr_btn = myitm
        return 

    def getPSTBoperations(self):
        return self.PSTBoperations

    def setPSTBoperations(self,myitm):
        self.PSTBoperations = myitm
        return 
    

    def getPSTBprd_lbl(self):
        return self.PSTBprd_lbl

    def setPSTBprd_lbl(self,myitm):
        self.PSTBprd_lbl = myitm
        return 
 
    def getPSTBcnclprod_btn(self):
        return self.PSTBcnclprod_btn

    def setPSTBcnclprod_btn(self,myitm):
        self.PSTBcnclprod_btn = myitm
        return 
        
    
    def getPSTBaddprod_btn(self):
        return self.PSTBaddprod_btn

    def setPSTBaddprod_btn(self,myitm):
        self.PSTBaddprod_btn= myitm
        return 
        

    def getPSTBNewProdPN(self):
        return self.PSTBNewProdPN

    def setPSTBNewProdPN(self,myitm):
        self.PSTBNewProdPN= myitm
        return 
        
    
    def getPSTBNewProdStocklvl(self):
        return self.PSTBNewProdStocklvl

    def setPSTBNewProdStocklvl(self,myitm):
        self.PSTBNewProdStocklvl= myitm
        return 
        


    def getPSTBNewProdName(self):
        return self.PSTBNewProdName

    def setPSTBNewProdName(self,myitm):
        self.PSTBNewProdName= myitm
        return 
        

    def setDataManager(self,DM):
        self.DataManager = DM
        return

  
    def setPSTBnewprd_btn(self,myitm):
        self.PSTBnewprd_btn= myitm
        return 
    
    def getPSTBnewprd_btn(self):
        return self.PSTBnewprd_btn

    def setPSTBProdList2(self,pdlist):
        self.PSTBProdList2= pdlist
        return 
        
    def getPSTBProdList2(self):
        return self.PSTBProdList2

    def getPSTBProdList(self):
        return self.PSTBProdList

    def setPSTBProdList(self,pdlist):
        self.PSTBProdList= pdlist
        return 
    
    def getPSTBtyp_lbl(self):
        return self.PSTBtyp_lbl

    def setPSTBtyp_lbl(self,reslbl):
        self.PSTBtyp_lbl = reslbl
        return 
        
    def getPSTBres_lbl(self):
        return self.PSTBres_lbl

    def setPSTBres_lbl(self,reslbl):
        self.PSTBres_lbl = reslbl
        return 



    def setProdSystemTab(self,mytab):
        self.ProdSystemTab = mytab
        return 

    def getPSTBcanclres_btn(self):
        return self.PSTBcanclres_btn

    def setPSTBcanclres_btn(self,clresbtn):
        self.PSTBcanclres_btn = clresbtn
        return 

    def getPSTBnewres_btn(self):
        return self.PSTBnewres_btn

    def setPSTBnewres_btn(self,nwresbtn):
        self.PSTBnewres_btn = nwresbtn
        return 

    def getPSTBaddres_btn(self):
        return self.PSTBaddres_btn

    def setPSTBaddres_btn(self,resbtn):
        self.PSTBaddres_btn = resbtn
        return 

    def getPSTBNewResCap(self):
        return self.PSTBNewResCap

    def setPSTBNewResCap(self,rescap):
        self.PSTBNewResCap = rescap
        return 

    def getPSTBNewResType(self):
        return self.PSTBNewResType

    def setPSTBNewResType(self,restype):
        self.PSTBNewResType = restype
        return 

    def getPSTBNewResName(self):
        return self.PSTBNewResName

    def setPSTBNewResName(self,resname):
        self.PSTBNewResName = resname
        return 

    def getPSTBResList(self):
        return self.PSTBResList

    def setPSTBResList(self,reslist):
        self.PSTBResList = reslist
        return 
    def getPSTBProdList(self):
        return self.PSTBProdList

    def setPSTBProdList(self,prdlist):
        self.PSTBProdList = prdlist
        return 

    def getPLTBmakeplan_btn(self):
        return self.PLTBmakeplan_btn
    def setPLTBmakeplan_btn(self,prdlist):
        self.PLTBmakeplan_btn = prdlist
        return 


    def ApplyVisuals(self,itemstoshow,itemstohide,itemstoreset):

        for item in itemstoreset:
            item.value = ''
    
        for item in itemstoshow:
            item.layout.display = 'block'
            item.layout.visibility  = 'visible'
    
        for item in itemstohide:
            item.layout.visibility  = 'hidden'
            item.layout.display = 'none'

        return


        
    def generatePLTAB(self):

        self.setPLTBresult2exp(widgets.Textarea(value='', placeholder='',description='Summary',disabled=True))
     
        self.getPLTBresult2exp().layout.height = '150px'
        self.getPLTBresult2exp().layout.width = "90%"

        self.setPLTBmakeplan_btn(widgets.Button(description="Make Plan"))
        self.getPLTBmakeplan_btn().on_click(self.getPlanningManager().MakeDeliveryPlan)
        
        tab_3 = VBox(children = [self.getPLTBmakeplan_btn(),self.getPLTBresult2exp()])

        itemstohide = [self.getPSTBNewResName(),self.getPSTBNewResType(),self.getPSTBNewResCap(),self.getPSTBres_lbl(),
        self.getPSTBaddres_btn(),self.getPSTBcanclres_btn(),self.getPSTBtyp_lbl(),
        self.getPSTBNewProdName(),self.getPSTBNewProdPN(),self.getPSTBNewProdStocklvl(),self.getPSTBprd_lbl(),
        self.getPSTBaddprod_btn(),self.getPSTBaddopr_btn(),self.getPSTBcnclprod_btn(),self.getPSTBNewOprName(),self.getPSTBNewOprProcTime(),
        self.getPSTBcanclopr_btn(),self.getPSTBpn_lbl(),self.getPSTBmyopr_lbl(),
        self.getCOTBNewOrderName(),self.getCOTBNewOrderQ(),self.getCOTBNewOrderDeadLine(),self.getCOTBaddord_btn(),self.getCOTBcnclord_btn()]
         
        self.ApplyVisuals([],itemstohide,[])
          
        return tab_3

    def generateCOTAB(self):

        prd_box2 = VBox(children=[widgets.Label(value ='Product List'),self.getPSTBProdList()])

        self.setCOTBnewrdr_btn(widgets.Button(description="New Order"))
        self.getCOTBnewrdr_btn().on_click(self.CreateOrder)
        self.setCOTBNewOrderName(widgets.Text(description ='Name:',value=''))
        self.setCOTBNewOrderQ(widgets.Text(description ='Quantity:',value =''))
        self.setCOTBNewOrderDeadLine(widgets.DatePicker(description='Select', disabled=False ))
        
        self.setCOTBaddord_btn(widgets.Button(description="Add Order"))
        self.getCOTBaddord_btn().on_click(self.AddOrder)
        
        self.setCOTBcnclord_btn(widgets.Button(description="Cancel"))
        self.getCOTBcnclord_btn().on_click(self.CancelOrder)
        
        self.setCOTBcasename(widgets.Text(description ='Case:',value=''))
        self.setCOTBsave_bttn(widgets.Button(description="Save"))
        self.getCOTBsave_bttn().on_click(self.DataManager.SaveInstance)
        
        
        self.setCOTBorders(widgets.Select(options=[],description = ''))
        ord_box = VBox(children=[widgets.Label(value ='Order List'),self.getCOTBorders()])
        #checktext =widgets.Text(description ='Check:',value='')
        
        
        
        tb2_vbox = VBox(children = [HBox(children=[prd_box2]),self.getCOTBnewrdr_btn(),self.getCOTBNewOrderName(),self.getCOTBNewOrderQ(),self.getCOTBNewOrderDeadLine(),HBox(children=[self.getCOTBaddord_btn(),self.getCOTBcnclord_btn()])
                                    ,ord_box,HBox(children=[self.getCOTBsave_bttn(),self.getCOTBcasename()])])

        if not self.IsEditMode():
            self.ApplyVisuals([],[self.getCOTBNewOrderName(),self.getCOTBNewOrderQ(),self.getCOTBNewOrderDeadLine(),self.getCOTBnewrdr_btn(),self.getCOTBaddord_btn(),self.getCOTBcnclord_btn(),self.getCOTBsave_bttn(),self.getCOTBcasename(),prd_box2],[])
           
        
        
        tab_2 = HBox(children=[tb2_vbox])
     
        return tab_2

    def generatePSTAB(self):

        self.setPSTBResList(widgets.Select(options=[],description = ''))
        res_box = VBox(children=[widgets.Label(value ='Resource List'),self.getPSTBResList()])
        
        
        self.setPSTBnewres_btn(widgets.Button(description="New Resource"))
        self.getPSTBnewres_btn().on_click(self.CreateResource)
        
        self.setPSTBNewResName(widgets.Text(description ='Name:',value=''))
        self.setPSTBNewResType(widgets.Text(description ='Type:',value =''))
        self.setPSTBNewResCap(widgets.Text(description ='Daily Capacity:',value =''))
        
        self.setPSTBaddres_btn(widgets.Button(description="Add Resource"))
        self.getPSTBaddres_btn().on_click(self.AddResource)
        
        self.setPSTBcanclres_btn(widgets.Button(description="Cancel"))
        self.getPSTBcanclres_btn().on_click(self.CancelResource)
        
        self.setPSTBres_lbl(widgets.Label(value ='Selected Resource:'))
        self.setPSTBtyp_lbl(widgets.Label(value ='Type:'))
        
        ressel_box = VBox(children=[self.getPSTBres_lbl(),self.getPSTBtyp_lbl()])
        
        tb4_vbox1 = VBox(children = [HBox(children=[res_box]),self.getPSTBnewres_btn(),self.getPSTBNewResName(),self.getPSTBNewResType(),self.getPSTBNewResCap(),HBox(children=[self.getPSTBaddres_btn(),self.getPSTBcanclres_btn()])
                                     ,ressel_box])

        if not self.IsEditMode():
            self.ApplyVisuals([],[self.getPSTBNewResName(),self.getPSTBNewResType(),self.getPSTBNewResCap(),self.getPSTBaddres_btn(),self.getPSTBcanclres_btn(),self.getPSTBnewres_btn()],[])
            

        self.setPSTBProdList(widgets.Select(options=[],description = ''))
    
        self.setPSTBProdList2(widgets.Select(options=[],description = ''))
        p_box = VBox(children=[widgets.Label(value ='Product List'),self.getPSTBProdList()])



        
        
        self.setPSTBnewprd_btn(widgets.Button(description="New Product"))
        self.getPSTBnewprd_btn().on_click(self.CreateProduct)
        self.setPSTBNewProdName(widgets.Text(description ='Name:',value=''))
        self.setPSTBNewProdPN(widgets.Text(description ='PN:',value =''))
        self.setPSTBNewProdStocklvl(widgets.Text(description ='Stock Level:',value =''))
        self.setPSTBaddprod_btn(widgets.Button(description="Add Product"))
        self.getPSTBaddprod_btn().on_click(self.AddProduct)
        
        self.setPSTBcnclprod_btn(widgets.Button(description="Cancel"))
        self.getPSTBcnclprod_btn().on_click(self.CancelProduct)
        
        self.setPSTBprd_lbl(widgets.Label(value ='Selected Product:'))
        self.setPSTBpn_lbl(widgets.Label(value ='PN:'))
        
        
        prdsel_box = VBox(children=[self.getPSTBprd_lbl(),self.getPSTBpn_lbl()])
        
        
        tb4_vbox2 = VBox(children = [HBox(children=[p_box]),self.getPSTBnewprd_btn(),self.getPSTBNewProdName(),self.getPSTBNewProdPN(),self.getPSTBNewProdStocklvl(),HBox(children=[self.getPSTBaddprod_btn(),self.getPSTBcnclprod_btn()]),prdsel_box])

        if not self.IsEditMode():
            self.ApplyVisuals([],[self.getPSTBNewProdName(),self.getPSTBNewProdPN(),self.getPSTBNewProdStocklvl(),self.getPSTBaddprod_btn(),self.getPSTBcnclprod_btn(),self.getPSTBnewprd_btn()],[])
        

    

        self.setPSTBoperations(widgets.Select(options=[],description = ''))
        op_box = VBox(children=[widgets.Label(value ='Operation List'),self.getPSTBoperations()])
        
        
        self.setPSTBnewopr_btn(widgets.Button(description="New Operation"))
        self.getPSTBnewopr_btn().on_click(self.CreateOperation)
        self.setPSTBNewOprName(widgets.Text(description ='Name:',value=''))
        self.setPSTBNewOprProcTime(widgets.Text(description ='Process Time:',value=''))
        self.setPSTBaddopr_btn(widgets.Button(description="Add Operation"))
        self.getPSTBaddopr_btn().on_click(self.AddOperation)
        self.setPSTBcanclopr_btn(widgets.Button(description="Cancel"))
        self.getPSTBcanclopr_btn().on_click(self.CancelOperation)
        

        
        self.setPSTBmyopr_lbl(widgets.Label(value ='Selected Operation:'))
        oprdsel_box = VBox(children=[self.getPSTBmyopr_lbl()])
        
        
        tb4_vbox3 = VBox(children = [HBox(children=[op_box]),self.getPSTBnewopr_btn(),self.getPSTBNewOprName(),self.getPSTBNewOprProcTime(),HBox(children=[self.getPSTBaddopr_btn(),self.getPSTBcanclopr_btn()])
                                    ,oprdsel_box])
        
        
        self.setPSTBopr_lbl(widgets.Label(value ='Operation:'))
        self.setPSTBoprtp_lbl(widgets.Label(value ='Type:'))
        
        oprboxxlay = widgets.Layout(width = '99%')
        oprsel_box = VBox(children=[self.getPSTBopr_lbl(),self.getPSTBoprtp_lbl()],layout = oprboxxlay)

        if not self.IsEditMode():
            self.ApplyVisuals([],[self.getPSTBnewopr_btn(),self.getPSTBNewOprName(),self.getPSTBNewOprProcTime(),self.getPSTBaddopr_btn(),self.getPSTBcanclopr_btn()],[])
        

    
        

       
        self.PSTBresoprmt_btn= None
        self.PSTBprodoprmt_btn= None
        self.PSTBprec_btn= None
        
        
        self.setPSTBresoprmt_btn(widgets.Button(description="Assign Resource"))
        self.getPSTBresoprmt_btn().on_click(self.ResOprMatchClick)

        if self.IsEditMode():
            ResOpr_box = HBox(children=[self.getPSTBResList(),self.getPSTBoperations(),self.getPSTBresoprmt_btn()])
        
        self.setPSTBprodoprmt_btn(widgets.Button(description="Assign Operation"))
        self.getPSTBprodoprmt_btn().on_click(self.AssignOprClick)

        if self.IsEditMode():
            ProOpr_box = HBox(children=[self.getPSTBProdList(),self.getPSTBoperations(),self.getPSTBprodoprmt_btn()])
        
        self.setPSTBprec_btn(widgets.Button(description="Define Precedence"))
        self.getPSTBprec_btn().on_click(self.PrecedenceClick)

        if self.IsEditMode():
            ProPro_box = HBox(children=[self.getPSTBProdList(),self.getPSTBProdList2(),self.getPSTBprec_btn()])

        if self.IsEditMode():
            tab_4 = VBox(children=[HBox(children=[tb4_vbox1,tb4_vbox2,tb4_vbox3]),ResOpr_box,ProPro_box,ProOpr_box])
        else:
            tab_4 = VBox(children=[HBox(children=[tb4_vbox1,tb4_vbox2,tb4_vbox3])])
        

        return tab_4



    def get_case_selection_tab(self):
        
        global wsheets, wslay, butlay, DFPage
        
       
        self.setFolderNameTxt(widgets.Text(description ='Folder name:',value = 'UseCases'))
        self.getFolderNameTxt().on_submit(self.DataManager.on_submit_func)
       
        self.setCasesDrop(widgets.Dropdown(options=[], description='Use Cases:'))
        self.setCaseInfo(widgets.Textarea(value='', placeholder='',description='Case Info:',disabled=True,layout = Layout(height ="200px" ,width='60%')))   

    
        self.setReadFileBtn(widgets.Button(description="Read") )
        self.getReadFileBtn().on_click(self.DataManager.read_dataset)
       

        tablayout = widgets.Layout(height='500px')
      
       
        tab_1 = VBox(children=[
            HBox(children = [self.getFolderNameTxt(),self.getCasesDrop(),self.getReadFileBtn()]),self.getCaseInfo()],layout=tablayout)

       
        return tab_1

    def RefreshViews(self):
        
        self.getPSTBResList().options = [resname for resname in self.DataManager.getResources().keys()]
        self.getPSTBoperations().options = [opname for opname in self.DataManager.getOperations().keys()]
        self.getPSTBProdList().options = [opname for opname in self.DataManager.getProducts().keys()]
        self.getPSTBProdList2().options = [opname for opname in self.DataManager.getProducts().keys()]
        self.getCOTBorders().options = [ordname for ordname in self.DataManager.getCustomerOrders().keys()]
        
        return
    def CreateResource(self,event):

        #self.getCaseInfo().value += ">>>resource.. "+"\n"
        
        itemstoshow = [self.getPSTBNewResName(),self.getPSTBNewResType(),self.getPSTBNewResCap(),self.getPSTBaddres_btn(),self.getPSTBcanclres_btn()]
        itemstohide = [self.getPSTBnewres_btn()]; itemstoreset = itemstoshow[:3]  
        self.ApplyVisuals(itemstoshow,itemstohide,itemstoreset)
        return 
        
    def AddResource(self,event):
    
        self.DataManager.CreateResource((self.getPSTBNewResName().value,self.getPSTBNewResType().value,self.getPSTBNewResCap().value),self.getPSTBResList())
    
        itemstohide = [self.getPSTBNewResName(),self.getPSTBNewResType(),self.getPSTBNewResCap(),self.getPSTBaddres_btn(),self.getPSTBcanclres_btn()]
        itemstoshow = [self.getPSTBnewres_btn()]
        self.ApplyVisuals(itemstoshow,itemstohide,[])
        return
    
    def CancelResource(self,event):
     
        itemstohide = [self.getPSTBNewResName(),self.getPSTBNewResType(),self.getPSTBNewResCap(),self.getPSTBaddres_btn(),self.getPSTBcanclres_btn()]
        itemstoshow =  [self.getPSTBnewres_btn()]
        self.ApplyVisuals(itemstoshow,itemstohide,[])
        return
        
    def CreateProduct(self,event):

        #self.getCaseInfo().value += ">>>create prod... "+"\n"
        itemstoshow = [self.getPSTBNewProdName(),self.getPSTBNewProdPN(),self.getPSTBNewProdStocklvl(),self.getPSTBaddprod_btn(),self.getPSTBcnclprod_btn()]
        itemstohide = [self.getPSTBnewprd_btn()]; itemstoreset = itemstoshow[:3]  
        self.ApplyVisuals(itemstoshow,itemstohide,itemstoreset)
    
        return
    
    
    def CancelProduct(self,event):
     
        itemstohide = [self.getPSTBNewProdName(),self.getPSTBNewProdPN(),self.getPSTBNewProdStocklvl(),self.getPSTBaddprod_btn(),self.getPSTBcnclprod_btn()]
        itemstoshow = [self.getPSTBnewprd_btn()]; 
        self.ApplyVisuals(itemstoshow,itemstohide,[])
    
        return
        
    def AddProduct(self,event):
                                
        self.DataManager.CreateProduct((self.getPSTBNewProdName().value,self.getPSTBNewProdPN().value,
                                                                self.getPSTBNewProdStocklvl().value),self.getPSTBProdList(),self.getPSTBProdList2())
     
        itemstohide = [self.getPSTBNewProdName(),self.getPSTBNewProdPN(),self.getPSTBNewProdStocklvl(),self.getPSTBaddprod_btn(),self.getPSTBcnclprod_btn()]
        itemstoshow = [self.getPSTBnewprd_btn()]; 
        self.ApplyVisuals(itemstoshow,itemstohide,[])
    
        return

    def CreateOperation(self,event):
    
        itemstoshow = [self.getPSTBNewOprName(),self.getPSTBNewOprProcTime(),self.getPSTBaddopr_btn(),self.getPSTBcanclopr_btn()]
        itemstohide = [self.getPSTBnewopr_btn()]; itemstoreset = itemstoshow[:1]  
        self.ApplyVisuals(itemstoshow,itemstohide,itemstoreset)
        return 
        
    def CancelOperation(self,event):
    
        itemstohide = [self.getPSTBNewOprName(),self.getPSTBNewOprProcTime(),self.getPSTBaddopr_btn(),self.getPSTBcanclopr_btn()]
        itemstoshow = [self.getPSTBnewopr_btn()]
        self.ApplyVisuals(itemstoshow,itemstohide,[])
        return
        
    def AddOperation(self,event):
        
        self.DataManager.CreateOperation((self.getPSTBNewOprName().value,self.getPSTBNewOprProcTime().value),self.getPSTBoperations())
     
        itemstohide = [self.getPSTBNewOprName(),self.getPSTBNewOprProcTime(),self.getPSTBaddopr_btn(),self.getPSTBcanclopr_btn()]
        itemstoshow = [self.getPSTBnewopr_btn()]
        self.ApplyVisuals(itemstoshow,itemstohide,[])
    
        
        return

    def CreateOrder(self,event):   
        itemstoshow = [self.getCOTBNewOrderName(),self.getCOTBNewOrderQ(),self.getCOTBNewOrderDeadLine(),self.getCOTBaddord_btn(),self.getCOTBcnclord_btn()]
        itemstohide = [self.getCOTBnewrdr_btn()]; itemstoreset = itemstoshow[:2]  
        self.ApplyVisuals(itemstoshow,itemstohide,itemstoreset)
    
        return
    
    def CancelOrder(self,event):
        itemstohide = [VisMgr.getCOTBNewOrderName(),VisMgr.getCOTBNewOrderQ(),VisMgr.getCOTBNewOrderDeadLine(),VisMgr.getCOTBaddord_btn(),VisMgr.getCOTBcnclord_btn()]
        itemstoshow = [VisMgr.getCOTBnewrdr_btn()]
        self.ApplyVisuals(itemstoshow,itemstohide,[])
    
        return
        
    def AddOrder(self,event):

        #def __init__(self,myid,myname,myprodid,myprodname,myqnty,myddline):
       
        self.getCaseInfo().value += ">>>create customer order... "+"\n"
        self.DataManager.CreateCustomerOrder((self.getCOTBNewOrderName().value,self.getCOTBNewOrderQ().value,self.getCOTBNewOrderDeadLine().value))
     
        itemstohide = [self.getCOTBNewOrderName(),self.getCOTBNewOrderQ(),self.getCOTBNewOrderDeadLine(),self.getCOTBaddord_btn(),self.getCOTBcnclord_btn()]
        itemstoshow = [self.getCOTBnewrdr_btn()]
        
        self.ApplyVisuals(itemstoshow,itemstohide,[])
    
        return
    def ResOprMatchClick(self,event):
        self.DataManager.MatchResourceOperation(self.getPSTBResList(),self.getPSTBoperations())
        return

    def PrecedenceClick(self,event):
        self.DataManager.DefinePrecedence(self.getPSTBProdList(),self.getPSTBProdList2())
        return
    
    def AssignOprClick(self,event):
        self.DataManager.AssignOperation(self.getPSTBProdList(),self.getPSTBoperations())
        return


  

#############################################################################################################################################  







#############################################################################################################################################   




 