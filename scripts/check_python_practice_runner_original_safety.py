#!/usr/bin/env python3
"""Original, immutable Python mentorship practice runner: read-only audit.

Reviewer synthetic scratch probes are NOT learner attempts or a sandbox guarantee.
"""
import hashlib
import http.client
import importlib.util
import json
import sys
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCH = ROOT / "99. Reference Materials" / "Original Mastery Snapshot" / "2. Python Mastry"
PINS = {
    "practice_runner.py": "46e478f026212896440343d37443ba44fa193248",
    "Start Practice.cmd": "13da483db0d607ec766677f80313d571bbdac889",
    "requirements-practice.txt": "f6d8f15b4129386f70f03cc51d859ca7f440f411",
    "00. Start Here.md": "6ac4f64ce4e2906a3936d7886c0f2bbed1ace9fa",
    "1. Python from Zero/01. Your first Python program.md": "5fd194caa2280c436371fb94cee97f1ee4c5f5fb",
    "1. Python from Zero/19. Mini project - monthly sales report.md": "30992048e800aa0aaf8e8940546993d5b48be366",
    "python_de_dataset/orders.csv": "2d08d1fc6acdc4f26c4427f27ac7925bfb202ea2",
    "python_de_dataset/README.md": "42ba92515379976a0d1cdd42114aa64c9a1daa9e",
}

