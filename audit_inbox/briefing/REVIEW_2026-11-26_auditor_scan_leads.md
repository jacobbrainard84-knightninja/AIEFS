# Auditor Seat 002 review of PLAN_2026-11-25_scan_leads.md (H8–H15) and the second-pass deltas (H16–H19)

_Written 2026-11-26 00:40 GMT by Auditor Seat 002. Reviewed: plan at audit-inbox `cd2dd8d`, the STATE.md second-pass row at `791b620`, and Researcher 001's box scan notes (second pass, section C). Checked against `origin/main` @ `7865ab1` (read-only) and the pinned Mathlib checkout (rev `0df444a`, toolchain v4.33.1), grep only. **Review only:** nothing was built, installed, branched or implemented. The engine was read with `git show` (sha256 `ca4593fd…acdede`, matches the pin) and not edited. The plan, STATE.md and other notes are not edited; this is a new add-only file._

Labels used here: **VERIFIED** means I read it in the repo or pinned Mathlib this session. **READ, NOT BUILT** means I reasoned from source text and did not compile. **UNVERIFIED** means not checked.

## Summary verdicts

| Item | Verdict | One line |
|---|---|---|
| H8 RESEARCH_LEADS | **AGREE + CHANGE** | Good, with the second-pass edits. Add a verification-level tag on every entry. Carty arithmetic re-checked. |
| H9 DiscreteGronwall | **CHANGE** | (a) is infeasible as written (AIEFGateCore cannot import AIEFFreezeCore) and close to decorative. Two of the three planted mutants are wrong. Keep (b). |
| H10 gate property tests | **CHANGE** | Useful. Use the stdlib fallback, not Hypothesis. Model the global `pre_violation` trigger. Add the ε-band witness. List existing coverage first. |
| H11 Arb E22 | **DROP** | E22 already ran the exact-rational path. The step has no sin/cos, so Arb adds nothing. A new rule after seeing v1 is post hoc. |
| H12 Hebbian contrast | **CHANGE** | Fine as a note. The candidate "EMA rate → 1" regime is degenerate in the engine (R ≡ 1 or R frozen). Drop the "not a gradient" Lean lemma unless it is stated precisely. |
| H13 discrete Halanay | **CHANGE** | Feasible at our pin. Fix the statement. It has no engine consumer yet, so a written target is required before Lean work. Stay in AIEFGateCore. |
| H14 LeanForControl/LeanCert | **CHANGE → DEFER** | No current target needs LeanCert (0.454286 = 159/350 and 3/7 are rational, DelayRoots is algebra). The marker-grep control is mis-predicted. |
| H15 reuse decision | **AGREE (DEFER)** | Only after H12 shows value. Recommend cite-only by default. |
| H16 Banach contraction of B | **CHANGE** | The scalar gate-inactive version is already implied by `Freeze.upper_geom` (plus its lower twin). The binding-gate matrix version may be false (UNVERIFIED). The λ(1−h)=1 mutant tests Mathlib, not us. |
| H17 Real.Angle bridge | **CHANGE** | The proposed mutant cannot fail, because coercion to `Real.Angle` forgets the representative. Bridge to `toIcoMod` instead. Add the float `np.mod` = 2π witness. |
| H18 Matrix.IsIrreducible | **DROP (for now)** | Vocabulary with no consumer, and no Perron–Frobenius at our pin. For symmetric support, `SimpleGraph.Connected` is the matching notion. |
| H19 LeanBlueprint | **DEFER (owner call)** | Process tooling (TeX/Python in CI). Not worth usage this week. Revisit after the reset if the owner wants it. |

## Item-by-item

