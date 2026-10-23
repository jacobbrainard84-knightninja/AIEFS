# AIEFS Epistemic & Conservation Registries (`registry/`)

This directory provides the machine-verifiable **authoritative status and provenance layer** for every artifact, study, scientific claim, supersession relationship, and planned Stage 4 path relocation in `jacobbrainard84-knightninja/AIEFS`.

All tables in this directory are validated automatically by:

```bash
python3 audits/engineering/verify_inventory.py
```

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
| `Unreviewed` | Reserved for uninspected files (`0` rows in Milestone 1 — all `2,898` worktree + archive entries have been explicitly classified). |

### Axis 2 — `evidence_scope` (Epistemic Strength)

| Value | Definition |
|---|---|
| `Implementation identity` | Exact property of implemented code, deterministic data transformation, equivalence gate, or build configuration. |
| `Finite numerical observation` | Exact replay diagnostic or numerical measurement on specific saved seeds, finite time horizons, or selected tangent directions. |
| `Controlled experimental result` | Multi-seed randomized counterfactual / paired-ablation statistical finding on fixed model protocols (e.g., $N=100$ disjoint AIEF-1.3 cohorts; 40-seed split-state, matched-phase, and 200-condition $T_{\text{window}}$ studies). |
| `Conditional theorem` | Analytic mathematical proof valid strictly under explicit structural hypotheses (e.g., persistent strict winner inequalities, edge-uniform base point $x_G = x_{\text{common}}\mathbf{1}$). |
| `Formalized theorem` | Machine-checked Lean 4 proof with zero `sorry`/`admit` axioms (`ControllerFiber.lean`: $\ker C_{\{2,7\}} = \operatorname{span}\{(1,-1,-1)\}$). |
| `Conjecture` | Open mathematical question or unproved infinite-time asymptotic hypothesis (`CF11`, `CF12`, pre-AIEF SSRH origin hypotheses). |

---

## Registry Files

| File | Rows | Purpose |
|---|---:|---|
| `artifacts.csv` | `2,898` | Complete SHA-256 inventory covering all `2,760` tracked working-tree files at `e47bad15` plus all `138` file entries inside the 3 `.zip` archives, with byte counts, duplicate hash group IDs (`DUP-0001`..`DUP-0360`), lock constraints, and Stage 4 targets. |
| `studies.csv` | `14` | Structured index of all active, foundational, exploratory, and rejected research studies with entrypoints, canonical evidence directories, sample designs, and Stage 4 `studies/<slug>/` destinations. |
| `claims.csv` | `43` | Unified claim table uniting active empirical results (`EMP-*`), modular platform identity (`IMPL-MODULAR-01`), Lean 4 formal proof (`LEAN-CF-01`), manuscript Corollary 8.4 caveat (`CAVEAT-MS-8.4`), controller-fiber claims (`CF01`–`CF12`), retired hypotheses (`S01`–`S18`), and methodological rejections (`REJ-*`). |
| `supersessions.csv` | `20` | Directed lineage map (`superseded_target -> authoritative_target`) across code, `.zip` bundles, numbered `01`/`02` folders, and run cohorts. |
| `relocation_map.csv` | `221` | Stage 4 conservative relocation plan across every top-level file, run folder, and package subtree, explicitly marking stationary authority-locked paths (`KEEP_STATIONARY_LOCKED`). |
