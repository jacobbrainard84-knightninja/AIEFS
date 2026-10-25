# [publication copy, 2026-10-24] local paths and personal values replaced by <placeholders>; otherwise verbatim.
import re,sys
def C(n, txt): return f" **[Correction 2026-10-23, response #{n}: {txt}]**"
def apply(src, edits):
    for old,new in edits:
        if src.count(old)!=1: sys.exit(f"edit not unique/found ({src.count(old)}): {old[:80]!r}")
        src=src.replace(old,new)
    return src
HOMEP="a hard-coded absolute home-directory path (author's user name; not repeated here)"
# ---------------- audit ----------------
a=open('<repo-clone>_audit.md').read()
A_HDR="""> **Status (2026-10-23): PARTIALLY SUPERSEDED.** The original text is from commit 55be461. It has been corrected in place after adjudicating a collaborator's 14-point critique; see `AIEFS_audit_response.md` (the current ledger). Corrections are marked **[Correction 2026-10-23 …]**, and retracted text is ~~struck~~.
> - **Unaffected:** the reproducibility, hygiene, PII, Lean-import and test findings (H3, H4, M2–M6, L1–L8).
> - **Superseded or scoped:** H1, H2, M1 and §10.
> - **Publication edits:** absolute local paths were replaced with neutral descriptions, and the author's user/host name is no longer spelled out.
> - **Script paths:** first-pass paths `audit/*.py` refer to the original scratch directory. Re-packaged equivalents are in `evidence/scripts/` (see `evidence/REPRODUCE.md`).

"""
a=apply(a,[
("# AIEFS — Independent Audit (read-only)\n\n", "# AIEFS — Independent Audit (read-only)\n\n"+A_HDR),
("cloned to `<repo-clone>`. Nothing was pushed, committed, or filed. All scratch scripts and logs are in `<round1-scratch>/`.",
 "cloned read-only to a local scratch directory. Nothing was pushed, committed, or filed. First-pass scratch scripts and logs were kept locally (`audit/`); re-packaged scripts, logs and results are in `evidence/`."),
("and it is exactly that closed-form set.", "and it is exactly that closed-form set."+C(4,"\"fixed by ω\" holds only for the repo's ω without delay. With delay there are 16 distinct baseline topologies at the repo's ω; for random ω the outcome is multistable, and the closed-form set is an informative predictor (precision 0.59–0.98, recall 0.18–0.57), not a guaranteed superset")),
("because B is driven by the very R it is correlated against.", "because B is driven by the very R it is correlated against."+C(2,"\"close to tautological\" was too strong. In held-out tests the past R beats a Δω-only predictor at the repo's ω (AUC 0.999995 vs 0.972) and is better calibrated on uniform random ω, but it is worse on clustered ω (AUC 0.46 vs 0.65). Weights at the split alone give AUC 1.0, so the statistic mainly measures persistence")),
("hard-coded `<home>` paths;", "hard-coded absolute home-directory paths;"),
("Only 7 distinct baseline outcomes exist. **[V]**", "~~Only 7 distinct baseline outcomes exist.~~ **[V]**"+C(1,"there are 16 distinct baseline topologies (11 per 50-seed manifest), per `evidence/results/archived13_closedform.json`. \"Fixed by ω\" is scoped to no_delay at the repo's ω; see #4")),
("compare against the ω-only null. |", "compare against the ω-only null."+C(2,"done; see the response ledger")+" |"),
("Diagnostics scripts hard-code `<home>/...` paths.", "Diagnostics scripts hard-code absolute home-directory paths."),
("The gate also has an O(ε/c) ≈ 1.6e‑12 jump at the boundary. **[V]**", "The gate also has an O(ε/c) ≈ 1.6e‑12 jump at the boundary. **[V]**"+C(5,"the interior output lies only 6.7e‑13 below c, an ε-level artifact, and the jump (1.579e‑12 = ε/cap) is numerically immaterial. The gate is bitwise idempotent (20000/20000). \"Not a projection\" rests on the ε=0 comparisons: Euclidean projection differs by 0.037–0.046 and KL projection by 0.022–0.030 per edge")),
('leaks the user/host name ("<redacted><redacted>").', "leaks the author's user and host names (not repeated here)."),
("In total there are 7 distinct outcomes.", "~~In total there are 7 distinct outcomes.~~"+C(1,"16 distinct outcomes; equal to the closed-form set in 50/100 seeds and a subset in 95/100")),
("output ≠ input. This means it is not a projection.", "output ≠ input. This means it is not a projection."+C(5,"this witness is ε-level only; see M1")),
("(hard-coded `<home>` paths).", "(hard-coded absolute home-directory paths)."),
("Lean `.trace` logs (`<home>/AI_Programs/SSRH`).", "Lean `.trace` logs (an absolute home-directory path)."),
("no_delay = closed-form ω set for 100/100 seeds |", "no_delay = closed-form ω set for 100/100 seeds"+C(7,"no amplification mechanism was shown. Still, delay is not inert: at the repo's ω it raises distinct topologies from 1 to 16 and shifts D_B by −0.027 and W by −0.16 (paired); on random ω it increases multistability")+" |"),
("Lean source inspection. Lean itself was not compiled; the broken build is inferred from the missing module plus the absent build artifact.",
 "Lean source inspection. ~~Lean itself was not compiled; the broken build is inferred from the missing module plus the absent build artifact.~~"+C(14,"Lean was compiled later (lean4 v4.33.1, mathlib v4.33.1). `lake build` as committed fails with \"bad import 'AIEFProofs.ControllerFiberProjector'\" (BUILD_EXIT 1). With that import removed it completes (1235 jobs) with no sorry/axiom/admit. See `evidence/logs/lean_build_*.log`. H3 is now verified by an actual build")),
("Replace `<home>` paths.", "Replace the hard-coded absolute home-directory paths."),
])
a=a.replace('a /tmp copy','a temporary copy').replace("The owner's gmail appears","The owner's personal email address appears"); open('<repo-clone>_audit_v2.md','w').write(a)
# ---------------- salvage ----------------
s=open('<repo-clone>_salvage.md').read()
S_HDR="""> **Status (2026-10-23): REVISED per `AIEFS_audit_response.md`.** The original text is from commit f7246a3. It has been corrected in place after adjudicating a collaborator's 14-point critique.
> - **Markup:** corrections are marked **[Correction 2026-10-23 …]**, and retracted text is ~~struck~~.
> - **Strongest claim:** the revised claim in §5 replaces the original.
> - **Publication edits:** absolute local paths were replaced with neutral descriptions.
> - **Script locations:** first-pass scripts referenced here (`audit/deep/*.py`) are re-packaged in `evidence/scripts/`.

"""
NEWCLAIM="""**Revised strongest defensible claim (2026-10-23; replaces the claim above):**
> In a delayed Kuramoto network (N=12) with thresholded EMA-coherence Hebbian plasticity, linear decay and min-endpoint multiplicative node-capacity normalisation:
> - **(i)** The closed-form frequency-proximity rule R_pred(Δω) > μ/(η+μ) is an informative but imperfect predictor of the persistent weight topology. It is exact for the repo's ω without delay; over random ω, precision is 0.59–0.98 and recall 0.18–0.57. Strong edges per node are capped at ⌊c/B_c⌋.
> - **(ii)** For generic ω the selected topology is multistable, and delay increases the number of distinct outcomes.
> - **(iii)** Path dependence is carried redundantly by the weights and the phase/EMA state.
> - **(iv)** On complete, saturated, phase-locked components of degree k, the slow weight-relaxation rate equals the closed form −log λ_{k,ε}/dt ≈ kη/c (the repo's Prop 8.3). The relative-retention rate is therefore κ = −log|λ_B/α|/dt ≈ kη/c − 1/T_w, verified to ≤5e-6 across five window lengths and 292 components.
>
> All of this is conditional on N=12 and the repo's parameters. The κ sign change at small T_w is a prediction, not a result.
"""
s=apply(s,[
("# AIEFS — Salvage assessment (deep dive #2)\n\n", "# AIEFS — Salvage assessment (deep dive #2)\n\n"+S_HDR),
("(read-only clone at <repo-clone>; `git status` clean; nothing pushed/changed on GitHub).", "(read-only local clone; `git status` clean; nothing pushed/changed on GitHub)."),
("Companion to <repo-clone>_audit.md. All new experiment scripts/logs: <round1-scratch>/deep/.", "Companion to `AIEFS_audit.md`. New experiment scripts/logs: originally in a local `audit/deep/` scratch directory; re-packaged in `evidence/`."),
("and it does not hold a new scientific result.", "~~and it does not hold a new scientific result.~~"+C(12,"this was a judgment, not a finding. The ingredients are prior art, the exact combination was not found in a non-exhaustive search, and novelty is not established either way")),
("or (b) artifacts of a hand-picked frequency vector,", "or (b) ~~artifacts of~~ specific to a hand-picked frequency vector (a scope limitation; response #3),"),
("is, to 0.09%, the parameter arithmetic **κ = 2η/c − 1/T_window**.", "is, to 0.09%, the parameter arithmetic **κ = 2η/c − 1/T_window**."+C(9,"this is a conditional closed form for complete saturated locked components, not an identity. The repo's exact discrete rate (Prop 8.3 + 11.1) gives 0.0691217 vs 0.0691225 observed")),
("mostly renames standard linear algebra of a piecewise-smooth map.", "mostly renames standard linear algebra of a piecewise-smooth map."+C(11,"most of these terms (cocycle, Duhamel, lineality) are used in their standard sense, so this is a style judgment. \"Projection/Bregman\" for the gate remains a misnomer. The \"spectral gap\" is a gap of the conditional augmented operator (#10)")),
("(i) the active topology is predicted by a closed-form frequency-proximity rule plus capacity competition, (ii) the topology is multistable and its \"memory\" lives in the phase/EMA state, not in the weights,",
 "(i) the active topology is ~~predicted by~~ informatively but imperfectly predicted by a closed-form frequency-proximity rule plus capacity competition, (ii) the topology is multistable and its \"memory\" ~~lives in the phase/EMA state, not in the weights~~ is carried redundantly by the phase/EMA state and the weights (#6),"),
("| **Valid but known/mostly trivial** | Set ≈ {Δω ≲ 0.12} ∩ capacity competition; hand-picked ω makes it exact |",
 "| **Valid but known/mostly trivial** | Set ≈ {Δω ≲ 0.12} ∩ capacity competition; hand-picked ω makes it exact (no_delay only)."+C(1,"the active set is not generally a subset of the closed-form set: uniform-ω subset in 9/40 and 11/60 runs")+" |"),
("| **Valid on the chosen ω only, so an artifact** |", "| **Valid on the chosen ω only (scope limitation)**"+C(3,"\"artifact\" retracted")+" |"),
("| **Valid but trivial** | Without the threshold every edge grows;", "| **Valid; outcome closed-form explainable**"+C(8,"\"trivial\" overstated; these are legitimate necessity tests")+" | Without the threshold every edge grows;"),
("| **Incoherent / false as stated** | Not idempotent onto the boundary: interior-output witness;",
 "| **Incoherent / false as stated** | ~~Not idempotent onto the boundary: interior-output witness;~~"+C(5,"the gate is idempotent (20000/20000 bitwise) and the witness is only ε-level (6.7e-13); at ε=0 the Euclidean projection differs by 0.037–0.046")),
("| **Valid but modest; the authors' own data says the memory is not in B** |", "| **Valid but modest; ~~the authors' own data says the memory is not in B~~**"+C(6,"memory is carried redundantly: erasing B alone or EMA alone barely matters, erasing both resets 32/40; B at split predicts the future set with AUC 1.0")+" |"),
("| **Valid but trivial: closed form** | κ = 2η/c − 1/T_w = 0.069182 vs observed 0.069122 (0.09%) |", "| **Valid; conditional closed form** | κ = 2η/c − 1/T_w = 0.069182 vs observed 0.069122 (0.09%); discrete exact 0.0691217."+C(9,"verified across 5 T_w for k=3–5 components")+" |"),
("unchanged.\n\n| ω draw", "unchanged.\n\n"+C(1,"replicated with 15+15 new ω sets × 4 seeds: subset 11/60 and 16/60 (uniform baseline/no_delay), 49/60 and 58/60 (clustered)").strip()+"\n\n| ω draw"),
("0.995 in the repo is a near-tautology: P_future and past R are both monotone in Δω for well-separated clusters.",
 "~~0.995 in the repo is a near-tautology~~: P_future and past R are both monotone in Δω for well-separated clusters."+C(2,"held-out test: at the repo's ω, past R beats Δω-only (AUC 0.999995 vs 0.972; logloss 0.003 vs 0.124). On uniform ω it is better calibrated (logloss 0.26 vs 0.45). On clustered ω it is worse (AUC 0.46 vs 0.65). B at split gives AUC 1.0. Not a tautology; mostly persistence")),
("cannot falsify anything nontrivial: each \"failure\" is guaranteed by the equation being removed.", "~~cannot falsify anything nontrivial: each \"failure\" is guaranteed by the equation being removed.~~"+C(8,"they are valid necessity tests whose outcomes have post-hoc closed-form explanations; no_mu's D_B = 0.035 is dynamical")),
("Its outputs can be strictly interior,", "~~Its outputs can be strictly interior,~~ Its outputs can be interior only at the ε level (6.7e-13; #5),"),
("(discrete version 0.069262)", "(~~discrete version 0.069262~~ **discrete version 0.0691217**, from the repo's Prop 8.3 λ_{2,ε} and Prop 11.1)"),
("I checked this by computing γ + Σ_j F_ij/c on rows 2, 7 and 11", "I checked this by computing ~~γ + Σ_j F_ij/c~~ **Σ_j F_ij/c (label corrected 2026-10-23)** on rows 2, 7 and 11"),
("**κ is therefore a parameter identity, not an emergent spectral quantity.**", "~~**κ is therefore a parameter identity, not an emergent spectral quantity.**~~ **κ is therefore a conditional closed form, valid on complete saturated locked components (#9).**"),
("and κ < 0 (no relative memory) for T_w < c/(2η) = 7.92. Not run: it needs the frozen-replay pipeline at other T_w (§7).",
 "and κ < 0 ~~(no relative memory)~~ (old forcing relatively amplified; the weight mode dominates) for T_w < c/(2η) = 7.92. ~~Not run: it needs the frozen-replay pipeline at other T_w (§7).~~"+C(9,"run at T_w ∈ {8.75, 13.13, 17.50, 26.25, 35.01}. The K3 slow channel exists only at T_w=17.50 (1/200 replays), so the K3 version cannot be tested. For k=3–5 complete components, κ_exact matches the discrete kη/c − 1/T_w to ≤5.3e-6 and frozen r_B matches Prop 8.3 to 3.1e-5 relative. κ>0 throughout, so the sign change is untested")),
("in a copy at <tmp>/leanbuild:", "in a temporary copy:"),
("Standard; the name adds nothing |", "Standard and correctly used; ~~the name adds nothing~~ (style judgment, #11) |"),
("| Difference of two decay rates, 2η/c − 1/T_w; not a spectral gap of any operator |", "| Difference of two decay rates, 2η/c − 1/T_w; ~~not a spectral gap of any operator~~ the gap between the eigenvalue log-moduli of the conditional triangular augmented operator (#10); value fixed by parameters |"),
("Ehresmann, holonomy, fiber bundle and gauge appear nowhere in the repo (only in the collaborator conversation, per the first audit).", "~~Ehresmann, holonomy, fiber bundle and gauge appear nowhere in the repo~~ Ehresmann, holonomy and fiber bundle appear nowhere in the repo (only in the collaborator conversation, per the first audit)."+C(11,"\"gauge\" appears once, in a code comment at `gap_phase_scan_v9.py:95`")),
("**Strongest defensible claim:**", "**Strongest defensible claim (original text, SUPERSEDED by the revised claim below; its \"subgraph\" and \"not the weights\" parts were wrong, see #1 and #6):**"),
("Every part is backed by runs above; the \"generic ω\" part rests on 10 + 40 draws at N = 12.", "Every part is backed by runs above; the \"generic ω\" part rests on 10 + 40 draws at N = 12.\n\n"+NEWCLAIM),
("So switching the delay off perturbs the selected topology about as much as changing initial conditions, and it adds no systematic structure.",
 "~~So switching the delay off perturbs the selected topology about as much as changing initial conditions, and it adds no systematic structure.~~"+C(7,"a paired test (15+15 ω × 4 seeds, plus 100 archived repo-ω seeds) shows delay increases multistability. Distinct topologies: 16 vs 1 at the repo's ω; more with delay in 7/15 and 5/15 random sets vs 1/15. At the repo's ω it shifts D_B by −0.027 and W by −0.16. Same-seed similarity exceeds cross-seed by +0.068 [0.021, 0.124]. There is no significant scalar shift and no delay-specific topology signature on random ω")),
("and test κ(T_w) = 2η/c − 1/T_w across T_w ∈ {10, 17.5, 25, 40}, predicting a sign change at T_w = c/2η.", "and test κ(T_w) = 2η/c − 1/T_w across T_w ∈ {10, 17.5, 25, 40}, predicting a sign change at T_w = c/2η."+C(9,"done for k=3–5 over 5 T_w. The K3 version is not testable; the sign change needs T_w < c/(kη)")),
("So the κ(T_w) formula is derived and matches one data point, but is untested elsewhere.", "~~So the κ(T_w) formula is derived and matches one data point, but is untested elsewhere.~~"+C(9,"now tested at 5 T_w for k=3–5 components")),
("- <round1-scratch>/deep/omega_random.{py,json,log}\n- <round1-scratch>/deep/omega_multistab.{py,json,log}\n- <tmp>/leanbuild (patched Lean copy); <tmp>/lake_build_orig.log\n- First-pass scripts in <round1-scratch>/",
 "- `evidence/scripts/omega_random.py`, `evidence/results/omega_random.json`, `evidence/logs/omega_random.log`\n- `evidence/scripts/omega_multistab.py`, `evidence/results/omega_multistab.json`, `evidence/logs/omega_multistab.log`\n- `evidence/scripts/lean_check.sh`, `evidence/logs/lean_build_original.log`, `evidence/logs/lean_build_patched.log`\n- All re-packaged scripts: `evidence/scripts/` (see `evidence/REPRODUCE.md`)"),
])
open('<repo-clone>_salvage_v2.md','w').write(s)
print("ok")
