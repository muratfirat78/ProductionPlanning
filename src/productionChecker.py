from simulator import *
from productionmain import *
from productionalgs import *


class productionFeasibilityChecker(FeasibilityChecker):
    def __init__(self,Simulator,ShopFloorMgr):
        super().__init__(Simulator,ShopFloorMgr)

    
    def CheckFeasibility(self):

        process_df = self.getOperationsManager().getProcessDF()
        location_df = self.getOperationsManager().getLocationDF()
             
        # Check for every item:
        #            if the processes are completed in proces data, 
        #               start and completion times of operations respect precedence ordering
        #               finally items come back to inventory or not (if simulation times allows.

        for itemID in process_df["ItemID"].unique():
            processData = process_df[process_df["ItemID"] == itemID]
            processViolations = dict()

            for i in range(len(processData)):
                completion_i = processData.iloc[i]["Completion"]
                start_next = None
                if i + 1 < len(processData):
                    start_next = processData.iloc[i + 1]["Start"]
            
                # -----------------------------
                # 1. Missing completion time
                # -----------------------------
                if pd.isna(completion_i):
                    processViolations.setdefault(itemID, []).append({
                        "row": i,
                        "issue": "missing_completion",
                        "message": f"Row {i} has no completion time"
                    })
                    # Skip precedence check because completion is missing
                    continue
            
                # ---------------------------
                # 2. Precedence violation
                # ---------------------------
                if start_next is not None and completion_i > start_next:
                    processViolations.setdefault(itemID, []).append({
                        "row": i,
                        "issue": "precedence_violation",
                        "completion": completion_i,
                        "next_start": start_next,
                        "message": f"Completion of row {i} is later than start of row {i+1}"})
    
            # --------------------------------------
            # 3. Check arrival back to inventory
            # --------------------------------------
            itemLocation_df = location_df[(location_df["Entity"] == "Item") & (location_df["EntityID"] == itemID)]
    
            if itemLocation_df.empty:
                print("No rows found for this Item/ItemID")
            else:
                last_row = itemLocation_df.iloc[-1]
            
                if last_row["LocationID"] == 2:
                    print(f"Item {itemID} has arrived back at the inventory buffer")
                else:
                    print(f"Item {itemID} has not yet arrived back at the inventory buffer")
    
            if not processViolations:
                print(f"No process violations found for item {itemID}")
    
            else:
                print(f"Violations for item {itemID}:")
                for v in processViolations[itemID]:
                    print(f" - Row {v['row']}: {v['issue']} → {v['message']}")
                              
            
        # Check for every entity:
        #            if the routing is continous.
        #               start and completion times of operations respect precedence ordering
        
        for entityID in location_df["EntityID"].unique():
            entityViolations = dict()
            Entity_data = location_df[location_df["EntityID"] == entityID]
            Entity = Entity_data["Entity"].iloc[0]

            for i in range(len(Entity_data) - 1):
                current_time = Entity_data.iloc[i]["Time"]
                next_time = Entity_data.iloc[i + 1]["Time"]
        
                if current_time >= next_time:
                    entityViolations.setdefault(entityID, []).append({
                        "entity": Entity,
                        "row": i,
                        "current_time": current_time,
                        "next_time": next_time,
                        "message": f"Time at row {i} is not less than time at row {i+1}"
                    })
                    
                if Entity == "Item" and Entity_data.iloc[i]["EventName"] == "Processing Automated":

                    current_loc = Entity_data.iloc[i]["LocationName"]
                
                    required_input_loc = current_loc + "_Input"
                    required_output_loc = current_loc + "_Output"
                
                    # -------------------------
                    # BACKWARD CHECK (i-1, i-2)
                    # -------------------------
                    for offset in [1, 2]:
                        j = i - offset
                
                        if j < 0:
                            entityViolations.setdefault(entityID, []).append({
                                "entity": Entity,
                                "row": i,
                                "offending_row": j,
                                "message": (
                                    f"Row {i-offset} does not exist but must be '{required_input_loc}' "
                                    f"for Processing Automated at row {i}"
                                )
                            })
                            continue
                
                        prev_loc = Entity_data.iloc[j]["LocationName"]
                
                        if prev_loc != required_input_loc:
                            entityViolations.setdefault(entityID, []).append({
                                "entity": Entity,
                                "row": i,
                                "offending_row": j,
                                "current_location": current_loc,
                                "previous_location": prev_loc,
                                "expected_location": required_input_loc,
                                "message": (
                                    f"Row {j} has '{prev_loc}', expected '{required_input_loc}' "
                                    f"for Processing Automated at row {i}"
                                )
                            })
                
                
                    # -------------------------
                    # FORWARD CHECK (i+1, i+2)
                    # -------------------------
                    for offset in [1, 2]:
                        k = i + offset
                
                        if k >= len(Entity_data):
                            entityViolations.setdefault(entityID, []).append({
                                "entity": Entity,
                                "row": i,
                                "offending_row": k,
                                "message": (
                                    f"Row {i+offset} does not exist but must be '{required_output_loc}' "
                                    f"for Processing Automated at row {i}"
                                )
                            })
                            continue
                
                        next_loc = Entity_data.iloc[k]["LocationName"]
                
                        if next_loc != required_output_loc:
                            entityViolations.setdefault(entityID, []).append({
                                "entity": Entity,
                                "row": i,
                                "offending_row": k,
                                "current_location": current_loc,
                                "next_location": next_loc,
                                "expected_location": required_output_loc,
                                "message": (
                                    f"Row {k} has '{next_loc}', expected '{required_output_loc}' "
                                    f"for Processing Automated at row {i}"
                                )
                            })

                if Entity_data.iloc[i]["EventName"] == "Trailer Transport":

                    source, dest = Entity_data.iloc[i]["LocationName"].split("->")
                    expected_prev = source + "_Output"
                    expected_next = dest + "_Input"

                    # -------------------------
                    # CHECK i-1 (must be source_output)
                    # -------------------------
                    j = i - 1
                    if j < 0:
                        entityViolations.setdefault(entityID, []).append({
                            "entity": Entity,
                            "row": i,
                            "message": f"Row {i-1} does not exist but must be '{expected_prev}'"
                        })
                    else:
                        prev_loc = Entity_data.iloc[j]["LocationName"]
                        if (prev_loc != expected_prev) and (prev_loc != "Central_Output"):
                            entityViolations.setdefault(entityID, []).append({
                                "entity": Entity,
                                "row": i,
                                "offending_row": j,
                                "expected": expected_prev,
                                "found": prev_loc,
                                "message": (
                                    f"Trailer transport mismatch: row {j} has '{prev_loc}', "
                                    f"expected '{expected_prev}' before transport at row {i}"
                                )
                            })
                    
                    
                    # -------------------------
                    # CHECK i+1 (must be dest_input)
                    # -------------------------
                    k = i + 1
                    if k >= len(Entity_data):
                        entityViolations.setdefault(entityID, []).append({
                            "entity": Entity,
                            "row": i,
                            "message": f"Row {i+1} does not exist but must be '{expected_next}'"
                        })
                    else:
                        next_loc = Entity_data.iloc[k]["LocationName"]
                        if next_loc != expected_next:
                            entityViolations.setdefault(entityID, []).append({
                                "entity": Entity,
                                "row": i,
                                "offending_row": k,
                                "expected": expected_next,
                                "found": next_loc,
                                "message": (
                                    f"Trailer transport mismatch: row {k} has '{next_loc}', "
                                    f"expected '{expected_next}' after transport at row {i}"
                                )
                            })

            if not entityViolations:
                    print(f"No entity violations found for entity {entityID}")        
            else:
                print(f"Violations for entity {entityID}:")
                for v in entityViolations[entityID]:
                    print(f" - Row {v['row']}: {v['message']}")

        ##Check if there is no overlap for each resource

        resources_dict = {}
        resourceViolations = {}

        for i in range(len(location_df)):
            row = location_df.iloc[i]
        
            resource = row["LocationName"]
            time_key = row["Time"]
        
            resources_dict.setdefault(resource, {})
            resources_dict[resource].setdefault(time_key, [])
        
            resources_dict[resource][time_key].append({
                "EventID": row["EventID"],
                "EventName": row["EventName"],
                "Entity": row["Entity"],
                "EntityID": row["EntityID"],
                "LocationID": row["LocationID"]
            })
            
        for resource, time_map in resources_dict.items():
            for time_key, events in time_map.items():
        
                if len(events) > 1:  # more than one event = overlap
                    resourceViolations.setdefault(resource, []).append({
                        "time": time_key,
                        "events": events,
                        "message": "Overlap detected: multiple events at the same timestamp"
                    })
        if not resourceViolations:
            print("No violations found")
        else:
            print("Violations detected:\n")
        
            for resource, issues in resourceViolations.items():
                print(f"Resource: {resource}")
        
                for v in issues:
                    print(f"  Time: {v['time']}")
                    print("  Events at this time:")
        
                    for e in v["events"]:
                        print(f"    - EventID: {e['EventID']}, EventName: {e['EventName']}, Entity: {e['Entity']}")
        
                    print(f"  Message: {v['message']}\n")
            
        print(" Checker >> "+" Location data size "+str(len(location_df))+", process data size: "+str(len(process_df)))
        

        return True
              
