#!/usr/bin/env python3
"""Read-only source-pinned reviewer of five live W3 Python collection/method pages.

Archived source snippets are replayed for source parity, not learner credit.
Other checks are synthetic Python semantics, NOT official W3 editor grades.
"""
from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import hashlib
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "99. Reference Materials" / "Original Mastery Snapshot" / "2. Python Mastry" / "1. Python from Zero"
ORIGINALS = (
    ("04. Strings - working with text.md", "efd9df91f7af2cb988eb406a1982350243dfc11a", "PDF page 8"),
    ("10. Lists - ordered collections.md", "bc2b6ec4ec0b77409570b19044e7ade55a51e961", "page 14 of 80"),
    ("11. Tuples and sets.md", "3a2788bfc668b3a1ebe5bfd6f58f8fc8c9bfcb2e", "page 15 of 80"),
    ("12. Dictionaries - key and value.md", "3602334cd9cc779f89eface11b82f844954068a8", "page 16 of 80"),
    ("13. Which data structure.md", "1142a434f0bda23d683eaf2de5176a4c13020438", "page 17 of 80"),
)
HOSTED = (
    "https://www.w3schools.com/python/python_strings_methods.asp",
    "https://www.w3schools.com/python/python_lists_methods.asp",
    "https://www.w3schools.com/python/python_lists_comprehension.asp",
    "https://www.w3schools.com/python/python_dictionaries_methods.asp",
    "https://www.w3schools.com/python/python_sets_methods.asp",
)

def blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

def source_text(name: str) -> str:
    # Reject any mutated/unpinned Markdown BEFORE executing source examples,
    # including on pull-request CI where another test could otherwise run it.
    matches = [sha for filename, sha, _ in ORIGINALS if filename == name]
    if len(matches) != 1:
        raise AssertionError("Unapproved source file for original-code replay")
    raw = (BASE / name).read_bytes()
    if blob_sha(raw) != matches[0]:
        raise AssertionError("Original source blob changed; refusing code replay")
    return raw.decode("utf-8-sig")

def published_pairs(name: str) -> list[tuple[str, str]]:
    # Two literal fence styles exist in this preserved source archive.
    fence = "(?:" + re.escape(chr(96)*3) + "|~~~)"
    rx = fence + r"python\n(.*?)\n" + fence + r"\s*(?:Output:\s*)?" + fence + r"text\n(.*?)\n" + fence
    return re.findall(rx, source_text(name), re.DOTALL)

def replay(name: str, indexes: tuple[int, ...]) -> None:
    pairs = published_pairs(name)
    for index in indexes:
        code, published = pairs[index]
        with StringIO() as captured, redirect_stdout(captured):
            exec(compile(code, name + ":original-example-" + str(index + 1), "exec"),
                 {"__name__": "__audit_replay__"})
            actual = captured.getvalue().rstrip("\n")
        # Archive Markdown trims invisible end-of-line spaces from the printed
        # sample (L12 snippet 2 uses print(product, end=" ")). Preserve every
        # visible character and line; ignore only trailing ASCII spaces.
        norm = lambda value: "\n".join(line.rstrip(" ") for line in value.splitlines())
        if norm(actual) != norm(published):
            raise AssertionError(f"{name} original example {index + 1}: {actual!r} != {published!r}")

