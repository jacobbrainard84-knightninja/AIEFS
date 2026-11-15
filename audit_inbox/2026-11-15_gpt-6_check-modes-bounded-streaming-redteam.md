# GPT-6 outside-audit review — D=50 reconciliation and check_modes bounded-stream red team

> **UNVERIFIED INPUT.** This submission is an outside-agent review only. It is not a finding, registry claim, erratum, approval, or instruction to integrate. Researcher 001 / Auditor Seat 002 must independently triage it. This is the single new Markdown file for this review; no existing inbox file or triage row is changed.

- **Agent / model:** GPT-6
- **Date:** 2026-11-15 (Europe/Tirane)
- **Main reviewed:** 871417d58504dd2e42276bde8142e3fdac73df44
- **Inbox guidance / triage read at:** audit-inbox@4ee9fe52b5b93a0b4042e653793bb2a334d4cf70
- **Scope:** Reconcile production D=50 delay coverage; assess the proposed phase-channel-only negative control; re-check the check_modes.py memory-scaling issue; red-team a bounded-memory git cat-file --batch prototype; refresh CI status.
- **Method:** Read-only GitHub inspection of current-main source and inbox guidance; isolated temporary-Git tests; fake-git protocol fault injection; Python bytecode compilation; fresh 128-MiB temporary-Git benchmark. No complete AIEFS checkout was available in this workspace. No external outreach was performed.

## 1. Executive disposition

1. **Production D=50 coverage is already on main.** The earlier finding that the production delay length was not tested was correctly triaged CONFIRMED. Current main contains production-length initialization, slot-isolation and FIFO-aging probes. Do not integrate the superseded local D=50 test candidate as duplicate coverage.
2. **One optional mutation-coverage improvement remains.** The D=50 channel-isolation test appears sensitive to a phase-coupling-only mutant that reads the newest history slot, but the mutant has not been run against the real engine source. Add this negative control only after a maintainer reproduces it in a full checkout.
3. **The check_modes.py memory-scaling concern remains present.** Current shebang_objects buffers the complete git cat-file --batch response although it only needs two prefix bytes from each blob. This is an avoidable resource risk, not a demonstrated correctness bug.
4. **The streaming replacement is a local prototype, not an integration-ready fix.** The candidate and focused harness passed 13/13 isolated tests, including malformed-protocol fault injection. A fresh 128-MiB benchmark reduced Python parent-process peak RSS by 260,864 KiB. The complete AIEFS checker, full test suite, strict tree check and Actions were not run with the patch.

## 2. Production D=50 issue: resolved on current main

The earlier GPT-6 production-delay finding is recorded as CONFIRMED in audit_inbox/TRIAGE.md:165, row GPT6-1113-P5DELAY (current inbox blob 251f4a3744d691aacc97b44607587913c6368892). The current main test source is blob 4734269b974a09664fdf231f05a153f6766fe61b:

- test_probe_d50_config_and_init, lines 195–202: verifies D=50, a 51-slot history queue, distinct array instances and correct initial values.
- test_probe_d50_reads_slot0_only, lines 205–220: changes slots 1–50 while holding slot 0 fixed, then changes slot 0; checks R, theta and B.
- test_probe_d50_queue_aging, lines 223–254: compares the 51-slot FIFO against an explicit trace over 120 transitions and checks the initial-to-live-delay boundary.
- PROBES, lines 256–259, includes all three production-D=50 probes.

This resolves the original coverage gap. Repo checks run #86 passed on main 871417d, including the research/lean_gate tests step (run 43617964046).

### Optional phase-channel mutation

The existing input_reads_newest mutant targets the compute_R input read. The phase-coupling read occurs separately in advance_state. Recommendation: add a distinct phase_coupling_reads_newest mutant that changes only the second delayed read from state.history[0] to state.history[-1], and require test_probe_d50_reads_slot0_only to kill it.

