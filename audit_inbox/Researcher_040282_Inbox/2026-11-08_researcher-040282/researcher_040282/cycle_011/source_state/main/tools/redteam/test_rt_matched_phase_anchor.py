"""Red-team negative control for the per-seed anchor flag in AIEF_1_4_matched_phase_memory_ablation.py.

The script (hash-pinned, ART-0041) writes matched_phase_seed_status.csv with an `anchor_pass` column
computed by one expression (around line 1751):

    row["anchor_pass"] = (not verify_anchors or (len(seed_anchors) == 3 and all(...))) if seed_anchors else True

The expression is extracted with `ast` from the unmodified script and evaluated on hand-built anchor
rows; the script is not imported or run. A seed with NO anchor rows while anchors are being verified
(e.g. a seed that failed before anchor validation, status "failed: ...") should not be reported as
anchor_pass=True. It is today: GAP (old-files drift review, ERRATA E15 context; finding F4).
The committed 40-seed run (test_output/) has 3 passing anchors per seed, so its CSV is not affected.
"""
import ast
import os
import unittest

from rtcommon import ACCEPTED, REPO, gap

SCRIPT = os.path.join(REPO, "AIEF_1_4_matched_phase_memory_ablation.py")


def anchor_pass_expr():
    with open(SCRIPT, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    found = []
    for node in ast.walk(tree):
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Subscript)
                and isinstance(node.targets[0].value, ast.Name) and node.targets[0].value.id == "row"
                and isinstance(node.targets[0].slice, ast.Constant)
                and node.targets[0].slice.value == "anchor_pass"):
            found.append(node)
    if len(found) != 1:
        raise RuntimeError(f"expected exactly one row['anchor_pass'] assignment, found {len(found)}")
    node = found[0]
    code = compile(ast.Expression(node.value), f"{SCRIPT}:{node.lineno}", "eval")
    return code, node.lineno


def evaluate(seed_anchors, verify_anchors=True):
    code, _ = anchor_pass_expr()
    return eval(code, {"__builtins__": {"len": len, "all": all}},
                {"seed_anchors": seed_anchors, "verify_anchors": verify_anchors})


def anchors(*passes):
    names = ("B_carrier_only", "full_reset", "continue")
    return [{"seed": "7", "production_branch": names[i], "pass": p} for i, p in enumerate(passes)]


class MatchedPhaseAnchorPass(unittest.TestCase):
    def test_00_control_three_passing_anchors_accepted(self):
        self.assertIs(evaluate(anchors(True, True, True)), True)

    def test_01_control_verify_anchors_false_skips_anchor_check(self):
        # --no-verify-anchors: the flag must not depend on the anchor rows (catches dropping `not verify_anchors or`).
        self.assertIs(evaluate(anchors(True, False, True), verify_anchors=False), True)

    def test_one_failed_anchor_rejected(self):
        self.assertIs(evaluate(anchors(True, False, True)), False, ACCEPTED + ": one anchor failed")

    def test_two_of_three_anchors_rejected(self):
        self.assertIs(evaluate(anchors(True, True)), False, ACCEPTED + ": only 2 of 3 anchors present")

    @gap("a seed with no anchor rows gets anchor_pass=True even though anchors were being verified")
    def test_GAP_seed_without_anchor_rows_passes(self):
        result = evaluate([], verify_anchors=True)
        self.assertIs(result, False, ACCEPTED + f": no anchor rows, verify_anchors=True -> anchor_pass={result!r}")


if __name__ == "__main__":
    unittest.main()
