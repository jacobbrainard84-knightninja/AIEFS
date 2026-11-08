"""Extract the six named files from this OWNED standalone audit.

This extracts text only. It does not import or execute code, download anything,
or implement a general untrusted-code security boundary. Review the report and
public dependencies before running the extracted checks.
"""
import argparse
import json
from pathlib import Path
import re

NAMES = {
    'AIEF_1_4_proposal_equalization_branch_selftest_r040282.py',
    'test_proposal_equalization_branch_selftest_r040282.py',
    'run_checks.py', 'fetch_public_dependencies.py',
    'source_modules.json', 'extract_from_report.py',
}
PATTERN = re.compile(
    r'<!-- BEGIN_CRITICAL_FILE: ([^>\n]+) -->\n```[^\n]*\n(.*?)\n```\n'
    r'<!-- END_CRITICAL_FILE: \1 -->', re.S)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    matches = PATTERN.findall(args.report.read_text())
    if len(matches) != len(NAMES) or {name for name, _ in matches} != NAMES:
        raise ValueError('Missing, duplicate or unexpected critical-file blocks')
    args.output.mkdir(parents=True, exist_ok=True)
    for name, text in matches:
        if Path(name).name != name:
            raise ValueError('Unexpected output path')
        target = args.output / name
        content = text + '\n'
        if target.exists() and target.read_text() != content:
            raise ValueError('Existing different extracted file: ' + name)
        target.write_text(content)
    print(json.dumps({'critical_files_extracted': len(matches),
                      'code_executed_by_extractor': False}, indent=2))


if __name__ == '__main__':
    main()
