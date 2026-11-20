# research/hardening

Truthfulness-hardening tools (plan 2026-11-20). Report-only: nothing here is a CI pass/fail gate.

## py_mutation_check.py (H3)
Hand-rolled, stdlib-only (ast) mutation tester for the checker scripts (tools/ci/*.py,
audits/engineering/verify_inventory_current.py). It clones the repo into a scratch folder, writes one mutant at a
time into the clone, and asks whether the checker's own tests, a run on the clean clone, or a run on a known-bad
fixture notice. Survivors are candidate test gaps, to be classified by reading the code (equivalent or real gap).

    unshare -rn python3 research/hardening/py_mutation_check.py --out report.json     # ~25 min, all checkers

Deterministic (fixed seed, at most 40 mutants per file), per-signal timeout, never touches the working tree.
Out of scope and refused: research/engine_guards, the SHA-locked engine, Pinned/, lean/AIEFProofs*, AIEFFreezeCore.
Self-test (the tool's own negative control): `pytest research/hardening/tests` (a weak test must leave a
survivor; a strong test must kill every mutant). Not run by CI.
