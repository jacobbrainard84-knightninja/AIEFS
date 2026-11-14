"""Frequency-lock rework (SPEC §14): pin FrequencyLock.lean without running Lean.

Checks that the module is imported by the library root and hash-pinned, that it has no escape hatches, that the
lock hypothesis is a lock of one pair (i, j) (not the frozen `u n i = 0` of the Arena cycle 3/5 deposit, and not
an all-nodes lock), that the periodic theorem carries the period condition, that every named theorem exists with a
`#print axioms` line, that mutants M85-M91 and control E16 are registered, and recomputes the engine-alpha step
counts quoted in the docs from dt and the omegas parsed out of the engine source.

Run: /workspace/venv-pt/bin/pytest -q research/lean_gate/tests/test_lean_gate_freqlock.py
"""
import hashlib
import math
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PROJ = REPO / "lean" / "AIEFGateCore"
F = PROJ / "AIEFGateCore" / "FrequencyLock.lean"
SRC = F.read_text()

THEOREMS = ["input_step_of_common_increment", "coherenceInput_constant_of_periodicPairRate",
            "coherenceInput_constant_of_pairLock", "coherenceTrace_error_of_pairLock",
            "coherenceTrace_norm_of_pairLock", "reported_of_pairLock", "probe_unitRate_nonzero",
            "frequencyLock_nonzero_rate", "common_rate_input_not_constant", "common_rate_input_ne_zero",
            "periodic_rate_input_constant", "probe_altU_not_constant", "nonperiodic_rate_refuted",
            "probe_pairLock_one_step", "pairLock_factor_two_refuted", "pairLock_norm_factor_two_refuted",
            "half_lock_refuted", "delay_start_refuted"]
PRINTED = [t for t in THEOREMS if t != "common_rate_input_ne_zero"]
PAIR_LOCK = "(hlock : ∀ n, N ≤ n → u n i = c ∧ u n j = c)"           # constant rate, the pair (i, j) only
PERIODIC_LOCK = "(hlock : ∀ n, N ≤ n → u n i = c n ∧ u n j = c n)"
PERIOD = "(hper : ∀ n, N + d ≤ n → c n = c (n - d))"


def code():
    s = re.sub(r"/-.*?-/", "", SRC, flags=re.S)
    return re.sub(r"--.*", "", s)


def test_imported_and_hash_pinned():
    root = (PROJ / "AIEFGateCore.lean").read_text()
    assert re.search(r"^import AIEFGateCore\.FrequencyLock$", root, re.M)
    sums = (PROJ / "AIEF_LEAN_GATE_SOURCE_SHA256SUMS.txt").read_text()
    assert f"{hashlib.sha256(F.read_bytes()).hexdigest()}  AIEFGateCore/FrequencyLock.lean" in sums


def test_no_escape_hatches():
    c = code()
    for bad in ("sorry", "admit", "native_decide", "axiom ", "unsafe", "implemented_by", "extern", "opaque"):
        assert bad not in c, bad


def test_theorems_and_axiom_prints():
    for t in THEOREMS:
        assert re.search(rf"^theorem {t}\b", SRC, re.M), t
    for t in PRINTED:
        assert f"#print axioms AIEFGate.FrequencyLock.{t}\n" in SRC, t


def head(t):
    c = code()
    body = c[c.index(f"theorem {t}"):]
    return " ".join(body[:body.index(":=")].split())


def test_lock_is_pairwise_not_frozen_not_global():
    c = code()
    assert "u n i = 0" not in c                                   # the frozen hypothesis of the deposit is gone
    assert "∀ i, u n i = c" not in " ".join(c.split())            # no all-nodes lock (B2: pair only)
    h = head("coherenceInput_constant_of_periodicPairRate")
    assert PERIODIC_LOCK in h and PERIOD in h and "(hn : N + d ≤ n)" in h
    for t in ["coherenceInput_constant_of_pairLock", "coherenceTrace_error_of_pairLock",
              "coherenceTrace_norm_of_pairLock", "reported_of_pairLock"]:
        assert PAIR_LOCK in head(t), t
    assert "(hn : N + d ≤ n)" in head("coherenceInput_constant_of_pairLock")
    assert "(hij : i ≠ j)" in head("reported_of_pairLock")
    assert "unitRate 0 0 ≠ 0" in head("frequencyLock_nonzero_rate")   # N3: nonzero rate is in the statement


