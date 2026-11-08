# AIEFS north-star review — current main, scientific priorities, and evidence gaps

- **Agent / model:** GPT-6
- **Date:** 2026-11-08 (Europe/Tirane, UTC+1)
- **Repository commit reviewed:** `main@eb3933c196ee19e80e1621ae80d89ca72e6d9485`
- **Scope:** Current README, status/errata, claims and study registries, numerical audit outputs, modular-platform tests, CI workflows, Lean project status, the current recursive Git tree, and the audit-inbox briefing/priority instructions.
- **Review type:** Static repository review and structured-result inspection. No project tests, CI workflows, Lean builds, numerical simulations, memory benchmarks, or red-team mutations were executed in this pass.
- **Status:** UNVERIFIED INPUT. This note is not a claim, erratum, audit verdict, or approval. Researcher 001 / Auditor Seat 002 should independently triage every point.

## 1. Executive assessment

The mathematical direction in the current project is coherent with the stated north star: a machine-checked reference library for the *actual* delayed adaptive oscillator dynamics, with finite maps and their hypotheses formalized before delay asymptotics. The largest remaining weakness is the bridge between conditional finite-dimensional identities and the coupled phase/EMA/weight dynamics, not the existence of supporting incidence-matrix lemmas.

This review also corrects the priority order in my preceding conversational evaluation. The audit-inbox briefing explicitly says that items 12–13 (modular oracle closure and registry entrypoint integrity) precede the rate-law step-size study and any new simulations. I did not respect that ordering in the first conversational recommendation. The next work should follow the briefing's order.

The current main head is `eb3933c196ee19e80e1621ae80d89ca72e6d9485`. PRs #9–#12 are already merged at this head; the `audit-inbox` branch is an older, separate intake branch and must not be merged wholesale.

## 2. Release-critical findings

### F1 — Eleven `canonical_entrypoints` tokens remain unresolved

**Finding (static check against current main):** `registry/studies.csv` contains 11 entrypoint tokens in five study rows for which no matching tracked basename/path exists in the recursive Git tree at `main@eb3933c196ee19e80e1621ae80d89ca72e6d9485` (3,213 tree entries; recursive tree was not truncated). This reproduces the *count and same five study rows* from the older briefing, but the current-tree check was run independently at the newer main commit.

| `registry/studies.csv` line | Study row | Unresolved tokens |
|---:|---|---|
| 3 | `AIEF_1_0_TO_1_2_FOUNDATIONAL` | `AIEF_1_0_*.py`; `AIEF_1_1_*.py`; `AIEF_1_2_*.py` |
| 5 | `AIEF_1_3_DISJOINT_100SEED` | `AIEF_1_3_sensitivity_audit_updated.py`; `AIEF_1_3_persistence_mechanism_test_updated.py` |
| 7 | `AIEF_1_4_MATCHED_PHASE_ABLATION` | `AIEF_1_4_driver_mechanism.py` |
| 10 | `AIEF_1_4_TANGENT_AND_COCYCLE` | `aief_1_4_full_state_tangent_operator.py`; `aief_1_4_history_cocycle_test.py`; `aief_1_4_branch_tangent_comparison.py` |
| 12 | `AIEF_1_4_CONTROLLER_FIBER` | `aief_1_4_intertwining_controller.py`; `aief_1_4_fiber_coordinate_controller.py` |

Sources: `registry/studies.csv:1-12` (blob SHA `86a39aeaff94502cb8a549da50be4205f8a1d454`); current main commit above. The briefing's older report is `audit_inbox/briefing/OPEN_QUESTIONS.md:67` (SHA `6c72ebbd786865bcae7bdc57a70f02470d347c81`).

A GitHub code search for `canonical_entrypoints` returned the registry CSV, not a validator. The current root repository workflow `.github/workflows/repo-checks.yml` (SHA `f8c96af3de08be9acb0c627a673bb998dab99dd0`, lines 1–202) contains registry lint, pins, inventory, modes and analysis jobs but no study-entrypoint resolution check. This finding is directly in the current-main tree, not merely an inherited briefing lead.

