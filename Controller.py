
from Visual import*
from Simulator import *
from productionmain import *

class Controller:
    def __init__(self):  
        self.VisualManager = VisualManager()
        self.VisualManager.setController(self)
        self.Simulator = Simulator()
        self.Simulator.setController(self)
        self.WorkManager = ShopFloorManager(self.Simulator)
        self.WorkManager.setDemandType("Product")

        self.WorkManager.getProductionAlgManager().getAlgorithmSetting()["Trailer Loading"] = []
        self.WorkManager.getProductionAlgManager().getAlgorithmSetting()["Trailer Loading"].append(("Select Items",'EDDOrder'))
        self.WorkManager.getProductionAlgManager().getAlgorithmSetting()["Trailer Loading"].append(('Assign Resource',"Straight Available"))
        self.WorkManager.getProductionAlgManager().getAlgorithmSetting()["Trailer Loading"].append(("Assign Equipment","Straight Available"))

        self.WorkManager.getProductionAlgManager().getAlgorithmSetting()["Trailer Transport"] = []
        self.WorkManager.getProductionAlgManager().getAlgorithmSetting()["Trailer Transport"].append(("Select Destination",'MostDemanded'))

        self.WorkManager.getProductionAlgManager().getAlgorithmSetting()["Trailer Unloading"] = []
        self.WorkManager.getProductionAlgManager().getAlgorithmSetting()["Trailer Unloading"].append(("Select Items", 'UnloadFeasible'))

        self.WorkManager.getProductionAlgManager().getAlgorithmSetting()["Machine Setup"] = []
        self.WorkManager.getProductionAlgManager().getAlgorithmSetting()["Machine Setup"].append(("Assign Equipment","Straight Available"))
        self.WorkManager.getProductionAlgManager().getAlgorithmSetting()["Machine Setup"].append(("Assign Resource","Straight Available"))
        self.WorkManager.getProductionAlgManager().getAlgorithmSetting()["Machine Setup"].append(("Select Items",'EDDOrder'))

        self.WorkManager.getProductionAlgManager().getAlgorithmSetting()["Machine Loading"] = []
        self.WorkManager.getProductionAlgManager().getAlgorithmSetting()["Machine Loading"].append(("Assign Resource","Straight Available"))

        self.WorkManager.getProductionAlgManager().getAlgorithmSetting()["Processing"] = []
        self.WorkManager.getProductionAlgManager().getAlgorithmSetting()["Processing"].append(("Assign Equipment","Straight Available"))
        
        self.WorkManager.getProductionAlgManager().getAlgorithmSetting()["Machine Unloading"] =[]
        self.WorkManager.getProductionAlgManager().getAlgorithmSetting()["Machine Unloading"].append(("Assign Resource","Straight Available"))
      
        self.WorkManager.getProductionAlgManager().setPriorityFunctions()


    def getVisualManager(self):
        return self.VisualManager
    def getWorkManager(self):
        return self.WorkManager
    def getSimulator(self):
        return self.Simulator
      
    def GetDashBoard(self):

        print("Controller: Generating dashboard")
        return self.VisualManager.GenerateMainTab()

    
    def ExecuteOperation(self,operation,numbers):
        result = 0
        if operation == "Average":
            result = self.Model.FindAverage(numbers)
        if operation == "Variance":
            result = self.Model.FindVariance(numbers)

        ## complete here...
        return result

        
        
    