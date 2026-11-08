"""Bounded packet validation, not a proof/security scanner or Lean rerun.

Validate a first archive, write a repeatable receipt, repackage to INCLUDE that
receipt, then validate final archive again. No self-referential ZIP digest field.
"""
from pathlib import Path
import csv
from io import StringIO
import json
import re
import zipfile

import build_packet as builder

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
EMAIL = re.compile(rb"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PATTERN = re.compile(r'<!-- BEGIN_CRITICAL_FILE: ([^>\n]+) -->\n```[^\n]*\n(.*?)\n```\n'
                     r'<!-- END_CRITICAL_FILE: \1 -->', re.S)


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def ledger(path):
    with path.open(newline='') as stream:
        return list(csv.DictReader(stream))


def preflight():
    state = json.loads((ROOT / 'STATE.json').read_text())
    require(state['current_cycle'] == 5 and state['current_status'] == 'COMPLETED_LOCAL_CANDIDATE_UNREVIEWED',
            'Current root completion mismatch')
    require(state['in_progress'] is None and state['research_processes_running'] == []
            and state['next_cycle'] == 6, 'Inconsistent completion/resumption state')
    require(state['current_cycle_independent_review_received'] is False
            and state['latest_packet_owner_upload_confirmed'] is False, 'Do not imply new review/upload')
    current = ledger(ROOT / 'CLAIM_LEDGER.csv')
    completion = ledger(HERE / 'completed_004_snapshot/CLAIM_LEDGER_COMPLETED_004.csv')
    require(len(current) == len({x['claim_id'] for x in current}) == 109, 'Current ledger count/uniqueness mismatch')
    require(len(completion) == len({x['claim_id'] for x in completion}) == 108, '004 ledger count/uniqueness mismatch')
    require([x for x in current if x['cycle'] != '5'] == completion, 'Prior108 not synchronized with004 snapshot')
    require(sum(x['evidence_label'] == 'LEAN_COMPILED' for x in current) == 94, 'Unexpected formal claim promotion')
    report = builder.REPORT.read_text()
    require('PROVISIONAL: extracted-code rerun not executed yet' not in report, 'Cannot deliver provisional report')
    blocks = PATTERN.findall(report)
    require(len(blocks) == 6 and {name for name, _ in blocks} == set(builder.CRITICAL), 'Critical file set mismatch')
    for name, content in blocks:
        data = (content + '\n').encode()
        require(data == (HERE / 'proposal' / name).read_bytes(), 'Inline source mismatch: ' + name)
        require(data == (HERE / 'standalone/extracted' / name).read_bytes(), 'Executed inline source mismatch: ' + name)
    repeated = json.loads((HERE / 'standalone/checks/cycle_results.json').read_text())
    require(repeated['all_preregistered_acceptance_conditions_met'] is True, 'Standalone check incomplete')
    require([x['tests_run'] for x in repeated['regression_runs']] == [3, 22, 22], 'Standalone counts mismatch')
    branch_records = [path for path in ROOT.rglob('*_branch*.json') if 'source_state' in path.parts]
    require(len(branch_records) == 8, 'Unexpected branch metadata record count')
    for path in branch_records:
        value = json.loads(path.read_text())
        require(set(value) == {'branch', 'commit', 'metadata_policy'}, 'Metadata not structurally minimized: ' + str(path.relative_to(ROOT)))
    contact_hits = []
    for path in builder.selected_files():
        matches = EMAIL.findall(path.read_bytes())
        if matches:
            contact_hits.append({'path': str(path.relative_to(ROOT)), 'occurrences': len(matches)})
    require(not contact_hits, 'Outgoing contact-pattern scan failed (paths/counts only): ' + json.dumps(contact_hits))
    require(not state['remote_changes_by_this_agent'] and not state['contacted_other_bots']
            and not state['automatic_work_between_turns'], 'Boundary state mismatch')
    index = json.loads((ROOT / 'EVIDENCE_INDEX.json').read_text())
    require(index['ledger_rows'] == 109 and index['archive_only_ledger_references'] == 0,
            'Evidence navigation not synchronized')
    for item in index['ledger_evidence']:
        require(item['availability'] == 'UNPACKED' and item['packet_members'], 'Unresolved evidence reference')
        for name in item['packet_members']:
            require((ROOT.parent / name).is_file(), 'Unpacked reference absent: ' + name)
    protected = ['2026-09-04_researcher040282_004_complex-ema.md']
    protected += ['cycle_004/' + name for name in (
        'GateFoundations.lean', 'FreezeCore.lean', 'GateProposalBridge.lean',
        'CoherenceEMA.lean', 'CoherenceDriveBridge.lean', 'check_cycle.py', 'compare_source.py')]
    with zipfile.ZipFile(ROOT / 'researcher040282-cycle004-complex-ema.zip') as old:
        for relative in protected:
            require((ROOT / relative).read_bytes() == old.read('researcher_040282/' + relative),
                    'Old004 critical source/report changed: ' + relative)
        old_ledger = list(csv.DictReader(StringIO(old.read('researcher_040282/CLAIM_LEDGER.csv').decode())))
    require(len(old_ledger) == 108, 'Historical004 ledger count unexpected')
    for before, after in zip(old_ledger, completion):
        for key in before:
            if key not in {'independent_review', 'publication'}:
                require(before[key] == after[key], 'Old scientific ledger field changed: ' + before['claim_id'])
    for name in ('README.md', 'WORKFLOW.md', 'RESEARCH_QUEUE.md'):
        require('005' in (ROOT / name).read_text(), 'Root navigation stale: ' + name)
    return {'current_ledger_rows': 109, 'completed004_ledger_rows': 108,
            'original108_statements_and_evidence_labels_preserved': True,
            'compiled_labels_unchanged': 94, 'critical_inline_files_match_actual_extracted_run': 6,
            'historical004_critical_sources_and_report_preserved': len(protected),
            'standalone_runner_observed_exit': 0, 'standalone_counts': [3, 22, 22],
            'reported_three_metadata_files_structurally_minimized': True,
            'all_eight_branch_metadata_records_minimal': True,
            'outgoing_email_pattern_matches': 0,
            'all_ledger_references_unpacked': True,
            'archive_only_ledger_references': 0,
            'ledger_reference_count': index['unique_ledger_references'],
            'unpacked_log_count': index['unpacked_log_count'],
            'no_remote_actions_or_current_candidate_review_claim': True}


