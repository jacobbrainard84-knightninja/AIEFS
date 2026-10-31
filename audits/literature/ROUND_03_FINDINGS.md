# Literature Review — Round 3: The Cocycle Resolved, and a Registry Defect

**Round:** 3 · **Date:** 2026-10-30 · **Sources added:** 5 (total 33) · **Leads:** 3 resolved, 1 opened
**Registry:** [`SOURCES.csv`](SOURCES.csv) · **Leads:** [`LEADS.csv`](LEADS.csv) · **Prior:** [R1](ROUND_01_FINDINGS.md) · [R2](ROUND_02_FINDINGS.md)

---

## 0. Bottom line

Round 3 was scheduled to run one computation and close three leads. It closed the leads, and it
did **not** run the computation — because examining the construction showed the computation would
have been vacuous. Resolving that, and saying why, is the round's main result.

Along the way it turned up something larger than any citation: **five of the fourteen studies name
canonical entrypoints that exist nowhere in the repository.** Not moved, not renamed — absent from
the working tree and from all three archives. One of those is the entire AIEF 1.0–1.2 codebase,
which the registry carries as `Frozen` / `Controlled experimental result`.

---

## 1. F16 — Registry referential integrity: 5 of 14 studies cite entrypoints that do not exist

**[VERIFIED]** Re-runnable check (stdlib only, from the repository root):

```python
import csv, pathlib, glob
rows = list(csv.DictReader(open('registry/artifacts.csv', encoding='utf-8')))
worktree = {r['path'] for r in rows if r['container'] == 'worktree'}
for r in csv.DictReader(open('registry/studies.csv', encoding='utf-8')):
    eps = [e.strip() for e in r['canonical_entrypoints'].split(';') if e.strip()]
    miss_d = [e for e in eps if not (pathlib.Path(e).exists() or glob.glob(e))]
    miss_r = [e for e in eps if e not in worktree]
    if miss_d or miss_r:
        print(r['study_id'], 'missing-on-disk:', miss_d, '| not-in-artifacts:', miss_r)
```

Result:

| Study | Registry status | Unresolved canonical entrypoints |
|---|---|---|
| `AIEF_1_0_TO_1_2_FOUNDATIONAL` | **`Frozen`** / `Controlled experimental result` | `AIEF_1_0_*.py`, `AIEF_1_1_*.py`, `AIEF_1_2_*.py` — **zero files match** |
| `AIEF_1_4_TANGENT_AND_COCYCLE` | `Supported` | `aief_1_4_full_state_tangent_operator.py`, `aief_1_4_history_cocycle_test.py`, `aief_1_4_branch_tangent_comparison.py` |
| `AIEF_1_4_CONTROLLER_FIBER` | `Supported` | `aief_1_4_intertwining_controller.py`, `aief_1_4_fiber_coordinate_controller.py` |
| `AIEF_1_4_MATCHED_PHASE_ABLATION` | **`Frozen`** | `AIEF_1_4_driver_mechanism.py` |
| `AIEF_1_3_DISJOINT_100SEED` | **`Frozen`** | `AIEF_1_3_sensitivity_audit_updated.py`, `AIEF_1_3_persistence_mechanism_test_updated.py` |

**[VERIFIED]** None of them exists inside any of the three `.zip` archives either (member-name scan of
all three: `workspace-019ff402`, `workspace-019ff86e`, `aief_modular_platform_v1_analysis_v4.zip` —
zero hits). The unresolved set is **11 entrypoint tokens: 3 glob patterns plus 8 concrete
filenames**.\* They are not recoverable from anything the repository contains.

\* Three of the eight are in the tangent/cocycle study; a fourth, `AIEF_1_4_driver_mechanism.py`, is
listed with a `.py` extension in `studies.csv` while the on-disk driver directories suggest the work
may have lived in a directory form. Either way, no file with that name exists anywhere.

**[VERIFIED]** `ls | grep -cE '^AIEF_1_[012]_'` returns **0**. There is no AIEF 1.0, 1.1 or 1.2
script anywhere.

Three consequences, in increasing order of severity:

1. **`REPRODUCING.md` overstates the reproducible set.** It promises that studies can be re-run from
   canonical entrypoints. For five studies, the entrypoint does not exist, so the promise holds only
   if the *outputs* are taken as the evidence — which is a different and weaker claim.
