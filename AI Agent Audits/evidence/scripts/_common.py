"""Shared helpers. All scripts must be run from the AIEFS repo root, e.g.
    python "AI Agent Audits/evidence/scripts/<script>.py"
Repo-relative inputs are read from the current working directory.
Outputs go to <bundle>/results, unless AIEF_AUDIT_OUT is set (run_all.sh sets it to a temp dir and then diffs).
Every JSON dict written through dump() gets a _meta block: schema version, script name, status, warnings (no timestamp, so outputs stay byte-deterministic).
"""
import os, sys, json, time
from pathlib import Path
REPO = Path.cwd()
if not (REPO / "AIEF_1_3_falsification_updated.py").exists():
    sys.exit("run from the AIEFS repo root (AIEF_1_3_falsification_updated.py not found in cwd)")
sys.path.insert(0, str(REPO))
BUNDLE = Path(__file__).resolve().parent.parent
OUT = Path(os.environ["AIEF_AUDIT_OUT"]) if os.environ.get("AIEF_AUDIT_OUT") else BUNDLE / "results"
OUT.mkdir(parents=True, exist_ok=True)
SCHEMA = "aiefs-audit-result/1"
def dump(name, obj, status="ok", warnings=None, indent=1):
    """status: 'ok' | 'ok_with_warnings' | 'failed'. warnings: list of strings (e.g. undefined correlations)."""
    if isinstance(obj, dict):
        obj = dict(_meta=dict(schema=SCHEMA, script=os.path.basename(sys.argv[0]), status=status,
                              warnings=list(warnings or [])), **obj)
    p = OUT / name
    with open(p, "w") as fh: json.dump(obj, fh, indent=indent, default=float)
    return p
def inp(name):
    """Input produced by an earlier step: prefer OUT (fresh run), fall back to the committed results/."""
    p = OUT / name
    return p if p.exists() else BUNDLE / "results" / name
