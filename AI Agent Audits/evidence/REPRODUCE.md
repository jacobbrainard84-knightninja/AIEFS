# Reproducing the audit evidence

Run every command **from the AIEFS repository root**. All paths are relative. Scripts read repo inputs from the working directory and write to `$AIEF_AUDIT_OUT` if it is set (as `run_all.sh` does, to a temporary directory), otherwise to `AI Agent Audits/evidence/results/`. Run individually, their stdout is the log. They do not modify any repo file. Set `PYTHONDONTWRITEBYTECODE=1` to avoid creating `__pycache__`.

```bash
python -m venv .venv && . .venv/bin/activate
pip install numpy==2.5.1 scipy==1.18.1 pandas==3.1.0
export PYTHONDONTWRITEBYTECODE=1
```

## Check the published files
```bash
python "AI Agent Audits/evidence/verify_manifest.py"            # sizes + sha256 of every published file; exit 0 OK, 1 mismatch, 2 usage
python "AI Agent Audits/evidence/verify_manifest.py" --inputs   # also the audited repo inputs (needs the repo at e47bad1)
```

## Everything (about 25 min on 7 cores, peak RAM about 3 GB)
```bash
PY=python bash "AI Agent Audits/evidence/run_all.sh"            # fresh outputs in a temp dir, compared byte-for-byte with results/
UPDATE=1 PY=python bash "AI Agent Audits/evidence/run_all.sh"   # same, then copy fresh results and logs into the tree
```
The script exits nonzero if any step fails or any committed result is missing or differs.

## Individual steps
| Step | Command | Runtime | Output (results/) | Response point |
|---|---|---|---|---|
| Math checks (projection, gate, KL, Jordan) | `python "AI Agent Audits/evidence/scripts/mathcheck.py"` | s | (log only) | 5 |
| Gate idempotence, ε=0 Euclidean/KL comparison | `python "AI Agent Audits/evidence/scripts/gate_idempotence.py"` | s | gate_idempotence.json | 5 |
| Closed-form ω predictor on archived 1.3 runs | `python "AI Agent Audits/evidence/scripts/freq_predictor.py"` | s | (log only) | 1, 4 |
| Archived 1.3: distinct topologies, ablation closed forms | `python "AI Agent Audits/evidence/scripts/archived13_closedform.py"` | s | archived13_closedform.json | 1, 4, 8 |
| κ row rates on the exceptional K3 | `python "AI Agent Audits/evidence/scripts/kappa_rows.py"` | s | kappa_rows.json | 9 |
| Matched-phase memory check (exploratory; input provenance from `test_output/`) | `python "AI Agent Audits/evidence/scripts/matched_phase_check.py"` | s | matched_phase_check.json | 6; R2 #3 |
| 1.4 ablation topologies | `python "AI Agent Audits/evidence/scripts/ablation14_topology.py"` | s | ablation14_topology.json | 6 |
| κ(T_w) replays (200 seed×ρ) | `python "AI Agent Audits/evidence/scripts/kappa_tw.py" all` | ~3 min | kappa_tw_all.json | 9 |
| κ(T_w) analysis (central-difference matrix; superseded by the cycle-kernel rows) | `python "AI Agent Audits/evidence/scripts/analyze_kappa_tw.py"` | s | kappa_tw_summary.json, kappa_tw_components.csv | 9 |
| Cycle-kernel (fiber) multipliers, K3 one-sided directions, tie nonadditivity | `python "AI Agent Audits/evidence/scripts/kappa_cycle_kernel.py"` | a few min | kappa_cycle_kernel.json | R2 #2 |
| Cycle-kernel analysis vs closed form | `python "AI Agent Audits/evidence/scripts/analyze_kappa_cycle_kernel.py"` | s | kappa_cycle_kernel_summary.json | R2 #2 |
| Repo augmented-spectrum procedure checks | `python "AI Agent Audits/evidence/scripts/evolution_checks.py"` | s | evolution_checks.json | R2 #9 |
| Paired delay on/off on random ω (240 runs) | `python "AI Agent Audits/evidence/scripts/delay_paired_heldout.py"` | ~2.5 min | delay_paired_edges_{uniform,clustered}.csv, delay_paired_runs.json | 1, 2, 7 |
| Held-out prediction (both target labels + label equality), delay statistics | `python "AI Agent Audits/evidence/scripts/analyze_delay_heldout.py"` | s | delay_heldout_analysis.json | 1, 2, 7; R2 #5, #6 |
| Post-split topology frozen? (B_split vs B_final threshold status) | `python "AI Agent Audits/evidence/scripts/frozen_topology_check.py"` | s | frozen_topology_check.json | R2 #4 |
| Random-ω predictor (first-pass rerun) | `python "AI Agent Audits/evidence/scripts/omega_random.py"` | ~1.5 min | omega_random.json | 1, 3 |
| Random-ω multistability | `python "AI Agent Audits/evidence/scripts/omega_multistab.py"` | ~0.5 min | omega_multistab.json | 4, 7 |
| Reproduction of 500 archived 1.3 runs, all 38 stored keys | `python "AI Agent Audits/evidence/scripts/repro13.py"` | ~5 min | repro13.json | 13; R2 #8 |
| Terminology counts | `bash "AI Agent Audits/evidence/scripts/terminology_grep.sh"` | s | (log only) | 11 |
| Lean build (original fails, patched copy builds) | `bash "AI Agent Audits/evidence/scripts/lean_check.sh"` | ~5 min + cache download | logs/lean_build_*.log | 14 |

