"""H9(b) + H16 (SPEC §18; author Auditor Seat 002): pin GronwallEnvelope.lean / GateContraction.lean, their mutants
M300-M316, the H16 probe result and the exact witness numbers, without running Lean.

The H16 binding-gate witness (Fin 3, frozen pE, D = 0) is recomputed here in exact rational arithmetic with an
independent mirror of the engine step (aief_experiment_engine_v1.py lines 790-813; mirrored, not imported, and the
engine is not edited). The numerical N = 12 probe is pinned through its stored output file only.

Run: /workspace/venv-pt/bin/pytest -q research/lean_gate/tests/test_lean_gate_h9h16.py
"""
import hashlib
import json
import re
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import lean_mutation_check as mc  # noqa: E402

REPO = HERE.parents[2]
PROJ = REPO / "lean" / "AIEFGateCore"
FILES = ("GronwallEnvelope.lean", "GateContraction.lean")
SRC = {f: (PROJ / "AIEFGateCore" / f).read_text() for f in FILES}
GE, GC = SRC["GronwallEnvelope.lean"], SRC["GateContraction.lean"]

N_BLOCK_STATEMENT = 13          # M300-M312
N_BLOCK_DEF = 4                 # M313-M316
BLOCK = [m for m in mc.MUTANTS if m[1] in FILES]
BLOCK_DEF = [m for m in mc.DEF_MUTANTS if m[1] in FILES]


def num(name):
    return int(name.split("_")[0][1:])


def test_modules_imported_and_hash_pinned():
    root = (PROJ / "AIEFGateCore.lean").read_text()
    sums = (PROJ / "AIEF_LEAN_GATE_SOURCE_SHA256SUMS.txt").read_text()
    for f in FILES:
        assert re.search(rf"^import AIEFGateCore\.{f[:-5]}$", root, re.M), f
        digest = hashlib.sha256((PROJ / "AIEFGateCore" / f).read_bytes()).hexdigest()
        assert f"{digest}  AIEFGateCore/{f}" in sums, f
        assert SRC[f].startswith("/-\nCopyright (c) 2026 Jacob Brainard and AIEF contributors.")
        assert f"namespace {f[:-5]}" in SRC[f]


def test_no_escape_hatches_scope_and_axioms_printed():
    for f, src in SRC.items():
        code = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith(("--", "/-", "*")))
        for bad in ("sorry", "admit", "native_decide", "axiom ", "unsafe", "implemented_by", "extern"):
            assert bad not in code.replace("#print axioms", ""), (f, bad)
        assert "conditional, not O1" in src, f                   # frozen drive / frozen R is stated, not hidden
    # H9: only the product-form Grönwall lemma
    ge_code = GE[GE.index("set_option autoImplicit false"):]                   # after the module doc
    ge_code = "\n".join(l for l in ge_code.splitlines() if not l.lstrip().startswith(("--", "/-")))
    assert "discrete_gronwall_prod_general" in ge_code
    assert not re.search(r"discrete_gronwall(?!_prod_general)", ge_code)          # not the (1 + c) growth form
    for thm in ("scalar_envelope_upper", "scalar_envelope_lower", "stepM_edge_envelope_upper",
                "stepM_edge_envelope_lower", "stepM_edge_envelope_pE", "upper_geom_via_gronwall",
                "upper_geom_of_ne_one", "false_envelope_gamma_dt_gt_one", "false_variant_gate_after_drive"):
        assert re.search(rf"^#print axioms {thm}$", GE, re.M), thm
    for thm in ("stepM_entry_lipschitz_gate_off", "stepM_entry_lipschitz_gate_off_symm", "scalar_map_contracting",
                "scalar_map_fixedPoint_tendsto", "binding_witness_l1", "false_stepM_l1_nonexpansive_binding",
                "false_entry_lipschitz_no_gate_off", "probe_l1_B3"):
        assert re.search(rf"^#print axioms {thm}$", GC, re.M), thm


def test_h9a_targets_gate_copy_and_statement_equality():
    """(a) targets AIEFGate.Freeze.upper_geom (GateCore may not import AIEFFreezeCore), both directions."""
    assert "AIEFFreezeCore" not in "".join(l for l in GE.splitlines() if l.startswith("import"))
    assert ":= AIEFGate.Freeze.upper_geom" in GE and ":= upper_geom_via_gronwall" in GE
    assert re.search(r"^theorem upper_geom_statement_eq :", GE, re.M) and ":= rfl" in GE