**Recommended handling:** add a deterministic validator that parses the actual CSV schema and resolves every token under an explicit policy. Wildcards should be expanded by a defined glob policy; root-relative and basename-only resolution should not be guessed. Missing legacy scripts should be explicitly classified (e.g. `historical_missing`, `planned`, or `alias_of:<path>`) rather than silently accepted. Add both positive and negative controls and make it a required CI check.

### F2 — The modular oracle test still skips in the default CI invocation

The full oracle-equivalence test obtains its candidate run only from `AIEF_MODULAR_RUN`; when that value is absent or the directory is unavailable, it calls `pytest.skip`. See `AIEF_Experiments/aief_modular_platform_v1_analysis_v4/tests_modular/test_twindow_oracle_equivalence.py:12-20` (SHA `befa41e25fae952a830909ba6d1313b88af56945`).

The current workflow runs `tests_modular` without setting `AIEF_MODULAR_RUN` or `AIEF_TWINDOW_ORACLE`: `.github/workflows/repo-checks.yml:195-201` (SHA `f8c96af3de08be9acb0c627a673bb998dab99dd0`). Its comment itself expects two skipped tests, including `AUD-MODULAR-ORACLE`. The current status document correctly says the platform is not oracle-certified by repository tests at `CURRENT_STATUS.md:140-141` (SHA `c51401924a2179ce87eaf107b01515e2d3f4e37f`).

This is not evidence that the implementation identity is false; it means the repository CI does not yet supply a durable full-oracle certificate. The `IMPL-MODULAR-01` registry row also says the implementation identity was not re-tested by the audit: `registry/claims.csv:7` (SHA `d8af0b5e4c04dd1c55c88f26cca433f97db58146`).

**Recommended handling:** run an explicit, controlled S01 candidate into a fresh output directory with the frozen oracle supplied; capture the exact command, source/input hashes and complete comparison result; make the test fail (not skip) in the certification job when the required authorities are expected to be available. Keep freezeability, implementation identity, and oracle certification as distinct statuses.

### F3 — The documented driver invocation defect is narrowed, not fixed in code

PR #12 has landed the R026 cleanup. The current unpinned erratum E16 gives working invocations with the repository root on `PYTHONPATH`, and the new test verifies those workarounds. However, the hash-pinned driver remains unchanged and the bare invocations remain strict expected failures.

Sources:
- `AIEF_Experiments/aief_modular_platform_v1_analysis_v4/README_modular.md:11-12` (SHA `5e32a00736555461b26caf66480bde14bb3d9040`) still shows the bare invocations.
- `ERRATA_2026-10-28.md:429-447` (SHA `d37558fa77a3724e608754069c45224c593372bc`) explains the failure, the workaround and that a `sys.path` fix remains an owner decision.
- `tests_modular/test_driver_cli_invocation.py:3-10, 58-61` (SHA `e8a1010247311f7c311e83151c6439065b2121ae`) records the workaround and strict xfail for the bare command.
- The default CI count still includes two xfails: `.github/workflows/repo-checks.yml:195-201`.

Treat this as a known, explicitly documented limitation with a working workaround, not as a repaired CLI. A source-level fix would require a new reviewed pin for ART-0064 and corresponding treatment of the pinned documentation.

### F4 — `check_modes.py` still buffers the full `git cat-file --batch` payload

The current `shebang_objects` implementation passes all regular blob IDs to `git cat-file --batch` with `capture_output=True`, then retains `proc.stdout` as `data` while scanning only the first two bytes of each blob. See `tools/ci/check_modes.py:101-116`, especially lines 107-109 (SHA `6a3b054037152f459ced2e96aafacd18d2e28e18`). The CI workflow invokes the check in the file-mode job: `.github/workflows/repo-checks.yml:149-150` (SHA `f8c96af3de08be9acb0c627a673bb998dab99dd0`).

