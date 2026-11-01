"""Red-team negative controls: the b2a95dfbfbe3 reproduction comparator
(audits/reproductions/b2a95dfbfbe3/compare_b2a95dfbfbe3_v3.py, hash-pinned; run unmodified).

The comparator reads paths relative to its working directory, so each test builds a temp
workspace: read-only symlinks to the zip folder and the two source files, plus a REAL copy of
runs/5a9f093a2fe0 (the "official" side), which is then tampered. Expected verdict on every
tampered copy: NOT REPRODUCED (exit 1). GAP tests are expected failures."""
import csv
import io
import json
import os
import shutil
import unittest

import numpy as np

from rtcommon import PY, REPO, TempDirMixin, gap, run

CMP = os.path.join(REPO, "audits/reproductions/b2a95dfbfbe3/compare_b2a95dfbfbe3_v3.py")
RUN = "runs/5a9f093a2fe0"
CSV = "AIEF_1_4_5a9f093a2fe0_scalar_summary.csv"
DIAG = "AIEF_1_4_5a9f093a2fe0_branch_diagnostics.npz"
ZIP = os.path.join(REPO, "Project Histories", "workspace-019ff425-d36a-7d5d-bfa7-8e81a82fa8f2.zip")


def load_npz(p):
    with np.load(p, allow_pickle=False) as z:
        return {k: z[k] for k in z.files}


