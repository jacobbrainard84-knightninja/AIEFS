# Final adversarial addendum — input provenance, before the new control

The original plan already requires rejection of a constant/manufactured projected
answer. A final source read found a stronger version of that falsifier: the first
candidate builds its Fraction oracle from the mutable proposal AFTER calling the
operator. A substituted operator could rewrite that argument to the default
fixture and return the default answer, so the oracle would verify the wrong
requested input consistently.

Test this BEFORE changing the candidate: supply the distinct valid input
(.40,.26,.30), substitute an operator that rewrites its argument to(.41,.27,.31),
then returns the genuine map at the rewritten input. The checker must reject
rather than certify the substituted fixture. If it passes, preserve the failing
control and fix the candidate to snapshot/construct the oracle before the call,
and reject unexpected mutation. This is a falsifier of OUR candidate, not a
claim that the current-main pure helper actually mutates its argument.

Do not change numerical allowances, main source, positive box, default/negative
fixtures or the original finding. Repeat the final complete suite and one-note
extraction after any fix. Retain the successful20/21-method development records
separately from the final suite. Stop after this bounded check and packaging.
