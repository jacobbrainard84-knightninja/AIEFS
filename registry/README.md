# AIEFS Epistemic & Conservation Registries (`registry/`)

This directory provides the machine-verifiable **authoritative status and provenance layer** for every artifact, study, scientific claim, supersession relationship, and planned Stage 4 path relocation in `jacobbrainard84-knightninja/AIEFS`.

All tables in this directory are validated automatically by:

```bash
python3 audits/engineering/verify_inventory.py
```

> **2026-10-28 (local merge-prep into `main`, pending auditor review).** On the merged tree, `verify_inventory.py`
> fails at check [1/5]. It conserves the file list of `e47bad1`, and `main` has since deleted 52 inventoried files.
> Use `python3 audits/engineering/validate_registry_against_tree.py` instead (add `--write` to refresh the flags).
> It runs on a fresh clone with no options; it needs the `--base` commit (`e47bad1`), so fetch full history
> (`git fetch --unshallow`) in a shallow clone. `--edited-since REV` is optional and must name a commit present in the clone.
> It records each row's current state in two appended columns, `tree_check_2026_10_28` and `tree_check_note`.
> The controlled-vocabulary columns were checked separately and are still valid. Audit verdicts were added as
> **new columns**, so existing `artifact_status` values stay inside the vocabulary. Status moves made per the audit
> (2026-10-28, `MERGE_CHECK`): EMP-AIEF14-02 and EMP-AIEF14-03 `Frozen` → `Exploratory`; CF05 and CF10 `Frozen` →
> `Supported` (finite numerical observation, single seed); AUD-SLOWPOLE → `Rejected` (the audited label is
> *Quarantined*, which the vocabulary lacks); SSRH-ORIG-01..07 `Unreviewed` → `Incomplete` (see "Status categories").
> Where an audited label has no `artifact_status`/`evidence_scope` value, the label is written in `audited_status` (see "Status vocabulary") and the row note says so.
> Corrections to hash-pinned documents are in `ERRATA_2026-10-28.md`; those files keep their pinned bytes.

---

## Two Orthogonal Classification Axes

A central finding of the repository audit is that **reproducibility of an artifact** and **mathematical generality of what that artifact proves** are orthogonal properties. A frozen simulation `.npz` can be bit-for-bit reproducible (`Frozen`) without establishing a general mathematical theorem, and an algebraic proof in Lean 4 can be formally verified (`Formalized theorem`) while still requiring an empirical bridge (`Finite numerical observation`) to show that its hypotheses hold along a trajectory.

Every row in `artifacts.csv`, `claims.csv`, and `studies.csv` therefore carries **both** independent controlled fields:

### Axis 1 — `artifact_status` (Trust & Lifecycle State)

| Value | Definition |
|---|---|
| `Supported` | Active, audited code, proof, or analysis currently endorsed within its stated `evidence_scope`. |
| `Frozen` | Immutable reference dataset, baseline cohort, or source-hash-locked production file that must never be edited or regenerated in place. |
| `Exploratory` | Preliminary pilot run (`runs_pivot_study/ebfec9a5c419`), historical origin scan, or draft manuscript with explicitly documented caveats (`AIEF_1_4_OPERATOR_THEORY_MANUSCRIPT.md`). |
| `Superseded` | Earlier code version, deterministic duplicate rerun, partial numbered output folder (`01`), build cache (`.pyc`, `.lake/`), or `.zip` duplicate replaced by a newer canonical artifact. |
| `Rejected` | Scientifically falsified or methodologically invalid analysis/output (e.g., 8D POD operator compression with `24,323.8%` leakage, subgraph triangle overcount `856` vs `26` isolated $K_3$ components, or pseudoreplicated `paired_seed_analysis/`). Preserved unmodified for negative-result provenance; never cite as positive support. |
| `Incomplete` | Aborted or partial execution artifact lacking completed outputs (e.g., `aief_1_4_matched_phase_memory_ablation/` 3-file partial attempt, `runs/a937d5e96efb/`). |
| `Unreviewed` | Reserved for uninspected files (`0` rows in Milestone 1 — all `2,898` worktree + archive entries have been explicitly classified; *classified* is not the same as *audit-verified*). |