### H8. RESEARCH_LEADS additions: AGREE, with the second-pass changes
- AGREE on content and on the planted-misstatement control. It is the right control for a literature item.
- **CHANGE:** every entry gets a verification-level tag: `full text read` / `abstract` / `third-party review (zbMATH/MaRDI)` / `metadata only` / `UNVERIFIED`. Wang–Dong must read "content per zbMATH review; full text not read; coupling convergence not stated in the review". Cho–Ha–Kang stays UNVERIFIED with no EMA analogy (agree).
- Carty constants: I re-did the arithmetic. P(24,11) = 99,638,080,819,200 ≈ 9.96e13; 2^11·P ≈ 2.04e17; ×11 ≈ 2.24e18. **VERIFIED arithmetic**, which matches R001. The reading of Lemma 2.3 is R001's; I did not re-read the paper (UNVERIFIED by me). Record it as "a lower bound on c under η > 2, by our arithmetic".
- Extra planted-error option for the review copy: "Ha–Lee–Li–Park is in our time-scale regime". Second pass says it is the opposite regime, so the review must catch that.
- Author R001, auditor me. No PR (audit-inbox). Agree.

### H9. DiscreteGronwall cross-check: CHANGE
- **(a) is infeasible as written.** `lean/AIEFGateCore/AIEFGateCore/Freeze.lean` (main) says AIEFGateCore may not depend on AIEFFreezeCore, because `check_lean_gate.sh` step 2 forbids path dependencies. The five statements are restated there, and `test_lean_gate_p4b.py` checks the text against FreezeCore. **VERIFIED.** So "type defeq to `upper_geom`, imported not copied" can only target `AIEFGate.Freeze.upper_geom`. Do that in both directions (`example : <new stmt> := AIEFGate.Freeze.upper_geom …` and the converse), and rely on the existing p4b text check for the link to FreezeCore.
- **(a) is close to decorative.** The kernel already checked `upper_geom`. A second proof by a different route adds little assurance. Keep it as a short corollary of `discrete_gronwall_prod_general` with `c n = ρ`, `b n = β` (exists at our pin, `Mathlib/Analysis/ODE/DiscreteGronwall.lean` L44, **VERIFIED**). Do not treat it as a deliverable in its own right.
- **Use the right Mathlib lemma.** `discrete_gronwall` (L73) is the exponential *growth* form `(1 + c n)`. It cannot give ρ < 1 decay. Only the product form fits.
- **Two of the three planted mutants are mis-predicted (READ, NOT BUILT):**
  - "Drop `0 ≤ u n₀`": `upper_geom` has no such hypothesis, and `prod_general` needs only `0 ≤ c n`. There is nothing to drop.
  - "c > 1": `upper_geom`'s proof uses ρ ≥ 0 and ρ ≠ 1 only (`field_simp` needs `1 − ρ ≠ 0`; the induction needs `0 ≤ ρ`). Its conclusion holds for ρ > 1 too, and ρ < 1 is needed only in `eventually_off/on`. A ρ > 1 mutant of `upper_geom` should **survive**, and that is a finding (the hypothesis is stronger than needed), not a gate failure.
  - The ρ = 1 mutant should be **killed**: Lean's `β/0 = 0` makes the claim `x n ≤ x 0`, which is false for β > 0.
  - **Rule to add to every Lean item:** predeclare kill/survive for each mutant in the first commit. A surviving mutant is reported, never deleted.
- **(b) is the real value:** n-step envelopes with time-varying drive, in the engine form `B⁺ = factor · max 0 ((1 − γdt) B + dt·D)` (`WeightUpdate.stepM_scalar_recurrence`). The `max 0` clamp needs B ≥ 0 and a nonnegative right-hand side to stay an upper bound. State it.
- **Engine-witness control:** instantiate at `pE` (dt = 1/100, γ = 3/200, so ρ = 1 − γdt = 19997/20000), as the existing `onGap_*` lemmas do. That ties the theorem to the frozen parameters rather than a free-floating recurrence.
- Author me, auditor R001. Accepted. Merge with H16 on one branch (see H16).

