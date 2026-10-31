<!--
PR template for AIEFS. Fill in every section; write "n/a" where a section does not apply.
Status of the project: CURRENT_STATUS.md (single status file). Claim labels: registry/README.md
("## Status vocabulary"). Working rules: OPERATING_MANUAL.md. Reviewer guide: docs/REVIEWING.md.
Never paste personal details, tokens or private strings into this PR. Report PII by type and location only.
-->

## Summary

**Author (agent or person):** <!-- e.g. Researcher 001 / Auditor Seat 002 / owner -->
**Branch → base:** <!-- e.g. research/xyz → main -->

What changed and why, in plain language:

-

## Claims affected

<!-- One row per claim in registry/claims.csv that this PR adds, edits or relies on for a new statement.
     Status values must come from "## Status vocabulary" in registry/README.md. Put free-text detail in
     audited_qualifier, never in audited_status. Untested origin ideas (SSRH-ORIG-*) stay
     "Speculative / untested origin hypothesis"; Retired / Rejected / Quarantined are only for claims that
     were tested and failed, or were withdrawn. -->

| claim_id | artifact_status: before → after | audited_status: before → after | Why (evidence path) |
|---|---|---|---|
|  |  |  |  |

- [ ] No claim statuses change in this PR.
- [ ] Ledger changes were made with `registry/reconciliation/build_claims_reconciliation.py`, not by hand (if applicable).
- [ ] Hash-pinned files were not edited; corrections go in a dated `ERRATA_*.md` sidecar and the ledger.
- [ ] `CURRENT_STATUS.md` updated if the been / are / going picture changed.

## Evidence and reproduction

<!-- Exact commands a reviewer can run from the repo root, with the output you got (pasted, trimmed).
     Name run folders, seeds, commit SHAs and output files. Say what you did NOT run. -->

```bash
# e.g. python3 AIEF_1_4_memory_ablation_updated.py ...   -> runs/<id>/
```

- Result files:
- Seeds / scope (single seed? 40 seeds? hand-picked frequencies?):
- Not run / known gaps:

## Checks run locally

<!-- Paste the final "== result" line of each. CI runs the same scripts (.github/workflows/repo-checks.yml, lean.yml). -->

- [ ] `python3 tools/ci/lint_claims.py` →
- [ ] `python3 tools/ci/hygiene_scan.py --base origin/main --pii` →
- [ ] `python3 tools/ci/hygiene_scan.py` →
- [ ] `python3 tools/ci/check_manifest.py` (runs `AI Agent Audits/evidence/verify_manifest.py --inputs`) →
- [ ] `python3 -m unittest discover -s tools/ci/tests` (only if `tools/ci/` changed) →
- [ ] `python3 audits/engineering/validate_registry_against_tree.py` (if `registry/` changed; no options needed,
      needs full history for `e47bad1`) →

## Lean axiom check

<!-- Required if anything under lean/ changed; otherwise write "no Lean changes". -->

- [ ] No Lean changes.
- [ ] `cd lean/AIEFProofs && ./check_lean.sh` passed on toolchain `leanprover/lean4:v4.33.1`
      (from `lean/AIEFProofs/lean-toolchain`).
- Axioms reported (must be a subset of `propext`, `Classical.choice`, `Quot.sound`):
- `sorry` / `admit` / user `axiom` / `native_decide` markers found: <!-- must be 0 -->
- CI run link ("Lean proof check"):

## Privacy and hygiene

- [ ] No personal details (names, e-mails, street addresses, IPs, device names, home-directory paths,
      account usernames, private context) in files, commit messages or this description.
- [ ] Any PII finding is reported by **type and location only**, never the value.
- [ ] No secrets: no tokens, keys, `.env`, `*.pem`, `*.key`; hygiene scan shows 0 errors.
- [ ] No file over 95 MiB; new binaries only in folders listed in `tools/ci/hygiene_allow.txt`.
- [ ] No unrelated files (scratch, caches, `__pycache__/`, `.lake/`, editor lock files).

## Major change?

<!-- DRAFT definition, not yet confirmed by the owner (OPERATING_MANUAL.md §5). Until confirmed,
     treat anything unclear as major. Current phase: the owner approves EVERY push on any branch. -->

- [ ] **Yes, major.** It does at least one of:
  - [ ] merges into `main`
  - [ ] moves a claim to `Supported` or `Frozen`
  - [ ] retires, rejects or quarantines a claim
  - [ ] rewrites history (rebase, amend or force-push of shared commits)
  - [ ] touches privacy or personal information in any way, including scrubbing
  - [ ] deletes files
  - [ ] changes the approval rules (OPERATING_MANUAL.md, claim-label rules)
- [ ] **No, not major** under the draft definition. Reason:
- Also touched (flag for the owner; proposed additions to the draft, not yet confirmed):
  - [ ] `LICENSE`, `LICENSE-docs`, `LICENSING.md` or `NOTICE`
  - [ ] Lean core proofs under `lean/AIEFProofs/AIEFProofs/`
  - [ ] CI or check configuration (`.github/`, `tools/ci/`, `tools/ci/hygiene_allow.txt`)

## Reviewer sign-off

<!-- No bot approves its own work. The author may not tick a reviewer box. -->

| Role | Name / seat | Checks re-run (yes/no, which) | Verdict (approve / changes / comment) | Date |
|---|---|---|---|---|
| Independent reviewer (not the author) |  |  |  |  |
| Outside reviewer (GPT / Arena AI), optional |  |  |  |  |
| **Owner** (required for every push in the current phase, and for any major change) |  |  |  |  |

- [ ] Reviewer re-ran the checks above rather than trusting the pasted output.
- [ ] Reviewer checked every changed claim against its evidence path (see docs/REVIEWING.md).
- [ ] Owner approval recorded for the push / merge.