def test_block_mutants_exact_shape():
    assert len(BLOCK) == N_BLOCK_STATEMENT and len(BLOCK_DEF) == N_BLOCK_DEF
    assert [num(m[0]) for m in BLOCK] == list(range(300, 313))
    assert [num(m[0]) for m in BLOCK_DEF] == list(range(313, 317))
    assert (len(mc.MUTANTS), len(mc.DEF_MUTANTS)) == (118, 89)
    assert all(num(m[0]) < 300 for m in mc.MUTANTS + mc.DEF_MUTANTS if m[1] not in FILES)   # separate block
    for name, f, thm, edits, closure, term, eterm in BLOCK:
        assert eterm is None and len(edits) == 1 and edits[0][2] == 1, name
        assert re.search(rf"^theorem {thm}\b", SRC[f], re.M), name
        assert mc.mutate(SRC[f], thm, edits) != SRC[f], name
        assert mc.statement_prop(SRC[f], thm, closure) != mc.statement_prop(mc.mutate(SRC[f], thm, edits), thm,
                                                                                 closure), name
        m = re.match(r"(GronwallEnvelope|GateContraction)\.(false_\w+)", term)
        assert m and m.group(1) == f[:-5] and re.search(rf"^theorem {m.group(2)}\b", SRC[f], re.M), name
    assert {m[1] for m in BLOCK} == set(FILES)
    assert "gate_before_drive" in BLOCK[6][0] and BLOCK[6][2] == "edge_recurrence"      # wrong-variant control
    assert "WeightUpdate.pH" in BLOCK[5][5] and "WeightUpdate.pH" in BLOCK[10][5]      # gamma dt > 1 witnesses
    assert not set(FILES) & set(mc.FILE_OPENS)


def test_block_def_mutants_and_probes():
    assert mc.VP_H16 == ["probe_scalarMap_value", "probe_scalarMap_clamp", "probe_l1_B3"]
    assert mc.VALUE_PROBES["GateContraction.lean"] == mc.VP_H16
    for p in mc.VP_H16:
        assert re.search(rf"^theorem {p}\b", GC, re.M) and p.startswith("probe_")
    for name, f, edits, pins in BLOCK_DEF:
        assert f == "GateContraction.lean" and pins and set(pins) <= set(mc.VP_H16), name
        assert mc.mutate_file(GC, edits) != GC, name
    assert mc.KNOWN_SURVIVORS == []


# ---- exact arithmetic --------------------------------------------------------------------------------------------
DT, G, A, QQ, DE, EPS = Q(1, 100), Q(15, 1000), Q(1), Q(3, 2), Q(5, 100), Q(1, 10 ** 12)
CAP = (A - DE) / QQ


def step(B, D, dt=DT, g=G, cap=CAP, eps=EPS, a=A, q=QQ, de=DE):
    """engine L790-813 in exact arithmetic (clip, symmetrise, zero diagonal, global trigger, min-outer scale)"""
    n = len(B)
    P = [[max(B[i][j] + dt * (D[i][j] - g * B[i][j]), Q(0)) for j in range(n)] for i in range(n)]
    U = [[Q(0) if i == j else (P[i][j] + P[j][i]) / 2 for j in range(n)] for i in range(n)]
    r = [sum(row) for row in U]
    on = min(a - q * x for x in r) < de
    if on:
        s = [min(Q(1), cap / (x + eps)) for x in r]
        U = [[Q(0) if i == j else U[i][j] * min(s[i], s[j]) for j in range(n)] for i in range(n)]
    return U, on, r


def l1(X, Y):
    return sum(abs(X[i][j] - Y[i][j]) for i in range(len(X)) for j in range(len(X)))


B3 = [[Q(0), Q(1, 3), Q(1, 3)], [Q(1, 3), Q(0), Q(1, 3)], [Q(1, 3), Q(1, 3), Q(0)]]
B3P = [[Q(0), Q(13, 30), Q(1, 3)], [Q(13, 30), Q(0), Q(1, 3)], [Q(1, 3), Q(1, 3), Q(0)]]
Z3 = [[Q(0)] * 3 for _ in range(3)]


def test_h16_fin3_witness_exact():
    U, on, r = step(B3, Z3)
    V, on2, r2 = step(B3P, Z3)
    rho = 1 - G * DT
    assert rho == Q(19997, 20000)
    assert on and on2 and all(x > CAP for x in r + r2)                       # binding_witness_rows
    assert r == [Q(19997, 30000)] * 3 and r2 == [Q(459931, 600000)] * 2 + [Q(19997, 30000)]
    sA, sB = CAP / (Q(19997, 30000) + EPS), CAP / (Q(459931, 600000) + EPS)
    assert U[0][1] == rho / 3 * sA and V[0][1] == rho * Q(13, 30) * sB and V[0][2] == rho / 3 * sB
    assert l1(B3, B3P) == Q(1, 5)                                             # probe_l1_B3
    ratio = l1(U, V) / l1(B3, B3P)
    assert Q(6, 5) < ratio < Q(124, 100) and abs(float(ratio) - 1.2391304) < 1e-6   # binding_witness_l1
    assert B3[0][2] == B3P[0][2] and U[0][2] - V[0][2] > 0                    # binding_witness_entry


