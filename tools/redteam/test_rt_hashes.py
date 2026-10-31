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

    def _fake_manifest_repo(self, data_files=()):
        """A fake repo whose audit manifest lists the verifier plus `data_files` (name -> bytes)."""
        fake = os.path.join(self.tmp, "fake")
        ev = os.path.join(fake, EVID)
        os.makedirs(ev)
        shutil.copy(os.path.join(REPO, EVID, "verify_manifest.py"), ev)
        v = os.path.join(ev, "verify_manifest.py")
        files = {"evidence/verify_manifest.py": {"bytes": os.path.getsize(v), "sha256": sha256(v)}}
        for name, data in dict(data_files).items():
            p = os.path.join(fake, "AI Agent Audits", name)
            with open(p, "wb") as f:
                f.write(data)
            files[name] = {"bytes": len(data), "sha256": sha256(p)}
        m = {"status": "PASSED", "verdict": "all audits passed", "files_sha256": files, "inputs_sha256": {}}
        with open(os.path.join(ev, "audit_manifest.json"), "w") as f:
            json.dump(m, f)
        return fake

    def test_passed_manifest_with_no_data(self):
        # G1 (fixed in tools/ci/check_manifest.py; verify_manifest.py itself is hash-pinned in
        # audit_manifest.json, so the coverage rule lives in the CI wrapper).
        fake = self._fake_manifest_repo()
        self.assertRejected(*run([PY, WRAP, "--repo", fake, "--no-inputs"]),
                            "manifest lists no data files beyond the verifier itself")

    def test_passed_manifest_with_empty_inputs(self):
        fake = self._fake_manifest_repo({"REPORT.md": b"report\n"})
        self.assertRejected(*run([PY, WRAP, "--repo", fake]),
                            "inputs_sha256 is empty, so the --inputs check would verify nothing")

    def test_control_manifest_listing_one_data_file_passes(self):
        fake = self._fake_manifest_repo({"REPORT.md": b"report\n"})
        rc, out = run([PY, WRAP, "--repo", fake, "--no-inputs"])
        self.assertEqual(rc, 0, out[-2000:])


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

    # --- G2b (Researcher 001 audit of a428c32): stub verifiers used to PASS because only rc 0 was checked ----------
    VER = f"{EVID}/verify_manifest.py"
    MAN = f"{EVID}/audit_manifest.json"
    NOT_RUN = f"ERROR   {EVID}/verify_manifest.py was NOT run, so the manifest hashes were NOT checked"
    FAIL0 = "== result: 0 verifier(s) run, 1 failed -> FAIL"
    FAIL1 = "== result: 1 verifier(s) run, 1 failed -> FAIL"

    def wrap(self):
        return run([PY, WRAP, "--repo", self.root])

    def assertWrapperFails(self, rc, out, *lines):
        self.assertRejected(rc, out)
        self.assertEqual(rc, 1, out[-3000:])
        self.assertNotIn("Traceback", out)
        got = out.splitlines()
        for ln in lines:
            self.assertIn(ln, got, out[-3000:])

    def real_pin(self):
        return sha256(os.path.join(REPO, self.VER))

    def stub(self, body):
        p = os.path.join(self.root, self.VER)            # real copy (copy_real in setUp)
        os.unlink(p)
        with open(p, "w") as f:
            f.write(body)
        return p

    def assertHashRejected(self, body):
        p = self.stub(body)
        self.assertWrapperFails(*self.wrap(),
                                f"ERROR   {self.VER}: sha256 {sha256(p)} does not match {self.MAN} "
                                f"files_sha256['evidence/verify_manifest.py'] {self.real_pin()}; refusing to run an unverified verifier",
                                self.NOT_RUN, self.FAIL0)

    def test_00_control_real_copy_passes(self):
        rc, out = self.wrap()
        self.assertEqual(rc, 0, out[-2000:])
        self.assertEqual(out.splitlines()[-1], "== result: 1 verifier(s) run, 0 failed -> PASS")

    def test_zero_byte_verifier_fails(self):
        self.assertHashRejected("")

    def test_comment_only_verifier_fails(self):
        self.assertHashRejected("# verify_manifest.py: all checks passed\n")

    def test_hash_mismatched_verifier_fails(self):
        """The real verifier with its verdict forced to exit 0: one edit, so its pin no longer matches."""
        with open(os.path.join(REPO, self.VER)) as f:
            src = f.read()
        self.assertIn("sys.exit(1 if bad else 0)", src)
        self.assertHashRejected(src.replace("sys.exit(1 if bad else 0)", "sys.exit(0)"))

    def test_symlinked_stub_outside_repo_fails(self):
        stub = os.path.join(self.tmp, "stub_verify.py")   # outside self.root
        with open(stub, "w") as f:
            f.write("import sys\nsys.exit(0)\n")
        p = os.path.join(self.root, self.VER)
        os.unlink(p); os.symlink(stub, p)
        self.assertWrapperFails(*self.wrap(), f"ERROR   {self.VER} resolves outside the repository (to "
                                              f"{os.path.realpath(stub)}); refusing to run it", self.NOT_RUN, self.FAIL0)

    def test_symlink_to_real_verifier_fails(self):
        """Even a symlink to the genuine bytes (here: the real repo's verifier, outside the temp repo) is refused."""
        p = os.path.join(self.root, self.VER)
        os.unlink(p); os.symlink(os.path.join(REPO, self.VER), p)
        self.assertWrapperFails(*self.wrap(), f"ERROR   {self.VER} resolves outside the repository (to "
                                              f"{os.path.realpath(os.path.join(REPO, self.VER))}); refusing to run it",
                                self.NOT_RUN, self.FAIL0)

    def _repin(self, body):
        """Stub the verifier AND rewrite its manifest pin to match (manifest itself is pinned in artifacts.csv)."""
        p = self.stub(body)
        mp = os.path.join(self.root, self.MAN)
        with open(mp) as f:
            m = json.load(f)
        m["files_sha256"]["evidence/verify_manifest.py"] = {"bytes": os.path.getsize(p), "sha256": sha256(p)}
        with open(mp, "w") as f:
            json.dump(m, f, indent=1)
        n = len(m["files_sha256"]); k = len(m["inputs_sha256"]); post = len(set(m.get("post_manifest_logs") or []))
        return (f"checked {n} published files and {k} inputs" + (f"; {post} post-manifest logs listed but not hashed" if post else ""))

    def test_repinned_verifier_exit0_without_success_line_fails(self):
        want = self._repin("import sys\nsys.exit(0)\n")
        self.assertWrapperFails(*self.wrap(), f"ERROR   {self.VER} exited 0 but did not print its success line '{want}' "
                                              "followed by 'OK'; the manifest hashes are NOT confirmed", self.FAIL1)

    def test_repinned_verifier_printing_failed_exit0_fails(self):
        want = self._repin("print('FAILED: 3 problem(s)')\n")
        self.assertWrapperFails(*self.wrap(), f"ERROR   {self.VER} exited 0 but did not print its success line '{want}' "
                                              "followed by 'OK'; the manifest hashes are NOT confirmed", self.FAIL1)


if __name__ == "__main__":
    unittest.main()
