# Researcher040282 ·011 — modulo-safe delayed phasor increments

**One bounded North-Star dynamics-library candidate. Local submitter evidence;
independent seat review, integration and owner upload pending.**

Prepared2026-09-04 Atlantic/Reykjavik (session label). Repository/owner November
labels, including the new Part5 inbox deposit, are retained as source labels,
not substituted for this preparation date. User's “Continue” authorized this011
cycle only. No012 work, remote change, other-bot contact or automatic upload.

## 1 · Result and why it matters

For constant-prehistory delay D, old-buffer read time n and an arbitrary
unwrapped increment u, set

- W(t)=t-floor(t/(2*pi))*2*pi, E(t)=exp(i*t);
- x_(n+1,i)=W(x_(n,i)+u_(n,i));
- H_n[k]=x_(max(0,n+k-D));
- z_(n,ij)=E(x_(n,i)-H_n[0]_j-((omega_i+omega_j)/2)*tau);
- L_(n,j)=0 for n<D, otherwise u_(n-D,j).

The new exact-real Lean bridge proves

**z_(n+1,ij)=z_(n,ij)*E(u_(n,i)-L_(n,j))**

and

**||z_(n+1,ij)-z_(n,ij)|| <= |u_(n,i)-L_(n,j)|.**

A separate named lemma proves E(W(t))=E(t) from actual floor wrapping and integer
periodicity. Three NEW named declarations; unchanged010 history's three claims
recompiled as a dependency, not counted again. All main declarations require only
standard propext/Classical.choice/Quot.sound, with complete axiom-print coverage,
no final main warnings/errors/added axioms/sorry/native_decide. Formal acceptance
also requires eight actually run controls, not merely a successful main build.

This closes a useful prerequisite between reachable delay indexing and
future time-varying-input EMA estimates. It handles wrap crossings and feedback-
generated increments without assuming locking, small drift or convergence. It
is standard mathematics made explicit for the reference library, not a novel
physical discovery or a failing-before engine repair.

### Scope table

| Evidence | What it supports | What it does NOT support |
|---|---|---|
| Three new `LEAN_COMPILED` claims | Universal exact-real floor wrap, startup-aware input identity, signed-increment chord bound | NumPy floating modulo/trig/FFI, C/R/B or full coupled-map equivalence, locking |
| Actual intact engine,9methods/mode | Seven short deterministic coupled/free-drift traces and independent math/cmath correspondence | Production/S01/baseline/CLI/certificate, arbitrary floats or all configurations |
|10wrong models/mode +8formal controls | Intended nonvacuous incorrect-factor/absolute-input/real-increment and compiler/integrity mechanisms | Arbitrary-source sandbox or exhaustive verification/security |
| Full extracted-note repetition |13owned files/four fresh public dependencies, same verified toolchain/Mathlib, matching detailed output | Independent review or second clean compiler/dependency bootstrap |
| Paper capacity specialization | Given nonnegative post-gate row sums<=c, a usable frequency/capacity chord estimate, finitely checked here | A new compiled coupled-capacity or synchronization theorem |

Ledger after actual closure: **122 unique rows / 100 LEAN_COMPILED labels**. Previous118rows/97formal labels
preserved; only three new scoped formal rows +one finite-contract row appended.
Unreviewed labels are not independent approval. No authority/paper/registry promotion.

## 2 · The easily missed boundary is startup, not just modulo

At n=D-1->D the oldest stays x0. It first changes at n=D->D+1, by u0.
Subtracting a delayed-node increment throughout startup silently replaces constant
prehistory with a fictitious drifting negative-time extension. The guard is
n>=D, not n>=D-1 or n>=D+1. Main theorem also covers abstract D0; positive
source dt/tau with exact D*dt=tau force source D>=1.

Concrete actual-source free drift, N1,D3,dt.125,omega1,tau.375:
z0..z7=E(-.375),E(-.25),E(-.125),1,1,1,1,1 up to fixed floating tolerance.
Its stored angle wraps, but startup inputs rotate and then become constant. This
is a boundary witness, not a phase-locking result.

**Two legitimate invariances must not be miscounted as wrong models:**

1 E(stored_new-stored_old)=E(u_n) remains valid modulo integer turns. The WRONG
   statement is real equality stored_new-stored_old=u_n. Observed maximum ordinary
   discrepancy25.132741228718345 (8*pi); valid representative-phasor residual
   9.992007221626409e-16 in the fixed domain.
2 A pair's constant mean-frequency offset cancels between consecutive z's. Omitting
   it can therefore pass ratio-only checks while disagreeing with the source's absolute complex input/C.
   This is absolute complex correspondence, not a claim that every constant phase
   convention changes downstream magnitudes. Absolute-input tests are essential;
   observed omitted-offset component
   difference reaches1.9133793755744422, while legitimate offset-ratio cancellation
   error is5.218048215738236e-15. These positive invariances are explicitly tested.

## 3 · Actual source, immutable oracle and measured finite outcomes

Fresh selected main/library/feedback read preceded preregistration. Entire Frozen
ART-0702 engine imported unchanged. No copied/extracted/replaced source functions,
no edits to source cache/registry/locks. Independent owned scalar math/cmath oracle
reused unchanged from010 and augmented by analytic phase-age/factor calculations.
ALL seven expected full traces built before acquired module import in each worker.
Expected evolution never comes from observed target outputs; no pre-call mutating
compute_R. Manual synthetic initial phases/B/C and CONSTANT initial histories,
not claimed production-random initializer outputs; no initialize_state call.

Source order remains old phase/history[0] ->directed C EMA ->magnitude then
symmetric/zero-diagonal R ->B Euler/clip/symmetry ->conditional capacity gate
->phase using **NEW gated B**, sin(delayed_j-current_i), no mean offset in that
sine ->modulo ->append COPY/pop. A historical u_(n-D,j) uses its own historical
post-gate B, not today's B. Generic theorem does not itself formalize this whole
coupled map; the finite experiment checks source correspondence.

Each normal/-O common suite:

-9common methods,9passes,0failures/errors/skips;
-7traces,56actual advances,0initializer/production calls;
-496complex input coordinates from eight advances per trace;
-434adjacent pair coordinates:157startup/277live,62first-live n=D,215later;
-maximum source/scalar component error4.440892098500626e-16;
-maximum input-ratio component error7.348288644237755e-15;
-fixed absolute5e-13,relative0; no post-result tolerance tuning;
-382nonzero chords with signed-increment bound<2, not merely the vacuous unit-
 circle chord bound2; maximum one-sided numerical chord excess2.509554599787633e-16;
-14positive/9negative winding events,16multiple-turn events (overlapping counts);
-10/10wrong models detected by intended fields, all witnesses>1e-7,0setup errors.

Eight advances read **z0..z7**, not z1..z8: C uses z_n before the phase update.
Thus only seven adjacent ratios n0..6 are observed. Decode innovations from actual
new C and copied actual old C using alpha=exp(-.25), safely away from1. This is
observed data, not the expected input. Also compare full C/B/theta/history and R,
explicit shape/finiteness/real-imag components, exact bools, range/B structure,
independent history allocation and unchanged RNG/immutable inputs.

Positive, negative and large multiwrap phases, D1..4, N1/N3/N4, active gates and
nonuniform time-varying coupled forcing are included. The wrong-current-delayed-
increment witness differs0.008387031264128972; old/unprojected-B witnesses differ
0.0052739455320261405/0.0031603045096356003. Source passes, not a red-before repair.
These remain finite cases, not a universal guarantee for arbitrary valid floats.

### Observed full runner record

```json
{
  "science": {
    "tested_main": "eb3933c196ee19e80e1621ae80d89ca72e6d9485",
    "source_contract_methods_each_mode": 9,
    "source_passes_each_mode": 9,
    "source_failures_errors_skips_each_mode": [
      0,
      0,
      0
    ],
    "actual_advances_each_common_mode": 56,
    "initializer_calls_each_common_mode": 0,
    "synthetic_traces_each_mode": 7,
    "complex_input_coordinates_each_mode": 496,
    "adjacent_complex_coordinates_each_mode": 434,
    "startup_coordinates_each_mode": 157,
    "live_coordinates_each_mode": 277,
    "first_live_coordinates_each_mode": 62,
    "later_live_coordinates_each_mode": 215,
    "maximum_observed_component_error": 4.440892098500626e-16,
    "maximum_ratio_component_error": 7.348288644237755e-15,
    "age_and_chord_stats": {
      "startup_coordinates": 157,
      "first_live_coordinates": 62,
      "first_live_versus_extra_delay_difference": 1.963225072909311,
      "later_live_coordinates": 215,
      "nonzero_chords_with_bound_below_two": 382,
      "maximum_one_sided_chord_excess": 2.509554599787633e-16,
      "omitted_offset_absolute_difference": 1.9133793755744422,
      "offset_cancellation_ratio_error": 5.218048215738236e-15,
      "constant_offset_ratio_invariance_is_valid_not_a_wrong_model": true
    },
    "winding_stats": {
      "positive_windings": 14,
      "negative_windings": 9,
      "multiple_turn_windings": 16,
      "maximum_raw_representative_increment_discrepancy": 25.132741228718345,
      "maximum_valid_representative_phasor_error": 9.992007221626409e-16,
      "representative_difference_phasor_is_valid_not_a_wrong_model": true
    },
    "absolute_tolerance": 5e-13,
    "relative_tolerance": 0.0,
    "wrong_models_detected_each_mode": 10,
    "setup_errors_credited_as_detections": 0,
    "normal_optimized_nontiming_results_match": true,
    "new_named_Lean_declarations_actually_compiled": 3,
    "reused_history_declarations_recompiled_not_new_labels": 3,
    "formal_controls": 8,
    "formal_positive_controls": 2,
    "formal_false_math_controls": 3,
    "formal_compiling_integrity_controls": 3,
    "axiom_footprints": {
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
    "targeted_Mathlib_used": true,
    "reviewed_public_engine_unchanged": 1,
    "reviewed_metadata_unchanged": 3,
    "actual_engine_import_no_copied_replaced_or_edited_source_functions": true,
    "no_source_repair_or_failing_before_claim": true,
    "all_preregistered_acceptance_conditions_met": true
  },
  "environment": {
    "python": "3.13.16 (main, Oct  6 2026, 04:38:44) [GCC 14.2.0]",
    "numpy": "2.3.5",
    "compiler": "Lean (version 4.33.1, x86_64-unknown-linux-gnu, commit 819816b2e0a3bf405af45ae5c7af2491d8f5bee6, Release)",
    "mathlib_revision": "0df444a360eaa60ab8c11dca51a86af692955474"
  },
  "elapsed_seconds": 448.87374336899984,
  "formal_elapsed_seconds": 446.17163870700006,
  "scope": "Exact-real modulo-safe startup-aware delayed input/chord theorem plus finite intact-engine correspondence. Not a Lean proof of Python/float FFI, full coupled map/locking, production baseline, certificate, integration or independent approval."
}
```


### Same nine common methods — actual normal-mode log