### Axis 2 — `evidence_scope` (Epistemic Strength)

| Value | Definition |
|---|---|
| `Implementation identity` | Exact property of implemented code, deterministic data transformation, equivalence gate, or build configuration. |
| `Finite numerical observation` | Exact replay diagnostic or numerical measurement on specific saved seeds, finite time horizons, or selected tangent directions. |
| `Controlled experimental result` | Multi-seed randomized counterfactual / paired-ablation statistical finding on fixed model protocols (e.g., $N=100$ disjoint AIEF-1.3 cohorts; 40-seed split-state, matched-phase, and 200-condition $T_{\text{window}}$ studies). |
| `Conditional theorem` | Analytic mathematical proof valid strictly under explicit structural hypotheses (e.g., persistent strict winner inequalities, edge-uniform base point $x_G = x_{\text{common}}\mathbf{1}$). |
| `Formalized theorem` | Machine-checked Lean 4 proof with zero `sorry`/`admit` axioms (`ControllerFiber.lean`: $\ker C_{\{2,7\}} = \operatorname{span}\{(1,-1,-1)\}$). |
| `Conjecture` | Open mathematical question or unproved infinite-time asymptotic hypothesis (`CF11`, `CF12`, pre-AIEF SSRH origin hypotheses). |

### Status categories (past origin hypotheses / current tested results / future untested ideas)

Added 2026-10-28 by owner decision. `audited_status` in `claims.csv` places each claim in one of three categories:

| Category | `audited_status` / rows | Rule |
|---|---|---|
| **Past origin hypotheses** | *Speculative / untested origin hypothesis* — `SSRH-ORIG-01..07` (`artifact_status` `Incomplete`, `evidence_scope` `Conjecture`, the nearest vocabulary values) | The pre-AIEF ideas the project grew from. Kept as origins and possible future directions. Not cited as results until a testable form is stated and a test is run; then they can be promoted to `Exploratory` or `Supported`. Each row's `reconciliation_note` says what would test it ("testable form not yet stated" where that is the case). |
| **Current tested results** | `Supported …`, `Exploratory …` and similar audited labels on `EMP-*`, `CF*`, `IMPL-*`, `LEAN-*`, `AUD-*` | Cited only at the scope given in `audited_status`, `audited_qualifier` and `scope_boundary_and_caveat`. |
| **Future untested ideas** | *Conjecture …* / *Not established* (`CF11`, `CF12`, `AUD-NOVELTY`) | Open questions; stated as such, never cited as results. |

**Retired / Rejected / Quarantined is reserved for claims that were tested and failed, or that were withdrawn**
(`S01–S18`, `REJ-*`, `AUD-SLOWPOLE`). An untested hypothesis is not retired.

## Status vocabulary

```text
Supported
Frozen
Exploratory
Superseded
Rejected
Incomplete
Unreviewed
Controlled exploratory
Finite numerical observation
Conjecture / Exploratory
Not established
Speculative / untested origin hypothesis
Retired / Superseded
Quarantined
```

The block above is the exact list of allowed claim statuses (added 2026-10-28). Matching is
case-sensitive, and a CI lint parses the block. In `registry/claims.csv`, every value in the
`artifact_status` column and every value in the `audited_status` column must be one of these strings,
exactly. Free-text detail about an audited verdict, such as "conditional, single exceptional seed", goes
in the `audited_qualifier` column, never in `audited_status`.

The first seven are the `artifact_status` values that `audits/engineering/verify_inventory.py` enforces
(see "Axis 1" above for their meanings). The rest are audit labels used in `audited_status`:

- **Supported**: the audit verified, derived or accepted the claim at the scope stated in
  `audited_qualifier` and `scope_boundary_and_caveat`.
- **Exploratory**: a preliminary or caveated result that may be cited only as exploratory.
- **Controlled exploratory**: an analysis with a fixed recorded design whose main estimand the audit did
  not test. Not Frozen.
- **Finite numerical observation**: a measurement on specific saved seeds or horizons, not re-checked by
  the audit and not Frozen.
