# CHANGES — 2026-10-28: fewer false e-mail warnings in the --pii scan (local only, not pushed)

Changed files (drop-in replacements for the copies integrated at merge-prep 21f4f35):
- `tools/ci/hygiene_scan.py`
- `tools/ci/tests/test_ci_tools.py`

What changed in `hygiene_scan.py` (only the `--pii` e-mail check; nothing else):
1. **Python matrix multiply is skipped.** A match like `M@np.array(...)` is ignored when the part after
   `@` starts with an array-library module (`np.`, `numpy.`, `jnp.`, `jax.numpy.`, `torch.`, `scipy.`, `sp.`,
   `la.`, `linalg.`, `sympy.`, `sm.`), or when the match runs straight into `(` or `[`. No mail address
   does either.
2. **Reserved domains are skipped** (RFC 2606 / RFC 6761): `.example`, `.invalid`, `.test`,
   `.localhost`, `localhost`, and `example.com/.net/.org` with any subdomain. The `.tld` placeholder
   is skipped as well, because it is not a real top-level domain. (The old code allowed only `example.com/org/net`
   and `localhost`, and only as the exact domain.)
3. Unchanged: GitHub noreply addresses and `noreply@`/`no-reply@`/`git@` are still skipped. Everything else
   still warns. `.local` is **not** skipped (it can name a real machine). Look-alikes such as
   `numpyfans.org`, `example-corp.com` and `testing.io` still warn.

New tests (18 total, all pass): matmul forms skipped; reserved domains skipped; a real-shaped synthetic
address, built at run time, still warns (alone, in brackets, after "np:"), plus the look-alike domains;
and an end-to-end scan where only the real-shaped line is reported, with the value never printed.

Result on a temporary copy of merge-prep 21f4f35 with the updated script:
- full scan with `--pii`: 0 errors and 3 warnings, all BIG_FILE (the 51–64 MiB trajectory CSVs). The 5 PII_EMAIL
  false positives are gone, and no PII warnings remain.
- changed since `main` (853498f) with `--pii`: 87 files, 0 errors, 0 warnings.
