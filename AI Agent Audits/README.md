# AI Agent Audits: AIEFS

This folder holds independent, read-only audits of this repository, along with the evidence needed to check them. The audits are judgments of the work. They are not part of the work.

## Documents

| File | Status | Dates | Contents |
|---|---|---|---|
| `AIEFS_audit.md` | **Partially superseded.** Corrected in place: struck text plus `[Correction 2026-10-23, response #N]` notes | Original 2026-10-23 (commit `55be461`); corrected 2026-10-23 | First audit: reproducibility, maths checks, Lean status, claims-vs-evidence |
| `AIEFS_salvage.md` | **Revised.** Corrected in place, same convention; the original "strongest claim" is kept and marked SUPERSEDED | Original 2026-10-23 (commit `f7246a3`); revised 2026-10-23 | What survives: closed-form predictions, ablation re-reading, κ analysis |
| `AIEFS_audit_response.md` | **Current.** This is the authoritative ledger | 2026-10-23 | Point-by-point ruling on a collaborator's 14-point critique of the two reports. Each point gets concede / partly concede / hold, with exact quotes from our text and the evidence. Also covers the critique's own overreach, revised conclusions, and a revised strongest claim |
| `evidence/` | Current | 2026-10-23 | Scripts, logs, results, manifest, environment, and reproduction steps |

Where the documents disagree, `AIEFS_audit_response.md` takes precedence.

## What was audited

- Repository: `github.com/jacobbrainard84-knightninja/AIEFS`
- Code and data audited at commit `e47bad150792425eb8e962ff636c69289eedd8b1`. The later commits `55be461` and `f7246a3` add only the two original report files, so the audited inputs match the current model code and data.
- Input file hashes: `evidence/audit_manifest.json`, under `inputs_sha256`.

## Evidence layout

```
evidence/
  REPRODUCE.md         commands (run from the repository root) and runtimes
  ENVIRONMENT.md       Python / package / Lean / mathlib versions used
  audit_manifest.json  sha256 of every published file and every audited input; for each finding:
                       command, outputs, confirmatory vs exploratory, RAN / READ / INFERRED
  run_all.sh           runs every Python step (about 15 min on 7 cores); the Lean check is separate: scripts/lean_check.sh
  scripts/             analysis scripts: read the repository, write only to evidence/results and evidence/logs
                       (lean_check.sh builds in a mktemp copy)
  logs/                stdout of each script; absolute local paths have been rewritten (see manifest)
  results/             JSON / CSV outputs
```

## Reproducing

From the repository root:

```
bash "AI Agent Audits/evidence/run_all.sh"
```

For individual steps, see `evidence/REPRODUCE.md`. Every script is deterministic with fixed seeds. The 500-run AIEF-1.3 replay and the delay-paired experiment were each rerun and reproduced bit-exactly.

## Conventions

- **Verified** means we ran it and the output is in `evidence/`, or we read it in the repository and cite the path. **Suspicion / inference** is labeled as such.
- No personal data is reproduced. Third-party PDFs in the repository are referred to by path only.