2. **The Era-1 programme has no code.** `AIEF_1_0_TO_1_2_FOUNDATIONAL` is registered `Frozen`, but
   freezing implies a frozen artifact. What exists is a set of outputs and reports whose generative
   code is absent. That is an `Incomplete`-class provenance situation being labelled `Frozen`.
   This is not a mystery about what the work *was*: Era-1 sits squarely in the Kuramoto framework,
   and [LIT-0031] supplies the vocabulary it uses — order parameter, critical coupling,
   phase-locked versus incoherent regimes — without the repository ever citing it. So the gap is
   specific and closable: the code is missing, the intellectual lineage is not.
3. **My own Milestone 1 verifier missed this.** `audits/engineering/verify_inventory.py` passes
   gates 1-4 (conservation, `2,898` SHA-256 digests, vocabularies, Lean ledger); gate 5 needs `numpy`
   and could not run in this sandbox after the venv was lost. It checks conservation, SHA-256 digests, vocabulary, the Lean lock and the authority
   lock — but it never checks whether `studies.csv` references resolve. Gate 1 proves every
   *inventoried* row hashes correctly; it cannot detect a `study_id` pointing at a path that was
   never inventoried. That is a real gap in the Milestone 1 work, not a false alarm from this round.

**Proposed fix (for owner approval, not applied):**
- Demote `AIEF_1_0_TO_1_2_FOUNDATIONAL` from `Frozen` to `Incomplete` until the code is restored, or
  add a `provenance_complete = false` field.
- Correct the ten stale entrypoints to the scripts that actually produce the outputs (for the
  tangent/cocycle study, `AIEF_1_4_frozen_driver_cocycle_analysis.py` is present and does exist).
- Add a sixth gate to `verify_inventory.py`: every `canonical_entrypoints` token resolves to a
  `path` in `artifacts.csv` **and** exists on disk. This is a ten-line addition and would have
  caught all five cases.

---

## 2. F17 — F10 resolved: the cocycle question was the wrong question

Round 2's F10 asked whether the AIEF history operator satisfies Arnold's composition law
$\Phi(t+s,\omega) = \Phi(t,\theta_s\omega)\Phi(s,\omega)$.

**[VERIFIED] The composition law is automatic and testing it would prove nothing.** The evidence
artifact is `aief_1_4_frozen_driver_cocycle/frozen_cocycle_propagator.csv` beside
`frozen_cocycle_matrices.npz`. The "propagator" at step $n$ is the time-ordered product
$K_{n-1}\cdots K_0$ of the stored matrices. For *any* sequence of matrices, associativity gives
$\Phi(n_2,n_0) = \Phi(n_2,n_1)\Phi(n_1,n_0)$. It cannot fail. Round 3 declined to run a test that
was guaranteed to pass, and reports that instead of reporting a green tick.

**The non-trivial condition is branch preservation.** A product of Jacobians equals the derivative of
the composed map only while the linearisation remains on one smooth branch; across a winner switch
the product is a patch of two different derivatives and means nothing. Here the evidence is
decisive and favourable. From `frozen_driver_cocycle_report.txt`:

> `Winner-signature changes: 0`
> `All selected classical Jacobians available: True`
> `Cocycle steps: 32000` · `Final base replay exact: True` · `Final base replay maximum error: 0`

Zero winner switches over 32,000 steps, with the certified branch-radius ratio
$\chi_n = \lVert\delta x_n\rVert/\rho(x_n)$ tracked at every step. So on this window the
linearisation is genuine, and the transition-matrix reading of "cocycle" is sound. This is exactly
the structure the piecewise-smooth and lexicographic-derivative literature describes [LIT-0020],
[LIT-0021], [LIT-0033]: the derivative exists branchwise, and validity is a condition on staying on
a branch.

**The name is still too strong.** The script's own docstring:

> *"This is not the full delayed-state variational equation. In particular it sets delta R_n = 0.
> Phase, history, and EMA feedback are downstream Stage B work if this reduced cocycle is
> insufficient."*

And the report restates it: *"This is the frozen-driver weight subsystem: delta R is set to zero."*

So what exists is a **frozen-driver, weight-sector, 3×3 $K_3$ cocycle**. The study title —
*"Full-State Tangent Operator & Exact History-Cocycle Dynamics"* — claims the delayed-state history
cocycle that the code explicitly defers to a Stage B that was never done.

**Resolution of F10:**

