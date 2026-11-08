"""Proposed comparison helper only; no installation or authority modification.

Reuse the existing modular helper's component split for an authorized successor
or verification companion. Importing this file patches nothing. No simulation,
lock check, saved-run comparison certificate or dtype-policy expansion is supplied.
"""
import numpy as np


def exact_array_equal_with_nan(a: np.ndarray, b: np.ndarray) -> bool:
    """Value-level exact equality: matching shape/dtype and per-component NaNs.

    Signed zeros compare equal; NaN payload bits need not match. A missing real
    component never hides a different imaginary component, or conversely.
    """
    a = np.asarray(a)
    b = np.asarray(b)
    if a.shape != b.shape or a.dtype != b.dtype:
        return False
    if np.issubdtype(a.dtype, np.complexfloating):
        return exact_array_equal_with_nan(a.real, b.real) and exact_array_equal_with_nan(a.imag, b.imag)
    if np.issubdtype(a.dtype, np.floating):
        a_nan = np.isnan(a)
        b_nan = np.isnan(b)
        if not np.array_equal(a_nan, b_nan):
            return False
        finite = ~a_nan
        return np.array_equal(a[finite], b[finite])
    return np.array_equal(a, b)
