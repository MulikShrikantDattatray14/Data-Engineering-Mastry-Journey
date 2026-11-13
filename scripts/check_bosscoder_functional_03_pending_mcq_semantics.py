"""Reviewer-only exact-source and synthetic checks of ten Bosscoder functional MCQs.

No Academy official answer, learner submission, grade or mastery is claimed.
"""
from __future__ import annotations
import ast, contextlib, functools, hashlib, io, re, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "99. Reference Materials/Legacy Journey Snapshot/02-python/bosscoder/lecture-03/assignments"
RECORDS = {
    "01": ("q01-lambda-default-argument.md", "611a105f59f6ee23c4fe7c5ac1e8509b46572159"),
    "02": ("q02-map-two-iterables.md", "436aecc93ad121e80866854c8cffa9402c4648cd"),
    "03": ("q03-functional-style.md", "4c5c99d6ef249aad2ce6615d942cccc5b2299c48"),
    "04": ("q04-zip-to-dictionary.md", "88d3401159a4fb58a57671e4ed597144d8eaaec8"),
    "05": ("q05-closure-cell.md", "6c0465f5683677b503b1c9bad2db18543fdc6650"),
    "06": ("q06-lambda-vs-def.md", "ced215fec0aac6dbe290678b2bb66f34bab5b995"),
    "07": ("q07-mutable-default-arguments.md", "9623ca7c3ee01a7b51d15695fb473629cd7bc18d"),
    "08": ("q08-purity-and-global-variable.md", "9bb8820b3e0ac695c473ec192e1ebafe51620910"),
    "09": ("q09-functional-programming-false-statement.md", "2e4819060da2fb4aba57ff7cefda671fd68b8bf9"),
    "10": ("q10-reduce-subtraction.md", "06ed303bdb3ede531fe981c15102f43962930a6a"),
}
FENCE = chr(96) * 3

def original(ident):
    filename, expected = RECORDS[ident]
    data = (SRC / filename).read_bytes()
    actual = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    if actual != expected:
        raise AssertionError(f"{ident}: preserved Git blob changed: {actual}")
    return data.decode("utf-8")

def snippet(ident):
    fragments = re.findall(re.escape(FENCE) + r"python\s*\n(.*?)\n" + re.escape(FENCE), original(ident), flags=re.S)
    if len(fragments) != 1:
        raise AssertionError(f"{ident}: expected one original Python fence, got {len(fragments)}")
    ast.parse(fragments[0])
    return fragments[0]

def printed(ident):
    buf = io.StringIO()
    # These specific SHA-pinned tiny fenced examples were manually inspected.
    with contextlib.redirect_stdout(buf):
        exec(compile(snippet(ident), "original-Q" + ident, "exec"), {})
    return buf.getvalue()

class FunctionalMCQReviewer(unittest.TestCase):
    def test_01_ten_immutable_source_pins_and_unanswered_statuses(self):
        for ident in RECORDS:
            with self.subTest(question=ident):
                source = original(ident)
                self.assertTrue("Pending" in source or "Unanswered" in source)
                self.assertTrue("Not provided" in source or "Hidden until" in source or "not shown" in source)
        print("PASS source pins: 10; original learner answers still pending")

    def test_02_original_q01_lambda_defaults(self):
        self.assertEqual(printed("01"), "9 27\n")
        self.assertEqual((3 ** 2, 3 ** 3), (9, 27))
        print("PASS Q01: unchanged original stdout")

    def test_03_original_q02_map_unequal_iterables(self):
        self.assertEqual(printed("02"), "[5, 7]\n")
        for a, b in [([], [1]), ([1], []), ([1, 2], [5]), ([1], [5, 6])]:
            self.assertEqual(list(map(lambda x, y: x + y, a, b)), [x + y for x, y in zip(a, b)])
        print("PASS Q02: unchanged stdout + 4 boundary cases")

    def test_04_original_q03_expression_not_print(self):
        self.assertEqual(eval(compile(snippet("03"), "original-Q03", "eval")), 30)
        self.assertEqual(sum(i * i for i in range(5)), 30)
        print("PASS Q03: expression value 30; style-label question is conceptual")

    def test_05_original_q04_zip_dictionary(self):
        self.assertEqual(printed("04"), "{1: 'a', 2: 'b'}\n")
        self.assertEqual(dict(zip([1, 1, 2], ["a", "b"])), {1: "b"})
        self.assertEqual(dict(zip([], ["x"])), {})
        print("PASS Q04: original stdout + key collision and empty input")

    def test_06_q05_missing_original_closure_code(self):
        self.assertNotIn(FENCE + "python", original("05"))
        def outer():
            x = 5
            def inner():
                return x
            return inner
        self.assertEqual(outer().__closure__[0].cell_contents, 5)
        print("Q05 reviewer model only; original code omitted from archive")

    def test_07_q06_lambda_annotation_syntax(self):
        with self.assertRaises(SyntaxError):
            compile("lambda x: int: x", "lambda-check", "eval")
        namespace = {}
        exec("def f(x: int) -> int:\n    return x", namespace)
        self.assertEqual(namespace["f"].__annotations__, {"x": int, "return": int})
        print("PASS Q06: independently constructed Python syntax contrast")

    def test_08_q07_ambiguous_mutable_default_protocol(self):
        source = original("07")
        self.assertNotIn(FENCE + "python", source)
        self.assertEqual(source.count("[1] [2] [3]"), 2)
        def shared(value, acc=[]):
            acc.append(value)
            return acc
        r1, r2, r3 = shared(1), shared(2), shared(3, [])
        self.assertIs(r1, r2)
        self.assertEqual([r1, r2, r3], [[1, 2], [1, 2], [3]])
        def snapshots(value, acc=[]):
            acc.append(value)
            return list(acc)
        self.assertEqual([snapshots(1), snapshots(2), snapshots(3, [])], [[1], [1, 2], [3]])
        print("Q07: two interpretations differ; duplicated option text, code missing")

    def test_09_q08_original_rebound_global(self):
        env = {}
        exec(compile(snippet("08"), "original-Q08", "exec"), env)
        self.assertEqual(env["g"](1), 11)
        env["x"] = 20
        self.assertEqual(env["g"](1), 21)
        print("PASS Q08: same input changes when global binding changes; grading unknown")

    def test_10_q09_python_mutability_and_first_class_model(self):
        self.assertNotIn(FENCE + "python", original("09"))
        items = [1]
        items.append(2)
        self.assertEqual(items, [1, 2])
        fn = lambda value: value + 1
        self.assertEqual({"fn": fn}["fn"](4), 5)
        print("PASS Q09: independent conceptual controls, not original answer key")

    def test_11_q10_reduce_left_fold_model(self):
        self.assertNotIn(FENCE + "python", original("10"))
        values = [10, 1, 2, 3]
        actual = functools.reduce(lambda x, y: x - y, values)
        result = values[0]
        for item in values[1:]:
            result -= item
        self.assertEqual(actual, result)
        self.assertEqual(result, 4)
        print("Q10: independent left-fold model, original code not in archive")

if __name__ == "__main__":
    unittest.main(verbosity=2)
