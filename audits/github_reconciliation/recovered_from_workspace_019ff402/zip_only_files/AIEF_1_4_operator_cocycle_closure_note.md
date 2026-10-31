# AIEF-1.4 operator/cocycle analysis freeze note

**Freeze date:** 2026-07-26  
**Frozen production run:** `5a9f093a2fe0`  
**Lineage rows:** 32  
**Superseded claims:** 18

## Purpose

This freeze records the analysis chain from split-state memory ablation through the fixed-branch operator, augmented tangent, Duhamel decomposition, biorthogonal reduction, nested operator families, analytic defect, radial observable, resonant EMA tracking, and delayed phase-balance decomposition.

The freeze does not imply that every result is a universal theorem. Each row in `AIEF_1_4_analysis_lineage.csv` records its estimand, scope, evidence class, principal conclusion, and caveat.

## Hash authority

The `source_sha256_current` column hashes the source file currently present in this workspace. Several scripts were improved after their first reported run. For an exact historical execution hash, use the `analysis_manifest.json` stored in the corresponding output directory. The production run's source/input hashes remain those recorded under `runs/5a9f093a2fe0/manifest.json`.

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
