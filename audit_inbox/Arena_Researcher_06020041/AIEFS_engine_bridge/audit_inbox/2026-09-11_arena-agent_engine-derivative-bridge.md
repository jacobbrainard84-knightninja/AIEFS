# Proposed smooth-interior engine-to-phase-block bridge — audit draft

- **Agent:** Arena.ai Agent Mode
- **Date:** 2026-09-11, Atlantic/Reykjavik
- **Base:** main `d2a62b7f9e6456ade8591d5f12c9ccdeed185d19`; inbox `e5ff81d1df5567cf89552fc6e51eeb854fa58632`.
- **Status:** source-referenced exact-real handwritten derivation; no Lean or independent verification.

`ENGINE_JACOBIAN_BRIDGE.md` states a restricted homogeneous-frequency, no-shuffle, prepared interior orbit with a consistent delay history and strict clipping/projection margins. It derives the linearized real/imaginary EMA, symmetrized weight and phase-history updates in the order of `aief_experiment_engine_v1.py`, citing exact source lines. On the invariant u=w=0 subsystem, projection to phase histories yields the proposed complete-graph no-self-loop shift block; v may be driven by phase, so setting v=0 is not generally invariant. The derivation explicitly distinguishes the idealized exact-real map from literal floating-point execution and notes that the state validator does not establish theta/history consistency.

Source version was byte-matched to the stated main commit. This is a reviewable argument, not an engine-derivative theorem: complex-EMA differentiability, circle charts, branch conditions and Python/state correspondence remain to be formalized. No active projection, heterogeneous-frequency, random-initialization or nonlinear stability claim; no tests, Lean build, full gate, mutation suite, independent review, push or promotion in this work. Suggested review: verify the derivative and assumptions against the cited lines, then formulate a minimal exact-real reference map and prove its derivative before resubmitting the held candidate layers.
