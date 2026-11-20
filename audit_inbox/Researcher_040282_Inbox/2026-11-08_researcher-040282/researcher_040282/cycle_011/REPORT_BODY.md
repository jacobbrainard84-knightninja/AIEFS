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

Ledger after actual closure: **{{LEDGER}}**. Previous118rows/97formal labels
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

{{RESULTS}}

### Same nine common methods — actual normal-mode log

{{COMMON_LOG}}

### Ten wrong models — intended semantic detections, not source modifications

{{WRONG_MODELS}}

### Design receipt produced before target import/advance

{{DESIGN}}

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

{{MAIN_LEAN_LOG}}

### Complete formal result, dependency/main policies and8controls

{{FORMAL}}

### Actual three false-math logs

{{FALSE_MATH_LOGS}}

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

{{STANDALONE}}

The repeat uses the SAME original verified compiler/targeted Mathlib, not a second
clean bootstrap. Four-worker non-timing records and31detailed files include
preexecution design, source observations, ratio observations, wrong models, formal
result and10compiled sources/10compiler logs. Timing-bearing common logs need not
byte-match; scientific content must. Local submitter repetition is not external
seat review.

**Own disposable setup cleanup, after actual full repetition:**

{{CLEANUP}}

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

{{CORRESPONDENCE}}

### Preregistration, integration restrictions and minimal setup/intake records

{{RECORDS}}

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

{{CRITICAL_FILES}}
