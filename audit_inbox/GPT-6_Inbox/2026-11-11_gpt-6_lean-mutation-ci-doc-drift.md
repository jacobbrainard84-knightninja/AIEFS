# GPT-6 review — Lean mutation-check CI documentation drift

- Agent: GPT-6
- Date: 2026-11-11 (UTC)
- Main reviewed: `1c30ca56e56f11517d1e04f90d521a5aa6990c52`
- Inbox branch reviewed: `b1f5bc4051dc3e81935d2c21c863778b10264350`
- Scope: post-merge integration of AIEFGateCore P3/P4a/P4b red-team checks; compare the current Lean workflow and CI run against the current Lean-gate specification.
- Status: **UNVERIFIED INPUT**; static review of source and GitHub workflow metadata only. No local Lean build or mutation script was run by GPT-6.

## Finding 1 — two current “not run in CI” statements are stale

**Classification: confirmed documentation drift against current main.**

At main `1c30ca56e56f11517d1e04f90d521a5aa6990c52`:

1. `.github/workflows/lean.yml`, blob `b36b3e2ca396e89ac62d4ad7e8ff13deab148bc7`, lines 90–102, defines the step **“Lean-gate mutation check (AIEFGateCore only)”** and executes `python3 research/lean_gate/lean_mutation_check.py` when `PROJECT == AIEFGateCore`. The project matrix has `AIEFGateCore` as a required job (same file, lines 47–49).
2. `research/lean_gate/lean_mutation_check.py`, blob `a289bca7949696184651fce9b1997e7662f43db3`, describes the complete M1–M36 set and returns success only when all positive/negative controls and every mutant rejection pass.
3. The live specification still says the mutation check is not run in CI:
   - `research/lean_gate/SPEC_P1_gate_identities.md`, blob `0788acaf56258e2c9616e66a1d14ac4c1f2bbe04`, line 696 (P3 §8.5).
   - Same file, line 784 (P4a §9.5).
4. PR #27's merge commit is main itself. Its diff explicitly adds the Lean workflow mutation-check step and adds the `research/lean_gate tests` pytest step to `.github/workflows/repo-checks.yml`. This is the direct change that makes the two “not run in CI” statements stale.

## Independent CI evidence

- Lean proof check run [42845144354](https://github.com/jacobbrainard84-knightninja/AIEFS/actions/runs/42845144354), on main commit `1c30ca56e56f11517d1e04f90d521a5aa6990c52`, completed successfully. Its `lean (AIEFGateCore)` job and the named **Lean-gate mutation check (AIEFGateCore only)** step both report success.
- Repo checks run [42845144147](https://github.com/jacobbrainard84-knightninja/AIEFS/actions/runs/42845144147), on the same main commit, completed successfully; its `research/lean_gate tests` step reports success.
- The workflow step's successful conclusion is evidence that the committed script returned success in CI; it is not a fresh GPT-6 local reproduction and does not replace independent review of theorem scope.

## Recommended documentation correction

Update only the two stale specification bullets in a maintainer-reviewed branch from current main. They should say the mutation checker is now run by `.github/workflows/lean.yml` on the required AIEFGateCore matrix row, and point to the CI step. Preserve the distinction between:
- the Lean mutation checker (M1–M36), which is now in CI; and
- any future Lean-side statement-hash/pin mechanism, which §10.6 still correctly lists as absent.

Do not infer that CI inclusion proves the mathematical hypotheses are realized by the coupled oscillator engine. P3 persistence remains conditional on branch assumptions and frozen (R); P4b OFF/ON results remain conditional on infinite-tail drive bands. The specification's substantive open-scope statements remain important.

## Scope and disposition

No mathematical counterexample or theorem defect was established in this bounded integration review. The actionable issue is the stale CI status in two specification passages. The current workflow, script, CI run metadata and main merge diff support the correction above.

**UNVERIFIED INPUT — not independently triaged or promoted.**
