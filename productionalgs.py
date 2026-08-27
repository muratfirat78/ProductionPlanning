from Simulator import *
from datetime import timedelta,date


#################################################################################
class ProductionAlgManager(AlgorithmManager): 
    def __init__(self,sim,workmgr):
        super().__init__(sim,workmgr) 

        self.decisionalgs = dict() #key: decision type, val: [(algname,algfunction)] 

        self.decisionalgs["Select Items"] = dict() 
        self.decisionalgs["Select Items"]["EDDOrder"] = self.selectItemsEDDOrder
        self.decisionalgs["Select Items"]["UnloadFeasible"] = self.selectItemsFeasibletoUnload

        self.decisionalgs["Assign Equipment"] = dict() 
        self.decisionalgs["Assign Equipment"]["Straight Available"] = self.assignStraightEquipment

        self.decisionalgs["Assign Resource"] = dict() 
        self.decisionalgs["Assign Resource"]["Straight Available"] = self.assignStraightResource

        self.decisionalgs["Select Destination"] = dict() 
        self.decisionalgs["Select Destination"]['MostDemanded'] = self.selectDestinationEarliestAvailable

        self.decisionalgs["Assign Processor"] = dict() 
        self.decisionalgs["Assign Processor"]["Straight Available"] = self.assignStraightProcessor
      

    def getDecisionAlgorithms(self):
        return self.decisionalgs 

#####################################################################################################################
    def assignStraightEquipment(self,event):

        #self.getSimulator().saveLog("REPORT: >>> Algorithm: assignStraightEquipment function <<<")

        selected_equip = None 
             
        av_equip = [r for r in self.getOperationsManager().getResources() if r.isAvailable() and (r.getType() == event.getEventType().getEquipmentType())]
        comp_equip = [r for r in av_equip if (r.isIdle() and len(r.getItems()) == 0)]
 
                
        if len(comp_equip) > 0:  
            onloc_equip = [r for r in comp_equip if r.getLocation() == event.getFromLocation().getLocation()]
            selected_equip = onloc_equip[0] if len(onloc_equip) > 0 else comp_equip[0] 
        
        return selected_equip
###################################################################################################################################################
    def assignStraightProcessor(self,event):

        #self.getSimulator().saveLog("REPORT: >>> Algorithm: assignStraightProcessor function <<<")
        selected_equip = None

        
        if event.getEquipment().isAvailable():
            if event.getProcessor()!= None:
                selected_equip = event.getProcessor()
            else: 
                processr = event.getEquipment().getProcessor()
                if processr != None:
                    selected_equip = processr                 
            
        return selected_equip
###################################################################################################################################################
    def assignStraightResource(self,event):
        
        selected_res = None
    
        avail_comp_res = [r for r in self.getOperationsManager().getResources() if r.isAvailable() and r.getType() == event.getEventType().getResourceType()] 

        #if self.getSimulator().getTime() >= 3360 and event.getType() == "Loading" :
        #    self.getSimulator().saveLog(" REPORT: available resources: "+str(len(avail_comp_res))+"> "+event.getName()+"-"+str(event.getID()))
           
              
        idle_res = [r for r in avail_comp_res if r.isIdle()] 


        #if self.getSimulator().getTime() >= 3360 and event.getType() == "Loading" :
        #    self.getSimulator().saveLog(" REPORT: idle resources: "+str(len(avail_comp_res)))
     
        

        if len(idle_res) > 0:
            onloc_res = [r for r in idle_res if r.getLocation() == event.getLocation()]
            selected_res = onloc_res[0] if len(onloc_res) > 0 else idle_res[0]

          
        return selected_res
    
