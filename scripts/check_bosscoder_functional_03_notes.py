#!/usr/bin/env python3
"""Read-only regression of immutable Lecture-03 public notes, not Academy grades.

The original 42-page private Colab PDF is NOT stored in this public repository.
These checks exercise the separately authored archived Journey note examples and
unchanged MCQ prompt snapshots. See BOSSCODER-FUNCTIONAL-03-INDEPENDENT-AUDIT.md.
"""
from __future__ import annotations

import hashlib
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from itertools import islice
from functools import reduce, wraps

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "99. Reference Materials/Legacy Journey Snapshot/02-python/bosscoder/lecture-03"
NOTES = [
    ("01-functional-foundations.md", "35b176024bfe61e6160ada806b824a6fb3c8096c", [
        "425 425",
    ]),
    ("02-functions-and-purity.md", "9851216d322a8288b7fb13f05d0439076d33a92f", [
        "Status: paid",
        "101: unknown\n102: west\n60\n{'source': 'api', 'status': 'ok'}",
        "15",
        "done",
        "Format one record for readable logs.\n{'row_id': <class 'int'>, 'status': <class 'str'>, 'return': <class 'str'>}",
        "",
        "PAID\npaid",
        "paid",
    ]),
    ("03-lambdas-and-decorators.md", "4e347e44a859c84b7730a648c5b82d92bc2e47e9", [
        "[{'amount': 50}, {'amount': 200}]\nhigh",
        "[2, 2, 2]\n[0, 1, 2]",
        "Beginning transformation\nTransformation complete\npaid",
        "['OK', 'OK']",
        "",
        "",
        "",
    ]),
    ("04-map-filter-zip-reduce.md", "0b33dff445dfbd03cdc9130bd35a854bdec47b73", [
        "5\n[10, 15]\n[11, 22]",
        "[6, 8, 10]",
        "[{'id': 1, 'ok': True}]\n[('Asha', 25), ('Ria', 31)]",
        "120",
        "[('id', 101), ('status', 'paid'), ('amount', 499)]\n[(1, 'a'), (2, 'b')]",
        "('east', 'west') (2, 3)",
        "['demo.txt']\nhello",
        "24",
    ]),
]
ASSIGNMENT_SHAS = {
    "q01-lambda-default-argument.md": "611a105f59f6ee23c4fe7c5ac1e8509b46572159",
    "q02-map-two-iterables.md": "436aecc93ad121e80866854c8cffa9402c4648cd",
    "q03-functional-style.md": "4c5c99d6ef249aad2ce6615d942cccc5b2299c48",
    "q04-zip-to-dictionary.md": "88d3401159a4fb58a57671e4ed597144d8eaaec8",
    "q05-closure-cell.md": "6c0465f5683677b503b1c9bad2db18543fdc6650",
    "q06-lambda-vs-def.md": "ced215fec0aac6dbe290678b2bb66f34bab5b995",
    "q07-mutable-default-arguments.md": "9623ca7c3ee01a7b51d15695fb473629cd7bc18d",
    "q08-purity-and-global-variable.md": "9bb8820b3e0ac695c473ec192e1ebafe51620910",
    "q09-functional-programming-false-statement.md": "2e4819060da2fb4aba57ff7cefda671fd68b8bf9",
    "q10-reduce-subtraction.md": "06ed303bdb3ede531fe981c15102f43962930a6a",
}
def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

def checked_read(path: Path, sha: str) -> str:
    raw = path.read_bytes()
    actual = git_blob_sha(raw)
    assert actual == sha, f"Immutable source changed: {path} {actual} != {sha}"
    return raw.decode("utf-8-sig")

