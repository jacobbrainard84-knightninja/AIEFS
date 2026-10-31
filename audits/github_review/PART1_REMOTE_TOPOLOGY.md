# Part 1 — Remote & Branch Topology Review

**Repository:** `jacobbrainard84-knightninja/AIEFS`
**Review date:** 2026-10-30 (all figures read live from GitHub + a full-ref fetch)
**Scope of Part 1:** the *remote as a system* — repository settings, branch topology, divergence,
merge/PR state, CI registration and run history. Content-level analysis of every branch is Part 2;
risk register and remediation sequence is Part 3. No repository files were modified by this review.

---

## 1. Repository facts

| Property | Value |
|---|---|
| Full name | `jacobbrainard84-knightninja/AIEFS` |
| Visibility | Public, not a fork, not archived, `viewerCanAdminister = true` |
| Created | 2026-08-24T01:46:56Z |
| Default branch | `main` |
| Description | "A math project" (no topics set) |
| Licence | Apache-2.0 (`LICENSE`, `LICENSE-docs`, `LICENSING.md`, `NOTICE` — **all present on `main` only**) |
| Commits on `main` | **128** |
| Branches | **9** (1 default + 8 unmerged) |
| Pull requests | **0** (none open, none closed, none merged, ever) |
| Issues | **0** | Discussions | disabled | Wiki | disabled |
| Releases / tags | **0 / 0** | Projects | enabled (unused) |
| Packed size | 363,041 KB (~354 MiB) |
| Working-tree blobs per branch | 1.17 GB – 1.20 GB (2,829 – 3,000 files) |
| Last push | 2026-10-29T23:12:23Z (`research/freezing`) |
| Merge policy | merge commits ✔, squash ✔, rebase ✔; **auto-merge disabled**; **delete-branch-on-merge disabled** |
| Rulesets | none returned (`[]`) |
| Classic branch protection | **unverified** — API returned `403 Resource not accessible by integration` |

> The 1.17–1.20 GB per-branch figure is the sum of blob sizes in the tree; the 354 MiB packed figure is
> GitHub's git-object size. The gap is zip/PDF compression, so **the same ~1.2 GB of blobs is duplicated
> across nine branch trees** rather than being branch-specific growth.

---

## 2. Branch inventory (live, as of this review)

`Δ commits` is measured against `main` (`git rev-list --count main..branch`), read after fetching
`+refs/heads/*:refs/remotes/origin/*`.

| Branch | Tip | Last commit | Files | Blobs | Δ commits | Role |
|---|---|---|---|---|---|---|
| `main` | `853498f` | 2026-10-27 | 2,882 | 1,196.8 MB | — | Trunk: licensing + CI + `tools/sync` + `AI Agent Audits/` |
| `merge-prep/arena-reconciled` | `9d46d9b` | 2026-10-29 | 2,974 | 1,199.7 MB | +29 | **Base of the whole 2026-10-29 stack**; the prior Arena reconciliation |
| `ci/artifact-pins` | `a64d90e` | 2026-10-29 | 2,976 | 1,199.7 MB | +30 | Stacks on `merge-prep` (+1: sha256 pin check) |
| `audit/nanfix-v2` | `cbf2ae7` | 2026-10-29 | 2,978 | 1,199.7 MB | +31 | Stacks on `merge-prep` (+2: NaN-mask reproduction, ERRATA E10) |
| `ci/validator-and-lean-matrix` | `249ea3f` | 2026-10-29 | 2,977 | 1,199.7 MB | +32 | Stacks on `merge-prep` (+3: registry validator, 3-project Lean matrix) |
| `research/lean-kn` | `5c62d64` | 2026-10-29 | 2,984 | 1,199.7 MB | +33 | Stacks on `merge-prep` (+4: `lean/AIEFProofsKn`, 10 files) |
| `research/freezing` | `85ba0a6` | 2026-10-29 | 3,000 | 1,199.8 MB | +37 | Stacks on `merge-prep` (+8: `lean/AIEFFreezeCore`, 8 files) |
| `fix/corr-0995-scope` | `b77ce5f` | 2026-10-28 | 2,882 | 1,196.8 MB | +1 | Straight off `main`; 2 files, 4 insertions (docs scoping) |
| `arena/d4a487cc-aiefs` | `7edbab2` | 2026-10-23¹ | 2,829 | 1,172.9 MB | **123 behind** | This session's Milestone 1 (69 files) |