def git_sha(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

def verify_pins():
    for name, sha in PINS.items():
        actual = git_sha((ARCH / name).read_bytes())
        assert actual == sha, f"Archived source changed: {name} {actual}"

verify_pins()
spec = importlib.util.spec_from_file_location("archived_mentor_practice_runner_reviewer", ARCH / "practice_runner.py")
assert spec and spec.loader
runner = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = runner
spec.loader.exec_module(runner)

class OriginalPracticeRunnerReviewer(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        try:
            verify_pins()
        finally:
            runner.WORKSPACE.cleanup()

    def test_01_eight_immutable_original_sources(self):
        verify_pins()
        self.assertEqual(len(PINS), 8)

    def test_02_part_inventory_and_original_lessons(self):
        self.assertEqual(set(runner.PART_DIRS), set("01234567"))
        self.assertEqual(runner.lesson_files("0")["00"].name, "00. Start Here.md")
        self.assertEqual(runner.lesson_files("1")["19"].name, "19. Mini project - monthly sales report.md")
        self.assertEqual(len(runner.example("1", "19", 4)[2]), 5)
        with self.assertRaises(ValueError):
            runner.lesson_files("invalid")
        with self.assertRaises(ValueError):
            runner.example("1", "19", 999)

    def test_03_untouched_source_fences_and_filename_scope(self):
        title, blocks = runner.code_blocks(ARCH / "00. Start Here.md")
        self.assertIn("Start Here", title)
        self.assertEqual(len(blocks), 3)
        title, blocks = runner.code_blocks(ARCH / "1. Python from Zero/19. Mini project - monthly sales report.md")
        self.assertIn("monthly sales report", title.lower())
        self.assertEqual(len(blocks), 5)
        self.assertIn("def read_orders", blocks[0]["code"])
        self.assertIn("print_report(build_report(rows))", blocks[3]["code"])
        self.assertEqual(runner.named_file("# helpers.py\nx = 1\n"), "helpers.py")
        self.assertIsNone(runner.named_file("# ../bad.py\nx = 1\n"))
        self.assertIsNone(runner.named_file("print(1)"))

    def test_04_real_original_monthly_source_demo_via_runner(self):
        verify_pins()
        code = runner.example("1", "19", 4)[2][3]["code"]
        result = runner.run_example("1", "19", 4, code, "")
        self.assertEqual(result["exit_code"], 0, result["stderr"])
        self.assertFalse(result["timed_out"])
        self.assertEqual(result["stderr"], "")
        self.assertEqual(result["setup_examples"], [1, 2, 3])
        self.assertIn("15 orders read", result["stdout"])
        self.assertIn("2025-03        4   7,291.00", result["stdout"])
        self.assertIn("18,972.00", result["stdout"])
        self.assertIsNone(result["saved_file"])
        verify_pins()

    def test_05_synthetic_edited_copy_never_modifies_archive(self):
        original = ARCH / "1. Python from Zero/19. Mini project - monthly sales report.md"
        before = original.read_bytes()
        result = runner.run_example("1", "19", 1, "print('AUDITOR_ONLY')", "")
        self.assertEqual(result["exit_code"], 0, result["stderr"])
        self.assertEqual(result["stdout"], "AUDITOR_ONLY\n")
        scratch = Path(runner.WORKSPACE.name) / "1-19" / "__practice_current__.py"
        self.assertTrue(scratch.exists())
        self.assertIn("AUDITOR_ONLY", scratch.read_text(encoding="utf-8"))
        self.assertEqual(original.read_bytes(), before)
        verify_pins()

    def test_06_bounded_source_stdin_and_local_host(self):
        with self.assertRaisesRegex(ValueError, "Code is too long"):
            runner.run_example("1", "19", 1, "x" * (runner.MAX_CODE + 1), "")
        with self.assertRaisesRegex(ValueError, "Input is too long"):
            runner.run_example("1", "19", 1, "print(1)", "x" * (runner.MAX_STDIN + 1))
        self.assertEqual((runner.HOST, runner.PORT), ("127.0.0.1", 8765))

    def test_07_synthetic_timeout_and_combined_output_limit(self):
        work = Path(runner.WORKSPACE.name) / "auditor_scratch"
        work.mkdir(exist_ok=True)
        old_timeout, old_output = runner.RUN_TIMEOUT_SECONDS, runner.MAX_OUTPUT
        try:
            runner.RUN_TIMEOUT_SECONDS = 1
            timed = runner.capture([sys.executable, "-u", "-c", "while True: pass"], work, "")
            self.assertTrue(timed["timed_out"], timed)
            self.assertNotEqual(timed["exit_code"], 0)
            runner.MAX_OUTPUT = 256
            noisy = runner.capture([sys.executable, "-u", "-c", "print('x'*100000)"], work, "")
            self.assertTrue(noisy["truncated"], noisy)
            self.assertLessEqual(len(noisy["stdout"].encode()) + len(noisy["stderr"].encode()), 256)
        finally:
            runner.RUN_TIMEOUT_SECONDS, runner.MAX_OUTPUT = old_timeout, old_output
        verify_pins()

    def test_08_loopback_http_host_origin_token_checks_and_authorized_scratch(self):
        server = runner.ThreadingHTTPServer(("127.0.0.1", 0), runner.Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        def request(method, path, headers, body=None):
            conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=6)
            try:
                conn.request(method, path, body=body, headers=headers)
                response = conn.getresponse()
                return response.status, response.read()
            finally:
                conn.close()
        try:
            good_host = {"Host": "127.0.0.1:8765"}
            status, _ = request("GET", "/", {"Host": "not-local.example"})
            self.assertEqual(status, 403)
            status, page = request("GET", "/", good_host)
            self.assertEqual(status, 200)
            self.assertIn(b"Python Mastry", page)
            payload = json.dumps({"part": "1", "lesson": "19", "snippet": 1,
                                  "code": "print('AUDITOR_HTTP_ONLY')", "stdin": ""}).encode()
            headers = {**good_host, "Content-Type": "application/json"}
            status, _ = request("POST", "/api/run", headers, payload)
            self.assertEqual(status, 403)
            headers["Origin"] = runner.ORIGIN
            headers["X-Practice-Token"] = "wrong-token"
            status, _ = request("POST", "/api/run", headers, payload)
            self.assertEqual(status, 403)
            headers["X-Practice-Token"] = runner.TOKEN
            status, body = request("POST", "/api/run", headers, payload)
            self.assertEqual(status, 200, body)
            result = json.loads(body)
            self.assertEqual(result["stdout"], "AUDITOR_HTTP_ONLY\n")
            self.assertEqual(result["exit_code"], 0)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
        verify_pins()

if __name__ == "__main__":
    unittest.main(verbosity=2)
