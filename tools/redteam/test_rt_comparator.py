"""Red-team negative controls: the b2a95dfbfbe3 reproduction comparator
(audits/reproductions/b2a95dfbfbe3/compare_b2a95dfbfbe3_v4.py, run unmodified; v4 supersedes v3, which is kept
unchanged as the record behind the v3 log, and closes the two v3 GAPs G10/G11).

The comparator reads paths relative to its working directory, so each test builds a temp
workspace: read-only symlinks to the zip folder and the two source files, plus a REAL copy of
runs/5a9f093a2fe0 (the "official" side), which is then tampered. Expected verdict on every
tampered copy: NOT REPRODUCED (exit 1) AND the specific reason in "problems" (every rejection test
asserts its own needle, so a crash or an unrelated problem cannot count as a PASS)."""
import csv
import io
import json
import os
import shutil
import unittest

import numpy as np

from rtcommon import PY, REPO, TempDirMixin, run

CMP = os.path.join(REPO, "audits/reproductions/b2a95dfbfbe3/compare_b2a95dfbfbe3_v4.py")
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

    def verdict_rejected(self, *reasons):
        """NOT REPRODUCED, exit 1 (a verdict, not a crash), no Traceback, and each reason in the output."""
        rc, out = self.compare()
        self.assertRejected(rc, out, '"verdict": "NOT REPRODUCED"', *reasons)
        self.assertEqual(rc, 1, out[-2000:])
        self.assertNotIn("Traceback", out)
        return out

    def set_manifest(self, fn):
        p = os.path.join(self.run_dir, "manifest.json")
        with open(p) as f:
            m = json.load(f)
        fn(m)
        with open(p, "w") as f:
            json.dump(m, f)

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
        self.assertIn('"problems": []', out)

    # --- tolerance -------------------------------------------------------------------
    def test_csv_cell_off_by_1e_9(self):
        def f(rows):
            j, v = self.first_finite_numeric_cell(rows)
            rows[1][j] = repr(v + 1e-9)
        self.edit_csv(f)
        self.verdict_rejected("worst abs diff", "> TOL")

    def test_csv_cell_off_by_just_over_tolerance(self):
        def f(rows):
            j, v = self.first_finite_numeric_cell(rows)
            rows[1][j] = repr(v + 1e-11)          # TOL = 1e-12; float64 keeps this at |v| ~ 1
        self.edit_csv(f)
        self.verdict_rejected("worst abs diff", "> TOL")

    # --- non-finite values -------------------------------------------------------------
    def _csv_set(self, text):
        def f(rows):
            j, _ = self.first_finite_numeric_cell(rows)
            rows[1][j] = text
        self.edit_csv(f)

    def test_csv_nan_injected(self):
        self._csv_set("nan"); self.verdict_rejected("scalar summary CSV: NaN pattern differs in 1 cells")

    def test_csv_pos_inf_injected(self):
        self._csv_set("inf"); self.verdict_rejected("scalar summary CSV: +inf pattern differs in 1 cells")

    def test_csv_neg_inf_injected(self):
        self._csv_set("-inf"); self.verdict_rejected("scalar summary CSV: -inf pattern differs in 1 cells")

    def test_branch_diagnostics_inf_injected(self):
        def f(d):
            k = self.first_float_field(d)
            a = d[k].copy(); a.flat[np.flatnonzero(np.isfinite(a))[0]] = np.inf; d[k] = a
        self.edit_npz(DIAG, f)
        self.verdict_rejected("branch_diagnostics:", "+inf pattern differs")

    def test_seed_nan_injected(self):
        def f(d):
            k = self.first_float_field(d)
            a = d[k].copy(); a.flat[np.flatnonzero(np.isfinite(a))[0]] = np.nan; d[k] = a
        self.edit_npz(self.seed_file(), f)
        self.verdict_rejected(f"{self.seed_file()}:", "NaN pattern differs")

    # --- corrupted / missing seed files --------------------------------------------------
    def test_seed_value_changed(self):
        def f(d):
            k = self.first_float_field(d)
            a = d[k].copy(); i = np.flatnonzero(np.isfinite(a))[0]; a.flat[i] += 1e-6; d[k] = a
        self.edit_npz(self.seed_file(), f)
        self.verdict_rejected("worst abs diff", "> TOL")

    def test_seed_file_bytes_corrupted(self):
        p = os.path.join(self.run_dir, self.seed_file())
        with open(p, "rb") as fh:
            data = fh.read()
        with open(p, "wb") as fh:
            fh.write(data[: len(data) // 2])
        self.verdict_rejected(f"{self.seed_file()}: unreadable in official run")   # v3: Traceback

    def test_seed_file_deleted(self):
        f = self.seed_file()
        os.unlink(os.path.join(self.run_dir, f))
        self.verdict_rejected(f"seed files missing in official run: ['{f}']", "seed file count")   # v3: Traceback

    def test_extra_fabricated_seed_file(self):
        src = os.path.join(self.run_dir, self.seed_file())
        shutil.copy(src, os.path.join(self.run_dir, "seed_99999999999999999999.npz"))
        self.verdict_rejected("seed files only in official run: ['seed_99999999999999999999.npz']", "seed file count")

    def test_seed_integer_field_changed(self):
        self.edit_npz(self.seed_file(), lambda d: d.__setitem__("seed", d["seed"] + 1))
        self.verdict_rejected(":seed: DIFF")

    # --- swapped / relabelled data -------------------------------------------------------
    def test_two_numeric_columns_swapped(self):
        def f(rows):
            hdr = rows[0]
            num = [j for j, n in enumerate(hdr) if n not in ("branch", "branch_family")]
            a, b = num[0], num[1]
            for r in rows[1:]:
                r[a], r[b] = r[b], r[a]
        self.edit_csv(f)
        self.verdict_rejected("worst abs diff", "> TOL")

    def test_manifest_model_parameter_changed(self):
        self.set_manifest(lambda m: m["model"].__setitem__("eta", 0.05 if m["model"].get("eta") != 0.05 else 0.04))
        self.verdict_rejected("manifest: model differs")

    # Former GAP G10 (v3 computed csv_nonnumeric_equal but did not gate on it); closed in v4.
    def test_csv_branch_labels_swapped(self):
        def f(rows):
            j = rows[0].index("branch")
            labels = sorted({r[j] for r in rows[1:]})
            a, b = labels[0], labels[1]
            for r in rows[1:]:
                r[j] = b if r[j] == a else a if r[j] == b else r[j]
        self.edit_csv(f)
        self.verdict_rejected("scalar summary CSV: non-numeric columns differ: branch (", '"csv_nonnumeric_equal": false')

    # Former GAP G11 (v3 computed schema_equal but did not gate on it); closed in v4.
    def test_manifest_schema_changed(self):
        self.set_manifest(lambda m: m.__setitem__("schema", "tampered-schema"))
        self.verdict_rejected("manifest: schema differs", '"schema_equal": false')

    # --- v4 gates on fields v3 computed but ignored ------------------------------------------
    def test_csv_branch_family_relabelled(self):
        def f(rows):
            j = rows[0].index("branch_family")
            rows[1][j] = "memory_ablation" if rows[1][j] != "memory_ablation" else "reference"
        self.edit_csv(f)
        self.verdict_rejected("non-numeric columns differ: branch_family (1 cells)")

    def test_manifest_unexpected_key_differs(self):
        self.set_manifest(lambda m: m.__setitem__("workflow_version", m.get("workflow_version", "") + "-tampered"))
        self.verdict_rejected("manifest: unexpected differing keys ['workflow_version']")

    def test_manifest_extra_key_added(self):
        self.set_manifest(lambda m: m.__setitem__("notes", "added after the fact"))
        self.verdict_rejected("manifest: unexpected differing keys ['notes']")

    def test_manifest_official_source_sha256_rewritten(self):
        self.set_manifest(lambda m: m.__setitem__("source_sha256", "0" * 64))
        self.verdict_rejected("manifest: official source_sha256 is not sha256(Older files/AIEF_1_4_memory_ablation_updated.py)")

    def test_manifest_official_config_hash_rewritten(self):
        self.set_manifest(lambda m: m.__setitem__("config_hash", "b2a95dfbfbe3"))
        self.verdict_rejected("manifest: official config_hash 'b2a95dfbfbe3' is not the run id '5a9f093a2fe0'")

    def test_seed_config_hash_label_rewritten(self):
        self.edit_npz(self.seed_file(), lambda d: d.__setitem__("config_hash", np.array("b2a95dfbfbe3")))
        self.verdict_rejected(f"{self.seed_file()}:config_hash: label ('b2a95dfbfbe3', 'b2a95dfbfbe3')")

    def test_rerun_source_file_edited(self):
        p = os.path.join(self.w, "AIEF_1_4_memory_ablation_updated.py")
        with open(p) as f:
            src = f.read()
        os.unlink(p)                                   # the symlink, not the repo file
        with open(p, "w") as f:
            f.write(src + "\nRT_EXTRA_CODE = 1\n")
        self.verdict_rejected("source diff: 3 code line(s) differ from the expected one-line rewrite",
                              "manifest: rerun source_sha256 is not sha256(AIEF_1_4_memory_ablation_updated.py)")

    def test_csv_zero_cell_set_to_1e_14(self):
        """|diff| = 1e-14 <= TOL, but relative diff = 1: v3's absolute-only TOL accepted this; v4's RTOL does not."""
        def f(rows):
            for r in rows[1:]:
                for j, name in enumerate(rows[0]):
                    if name not in ("branch", "branch_family") and r[j] in ("0", "0.0"):
                        r[j] = "1e-14"; return
            raise AssertionError("no zero cell")
        self.edit_csv(f)
        out = self.verdict_rejected("worst relative diff", "> RTOL")
        self.assertNotIn("> TOL", out)

    def test_official_csv_deleted(self):
        os.unlink(os.path.join(self.run_dir, CSV))
        self.verdict_rejected("scalar summary CSV: official file missing or unreadable (FileNotFoundError)")

    def test_official_branch_diagnostics_deleted(self):
        os.unlink(os.path.join(self.run_dir, DIAG))
        self.verdict_rejected(f"{DIAG}: missing in official run")

    def test_selftest_still_passes(self):
        rc, out = run([PY, CMP, "--selftest"], cwd=self.w)
        self.assertEqual(rc, 0, out)
        self.assertIn("selftest OK", out)


if __name__ == "__main__":
    unittest.main()
