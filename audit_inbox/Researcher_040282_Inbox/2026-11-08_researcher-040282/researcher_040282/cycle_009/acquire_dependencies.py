"""Static local Python import acquisition for the reviewed candidate; no imports."""
import ast
import hashlib
import json
from pathlib import Path
from urllib.parse import quote
import urllib.request

HERE = Path(__file__).resolve().parent
STATE = HERE / 'source_state'
PLATFORM = 'AIEF_Experiments/aief_modular_platform_v1_analysis_v4'
CANDIDATE = PLATFORM + '/AIEF_1_4_Twindow_sensitivity_analysis_v4_1.py'


def main():
    branch = json.loads((STATE / 'main_branch.json').read_text())
    commit = branch['commit']
    tree = json.loads((STATE / 'main_tree.json').read_text())
    files = {item['path']: item for item in tree['tree'] if item['type'] == 'blob'}
    selected = json.loads((STATE / 'main_selected.json').read_text())
    records = {item['path']: item for item in selected['files']}
    def locate(stem):
        for result in (stem + '.py', stem + '/__init__.py'):
            if result in files:
                return result
        return None
    def absolute(name):
        stem = name.replace('.', '/')
        return locate(PLATFORM + '/' + stem) or locate(stem)
    pending = [CANDIDATE]
    graph = {}
    while pending:
        path = pending.pop()
        if path in graph:
            continue
        target = STATE / 'main' / path
        if target.exists():
            data = target.read_bytes()
        else:
            url = 'https://raw.githubusercontent.com/jacobbrainard84-knightninja/AIEFS/' + commit + '/' + quote(path, safe='/')
            request = urllib.request.Request(url, headers={'User-Agent': 'Researcher-040282-read-only'})
            with urllib.request.urlopen(request, timeout=60) as response:
                data = response.read()
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        if blob != files[path]['sha']:
            raise RuntimeError('Dependency differs from acquired current tree: ' + path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        records[path] = {'path': path, 'blob': blob, 'bytes': len(data)}
        dependencies = set()
        for node in ast.walk(ast.parse(data, filename=path)):
            names = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
                for name in names:
                    found = absolute(name)
                    if found:
                        dependencies.add(found)
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    base = Path(path).parent
                    for _ in range(node.level - 1):
                        base = base.parent
                    stem = str(base / node.module.replace('.', '/')) if node.module else str(base)
                    found = locate(stem)
                    if found:
                        dependencies.add(found)
                    if not node.module:
                        for alias in node.names:
                            found = locate(str(base / alias.name))
                            if found:
                                dependencies.add(found)
                elif node.module:
                    found = absolute(node.module)
                    if found:
                        dependencies.add(found)
        for dependency in list(dependencies) + [path]:
            parent = Path(dependency).parent
            while str(parent) not in ('.', PLATFORM):
                init = str(parent / '__init__.py')
                if init in files and init != path:
                    dependencies.add(init)
                parent = parent.parent
        graph[path] = sorted(dependencies - {path})
        pending.extend(graph[path])
    selected['files'] = [records[name] for name in sorted(records)]
    selected['fetched_and_verified'] = len(records)
    selected['dependency_note'] = 'Initial9 selected main files plus STATIC verified Python import closure; no source imports'
    (STATE / 'main_selected.json').write_text(json.dumps(selected, indent=2) + '\n')
    proposal = HERE / 'proposal'
    proposal.mkdir(exist_ok=True)
    manifest = {'repo': 'jacobbrainard84-knightninja/AIEFS', 'commit': commit,
                'candidate': CANDIDATE, 'platform': PLATFORM,
                'modules': [records[name] for name in sorted(graph)],
                'authority_metadata': [records[name] for name in ('registry/artifacts_current.csv','runs/b57562a8ee77/manifest.json')],
                'authority': {'artifact_id':'ART-2217','inventory':'registry/artifacts_current.csv',
                              'manifest':'runs/b57562a8ee77/manifest.json',
                              'scope':'METADATA_ONLY;not genuine S01 input validation or authority issuance'}}
    (proposal / 'source_modules.json').write_text(json.dumps(manifest, indent=2) + '\n')
    result = {'commit': commit, 'verified_modules': len(graph), 'main_selected_total': len(records),
              'import_graph': graph, 'code_executed_by_acquisition_helper': False}
    (HERE / 'dependency_acquisition.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
