"""Source-preserving audit of archived Python mentorship companion pages 65-68.

Eight source-published output checks (one source contains a broken closing fence),
one network-dependent illustrative definition syntax/mock checked, and five
auditor-created synthetic boundary groups. Never treats these as learner answers
or as official PDF page-parity verification.
"""
from __future__ import annotations

import ast
import contextlib
import hashlib
import io
import itertools
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
PATTERNS = MASTER / "5. Coding Round Patterns"
DATA = MASTER / "python_de_dataset"
# Page: archived file, immutable Git blob SHA, playground example count, lesson number.
LESSONS = {
    65: ("08. Intervals and hash joins.md", "722854478aa7acddba235436c0e151a0e33ea8c5", 2, 8),
    66: ("09. Chunking and retries.md", "49585e9c1378cc3cd3cddf2e5b98773cb4222d24", 2, 9),
    67: ("10. Pagination and LRU caching.md", "f81d641620f51ac82bcff523942b675bed41dce2", 3, 10),
    68: ("11. Validation and snapshot differences.md", "aa3ae4081c26bf16ea221a28c552535be53abefe", 2, 11),
}
DATA_SHA = {
    "orders.csv": "2d08d1fc6acdc4f26c4427f27ac7925bfb202ea2",
    "customers.json": "d6125fce237e7f7e3193667946d1eb117cd19db0",
    "orders_dirty.csv": "e36bedf1e6b9b5ef2582b007440c92ccf9fda83a",
    "snapshot_day1.csv": "12043a47a749ea54c89ae2becb509e22c991b399",
    "snapshot_day2.csv": "3966cea9b4f16dd9a7ac0da6d4beff201a60c7a1",
}
LINK = re.compile(
    r"\[▶ Run and edit this example\]\(<http://127\.0\.0\.1:8765/"
    r"\?part=(\d+)&lesson=(\d+)&snippet=(\d+)>\)"
)
TICK = chr(96)
FENCE = re.compile(
    r"(?ms)^" + re.escape(TICK * 3) + r"(python|text)[ \t]*\n(.*?)^" +
    re.escape(TICK * 3) + r"[ \t]*$"
)


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def verify_sources() -> None:
    for page, (name, sha, _, _) in LESSONS.items():
        assert git_blob_sha((PATTERNS / name).read_bytes()) == sha, f"Archived page {page} modified"
    for name, sha in DATA_SHA.items():
        assert git_blob_sha((DATA / name).read_bytes()) == sha, f"Archived dataset {name} modified"


def examples(page: int) -> dict[int, tuple[str, str | None]]:
    name, sha, count, lesson = LESSONS[page]
    raw = (PATTERNS / name).read_bytes()
    assert git_blob_sha(raw) == sha
    source = raw.decode("utf-8-sig")
    # These are source-side ungraded prompts; presence is not course completion.
    prompt_region = source.split("## Your turn", 1)
    assert len(prompt_region) == 2, f"Missing ungraded practice p.{page}"
    assert len(re.findall(r"(?m)^\s*[123]\. ", prompt_region[1].split("## W3Schools", 1)[0])) == 3
    links = list(LINK.finditer(source))
    assert len(links) == count, f"Wrong archived source link count p.{page}"
    found = {}
    for index, match in enumerate(links, 1):
        assert tuple(map(int, match.groups())) == (5, lesson, index)
        end = links[index].start() if index < len(links) else len(source)
        region = source[match.end():end]
        fences = [(f.group(1), f.group(2).strip("\n")) for f in FENCE.finditer(region)]
        assert fences and fences[0][0] == "python", f"Missing untouched source code p.{page} #{index}"
        code = fences[0][1]
        compile(code, f"original-mentorship-p{page}-{index}", "exec")
        if (page, index) == (67, 2):
            # Published API illustration: no stdout, requires requests and credentials;
            # check syntax/mock behavior separately without making an HTTP request.
            assert not any(k == "text" for k, _ in fences[1:])
            expected = None
        elif (page, index) == (66, 2):
            # Original source has an actual malformed closing 'two backticks + n'.
            # Inspect the unmodified printed text, rather than silently repairing it.
            assert len(fences) == 1, "Malformed archived transcript marker changed"
            open_marker = TICK * 3 + "text\n"
            broken_close = "\n" + TICK * 2 + "n\n"
            assert open_marker in region and broken_close in region
            start = region.index(open_marker) + len(open_marker)
            expected = region[start:region.index(broken_close, start)].strip("\n")
        else:
            assert len(fences) >= 2 and fences[1][0] == "text", f"No printed source output p.{page} #{index}"
            expected = fences[1][1]
        found[index] = (code, expected)
    assert list(found) == list(range(1, count + 1))
    return found


def copy_data(work: Path, override: dict[str, bytes] | None = None) -> None:
    target = work / "python_de_dataset"
    target.mkdir()
    for name in DATA_SHA:
        shutil.copyfile(DATA / name, target / name)
    for name, value in (override or {}).items():
        assert name in DATA_SHA, f"Unknown scratch-only input override {name}"
        (target / name).write_bytes(value)


def run(code: str, override: dict[str, bytes] | None = None) -> subprocess.CompletedProcess[str]:
    verify_sources()
    with tempfile.TemporaryDirectory(prefix="mentor-65-68-") as folder:
        work = Path(folder)
        copy_data(work, override)
        script = work / "original_source.py"
        script.write_text(code + "\n", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "-I", "-B", str(script)], cwd=work,
            input="", capture_output=True, text=True, timeout=25, check=False,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        for name, sha in DATA_SHA.items():
            path = work / "python_de_dataset" / name
            if override and name in override:
                assert path.read_bytes() == override[name], f"Scratch override mutated: {name}"
            else:
                assert git_blob_sha(path.read_bytes()) == sha, f"Scratch dataset modified: {name}"
    verify_sources()
    return result


