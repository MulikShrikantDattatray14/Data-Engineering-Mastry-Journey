"""Read-only original companion source audit: mentorship PDF pp.73-74.

The harness executes four original examples against original archived inputs,
syntax-checks two OPTIONAL external-runtime examples, and uses separately
labelled synthetic boundary fixtures. No student work is graded here.
"""
from __future__ import annotations

import hashlib
import math
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
LESSONS_DIR = MASTER / '6. Python for Data Engineering'
DATA_DIR = MASTER / 'python_de_dataset'
LESSONS = {
    73: ('05. Testing and data quality.md', '05b4ff35d2666ef5908237686f2a517dd718301a', 3, 5),
    74: ('06. From pandas to PySpark and Airflow.md', '17b999bcc639f184c5ca7bac4c3a325d4d05e763', 3, 6),
}
DATA = {
    'orders.csv': '2d08d1fc6acdc4f26c4427f27ac7925bfb202ea2',
    'orders_dirty.csv': 'e36bedf1e6b9b5ef2582b007440c92ccf9fda83a',
    'customers.json': 'd6125fce237e7f7e3193667946d1eb117cd19db0',
}
FENCE = chr(96) * 3
PYTHON = re.compile(r'(?ms)^' + FENCE + r'python[ \t]*\n(.*?)^' + FENCE + r'[ \t]*$')
TEXT = re.compile(r'(?ms)^' + FENCE + r'text[ \t]*\n(.*?)^' + FENCE + r'[ \t]*$')
LINK = re.compile(r'\[▶ Run and edit this example\]\(<http://127\.0\.0\.1:8765/\?part=(\d+)&lesson=(\d+)&snippet=(\d+)>\)')


