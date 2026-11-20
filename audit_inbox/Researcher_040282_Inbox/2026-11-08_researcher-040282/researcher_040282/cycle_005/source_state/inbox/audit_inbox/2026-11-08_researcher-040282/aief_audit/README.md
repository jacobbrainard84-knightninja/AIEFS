# Reproducing this source audit

Start with **AUDIT-REPORT.md**.

## Scope

This package audits the supplied Python analysis, not the underlying scientific
model or actual S01 dataset. No actual study trajectories are included.
`analysis_under_audit.py` is the pasted source; it was not patched.

The real `aief_modular` package was unavailable. `audit_support.py` loads the
source with only those import statements omitted and supplies explicit I/O and
exception stand-ins. All analysis function bodies execute unchanged. This is
not a validation of the actual imported package.

`synthetic_fixture.py` makes an artificial 40-seed, five-regime, four-branch
fixture with the expected schema and saved times. It is not a model simulation,
a reconstruction of S01, or a real baseline-equivalence test. Files it calls
certificates are solely clearly labeled test inputs.

## Dependencies / tested environment

- Python 3.13.16
- NumPy 2.3.5
- pandas 2.2.3
- pytest 9.0.3

The audit imports no SciPy. Tests create temporary synthetic files.

## Commands

```bash
python -m pytest -q -rx --durations=8 test_audit.py
python probes.py
```

Expected for the unmodified source: **23 passed, 6 xfailed**.
The expected failures document unresolved regression cases; they are not fixes
and must not be described as a clean bill of health.

To inspect those regression failures without the expected-failure markers:

```bash
python -m pytest -q --runxfail --tb=short \
  -k 'fixed_hold_translation or literal_timestamp or zero_events or published_input_digest or nominal_window_check or staged_manifest_payload' \
  test_audit.py
```

Expected: **6 failed, 23 deselected** (nonzero process exit status).

## Files

- `AUDIT-REPORT.md`: findings, caveats, source locations, repair priorities.
- `analysis_under_audit.py`: unchanged supplied program.
- `audit_support.py`: dependency stand-ins and transparent loader.
- `synthetic_fixture.py`: synthetic inputs only.
- `test_audit.py`: controls, characterizations, and expected regressions.
- `probes.py`: deterministic numerical witnesses.
- `probe_results.json`: recorded probe output.
- `pytest_results.txt`: recorded test run with expected-failure markers.
- `unmasked_failures.txt`: actual regression traces without those markers.

Do not use this synthetic audit package to draw conclusions about the real
study's event counts, effect sizes, baseline equivalence, or coverage.
