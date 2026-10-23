#!/usr/bin/env python3
"""Freeze the AIEF-1.4 analysis lineage and superseded-claim register.

The source hashes written here are hashes of the current workspace files.  For
an exact execution hash of a previously completed analysis, the corresponding
output-directory analysis_manifest.json remains authoritative because several
scripts were improved after their first reported run.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
RUN_HASH = "5a9f093a2fe0"
FREEZE_DATE = "2026-07-26"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def atomic_text(path: Path, text: str) -> None:
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def lineage_definitions() -> list[dict[str, str]]:
    # Evidence classes: exact code identity; replay fact; controlled
    # counterfactual; conditional mechanism; descriptive cohort result.
    return [
        dict(stage="production", analysis="split_state_memory_ablation", source="AIEF_1_4_memory_ablation_updated.py", output="runs/5a9f093a2fe0", estimand="paired late topology after split-state interventions", scope="40 paired seeds; full branch run", evidence="descriptive cohort result", result="No unique memory register; reset_B reconstructs nearly exactly; future edge identity is required for maintenance.", superseded="B is the unique or dominant memory carrier.", caveat="B_carrier_only and full_reset used unmatched randomized phase/history resets."),
        dict(stage="results", analysis="branch_results_summary", source="AIEF_1_4_results_analysis.py", output="aief_1_4_results_analysis", estimand="late persistence, similarity, retention, emergence", scope="40 paired seeds", evidence="descriptive cohort result", result="State channels are redundant; full reset recovers a recognizable but nonunique attractor.", superseded="Late recovery implies storage in one state variable.", caveat="Topology persistence is distinct from continuous-weight similarity."),
        dict(stage="recovery", analysis="trajectory_recovery_equivalence", source="AIEF_1_4_trajectory_recovery_equivalence.py", output="aief_1_4_trajectory_recovery", estimand="sustained similarity recovery and restricted mean unrecovered time", scope="40 paired seeds", evidence="descriptive cohort result", result="reset_B recovers rapidly; joint resets are slower and less reliable; future_shuffle never recovers.", superseded="Means among recovered seeds adequately summarize recovery.", caveat="Censoring requires recovery probability and RMUT."),
        dict(stage="survival", analysis="survival_outlier_spectral", source="AIEF_1_4_survival_outlier_spectral.py", output="aief_1_4_survival_outlier_spectral", estimand="edge survival, outliers, and residual spectra", scope="40 paired seeds", evidence="descriptive cohort result", result="Recovery and survival are heterogeneous; reset_B residual is tiny but localized.", superseded="Small aggregate residual implies diffuse edgewise residual.", caveat="One paired seed/graph is the inferential unit."),
        dict(stage="geometry", analysis="entropy_geometry", source="AIEF_1_4_entropy_geometry_diagnostics.py", output="aief_1_4_entropy_geometry", estimand="Legendre coordinates, Hessian, inverse map, conditioning", scope="40 mature split states", evidence="replay fact", result="Mature AIEF lies on a singular boundary face; inverse map works but intrinsic metrics are epsilon-sensitive.", superseded="Mirror AIEF is a coordinate rewrite of current AIEF.", caveat="Entropy geometry is natural, not canonical; Bregman divergence is not geodesic distance."),
        dict(stage="geometry", analysis="local_update_comparison", source="AIEF_1_4_local_update_comparison.py", output="aief_1_4_local_update_comparison", estimand="current versus coordinate-dual versus mirror one-step increments", scope="mature split states and probes", evidence="controlled counterfactual", result="Coordinate dual Euler is first-order equivalent only in the interior; mirror Euler is a different vector field.", superseded="Coordinate change, mirror flow, and proximal dynamics are interchangeable.", caveat="Interior order does not establish active-boundary equivalence."),
        dict(stage="operator", analysis="active_boundary_probe", source="AIEF_1_4_active_boundary_analysis.py", output="aief_1_4_active_boundary_analysis", estimand="ideal directional field and finite-difference order", scope="mature split states and deterministic probes", evidence="conditional mechanism", result="Candidate ideal field has O(dt) rate and O(dt^2) increment errors; mature adaptive field is constraint-balanced.", superseded="The hard admissibility operation is a soft regularizer or rare repair.", caveat="The theorem concerns the ideal map without the fixed 1e-12 safeguard."),
        dict(stage="operator", analysis="trajectory_stationarity_perturbation", source="AIEF_1_4_stationarity_perturbation_analysis_updated.py", output="aief_1_4_stationarity_perturbation", estimand="trajectory-wide adaptive stationarity and feasible perturbation restoration", scope="40 seeds; ~1.28M mature updates", evidence="replay fact", result="39 seeds remain adaptively stationary; one deterministic exceptional seed drifts; operator audits pass numerically.", superseded="Adaptive-component stationarity means full delayed-state equilibrium.", caveat="Implementation audits are not proof of Hadamard differentiability."),
        dict(stage="tangent", analysis="corrected_exceptional_tangent", source="AIEF_1_4_exceptional_tangent_analysis.py", output="aief_1_4_exceptional_tangent", estimand="fixed-direction tangent restoration across amplitudes", scope="40 seeds x 5 directions", evidence="replay fact", result="Typical observed contraction agrees with frozen prediction; exceptional directions are slower and less radial.", superseded="Repeated amplitudes are independent perturbation experiments.", caveat="Unique seed/direction is the directional unit; full seed remains inferential unit."),
        dict(stage="tangent", analysis="face_spectrum", source="AIEF_1_4_face_spectrum_analysis.py", output="aief_1_4_face_spectrum", estimand="analytic/numerical fixed-face tangent Jacobians and modal prediction", scope="40 split states plus exceptional stages", evidence="replay fact", result="J_T=Q^T diag(-gamma-rho) Q matches numerical derivatives; matrix-exponential predictions are accurate.", superseded="Repeated rational-looking rates are unexplained quantization.", caveat="Frozen-fast local stability is not full coupled stability."),
        dict(stage="tangent", analysis="channel_invariance", source="AIEF_1_4_channel_invariance_analysis.py", output="aief_1_4_channel_invariance", estimand="tangent/channel invariance and multiplicities", scope="40 seeds; 200 unique directions", evidence="replay fact", result="All split-state tangent spaces are channel invariant to tolerance; multiplicities match.", superseded="Only the spectral abscissa is explained by face geometry.", caveat="Tolerance below numerical resolution creates artificial channels."),
        dict(stage="tangent", analysis="intertwining_controller", source="AIEF_1_4_intertwining_controller_analysis.py", output="aief_1_4_intertwining_controller", estimand="CD=LC, controller balance, edge balance", scope="40 split states plus exceptional stages", evidence="replay fact", result="Intertwining is machine-precision; controller equation holds on active rows; all-node residual is driven by unsaturated rows.", superseded="diag(c) alpha=K alpha is an all-node equation on slack rows.", caveat="Intertwining and projector commutation are equivalent certificates, not independent evidence."),
        dict(stage="components", analysis="component_controller_audit", source="AIEF_1_4_component_controller_audit.py", output="aief_1_4_component_controller_audit", estimand="actual support components, degree rates, explicit component intertwiner", scope="40 split states plus exceptional stages", evidence="replay fact", result="39 ordinary states are unions of fully saturated rate-uniform cliques; explicit component spectra match.", superseded="Clique structure is only inferred from spectra.", caveat="Ordinary-cohort regularity does not prove every future mature state is a clique union."),
        dict(stage="exceptional", analysis="exceptional_K3_transition", source="AIEF_1_4_exceptional_K3_transition_audit.py", output="aief_1_4_exceptional_K3_transition", estimand="dense K3 classifier, rates, node/edge trajectory", scope="one exceptional seed; 32,001 states", evidence="replay fact", result="K3 nodes/edges identified; classifier nullity changes 2->1; support and replay are exact.", superseded="Classifier transition time is an intrinsic implemented branch-switch time.", caveat="Boundary tolerance changes the classifier time and active count."),
        dict(stage="finite_map", analysis="actual_admissibility_branch", source="AIEF_1_4_actual_admissibility_branch_audit.py", output="aief_1_4_actual_admissibility_branch", estimand="proposal gate, scales, endpoint winners, actual branch Jacobian", scope="one exceptional seed; complete replay", evidence="exact code identity", result="Reconstructed map equals executed map; winner map is fixed; node 11 clipping changes no positive-edge formula.", superseded="The implemented K3 branch switches at t=124.05 or 113.81.", caveat="Base branch constancy does not imply finite-amplitude perturbations stay on branch."),
        dict(stage="cocycle", analysis="frozen_driver_cocycle", source="AIEF_1_4_frozen_driver_cocycle_analysis.py", output="aief_1_4_frozen_driver_cocycle", estimand="finite-time K3 frozen-weight propagator, nonnormality, nonlinear validation", scope="exceptional seed; 3x3 weight sector", evidence="controlled counterfactual", result="Initial nonnormal K0 explains modest transient; frozen cocycle predicts frozen nonlinear perturbations.", superseded="Coefficient drift or rewiring is required for the initial transient.", caveat="This is the deltaR=0 reduced subsystem, not the full delayed tangent."),
        dict(stage="cocycle", analysis="cocycle_controls_coupled", source="AIEF_1_4_cocycle_controls_coupled_comparison.py", output="aief_1_4_cocycle_controls_coupled", estimand="stable singular spectra, controls, coupled-minus-frozen feedback", scope="exceptional K3; two directions; feasible amplitudes", evidence="controlled counterfactual", result="Low-rank admissibility term creates transient/anisotropy; coupled feedback is material for the slow direction.", superseded="Frozen weight cocycle fully explains coupled perturbations.", caveat="Finite-time exponents are not asserted Oseledets limits."),
        dict(stage="augmented", analysis="augmented_tangent_cocycle", source="AIEF_1_4_augmented_tangent_cocycle_analysis.py", output="aief_1_4_augmented_tangent_cocycle", estimand="full directional tangent on theta,B,C,history", scope="exceptional seed; two directions; multiple amplitudes", evidence="replay fact", result="Augmented tangent predicts coupled nonlinear response with small errors and preserved branches.", superseded="Weight alone is the Markov state of the adaptive perturbation dynamics.", caveat="Validated on one branch, directions, amplitudes, and finite horizons."),
        dict(stage="duhamel", analysis="augmented_duhamel_feedback", source="AIEF_1_4_augmented_duhamel_feedback_analysis.py", output="aief_1_4_augmented_duhamel_feedback", estimand="homogeneous versus endogenous feedback decomposition and ablations", scope="exceptional K3; two analytic tangent directions", evidence="replay fact", result="Duhamel reconstruction is machine-precision; feedback crossover times are 0.38 and 72.86; EMA/fresh-phase/R-to-B paths are necessary late.", superseded="Feedback is a large instantaneous forcing or an external input.", caveat="Forcing is endogenous to the closed augmented tangent system."),
        dict(stage="duhamel", analysis="duhamel_memory_alignment", source="AIEF_1_4_duhamel_memory_alignment_analysis.py", output="aief_1_4_duhamel_memory_alignment", estimand="exact crossover, forcing-age memory, alignment, selected ablation states", scope="saved Duhamel vectors", evidence="replay fact", result="Recent 60-70 units reconstruct final feedback; forcing aligns with persistent directions; older forcing is forgotten.", superseded="Final response accumulates uniformly over the entire 320-unit history.", caveat="Propagated influence is not automatically amplification; vector contributions cancel."),
        dict(stage="reduction", analysis="feedback_rank_memory", source="AIEF_1_4_feedback_rank_memory_reduction.py", output="aief_1_4_feedback_rank_memory_reduction", estimand="target-time memory fits, POD rank, scalar transverse residual", scope="saved Duhamel arrays; two directions", evidence="replay fact", result="Late memory envelope stabilizes near 0.06913; total/feedback response is nearly rank one; propagated forcing is more rank one than raw forcing.", superseded="Pairwise alignment alone establishes a one-dimensional channel.", caveat="Late rank one on two directions is not a universal invariant manifold."),
        dict(stage="reduction", analysis="scalar_spectral_gap", source="AIEF_1_4_scalar_spectral_gap_reduction.py", output="aief_1_4_scalar_spectral_gap_reduction", estimand="projected recurrence, Rayleigh gap, unconstrained two-state fit", scope="saved Duhamel arrays", evidence="controlled counterfactual", result="Scalar recurrence closes; forcing decays at EMA rate; POD-Rayleigh gap is approximate; pooled (a,g) model is unidentifiable.", superseded="The POD Rayleigh quotient gives the exact memory propagation rate and identifies a shared two-state model.", caveat="Direction-specific perfect fits can result from late collinearity."),
        dict(stage="reduction", analysis="propagation_gap_geometric", source="AIEF_1_4_propagation_gap_geometric_control.py", output="aief_1_4_propagation_gap_geometric_control", estimand="actual forcing propagation rate and analytic geometric-axis control", scope="saved Duhamel arrays", evidence="replay fact", result="Geometric and POD axes agree; direct propagated forcing closes the late spectral gap near 1e-6.", superseded="A fixed-vector Euclidean Rayleigh rate is the unique weight contraction estimand.", caveat="Closure is late-regime and replay-specific."),
        dict(stage="reduction", analysis="parameter_free_triangular", source="AIEF_1_4_parameter_free_triangular_closure.py", output="aief_1_4_parameter_free_triangular_closure", estimand="no-fit triangular rollout with measured lambda and fixed EMA multiplier", scope="saved Duhamel arrays", evidence="controlled counterfactual", result="POD coordinate predicts direction 1 late but Euclidean direction 0 fails; geometric gap rate closes.", superseded="Small transverse Euclidean residual guarantees accurate long rollout.", caveat="Rate closure and state-coordinate closure are distinct."),
        dict(stage="reduction", analysis="biorthogonal_triangular", source="AIEF_1_4_biorthogonal_triangular_closure.py", output="aief_1_4_biorthogonal_triangular_closure", estimand="fixed left/right modal coordinate and no-fit rollout", scope="saved Duhamel arrays", evidence="replay fact", result="Fixed late left covector repairs direction-0 rollout by ~4e4; adjoint bundle gives no material improvement.", superseded="Direction-0 failure requires a second weight mode or curved manifold.", caveat="One-dimensional success is conditional on this replay and tested directions."),
        dict(stage="operator_family", analysis="nested_operator_family", source="AIEF_1_4_nested_operator_family_audit.py", output="aief_1_4_nested_operator_family", estimand="distances to sparse/right/biorthogonal/symmetric families and defect POD", scope="complete exceptional K3 matrix sequence", evidence="replay fact", result="Right invariance appears far earlier; biorthogonal/symmetric defects are rank one and decay at EMA rate.", superseded="Full symmetry is required to explain geometric right invariance.", caveat="A one-branch defect mode is not universal across AIEF branches."),
        dict(stage="operator_family", analysis="analytic_defect_recurrence", source="AIEF_1_4_defect_recurrence_analytic_mode.py", output="aief_1_4_defect_recurrence_analytic_mode", estimand="analytic E* versus POD and pointwise defect multiplier", scope="complete exceptional K3 matrix sequence", evidence="replay fact", result="Analytic projected defect matches POD at 1-O(1e-12); dominant defect follows EMA multiplier pointwise late.", superseded="Defect direction is merely empirical POD output.", caveat="Shared multiplier does not by itself prove EMA causation."),
        dict(stage="causal_trace", analysis="defect_causal_ema_trace", source="AIEF_1_4_defect_causal_ema_trace.py", output="aief_1_4_defect_causal_ema_trace", estimand="complex EMA -> R -> proposal -> operator identities", scope="exceptional full replay", evidence="exact code identity", result="Downstream chain closes exactly, but full complex differences and source differences persist rather than decay.", superseded="Full complex DeltaC becomes source-free and decays homogeneously at EMA rate.", caveat="The unresolved mechanism lies in C -> |C| and phase geometry."),
        dict(stage="observable", analysis="radial_observable_subsystem", source="AIEF_1_4_radial_observable_subsystem_analysis.py", output="aief_1_4_radial_observable_subsystem", estimand="directed squared magnitudes, radial/tangent geometry, observable subsystem", scope="exceptional full replay", evidence="replay fact", result="Each directed magnitude channel acquires alpha independently; forward/reverse reinforce; complex difference becomes tangential.", superseded="Symmetrization cancellation creates the resonance mode.", caveat="Radial/tangential decomposition is geometric; squared-magnitude recurrence is exact."),
        dict(stage="observable", analysis="phase_source_locking", source="AIEF_1_4_phase_source_locking_analysis.py", output="aief_1_4_phase_source_locking", estimand="tracking-error and alignment-component decomposition", scope="exceptional full replay", evidence="replay fact", result="Source-memory locking, tangentialization, mean alignment, and T1~ -T2 cancellation explain the radial law.", superseded="Alignment law is cancellation free or both components vanish independently.", caveat="Source increment is ~5% of homogeneous tracking decrement late, not 1e-5."),
        dict(stage="observable", analysis="resonant_tracking_angular", source="AIEF_1_4_resonant_tracking_angular_analysis.py", output="aief_1_4_resonant_tracking_angular", estimand="complex resonant tracking, source limit, T1/T2, angular/radius freezing", scope="exceptional full replay", evidence="conditional mechanism", result="E/alpha^n is affine; S/alpha^(n+1) matches slope; phase separation freezes; radius difference decays at EMA rate.", superseded="Tracking error is a pure exponential without a polynomial prefactor.", caveat="Jordan structure is a reduced asymptotic subsystem, not the full nonlinear Jacobian."),
        dict(stage="observable", analysis="phase_balance_source_dynamics", source="AIEF_1_4_phase_balance_source_dynamics.py", output="aief_1_4_phase_balance_source_dynamics", estimand="intrinsic/coupling/history balance in source mean and separation", scope="exceptional full replay", evidence="replay fact", result="Mean, separation, and source increments acquire EMA rate through increasingly precise delayed phase-balance cancellation.", superseded="Phase-source stabilization is caused by vanishing individual phase terms.", caveat="Phase-balance convergence is replay evidence, not an invariant-manifold theorem."),
    ]


def superseded_claims() -> list[dict[str, str]]:
    return [
        dict(id="S01", claim="B is the unique or dominant memory carrier.", replacement="Memory is redundantly reconstructed; reset_B recovers mature topology nearly exactly.", evidence="AIEF-1.4 split-state memory ablation.", scope="40 paired seeds", status="retired"),
        dict(id="S02", claim="Admissibility is a rare repair or soft regularizer.", replacement="The hard map is active on essentially every mature update and is comparable to the proposed increment.", evidence="projection and active-boundary diagnostics", scope="implemented AIEF-1.3/1.4", status="retired"),
        dict(id="S03", claim="The mature full delayed system is at equilibrium.", replacement="The adaptive weight component is constraint-balanced; phase/history/EMA continue evolving.", evidence="stationarity and replay diagnostics", scope="mature baseline", status="retired"),
        dict(id="S04", claim="The exceptional trajectory undergoes an implemented active-face switch at t=124.05.", replacement="The event is a tolerance-classifier change; the positive-edge winner map remains fixed.", evidence="actual finite-step branch audit", scope="exceptional seed", status="retired"),
        dict(id="S05", claim="The finite-step exceptional K3 has an operational bare-gamma edge mode.", replacement="Node 2 is proposal-violating from the split and controls edge 29 under the actual finite map.", evidence="proposal/scale/winner audit", scope="dt=0.01 exceptional replay", status="retired"),
        dict(id="S06", claim="The controller equilibrium diag(c)alpha=Kalpha is an all-node relation.", replacement="The equation belongs on active saturated rows; slack rows can carry nonzero controller load.", evidence="component/controller residual decomposition", scope="fixed split states and exceptional replay", status="retired"),
        dict(id="S07", claim="Complete K4/K5/K6 components are only a spectral hypothesis.", replacement="Complete support components are reconstructed directly in the frozen cohort.", evidence="component topology audit", scope="40 split states", status="retired"),
        dict(id="S08", claim="A Euclidean scalar coordinate should predict both K3 tangent directions.", replacement="A fixed biorthogonal left coordinate is required by non-normality and repairs direction-0 rollout.", evidence="biorthogonal triangular closure", scope="exceptional late replay", status="retired"),
        dict(id="S09", claim="The POD Rayleigh quotient is the exact memory propagation rate.", replacement="The relevant rate is measured from the actual propagated forcing ensemble/geometric branch channel.", evidence="direct propagation-gap control", scope="exceptional late replay", status="retired"),
        dict(id="S10", claim="A shared two-state model in coordinates (a,g) has been identified.", replacement="Late collinearity makes unconstrained coefficients unidentifiable; the parameter-free triangular reduction is supported.", evidence="two-state conditioning and pooled rollout", scope="exceptional late replay", status="retired"),
        dict(id="S11", claim="The full directed complex EMA difference decays homogeneously at the EMA rate.", replacement="Complex differences persist; the radial magnitude observable decays while tangential separation remains.", evidence="causal EMA and radial-observable audits", scope="exceptional directed K3 channels", status="retired"),
        dict(id="S12", claim="Forward/reverse symmetrization creates the EMA-rate resonance mode.", replacement="Both directed magnitude channels carry the mode independently and reinforce under symmetrization.", evidence="radial-observable audit", scope="exceptional directed K3 channels", status="retired"),
        dict(id="S13", claim="The alignment law is cancellation free.", replacement="Tracking and tangential alignment terms are comparable and cancel with T1/T2 -> -1.", evidence="phase-source locking and resonant tracking", scope="exceptional directed K3 channels", status="retired"),
        dict(id="S14", claim="lambda_B/alpha_EMA is an established loop gain.", replacement="It is a relative-retention factor; a loop gain requires cross-block return operators.", evidence="triangular reduction and system partition", scope="late reduced model", status="retired"),
        dict(id="S15", claim="A rank-one weight tangent implies a one-dimensional full attractor or pointed torus.", replacement="The rank-one direction is a stable weight-sector response; full-state topology is unestablished.", evidence="rank/POD and augmented-state analysis", scope="tested weight tangent subspace", status="retired"),
        dict(id="S16", claim="The defect direction is only an empirical POD mode.", replacement="The dominant raw and projected defect matrices are derived from the implemented branch coefficients and match POD numerically.", evidence="analytic defect-mode audit", scope="exceptional fixed winner branch", status="retired"),
        dict(id="S17", claim="Source forcing is negligible because |Delta_t DeltaZ|/|E| is ~1e-5.", replacement="Relative to homogeneous EMA decrement, source forcing is ~5% late and remains measurable.", evidence="corrected tracking-forcing normalization", scope="exceptional directed K3 channels", status="retired"),
        dict(id="S18", claim="Phase-source stabilization occurs because intrinsic/coupling/history terms vanish separately.", replacement="Large phase terms cancel increasingly precisely to produce small mean/separation increments.", evidence="phase-balance source dynamics", scope="exceptional directed K3 channels", status="retired"),
    ]


def closure_note(lineage: list[dict[str, Any]], claims: list[dict[str, str]]) -> str:
    return f"""# AIEF-1.4 operator/cocycle analysis freeze note

