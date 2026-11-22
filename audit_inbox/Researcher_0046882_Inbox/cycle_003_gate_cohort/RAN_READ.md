Researcher: 0046882 (Arena.ai)  
Date/time: 2026-11-22T03:01:39.733080-07:00 (host-reported MST; not authenticated)  
main sha: d1cbcf38937b75538100ccaf3115fcbe45a2714f  
Engine sha256: ca4593fda86a1b0a3d450d68b5ce4bddd08583fdb93deaf17db20dd6b1acdede (original) / a69b7943d31542097d1a599accc1c8ba722b0bf6b74d31a20a6dd8538090c830 (copy)  
Scope: Gate spillover lane, DIRECTION-2; full 40-seed reference cohort  
Status: UNVERIFIED by project seats

# Ran / read only / NOT_RUN

## RAN

Python: 3.13.18 (main, Nov  5 2026, 09:37:13) [GCC 14.2.0]. NumPy: 2.3.5. Platform: Linux-6.1.189+-x86_64-with-glibc2.41.

Working directory: this extracted cycle directory. Exact measurement commands:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python -u code/run_cohort.py 2>&1 | tee evidence/run.log.txt
# Above was interrupted; log preserved as evidence/attempt1.log.txt.
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python -u code/resume_cohort.py > evidence/recovery.log.txt 2>&1
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python -u code/validate_saved.py > evidence/validation.log.txt 2>&1
```

Recovery ran through the background-process tool and exited0. Validation exited0. Exact seeds are in PROTOCOL.md / METADATA.json. Raw log files, initial failure, completed counts and environment are deposited. First26 durable records were checked during recovery; remaining 14 were simulated. First seed original/instrumented was rerun. None of this is a second independent simulation by another agent.

## READ ONLY

Owner-relayed DIRECTION-2 gives the acceptance verdict on Cycle002; it is treated as the project lead’s report, not work independently performed here. Existing baseline source is reused at its verified hash; current main was not silently substituted. The previous adjudication scripts were not executed. The unchanged baseline engine was both read and executed as described above; verbatim relevant excerpts follow.

### aief_experiment_engine_v1.py:75-87 @ d1cbcf38937b75538100ccaf3115fcbe45a2714f

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

### aief_experiment_engine_v1.py:155-170 @ d1cbcf38937b75538100ccaf3115fcbe45a2714f

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

### aief_experiment_engine_v1.py:790-816 @ d1cbcf38937b75538100ccaf3115fcbe45a2714f

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

### aief_experiment_engine_v1.py:880-900 @ d1cbcf38937b75538100ccaf3115fcbe45a2714f

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

### aief_experiment_engine_v1.py:2049-2055 @ d1cbcf38937b75538100ccaf3115fcbe45a2714f

```text
2049:         }
2050:     
2051:     # P0 #4: Validate seed/branch authority - seeds and branches must match manifest
2052:     manifest_seeds = [int(x) for x in frozen_manifest["randomization"]["paired_seeds"]]
2053:     manifest_branches = tuple(frozen_manifest["protocol"]["branches"])
2054:     if list(seeds) != manifest_seeds:
2055:         return {
```

## NOT_RUN

- Other intervention branches, parameter sweeps, gate redesign, cumulative-impact experiments: out of scope.
- Lean builds, proof changes, full registry-claim reproduction, self-test census: other lanes, not this task.
- Cross-host replay and externally authenticated timestamp: not performed.
- Independent full40 simulation by a second implementation: not claimed. Local validation recomputes metrics from saved raw arrays.
- Intermediate state-stream digests for recovered seeds 2–26: not durably saved by interrupted attempt, explicitly unavailable; raw observation hashes retained.
- Durable upload of full40 raw NPZ: omitted under predeclared permitted fallback because persistence limit is insufficient. Compact descriptors and240 hashes are delivered.
