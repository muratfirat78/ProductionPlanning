# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 11:46:59 2024

@author: mfirat
"""

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
from PlanningObjects import *
from IPython.display import display, HTML

warnings.filterwarnings("ignore")
display(HTML("<style>.red_label { color:red }</style>"))
display(HTML("<style>.blue_label { color:blue }</style>"))

class VisualManager():

    def __init__(self):  


        self.EditMode = True
        self.DataManager = None
        self.PlanningManager = None
        self.SchedulingManager = None
        self.SimulationManager = None
        self.ProdSystemTab = None
        self.PSTBBOMOutput = None

        self.SchedulingTab = None
        self.SimulationTab = None
        self.ProductionProgressTab = None

        self.PSTBOprRes = None
        
        self.PSTBResList = None
        self.PSTBNewResName = None
        self.PSTBNewResType = None
        self.PSTBResName = None
        self.PSTBResType = None
        self.PSTBResOprs = None
        self.PSTBResCap = None
        self.PSTBNewResCap = None
        self.PSTBaddres_btn = None
        self.PSTBnewres_btn = None
        self.PSTBcanclres_btn = None
        self.PSTBres_lbl = None
        self.PSTBtyp_lbl =  None

        self.BOMTree = None
        self.BOMTreeRootNode = None


        self.PSTBFinalProd = None
        self.PSTBQuantity = None
        self.PSTBDeadLine = None

        self.PSTBeditres_btn = None
        self.PSTBeditprd_btn = None


        self.USTBCustomerOders = None
        self.USTBProducts = None
        self.USTBRawMaterials = None
        self.USTBRawResources = None

        self.PLTBDisplayPeriod = 4 # weeks
        
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

        self.PSTBProdName = None
        self.PSTBProdPN = None
        self.PSTBProdStocklvl = None
        self.PSTBProdOprs = None

        self.PSTBOprName = None
        self.PSTBOprProcTime = None

        self.ResourcetoEdit = None
        self.PSTBResSearch = None
        self.PSTBProdSearch = None

        self.PLTBPlanStart = None
        self.PLTBPlanEnd = None
        self.PLTBPlanChange = None

        self.PLTBDesciptives = None
        self.PLTBDisplayPeriod = None
     


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
        self.ProdSearch = None


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
        self.PLTBmakeplan_btn = None
        self.PLTBrawlist = None
        self.PLTBresult2exp = None
        self.PLTBStockLevels = None
        self.PLTBCheckRaw = None
        self.PLTBCheckCapacity = None

        self.PLTBOrdlist = None
        self.PLTBOrdProd = None

        self.PSchTBmakesch_btn = None
        self.PSchJoblist = None
        self.PSchResources = None
        self.PSchScheRes = None
    
        self.CaseInfo = None
        self.DiagInfo = None

        self.FolderNameTxt = None
        self.CasesDrop = None
        self.ReadFileBtn = None

        self.DiagTree = None
        self.PLTBDiagOutput = None
        self.DiagTreeRootNode = None


        self.UseResTree= None
        self.UseResTreeRootNode= None
        self.PLTBUseResOutput= None
        self.PSTBProdBatch = None

        self.DataDiaBtn = None # Button for data diagnostics
        self.DataDiaOpt = None

        self.NewCustOrdrs_btn = None
        self.NewProd_btn = None

        self.UpdStocks_btn = None
        

       

        return

 
    def setSimulationTab(self,myit):
        self.SimulationTab = myit
        return

    def getSimulationTab(self):
        return self.SimulationTab
       


    def setSimulationManager(self,myit):
        self.SimulationManager = myit
        return

    def getSimulationManager(self):
        return self.SimulationManager
       

    def setUpdStocks_btn(self,myit):
        self.UpdStocks_btn = myit
        return

    def getUpdStocks_btn(self):
        return self.UpdStocks_btn


    def setNewProd_btn(self,myit):
        self.NewProd_btn = myit
        return

    def getNewProd_btn(self):
        return self.NewProd_btn

    def setPSTBProdBatch(self,myit):
        self.PSTBProdBatch = myit
        return

    def getPSTBProdBatch(self):
        return self.PSTBProdBatch

    def setNewCustOrdrs_btn(self,myit):
        self.NewCustOrdrs_btn = myit
        return

    def getNewCustOrdrs_btn(self):
        return self.NewCustOrdrs_btn

     

    def setPSTBOprRes(self,myit):
        self.PSTBOprRes = myit
        return

    def getPSTBOprRes(self):
        return self.PSTBOprRes

     

    def setPLTBUseResOutput(self,myit):
        self.PLTBUseResOutput = myit
        return

    def getPLTBUseResOutput(self):
        return self.PLTBUseResOutput

    def setUseResTree(self,myit):
        self.UseResTree = myit
        return

    def getUseResTree(self):
        return self.UseResTree

    def setUseResTreeRootNode(self,myit):
        self.UseResTreeRootNode = myit
        return

    def getUseResTreeRootNode(self):
        return self.UseResTreeRootNode






    def setDiagTreeRootNode(self,myit):
        self.DiagTreeRootNode = myit
        return

    def getDiagTreeRootNode(self):
        return self.DiagTreeRootNode
        

    def setPLTBDiagOutput(self,myit):
        self.PLTBDiagOutput = myit
        return

    def getPLTBDiagOutput(self):
        return self.PLTBDiagOutput
        
    

    def setDiagTree(self,myit):
        self.DiagTree = myit
        return

    def getDiagTree(self):
        return self.DiagTree

    


    def setUSTBRawResources(self,myit):
        self.USTBRawResources = myit
        return

    def getUSTBRawResources(self):
        return self.USTBRawResources

    def setPSTBBOMOutput(self,myit):
        self.PSTBBOMOutput = myit
        return

    def getPSTBBOMOutput(self):
        return self.PSTBBOMOutput

    def setBOMTreeRootNode(self,myit):
        self.BOMTreeRootNode = myit
        return

    def getBOMTreeRootNode(self):
        return self.BOMTreeRootNode

    

    def setProdSearch(self,myit):
        self.ProdSearch = myit
        return

    def getProdSearch(self):
        return self.ProdSearch

    def setBOMTree(self,myit):
        self.BOMTree = myit
        return

    def getBOMTree(self):
        return self.BOMTree


    def setUSTBRawMaterials(self,myit):
        self.USTBRawMaterials = myit
        return

    def getUSTBRawMaterials(self):
        return self.USTBRawMaterials


    def setUSTBProducts(self,myit):
        self.USTBProducts = myit
        return

    def getUSTBProducts(self):
        return self.USTBProducts

    def setUSTBCustomerOders(self,myit):
        self.USTBCustomerOders = myit
        return

    def getUSTBCustomerOders(self):
        return self.USTBCustomerOders


    

    def setPLTBDisplayPeriod(self,myit):
        self.PLTBDisplayPeriod = myit
        return

    def getPLTBDisplayPeriod(self):
        return self.PLTBDisplayPeriod

    

    def setPLTBDesciptives(self,myit):
        self.PLTBDesciptives = myit
        return

    def getPLTBDesciptives(self):
        return self.PLTBDesciptives

    def setPLTBOrdProd(self,myit):
        self.PLTBOrdProd = myit
        return
        
    def getPLTBOrdProd(self):
        return self.PLTBOrdProd


    def setPLTBOrdlist(self,myit):
        self.PLTBOrdlist = myit
        return
        
    def getPLTBOrdlist(self):
        return self.PLTBOrdlist


    def setPSTBResSearch(self,myit):
        self.PSTBResSearch  = myit
        return
        
    def getPSTBResSearch(self):
        return self.PSTBResSearch

    def setPLTBPlanStart(self,myit):
        self.PLTBPlanStart  = myit
        return
        
    def getPLTBPlanStart (self):
        return self.PLTBPlanStart

   
    
    def setPLTBPlanEnd(self,myit):
        self.PLTBPlanEnd  = myit
        return
        
    def getPLTBPlanEnd(self):
        return self.PLTBPlanEnd

    def setPSTBProdSearch(self,myit):
        self.PSTBProdSearch  = myit
        return
        
    def getPSTBProdSearch(self):
        return self.PSTBProdSearch
        

    def setResourcetoEdit(self,myit):
        self.ResourcetoEdit = myit
        return

    def getResourcetoEdit(self):
        return self.ResourcetoEdit 
       
        

    def setPSTBeditres_btn(self,myit):
        self.PSTBeditres_btn = myit
        return
        
    def getPSTBeditres_btn(self):
        return self.PSTBeditres_btn


    
    def setPSTBeditprd_btn(self,myit):
        self.PSTBeditprd_btn = myit
        return
        
    def getPSTBeditprd_btn(self):
        return self.PSTBeditprd_btn

     

    def getPSTBOprName(self):
        return self.PSTBOprName

    def getPSTBOprProcTime(self):
        return self.PSTBOprProcTime

    def setPSTBOprName(self,myit):
        self.PSTBOprName = myit
        return 

    def setPSTBOprProcTime(self,myit):
        self.PSTBOprProcTime = myit
        return 
        
    def setPSTBProdName(self,myit):
        self.PSTBProdName = myit
        
    def getPSTBProdName(self):
        return self.PSTBProdName 
     
    def getPSTBProdPN(self):
        return self.PSTBProdPN
 
    def setPSTBProdPN(self,myit):
        self.PSTBProdPN = myit
        return
        
    def setPSTBProdStocklvl(self,myit):
        self.PSTBProdStocklvl = myit
        return

    def getPSTBProdStocklvl(self):
        return self.PSTBProdStocklvl


    def setPSTBProdOprs(self,myit):
        self.PSTBProdOprs = myit
        return
   
        
    def setPSchScheRes(self,myitm):
        self.PSchScheRes = myitm
        return
        
    def getPSchScheRes(self):
        return self.PSchScheRes


    def setPSchResources(self,myitm):
        self.PSchResources = myitm
        return
        
    def getPSchResources(self):
        return self.PSchResources

    def setPSchJoblist(self,myitm):
        self.PSchJoblist = myitm
        return
        
    def getPSchJoblist(self):
        return self.PSchJoblist


    def setPSchTBmakesch_btn(self,myitm):
        self.PSchTBmakesch_btn = myitm
        return
        
    def getPSchTBmakesch_btn(self):
        return self.PSchTBmakesch_btn


    def setEditMode(self,edit):
        self.EditMode = edit
        
    def getPLTBOrders(self):
        return self.PLTBOrders

    def setPLTBOrders(self,myitm):
        self.PLTBOrders= myitm
        return

    def getPLTBCheckCapacity(self):
        return self.PLTBCheckCapacity

    def setPLTBCheckCapacity(self,myitm):
        self.PLTBCheckCapacity= myitm
        return
    def getPLTBCheckRaw(self):
        return self.PLTBCheckRaw

    def setPLTBCheckRaw(self,myitm):
        self.PLTBCheckRaw = myitm
        return 
    def getPLTBStockLevels(self):
        return self.PLTBStockLevels

    def setPLTBStockLevels(self,myitm):
        self.PLTBStockLevels = myitm
        return 

    def getPLTBrawlist(self):
        return self.PLTBrawlist

    def setPLTBrawlist(self,myitm):
        self.PLTBrawlist = myitm
        return 
    def getPlanningManager(self):
        return self.PlanningManager

    def setPlanningManager(self,myitm):
        self.PlanningManager = myitm
        return 

    def getSchedulingManager(self):
        return self.SchedulingManager

    def setSchedulingManager(self,myitm):
        self.SchedulingManager = myitm
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
        
    def getDiagInfo(self):
        return self.DiagInfo

    def setDiagInfo(self,myitm):
        self.DiagInfo = myitm
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

    def setPSTBResName(self,myit):
        self.PSTBResName = myit
        return
    def setPSTBResCap(self,myit):
        self.PSTBResCap = myit
        return
    def setPSTBResType(self,myit):
        self.PSTBResType = myit
        return
        
    def setPSTBResOprs(self,myit):
        self.PSTBResOprs = myit
        return   


    def getPSTBResName(self):
        return self.PSTBResName
        
    def getPSTBResCap(self):
        return self.PSTBResCap
        
    def getPSTBResType(self):
        return self.PSTBResType
        
        
    def getPSTBResOprs(self):
        return self.PSTBResOprs
            
        
       

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

    def setSchedulingTab(self,myit):
        self.SchedulingTab = myit
        return
    
    def getSchedulingTab(self):
        return self.SchedulingTab

    def setProductionProgressTab(self,myit):
        self.ProductionProgressTab = myit
        return
    
    def getProductionProgressTab(self):
        return self.ProductionProgressTab

    def getPSTBFinalProd(self):
        return self.PSTBFinalProd
    def setPSTBFinalProd(self,myit):
        self.PSTBFinalProd = myit
        return

    def getPSTBQuantity(self):
        return self.PSTBQuantity
    def setPSTBQuantity(self,myit):
        self.PSTBQuantity = myit
        return

    def getPSTBDeadLine(self):
        return self.PSTBDeadLine
    def setPSTBDeadLine(self,myit):
        self.PSTBDeadLine = myit
        return

    def getDataDiaBtn(self):
        return self.DataDiaBtn

    def setDataDiaBtn(self,myint):
        self.DataDiaBtn = myint
        return

    def getDataDiaOpt(self):
        return self.DataDiaOpt

    def setDataDiaOpt(self,myint):
        self.DataDiaOpt = myint
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


    def Rawclick(self,event):  
 
        #self.getPLTBresult2exp().value+="raw..."+str(rawname)+"\n"
        
        if (event['name']  == "_options_labels") or (event['name']  == "options"):
            return

        if not self.DataManager.isOnlineVersion():
            if not "new" in event:
                return
    
            if not "index" in event['new']:
                return

            selected = self.getPLTBrawlist().options[event["new"]["index"]]
        else:
            
            selected = self.getPLTBrawlist().value
       
        self.getPLTBresult2exp().value+=str(event)+"\n"
        self.getPLTBresult2exp().value+=str(self.getPLTBDesciptives().value)+"\n"
        self.getPLTBresult2exp().value+=str(event["new"]["index"])+"\n"
        self.getPLTBresult2exp().value+=str(self.getPLTBrawlist().options[event["new"]["index"]])+"\n"
        
        if (self.getPLTBDesciptives().value == 'Product Target Levels') or (self.getPLTBrawlist().options[event["new"]["index"]] == 'Product Target Levels' ):
            rawname = selected

            rawname = self.getPLTBrawlist().options[event["new"]["index"]]
           
            rawmat = None

            self.getPLTBresult2exp().value+=str(rawname in self.DataManager.getProducts())+"\n"
            
            for prodname,myprod in self.DataManager.getProducts().items():
                if len(myprod.getPredecessors()) == 0:
                    if rawname == prodname:
                        rawmat = myprod
                        break
    
            if rawmat == None:
                return
            
            
            
            with self.getPLTBStockLevels():
                clear_output()
                plandays = rawmat.getTargetLevels().keys()
                values = rawmat.getTargetLevels().values()

                total = sum([demand for myord,demand in rawmat.getDemandingOrders().items()])
    
                fig = plt.figure(figsize=(6, 4))
                ax = plt.subplot(111)
                ax.plot(plandays,values,  color='blue')
                #ax.set_title('Targets '+rawname) 
                plt.xticks(rotation=-45)
                plt.tight_layout()
                plt.show()
                
        if  self.getPLTBDesciptives().value == 'Resource Capacity Plans':
            res_name = selected
           
            my_res = None
            
            for resame,myres in self.DataManager.getResources().items():
                if resame == res_name:
                    my_res = myres
                    break
    
            if my_res == None:
                return


            with self.getPLTBStockLevels():
                clear_output()
                plandays = my_res.getCapacityLevels().keys()
                capvalues = [v for v in my_res.getCapacityLevels().values()]
                
                usevalues = []
                cumuseval = 0

                totalval = 0
                for cstord,usedict in my_res.getCapacityUsePlan().items():
                    totalval+=sum([v for v in usedict.values()])
                    
                for mydate in my_res.getCapacityLevels().keys():
                    for cstord,usedict in my_res.getCapacityUsePlan().items():
                        if mydate in usedict:
                            cumuseval+=usedict[mydate]
                    usevalues.append(cumuseval)  

                
                fig = plt.figure(figsize=(5, 3.5))
                ax = plt.subplot(111)
                ax.plot(plandays,usevalues,  color='blue')
                ax.plot(plandays,capvalues,  color='red')
                plt.xticks(rotation=-45)
                plt.tight_layout()
                plt.show()
                
            


        return
  
        
   
    def ShowJobs(self,event):

        selectedopr = self.getPSchResources().value

        if selectedopr == None:
            return

        if selectedopr == '':
            return

        
    
        joblist = [selectedopr,"hoi"]
        for prname,prod in self.DataManager.getProducts().items():
            if prod.getName() == selectedopr:
                for opr in prod.getOperations():
                    joblist.append("> Opr: "+opr.getName())
                    for job in opr.getJobs():
                        joblist.append(" >> "+job.getName()+", q: "+str(job.getQuantity())+", d: "+str(job.getDeadLine()))
                break
    
        
        self.getPSchJoblist().options = [j for j in joblist]   
       
        return

   

    def ShowOperation2(self,event):
        if event['type'] == 'change' and event['name'] == 'value':
            print("changed to %s" % event['new'])
        else:
            return
        
        selectedopr = self.getPSTBoperations().value
        sel_opr = None
        curr_prod = None
    
      
        itemstoshow = [self.getPSTBOprName(),self.getPSTBOprProcTime()]
        itemstohide = []; itemstoreset = []  
        self.ApplyVisuals(itemstoshow,itemstohide,itemstoreset)

        itemstohide = [self.getPSTBNewOprName(),self.getPSTBNewOprProcTime(),self.getPSTBaddopr_btn(),self.getPSTBcanclopr_btn()]
        itemstoshow = []; itemstoreset = itemstoshow[:1]  
        self.ApplyVisuals(itemstoshow,itemstohide,itemstoreset)

       

        for prname,prod in self.DataManager.getProducts().items():
            if prname == self.getPSTBProdName().value:
                curr_prod = prod
                break

        if curr_prod!= None:
            self.getPLTBresult2exp().value+=" Product->"+str(curr_prod.getName())+"\n"
   
        for operation in prod.getOperations():
            if operation.getName() == selectedopr:
                sel_opr = operation
                break
               

        
      

        if sel_opr!= None:
            self.getPSTBOprName().value = sel_opr.getName()
            self.getPSTBOprProcTime().value = str(round(sel_opr.getProcessTime(),3))

            res = None
            for resource in sel_opr.getRequiredResources():
                    res = resource
                    if isinstance(res,list):
                        res = resource[0]
                    break
                
            if len(sel_opr.getRequiredResources())>0:
                ops = [x.getName() for x in sel_opr.getRequiredResources()]
                self.getPSTBOprRes().options = ops
                self.getPSTBResSearch().value = ops[0]

        
                itemstoshow = [self.getPSTBResName(),self.getPSTBResType(),self.getPSTBResCap(),self.getPSTBeditres_btn()]
                itemstohide = []; itemstoreset = []  
                self.ApplyVisuals(itemstoshow,itemstohide,itemstoreset)
        
          
                myresname = self.getPSTBResSearch().value
        
                if myresname in self.DataManager.getResources():
                    res = self.DataManager.getResources()[myresname]
                    self.getPSTBResName().value = res.getName()
                    self.getPSTBResType().value = res.getType()
                    self.getPSTBResCap().value = str(res.getDailyCapacity())+" shift/day"
                else:
                    self.getPSTBResName().value = myresname+" not found.." 

        return

    def ShowProduct(self,event):

        if event['name'] !=  '_property_lock':
            return

        
        selectedprd = self.getPSTBProdList().options[event['new']['index']]
        sel_prod = None

    
      
        itemstoshow = [self.getPSTBeditprd_btn(),self.getPSTBProdName(),self.getPSTBProdPN(),self.getPSTBProdStocklvl()]
        itemstohide = []; itemstoreset = []  
        self.ApplyVisuals(itemstoshow,itemstohide,itemstoreset)

        itemstohide = [self.getPSTBNewProdName(),self.getPSTBNewProdPN(),self.getPSTBNewProdStocklvl(),self.getPSTBaddprod_btn(),self.getPSTBcnclprod_btn()]
        itemstoshow = [self.getPSTBnewprd_btn()]; itemstoreset = itemstoshow[:3]  
        self.ApplyVisuals(itemstoshow,itemstohide,itemstoreset)

     
        for prname,prod in self.DataManager.getProducts().items():
            if prname == selectedprd:
                sel_prod = prod
                break

        self.getPSTBOprName().value = ''
        self.getPSTBOprProcTime().value = ''

        
        self.getPSTBProdName().value = sel_prod.getName()
        self.getPSTBProdPN().value = sel_prod.getPN()
        if sel_prod.getBatchsize()!= None: 
            self.getPSTBProdBatch().value = str(sel_prod.getBatchsize())
        else:
            self.getPSTBProdBatch().value = "-"
        self.getPSTBProdStocklvl().value = str(sel_prod.getStockLevel())
        self.getPSTBoperations().options = [opr.getName() for opr in sel_prod.getOperations()]
        
        return

    
    def ShowProduct2(self,event):

        self.getPSTBProdPN().value = str(len(self.getBOMTreeRootNode().nodes))

        selectednode = self.RecFindSelected(self.getBOMTreeRootNode())

        
        selectedprodpn = selectednode.name
 
        sel_prod = None

      
        itemstoshow = [self.getPSTBeditprd_btn(),self.getPSTBProdName(),self.getPSTBProdPN(),self.getPSTBProdStocklvl()]
        itemstohide = []; itemstoreset = []  
        self.ApplyVisuals(itemstoshow,itemstohide,itemstoreset)

        itemstohide = [self.getPSTBNewProdName(),self.getPSTBNewProdPN(),self.getPSTBNewProdStocklvl(),self.getPSTBaddprod_btn(),self.getPSTBcnclprod_btn()]
        itemstoshow = [self.getPSTBnewprd_btn()]; itemstoreset = itemstoshow[:3]  
        self.ApplyVisuals(itemstoshow,itemstohide,itemstoreset)

     
        for prname,prod in self.DataManager.getProducts().items():
            if prod.getPN() == selectedprodpn:
                sel_prod = prod
                break
        if sel_prod == None:
            self.getPSTBProdPN().value = selectedprodpn+" not found..."
            return

        self.getPSTBOprName().value = ''
        self.getPSTBOprProcTime().value = ''

        self.getPSTBProdSearch().value = sel_prod.getName()
        self.getPSTBProdName().value = sel_prod.getName()
        self.getPSTBProdPN().value = sel_prod.getPN()
        if sel_prod.getBatchsize()!= None: 
            self.getPSTBProdBatch().value = str(sel_prod.getBatchsize())
        else:
            self.getPSTBProdBatch().value = "-"
        self.getPSTBProdStocklvl().value = str(sel_prod.getStockLevel())
        self.getPSTBoperations().options = [opr.getName() for opr in sel_prod.getOperations()]
        
        return
   

    def RecFindSelected(self,node):
    
        selected = None 
        if node.selected:
            selected = node
        else: 
            for subnode in node.nodes: 
                selected = self.RecFindSelected(subnode) 
                if selected != None:
                    break       
        return selected 

    def ShowResource(self,event):


        if event['name'] !=  '_property_lock':
            return

        
        selectedres = self.getPSTBResList().options[event['new']['index']]
        sel_resource = None

     

        itemstoshow = [self.getPSTBeditres_btn(),self.getPSTBResName(),self.getPSTBResType(),self.getPSTBResCap()]
        itemstohide = []; itemstoreset = []  
        self.ApplyVisuals(itemstoshow,itemstohide,itemstoreset)

        itemstohide  = [self.getPSTBNewResName(),self.getPSTBNewResType(),self.getPSTBNewResCap(),self.getPSTBaddres_btn(),self.getPSTBcanclres_btn()]
        itemstoshow = [self.getPSTBnewres_btn()]; itemstoreset = itemstoshow[:3]  
        self.ApplyVisuals(itemstoshow,itemstohide,itemstoreset)

        


        for resname,res in self.DataManager.getResources().items():
            if resname == selectedres:
                sel_resource = res
                
                break

        
        self.getPSTBResName().value = sel_resource.getName()
        self.getPSTBResType().value = sel_resource.getType()
        self.getPSTBResCap().value = str(sel_resource.getDailyCapacity())+" shift/day"

       

        return

 

    def SetStart(self,event):

        sel_start = self.getPLTBPlanStart().value 
    
        self.getPlanningManager().setPHStart(sel_start)
      
        return
        
    def SetEnd(self,event):

        sel_end = self.getPLTBPlanEnd().value
        self.getPlanningManager().setPHEnd(sel_end)
       
        if self.getPlanningManager().getPHStart() != None:
            self.getPLTBmakeplan_btn().disabled = False

        return
        
    def ShowOrderStatus(self,event):

        if not 'new' in event:
            return

        if not 'index' in event['new']:
            return
            
        if event['new']['index'] < 0:
            return
            
        #self.getPLTBOrdProd().value = "order..index>> "+str(event['new']['index'])+"\n"
        
        ordtext = self.getPLTBOrdlist().options[event['new']['index']]

        #self.getPLTBOrdProd().value += ">"+str(ordtext.find(":"))+"\n"
        
        ordname = ordtext[:ordtext.find(":")]
        self.getPLTBresult2exp().value+=ordtext+" >> "+ordname+"\n"

 
      
        #self.getPLTBOrdProd().value += ordname+"\n"

        
        if ordname in self.DataManager.getCustomerOrders():
            self.getPLTBresult2exp().value+="order found!!!!! "+"\n"

            myord = self.DataManager.getCustomerOrders()[ordname]

            self.getPSTBFinalProd().value = myord.getProduct().getName()
            self.getPSTBQuantity().value = str(myord.getQuantity())
            self.getPSTBDeadLine().value = str(myord.getDeadLine())
            myprodname = self.getPSTBFinalProd().value
            self.getPSTBProdSearch().value = myprodname 
            self.getPSTBProdName().value = myord.getProduct().getName()
            self.getPSTBProdPN().value = myord.getProduct().getPN()
            self.getPSTBProdStocklvl().value = str(myord.getProduct().getStockLevel())
            self.getPSTBoperations().options = [opr.getName() for opr in myord.getProduct().getOperations()]

            self.MakeBOMTree(myord.getProduct())



            self.MakeDiagTree(myord)

            if myord.getPlannedDelivery() != None:
                #self.getPLTBOrdProd().value = "Final Product: "+"\n"
                #self.getPLTBOrdProd().value += myord.getProduct().getName()+"\n"
                #self.getPLTBOrdProd().value += "LatestStart: "+str(myord.getLatestStart())+"\n"
                #self.getPLTBOrdProd().value += "Quantity: "+str(myord.getQuantity())+"\n"
                
                self.MakeUseResTree(myord)

                #self.getPLTBOrdProd().value += "Target product levels: "+str(len(myord.getOrderPlan()['Products']))+"\n"
                #prodid = 1
                #for prod,usedict in myord.getOrderPlan()['Products'].items():
                #    self.getPLTBOrdProd().value += str(prodid)+"->"+prod.getName()+"\n"
                #    for mydate,val in usedict.items():
                #        self.getPLTBOrdProd().value +="  >> Date: "+str(mydate)+", Val: "+str(val)+"\n"
                #    prodid+=1

   
        return

    def ShowOrder(self,event):

        if not 'new' in event:
            return

        if not 'index' in event['new']:
            return
            
        if event['new']['index'] < 0:
            return
            
        ordtext = self.getCOTBorders().options[event['new']['index']]

     
        
        if ordtext in self.DataManager.getCustomerOrders():
            myord = self.DataManager.getCustomerOrders()[ordtext]

            self.getPSTBFinalProd().value = myord.getProduct().getName()
            self.getPSTBQuantity().value = str(myord.getQuantity())
            self.getPSTBDeadLine().value = str(myord.getDeadLine())

            #------------------------------------
            itemstoshow = [self.getPSTBProdName(),self.getPSTBProdPN(),self.getPSTBProdStocklvl(),self.getPSTBeditprd_btn()]
            itemstohide = []; itemstoreset = []  
            self.ApplyVisuals(itemstoshow,itemstohide,itemstoreset)

  
            myprodname = self.getPSTBFinalProd().value
            self.getPSTBProdSearch().value = myprodname 

       
       
            self.getPSTBProdName().value = myord.getProduct().getName()
            self.getPSTBProdPN().value = myord.getProduct().getPN()
            if myord.getProduct().getBatchsize()!= None: 
                self.getPSTBProdBatch().value = str(myord.getProduct().getBatchsize())
            else:
                self.getPSTBProdBatch().value = "-"
            self.getPSTBProdStocklvl().value = str(myord.getProduct().getStockLevel())
            self.getPSTBoperations().options = [opr.getName() for opr in myord.getProduct().getOperations()]

            self.MakeBOMTree(myord.getProduct())
       
            
        else:
            self.getPSTBFinalProd().value = "Order not found..."

        
        return

  

    def ShowDescriptives(self,event):

        if not 'index' in event['new']:
            return
            
        if event['new']['index'] < 0:
            return
    
        selected = self.getPLTBDesciptives().options[event['new']['index']]

        if selected == None:
            return

        if selected == '':
            return

        with self.getPLTBStockLevels():
            clear_output()

        self.getPLTBresult2exp().value+=str(selected)+"\n"

        if selected == 'Product Target Levels':

            rawlist = []
                 
            sorteddict = dict(sorted(self.DataManager.getProducts().items(), key=lambda item: -sum([x for x in item[1].getTargetLevels().values()])))
            for prodname,myprod in sorteddict.items():                      
                if len(myprod.getPredecessors()) == 0:
                    rawlist.append(prodname)
                     
            self.getPLTBrawlist().options = rawlist
               
           
        if selected == 'Resource Capacity Plans':

            reslist = [res.getName() for res in self.DataManager.getResources().values()] 
            self.getPLTBrawlist().options = reslist

            self.getPLTBresult2exp().value+=str(type(self.getPlanningManager().getPHEnd()))+"\n"

            self.getPLTBDisplayPeriod().options = [(w+1) for w in range((self.getPlanningManager().getPHEnd()-self.getPlanningManager().getPHStart()).days//7)]
                
            #self.getPLTBDisplayPeriod().options = ["Week "+str(w) for w in range(1,weeks+1)]
      
        
        return
        
        
        
    def generatePLTAB(self):

        self.setPLTBresult2exp(widgets.Textarea(value='', placeholder='',description='',disabled=True))
       
        self.setPLTBOrdlist(widgets.Select(options=[],description = ''))
        self.getPLTBOrdlist().observe(self.ShowOrderStatus)
        
        self.getPLTBOrdlist().layout.height = '150px'
        
        self.setPLTBOrdProd(widgets.Textarea(description ='',value=''))
        self.getPLTBOrdProd().layout.height = '75px'
        self.getPLTBOrdProd().layout.height = '150px'
  
        self.setPLTBPlanStart(widgets.DatePicker(description='Start',disabled=False))
        self.getPLTBPlanStart().observe(self.SetStart)

        
        self.setPLTBPlanEnd(widgets.DatePicker(description='End',disabled=False))
        self.getPLTBPlanEnd().observe(self.SetEnd)
        self.getPLTBresult2exp().layout.height = '150px'
       

        self.setPLTBmakeplan_btn(widgets.Button(description="Make Plan",disabled = True,icon ='gear'))
        self.getPLTBmakeplan_btn().on_click(self.getPlanningManager().MakeDeliveryPlan)

        self.setPLTBrawlist(widgets.Select(options=[],description = ''))
        self.getPLTBrawlist().layout.height = '200px'
        self.getPLTBrawlist().observe(self.Rawclick)

        self.setPLTBStockLevels(widgets.Output())

      
        self.setPLTBDesciptives(widgets.Dropdown(options=['Product Target Levels','Resource Utilizations','Resource Capacity Plans'], description=''))

        self.getPLTBDesciptives().observe(self.ShowDescriptives)

        self.setPLTBDisplayPeriod(widgets.Dropdown(options=[], description=''))

        ordl = widgets.Label(value ='Customer Orders')
        ordl.add_class("red_label")
        prgl = widgets.Label(value ='Planning Progress')
        prgl.add_class("red_label")

        ordresl = widgets.Label(value ='Use of Resources ')
        ordresl.add_class("red_label")
        
        ordtl = widgets.Label(value ='Planning Diagnostics')
        ordtl.add_class("red_label")

        plnhrn = widgets.Label(value ='Planning Horizon')
        plnhrn.add_class("red_label")


        diagtree = Tree()
        rootnode = Node("Diagnostics",[], icon="cut", icon_style="success") 
        diagtree.add_node(rootnode)
        self.setDiagTree(diagtree)
        self.setDiagTreeRootNode(rootnode)

        self.setPLTBDiagOutput(widgets.Output())


        userestree = Tree()
        root2node = Node("Resources",[], icon="cut", icon_style="success") 
        userestree.add_node(root2node)
        self.setUseResTree(userestree)
        self.setUseResTreeRootNode(root2node)

        self.setPLTBUseResOutput(widgets.Output())


   
    
        tab_3 = VBox(children = [plnhrn,
               HBox(children = [self.getPLTBPlanStart(),self.getPLTBPlanEnd(),self.getPLTBmakeplan_btn()]),   
               HBox(children = [VBox(children = [prgl,self.getPLTBresult2exp()]),
                                VBox(children = [ordl,self.getPLTBOrdlist()]),
                                VBox(children = [ordresl,self.getPLTBUseResOutput(),ordtl,self.getPLTBDiagOutput()]),
                                ]),
               
                HBox(children=[VBox(children = [widgets.Label(value ='Planning Descriptives '),self.getPLTBDesciptives()])
                              ]),
            
                HBox(children=[self.getPLTBrawlist(),self.getPLTBStockLevels()],layout = widgets.Layout(height = '375px'))])


        
        with self.getPLTBDiagOutput():
            clear_output()
            display(self.getDiagTree())

        
        with self.getPLTBUseResOutput():
            clear_output()
            display(self.getUseResTree())

        tab_3.layout.height = '700px'

        itemstohide = [self.getPSTBNewResName(),self.getPSTBNewResType(),self.getPSTBNewResCap(),self.getPSTBres_lbl(),
        self.getPSTBaddres_btn(),self.getPSTBcanclres_btn(),self.getPSTBtyp_lbl(),
        self.getPSTBNewProdName(),self.getPSTBNewProdPN(),self.getPSTBNewProdStocklvl(),self.getPSTBprd_lbl(),
        self.getPSTBaddprod_btn(),self.getPSTBaddopr_btn(),self.getPSTBcnclprod_btn(),self.getPSTBNewOprName(),self.getPSTBNewOprProcTime(),
        self.getPSTBcanclopr_btn(),self.getPSTBpn_lbl(),self.getPSTBmyopr_lbl()]
         
        self.ApplyVisuals([],itemstohide,[])
          
        return tab_3

    

    def ResourceEnable(self,event):

        if self.getPSTBResName().disabled:
            self.getPSTBResName().disabled = False
            self.getPSTBResType().disabled = False
            self.getPSTBResCap().disabled = False
            myresname = self.getPSTBResName().value
            for resname,res in self.DataManager.getResources().items():
                if resname == myresname:
                    self.setResourcetoEdit(res)
                    break
        else:
            myres = self.getResourcetoEdit() 
            del self.DataManager.getResources()[myres.getName()]

            myres.setName(self.getPSTBResName().value)
            self.DataManager.getResources()[myres.getName()] = myres
            
            newops = []
            for resname,res in self.DataManager.getResources().items():
                newops.append(res.getName())
          
            self.getPSTBResList().options = [nwop for nwop in newops]
      
            self.getPSTBResName().disabled = True
            self.getPSTBResType().disabled = True
            self.getPSTBResCap().disabled = True

        if event.description == "Edit":
            event.description = "Save"
        else:
            
            
            event.description = "Edit"
        return

    def ProductEnable(self,event):

        if self.getPSTBProdName().disabled:
            self.getPSTBProdName().disabled = False
            self.getPSTBProdPN().disabled = False
            self.getPSTBProdStocklvl().disabled = False
        else:
            self.getPSTBProdName().disabled = True
            self.getPSTBProdPN().disabled = True
            self.getPSTBProdStocklvl().disabled = True

        if event.description == "Edit":
            event.description = "Save"
        else:
            event.description = "Edit"
        return

    def SearchRes(self,sender):

        itemstoshow = [self.getPSTBResName(),self.getPSTBResType(),self.getPSTBResCap(),self.getPSTBeditres_btn()]
        itemstohide = []; itemstoreset = []  
        self.ApplyVisuals(itemstoshow,itemstohide,itemstoreset)

  
        myresname = self.getPSTBResSearch().value

        if myresname in self.DataManager.getResources():
            res = self.DataManager.getResources()[myresname]
            self.getPSTBResName().value = res.getName()
            self.getPSTBResType().value = res.getType()
            self.getPSTBResCap().value = str(res.getDailyCapacity())+" shift/day"
        else:
            self.getPSTBResName().value = myresname+" not found.." 
                
             
        return
    def SearchProd(self,sender):

        itemstoshow = [self.getPSTBProdName(),self.getPSTBProdPN(),self.getPSTBProdStocklvl(),self.getPSTBeditprd_btn()]
        itemstohide = []; itemstoreset = []  
        self.ApplyVisuals(itemstoshow,itemstohide,itemstoreset)

  
        myprodname = self.getPSTBProdSearch().value

        if myprodname[-1] == "*":
            pns = [p.getPN() for p in self.DataManager.getProducts().values()]
            if myprodname[:-1] in pns:
                for pn,p in self.DataManager.getProducts().items():
                    if p.getPN() == myprodname[:-1]:                
                        self.getPSTBProdName().value = p.getName()
                        self.getPSTBProdPN().value = p.getPN()
                        if p.getBatchsize()!= None: 
                            self.getPSTBProdBatch().value = str(p.getBatchsize())
                        else:
                            self.getPSTBProdBatch().value = "-"
                        self.getPSTBProdStocklvl().value = str(p.getStockLevel())
                        self.getPSTBoperations().options = [opr.getName() for opr in p.getOperations()]  
            else:
                self.getPSTBProdName().value = myprodname[:-1]+" not found.." 
        else:
            if myprodname in self.DataManager.getProducts():
                prod = self.DataManager.getProducts()[myprodname]
                self.getPSTBProdName().value = prod.getName()
                self.getPSTBProdPN().value = prod.getPN()
                if prod.getBatchsize()!= None: 
                    self.getPSTBProdBatch().value = str(prod.getBatchsize())
                else:
                    self.getPSTBProdBatch().value = "-"
                self.getPSTBProdStocklvl().value = str(prod.getStockLevel())
                self.getPSTBoperations().options = [opr.getName() for opr in prod.getOperations()]
            else:
                self.getPSTBProdName().value = myprodname+" not found.." 
                
             
        return


   
        
        
    def generatePSTAB(self):

        self.setPSTBResSearch(widgets.Text(description ='',value=''))
        self.getPSTBResSearch().on_submit(self.SearchRes)
        self.setPSTBResList(widgets.Select(options=[],description = ''))

        opl = widgets.Label(value ='Resources')
        opl.add_class("red_label")
        
        res_box = VBox(children=[opl,self.getPSTBResSearch(),self.getPSTBResList()])
        
        
        self.setPSTBnewres_btn(widgets.Button(description="New Resource"))
        self.setPSTBeditres_btn(widgets.Button(description="Edit"))
        self.getPSTBeditres_btn().on_click(self.ResourceEnable) 
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
        
      

        self.setPSTBResName(widgets.Label(value='',disabled = True))
        self.setPSTBResType(widgets.Label(value ='',disabled = True))
        self.setPSTBResCap(widgets.Label(value ='',disabled = True))
        #self.setPSTB(widgets.Label(value ='',disabled = True))

        rsnl = widgets.Label(value ='Name:')
        rsnl.add_class("blue_label")
        rstl = widgets.Label(value ='Type:')
        rstl.add_class("blue_label")
        rscl = widgets.Label(value ='Cap:')
        rscl.add_class("blue_label")
       
       

        tb4_vbox1 = VBox(children = [
                                     HBox(children=[res_box]),self.getPSTBNewResName(),self.getPSTBNewResType(),self.getPSTBNewResCap(),
                     HBox(children=[rsnl,self.getPSTBResName()]),
                     HBox(children=[rstl,self.getPSTBResType(),widgets.Label(value =  " | ",disabled = True),rscl,self.getPSTBResCap()]),
                                     HBox(children=[self.getPSTBaddres_btn(),self.getPSTBcanclres_btn()]),ressel_box
                                    ]
                        )

        self.getPSTBResList().observe(self.ShowResource)

        if not self.IsEditMode():
            self.ApplyVisuals([],[self.getPSTBNewResName(),self.getPSTBNewResType(),self.getPSTBNewResCap(),self.getPSTBaddres_btn(),self.getPSTBcanclres_btn(),self.getPSTBnewres_btn()],[])
             
        self.ApplyVisuals([],[self.getPSTBeditres_btn(),self.getPSTBResName(),self.getPSTBResType(),self.getPSTBResCap()],[])



        self.setPSTBProdSearch(widgets.Text(description ='',value=''))
        self.getPSTBProdSearch().on_submit(self.SearchProd)

 #       self.setNewProd_btn(widgets.Button(description="New products",icon='fa-download'))

        self.setNewProd_btn(widgets.FileUpload(accept='.csv',  # Accepted file extension e.g. '.txt', '.pdf', 'image/*', 'image/*,.pdf'
                             description ='New Products',multiple=False  # True to accept multiple files upload else False
                           ))
        self.getNewProd_btn().observe(self.DataManager.ImportProducts)

        
        self.getNewProd_btn().layout.width = '150px'
        self.getNewProd_btn().layout.height = '28px'

        self.setUpdStocks_btn(widgets.FileUpload(accept='.csv',  # Accepted file extension e.g. '.txt', '.pdf', 'image/*', 'image/*,.pdf'
                             description ='New Operations',multiple=False  # True to accept multiple files upload else False
                           ))
        self.getUpdStocks_btn().layout.width = '150px'
        self.getUpdStocks_btn().layout.height = '28px'
        self.getUpdStocks_btn().observe(self.DataManager.ImportOperations)

       

        
        self.setPSTBProdList(widgets.Select(options=[],description = ''))
        self.setPSTBProdList2(widgets.Select(options=[],description = ''))
        prl = widgets.Label(value ='Products')
        prl.add_class("red_label")
        #prl.layout.width = '30%'
        p_box = VBox(children=[HBox(children=[prl,self.getNewProd_btn(),self.getUpdStocks_btn()]),self.getPSTBProdSearch(),self.getPSTBProdList()])


        self.getPSTBProdList().observe(self.ShowProduct)

       
        self.setPSTBnewprd_btn(widgets.Button(description="New Product"))
        self.setPSTBeditprd_btn(widgets.Button(description="Edit"))
        self.getPSTBeditprd_btn().on_click(self.ProductEnable) 
        self.getPSTBnewprd_btn().on_click(self.CreateProduct)
        self.setPSTBNewProdName(widgets.Text(description ='Name:',value=''))
        self.setPSTBNewProdPN(widgets.Text(description ='PN:',value =''))
        self.setPSTBNewProdStocklvl(widgets.Text(description ='Stock Level:',value =''))
        self.setPSTBaddprod_btn(widgets.Button(description="Add Product"))
        self.getPSTBaddprod_btn().on_click(self.AddProduct)

        self.setPSTBProdName(widgets.Label(value='',disabled = True))
        self.setPSTBProdPN(widgets.Label(value ='',disabled = True))
      
        self.setPSTBProdStocklvl(widgets.Label(value ='',disabled = True))
        self.setPSTBProdBatch(widgets.Label(value ='',disabled = True))

        
      

       
        
        self.setPSTBcnclprod_btn(widgets.Button(description="Cancel"))
        self.getPSTBcnclprod_btn().on_click(self.CancelProduct)
        
        self.setPSTBprd_lbl(widgets.Label(value ='Selected Product:'))
        self.setPSTBpn_lbl(widgets.Label(value ='PN:'))
        
        
        prdsel_box = VBox(children=[self.getPSTBprd_lbl(),self.getPSTBpn_lbl()])

        #
       
        l = widgets.Label(value =  "Name: ",disabled = True)
        l.add_class("blue_label")
        m = widgets.Label(value =  "PN: ",disabled = True)
        m.add_class("blue_label")

        n = widgets.Label(value =  "Stock: ",disabled = True)
        n.add_class("blue_label")

        b = widgets.Label(value =  "Batch: ",disabled = True)
        b.add_class("blue_label")
        tb4_vbox2 = VBox(children = [HBox(children=[p_box]),
                                     #HBox(children=[self.getPSTBnewprd_btn(),self.getPSTBeditprd_btn()]),
                                     #self.getPSTBNewProdName(),self.getPSTBNewProdPN(),self.getPSTBNewProdStocklvl(),
                                     HBox(children=[l,self.getPSTBProdName()]),
                                     HBox(children=[m,self.getPSTBProdPN(),widgets.Label(value =  " | ",disabled = True),n,self.getPSTBProdStocklvl(),widgets.Label(value =  " | ",disabled = True),b,self.getPSTBProdBatch()]),
                                    
                                     HBox(children = [self.getPSTBaddprod_btn(),self.getPSTBcnclprod_btn()])
                                     ,prdsel_box]
                        )

        if not self.IsEditMode():
            self.ApplyVisuals([],[self.getPSTBNewProdName(),self.getPSTBNewProdPN(),self.getPSTBNewProdStocklvl(),self.getPSTBaddprod_btn(),self.getPSTBcnclprod_btn(),self.getPSTBnewprd_btn(),self.getPSTBeditprd_btn()],[])
        

        self.ApplyVisuals([],[self.getPSTBeditprd_btn(),self.getPSTBProdName(),self.getPSTBProdPN(),self.getPSTBProdStocklvl()],[])
    

        self.setPSTBoperations(widgets.Select(options=[],description = ''))
        self.getPSTBoperations().layout.height = '120px'
        self.getPSTBoperations().observe(self.ShowOperation2)
        oprl = widgets.Label(value ='Operations')
        oprl.add_class("red_label")
        op_box = VBox(children=[oprl,self.getPSTBoperations()])
        
        
        #self.setPSTBnewopr_btn(widgets.Button(description="New Operation"))
        #self.getPSTBnewopr_btn().on_click(self.CreateOperation)
        self.setPSTBNewOprName(widgets.Text(description ='Name:',value=''))
        self.setPSTBNewOprProcTime(widgets.Text(description ='Process Time:',value=''))
        self.setPSTBaddopr_btn(widgets.Button(description="Add Operation"))
        self.getPSTBaddopr_btn().on_click(self.AddOperation)
        self.setPSTBcanclopr_btn(widgets.Button(description="Cancel"))
        self.getPSTBcanclopr_btn().on_click(self.CancelOperation)


        self.setPSTBOprName(widgets.Label(value='',disabled = True))
        self.setPSTBOprRes(widgets.Dropdown(options=[],disabled=False))
  
       
        self.setPSTBOprProcTime(widgets.Label(value='',disabled = True))
        

        
        self.setPSTBmyopr_lbl(widgets.Label(value ='Selected Operation:'))
        oprdsel_box = VBox(children=[self.getPSTBmyopr_lbl()])

        oprn = widgets.Label(value ='Name :')
        oprn.add_class("blue_label")

        oprt = widgets.Label(value ='Process Time :')
        oprt.add_class("blue_label")

        oprest = widgets.Label(value ='Resource:')
        oprest.add_class("blue_label")
        
        
        tb4_vbox3 = VBox(children = [HBox(children=[op_box]),self.getPSTBNewOprName(),self.getPSTBNewOprProcTime(),
                                     HBox(children=[oprn,self.getPSTBOprName()]),
                                     HBox(children=[oprt,self.getPSTBOprProcTime()]),
                                     HBox(children=[oprest,self.getPSTBOprRes()]),
                                     HBox(children=[self.getPSTBaddopr_btn(),self.getPSTBcanclopr_btn()])
                                    ,oprdsel_box])
        
        
        self.setPSTBopr_lbl(widgets.Label(value ='Operation:'))
        self.setPSTBoprtp_lbl(widgets.Label(value ='Type:'))
        
        oprboxxlay = widgets.Layout(width = '99%')
        oprsel_box = VBox(children=[self.getPSTBopr_lbl(),self.getPSTBoprtp_lbl()],layout = oprboxxlay)

        if not self.IsEditMode():
            self.ApplyVisuals([],[self.getPSTBNewOprName(),self.getPSTBNewOprProcTime(),self.getPSTBaddopr_btn(),self.getPSTBcanclopr_btn()],[])

        self.ApplyVisuals([],[self.getPSTBOprName(),self.getPSTBOprProcTime()],[])
        

       
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

        #if self.IsEditMode():
            #tab_4 = VBox(children=[HBox(children=[tb4_vbox1,tb4_vbox2,tb4_vbox3]),ResOpr_box,ProPro_box,ProOpr_box])
        #else:

        self.setCOTBorders(widgets.Select(options=[],description = ''))
        self.getCOTBorders().observe(self.ShowOrder)


        self.setNewCustOrdrs_btn(widgets.FileUpload(accept='.csv',  # Accepted file extension e.g. '.txt', '.pdf', 'image/*', 'image/*,.pdf'
                             description ='Import order',multiple=False  # True to accept multiple files upload else False
                           ))
        self.getNewCustOrdrs_btn().observe(self.DataManager.ImportOrders2)

        #self.setNewCustOrdrs_btn(widgets.Button(description="Import orders",icon='fa-download'))
        #self.getNewCustOrdrs_btn().on_click(self.DataManager.ImportOrders)
        self.getNewCustOrdrs_btn().layout.width = '150px'
        self.getNewCustOrdrs_btn().layout.height = '28px'

        ordl = widgets.Label(value ='Customer Orders')
        ordl.layout.width = '120px'
        ordl.add_class("red_label")
        
        ord_box = VBox(children=[HBox(children =[ordl,self.getNewCustOrdrs_btn()]),self.getCOTBorders()])

        self.setPSTBFinalProd(widgets.Text(description ='Product:',value='',disabled = True))
        self.setPSTBQuantity(widgets.Text(description ='Quantity:',value ='',disabled = True))
        self.setPSTBDeadLine(widgets.Text(description ='Deadline:',value ='',disabled = True))
        self.setDiagInfo(widgets.Textarea(value='', placeholder='',description='',disabled=True,layout = Layout(height ="100px" ,width='60%')))

    
      
        self.setCOTBcasename(widgets.Text(description ='Case:',value=''))
        self.setCOTBsave_bttn(widgets.Button(description="Save"))
        self.getCOTBsave_bttn().on_click(self.DataManager.SaveInstance)

        self.setDataDiaOpt(widgets.Dropdown(options = ['Process times','Product operations','Operation resources'],description = ''))
        self.getDataDiaOpt().layout.width = '220px'
        self.setDataDiaBtn(widgets.Button(description="Run",icon= 'search'))
        self.getDataDiaBtn().on_click(self.RunDiagnostics)
        self.getDataDiaBtn().layout.width = '90px'

        ordinf = widgets.Label(value ='Order Information')
        ordinf.add_class("red_label")

        bominf = widgets.Label(value ='Bill of Materials')
        bominf.add_class("red_label")

        self.setPSTBBOMOutput(widgets.Output())

        datadiag = widgets.Label(value ='Data Diagnostics')
        datadiag.add_class("red_label")
        
        
        bomtree = Tree()
        rootnode = Node("BOM tree",[], icon="cut", icon_style="success") 
        bomtree.add_node(rootnode)
        self.setBOMTree(bomtree)
        self.setBOMTreeRootNode(rootnode)
        self.getBOMTree().observe(self.ShowProduct2)

        ordersbox = HBox(children=[ord_box,
                                   VBox(children=[ordinf,HBox(children=[self.getPSTBFinalProd()]),self.getPSTBQuantity(),self.getPSTBDeadLine()]),
                                   VBox(children=[bominf,self.getPSTBBOMOutput()])
                                  ])


        with self.getPSTBBOMOutput():
            clear_output()
            display(self.getBOMTree())
        

        tab_4 = VBox(children=[HBox(children=[tb4_vbox1,tb4_vbox2,tb4_vbox3]),
                               ordersbox,
                               HBox(children=[
                                   #self.getCOTBsave_bttn(),self.getCOTBcasename(), 
                                   datadiag,self.getDataDiaOpt(),self.getDataDiaBtn()]),
                               HBox(children=[self.getDiagInfo()])])
        

        return tab_4



    def MakeUseResTree(self,order):

        userestree = Tree()

        subnodes = []
         
        for res,usedict in order.getOrderPlan()['Resources'].items():  
            mystr = ">"+res.getName()
           
            ressubnodes = []
            for mydate,val in usedict.items():
                usestr = "  > Date: "+str(mydate)+", Val: "+str(val)
                usenode = Node(usestr,[], icon="cut", icon_style="success") 
                ressubnodes.append(usenode)

            resnode = Node(mystr,ressubnodes, icon="cut", icon_style="success") 
            subnodes.append(resnode)

         
        nodestr = order.getName()
        rootnode = Node(nodestr,subnodes, icon="cut", icon_style="success") 
        
        userestree.add_node(rootnode)
        self.setUseResTree(userestree)
        self.setUseResTreeRootNode(rootnode)
        
        with self.getPLTBUseResOutput():
            clear_output()
            display(self.getUseResTree())

        return

    def MakeDiagTree(self,order):

        diagtree = Tree()
    
        subnodes = []
      
        for mydate,reasstr in order.getDelayReasons().items():
            prodpn = reasstr[:reasstr.find("->")]
                   
            mystr = "> Delivery check:  "+str(mydate)

            reason = reasstr[reasstr.find("->")+3:]
            casenode = Node(reason,[], icon="cut", icon_style="success") 
            
            reasonnode = Node(mystr,[casenode], icon="cut", icon_style="success") 
            subnodes.append(reasonnode)
                

        nodestr = order.getName()
        rootnode = Node(nodestr,subnodes, icon="cut", icon_style="success") 
        
        diagtree.add_node(rootnode)
        self.setDiagTree(diagtree)
        self.setDiagTreeRootNode(rootnode)
        
        with self.getPLTBDiagOutput():
            clear_output()
            display(self.getDiagTree())


        return 

    def MakeBOMTree(self,prod):

        bomtree = Tree()
        rootnode = self.RecursiveBOMNode(prod)
        bomtree.add_node(rootnode)

        self.setBOMTree(bomtree)
        self.setBOMTreeRootNode(rootnode)    
        self.getBOMTree().observe(self.ShowProduct2)
        

        with self.getPSTBBOMOutput():
            clear_output()
            display(self.getBOMTree())


        return 

    def RecursiveBOMNode(self,product):

        subnodes = []

        for predecessor,multiplier in product.getMPredecessors().items():
            subnode = self.RecursiveBOMNode(predecessor)
            
            if not subnode is None:
                subnodes.append(subnode)

        nodestr = product.getPN()
        currnode = Node(nodestr,subnodes, icon="cut", icon_style="success") 

        return currnode




    def get_case_selection_tab(self):
        
        global wsheets, wslay, butlay, DFPage
        
       
        self.setFolderNameTxt(widgets.Text(description ='Folder name:',value = 'UseCases'))
        self.getFolderNameTxt().on_submit(self.DataManager.on_submit_func)
       
        self.setCasesDrop(widgets.Dropdown(options=[], description='Use Cases:'))
        self.setCaseInfo(widgets.Textarea(value='', placeholder='',description='',disabled=True,layout = Layout(height ="100px" ,width='60%')))   

    
        self.setReadFileBtn(widgets.Button(description="Read",icon = 'fa-folder-o') )
        self.getReadFileBtn().on_click(self.DataManager.read_dataset)


        self.setUSTBCustomerOders(widgets.Label(value =''))
        self.setUSTBProducts(widgets.Label(value =''))
        self.setUSTBRawMaterials(widgets.Label(value =''))
        self.setUSTBRawResources(widgets.Label(value =''))
       

        tablayout = widgets.Layout(height='500px')
      
       
        tab_1 = VBox(children=[
            HBox(children = [self.getFolderNameTxt(),self.getCasesDrop(),self.getReadFileBtn()]),self.getCaseInfo(),
            HBox(children = [widgets.Label(value ='Customer Orders: '),self.getUSTBCustomerOders()]),
            HBox(children = [widgets.Label(value ='Products: '),self.getUSTBProducts()]),
            HBox(children = [widgets.Label(value ='Raw Materials: '),self.getUSTBRawMaterials()]),
            HBox(children = [widgets.Label(value ='Resources: '),self.getUSTBRawResources()])],layout=tablayout)

       
        return tab_1

    def RefreshViews(self):
        
        self.getPSTBResList().options = [resname for resname in self.DataManager.getResources().keys()]
        self.getPSTBoperations().options = [opname for opname in self.DataManager.getOperations().keys()]
        self.getPSTBProdList().options = [opname for opname in self.DataManager.getProducts().keys()]
        self.getPSTBProdList2().options = [opname for opname in self.DataManager.getProducts().keys()]
        self.getCOTBorders().options = [ordname for ordname in self.DataManager.getCustomerOrders().keys()]
        self.getProductionProgressTab().getCustomerOrderList().options = [ordname for ordname in self.DataManager.getCustomerOrders().keys()]
        self.getProductionProgressTab().getResourceList().options = [resname for resname in self.DataManager.getResources().keys()]
        
        return
    def CreateResource(self,event):

        #self.getCaseInfo().value += ">>>resource.. "+"\n"
        
        itemstoshow = [self.getPSTBNewResName(),self.getPSTBNewResType(),self.getPSTBNewResCap(),self.getPSTBaddres_btn(),self.getPSTBcanclres_btn()]
        itemstohide = [self.getPSTBnewres_btn(),self.getPSTBeditres_btn()]; itemstoreset = itemstoshow[:3]  
        self.ApplyVisuals(itemstoshow,itemstohide,itemstoreset)

        itemstohide= [self.getPSTBResName(),self.getPSTBResType(),self.getPSTBResCap(),self.getPSTBResOprs()]
        itemstoshow= []; itemstoreset = []  
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

        self.ApplyVisuals([],[self.getPSTBProdName(),self.getPSTBProdPN(),self.getPSTBProdStocklvl()],[])

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

    def RunDiagnostics(self,event):
        
        folder = 'UseCases'; casename = "TBRM_Volledige_Instantie"
        path = folder+"\\"+casename
        isExist = os.path.exists(path)
        
        if not isExist:
            os.makedirs(path)

        # if not 'index' in event['new']:
        #     return

        # if event['new']['index'] < 0:
        #     return
        self.getDiagInfo().value = ''
        selected = self.getDataDiaOpt().value        

        if selected == None:
            return

        if selected == '':
            return

        if selected == 'Process time diagnostics':
            
            # diag_df = pd.DataFrame(columns = ["Operation name"])
            check = False
            count = 0
            self.getDiagInfo().value += ">>>Starting Process time diagnostics... "+"\n"
            self.getDiagInfo().value += ">>>Checking operations without process time... "+"\n"
            for opnam, opr in self.DataManager.getOperations().items():
                if opr.getProcessTime() == 0 or opr.getProcessTime() is None:
                    check = True
                    count += 1
                    self.getDiagInfo().value += "Operation "+str(opnam)+" has no process time defined. "+ "\n"
                    # diag_df.loc[len(diag_df)] = {"Operation name":opnam}
            if check == True:
                self.getDiagInfo().value +="There are "+str(count)+" out of "+str(len(self.DataManager.getOperations().items()))+" operations without a process time. "+ "\n"
                self.getDiagInfo().value +=">>>Process time diagnostics finished... "+ "\n"
            if check == False:
                self.getDiagInfo().value +="All operations have a processtime defined. "+ "\n"
                self.getDiagInfo().value +=">>>Process time diagnostics finished... "+ "\n"

            # filename = "Process_time_diagnostics.csv"; path = folder+"\\"+casename+"\\"+filename;fullpath = os.path.join(Path.cwd(), path)
            # diag_df.to_csv(fullpath, index=False)  

        if selected == 'Product operation diagnostics':

            # diag_df = pd.DataFrame(columns = ["Product name"])
            check = False
            count = 0
            total = 0
            self.getDiagInfo().value +=">>>Starting Product operations diagnostics... "+"\n"
            self.getDiagInfo().value +=">>>Checking (non raw material) products without operations... "+"\n"

            for prodname, prod in self.DataManager.getProducts().items():
                if len(prod.getPredecessors()) > 0:
                    total +=1
                    if len(prod.getOperations()) == 0:
                        check = True
                        count +=1
                        self.getDiagInfo().value +="Product "+str(prodname)+" has no operations defined. "+"\n"
                        # diag_df.loc[len(diag_df)] = {"Product name":prodname}

            if check == True:
                self.getDiagInfo().value+="There are "+str(count)+" out of "+str(len(self.DataManager.getProducts().items()))+" products without an operation defined. "+ "\n"
                self.getDiagInfo().value +=">>>Product operations diagnostics finished... "+ "\n"
            if check == False:
                self.getDiagInfo().value +="All products have an operation defined. "+ "\n"
                self.getDiagInfo().value +=">>>Product operations diagnostics finished... "+ "\n"

            # filename = "Product_operation_diagnostics.csv"; path = folder+"\\"+casename+"\\"+filename;fullpath = os.path.join(Path.cwd(), path)
            # diag_df.to_csv(fullpath, index=False)

        if selected == 'Operation resource diagnostics':

            # diag_df = pd.DataFrame(columns = ["Operation name"])
            check = False
            count = 0
            MillingOps = []
            self.getDiagInfo().value+=">>>Starting Milling operations diagnostics... "+"\n"
            self.getDiagInfo().value+=">>>Checking milling operations with only one resource... "+"\n"
            for opnam,opr in self.DataManager.getOperations().items():
                if 'Milling' in str(opnam) or 'milling' in str(opnam):
                    MillingOps.append(opnam)
                    if len(opr.getRequiredResources()) == 1:
                        check = True
                        count += 1
                        self.getDiagInfo().value += "Operation "+str(opnam)+" has only one resource defined. "+ "\n"                        
                        self.getDiagInfo().value += "This is resource "+ str(opr.getRequiredResources()[0][0].getName())+"."+ "\n"
                        # diag_df.loc[len(diag_df)] = {"Operation name":opnam}

            if check == True:
                self.getDiagInfo().value +="There are "+str(count)+" out of "+str(len(MillingOps))+" milling operations with only one resource defined. "+ "\n"
                self.getDiagInfo().value +=">>>Milling operations diagnostics finished... "+ "\n"
            if check == False:
                self.getDiagInfo().value +="All milling operations have more that one resource defined. "+ "\n"
                self.getDiagInfo().value +=">>>Milling operations diagnostics finished... "+ "\n"

            # filename = "Operation_resource_diagnostics.csv"; path = folder+"\\"+casename+"\\"+filename;fullpath = os.path.join(Path.cwd(), path)
            # diag_df.to_csv(fullpath, index=False)

        return
                        
            
            
            
                                                                                
                    
                    
        


  

#############################################################################################################################################  







#############################################################################################################################################   




 