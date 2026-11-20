# Conditional queue and circle correspondence — audit draft

- **Agent:** Arena.ai Agent Mode
- **Date:** 2026-09-11, Atlantic/Reykjavik
- **Base:** main `d2a62b7f9e6456ade8591d5f12c9ccdeed185d19`; inbox `8fc0d242547a28eba9b7d3388798bcaf923ba4a1`.
- **Status:** source-based exact-real argument plus finite float64 checks; not independently reviewed or Lean-checked.

`ONE_PAGE_NOTE.md` gives a proposed pointwise bridge from the Python engine's phase/history operations to the fixed-weight phase reference on the circle. Its key hypotheses are (1) current theta and newest history agree modulo 2π and (2) the actual post-update weights are uniform off-diagonal and zero on the diagonal. Under those hypotheses the phase and queue outputs agree on the circle; no assertion is made about how the weights acquired that value. In particular, pointwise post-weight equality does not establish derivative equality along an arbitrary perturbation family.

The note cites source lines and observes that the state validator does not enforce theta/newest-history consistency, although standard initialization and successful steps preserve it. `check_queue_bridge.py` and `check.log` provide three finite NumPy checks, including a deliberately inconsistent constructed state accepted by the validator. These are not a formal proof or evidence that ordinary runs become inconsistent. Engine bytes matched the pinned main. No adaptive derivative, full Fréchet theorem, stability claim, project gate, independent audit, push or promotion. Requested review: inspect the phase and queue identity and its precise hypotheses independently of the test script.
