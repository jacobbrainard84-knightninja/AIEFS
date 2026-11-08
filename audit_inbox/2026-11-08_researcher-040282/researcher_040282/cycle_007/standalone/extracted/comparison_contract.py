"""Independent scalar-component spec and deterministic finite007 fixtures.
No candidate helper, complex-wide missingness mask or approximate oracle.
"""
from dataclasses import dataclass
import math
from typing import Any
import numpy as np


class ContractMismatch(RuntimeError):
    def __init__(self, rule, name, expected, observed):
        self.rule = rule
        self.case = name
        self.expected = expected
        self.observed = observed
        super().__init__(f'{rule}: {name}; expected={expected}, observed={observed}')


@dataclass
class Case:
    group: str
    name: str
    left: Any
    right: Any
    watch: tuple = ()


def real_equal(x, y):
    x, y = float(x), float(y)
    return math.isnan(y) if math.isnan(x) else not math.isnan(y) and x == y


def specification(left, right):
    a, b = np.asarray(left), np.asarray(right)
    if a.shape != b.shape or a.dtype != b.dtype:
        return False
    for x, y in zip(a.flat, b.flat):
        if a.dtype.kind == 'c':
            if not real_equal(x.real, y.real) or not real_equal(x.imag, y.imag):
                return False
        elif a.dtype.kind == 'f':
            if not real_equal(x, y):
                return False
        elif not bool(x == y):
            return False
    return True


def fingerprint(value):
    a = np.asarray(value)
    return (a.shape, a.dtype.str, a.strides, a.flags.writeable, a.tobytes(order='C'))


def checked(target, case):
    objects = (case.left, case.right) + case.watch
    snapshots = tuple(fingerprint(value) for value in objects)
    expected = specification(case.left, case.right)  # MUST precede target call.
    answer = target(case.left, case.right)
    after = tuple(fingerprint(value) for value in objects)
    if snapshots != after:
        raise ContractMismatch('input_preservation', case.name, 'unchanged', 'mutated')
    if not isinstance(answer, (bool, np.bool_)):
        raise ContractMismatch('boolean_return', case.name, 'scalar boolean', type(answer).__name__)
    answer = bool(answer)
    if answer != expected:
        raise ContractMismatch('truth_value', case.name, expected, answer)
    return answer


