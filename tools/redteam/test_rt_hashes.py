"""Red-team negative controls: hash pins and manifests.

Each test builds a known-false input in a temp mirror of the repo and asserts the real checker
REJECTS it. Tests marked GAP are expected failures: the checker accepts the false input today.
Run:  python3 -m unittest discover -s tools/redteam -v   (from the repository root)
"""
import json
import os
import shutil
import unittest

from rtcommon import gap, PY, REPO, TempDirMixin, copy_real, farm, remove, run, sha256, tamper

PINS = os.path.join(REPO, "tools/ci/check_artifact_pins.py")
WRAP = os.path.join(REPO, "tools/ci/check_manifest.py")
EVID = "AI Agent Audits/evidence"
PINNED = "AIEF_1_3_analysis.py"            # ART-0003, PRESENT_SAME_SHA in registry/artifacts.csv
SEED_DIR = "runs/c3da1ac707bf"             # hashed as an aggregate in audit_manifest.json inputs


def flip_byte(data, i=None):
    i = len(data) // 2 if i is None else i
    return data[:i] + bytes([data[i] ^ 0x01]) + data[i + 1:]


class ArtifactPins(TempDirMixin, unittest.TestCase):
    """tools/ci/check_artifact_pins.py --no-git on a symlink mirror of the tree."""

    def pins(self):
        return run([PY, PINS, "--repo", self.root, "--no-git"])

    def setUp(self):
        super().setUp()
        self.root = farm(os.path.join(self.tmp, "repo"))

    def test_00_control_untampered_mirror_passes(self):
        rc, out = self.pins()
        self.assertEqual(rc, 0, out[-2000:])

    def test_tampered_pinned_file_one_byte(self):
        tamper(self.root, PINNED, flip_byte)
        self.assertRejected(*self.pins(), "PIN_MISMATCH")

    def test_pinned_file_deleted(self):
        remove(self.root, PINNED)
        self.assertRejected(*self.pins(), "PIN_MISSING")

    def test_tampered_file_and_its_pin_rewritten_to_match(self):
        new = tamper(self.root, PINNED, lambda d: d + b"# injected\n")
        h, n = sha256(new), os.path.getsize(new)
        def rewrite(csvb):
            lines = csvb.decode().split("\n")
            for k, line in enumerate(lines):
                if line.startswith("ART-0003,worktree," + PINNED + ","):
                    f = line.split(",")
                    f[3], f[4] = h, str(n)
                    lines[k] = ",".join(f)
            return "\n".join(lines).encode()
        tamper(self.root, "registry/artifacts.csv", rewrite)
        self.assertRejected(*self.pins(), "REGISTRY_CHANGED")

    def test_registry_row_citing_nonexistent_artifact(self):
        row = ("ART-9999,worktree,results/does_not_exist.npz," + "0" * 64 +
               ",1,result,FAKE,Supported,Controlled experimental result,none,,,,,\n")
        tamper(self.root, "registry/artifacts.csv", lambda d: d + row.encode())
        self.assertRejected(*self.pins(), "REGISTRY_CHANGED")


