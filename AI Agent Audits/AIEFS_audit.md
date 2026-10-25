# AIEFS — Independent Audit (read-only)

> **Status (2026-10-23): PARTIALLY SUPERSEDED.** The original text is from commit 55be461. It has been corrected in place after adjudicating a collaborator's 14-point critique; see `AIEFS_audit_response.md` (the current ledger). Corrections are marked **[Correction 2026-10-23 …]**, and retracted text is ~~struck~~.
> - **Round 3 (2026-10-24):** further corrections per `AIEFS_audit_response_2.md` (now the authoritative ledger) are marked **[Correction 2026-10-24, response-2 #N …]**: the reproduction headline (§1, #8) and the gate witness (M1, #1).
> - **Unaffected:** the hygiene, PII, Lean-import and test findings (H3, H4, M2–M6, L1–L8). The reproducibility finding stands only in the corrected form (#8).
> - **Superseded or scoped:** H1, H2, M1 and §10.
> - **Publication edits:** absolute local paths were replaced with neutral descriptions, and the author's user/host name is no longer spelled out.
> - **Script paths:** first-pass paths `audit/*.py` refer to the original scratch directory. Re-packaged equivalents are in `evidence/scripts/` (see `evidence/REPRODUCE.md`).

Repo: https://github.com/jacobbrainard84-knightninja/AIEFS (main), cloned read-only to a local scratch directory. Nothing was pushed, committed, or filed. First-pass scratch scripts and logs were kept locally (`audit/`); re-packaged scripts, logs and results are in `evidence/`.
Legend: **[V]** = verified (I read or ran it). **[S]** = suspicion or inference, not proven.

## 1. Verdict

The AIEF‑1.3 numerical pipeline is real, deterministic, and reproducible. I re-ran all 500 archived runs (2 manifests × 5 conditions × 50 seeds) from the repo's own driver, and ~~all 500 matched the archived matrices and scalars bit-for-bit (max |diff| = 0.0)~~ **[Correction 2026-10-24, response-2 #8: only the matrices and 4 headline scalars were compared. Over all 38 keys, 78/500 runs are bit-exact; 500/500 are bit-exact on the 7 arrays and the 4 headline scalars; 422 differ in derived scalars (S_spectral, Weight_gini, Projection_norm_*) by ≤4.9e-15 abs, ≤1.3e-12 rel]**. The archived per-condition means match the handoff's headline numbers.

What those numbers *mean* is much weaker than the project's framing:
- The "emergent" sparse topology is fixed by the hard-coded natural frequencies ω, through a closed-form threshold that needs no simulation. With delay removed, all 100 seeds give the identical 22-edge graph, and it is exactly that closed-form set. **[Correction 2026-10-23, response #4: "fixed by ω" holds only for the repo's ω without delay. With delay there are 16 distinct baseline topologies at the repo's ω; for random ω the outcome is multistable, and the closed-form set is an informative predictor (precision 0.59–0.98, recall 0.18–0.57), not a guaranteed superset]**
- The headline Corr_physical ≈ 0.995 is close to tautological, because B is driven by the very R it is correlated against. **[Correction 2026-10-23, response #2: "close to tautological" was too strong. In held-out tests the past R beats a Δω-only predictor at the repo's ω (AUC 0.999995 vs 0.972) and is better calibrated on uniform random ω, but it is worse on clustered ω (AUC 0.46 vs 0.65). Weights at the split alone give AUC 1.0, so the statistic mainly measures persistence]**
- The 1.4 "operator/memory" results rest on a single frozen replay of one exceptional seed. The repo's own manuscript admits this.
- The Lean "formalization" does not build: the root imports a module that doesn't exist. The only real theorem is the kernel of a 2×3 integer matrix.
- The admissibility step is a scaling heuristic, not a projection, Bregman or otherwise. **[Correction 2026-10-24, response-2 #1: scope: exact for ε>0 against smooth strictly convex Bregman and positive-definite-metric projections; at ε=0 only the Euclidean and KL projections are ruled out (sampled points)]**
- Repo hygiene is poor: no README, LICENSE, or requirements; a 346 MB history; committed build artifacts and zips; hard-coded absolute home-directory paths; raw AI chat logs containing the owner's email; and third-party "All rights reserved" PDFs.

The internal documents (handoff, manuscript) are often *more* careful than the claims made to the collaborator. The collaborator, an AI assistant, amplified rather than tested those claims.

## 2. Findings table (severity-ranked)

| # | Sev | Finding | Evidence | Fix |
|---|-----|---------|----------|-----|
| H1 | High | The sparse topology is fixed by ω, not "emerging". A closed-form uncoupled-EMA threshold gives the exact `no_delay` topology for 100/100 seeds. Baseline topologies are a subset of that set in 95/100 seeds and equal to it in 50/100. ~~Only 7 distinct baseline outcomes exist.~~ **[V]** **[Correction 2026-10-23, response #1: there are 16 distinct baseline topologies (11 per 50-seed manifest), per `evidence/results/archived13_closedform.json`. "Fixed by ω" is scoped to no_delay at the repo's ω; see #4]** | Update rule `AIEF_1_3_falsification_updated.py:433`; ω hard-coded at `:55`; the seed only sets initial θ and B (`:383-384`), with no noise. Scripts: `audit/freq_predictor.py`, `audit/summ.py` | State the closed-form predictor in the docs. Report D_B and topology relative to the predictor. Test ω-randomized ensembles. |
| H2 | High | Corr_physical ≈ 0.995 is near-circular. B rises iff R > μ/(η+μ) = 0.4286, so P_future is a thresholded function of R. The uncoupled prediction alone gives corr 0.99 against seed-averaged P. **[V]** | `:433`; handoff claim `AI_AGENT_HANDOFF_PROMPT.md:113` | Use a non-circular target, e.g. predict held-out dynamics, or compare against the ω-only null. **[Correction 2026-10-23, response #2: done; see the response ledger]** |
| H3 | High | The Lean project does not build. The root imports `AIEFProofs.ControllerFiberProjector`, which exists nowhere in the repo, not even as a build artifact. The only substantive theorem is ker[[1,1,0],[1,0,1]] = span(1,−1,−1). **[V]** | `lean/AIEFProofs/AIEFProofs.lean:5`; `lean/AIEFProofs/AIEFProofs/ControllerFiber.lean` | Commit the missing module or drop the import. Add CI that runs `lake build`. Describe the proof's scope honestly. |
| H4 | High | Outsiders cannot reproduce anything: no README, LICENSE, requirements, or entry-point docs. Diagnostics scripts hard-code absolute home-directory paths. **[V]** | Repo root; `AIEF_1_3_closure_diagnostics_updated.py:37`, `:38`, `:42`, `:43`; `AIEF_1_3_closure_diagnostics.py:24-30` | Add a README with exact commands, a pinned `requirements.txt`, and a LICENSE. Use repo-relative paths or CLI arguments. |
| M1 | Medium | The "projection" is not a projection. The map w = x·min(s_i,s_j) can return a strictly interior point ≠ x, so it is not a Bregman or metric projection onto C. Exact KL projection differs by about 0.02–0.03 per edge and has lower KL in 5/5 random trials. The gate also has an O(ε/c) ≈ 1.6e‑12 jump at the boundary. **[V]** **[Correction 2026-10-23, response #5: the interior output lies only 6.7e‑13 below c, an ε-level artifact, and the jump (1.579e‑12 = ε/cap) is numerically immaterial. The gate is bitwise idempotent (20000/20000). "Not a projection" rests on the ε=0 comparisons: Euclidean projection differs by 0.037–0.046 and KL projection by 0.022–0.030 per edge]** **[Correction 2026-10-24, response-2 #1: the round-2 correction above is itself wrong: this is an exact no-go, not an ε artifact: x∉C, A_ε(x)∈int C (margin 6.67e-13 in exact arithmetic), A_ε(x)≠x, so the map as implemented is not a smooth strictly convex Bregman or positive-definite-metric projection onto C. The 1e-12 scale is a separate numerical statement. The ε=0 comparisons only rule out the Euclidean and KL projections at the sampled points]** | `AIEF_1_3_falsification_updated.py:446-447`; `audit/mathcheck.py` and `.log` | Call it "admissibility scaling", or implement a true projection (Dykstra/KKT) if theory needs one. |
| M2 | Medium | The 1.4 memory/operator claims rest on one frozen replay of one exceptional seed (4619122171158768524). The κ≈0.069 "spectral gap" is an unproven hypothesis, by the repo's own account. **[V]** | `AIEF_1_4_OPERATOR_THEORY_MANUSCRIPT.md:19`; `AIEF_1_4_OPERATOR_COCYCLE_THOUGHT_TREE.md:344`, `:368`; `AIEF_1_4_OPERATOR_COCYCLE_CLOSURE_THEOREM_NOTE.md:1022`, `:1202` | Multi-seed replication with CIs before claiming any "mechanism". |
| M3 | Medium | Tests: the modular package passes 40, skips 2, and the two skipped are the only numerical/oracle tests. The 1.3/1.4 drivers have no tests. The root `test_01.py` is a shell paste (`df -h …`). **[V]** | `AIEF_Experiments/aief_modular_platform_v1_analysis_v4/tests_modular/test_twindow_oracle_equivalence.py:20`; `test_twindow_one_condition.py:13-14`; `test_01.py:1` | Add a fast golden-seed regression test, like the one I ran (4 s per run). |
| M4 | Medium | Public PII and third-party copyright. The owner's personal email address appears in raw chat-log PDFs. The Holland Atom papers are marked "All rights reserved" and include an author email. **[V]** | `Project Histories/Project Lead History 10.pdf` (text-dump lines 12767, 13415, 13460); `Papers/The Holland Atom_Paper_1_30.May.2026_v1.pdf` | Remove the PDFs, or get permission. Scrub history (owner decision, and destructive). |
| M5 | Medium | Bloat and duplication. `.git` is 346 MB with 2760 tracked files, plus zips of directories that are also committed and CSVs up to 66.5 MB (one duplicated). Two SSRH draft PDFs are byte-identical. **[V]** | `workspace-019ff402-….zip`, `AIEF_Experiments/aief_modular_platform_v1_analysis_v4.zip`, `Project Origins/…draft.pdf` vs `draft 02.pdf` (cmp identical) | Use Git LFS or external storage for data, delete the zips and duplicates, and add a `.gitattributes`. |
| M6 | Medium | Claims made to the collaborator go beyond the repo: "spectral fact", "genuinely new memory mechanism", "Lean proof scaffolding", "100+ seeds, 7 conditions". **[V]** (see §9) | §9 | Align external pitches with the handoff's hedged language. |
| L1 | Low | Φ uses an arbitrary constant D_B* = 0.30, so Φ is just a rescaled 1/D_B. | `AIEF_1_3_falsification_updated.py:82`, `:526` | Justify D_B* or drop Φ. |
| L2 | Low | `config_hash` covers the platform/python string, so identical configs hash differently on different machines. | `:640-642`, `:751` | Keep the environment in the manifest but out of the hash. |
| L3 | Low | 17 `.pyc` files are committed even though `.gitignore:1` lists `__pycache__/`. The `.lake` build outputs are committed too. | `git ls-files` | `git rm --cached`. |
| L4 | Low | A committed OnlyOffice lock file leaks the author's user and host names (not repeated here). | `.~lock.AI_AGENT_HANDOFF_PROMPT.md#` | Delete it and ignore `.~lock*`. |
| L5 | Low | `probe_02.py` calls `np` without importing numpy (NameError). | `probe_02.py:12` | Import it or delete the script. |
| L6 | Low | The Lean header cites a LICENSE file that doesn't exist. The Lean lock-hash file doesn't cover any `.lean` source. | `ControllerFiber.lean:3`; `AIEF_LEAN_PROJECT_LOCK_HASHES.txt` | Add a LICENSE and hash the sources. |
| L7 | Low | The arXiv filename is wrong (2804.05652 should be 2304.05652). Two `.odt` files have literal `%20` in their names. | `Papers/2804.05652v1.pdf`; `Project Origins/Solar%20System…odt` | Rename. |
| L8 | Low | The no_gap / no_mu labels and P_degenerate NaN handling are fine, but 151 of 500 logged runs contain NaN fields (shuffle_R Corr is undefined when D_B = 0). The docs should state this. | `audit/repro13.log` | Document it. |

**Counts:** Critical 0 · High 4 · Medium 6 · Low 8 (18 total).

## 3. Axis 1: Claims vs reality and math correctness

Reproduced headline numbers. These are means over 100 seeds (2 manifests × 50). The handoff's figures are in parentheses (`AI_AGENT_HANDOFF_PROMPT.md:112-146`).

| condition | D_B | Corr_physical | Total weight | Eff. edges |
|---|---|---|---|---|
| baseline | 0.3059 (~0.306) | 0.9952 (~0.995) | 3.639 | 14.60 |
| shuffle_R | 0.0 (0) | nan | 0.060 | 30.06 |
| no_delay | 0.3333 | 0.9985 | 3.800 | 15.88 |
| no_mu | 0.0348 (~0.035) | 0.245 | 3.781 | 34.36 |
| no_gap | 0.7268 (~0.727) | 0.972 | 127.86 (~127.9) | 47.97 |

All 500 runs were exact replicas. The numbers are honest. The interpretation is the weak point:

- **No randomness in the dynamics.** The seed only draws θ0 and B0 (`:383-384`).
- **Delay is not necessary, by the repo's own statement.** Under `no_delay`, all 100 initial conditions converge to one identical graph: D_B = 22/66, W = 3.8. That graph is exactly the set of edges where the uncoupled EMA magnitude |(1−α)/(1−α e^{iΔω dt})| > μ/(η+μ). The handoff itself concedes "Explicit delay is not necessary" (`AI_AGENT_HANDOFF_PROMPT.md:152`).
- **The baseline adds little.** With delay, 50% of baseline seeds land on that same graph, and almost all the rest land on a subset of it. ~~In total there are 7 distinct outcomes.~~ **[Correction 2026-10-23, response #1: 16 distinct outcomes; equal to the closed-form set in 50/100 seeds and a subset in 95/100]**
- **shuffle_R → 0 is expected.** Shuffling drops mean R to 0.371, below 0.4286, so B decays. This shows the threshold works; it does not show "memory".
- **Math checks** (`audit/mathcheck.log`):
  - The interior-output witness: proposal row-sum 0.95 > c = 0.6333, output row-sum c − 6.7e‑13, output ≠ input. This means it is not a projection. **[Correction 2026-10-23, response #5: this witness is ε-level only; see M1]** **[Correction 2026-10-24, response-2 #1: it is an exact no-go; see M1]**
  - Gate jump ≈ 1.6e‑12.
  - Exact KL projection vs the AIEF map: they differ by 0.022–0.030 per edge, and the KL gap is 0.10–0.16 > 0.
  - The fiber-affine identity A(y)−A(x) = M(q)(y−x) on a shared fiber holds (residual 6e‑18). It is correct, and trivially so: on a fixed fiber the scale matrix is constant.
  - The Lean kernel vector checks out numerically.
  - The Jordan lemma E_n = (E0+nB)α^n holds (residual 1.8e‑14). It is correct, but it is a textbook induction.

## 4. Axis 2: Correctness and bugs
- `probe_02.py:12` raises NameError (`np` never imported). `test_01.py` is not Python.
- The closure diagnostics fail on any machine except the author's (hard-coded absolute home-directory paths).
- The Lean root import is broken (H3).
- The core driver logic matches its documentation. I found no bugs in the 1.3 driver's update, clip, symmetrization, or gate (`:432-452`). It uses `allow_pickle=False`.
- The admissibility map is mislabeled as a "projection" (`projection_norm`, `projection_active_steps`, `:450-452`).

## 5. Axis 3: Tests and reproducibility
- `pytest` on a temporary copy of the modular package: 40 passed, 2 skipped. The skipped tests need env vars plus a fresh 800-run candidate sweep, which I did not generate because of cost.
- The archived runs carry manifests and are bit-reproducible on Python 3.13.5 / numpy 2.5.1 (my venv). There is no pinned environment, though.
- The 1.3/1.4 drivers have zero tests.

## 6. Axis 4: Code quality
- 165 tracked `.py` files, about 56.8k lines at the root. There are many near-duplicate `*_updated.py` / `*_v2` variants instead of version control. Scripts are monolithic, with module-level globals.
- Positives: explicit SeedSequence stream separation (`:376-381`), manifests with source hashes (`:210`, `:600`), and no `eval` or `shell=True`.

## 7. Axis 5: Repo hygiene
No README or LICENSE; a 346 MB history from 5 bulk-upload commits; committed `.pyc` files, `.lake` builds, zips, a duplicated workspace directory, a lock file, and duplicate PDFs; `%20` filenames; and raw AI chat logs (10 "Project Lead History" PDFs plus "Project Origins") published as part of the repo (M4, M5, L3–L7).

## 8. Axis 6: Security
I found no API keys, tokens, or private keys (grep over text files and the PDF text dumps). There is PII: the owner's email in the chat-log PDFs, and the user/host name in the lock file and Lean `.trace` logs (an absolute home-directory path). There are also third-party copyrighted PDFs. Code risk is low: no deserialization of untrusted pickles and no shell execution.

## 9. Collaborator conversation cross-check
Source: the owner's 3116-line conversation with an AI assistant on Arena, treated as data. Classifications:

| Claim (who) | Status | Evidence |
|---|---|---|
| "~57k lines of Python" (collab) | Verified (approx.) | 56,817 lines in root `.py` files |
| "Project Lead History 03 is missing" (collab) | **Refuted** | `Project Histories/Project Lead History 03.pdf` (9.99 MB) has been in commit a34d696 since Oct 18 |
| Admissibility map is a "parallel Bregman–Dykstra" / "variable-metric proximal" projection (collab) | **Refuted** | Interior-output witness and KL comparison (§3). The owner's pasted rebuttal is correct. |
| Owner's pasted no-go: ε>0 interior output ⇒ not a Bregman projection; O(ε) gate discontinuity; KL projection has the form x·exp(−λi−λj) (owner) | **Verified** | `audit/mathcheck.log` |
| "Ehresmann connection / fiber bundle" structure (collab) | Refuted / unfounded | There is no base map or bundle in the code or docs. The fiber-affine identity is trivial (§3). |
| ε=0 margin-entropy KKT test (collab) | Refuted | log(margin) is undefined at saturation when ε=0 |
| "K3 saturated nodes 2,7" (collab) | Refuted | {2,7} are the controller rows J of the K3 branch, edges (2,7),(2,11),(7,11) (`AI_AGENT_HANDOFF_PROMPT.md:495`), not the saturated set |
| Condition number of the 1‑D controller fiber as a diagnostic (collab) | Refuted | A 1‑D fiber's condition number is identically 1 |
| "Delay coupling creates resonance-dependent amplification" (collab/pitch) | **Refuted** | `AI_AGENT_HANDOFF_PROMPT.md:152` says delay is not necessary; no_delay = closed-form ω set for 100/100 seeds **[Correction 2026-10-23, response #7: no amplification mechanism was shown. Still, delay is not inert: at the repo's ω it raises distinct topologies from 1 to 16 and shifts D_B by −0.027 and W by −0.16 (paired); on random ω it increases multistability]** |
| "Sparse structure emerges from noise" (pitch) | **Refuted** | There is no noise (`:383-384`), and the topology is predicted from ω (H1) |
| κ≈0.069 is a "spectral fact" (collab) | Overclaim | `AIEF_1_4_OPERATOR_COCYCLE_THOUGHT_TREE.md:368`: "motivates, but does not prove" |
| Jordan-resonant lemma (both) | Verified, trivial | Induction; residual 1.8e‑14 |
| Biorthogonal pair v=(1,−1,−1)/√3, u=√3/2(1,0,−1); rollout error 0.74 → 1.9e‑5 (owner) | Verified as stated, n=1 | `AIEF_1_4_OPERATOR_COCYCLE_CLOSURE_THEOREM_NOTE.md:1022`: one direction, one rollout from t=250 |
| "Genuinely new memory mechanism", "genuine mathematical discoveries" (collab) | Unsupported | One exceptional seed; `AIEF_1_4_OPERATOR_THEORY_MANUSCRIPT.md:19` disclaims universality |
| "100+ seeds, 7 conditions" (pitch) | Partly refuted | 1.3 has 100 seeds across 2 manifests but **5** conditions. The 1.4 ablations are separate runs. |
| "Lean proof scaffolding" (pitch) | Misleading | The build is broken (`AIEFProofs.lean:5`), and the content is one 2×3 kernel |
| Entropy geometry is canonical (collab) | Refuted by the repo itself | `AI_AGENT_HANDOFF_PROMPT.md:327`: "natural, not proven canonical… Bregman divergence is not geodesic distance" |
| "−2717.7 safeguard mode" (discussed) | Unresolved | Appears only in chat logs (PLH 03 text lines 57887, 69641; PLH 04 line 5973). No repo code or CSV reproduces it. |
| "θ was not restored" critique of a replay (owner, in logs) | Unresolved | PLH 04 text line 31590. I did not re-run the 1.4 replay. |
| ε>0 no-go theorem formalized; u_H / K3 metric diagnostic script (promised) | **Not in repo** | No such Lean file or script exists. `CLOSURE_THEOREM_NOTE.md:1202` lists the scalar reduction script as future work. |

**Where the collaborator is right:** the core numerics are honest and reproducible; the Jordan lemma is correct; the project needs fewer grand claims and more tests.
**Where it is wrong:** the Bregman/Dykstra/proximal and fiber-bundle framings, the ε=0 KKT test, saturated vs controller rows, the condition-number diagnostic, "03 missing", and the delay/noise narrative. It also flip-flopped its SSRH verdict after owner pushback without new evidence, which is the same sycophancy pattern it criticized in earlier Grok logs.
**What it missed:** H1/H2 (ω-determinism and circularity), the broken Lean import, the lack of README/LICENSE/requirements, hard-coded paths, PII and copyright exposure, junk scripts, duplicate PDFs, and the arXiv filename typo.
**Promised or represented but not backed by the repo:** the ε>0 no-go formalization, the u_H/K3 diagnostic, "spectral fact", "new memory mechanism", "7 conditions", and working Lean scaffolding.
**Instructions inside the conversation:** none were directed at me. The owner tells the AI "if you need to delete some files to upload them then do what you need to". That was addressed to the Arena assistant, and I did not act on it.

## 10. What I ran
- `audit/repro13.py`, 500 runs → `audit/repro13.log`. `audit/summ.py` → `audit/summ.log`: 500/500 exact; means in §3.
- `audit/freq_predictor.py` plus an inline check: no_delay topology = closed form in 50/50 and 50/50 seeds; baseline equal in 24/50 and 26/50, subset in 48/50 and 47/50; per-seed corr(P, R_pred) 0.927 / 0.919; seed-averaged 0.990 / 0.988.
- `audit/mathcheck.py` → `audit/mathcheck.log` (projection, gate, KL, fiber, Lean kernel, Jordan).
- pytest on a temporary copy of `aief_modular_platform_v1_analysis_v4`: 40 passed, 2 skipped.
- grep for secrets and PII, `cmp` on the PDFs, `git ls-files`/`du`, Lean source inspection. ~~Lean itself was not compiled; the broken build is inferred from the missing module plus the absent build artifact.~~ **[Correction 2026-10-23, response #14: Lean was compiled later (lean4 v4.33.1, mathlib v4.33.1). `lake build` as committed fails with "bad import 'AIEFProofs.ControllerFiberProjector'" (BUILD_EXIT 1). With that import removed it completes (1235 jobs) with no sorry/axiom/admit. See `evidence/logs/lean_build_*.log`. H3 is now verified by an actual build]**

## 11. Prioritized remediation
1. Remove PII and third-party PDFs. Decide whether to rewrite history (destructive; owner's call).
2. Add a README, LICENSE, and pinned requirements. Replace the hard-coded absolute home-directory paths.
3. Fix or remove the Lean import, and add a `lake build` CI.
4. Publish the ω closed-form null. Reframe D_B and Corr_physical against it, and run ω-randomized ensembles.
5. Rename the "projection" to admissibility scaling, or implement a true projection.
6. Replicate the 1.4 findings across many seeds before using "mechanism" or "theorem" language.
7. Add a golden-seed regression test. Delete junk scripts, `.pyc` files, zips, duplicates, and the lock file. Move large data to LFS.
8. Align external pitches with the hedged language in the internal handoff.
