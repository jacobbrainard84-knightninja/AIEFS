import pandas as pd

path = (
    "aief_1_4_exceptional_K3_transition/"
    "exceptional_K3_node_trajectory.csv"
)

df = pd.read_csv(path)

dt = 0.01
df["proposal_excess"] = (
    df["row_sum"]
    + dt * df["row_direction_d"]
    - df["capacity"]
)
df["proposal_violating"] = df["proposal_excess"] > 0.0
df["projection_ratio"] = (
    dt * df["row_direction_d"]
    / df["slack"].clip(lower=1e-300)
)
df["critical_dt"] = (
    df["slack"]
    / df["row_direction_d"].where(df["row_direction_d"] > 0.0)
)

for node, group in df.groupby("node"):
    violating = group.loc[group["proposal_violating"]]
    first = violating.iloc[0] if len(violating) else None

    print(f"\nnode {node}")
    if first is None:
        print("  never proposal-violating")
    else:
        print(f"  first proposal-violating step: {int(first['step'])}")
        print(f"  state time: {first['state_elapsed_time']}")
        print(f"  slack: {first['slack']}")
        print(f"  proposal excess: {first['proposal_excess']}")
        print(f"  projection ratio: {first['projection_ratio']}")