class AuditManifest(TempDirMixin, unittest.TestCase):
    """AI Agent Audits/evidence/verify_manifest.py (real copy of the evidence folder, since the
    verifier resolves its own path) run from a symlink mirror of the tree."""

    def setUp(self):
        super().setUp()
        self.root = farm(os.path.join(self.tmp, "repo"))
        copy_real(self.root, "AI Agent Audits")
        with open(os.path.join(self.root, EVID, "audit_manifest.json")) as f:
            self.manifest = json.load(f)

    def verify(self, *args):
        return run([PY, os.path.join(self.root, EVID, "verify_manifest.py"), *args], cwd=self.root)

    def test_00_control_untampered_passes(self):
        rc, out = self.verify("--inputs")
        self.assertEqual(rc, 0, out[-2000:])

    def test_published_file_one_byte_changed(self):
        rel = sorted(self.manifest["files_sha256"])[0]
        p = os.path.join(self.root, "AI Agent Audits", rel)
        with open(p, "rb") as f:
            data = f.read()
        with open(p, "wb") as f:                      # p is a real temp copy
            f.write(flip_byte(data))
        self.assertRejected(*self.verify(), "SHA256")

    def test_manifest_hash_tampered(self):
        rel = sorted(self.manifest["files_sha256"])[0]
        self.manifest["files_sha256"][rel]["sha256"] = "f" * 64
        with open(os.path.join(self.root, EVID, "audit_manifest.json"), "w") as f:
            json.dump(self.manifest, f)
        self.assertRejected(*self.verify(), "SHA256")

    def test_unlisted_file_added(self):
        with open(os.path.join(self.root, "AI Agent Audits", "evidence", "PASSED.txt"), "w") as f:
            f.write("PASSED\n")
        self.assertRejected(*self.verify(), "UNLISTED")

    def test_corrupted_seed_file_in_hashed_run(self):
        seed = sorted(f for f in os.listdir(os.path.join(REPO, SEED_DIR)) if f.endswith(".npz"))[0]
        tamper(self.root, f"{SEED_DIR}/{seed}", flip_byte)
        self.assertRejected(*self.verify("--inputs"), "INPUT")

    def test_hashed_input_script_edited(self):
        tamper(self.root, "aief_experiment_engine_v1.py", lambda d: d.replace(b"FROZEN_ETA = 0.04", b"FROZEN_ETA = 0.05"))
        self.assertRejected(*self.verify("--inputs"), "INPUT")

    @gap("verify_manifest.py: a manifest that lists no report, no data and no inputs verifies OK")
    def test_GAP_passed_manifest_with_no_data(self):
        ev = os.path.join(self.tmp, "fake", "AI Agent Audits", "evidence")
        os.makedirs(ev)
        shutil.copy(os.path.join(REPO, EVID, "verify_manifest.py"), ev)
        v = os.path.join(ev, "verify_manifest.py")
        # The only file "published" is the verifier itself; no report, no data, no inputs.
        fake = {"status": "PASSED", "verdict": "all audits passed",
                "files_sha256": {"evidence/verify_manifest.py": {"bytes": os.path.getsize(v), "sha256": sha256(v)}},
                "inputs_sha256": {}}
        with open(os.path.join(ev, "audit_manifest.json"), "w") as f:
            json.dump(fake, f)
        rc, out = run([PY, os.path.join(ev, "verify_manifest.py")], cwd=os.path.join(self.tmp, "fake"))
        self.assertRejected(rc, out)


class ManifestWrapper(TempDirMixin, unittest.TestCase):
    """tools/ci/check_manifest.py (the CI entry point)."""

    def setUp(self):
        super().setUp()
        self.root = farm(os.path.join(self.tmp, "repo"))
        copy_real(self.root, "AI Agent Audits")

    def test_wrapper_propagates_verifier_failure(self):
        p = os.path.join(self.root, EVID, "audit_manifest.json")
        with open(p) as f:
            m = json.load(f)
        rel = sorted(m["files_sha256"])[0]
        m["files_sha256"][rel]["sha256"] = "0" * 64
        with open(p, "w") as f:
            json.dump(m, f)
        self.assertRejected(*run([PY, WRAP, "--repo", self.root]), "verify_manifest.py exited 1", "-> FAIL")

    def test_verifier_missing_fails(self):
        """Was GAP G2 (NOTICE and exit 0). Fixed on fix/check-manifest-missing-verifier: exit 1 with a named error."""
        os.unlink(os.path.join(self.root, EVID, "verify_manifest.py"))   # temp copy
        rc, out = run([PY, WRAP, "--repo", self.root])
        self.assertRejected(rc, out, "manifest verifier missing", "NOT checked", "-> FAIL")
        self.assertEqual(rc, 1, out)
        self.assertNotIn("Traceback", out)


if __name__ == "__main__":
    unittest.main()
