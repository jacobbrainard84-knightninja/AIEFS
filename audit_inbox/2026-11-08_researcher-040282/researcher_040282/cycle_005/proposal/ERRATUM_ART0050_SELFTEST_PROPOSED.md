# PROPOSED erratum: ART-0050 synthetic K3 assurance

**Owner/seat review required; not an approved registry erratum.** Existing
ART-0050 and saved output files remain unchanged. Test base:
`f3e3a57632c613e860a9941f007732cb4c2c91c6` on main.

## Correction

Withdraw the interpretation that ART-0050's existing `--self-test` PASS certifies
its K3 fixture against the implemented admissibility map. The isolated proposal
`(x25,x29,x59)=(.41,.31,.27)` has actual winners `(2,2,7)`, not `(7,2,7)`.
The left-identity residual using the current-main edge-coordinate operator is
`-0.02121459694983044`, against the old `1e-14` allowance. The old synthetic test
constructs its own projected answer and never calls that operator.

This is the previously reported B-F4 mechanism, independently reproduced by
Researcher 001 on their earlier main and locally reproduced on the tested main;
it is not a new mathematical counterexample to the CONDITIONAL identity.

## New-file proposal, not an in-place fix

Add `AIEF_1_4_proposal_equalization_branch_selftest_r040282.py` as a reviewed
synthetic K3 companion. Add its regression test as a separate reviewable file.
An owner/seat may later assign an artifact/erratum ID and decide registry wording;
no ID or status promotion is asserted by this proposal.

The companion calls
`AIEF_1_4_actual_admissibility_branch_audit.admissibility_from_nonnegative_proposal`
on the full isolated12-node vector, verifies the public incidence layout, and
compares ALL operator outputs/branch metadata with a separate Fraction-loop map.
It checks identities using actual returned `y`, not a reconstructed projection.
This pure edge-coordinate audit helper is not a fresh call to the production
engine's full delayed `advance_state` or a real-data bridge replay.

Default positive fixture: `(.41,.27,.31)`, observed winners `(7,2,7)`.
The old fixture, a tie and an inactive gate are rejected as strict-branch tests.
Corrupted output/winner metadata, a constant default projection, unguarded scaling,
and an epsilon-dropped coefficient are detected by the accompanying controls.
The proposal is snapshotted/oracle-evaluated before the call; a test double that
rewrites it to a default answer is rejected. That mutation falsifier exposed and
repaired a flaw in the first local candidate, not an upstream-helper mutation.
No core decision relies on removable Python assertions.

From an upstream-root integration after review:

```sh
python AIEF_1_4_proposal_equalization_branch_selftest_r040282.py --self-test
python AIEF_1_4_proposal_equalization_branch_selftest_r040282.py --self-test --fixture .41 .31 .27
# Second command must exit2, report BranchMismatch, and print no PASS.
```

Outside an upstream root, set `R040282_AIEFS_SOURCE` to the reviewed source
directory. Full reproduction (including legacy-red/candidate-green comparison)
is in the cycle005 standalone packet. Twenty-one unittest methods pass normally
and under `-O`;64 seeded perturbations plus one default positive are finite
numerical checks at absolute1e-14,relative0, not a universal float64 proof.

## What this does not correct or establish

- The original script remains a frozen historical artifact and will still print
  its old PASS; the erratum withdraws that PASS's claimed K3 coverage.
- The new companion only replaces the K3 assurance. It does not rerun/replace the
  old proposal-difference, directed-radial, or forced-recurrence self-test blocks.
- No production parameter, dynamics, conditional theorem, replay trajectory,
  identity summary, artifact registry row, or saved report is changed.
- The inspected saved bridge command omits `--self-test`; source dispatch returns
  immediately from that flag's branch. This makes the false synthetic PASS
  separate from the recorded normal replay path. That is static provenance
  evidence, not a fresh replay, an exhaustive dependence audit, or proof that
  every historic wrapper avoided the flag.
- The manifest's smallest saved winner margin is about 4.44e-14, whereas the new
  finite positive fixtures have comfortable margins. These tests do not certify
  that saved near-tie states have any floating-point robustness guarantee.
- No coupled locking, future branch persistence or rate-law conclusion follows.

## Requested disposition

Owner uploads only to a dated audit-inbox handoff. Review the proposal FROM
current main, keep this one finding on its own repair branch if accepted, and
run independently designed wrong-branch/constant-answer/epsilon/tie controls.
Do not merge inbox or salvage worktrees directly into main. Engine complex-NaN,
oracle uniqueness, v4.1 inference/estimand review, and Lean integration are
separate work items. Nothing was pushed or submitted by this agent.
