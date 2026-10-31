# Remote-content sweep against the literature inbox's open questions

- **Agent:** Arena.ai Agent Mode (coding agent)
- **Date:** 2026-10-31 (Atlantic/Reykjavik, UTC+0)
- **Reviewed:** all 11 remote branches. Primary: `origin/main` @ `a991b46`, `origin/integration/round5` @ `893e0b6`, open PR #1. Local base: `arena/d4a487cc-aiefs` @ `e597504`.
- **Scope:** (a) every branch's tree, (b) open PR #1 and its checks, (c) `ERRATA_2026-10-28.md` E1–E13, (d) `AI Agent Audits/` (149 files), (e) `registry/` comparison across branches, (f) `tools/ci/*`.
- **Status:** UNVERIFIED INPUT per `README.md` rule 3. Nothing here changes the repo; all of it is checkable from the citations.

---

## 0. Why this file exists

Five literature rounds on `arena/d4a487cc-aiefs` left a set of specific, checkable open questions
(F16 entrypoints, F23 Lean generality, F17 Stage B, registry currency). This note asks one question
of the remote: **does any of it already answer them?** Several do. Two answers contradict my own
published work, and I have written those up as corrections, not omissions.

---

## 1. Answered: the "phantom entrypoints" were mostly stale names

**Question (rounds 3–5).** Five studies name `canonical_entrypoints` that exist nowhere. Is the
capability gone, or the name wrong?

**Answer: for two of the five, the name is wrong and both script and outputs exist.**

| Registry name | Reality |
|---|---|
| `aief_1_4_intertwining_controller.py` | **`AIEF_1_4_intertwining_controller_analysis.py`** (case + `_analysis` suffix), plus committed run outputs in `aief_1_4_intertwining_controller/`, `aief_1_4_intertwining_controller 01/`, `aief_1_4_intertwining_controller 02/` — 34 paths, present on **all 11 branches** including `main` |
| `AIEF_1_3_sensitivity_audit_updated.py`, `AIEF_1_3_persistence_mechanism_test_updated.py` | **`AIEF_1_3_falsification_updated.py`** (869 lines) is the five-condition simulator: `CONDITIONS = ("baseline","shuffle_R","no_delay","no_mu","no_gap")` at line 85; the past-resonance → future-persistence windows are its output. Companion `AIEF_1_3_falsification.py` (392 lines) is the earlier version. **Neither is registered in `registry/studies.csv` at all.** |

The `falsification_updated.py` finding is the more serious of the two. It is the primary
data-generating script for AIEF-1.3 — the thing the paired-statistics script consumes — and the
registry names two scripts that do not exist while naming the real one nowhere.

**Still genuinely absent on every branch** (`git ls-tree` exact-basename search, all 11 refs):
`aief_1_4_fiber_coordinate_controller.py`, `AIEF_1_4_driver_mechanism.py`, and any
`AIEF_1_0_*` / `AIEF_1_1_*` / `AIEF_1_2_*`.

---

## 2. Answered: the Lean generalization I recommended has already been done — better than I asked

**Question (round 1 F4, round 4 F23).** `LEAN-CF-01` fixes `C_{2,7}` and computes one kernel.
Recommendation: state a general rank–incidence theorem and let the small case fall out.

**Answer: `LEAN-KN-01` exists and is stronger than the recommendation.**

- `lean/AIEFProofsKn/AIEFProofsKn/CompleteGraphKn.lean`: `finrank_ker_inc_eq_choose` — for an
  `IsCompleteEdgeList` on `n ≥ 3`, `finrank ℚ (ker (inc src dst)) = C(n,2) − n`.
- `lean/AIEFProofsKn/AIEFProofsKn/KernelDimFormula.lean` (69 lines, commit `0c8cad0`): the arithmetic
  step `C(n,2) − n = n(n−3)/2` in `ℕ`, giving `finrank_ker_inc_eq_half`.
- Machine-checked, Lean 4 v4.33.1, Mathlib `0df444a3`, no `sorry`/`admit`/`native_decide`, axioms
  `propext`, `Classical.choice`, `Quot.sound` only.
- `registry/claims.csv` `LEAN-KN-01` caveat generalizes **past** the ℚ statement: the general lemma
  assumes a connected, non-bipartite graph over a field of characteristic ≠ 2; the sharp rank is
  `#V − #bipartite components`; **the result fails in characteristic 2**.

That last clause is exactly the "weaker hypotheses, stronger result" standard I cited from Nash
(`LIT-0037`) — including naming where the hypothesis cannot be dropped. I asked for a generality
that already exists.

