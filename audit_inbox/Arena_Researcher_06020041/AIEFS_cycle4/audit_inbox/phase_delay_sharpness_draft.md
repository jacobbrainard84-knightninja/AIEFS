# Audit inbox draft: sharp delay threshold and conditional reported R

**Unverified research input; owner review requested. No claim promotion.**

On the proposed P5 + Cycle 2 + Cycle 3 stack, the input-constancy threshold n ≥ N+d is sharp in the universal sense for N,d ≥ 1. Choose nodes i≠j, zero initial phases/frequencies and τ, and u(N−1,j)=π with every other increment zero. At n=N+d−1 the delayed phase is still zero; at n+1 it is π. Thus the input changes from 1 to −1 despite all increments vanishing from N onward. This is a semantic counterexample to dropping +d, not just a proof failure. N=0 is a special case.

Also, mathematically composing Cycle 3's consecutive input equality with its EMA identity gives a geometric error formula from n₀=N+d. For 0≤α<1, off-diagonal P5 reported R satisfies 0≤1−R(n₀+k)≤2αᵏ if both directed C(n₀) entries lie in the unit disk. This is conditional on assumed phase freezing, not closed-loop locking, monotonicity, float behavior, or Python–Lean equivalence. Formalization and independent review are outstanding.

Evidence: `AIEFS_cycle4/ONE_PAGE_NOTE.md`, `test_delay_lock.py`, `test_log.txt`, `SHA256SUMS.txt` (workspace files, not repo additions). Run `python3 /home/user/AIEFS_cycle4/test_delay_lock.py`. Exact arithmetic checks 64 counterexample instances and 16 EMA families. No Lean or full gate run in this cycle. Main and P5 branch SHAs were rechecked; no merge or push was made. Earlier Cycle 3 claims were kernel-checked on pre-final-comment bytes, not reviewed independently. Suggested next step: formalize the semantic counterexample and composed off-diagonal bound on a reviewed stack, run project gate and mutation suite, and independently review.