def original_namespace(page: int, number: int) -> dict:
    code, _ = examples(page)[number]
    with tempfile.TemporaryDirectory(prefix="mentor-65-68-synthetic-") as folder:
        work = Path(folder)
        copy_data(work)
        before = Path.cwd()
        namespace = {"__name__": "auditor_original_source"}
        try:
            os.chdir(work)
            with contextlib.redirect_stdout(io.StringIO()):
                exec(compile(code, "archived-source", "exec"), namespace)
        finally:
            os.chdir(before)
    verify_sources()
    return namespace


class MentorshipPages65To68(unittest.TestCase):
    def test_pinned_original_sources_links_prompts_and_inputs(self):
        self.assertEqual(sum(item[2] for item in LESSONS.values()), 9)
        verify_sources()
        for page in LESSONS:
            with self.subTest(page=page):
                self.assertEqual(len(examples(page)), LESSONS[page][2])

    def test_eight_source_published_output_contracts(self):
        verified = 0
        for page in LESSONS:
            for number, (code, expected) in examples(page).items():
                if expected is None:
                    continue
                with self.subTest(page=page, original_snippet=number):
                    result = run(code)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stderr, "")
                    self.assertEqual(result.stdout.rstrip("\n"), expected.rstrip("\n"))
                    verified += 1
        self.assertEqual(verified, 8)

    def test_synthetic_p65_interval_containment_and_orphan_join(self):
        merge = original_namespace(65, 1)["merge"]
        self.assertEqual(merge([(1, 10), (2, 3), (10, 12)]), [[1, 12]])
        self.assertEqual(merge([(1, 2), (3, 4)]), [[1, 2], [3, 4]])
        # Source inserts the orphan into its integer-ID seen set, but drops it from joined.
        alternate_orders = (
            b"order_id,customer_id,order_date,status,amount\n"
            b"991,999999,2025-01-01,delivered,1.00\n"
        )
        code, _ = examples(65)[2]
        result = run(code, {"orders.csv": alternate_orders})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("0 joined, 1 orphans", result.stdout)

    def test_synthetic_p66_chunk_bounds_and_retry_exhaustion(self):
        scope = original_namespace(66, 1)
        with self.assertRaises(ValueError):
            list(scope["read_in_chunks"]("ignored.csv", 0))
        # Retry exhaustion is surfaced; no real sleep or network call.
        scope = original_namespace(66, 2)
        def always_limited():
            raise scope["RateLimited"]("429")
        with contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(scope["RateLimited"]):
                scope["with_retry"](always_limited, attempts=2, base=0.001)

    def test_synthetic_p67_repeated_cursor_and_lru_eviction(self):
        scope = original_namespace(67, 1)
        scope["fake_api"] = lambda cursor=None, limit=4: {"data": [99], "next_cursor": "loop"}
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(list(itertools.islice(scope["extract_all"](), 3)), [99, 99, 99])
        # Existing source lacks repeated-cursor detection; the test documents this risk.
        scope = original_namespace(67, 3)
        cache = scope["LRU"](2)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        self.assertEqual(list(cache.data), ["b", "c"])
        with self.assertRaises(ValueError):
            scope["LRU"](0)

    def test_synthetic_p67_requests_api_stub_no_network(self):
        # Execute the *original* requests-dependent definition against a stub
        # dependency and assert pagination/header/timeout, never live external HTTP.
        code, expected = examples(67)[2]
        self.assertIsNone(expected)
        class Reply:
            def __init__(self, values):
                self.values = values
            def raise_for_status(self):
                pass
            def json(self):
                return self.values
        class Session:
            def __init__(self):
                self.headers = {}
                self.calls = []
            def get(self, url, params=None, timeout=None):
                self.calls.append((url, params, timeout))
                if len(self.calls) == 1:
                    return Reply({"data": [1], "next": "/next"})
                return Reply({"data": [2], "next": None})
        session = Session()
        fake_requests = types.ModuleType("requests")
        fake_requests.Session = lambda: session
        previous = sys.modules.get("requests")
        sys.modules["requests"] = fake_requests
        try:
            namespace = {"__name__": "auditor_source_requests_stub"}
            exec(compile(code, "archived-request-source", "exec"), namespace)
            self.assertEqual(list(namespace["pages"]("/first", "fake-token", {"limit": 5})), [1, 2])
            self.assertEqual(session.headers["Authorization"], "Bearer fake-token")
            self.assertEqual(session.calls,
                             [("/first", {"limit": 5}, 30), ("/next", None, 30)])
        finally:
            if previous is None:
                del sys.modules["requests"]
            else:
                sys.modules["requests"] = previous

    def test_synthetic_p68_two_rejections_and_snapshot_caveats(self):
        scope = original_namespace(68, 1)
        two_bad = {"customer_id": "", "order_date": "2025-02-30",
                   "status": "delivered", "amount": "10", "order_id": "test"}
        _, errors = scope["validate"](two_bad)
        self.assertEqual(len(errors), 2)
        # Source float validation currently accepts NaN: document this as a defect.
        nan_row = {**two_bad, "customer_id": "1", "order_date": "2025-04-01", "amount": "NaN"}
        _, errors = scope["validate"](nan_row)
        self.assertEqual(errors, [])
        # Snapshot dict silently keeps the final duplicate ID in the incoming file.
        scope = original_namespace(68, 2)
        self.assertEqual(scope["inserts"], ["9"])
        self.assertEqual(scope["deletes"], ["8"])
        self.assertEqual([row[0] for row in scope["updates"]], ["4", "6"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
