from fractions import Fraction as F

Z = F(0)
B = ((Z, F(1), F(1, 2)),
     (F(1), Z, F(1, 4)),
     (F(1, 2), F(1, 4), Z))
cap, eps = F(1), F(1, 4)
assert cap > 0 and eps > 0
assert all(B[i][i] == 0 for i in range(3))
assert all(B[i][j] >= 0 and B[i][j] == B[j][i]
           for i in range(3) for j in range(3))
rows = tuple(sum(row) for row in B)
assert rows == (F(3, 2), F(5, 4), F(3, 4))
assert max(rows) > cap  # engine's capacity branch activates
scale = tuple(min(F(1), cap / (x + eps)) for x in rows)
assert scale == (F(4, 7), F(2, 3), F(1))
si, sj = scale[0], scale[1]
edge_factor = min(si, sj)
product = si * sj
assert edge_factor == F(4, 7) and product == F(8, 21)
assert edge_factor != product
assert edge_factor >= 0 and edge_factor ** 2 != product
# By nonnegativity, unequal squares imply edge_factor != sqrt(product).
projected = tuple(tuple(B[i][j] * min(scale[i], scale[j])
                        for j in range(3)) for i in range(3))
projected_rows = tuple(sum(row) for row in projected)
assert projected_rows == (F(6, 7), F(31, 42), F(19, 42))
assert all(x <= cap for x in projected_rows)
print('B valid symmetric/nonnegative/zero-diagonal; cap=1, epsilon=1/4')
print('row sums:', rows, '; scales:', scale, '; active:', max(rows) > cap)
print('edge (0,1): min=', edge_factor, ', product=', product,
      ', min squared=', edge_factor ** 2, ', sqrt argument=', product)
print('projected row sums:', projected_rows)
print('EXACT WITNESS: PASS')

# Locally executed mutations of the gate factor; the fixed exact value is the test.
for name, mutant_square, mutant_value in (
    ('product', product ** 2, product),
    ('geometric mean', product, None),
):
    try:
        if mutant_value is not None:
            assert mutant_value == F(4, 7)
        else:
            assert mutant_square == F(4, 7) ** 2
    except AssertionError:
        print('MUTANT', name, ': KILLED (fixed gate-value assertion failed)')
    else:
        raise AssertionError('mutant unexpectedly survived: ' + name)
