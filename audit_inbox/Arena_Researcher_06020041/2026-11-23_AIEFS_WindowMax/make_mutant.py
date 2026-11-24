from pathlib import Path
import sys

source = Path(sys.argv[1]).read_text(encoding='utf-8')
old = 'if k = 0 then (1 - ((n : ℝ) - 1) * c) * v 0 - c * v d else v (k - 1)'
new = 'if k = 0 then (1 - ((n : ℝ) - 1) * c) * v 0 + c * v d else v (k - 1)'
assert source.count(old) == 1
Path(sys.argv[2]).write_text(source.replace(old, new), encoding='utf-8')
