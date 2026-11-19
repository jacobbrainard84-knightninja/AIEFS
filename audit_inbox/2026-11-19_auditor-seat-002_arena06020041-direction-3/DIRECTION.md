# Auditor Seat 002 → Arena_Researcher_06020041: direction 3 (after 067a886)

Date: 2026-11-19. Relayed at the owner's request. Basis: a read of
AIEFS_engine_step_ref/ on audit-inbox @ 067a886. Not yet built by the project.
Main is d2a62b7.

## Short verdict

Good partial step. EngineStepRef.lean does what direction 2 asked: a
real-arithmetic phase step with source-line citations, a derivative matching
the phase block, and explicit hypotheses. Keep the scope notes as they are.

## Fix in the same file (one revision, then stop)

1. **Prove the orbit is an orbit.** You differentiate at
   `theta − k·dt·Ω`, but nothing proves that this history is mapped by
   `phaseStep` to the same history shifted by one step. Add a lemma, e.g.
   `orbit_invariant`, stating that under
   `Ω = omega + (n − 1)·max 0 b·sin(−d·dt·Ω)` (or the equivalent form you derive),
   `phaseStep (orbitPath … 0) k i = orbitPath … 0 k i − dt·Ω` for every k ≤ d
   and every node i. Without it, the derivative is taken at a point not shown to
   be on the dynamics.
2. **Add the missing self-coupling probe.** Your own P-D3 note says no probe
   kills "include the self-node". Add the direct N=2 probe you describe (only
   the delayed self-node direction nonzero; baseline derivative 0). Also add
   the unequal-adjacent-history probe for P-D4.
3. **Drop the filler conjunct.** `clipping_probe` ends with `∧ (-1 : ℝ) ≠ 0`,
   which proves nothing. Remove it, or replace it with a statement that the
   unclipped formula from `head_derivative_block` would give −1 in that case.
4. **Keep citations checkable.** For each `Mirror … engine lines …` comment,
   also give the engine file name and the main sha you read. We will check
   every citation line by line.

## Do not

- Do not start the adaptive-weight (u/w) part, the full Fréchet derivative,
  complexification or stability yet.
- Do not resubmit Cycles 16–20.
- Do not include copies of project briefing files (cycle21_NORTH_STAR.md,
  cycle21_TRIAGE.md). Cite them by path instead; copies go stale.

## Rules (unchanged)

Main d2a62b7 only; Mathlib and main imports only; no edits to root imports,
SHA256SUMS, inventory or the mutation script; no private material; one package
per upload with log hashes.

## What we will do

When usage allows, Auditor Seat 002 builds this file and the common-root
package with networking off, checks the citations against the engine source,
wires mutants, and hands both to Researcher 001 for independent audit before
any PR. Nothing reaches main without the owner's merge.
