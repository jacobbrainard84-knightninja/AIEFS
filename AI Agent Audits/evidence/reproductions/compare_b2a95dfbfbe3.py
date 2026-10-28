"""Reproduction check (2026-10-28): does run b2a95dfbfbe3, stored inside
'workspace-019ff425-d36a-7d5d-bfa7-8e81a82fa8f2.zip' (in the 'Project Histories' folder) at
runs/frozen_production_20260806/b2a95dfbfbe3/, reproduce the official run runs/5a9f093a2fe0?

Run from the AIEFS repo root (needs numpy and pandas):
    python "AI Agent Audits/evidence/reproductions/compare_b2a95dfbfbe3.py"
The zip is read in memory; nothing is extracted, so nothing in the repo can be overwritten.
Prints a JSON summary (the committed log is compare_b2a95dfbfbe3.log). Exit 0 if the runs agree to
TOL in every float field and exactly in every non-float field; exit 1 otherwise.
Platform strings are not printed (the official run's names the owner's device); only numpy and python versions."""
import hashlib, io, json, sys, zipfile, difflib, warnings
from pathlib import Path
import numpy as np, pandas as pd

TOL = 1e-12
LABELS = {"config_hash"}   # run-identity labels: expected to differ (the source hash feeds the config hash)
warnings.simplefilter("ignore", RuntimeWarning)   # all-NaN fields: NaN patterns are compared separately
ZIP = Path("Project Histories", "workspace-019ff425-d36a-7d5d-bfa7-8e81a82fa8f2.zip")
ZRUN = "runs/frozen_production_20260806/b2a95dfbfbe3/"
RRUN = Path("runs/5a9f093a2fe0")
SRC_NEW, SRC_OLD = Path("AIEF_1_4_memory_ablation_updated.py"), Path("Older files/AIEF_1_4_memory_ablation_updated.py")
if not ZIP.is_file() or not RRUN.is_dir(): sys.exit("run from the AIEFS repo root")
sha = lambda b: hashlib.sha256(b).hexdigest()
zb = ZIP.read_bytes(); z = zipfile.ZipFile(io.BytesIO(zb))
names = [n for n in z.namelist() if n.startswith(ZRUN) and not n.endswith("/")]
zread = lambda rel: z.read(ZRUN + rel)
out = {"zip_folder": ZIP.parent.name, "zip_file": ZIP.name, "zip_sha256": sha(zb), "zip_run_dir": ZRUN, "zip_run_files": len(names), "official_run": str(RRUN)}

mz = json.loads(zread("manifest.json")); mr = json.loads((RRUN / "manifest.json").read_text())
out["model_equal"] = mz["model"] == mr["model"]
out["protocol_equal"] = mz["protocol"] == mr["protocol"]
out["randomization_equal"] = mz.get("randomization") == mr.get("randomization")
out["schema_equal"] = mz.get("schema") == mr.get("schema")
out["manifest_keys_differing"] = sorted(k for k in set(mz) | set(mr) if mz.get(k) != mr.get(k))
out["env_rerun"] = {k: v for k, v in mz.get("environment", {}).items() if k != "platform"}
out["env_official"] = {k: v for k, v in mr.get("environment", {}).items() if k != "platform"}
out["source_sha256_rerun"] = mz.get("source_sha256"); out["source_sha256_official"] = mr.get("source_sha256")

# Source files: which tracked file each run used, and what differs between them.
hn, ho = sha(SRC_NEW.read_bytes()), sha(SRC_OLD.read_bytes())
out["source_files"] = {str(SRC_NEW): hn, str(SRC_OLD): ho}
a, b = SRC_OLD.read_text().splitlines(), SRC_NEW.read_text().splitlines()
changed = [l for l in difflib.unified_diff(a, b, lineterm="", n=0) if l[:1] in "+-" and not l.startswith(("+++", "---"))]
code = [l for l in changed if l[1:].strip() and not l[1:].strip().startswith("#")]
out["source_diff_changed_lines"] = len(changed)
out["source_diff_blank_or_comment_lines"] = len(changed) - len(code)
out["source_diff_code_lines"] = code   # expected: one tuple-unpacking rewrite of a 3-value return

