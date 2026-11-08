"""Build owned007 standalone note/optional packet; execute no upstream code."""
from pathlib import Path
import argparse
import csv
import json
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPORT = ROOT / '2026-09-04_researcher040282_007_complex-nan-comparator.md'
ARCHIVE = ROOT / 'researcher040282-cycle007-complex-nan-comparator.zip'
CRITICAL = ('componentwise_exact.py', 'comparison_contract.py', 'load_reviewed.py',
            'test_comparison_contract.py', 'run_checks.py', 'source_modules.json',
            'fetch_public_dependencies.py', 'extract_from_report.py')


def fence(text, language='text'):
    return '```' + language + '\n' + text.rstrip('\n') + '\n```\n'


def build_report():
    text = (HERE / 'REPORT_BODY.md').read_text()
    blocks = []
    for name in CRITICAL:
        blocks.append('### ' + name + '\n\n<!-- BEGIN_CRITICAL_FILE: ' + name + ' -->\n' +
                      fence((HERE / 'proposal' / name).read_text(),
                            'json' if name.endswith('.json') else 'python') +
                      '<!-- END_CRITICAL_FILE: ' + name + ' -->\n')
    text = text.replace('{{CRITICAL_FILES}}', '\n'.join(blocks))
    text = text.replace('{{RESULTS}}', fence((HERE / 'checks/cycle_results.json').read_text(), 'json'))
    records = []
    for name in ('PLAN.md', 'proposal/INTEGRATION_NOTE.md', 'review_decision.json', 'historical_restoration.json'):
        records.append('### ' + name + '\n\n' + fence((HERE / name).read_text(),
                       'json' if name.endswith('.json') else 'text'))
    text = text.replace('{{RECORDS}}', '\n'.join(records))
    receipt = HERE / 'standalone_reproduction.json'
    if receipt.exists():
        status = json.loads(receipt.read_text())
        if not status['actually_executed'] or status['runner_returncode'] !=0:
            raise RuntimeError('Incomplete extracted reproduction')
        value = ('**Actually executed.** Eight critical files were extracted byte-for-byte; '
                 'two public dependency files were freshly fetched/verified. The extracted '
                 'runner returned0 after repeating all original/candidate/modular normal/-O '
                 'contracts and both mutant modes. Scientific summaries and per-target '
                 'non-timing results match the original run. This is submitter-local '
                 'self-reproduction, not independent-seat confirmation.\n\n' +
                 fence(json.dumps(status, indent=2), 'json'))
    else:
        value = '**PROVISIONAL: extracted-code rerun not executed yet. Do not deliver this draft.**'
    text = text.replace('{{STANDALONE}}', value)
    if any(tag in text for tag in ('{{STANDALONE}}', '{{CRITICAL_FILES}}', '{{RESULTS}}', '{{RECORDS}}')):
        raise RuntimeError('Unexpanded assembly field')
    REPORT.write_text(text)
    print('Report written:', REPORT.name, 'bytes', REPORT.stat().st_size)


def selected_files():
    extensions = {'.md', '.csv', '.json', '.py', '.lean', '.log', '.sh', '.txt', '.yml', '.yaml'}
    excluded = {'__pycache__', '.cache', '.git', 'node_modules', '.venv'}
    files = []
    for path in ROOT.rglob('*'):
        if not path.is_file() or path.is_symlink() or path.suffix not in extensions:
            continue
        relative = path.relative_to(ROOT)
        if excluded.intersection(relative.parts) or path.name == 'REPORT_BODY.md':
            continue
        files.append(path)
    return sorted(files)


def build_indices():
    with (ROOT / 'CLAIM_LEDGER.csv').open(newline='') as stream:
        ledger = list(csv.DictReader(stream))
    selected = {str(path.relative_to(ROOT)): path for path in selected_files()}
    references = sorted({value.strip() for row in ledger
                         for value in row['evidence_files'].split(';') if value.strip()})
    records = []
    for reference in references:
        path = ROOT / reference
        if path.is_file():
            members = [reference] if reference in selected else []
        elif path.is_dir():
            members = sorted(name for name in selected if name.startswith(reference.rstrip('/') + '/'))
        else:
            members = []
        if not members:
            raise FileNotFoundError('Missing unpacked evidence: ' + reference)
        records.append({'referenced_as': reference, 'availability': 'UNPACKED',
                        'packet_members': ['researcher_040282/' + name for name in members]})
    logs = sorted(name for name in selected if name.endswith('.log'))
    index = {'ledger_rows': len(ledger), 'completed004_rows': 108, 'completed005_rows': 109, 'completed006_rows': 111,
             'unique_ledger_references': len(references), 'all_ledger_references_unpacked': True,
             'archive_only_ledger_references': 0, 'unpacked_log_count': len(logs),
             'log_packet_members': ['researcher_040282/' + name for name in logs],
             'ledger_evidence': records,
             'note': 'Historical ZIPs are not nested. Their cited logs are preserved unpacked. Old closure records concern their frozen cycle, not the current root.'}
    (ROOT / 'EVIDENCE_INDEX.json').write_text(json.dumps(index, indent=2) + '\n')
    rows = []
    for old in sorted(ROOT.glob('*.zip')):
        if old == ARCHIVE:
            continue
        with zipfile.ZipFile(old) as archive:
            for member in archive.namelist():
                if not member.endswith('.log'):
                    continue
                prefix = 'researcher_040282/'
                if not member.startswith(prefix):
                    raise RuntimeError('Unexpected historical log root')
                relative = member[len(prefix):]
                if relative not in selected or selected[relative].read_bytes() != archive.read(member):
                    raise RuntimeError('Historical log not preserved unpacked: ' + member)
                rows.append({'historical_archive': old.name, 'historical_log_member': member,
                             'now_unpacked_at': member, 'content_matches_historical_member': 'TRUE',
                             'archive_only_in_this_handoff': 'FALSE'})
    with (ROOT / 'HISTORICAL_ARCHIVE_LOG_MAP.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['historical_archive', 'historical_log_member',
                                'now_unpacked_at', 'content_matches_historical_member',
                                'archive_only_in_this_handoff'])
        writer.writeheader()
        writer.writerows(rows)
    print('Index:', len(references), 'references,', len(logs), 'unpacked logs,', len(rows), 'historical log mappings')


def package():
    build_indices()
    files = selected_files()
    with zipfile.ZipFile(ARCHIVE, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            archive.write(path, 'researcher_040282/' + str(path.relative_to(ROOT)))
    print('Package written:', ARCHIVE.name, 'files', len(files), 'bytes', ARCHIVE.stat().st_size)



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', action='store_true')
    args = parser.parse_args()
    build_report()
    if args.package:
        package()


if __name__ == '__main__':
    main()
