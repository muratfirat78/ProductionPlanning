from Simulator import *
from datetime import timedelta,date
from productionobjects import *
from productionalgs import *
from productionChecker import *
from datetime import timedelta,date,datetime
import numpy as np

class ProductionDataManager(DataManager): 
    def __init__(self,sim,workmgr):
        super().__init__(sim,workmgr) 

###########################################################################################
    def ReadResources(self):
     u
        rel_path = '/'+self.getOperationsManager().getUseCase()
        abs_file_path = os.path.dirname(os.path.realpath(__file__))+rel_path
        
        print(abs_file_path)

        

        latestfiledate = None
        filename = None

        for root, dirs, files in os.walk(abs_file_path):
            for file in files: 
                print(file)
                if ".csv" in file:                  
                    try: 
                        filedate = datetime.strptime(file[file.find("Resources_")+len("Resources_"):-5],"%Y-%m-%d")
                        if latestfiledate == None:
                            latestfiledate = filedate
                            filename = file
                        else:
                            if latestfiledate < filedate:
                                latestfilsedate = filedate
                                filename = file
               
                    except Exception as e:s
                        pass

        if latestfiledate != None:
            print("Latest Date resources file date: ",latestfiledate)
            TBRMResources_df = pd.read_csv(abs_file_path+'/'+filename)

            print(TBRMResources_df.info())
            for i,r in TBRMResources_df.iterrows():
                if r['ResourceType'] == 'Operator':
                    AvlShifts = [1]  
                    try: 
                        AvlShifts = r['AvailableShifts'].split("_")
                        AvlShifts = [int(s) for s in AvlShifts]
                    except Exception as e:
                        print("Error in reading available shifts of operator ",r['Name'])
                    #myname,avshifts,mycap,sim,workmngr
                    optr = Operator(r['Name'],AvlShifts,1,self.getSimulator(),self.getOperationsManager())
                    optr.setLocation(self.getOperationsManager().getCentralInventory())
                    self.getOperationsManager().getResources().append(optr) 
                if r['ResourceType'] == 'Machine': #mycap,sim,workmngr  

                    mcode = r['Name'][r['Name'].find("(")+1:]
                    mcode = mcode[:mcode.find(")")]

                    #print("machine code",mcode)

                    OperatingShifts = [1]  
                    try: 
                        OperatingShifts = r['AvailableShifts'].split("_")
                        OperatingShifts = [int(s) for s in OperatingShifts]
                    except Exception as e:
                        print("Error in reading operating shifts of machine ",r['Name'])

                    Alternatives = []
                    if not pd.isna(r['Alternatives']): 
                        try: 
                            Alternatives = r['Alternatives'].split("~")
                        except Exception as e:
                            print("Error in reading alternatives of machine ",r['Name'],":",pd.isna(r['Alternatives']))

                    #myname,machcode,OprtingShifts,processtype,automated,mycap,Alternatives,OprtingEffort,sim,workmngr
                    if len(Alternatives) > 0:
                        print(Alternatives)
                    mach = Machine(mcode,r['Name'],OperatingShifts,r['ProcessType'],r['Automated'],50000,Alternatives,int(r['SetupTime']),float(r['OperatingEffort']),self.getSimulator(),self.getOperationsManager())
                
                    mach.setLocation(mach)
                    self.getOperationsManager().getResources().append(mach)
                    
            
            print("No resources: ",len(self.getOperationsManager().getResources()))         
           
        return
        