def cases():
    out = []
    def add(group, name, left, right, watch=()):
        out.append(Case(group, name, left, right, watch))
    for dtype in (np.complex64, np.complex128):
        tag = np.dtype(dtype).name
        def z(r, i):
            return np.array([complex(r, i)], dtype=dtype)
        add('missing_real', tag + '_missing_real_changed_imag', z(math.nan, 1), z(math.nan, 99))
        add('missing_imag', tag + '_missing_imag_changed_real', z(1, math.nan), z(5, math.nan))
        add('nan_positions', tag + '_swapped_missing_component', z(math.nan, 1), z(1, math.nan))
        alphabet = (math.nan, -math.inf, -1.0, 0.0, 1.0, math.inf)
        values = [complex(r, i) for r in alphabet for i in alphabet]
        for i, left in enumerate(values):
            for j, right in enumerate(values):
                add('reduced_alphabet', tag + f'_alphabet_{i}_{j}',
                    np.array([left], dtype=dtype), np.array([right], dtype=dtype))
        add('complex_exactness', tag + '_matching_inf_components', z(math.inf, -math.inf), z(math.inf, -math.inf))
        add('complex_exactness', tag + '_opposite_inf_components', z(math.inf, 1), z(-math.inf, 1))
        add('complex_exactness', tag + '_signed_zero_values', z(-0.0, 0.0), z(0.0, -0.0))
        component = np.float32 if dtype is np.complex64 else np.float64
        neighbor = float(np.nextafter(component(1), component(2)))
        add('complex_exactness', tag + '_imaginary_one_ulp', z(1, 1), z(1, neighbor))
        add('complex_exactness', tag + '_real_one_ulp', z(1, 1), z(neighbor, 1))
        uint = np.uint32 if dtype is np.complex64 else np.uint64
        nan1 = 0x7fc00001 if dtype is np.complex64 else 0x7ff8000000000001
        nan2 = 0xffc00002 if dtype is np.complex64 else 0xfff8000000000002
        one = np.array([component(1)], dtype=component).view(uint)[0]
        a = np.array([nan1, one], dtype=uint).view(dtype)
        b = np.array([nan2, one], dtype=uint).view(dtype)
        add('complex_exactness', tag + '_nan_payload_sign_ignored', a, b)
    for dtype in (np.float16, np.float32, np.float64):
        tag = np.dtype(dtype).name
        a = np.array([1.0], dtype=dtype)
        neighbor = np.nextafter(a, np.array([2.0], dtype=dtype))
        subnormal = np.nextafter(np.array([0.0], dtype=dtype), np.array([1.0], dtype=dtype))
        add('real_exactness', tag + '_one_ulp', a, neighbor)
        add('real_exactness', tag + '_nonzero_subnormal', np.array([0], dtype=dtype), subnormal)
        add('real_exactness', tag + '_same_nan_inf_zero', np.array([math.nan, math.inf, -math.inf, -0.0], dtype=dtype),
            np.array([math.nan, math.inf, -math.inf, 0.0], dtype=dtype))
        add('real_exactness', tag + '_nan_position', np.array([math.nan, 1], dtype=dtype), np.array([1, math.nan], dtype=dtype))
        add('real_exactness', tag + '_inf_sign', np.array([math.inf], dtype=dtype), np.array([-math.inf], dtype=dtype))
    for dtype in (np.float64, np.complex128, np.int64):
        a = np.arange(6, dtype=np.float64).astype(dtype).reshape(2, 3)
        add('guards', str(dtype) + '_shape_not_flattened', a, a.reshape(6))
        add('guards', str(dtype) + '_shape_not_broadcast', np.ones((1, 3), dtype=dtype), np.ones((2, 3), dtype=dtype))
    for left, right in ((np.int32, np.int64), (np.float32, np.float64), (np.complex64, np.complex128), (np.uint32, np.int32)):
        add('guards', str(left) + '_dtype', np.array([1, 2], dtype=left), np.array([1, 2], dtype=right))
        add('guards', str(left) + '_empty_dtype', np.array([], dtype=left), np.array([], dtype=right))
    for shape in ((), (0,), (0, 3), (2, 0, 3), (1,), (2, 3, 4), (12, 12)):
        for dtype in (np.float64, np.complex128, np.int64):
            add('empty_scalar', str(shape) + str(dtype), np.zeros(shape, dtype=dtype), np.zeros(shape, dtype=dtype))
    add('empty_scalar', 'python_float_nan', math.nan, math.nan)
    add('empty_scalar', 'python_complex_nan', complex(math.nan, 1), complex(math.nan, 1))
    add('empty_scalar', 'numpy_complex_scalar', np.complex64(complex(1, math.nan)), np.complex64(complex(1, math.nan)))
    for kind in ('transpose', 'reverse', 'stride', 'readonly'):
        base = np.arange(60, dtype=np.float64).reshape(3, 4, 5)
        a = {'transpose': base.transpose(2, 0, 1), 'reverse': base[:, ::-1, :],
             'stride': base[:, ::2, ::2], 'readonly': base.view()}[kind]
        if kind == 'readonly':
            a.flags.writeable = False
        b = a.copy()
        add('views', kind + '_equal', a, b, (base,))
        add('views', kind + '_finite_difference', a, b + 1, (base,))
    for dtype, values in ((np.bool_, [True, False]), (np.int8, [-1, 0, 1]),
                          (np.int64, [2**53, 2**53 + 1]), (np.uint64, [2**64 - 2, 2**64 - 1]),
                          ('U2', ['a', 'bb']), ('S2', [b'a', b'bb'])):
        a = np.array(values, dtype=dtype)
        add('fallback', str(dtype) + '_equal', a, a.copy())
        add('fallback', str(dtype) + '_different', a, a[::-1].copy())
    for dtype in (np.float32, np.float64, np.complex64, np.complex128):
        a = np.array([1, 2, 3], dtype=dtype)
        add('preservation', str(dtype) + '_equal_inputs_preserved', a, a.copy())
    return out


def group_names():
    return ('missing_real', 'missing_imag', 'nan_positions', 'reduced_alphabet',
            'real_exactness', 'complex_exactness', 'guards', 'empty_scalar',
            'views', 'fallback', 'preservation')
