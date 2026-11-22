Researcher: 0046882 (Arena.ai)  
Date/time: 2026-11-22T03:01:39.733080-07:00 (host-reported MST; not authenticated)  
main sha: d1cbcf38937b75538100ccaf3115fcbe45a2714f  
Engine sha256: ca4593fda86a1b0a3d450d68b5ce4bddd08583fdb93deaf17db20dd6b1acdede (original) / a69b7943d31542097d1a599accc1c8ba722b0bf6b74d31a20a6dd8538090c830 (copy)  
Scope: Gate spillover lane, DIRECTION-2; full 40-seed reference cohort  
Status: UNVERIFIED by project seats

# Resource limits and potential blockers — requested owner disclosure

## Confirmed or observed limits
1. **Saved workspace snapshots: approximately 128 MiB or 10,000 files, best effort.** A 1.6 GiB downloaded clone previously prevented the Cycle002 ZIP reaching the owner's saved workspace, despite the file existing during execution. Moving scratch data out of the saved area restored delivery. This is an observed delivery blocker, not a scientific failure.
2. **Temporary cache is not durable.** Paths under `.cache/` may disappear between sessions. The prior cloned repository was absent at this cycle's start. Baseline engine/manifest copies survive in the delivered Cycle002 package and were hash-checked. Full raw40 arrays and pool vectors in this cycle are scratch, not promised future deliverables.
3. **Observed RAM approximately 2 GiB, no swap.** Avoid holding the full cohort and its quantile temporaries in memory. This cycle runs one observed trajectory at a time, uses cached raw NPZ and binary pooled vectors, and reduces one distribution at a time. Raw arrays for a seed require about 23 MiB; all 40 together would approach0.93 GiB before statistics temporaries.
4. **Observed one-shot execution transport failure.** The first tool call requested a 1,800-second timeout but returned shell_error after about479 seconds while its child process was still alive. The stdout/tee pipe later broke. The saved exception is BrokenPipeError at progress logging, not a numerical assertion. Twenty-six seeds had durable summaries and raw hashes. The run was resumed with a background-process tool and direct `.log.txt` redirection, preserving the failure record and validating recovered arrays before reuse. Future long jobs should use that execution mode from the start.
5. **Git upload ignores *.log.** Auditor002 reported two Cycle002 log files dropped by audit-inbox's ignore rule. All Cycle003 logs use `.log.txt`; source copies/diffs containing text `.log` do not create ignored log files.

## Mitigations used
- Full raw cohort retained only in excluded temporary cache. Deliver all per-seed/window summaries, hashes of all six raw numeric arrays per seed (240 arrays), and compact per-step future descriptors. This is the direction's permitted storage fallback, chosen before execution.
- Deliver unchanged engine source, instrumented source, source hashes and diff so independent regeneration does not require a fresh full clone.
- Preserve first-attempt outputs, failure and execution-only recovery script; reconstruct pools from validated arrays rather than append twice.
- Keep Cycle002 untouched; keep Cycle003 files and its ZIP within the save budget.
- Raw file/array completeness is checked before declaring completion; no early subset is called a full cohort.

## Potential blockers, not observed scientific failures
- A different Python/NumPy/BLAS environment may give a different floating-point trajectory. Cross-host equality is NOT_RUN here; local source/copy equality and pilot equality are separately checked.
- A future Lean task would need a toolchain and dependency cache; no Lean task was assigned or built in this lane.
- No independently authenticated clock: session date and host/project timestamps disagree. Use owner upload commit for deposit chronology, as directed. Protocol predeclaration is evidenced by session operation order and the printed pre-run hash, not an external timestamp authority.
- No independent access to private project communications or automatic handoff. Owner relays directions/uploads. I do not keep researching autonomously between active sessions.

## Decisions for Auditor002
No larger storage grant is needed for this assigned measurement if summaries+array hashes are acceptable, as DIRECTION-2 allows. If future work requires durable full raw trajectories, request a separate artifact-storage plan before running it. Do not rely on this temporary cache as the project's archive. No relaxation of scientific thresholds, seed coverage or scope is requested.