For the exact test fixture, the algebraic phase-update difference between H and H2 under this phase-channel-only mutation is (1.79796014e-4, 1.70717488e-5), with L2 norm 1.80604683e-4, while R and B remain unchanged. The sensitivity calculation is reproduced in the appendix.

**Limit:** this is a recurrence/formula sensitivity calculation, not execution of a mutated aief_experiment_engine_v1.py. The suggested patch passed git apply --check only against a synthetic source-context skeleton. The mutant itself was not executed. Treat this as a lead for an actual full-checkout mutation test, not as demonstrated mutation coverage.

## 3. check_modes.py: current source and resource risk

Current main tools/ci/check_modes.py is unchanged at blob 5647720d6e88d2a1c5e36063b55affb745eec02e. shebang_objects, lines 103–121, calls subprocess.run(..., capture_output=True) for git cat-file --batch, retains the whole response in proc.stdout, then advances through the blob payloads although the predicate only checks the first two bytes for #!.

The current main tree census recorded at 871417d is 3,272 entries, 3,102 regular-file entries, 2,805 unique regular blobs and 1,236,348,312 bytes (1.15144 GiB) of unique regular-blob payload. This shows the potential scale of the captured stream; it does not establish peak RSS on the current Actions runner. Repo checks #86 passes with the existing implementation, but that does not remove the avoidable buffering.

The concern is already listed as audit_inbox/briefing/OPEN_QUESTIONS.md:70, item 15 (blob d5560e04349de0b121d43a57eee8e75f818e4e5e). Current source lines and blob above independently reconfirm the implementation detail.

## 4. Bounded-memory prototype: design and local test results

The proposed implementation uses:
- a file-backed stdin object-ID batch, avoiding a producer/consumer pipe deadlock;
- Popen with stdout parsed incrementally and stderr redirected to a temporary file;
- one response header at a time, validating returned object ID, object type and declared size;
- at most the two-byte prefix needed for the shebang decision;
- discarding remaining content in chunks no larger than 1 MiB, checking exact payload length and the record terminator;
- explicit handling of missing objects, extra output and nonzero Git exit status.

**Fresh test run on 2026-11-15:**

    cd evidence
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python -m unittest -v \
      test_check_modes_streaming_candidate test_check_modes_streaming_parser_redteam

**Result: 13/13 passed in 9.489 seconds.** Six functional tests cover bounded reads, truncated stream rejection, empty inputs, missing objects, non-blob objects and a real temporary Git batch containing shebang/non-shebang blobs, duplicate object IDs, an empty blob and excluded symlink-mode entries. Seven protocol-red-team tests exercise grouped cases for missing/truncated/malformed headers, wrong OIDs/types, invalid or negative sizes, prefix/payload truncation, missing terminators, extra output and nonzero subprocess exits with stderr preserved.

Python bytecode compilation also passed for the candidate, both test modules and benchmark script. The full candidate implementation and protocol fault-injection script are included below. The functional-test cases are enumerated above. This report follows the inbox's one-new-file submission rule; no executable file is added separately.

### 128-MiB memory experiment

A fresh temporary Git repository containing one real 134,217,728-byte blob was benchmarked in separate Python parent processes:

- Whole-output capture: 358,420 KiB peak parent RSS.
- Streaming prototype: 97,556 KiB peak parent RSS.
- Reduction: 260,864 KiB.

The Git child process RSS is not included. This is a controlled parent-process comparison on one synthetic 128-MiB blob, not a full AIEFS or CI-runner benchmark. The benchmark script is included below.

### Patch validation boundary

The combined patch's git apply --check passed against a synthetic aligned source skeleton only. It has not been applied to a complete AIEFS checkout. A repository-shaped six-test adapter variant passed against a temporary adapter, but this is not execution against the original full tools/ci/check_modes.py module.

## 5. Current CI status (unmodified main)

