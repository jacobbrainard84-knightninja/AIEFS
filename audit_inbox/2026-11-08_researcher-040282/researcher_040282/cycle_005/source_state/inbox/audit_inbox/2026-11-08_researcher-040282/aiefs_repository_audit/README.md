# AIEFS `audit-inbox` audit reproduction package

Start with **AUDIT-REPORT.md**. This package contains the audit programs, raw logs,
selected generated analysis results, and public snapshot metadata. It does **not**
contain the 1.3 GB repository or the raw NPZ datasets.

## Safety and scope

- Audit target: the user-requested `audit-inbox` snapshot recorded in
  `branch_snapshot.json`. Findings are not attributed to another branch.
- No repository patch was applied. Public acquisition uses HTTPS GET requests.
- Git safety tests create temporary **local bare remotes**. They never push to
  GitHub and never use real credentials. Credential-shaped fixtures are invalid
  dummy strings.
- Archived inbox scripts are not executed by these reproductions.
- Generated analysis evidence is outside the source snapshot.
- The existing sync README documents `chmod` setup. The original shell suite was
  run after that setup on a temporary copy, not by changing the snapshot's modes.

## Environment

The audit used Python 3.13.16 on Linux x86_64, NumPy 2.3.5, pandas 2.2.3,
pytest 9.0.3, SciPy 1.17.1, and SymPy 1.14.0. Git and Bash are required for the
local-remote controls. `requirements-audit.txt` records the Python package pins.

The saved S01 manifest records a different numerical environment. These audit
pins do **not** promise bitwise reproduction of the saved S01 trajectories. The
same-environment modular/original replay comparison is a separate check.

## Obtain inputs

Run from this package's directory. The default is a verified **sparse HTTP
snapshot**, not a clone. This downloads selected source/configuration/small
artifacts, then the three selected larger files used in the audit:

```bash
python acquire_repository.py
python acquire_repository.py \
  runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_branch_diagnostics.npz \
  runs/b57562a8ee77/AIEF_1_4_Twindow_sensitivity_b57562a8ee77_branch_diagnostics.npz \
  runs/b57562a8ee77/baseline_equivalence_certificate.json
python verify_inputs.py
```

This is about 63 MB of snapshot files rather than the entire repository. The
acquirer checks downloaded bytes against the saved Git tree and restores tracked
file modes. It does not execute downloaded scripts.

Alternatively, point the audit programs at an existing checkout of the audited
source:

```bash
export AIEFS_AUDIT_REPO=/absolute/path/to/AIEFS
```

The source and raw files must match this audit's target for the reported results
to be comparable. `verify_inputs.py` checks the selected files and verifies the
actual authority lock; it does **not** regenerate the numerical baseline.

## Run the independent controls

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -rx -p no:cacheprovider test_deep_audit.py
```

Recorded final result: **9 passed, 8 xfailed**. Strict `xfail` markers identify
known defect/risk witnesses, not additional passing tests. Their assertions are
exposed with:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -m xfail --runxfail \
  -p no:cacheprovider test_deep_audit.py
# Expected exit status 1: eight failing assertions, nine deselected tests.
```

The eight witnesses cover seven report findings because the unpublished-content
and intermediate-history cases are grouped under F2. The interval witness tests
the population-uncertainty interpretation discussed explicitly under F3.

Collect quantitative witnesses and individual helper logs:

```bash
PYTHONDONTWRITEBYTECODE=1 python additional_probes.py
PYTHONDONTWRITEBYTECODE=1 python probe_duplicate_oracle.py
```

The second command tests the public oracle using the real S01 scalar CSV/NPZ
without changing them, plus a duplicate status record in a temporary candidate.
That known-false control is not a regenerated production candidate.

## Actual-data analysis and bounded engine replay

```bash
PYTHONDONTWRITEBYTECODE=1 python check_real_s01.py
PYTHONDONTWRITEBYTECODE=1 python replay_one_condition.py
```

