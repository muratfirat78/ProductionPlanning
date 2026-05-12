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
        
        
        
########### get-set functions ###########        
    def setInputText(self,myitem):
       self.InputText = myitem
       return 
    def getInputText(self):
       return self.InputText
          
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
    def getMyController(self):
       return self.MyController

        
########### get-set functions ###########    

    def MakeOperation(self,event):

        inputvals = self.getInputText().value
        numbers = [int(x)  for x in inputvals.split(",")]
        result = self.getMyController().ExecuteOperation(str(self.getOperationMenu().value),numbers)

        self.getResultText().value = str(result)
        
        return 
    
 

    def GenerateTab(self):

        print("Visual Manager: Generating dashboard")

        self.setInputText(widgets.Text(description ='Input values: ',value=''))
        self.setCalculateButton(widgets.Button(description="Calculate"))
        self.setOperationMenu(widgets.Dropdown(options = ['Maximum','Minimum','Median','Average','Variance'],description = 'Operations'))
        self.setResultText(widgets.Textarea(value='', placeholder='',description='',disabled=True))


        self.getCalculateButton().on_click(self.MakeOperation)

        tab = VBox(children=[self.getInputText(),
                             self.getOperationMenu(),
                             self.getCalculateButton(),
                             self.getResultText()])       
        return tab 
 

   
    