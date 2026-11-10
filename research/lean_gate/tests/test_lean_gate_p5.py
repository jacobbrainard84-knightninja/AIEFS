"""Lean P5: pin the exact values behind PhaseCoherence.lean (port of cycles 010, 011 and 013 of Researcher 040282,
restated on Params / preM / stepM) against an independent floating/exact simulation of the engine convention
(compute_R, aief_experiment_engine_v1.py about lines 735-751, hand-checked, NOT proved against Python), check that the
statements restated in HistoryBuffer.lean / PhaseIncrement.lean / PhaseCoherence.lean agree textually with the
deposited sources (the deposit is not on main, so the statements are recorded below with their md5s), and pin the
shape and the EXACT COUNT of the P5 mutants of lean_mutation_check.py without running Lean.

Mutation-count pin (this file is the only exact pin; the P4a test still asserts the 23 statement mutants of
`MUTANTS`): `MUTANTS` has 23 entries (M1-M23) and `DEF_MUTANTS` 16 (M37-M52), total 39; controls: 9 equivalence, 3 typo, 2 statement-level. M24-M36 are reserved for P4b
(PR #26): when P4b merges, `MUTANTS` becomes 36 entries (its own test pins 36) and the total becomes 52, so
`TOTAL_MUTANTS` below must be reconciled to 52 (and the `MUTANTS` pin to 36) in that merge.

Run: /workspace/venv_req_cmp/bin/python -m pytest research/lean_gate/tests -q
"""
import cmath
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import lean_mutation_check as mc  # noqa: E402

REPO = HERE.parents[2]
GATE = REPO / "lean" / "AIEFGateCore" / "AIEFGateCore"
HB = (GATE / "HistoryBuffer.lean").read_text()
PI = (GATE / "PhaseIncrement.lean").read_text()
PC = (GATE / "PhaseCoherence.lean").read_text()

N_STATEMENT_MUTANTS = 23          # M1-M23 (P1-P4a); P4b's M24-M36 are not on this branch
N_DEF_MUTANTS = 16                # M37-M52
TOTAL_MUTANTS = N_STATEMENT_MUTANTS + N_DEF_MUTANTS   # 39; reconcile to 52 when P4b merges (see module docstring)

# Statements of the deposit (md5 fe47db36... HistoryBuffer.lean, b26f225f... PhaseIncrement.lean, 410275ad...
# PhaseCoherenceBridge.lean), whitespace-normalised, namespace prefixes (Researcher040282.Phase./Delay.) removed.
HISTORY_STATEMENTS = {
    'historyTrace_index':
        '{A : Type u} (d : Nat) (x : Nat → A) : ∀ n (i : Fin (d + 1)), historyTrace d x n i = x (n + i.val - d)',
    'historyTrace_oldest':
        '{A : Type u} (d : Nat) (x : Nat → A) (n : Nat) : historyTrace d x n ⟨0, Nat.zero_lt_succ d⟩ = x (n - d)',
    'historyTrace_newest':
        '{A : Type u} (d : Nat) (x : Nat → A) (n : Nat) : historyTrace d x n ⟨d, Nat.lt_succ_self d⟩ = x n',
}

PHASE_STATEMENTS = {
    'phasor_wrap':
        '(t : ℝ) : phasor (wrapPhase t) = phasor t',
    'delayed_input_step':
        '(d : ℕ) (x0 : ι → ℝ) (u : ℕ → ι → ℝ) (omega : ι → ℝ) (tau : ℝ) (n : ℕ) (i j : ι) : inputPhasor d x0 u omega tau (n + 1) i j = inputPhasor d x0 u omega tau n i j * phasor (u n i - delayedIncrement d u n j)',
    'delayed_input_chord_bound':
        '(d : ℕ) (x0 : ι → ℝ) (u : ℕ → ι → ℝ) (omega : ι → ℝ) (tau : ℝ) (n : ℕ) (i j : ι) : ‖inputPhasor d x0 u omega tau (n + 1) i j - inputPhasor d x0 u omega tau n i j‖ ≤ |u n i - delayedIncrement d u n j|',
}

