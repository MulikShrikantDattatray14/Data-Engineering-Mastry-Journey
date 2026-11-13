#!/usr/bin/env python3
"""Read-only, source-pinned reviewer semantics for public-derived Pandas-07 MCQs.
Not Academy answer authentication, platform grading, learner attempts or mastery.
"""
from __future__ import annotations
import contextlib
import hashlib
import io
import os
import re
import unittest
from pathlib import Path
os.environ["MPLBACKEND"] = "Agg"
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

SRC = Path(__file__).resolve().parents[1] / "99. Reference Materials/Legacy Journey Snapshot/02-python/bosscoder/lecture-07/assignments"
PINS = (
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
)
def record(n):
    raw = (SRC / f"q{n:02d}.md").read_bytes()
    sha = hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    assert sha == PINS[n-1], (n, sha, PINS[n-1])
    return raw.decode("utf8")

def snippet(n):
    fence = re.escape(chr(96)*3)
    match = re.search(r"### Given code\s*\n"+fence+r"python\s*\n(.*?)\n"+fence,record(n),re.S)
    assert match is not None, n
    return match.group(1)

def replay(n, extra=None):
    ns = {"__name__":"__auditor__","pd":pd,"plt":plt,"sns":sns}
    if extra: ns.update(extra)
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        exec(compile(snippet(n),f"archived-q{n:02d}","exec"),ns,ns)
    return ns,log.getvalue()

class TestDerivedPandasMCQs(unittest.TestCase):
    def tearDown(self):
        plt.close("all")

    def test_00_hashes_options_and_original_pending_status(self):
        self.assertEqual(len(set(PINS)),10)
        for n in range(1,11):
            with self.subTest(q=n):
                t=record(n)
                self.assertIn(f"MCQ {n:02d}:",t)
                options=t.split("### Options",1)[1].split("## Topic reference",1)[0]
                self.assertEqual(re.findall(r"^([1-4])\. ",options,flags=re.M),["1","2","3","4"])
                for marker in ("**Status:** Pending student attempt.","**Your choice:** Pending",
                               "**Reviewed:** Pending","**Bosscoder submission status:** Unverified",
                               "**Solution and correct option:** Not included."):
                    self.assertIn(marker,t)

    def test_01_exact_derived_forward_fill_and_duplicate_options(self):
        ns,stdout=replay(1)
        self.assertEqual(ns["s"].reindex(range(5),method="ffill").tolist(),[1,1,2,2,3])
        self.assertIn("4    3",stdout)
        choices=re.findall(r"^[1-4]\. (.*)$",record(1).split("### Options",1)[1].split("## Topic reference",1)[0],flags=re.M)
        self.assertEqual(choices[0],choices[2])

    def test_02_exact_derived_loc_and_iloc_boundary(self):
        ns,stdout=replay(2)
        self.assertIn("x",stdout)
        self.assertIn("y",stdout)
        self.assertEqual(ns["df"].loc["x":"y"].index.tolist(),["x","y"])
        self.assertEqual(ns["df"].iloc[0:1].index.tolist(),["x"])

    def test_03_exact_derived_apply_and_all_null_boundary(self):
        ns,stdout=replay(3)
        self.assertEqual(ns["df"].apply(lambda x:x.max()-x.min()).tolist(),[2,2])
        self.assertIn("A    2",stdout)
        f=pd.DataFrame({"a":[2.,None,5.],"b":[None,None,None]})
        r=f.apply(lambda x:x.max()-x.min())
        self.assertEqual(r["a"],3)
        self.assertTrue(pd.isna(r["b"]))

    def test_04_exact_derived_transform_and_null_key(self):
        ns,stdout=replay(4)
        self.assertEqual(ns["df"].groupby("A")["B"].transform("mean").tolist(),[15.,15.,35.,35.])
        self.assertIn("35.0",stdout)
        x=pd.DataFrame({"k":["a","a",None],"v":[10,20,99]})
        self.assertTrue(pd.isna(x.groupby("k")["v"].transform("mean").iloc[-1]))
        self.assertEqual(x.groupby("k",dropna=False)["v"].transform("mean").iloc[-1],99)

    def test_05_exact_derived_dropna_reset_index_dtype(self):
        ns,stdout=replay(5)
        cleaned=ns["df"].dropna().reset_index(drop=True)
        self.assertEqual(cleaned.index.tolist(),[0,1,2])
        self.assertEqual(cleaned["A"].tolist(),[1.,2.,3.])
        self.assertIn("2  3.0",stdout)
        self.assertEqual(str(ns["df"]["A"].dtype),"float64")

    def test_06_missing_df_and_no_universal_speed_winner(self):
        with self.assertRaises(NameError):
            exec(compile(snippet(6),"isolated-q06","exec"),{})
        frame=pd.DataFrame({"A":[1,2,3]})
        replay(6,{"df":frame})
        self.assertEqual(frame["A"].sum(),frame["A"].values.sum())
        self.assertNotEqual(type(pd.Series([1,pd.NA],dtype="Int64").array).__name__,
                            type(frame["A"].values).__name__)
        print("Q06 BLOCKER: no archived DataFrame, dtype, benchmark protocol or Academy rubric")

    def test_07_exact_derived_best_legend(self):
        replay(7)
        ax=plt.gca()
        self.assertIsNotNone(ax.get_legend())
        self.assertEqual(ax.get_legend()._loc,0)
        self.assertEqual(len(ax.lines),1)

    def test_08_not_standalone_injected_pd_seaborn_line(self):
        with self.assertRaises(NameError):
            exec(compile(snippet(8),"isolated-q08","exec"),{})
        replay(8)
        ax=plt.gca()
        self.assertEqual(len(ax.lines),1)
        self.assertEqual(list(ax.lines[0].get_xdata()),[1.,2.,3.,4.])
        self.assertEqual(list(ax.lines[0].get_ydata()),[4.,3.,2.,1.])

    def test_09_not_standalone_injected_plt_subplots(self):
        with self.assertRaises(NameError):
            exec(compile(snippet(9),"isolated-q09","exec"),{})
        ns,_=replay(9)
        self.assertEqual(len(ns["fig"].axes),2)
        self.assertEqual(len(ns["ax"][0].lines),1)
        self.assertEqual(len(ns["ax"][1].patches),2)
        self.assertGreater(ns["ax"][0].get_position().y0,ns["ax"][1].get_position().y0)

    def test_10_not_standalone_injected_pd_bar(self):
        with self.assertRaises(NameError):
            exec(compile(snippet(10),"isolated-q10","exec"),{})
        replay(10)
        ax=plt.gca()
        self.assertEqual(len(ax.patches),3)
        self.assertEqual([float(b.get_height()) for b in ax.patches],[3.,2.,1.])
        self.assertEqual([t.get_text() for t in ax.get_xticklabels()],["1","2","3"])

if __name__ == "__main__":
    print("AUDITOR RUNTIME",pd.__version__,matplotlib.__version__,sns.__version__)
    unittest.main(verbosity=2)
