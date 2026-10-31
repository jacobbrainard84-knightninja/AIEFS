"""Reproduction check (2026-10-28): does run b2a95dfbfbe3, stored inside
'workspace-019ff425-d36a-7d5d-bfa7-8e81a82fa8f2.zip' (in the 'Project Histories' folder) at
runs/frozen_production_20260806/b2a95dfbfbe3/, reproduce the official run runs/5a9f093a2fe0?

v4 of the hash-pinned "AI Agent Audits/evidence/reproductions/compare_b2a95dfbfbe3.py".
v2 added the NaN-mask check to the scalar-summary CSV path (see compare_b2a95dfbfbe3_ERRATUM.md in this folder).
v3 (2026-10-29, review r026) also checks the +inf and -inf masks and takes max abs diffs only over finite cells.
v4 (2026-10-31, red-team fix #1; see compare_b2a95dfbfbe3_v3_to_v4.diff and the ERRATUM's v4 section) gates the
verdict on fields that v3 computed but ignored. Every failed gate adds a named entry to "problems":
  - the CSV's non-numeric columns (branch, branch_family) must be equal cell for cell   [red-team G10]
  - manifest "schema" must be equal                                                    [red-team G11]
  - manifest keys may differ only in EXPECTED_DIFFERING_KEYS (run identity + environment)
  - each manifest's source_sha256 must be the sha256 of the source file that run used
  - the source diff must be exactly EXPECTED_SOURCE_DIFF (one tuple-unpacking rewrite)
  - config_hash labels must be exactly (rerun run id, official run id) in every seed file
  - seed file NAMES must match one to one, and a missing or unreadable file is a named problem, not a crash
  - float fields: worst abs diff <= TOL (as before) AND worst relative diff <= RTOL (new; tighter, never looser)
Not gated, on purpose: zip_stub_model_matches_official. That compares a known-wrong stub inside the zip
(runs/5a9f093a2fe0/manifest.json in the zip; b2a95dfbfbe3_REPRODUCTION.md documents it as the wrong parameters),
not the rerun, and it is false on the genuine data. It stays an informational key.
Run from the AIEFS repo root (needs numpy and pandas):
    python "audits/reproductions/b2a95dfbfbe3/compare_b2a95dfbfbe3_v4.py"
    python "audits/reproductions/b2a95dfbfbe3/compare_b2a95dfbfbe3_v4.py" --selftest   (synthetic checks only)
The zip is read in memory; nothing is extracted, so nothing in the repo can be overwritten.
Prints a JSON summary (the committed log is compare_b2a95dfbfbe3_v4.log in this folder). Exit 0 if every gate
passes (verdict REPRODUCED), 1 otherwise (NOT REPRODUCED), 2 if not run from the repo root.
Platform strings are not printed (the official run's names the owner's device); only numpy and python versions."""
import hashlib, io, json, sys, zipfile, difflib, warnings
from pathlib import Path
import numpy as np, pandas as pd

TOL = 1e-12    # absolute, as in v1-v3
RTOL = 1e-12   # v4: relative, |x-y| / max(|x|,|y|); applied IN ADDITION to TOL, so it can only tighten
LABELS = {"config_hash"}   # run-identity labels: expected to differ (the source hash feeds the config hash)
EXPECTED_DIFFERING_KEYS = {"config_hash", "environment", "source_sha256"}
EXPECTED_SOURCE_DIFF = ["-        R_physical, _, _ = advance_state(", "+        R_physical, *_ = advance_state("]
warnings.simplefilter("ignore", RuntimeWarning)   # all-NaN fields: NaN/inf patterns are compared separately
ZIP = Path("Project Histories", "workspace-019ff425-d36a-7d5d-bfa7-8e81a82fa8f2.zip")
ZRUN = "runs/frozen_production_20260806/b2a95dfbfbe3/"
RRUN = Path("runs/5a9f093a2fe0")
ZID, RID = ZRUN.rstrip("/").rsplit("/", 1)[-1], RRUN.name
SRC_NEW, SRC_OLD = Path("AIEF_1_4_memory_ablation_updated.py"), Path("Older files/AIEF_1_4_memory_ablation_updated.py")
MASKS = (("NaN", np.isnan), ("+inf", np.isposinf), ("-inf", np.isneginf))
N_SEEDS = 40

