"""Read-only, source-extracted Python companion audit for PDF pages 53–58.

Source transcript checks and auditor-created synthetic tests are separate tiers.
Neither verifies the original PDF's image fidelity, platform grading nor learner mastery.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "99. Reference Materials" / "Original Mastery Snapshot" / "2. Python Mastry"
DSA = MASTER / "4. DSA and Complexity"
PATTERNS = MASTER / "5. Coding Round Patterns"
DATA = MASTER / "python_de_dataset"

# PDF page: (original archived source path, original Git blob SHA, example count, part, lesson)
LESSONS = {
    53: (DSA / "13. Trees with DFS and BFS.md", "13813ce3c2a6d0b79dfe40761bb4005182be00ee", 3, 4, 13),
    54: (DSA / "14. Graphs and pipeline DAGs.md", "e40f50bb779b91c28d36fc31822006dd9cb4dbc3", 3, 4, 14),
    55: (DSA / "15. Heaps and greedy choices.md", "37d80b6dc75be56bfa99f604bf34d7ae98017453", 3, 4, 15),
    56: (DSA / "16. Dynamic programming basics.md", "5b588d7c70fa95ed12c1e4072fc9eec032bd19a2", 4, 4, 16),
    57: (DSA / "17. Practice set 3 - DSA.md", "2f26f022dc34cb272be5458a0cb34fcb17e9a3b0", 5, 4, 17),
    58: (PATTERNS / "01. The 18-pattern map.md", "33f80a910e46bef5eef9aaa4515179d74603cf3a", 1, 5, 1),
}
DATA_SHA = {
    "orders.csv": "2d08d1fc6acdc4f26c4427f27ac7925bfb202ea2",
    "employees.csv": "08d2330cc9dab1530d6ff8e896211f7867438e4b",
}
LINK = re.compile(
    r"\[▶ Run and edit this example\]\(<http://127\.0\.0\.1:8765/"
    r"\?part=(\d+)&lesson=(\d+)&snippet=(\d+)>\)"
)
# Part 4 uses ~~~ fences; Part 5 uses Markdown's triple-backtick fences.
FENCE = re.compile(r"(?ms)^(\~{3}|\x60{3})(python|text)[ \t]*\n(.*?)^\1[ \t]*$")


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def assert_preserved_data() -> None:
    for name, sha in DATA_SHA.items():
        assert git_blob_sha((DATA / name).read_bytes()) == sha, (
            f"Archived dataset changed: {name}"
        )


def linked_examples(page: int) -> dict[int, tuple[str, str]]:
    source, sha, expected_count, part, lesson = LESSONS[page]
    raw = source.read_bytes()
    assert git_blob_sha(raw) == sha, f"Archived p.{page} lesson altered"
    body = raw.decode("utf-8-sig")
    matches = list(LINK.finditer(body))
    assert len(matches) == expected_count, f"p.{page}: wrong source link count"
    examples: dict[int, tuple[str, str]] = {}
    for i, match in enumerate(matches):
        this_part, this_lesson, number = map(int, match.groups())
        assert (this_part, this_lesson) == (part, lesson), (
            f"Wrong original source link at p.{page} #{number}"
        )
        assert number not in examples, f"Duplicate original snippet p.{page} #{number}"
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        region = body[match.end():end]
        fences = [(m.group(2), m.group(3)) for m in FENCE.finditer(region)]
        assert len(fences) >= 2 and fences[0][0] == "python" and fences[1][0] == "text", (
            f"Missing original code/printed-output pair p.{page} #{number}"
        )
        examples[number] = (fences[0][1].strip("\n"), fences[1][1].strip("\n"))
    assert sorted(examples) == list(range(1, expected_count + 1)), (
        f"Missing source code IDs at p.{page}"
    )
    return examples


def normalize_display(s: str) -> str:
    return "\n".join(line.rstrip() for line in s.strip("\n").splitlines())


def prepare_scratch(folder: Path) -> None:
    (folder / "python_de_dataset").mkdir()
    for name in DATA_SHA:
        shutil.copyfile(DATA / name, folder / "python_de_dataset" / name)


def run_original(code: str, override_orders: bytes | None = None) -> subprocess.CompletedProcess[str]:
    assert_preserved_data()
    with tempfile.TemporaryDirectory(prefix="mentor-53-58-") as temp:
        work = Path(temp)
        prepare_scratch(work)
        if override_orders is not None:  # REVIEWER FIXTURE ONLY, never official
            (work / "python_de_dataset" / "orders.csv").write_bytes(override_orders)
        script = work / "source_example.py"
        script.write_text(code + "\n", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "-I", "-B", str(script)],
            cwd=work, input="", capture_output=True, text=True,
            timeout=15, check=False, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        expected_orders = override_orders if override_orders is not None else (DATA / "orders.csv").read_bytes()
        assert (work / "python_de_dataset" / "orders.csv").read_bytes() == expected_orders
        assert git_blob_sha((work / "python_de_dataset" / "employees.csv").read_bytes()) == DATA_SHA["employees.csv"]
    assert_preserved_data()
    return result


def source_namespace(page: int, number: int) -> dict:
    """Load the unchanged archived definition with only read-only scratch CSV inputs."""
    code = linked_examples(page)[number][0]
    assert_preserved_data()
    with tempfile.TemporaryDirectory(prefix="mentor-synthetic-") as temp:
        work = Path(temp)
        prepare_scratch(work)
        previous = Path.cwd()
        module_name = f"auditor_source_page_{page}_example_{number}"
        module = types.ModuleType(module_name)
        sys.modules[module_name] = module  # dataclasses resolves its forward types through sys.modules.
        scope: dict = module.__dict__
        try:
            os.chdir(work)
            with contextlib.redirect_stdout(io.StringIO()):
                exec(compile(code, f"source-page-{page}-snippet-{number}", "exec"), scope)
        finally:
            os.chdir(previous)
    assert_preserved_data()
    return scope


class MentorshipSourcePages53To58(unittest.TestCase):
    def test_source_sha_link_inventory_and_original_datasets(self):
        self.assertEqual(list(LESSONS), list(range(53, 59)))
        self.assertEqual([v[2] for v in LESSONS.values()], [3, 3, 3, 4, 5, 1])
        self.assertEqual(sum(v[2] for v in LESSONS.values()), 19)
        assert_preserved_data()
        for page in LESSONS:
            with self.subTest(pdf_page=page):
                self.assertEqual(len(linked_examples(page)), LESSONS[page][2])

    def test_all_19_original_companion_code_output_pairs(self):
        seen = 0
        for page in LESSONS:
            for number, (code, printed) in linked_examples(page).items():
                with self.subTest(pdf_page=page, source_example=number):
                    result = run_original(code)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stderr, "", "Original example unexpected stderr")
                    self.assertEqual(normalize_display(result.stdout),
                                     normalize_display(printed),
                                     f"Original transcript mismatch at p.{page} #{number}")
                    seen += 1
        self.assertEqual(seen, 19)

    # Below: REVISION-ONLY independent synthetic edge probes, NOT official answers.
    def test_synthetic_p53_tree_insertion_shape_and_empty_walk(self):
        namespace = source_namespace(53, 2)
        insert, inorder, height = (namespace[name] for name in ("insert", "inorder", "height"))
        self.assertEqual(inorder(None), [])
        self.assertEqual(height(None), 0)
        node = None
        for value in [2, 2, 1, 3]:
            node = insert(node, value)
        self.assertEqual(inorder(node), [1, 2, 2, 3])

    def test_synthetic_p54_graph_isolated_and_cycle_boundaries(self):
        graph = source_namespace(54, 1)["run_order"]
        self.assertEqual(graph([]), [])  # Edge-list API cannot include isolated nodes.
        with self.assertRaisesRegex(ValueError, "cycle"):
            graph([("a", "b"), ("b", "a")])
        self.assertEqual(graph([("a", "b"), ("b", "c")]), ["a", "b", "c"])
        islands = source_namespace(54, 2)["islands"]
        self.assertEqual(islands([]), 0)
        self.assertEqual(islands(["101", "000", "101"]), 4)

    def test_synthetic_p55_room_reuse_and_streaming_median(self):
        rooms = source_namespace(55, 1)["rooms_needed"]
        self.assertEqual(rooms([]), 0)
        self.assertEqual(rooms([("01", "02"), ("02", "03")]), 1)
        self.assertEqual(rooms([("01", "04"), ("02", "05"), ("03", "06")]), 3)
        maximum = source_namespace(55, 2)["max_jobs"]
        self.assertEqual(maximum([("01", "02"), ("02", "03")]), 2)
        median_cls = source_namespace(55, 3)["RunningMedian"]
        tracker = median_cls()
        for val, expected in [(2, 2), (2, 2.0), (10, 2), (-2, 2.0)]:
            tracker.add(val)
            self.assertEqual(tracker.median(), expected)

    def test_synthetic_p56_unreachable_coin_and_negative_subarray(self):
        coins = source_namespace(56, 2)["min_coins"]
        self.assertEqual(coins([4, 6], 5), -1)
        self.assertEqual(coins([2, 5], 0), 0)
        maximum = source_namespace(56, 3)["max_subarray"]
        self.assertEqual(maximum([-8, -3, -5]), -3)
        climb = source_namespace(56, 4)["climb"]
        self.assertEqual(climb(0), 1)

    def test_synthetic_p57_published_solution_boundaries(self):
        missing = source_namespace(57, 1)["missing"]
        self.assertEqual(missing([1, 3]), 2)
        kth = source_namespace(57, 2)["kth_largest"]
        self.assertEqual(kth([5, 5, 2], 2), 5)  # Ties count as rows.
        with self.assertRaises(ValueError):
            kth([1], 2)
        prefix = source_namespace(57, 3)["common_prefix"]
        self.assertEqual(prefix([]), "")
        self.assertEqual(prefix(["abc", "abd"]), "ab")  # Not directory-aware.
        product = source_namespace(57, 4)["product_except_self"]
        self.assertEqual(product([0, 3, 0]), [0, 0, 0])
        self.assertEqual(product([7]), [1])

    def test_synthetic_p58_pattern_map_frequency(self):
        code, _ = linked_examples(58)[1]
        alternate = (b"order_id,status\n1,delivered\n2,delivered\n"
                     b"3,cancelled\n4,pending\n")
        result = run_original(code, override_orders=alternate)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(normalize_display(result.stdout),
                         "{'delivered': 2, 'cancelled': 1, 'pending': 1}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
