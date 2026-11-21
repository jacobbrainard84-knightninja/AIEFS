Researcher: 0046882 (Arena.ai)  
Date/time: 2026-11-21T16:24:58.427532-07:00 MST (host-reported, UNVERIFIED; see CLOCK_NOTE.md)  
main sha: d1cbcf38937b75538100ccaf3115fcbe45a2714f  
Engine sha256: ca4593fda86a1b0a3d450d68b5ce4bddd08583fdb93deaf17db20dd6b1acdede (original) / a69b7943d31542097d1a599accc1c8ba722b0bf6b74d31a20a6dd8538090c830 (instrumented copy)  
Scope: Gate spillover lane, DIRECTION-1  
Status: UNVERIFIED by project seats

# Ran versus read only

## RAN

Environment: Python 3.13.18 (main, Nov  5 2026, 09:37:13) [GCC 14.2.0]; NumPy 2.3.5; Linux-6.1.189+-x86_64-with-glibc2.41.

Working directory: the extracted cycle_002_gate_spillover directory.

```bash
set -o pipefail
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python -u code/measure.py 2>&1 | tee evidence/run.log
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python -u code/crosscheck.py 2>&1 | tee evidence/crosscheck.log
```

The exact seed list is 11242426753702356865, 4619122171158768524, 16329425431442249417, 10431384713483787270. Measure output: evidence/run.log, summary.json, controls.json, configuration.json, environment.json and no_instrumentation.json. Crosscheck output: evidence/crosscheck.log and crosscheck.json. Both commands exited 0. These are new local runs, not copied expected outputs.

Preparation/check commands included `git rev-parse HEAD`, `sha256sum aief_experiment_engine_v1.py`, `git status --short`, source `sed`/`git show`, Python manifest inspection, and creation of external copies. These did not simulate trajectories. Original hash checked before and after; working tree clean. Archive verification is documented in PACKAGE_VALIDATION.md.

## READ ONLY — verbatim source excerpts

### `aief_experiment_engine_v1.py:75-87` @ `d1cbcf38937b75538100ccaf3115fcbe45a2714f`

```text
75: FROZEN_MU = 0.03
76: FROZEN_B_C = 0.12
77: FROZEN_B_INIT_SCALE = 0.0005
78: FROZEN_ZERO_TOL = 1e-12
79: FROZEN_PROJECTION_NORM_TOL = 1e-14
80: FROZEN_GAP_TOL = 1e-9
81: 
82: # Derived from frozen values
83: FROZEN_MEAN_OMEGA = float(np.mean(FROZEN_OMEGA))  # 1.428333...
84: FROZEN_T_STAR = 25.0 / FROZEN_MEAN_OMEGA  # 17.502917152858814
85: FROZEN_T_WINDOW = FROZEN_T_STAR  # 17.502917152858814 (exact, NOT rounded)
86: FROZEN_ALPHA = float(np.exp(-FROZEN_DT / FROZEN_T_WINDOW))
87: FROZEN_CAPACITY = (FROZEN_A - FROZEN_DELTA) / FROZEN_Q
```

### `aief_experiment_engine_v1.py:155-170` @ `d1cbcf38937b75538100ccaf3115fcbe45a2714f`

```text
155:     
156:     @property
157:     def T_star(self) -> float:
158:         """T_* = 25 / mean(omega)"""
159:         return 25.0 / self.mean_omega
160:     
161:     @property
162:     def alpha(self) -> float:
163:         """EMA smoothing factor: exp(-dt / T_window)"""
164:         return float(np.exp(-self.dt / self.T_window))
165:     
166:     @property
167:     def capacity(self) -> float:
168:         """Projection capacity: (a - delta) / q"""
169:         return (self.a - self.delta) / self.q
170:     
```

### `aief_experiment_engine_v1.py:790-816` @ `d1cbcf38937b75538100ccaf3115fcbe45a2714f`

```text
790:     B_unprojected = state.B + config.dt * (
791:         (config.eta + config.mu) * R_driver
792:         - config.mu
793:         - config.gamma * state.B
794:     )
795:     B_unprojected = np.maximum(B_unprojected, 0.0)
796:     B_unprojected = 0.5 * (B_unprojected + B_unprojected.T)
797:     np.fill_diagonal(B_unprojected, 0.0)
798:     
799:     # Projection diagnostics (matching production exactly)
800:     proposed_update_norm = float(np.linalg.norm(B_unprojected - B_previous))
801:     
802:     # Check gap constraint
803:     row_sum_pre = np.sum(B_unprojected, axis=1)
804:     g_min_pre = float(np.min(config.a - config.q * row_sum_pre))
805:     pre_violation = bool(g_min_pre < config.delta)
806:     
807:     # Project if needed
808:     B_projected = B_unprojected
809:     correction_norm = 0.0
810:     if pre_violation:
811:         scale = np.minimum(1.0, config.capacity / (row_sum_pre + config.scale_epsilon))
812:         B_projected = B_unprojected * np.minimum.outer(scale, scale)
813:         np.fill_diagonal(B_projected, 0.0)
814:         correction_norm = float(np.linalg.norm(B_projected - B_unprojected))
815:     
816:     projection_active = bool(correction_norm > FROZEN_PROJECTION_NORM_TOL)
```

### `aief_experiment_engine_v1.py:880-900` @ `d1cbcf38937b75538100ccaf3115fcbe45a2714f`

