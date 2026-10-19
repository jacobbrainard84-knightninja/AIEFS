#!/usr/bin/env python3
"""Diagnose import issues for AIEF_1_4_matched_phase_memory_ablation.py"""

import sys
import traceback

print("=" * 70)
print("IMPORT DIAGNOSTIC")
print("=" * 70)

# Test 1: Can we import the script?
print("\n1. Testing script import...")
try:
    import AIEF_1_4_matched_phase_memory_ablation as script
    print(f"   ✓ Script imported from: {script.__file__}")
except Exception as e:
    print(f"   ✗ Failed to import script: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 2: Can we import production module?
print("\n2. Testing production module import...")
try:
    import AIEF_1_4_memory_ablation_updated as prod
    print(f"   ✓ Production module imported from: {prod.__file__}")
    print(f"   BRANCHES: {prod.BRANCHES}")
    print(f"   BRANCH_MATRIX_KEYS: {prod.BRANCH_MATRIX_KEYS}")
except Exception as e:
    print(f"   ✗ Failed to import production module: {e}")
    traceback.print_exc()

# Test 3: Can we import recovery module?
print("\n3. Testing recovery module import...")
try:
    import AIEF_1_4_trajectory_recovery_equivalence as recovery
    print(f"   ✓ Recovery module imported from: {recovery.__file__}")
    print(f"   Functions: {[x for x in dir(recovery) if not x.startswith('_')]}")
except Exception as e:
    print(f"   ✗ Failed to import recovery module: {e}")
    traceback.print_exc()

# Test 4: Check frozen data
print("\n4. Checking frozen data...")
import os
npz_path = "runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_branch_diagnostics.npz"
manifest_path = "runs/5a9f093a2fe0/manifest.json"
scalar_path = "runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_scalar_summary.csv"

for path in [npz_path, manifest_path, scalar_path]:
    if os.path.exists(path):
        print(f"   ✓ {path} exists")
    else:
        print(f"   ✗ {path} NOT FOUND")

# Test 5: Try to load manifest
print("\n5. Loading manifest...")
try:
    import json
    with open(manifest_path) as f:
        manifest = json.load(f)
    print(f"   ✓ Manifest loaded")
    print(f"   Model N: {manifest['model']['N']}")
    print(f"   Branches: {manifest['protocol']['branches']}")
except Exception as e:
    print(f"   ✗ Failed to load manifest: {e}")
    traceback.print_exc()

# Test 6: Try to load NPZ
print("\n6. Loading NPZ...")
try:
    import numpy as np
    with np.load(npz_path) as npz:
        keys = list(npz.files)
    print(f"   ✓ NPZ loaded with {len(keys)} keys")
    print(f"   First 5 keys: {keys[:5]}")
except Exception as e:
    print(f"   ✗ Failed to load NPZ: {e}")
    traceback.print_exc()

print("\n" + "=" * 70)
print("DIAGNOSTIC COMPLETE")
print("=" * 70)
