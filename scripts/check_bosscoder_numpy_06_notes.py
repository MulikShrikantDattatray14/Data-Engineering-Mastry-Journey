#!/usr/bin/env python3
"""Independent CI for public archived Bosscoder NumPy Lecture-06 notes.
The private 26-page original PDF is NOT available in GitHub Actions.
These checks do not grade the 12 Academy MCQs or award learner completion.
"""
from __future__ import annotations

import ast
import contextlib
import hashlib
import io
import re
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "99. Reference Materials/Legacy Journey Snapshot/02-python/bosscoder/lecture-06"
NOTE_SHA = {
    "01-arrays-creation-and-shapes.md": "25d84c5e48811483874c996bc0bccf438455f705",
    "02-indexing-and-computing.md": "64dcb7ed6a013830ad3e12cf87ad5d943bd1c90a",
    "03-manipulation-broadcasting.md": "7a81c28d8248afa1812b9320e7f0e1dde0fb962d",
    "04-structured-arrays.md": "a27673ef0572bb26546dad65d68a9eb71f2222b5",
}
MCQ_SHA = [
    "61b02ca73bd1e3a0722dfe3fdfb58cf6ddea9f08",
    "5654018fb5d3f4de542b997e81ab67dd2014590d",
    "4c776db42ce60d310def064e062d6f243b374294",
    "d9d901e3aed521e2a8956d87827d3d12f1672007",
    "48e3d40f69891342ef883fbd209a78d19db2d7b6",
    "0ca931a6cacc044a1897454919d016cb63367435",
    "9827c7cbe0b0ebe6ae3fb2dccf91771d5f6bcc87",
    "6d7d65662d42784278f56a94acd281869ea0bfdc",
    "bb8fcb06c9a957347657a9d6ab3e2cbbc74e267d",
    "4e3d5dc6d658a8462344bc06e8daec2df2bbd3d8",
    "30ae521de20e6a463f3aaae570226afffed59a45",
    "40377a8acd5cd2651e41d877a64b32455589592f",
]
# One independently predicted deterministic stdout anchor for each source code fence.
# Verify snippets in notebook order within each *individual public note chapter*.
ANCHORS = [
    ["(3,) 1", "(3,) (2, 3) (2, 3, 4)", "[[0 0 0]", "(3, 4) (2, 3, 2) (2, 6)", "0"],
    ["12\n", "[ 0 80  0  3  4  5]", "[3 5 8] [8 3 5]", "[12 24 35]", "5.0 [4. 6.]"],
    ["(4, 2) (2, 4)", "44", "[[11 22 33]\n [41 52 63]]", "[[17 27 37]\n [49 59 69]]"],
    ["315.25", "210.5 420.0"],
]


def pinned_text(path: Path, sha: str) -> str:
    raw = path.read_bytes()
    actual = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    assert actual == sha, (path, actual, sha)
    return raw.decode("utf-8")


def python_fences(note: str) -> list[str]:
    marker = chr(96) * 3
    return re.findall(
        r"^" + re.escape(marker + "python") + r"\s*\n(.*?)^" +
        re.escape(marker) + r"\s*$", note, flags=re.M | re.S,
    )


def check_notes() -> None:
    total = 0
    for name, expected_anchors in zip(NOTE_SHA, ANCHORS, strict=True):
        note = pinned_text(SOURCE / name, NOTE_SHA[name])
        fences = python_fences(note)
        assert len(fences) == len(expected_anchors), (name, len(fences))
        scope: dict = {"__name__": "__main__"}
        for index, (snippet, expected) in enumerate(zip(fences, expected_anchors, strict=True), 1):
            ast.parse(snippet, filename=f"{name}:{index}")
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                exec(compile(snippet, f"{name}:{index}", "exec"), scope, scope)
            out = buffer.getvalue()
            assert expected in out, (name, index, expected, out)
            total += 1
    assert total == 16, total
    print("PASS: 16/16 SHA-pinned archived independent public note fences executed; 16 stdout anchors checked")


def check_assignment_evidence() -> None:
    assert len(MCQ_SHA) == 12 and len(set(MCQ_SHA)) == 12
    for index, sha in enumerate(MCQ_SHA, 1):
        name = f"q{index:02d}.md"
        t = pinned_text(SOURCE / "assignments" / name, sha)
        assert f"MCQ {index:02d}" in t, name
        assert "## Four choices" in t and "## Independent attempt" in t, name
        options = t.split("## Four choices", 1)[1].split("## Independent attempt", 1)[0]
        assert re.findall(r"^([1-4])\. ", options, re.M) == ["1", "2", "3", "4"], name
        for pending in ("**Selected choice:** Pending", "**Reviewed:** Pending",
                        "**Academy completion:** Unverified"):
            assert pending in t, (name, pending)
        assert "**Answer:** Not provided." in t, name
    print("PASS: 12/12 unchanged MCQ records and all four options; 12 remain unattempted/ungraded")


def check_synthetic_edges() -> None:
    base = np.arange(6).reshape(2, 3)
    flattened = base.flatten()
    viewed = base.ravel()
    flattened[0] = 900
    viewed[0] = 800
    assert base[0, 0] == 800 and not np.shares_memory(base, flattened)
    print("PASS synthetic 1: flatten copy versus ravel view")

    base = np.arange(6).reshape(2, 3)
    assert np.shares_memory(base, base[:, 1:])
    assert not np.shares_memory(base, base[[0, 1]])
    assert not np.shares_memory(base, base[base > 2])
    print("PASS synthetic 2: basic slicing view versus integer/mask copy")

    output = np.zeros(3, dtype=int)
    returned = np.add([3, 4, 5], [6, 7, 8], out=output)
    assert returned is output and output.tolist() == [9, 11, 13]
    print("PASS synthetic 3: ufunc third operand is mutable output")

    table = np.ones((2, 3), dtype=int)
    assert (table + np.array([1, 2, 3])).tolist() == [[2, 3, 4], [2, 3, 4]]
    assert (table + np.array([4, 8]).reshape(2, 1)).tolist() == [[5, 5, 5], [9, 9, 9]]
    try:
        table + np.array([4, 8])
    except ValueError:
        pass
    else:
        raise AssertionError("incompatible shapes must not broadcast")
    print("PASS synthetic 4: compatible and incompatible broadcasting")

    vals = np.array([1., 2., 3.])
    assert np.isclose(np.std(vals), (2/3) ** .5)
    assert np.isclose(np.std(vals, ddof=1), 1.)
    print("PASS synthetic 5: population versus sample standard deviation")

    with np.errstate(divide="ignore", invalid="ignore"):
        result = np.divide([1., 0.], [0., 0.])
    assert np.isinf(result[0]) and np.isnan(result[1])
    print("PASS synthetic 6: NumPy non-scalar float divide-by-zero defaults")

    records = np.array([("longname", 4), ("bee", 2)],
                       dtype=[("code", "U3"), ("age", "i4")])
    assert records["code"].tolist() == ["lon", "bee"]
    assert np.sort(records, order="age")["age"].tolist() == [2, 4]
    print("PASS synthetic 7: structured field sorting and fixed-width Unicode truncation")


if __name__ == "__main__":
    check_notes()
    check_assignment_evidence()
    check_synthetic_edges()
    print("PASS Lecture 06 public-archive verification only; private PDF and Academy scores not in CI")