```text
test_01_seven_complete_traces (__main__.suite.<locals>.PhaseContract.test_01_seven_complete_traces) ... ok
test_02_startup_has_zero_delayed_increment (__main__.suite.<locals>.PhaseContract.test_02_startup_has_zero_delayed_increment) ... ok
test_03_first_live_read_is_n_equals_D (__main__.suite.<locals>.PhaseContract.test_03_first_live_read_is_n_equals_D) ... ok
test_04_later_live_uses_aged_increment (__main__.suite.<locals>.PhaseContract.test_04_later_live_uses_aged_increment) ... ok
test_05_windings_and_valid_representative_phasor (__main__.suite.<locals>.PhaseContract.test_05_windings_and_valid_representative_phasor) ... ok
test_06_chord_and_capacity_specialization (__main__.suite.<locals>.PhaseContract.test_06_chord_and_capacity_specialization) ... ok
test_07_absolute_offset_and_valid_ratio_cancellation (__main__.suite.<locals>.PhaseContract.test_07_absolute_offset_and_valid_ratio_cancellation) ... ok
test_08_new_gated_B_storage_and_rng (__main__.suite.<locals>.PhaseContract.test_08_new_gated_B_storage_and_rng) ... ok
test_09_C_input_is_pre_phase_and_exact_inventory (__main__.suite.<locals>.PhaseContract.test_09_C_input_is_pre_phase_and_exact_inventory) ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.202s

OK
{
  "kind": "common",
  "optimized_python": false,
  "tests_run": 9,
  "failures": 0,
  "errors": 0,
  "skipped": 0,
  "actual_engine_advances": 56,
  "source_initializations": 0,
  "source_cases": 7,
  "input_complex_coordinates": 496,
  "adjacent_complex_coordinates": 434,
  "maximum_component_error": 4.440892098500626e-16,
  "maximum_ratio_component_error": 7.348288644237755e-15,
  "age_and_chord_stats": {
    "startup_coordinates": 157,
    "first_live_coordinates": 62,
    "first_live_versus_extra_delay_difference": 1.963225072909311,
    "later_live_coordinates": 215,
    "nonzero_chords_with_bound_below_two": 382,
    "maximum_one_sided_chord_excess": 2.509554599787633e-16,
    "omitted_offset_absolute_difference": 1.9133793755744422,
    "offset_cancellation_ratio_error": 5.218048215738236e-15,
    "constant_offset_ratio_invariance_is_valid_not_a_wrong_model": true
  },
  "winding_stats": {
    "positive_windings": 14,
    "negative_windings": 9,
    "multiple_turn_windings": 16,
    "maximum_raw_representative_increment_discrepancy": 25.132741228718345,
    "maximum_valid_representative_phasor_error": 9.992007221626409e-16,
    "representative_difference_phasor_is_valid_not_a_wrong_model": true
  },
  "absolute_tolerance": 5e-13,
  "relative_tolerance": 0.0,
  "source_files_unchanged": 1,
  "metadata_files_unchanged": 3,
  "independent_expected_trace_built_before_import": true,
  "explicit_compute_R_calls_by_harness": 0,
  "actual_full_engine_import_no_function_copy_replacement_or_edit": true,
  "production_simulation_baseline_CLI_or_certificate_called": false,
  "immutable_cases_rng_and_history_ownership_verified": true
}
```


### Ten wrong models — intended semantic detections, not source modifications

```json
[
  {
    "model": "omit_startup_guard",
    "detected": true,
    "intended_field": "factor",
    "detected_field": "factor",
    "component_difference": 0.12068496986146218,
    "witness": {
      "case": "active_D2",
      "n": 0,
      "i": 0,
      "j": 1
    },
    "setup_errors_credited": 0
  },
  {
    "model": "one_step_early",
    "detected": true,
    "intended_field": "factor",
    "detected_field": "factor",
    "component_difference": 0.12068393293079901,
    "witness": {
      "case": "active_D2",
      "n": 1,
      "i": 0,
      "j": 1
    },
    "setup_errors_credited": 0
  },
  {
    "model": "current_delayed_increment",
    "detected": true,
    "intended_field": "factor",
    "detected_field": "factor",
    "component_difference": 0.008387031264128972,
    "witness": {
      "case": "active_D2",
      "n": 3,
      "i": 0,
      "j": 1
    },
    "setup_errors_credited": 0
  },
  {
    "model": "one_extra_delay",
    "detected": true,
    "intended_field": "factor",
    "detected_field": "factor",
    "component_difference": 0.12068099581739043,
    "witness": {
      "case": "active_D2",
      "n": 2,
      "i": 0,
      "j": 1
    },
    "setup_errors_credited": 0
  },
  {
    "model": "reverse_difference",
    "detected": true,
    "intended_field": "factor",
    "detected_field": "factor",
    "component_difference": 0.09598421576808373,
    "witness": {
      "case": "active_D2",
      "n": 3,
      "i": 0,
      "j": 1
    },
    "setup_errors_credited": 0
  },
  {
    "model": "old_B_increment",
    "detected": true,
    "intended_field": "factor",
    "detected_field": "factor",
    "component_difference": 0.0052739455320261405,
    "witness": {
      "case": "active_D2",
      "n": 0,
      "i": 0,
      "j": 1
    },
    "setup_errors_credited": 0
  },
  {
    "model": "unprojected_B_increment",
    "detected": true,
    "intended_field": "factor",
    "detected_field": "factor",
    "component_difference": 0.0031603045096356003,
    "witness": {
      "case": "active_D2",
      "n": 0,
      "i": 0,
      "j": 1
    },
    "setup_errors_credited": 0
  },
  {
    "model": "omit_mean_offset",
    "detected": true,
    "intended_field": "absolute_input",
    "detected_field": "absolute_input",
    "component_difference": 0.16275191423722463,
    "witness": {
      "case": "active_D2",
      "n": 0,
      "i": 0,
      "j": 1
    },
    "setup_errors_credited": 0
  },
  {
    "model": "next_step_C_input",
    "detected": true,
    "intended_field": "absolute_input",
    "detected_field": "absolute_input",
    "component_difference": 0.0521000678316027,
    "witness": {
      "case": "active_D2",
      "n": 0,
      "i": 0,
      "j": 1
    },
    "setup_errors_credited": 0
  },
  {
    "model": "raw_angle_increment",
    "detected": true,
    "intended_field": "real_increment",
    "detected_field": "real_increment",
    "component_difference": 18.84955592153876,
    "witness": {
      "case": "multiwrap_D2",
      "n": 0,
      "i": 0
    },
    "setup_errors_credited": 0
  }
]
```


### Design receipt produced before target import/advance

```json
{
  "phase": "Independent scalar design before acquired-engine import/advance; not source observations",
  "cases": [
    {
      "name": "positive_wrap_D1",
      "N": 3,
      "D": 1,
      "first_increment": [
        0.05360259904774863,
        0.11802245643122745,
        0.20337494452102392
      ],
      "first_windings": [
        1,
        0,
        0
      ],
      "first_pre_violation": true,
      "first_projection_active": true
    },
    {
      "name": "active_D2",
      "N": 3,
      "D": 2,
      "first_increment": [
        0.0579317666269875,
        0.12075869227755759,
        0.1963095410954549
      ],
      "first_windings": [
        0,
        0,
        0
      ],
      "first_pre_violation": true,
      "first_projection_active": true
    },
    {
      "name": "active_D3",
      "N": 3,
      "D": 3,
      "first_increment": [
        0.0579317666269875,
        0.12075869227755759,
        0.1963095410954549
      ],
      "first_windings": [
        0,
        0,
        0
      ],
      "first_pre_violation": true,
      "first_projection_active": true
    },
    {
      "name": "coupled_N4_D4",
      "N": 4,
      "D": 4,
      "first_increment": [
        0.07904646900936489,
        0.1419095277152389,
        0.165059268771988,
        0.14523473450340818
      ],
      "first_windings": [
        0,
        0,
        0,
        0
      ],
      "first_pre_violation": true,
      "first_projection_active": true
    },
    {
      "name": "negative_wrap_D2",
      "N": 3,
      "D": 2,
      "first_increment": [
        -0.13359217105176302,
        0.08691580063936165,
        0.20292637041240136
      ],
      "first_windings": [
        -1,
        0,
        0
      ],
      "first_pre_violation": true,
      "first_projection_active": true
    },
    {
      "name": "multiwrap_D2",
      "N": 3,
      "D": 2,
      "first_increment": [
        20.120431766626986,
        -17.87924130772244,
        3.383809541095455
      ],
      "first_windings": [
        3,
        -3,
        1
      ],
      "first_pre_violation": true,
      "first_projection_active": true
    },
    {
      "name": "free_drift_N1_D3",
      "N": 1,
      "D": 3,
      "first_increment": [
        0.125
      ],
      "first_windings": [
        0
      ],
      "first_pre_violation": false,
      "first_projection_active": false
    }
  ],
  "actual_advances_planned": 56,
  "input_complex_coordinates_planned": 496,
  "adjacent_complex_coordinates_planned": 434,
  "startup_adjacent_coordinates_planned": 157,
  "ten_fixed_control_witnesses": [
    {
      "model": "omit_startup_guard",
      "field": "factor",
      "component_difference": 0.12068496986146218,
      "witness": {
        "case": "active_D2",
        "n": 0,
        "i": 0,
        "j": 1
      }
    },
    {
      "model": "one_step_early",
      "field": "factor",
      "component_difference": 0.12068393293079901,
      "witness": {
        "case": "active_D2",
        "n": 1,
        "i": 0,
        "j": 1
      }
    },
    {
      "model": "current_delayed_increment",
      "field": "factor",
      "component_difference": 0.008387031264128972,
      "witness": {
        "case": "active_D2",
        "n": 3,
        "i": 0,
        "j": 1
      }
    },
    {
      "model": "one_extra_delay",
      "field": "factor",
      "component_difference": 0.12068099581739043,
      "witness": {
        "case": "active_D2",
        "n": 2,
        "i": 0,
        "j": 1
      }
    },
    {
      "model": "reverse_difference",
      "field": "factor",
      "component_difference": 0.09598421576808373,
      "witness": {
        "case": "active_D2",
        "n": 3,
        "i": 0,
        "j": 1
      }
    },
    {
      "model": "old_B_increment",
      "field": "factor",
      "component_difference": 0.0052739455320261405,
      "witness": {
        "case": "active_D2",
        "n": 0,
        "i": 0,
        "j": 1
      }
    },
    {
      "model": "unprojected_B_increment",
      "field": "factor",
      "component_difference": 0.0031603045096356003,
      "witness": {
        "case": "active_D2",
        "n": 0,
        "i": 0,
        "j": 1
      }
    },
    {
      "model": "omit_mean_offset",
      "field": "absolute_input",
      "component_difference": 0.16275191423722463,
      "witness": {
        "case": "active_D2",
        "n": 0,
        "i": 0,
        "j": 1
      }
    },
    {
      "model": "next_step_C_input",
      "field": "absolute_input",
      "component_difference": 0.0521000678316027,
      "witness": {
        "case": "active_D2",
        "n": 0,
        "i": 0,
        "j": 1
      }
    },
    {
      "model": "raw_angle_increment",
      "field": "real_increment",
      "component_difference": 18.84955592153876,
      "witness": {
        "case": "multiwrap_D2",
        "n": 0,
        "i": 0
      }
    }
  ],
  "absolute_tolerance": 5e-13,
  "relative_tolerance": 0.0,
  "positive_equivalences_not_misclassified_as_mutants": [
    "stored-angle-difference versus unwrapped increment inside phasor",
    "constant mean-frequency offset cancels in adjacent input ratio"
  ]
}
```


## 4 · Proof and formal falsifiers

New module defines floor wrap, phaseTrace, source-shaped inputPhasor and guarded
delayedIncrement. No conclusion disguised as an input hypothesis. The arbitrary
increment function can be feedback-generated; this is not a proof that all
coupled dynamics lock. No finite-index assumption is needed for this abstract
identity. Reused history's3claims remain historical labels. Three new full names:

-Researcher040282.Phase.phasor_wrap
-Researcher040282.Phase.delayed_input_step
-Researcher040282.Phase.delayed_input_chord_bound

Two nonzero positives: startup z1=I and live z2=-1 for a concrete time-varying
increment trace. Three false math examples: ignore wrap at2*pi, subtract a delayed
increment during startup, use current rather than aged delayed-node increment.
They must reduce to explicit **False**, with nonzero compiler return, not an
import/identifier/runtime/timeout failure. Three compiling integrity payloads:
sorry, an injected axiom and missing axiom-print coverage; require raw0 and the
intended policy refusal. They are not mathematical counterexample detections.

Fixed-owned-source checker, not a secure parser/sandbox for arbitrary Lean source
or plugins. It rejects forbidden markers, main warnings/errors, unapproved axiom
footprints and incomplete named print coverage. Compiler/library/cache trust is
ordinary toolchain trust, not a general security certificate.

### Actual main compiler output

```text
'Researcher040282.Phase.phasor_wrap' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.Phase.delayed_input_step' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.Phase.delayed_input_chord_bound' depends on axioms: [propext, Classical.choice, Quot.sound]
```


### Complete formal result, dependency/main policies and8controls

