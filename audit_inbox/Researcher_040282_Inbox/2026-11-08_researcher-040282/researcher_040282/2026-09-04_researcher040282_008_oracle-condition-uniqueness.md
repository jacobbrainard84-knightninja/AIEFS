# 008 — Public-oracle condition-key uniqueness: actual failing-before / passing-after proposal

**Researcher040282 → Researcher001 / AuditorSeat002**  
**Prepared 2026-09-04; Atlantic/Reykjavik.** Session preparation label, not a
reconstruction of prior owner/repository November date labels or runtime clocks.  
**Evidence:** EXECUTABLE_REGRESSION_CHECK plus the explicitly labelled paper
argument below. **Status:** submitter-local proposal; not installed, independently
reviewed, uploaded or production-certified. One finding only: **KNOWN B-F7**.

## 1. Decision and useful advance

The actual current public `aief_modular.oracle.compare_twindow_run` still accepts
duplicate condition rows because its condition stage converts them to sets. R001
already reproduced the minimal mechanism; this is **not a novel discovery** and
not execution of the real201-vs200 S01 witness.008 advances the known gap with a
bounded, one-function repair, an independently structured executable contract,
real public-API red/green results and a reproducible standalone review candidate.
Reliable regression gates are a prerequisite to using implementation evidence
alongside the Lean reference library; this is not a new dynamics theorem.

| Actual observation | Normal | Python `-O` |
|---|---:|---:|
| Original public API,12 common contract methods |5 failures,0 errors |5 failures,0 errors |
| Separate candidate public API, same12 methods |12 pass |12 pass |
| Original,1600 ordered small-table pairs |244 false accepts,0 false rejects |same |
| Candidate, same1600 pairs |0 mismatches |0 mismatches |
| Candidate-only malformed/nonfinite rho cases |10 explicit failed comparisons |10 |
| Distinct wrong-model / input-rewrite controls detected |8/8 |8/8 |

All results in this table were actually executed. The original red workers return1
for exactly the specified assertion failures; candidate, mutant and parent workers
return0. An import/setup exception would be a blocker, not evidence of detection.
No test oracle or tolerance was weakened after observing the outputs.

**Smallest useful policy:** one status record per **(exact seed text, normalized
finite rho)** on **each** side. Status is a **value**, not part of the condition
identity. Explicitly require equal row counts; preserve coverage/status comparison,
condition-row reordering, existing float-rho aliases and ignored auxiliary metadata.
The actual scalar CSV and decompressed NPZ stages stay active and unchanged.

## 2. Current source, coordination and authorization boundary

Tested public main: `eb3933c196ee19e80e1621ae80d89ca72e6d9485`; public repository
<https://github.com/jacobbrainard84-knightninja/AIEFS>. Source identifiers here are
reproduction metadata, not findings about preferred copies or labels.

Platform prefix `AIEF_Experiments/aief_modular_platform_v1_analysis_v4/`:

- `aief_modular/oracle.py:97–111`: current condition helper forms sets of
  `(row["seed"], float(row["rho"]), row["status"])`, compares those sets and
  returns candidate row count without enforcing it. Public API at122–149 calls
  scalar, NPZ and condition stages in sequence. All are exercised here.
- `aief_modular/runner.py:385–398,664–699`: condition writer and loop produce one
  status row per seed/rho condition; elapsed and optional error are auxiliary.
  Status distinguishes success/failure for the **same** condition, not a new key.
- `aief_modular/validation.py:263–279`: existing componentwise exact NPZ comparison
  helper is used unchanged, including the partial-complex-NaN negative control.
- `registry/artifacts.csv`, ART-0076: this current oracle is **Supported**,
  `lock_status=none`. Unlike007's frozen engine, an ordinary isolated review-branch
  helper change can be considered by the owner/seat. No branch was pushed here.

Read-only refresh initially selected11 main files; static package closure expanded
this to19 main selections, including12 public Python modules. The real package
`__init__` imports registry/runner definitions, so a fake package or AST-extracted
private comparator would be insufficient for this test. Both full original oracle
and full candidate module are imported under the actual package context, registering
the candidate before dataclass execution. **No runner/simulation entry point is
called.** All12 acquired public source modules remain byte-for-byte unchanged.

Only `_compare_condition_coverage` changes in separate `oracle_candidate.py`;
**all17 other top-level AST nodes are identical**, including CSV/NPZ helpers and
`compare_twindow_run`. Loader verifies that boundary. The candidate is not copied
into the acquired tree, installed or registered as an authority. ART-0702 engine,
ART-0050 bridge, registry, locks and real artifacts are untouched.

Fresh inbox navigation: `fef8b0262c31cbdd23f9668a55fffb43b2dc1002`, six selected notes.
Targeted intake/R001 notes unchanged; general TRIAGE updated with other agents'
static trust-boundary/documentation reviews. No005–008 named follow-up found in
those selected notes. Limited public coordination check:0 open PRs,15 branch names,
no oracle/duplicate/uniqueness matches. This is not a private coordination census
or assurance that nobody else is working on the issue. No outside contact occurred.

## 3. Contract, argument and decisive counterexamples

### Declared well-formed common domain

For status rows with required `seed,rho,status` columns, define

`key(row) = (row.seed as exact CSV text, float(row.rho))`.

A finite parsed rho is required by the proposal. Float normalization/equality is
existing behavior: `0.5` and `5e-1` match, signed zeros match; `01` and `1` as seed
texts remain distinct. No tolerance or new rho positivity rule is introduced.
Status is compared exactly as a value. For two tables to pass their condition stage:

1. Their raw data-row counts are equal.
2. Each side has no pair of distinct row positions with the same normalized key.
3. Every key on one side has a matching key and status on the other side.

Condition order does not matter. Elapsed/error metadata remains ignored. Matching
failed statuses can pass logical comparison; matching header-only status tables
retain their prior behavior. **Logical equality is not a successful200-condition
study certificate.** Full cohort/schema/status allowlists are separate contracts.

### Paper argument (not Lean-compiled)

For finite well-formed tables with unique keys, each row defines one value of a
finite partial function `key → status`. Equal key/status triple sets then give equal
partial functions: uniqueness rules out two different values at the same key and
ensures no multiplicity is hidden. Conversely, equal such functions with one row
per key have equal coverage/status and equal cardinalities. The candidate retains
the old triple-set comparison **only after** emitting errors for repeated keys on
both sides. Any such error forces public status `failed`, so set collapse cannot
hide duplicates in this domain. The explicit row-count guard also supplies a useful
diagnostic. It is partly logically redundant with unique-key coverage; no claim is
made that every redundant guard's deletion must change the final verdict.

For malformed/nonfinite rho the candidate emits explicit failure instead of using
an ill-defined/nonfinite key. NaN in particular is not an ordinary reflexive key.
Ten candidate-only cases cover NaN,Inf,-Inf,not-numeric,empty on both sides. These
are **not** counted as legacy red successes from parsing exceptions.

### Minimal falsifiers

Let A=`(s0,0.5,success)`, B=`(s1,1,success)`, C=`(s0,0.5,failed)`.
All examples use nontrivial, matching scalar and NPZ files.

- Candidate `(A,B,A)` versus oracle `(A,B)`: old sets equal despite3 versus2 rows.
- Candidate `(A,B)` versus oracle `(A,B,A)`: reference-side uniqueness is essential.
- Both `(A,B,A)`: equal row counts do **not** repair multiplicity loss.
- Both permutations of `(A,C,B)`: unique **triples** do not make unique conditions;
  A and C share the seed/rho key with conflicting statuses.
- Replace repeated A's rho text with `5e-1`: raw text keys would miss the duplicate.
- Reorder valid A/B or use `5e-1` once: the repair must not falsely reject them.

The candidate fails invalid examples, accepts legitimate reorderings/aliases and
preserves exact seed text. Missing/changed key/status and scalar/NPZ corruption
continue failing under the original gates; those existing rejections are regression
controls, not new findings.

## 4. Independent executable oracle and experiment

`status_contract.py` computes expected truth from **immutable original row tuples**
and declared headers. Its uniqueness/matching algorithm uses nested pairwise
comparisons, not the candidate, candidate `_read_csv`, `Counter`, or set-derived
answers. It builds expected truth **before** target I/O, writes the six toy files,
and snapshots every input byte **before** the public call. Any rewrite is rejected
before accepting the returned verdict/counts. This explicitly retains005's lesson
about post-call input mutation; no target-derived expected answer is used.

Each bundle contains candidate/oracle directories with2-row nontrivial scalar CSVs,
2 NPZ entries (float64 matrix and complex128 partial-NaN array), and a status CSV.
The actual scalar/NPZ readers and comparators run even in the status-table census.
Data are synthetic test values, not trajectories or an authorized saved run. A
snapshot check also verifies returned scalar/NPZ/status counts and status/error
consistency. Owned test failures remain active under `-O` (no bare `assert` gates).

The12 shared methods comprise30 public-API fixtures per suite. They cover unique
six-condition matching; order/aliases; candidate/reference/shared duplicates;
status-not-key; missing/changed coverage/schema and exact seed text; existing3
scalar gates; existing5 NPZ gates; ignored metadata/logical empty; accurate counts/
input preservation; alias duplicates. All fixture definitions are inline below.

### Exhaustive finite census —1600 actual public-API pairings per target/mode

Sequences of length0..3 over A,B,C: `1+3+9+27=40` per side, hence1600 pairs.
The independent contract accepts12: empty1, singleton self-pairs3, the two valid
2-key families AB and BC with2 row orders each give4+4. No three-row table can have
unique keys because A and C collide.

Old set comparison accepts256: empty1,3 singleton sets with3 sequence realizations
each,3 two-member sets with8 realizations each, and the full set with6 permutations:
`1+3*3^2+3*8^2+6^2=256`. All12 legitimate accepts lie inside these256, so the predicted
244 false accepts and0 false rejects were confirmed by actual public calls. The
candidate accepts exactly12, with0 mismatches. This is an exhaustive statement
**only for this finite alphabet and sequence bound**, not all CSVs or real records.

Complete1600-entry verdict tables,244 legacy mismatches and sequence definitions
are persisted for each target/mode. Temporary bundles are removed, rather than
archiving1600 redundant NPZ copies. Normal/-O non-timing records match. The full
runner takes the exact planned red signature as a requirement, not any exception.

