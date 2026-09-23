
from visual import *
from simulator import *
from productionmain import *
from logisticsmain import *
from ProductionMILPScheduling import * 

class Controller:
    def __init__(self,gitfolder,online):  
        self.online = online
        self.VisualManager = VisualManager()
        self.VisualManager.setController(self)
        self.Simulator = Simulator()
        self.Simulator.setController(self)
        self.WorkManager = None     
        self.MILPManager = ProductionMILPManager(self.Simulator)
        self.UseCase = None
        self.GitDir = gitfolder
        self.checkUseCases()

    def setGitDir(self,gitdir):
        self.GitDir = gitdir
        return
        
    def getGitDir(self):
        return self.GitDir

    def setOnline(self,online):
        self.online = online
        return 

    def isOnline(self):
        return self.online

    def getVisualManager(self):
        return self.VisualManager
  
  
    def getSimulator(self):
        return self.Simulator

    def getMILPManager(self):
        return self.MILPManager

    def checkUseCases(self):
        try: 
            if not self.isOnline(): 
                abs_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),"usecases")
                for root, dirs, files in os.walk(abs_file_path):
                    for name in files:
                        if name.find("_EventTypes.csv") > -1:
                            usecasename = name[:name.index("_EventTypes.csv")]
                            if not usecasename in self.getSimulator().getUseCases():
                                self.getSimulator().getUseCases().append(usecasename)
            else:
                source_directory = '/content/'
                for filename in os.listdir(source_directory):
                    if filename.find("_EventTypes.csv") > -1:
                        usecasename = filename[:filename.index("_EventTypes.csv")]
                        if not usecasename in self.getSimulator().getUseCases():
                            self.getSimulator().getUseCases().append(usecasename)

            
        except Exception as e:
            print("ERROR: in checking use cases "+str(e))    

        return 

    def setUseCase(self,usecase):
        
        self.UseCase = usecase
        try: 
            self.getSimulator().saveLog("REPORT: set use case  "+str(self.UseCase))
            if usecase == "Production":
                self.setWorkManager(ShopFloorManager(self.Simulator))
                self.getWorkManager().setDemandType("Product")
                
            if usecase == "Logistics":
                self.setWorkManager(LogisticsManager(self.Simulator))
                self.getWorkManager().setDemandType("Shipment")
    

            self.getSimulator().saveLog("REPORT: applying use case "+str(self.UseCase))
            self.applyUseCase()

        except Exception as e:
            self.getSimulator().saveLog("ERROR: in setting use case "+str(e))  
      


    
        return

    def applyUseCase(self):

        try: 

            abs_file_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                "usecases"
            )

            self.getSimulator().saveLog("REPORT: path "+str(abs_file_path))

            myworkmgr = self.getWorkManager()

            
            for root, dirs, files in os.walk(abs_file_path):
                self.getSimulator().saveLog("REPORT: files "+str(files))
                     
                for name in files:
                                    
                    if name.find(self.UseCase+"_EventTypes.csv") > -1:

                      
            
                        events_df = pd.read_csv(abs_file_path+'/'+self.UseCase+"_EventTypes.csv")

                        for i,r in events_df.iterrows():
                            eventtype = SimEvent(self.getSimulator(),r['Name'],r['Type'],r["ResourceType"],r["EquipmentType"],bool(r["Preemptable"]))
                            myworkmgr.getEventTypes()[eventtype.getName()]= eventtype
                            self.getSimulator().saveLog("REPORT: eventtype defined: "+str(eventtype.getName()))

                        self.getSimulator().saveLog("REPORT: eventtypes "+str(myworkmgr.getEventTypes().keys()))
                        for eventtypename,eventtype in myworkmgr.getEventTypes().items():
                            ev_df = events_df[events_df["Name"] == eventtypename]
                            self.getSimulator().saveLog("REPORT: eventtype df "+str(len(ev_df)))
                            for i,r in ev_df.iterrows():
                                if not pd.isna(r['Successor']):
                                    if r['Successor'] in myworkmgr.getEventTypes():
                                        succ_event = myworkmgr.getEventTypes()[r['Successor']]
                                        if not succ_event in eventtype.getSuccessorDict():
                                            eventtype.getSuccessorDict()[succ_event] = "Finish to Start"
                                            self.getSimulator().saveLog("REPORT: eventtype "+str(eventtypename)+" has successor  "+r['Successor'])
                                        else:
                                            self.getSimulator().saveLog("REPORT: successor  "+r['Successor']+" is not found in successordict...")
                                        
                                    else:
                                        self.getSimulator().saveLog("ERROR: successor  "+r['Successor']+" is not found in eventtypes...")
                      

                        decisions_df = pd.read_csv(abs_file_path+'/'+self.UseCase+"_Decisions.csv")
                        self.getSimulator().saveLog("REPORT: decisions_df "+str(len(decisions_df)))
                        for eventtypename,eventtype in myworkmgr.getEventTypes().items():
                            event_df = decisions_df[decisions_df["EventType"] == eventtypename]
                            if not (eventtypename in myworkmgr.getAlgorithmSetting()):
                                myworkmgr.getAlgorithmSetting()[eventtypename] = dict()
                                
                            for i,r in event_df.iterrows():

                                self.getSimulator().saveLog("REPORT: eventtype "+str(eventtypename)+"  decisions case none? "+str(pd.isna(r['Case'])))
                                if not pd.isna(r['Case']):
                                    if not r['Case'] in eventtype.getDecisionsDict():
                                        eventtype.getDecisionsDict()[r['Case']] = []

                                    self.getSimulator().saveLog("REPORT: eventtype "+str(eventtypename)+" case "+str(r['Case'])+" decision "+str(r['DecisionType']))
                                    eventtype.getDecisionsDict()[r['Case']].append(r['DecisionType'])
                                self.getSimulator().saveLog("REPORT: decision type "+str(r['DecisionType'])+", alg: "+str(r['DecisionAlgorithm']))
                                myworkmgr.getAlgorithmSetting()[eventtypename][r['DecisionType']]= r['DecisionAlgorithm']
                               
                        precedenceinfo_df = pd.read_csv(abs_file_path+'/'+self.UseCase+"_PrecedenceInfo.csv")
                        #self.getOperationsManager().getSimulator().saveLog("REPORT: precedenceinfo_df size "+str(len(precedenceinfo_df)))
                        
                        for eventtypename,eventtype in myworkmgr.getEventTypes().items():
                            event_df = precedenceinfo_df[precedenceinfo_df["Predecessor"] == eventtypename]

                            for i,r in event_df.iterrows():
                                if not r['Successor'] in eventtype.getPrecendenceDict():
                                    eventtype.getPrecendenceDict()[r['Successor']] = []
                                eventtype.getPrecendenceDict()[r['Successor']].append(r['PrecedenceInfo'])

                        #self.getOperationsManager().getSimulator().saveLog("REPORT: precedenceinfo_df applied ")

                            
       
        except Exception as e:
            self.getSimulator().saveLog("ERROR: in reading use case "+str(e))  
     
        return

    def setWorkManager(self,wrkmgr):
        self.WorkManager = wrkmgr
        return 

    def getWorkManager(self):
        return self.WorkManager

    def getUseCase(self):
        return self.UseCase

    
    def GetDashBoard(self):

        print("Controller: Generating dashboard")
        return self.VisualManager.GenerateMainTab()

    