```json
{
  "compiler_version": "Lean (version 4.33.1, x86_64-unknown-linux-gnu, commit 819816b2e0a3bf405af45ae5c7af2491d8f5bee6, Release)",
  "mathlib_revision": "0df444a360eaa60ab8c11dca51a86af692955474",
  "Mathlib_used": true,
  "dependency": {
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
  },
  "main": {
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
  },
  "new_named_declarations_compiled": 3,
  "reused_named_history_declarations_recompiled_not_new_labels": 3,
  "formal_controls": 8,
  "positive_controls_accepted": 2,
  "false_math_witnesses_rejected_by_compiler": 3,
  "compiling_integrity_payloads_rejected_by_policy": 3,
  "controls": [
    {
      "control": "positive_startup_nonzero",
      "kind": "positive",
      "expected_mechanism": null,
      "expected_outcome_observed": true,
      "policy": {
        "accepted": true,
        "reasons": [],
        "named_declarations": [
          "controlStartup"
        ],
        "requested_axiom_prints": [
          "controlStartup"
        ],
        "footprints": {
          "controlStartup": [
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
      "control": "positive_live_nonzero",
      "kind": "positive",
      "expected_mechanism": null,
      "expected_outcome_observed": true,
      "policy": {
        "accepted": true,
        "reasons": [],
        "named_declarations": [
          "controlLive"
        ],
        "requested_axiom_prints": [
          "controlLive"
        ],
        "footprints": {
          "controlLive": [
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
      "control": "false_no_wrap",
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
      "control": "false_startup_delayed_increment",
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
      "control": "false_current_instead_of_aged",
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
  "scope": "Exact-real floor modulo/complex input identity and signed-increment chord bound, not Python/float FFI, full coupled dynamics or locking; fixed-file policy not general sandbox"
}
```


### Actual three false-math logs

### false_no_wrap

```text
false_no_wrap.lean:6:51: error: unsolved goals
⊢ False
```

### false_startup_delayed_increment

```text
false_startup_delayed_increment.lean:6:168: error: unsolved goals
hs : inputPhasor 1 controlX0 controlU controlOmega 1 1 () () = Complex.I
⊢ False
```

### false_current_instead_of_aged

```text
false_current_instead_of_aged.lean:6:168: error: unsolved goals
hs : inputPhasor 1 controlX0 controlU controlOmega 1 1 () () = Complex.I
hl : inputPhasor 1 controlX0 controlU controlOmega 1 2 () () = -1
⊢ False
```


### Development errors retained, not promoted or credited

-`development/phase_pilot_01/`: first draft lacked explicit phasor-zero
 normalization, used a deprecated import alias, and over-simplified a real cast
 before unit-norm matching. Unsound/sorryAx draft never promoted.
-`development/phase_pilot_02/`: concurrent same-file edit calls overwrote intended
 corrections. Fixed with one checked sequential rewrite, not a mathematical result.
-`development/phase_pilot_03/`: raw0/standard footprints but unused/unreachable ring
 warnings, because field_simp already closed the goals. Removed unused tactics,
 did not disable warning linters to hide them. Not an accepted final build.
-`development/first_full_runner_control_blocker/`: both source suites and both
 wrong-model workers passed and main/dependency compiled clean, but concrete
 positive-control n0 oldest-lemma simplification failed. Reduced actual constant
 history definition in the control; changed no source, theorem statement, case
 or tolerance. This attempt did NOT meet overall acceptance and is not a formal
 falsifier success. Corrected concrete nonzero positives separately verified under
 `development/control_fixture_direct_startup/`, then final full runner repeated.

## 5 · What the capacity corollary adds, and what remains open

For nonnegative post-gate row sum<=c, |kappa_ni|<=c. At dt>=0 the generic bound
specializes to dt*(|omega_i|+c) during startup and
**dt*(|omega_i-omega_j|+2*c)** live. This is a paper derivation +finite check here,
not a fourth new compiled capacity/composition theorem. It is not an assumed
phase-locking bound and may be large. Python validation's gap tolerance is not
identical to exact row feasibility in every possible input; these fixed actual
rows and inequalities are checked with the fixed numerical slack.

004 exact-real EMA definitions have the same mathematical input shape but are
not imported/composed in this module. Reference-library project integration,
interface alignment and new coupled definitions/obligations remain pending. No
proof of a common finite freeze time, complete baseline equivalence, ON/OFF rate
law, convergence or real S01 data. Independent001/Seat002 review required.

## 6 · Reproduce from this note, not a private workspace module

All13critical OWNED files are inline in section9. Extract them with
extract_from_report.py, fetch4public dependencies with fetch_public_dependencies.py
(engine +Frozen registry +compiler prescription +lake manifest), then run:

```text
python -B prepare_lean.py --receipt compiler_setup.json
python -B prepare_mathlib.py --receipt mathlib_setup.json
python -B run_checks.py --source upstream --output checks \
  --lean ~/.cache/researcher040282-cycle011/lean-4.33.1-linux/bin/lean \
  --mathlib ~/.cache/researcher040282-cycle011/mathlib4
```

Python+NumPy required; setup additionally uses Git/network and a decoder isolated
to its own disposable target. Follow the same read-only/source scope. Full Lean
runtime is needed to build the public cache helper, targeted2196-module Mathlib
closure rather than omnibus Mathlib/Tactic. Current source project prescription
used; actual570405234-byte compiler asset reverified against inherited official
release selected length/digest (fresh release API quota unavailable). Complete
runtime18130members/3037354159extracted bytes; Mathlib setup63.66690114100004s,
initial owned cache6021822789logical bytes within12GiB/15minute setup bound. No
old cache restored, global toolchain setting or production helper installation.

**Actually performed extracted-note repetition:**

**Actually executed:** thirteen critical files extracted byte-identically, four public dependencies freshly fetched/verified, same disposable compiler/targeted Mathlib; complete runner repeated. Science/four non-timing workers and all31 detailed proof/source/log records match. Submitter-local reproduction only, not independent-seat review.

```json
{
  "actually_executed": true,
  "runner_returncode": 0,
  "tested_main": "eb3933c196ee19e80e1621ae80d89ca72e6d9485",
  "critical_file_count": 13,
  "critical_files": [
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
  "all_thirtyone_detailed_records_byte_identical": true,
  "detailed_matching_files": [
    "common_normal/advance_observations.json",
    "common_normal/input_ratio_observations.json",
    "common_normal/preexecution_design.json",
    "common_optimized/advance_observations.json",
    "common_optimized/input_ratio_observations.json",
    "common_optimized/preexecution_design.json",
    "proof/compiled_sources/HistoryBuffer.lean",
    "proof/compiled_sources/PhaseIncrement.lean",
    "proof/compiled_sources/compiling_extra_axiom.lean",
    "proof/compiled_sources/compiling_sorry.lean",
    "proof/compiled_sources/false_current_instead_of_aged.lean",
    "proof/compiled_sources/false_no_wrap.lean",
    "proof/compiled_sources/false_startup_delayed_increment.lean",
    "proof/compiled_sources/omitted_axiom_print.lean",
    "proof/compiled_sources/positive_live_nonzero.lean",
    "proof/compiled_sources/positive_startup_nonzero.lean",
    "proof/compiler_logs/HistoryBuffer.log",
    "proof/compiler_logs/PhaseIncrement.log",
    "proof/compiler_logs/compiling_extra_axiom.log",
    "proof/compiler_logs/compiling_sorry.log",
    "proof/compiler_logs/false_current_instead_of_aged.log",
    "proof/compiler_logs/false_no_wrap.log",
    "proof/compiler_logs/false_startup_delayed_increment.log",
    "proof/compiler_logs/omitted_axiom_print.log",
    "proof/compiler_logs/positive_live_nonzero.log",
    "proof/compiler_logs/positive_startup_nonzero.log",
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
    56,
    56
  ],
  "source_initializations_each_common_mode": [
    0,
    0
  ],
  "input_complex_coordinates_each_mode": [
    496,
    496
  ],
  "adjacent_complex_coordinates_each_mode": [
    434,
    434
  ],
  "wrong_models_detected_each_mode": [
    10,
    10
  ],
  "new_named_Lean_declarations_compiled": 3,
  "reused_history_labels_not_added": 3,
  "formal_controls_repeated": 8,
  "original_elapsed_seconds": 448.87374336899984,
  "extracted_elapsed_seconds": 443.7656343220001,
  "command": "python -B standalone/extracted/run_checks.py --source standalone/upstream --output standalone/checks --lean <same verified compiler> --mathlib <same targeted Mathlib>",
  "result": "cycle_011/standalone/checks/cycle_results.json",
  "log": "cycle_011/standalone/reproduction.log",
  "scope": "Submitter-local exact-note full repetition, not independent review, Python/float/full-coupled proof, real study, authority certificate, source repair/integration or upload"
}
```


The repeat uses the SAME original verified compiler/targeted Mathlib, not a second
clean bootstrap. Four-worker non-timing records and31detailed files include
preexecution design, source observations, ratio observations, wrong models, formal
result and10compiled sources/10compiler logs. Timing-bearing common logs need not
byte-match; scientific content must. Local submitter repetition is not external
seat review.

**Own disposable setup cleanup, after actual full repetition:**

```json
{
  "own_cache": "/home/user/.cache/researcher040282-cycle011",
  "measured_before_removal": true,
  "regular_files_removed": 62891,
  "regular_file_logical_bytes_removed": 6022343486,
  "allocated_bytes_summed_over_regular_file_entries": 6141032960,
  "allocated_sum_not_unique_physical_freed_space_claim": true,
  "symlinks_removed": 15,
  "subdirectories_removed": 3119,
  "actually_removed_after_successful_full_reproduction": true,
  "only_cycle011_owned_runtime_archive_decoder_Git_Mathlib_target_removed": true,
  "compiler_global_setting_changed": false,
  "all_unrelated_caches_untouched_claimed": false,
  "old_AIEFS_evidence_deleted": false,
  "legacy_deleted_Lua_restored": false,
  "cache_absent_after_removal": true
}
```


Only own011cache is removed, including Git object metadata not copied to packet.
No assertion that unrelated system/pip caches were audited. Prior AIEFS reports,
archives/evidence and completed010state/ledger preserved; deleted old Lua audit
folder remains absent and is not restored.

## 7 · Source map, intake, public navigation and provenance boundaries

GitHub API403 at initial branch request prevented any API acquisition. Preserve
failure log; read-only Git shallow blobless ref/tree navigation and raw selected
file verification succeeded. No generated-data repository download. Initial Git
quoted Unicode navigation corrected using NUL-delimited exact paths before
preregistration; no new-file finding inferred from quoted rendering. Public HTML
pull-list separately showed1openPR16, unrelated chronicler corrigenda.16Git heads
and selected current Lean scopes/keywords had no matching phase-increment work;
limited public nonduplication evidence, not exhaustive/private-work assurance.

Fresh32main selections,8inbox notes/evidence. New Part5 trust-anchor design/evidence
was read only; its contributed reproducer NOT fetched/executed. It is not an
independent run/approval of009/010 guards or this011 module. No duplicated guard,
uploader/checksum, rate-law or chronicler work. Source identifiers in retained
metadata serve reproduction/scope only, not a canonical-copy/version finding.