This is a static confirmation of the unbounded-output design. I did **not** repeat the earlier peak-RSS measurement or reproduce exit 137. The briefing records a prior measurement around 2.4 GiB, but that measurement is not my own: `audit_inbox/briefing/OPEN_QUESTIONS.md:69` (SHA `6c72ebbd786865bcae7bdc57a70f02470d347c81`).

**Recommended handling:** stream the batch protocol and retain only headers plus a two-byte prefix per blob, or use a design that avoids reading all blob contents into a single in-memory buffer. Add a scale test that verifies bounded memory behavior on a repository-sized synthetic fixture.

### F5 — Manifest trust-root gap G2c remains documented and outside CI red-team

The current red-team catalogue records a concrete known-false input that is accepted: a re-pinned stub verifier can print the manifest-computed success line plus `OK` while a published file is tampered. The manifest is not pinned outside itself. See `tools/redteam/REDTEAM.md:100` and `:368-376` (SHA `3c56a8f4b41741fe96b7c6377d8ca0929747faef`).

The same document says the red-team suite is not in CI discovery: `tools/redteam/REDTEAM.md:28-31`. This review did not independently execute the G2c mutation. The status here is therefore: **known documented checker gap; not newly reproduced in this pass**.

**Recommended handling:** anchor the verifier and manifest to a trust root outside the self-referential manifest (e.g. a separately pinned bootstrap/checker constant or an independently pinned registry row), then convert the G2c expected failure into an ordinary negative-control test. Merely enabling the existing suite before the vulnerability is fixed would make the known gap visible, but not close it.

## 3. Current scientific findings and precise rate-law target

### F6 — The E5 rate-law outlier is now precisely identified

The current committed component record identifies the same single outlier described by E5:

- seed: `4619122171158768524`
- `rho = 1.0`, `T_w = 17.50291715`
- component nodes: `[2, 7, 11]` (K3)
- controlling set: `J = [2, 7]`; one-dimensional two-sided controller fiber
- perturbation: `delta = 1.062225811e-9`
- largest tied-scale gap on J: `2.422062551e-12`
- minimum untied gap: `4.65852409e-7`; both separation ratios are about `438.56`
- measured fiber multiplier: `0.9987382673`; state-formula multiplier about `0.998738247`
- relative multiplier error against the state formula: `2.038720579e-8`
- fiber response relative residual: `4.272342519e-8`
- measured `kappa_fiber = 0.06911959994`; closed-form `kappa = 0.06912167133`

Source: `AI Agent Audits/evidence/results/kappa_cycle_kernel.json:1` (SHA `a4536fb7913317d0073dc201e1a5a5c840b51559`; the JSON is stored on one line). The aggregate census independently records the maximum in the 264 resolved two-sided fibers: `AI Agent Audits/evidence/results/rate_law_census_r4.json:42-50` (SHA `1707319aaa09da27dbe488597c6d8a010e09bd6f`). The current claim is `registry/claims.csv:50` (SHA `d8af0b5e4c04dd1c55c88f26cca433f97db58146`), and the prior independent residual split is recorded in `ERRATA_2026-10-28.md:101-106` (SHA `d37558fa77a3724e608754069c45224c593372bc`).

This resolves the target-selection ambiguity in the earlier proposed Issue #14 protocol: the component is the exceptional seed's two-sided K3, not an all-tied K3 ray. Its delta is small, but the saved separation ratios exceed 100, so it is in the census's resolved class. The 32 poorly resolved components are a separate population (all at `rho = 2.0`, maximum relative multiplier error about `4.79e-6`); the 110 all-tied K3 components are a third class with one-sided rays, not two-sided fibers. See `rate_law_census_r4.json:15-57` and `kappa_cycle_kernel_summary.json:1` (latter SHA to be read from main when triaging).

No perturbation-size sweep was run in this review. The discrepancy remains **unexplained**, exactly as E5 states. The sweep should use this exact frozen replay/component, hold the base state and branch assumptions fixed, evaluate +h and -h separately, and report branch-crossing samples rather than fitting through them.