At main 871417d:
- Repo checks run #86 (43617964046): completed / success. Job metadata confirms CI tool self-tests, File modes / check_modes.py, and Analysis tests / research/lean_gate tests passed.
- Lean proof check run #157 (43617963973): completed / success. This is an update; it was still in progress when the earlier note was written.

These runs validate unmodified main only. They do not validate the streaming candidate or either proposed mutation patch.

## 6. Recommendations

1. Keep the former production D=50 test candidate superseded; do not duplicate the already-landed coverage.
2. In a complete checkout, apply the bounded-stream change, run all tools/ci/tests, run patched check_modes.py against the actual index, run --strict and verify classifications match the current implementation.
3. Have a different reviewer inspect the parser's framing, subprocess and error-handling behavior; run candidate CI before any integration proposal.
4. Execute the phase-channel-only mutant against the actual engine source and require the specific D=50 slot-isolation probe to kill it.
5. Keep any accepted code change on a reviewed side branch and integrate only through the owner's normal PR process. This submission does not request automatic promotion.

## 7. What was not done

- No complete AIEFS checkout was obtained in the local environment.
- The streaming patch was not applied to the actual source tree.
- The actual tools/ci/check_modes.py module was not tested with this patch; the complete tools/ci/tests, full-tree strict scan and candidate Actions run were not performed.
- The phase-coupling mutant was not executed against the engine.
- No main files, claim rows, errata, TRIAGE.md, briefing files or other inbox submissions were edited by this work.
- No outreach was made.

---

# Reproducibility appendices

The following code is unverified input until an independent maintainer reproduces it. It is embedded by value in this single Markdown file to preserve the inbox's one-file intake rule.

## Appendix A — standalone streaming candidate

    #!/usr/bin/env python3
    """Candidate bounded-memory replacement for check_modes.py::shebang_objects."""
    from __future__ import annotations

    import subprocess
    import tempfile
    from collections.abc import Mapping

    CHUNK_SIZE = 1024 * 1024

    def _discard_exact(stream, count: int, *, chunk_size: int = CHUNK_SIZE) -> None:
        remaining = count
        while remaining:
            chunk = stream.read(min(remaining, chunk_size))
            if not chunk:
                raise ValueError(f"truncated cat-file payload: {remaining} byte(s) missing")
            remaining -= len(chunk)

    def shebang_objects_streaming(repo: str, entries: Mapping[str, tuple[str, str]]) -> set[str]:
        objects = sorted({oid for mode, oid in entries.values() if mode in ("100644", "100755")})
        if not objects:
            return set()

        command = ["git", "-C", repo, "cat-file", "--batch"]
        found: set[str] = set()
        with tempfile.TemporaryFile() as request, tempfile.TemporaryFile() as errors:
            request.write(("\n".join(objects) + "\n").encode("ascii"))
            request.seek(0)
            process = subprocess.Popen(command, stdin=request, stdout=subprocess.PIPE, stderr=errors)
            assert process.stdout is not None
            try:
                for expected_oid in objects:
                    header = process.stdout.readline()
                    if not header or not header.endswith(b"\n"):
                        raise ValueError("truncated or missing cat-file batch header")
                    fields = header[:-1].split()
                    if len(fields) == 2 and fields[1] == b"missing":
                        if fields[0].decode("ascii", "strict") != expected_oid:
                            raise ValueError("cat-file missing-object response out of order")
                        continue
                    if len(fields) != 3:
                        raise ValueError(f"malformed cat-file batch header: {header[:160]!r}")
                    oid_b, object_type, size_b = fields
                    oid = oid_b.decode("ascii", "strict")
                    if oid != expected_oid:
                        raise ValueError("cat-file batch response out of order")
                    if object_type != b"blob":
                        raise ValueError(f"expected blob object, got {object_type!r}")
                    try:
                        size = int(size_b)
                    except ValueError as exc:
                        raise ValueError(f"invalid cat-file object size: {size_b!r}") from exc
                    if size < 0:
                        raise ValueError(f"negative cat-file object size: {size}")
                    prefix_size = min(2, size)
                    prefix = process.stdout.read(prefix_size)
                    if len(prefix) != prefix_size:
                        raise ValueError("truncated cat-file object prefix")
                    if prefix == b"#!":
                        found.add(oid)
                    _discard_exact(process.stdout, size - prefix_size)
                    if process.stdout.read(1) != b"\n":
                        raise ValueError("missing cat-file batch record terminator")
                if process.stdout.read(1):
                    raise ValueError("unexpected extra data after cat-file batch responses")
            except Exception:
                process.kill()
                process.wait()
                raise
            finally:
                process.stdout.close()
            return_code = process.wait()
            if return_code:
                errors.seek(0)
                detail = errors.read(8192).decode("utf-8", "replace")
                raise subprocess.CalledProcessError(return_code, command, stderr=detail)
        return found

