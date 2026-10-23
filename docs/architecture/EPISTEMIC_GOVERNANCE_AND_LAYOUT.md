# AIEFS Epistemic Governance & Conservative Repository Architecture

**Status:** Active Governance Specification (Milestone 1 — Stages 1–3 Complete; Stages 4–7 Planned)

---

## 1. Core Architectural Principles

1. **Zero Deletion Conservation Law:** No historical file, negative experiment, partial run, or superseded script is ever deleted. Every pre-existing tracked file from base commit `e47bad150792425eb8e962ff636c69289eedd8b1` (`2,760` files) and every `.zip` archive member (`138` entries) is permanently indexed by SHA-256 in `registry/artifacts.csv`.
2. **Strict Separation of Organizational Changes from Scientific / Code Edits:** Directory structure, status documentation, and provenance registries never silently alter mathematical logic, numerical constants, or frozen outputs.
3. **Stationary Lock Respect:** Files locked by relative path and SHA-256 digest in `AIEF_1_4_FROZEN_5a9f093a2fe0.authority.lock.json` (`aief_experiment_engine_v1.py`, `AIEF_1_4_Twindow_sensitivity.py`, `AIEF_1_4_Twindow_sensitivity_analysis_v3.py`, `runs/5a9f093a2fe0/*`), manifest-locked sources (`AIEF_1_4_memory_ablation_updated.py`), frozen production run directories (`runs/b57562a8ee77/`, `runs/c3da1ac707bf/`, `runs/73dca37cf93f/`), and Lean hash-locked files (`lean/AIEFProofs/*`) remain stationary at their verified coordinates.
4. **Two-Axis Epistemic Classification (`artifact_status` × `evidence_scope`):** Every artifact, study, and claim independently records **trust/lifecycle status** (`Supported`, `Frozen`, `Exploratory`, `Superseded`, `Rejected`, `Incomplete`) and **epistemic scope** (`Implementation identity`, `Finite numerical observation`, `Controlled experimental result`, `Conditional theorem`, `Formalized theorem`, `Conjecture`).
5. **Quarantined Negative Results Rather Than Silent Erasure:** Scientifically falsified analyses (`Rejected`) preserve their original scripts and outputs byte-for-byte unchanged alongside a neighboring `README.md` explaining the flaw and a machine-readable `provenance.json`.

---

## 2. Target Repository Layout & Stationary Reference Design (Stages 1–7)

```text
AIEFS/
├── README.md                          # Front-door orientation & navigation (Stage 2 - LIVE)
├── CURRENT_STATUS.md                  # What is Supported, Frozen, Exploratory, Conditional, Rejected (Stage 2 - LIVE)
├── REPRODUCING.md                     # Exact commands, runtimes, SHA-256 & libm notes (Stage 2 - LIVE)
├── registry/                          # Machine-verified CSV ledgers (Stage 1/2 - LIVE)
│   ├── README.md
│   ├── artifacts.csv                  # 2,898 SHA-256 entries (2,760 worktree + 138 zip members)
│   ├── studies.csv                    # 14 research studies mapped end-to-end
│   ├── claims.csv                     # 43 claims across empirical, formal, conditional & retired scopes
│   ├── supersessions.csv              # 20 directed replacement edges
│   └── relocation_map.csv             # 221 exact Stage 4 path mappings + lock flags
├── audits/                            # Full forensic, scientific & engineering audits (Stages 2–3 - LIVE)
│   ├── github_reconciliation/         # .zip vs worktree reconciliation + non-destructively unpacked lineage files
│   ├── scientific/                    # Spectral program split, Corollary 8.4 derivation, revalidated CSVs
│   └── engineering/                   # AST path dependencies across 165 .py scripts + verify_inventory.py
├── docs/
│   ├── architecture/                  # Epistemic governance & migration design (Stage 2 - LIVE)
│   ├── synthesis/                     # Stage 4 destination for active synthesis/theorem docs
│   └── manuscripts/                   # Stage 4 destination for draft manuscripts with scope headers
├── history/
│   ├── timeline.md                    # Complete Era 0 -> Era 4 intellectual history (Stage 2 - LIVE)
│   ├── project_histories/             # Stage 4 destination for Project Lead History 01–10 PDFs
│   ├── papers/                        # Stage 4 destination for historical paper drafts
│   └── project_origins/               # Stage 4 destination for pre-AIEF SSRH explorations
├── runs/                              # Stationary frozen run directories (5a9f093a2fe0, b57562a8ee77, c3da1ac707bf, 73dca37cf93f)
├── lean/AIEFProofs/                   # Verified Lean 4 package (ker C_{2,7} = span{(1,-1,-1)})
├── platform/                          # Stage 4 promotion target for modular platform v1 + Analysis v4
├── studies/                           # Stage 5 uniform study entry points referencing stationary frozen assets
│   ├── aief_1_3_disjoint_cohorts/
│   ├── split_state_ablation/
│   ├── matched_phase_ablation/
│   ├── twindow_sensitivity/
│   ├── tangent_cocycle_dynamics/
│   ├── controller_fiber_theory/
│   ├── proposal_equalization/
│   ├── exploratory/
│   └── rejected/                      # Unmodified negative-evidence scripts + README.md + provenance.json
└── archive/                           # Stage 4 destination for superseded code, duplicate zips, caches & partial runs
```

---

## 3. Seven-Stage Conservative Migration Gate Checklist

- [x] **Stage 1 — Complete Hash Inventory (`registry/artifacts.csv`):** All `2,760` worktree files + `138` `.zip` members hashed (`SHA-256`) and classified (`Unreviewed = 0`).
- [x] **Stage 2 — Authoritative Status Layer & Reconciliation:** `README.md`, `CURRENT_STATUS.md`, `REPRODUCING.md`, `history/timeline.md`, `registry/*.csv`, `audits/github_reconciliation/*`, and `audits/scientific/*` authored and verified.
- [x] **Stage 3 — Engineering & Lock Dependency Audit:** AST scan of all `165` `.py` files, live `verify_authority_lock()`, live `pytest` (`41 passed`), live `AIEF-1.3 N=100` & `Analysis v4` revalidations, and cross-`glibc` floating-point audit complete. **Zero existing files touched (`M=0, D=0, R=0`).**
- [ ] **Stage 4 — Safe Non-Breaking Relocation (`Milestone 2`):** Relocate unlocked files per `registry/relocation_map.csv` while keeping all `authority.py`-locked and `manifest.json`-locked files stationary at root/`runs/`.
- [ ] **Stage 5 — Uniform `studies/<slug>/` Entry Points & Rejected Quarantine (`Milestone 2`):** Add standardized `README.md`, `run_reproduce.sh` / wrapper entrypoints, and `provenance.json` across active and rejected study directories.
- [ ] **Stage 6 — Post-Move Byte Conservation Verification (`Milestone 2`):** Confirm the multiset of `(sha256, size_bytes)` across all `2,760` pre-existing tracked files is **100% conserved** (`0` bytes lost, `verify_authority_lock()` green).
- [ ] **Stage 7 — Root GitHub Actions CI & Pull Request (`Milestone 2`):** Wire `.github/workflows/ci.yml` running conservation checks, `pytest`, `Analysis v4`, `AIEF-1.3 N=100` stats, cross-libm gate, and Lean 4 `lake build` (`lean/AIEFProofs`), then open review PR.
