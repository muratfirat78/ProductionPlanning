
from visual import *
from simulator import *
from productionmain import *
from MILPScheduling import * 

class Controller:
    def __init__(self):  
        self.VisualManager = VisualManager()
        self.VisualManager.setController(self)
        self.Simulator = Simulator()
        self.Simulator.setController(self)
        self.WorkManager = ShopFloorManager(self.Simulator)
        self.WorkManager.setDemandType("Product")
        self.MILPManager = ProductionMILPManager(self.Simulator)


    def getVisualManager(self):
        return self.VisualManager
    def getWorkManager(self):
        return self.WorkManager
    def getSimulator(self):
        return self.Simulator

    def getMILPManager(self):
        return self.MILPManager
      
    def GetDashBoard(self):

        print("Controller: Generating dashboard")
        return self.VisualManager.GenerateMainTab()

    def GenerateMILPTab(self):

        return self.VisualManager.GenerateMILPTab()

    
    def ExecuteOperation(self,operation,numbers):
        result = 0
        if operation == "Average":
            result = self.Model.FindAverage(numbers)
        if operation == "Variance":
            result = self.Model.FindVariance(numbers)

        ## complete here...
        return result

        
        
    