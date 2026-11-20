# Researcher040282 ·012 — causal EMA tracking of moving delayed phasors

**One bounded North-Star component bridge. Submitter-local evidence, not
independent seat review, installed library or full coupled locking.**

Prepared2026-09-04 Atlantic/Reykjavik session label. Repository/owner November
labels and runtime build timestamps are recorded separately. This Continue
only authorizes012; no013selection/preregistration/setup/test or remote action.

## 1 · Main result: input motion is not contracted away

The actual coherence update consumes the OLD input:

C_(n+1)=alpha*C_n+(1-alpha)*z_n.

Set e_n=C_n-z_n. The exact causal identity is

**e_(n+1)=alpha*e_n-(z_(n+1)-z_n).**

The input-motion coefficient is **1**, not alpha or1-alpha. Source post-update
error relative to the CONSUMED input is different:
C_(n+1)-z_n=alpha*e_n. Confusing these two errors silently applies a fixed-input
contraction theorem to a moving input.

For alpha>=0 and arbitrary complex C0/sequence z, define

B(alpha,E0,a,n)=alpha^n*E0+sum_(k<n)alpha^(n-1-k)*a_k.

New Lean proof gives

**||C_n-z_n|| <= B(alpha,||C0-z0||,k->||z_(k+1)-z_k||,n).**

The freshest variation has weight1. Both the initial error and chronological
weights matter. Definition-level composition with004EMA and011/010wrapped delay
input gives

**||C_n-z_n|| <= B(alpha,||C0-z0||,k->|u_(k,i)-L_(k,j)|,n),**

where z_k uses actual-shaped current-minus-oldest-minus-pair-mean-frequency offset,
L_kj=0 for k<D, otherwise u_(k-D,j), and phase x_(k+1)=wrap(x_k+u_k).
Source u uses NEW gated B and old delayed-current sine. Constant startup is not
an invented drifting negative-time extension.

Three NEW named declarations actually compiled;28prior named dependencies
(22EMA+3history+3phase) explicitly recompiled, NOT28new labels. Complete standard
propext/Classical.choice/Quot.sound footprints, no final main warnings/errors/
sorry/native_decide/added axioms. Arbitrary input motion and feedback-capable
increments, no locking/convergence conclusion hidden in a premise.

**Why this advances the North Star:**004fixed/shared-input EMA facts and011phase
increments now genuinely compose in one checked module. It is standard linear-
filter/convolution mathematics at a source-faithful interface, not a new physical
discovery or a source defect/repair. Finite bounds do not prove closed-loop
phase synchronization, sharp future drive bands or topology freezing.

Local ledger after actual closure: **126 unique rows / 103 LEAN_COMPILED labels**. Prior122rows/100formal labels
preserved,3scoped compiled rows+1finite contract appended. Labels describe local
proof evidence, not integration into main or independent approval.

## 2 · The endpoint that must not disappear in translation

The finite theorem needs only alpha>=0, not alpha<1, and divides by no1-alpha.
Abstract alpha0/1 are handled. Source validation requires0<alpha<=1: abstract0 is
NOT a valid source configuration; float1 CAN occur by rounding.

Synthetic dt.125,Twindow1e20 gives **actual source alpha=1**. N1,D2,C0=.3+.4i:
C stays **exactly unchanged for all10tested updates**; stationary-tail input is
near1 and final observed error is0.8062257748298549. The ideal exact-real theorem
physicalAlpha(dt,Tw)<1 for positive dt/Tw does not certify the rounded coefficient.
Do not infer strict contraction or asymptotic tracking from float alpha<=1.
This is a deliberately extreme synthetic boundary, not a finding about frozen
production cohorts or an infinite-time floating trajectory result.

At beta=1-alpha=0, C innovation cannot reveal the consumed input. Dividing
(Cnew-alpha*Cold)/beta would be undefined. We explicitly separate:

-360coordinates: input reconstructed from copied actual pre-state arguments AND
  independently checked against ACTUAL decoded C innovations, beta>=.05;
-10alpha1coordinates: argument-formula input only, NOT called decoded or directly
  returned by the source; exact C-unchanged/state/error checks still run.

No hidden fallback, denominator clamp, skipped test or credit for unobservable
innovation. Nine methods run and pass,0failures/errors/skips.

Two alpha<1N1stationary-tail observations agree with conditional geometric decay:
matched-start tail error0.2964698721901245->0.06615137006096694;
fast tail0.17834921530308442->2.007056014602578e-08. These are finite checks on
prescribed/free-drift inputs, not a coupled-locking result.

## 3 · Actual engine and independent finite protocol

Entire current reviewed Frozen ART-0702 engine imported unchanged, not extracted
functions or a replacement clone. No source/cache/frozen/registry/lock edit. All
six full expected trajectories AND370derived error/budget/unroll cells computed
with pure math/cmath BEFORE acquired module import. Scalar expected history
never comes from target output. Analytic max(0,n-D) lag, actual-shaped offset,
expected NEW gated-B increments and chronological convolution fixed in PLAN.

Manual synthetic initial states, not a claim the production random initializer
returns them. No initialize_state, run_seed, simulate_*, baseline-equivalence,
shuffle/intervention, genuine S01, CLI, writer or certificate call. Source order:
oldtheta/history ->directed C update ->magnitude then symmetric R/diag0 ->B Euler/
clip/symmetry ->conditional capacity gate/post-gap check ->phase NEW gated B
with sin(delayed_j-current_i) ->modulo ->append COPY/pop. No pre-call compute_R.

Each accepted normal/-O suite:

-9/9methods pass,6traces/60actual advances/0initializers;
-370current tracking cells n0..9 and370consumed-input post-errors;
-333adjacent causal recurrences n0..8=115startup+218live,37first-live n=D;
-240offdiag reported-R bounds/130exact diagonal zeros;
-360decoded innovations+10explicit alpha1formula-only inputs;
-max source/scalar component9.992007221626409e-16;
-max causal and complex-unroll residual4.440892098500626e-16;
-max consumed-error residual2.220446049250313e-16;
-fixed abs5e-13/rel0; no post-target tolerance or witness tuning;
-245nonzero tracking bounds<2 and12tight nonzero reported-R bounds<1;
-3first-step active gates,21positive/11negative winding events,
 20multiple-turn events (overlapping counts);
-10intended wrong models per mode, minimum fixed witness0.0033444335669670783,
 0setup errors credited.

Ten calls expose z0..z9 plus C0..C10. We compare e_n only n0..9; no invented
C10-z10/e1..e10tracking observations. R returned is reportedR(C_(n+1)); consumed
post-error uses z_n. Alpha1argument reconstruction is not source innovation data.
Other source fields C/B/theta/history/R, explicit finite shapes/real-imag parts,
exact bools, ranges/Bstructure, copy ownership and unchanged RNG are also checked.
Relational observed-error equations are ADDITIONALLY compared with independent
precomputed predictions, not used as the sole oracle.

### Observed complete runner record

```json
{
  "science": {
    "tested_main": "543e7e1aaa11e4c810783806cb180eee36ec5313",
    "source_contract_methods_each_mode": 9,
    "source_passes_each_mode": 9,
    "source_failures_errors_skips_each_mode": [
      0,
      0,
      0
    ],
    "actual_advances_each_common_mode": 60,
    "initializer_calls_each_common_mode": 0,
    "synthetic_traces_each_mode": 6,
    "current_tracking_coordinates_each_mode": 370,
    "consumed_input_coordinates_each_mode": 370,
    "adjacent_causal_coordinates_each_mode": 333,
    "startup_adjacent_coordinates_each_mode": 115,
    "live_adjacent_coordinates_each_mode": 218,
    "first_live_coordinates_each_mode": 37,
    "decoded_C_innovation_coordinates_each_mode": 360,
    "alpha1_formula_only_input_coordinates_each_mode": 10,
    "reported_R_offdiag_bounds_each_mode": 240,
    "reported_R_exact_diagonal_zeros_each_mode": 130,
    "maximum_observed_component_error": 9.992007221626409e-16,
    "tracking_stats": {
      "adjacent_causal_coordinates": 333,
      "maximum_causal_component_residual": 4.440892098500626e-16,
      "tracking_coordinates": 370,
      "maximum_unroll_component_residual": 4.440892098500626e-16,
      "nonzero_tracking_bounds_below_two": 245,
      "maximum_one_sided_input_budget_excess": 0.0,
      "consumed_input_coordinates": 370,
      "maximum_consumed_component_residual": 2.220446049250313e-16,
      "startup_adjacent_coordinates": 115,
      "live_adjacent_coordinates": 218,
      "first_live_coordinates": 37,
      "alpha_less_one_stationary_tails": [
        {
          "case": "matched_start_N1_D3",
          "first_tail_error": 0.2964698721901245,
          "last_tail_error": 0.06615137006096694
        },
        {
          "case": "fast_tail_N1_D1",
          "first_tail_error": 0.17834921530308442,
          "last_tail_error": 2.007056014602578e-08
        }
      ],
      "rounded_alpha1_tail_error": 0.8062257748298549,
      "alpha1_C_exactly_constant": true,
      "alpha1_not_strict_contraction": true,
      "reported_R_offdiag_bound_coordinates": 240,
      "reported_R_exact_diag_coordinates": 130,
      "tight_nonzero_reported_R_bounds_below_one": 12,
      "maximum_one_sided_R_bound_excess": 0.0,
      "decoded_C_innovation_coordinates": 360,
      "alpha1_formula_only_input_coordinates": 10,
      "first_active_gate_cases": 3,
      "positive_windings": 21,
      "negative_windings": 11,
      "multiple_turn_windings": 20,
      "beta0_divisions": 0,
      "source_alpha0_configs": 0
    },
    "absolute_tolerance": 5e-13,
    "relative_tolerance": 0.0,
    "wrong_models_detected_each_mode": 10,
    "setup_errors_credited_as_detections": 0,
    "normal_optimized_nontiming_results_match": true,
    "new_named_Lean_declarations_actually_compiled": 3,
    "reused_named_declarations_recompiled_not_new_labels": 28,
    "formal_controls": 8,
    "formal_positive_controls": 2,
    "formal_false_math_controls": 3,
    "formal_compiling_integrity_controls": 3,
    "axiom_footprints": {
      "Researcher040282.Tracking.tracking_error_step": [
        "Classical.choice",
        "Quot.sound",
        "propext"
      ],
      "Researcher040282.Tracking.tracking_error_budget": [
        "Classical.choice",
        "Quot.sound",
        "propext"
      ],
      "Researcher040282.Tracking.delayed_phase_tracking_budget": [
        "Classical.choice",
        "Quot.sound",
        "propext"
      ]
    },
    "targeted_Mathlib_used": true,
    "reviewed_public_engine_unchanged": 1,
    "reviewed_metadata_unchanged": 3,
    "actual_engine_import_no_copied_replaced_or_edited_source_functions": true,
    "no_source_repair_or_failing_before_claim": true,
    "alpha1_no_division_or_strict_contraction_assumption": true,
    "all_preregistered_acceptance_conditions_met": true
  },
  "environment": {
    "python": "3.13.16 (main, Oct  6 2026, 04:38:44) [GCC 14.2.0]",
    "numpy": "2.3.5",
    "compiler": "Lean (version 4.33.1, x86_64-unknown-linux-gnu, commit 819816b2e0a3bf405af45ae5c7af2491d8f5bee6, Release)",
    "mathlib_revision": "0df444a360eaa60ab8c11dca51a86af692955474"
  },
  "elapsed_seconds": 554.1702804020001,
  "formal_elapsed_seconds": 551.9822740479999,
  "scope": "Exact-real causal error/finite convolution composed with phase input; finite intact-engine trajectories including rounded alpha1. Not floating FFI/full coupled locking, sharp future bands, production/S01/baseline/CLI/certificate, installed library or independent review."
}
```


### Actual same nine common methods — normal-mode log

```text
test_01_six_full_independent_traces (__main__.suite.<locals>.TrackingContract.test_01_six_full_independent_traces) ... ok
test_02_exact_causal_tracking_error (__main__.suite.<locals>.TrackingContract.test_02_exact_causal_tracking_error) ... ok
test_03_complex_unroll_and_two_budgets (__main__.suite.<locals>.TrackingContract.test_03_complex_unroll_and_two_budgets) ... ok
test_04_consumed_input_is_not_next_input (__main__.suite.<locals>.TrackingContract.test_04_consumed_input_is_not_next_input) ... ok
test_05_startup_and_first_live_phase_budget (__main__.suite.<locals>.TrackingContract.test_05_startup_and_first_live_phase_budget) ... ok
test_06_constant_input_tail_and_alpha1 (__main__.suite.<locals>.TrackingContract.test_06_constant_input_tail_and_alpha1) ... ok
test_07_reported_R_is_after_C_and_enveloped (__main__.suite.<locals>.TrackingContract.test_07_reported_R_is_after_C_and_enveloped) ... ok
test_08_nonzero_C_gate_windings_and_decoder_channels (__main__.suite.<locals>.TrackingContract.test_08_nonzero_C_gate_windings_and_decoder_channels) ... ok
test_09_counts_preservation_and_no_extra_source_calls (__main__.suite.<locals>.TrackingContract.test_09_counts_preservation_and_no_extra_source_calls) ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.153s

OK
{
  "kind": "common",
  "optimized_python": false,
  "tests_run": 9,
  "failures": 0,
  "errors": 0,
  "skipped": 0,
  "actual_engine_advances": 60,
  "source_initializations": 0,
  "source_cases": 6,
  "precomputed_tracking_cells": 370,
  "maximum_component_error": 9.992007221626409e-16,
  "tracking_stats": {
    "adjacent_causal_coordinates": 333,
    "maximum_causal_component_residual": 4.440892098500626e-16,
    "tracking_coordinates": 370,
    "maximum_unroll_component_residual": 4.440892098500626e-16,
    "nonzero_tracking_bounds_below_two": 245,
    "maximum_one_sided_input_budget_excess": 0.0,
    "consumed_input_coordinates": 370,
    "maximum_consumed_component_residual": 2.220446049250313e-16,
    "startup_adjacent_coordinates": 115,
    "live_adjacent_coordinates": 218,
    "first_live_coordinates": 37,
    "alpha_less_one_stationary_tails": [
      {
        "case": "matched_start_N1_D3",
        "first_tail_error": 0.2964698721901245,
        "last_tail_error": 0.06615137006096694
      },
      {
        "case": "fast_tail_N1_D1",
        "first_tail_error": 0.17834921530308442,
        "last_tail_error": 2.007056014602578e-08
      }
    ],
    "rounded_alpha1_tail_error": 0.8062257748298549,
    "alpha1_C_exactly_constant": true,
    "alpha1_not_strict_contraction": true,
    "reported_R_offdiag_bound_coordinates": 240,
    "reported_R_exact_diag_coordinates": 130,
    "tight_nonzero_reported_R_bounds_below_one": 12,
    "maximum_one_sided_R_bound_excess": 0.0,
    "decoded_C_innovation_coordinates": 360,
    "alpha1_formula_only_input_coordinates": 10,
    "first_active_gate_cases": 3,
    "positive_windings": 21,
    "negative_windings": 11,
    "multiple_turn_windings": 20,
    "beta0_divisions": 0,
    "source_alpha0_configs": 0
  },
  "absolute_tolerance": 5e-13,
  "relative_tolerance": 0.0,
  "all_expected_traces_and_derived_budgets_before_import": true,
  "explicit_compute_R_calls_by_harness": 0,
  "source_files_unchanged": 1,
  "metadata_files_unchanged": 3,
  "actual_full_engine_import_no_function_copy_replacement_or_edit": true,
  "production_simulation_baseline_CLI_or_certificate_called": false,
  "immutable_inputs_expected_tables_rng_and_history_ownership_verified": true,
  "alpha1_not_decoded_or_assumed_strictly_less_than_one": true
}
```


### Ten independent wrong models, NOT source mutations

```json
[
  {
    "model": "drift_beta",
    "kind": "equality",
    "detected": true,
    "intended_field": "causal_error",
    "detected_field": "causal_error",
    "numeric_witness": 0.09257493526736936,
    "case": "matched_start_N1_D3",
    "n": 1,
    "i": 0,
    "j": 0,
    "setup_errors_credited": 0
  },
  {
    "model": "drift_plus",
    "kind": "equality",
    "detected": true,
    "intended_field": "causal_error",
    "detected_field": "causal_error",
    "numeric_witness": 0.23773713966304927,
    "case": "matched_start_N1_D3",
    "n": 1,
    "i": 0,
    "j": 0,
    "setup_errors_credited": 0
  },
  {
    "model": "future_input_update",
    "kind": "equality",
    "detected": true,
    "intended_field": "updated_C",
    "detected_field": "updated_C",
    "numeric_witness": 0.01302522614159568,
    "case": "active_N3_D2",
    "n": 0,
    "i": 0,
    "j": 1,
    "setup_errors_credited": 0
  },
  {
    "model": "omit_variation",
    "kind": "upper_bound",
    "detected": true,
    "intended_field": "tracking_envelope",
    "detected_field": "tracking_envelope",
    "numeric_witness": 0.12491863568476039,
    "case": "matched_start_N1_D3",
    "n": 1,
    "i": 0,
    "j": 0,
    "setup_errors_credited": 0
  },
  {
    "model": "newest_weight_alpha",
    "kind": "upper_bound",
    "detected": true,
    "intended_field": "tracking_envelope",
    "detected_field": "tracking_envelope",
    "numeric_witness": 0.027631904393257453,
    "case": "matched_start_N1_D3",
    "n": 1,
    "i": 0,
    "j": 0,
    "setup_errors_credited": 0
  },
  {
    "model": "reverse_weights",
    "kind": "equality",
    "detected": true,
    "intended_field": "complex_error_unroll",
    "detected_field": "complex_error_unroll",
    "numeric_witness": 0.0033444335669670783,
    "case": "matched_start_N1_D3",
    "n": 2,
    "i": 0,
    "j": 0,
    "setup_errors_credited": 0
  },
  {
    "model": "omit_initial",
    "kind": "upper_bound",
    "detected": true,
    "intended_field": "tracking_envelope",
    "detected_field": "tracking_envelope",
    "numeric_witness": 1.2843279264427772,
    "case": "active_N3_D2",
    "n": 0,
    "i": 0,
    "j": 1,
    "setup_errors_credited": 0
  },
  {
    "model": "drifting_prehistory",
    "kind": "upper_bound",
    "detected": true,
    "intended_field": "tracking_envelope",
    "detected_field": "tracking_envelope",
    "numeric_witness": 0.12491863568476039,
    "case": "matched_start_N1_D3",
    "n": 1,
    "i": 0,
    "j": 0,
    "setup_errors_credited": 0
  },
  {
    "model": "alpha1_forced_decay",
    "kind": "equality",
    "detected": true,
    "intended_field": "stationary_tail_error",
    "detected_field": "stationary_tail_error",
    "numeric_witness": 0.35,
    "case": "rounded_alpha1_N1_D2",
    "n": 3,
    "i": 0,
    "j": 0,
    "setup_errors_credited": 0
  },
  {
    "model": "stale_reported_R",
    "kind": "equality",
    "detected": true,
    "intended_field": "reported_R",
    "detected_field": "reported_R",
    "numeric_witness": 0.09940954854603168,
    "case": "active_N3_D2",
    "n": 0,
    "i": 0,
    "j": 1,
    "setup_errors_credited": 0
  }
]
```


For wrong upper bounds, rejection requires actual error>wrong bound+1e-7,
not merely a different safe envelope. Equality controls require intended component
mismatch>1e-7. Fixed cases/points preceded scalar inspection and acquired import.
Missing variation/initial term, beta-scaled/sign-flipped drift, future-input update,
reverse weights, drifting prehistory, forced alpha1decay and stale R are tested.

### Pre-target design receipt

```json
{
  "phase": "Independent pure math/cmath design before acquired module import/advance",
  "cases": [
    {
      "name": "active_N3_D2",
      "N": 3,
      "D": 2,
      "alpha": 0.7788007830714049,
      "one_minus_alpha": 0.22119921692859512,
      "initial_error_max": 1.6125702169463703,
      "first_windings": [
        1,
        0,
        0
      ],
      "first_gate_active": true,
      "input_channel": "prestate_formula_and_actual_C_innovation"
    },
    {
      "name": "slow_negative_N3_D3",
      "N": 3,
      "D": 3,
      "alpha": 0.9394130628134758,
      "one_minus_alpha": 0.06058693718652419,
      "initial_error_max": 1.6002067052907114,
      "first_windings": [
        -1,
        0,
        0
      ],
      "first_gate_active": true,
      "input_channel": "prestate_formula_and_actual_C_innovation"
    },
    {
      "name": "fast_multiwrap_N4_D4",
      "N": 4,
      "D": 4,
      "alpha": 0.36787944117144233,
      "one_minus_alpha": 0.6321205588285577,
      "initial_error_max": 1.0,
      "first_windings": [
        3,
        -3,
        1,
        0
      ],
      "first_gate_active": true,
      "input_channel": "prestate_formula_and_actual_C_innovation"
    },
    {
      "name": "matched_start_N1_D3",
      "N": 1,
      "D": 3,
      "alpha": 0.7788007830714049,
      "one_minus_alpha": 0.22119921692859512,
      "initial_error_max": 0.0,
      "first_windings": [
        0
      ],
      "first_gate_active": false,
      "input_channel": "prestate_formula_and_actual_C_innovation"
    },
    {
      "name": "rounded_alpha1_N1_D2",
      "N": 1,
      "D": 2,
      "alpha": 1.0,
      "one_minus_alpha": 0.0,
      "initial_error_max": 0.9309004857541066,
      "first_windings": [
        0
      ],
      "first_gate_active": false,
      "input_channel": "prestate_formula_only_beta0_no_division"
    },
    {
      "name": "fast_tail_N1_D1",
      "N": 1,
      "D": 1,
      "alpha": 0.1353352832366127,
      "one_minus_alpha": 0.8646647167633873,
      "initial_error_max": 1.0,
      "first_windings": [
        0
      ],
      "first_gate_active": false,
      "input_channel": "prestate_formula_and_actual_C_innovation"
    }
  ],
  "actual_advances_planned": 60,
  "input_tracking_complex_coordinates_planned": 370,
  "consumed_input_complex_coordinates_planned": 370,
  "adjacent_error_recurrences_planned": 333,
  "startup_adjacent_coordinates_planned": 115,
  "first_live_adjacent_coordinates_planned": 37,
  "decoded_C_innovation_coordinates_planned": 360,
  "alpha1_reconstructed_input_coordinates_planned": 10,
  "reported_R_offdiag_bound_coordinates_planned": 240,
  "reported_R_diag_zero_coordinates_planned": 130,
  "ten_wrong_models": [
    {
      "model": "drift_beta",
      "kind": "equality",
      "field": "causal_error",
      "case": "matched_start_N1_D3",
      "n": 1,
      "i": 0,
      "j": 0,
      "intended_witness": 0.09257493526736936
    },
    {
      "model": "drift_plus",
      "kind": "equality",
      "field": "causal_error",
      "case": "matched_start_N1_D3",
      "n": 1,
      "i": 0,
      "j": 0,
      "intended_witness": 0.23773713966304927
    },
    {
      "model": "future_input_update",
      "kind": "equality",
      "field": "updated_C",
      "case": "active_N3_D2",
      "n": 0,
      "i": 0,
      "j": 1,
      "intended_witness": 0.01302522614159568
    },
    {
      "model": "omit_variation",
      "kind": "upper_bound",
      "field": "tracking_envelope",
      "case": "matched_start_N1_D3",
      "n": 1,
      "i": 0,
      "j": 0,
      "intended_witness": 0.12491863568476039
    },
    {
      "model": "newest_weight_alpha",
      "kind": "upper_bound",
      "field": "tracking_envelope",
      "case": "matched_start_N1_D3",
      "n": 1,
      "i": 0,
      "j": 0,
      "intended_witness": 0.027631904393257453
    },
    {
      "model": "reverse_weights",
      "kind": "equality",
      "field": "complex_error_unroll",
      "case": "matched_start_N1_D3",
      "n": 2,
      "i": 0,
      "j": 0,
      "intended_witness": 0.0033444335669670783
    },
    {
      "model": "omit_initial",
      "kind": "upper_bound",
      "field": "tracking_envelope",
      "case": "active_N3_D2",
      "n": 0,
      "i": 0,
      "j": 1,
      "intended_witness": 1.2843279264427772
    },
    {
      "model": "drifting_prehistory",
      "kind": "upper_bound",
      "field": "tracking_envelope",
      "case": "matched_start_N1_D3",
      "n": 1,
      "i": 0,
      "j": 0,
      "intended_witness": 0.12491863568476039
    },
    {
      "model": "alpha1_forced_decay",
      "kind": "equality",
      "field": "stationary_tail_error",
      "case": "rounded_alpha1_N1_D2",
      "n": 3,
      "i": 0,
      "j": 0,
      "intended_witness": 0.35
    },
    {
      "model": "stale_reported_R",
      "kind": "equality",
      "field": "reported_R",
      "case": "active_N3_D2",
      "n": 0,
      "i": 0,
      "j": 1,
      "intended_witness": 0.09940954854603168
    }
  ],
  "absolute_tolerance": 5e-13,
  "relative_tolerance": 0.0,
  "alpha0_formal_only_not_source_valid": true,
  "float_alpha1_source_valid_not_ideal_exp_strictly_less_than_one": true
}
```


