"""Assemble the standalone handoff from observed results and exact source blocks.

Default: rebuild the Markdown. --package also makes the optional supporting ZIP.
Fails rather than report success from mismatched or absent final-run evidence.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import zipfile

CYCLE = Path(__file__).resolve().parent
ROOT = CYCLE.parent
NAME = '2026-11-07_researcher040282_002_guarded-capacity-lean.md'
REPORT = ROOT / NAME
ALLOWED = {'propext', 'Classical.choice', 'Quot.sound'}
EXPECTED_CASES = {
    'positive', 'false_unconditional_idempotence', 'false_unrestricted_epsilon',
    'sorry_payload', 'extra_axiom_payload', 'missing_footprint',
    'nonzero_active_gate_witness', 'replace_endpoint_min_with_max',
    'drop_entrywise_nonnegativity',
}


def validate_result(data, lean, checker):
    assert data['control_count'] == 9 and data['all_controls_passed'] is True
    assert data['source_sha256'] == hashlib.sha256(lean.encode()).hexdigest()
    assert data['harness_sha256'] == hashlib.sha256(checker.encode()).hexdigest()
    assert data['mathlib_revision'] == '0df444a360eaa60ab8c11dca51a86af692955474'
    controls = {r['case']: r for r in data['controls']}
    assert set(controls) == EXPECTED_CASES
    assert all(r['control_passed'] for r in controls.values())
    positive = controls['positive']
    assert positive['raw_lean_exit'] == 0 and positive['verified']
    assert positive['problems'] == [] and positive['theorem_count'] == 22
    assert len(positive['axiom_footprints']) == 22
    assert all(set(a) <= ALLOWED for a in positive['axiom_footprints'].values())
    for name in ['false_unconditional_idempotence', 'false_unrestricted_epsilon']:
        r = controls[name]
        assert r['raw_lean_exit'] != 0 and r['mathematical_error_observed']
        assert not r['dependency_error_observed'] and not r['verified']
    for name in ['sorry_payload', 'extra_axiom_payload', 'missing_footprint']:
        assert controls[name]['raw_lean_exit'] == 0 and not controls[name]['verified']
    return controls


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--package', action='store_true')
    args = parser.parse_args()
    lean = (CYCLE / 'GateFoundations.lean').read_text()
    checker = (CYCLE / 'check_cycle.py').read_text()
    result = json.loads((CYCLE / 'cycle_results.json').read_text())
    controls = validate_result(result, lean, checker)
    text = (CYCLE / 'REPORT_BODY.md').read_text().rstrip() + '\n\n'
    text += '## 8. Observed fresh-build and red-team evidence\n\n'
    text += '**Recorded compiler:** `' + result['compiler_version'] + '`.\n\n'
    text += ('The final local runner exited `0`. **All nine controls passed their '
             'intended acceptance/rejection checks: two positive controls and seven '
             'negative controls.** A negative-control PASS means the bad statement, '
             'bad evidence policy, or wrong variant was rejected/refuted; it does not '
             'mean that a false theorem was verified.\n\n')
    text += '| Case | Raw Lean exit | Verification / exact outcome | Control |\n'
    text += '|---|---:|---|---|\n'
    labels = {
        'positive': 'Fresh 22-theorem positive source',
        'false_unconditional_idempotence': 'False unconditional idempotence',
        'false_unrestricted_epsilon': 'False unrestricted-epsilon capacity',
        'sorry_payload': 'Proof-hole payload',
        'extra_axiom_payload': 'New-axiom payload',
        'missing_footprint': 'Deleted one axiom-print request',
        'nonzero_active_gate_witness': 'Nonzero active-gate witness',
        'replace_endpoint_min_with_max': 'Wrong endpoint max',
        'drop_entrywise_nonnegativity': 'Signed input with nonnegative row sums',
    }
    for r in result['controls']:
        name = r['case']
        if r['kind'] == 'positive': outcome = 'Accepted; 22/22 footprints allowed'
        elif r['kind'] == 'false_math': outcome = 'Rejected; mathematical error, no dependency error'
        elif r['kind'] in {'sorry_payload', 'extra_axiom_payload', 'missing_footprint'}:
            outcome = 'Rejected: `' + '; '.join(r['problems']) + '`'
        elif r['kind'] == 'positive_exact': outcome = 'Exact nonzero/feasible active result'
        else: outcome = 'Exact capacity counterexample to weakened/wrong variant'
        text += f"| {labels[name]} | {r.get('raw_lean_exit', 'not a Lean case')} | {outcome} | PASS |\n"
    text += ('\nFor each false mathematical payload, Lean reached `unsolved goals` '
             'with goal `False`; the positive file proves the corresponding exact '
             'opposite statement. Missing imports or unknown identifiers were not '
             'counted as mathematical rejection. The proof-hole footprint contains '
             '`sorryAx`; the new-axiom footprint contains `injectedEquality`. The '
             'missing-print case still compiles valid mathematics but has incomplete '
             'audit coverage, which this policy rejects.\n\n')
    text += '### Complete positive-file printed axiom output\n\n```text\n'
    positive_log = (CYCLE / 'checks/positive.log').read_text().strip()
    assert len(positive_log.splitlines()) == 22
    assert all('depends on axioms:' in line for line in positive_log.splitlines())
    text += positive_log + '\n```\n\n'
    text += '### Recorded runner output\n\n```text\n'
    text += (CYCLE / 'cycle_checks.log').read_text().strip() + '\n```\n\n'
    stand = CYCLE / 'standalone_results.json'
    if stand.exists():
        standalone = json.loads(stand.read_text())
        validate_result(standalone, lean, checker)
        manifest = json.loads((CYCLE / 'standalone_manifest.json').read_text())
        assert manifest['runner_exit'] == 0 and manifest['code_blocks_match_workspace']
        text += ('### Single-file extraction was also executed\n\n'
                 'The two inline code blocks were extracted from this standalone '
                 'Markdown into a new temporary directory and the extracted checker '
                 'was actually run with the recorded dependencies. That runner also '
                 'exited `0`, accepted the 22-theorem positive source, and reached '
                 'all nine intended outcomes. The extracted code blocks match the '
                 'final supplied source exactly. Its JSON, raw logs, and extraction '
                 'manifest are supplied in the optional ZIP. This is a local '
                 'self-reproduction check, **not independent-seat review**.\n\n')
    else:
        text += ('### Single-file extraction status\n\n'
                 'The sources are inline, but a separate run extracted from this '
                 'Markdown has not yet been recorded. The results above are from '
                 'the fresh local checker run.\n\n')
    text += '## Appendix A — complete compiled Lean source\n\n'
    text += '<!-- FILE: GateFoundations.lean -->\n```lean\n' + lean.rstrip() + '\n```\n\n'
    text += '## Appendix B — complete bounded proof/red-team checker\n\n'
    text += '<!-- FILE: check_cycle.py -->\n```python\n' + checker.rstrip() + '\n```\n'
    REPORT.write_text(text)
    print(f'Wrote {REPORT.name}: {REPORT.stat().st_size:,} bytes')
    if args.package:
        required = [REPORT, ROOT / 'README.md', ROOT / 'WORKFLOW.md',
                    ROOT / 'RESEARCH_QUEUE.md', ROOT / 'STATE.json',
                    ROOT / 'CLAIM_LEDGER.csv']
        for name in ['GateFoundations.lean', 'check_cycle.py', 'PLAN.md',
                     'REPORT_BODY.md', 'build_packet.py', 'one_file_reproduce.py',
                     'lean_compile.log', 'lean_compile_initial.log',
                     'cycle_checks.log', 'cycle_results.json',
                     'standalone_results.json', 'standalone_reproduction.log',
                     'standalone_manifest.json']:
            required.append(CYCLE / name)
        required += sorted((CYCLE / 'checks').glob('*.log'))
        required += sorted((CYCLE / 'standalone_checks').glob('*.log'))
        required.append(ROOT / 'coordination/source_state/selected_source_verification.json')
        assert all(p.is_file() for p in required)
        path = ROOT / 'researcher040282-cycle002-guarded-capacity.zip'
        with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            for file in required:
                archive.write(file, (Path('researcher_040282') / file.relative_to(ROOT)).as_posix())
        with zipfile.ZipFile(path) as archive:
            assert archive.testzip() is None
            assert len(archive.namelist()) == len(required)
        print(f'ZIP CRC passed: {len(required)} files, {path.stat().st_size:,} bytes')


if __name__ == '__main__':
    main()