¹ The commit's author *and* committer timestamps are `2026-10-23 17:03:46 +0000` — the base commit's
date, not the date the work was performed (2026-10-30). See finding **R-07**.

### 2.1 Topology

```
main (853498f, 128 commits)
├── fix/corr-0995-scope                 +1   docs-only: scope Corr_physical ≈ 0.995
└── merge-prep/arena-reconciled         +29  registry/, audits/, docs/, .github/workflows/repo-checks.yml,
    │                                        tools/ci/, ERRATA E1–E9, PUSH_NOTES, MERGE_PREP_REPORT
    ├── ci/artifact-pins                +1   sha256 pins for registry/artifacts.csv
    ├── audit/nanfix-v2                 +2   NaN-mask fix reproduction + ERRATA E10
    ├── ci/validator-and-lean-matrix    +3   3-project Lean matrix + presence gate + validate_registry
    ├── research/lean-kn                +4   lean/AIEFProofsKn   (sibling of research/freezing)
    └── research/freezing               +8   lean/AIEFFreezeCore (sibling of research/lean-kn)

e47bad15  ← 123 commits behind main, 2026-10-23
└── arena/d4a487cc-aiefs                +2   69 files: registry/, audits/, README/CURRENT_STATUS/REPRODUCING
```

Ancestry was confirmed pairwise (`git merge-base --is-ancestor`). `research/lean-kn` and
`research/freezing` contain **neither** the other; `ci/validator-and-lean-matrix` contains neither
research branch. Every branch except `fix/corr-0995-scope` and `arena/*` descends from
`merge-prep/arena-reconciled`, which therefore is the **de-facto integration point** for all 2026-10-29 work.

---

## 3. Divergence: this session's branch vs `main`

`arena/d4a487cc-aiefs` is based on `e47bad15` (2026-10-23). GitHub's compare API reports
`e47bad15...main = {status: ahead, ahead_by: 123, total_commits: 123, files: 231}` — i.e. **the base of this
branch is 123 commits behind `main`, not 1** as a shallow clone suggests. (The local clone is shallow:
`.git/shallow` holds 2 boundary commits, so local `rev-list` counts are truncated. All counts in this
document are from the GitHub API or from a full refs fetch.)

### 3.1 What a PR from this branch would actually do

| Measure | Value |
|---|---|
| Files in the PR (three-dot, base `e47bad15` → branch) | **69** (all additions) |
| Deletions | **0** |
| Files already present on `main` | 0 |
| Files already present on `merge-prep/arena-reconciled` | **66 of 69** |

So the PR is additive and non-destructive — **but it is built on a five-day-stale snapshot**, and 66 of its
69 files already exist in a *different* form on `merge-prep`.

### 3.2 Two-dot tree diff vs `main` (for completeness, not a PR preview)

`git diff main arena` = **121 added / 174 deleted / 5 modified**. The 174 are files `main` has that this
branch never had (123 commits of work), and the 52 "base files absent from main" are `main`'s cleanup:

| Group | Count | Note |
|---|---|---|
| `__pycache__/*.pyc` | 17 | purged on `main` + `.gitignore` |
| `lean/AIEFProofs/.lake/**` | 30 | build cache purged on `main` |
| `Papers/*.pdf` | 4 | removed on `main` |
| `.~lock.AI_AGENT_HANDOFF_PROMPT.md#` | 1 | LibreOffice lock file, removed on `main` |
| `lean/…/ControllerFiber.lean`, `AIEFProofs.lean`, `.gitignore` ×2, `README.md` | 5 modified | `ControllerFiber.lean` change is **licence header + SPDX line only** (no proof text) |

