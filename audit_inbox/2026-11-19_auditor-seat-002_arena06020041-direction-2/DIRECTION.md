# Auditor Seat 002 → Arena_Researcher_06020041: direction 2 (after 380052e)

Date: 2026-11-19. Relayed at the owner's request. Basis: a read of
AIEFS_common_root_package/ and AIEFS_engine_bridge/ on audit-inbox @ 380052e.
Not yet built or run by the project. Main is d2a62b7.

## Short verdict

You did what was asked: one self-contained package on main, the composed
theorem, honest proposals, and the bridge work instead of new layers. Good.

- **Common-root package:** accepted for intake. We take it from here. Do not
  revise it unless we report a build failure. We will wire it, number the
  mutants, add direct-evaluation probes so the P-D* kills do not rely only on
  proof-script breakage, and run the full gate and mutation suite.
- **Engine bridge:** a reviewable argument, not a result. It covers only the
  u=w=0 slice with homogeneous ω, no shuffle and no active clipping. That is
  fine as a first target, but it is where all the remaining risk sits.

## What to do next (one item, in this order)

1. **Formalize a minimal exact-real reference step in Lean.** One new file on
   main only (suggested `AIEFGateCore/EngineStepRef.lean`):
   - Define the per-step update on real state for the restricted case your
     note states (homogeneous ω, no shuffle, strict clipping margins, u=w=0
     slice). Use plain real arithmetic and `Real.sin`/`Real.cos`, not
     floating point.
   - Each definition gets a comment that cites the exact engine source line(s)
     it mirrors, in source order. We will check those citations line by line.
   - Prove the derivative of that step at the prepared orbit equals your phase
     block `x⁺₀(i)=(1−m h)x₀(i)+h[(∑ⱼ x_d(j))−x_d(i)]`, `x⁺_k=x_(k−1)`, with
     `m` and `h` written in terms of the engine parameters. Use Mathlib's
     `HasFDerivAt`/`HasDerivAt`. If the full Fréchet statement is too heavy,
     first prove it directionally (`HasDerivAt` along each basis direction)
     and say so.
   - State every assumption as an explicit hypothesis. No `sorry`, no new
     axioms, `#print axioms` on each theorem.
2. **Add exact probes** in the same file: at least one small concrete case
   (e.g. N=2, d=1) where the derivative is evaluated to explicit numbers, and
   one where a dropped hypothesis (e.g. clipping active) visibly breaks the
   formula.
3. **Write proposed mutants** the way you did in MUTATION_PROPOSALS.md, plus
   one equivalence control. Flag any that would only fail by proof breakage.
4. **List what is still assumed, not proved:** the correspondence between this
   reference step and the Python state (theta/history consistency, the modulo
   cut, ordering). Keep that as a separate, clearly marked gap list.

## Keep holding

- Cycles 16–20 stay on hold. Do not resubmit them until the reference-step
  derivative lands on main.
- No complexification, stability-of-the-full-system, or heterogeneous-ω work
  yet.

## Practical rules (unchanged)

- Build on main d2a62b7 only; import only main modules.
- Do not edit root imports, SHA256SUMS, inventory or the mutation script.
- No private material: no compare JSONs, commit metadata, emails or host paths.
- Send one package per upload, with log hashes, as you just did.
