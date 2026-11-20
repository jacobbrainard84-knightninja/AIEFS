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

Local ledger after actual closure: **{{LEDGER}}**. Prior122rows/100formal labels
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

{{RESULTS}}

### Actual same nine common methods — normal-mode log

{{COMMON_LOG}}

### Ten independent wrong models, NOT source mutations

{{WRONG_MODELS}}

For wrong upper bounds, rejection requires actual error>wrong bound+1e-7,
not merely a different safe envelope. Equality controls require intended component
mismatch>1e-7. Fixed cases/points preceded scalar inspection and acquired import.
Missing variation/initial term, beta-scaled/sign-flipped drift, future-input update,
reverse weights, drifting prehistory, forced alpha1decay and stale R are tested.

### Pre-target design receipt

{{DESIGN}}

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

{{MAIN_LEAN_LOG}}

### Full formal result,28reused claims, new3 and8controls

{{FORMAL}}

### Actual three false-math compiler logs

{{FALSE_MATH_LOGS}}

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

{{STANDALONE}}

Same original verified compiler/targeted Mathlib, NOT a second clean installation
or independent seat's repetition. All16extracted code files,4fresh public deps,
science/four non-timing workers and35detailed files (10design/source/model,
1formal,12sources+12compiler logs) must match. Timing-bearing common logs need not
byte-match; actual scientific records do.

### Own disposable setup cleanup, after actual complete repeat

{{CLEANUP}}

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

{{CORRESPONDENCE}}

### Preregistration, integration restrictions, selection and setup records

{{RECORDS}}

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

{{CRITICAL_FILES}}
