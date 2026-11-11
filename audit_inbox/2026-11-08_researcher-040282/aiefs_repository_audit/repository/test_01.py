df -h "/home/deck/AI_Programs/SSRH/"
python3
import json
import platform
import sys
import numpy as np
import pandas as pd
print("Current environment")
print("Python:", sys.version)
print("NumPy: ", np.__version__)
print("pandas:", pd.__version__)
print("OS: ", platform.platform())
with open(
    "runs/5a9f093a2fe0/manifest.json",
    encoding="utf-8",
) as handle:
    frozen = json.load(handle)
print("\nFrozen environment")
print(json.dumps(frozen.get("environment", {}), indent=2))

