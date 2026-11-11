#014 bounded plan — feedback trajectory safety on current main

Fresh basis3c5c0ef58c771b25c4b1eebd442e4073afa94b1f, ERRATA read, merged PR25
explicitly observed, no openPR. Inbox unchanged1b5ae52; no new013review. Current
Capacity.lean now has one-step stepM_nonneg/row_le_cap, MatrixForm has symmetry/
diagonal; Capacity explicitly says trajectories NOT proved. Existing Persistence
is frozen-drive branch-response, not this result. No public active trajectory
branch found; limited public coordination, not private assurance. User priorities:
013pending review; main still lacks phase state, so choose next missing Btrajectory
invariants, not duplicate003port,008/009,rate-law or other team work.

ONE Lean file +short note, no packet/self-certification. Main/pinned sources
unmodified. Direct compile/footprints and fixed semantic counterexamples only.
Execution-clock UTC captured, old historical dates not guessed.

Define a causal feedback recursion on Aux ×(V→V→Real): each step n computes
D=F(n,aux,B), Bnew=main MatrixForm.stepM(p_n,D,B), then updates auxiliary state
U(n,aux,B,Bnew). Aux can carry phase/history/EMA; F/U unrestricted, so R need
NOT be frozen or assumed symmetric. This does NOT yet instantiate a complete
Python/real coupled oscillator model.

Prove (using current one-step facts, not restating them as new research):
- for cap_n>=0,epsilon_n>=0, every positive-time B is symmetric/nonnegative/diag0,
  regardless of initialB; including time0 requires initial structural invariant;
- for EngineGate(p_n), B_(n+1) row sums<=cap_n; parameter clock is n, NOTn+1.
  Fixed parameters give all-positive-time capacity. No initial feasibility needed;
- nonnegative entry/row/edge envelope and |sum_j B_ij sin(delayed_j-theta_i)|<=cap
  for each positive-time B. With p.dt use |dt|*(|omega_i|+cap) increment bound.
  Theta/delayed vectors arbitrary: no assumed locking, future band or small drift.

Exact scope: structural positivity can use cap/epsilon>=0 (abstract Real division
by0 convention included); guarded capacity uses existing EngineGate, hence cap>0,
epsilon>0,gapQ>0,exact cap*gapQ=gapA-gapDelta. Physical source epsilon>0 only.
No unnecessary symmetry/nonnegativity hypothesis on drive or oldB, no gamma/dt
stability hypothesis for clipped/gated safety, no redundant hf0. No convergence,
common freeze time or sharp N12ON certificate derived from boundedness alone.

Nonzero/dirty-start concrete witnesses and known-false variants in Lean: returning
stale B; omitting clip; omitting symmetrisation; retaining diagonal; bypassing gate;
wrong current/next capacity clock; including time0without initial invariant;
broken capacity/guard link. Temporary implementation or statement mutations with
held proofs, no missing-name/setup failures credited. Use current main counterexample
for broken link when appropriate, don't rerun a gate audit already done by team.

Direct compile against unmodified main GateMap,EngineWitness,MatrixForm,Capacity.
No Python engine execution, production/baseline/S01/CLI/certificate, frozen edit,
remote contact/push/PR/upload/merge or015work. Own disposable compiler/Mathlib
cache removed after actual checks. Root state/ledger/index updated; prior evidence
preserved and only known missing historical citation copies restored if necessary.

Clarification before mutation runs: extend the chosen state-feedback 1→0→1 witness
to an exact two-cycle for all n, proving no eventually constant edge in the GENERAL
drive class. This is NOT a counterexample to the still-uninstantiated full
phase/EMA oscillator. It makes the safety/not-freezing scope mathematically explicit.

Adversarial-method refinement: whole-file bad-adapter copies hit downstream
isDefEq heartbeat limits and are NOT credited. Use definition-prefix copies with
focused, exact concrete held probes (six positive baselines) plus explicit false
time0/unlinked claims. Same eight semantic variants/counterpoints, same candidate
and hypotheses, no timeout relaxation. Each negative must reduce to explicit
False, not merely fail a generic elaboration path.