#####################################################################################################################################
    def ReadDemandFile(self):
        rel_path = '/'+self.getOperationsManager().getUseCase()
        abs_file_path = os.path.dirname(os.path.realpath(__file__))+rel_path
        
        print(abs_file_path)

        

        latestfiledate = None
        filename = None

        for root, dirs, files in os.walk(abs_file_path):
            for file in files: 
                print(file)
                if ".xlsx" in file:                  
                    try: 
                        #print("Length: ","Production Orders_",len("Production Orders_"))
                        filedate = datetime.strptime(file[file.find("Production Orders_")+18:-5],"%Y-%m-%d")
                        if latestfiledate == None:
                            latestfiledate = filedate
                            filename = file
                        else:
                            if latestfiledate < filedate:
                                latestfiledate = filedate
                                filename = file
               
                    except Exception as e:
                        pass

        if latestfiledate != None:

           
            print("Latest Date input file date: ",latestfiledate)
            TBRM_df = pd.read_excel(abs_file_path+'/'+filename)

            print([x for x in TBRM_df["Work Orders/Status"].unique()])

            #TBRM_df.info()
            TBRM_df["Index"] = [i for i in range(len(TBRM_df))]
           

            TBRM_df["Deadline"] = TBRM_df["Deadline"].fillna(TBRM_df["Deadline"].max()+timedelta(days=7))
            TBRM_df["Components/Product"] = TBRM_df["Components/Product"].fillna("UnknownRawMaterial")
            TBRM_df["Components/Product/ID"] = TBRM_df["Components/Product/ID"].fillna("UnknownRawMaterialID")
            TBRM_df["Components/Quantity To Consume"] = TBRM_df["Components/Quantity To Consume"].fillna("UnknownRawMaterialQ")
            
           
            #TBRM_df.info()
           
  
            print("Size of input file: ",len(TBRM_df))

            prodorder_aggrfeats = [x[1] for x in self.getOperationsManager().getDataManager().getObjectFeatures()["ProductionOrder"]]
            print("Prod order feats to aggregte: ",prodorder_aggrfeats)
     
            prodorders_df = TBRM_df.groupby(prodorder_aggrfeats).size().reset_index() 

            ####### PRODUCTS TO PRODUCE 
            prod_aggrfeats = [x[1] for x in self.getOperationsManager().getDataManager().getObjectFeatures()["Product"]]
            products_df = prodorders_df.groupby(prod_aggrfeats).size().reset_index()

            for i,r in products_df.iterrows():
                prodpn = None
                if "[" in r['Product']:
                    prodpn = r['Product'][r['Product'].find("[")-1:]
                    prodpn = r['Product'][:r['Product'].find("]")+1]
                else:
                    prodpn = r['Product']
                    
                myproduct= Product(prodpn,str(r['Product/ID']),r['Product'])
                self.getOperationsManager().getProducts()[myproduct.getID()]= myproduct
    
                #print(i,"Product created with PN:",myproduct.getPN())
                
           ####### RAW MATERIALS 
            rawmat_aggrfeats = [x[1] for x in self.getOperationsManager().getDataManager().getObjectFeatures()["RawMaterial"]]

            raw_materials_df = prodorders_df.groupby(rawmat_aggrfeats).size().reset_index()
            for i,r in raw_materials_df.iterrows():
                prodpn = None
                if "[" in r['Components/Product']:
                    prodpn = r['Components/Product'][r['Components/Product'].find("[")-1:]
                    prodpn = r['Components/Product'][:r['Components/Product'].find("]")+1]
                else:
                    prodpn = r['Components/Product']
                    
                myproduct= Product(prodpn,str(r['Components/Product/ID']),r['Components/Product'])
                self.getOperationsManager().getProducts()[myproduct.getID()]= myproduct
    
                #print(i,"Raw Material created with PN:",myproduct.getPN())

            prodorders = []

            ## Create Production Orders
            for i,r in prodorders_df.iterrows():
                props = [x[1] for x in self.getOperationsManager().getDataManager().getObjectFeatures()["ProductionOrder"]]
              
                myprod = self.getOperationsManager().getProducts()[str(r[props[1]])]

                if str(r[props[9]]) in self.getOperationsManager().getProducts():
                    myraw = self.getOperationsManager().getProducts()[str(r[props[9]])]
   
                    myprod.getPredecessors()[myraw] = r[props[10]]
                    myraw.getSuccessors()[myprod] = r[props[10]]
                    
                prodorder = ProductionOrder(r[props[7]],r[props[2]],myprod,int(r[props[4]]),r['Index']) #ddline,myid,demtype,quantity,dfindex

                self.getOperationsManager().getProductionOrders()[prodorder.getID()] = prodorder
                prodorders.append((r['Index'],prodorder))

            prodorders.sort(key=lambda x: x[0], reverse=False)
      
            #print(TBRM_df.head(25))

            ###### Read the operation sequences 
            prodordind = 0 
            for prodordind in range(len(prodorders)):
                #print(prodordind,"Production order created:",prodorders[prodordind][1].getID()," of prod id",prodorders[prodordind][1].getFinalProduct().getID(),"index ",prodorders[prodordind][0])

                if prodordind < len(prodorders)-1:
                    for i in range(prodorders[prodordind][0],prodorders[prodordind+1][0]):
                        TBRM_df.iloc[i, TBRM_df.columns.get_loc('ID')] = prodorders[prodordind][1].getID()
                
                prodordind+=1

            TBRM_Operations_df = TBRM_df.groupby(['ID'], dropna=True)[['Work Orders/Work Center','Work Orders/Work Center/ID','Work Orders/Operation','Work Orders/Expected Duration','Work Orders/Start','Work Orders/End','Work Orders/Status']].agg(lambda x:list(x)).reset_index()


            machines = [r for r in self.getOperationsManager().getResources() if isinstance(r,Machine)]

            print("The system has ",len(machines),"machines")

            for i,r in TBRM_Operations_df.iterrows():
                OprResources = r['Work Orders/Work Center']
                OprResourceIDs = r['Work Orders/Work Center/ID']
                OprProcTimes = r['Work Orders/Expected Duration']
                OprStatus = r['Work Orders/Status']
                OprStarts = r['Work Orders/Start']
                OprFinishes = r['Work Orders/End'] 

                #print(OprStatus)

                oprsequence = []

                prodorder = self.getOperationsManager().getProductionOrders()[r['ID']]

              
                for resid in range(len(OprResources)):
                    #first find the resource

                    prodorder.getOperationsStatus().append((OprStatus[resid],(OprStarts[resid],OprFinishes[resid])))
                    oprres = OprResources[resid]

                    
                    if not pd.isna(oprres): 
                        for mach in machines:
                            if mach.getMachineCode() in oprres:
                                if mach.getID() != OprResourceIDs[resid]:
                                    mach.setID(OprResourceIDs[resid])
                                myopr = Operation(oprres,self.getOperationsManager().giveProcessID(),OprProcTimes[resid],None) #name,myid,proctime
                                myopr.getAlternativeResources().append(mach)
                                for mach_alternative in mach.getAlternatives():
                                    for mymach in machines:
                                        if mymach.getMachineCode() == mach_alternative:
                                            myopr.getAlternativeResources().append(mymach)
                                            break
                                #if len(myopr.getAlternativeResources()) > 1: 
                                    #print("Opr",myopr.getName(),"has alternative resources: ",len(myopr.getAlternativeResources())-1)
                                oprsequence.append(myopr)
                    else:
                        myopr = Operation("UnknownOperation",self.getOperationsManager().giveProcessID(),0,None) #name,myid,proctime
                        oprsequence.append(myopr)

                
                

                prodorder.getFinalProduct().getOperationSequences()[r['ID']] = oprsequence

                #print("Product ", prodorder.getFinalProduct().getName()," has ",len(oprsequence),"Operations")

                #print(" Alt res: ",[op.getName()+" @"+str(alt.getMachineCode()) for op in oprsequence for alt in op.getAlternativeResources() ])

        return

    def ShowOrderProgress(self):

        item_process_df = pd.read_csv("ProcessData.csv")


        demand_process_df =item_process_df.groupby(["ResourceID",'Resource','Start','Completion'])[['ItemID','Demand','Product']].agg(lambda x:list(x)).reset_index()

        for res in demand_process_df["ResourceID"].unique():
            sub_df = demand_process_df[demand_process_df["ResourceID"] == res]
            sub_df['Start'] = pd.to_datetime(sub_df['Start'])
            sub_df = sub_df.sort_values(by ="Start")
            
            display(sub_df.head(25))

        