**Freeze date:** {FREEZE_DATE}  
**Frozen production run:** `{RUN_HASH}`  
**Lineage rows:** {len(lineage)}  
**Superseded claims:** {len(claims)}

## Purpose

This freeze records the analysis chain from split-state memory ablation through the fixed-branch operator, augmented tangent, Duhamel decomposition, biorthogonal reduction, nested operator families, analytic defect, radial observable, resonant EMA tracking, and delayed phase-balance decomposition.

The freeze does not imply that every result is a universal theorem. Each row in `AIEF_1_4_analysis_lineage.csv` records its estimand, scope, evidence class, principal conclusion, and caveat.

## Hash authority

The `source_sha256_current` column hashes the source file currently present in this workspace. Several scripts were improved after their first reported run. For an exact historical execution hash, use the `analysis_manifest.json` stored in the corresponding output directory. The production run's source/input hashes remain those recorded under `runs/{RUN_HASH}/manifest.json`.

## Current closure status

### Closed numerically on the exceptional replay/tested subspace

- exact replay and fixed effective K3 winner branch;
- frozen and augmented tangent validation;
- exact direction-wise Duhamel reconstruction;
- geometric/biorthogonal scalar reduction;
- nested operator-family hierarchy;
- implementation-derived rank-one defect and pointwise EMA multiplier;
- exact complex EMA, squared-magnitude, proposal, and weight identities;
- resonant tracking, angular/radius freezing, and delayed phase-balance cancellation.

