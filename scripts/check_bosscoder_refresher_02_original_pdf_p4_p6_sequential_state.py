#!/usr/bin/env python3
"""Independent PDF-page 4-6 transcription boundary checks for Refresher 2.

Reviewer-authored execution reconstructed from learner-owned original PDF
SHA256 09ba1141054463b6eac814da13eaa0c401822298eded114fe831d89d5a3ff010.
The PDF is NOT in the public repo/CI: recorded printed outputs were inspected
against original rendered pages before writing this reviewer. Do not interpret
the checks as Academy notebook-state reconstruction, grading or mastery.
"""
import unittest

PDF_SHA256 = "09ba1141054463b6eac814da13eaa0c401822298eded114fe831d89d5a3ff010"
# Manually read from the original rendered PDF page 4 / page 5.
VISIBLE_LIST_OUTPUTS = {
    "append": ["apple", "banana", "cherry", "date"],
    "insert": ["apple", "banana", "banana", "banana", "cherry", "date"],
    "remove": ["apple", "banana", "banana", "cherry", "date"],
    "pop_result": "banana",
    "pop_remaining": ["apple", "banana", "cherry", "date"],
    "clear": [],
    "extend": ["apple", "banana", "cherry", "fig", "grape"],
}

def reviewer_sequential_p4_p5():
    """Apply only the visible fruit-list operations in page order."""
    fruits = ["apple", "banana", "cherry"]
    outcomes = {}
    fruits.append("date")
    outcomes["append"] = fruits.copy()
    fruits.insert(1, "banana")
    outcomes["insert"] = fruits.copy()
    fruits.remove("banana")
    outcomes["remove"] = fruits.copy()
    outcomes["pop_result"] = fruits.pop(1)
    outcomes["pop_remaining"] = fruits.copy()
    fruits.clear()
    outcomes["clear"] = fruits.copy()
    # The PDF uses a distinct singular variable 'fruit' for count();
    # that cell does not repopulate the plural 'fruits'.
    fruit = ["apple", "banana", "cherry"]
    outcomes["count_apple"] = fruit.count("apple")
    fruits.extend(["fig", "grape"])
    outcomes["extend"] = fruits.copy()
    return outcomes

class OriginalPdfVisibleCells(unittest.TestCase):
    def test_p4_p5_sequence_four_visible_disagreements(self):
        actual = reviewer_sequential_p4_p5()
        self.assertEqual(set(VISIBLE_LIST_OUTPUTS), set(actual) - {"count_apple"})
        mismatch = [name for name, display in VISIBLE_LIST_OUTPUTS.items()
                    if display != actual[name]]
        # Only the four lists differ; the returned pop value still matches.
        self.assertEqual(mismatch, ["insert", "remove", "pop_remaining", "extend"])

    def test_p4_append_clear_and_pop_value_reconcile(self):
        actual = reviewer_sequential_p4_p5()
        for name in ("append", "pop_result", "clear"):
            with self.subTest(cell=name):
                self.assertEqual(actual[name], VISIBLE_LIST_OUTPUTS[name])

    def test_p4_insert_expected_vs_pdf_display(self):
        self.assertEqual(reviewer_sequential_p4_p5()["insert"],
                         ["apple", "banana", "banana", "cherry", "date"])
        self.assertNotEqual(reviewer_sequential_p4_p5()["insert"],
                            VISIBLE_LIST_OUTPUTS["insert"])

    def test_p4_remove_expected_vs_pdf_display(self):
        self.assertEqual(reviewer_sequential_p4_p5()["remove"],
                         ["apple", "banana", "cherry", "date"])
        self.assertNotEqual(reviewer_sequential_p4_p5()["remove"],
                            VISIBLE_LIST_OUTPUTS["remove"])

    def test_p4_pop_expected_list_and_separate_return(self):
        replay = reviewer_sequential_p4_p5()
        self.assertEqual(replay["pop_result"], "banana")
        self.assertEqual(replay["pop_remaining"], ["apple", "cherry", "date"])
        self.assertNotEqual(replay["pop_remaining"], VISIBLE_LIST_OUTPUTS["pop_remaining"])

    def test_p5_clear_then_extend_requires_reinitialized_state(self):
        replay = reviewer_sequential_p4_p5()
        self.assertEqual(replay["clear"], [])
        self.assertEqual(replay["count_apple"], 1)
        self.assertEqual(replay["extend"], ["fig", "grape"])
        self.assertNotEqual(replay["extend"], VISIBLE_LIST_OUTPUTS["extend"])

    def test_p4_number_sort_reverse_independent_correctness(self):
        numbers = [5, 2, 9, 1]
        numbers.sort()
        self.assertEqual(numbers, [1, 2, 5, 9])
        numbers.reverse()
        self.assertEqual(numbers, [9, 5, 2, 1])

    def test_p5_string_operations_source_outputs(self):
        self.assertEqual("Hello" + " " + "World", "Hello World")
        self.assertEqual("Hi! " * 3, "Hi! Hi! Hi! ")
        phrase = "Python Programming"
        self.assertTrue("Python" in phrase)
        self.assertTrue("Java" not in phrase)

    def test_p6_character_iteration_trailing_space(self):
        # print(ch, end=" ") creates a final blank but no final newline.
        result = "".join(ch + " " for ch in "Alice")
        self.assertEqual(result, "A l i c e ")
        self.assertFalse(result.endswith("\n"))

    def test_p6_six_interactive_expression_display_values(self):
        # Original Colab expression cells display repr(value), not print().
        actual = [
            repr(len("Hello")),
            repr("Hello".lower()),
            repr("Hello".upper()),
            repr("Hello     ".strip()),
            repr("Hello, World!".replace("World", "Python")),
            repr("Hello, World!".split(", ")),
        ]
        self.assertEqual(actual, [
            "5", "'hello'", "'HELLO'", "'Hello'",
            "'Hello, Python!'", "['Hello', 'World!']",
        ])

if __name__ == "__main__":
    unittest.main(verbosity=2)