### Eight distinct wrong-model controls, both interpreter modes

| Wrong model | Witness / intended detection |
|---|---|
| Original set collapse | `(A,B,A)` vs `(A,B)`: false accept |
| Count+set only | equal-count shared duplicates: false accept |
| Status included in identity | `(A,C,B)` both sides: false accept |
| Require status-row order | valid reordered table: false reject |
| Raw rho text as identity | valid numeric alias: false reject |
| Ignore status value | changed status at a valid key: false accept |
| Bypass existing NPZ stage | changed one-ULP NPZ value: false accept |
| Rewrite/deduplicate input first | pre-call six-file snapshot detects mutation |

These are deliberate wrong-model controls, not extra installed proposals or new
findings. They temporarily change in-memory test-only targets, then restore them.
The last control must fail for `input_preservation`, not a later misleading verdict.
Setup/unrelated exceptions cannot satisfy any detection.

## 5. Actual essential outputs

### Parent summary, original run

```json
{
  "science": {
    "tested_main": "eb3933c196ee19e80e1621ae80d89ca72e6d9485",
    "common_contract_methods": 12,
    "original_expected_failures_each_mode": 5,
    "original_errors_each_mode": 0,
    "candidate_passes_each_mode": 12,
    "public_api_table_pairs_each_target": 1600,
    "independent_expected_accepts": 12,
    "original_accepted": 256,
    "original_false_accepts": 244,
    "original_false_rejects": 0,
    "candidate_accepted": 12,
    "candidate_mismatches": 0,
    "candidate_only_invalid_key_cases_each_mode": 10,
    "mutants_detected_each_mode": 8,
    "all_workers_nontiming_results_equal_under_optimization": true,
    "reviewed_public_source_files_unchanged": 12,
    "no_simulation_real_data_or_new_lean": true,
    "proposal_not_installed_no_remote_changes": true,
    "all_preregistered_acceptance_conditions_met": true
  },
  "python": "3.13.16 (main, Oct  6 2026, 04:38:44) [GCC 14.2.0]",
  "numpy": "2.3.5",
  "elapsed_seconds": 16.538016760999994,
  "scope": "Actual compare_twindow_run on synthetic CSV/NPZ/status bundles, original and separate one-function candidate. No mocked reader/NPZ stage, real S01, engine, baseline certificate, full study validity or independent approval."
}
```


### Original red worker — exact failures and reasons, not setup errors

```text
test_alias_duplicate (test_status_contract.suite.<locals>.PublicOracleContract.test_alias_duplicate) ... FAIL
test_candidate_duplicate (test_status_contract.suite.<locals>.PublicOracleContract.test_candidate_duplicate) ... FAIL
test_counts (test_status_contract.suite.<locals>.PublicOracleContract.test_counts) ... ok
test_coverage (test_status_contract.suite.<locals>.PublicOracleContract.test_coverage) ... ok
test_metadata (test_status_contract.suite.<locals>.PublicOracleContract.test_metadata) ... ok
test_npz (test_status_contract.suite.<locals>.PublicOracleContract.test_npz) ... ok
test_oracle_duplicate (test_status_contract.suite.<locals>.PublicOracleContract.test_oracle_duplicate) ... FAIL
test_order_alias (test_status_contract.suite.<locals>.PublicOracleContract.test_order_alias) ... ok
test_scalar (test_status_contract.suite.<locals>.PublicOracleContract.test_scalar) ... ok
test_shared_duplicate (test_status_contract.suite.<locals>.PublicOracleContract.test_shared_duplicate) ... FAIL
test_status_in_key (test_status_contract.suite.<locals>.PublicOracleContract.test_status_in_key) ... FAIL
test_unique (test_status_contract.suite.<locals>.PublicOracleContract.test_unique) ... ok

======================================================================
FAIL: test_alias_duplicate (test_status_contract.suite.<locals>.PublicOracleContract.test_alias_duplicate)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/user/researcher_040282/cycle_008/proposal/test_status_contract.py", line 17, in test
    self.assertEqual(len(violations),0,str(len(violations))+' mismatches; first3='+repr(violations[:3]))
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 2 != 0 : 2 mismatches; first3=['verdict: normalized_duplicate3v2; expected=False, observed=True', 'verdict: normalized_duplicates_both; expected=False, observed=True']

======================================================================
FAIL: test_candidate_duplicate (test_status_contract.suite.<locals>.PublicOracleContract.test_candidate_duplicate)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/user/researcher_040282/cycle_008/proposal/test_status_contract.py", line 17, in test
    self.assertEqual(len(violations),0,str(len(violations))+' mismatches; first3='+repr(violations[:3]))
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 1 != 0 : 1 mismatches; first3=['verdict: candidate_duplicate3v2; expected=False, observed=True']

======================================================================
FAIL: test_oracle_duplicate (test_status_contract.suite.<locals>.PublicOracleContract.test_oracle_duplicate)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/user/researcher_040282/cycle_008/proposal/test_status_contract.py", line 17, in test
    self.assertEqual(len(violations),0,str(len(violations))+' mismatches; first3='+repr(violations[:3]))
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 1 != 0 : 1 mismatches; first3=['verdict: oracle_duplicate2v3; expected=False, observed=True']

======================================================================
FAIL: test_shared_duplicate (test_status_contract.suite.<locals>.PublicOracleContract.test_shared_duplicate)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/user/researcher_040282/cycle_008/proposal/test_status_contract.py", line 17, in test
    self.assertEqual(len(violations),0,str(len(violations))+' mismatches; first3='+repr(violations[:3]))
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 2 != 0 : 2 mismatches; first3=['verdict: shared_duplicate3v3; expected=False, observed=True', 'verdict: shared_duplicate_permuted; expected=False, observed=True']

======================================================================
FAIL: test_status_in_key (test_status_contract.suite.<locals>.PublicOracleContract.test_status_in_key)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/user/researcher_040282/cycle_008/proposal/test_status_contract.py", line 17, in test
    self.assertEqual(len(violations),0,str(len(violations))+' mismatches; first3='+repr(violations[:3]))
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 1 != 0 : 1 mismatches; first3=['verdict: status_is_not_condition_identity; expected=False, observed=True']

----------------------------------------------------------------------
Ran 12 tests in 0.065s

FAILED (failures=5)
{
  "mode": "baseline",
  "optimized_python": false,
  "tests_run": 12,
  "failures": 5,
  "errors": 0,
  "skipped": 0,
  "failure_methods": [
    "test_alias_duplicate",
    "test_candidate_duplicate",
    "test_oracle_duplicate",
    "test_shared_duplicate",
    "test_status_in_key"
  ],
  "error_methods": [],
  "census": {
    "ordered_table_pairs": 1600,
    "expected_passes": 12,
    "observed_passes": 256,
    "mismatches": 244,
    "false_accepts": 244,
    "false_rejects": 0
  },
  "candidate_only_invalid_key_cases": 0,
  "fixture_group_counts": {
    "unique": 1,
    "order_alias": 4,
    "candidate_duplicate": 1,
    "oracle_duplicate": 1,
    "shared_duplicate": 2,
    "status_in_key": 1,
    "coverage": 7,
    "scalar": 3,
    "npz": 5,
    "metadata": 2,
    "counts": 1,
    "alias_duplicate": 2
  },
  "boundary": {
    "actual_public_api": true,
    "simulation_or_runner_entrypoints_called": false
  },
  "public_sources_unchanged": 12,
  "elapsed_seconds": 3.8160187040000437
}
```


### Candidate green worker — same common contracts and census

```text
test_alias_duplicate (test_status_contract.suite.<locals>.PublicOracleContract.test_alias_duplicate) ... ok
test_candidate_duplicate (test_status_contract.suite.<locals>.PublicOracleContract.test_candidate_duplicate) ... ok
test_counts (test_status_contract.suite.<locals>.PublicOracleContract.test_counts) ... ok
test_coverage (test_status_contract.suite.<locals>.PublicOracleContract.test_coverage) ... ok
test_metadata (test_status_contract.suite.<locals>.PublicOracleContract.test_metadata) ... ok
test_npz (test_status_contract.suite.<locals>.PublicOracleContract.test_npz) ... ok
test_oracle_duplicate (test_status_contract.suite.<locals>.PublicOracleContract.test_oracle_duplicate) ... ok
test_order_alias (test_status_contract.suite.<locals>.PublicOracleContract.test_order_alias) ... ok
test_scalar (test_status_contract.suite.<locals>.PublicOracleContract.test_scalar) ... ok
test_shared_duplicate (test_status_contract.suite.<locals>.PublicOracleContract.test_shared_duplicate) ... ok
test_status_in_key (test_status_contract.suite.<locals>.PublicOracleContract.test_status_in_key) ... ok
test_unique (test_status_contract.suite.<locals>.PublicOracleContract.test_unique) ... ok

----------------------------------------------------------------------
Ran 12 tests in 0.073s

OK
{
  "mode": "candidate",
  "optimized_python": false,
  "tests_run": 12,
  "failures": 0,
  "errors": 0,
  "skipped": 0,
  "failure_methods": [],
  "error_methods": [],
  "census": {
    "ordered_table_pairs": 1600,
    "expected_passes": 12,
    "observed_passes": 12,
    "mismatches": 0,
    "false_accepts": 0,
    "false_rejects": 0
  },
  "candidate_only_invalid_key_cases": 10,
  "fixture_group_counts": {
    "unique": 1,
    "order_alias": 4,
    "candidate_duplicate": 1,
    "oracle_duplicate": 1,
    "shared_duplicate": 2,
    "status_in_key": 1,
    "coverage": 7,
    "scalar": 3,
    "npz": 5,
    "metadata": 2,
    "counts": 1,
    "alias_duplicate": 2
  },
  "boundary": {
    "actual_public_api": true,
    "only_changed_function": "_compare_condition_coverage",
    "other_top_level_nodes_preserved": 17,
    "simulation_or_runner_entrypoints_called": false,
    "proposal_installed": false
  },
  "public_sources_unchanged": 12,
  "elapsed_seconds": 3.6619492519999994
}
```


### Mutation controls — actual normal-mode record (`-O` matches without timings)

