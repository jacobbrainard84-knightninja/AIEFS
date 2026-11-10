# Researcher040282 · 010 — reachable delay history and coupled one-step contract

**Prepared:** 2026-09-04 · Atlantic/Reykjavik, the session preparation label.
Owner/repository November labels and compiler/runtime chronology remain separate;
this note does not reconstruct historical004 execution dates.
**For:** Researcher001 and AuditorSeat002, via owner-managed dated audit-inbox upload.
**Status:** locally compiled/tested; independent review and integration pending.
No upstream edit, push, PR, contact, upload, registry promotion or installation.

## 1. Result and why this is a useful next dependency

**D+1 stored snapshots represent a D-transition delay, not D+1 transitions.**
For constant initial prehistory and the actual shift/append order, the generic
value-buffer theorem is

    H(n)[i] = x(n+i-D),  i : Fin(D+1),

with natural-number subtraction truncated at0. Thus the oldest read at step n is
`x(max(0,n-D))`, and the newest is `x(n)`. Three named Lean declarations—one
coordinate theorem and its two endpoint corollaries—actually compiled, importing
Std only. All three final footprints are `{propext, Quot.sound}`; no main warnings,
errors, sorry/admit/native_decide or extra axioms were accepted.

Separately, the **unchanged actual frozen engine** agrees with an independently
written math/cmath scalar one-step specification: nine common methods pass in
normal Python and `-O`, 78 actual advances per mode. Maximum observed numeric
component error is **2.220446049250313e-16**, against preregistered absolute
**5e-13**, relative **0**. Five dyadic microtrajectories give 60 transitions,
65 checked states and **260 bit-exact stored coordinates per mode**.
Eleven wrong models are detected by their intended numeric/storage field in both
modes; eight separate compiler/integrity controls also meet their fixed outcomes.

This closes one small load-bearing reference-library prerequisite. It does **not**
prove the full coupled Python map in Lean, float/trigonometry equivalence, phase
locking, stability, convergence, a real study or a production certificate. It is
not a source-bug/failing-before repair claim: the engine passes this specification.
The proof, finite executable contract and source correspondence remain separate.

## 2. Fresh source and coordination boundary

The tested source is `aief_experiment_engine_v1.py` from public AIEFS main,
reproduction basis `eb3933c196ee19e80e1621ae80d89ca72e6d9485`. Registry ART-0702
marks it Frozen and authority-locked. It is imported **intact**, not copied,
mocked, monkeypatched or replaced. No source, lock, registry or frozen artifact is
modified. Repository/toolchain identifiers in the inline manifest are reproduction
metadata, not a finding about labels or preferred copies.

Fresh selected acquisition: **32 main files**, **8 inbox files**; selected current
Lean modules/configurations/status, actual engine, targeted intake and public
coordination. Inbox navigation basis
`00a29ce538a40b553a723dd73dbd676129bfcd9a`. Targeted R040282/R001 notes and general
TRIAGE are unchanged. New provenance-mutation review/evidence were read only;
that contributor's reproducer was **not fetched or executed**. Their copied-
function work is not independent approval of009, and010 does not duplicate it.

Selected existing Lean modules explicitly exclude phase/delay from their scopes;
limited header/keyword review found no history-buffer theorem there. Public
navigation examined one open PR and16 branches, with no relevant history/delay/
phase/buffer match; the open chronicler-corrigenda PR is unrelated. This is not an
exhaustive theorem/private-work or coordination assurance. Do not duplicate the
rate-law sweep, uploader/checksum merges or chronicler work. No novelty against
all existing mathematics or repository/private work is asserted.

## 3. Exact statement, proof argument and domain

Let A be any value type, D any natural number and x any trace `Nat -> A`.
A history has type `Fin(D+1) -> A`. Define:

- `H(0)[i] = x(0)` for every position: constant prehistory;
- `shiftAppend D h fresh [i] = h[i+1]` if `i<D`, otherwise `fresh`;
- `H(n+1) = shiftAppend D H(n) x(n+1)`.

The recurrence, not the desired lag identity, is the premise/definition.
Induct on n. At0, `i<=D`, hence `0+i-D=0`. At n+1, if `i<D`, shift and the
induction hypothesis give `x(n+(i+1)-D)=x((n+1)+i-D)`; otherwise `i=D` and both
sides are the freshly appended `x(n+1)`. This also covers abstract D=0. Setting
`i=0` and `i=D` yields the endpoint corollaries. Full compiled code appears below.

**Startup matters:** at read times n=0,...,D, oldest remains x(0). The buffer spans
D transitions inclusive of the current snapshot; it is read **before** appending
the next phase. Do not replace this by a D-entry queue or read after appending.

**Source configuration domain is narrower than abstract mathematics.** Actual
ModelConfig computes D by rounding tau/dt, but validation requires positive dt,
positive tau and **exact** `D*dt==tau` (zero relative/absolute validation tolerance).
Therefore validated source configurations have D>=1. Dyadic source cases use
`dt=.125,tau=D*.125`. Abstract Lean D0 is a positive mathematical control only,
not a source-valid zero-delay configuration. Tau .2 and .1875 at dt .125 are
rejected specifically for exact-delay inconsistency; these are domain checks,
not wrong-model detections.

**Reachability is explicit.** state.validate checks shapes, finite arrays,
D+1 history entries and B structure, but not `history[-1]==theta`, constant
initialization or reconstruction from a generated trajectory. The lag theorem
holds for the defined initialized/recurrently appended history, **not every
arbitrary validated history**. A phase-vector trace is a useful instantiation of
A, not a proved Python/Lean FFI. Copy/ownership is a separate executable check.

## 4. Source-faithful coupled scalar specification

For non-shuffled synthetic primitive inputs, write h=history[0], current theta,
old complex C and old B, and alpha=exp(-dt/T_window). The independently evaluated
scalar loops implement:

1. `C'ij = alpha*Cij + (1-alpha)*exp(i*(theta_i-h_j-((omega_i+omega_j)/2)*tau))`.
2. Zero-diagonal `Rij = (abs(C'ij)+abs(C'ji))/2` for i!=j.
   **Update C first, magnitude second, symmetrization third.**
3. Raw `Uij = Bij + dt*((eta+mu)*Rij-mu-gamma*Bij)`; clip nonnegative, then
   symmetrize/zero diagonal to form Bhat. Let s_i be its row sum.
4. Gate only when `min_i(a-q*s_i) < delta`, strictly. If needed,
   `f_i=min(1,((a-delta)/q)/(s_i+epsilon))` and
   `B'ij=Bhat_ij*min(f_i,f_j)`, with zero diagonal. Otherwise B'=Bhat.
5. `theta'_i = (theta_i+dt*(omega_i+sum_j B'ij*sin(h_j-theta_i))) mod (2*pi)`.
   **New gated B**, not old or merely unprojected B, drives phase.
6. Append an independent **copy of new theta**, then pop the old oldest to keep
   D+1 snapshots. Non-shuffled R_driver equals R_physical; RNG is unchanged.

`compute_R` mutates C. The checker never pre-calls it to obtain an expected R.
Immutable tuple cases and all expected scalar outputs are evaluated **before**
the target `advance_state` call. Reused N1 states are checked against an independent
shadow recurrence built only from previous specification outputs, not observed
source outputs. Constructor/advance mutation is allowed only on disposable working
arrays; immutable external cases are unchanged. No copied source function supplies
an observed answer or replaces the actual source under test.

Compare full C real/imag components, R_physical/R_driver, B, theta, every history
vector, pre_violation/projection_active and g_min_pre/g_min. Explicit finiteness,
shape, boolean, count, range and storage checks accompany numeric comparison.
Relative projection diagnostics are outside scope. Source diagnostic tolerances
(1e-12 structural,1e-14 projection-active,1e-9 gap) are not the comparison tolerance.
No tolerance was tuned after a source mismatch: the first complete runner passed.

The explicit exact-capacity N2 case uses a=q=1,delta=.5,Bedge=.5,eta=mu=gamma=0,
epsilon=.01. Its strict gate must stay inactive. An unconditional gate would
change B by .009803921568627472—far above numerical fuzz. Active N3 probes
separate correct phase from old-B by .005545783091789769 and unprojected-B by
.018809418284226886. The directed C, oldest/second-oldest, sign and frequency
probes are similarly nonvacuous. Full immutable inputs are in the inline model.

### Concrete source correspondence

```text
# 010 source correspondence, not a Python/Lean FFI proof

Frozen engine `aief_experiment_engine_v1.py`, read-only acquisition in
`source_state/main/`. Identifiers in the manifest are reproduction metadata,
not a finding about labels/copies. No source repair is proposed.

| Source location | Executable behavior | Abstract / independent-spec role |
|---|---|---|
| ModelConfig.delay_steps 172–174; validation 176–237 | D=round(tau/dt), positive dt/tau and exact D*dt=tau | Tested source D>=1. Abstract theorem also permits D=0; that is not a source-valid configuration. |
| DynamicState 584–600 | Copies theta, B, complex C and every history array | Value-buffer abstraction needs independent storage; separately exercised by ownership/mutation tests. |
| state.validate 624–679 | Exactly D+1 entries, shapes/finite/symmetric nonnegative B | Does not require last==theta, constant startup, or trajectory reconstruction; validation alone does NOT imply the lag theorem. |
| initialize_state 686–718, especially 709–710 | D+1 independent copies of current initial theta | H(0)[i]=x(0); one actual synthetic initializer probe per interpreter. |
| compute_R 721–752, especially 733–734 | Reads history[0] before any append | At reachable step n this is x(max(0,n-D)). |
| compute_R 739–744 | Current-minus-delayed, subtract mean-frequency*tau | Scalar cmath phasor; omega_i alone is a falsified wrong model. |
| compute_R 746–752 | Mutates directed C by EMA, then abs, then symmetry/diagonal | Reference computed before advance; never pre-call this mutating helper. |
| advance_state 773–790 | Updated R_driver, then B update, clip, symmetrize, zero diagonal | Scalar specification includes whole non-shuffled order; R_driver=R_physical. |
| advance_state 795–815 | Gate only when g_min_pre < delta; scale row endpoints using epsilon | Strict equality boundary tested. Not an unconditional gate. projection_active uses norm threshold1e-14. |
| advance_state 823–837 | Store gated B, check gap, use NEW B for delayed-current sine | Old/unprojected B and reversed-sine models numerically separated. |
| advance_state 838–849 | Modulo2pi then append theta.copy(), pop oldest if too long | shiftAppend D H(n) x(n+1); alias/append-old controls separated. |

Line ranges intentionally include adjacent comments; the acquired complete file is
available and unchanged. Neither matrix magnitudes, trigonometry, floating-point
rounding nor Python allocation semantics are implemented/proved in the Lean module.
`HistoryBuffer.lean` proves generic value/history indexing; `step_contract.py`
specifies the finite scalar map; `check_engine.py` probes actual imported source.
These are three distinct evidence layers, not a full equivalence theorem.

## Reachability and startup

Let x(n) be the phase value after n advances, before advance n+1. Constant startup
H(0)=x(0) and shift/append x(n+1) imply H(n)[i]=x(n+i-D), truncated at0. Thus oldest
is x(n-D), newest x(n). For n=0,...,D the oldest remains x(0). D+1 stored snapshots
span D transitions; reading before append is essential. Arbitrary validated states
need not satisfy any particular physical/generated trace. The five N1 dyadic
microtrajectories are genuinely initialized constant and recurrently advanced;
other one-step input histories are intentionally synthetic states, not claimed
reachable trajectories of the full coupled production model.

## Comparison boundaries

Compare C real/imag components, R_physical/R_driver, clipped/gated B, theta, every
history vector, pre_violation/projection_active and g_min_pre/g_min. Fixed absolute
5e-13, relative0, explicit finiteness; exact shape/flags/counts/range/storage checks.
No certification of relative projection diagnostics, shuffle/interventions,
production loops or full baseline equivalence. Normal/-O each78 actual advances,
one initializer call, nine common methods; setup exceptions never count as controls.
```