def mask_mismatches(x, y):
    """{name: number of cells where exactly one side has that non-finite value}; complex: real and imag parts."""
    parts = [(x.real, y.real), (x.imag, y.imag)] if x.dtype.kind == "c" else [(x, y)]
    return {name: int(sum((f(a) != f(b)).sum() for a, b in parts)) for name, f in MASKS}

def diffs(x, y):
    """(worst abs diff, worst relative diff) over cells finite in both; relative = |x-y| / max(|x|,|y|), 0 if equal."""
    both = np.isfinite(x) & np.isfinite(y)
    d = np.abs(x - y)[both] if x.size else np.zeros(0)
    if not d.size: return 0.0, 0.0
    s = np.maximum(np.abs(x), np.abs(y))[both]
    nz = d > 0
    return float(d.max()), float((d[nz] / s[nz]).max()) if nz.any() else 0.0

def cmp_arrays(x, y):
    """str problem, or (worst abs diff, worst rel diff)."""
    if x.shape != y.shape: return "shape"
    if x.dtype.kind in "fc":
        bad = [name for name, n in mask_mismatches(x, y).items() if n]
        if bad: return " and ".join(bad) + " pattern differs"
        return diffs(x, y)
    return (0.0, 0.0) if np.array_equal(x, y) else "DIFF"

if "--selftest" in sys.argv[1:]:
    f = np.array
    assert cmp_arrays(f([1.0, np.nan, np.inf, -np.inf]), f([1.0, np.nan, np.inf, -np.inf])) == (0.0, 0.0)
    assert cmp_arrays(f([np.inf]), f([1.0])) == "+inf pattern differs"
    assert cmp_arrays(f([-np.inf]), f([np.inf])) == "+inf and -inf pattern differs"
    assert cmp_arrays(f([np.nan]), f([-np.inf])) == "NaN and -inf pattern differs"
    assert cmp_arrays(f([complex(1.0, np.inf)]), f([1 + 1j])) == "+inf pattern differs"
    a, r = cmp_arrays(f([1.0, 2.0, np.inf]), f([1.0, 2.5, np.inf])); assert abs(a - 0.5) < 1e-15 and abs(r - 0.2) < 1e-15
    a, r = cmp_arrays(f([1e-20]), f([2e-20])); assert a <= TOL and r > RTOL   # abs-only would pass this; v4 does not
    assert cmp_arrays(f([1, 2]), f([2, 1])) == "DIFF" and cmp_arrays(f([1.0]), f([1.0, 2.0])) == "shape"
    assert mask_mismatches(f([[np.inf, 0.0]]), f([[0.0, np.inf]])) == {"NaN": 0, "+inf": 2, "-inf": 0}
    print("selftest OK"); sys.exit(0)
if not ZIP.is_file() or not RRUN.is_dir(): print("run from the AIEFS repo root", file=sys.stderr); sys.exit(2)
sha = lambda b: hashlib.sha256(b).hexdigest()
zb = ZIP.read_bytes(); z = zipfile.ZipFile(io.BytesIO(zb))
names = [n for n in z.namelist() if n.startswith(ZRUN) and not n.endswith("/")]
zread = lambda rel: z.read(ZRUN + rel)
out = {"comparator": "v4", "zip_folder": ZIP.parent.name, "zip_file": ZIP.name, "zip_sha256": sha(zb), "zip_run_dir": ZRUN,
       "zip_run_files": len(names), "official_run": str(RRUN)}
problems = []

def load_npz(side, f, getbytes):
    """np.load from bytes; a missing or unreadable file is a named problem (v3 crashed with a Traceback)."""
    try:
        return np.load(io.BytesIO(getbytes()), allow_pickle=False)
    except FileNotFoundError:
        problems.append(f"{f}: missing in {side} run")
    except Exception as e:   # truncated / corrupted npz
        problems.append(f"{f}: unreadable in {side} run ({type(e).__name__})")
    return None

# --- manifests -------------------------------------------------------------------------------
mz = json.loads(zread("manifest.json"))
try:
    mr = json.loads((RRUN / "manifest.json").read_text())
except Exception as e:
    mr = {}; problems.append(f"official manifest.json missing or unreadable ({type(e).__name__})")
for key in ("model", "protocol", "randomization", "schema"):
    out[f"{key}_equal"] = mz.get(key) == mr.get(key)
    if not out[f"{key}_equal"]: problems.append(f"manifest: {key} differs")
