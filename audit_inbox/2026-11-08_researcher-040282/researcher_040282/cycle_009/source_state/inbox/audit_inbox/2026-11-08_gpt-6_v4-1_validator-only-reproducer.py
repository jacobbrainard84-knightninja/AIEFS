#!/usr/bin/env python3
"""Self-contained launcher for the v4.1 validator-only forged-cohort test.

Run without arguments to execute the expanded source-copy harness, or pass
--extract PATH to write the readable source after checking its SHA-256.
"""
import base64, hashlib, sys, zlib
from pathlib import Path
EXPECTED_SHA256 = "cab5c2ad4cd8d2a6600fb56294e96d537b355d16bc29bffce70c724fbd448b5e"
PAYLOAD = (
    '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'
    'mkzenV88fFXYU9sj4f+DQomO'
)
source = zlib.decompress(base64.b64decode("".join(PAYLOAD).encode("ascii")))
observed = hashlib.sha256(source).hexdigest()
if observed != EXPECTED_SHA256:
    raise SystemExit(f"expanded source hash mismatch: {observed}")
if len(sys.argv) == 3 and sys.argv[1] == "--extract":
    target = Path(sys.argv[2]); target.write_bytes(source)
    print(f"EXTRACTED={target}"); print(f"EXPANDED_SOURCE_SHA256={observed}")
elif len(sys.argv) == 1:
    exec(compile(source, "AIEFS_Part2_v41_forged_cohort_reproducer.py", "exec"),
         {"__name__": "__main__", "__file__": "AIEFS_Part2_v41_forged_cohort_reproducer.py"})
else:
    raise SystemExit("usage: reproducer.py [--extract PATH]")