## 4 · Exact kernel evidence and formal controls

New namespace Researcher040282.Tracking:

1 tracking_error_step — exact causal identity, all real alpha;
2 tracking_error_budget — chronological finite convolution, alpha>=0;
3 delayed_phase_tracking_budget — actual definition-level004/011/010composition,
 alpha>=0, constant startup and arbitrary unwrapped increments.

Core assumptions are explicit. Nonnegative coefficient is needed to compare
weighted norms; no hypothesis that the error is small or phases lock. Generic D0
is inherited mathematics only; positive exact-delay source configs have D>=1.
C0/inputs arbitrary complex in generic bound, not forced zero/unit/vacuous.

Eight actual formal controls:

-2nonzero endpoint positives: alpha0previous-input and alpha1no-update errors;
-3false math examples: beta-scaled drift, reversed weights at a late input jump,
  and dropping alpha>=0 at alpha=-1. Must reduce to explicit **False**, not a
  parse/import/identifier/runtime/timeout failure;
-3compiling integrity payloads: sorry, injected axiom, missing axiom-print coverage.
  Raw0and intended policy refusal required; not mathematical counterexamples.

Owned fixed-file marker/axiom/coverage policy is NOT a generic untrusted-Lean
sandbox or security certificate. Normal toolchain/cache trust remains explicit.
Every main name has a printed footprint; compiling a theorem is not enough if
sorry/unapproved axiom/warning or missing coverage appears.

### Actual final main compiler output

```text
'Researcher040282.Tracking.tracking_error_step' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.Tracking.tracking_error_budget' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.Tracking.delayed_phase_tracking_budget' depends on axioms: [propext, Classical.choice, Quot.sound]
```


### Full formal result,28reused claims, new3 and8controls

```json
{
  "compiler_version": "Lean (version 4.33.1, x86_64-unknown-linux-gnu, commit 819816b2e0a3bf405af45ae5c7af2491d8f5bee6, Release)",
  "mathlib_revision": "0df444a360eaa60ab8c11dca51a86af692955474",
  "Mathlib_used": true,
  "dependencies": [
    {
      "module": "HistoryBuffer",
      "reused_named_claims_not_new_labels": 3,
      "policy": {
        "accepted": true,
        "reasons": [],
        "named_declarations": [
          "historyTrace_index",
          "historyTrace_oldest",
          "historyTrace_newest"
        ],
        "requested_axiom_prints": [
          "Researcher040282.Delay.historyTrace_index",
          "Researcher040282.Delay.historyTrace_oldest",
          "Researcher040282.Delay.historyTrace_newest"
        ],
        "footprints": {
          "Researcher040282.Delay.historyTrace_index": [
            "Quot.sound",
            "propext"
          ],
          "Researcher040282.Delay.historyTrace_oldest": [
            "Quot.sound",
            "propext"
          ],
          "Researcher040282.Delay.historyTrace_newest": [
            "Quot.sound",
            "propext"
          ]
        },
        "unapproved_axioms": {},
        "raw_compiler_returncode": 0
      }
    },
    {
      "module": "PhaseIncrement",
      "reused_named_claims_not_new_labels": 3,
      "policy": {
        "accepted": true,
        "reasons": [],
        "named_declarations": [
          "phasor_wrap",
          "delayed_input_step",
          "delayed_input_chord_bound"
        ],
        "requested_axiom_prints": [
          "Researcher040282.Phase.phasor_wrap",
          "Researcher040282.Phase.delayed_input_step",
          "Researcher040282.Phase.delayed_input_chord_bound"
        ],
        "footprints": {
          "Researcher040282.Phase.phasor_wrap": [
            "Classical.choice",
            "Quot.sound",
            "propext"
          ],
          "Researcher040282.Phase.delayed_input_step": [
            "Classical.choice",
            "Quot.sound",
            "propext"
          ],
          "Researcher040282.Phase.delayed_input_chord_bound": [
            "Classical.choice",
            "Quot.sound",
            "propext"
          ]
        },
        "unapproved_axioms": {},
        "raw_compiler_returncode": 0
      }
    },
    {
      "module": "CoherenceEMA",
      "reused_named_claims_not_new_labels": 22,
      "policy": {
        "accepted": true,
        "reasons": [],
        "named_declarations": [
          "phaseInput_norm",
          "physicalAlpha_pos",
          "physicalAlpha_lt_one",
          "emaStep_norm_le",
          "emaStep_unitDisk",
          "emaTrajectory_unitDisk",
          "coherenceUpdate_unitDisk",
          "reportedR_nonneg",
          "reportedR_symmetric",
          "reportedR_diag",
          "reportedR_le_one",
          "reportedR_lipschitz",
          "ema_difference",
          "ema_same_input_difference",
          "trajectory_same_input_difference",
          "trajectory_same_input_norm",
          "constant_closed_form",
          "constant_error_norm",
          "constant_zero_norm",
          "constant_converges",
          "matrix_same_input_reported_bound",
          "constant_zero_reported"
        ],
        "requested_axiom_prints": [
          "Researcher040282.EMA.phaseInput_norm",
          "Researcher040282.EMA.physicalAlpha_pos",
          "Researcher040282.EMA.physicalAlpha_lt_one",
          "Researcher040282.EMA.emaStep_norm_le",
          "Researcher040282.EMA.emaStep_unitDisk",
          "Researcher040282.EMA.emaTrajectory_unitDisk",
          "Researcher040282.EMA.coherenceUpdate_unitDisk",
          "Researcher040282.EMA.reportedR_nonneg",
          "Researcher040282.EMA.reportedR_symmetric",
          "Researcher040282.EMA.reportedR_diag",
          "Researcher040282.EMA.reportedR_le_one",
          "Researcher040282.EMA.reportedR_lipschitz",
          "Researcher040282.EMA.ema_difference",
          "Researcher040282.EMA.ema_same_input_difference",
          "Researcher040282.EMA.trajectory_same_input_difference",
          "Researcher040282.EMA.trajectory_same_input_norm",
          "Researcher040282.EMA.constant_closed_form",
          "Researcher040282.EMA.constant_error_norm",
          "Researcher040282.EMA.constant_zero_norm",
          "Researcher040282.EMA.constant_converges",
          "Researcher040282.EMA.matrix_same_input_reported_bound",
          "Researcher040282.EMA.constant_zero_reported"
        ],
        "footprints": {
          "Researcher040282.EMA.phaseInput_norm": [
            "Classical.choice",
            "Quot.sound",
            "propext"
          ],
          "Researcher040282.EMA.physicalAlpha_pos": [
            "Classical.choice",
            "Quot.sound",
            "propext"
          ],
          "Researcher040282.EMA.physicalAlpha_lt_one": [
            "Classical.choice",
            "Quot.sound",
            "propext"
          ],
          "Researcher040282.EMA.emaStep_norm_le": [
            "Classical.choice",
            "Quot.sound",
            "propext"
          ],
          "Researcher040282.EMA.emaStep_unitDisk": [
            "Classical.choice",
            "Quot.sound",
            "propext"
          ],
          "Researcher040282.EMA.emaTrajectory_unitDisk": [
            "Classical.choice",
            "Quot.sound",
            "propext"
          ],
          "Researcher040282.EMA.coherenceUpdate_unitDisk": [
            "Classical.choice",
            "Quot.sound",
            "propext"
          ],
          "Researcher040282.EMA.reportedR_nonneg": [
            "Classical.choice",
            "Quot.sound",
            "propext"
          ],
          "Researcher040282.EMA.reportedR_symmetric": [
            "Classical.choice",
            "Quot.sound",
            "propext"
          ],
          "Researcher040282.EMA.reportedR_diag": [
            "Classical.choice",
            "Quot.sound",
            "propext"
          ],
          "Researcher040282.EMA.reportedR_le_one": [
            "Classical.choice",
            "Quot.sound",
            "propext"
          ],
          "Researcher040282.EMA.reportedR_lipschitz": [
            "Classical.choice",
            "Quot.sound",
            "propext"
          ],
          "Researcher040282.EMA.ema_difference": [
            "Classical.choice",
            "Quot.sound",
            "propext"
          ],
          "Researcher040282.EMA.ema_same_input_difference": [
            "Classical.choice",
            "Quot.sound",
            "propext"
          ],
          "Researcher040282.EMA.trajectory_same_input_difference": [
            "Classical.choice",
            "Quot.sound",
            "propext"
          ],
          "Researcher040282.EMA.trajectory_same_input_norm": [
            "Classical.choice",
            "Quot.sound",
            "propext"
          ],
          "Researcher040282.EMA.constant_closed_form": [
            "Classical.choice",
            "Quot.sound",
            "propext"
          ],
          "Researcher040282.EMA.constant_error_norm": [
            "Classical.choice",
            "Quot.sound",
            "propext"
          ],
          "Researcher040282.EMA.constant_zero_norm": [
            "Classical.choice",
            "Quot.sound",
            "propext"
          ],
          "Researcher040282.EMA.constant_converges": [
            "Classical.choice",
            "Quot.sound",
            "propext"
          ],
          "Researcher040282.EMA.matrix_same_input_reported_bound": [
            "Classical.choice",
            "Quot.sound",
            "propext"
          ],
          "Researcher040282.EMA.constant_zero_reported": [
            "Classical.choice",
            "Quot.sound",
            "propext"
          ]
        },
        "unapproved_axioms": {},
        "raw_compiler_returncode": 0
      }
    }
  ],
  "main": {
    "accepted": true,
    "reasons": [],
    "named_declarations": [
      "tracking_error_step",
      "tracking_error_budget",
      "delayed_phase_tracking_budget"
    ],
    "requested_axiom_prints": [
      "Researcher040282.Tracking.tracking_error_step",
      "Researcher040282.Tracking.tracking_error_budget",
      "Researcher040282.Tracking.delayed_phase_tracking_budget"
    ],
    "footprints": {
      "Researcher040282.Tracking.tracking_error_step": [
        "Classical.choice",
        "Quot.sound",
        "propext"
      ],
      "Researcher040282.Tracking.tracking_error_budget": [
        "Classical.choice",
        "Quot.sound",
        "propext"
      ],
      "Researcher040282.Tracking.delayed_phase_tracking_budget": [
        "Classical.choice",
        "Quot.sound",
        "propext"
      ]
    },
    "unapproved_axioms": {},
    "raw_compiler_returncode": 0
  },
  "new_named_declarations_compiled": 3,
  "reused_named_declarations_recompiled_not_new_labels": 28,
  "formal_controls": 8,
  "positive_controls_accepted": 2,
  "false_math_witnesses_rejected_by_compiler": 3,
  "compiling_integrity_payloads_rejected_by_policy": 3,
  "controls": [
    {
      "control": "positive_alpha0_nonzero",
      "kind": "positive",
      "expected_mechanism": null,
      "expected_outcome_observed": true,
      "policy": {
        "accepted": true,
        "reasons": [],
        "named_declarations": [
          "controlAlphaZero"
        ],
        "requested_axiom_prints": [
          "controlAlphaZero"
        ],
        "footprints": {
          "controlAlphaZero": [
            "Classical.choice",
            "Quot.sound",
            "propext"
          ]
        },
        "unapproved_axioms": {},
        "raw_compiler_returncode": 0
      },
      "setup_errors_credited": 0
    },
    {
      "control": "positive_alpha1_nonzero",
      "kind": "positive",
      "expected_mechanism": null,
      "expected_outcome_observed": true,
      "policy": {
        "accepted": true,
        "reasons": [],
        "named_declarations": [
          "controlAlphaOne"
        ],
        "requested_axiom_prints": [
          "controlAlphaOne"
        ],
        "footprints": {
          "controlAlphaOne": [
            "Classical.choice",
            "Quot.sound",
            "propext"
          ]
        },
        "unapproved_axioms": {},
        "raw_compiler_returncode": 0
      },
      "setup_errors_credited": 0
    },
    {
      "control": "false_beta_scaled_drift",
      "kind": "false_math",
      "expected_mechanism": null,
      "expected_outcome_observed": true,
      "policy": {
        "accepted": false,
        "reasons": [
          "compiler_nonzero",
          "compiler_error",
          "axiom_print_coverage"
        ],
        "named_declarations": [],
        "requested_axiom_prints": [],
        "footprints": {},
        "unapproved_axioms": {},
        "raw_compiler_returncode": 1
      },
      "setup_errors_credited": 0
    },
    {
      "control": "false_reverse_weights",
      "kind": "false_math",
      "expected_mechanism": null,
      "expected_outcome_observed": true,
      "policy": {
        "accepted": false,
        "reasons": [
          "compiler_nonzero",
          "compiler_error",
          "axiom_print_coverage"
        ],
        "named_declarations": [],
        "requested_axiom_prints": [],
        "footprints": {},
        "unapproved_axioms": {},
        "raw_compiler_returncode": 1
      },
      "setup_errors_credited": 0
    },
    {
      "control": "false_drop_nonnegative_alpha",
      "kind": "false_math",
      "expected_mechanism": null,
      "expected_outcome_observed": true,
      "policy": {
        "accepted": false,
        "reasons": [
          "compiler_nonzero",
          "compiler_error",
          "axiom_print_coverage"
        ],
        "named_declarations": [],
        "requested_axiom_prints": [],
        "footprints": {},
        "unapproved_axioms": {},
        "raw_compiler_returncode": 1
      },
      "setup_errors_credited": 0
    },
    {
      "control": "compiling_sorry",
      "kind": "integrity",
      "expected_mechanism": "forbidden_source:sorry",
      "expected_outcome_observed": true,
      "policy": {
        "accepted": false,
        "reasons": [
          "compiler_warning",
          "forbidden_source:sorry",
          "unapproved_axiom_footprint"
        ],
        "named_declarations": [
          "controlSorry"
        ],
        "requested_axiom_prints": [
          "controlSorry"
        ],
        "footprints": {
          "controlSorry": [
            "sorryAx"
          ]
        },
        "unapproved_axioms": {
          "controlSorry": [
            "sorryAx"
          ]
        },
        "raw_compiler_returncode": 0
      },
      "setup_errors_credited": 0
    },
    {
      "control": "compiling_extra_axiom",
      "kind": "integrity",
      "expected_mechanism": "unapproved_axiom_footprint",
      "expected_outcome_observed": true,
      "policy": {
        "accepted": false,
        "reasons": [
          "forbidden_source:axiom",
          "unapproved_axiom_footprint"
        ],
        "named_declarations": [
          "controlExtraAxiom"
        ],
        "requested_axiom_prints": [
          "controlExtraAxiom"
        ],
        "footprints": {
          "controlExtraAxiom": [
            "injectedFalse"
          ]
        },
        "unapproved_axioms": {
          "controlExtraAxiom": [
            "injectedFalse"
          ]
        },
        "raw_compiler_returncode": 0
      },
      "setup_errors_credited": 0
    },
    {
      "control": "omitted_axiom_print",
      "kind": "integrity",
      "expected_mechanism": "axiom_print_coverage",
      "expected_outcome_observed": true,
      "policy": {
        "accepted": false,
        "reasons": [
          "axiom_print_coverage"
        ],
        "named_declarations": [
          "controlNoPrint"
        ],
        "requested_axiom_prints": [],
        "footprints": {},
        "unapproved_axioms": {},
        "raw_compiler_returncode": 0
      },
      "setup_errors_credited": 0
    }
  ],
  "setup_errors_credited": 0,
  "all_preregistered_formal_conditions_met": true,
  "scope": "Exact-real causal moving-input EMA error and finite weighted budget, composed with prior phase/history; not floating FFI/full coupled map/locking; alpha>=0finite, no hidden alpha<1 assumption; fixed-owned-source policy not generic sandbox"
}
```


### Actual three false-math compiler logs

### false_beta_scaled_drift

```text
false_beta_scaled_drift.lean:5:63: error: unsolved goals
⊢ False
```

### false_reverse_weights

```text
false_reverse_weights.lean:5:79: error: unsolved goals
h : emaTrajectory (1 / 2) 1 controlLateZ 2 - controlLateZ 2 = 2
⊢ False
```

### false_drop_nonnegative_alpha

```text
false_drop_nonnegative_alpha.lean:5:66: error: unsolved goals
⊢ False
```


### Retained development errors, never credited or promoted

-`development/initial_proof/`: two additive-helper left/right orientation type
 mismatches in own proof. Explicit componentwise add_le_add/reflexivity fixes
 them, changing no statement/coefficient/domain/tolerance/case. Draft had inherited
 sorryAx and is not a verified claim or planned falsifier. Corrected main clean
 under `development/explicit_additions/`.
-`development/first_full_runner_control_blocker/`: all4Python workers passed,
 main3and28dependencies compiled clean, but false reverse-weight control hit a
 complex-numeral versus coerced-real norm rewrite error. Strict classifier BLOCKED
 it, did not call it a mathematical success. Normalize complex norm via
 norm_def/normSq, same false statement/classifier; explicit False observed in
 `development/explicit_norm_control/`, then corrected full runner repeated.
-No upstream/source repair or failing-before claim. No target-derived expected
 values or post-target tolerance/witness tuning. Other completed reports/evidence
 remain untouched.

## 5 · What can be derived, and what is still not proved

If input variation<=M, finite budget<=alpha^nE0+M*sum_(r<n)alpha^r.
For0<=alpha<1 this equals alpha^nE0+M*(1-alpha^n)/(1-alpha). This is paper
corollary here, not a fourth compiled claim. Even then M>0gives a possible error
floor, not exact tracking/phase locking. At alpha1 use the finite sum, not a
singular formula or a silently discounted coefficient.

Using004reportedR_lipschitz and unit phasors, offdiag
|R_(n+1,ij)-1|<=alpha*(B_nij+B_nji)/2; diagonal0. Paper+finite check, not a new
compiled sharp future-R-band, rate-law or common-freeze theorem. Twelve nonzero
first-step Rbounds are tight below1, but no future margin is asserted. Source
capacity reasoning can further bound phase increments (011paper scope), without
assuming the desired convergence; that full closed-loop composition remains open.

This is not a Lean proof of NumPy floating remainder/trig/EMA FFI, source allocation,
whole C/R/B/phase map, complete baseline equivalence, stability, real production
study or certificate. It genuinely composes the earlier exact-real components,
not the whole reference-library Lake project/CI. New module is unregistered and
uninstalled pending owner/R001/Seat002decision. No independent012approval.

## 6 · Reproduce from this note

All16critical owned files inline below; no inaccessible private dependency. Use
extract_from_report.py, then fetch_public_dependencies.py for4public dependencies
(engine+Frozen registry+source toolchain+lake manifest). Python/NumPy required.
Setup/public cache helper needs network+Git and own decoder target. Example:

```text
python -B prepare_lean.py --receipt compiler_setup.json
python -B prepare_mathlib.py --receipt mathlib_setup.json
python -B run_checks.py --source upstream --output checks \
  --lean ~/.cache/researcher040282-cycle012/lean-4.33.1-linux/bin/lean \
  --mathlib ~/.cache/researcher040282-cycle012/mathlib4
```

Actual compiler archive570405234bytes reverified against retained official selected
release length/digest, not a fresh release-API claim. Complete runtime18130members/
3037354159extracted bytes; targeted8roots/2195cached module bundles, not omnibus
Mathlib/Tactic; setup41.58987966400002s+53.50482302099999s and6021761311owned logical
bytes, within12GiB/15minutes. No global toolchain setting or old-cache restoration.
Source project prescription used. Later cleanup includes its Git object metadata
and one irrelevant quarantined PII-path text never included as evidence.

### Actual full extracted-note repetition

**Actually executed:** sixteen critical files extracted byte-identically, four public dependencies freshly fetched/verified, same disposable compiler/targeted Mathlib; complete runner repeated. Science/four non-timing workers and all35 detailed proof/source/log records match. Submitter-local reproduction only, not independent-seat review.

```json
{
  "actually_executed": true,
  "runner_returncode": 0,
  "tested_main": "543e7e1aaa11e4c810783806cb180eee36ec5313",
  "critical_file_count": 16,
  "critical_files": [
    "CoherenceEMA.lean",
    "EMATracking.lean",
    "tracking_contract.py",
    "HistoryBuffer.lean",
    "PhaseIncrement.lean",
    "phase_contract.py",
    "prepare_mathlib.py",
    "step_contract.py",
    "check_engine.py",
    "load_reviewed.py",
    "check_lean.py",
    "prepare_lean.py",
    "run_checks.py",
    "source_modules.json",
    "fetch_public_dependencies.py",
    "extract_from_report.py"
  ],
  "all_extracted_files_byte_identical": true,
  "fresh_public_dependencies_fetched_and_verified": 4,
  "fresh_public_python_sources": 1,
  "fresh_scope_compiler_metadata_files": 3,
  "same_original_verified_compiler_and_Mathlib_reused": true,
  "fresh_clean_compiler_or_Mathlib_installation_claimed": false,
  "scientific_summary_matches_original": true,
  "all_four_worker_nontiming_results_match_original": true,
  "all_thirtyfive_detailed_records_byte_identical": true,
  "detailed_matching_files": [
    "common_normal/advance_observations.json",
    "common_normal/preexecution_design.json",
    "common_normal/tracking_observations.json",
    "common_optimized/advance_observations.json",
    "common_optimized/preexecution_design.json",
    "common_optimized/tracking_observations.json",
    "proof/compiled_sources/CoherenceEMA.lean",
    "proof/compiled_sources/EMATracking.lean",
    "proof/compiled_sources/HistoryBuffer.lean",
    "proof/compiled_sources/PhaseIncrement.lean",
    "proof/compiled_sources/compiling_extra_axiom.lean",
    "proof/compiled_sources/compiling_sorry.lean",
    "proof/compiled_sources/false_beta_scaled_drift.lean",
    "proof/compiled_sources/false_drop_nonnegative_alpha.lean",
    "proof/compiled_sources/false_reverse_weights.lean",
    "proof/compiled_sources/omitted_axiom_print.lean",
    "proof/compiled_sources/positive_alpha0_nonzero.lean",
    "proof/compiled_sources/positive_alpha1_nonzero.lean",
    "proof/compiler_logs/CoherenceEMA.log",
    "proof/compiler_logs/EMATracking.log",
    "proof/compiler_logs/HistoryBuffer.log",
    "proof/compiler_logs/PhaseIncrement.log",
    "proof/compiler_logs/compiling_extra_axiom.log",
    "proof/compiler_logs/compiling_sorry.log",
    "proof/compiler_logs/false_beta_scaled_drift.log",
    "proof/compiler_logs/false_drop_nonnegative_alpha.log",
    "proof/compiler_logs/false_reverse_weights.log",
    "proof/compiler_logs/omitted_axiom_print.log",
    "proof/compiler_logs/positive_alpha0_nonzero.log",
    "proof/compiler_logs/positive_alpha1_nonzero.log",
    "proof/result.json",
    "wrong_models_normal/preexecution_design.json",
    "wrong_models_normal/wrong_models.json",
    "wrong_models_optimized/preexecution_design.json",
    "wrong_models_optimized/wrong_models.json"
  ],
  "commands_observed": [
    {
      "program": "proposal/extract_from_report.py",
      "returncode": 0
    },
    {
      "program": "standalone/extracted/fetch_public_dependencies.py",
      "returncode": 0
    },
    {
      "program": "standalone/extracted/run_checks.py",
      "returncode": 0
    }
  ],
  "source_passes_each_mode": [
    9,
    9
  ],
  "source_failures_errors_skips_each_mode": [
    0,
    0,
    0
  ],
  "actual_advances_each_common_mode": [
    60,
    60
  ],
  "source_initializations_each_common_mode": [
    0,
    0
  ],
  "current_tracking_coordinates_each_mode": [
    370,
    370
  ],
  "adjacent_causal_coordinates_each_mode": [
    333,
    333
  ],
  "wrong_models_detected_each_mode": [
    10,
    10
  ],
  "new_named_Lean_declarations_compiled": 3,
  "reused_dependency_labels_not_added": 28,
  "formal_controls_repeated": 8,
  "original_elapsed_seconds": 554.1702804020001,
  "extracted_elapsed_seconds": 562.327805163,
  "command": "python -B standalone/extracted/run_checks.py --source standalone/upstream --output standalone/checks --lean <same verified compiler> --mathlib <same targeted Mathlib>",
  "result": "cycle_012/standalone/checks/cycle_results.json",
  "log": "cycle_012/standalone/reproduction.log",
  "scope": "Submitter-local exact-note full repetition, not independent review, Python/float/full-coupled proof, real study, authority certificate, source repair/integration or upload"
}
```


