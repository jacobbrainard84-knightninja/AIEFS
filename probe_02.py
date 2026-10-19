# Run this to check:
import json
import AIEF_1_4_memory_ablation_updated as prod

with open('runs/5a9f093a2fe0/manifest.json') as f:
    manifest = json.load(f)

model = manifest['model']
print(f"N: frozen={model['N']}, prod={prod.N}")
print(f"dt: frozen={model['dt']}, prod={prod.DT}")
print(f"T_window: frozen={model['T_window']}, prod={prod.T_WINDOW}")
print(f"omega match: {np.allclose(model['omega'], prod.OMEGA)}")