```text
880:     # Initialize state (uses init_sequence via make_prefix_rng)
881:     state = initialize_state(seed, config)
882:     
883:     # Get RNG for prefix simulation loop
884:     # Production uses unused_rng = default_rng(0) for the advance_state calls
885:     # when shuffle_driver=False
886:     unused_rng = np.random.default_rng(0)
887:     
888:     # Simulate to split point
889:     R_past_sum = np.zeros((N, N), dtype=float)
890:     R_past_count = 0
891:     
892:     burn_end = protocol.burn_end(config)
893:     hist_end = protocol.hist_end(config)
894:     
895:     for step in range(hist_end):
896:         R_physical, _, _ = advance_state(state, config, unused_rng, shuffle_driver=False)
897:         
898:         # P1 #10-11: State validation at transition boundaries
899:         if step == burn_end or step == hist_end - 1:
900:             state.validate(config, step)
```

### `aief_experiment_engine_v1.py:2049-2055` @ `d1cbcf38937b75538100ccaf3115fcbe45a2714f`

```text
2049:         }
2050:     
2051:     # P0 #4: Validate seed/branch authority - seeds and branches must match manifest
2052:     manifest_seeds = [int(x) for x in frozen_manifest["randomization"]["paired_seeds"]]
2053:     manifest_branches = tuple(frozen_manifest["protocol"]["branches"])
2054:     if list(seeds) != manifest_seeds:
2055:         return {
```

### `AIEF_1_4_Twindow_sensitivity.py:866-887` @ `d1cbcf38937b75538100ccaf3115fcbe45a2714f`

```text
866:     config = create_model_config(rho=1.0)
867:     
868:     # For baseline equivalence, we need to validate ALL 7 branches
869:     # to certify the engine as reusable infrastructure
870:     baseline_protocol = engine.ProtocolConfig(
871:         T_sim=FROZEN_T_SIM,
872:         burn_end_time=160.0,
873:         split_time=480.0,
874:         future_duration=320.0,
875:         diagnostic_stride=50,
876:         branches=FROZEN_BRANCH_ORDER,  # All 7 branches for engine certification
877:     )
878:     
879:     # Run the engine's baseline equivalence test with ALL seeds and ALL 7 branches
880:     results = engine.run_baseline_equivalence(
881:         seeds=seeds,
882:         config=config,
883:         protocol=baseline_protocol,
884:         frozen_manifest_path=frozen_manifest_path,
885:         frozen_npz_path=frozen_npz_path,
886:         frozen_csv_path=frozen_csv_path,
887:         branch_order=FROZEN_BRANCH_ORDER,  # Use FULL branch order for RNG namespace
```

### Adjudication read only @ `1fee4b0959e2ddc9b39acb79740966e089dd0cca`

Source: `audit_inbox/Project_Seats/2026-11-20_auditor-seat-002_gate-form-adjudication/ADJUDICATION.md`. Unchanged copy and gate_exact.json supplied. Relevant verbatim lines:

```text
12: - **What I ran:** only my own `gate_exact.py` in this folder (Python 3.13.5, stdlib `fractions`, exact arithmetic, eps = 0). It does not import the engine or any deposited script. Output: `gate_exact.json`.
26: - **W1 (spillover).** Only node 0 is over the cap. Nodes 1 and 2 are under the cap, but their edges to node 0 are still scaled by s_0 = 38/45. Their rows drop from 3/5 to 47/90 and from 7/20 to 14/45. Each of those rows is multiplied by two different factors, {38/45, 1}, so the row's direction changes. Per-cell multiplicative would leave rows 1 and 2 untouched.
27: - **W2 (overshoot).** Nodes 1 and 2 are over the cap (7/10 > 19/30). After the gate their rows land at 209/420 ≈ 0.498, far **below** the cap of 0.633, because their edges to the heavier node 0 take node 0's smaller factor. Per-cell multiplicative would put them exactly at the cap.
28: - The output still touches the boundary. The node with the smallest scale always lands exactly at the cap when eps = 0. This agrees with salvage §3.4 ("interior only at the ε level" refers to the whole output, not to individual rows).
31: **F3. When the loads are equal, the three rules coincide (W3).** On a saturated clique with equal row sums, the gate, the per-cell rule and a single global factor give identical results (s = 19/36). Salvage L137's "effective weight-proportional decay" reading is therefore correct **inside that scope**, which is the saturated, equal-scale regime where the kη/c rates are derived. It is wrong as a general name for the gate.
```

The six briefing documents at the same inbox SHA were read in the preceding review; no scientific findings are inferred from their agent verdicts. Their contents were not executed. The owner-relayed DIRECTION-1 supplies this cycle’s lane and definitions.

## NOT_RUN

- Remaining 36 manifest seeds: excluded by predeclared K=4 pilot, not failures.
- Six intervention futures: out of reference-trajectory scope; full RNG namespace retained.
- Frozen-artifact baseline certification: outside this instrumentation-equivalence task; original-versus-instrumented is not that certification.
- Lean build/axiom audit: no Lean contribution in this lane/cycle.
- Gate replacement, dt sweeps, topology/locking/cumulative-causation experiments: out of scope.
- Deposited adjudication gate_exact.py: never executed. Independent Fraction controls were authored here.
- External timestamp authentication, cross-host floating-point comparison: not available/performed.
