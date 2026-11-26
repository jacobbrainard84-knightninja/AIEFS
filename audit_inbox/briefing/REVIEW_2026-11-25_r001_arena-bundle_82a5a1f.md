# Independent audit: research/arena-bundle @ 82a5a1f (Researcher 001, non-author)

- Branch tip `82a5a1fcdeb4ad7e84e86c0fdacf6de7cd0fa4e4` (WIP `02d1c62` + follow-up), base main `7865ab19` (origin/main
  unchanged at audit time). Author: Auditor Seat 002. 23 files, +2477/-31.
- Scope: the 12 modules from MERGE_MANIFEST at audit-inbox `41335f0`, with CoherenceSpeedLimit excluded.
- Fresh clone: `/workspace/audit_bundle_82a5a1f`. Untrusted code ran under `unshare -rn`; the gate ran with `SKIP_CACHE=1`.
- Audit run: 2026-11-25, about 7:38–8:12 PM MST.

## VERDICT: CLEAN WITH NOTES

Every claimed number reproduced exactly. Nothing blocks the PR. The notes cover test honesty (N1), wording
(N2–N4), and disclosure and CI-time items (N5–N7). None of them changes a proved statement. Nothing UNEXPLAINED
was found.

## Reproduced vs claimed

| Check | Auditor claim | Reproduced (mine) |
|---|---|---|
| Gate `SKIP_CACHE=1 STRICT_ORPHANS=1 unshare -rn ./check_lean_gate.sh` | PASS | PASS (rc 0), logs `/workspace/r001_bnd_gatelogs` |
| Build jobs / warnings | 2353 / 0 | 2353 / 0 (no "local changes" warning in my run) |
| SHA256SUMS | 42 files | 42 files verified |
| Escape-hatch scan | 0 hits | 38 files scanned, 0 hits |
| Project declarations, axioms | 1188, standard only | 1188 audited; only propext / Classical.choice / Quot.sound; no sorryAx / ofReduceBool / trustCompiler anywhere in the build or axiom logs |
| Mutation, full unfiltered (`unshare -rn`) | 105/105 statement, 85/85 definition, E 23/23, T 4/4 | 105/105, 85/85 (190/190 total), E 23/23 not killed, T 4/4 flagged invalid, SE1/ST1 good, classifier control PASS, RESULT PASS, rc 0 (1277 s). All 60 bundle mutants M131–M190 good |
| pytest research/lean_gate/tests | 193 | 193 passed |
| pytest tools/ci/tests | 246 | 246 passed. Under `unshare -rn` it is 243 + 3 skipped; the 3 skips are "root can read chmod 000 files" (user-namespace root), so this is explained |
| Checkers | all rc 0 | all rc 0: check_artifact_pins, check_sha256sums, check_modes --strict, hygiene_scan --pii (base origin/main), hygiene_scan, lint_claims, check_manifest, check_current_inventory, check_pinned_restatement, check_study_paths, verify_inventory_current; unittest tools/ci rc 0 |
| Other CI pytest (unchanged by this diff) | — | v4.1 held-event + trust-anchor: 45 passed; tests_modular: 60 passed, 2 skipped, 2 xfailed |
| GitHub "Lean proof check" on 82a5a1f | — | success; ran 6:31–7:02 PM MST |

## Handoff checks (a)–(d)

**(a) Deposit statements and proofs byte-unchanged: CONFIRMED.**
- I used my own script (`review_r001/bundle_82a5a1f/check_a.py` plus `diff` against `git show 41335f0:`).
  - All 13 inbox sources match their `source_inventory.tsv` sha256.
  - For each of the 12 bundle files, `diff source bundle` shows only additions, in three places: the copyright
    block at the top, the module doc after the imports, and the appended section before the closing `end`.
  - No deposit line is changed or deleted. The one exception is MatrixPhaseBridge's 4-line SPDX comment, which was
    replaced (see N4).
  - Imports are identical.
