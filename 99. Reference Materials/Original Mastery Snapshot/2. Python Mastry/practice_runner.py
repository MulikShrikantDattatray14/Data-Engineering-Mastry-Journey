#!/usr/bin/env python3
"""Offline, local practice runner for all seven parts of Python Mastry."""

from __future__ import annotations

import hashlib
import html
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parent
PART_DIRS = {
    "0": ROOT,
    "1": ROOT / "1. Python from Zero",
    "2": ROOT / "2. Python Foundations",
    "3": ROOT / "3. Advanced Python",
    "4": ROOT / "4. DSA and Complexity",
    "5": ROOT / "5. Coding Round Patterns",
    "6": ROOT / "6. Python for Data Engineering",
    "7": ROOT / "7. Practice Prep Flow and Revision",
}
DATASET_DIR = ROOT / "python_de_dataset"
HOST = "127.0.0.1"
PORT = 8765
ORIGIN = f"http://{HOST}:{PORT}"
TOKEN = secrets.token_urlsafe(32)
MAX_REQUEST = 100_000
MAX_CODE = 50_000
MAX_STDIN = 10_000
MAX_OUTPUT = 65_536
RUN_TIMEOUT_SECONDS = 8
WORKSPACE = tempfile.TemporaryDirectory(prefix="python_mastry_practice_")
RUN_LOCK = threading.Lock()

# These lessons build an example across several code blocks. They are appended
# as setup only in the temporary runnable copy, never in the lesson Markdown.
AUTO_SETUP = {
    "04": {3: (2,)},
    "15": {5: (3, 4)},
    "18": {2: (1,), 4: (1,), 6: (1,)},
    "19": {4: (1, 2, 3), 5: (2,)},
}

FENCE_OPEN = re.compile(
    r"^ {0,3}(" + re.escape(chr(96)) + r"{3,}|~{3,})python[ \t]*$",
    re.IGNORECASE,
)
FILE_LABEL = re.compile(r"^\s*#\s*([A-Za-z_][A-Za-z_0-9]*\.py)\s*$")
LESSON_NAME = re.compile(r"^([0-9]{2})\. .+\.md$")


def lesson_files(part: str = "1") -> dict[str, Path]:
    directory = PART_DIRS.get(part)
    if directory is None:
        raise ValueError("Unknown part")
    return {
        path.name[:2]: path
        for path in directory.glob("*.md")
        if LESSON_NAME.fullmatch(path.name)
    }


def code_blocks(path: Path) -> tuple[str, list[dict[str, str]]]:
    """Read fenced Python examples, including both tilde and backtick fences."""
    title = path.stem
    heading = title
    blocks: list[dict[str, str]] = []
    current: list[str] | None = None
    fence = ""
    for line in path.read_text(encoding="utf-8").splitlines():
        if current is None:
            if line.startswith("# "):
                title = line[2:].strip()
                heading = title
            elif line.startswith(("## ", "### ")):
                heading = line.lstrip("# ").strip()
            match = FENCE_OPEN.fullmatch(line)
            if match:
                fence = match.group(1)
                current = []
        elif re.fullmatch(
            r" {0,3}" + re.escape(fence[0]) + "{" + str(len(fence)) + r",}[ \t]*",
            line,
        ):
            code = "\n".join(current).rstrip() + "\n"
            blocks.append({"code": code, "heading": heading})
            current = None
            fence = ""
        else:
            current.append(line)
    return title, blocks


def example(part: str, lesson: str, snippet: int) -> tuple[Path, str, list[dict[str, str]]]:
    path = lesson_files(part).get(lesson)
    if path is None:
        raise ValueError("Unknown lesson")
    title, blocks = code_blocks(path)
    if snippet < 1 or snippet > len(blocks):
        raise ValueError("Unknown code example")
    return path, title, blocks


def named_file(code: str) -> str | None:
    first_line = code.splitlines()[0] if code.splitlines() else ""
    match = FILE_LABEL.fullmatch(first_line)
    return match.group(1) if match else None


def practice_directory(part: str, lesson: str) -> Path:
    directory = Path(WORKSPACE.name) / f"{part}-{lesson}"
    if not directory.exists():
        directory.mkdir(parents=True)
        if DATASET_DIR.is_dir():
            shutil.copytree(DATASET_DIR, directory / "python_de_dataset")
    return directory


