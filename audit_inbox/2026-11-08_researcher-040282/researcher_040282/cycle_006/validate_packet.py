"""Bounded owned-packet closure/privacy checks. No scientific or Lean rerun.

Original-owner-workspace closeout: historical archive comparisons require those
prior archives, which are not nested in the new packet. Reproduce the scientific
checks with the seven-file standalone note instead. This validator does not
authenticate independent review or secure arbitrary-code intake. Deliberately
synthetic PUBLIC Git fixture addresses are not actual author data.
"""
from pathlib import Path
import csv
import hashlib
import json
import re
import zipfile

import build_packet as builder

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SCIENCE = ('exhaustive_small', 'saved_grid', 'policy_boundaries', 'mutations', 'synthetic_pipeline', 'bootstrap')
EMAIL = re.compile(rb"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
BLOCK = re.compile(r'<!-- BEGIN_CRITICAL_FILE: ([^>\n]+) -->\n```[^\n]*\n(.*?)\n```\n'
                   r'<!-- END_CRITICAL_FILE: \1 -->', re.S)
FIXTURE = 'cycle_006/source_state/main/tools/redteam/test_rt_claims_hygiene.py'


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def read_ledger(path):
    with path.open(newline='') as stream:
        return list(csv.DictReader(stream))


def git_blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def inspect_contact_patterns(items):
    matches = []
    for name, data in items:
        count = len(EMAIL.findall(data))
        if count:
            require(name == FIXTURE and count == 2,
                    'Unclassified outgoing contact pattern (path/count only): ' + name + '/' + str(count))
            require(b'GIT_AUTHOR_NAME": "fixture"' in data and b'GIT_COMMITTER_NAME": "fixture"' in data,
                    'Allowlisted path no longer has synthetic fixture context')
            metadata = json.loads((HERE / 'source_state/main_selected.json').read_text())
            record = next(row for row in metadata['files'] if row['path'] == 'tools/redteam/test_rt_claims_hygiene.py')
            require(git_blob(data) == record['blob'] and len(data) == record['bytes'],
                    'Public fixture differs from acquired, reviewed source')
            matches.append({'path': name, 'occurrences': count,
                            'classification': 'INTENTIONALLY_SYNTHETIC_PUBLIC_GIT_ENV_FIXTURE;NOT_PERSONAL_COMMIT_METADATA',
                            'source_unmodified_and_acquisition_verified': True,
                            'executed_by_this_cycle': False})
    require(len(matches) == 1, 'Expected one synthetic public fixture path')
    return matches


def preflight():
    state = json.loads((ROOT / 'STATE.json').read_text())
    require(state['current_cycle'] == 6 and state['current_status'] == 'COMPLETED_LOCAL_QUALIFIED_CONTRACT_REVIEW',
            'Current scientific-completion state mismatch')
    require(state['in_progress'] is None and state['next_cycle'] == 7 and state['research_processes_running'] == [],
            'Resumption/active-process state mismatch')
    require(state['last_updated_date'] == '2026-09-04' and
            state['date_provenance']['administrative_notice_written_after_original006_executions'] and
            not state['date_provenance']['scientific_protocol_or_seed_changed_by_notice'] and
            not state['date_provenance']['historical004_execution_date_reconstructed'], 'Administrative provenance mismatch')
    require(not state['current_cycle_independent_review_received'] and not state['latest_packet_owner_upload_confirmed'],
            'New review/upload must not be inferred')
    require(not state['remote_changes_by_this_agent'] and not state['contacted_other_bots'] and
            not state['automatic_work_between_turns'], 'Remote/autonomy boundary mismatch')
    current = read_ledger(ROOT / 'CLAIM_LEDGER.csv')
    prior = read_ledger(HERE / 'previous005_snapshot/CLAIM_LEDGER.csv')
    completed004 = read_ledger(ROOT / 'cycle_005/completed_004_snapshot/CLAIM_LEDGER_COMPLETED_004.csv')
    require(len(current) == len({row['claim_id'] for row in current}) == 111, 'Current ledger mismatch')
    require(len(prior) == 109 and current[:109] == prior, 'Prior109 rows changed')
    require(len(completed004) == 108 and [row for row in prior if row['cycle'] != '5'] == completed004,
            'Completed004 scope/rows not preserved')
    require(sum(row['evidence_label'] == 'LEAN_COMPILED' for row in current) ==94,
            'Unexpected formal-evidence promotion')
    require([row['evidence_label'] for row in current[-2:]] == ['EXECUTABLE_REGRESSION_CHECK', 'PAPER_ARGUMENT'],
            '006 evidence labels overstate scope')
    four = [json.loads((HERE / path / 'cycle_results.json').read_text())
            for path in ('checks', 'optimized_checks', 'standalone/checks', 'standalone/optimized_checks')]
    for item, flag in zip(four, (False, True, False, True)):
        require(item['all_preregistered_robust_checks_passed'] and item['upstream_modules_unchanged'] ==12 and
                item['candidate_cli_default_refuses_real_pipeline'] and item['optimized_python'] is flag,
                'Actual execution acceptance mismatch')
    for key in SCIENCE:
        require(all(value[key] == four[0][key] for value in four[1:]), 'Scientific reproduction mismatch: ' + key)
    require(four[0]['exhaustive_small']['robust_cases'] ==3072 and
            four[0]['saved_grid']['translated_robust_cases'] ==2350, 'Expected case families missing')
    receipt = json.loads((HERE / 'standalone_reproduction.json').read_text())
    require(receipt['returncodes'] == [0, 0] and receipt['critical_file_count'] ==7 and
            receipt['fresh_public_modules_fetched_and_verified'] ==12 and
            receipt['all_six_scientific_result_groups_match_all_four_runs'], 'Standalone receipt incomplete')
    report = builder.REPORT.read_text()
    require('PROVISIONAL: extracted-code rerun not executed yet' not in report, 'Provisional report cannot be delivered')
    require('schema-total coverage' in report and 'density and similarity share masks/targets' in report
            and '`window_steps`' in report, 'Missing bounded coverage language')
    blocks = BLOCK.findall(report)
    require(len(blocks) ==7 and {name for name, _ in blocks} == set(builder.CRITICAL), 'Critical source set mismatch')
    for name, content in blocks:
        data = (content + '\n').encode()
        require(data == (HERE / 'programs' / name).read_bytes() == (HERE / 'standalone/extracted' / name).read_bytes(),
                'Inline code differs from actual extracted execution: ' + name)
    before_notice = (HERE / 'PLAN_PREREGISTERED_BEFORE_ADMIN_NOTICE.md').read_text()
    current_plan = (HERE / 'PLAN.md').read_text()
    require(current_plan.startswith(before_notice) and
            '## Post-execution administrative notice' in current_plan[len(before_notice):],
            'Scientific preregistration text changed rather than append-only admin notice')
    verified = {}
    for branch, expected in (('main', 28), ('inbox', 37)):
        metadata = json.loads((HERE / 'source_state' / (branch + '_selected.json')).read_text())
        require(len(metadata['files']) == metadata['fetched_and_verified'] == expected, 'Acquisition count mismatch')
        for record in metadata['files']:
            path = HERE / 'source_state' / branch / record['path']
            data = path.read_bytes()
            require(len(data) == record['bytes'] and git_blob(data) == record['blob'],
                    'Acquired source modified: ' + branch + '/' + record['path'])
        verified[branch] = expected
    records = [path for path in ROOT.rglob('*_branch*.json') if 'source_state' in path.parts]
    require(len(records) ==10, 'Expected ten acquisition branch records')
    for path in records:
        value = json.loads(path.read_text())
        require(set(value) == {'branch', 'commit', 'metadata_policy'} and all(isinstance(x, str) for x in value.values()),
                'Nonminimal acquisition metadata: ' + str(path.relative_to(ROOT)))
    contacts = inspect_contact_patterns((str(path.relative_to(ROOT)), path.read_bytes()) for path in builder.selected_files())
    privacy = {'all_ten_branch_records_structurally_minimal': True,
               'new006_metadata_minimal_at_acquisition': True,
               'personal_commit_contacts_or_signed_payloads_in_branch_metadata': 0,
               'unclassified_outgoing_email_pattern_matches': 0,
               'allowlisted_synthetic_source_fixture_matches': contacts,
               'printed_contact_values': False,
               'scope': 'Owned-packet structural minimization and scoped email-pattern check; not exhaustive secret detection, arbitrary-code security, or remediation of a remote file'}
    (HERE / 'privacy_results.json').write_text(json.dumps(privacy, indent=2) + '\n')
    old004 = ROOT / 'researcher040282-cycle004-complex-ema.zip'
    protected004 = ['2026-09-04_researcher040282_004_complex-ema.md']
    protected004 += ['cycle_004/' + name for name in ('GateFoundations.lean', 'FreezeCore.lean',
                    'GateProposalBridge.lean', 'CoherenceEMA.lean', 'CoherenceDriveBridge.lean',
                    'check_cycle.py', 'compare_source.py')]
    with zipfile.ZipFile(old004) as archive:
        for name in protected004:
            require((ROOT / name).read_bytes() == archive.read('researcher_040282/' + name),
                    'Protected004 source/report changed: ' + name)
    protected005 = 0
    with zipfile.ZipFile(ROOT / 'researcher040282-cycle005-review-response.zip') as archive:
        for name in archive.namelist():
            relative = name.removeprefix('researcher_040282/')
            if relative.startswith('cycle_005/') or relative in {
                '2026-11-08_researcher040282_005_review-response.md',
                '2026-11-08_researcher040282_004_addendum.md'}:
                require((ROOT / relative).is_file() and (ROOT / relative).read_bytes() == archive.read(name),
                        'Delivered005 evidence changed: ' + relative)
                protected005 +=1
    require((HERE / 'prior_context/pasted_source_AUDIT-REPORT.md').read_bytes() ==
            Path('/home/user/aief_audit/AUDIT-REPORT.md').read_bytes(), 'Historical prior-context copy changed')
    for name in ('README.md', 'WORKFLOW.md', 'RESEARCH_QUEUE.md'):
        text = (ROOT / name).read_text()
        require('006' in text and '007' in text, 'Root navigation stale: ' + name)
    index = json.loads((ROOT / 'EVIDENCE_INDEX.json').read_text())
    require(index['ledger_rows'] ==111 and index['archive_only_ledger_references'] ==0,
            'Evidence index mismatch')
    for item in index['ledger_evidence']:
        require(item['availability'] == 'UNPACKED' and item['packet_members'], 'Archive-only/unavailable citation')
        for member in item['packet_members']:
            require((ROOT.parent / member).is_file(), 'Missing unpacked citation: ' + member)
    return {'current_ledger_rows':111, 'completed004_rows':108, 'completed005_rows':109,
            'prior109_rows_preserved':True, 'formal_labels_unchanged':94,
            'original_and_extracted_normal_optimized_runs_observed_successful':True,
            'all_six_scientific_result_groups_agree':True,
            'critical_inline_files_equal_actual_extracted_sources':7,
            'verified_source_acquisition_files_unchanged':verified,
            'upstream_dependency_modules_unchanged_each_run':12,
            'preregistered_science_preserved_admin_notice_post_execution':True,
            'protected004_critical_files':len(protected004),
            'delivered005_evidence_files_preserved':protected005,
            'all_ten_branch_records_minimal':True,
            'unclassified_outgoing_email_pattern_matches':0,
            'intentionally_synthetic_fixture_addresses_distinguished':2,
            'ledger_reference_count':index['unique_ledger_references'],
            'unpacked_log_count':index['unpacked_log_count'],
            'all_ledger_references_unpacked':True,
            'scope':'Local owned-packet consistency and scoped privacy hygiene; not scientific reexecution, independent approval, arbitrary-code security, real S01 or project freeze'}


def verify_archive():
    expected = {'researcher_040282/' + str(path.relative_to(ROOT)): path for path in builder.selected_files()}
    with zipfile.ZipFile(builder.ARCHIVE) as archive:
        names = archive.namelist()
        require(archive.testzip() is None and len(names) == len(set(names)), 'CRC/duplicate archive member failure')
        require(set(names) == set(expected), 'Archive/workspace file selection mismatch')
        contents = []
        for name, path in expected.items():
            data = archive.read(name)
            require(data == path.read_bytes(), 'Archive member differs from workspace: ' + name)
            contents.append((name.removeprefix('researcher_040282/'), data))
        inspect_contact_patterns(contents)
    return len(expected)


def main():
    builder.build_report()
    builder.build_indices()
    result = preflight()
    builder.package()
    verify_archive()
    result.update({'zip_crc_verified':True,'all_members_match_selected_workspace_files':True,
                   'receipt_included_and_final_archive_reverified':True})
    (HERE / 'packet_validation.json').write_text(json.dumps(result, indent=2) + '\n')
    builder.package()
    verify_archive()
    state_path = ROOT / 'STATE.json'
    state = json.loads(state_path.read_text())
    state['handoff_status'] = 'LOCAL_PACKET_CLOSURE_VERIFIED;NOT_UPLOADED'
    state_path.write_text(json.dumps(state, indent=2) + '\n')
    builder.package()
    try:
        members = verify_archive()
        preflight()
        # Preflight writes an identical deterministic privacy receipt; verify that too.
        verify_archive()
    except Exception:
        state['handoff_status'] = 'PACKET_CLOSURE_RECHECK_FAILED;DO_NOT_DELIVER'
        state_path.write_text(json.dumps(state, indent=2) + '\n')
        raise
    print(json.dumps({'validation':result, 'final_archive_members':members,
                      'final_archive_bytes':builder.ARCHIVE.stat().st_size,
                      'standalone_report_bytes':builder.REPORT.stat().st_size}, indent=2))


if __name__ == '__main__':
    main()