- CoherenceSpeedLimit is absent: no file and no root import. The stated reason checks out: its `trace_motion_min`
  has the same statement as main's `CoherenceMotion.trace_step_abs_le_min`.

**(b) FILE_OPENS short-name handling: CONFIRMED, one wording nit (N2).**
- Short names collide between namespaces in the build: `window_step` and `window_all_steps` (WindowMax and
  HeteroStepRef), and `mode_sum`, `one_step_bound`, `eigenmode_stable`, `reference_mode_link`, `probe_step_values`
  and `probe_energy_value` (TransientBridge and TransientParameter), plus defs such as `step`, `energy` and `mode`.
- FILE_OPENS opens exactly one bundle namespace per file. The exception is EMAFiniteSum, which opens CausalEMATracking
  and EMAFiniteSum; those two share no names. None of these namespaces is in the global `OPENS`.
- Ambiguity could not fake a pass. The refutation (b) and the control (c) use the same preamble, and my negative
  controls show the refutation fails closed.

**(c) SPEC §17.4 merge note: CONFIRMED correct.**
- With uniform weights, HeteroStepRef's row condition is `dt·(N−1)b ≤ 1`, i.e. `c ≤ 1/(N−1)`. WindowMax's
  `coefficient_bound` needs `N ≥ 2` and `N·c ≤ 2`, and `1/(N−1) ≤ 2/N` ⟺ `N ≥ 2`.
- HeteroStepRef's `growth_witness` uses a node-uniform window `(+1, −1, …)`, which is not mean-zero, so it does not
  contradict WindowMax.
- At `N = 3`, `c = 3/5`: WindowMax's coefficient is `1/5 + 3/5 ≤ 1`, and the hetero head is `|1 − 2·6/5| = 7/5`.
  Both modules are complementary. TransientParameter's `step` is WindowMax's `next` at `N = 3`, `d = 1`, so for
  `2/3 < c < 1` you get one-step max-norm growth (`exact_growth_witness`) while the mode is spectrally stable
  (`stable_roots`). That is consistent: transient growth, not a contradiction.
- Scope wording: see N3.

**(d) M131–M190 / E21–E23 expectations: CONFIRMED.**
- 26 statement mutants (M131–M156) were all REJECTED (build rejected, refuted with standard axioms, term-specific).
- 34 definition mutants (M157–M190) were all KILLED by their declared probes.
- E21–E23 were not killed and T1–T4 were flagged invalid.
- The pins move consistently: 79+26=105, 51+34=85, 20+3=23.

## Negative controls: can the checks fail? (my own, not the author's script)

**Harness:** filtered runs on a copy (`/workspace/r001_bnd_nc`). Logs: `/workspace/r001_bnd_nc.log` and `r001_bnd_nc2.log`.
- NC1: I narrowed `WindowMax.probe_next_values` to slot 1 only. M182, M183 and M184 then **SURVIVED (BAD)**; M185
  was still killed. The probe rule really does depend on the probe.
- NC2: I made E21 non-equivalent (`- v 0 * c`) with the real probe in place. It was **KILLED (BAD)**, giving 22/23
  and RESULT FAIL. The equivalence controls can fail.
- NC3: I gave M149 the wrong refuter (`false_coefficient_no_size`). Result: **NOT REJECTED (BAD)**.
- NC4: I added a cosmetic statement mutant, `(ht : n·c ≤ 2 ∧ True)`. Result: **NOT REJECTED (BAD)**; it cannot
  pass as a weakening.
- A filtered run always reports RESULT FAIL (partial-run guard), as designed.

