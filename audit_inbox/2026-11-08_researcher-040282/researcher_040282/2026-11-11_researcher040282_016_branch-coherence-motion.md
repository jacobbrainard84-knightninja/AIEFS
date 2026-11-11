#016 — one-step movement of reported coherence R

**Researcher040282 → Researcher001 / AuditorSeat002. USER-APPROVED BRANCH SCOPE.**

[CoherenceMotion.lean](cycle_016/CoherenceMotion.lean) +this note. This imports
**the team’s unmerged P5 branch**, not flat local015files and not current main.
Source: `research/lean-gate-p5@54037ea1fabbeaed1eab44636971051000ac1673`;
module `AIEFGateCore.PhaseCoherence`, namespace `AIEFGate.PhaseCoherence`.
No state/model/operator is redefined; `rTrace` only names the existing reported
value along the existing coherence trace.

## Scope decision before proof

Fresh main `1c30ca56...`, ERRATA and merged/open PRs read: #26/#27merged, no openPR
at inspection. P5/C014are still unmerged branches; the015port is not publicly
present. I asked rather than inventing main imports. The user selected the
**branch-scoped R component**; the coupled non-reset/nonconstant-history Bprobe
is **deferred until its main model port is available**. I have not resent015or
claimed its F1/F2fixes completed here.

## Derived property — no assumed future band

Write r=reported C and rnext=reported(coherenceStep alpha C …), beta=1-alpha.
For0<=alpha<=1 and the existing P5unit phase input, the file proves:

**alpha*r-beta <= rnext <= alpha*r+beta.**

Equivalently,

**-beta*(1+r) <= rnext-r <= beta*(1-r),**

and therefore **|rnext-r| <= beta*(1+r)**.

The state-dependent envelope needs no initial Cunit-disk condition. It follows
from the two directed complex norms and the existing magnitude-then-symmetric
reported operator, not a frozen-phase/controller or desired-band premise.

Along the existing P5coherence trajectory, its already-proved unit-disk invariant
transfers from the plainly stated initial condition `||C0_ij||<=1`. Thus for every n:

**|R_(n+1)-R_n| <= min(1,2*(1-alpha)).**

Our observable is `rTrace_n = reported(C_n)`. A source advance starting at n
returns `reported(C_(n+1))`, not `reported(C_n)`; consecutive returned Rvalues
use the same theorem shifted by one index. The fixed-time value probes, not a
self-agreement rfl, test that visible clock.

The diagonal stays exactly0. The factor2cannot generally be replaced by1: with
unit initial coherence and opposite unit input, it is attained for every
**1/2<=alpha<=1**. This is not a claim that the min-bound is globally optimal
for all smaller alpha, or that a production zero-initialised run attains equality.

This is a first **derived movement constraint** on the proposed coherence
component. It does not assert Rconvergence, a strict ON/future band, phase locking,
Bpositivity/freezing or finite-time certification. Repeated small changes may
accumulate; the estimate alone gives no infinite-tail guarantee.

## Independent value evidence, not rfl self-agreement

The closed-form probes evaluate the existing branch definitions at fixed times.
Their input is−1 (zero phase increments, omega1,tau=pi); arbitrary prescribed
increments are allowed by P5. They are component witnesses, NOT full phase/B
trajectories or the requested non-reset coupled-state probe.

- alpha1/2,C0=1: r0=1,r1=0, change1=2*beta (maximum decrease witness).
- alpha1/2,C0=0: r0=0,r1=1/2 (upper increase witness).
- alpha3/4,C0=1: r2=1/8; two-step change7/8exceeds one-step allowance1/2.
- alpha−1,C0=1: r1=3while the claimed upper envelope would be1.
- alpha2,C0=0: r1=1while the claimed upper envelope would be−1.
- alpha1/2,C0=3: change2exceeds the unit-initial one-step bound1.

Negative/out-of-domain alpha or C0values test dropping hypotheses, not invalid
source configurations run as successful checks. The predicates/time indices are
held; no expected value is obtained by applying the new inequality to itself.

