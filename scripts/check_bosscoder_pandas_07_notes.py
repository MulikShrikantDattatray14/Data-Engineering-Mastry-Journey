#!/usr/bin/env python3
"""Source-pinned, read-only CI for archived public Bosscoder pandas Lecture 07.

The private Academy 21-page PDF is NOT available inside GitHub Actions;
passing does not certify private Colab cell replay, Academy grades or mastery.
"""
from __future__ import annotations
import ast
import contextlib
import hashlib
import io
import os
import re
import sqlite3
import tempfile
from pathlib import Path

os.environ["MPLBACKEND"] = "Agg"
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "99. Reference Materials/Legacy Journey Snapshot/02-python/bosscoder/lecture-07"
NOTE_SHA = {
    "01-pandas-fundamentals.md": "36b1de4dd156aba649a048f7bf886f86826a4ac2",
    "02-pandas-transformations-and-io.md": "dcbc211cc83e9301cb3c45e02e3174a621c77c8f",
    "03-data-visualisation.md": "4399919ff28833f429a5203104463fbde18c8515",
}
MCQ_SHA = [
    "ba6627cc4500c4193f19d286e3774c1b8c080333",
    "b0810b24d1d62515d3579f4a9fc99e585ef4e26f",
    "1469fcb14bd69ee230f67b66dfef1d0fbc201e4e",
    "fbbdf5790b18a85028e2d11c2de7be038efb98d3",
    "2a3aaed9911130cbcaf2cc0aeff97781933515ff",
    "178900492e03848e7d03e1e76b29f2c9a2c7413c",
    "1fec8f9c921a1dfd1c2bbe5f69829fcf3f23f462",
    "317614bb14da79e16f5dba88b82c096664488ccb",
    "6795c608475326184f022fc3cbd739dec5dc190a",
    "40791f4b593e59d07640372e348f92676e6ae307",
]
# Each anchor is separately predicted from the archived public note code.
# None indicates an output-free example whose state/plot is checked directly.
ANCHORS = [
    ["2.3.3", "120\n80", "west\n120", "Data columns (total 3 columns)", "101", "Amit"],
    ["gross_amount", "gross_amount", "payment_order_id", "3", "east", None, "qty"],
    [None, None, None, None],
]

def pinned_text(path: Path, expected_sha: str) -> str:
    raw = path.read_bytes()
    actual = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    assert actual == expected_sha, (str(path), actual, expected_sha)
    return raw.decode("utf-8")

def python_fences(note: str) -> list[str]:
    marker = re.escape(chr(96) * 3)
    return re.findall(r"^" + marker + r"python\s*\n(.*?)^" + marker + r"\s*$",
                      note, flags=re.M | re.S)

def check_notes() -> None:
    total = 0
    for chapter, (name, expected) in enumerate(zip(NOTE_SHA, ANCHORS, strict=True), 1):
        snippets = python_fences(pinned_text(SOURCE / name, NOTE_SHA[name]))
        assert len(snippets) == len(expected), (name, len(snippets), len(expected))
        scope: dict = {"__name__": "__main__"}
        for num, (snippet, anchor) in enumerate(zip(snippets, expected, strict=True), 1):
            ast.parse(snippet, filename=f"{name}:fence-{num}")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                exec(compile(snippet, f"{name}:fence-{num}", "exec"), scope, scope)
            if anchor is not None:
                assert anchor in out.getvalue(), (name, num, anchor, out.getvalue())
            if chapter == 2 and num == 6:
                assert scope["events"]["year"].tolist() == [2026, 2026]
                assert scope["events"]["next_day"].dt.day.tolist() == [6, 7]
            if chapter == 2 and num == 7:
                assert scope["data"]["total"].tolist() == [20.0, 60.0, 60.0]
                assert str(scope["data"]["qty"].dtype) == "int8"
            if chapter == 3:
                ax = plt.gcf().axes
                if num == 1:
                    assert len(ax) == 1 and ax[0].get_title() == "Daily ingestion volume"
                    assert list(ax[0].lines[0].get_ydata()) == [100, 130, 120, 150]
                elif num == 2:
                    assert len(ax) == 2 and len(ax[0].lines) == 1 and len(ax[1].patches) == 2
                elif num == 3:
                    assert len(ax) == 1 and ax[0].get_title() == "Pipeline stage durations"
                    assert any(np.isclose(p.get_height(), 3.5) for p in ax[0].patches)
                else:
                    assert len(ax) == 1 and len(ax[0].collections) >= 1
                plt.close("all")
            total += 1
    assert total == 17, total
    print("PASS: 17/17 unchanged SHA-pinned public-note Python fences: 13 stdout/state and 4 plot structure contracts")