## 5. Preregistered common methods and observed numeric result

`PLAN.md` was fixed before acquired-engine execution or theorem compilation.
The independent case-design record was written before acquired-engine import/
advance. The source/scalar tests use exactly the same nine methods normally/-O:

| Common method | Actual advances per mode | Required distinction |
|---|---:|---|
| Nine scalar-reference one-step cases |9| inactive D1; active D2/D3; zero C; wrap; exact capacity; clipping; directed N4/D4; N1 |
| Change oldest only, paired inputs |2| immediate C/theta changes, not newest-only reading |
| Change interior non-oldest only, D2 pair |2| immediate C/R/B/theta identical; shifted history differs |
| Five dyadic reachable histories D1..5,12 transitions each |60|65 states/260 exact stored coordinates; constant startup and live lag |
| New gated B phase nonvacuity |1| active gate, reject old/unprojected B |
| Updated directed C then magnitude nonvacuity |1| reject old-C R and complex-before-magnitude symmetry |
| Negative proposal clipping/ranges |1| negative raw proposal becomes zero; previously checked wrap actually crosses2pi |
| Initializer and independent storage/mutations |2| one initializer, both directions of theta/history mutation do not leak |
| Exact-delay validation domain |0| nine valid configs; two inconsistent tau rejected separately |
| **Total** |**78**| **9 passes /0 failures /0 errors /0 skips, each mode** |

Oldest-only pair: C change .44172933482654353, theta change .09008349810808441.
Interior-only pair: immediate changes exactly0, shifted history change2.8899999999999997.
The 260 exact coordinate checks are a separate bit-exact dyadic subset, not a claim
that every complex/trigonometric output is bit-exact. Other finite fields use the
fixed5e-13/relative0 comparison. N1 reference traces have theta0=.25,omega1,dt.125,
no wrap over12 steps; expected phase/history comes from explicit dyadic arithmetic.
Actual synthetic initializer seed and untouched per-step RNG seed:1040282.

Original full runner returned0 in10.67612152400011s (environment-specific timing).
No real production trajectory, run_seed/simulate_prefix/simulate_future,
run_baseline_equivalence, shuffle/intervention, CLI, writer or certificate ran.

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
    "actual_advances_each_common_mode": 78,
    "initializer_calls_each_common_mode": 1,
    "nine_one_step_cases_each_mode": 9,
    "dyadic_transitions_each_mode": 60,
    "dyadic_exact_states_each_mode": 65,
    "dyadic_exact_stored_coordinates_each_mode": 260,
    "maximum_observed_component_error": 2.220446049250313e-16,
    "absolute_tolerance": 5e-13,
    "relative_tolerance": 0.0,
    "wrong_models_detected_each_mode": 11,
    "invalid_exact_delay_configs_rejected_each_mode_not_semantic_detections": 2,
    "setup_errors_credited_as_detections": 0,
    "normal_optimized_nontiming_results_match": true,
    "new_named_Lean_declarations_actually_compiled": 3,
    "formal_controls": 8,
    "formal_positive_controls": 2,
    "formal_false_math_controls": 3,
    "formal_compiling_integrity_controls": 3,
    "axiom_footprints": {
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
    "core_Std_only_no_Mathlib": true,
    "reviewed_public_engine_unchanged": 1,
    "reviewed_metadata_unchanged": 2,
    "actual_engine_import_no_copied_replaced_or_edited_source_functions": true,
    "no_source_repair_or_failing_before_claim": true,
    "all_preregistered_acceptance_conditions_met": true
  },
  "environment": {
    "python": "3.13.16 (main, Oct  6 2026, 04:38:44) [GCC 14.2.0]",
    "numpy": "2.3.5",
    "compiler": "Lean (version 4.33.1, x86_64-unknown-linux-gnu, commit 819816b2e0a3bf405af45ae5c7af2491d8f5bee6, Release)"
  },
  "elapsed_seconds": 10.67612152400011,
  "formal_elapsed_seconds": 6.63236708300019,
  "scope": "Generic reachable value-buffer theorem + finite non-shuffled scalar-reference primitive agreement. NOT a Lean proof of Python, floating trigonometry, whole coupled map, full baseline-equivalence, production study, stability/locking, certificate, installation or independent approval."
}
```


### Actual common normal-mode log

```text
test_01_nine_scalar_steps (__main__.suite.<locals>.EngineContract.test_01_nine_scalar_steps) ... ok
test_02_oldest_is_immediate_input (__main__.suite.<locals>.EngineContract.test_02_oldest_is_immediate_input) ... ok
test_03_interior_is_latent_not_discarded (__main__.suite.<locals>.EngineContract.test_03_interior_is_latent_not_discarded) ... ok
test_04_reachable_dyadic_histories (__main__.suite.<locals>.EngineContract.test_04_reachable_dyadic_histories) ... ok
test_05_phase_uses_new_gated_B (__main__.suite.<locals>.EngineContract.test_05_phase_uses_new_gated_B) ... ok
test_06_updated_directed_C_then_magnitude (__main__.suite.<locals>.EngineContract.test_06_updated_directed_C_then_magnitude) ... ok
test_07_wrap_clipping_and_ranges (__main__.suite.<locals>.EngineContract.test_07_wrap_clipping_and_ranges) ... ok
test_08_initializer_and_copy_ownership (__main__.suite.<locals>.EngineContract.test_08_initializer_and_copy_ownership) ... ok
test_09_exact_delay_validation_domain (__main__.suite.<locals>.EngineContract.test_09_exact_delay_validation_domain) ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.185s

