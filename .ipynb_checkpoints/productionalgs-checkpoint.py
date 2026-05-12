from Simulator import *
from datetime import timedelta,date


#################################################################################
class ProductionAlgManager(AlgorithmManager): 
    def __init__(self,sim,workmgr):
        super().__init__(sim)
        self.ProdManager = workmgr

    def getProdManager(self):
        return self.ProdManager
        
        
    def setPriorityFunctions(self):

        self.getPriorityScoringFunctions()["Trailer Loading"] = dict()
        self.getPriorityScoringFunctions()["Trailer Loading"][("Select Items",'FindMostCommon')] = self.findTrailerLoadScores

        
        self.getPriorityScoringFunctions()["Trailer Transport"] = dict()
        self.getPriorityScoringFunctions()["Trailer Transport"][("Select Destination",'MostDemanded')] = self.findTrailerDestinationMostDemanded

        self.getPriorityScoringFunctions()["Trailer Unloading"] = dict()
        self.getPriorityScoringFunctions()["Trailer Unloading"][("Select Items", 'UnloadFeasible')] = self.findTrailerUnloadFeasible
        
        self.getPriorityScoringFunctions()["Machine Loading Automated"] = dict()
        self.getPriorityScoringFunctions()["Machine Loading Automated"][("Select Items",'HighestNoItems')] = self.findMachineLoadAutoHighestItems


        
        return
    

    def findTrailerLoadScores(self,event,items):
        print(" > "+str(self.getSimulator().getTime())+": >>> Algorithm: findTrailerLoadScores function <<<")
        
        select_dict = dict()
        for item in items:  
            myopr = item.getActiveOperation()
            if myopr!= None: 
                for mach in myopr.getAlternativeResources():
                    if not mach in select_dict:
                        select_dict[mach] = 0
                    select_dict[mach] += 1
            else:
                if not self.getProdManager().getCentralInventory() in select_dict:
                    select_dict[self.getProdManager().getCentralInventory()] = 0
                select_dict[self.getProdManager().getCentralInventory()] += 1
  
        # item 1: Next operation machines:  Mach1, Mach2
        # item 2: Next operation machines:  Mach1, Mach3
        # item 3: Next operation machines:  Mach4, Mach5

        #Scores: Item1: 3, Item2: 3, Item3: 2
        
        for item in items:
            myopr = item.getActiveOperation()
            if myopr!= None: 
                item.setPriorityScore(sum([select_dict[m] for m in myopr.getAlternativeResources()]))
            else:
                item.setPriorityScore(select_dict[self.getProdManager().getCentralInventory()])

        items.sort(key=lambda x: x.getPriorityScore(), reverse=True)

        return items

    def findTrailerDestinationMostDemanded(self,event,items):
        print(" > "+str(self.getSimulator().getTime())+": >>> Algorithm: findTrailerDestinationMostDemanded function <<<")
        select_dict = dict()
        for item in items:
            myopr = item.getActiveOperation()
            if myopr!= None: 
                for mach in myopr.getAlternativeResources():
                    if not mach in select_dict:
                        select_dict[mach] = 0
                    select_dict[mach] += 1
            else:
                if not self.getProdManager().getCentralInventory() in select_dict:
                    select_dict[self.getProdManager().getCentralInventory()] = 0
                select_dict[self.getProdManager().getCentralInventory()] += 1

        for item in items:  
            myopr = item.getActiveOperation()
            if myopr!= None: 
                item.setPriorityScore(sum([select_dict[m] for m in myopr.getAlternativeResources()]))
            else:
                item.setPriorityScore(select_dict[self.getProdManager().getCentralInventory()])


        items.sort(key=lambda x: x.getPriorityScore(), reverse=True)

        mostdemanded = None; highestdemand = 0

        for mymach,demand in select_dict.items():
            if mostdemanded == None:
                mostdemanded = mymach
                highestdemand = demand
            else: 
                if highestdemand < demand:
                    mostdemanded = mymach
                    highestdemand = demand

        return mostdemanded

    def findTrailerUnloadFeasible(self,event,items):
        print(" > "+str(self.getSimulator().getTime())+": >>> Algorithm: findTrailerUnloadFeasible function <<<")

        items_to_unload = []
     

        for item in items:
            myopr = item.getActiveOperation()
            

            if myopr!= None:
                print(" > "+str(self.getSimulator().getTime())+": >>> item ",item.getID()," opr ",myopr.getName(),  "ev loc ",event.getLocation().getName())
                if event.getLocation().getMachine() in myopr.getAlternativeResources():
                    items_to_unload.append(item)
            else:
                print(" > "+str(self.getSimulator().getTime())+": >>> item ",item.getID(),"to no  opr left ", "ev loc ",event.getLocation().getName())
                if event.getLocation() == self.getProdManager().getCentralInventory().getInputBuffer():
                    items_to_unload.append(item)
   
        return items_to_unload

 
        
    def findMachineLoadAutoHighestItems(self,event,items):
        
        print(" > "+str(self.getSimulator().getTime())+": >>> Algorithm: findMachineLoadAutoHighestItems function <<<")
        select_dict = dict()
        for item in items:
            myopr = item.getActiveOperation()
            if not myopr in select_dict:
                select_dict[myopr] = 0
            select_dict[myopr] += 1

        for item in items:
            item.setPriorityScore(select_dict[item.getActiveOperation()])

        items.sort(key=lambda x: x.getPriorityScore(), reverse=True)

        return items


