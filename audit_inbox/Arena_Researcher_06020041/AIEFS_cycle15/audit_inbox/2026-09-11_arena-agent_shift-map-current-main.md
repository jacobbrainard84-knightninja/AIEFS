# Scalar delayed shift-map bridge against current main — audit draft

- **Agent:** Arena.ai Agent Mode
- **Date:** 2026-09-11, Atlantic/Reykjavik
- **Reviewed:** main `c9863e1c391a9f39cc8cef680a2fa349378b6cfe`, `lean/AIEFGateCore/AIEFGateCore/DelayRoots.lean`; audit-inbox head `2e63035c1c973ff07e8124e3ca9b8e198b4e5171`.
- **Scope:** rebase of the unmerged Cycle 14 abstract delayed shift bridge on the actual main root bounds. Unverified input, not a project claim.

PR #42 brought `DelayRoots.lean` to main. It already covers both Cycle 11/12 polynomial root bounds, so the old root files and Cycle 14 import stack should not be promoted unchanged. `DelayModeMain.lean` imports main's `DelayRoots` directly, defines the scalar map `T(v)₀=a v₀+b v_d`, `T(v)ₖ=vₖ₋₁`, and proves the characteristic equation for a nonzero pointwise eigenmode. It instantiates main's common and transverse root theorems, including the N=2 case. This does not prove the map is the full AIEFS Jacobian, a Matrix spectral result, nonlinear stability, projected-gate stability, or any production claim. Main's DelayRoots docstring explicitly says common-root simplicity is not proved there; Cycle 13 is a separate unmerged candidate and is not imported here.

Evidence: Lean 4.33.1, mathlib `0df444a360eaa60ab8c11dca51a86af692955474`; `lake build AIEFGateCore.DelayModeMain` passed 2212 jobs with no warnings on sparse cited main plus this file. Seven theorem axiom reports are standard only. A check file verifies a zero-state/z=2 counterexample to dropping nonzero and a nonzero common eigenvector at z=1. Workspace `AIEFS_cycle15/ONE_PAGE_NOTE.md`, source, check file, `attempt1.log`, `check.log`, `SHA256SUMS.txt` contain details. Full gate, mutation suite, module/checksum/inventory wiring and independent review are outstanding. No push or claim promotion.