Same original verified compiler/targeted Mathlib, NOT a second clean installation
or independent seat's repetition. All16extracted code files,4fresh public deps,
science/four non-timing workers and35detailed files (10design/source/model,
1formal,12sources+12compiler logs) must match. Timing-bearing common logs need not
byte-match; actual scientific records do.

### Own disposable setup cleanup, after actual complete repeat

```json
{
  "own_cache": "/home/user/.cache/researcher040282-cycle012",
  "measured_before_removal": true,
  "regular_files_removed": 62879,
  "regular_file_logical_bytes_removed": 6022977073,
  "allocated_bytes_summed_over_regular_file_entries": 6141650944,
  "allocated_sum_not_unique_physical_freed_space_claim": true,
  "symlinks_removed": 15,
  "subdirectories_removed": 3120,
  "actually_removed_after_successful_full_reproduction": true,
  "only_cycle012_owned_runtime_archive_decoder_Git_Mathlib_quarantined_input_target_removed": true,
  "quarantined_irrelevant_PII_text_removed": true,
  "quarantined_contact_value_printed_or_copied_to_outgoing_evidence": false,
  "compiler_global_setting_changed": false,
  "all_unrelated_caches_untouched_claimed": false,
  "old_AIEFS_evidence_deleted": false,
  "legacy_deleted_Lua_restored": false,
  "cache_absent_after_removal": true
}
```


Only own012runtime/archive/decoder/Git/Mathlib/quarantined irrelevant input cache
removed. No claim all unrelated system/pip caches were audited. Earlier AIEFS
reports/science/archives preserved; deleted legacy Lua folder remains absent.

## 7 · Fresh team context, privacy and numbered011clarification

Current main42texts and12retained inbox notes/evidence inspected BEFORE selection;
22Git heads and1openPR24scope read. Current Gate P1/P2 and active P3have R frozen/
controller/persistence scope, not EMA tracking. Prior004owns fixed/shared input
EMA,011owns wrapped increments. Limited public nonduplication, not exhaustive/
private-work assurance. No source-version/canonical-copy finding.

Main E19-E21 now have new-file F4/F6/F7 successors/errata/tests; E24-E26trust-guard
work landed. Older own "not installed" statements are historical, not current
absence. Contributor genuine S01 validator positive/forgeries is NOT our009harness
or010/011/012approval. Scientific v4.1 audit/analysis certification still separate.
E22rate-law sweep already performed (UNEXPLAINED under rule); new entrypoint
checker proposal/evidence also read only. No duplicated sweep/guard/entrypoint/
uploader/chronicler work, no contributed script acquired/executed.

Read-only Git shallow blobless refs/tree and selected raw texts from the start,
no current012API403 claim or full generated-data download. Initial substring ema
matched email/schema. An irrelevant salvage PII note (1pattern, value NOT printed)
was confined to own excluded disposable cache and omitted retained evidence.
Token-bounded EMA matching fixes navigation; all retained bytes unmodified. Raw
Git contacts/signatures never copied into outgoing metadata. Branch records
minimal; historical synthetic fixtures distinguished, not exhaustive secrets scan.

**Numbered011clarification:** its source table overstated DynamicState.validate as
checking B "structure/gap". Actual validation only structural/finite/history length/
Bsymmetry/diag/nonnegative; NO capacity/gap or reachability/newest guarantee.
The advance's825-828post-gate check enforces tolerated gap. This012follow-up leaves
completed011report/code/results/ledger untouched, and does not rerun011science.
Its generic proof and explicitly separate finite row-capacity checks unaffected.

```text
#012 source correspondence and numbered011 clarification

## A. Exact read-only target and current team context

Current selected main is543e7e1aaa11e4c810783806cb180eee36ec5313,42retained main
texts. Full119493-byte ART-0702 Frozen engine is imported intact; no copied/
extracted/replaced source functions or frozen source/registry/lock edit. Other
recent successors/guards/gate packages only read as coordination, not executed.
Four standalone public dependencies: engine, Frozen artifacts.csv, source Lean
prescription, lake-manifest. Metadata identifiers are scope/reproduction, not a
canonical-copy/version finding.

Current main contains Gate P1/P2; active public PR24 P3 uses R FROZEN, controller
fiber/branch persistence, not moving-phase/EMA tracking. E19-E21 new-file F4/F6/F7
successors/errata/tests and E24-E26 trust-guard work now landed, per current tree/
errata. Historical own005-009submission installation statuses are not a statement
of current absence. Contributor002 genuine S01 validator positive/forgeries
reproduction is its scope, not our009harness or010/011/012approval. No authentic
S01, candidate validator/CLI or production simulation executed by012. New entrypoint
proposal/evidence read only, no contributed checker or reproducer fetched/executed.
E22 rate-law sweep already performed, label still UNEXPLAINED; do not duplicate.
Dated briefings can lag current refs; inspect relevant current tree and PR scope.

## B. Numbered clarification to011, without changing delivered evidence

011 SOURCE_CORRESPONDENCE table (and its inline report copy) overstated
DynamicState.validate as checking B "structure/gap". Actual584-679 checks state
N, history length D+1/vector shapes, theta/B/C shapes, finite arrays, B symmetry,
diagonal and nonnegativity. It checks neither capacity/gap nor initialized
history reachability/newest==theta. Runtime advance's825-828post-gate check
computes g_min and enforces g_min>=delta-FROZEN_GAP_TOL.

This012correction is a new numbered follow-up, not an in-place edit of011report,
source/evidence or claims.011generic history/phasor proof does not require Python
validation to guarantee capacity;011finite row-capacity checks explicitly ran
separately. Its scientific code/results/ledger labels unchanged and not rerun.
012tracking theorem also does not assume an initial or validation-certified gap.

## C. Time-index map: what actual advance n does

| Source | Mathematical object / tested role |
|---|---|
| ModelConfig155-174,178-237 | alpha=float(exp(-dt/Twindow)), capacity and D; positive dt/tau, exact D*dt=tau force source D>=1. Alpha validation is0<alpha<=1, not strict<1. |
| DynamicState584-679 | copies synthetic arrays, validates structural/finite domain as sectionB; no initializer call in012. |
| compute_R721-752 | reads old theta_n/H_n[0], z_nij=exp(i*(theta_ni-H0_j-((omega_i+omega_j)/2)*tau)); writes directed C_(n+1)=alpha*C_n+(1-alpha)*z_n; magnitude THEN symmetric R/diag0. |
| advance755-844 | R_(n+1) from NEW C first, B Euler/clip/symmetry/conditional gate, post-gap check; NEW gated B in phase sin(H0_j-theta_i); modulo; append theta COPY/pop. |
| phase830-839/history841-844 | u_ni=dt*(omega_i+sum_j B_(n+1,ij)*sin(H0_j-theta_ni)); wrapped x_(n+1)=W(x_n+u_n), reachable constant initial history supplies exact lag. |

Source return R_physical is reportedR(C_(n+1)), NOT reportedR(C_n).
One call n consumes z_n, not z_(n+1).10calls per trace expose old-state arguments
for z0..z9 and C0..C10. Current-input e_n=C_n-z_n is checked n0..9; consumed-
input post-error r_n=C_(n+1)-z_n is checked n0..9; next-current recurrence n0..8
needs two observed inputs. We do NOT claim C10-z10 from a nonexistent eleventh read.

## D. Formal composition, not another assumed lock premise

Unchanged004 CoherenceEMA supplies actual-shaped emaStep/emaTrajectory/phaseInput
and reportedR_lipschitz. Unchanged011 PhaseIncrement supplies wrapped trace and
startup-aware unit phasor motion; unchanged010 HistoryBuffer supplies reachable
oldest. Recompile22+3+3prior claims as explicit dependencies, NOT28new labels or
reruns of historical scientific suites.

New delayedPhaseInput is defined using004.phaseInput on011.phaseTrace and010oldest.
Inside the new proof it is DEFINITIONALLY the011.inputPhasor; equality is not an
assumed axiom or input hypothesis. Thus composition really compiles, unlike011's
then-future004interface integration. New three named claims:

1 tracking_error_step: e_(n+1)=alpha*e_n-(z_(n+1)-z_n), ALL real alpha.
2 tracking_error_budget, alpha>=0: ||e_n||<=alpha^n||e0||+
   sum_(k<n)alpha^(n-1-k)||z_(k+1)-z_k||.
3 delayed_phase_tracking_budget, alpha>=0: replace each variation by
   |u_ki-L_kj|, L=0startup k<D, else u_(k-D,j).

The newest input variation has weight1, not alpha or1-alpha. Initial error is
not discarded. No small-variation, convergence, complete coupled-map or locking
conclusion in the hypotheses. Alpha may be0,1or>1 abstractly; nonnegative finite
budget remains valid. Source-valid alpha>0, source D>=1; abstract0 not a source
run. Mathematical D0 carried by inherited theorem, not a positive-tau config.

Uniform M gives only paper M*sum alpha^r. Division by1-alpha and asymptotic decay
requirealpha<1; even then nonzero M gives an error floor, not exact tracking or
phase locking. Reported-R bound offdiag follows004lipschitz/unit phasors and
r_n=alpha*e_n: |R_(n+1,ij)-1|<=alpha/2*(B_nij+B_nji); diagonal0. Paper+finite
check, not an extra newly compiled R/freeze/rate-law theorem.

## E. Floating endpoint is real evidence, not a refutation of real exp

Synthetic N1,D2,dt.125,Twindow1e20 yields source float alpha=1, accepted by its
validation. C0=.3+.4i remains EXACTLY unchanged for10calls. With late input near1,
observed late error0.8062257748298549. Do not apply ideal real
physicalAlpha(dt,Tw)<1 directly to rounded source values, or infer strict
contraction/convergence from alpha<=1. This is an extreme synthetic numerical
boundary, not a defect finding about production cohorts or a universal infinite-
time floating trajectory statement. The formal finite theorem needs no1-alpha
inverse and covers this numerical coefficient as a real parameter.

At alpha1 no C innovation can identify z: (Cnew-alpha*Cold)/(1-alpha) is undefined.
Our10endpoint inputs are explicitly reconstructed from copied observed pre-state
arguments via pure math, NOT decoded or directly returned by engine. Constant C,
phase/history/scalar state and error relations still checked. Other360input
coordinates have both argument reconstruction AND actual C-innovation decoding,
with fixed beta>=.05. No division by0, hidden fallback/skip or false detection.

## F. Independence, finite counts and falsifiers

All6expected full traces AND370derived error/budget/unroll cells completed before
acquired module import in each worker. Pure math/cmath independent scalar dynamics;
expected history never assigned from target, analytic max(0,n-D) input lag,
expected u uses predicted NEW gated B, no pre-call mutating compute_R.

Observed snapshots/actualC innovations are measurements, not expected values.
Relational checks using observed e/delta are additionally compared with independent
precomputed predictions. Frozen input tuples/cells, copied actual data, ownership
and RNG preserved. No initializer/run_seed/simulate_*/shuffle/baseline/S01/CLI/
writer/certificate call or source function replacement.

Per normal/-O common suite:9methods/60actual advances/6cases;370current errors,
370consumed errors,333adjacent recurrences=115startup+218live,37first-live;
240offdiag R bounds/130diag0;360decoded inputs+10explicit alpha1formula-only.
Fixed abs5e-13/rel0, one-sided bound slack same; finite shape/real/imag checked
explicitly. Source ZERO1e-12/PROJECTION_NORM1e-14/GAP1e-9 distinct constants.
Observed max source/scalar error9.992007221626409e-16; causal/unroll4.440892098500626e-16,
consumed2.220446049250313e-16;245nonzero phase-budget checks below2;12tight nonzero
R bounds below1. Two alpha<1stationary tails decay finitely as predicted, not
proof of coupled phase locking. Alpha1C constant/non-decay separate.

Ten wrong models are independent references, never injected source variants.
Equality models need intended component residual>1e-7; wrong upper bounds need an
actual positive violation>1e-7, NOT merely disagreement with another safe bound.
Eight formal controls: alpha0/1nonzero positives, beta-scaled drift/reversed weight/
dropped-nonnegative false math reduced to explicit False, compiling sorry/extra
axiom/missing-print policy refusals. Unknown identifier/import/setup/timeout
failures block, never semantic detections. Fixed-owned-source integrity policy
not arbitrary-source sandbox or security certificate.

Initial new proof had two additive-helper orientation type mismatches; use explicit
componentwise add_le_add/reflexivity. Statements/coefficients/domains/cases/tolerance
unchanged. Failed draft/log retained, not a falsifier or promoted build. All28old
component claims and corrected3main claims compiled clean; final full-run controls
and actual extracted repetition still required for closure/promotion.
```


### Preregistration, integration restrictions, selection and setup records

### PLAN.md

```text
#012 preregistration — causal time-varying-input EMA tracking

Researcher040282; prepared2026-09-04 Atlantic/Reykjavik session label. Repository/
owner November labels and runtime build dates remain separate. BEFORE owned012
proof compilation or acquired-engine execution. Completed011state/122-row ledger
protected under previous011_snapshot. Current stage so far public inspection only.

## Fresh scope, changed team state, bounded result selection

Current main543e7e1aaa11e4c810783806cb180eee36ec5313,42selected texts including
new GateCore P1/P2; inboxb61f4340a4dfc9ae5b2732e51efeb49d0c10bd3d,12retained
notes/evidence (some repeated historical content).22Git heads,1openPR24, fresh
public HTML body read: P3 controller-fiber/persistence with R FROZEN, not EMA
tracking. Selected current Lean scopes/keywords no tracking result. Own004 has
EMA definitions, fixed/shared-input facts, NOT moving-input tracking;011 gives
phase increments/chord, no EMA tracking. Limited public navigation, not exhaustive
or private-work assurance. Standard filter bound, no physical novelty claim.

Fresh E19-E21 indicate F4/F6/F7 new-file successors/errata/tests now landed; old
"not installed" submission statements are historical, not current absence. E22
rate-law sweep landed but UNEXPLAINED under its rule; no duplicate sweep. E24-E26
trust-input guard/followups landed. New Auditor002 genuine S01 validator positive/
P1 forgeries evidence concerns ITS test, not our009harness or010/011approval.
No run_analysis/CLI scientific certification inferred. New entrypoint integrity
proposal read only, do NOT duplicate or execute it. Targeted R040282/R001 intake
unchanged; no independent010/011approval discovered. Dated briefings not live:
PR24 is now open and main includes E26 despite stale pending labels in notes.

Git shallow BLOBLESS tree/raw selected files from start, no API403 attempt012.
Never download generated-data repo. Initial substring ema selected email/schema;
one irrelevant salvage PII note (1pattern, value NOT printed) quarantined into
own EXCLUDED disposable cache and omitted retained manifest. Refiner uses token
EMA, not email/schema. No contributed reproducer/checker acquired/executed.
Only minimal branch IDs/policy outgoing, raw Git objects confined own cache.

One result set: compose unchanged004 CoherenceEMA definitions and011 delayed
phasor input/chord using unchanged010 HistoryBuffer. No gate P1-P3, rate-law,
uploader/checksum, guard, chronicler or registry-entrypoint duplicate work.
No source/registry/lock/frozen repair/integration, production/S01/baseline/shuffle/
intervention/CLI/writer/certificate, remote contact/push/PR/upload/merge or013.

## Numbered correction to011 mapping (not editing completed evidence)

011 correspondence table said DynamicState.validate checks B structure/gap.
Actual584-679 checks finiteness, shapes/history length, symmetry/diag/nonnegative
ONLY, not capacity/gap, newest==theta or reachability. Runtime advance checks
post-gate g_min at825-828.012states this precisely. Prior011generic proof and
finite post-gate row checks unaffected; no011science rerun or report rewrite.

## Three intended new named formal declarations

Reuse unchanged004 emaStep/emaTrajectory (C_(n+1)=alpha*C_n+(1-alpha)*z_n) and
011/010phase/history. Define e_n=C_n-z_n, Delta z_n=z_(n+1)-z_n, and

 B(alpha,E0,a,n)=alpha^n*E0 + sum_(k<n) alpha^(n-1-k)*a_k.

1 Exact causal tracking error: e_(n+1)=alpha*e_n-Delta z_n. The drift coefficient
  is1, NOT1-alpha/alpha. Consumed-input error C_(n+1)-z_n=alpha*e_n is distinct.
2 For alpha>=0, ANY complex C0/sequence z:
  ||e_n||<=B(alpha,||C0-z0||,k->||Delta z_k||,n).
3 Actual definition-level composition: using004.phaseInput on011.phaseTrace and
 010.historyTrace oldest, ||e_n||<=B(alpha,||C0-z0||,
 k->|u_(k,i)-L_(k,j)|,n), L=0 when k<D else u_(k-D,j).

No tracking/convergence conclusion assumed as a forcing premise. Arbitrary
increments can be feedback-generated; no full coupled C/R/B/phase FFI theorem.
Only alpha>=0 needed for finite bounds: alpha0/1 handled, no1-alpha division.
Abstract alpha0 not source-valid (source validates alpha>0); SOURCE float alpha1
CAN occur when exp(-dt/Tw) rounds to1. Ideal-real physicalAlpha(dt,Tw)<1 from
positive dt/Tw is NOT a verified floating inequality. Do not infer convergence
for the rounded1endpoint or coupled locking for any alpha.

Uniform variation M gives paper corollary alpha^n*E0+M*sum_(r<n)alpha^r; for
0<=alpha<1 this equals alpha^n E0+M*(1-alpha^n)/(1-alpha). No new compiled uniform/
asymptotic claim. Paper/finite reported R bound offdiag:
|R(C_(n+1))_ij-1|<=alpha/2*(B_nij+B_nji), via004.reportedR_lipschitz and unit
phasors. Diagonal0. No future ON band/freeze/locking or physical threshold claim.

Three new names only, standard full footprints subset{propext,Classical.choice,
Quot.sound}, no main warnings/errors/sorry/admit/native_decide/extra axioms.
RECOMPILE28prior declarations as dependencies (22EMA+3history+3phase), no new
labels for them, not rerunning old004/010/011full scientific suites.

## Fixed six synthetic cases / independent expectations

10advances each,60calls/common suite/mode.37coordinates per time:
370current-input tracking coordinates n0..9,370consumed-input post-C errors,
333adjacent causal recurrences n0..8=115startup+218live;37first-live n=D.
360decoded innovation coordinates in alpha<1cases;10alpha1inputs only reconstructed
from copied observed pre-state, NOT falsely called observable C innovations.
240offdiag reported-R bounds/130exact diag-zero coordinates per mode.

All histories D+1constant copies initially. Immutable full expected traces using
pure math/cmath scalar reference built BEFORE acquired module import, not target
outputs. Expected phi uses analytic max(0,n-D) trace age; expected u uses NEW
gated B/delayed-current sine. Complete C/B/theta/history/R also compared. No
initialize_state, no pre-call mutating compute_R or source function replacements.

Common dt.125,a1,q1.5,delta.1,mu.05,gamma.2,epsilon1e-12,B_c/B_init_scale0.
Coupled eta3, N3B edges(.08,.23,.32), N4Bij=.04*(1+i+j) offdiag/diag0.
N3 directed C0 is unchanged010base_case pattern (all finite, nonzero), N4C0zero.

- active_N3_D2: theta(2*pi-.015,1.27,4.13),omega(.5,1,1.5),Tw.5;
- slow_negative_N3_D3: theta(.01,1.27,4.13),omega(-1,.75,1.5),Tw2;
- fast_multiwrap_N4_D4: theta(.31,1.27,4.13,2.71),omega(161,-143,27,1.25),Tw.125;
- matched_start_N1_D3: theta6.1,omega1,B0,eta=mu=gamma0,Tw.5,C0=exp(-i*.375)=z0;
- rounded_alpha1_N1_D2: theta6.1,omega1,B0,eta=mu=gamma0,Tw1e20,C0=.3+.4i;
- fast_tail_N1_D1: theta.25,omega1,B0,eta=mu=gamma0,Tw.0625,C0=0.

Fixed abs5e-13/rel0 for finite real/imag components, exact-recursion/unroll residual,
one-sided bound slack. Exact shapes/bools/ownership/range/RNG/input preservation.
No NaN-masking whole-complex predicate. All numeric wrong witnesses>1e-7. No
post-target tolerance or witness tuning. Scalar-only design receipts may flag
vacuity BEFORE actual import; if needed record prereg amendment then, not after.

## Nine same common methods normal/-O

1 all6x10independent full traces/actual scalar component comparison; only method
 making source calls, immutable observations reused by other methods;
2 exact causal e-next=alpha e-Delta z,333coordinates;
3 exact complex finite unroll plus norm-input and phase-increment budgets,370coords;
4 consumed-input post-C=alpha*current error, not next-input tracking,370coords;
5 startup/live phase variation,115startup/37first-live, weighted constant startup;
6 stationary-input N1tails: alpha<1geometric error vs roundedalpha1non-decay;
 abstract alpha0 endpoint is formal/pure arithmetic only, not invalid source run;
7 R physically returned AFTER C,240offdiag bounds/130diag0, at least one tight
 nonzero bound<1, not a sharp future-band or locking assertion;
8 nonzero initial C, active gate, positive/negative/multiwrap, decoder360 versus
 reconstructed-only alpha1ten; beta0never divided, no skip credited;
9 exact inventory/preservation,9passes/0failures/errors/skips, all normal/-O
 non-timing records match. No actual008/009guard/production entry point calls.

## Ten fixed wrong models per mode, not injected source variants

All positions fixed BEFORE scalar or target execution. Matching source model's
OWN exact outputs/complex errors (or inequality violation), not merely a different
safe upper bound. Minimal numeric witness>1e-7; setup/errors block.

1 drift_beta: matched_start,transition n0,node00,wrong e1=alpha e0-(1-alpha)Delta;
2 drift_plus: same,wrong e1=alpha e0+Delta;
3 future_input_update: active_N3_D2,n0,i0j1,wrong C1=alpha C0+beta*z1;
4 omit_variation: matched_start,n1,wrong bound alpha^1 E0=0, actual error>0;
5 newest_weight_alpha: same,wrong bound alpha*||Delta0||, actual error larger;
6 reverse_weights: matched_start,n2,wrong complex error alpha^2 e0-Delta0-alpha Delta1;
7 omit_initial: active_N3_D2,n0,i0j1,wrong bound0, actual initial error>0;
8 drifting_prehistory: matched_start,n1,wrong phase budget0 by u0i-u0j in startup;
9 alpha1_forced_decay: rounded_alpha1,n3,wrong e3=.5*e2 instead of unchanged tail;
10 stale_reported_R: active_N3_D2,n0,i0j1,wrong R from OLD C rather than updated C.

8formal controls:2nonzero endpoint positives alpha0previous-input and alpha1no-
update;3false math (beta-scaled drift; reversed finite weights for a late input
jump; drop alpha>=0 with alpha=-1), must reduce explicit False;3compiling integrity
payloads sorry/extra axiom/missing axiom-print, raw0but intended policy refusal.
Unknown identifier/import/parse/setup/runtime/timeouts are NEVER math detections.

## Setup, reproduction and closure

Lean/lake/old caches absent,~20GiB free. Deliberate own excluded
.cache/researcher040282-cycle012 only, complete prescribed runtime for Lake,
targeted Mathlib roots (prior6plus SpecificLimits.Normed and Positivity). Source
project same prescribed Lean/Mathlib as recorded selected metadata; reverify
actual compiler archive against retained official selected release length/digest.
Not a fresh release-API claim. No global toolchain setting/earlier cache restore.
Setup bound12GiB/15minutes; blocked setup means uncompiled honestly. Preserve
all draft/control/setup errors separately, no promotion from sketches.

Then13+3=16critical owned files inline, extract into fresh directory, freshly
fetch current engine+Frozen registry+toolchain+lake-manifest (4deps), repeat FULL
runner with same verified compiler/Mathlib (not second clean install). Compare
science/four worker non-timing records and35detailed files (10design/source/model,
1formal record,12compiled sources+12compiler logs). Remove OWN runtime/archive/
decoder/Git/Mathlib/quarantined irrelevant input cache only AFTER actual rerun.

Append3scoped compiled rows+1finite contract ONLY after observed success, expected
126rows/103formal labels if all gates met; prior122/100 preserved. All prior
reports/archives/nonlive evidence/snapshots unchanged. Missing old CI copy may be
restored missing-only from delivered011ZIP, no old science rerun or deleted Lua
restoration. Packet/privacy/citation/CRC/preservation closure; freeze logs BEFORE
packaging, no active in-packet stdout capture. Owner upload only, no independent
approval/integration inferred, no unattended013.
```

