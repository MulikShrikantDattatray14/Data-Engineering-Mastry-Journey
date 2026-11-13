#!/usr/bin/env python3
"""Source-pinned reviewer-only semantics for 12 PENDING Bosscoder OOP Lecture-05 MCQs.

Original Academy screenshots/executable programs, keys, grades and learner attempts
are NOT available. This is NOT official-answer verification or student completion.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
import hashlib
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "99. Reference Materials/Legacy Journey Snapshot/02-python/bosscoder/lecture-05/assignments"
EXPECTED = {
    "q01-class-instance-attributes.md": "5af9009d9f01b17366c641efcd54f0b16910c969",
    "q02-private-name-hasattr.md": "f34d83fabdef488eb501ec8dda7eef60d436cd52",
    "q03-method-shadowing.md": "9ba45edd4052c7e436ca54ef12ff8845946a0d4a",
    "q04-staticmethod-class-call.md": "4189716be2e86ec62cb2598fb7648031751b7d5b",
    "q05-method-shadowing-variant.md": "fe2b5837a64ba60d1f2ea696b5a29c62632241a2",
    "q06-abstract-class.md": "74ae715d294ac099291724c7434c9102af0ede68",
    "q07-polymorphic-override.md": "5a18928eb83ee05720444bb77d3645634a968b5d",
    "q08-diamond-method-resolution.md": "d2fc2d897589947e1fb6f4aafecf9101bbb55357",
    "q09-mro-tuple.md": "46d2054921d7a907be8640afb16922db0c18f5de",
    "q10-subclass-constructor.md": "9593fa307e7a692c97672252c4da5cdae70d5926",
    "q11-shared-class-list.md": "ad68c62247b10da80e11d7680ec74867e27b832b",
    "q12-explicit-super.md": "4ef15709785cf6f7a34759682631aaef17ab21a9"
}


def git_blob_sha(content: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()


class Lecture05OOPPendingReviewerChecks(unittest.TestCase):
    def test_all_twelve_immutable_derived_statements_still_pending(self):
        self.assertEqual(len(EXPECTED), 12)
        for filename, sha in EXPECTED.items():
            with self.subTest(filename=filename):
                raw = (SOURCE / filename).read_bytes()
                self.assertEqual(git_blob_sha(raw), sha)
                text = raw.decode("utf-8")
                self.assertIn("study-purpose paraphrase", text)
                self.assertIn("**Chosen option:** Pending", text)
                self.assertIn("**Review:** Pending", text)
                self.assertIn("**Platform completion:** Not verified", text)
                self.assertIn("Four choices", text)
        readme = (SOURCE / "README.md").read_text(encoding="utf-8")
        self.assertIn("0/12 reviewed", readme)

    def test_q01_class_instance_attribute_independence(self):
        class C:
            x = 5
            def __init__(self):
                self.x = 10
        obj = C()
        self.assertEqual((obj.x, C.x), (10, 5))
        del obj.x
        self.assertEqual(obj.x, 5)

    def test_q02_name_mangling_and_hasattr(self):
        class C:
            def __init__(self):
                self._name = 1
                self.__name = 2
        obj = C()
        self.assertEqual(
            (hasattr(obj, "_name"), hasattr(obj, "__name"),
             hasattr(obj, "_C__name")), (True, False, True))
        self.assertEqual(obj.__dict__, {"_name": 1, "_C__name": 2})

    def test_q03_q05_distinct_items_shared_shadowing_principle(self):
        class C:
            def method(self):
                return "method"
        obj = C()
        self.assertEqual(obj.method(), "method")
        obj.method = "attribute"
        self.assertEqual(obj.method, "attribute")
        self.assertEqual(C.method(obj), "method")
        with self.assertRaises(TypeError):
            obj.method()
        # Same core concept, two original assessment records: no consolidation.

    def test_q04_static_vs_instance_binding_and_missing_argument(self):
        class C:
            @staticmethod
            def static():
                return "static"
            def instance(self):
                return "instance"
        obj = C()
        self.assertEqual((C.static(), obj.static(), obj.instance(), C.instance(obj)),
                         ("static", "static", "instance", "instance"))
        with self.assertRaises(TypeError):
            C.instance()
        # Exact archived call sequence absent; success and error both possible.

    def test_q06_abstract_method_subclass_instantiation(self):
        class Base(ABC):
            @abstractmethod
            def work(self):
                raise NotImplementedError
        class Incomplete(Base):
            pass
        class Complete(Base):
            def work(self):
                return 9
        with self.assertRaises(TypeError):
            Incomplete()
        self.assertEqual(Complete().work(), 9)

    def test_q07_overridden_method_runtime_dispatch(self):
        class A:
            def speak(self):
                return "A"
        class B(A):
            def speak(self):
                return "B"
        def speak(value):
            return value.speak()
        self.assertEqual((speak(A()), speak(B())), ("A", "B"))

    def test_q08_diamond_mro_depends_on_hierarchy_and_implementations(self):
        class A:
            def who(self):
                return "A"
        class B(A):
            def who(self):
                return "B"
        class C(A):
            def who(self):
                return "C"
        class D(B, C):
            pass
        class E(C, B):
            pass
        self.assertEqual((D().who(), E().who()), ("B", "C"))
        self.assertEqual(D.__mro__, (D, B, C, A, object))
        class Left(A):
            pass
        class Right(A):
            pass
        class Join(Left, Right):
            pass
        self.assertEqual(Join().who(), "A")
        # Missing original hierarchy/print expression means no unique MCQ key.

    def test_q09_base_order_controls_mro_tuple(self):
        class A:
            pass
        class B:
            pass
        class C(A, B):
            pass
        class D(B, A):
            pass
        self.assertEqual(C.__mro__, (C, A, B, object))
        self.assertEqual(D.__mro__, (D, B, A, object))

    def test_q10_super_call_changes_constructor_effects(self):
        trace = []
        class A:
            def __init__(self):
                trace.append("A")
        class B(A):
            def __init__(self):
                trace.append("B")
        class C(A):
            def __init__(self):
                super().__init__()
                trace.append("C")
        B()
        self.assertEqual(trace, ["B"])
        trace.clear()
        C()
        self.assertEqual(trace, ["A", "C"])
        # Question paraphrase does not preserve actual child __init__ implementation.

    def test_q11_shared_mutable_class_list_and_instance_rebinding(self):
        class C:
            values = []
            def __init__(self, value):
                self.values.append(value)
        left, right = C(1), C(2)
        self.assertIs(left.values, right.values)
        self.assertEqual((len(left.values), len(right.values), len(C.values)),
                         (2, 2, 2))
        right.values = [3]
        self.assertEqual((left.values, right.values, C.values), ([1, 2], [3], [1, 2]))

    def test_q12_explicit_super_class_instance_lookup(self):
        class A:
            def method(self):
                return "A"
        class B(A):
            def method(self):
                return "B"
        instance = B()
        self.assertEqual((A().method(), instance.method(),
                          super(B, instance).method()), ("A", "B", "A"))
        with self.assertRaises(TypeError):
            super(B, A())


if __name__ == "__main__":
    unittest.main(verbosity=2)