```json
{
  "mode": "mutants",
  "optimized_python": false,
  "detected": 8,
  "records": [
    {
      "mutant": "legacy_set_collapse",
      "detected": true,
      "reason": "verdict",
      "expected": false,
      "observed": true,
      "precall_rows": {
        "candidate_rows": [
          [
            "s0",
            "0.5",
            "success"
          ],
          [
            "s1",
            "1",
            "success"
          ],
          [
            "s0",
            "0.5",
            "success"
          ]
        ],
        "oracle_rows": [
          [
            "s0",
            "0.5",
            "success"
          ],
          [
            "s1",
            "1",
            "success"
          ]
        ]
      }
    },
    {
      "mutant": "count_plus_set_only",
      "detected": true,
      "reason": "verdict",
      "expected": false,
      "observed": true,
      "precall_rows": {
        "candidate_rows": [
          [
            "s0",
            "0.5",
            "success"
          ],
          [
            "s1",
            "1",
            "success"
          ],
          [
            "s0",
            "0.5",
            "success"
          ]
        ],
        "oracle_rows": [
          [
            "s0",
            "0.5",
            "success"
          ],
          [
            "s1",
            "1",
            "success"
          ],
          [
            "s0",
            "0.5",
            "success"
          ]
        ]
      }
    },
    {
      "mutant": "status_in_identity",
      "detected": true,
      "reason": "verdict",
      "expected": false,
      "observed": true,
      "precall_rows": {
        "candidate_rows": [
          [
            "s0",
            "0.5",
            "success"
          ],
          [
            "s0",
            "0.5",
            "failed"
          ],
          [
            "s1",
            "1",
            "success"
          ]
        ],
        "oracle_rows": [
          [
            "s0",
            "0.5",
            "success"
          ],
          [
            "s0",
            "0.5",
            "failed"
          ],
          [
            "s1",
            "1",
            "success"
          ]
        ]
      }
    },
    {
      "mutant": "require_condition_row_order",
      "detected": true,
      "reason": "verdict",
      "expected": true,
      "observed": false,
      "precall_rows": {
        "candidate_rows": [
          [
            "s1",
            "1",
            "success"
          ],
          [
            "s0",
            "0.5",
            "success"
          ]
        ],
        "oracle_rows": [
          [
            "s0",
            "0.5",
            "success"
          ],
          [
            "s1",
            "1",
            "success"
          ]
        ]
      }
    },
    {
      "mutant": "raw_rho_text_keys",
      "detected": true,
      "reason": "verdict",
      "expected": true,
      "observed": false,
      "precall_rows": {
        "candidate_rows": [
          [
            "s0",
            "5e-1",
            "success"
          ],
          [
            "s1",
            "1",
            "success"
          ]
        ],
        "oracle_rows": [
          [
            "s0",
            "0.5",
            "success"
          ],
          [
            "s1",
            "1",
            "success"
          ]
        ]
      }
    },
    {
      "mutant": "ignore_status",
      "detected": true,
      "reason": "verdict",
      "expected": false,
      "observed": true,
      "precall_rows": {
        "candidate_rows": [
          [
            "s0",
            "0.5",
            "failed"
          ],
          [
            "s1",
            "1",
            "success"
          ]
        ],
        "oracle_rows": [
          [
            "s0",
            "0.5",
            "success"
          ],
          [
            "s1",
            "1",
            "success"
          ]
        ]
      }
    },
    {
      "mutant": "bypass_existing_npz_gate",
      "detected": true,
      "reason": "verdict",
      "expected": false,
      "observed": true,
      "precall_rows": {
        "candidate_rows": [
          [
            "s0",
            "0.5",
            "success"
          ],
          [
            "s1",
            "1",
            "success"
          ]
        ],
        "oracle_rows": [
          [
            "s0",
            "0.5",
            "success"
          ],
          [
            "s1",
            "1",
            "success"
          ]
        ]
      }
    },
    {
      "mutant": "rewrite_requested_input",
      "detected": true,
      "reason": "input_preservation",
      "expected": "all six files unchanged",
      "observed": "modified",
      "precall_rows": {
        "candidate_rows": [
          [
            "s0",
            "0.5",
            "success"
          ],
          [
            "s1",
            "1",
            "success"
          ],
          [
            "s0",
            "0.5",
            "success"
          ]
        ],
        "oracle_rows": [
          [
            "s0",
            "0.5",
            "success"
          ],
          [
            "s1",
            "1",
            "success"
          ]
        ]
      }
    }
  ],
  "setup_errors_credited": 0,
  "public_sources_unchanged": 12,
  "elapsed_seconds": 0.055332900999928825
}
```


## 6. Reproduce from just this note

Requires Python3.10+ and available NumPy. No package installation occurred here.
Save the eight marked critical blocks below under their displayed filenames in
one directory. The extractor itself is included; bootstrap-save it first, then:

```sh
python -B extract_from_report.py 2026-09-04_researcher040282_008_oracle-condition-uniqueness.md extracted
python -B extracted/fetch_public_dependencies.py --output upstream
python -B extracted/run_checks.py --source upstream --output checks
```

The fetcher retrieves12 reviewed public Python dependencies, verifies source
identity/length and requests no raw author/committer records; it executes none.
Use a fresh upstream directory for a fresh fetch (existing matching files are
reused). The runner imports reviewed code: this is not arbitrary-code security.
No real data/engine simulation or authority validation runs. Expected parent exit0;
inside it, original workers exit1 for exactly5 failures/0errors, candidate12pass and
8 mutants are required in each interpreter mode. A setup exception blocks success.

**Actually executed.** Eight critical files were extracted byte-for-byte; 12 public package sources were freshly fetched and verified. The extracted runner returned0 after repeating all actual-public-API original/candidate normal/-O contracts, both1600-pair censuses, candidate-only key checks and both mutant modes. Science, all six worker non-timing records and all14 detailed census/key files match the original run. This is submitter-local self-reproduction, not independent-seat confirmation.

```json
{
  "actually_executed": true,
  "runner_returncode": 0,
  "tested_main": "eb3933c196ee19e80e1621ae80d89ca72e6d9485",
  "critical_file_count": 8,
  "critical_files": [
    "oracle_candidate.py",
    "status_contract.py",
    "load_reviewed.py",
    "test_status_contract.py",
    "run_checks.py",
    "source_modules.json",
    "fetch_public_dependencies.py",
    "extract_from_report.py"
  ],
  "all_extracted_files_byte_identical": true,
  "fresh_public_source_files_fetched_and_verified": 12,
  "scientific_summary_matches_original": true,
  "all_six_worker_nontiming_results_match_original": true,
  "all_fourteen_detailed_census_and_invalid_key_files_byte_identical": true,
  "detailed_matching_files": [
    "baseline_normal/table_census.json",
    "baseline_optimized/table_census.json",
    "candidate_normal/table_census.json",
    "candidate_optimized/table_census.json",
    "baseline_normal/census_mismatches.json",
    "baseline_optimized/census_mismatches.json",
    "candidate_normal/census_mismatches.json",
    "candidate_optimized/census_mismatches.json",
    "baseline_normal/sequence_definitions.json",
    "baseline_optimized/sequence_definitions.json",
    "candidate_normal/sequence_definitions.json",
    "candidate_optimized/sequence_definitions.json",
    "candidate_normal/invalid_key_results.json",
    "candidate_optimized/invalid_key_results.json"
  ],
  "commands_observed": [
    {
      "program": "proposal/extract_from_report.py",
      "returncode": 0
    },
    {
      "program": "standalone/extracted/fetch_public_dependencies.py",
      "returncode": 0
    },
    {
      "program": "standalone/extracted/run_checks.py",
      "returncode": 0
    }
  ],
  "original_failures_each_mode": [
    5,
    5
  ],
  "original_errors_each_mode": [
    0,
    0
  ],
  "candidate_passes_each_mode": [
    12,
    12
  ],
  "original_census_false_accepts_each_mode": [
    244,
    244
  ],
  "candidate_census_mismatches_each_mode": [
    0,
    0
  ],
  "candidate_only_invalid_key_cases_each_mode": [
    10,
    10
  ],
  "mutants_detected_each_mode": [
    8,
    8
  ],
  "original_elapsed_seconds": 16.538016760999994,
  "extracted_elapsed_seconds": 15.685279412,
  "command": "python -B standalone/extracted/run_checks.py --source standalone/upstream --output standalone/checks",
  "result": "cycle_008/standalone/checks/cycle_results.json",
  "log": "cycle_008/standalone/reproduction.log",
  "scope": "Submitter-local exact-note actual-public-API reproduction, not independent-seat approval, installed repair, real S01/201-vs200 or authority/whole-study certificate"
}
```


## 7. Complete inline critical code and dependency manifest

The complete separate candidate is included, not just a diff requiring private
workspace access. The other public sources come from the manifest/fetcher. Same
bytes are compared between inline files, proposal and actually executed extraction.

### oracle_candidate.py