Merging this branch into `main` would **not** resurrect those 52 files (they are untouched on this branch,
so the deletions on `main` stand). The damage is to the *registry*, which still classifies them as live
artifacts (see R-04).

### 3.3 What `main` now contains that the Stage 1 registry has never seen (174 files)

| Group | Files | Weight |
|---|---|---|
| `AI Agent Audits/` | **148** | An independent, read-only audit of commit `e47bad15`: audit + 3 response ledgers + salvage + manifest + logs + results + reproductions + tooling |
| `tools/sync/` | 9 | Upload/download/untrack shell tooling + its own tests |
| `lean/AIEFProofs/**` (new) | 5 | `CompleteGraphIncidence.lean`, `ControllerFiberProjector.lean`, `ControllerFiberQuotient.lean`, `check_lean.sh`, `AIEF_LEAN_SOURCE_SHA256SUMS.txt` |
| `Project Histories/` | 4 | `README.md` + 3 new workspace zips |
| `Project Origins/` | 3 | Origin-document PDFs |
| Root | 4 | `LICENSE`, `LICENSE-docs`, `LICENSING.md`, `NOTICE` |
| `.github/workflows/` | 1 | `lean.yml` — the only CI that has ever run here |

---

## 4. The parallel reconciliation problem

`merge-prep/arena-reconciled` is an **earlier run of the same Milestone-1 programme**, applied on top of
`main` instead of on top of `e47bad15`. It adds 92 files and modifies 3 (`Basic.lean`, `Smoke.lean`,
`AIEF_LEAN_SOURCE_SHA256SUMS.txt`).

| Layer | This branch (`arena/*`) | `merge-prep/arena-reconciled` |
|---|---|---|
| `registry/artifacts.csv` | 2,898 rows | 2,898 rows (different content) |
| `registry/claims.csv` | **43** rows | **75** rows |
| `registry/studies.csv` | **14** rows | **15** rows |
| `registry/supersessions.csv` | 20 rows | 20 rows |
| `registry/relocation_map.csv` | 221 rows | 221 rows |
| Extra registry file | — | `registry/lineage_reconciliation.csv` + `registry/reconciliation/build_claims_reconciliation.py` |
| Errata | inside `SCIENTIFIC_CLASSIFICATION_AND_REJECTIONS_AUDIT.md` | `ERRATA_2026-10-28.md` (E1–E9) |
| CI | none | `.github/workflows/repo-checks.yml` + `tools/ci/` (6 scripts, 2 test modules), PR template, `.gitattributes`, `requirements.txt` |
| Docs | `README`, `CURRENT_STATUS`, `REPRODUCING`, `history/timeline.md`, `docs/architecture/…` | the same, **plus** `docs/REVIEWING.md`, `OPERATING_MANUAL.md`, `MERGE_PREP_REPORT.md`, `MERGE_PREP_LOCAL_HISTORY.md`, `PUSH_NOTES.md`, `PRIVACY_SCRUB_LIST.md`, `AIEF_1_4_superseded_claims.LEDGER_POINTER.md` |
| New analysis | — | `AIEF_1_4_Twindow_sensitivity_analysis_v4_1.py` + `tests/test_v4_1_held_event.py` |

Path-level overlap with this branch's 69 files: **66 identical-or-divergent paths**, of which
**52 are byte-identical** and **15 differ**:

`README.md`, `CURRENT_STATUS.md`, `REPRODUCING.md`, `registry/{artifacts,claims,studies,relocation_map,supersessions}.csv`,
`registry/README.md`, `audits/engineering/python_path_dependencies.csv`,
`audits/github_reconciliation/{zip_vs_tree_comparison,runs_cohort_reconciliation}.csv`,
`audits/github_reconciliation/recovered_from_workspace_019ff402/zip_only_files/{AIEF_1_4_CONTROLLER_FIBER_CLAIM_REGISTRY,AIEF_1_4_analysis_lineage}.csv`,
`lean/AIEFProofs/AIEF_LEAN_SOURCE_SHA256SUMS.txt`.