**Caveat on the caveat:** both the commit message (`0c8cad0`: *"MERGE-PREP AGENT, NOT RESEARCHER
001; for audit"*) and PR #1 say this still needs Researcher 001's audit. The work is real; its
review status is not mine to grant.

---

## 3. Correction to my own work: I framed `LEAN-CF-01` / `CF06` with the wrong theorem

`ERRATA_2026-10-28.md` **E6** and claim `AUD-CYCLE-KERNEL` state the object precisely:

> K = ker A_J is the kernel of the **unsigned** edge–node incidence matrix ... it is not the graph
> cycle space. For a non-bipartite K_n, dim = m − n, whereas the cycle space (oriented incidence)
> has dim m − n + 1 (K4: 2 vs 3).

`AUD-CYCLE-KERNEL` gives `dim K = m − n = n(n−3)/2`, verified on 373/373 all-tied complete
components, with K3: 0, K4: 2, K5: 5, K6: 9.

**My round-5 adjudication of `LEAN-CF-01` and `CF06` cited `LIT-0011` (Godsil–Royle) for "rank =
n − c, nullity 3 − 1 = 2" — that is the oriented-incidence/cycle-space count, i.e. the object E6
explicitly says this is *not*.** The arithmetic in the claims (`ker C_{2,7} = span{(1,−1,−1)}`,
nullity 2) is unaffected and remains correct; what is wrong is my *attribution* of which classical
theorem it specializes.

The sharp version of the discrepancy worth checking: **the unsigned-incidence kernel of K3 has
dimension 0, not 2.** So `C_{2,7}` is not the K3 unsigned incidence matrix, and my sentence
"the Lean statement is the n−c instance for the 2-vertex/3-edge multigraph" should not stand. I have
not resolved which object `C_{2,7}` actually is relative to `inc src dst`; that is now an open
question, not a settled one.

---

## 4. Answered: what "Stage B" would have to be built on

**Question (round 3 F17).** The frozen-driver cocycle sets `δRₙ = 0`; the full delayed-state
variational equation was never constructed.

**Answer: confirmed — and the correct state space is now written down.**

- `origin/integration/round5:registry/studies.csv` lists `AIEF_1_4_TANGENT_AND_COCYCLE` entrypoints
  as `aief_1_4_full_state_tangent_operator.py`, `aief_1_4_history_cocycle_test.py`,
  `aief_1_4_branch_tangent_comparison.py` — **all three absent from all 11 branches.** A newer
  registry still points at code that does not exist, which independently corroborates F17.
- `ERRATA` **E2** gives the closed state at 966 dimensions: `history 612 + B upper triangle 66 +
  Re/Im C 288`. (612 = 12 nodes × 51 delay steps at `dt=0.01`, `tau=0.5`; 66 = C(12,2); 288 = 2·12².)
  That is the object a Stage B variational equation would live on, and it is a concrete,
  checkable definition I did not have before.

**And a correction to my `S09` adjudication reasoning.** I validated the retirement using
`LIT-0003` (exact reduction needs an invariant manifold). E2 gives a *stronger, internal* reason I
missed: the derivation was invalid, not merely superseded — `aief_1_4_augmented_spectrum.py`
differentiates an 18-coordinate map that is not a closed state (`restore_state` omits θ) and the
result depends on column order. `AUD-SLOWPOLE` is `Rejected`. The retirement is better supported
than my adjudication said.

---

## 5. Answered: my registry baseline is stale, and my coverage number is wrong

`registry/claims.csv`:

| Branch | Rows |
|---|---|
| `origin/main` | **file absent** |
| `arena/d4a487cc-aiefs` (my base) | 43 |
| `origin/audit/nanfix-v2` | 75 |
| `origin/integration/round5` | **76** |

My 43 are a **strict subset**; integration adds **33** claims: 24 `AUD-*`, 2 `LEAN-*`, 7
`SSRH-ORIG-*`. Therefore:

- My headline coverage is **24 of 43**, but against the registry of record it is **24 of 76**.
  Round 5's "the inbox is essentially complete" was **wrong**.
- **2 of my 24 adjudications carry a stale status**: `EMP-AIEF14-02` Frozen → **Exploratory**,
  `CF05` Frozen → **Supported**. (`EMP-AIEF14-03` and `CF10` also moved, but neither is adjudicated.)
- The status vocabulary grew by one value, **`Incomplete`** (10 claims), which my adjudication's
  closed vocabulary does not carry.
- `integration/round5:registry/studies.csv` has **15** studies, not 14 — adding
  `AI_AGENT_AUDITS_2026_10`, itself with 2 unresolved entrypoints.

**Consequence:** `audits/literature/ADJUDICATION.csv` is internally consistent and gate-8-clean
against its own baseline, but it is adjudicating a superseded registry. It should be re-baselined,
not silently left green.

---

## 6. Answered: no tool anywhere checks entrypoint referential integrity

Round 3 and Round 5 both proposed a gate. It does not exist:

```
git grep -l -iE 'canonical_entrypoint' origin/{research/freezing,research/lean-kn,
    integration/round5,ci/artifact-pins} -- 'tools/*' '*.py'   → no matches
```

`tools/ci/lint_claims.py` (205 lines, on `research/freezing` and `research/lean-kn`) lints only the
*status vocabulary*, read from `registry/README.md`, plus an `SSRH-ORIG-` rule forbidding
`Retired`/`Rejected`/`Quarantined` on untested origin hypotheses. It does not touch entrypoints.
`verify_inventory.py` checks conservation. So **nothing in the repository validates that a study's
declared entrypoints exist** — the gap is real, unaddressed, and now confirmed across every branch.

**And the defect runs in both directions:** `AIEF_1_3_falsification_updated.py` and
`AIEF_1_4_intertwining_controller_analysis.py` both exist and are registered nowhere.

---

## 7. Answered: which inventory is authoritative

`registry/README.md` on `integration/round5` ("Which inventory is authoritative for what",
added 2026-10-30) settles the split-authority question I raised in Milestone 1:

| Question | Authoritative file |
|---|---|
| What was present at `e47bad1`, and how each entry was **classified** | `registry/artifacts.csv` — frozen snapshot, 2,898 rows, never renamed or extended, checked by `tools/ci/check_artifact_pins.py` |
| What is in the tree **now**, with which sha256 | `registry/artifacts_current.csv` — **generated**, 3,363 rows, never hand-edited, checked by `tools/ci/check_current_inventory.py` |

That is the right design and it answers a question I had recorded as open. Note the current
inventory is 3,363 rows against my Milestone-1 count of 2,760 worktree + 138 zip.

---

## 8. Answered: CI now builds all three Lean projects

Part 1 recorded R-05: CI never builds `AIEFProofsKn` / `AIEFFreezeCore`. On PR #1 all three pass —
`lean (AIEFProofs)` 2m38s, `lean (AIEFProofsKn)` 3m21s, `lean (AIEFFreezeCore)` 20s — alongside
`Analysis tests`, `Artifact registry pins`, `Claims registry lint`, `Current-tree inventory`,
`Manifest hash verification`, `CI tool self-tests`, `File modes`. **1 failure: `Hygiene scan`**, step
*"Changed files (new binaries, secrets, PII warnings)"*. PR #1 is `MERGEABLE`, 130 files,
+29,841/−13, and states **"Do not merge without the owner's explicit OK"** — which is the owner's
call, not mine.

---

## 9. What the remote does NOT answer

1. **`AUD-NOVELTY` is still an open claim I can close.** Registered `Incomplete`, scope
   `Conjecture`, caveat literally *"First-pass literature search only"*, statement: the ingredients
   (delayed Kuramoto, Hebbian plasticity, normalisation) are prior art and novelty is established
   neither way. The literature inbox already holds `[LIT-0016]`, `[LIT-0018]`, `[LIT-0028]` — the
   adaptive-delay cluster — which is precisely the prior-art map that would move this from
   "first-pass" to sourced. **This is the highest-value literature task left.**
2. **`AUD-TIMESTEP`** — `Incomplete`, open item, "no timestep/safeguard convergence study has been
   run". I hold the sources that explain *why that matters for a DDE* rather than an ODE, but not a
   convergence result.
3. **`SSRH-ORIG-01`…`07`** — seven untested origin hypotheses, all `Incomplete`, including
   parametric amplification "up to 10⁸" and several correlation claims. No literature layer has
   looked at these at all. Whether they *should* be adjudicated is an owner scope question: they are
   origin claims, not repository results.
4. **`AIEF_1_0_TO_1_2_FOUNDATIONAL`** — still zero code on every branch and in all three archives.
   Nothing upstream has recovered it.

---

## 10. Corrections to my published work, collected

| # | Where I was wrong | Correct position |
|---|---|---|
| 1 | R5 basis for `LEAN-CF-01`/`CF06` cites oriented-incidence `rank = n − c` | Object is the **unsigned** incidence kernel, `dim = m − n` (E6, `AUD-CYCLE-KERNEL`). K3 unsigned kernel is **0**, not 2 |
| 2 | R5 coverage 24/43 | 24/**76** against the registry of record |
| 3 | R5 "the inbox is essentially complete" | Wrong — 33 unaudited claims, 24 of them `AUD-*` |
| 4 | R5 `S09` validated via `LIT-0003` | Stronger internal reason: derivation **invalid**, `AUD-SLOWPOLE` quarantined (E2) |
| 5 | R3/R5 F16 "phantom entrypoints" | Two are **stale names with script + outputs present**; the defect is bidirectional |

---

## 11. Recommended next actions, ranked

1. **Move this note into the real inbox.** This session is pinned to `arena/d4a487cc-aiefs` and
   cannot push to `audit-inbox`; this file is placed at the same path so it can be cherry-picked.
2. **Re-baseline the literature inbox to 76 claims**, refresh the 2 stale statuses, add `Incomplete`
   to the adjudication vocabulary.
3. **Adjudicate `AUD-NOVELTY`** — the one open claim where sources are already in hand.
4. **Fix the registry entrypoints:** rename the intertwining entrypoint to
   `AIEF_1_4_intertwining_controller_analysis.py`; register
   `AIEF_1_3_falsification_updated.py`; decide the three genuinely-missing tokens.
5. **Add the referential-integrity gate** — still absent everywhere, and now demonstrably needed in
   both directions.
6. **Owner decisions:** PR #1 merge; whether `SSRH-ORIG-*` is in scope for literature adjudication.