## Appendix B — protocol fault-injection test script

    #!/usr/bin/env python3
    """Fault-injection tests for malformed or failing cat-file batch streams."""
    from __future__ import annotations

    import os
    import subprocess
    import tempfile
    import unittest
    from pathlib import Path
    from unittest import mock

    from check_modes_streaming_candidate import shebang_objects_streaming

    OID = "1" * 40
    OTHER_OID = "2" * 40

    FAKE_GIT = r'''#!/usr/bin/env python3
    import os, sys
    sys.stdin.buffer.read()
    mode = os.environ.get("FAKE_GIT_MODE", "good")
    responses = {
        "good": (f"{os.environ['FAKE_GIT_OID']} blob 2\n#!\n".encode(), 0, b""),
        "empty_header": (b"", 0, b""),
        "no_header_newline": (f"{os.environ['FAKE_GIT_OID']} blob 2".encode(), 0, b""),
        "malformed_header": (b"not-a-valid-header\n", 0, b""),
        "wrong_oid": (f"{os.environ['FAKE_GIT_OTHER_OID']} blob 2\n#!\n".encode(), 0, b""),
        "wrong_type": (f"{os.environ['FAKE_GIT_OID']} tree 2\n#!\n".encode(), 0, b""),
        "bad_size": (f"{os.environ['FAKE_GIT_OID']} blob nope\n".encode(), 0, b""),
        "negative_size": (f"{os.environ['FAKE_GIT_OID']} blob -1\n".encode(), 0, b""),
        "short_prefix": (f"{os.environ['FAKE_GIT_OID']} blob 2\n#".encode(), 0, b""),
        "short_payload": (f"{os.environ['FAKE_GIT_OID']} blob 10\n#!abc".encode(), 0, b""),
        "missing_trailer": (f"{os.environ['FAKE_GIT_OID']} blob 2\n#!X".encode(), 0, b""),
        "extra_output": (f"{os.environ['FAKE_GIT_OID']} blob 2\n#!\nEXTRA\n".encode(), 0, b""),
        "nonzero_exit": (f"{os.environ['FAKE_GIT_OID']} blob 2\n#!\n".encode(), 7, b"deliberate fake git failure"),
    }
    out, rc, err = responses[mode]
    sys.stdout.buffer.write(out)
    sys.stdout.buffer.flush()
    if err:
        sys.stderr.buffer.write(err)
        sys.stderr.buffer.flush()
    sys.exit(rc)
    '''

    class CatFileProtocolRedTeam(unittest.TestCase):
        def setUp(self):
            self.temp = tempfile.TemporaryDirectory(prefix="cat-file-fault-injection-")
            self.root = Path(self.temp.name)
            self.bin = self.root / "bin"
            self.bin.mkdir()
            fake = self.bin / "git"
            fake.write_text(FAKE_GIT, encoding="utf-8")
            fake.chmod(0o755)
            self.env = {
                "PATH": str(self.bin) + os.pathsep + os.environ.get("PATH", ""),
                "FAKE_GIT_OID": OID,
                "FAKE_GIT_OTHER_OID": OTHER_OID,
            }
            self.entries = {"a.py": ("100644", OID)}

        def tearDown(self):
            self.temp.cleanup()

        def run_mode(self, mode: str):
            env = dict(self.env, FAKE_GIT_MODE=mode)
            with mock.patch.dict(os.environ, env, clear=False):
                return shebang_objects_streaming("ignored-repo-path", self.entries)

        def test_valid_protocol_response(self):
            self.assertEqual(self.run_mode("good"), {OID})

        def test_missing_or_truncated_header_rejected(self):
            for mode in ("empty_header", "no_header_newline", "malformed_header"):
                with self.subTest(mode=mode), self.assertRaises(ValueError):
                    self.run_mode(mode)

        def test_response_order_and_type_are_checked(self):
            for mode, message in (("wrong_oid", "out of order"), ("wrong_type", "expected blob")):
                with self.subTest(mode=mode), self.assertRaisesRegex(ValueError, message):
                    self.run_mode(mode)

        def test_object_size_is_validated(self):
            for mode, message in (("bad_size", "invalid cat-file object size"), ("negative_size", "negative cat-file object size")):
                with self.subTest(mode=mode), self.assertRaisesRegex(ValueError, message):
                    self.run_mode(mode)

        def test_prefix_and_payload_truncation_rejected(self):
            for mode, message in (("short_prefix", "truncated cat-file object prefix"),
                                  ("short_payload", "truncated cat-file payload")):
                with self.subTest(mode=mode), self.assertRaisesRegex(ValueError, message):
                    self.run_mode(mode)

        def test_record_terminator_and_extra_output_checked(self):
            with self.assertRaisesRegex(ValueError, "missing cat-file batch record terminator"):
                self.run_mode("missing_trailer")
            with self.assertRaisesRegex(ValueError, "unexpected extra data"):
                self.run_mode("extra_output")

        def test_nonzero_git_exit_preserves_exit_and_stderr(self):
            with self.assertRaises(subprocess.CalledProcessError) as caught:
                self.run_mode("nonzero_exit")
            self.assertEqual(caught.exception.returncode, 7)
            self.assertIn("deliberate fake git failure", caught.exception.stderr)

    if __name__ == "__main__":
        unittest.main(verbosity=2)