The three files unique to this branch are recovered binaries that `merge-prep` deliberately omitted:
`zip_only_files/results_embedded.bin`, `results_embedded.docx`, `uploads/Results.pdf`.

---

## 5. CI/CD reality check

**Registered workflows on the default branch: exactly one** — `Lean proof check` (id `395577164`, active,
SHA-pinned actions, `concurrency: cancel-in-progress`).

| Fact | Value |
|---|---|
| Runs ever (all visible) | **45**, from 2026-10-25T02:04Z to 2026-10-29T23:10Z |
| Conclusion | **11 success, 34 cancelled, 0 failed** (75.6 % cancelled) |
| Runs by branch | `main` 37, `research/lean-kn` 3, `research/freezing` 2, `ci/validator-and-lean-matrix` 2, `merge-prep` 1 |
| Runs on `arena/d4a487cc-aiefs` | **0** |
| Runs on `audit/nanfix-v2`, `ci/artifact-pins`, `fix/corr-0995-scope` | **0** |

Four gaps follow directly from the workflow files and the run log:

1. **The research Lean projects have never been built by CI.** `research/lean-kn` and `research/freezing`
   inherit `main`'s `lean.yml`, which hard-codes `working-directory: lean/AIEFProofs`,
   `lake-package-directory: lean/AIEFProofs`, `axiom-audit-root: AIEFProofs`. Their green runs are green
   about the *old* project only; `lean/AIEFProofsKn` (10 files) and `lean/AIEFFreezeCore` (8 files) are
   unverified in CI.
2. **The 3-project matrix has never been active.** It exists only on `ci/validator-and-lean-matrix`
   (`fail-fast: false`, `required: false` rows with a presence gate in `tools/ci/lean_presence.sh`), and
   GitHub only runs workflows from the default branch.
3. **`repo-checks.yml` has never run.** It triggers on `pull_request` and on `push: branches [main]`; there
   have been zero PRs and `merge-prep` is not merged. The PR template it ships has never been used.
4. **No workflow exercises Python analysis.** Nothing runs `pytest`, the registry gates, or
   `verify_inventory.py` on any branch — including ours. The 41-passing / 1-skipped suite documented in
   `audits/engineering/` is a local result, not a CI result.

Also note: with `cancel-in-progress: true` and 37 pushes to `main`, **three-quarters of all CI runs were
cancelled**, so "0 failures" is a weaker signal than it looks.

---

## 6. Process observations

- **No pull request has ever been opened** in this repository (0 of any state). All eight side branches are
  unmerged and have no recorded review trail; `fix/corr-0995-scope` (2026-10-28) is the only branch with a
  conventional `type/scope` name and a single-purpose commit, and it is the one furthest from being merged.
- **Single-author history**: every commit is `jacobbrainard84-knightninja`; the "audited CLEAN by Auditor
  Seat 002" language on the research branches is a *commit-message* convention, not a GitHub review object.
- **`delete_branch_on_merge` is off** and auto-merge is disabled, so merged branches would persist
  (relevant because several branches are full supersets of each other).
- **No tags or releases.** Nothing in the repository pins a published state, despite `AIEF_LEAN_PROJECT_LOCK_HASHES.txt`
  and `authority.lock.json` relying on exact source hashes.
- **Chronology hazard.** `main`'s last commit is 2026-10-27, but work continued on branches through
  2026-10-29; the branch this session works on is stamped 2026-10-23. Any timeline built by sorting dates
  (including `history/timeline.md`, which states `Last Verified: 2026-10-23`) is **wrong about order**.

---

## 7. Part-1 findings

