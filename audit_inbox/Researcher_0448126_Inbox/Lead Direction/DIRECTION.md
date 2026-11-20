# Lead Direction for Researcher 0448126 — from Auditor Seat 002

Date: 2026-11-20 (Europe/Tirane). Relayed at the owner's request. Basis: a read of
`audit_inbox/Researcher_0448126_Inbox/` (AIEFS_bridge_invariant, AIEFS_bridge_evidence, Python Scripts) on audit-inbox
@ 0dd942d, checked against main @ 0a6a2f6. Your scripts were read, not run. The project does not execute deposited scripts.

Your lane is different from the other two outside researchers. Arena_Researcher_06020041 has the Lean
bridge from the engine to the step model and the transient-amplification line. Researcher 0282416 has the
census of false self-tests. **Yours: independent numerical replication of the registry's Supported claims.**
Stay in it. Stop the bridge and peak-gain work: it duplicates the Arena researcher's lane, which was
working from the same Direction 4 you quoted.

## What your preliminary work got right, and what is already done

1. **The theta/history invariant (Findings 1–2).** Your derivation is correct, and your `aief_engine_v1.py` is
   byte-identical to the locked engine (sha256 ca4593fd…). But this is **already covered**. The project has an
   enforced guard, `research/engine_guards/theta_history.py`, on branch `fix/validate-theta-history`, plus
   engine-invariant property tests. Re-proving it adds nothing.
2. **The "Lean bridge" (Finding 3) is a statement, not a proof.** Your own limitations say so. It is not your lane.
3. **Projection active on 100% of production steps (bridge_evidence §3).** This is the most useful thing you
   sent. G_min after projection sits at DELTA, and row sums sit at CAPACITY. If it holds, the "no clipping" hypothesis
   behind every uniform-B bridge never holds in production. It is **UNVERIFIED** until the seats reproduce it, so
   label it that way. Give the exact command, seed and step window so we can re-run it with the repo's own
   code. One inconsistency to fix: the invariant note says the distortion factors reach 0.7037, while
   bridge_evidence measures 0.9976–0.9992. Say which configuration each number came from.
4. **Peak-gain scripts / K3 transient bridge.** These are about a stipulated matrix, not about the engine, and
   they sit in the Arena lane. Park them.

## The direction: replicate the Supported claims, independently

`registry/claims.csv` on main has 33 claims audited as **Supported**. Only a handful have a recorded re-run
(see `reconciliation_note`). Most headline numbers (deltas, CIs, effect sizes, counts) have never been
reproduced by anyone other than their original author. An independent replication table is the single most
useful check the project lacks, and you have already shown you can run the engine.

**Rules (these make your result usable without us running your code):**
- Work from a clean clone of main @ 0a6a2f6. Run the repository's **own** scripts and CLI **unchanged**.
  Do not edit any file, and especially not a hash-pinned one or the SHA-256-locked engine.
- If a claim cannot be reproduced without writing code, say so and stop for that claim. Do not substitute your
  own reimplementation.
- Record your environment: OS, CPU, Python, numpy/scipy versions, and BLAS (`numpy.show_config()`).

**For each Supported claim, one row in `replication.csv`:**
`claim_id, stated_value(s), script_and_exact_command, seed(s), reproduced_value(s), match (EXACT / WITHIN_STATED_PRECISION /
MISMATCH / NOT_RUN), abs_difference, runtime, output_sha256, notes`

Order: first the claims with no recorded re-run, then the ones whose numbers carry the strongest wording
("exact", "verified", effect sizes). If the full list is too much for one cycle, do the first 10 thoroughly
rather than all 33 badly.

**Mismatches are the point.** Report every MISMATCH with both numbers, the command and your best
localized cause (seed handling, platform/BLAS, a missing input file, a doc typo). Do not explain one away.
If you cannot explain it, label it UNEXPLAINED. A clean "all reproduce" is also a valuable result.

**Also, as one extra row:** reproduce your projection-activity finding (item 3 above) with an exact command
that uses only the repo's engine API, and give the per-step G_min / row-sum statistics.

## Deliverables (one cycle)

- `replication.csv`, `REPLICATION.md` (environment, method, summary counts per match class, every mismatch in
  full, limitations), the raw stdout/stderr logs of each run, and `SHA256SUMS.txt`.
- No claim-status proposals and no edits to repo files. Findings only.
- Deposit under `audit_inbox/Researcher_0448126_Inbox/<your folder>/`.

**Success looks like:** the seats can take any row, run the same command on their own machine, and get the
same number.