```text
# Source correspondence and proof boundary —011

## Read-only source and timing

`source_state/main/aief_experiment_engine_v1.py` is the119493-byte entire reviewed
ART-0702 Frozen module, acquired/verified before preregistration, imported intact
by `load_reviewed.py`. Registry/lock acknowledgement is a scope restriction, not
permission to patch a frozen file. No copied/extracted/replaced source functions.
The independent owned math/cmath scalar specification is explicitly separate.

| Actual source location | Exact role in this cycle |
|---|---|
| ModelConfig properties172–174/validation through237 | positive finite dt/tau, D=round(tau/dt), exact D*dt=tau; hence source D>=1. Frequencies finite, not required positive. All7configs satisfy. |
| DynamicState584–679 | validates finite shape/history length D+1 and B structure/gap; does not certify history reachability or newest==theta. Our synthetic initial histories are separately constant and thereafter independently shadowed. |
| initialize_state686–718 | historical justification of constant-prehistory convention; NOT called in011. We construct7synthetic states; random production initializer not claimed to output them. |
| compute_R721–752 | reads OLD theta/history[0], input exp(i*(theta_i-H0_j-((omega_i+omega_j)/2)*tau)), directed C EMA, THEN magnitude, THEN symmetric R/zero diagonal. Mutates C, so never pre-call for expected values. |
| advance_state755–856 | C/R update first; B Euler/clipping/symmetry; strict g_min_pre<delta conditional capacity gate; phase from NEW gated B using sin(H0_j-theta_i), no mean-frequency offset in that sine; modulo; append theta COPY/pop oldest. |
| phase update830–839/history841–844 | real mathematical shape x_(n+1)=W(x_n+u_n), u_ni=dt*(omega_i+sum_j B_(n+1,ij)*sin(H0_j-x_ni)); source B_(n+1) means post-step/gated B. Delayed historical u_(n-D,j) uses that historical step's own post-gate B, not current B. |

No shuffle; same supplied RNG unchanged. No run_seed/simulate_*/full baseline/
intervention/production/CLI/writer/certificate or authority-validation call.

## Universal exact-real theorem, not floating equivalence

Owned `HistoryBuffer.lean` is unchanged010 reusable dependency; its three Std
claims are RECOMPILED, not three new ledger claims. `HistoryTrace` starts with
constant x0 and shifts/appends x(n+1), so H_n[k]=x(max(0,n+k-D)). New
`PhaseIncrement.lean` defines actual floor wrap W(t)=t-floor(t/(2pi))*2pi and
arbitrary unwrapped increment trace u. New claims:

- `Researcher040282.Phase.phasor_wrap`: E(W(t))=E(t).
- `.delayed_input_step`: z_(n+1,ij)=z_(n,ij)*E(u_ni-L_nj), where
  L_nj=0 for n<D, else u_(n-D,j).
- `.delayed_input_chord_bound`: ||z_(n+1,ij)-z_(n,ij)||<=|u_ni-L_nj|.

z_n uses the D+1 queue's oldest value, exact source-shaped mean-frequency offset
and E(t)=exp(i*t). No assumption of synchronization, small increments, convergence,
locking, freeze time, or the asserted phasor identity. The wrapped recurrence is a
definition. Arbitrary u permits feedback-generated increments, but C/R/B and a full
coupled real map have NOT been formalized/instantiated in Lean here. Module does
not import004's EMA module; its same-shaped input can be aligned in future reviewed
integration, not an already compiled end-to-end composition.

Mathlib's integer-period exponential theorem proves floor-wrap invariance; the
stock unit norm and real-imaginary-exponential Lipschitz/chord inequality give the
norm estimate. Complete three-name axiom-print coverage; allowed standard
propext/Classical.choice/Quot.sound only. No new axiom/sorry/native_decide premise.
Mathematical D0 is covered by the generic theorem but not source-valid with positive
tau. No proof of NumPy remainder/trig rounding or float/Python FFI.

For D>=1 the same delayed phasor increment can be read as E(H_n[1]_j-H_n[0]_j),
including startup repetitions; recovering the UNWRAPPED historical increment as an
ordinary stored-angle difference is invalid. That observation is a paper/value-
index corollary, NOT another new compiled declaration in this cycle.

## Constant startup is not a drifting negative-time extension

At transition n=D-1->D the oldest stays x0. It first changes on n=D->D+1,
with increment u0. Thus guard is n>=D, not n>=D-1 or n>=D+1. During startup
one must NOT subtract dt*omega_j or an initial/current delayed-node increment.

Finite N1,D3,omega1,dt.125,tau.375 example: absolute inputs z0..z7 are
E(-.375),E(-.25),E(-.125),1,1,1,1,1 (up to fixed floating tolerance),
even though stored theta wraps. Startup ratios E(.125), first live and later1.
A fictitious linearly drifting prehistory would erase exactly this startup.

Mean-frequency offset is static for a pair: it cancels between consecutive z's,
but its absolute phasor remains part of the C input/initial condition. Ratio-only
checks cannot catch omitting it. Conversely E(stored_new-stored_old)=E(u_n) is
VALID despite winding; do not count it as a mutant. Only an equality of ordinary
real stored differences to unwrapped u is wrong. No global Euclidean angle bound
is inferred from the circular chord estimate.

## Independent finite evidence design and C read order

All seven full immutable expected traces built by pure math/cmath BEFORE actual
engine import in EACH common worker. Scalar C/B/phase/history evolve only from
prior expected tuples, never observed outputs. Expected u uses predicted NEW gated
B, and expected z uses independent analytic age index max(0,n-D), not target
history contents. First/negative/multiple winding witnesses all fixed in PLAN.

Eight actual advances per trace produce C innovations for z0..z7, not z1..z8.
Observe each innovation from copied ACTUAL old C and actual new C, divided by
1-alpha (alpha=exp(-.25), safely bounded away from1). This is observed data, not an
expected value. Seven adjacent ratios n0..6 need two consecutive actual updates;
no ninth call, no pre-call mutating compute_R. Counts per normal/-O suite:
56advances,496complex inputs,434adjacent pair coordinates=157startup+277live;
62first live at n=D,215strictly later. C/B/theta/history and R outputs also checked.

Fixed abs5e-13,rel0; explicit finite real/imag/shape checks, exact bools, structure,
range, ownership and RNG/input preservation. One-sided chord/capacity slack also
5e-13, not source diagnostic thresholds (ZERO1e-12,PROJECTION_NORM1e-14,GAP1e-9).
This finite domain is not a blanket guarantee for arbitrary validated floats.

## Capacity specialization — paper + finite check, not a new formal gate theorem

If post-gate B>=0 and row sum<=c, |kappa_ni|<=c by |sin|<=1. Then for dt>=0:
startup |v_ij|<=dt*(|omega_i|+c); live |v_ij|<=dt*(|omega_i-omega_j|+2c).
No locking assumption; frequency differences, rather than a cancelled constant
phase offset, remain in the live bound. C=.6 for these configs. Numerically check
post-gate rows and both inequalities on the fixed cases. Do not equate Python's
validation tolerance with exact row feasibility for EVERY possible input. The
formal result is the signed-increment chord bound; a coupled-capacity composition
still requires separate exact-real definitions/obligations.

## Controls, setup and independence

Ten independent incorrect-factor/absolute-input/real-increment models exercise
startup, boundary, aged increment, sign, old/unprojected B, missing absolute offset,
C read time and Euclidean-winding confusion. They do not replace frozen functions.
Two nonzero formal positives; three false math witnesses must reduce to explicit
False; three compiling integrity payloads must be policy-rejected for intended
reason. Imports, setup, unknown identifiers, timeouts and proof-draft errors block
and are never mathematical detections. Fixed owned-source checker is not a generic
untrusted-Lean sandbox/security certification.

Development errors retained: initial proof's phasor-zero/cast-matching/import and
unused-tactic issues, concurrent edit overwrite, then concrete positive control's
n0 history simplification. First full attempt already passed both source modes
and10wrong models/mode and clean main proof, but its positive-control blocker did
NOT satisfy overall acceptance. Correct only own control/harness code, not source,
statements or tolerances. Independent seat approval still absent.
```


### Preregistration, integration restrictions and minimal setup/intake records

### PLAN.md

