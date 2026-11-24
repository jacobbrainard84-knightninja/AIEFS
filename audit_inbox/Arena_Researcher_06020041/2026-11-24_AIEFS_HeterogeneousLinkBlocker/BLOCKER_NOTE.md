# AIEFS_HeterogeneousLinkBlocker — DIRECTION-15, item 1

**Status:** prepared locally for owner deposit; not deposited, independently reviewed, pushed, or promoted. Following DIRECTION-15's explicit instruction to stop if the reference link is blocked, this note does not claim to complete items 2–4. Folder date is `date -u +%F`: 2026-11-24.

**Base:** main `7865ab19282ceae49df9aa70b396d60ada38d3c2`, the base used and verified in the previous cycle. This cycle read the previously verified byte-identical local `EngineStepRef` snapshot; the ephemeral checkout was not present, so I did not independently re-fetch or re-verify main HEAD this cycle. The snapshot SHA-256 is `573adfd6d98181d5734c2293f8867236e78c55c3fe0a5bdaa8f120d4844c2666`. The supplied DIRECTION-15 reports WindowMax accepted at inbox `a5cf30e`; I did not myself fetch or rerun that review this cycle.

## Exact blocker

Main `lean/AIEFGateCore/AIEFGateCore/EngineStepRef.lean`:

- `clippedWeight` L27 takes a **scalar** b.
- `phaseHead` L33–36 uses that same `clippedWeight b` for every `j ∈ univ.erase i`; `phaseStep` L40–42 also takes only scalar b.
- `head_derivative_raw` L98–102 and `head_derivative_block` L120–125 preserve this common scalar. Most directly, `phase_step_head` L137–143 has `dt*b*cos(...)` as the coefficient of **every** delayed neighbor and `(n−1)*dt*b*cos(...)` as the aggregate current-node coefficient. Its conclusion concerns the scalar-parameter `phaseStep`, not a matrix-parameter phase step. It therefore cannot express the requested derivative for arbitrary heterogeneous B as a direct instance.
- `neighbor_derivative` L78 and `history_derivative` L146 are useful ingredients for an **additional** matrix-weighted reference definition and new head lemma, but such a definition is not the existing `phaseStep` and establishing it would be new work. A link to main's individual-neighbor result would not by itself be a proof of correspondence to Python's complete update.

This is a limitation of the current reference statement, not a claim that a heterogeneous theorem is mathematically impossible. It also does not invalidate WindowMax's uniform-weight statement.

## Why scalar instantiation cannot cover arbitrary B

Hand check, not a Lean run: take N=3, d=1, dt=1, synchronized Ω=0, and symmetric nonnegative zero-diagonal B with b₀₁=1, b₀₂=2, b₁₂=0. Set all current components to zero. In the requested heterogeneous head for node 0, a delayed unit perturbation at node 1 gives derivative 1; a delayed unit perturbation at node 2 gives derivative 2. In main's `phase_step_head`, the same two probes each produce the same scalar b (or `clippedWeight b` before the positive-branch lemma). No single scalar b can equal both 1 and 2. Thus merely instantiating the existing main theorem cannot establish the requested all-perturbation reference link.

**OPEN:** new heterogeneous reference step and derivative lemma; its link to the engine including clipping, gate and modulo; max-window theorem for it; capacity-row algebra and numerical consequence; growth witness and three mutant tests. Per the stop condition, none are claimed or counted here, and no Lean or engine test was run.

## Limited read of phase-step ordering

Read only: in the local engine source `aief_experiment_engine_v1.py` (SHA-256 `ca4593fda86a1b0a3d450d68b5ce4bddd08583fdb93deaf17db20dd6b1acdede`), L808 initializes `B_projected` from the clipped/symmetrized proposal; L810–813 replace it with the minimum-outer projected proposal when `pre_violation` holds; L823 assigns `state.B = B_projected`; L830–839 then use `state.B` in phase coupling. Thus the phase step reads the post-gate value whether projection was active or not. This ordering observation is not a proof that its rows satisfy the proposed mathematical capacity bound, and no claim about floating-point strictness is made.

## Reproduction and next decision

`inspection.log.txt` records the clock, local source hashes and symbol/ordering line hits; path names in that log are normalized to basenames for privacy. The inspected commands were `date -u +%F`, `sha256sum` on the two local files, `grep -nE` on the indicated Lean symbol names and engine assignments, and `nl -ba ... | sed -n` over the cited line ranges. No new Lean candidate, mutants, engine simulation, root import, frozen evidence, or prior inbox item was changed.

Request lead direction: authorize an add-only heterogeneous fixed-weight reference definition using main's neighbor and history derivative ingredients, with a separate and explicit Python correspondence obligation, or provide an existing matrix-weighted main reference lemma to use. Do not treat this blocker note as an acceptance claim.