| Question | Answer |
|---|---|
| Does the operator satisfy the cocycle composition law? | Yes, trivially — it is a product of transition matrices. The question was ill-posed. |
| Is the linearisation valid? | Yes on the audited window: 0 winner-signature changes in 32,000 steps, branch radius certified. |
| Is it the *history* cocycle? | **No.** δR = 0; history and phase feedback are excluded by construction. |
| Is "exact" supportable? | Not for the full state. For the reduced weight sector on a no-switch window, yes. |

**Recommendation:** keep the word "cocycle" (it is correct for a non-autonomous linear propagator),
drop or scope "exact history", and record that Stage B was not performed. That is a one-line registry
change that removes a real overclaim — and it is the kind of thing that survives a specialist reader
where the current title does not.

---

## 3. F18 — `REJ-LOCK-03` now has a structural replacement

**[INFERRED]** The rejected claim: *mature oscillator frequencies satisfy the bare algebraic zero-sum
$\omega_i + G_i = 0$.* It was rejected numerically. The literature says the functional form was
wrong, which is stronger than saying the numbers disagreed.

For delay-coupled oscillator networks, phase-locked states are governed by a transcendendental
condition in the delay, and the collective frequency must be solved for rather than checked as an
algebraic sum. Earl & Strogatz established the stability criterion for phase-locked states in exactly
this network class [LIT-0030]; Park & Lefebvre give implicit equations for the global frequency
$\Omega$ and the stability eigenvalues [LIT-0018]; Jolly et al. extend the treatment to multiple and
state-dependent delays [LIT-0028].

So `REJ-LOCK-03` can be restated: *an algebraic zero-sum is the wrong functional form for a
delay-coupled network; locking requires solving an implicit condition in the delay.* That converts a
numerical negative into a structural one.

**Caveat on the citation, stated plainly:** [LIT-0030]'s record is `VERIFIED_METADATA`, and unlike
most rows its *content* description comes from how four independent citing works characterise it,
not from its own abstract. The `notes` field says so. Round 4 should open the abstract.

---

## 4. F19 — The split-state ablation inherits a discontinuity it does not record

**[INFERRED]** `AIEF_1_4_SPLIT_STATE_ABLATION` resets components at a split time and compares
post-split recovery across arms.

In a delay system the state is the history segment [LIT-0010], and the standard numerical theory is
organised around the fact that a DDE solution's derivative carries discontinuities that propagate
and smooth: an initial history with a derivative jump produces a jump in $\dot x$ on the first step,
in $\ddot x$ on the second, and so on [LIT-0029].

An ablation applied *at* the split injects a new first-order discontinuity into the history at that
moment. Two consequences the registry does not currently state:

1. The post-split trajectory is not simply "the same system with one component reset" — it is a
   system with a modified discontinuity structure.
2. If the split is implemented identically across arms this is harmless and common to all
   conditions. If it is not — for example if one arm's reset changes a derivative at a different
   order — the arms are not comparable.

**Action item:** state the discontinuity order induced by the split and confirm it is identical
across arms. This is cheap (it is a property of the code, not a new experiment) and it is the kind
of detail that decides whether a reviewer accepts a split-time comparison.

---

## 5. F20 — Wild bootstrap: F14 confirmed, caveat noted, action still none

**[VERIFIED]** [LIT-0032] resolves `LEAD-0005` and states the failure modes precisely: the CRVE
"rule of 42" *"is not true for unbalanced clusters"*, and the wild cluster bootstrap *"fails when a
small number of clusters is treated."*

Neither applies. AIEF seeds are exchangeable and **every seed is treated in every arm**, so the
treated fraction is 1 and cluster sizes are equal by construction.

**Round 2's F14 stands unchanged: no remedial work on `EMP-AIEF13-01`'s interval.** The transferable
caution is narrow and worth recording: if a future design ever ablates a *subset* of seeds, this
paper says the interval construction must change at that moment.

---

## 6. F21 — `CF03` is confirmed as current best practice

**[VERIFIED]** [LIT-0033] is the applied demonstration Round 2 asked for. Same structure as the CF
block — a nonsmooth map, a Jacobian that does not exist at the non-differentiable points, and a
choice between hybridising into smooth modes or using the lexicographic derivative. The authors take
the lexicographic route, *"avoid hybridization, eliminate mode transition computations"*, and report
*"accuracy on average by 50%, compared to hybrid algorithms."*

