from Simulator import *
from datetime import timedelta,date


#################################################################################
class ProductionAlgManager(AlgorithmManager): 
    def __init__(self,sim,workmgr):
        super().__init__(sim,workmgr) 
        
    def setPriorityFunctions(self):

        # self.getPriorityScoringFunctions()[event name][(decision_type,decision_alg)] = alg_function

        self.getPriorityScoringFunctions()["Trailer Loading"] = dict()
        self.getPriorityScoringFunctions()["Trailer Loading"][("Select Items",'EDDOrder')] = self.findTrailerLoadEarliestOrder
        self.getPriorityScoringFunctions()["Trailer Loading"][("Assign Equipment","Straight Available")] = self.assignStraightEquipment
        self.getPriorityScoringFunctions()["Trailer Loading"][("Assign Resource","Straight Available")] = self.assignStraightResource

        self.getPriorityScoringFunctions()["Trailer Transport"] = dict()
        self.getPriorityScoringFunctions()["Trailer Transport"][("Select Destination",'MostDemanded')] = self.findTrailerDestinationMostDemanded

        self.getPriorityScoringFunctions()["Trailer Unloading"] = dict()
        self.getPriorityScoringFunctions()["Trailer Unloading"][("Select Items", 'UnloadFeasible')] = self.findTrailerUnloadFeasible


        self.getPriorityScoringFunctions()["Machine Setup"] = dict()
        self.getPriorityScoringFunctions()["Machine Setup"][("Assign Equipment","Straight Available")] = self.assignStraightEquipment
        self.getPriorityScoringFunctions()["Machine Setup"][("Assign Resource","Straight Available")] = self.assignStraightResource
        self.getPriorityScoringFunctions()["Machine Setup"][("Select Items",'EDDOrder')] = self.findMachineSetupSelectEDD

        self.getPriorityScoringFunctions()["Machine Loading"] = dict()
        self.getPriorityScoringFunctions()["Machine Loading"][("Assign Resource","Straight Available")] = self.assignStraightResource

        self.getPriorityScoringFunctions()["Processing"] = dict()
        self.getPriorityScoringFunctions()["Processing"][("Assign Equipment","Straight Available")] = self.assignStraightEquipment


        self.getPriorityScoringFunctions()["Machine Unloading"] = dict()
        self.getPriorityScoringFunctions()["Machine Unloading"][("Assign Resource","Straight Available")] = self.assignStraightResource


      
        return

    def assignStraightEquipment(self,event):

        self.getSimulator().saveLog(" >>> Algorithm: assignStraightEquipment function <<<")

        selected_equip = None 

        self.getSimulator().saveLog(" >>> event type:  "+str(event.getEventType().getName()))
        
        if event.getEventType().getName() == "Machine Setup": 
            event_mach = event.getLocation()

            if event_mach.isAvailable():
                processr = event_mach.getProcessor()
                self.getSimulator().saveLog(" Assign processor at machine "+event_mach.getName()+" processor found? "+str(processr != None))
                
                if processr != None:
                    event_mach.getProcessMatch()[event] = processr
                    selected_equip = event_mach

        else:
            

            av_equip = [r for r in self.getOperationsManager().getResources() if r.isAvailable() and (r.getType() == event.getEventType().getEquipmentType())]
    
            self.getSimulator().saveLog(" av_equip: "+str(len(av_equip)))
            
            comp_equip = [r for r in av_equip if (r.isIdle())]
    
            self.getSimulator().saveLog(" comp_equip: "+str(len(comp_equip)))
            if len(comp_equip) > 0:  
                onloc_equip = [r for r in comp_equip if r.getLocation() == event.getLocation()]
                selected_equip = onloc_equip[0] if len(onloc_equip) > 0 else comp_equip[0] 
                
   
        return selected_equip

    def assignStraightResource(self,event):

        selected_res = None
        
        
        avail_res = [r for r in self.getOperationsManager().getResources() if r.isAvailable() and r.getType() == event.getEventType().getResourceType()] 

        #if event.getName() == 'Machine Loading' or ((self.getSimulator().getTime() >= 2880) and (self.getSimulator().getTime() <= 2980)):
        #    self.getSimulator().saveLog("ERROR check: "+str(event.getName())+"("+str(event.getID())+")"+" avail_res: "+str(len(avail_res)))
        #    self.getSimulator().saveLog("ERROR check: "+"getResourceType: "+str(event.getEventType().getResourceType()))
            #self.getSimulator().saveLog(" avail_res: "+str(len(avail_res)))
            
        idle_res = [r for r in avail_res if (r.isIdle() and len(r.getMyEvents()) == 0)] 
    
        if len(idle_res) > 0:
            self.getSimulator().saveLog(str([r.getName()+"->"+str(r.getLocation() == None) for r in idle_res]))
    
            

        #if event.getName() == 'Machine Loading':
        #    self.getSimulator().saveLog("ERROR check: "+str(event.getName())+"("+str(event.getID())+")"+" idle_res: "+str(len(idle_res)))
            #self.getSimulator().saveLog(" >>> Algorithm: assignStraightResource function <<<"+str(len(idle_res)))
            
        if len(idle_res) > 0:
            onloc_res = [r for r in idle_res if r.getLocation() == event.getLocation()]
            self.getSimulator().saveLog(" >>> Algorithm: onloc_res "+str(len(onloc_res)))
            selected_res = onloc_res[0] if len(onloc_res) > 0 else idle_res[0]

           

        return selected_res
    

        
    def findTrailerLoadEarliestOrder(self,event):
        self.getSimulator().saveLog(" >>> Algorithm: findTrailerLoadEarliestOrder function <<<")

        select_dict = dict() #determine order items
        orders = []
        for item in event.getPlace().getItems():  
            myorder = item.getDemand()
            if not myorder in select_dict:
                select_dict[myorder] = []
                orders.append(myorder)
            select_dict[myorder].append(item)

        orders.sort(key=lambda x: x.getDeadline(), reverse= False)      
        return  select_dict[orders[0]]
        

    def findTrailerDestinationMostDemanded(self,event):
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
        if mostdemanded == None: 
            for mymach,demand in select_dict.items():
                self.getSimulator().saveLog(" >>> mach "+mymach.getName()+" demand "+str(demand))
            for item in event.getEquipment().getItems():
                myopr = item.getActiveOperation()
                if myopr!=None:
                    self.getSimulator().saveLog(" >>> item "+str(item.getID())+" active opr "+myopr.getName()+" alts: "+str(len(myopr.getAlternativeResources())))
        return mostdemanded

    def findTrailerUnloadFeasible(self,event):
        self.getSimulator().saveLog(" >>> Algorithm: findTrailerUnloadFeasible function <<<")

        items_to_unload = []
     

        for item in event.getEquipment().getItems():
            myopr = item.getActiveOperation()
 
            if myopr!= None:
                #print(" > "+str(self.getSimulator().getTime())+": >>> item ",item.getID()," opr ",myopr.getName(),  "ev loc ",event.getLocation().getName())
                if event.getLocation() in myopr.getAlternativeResources():
                    items_to_unload.append(item)
            else:
                #print(" > "+str(self.getSimulator().getTime())+": >>> item ",item.getID(),"to no  opr left ", "ev loc ",event.getLocation().getName())
                if event.getLocation() == self.getOperationsManager().getCentralInventory():
                    items_to_unload.append(item)
   
        return items_to_unload

 
        
    def findMachineSetupSelectEDD(self,event):
        
        self.getSimulator().saveLog(" >>> Algorithm: findMachineSetupSelectEDD function <<<")
        
        select_dict = dict() #determine order items
        
        orders = []

        self.getSimulator().saveLog(" >event none?"+str(type(event.getPlace())))
        for item in event.getPlace().getItems():  
            myorder = item.getDemand()
            if not myorder in select_dict:
                select_dict[myorder] = []
                orders.append(myorder)
            select_dict[myorder].append(item)

        orders.sort(key=lambda x: x.getDeadline(), reverse= False)   
        self.getSimulator().saveLog(" >>> Algorithm: findMachineSetupSelectEDD function end <<<")
        return  select_dict[orders[0]]