<!-- BEGIN_CRITICAL_FILE: oracle_candidate.py -->
```python
"""Logical-content comparison against the successful T_window production oracle."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from .validation import ArtifactIntegrityError, exact_equal_with_nan, exact_scalar_equal_with_nan


@dataclass(frozen=True)
class OracleComparison:
    status: str
    scalar_rows: int
    npz_entries: int
    condition_rows: int
    errors: tuple[str, ...]


def _read_csv(path: Path) -> tuple[tuple[str, ...], list[dict[str, str]]]:
    with open(path, "r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ArtifactIntegrityError(f"CSV has no header: {path}")
        return tuple(reader.fieldnames), list(reader)


def _is_numeric_text(value: str) -> bool:
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False


def _compare_scalar_csv(candidate: Path, oracle: Path, errors: list[str]) -> int:
    candidate_fields, candidate_rows = _read_csv(candidate)
    oracle_fields, oracle_rows = _read_csv(oracle)
    if candidate_fields != oracle_fields:
        errors.append(
            f"Scalar CSV columns/order differ: candidate={candidate_fields!r}, oracle={oracle_fields!r}"
        )
        return len(candidate_rows)
    if len(candidate_rows) != len(oracle_rows):
        errors.append(
            f"Scalar CSV row count differs: candidate={len(candidate_rows)}, oracle={len(oracle_rows)}"
        )
        return len(candidate_rows)

    text_fields = {"seed_index", "seed", "branch"}
    for index, (left, right) in enumerate(zip(candidate_rows, oracle_rows, strict=True)):
        for field in candidate_fields:
            a = left[field]
            b = right[field]
            if field in text_fields:
                if a != b:
                    errors.append(f"Scalar row {index} field {field}: {a!r} != {b!r}")
            elif not exact_scalar_equal_with_nan(a, b):
                errors.append(f"Scalar row {index} field {field}: {a!r} != {b!r}")
            if len(errors) >= 100:
                return len(candidate_rows)
    return len(candidate_rows)


def _load_npz(path: Path) -> dict[str, np.ndarray]:
    try:
        with np.load(path, allow_pickle=False) as archive:
            return {key: archive[key].copy() for key in archive.files}
    except Exception as exc:
        raise ArtifactIntegrityError(f"Cannot load NPZ {path}: {exc}") from exc


def _compare_npz(candidate: Path, oracle: Path, errors: list[str]) -> int:
    left = _load_npz(candidate)
    right = _load_npz(oracle)
    if set(left) != set(right):
        missing = sorted(set(right) - set(left))
        extra = sorted(set(left) - set(right))
        errors.append(f"NPZ key mismatch: missing={missing[:20]}, extra={extra[:20]}")
    for key in sorted(set(left) & set(right)):
        if not exact_equal_with_nan(left[key], right[key]):
            errors.append(
                f"NPZ value mismatch for {key}: "
                f"candidate(shape={left[key].shape},dtype={left[key].dtype}), "
                f"oracle(shape={right[key].shape},dtype={right[key].dtype})"
            )
            if len(errors) >= 100:
                break
    return len(left)


def _compare_condition_coverage(candidate: Path, oracle: Path, errors: list[str]) -> int:
    """Compare one record per normalized condition key, never a lossy multiset."""
    from collections import Counter

    left_fields, left_rows = _read_csv(candidate)
    right_fields, right_rows = _read_csv(oracle)
    required = {"seed", "rho", "status"}
    if not required.issubset(left_fields) or not required.issubset(right_fields):
        errors.append("Condition status files lack seed/rho/status columns")
        return len(left_rows)
    if len(left_rows) != len(right_rows):
        errors.append(
            f"Condition status row count differs: candidate={len(left_rows)}, oracle={len(right_rows)}"
        )

    tables = []
    for label, rows in (("candidate", left_rows), ("oracle", right_rows)):
        counts = Counter()
        values = set()
        for index, row in enumerate(rows):
            try:
                rho = float(row["rho"])
            except (TypeError, ValueError):
                errors.append(f"Condition status invalid finite rho in {label} row {index}")
                continue
            if not math.isfinite(rho):
                errors.append(f"Condition status invalid finite rho in {label} row {index}")
                continue
            if not isinstance(row["seed"], str) or not isinstance(row["status"], str):
                errors.append(f"Condition status invalid seed/status text in {label} row {index}")
                continue
            key = (row["seed"], rho)
            counts[key] += 1
            values.add((row["seed"], rho, row["status"]))
        duplicates = sorted((key, count) for key, count in counts.items() if count > 1)
        if duplicates:
            errors.append(f"Condition status duplicate (seed,rho) keys in {label}: {duplicates[:10]}")
        tables.append(values)
    left_keys, right_keys = tables
    if left_keys != right_keys:
        errors.append(
            f"Condition status coverage differs: missing={sorted(right_keys-left_keys)[:10]}, "
            f"extra={sorted(left_keys-right_keys)[:10]}"
        )
    return len(left_rows)


def _single_file(directory: Path, pattern: str) -> Path:
    files = sorted(directory.glob(pattern))
    if len(files) != 1:
        raise ArtifactIntegrityError(
            f"Expected exactly one {pattern!r} in {directory}, found {[item.name for item in files]}"
        )
    return files[0]


def compare_twindow_run(candidate_dir: str | Path, oracle_dir: str | Path) -> OracleComparison:
    """Compare decompressed logical contents, never compressed NPZ bytes."""
    candidate = Path(candidate_dir)
    oracle = Path(oracle_dir)
    errors: list[str] = []
    candidate_csv = _single_file(candidate, "AIEF_1_4_Twindow_sensitivity_*_scalar_summary.csv")
    oracle_csv = _single_file(oracle, "AIEF_1_4_Twindow_sensitivity_*_scalar_summary.csv")
    candidate_npz = _single_file(candidate, "AIEF_1_4_Twindow_sensitivity_*_branch_diagnostics.npz")
    oracle_npz = _single_file(oracle, "AIEF_1_4_Twindow_sensitivity_*_branch_diagnostics.npz")
    scalar_rows = _compare_scalar_csv(candidate_csv, oracle_csv, errors)
    npz_entries = _compare_npz(candidate_npz, oracle_npz, errors)
    condition_rows = _compare_condition_coverage(
        candidate / "twindow_condition_status.csv",
        oracle / "twindow_condition_status.csv",
        errors,
    )
    return OracleComparison(
        status="passed" if not errors else "failed",
        scalar_rows=scalar_rows,
        npz_entries=npz_entries,
        condition_rows=condition_rows,
        errors=tuple(errors),
    )
```
<!-- END_CRITICAL_FILE: oracle_candidate.py -->

### status_contract.py

<!-- BEGIN_CRITICAL_FILE: status_contract.py -->
```python
"""Independent pairwise condition contract and small public-API toy bundles.
All expected rows are immutable and expected truth/file snapshots precede calls.
"""
import csv
from dataclasses import dataclass
import itertools
import math
from pathlib import Path
import tempfile
import numpy as np

FIELDS = ('seed','rho','status','elapsed_seconds')
A = ('s0','0.5','success')
B = ('s1','1','success')
C = ('s0','0.5','failed')
BASE = (A,B)
SIX = tuple((f's{i}',rho,'success') for i in range(3) for rho in ('0.5','1'))
SCALAR_FIELDS = ('seed_index','seed','rho','branch','metric')
SCALAR_ROWS = (('0','s0','0.5','continue','0.25'),('1','s1','1','reset_ema','0.75'))


class ContractMismatch(RuntimeError):
    def __init__(self, rule, name, expected, observed):
        self.rule,self.case,self.expected,self.observed = rule,name,expected,observed
        super().__init__(f'{rule}: {name}; expected={expected!r}, observed={observed!r}')


@dataclass(frozen=True)
class Scenario:
    name: str
    group: str
    left: tuple = BASE
    right: tuple = BASE
    left_fields: tuple = FIELDS
    right_fields: tuple = FIELDS
    scalar_variant: str = 'same'
    npz_variant: str = 'same'
    auxiliary_difference: bool = False


def condition_expected(left, right, left_fields=FIELDS, right_fields=FIELDS):
    for fields in (left_fields,right_fields):
        if not all(name in fields for name in ('seed','rho','status')):
            return False
    if len(left) !=len(right):
        return False
    normalized = []
    for rows in (left,right):
        current = []
        for seed,text,status in rows:
            try:
                rho = float(text)
            except (TypeError,ValueError):
                return False
            if not math.isfinite(rho):
                return False
            key = (seed,rho)
            if any(key ==earlier[0] for earlier in current):
                return False
            current.append((key,status))
        normalized.append(current)
    for key,status in normalized[0]:
        if not any(key ==other_key and status ==other_status for other_key,other_status in normalized[1]):
            return False
    return True


def expected(case):
    return (condition_expected(case.left,case.right,case.left_fields,case.right_fields) and
            case.scalar_variant =='same' and case.npz_variant =='same')


def write_status(path, rows, fields=FIELDS, alternate_metadata=False):
    with Path(path).open('w',newline='') as stream:
        writer = csv.DictWriter(stream,fieldnames=fields,extrasaction='ignore')
        writer.writeheader()
        for seed,rho,status in rows:
            writer.writerow({'seed':seed,'rho':rho,'status':status,
                             'elapsed_seconds':'999' if alternate_metadata else '0.01',
                             'error':'different auxiliary metadata' if alternate_metadata else ''})


class Bundle:
    def __init__(self, parent=None):
        self.temp = tempfile.TemporaryDirectory(prefix='r040282_008_',dir=parent)
        self.root = Path(self.temp.name)
        self.left,self.right = self.root/'candidate',self.root/'oracle'
        self.left.mkdir();self.right.mkdir()

    def close(self):
        self.temp.cleanup()

    def prepare(self, case):
        for directory,is_left,rows,fields in ((self.left,True,case.left,case.left_fields),
                                              (self.right,False,case.right,case.right_fields)):
            scalar_rows = [dict(zip(SCALAR_FIELDS,row)) for row in SCALAR_ROWS]
            scalar_fields = list(SCALAR_FIELDS)
            if is_left:
                if case.scalar_variant =='value':scalar_rows[0]['metric']='0.250001'
                elif case.scalar_variant =='branch':scalar_rows[0]['branch']='wrong_branch'
                elif case.scalar_variant =='columns':scalar_fields=scalar_fields[::-1]
                elif case.scalar_variant !='same':raise ValueError('Unknown scalar fixture')
            path = directory/'AIEF_1_4_Twindow_sensitivity_SYNTHETIC_scalar_summary.csv'
            with path.open('w',newline='') as stream:
                writer=csv.DictWriter(stream,fieldnames=scalar_fields);writer.writeheader();writer.writerows(scalar_rows)
            payload={'weights':np.array([[.2,.3],[.4,.6]],dtype=np.float64),
                     'partial_complex':np.array([complex(math.nan,1),complex(2,3)],dtype=np.complex128)}
            if is_left:
                if case.npz_variant =='value':payload['weights'][0,1]=np.nextafter(payload['weights'][0,1],math.inf)
                elif case.npz_variant =='dtype':payload['weights']=payload['weights'].astype(np.float32)
                elif case.npz_variant =='shape':payload['weights']=payload['weights'].reshape(4)
                elif case.npz_variant =='key':payload['wrong_key']=payload.pop('weights')
                elif case.npz_variant =='nan_component':payload['partial_complex'][0]=complex(math.nan,99)
                elif case.npz_variant !='same':raise ValueError('Unknown NPZ fixture')
            np.savez(directory/'AIEF_1_4_Twindow_sensitivity_SYNTHETIC_branch_diagnostics.npz',**payload)
            write_status(directory/'twindow_condition_status.csv',rows,fields,
                         is_left and case.auxiliary_difference)

    def snapshot(self):
        return {str(p.relative_to(self.root)):p.read_bytes() for p in sorted(self.root.rglob('*')) if p.is_file()}


def checked(api, bundle, case):
    answer_expected = expected(case)  # From original immutable rows, before I/O/target.
    bundle.prepare(case)
    before = bundle.snapshot()
    result = api(bundle.left,bundle.right)
    if before !=bundle.snapshot():
        raise ContractMismatch('input_preservation',case.name,'all six files unchanged','modified')
    counts = (result.scalar_rows,result.npz_entries,result.condition_rows)
    wanted = (len(SCALAR_ROWS),2,len(case.left))
    if counts !=wanted:
        raise ContractMismatch('counts',case.name,wanted,counts)
    if result.status not in ('passed','failed') or bool(result.errors) !=(result.status =='failed'):
        raise ContractMismatch('status_errors',case.name,'consistent status/errors',(result.status,result.errors))
    answer = result.status =='passed'
    if answer !=answer_expected:
        raise ContractMismatch('verdict',case.name,answer_expected,answer)
    return {'status':result.status,'condition_rows':result.condition_rows,'errors':list(result.errors)}


def cases():
    return [
        Scenario('six_unique_conditions','unique',SIX,SIX),
        Scenario('reordered','order_alias',BASE[::-1],BASE),
        Scenario('rho_aliases','order_alias',(('s0','5e-1','success'),('s1','1.00','success')),BASE),
        Scenario('condition_header_order','order_alias',left_fields=('status','rho','seed','elapsed_seconds')),
        Scenario('signed_zero_key_policy','order_alias',(('s0','-0.0','success'),B),(('s0','0.0','success'),B)),
        Scenario('candidate_duplicate3v2','candidate_duplicate',BASE+(A,),BASE),
        Scenario('oracle_duplicate2v3','oracle_duplicate',BASE,BASE+(A,)),
        Scenario('shared_duplicate3v3','shared_duplicate',BASE+(A,),BASE+(A,)),
        Scenario('shared_duplicate_permuted','shared_duplicate',(A,A,B),(B,A,A)),
        Scenario('status_is_not_condition_identity','status_in_key',(A,C,B),(B,A,C)),
        Scenario('missing_condition','coverage',BASE[:1],BASE),
        Scenario('changed_seed','coverage',(('s2','0.5','success'),B),BASE),
        Scenario('changed_rho','coverage',(('s0','0.75','success'),B),BASE),
        Scenario('changed_status','coverage',(C,B),BASE),
        Scenario('duplicate_replaces_other_key','coverage',(A,A),BASE),
        Scenario('required_status_column_missing','coverage',left_fields=('seed','rho','elapsed_seconds')),
        Scenario('numeric_seed_text_distinction','coverage',(('01','0.5','success'),B),(('1','0.5','success'),B)),
        *[Scenario('scalar_'+kind,'scalar',scalar_variant=kind) for kind in ('value','branch','columns')],
        *[Scenario('npz_'+kind,'npz',npz_variant=kind) for kind in ('value','dtype','shape','key','nan_component')],
        Scenario('aux_metadata_ignored','metadata',right_fields=FIELDS+('error',),auxiliary_difference=True),
        Scenario('logical_empty_not_a_study_certificate','metadata',(),()),
        Scenario('counts_and_file_preservation','counts',SIX,SIX),
        Scenario('normalized_duplicate3v2','alias_duplicate',(A,('s0','5e-1','success'),B),BASE),
        Scenario('normalized_duplicates_both','alias_duplicate',(A,('s0','5e-1','success'),B),
                 (('s0','.50','success'),A,B)),
    ]


def groups():
    return ('unique','order_alias','candidate_duplicate','oracle_duplicate','shared_duplicate',
            'status_in_key','coverage','scalar','npz','metadata','counts','alias_duplicate')


def sequences():
    return tuple(rows for length in range(4) for rows in itertools.product((A,B,C),repeat=length))


def invalid_rho_cases():
    out=[]
    for bad in ('NaN','Inf','-Inf','not-numeric',''):
        rows=(('s0',bad,'success'),B)
        out.append(Scenario('invalid_candidate_rho_'+repr(bad),'candidate_only',rows,BASE))
        out.append(Scenario('invalid_oracle_rho_'+repr(bad),'candidate_only',BASE,rows))
    return out
```
<!-- END_CRITICAL_FILE: status_contract.py -->

