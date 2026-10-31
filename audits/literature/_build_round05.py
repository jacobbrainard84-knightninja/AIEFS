#!/usr/bin/env python3
"""Build Round 5: the claim-by-claim adjudication table.

This is the deliverable four rounds of sources were for. Each row states what the
literature is being asked to attest, whether it does, and what registry change
follows.

Two axes, deliberately separate:
  verdict        - is the CLAIM sound, given the literature?
  mapping_health - is the REGISTRY MAPPING from claim to source correct?
A claim can be scientifically right and wrongly sourced (REJ-LOCK-03), or
scientifically unremarkable and correctly sourced. Collapsing the axes would hide
exactly the defect that matters most.
"""

from __future__ import annotations

import csv
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
# Round 7 re-baseline: adjudicate against the pinned registry of record.
# registry/claims.csv does not exist on origin/main and has only 43 rows on the
# arena base branch, while integration/round5 has 76. Editing registry/ is
# forbidden by the inbox protocol, so a byte-exact copy is pinned in baseline/.
REG = ROOT / "baseline" if (ROOT / "baseline" / "claims.csv").exists() else ROOT.parent.parent / "registry"

COLS = [
    "claim_id", "study_id", "registry_status", "claim_class", "literature_role",
    "sources", "n_sources", "verdict", "mapping_health", "verdict_basis",
    "producing_code", "required_change", "severity",
]

VERDICTS = {
    "SUPPORTED",            # literature substantiates the role it is asked to play
    "SUPPORTED_WITH_SCOPE", # substantiated, but a precondition must be stated
    "BOUNDED",              # claim as written exceeds what the literature licenses
    "CONTEXT_ONLY",         # no external literature can attest it; sources frame it
    "VALIDATED_RETIREMENT", # retired claim; literature confirms the retirement
    "VALIDATED_REJECTION",  # rejected claim; literature confirms the rejection
}
MAPPING = {"COMPLETE", "INCOMPLETE", "WRONG"}
SEVERITY = {"NONE", "LOW", "MEDIUM", "HIGH"}
CLAIM_CLASS = {"EMPIRICAL", "FORMAL", "IMPLEMENTATION", "REJECTION", "RETIRED"}
ROLE = {
    "DESIGN", "INFERENCE", "INTERPRETATION", "FORMALIZATION",
    "METHOD_VALIDITY", "SCOPE_ONLY",
}
CODE = {"PRESENT", "RELOCATED", "UNRESOLVED", "NOT_APPLICABLE"}

