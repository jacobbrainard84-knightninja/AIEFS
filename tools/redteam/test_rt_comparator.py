"""Red-team negative controls: the b2a95dfbfbe3 reproduction comparator
(audits/reproductions/b2a95dfbfbe3/compare_b2a95dfbfbe3_v4.py, run unmodified; v4 supersedes v3, which is kept
unchanged as the record behind the v3 log, and closes the two v3 GAPs G10/G11).

The comparator reads paths relative to its working directory, so each test builds a temp
workspace: read-only symlinks to the zip folder and the two source files, plus a REAL copy of
runs/5a9f093a2fe0 (the "official" side), which is then tampered. Expected verdict on every
tampered copy: NOT REPRODUCED (exit 1) AND the specific reason in "problems" (every rejection test
asserts its own needle, so a crash or an unrelated problem cannot count as a PASS).

Zip-side tests (added after review r001 of 1250bbd: G-A to G-E) replace the "Project Histories" symlink with a real
temp folder holding a REBUILT, reduced zip (the rerun folder plus the stub manifest, optionally tampered). A rebuilt zip
can never match EXPECTED_ZIP_SHA256, so each of those tests asserts its own needle in addition to the sha problem."""
import csv
import io
import json
import os
import shutil
import unittest
import zipfile

import numpy as np

from rtcommon import PY, REPO, TempDirMixin, run

CMP = os.path.join(REPO, "audits/reproductions/b2a95dfbfbe3/compare_b2a95dfbfbe3_v4.py")
RUN = "runs/5a9f093a2fe0"
CSV = "AIEF_1_4_5a9f093a2fe0_scalar_summary.csv"
DIAG = "AIEF_1_4_5a9f093a2fe0_branch_diagnostics.npz"
ZIP = os.path.join(REPO, "Project Histories", "workspace-019ff425-d36a-7d5d-bfa7-8e81a82fa8f2.zip")
ZRUN = "runs/frozen_production_20260806/b2a95dfbfbe3/"
ZSTUB = "runs/5a9f093a2fe0/manifest.json"
ZID, RID = "b2a95dfbfbe3", "5a9f093a2fe0"
ZCSV, ZDIAG = f"AIEF_1_4_{ZID}_scalar_summary.csv", f"AIEF_1_4_{ZID}_branch_diagnostics.npz"


def load_npz(p):
    with np.load(p, allow_pickle=False) as z:
        return {k: z[k] for k in z.files}


def npz_bytes(d):
    b = io.BytesIO(); np.savez(b, **d); return b.getvalue()


