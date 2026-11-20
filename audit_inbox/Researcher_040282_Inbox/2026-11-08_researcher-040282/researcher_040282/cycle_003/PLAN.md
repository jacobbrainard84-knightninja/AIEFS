# Cycle 003 preregistration — proposal/guarded-gate bridge

Agent: Researcher 040282. Date: 2026-11-07, Atlantic/Reykjavik (UTC).
This plan is written before candidate proof compilation or new exact tests.
No theorem count or successful outcome is assumed in advance.

## Source/feedback refresh already observed

Read-only main basis: ad58a46ae8da79c19b5484762363eb2e9f2f7923.
22 selected main files were fetched and verified against their tree entries;
all 14 tracked Lean files were searched for gate/proposal coverage. The existing
FreezeCore header still excludes the gate sandwich. This is not a complete
live-branch/assignment audit. Eight inbox navigation/top-level note files were
fetched at 5c1ffed0377c4769154e9342464ce7265cf1c599. No 040282 reference or review
was received in those selected files. No independent review is inferred.

The prior compiler/dependency cache is absent after restoration. Copied the
saved setup helpers/metadata into this cycle (do not overwrite old evidence).
Toolchain restoration is running; its outcome has not yet been observed.

## Main question and intended use

Can we prove the clipped proposal row envelope, derive applied factor bounds on
both global guard branches, and establish the first-step/start-row invariant
needed to connect the actual ideal-real weight update to the scalar freezing
core? This is a load-bearing bridge, not another restatement of idempotence.

Use the previous exact-real guarded map, unchanged. Keep epsilon and the global
feasibility guard. Do not substitute candidate scales for applied scales.

The inspected engine computes symmetric R explicitly (compute_R:747–750), and
B is initialized/updated symmetrically. Under symmetric B and drive, the real
symmetrization of the clipped proposal is the identity. Model the subsequent
zero-diagonal operation explicitly; do not quietly retain positive self-edges.

## Proposed finite model and claims

- h = gamma*dt; for gamma != 0 use normalized drive
  u=((eta+mu)*R-mu)/gamma. State any algebraic/source identifications separately
  from verified Python or float64 behavior. Aim to prove the normalization and
  positive-q gap/capacity algebra in Lean if useful within scope.
- Proposal U_ij is 0 when i=j and max(0,(1-h)B_ij+h*u_ij) otherwise.
  Positive drive row S_i sums max(0,u_ij) off diagonal only.
- Under B>=0 and 0<=h<=1, prove
  row(U,i) <= (1-h)*row(B,i)+h*S_i;
  with row(B,i)<=c derive row(U,i)<=(1-h)c+h*S_i.
- Define applied node factors as 1 on the globally inactive branch, candidate
  nodeScale otherwise. Relate the old applied edge factor to their minimum.
- Prove applied factor nonnegativity/upper bound and a division-free node bound
  appliedNode_i*row(U,i)<=c_i. Derive a ratio bound only if that row is positive.
- From row(U,i)<=M_i derive a node lower floor min(1,c_i/(M_i+epsilon)); from
  endpoint row envelopes obtain edge floor min(1,c/(max(M_i,M_j)+epsilon)).
  Require c>0 for strictly positive floors, not for basic row feasibility.
- Define the adaptive weight step as gate(proposal), prove nonnegativity,
  zero diagonal, symmetry under symmetric inputs, and row feasibility.
- Establish row/nonnegative invariants from the first completed step. Handle
  H0 (previous row feasibility at step zero, or start at/after step one) explicitly.
- Derive the actual off-diagonal scalar recurrence with its applied edge factor,
  not an arbitrary factor postulated in a hypothesis.
- If feasible after the main bridge compiles, compose with the existing upstream
  scalar freezing core under explicit drive-band hypotheses. Do not force this
  extension or claim it compiled if it remains a paper-level next step.

The main proof target is the gate/proposal bridge (floor form of Lemma 1(b,c)
plus correct first-step invariance), not closed-loop locking, delayed phases,
complex EMA correctness, selected-controller rate laws, or coupled stability.

## Adversarial plan (fixed before new test outcomes)

1. Exhibit a nonzero active step from a feasible nonnegative state, and a
   separate inactive/zero-row example. Check the claimed envelopes/floors exactly.
2. Drop previous row feasibility: a nonnegative oversized input and zero drive
   must defeat the claimed c-based proposal envelope, while the next gated state
   can still be feasible. Do not confuse these two conclusions.
3. Drop h>=0 or h<=1: obtain exact counterexamples to the proposal envelope.
4. Apply c/row as a total-real upper bound at row zero: this wrong statement
   must fail; the correct division-free theorem must remain meaningful there.
5. Replace the applied factor by a candidate scale on an inactive branch:
   exhibit a difference even with nonnegative symmetric zero-diagonal input.
6. Omit epsilon from the lower floor: use a valid globally active configuration
   with a local row exactly at capacity, preferably reached from a feasible
   previous state, and show the epsilon-free floor is too large.
7. Check capacity zero separately; do not assume a strictly positive factor floor
   there. Include positive-epsilon and zero-row boundaries.
8. Freshly compile positive sources plus known-false mathematical payloads.
   A dependency/import failure does not count as mathematical rejection.
9. Reject raw-compiling proof holes, extra axioms, and omitted theorem-footprint
   coverage. Scope the harness honestly to the closed supplied files; it is not
   a secure general Lean parser or a substitute for trusted receiving-seat CI.

No floating tolerance is allowed for formal/rational claims. If source-side
floating comparisons are added, preregister their finite scope and tolerance
before running them, and do not infer general float64 correctness.

## Delivery and boundaries

Preserve exact sources, raw logs and structured results outside disposable cache.
Deliver one numbered standalone Markdown with all critical new/imported proof
and checker code inline, reproduction commands, actual outcomes, limitations,
and requested independent checks. Re-extract/rerun it if feasible.

No remote write, inbox upload, registry promotion, main edit, frozen-authority
change, or bot contact is authorized. The owner handles uploads. Self-red-team
and compiler success are not independent approval, integration, or publication.