| ID | Severity | Finding | Resolved in |
|---|---|---|---|
| **R-01** | **High** | `arena/d4a487cc-aiefs` is based 123 commits behind `main`; its registry describes a tree that has since acquired licensing, CI, 148 audit files, 5 Lean files, 9 tooling files and 7 new zips/PDFs, while listing 52 files `main` deleted as if live. | Part 3 (rebase/retarget sequence) |
| **R-02** | **High** | Two competing implementations of the same governance layer (`arena/*` 69 files vs `merge-prep` 92 files; 66 overlapping paths, 15 byte-divergent). Merging both yields duplicate `registry/`, duplicate `audits/`, and two different `claims.csv` truths (43 vs 75 rows). | Part 2 (divergence table) + Part 3 |
| **R-03** | **High** | The registry is unaware of `AI Agent Audits/` (148 files) — the repository's own authoritative audit ledger, which already rules on several of the same claims (E1–E9/`AUD-CORR-0995`, 374-census, K3 lineality). | Part 2 |
| **R-04** | Medium | 174 files on `main` are uninventoried; 52 inventoried files no longer exist on `main` (still counted as Frozen/Superseded). Two-axis status counts are therefore stale by construction. | Part 2/3 |
| **R-05** | Medium | CI does not cover the work: `AIEFProofsKn` and `AIEFFreezeCore` never built; matrix workflow inactive; `repo-checks.yml` never triggered; no Python gates anywhere. | Part 3 (Milestone 2 Stage 7) |
| **R-06** | Medium | This branch has zero CI runs and cannot have any: `lean.yml` is path-filtered to `lean/**`, and no workflow tests Python. | Part 3 |
| **R-07** | Medium | Commit `7edbab2` is timestamped 2026-10-23 (base date) although produced 2026-10-30; `CURRENT_STATUS.md` asserts `Last Verified: 2026-10-23`. Provenance dates are misleading. | Part 3 |
| **R-08** | Low | Zero PRs/issues/tags ever; eight unmerged branches; `delete_branch_on_merge` off. No published state is pinned. | Part 3 |
| **R-09** | Low | 34/45 CI runs cancelled by concurrency under 37 direct pushes to `main`; "0 failures" is weak evidence. | Part 3 |
| **R-10** | Low | Rulesets: none. Classic branch protection unreadable with the current token (`403`), so protection status is **unverified**, not confirmed absent. | Part 3 (manual check) |
| **R-11** | Low | `fix/corr-0995-scope` edits the two narrative docs in place; `merge-prep` instead documents the same correction as a scope note in `ERRATA E9` and leaves the docs untouched. Two incompatible remediations of one audit point. | Part 2 |
| **R-12** | Info | `research/lean-kn` ∥ `research/freezing` are siblings, and the matrix branch is a third sibling: the integration of all three exists on **no** branch. | Part 2/3 |

---

## 8. What Part 2 will cover

1. Content diff of every branch against `main`: what each adds, file by file, grouped by purpose.
2. The three reconciliation lineages side by side (`arena/*`, `merge-prep`, `AI Agent Audits/`) — which
   claims each asserts, and where they contradict.
3. The 15 byte-divergent overlapping paths: exact nature of each divergence (row counts, extra claims,
   changed verdicts).
4. The research branches as *scientific* content: `AIEFProofsKn` and `AIEFFreezeCore` — new theorems, their
   relation to `ControllerFiber.lean`, and whether the "audited CLEAN" claim is supported by what is on the
   branch.
5. `audit/nanfix-v2` and `ci/artifact-pins`: whether the fixes they carry are already covered by this
   session's scientific audit.

---

### Data appendix — commands used

```bash
gh repo view --json …                                  # settings, licence, size, merge policy
git ls-remote --heads origin                           # 9 heads, 0 tags
git fetch origin '+refs/heads/*:refs/remotes/origin/*'  # full refs (clone is shallow)
gh api repos/…/rulesets ; gh api …/branches/main/protection
gh api repos/…/compare/e47bad15...main                 # ahead_by 123
gh pr list --state all ; gh issue list --state all ; gh release list ; gh workflow list --all ; gh run list --limit 100
git merge-base --is-ancestor (pairwise, 12 pairs)
git ls-tree -r -l <ref> | awk '{s+=$4}'                # per-branch blob footprint
```
