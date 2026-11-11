#013 bounded plan — phase-specific EMA/drive binding

User/team correction received. Deliver ONE new Lean file +short note, no packet
builder, ZIP, self-certification harness, production run or008/009continuation.
Protect completed012root snapshots; refresh live state/ledger/index every cycle.

Fresh read: main b198a77afe9890a815c614031e382973258e2d94;48selected source/docs.
Merged PR listing explicitly read: #17–#24 merged (including gate P3); current
open#25 guarded-capacity port, not merged. ERRATA E19–E26 and current gate
GateMap/MatrixForm inspected. Use actual main Params/preM interfaces, never
modify main/pinned sources. Accepted010/011source files remain dependencies.
Main at this basis has NO phase/EMA state/convention definition; do not pretend
an equality to an existing main phase model or a Python/float FFI proof.

Focus: restate source-specific EMA/drive on011inputPhasor, add exact complex
phase-convention/innovation equations and nonzero concrete phase-response probes,
then bind the resulting drive to CURRENT main MatrixForm.preM. Mere unit-disk/
range bounds remain true for any phase and CANNOT themselves pin conventions.

Intended new module: PhaseCoherenceBridge.lean, importing current main
AIEFGateCore.MatrixForm and accepted PhaseIncrement/HistoryBuffer. Define only
phase-specific coherence step/trajectory (no arbitrary z argument), reported R,
D=(eta+mu)*R-mu and normalized drive when gamma>0. Prove source-angle equality,
innovation transport with correct startup late increment, phase-specific unit-disk/
reported-R/drive bounds, exact preM source formula and eta response.

Concrete held-proof witnesses: Fin2, D2, theta0=0,u_k=pi/2,omega=1,tau=pi,
alpha=1/2,C0=1. Inputs z0=-1,z1=-I,z2=z3=1; C1=0,C2=-I/2,C3=1/2-I/4,
C4=3/4-I/8. Offdiag R after second update=1/2. With main p.dt=1,p.gamma=1,
B0=0,eta2,mu1, preM after second update=1/2. Generic-increment witness, not a
formal proof that a whole production trajectory generates this u/alpha.

Mutate implementation components ONLY in disposable copies, keep main and held
statements/reference/probes fixed: D+1delay, H1instead ofoldest, current/newest
instead ofdelayed, dropped mean-frequency*tau, constant phase0(exp0=1), early
startup late increment n>=D-1, missing eta. Constant complex0 extra if useful.
Require actual proof failures, not unknown identifiers/setup; independently
reduce the mutant's explicit witness to contradiction/refutation where feasible.
Do not falsely demand valid generic bounds become false under every phase change.
No full coupled dynamics/locking/future-band assertion.

Compile directly with prescribed Lean/Mathlib +unmodified selected main sources,
print named axiom footprints. No check_cycle.py security claim: source review for
implemented_by/extern/macro/elab and other executable hooks is explicit, NOT a
complete arbitrary-Lean verifier. Stock compiler/library trust remains.

Source timing: old theta/history->C->magnitude/symmetric R->new B->phase->append.
Use correct read-time oldest max(0,n-D), no drifting startup. Source epsilon
not used in this phase/preM algebra; no gate-capacity theorem or epsilon claim.
Do not introduce redundant hf0; the003port/trajectory invariants/sharp row bounds
remain separate work, not silently bundled into013.

Date correction: old September labels are NOT reliable execution dates for
November source snapshots. Do not invent historical run dates. New run records
capture observed UTC execution-clock timestamps, explicitly distinguished from
source commit/upload dates. Retain original delivered scientific files; issue
numbered date/state correction in the short note/root records, not a silent
pinned-file rewrite. Local root before013was012/126rows/103labels; team handoff
will include current root files rather than recreating an old uploaded snapshot.
