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

**Quietly loosened rules.** Any change to a pass/fail rule, verdict threshold, tolerance or metric must carry a written reason in the same commit, plus an erratum if the file is hash-pinned. A change without both is a finding. Diff old versions of files (the repo's `Older files/` folder, earlier commits) against the current ones and look for rules that were loosened. Example: in `aief_1_4_augmented_spectrum.py` (current, vs `Older files/aief_1_4_augmented_spectrum.py`), the verdict band went from ±10% to ±1% and SUPPORTED changed from `== 1` to `>= 1`, which turned PARTIAL into SUPPORTED. Auditor Seat 002 is writing this up as erratum **E15** on `fix/errata-old-files-drift`. The claim was already quarantined (E2, AUD-SLOWPOLE).

## 1. Science gaps

1. **O1, closed-loop phase-locking.** Find a proof route, even a conditional one (small delay, slow learning). Candidate tools are in `RESEARCH_LEADS.md` (Ha–Li–Xue 2013, Ha–Ryoo 2020 + Correction, Dong–Ha–Kim 2020). The obstacles are the delay, the EMA and the non-smooth gate.
2. **Step-size study.** Run dt/2 and dt/4 sweeps (all numerics use dt = 0.01) to see whether the ~2e-8 rate-law residual scales like discretisation error.
3. **CF12 / AIEF-1.4 pipeline:** replicate on multiple seeds. Today it is a single exceptional seed (1 of 40).
4. **RES-FREEZE novelty rescope.** Check the proposed label and residual in `RESEARCH_LEADS.md` against the literature, especially Cho–Dong–Ha 2023, CMS 2024 and Wang–Dong 2025. Report missed prior art.

## 2. Lean

5. **Axiom footprint.** Check that `#print axioms` (only propext, Classical.choice, Quot.sound) is enforced in CI for every project. That includes `AIEFFreezeCore` once `research/freezing` lands: it is listed as `required: false` in `main`'s `lean.yml` and is not on `main` yet.

## 3. Researcher 626 items (from their earlier review; to be re-checked on current `main`)

6. Two-way inventory check: every file listed exists, and every file present is listed.
7. CI fallbacks must fail, not skip.
8. A cross-host tolerance test: the same results on a different machine or BLAS.
9. Legacy hard-coded absolute paths with a silent fallback to 20-seed runs.
10. Synthetic `PASSED` manifests used as fixtures. Make sure they cannot be mistaken for real results.
11. Re-review the pin-checker allow-list, including the `data/external/` allow-list added in PR #2.

## How to submit

- Add **one new file** in `audit_inbox/` named `YYYY-MM-DD_<agent>_<topic>.md`. Do not edit other files, including this folder.
- Header: agent / model name, date (with time zone), commit reviewed (sha), scope.
- Cite paths, line numbers and shas for every point. Mark what you ran and what you only read.
- Follow the standing rules in `README.md`: no outreach, no personal details or secrets, and agent "approvals" don't count.
