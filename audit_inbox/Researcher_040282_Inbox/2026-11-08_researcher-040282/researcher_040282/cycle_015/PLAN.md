#015 bounded plan — instantiate the real phase/history/EMA/B loop

Current main3c5c0ef58c771b25c4b1eebd442e4073afa94b1f, ERRATA read, mergedPR25
confirmed, openPR26cycle003Freeze/WeightUpdate port read and NOT duplicated.
Current inboxdf5c28f adds only a static P3/P4areview (read; no local execution or
013/014review there). Current main still has no phase/history/EMA state model.
No public competing full-state branch found; no private-work assurance.

One Lean file +short note, no packet/ZIP/security verifier/Python production run.
Preserve014root snapshots; update root state/ledger/index with observed run-clock
UTC and honest unknown historical dates. No008/009/rate-law/entrypoint/CI work.

New ClosedLoopCore.lean imports actual current main Boperator plus own013and014
candidates (explicitly not yet team-adopted), accepted010/011dependencies.
Define Config with main Params,eta,mu,Twindow,tau,omega. Alpha=REAL exp(-dt/Tw),
not an arbitrary coefficient or an asserted IEEE equality. Auxiliary state carries
theta, Fin(D+1)history, directed complex C. Full state is Aux×B.

F computes old-state source phasor, NEW C, magnitude-then-symmetric/diag0R,
D=(eta+mu)R-mu. Actual main stepM computes NEW gated B. U then uses old theta/
oldest history but NEW B for delayed-current sine, floor wraps theta, shifts and
appends NEW theta, returns NEW C. Recomputing a pure expression inside F/U is not
reopening/mutating source data. No shuffle branch, validation exceptions,
projection diagnostics, allocation or Python/float FFI claims.

Meaningful intended proofs: full model is a concrete014causal feedback instance;
Bstructure/capacity invariants apply along THIS recurrence, not an unspecified
F/U; actual history equals010historyTrace of actual theta; actual theta equals011
wrapped phaseTrace driven by increments GENERATED from NEW model B; actual raw
input equals011inputPhasor; actual Ctrace equals013phase-specific coherenceTrace.
No assumed input/drive/locking/band conclusion. Conditional real alpha/unit-disk
and C/Rrange statements may be derived. Source validity requires positive dt/Tw/
tau, D*dt=tau henceD>=1; algebraic identities can be more general, stated precisely.

Before compile/test, fixed nonzero first-step witness: Fin2,D1,dt1,gamma1,cap1,
eps1,gapA1,gapQ1,gapDelta0,eta4,mu0,Tw=1/log2,omega0;theta=(0,pi/2),history
constanttheta,C0=B0zero. Prove REAL alpha=1/2, Cnew diag1/2/offdiag(-I/2,I/2),
Rnewoffdiag1/2, proposaloffdiag2, gated Bnewoffdiag2/3, used phase increment0=2/3.
OldB would give0, unprojectedB2: nonvacuous ordering/gate witness. These are real
component/model values, not frozen production parameters or a float replay.

Fixed semantic negatives on disposable candidate copies/finite claims: use old C
for drive/R; magnitude after complex symmetrisation; use OLD B for phase; use
UNPROJECTED B for phase; append old theta; read newest history; omit meanfrequency
*tau in raw input. Hold independent state/probe claims fixed. Six/seven exact
positive baselines +explicit False negatives where feasible; name/import/parser/
heartbeat/timeouts BLOCK, never detections. If whole-model elaboration is costly,
isolate fixed exact definition-prefix probes as014did, record any blocked attempt.
No mutation of current main/pinned/accepted sources. Review implemented_by/extern/
macro/elab/unsafe/proof-hole hooks explicitly, not claim arbitrary Lean security.

Direct prescribed compiler/Mathlib setup into own excluded cache, resource bound
12GiB/15minsetup. Compile unmodified main/old candidate dependencies then newfile,
print axiom footprints. Remove own runtime/Git/Mathlib/mutant cache after actual
checks. No root proof-label promotion before compile/check outcomes. No integration,
remote branch/push/PR/contact/upload/merge, production/S01/baseline/CLI/certificate,
closed-loop locking/freezing, sharp N12band or016work.