C013_STATEMENTS = {
    'input_engine_convention':
        '(d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ) (n : ℕ) (i j : V) : coherenceInput d x0 u omega tau n i j = Complex.exp (Complex.I * ((phaseTrace x0 u n i - phaseTrace x0 u (n - d) j - ((omega i + omega j) / 2) * tau : ℝ) : ℂ))',
    'input_norm':
        '(d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ) (n : ℕ) (i j : V) : ‖coherenceInput d x0 u omega tau n i j‖ = 1',
    'innovation_engine_convention':
        '(alpha : ℝ) (C : V → V → ℂ) (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ) (n : ℕ) (i j : V) : coherenceStep alpha C d x0 u omega tau n i j - (alpha : ℂ) * C i j = ((1 - alpha : ℝ) : ℂ) * Complex.exp (Complex.I * ((phaseTrace x0 u n i - phaseTrace x0 u (n - d) j - ((omega i + omega j) / 2) * tau : ℝ) : ℂ))',
    'lateSource_startup':
        '(d : ℕ) (u : ℕ → V → ℝ) (n : ℕ) (j : V) (h : n < d) : lateSource d u n j = 0',
    'innovation_transport':
        '(alpha : ℝ) (C0 : V → V → ℂ) (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ) (n : ℕ) (i j : V) : coherenceTrace alpha C0 d x0 u omega tau (n + 2) i j - (alpha : ℂ) * coherenceTrace alpha C0 d x0 u omega tau (n + 1) i j = (coherenceTrace alpha C0 d x0 u omega tau (n + 1) i j - (alpha : ℂ) * coherenceTrace alpha C0 d x0 u omega tau n i j) * phasor (u n i - lateSource d u n j)',
    'coherenceTrace_unitDisk':
        '(alpha : ℝ) (C0 : V → V → ℂ) (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ) (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) (hC : ∀ i j, ‖C0 i j‖ ≤ 1) : ∀ n i j, ‖coherenceTrace alpha C0 d x0 u omega tau n i j‖ ≤ 1',
    'reported_bounds':
        '(C : V → V → ℂ) (hC : ∀ i j, ‖C i j‖ ≤ 1) (i j : V) : 0 ≤ reported C i j ∧ reported C i j ≤ 1',
    'phase_drive_bounds':
        '(eta mu alpha : ℝ) (C0 : V → V → ℂ) (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ) (heta : 0 ≤ eta) (hmu : 0 ≤ mu) (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) (hC : ∀ i j, ‖C0 i j‖ ≤ 1) (n : ℕ) (i j : V) : -mu ≤ sourceDrive eta mu (coherenceTrace alpha C0 d x0 u omega tau (n + 1)) i j ∧ sourceDrive eta mu (coherenceTrace alpha C0 d x0 u omega tau (n + 1)) i j ≤ eta',
    'phase_normalized_drive_bounds':
        '(p : AIEFGate.Params) (eta mu alpha : ℝ) (C0 : V → V → ℂ) (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ) (heta : 0 ≤ eta) (hmu : 0 ≤ mu) (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) (hC : ∀ i j, ‖C0 i j‖ ≤ 1) (hg : 0 < p.γ) (n : ℕ) (i j : V) : -mu / p.γ ≤ sourceDrive eta mu (coherenceTrace alpha C0 d x0 u omega tau (n + 1)) i j / p.γ ∧ sourceDrive eta mu (coherenceTrace alpha C0 d x0 u omega tau (n + 1)) i j / p.γ ≤ eta / p.γ',
    'phase_positiveRow_bound':
        '[Fintype V] [DecidableEq V] (p : AIEFGate.Params) (eta mu alpha : ℝ) (C0 : V → V → ℂ) (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ) (heta : 0 ≤ eta) (hmu : 0 ≤ mu) (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) (hC : ∀ i j, ‖C0 i j‖ ≤ 1) (hg : 0 < p.γ) (n : ℕ) (i : V) : (∑ j ∈ (Finset.univ : Finset V).erase i, max 0 (sourceDrive eta mu (coherenceTrace alpha C0 d x0 u omega tau (n + 1)) i j / p.γ)) ≤ ((Fintype.card V - 1 : ℕ) : ℝ) * (eta / p.γ)',
    'drive_eta_response':
        '(eta mu delta : ℝ) (C : V → V → ℂ) (i j : V) : sourceDrive (eta + delta) mu C i j - sourceDrive eta mu C i j = delta * reported C i j',
    'main_preM_source_formula':
        '(p : AIEFGate.Params) (eta mu : ℝ) (C : V → V → ℂ) (B : V → V → ℝ) (i j : V) : AIEFGate.MatrixForm.preM p (sourceDrive eta mu C) B i j = B i j + p.dt * ((eta + mu) * reported C i j - mu - p.γ * B i j)',
    'main_phase_preM':
        '(p : AIEFGate.Params) (eta mu alpha : ℝ) (C0 : V → V → ℂ) (d : ℕ) (x0 : V → ℝ) (u : ℕ → V → ℝ) (omega : V → ℝ) (tau : ℝ) (n : ℕ) (B : V → V → ℝ) (i j : V) : AIEFGate.MatrixForm.preM p (sourceDrive eta mu (coherenceTrace alpha C0 d x0 u omega tau (n + 1))) B i j = B i j + p.dt * ((eta + mu) * reported (coherenceTrace alpha C0 d x0 u omega tau (n + 1)) i j - mu - p.γ * B i j)',
    'probe_coherence_values':
        '(i j : Fin 2) : coherenceTrace (1/2) probeC0 2 probeX probeU probeOmega Real.pi 1 i j = 0 ∧ coherenceTrace (1/2) probeC0 2 probeX probeU probeOmega Real.pi 2 i j = -Complex.I/2 ∧ coherenceTrace (1/2) probeC0 2 probeX probeU probeOmega Real.pi 3 i j = 1/2-Complex.I/4 ∧ coherenceTrace (1/2) probeC0 2 probeX probeU probeOmega Real.pi 4 i j = 3/4-Complex.I/8',
    'probe_late_start':
        ': lateSource 2 probeU 1 (0 : Fin 2) = 0',
    'probe_reported_second':
        ': reported (coherenceTrace (1/2) probeC0 2 probeX probeU probeOmega Real.pi 2) (0 : Fin 2) 1 = 1/2',
    'probe_drive_second':
        ': sourceDrive 2 1 (coherenceTrace (1/2) probeC0 2 probeX probeU probeOmega Real.pi 2) (0 : Fin 2) 1 = 1/2',
}


