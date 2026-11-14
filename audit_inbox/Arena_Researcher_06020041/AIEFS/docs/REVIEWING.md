# Reviewing a pull request (AIEFS)

A short guide for outside AI reviewers (GPT, Arena AI) and for people. AIEFS is a research repo:
a delayed Kuramoto network with EMA-coherence Hebbian plasticity and a capacity gate, Python
simulations, and Lean 4 proofs. Most PRs come from agents: **Researcher 001** (research and simulations)
and **Auditor Seat 002** (audit and reproduction). **No bot approves its own work.**

Read first: `CURRENT_STATUS.md` (where we've been / are / going), `registry/README.md` (what each status
label means, and the `## Status vocabulary` list), `OPERATING_MANUAL.md` (roles, workflow, approval levels).

## 1. Run the checks yourself

Do not trust pasted output; re-run. From the repo root, on the PR branch (Python 3, stdlib only):

```bash
git fetch origin && git checkout <pr-branch>
python3 tools/ci/lint_claims.py                          # claim statuses vs registry/README.md
python3 tools/ci/hygiene_scan.py --base origin/main --pii  # changed files: secrets, new binaries, PII (type+location only)
python3 tools/ci/hygiene_scan.py                         # whole tree: >95 MiB files, secret files/patterns
python3 tools/ci/check_manifest.py                       # AI Agent Audits/evidence/verify_manifest.py --inputs
python3 tools/ci/check_artifact_pins.py                  # registry/artifacts.csv sha256 pins vs the tree
python3 tools/ci/check_current_inventory.py              # registry/artifacts_current.csv matches the tree (regenerate: registry/reconciliation/build_current_inventory.py)
python3 tools/ci/check_modes.py                          # scripts not 100755 in the git index (warn-only)
python3 -m unittest discover -s tools/ci/tests           # self-tests of the checks
cd lean/AIEFProofs && ./check_lean.sh                    # only if lean/ changed; needs elan + Lean v4.33.1
```

Each script ends with `== result: ... -> PASS` or `FAIL` and exits non-zero on failure. Warnings
(`BIG_FILE`, `SECRET_ASSIGN`, `PII_*`, `KNOWN_NOT_EXEC`, `SHEBANG_NOT_EXEC`) do not fail CI but must be looked at. The same scripts run in
CI (`.github/workflows/repo-checks.yml`); the Lean build and axiom allowlist run in
`.github/workflows/lean.yml`. Lean may use only `propext`, `Classical.choice`, `Quot.sound`, with no
`sorry`/`admit`.

If you cannot run something (no Lean toolchain, no time for a simulation), say so in your review.

## 2. Verify the claims

For every row of the PR's "Claims affected" table:

1. Find the row in `registry/claims.csv` (by `claim_id`). Read `statement`, `scope_boundary_and_caveat`,
   `audited_status`, `audited_qualifier`, `audit_source`.
2. Open the evidence paths the PR cites. Check the numbers in the statement match the files.
3. Re-run at least one reproduction command from the PR when feasible, and compare.
4. Check the scope is not stretched: single seed vs. 40 seeds; hand-picked vs. random frequencies;
   exact-only-under-conditions results stated with their conditions; no causal words ("mediates",
   "drives") without a causal test.
5. Check the label rules:
   - status values are exactly from `## Status vocabulary` (the lint enforces this);
   - untested origin ideas (`SSRH-ORIG-*`) stay *Speculative / untested origin hypothesis*, never
     Retired;
   - Retired / Rejected / Quarantined only for claims tested and failed, or withdrawn;
   - hash-pinned files are not edited; corrections go in a dated `ERRATA_*.md` and the ledger.
6. If `CURRENT_STATUS.md` changed, every factual line should point to a file in the repo.

## 3. Privacy and hygiene

Report personal information by **type and location only** (e.g. "e-mail address, `FILE.md:91`"),
never the value, including in review comments. Never paste tokens or private strings. Flag
any new binary, any file near 100 MiB, and unrelated files (caches, scratch).

## 4. What counts as major

**DRAFT definition, not yet confirmed by the owner** (mirrors `OPERATING_MANUAL.md` §5). A change is
major if it:

- merges anything into `main`;
- moves a claim to `Supported` or `Frozen`;
- retires, rejects or quarantines a claim;
- rewrites history (rebase, amend or force-push of shared commits);
- touches privacy or personal information in any way, including scrubbing;
- deletes files;
- changes the approval rules (the operating manual or claim-label rules).

Proposed additions awaiting the owner: changes to `LICENSE*`/`NOTICE`, to the Lean core proofs, or to CI
and check configuration (`.github/`, `tools/ci/`). Until confirmed, treat anything unclear as major.

**Current phase:** the owner approves every push, on any branch. Later the owner approves only major
changes. A reviewer approval never replaces the owner's.

## 5. Writing the review

State: what you re-ran and the results; each claim checked (agree / disagree, with file:line); anything
you could not check; whether the PR is major under the draft definition; and a verdict (approve /
request changes / comment). Keep it in plain language.