## Appendix C — benchmark script

    #!/usr/bin/env python3
    """Compare buffered versus bounded streaming on one large real Git blob."""
    from __future__ import annotations

    import os
    from pathlib import Path
    import subprocess
    import sys
    import tempfile

    CHILD = r'''
    import resource, subprocess, sys
    sys.path.insert(0, sys.argv[1])
    from check_modes_streaming_candidate import shebang_objects_streaming
    mode, repo, oid = sys.argv[2:]
    if mode == "buffered":
        p = subprocess.run(["git", "-C", repo, "cat-file", "--batch"],
                           input=(oid + "\n").encode(), stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, check=True)
        assert p.stdout[:2] != b"#!"
    elif mode == "streaming":
        assert shebang_objects_streaming(repo, {"bulk.bin": ("100644", oid)}) == set()
    else:
        raise SystemExit("unknown mode")
    print(f"mode={mode} peak_rss_kib={resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}")
    '''

    def git(repo: Path, *args: str, stdin=None) -> str:
        p = subprocess.run(
            ["git", "-C", str(repo), *args], stdin=stdin,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
        )
        return p.stdout.decode().strip()

    def main() -> None:
        with tempfile.TemporaryDirectory(prefix="check-modes-large-blob-") as td:
            repo = Path(td)
            git(repo, "init", "--quiet")
            blob_path = repo / "bulk.bin"
            block = b"x" * (1024 * 1024)
            with blob_path.open("wb") as f:
                for _ in range(128):
                    f.write(block)
            with blob_path.open("rb") as f:
                oid = git(repo, "hash-object", "-w", "--stdin", stdin=f)
            print(f"fixture_blob_bytes={blob_path.stat().st_size}")
            for mode in ("buffered", "streaming"):
                p = subprocess.run(
                    [sys.executable, "-c", CHILD, str(Path(__file__).resolve().parent), mode, str(repo), oid],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=True,
                    env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                )
                print(p.stdout.strip())

    if __name__ == "__main__":
        main()

