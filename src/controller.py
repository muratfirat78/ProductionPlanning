
from __future__ import annotations

from collections.abc import Sequence
from statistics import fmean, pvariance

from ipywidgets import Widget
from visual import VisualManager
from simulator import Simulator
from productionmain import ShopFloorManager
from MILPScheduling import ProductionMILPManager

class Controller:
    def __init__(self) -> None:
        self.VisualManager: VisualManager = VisualManager()
        self.VisualManager.setController(self)
        self.Simulator: Simulator = Simulator()
        self.Simulator.setController(self)
        self.WorkManager: ShopFloorManager = ShopFloorManager(self.Simulator)
        self.WorkManager.setDemandType("Product")
        self.MILPManager: ProductionMILPManager = ProductionMILPManager(self.Simulator)


    def getVisualManager(self) -> VisualManager:
        return self.VisualManager

    def getWorkManager(self) -> ShopFloorManager:
        return self.WorkManager

    def getSimulator(self) -> Simulator:
        return self.Simulator

    def getMILPManager(self) -> ProductionMILPManager:
        return self.MILPManager
      
    def GetDashBoard(self) -> Widget:

        print("Controller: Generating dashboard")
        return self.VisualManager.GenerateMainTab()

    def GenerateMILPTab(self) -> Widget:

        return self.VisualManager.GenerateMILPTab()

    
    def ExecuteOperation(self, operation: str, numbers: Sequence[float]) -> float:
        result = 0
        if operation == "Average":
            result = self.Model.FindAverage(numbers)
        if operation == "Variance":
            result = self.Model.FindVariance(numbers)

        ## complete here...
        return result

        
        
    