### proposal/INTEGRATION_NOTE.md

```text
#012 proposed new-file library intake — causal EMA tracking, not installed

Researcher040282 -> Researcher001 / AuditorSeat002. One standard but load-bearing
component bridge: causal tracking error and finite weighted variation budget,
composed with wrapped delayed phasor input. Not new physics or engine repair.

Candidate new `EMATracking.lean`; unchanged `CoherenceEMA.lean`(004),
`PhaseIncrement.lean`(011),`HistoryBuffer.lean`(010) explicit dependencies.28old
named claims recompiled, NOT new ledger labels.3new names in
`Researcher040282.Tracking`:tracking_error_step,tracking_error_budget,
delayed_phase_tracking_budget. Source library project integration/import layout,
registry/authority adoption and independent statement/control review remain pending.
Standalone compilation genuinely composes004EMA definitions and011/010input,
but not the FULL coupled C/R/B/phase evolution or Python/float FFI.

C_(n+1) consumes z_n. So current error e_(n+1)=alpha e_n-Delta z_n (coefficient1,
NOT1-alpha), while consumed post-error C_(n+1)-z_n=alpha e_n. Finite bound's most
recent variation has weight1, initial term alpha^n||e0|| explicit. The only bound
hypothesis is alpha>=0; no input-locking conclusion assumed. Generic alpha0/1
covered. Source alpha>0 can FLOAT-ROUND to1: do not apply ideal exp strict<1 to
that value or divide its innovation by0. No infinite-time production claim from
ten synthetic endpoint steps. All expected traces and derived budgets before
acquired import; actual engine remains frozen/unmodified.

New source/context before selection: main has Gate P1/P2, active PR24P3R frozen;
not duplication. E19-E21 successors and E24-E26 guards landed by others, E22sweep
already run. Do not claim these current gaps remain uninstalled just because our
older submissions were. Contributor genuineS01P1reproduction not our009harness
approval. No old guard/rate-law/entrypoint/uploader/chronicler work executed.

Review actions:
1 Reproduce all16inline owned files +4fresh public deps and full9method normal/-O,
  10wrong-model/mode,8formal controls. Same original verified runtime/Mathlib in
  submitter repeat is NOT independent clean bootstrap or approval.
2 Read exact generic hypotheses; no alpha<1 required finite, but needed for a
  decaying geometric estimate; nonzero forcing variation need not give error0.
3 Verify definition-level phaseInput/interface alignment, startup guard n>=D,
  NEW gated B mapping, C pre-phase read, R afterC, circular not Euclidean motion.
4 Review numeric beta0 channel distinction:10inputs only reconstructed from actual
  arguments, not observable C innovation;360others actually decoded. No hidden skip.
5 Review new012clarification to011validation wording: no state.validate capacity/
  gap/reachability guarantee. Prior011science intact; no in-place completed edit.
6 Treat uniform-variation/reported-R bounds as paper+finite checks here, not extra
  compiled rate/ON/OFF/freezing/locking results. No new ART/authority pin requested.

Only separately reviewed new-file intake after owner/seat decision. No frozen
ART-0050/ART-0702/registry/lock/source patch, integration, remote branch/push/PR/
contact/upload/merge or unattended013. Possible next boundary ONLY another Continue
and fresh check: smallest formally composed reported-R envelope from this budget,
without assuming a sharp future band or coupled phase locking. Not selected013.
```

### review_decision.json

```json
{
  "role": "Researcher040282 supporting Researcher001 and AuditorSeat002",
  "decision": "One standalone unregistered causal EMA-tracking candidate, local evidence only; independent012review and project integration pending",
  "question": "What finite tracking error does the actual old-input EMA accumulate from a moving wrapped delayed phasor, including constant startup and alpha1float endpoint?",
  "novelty": "Standard linear-filter error/convolution mathematics formalized at the source-faithful phase/EMA boundary, not a new physical discovery or engine bug",
  "scope": "Three new named claims,28old dependencies recompiled without new labels; six short intact-engine cases, expectations and derived tables before acquired import",
  "fresh_coordination": "42main/12retained inbox texts,22heads,1openPR24R-frozen gate/controller persistence. New-main E19-E21/E24-E26 context acknowledged; E22alreadyrun. No parallel guard/rate-law/entrypoint/uploader/chronicler work",
  "new_numbered_clarification": "011table overstated DynamicState.validate as gap checking; actual structural/finite checks only, advance post-gate checks gap.012corrects this without editing delivered011or rerunning its science",
  "not_approved": [
    "Independent012seat review, library project integration, authority/registry/lock/freeze or paper promotion",
    "Universal Python/NumPy floating remainder/trig/EMA FFI or entire coupled C/R/B/phase evolution equivalence",
    "Closed-loop phase synchronization/locking/convergence, strict future Rbands or common finite freeze time",
    "Inferring float alpha<1 from ideal physicalAlpha strict inequality, or decoding C input by dividing beta0",
    "Calling alpha0a valid source configuration; calling ten alpha1formula-only inputs decoded source innovations",
    "Using expected values from target outputs, comparing only safe bounds rather than actual wrong-bound violations, tuning tolerances after target",
    "Crediting draft/import/identifier/parse/setup/runtime/timeout failures as successful mathematical falsifiers",
    "A real S01/production/baseline/shuffle/intervention/CLI/writer/certificate or prior guard installation/re-review",
    "Remote branch/push/PR/contact/upload/merge, frozen source/registry/lock edit or unattended013"
  ],
  "next_cycle_candidate_not_executed": "Only another Continue and fresh feedback/source/library/nonduplication check: consider smallest exact reported-R envelope composition from the causal tracking budget, without assuming sharp future bands or coupled locking. No013selection/preregistration/setup/test begun."
}
```

### nonduplication_check.json

```json
{
  "transport": "Read-only Git heads/tree, selected raw files; public PR HTML separately inspected",
  "branch_count": 22,
  "branches": [
    {
      "branch": "arena/8aa39f3a-aiefs",
      "commit": "6f7471c86507daba193cf924f3fad98822a30f02"
    },
    {
      "branch": "arena/d4a487cc-aiefs",
      "commit": "2af3859eefbec5ced8a434711cdd03ee6c2ade04"
    },
    {
      "branch": "arena/eae4f5a6-aiefs",
      "commit": "bf0c62d985f2c5257eddb66d0207df8f7ba1deab"
    },
    {
      "branch": "audit-inbox",
      "commit": "b61f4340a4dfc9ae5b2732e51efeb49d0c10bd3d"
    },
    {
      "branch": "ci/check-sha256sums",
      "commit": "aababfe5178fd8f1ab4edf55c1647dec2f0f96ce"
    },
    {
      "branch": "fix/040282-f4-f6-f7",
      "commit": "19f0786ca0a5ce1c1b93f230ec7605089f267ce4"
    },
    {
      "branch": "fix/check-manifest-g1g2",
      "commit": "13a01d1222a5f76c3e6b0b3ba728c6b35539570b"
    },
    {
      "branch": "fix/comparator-v4-from-main",
      "commit": "c0fc70bad9c75218526124496cedc07f4504f987"
    },
    {
      "branch": "fix/comparator-v4-gates",
      "commit": "902abe8b2bdaabf13ee3060dce1e3e7da72ded18"
    },
    {
      "branch": "fix/lint-claims-combined",
      "commit": "382ccdb9d19b2c7f1dd3c23aa0ff774f56c5a5a8"
    },
    {
      "branch": "fix/manifest-nonempty",
      "commit": "92993ebc8b128d4f758083bcc8518e27a70a0b7f"
    },
    {
      "branch": "fix/r026-cleanup",
      "commit": "9538706197ee49c44779a73b323377f3d72c77c0"
    },
    {
      "branch": "fix/upload-new-f1f2",
      "commit": "9229817b451c6176b9bf856354a760f52adba8d0"
    },
    {
      "branch": "fix/v41-followup-notes",
      "commit": "314daa3b2eaa944b1c3930e66ecbc4bb6e10067e"
    },
    {
      "branch": "fix/v41-trust-anchor",
      "commit": "df01b346a785a1384d63029e258a3ba5e35f547d"
    },
    {
      "branch": "fix/v41-trust-anchor-followup",
      "commit": "137c2a222495f702ea6bc6896de3324f107e8588"
    },
    {
      "branch": "main",
      "commit": "543e7e1aaa11e4c810783806cb180eee36ec5313"
    },
    {
      "branch": "research/aiefs-northstar-evaluation",
      "commit": "003522e2e9c5b10b94d7f2b0811c7986059a75c0"
    },
    {
      "branch": "research/lean-gate-identities",
      "commit": "a1b54719d68151fa876f19c5f462da03b683f74c"
    },
    {
      "branch": "research/lean-gate-p2",
      "commit": "c8a40ab3323530474f068b61d44c5eba074afe37"
    },
    {
      "branch": "research/lean-gate-p3",
      "commit": "4c1b673f0a41e2752afdd373a7eaea5c1e9582de"
    },
    {
      "branch": "research/rate-law-delta-sweep",
      "commit": "21870922dae696ec8ae5059d73f4f76ec5920013"
    }
  ],
  "candidate_name_matches": [],
  "public_PR_HTML": {
    "url": "https://github.com/jacobbrainard84-knightninja/AIEFS/pulls",
    "open_count": 1,
    "entries": [
      {
        "number": 24,
        "title": "Lean P3: pinned CCtrl/vCtrl bridge + n-step branch persistence",
        "relevance": "P3 active controller-fiber bridge/persistence with R frozen; PR body scope excludes phase/EMA closed-loop; not EMA-tracking result. Do not duplicate P1-P3."
      }
    ]
  },
  "scope": "Limited public navigation and current selected library, not exhaustive/private assurance",
  "selected_library_keyword_scope": "Fresh42main texts incl GateCore P1/P2; no EMA trajectory/tracking implementation in selected current library; previous owned004 defines EMA and fixed/shared-input facts only;011 gives phasor increment/chord, no tracking bound",
  "read_only_scope": "No contributed reproducer, mutation/checker, new-study or PR code executed; no source/current registry/lock edits"
}
```

### review_intake.json

```json
{
  "current_main": "543e7e1aaa11e4c810783806cb180eee36ec5313",
  "inbox": "b61f4340a4dfc9ae5b2732e51efeb49d0c10bd3d",
  "engine_scope": "Current exact engine read; unchanged previous read content, no defect finding from metadata",
  "new_main_context": [
    "E19-E21/new-file F4/F6/F7 successors now on main; previous submission/install status was historical, not current absence",
    "E22 rate-law sweep landed and remains UNEXPLAINED under rule; no duplicate sweep",
    "Gate P1/P2 landed; P3 PR24 active, R frozen/controller bridge/persistence, not phase/EMA tracking",
    "E24-E26 candidate trust-anchor work landed; new independent P1 reproduction and real S01 trusted-input positive are contributors own scope, not our009 control harness approval"
  ],
  "inbox_new_entrypoint_checker": "Read proposal/evidence only; do not acquire/execute or duplicate",
  "targeted_R040282_intake_and_R001_notes": "Unchanged; no independent010/011 or planned012 review found",
  "reproducer_scripts_acquired_or_executed": false,
  "public_inspection_non_exhaustive_private_coordination_assurance": false,
  "irrelevant_PII_path_selection": "Quarantined in own excluded cache without printing contact; omitted retained evidence, to be removed with setup cache"
}
```

### compiler_setup.json

```json
{
  "toolchain": "leanprover/lean4:v4.33.1",
  "compiler_version": "Lean (version 4.33.1, x86_64-unknown-linux-gnu, commit 819816b2e0a3bf405af45ae5c7af2491d8f5bee6, Release)",
  "public_asset_verified": true,
  "download_bytes": 570405234,
  "complete_runtime_extracted_members": 18130,
  "complete_runtime_extracted_bytes": 3037354159,
  "compiler_binary": "/home/user/.cache/researcher040282-cycle012/lean-4.33.1-linux/bin/lean",
  "cache": "/home/user/.cache/researcher040282-cycle012",
  "Mathlib_installed": false,
  "global_toolchain_changed": false,
  "decoder_installed_into_disposable_target": true,
  "decoder_version": "0.25.0",
  "cache_excluded_from_packet_and_to_be_removed_after_reproduction": true,
  "elapsed_seconds": 41.58987966400002
}
```

### mathlib_setup.json

```json
{
  "mathlib_revision": "0df444a360eaa60ab8c11dca51a86af692955474",
  "compiler_version": "Lean (version 4.33.1, x86_64-unknown-linux-gnu, commit 819816b2e0a3bf405af45ae5c7af2491d8f5bee6, Release)",
  "compiler_prescription": "leanprover/lean4:v4.33.1",
  "mathlib_directory": "/home/user/.cache/researcher040282-cycle012/mathlib4",
  "compiler_binary": "/home/user/.cache/researcher040282-cycle012/lean-4.33.1-linux/bin/lean",
  "cache": "/home/user/.cache/researcher040282-cycle012",
  "targeted_roots": [
    "Mathlib/Analysis/SpecialFunctions/Trigonometric/Bounds.lean",
    "Mathlib/Algebra/Order/Archimedean/Real/Basic.lean",
    "Mathlib/Tactic/Ring.lean",
    "Mathlib/Tactic/FieldSimp.lean",
    "Mathlib/Tactic/NormNum.lean",
    "Mathlib/Tactic/Linarith.lean",
    "Mathlib/Analysis/SpecificLimits/Normed.lean",
    "Mathlib/Tactic/Positivity.lean"
  ],
  "targeted_not_omnibus_Mathlib": true,
  "cache_helper_returncode": 0,
  "owned_regular_file_logical_bytes": 6021761311,
  "all_setup_cache_download_targets_inside_own_prefix": true,
  "global_toolchain_changed": false,
  "raw_git_objects_not_copied_to_packet": true,
  "remove_only_own_cache_after_full_extracted_reproduction": true,
  "elapsed_seconds": 53.50482302099999
}
```

### selection_refinement.json

```json
{
  "issue": "Substring ema matched email/schema in initial bounded navigation selection",
  "irrelevant_salvage_PII_note_not_used_as_evidence": true,
  "raw_not_in_packet": "Confined to own excluded disposable cache until cleanup",
  "email_pattern_count_only": 1,
  "personal_values_printed": false,
  "source_executed": false,
  "all_retained_acquired_evidence_bytes_unmodified": true
}
```

### historical_restoration.json

```json
{
  "prior_archive": "researcher040282-cycle011-modulo-phase-increment.zip",
  "nonlive_members_checked": 1504,
  "missing_before_administrative_recovery": [
    {
      "path": "cycle_006/source_state/main/.github/workflows/repo-checks.yml",
      "bytes": 9175
    }
  ],
  "missing_only_restored": 1,
  "all_recovered_bytes_equal_delivered_members": true,
  "existing_files_overwritten": false,
  "historical_science_rerun": false,
  "scientific012_inputs_code_results_changed": false,
  "legacy_deleted_Lua_restored": false,
  "user_deleted_legacy_Lua_absent": true
}
```


## 8 · Handoff, preservation and stop

For001/Seat002: independently inspect one new-file causal EMA tracking result set,
not an engine fix or physical locking claim. Review source time index, initial
error/weight ordering, alpha1channel distinction, definition-level component
composition and precise domains. Owner handles separately dated inbox upload;
no remote branch/push/PR/contact/upload/merge, frozen/registry/lock or production
helper change by agent. All current proposals unreviewed locally unless explicitly
stated for the contributors' OWN separate scopes.

Previous011state/ledger snapshot protected.1504prior011nonlive members checked;
missing-only9175-byte old006CI workflow copy restored exactly from delivered011ZIP,
no existing file overwritten, old science rerun or deleted Lua restored. Current
all ledger citations/logs unpacked/indexed; historical archives separate, not nested.
Packet/privacy/CRC/member/preservation closure is local administrative consistency,
not independent review/security/authority certification. No active stdout capture
is included while being written by final validator.

Optional evidence ZIP: `researcher040282-cycle012-causal-ema-tracking.zip`.
**Stop here.** Only another Continue: fresh feedback/source/library/nonduplication,
then consider smallest formally composed reported-R envelope from this budget,
without assuming sharp future bands or coupled locking. No013work started.

## 9 · Complete critical owned code

### CoherenceEMA.lean

<!-- BEGIN_CRITICAL_FILE: CoherenceEMA.lean -->
```lean
/-
Researcher 040282: exact-real complex EMA and reported coherence component.
Prescribed real phase/delayed vectors are inputs, not a proof of coupled locking.
C is directed and may have a nonzero diagonal. Only reported R is symmetrized
and zero-diagonal. The source returns R AFTER updating C.
-/
import Mathlib.Analysis.Complex.Basic
import Mathlib.Analysis.Complex.Trigonometric
import Mathlib.Analysis.SpecificLimits.Normed
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Ring

set_option autoImplicit false
set_option linter.style.header false

open Filter
open scoped Topology

namespace Researcher040282.EMA

variable {ι : Type*}

abbrev ComplexWeights (ι : Type*) := ι → ι → ℂ

noncomputable def physicalAlpha (dt Tw : ℝ) : ℝ := Real.exp (-dt / Tw)

noncomputable def phaseInput (theta delayed omega : ι → ℝ) (tau : ℝ)
    (i j : ι) : ℂ :=
  Complex.exp (((theta i - delayed j - ((omega i + omega j) / 2) * tau : ℝ) : ℂ) * Complex.I)

noncomputable def emaStep (alpha : ℝ) (C z : ℂ) : ℂ :=
  (alpha : ℂ) * C + ((1 - alpha : ℝ) : ℂ) * z

noncomputable def emaTrajectory (alpha : ℝ) (C0 : ℂ) (z : ℕ → ℂ) : ℕ → ℂ
  | 0 => C0
  | n + 1 => emaStep alpha (emaTrajectory alpha C0 z n) (z n)

noncomputable def coherenceUpdate (alpha : ℝ) (C : ComplexWeights ι)
    (theta delayed omega : ι → ℝ) (tau : ℝ) : ComplexWeights ι :=
  fun i j => emaStep alpha (C i j) (phaseInput theta delayed omega tau i j)

noncomputable def reportedR (C : ComplexWeights ι) (i j : ι) : ℝ := by
  classical
  exact if i = j then 0 else (‖C i j‖ + ‖C j i‖) / 2

noncomputable def matrixTrajectory (alpha : ℝ) (C0 : ComplexWeights ι)
    (z : ℕ → ComplexWeights ι) (n : ℕ) : ComplexWeights ι :=
  fun i j => emaTrajectory alpha (C0 i j) (fun m => z m i j) n

theorem phaseInput_norm (theta delayed omega : ι → ℝ) (tau : ℝ) (i j : ι) :
    ‖phaseInput theta delayed omega tau i j‖ = 1 := by
  simp [phaseInput, Complex.norm_exp]

theorem physicalAlpha_pos (dt Tw : ℝ) : 0 < physicalAlpha dt Tw :=
  Real.exp_pos _

theorem physicalAlpha_lt_one (dt Tw : ℝ) (hdt : 0 < dt) (hTw : 0 < Tw) :
    physicalAlpha dt Tw < 1 := by
  rw [physicalAlpha, Real.exp_lt_one_iff, neg_div]
  have := div_pos hdt hTw
  linarith

theorem emaStep_norm_le (alpha : ℝ) (C z : ℂ)
    (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) :
    ‖emaStep alpha C z‖ ≤ alpha * ‖C‖ + (1-alpha) * ‖z‖ := by
  calc
    ‖emaStep alpha C z‖ ≤ ‖(alpha : ℂ) * C‖ + ‖((1-alpha : ℝ) : ℂ) * z‖ :=
      norm_add_le _ _
    _ = alpha * ‖C‖ + (1-alpha) * ‖z‖ := by
      rw [norm_mul, norm_mul, Complex.norm_of_nonneg ha0,
        Complex.norm_of_nonneg (sub_nonneg.mpr ha1)]

theorem emaStep_unitDisk (alpha : ℝ) (C z : ℂ)
    (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) (hC : ‖C‖ ≤ 1) (hz : ‖z‖ ≤ 1) :
    ‖emaStep alpha C z‖ ≤ 1 := by
  calc
    ‖emaStep alpha C z‖ ≤ alpha * ‖C‖ + (1-alpha) * ‖z‖ :=
      emaStep_norm_le alpha C z ha0 ha1
    _ ≤ alpha * 1 + (1-alpha) * 1 :=
      add_le_add (mul_le_mul_of_nonneg_left hC ha0)
        (mul_le_mul_of_nonneg_left hz (sub_nonneg.mpr ha1))
    _ = 1 := by ring

theorem emaTrajectory_unitDisk (alpha : ℝ) (C0 : ℂ) (z : ℕ → ℂ)
    (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) (hC : ‖C0‖ ≤ 1)
    (hz : ∀ n, ‖z n‖ ≤ 1) : ∀ n, ‖emaTrajectory alpha C0 z n‖ ≤ 1 := by
  intro n
  induction n with
  | zero => exact hC
  | succ n ih => exact emaStep_unitDisk alpha _ _ ha0 ha1 ih (hz n)

theorem coherenceUpdate_unitDisk (alpha : ℝ) (C : ComplexWeights ι)
    (theta delayed omega : ι → ℝ) (tau : ℝ)
    (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) (hC : ∀ i j, ‖C i j‖ ≤ 1) :
    ∀ i j, ‖coherenceUpdate alpha C theta delayed omega tau i j‖ ≤ 1 := by
  intro i j
  exact emaStep_unitDisk alpha _ _ ha0 ha1 (hC i j)
    (phaseInput_norm theta delayed omega tau i j).le

theorem reportedR_nonneg (C : ComplexWeights ι) (i j : ι) :
    0 ≤ reportedR C i j := by
  classical
  unfold reportedR
  split_ifs <;> positivity

theorem reportedR_symmetric (C : ComplexWeights ι) (i j : ι) :
    reportedR C i j = reportedR C j i := by
  classical
  by_cases h : i = j
  · subst j; rfl
  · simp only [reportedR, if_neg h, if_neg (Ne.symm h)]
    ring

theorem reportedR_diag (C : ComplexWeights ι) (i : ι) : reportedR C i i = 0 := by
  simp [reportedR]

theorem reportedR_le_one (C : ComplexWeights ι) (hC : ∀ i j, ‖C i j‖ ≤ 1) (i j : ι) :
    reportedR C i j ≤ 1 := by
  classical
  by_cases h : i = j
  · simp [reportedR, h]
  · simp only [reportedR, if_neg h]
    have := hC i j
    have := hC j i
    linarith

theorem reportedR_lipschitz (C D : ComplexWeights ι) (i j : ι) :
    |reportedR C i j - reportedR D i j| ≤
      (‖C i j - D i j‖ + ‖C j i - D j i‖) / 2 := by
  classical
  by_cases h : i = j
  · subst j
    rw [reportedR_diag, reportedR_diag, sub_self, abs_zero]
    exact div_nonneg (add_nonneg (norm_nonneg _) (norm_nonneg _)) (by norm_num)
  · simp only [reportedR, if_neg h]
    have h1 := abs_norm_sub_norm_le (C i j) (D i j)
    have h2 := abs_norm_sub_norm_le (C j i) (D j i)
    rw [show (‖C i j‖ + ‖C j i‖) / 2 - (‖D i j‖ + ‖D j i‖) / 2 =
      ((‖C i j‖ - ‖D i j‖) + (‖C j i‖ - ‖D j i‖)) / 2 by ring,
      abs_div, abs_of_pos (by norm_num : (0 : ℝ) < 2)]
    exact div_le_div_of_nonneg_right
      ((abs_add_le _ _).trans (add_le_add h1 h2)) (by norm_num)

theorem ema_difference (alpha : ℝ) (C D z w : ℂ) :
    emaStep alpha C z - emaStep alpha D w =
      (alpha : ℂ) * (C-D) + ((1-alpha : ℝ) : ℂ) * (z-w) := by
  unfold emaStep
  ring

theorem ema_same_input_difference (alpha : ℝ) (C D z : ℂ) :
    emaStep alpha C z - emaStep alpha D z = (alpha : ℂ) * (C-D) := by
  rw [ema_difference, sub_self, mul_zero, add_zero]

theorem trajectory_same_input_difference (alpha : ℝ) (C0 D0 : ℂ)
    (z : ℕ → ℂ) (n : ℕ) :
    emaTrajectory alpha C0 z n - emaTrajectory alpha D0 z n =
      (alpha : ℂ)^n * (C0-D0) := by
  induction n with
  | zero => simp [emaTrajectory]
  | succ n ih =>
    change emaStep alpha (emaTrajectory alpha C0 z n) (z n) -
      emaStep alpha (emaTrajectory alpha D0 z n) (z n) = _
    rw [ema_same_input_difference, ih, pow_succ]
    ring

theorem trajectory_same_input_norm (alpha : ℝ) (C0 D0 : ℂ)
    (z : ℕ → ℂ) (n : ℕ) (ha0 : 0 ≤ alpha) :
    ‖emaTrajectory alpha C0 z n - emaTrajectory alpha D0 z n‖ =
      alpha^n * ‖C0-D0‖ := by
  rw [trajectory_same_input_difference, norm_mul, norm_pow, Complex.norm_of_nonneg ha0]

theorem constant_closed_form (alpha : ℝ) (C0 z : ℂ) (n : ℕ) :
    emaTrajectory alpha C0 (fun _ => z) n = z + (alpha : ℂ)^n * (C0-z) := by
  induction n with
  | zero =>
    simp only [emaTrajectory, pow_zero, one_mul]
    ring
  | succ n ih =>
    change emaStep alpha (emaTrajectory alpha C0 (fun _ => z) n) z = _
    rw [ih]
    simp only [emaStep, pow_succ]
    push_cast
    ring

theorem constant_error_norm (alpha : ℝ) (C0 z : ℂ) (n : ℕ) (ha0 : 0 ≤ alpha) :
    ‖emaTrajectory alpha C0 (fun _ => z) n - z‖ = alpha^n * ‖C0-z‖ := by
  rw [constant_closed_form]
  rw [show z + (alpha : ℂ)^n * (C0-z) - z = (alpha : ℂ)^n * (C0-z) by ring]
  rw [norm_mul, norm_pow, Complex.norm_of_nonneg ha0]

theorem constant_zero_norm (alpha : ℝ) (z : ℂ) (n : ℕ)
    (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) (hz : ‖z‖ = 1) :
    ‖emaTrajectory alpha 0 (fun _ => z) n‖ = 1-alpha^n := by
  have heq : emaTrajectory alpha 0 (fun _ => z) n = ((1-alpha^n : ℝ) : ℂ) * z := by
    rw [constant_closed_form]
    push_cast
    ring
  rw [heq, norm_mul, Complex.norm_of_nonneg (sub_nonneg.mpr (pow_le_one₀ ha0 ha1)),
    hz, mul_one]

theorem constant_converges (alpha : ℝ) (C0 z : ℂ) (ha0 : 0 ≤ alpha) (ha1 : alpha < 1) :
    Tendsto (emaTrajectory alpha C0 (fun _ => z)) atTop (𝓝 z) := by
  have hp : Tendsto (fun n : ℕ => (alpha : ℂ)^n) atTop (𝓝 0) :=
    tendsto_pow_atTop_nhds_zero_of_norm_lt_one (by
      rw [Complex.norm_of_nonneg ha0]
      exact ha1)
  have ht : Tendsto (fun n : ℕ => z + (alpha : ℂ)^n * (C0-z)) atTop
      (𝓝 (z + 0 * (C0-z))) := tendsto_const_nhds.add (hp.mul_const (C0-z))
  have heq : emaTrajectory alpha C0 (fun _ => z) =
      (fun n => z + (alpha : ℂ)^n * (C0-z)) :=
    funext (fun n => constant_closed_form alpha C0 z n)
  rw [heq]
  simpa only [zero_mul, add_zero] using ht

theorem matrix_same_input_reported_bound (alpha : ℝ) (C0 D0 : ComplexWeights ι)
    (z : ℕ → ComplexWeights ι) (n : ℕ) (ha0 : 0 ≤ alpha) (i j : ι) :
    |reportedR (matrixTrajectory alpha C0 z n) i j -
      reportedR (matrixTrajectory alpha D0 z n) i j| ≤
      alpha^n * (‖C0 i j - D0 i j‖ + ‖C0 j i - D0 j i‖) / 2 := by
  calc
    _ ≤ (‖matrixTrajectory alpha C0 z n i j - matrixTrajectory alpha D0 z n i j‖ +
        ‖matrixTrajectory alpha C0 z n j i - matrixTrajectory alpha D0 z n j i‖) / 2 :=
      reportedR_lipschitz _ _ i j
    _ = _ := by
      simp only [matrixTrajectory, trajectory_same_input_norm alpha _ _ _ n ha0]
      ring

theorem constant_zero_reported (alpha : ℝ) (z : ComplexWeights ι) (n : ℕ)
    (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) (hz : ∀ i j, ‖z i j‖ = 1)
    (i j : ι) (hij : i ≠ j) :
    reportedR (matrixTrajectory alpha (fun _ _ => 0) (fun _ => z) n) i j =
      1-alpha^n := by
  simp only [reportedR, if_neg hij, matrixTrajectory]
  rw [constant_zero_norm alpha (z i j) n ha0 ha1 (hz i j),
    constant_zero_norm alpha (z j i) n ha0 ha1 (hz j i)]
  ring

end Researcher040282.EMA

-- Closed-file audit queries.
#print axioms Researcher040282.EMA.phaseInput_norm
#print axioms Researcher040282.EMA.physicalAlpha_pos
#print axioms Researcher040282.EMA.physicalAlpha_lt_one
#print axioms Researcher040282.EMA.emaStep_norm_le
#print axioms Researcher040282.EMA.emaStep_unitDisk
#print axioms Researcher040282.EMA.emaTrajectory_unitDisk
#print axioms Researcher040282.EMA.coherenceUpdate_unitDisk
#print axioms Researcher040282.EMA.reportedR_nonneg
#print axioms Researcher040282.EMA.reportedR_symmetric
#print axioms Researcher040282.EMA.reportedR_diag
#print axioms Researcher040282.EMA.reportedR_le_one
#print axioms Researcher040282.EMA.reportedR_lipschitz
#print axioms Researcher040282.EMA.ema_difference
#print axioms Researcher040282.EMA.ema_same_input_difference
#print axioms Researcher040282.EMA.trajectory_same_input_difference
#print axioms Researcher040282.EMA.trajectory_same_input_norm
#print axioms Researcher040282.EMA.constant_closed_form
#print axioms Researcher040282.EMA.constant_error_norm
#print axioms Researcher040282.EMA.constant_zero_norm
#print axioms Researcher040282.EMA.constant_converges
#print axioms Researcher040282.EMA.matrix_same_input_reported_bound
#print axioms Researcher040282.EMA.constant_zero_reported
```
<!-- END_CRITICAL_FILE: CoherenceEMA.lean -->