```text
# 011 preregistration — modulo-safe delayed phasor increment and chord bound

Researcher040282; prepared2026-09-04 Atlantic/Reykjavik (session label). Prior
owner/repository November labels and runtime/compiler clocks remain separate.
This fixes the protocol BEFORE any011 acquired-engine execution or theorem
compilation. So far: public source/feedback/API inspection and mathematical design.

## Fresh scope / intake / no duplicate provenance work

Current main eb3933c196ee19e80e1621ae80d89ca72e6d9485:32 selected texts (claims
inventory deliberately not fetched; includes one matched-phase anchor test read
statically only). Current inbox4fbd00b6e5f975b49bd74885e8c381af9abaf9f7:8 selected
notes/evidence after adding new trust-anchor Part5 review/evidence ONLY. Its
contributed regression reproducer not fetched/executed, its design not approval
of009/010. Targeted R040282/R001/general TRIAGE unchanged. Do not duplicate guard,
rate-law, uploader/checksum or chronicler work. One public open PR16 unrelated;
16Git branch names, no relevant phase/phasor/history/delay/wrap/increment match.
Selected Lean scopes exclude phase/delay; header/keyword inspection no matching
implementation. Limited public navigation, not exhaustive/private-work assurance.

GitHub API403 quota failure preserved under development. Read-only Git refs and
shallow BLOBLESS tree navigation + raw selected-file fetch succeeded; public PR
HTML independently read. NUL-delimited tree parsing corrects initial Unicode path
quoting BEFORE any science; no new-file finding inferred from quoted rendering.
Raw Git objects remain in own excluded disposable cache, not outgoing metadata.

Actual frozen ART-0702 engine imported intact. No edits/replacements/monkeypatches,
source/registry/lock change, full production/baseline study, run_seed/simulate_*,
shuffle/intervention/CLI/writer/certificate, real S01, remote push/PR/contact/upload
or unattended012. Reuse unchanged010 history module/scalar oracle as explicit
owned components, not rerunning historical010 suite or modifying its evidence.

## One mathematical bridge, three intended named claims

Let P=2*pi. Define the IDEAL-REAL wrap W(t)=t-floor(t/P)*P; phasor E(t)=exp(i*t).
For arbitrary real initial vector x0 and arbitrary unwrapped increments
u:Nat->(index->Real), define x(n+1,i)=W(x(n,i)+u(n,i)). Constants omega,tau need
not obey a synchronization assumption. Use010's constant-initialized D+1 history
H(n), so oldest=x(max(0,n-D)). Define actual-shaped coherence input

 z(n,i,j)=E(x(n,i)-H(n)[0](j)-((omega_i+omega_j)/2)*tau).

Define delayed increment L(n,j)=0 when n<D, otherwise u(n-D,j), and
v(n,i,j)=u(n,i)-L(n,j). Prove in the prescribed Lean/Mathlib toolchain:

1 E(W(t))=E(t), with explicit floor-based wrap, not an assumed periodicity axiom.
2 z(n+1,i,j)=z(n,i,j)*E(v(n,i,j)), ALL n, including n=D-1 and first live n=D.
3 ||z(n+1,i,j)-z(n,i,j)|| <= |v(n,i,j)|.

Only three new named main declarations intended. Recompile unchanged010 history
as dependency, not three new labels. Main imports targeted Mathlib trigonometric
Bounds/floor/real and Ring/FieldSimp/NormNum/Linarith, not omnibus Mathlib/Tactic.
Footprints subset{propext,Classical.choice,Quot.sound}; complete named axiom-print
coverage, no main warnings/errors/sorry/admit/native_decide/extra axioms/unsafe.
Preserve development errors, never count as planned falsifiers or compiled claims.

The recurrence is a definition, not the desired phasor identity assumed as a
premise. Arbitrary forcing u can represent dt*(omega_i+coupling_i), where source
coupling uses NEW gated B and old delayed-current sine. This universality permits
feedback instantiation but does NOT formalize C/R/B, Python allocations, actual
floating remainder/trigonometry, whole coupled evolution, locking or convergence.
The formal real wrap is a mathematical model of remainder, not verified NumPy FFI.
Source configurations retain positive dt/tau and exact D*dt=tau, hence D>=1;
abstract D0 is mathematically covered only, not a source-valid configuration.

Paper-only specialization if post-gate nonnegative row sum<=c:
startup bound dt*(|omega_i|+c); live bound dt*(|omega_i-omega_j|+2*c), dt>=0.
This follows |sum B*sin|<=c, not a synchronization assumption. Not a new Lean gate
or capacity/composition theorem; generic signed-increment chord bound is formal.
Ordinary stored-angle differences can jump2*pi: do NOT replace the circular/phasor
bound by a Euclidean representative bound. Conversely exp(i*(stored_new-old)) is
legitimately equal to exp(i*u) modulo winding: test as a POSITIVE, not a mutant.
The mean-frequency offset cancels from the ratio, but matters in absolute input;
ratio-only checks cannot detect omitting that constant.

## Fixed independent synthetic design and numeric tolerances

All source expected traces precomputed using immutable tuple cases, pure math/
cmath scalar oracle reused unchanged from010, BEFORE acquired module import.
For each synthetic case initialize history as D+1 equal value copies of specified
x0 (constructor later makes independent arrays), C0=0, B as below. Seven cases,
EIGHT advances each, INPUT phasors z0..z7, ADJACENT input ratios n0..6 only:

- N3,D1,theta(2*pi-.015,1.27,4.13),omega(.5,1,1.5), active eta3;
- N3,D2,theta(.31,1.27,4.13),sameomega/active;
- N3,D3,same theta/omega/active;
- N4,D4,theta(.31,1.27,4.13,2.71),omega(.5,1,1.5,1.25),active;
- N3,D2,theta(.01,1.27,4.13),omega(-1,.75,1.5),active (negative wrap);
- N3,D2,theta(.31,1.27,4.13),omega(161,-143,27),active (multiple windings);
- N1,D3,theta(6.1),omega1,B0,eta=mu=gamma0 (free drift/startup/positive wrap).

Common dt=.125,tau=D*.125,Twindow=.5,a1,q1.5,delta.1,epsilon1e-12,mu.05,gamma.2;
N3 B edges(.08,.23,.32); N4 Bij=.04*(1+i+j) offdiag, diag0. C0 all complex0,
B_c=B_init_scale0. This is manual synthetic initialization, not a claim random
production initialize_state returns these exact values. No initializer calls.

Expect 56actual advances/common suite,496 full complex input coordinates,
434adjacent pair coordinates:157startup/277live, of which62first-live at n=D.
Actual source updates C with z_n BEFORE updating phase; observing z_(n+1) requires
the NEXT advance. Do not mislabel a post-call C innovation as next-time input.
Observed innovations=(C_after-alpha*C_before)/(1-alpha), with copied ACTUAL old C
as observed data only; independent expected z_n/phase/forcing never from target.
Alpha=exp(-.25), safely away from1; no unstable tiny denominator in this domain.
Never pre-call mutating compute_R. Also compare C/B/theta/history and physical/
driver R to scalar prediction. Reused expected shadow only from oracle outputs.

Fixed absolute5e-13,relative0 for finite real/imag components, unwrapped-winding
residuals, phasor/ratio residuals and one-sided chord/capacity bound slack. Exact
shape/boolean/count/history storage/RNG/input preservation checks; no known NaN-
masking whole-element predicate. No tolerance tuning after source results.
Require each wrong numeric witness>1e-7, not tolerance fuzz. Case-design scalar
numbers may be inspected before engine execution; if a chosen witness is vacuous,
record blocker/plan amendment before execution rather than crediting it.

## Same nine source methods normally and -O

1 all7x8 complete source/scalar traces and input innovations,56actual calls;
2 startup L=0, including frozen N1 input rotating until delay becomes live;
3 first live read n=D, not n=D+1;
4 later live age n-D, not current delayed-node increment;
5 positive/negative/multiple integer windings; raw-difference equality counterexample
  AND representative-phasor equality as legitimate positive;
6 chord bound signed v and paper row-capacity specialization; nonzero chord with
  bound<2 must occur, not merely a vacuous universal2 bound;
7 absolute mean-frequency-offset input, plus legitimate ratio cancellation;
8 NEW gated B forcing nonvacuity against old/unprojected B; independent history
  storage, immutable cases and RNG preservation;
9 C reads z_n before phase/append; exact observation counts, no extra compute_R.

Only method1 makes actual calls; others inspect those fixed immutable observations.
Expect nine methods PASS/0errors/0skips normally/-O. No repair/red-before claim.

## Ten wrong models, each mode; fixed independent witness positions

All are checker falsifiers, never injected into or substituted for engine functions.
Base active-D2 at n/i/j unless stated:
1 omit startup guard: n0,0,1 subtract u0j;
2 one-step-early delayed read: n1,0,1 subtract u0j;
3 current delayed-node increment: n3,0,1 subtract u3j instead of u1j;
4 one-extra delay: n2,0,1 subtract0 instead of u0j;
5 reverse increment difference: n3,0,1;
6 old B current increment: n0,0,1;
7 unprojected B current increment: n0,0,1;
8 omit mean-frequency offset: absolute z0,0,1 (ratio alone would not detect);
9 next-step C input timing: z0 claimed z1,0,1;
10 raw stored-angle difference equals unwrapped increment: multiwrap-D2,n0,node0.

Expected fields: factor for1..7, absolute_input for8..9, real_increment for10.
All numeric component witnesses>1e-7. Import/setup/timeouts must BLOCK rather than
be mistaken for semantic detection. Normal/-O non-timing records match.

## Eight formal controls, compiler resource and closeout

Two nonzero positives (startup D1 and live delayed increment); three false math
witnesses (no-wrap W(2*pi)=2*pi; subtract delayed increment during startup; use
current instead of aged delayed increment); compiling sorry/added-axiom payloads
rejected by policy and compiling omitted-print rejected by coverage. Raw compiler
outcomes and intended mathematical/policy reasons required. False math import/
unknown-identifier/runtime/timeout failures never count as rejection.

Lean/lake/old cache absent,20GB free observed. Select prescribed current project
Lean4.33.1 and Mathlib revision from acquired lake-manifest. Recorded official
Lean570405234B asset info inherited from010, fresh API quota unavailable; verify
actual download against recorded length/published digest. Install ONLY into own
excluded .cache/researcher040282-cycle011; complete runtime needed for Lake/cache
helper, targeted Mathlib cache (no omnibus library). Decoder target own cache,
pip --no-cache-dir; Mathlib/cache helper code is a setup dependency, not science.
No global toolchain setting. Bound setup at12GB owned cache and15minutes; if blocked,
label uncompiled honestly, no labels from sketches. Remove OWN compiler/archive/
decoder/Git navigation/Mathlib caches only AFTER actual full extracted rerun.

After original science, complete inline standalone note with all owned critical
code and essential outputs; extract into clean directory; freshly fetch engine+
registry+toolchain+lake-manifest (4public dependencies) and repeat full runner with
same verified compiler/Mathlib setup. Compare science,4worker non-timing records,
formal records and detailed deterministic outputs, not timing logs. Only afterward
append3scoped LEAN_COMPILED rows+1finite source-contract row, expected122rows/
100formal labels if observed. Preserve all prior118/97 and completed010 state/
ledger/report/archive/science. Unpack/index citations, minimal metadata/privacy/
packet closure before delivery; owner upload only, no independent approval inferred.
```

### proposal/INTEGRATION_NOTE.md

```text
# Proposed one-branch library intake — not installed

Researcher040282 -> Researcher001 / AuditorSeat002. One bounded bridge:
**floor-modulo-safe constant-startup delayed phasor increment and circular chord
bound**. Standard mathematics formalized for a load-bearing dynamics interface,
not a new phase-locking claim or an engine defect/repair.

Candidate files: unchanged reusable `HistoryBuffer.lean`, new `PhaseIncrement.lean`.
Namespaced `Researcher040282.Delay` / `Researcher040282.Phase`; three NEW public
named declarations, dependency's three history declarations not counted again.
Arbitrary index type and feedback-capable increment function; no finite-network
assumption needed for the generic phasor result. Physical source still N>=1,D>=1,
dt/tau>0 and exact delay. Explicit floor real wrap, not NumPy FFI verification.

Suggested reviewed intake location (not created remotely): new unregistered
`lean/.../Researcher040282/PhaseIncrement.lean` with appropriately located history
dependency/import. Owner/R001 must choose project/import layout and run the actual
reference-library build; current compilation is standalone, NOT integration with
existing lake project, source maps, registry, locks,001 library or004 EMA module.
Do not edit pinned ART-0050 or any frozen source/lock/registry. No artifact number
reserved or authority/paper promotion requested on submitter evidence alone.

Actual engine is read-only ART-0702; all mathematical expectations precede import.
Source C reads z_n before phase update; eight calls yield z0..z7 and seven ratios,
not eight ratios or next-time innovation. Finite coupled trajectories exercise NEW
gated B, startup/boundary/live ages, nonzero forcing, positive/negative/multiwrap,
absolute pair-mean offset and valid representative/offset ratio invariances.
Wrong models are independent reference falsifiers, never source replacements.

Prereview checklist:
1 Reproduce all13 inline owned files +4 fresh public dependencies, prescribed
  complete Lean runtime and targeted Mathlib setup; verify main/controls/output
  records. Same original setup reused in local extracted rerun is NOT an independent
  clean install or an external seat's approval.
2 Read exact generic hypotheses/definitions, especially arbitrary UNWRAPPED u and
  constant startup. D0 abstract only. No automatic lift from stored angle changes
  to a real increment bound; inside a phasor that difference IS valid modulo turns.
3 Check source-shaped offset, mean term's absolute role and its ratio cancellation;
  new gated B belongs in u_n. A historical increment has its own historical B, not
  current B. No synchronization/small-drift/convergence conclusion assumed.
4 Review exact scalar-reference and compiler-policy scope; no universal float/
  Python/full-coupled theorem, no arbitrary-Lean sandbox. Setup/import/timeouts and
  retained development errors are NOT falsifier detections.
5 If integrating with004 exact-real EMA input, separately align interfaces and
  compile the composition. Paper capacity specialization remains a source-related
  corollary/finite check here, not a new compiled coupled-capacity theorem.

Possible next bounded boundary, ONLY after another Continue and fresh feedback/
source/nonduplication check: derive time-varying-input EMA tracking error from
proved input increments, without assuming locking/convergence of the whole map.
No012 study, proof, source refresh, compiler setup or preregistration authorized by
this note. Owner handles dated audit-inbox upload; no remote branch/push/PR/contact,
merge or automatic upload made by this agent.
```

### review_decision.json

```json
{
  "role": "Researcher040282 supporting Researcher001/AuditorSeat002",
  "decision": "One unregistered standalone modulo-safe delayed-input/chord library candidate; submitter-local evidence only; independent011 review and integration pending",
  "main_question": "Does the source-shaped phasor input obey the startup-aware increment identity and circular chord bound when stored phases are modulo-wrapped?",
  "novelty_scope": "Standard mathematical bridge formalized and finitely related to actual source; not a new physical discovery or engine bug/repair",
  "intake": "Current selected main/library/source and8inbox notes/evidence read; new Part5 trust-anchor design/evidence not independent009/010 approval; contributed reproducer not fetched/executed",
  "nonduplication": "Limited selected current Lean scopes and keywords,16public Git heads, public HTML1openPR16 unrelated; API403 fallback documented, no exhaustive/private-work assurance",
  "approved_for_local_evidence_only": [
    "Three new named exact-real floor-wrap/input-step/chord declarations, subject to clean actual compiler and standard complete axiom footprints",
    "Unchanged010 history module recompiled as explicit dependency, not new labels",
    "Seven deterministic short synthetic actual-engine traces, normal/-O; independent expectations before import, no extra compute_R",
    "Ten fixed wrong models/mode and eight actual formal controls, intended mechanisms only",
    "Complete inline note extraction, four fresh dependency fetches and actual full runner repetition with same original verified compiler/targeted Mathlib",
    "Own disposable compiler/archive/decoder/Git/Mathlib cache removal after successful full reproduction"
  ],
  "not_approved": [
    "Independent011 seat review, library integration, freeze/registry/lock/authority or paper promotion",
    "A universal NumPy/Python floating remainder/trigonometry/FFI or complete coupled C/R/B/phase dynamics equivalence theorem",
    "Phase synchronization/locking/convergence, strict future ON/OFF bands, finite common freeze time or production correctness",
    "A real S01/cohort/baseline/shuffle/intervention/CLI/writer/certificate/full study or guard installation",
    "Replacing circular chord bounds by Euclidean representative bounds, or treating valid representative/constant-offset ratio invariances as mutants",
    "Ignoring the absolute mean-frequency offset because adjacent ratios cancel it",
    "Counting setup, import, unknown identifier, timeout, draft errors, warning-bearing builds or compiling integrity payloads as mathematical detections",
    "Remote branch, push, PR, contact, upload, merge, frozen edit or unattended012"
  ],
  "next_cycle_candidate_not_executed": "Only after another Continue: fresh feedback/source/library/nonduplication check, then consider smallest time-varying-input EMA tracking-error lemma using this phase-input increment boundary, with no coupled-locking premise. Not selected or preregistered012 work."
}
```