def cmp_arrays(x, y):
    if x.shape != y.shape: return "shape"
    if x.dtype.kind in "fc":
        if not np.array_equal(np.isnan(x), np.isnan(y)): return "NaN pattern differs"
        d = np.abs(x - y)[~np.isnan(x)] if x.size else np.zeros(0)
        return float(d.max()) if d.size else 0.0
    return 0.0 if np.array_equal(x, y) else "DIFF"

seeds = sorted(n[len(ZRUN):] for n in names if n[len(ZRUN):].startswith("seed_") and n.endswith(".npz"))
labels = {}; worst = 0.0; problems = []; nonzero = 0; byte_identical = 0; nfields = 0
for f in seeds:
    zbytes = zread(f); rbytes = (RRUN / f).read_bytes(); byte_identical += zbytes == rbytes
    A = np.load(io.BytesIO(zbytes), allow_pickle=False); B = np.load(io.BytesIO(rbytes), allow_pickle=False)
    if set(A.files) != set(B.files): problems.append(f"{f}: field sets differ")
    for k in sorted(set(A.files) & set(B.files)):
        if k in LABELS:
            labels.setdefault(k, set()).add((str(A[k]), str(B[k]))); continue
        nfields += 1; d = cmp_arrays(A[k], B[k])
        if isinstance(d, str): problems.append(f"{f}:{k}: {d}"); continue
        worst = max(worst, d); nonzero += d > 0
out.update(seed_files_rerun=len(seeds), seed_files_official=len(list(RRUN.glob("seed_*.npz"))),
           seed_fields_compared=nfields, seed_fields_nonzero_diff=nonzero, seed_files_byte_identical=byte_identical,
           seed_worst_abs_diff=worst,
           seed_label_fields_rerun_vs_official={k: sorted(v) for k, v in labels.items()})

cz = pd.read_csv(io.BytesIO(zread("AIEF_1_4_b2a95dfbfbe3_scalar_summary.csv")))
cr = pd.read_csv(RRUN / "AIEF_1_4_5a9f093a2fe0_scalar_summary.csv")
out["csv_shape"] = [list(cz.shape), list(cr.shape)]
if list(cz.columns) == list(cr.columns) and cz.shape == cr.shape:
    num = cz.select_dtypes("number").columns
    out["csv_worst_abs_diff"] = float((cz[num] - cr[num]).abs().max().max())
    out["csv_nonnumeric_equal"] = all((cz[c].astype(str) == cr[c].astype(str)).all() for c in cz.columns if c not in num)
else: problems.append("scalar summary CSV columns/shape differ")

BZ = np.load(io.BytesIO(zread("AIEF_1_4_b2a95dfbfbe3_branch_diagnostics.npz")), allow_pickle=False)
BR = np.load(RRUN / "AIEF_1_4_5a9f093a2fe0_branch_diagnostics.npz", allow_pickle=False)
if set(BZ.files) != set(BR.files): problems.append("branch diagnostics field sets differ")
bw = 0.0
for k in sorted(set(BZ.files) & set(BR.files)):
    d = cmp_arrays(BZ[k], BR[k])
    if isinstance(d, str): problems.append(f"branch_diagnostics:{k}: {d}")
    else: bw = max(bw, d)
out["branch_diag_fields"] = len(set(BZ.files) & set(BR.files)); out["branch_diag_worst_abs_diff"] = bw

stub = json.loads(z.read("runs/5a9f093a2fe0/manifest.json"))
out["zip_also_contains_stub_runs_5a9f093a2fe0_manifest"] = True
out["zip_stub_model_matches_official"] = stub.get("model") == mr["model"]

ok = (not problems and out["model_equal"] and out["protocol_equal"] and out["randomization_equal"]
      and len(seeds) == out["seed_files_official"] == 40 and max(worst, out.get("csv_worst_abs_diff", 1.0), bw) <= TOL)
out["problems"] = problems; out["tolerance"] = TOL; out["verdict"] = "REPRODUCED" if ok else "NOT REPRODUCED"
print(json.dumps(out, indent=1, default=str))
sys.exit(0 if ok else 1)