### load_reviewed.py

<!-- BEGIN_CRITICAL_FILE: load_reviewed.py -->
```python
"""Verified actual package/public-API loads, no AST-extracted or mocked oracle.
Never run simulations/baseline/authority gates. Not arbitrary-code intake security.
"""
import ast
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent


def verify(source):
    source=Path(source).resolve()
    manifest=json.loads((HERE/'source_modules.json').read_text())
    for row in manifest['modules']:
        data=(source/row['path']).read_bytes()
        actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if actual!=row['blob'] or len(data)!=row['bytes']:
            raise RuntimeError('Reviewed public dependency differs: '+row['path'])
    return manifest


def load(source, mode):
    source=Path(source).resolve();manifest=verify(source)
    sys.path.insert(0,str(source/manifest['platform']))
    original=importlib.import_module('aief_modular.oracle')
    if Path(original.__file__).resolve()!=source/manifest['oracle']:
        raise RuntimeError('Wrong public package source imported')
    if mode=='baseline':
        return original,{'actual_public_api':True,'simulation_or_runner_entrypoints_called':False}
    if mode!='candidate':raise ValueError('Unknown controlled mode')
    before=ast.parse((source/manifest['oracle']).read_text())
    path=HERE/'oracle_candidate.py';after=ast.parse(path.read_text())
    name='_compare_condition_coverage'
    def unchanged(tree):
        return [ast.dump(n,include_attributes=False) for n in tree.body if not(isinstance(n,ast.FunctionDef) and n.name==name)]
    for tree in (before,after):
        if sum(isinstance(n,ast.FunctionDef) and n.name==name for n in tree.body)!=1:
            raise RuntimeError('Missing/duplicate proposal function')
    if unchanged(before)!=unchanged(after):raise RuntimeError('Proposal altered another public-API gate')
    spec=importlib.util.spec_from_file_location('aief_modular._r040282_oracle_candidate',path)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    verify(source)
    return module,{'actual_public_api':True,'only_changed_function':name,
                   'other_top_level_nodes_preserved':len(unchanged(before)),
                   'simulation_or_runner_entrypoints_called':False,'proposal_installed':False}
```
<!-- END_CRITICAL_FILE: load_reviewed.py -->

### test_status_contract.py

<!-- BEGIN_CRITICAL_FILE: test_status_contract.py -->
```python
"""Same twelve public API contracts on original and candidate, also with -O."""
import unittest
from status_contract import cases,groups,checked,ContractMismatch


def suite(api,bundle):
    class PublicOracleContract(unittest.TestCase):
        pass
    def method(group):
        def test(self):
            selected=[case for case in cases() if case.group==group]
            self.assertTrue(selected,'Missing nonvacuity fixture')
            violations=[]
            for case in selected:
                try:checked(api,bundle,case)
                except ContractMismatch as e:violations.append(str(e))
            self.assertEqual(len(violations),0,str(len(violations))+' mismatches; first3='+repr(violations[:3]))
        return test
    for group in groups():setattr(PublicOracleContract,'test_'+group,method(group))
    return unittest.defaultTestLoader.loadTestsFromTestCase(PublicOracleContract)
```
<!-- END_CRITICAL_FILE: test_status_contract.py -->

### run_checks.py