# ---------------------------------------------------------------------------
ADJ = [
    # ---------------- AIEF-1.3 empirical ----------------
    dict(
        claim_id="EMP-AIEF13-01", claim_class="EMPIRICAL", literature_role="INFERENCE",
        verdict="SUPPORTED_WITH_SCOPE", mapping_health="COMPLETE",
        producing_code="PRESENT", severity="LOW",
        verdict_basis=(
            "Inference design holds, and the open Round 1 item is now closed. "
            "AIEF_1_3_paired_statistics_updated.py:348 uses np.percentile on a stratified "
            "paired bootstrap of the mean difference - a PERCENTILE interval, not the wild "
            "cluster bootstrap LIT-0002 prefers at 40-100 clusters. That preference does not "
            "bind here: clusters are balanced, every seed is treated in every arm (treated "
            "fraction 1, so no few-treated-cluster problem per LIT-0032), and dz=8.434 makes "
            "the interval variant immaterial to the conclusion. Webb's 11-cluster threshold is "
            "cleared by N=100 (LIT-0027)."
        ),
        required_change=(
            "Record the interval variant (stratified paired percentile bootstrap) and one line "
            "on why the wild-bootstrap preference does not bind; add LIT-0032's conditional that "
            "any future arm ablating a SUBSET of seeds requires changing the interval construction."
        ),
    ),
    dict(
        claim_id="EMP-AIEF13-02", claim_class="EMPIRICAL", literature_role="INTERPRETATION",
        verdict="SUPPORTED_WITH_SCOPE", mapping_health="INCOMPLETE",
        producing_code="RELOCATED", severity="LOW",
        verdict_basis=(
            "The no_mu / no_delay contrasts are computed by a surviving script: "
            "AIEF_1_3_paired_statistics_updated.py:59 lists CONTROLS = (shuffle_R, no_delay, "
            "no_mu, no_gap) and defines their arms at :104 and :112. The registry instead names "
            "AIEF_1_3_persistence_mechanism_test_updated.py, which does not exist - a stale "
            "name, not lost capability. The interpretive half ('adaptive coupling rather than "
            "bare delay drives persistence') is consistent with the adaptive-delay cluster; "
            "LIT-0039 supplies the review-level framing and LIT-0018/LIT-0016 the specific "
            "mechanism. Round 7 added LIT-0040 (Seliger, Young & Tsimring) and "
            "LIT-0041 (Timms & English) to the mapping: these are the Hebbian-plasticity and "
            "delay-plus-plasticity ingredients, and together they are what makes \"adaptive "
            "coupling rather than bare delay\" a claim with prior art behind it rather than a "
            "local reading."
        ),
        required_change=(
            "Add LIT-0018 and LIT-0016 to bears_on_ids as corroborating CONTEXT; annotate that "
            "the mechanism contrast is computed in the paired-statistics script, not in the "
            "missing mechanism test."
        ),
    ),
    # ---------------- AIEF-1.4 empirical ----------------
    dict(
        claim_id="EMP-AIEF14-01", claim_class="EMPIRICAL", literature_role="SCOPE_ONLY",
        verdict="CONTEXT_ONLY", mapping_health="INCOMPLETE",
        producing_code="PRESENT", severity="MEDIUM",
        verdict_basis=(
            "The claim that B is not a unique memory bottleneck is the single most "
            "literature-explainable statement in the registry, and it currently has no "
            "supporting source: its only mapping is LIT-0016, a CONTEXT-stance nearest-neighbour "
            "paper. The two sources that actually explain it are attached to OTHER claims - "
            "LIT-0010 (the state of a delay system IS the history segment, so removing one "
            "component leaves the history intact) and LIT-0018 (the state is an N + N^2 "
            "dimensional functional differential equation, so memory is distributed by "
            "construction)."
        ),
        required_change=(
            "Add LIT-0010 and LIT-0018 to bears_on_ids. On that change the claim moves from "
            "CONTEXT_ONLY to SUPPORTED_WITH_SCOPE with no scientific edit."
        ),
    ),
    dict(
        claim_id="EMP-AIEF14-02", claim_class="EMPIRICAL", literature_role="DESIGN",
        verdict="SUPPORTED_WITH_SCOPE", mapping_health="COMPLETE",
        producing_code="PRESENT", severity="MEDIUM",
        verdict_basis=(
            "The matched-phase design has a formal justification, not just an empirical one: "
            "LIT-0025 names the confound - shared information due to common history - that a "
            "naive comparison cannot separate, which is exactly what matching controls. "
            "Authoritative output is present (test_output/ holds 8 matched_phase files). But two "
            "scope constraints must be stated: LIT-0016 shows the underlying mechanism (adaptive "
            "delay reshaping effective coupling) is under active independent investigation, so "
            "novelty must be claimed for the ablation design and the recovery metric, not for the "
            "existence of delay-driven frequency selection; and LIT-0028 establishes that any "
            "description routed through a phase variable loses delay information."
        ),
        required_change=(
            "State the novelty boundary explicitly (design + metric, not mechanism), and state "
            "that the delay is kept explicit rather than phase-reduced - LIT-0028 frames the "
            "latter as the less restrictive choice, so it is a strength worth recording."
        ),
    ),
    # ---------------- implementation ----------------
    dict(
        claim_id="IMPL-MODULAR-01", claim_class="IMPLEMENTATION", literature_role="METHOD_VALIDITY",
        verdict="SUPPORTED", mapping_health="COMPLETE",
        producing_code="PRESENT", severity="NONE",
        verdict_basis=(
            "Correctly scoped and now citable. LIT-0012 establishes that bit-identical agreement "
            "is a same-order, same-environment property, so the claim's 'identical host/libm' "
            "boundary is the right one rather than excessive caution; LIT-0014 puts the "
            "4.405e-13 cross-host drift at the predicted rounding-error scale; LIT-0038 makes "
            "tolerance-based validation the standard's own requirement, provided the tolerance is "
            "stated and justified. The observed pattern (0.0 on discrete P_*, drift only on "
            "continuous arrays) is textbook behaviour, not a defect."
        ),
        required_change=(
            "None to the claim. Repository-level and separate: mint a DOI for frozen run "
            "directories, without which the artifact cannot claim ACM 'Artifacts Available' "
            "regardless of its quality."
        ),
    ),
    # ---------------- Lean / formal ----------------
    dict(
        claim_id="LEAN-CF-01", claim_class="FORMAL", literature_role="FORMALIZATION",
        verdict="SUPPORTED", mapping_health="COMPLETE",
        producing_code="PRESENT", severity="NONE",
        verdict_basis=(
            "The Lean statement is the correct specialization of a classical theorem, which is "
            "the right status for it: rank = n - c gives nullity 3 - 1 = 2 in edge coordinates "
            "for the 2-vertex / 3-edge multigraph with c = 1 (LIT-0011), and the machine-checked "
            "result is the orientation-compatible instance. The claim does not overreach - it "
            "says 'for C_{2,7}' and nothing wider. Its limitation is scope, not error: LIT-0037 "
            "shows what the same library supports when the result is stated at full generality."
        ),
        required_change=(
            "None to the claim. Scope note only: record LIT-0037 as the standard to measure any "
            "future generalization against."
        ),
    ),
    dict(
        claim_id="CAVEAT-MS-8.4", claim_class="FORMAL", literature_role="FORMALIZATION",
        verdict="SUPPORTED", mapping_health="COMPLETE",
        producing_code="RELOCATED", severity="NONE",
        verdict_basis=(
            "This claim IS a correction - it asserts that draft Corollary 8.4 is wrong - and the "
            "literature supports the correction rather than the original. For a non-normal "
            "finite-step operator, left and right eigenvectors are not orthogonal and the "
            "pointwise left-covector decomposition is a property of one fibre and one "
            "normalization, not an invariant object (LIT-0008). LIT-0009 supplies the reason "
            "ambient orthogonality fails off the edge-uniform locus. The producing code is "
            "AIEF_1_4_freeze_controller_fiber_theorem.py, which exists but is not a registered "
            "entrypoint for its study."
        ),
        required_change=(
            "Register AIEF_1_4_freeze_controller_fiber_theorem.py as an entrypoint for "
            "AIEF_1_4_CONTROLLER_FIBER; the registry currently omits the script that produces "
            "two of its claims."
        ),
    ),
    dict(
        claim_id="CF01", claim_class="FORMAL", literature_role="FORMALIZATION",
        verdict="SUPPORTED", mapping_health="COMPLETE",
        producing_code="PRESENT", severity="NONE",
        verdict_basis=(
            "Four independent pillars, which is why this block is the best-supported in the "
            "registry: the piecewise-smooth framing (LIT-0020), the uniqueness of the "
            "lexicographic derivative once a basis is fixed (LIT-0021), an implementable "
            "automatic-differentiation forward mode with rules for min/max/mid/abs (LIT-0022), "
            "and an applied demonstration that the lexicographic route outperforms hybridising "
            "into smooth modes by ~50% (LIT-0033). The stated hypotheses (positive support, exact "
            "active capacity set) match what the theorem needs."
        ),
        required_change="none",
    ),
    dict(
        claim_id="CF02", claim_class="FORMAL", literature_role="FORMALIZATION",
        verdict="SUPPORTED", mapping_health="COMPLETE",
        producing_code="PRESENT", severity="NONE",
        verdict_basis=(
            "Same four pillars as CF01 and the same hypothesis structure. The caveat that the "
            "statement concerns the projected output rather than the input weight state is "
            "consistent with LIT-0020's treatment of piecewise-smooth maps, where the output "
            "side is smooth on a region while the preimage is not."
        ),
        required_change="none",
    ),
    dict(
        claim_id="CF03", claim_class="FORMAL", literature_role="FORMALIZATION",
        verdict="SUPPORTED", mapping_health="COMPLETE",
        producing_code="PRESENT", severity="NONE",
        verdict_basis=(
            "The strongest single result of the adjudication. Exact affinity on "
            "multiplier-controller fibres INCLUDING active endpoint ties is precisely what "
            "LIT-0021 licenses: the lexicographic derivative is unique once a basis is fixed, "
            "which is exactly the property a branchwise Jacobian lacks at a tie. LIT-0033 then "
            "shows this is current practice in a verified-systems venue, not local convention - "
            "and its reported gain came from using the lexicographic derivative INSTEAD of the "
            "branch bookkeeping the AIEF audit performs, which is evidence that the bookkeeping "
            "is avoidable rather than necessary."
        ),
        required_change="none",
    ),
    dict(
        claim_id="CF05", claim_class="EMPIRICAL", literature_role="SCOPE_ONLY",
        verdict="CONTEXT_ONLY", mapping_health="COMPLETE",
        producing_code="PRESENT", severity="NONE",
        verdict_basis=(
            "A finite numerical observation - no external literature can corroborate that a "
            "specific winner map held across 32,001 saved states, and the four attached sources "
            "only supply the vocabulary (LIT-0020's border-collision frame) for what a change "
            "would have been. The claim's own caveat already declines to infer infinite-time "
            "persistence. Independently corroborated internally: Round 3's frozen-driver audit "
            "reports 0 winner-signature changes across 32,000 steps, consistent with 32,001 "
            "saved states = initial state + 32,000 steps."
        ),
        required_change=(
            "None. Optional: state the 32,001/32,000 relationship explicitly so the two round "
            "figures are not read as a discrepancy."
        ),
    ),
    dict(
        claim_id="CF06", claim_class="FORMAL", literature_role="FORMALIZATION",
        verdict="SUPPORTED_WITH_SCOPE", mapping_health="COMPLETE",
        producing_code="PRESENT", severity="NONE",
        verdict_basis=(
            "Correct as a conditional: given the audited winner map, the kernel is the same "
            "rank-incidence nullity as LEAN-CF-01 (LIT-0011), reached through multiplier "
            "coordinates instead of edge coordinates. The caveat distinguishes this from exact "
            "face lineality, which is the right distinction and keeps the claim inside what "
            "LIT-0020 licenses."
        ),
        required_change="none",
    ),
    dict(
        claim_id="CF08", claim_class="FORMAL", literature_role="FORMALIZATION",
        verdict="SUPPORTED_WITH_SCOPE", mapping_health="COMPLETE",
        producing_code="RELOCATED", severity="LOW",
        verdict_basis=(
            "Defensible as written, because the claim's own caveat already states that pointwise "
            "left eigenvectors do not form a fixed or moving cocycle dual. LIT-0008 supports "
            "exactly that restriction. The residual risk is the word 'exact': it invites a global "
            "reading of orthogonality, and global ambient orthogonality is precisely what "
            "CAVEAT-MS-8.4 proves false off the edge-uniform locus. Producing code is "
            "AIEF_1_4_freeze_controller_fiber_theorem.py (contains the right-closure computation), "
            "again not a registered entrypoint."
        ),
        required_change=(
            "Reword to make 'exact' explicitly POINTWISE and normalization-dependent, citing "
            "CAVEAT-MS-8.4 for where the global reading fails."
        ),
    ),
    # ---------------- audit-corpus claims (present only in the pinned baseline) ----
    dict(
        claim_id="AUD-NOVELTY", claim_class="EMPIRICAL", literature_role="INTERPRETATION",
        verdict="SUPPORTED_WITH_SCOPE", mapping_health="COMPLETE",
        producing_code="NOT_APPLICABLE", severity="MEDIUM",
        verdict_basis=(
            "The claim has two halves and the literature settles only one, which is exactly why "
            "the verdict is scoped rather than plain. Half two - 'the ingredients (delayed "
            "Kuramoto, Hebbian plasticity, normalisation) are prior art' - is now fully sourced: "
            "LIT-0040 (Seliger, Young & Tsimring 2002, Hebbian Kuramoto coupling) for plasticity, "
            "LIT-0041 (Timms & English 2014) for delay plus plasticity, LIT-0042 (Picallo & "
            "Riecke 2011) for conserved-coupling normalisation, LIT-0043 (Miller & MacKay 1994) "
            "for multiplicative versus subtractive normalisation, and LIT-0039 (Berner et al. "
            "2023) as the field review of the whole class. Half one - 'novelty is not established "
            "either way' - literature cannot close: no search can prove a negative, and the "
            "repository's own audit says the exact combination (EMA of the delay-compensated "
            "phasor as driver, plus a min-endpoint hard capacity cap) was not found but the "
            "search was not exhaustive. LIT-0043 is the sharpest of the five: it is a 1994 result "
            "showing that the CHOICE of normalisation (multiplicative vs subtractive) determines "
            "which fixed point is selected - directly relevant to why the capacity cap matters "
            "rather than being cosmetic."
        ),
        required_change=(
            "Split the row. The prior-art half can move from Incomplete to Supported with the "
            "five sources attached. The novelty half should stay Incomplete with its caveat, and "
            "should be restated narrowly: 'no prior art was found for the specific combination', "
            "not 'novelty is not established either way' - the ingredients' prior-art status IS "
            "established, and leaving that ambiguous understates the literature."
        ),
    ),
    # ---------------- retirements ----------------
    dict(
        claim_id="S03", claim_class="RETIRED", literature_role="SCOPE_ONLY",
        verdict="VALIDATED_RETIREMENT", mapping_health="COMPLETE",
        producing_code="NOT_APPLICABLE", severity="NONE",
        verdict_basis=(
            "The retirement is right for a structural reason. In a delay system the state is the "
            "history segment (LIT-0010), so 'the mature system is at equilibrium' would require "
            "the entire history to be constant - a strictly stronger condition than any "
            "component-level balance. The replacement (weights constraint-balanced, dynamics "
            "continuing) is the only reading compatible with LIT-0029 / LIT-0035's method-of-steps "
            "framing."
        ),
        required_change="none",
    ),
    dict(
        claim_id="S04", claim_class="RETIRED", literature_role="SCOPE_ONLY",
        verdict="VALIDATED_RETIREMENT", mapping_health="COMPLETE",
        producing_code="NOT_APPLICABLE", severity="NONE",
        verdict_basis=(
            "The retirement correctly reclassifies a tolerance-classifier change as a "
            "discontinuity-induced phenomenon rather than an implemented face switch. LIT-0020 "
            "supplies the precise vocabulary for that class (border collision / "
            "boundary-equilibrium bifurcation), and LIT-0009 supplies the reason the event is "
            "not a differentiable transition. The replacement keeps the winner map fixed, which "
            "is consistent with the branch audit."
        ),
        required_change="none",
    ),
    dict(
        claim_id="S07", claim_class="RETIRED", literature_role="SCOPE_ONLY",
        verdict="VALIDATED_RETIREMENT", mapping_health="COMPLETE",
        producing_code="NOT_APPLICABLE", severity="NONE",
        verdict_basis=(
            "Retirement moves a claim from spectral inference to direct reconstruction, which is "
            "strictly stronger evidence. LIT-0015 is the relevant standard: component structure "
            "should be established from the graph, not inferred from a spectrum - the same "
            "principle that made the K3 census failure (REJ-K3-04) diagnosable."
        ),
        required_change="none",
    ),
    dict(
        claim_id="S09", claim_class="RETIRED", literature_role="METHOD_VALIDITY",
        verdict="VALIDATED_RETIREMENT", mapping_health="COMPLETE",
        producing_code="NOT_APPLICABLE", severity="NONE",
        verdict_basis=(
            "The best-justified retirement in the set. Calling a POD Rayleigh quotient the 'exact "
            "memory propagation rate' requires a finite-dimensional invariant subspace, and "
            "LIT-0003 establishes that an exact slow reduction needs an invariant manifold "
            "tangent to a spectral subspace instead. LIT-0004 shows a sound delay-aware reduction "
            "(SSM) exists and was not attempted; LIT-0006 supplies the residual test that would "
            "have rejected the quotient automatically; LIT-0007 shows that truncating a spectrum "
            "without carrying the remainder as a bounded error process has no quantitative "
            "referent."
        ),
        required_change="none",
    ),
    dict(
        claim_id="S11", claim_class="RETIRED", literature_role="SCOPE_ONLY",
        verdict="VALIDATED_RETIREMENT", mapping_health="COMPLETE",
        producing_code="NOT_APPLICABLE", severity="NONE",
        verdict_basis=(
            "Homogeneous exponential decay at a single rate presumes a normal operator, which a "
            "non-normal finite-step propagator is not (LIT-0008). The replacement's distinction "
            "between a decaying radial magnitude and a persisting tangential separation is the "
            "standard non-normal behaviour, and LIT-0010 supplies the reason the history keeps "
            "the two components from collapsing onto one rate."
        ),
        required_change="none",
    ),
    dict(
        claim_id="S16", claim_class="RETIRED", literature_role="SCOPE_ONLY",
        verdict="VALIDATED_RETIREMENT", mapping_health="COMPLETE",
        producing_code="NOT_APPLICABLE", severity="NONE",
        verdict_basis=(
            "Retirement replaces 'only an empirical POD mode' with a derivation from implemented "
            "branch coefficients that matches POD numerically. That converts an existence claim "
            "into a consistency check, and LIT-0005 is the right standard for why the "
            "distinction matters: a projected mode's spectrum is not automatically attributable "
            "to the full system, so agreement between a derived matrix and a POD estimate is "
            "evidence of consistency rather than of identification."
        ),
        required_change="none",
    ),
    # ---------------- rejections ----------------
    dict(
        claim_id="REJ-SPEC-01", claim_class="REJECTION", literature_role="METHOD_VALIDITY",
        verdict="VALIDATED_REJECTION", mapping_health="COMPLETE",
        producing_code="NOT_APPLICABLE", severity="LOW",
        verdict_basis=(
            "The rejection is validated by the strongest external justification in the record, "
            "and it is over-determined: LIT-0003 (exact reduction needs an invariant manifold, "
            "not a truncated POD basis), LIT-0006 (a residual acceptance test would have caught "
            "the spurious eigenpairs automatically), LIT-0007 (truncation without a bounded "
            "remainder has no quantitative meaning), LIT-0005 (closure/aliasing produces "
            "plausible spurious eigenvalues in exactly this regime)."
        ),
        required_change=(
            "Clarify scope: the rejection is of POD truncation as applied, not of spectral "
            "reduction in general. LIT-0004 provides a published, delay-aware alternative that "
            "should be the citable target if this is ever revisited."
        ),
    ),
    dict(
        claim_id="REJ-SPEC-02", claim_class="REJECTION", literature_role="METHOD_VALIDITY",
        verdict="VALIDATED_REJECTION", mapping_health="COMPLETE",
        producing_code="NOT_APPLICABLE", severity="NONE",
        verdict_basis=(
            "Validated twice over, and importantly NOT rescuable by shrinking epsilon. (1) "
            "LIT-0014: eps=1e-8 is two to three orders of magnitude larger than the 4.44e-14 tie "
            "margin it was meant to resolve, so the reported spectrum is dominated by the "
            "difference step. (2) LIT-0022: finite differencing is unsuitable for nonsmooth "
            "functions because it steps across nonsmooth points - a property of the method, not "
            "of the step size. (3) LIT-0009: at a tie the branchwise Jacobian does not exist, so "
            "no finite-difference quotient converges to one."
        ),
        required_change="none",
    ),
    dict(
        claim_id="REJ-LOCK-03", claim_class="REJECTION", literature_role="METHOD_VALIDITY",
        verdict="VALIDATED_REJECTION", mapping_health="WRONG",
        producing_code="NOT_APPLICABLE", severity="HIGH",
        verdict_basis=(
            "The rejection is correct and the citation is wrong - the highest-severity item in "
            "this table. The claim rejects a bare algebraic zero-sum as the locking condition, "
            "and the functional-form argument is sound. But its ONLY attached source, LIT-0030, "
            "requires uniform in-degree k, which adaptive hypergraph AIEF networks violate by "
            "construction. So the sole citation for this claim does not apply to the system it is "
            "cited for. Round 4's F24 corrected the prose; the registry mapping was never fixed."
        ),
        required_change=(
            "Replace the mapping: LIT-0018 (implicit equations for the collective frequency, no "
            "uniform-k restriction) and LIT-0028 (multiple and state-dependent delays) carry the "
            "claim; demote LIT-0030 to CONTEXT with its precondition stated."
        ),
    ),
    dict(
        claim_id="REJ-K3-04", claim_class="REJECTION", literature_role="METHOD_VALIDITY",
        verdict="VALIDATED_REJECTION", mapping_health="COMPLETE",
        producing_code="NOT_APPLICABLE", severity="NONE",
        verdict_basis=(
            "LIT-0015 defines a network motif as excess over a degree-matched null ensemble, "
            "never a raw count. The rejection has two independent grounds and either suffices: "
            "the census counted 856 embedded 3-cliques inside K4/K5/K6 components rather than "
            "isolated K3 components, and even a correct count would not establish motif status "
            "without a degree-matched null. This is the cleanest instance in the registry of a "
            "rejection resting on a definitional error rather than a numerical one."
        ),
        required_change=(
            "None. If a motif claim is ever revived, LIT-0015 requires a degree-matched null "
            "ensemble, which is stated in Round 1's F3 but not yet in the registry."
        ),
    ),
    dict(
        claim_id="REJ-COHORT-05", claim_class="REJECTION", literature_role="METHOD_VALIDITY",
        verdict="VALIDATED_REJECTION", mapping_health="COMPLETE",
        producing_code="NOT_APPLICABLE", severity="NONE",
        verdict_basis=(
            "Hurlbert's pseudoreplication is exactly this failure mode: pooling two bit-identical "
            "20-seed runs (overlap 20) and reporting N=40 independent paired seeds treats "
            "non-independent replicates as independent and inflates the false-positive rate. "
            "LIT-0001 also confirms the remedy adopted - independent experimental units, i.e. "
            "the disjoint N=100 cohort - is the standard one, not merely a conservative choice."
        ),
        required_change="none",
    ),
]