def verify_archive():
    expected = {'researcher_040282/' + str(path.relative_to(ROOT)): path
                for path in builder.selected_files()}
    with zipfile.ZipFile(builder.ARCHIVE) as archive:
        require(archive.testzip() is None, 'Archive CRC failure')
        require(len(archive.namelist()) == len(set(archive.namelist())), 'Duplicate archive member')
        require(set(archive.namelist()) == set(expected), 'Archive file selection differs from workspace')
        for name, path in expected.items():
            content = archive.read(name)
            require(content == path.read_bytes(), 'Archive member/workspace mismatch: ' + name)
            require(not EMAIL.search(content), 'Contact-pattern match in archive member: ' + name)
    return len(expected)


def main():
    result = preflight()
    verify_archive()
    result.update({'zip_crc_verified': True, 'all_members_match_selected_workspace_files': True,
                   'receipt_included_then_final_archive_reverified': True,
                   'scope': 'Local owned-packet consistency/privacy hygiene; not fresh Lean compilation, arbitrary-code security, or independent approval'})
    (HERE / 'packet_validation.json').write_text(json.dumps(result, indent=2) + '\n')
    builder.package()
    members = verify_archive()
    preflight()
    print(json.dumps({'validation': result, 'final_archive_members': members,
                      'final_archive_bytes': builder.ARCHIVE.stat().st_size}, indent=2))


if __name__ == '__main__':
    main()
