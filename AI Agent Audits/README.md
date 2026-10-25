# AI Agent Audits: AIEFS

This folder holds independent, read-only audits of this repository, along with the evidence needed to check them. The audits are judgments of the work. They are not part of the work.

## Documents

| File | Status | Dates | Contents |
|---|---|---|---|
| `AIEFS_audit.md` | **Partially superseded.** Corrected in place: struck text plus `[Correction 2026-10-23, response #N]` and `[Correction 2026-10-24, response-2 #N]` notes | Original 2026-10-23 (commit `55be461`); corrected 2026-10-23 and 2026-10-24 | First audit: reproducibility, maths checks, Lean status, claims-vs-evidence |
| `AIEFS_salvage.md` | **Revised.** Corrected in place, same convention; the original "strongest claim" is kept and marked SUPERSEDED | Original 2026-10-23 (commit `f7246a3`); revised 2026-10-23 and 2026-10-24 | What survives: closed-form predictions, ablation re-reading, κ analysis |
| `AIEFS_audit_response_3.md` | **Current.** This is the authoritative ledger | 2026-10-25 | Round-4 ruling: 374-census split, exact vs conditional rate law and finite-ε fixed point, K3 zero lineality and one-sided rays, derived tie patterns, P_future check, Bregman domain, publication commits, PII scope, quarantine of the 18-coordinate spectrum, Lean (Part B) |
| `AIEFS_audit_response_2.md` | **Superseded where marked** by `AIEFS_audit_response_3.md` (`[Correction 2026-10-25, response-3 #N]` notes); was the round-3 ledger | 2026-10-24; corrected 2026-10-25 | Round-3 ruling on two reviews of the published tree (commit `c9907a6`): gate no-go, cycle-kernel κ and K3 census, matched-phase provenance, memory and delay wording, held-out target label, design labels, full-key reproduction, engineering. Each point gets concede / partly concede / dispute, with exact quotes, the derivation, the evidence, and the fix |
| `AIEFS_audit_response.md` | **Partly superseded** by `AIEFS_audit_response_2.md`; corrected in place with `[Correction 2026-10-24, response-2 #N]` notes | 2026-10-23; corrected 2026-10-24 | Point-by-point ruling on a collaborator's 14-point critique of the two reports. Each point gets concede / partly concede / hold, with exact quotes from our text and the evidence. Also covers the critique's own overreach, revised conclusions, and a revised strongest claim |
| `evidence/` | Current | 2026-10-23; updated 2026-10-24 | Scripts, logs, results, manifest, environment, and reproduction steps |

Where the documents disagree, `AIEFS_audit_response_3.md` takes precedence, then `AIEFS_audit_response_2.md`, then `AIEFS_audit_response.md`.

## What was audited