def main() -> None:
    claims = {r["claim_id"]: r for r in csv.DictReader((REG / "claims.csv").open(encoding="utf-8"))}
    src = list(csv.DictReader((ROOT / "SOURCES.csv").open(encoding="utf-8")))

    mapped: dict[str, list[str]] = {}
    for s in src:
        for t in s["bears_on_ids"].split(";"):
            t = t.strip()
            if t in claims:
                mapped.setdefault(t, []).append(s["source_id"])

    rows = []
    for rec in ADJ:
        cid = rec["claim_id"]
        assert cid in claims, f"unknown claim {cid}"
        assert rec["verdict"] in VERDICTS, (cid, rec["verdict"])
        assert rec["mapping_health"] in MAPPING, (cid, rec["mapping_health"])
        assert rec["severity"] in SEVERITY, (cid, rec["severity"])
        assert rec["claim_class"] in CLAIM_CLASS, (cid, rec["claim_class"])
        assert rec["literature_role"] in ROLE, (cid, rec["literature_role"])
        assert rec["producing_code"] in CODE, (cid, rec["producing_code"])
        assert rec["verdict_basis"].strip(), f"{cid}: empty verdict_basis"
        assert rec["required_change"].strip(), f"{cid}: empty required_change"
        assert cid in mapped, f"{cid} has no source mapping but is adjudicated"
        rows.append({
            "claim_id": cid,
            "study_id": claims[cid]["study_id"],
            "registry_status": claims[cid]["artifact_status"],
            "claim_class": rec["claim_class"],
            "literature_role": rec["literature_role"],
            "sources": ";".join(sorted(mapped[cid])),
            "n_sources": len(mapped[cid]),
            "verdict": rec["verdict"],
            "mapping_health": rec["mapping_health"],
            "verdict_basis": rec["verdict_basis"],
            "producing_code": rec["producing_code"],
            "required_change": rec["required_change"],
            "severity": rec["severity"],
        })

    order = {c: i for i, c in enumerate(sorted(claims, key=lambda k: (claims[k]["study_id"], k)))}
    rows.sort(key=lambda r: order[r["claim_id"]])

    out = ROOT / "ADJUDICATION.csv"
    with out.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)

    from collections import Counter
    print(f"wrote {len(rows)} adjudications -> ADJUDICATION.csv")
    print("  verdict :", dict(Counter(r["verdict"] for r in rows)))
    print("  mapping :", dict(Counter(r["mapping_health"] for r in rows)))
    print("  severity:", dict(Counter(r["severity"] for r in rows)))
    print("  code    :", dict(Counter(r["producing_code"] for r in rows)))
    uncovered = set(mapped) - {r["claim_id"] for r in rows}
    print(f"  mapped-but-unadjudicated: {sorted(uncovered) or 'none'}")


if __name__ == "__main__":
    main()
