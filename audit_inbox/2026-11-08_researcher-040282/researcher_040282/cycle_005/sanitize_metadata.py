"""Minimize branch acquisition metadata; never print/back up removed values.

Also drop contact/signature fields when their values do not match an email
pattern. Historical scientific source/log content is not changed. Previously
recorded removal counts are retained without retaining the removed content.
"""
from pathlib import Path
from io import BytesIO
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parent.parent
EMAIL = re.compile(rb"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
SAFE_KEYS = {'branch', 'commit', 'metadata_policy'}


def is_branch_metadata(name):
    path = Path(name)
    return path.suffix == '.json' and 'source_state' in path.parts and '_branch' in path.stem


def minimal(data):
    value = json.loads(data)
    commit = value.get('commit')
    if isinstance(commit, dict):
        commit = commit.get('sha')
    if not isinstance(commit, str) or not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise ValueError('Expected acquisition identifier; input payload not printed')
    safe = {'branch': value.get('branch', value.get('name', 'main')),
            'commit': commit,
            'metadata_policy': 'author/committer/contact/signature payload omitted'}
    result = (json.dumps(safe, indent=2) + '\n').encode()
    if EMAIL.search(result):
        raise ValueError('Unexpected contact-like content in minimized identifiers')
    return result


def clean_zip(data, prefix=''):
    stream = BytesIO()
    changes = []
    with zipfile.ZipFile(BytesIO(data)) as source, zipfile.ZipFile(stream, 'w') as dest:
        if source.testzip() is not None:
            raise ValueError('Input archive CRC failure')
        for entry in source.infolist():
            content = source.read(entry.filename)
            name = prefix + entry.filename
            if is_branch_metadata(entry.filename):
                cleaned = minimal(content)
                if cleaned != content:
                    changes.append({'member': name, 'removed_contact_matches': len(EMAIL.findall(content)),
                                    'contact_and_signed_payload_fields_dropped': True})
                    content = cleaned
            elif entry.filename.lower().endswith('.zip'):
                content, nested = clean_zip(content, name + '!/')
                changes.extend(nested)
            dest.writestr(entry, content)
    result = stream.getvalue()
    with zipfile.ZipFile(BytesIO(result)) as check:
        if check.testzip() is not None:
            raise ValueError('Repacked archive CRC failure')
    return (result if changes else data), changes


def main():
    target = Path(__file__).resolve().parent / 'privacy_results.json'
    previous = json.loads(target.read_text()) if target.exists() else {}
    files = {item['path']: item for item in previous.get('files', [])}
    archives = {item['path']: item for item in previous.get('archives', [])}
    for path in sorted(ROOT.rglob('*.json')):
        if not is_branch_metadata(str(path)):
            continue
        data = path.read_bytes()
        cleaned = minimal(data)
        if data != cleaned:
            name = str(path.relative_to(ROOT))
            record = files.get(name, {'path': name, 'removed_contact_matches': 0})
            record['removed_contact_matches'] += len(EMAIL.findall(data))
            record['contact_and_signed_payload_fields_dropped'] = True
            record['scope'] = 'reported contact-bearing file' if record['removed_contact_matches'] else 'additional legacy inbox metadata: structural cleanup even without pattern matches'
            files[name] = record
            path.write_bytes(cleaned)
    for path in sorted(ROOT.rglob('*.zip')):
        content, changes = clean_zip(path.read_bytes())
        if changes:
            path.write_bytes(content)
            archives[str(path.relative_to(ROOT))] = {'path': str(path.relative_to(ROOT)),
                                                     'changed_members': changes, 'crc_ok': True}
    leftovers, nonminimal = [], []
    for path in sorted(ROOT.rglob('*.json')):
        if not is_branch_metadata(str(path)):
            continue
        data = path.read_bytes()
        if EMAIL.search(data):
            leftovers.append(str(path.relative_to(ROOT)))
        if set(json.loads(data)) != SAFE_KEYS:
            nonminimal.append(str(path.relative_to(ROOT)))
    if leftovers or nonminimal:
        raise ValueError('Branch metadata privacy/structural check failed; no payload values printed')
    # Original reported main-file count remains3; other inbox branch records also
    # had author/contact/signature keys and are minimized regardless of patterns.
    report = {'policy': 'minimal acquisition identifiers only; no removed values or unredacted backups retained',
              'scientific_sources_changed': False, 'remote_files_changed': False,
              'files': [files[k] for k in sorted(files)], 'archives': [archives[k] for k in sorted(archives)],
              'reported_contact_bearing_files_minimized': sum(x['removed_contact_matches'] > 0 for x in files.values()),
              'additional_legacy_inbox_metadata_minimized': sum(x['removed_contact_matches'] == 0 for x in files.values()),
              'branch_metadata_contact_matches_remaining': 0,
              'branch_metadata_nonminimal_records_remaining': 0,
              'pattern_scan_limit': 'A pattern-only scan is insufficient: author/contact/signed payload fields are structurally dropped too'}
    target.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
