# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 11:46:59 2024

@author: mfirat
"""

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
import numpy as np
from pathlib import Path
from PlanningObjects import *

warnings.filterwarnings("ignore")

class VisualManager():

    def __init__(self):  


        self.EditMode = True
        self.DataManager = None
        self.PlanningManager = None
        self.SchedulingManager = None
        self.ProdSystemTab = None

        self.SchedulingTab = None
        
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

        self.FolderNameTxt = None
        self.CasesDrop = None
        self.ReadFileBtn = None
        
        
  
        return


    def setUSTBRawResources(self,myit):
        self.USTBRawResources = myit
        return

    def getUSTBRawResources(self):
        return self.USTBRawResources


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
    def getPSTBProdOprs(self):
        return self.PSTBProdOprs
        
        
        
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
       

        if self.getPLTBDesciptives().value == 'Product Target Levels':
            rawname = selected
           
            rawmat = None
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
                ax.set_title('Targets '+rawname) 
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

    def ShowOperation(self,event):

 
        if event['type'] == 'change' and event['name'] == 'value':
            print("changed to %s" % event['new'])
        else:
            return
        
        selectedopr = self.getPSTBProdOprs().value
        sel_opr = None
        curr_prod = None
    
      
        itemstoshow = [self.getPSTBOprName(),self.getPSTBOprProcTime()]
        itemstohide = []; itemstoreset = []  
        self.ApplyVisuals(itemstoshow,itemstohide,itemstoreset)

        itemstohide = [self.getPSTBNewOprName(),self.getPSTBNewOprProcTime(),self.getPSTBaddopr_btn(),self.getPSTBcanclopr_btn()]
        itemstoshow = [self.getPSTBnewopr_btn()]; itemstoreset = itemstoshow[:1]  
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
            self.getPSTBOprProcTime().value = str(sel_opr.getProcessTime())
       
        
        return

    def ShowProduct(self,event):

        if event['name'] !=  '_property_lock':
            return

        
        selectedprd = self.getPSTBProdList().options[event['new']['index']]
        sel_prod = None

    
      
        itemstoshow = [self.getPSTBeditprd_btn(),self.getPSTBProdName(),self.getPSTBProdPN(),self.getPSTBProdStocklvl(),self.getPSTBProdOprs()]
        itemstohide = []; itemstoreset = []  
        self.ApplyVisuals(itemstoshow,itemstohide,itemstoreset)

        itemstohide = [self.getPSTBNewProdName(),self.getPSTBNewProdPN(),self.getPSTBNewProdStocklvl(),self.getPSTBaddprod_btn(),self.getPSTBcnclprod_btn()]
        itemstoshow = [self.getPSTBnewprd_btn()]; itemstoreset = itemstoshow[:3]  
        self.ApplyVisuals(itemstoshow,itemstohide,itemstoreset)

     
        for prname,prod in self.DataManager.getProducts().items():
            if prname == selectedprd:
                sel_prod = prod
                break

        
        self.getPSTBProdName().value = sel_prod.getName()
        self.getPSTBProdPN().value = sel_prod.getPN()
        self.getPSTBProdStocklvl().value = str(sel_prod.getStockLevel())
        self.getPSTBProdOprs().options = [opr.getName() for opr in sel_prod.getOperations()]
        
        return

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
        self.getPSTBResCap().value = str(sel_resource.getDailyCapacity())+" hrs/day"

       

        return

    def generatePSschTAB(self):
    

        self.setPSchScheRes(widgets.Textarea(value='', placeholder='',description='Schedule',disabled=True))
     
        self.getPSchScheRes().layout.height = '150px'
        self.getPSchScheRes().layout.width = "90%"

        self.setPSchTBmakesch_btn(widgets.Button(description="Make Schedule"))
        self.getPSchTBmakesch_btn().on_click(self.getSchedulingManager().MakeSchedule)

        self.setPSchJoblist(widgets.Select(options=[],description = 'Jobs'))
        self.getPSchJoblist().layout.height = '250px'
        #self.getPSchJoblist().observe(self.Rawclick)

        #self.setPLTBStockLevels(widgets.Output())


        self.setPSchResources(widgets.Dropdown(options=[], description='Operations:'))
        self.getPSchResources().observe(self.ShowJobs)
    
        tab_sch = VBox(children = [self.getPSchTBmakesch_btn(),HBox(children=[self.getPSchResources(),self.getPSchJoblist()]),self.getPSchScheRes()])

        tab_sch.layout.height = '600px'
          
        return tab_sch

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
            
        self.getPLTBOrdProd().value = "order..index>> "+str(event['new']['index'])+"\n"
        
        ordtext = self.getPLTBOrdlist().options[event['new']['index']]

        self.getPLTBOrdProd().value += ">"+str(ordtext.find(":"))+"\n"
        
        ordname = ordtext[:ordtext.find(":")]

        self.getPLTBOrdProd().value += ordname+"\n"

        
        if ordname in self.DataManager.getCustomerOrders():
            myord = self.DataManager.getCustomerOrders()[ordname]

            if myord.getPlannedDelivery() != None:
                self.getPLTBOrdProd().value = "Final Product: "+"\n"
                self.getPLTBOrdProd().value += myord.getProduct().getName()+"\n"
                self.getPLTBOrdProd().value += "LatestStart: "+str(myord.getLatestStart())+"\n"
                self.getPLTBOrdProd().value += "Quantity: "+str(myord.getQuantity())+"\n"
                
                self.getPLTBOrdProd().value += "Resource use: "+str(len(myord.getOrderPlan()['Resources']))+"\n"
                resid = 1
                for res,usedict in myord.getOrderPlan()['Resources'].items():    
                    self.getPLTBOrdProd().value += str(resid)+"->"+res.getName()+"\n"
                    for mydate,val in usedict.items():
                        self.getPLTBOrdProd().value += "  >> Date: "+str(mydate)+", Val: "+str(val)+"\n"
                    resid+=1

                self.getPLTBOrdProd().value += "Target product levels: "+str(len(myord.getOrderPlan()['Products']))+"\n"
                prodid = 1
                for prod,usedict in myord.getOrderPlan()['Products'].items():
                    self.getPLTBOrdProd().value += str(prodid)+"->"+prod.getName()+"\n"
                    for mydate,val in usedict.items():
                        self.getPLTBOrdProd().value +="  >> Date: "+str(mydate)+", Val: "+str(val)+"\n"
                    prodid+=1
                
                if (myord.getPlannedDelivery().date()-max(myord.getDeadLine().date(),self.getPlanningManager().getPHStart())).days-1 > 0:
                    self.getPLTBOrdProd().value += "Delay reasons: "+"\n"
                    for myprd,reason in myord.getDelayReasons().items():
                        self.getPLTBOrdProd().value +="  > Prod "+myprd.getName()+", reason "+str(reason[0])+":"+str(reason[1])+"\n"
                else:
                    self.getPLTBOrdProd().value += "No delay"+"\n"
            else:
                self.getPLTBOrdProd().value = "Not planned... "+"\n"
           
        else:
            self.getPLTBOrdProd().value = "Order not found..."+"\n"

        
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
       

        self.setPLTBmakeplan_btn(widgets.Button(description="Make Plan",disabled = True))
        self.getPLTBmakeplan_btn().on_click(self.getPlanningManager().MakeDeliveryPlan)

        self.setPLTBrawlist(widgets.Select(options=[],description = ''))
        self.getPLTBrawlist().layout.height = '200px'
        self.getPLTBrawlist().observe(self.Rawclick)

        self.setPLTBStockLevels(widgets.Output())

      
        self.setPLTBDesciptives(widgets.Dropdown(options=['Product Target Levels','Resource Utilizations','Resource Capacity Plans'], description=''))

        self.getPLTBDesciptives().observe(self.ShowDescriptives)

        self.setPLTBDisplayPeriod(widgets.Dropdown(options=[], description=''))

        
    
        tab_3 = VBox(children = [
                widgets.Label(value ='Planning Settings '),
               HBox(children = [self.getPLTBPlanStart(),self.getPLTBPlanEnd(),self.getPLTBmakeplan_btn()]),   
               HBox(children = [VBox(children = [widgets.Label(value ='Planning Progress '),self.getPLTBresult2exp()]),
                                VBox(children = [widgets.Label(value ='Planned Orders '),self.getPLTBOrdlist()]),
                                VBox(children = [widgets.Label(value ='Order Details '),self.getPLTBOrdProd()])],layout = widgets.Layout(height = '205px')),
               
                HBox(children=[VBox(children = [widgets.Label(value ='Planning Descriptives '),self.getPLTBDesciptives()]),
                               VBox(children = [widgets.Label(value ='Display Period'),self.getPLTBDisplayPeriod()])]),
            
                HBox(children=[self.getPLTBrawlist(),self.getPLTBStockLevels()],layout = widgets.Layout(height = '205px'))])

        tab_3.layout.height = '700px'

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
            self.getPSTBResCap().value = str(res.getDailyCapacity())+" hrs/day"
        else:
            self.getPSTBResName().value = myresname+" not found.." 
                
             
        return

    def SearchProd(self,sender):

        itemstoshow = [self.getPSTBProdName(),self.getPSTBProdPN(),self.getPSTBProdStocklvl(),self.getPSTBProdOprs(),self.getPSTBeditprd_btn()]
        itemstohide = []; itemstoreset = []  
        self.ApplyVisuals(itemstoshow,itemstohide,itemstoreset)

  
        myprodname = self.getPSTBProdSearch().value

        if myprodname in self.DataManager.getProducts():
            prod = self.DataManager.getProducts()[myprodname]
            self.getPSTBProdName().value = prod.getName()
            self.getPSTBProdPN().value = prod.getPN()
            self.getPSTBProdStocklvl().value = str(prod.getStockLevel())
            self.getPSTBProdOprs().options = [opr.getName() for opr in prod.getOperations()]
        else:
            self.getPSTBProdName().value = myprodname+" not found.." 
                
             
        return
        
        

    def generatePSTAB(self):

        self.setPSTBResSearch(widgets.Text(description ='',value=''))
        self.getPSTBResSearch().on_submit(self.SearchRes)
        self.setPSTBResList(widgets.Select(options=[],description = ''))
        res_box = VBox(children=[widgets.Label(value ='Resource List'),self.getPSTBResSearch(),self.getPSTBResList()])
        
        
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
        
      

        self.setPSTBResName(widgets.Text(description ='Name:',value='',disabled = True))
        self.setPSTBResType(widgets.Text(description ='Type:',value ='',disabled = True))
        self.setPSTBResCap(widgets.Text(description ='Daily Capacity:',value ='',disabled = True))
       

        tb4_vbox1 = VBox(children = [
                                     HBox(children=[res_box]),
                                HBox(children=[self.getPSTBnewres_btn(),self.getPSTBeditres_btn()]),self.getPSTBNewResName(),self.getPSTBNewResType(),self.getPSTBNewResCap(),
                                     self.getPSTBResName(),self.getPSTBResType(),self.getPSTBResCap(),
                                     HBox(children=[self.getPSTBaddres_btn(),self.getPSTBcanclres_btn()]),ressel_box
                                    ]
                        )

        self.getPSTBResList().observe(self.ShowResource)

        if not self.IsEditMode():
            self.ApplyVisuals([],[self.getPSTBNewResName(),self.getPSTBNewResType(),self.getPSTBNewResCap(),self.getPSTBaddres_btn(),self.getPSTBcanclres_btn(),self.getPSTBnewres_btn()],[])
             
        self.ApplyVisuals([],[self.getPSTBeditres_btn(),self.getPSTBResName(),self.getPSTBResType(),self.getPSTBResCap()],[])



        self.setPSTBProdSearch(widgets.Text(description ='',value=''))
        self.getPSTBProdSearch().on_submit(self.SearchProd)
        
        self.setPSTBProdList(widgets.Select(options=[],description = ''))
        self.setPSTBProdList2(widgets.Select(options=[],description = ''))
        p_box = VBox(children=[widgets.Label(value ='Product List'),self.getPSTBProdSearch(),self.getPSTBProdList()])


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

        self.setPSTBProdName(widgets.Text(description ='Name:',value='',disabled = True))
        self.setPSTBProdPN(widgets.Text(description ='PN:',value ='',disabled = True))
        self.setPSTBProdStocklvl(widgets.Text(description ='Stock Level:',value ='',disabled = True))
        self.setPSTBProdOprs(widgets.Dropdown(description ='Operations:',options =[]))

        self.getPSTBProdOprs().observe(self.ShowOperation)
        
        self.setPSTBcnclprod_btn(widgets.Button(description="Cancel"))
        self.getPSTBcnclprod_btn().on_click(self.CancelProduct)
        
        self.setPSTBprd_lbl(widgets.Label(value ='Selected Product:'))
        self.setPSTBpn_lbl(widgets.Label(value ='PN:'))
        
        
        prdsel_box = VBox(children=[self.getPSTBprd_lbl(),self.getPSTBpn_lbl()])
        
        
        tb4_vbox2 = VBox(children = [HBox(children=[p_box]),HBox(children=[self.getPSTBnewprd_btn(),self.getPSTBeditprd_btn()]),self.getPSTBNewProdName(),self.getPSTBNewProdPN(),self.getPSTBNewProdStocklvl(),
self.getPSTBProdName(),self.getPSTBProdPN(),self.getPSTBProdStocklvl(),self.getPSTBProdOprs(),HBox(children = [self.getPSTBaddprod_btn(),self.getPSTBcnclprod_btn()]),prdsel_box])

        if not self.IsEditMode():
            self.ApplyVisuals([],[self.getPSTBNewProdName(),self.getPSTBNewProdPN(),self.getPSTBNewProdStocklvl(),self.getPSTBaddprod_btn(),self.getPSTBcnclprod_btn(),self.getPSTBnewprd_btn(),self.getPSTBeditprd_btn()],[])
        

        self.ApplyVisuals([],[self.getPSTBeditprd_btn(),self.getPSTBProdName(),self.getPSTBProdPN(),self.getPSTBProdStocklvl(),self.getPSTBProdOprs()],[])
    

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


        self.setPSTBOprName(widgets.Text(description ='Name:',value='',disabled = True))
       
        self.setPSTBOprProcTime(widgets.Text(description ='Process Time:',value='',disabled = True))
        

        
        self.setPSTBmyopr_lbl(widgets.Label(value ='Selected Operation:'))
        oprdsel_box = VBox(children=[self.getPSTBmyopr_lbl()])
        
        
        tb4_vbox3 = VBox(children = [HBox(children=[op_box]),self.getPSTBnewopr_btn(),self.getPSTBNewOprName(),self.getPSTBNewOprProcTime(),self.getPSTBOprName(),self.getPSTBOprProcTime(),HBox(children=[self.getPSTBaddopr_btn(),self.getPSTBcanclopr_btn()])
                                    ,oprdsel_box])
        
        
        self.setPSTBopr_lbl(widgets.Label(value ='Operation:'))
        self.setPSTBoprtp_lbl(widgets.Label(value ='Type:'))
        
        oprboxxlay = widgets.Layout(width = '99%')
        oprsel_box = VBox(children=[self.getPSTBopr_lbl(),self.getPSTBoprtp_lbl()],layout = oprboxxlay)

        if not self.IsEditMode():
            self.ApplyVisuals([],[self.getPSTBnewopr_btn(),self.getPSTBNewOprName(),self.getPSTBNewOprProcTime(),self.getPSTBaddopr_btn(),self.getPSTBcanclopr_btn()],[])

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
        self.setCaseInfo(widgets.Textarea(value='', placeholder='',description='',disabled=True,layout = Layout(height ="100px" ,width='60%')))   

    
        self.setReadFileBtn(widgets.Button(description="Read") )
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

        self.ApplyVisuals([],[self.getPSTBProdName(),self.getPSTBProdPN(),self.getPSTBProdStocklvl(),self.getPSTBProdOprs()],[])

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




 