def _norm(s):
    s = s.replace("Researcher040282.Phase.", "").replace("Researcher040282.Delay.", "")
    s = s.replace("Phase.", "").replace("History.", "")
    return " ".join(s.split())


def _stmt(src, name):
    m = re.search(rf"^(?:theorem|lemma) {re.escape(name)}\b(.*?):=", src, re.M | re.S)
    assert m, name
    return _norm(m.group(1))


def test_restated_statements_match_deposit():
    for name, want in HISTORY_STATEMENTS.items():
        assert _stmt(HB, name) == want, name
    for name, want in PHASE_STATEMENTS.items():
        assert _stmt(PI, name) == want, name
    for name, want in C013_STATEMENTS.items():
        assert _stmt(PC, name) == want, name


def test_sources_have_no_banned_markers_credit_by_handle_only():
    for src in (HB, PI, PC):
        body = [l for l in src.splitlines() if not l.lstrip().startswith(("--", "/-", "*"))]
        for bad in ("sorry", "admit", "native_decide", "axiom ", "unsafe", "implemented_by", "extern"):
            assert not any(bad in l for l in body), bad
        assert "@" not in src.replace("@[", "")                      # no e-mail addresses
        assert "Researcher 040282" in src and ("1b5ae52" in src or "410275ad" in src)
    assert "fe47db36" in HB and "b26f225f" in PI and "410275adc4ea837a6384cefe2d545c2d" in PC
    assert "hand-checked, not proved against Python" in PC.replace("\n", " ")  # transcription honesty (scope)
    assert "wrong_" not in PC.replace("`wrong_*_refuted`", "")      # N3: no wrong_*_refuted lemma name left


