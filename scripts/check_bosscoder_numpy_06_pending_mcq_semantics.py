#!/usr/bin/env python3
"""Reviewer-only NumPy Lecture-06 MCQ semantics, NEVER Academy grading.

The public records are independent paraphrases of private screenshots; exact
question programs and authenticated answer keys are absent. Keep learner
answers, completion and original source files unchanged.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "99. Reference Materials/Legacy Journey Snapshot/02-python/bosscoder/lecture-06/assignments"
PINS = (
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
)


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\\0" + data).hexdigest()


class NumPy06ReviewerOnly(unittest.TestCase):
    def test_00_all_source_blobs_and_unsolved_status(self):
        self.assertEqual(len(PINS), len(set(PINS)))
        self.assertEqual(len(PINS), 12)
        for i, expected in enumerate(PINS, 1):
            with self.subTest(question=i):
                data = (SRC / f"q{i:02d}.md").read_bytes()
                self.assertEqual(git_blob_sha(data), expected)
                statement = data.decode("utf-8")
                self.assertIn("independent paraphrase", statement)
                self.assertIn(f"MCQ {i:02d}", statement)
                self.assertIn("## Four choices", statement)
                self.assertIn("**Selected choice:** Pending", statement)
                self.assertIn("**Reviewed:** Pending", statement)
                self.assertIn("**Academy completion:** Unverified", statement)
                self.assertIn("**Answer:** Not provided.", statement)
                option_region = statement.split("## Four choices", 1)[1].split("## Independent attempt", 1)[0]
                for n in range(1, 5):
                    self.assertIn(f"{n}. ", option_region)
        readme = (SRC / "README.md").read_text(encoding="utf-8")
        self.assertIn("Pending", readme)

    def test_01_dtype_inference_platform_boundary(self):
        integers = np.array([1, 2, 3])
        floats = np.array([1.0, 2.0, 3.0])
        self.assertEqual(integers.dtype.kind, "i")
        self.assertEqual(floats.dtype.kind, "f")
        self.assertEqual(floats.dtype.itemsize, 8)
        self.assertIn(integers.dtype.itemsize, (4, 8))
        self.assertEqual(np.array([1, 2.5]).dtype.kind, "f")
        self.assertEqual(np.array([1, 2], dtype=np.int32).dtype.itemsize, 4)
        # Never infer an original screenshot's exact dtype or operating system.

    def test_02_ones_like_shape_and_explicit_dtype(self):
        source = np.zeros((2, 3))
        result = np.ones_like(source, dtype=int)
        self.assertEqual(result.shape, (2, 3))
        self.assertEqual(result.dtype.kind, "i")
        self.assertEqual(result.tolist(), [[1, 1, 1], [1, 1, 1]])
        self.assertEqual(np.ones_like(source).dtype, source.dtype)

    def test_03_one_inferred_axis_and_bad_dimensions(self):
        a = np.arange(8).reshape((2, -1, 2))
        self.assertEqual(a.shape, (2, 2, 2))
        self.assertEqual(a.ravel().tolist(), list(range(8)))
        with self.assertRaises(ValueError):
            np.arange(8).reshape((3, -1, 2))
        with self.assertRaises(ValueError):
            np.arange(8).reshape((-1, -1))

    def test_04_ravel_view_or_copy_depends_on_layout(self):
        a = np.array([[1, 2], [3, 4]])
        flat = a.ravel()
        self.assertTrue(np.shares_memory(a, flat))
        flat[0] = 99
        self.assertEqual(a.tolist(), [[99, 2], [3, 4]])
        reversed_rows = a[::-1, :]
        copied = reversed_rows.ravel()
        self.assertFalse(np.shares_memory(a, copied))
        copied[0] = -1
        self.assertEqual(a.tolist(), [[99, 2], [3, 4]])

    def test_05_functional_sort_vs_method_sort(self):
        a = np.array([3, 1, 2])
        ordered = np.sort(a)
        self.assertEqual(ordered.tolist(), [1, 2, 3])
        self.assertEqual(a.tolist(), [3, 1, 2])
        self.assertFalse(np.shares_memory(a, ordered))
        a.sort()
        self.assertEqual(a.tolist(), [1, 2, 3])

    def test_06_boolean_mask_assignment_vs_selection(self):
        a = np.arange(6)
        selected = a[a % 2 == 0]
        self.assertEqual(selected.tolist(), [0, 2, 4])
        self.assertFalse(np.shares_memory(a, selected))
        a[a % 2 == 0] = -1
        self.assertEqual(a.tolist(), [-1, 1, -1, 3, -1, 5])

    def test_07_integer_fancy_index_order_and_bounds(self):
        a = np.array([10, 20, 30, 40])
        selected = a[[3, 1, 2, 0]]
        self.assertEqual(selected.tolist(), [40, 20, 30, 10])
        self.assertFalse(np.shares_memory(a, selected))
        with self.assertRaises(IndexError):
            _ = a[[4]]

    def test_08_last_rows_reverse_columns_and_view(self):
        a = np.arange(12).reshape(3, 4)
        view = a[1:, ::-1]
        self.assertEqual(view.tolist(), [[7, 6, 5, 4], [11, 10, 9, 8]])
        self.assertTrue(np.shares_memory(a, view))
        view[0, 0] = -7
        self.assertEqual(a[1, 3], -7)

    def test_09_elementwise_versus_dot_rank(self):
        a, b = np.array([1, 2, 3]), np.array([4, 5, 6])
        self.assertEqual((a * b).tolist(), [4, 10, 18])
        self.assertEqual((a @ b).item(), 32)
        self.assertEqual(np.ndim(a @ b), 0)
        self.assertEqual((a.reshape(1, 3) @ b.reshape(3, 1)).shape, (1, 1))

    def test_10_broadcast_row_vector_and_bad_axis(self):
        rows = np.ones((2, 3), dtype=int)
        self.assertEqual((rows + np.arange(3)).tolist(), [[1, 2, 3], [1, 2, 3]])
        self.assertEqual((rows + np.array([[10], [20]])).tolist(), [[11, 11, 11], [21, 21, 21]])
        with self.assertRaises(ValueError):
            _ = rows + np.arange(2)
        # Original screenshot omitted; np.ones default would be FLOAT, not int.

    def test_11_1d_stacking_and_2d_non_added_axis(self):
        a, b = np.array([1, 2]), np.array([3, 4])
        self.assertEqual(np.vstack((a, b)).shape, (2, 2))
        self.assertEqual(np.hstack((a, b)).shape, (4,))
        x = np.ones((2, 3))
        self.assertEqual(np.vstack((x, x)).shape, (4, 3))
        self.assertEqual(np.hstack((x, x)).shape, (2, 6))

    def test_12_structured_bytes_unicode_field_and_mean(self):
        byte_rows = np.array([("Amy", 20), ("Bob", 35)],
                             dtype=[("name", "S3"), ("age", "i4")])
        self.assertEqual(byte_rows["name"][0], b"Amy")
        self.assertEqual(float(byte_rows["age"].mean()), 27.5)
        unicode_rows = np.array([("Amy", 20), ("Bob", 35)],
                                dtype=[("name", "U3"), ("age", "i4")])
        self.assertEqual(unicode_rows["name"][0], "Amy")
        # Byte vs text presentation cannot be established without source dtype.


if __name__ == "__main__":
    unittest.main(verbosity=2)
