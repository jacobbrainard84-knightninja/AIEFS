from pathlib import Path
import sys
src = Path(sys.argv[1]).read_text(encoding='utf-8')
out = Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
mutations = {
  'Sign': ('if k = 0 then (1 - dt * row n B i) * v 0 i + dt * ∑ j, B i j * v d j',
           'if k = 0 then (1 - dt * row n B i) * v 0 i - dt * ∑ j, B i j * v d j'),
  'Threshold': ('(hrow : ∀ i, dt * row n B i ≤ 1) (_hM : 0 ≤ M)',
                '(hrow : ∀ i, dt * row n B i ≤ 2) (_hM : 0 ≤ M)'),
  'Nonnegative': ('(v : ℕ → Fin n → ℝ) (hdt : 0 ≤ dt) (hB : ∀ i j, 0 ≤ B i j)\n    (hrow',
                  '(v : ℕ → Fin n → ℝ) (hdt : 0 ≤ dt) (hB : ∀ i j, 0 ≤ B i j ∨ B i j < 0)\n    (hrow'),
}
for name, (old, new) in mutations.items():
    if name == 'Sign':
        assert src.count(old) == 1
    elif name == 'Threshold':
        assert src.count(old) == 1
    else:
        assert src.count(old) == 2
    (out / f'HeteroMutant{name}.lean').write_text(src.replace(old, new, 1), encoding='utf-8')
    print(name, 'generated')
