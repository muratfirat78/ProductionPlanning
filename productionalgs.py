from Simulator import *
from datetime import timedelta,date


#################################################################################
class ProductionAlgManager(AlgorithmManager): 
    def __init__(self,sim,workmgr):
        super().__init__(sim,workmgr) 
        
    def setPriorityFunctions(self):

        self.getPriorityScoringFunctions()["Trailer Loading"] = dict()
        self.getPriorityScoringFunctions()["Trailer Loading"][("Select Items",'FindMostCommon')] = self.findTrailerLoadScores

        self.getPriorityScoringFunctions()["Trailer Loading"][("Select Items",'EDDOrder')] = self.findTrailerLoadEarliestOrder
        # one-prodorder items at a time loaded to trailer.  

        
        self.getPriorityScoringFunctions()["Trailer Transport"] = dict()
        self.getPriorityScoringFunctions()["Trailer Transport"][("Select Destination",'MostDemanded')] = self.findTrailerDestinationMostDemanded

        self.getPriorityScoringFunctions()["Trailer Unloading"] = dict()
        self.getPriorityScoringFunctions()["Trailer Unloading"][("Select Items", 'UnloadFeasible')] = self.findTrailerUnloadFeasible
        
        self.getPriorityScoringFunctions()["Machine Loading"] = dict()
        self.getPriorityScoringFunctions()["Machine Loading"][("Select Items",'HighestNoItems')] = self.findMachineLoadAutoHighestItems

        self.getPriorityScoringFunctions()["Assign Event Equipment"] = dict()
        self.getPriorityScoringFunctions()["Assign Event Equipment"]["Straight Available"] = self.assignStraightEquipment

        self.getPriorityScoringFunctions()["Assign Event Resource"] = dict()
        self.getPriorityScoringFunctions()["Assign Event Resource"]["Straight Available"] = self.assignStraightResource

      
        return

    def assignStraightEquipment(self,event):

        self.getSimulator().saveLog(" >>> Algorithm: assignStraightEquipment function <<<")
        
        comp_equip = [r for r in self.getOperationsManager().getResources() if r.IsIdle() and (r.getType() == event.getEventType().getEquipmentType())]

        selected_equip = None 

        if len(comp_equip) > 0:
                
            onloc_equip = [r for r in comp_equip if r.getLocation() == event.getLocation()]
            comp_res = [r for r in self.getOperationsManager().getResources() if r.IsIdle() and (r.getType() == event.getEventType().getResourceType())]

            selected_equip = onloc_equip[0] if len(onloc_equip) > 0 else comp_equip[0] 
            
            event.setEquipment(selected_equip)
            selected_equip.setAssigned()    
            selected_equip.getAssignedEvents().append(event)     

        return selected_equip

    def assignStraightResource(self,event):
        
        
        comp_res = [r for r in self.getOperationsManager().getResources() if r.IsIdle() and (r.getType() == event.getEventType().getResourceType())] 

        if len(comp_res) > 0:
            self.getSimulator().saveLog(" >>> Algorithm: assignStraightResource function <<<")

        selected_res = None
        
        if len(comp_res) > 0:
 
            onloc_res = [r for r in comp_res if r.getLocation() == event.getLocation()]
            selected_res = onloc_res[0] if len(onloc_res) > 0 else comp_res[0]

            event.setResource(selected_res)
            selected_res.setAssigned()   
            selected_res.getAssignedEvents().append(event)
            

        return selected_res
    

    
    def findTrailerLoadScores(self,event,items):
        self.getSimulator().saveLog(" >>> Algorithm: findTrailerLoadScores function <<<")
        
        select_dict = dict()
        for item in items:  
            myopr = item.getActiveOperation()
            if myopr!= None: 
                for mach in myopr.getAlternativeResources():
                    if not mach in select_dict:
                        select_dict[mach] = 0
                    select_dict[mach] += 1
            else:
                if not self.getOperationsManager().getCentralInventory() in select_dict:
                    select_dict[self.getOperationsManager().getCentralInventory()] = 0
                select_dict[self.getOperationsManager().getCentralInventory()] += 1

        
        for item in items:
            myopr = item.getActiveOperation()
            if myopr!= None: 
                item.setPriorityScore(sum([select_dict[m] for m in myopr.getAlternativeResources()]))
            else:
                item.setPriorityScore(select_dict[self.getOperationsManager().getCentralInventory()])

        items.sort(key=lambda x: x.getPriorityScore(), reverse=True)

        return items
        
    def findTrailerLoadEarliestOrder(self,event,items):
        self.getSimulator().saveLog(" >>> Algorithm: findTrailerLoadEarliestOrder function <<<")

        select_dict = dict() #determine order items
        orders = []
        for item in items:  
            myorder = item.getDemand()
            if not myorder in select_dict:
                select_dict[myorder] = []
                orders.append(myorder)
            select_dict[myorder].append(item)

        orders.sort(key=lambda x: x.getDeadline(), reverse= False)      
        return  select_dict[orders[0]]

    def findTrailerDestinationMostDemanded(self,event,items):
        self.getSimulator().saveLog(" >>> Algorithm: findTrailerDestinationMostDemanded function <<<")
        select_dict = dict()
        for item in items:
            myopr = item.getActiveOperation()
            #print("Active operation of item",item.getID(),myopr.getName())
            if myopr!= None: 
                for mach in myopr.getAlternativeResources():
                    if not mach in select_dict:
                        select_dict[mach] = 0
                    select_dict[mach] += 1
            else:
                if not self.getOperationsManager().getCentralInventory() in select_dict:
                    select_dict[self.getOperationsManager().getCentralInventory()] = 0
                select_dict[self.getOperationsManager().getCentralInventory()] += 1

        for item in items:  
            myopr = item.getActiveOperation()
            if myopr!= None: 
                item.setPriorityScore(sum([select_dict[m] for m in myopr.getAlternativeResources()]))
            else:
                item.setPriorityScore(select_dict[self.getOperationsManager().getCentralInventory()])


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
        self.getSimulator().saveLog(" >>> Algorithm: findTrailerUnloadFeasible function <<<")

        items_to_unload = []
     

        for item in items:
            myopr = item.getActiveOperation()
            

            if myopr!= None:
                #print(" > "+str(self.getSimulator().getTime())+": >>> item ",item.getID()," opr ",myopr.getName(),  "ev loc ",event.getLocation().getName())
                if event.getLocation().getMachine() in myopr.getAlternativeResources():
                    items_to_unload.append(item)
            else:
                #print(" > "+str(self.getSimulator().getTime())+": >>> item ",item.getID(),"to no  opr left ", "ev loc ",event.getLocation().getName())
                if event.getLocation() == self.getOperationsManager().getCentralInventory().getInputBuffer():
                    items_to_unload.append(item)
   
        return items_to_unload

 
        
    def findMachineLoadAutoHighestItems(self,event,items):
        
        self.getSimulator().saveLog(" >>> Algorithm: findMachineLoadAutoHighestItems function <<<")
        select_dict = dict()
        for item in items:
            myopr = item.getActiveOperation()
            if not myopr in select_dict:
                select_dict[myopr] = 0
            select_dict[myopr] += 1

        highest_opr = None; max_items = 0
        for opr,noitems in select_dict.items():
            self.getSimulator().saveLog("Opr: "+opr.getName()+", items: "+str(noitems))
            if highest_opr == None:
                highest_opr = opr; max_items = noitems
            else:
                if max_items < noitems:
                    highest_opr = opr; max_items = noitems
                
        # here choose one operation and send these items..
        return [i for i in items if i.getActiveOperation() == highest_opr]