out["manifest_keys_differing"] = sorted(k for k in set(mz) | set(mr) if mz.get(k) != mr.get(k))
unexpected = sorted(set(out["manifest_keys_differing"]) - EXPECTED_DIFFERING_KEYS)
if unexpected: problems.append(f"manifest: unexpected differing keys {unexpected}")
out["env_rerun"] = {k: v for k, v in mz.get("environment", {}).items() if k != "platform"}
out["env_official"] = {k: v for k, v in mr.get("environment", {}).items() if k != "platform"}
out["source_sha256_rerun"] = mz.get("source_sha256"); out["source_sha256_official"] = mr.get("source_sha256")
for side, m in (("rerun", mz), ("official", mr)):
    if m.get("config_hash") != {"rerun": ZID, "official": RID}[side]:
        problems.append(f"manifest: {side} config_hash {m.get('config_hash')!r} is not the run id {({'rerun': ZID, 'official': RID}[side])!r}")

# --- source files: which tracked file each run used, and what differs between them ------------------
hn, ho = sha(SRC_NEW.read_bytes()), sha(SRC_OLD.read_bytes())
out["source_files"] = {str(SRC_NEW): hn, str(SRC_OLD): ho}
if out["source_sha256_rerun"] != hn: problems.append(f"manifest: rerun source_sha256 is not sha256({SRC_NEW})")
if out["source_sha256_official"] != ho: problems.append(f"manifest: official source_sha256 is not sha256({SRC_OLD})")
a, b = SRC_OLD.read_text().splitlines(), SRC_NEW.read_text().splitlines()
changed = [l for l in difflib.unified_diff(a, b, lineterm="", n=0) if l[:1] in "+-" and not l.startswith(("+++", "---"))]
code = [l for l in changed if l[1:].strip() and not l[1:].strip().startswith("#")]
out["source_diff_changed_lines"] = len(changed)
out["source_diff_blank_or_comment_lines"] = len(changed) - len(code)
out["source_diff_code_lines"] = code
out["source_diff_code_lines_expected"] = code == EXPECTED_SOURCE_DIFF
if code != EXPECTED_SOURCE_DIFF: problems.append(f"source diff: {len(code)} code line(s) differ from the expected one-line rewrite")

# --- seed files --------------------------------------------------------------------------------
seeds = sorted(n[len(ZRUN):] for n in names if n[len(ZRUN):].startswith("seed_") and n.endswith(".npz"))
oseeds = sorted(p.name for p in RRUN.glob("seed_*.npz"))
only_z, only_r = sorted(set(seeds) - set(oseeds)), sorted(set(oseeds) - set(seeds))
if only_z: problems.append(f"seed files missing in official run: {only_z}")
if only_r: problems.append(f"seed files only in official run: {only_r}")
if not len(seeds) == len(oseeds) == N_SEEDS: problems.append(f"seed file count: rerun {len(seeds)}, official {len(oseeds)}, expected {N_SEEDS}")
labels = {}; worst = 0.0; worst_rel = 0.0; nonzero = 0; byte_identical = 0; nfields = 0
for f in seeds:
    if f in only_z: continue
    zbytes = zread(f)
    try: rbytes = (RRUN / f).read_bytes()
    except Exception as e: problems.append(f"{f}: unreadable in official run ({type(e).__name__})"); continue
    byte_identical += zbytes == rbytes
    A = load_npz("rerun", f, lambda: zbytes); B = load_npz("official", f, lambda: rbytes)
    if A is None or B is None: continue
    try:
        if set(A.files) != set(B.files): problems.append(f"{f}: field sets differ")
        for k in sorted(set(A.files) & set(B.files)):
            if k in LABELS:
                pair = (str(A[k]), str(B[k])); labels.setdefault(k, set()).add(pair)
                if pair != (ZID, RID): problems.append(f"{f}:{k}: label {pair} is not ({ZID!r}, {RID!r})")
                continue
            nfields += 1; d = cmp_arrays(A[k], B[k])
            if isinstance(d, str): problems.append(f"{f}:{k}: {d}"); continue
            worst = max(worst, d[0]); worst_rel = max(worst_rel, d[1]); nonzero += d[0] > 0
    except Exception as e:   # a member that fails to decompress or parse
        problems.append(f"{f}: unreadable field ({type(e).__name__})")
out.update(seed_files_rerun=len(seeds), seed_files_official=len(oseeds),
           seed_fields_compared=nfields, seed_fields_nonzero_diff=nonzero, seed_files_byte_identical=byte_identical,
           seed_worst_abs_diff=worst, seed_worst_rel_diff=worst_rel,
           seed_label_fields_rerun_vs_official={k: sorted(v) for k, v in labels.items()})

