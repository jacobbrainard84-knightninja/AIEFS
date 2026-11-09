#!/usr/bin/env python3
"""Read-only preflight for the exact, genuine AIEFS S01 v4.1 bundle.

This checks byte pins, cohort counts and archive readability only. It does NOT
run original validate_run(), run_analysis(), CLI or oracle certification.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, stat, sys
from pathlib import Path

BASE = Path("runs/b57562a8ee77")
EXPECTED = {
 "manifest.json":"7d1b86ab39eed397e2d281faf729ee5c3ac515efc00b2789c2e0013dce0d1e78",
 "AIEF_1_4_Twindow_sensitivity_b57562a8ee77_branch_diagnostics.npz":"55a419c790d0a46bad2a52488d9de018a539ad3daa3759eee849cebf4df468c2",
 "AIEF_1_4_Twindow_sensitivity_b57562a8ee77_scalar_summary.csv":"e9aa74e68b758b21e64b5757607af3c4bf98e88f616757319cb9e4e6d3a8e378",
 "baseline_equivalence_by_seed.json":"47b1627a20be52ee4cf3ad69feeae3fe8d8e008687912c83c2237dfa8e5363ff",
 "baseline_equivalence_certificate.json":"08314de365196fa369bfa2b0363352cf04bdfb1a957f3ed86847f5d17b9d620f",
 "twindow_condition_status.csv":"1f6985026c292c15b5fa5cacacbe92600916ab8d43bdbc8df4f9f0a76baa98e8",
}
RHOS=[0.5,0.75,1.0,1.5,2.0]
BRANCHES=["continue","reset_ema","reset_B","future_shuffle"]

def fail(msg):
 print("FAIL: "+msg,file=sys.stderr); return 1

def digest(path):
 h=hashlib.sha256()
 with path.open("rb") as f:
  for block in iter(lambda:f.read(1<<20),b""): h.update(block)
 return h.hexdigest()

def safe(root, name):
 cur=root
 parts=(BASE/name).parts
 try:
  for part in parts[:-1]:
   cur=cur/part; st=cur.lstat()
   if stat.S_ISLNK(st.st_mode) or not stat.S_ISDIR(st.st_mode):
    return None,"unsafe path component: "+str(cur)
  path=cur/parts[-1]; st=path.lstat()
 except FileNotFoundError: return None,"missing: "+str(BASE/name)
 except OSError as e: return None,"stat error: "+str(e)
 if stat.S_ISLNK(st.st_mode) or not stat.S_ISREG(st.st_mode):
  return None,"not a regular non-symlink file: "+str(BASE/name)
 return path,None

def read_csv(path):
 with path.open("r",encoding="utf-8",newline="") as f: return list(csv.DictReader(f))

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument("--repo-root",type=Path,default=Path.cwd())
 arg=ap.parse_args().repo_root
 if arg.is_symlink() or not arg.is_dir(): return fail("repo root is not a real directory")
 root=arg.resolve(); files={}; errors=[]
 for name,expected in EXPECTED.items():
  path,error=safe(root,name)
  if error: errors.append(error); continue
  observed=digest(path)
  if observed!=expected: errors.append(f"SHA mismatch {name}: expected={expected} observed={observed}")
  else: print(f"HASH_OK {name} {observed}"); files[name]=path
 if errors:
  for e in errors: print("INPUT_ERROR: "+e,file=sys.stderr)
  return 1
 try: manifest=json.loads(files["manifest.json"].read_text(encoding="utf-8"))
 except (OSError,UnicodeError,json.JSONDecodeError) as e: return fail(f"manifest invalid: {e}")
 if manifest.get("study_name")!="AIEF_1_4_Twindow_sensitivity" or manifest.get("config_hash")!="b57562a8ee77":
  return fail("unexpected study identity")
 seeds=[str(x) for x in manifest.get("randomization",{}).get("paired_seeds",[])]
 rhos=[float(x) for x in manifest.get("study",{}).get("rho_values",[])]
 branches=manifest.get("protocol",{}).get("branches",[])
 if len(seeds)!=40 or len(set(seeds))!=40 or rhos!=RHOS or branches!=BRANCHES:
  return fail("seed/rho/branch design mismatch")
 keys={"branch_npz":"AIEF_1_4_Twindow_sensitivity_b57562a8ee77_branch_diagnostics.npz",
 "scalar_csv":"AIEF_1_4_Twindow_sensitivity_b57562a8ee77_scalar_summary.csv",
 "baseline_seed_results":"baseline_equivalence_by_seed.json",
 "baseline_certificate":"baseline_equivalence_certificate.json",
 "condition_status_csv":"twindow_condition_status.csv"}
 for key,name in keys.items():
  if manifest.get("output_hashes",{}).get(key)!=EXPECTED[name]: return fail("manifest child pin mismatch: "+key)
 try:
  json.loads(files["baseline_equivalence_by_seed.json"].read_text(encoding="utf-8"))
  cert=json.loads(files["baseline_equivalence_certificate.json"].read_text(encoding="utf-8"))
 except (OSError,UnicodeError,json.JSONDecodeError) as e: return fail(f"baseline JSON invalid: {e}")
 if cert.get("status")!="passed" or cert.get("n_seeds")!=40: return fail("baseline certificate status/seed-count mismatch")
 scalar=read_csv(files["AIEF_1_4_Twindow_sensitivity_b57562a8ee77_scalar_summary.csv"])
 status=read_csv(files["twindow_condition_status.csv"])
 if len(scalar)!=800 or len(status)!=200: return fail(f"CSV row counts scalar={len(scalar)} status={len(status)}")
 need={"seed","rho","branch","T_window","D_B_final"}
 if not scalar or not need.issubset(scalar[0]): return fail("scalar CSV required columns absent")
 expected={(s,r,b) for s in seeds for r in rhos for b in branches}
 observed={(r["seed"],float(r["rho"]),r["branch"]) for r in scalar}
 if len(observed)!=800 or observed!=expected: return fail("scalar coverage mismatch")
 counts={b:sum(r["branch"]==b for r in scalar) for b in branches}
 if set(counts.values())!={200}: return fail("scalar branch counts mismatch")
 st_expected={(s,r) for s in seeds for r in rhos}
 st_observed={(r["seed"],float(r["rho"])) for r in status}
 if len(st_observed)!=200 or st_observed!=st_expected or {r["status"] for r in status}!={"success"}:
  return fail("condition-status coverage/status mismatch")
 print(f"CSV_OK scalar=800 {counts}; status=200 success")
 try:
  import numpy as np
  with np.load(files["AIEF_1_4_Twindow_sensitivity_b57562a8ee77_branch_diagnostics.npz"],allow_pickle=False) as archive:
   if not archive.files or len(archive.files)!=len(set(archive.files)): return fail("empty/duplicate NPZ keys")
   for key in archive.files:
    if archive[key].dtype.hasobject: return fail("object dtype rejected: "+key)
   print(f"NPZ_OK keys={len(archive.files)} pickle_disabled")
 except ImportError: return fail("NumPy required")
 except Exception as e: return fail(f"NPZ invalid: {type(e).__name__}: {e}")
 print("PREFLIGHT=PASS")
 print("ORIGINAL_V41_VALIDATE_RUN=NOT_RUN")
 print("ORACLE_CERTIFICATION=NOT_ESTABLISHED")
 return 0

if __name__=="__main__": raise SystemExit(main())