### EMATracking.lean

<!-- BEGIN_CRITICAL_FILE: EMATracking.lean -->
```lean
/-
Causal tracking of a moving phasor input by the actual old-input EMA recurrence.
Exact-real component composition, not floating FFI or closed-loop phase locking.
Finite bounds require alpha nonnegative, not strict contraction or alpha < 1.
-/
import CoherenceEMA
import PhaseIncrement

set_option autoImplicit false
set_option linter.style.header false

open scoped BigOperators

namespace Researcher040282.Tracking

open Researcher040282.EMA

variable {ι : Type*}

noncomputable def trackingBudget (alpha E0 : ℝ) (a : ℕ → ℝ) (n : ℕ) : ℝ :=
  alpha ^ n * E0 + ∑ k ∈ Finset.range n, alpha ^ (n - 1 - k) * a k

noncomputable def delayedPhaseInput (d : ℕ) (x0 : ι → ℝ) (u : ℕ → ι → ℝ)
    (omega : ι → ℝ) (tau : ℝ) (n : ℕ) (i j : ι) : ℂ :=
  phaseInput (Researcher040282.Phase.phaseTrace x0 u n)
    (Researcher040282.Delay.historyTrace d (Researcher040282.Phase.phaseTrace x0 u) n
      ⟨0, Nat.zero_lt_succ d⟩) omega tau i j

/-- Input motion has coefficient one: C_(n+1) consumes z_n, not z_(n+1). -/
theorem tracking_error_step (alpha : ℝ) (C0 : ℂ) (z : ℕ → ℂ) (n : ℕ) :
    emaTrajectory alpha C0 z (n + 1) - z (n + 1) =
      (alpha : ℂ) * (emaTrajectory alpha C0 z n - z n) - (z (n + 1) - z n) := by
  change emaStep alpha (emaTrajectory alpha C0 z n) (z n) - z (n + 1) = _
  unfold emaStep
  push_cast
  ring

/-- The newest input variation has weight one; initial error is not discarded. -/
theorem tracking_error_budget (alpha : ℝ) (C0 : ℂ) (z : ℕ → ℂ)
    (ha : 0 ≤ alpha) (n : ℕ) :
    ‖emaTrajectory alpha C0 z n - z n‖ ≤
      trackingBudget alpha ‖C0 - z 0‖ (fun k => ‖z (k + 1) - z k‖) n := by
  have hb (E0 : ℝ) (a : ℕ → ℝ) (m : ℕ) :
      trackingBudget alpha E0 a (m + 1) = alpha * trackingBudget alpha E0 a m + a m := by
    unfold trackingBudget
    rw [Finset.sum_range_succ]
    have hs : (∑ k ∈ Finset.range m, alpha ^ (m + 1 - 1 - k) * a k) =
        alpha * ∑ k ∈ Finset.range m, alpha ^ (m - 1 - k) * a k := by
      rw [Finset.mul_sum]
      apply Finset.sum_congr rfl
      intro k hk
      have hk0 : k < m := Finset.mem_range.mp hk
      have he : m + 1 - 1 - k = (m - 1 - k) + 1 := by omega
      rw [he, pow_succ]
      ring
    rw [hs]
    have ht : m + 1 - 1 - m = 0 := by omega
    rw [ht, pow_zero, one_mul, pow_succ]
    ring
  induction n with
  | zero => simp [emaTrajectory, trackingBudget]
  | succ n ih =>
      calc
        ‖emaTrajectory alpha C0 z (n + 1) - z (n + 1)‖ =
            ‖(alpha : ℂ) * (emaTrajectory alpha C0 z n - z n) - (z (n + 1) - z n)‖ := by
          rw [tracking_error_step]
        _ ≤ ‖(alpha : ℂ) * (emaTrajectory alpha C0 z n - z n)‖ + ‖z (n + 1) - z n‖ :=
          norm_sub_le _ _
        _ = alpha * ‖emaTrajectory alpha C0 z n - z n‖ + ‖z (n + 1) - z n‖ := by
          rw [norm_mul, Complex.norm_of_nonneg ha]
        _ ≤ alpha * trackingBudget alpha ‖C0 - z 0‖ (fun k => ‖z (k + 1) - z k‖) n +
            ‖z (n + 1) - z n‖ :=
          add_le_add (mul_le_mul_of_nonneg_left ih ha) le_rfl
        _ = trackingBudget alpha ‖C0 - z 0‖ (fun k => ‖z (k + 1) - z k‖) (n + 1) :=
          (hb _ _ n).symm

/-- Definition-level composition of the old EMA and startup-aware delayed phasor. -/
theorem delayed_phase_tracking_budget (alpha : ℝ) (C0 : ℂ) (ha : 0 ≤ alpha)
    (d : ℕ) (x0 : ι → ℝ) (u : ℕ → ι → ℝ) (omega : ι → ℝ) (tau : ℝ)
    (n : ℕ) (i j : ι) :
    ‖emaTrajectory alpha C0 (fun k => delayedPhaseInput d x0 u omega tau k i j) n -
        delayedPhaseInput d x0 u omega tau n i j‖ ≤
      trackingBudget alpha ‖C0 - delayedPhaseInput d x0 u omega tau 0 i j‖
        (fun k => |u k i - Researcher040282.Phase.delayedIncrement d u k j|) n := by
  apply (tracking_error_budget alpha C0 (fun k => delayedPhaseInput d x0 u omega tau k i j) ha n).trans
  unfold trackingBudget
  apply add_le_add le_rfl
  apply Finset.sum_le_sum
  intro k _
  apply mul_le_mul_of_nonneg_left _ (pow_nonneg ha _)
  change ‖Researcher040282.Phase.inputPhasor d x0 u omega tau (k + 1) i j -
      Researcher040282.Phase.inputPhasor d x0 u omega tau k i j‖ ≤ _
  exact Researcher040282.Phase.delayed_input_chord_bound d x0 u omega tau k i j

#print axioms Researcher040282.Tracking.tracking_error_step
#print axioms Researcher040282.Tracking.tracking_error_budget
#print axioms Researcher040282.Tracking.delayed_phase_tracking_budget

end Researcher040282.Tracking
```
<!-- END_CRITICAL_FILE: EMATracking.lean -->

### tracking_contract.py

<!-- BEGIN_CRITICAL_FILE: tracking_contract.py -->
```python
"""Pure immutable012 tracking oracle. No NumPy or acquired engine import.
Old scalar/phasor definitions reused explicitly; full expectations precede import.
"""
from dataclasses import dataclass,replace
import math
from step_contract import Case,Parameters,base_case,drift_case,matrix,reference,shadow_after
from phase_contract import Frame,increment,input_phasor,phasor

ABS_TOL=5e-13
MIN_WITNESS=1e-7
STEPS=10

@dataclass(frozen=True)
class Trace:
    initial:Case
    frames:tuple[Frame,...]
    phase_values:tuple[tuple[float,...],...]

def alpha(trace):return math.exp(-trace.initial.p.dt/trace.initial.p.T_window)

def cases():
    active=base_case('active_N3_D2',2,True);active=replace(active,theta=(math.tau-.015,1.27,4.13))
    slow=base_case('slow_negative_N3_D3',3,True)
    slow=replace(slow,p=replace(slow.p,omega=(-1.0,.75,1.5),T_window=2.0),theta=(.01,1.27,4.13))
    theta=(.31,1.27,4.13,2.71)
    fast=Case('fast_multiwrap_N4_D4',Parameters(4,.125,.5,(161.0,-143.0,27.0,1.25),eta=3.0,T_window=.125),theta,
              matrix(4,lambda i,j:0.0 if i==j else .04*(1+i+j)),matrix(4,lambda i,j:0j),())
    matched=drift_case(3);matched=replace(matched,name='matched_start_N1_D3',theta=(6.1,),C=((phasor(-.375),),))
    endpoint=drift_case(2);endpoint=replace(endpoint,name='rounded_alpha1_N1_D2',theta=(6.1,),p=replace(endpoint.p,T_window=1e20),C=((.3+.4j,),))
    tail=drift_case(1);tail=replace(tail,name='fast_tail_N1_D1',p=replace(tail.p,T_window=.0625))
    return tuple(replace(c,history=tuple(c.theta for _ in range(round(c.p.tau/c.p.dt)+1))) for c in (active,slow,fast,matched,endpoint,tail))

def prepare_traces():
    out=[]
    for first in cases():
        shadow=first;values=[first.theta];frames=[];d=round(first.p.tau/first.p.dt)
        for n in range(STEPS):
            if shadow.history[0]!=values[max(0,n-d)]:raise RuntimeError('Independent history-age design mismatch')
            prediction=reference(shadow);u=increment(shadow,prediction);z=input_phasor(shadow,values[max(0,n-d)])
            frames.append(Frame(shadow,prediction,u,z,tuple(math.floor((shadow.theta[i]+u[i])/math.tau) for i in range(shadow.p.N))))
            values.append(prediction.theta);shadow=shadow_after(shadow,prediction)
        out.append(Trace(first,tuple(frames),tuple(values)))
    return tuple(out)

def error(trace,n,i,j):return trace.frames[n].case.C[i][j]-trace.frames[n].input_phasor[i][j]
def delta(trace,k,i,j):return trace.frames[k+1].input_phasor[i][j]-trace.frames[k].input_phasor[i][j]
def signed_drift(trace,k,i,j,drifting_prehistory=False):
    d=round(trace.initial.p.tau/trace.initial.p.dt)
    late=trace.frames[max(0,k-d)].increment[j] if drifting_prehistory or k>=d else 0.0
    return trace.frames[k].increment[i]-late

def budget(trace,n,i,j,kind='input'):
    a=alpha(trace)
    def variation(k):
        return abs(delta(trace,k,i,j)) if kind=='input' else abs(signed_drift(trace,k,i,j,kind=='drifting_prehistory'))
    return a**n*abs(error(trace,0,i,j))+sum(a**(n-1-k)*variation(k) for k in range(n))

def complex_unroll(trace,n,i,j,reverse=False):
    a=alpha(trace)
    return a**n*error(trace,0,i,j)-sum(a**(k if reverse else n-1-k)*delta(trace,k,i,j) for k in range(n))

def controls(traces):
    by={x.initial.name:x for x in traces};m=by['matched_start_N1_D3'];active=by['active_N3_D2'];endpoint=by['rounded_alpha1_N1_D2']
    a=alpha(m);d=delta(m,0,0,0);e0=error(m,0,0,0)
    out=[]
    def equality(name,field,trace,n,i,j,want,wrong):
        out.append({'model':name,'kind':'equality','field':field,'case':trace.initial.name,'n':n,'i':i,'j':j,'expected':want,'wrong':wrong})
    def upper(name,trace,n,i,j,wrong):
        out.append({'model':name,'kind':'upper_bound','field':'tracking_envelope','case':trace.initial.name,'n':n,'i':i,'j':j,'expected':abs(error(trace,n,i,j)),'wrong':wrong})
    equality('drift_beta','causal_error',m,1,0,0,error(m,1,0,0),a*e0-(1-a)*d)
    equality('drift_plus','causal_error',m,1,0,0,error(m,1,0,0),a*e0+d)
    f=active.frames[0];aa=alpha(active)
    equality('future_input_update','updated_C',active,0,0,1,f.prediction.C[0][1],aa*f.case.C[0][1]+(1-aa)*active.frames[1].input_phasor[0][1])
    upper('omit_variation',m,1,0,0,a*abs(e0))
    upper('newest_weight_alpha',m,1,0,0,a*abs(d))
    equality('reverse_weights','complex_error_unroll',m,2,0,0,error(m,2,0,0),complex_unroll(m,2,0,0,True))
    upper('omit_initial',active,0,0,1,0.0)
    upper('drifting_prehistory',m,1,0,0,budget(m,1,0,0,'drifting_prehistory'))
    equality('alpha1_forced_decay','stationary_tail_error',endpoint,3,0,0,error(endpoint,3,0,0),.5*error(endpoint,2,0,0))
    old_R=(abs(f.case.C[0][1])+abs(f.case.C[1][0]))/2
    equality('stale_reported_R','reported_R',active,0,0,1,f.prediction.R[0][1],old_R)
    return tuple(out)

def difference(row):
    if row['kind']=='upper_bound':return row['expected']-row['wrong']
    a=row['expected'];b=row['wrong']
    return max(abs(a.real-b.real),abs(a.imag-b.imag)) if isinstance(a,complex) or isinstance(b,complex) else abs(a-b)

def control_design(row):
    return {k:v for k,v in row.items() if k not in ('expected','wrong')}|{'intended_witness':difference(row)}

def design_record(traces):
    return {'phase':'Independent pure math/cmath design before acquired module import/advance',
            'cases':[{'name':x.initial.name,'N':x.initial.p.N,'D':round(x.initial.p.tau/x.initial.p.dt),'alpha':alpha(x),'one_minus_alpha':1-alpha(x),
                      'initial_error_max':max(abs(error(x,0,i,j)) for i in range(x.initial.p.N) for j in range(x.initial.p.N)),
                      'first_windings':x.frames[0].windings,'first_gate_active':x.frames[0].prediction.projection_active,
                      'input_channel':'prestate_formula_only_beta0_no_division' if alpha(x)==1 else 'prestate_formula_and_actual_C_innovation'} for x in traces],
            'actual_advances_planned':60,'input_tracking_complex_coordinates_planned':370,'consumed_input_complex_coordinates_planned':370,
            'adjacent_error_recurrences_planned':333,'startup_adjacent_coordinates_planned':115,'first_live_adjacent_coordinates_planned':37,
            'decoded_C_innovation_coordinates_planned':360,'alpha1_reconstructed_input_coordinates_planned':10,
            'reported_R_offdiag_bound_coordinates_planned':240,'reported_R_diag_zero_coordinates_planned':130,
            'ten_wrong_models':[control_design(r) for r in controls(traces)],'absolute_tolerance':ABS_TOL,'relative_tolerance':0.0,
            'alpha0_formal_only_not_source_valid':True,'float_alpha1_source_valid_not_ideal_exp_strictly_less_than_one':True}

@dataclass(frozen=True)
class Cell:
    case:str
    n:int
    i:int
    j:int
    tracking_error:complex
    consumed_error:complex
    complex_unroll:complex
    input_budget:float
    phase_budget:float
    reported_R_bound:float
    next_error_rhs:complex|None
    phase_factor:complex|None
    signed_increment:float|None


def prepare_expectations(traces):
    """All derived budgets/unrolls also completed BEFORE acquired import."""
    out=[]
    for trace in traces:
        a=alpha(trace)
        for n in range(STEPS):
            frame=trace.frames[n]
            for i in range(trace.initial.p.N):
                for j in range(trace.initial.p.N):
                    signed=signed_drift(trace,n,i,j) if n<STEPS-1 else None
                    out.append(Cell(trace.initial.name,n,i,j,error(trace,n,i,j),frame.prediction.C[i][j]-frame.input_phasor[i][j],
                        complex_unroll(trace,n,i,j),budget(trace,n,i,j),budget(trace,n,i,j,'phase'),
                        a*(budget(trace,n,i,j,'phase')+budget(trace,n,j,i,'phase'))/2,
                        a*error(trace,n,i,j)-delta(trace,n,i,j) if n<STEPS-1 else None,
                        phasor(signed) if signed is not None else None,signed))
    return tuple(out)
```
<!-- END_CRITICAL_FILE: tracking_contract.py -->

### HistoryBuffer.lean

<!-- BEGIN_CRITICAL_FILE: HistoryBuffer.lean -->
```lean
/-
Reachable constant-prehistory queue for a D-step delay: D+1 snapshots.
Pure value/index theorem, independent of how the appended trace is generated.
Not a theorem about Python aliasing, floating trigonometry, or phase locking.
-/
import Std

set_option autoImplicit false

universe u

namespace Researcher040282.Delay

abbrev History (d : Nat) (A : Type u) := Fin (d + 1) → A

def shiftAppend {A : Type u} (d : Nat) (h : History d A) (fresh : A) : History d A :=
  fun i => if hi : i.val < d then h ⟨i.val + 1, Nat.succ_lt_succ hi⟩ else fresh

def historyTrace {A : Type u} (d : Nat) (x : Nat → A) : Nat → History d A
  | 0 => fun _ => x 0
  | n + 1 => shiftAppend d (historyTrace d x n) (x (n + 1))

/-- Every queue position, including startup with constant prehistory. -/
theorem historyTrace_index {A : Type u} (d : Nat) (x : Nat → A) :
    ∀ n (i : Fin (d + 1)), historyTrace d x n i = x (n + i.val - d) := by
  intro n
  induction n with
  | zero =>
      intro i
      have hzero : 0 + i.val - d = 0 := by omega
      simp only [historyTrace, hzero]
  | succ n ih =>
      intro i
      simp only [historyTrace, shiftAppend]
      split
      · rename_i hi
        rw [ih]
        congr 1
        change n + (i.val + 1) - d = n + 1 + i.val - d
        omega
      · rename_i hi
        have heq : i.val = d := by omega
        congr 1
        omega

/-- At read time n the oldest phase is n-D, not n-(D+1) or n-D+1. -/
theorem historyTrace_oldest {A : Type u} (d : Nat) (x : Nat → A) (n : Nat) :
    historyTrace d x n ⟨0, Nat.zero_lt_succ d⟩ = x (n - d) := by
  simpa only [Nat.add_zero] using historyTrace_index d x n ⟨0, Nat.zero_lt_succ d⟩

/-- The newest snapshot agrees with the current appended trace value. -/
theorem historyTrace_newest {A : Type u} (d : Nat) (x : Nat → A) (n : Nat) :
    historyTrace d x n ⟨d, Nat.lt_succ_self d⟩ = x n := by
  simpa only [Nat.add_sub_cancel] using historyTrace_index d x n ⟨d, Nat.lt_succ_self d⟩

#print axioms Researcher040282.Delay.historyTrace_index
#print axioms Researcher040282.Delay.historyTrace_oldest
#print axioms Researcher040282.Delay.historyTrace_newest

end Researcher040282.Delay
```
<!-- END_CRITICAL_FILE: HistoryBuffer.lean -->

### PhaseIncrement.lean

