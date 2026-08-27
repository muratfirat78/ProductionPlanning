from datetime import datetime, timedelta

import pandas as pd


COMMON_SCHEDULE_COLUMNS = [
    "ID",
    "Product",
    "Operation",
    "Resource",
    "Start",
    "End",
]


def write_milp_schedule(MILP_schedule, output_file="MILP_Schedule.csv"):
    """Write MILP schedules using the common schedule format."""
    rows = []
    for _, row in MILP_schedule.iterrows():
        rows.append({
                "ID": row["ID"],
                "Product": row["Product"],
                "Operation": row["Work Orders/Operation"],
                "Resource": row["Processing Machine"],
                "Start": row["Work Orders/Start"],
                "End": row["Work Orders/End"],
            })

    pd.DataFrame(rows, columns=COMMON_SCHEDULE_COLUMNS).to_csv(output_file, index=False)


def write_simulation_schedule(execution_data, output_file="Simulation_Schedule.csv"):
    """Write completed simulation processing events using the common format."""
    rows = []
    for _, event in execution_data.iterrows():
        progress_steps = str(event["ProgressSteps"])
        first_step = progress_steps.split("~", 1)[0]

        start = first_step.split("-", 1)[0] if first_step else ""

        end_realtime = datetime.strptime(event["Date"],"%Y-%m-%d %H:%M:%S")
        start__realtime = end_realtime - timedelta(minutes=float(event["SimTime"]) - float(start))
        start_realtime = start__realtime.strftime("%Y-%m-%d %H:%M:%S")

        rows.append({
            "ID": event["ID"],
            "Product": event["Product"],
            "Operation": event["Work Orders/Operation"],
            "Resource": event["Resource"],
            "Start": start_realtime,
            "End": event["Date"],
        })

    pd.DataFrame(
        rows,
        columns=COMMON_SCHEDULE_COLUMNS
    ).to_csv(output_file, index=False)