"""Frequency-lock rework (SPEC §13): pin FrequencyLock.lean without running Lean.

Checks that the module is imported by the library root and hash-pinned, that it has no escape hatches, that the
lock hypothesis is the constant common rate (not the frozen `u n i = 0` of the Arena cycle 3/5 deposit), that every
named theorem exists with a `#print axioms` line, and recomputes the engine-alpha step count quoted in the docs.

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

THEOREMS = ["input_step_of_common_increment", "coherenceInput_step_of_frequencyLock",
            "coherenceInput_constant_of_frequencyLock", "coherenceTrace_error_of_frequencyLock",
            "coherenceTrace_norm_of_frequencyLock", "reported_of_frequencyLock", "frequencyLock_nonzero_rate",
            "common_rate_input_not_constant", "common_rate_input_ne_zero"]
PRINTED = ["input_step_of_common_increment", "coherenceInput_constant_of_frequencyLock",
           "coherenceTrace_error_of_frequencyLock", "coherenceTrace_norm_of_frequencyLock",
           "reported_of_frequencyLock", "common_rate_input_not_constant", "frequencyLock_nonzero_rate"]
LOCK = "(N : ℕ) (hlock : ∀ n, N ≤ n → ∀ i, u n i = c)"


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


def test_lock_is_constant_common_rate_not_frozen():
    c = code()
    assert "u n i = 0" not in c                                   # the frozen hypothesis of the deposit is gone
    for t in ["coherenceInput_step_of_frequencyLock", "coherenceInput_constant_of_frequencyLock",
              "coherenceTrace_error_of_frequencyLock", "coherenceTrace_norm_of_frequencyLock",
              "reported_of_frequencyLock"]:
        body = c[c.index(f"theorem {t}"):]
        head = body[:body.index(":= by") if ":= by" in body[:1500] else 1500]
        assert LOCK in " ".join(head.split()), t


def test_conclusions_exact():
    flat = " ".join(code().split())
    assert "1 - 2 * alpha ^ k ≤ reported (coherenceTrace alpha C0 d x0 u omega tau (N + d + k)) i j" in flat
    assert "1 - 2 * alpha ^ k ≤ ‖coherenceTrace alpha C0 d x0 u omega tau (N + d + k) i j‖" in flat
    assert ("coherenceInput d x0 u omega tau n i j = coherenceInput d x0 u omega tau (N + d) i j" in flat)
    assert "coherenceInput d x0 u omega tau n i j * phasor (c n - c (n - d))" in flat
    assert "= - coherenceInput 1 (fun _ => 0) altU (fun _ => 0) 0 n 0 1" in flat


def test_engine_alpha_step_count():
    alpha = math.exp(-0.01 / 17.502917152858814)                 # engine alpha = exp(-dt / T_window), frozen values
    k = math.ceil(math.log(0.25) / math.log(alpha))               # 1 - 2 alpha^k > 1/2  <=>  alpha^k < 1/4
    assert k == 2427 and "k = 2427" in SRC and "`k = 2427`" in (HERE.parent / "SPEC_P1_gate_identities.md").read_text()
    eng = (REPO / "aief_experiment_engine_v1.py").read_text()
    assert "return float(np.exp(-self.dt / self.T_window))" in eng and "FROZEN_DT = 0.01" in eng
