#!/usr/bin/env python3
"""Compare the zip's re-run 'frozen_production_20260806/b2a95dfbfbe3' (workspace-019ff425) with the
repo's authoritative run runs/5a9f093a2fe0: model params, per-seed npz arrays, scalar summary CSV.
Also compare the zip's runs/5a9f093a2fe0 stub against the repo's. Output: results/compare_runs.json"""
import json, os, numpy as np, pandas as pd, hashlib
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Z=os.path.join(ROOT,"scratch/zips/workspace-019ff425-d36a-7d5d-bfa7-8e81a82fa8f2")
R=os.path.join(ROOT,"repo")
zr=os.path.join(Z,"runs/frozen_production_20260806/b2a95dfbfbe3"); rr=os.path.join(R,"runs/5a9f093a2fe0")
mz=json.load(open(os.path.join(zr,"manifest.json"))); mr=json.load(open(os.path.join(rr,"manifest.json")))
out={"model_equal":mz["model"]==mr["model"],"protocol_equal":mz["protocol"]==mr["protocol"],
     "env_zip":mz.get("environment"),"env_repo_platform_redacted":{k:v for k,v in mr.get("environment",{}).items() if k!="platform"},
     "top_keys_only_zip":sorted(set(mz)-set(mr)),"top_keys_only_repo":sorted(set(mr)-set(mz))}
out["randomization_equal"]=mz.get("randomization")==mr.get("randomization")
seeds=[f for f in os.listdir(zr) if f.startswith("seed_")]
per=[]; worst=0.0; nbytes_eq=0
for f in sorted(seeds):
    a=np.load(os.path.join(zr,f),allow_pickle=False); b=np.load(os.path.join(rr,f),allow_pickle=False)
    keys=sorted(set(a.files)|set(b.files)); d={}
    for k in keys:
        if k not in a.files or k not in b.files: d[k]="missing_in_"+("zip" if k not in a.files else "repo"); continue
        x,y=a[k],b[k]
        if x.shape!=y.shape: d[k]=f"shape {x.shape} vs {y.shape}"; continue
        if x.dtype.kind in "fc":
            m=float(np.nanmax(np.abs(x-y))) if x.size else 0.0; d[k]=m; worst=max(worst,m)
        else: d[k]="equal" if np.array_equal(x,y) else "DIFF"
    if hashlib.sha256(open(os.path.join(zr,f),"rb").read()).digest()==hashlib.sha256(open(os.path.join(rr,f),"rb").read()).digest(): nbytes_eq+=1
    per.append({"seed_file":f,"max_abs_diff":d})
out["n_seed_files"]=len(seeds); out["n_byte_identical"]=nbytes_eq; out["worst_float_abs_diff"]=worst
out["per_seed_sample"]=per[:3]
nonzero=[(p["seed_file"],k,v) for p in per for k,v in p["max_abs_diff"].items() if (isinstance(v,float) and v>0) or (isinstance(v,str) and v!="equal")]
out["n_nonzero_or_nonequal_fields"]=len(nonzero); out["nonzero_examples"]=nonzero[:15]
# scalar summary
cz=pd.read_csv(os.path.join(zr,"AIEF_1_4_b2a95dfbfbe3_scalar_summary.csv")); cr=pd.read_csv(os.path.join(rr,"AIEF_1_4_5a9f093a2fe0_scalar_summary.csv"))
out["csv_shapes"]=[list(cz.shape),list(cr.shape)]; out["csv_cols_equal"]=list(cz.columns)==list(cr.columns)
if list(cz.columns)==list(cr.columns) and cz.shape==cr.shape:
    num=cz.select_dtypes("number").columns
    diff=(cz[num]-cr[num]).abs().max()
    out["csv_max_abs_diff_by_col_top"]=diff.sort_values(ascending=False).head(8).to_dict()
    nn=[c for c in cz.columns if c not in num]; out["csv_nonnumeric_equal"]={c:bool((cz[c].astype(str)==cr[c].astype(str)).all()) for c in nn}
# branch diagnostics
bz=np.load(os.path.join(zr,"AIEF_1_4_b2a95dfbfbe3_branch_diagnostics.npz")); br=np.load(os.path.join(rr,"AIEF_1_4_5a9f093a2fe0_branch_diagnostics.npz"))
bd={}
for k in sorted(set(bz.files)&set(br.files)):
    x,y=bz[k],br[k]
    if x.shape!=y.shape: bd[k]="shape"; continue
    bd[k]=float(np.nanmax(np.abs(x-y))) if x.dtype.kind in "fc" and x.size else ("equal" if np.array_equal(x,y) else "DIFF")
out["branch_diag_only_zip"]=sorted(set(bz.files)-set(br.files)); out["branch_diag_only_repo"]=sorted(set(br.files)-set(bz.files))
out["branch_diag_maxdiff_nonzero"]={k:v for k,v in bd.items() if v not in (0.0,"equal")}
out["branch_diag_n_keys"]=len(bd)
# stub
zs=json.load(open(os.path.join(Z,"runs/5a9f093a2fe0/manifest.json")))
out["zip_5a9f093a2fe0_stub_model"]=zs["model"]; out["zip_stub_matches_repo_model"]=zs["model"]==mr["model"]
os.makedirs(os.path.join(ROOT,"results"),exist_ok=True)
json.dump(out,open(os.path.join(ROOT,"results/compare_runs.json"),"w"),indent=1,default=str)
print(json.dumps({k:v for k,v in out.items() if k!="per_seed_sample"},indent=1,default=str)[:5000])