def test_fix_lemmas_present_n1_n2_n3_n5():
    for name in ("reported_diag", "reported_symm", "reported_offdiag", "sourceDrive_diag", "sourceDrive_symm",
                 "probe_asym_coherence_values", "probe_asym_directed_ne", "probe_asym_reported",
                 "probe_asym_reported_swapped", "probe_asym_reported_diag", "probe_alpha_quarter",
                 "main_phase_stepM_eq_stepB"):
        assert re.search(rf"^theorem {name}\b", PC, re.M), name
    for name in ("inputPhasor_delay_three_differs", "inputPhasor_delay_one_differs", "inputPhasor_delay_zero_differs",
                 "inputPhasor_no_offset_differs", "constant_input_differs", "drive_without_eta_differs"):
        assert re.search(rf"^theorem {name}\b", PC, re.M), name
    assert "def probeC00 (_ _ : Fin 2) : ℂ := 0" in PC            # N5 zero initial coherence
    assert "def probeU2 (_ : ℕ) (i : Fin 2) : ℝ := if i = 0 then Real.pi / 2 else 0" in PC  # N1 node-dependent


# ---- independent simulation of the engine convention (compute_R, advance of theta, EMA) ----------------------

def simulate(alpha, c0, d, x0, u, omega, tau, steps):
    """theta_{n+1} = wrap(theta_n + u_n); history of d+1 snapshots with constant prehistory; C_{n+1} = alpha C_n +
    (1-alpha) z_n with z_n = exp(i (theta_n,i - delayed_j - (omega_i + omega_j)/2 tau)), delayed = oldest snapshot."""
    n_nodes = len(x0)
    theta = [list(x0)]
    for n in range(steps):
        theta.append([(theta[n][i] + u(n, i)) % (2 * math.pi) for i in range(n_nodes)])
    cs = [c0]
    for n in range(steps):
        zs = [[cmath.exp(1j * (theta[n][i] - theta[max(n - d, 0)][j] - (omega[i] + omega[j]) / 2 * tau))
               for j in range(n_nodes)] for i in range(n_nodes)]
        cs.append([[alpha * cs[n][i][j] + (1 - alpha) * zs[i][j] for j in range(n_nodes)] for i in range(n_nodes)])
    return cs


def reported(c, i, j):
    return 0.0 if i == j else (abs(c[i][j]) + abs(c[j][i])) / 2


def test_asymmetric_zero_init_probe_pins_the_average():
    u = lambda n, i: math.pi / 2 if i == 0 else 0.0          # probeU2
    zero = [[0j, 0j], [0j, 0j]]
    cs = simulate(0.5, zero, 1, [0.0, 0.0], u, [0.0, 0.0], 0.0, 2)
    assert all(abs(cs[1][i][j] - 0.5) < 1e-12 for i in range(2) for j in range(2))
    assert abs(cs[2][0][1] - (0.25 + 0.5j)) < 1e-12 and abs(cs[2][1][0] - 0.75) < 1e-12
    assert abs(abs(cs[2][0][1]) - math.sqrt(5) / 4) < 1e-12 and abs(abs(cs[2][1][0]) - 0.75) < 1e-12
    assert abs(abs(cs[2][0][1]) - abs(cs[2][1][0])) > 0.1                       # probe_asym_directed_ne
    r = reported(cs[2], 0, 1)
    assert abs(r - (3 + math.sqrt(5)) / 8) < 1e-12 and reported(cs[2], 1, 0) == r   # probe_asym_reported(_swapped)
    # the one-sided mutants (N1) are far from the average, the diagonal mutant is far from 0 (N2)
    assert abs(abs(cs[2][0][1]) - r) > 0.09 and abs(abs(cs[2][1][0]) - r) > 0.09
    assert reported(cs[2], 0, 0) == 0.0 and abs(cs[2][0][0]) > 0.1               # probe_asym_reported_diag
    assert abs(3 * r - 1 - (3 * (3 + math.sqrt(5)) / 8 - 1)) < 1e-12              # probe_asym_drive (eta=2, mu=1)


def test_alpha_quarter_probe_detects_alpha_swap():
    u = lambda n, i: math.pi / 2 if i == 0 else 0.0
    zero = [[0j, 0j], [0j, 0j]]
    cs = simulate(0.25, zero, 1, [0.0, 0.0], u, [0.0, 0.0], 0.0, 1)
    assert all(abs(cs[1][i][j] - 0.75) < 1e-12 for i in range(2) for j in range(2))   # probe_alpha_quarter
    cs_swapped = simulate(0.75, zero, 1, [0.0, 0.0], u, [0.0, 0.0], 0.0, 1)             # alpha <-> 1 - alpha
    assert abs(cs_swapped[1][0][0] - 0.75) > 0.4
    half = simulate(0.5, zero, 1, [0.0, 0.0], u, [0.0, 0.0], 0.0, 1)
    assert abs(half[1][0][0] - 0.5) < 1e-12                       # alpha = 1/2 is self-dual: blind to the swap