################################################################################################################################################    
    def selectItemsEDDOrder(self,event):
        self.getSimulator().saveLog(" >>> Algorithm: selectItemsEDDOrder <<<")

        select_dict = dict() #determine order items
        orders = []
        event_place = None

        if event.getType() == "Loading":
            event_place = event.getFromLocation()  
        if event.getType() == "Setup":
            event_place = event.getEquipment().getInputBuffer()
           
        for item in event_place.getItems():
            if item.getReservedEvent()!= event:
                continue
            myorder = item.getDemand()
            if not myorder in select_dict:
                select_dict[myorder] = []
                orders.append(myorder)
            select_dict[myorder].append(item)

        if len(orders) == 0:
            self.getSimulator().saveLog(" REPORT: event order list is empty! >>> Algorithm: selectItemsEDDOrder <<<")
            self.getSimulator().saveLog(" REPORT: items: "+str(len(event_place.getItems())))
            self.getSimulator().saveLog(" REPORT: this event "+str(event.getName())+"-"+str(event.getID()))
            
            return None

        
        orders.sort(key=lambda x: x.getDeadline(), reverse= False)      

        select_id = 0
        while len(select_dict[orders[select_id]]) > event_place.getCapacity():
            select_id+=1
            if select_id >= len(orders):
                return None
                
        return  select_dict[orders[select_id]]
################################################################################################################################################### 
    def selectDestinationEarliestAvailable(self, event):
 
        self.getSimulator().saveLog(" >>> Algorithm: selectByConsideringAlternativeMachines function <<<")
        self.getSimulator().saveLog(" >>> items in equip: " + str(len(event.getEquipment().getItems())))

        # 1. Collect all items being transported (from equipment or event)
        checkitems = event.getEquipment().getItems()
        if len(checkitems) == 0 and len(event.getItems()) > 0:
            checkitems = event.getItems()

        # 2. Map feasible destination candidates to their item demand count
        select_dict = dict()
        central_inventory = self.getOperationsManager().getCentralInventory()

        for item in checkitems:
            myopr = item.getActiveOperation()
            if myopr is not None:
                # Add all eligible alternative machines for this operation
                for mach in myopr.getAlternativeResources():
                    select_dict[mach] = select_dict.get(mach, 0) + 1
            else:
                # Items with no remaining operations go to Central Inventory
                select_dict[central_inventory] = select_dict.get(central_inventory, 0) + 1

        if not select_dict:
            return None

        # 3. Select candidate with minimum available time (tie-breaker: maximum item demand)
        def ranking_score(machine):
            avail_time = machine.getNextAvailableTime()
            demand = select_dict[machine]
            return (avail_time, -demand)

        selected_dest = min(select_dict.keys(), key=ranking_score)

        earliest_avail_time = selected_dest.getNextAvailableTime()

        self.getSimulator().saveLog(
            " >>> event " + event.getName() + "[" + str(event.getID()) + "] returning destination "
            + (selected_dest.getName() if selected_dest is not None else "None")
            + ", available time: " + str(earliest_avail_time)
            + ", dict size " + str(len(select_dict)) + " items " + str(len(checkitems))
        )

        return selected_dest

#########################################################################################################################################################
    def selectItemsFeasibletoUnload(self,event):
        self.getSimulator().saveLog(" >>> Algorithm: findTrailerUnloadFeasible function <<<")

        items_to_unload = []
 
        for item in event.getEquipment().getItems():
            myopr = item.getActiveOperation()

            #self.getSimulator().saveLog("REPORT: >>> Next operation none?: "+str(myopr == None))
            if myopr!= None:
                #print(" > "+str(self.getSimulator().getTime())+": >>> item ",item.getID()," opr ",myopr.getName(),  "ev loc ",event.getLocation().getName())
                if event.getToLocation().getMachine() in myopr.getAlternativeResources():
                    items_to_unload.append(item)
            else:
                #print(" > "+str(self.getSimulator().getTime())+": >>> item ",item.getID(),"to no  opr left ", "ev loc ",event.getLocation().getName())
                if event.getToLocation().getLocation() == self.getOperationsManager().getCentralInventory().getLocation():
                    items_to_unload.append(item)
            if len(items_to_unload) == event.getToLocation().getCapacity(): # this getCapacity should return the current available capacity, considering waiting items.  
                break
   
        return items_to_unload

####################################################################################################################################################     
