"""Finite test only: grid in c and integer powers of the 2x2 model."""
import numpy as np
best = (0.0, None, None)
for c in np.arange(1, 1000) / 1000:
    matrix = np.array([[1 - 2*c, -c], [1., 0.]])
    power = np.eye(2)
    for k in range(1, 101):
        power = power @ matrix
        gain = float(np.linalg.norm(power, 2))
        if gain > best[0]:
            best = (gain, float(c), k)
print('c grid: 0.001 through 0.999, step 0.001; k=1 through 100')
print('largest observed norm:', best[0], 'at c=', best[1], 'k=', best[2])
print('proposed all-step threshold sqrt(21/8):', np.sqrt(21/8))
print('finite-grid threshold:', 'PASS' if best[0] <= np.sqrt(21/8) else 'FAIL')
print('This grid does not prove the all-step or continuum claim.')