@unittest.skipUnless(os.path.isfile(ZIP) and os.path.isdir(os.path.join(REPO, RUN)), "zip or official run missing")
class Comparator(TempDirMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.w = os.path.join(self.tmp, "ws")
        os.makedirs(os.path.join(self.w, "runs"))
        for rel in ("Project Histories", "Older files", "AIEF_1_4_memory_ablation_updated.py"):
            os.symlink(os.path.join(REPO, rel), os.path.join(self.w, rel))
        shutil.copytree(os.path.join(REPO, RUN), os.path.join(self.w, RUN))
        self.run_dir = os.path.join(self.w, RUN)

    def compare(self):
        rc, out = run([PY, CMP], cwd=self.w)
        return rc, out

    def verdict_rejected(self):
        rc, out = self.compare()
        self.assertRejected(rc, out, '"verdict": "NOT REPRODUCED"')

    # --- helpers that tamper the temp copy -----------------------------------------------
    def edit_csv(self, fn):
        p = os.path.join(self.run_dir, CSV)
        with open(p, newline="") as f:
            rows = list(csv.reader(f))
        fn(rows)
        with open(p, "w", newline="") as f:
            csv.writer(f, lineterminator="\n").writerows(rows)

    def first_finite_numeric_cell(self, rows):
        hdr = rows[0]
        for j, name in enumerate(hdr):
            if name in ("branch", "branch_family"):
                continue
            try:
                v = float(rows[1][j])
            except ValueError:
                continue
            if np.isfinite(v) and v != 0:
                return j, v
        raise AssertionError("no finite numeric cell")

    def edit_npz(self, name, fn):
        p = os.path.join(self.run_dir, name)
        d = load_npz(p)
        fn(d)
        os.unlink(p)
        np.savez(p, **d)

    def first_float_field(self, d):
        for k in sorted(d):
            if d[k].dtype.kind == "f" and d[k].size and np.isfinite(d[k]).any():
                return k
        raise AssertionError("no float field")

    def seed_file(self):
        return sorted(f for f in os.listdir(self.run_dir) if f.startswith("seed_"))[0]

    # --- positive control ------------------------------------------------------------
    def test_00_control_untampered_copy_reproduces(self):
        rc, out = self.compare()
        self.assertEqual(rc, 0, out[-2000:])
        self.assertIn('"verdict": "REPRODUCED"', out)

    # --- tolerance -------------------------------------------------------------------
    def test_csv_cell_off_by_1e_9(self):
        def f(rows):
            j, v = self.first_finite_numeric_cell(rows)
            rows[1][j] = repr(v + 1e-9)
        self.edit_csv(f)
        self.verdict_rejected()

    def test_csv_cell_off_by_just_over_tolerance(self):
        def f(rows):
            j, v = self.first_finite_numeric_cell(rows)
            rows[1][j] = repr(v + 1e-11)          # TOL = 1e-12; float64 keeps this at |v| ~ 1
        self.edit_csv(f)
        self.verdict_rejected()

    # --- non-finite values -------------------------------------------------------------
    def _csv_set(self, text):
        def f(rows):
            j, _ = self.first_finite_numeric_cell(rows)
            rows[1][j] = text
        self.edit_csv(f)

    def test_csv_nan_injected(self):
        self._csv_set("nan"); self.verdict_rejected()

    def test_csv_pos_inf_injected(self):
        self._csv_set("inf"); self.verdict_rejected()

    def test_csv_neg_inf_injected(self):
        self._csv_set("-inf"); self.verdict_rejected()

    def test_branch_diagnostics_inf_injected(self):
        def f(d):
            k = self.first_float_field(d)
            a = d[k].copy(); a.flat[np.flatnonzero(np.isfinite(a))[0]] = np.inf; d[k] = a
        self.edit_npz(DIAG, f)
        self.verdict_rejected()

    def test_seed_nan_injected(self):
        def f(d):
            k = self.first_float_field(d)
            a = d[k].copy(); a.flat[np.flatnonzero(np.isfinite(a))[0]] = np.nan; d[k] = a
        self.edit_npz(self.seed_file(), f)
        self.verdict_rejected()

    # --- corrupted / missing seed files --------------------------------------------------
    def test_seed_value_changed(self):
        def f(d):
            k = self.first_float_field(d)
            a = d[k].copy(); i = np.flatnonzero(np.isfinite(a))[0]; a.flat[i] += 1e-6; d[k] = a
        self.edit_npz(self.seed_file(), f)
        self.verdict_rejected()

    def test_seed_file_bytes_corrupted(self):
        p = os.path.join(self.run_dir, self.seed_file())
        with open(p, "rb") as fh:
            data = fh.read()
        with open(p, "wb") as fh:
            fh.write(data[: len(data) // 2])
        rc, out = self.compare()
        self.assertNotEqual(rc, 0, out[-2000:])   # truncated npz: crashes (non-zero), never REPRODUCED
        self.assertNotIn('"verdict": "REPRODUCED"', out)

    def test_seed_file_deleted(self):
        os.unlink(os.path.join(self.run_dir, self.seed_file()))
        rc, out = self.compare()
        self.assertNotEqual(rc, 0, out[-2000:])   # crashes (FileNotFoundError): fails closed
        self.assertNotIn('"verdict": "REPRODUCED"', out)

    def test_extra_fabricated_seed_file(self):
        src = os.path.join(self.run_dir, self.seed_file())
        shutil.copy(src, os.path.join(self.run_dir, "seed_99999999999999999999.npz"))
        self.verdict_rejected()

    def test_seed_integer_field_changed(self):
        self.edit_npz(self.seed_file(), lambda d: d.__setitem__("seed", d["seed"] + 1))
        self.verdict_rejected()

    # --- swapped / relabelled data -------------------------------------------------------
    def test_two_numeric_columns_swapped(self):
        def f(rows):
            hdr = rows[0]
            num = [j for j, n in enumerate(hdr) if n not in ("branch", "branch_family")]
            a, b = num[0], num[1]
            for r in rows[1:]:
                r[a], r[b] = r[b], r[a]
        self.edit_csv(f)
        self.verdict_rejected()

    def test_manifest_model_parameter_changed(self):
        p = os.path.join(self.run_dir, "manifest.json")
        with open(p) as f:
            m = json.load(f)
        m["model"]["eta"] = 0.05 if m["model"].get("eta") != 0.05 else 0.04
        with open(p, "w") as f:
            json.dump(m, f)
        self.verdict_rejected()

    @gap("comparator: relabelling rows in the CSV's text columns (branch names) still gives REPRODUCED")
    def test_GAP_csv_branch_labels_swapped(self):
        def f(rows):
            j = rows[0].index("branch")
            labels = sorted({r[j] for r in rows[1:]})
            a, b = labels[0], labels[1]
            for r in rows[1:]:
                r[j] = b if r[j] == a else a if r[j] == b else r[j]
        self.edit_csv(f)
        self.verdict_rejected()

    @gap("comparator: manifest 'schema' field differs but is not part of the verdict")
    def test_GAP_manifest_schema_changed(self):
        p = os.path.join(self.run_dir, "manifest.json")
        with open(p) as f:
            m = json.load(f)
        m["schema"] = "tampered-schema"
        with open(p, "w") as f:
            json.dump(m, f)
        self.verdict_rejected()

    def test_selftest_still_passes(self):
        rc, out = run([PY, CMP, "--selftest"], cwd=self.w)
        self.assertEqual(rc, 0, out)


if __name__ == "__main__":
    unittest.main()
