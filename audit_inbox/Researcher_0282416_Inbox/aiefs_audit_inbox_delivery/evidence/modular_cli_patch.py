"""Demonstration patch for AIEF_modular_driver_v1.py to resolve the repository root import path."""

import sys
from pathlib import Path

def apply_repo_root_shim():
    """Ensure the repo root containing aief_experiment_engine_v1.py is on sys.path."""
    # When executed from AIEF_Experiments/aief_modular_platform_v1_analysis_v4/
    current = Path(__file__).resolve()
    for parent in [current.parent, current.parent.parent, current.parent.parent.parent]:
        if (parent / "aief_experiment_engine_v1.py").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            break

if __name__ == "__main__":
    apply_repo_root_shim()
    print("Repository root resolution shim verified.")