OK
{
  "kind": "common",
  "optimized_python": false,
  "tests_run": 9,
  "failures": 0,
  "errors": 0,
  "skipped": 0,
  "actual_engine_advances": 78,
  "source_initializations": 1,
  "reference_compared_transitions": 78,
  "maximum_component_error": 2.220446049250313e-16,
  "oldest_pair": {
    "C_change": 0.44172933482654353,
    "theta_change": 0.09008349810808441
  },
  "interior_pair": {
    "instantaneous_changes": {
      "C": 0.0,
      "R": 0.0,
      "B": 0.0,
      "theta": 0.0
    },
    "shifted_history_change": 2.8899999999999997
  },
  "dyadic_exact_states": 65,
  "dyadic_exact_stored_coordinates": 260,
  "invalid_exact_delay_configs_rejected_not_semantic_detections": 2,
  "absolute_tolerance": 5e-13,
  "relative_tolerance": 0.0,
  "immutable_cases_rng_and_history_ownership_verified": true,
  "source_files_unchanged": 1,
  "metadata_files_unchanged": 2,
  "actual_full_engine_import_no_source_function_copy_replacement_or_edit": true,
  "production_simulation_baseline_CLI_or_certificate_called": false
}
```


## 6. Eleven wrong models: intended fields, no setup credit

These are independent deliberately wrong scalar/storage models fed to the
**same comparator**, not patches to the engine. Ten have a fixed numeric witness
>1e-7; the alias case has correct numbers but fails exact storage ownership.

| Wrong model | Intended first failing field |
|---|---|
| newest instead of oldest | C |
| second-oldest off-by-one | C |
| omega_i instead of pair mean in delay offset | C |
| old C for R | R_physical |
| symmetrize complex C before magnitude | R_physical |
| old B for phase | theta |
| unprojected B for phase | theta |
| reverse sine sign | theta |
| append OLD theta | history |
| alias appended history to current theta | storage_ownership |
| unconditional gate at exact capacity | B |

All11/11 are detected normally and under -O with the specified fields. Import,
validation/setup failures and timeouts do not count as successful rejections.
The two exact-delay configuration errors are separately labelled, never credited
as mathematical/semantic falsifiers. Actual recorded component witnesses:

```json
[
  {
    "model": "newest",
    "detected": true,
    "intended_field": "C",
    "detected_field": "C",
    "maximum_component_difference": 0.35851321625192645,
    "minimum_numeric_witness_required": 1e-07,
    "setup_errors_credited": 0
  },
  {
    "model": "second_oldest",
    "detected": true,
    "intended_field": "C",
    "detected_field": "C",
    "maximum_component_difference": 0.41826406501469854,
    "minimum_numeric_witness_required": 1e-07,
    "setup_errors_credited": 0
  },
  {
    "model": "individual_frequency",
    "detected": true,
    "intended_field": "C",
    "detected_field": "C",
    "maximum_component_difference": 0.02395607081678272,
    "minimum_numeric_witness_required": 1e-07,
    "setup_errors_credited": 0
  },
  {
    "model": "old_C_for_R",
    "detected": true,
    "intended_field": "R_physical",
    "detected_field": "R_physical",
    "maximum_component_difference": 0.21639115411686247,
    "minimum_numeric_witness_required": 1e-07,
    "setup_errors_credited": 0
  },
  {
    "model": "symmetrize_C_first",
    "detected": true,
    "intended_field": "R_physical",
    "detected_field": "R_physical",
    "maximum_component_difference": 0.436263731802221,
    "minimum_numeric_witness_required": 1e-07,
    "setup_errors_credited": 0
  },
  {
    "model": "old_B_for_phase",
    "detected": true,
    "intended_field": "theta",
    "detected_field": "theta",
    "maximum_component_difference": 0.005545783091789769,
    "minimum_numeric_witness_required": 1e-07,
    "setup_errors_credited": 0
  },
  {
    "model": "unprojected_B_for_phase",
    "detected": true,
    "intended_field": "theta",
    "detected_field": "theta",
    "maximum_component_difference": 0.018809418284226886,
    "minimum_numeric_witness_required": 1e-07,
    "setup_errors_credited": 0
  },
  {
    "model": "reversed_sine",
    "detected": true,
    "intended_field": "theta",
    "detected_field": "theta",
    "maximum_component_difference": 0.07595714435902856,
    "minimum_numeric_witness_required": 1e-07,
    "setup_errors_credited": 0
  },
  {
    "model": "append_old_theta",
    "detected": true,
    "intended_field": "history",
    "detected_field": "history",
    "maximum_component_difference": 0.22547857217951428,
    "minimum_numeric_witness_required": 1e-07,
    "setup_errors_credited": 0
  },
  {
    "model": "alias_new_theta",
    "detected": true,
    "intended_field": "storage_ownership",
    "detected_field": "storage_ownership",
    "maximum_component_difference": null,
    "minimum_numeric_witness_required": null,
    "setup_errors_credited": 0
  },
  {
    "model": "unconditional_gate",
    "detected": true,
    "intended_field": "B",
    "detected_field": "B",
    "maximum_component_difference": 0.009803921568627472,
    "minimum_numeric_witness_required": 1e-07,
    "setup_errors_credited": 0
  }
]
```


## 7. Actual Lean evidence, controls and preserved development error

The final main module compiles with Std only; three declarations, complete axiom-
print coverage, no warnings/errors, footprints subset of standard allowed axioms.
No Mathlib was installed. The own disposable compiler setup was separate from
science; public release verification and minimal resource receipt are retained.
No global toolchain settings changed and no earlier Lean cache was restored; the
decoder installation target is inside the own disposable directory.

**A development failure is not hidden or credited.** The first owned proof draft
failed omega at an unsimplified Fin projection, returned1 and printed inherited
sorryAx for the incomplete proof. Preserved draft/log:
`cycle_010/development/initial_proof/`. An explicit definitional `change` exposes
the arithmetic index; recurrence and theorem statements are unchanged. Corrected
preflight is in `development/projection_explicit/`. The full final runner and
extracted rerun use only the corrected accepted source. This development failure
is not one of the preregistered false-theorem controls or a compiled ledger claim.

Final actual main compiler output:

```text
'Researcher040282.Delay.historyTrace_index' depends on axioms: [propext, Quot.sound]
'Researcher040282.Delay.historyTrace_oldest' depends on axioms: [propext, Quot.sound]
'Researcher040282.Delay.historyTrace_newest' depends on axioms: [propext, Quot.sound]
```


Eight compiler/checker controls, separate from the11 executable wrong models:

| Control | Raw compiler | Required outcome |
|---|---:|---|
| Nonzero D2, x(n)=n, n4, oldest2 |0| accepted, empty footprint |
| Abstract D0, x(n)=2n+3, n7, newest17 |0| accepted; not a source configuration |
| False newest read: D2,n4,oldest claimed4 instead of2 |1| decide evaluates false |
| False extra delay: same oldest claimed1 instead of2 |1| decide evaluates false |
| False append-old endpoint: newest claimed3 instead of4 |1| decide evaluates false |
| Explicit sorry proof of False |0| policy rejects marker/warning/sorryAx |
| Added-axiom proof of False |0| policy rejects extra axiom/footprint |
| Compiling true theorem with omitted axiom print |0| policy rejects coverage |

**The integrity payloads actually compile.** Rejection is by the additional policy,
not mislabeled compilation failure. False math fails for explicit finite Nat
witnesses, not missing modules/runtime. The fixed-source policy harness is not a
secure general Lean parser or arbitrary-code sandbox. All owned critical Python
gates avoid optimization-removable `assert` statements.

```json
{
  "compiler_version": "Lean (version 4.33.1, x86_64-unknown-linux-gnu, commit 819816b2e0a3bf405af45ae5c7af2491d8f5bee6, Release)",
  "imports": [
    "Std"
  ],
  "Mathlib_used": false,
  "main": {
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
  "named_declarations_compiled": 3,
  "formal_controls": 8,
  "positive_controls_accepted": 2,
  "false_math_witnesses_rejected_by_compiler": 3,
  "compiling_integrity_payloads_rejected_by_policy": 3,
  "controls": [
    {
      "control": "positive_nonzero",
      "kind": "positive",
      "expected_mechanism": null,
      "expected_outcome_observed": true,
      "policy": {
        "accepted": true,
        "reasons": [],
        "named_declarations": [
          "controlNonzero"
        ],
        "requested_axiom_prints": [
          "controlNonzero"
        ],
        "footprints": {
          "controlNonzero": []
        },
        "unapproved_axioms": {},
        "raw_compiler_returncode": 0
      },
      "setup_errors_credited": 0
    },
    {
      "control": "positive_abstract_D0",
      "kind": "positive",
      "expected_mechanism": null,
      "expected_outcome_observed": true,
      "policy": {
        "accepted": true,
        "reasons": [],
        "named_declarations": [
          "controlAbstractZero"
        ],
        "requested_axiom_prints": [
          "controlAbstractZero"
        ],
        "footprints": {
          "controlAbstractZero": []
        },
        "unapproved_axioms": {},
        "raw_compiler_returncode": 0
      },
      "setup_errors_credited": 0
    },
    {
      "control": "false_youngest_read",
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
      "control": "false_extra_delay",
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
      "control": "false_append_old",
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
  "scope": "Universal value-history trace only; no Python/float FFI or coupled dynamics proof; closed-file policy not an arbitrary-source sandbox"
}
```


### Explicit false-math compiler diagnostics

### false_youngest_read

```text
false_youngest_read.lean:4:71: error: Tactic `decide` proved that the proposition
  historyTrace 2 (fun n => n) 4 ⟨0, ⋯⟩ = 4
is false
```

### false_extra_delay

```text
false_extra_delay.lean:4:71: error: Tactic `decide` proved that the proposition
  historyTrace 2 (fun n => n) 4 ⟨0, ⋯⟩ = 1
is false
```

### false_append_old

```text
false_append_old.lean:4:71: error: Tactic `decide` proved that the proposition
  historyTrace 2 (fun n => n) 4 ⟨2, ⋯⟩ = 3
is false
```


## 8. Reproduce from this note alone

All ten owned critical files are inline below. Only Python with NumPy and a
compatible Linux core Lean runtime is required for science; no pandas/Mathlib or
real data are needed. The optional bootstrap needs internet plus pip/zstandard,
uses its own disposable cache, verifies the recorded public compiler asset and
does not set a global toolchain. Fetching acquires exactly three public dependencies:
engine, registry scope metadata and Lean toolchain metadata. Acquired source import
is reviewed-code execution, not a sandbox for arbitrary submissions.

1. Save the ten named fenced critical files, or save just the inline extractor
   first and run it against this Markdown.
2. Fetch the public inputs; install the prescribed core runtime only if no matching
   compiler is already available. The runtime/archive/decoder are not in this ZIP.
3. Run the complete runner, which repeats both interpreter suites, both11-model
   modes and all actual main/control compilations.

```sh
python -B extract_from_report.py 2026-09-04_researcher040282_010_history-phase-contract.md extracted
python -B extracted/fetch_public_dependencies.py --output upstream
python -B extracted/prepare_lean.py --receipt compiler_setup.json
LEAN="$HOME/.cache/researcher040282-cycle010/lean-4.33.1-linux/bin/lean"
PYTHONDONTWRITEBYTECODE=1 python -B extracted/run_checks.py \
  --source upstream --output checks --lean "$LEAN"
```

Use a separate --cache if that own cache already holds unrelated work. The source
manifest, bootstrap and actual setup receipt record the runtime. The author's
fresh-note reproduction reused the **same verified compiler**, not a second clean
compiler installation. Main source imports and tests were independently repeated
from the extracted files and newly fetched public dependencies. Timing text is not
a scientific equality target; science, workers and detailed deterministic records
are compared. Expected runner return0;9passes,78advances,11wrong-model detections
per mode;3 main declarations and8 formal controls.

**Actually executed:** ten critical files extracted byte-identically, three public dependencies freshly fetched/verified, same disposable compiler; complete runner repeated. Science/four non-timing workers and all25 detailed proof/source/log records match. Submitter-local reproduction only, not independent-seat review.

```json
{
  "actually_executed": true,
  "runner_returncode": 0,
  "tested_main": "eb3933c196ee19e80e1621ae80d89ca72e6d9485",
  "critical_file_count": 10,
  "critical_files": [
    "HistoryBuffer.lean",
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
  "fresh_public_dependencies_fetched_and_verified": 3,
  "fresh_public_python_sources": 1,
  "fresh_scope_compiler_metadata_files": 2,
  "same_original_verified_compiler_reused": true,
  "fresh_clean_compiler_installation_claimed": false,
  "scientific_summary_matches_original": true,
  "all_four_worker_nontiming_results_match_original": true,
  "all_twentyfive_detailed_records_byte_identical": true,
  "detailed_matching_files": [
    "common_normal/advance_observations.json",
    "common_normal/domain_checks.json",
    "common_optimized/advance_observations.json",
    "common_optimized/domain_checks.json",
    "proof/compiled_sources/HistoryBuffer.lean",
    "proof/compiled_sources/compiling_extra_axiom.lean",
    "proof/compiled_sources/compiling_sorry.lean",
    "proof/compiled_sources/false_append_old.lean",
    "proof/compiled_sources/false_extra_delay.lean",
    "proof/compiled_sources/false_youngest_read.lean",
    "proof/compiled_sources/omitted_axiom_print.lean",
    "proof/compiled_sources/positive_abstract_D0.lean",
    "proof/compiled_sources/positive_nonzero.lean",
    "proof/compiler_logs/HistoryBuffer.log",
    "proof/compiler_logs/compiling_extra_axiom.log",
    "proof/compiler_logs/compiling_sorry.log",
    "proof/compiler_logs/false_append_old.log",
    "proof/compiler_logs/false_extra_delay.log",
    "proof/compiler_logs/false_youngest_read.log",
    "proof/compiler_logs/omitted_axiom_print.log",
    "proof/compiler_logs/positive_abstract_D0.log",
    "proof/compiler_logs/positive_nonzero.log",
    "proof/result.json",
    "wrong_models_normal/wrong_models.json",
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
    78,
    78
  ],
  "source_initializations_each_common_mode": [
    1,
    1
  ],
  "dyadic_exact_states_each_mode": [
    65,
    65
  ],
  "dyadic_exact_stored_coordinates_each_mode": [
    260,
    260
  ],
  "wrong_models_detected_each_mode": [
    11,
    11
  ],
  "invalid_delay_config_rejections_separate_each_mode": [
    2,
    2
  ],
  "named_Lean_declarations_compiled": 3,
  "formal_controls_repeated": 8,
  "original_elapsed_seconds": 10.67612152400011,
  "extracted_elapsed_seconds": 8.73614141600001,
  "command": "python -B standalone/extracted/run_checks.py --source standalone/upstream --output standalone/checks --lean <same verified compiler>",
  "result": "cycle_010/standalone/checks/cycle_results.json",
  "log": "cycle_010/standalone/reproduction.log",
  "scope": "Submitter-local exact-note repetition, not independent review or formal Python/float/coupled-map equivalence; no real study, authority/baseline certificate, frozen edit or installation"
}
```


### Own disposable compiler cleanup

Cleanup occurs only after successful full reproduction, removes only the
cycle010-owned compiler/archive/decoder target, not other caches or research.
The already deleted old Lua audit remains absent and is not restored.

```json
{
  "actually_removed_after_successful_full_reproduction": true,
  "own_cache": "/home/user/.cache/researcher040282-cycle010",
  "regular_files_removed": 7492,
  "symlinks_removed": null,
  "regular_file_logical_bytes_removed": 2718508891,
  "regular_file_allocated_bytes_removed": 2733250560,
  "cache_absent_after_removal": true,
  "only_cycle010_owned_compiler_archive_decoder_target_removed": true,
  "other_research_and_cache_directories_not_deleted": true,
  "Mathlib_or_global_toolchain_installation": false,
  "legacy_lua_audit_remains_absent": true,
  "science_proofs_sources_logs_receipts_preserved": true,
  "symlink_count_note": "Not measured before deletion; the initial receipt inspected saved paths after deletion, so its reported zero is not reliable and is not used."
}
```


## 9. Review request and explicit non-results

Researcher001: independently check the recurrence proof, constant-startup/lag
interpretation and the source-to-value-buffer assumptions before considering a
new unregistered library module. AuditorSeat002: independently inspect/run the
scalar oracle, actual call inventory, storage tests and compiler/policy controls.
Prior94-compilation/minimal-mechanism review does not approve these new three
declarations, source correspondence or controls. Earlier005–009 proposals remain
under their prior separate review/integration boundaries.

- No universal float64/Python/NumPy or whole coupled-map theorem; no proof of
  exponentials, sine, modulo implementation, all schedules/platforms/dtypes or
  Python memory semantics. Exact Lean history indexing is the formal claim.
- No history-lag conclusion merely from state.validate; no source-valid D0.
  Non-dyadic one-step histories are synthetic states, not certified coupled
  trajectories from a real initialization. The N1 traces exercise recurrence.
- No full baseline-equivalence campaign, real S01 positive, saved-array census,
  shuffle/intervention, scientific ON/OFF/locking result, certificate or authority
  issuance. No engine/frozen/registry/lock change or installation.
- No independent review, private-work novelty guarantee, security certification,
  remote branch/PR/contact/upload, direct inbox merge or unattended011.

Live ledger at final assembly: **118 unique rows / 97 LEAN_COMPILED labels**. Prior114 rows and their94 formal
labels are preserved exactly; only the three precisely scoped new compiled claims
and one finite executable-contract row are eligible after actual reproduction.
All historical scientific reports/code/archives/logs and the completed009 state/
ledger snapshot remain intact. One missing9175-byte historical006 CI source file
was restored **missing-only, byte-for-byte from delivered009 ZIP**; no existing
file overwritten or historical science rerun. This is administrative evidence
recovery, not a new finding/repair. The deleted Lua audit is not restored.
Historical cited logs are unpacked/indexed; minimal acquisition metadata omits
personal commit contacts and signed payloads.

**Next bounded candidate, not executed:** fresh-check a modulo-safe phase-
increment/delayed-input bridge using the established buffer indices and actual
new gated-B phase map. Separate constant startup from live delayed history and
select one noncircular useful statement before any new run. This is not a promise
of coupled convergence or an unattended next cycle. Owner controls upload/review.

## Appendix A. All ten critical files, complete

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
"""Nine common actual-engine methods and eleven independent wrong models.
Only immutable synthetic primitive inputs; no production simulation entry point.
All checks survive -O. AssertionError subclass only for semantic mismatches;
import/validation/runtime/setup errors are never credited control detections.
"""
import argparse
from dataclasses import asdict,replace
import io
import json
import math
from pathlib import Path
from types import SimpleNamespace
import unittest

import numpy as np
from load_reviewed import load,verify
from step_contract import (ABS_TOL,MIN_CONTROL_WITNESS,base_case,cases,control_cases,
                           drift_case,reference,shadow_after)


class ContractMismatch(AssertionError):
    def __init__(self,field,expected,observed,delta=None):
        self.field=field;self.expected=expected;self.observed=observed;self.delta=delta
        super().__init__(f'{field}: expected {expected}; observed {observed}; component difference {delta}')


def require(condition,message):
    if not condition:raise RuntimeError(message)


def save(path,value):path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')


def field_arrays(prediction):
    return {'C':prediction.C,'R_physical':prediction.R,'R_driver':prediction.R,
            'B':prediction.B,'theta':prediction.theta,'history':prediction.history}


def actual_arrays(state,physical,driver):
    return {'C':state.coherence_acc,'R_physical':physical,'R_driver':driver,
            'B':state.B,'theta':state.theta,'history':state.history}


def component_error(expected,observed,field):
    want=np.asarray(expected);got=np.asarray(observed)
    if want.shape!=got.shape:raise ContractMismatch(field+'.shape',list(want.shape),list(got.shape))
    if not np.all(np.isfinite(want)) or not np.all(np.isfinite(got)):
        raise ContractMismatch(field+'.finite',True,False)
    # Real/imag components each compared, never a NaN-masking whole-element max.
    if np.iscomplexobj(want) or np.iscomplexobj(got):
        return max(float(np.max(np.abs(got.real-want.real),initial=0.0)),
                   float(np.max(np.abs(got.imag-want.imag),initial=0.0)))
    return float(np.max(np.abs(got-want),initial=0.0))


def storage_ownership(state):
    for i,h in enumerate(state.history):
        if np.shares_memory(h,state.theta):raise ContractMismatch('storage_ownership','independent history/theta','shared theta/history '+str(i))
        for j in range(i):
            if np.shares_memory(h,state.history[j]):raise ContractMismatch('storage_ownership','independent history vectors',f'shared history {j}/{i}')


def compare(prediction,state,physical,driver,info):
    errors={}
    for field,want in field_arrays(prediction).items():
        error=component_error(want,actual_arrays(state,physical,driver)[field],field);errors[field]=error
        if error>ABS_TOL:raise ContractMismatch(field,'absolute error <= '+str(ABS_TOL),error,error)
    for field in ('pre_violation','projection_active'):
        observed=info[field]
        if type(observed) is not bool or observed!=getattr(prediction,field):
            raise ContractMismatch(field,getattr(prediction,field),observed)
    for field in ('g_min_pre','g_min'):
        error=component_error(getattr(prediction,field),info[field],field);errors[field]=error
        if error>ABS_TOL:raise ContractMismatch(field,getattr(prediction,field),info[field],error)
    theta=np.asarray(state.theta)
    if np.any(theta<0.0) or np.any(theta>=math.tau):raise ContractMismatch('phase_range','[0,2*pi)',theta.tolist())
    B=np.asarray(state.B)
    if not np.array_equal(B,B.T) or np.any(np.diag(B)!=0.0) or np.any(B<0.0):
        raise ContractMismatch('B_structure','symmetric/zero diagonal/nonnegative',B.tolist())
    storage_ownership(state)
    return errors


def materialize(prediction,alias=False):
    theta=np.array(prediction.theta,dtype=float)
    state=SimpleNamespace(theta=theta,B=np.array(prediction.B,dtype=float),
                          coherence_acc=np.array(prediction.C,dtype=complex),
                          history=[np.array(h,dtype=float) for h in prediction.history])
    if alias:state.history[-1]=theta
    info={key:getattr(prediction,key) for key in ('pre_violation','projection_active','g_min_pre','g_min')}
    return state,np.array(prediction.R),np.array(prediction.R),info


class Context:
    def __init__(self,module):
        self.module=module;self.records=[];self.calls=0;self.initializations=0
        self.domain_records=[];self.trace_states=0;self.trace_coordinates=0
        self.oldest_pair=None;self.interior_pair=None
    def config(self,case):
        cfg=self.module.ModelConfig(**asdict(case.p));cfg.validate();return cfg
    def state(self,case):
        return self.module.DynamicState(np.array(case.theta),np.array(case.B),np.array(case.C),
                                        [np.array(h) for h in case.history])
    def checked(self,case,label,state=None):
        frozen_before=repr(case)
        # The reference is evaluated BEFORE target advance, including state reuse.
        prediction=reference(case);cfg=self.config(case)
        if state is None:state=self.state(case)
        state.validate(cfg)
        rng=np.random.default_rng(1040282);rng_before=json.dumps(rng.bit_generator.state,sort_keys=True)
        self.calls+=1
        physical,driver,info=self.module.advance_state(state,cfg,rng,shuffle_driver=False)
        state.validate(cfg)
        if rng_before!=json.dumps(rng.bit_generator.state,sort_keys=True):
            raise ContractMismatch('rng_preservation','unchanged for non-shuffle','changed')
        errors=compare(prediction,state,physical,driver,info)
        if frozen_before!=repr(case):raise ContractMismatch('immutable_case_preservation','unchanged','changed')
        self.records.append({'label':label,'case':case.name,'N':case.p.N,'D':round(case.p.tau/case.p.dt),
                             'component_errors':errors,'maximum_component_error':max(errors.values()),
                             'flags':{k:info[k] for k in ('pre_violation','projection_active')},
                             'theta':state.theta.tolist(),'g_min_pre':float(info['g_min_pre']),'g_min':float(info['g_min']),
                             'input_case_unchanged':True,'rng_unchanged':True,'independent_history_storage':True})
        return prediction,state,(physical,driver,info)


def suite(context):
    class EngineContract(unittest.TestCase):
        def test_01_nine_scalar_steps(self):
            for case in cases():
                with self.subTest(case=case.name):context.checked(case,'one_step/'+case.name)
        def test_02_oldest_is_immediate_input(self):
            first=base_case('oldest_pair_base',2,True)
            changed=replace(first,name='oldest_pair_changed',history=((0.19,4.77,5.38),)+first.history[1:])
            a,_,_=context.checked(first,'oldest/base');b,_,_=context.checked(changed,'oldest/changed')
            cdelta=component_error(a.C,b.C,'C');tdelta=component_error(a.theta,b.theta,'theta')
            require(cdelta>MIN_CONTROL_WITNESS and tdelta>MIN_CONTROL_WITNESS,'Oldest-read probe is vacuous')
            context.oldest_pair={'C_change':cdelta,'theta_change':tdelta}
        def test_03_interior_is_latent_not_discarded(self):
            first=base_case('interior_pair_base',2,True)
            changed=replace(first,name='interior_pair_changed',history=(first.history[0],(0.22,3.44,5.55),first.history[2]))
            a,_,_=context.checked(first,'interior/base');b,_,_=context.checked(changed,'interior/changed')
            immediate={field:component_error(getattr(a,field),getattr(b,field),field) for field in ('C','R','B','theta')}
            latent=component_error(a.history,b.history,'history')
            require(all(value==0.0 for value in immediate.values()) and latent>MIN_CONTROL_WITNESS,'Interior age probe failed')
            context.interior_pair={'instantaneous_changes':immediate,'shifted_history_change':latent}
        def test_04_reachable_dyadic_histories(self):
            for d in range(1,6):
                shadow=drift_case(d);state=context.state(shadow)
                for n in range(13):
                    want=np.array([[0.25+max(0,n+i-d)*0.125] for i in range(d+1)])
                    if not np.array_equal(np.array(state.history),want):
                        raise ContractMismatch('exact_history_trace',want.tolist(),np.array(state.history).tolist())
                    if not np.array_equal(state.theta,np.array([0.25+n*0.125])):
                        raise ContractMismatch('exact_current_trace',[0.25+n*0.125],state.theta.tolist())
                    storage_ownership(state);context.trace_states+=1;context.trace_coordinates+=d+1
                    if n<12:
                        prediction,state,_=context.checked(shadow,f'dyadic/D{d}/step{n+1}',state=state)
                        # Next expected state comes from independent spec, not observed target.
                        shadow=shadow_after(shadow,prediction)
        def test_05_phase_uses_new_gated_B(self):
            case=base_case('new_gated_B',2,True);prediction,_,_=context.checked(case,'phase/new_gated_B')
            require(prediction.pre_violation and prediction.projection_active,'Active phase probe never gates')
            for wrong in ('old_B_for_phase','unprojected_B_for_phase'):
                require(component_error(prediction.theta,reference(case,wrong).theta,'theta')>MIN_CONTROL_WITNESS,'Vacuous phase order control')
        def test_06_updated_directed_C_then_magnitude(self):
            case=base_case('updated_directed_C',2,True);prediction,_,_=context.checked(case,'C/updated_then_magnitude')
            for wrong in ('old_C_for_R','symmetrize_C_first'):
                require(component_error(prediction.R,reference(case,wrong).R,'R')>MIN_CONTROL_WITNESS,'Vacuous C order control')
        def test_07_wrap_clipping_and_ranges(self):
            case=cases()[6];prediction,_,_=context.checked(case,'clipping/negative_raw')
            require(prediction.minimum_raw_offdiagonal_proposal<0 and all(v==0 for row in prediction.B for v in row),'Clipping probe is vacuous')
            wrap=next(row for row in context.records if row['label']=='one_step/phase_wrap_D1')
            require(wrap['theta'][0]<1.0 and wrap['theta'][2]<1.0,'Wrap probe did not cross modulo boundary')
            require(all(0<=v<math.tau for row in context.records for v in row['theta']),'Range probe failed')
        def test_08_initializer_and_copy_ownership(self):
            case=base_case('copy_probe',2,True);cfg=context.config(case)
            initialized=context.module.initialize_state(1040282,cfg);context.initializations+=1;initialized.validate(cfg)
            require(len(initialized.history)==3 and all(np.array_equal(h,initialized.theta) for h in initialized.history),'Constant prehistory initializer correspondence failed')
            storage_ownership(initialized)
            _,state,_=context.checked(case,'ownership/current_mutation')
            saved=[h.copy() for h in state.history];state.theta[0]+=0.5
            require(all(np.array_equal(a,b) for a,b in zip(saved,state.history)),'Current phase mutation leaked into history')
            _,state,_=context.checked(base_case('copy_probe_D3',3,True),'ownership/history_mutation')
            theta=state.theta.copy();others=[h.copy() for h in state.history[:-1]];state.history[-1][0]+=0.5
            require(np.array_equal(state.theta,theta) and all(np.array_equal(a,b) for a,b in zip(others,state.history[:-1])),'History mutation leaked to current/other history')
        def test_09_exact_delay_validation_domain(self):
            for case in cases():
                cfg=context.config(case)
                require(cfg.delay_steps>=1 and cfg.delay_steps*cfg.dt==cfg.tau,'Invalid planned source domain')
            for tau in (0.2,0.1875):
                p=replace(base_case().p,tau=tau);cfg=context.module.ModelConfig(**asdict(p))
                try:cfg.validate()
                except ValueError as error:
                    require('must equal tau' in str(error),'Domain rejected for unintended reason')
                    context.domain_records.append({'tau':tau,'dt':p.dt,'rejected_for_exact_delay':True,'semantic_negative_detection_credited':False})
                else:raise ContractMismatch('exact_delay_validation','ValueError',None)
    return unittest.defaultTestLoader.loadTestsFromTestCase(EngineContract)


def wrong_models():
    records=[]
    for name,case,intended in control_cases():
        expected=reference(case)
        wrong=reference(case,None if name=='alias_new_theta' else name)
        state,physical,driver,info=materialize(wrong,alias=name=='alias_new_theta')
        try:compare(expected,state,physical,driver,info)
        except ContractMismatch as error:
            require(error.field==intended,'Wrong detection mechanism: '+name+'/'+error.field)
            if intended!='storage_ownership':require(error.delta is not None and error.delta>MIN_CONTROL_WITNESS,'Control witness too small')
            records.append({'model':name,'detected':True,'intended_field':intended,'detected_field':error.field,
                            'maximum_component_difference':error.delta,'minimum_numeric_witness_required':None if intended=='storage_ownership' else MIN_CONTROL_WITNESS,
                            'setup_errors_credited':0})
        else:raise RuntimeError('Undetected wrong model: '+name)
    require(len(records)==11 and len({r['model'] for r in records})==11,'Wrong-model inventory incomplete')
    return records


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--kind',choices=('common','wrong_models'),required=True)
    args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    try:
        if args.kind=='wrong_models':
            # Source verification, but NO engine calls necessary for independent falsifiers.
            manifest=verify(args.source);records=wrong_models()
            value={'kind':'wrong_models','optimized_python':not __debug__,'detected':len(records),'records':records,
                   'actual_engine_advances':0,'setup_errors_credited':0,'source_files_unchanged':len(manifest['modules']),
                   'metadata_files_unchanged':len(manifest['metadata'])}
            save(args.output/'wrong_models.json',records);save(args.output/'result.json',value);print(json.dumps(value,indent=2));return 0
        module=load(args.source);context=Context(module);stream=io.StringIO()
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite(context));print(stream.getvalue(),end='')
        save(args.output/'advance_observations.json',context.records);save(args.output/'domain_checks.json',context.domain_records)
        value={'kind':'common','optimized_python':not __debug__,'tests_run':result.testsRun,'failures':len(result.failures),
               'errors':len(result.errors),'skipped':len(result.skipped),'actual_engine_advances':context.calls,
               'source_initializations':context.initializations,'reference_compared_transitions':len(context.records),
               'maximum_component_error':max((r['maximum_component_error'] for r in context.records),default=0.0),
               'oldest_pair':context.oldest_pair,'interior_pair':context.interior_pair,
               'dyadic_exact_states':context.trace_states,'dyadic_exact_stored_coordinates':context.trace_coordinates,
               'invalid_exact_delay_configs_rejected_not_semantic_detections':len(context.domain_records),
               'absolute_tolerance':ABS_TOL,'relative_tolerance':0.0,'immutable_cases_rng_and_history_ownership_verified':True,
               'source_files_unchanged':len(verify(args.source)['modules']),'metadata_files_unchanged':len(verify(args.source)['metadata']),
               'actual_full_engine_import_no_source_function_copy_replacement_or_edit':True,
               'production_simulation_baseline_CLI_or_certificate_called':False}
        save(args.output/'result.json',value);print(json.dumps(value,indent=2));return 0 if result.wasSuccessful() else 1
    except Exception as error:
        save(args.output/'failure.json',{'type':type(error).__name__,'message':str(error),'semantic_negative_detection_credited':False});raise


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
    source=Path(source).resolve();manifest=verify(source);name='r040282_010_unchanged_engine'
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
"""Compile the owned Std-only history module and eight closed-file controls.
Checks survive Python -O. Compiler/import/timeouts are blockers, not falsifiers.
This is a reproducibility/integrity harness for these fixed sources, NOT a secure
parser/sandbox for arbitrary Lean submissions or untrusted compiler plugins.
"""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

HERE=Path(__file__).resolve().parent
ALLOWED={'propext','Classical.choice','Quot.sound'}
NAMES={'Researcher040282.Delay.historyTrace_index','Researcher040282.Delay.historyTrace_oldest',
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


def controls():
    header='import HistoryBuffer\nopen Researcher040282.Delay\n\n'
    nonzero=header+'''theorem controlNonzero : historyTrace 2 (fun n : Nat => n) 4 ⟨0, by decide⟩ = 2 := by decide
#print axioms controlNonzero
'''
    zero=header+'''theorem controlAbstractZero : historyTrace 0 (fun n : Nat => 2*n+3) 7 ⟨0, by decide⟩ = 17 := by decide
#print axioms controlAbstractZero
'''
    youngest=header+'''example : historyTrace 2 (fun n : Nat => n) 4 ⟨0, by decide⟩ = 4 := by decide
'''
    extra=header+'''example : historyTrace 2 (fun n : Nat => n) 4 ⟨0, by decide⟩ = 1 := by decide
'''
    append_old=header+'''example : historyTrace 2 (fun n : Nat => n) 4 ⟨2, by decide⟩ = 3 := by decide
'''
    sorry=header+'''theorem controlSorry : False := by sorry
#print axioms controlSorry
'''
    axiom=header+'''axiom injectedFalse : False
theorem controlExtraAxiom : False := injectedFalse
#print axioms controlExtraAxiom
'''
    omitted=header+'''theorem controlNoPrint : True := by trivial
'''
    return (('positive_nonzero','positive',nonzero,None),('positive_abstract_D0','positive',zero,None),
            ('false_youngest_read','false_math',youngest,None),('false_extra_delay','false_math',extra,None),
            ('false_append_old','false_math',append_old,None),('compiling_sorry','integrity',sorry,'forbidden_source:sorry'),
            ('compiling_extra_axiom','integrity',axiom,'unapproved_axiom_footprint'),
            ('omitted_axiom_print','integrity',omitted,'axiom_print_coverage'))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--lean',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    try:
        compiler=args.lean.resolve();require(compiler.is_file(),'Core compiler missing: setup blocker')
        version=subprocess.check_output([str(compiler),'--version'],text=True,timeout=20).strip()
        manifest=json.loads((HERE/'source_modules.json').read_text())
        require('version '+manifest['lean_toolchain']['toolchain'].rsplit(':v',1)[1]+',' in version,'Wrong compiler: setup blocker')
        sources=args.output/'compiled_sources';sources.mkdir(exist_ok=True);logs=args.output/'compiler_logs';logs.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='r040282-010-lean-') as temporary:
            work=Path(temporary);env=dict(os.environ,LEAN_PATH=str(work))
            def compile_one(name,text,produce_object=False):
                filename=name+'.lean';(work/filename).write_text(text);(sources/filename).write_text(text)
                command=[str(compiler),'--root='+str(work)]+(['-o',str(work/'HistoryBuffer.olean')] if produce_object else [])+[filename]
                run=subprocess.run(command,cwd=work,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60)
                (logs/(name+'.log')).write_text(run.stdout)
                if re.search(r'unknown module|object file .* does not exist|failed to import|cannot open shared object|unknown namespace',run.stdout,re.I):
                    raise RuntimeError('Import/runtime blocker, never a successful control: '+name)
                return run,assess(text,run.stdout,run.returncode)
            main_run,main_policy=compile_one('HistoryBuffer',(HERE/'HistoryBuffer.lean').read_text(),True)
            require(main_policy['accepted'] and set(main_policy['footprints'])==NAMES and len(main_policy['named_declarations'])==3,
                    'Main theorem compilation/footprint acceptance failed: '+json.dumps(main_policy))
            records=[]
            for name,kind,text,intended in controls():
                run,policy=compile_one(name,text)
                if kind=='positive':require(run.returncode==0 and policy['accepted'],'Positive control rejected: '+name)
                elif kind=='false_math':
                    require(run.returncode!=0 and not policy['accepted'] and
                            re.search(r"decide.*(?:false|failed)|proposition.*false",run.stdout,re.I|re.S),
                            'False theorem did not fail for explicit mathematical witness: '+name)
                else:
                    require(run.returncode==0 and not policy['accepted'] and intended in policy['reasons'],
                            'Compiling integrity payload not rejected for intended policy: '+name)
                records.append({'control':name,'kind':kind,'expected_mechanism':intended,
                                'expected_outcome_observed':True,'policy':policy,'setup_errors_credited':0})
        require(len(records)==8,'Formal control inventory incomplete')
        value={'compiler_version':version,'imports':['Std'],'Mathlib_used':False,'main':main_policy,
               'named_declarations_compiled':3,'formal_controls':8,'positive_controls_accepted':2,
               'false_math_witnesses_rejected_by_compiler':3,'compiling_integrity_payloads_rejected_by_policy':3,
               'controls':records,'setup_errors_credited':0,'all_preregistered_formal_conditions_met':True,
               'scope':'Universal value-history trace only; no Python/float FFI or coupled dynamics proof; closed-file policy not an arbitrary-source sandbox'}
        save(args.output/'result.json',value);print(json.dumps(value,indent=2));return 0
    except Exception as error:
        save(args.output/'failure.json',{'type':type(error).__name__,'message':str(error),'semantic_negative_detection_credited':False});raise


if __name__=='__main__':raise SystemExit(main())
```
<!-- END_CRITICAL_FILE: check_lean.py -->

### prepare_lean.py

<!-- BEGIN_CRITICAL_FILE: prepare_lean.py -->
```python
"""Disposable prescribed CORE Lean runtime; no Mathlib/global toolchain change.
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
DEFAULT=Path.home()/'.cache/researcher040282-cycle010'


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
        print('Downloading disposable prescribed core compiler asset:',record['bytes'],'bytes',flush=True)
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
                            '--no-deps','--target',str(decoder),'zstandard==0.25.0'],check=True,timeout=90)
        sys.path.insert(0,str(decoder));zstandard=importlib.import_module('zstandard');decoder_installed=True
    files=0;bytes_written=0
    print('Extracting compiler/shared runtime/core Std objects only; no Mathlib.',flush=True)
    with archive.open('rb') as source,zstandard.ZstdDecompressor().stream_reader(source) as decoded:
        with tarfile.open(fileobj=decoded,mode='r|') as tar:
            for member in tar:
                path=Path(member.name)
                require(not path.is_absolute() and '..' not in path.parts,'Unsafe release member path')
                if path.parts[0]!=install.name:raise RuntimeError('Unexpected compiler release root')
                wanted=(member.name==install.name+'/bin/lean' or
                        ('lib' in path.parts and ('.so' in path.name or '.olean' in path.name)) or
                        path.name in ('LICENSE','LICENSES'))
                if wanted:
                    tar.extract(member,cache,filter='data');files+=1;bytes_written+=member.size
    require(binary.is_file(),'Compiler extraction incomplete')
    version=subprocess.check_output([str(binary),'--version'],text=True).strip()
    expected=record['toolchain'].rsplit(':v',1)[1]
    require('version '+expected+',' in version,'Wrong prescribed compiler')
    receipt={'toolchain':record['toolchain'],'compiler_version':version,'public_asset_verified':True,
             'download_bytes':record['bytes'],'selectively_extracted_members':files,'selectively_extracted_bytes':bytes_written,
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
"""010 complete bounded history/one-step contract plus actual core Lean checks.
No production study, full baseline-equivalence, CLI, intervention or certificate.
Run after separately bootstrapping prescribed disposable compiler, or supply one.
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
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);parser.add_argument('--lean',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True);start=time.perf_counter()
    try:
        manifest=verify(args.source)
        require((args.source/'lean/AIEFProofs/lean-toolchain').read_text().strip()==manifest['lean_toolchain']['toolchain'],
                'Source compiler prescription changed')
        require(args.lean.is_file(),'Compiler missing: setup blocker, never scientific control detection')
        env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONOPTIMIZE',None);workers=[]
        for kind in ('common','wrong_models'):
            for optimized in (False,True):
                name=kind+('_optimized' if optimized else '_normal');directory=args.output/name
                command=[sys.executable]+(['-O'] if optimized else [])+['-B',str(HERE/'check_engine.py'),
                          '--kind',kind,'--source',str(args.source.resolve()),'--output',str(directory.resolve())]
                worker_start=time.perf_counter()
                run=subprocess.run(command,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=env,timeout=60)
                (args.output/(name+'.log')).write_text(run.stdout)
                require((directory/'result.json').is_file(),'Worker failed before result (not a falsifier): '+name)
                value=json.loads((directory/'result.json').read_text())
                require(run.returncode==0 and value['optimized_python'] is optimized and value['source_files_unchanged']==1 and value['metadata_files_unchanged']==2,
                        'Actual engine/control worker failed or source changed: '+name)
                if kind=='common':
                    require(value['tests_run']==9 and value['failures']==value['errors']==value['skipped']==0 and
                            value['actual_engine_advances']==value['reference_compared_transitions']==78 and value['source_initializations']==1 and
                            value['dyadic_exact_states']==65 and value['dyadic_exact_stored_coordinates']==260 and
                            value['invalid_exact_delay_configs_rejected_not_semantic_detections']==2 and
                            value['maximum_component_error']<=5e-13 and value['absolute_tolerance']==5e-13 and value['relative_tolerance']==0,
                            'Common suite not equal to preregistered inventory: '+name)
                else:require(value['detected']==11 and value['setup_errors_credited']==0 and value['actual_engine_advances']==0,
                             'Wrong-model inventory incomplete: '+name)
                value['observed_returncode']=run.returncode;value['elapsed_seconds']=time.perf_counter()-worker_start
                workers.append(value);print(name,'return',run.returncode,'preregistered outcomes verified',flush=True)
        for kind in ('common','wrong_models'):
            values=[{k:v for k,v in row.items() if k not in ('elapsed_seconds','optimized_python')} for row in workers if row['kind']==kind]
            require(values[0]==values[1],'Normal/-O non-timing records differ: '+kind)
        save(args.output/'worker_results.json',workers)
        proof_start=time.perf_counter()
        run=subprocess.run([sys.executable,'-B',str(HERE/'check_lean.py'),'--lean',str(args.lean.resolve()),
                            '--output',str((args.output/'proof').resolve())],env=env,text=True,stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT,timeout=180)
        (args.output/'proof.log').write_text(run.stdout)
        require(run.returncode==0 and (args.output/'proof/result.json').is_file(),'Formal run blocked/failed; not a falsifier')
        proof=json.loads((args.output/'proof/result.json').read_text())
        require(proof['all_preregistered_formal_conditions_met'] and proof['named_declarations_compiled']==3 and
                proof['formal_controls']==8 and proof['setup_errors_credited']==0,'Formal acceptance incomplete')
        common=next(row for row in workers if row['kind']=='common')
        science={'tested_main':manifest['commit'],'source_contract_methods_each_mode':9,'source_passes_each_mode':9,
                 'source_failures_errors_skips_each_mode':[0,0,0],'actual_advances_each_common_mode':78,
                 'initializer_calls_each_common_mode':1,'nine_one_step_cases_each_mode':9,
                 'dyadic_transitions_each_mode':60,'dyadic_exact_states_each_mode':65,'dyadic_exact_stored_coordinates_each_mode':260,
                 'maximum_observed_component_error':common['maximum_component_error'],
                 'absolute_tolerance':5e-13,'relative_tolerance':0.0,'wrong_models_detected_each_mode':11,
                 'invalid_exact_delay_configs_rejected_each_mode_not_semantic_detections':2,
                 'setup_errors_credited_as_detections':0,'normal_optimized_nontiming_results_match':True,
                 'new_named_Lean_declarations_actually_compiled':3,'formal_controls':8,'formal_positive_controls':2,
                 'formal_false_math_controls':3,'formal_compiling_integrity_controls':3,
                 'axiom_footprints':proof['main']['footprints'],'core_Std_only_no_Mathlib':True,
                 'reviewed_public_engine_unchanged':1,'reviewed_metadata_unchanged':2,
                 'actual_engine_import_no_copied_replaced_or_edited_source_functions':True,
                 'no_source_repair_or_failing_before_claim':True,'all_preregistered_acceptance_conditions_met':True}
        record={'science':science,'environment':{'python':sys.version,'numpy':np.__version__,'compiler':proof['compiler_version']},
                'elapsed_seconds':time.perf_counter()-start,'formal_elapsed_seconds':time.perf_counter()-proof_start,
                'scope':'Generic reachable value-buffer theorem + finite non-shuffled scalar-reference primitive agreement. NOT a Lean proof of Python, floating trigonometry, whole coupled map, full baseline-equivalence, production study, stability/locking, certificate, installation or independent approval.'}
        verify(args.source);save(args.output/'cycle_results.json',record);print(json.dumps(record,indent=2));return 0
    except Exception as error:
        save(args.output/'failure.json',{'type':type(error).__name__,'message':str(error),'semantic_negative_detection_credited':False});raise


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
    }
  ],
  "lean_toolchain": {
    "toolchain": "leanprover/lean4:v4.33.1",
    "asset_name": "lean-4.33.1-linux.tar.zst",
    "url": "https://github.com/leanprover/lean4/releases/download/v4.33.1/lean-4.33.1-linux.tar.zst",
    "bytes": 570405234,
    "published_digest": "sha256:890afd185370f85666025b883914ab4f4b339136f8c96167b69cfb62aecaf235",
    "scope": "Disposable core compiler/runtime only, no Mathlib; no raw uploader/contact/signature metadata retained"
  }
}
```
<!-- END_CRITICAL_FILE: source_modules.json -->

### fetch_public_dependencies.py

<!-- BEGIN_CRITICAL_FILE: fetch_public_dependencies.py -->
```python
"""Fetch one reviewed public engine and two scope/compiler metadata files.
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
        if relative.is_absolute() or '..' in relative.parts or not (relative.suffix in {'.py','.csv'} or relative.name=='lean-toolchain'):
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
    with ThreadPoolExecutor(max_workers=3) as pool:files=list(pool.map(fetch,manifest['modules']+manifest['metadata']))
    print(json.dumps({'tested_main':manifest['commit'],'public_dependencies_fetched_and_verified':len(files),
                      'python_sources':len(manifest['modules']),'metadata_files':len(manifest['metadata']),
                      'files':files,'source_executed_by_fetcher':False,'raw_commit_author_metadata_requested':False},indent=2))


if __name__=='__main__':main()
```
<!-- END_CRITICAL_FILE: fetch_public_dependencies.py -->

### extract_from_report.py

<!-- BEGIN_CRITICAL_FILE: extract_from_report.py -->
```python
"""Extract the ten named critical010 files. No execution or fetching."""
import argparse
import json
from pathlib import Path
import re

NAMES={'HistoryBuffer.lean','step_contract.py','check_engine.py','load_reviewed.py','check_lean.py',
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


## Appendix B. Independent pre-engine case design

This design record predates acquired-engine import/advance. It is scalar-formula
evidence and fixed-witness design, not observations from the engine.

```json
{
  "phase": "Before acquired-engine import/advance; independent scalar design only",
  "reference": "math/cmath, no NumPy or acquired code",
  "cases": [
    {
      "case": "inactive_D1",
      "N": 3,
      "D": 1,
      "pre_violation": false,
      "projection_active": false,
      "g_min_pre": 0.1678136633694446,
      "g_min": 0.1678136633694446,
      "theta": [
        0.4041391349938893,
        1.4186776812987445,
        4.352839341505965
      ],
      "minimum_raw_offdiagonal_proposal": 0.07860569078800575
    },
    {
      "case": "active_D2",
      "N": 3,
      "D": 2,
      "pre_violation": true,
      "projection_active": true,
      "g_min_pre": -0.34573756948342016,
      "g_min": 0.10000000000100329,
      "theta": [
        0.4097551287319256,
        1.4139502387955527,
        4.355478572179514
      ],
      "minimum_raw_offdiagonal_proposal": 0.1614783978454979
    },
    {
      "case": "active_D3",
      "N": 3,
      "D": 3,
      "pre_violation": true,
      "projection_active": true,
      "g_min_pre": -0.33558979083295637,
      "g_min": 0.10000000000101072,
      "theta": [
        0.4105305960280428,
        1.4128158378483457,
        4.355820100609233
      ],
      "minimum_raw_offdiagonal_proposal": 0.1681059894783784
    },
    {
      "case": "zero_C_new_drive_D2",
      "N": 3,
      "D": 2,
      "pre_violation": false,
      "projection_active": false,
      "g_min_pre": 0.1936375734129442,
      "g_min": 0.1936375734129442,
      "theta": [
        0.40353383725854497,
        1.4174317932252485,
        4.351936807681926
      ],
      "minimum_raw_offdiagonal_proposal": 0.0786624755290186
    },
    {
      "case": "phase_wrap_D1",
      "N": 3,
      "D": 1,
      "pre_violation": false,
      "projection_active": false,
      "g_min_pre": 0.1739973340965404,
      "g_min": 0.1739973340965404,
      "theta": [
        0.07764709118065216,
        0.16356392254644053,
        0.19322079144840476
      ],
      "minimum_raw_offdiagonal_proposal": 0.08289357442643124
    },
    {
      "case": "exact_capacity_N2",
      "N": 2,
      "D": 1,
      "pre_violation": false,
      "projection_active": false,
      "g_min_pre": 0.5,
      "g_min": 0.5,
      "theta": [
        0.4024640961627627,
        1.3326636836438692
      ],
      "minimum_raw_offdiagonal_proposal": 0.5
    },
    {
      "case": "negative_proposal_clipped",
      "N": 3,
      "D": 2,
      "pre_violation": false,
      "projection_active": false,
      "g_min_pre": 1.0,
      "g_min": 1.0,
      "theta": [
        0.3725,
        1.395,
        4.3175
      ],
      "minimum_raw_offdiagonal_proposal": -0.778800783071405
    },
    {
      "case": "directed_C_N4_D4",
      "N": 4,
      "D": 4,
      "pre_violation": true,
      "projection_active": true,
      "g_min_pre": -0.4503795906193895,
      "g_min": 0.10000000000093079,
      "theta": [
        0.3807843946981819,
        1.3867087506243583,
        4.354153716748924,
        2.828574383269851
      ],
      "minimum_raw_offdiagonal_proposal": 0.16196551318201532
    },
    {
      "case": "dyadic_D1",
      "N": 1,
      "D": 1,
      "pre_violation": false,
      "projection_active": false,
      "g_min_pre": 1.0,
      "g_min": 1.0,
      "theta": [
        0.375
      ],
      "minimum_raw_offdiagonal_proposal": 0.0
    }
  ],
  "fixed_control_witnesses": [
    {
      "model": "newest",
      "intended_field": "C",
      "component_difference": 0.35851321625192645
    },
    {
      "model": "second_oldest",
      "intended_field": "C",
      "component_difference": 0.41826406501469854
    },
    {
      "model": "individual_frequency",
      "intended_field": "C",
      "component_difference": 0.02395607081678272
    },
    {
      "model": "old_C_for_R",
      "intended_field": "R_physical",
      "component_difference": 0.21639115411686247
    },
    {
      "model": "symmetrize_C_first",
      "intended_field": "R_physical",
      "component_difference": 0.436263731802221
    },
    {
      "model": "old_B_for_phase",
      "intended_field": "theta",
      "component_difference": 0.005545783091789769
    },
    {
      "model": "unprojected_B_for_phase",
      "intended_field": "theta",
      "component_difference": 0.018809418284226886
    },
    {
      "model": "reversed_sine",
      "intended_field": "theta",
      "component_difference": 0.07595714435902856
    },
    {
      "model": "append_old_theta",
      "intended_field": "history",
      "component_difference": 0.22547857217951428
    },
    {
      "model": "alias_new_theta",
      "intended_field": "storage_ownership",
      "component_difference": null
    },
    {
      "model": "unconditional_gate",
      "intended_field": "B",
      "component_difference": 0.009803921568627472
    }
  ]
}
```


## Appendix C. Preregistration, review/integration and resource records

### PLAN.md

```text
# 010 preregistration — reachable history indices and coupled one-step source contract

Researcher040282. Prepared2026-09-04 Atlantic/Reykjavik. Session preparation label
is separate from owner/repository November labels and compiler/runtime clocks.
This plan precedes acquired-engine execution, theorem compilation and comparisons.
Source/Lean/feedback inspection and independent formula design only so far.

## Fresh source, scope and nonduplication

Main eb3933c196ee19e80e1621ae80d89ca72e6d9485;32 selected source/library/status
files. Inbox00a29ce538a40b553a723dd73dbd676129bfcd9a;8 selected notes/evidence.
Targeted R040282 intake/R001 notes/general TRIAGE unchanged. Three new public
provenance-mutation files exist; read only review/evidence, not the reproducer.
Those report copied-function mutations consistent with009; not independent review
of our companion, not a reason to duplicate provenance work in010. No new named
005–009 review/receipt in selected targeted notes. Current main Lean modules
explicitly exclude phases/delay in their scopes; keyword/header check finds no
history-buffer implementation among selected main lean/*.lean. Not an exhaustive
private theorem/coordination search. Public first100 navigation:1 open PR,
16branches, no history/delay/phase/buffer match. Open PR16 is chronicler corrigenda,
not a dynamics-buffer implementation; avoid that work and rate-law sweep/docs.

Actual aief_experiment_engine_v1.py is ART-0702 Frozen/authority-locked. Never edit
source, registry, locks or install a replacement. Full engine import allowed for
isolated synthetic primitive probes; NO run_seed/simulate_prefix/simulate_future/
run_baseline_equivalence, real study, production trajectory or certificate. Short
one/few-step SYNTHETIC microtrajectories are the test, not a campaign. Shuffle
branch/interventions/diagnostic pipeline remain outside scope. No remote writes,
PR, contact/upload or unattended011. Prior009 is complete; do not rerun it.

## One load-bearing boundary and exact mathematical statement

Source ModelConfig.delay_steps is D=round(tau/dt); validate requires tau>0,
dt>0 and EXACT D*dt==tau (rtol0,atol0), hence validated cases have D>=1.
History length must be D+1; initialize_state constructs D+1 independent copies
of theta0. compute_R and phase update read history[0] BEFORE append/pop.
advance_state uses theta_old/history0 to update directed complex C, reads R from
UPDATED C by magnitude THEN symmetrization/zero diagonal, updates/clips/symmetrizes
B, conditionally gates it, advances phase with NEW GATED B, then appends a COPY of
new theta and pops oldest if length>D+1. No separately pre-calling compute_R,
which would update C twice. RNG must remain unchanged for shuffle_driver=False.

For any value type A, delay D in Nat and arbitrary trace x:Nat->A, define H0 as
constant D+1-vector x(0). Let H(n+1)=shift-tail-and-append(H(n),x(n+1)). Prove:

    H(n)[i] = x(n+i-D), for every i:Fin(D+1),

where Nat subtraction is truncated at0. Endpoint corollaries:
H(n)[0]=x(n-D), H(n)[D]=x(n). This settles the D versus D+1 storage/read confusion
and startup constant prehistory, without assuming the lag identity in a premise.
At read time step n the delayed phase is x(max(0,n-D)), not x(n-D+1).
This is a reachable/initialization-history theorem, NOT an assertion for every
arbitrary history merely accepted by state.validate (it does not enforce last=
theta or reconstruction from a trajectory). Shift equality assumes value semantics;
Python copy-ownership is separately probed, not Lean-verified memory semantics.

Three named declarations intended: universal coordinate theorem plus oldest/
newest corollaries. Generic core Lean module, import Std only; no Mathlib or
coupled stability assumption. A=phase vectors is an intended instantiation, not a
formal Python/float FFI theorem. No phase-locking/global gate/ON/OFF claim.

## Independent scalar reference and fixed numeric domain

Immutable tuple cases; compute ALL expected outputs BEFORE source call. Pure
Python math/cmath scalar loops for phase input/complex EMA, magnitudes, row sums,
nonnegative B clipping, strict conditional capacity gate, coupling and modulo.
Do not call engine compute_R/advance_state or get expected values from their
outputs. Actual engine imported intact, constructor copies provided arrays;
advance_state mutates only a disposable working state, not immutable case data.
Use actual config/state validation before each intended transition.

Check R_physical/R_driver, C_new, B_new, theta_new, every history vector, selected
pre_violation/projection_active/g_min_pre/g_min values. No certification of other
norm/relative projection diagnostics, shuffle/intervention or production loops.
Absolute tolerance5e-13,relative0 for finite numeric fields, fixed before results;
exact shapes/flags/counts/alias checks, finite outputs and phase range[0,2*pi).
Do not adjust tolerance to turn a failure green. Compare complex components via
real/imag numeric differences, not the known whole-element-NaN helper.

Nine one-step cases: nontrivial inactive D1; active D2; active D3; zero-C/new-drive
D2; phase-wrap D1; exact-capacity N2 boundary (a1,q1,delta.5,Bedge.5,eta=mu=gamma0,
epsilon.01); negative proposal clipped to0; directed-C N4/D4; N1 dyadic drift.
Default nontrivial N3 theta(.31,1.27,4.13), omega(.5,1,1.5), oldest(5.91,.81,2.24),
Bold edges(.08,.23,.32), directed C with nonparallel/asymmetric entries. dt1/8,
tau=D/8, Tw.5; a1,q1.5,delta.1; active eta3,mu.05,gamma.2,epsilon1e-12. Values
chosen from the scalar formulas BEFORE comparing source. Require active case's
correct phase to differ from old-B and unprojected-B models by>1e-7; asymmetric
R models/age/frequency/sign controls must have a>1e-7 field witness (not tolerance
fuzz). Inactive/zero/clipped/boundary cases avoid only vacuous zero coupling.

## Same nine common source methods, normal and -O

1 nine scalar-reference one-step cases, all fields above;
2 change oldest only (pair): expected instantaneous C/phase dependence, not newest;
3 change an interior non-oldest history only (pair,D2): same immediate C/R/B/theta,
   different shifted history; shows interior is latent rather than discarded;
4 five exact dyadic N1 histories (D1..5),12 advances each, theta0=.25,omega1,
   dt.125, no wrapping: exact H(n)[i]=.25+(max(0,n+i-D))*.125.65 states,
   260 stored-coordinate checks,60 actual transitions; source values bit-exact,
   expected from arithmetic trace not previously observed source phase outputs;
5 explicit new-gated-B nonvacuity versus old/unprojected models;
6 updated-C then magnitude/symmetrization nonvacuity;
7 wrap/clipping cases and output ranges;
8 independent history storage: no vector aliases another or theta;
9 validate nine configs and exact-delay domain; tau.2/.1875 withdt.125 fail for
   exact consistency, not setup errors. Domain checks counted separately, not
   wrong-model detections. Abstract Lean D0 is valid mathematics only, not a
   source config permitted by positive tau/exact consistency.

Expect nine source methods PASS/0errors/0skips, both interpreters. Planned78
actual advance_state calls per common suite (including60 dyadic transitions).
No source repair/failing-before claim:010 establishes a faithful component.

## Eleven independent wrong models, both interpreters

Newest instead of oldest; second-oldest off-by-one; individual omega_i instead
of mean(omega_i,omega_j) in C input; old C for R; symmetrize C before magnitude;
old B for phase; unprojected B for phase; reverse sine coupling sign; append OLD
theta; alias appended history to current theta; apply gate unconditionally even
at exact capacity. All numerical controls must fail intended field comparison;
alias control must fail storage_ownership. Use fixed witnesses, require distinct
wrong-model names; source remains untouched. Setup/import/timeouts are blockers,
not successful falsifiers. Normal/-O records match without timings.

## Lean/compiler and eight proof-check controls

Existing lean/lake executable and old disposable cache absent;20GB free observed.
Use prescribed leanprover/lean4:v4.33.1, core Std only. Public570405234B release
asset; verify published digest/length before selective compiler/runtime extraction
into own excluded .cache/researcher040282-cycle010. Small zstandard decoder may
be installed into that disposable target only. No global toolchain setting,
Mathlib download, old cache restoration or third-party code in packet. Remove
OWN disposable compiler/archive/decoder after actual standalone reproduction;
preserve minimal setup receipt/logs only. Do not restore deleted Lua audit.

Compiler must return0 without warnings, named theorem/axiom print coverage exact,
footprints subset{propext,Classical.choice,Quot.sound}; no sorry/admit/native_decide/
extra axioms/unsafe accepted. Preserve any development compilation errors as such,
not intended negative controls; final claim only actually accepted theorem source.

Eight formal controls: nonzero-delay positive, abstract-D0 positive; false youngest-
read, false one-extra-delay read, false append-old/current endpoint (three explicit
Nat witnesses) must fail math with no dependency/setup error; compiling sorry and
compiling added-axiom payloads must be rejected by policy; compiling omitted-axiom-
print source must be rejected by coverage. Do not count compiler/setup failures
as rejection of false math or integrity detection.

## Closeout / what must not be promoted

Full runner original/optimized engine/mutant checks plus actual theorem/control
compilation; then full inline standalone note, extract owned critical code,
fresh-fetch engine+registry/toolchain metadata (3 public dependencies) and repeat
complete runner with same disposable compiler. Compare science/non-timing child/
proof records, not timing logs. No independent approval inferred. Only after
observed success append three scoped LEAN_COMPILED rows and one executable source
contract row (expected118total,97formal labels), retaining prior114/94 unchanged.
If Lean is blocked, no compiled promotion; if source mismatch, preserve and narrow
or report blocker rather than weaken tests. All old science/state snapshots,
reports and archives unchanged, cited logs unpacked/indexed, metadata minimal.
One bounded foundation result; no011 work this turn. Owner uploads dated note.
```

### proposal/INTEGRATION_NOTE.md

```text
# 010 new-file history foundation — review only

No engine repair: the tested frozen engine agrees with the independently derived
finite primitive contract. Do not edit ART-0702, authority locks, registries,
pinned ART-0050 or existing reference modules from this packet.

Candidate new module `HistoryBuffer.lean` imports only Std. Its generic trace
recurrence and three theorems settle constant startup, D+1 storage versus D-step
lag, and oldest/newest endpoints. It does not assume the desired index formula;
it assumes the concrete constant initialization and shift/append recurrence.

Review the correspondence in `SOURCE_CORRESPONDENCE.md` separately from the Lean
kernel result. Python copies/allocations, exponential/sine/modulo and coupled
matrix evolution are not Lean verified. Source state.validate alone does not
assert reachability. Abstract D0 is valid for the value theorem but invalid for
the source's positive-tau/exact-delay configuration domain.

The independent math/cmath scalar model and finite actual-engine tests exercise
updated C -> magnitude/symmetry R -> clipped/conditionally gated B -> phase using
NEW gated B -> append COPY. They are executable evidence, not a replacement
engine or full baseline-equivalence certificate. Wrong models never replace
functions on the imported engine. No production studies or shuffle branch.

Owner/Researcher001/AuditorSeat002 must independently review and decide whether
to incorporate a new module. Prior compilation/intake reviews do not approve this
new module, contract, oracle or controls. No direct inbox merge, remote change,
automatic upload, authority promotion or production installation is authorized.
```

### review_decision.json

```json
{
  "cycle": 10,
  "decision": "LOCAL_HISTORY_FOUNDATION_AND_FINITE_SOURCE_CONTRACT_ONLY;INDEPENDENT_REVIEW_PENDING",
  "feedback_refresh": {
    "main_selected_files": 32,
    "inbox_selected_files": 8,
    "targeted_intake_R001_notes_general_TRIAGE_unchanged": true,
    "new_provenance_mutation_review_evidence_read_only": true,
    "new_contributed_reproducer_fetched_or_executed": false,
    "colleague_report_approval_of_009_guard_inferred": false,
    "public_open_PRs_examined": 1,
    "public_branches_examined": 16,
    "relevant_history_delay_phase_buffer_match_in_limited_navigation": false,
    "nonduplication_is_exhaustive_or_private_work_assurance": false
  },
  "accepted_locally_after_original_execution": [
    "Three actual compiled generic reachable-history declarations, Std only, footprints propext/Quot.sound, no main warnings/errors/sorryAx",
    "Nine unchanged-engine contract methods pass normal/-O, 78 advances and one initializer per mode, independent math/cmath reference",
    "Exact five dyadic histories: 60 transitions, 65 states, 260 stored coordinates each mode",
    "Eleven fixed wrong models detected each mode by intended field/storage check; two exact-delay configuration rejections separately",
    "Eight formal controls: two positive, three explicit false-Nat witnesses, three compiling integrity payloads"
  ],
  "development_failure_preserved": {
    "path": "development/initial_proof/compiler.log",
    "reason": "Initial owned proof did not expose a Fin projection before omega arithmetic; compilation returned1 and printed inherited sorryAx",
    "correction": "Explicit definitional change of the projected arithmetic goal; statement/recurrence unchanged",
    "corrected_preflight": "development/projection_explicit/compiler.log",
    "credited_as_intended_control_or_compiled_final_evidence": false
  },
  "not_approved": [
    "Universal Python/NumPy or float/trigonometry equivalence, full Lean coupled one-step theorem, stability or phase locking",
    "Lag identity for every arbitrary history accepted by state.validate, or source validity of abstract D0",
    "Production simulation, real S01, baseline-equivalence campaign, shuffle/intervention, certificate, CLI or full-study result",
    "Registry/lock/frozen source edit, replacement engine, reference-library integration or installation",
    "Independent approval of new history theorem, scalar oracle, fixtures, tests, controls or earlier005-009 companions",
    "Novelty against all existing/private work, approval of third-party provenance calculations, remote push/contact/PR/upload or unattended011"
  ],
  "requested_review": {
    "Researcher001": "Check shiftAppend/startup theorem and the source-to-value-model correspondence, especially D versus D+1, truncated startup, and explicit reachability assumptions; consider a new unregistered library module only after review.",
    "AuditorSeat002": "Independently inspect/run fixed scalar oracle, source call inventory, ownership probes and compiler/policy controls; keep finite agreement and generic proof separate. Do not treat earlier94 compilation review as approval of010."
  },
  "publication": "LOCAL_PREPARED_FOR_OWNER_UPLOAD_ONLY",
  "next_cycle_candidate_not_executed": "Fresh-check modulo-safe phase-increment/delayed-input bridge, separating constant startup from live delayed history; choose smallest noncircular useful statement before any new run."
}
```

### nonduplication_check.json

```json
{
  "open_pr_count_seen": 1,
  "branch_count_seen": 16,
  "matching_open_prs": [],
  "matching_public_branch_names": [],
  "current_main_Lean_keyword_review": "Only exclusions/comments on delay/history; no matching implementation found among selected main lean/*.lean. Limited static keyword/header review, not exhaustive theorem search/private work assurance.",
  "scope": "Public first100 names and selected main/source/feedback only; no contact or author payload persisted",
  "open_pr_navigation": [
    {
      "number": 16,
      "title": "Corrigenda: fix the chronicler's own two errors at the source (shallow-clone dates, mention-vs-assertion bare refs)",
      "head_branch": "arena/8aa39f3a-aiefs"
    }
  ]
}
```

### compiler_setup.json

```json
{
  "toolchain": "leanprover/lean4:v4.33.1",
  "compiler_version": "Lean (version 4.33.1, x86_64-unknown-linux-gnu, commit 819816b2e0a3bf405af45ae5c7af2491d8f5bee6, Release)",
  "public_asset_verified": true,
  "download_bytes": 570405234,
  "selectively_extracted_members": 7488,
  "selectively_extracted_bytes": 2124052415,
  "compiler_binary": "/home/user/.cache/researcher040282-cycle010/lean-4.33.1-linux/bin/lean",
  "cache": "/home/user/.cache/researcher040282-cycle010",
  "Mathlib_installed": false,
  "global_toolchain_changed": false,
  "decoder_installed_into_disposable_target": true,
  "decoder_version": "0.25.0",
  "cache_excluded_from_packet_and_to_be_removed_after_reproduction": true,
  "elapsed_seconds": 26.25736227699997
}
```