### Proof-ready implementation identities

- admissibility factorization and fiber linearity;
- strict-branch Jacobian and tie directional formula;
- fixed-winner sparse K3 block;
- nested invariant-family conditions;
- analytic left/right pair and defect matrices;
- phase increment, EMA tracking, squared-magnitude, and alignment identities;
- Duhamel and Jordan-resonant algebraic lemmas.

### Open

- formal augmented directional-differentiability theorem for the composed map;
- derivation of phase-balance convergence from the coupled nonlinear dynamics;
- timestep/safeguard convergence under regenerated states;
- consistently regenerated EMA sensitivity;
- invariant-subspace generality across existing K4/K5/K6 components;
- matched-phase B_carrier_only/full_reset correction;
- generality beyond one exceptional seed and two tangent directions.

## Superseded-claim policy

Claims listed in `AIEF_1_4_superseded_claims.csv` should not reappear without explicit historical qualification. Their replacement statements are the current preferred formulations.

## Next action

Follow `AIEF_1_4_FORWARD_PLAN.md`: formalize the proof-oriented manuscript, freeze administrative sources, test existing-component invariant subspaces, and only afterward design regenerated parameter/timestep studies.
"""


def main() -> None:
    raw_lineage = lineage_definitions()
    lineage: list[dict[str, Any]] = []
    for sequence, row in enumerate(raw_lineage, start=1):
        source_path = ROOT / row["source"]
        if not source_path.is_file():
            raise FileNotFoundError(source_path)
        lineage.append(
            {
                "sequence": sequence,
                "freeze_date": FREEZE_DATE,
                "stage": row["stage"],
                "analysis_id": row["analysis"],
                "source_file": row["source"],
                "source_sha256_current": sha256(source_path),
                "hash_role": "current workspace source; historical execution hash is in output analysis_manifest.json",
                "production_run_hash": RUN_HASH,
                "input_artifact_authority": f"runs/{RUN_HASH}/manifest.json and per-analysis analysis_manifest.json",
                "output_directory": row["output"],
                "estimand": row["estimand"],
                "scope": row["scope"],
                "evidence_class": row["evidence"],
                "principal_result": row["result"],
                "superseded_claim": row["superseded"],
                "key_caveat": row["caveat"],
                "freeze_status": "active lineage",
            }
        )

    lineage_fields = [
        "sequence",
        "freeze_date",
        "stage",
        "analysis_id",
        "source_file",
        "source_sha256_current",
        "hash_role",
        "production_run_hash",
        "input_artifact_authority",
        "output_directory",
        "estimand",
        "scope",
        "evidence_class",
        "principal_result",
        "superseded_claim",
        "key_caveat",
        "freeze_status",
    ]
    atomic_csv(ROOT / "AIEF_1_4_analysis_lineage.csv", lineage, lineage_fields)

    claims = superseded_claims()
    claim_fields = [
        "id",
        "claim",
        "status",
        "replacement",
        "evidence",
        "scope",
    ]
    atomic_csv(ROOT / "AIEF_1_4_superseded_claims.csv", claims, claim_fields)

    note = closure_note(lineage, claims)
    atomic_text(ROOT / "AIEF_1_4_operator_cocycle_closure_note.md", note)

    administrative_files = [
        "AIEF_1_4_analysis_lineage.csv",
        "AIEF_1_4_superseded_claims.csv",
        "AIEF_1_4_operator_cocycle_closure_note.md",
        "AIEF_1_4_OPERATOR_COCYCLE_CLOSURE_THEOREM_NOTE.md",
        "AIEF_1_4_OPERATOR_THEORY_MANUSCRIPT.md",
        "AIEF_1_4_OPERATOR_COCYCLE_THOUGHT_TREE.md",
        "AIEF_1_4_FORWARD_PLAN.md",
        "AIEF_HISTORIC_UNFOLDING.md",
        "AI_AGENT_HANDOFF_PROMPT.md",
    ]
    freeze_manifest = {
        "freeze_date": FREEZE_DATE,
        "production_run_hash": RUN_HASH,
        "lineage_row_count": len(lineage),
        "superseded_claim_count": len(claims),
        "generator": {
            "path": Path(__file__).name,
            "sha256": sha256(Path(__file__)),
        },
        "hash_note": (
            "Current workspace source hashes are not substitutes for historical "
            "execution hashes in per-analysis manifests."
        ),
        "files": {},
    }
    for filename in administrative_files:
        path = ROOT / filename
        if path.is_file():
            freeze_manifest["files"][filename] = sha256(path)
        else:
            freeze_manifest["files"][filename] = None
    atomic_text(
        ROOT / "AIEF_1_4_lineage_freeze_manifest.json",
        json.dumps(freeze_manifest, indent=2, sort_keys=True) + "\n",
    )

    print(f"Wrote {len(lineage)} lineage rows")
    print(f"Wrote {len(claims)} superseded claims")
    print("Wrote AIEF_1_4_operator_cocycle_closure_note.md")
    print("Wrote AIEF_1_4_lineage_freeze_manifest.json")


if __name__ == "__main__":
    main()