**pytest red-team:** `review_r001/bundle_82a5a1f/redteam_r001.sh` and its output `redteam_r001.out`; all 16 rows
came out as predicted. Unlike the author's script, every Lean edit also regenerates
AIEF_LEAN_GATE_SOURCE_SHA256SUMS.txt, so the file-hash pin cannot be what catches a variant.
- R0, the baseline: passes (expected).
- R2, a deposit threshold weakened: caught by the deposit digest.
- R4 (`sorry` in the appended section) and R5 (a new `native_decide` theorem): caught by the escape-hatch test.
- R6 and R7 (`#print axioms` dropped or retargeted): caught.
- R8 (EMAFiniteSum opens changed), R9 (a pin pointing to another file's probe) and R10 (a no-op mutant edit): caught.
- R13 (a stray CoherenceSpeedLimit.lean), R14 (a deposit theorem moved into the appended section) and R15 (a wrong
  engine line cited): caught.
- **R1** (a Lean probe value changed, sums regenerated) **survives all pytest**. Only the Lean build catches it,
  because −3/4 is false. See N1.
- **R11** (E21 made non-equivalent): survives pytest. Only the Lean harness catches it (NC2). That is acceptable.
- **R12** (SPEC §17.4 threshold rewritten to a wrong `c ≤ 1/N`): **survives all pytest**. See N1.
- R3 (a blank-line-only deposit change): survives, by design (blank lines are ignored).

## Other verifications

- **Hash-pinned artifacts untouched.** The diff touches none of Pinned/, lean/AIEFProofs*, lean/AIEFFreezeCore,
  ART-0076, or `aief_experiment_engine_v1.py`; check_artifact_pins and check_pinned_restatement are rc 0.
- **No forbidden or private files** in the diff: no private_literals.txt, tree_c9907a6.json, 040282 source_state
  `*main_branch*.json`, Arena main_compare.json or p5_compare.json, logs, .lake, agent-tools, auditvenv, scrub,
  audit_evidence, or audit_inbox paths.
- **No personal details or author emails added.** The only name is the repository's standard copyright line (already
  in 36 files on main). Commit metadata is a GitHub noreply address (see N7). One docstring path,
  `/workspace/venv-pt/bin/pytest`, matches existing tests.
- **Engine citations.** These match `aief_experiment_engine_v1.py`:
  - lines 823 and 830–839, delayed = `history[0]`;
  - `np.sin(delayed[None,:] - theta[:,None])` and `np.mod(…, 2π)`;
  - lines 841–844, append/pop.
  HeteroGuard's constants (dt 0.01, a 1.0, δ 0.05, tol 1e-9, q 1.5) match FROZEN_* at engine L64–80.
- **Claims and registry wording against the proofs.** I read every deposited statement. README and SPEC §17.1
  match what is proved, including:
  - the hypotheses for EmaNearUnit (phase spread assumed) and CausalEMATracking (`0 ≤ α`);
  - TransientParameter's `21/8` (the true sup at c = 1 is (3+√5)/2 ≈ 2.618, so "near-sharp" is honest);
  - the Transient "queue-copy artifact" disclaimer.
  Exceptions: N3 and N4.

## Findings (numbered)

**N1 (test honesty, non-blocking but should be fixed or relabelled).** Two tests in
`test_lean_gate_arena_bundle.py` exist only to pass.
- What they are:
  - `test_probe_and_witness_values_exact` and `test_window_max_and_hetero_are_complementary` never read a Lean file
    or the SPEC.
  - They recompute constants in Python. Some lines are pure tautologies: `v[1] != 1` with v[1] = 4,
    `abs(1 - 0 * 1) + 1 == 2`, and the M146/M147 polynomial constants.
  - R1 and R12 show neither test can catch a change to the thing it is named after.
- Why it matters:
  - The Lean build is the real check for probe values, so nothing false can get in.
  - But SPEC §17.5 describes these as pinning "the probe and witness values in exact arithmetic, the §17.4
    inequality", which overstates them.
  - The author's "11/11 caught" also overstates the test file. At least probe-value-changed, and with it
    sorry-inserted and edited-deposit-proof, were also tripped by the stale SHA256SUMS pin, because the script
    never regenerated the sums.
- Fix, either of:
  1. Parse the probe statements from the Lean source (e.g. assert `"= -1/2 ∧"` in `probe_next_values`) and the
     §17.4 thresholds from the SPEC text.
  2. Rename the tests and docstrings to say "worked arithmetic (documentation, cannot fail)".