<!-- BEGIN_CRITICAL_FILE: run_checks.py -->
```python
"""Preregistered actual-public-API008 red/green, finite census and mutants.
No simulation, real oracle run, source installation or authority mutation.
"""
import argparse
from collections import Counter
import csv
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import unittest
import numpy as np

from load_reviewed import load,verify
from status_contract import (A,B,C,BASE,Bundle,Scenario,ContractMismatch,cases,checked,
                             condition_expected,invalid_rho_cases,sequences)
from test_status_contract import suite

MODES=('baseline','candidate','mutants')
RED={'test_candidate_duplicate','test_oracle_duplicate','test_shared_duplicate','test_status_in_key','test_alias_duplicate'}


def require(condition,message):
    if not condition:raise RuntimeError(message)


def save(path,value):
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')


def census(api,bundle):
    seq=sequences();records=[];bad=[]
    for i,left in enumerate(seq):
        for j,right in enumerate(seq):
            case=Scenario(f'census_{i}_{j}','census',left,right)
            predicted=condition_expected(left,right)
            try:
                result=checked(api,bundle,case)
                observed=result['status']=='passed'
            except ContractMismatch as error:
                require(error.rule=='verdict','Unexpected nonverdict census violation: '+str(error))
                observed=error.observed
            row={'candidate_sequence':i,'oracle_sequence':j,'expected':predicted,'observed':observed}
            records.append(row)
            if predicted!=observed:bad.append(row)
    summary={'ordered_table_pairs':len(records),'expected_passes':sum(r['expected'] for r in records),
             'observed_passes':sum(r['observed'] for r in records),'mismatches':len(bad),
             'false_accepts':sum(not r['expected'] and r['observed'] for r in bad),
             'false_rejects':sum(r['expected'] and not r['observed'] for r in bad)}
    return summary,records,bad,seq


def mutant_worker(source,bundle):
    original,_=load(source,'baseline');candidate,_=load(source,'candidate')
    fixed=candidate._compare_condition_coverage
    npz_fixed=candidate._compare_npz
    def rows(a,b):
        return candidate._read_csv(a)[1],candidate._read_csv(b)[1]
    def triples(items,raw=False,no_status=False):
        return [(r['seed'],r['rho'] if raw else float(r['rho']))+
                (() if no_status else (r['status'],)) for r in items]
    def count_set(a,b,errors):
        left,right=rows(a,b)
        if len(left)!=len(right):errors.append('mutant row count')
        if set(triples(left))!=set(triples(right)):errors.append('mutant coverage')
        return len(left)
    def triple_identity(a,b,errors):
        left,right=rows(a,b);l,r=triples(left),triples(right)
        if len(left)!=len(right) or len(set(l))!=len(l) or len(set(r))!=len(r):errors.append('mutant triple duplicates/count')
        if set(l)!=set(r):errors.append('mutant coverage')
        return len(left)
    def order_sensitive(a,b,errors):
        count=fixed(a,b,errors);left,right=rows(a,b)
        if triples(left)!=triples(right):errors.append('mutant condition order')
        return count
    def raw_rho(a,b,errors):
        left,right=rows(a,b)
        if set(triples(left,raw=True))!=set(triples(right,raw=True)):errors.append('mutant rho text')
        return len(left)
    def ignore_status(a,b,errors):
        left,right=rows(a,b);l,r=triples(left,no_status=True),triples(right,no_status=True)
        if len(l)!=len(r) or len(set(l))!=len(l) or len(set(r))!=len(r) or set(l)!=set(r):errors.append('mutant key coverage')
        return len(left)
    def bypass_npz(a,b,errors):
        return len(candidate._load_npz(a))
    def deduplicate_input(a,b):
        path=Path(a)/'twindow_condition_status.csv'
        fields,items=candidate._read_csv(path);seen=[];kept=[]
        for row in items:
            key=(row['seed'],float(row['rho']))
            if key not in seen:seen.append(key);kept.append(row)
        with path.open('w',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(kept)
        return candidate.compare_twindow_run(a,b)
    controls=[
        ('legacy_set_collapse','baseline',None,Scenario('duplicate_append','mutant',BASE+(A,),BASE),'verdict'),
        ('count_plus_set_only','condition',count_set,Scenario('equal_count_shared_duplicate','mutant',BASE+(A,),BASE+(A,)),'verdict'),
        ('status_in_identity','condition',triple_identity,Scenario('conflicting_status_same_key','mutant',(A,C,B),(A,C,B)),'verdict'),
        ('require_condition_row_order','condition',order_sensitive,Scenario('valid_reordering','mutant',BASE[::-1],BASE),'verdict'),
        ('raw_rho_text_keys','condition',raw_rho,Scenario('valid_numeric_alias','mutant',(('s0','5e-1','success'),B),BASE),'verdict'),
        ('ignore_status','condition',ignore_status,Scenario('changed_status','mutant',(C,B),BASE),'verdict'),
        ('bypass_existing_npz_gate','npz',bypass_npz,Scenario('changed_npz_value','mutant',npz_variant='value'),'verdict'),
        ('rewrite_requested_input','rewrite',deduplicate_input,Scenario('deduplicate_before_answer','mutant',BASE+(A,),BASE),'input_preservation'),
    ]
    results=[]
    for name,kind,fn,case,rule in controls:
        candidate._compare_condition_coverage=fixed;candidate._compare_npz=npz_fixed
        if kind=='baseline':api=original.compare_twindow_run
        elif kind=='rewrite':api=fn
        else:
            if kind=='condition':candidate._compare_condition_coverage=fn
            else:candidate._compare_npz=fn
            api=candidate.compare_twindow_run
        before={'candidate_rows':case.left,'oracle_rows':case.right}
        try:
            try:checked(api,bundle,case)
            except ContractMismatch as error:
                require(error.rule==rule,'Wrong mechanism for '+name)
                results.append({'mutant':name,'detected':True,'reason':rule,'expected':error.expected,
                                'observed':error.observed,'precall_rows':before})
            else:raise RuntimeError('Undetected mutant: '+name)
        finally:
            candidate._compare_condition_coverage=fixed;candidate._compare_npz=npz_fixed
    require(len(results)==8,'Mutant inventory incomplete')
    return results


def child(args):
    args.output.mkdir(parents=True,exist_ok=True);start=time.perf_counter();bundle=Bundle(args.output)
    try:
        if args.child=='mutants':
            records=mutant_worker(args.source,bundle)
            value={'mode':'mutants','optimized_python':not __debug__,'detected':len(records),'records':records,
                   'setup_errors_credited':0,'public_sources_unchanged':len(verify(args.source)['modules']),
                   'elapsed_seconds':time.perf_counter()-start}
            save(args.output/'result.json',value);print(json.dumps(value,indent=2));return 0
        module,boundary=load(args.source,args.child);api=module.compare_twindow_run
        stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite(api,bundle))
        print(stream.getvalue(),end='')
        summary,records,bad,seq=census(api,bundle)
        save(args.output/'table_census.json',records);save(args.output/'census_mismatches.json',bad)
        save(args.output/'sequence_definitions.json',seq)
        advanced=[]
        if args.child=='candidate':
            for case in invalid_rho_cases():
                report=checked(api,bundle,case)
                require(any('invalid finite rho' in item for item in report['errors']), 'Invalid key lacks explicit failure')
                advanced.append({'case':case.name,'status':report['status'],'errors':report['errors']})
            save(args.output/'invalid_key_results.json',advanced)
        value={'mode':args.child,'optimized_python':not __debug__,'tests_run':result.testsRun,
               'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),
               'failure_methods':sorted(test.id().split('.')[-1] for test,_ in result.failures),
               'error_methods':sorted(test.id().split('.')[-1] for test,_ in result.errors),
               'census':summary,'candidate_only_invalid_key_cases':len(advanced),
               'fixture_group_counts':dict(Counter(case.group for case in cases())),
               'boundary':boundary,'public_sources_unchanged':len(verify(args.source)['modules']),
               'elapsed_seconds':time.perf_counter()-start}
        save(args.output/'result.json',value);print(json.dumps(value,indent=2))
        return 0 if result.wasSuccessful() else 1
    finally:bundle.close()


def parent(args):
    args.output.mkdir(parents=True,exist_ok=True);start=time.perf_counter();manifest=verify(args.source)
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONOPTIMIZE',None);runs=[]
    for mode in MODES:
        for opt in (False,True):
            name=mode+('_optimized' if opt else '_normal');directory=args.output/name
            command=[sys.executable]+(['-O'] if opt else [])+['-B',str(Path(__file__).resolve()),'--child',mode,
                     '--source',str(args.source.resolve()),'--output',str(directory.resolve())]
            run=subprocess.run(command,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=env,timeout=90)
            (args.output/(name+'.log')).write_text(run.stdout)
            require((directory/'result.json').is_file(),'Child failed before results: '+name)
            value=json.loads((directory/'result.json').read_text())
            require(value['optimized_python'] is opt and value['public_sources_unchanged']==12,'Source/optimization mismatch')
            if mode=='baseline':
                require(run.returncode==1 and value['tests_run']==12 and value['failures']==5 and
                        value['errors']==0 and value['skipped']==0 and set(value['failure_methods'])==RED,
                        'Original did not fail exactly the intended contracts; stop/reassess')
                require(value['census']=={'ordered_table_pairs':1600,'expected_passes':12,'observed_passes':256,
                                         'mismatches':244,'false_accepts':244,'false_rejects':0},'Original census differs from protocol')
            elif mode=='candidate':
                require(run.returncode==0 and value['tests_run']==12 and value['failures']==value['errors']==value['skipped']==0 and
                        value['census']=={'ordered_table_pairs':1600,'expected_passes':12,'observed_passes':12,
                                         'mismatches':0,'false_accepts':0,'false_rejects':0} and
                        value['candidate_only_invalid_key_cases']==10,'Candidate acceptance incomplete')
            else:
                require(run.returncode==0 and value['detected']==8 and value['setup_errors_credited']==0,'Mutant controls incomplete')
            value['observed_returncode']=run.returncode;runs.append(value)
            print(name,'return',run.returncode,'science verified',flush=True)
    for mode in MODES:
        a,b=[row for row in runs if row['mode']==mode]
        omit={'optimized_python','elapsed_seconds'}
        require({k:v for k,v in a.items() if k not in omit}=={k:v for k,v in b.items() if k not in omit},
                'Normal/optimized mismatch: '+mode)
    save(args.output/'worker_results.json',runs)
    science={'tested_main':manifest['commit'],'common_contract_methods':12,
             'original_expected_failures_each_mode':5,'original_errors_each_mode':0,
             'candidate_passes_each_mode':12,'public_api_table_pairs_each_target':1600,
             'independent_expected_accepts':12,'original_accepted':256,'original_false_accepts':244,
             'original_false_rejects':0,'candidate_accepted':12,'candidate_mismatches':0,
             'candidate_only_invalid_key_cases_each_mode':10,'mutants_detected_each_mode':8,
             'all_workers_nontiming_results_equal_under_optimization':True,
             'reviewed_public_source_files_unchanged':len(verify(args.source)['modules']),
             'no_simulation_real_data_or_new_lean':True,'proposal_not_installed_no_remote_changes':True,
             'all_preregistered_acceptance_conditions_met':True}
    record={'science':science,'python':sys.version,'numpy':np.__version__,
            'elapsed_seconds':time.perf_counter()-start,
            'scope':'Actual compare_twindow_run on synthetic CSV/NPZ/status bundles, original and separate one-function candidate. No mocked reader/NPZ stage, real S01, engine, baseline certificate, full study validity or independent approval.'}
    save(args.output/'cycle_results.json',record);print(json.dumps(record,indent=2));return 0


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--child',choices=MODES);args=p.parse_args()
    try:return child(args) if args.child else parent(args)
    except Exception as error:
        args.output.mkdir(parents=True,exist_ok=True)
        save(args.output/'failure.json',{'type':type(error).__name__,'message':str(error),'semantic_rejection_credited':False})
        raise


if __name__=='__main__':raise SystemExit(main())
```
<!-- END_CRITICAL_FILE: run_checks.py -->

### source_modules.json

