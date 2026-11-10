"""Independently test untouched mentorship companion pp.69-72 against archived data.

Eight literal printed-output contracts, four separately labelled descriptive
contracts, and four auditor-authored synthetic boundary groups. Not learner work.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / '99. Reference Materials' / 'Original Mastery Snapshot' / '2. Python Mastry'
LESSON_DIR = MASTER / '6. Python for Data Engineering'
DATA_DIR = MASTER / 'python_de_dataset'
LESSONS = {
    69: ('01. Pandas essentials mapped to SQL.md', 'abe851ff69b8a2c83830f65813de92ee2e5c7d9a', 3, 1),
    70: ('02. Pandas pitfalls and speed.md', '71138767835da7cd6aa9eba386d14888d7704219', 4, 2),
    71: ('03. Python and databases.md', '02af93e471c9f933274981230981102c72e76d69', 3, 3),
    72: ('04. Build an idempotent ETL pipeline.md', 'fc859b44748d06318f2d0bdb4ae36266715253e7', 2, 4),
}
DATA_SHA = {
    'orders.csv': '2d08d1fc6acdc4f26c4427f27ac7925bfb202ea2',
    'order_items.csv': '072bd904c499ce5547049eb8ba0fc2dd4c071cd0',
    'products.csv': 'c5beff443efbdc3cd73376cd721334fa0bf43d8b',
    'customers.json': 'd6125fce237e7f7e3193667946d1eb117cd19db0',
    'orders_dirty.csv': 'e36bedf1e6b9b5ef2582b007440c92ccf9fda83a',
}
LINK = re.compile(r'\[▶ Run and edit this example\]\(<http://127\.0\.0\.1:8765/\?part=(\d+)&lesson=(\d+)&snippet=(\d+)>\)')
PYTHON = re.compile(r'(?ms)^' + chr(96) * 3 + r'python[ \t]*\n(.*?)^' + chr(96) * 3 + r'[ \t]*$')
TEXT = re.compile(r'(?ms)^' + chr(96) * 3 + r'text[ \t]*\n(.*?)^' + chr(96) * 3 + r'[ \t]*$')
EXACT = {(69, 3), (70, 1), (70, 2), (70, 4), (71, 1), (71, 2), (71, 3), (72, 1)}
DESCRIPTIVE = {(69, 1), (69, 2), (70, 3), (72, 2)}


def blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def verify_archive() -> None:
    for page, (name, sha, _, _) in LESSONS.items():
        assert blob_sha((LESSON_DIR / name).read_bytes()) == sha, f'Archived lesson p.{page} changed'
    for name, sha in DATA_SHA.items():
        assert blob_sha((DATA_DIR / name).read_bytes()) == sha, f'Archived input {name} changed'


def examples(page: int) -> dict[int, tuple[str, str | None]]:
    name, sha, count, lesson = LESSONS[page]
    raw = (LESSON_DIR / name).read_bytes()
    assert blob_sha(raw) == sha
    body = raw.decode('utf-8-sig')
    turns = body.split('## Your turn', 1)
    assert len(turns) == 2 and len(re.findall(r'(?m)^\s*[123]\. ', turns[1].split('## W3Schools', 1)[0])) == 3
    links = list(LINK.finditer(body))
    assert len(links) == count, f'Wrong original code link count p.{page}'
    found = {}
    for number, match in enumerate(links, 1):
        assert tuple(map(int, match.groups())) == (6, lesson, number)
        region = body[match.end(): links[number].start() if number < len(links) else len(body)]
        code_matches = list(PYTHON.finditer(region))
        assert len(code_matches) == 1, f'p.{page} snippet {number} has {len(code_matches)} code blocks'
        code = code_matches[0].group(1).strip('\n')
        compile(code, f'untouched-p{page}-{number}', 'exec')
        texts = list(TEXT.finditer(region))
        expected = texts[0].group(1).strip('\n') if (page, number) in EXACT else None
        assert (expected is not None) == ((page, number) in EXACT)
        found[number] = code, expected
    return found


def copy_inputs(folder: Path) -> None:
    target = folder / 'python_de_dataset'
    target.mkdir()
    for name in DATA_SHA:
        shutil.copyfile(DATA_DIR / name, target / name)


def run_code(code: str) -> subprocess.CompletedProcess[str]:
    verify_archive()
    with tempfile.TemporaryDirectory(prefix='mentor-p69-72-') as dirname:
        folder = Path(dirname)
        copy_inputs(folder)
        script = folder / 'unaltered_example.py'
        script.write_text(code + '\n', encoding='utf-8')
        process = subprocess.run([sys.executable, '-I', '-B', str(script)], cwd=folder,
                                 capture_output=True, text=True, timeout=60,
                                 env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}, check=False)
        for name, sha in DATA_SHA.items():
            assert blob_sha((folder / 'python_de_dataset' / name).read_bytes()) == sha
    verify_archive()
    return process


def source_namespace(page: int, snippet: int) -> dict:
    code, _ = examples(page)[snippet]
    verify_archive()
    with tempfile.TemporaryDirectory(prefix='mentor-synthetic-') as dirname:
        folder = Path(dirname)
        copy_inputs(folder)
        old = Path.cwd()
        env = {'__name__': 'auditor_original_source'}
        try:
            os.chdir(folder)
            with contextlib.redirect_stdout(io.StringIO()):
                exec(compile(code, 'untouched-example', 'exec'), env)
        finally:
            os.chdir(old)
    verify_archive()
    return env


class ArchivedMentorshipP69to72(unittest.TestCase):
    def test_archive_link_inventory_and_prompts(self):
        verify_archive()
        self.assertEqual(sum(row[2] for row in LESSONS.values()), 12)
        for page in LESSONS:
            with self.subTest(page=page):
                self.assertEqual(len(examples(page)), LESSONS[page][2])
        self.assertEqual(len(EXACT), 8)
        self.assertEqual(len(DESCRIPTIVE), 4)

    def test_eight_exact_published_output_contracts(self):
        for page, number in sorted(EXACT):
            with self.subTest(page=page, snippet=number):
                code, expected = examples(page)[number]
                result = run_code(code)
                self.assertEqual(result.returncode, 0, result.stderr)
                # Pandas 2.3 prints a SettingWithCopyWarning for the original
                # temporary-assignment demonstration; this is source behavior.
                if result.stderr and (page, number) != (70, 2):
                    self.fail(f'Unexpected stderr p.{page}#{number}: {result.stderr}')
                if (page, number) == (70, 2) and result.stderr:
                    self.assertIn('SettingWithCopyWarning', result.stderr)
                self.assertEqual(result.stdout.rstrip('\n'), expected.rstrip('\n'))

    def test_four_source_descriptive_output_contracts(self):
        for page, number in sorted(DESCRIPTIVE):
            with self.subTest(page=page, snippet=number):
                result = run_code(examples(page)[number][0])
                self.assertEqual(result.returncode, 0, result.stderr)
                stdout = result.stdout
                if (page, number) == (69, 1):
                    self.assertIn('(15, 5)', stdout)
                    self.assertIn('order_id', stdout)
                    for month, count, revenue, average in ((1, 2, '1994.0', '997.0'), (2, 2, '2847.0', '1423.5'),
                                                         (3, 4, '7291.0', '1822.8'), (4, 4, '6840.0', '1710.0')):
                        self.assertRegex(stdout, rf'(?m)^\s*2025-0{month}\s+{count}\s+{revenue}\s+{average}\s*$')
                    # Original published dtype display is version-dependent and
                    # its closing printed-output fence is malformed.
                elif (page, number) == (69, 2):
                    for category, values in {'Electronics': [799, 1499, 5096, 4396],
                                             'Home': [399, 1199, 1199, 1997],
                                             'Stationery': [796, 149, 996, 447]}.items():
                        self.assertRegex(stdout, rf'(?m)^\s*{category}\s+' + r'\s+'.join(map(str, values)) + r'\s*$')
                elif (page, number) == (70, 3):
                    for method in ('vectorized', 'apply', 'iterrows'):
                        self.assertRegex(stdout, rf'(?m)^{method} rows: 5000 milliseconds:')
                    numbers = re.findall(r'(?:text|category) KB: (\d+)', stdout)
                    self.assertEqual(len(numbers), 2)
                    self.assertLess(int(numbers[1]), int(numbers[0]))
                else:
                    self.assertEqual(stdout.strip(), 'bad arguments, exit code 2')
                    self.assertIn('--date', result.stderr)

    def test_synthetic_p69_merge_duplicate_and_group_totals(self):
        scope = source_namespace(69, 2)
        import pandas as pd
        duplicates = pd.concat([scope['products'], scope['products'].iloc[[0]]], ignore_index=True)
        with self.assertRaises(pd.errors.MergeError):
            scope['items'].merge(duplicates, on='product_id', how='left', validate='many_to_one')
        self.assertEqual(len(scope['orders']), 15)

    def test_synthetic_p70_null_group_and_dirty_input(self):
        scope = source_namespace(70, 1)
        joined = scope['joined']
        self.assertEqual(float(joined['amount'].sum()), 23268.0)
        self.assertEqual(float(joined.groupby('address.city')['amount'].sum().sum()), 21270.0)
        self.assertEqual(float(joined.groupby('address.city', dropna=False)['amount'].sum().sum()), 23268.0)
        dirty = source_namespace(70, 4)['dirty']
        self.assertEqual(len(dirty), 7)
        self.assertEqual(int(dirty['customer_id'].isna().sum()), 1)

    def test_synthetic_p71_sql_parameter_and_rollback(self):
        scope = source_namespace(71, 1)
        conn = scope['connection']
        self.assertEqual(conn.execute('SELECT COUNT(*) FROM orders WHERE status=?',
                                      ("x' OR '1'='1",)).fetchone()[0], 0)
        self.assertEqual(conn.execute('SELECT COUNT(*) FROM orders').fetchone()[0], 15)
        scope = source_namespace(71, 2)
        self.assertEqual(scope['connection'].execute('SELECT status FROM orders WHERE order_id=101').fetchone()[0], 'delivered')

    def test_synthetic_p72_rerun_replacement_and_atomic_failure(self):
        scope = source_namespace(72, 1)
        conn = scope['connection']
        load = scope['load']
        day = '2025-04-20'
        self.assertEqual(load(conn, day, [(114, 1, day, 'delivered', 1.25)]), 1)
        self.assertEqual(load(conn, day, [(114, 1, day, 'returned', 2.50)]), 1)
        self.assertEqual(conn.execute('SELECT amount FROM fact_orders WHERE order_id=114').fetchone()[0], 2.5)
        import sqlite3
        with self.assertRaises(sqlite3.IntegrityError):
            load(conn, day, [(114, 1, day, 'bad', 5), (114, 1, day, 'bad', 6)])
        self.assertEqual(conn.execute('SELECT amount FROM fact_orders WHERE order_id=114').fetchone()[0], 2.5)
        self.assertEqual(conn.execute('SELECT COUNT(*) FROM fact_orders').fetchone()[0], 2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