### nonduplication_check.json

```json
{
  "transport": "Read-only Git heads after API403; no author metadata in record",
  "branch_count": 16,
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
      "commit": "4fbd00b6e5f975b49bd74885e8c381af9abaf9f7"
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
      "branch": "main",
      "commit": "eb3933c196ee19e80e1621ae80d89ca72e6d9485"
    },
    {
      "branch": "research/aiefs-northstar-evaluation",
      "commit": "003522e2e9c5b10b94d7f2b0811c7986059a75c0"
    },
    {
      "branch": "research/rate-law-delta-sweep",
      "commit": "62239a2eef5a7c8fdd8d61713d2cb507934e2f1f"
    }
  ],
  "relevant_name_matches": [],
  "scope": "Branch name navigation only; not exhaustive/private-work assurance or branch source execution",
  "PR_open_state_not_obtained_from_git_refs": true,
  "PR_navigation": {
    "url": "https://github.com/jacobbrainard84-knightninja/AIEFS/pulls",
    "transport": "Public HTML rendered by fetch_page after API403",
    "open_PR_count": 1,
    "entries": [
      {
        "number": 16,
        "title": "Corrigenda: fix the chronicler's own two errors at the source (shallow-clone dates, mention-vs-assertion bare refs)",
        "relevant_to_phase_increment": false
      }
    ]
  }
}
```

### review_intake.json

```json
{
  "new_feedback": "Part5 trust-anchor prototype/report/evidence, not independent review of009 or010",
  "contributed_reproducer_acquired_or_executed": false,
  "current010_independent_review_found_in_selected_notes": false,
  "selected_targeted_intake_R001_general_triage_unchanged": true,
  "nonduplication": "Limited selected current Lean/header/keyword +16Git heads +public1openPR; no phase/history theorem found, not exhaustive/private-work assurance",
  "API403": "Preserved development log; Git blobless shallow tree/raw selected-file fallback and public PR HTML succeeded",
  "unrelated_matched_phase_anchor_test": "Static read only, ART0041 flag audit not phase-increment semantics; do not execute/duplicate",
  "not_claimed": "No approval of copied-function downstream results or guard, no canonical/version finding, no remote write/PR/contact/upload"
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
  "compiler_binary": "/home/user/.cache/researcher040282-cycle011/lean-4.33.1-linux/bin/lean",
  "cache": "/home/user/.cache/researcher040282-cycle011",
  "Mathlib_installed": false,
  "global_toolchain_changed": false,
  "decoder_installed_into_disposable_target": true,
  "decoder_version": "0.25.0",
  "cache_excluded_from_packet_and_to_be_removed_after_reproduction": true,
  "elapsed_seconds": 20.254798719000064
}
```

### mathlib_setup.json

```json
{
  "mathlib_revision": "0df444a360eaa60ab8c11dca51a86af692955474",
  "compiler_version": "Lean (version 4.33.1, x86_64-unknown-linux-gnu, commit 819816b2e0a3bf405af45ae5c7af2491d8f5bee6, Release)",
  "compiler_prescription": "leanprover/lean4:v4.33.1",
  "mathlib_directory": "/home/user/.cache/researcher040282-cycle011/mathlib4",
  "compiler_binary": "/home/user/.cache/researcher040282-cycle011/lean-4.33.1-linux/bin/lean",
  "cache": "/home/user/.cache/researcher040282-cycle011",
  "targeted_roots": [
    "Mathlib/Analysis/SpecialFunctions/Trigonometric/Bounds.lean",
    "Mathlib/Data/Real/Archimedean.lean",
    "Mathlib/Tactic/Ring.lean",
    "Mathlib/Tactic/FieldSimp.lean",
    "Mathlib/Tactic/NormNum.lean",
    "Mathlib/Tactic/Linarith.lean"
  ],
  "targeted_not_omnibus_Mathlib": true,
  "cache_helper_returncode": 0,
  "owned_regular_file_logical_bytes": 6021822789,
  "all_setup_cache_download_targets_inside_own_prefix": true,
  "global_toolchain_changed": false,
  "raw_git_objects_not_copied_to_packet": true,
  "remove_only_own_cache_after_full_extracted_reproduction": true,
  "elapsed_seconds": 63.66690114100004
}
```

### historical_restoration.json

```json
{
  "prior_archive": "researcher040282-cycle010-history-phase-contract.zip",
  "nonlive_members_checked": 1243,
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
  "scientific011_inputs_code_results_changed": false,
  "legacy_deleted_Lua_restored": false,
  "user_deleted_legacy_Lua_absent": true
}
```


## 8 · Handoff and next boundary

For Researcher001/AuditorSeat002: review one candidate branch/result set—generic
wrapped delayed-input/chord bridge, with finite actual-source correspondence—not
a full engine repair or physical locking claim. New-file intake only, unregistered
and uninstalled; no frozen ART-0050/engine/registry/lock change. Owner handles
separately dated audit-inbox deposit. No remote upload/push/PR/contact/merge by agent.

Administrative missing-only recovery restored the9175-byte historical006
`.github/workflows/repo-checks.yml` copy exactly from the delivered010ZIP;
1243prior010nonlive members checked, no existing file changed or old science
rerun. Completed010state/ledger snapshots match delivery. No deleted Lua restored.

Evidence index and historical archive log map locate all ledger evidence/logs
UNPACKED; prior archives are not nested in the new ZIP. Branch metadata stores
only minimal identifiers/policy, never copied raw commit contacts/signatures.
Final closure freezes its completed stdout capture before repacking; an initial
active-capture self-inclusion issue is retained under development, not a science
rerun or result change. Final stdout is not an in-packet file being written.
Privacy scan distinguishes historical synthetic fixtures, not exhaustive secret
or security certification. Packet closure receipt verifies member/CRC/content and
historical preservation, not scientific independent review. Optional supporting
archive: `researcher040282-cycle011-modulo-phase-increment.zip`.

**Stop here.** Only on another Continue: fresh feedback/source/library/nonduplication
check, then consider the smallest time-varying-input EMA tracking-error lemma
using the increment bound. No012selection/preregistration/proof/setup/test has
started. Broader coupled dynamics/locking and production studies remain separate.

## 9 · Complete critical owned code

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
"""Targeted prescribed Mathlib cache into OWN disposable011 target only.
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
DEFAULT=Path.home()/'.cache/researcher040282-cycle011'


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
"""Nine bounded full-engine phase methods and ten independent wrong models.
Normal/-O share exact code. All math expectations precede acquired import/calls.
No production simulation, source replacement, pre-call mutating compute_R or S01.
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
from phase_contract import (ABS_TOL,MIN_WITNESS,STEPS,capacity_bound,control_witnesses,
                            design_record,drift,input_phasor,phasor,prepare_traces)

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
    theta_before:tuple
    theta_after:tuple
    innovation:tuple
    component_errors:tuple
    pre_violation:bool
    projection_active:bool
    row_sums:tuple

class Context:
    def __init__(self,module,traces):
        self.module=module;self.traces=traces;self.observed={};self.records=[];self.ratios=[];self.calls=0
        self.stats={};self.winding_stats={};self.maximum_ratio_error=0.0
    def run_traces(self):
        unchanged=repr(self.traces)
        for trace in self.traces:
            first=trace.initial;p=first.p;cfg=self.module.ModelConfig(**asdict(p));cfg.validate()
            require(cfg.delay_steps>=1 and cfg.delay_steps*cfg.dt==cfg.tau,'Invalid source delay domain')
            state=self.module.DynamicState(np.array(first.theta),np.array(first.B),np.array(first.C),[np.array(h) for h in first.history])
            rng=np.random.default_rng(1040282);rng_before=json.dumps(rng.bit_generator.state,sort_keys=True);items=[]
            for n,frame in enumerate(trace.frames):
                state.validate(cfg);ownership(state)
                for field,want,got in (('theta_before',frame.case.theta,state.theta),('B_before',frame.case.B,state.B),
                                       ('C_before',frame.case.C,state.coherence_acc),('history_before',frame.case.history,state.history)):
                    close(want,got,field)
                old_c=state.coherence_acc.copy();old_theta=real_tuple(state.theta)
                # Sole actual target call. Expected frame was built BEFORE module import.
                self.calls+=1;physical,driver,info=self.module.advance_state(state,cfg,rng,shuffle_driver=False)
                state.validate(cfg);ownership(state)
                prediction=frame.prediction;errors={}
                for field,want,got in (('C',prediction.C,state.coherence_acc),('B',prediction.B,state.B),('theta',prediction.theta,state.theta),
                                       ('history',prediction.history,state.history),('R_physical',prediction.R,physical),('R_driver',prediction.R,driver)):
                    errors[field]=close(want,got,field)
                for flag in ('pre_violation','projection_active'):
                    if type(info[flag]) is not bool or info[flag]!=getattr(prediction,flag):raise ContractMismatch(flag,getattr(prediction,flag),info[flag])
                for field in ('g_min_pre','g_min'):errors[field]=close(getattr(prediction,field),info[field],field)
                if np.any(state.theta<0) or np.any(state.theta>=math.tau):raise ContractMismatch('phase_range','[0,2pi)',state.theta.tolist())
                if not np.array_equal(state.B,state.B.T) or np.any(state.B<0) or np.any(np.diag(state.B)!=0):raise ContractMismatch('B_structure','symmetric nonnegative diag0','bad')
                if rng_before!=json.dumps(rng.bit_generator.state,sort_keys=True):raise ContractMismatch('rng','unchanged','changed')
                # Observed data extraction; NEVER used as independent expected input.
                innovation=complex_matrix((state.coherence_acc-cfg.alpha*old_c)/(1-cfg.alpha))
                errors['input_innovation']=close(frame.input_phasor,innovation,'input_innovation')
                item=Observation(old_theta,real_tuple(state.theta),innovation,tuple(sorted(errors.items())),info['pre_violation'],info['projection_active'],real_tuple(np.sum(state.B,axis=1)))
                items.append(item);self.records.append({'case':first.name,'n':n,'N':p.N,'D':cfg.delay_steps,'theta_before':item.theta_before,
                    'theta_after':item.theta_after,'decoded_input_innovation':encoded(innovation),'component_errors':dict(item.component_errors),
                    'pre_violation':item.pre_violation,'projection_active':item.projection_active,'row_sums':item.row_sums,
                    'independent_expected_trace_before_import':True,'rng_unchanged':True,'independent_history_storage':True})
            self.observed[first.name]=tuple(items)
        require(unchanged==repr(self.traces),'Immutable independent expectations changed')
    def pairs(self):
        for trace in self.traces:
            obs=self.observed[trace.initial.name]
            for n in range(STEPS-1):
                for i in range(trace.initial.p.N):
                    for j in range(trace.initial.p.N):yield trace,obs,n,i,j