- **Conjecture / Exploratory**: an open question with no proof or test in the repo (a future untested idea).
- **Not established**: the audit found no support. It is an open question, not a rejection.
- **Speculative / untested origin hypothesis**: the pre-AIEF origin ideas (`SSRH-ORIG-01..07`). They
  were never tested and are not retired (`artifact_status` `Incomplete`).
- **Retired / Superseded**: tested and replaced, or withdrawn (`S01–S18`).
- **Rejected**: tested and failed.
- **Quarantined**: withdrawn because the derivation is invalid. Do not cite (`AUD-SLOWPOLE`;
  `artifact_status` `Rejected`).

`evidence_scope` is a separate axis and is **not** a status. Its allowed values are `Implementation identity`,
`Finite numerical observation`, `Controlled experimental result`, `Conditional theorem`,
`Formalized theorem` and `Conjecture` (see "Axis 2" above).

---

## Registry Files

| File | Rows | Purpose |
|---|---:|---|
| `artifacts.csv` | `2,898` | Complete SHA-256 inventory covering all `2,760` tracked working-tree files at `e47bad15` plus all `138` file entries inside the 3 `.zip` archives, with byte counts, duplicate hash group IDs (`DUP-0001`..`DUP-0360`), lock constraints, and Stage 4 targets. **2026-10-28 tree check (refreshed at `886daf6`):** 2,701 present with the same SHA, 7 present with a changed SHA (5 Lean and .gitignore changes on `main`, plus `Basic.lean` and `Smoke.lean` edited in merge prep, ERRATA E7; the 4 merge-prep doc edits counted earlier were reverted to their pinned bytes, see `ERRATA_2026-10-28.md`), 52 missing (deleted on `main`), 138 zip members present. At the refreshed check (after commit `OPERATING_MANUAL.md`, 2026-10-28), the merged tree had 2,960 tracked files, of which 252 are not inventoried (mostly `AI Agent Audits/` and arena `audits/`). After the 9 CI files were added (commit `e861124`), it is 2,969 tracked and 261 not inventoried (unchanged at `886daf6`). |
| `studies.csv` | `15` (2026-10-28: + `AI_AGENT_AUDITS_2026_10`) | Structured index of all active, foundational, exploratory, and rejected research studies with entrypoints, canonical evidence directories, sample designs, and Stage 4 `studies/<slug>/` destinations. |
| `claims.csv` | `75` (2026-10-28: 43 original + 17 `AUD-*` audit verdicts + `LEAN-R4` + 7 `SSRH-ORIG-*` origin hypotheses + 7 post-push review `AUD-*` rows (local branch `work/post-push-1`); new columns `prior_status`, `audited_status` (one value from "Status vocabulary"), `audited_qualifier` (free text), `audit_source`, `reconciliation_note`, `legacy_list_refs`; built by `reconciliation/build_claims_reconciliation.py`) | Unified claim table uniting active empirical results (`EMP-*`), modular platform identity (`IMPL-MODULAR-01`), Lean 4 formal proof (`LEAN-CF-01`), manuscript Corollary 8.4 caveat (`CAVEAT-MS-8.4`), controller-fiber claims (`CF01`–`CF12`), retired hypotheses (`S01`–`S18`), and methodological rejections (`REJ-*`). |
| `supersessions.csv` | `20` | Directed lineage map (`superseded_target -> authoritative_target`) across code, `.zip` bundles, numbered `01`/`02` folders, and run cohorts. |
| `relocation_map.csv` | `221` | Stage 4 conservative relocation plan across every top-level file, run folder, and package subtree, explicitly marking stationary authority-locked paths (`KEEP_STATIONARY_LOCKED`). **2026-10-28 tree check:** 214 same file count, 3 count changed (`Project Histories`, `Project Origins`, `lean/AIEFProofs/AIEFProofs`), 4 missing (`Papers`, `__pycache__`, `lean/AIEFProofs/.lake`, editor lock file). |
| `lineage_reconciliation.csv` | `32` | 2026-10-28: the audited verdict for every row of the recovered 1.4 lineage claim register (which is hash-pinned and left unedited). |
