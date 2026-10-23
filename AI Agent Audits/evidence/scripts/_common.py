"""Shared helpers. All scripts must be run from the AIEFS repo root, e.g.
    cd AIEFS && python <bundle>/scripts/<script>.py
Repo-relative inputs are read from the current working directory; outputs go to <bundle>/results.
"""
import os, sys, json, hashlib
from pathlib import Path
REPO = Path.cwd()
if not (REPO / "AIEF_1_3_falsification_updated.py").exists():
    sys.exit("run from the AIEFS repo root (AIEF_1_3_falsification_updated.py not found in cwd)")
sys.path.insert(0, str(REPO))
BUNDLE = Path(__file__).resolve().parent.parent
OUT = BUNDLE / "results"; OUT.mkdir(exist_ok=True)
def dump(name, obj):
    p = OUT / name
    with open(p, "w") as fh: json.dump(obj, fh, indent=1, default=float)
    return p
