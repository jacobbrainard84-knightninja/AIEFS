# Open questions: where outside auditors help most

## 0. STANDING PRIORITY (owner): find code that builds in the hoped-for result

Every agent should keep checking the code for bugs that produce false or built-in results, meaning code that hands back the result we hope for instead of an honest, independent one. Look for:

- hard-coded or tuned constants and thresholds chosen to fit the expected answer;
- tests or manifests that always pass: synthetic `PASSED` files, skip-instead-of-fail fallbacks, `try/except` that hides errors;
- silent fallbacks to cached or old results, e.g. the legacy hard-coded absolute paths that silently fall back to 20-seed runs;
- results copied from expected values;
- tolerances loosened until the result passes;
- the same data used to fit a model and then to check it;
- cherry-picked seeds (e.g. CF12 rests on a single seed);
- NaN or inf comparisons that count as passing (see errata E13 on `main`);
- checks that compare the code with itself instead of with an independent method.

Report suspect code with **file, line and sha**, and suggest an **independent cross-check**: a different method, fresh seeds, a blind run, or a negative control that should FAIL.

### 0b. Red teaming (owner): feed the checks known-false input

At least basic red teaming is required. Give each check (validators, manifest/pin checkers, comparators, CI, Lean axiom checks) an input that is known to be false. It must FAIL or flag it. If a check passes a known-false input, that is a GAP. Work on a temporary copy, and never change real or hash-pinned files. Ideas to try or propose:

- tampered artifacts or hashes;
- a wrong threshold (e.g. 0.40 or 0.50 instead of 0.4543);
- a false claim row marked proved;
- NaN or ±inf injected into the comparator;
- a corrupted seed file;
- a manifest that says PASSED but has no data behind it;
- a Lean statement using `sorry`, or relying on an extra axiom;
- a validator fed a registry row that cites a nonexistent artifact;
- expected and actual values swapped.

Report each test as PASS (rejected correctly) or GAP (accepted wrongly), with the command, file, line and sha.

