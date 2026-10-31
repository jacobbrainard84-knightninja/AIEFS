"""Re-apply three versions of the slow-pole verdict rule to the committed spectrum (ERRATA E15).

Reads only committed data (no Jacobian is recomputed, nothing is written):
  aief_1_4_augmented_spectrum/augmented_eigenvalues.csv   (14 rows written by the current script)
  aief_1_4_augmented_spectrum/analysis_manifest.json      (r_EMA, mu_phase, dt)

Rules, as written in the three tracked copies of the analysis script:
  v1   Older files/aief_1_4_augmented_spectrum.py     L277 relevant=|l|>1e-14;  L281 gap=(r_ema, mu);
                                                      L327 "no eigenvalues in gap" if n_in_gap == 0
  v2   Older files/aief_1_4_augmented_spectrum_02.py  L284 relevant=|l|>1e-14 & rate<100; L288 gap=(r_ema, mu);
                                                      L294 near=(0.9 r_ema, 1.1 r_ema); L341 SUPPORTED iff
                                                      n_in_gap == 0 and n_near == 1; L346 PARTIAL iff n_in_gap == 0;
                                                      L350 REVISED iff n_in_gap > 0
  cur  aief_1_4_augmented_spectrum.py                 L291 gap=(1.01 r_ema, mu); L297 near=(0.99 r_ema, 1.01 r_ema);
                                                      L344 SUPPORTED iff n_in_gap == 0 and n_near >= 1

v2 and cur differ only in the verdict lines, so the committed eigenvalues are exactly what v2 would have
produced. v1 differs from v2 in ~300 other lines (the state map), so applying the v1 rule here is a
counterfactual about the rule only, not a re-run of v1.

The CSV holds only the rows the current script calls relevant (|l| > 1e-14 and rate < 100). Its sorted
indices are 0..13 with no holes, so the 4 omitted eigenvalues (of 18) all have rate >= the largest kept rate
(31.71 > mu_phase): they cannot fall in any gap or near-EMA band under any of the three rules.

Run from the repository root:  python3 audits/old_files_drift/recheck_slowpole_rule.py
Committed output: audits/old_files_drift/recheck_slowpole_rule_output.txt
Exit status 0 iff all consistency checks against the committed CSV/report pass.
"""

import csv
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "aief_1_4_augmented_spectrum"


def main() -> int:
    manifest = json.loads((SPEC / "analysis_manifest.json").read_text(encoding="utf-8"))
    params = manifest["parameters"]
    r_ema = float(params["r_EMA"])
    mu = float(params["mu_phase"])
    dt = float(params["dt"])

    with open(SPEC / "augmented_eigenvalues.csv", newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    problems = []
    idx = [int(r["index"]) for r in rows]
    if idx != list(range(len(rows))):
        problems.append(f"CSV indices are not 0..{len(rows) - 1}: {idx}")
    rates = []
    for r in rows:
        rate = float(r["rate"])
        absl = float(r["abs_eval"])
        if not math.isclose(rate, -math.log(absl) / dt, rel_tol=1e-9, abs_tol=1e-12):
            problems.append(f"row {r['index']}: rate {rate} != -log|l|/dt")
        rates.append(rate)
    if rates != sorted(rates):
        problems.append("CSV rates are not sorted ascending")
    if max(rates) <= mu:
        problems.append("largest kept rate <= mu_phase; omitted rows could matter")

    def count(lo, hi):
        return sum(1 for x in rates if lo < x < hi)

    # Cross-check the current rule against the flags the current script wrote into the CSV.
    cur_gap_flags = sum(r["in_gap"] == "True" for r in rows)
    cur_near_flags = sum(r["near_ema"] == "True" for r in rows)

    res = {}
    n = count(r_ema, mu)
    res["v1"] = (n, None, "NO eigenvalues in the gap (alpha 'unique slow pole')" if n == 0
                 else f"{n} eigenvalue(s) found in the gap")
    n, k = count(r_ema, mu), count(0.9 * r_ema, 1.1 * r_ema)
    res["v2"] = (n, k, "SUPPORTED" if n == 0 and k == 1 else "PARTIAL" if n == 0 else f"REVISED ({n} in gap)")
    n, k = count(1.01 * r_ema, mu), count(0.99 * r_ema, 1.01 * r_ema)
    res["cur"] = (n, k, "SUPPORTED" if n == 0 and k >= 1 else "PARTIAL" if n == 0 else f"REVISED ({n} in gap)")

    if (res["cur"][0], res["cur"][1]) != (cur_gap_flags, cur_near_flags):
        problems.append(f"current rule {res['cur'][:2]} != CSV flags {(cur_gap_flags, cur_near_flags)}")
    report = (SPEC / "augmented_spectrum_report.txt").read_text(encoding="utf-8")
    if "VERDICT: SUPPORTED." not in report:
        problems.append("committed report does not say VERDICT: SUPPORTED.")

    dim = next((ln.split(":")[1].split()[0] for ln in report.splitlines() if ln.startswith("dimension:")), "?")
    print(f"inputs: {len(rows)} CSV rows (of {dim} eigenvalues), r_EMA={r_ema!r}, mu_phase={mu!r}, dt={dt!r}")
    print(f"committed report verdict: {'SUPPORTED' if 'VERDICT: SUPPORTED.' in report else '?'}")
    print("rates (slowest first): " + ", ".join(f"{x:.9g}" for x in rates))
    print(f"unstable (rate < 0, |l| > 1): {sum(x < 0 for x in rates)}; "
          f"stable but below the current near band (0 <= rate <= 0.99 r_EMA): {[round(x, 9) for x in rates if 0 <= x <= 0.99 * r_ema]}")
    print()
    print(f"{'rule':4} {'gap interval':>26} {'n_in_gap':>8} {'near band':>24} {'n_near':>6}  verdict")
    bands = {
        "v1": ((r_ema, mu), None),
        "v2": ((r_ema, mu), (0.9 * r_ema, 1.1 * r_ema)),
        "cur": ((1.01 * r_ema, mu), (0.99 * r_ema, 1.01 * r_ema)),
    }
    for key in ("v1", "v2", "cur"):
        (glo, ghi), near = bands[key]
        n, k, verdict = res[key]
        nb = "-" if near is None else f"({near[0]:.6f}, {near[1]:.6f})"
        print(f"{key:4} {f'({glo:.6f}, {ghi:.6f})':>26} {n:>8} {nb:>24} {'-' if k is None else k:>6}  {verdict}")
    print()
    print(f"in v1/v2 gap: {[round(x, 9) for x in rates if r_ema < x < mu]}")
    print(f"current-rule CSV flags: in_gap={cur_gap_flags}, near_ema={cur_near_flags}")
    print(f"problems: {problems}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