### H10. Gate property tests vs a Fraction oracle: CHANGE
- **Owner call:** Hypothesis (MPL-2.0). **I recommend declining it.** The seeded stdlib fallback is enough for a deterministic CI gate. Hypothesis, mpmath and python-flint are not installed on the box (**VERIFIED**, import probe only).
- **The oracle must model the engine's control flow, not just the formula.** Projection runs only if `pre_violation` (`g_min_pre < δ`, i.e. some row sum > cap). Then `scale = min(1, cap/(row_sum_pre + scale_epsilon))` (engine L811, **VERIFIED**), followed by `np.minimum.outer`, a zeroed diagonal and the post-check `g_min < δ − FROZEN_GAP_TOL` raise. The plan's "L803–813" is the right block.
- **Missed adversarial witness (ε-band).** A mutant that always projects agrees with the engine almost everywhere. It differs only when every row sum is ≤ cap and some row has `cap − ε < row_sum ≤ cap`, where `scale < 1`. With ε = 1e-12 random tests will essentially never hit that band. A fixed witness row in it must kill the "always project" mutant.
- Row sum ≤ cap: after projection, `Σ_j min(s_i,s_j) B_ij ≤ s_i·rowsum = cap·rowsum/(rowsum+ε) < cap` on binding rows. The property should hold (READ, NOT BUILT). Keep it, with the +ε slack only on the float side.
- **List existing coverage first.** `GateMap.lean`/`Capacity.lean`, `lean_gate_crosscheck_v1.py` and the W1–W5 Fraction witnesses already exist. The README must say what H10 adds: generalization, the ε-band, ties, and float vs exact at ties. Otherwise it duplicates existing work.
- The spillover measurement stays an observation. Agree.
- Author R001, auditor me (I open the PR). Accepted.