def check_mcq_evidence() -> None:
    assert len(MCQ_SHA) == len(set(MCQ_SHA)) == 10
    for i, sha in enumerate(MCQ_SHA, 1):
        text = pinned_text(SOURCE / "assignments" / f"q{i:02d}.md", sha)
        assert f"MCQ {i:02d}:" in text, i
        assert "### Options" in text and "## Your attempt" in text, i
        section = text.split("### Options", 1)[1].split("## Topic reference", 1)[0]
        assert re.findall(r"^([1-4])\. ", section, flags=re.M) == ["1", "2", "3", "4"], i
        for marker in ("**Status:** Pending student attempt.",
                       "**Your choice:** Pending", "**Reviewed:** Pending",
                       "**Bosscoder submission status:** Unverified",
                       "**Solution and correct option:** Not included."):
            assert marker in text, (i, marker)
    print("PASS: 10/10 immutable MCQ records and four options; all remain pending and ungraded")

def check_synthetic_edges() -> None:
    duplicate = pd.Series([5, 8, 13], index=["a", "a", "b"])
    assert not duplicate.index.is_unique
    try:
        duplicate.reindex(["a", "b"])
    except ValueError:
        pass
    else:
        raise AssertionError("duplicate-label reindex must not be assumed safe")
    print("PASS synthetic 1: nonunique Index labels and ambiguous reindex")

    frame = pd.DataFrame({"v": [10, 20, 30]}, index=["x", "y", "z"])
    assert frame.loc["x":"y", "v"].tolist() == [10, 20]
    assert frame.iloc[0:1]["v"].tolist() == [10]
    print("PASS synthetic 2: label-inclusive versus positional-exclusive slicing")

    left = pd.DataFrame({"id": [1, 2], "sales": [10, 20]})
    right = pd.DataFrame({"id": [1, 1], "tag": ["a", "b"]})
    assert len(left.merge(right, on="id", how="left")) == 3
    try:
        left.merge(right, on="id", how="left", validate="many_to_one")
    except pd.errors.MergeError:
        pass
    else:
        raise AssertionError("many_to_one must reject nonunique lookup")
    print("PASS synthetic 3: join grain and merge(validate=...)")

    groups = pd.DataFrame({"team": ["A", "A", None], "score": [10, 20, 40]})
    assert groups.groupby("team")["score"].sum().sum() == 30
    assert groups.groupby("team", dropna=False)["score"].sum().sum() == 70
    assert groups.groupby("team")["score"].transform("mean").iloc[:2].tolist() == [15, 15]
    print("PASS synthetic 4: NULL groups and transform per-row alignment")

    stamp = pd.to_datetime(pd.Series(["2024-08-17", "not-a-date"]),
                           errors="coerce", utc=True, format="%Y-%m-%d")
    assert stamp.iloc[0].year == 2024 and pd.isna(stamp.iloc[1])
    assert str(stamp.dt.tz) == "UTC"
    print("PASS synthetic 5: date parse failure and explicit timezone")

    table = pd.DataFrame({"id": [1, 2], "value": [10.0, 20.0]})
    with tempfile.TemporaryDirectory() as td:
        csv, lines = Path(td) / "x.csv", Path(td) / "x.jsonl"
        table.to_csv(csv, index=False)
        table.to_json(lines, orient="records", lines=True)
        assert pd.read_csv(csv).to_dict("list") == table.to_dict("list")
        assert pd.read_json(lines, lines=True).to_dict("list") == table.to_dict("list")
        con = sqlite3.connect(":memory:")
        try:
            assert table.to_sql("test_rows", con, index=False) == 2
            assert pd.read_sql_query("SELECT * FROM test_rows ORDER BY id", con)["id"].tolist() == [1, 2]
        finally:
            con.close()
    print("PASS synthetic 6: isolated CSV / JSON Lines / SQLite I-O")

    fig, ax = plt.subplots()
    sns.lineplot(data=pd.DataFrame({"x": [1, 2, 3], "y": [3, 2, 1]}),
                 x="x", y="y", ax=ax)
    assert len(ax.lines) == 1 and list(ax.lines[0].get_ydata()) == [3, 2, 1]
    plt.close(fig)
    print("PASS synthetic 7: headless Seaborn figure structure")

if __name__ == "__main__":
    assert pd.__version__ == "2.3.3", ("CI pandas pin changed", pd.__version__)
    print("VERSIONS pandas", pd.__version__, "numpy", np.__version__,
          "matplotlib", matplotlib.__version__, "seaborn", sns.__version__)
    check_notes()
    check_mcq_evidence()
    check_synthetic_edges()
    print("PASS public-archive evidence only; private PDF is not in CI and no Academy answers/grades were checked")
