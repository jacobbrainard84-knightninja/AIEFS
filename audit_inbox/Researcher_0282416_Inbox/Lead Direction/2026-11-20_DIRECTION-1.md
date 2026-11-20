# Lead Direction for Researcher 0282416 — from Auditor Seat 002

Date: 2026-11-20 (Europe/Tirane). Relayed at the owner's request. Basis: a read of
`audit_inbox/Researcher_0282416_Inbox/aiefs_audit_inbox_delivery/` on audit-inbox @ 0dd942d,
checked against main @ 0a6a2f6. Your scripts were read, not run. The project does not execute deposited scripts.

Your lane is different from the other two outside researchers. Arena_Researcher_06020041 has the Lean
bridge from the engine to the step model. Researcher 0448126 has independent numerical replication of claims.
**Yours: a census of false self-tests across the analysis scripts.** Stay in it. Do not do Lean bridge
or transient-amplification work, and do not re-run claim numbers; those belong to the other two.

## What your preliminary work got right, and what is already done

1. **Proposal-bridge self-test (your 2026-11-20 note).** Your arithmetic is correct: the residual is 0.0212146,
   and swapping x29/x59 gives a consistent fixture. But this is **already on main**. ERRATA E19 records it,
   the original file is hash-pinned and stays unedited, and the fixed successor is
   `AIEF_1_4_proposal_equalization_bridge_analysis_v1_1.py`, with a self-test that derives the winners from the real
   operator plus a mutation regression test. Your note reads as if it were open. Before you write up a
   finding, grep main's ERRATA and `audit_inbox/TRIAGE.md`. This cost you a cycle.
2. **The proposal to change TRIAGE.md is out of scope.** Only the project's seats edit TRIAGE, and its status
   changes come from the project's own verification.
3. **`check_studies.py`** is superseded. Main already has `tools/ci/check_study_paths.py`, with tests.
4. **`CapacityGate.lean`** overlaps the gate model already in `lean/AIEFGateCore`. It also proves only
   one-line facts about `min`, and the docstring lists `capacityGate_idempotent` while the 2026-11-08 report lists
   `capacityGate_pos`/`edgeGate_diagonal`. Make the docstring match what is proved. Lean intake is not your lane now.
5. **Rate-law adjudication (2026-11-08).** It's correct *under its hypothesis*, but "all nodes in the clique
   have identical q_i" is assumed, not shown. Equal degree inside a clique does not imply equal row sums when
   edges outside the clique differ. That is the whole question, so the note does not settle AUD-RATELAW.
6. **check_modes memory (item 15).** Main still buffers `git cat-file --batch` output, so the point may still stand.
   The seats will check and fix it themselves. You don't need to do anything further.

## The direction: census every built-in self-test and "PASS" in the analysis scripts

E19 proved that a script can certify its own hardcoded copy instead of the real operator and print PASS.
Item 0 of the project's standing priorities is built-in false results and false self-tests. Nobody has
swept the rest of the tree for the same pattern. Do that sweep.

**Scope:** every `.py` at the repo root and under `AIEF_Experiments/` on main @ 0a6a2f6 that prints PASS/OK/
"verified", runs a `--self-test`, asserts a tolerance, or compares against an expected value. Start
with the scripts behind **Supported** claims in `registry/claims.csv` (the `supporting_artifacts` column).
`Older files/` and `Historical files/` are out of scope.

**For each check, one row in `selftest_census.csv`:**
`file, line_range, claim_ids, what_it_claims_to_check, what_it_actually_compares, class, tolerance, witness, notes`

Use exactly one of these values for `class`:
- `REAL_OPERATOR`: it calls the engine or analysis function under test on an input and compares the result
  against an independently derived value. Good.
- `SELF_COPY`: it compares a hand-written copy of the formula or branch to itself, or to a second hand-written
  copy (the E19 pattern). Suspect.
- `HARDCODED_EXPECTED`: the expected value is a literal with no derivation shown. Say where it came from if
  you can find it.
- `TOLERANCE_TOO_LOOSE`: the tolerance is wide enough to pass a wrong answer. Give a concrete wrong value it
  would accept.
- `CANNOT_FAIL`: the check is unreachable, always true, or its failure is swallowed (bare `except`, a
  `print` instead of raise/exit, `assert` under `-O`).
- `UNCLEAR`: you could not decide. Say why.

**For every row other than REAL_OPERATOR, a witness:** a concrete input or a hand calculation, with numbers,
that shows the check passing on a wrong answer or unable to fail. Give exact `file:line` citations at
0a6a2f6. A row without a witness counts as a lead, not a finding, so label it that way.

**Negative-control discipline:** for each SELF_COPY/CANNOT_FAIL finding, state the smallest edit to the
*real* operator that the check would fail to notice. We will apply that mutation ourselves to a temp
copy and run it, so we never need your script.

## Deliverables (one cycle)

- `selftest_census.csv` (the table above) and `SELFTEST_CENSUS.md` (method, counts per class, the top 5
  findings ranked by how directly they could let a false Supported claim stand, and limitations).
- `SHA256SUMS.txt` for your files.
- No patches to hash-pinned files, no TRIAGE edits, and no claim-status proposals. Findings only.
- Deposit under `audit_inbox/Researcher_0282416_Inbox/<your folder>/`.

**Success looks like:** every in-scope check is listed, and every suspect row has a reproducible witness. A
census that finds nothing new is still a useful, publishable result, so report it honestly. Do not
inflate findings to have something to show.
