"""Recompute complete matrices after swapping the gate's combining function."""
from fractions import Fraction as F

B = ((F(0), F(1), F(1, 2)),
     (F(1), F(0), F(1, 4)),
     (F(1, 2), F(1, 4), F(0)))
CAP, EPS = F(1), F(1, 4)
EXPECTED = ((F(0), F(4, 7), F(2, 7)),
            (F(4, 7), F(0), F(1, 6)),
            (F(2, 7), F(1, 6), F(0)))


def project(b, combine):
    rows = tuple(sum(row) for row in b)
    if max(rows) <= CAP:
        return False, b
    scales = tuple(min(F(1), CAP / (r + EPS)) for r in rows)
    result = tuple(tuple(b[i][j] * combine(scales[i], scales[j])
                         for j in range(3)) for i in range(3))
    return True, result


def verify(combine):
    active, actual = project(B, combine)
    half = tuple(tuple(x / 2 for x in row) for row in B)
    inactive, negative_result = project(half, combine)
    negative_ok = not inactive and negative_result == half
    active_ok = active and actual == EXPECTED
    print('active:', active, 'edge01:', actual[0][1], 'edge12:', actual[1][2],
          'full-matrix oracle:', 'PASS' if active_ok else 'FAIL')
    print('inactive branch control:', 'PASS' if negative_ok else 'FAIL')
    return active_ok and negative_ok


if __name__ == '__main__':
    import sys
    if sys.argv[1:] == ['min']:
        combine = min
    elif sys.argv[1:] == ['product']:
        combine = lambda x, y: x * y
    else:
        raise SystemExit('usage: python exact_gate_checks.py min|product')
    raise SystemExit(0 if verify(combine) else 1)