def prepare_named_files(blocks: list[dict[str, str]], snippet: int, directory: Path) -> None:
    """Provide earlier helpers.py/tool.py examples to multi-file examples."""
    for block in blocks[: snippet - 1]:
        filename = named_file(block["code"])
        if filename:
            target = directory / filename
            if not target.exists():
                target.write_text(block["code"], encoding="utf-8")


def capture(command: list[str], directory: Path, user_input: str) -> dict[str, object]:
    """Run one isolated Python process with a time and combined-output limit."""
    environment = os.environ.copy()
    environment["PYTHONIOENCODING"] = "utf-8"
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    started = time.monotonic()
    process = subprocess.Popen(
        command,
        cwd=directory,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=environment,
    )
    stdout_chunks: list[bytes] = []
    stderr_chunks: list[bytes] = []
    total = 0
    truncated = False
    output_lock = threading.Lock()

    def drain(pipe, chunks: list[bytes]) -> None:
        nonlocal total, truncated
        try:
            while True:
                piece = pipe.read(4096)
                if not piece:
                    return
                with output_lock:
                    remaining = MAX_OUTPUT - total
                    if remaining > 0:
                        chunks.append(piece[:remaining])
                    total += len(piece)
                    if total > MAX_OUTPUT:
                        truncated = True
                if truncated:
                    try:
                        process.kill()
                    except OSError:
                        pass
                    return
        finally:
            pipe.close()

    stdout_thread = threading.Thread(target=drain, args=(process.stdout, stdout_chunks), daemon=True)
    stderr_thread = threading.Thread(target=drain, args=(process.stderr, stderr_chunks), daemon=True)
    stdout_thread.start()
    stderr_thread.start()
    # A child that does not read stdin can fill the OS pipe. Write on a
    # separate daemon thread so the process timeout still applies.
    def send_input() -> None:
        try:
            process.stdin.write(user_input.encode("utf-8"))
            process.stdin.close()
        except (BrokenPipeError, OSError, ValueError):
            pass

    input_thread = threading.Thread(target=send_input, daemon=True)
    input_thread.start()
    timed_out = False
    try:
        process.wait(timeout=RUN_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        timed_out = True
        process.kill()
        process.wait()
    input_thread.join(timeout=2)
    stdout_thread.join(timeout=2)
    stderr_thread.join(timeout=2)
    return {
        "stdout": b"".join(stdout_chunks).decode("utf-8", errors="replace"),
        "stderr": b"".join(stderr_chunks).decode("utf-8", errors="replace"),
        "exit_code": process.returncode,
        "timed_out": timed_out,
        "truncated": truncated,
        "seconds": round(time.monotonic() - started, 2),
    }


def run_example(part: str, lesson: str, snippet: int, edited_code: str, user_input: str) -> dict[str, object]:
    if len(edited_code) > MAX_CODE:
        raise ValueError("Code is too long")
    if len(user_input) > MAX_STDIN:
        raise ValueError("Input is too long")
    _path, _title, blocks = example(part, lesson, snippet)
    with RUN_LOCK:
        directory = practice_directory(part, lesson)
        prepare_named_files(blocks, snippet, directory)
        filename = named_file(edited_code)
        if filename:
            script = directory / filename
            source = edited_code
        else:
            script = directory / "__practice_current__.py"
            prerequisites = AUTO_SETUP.get(lesson, {}).get(snippet, ()) if part == "1" else ()
            if part == "1" and lesson == "04" and snippet == 3:
                # Only the earlier status assignment is needed; avoid replaying
                # its unrelated print statements in this example's output.
                source = 'status = "  Delivered  "\n\n'
            else:
                source = "\n\n".join(blocks[number - 1]["code"] for number in prerequisites)
                if source:
                    source += "\n\n"
            source += edited_code
        script.write_text(source, encoding="utf-8")
        result = capture([sys.executable, "-u", str(script)], directory, user_input)
        result["saved_file"] = filename
        result["setup_examples"] = list(AUTO_SETUP.get(lesson, {}).get(snippet, ())) if part == "1" else []
        return result


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="practice-token" content="__TOKEN__">
<title>Python Mastry · Run and edit</title>
<style>
:root { color-scheme: light; font-family: system-ui, -apple-system, "Segoe UI", sans-serif; }
* { box-sizing: border-box; }
body { margin: 0; background: #f3f6fc; color: #152540; }
header { background: #142b51; color: white; padding: 1.2rem max(1.2rem, calc((100vw - 1250px)/2)); }
header p { color: #b7d1fd; margin: .35rem 0 0; }
main { max-width: 1250px; margin: 1.6rem auto; padding: 0 1rem 2rem; }
.meta { display: flex; justify-content: space-between; gap: 1rem; align-items: end; flex-wrap: wrap; }
.meta h1 { margin: 0 0 .35rem; font-size: 1.5rem; }
.meta p { margin: 0; color: #526580; }
.controls { display: flex; flex-wrap: wrap; gap: .55rem; align-items: center; margin: 1.2rem 0; }
button { border: 1px solid #b5c3d9; background: white; color: #193455; padding: .65rem .9rem; border-radius: .55rem; cursor: pointer; font-weight: 600; }
button:hover { background: #e8f0fe; }
button:disabled { opacity: .5; cursor: default; }
button.primary { background: #175bd5; border-color: #175bd5; color: white; }
button.primary:hover { background: #114dbb; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.panel { background: white; border: 1px solid #d9e2f0; border-radius: .75rem; overflow: hidden; box-shadow: 0 2px 10px #1830500b; }
.panel h2 { margin: 0; padding: .9rem 1rem; background: #e9eff9; font-size: 1rem; }
.panel p { margin: .65rem 1rem; color: #526580; font-size: .9rem; }
pre, textarea { margin: 0; width: 100%; min-height: 270px; padding: 1rem; border: 0; color: #152540; background: white; font: 14px/1.55 Consolas, "Cascadia Code", monospace; overflow: auto; white-space: pre; tab-size: 4; }
textarea { resize: vertical; outline: none; border-top: 1px solid #e2e8f3; }
textarea:focus { box-shadow: inset 0 0 0 2px #77aaff; }
#input { min-height: 85px; }
#output, #errors { min-height: 110px; white-space: pre-wrap; overflow-wrap: anywhere; }
#errors { color: #9b2121; }
.note { margin: 1rem 0; padding: .8rem 1rem; background: #e8f3ff; border-left: 4px solid #3675ce; border-radius: .3rem; }
.small { font-size: .9rem; color: #526580; }
@media (max-width: 800px) { .grid { grid-template-columns: 1fr; } }
</style>
</head>
<body>
<header>
<strong>Python Mastry · Practice</strong>
<p>Run and change an editable copy. Your lesson's original code stays untouched.</p>
</header>
<main>
<div class="meta">
<div><h1 id="title">Loading example…</h1><p id="source"></p></div>
<div class="small" id="progress"></div>
</div>
<div class="controls">
<button id="prev" type="button">← Previous example</button>
<button id="next" type="button">Next example →</button>
<button id="run" class="primary" type="button">▶ Run code</button>
<button id="reset" type="button">Restore original</button>
<span class="small" id="draft-status"></span>
</div>
<div class="grid">
<section class="panel"><h2>Original lesson code</h2><p>Read only. Running or editing never changes this text.</p><pre id="original"></pre></section>
<section class="panel"><h2>Your editable copy</h2><p>Your changes are saved separately for this example in this browser.</p><textarea id="editor" spellcheck="false" aria-label="Editable Python code"></textarea></section>
</div>
<div class="note">Examples with <code>input()</code>: type one answer per line below. Some examples deliberately raise an error; the traceback is the expected result. Examples that build on earlier code receive that setup automatically where noted.</div>
<section class="panel"><h2>Answers for input() (optional)</h2><textarea id="input" spellcheck="false" aria-label="Input for Python program" placeholder="One answer per line"></textarea></section>
<div class="grid" style="margin-top: 1rem">
<section class="panel"><h2>Output</h2><pre id="output" aria-live="polite">Run the code to see its output.</pre></section>
<section class="panel"><h2>Errors and traceback</h2><pre id="errors" aria-live="polite"></pre></section>
</div>
<p class="small" id="run-status"></p>
</main>
<script>
"use strict";
const token = document.querySelector('meta[name="practice-token"]').content;
const query = new URLSearchParams(location.search);
const part = query.get("part") || "1";
const lesson = query.get("lesson") || "01";
const snippet = Number(query.get("snippet") || "1");
const el = (id) => document.getElementById(id);
let original = "";
let draftKey = "";
let inputKey = "";
let count = 0;
let sourceHash = "";

function goTo(number) {
  if (number < 1 || number > count) return;
  const target = new URL(location.href);
  target.searchParams.set("part", part);
  target.searchParams.set("lesson", lesson);
  target.searchParams.set("snippet", String(number));
  location.href = target.href;
}

async function loadExample() {
  try {
    const response = await fetch("/api/snippet?part=" + encodeURIComponent(part)
      + "&lesson=" + encodeURIComponent(lesson)
      + "&snippet=" + encodeURIComponent(snippet));
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Could not load the example.");
    original = data.code;
    sourceHash = data.source_hash;
    count = data.count;
    const lessonKey = part === "1" ? lesson : part + ":" + lesson;
    draftKey = "python-mastry-draft:" + lessonKey + ":" + snippet;
    inputKey = "python-mastry-input:" + lessonKey + ":" + snippet;
    el("title").textContent = data.heading;
    el("source").textContent = data.lesson_title + " · " + data.source;
    el("progress").textContent = "Example " + snippet + " of " + count;
    el("original").textContent = original;
    let saved = null;
    try { saved = JSON.parse(localStorage.getItem(draftKey)); } catch (_) {}
    el("editor").value = saved && typeof saved.code === "string" ? saved.code : original;
    el("input").value = localStorage.getItem(inputKey) || "";
    el("draft-status").textContent = saved ? "Your draft restored." : "Original loaded into editor.";
    if (saved && saved.source_hash !== data.source_hash) {
      el("draft-status").textContent = "Original changed since your draft; your draft is preserved.";
    }
    el("prev").disabled = snippet <= 1;
    el("next").disabled = snippet >= count;
    if (data.setup_examples.length) {
      el("run-status").textContent = "Setup from earlier example(s) "
        + data.setup_examples.join(", ") + " will run first.";
    }
  } catch (error) {
    el("title").textContent = "Example unavailable";
    el("output").textContent = String(error);
    el("run").disabled = true;
    el("reset").disabled = true;
    el("prev").disabled = true;
    el("next").disabled = true;
  }
}

el("editor").addEventListener("input", () => {
  localStorage.setItem(draftKey, JSON.stringify({
    code: el("editor").value,
    source_hash: sourceHash
  }));
  el("draft-status").textContent = "Draft saved in this browser.";
});
el("editor").addEventListener("keydown", (event) => {
  if (event.key === "Tab") {
    event.preventDefault();
    const editor = el("editor");
    const start = editor.selectionStart;
    const end = editor.selectionEnd;
    editor.value = editor.value.slice(0, start) + "    " + editor.value.slice(end);
    editor.selectionStart = editor.selectionEnd = start + 4;
    editor.dispatchEvent(new Event("input"));
  }
});
el("input").addEventListener("input", () => {
  localStorage.setItem(inputKey, el("input").value);
});
el("prev").addEventListener("click", () => goTo(snippet - 1));
el("next").addEventListener("click", () => goTo(snippet + 1));
el("reset").addEventListener("click", () => {
  localStorage.removeItem(draftKey);
  el("editor").value = original;
  el("draft-status").textContent = "Original restored in editor. Lesson file unchanged.";
});
el("run").addEventListener("click", async () => {
  el("run").disabled = true;
  el("output").textContent = "Running…";
  el("errors").textContent = "";
  el("run-status").textContent = "";
  try {
    const response = await fetch("/api/run", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Practice-Token": token },
      body: JSON.stringify({
        part: part, lesson: lesson, snippet: snippet,
        code: el("editor").value, stdin: el("input").value
      })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Run failed.");
    el("output").textContent = data.stdout ||
      (data.saved_file ? "Saved " + data.saved_file + " in the temporary practice workspace." :
      "(No printed output. This example may only define a value or function.)");
    el("errors").textContent = data.stderr || "";
    let status = "Exit code " + data.exit_code + " · " + data.seconds + " s";
    if (data.timed_out) status += " · Stopped after the time limit";
    if (data.truncated) status += " · Output limit reached";
    if (data.setup_examples.length) status += " · Used setup examples " + data.setup_examples.join(", ");
    el("run-status").textContent = status;
  } catch (error) {
    el("output").textContent = "";
    el("errors").textContent = String(error);
  } finally {
    el("run").disabled = false;
  }
});
loadExample();
</script>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        print("%s - %s" % (self.address_string(), format % args))

    def allowed_host(self) -> bool:
        return self.headers.get("Host") == f"{HOST}:{PORT}"

    def send_data(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, status: int, payload: dict[str, object]) -> None:
        self.send_data(status, json.dumps(payload).encode("utf-8"), "application/json; charset=utf-8")

    def do_GET(self) -> None:
        if not self.allowed_host():
            self.send_json(403, {"error": "Invalid local host."})
            return
        url = urlsplit(self.path)
        if url.path == "/favicon.ico":
            self.send_data(204, b"", "image/x-icon")
            return
        if url.path == "/":
            page = PAGE.replace("__TOKEN__", html.escape(TOKEN, quote=True))
            self.send_data(200, page.encode("utf-8"), "text/html; charset=utf-8")
            return
        if url.path == "/api/snippet":
            params = parse_qs(url.query)
            part = params.get("part", ["1"])[0]
            lesson = params.get("lesson", [""])[0]
            try:
                snippet = int(params.get("snippet", [""])[0])
                path, title, blocks = example(part, lesson, snippet)
                block = blocks[snippet - 1]
                self.send_json(200, {
                    "part": part,
                    "lesson": lesson,
                    "snippet": snippet,
                    "count": len(blocks),
                    "lesson_title": title,
                    "heading": block["heading"],
                    "source": path.name,
                    "code": block["code"],
                    "source_hash": hashlib.sha256(block["code"].encode("utf-8")).hexdigest(),
                    "setup_examples": list(AUTO_SETUP.get(lesson, {}).get(snippet, ())),
                })
            except (ValueError, IndexError):
                self.send_json(404, {"error": "Lesson or example not found."})
            return
        self.send_json(404, {"error": "Not found."})

    def do_POST(self) -> None:
        if not self.allowed_host() or self.headers.get("Origin") != ORIGIN:
            self.send_json(403, {"error": "Only this local practice page can run code."})
            return
        if self.headers.get("X-Practice-Token") != TOKEN:
            self.send_json(403, {"error": "Practice session token is missing or invalid."})
            return
        if urlsplit(self.path).path != "/api/run":
            self.send_json(404, {"error": "Not found."})
            return
        if self.headers.get_content_type() != "application/json":
            self.send_json(415, {"error": "Expected JSON."})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_REQUEST:
                raise ValueError("Request is too large or empty")
            payload = json.loads(self.rfile.read(length))
            part = payload.get("part", "1")
            lesson = payload["lesson"]
            snippet = payload["snippet"]
            code = payload["code"]
            user_input = payload.get("stdin", "")
            if not isinstance(part, str) or not isinstance(lesson, str) or not isinstance(snippet, int):
                raise ValueError("Invalid example")
            if not isinstance(code, str) or not isinstance(user_input, str):
                raise ValueError("Code and input must be text")
            result = run_example(part, lesson, snippet, code, user_input)
            self.send_json(200, result)
        except (KeyError, ValueError, TypeError, json.JSONDecodeError) as error:
            self.send_json(400, {"error": str(error)})
        except Exception as error:
            self.send_json(500, {"error": f"Runner error: {error}"})


def main() -> None:
    try:
        server = ThreadingHTTPServer((HOST, PORT), Handler)
    except OSError as error:
        print(f"Could not start practice runner on {ORIGIN}: {error}", file=sys.stderr)
        print("Close any previous practice runner and try again.", file=sys.stderr)
        raise SystemExit(1)
    print(f"Python practice is ready: {ORIGIN}/?lesson=01&snippet=1")
    print("Keep this window open while practising. Press Ctrl+C to stop.")
    if "--no-browser" not in sys.argv:
        threading.Timer(0.6, lambda: webbrowser.open(f"{ORIGIN}/?lesson=01&snippet=1")).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        WORKSPACE.cleanup()
        print("Practice runner stopped.")


if __name__ == "__main__":
    main()