def blob_sha(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def verify_archive() -> None:
    for name, sha, _, _ in LESSONS.values():
        assert blob_sha((LESSONS_DIR / name).read_bytes()) == sha, f'Original lesson modified: {name}'
    for name, sha in DATA.items():
        assert blob_sha((DATA_DIR / name).read_bytes()) == sha, f'Original dataset modified: {name}'


def original_snippets(page: int) -> dict[int, tuple[str, str | None]]:
    name, _, count, lesson = LESSONS[page]
    raw = (LESSONS_DIR / name).read_text(encoding='utf-8')
    prompt_section = raw.split('## Your turn', 1)
    assert len(prompt_section) == 2
    prompts = re.findall(r'(?m)^\s*[123]\. ', prompt_section[1].split('## W3Schools', 1)[0])
    assert len(prompts) == 3, f'Lost original practice prompts on p.{page}'
    links = list(LINK.finditer(raw))
    assert len(links) == count, f'Wrong original snippet inventory for p.{page}'
    found = {}
    for index, link in enumerate(links, 1):
        assert tuple(map(int, link.groups())) == (6, lesson, index)
        region = raw[link.end(): links[index].start() if index < len(links) else len(raw)]
        code_blocks = list(PYTHON.finditer(region))
        assert len(code_blocks) == 1, f'Expected one Python block at p.{page} #{index}'
        code = code_blocks[0].group(1).strip('\n')
        compile(code, f'original-p{page}-snippet-{index}', 'exec')
        outputs = list(TEXT.finditer(region))
        expected = outputs[0].group(1).strip('\n') if outputs else None
        found[index] = (code, expected)
    return found


def copy_data(temp: Path) -> None:
    dest = temp / 'python_de_dataset'
    dest.mkdir()
    for name in DATA:
        shutil.copyfile(DATA_DIR / name, dest / name)


def execute_original(page: int, number: int) -> subprocess.CompletedProcess[str]:
    verify_archive()
    with tempfile.TemporaryDirectory(prefix='source-p73-74-') as dirname:
        temp = Path(dirname)
        copy_data(temp)
        if (page, number) == (73, 2):
            first = original_snippets(73)[1][0]
            (temp / 'transform.py').write_text(first + '\n', encoding='utf-8')
            script = temp / 'test_transform.py'
        else:
            script = temp / 'source_example.py'
        script.write_text(original_snippets(page)[number][0] + '\n', encoding='utf-8')
        result = subprocess.run([sys.executable, '-B', str(script)], cwd=temp,
                                capture_output=True, text=True, timeout=90, check=False,
                                env={**os.environ, 'PYTHONUNBUFFERED': '1',
                                     'PYTHONDONTWRITEBYTECODE': '1',
                                     'PYTEST_DISABLE_PLUGIN_AUTOLOAD': '1'})
        for name, sha in DATA.items():
            assert blob_sha((temp / 'python_de_dataset' / name).read_bytes()) == sha
    verify_archive()
    return result


class Pages73And74ArchiveAudit(unittest.TestCase):
    def test_source_inventory_prompt_counts_syntax_and_archive(self):
        verify_archive()
        self.assertEqual({page: len(original_snippets(page)) for page in LESSONS}, {73: 3, 74: 3})
        self.assertIsNotNone(original_snippets(73)[1][1])
        self.assertIsNotNone(original_snippets(73)[3][1])
        # Spark and Airflow have external runtime dependencies; this is static
        # source inspection, NOT a claim that the source ran in Spark/Airflow.
        spark = original_snippets(74)[2][0]
        airflow = original_snippets(74)[3][0]
        self.assertIn('F.dense_rank().over(window)', spark)
        self.assertIn('.show()', spark)
        self.assertIn('airflow.sdk', airflow)
        self.assertIn('NotImplementedError', airflow)

    def test_source_p73_transform_exact_printed_output(self):
        result = execute_original(73, 1)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(result.stderr)
        self.assertEqual(result.stdout.strip(), original_snippets(73)[1][1])

    def test_source_p73_six_pytest_cases_descriptive_contract(self):
        result = execute_original(73, 2)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertRegex(result.stdout, r'\b6 passed\b')
        self.assertNotIn('failed', result.stdout.lower())

    def test_source_p73_quality_exact_printed_output(self):
        result = execute_original(73, 3)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(result.stderr)
        self.assertEqual(result.stdout.strip(), original_snippets(73)[3][1])

    def test_source_p74_pandas_seven_row_descriptive_contract(self):
        result = execute_original(74, 1)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(result.stderr)
        rows = [r.split() for r in result.stdout.strip().splitlines()[1:]]
        self.assertEqual(rows, [[str(c), str(o), str(float(v))]
                                 for c, o, v in ((1, 114, 2397), (2, 111, 1999),
                                                 (3, 109, 747), (4, 106, 1048),
                                                 (5, 108, 3498), (6, 110, 1998),
                                                 (7, 112, 846))])

    def test_synthetic_p73_nonfinite_amount_defect(self):
        # Auditor-supplied fixture, not a source-published expected output.
        scope = {'__name__': 'auditor_test'}
        exec(compile(original_snippets(73)[1][0], 'original-transform', 'exec'), scope)
        self.assertEqual(scope['normalize_status'](' CancelED '), 'cancelled')
        self.assertEqual(scope['normalize_status'](None), 'unknown')
        self.assertEqual(scope['to_amount']('1,198.50'), 1198.5)
        for bad in ('0', '-1'):
            with self.assertRaises(ValueError):
                scope['to_amount'](bad)
        self.assertTrue(math.isnan(scope['to_amount']('NaN')))
        self.assertEqual(scope['to_amount']('Infinity'), math.inf)

    def test_synthetic_p73_empty_batch_vacuous_quality_pass(self):
        # Verify actual original check function on scratch-only DataFrames.
        import pandas as pd
        import json
        with tempfile.TemporaryDirectory(prefix='qa-fixture-') as dirname:
            temp = Path(dirname)
            copy_data(temp)
            original = original_snippets(73)[3][0]
            old = Path.cwd()
            scope = {'__name__': 'auditor_test'}
            try:
                os.chdir(temp)
                exec(compile(original, 'original-data-quality', 'exec'), scope)
            finally:
                os.chdir(old)
            empty = pd.read_csv(temp / 'python_de_dataset' / 'orders.csv').iloc[0:0]
            self.assertEqual(scope['run_checks'](empty, scope['customers']), [])
        verify_archive()

    def test_synthetic_p74_tie_and_null_partition_semantics(self):
        # Reuses exact source ranking expressions with auditor-created rows.
        import pandas as pd
        data = pd.DataFrame({
            'customer_id': [1.0, 1.0, None, 2.0],
            'order_id': [1, 2, 3, 4],
            'amount': [100.0, 100.0, 999.0, 1.0],
            'status': ['delivered'] * 4,
        })
        delivered = data.loc[data.status == 'delivered'].copy()
        delivered['rank'] = delivered.groupby('customer_id')['amount'].rank(
            method='dense', ascending=False)
        chosen = delivered.loc[delivered['rank'] == 1, 'order_id'].tolist()
        self.assertEqual(chosen, [1, 2, 4])
        self.assertTrue(math.isnan(float(delivered.loc[2, 'rank'])))


if __name__ == '__main__':
    unittest.main(verbosity=2)
