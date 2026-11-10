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

{{CORRESPONDENCE}}

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

{{RESULTS}}

### Actual common normal-mode log

{{COMMON_LOG}}

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

{{WRONG_MODELS}}

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

{{MAIN_LEAN_LOG}}

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

{{FORMAL}}

### Explicit false-math compiler diagnostics

{{FALSE_MATH_LOGS}}

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

{{STANDALONE}}

### Own disposable compiler cleanup

Cleanup occurs only after successful full reproduction, removes only the
cycle010-owned compiler/archive/decoder target, not other caches or research.
The already deleted old Lua audit remains absent and is not restored.

{{CLEANUP}}

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

Live ledger at final assembly: **{{LEDGER}}**. Prior114 rows and their94 formal
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

{{CRITICAL_FILES}}

## Appendix B. Independent pre-engine case design

This design record predates acquired-engine import/advance. It is scalar-formula
evidence and fixed-witness design, not observations from the engine.

{{DESIGN}}

## Appendix C. Preregistration, review/integration and resource records

{{RECORDS}}