# --- scalar summary CSV --------------------------------------------------------------------------
cz = pd.read_csv(io.BytesIO(zread(f"AIEF_1_4_{ZID}_scalar_summary.csv")))
try:
    cr = pd.read_csv(RRUN / f"AIEF_1_4_{RID}_scalar_summary.csv")
except Exception as e:
    cr = None; problems.append(f"scalar summary CSV: official file missing or unreadable ({type(e).__name__})")
if cr is not None and list(cz.columns) == list(cr.columns) and cz.shape == cr.shape:
    out["csv_shape"] = [list(cz.shape), list(cr.shape)]
    num = cz.select_dtypes("number").columns
    if list(num) != list(cr.select_dtypes("number").columns): problems.append("scalar summary CSV: numeric column sets differ")
    xz, xr = cz[num].to_numpy(dtype=float), cr[num].to_numpy(dtype=float)
    mm = mask_mismatches(xz, xr)
    out["csv_nan_mask_mismatches"] = mm["NaN"]
    out["csv_posinf_mask_mismatches"] = mm["+inf"]; out["csv_neginf_mask_mismatches"] = mm["-inf"]
    out["csv_nonfinite_cells_rerun"] = {name: int(f(xz).sum()) for name, f in MASKS}
    out["csv_nonfinite_cells_official"] = {name: int(f(xr).sum()) for name, f in MASKS}
    for name, n in mm.items():
        if n: problems.append(f"scalar summary CSV: {name} pattern differs in {n} cells")
    out["csv_worst_abs_diff"], out["csv_worst_rel_diff"] = diffs(xz, xr)
    text = [c for c in cz.columns if c not in num]
    bad = {c: int((cz[c].astype(str) != cr[c].astype(str)).sum()) for c in text}
    out["csv_nonnumeric_columns"] = text
    out["csv_nonnumeric_equal"] = not any(bad.values())
    if not out["csv_nonnumeric_equal"]:
        problems.append("scalar summary CSV: non-numeric columns differ: " + ", ".join(f"{c} ({n} cells)" for c, n in bad.items() if n))
elif cr is not None:
    out["csv_shape"] = [list(cz.shape), list(cr.shape)]; problems.append("scalar summary CSV columns/shape differ")

# --- branch diagnostics --------------------------------------------------------------------------
DIAG = f"AIEF_1_4_{{}}_branch_diagnostics.npz"
BZ = load_npz("rerun", DIAG.format(ZID), lambda: zread(DIAG.format(ZID)))
BR = load_npz("official", DIAG.format(RID), lambda: (RRUN / DIAG.format(RID)).read_bytes())
bw = 0.0; bw_rel = 0.0; nb = 0
if BZ is not None and BR is not None:
    try:
        if set(BZ.files) != set(BR.files): problems.append("branch diagnostics field sets differ")
        for k in sorted(set(BZ.files) & set(BR.files)):
            nb += 1; d = cmp_arrays(BZ[k], BR[k])
            if isinstance(d, str): problems.append(f"branch_diagnostics:{k}: {d}")
            else: bw = max(bw, d[0]); bw_rel = max(bw_rel, d[1])
    except Exception as e:
        problems.append(f"branch diagnostics: unreadable field ({type(e).__name__})")
out["branch_diag_fields"] = nb; out["branch_diag_worst_abs_diff"] = bw; out["branch_diag_worst_rel_diff"] = bw_rel

# --- informational only (see the docstring) -----------------------------------------------------
stub = json.loads(z.read("runs/5a9f093a2fe0/manifest.json"))
out["zip_also_contains_stub_runs_5a9f093a2fe0_manifest"] = True
out["zip_stub_model_matches_official"] = stub.get("model") == mr.get("model")

wa = max(worst, out.get("csv_worst_abs_diff", 1.0), bw); wr = max(worst_rel, out.get("csv_worst_rel_diff", 1.0), bw_rel)
if wa > TOL: problems.append(f"worst abs diff {wa!r} > TOL {TOL}")
if wr > RTOL: problems.append(f"worst relative diff {wr!r} > RTOL {RTOL}")
ok = not problems
out["problems"] = problems; out["tolerance"] = TOL; out["rel_tolerance"] = RTOL
out["verdict"] = "REPRODUCED" if ok else "NOT REPRODUCED"
print(json.dumps(out, indent=1, default=str))
sys.exit(0 if ok else 1)
