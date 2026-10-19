import json
import numpy as np
import pandas as pd

path = (
    "aief_1_4_biorthogonal_triangular_closure/"
    "biorthogonal_coordinate_summary.csv"
)

df = pd.read_csv(path)

u_exact = np.sqrt(3.0) / 2.0 * np.array([1.0, 0.0, -1.0])
v_exact = np.array([1.0, -1.0, -1.0]) / np.sqrt(3.0)

for _, row in df.iterrows():
    if not str(row["coordinate"]).startswith("left_"):
        continue

    u_start = np.asarray(json.loads(row["u_start_json"]), dtype=float)
    u_end = np.asarray(json.loads(row["u_end_json"]), dtype=float)

    for label, u in (("start", u_start), ("end", u_end)):
        # Both vectors are already normalized by u^T v = 1.
        difference = np.linalg.norm(u - u_exact)
        alignment = abs(
            np.dot(u, u_exact)
            / (np.linalg.norm(u) * np.linalg.norm(u_exact))
        )
        angle = np.degrees(np.arccos(np.clip(alignment, -1.0, 1.0)))

        print(
            row["coordinate"],
            label,
            "u =", u,
            "difference =", difference,
            "angle_deg =", angle,
            "pairing =", np.dot(u, v_exact),
        )