def parse(out):
    return json.loads(out[out.index("{"):out.rindex("}") + 1])


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

    def rebuild_zip(self, edit=None, drop=()):
        """Reduced copy of the zip (rerun folder + stub manifest) in a real temp 'Project Histories' folder.
        edit(rel, bytes) -> bytes; rel is relative to the rerun folder, or the stub's full name. drop: rel names."""
        ph = os.path.join(self.w, "Project Histories")
        os.unlink(ph); os.makedirs(ph)
        with zipfile.ZipFile(ZIP) as src, \
                zipfile.ZipFile(os.path.join(ph, os.path.basename(ZIP)), "w", zipfile.ZIP_DEFLATED) as dst:
            for n in src.namelist():
                if n.endswith("/") or not (n.startswith(ZRUN) or n == ZSTUB):
                    continue
                rel = n[len(ZRUN):] if n.startswith(ZRUN) else n
                if rel in drop:
                    continue
                data = src.read(n)
                dst.writestr(n, edit(rel, data) if edit else data)

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

    # --- review r001 of 1250bbd: G-B (zip not pinned; exact copies) ----------------------------
    def test_zip_rebuilt_unchanged_fails_only_on_zip_sha(self):
        self.rebuild_zip()
        out = self.verdict_rejected("zip sha256 ", "is not EXPECTED_ZIP_SHA256 281bf33be105cb6219af7aecb9f8ae547459856c1548fdf646f5caee9f8d17ad")
        probs = parse(out)["problems"]
        self.assertEqual(len(probs), 1, probs)   # same members, same data: every other gate still passes

    def test_GB_zip_seeds_replaced_by_official_seeds_relabelled(self):
        """Review r001 case 31: v4 at 1250bbd said REPRODUCED with diff 0."""
        def edit(rel, data):
            if rel.startswith("seed_"):
                d = load_npz(os.path.join(self.run_dir, rel)); d["config_hash"] = np.array(ZID)
                return npz_bytes(d)
            return data
        self.rebuild_zip(edit)
        out = self.verdict_rejected("is not EXPECTED_ZIP_SHA256",
                                    "SUSPICIOUS: 40 seed file(s) identical to the official run in every field")
        self.assertNotIn("label", "".join(parse(out)["problems"]))   # the relabelling itself passes the label gate

    def test_GB_zip_csv_replaced_by_official_csv(self):
        with open(os.path.join(self.run_dir, CSV), "rb") as f:
            official = f.read()
        self.rebuild_zip(lambda rel, data: official if rel == ZCSV else data)
        self.verdict_rejected("SUSPICIOUS: scalar summary CSV numeric cells all exactly equal")

    def test_GB_zip_branch_diagnostics_replaced_by_official(self):
        with open(os.path.join(self.run_dir, DIAG), "rb") as f:
            official = f.read()
        self.rebuild_zip(lambda rel, data: official if rel == ZDIAG else data)
        self.verdict_rejected("SUSPICIOUS: branch diagnostics all exactly equal")

    # --- G-D: zip-side missing / empty / garbled files give a verdict, not a traceback --------
    def test_zip_manifest_missing(self):
        self.rebuild_zip(drop=("manifest.json",))
        self.verdict_rejected("rerun manifest.json missing or unreadable (FileNotFoundError)")

    def test_zip_manifest_empty(self):
        self.rebuild_zip(lambda rel, data: b"" if rel == "manifest.json" else data)
        self.verdict_rejected("rerun manifest.json missing or unreadable (JSONDecodeError)")

    def test_zip_csv_missing(self):
        self.rebuild_zip(drop=(ZCSV,))
        self.verdict_rejected("scalar summary CSV: rerun file missing or unreadable (FileNotFoundError)")

    def test_zip_csv_empty(self):
        self.rebuild_zip(lambda rel, data: b"" if rel == ZCSV else data)
        self.verdict_rejected("scalar summary CSV: rerun file missing or unreadable (EmptyDataError)")

    def test_zip_branch_diagnostics_missing(self):
        self.rebuild_zip(drop=(ZDIAG,))
        self.verdict_rejected(f"{ZDIAG}: missing in rerun run")

    def test_zip_seed_member_empty(self):
        f = self.seed_file()
        self.rebuild_zip(lambda rel, data: b"" if rel == f else data)
        self.verdict_rejected(f"{f}: unreadable in rerun run")

    def test_zip_stub_manifest_missing(self):
        self.rebuild_zip(drop=(ZSTUB,))
        out = self.verdict_rejected(f"zip stub {ZSTUB} missing or unreadable (KeyError)")
        self.assertIn('"zip_also_contains_stub_runs_5a9f093a2fe0_manifest": false', out)

    def _text_cell(self, rows):
        j, _ = self.first_finite_numeric_cell(rows)
        name = rows[0][j]; rows[1][j] = "abc"
        return name

    def test_official_csv_text_in_numeric_cell(self):
        names = []
        self.edit_csv(lambda rows: names.append(self._text_cell(rows)))
        self.verdict_rejected(f"non-numeric text in numeric cells of the official run: {names[0]} (1 cells)")

    def test_zip_csv_text_in_numeric_cell(self):
        names = []
        def edit(rel, data):
            if rel != ZCSV:
                return data
            rows = list(csv.reader(io.StringIO(data.decode())))
            names.append(self._text_cell(rows))
            b = io.StringIO(); csv.writer(b, lineterminator="\n").writerows(rows); return b.getvalue().encode()
        self.rebuild_zip(edit)
        self.verdict_rejected(f"non-numeric text in numeric cells of the rerun run: {names[0]} (1 cells)")

    # --- G-A: manifest key sets ----------------------------------------------------------------
    def test_manifest_null_key_added(self):
        """Review r001 case 06: a key added with value null passed the .get()-based differing-keys check."""
        self.set_manifest(lambda m: m.__setitem__("notes", None))
        out = self.verdict_rejected("manifest: key(s) present in only one manifest ['notes']")
        self.assertNotIn("unexpected differing keys", out)   # the old check alone would still accept it

    # --- G-C / G-E: gated fields must be present on both sides ------------------------------------
    def test_seed_config_hash_removed_on_both_sides(self):
        """Review r001 case 35 (one seed): the label gate was vacuous when the field was absent on both sides."""
        f = self.seed_file()
        self.edit_npz(f, lambda d: d.pop("config_hash"))
        def edit(rel, data):
            if rel != f:
                return data
            d = load_npz(io.BytesIO(data)); d.pop("config_hash"); return npz_bytes(d)
        self.rebuild_zip(edit)
        out = self.verdict_rejected(f"{f}: config_hash label missing in rerun run",
                                    f"{f}: config_hash label missing in official run")
        self.assertNotIn(f"{f}: field sets differ", out)   # sets are equal, so only the presence gate catches it

    def test_manifest_model_removed_on_both_sides(self):
        """Review r001 case 39: None == None counted as equal."""
        self.set_manifest(lambda m: m.pop("model"))
        def edit(rel, data):
            if rel != "manifest.json":
                return data
            m = json.loads(data); m.pop("model"); return json.dumps(m).encode()
        self.rebuild_zip(edit)
        out = self.verdict_rejected("manifest: model missing in rerun manifest", "manifest: model missing in official manifest")
        self.assertIn('"model_equal": true', out)   # equality alone is vacuous here

    def test_selftest_still_passes(self):
        rc, out = run([PY, CMP, "--selftest"], cwd=self.w)
        self.assertEqual(rc, 0, out)
        self.assertIn("selftest OK", out)


if __name__ == "__main__":
    unittest.main()