def test_h16_gate_off_and_gamma_dt_witnesses_exact():
    # pH = <dt 2, gamma 1, cap 1, eps 1, a 1, q 1, delta 0>: gamma dt = 2, rho = -1 (engine-legal)
    ph = dict(dt=Q(2), g=Q(1), cap=Q(1), eps=Q(1), a=Q(1), q=Q(1), de=Q(0))
    D = [[Q(0), Q(1, 4)], [Q(1, 4), Q(0)]]
    U, on, _ = step([[Q(0)] * 2] * 2, D, **ph)
    V, on2, _ = step([[Q(0), Q(1, 4)], [Q(1, 4), Q(0)]], D, **ph)
    assert not on and not on2 and abs(U[0][1] - V[0][1]) == Q(1, 4) > (1 - 2) * Q(1, 4)
    # asymmetric pair at pE, gate off: entry (0,1) unchanged in the input, moved by rho/20 in the image
    Z2 = [[Q(0)] * 2] * 2
    U, on, _ = step(Z2, Z2)
    V, on2, _ = step([[Q(0), Q(0)], [Q(1, 10), Q(0)]], Z2)
    assert not on and not on2 and V[0][1] - U[0][1] == Q(19997, 20000) / 20 > 0
    # gamma dt > 1 envelope witness (false_envelope_gamma_dt_gt_one): one step from Xo 1, no drive
    W, on, _ = step([[Q(0), Q(1)], [Q(1), Q(0)]], Z2, **ph)
    assert not on and W[0][1] == 0 > (1 - 2) * 1
    # wrong-variant control (false_variant_gate_after_drive): pE, B = D = Xo 1
    X1 = [[Q(0), Q(1)], [Q(1), Q(0)]]
    W, on, r = step(X1, X1)
    lam = min(Q(1), CAP / (r[0] + EPS))
    assert on and W[0][1] == lam * ((1 - G * DT) * 1 + DT) != max(Q(0), lam * (1 - G * DT) + DT)


def test_h9_scalar_witnesses_and_pE_envelope_constant():
    def run(B0, lam, d, rho, n):
        B = [B0]
        for k in range(n):
            B.append(lam[k] * max(Q(0), rho * B[k] + d[k]))
        return B
    def upper(B0, d, rho, n):
        return rho ** n * B0 + sum(rho ** (n - 1 - k) * max(Q(0), d[k]) for k in range(n))
    assert run(Q(1), [1], [0], Q(-2), 1)[1] == 0 > upper(Q(1), [0], Q(-2), 1)            # rho >= 0 needed
    assert run(Q(-1), [1], [0], Q(1, 2), 1)[1] == 0 > upper(Q(-1), [0], Q(1, 2), 1)      # B 0 >= 0 needed
    assert run(Q(0), [2], [1], Q(0), 1)[1] == 2 > upper(Q(0), [1], Q(0), 1)              # lam <= 1 needed
    B = run(Q(0), [1, 1], [1, 2], Q(-1), 2)
    kap = [Q(1, 2), Q(1)]
    lower2 = kap[0] * 1 * (kap[1] * -1) + kap[1] * 2
    assert B[2] == 1 < lower2 == Q(3, 2)                                                  # rho >= 0 needed (lower)
    # pE: dt * Dmax / (gamma dt) = (1/100)(1/25) / (3/20000) = 8/3 = u
    assert DT * Q(1, 25) / (G * DT) == Q(8, 3)


def test_probe_output_pinned():
    out = (REPO / "research" / "lean_gate" / "results" / "h16_binding_probe_v1.txt").read_text()
    first = json.loads(out[:out.index("}") + 1])
    assert first["n_binding_states"] == 200 and first["rho_1_minus_gdt"] == 0.99985
    assert 1.22 < first["l1_induced"][0] and 2.29 < first["l1_induced"][1] < 2.30
    assert 4.43 < first["linf_induced"][1] < 4.44 and 1.51 < first["spectral"][1] < 1.52
    assert '"ratio": 2.295660707448888' in out and '"gate_on_both": true' in out
    probe = (REPO / "research" / "lean_gate" / "h16_binding_probe.py").read_text()
    assert "import aief_experiment_engine_v1" not in probe and "default_rng(20261126)" in probe


def test_engine_lines_mirrored_exist():
    eng = (REPO / "aief_experiment_engine_v1.py").read_text()
    for cite in ("B_unprojected = np.maximum(B_unprojected, 0.0)",
                 "B_unprojected = 0.5 * (B_unprojected + B_unprojected.T)",
                 "pre_violation = bool(g_min_pre < config.delta)",
                 "scale = np.minimum(1.0, config.capacity / (row_sum_pre + config.scale_epsilon))",
                 "B_projected = B_unprojected * np.minimum.outer(scale, scale)"):
        assert cite in eng, cite
    assert hashlib.sha256((REPO / "aief_experiment_engine_v1.py").read_bytes()).hexdigest() == \
        "ca4593fda86a1b0a3d450d68b5ce4bddd08583fdb93deaf17db20dd6b1acdede"