def test_uniform_c0_one_probe_values():
    u = lambda n, i: math.pi / 2
    one = [[1 + 0j, 1 + 0j], [1 + 0j, 1 + 0j]]
    cs = simulate(0.5, one, 2, [0.0, 0.0], u, [1.0, 1.0], math.pi, 4)
    want = [0, -0.5j, 0.5 - 0.25j, 0.75 - 0.125j]                # probe_coherence_values (traces 1..4)
    for k, w in enumerate(want, start=1):
        assert abs(cs[k][0][1] - w) < 1e-9, k
    assert abs(reported(cs[2], 0, 1) - 0.5) < 1e-9                # probe_reported_second


# ---- mutants: shape, edits apply, pins exist, kill rule --------------------------------------------------------

def test_p5_mutants_shape_and_exact_count():
    assert len(mc.MUTANTS) == N_STATEMENT_MUTANTS                       # M1-M23, untouched
    assert len(mc.DEF_MUTANTS) == N_DEF_MUTANTS
    assert len(mc.MUTANTS) + len(mc.DEF_MUTANTS) == TOTAL_MUTANTS       # the exact pin (39 on this branch)
    names = [m[0] for m in mc.DEF_MUTANTS]
    assert names[0].startswith("M37") and names[-1].startswith("M52")
    assert [int(n.split("_")[0][1:]) for n in names] == list(range(37, 53))
    assert len({m[0] for m in mc.MUTANTS} & set(names)) == 0
    required = ("delay_plus_one", "delay_minus_one", "current_theta", "dropped_omega_tau", "phase_is_zero",
                "missing_eta", "swap_i_j", "conjugated", "alpha_swapped", "mu_sign", "next_input",
                "one_sided", "diagonal_one")
    for r in required:
        assert any(r in n for n in names), r


def test_def_mutants_apply_exactly_once_and_pins_are_value_probes():
    srcs = {"PhaseIncrement.lean": PI, "PhaseCoherence.lean": PC}
    rewrite_lemmas = ("input_engine_convention", "delayed_input_step", "innovation_engine_convention",
                      "innovation_transport", "reported_symm", "reported_offdiag", "reported_diag",
                      "main_preM_source_formula", "drive_eta_response", "coherenceTrace_unitDisk")
    for f, probes in mc.VALUE_PROBES.items():
        for p in probes:
            assert re.search(rf"^theorem {p}\b", srcs[f], re.M), (f, p)
            assert p.startswith("probe_") and p not in rewrite_lemmas
    for name, f, edits, pins in mc.DEF_MUTANTS:
        assert f in srcs, name
        assert mc.mutate_file(srcs[f], edits) != srcs[f], name        # each edit matches exactly `count` times
        assert pins and set(pins) <= set(mc.VALUE_PROBES[f]), (name, pins)   # credit only via VALUE probes
    for name, f, edits in mc.EQUIV_CONTROLS + mc.TYPO_CONTROLS + mc.KNOWN_SURVIVORS:
        assert mc.mutate_file(srcs[f], edits) != srcs[f], name