## Appendix D — proposed phase-channel-only mutant patch

The patch below is a recommendation only; it was apply-checked against a synthetic aligned source skeleton, not a complete AIEFS checkout. It has not been executed against the engine.

    diff --git a/research/lean_gate/tests/test_engine_step_order.py b/research/lean_gate/tests/test_engine_step_order.py
    --- a/research/lean_gate/tests/test_engine_step_order.py
    +++ b/research/lean_gate/tests/test_engine_step_order.py
    @@ -267,5 +267,6 @@
         ("phase_uses_old_B", "state.B * np.sin(", "B_previous * np.sin("),
         ("input_reads_newest", "delayed = state.history[0]", "delayed = state.history[-1]"),
    +    ("phase_coupling_reads_newest", "delayed = state.history[0]", "delayed = state.history[-1]"),
         ("no_B_carry", "B_unprojected = state.B + config.dt * (", "B_unprojected = 0.0 + config.dt * ("),
    @@ -297,6 +298,15 @@
         if name == "R_from_old_C":
             assert n == 1
             src = src.replace(old, new, 1).replace("result = np.abs(state.coherence_acc)",
                                                    "result = old_abs", 1)
    +    elif name == "phase_coupling_reads_newest":
    +        start = src.index("def advance_state(")
    +        end = src.index("\ndef simulate_prefix(", start)
    +        block = src[start:end]
    +        assert block.count(old) == 1
    +        block = block.replace(old, new, 1)
    +        src = src[:start] + block + src[end:]
    @@ -319,6 +329,8 @@
         assert failed, f"mutant {name} survived every probe"
    +    if name == "phase_coupling_reads_newest":
    +        assert "test_probe_d50_reads_slot0_only" in failed, failed

## Appendix E — D=50 phase-channel sensitivity and transcripts

Using the exact main test fixture: theta=(1.0, 2.5), omega=(1.0, 2.0), H[0]=(0.1, 3.0), H[-1]=(0.6, 2.0), H2[0]=H[0], H2[-1]=H[-1]+0.7, B0 off-diagonal 0.1, C0 off-diagonal 0.5, dt=0.01, tau=0.5, gamma=0.015, eta=4, mu=0.

Assuming compute_R still reads history[0], H and H2 yield the same R and updated B. For the phase-channel-only mutant reading history[-1], the phase updates differ by (1.79796014e-4, 1.70717488e-5), L2 norm 1.80604683e-4. Nominal slot-0 phase update is (1.01108851, 2.51919141); mutant phase update using H[-1] is (1.01100732, 2.51886719), and using H2[-1] is (1.01118712, 2.51888426). This is algebraic sensitivity, not execution of the mutated engine.

Current-turn test transcript: command above; result 13 tests passed in 9.489 seconds. Functional tests: 6/6 passed. Protocol-red-team tests: 7/7 passed, covering the grouped malformed/failing cases listed in §4. The six-test repository-shaped adapter variant passed 6/6 against a temporary adapter, not the original full check_modes.py.

Fresh benchmark output:
    fixture_blob_bytes=134217728
    mode=buffered peak_rss_kib=358420
    mode=streaming peak_rss_kib=97556

Python bytecode compilation: PASS for the candidate, both test modules and benchmark script. Combined patch apply-check: PASS only against a synthetic aligned source skeleton. The Git child process RSS is not counted in the reported Python parent peak RSS.