def test_conclusions_exact():
    flat = " ".join(code().split())
    assert "1 - 2 * alpha ^ k ≤ reported (coherenceTrace alpha C0 d x0 u omega tau (N + d + k)) i j" in flat
    assert "1 - 2 * alpha ^ k ≤ ‖coherenceTrace alpha C0 d x0 u omega tau (N + d + k) i j‖" in flat
    assert ("coherenceInput d x0 u omega tau n i j = coherenceInput d x0 u omega tau (N + d) i j" in flat)
    assert "coherenceInput d x0 u omega tau n i j * phasor (c n - c (n - d))" in flat
    assert "= - coherenceInput 1 (fun _ => 0) altU (fun _ => 0) 0 n 0 1" in flat
    assert "def altU (n : ℕ) (_ : Fin 2) : ℝ := if n % 2 = 0 then Real.pi else 0" in flat
    assert "def unitRate (_ : ℕ) (_ : Fin 2) : ℝ := 1" in flat


def test_mutants_registered():
    import sys
    sys.path.insert(0, str(HERE.parent))
    import lean_mutation_check as mc
    st = [m for m in mc.MUTANTS if m[1] == "FrequencyLock.lean"]
    de = [m for m in mc.DEF_MUTANTS if m[1] == "FrequencyLock.lean"]
    assert [m[0].split("_")[0] for m in st] == ["M85", "M86", "M87", "M88", "M89"]
    assert [m[0].split("_")[0] for m in de] == ["M90", "M91"]
    for name, f, thm, edits, closure, term, _ in st:
        assert mc.mutate(SRC, thm, edits) != SRC, name               # edit inside that statement only
        assert term.startswith("FrequencyLock.") and "_refuted (@H " in term, name
    for name, f, edits, pins in de:
        assert mc.mutate_file(SRC, edits) != SRC and set(pins) <= set(mc.VALUE_PROBES[f]), name
    eq = [c for c in mc.EQUIV_CONTROLS if c[1] == "FrequencyLock.lean"]
    assert [c[0].split("_")[0] for c in eq] == ["E16"] and mc.mutate_file(SRC, eq[0][2]) != SRC


def engine_constants():
    """dt and T_window read from the engine source (N4), not hard-coded here."""
    eng = (REPO / "aief_experiment_engine_v1.py").read_text()
    assert "return float(np.exp(-self.dt / self.T_window))" in eng
    assert re.search(r"^FROZEN_T_STAR = 25\.0 / FROZEN_MEAN_OMEGA\b", eng, re.M)
    assert re.search(r"^FROZEN_T_WINDOW = FROZEN_T_STAR\b", eng, re.M)
    assert re.search(r"^FROZEN_MEAN_OMEGA = float\(np\.mean\(FROZEN_OMEGA\)\)", eng, re.M)
    dt = float(re.search(r"^FROZEN_DT = ([0-9.]+)", eng, re.M).group(1))
    om = re.search(r"^FROZEN_OMEGA = np\.array\(\[(.*?)\]", eng, re.M | re.S).group(1)
    omega = [float(x) for x in re.findall(r"[0-9]+\.[0-9]+", om)]
    assert len(omega) == 12
    return dt, 25.0 / (sum(omega) / len(omega))


def test_engine_alpha_step_count():
    dt, t_window = engine_constants()
    alpha = math.exp(-dt / t_window)
    k = next(k for k in range(1, 10 ** 5) if 1 - 2 * alpha ** k > 0.5)
    half = next(k for k in range(1, 10 ** 5) if alpha ** k <= 0.5)
    spec = (HERE.parent / "SPEC_P1_gate_identities.md").read_text()
    assert (k, half) == (2427, 1214)
    assert "k = 2427" in SRC and "k = 1214" in SRC and "`k = 2427`" in spec and "`k = 1214`" in spec