<!-- BEGIN_CRITICAL_FILE: source_modules.json -->
```json
{
  "repo": "jacobbrainard84-knightninja/AIEFS",
  "commit": "eb3933c196ee19e80e1621ae80d89ca72e6d9485",
  "oracle": "AIEF_Experiments/aief_modular_platform_v1_analysis_v4/aief_modular/oracle.py",
  "platform": "AIEF_Experiments/aief_modular_platform_v1_analysis_v4",
  "modules": [
    {
      "path": "AIEF_Experiments/aief_modular_platform_v1_analysis_v4/aief_modular/__init__.py",
      "blob": "2693906361d9b8a958dcca3809a1e48f3ba3d37b",
      "bytes": 429
    },
    {
      "path": "AIEF_Experiments/aief_modular_platform_v1_analysis_v4/aief_modular/artifacts.py",
      "blob": "1755fd1c91c78306efe185614a5ec25ccb2812f0",
      "bytes": 12582
    },
    {
      "path": "AIEF_Experiments/aief_modular_platform_v1_analysis_v4/aief_modular/authority.py",
      "blob": "23f50b547e5035cd8638ccf00525e18ffeab188f",
      "bytes": 9065
    },
    {
      "path": "AIEF_Experiments/aief_modular_platform_v1_analysis_v4/aief_modular/branches.py",
      "blob": "28e364284afbf799ee2d474bb5791a6efab3f56c",
      "bytes": 3477
    },
    {
      "path": "AIEF_Experiments/aief_modular_platform_v1_analysis_v4/aief_modular/collectors.py",
      "blob": "06ea96da686224bdbbf0790792e83a58f73b2abe",
      "bytes": 9992
    },
    {
      "path": "AIEF_Experiments/aief_modular_platform_v1_analysis_v4/aief_modular/factors.py",
      "blob": "a9c16999baf18b0ada513bc29b62ccb0da0c7ebf",
      "bytes": 12545
    },
    {
      "path": "AIEF_Experiments/aief_modular_platform_v1_analysis_v4/aief_modular/oracle.py",
      "blob": "d2c59fe2ded5c842fcfd56dd8819f50cc55dc434",
      "bytes": 5683
    },
    {
      "path": "AIEF_Experiments/aief_modular_platform_v1_analysis_v4/aief_modular/registry.py",
      "blob": "2b50e409c851bf02b87ecdd3b1fe56fec2c66169",
      "bytes": 3180
    },
    {
      "path": "AIEF_Experiments/aief_modular_platform_v1_analysis_v4/aief_modular/runner.py",
      "blob": "9e3eb431444f3f32b3b3e616014332939bf0ea59",
      "bytes": 32813
    },
    {
      "path": "AIEF_Experiments/aief_modular_platform_v1_analysis_v4/aief_modular/spec.py",
      "blob": "6ce7361d85e14946a0b854bb9078bcb58f75e9dc",
      "bytes": 19734
    },
    {
      "path": "AIEF_Experiments/aief_modular_platform_v1_analysis_v4/aief_modular/studies/__init__.py",
      "blob": "2b1fcdde0aa007b747e60cf0bdd234ab8e186840",
      "bytes": 58
    },
    {
      "path": "AIEF_Experiments/aief_modular_platform_v1_analysis_v4/aief_modular/validation.py",
      "blob": "9afffc1c0e3d1f8e0ad726e33d3b059e9337a1da",
      "bytes": 11178
    }
  ]
}
```
<!-- END_CRITICAL_FILE: source_modules.json -->

### fetch_public_dependencies.py

<!-- BEGIN_CRITICAL_FILE: fetch_public_dependencies.py -->
```python
"""Fetch the reviewed public package source closure; no source execution/author API."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
from urllib.parse import quote
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('upstream'))
    args = parser.parse_args()
    manifest = json.loads((Path(__file__).resolve().parent / 'source_modules.json').read_text())
    def fetch(record):
        relative = Path(record['path'])
        if relative.is_absolute() or '..' in relative.parts or relative.suffix != '.py':
            raise ValueError('Unexpected public dependency path')
        target = args.output / relative
        if target.exists():
            data = target.read_bytes()
        else:
            url = ('https://raw.githubusercontent.com/' + manifest['repo'] + '/' + manifest['commit'] + '/' +
                   quote(record['path'], safe='/'))
            request = urllib.request.Request(url, headers={'User-Agent': 'Researcher-040282-read-only'})
            with urllib.request.urlopen(request, timeout=60) as response:
                data = response.read()
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        if blob != record['blob'] or len(data) != record['bytes']:
            raise RuntimeError('Dependency differs from reviewed source: ' + record['path'])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        return str(relative)
    with ThreadPoolExecutor(max_workers=4) as pool:
        files = list(pool.map(fetch, manifest['modules']))
    print(json.dumps({'tested_main':manifest['commit'], 'public_sources_fetched_and_verified':len(files),
                      'source_executed_by_fetcher':False, 'raw_commit_author_metadata_requested':False}, indent=2))


if __name__ == '__main__':
    main()
```
<!-- END_CRITICAL_FILE: fetch_public_dependencies.py -->

### extract_from_report.py

<!-- BEGIN_CRITICAL_FILE: extract_from_report.py -->
```python
"""Extract the eight named critical008 files. Does not execute/fetch anything."""
import argparse
import json
from pathlib import Path
import re

NAMES = {'oracle_candidate.py', 'status_contract.py', 'load_reviewed.py',
         'test_status_contract.py', 'run_checks.py', 'source_modules.json',
         'fetch_public_dependencies.py', 'extract_from_report.py'}
PATTERN = re.compile(r'<!-- BEGIN_CRITICAL_FILE: ([^>\n]+) -->\n```[^\n]*\n(.*?)\n```\n'
                     r'<!-- END_CRITICAL_FILE: \1 -->', re.S)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    pairs = PATTERN.findall(args.report.read_text())
    if len(pairs) !=len(NAMES) or {name for name, _ in pairs} !=NAMES:
        raise RuntimeError('Missing/duplicate/unexpected critical file')
    args.output.mkdir(parents=True, exist_ok=True)
    for name, body in pairs:
        if Path(name).name !=name:
            raise RuntimeError('Unsafe extraction path')
        target = args.output / name
        text = body + '\n'
        if target.exists() and target.read_text() !=text:
            raise RuntimeError('Existing different file: ' + name)
        target.write_text(text)
    print(json.dumps({'critical_files_extracted':len(pairs), 'code_executed':False}, indent=2))


if __name__ == '__main__':
    main()
```
<!-- END_CRITICAL_FILE: extract_from_report.py -->


## 8. Fixed protocol, source boundary and review request

### PLAN.md

```text
# 008 preregistration — condition-key multiplicity in the public oracle

Researcher040282; session preparation2026-09-04, Atlantic/Reykjavik. Prior owner/
repository date labels are not inferred execution timestamps. Deterministic tests;
no RNG or change to old seeds. This plan precedes all acquired-code execution.

## Source, coordination and one finding

Fresh main eb3933c196ee19e80e1621ae80d89ca72e6d9485. Inbox
fef8b0262c31cbdd23f9668a55fffb43b2dc1002. Initially11 main/6 selected inbox files;
static package import acquisition now19 main selections/12 Python source modules.
No acquired code imported during acquisition. Six selected notes: intake/targeted
R001 note unchanged; general TRIAGE updated with other agents' static reviews.
No005–008 named follow-up found. Public open-PR list empty;15 public branch names
seen, none matching oracle/duplicate/uniqueness. Limited public navigation only.

B-F7 is KNOWN: R001 previously reproduced the public3-vs2 toy mechanism, not the
real201-vs200 S01 witness. Main oracle.py still turns condition rows into sets.
runner.py:385–398,664–699 writes one status row per condition with seed/rho/status.
Natural condition identity is (seed text, float(rho)); status is a VALUE, not part
of identity. Scalar/NPZ content, elapsed/error metadata and whole-study validity
are separate questions. No renewed uploader/bridge/engine repair in this branch.

ART-0076 (current oracle.py) is Supported, lock_status=none. Proposal may be a
normal one-function review-branch change, but no live upstream/source-cache edit,
registry update, PR or installation is authorized. Frozen engine/real artifacts
stay unchanged. Deliver a complete separate oracle_candidate.py, derived from
current source with only _compare_condition_coverage replaced; all other AST
nodes and public entry point remain unchanged. Import ACTUAL package/oracle and
candidate module, call actual compare_twindow_run; do not mock its CSV/NPZ stages.
No runner/simulation, real NPZ, baseline certificate or Lean build.

## Declared contract, before tests

Required status columns seed,rho,status. Seed is exact text, unchanged from
current API (do not coerce numeric-looking seeds). Rho normalization is the
EXISTING Python float parsing/equality policy, not raw text and not a tolerance.
Require finite parsed rho to make semantic keys well-defined; malformed/nonfinite
rho produces explicit failed comparison on either side. Positivity, full cohort,
200-condition design and all status-file metadata are not newly validated here.

For each side, each normalized (seed,rho) key must appear exactly once, even if
repeated rows have different statuses. Enforce row-count equality explicitly;
compare coverage/status values as before. Order of condition rows is irrelevant;
numeric rho spellings that parse to the same float remain equivalent. Missing/
changed coverage/status, schema failure, duplicates on either side or row-count
mismatch must reject. Both header-only status tables retain prior logical-empty
behavior: not a real-study certificate. Elapsed/error auxiliary metadata remains
ignored; scalar CSV and NPZ comparison logic must stay unchanged and active.
No numeric comparison tolerance is changed (exact).

Independent oracle: from IMMUTABLE original row tuples/header declarations,
normalize keys by the declared float policy, check finiteness, use nested PAIRWISE
comparisons for uniqueness and matching key/status values. Do not call candidate,
_read_csv, set/Counter validation or returned source answers for expected truth.
Expected answer and snapshots of all six toy input files precede target call;
reject any input rewrite, even if the target returns the now-matching answer.

## Same12 common contracts, normal and -O

1 Unique nontrivial six-condition match.
2 Reordered condition rows and numeric rho aliases still match (seed stays text).
3 Candidate-only exact duplicate appended rejects.
4 Oracle-only duplicate appended rejects.
5 Equal row counts with matching duplicates on both sides reject (count alone is insufficient).
6 Matching tables with conflicting statuses at ONE key reject (status is not key).
7 Missing/changed seed/rho/status, duplicate replacing another key, required column
  loss and text-seed distinction reject; do not mistake them for new findings.
8 Existing scalar CSV value/branch/column gates still reject corruption.
9 Existing NPZ value/dtype/shape/key/partial-NaN-component gates still reject.
10 Auxiliary condition metadata ignored and logical-empty comparison preserved.
11 Returned scalar/NPZ/condition counts accurate, files unchanged on valid cases.
12 Numeric-alias duplicates reject under normalized key identity.

Expect original exactly5 failing methods (3,4,5,6,12),0 errors; candidate all12
pass. Invalid/malformed rho is outside the original well-formed common domain:
add candidate-only validation for NaN,Inf,-Inf,not-numeric,empty rho on each side
(10 cases). Do not count original parse exceptions as semantic red success.

## Exhaustive small-table census, also public API

Alphabet A=(s0,.5,success), B=(s1,1,success), C=(s0,.5,failed).
All ordered sequences length0..3:40 per side;1600 ordered table pairs. Every pair
runs actual public API with nontrivial matching scalar CSV (2 rows) and NPZ
(2 entries), not only the private condition helper. Independent contract predicts
12 accepted pairings: empty1; three singleton self-pairs3; permutations of AB and
BC give4 each. Current set-based source predicts256 accepted pairings:1 +3*3^2
+3*8^2 +6^2. Thus244 false accepts,0 false rejects. Record actual mismatches;
this finite alphabet is not all CSVs, all real runs or affected production records.
Write/reuse small temporary toy bundles, then remove them; persist complete census
results/witnesses, not1600 redundant copies of NPZ files.

## Distinct wrong-model controls

Require intended ContractMismatch for: original set collapse; count+set only;
uniqueness of (seed,rho,status) instead of condition key; order-sensitive status
comparison; raw-rho-text identity; ignoring status; bypassing the existing NPZ
gate; mutating/deduplicating requested CSV before comparison. Same8 controls in
normal and optimized workers. Only truth/input-preservation/count failures count;
import/setup/unrelated exceptions block, never count as semantic detections.
No false claim that removing redundant guards is detectable from status alone.

## Closeout

All12 reviewed public source modules unchanged before/after. Only one candidate
function AST differs; public API/other validators untouched. Return1 original red
runs expected only for exactly the intended failures; return0 candidate/control
workers and whole runner only when preregistered outcomes observed. No Python
assert acceptance that disappears under -O. No original control weaken/tolerance
change after observing results.

Standalone numbered Markdown with full critical files and essential actual output;
extract to fresh dir, fetch12 reviewed public dependencies and repeat entire
normal/-O runner, compare science and non-timing worker/census records. Preserve
prior112 ledger rows/94 formal labels and completed007 state; one bounded new
proposal record. Metadata minimal, cited logs unpacked/indexed. Do not restore
user-deleted Lua audit. No contact/push/PR/upload, frozen edit or unattended work.

Fresh triage also confirms v4.1 self-supplied-manifest trust-root risk but no
runtime false-accept reproduction; proposed next009 is an isolated boundary
negative control after fresh source/feedback, not a second finding in008.
Do NOT duplicate the existing rate-law delta sweep on the reported research
branch. No documentation cleanup duplicates of the Chronicler deposit.
```