def test_controls_exist_with_exact_counts():
    assert len(mc.EQUIV_CONTROLS) == 9 and len(mc.TYPO_CONTROLS) == 3 and len(mc.STATEMENT_CONTROLS) == 2
    eq = {n.split("_")[0]: (n, e) for n, f, e in mc.EQUIV_CONTROLS}
    ci_new = {k: eq[k][1][0][1] for k in ("E1", "E2", "E3")}
    assert "* 1" in ci_new["E1"] and "+ 0" in ci_new["E2"] and "id (inputPhasor" in ci_new["E3"]   # the audit's three
    # one equivalent rewrite on each of: the 011 delayed read, the EMA step, reported
    assert {f for n, f, e in mc.EQUIV_CONTROLS if n.startswith(("E4", "E5", "E6"))} == {"PhaseIncrement.lean"}
    assert any(n.startswith("E7_ema") for n, f, e in mc.EQUIV_CONTROLS)
    assert any(n.startswith("E8_reported") for n, f, e in mc.EQUIV_CONTROLS)
    assert [n.split("_")[0] for n, f, e in mc.TYPO_CONTROLS] == ["T1", "T2", "T3"]
    assert "inputPhasorXX" in mc.TYPO_CONTROLS[0][2][0][1]
    assert [c[0].split("_")[0] for c in mc.STATEMENT_CONTROLS] == ["SE1", "ST1"]
    names = [m[0] for m in mc.DEF_MUTANTS] + [c[0] for c in mc.EQUIV_CONTROLS + mc.TYPO_CONTROLS]
    assert len(names) == len(set(names))


def test_def_mutants_never_edit_unlisted_files_and_survivor_is_only_the_011_offset():
    assert {m[1] for m in mc.DEF_MUTANTS} == {"PhaseIncrement.lean", "PhaseCoherence.lean"}
    assert [s[0] for s in mc.KNOWN_SURVIVORS] == ["S1_phase_input_dropped_offset_in_011_only"]
    # the offset is killed one level up by VALUE probes (audit fix): M43 pins probe_input_offset_value
    m43 = [m for m in mc.DEF_MUTANTS if m[0].startswith("M43")][0]
    assert m43[3] == ["probe_input_offset_value", "probe_coherence_values"]
    m51 = [m for m in mc.DEF_MUTANTS if m[0].startswith("M51")][0]
    m52 = [m for m in mc.DEF_MUTANTS if m[0].startswith("M52")][0]
    assert m51[3] == ["probe_asym_reported"] and m52[3] == ["probe_asym_reported_diag"]


def test_kill_rule_revised_negative_controls():
    real = ["Mutant.lean:10:2: error: type mismatch"]
    unk = ["Mutant.lean:60:2: error(lean.unknownIdentifier): Unknown identifier `inputPhasorXX`"]
    unkc = ["Mutant.lean:61:2: error(lean.unknownIdentifier): Unknown constant `foo`"]
    parse = ["Mutant.lean:60:37: error: unexpected token ')'; expected command"]
    msrc = "\n".join(["x"] * 3 + ["theorem pin_a : True := by", "  trivial", "theorem other : True := by"] +
                     ["  sorry"] * 4 + ["  rfl"])
    assert mc.failing_decls(msrc, ["Mutant.lean:5:3: error: boom"]) == ["pin_a"]
    assert mc.failing_decls(msrc, ["Mutant.lean:9:3: error: boom"]) == ["other"]
    st = mc.def_mutant_status
    assert st(1, real, ["pin_a"], ["pin_a"]) == "KILLED"
    assert st(1, real, ["other"], ["pin_a"]) == "SURVIVED"                    # only a rewrite lemma fails: no credit
    assert st(0, [], [], ["pin_a"]) == "BUILDS"
    for bad in (unk, unkc, parse, real + unk, unk + real):                    # ANY invalid line anywhere
        assert st(1, bad, ["pin_a"], ["pin_a"]) == "INVALID"
        assert not mc.def_mutant_killed(1, bad, ["pin_a"], ["pin_a"])
    # a type mismatch message mentions "expected to have type": it must NOT be read as a parse error
    mism = ["Mutant.lean:7:2: error: Type mismatch\n  has type A but is expected to have type B"]
    assert mc.invalid_lines(mism) == [] and st(1, mism, ["pin_a"], ["pin_a"]) == "KILLED"
    assert mc.invalid_lines(real + unk) == unk


def test_value_probe_statements_are_closed_value_equalities():
    # every VALUE probe states `f concrete = concrete` (an equality over concrete data, only node indices quantified)
    for f, src in (("PhaseIncrement.lean", PI), ("PhaseCoherence.lean", PC)):
        for p in mc.VALUE_PROBES[f]:
            st = _stmt(src, p)
            assert "=" in st, p
            assert not re.search(r"\((d|x0|u|omega|tau|alpha|C0|eta|mu|C) :", st), p   # no quantified data
