# Proposed007 comparison helper — owner/seat integration decision required

One finding only: B-F6, the already-known engine complex-NaN false-equality
mechanism. Reuse the existing modular helper's component split, retaining the
engine function's shape/dtype/real/fallback behavior. No new algorithm/novelty or
saved-data impact is claimed.

**Do not edit or replace `aief_experiment_engine_v1.py` in place.** On tested main
it is ART-0702, Frozen and authority-locked (`registry/artifacts.csv:703`).
Do not update/disable a lock to make this proposal pass. Importing
`componentwise_exact.py` installs/patches nothing.

Permissible future routes, after explicit owner/seat review:

1. A NEW verification companion that calls this predicate at a clearly documented
   comparison boundary, with its own provenance and authority status; or
2. An authorized NEW engine successor whose comparison function uses this code,
   with explicit erratum/registry/lock handling and independently reviewed tests.

This packet chooses neither authority route and does not produce a production
patch, frozen-run certificate or approved successor. Do not silently monkeypatch
an already-authority-labelled live run and describe it as the frozen engine.

The test-only `candidate-engine` mode compiles the reviewed full engine AST after
replacing just its comparison function. The other98 top-level nodes are preserved;
its name and `__file__` identify a **memory-only, non-authority candidate**. Only
its comparison predicate is called; `run_baseline_equivalence`, simulations and
lock validation are NOT run. This is a controlled failing-before/passing-after
vehicle, not a reusable certified engine artifact.

The direct leaf and existing modular AST-extracted helper are tested against the
SAME independent scalar-component specification. The full modular package is not
imported or certified. Noncomplex fallback remains unchanged; no object/datetime/
structured-dtype policy is introduced. Exact value equality is not byte identity:
signed zeros match and matching NaN payload/sign bits are ignored.

**Unchanged limits:** engine max-difference diagnostics at2441–2443,2503–2505 and
2539–2541 still apply whole-element missingness masks; no component-resolved error
report is supplied/approved here. No full equivalence-validation pipeline, array
census, real trajectory or production result is changed or rechecked. Four red
contract methods and220 reduced-alphabet false accepts are synthetic checks, not
four new bugs or220 affected production records.

Request: Researcher001/AuditorSeat002 independently review the new helper,
pre-call oracle/input-preservation checks, exact dtype/shape policy, arbitrary-
shape and partial-NaN/Inf/ULP counterexamples. Choose an authorized integration
route and any needed diagnostics before using it for a citable certificate.
Keep any oracle-uniqueness change on a separate branch. Owner uploads this note;
no remote push/PR/contact/upload has been performed by Researcher040282.
