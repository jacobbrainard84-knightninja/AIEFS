"""Round 4 (2026-10-25): apply the dated inline corrections that point to AIEFS_audit_response_3.md.
Run from the repository root. Each anchor must occur exactly once; the script refuses to apply twice (idempotence marker check).
Only text is appended or a sentence is struck (~~...~~) and annotated; nothing else in the files is changed."""
import sys
from pathlib import Path
A = Path("AI Agent Audits")
C = "[Correction 2026-10-25, response-3 #{}: {}]"
EDITS = {
 "AIEFS_audit_response_2.md": [
  ("Status: **current** (2026-10-24).",
   "Status: **superseded where marked** by `AIEFS_audit_response_3.md` (2026-10-25); originally current (2026-10-24)."),
  ("Nothing was pushed, committed or changed on GitHub for this round. All work is local.",
   "~~Nothing was pushed, committed or changed on GitHub for this round. All work is local.~~ **" + C.format(6, "stale: round 3 was published at `60e6029` (22 commits from `7d752fd`); followed by `0b5b108` and `0f5ef7a`…`dc0250a`") + "**"),
  ("The closed form (identical to the reviewers' at ε=0; §2.2) matches the fiber multiplier on all 374 well-resolved components (λ to 2.1e-8 relative, κ to 2.1e-6 absolute).",
   "The closed form (identical to the reviewers' at ε=0; §2.2) matches the fiber multiplier on all 374 well-resolved components (λ to 2.1e-8 relative, κ to 2.1e-6 absolute). **" + C.format(1, "374 = 264 resolved two-sided fibers (these bounds) + 110 resolved all-tied K3s with no fiber, checked on one-sided rays (λ to 1.7e-7, κ to 1.7e-5)") + "**"),
  ("So h is an eigen-direction with multiplier λ = (1−γdt)·s_J. At the fixed point the row sum is c up to O(ε), which gives",
   "So h is an eigen-direction with multiplier λ = (1−γdt)·s_J. **" + C.format(2, "this is the exact statement, under conditions (a)–(e) of response_3 §2.2, incl. equal controlling scales; the closed form below additionally needs the ideal hypotheses R=1 and row sum c, and the finite-ε fixed point moves λ by 1.6e-12") + "** At the fixed point the row sum is c up to O(ε), which gives"),
  ("- Step resolution. A component is resolved if δ ≥ 100× its max tied gap and its min untied gap ≥ 100×δ. 374 are resolved:",
   "- Step resolution. A component is resolved if δ ≥ 100× its max tied gap and its min untied gap ≥ 100×δ. **" + C.format(1, "the 374 split as 264 two-sided + 110 all-tied K3; the bounds in this bullet are the two-sided ones") + "** 374 are resolved:"),
  ("+v_c lowers row c only, so c stops controlling and the other two rows are preserved. The response is linear, with multiplier λ_2.",
   "+v_c lowers row c only, so c stops controlling and the other two rows are preserved. ~~The response is linear, with multiplier λ_2.~~ **" + C.format(3, "the response along the ray +v_c is D(+v_c) = λ_2 v_c (one-sided; derived in response_3 §2.4); the K3 has zero lineality and no eigenmode") + "**"),
  ("  - So the all-tied K3 is not \"spectrally silent\". It has a one-sided slow direction at rate r_{B,2}, and the round-2 \"unexplained\" twin rate 0.126255 is exactly this rate.",
   "  - So the all-tied K3 is not \"spectrally silent\". ~~It has a one-sided slow direction at rate r_{B,2},~~ **" + C.format(3, "it has zero lineality but nontrivial one-sided controller-selection rays +v_c with the degree-two slow multiplier λ_2 (rate r_{B,2})") + "** and the round-2 \"unexplained\" twin rate 0.126255 is exactly this rate."),
  ("That pattern is observed only, not derived.",
   "~~That pattern is observed only, not derived.~~ **" + C.format(3, "now derived for all-tied K_n with equal edge weights (response_3 §2.3); synthetic K3–K8 to 4.4e-10; fails for unequal edges") + "**"),
  ("Run with the repo's `aief_1_4_augmented_spectrum` functions at their defaults",
   "**" + C.format(8, "the 18-coordinate result is quarantined; corrected full-state proposal: `evidence/proposals/aief_1_4_full_state_spectrum.py` (verdict NO); citations: `evidence/proposals/augmented_spectrum_citations.md`") + "** Run with the repo's `aief_1_4_augmented_spectrum` functions at their defaults"),
  ("The ε=0 comparisons only show a difference from two specific projections, at the sampled points. | **Concede.**",
   "The ε=0 comparisons only show a difference from two specific projections, at the sampled points. | **" + C.format(5, "domain: the no-go holds for every Legendre generator differentiable on a neighbourhood of both x and A_ε(x), both in the open positive orthant of edge space; response_3 §2.1") + "** **Concede.**"),
  ("whether it is a projection under some other divergence is open. Accurate name:",
   "whether it is a projection under some other divergence is open. **" + C.format(5, "for generators whose differentiable domain contains both x and A_ε(x)") + "** Accurate name:"),
  ("- **κ:** \"On complete, saturated, phase-locked components, the multiplier",
   "- **κ:** **" + C.format(2, "replaced by response_3 §3 (exact statement λ=(1−γdt)s_J; closed form conditional; 374 = 264 + 110)") + "** \"On complete, saturated, phase-locked components, the multiplier"),
  ("All-tied K3s have a one-sided slow direction at rate r_{B,2}.\"",
   "All-tied K3s have a one-sided slow direction at rate r_{B,2}.\" **" + C.format(3, "read: zero lineality but nontrivial one-sided controller-selection rays with the degree-two slow multiplier") + "**"),
  ("This was checked to 2.1e-6 on 374 resolved components across five T_w (40 fixed seeds; not independent replications).",
   "This was checked to 2.1e-6 on 374 resolved components across five T_w (40 fixed seeds; not independent replications). **" + C.format(1, "superseded by the reworded (iv) in response_3 §3: exact statement λ=(1−γdt)s_J; closed form under R=1/row sum c; 264 two-sided (κ to 2.1e-6) + 110 all-tied K3 rays (κ to 1.7e-5)") + "**"),
  ("- Editor lock file committed.",
   "- Editor lock file committed. **" + C.format(6, "resolved: no longer tracked, cleanup commits `e8bcb0b`…`dc0250a`") + "**"),
  ("- The Lean build fails on the missing import `ControllerFiberProjector`.",
   "- The Lean build fails on the missing import `ControllerFiberProjector`. **" + C.format(6, "resolved in `0b5b108`; GitHub Actions run 40153641197 passed at `dc0250a`") + "**"),
  ("- No status checks on the latest commit.",
   "- No status checks on the latest commit. **" + C.format(6, "resolved: root workflow `.github/workflows/lean.yml` (`1f9afc9`), run 40153641197 success") + "**"),
  ("7. **The Lean build** (`logs/lean_build_*.log`). It ran in round 2 and was not rerun in round 3.",
   "7. **The Lean build** (`logs/lean_build_*.log`). It ran in round 2 and was not rerun in round 3. **" + C.format(9, "closed: CI run 40153641197 and the round-4 local run, `evidence/logs/lean_r4/`") + "**"),
 ],
 "README.md": [
  ("| `AIEFS_audit_response_2.md` | **Current.** This is the authoritative ledger | 2026-10-24 |",
   "| `AIEFS_audit_response_3.md` | **Current.** This is the authoritative ledger | 2026-10-25 | Round-4 ruling: 374-census split, exact vs conditional rate law and finite-ε fixed point, K3 zero lineality and one-sided rays, derived tie patterns, P_future check, Bregman domain, publication commits, PII scope, quarantine of the 18-coordinate spectrum, Lean (Part B) |\n| `AIEFS_audit_response_2.md` | **Superseded where marked** by `AIEFS_audit_response_3.md` (`[Correction 2026-10-25, response-3 #N]` notes); was the round-3 ledger | 2026-10-24; corrected 2026-10-25 |"),
  ("Where the documents disagree, `AIEFS_audit_response_2.md` takes precedence, then `AIEFS_audit_response.md`.",
   "Where the documents disagree, `AIEFS_audit_response_3.md` takes precedence, then `AIEFS_audit_response_2.md`, then `AIEFS_audit_response.md`."),
  ("The round-3 changes in this folder (corrections dated 2026-10-24, `AIEFS_audit_response_2.md` and the new evidence) were prepared locally and are not part of that publication.",
   "~~The round-3 changes in this folder (corrections dated 2026-10-24, `AIEFS_audit_response_2.md` and the new evidence) were prepared locally and are not part of that publication.~~ **" + C.format(6, "stale: round 3 was published at `60e6029` (22 commits, `7d752fd`…`60e6029`); then `0b5b108` (Lean projector) and `0f5ef7a`…`dc0250a` (tooling, lean_recovery, cleanup; 56 commits). The round-4 changes (corrections dated 2026-10-25, `AIEFS_audit_response_3.md`) are local until the owner approves publication") + "**"),
  ("matches are printed as `<private literal #k>`, never as the value.",
   "matches are printed as `<private literal #k>`, never as the value. **Scope: this folder only.** A CLEAN result says nothing about the rest of the repository; repo-wide privacy/copyright is an open owner decision (`AIEFS_audit_response_3.md` #7)."),
 ],
 "AIEFS_salvage.md": [
  ("rechecked with the cycle-kernel multiplier: 374 resolved components, κ to 2.1e-6; 40 fixed seeds]**",
   "rechecked with the cycle-kernel multiplier: 374 resolved components, κ to 2.1e-6; 40 fixed seeds]** **" + C.format(1, "superseded by response_3 §3: 374 = 264 two-sided fibers (κ to 2.1e-6) + 110 all-tied K3 one-sided rays (κ to 1.7e-5); exact statement λ=(1−γdt)s_J, closed form conditional on R=1 and row sum c") + "**"),
  ("all-tied K3s (110 components, 34 seeds) carry a one-sided slow direction at r_{B,2}]**",
   "all-tied K3s (110 components, 34 seeds) carry a one-sided slow direction at r_{B,2}]** **" + C.format(3, "zero lineality; one-sided controller-selection rays with the degree-two slow multiplier, not a mode") + "**"),
 ],
 "AIEFS_audit_response.md": [
  ("now checked with the cycle-kernel multiplier on 374 resolved components (κ to 2.1e-6); 40 fixed seeds × 5 T_w, not independent replications]**",
   "now checked with the cycle-kernel multiplier on 374 resolved components (κ to 2.1e-6); 40 fixed seeds × 5 T_w, not independent replications]** **" + C.format(1, "superseded by response_3 §3: 374 = 264 two-sided (κ to 2.1e-6) + 110 all-tied K3 one-sided rays (κ to 1.7e-5); closed form conditional") + "**"),
  ("all-tied K3s carry a one-sided slow direction at r_{B,2} in 110/110]**",
   "all-tied K3s carry a one-sided slow direction at r_{B,2} in 110/110]** **" + C.format(3, "read: zero lineality, one-sided controller-selection rays with the degree-two slow multiplier") + "**"),
 ],
}
if __name__ == "__main__":
    for f, eds in EDITS.items():
        p = A / f; s = p.read_text(encoding="utf-8")
        if "response-3 #" in s: sys.exit(f"{p}: already contains response-3 corrections; refusing to apply twice")
        for old, new in eds:
            n = s.count(old)
            if n != 1: sys.exit(f"{p}: anchor found {n} times: {old[:80]!r}")
            s = s.replace(old, new)
        p.write_text(s, encoding="utf-8"); print(f"{f}: {len(eds)} edits")
