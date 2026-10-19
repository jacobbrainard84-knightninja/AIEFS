"""AIEF Modular Experiment Driver Platform v1.

This package orchestrates certified engine-v1 studies without reimplementing
numerical dynamics.  Built-in studies are registered explicitly via
``aief_modular.registry.load_builtin_studies``.
"""

from .registry import REGISTRY, load_builtin_studies
from .runner import RUNNER_VERSION

__all__ = ["REGISTRY", "RUNNER_VERSION", "load_builtin_studies"]
__version__ = RUNNER_VERSION
