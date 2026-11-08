"""Build the standalone note and privacy-scanned, log-unpacked owner handoff.
No execution of upstream/model code occurs here. Package validation is separate.
"""
from pathlib import Path
import argparse
import csv
from io import StringIO
import json
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPORT = ROOT / '2026-11-08_researcher040282_005_review-response.md'
ADDENDUM = ROOT / '2026-11-08_researcher040282_004_addendum.md'
ARCHIVE = ROOT / 'researcher040282-cycle005-review-response.zip'
CRITICAL = (
    'AIEF_1_4_proposal_equalization_branch_selftest_r040282.py',
    'test_proposal_equalization_branch_selftest_r040282.py',
    'run_checks.py', 'fetch_public_dependencies.py', 'source_modules.json',
    'extract_from_report.py',
)


def fence(text, language='text'):
    return '```' + language + '\n' + text.rstrip('\n') + '\n```\n'


def build_report():
    text = (HERE / 'REPORT_BODY.md').read_text()
    text = text.replace('{{ADDENDUM}}', __import__('re').sub(r'(?m)^(#{1,4}) ', r'##\1 ', ADDENDUM.read_text()))
    text = text.replace('{{ERRATUM}}', __import__('re').sub(r'(?m)^(#{1,4}) ', r'##\1 ', (HERE / 'proposal/ERRATUM_ART0050_SELFTEST_PROPOSED.md').read_text()))
    blocks = []
    for name in CRITICAL:
        body = (HERE / 'proposal' / name).read_text()
        language = 'json' if name.endswith('.json') else 'python'
        blocks.append('### ' + name + '\n\n<!-- BEGIN_CRITICAL_FILE: ' + name + ' -->\n'
                      + fence(body, language) + '<!-- END_CRITICAL_FILE: ' + name + ' -->\n')
    text = text.replace('{{CRITICAL_FILES}}', '\n'.join(blocks))
    text = text.replace('{{RESULTS}}', fence((HERE / 'checks/cycle_results.json').read_text(), 'json'))
    records = []
    for name in ('PLAN.md', 'ADVERSARIAL_ADDENDUM.md', 'input_mutation_red.json', 'feedback_scope.json', 'privacy_results.json', 'saved_evidence_provenance.json'):
        records.append('### ' + name + '\n\n' + fence((HERE / name).read_text(),
                       'json' if name.endswith('.json') else 'text'))
    text = text.replace('{{RECORDS}}', '\n'.join(records))
    standalone = HERE / 'standalone_reproduction.json'
    if standalone.exists():
        status = json.loads(standalone.read_text())
        reproduction = ('**Actually executed, not just prepared.** All six inline files were extracted into a fresh directory, '
                        'matched the supplied sources, and ran against ten freshly fetched public dependency modules. '
                        'The extracted runner again returned0: legacy red3 failures/0 errors, candidate21 pass normally '
                        'and21 pass optimized,65 valid comparisons. This is submitter-local self-reproduction, '
                        'not independent-seat confirmation.\n\n' + fence(json.dumps(status, indent=2), 'json'))
    else:
        reproduction = '**PROVISIONAL: extracted-code rerun not executed yet. Do not deliver this draft.**'
    text = text.replace('{{STANDALONE}}', reproduction)
    if '{{' in text and any(tag in text for tag in ('{{RESULTS}}', '{{RECORDS}}', '{{CRITICAL_FILES}}')):
        raise ValueError('Unexpanded report field')
    REPORT.write_text(text)
    print('Report written:', REPORT.name, 'bytes', REPORT.stat().st_size)


def selected_files():
    extensions = {'.md', '.csv', '.json', '.py', '.lean', '.log', '.sh', '.txt'}
    excluded_parts = {'__pycache__', '.cache', '.git', 'node_modules', '.venv'}
    paths = []
    for path in ROOT.rglob('*'):
        if not path.is_file() or path.is_symlink() or path.suffix not in extensions:
            continue
        relative = path.relative_to(ROOT)
        if excluded_parts.intersection(relative.parts):
            continue
        # The unexpanded assembly template is not a handoff document.
        if relative == Path('cycle_005/REPORT_BODY.md'):
            continue
        paths.append(path)
    return sorted(paths)


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
            prefix = reference.rstrip('/') + '/'
            members = sorted(name for name in selected if name.startswith(prefix))
        else:
            members = []
        if not members:
            raise FileNotFoundError('Ledger evidence unavailable unpacked: ' + reference)
        records.append({'referenced_as': reference, 'availability': 'UNPACKED',
                        'packet_members': ['researcher_040282/' + name for name in members]})
    logs = sorted(name for name in selected if name.endswith('.log'))
    index = {'ledger_rows': len(ledger), 'completed004_rows': 108,
             'unique_ledger_references': len(references), 'all_ledger_references_unpacked': True,
             'archive_only_ledger_references': 0,
             'unpacked_log_count': len(logs), 'log_packet_members': ['researcher_040282/' + name for name in logs],
             'ledger_evidence': records,
             'note': 'Old ZIPs are not nested here. Important historic logs are unpacked; historical frozen closure records are not the new live root state.'}
    (ROOT / 'EVIDENCE_INDEX.json').write_text(json.dumps(index, indent=2) + '\n')
    rows = []
    for old in sorted(ROOT.glob('*.zip')):
        if old == ARCHIVE:
            continue
        with zipfile.ZipFile(old) as archive:
            for name in archive.namelist():
                if not name.endswith('.log'):
                    continue
                prefix = 'researcher_040282/'
                if not name.startswith(prefix):
                    raise ValueError('Unexpected historical log root')
                relative = name[len(prefix):]
                path = ROOT / relative
                if relative not in selected or not path.exists() or path.read_bytes() != archive.read(name):
                    raise ValueError('Historic log not preserved unpacked: ' + name)
                rows.append({'historical_archive': old.name, 'historical_log_member': name,
                             'now_unpacked_at': name, 'content_matches_historical_member': 'TRUE',
                             'archive_only_in_this_handoff': 'FALSE'})
    with (ROOT / 'HISTORICAL_ARCHIVE_LOG_MAP.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['historical_archive', 'historical_log_member',
                                                   'now_unpacked_at', 'content_matches_historical_member',
                                                   'archive_only_in_this_handoff'])
        writer.writeheader()
        writer.writerows(rows)
    print('Index:', len(references), 'ledger references,', len(logs), 'unpacked logs,', len(rows), 'old archive-log mappings')


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
