import pandas as pd
import numpy as np

path = (
    "aief_1_4_proposal_equalization_bridge/"
    "proposal_equalization_trajectory.csv"
)
df = pd.read_csv(path)

for pair, g in df.groupby("pair", sort=False):
    print("\n", pair)
    for col in ["delta_x", "delta_R"]:
        x = g[col].to_numpy(float)
        changes = np.sum(np.signbit(x[1:]) != np.signbit(x[:-1]))
        print(
            col,
            "min=", np.min(x),
            "max=", np.max(x),
            "final=", x[-1],
            "sign_changes=", changes,
            "all_positive=", bool(np.all(x > 0)),
        )
