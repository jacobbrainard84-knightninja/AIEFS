"""Acquire only current-main local import closure; never import downloaded code.
Use public read-only raw content, Git-blob verification, and contact-free records.
"""
import ast
import hashlib
import json
from pathlib import Path
from urllib.parse import quote
import urllib.request

ROOT = Path(__file__).resolve().parent
STATE = ROOT / 'source_state'
SOURCE = STATE / 'main'
REPO = 'jacobbrainard84-knightninja/AIEFS'


def main():
    branch = json.loads((STATE / 'main_branch.json').read_text())
    commit = branch['commit']
    if commit != 'f3e3a57632c613e860a9941f007732cb4c2c91c6':
        raise RuntimeError('Preregistered source base changed; stop before execution')
    tree = json.loads((STATE / 'main_tree.json').read_text())
    files = {x['path']: x for x in tree['tree'] if x['type'] == 'blob'}
    selected = json.loads((STATE / 'main_selected.json').read_text())
    records = {x['path']: x for x in selected['files']}
    pending = ['AIEF_1_4_proposal_equalization_bridge_analysis.py',
               'AIEF_1_4_actual_admissibility_branch_audit.py']
    visited = set()
    graph = {}
    while pending:
        path = pending.pop()
        if path in visited:
            continue
        visited.add(path)
        target = SOURCE / path
        if target.exists():
            content = target.read_bytes()
        else:
            url = 'https://raw.githubusercontent.com/' + REPO + '/' + commit + '/' + quote(path, safe='/')
            request = urllib.request.Request(url, headers={'User-Agent': 'Researcher-040282-read-only'})
            with urllib.request.urlopen(request, timeout=60) as response:
                content = response.read()
        actual = hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest()
        if actual != files[path]['sha']:
            raise RuntimeError('Acquired dependency does not match pinned tree: ' + path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        records[path] = {'path': path, 'blob': actual, 'bytes': len(content)}
        modules = set()
        for node in ast.walk(ast.parse(content, filename=path)):
            if isinstance(node, ast.Import):
                modules.update(x.name for x in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules.add(node.module)
        deps = sorted({name.replace('.', '/') + '.py' for name in modules
                       if name.replace('.', '/') + '.py' in files})
        graph[path] = deps
        pending.extend(deps)
    selected['files'] = [records[k] for k in sorted(records)]
    selected['fetched_and_verified'] = len(records)
    selected['dependency_acquisition_note'] = 'Initial refresh log selected12; six bridge files then recursively verified local Python imports added. Counts here describe final acquired set.'
    (STATE / 'main_selected.json').write_text(json.dumps(selected, indent=2) + '\n')
    report = {'commit': commit, 'selected_files_total': len(records),
              'verified_local_import_modules': len(visited), 'import_graph': graph,
              'scope': 'Static local import closure; third-party installed packages separately recorded; downloaded code not imported by acquisition helper'}
    (ROOT / 'dependency_acquisition.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
