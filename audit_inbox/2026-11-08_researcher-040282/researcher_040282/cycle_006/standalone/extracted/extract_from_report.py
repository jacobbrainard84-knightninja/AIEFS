"""Extract seven named text files from the owned006 standalone audit.
Does not import/run code, fetch dependencies, or sandbox arbitrary submissions.
"""
import argparse
import json
from pathlib import Path
import re

NAMES = {'audit_v41.py', 'reference_contract.py', 'load_upstream.py',
         'ESTIMAND_CONTRACT.json', 'source_modules.json',
         'fetch_public_dependencies.py', 'extract_from_report.py'}
PATTERN = re.compile(r'<!-- BEGIN_CRITICAL_FILE: ([^>\n]+) -->\n```[^\n]*\n(.*?)\n```\n'
                     r'<!-- END_CRITICAL_FILE: \1 -->', re.S)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    pairs = PATTERN.findall(args.report.read_text())
    if len(pairs) != len(NAMES) or {name for name, _ in pairs} != NAMES:
        raise ValueError('Missing/duplicate/unexpected critical-file blocks')
    args.output.mkdir(parents=True, exist_ok=True)
    for name, content in pairs:
        if Path(name).name != name:
            raise ValueError('Unexpected extraction path')
        text = content + '\n'
        target = args.output / name
        if target.exists() and target.read_text() != text:
            raise ValueError('Existing different extracted file: ' + name)
        target.write_text(text)
    print(json.dumps({'critical_files_extracted': len(pairs), 'code_executed': False}, indent=2))


if __name__ == '__main__':
    main()