- `check_real_s01.py` validates actual S01, executes the complete analysis with
  2,000 bootstrap replicates, and compares all 4,800 held cases to an independent
  integer-grid-span oracle. It does not regenerate engine trajectories.
- `replay_one_condition.py` regenerates one real condition through both actual
  orchestration paths: 176,000 integration steps per path. It compares their
  logical NPZ/scalar outputs exactly, then characterizes the mismatch with the
  saved S01 output in the different environment. It does not run the complete
  40-seed baseline or 200-condition modular experiment.
- New analysis bundles have new timestamps; comparison should use logical
  outputs and stated checks, not expect identical directory names.

## Existing repository tests

For the default downloaded layout:

```bash
repo="$PWD/repository"
pkg="$repo/AIEF_Experiments/aief_modular_platform_v1_analysis_v4"
(cd "$pkg" && PYTHONPATH="$repo:$pkg" PYTHONDONTWRITEBYTECODE=1 \
  python -m pytest -q -p no:cacheprovider tests_modular)
(cd "$pkg" && AIEF_RUN_SLOW_TESTS=1 PYTHONPATH="$repo:$pkg" PYTHONDONTWRITEBYTECODE=1 \
  python -m pytest -q -p no:cacheprovider tests_modular/test_twindow_one_condition.py)
```

Recorded: **40 passed / 2 skipped** in the ordinary suite; the opt-in smoke was
then run separately and **passed**. The full regenerated-candidate oracle test
was not run. Unit tests alone are not full numerical certification.

To repeat the original shell suite using its documented permissions setup:

```bash
scratch=$(mktemp -d)
cp -R "$repo/tools" "$scratch/tools"
chmod +x "$scratch"/tools/sync/*.sh "$scratch"/tools/sync/tests/*.sh
bash "$scratch/tools/sync/tests/run_tests.sh"
rm -rf "$scratch"
```

Recorded: **108 checks passed / 0 failed**. The additional audit tests expose
cases those existing checks omit.

## Evidence map

| File | Meaning |
|---|---|
| `evidence/deep_audit_pytest.txt` | Final added suite, strict expected failures listed |
| `evidence/deep_audit_unmasked.txt` | Eight actual failing witness assertions |
| `evidence/local_git_safety_probes.json` | Quantitative local-remote safety results |
| `evidence/upload_*.txt` | Actual uploader transcripts for dummy fixtures |
| `evidence/independent_scientific_probes.json` | Wrong-branch numbers, boundary coverage example, real complex-array finiteness |
| `evidence/duplicate_public_oracle.json` | Public oracle incorrectly accepting 201 versus 200 status rows |
| `evidence/real_s01_execution.json` | Actual-data counts and independent held-grid comparison |
| `evidence/real_s01_analysis/` | Complete actual S01 analysis output bundle |
| `evidence/one_condition_replay.json` | Same-environment agreement and saved-oracle differences |
| `evidence/modular_pytest.txt` | Existing ordinary repository suite |
| `evidence/repository_slow_smoke.txt` | Existing opt-in numerical smoke |
| `evidence/sync_original_suite.txt` | Original 108-check shell suite |
| `evidence/actual_authority_lock_check.json` | Actual input/source lock verification, not numerical regeneration |
| `evidence/final_snapshot_integrity.json` | Final 937-file byte/mode verification |
| `evidence/documented_cli_describe.txt` | Reproduced, already-triaged CLI import-path issue |

The initial Git test-harness setup error is retained as
`deep_audit_pytest_initial_harness_error.txt` for transparency. Repository-local
Git identity was then configured in the isolated fixtures, and the final tests
were rerun. That setup failure is not counted as a product finding.

Lean compilation, the complete numerical baseline, the full modular production
run, full bridge replay, and literature/novelty adjudication remain outside the
completed execution evidence. See the report for the precise limitations.