**Quietly loosened rules.** Any change to a pass/fail rule, verdict threshold, tolerance or metric must carry a written reason in the same commit, plus an erratum if the file is hash-pinned. A change without both is a finding. Diff old versions of files (the repo's `Older files/` folder, earlier commits) against the current ones and look for rules that were loosened. Example: in `aief_1_4_augmented_spectrum.py` (current, vs `Older files/aief_1_4_augmented_spectrum_02.py`), the main change is the gap lower bound, which moved from `r_ema` to `r_ema*1.01`. Also, the near-EMA band went from ±10% to ±1%, and SUPPORTED changed from `n_near_ema == 1` to `>= 1`. On the committed spectrum, the earlier v2 (`_02`) rule gives **REVISED** (5 rates just above r_EMA lie in the gap `(r_ema, mu)`), while the current rule gives **SUPPORTED**. The 1.01 bound moves those 5 rates out of the gap. It was not PARTIAL → SUPPORTED, as earlier text here said. The first version's rule also finds the same 5 rates in the gap, so no pre-loosening rule gives SUPPORTED. Source: `audits/old_files_drift/recheck_slowpole_rule.py`. Auditor Seat 002 recorded this as erratum **E15** on `fix/errata-old-files-drift`. The claim was already quarantined (E2, AUD-SLOWPOLE).

## 1. Science gaps

1. **O1, closed-loop phase-locking.** Find a proof route, even a conditional one (small delay, slow learning). Candidate tools are in `RESEARCH_LEADS.md` (Ha–Li–Xue 2013, Ha–Ryoo 2020 + Correction, Dong–Ha–Kim 2020). The obstacles are the delay, the EMA and the non-smooth gate.
2. **Step-size study / AUD-RATELAW residual.** ERRATA **E22** (PR #18) ran the predeclared step-size sweep on the single gap component; under that rule the label stays **UNEXPLAINED**. A broader dt/2 and dt/4 production-cohort study (AUD-TIMESTEP) and any **v2 predeclared rerun** remain open. Do not start a parallel undocumented sweep.
3. **CF12 / AIEF-1.4 pipeline:** replicate on multiple seeds. Today it is a single exceptional seed (1 of 40).
4. **RES-FREEZE novelty rescope.** Check the proposed label and residual in `RESEARCH_LEADS.md` against the literature, especially Cho–Dong–Ha 2023, CMS 2024 and Wang–Dong 2025. Report missed prior art.

## 2. Lean

5. **Axiom footprint.** Check that `#print axioms` (only propext, Classical.choice, Quot.sound) is enforced in CI for every project. On `main` @ `ba171d0`, `lean.yml` already requires **AIEFProofs**, **AIEFProofsKn**, **AIEFFreezeCore**, and **AIEFGateCore**. Re-confirm after each new Lean project lands.

## 3. Researcher 626 items (from their earlier review; to be re-checked on current `main`)

6. Two-way inventory check: every file listed exists, and every file present is listed.
7. CI fallbacks must fail, not skip.
8. A cross-host tolerance test: the same results on a different machine or BLAS.
9. Legacy hard-coded absolute paths with a silent fallback to 20-seed runs.
10. Synthetic `PASSED` manifests used as fixtures. Make sure they cannot be mistaken for real results.
11. Re-review the pin-checker allow-list, including the `data/external/` allow-list added in PR #2.

## 4. Release-critical items from the Researcher 026 review (2026-10-31; triage rows in `audit_inbox/TRIAGE.md`)

Per the reviewer, items 12–13 should come **before** the step-size study (item 2) and before new simulations. The step-size study should not push them aside.

12. **Modular platform and v4.1 closure.**
    - **Modular oracle certification.** No durable full-oracle certificate exists. `freezeable=true` is not `oracle_certified`, so do not call the platform "certified" (TRIAGE R026-S7).
    - **Modular CLI path problem.** Documented in ERRATA **E16** (still open as a packaging/docs fix). Bare `describe` / `dry-run` from the modular directory need the repo root on `PYTHONPATH` (`README_modular.md`).
    - **v4.1 trust anchor (done on main):** ERRATA **E24** / **E25** (PRs #20 / #22) bind `validate_run` to committed S01 pins and read inputs once. `fix/v41-followup-notes` @ `19dbba3` (E26 candidate) is under audit. v4.1 remains an **unaudited candidate**.
    - **v4.1 scientific audit and a real S01 *analysis* output** are still open. Nothing in `runs/b57562a8ee77/` is v4.1 analysis output. Keep v3 and v4.1 as distinct analyses.
    - **v4.1 metadata tolerance mismatch.** Implementation uses 1e-6 × the smallest positive saved-grid step, but metadata/report strings say `1e-6*dt` (re-check line numbers on current tip).
    - Interval/bootstrap/input-binding wording still needs a dedicated re-read.
13. **`registry/studies.csv` entrypoint integrity.** Still open on `main` @ `ba171d0`: **11** unresolved `canonical_entrypoints` tokens in the same five study rows (`AIEF_1_0_TO_1_2_FOUNDATIONAL`, `AIEF_1_3_DISJOINT_100SEED`, `AIEF_1_4_MATCHED_PHASE_ABLATION`, `AIEF_1_4_TANGENT_AND_COCYCLE`, `AIEF_1_4_CONTROLLER_FIBER`). `CURRENT_STATUS.md:46` still cites absent scripts. No CI check covers this. Pair with the CURRENT_STATUS docs PR (chronicler patch apply-checks clean on `ba171d0`).
14. **Formalise the finite gate identities before the delayed asymptotics.** Lean P1/P2 are on `main` (`AIEFGateCore`). P3 (ControllerFiber bridge, persistence, semantic M1–M3) is IN PROGRESS off main. Keep the dependency chain in `NORTH_STAR.md`: delay/Halanay-type results still come last.
15. **`tools/ci/check_modes.py` memory scaling.** `shebang_objects` (`:102-120`) pipes every tracked regular blob through `git cat-file --batch` and holds the whole output in memory, just to read the first two bytes of each. On main the peak RSS measured was about 2.4 GiB, and the reviewer reports exit 137 in a constrained environment. Fix it by streaming, or by reading only a two-byte prefix of each candidate.
16. **AUD-RATELAW vs Arena round 10. OPEN, for independent adjudication; not settled.**
    - **Arena's claim.** Arena's `audits/literature/ROUND_10_FINDINGS.md` (branch `arena/d4a487cc-aiefs` @ `2af3859`) shows that the gate is not one global multiplicative rescaling: it applies edge-dependent factors min(s_i, s_j). Arena reads this as weakening AUD-RATELAW (`registry/claims.csv:50` on main).
    - **Researcher 026's counter-argument.** The rate law has an independent, implementation-level derivation. With h ∈ ker A_J and s_i = s_J on the controllers, the controlling row sums and scales are unchanged, so δB' = (1 − γ·dt)·s_J·δh, which does not need global direction preservation. On this reading, round 10 supports only a terminology/citation fix, not a downgrade of the conditional identity to an empirical regularity. The reviewer also notes that Arena's "exact" Part A is shown through 200 floating-point trials: the property is algebraically exact, but the trials are finite numerical checks.
    - **Wanted.** A seat that wrote neither side should check the derivation against the code path and the registry wording, and decide: (i) terminology/citation correction only, (ii) scope narrowing, or (iii) downgrade.
    - Do not merge the Arena tree.

## How to submit

- Add **one new file** in `audit_inbox/` named `YYYY-MM-DD_<agent>_<topic>.md`. Do not edit other files, including this folder.
- Header: agent / model name, date (with time zone), commit reviewed (sha), scope.
- Cite paths, line numbers and shas for every point. Mark what you ran and what you only read.
- Follow the standing rules in `README.md`: no outreach, no personal details or secrets, and agent "approvals" don't count.