def archived_examples() -> int:
    count = 0
    fence = chr(96) * 3
    pattern = re.compile(re.escape(fence) + r"python\s*\n(.*?)\n" + re.escape(fence), re.S)
    for filename, expected_sha, expected_outputs in NOTES:
        text = checked_read(BASE / filename, expected_sha)
        examples = pattern.findall(text)
        assert len(examples) == len(expected_outputs), (filename, len(examples), len(expected_outputs))
        for number, (code, output) in enumerate(zip(examples, expected_outputs), 1):
            with tempfile.TemporaryDirectory(prefix="bosscoder-fp03-") as directory:
                run = subprocess.run(
                    [sys.executable, "-c", code], cwd=directory,
                    capture_output=True, text=True, timeout=15, check=False
                )
            assert run.returncode == 0, (filename, number, run.stderr)
            actual = run.stdout.rstrip("\n")
            assert actual == output, (filename, number, repr(actual), repr(output))
            count += 1
        print(f"PASS {filename}: {len(examples)} archived-note Python blocks and stdout contracts")
    return count

def pending_assignment_integrity() -> int:
    for filename, sha in ASSIGNMENT_SHAS.items():
        text = checked_read(BASE / "assignments" / filename, sha)
        assert re.search(r"\b(Pending|Unanswered)\b", text, re.I), filename
        assert re.search(r"(Unverified|Not verified)", text, re.I), filename
        assert not re.search(r"\*\*(?:Student selection|Reviewed answer):\*\*\s*(?:[1-4]|Correct)", text, re.I), filename
    print(f"PASS {len(ASSIGNMENT_SHAS)} archived assignment source hashes/statuses (learner & platform unverified)")
    return len(ASSIGNMENT_SHAS)

def synthetic_boundaries() -> int:
    # Auditor-generated edge cases, not published Academy solutions.
    evaluated = []
    full = list(map(lambda x: evaluated.append(x) or x*x, range(21)))[:3]
    assert full == [0, 1, 4] and len(evaluated) == 21
    evaluated.clear()
    lazy = list(islice(map(lambda x: evaluated.append(x) or x*x, range(21)), 3))
    assert lazy == full and len(evaluated) == 3

    late = [lambda: n for n in range(4)]
    fixed = [lambda n=n: n for n in range(4)]
    assert [f() for f in late] == [3] * 4
    assert [f() for f in fixed] == [0, 1, 2, 3]

    assert list(zip([1, 2, 3], ["a"])) == [(1, "a")]
    try:
        list(zip([1, 2, 3], ["a"], strict=True))
    except ValueError:
        pass
    else:
        raise AssertionError("zip(strict=True) failed to detect unequal streams")

    def unsafe(entry, bucket=[]):
        bucket.append(entry)
        return list(bucket)
    assert unsafe("x") == ["x"] and unsafe("y") == ["x", "y"]
    def safe(entry, bucket=None):
        if bucket is None:
            bucket = []
        bucket.append(entry)
        return bucket
    assert safe("x") == ["x"] and safe("y") == ["y"]

    def trace(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        return wrapper
    @trace
    def name_of(value: str) -> str:
        """sample metadata"""
        return value.upper()
    assert name_of("paid") == "PAID" and name_of.__name__ == "name_of" and name_of.__doc__ == "sample metadata"

    assert reduce(lambda a, b: a - b, [20, 4, 3]) == 13
    assert reduce(lambda a, b: a + b, [], 7) == 7
    try:
        reduce(lambda a, b: a + b, [])
    except TypeError:
        pass
    else:
        raise AssertionError("Unseeded empty reduce must raise TypeError")
    print("PASS six auditor-authored boundaries: lazy evaluation, late capture, strict zip, defaults, wraps, reduce")
    return 6

def main() -> None:
    example_count = archived_examples()
    assert example_count == 24
    pending_count = pending_assignment_integrity()
    synthetic_count = synthetic_boundaries()
    print(f"PASS Bosscoder Lecture-03: {example_count} original archived NOTE examples, "
          f"{pending_count} pending assignment snapshots, {synthetic_count} synthetic boundary groups. "
          "Private PDF source execution and graded answers NOT certified.")

if __name__ == "__main__":
    main()