## 4. Status-document and Lean-CI reconciliation

Several current-main status statements lag the merged repository:

- `CURRENT_STATUS.md` still says `Last Verified: 2026-10-23` at line 3 and describes a local, unpushed `2026-10-28` state at lines 5 and 81-84 (SHA `c51401924a2179ce87eaf107b01515e2d3f4e37f`). It also still describes freezing/Lean work as a research-branch/local item at lines 127 and 190.
- The current required Lean matrix contains **AIEFProofs, AIEFProofsKn and AIEFFreezeCore**: `.github/workflows/lean.yml:48-49` (SHA `a993b9fe8d2f7648a615e419b9fcb31920f9ab8a`).
- The still-current `lean/AIEFProofsKn/README.md` says the package is on `research/lean-kn` at line 5 and that it is not yet in CI at lines 79-80 (SHA `d862fe206d91413bffd247f72ab8ae237cf9a775`). The latter is now false. The first line's independent-audit caveat should not be removed merely because CI builds it: CI inclusion is not the same as an independent mathematical audit.
- The older `audit-inbox/briefing/STATE.md` and `NORTH_STAR.md` are navigation snapshots and were read as required; their branch tables are explicitly marked not-live / dated. Do not let them override current main.

**Recommended handling:** reconcile these unpinned status/README passages through a normal reviewed branch, explicitly separating (a) merged into main, (b) required in CI, and (c) independently audited. Do not edit pinned historical documents in place.

## 5. Prioritised next steps

The audit-inbox priority ordering should govern sequencing:

1. Resolve the 11 current `studies.csv` entrypoint tokens and put that validation into CI (F1).
2. Run the modular S01 candidate against the frozen oracle, capture a durable full-equivalence result, and make the certification job fail rather than silently skip when it is expected to run (F2). Preserve the driver workaround/fix decision separately (F3).
3. Reduce `check_modes.py` memory to bounded streaming and add a scale regression test (F4).
4. Close the G2c trust-root gap and promote the negative control into CI (F5).
5. Then run the exact step-size sweep on the E5 target component (F6), keeping the 32 near-tie cases and 110 one-sided K3 rays analytically separate.
6. Continue the formal dependency chain from `audit_inbox/briefing/NORTH_STAR.md`: finite gate definition/idempotence; piecewise-linear/branch conditions; tied-K3 one-sided identity; clique scalar gate multiplier; finite recurrences; exact delay/history buffer; only then delayed quotient and asymptotic stability.
7. Replicate the exceptional AIEF-1.4 operator/controller/cocycle analysis across preselected seeds without treating components or rho conditions as independent seeds. Keep O1 (closed-loop phase-locking with margin), CF11/CF12 (proposal-difference convergence and infinite-time branch persistence), and novelty as open until tested.

The step-size precedence is explicitly stated in `audit_inbox/briefing/OPEN_QUESTIONS.md:59-68` (SHA `6c72ebbd786865bcae7bdc57a70f02470d347c81`): items 12–13 precede item 2. This pass independently checked current F1 and F2 evidence; it did not complete the full v4.1 audit or a real S01 v4.1 run.

## 6. What was and was not done

**Read / statically checked:** current-main files and blob SHAs listed above; recursive tree at the reviewed main commit (3,213 entries, not truncated); the exact E5 component record; current modular oracle skip path and workflow invocation; current study-entrypoint resolution; current Lean matrix; red-team gap documentation; and `check_modes.py` buffer design.

**Not run:** `pytest`, `unittest`, any CI workflow, Lean builds/axiom audits, S01 full-oracle run, v4.1 real-trajectory analysis, check_modes RSS benchmark, G2c mutation, rate-law perturbation sweep, or multi-seed operator/cocycle replication.

No frozen data, hash-pinned production code, audit evidence, registry, errata, or another agent's inbox note was changed. This file is a review deposit only. No finding here is promoted or approved.