<!-- BEGIN_CRITICAL_FILE: PhaseIncrement.lean -->
```lean
/-
Modulo-safe coherence-input motion for a constant-prehistory delay queue.
Exact-real model; arbitrary increments may be feedback-generated. This file does
not formalize floating remainder, allocation, C/R/B evolution or phase locking.
-/
import HistoryBuffer
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Bounds
import Mathlib.Algebra.Order.Archimedean.Real.Basic
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith

set_option autoImplicit false
set_option linter.style.header false

namespace Researcher040282.Phase

variable {ι : Type*}

noncomputable def phasor (t : ℝ) : ℂ := Complex.exp ((t : ℂ) * Complex.I)

noncomputable def wrapPhase (t : ℝ) : ℝ :=
  t - (Int.floor (t / (2 * Real.pi)) : ℝ) * (2 * Real.pi)

noncomputable def phaseTrace (x0 : ι → ℝ) (u : ℕ → ι → ℝ) : ℕ → ι → ℝ
  | 0 => x0
  | n + 1 => fun i => wrapPhase (phaseTrace x0 u n i + u n i)

noncomputable def inputPhasor (d : ℕ) (x0 : ι → ℝ) (u : ℕ → ι → ℝ)
    (omega : ι → ℝ) (tau : ℝ) (n : ℕ) (i j : ι) : ℂ :=
  phasor (phaseTrace x0 u n i -
    Researcher040282.Delay.historyTrace d (phaseTrace x0 u) n ⟨0, Nat.zero_lt_succ d⟩ j -
    ((omega i + omega j) / 2) * tau)

noncomputable def delayedIncrement (d : ℕ) (u : ℕ → ι → ℝ) (n : ℕ) (j : ι) : ℝ :=
  if d ≤ n then u (n - d) j else 0

/-- Floor-based wrapping changes an angle only by an integer period. -/
theorem phasor_wrap (t : ℝ) : phasor (wrapPhase t) = phasor t := by
  unfold phasor wrapPhase
  push_cast
  rw [sub_mul, Complex.exp_sub, mul_assoc]
  simp only [Complex.exp_int_mul_two_pi_mul_I, div_one]

/-- Startup has zero delayed increment; the first live delayed increment is n=D. -/
theorem delayed_input_step (d : ℕ) (x0 : ι → ℝ) (u : ℕ → ι → ℝ)
    (omega : ι → ℝ) (tau : ℝ) (n : ℕ) (i j : ι) :
    inputPhasor d x0 u omega tau (n + 1) i j =
      inputPhasor d x0 u omega tau n i j *
        phasor (u n i - delayedIncrement d u n j) := by
  have hadd (a b : ℝ) : phasor (a + b) = phasor a * phasor b := by
    simp only [phasor, Complex.ofReal_add, add_mul, Complex.exp_add]
  have hsub (a b : ℝ) : phasor (a - b) = phasor a / phasor b := by
    simp only [phasor, Complex.ofReal_sub, sub_mul, Complex.exp_sub]
  have hstep (k : ℕ) (r : ι) :
      phasor (phaseTrace x0 u (k + 1) r) = phasor (phaseTrace x0 u k r) * phasor (u k r) := by
    change phasor (wrapPhase (phaseTrace x0 u k r + u k r)) = _
    rw [phasor_wrap, hadd]
  have hz : phasor 0 = 1 := by simp [phasor]
  simp only [inputPhasor, Researcher040282.Delay.historyTrace_oldest, hsub]
  by_cases hd : d ≤ n
  · have hs : n + 1 - d = (n - d) + 1 := by omega
    rw [hs, hstep, hstep]
    simp only [delayedIncrement, if_pos hd]
    field_simp [phasor, Complex.exp_ne_zero]
  · have h0 : n - d = 0 := by omega
    have h1 : n + 1 - d = 0 := by omega
    simp only [h0, h1, hstep, delayedIncrement, if_neg hd, hz, div_one]
    field_simp [phasor, Complex.exp_ne_zero]

/-- Circular chord bound, NOT a Euclidean difference of stored representatives. -/
theorem delayed_input_chord_bound (d : ℕ) (x0 : ι → ℝ) (u : ℕ → ι → ℝ)
    (omega : ι → ℝ) (tau : ℝ) (n : ℕ) (i j : ι) :
    ‖inputPhasor d x0 u omega tau (n + 1) i j - inputPhasor d x0 u omega tau n i j‖ ≤
      |u n i - delayedIncrement d u n j| := by
  rw [delayed_input_step]
  have heq : inputPhasor d x0 u omega tau n i j * phasor (u n i - delayedIncrement d u n j) -
      inputPhasor d x0 u omega tau n i j =
      inputPhasor d x0 u omega tau n i j * (phasor (u n i - delayedIncrement d u n j) - 1) := by ring
  rw [heq, norm_mul]
  have hnorm : ‖inputPhasor d x0 u omega tau n i j‖ = 1 := by
    unfold inputPhasor phasor
    exact Complex.norm_exp_ofReal_mul_I _
  rw [hnorm, one_mul]
  simpa only [phasor, mul_comm, Real.norm_eq_abs] using
    (Real.norm_exp_I_mul_ofReal_sub_one_le (x := u n i - delayedIncrement d u n j))

#print axioms Researcher040282.Phase.phasor_wrap
#print axioms Researcher040282.Phase.delayed_input_step
#print axioms Researcher040282.Phase.delayed_input_chord_bound

end Researcher040282.Phase
```
<!-- END_CRITICAL_FILE: PhaseIncrement.lean -->

### phase_contract.py

<!-- BEGIN_CRITICAL_FILE: phase_contract.py -->
```python
"""Independent immutable011 phase-input design. Pure math/cmath, no NumPy/engine.
The010 scalar step is reused explicitly; phase factors use analytic age indices,
not source outputs. All seven full traces are built before the acquired import.
"""
from dataclasses import dataclass,replace
import cmath
import math
from step_contract import Case,Parameters,Prediction,base_case,drift_case,matrix,reference,shadow_after

ABS_TOL=5e-13
MIN_WITNESS=1e-7
STEPS=8

@dataclass(frozen=True)
class Frame:
    case:Case
    prediction:Prediction
    increment:tuple[float,...]
    input_phasor:tuple[tuple[complex,...],...]
    windings:tuple[int,...]

@dataclass(frozen=True)
class Trace:
    initial:Case
    frames:tuple[Frame,...]
    phase_values:tuple[tuple[float,...],...]


def phasor(value):return cmath.exp(1j*value)


def source_cases():
    base=base_case('active_D2',2,True)
    def constant(case):return replace(case,C=matrix(case.p.N,lambda i,j:0j),history=tuple(case.theta for _ in range(round(case.p.tau/case.p.dt)+1)))
    wrap=base_case('positive_wrap_D1',1,True);wrap=replace(wrap,theta=(math.tau-0.015,1.27,4.13))
    d3=base_case('active_D3',3,True)
    theta4=(0.31,1.27,4.13,2.71)
    n4=Case('coupled_N4_D4',Parameters(4,0.125,0.5,(0.5,1.0,1.5,1.25),eta=3.0),theta4,
            matrix(4,lambda i,j:0.0 if i==j else 0.04*(1+i+j)),matrix(4,lambda i,j:0j),())
    negative=replace(base,name='negative_wrap_D2',p=replace(base.p,omega=(-1.0,0.75,1.5)),theta=(0.01,1.27,4.13))
    multi=replace(base,name='multiwrap_D2',p=replace(base.p,omega=(161.0,-143.0,27.0)))
    drift=drift_case(3);drift=replace(drift,name='free_drift_N1_D3',theta=(6.1,))
    return tuple(constant(case) for case in (wrap,base,d3,n4,negative,multi,drift))


def increment(case,prediction,which='new_gated'):
    p=case.p;n=p.N
    B=case.B if which=='old_B' else prediction.B_unprojected if which=='unprojected_B' else prediction.B
    return tuple(p.dt*(p.omega[i]+sum(B[i][j]*math.sin(case.history[0][j]-case.theta[i]) for j in range(n))) for i in range(n))


def input_phasor(case,delayed,omit_offset=False):
    return matrix(case.p.N,lambda i,j:phasor(case.theta[i]-delayed[j]-(0.0 if omit_offset else (case.p.omega[i]+case.p.omega[j])/2.0*case.p.tau)))


def prepare_traces():
    traces=[]
    for initial in source_cases():
        d=round(initial.p.tau/initial.p.dt);shadow=initial;frames=[];values=[initial.theta]
        for n in range(STEPS):
            if shadow.history[0]!=values[max(0,n-d)]:raise RuntimeError('Independent shadow/history-age design disagreement')
            prediction=reference(shadow);u=increment(shadow,prediction)
            z=input_phasor(shadow,values[max(0,n-d)])
            windings=tuple(math.floor((shadow.theta[i]+u[i])/math.tau) for i in range(shadow.p.N))
            frames.append(Frame(shadow,prediction,u,z,windings))
            values.append(prediction.theta);shadow=shadow_after(shadow,prediction)
        traces.append(Trace(initial,tuple(frames),tuple(values)))
    return tuple(traces)


def drift(trace,n,i,j,wrong=None):
    d=round(trace.initial.p.tau/trace.initial.p.dt);current=trace.frames[n].increment[i]
    delayed=0.0 if n<d else trace.frames[n-d].increment[j]
    if wrong=='omit_startup_guard':delayed=trace.frames[max(0,n-d)].increment[j]
    elif wrong=='one_step_early':delayed=0.0 if n+1<d else trace.frames[n+1-d].increment[j]
    elif wrong=='current_delayed_increment':delayed=0.0 if n<d else trace.frames[n].increment[j]
    elif wrong=='one_extra_delay':delayed=0.0 if n<d+1 else trace.frames[n-d-1].increment[j]
    elif wrong=='old_B_increment':current=increment(trace.frames[n].case,trace.frames[n].prediction,'old_B')[i]
    elif wrong=='unprojected_B_increment':current=increment(trace.frames[n].case,trace.frames[n].prediction,'unprojected_B')[i]
    return delayed-current if wrong=='reverse_difference' else current-delayed


def capacity_bound(trace,n,i,j):
    p=trace.initial.p;c=(p.a-p.delta)/p.q;d=round(p.tau/p.dt)
    return p.dt*(abs(p.omega[i])+c) if n<d else p.dt*(abs(p.omega[i]-p.omega[j])+2*c)


def component_difference(a,b):
    if isinstance(a,tuple):return max((component_difference(x,y) for x,y in zip(a,b)),default=0.0)
    if isinstance(a,complex) or isinstance(b,complex):return max(abs(a.real-b.real),abs(a.imag-b.imag))
    return abs(a-b)


def control_witnesses(traces):
    by={trace.initial.name:trace for trace in traces};base=by['active_D2'];multi=by['multiwrap_D2'];out=[]
    specs=(('omit_startup_guard',0),('one_step_early',1),('current_delayed_increment',3),('one_extra_delay',2),
           ('reverse_difference',3),('old_B_increment',0),('unprojected_B_increment',0))
    for name,n in specs:
        expected=phasor(drift(base,n,0,1));wrong=phasor(drift(base,n,0,1,name))
        out.append((name,'factor',expected,wrong,{'case':base.initial.name,'n':n,'i':0,'j':1}))
    case=base.frames[0].case
    out.append(('omit_mean_offset','absolute_input',base.frames[0].input_phasor[0][1],input_phasor(case,case.history[0],True)[0][1],
                {'case':base.initial.name,'n':0,'i':0,'j':1}))
    out.append(('next_step_C_input','absolute_input',base.frames[0].input_phasor[0][1],base.frames[1].input_phasor[0][1],
                {'case':base.initial.name,'n':0,'i':0,'j':1}))
    raw=multi.phase_values[1][0]-multi.phase_values[0][0]
    out.append(('raw_angle_increment','real_increment',multi.frames[0].increment[0],raw,{'case':multi.initial.name,'n':0,'i':0}))
    return tuple(out)


def design_record(traces):
    controls=[{'model':name,'field':field,'component_difference':component_difference(expected,wrong),'witness':witness}
              for name,field,expected,wrong,witness in control_witnesses(traces)]
    coordinates=sum(trace.initial.p.N**2 for trace in traces)
    return {'phase':'Independent scalar design before acquired-engine import/advance; not source observations',
            'cases':[{'name':t.initial.name,'N':t.initial.p.N,'D':round(t.initial.p.tau/t.initial.p.dt),
                      'first_increment':t.frames[0].increment,'first_windings':t.frames[0].windings,
                      'first_pre_violation':t.frames[0].prediction.pre_violation,
                      'first_projection_active':t.frames[0].prediction.projection_active} for t in traces],
            'actual_advances_planned':len(traces)*STEPS,'input_complex_coordinates_planned':coordinates*STEPS,
            'adjacent_complex_coordinates_planned':coordinates*(STEPS-1),
            'startup_adjacent_coordinates_planned':sum(round(t.initial.p.tau/t.initial.p.dt)*t.initial.p.N**2 for t in traces),
            'ten_fixed_control_witnesses':controls,'absolute_tolerance':ABS_TOL,'relative_tolerance':0.0,
            'positive_equivalences_not_misclassified_as_mutants':['stored-angle-difference versus unwrapped increment inside phasor',
                                                               'constant mean-frequency offset cancels in adjacent input ratio']}
```
<!-- END_CRITICAL_FILE: phase_contract.py -->

### prepare_mathlib.py

<!-- BEGIN_CRITICAL_FILE: prepare_mathlib.py -->
```python
"""Targeted prescribed Mathlib cache into OWN disposable012 target only.
Public setup dependencies are executed by Lake, not counted as science/controls.
No global toolchain setting, credentials, remote write or outgoing Git metadata.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time

HERE=Path(__file__).resolve().parent
DEFAULT=Path.home()/'.cache/researcher040282-cycle012'


def require(condition,message):
    if not condition:raise RuntimeError(message)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--cache',type=Path,default=DEFAULT)
    parser.add_argument('--receipt',type=Path,required=True);args=parser.parse_args();started=time.perf_counter()
    cache=args.cache.resolve();manifest=json.loads((HERE/'source_modules.json').read_text());record=manifest['mathlib']
    install=cache/manifest['lean_toolchain']['asset_name'].removesuffix('.tar.zst');lake=install/'bin/lake';lean=install/'bin/lean'
    require(lean.is_file() and lake.is_file(),'Complete prescribed runtime required before Mathlib: setup blocker')
    env=dict(os.environ,PATH=str(install/'bin')+os.pathsep+os.environ.get('PATH',''),GIT_TERMINAL_PROMPT='0',
             XDG_CACHE_HOME=str(cache/'xdg'),MATHLIB_CACHE_DIR=str(cache/'mathlib-downloads'),LAKE_HOME=str(cache/'lake-home'),
             ELAN_HOME=str(cache/'elan-home'),PYTHONDONTWRITEBYTECODE='1')
    mathlib=cache/'mathlib4'
    if not (mathlib/'.git').is_dir():
        subprocess.run(['git','clone','--quiet','--depth','1','--branch',record['inputRev'],record['url']+'.git',str(mathlib)],
                       env=env,check=True,timeout=180)
    revision=subprocess.check_output(['git','-C',str(mathlib),'rev-parse','HEAD'],env=env,text=True,timeout=30).strip()
    require(revision==record['revision'],'Wrong prescribed Mathlib source: setup blocker')
    source_prescription=(mathlib/'lean-toolchain').read_text().strip()
    require(source_prescription==manifest['lean_toolchain']['toolchain'],'Incompatible dependency compiler prescription')
    require(all((mathlib/path).is_file() for path in record['targets']),'Missing targeted dependency source')
    print('Acquiring targeted public cache closure only:',len(record['targets']),'roots',flush=True)
    subprocess.run([str(lake),'exe','cache','get']+record['targets'],cwd=mathlib,env=env,check=True,timeout=660)
    size=sum(path.stat().st_size for path in cache.rglob('*') if path.is_file() and not path.is_symlink())
    require(size<=12*1024**3,'Owned setup exceeded preregistered12GiB resource bound')
    version=subprocess.check_output([str(lean),'--version'],env=env,text=True,timeout=20).strip()
    receipt={'mathlib_revision':revision,'compiler_version':version,'compiler_prescription':source_prescription,
             'mathlib_directory':str(mathlib),'compiler_binary':str(lean),'cache':str(cache),'targeted_roots':record['targets'],
             'targeted_not_omnibus_Mathlib':True,'cache_helper_returncode':0,'owned_regular_file_logical_bytes':size,
             'all_setup_cache_download_targets_inside_own_prefix':True,'global_toolchain_changed':False,
             'raw_git_objects_not_copied_to_packet':True,'remove_only_own_cache_after_full_extracted_reproduction':True,
             'elapsed_seconds':time.perf_counter()-started}
    args.receipt.parent.mkdir(parents=True,exist_ok=True);args.receipt.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':main()
```
<!-- END_CRITICAL_FILE: prepare_mathlib.py -->

### step_contract.py

<!-- BEGIN_CRITICAL_FILE: step_contract.py -->
```python
"""Independent scalar specification of the synthetic non-shuffled primitive.
No NumPy, acquired module, RNG, engine helper or engine-derived expected output.
Immutable tuple inputs. Fixed finite absolute comparison tolerance elsewhere.
"""
from dataclasses import dataclass, replace
import cmath
import math

ABS_TOL=5e-13
MIN_CONTROL_WITNESS=1e-7
PROJECTION_ACTIVE_TOL=1e-14  # reviewed source diagnostic threshold, NOT ABS_TOL

@dataclass(frozen=True)
class Parameters:
    N:int
    dt:float
    tau:float
    omega:tuple[float,...]
    a:float=1.0
    q:float=1.5
    delta:float=0.1
    eta:float=0.2
    mu:float=0.05
    gamma:float=0.2
    T_window:float=0.5
    B_c:float=0.0
    B_init_scale:float=0.0
    scale_epsilon:float=1e-12

@dataclass(frozen=True)
class Case:
    name:str
    p:Parameters
    theta:tuple[float,...]
    B:tuple[tuple[float,...],...]
    C:tuple[tuple[complex,...],...]
    history:tuple[tuple[float,...],...]

@dataclass(frozen=True)
class Prediction:
    theta:tuple[float,...]
    B:tuple[tuple[float,...],...]
    C:tuple[tuple[complex,...],...]
    history:tuple[tuple[float,...],...]
    R:tuple[tuple[float,...],...]
    B_unprojected:tuple[tuple[float,...],...]
    minimum_raw_offdiagonal_proposal:float
    pre_violation:bool
    projection_active:bool
    g_min_pre:float
    g_min:float


def matrix(n,function):return tuple(tuple(function(i,j) for j in range(n)) for i in range(n))


def reference(case,wrong=None):
    """One scalar step; wrong chooses ONE explicitly named incorrect model.
    Wrong models are oracle falsifiers, not modifications of frozen source.
    """
    p=case.p;n=p.N
    delayed=case.history[-1] if wrong=='newest' else case.history[1] if wrong=='second_oldest' else case.history[0]
    alpha=math.exp(-p.dt/p.T_window)
    def new_c(i,j):
        offset=p.omega[i] if wrong=='individual_frequency' else (p.omega[i]+p.omega[j])/2.0
        z=cmath.exp(1j*(case.theta[i]-delayed[j]-offset*p.tau))
        return alpha*case.C[i][j]+(1.0-alpha)*z
    C=matrix(n,new_c)
    if wrong=='old_C_for_R':R=matrix(n,lambda i,j:0.0 if i==j else (abs(case.C[i][j])+abs(case.C[j][i]))/2.0)
    elif wrong=='symmetrize_C_first':R=matrix(n,lambda i,j:0.0 if i==j else abs((C[i][j]+C[j][i])/2.0))
    else:R=matrix(n,lambda i,j:0.0 if i==j else (abs(C[i][j])+abs(C[j][i]))/2.0)
    raw=matrix(n,lambda i,j:case.B[i][j]+p.dt*((p.eta+p.mu)*R[i][j]-p.mu-p.gamma*case.B[i][j]))
    clipped=matrix(n,lambda i,j:max(raw[i][j],0.0))
    before=matrix(n,lambda i,j:0.0 if i==j else (clipped[i][j]+clipped[j][i])/2.0)
    rows=tuple(sum(row) for row in before)
    pre=min(p.a-p.q*row for row in rows);violation=pre<p.delta
    if violation or wrong=='unconditional_gate':
        capacity=(p.a-p.delta)/p.q
        scales=tuple(min(1.0,capacity/(row+p.scale_epsilon)) for row in rows)
        B=matrix(n,lambda i,j:0.0 if i==j else before[i][j]*min(scales[i],scales[j]))
    else:B=before
    correction=math.sqrt(sum((B[i][j]-before[i][j])**2 for i in range(n) for j in range(n)))
    phase_B=case.B if wrong=='old_B_for_phase' else before if wrong=='unprojected_B_for_phase' else B
    def next_theta(i):
        coupling=sum(phase_B[i][j]*math.sin((case.theta[i]-delayed[j]) if wrong=='reversed_sine' else (delayed[j]-case.theta[i])) for j in range(n))
        return (case.theta[i]+p.dt*(p.omega[i]+coupling))%math.tau
    theta=tuple(next_theta(i) for i in range(n))
    fresh=case.theta if wrong=='append_old_theta' else theta
    history=case.history[1:]+(fresh,)
    offdiag=[raw[i][j] for i in range(n) for j in range(n) if i!=j]
    return Prediction(theta,B,C,history,R,before,min(offdiag,default=0.0),violation,
                      correction>PROJECTION_ACTIVE_TOL,pre,min(p.a-p.q*sum(row) for row in B))


def base_case(name='inactive_D1',d=1,active=False):
    theta=(0.31,1.27,4.13);oldest=(5.91,0.81,2.24)
    history=tuple(tuple(oldest[j]+(theta[j]-oldest[j])*k/d for j in range(3)) for k in range(d))+(theta,)
    return Case(name,Parameters(3,0.125,d*0.125,(0.5,1.0,1.5),eta=3.0 if active else 0.2),theta,
                ((0.0,0.08,0.23),(0.08,0.0,0.32),(0.23,0.32,0.0)),
                ((0.17+0.23j,-0.42+0.18j,0.11-0.56j),
                 (0.37-0.25j,-0.2+0.09j,0.61+0.13j),
                 (-0.08+0.33j,-0.48-0.27j,0.26-0.19j)),history)


def drift_case(d=1):
    return Case('dyadic_D'+str(d),Parameters(1,0.125,d*0.125,(1.0,),eta=0.0,mu=0.0,gamma=0.0),
                (0.25,),((0.0,),),((0j,),),tuple((0.25,) for _ in range(d+1)))


def cases():
    inactive=base_case();active=base_case('active_D2',2,True);active3=base_case('active_D3',3,True)
    zero=base_case('zero_C_new_drive_D2',2);zero=replace(zero,C=matrix(3,lambda i,j:0j))
    wrap=base_case('phase_wrap_D1');wrap=replace(wrap,theta=(math.tau-0.015,0.011,6.27),
                                               history=(wrap.history[0],(math.tau-0.015,0.011,6.27)))
    boundary=Case('exact_capacity_N2',Parameters(2,0.125,0.125,(0.5,1.0),q=1.0,delta=0.5,
                                               eta=0.0,mu=0.0,gamma=0.0,scale_epsilon=0.01),
                  (0.31,1.27),((0.0,0.5),(0.5,0.0)),((0j,0j),(0j,0j)),((5.91,0.81),(0.31,1.27)))
    clipped=base_case('negative_proposal_clipped',2);clipped=replace(clipped,p=replace(clipped.p,eta=0.0,mu=8.0,gamma=8.0),C=matrix(3,lambda i,j:0j))
    theta4=(0.31,1.27,4.13,2.71);old4=(5.91,0.81,2.24,4.61)
    directed=Case('directed_C_N4_D4',Parameters(4,0.125,0.5,(0.5,1.0,1.5,1.25),eta=3.0),theta4,
                  matrix(4,lambda i,j:0.0 if i==j else 0.04*(1+i+j)),
                  matrix(4,lambda i,j:complex(0.11*(i+1)-0.07*j,0.09*(j+1)-0.13*i)),
                  tuple(tuple(old4[j]+(theta4[j]-old4[j])*k/4 for j in range(4)) for k in range(4))+(theta4,))
    return (inactive,active,active3,zero,wrap,boundary,clipped,directed,drift_case())


def shadow_after(case,prediction):
    return replace(case,theta=prediction.theta,B=prediction.B,C=prediction.C,history=prediction.history)


def control_cases():
    active=base_case('fixed_active_control',2,True)
    return tuple((name,active if name!='unconditional_gate' else cases()[5],field) for name,field in (
        ('newest','C'),('second_oldest','C'),('individual_frequency','C'),('old_C_for_R','R_physical'),
        ('symmetrize_C_first','R_physical'),('old_B_for_phase','theta'),('unprojected_B_for_phase','theta'),
        ('reversed_sine','theta'),('append_old_theta','history'),('alias_new_theta','storage_ownership'),
        ('unconditional_gate','B')))
```
<!-- END_CRITICAL_FILE: step_contract.py -->

### check_engine.py

