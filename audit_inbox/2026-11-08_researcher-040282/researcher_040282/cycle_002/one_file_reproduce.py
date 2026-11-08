"""Extract and actually rerun the two critical blocks from the standalone note.

The checker run sees only those extracted files and the public Lean/Mathlib
installation, not the original research Python/Lean source directory.
"""
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

CYCLE = Path(__file__).resolve().parent
NAME = '2026-11-07_researcher040282_002_guarded-capacity-lean.md'
REPORT = CYCLE.parent / NAME
CACHE = Path(os.environ.get('R040282_CACHE', Path.home() / '.cache/researcher040282')).expanduser().resolve()


def main():
    for name in ['standalone_results.json', 'standalone_manifest.json']:
        (CYCLE / name).unlink(missing_ok=True)
    note = REPORT.read_text()
    pattern = r"<!-- FILE: (GateFoundations\.lean|check_cycle\.py) -->\n```[^\n]*\n(.*?)\n```"
    matches = re.findall(pattern, note, re.S)
    assert len(matches) == 2
    blocks = dict(matches)
    assert set(blocks) == {'GateFoundations.lean', 'check_cycle.py'}
    CACHE.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='r040282-standalone-', dir=CACHE) as tmp:
        out = Path(tmp)
        for name, content in blocks.items():
            (out / name).write_text(content + '\n')
        same = all((out / name).read_bytes() == (CYCLE / name).read_bytes() for name in blocks)
        assert same, 'Inline source and supplied files must match exactly'
        env = os.environ.copy()
        env['R040282_CACHE'] = str(CACHE)
        env['R040282_MATHLIB'] = str(Path(env.get('R040282_MATHLIB', CACHE / 'mathlib4')).expanduser().resolve())
        env['R040282_LEAN_BIN'] = str(Path(env.get('R040282_LEAN_BIN', CACHE / 'lean-4.33.1-linux/bin/lean')).expanduser().absolute())
        env['PYTHONDONTWRITEBYTECODE'] = '1'
        print('Running files extracted from the standalone Markdown.', flush=True)
        run = subprocess.run([sys.executable, str(out / 'check_cycle.py')], cwd=out, env=env,
                             text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=600)
        (CYCLE / 'standalone_reproduction.log').write_text(run.stdout)
        print(run.stdout, end='', flush=True)
        assert run.returncode == 0, f'Standalone runner exited {run.returncode}'
        result = json.loads((out / 'cycle_results.json').read_text())
        assert result['control_count'] == 9 and result['all_controls_passed'] is True
        assert result['source_sha256'] == hashlib.sha256((out / 'GateFoundations.lean').read_bytes()).hexdigest()
        assert result['harness_sha256'] == hashlib.sha256((out / 'check_cycle.py').read_bytes()).hexdigest()
        shutil.copyfile(out / 'cycle_results.json', CYCLE / 'standalone_results.json')
        destination = CYCLE / 'standalone_checks'
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(out / 'checks', destination)
    manifest = {
        'report': NAME,
        'extraction': 'Exactly the two allowlisted inline FILE blocks; no original source used for execution',
        'critical_files': sorted(blocks),
        'code_blocks_match_workspace': same,
        'runner_exit': run.returncode,
        'control_count': result['control_count'],
        'all_controls_passed': result['all_controls_passed'],
        'scope': 'Local self-reproduction only; no independent-seat approval or integration',
    }
    (CYCLE / 'standalone_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print('Single-file reproduction passed; evidence copied out of disposable directory.', flush=True)


if __name__ == '__main__':
    main()