### H11. Arb/python-flint E22 residual: DROP
- ERRATA E22 on main (**VERIFIED**, read) already evaluated "the same one-step gate map … in exact rational arithmetic on the engine's float64 inputs". Exact multiplier: 0.9987382469602354, which matches the branch formula to 4.04e-13. The float error is reproduced by exact arithmetic on the rounded input fl(B+δH) (2.63e-8, the perturbation's representation error).
- The step is rational given R. There is no sin/cos in the B update; R is an input. So ball arithmetic cannot say anything that `Fraction` hasn't already said exactly.
- E22 failed on a predeclared threshold (2.170e-10 vs 2.1e-10) at a branch-window edge, not on an open rounding question. E22 itself says that adopting a new rule after seeing v1 is post hoc.
- If the owner wants that closed, the honest route is E22's own suggestion: a **v2 rule, predeclared and independently reviewed before it runs**, with stdlib Fraction and no new dependency. That is a different item, and it needs the owner's go-ahead. AUD-RATELAW stays UNEXPLAINED.
- This removes one of the items proposed for me to author, and removes the python-flint/mpmath owner question.

### H12. Hebbian contrast note: CHANGE
- AGREE on a note with citation only, no copying, and adding Wang–Dong as the second contrast target.
- **The candidate regime is degenerate.** The engine EMA is `acc ← α·acc + (1−α)·z_inst`, `R = |acc|` (**VERIFIED**). At (1−α) → 1, R = |z_inst| = 1 for every edge, so the drive is constant and decoupled from the phases. At α → 1, R is frozen at its initial value. In both limits the weight law stops being Hebbian at all, so a joint energy there says nothing about the obstruction. The note should look for a non-degenerate restricted regime (τ = 0, fixed α ∈ (0,1), gate inactive) or say none was found.
- **Drop the optional "the drive is not ∂E of any energy" Lean lemma** unless it fixes the state space, the variables and the class of E. Stated loosely it is either trivially true or unprovable. A numerical counterexample (candidate energy increases on the engine copy) is the right red team, as planned.
- Author R001, auditor me. Accepted.

### H13. Discrete Halanay in Lean: CHANGE
- Feasible at our pin: elementary real induction, no new Mathlib needed (READ, NOT BUILT).
- **Fix the statement before work starts:**
  - Define u on the initial window `0..d`, or quantify n ≥ d.
  - Use `M := max_{k ≤ d} u k` and conclude `u n ≤ M · (a+b)^(n / (d+1))` (Nat floor division). That is the easy, standard form.
  - Treat the sharper `ρ^n` with `ρ^(d+1) = a ρ^d + b` as a separate, optional theorem.
  - Production d = round(τ/dt) = 50 (engine `delay_steps`, **VERIFIED**).
- **It is decorative until it has a consumer.** The engine's B recurrence has no delay. The delay is in the phases, and a Halanay hypothesis on a phase quantity is essentially O1, which is unproven. Require a short written derivation (paper only) naming the engine quantity that would satisfy `u(n+1) ≤ a u n + b max …`, under which assumptions, and roughly what a + b is at `pE`. If the margin is about γdt = 1.5e-4, say so; that is a slow but honest ρ.
- R001's "Carty has no usable constants" edit is fine. It does **not** show that Halanay will give usable constants; don't word it as "strengthens the case" until the consumer exists.
- Red team: the a + b = 1 constant-sequence counterexample (¬conclusion proved), the a + b ≤ 1 mutant (killed), predeclared kill/survive per mutant, and a Fraction check of the bound on sampled sequences including an adversarial one that sits on the bound for d steps.
- **Location: AIEFGateCore, not a new `AIEFDelayCore`.** That avoids a CI job row and an owner decision.
- Novelty: "first in Lean as far as searched" only. I did not run the literature check (UNVERIFIED).
- Author me, auditor R001. Accepted, after H9/H16 and only once the consumer paragraph is written and agreed.

### H14. LeanForControl / LeanCert evaluation: CHANGE → DEFER
- **No current target needs LeanCert.** 0.454286 is 159/350 and 3/7 is rational (`freq_predictor.log`, `research/freezing/REPORT.md`, `EngineWitness.lean`; **VERIFIED**). `norm_num` already proves these in the kernel. DelayRoots is pure polynomial/complex algebra and is already proven. Revisit LeanCert only when a transcendental interval bound (sin/cos/exp at a specific value) is actually needed.
- **The marker-grep control is mis-predicted.** A tactic that elaborates to native evaluation need not leave the literal `native_decide` in user source, so a source grep (`test_lean_gate_p5.py` L130 list, `check_lean_gate.sh` markers step) may well **not** flag it. The control that should catch it is `#print axioms` / axiom-audit (`Lean.ofReduceBool` is outside the allow-list propext/Classical.choice/Quot.sound; the `lean.yml` allow-list is **VERIFIED**). Predeclare: grep may miss (report a GAP if it does), and axiom-audit must catch.
- Drop lasalle-lean (agree with R001's second pass).
- **Owner calls:** Lean v4.33.1 → v4.36.0 (**recommend: no**, not for an evaluation), LeanCert trust mode (**recommend: defer**, no target), and the Architect dependency (**recommend: defer**).
- Author R001, auditor me. Accepted, deferred.

### H15. LeanPool / kuramoto-lean reuse decision: AGREE (DEFER)
- Gated on H12 showing value. The default recommendation is **cite only**. Vendoring Apache-2.0/MIT code needs NOTICE, attribution headers and a toolchain match (they target 4.36), and all of that is the owner's call. Author R001, auditor me.

### H16. Banach/contraction convergence of B: CHANGE
- `ContractingWith` (L40) and `fixedPoint_isFixedPt` / `dist_fixedPoint_le` / `apriori_dist_iterate_fixedPoint_le` / `tendsto_iterate_fixedPoint` (L278/284/293/300) exist at our pin (**VERIFIED**).
- **The scalar, gate-inactive, frozen-R case is already on main in substance.** For the affine map with equality, `upper_geom` and its lower twin give `x n − U = ρ^n (x 0 − U)`: existence, uniqueness, convergence and an explicit rate, with ρ = 19997/20000 at `pE`. Banach restates this. The `max 0` clamp is 1-Lipschitz, so it doesn't change the constant. Adding it is fine only as a short corollary, and NORTH_STAR row 7 must not be advertised as newly closed by it.
- **The case that would matter is the binding-gate matrix map, and it may be false (UNVERIFIED).** When the gate binds, the factor `min(s_i, s_j)` with `s_i = cap/(rowsum_i + ε)` depends on B. That is row normalization, whose ℓ1 Lipschitz bound is about 2·cap/rowsum ≈ 2 near the cap (rough estimate, not proven). So `(1 − γdt) × (≈2)` need not be < 1, and a "fixed gate factor λ" hides exactly that dependence. E22's local multiplier 0.99874 on one fiber suggests local contraction there; it is not a global bound.
  - **First step, before any Lean:** a numeric adversarial probe on an engine copy for two binding-region states whose images are farther apart than the states.
  - If the probe finds them, the matrix contraction claim is dropped and that is recorded.
  - If it finds none, that is "not found", not proof.
- **The λ(1−h) = 1 mutant is weak.** It fails only because Mathlib's definition requires K < 1; it tests Mathlib, not us. Replace or add:
  - A wrong-variant control: clamp order swapped, i.e. `max 0` outside the factor vs inside, or the gate applied before decay. The statement-to-`stepM` equality must reject it.
  - The `pE` engine witness.
  - An adversarial witness at `γdt ≥ 1`. That is engine-legal (the engine validates only γ ≥ 0; `WeightUpdate.lean` says so), but the theorem's hypotheses must exclude it.
- Frozen R does not hold in the engine (R depends on phases, which depend on B). The module header must say "conditional, not O1".
- **Merge with H9(b) on one branch** (`research/h9-h16-b-recurrence`, two modules), since they share the recurrence and the `pE` witness. Author me, auditor R001.

### H17. Real.Angle bridge for wrapPhase: CHANGE
- **The proposed mutant cannot fail.** `((wrapPhase t : ℝ) : Real.Angle) = (t : Real.Angle)` is true for *any* representative choice, because the coercion to the quotient forgets which one. A (−π, π] wrap satisfies it too. That makes the bridge a restatement of `phasor_wrap` with no discriminating power.
- Our `wrapPhase t = t − ⌊t/2π⌋·2π` is the **[0, 2π)** convention (**VERIFIED**, `PhaseIncrement.lean` L47–48; the plan's "L64" is `phasor_wrap`). The engine uses `np.mod(…, 2π)` (L836, **VERIFIED**).
- **Bridge to Mathlib's `toIcoMod two_pi_pos 0 t`** (`coe_toIcoMod` exists, `Angle.lean` L417, **VERIFIED**). Prove `wrapPhase t = toIcoMod two_pi_pos 0 t` plus `0 ≤ wrapPhase t < 2π`. Then a (−π, π] mutant (`toIocMod two_pi_pos (−π)`) fails on the witness t = −π/2 (3π/2 vs −π/2) (READ, NOT BUILT).
- **Missed float witness (VERIFIED on box numpy):** `np.mod(-1e-20, 2*np.pi)` returns exactly `6.283185307179586 == 2*np.pi`. The engine can store θ = 2π in float64, which is outside the real-number [0, 2π) range Lean proves. The phasor is unaffected, so the impact is probably nil. Whether it ever occurs in production runs is **UNEXPLAINED/UNVERIFIED**. Record it as a float-vs-real gap and as a fixed witness in the Python cross-check.
- Author: **R001** (small, keeps the split balanced), auditor me.

### H18. Matrix.IsIrreducible support lemma: DROP for now
- `Matrix.IsIrreducible`, `IsPrimitive` and `isIrreducible_iff_exists_pow_pos` exist at our pin (`Irreducible/Defs.lean` L82/88/159, **VERIFIED**). There is no Perron–Frobenius, so nothing downstream consumes it.
- It is a directed-graph notion. The frozen B support is symmetric, and Wang–Dong's hypothesis is connected undirected, which is `SimpleGraph.Connected` in Mathlib. Proving irreducibility of a specific run's support is a per-run computed fact, and checking a 12×12 by `decide` is a performance and `native_decide` temptation.
- Revisit only when a theorem needs connectivity as a hypothesis.

### H19. LeanBlueprint: DEFER (owner call)
- Process value only. It needs TeX/Python tooling plus a CI job, which is owner decision 1 (tooling) and 2 (CI rule change). Not worth usage before the Fri 2026-11-27 19:02 GMT reset. A cheaper interim: a script-free Markdown table of NORTH_STAR steps with Lean declaration names, checked by an existing-style text test. That is optional and needs no owner call.

## Author / auditor split (settled proposal; non-author audits, non-author opens the PR, owner merges)

| Item | Author | Auditor (opens PR) |
|---|---|---|
| H8 | Researcher 001 | Auditor Seat 002 (no PR; audit-inbox) |
| H9(b) + H16 (one branch) | Auditor Seat 002 | Researcher 001 |
| H10 | Researcher 001 | Auditor Seat 002 |
| H12 | Researcher 001 | Auditor Seat 002 |
| H13 | Auditor Seat 002 | Researcher 001 |
| H17 | Researcher 001 | Auditor Seat 002 |
| H14, H15 (deferred) | Researcher 001 | Auditor Seat 002 |
| H11, H18 | dropped | none |
| H19 | owner call | none |

Change from R001's proposal: H11 is dropped (so I author H9 + H16 + H13), and H17 goes to R001.

## Sequence and usage
Usage is past this week's Wednesday soft stop. Suggested order once the owner gives the usage go-ahead:
1. H8.
2. H9(b) + H16, scalar parts and the binding-gate probe first.
3. H17 (parallel).
4. H10 (stdlib).
5. H12.
6. H13, only after its consumer paragraph is agreed.

H14/H15/H19 wait on owner decisions. None of these touches `registry/claims.csv`, ERRATA, pinned files or the engine.

## Owner calls (flagged; recommendations only, not decisions)
- [ ] Usage go-ahead for any implementation.
- [ ] Hypothesis (H10). **Recommend decline** (stdlib fallback).
- [ ] python-flint/mpmath (H11). **Moot** if H11 is dropped.
- [ ] Lean v4.33.1 → v4.36.0. **Recommend no** for now.
- [ ] LeanCert kernel-trust mode + Architect. **Recommend defer** (no target).
- [ ] Vendoring LeanPool/kuramoto-lean (H15). **Recommend cite-only.**
- [ ] LeanBlueprint tooling + CI job (H19). **Recommend defer.**
- [ ] A new Lean project for H13. **Recommend no** (use AIEFGateCore).
- [ ] Any ledger/claims wording from these items.
- [ ] (Separate, if wanted) an E22 v2 predeclared rule, to be reviewed before it runs.

## Missed leads and red-team controls (added)
1. **Predeclared kill/survive per mutant** in every Lean item's first commit. Survivors are findings (H9's ρ > 1 mutant is the worked example).
2. **ε-band adversarial witness** for the gate trigger (H10).
3. **Float θ = 2π witness** from `np.mod` (H17). UNEXPLAINED whether it occurs in runs.
4. **Binding-gate non-contraction probe** before any matrix contraction claim (H16).
5. **Axiom-audit, not grep, as the native-evaluation control** (H14).
6. **`pE` engine-witness instantiation** and a statement-equality check against `stepM` for every new B-recurrence theorem, so the results are about the engine form, not a free-floating recurrence.
7. The **γdt ≥ 1, engine-legal but uncovered** case is stated as excluded in every new theorem.

## Top concerns
1. **H16 as drafted mostly re-proves main.** The version that would matter (binding gate) may be false, so it must be probed before anyone writes Lean or mentions NORTH_STAR row 7.
2. **Several planned red-team controls cannot fail:** H17's mutant, H9's "drop 0 ≤ u n₀" and "c > 1" mutants, H16's λ(1−h) = 1 mutant, and H14's marker grep. Controls that cannot say no are decorative. Fix them before the work starts, not after.
3. **H11 and H14's LeanCert half spend owner decisions and new dependencies on questions already answered** (E22's exact path; rational constants provable by `norm_num`). Drop or defer them so the owner's decisions go to items with a real target.
