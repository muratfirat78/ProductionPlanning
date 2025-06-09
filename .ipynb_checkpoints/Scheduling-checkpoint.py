# -*- coding: utf-8 -*-

##### import ipywidgets as widgets
from IPython.display import clear_output
from IPython import display
from ipywidgets import *
from datetime import timedelta,date,datetime,time
import matplotlib.pyplot as plt
import warnings
import seaborn as sns
import os
import pandas as pd
import warnings
import sys
import numpy as np
from PlanningObjects import *
from Visual import *
from Data import *


#######################################################################################################################


        
class SchedulingManager:
    def __init__(self): 

        self.DataManager = None
        self.VisualManager = None
        self.PlanningManager = None
        

    def setDataManager(self,DataMgr):
        self.DataManager = DataMgr 
        return

    def getDataManager(self):
        return self.DataManager


    def setPlanningManager(self,MyMgr):
        self.PlanningManager = MyMgr 
        return

    def getPlanningManager(self):
        return self.PlanningManager


    def setVisualManager(self,VMgr):
        self.VisualManager = VMgr 
        return

    def getVisualManager(self):
        return self.VisualManager


    def MakeSchedule(self,b):

        self.getVisualManager().getPSchScheRes().value+="Scheduling starts..."+"\n"

        oprdict = dict() # key: operation, #val: set of jobs
        

        for resname,res in self.getDataManager().getResources().items():
            res.getSchedule().clear()

        # Collect operations with jobs
        nrjobs = 0
        for prname,prod in self.getDataManager().getProducts().items():
            for opr in prod.getOperations():
                if not opr in oprdict:
                    oprdict[opr] = opr.getJobs()
                    nrjobs+= len(opr.getJobs())
                
        self.getVisualManager().getPSchScheRes().value+=" To schedule jobs: "+str(nrjobs)+"\n"
        revopdict = {k: oprdict[k] for k in sorted(oprdict, key=lambda x: list(oprdict.keys()).index(x), reverse=True)}
        

        for k1, k2 in zip(revopdict, list(revopdict)[1:]): #links pairs of keys together 
            CurJobs = revopdict[k1].reverse();
            Predjobs = revopdict[k2].reverse();
            
            for i in range(0,len(CurJobs)):
                CapCurJob = CurJobs[i].getQuantity();
                numPredjobs = len(Predjobs)
                k = 0;
                while k < numPredjobs:
                    if Predjob[k].getQuantity() < CapCurJob:
                        CapCurJob = CapCurJob - Predjob[k].getQuantity();
                        CurJobs[i].getPredecessors().append(Predjob[k]);
                        PredJob[k].getSuccessor().append(CurJobs[i]);
                        k += 1;
                    else:
                        CurJobs[i].getPredecessors.append(Predjob[k]);
                        PredJob[k].getSuccessor().append(CurJobs[i]);
                        k +=1;
                        if k == num Predjobs:
                            break
                        else:
                            Predjobs = Predjobs[k:];
                            break
                        
        return

        
       
      
        

    

  