def suite(context):
    class PhaseContract(unittest.TestCase):
        def test_01_seven_complete_traces(self):context.run_traces()
        def test_02_startup_has_zero_delayed_increment(self):
            count=0
            for trace,obs,n,i,j in context.pairs():
                if n<round(trace.initial.p.tau/trace.initial.p.dt):
                    close(phasor(trace.frames[n].increment[i]),obs[n+1].innovation[i][j]/obs[n].innovation[i][j],'startup_factor');count+=1
            require(count==157,'Startup inventory mismatch')
            trace=next(t for t in context.traces if t.initial.name=='free_drift_N1_D3')
            for n,item in enumerate(context.observed[trace.initial.name]):
                close(phasor(-max(0,3-n)*0.125),item.innovation[0][0],'N1_frozen_prehistory_not_drifting')
            context.stats['startup_coordinates']=count
        def test_03_first_live_read_is_n_equals_D(self):
            count=0;nonzero=0.0
            for trace,obs,n,i,j in context.pairs():
                if n==round(trace.initial.p.tau/trace.initial.p.dt):
                    close(phasor(drift(trace,n,i,j)),obs[n+1].innovation[i][j]/obs[n].innovation[i][j],'first_live_factor')
                    nonzero=max(nonzero,error(phasor(drift(trace,n,i,j)),phasor(trace.frames[n].increment[i]),'nonvacuity'));count+=1
            require(count==62 and nonzero>MIN_WITNESS,'First-live witness vacuous/incomplete')
            context.stats.update(first_live_coordinates=count,first_live_versus_extra_delay_difference=nonzero)
        def test_04_later_live_uses_aged_increment(self):
            count=0
            for trace,obs,n,i,j in context.pairs():
                if n>round(trace.initial.p.tau/trace.initial.p.dt):
                    close(phasor(drift(trace,n,i,j)),obs[n+1].innovation[i][j]/obs[n].innovation[i][j],'later_live_factor');count+=1
            require(count==215,'Later-live inventory mismatch');context.stats['later_live_coordinates']=count
        def test_05_windings_and_valid_representative_phasor(self):
            positive=negative=multiple=0;maximum_raw=0.0;maximum_phasor=0.0
            for trace in context.traces:
                for n,item in enumerate(context.observed[trace.initial.name]):
                    frame=trace.frames[n]
                    for i,k in enumerate(frame.windings):
                        raw=item.theta_after[i]-item.theta_before[i];u=frame.increment[i]
                        close(u-math.tau*k,raw,'integer_winding_residual')
                        maximum_phasor=max(maximum_phasor,close(phasor(u),phasor(raw),'representative_phasor_positive'))
                        positive+=k>0;negative+=k<0;multiple+=abs(k)>1;maximum_raw=max(maximum_raw,abs(raw-u))
            require(positive>0 and negative>0 and multiple>0 and maximum_raw>math.tau,'Winding probes vacuous')
            context.winding_stats={'positive_windings':positive,'negative_windings':negative,'multiple_turn_windings':multiple,
                                   'maximum_raw_representative_increment_discrepancy':maximum_raw,'maximum_valid_representative_phasor_error':maximum_phasor,
                                   'representative_difference_phasor_is_valid_not_a_wrong_model':True}
        def test_06_chord_and_capacity_specialization(self):
            tight=0;maximum_excess=0.0;maximum_factor=0.0
            for trace,obs,n,i,j in context.pairs():
                v=drift(trace,n,i,j);z=obs[n].innovation[i][j];zn=obs[n+1].innovation[i][j]
                factor=zn/z;delta=close(phasor(v),factor,'input_ratio_factor');maximum_factor=max(maximum_factor,delta)
                chord=abs(zn-z);bound=abs(v);cap=capacity_bound(trace,n,i,j)
                if chord>bound+ABS_TOL:raise ContractMismatch('chord_bound',bound,chord,chord-bound)
                if bound>cap+ABS_TOL:raise ContractMismatch('capacity_specialization',cap,bound,bound-cap)
                maximum_excess=max(maximum_excess,chord-bound);tight+=chord>MIN_WITNESS and bound<2.0
                context.ratios.append({'case':trace.initial.name,'n':n,'i':i,'j':j,'startup':n<round(trace.initial.p.tau/trace.initial.p.dt),
                    'signed_increment':v,'expected_factor':[phasor(v).real,phasor(v).imag],
                    'observed_factor':[factor.real,factor.imag],'component_error':delta,'observed_chord':chord,'signed_increment_bound':bound,
                    'paper_capacity_bound':cap})
            for trace in context.traces:
                c=(trace.initial.p.a-trace.initial.p.delta)/trace.initial.p.q
                if any(row>c+ABS_TOL for item in context.observed[trace.initial.name] for row in item.row_sums):raise ContractMismatch('post_gate_capacity',c,'exceeded')
            require(tight>0 and len(context.ratios)==434,'Chord checks vacuous/incomplete')
            context.maximum_ratio_error=maximum_factor;context.stats.update(nonzero_chords_with_bound_below_two=tight,maximum_one_sided_chord_excess=maximum_excess)
        def test_07_absolute_offset_and_valid_ratio_cancellation(self):
            maximum_absolute=maximum_ratio=0.0
            for trace,obs,n,i,j in context.pairs():
                f=trace.frames[n];g=trace.frames[n+1]
                wrong0=input_phasor(f.case,f.case.history[0],True)[i][j];wrong1=input_phasor(g.case,g.case.history[0],True)[i][j]
                maximum_absolute=max(maximum_absolute,error(f.input_phasor[i][j],wrong0,'omitted_offset'))
                maximum_ratio=max(maximum_ratio,close(phasor(drift(trace,n,i,j)),wrong1/wrong0,'offset_ratio_cancellation_positive'))
            require(maximum_absolute>MIN_WITNESS,'Absolute offset probe vacuous')
            context.stats.update(omitted_offset_absolute_difference=maximum_absolute,offset_cancellation_ratio_error=maximum_ratio,
                                 constant_offset_ratio_invariance_is_valid_not_a_wrong_model=True)
        def test_08_new_gated_B_storage_and_rng(self):
            trace=next(t for t in context.traces if t.initial.name=='active_D2');frame=trace.frames[0]
            require(frame.prediction.pre_violation and frame.prediction.projection_active,'Forcing gate probe inactive')
            for name in ('old_B_increment','unprojected_B_increment'):
                require(error(phasor(drift(trace,0,0,1)),phasor(drift(trace,0,0,1,name)),name)>MIN_WITNESS,'Vacuous gated forcing control')
            require(len(context.records)==56 and all(r['rng_unchanged'] and r['independent_history_storage'] for r in context.records),'Storage/RNG incomplete')
        def test_09_C_input_is_pre_phase_and_exact_inventory(self):
            trace=next(t for t in context.traces if t.initial.name=='active_D2')
            require(error(trace.frames[0].input_phasor[0][1],trace.frames[1].input_phasor[0][1],'C_timing')>MIN_WITNESS,'C timing probe vacuous')
            require(context.calls==56 and len(context.records)==56,'Unexpected source advance count')
            require(sum(len(item.innovation)**2 for values in context.observed.values() for item in values)==496,'Input coordinate inventory mismatch')
    return unittest.defaultTestLoader.loadTestsFromTestCase(PhaseContract)