<!-- BEGIN_CRITICAL_FILE: check_engine.py -->
```python
"""Nine012 source/causal tracking methods +ten explicit independent wrong models.
All expectations BEFORE acquired import. No source mutation, pre-call compute_R,
production/baseline/S01/CLI/certificate or setup error credited as a falsifier.
"""
import argparse
from dataclasses import asdict,dataclass
import io
import json
import math
from pathlib import Path
import unittest
import numpy as np
from load_reviewed import load,verify
from tracking_contract import (ABS_TOL,MIN_WITNESS,STEPS,alpha,budget,complex_unroll,controls,delta,design_record,
                               error as expected_error,phasor,prepare_traces,signed_drift)

class ContractMismatch(AssertionError):
    def __init__(self,field,expected,observed,delta=None):
        self.field=field;self.delta=delta
        super().__init__(f'{field}: expected {expected}; observed {observed}; component difference {delta}')

def require(condition,message):
    if not condition:raise RuntimeError(message)

def save(path,value):path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')

def error(want,got,field):
    want=np.asarray(want);got=np.asarray(got)
    if want.shape!=got.shape:raise ContractMismatch(field+'.shape',list(want.shape),list(got.shape))
    if not np.all(np.isfinite(want)) or not np.all(np.isfinite(got)):raise ContractMismatch(field+'.finite',True,False)
    if np.iscomplexobj(want) or np.iscomplexobj(got):
        return max(float(np.max(np.abs(got.real-want.real),initial=0.0)),float(np.max(np.abs(got.imag-want.imag),initial=0.0)))
    return float(np.max(np.abs(got-want),initial=0.0))

def close(want,got,field):
    delta=error(want,got,field)
    if delta>ABS_TOL:raise ContractMismatch(field,'absolute error <= '+str(ABS_TOL),delta,delta)
    return delta

def ownership(state):
    for i,h in enumerate(state.history):
        if np.shares_memory(h,state.theta) or any(np.shares_memory(h,other) for other in state.history[:i]):
            raise ContractMismatch('history_ownership','independent history/current vectors','shared allocation')

def real_tuple(value):return tuple(float(x) for x in value)
def complex_matrix(value):return tuple(tuple(complex(x) for x in row) for row in value)
def encoded(value):return [[[float(x.real),float(x.imag)] for x in row] for row in value]


@dataclass(frozen=True)
class Observation:
    C_before:tuple
    C_after:tuple
    z:tuple
    decoded_innovation:tuple|None
    R:tuple
    theta_before:tuple
    theta_after:tuple
    row_sums:tuple
    errors:tuple
    pre_violation:bool
    projection_active:bool


def snapshot_input(theta,oldest,omega,tau):
    return tuple(tuple(phasor(theta[i]-oldest[j]-(omega[i]+omega[j])/2*tau) for j in range(len(theta))) for i in range(len(theta)))


def packed(z):return [float(z.real),float(z.imag)]


class Context:
    def __init__(self,module,traces,cells):
        self.module=module;self.traces=traces;self.cells=cells;self.lookup={(c.case,c.n,c.i,c.j):c for c in cells}
        self.observed={};self.records=[];self.tracking=[];self.calls=0;self.stats={};self.recurrence_errors={}
    def run_traces(self):
        saved=repr((self.traces,self.cells))
        for trace in self.traces:
            first=trace.initial;cfg=self.module.ModelConfig(**asdict(first.p));cfg.validate();a=alpha(trace)
            close(a,cfg.alpha,'configuration_alpha');require(cfg.delay_steps>=1 and cfg.delay_steps*cfg.dt==cfg.tau,'Invalid planned exact delay')
            state=self.module.DynamicState(np.array(first.theta),np.array(first.B),np.array(first.C),[np.array(h) for h in first.history])
            rng=np.random.default_rng(1040282);rng_before=json.dumps(rng.bit_generator.state,sort_keys=True);items=[]
            for n,frame in enumerate(trace.frames):
                state.validate(cfg);ownership(state)
                for field,want,got in (('pre_C',frame.case.C,state.coherence_acc),('pre_theta',frame.case.theta,state.theta),('pre_B',frame.case.B,state.B),('pre_history',frame.case.history,state.history)):
                    close(want,got,field)
                old_c=state.coherence_acc.copy();theta=real_tuple(state.theta);oldest=real_tuple(state.history[0])
                z=snapshot_input(theta,oldest,cfg.omega,cfg.tau);errors={'input_argument_formula':close(frame.input_phasor,z,'input_argument_formula')}
                # Only target call. ALL expected traces/cells already computed before module import.
                self.calls+=1;physical,driver,info=self.module.advance_state(state,cfg,rng,shuffle_driver=False)
                state.validate(cfg);ownership(state);prediction=frame.prediction
                for field,want,got in (('C',prediction.C,state.coherence_acc),('B',prediction.B,state.B),('theta',prediction.theta,state.theta),('history',prediction.history,state.history),('R_physical',prediction.R,physical),('R_driver',prediction.R,driver)):
                    errors[field]=close(want,got,field)
                for flag in ('pre_violation','projection_active'):
                    if type(info[flag]) is not bool or info[flag]!=getattr(prediction,flag):raise ContractMismatch(flag,getattr(prediction,flag),info[flag])
                for field in ('g_min_pre','g_min'):errors[field]=close(getattr(prediction,field),info[field],field)
                if np.any(state.theta<0) or np.any(state.theta>=math.tau):raise ContractMismatch('phase_range','[0,2pi)',state.theta.tolist())
                if not np.array_equal(state.B,state.B.T) or np.any(state.B<0) or np.any(np.diag(state.B)!=0):raise ContractMismatch('B_structure','nonnegative/symmetric/diag0','bad')
                if rng_before!=json.dumps(rng.bit_generator.state,sort_keys=True):raise ContractMismatch('RNG','unchanged','changed')
                decoded=None
                if a<1:
                    require(1-a>=.05,'Unplanned ill-conditioned innovation extraction')
                    decoded=complex_matrix((state.coherence_acc-cfg.alpha*old_c)/(1-cfg.alpha))
                    errors['decoded_C_innovation']=close(frame.input_phasor,decoded,'decoded_C_innovation')
                else:
                    require(a==1 and cfg.alpha==1,'Unplanned alpha endpoint')
                    if not np.array_equal(old_c,state.coherence_acc):raise ContractMismatch('alpha1_no_update','C unchanged','changed')
                item=Observation(complex_matrix(old_c),complex_matrix(state.coherence_acc),z,decoded,tuple(real_tuple(r) for r in physical),theta,real_tuple(state.theta),real_tuple(np.sum(state.B,axis=1)),tuple(sorted(errors.items())),info['pre_violation'],info['projection_active'])
                items.append(item);self.records.append({'case':first.name,'n':n,'N':first.p.N,'D':cfg.delay_steps,'alpha':a,'C_before':encoded(item.C_before),'C_after':encoded(item.C_after),
                    'input_from_observed_arguments':encoded(z),'decoded_C_innovation':None if decoded is None else encoded(decoded),
                    'input_channel':'formula_only_beta0_unidentifiable_in_C' if decoded is None else 'formula_and_actual_C_innovation',
                    'R_physical':item.R,'theta_before':theta,'theta_after':item.theta_after,'row_sums':item.row_sums,'component_errors':dict(item.errors),
                    'pre_violation':item.pre_violation,'projection_active':item.projection_active,'all_expectations_before_import':True,'rng_unchanged':True,'independent_history_storage':True})
            self.observed[first.name]=tuple(items)
        require(saved==repr((self.traces,self.cells)),'Immutable independent traces/budgets changed')
    def all_cells(self):
        for trace in self.traces:
            obs=self.observed[trace.initial.name]
            for n in range(STEPS):
                for i in range(trace.initial.p.N):
                    for j in range(trace.initial.p.N):yield trace,obs,n,i,j,self.lookup[(trace.initial.name,n,i,j)]


def current_error(item,i,j):return item.C_before[i][j]-item.z[i][j]


def suite(context):
    class TrackingContract(unittest.TestCase):
        def test_01_six_full_independent_traces(self):context.run_traces()
        def test_02_exact_causal_tracking_error(self):
            count=0;maximum=0.0
            for trace,obs,n,i,j,cell in context.all_cells():
                if n<STEPS-1:
                    got=current_error(obs[n+1],i,j);rhs=alpha(trace)*current_error(obs[n],i,j)-(obs[n+1].z[i][j]-obs[n].z[i][j])
                    residual=close(rhs,got,'causal_relational_error');close(cell.next_error_rhs,got,'independent_causal_prediction')
                    context.recurrence_errors[(trace.initial.name,n+1,i,j)]=residual;count+=1;maximum=max(maximum,residual)
            require(count==333,'Recurrence inventory mismatch');context.stats.update(adjacent_causal_coordinates=count,maximum_causal_component_residual=maximum)
        def test_03_complex_unroll_and_two_budgets(self):
            count=0;maximum=0.0;small_nonzero=0;max_excess=0.0
            for trace,obs,n,i,j,cell in context.all_cells():
                got=current_error(obs[n],i,j);close(cell.tracking_error,got,'independent_current_error')
                residual=close(cell.complex_unroll,got,'independent_complex_unroll');maximum=max(maximum,residual)
                norm=abs(got)
                if norm>cell.input_budget+ABS_TOL:raise ContractMismatch('input_variation_budget',cell.input_budget,norm,norm-cell.input_budget)
                if cell.input_budget>cell.phase_budget+ABS_TOL:raise ContractMismatch('phase_composition_budget',cell.phase_budget,cell.input_budget,cell.input_budget-cell.phase_budget)
                max_excess=max(max_excess,norm-cell.input_budget);small_nonzero+=norm>MIN_WITNESS and cell.phase_budget<2
                context.tracking.append({'case':trace.initial.name,'n':n,'i':i,'j':j,'alpha':alpha(trace),'observed_current_error':packed(got),
                    'expected_current_error':packed(cell.tracking_error),'expected_complex_unroll':packed(cell.complex_unroll),'unroll_component_error':residual,
                    'observed_error_norm':norm,'input_variation_budget':cell.input_budget,'phase_increment_budget':cell.phase_budget,
                    'reported_R_bound':cell.reported_R_bound,'consumed_input_error':packed(obs[n].C_after[i][j]-obs[n].z[i][j]),
                    'expected_consumed_error':packed(cell.consumed_error),'causal_residual_from_previous':context.recurrence_errors.get((trace.initial.name,n,i,j))})
                count+=1
            require(count==370 and small_nonzero>0,'Budget checks vacuous/incomplete');context.stats.update(tracking_coordinates=count,maximum_unroll_component_residual=maximum,
                nonzero_tracking_bounds_below_two=small_nonzero,maximum_one_sided_input_budget_excess=max_excess)
        def test_04_consumed_input_is_not_next_input(self):
            maximum=0.0;count=0
            for trace,obs,n,i,j,cell in context.all_cells():
                got=obs[n].C_after[i][j]-obs[n].z[i][j];rhs=alpha(trace)*current_error(obs[n],i,j)
                maximum=max(maximum,close(rhs,got,'consumed_current_error'));close(cell.consumed_error,got,'independent_consumed_error');count+=1
            require(count==370,'Consumed-error count differs');context.stats.update(consumed_input_coordinates=count,maximum_consumed_component_residual=maximum)
        def test_05_startup_and_first_live_phase_budget(self):
            startup=live=first=0
            for trace,obs,n,i,j,cell in context.all_cells():
                if n==STEPS-1:continue
                factor=obs[n+1].z[i][j]/obs[n].z[i][j];close(cell.phase_factor,factor,'phase_increment_factor')
                d=round(trace.initial.p.tau/trace.initial.p.dt)
                if n<d:startup+=1
                else:live+=1
                first+=n==d
            require((startup,live,first)==(115,218,37),'Startup/live inventory differs');context.stats.update(startup_adjacent_coordinates=startup,live_adjacent_coordinates=live,first_live_coordinates=first)
        def test_06_constant_input_tail_and_alpha1(self):
            stable=[];endpoint=None
            for trace in context.traces:
                if trace.initial.p.N!=1:continue
                d=round(trace.initial.p.tau/trace.initial.p.dt);obs=context.observed[trace.initial.name];a=alpha(trace)
                for n in range(d,STEPS):
                    close(1+0j,obs[n].z[0][0],'N1_stationary_tail_input')
                    close(a**(n-d)*current_error(obs[d],0,0),current_error(obs[n],0,0),'stationary_tail_error_decay')
                if a<1:stable.append({'case':trace.initial.name,'first_tail_error':abs(current_error(obs[d],0,0)),'last_tail_error':abs(current_error(obs[-1],0,0))})
                else:
                    require(a==1 and all(item.decoded_innovation is None for item in obs),'Alpha1 channel/dynamics mismatch')
                    require(all(item.C_before==item.C_after==obs[0].C_before for item in obs),'Alpha1 C not EXACTLY unchanged')
                    endpoint=abs(current_error(obs[-1],0,0));require(endpoint>.8,'Alpha1 nondecay witness vacuous')
            require(len(stable)==2 and all(x['last_tail_error']<x['first_tail_error']-MIN_WITNESS for x in stable) and endpoint is not None,'Tail checks incomplete/vacuous')
            context.stats.update(alpha_less_one_stationary_tails=stable,rounded_alpha1_tail_error=endpoint,alpha1_C_exactly_constant=True,alpha1_not_strict_contraction=True)
        def test_07_reported_R_is_after_C_and_enveloped(self):
            off=diag=tight=0;maximum_excess=0.0
            for trace,obs,n,i,j,cell in context.all_cells():
                got=obs[n].R[i][j]
                if i==j:
                    if got!=0.0:raise ContractMismatch('reported_R_diagonal',0,got)
                    diag+=1
                else:
                    residual=abs(got-1);maximum_excess=max(maximum_excess,residual-cell.reported_R_bound)
                    if residual>cell.reported_R_bound+ABS_TOL:raise ContractMismatch('reported_R_envelope',cell.reported_R_bound,residual,residual-cell.reported_R_bound)
                    off+=1;tight+=residual>MIN_WITNESS and cell.reported_R_bound<1 and abs(residual-cell.reported_R_bound)<=ABS_TOL
            require((off,diag)==(240,130) and tight>0,'R bound incomplete/vacuous');context.stats.update(reported_R_offdiag_bound_coordinates=off,reported_R_exact_diag_coordinates=diag,
                tight_nonzero_reported_R_bounds_below_one=tight,maximum_one_sided_R_bound_excess=maximum_excess)
        def test_08_nonzero_C_gate_windings_and_decoder_channels(self):
            decoded=endpoint=positive=negative=multiple=active=0
            for trace in context.traces:
                active+=trace.frames[0].prediction.projection_active
                for n,item in enumerate(context.observed[trace.initial.name]):
                    amount=trace.initial.p.N**2
                    if item.decoded_innovation is None:endpoint+=amount
                    else:decoded+=amount
                    for k in trace.frames[n].windings:positive+=k>0;negative+=k<0;multiple+=abs(k)>1
            require((decoded,endpoint)==(360,10) and active==3 and positive>0 and negative>0 and multiple>0,'Nonvacuity/channel inventory mismatch')
            context.stats.update(decoded_C_innovation_coordinates=decoded,alpha1_formula_only_input_coordinates=endpoint,first_active_gate_cases=active,
                positive_windings=positive,negative_windings=negative,multiple_turn_windings=multiple,beta0_divisions=0,source_alpha0_configs=0)
        def test_09_counts_preservation_and_no_extra_source_calls(self):
            require(context.calls==len(context.records)==60 and len(context.tracking)==370 and len(context.cells)==370,'Actual source/expected table counts differ')
            require(all(x['all_expectations_before_import'] and x['rng_unchanged'] and x['independent_history_storage'] for x in context.records),'Preservation proof incomplete')
    return unittest.defaultTestLoader.loadTestsFromTestCase(TrackingContract)


def wrong_models(traces):
    out=[]
    for row in controls(traces):
        try:
            if row['kind']=='upper_bound':
                violation=row['expected']-row['wrong']
                if violation>ABS_TOL:raise ContractMismatch(row['field'],'upper bound '+str(row['wrong']),row['expected'],violation)
            else:close(row['expected'],row['wrong'],row['field'])
        except ContractMismatch as problem:
            require(problem.field==row['field'] and problem.delta is not None and problem.delta>MIN_WITNESS,'Wrong mechanism/tolerance fuzz: '+row['model'])
            out.append({'model':row['model'],'kind':row['kind'],'detected':True,'intended_field':row['field'],'detected_field':problem.field,'numeric_witness':problem.delta,
                        'case':row['case'],'n':row['n'],'i':row['i'],'j':row['j'],'setup_errors_credited':0})
        else:raise RuntimeError('Undetected incorrect model: '+row['model'])
    require(len(out)==10,'Wrong-model count differs');return out


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--source',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--kind',choices=('common','wrong_models'),required=True);args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    try:
        from tracking_contract import prepare_expectations
        traces=prepare_traces();cells=prepare_expectations(traces);design=design_record(traces);save(args.output/'preexecution_design.json',design)
        require(len(cells)==370 and all(x['intended_witness']>MIN_WITNESS for x in design['ten_wrong_models']),'Preimport expectations/witness invalid')
        manifest=verify(args.source)
        if args.kind=='wrong_models':
            records=wrong_models(traces);save(args.output/'wrong_models.json',records)
            value={'kind':'wrong_models','optimized_python':not __debug__,'detected':len(records),'records':records,'actual_engine_advances':0,'actual_engine_imported':False,
                   'setup_errors_credited':0,'source_files_unchanged':len(manifest['modules']),'metadata_files_unchanged':len(manifest['metadata'])}
        else:
            context=Context(load(args.source),traces,cells);stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite(context));print(stream.getvalue(),end='')
            save(args.output/'advance_observations.json',context.records);save(args.output/'tracking_observations.json',context.tracking)
            value={'kind':'common','optimized_python':not __debug__,'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),
                   'actual_engine_advances':context.calls,'source_initializations':0,'source_cases':len(traces),'precomputed_tracking_cells':len(cells),
                   'maximum_component_error':max((v for r in context.records for v in r['component_errors'].values()),default=0.0),'tracking_stats':context.stats,
                   'absolute_tolerance':ABS_TOL,'relative_tolerance':0.0,'all_expected_traces_and_derived_budgets_before_import':True,
                   'explicit_compute_R_calls_by_harness':0,'source_files_unchanged':len(verify(args.source)['modules']),'metadata_files_unchanged':len(manifest['metadata']),
                   'actual_full_engine_import_no_function_copy_replacement_or_edit':True,'production_simulation_baseline_CLI_or_certificate_called':False,
                   'immutable_inputs_expected_tables_rng_and_history_ownership_verified':True,'alpha1_not_decoded_or_assumed_strictly_less_than_one':True}
            if not result.wasSuccessful():save(args.output/'result.json',value);print(json.dumps(value,indent=2));return 1
        save(args.output/'result.json',value);print(json.dumps(value,indent=2));return 0
    except Exception as problem:
        save(args.output/'failure.json',{'type':type(problem).__name__,'message':str(problem),'semantic_negative_detection_credited':False});raise

if __name__=='__main__':raise SystemExit(main())
```
<!-- END_CRITICAL_FILE: check_engine.py -->

### load_reviewed.py

<!-- BEGIN_CRITICAL_FILE: load_reviewed.py -->
```python
"""Actual intact engine import for synthetic primitive probes, no authority run.
Reviewed-code loader, not a security boundary for arbitrary source submissions.
"""
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent


def verify(source):
    source=Path(source).resolve();manifest=json.loads((HERE/'source_modules.json').read_text())
    for row in manifest['modules']+manifest['metadata']:
        data=(source/row['path']).read_bytes();blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if len(data)!=row['bytes'] or blob!=row['blob']:raise RuntimeError('Reviewed public dependency changed: '+row['path'])
    with (source/'registry/artifacts.csv').open(newline='') as stream:
        rows=[r for r in csv.DictReader(stream) if r['artifact_id']=='ART-0702']
    if len(rows)!=1 or rows[0]['path']!=manifest['engine'] or rows[0]['artifact_status']!='Frozen' or 'authority.lock.json' not in rows[0]['lock_status']:
        raise RuntimeError('Frozen engine policy not acknowledged')
    return manifest


def load(source):
    source=Path(source).resolve();manifest=verify(source);name='r040282_012_unchanged_engine'
    spec=importlib.util.spec_from_file_location(name,source/manifest['engine'])
    if spec is None or spec.loader is None:raise ImportError('Unable to import reviewed engine')
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    try:spec.loader.exec_module(module)
    except Exception:sys.modules.pop(name,None);raise
    if Path(module.__file__).resolve()!=source/manifest['engine']:raise RuntimeError('Wrong engine source')
    verify(source);return module
```
<!-- END_CRITICAL_FILE: load_reviewed.py -->

### check_lean.py

