#!/usr/bin/env python3
"""Read-only reviewer tests for 11 *pending* Bosscoder Lecture-04 derived MCQs.

Independent Python behavior probes, NOT original Academy answer execution,
official grading, reconstructed missing original programs, or learner attempts.
"""
from __future__ import annotations

import asyncio
from contextlib import ExitStack, contextmanager
import hashlib
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "99. Reference Materials/Legacy Journey Snapshot/02-python/bosscoder/lecture-04/assignments"
EXPECTED = {
    "q01.md": "2da86260dc526bc5207de315bebd8d20aad9fe89",
    "q02.md": "5ef441ab29e04249bdb347a6c0317bb2879d26a0",
    "q03.md": "e846847aea325e52df9988c286601e06f27d0501",
    "q04.md": "2dde93666919e6b35338397f8e292ba5d2df610f",
    "q05.md": "667e329c8db55534e69115940e3a75c0b9e02aa1",
    "q06.md": "5dfe9de35078ee849a7818c88175118d4cb88307",
    "q07.md": "7b3e407edf04b37e1b929195139567dba09f677b",
    "q08.md": "abc35b782290ba0de7d0cb00dc51a02851d1e7d0",
    "q09.md": "8866d908c51ec752cdffe6c1dd4132571dab4364",
    "q10.md": "2c53992126b23446d531b0e520484448efb10fa2",
    "q11.md": "a8ab3c28d5e8ede1cc4118c8c714d2ecb4fccbbc",
}


def git_blob_sha(content: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()


class PendingLecture04MCQReviewerChecks(unittest.TestCase):
    def test_original_source_pins_and_unanswered_status(self):
        for name, expected in EXPECTED.items():
            with self.subTest(name=name):
                raw = (SOURCE / name).read_bytes()
                self.assertEqual(git_blob_sha(raw), expected)
                original = raw.decode("utf-8")
                self.assertIn("**Selection:** Pending", original)
                self.assertIn("**Reviewed:** Pending", original)
                self.assertIn("Four choices", original)
                self.assertIn("practice paraphrase", original)
        print("11 immutable derivative source pins and Pending statuses PASS")

    def test_q01_q09_two_coro_exception_handling_locations(self):
        async def inside():
            try:
                raise ValueError("bad")
            except ValueError:
                return "caught inside"

        async def failure():
            raise ValueError("bad")

        async def outside():
            try:
                await failure()
            except ValueError:
                return "caught at await"

        self.assertEqual(asyncio.run(inside()), "caught inside")
        self.assertEqual(asyncio.run(outside()), "caught at await")
        with self.assertRaisesRegex(ValueError, "bad"):
            asyncio.run(failure())
        print("Q01/Q09: inside and await-side catching both work; await alone does NOT suppress")

    def test_q02_reviewer_nested_try_finally_trace_not_original_program(self):
        trace = []
        try:
            try:
                1 / 0
            except ZeroDivisionError:
                trace.append("inner except")
            finally:
                trace.append("inner finally")
        finally:
            trace.append("outer finally")
        self.assertEqual(trace, ["inner except", "inner finally", "outer finally"])

    def test_q03_reviewer_explicit_raise(self):
        def throw():
            raise RuntimeError("example")
        with self.assertRaisesRegex(RuntimeError, "example"):
            throw()

    def test_q04_finally_normal_exception_and_return(self):
        trace = []
        try:
            trace.append("normal")
        finally:
            trace.append("normal finally")
        try:
            raise LookupError("example")
        except LookupError:
            trace.append("caught")
        finally:
            trace.append("caught finally")

        def early_return():
            try:
                return "value"
            finally:
                trace.append("return finally")

        self.assertEqual(early_return(), "value")
        self.assertEqual(trace, ["normal", "normal finally", "caught", "caught finally", "return finally"])
        # This does not cover abrupt process termination.

    def test_q05_exitstack_lifo_dynamic_and_opt_in_suppression(self):
        trace = []

        @contextmanager
        def resource(label):
            trace.append("enter " + label)
            try:
                yield label
            finally:
                trace.append("exit " + label)

        with ExitStack() as stack:
            for label in ("a", "b", "c"):
                self.assertEqual(stack.enter_context(resource(label)), label)
        self.assertEqual(trace, ["enter a", "enter b", "enter c", "exit c", "exit b", "exit a"])
        with self.assertRaises(KeyError):
            with ExitStack():
                raise KeyError("not automatically suppressed")
        with ExitStack() as stack:
            stack.push(lambda exc_type, exc, tb: exc_type is LookupError)
            raise LookupError("suppression explicitly requested")

    def test_q06_exception_chaining_cause_vs_wrapper_message(self):
        class WrappedError(Exception):
            pass

        try:
            try:
                int("not-an-int")
            except ValueError as cause:
                raise WrappedError("wrapper") from cause
        except WrappedError as err:
            self.assertEqual(str(err), "wrapper")
            self.assertIsInstance(err.__cause__, ValueError)
            self.assertIn("invalid literal", str(err.__cause__))
            self.assertTrue(err.__suppress_context__)
        else:
            self.fail("expected wrapped exception")
        # Precise original print call absent; no claimed MCQ output/key.

    def test_q07_reviewer_zero_division_warning(self):
        trace = []
        try:
            _ = 9 / 0
        except ZeroDivisionError:
            trace.append("custom warning")
        self.assertEqual(trace, ["custom warning"])

    def test_q08_propagation_through_caller_and_top_level(self):
        def inner():
            raise ValueError("from inner")

        def outer():
            return inner()

        with self.assertRaisesRegex(ValueError, "from inner"):
            outer()
        print("Q08: propagation and uncaught top-level termination are compatible scopes")

    def test_q10_tuple_of_types_shared_except(self):
        trace = []
        for exc in (ValueError("v"), KeyError("k"), TypeError("t")):
            try:
                raise exc
            except (ValueError, KeyError):
                trace.append("shared")
            except TypeError:
                trace.append("separate")
        self.assertEqual(trace, ["shared", "shared", "separate"])

    def test_q11_two_source_variants_produce_different_traces(self):
        trace = []

        def inner():
            try:
                raise ValueError("boom")
            finally:
                trace.append("inner finally")

        def outer():
            try:
                inner()
            except ValueError:
                trace.append("outer except")
            finally:
                trace.append("outer finally")

        outer()
        self.assertEqual(trace, ["inner finally", "outer except", "outer finally"])
        trace.clear()

        def inner_caught():
            try:
                raise ValueError("boom")
            except ValueError:
                trace.append("inner except")
            finally:
                trace.append("inner finally")

        def outer_variant():
            try:
                inner_caught()
            finally:
                trace.append("outer finally")

        outer_variant()
        self.assertEqual(trace, ["inner except", "inner finally", "outer finally"])
        print("Q11: original program omitted; distinct possible print sequences reproduced")


if __name__ == "__main__":
    unittest.main(verbosity=2)