The Lean step needs elan. It builds a temporary copy of `lean/AIEFProofs`, so the repo is never patched. The committed logs come from the audit's own copy; its absolute temp paths were replaced with `<tmpcopy>`.

"R2 #N" = point N of `AIEFS_audit_response_2.md`. To check reproduction, run `run_all.sh` (it diffs against the committed results), or compare against the sha256 values in `audit_manifest.json` with `verify_manifest.py`. The κ(T_w) and delay outputs are deterministic on the stack in `ENVIRONMENT.md`.

## Tooling (packaging and provenance)
| Tool | Command | Output | Purpose |
|---|---|---|---|
| Manifest | `python "AI Agent Audits/evidence/tooling/make_manifest.py"` | audit_manifest.json | sha256 of audited inputs and published files; every finding with command, outputs, design type, basis |
| Manifest check | `python "AI Agent Audits/evidence/verify_manifest.py" --inputs` | tooling/logs/verify_manifest.log | sizes + sha256 of every published file and input; flags unlisted files |
| PII / secret scan | `python "AI Agent Audits/evidence/tooling/pii_scan.py" [--private FILE]` | tooling/logs/pii_scan.log, pii_scan_selftest.log | e-mails, local paths, token / device-code shapes, binaries, CR, per-file < 1 MB, total < 5 MB; private literals come from a local file that is not published and are reported by index only |
| GitHub blob check | `python "AI Agent Audits/evidence/tooling/verify_github_blobs.py" TREE.json "AI Agent Audits"` | tooling/logs/verify_github_blobs_c9907a6.log | git blob sha1 of each local file vs a GitHub tree listing (`GET /repos/{owner}/{repo}/git/trees/{sha}?recursive=1`, read-only) |
| Round-1 scratch | `tooling/round1/*.py`, `tooling/round1/deep/*.py` (redacted) | their `.log` files where kept | first-pass math check, predictor, repro, summaries, random-ω; superseded by `scripts/` |
| Round-2 builders | `tooling/round2/make_v2.py`, `make_manifest_v2.py` (redacted) | (the round-2 tree) | in-place correction and path/name neutralisation of the reports; round-2 manifest |
| Round-3 builders | `tooling/round3/corrections.py`, `kck_one.py`, `collect_tooling.py` (redacted) | (this tree) | 2026-10-24 inline corrections (applied once; not idempotent); single-seed cycle-kernel probe; the copy/redaction step that produced `tooling/` |
| Ad-hoc commands | `tooling/adhoc_commands.md` | — | staging copies, zip builds, CR→LF fix, scans, blob checks, results diff, verbatim apart from redaction |

The redacted copies are not runnable verbatim; they record what was done.

`tooling/logs/verify_manifest.log` and `tooling/logs/pii_scan.log` are written after `audit_manifest.json`. They appear in its `post_manifest_logs` list and are not hashed, which avoids circularity. Regenerate them, in order, with `make_manifest.py`, then `verify_manifest.py --inputs`, then `pii_scan.py`.