Seven fixed positive value probes compile (return0). Seven negatives return1
with explicit `⊢ False`, no name/import/parser/heartbeat/timeout credit:

| false variant | exact obstruction |
|---|---|
| factor2replaced by1 | change1exceeds beta1/2 |
| increase-only bound used for absolute decrease | change1exceeds beta*(1-r0)=0 |
| alpha>=0dropped | alpha−1gives r1=3>upper1 |
| alpha<=1dropped | alpha2gives r1=1>upper−1 |
| initial unit disk dropped | C0=3gives change2>bound1 |
| two-step difference given one-step allowance | change7/8>allowance1/2 |
| observable clock shifted n→n+1 | held r0=1becomes0 |

A legitimate **+0observable equivalence** compiles with the same seven held value
probes (return0). The negatives are not counted merely because a proof term no
longer matches: independent fixed-time branch-operator values yield contradictions.


The baseline Lean file compiles cleanly: no warnings/errors/holes; printed public
footprints only propext/Classical.choice/Quot.sound. One negation-placement proof
draft needed explicit `neg_mul`normalisation; that draft is retained, not promoted
or counted as a negative. Branch definitions/imports/pinned files unmodified.
New fixed source reviewed for implemented_by/extern/macro/elab/unsafe/hole hooks,
none present; this is NOT an arbitrary-source Lean security verifier.

## Adoption notes and limits

015is recorded as **ADOPT WITH NOTES** in the root ledger/state, exactly as relayed:
Auditor002recompiled35prints/steporder, killed13invalid mutations and accepted2
legitimate equivalences. F1delayed phase-read required and F2dt pin go into the
team’s port; F3non-reset carry, F4dead complex-mean helper and F5probe-over-rfl
qualifications remain explicit. No blanket approval of own old probe scripts.

This file does **not** solve the deferred Bcarry/delay/dt probe. It does not port
015or widen the model. It uses the branch’s named coherence operator, with
0<=alpha<=1 and, for the uniform trace bound, unit initial C. The broad unit-disk
geometric range is derived, not an assumed strict future Rband. Generic norm
estimates do not pin phase/delay conventions; no such claim here.

No claim about a complete coupled model already on main, Python/float equality,
rounded-alpha strict contraction, source validation/aliasing/shuffle/production,
S01/baseline/CLI/certificate or independent adoption. Source main still lacks the
required ports at the recorded basis. User specifically approved this narrower,
explicitly unmerged component result.

## Reproduce / handoff

Use a scratch checkout of **P5branch54037ea**, NOT a guessed current-main API,
with its prescribed Lean/Mathlib. Compile the branch imports unchanged:

```text
export LEAN_PATH="$PWD:$(lake env printenv LEAN_PATH)"
# use project-prescribed lean
for f in GateMap MatrixForm HistoryBuffer PhaseIncrement PhaseCoherence; do
  lean --root=. -o "AIEFGateCore/$f.olean" "AIEFGateCore/$f.lean" || exit 1
done
lean --root=. CoherenceMotion.lean
```

Raw baseline: `cycle_016/development/baseline_compile/compiler.log`.
Exact probes: `cycle_016/development/counterprobes/`.
No new ZIP, packet/self-certification,015resubmission,008/009/rate-law/CI work,
main edit or remote contact/push/PR/upload/merge.

**Observed run-clock record:** clean baseline compile began
2026-11-11T01:58:30.083804Z; focused negative runs began02:02:00Z, followed by the
accepted equivalence control finishing by02:07:46Z. Own setup removed afterward
(62910regular entries,6026979541logical bytes,15measured symlinks).
No unrelated-cache audit/deletion claim. Root STATE/ledger/index updated for016,
including the scoped015adoption/F1–F5notes and explicit deferred coupled probe.
Historical statements/evidence preserved; no guessed old dates or017work.


**Requested review:** additive Rmovement envelope, exact hypotheses and clock
against the named P5component. Once the ports land, instantiate the property on
the actual team coupled recursion and do the non-full-reset/nonconstant-history
carry/delay probe with main names. Another Continue first refreshes source and
feedback; no017work has started.
