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
        self.decisionalgs["Select Destination"]['MostDemanded'] = self.selectDestionationMostDemanded
      

    def getDecisionAlgorithms(self):
        return self.decisionalgs 

#####################################################################################################################
    def assignStraightEquipment(self,event):

        #self.getSimulator().saveLog("REPORT: >>> Algorithm: assignStraightEquipment function <<<")

        selected_equip = None 

        #self.getSimulator().saveLog("REPORT: >>> event:  "+str(event.getName()))
        
        if event.getName() == "Machine Setup": 
        
            if event.getFromLocation().getMachine().isAvailable():
                
                if event in event.getFromLocation().getMachine().getProcessMatch():
                    selected_equip = event.getFromLocation().getMachine().getProcessMatch()[event]
                else:
                    processr = event.getFromLocation().getMachine().getProcessor()
                    
                    
                    if processr != None:
                        selected_equip = processr
        else:        
            if event.getName() == "Machine Processing": 
            # only resume case, equipment/processor is only checked for availability. 
                if event.getEquipment().isAvailable():
                    selected_equip = event.getProgressList()[-1][0] 
                    
            else:
            # event types: trailer loading (case: handle)
                #self.getSimulator().saveLog("REPORT: >>> Algorithm str equip: event location: "+str(event.getLocation().getName()))
             
                av_equip = [r for r in self.getOperationsManager().getResources() if r.isAvailable() and (r.getType() == event.getEventType().getEquipmentType())]
                
                #self.getSimulator().saveLog("REPORT: av_equip: "+str(len(av_equip)))   
                comp_equip = [r for r in av_equip if (r.isIdle())]
                #self.getSimulator().saveLog("REPORT: comp_equip: "+str(len(comp_equip)))
                
                if len(comp_equip) > 0:  
                    onloc_equip = [r for r in comp_equip if r.getLocation() == event.getFromLocation().getLocation()]
                    #self.getSimulator().saveLog("REPORT: onloc_equip: "+str(len(onloc_equip)))
                    selected_equip = onloc_equip[0] if len(onloc_equip) > 0 else comp_equip[0] 

                
        return selected_equip
###################################################################################################################################################
    def assignStraightResource(self,event):

        selected_res = None

        # events requiring this algorithm: 
        # 1: Trailer loading(handle), Machine Setup(handle), Machine Loading(handle,resume), Machine Unloading (handle,resume), 
         
    
        avail_comp_res = [r for r in self.getOperationsManager().getResources() if r.isAvailable() and r.getType() == event.getEventType().getResourceType()] 

        #self.getSimulator().saveLog(" REPORT: >>> assignStraightResource: avail_comp_res "+str(len(avail_comp_res)))
        
        idle_res = [r for r in avail_comp_res if r.isIdle()] 
      
        #self.getSimulator().saveLog("REPORT: >>> Algorithm str res: event location: "+str(event.getLocation().getName()))
        #self.getSimulator().saveLog("REPORT:  >>> Algorithm: idle_res "+str(len(idle_res)))
        if len(idle_res) > 0:
            
            onloc_res = [r for r in idle_res if r.getLocation() == event.getLocation()]
            #self.getSimulator().saveLog("REPORT: >>> Algorithm: onloc_res "+str(len(onloc_res)))

            selected_res = onloc_res[0] if len(onloc_res) > 0 else idle_res[0]

           

        return selected_res
    
################################################################################################################################################    
    def selectItemsEDDOrder(self,event):
        self.getSimulator().saveLog(" >>> Algorithm: findTrailerLoadEarliestOrder function <<<")

        select_dict = dict() #determine order items
        orders = []
    
        for item in event.getFromLocation().getItems():
            if item.getReservedEvent()!= None:
                continue
            myorder = item.getDemand()
            if not myorder in select_dict:
                select_dict[myorder] = []
                orders.append(myorder)
            select_dict[myorder].append(item)

        orders.sort(key=lambda x: x.getDeadline(), reverse= False)      

        select_id = 0

        #self.getSimulator().saveLog("REPORT: >>> Algorithm: findTrailerLoadEarliestOrder <<<  tolocation None? "+str(event.getToLocation() == None))
        
        selection_loc = event.getToLocation() if event.getName() != "Machine Setup" else event.getFromLocation().getMachine()

        
        while len(select_dict[orders[select_id]]) > selection_loc.getCapacity():
            select_id+=1
            if select_id >= len(orders):
                return None
                
        return  select_dict[orders[select_id]]
###################################################################################################################################################        
    def selectDestionationMostDemanded(self,event):
        self.getSimulator().saveLog(" >>> Algorithm: findTrailerDestinationMostDemanded function <<<")
        self.getSimulator().saveLog(" >>> items in equip: "+str(len(event.getEquipment().getItems())))
        select_dict = dict()
        
        for item in event.getEquipment().getItems():
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

        mostdemanded = None; highestdemand = 0

        for mymach,demand in select_dict.items():
            if mostdemanded == None:
                mostdemanded = mymach
                highestdemand = demand
            else: 
                if highestdemand < demand:
                    mostdemanded = mymach
                    highestdemand = demand
        self.getSimulator().saveLog(" >>> event "+event.getName()+"["+str(event.getID())+"] returning... None? "+str(mostdemanded == None)+", dict size "+str(len(select_dict))+" items "+str(len(event.getEquipment().getItems())))

        
        return mostdemanded
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
'''
        if self.getSimulator().getTime() > 475:
            for r in self.getOperationsManager().getResources():
                if r.getType() == event.getEventType().getResourceType() and r.isAvailable():
                    self.getSimulator().saveLog(" REPORT: >>> res "+str(r.getName())+", av: "+str(r.isAvailable())+", idle: "+str(r.isIdle()))
'''  