### proposal/INTEGRATION_NOTE.md

```text
# 008 integration handoff — one condition-key finding, not installed

Known B-F7, not a new production-data discovery. Actual main's public comparator
loses condition-row multiplicity. The condition identity follows the writer:
exact seed text and the existing float(rho) policy; status is a value. Repairing
only total row counts or requiring unique (seed,rho,status) triples is insufficient.

The complete separate `oracle_candidate.py` derives from the reviewed oracle;
only `_compare_condition_coverage` differs. All17 other top-level AST nodes,
including actual scalar/NPZ gates and public entry point, remain unchanged.
Original12-source package is imported normally; the candidate is separately
registered as a descendant module before execution. No stubbed readers. Package
import imports runner definitions; NO runner/simulation entry point is called.

Proposed policy: required seed/rho/status columns, explicit row-count equality,
finite parsed rho, unique (seed,rho) on BOTH sides, same coverage/status values.
Condition row order and numeric rho aliases remain irrelevant; seed text exact.
Aux elapsed/error metadata remains ignored. Equal failed statuses and equal
header-only status tables may logically compare equal. This is NOT a successful
200-condition study certificate. Positivity/full cohort/full schema/atomic I/O/
trust-root/security validation is not added. No comparison tolerance changes.

Observed, not merely predicted: original5/12 intended failing methods,0errors;
candidate12/12pass, both normal and-O.1600 public-API table pairs per target give
original244false accepts/0false rejects versus candidate0mismatches;10 additional
invalid-rho cases fail candidate explicitly each mode.8 distinct semantic/input-
mutation controls detected each mode. Immutable expected rows and six-file
snapshots precede every target call. Separate fresh-note reproduction receipt
must actually exist before delivery; tests are submitter-local, not seat approval.

ART-0076 is Supported and lock_status=none. An ordinary ONE-function review branch
could be appropriate if the owner/seat accepts this contract and independent tests.
This agent has not created a remote branch, PR, push, upload, registry change or
production installation. Frozen ART-0702, pinned ART-0050 and existing authorities
remain untouched. Do not combine007 engine,005 bridge,006 estimand or future
trust-root work into this proposal. No real S01/201-vs200 execution is represented.

Requested review: independently reproduce from the standalone note, confirm
condition identity/status-value and logical-comparison policy, inspect finite-rho
and ignored-metadata boundaries, and decide whether/how to integrate the single
helper change. Prior R001 B-F7 mechanism reproduction does not approve this new
candidate, specification, census or mutation controls.
```

### review_decision.json

```json
{
  "evidence_label": "EXECUTABLE_REGRESSION_CHECK",
  "decision": "BOUNDED_PUBLIC_API_PROPOSAL_SUPPORTED_BY_OWN_TESTS_NOT_INSTALLED_OR_INDEPENDENTLY_REVIEWED",
  "known_condition": "B-F7 set collapse of condition-row multiplicity, previously reproduced by R001 on minimal toy inputs",
  "finding_count": 1,
  "changed_function": "_compare_condition_coverage",
  "other_top_level_ast_nodes_preserved": 17,
  "semantic_condition_key": "exact seed text, existing float(rho) normalization; finite parsed rho required",
  "status_is": "VALUE_NOT_KEY",
  "row_count_equality_explicit": true,
  "unique_keys_required_on_both_sides": true,
  "original_expected_failures_observed_each_mode": 5,
  "original_errors_each_mode": 0,
  "candidate_contract_passes_each_mode": 12,
  "public_api_census_pairs_each_target_each_mode": 1600,
  "original_false_accepts_each_mode": 244,
  "original_false_rejects_each_mode": 0,
  "candidate_census_mismatches_each_mode": 0,
  "candidate_only_invalid_finite_key_cases_each_mode": 10,
  "distinct_mutants_detected_each_mode": 8,
  "source_policy": "ART-0076 Supported/lock_status none; separate local full-module candidate, source-cache unchanged",
  "standalone_receipt_required_before_delivery": "cycle_008/standalone_reproduction.json",
  "current_candidate_harness_independently_reviewed": false,
  "not_approved": [
    "production repair installation or successful full-study certification",
    "real S01 or 201-vs200 production witness, all saved-artifact census or quantified real impact",
    "all malformed CSV/NPZ, complete schema, positive rho, complete cohort/status allowlist or atomic I/O validation",
    "self-supplied-manifest trust root, uploader, bridge, engine, interval estimands or authority lock changes",
    "universal Python/NumPy theorem, new Lean proof, coupled oscillator stability or scientific inference",
    "independent-seat approval of008 candidate, independent contract, fixtures, census, or mutants",
    "remote branch push, PR, outside contact, inbox merge, upload or unattended next cycle"
  ]
}
```

### candidate_boundary.json

```json
{
  "only_function_changed": "_compare_condition_coverage",
  "other_top_level_ast_nodes_preserved": 17,
  "original_function_lines": [
    97,
    111
  ],
  "source_cache_or_upstream_modified": false,
  "proposal_installed": false
}
```

### historical_restoration.json

```json
{
  "kind": "ADMINISTRATIVE_MISSING_ONLY_RESTORATION_NOT_SCIENTIFIC_REEXECUTION",
  "reason": "Prior007 archive comparison found this one old006 workflow absent in current workspace; cause not inferred",
  "path": "cycle_006/source_state/main/.github/workflows/repo-checks.yml",
  "delivered_archive": "researcher040282-cycle007-complex-nan-comparator.zip",
  "restored_bytes": 9175,
  "restored_content_matches_delivered_member": true,
  "existing_source_or_log_overwritten": false,
  "scientific008_inputs_code_results_changed": false,
  "historical_science_rerun": false,
  "user_deleted_legacy_lua_audit_remains_absent": true
}
```


## 9. Limitations, labels and next step

- Supported result: bounded actual-public-API regression evidence for one known
  multiplicity/semantic-key gap and a local one-function candidate. The finite
  uniqueness argument is paper reasoning, not a universal runtime/NumPy proof.
- No full S01, real201-vs200 run,4800-case replay, saved-artifact finiteness census,
  affected production record count, new production certificate or impact estimate.
- No new positivity, complete-study/schema/status allowlist, atomic read-back,
  hostile CSV/NPZ security or manifest trust-root certification. Aux metadata is
  intentionally ignored. Matching failed/empty tables may logically compare equal.
- No tolerance change, frozen/pinned repair, engine/bridge/uploader/interval change,
  new Lean compilation or inference about coupled locking.
- R001's prior B-F7 mechanism reproduction is not approval of008 code/contract/
  controls. Earlier94 independent declaration compilations do not approve our
  controls, library fidelity,005–008 proposals or full production equivalence.
- Prior112 ledger rows/94 formal labels and all delivered scientific evidence stay
  unchanged. One scoped proposal record is appended only after actual extraction/
  fresh-source rerun. Privacy metadata is minimized; all cited evidence unpacked.
- Owner/seat should independently reproduce, accept/revise the key/status/logical-
  comparison policy and decide integration of this ONE helper on an authorized
  review branch. **Prepared is not uploaded. Tested is not independently approved.**

**Next009, not started:** fresh-check the candidate assessment-tool trust boundary
and isolate the reported self-supplied-manifest negative control. Current TRIAGE
only structurally confirms that concern, with no executed forged-cohort witness;
do not describe it as an observed false accept yet. Do not duplicate the existing
rate-law delta sweep or Chronicler documentation work. No real campaign, outside
contact, remote push/PR/upload or unattended continuation is authorized here.