- Repository: `github.com/jacobbrainard84-knightninja/AIEFS`
- Code and data audited at commit `e47bad150792425eb8e962ff636c69289eedd8b1`. The later commits `55be461` and `f7246a3` add only the two original report files, so the audited inputs match the current model code and data.
- Input file hashes: `evidence/audit_manifest.json`, under `inputs_sha256`.
- The round-2 publication is commits `880e07e..c9907a6`. ~~The round-3 changes in this folder (corrections dated 2026-10-24, `AIEFS_audit_response_2.md` and the new evidence) were prepared locally and are not part of that publication.~~ **[Correction 2026-10-25, response-3 #6: stale: round 3 was published at `60e6029` (22 commits, `7d752fd`…`60e6029`); then `0b5b108` (Lean projector) and `0f5ef7a`…`dc0250a` (tooling, lean_recovery, cleanup; 56 commits). The round-4 changes (corrections dated 2026-10-25, `AIEFS_audit_response_3.md`) are local until the owner approves publication]**

## Evidence layout

```
evidence/
  REPRODUCE.md         commands (run from the repository root) and runtimes
  ENVIRONMENT.md       Python / package / Lean / mathlib versions used
  audit_manifest.json  sha256 of every published file and every audited input; for each finding:
                       command, outputs, design type (controlled exploratory / exploratory / reproduction check), RAN / READ / INFERRED
  verify_manifest.py   checks every published file against audit_manifest.json (size + sha256); --inputs also checks the audited repo inputs
  run_all.sh           runs every Python step into a temporary directory and compares the fresh outputs byte-for-byte with
                       results/ (about 25 min on 7 cores); UPDATE=1 copies them in. The Lean check is separate: scripts/lean_check.sh
  scripts/             analysis scripts: read the repository, write only to $AIEF_AUDIT_OUT (set by run_all.sh) or evidence/results
                       (lean_check.sh builds in a mktemp copy)
  logs/                stdout of each script; absolute local paths have been rewritten (see manifest)
  results/             JSON / CSV outputs
  tooling/             the packaging and provenance tooling (see "Tooling" below and REPRODUCE.md)
```

## Tooling

Every script used to build, check or package this folder is included, so other agents can audit the process as well as the results.

- `tooling/make_manifest.py` writes `audit_manifest.json` (input hashes, findings, file hashes).
- `tooling/pii_scan.py` scans this folder for e-mail addresses, local paths, token and device-code shapes, binaries, CR line endings and size limits. `--private FILE` adds literals kept in a local, unpublished file; matches are printed as `<private literal #k>`, never as the value. **Scope: this folder only.** A CLEAN result says nothing about the rest of the repository; repo-wide privacy/copyright is an open owner decision (`AIEFS_audit_response_3.md` #7). `tooling/logs/pii_scan_selftest.log` shows it catching 5/5 planted issues.
- `tooling/verify_github_blobs.py` compares the git blob sha1 of local files with a GitHub tree listing. It was used to confirm that the round-2 publication at `c9907a6` is byte-identical to the staged tree (`tooling/logs/verify_github_blobs_c9907a6.log`).
- `tooling/round1/`, `tooling/round2/`, `tooling/round3/` hold the scratch scripts (and their logs, where they were kept) from each round. `tooling/round4/corrections_r4.py` applied the dated 2026-10-25 corrections. `tooling/adhoc_commands.md` holds the interactive shell commands: staging copies, zip builds, the CR→LF fix, scans, the blob check, and the v2-vs-v3 results diff.
- These copies are **redacted**: local paths are replaced by `<placeholders>`, the owner's e-mail by `<owner-email-redacted>`, and user/host names by `<redacted>`. They are there for audit and are not runnable verbatim. The runnable, path-free versions of the analyses are in `scripts/`.
- Numbers that cannot be traced to a script, log and result are listed in `AIEFS_audit_response_2.md`, under "Provenance gaps".

## Reproducing

From the repository root:

```
python "AI Agent Audits/evidence/verify_manifest.py"            # published files match the manifest (exit 0)
python "AI Agent Audits/evidence/verify_manifest.py" --inputs   # also check the audited repo inputs
python "AI Agent Audits/evidence/tooling/pii_scan.py"           # personal-data / secret / packaging scan (exit 0 = CLEAN)
bash "AI Agent Audits/evidence/run_all.sh"                      # rerun everything into a temp dir and diff against results/
```

For individual steps, see `evidence/REPRODUCE.md`. Every script is deterministic with fixed seeds. The delay-paired experiment reproduced byte-identically. The 500-run AIEF-1.3 replay is bit-exact on all 7 stored arrays and the 4 headline scalars; 78/500 runs are bit-exact on all 38 stored keys, and the rest differ only in derived scalars by ≤1.3e-12 relative (`AIEFS_audit_response_2.md`, #8).

## Conventions

- **Verified** means we ran it and the output is in `evidence/`, or we read it in the repository and cite the path. **Suspicion / inference** is labeled as such.
- No personal data is reproduced. Third-party PDFs in the repository are referred to by path only.