<!-- BEGIN_CRITICAL_FILE: check_lean.py -->
```python
"""Compile012 causal EMA tracker +28explicit reused named dependencies.
Eight strict mathematical/integrity controls; setup/identifier/runtime/timeout
failures NEVER detections. Closed-owned-file policy, NOT general Lean sandbox.
"""
import argparse
import concurrent.futures
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

HERE=Path(__file__).resolve().parent
ALLOWED={'propext','Classical.choice','Quot.sound'}
NAMES={'Researcher040282.Tracking.tracking_error_step','Researcher040282.Tracking.tracking_error_budget','Researcher040282.Tracking.delayed_phase_tracking_budget'}
DEPENDENCY_COUNTS={'HistoryBuffer':3,'PhaseIncrement':3,'CoherenceEMA':22}

def require(condition,message):
    if not condition:raise RuntimeError(message)


def save(path,value):path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')


def source_without_comments(text):
    # Fixed owned files have no nested block comments or command-bearing strings.
    return re.sub(r'--[^\n]*','',re.sub(r'/-.*?-/', '', text,flags=re.S))


def assess(text,output,returncode):
    source=source_without_comments(text);reasons=[]
    declarations=re.findall(r'^\s*(?:theorem|lemma)\s+([\w.]+)',source,re.M)
    requests=re.findall(r'^\s*#print\s+axioms\s+([\w.]+)\s*$',source,re.M)
    footprints={};seen=[]
    for name,body in re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]",output):
        seen.append(name);footprints[name]=sorted(value.strip() for value in body.split(',') if value.strip())
    for name in re.findall(r"'([^']+)' does not depend on any axioms",output):
        seen.append(name);footprints[name]=[]
    if returncode!=0:reasons.append('compiler_nonzero')
    if re.search(r'\bwarning\s*:',output,re.I):reasons.append('compiler_warning')
    if re.search(r'\berror\s*:',output,re.I):reasons.append('compiler_error')
    forbidden=sorted(set(re.findall(r'\b(?:sorry|admit|axiom|native_decide|unsafe|run_tac|elab|macro|initialize)\b',source)))
    if forbidden:reasons.append('forbidden_source:'+','.join(forbidden))
    if any(line.lstrip().startswith('#') and not line.lstrip().startswith('#print axioms ') for line in source.splitlines()):
        reasons.append('unexpected_metacommand')
    declaration_bases=sorted(name.rsplit('.',1)[-1] for name in declarations)
    request_bases=sorted(name.rsplit('.',1)[-1] for name in requests)
    if (not declarations or declaration_bases!=request_bases or len(set(requests))!=len(requests)
        or set(requests)!=set(footprints) or len(seen)!=len(requests)):
        reasons.append('axiom_print_coverage')
    bad={name:sorted(set(values)-ALLOWED) for name,values in footprints.items() if set(values)-ALLOWED}
    if bad:reasons.append('unapproved_axiom_footprint')
    return {'accepted':not reasons,'reasons':reasons,'named_declarations':declarations,
            'requested_axiom_prints':requests,'footprints':footprints,'unapproved_axioms':bad,
            'raw_compiler_returncode':returncode}


def proof_environment(compiler,mathlib):
    manifest=json.loads((HERE/'source_modules.json').read_text());cache=mathlib.parent
    require(compiler.is_file() and (compiler.parent/'lake').is_file() and (mathlib/'lakefile.lean').is_file(),'Compiler/Mathlib setup blocker')
    revision=subprocess.check_output(['git','-C',str(mathlib),'rev-parse','HEAD'],text=True,timeout=30).strip()
    require(revision==manifest['mathlib']['revision'],'Wrong prescribed Mathlib: setup blocker')
    version=subprocess.check_output([str(compiler),'--version'],text=True,timeout=20).strip()
    require('version '+manifest['lean_toolchain']['toolchain'].rsplit(':v',1)[1]+',' in version,'Wrong prescribed compiler')
    env=dict(os.environ,PATH=str(compiler.parent)+os.pathsep+os.environ.get('PATH',''),PYTHONDONTWRITEBYTECODE='1',GIT_TERMINAL_PROMPT='0',
             XDG_CACHE_HOME=str(cache/'xdg'),MATHLIB_CACHE_DIR=str(cache/'mathlib-downloads'),LAKE_HOME=str(cache/'lake-home'),ELAN_HOME=str(cache/'elan-home'))
    env['LEAN_PATH']=subprocess.check_output([str(compiler.parent/'lake'),'env','printenv','LEAN_PATH'],cwd=mathlib,env=env,text=True,timeout=60).strip()
    return env,version,revision


CONTROL_HEADER='''import EMATracking
open Researcher040282.EMA Researcher040282.Tracking
noncomputable def controlZ (n : ℕ) : ℂ := if n = 0 then 1 else -1
noncomputable def controlLateZ (n : ℕ) : ℂ := if n < 2 then 1 else -1
'''


def controls():
    zero=CONTROL_HEADER+'''theorem controlAlphaZero : emaTrajectory 0 1 controlZ 1 - controlZ 1 = 2 := by
  norm_num [emaTrajectory, emaStep, controlZ]
#print axioms controlAlphaZero
'''
    one=CONTROL_HEADER+'''theorem controlAlphaOne : emaTrajectory 1 1 controlZ 3 - controlZ 3 = 2 := by
  norm_num [emaTrajectory, emaStep, controlZ]
#print axioms controlAlphaOne
'''
    beta=CONTROL_HEADER+'''example : emaTrajectory (1/2) 1 controlZ 1 - controlZ 1 = 1 := by
  norm_num [emaTrajectory, emaStep, controlZ, Complex.ext_iff]
'''
    reversed_weights=CONTROL_HEADER+'''example : ‖emaTrajectory (1/2) 1 controlLateZ 2 - controlLateZ 2‖ ≤ (1 : ℝ) := by
  have h : emaTrajectory (1/2) 1 controlLateZ 2 - controlLateZ 2 = (2 : ℂ) := by
    norm_num [emaTrajectory, emaStep, controlLateZ]
  rw [h]
  norm_num [Complex.norm_def, Complex.normSq]
'''
    negative=CONTROL_HEADER+'''example : ‖emaTrajectory (-1) 0 (fun _ => 1) 1 - 1‖ ≤ (-1 : ℝ) := by
  norm_num [emaTrajectory, emaStep]
'''
    sorry=CONTROL_HEADER+'''theorem controlSorry : False := by sorry
#print axioms controlSorry
'''
    axiom=CONTROL_HEADER+'''axiom injectedFalse : False
theorem controlExtraAxiom : False := injectedFalse
#print axioms controlExtraAxiom
'''
    omitted=CONTROL_HEADER+'''theorem controlNoPrint : True := by trivial
'''
    return (('positive_alpha0_nonzero','positive',zero,None),('positive_alpha1_nonzero','positive',one,None),
            ('false_beta_scaled_drift','false_math',beta,None),('false_reverse_weights','false_math',reversed_weights,None),
            ('false_drop_nonnegative_alpha','false_math',negative,None),('compiling_sorry','integrity',sorry,'forbidden_source:sorry'),
            ('compiling_extra_axiom','integrity',axiom,'unapproved_axiom_footprint'),('omitted_axiom_print','integrity',omitted,'axiom_print_coverage'))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--lean',type=Path,required=True);parser.add_argument('--mathlib',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    try:
        compiler=args.lean.resolve();env,version,revision=proof_environment(compiler,args.mathlib.resolve())
        sources=args.output/'compiled_sources';logs=args.output/'compiler_logs';sources.mkdir(exist_ok=True);logs.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='r040282-012-lean-') as temporary:
            work=Path(temporary);env['LEAN_PATH']=str(work)+os.pathsep+env['LEAN_PATH']
            def compile_one(name,text,produce=False):
                filename=name+'.lean';(work/filename).write_text(text);(sources/filename).write_text(text)
                command=[str(compiler),'--root='+str(work)]+(['-o',str(work/(name+'.olean'))] if produce else [])+[filename]
                run=subprocess.run(command,cwd=work,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=240)
                (logs/(name+'.log')).write_text(run.stdout)
                if re.search(r'unknown module|object file .* does not exist|failed to import|cannot open shared object|unknown namespace|unknown identifier|unknown constant|unknown tactic|failed to synthesize|maximum.*(?:recursion|heartbeats)|deterministic timeout|unexpected token|invalid field',run.stdout,re.I):
                    raise RuntimeError('Setup/import/parse/elaboration/runtime blocker, never mathematical detection: '+name)
                return run,assess(text,run.stdout,run.returncode)
            dependencies=[]
            for name,count in DEPENDENCY_COUNTS.items():
                text=(HERE/(name+'.lean')).read_text();_,policy=compile_one(name,text,True)
                expected=set(re.findall(r'^#print axioms ([\w.]+)',text,re.M))
                require(policy['accepted'] and len(policy['named_declarations'])==count and len(expected)==count and set(policy['footprints'])==expected,'Reused dependency rejected: '+name)
                dependencies.append({'module':name,'reused_named_claims_not_new_labels':count,'policy':policy})
            _,main_policy=compile_one('EMATracking',(HERE/'EMATracking.lean').read_text(),True)
            require(main_policy['accepted'] and len(main_policy['named_declarations'])==3 and set(main_policy['footprints'])==NAMES,'New main theorem acceptance failed: '+json.dumps(main_policy))
            def evaluate(item):
                name,kind,text,intended=item;run,policy=compile_one(name,text)
                if kind=='positive':require(run.returncode==0 and policy['accepted'],'Nonzero endpoint positive failed: '+name)
                elif kind=='false_math':require(run.returncode!=0 and not policy['accepted'] and re.search('unsolved goals',run.stdout,re.I) and re.search(r'⊢\s*False',run.stdout),'False math not explicit mathematical False: '+name)
                else:require(run.returncode==0 and not policy['accepted'] and intended in policy['reasons'],'Compiling payload wrong refusal: '+name)
                return {'control':name,'kind':kind,'expected_mechanism':intended,'expected_outcome_observed':True,'policy':policy,'setup_errors_credited':0}
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:records=list(pool.map(evaluate,controls()))
        require(len(records)==8,'Formal inventory incomplete')
        value={'compiler_version':version,'mathlib_revision':revision,'Mathlib_used':True,'dependencies':dependencies,'main':main_policy,
               'new_named_declarations_compiled':3,'reused_named_declarations_recompiled_not_new_labels':28,'formal_controls':8,'positive_controls_accepted':2,
               'false_math_witnesses_rejected_by_compiler':3,'compiling_integrity_payloads_rejected_by_policy':3,'controls':records,
               'setup_errors_credited':0,'all_preregistered_formal_conditions_met':True,
               'scope':'Exact-real causal moving-input EMA error and finite weighted budget, composed with prior phase/history; not floating FFI/full coupled map/locking; alpha>=0finite, no hidden alpha<1 assumption; fixed-owned-source policy not generic sandbox'}
        save(args.output/'result.json',value);print(json.dumps(value,indent=2));return 0
    except Exception as problem:
        save(args.output/'failure.json',{'type':type(problem).__name__,'message':str(problem),'semantic_negative_detection_credited':False});raise

if __name__=='__main__':raise SystemExit(main())
```
<!-- END_CRITICAL_FILE: check_lean.py -->

### prepare_lean.py

<!-- BEGIN_CRITICAL_FILE: prepare_lean.py -->
```python
"""Disposable prescribed complete Lean runtime; Mathlib is a separate targeted setup; no global toolchain change.
Public release verified before selective extraction. Caller may supply installed
compiler instead. Own cache is excluded from snapshots and removed at closeout.
"""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.request

HERE=Path(__file__).resolve().parent
DEFAULT=Path.home()/'.cache/researcher040282-cycle012'


def require(condition,message):
    if not condition:raise RuntimeError(message)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cache',type=Path,default=DEFAULT)
    p.add_argument('--receipt',type=Path,required=True);args=p.parse_args();start=time.perf_counter()
    cache=args.cache.resolve();cache.mkdir(parents=True,exist_ok=True)
    record=json.loads((HERE/'source_modules.json').read_text())['lean_toolchain']
    archive=cache/record['asset_name'];install=cache/record['asset_name'].removesuffix('.tar.zst');binary=install/'bin/lean'
    if not archive.is_file() or archive.stat().st_size!=record['bytes']:
        partial=archive.with_name(archive.name+'.partial')
        print('Downloading disposable prescribed compiler asset:',record['bytes'],'bytes',flush=True)
        request=urllib.request.Request(record['url'],headers={'User-Agent':'Researcher-040282-read-only'})
        with urllib.request.urlopen(request,timeout=60) as response,partial.open('wb') as stream:
            shutil.copyfileobj(response,stream,8*1024*1024)
        partial.replace(archive)
    digest=hashlib.sha256()
    with archive.open('rb') as stream:
        for block in iter(lambda:stream.read(8*1024*1024),b''):digest.update(block)
    require(archive.stat().st_size==record['bytes'] and 'sha256:'+digest.hexdigest()==record['published_digest'],
            'Compiler asset differs from recorded public release')
    decoder=cache/'decoder'
    try:zstandard=importlib.import_module('zstandard');decoder_installed=False
    except ImportError:
        if not (decoder/'zstandard').is_dir():
            subprocess.run([sys.executable,'-m','pip','install','--quiet','--disable-pip-version-check','--no-input',
                            '--no-cache-dir','--no-deps','--target',str(decoder),'zstandard==0.25.0'],check=True,timeout=90)
        sys.path.insert(0,str(decoder));zstandard=importlib.import_module('zstandard');decoder_installed=True
    files=0;bytes_written=0
    print('Extracting complete compiler/runtime for Lake cache helper; Mathlib separate.',flush=True)
    with archive.open('rb') as source,zstandard.ZstdDecompressor().stream_reader(source) as decoded:
        with tarfile.open(fileobj=decoded,mode='r|') as tar:
            for member in tar:
                path=Path(member.name)
                require(not path.is_absolute() and '..' not in path.parts,'Unsafe release member path')
                if path.parts[0]!=install.name:raise RuntimeError('Unexpected compiler release root')
                wanted=True  # complete verified public runtime, own disposable target only
                if wanted:
                    tar.extract(member,cache,filter='data');files+=1;bytes_written+=member.size
    require(binary.is_file(),'Complete compiler extraction incomplete')
    version=subprocess.check_output([str(binary),'--version'],text=True).strip()
    expected=record['toolchain'].rsplit(':v',1)[1]
    require('version '+expected+',' in version,'Wrong prescribed compiler')
    receipt={'toolchain':record['toolchain'],'compiler_version':version,'public_asset_verified':True,
             'download_bytes':record['bytes'],'complete_runtime_extracted_members':files,'complete_runtime_extracted_bytes':bytes_written,
             'compiler_binary':str(binary),'cache':str(cache),'Mathlib_installed':False,'global_toolchain_changed':False,
             'decoder_installed_into_disposable_target':decoder_installed,'decoder_version':zstandard.__version__,
             'cache_excluded_from_packet_and_to_be_removed_after_reproduction':True,
             'elapsed_seconds':time.perf_counter()-start}
    args.receipt.parent.mkdir(parents=True,exist_ok=True);args.receipt.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':main()
```
<!-- END_CRITICAL_FILE: prepare_lean.py -->

### run_checks.py

<!-- BEGIN_CRITICAL_FILE: run_checks.py -->
```python
"""012 causal moving-input EMA contract, actual full engine normal/-O + Lean.
Deliberate external setup first; no production/full baseline/S01/CLI/certificate.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import numpy as np
from load_reviewed import verify

HERE=Path(__file__).resolve().parent

def require(condition,message):
    if not condition:raise RuntimeError(message)

def save(path,value):path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--lean',type=Path,required=True);p.add_argument('--mathlib',type=Path,required=True);args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True);start=time.perf_counter()
    try:
        manifest=verify(args.source)
        require((args.source/'lean/AIEFProofs/lean-toolchain').read_text().strip()==manifest['lean_toolchain']['toolchain'],'Compiler prescription mismatch')
        lake=json.loads((args.source/'lean/AIEFProofs/lake-manifest.json').read_text());ml=next(x for x in lake['packages'] if x['name']=='mathlib')
        require(ml['rev']==manifest['mathlib']['revision'] and args.lean.is_file() and args.mathlib.is_dir(),'Dependency/available setup mismatch')
        env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONOPTIMIZE',None);workers=[]
        for kind in ('common','wrong_models'):
            for optimized in (False,True):
                name=kind+('_optimized' if optimized else '_normal');directory=args.output/name;begin=time.perf_counter()
                command=[sys.executable]+(['-O'] if optimized else [])+['-B',str(HERE/'check_engine.py'),'--kind',kind,'--source',str(args.source.resolve()),'--output',str(directory.resolve())]
                run=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,env=env,timeout=90);(args.output/(name+'.log')).write_text(run.stdout)
                require((directory/'result.json').is_file(),'Worker failed before result, never falsifier: '+name);value=json.loads((directory/'result.json').read_text())
                require(run.returncode==0 and value['optimized_python'] is optimized and value['source_files_unchanged']==1 and value['metadata_files_unchanged']==3,'Worker/source failure: '+name)
                if kind=='common':
                    s=value['tracking_stats']
                    require(value['tests_run']==9 and value['failures']==value['errors']==value['skipped']==0 and value['actual_engine_advances']==60 and
                        value['source_initializations']==0 and value['source_cases']==6 and value['precomputed_tracking_cells']==370 and s['tracking_coordinates']==370 and
                        s['adjacent_causal_coordinates']==333 and s['consumed_input_coordinates']==370 and s['startup_adjacent_coordinates']==115 and s['live_adjacent_coordinates']==218 and
                        s['first_live_coordinates']==37 and s['reported_R_offdiag_bound_coordinates']==240 and s['reported_R_exact_diag_coordinates']==130 and
                        s['decoded_C_innovation_coordinates']==360 and s['alpha1_formula_only_input_coordinates']==10 and s['beta0_divisions']==0 and
                        s['alpha1_C_exactly_constant'] and s['alpha1_not_strict_contraction'] and value['maximum_component_error']<=5e-13 and
                        s['maximum_causal_component_residual']<=5e-13 and s['maximum_unroll_component_residual']<=5e-13 and s['maximum_consumed_component_residual']<=5e-13 and
                        value['absolute_tolerance']==5e-13 and value['relative_tolerance']==0,'Common acceptance/count mismatch: '+name)
                else:require(value['detected']==10 and value['setup_errors_credited']==0 and value['actual_engine_advances']==0 and not value['actual_engine_imported'],'Wrong-model acceptance mismatch')
                value['observed_returncode']=run.returncode;value['elapsed_seconds']=time.perf_counter()-begin;workers.append(value);print(name,'return0 / observed preregistered conditions',flush=True)
        for kind in ('common','wrong_models'):
            pair=[{k:v for k,v in row.items() if k not in ('elapsed_seconds','optimized_python')} for row in workers if row['kind']==kind];require(pair[0]==pair[1],'Normal/-O non-timing mismatch: '+kind)
        save(args.output/'worker_results.json',workers);begin=time.perf_counter()
        run=subprocess.run([sys.executable,'-B',str(HERE/'check_lean.py'),'--lean',str(args.lean.resolve()),'--mathlib',str(args.mathlib.resolve()),'--output',str((args.output/'proof').resolve())],
            stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,env=env,timeout=900);(args.output/'proof.log').write_text(run.stdout)
        require(run.returncode==0 and (args.output/'proof/result.json').is_file(),'Formal check/control blocker, never detection');proof=json.loads((args.output/'proof/result.json').read_text())
        require(proof['all_preregistered_formal_conditions_met'] and proof['new_named_declarations_compiled']==3 and proof['reused_named_declarations_recompiled_not_new_labels']==28 and
                proof['formal_controls']==8 and proof['setup_errors_credited']==0,'Formal inventory incomplete')
        common=next(x for x in workers if x['kind']=='common')
        science={'tested_main':manifest['commit'],'source_contract_methods_each_mode':9,'source_passes_each_mode':9,'source_failures_errors_skips_each_mode':[0,0,0],
            'actual_advances_each_common_mode':60,'initializer_calls_each_common_mode':0,'synthetic_traces_each_mode':6,'current_tracking_coordinates_each_mode':370,
            'consumed_input_coordinates_each_mode':370,'adjacent_causal_coordinates_each_mode':333,'startup_adjacent_coordinates_each_mode':115,'live_adjacent_coordinates_each_mode':218,
            'first_live_coordinates_each_mode':37,'decoded_C_innovation_coordinates_each_mode':360,'alpha1_formula_only_input_coordinates_each_mode':10,
            'reported_R_offdiag_bounds_each_mode':240,'reported_R_exact_diagonal_zeros_each_mode':130,'maximum_observed_component_error':common['maximum_component_error'],
            'tracking_stats':common['tracking_stats'],'absolute_tolerance':5e-13,'relative_tolerance':0.0,'wrong_models_detected_each_mode':10,
            'setup_errors_credited_as_detections':0,'normal_optimized_nontiming_results_match':True,'new_named_Lean_declarations_actually_compiled':3,
            'reused_named_declarations_recompiled_not_new_labels':28,'formal_controls':8,'formal_positive_controls':2,'formal_false_math_controls':3,'formal_compiling_integrity_controls':3,
            'axiom_footprints':proof['main']['footprints'],'targeted_Mathlib_used':True,'reviewed_public_engine_unchanged':1,'reviewed_metadata_unchanged':3,
            'actual_engine_import_no_copied_replaced_or_edited_source_functions':True,'no_source_repair_or_failing_before_claim':True,
            'alpha1_no_division_or_strict_contraction_assumption':True,'all_preregistered_acceptance_conditions_met':True}
        result={'science':science,'environment':{'python':sys.version,'numpy':np.__version__,'compiler':proof['compiler_version'],'mathlib_revision':proof['mathlib_revision']},
            'elapsed_seconds':time.perf_counter()-start,'formal_elapsed_seconds':time.perf_counter()-begin,
            'scope':'Exact-real causal error/finite convolution composed with phase input; finite intact-engine trajectories including rounded alpha1. Not floating FFI/full coupled locking, sharp future bands, production/S01/baseline/CLI/certificate, installed library or independent review.'}
        verify(args.source);save(args.output/'cycle_results.json',result);print(json.dumps(result,indent=2));return 0
    except Exception as problem:
        save(args.output/'failure.json',{'type':type(problem).__name__,'message':str(problem),'semantic_negative_detection_credited':False});raise

if __name__=='__main__':raise SystemExit(main())
```
<!-- END_CRITICAL_FILE: run_checks.py -->

### source_modules.json

<!-- BEGIN_CRITICAL_FILE: source_modules.json -->
```json
{
  "repo": "jacobbrainard84-knightninja/AIEFS",
  "commit": "543e7e1aaa11e4c810783806cb180eee36ec5313",
  "engine": "aief_experiment_engine_v1.py",
  "modules": [
    {
      "path": "aief_experiment_engine_v1.py",
      "blob": "0d116e83a0d2f6b3f6be0e21d8a730c0aec3b689",
      "bytes": 119493
    }
  ],
  "metadata": [
    {
      "path": "registry/artifacts.csv",
      "blob": "28fbbabc57caa095fe76dad223f15f099deabc5e",
      "bytes": 1264455
    },
    {
      "path": "lean/AIEFProofs/lean-toolchain",
      "blob": "a8afa7d1b02d96f0671eba854a8dc4b416beb473",
      "bytes": 25
    },
    {
      "path": "lean/AIEFProofs/lake-manifest.json",
      "blob": "e6c34897cbe880f625aa52983ab1521a61d9bebb",
      "bytes": 3144
    }
  ],
  "lean_toolchain": {
    "toolchain": "leanprover/lean4:v4.33.1",
    "asset_name": "lean-4.33.1-linux.tar.zst",
    "url": "https://github.com/leanprover/lean4/releases/download/v4.33.1/lean-4.33.1-linux.tar.zst",
    "bytes": 570405234,
    "published_digest": "sha256:890afd185370f85666025b883914ab4f4b339136f8c96167b69cfb62aecaf235",
    "scope": "Disposable complete runtime for targeted Mathlib/cache helper012; no global setting; raw Git/irrelevant quarantined input removed after full repetition",
    "metadata_provenance": "Retained official selected release length/digest from completed010/011; actual012archive download reverified, no fresh release-API claim"
  },
  "mathlib": {
    "url": "https://github.com/leanprover-community/mathlib4",
    "revision": "0df444a360eaa60ab8c11dca51a86af692955474",
    "inputRev": "v4.33.1",
    "targets": [
      "Mathlib/Analysis/SpecialFunctions/Trigonometric/Bounds.lean",
      "Mathlib/Algebra/Order/Archimedean/Real/Basic.lean",
      "Mathlib/Tactic/Ring.lean",
      "Mathlib/Tactic/FieldSimp.lean",
      "Mathlib/Tactic/NormNum.lean",
      "Mathlib/Tactic/Linarith.lean",
      "Mathlib/Analysis/SpecificLimits/Normed.lean",
      "Mathlib/Tactic/Positivity.lean"
    ],
    "scope": "Targeted public setup dependency in excluded disposable cache, not vendored scientific output/independent approval"
  }
}
```
<!-- END_CRITICAL_FILE: source_modules.json -->

### fetch_public_dependencies.py

<!-- BEGIN_CRITICAL_FILE: fetch_public_dependencies.py -->
```python
"""Fetch one reviewed public engine and three scope/compiler metadata files.
No acquired-source execution, raw author metadata or compiler download here.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
from urllib.parse import quote
import urllib.request


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=Path('upstream'))
    args=parser.parse_args();manifest=json.loads((Path(__file__).resolve().parent/'source_modules.json').read_text())
    def fetch(record):
        relative=Path(record['path'])
        if relative.is_absolute() or '..' in relative.parts or not (relative.suffix in {'.py','.csv'} or relative.name in {'lean-toolchain','lake-manifest.json'}):
            raise ValueError('Unexpected dependency path')
        target=args.output/relative;was_present=target.exists()
        if was_present:data=target.read_bytes()
        else:
            url='https://raw.githubusercontent.com/'+manifest['repo']+'/'+manifest['commit']+'/'+quote(record['path'],safe='/')
            request=urllib.request.Request(url,headers={'User-Agent':'Researcher-040282-read-only'})
            with urllib.request.urlopen(request,timeout=60) as response:data=response.read()
        blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if blob!=record['blob'] or len(data)!=record['bytes']:raise RuntimeError('Dependency differs: '+record['path'])
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        return {'path':str(relative),'freshly_fetched':not was_present,'verified':True}
    with ThreadPoolExecutor(max_workers=4) as pool:files=list(pool.map(fetch,manifest['modules']+manifest['metadata']))
    print(json.dumps({'tested_main':manifest['commit'],'public_dependencies_fetched_and_verified':len(files),
                      'python_sources':len(manifest['modules']),'metadata_files':len(manifest['metadata']),
                      'files':files,'source_executed_by_fetcher':False,'raw_commit_author_metadata_requested':False},indent=2))


if __name__=='__main__':main()
```
<!-- END_CRITICAL_FILE: fetch_public_dependencies.py -->

### extract_from_report.py

<!-- BEGIN_CRITICAL_FILE: extract_from_report.py -->
```python
"""Extract the sixteen named critical012 files. No execution or fetching."""
import argparse
import json
from pathlib import Path
import re

NAMES={'CoherenceEMA.lean','EMATracking.lean','tracking_contract.py','HistoryBuffer.lean','PhaseIncrement.lean','phase_contract.py','prepare_mathlib.py','step_contract.py','check_engine.py','load_reviewed.py','check_lean.py',
       'prepare_lean.py','run_checks.py','source_modules.json','fetch_public_dependencies.py','extract_from_report.py'}
PATTERN=re.compile(r'<!-- BEGIN_CRITICAL_FILE: ([^>\n]+) -->\n```[^\n]*\n(.*?)\n```\n'
                   r'<!-- END_CRITICAL_FILE: \1 -->',re.S)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('report',type=Path);parser.add_argument('output',type=Path)
    args=parser.parse_args();pairs=PATTERN.findall(args.report.read_text())
    if len(pairs)!=len(NAMES) or {name for name,_ in pairs}!=NAMES:raise RuntimeError('Missing/duplicate/unexpected critical file')
    args.output.mkdir(parents=True,exist_ok=True)
    for name,body in pairs:
        if Path(name).name!=name:raise RuntimeError('Unsafe extraction path')
        target=args.output/name;text=body+'\n'
        if target.exists() and target.read_text()!=text:raise RuntimeError('Existing different file: '+name)
        target.write_text(text)
    print(json.dumps({'critical_files_extracted':len(pairs),'code_executed':False},indent=2))


if __name__=='__main__':main()
```
<!-- END_CRITICAL_FILE: extract_from_report.py -->

