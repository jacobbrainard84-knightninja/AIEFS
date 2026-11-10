import hashlib, importlib.util, json, shutil, sys, tempfile
from pathlib import Path
REPO = Path("/workspace/wt_p1_neg")
SRC = REPO/"AIEF_Experiments/aief_modular_platform_v1_analysis_v4/AIEF_1_4_Twindow_sensitivity_analysis_v4_1.py"
spec = importlib.util.spec_from_file_location("v41", SRC); m = importlib.util.module_from_spec(spec)
sys.modules["v41"] = m; spec.loader.exec_module(m)
RUN = REPO/"runs/b57562a8ee77"
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
def attempt(name, d):
    try:
        v = m.validate_run(m.discover_inputs(d)); print(f"{name}: ACCEPTED seeds={len(v.seeds)} rows={len(v.scalar)}")
    except Exception as e: print(f"{name}: REJECTED {type(e).__name__}: {str(e)[:110]}")
def copy():
    d = Path(tempfile.mkdtemp(dir="/tmp/p1"))/"run"
    shutil.copytree(RUN, d, ignore=shutil.ignore_patterns("condition_seed_*", "analysis")); return d
print("source sha256", sha(SRC)); print("real manifest sha256", sha(RUN/"manifest.json"))
attempt("POS real S01", RUN)
csv = lambda d: next(d.glob("*_scalar_summary.csv"))
# N1: edit one scalar outcome, no re-pin
d = copy(); p = csv(d); lines = p.read_text().splitlines(); hdr = lines[0].split(",")
col = hdr.index("D_B_final"); r = lines[1].split(","); r[col] = "0.123456"; lines[1] = ",".join(r)
p.write_text("\n".join(lines)+"\n"); attempt("N1 edit scalar, manifest untouched", d)
# N2: same edit, re-pin in manifest
man = json.loads((d/"manifest.json").read_text()); man["output_hashes"]["scalar_csv"] = sha(p)
(d/"manifest.json").write_text(json.dumps(man, indent=2)); attempt("N2 edit scalar + re-pin manifest", d)
print("   forged manifest sha256 == ART-2217 pin?", sha(d/"manifest.json") == "7d1b86ab39eed397e2d281faf729ee5c3ac515efc00b2789c2e0013dce0d1e78")
# N3: replace the certificate with a 2-field stub and re-pin
d = copy(); (d/"baseline_equivalence_certificate.json").write_text('{"status":"passed","n_seeds":40}')
man = json.loads((d/"manifest.json").read_text()); man["output_hashes"]["baseline_certificate"] = sha(d/"baseline_equivalence_certificate.json")
(d/"manifest.json").write_text(json.dumps(man, indent=2)); attempt("N3 stub certificate + re-pin", d)
# N4: rename all 40 seeds consistently across manifest, scalar CSV, status CSV; re-pin
d = copy(); man = json.loads((d/"manifest.json").read_text()); seeds = [str(s) for s in man["randomization"]["paired_seeds"]]
mp = {s: f"9{i:018d}" for i, s in enumerate(seeds)}
man["randomization"]["paired_seeds"] = [mp[s] for s in seeds]
import pandas as pd
f = pd.read_csv(csv(d), dtype={"seed": str, "branch": str}); f["seed"] = f["seed"].map(mp); f.to_csv(csv(d), index=False)
st = pd.read_csv(d/"twindow_condition_status.csv", dtype={"seed": str}); st["seed"] = st["seed"].map(mp); st.to_csv(d/"twindow_condition_status.csv", index=False)
for lab, fn in (("scalar_csv", csv(d)), ("condition_status_csv", d/"twindow_condition_status.csv")): man["output_hashes"][lab] = sha(fn)
(d/"manifest.json").write_text(json.dumps(man, indent=2)); attempt("N4 foreign 40-seed cohort + re-pin", d)