class W3PythonCollectionMethodsFiveCrossSource(unittest.TestCase):
    def test_01_five_original_git_blob_pins_and_pdf_companion_references(self):
        for name, sha, page in ORIGINALS:
            with self.subTest(name=name):
                raw = (BASE / name).read_bytes()
                self.assertEqual(sha, blob_sha(raw))
                self.assertIn(page, raw.decode("utf-8-sig"))
        self.assertEqual(5, len(set(HOSTED)))

    def test_02_replay_original_string_snippets_one_and_two(self):
        replay(ORIGINALS[0][0], (0, 1))

    def test_03_replay_original_list_snippets_one_and_two(self):
        replay(ORIGINALS[1][0], (0, 1))

    def test_04_replay_original_set_snippets_two_and_three(self):
        replay(ORIGINALS[2][0], (1, 2))

    def test_05_replay_original_dict_snippets_one_and_two(self):
        replay(ORIGINALS[3][0], (0, 1))

    def test_06_dictionary_keys_values_items_are_live_views_not_lists(self):
        d = {"a": 1}
        keys, values, items = d.keys(), d.values(), d.items()
        for view in (keys, values, items):
            self.assertNotIsInstance(view, list)
        d["b"] = 2
        self.assertEqual(["a", "b"], list(keys))
        self.assertEqual([1, 2], list(values))
        self.assertEqual([("a", 1), ("b", 2)], list(items))

    def test_07_live_dict_view_iterator_rejects_key_size_mutation(self):
        d = {"a": 1, "b": 2}
        it = iter(d.items())
        self.assertEqual(("a", 1), next(it))
        d["c"] = 3
        with self.assertRaises(RuntimeError):
            next(it)

    def test_08_dictionary_get_and_setdefault_missing_vs_present_none(self):
        d = {"a": None}
        self.assertIsNone(d.get("a", "fallback"))
        self.assertEqual("fallback", d.get("missing", "fallback"))
        self.assertIsNone(d.setdefault("a", 9))
        self.assertEqual(9, d.setdefault("new", 9))
        self.assertEqual({"a": None, "new": 9}, d)

    def test_09_dict_shallow_copy_and_fromkeys_shared_mutable_default(self):
        a = {"key": [1]}
        b = a.copy()
        self.assertIsNot(a, b)
        b["key"].append(2)
        self.assertEqual([1, 2], a["key"])
        shared = dict.fromkeys(("x", "y"), [])
        shared["x"].append(7)
        self.assertEqual([7], shared["y"])
        self.assertIs(shared["x"], shared["y"])

    def test_10_list_sort_returns_none_and_sorted_keeps_input(self):
        amounts = [3, 1, 2]
        self.assertEqual([1, 2, 3], sorted(amounts))
        self.assertEqual([3, 1, 2], amounts)
        self.assertIsNone(amounts.sort())
        self.assertEqual([1, 2, 3], amounts)

    def test_11_list_remove_first_occurrence_pop_and_missing_errors(self):
        a = [2, 1, 2]
        a.remove(2)
        self.assertEqual([1, 2], a)
        self.assertEqual(1, a.pop(0))
        self.assertEqual([2], a)
        with self.assertRaises(ValueError):
            a.remove(999)
        with self.assertRaises(IndexError):
            a.pop(20)

    def test_12_list_extend_vs_append_and_shallow_copy(self):
        a = [[1]]
        copied = a.copy()
        copied[0].append(2)
        self.assertEqual([[1, 2]], a)
        a.extend((3, 4))
        self.assertEqual([[1, 2], 3, 4], a)
        a.append([5, 6])
        self.assertEqual([5, 6], a[-1])

    def test_13_list_comprehension_filter_vs_mapping_and_generator_exhaustion(self):
        fruits = ["apple", "banana", "cherry"]
        self.assertEqual(["apple", "banana"], [x for x in fruits if "a" in x])
        self.assertEqual(["apple", "orange", "cherry"],
                         [x if x != "banana" else "orange" for x in fruits])
        self.assertEqual(["apple", "banana", "cherry"], fruits)
        gen = (i for i in range(4))
        self.assertEqual([0, 2], [i for i in gen if i % 2 == 0])
        self.assertEqual([], list(gen))

    def test_14_set_difference_vs_in_place_difference_update(self):
        yesterday, today = {101, 102, 103}, {102, 104}
        self.assertEqual({104}, today.difference(yesterday))
        self.assertEqual({102, 104}, today)
        self.assertIsNone(today.difference_update(yesterday))
        self.assertEqual({104}, today)
        self.assertEqual({101, 102, 103, 104}, yesterday | {104})

    def test_15_set_discard_remove_hashability_and_bool_int_collision(self):
        a = {True, 1, False, 0, 2}
        self.assertEqual(3, len(a))
        a.discard(12345)
        with self.assertRaises(KeyError):
            a.remove(12345)
        with self.assertRaises(TypeError):
            a.add([1, 2])
        self.assertEqual({1, 2, 3}, set([1, 2, 2, 3]))

    def test_16_string_methods_find_index_casefold_and_immutability(self):
        original = "  STRASSE  "
        clean = original.strip().casefold()
        self.assertEqual("strasse", clean)
        self.assertEqual("  STRASSE  ", original)
        self.assertEqual(-1, clean.find("x"))
        with self.assertRaises(ValueError):
            clean.index("x")
        self.assertEqual("ss", "ß".casefold())
        self.assertEqual("x x", "a a".replace("a", "x"))

if __name__ == "__main__":
    unittest.main(verbosity=2)