- Also correct the redteam_test.sh baseline label.

**N2 (wording).** The `lean_mutation_check.py` comments (header L125 and above FILE_OPENS) say a refutation opens
"never two bundle namespaces at once". EMAFiniteSum opens two: CausalEMATracking and EMAFiniteSum. That is harmless
because they share no names, and the test pins it, but the comment should say so.

**N3 (scope wording).** README row and SPEC §17.1 for WindowMax and HeteroStepRef:
- The proved link is the derivative at the in-phase frozen state: `orbitPath … Ω = 0`, base θ = 1, fixed weights.
- "All perturbations" means all perturbations of that one linearised map, iterated. That only matches an engine
  linearisation along an orbit when cos(d·dt·Ω) = 1. The engine's heterogeneous ω has no such in-phase orbit.
- HeteroStepRef's module doc says "at Ω = 0". README and SPEC do not.
- Add one clause, e.g. "(linearised at the in-phase state, Ω = 0)".
- `HeteroGuard.engine_constants_safe` is exact-rational algebra on the defaults (dt·cap ≈ 0.0063 ≪ 1), not a
  statement about runs. The doc says this; keep it that way in any claim text.

**N4 (provenance, minor).** MatrixPhaseBridge's replaced SPDX comment carried "lead-note date conflicts, see note".
- The new doc keeps the session date but drops that caveat.
- SPEC §17.1 says the session-date note is "kept", which is only partly true.
- There is no "note" in the deposit file itself.
- Restore the caveat in the module doc, or say it was dropped.

**N5 (coverage disclosure).** Several deposited theorems have no statement mutant, for example:
- EmaNearUnit: `trace_projection_bound`, `trace_norm_bound`, `near_unit_of_phase_spread`;
- EMAFiniteSum: `delayed_tracking_sum`;
- ReachableQueue: `step_reachable_consistent`;
- QueueComposition: `finite_abstract_step`, `initialized_trajectory_bridge`;
- MatrixPhaseBridge: `matrix_head_direction`;
- TransientBridge: `after_first_bound`, `eigenmode_stable`; TransientParameter: `eigenmode_stable`;
- HeteroStepRef: `window_all_steps` (only `window_step` is mutated).

The SPEC doesn't claim full coverage, but §17.2 should say these are unmutated.

**N6 (CI time budget).** The GitHub "Lean proof check" on 82a5a1f took 31 m 43 s, against ~14–19 min on main
(Nov 18–20 runs) and a 60-min job timeout. Locally the mutation harness took 1277 s. Headroom is shrinking with each
intake, so watch it before the next mutant batch.

**N7 (info).** Both commits are authored and committed as the owner's GitHub account (noreply address), not a
seat identity. That matches 4 earlier commits on main. No email or personal detail leaks. Flagged only because the
seat conventions differ.

**Independence limit (disclosed).** `.lake/packages` came from the author's working tree; I did not re-download or
rebuild Mathlib.
- All 9 packages are at their `lake-manifest.json` revs and git-clean (tracked files), including the restored
  mathlib `scripts/bench/build`.
- Project oleans were rebuilt from scratch: the gate removes `.lake/build`.
- The prebuilt Mathlib oleans (2042) were not rebuilt by me.

**Out of scope (pre-existing on main, not this diff).** The `repo-checks.yml` comment says tests_modular expects
"43 passed"; the actual result is 60 passed, 2 skipped, 2 xfailed.

## Not done

I did not push, edit the branch, or open the PR. The non-author PR, from exact sha 82a5a1f, is now the next step if
the owner and Auditor Seat 002 accept CLEAN WITH NOTES. N1–N4 can go in a follow-up commit (which would need a short
delta re-audit) or a later PR.

Artifacts:
- `/workspace/review_r001/bundle_82a5a1f/` (check_a.py, redteam_r001.sh, redteam_r001.out)
- `/workspace/r001_bnd_{gate,mut,ci,pytest_lg,pytest_ci,nc,nc2}.log`
- `/workspace/r001_bnd_gatelogs/`