def wrong_models(traces):
    out=[]
    for name,field,expected,wrong,witness in control_witnesses(traces):
        try:close(expected,wrong,field)
        except ContractMismatch as problem:
            require(problem.field==field and problem.delta is not None and problem.delta>MIN_WITNESS,'Wrong control mechanism/tiny witness')
            out.append({'model':name,'detected':True,'intended_field':field,'detected_field':problem.field,'component_difference':problem.delta,
                        'witness':witness,'setup_errors_credited':0})
        else:raise RuntimeError('Undetected wrong model: '+name)
    require(len(out)==10,'Wrong-model inventory mismatch');return out


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--kind',choices=('common','wrong_models'),required=True);args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    try:
        # NO acquired engine import until ALL immutable math expectations are complete.
        traces=prepare_traces();design=design_record(traces);save(args.output/'preexecution_design.json',design);manifest=verify(args.source)
        require(all(r['component_difference']>MIN_WITNESS for r in design['ten_fixed_control_witnesses']),'Vacuous control before target')
        if args.kind=='wrong_models':
            records=wrong_models(traces);save(args.output/'wrong_models.json',records)
            value={'kind':'wrong_models','optimized_python':not __debug__,'detected':len(records),'records':records,'actual_engine_advances':0,
                   'actual_engine_imported':False,'setup_errors_credited':0,'source_files_unchanged':len(manifest['modules']),'metadata_files_unchanged':len(manifest['metadata'])}
        else:
            context=Context(load(args.source),traces);stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite(context));print(stream.getvalue(),end='')
            save(args.output/'advance_observations.json',context.records);save(args.output/'input_ratio_observations.json',context.ratios)
            value={'kind':'common','optimized_python':not __debug__,'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
                   'skipped':len(result.skipped),'actual_engine_advances':context.calls,'source_initializations':0,'source_cases':len(traces),
                   'input_complex_coordinates':sum(len(item.innovation)**2 for values in context.observed.values() for item in values),
                   'adjacent_complex_coordinates':len(context.ratios),'maximum_component_error':max((v for r in context.records for v in r['component_errors'].values()),default=0),
                   'maximum_ratio_component_error':context.maximum_ratio_error,'age_and_chord_stats':context.stats,'winding_stats':context.winding_stats,
                   'absolute_tolerance':ABS_TOL,'relative_tolerance':0.0,'source_files_unchanged':len(verify(args.source)['modules']),
                   'metadata_files_unchanged':len(manifest['metadata']),'independent_expected_trace_built_before_import':True,
                   'explicit_compute_R_calls_by_harness':0,'actual_full_engine_import_no_function_copy_replacement_or_edit':True,
                   'production_simulation_baseline_CLI_or_certificate_called':False,'immutable_cases_rng_and_history_ownership_verified':True}
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
    source=Path(source).resolve();manifest=verify(source);name='r040282_011_unchanged_engine'
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
"""Compile owned phase bridge + reused history with targeted prescribed Mathlib.
Eight closed-file controls; imports/timeouts/setup never semantic detections.
This fixed-owned-source integrity policy is NOT a general Lean sandbox/parser.
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
NAMES={'Researcher040282.Phase.phasor_wrap','Researcher040282.Phase.delayed_input_step',
       'Researcher040282.Phase.delayed_input_chord_bound'}
DEPENDENCIES={'Researcher040282.Delay.historyTrace_index','Researcher040282.Delay.historyTrace_oldest',
              'Researcher040282.Delay.historyTrace_newest'}

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


CONTROL_HEADER='''import PhaseIncrement
open Researcher040282.Phase
noncomputable def controlX0 (_ : Unit) : ℝ := 0
noncomputable def controlOmega (_ : Unit) : ℝ := 0
noncomputable def controlU (n : ℕ) (_ : Unit) : ℝ := if n = 0 then Real.pi / 2 else Real.pi
'''
Z='inputPhasor 1 controlX0 controlU controlOmega 1'
STARTUP='''  have h0 : inputPhasor 1 controlX0 controlU controlOmega 1 0 () () = 1 := by
    simp [inputPhasor, Researcher040282.Delay.historyTrace, phaseTrace, controlX0, controlOmega, phasor]
  have hd : delayedIncrement 1 controlU 0 () = 0 := by simp [delayedIncrement]
  have hi : phasor (controlU 0 ()) = Complex.I := by simp [controlU, phasor]
  have h := delayed_input_step 1 controlX0 controlU controlOmega 1 0 () ()
  rw [h0, hd, sub_zero, one_mul, hi] at h
  exact h
'''
LIVE='''  have hs : inputPhasor 1 controlX0 controlU controlOmega 1 1 () () = Complex.I := by
'''+''.join('  '+line+'\n' for line in STARTUP.splitlines())+'''  have hi : phasor (controlU 1 () - delayedIncrement 1 controlU 1 ()) = Complex.I := by
    have hd : controlU 1 () - delayedIncrement 1 controlU 1 () = Real.pi / 2 := by
      dsimp [controlU, delayedIncrement]
      ring
    rw [hd]
    simp [phasor]
  have h := delayed_input_step 1 controlX0 controlU controlOmega 1 1 () ()
  rw [hs, hi, Complex.I_mul_I] at h
  exact h
'''


def indent(text):return ''.join('  '+line+'\n' for line in text.splitlines())


def controls():
    startup=CONTROL_HEADER+'theorem controlStartup : '+Z+' 1 () () = Complex.I := by\n'+STARTUP+'#print axioms controlStartup\n'
    live=CONTROL_HEADER+'theorem controlLive : '+Z+' 2 () () = -1 := by\n'+LIVE+'#print axioms controlLive\n'
    no_wrap=CONTROL_HEADER+'''example : wrapPhase (2 * Real.pi) = 2 * Real.pi := by
  norm_num [wrapPhase, Real.pi_ne_zero]
'''
    early=CONTROL_HEADER+'example : '+Z+' 1 () () = '+Z+' 0 () () * phasor (controlU 0 () - controlU 0 ()) := by\n'+\
        '  have hs : '+Z+' 1 () () = Complex.I := by\n'+indent(STARTUP)+\
        '''  rw [hs]
  norm_num [inputPhasor, Researcher040282.Delay.historyTrace, phaseTrace, controlX0, controlOmega, phasor, Complex.ext_iff]
'''
    wrong_age=CONTROL_HEADER+'example : '+Z+' 2 () () = '+Z+' 1 () () * phasor (controlU 1 () - controlU 1 ()) := by\n'+\
        '  have hs : '+Z+' 1 () () = Complex.I := by\n'+indent(STARTUP)+\
        '  have hl : '+Z+' 2 () () = -1 := by\n'+indent(LIVE)+'''  rw [hl, hs]
  norm_num [phasor, Complex.ext_iff]
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
    return (('positive_startup_nonzero','positive',startup,None),('positive_live_nonzero','positive',live,None),
            ('false_no_wrap','false_math',no_wrap,None),('false_startup_delayed_increment','false_math',early,None),
            ('false_current_instead_of_aged','false_math',wrong_age,None),
            ('compiling_sorry','integrity',sorry,'forbidden_source:sorry'),
            ('compiling_extra_axiom','integrity',axiom,'unapproved_axiom_footprint'),
            ('omitted_axiom_print','integrity',omitted,'axiom_print_coverage'))


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


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--lean',type=Path,required=True)
    parser.add_argument('--mathlib',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    try:
        compiler=args.lean.resolve();mathlib=args.mathlib.resolve();env,version,revision=proof_environment(compiler,mathlib)
        sources=args.output/'compiled_sources';sources.mkdir(exist_ok=True);logs=args.output/'compiler_logs';logs.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='r040282-011-lean-') as temporary:
            work=Path(temporary);env['LEAN_PATH']=str(work)+os.pathsep+env['LEAN_PATH']
            def compile_one(name,text,produce=False):
                filename=name+'.lean';(work/filename).write_text(text);(sources/filename).write_text(text)
                command=[str(compiler),'--root='+str(work)]+(['-o',str(work/(name+'.olean'))] if produce else [])+[filename]
                run=subprocess.run(command,cwd=work,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180)
                (logs/(name+'.log')).write_text(run.stdout)
                if re.search(r'unknown module|object file .* does not exist|failed to import|cannot open shared object|unknown namespace|unknown identifier|unknown constant|unknown tactic|failed to synthesize|maximum.*(?:recursion|heartbeats)|deterministic timeout|unexpected token|invalid field',run.stdout,re.I):
                    raise RuntimeError('Import/parse/elaboration/runtime blocker, never mathematical detection: '+name)
                return run,assess(text,run.stdout,run.returncode)
            _,dependency=compile_one('HistoryBuffer',(HERE/'HistoryBuffer.lean').read_text(),True)
            require(dependency['accepted'] and set(dependency['footprints'])==DEPENDENCIES and len(dependency['named_declarations'])==3,'Reused history dependency failed')
            _,main_policy=compile_one('PhaseIncrement',(HERE/'PhaseIncrement.lean').read_text(),True)
            require(main_policy['accepted'] and set(main_policy['footprints'])==NAMES and len(main_policy['named_declarations'])==3,
                    'Main theorem acceptance failed: '+json.dumps(main_policy))
            def evaluate(item):
                name,kind,text,intended=item;run,policy=compile_one(name,text)
                if kind=='positive':require(run.returncode==0 and policy['accepted'],'Nonzero positive rejected: '+name)
                elif kind=='false_math':
                    require(run.returncode!=0 and not policy['accepted'] and re.search(r'unsolved goals',run.stdout,re.I) and
                            re.search(r'⊢\s*False',run.stdout),'False math witness did not reduce to explicit False: '+name)
                else:require(run.returncode==0 and not policy['accepted'] and intended in policy['reasons'],'Integrity payload wrong rejection mechanism: '+name)
                return {'control':name,'kind':kind,'expected_mechanism':intended,'expected_outcome_observed':True,'policy':policy,'setup_errors_credited':0}
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:records=list(pool.map(evaluate,controls()))
        require(len(records)==8,'Formal control inventory incomplete')
        value={'compiler_version':version,'mathlib_revision':revision,'Mathlib_used':True,'dependency':dependency,'main':main_policy,
               'new_named_declarations_compiled':3,'reused_named_history_declarations_recompiled_not_new_labels':3,'formal_controls':8,
               'positive_controls_accepted':2,'false_math_witnesses_rejected_by_compiler':3,'compiling_integrity_payloads_rejected_by_policy':3,
               'controls':records,'setup_errors_credited':0,'all_preregistered_formal_conditions_met':True,
               'scope':'Exact-real floor modulo/complex input identity and signed-increment chord bound, not Python/float FFI, full coupled dynamics or locking; fixed-file policy not general sandbox'}
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
DEFAULT=Path.home()/'.cache/researcher040282-cycle011'


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
"""011 bounded phase-input contract: full engine normal/-O + actual Lean proof.
Prerequisite separate disposable compiler/targeted Mathlib setup. No production
study, full baseline, shuffle/intervention, CLI/certificate or frozen-file edit.
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
    p.add_argument('--lean',type=Path,required=True);p.add_argument('--mathlib',type=Path,required=True);args=p.parse_args()
    args.output.mkdir(parents=True,exist_ok=True);start=time.perf_counter()
    try:
        manifest=verify(args.source)
        require((args.source/'lean/AIEFProofs/lean-toolchain').read_text().strip()==manifest['lean_toolchain']['toolchain'],'Source compiler prescription mismatch')
        lake=json.loads((args.source/'lean/AIEFProofs/lake-manifest.json').read_text());mathlib=next(row for row in lake['packages'] if row['name']=='mathlib')
        require(mathlib['rev']==manifest['mathlib']['revision'],'Source Mathlib prescription mismatch')
        require(args.lean.is_file() and args.mathlib.is_dir(),'Compiler/dependency setup blocker')
        env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONOPTIMIZE',None);workers=[]
        for kind in ('common','wrong_models'):
            for optimized in (False,True):
                name=kind+('_optimized' if optimized else '_normal');directory=args.output/name;begin=time.perf_counter()
                command=[sys.executable]+(['-O'] if optimized else [])+['-B',str(HERE/'check_engine.py'),'--kind',kind,
                          '--source',str(args.source.resolve()),'--output',str(directory.resolve())]
                run=subprocess.run(command,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=env,timeout=90)
                (args.output/(name+'.log')).write_text(run.stdout)
                require((directory/'result.json').is_file(),'Worker failed before result, not a falsifier: '+name)
                value=json.loads((directory/'result.json').read_text())
                require(run.returncode==0 and value['optimized_python'] is optimized and value['source_files_unchanged']==1 and value['metadata_files_unchanged']==3,
                        'Source/control worker failed or dependency changed: '+name)
                if kind=='common':
                    require(value['tests_run']==9 and value['failures']==value['errors']==value['skipped']==0 and value['actual_engine_advances']==56 and
                            value['source_initializations']==0 and value['source_cases']==7 and value['input_complex_coordinates']==496 and
                            value['adjacent_complex_coordinates']==434 and value['age_and_chord_stats']['startup_coordinates']==157 and
                            value['age_and_chord_stats']['first_live_coordinates']==62 and value['age_and_chord_stats']['later_live_coordinates']==215 and
                            value['maximum_component_error']<=5e-13 and value['maximum_ratio_component_error']<=5e-13 and
                            value['absolute_tolerance']==5e-13 and value['relative_tolerance']==0,'Common inventory/acceptance mismatch: '+name)
                else:require(value['detected']==10 and value['setup_errors_credited']==0 and value['actual_engine_advances']==0 and
                             not value['actual_engine_imported'],'Wrong-model inventory/mechanism mismatch: '+name)
                value['observed_returncode']=run.returncode;value['elapsed_seconds']=time.perf_counter()-begin;workers.append(value)
                print(name,'return0 / preregistered outcomes verified',flush=True)
        for kind in ('common','wrong_models'):
            values=[{k:v for k,v in row.items() if k not in ('elapsed_seconds','optimized_python')} for row in workers if row['kind']==kind]
            require(values[0]==values[1],'Normal/-O non-timing records differ: '+kind)
        save(args.output/'worker_results.json',workers);proof_start=time.perf_counter()
        run=subprocess.run([sys.executable,'-B',str(HERE/'check_lean.py'),'--lean',str(args.lean.resolve()),'--mathlib',str(args.mathlib.resolve()),
                            '--output',str((args.output/'proof').resolve())],env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=600)
        (args.output/'proof.log').write_text(run.stdout)
        require(run.returncode==0 and (args.output/'proof/result.json').is_file(),'Formal proof/control run blocked, never detection')
        proof=json.loads((args.output/'proof/result.json').read_text())
        require(proof['all_preregistered_formal_conditions_met'] and proof['new_named_declarations_compiled']==3 and
                proof['reused_named_history_declarations_recompiled_not_new_labels']==3 and proof['formal_controls']==8 and proof['setup_errors_credited']==0,
                'Incomplete formal acceptance')
        common=next(row for row in workers if row['kind']=='common')
        science={'tested_main':manifest['commit'],'source_contract_methods_each_mode':9,'source_passes_each_mode':9,'source_failures_errors_skips_each_mode':[0,0,0],
                 'actual_advances_each_common_mode':56,'initializer_calls_each_common_mode':0,'synthetic_traces_each_mode':7,
                 'complex_input_coordinates_each_mode':496,'adjacent_complex_coordinates_each_mode':434,'startup_coordinates_each_mode':157,
                 'live_coordinates_each_mode':277,'first_live_coordinates_each_mode':62,'later_live_coordinates_each_mode':215,
                 'maximum_observed_component_error':common['maximum_component_error'],'maximum_ratio_component_error':common['maximum_ratio_component_error'],
                 'age_and_chord_stats':common['age_and_chord_stats'],'winding_stats':common['winding_stats'],
                 'absolute_tolerance':5e-13,'relative_tolerance':0.0,'wrong_models_detected_each_mode':10,'setup_errors_credited_as_detections':0,
                 'normal_optimized_nontiming_results_match':True,'new_named_Lean_declarations_actually_compiled':3,
                 'reused_history_declarations_recompiled_not_new_labels':3,'formal_controls':8,'formal_positive_controls':2,'formal_false_math_controls':3,
                 'formal_compiling_integrity_controls':3,'axiom_footprints':proof['main']['footprints'],'targeted_Mathlib_used':True,
                 'reviewed_public_engine_unchanged':1,'reviewed_metadata_unchanged':3,'actual_engine_import_no_copied_replaced_or_edited_source_functions':True,
                 'no_source_repair_or_failing_before_claim':True,'all_preregistered_acceptance_conditions_met':True}
        record={'science':science,'environment':{'python':sys.version,'numpy':np.__version__,'compiler':proof['compiler_version'],'mathlib_revision':proof['mathlib_revision']},
                'elapsed_seconds':time.perf_counter()-start,'formal_elapsed_seconds':time.perf_counter()-proof_start,
                'scope':'Exact-real modulo-safe startup-aware delayed input/chord theorem plus finite intact-engine correspondence. Not a Lean proof of Python/float FFI, full coupled map/locking, production baseline, certificate, integration or independent approval.'}
        verify(args.source);save(args.output/'cycle_results.json',record);print(json.dumps(record,indent=2));return 0
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
  "commit": "eb3933c196ee19e80e1621ae80d89ca72e6d9485",
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
    "scope": "Disposable complete runtime for targeted Mathlib cache; no global setting; no raw uploader/contact/signature metadata in packet",
    "metadata_provenance": "Inherited official release selected record from completed010; current source prescription matches; fresh release API unavailable (403); actual download reverified"
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
      "Mathlib/Tactic/Linarith.lean"
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
"""Extract the thirteen named critical011 files. No execution or fetching."""
import argparse
import json
from pathlib import Path
import re

NAMES={'HistoryBuffer.lean','PhaseIncrement.lean','phase_contract.py','prepare_mathlib.py','step_contract.py','check_engine.py','load_reviewed.py','check_lean.py',
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

