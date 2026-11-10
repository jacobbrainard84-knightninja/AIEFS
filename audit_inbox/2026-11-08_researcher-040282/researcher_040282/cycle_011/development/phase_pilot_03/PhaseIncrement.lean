/-
Modulo-safe coherence-input motion for a constant-prehistory delay queue.
Exact-real model; arbitrary increments may be feedback-generated. This file does
not formalize floating remainder, allocation, C/R/B evolution or phase locking.
-/
import HistoryBuffer
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Bounds
import Mathlib.Algebra.Order.Archimedean.Real.Basic
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith

set_option autoImplicit false
set_option linter.style.header false

namespace Researcher040282.Phase

variable {ι : Type*}

noncomputable def phasor (t : ℝ) : ℂ := Complex.exp ((t : ℂ) * Complex.I)

noncomputable def wrapPhase (t : ℝ) : ℝ :=
  t - (Int.floor (t / (2 * Real.pi)) : ℝ) * (2 * Real.pi)

noncomputable def phaseTrace (x0 : ι → ℝ) (u : ℕ → ι → ℝ) : ℕ → ι → ℝ
  | 0 => x0
  | n + 1 => fun i => wrapPhase (phaseTrace x0 u n i + u n i)

noncomputable def inputPhasor (d : ℕ) (x0 : ι → ℝ) (u : ℕ → ι → ℝ)
    (omega : ι → ℝ) (tau : ℝ) (n : ℕ) (i j : ι) : ℂ :=
  phasor (phaseTrace x0 u n i -
    Researcher040282.Delay.historyTrace d (phaseTrace x0 u) n ⟨0, Nat.zero_lt_succ d⟩ j -
    ((omega i + omega j) / 2) * tau)

noncomputable def delayedIncrement (d : ℕ) (u : ℕ → ι → ℝ) (n : ℕ) (j : ι) : ℝ :=
  if d ≤ n then u (n - d) j else 0

/-- Floor-based wrapping changes an angle only by an integer period. -/
theorem phasor_wrap (t : ℝ) : phasor (wrapPhase t) = phasor t := by
  unfold phasor wrapPhase
  push_cast
  rw [sub_mul, Complex.exp_sub, mul_assoc]
  simp only [Complex.exp_int_mul_two_pi_mul_I, div_one]

/-- Startup has zero delayed increment; the first live delayed increment is n=D. -/
theorem delayed_input_step (d : ℕ) (x0 : ι → ℝ) (u : ℕ → ι → ℝ)
    (omega : ι → ℝ) (tau : ℝ) (n : ℕ) (i j : ι) :
    inputPhasor d x0 u omega tau (n + 1) i j =
      inputPhasor d x0 u omega tau n i j *
        phasor (u n i - delayedIncrement d u n j) := by
  have hadd (a b : ℝ) : phasor (a + b) = phasor a * phasor b := by
    simp only [phasor, Complex.ofReal_add, add_mul, Complex.exp_add]
  have hsub (a b : ℝ) : phasor (a - b) = phasor a / phasor b := by
    simp only [phasor, Complex.ofReal_sub, sub_mul, Complex.exp_sub]
  have hstep (k : ℕ) (r : ι) :
      phasor (phaseTrace x0 u (k + 1) r) = phasor (phaseTrace x0 u k r) * phasor (u k r) := by
    change phasor (wrapPhase (phaseTrace x0 u k r + u k r)) = _
    rw [phasor_wrap, hadd]
  have hz : phasor 0 = 1 := by simp [phasor]
  simp only [inputPhasor, Researcher040282.Delay.historyTrace_oldest, hsub]
  by_cases hd : d ≤ n
  · have hs : n + 1 - d = (n - d) + 1 := by omega
    rw [hs, hstep, hstep]
    simp only [delayedIncrement, if_pos hd]
    field_simp [phasor, Complex.exp_ne_zero]
    <;> ring
  · have h0 : n - d = 0 := by omega
    have h1 : n + 1 - d = 0 := by omega
    simp only [h0, h1, hstep, delayedIncrement, if_neg hd, hz, div_one]
    field_simp [phasor, Complex.exp_ne_zero]
    <;> ring

/-- Circular chord bound, NOT a Euclidean difference of stored representatives. -/
theorem delayed_input_chord_bound (d : ℕ) (x0 : ι → ℝ) (u : ℕ → ι → ℝ)
    (omega : ι → ℝ) (tau : ℝ) (n : ℕ) (i j : ι) :
    ‖inputPhasor d x0 u omega tau (n + 1) i j - inputPhasor d x0 u omega tau n i j‖ ≤
      |u n i - delayedIncrement d u n j| := by
  rw [delayed_input_step]
  have heq : inputPhasor d x0 u omega tau n i j * phasor (u n i - delayedIncrement d u n j) -
      inputPhasor d x0 u omega tau n i j =
      inputPhasor d x0 u omega tau n i j * (phasor (u n i - delayedIncrement d u n j) - 1) := by ring
  rw [heq, norm_mul]
  have hnorm : ‖inputPhasor d x0 u omega tau n i j‖ = 1 := by
    unfold inputPhasor phasor
    exact Complex.norm_exp_ofReal_mul_I _
  rw [hnorm, one_mul]
  simpa only [phasor, mul_comm, Real.norm_eq_abs] using
    (Real.norm_exp_I_mul_ofReal_sub_one_le (x := u n i - delayedIncrement d u n j))

#print axioms Researcher040282.Phase.phasor_wrap
#print axioms Researcher040282.Phase.delayed_input_step
#print axioms Researcher040282.Phase.delayed_input_chord_bound

end Researcher040282.Phase
