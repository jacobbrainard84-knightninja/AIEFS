"""Extract the ten named critical010 files. No execution or fetching."""
import argparse
import json
from pathlib import Path
import re

NAMES={'HistoryBuffer.lean','step_contract.py','check_engine.py','load_reviewed.py','check_lean.py',
       'prepare_lean.py','run_checks.py','source_modules.json','fetch_public_dependencies.py','extract_from_report.py'}
PATTERN=re.compile(r'<!-- BEGIN_CRITICAL_FILE: ([^>\n]+) -->\n```[^\n]*\n(.*?)\n```\n'
                   r'<!-- END_CRITICAL_FILE: \1 -->',re.S)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('report',type=Path);parser.add_argument('output',type=Path)
    args=parser.parse_args();pairs=PATTERN.findall(args.report.read_text())
    if len(pairs)!=len(NAMES) or {name for name,_ in pairs}!=NAMES:raise RuntimeError('Missing/duplicate/unexpected critical file')
    args.output.mkdir(parents=True,exist_ok=True)
    for name,body in pairs:
        if Path(name).name!=name:raise RuntimeError('Unsafe extraction path')
        target=args.output/name;text=body+'\n'
        if target.exists() and target.read_text()!=text:raise RuntimeError('Existing different file: '+name)
        target.write_text(text)
    print(json.dumps({'critical_files_extracted':len(pairs),'code_executed':False},indent=2))


if __name__=='__main__':main()