Two implications. `CF03`'s approach is current practice in a verified-systems venue, not a local
convention. And the AIEF audit's careful winner-signature bookkeeping is the *hybridisation* the
paper argues is avoidable — worth knowing before the CF block is rewritten, because it suggests the
bookkeeping can be replaced by a lexicographic computation rather than maintained forever.

---

## 7. Coverage

| Measure | R1 | R2 | **R3** |
|---|---|---|---|
| Sources | 16 | 28 | **33** |
| Claims with a source | 19/43 | 22/43 | **24/43** |
| Studies with a source | 9/14 | 11/14 | **11/14** |
| Domains | 7/8 | 8/8 | **8/8** |
| Open leads | 3 | 3 | **1** |

Stance mix this round: 3 `SUPPORTS` / 1 `METHOD` / 1 `CONTEXT` / 1 `CAUTION`.

Unmapped now: 6 `CF` claims (`CF04`, `CF07`, `CF09`–`CF12` — correctly unmapped, they are linear
algebra, spectral invariance, asymptotics and open conjectures, not nonsmooth problems), 12 retired
`S` claims (deliberately unmapped), `EMP-AIEF14-03` (still no anchor — see below), and three studies
(`HISTORICAL_PROJECT_ORIGINS`, `AIEF_1_4_PIVOT_PILOT`, `AIEF_1_4_PROPOSAL_EQUALIZATION`).

**On `EMP-AIEF14-03`:** Round 3 could not anchor the $\rho$-sweep claim and will not force a
citation onto it. The claim — that separating fixed physical horizons from normalised EMA horizons
resolves horizon-scaling confounding — is a design argument about timescale normalisation, and the
literature that addresses it is the multiple-timescale / dimensionless-grouping material, which is
general enough that citing it would be decorative. Recorded as a gap.

**New lead:** `LEAD-0007` — Bellen, Guglielmi, Maset & Zennaro, *Recent trends in the numerical
solution of retarded functional differential equations*, Acta Numerica 18:1–110 (2009). Seen only as
a reference inside a Springer encyclopedia entry while verifying [LIT-0029]. It would supersede
[LIT-0029] as the citation of record for method-of-steps detail; not opened, so not promoted.

---

## 8. Proposed registry amendments — **for owner approval, not applied**

| Target | Proposed change | Basis |
|---|---|---|
| `AIEF_1_0_TO_1_2_FOUNDATIONAL` | Demote `Frozen` → `Incomplete`, or add `provenance_complete = false`; record that no Era-1 code exists | F16 |
| `AIEF_1_4_TANGENT_AND_COCYCLE` | Correct the three stale entrypoints to `AIEF_1_4_frozen_driver_cocycle_analysis.py`; **scope the title**: frozen-driver weight-sector cocycle, δR = 0, Stage B not performed | F16, F17 |
| `AIEF_1_4_CONTROLLER_FIBER` | Correct the two stale entrypoints | F16 |
| `AIEF_1_4_MATCHED_PHASE_ABLATION` | Correct `AIEF_1_4_driver_mechanism.py` | F16 |
| `AIEF_1_3_DISJOINT_100SEED` | Correct the two stale `_updated` entrypoints | F16 |
| `REJ-LOCK-03` | Restate as a functional-form error: locking requires an implicit delay condition, not an algebraic sum | [LIT-0030], [LIT-0018], [LIT-0028] |
| `AIEF_1_4_SPLIT_STATE_ABLATION` | Record the induced discontinuity order and confirm it is common across arms | [LIT-0029], [LIT-0010] |
| `EMP-AIEF13-01/02` | Add that the treated fraction is 1, which is why the few-treated-cluster failure mode does not apply | [LIT-0032] |
| `CF01`–`CF03`, `CF05` | Note that lexicographic differentiation is current practice in verified reachability, with a 50% accuracy gain over hybridisation | [LIT-0033] |
| `verify_inventory.py` | Add gate 6: entrypoint referential integrity | F16 |

---

## 9. What Round 3 did not do

- Did not run the cocycle composition test. **Deliberate**: it is automatic, and running it would
  have produced a meaningless pass. See §2.
- Did not open [LIT-0030]'s abstract; its content description is second-hand and labelled as such.
- Did not repair any registry row. Everything above is proposed, not applied.
- Did not anchor `EMP-AIEF14-03`, and did not manufacture a citation to cover the gap.
- Did not open `LEAD-0007`.
