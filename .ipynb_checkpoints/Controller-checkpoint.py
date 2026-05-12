
from Visual import*
from Model import*


class Controller:
    def __init__(self):  
        self.VisualManager = VisualManager()
        self.VisualManager.setController(self)
        self.Model = ArithmaticManager()
        self.Model.setController(self)
      
    def GetDashBoard(self):

        print("Controller: Generating dashboard")
        return self.VisualManager.GenerateTab()

    
    def ExecuteOperation(self,operation,numbers):
        result = 0
        if operation == "Average":
            result = self.Model.FindAverage(numbers)
        if operation == "Variance":
            result = self.Model.FindVariance(numbers)

        ## complete here...
        return result

        
        
    