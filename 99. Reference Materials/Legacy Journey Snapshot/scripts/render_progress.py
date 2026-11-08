#!/usr/bin/env python3
"""Render verified learning progress; run: python scripts/render_progress.py"""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
data = json.loads((root / "progress/daily-progress.json").read_text())
days = data["daily"]
base = data["baseline"]

def bar(value, width=12):
    filled = max(0, min(width, round(value * width)))
    return "█" * filled + "░" * (width - filled)

def score(d):
    s, p = d["sql"], d["python"]
    if not set(s["completed_ids"]) <= set(s["source_ids"]):
        raise ValueError("Invalid completed SQL IDs")
    if not set(p["completed_pages"]) <= set(p["pdf_pages"]):
        raise ValueError("Invalid completed PDF pages")
    sq = len(set(s["completed_ids"])) / len(s["source_ids"]) if s["source_ids"] else float(s["applied_task_done"])
    py = len(set(p["completed_pages"])) / len(p["pdf_pages"]) if p["pdf_pages"] else float(p["applied_task_done"])
    a = (sq + float(s["guided_reviewed"])) / 2
    b = (py + float(p["guided_reviewed"])) / 2
    return (a+b)/2, a, b

assert len(days) == 157
assert days[0]["date"] == "2026-11-06"
assert days[1]["date"] == "2026-11-07"
assert [d["day"] for d in days] == list(range(1,158))
ids = [x for d in days for x in d["sql"]["source_ids"]]
pages = [x for d in days for x in d["python"]["pdf_pages"]]
assert len(ids) == len(set(ids)) == 185
assert set(pages) == set(range(1,81))
scores = [score(d) for d in days]
wins = sum(s[0] == 1 and d["reflection_completed"] for d,s in zip(days,scores))
pct = sum(s[0] for s in scores) / len(days)
sql_done = base["sql_previously_solved"] + sum(len(set(d["sql"]["completed_ids"])) for d in days)
pdf_done = sum(len(set(d["python"]["completed_pages"])) for d in days)
sql_pct = sql_done / base["sql_source_total"]
pdf_pct = pdf_done / base["python_pdf_total_pages"]
sql_h = sum(d["focus_minutes"]["sql"] for d in days)/60
py_h = sum(d["focus_minutes"]["python"] for d in days)/60

out = [
"# Data Engineering — Daily Wins Dashboard", "",
"> **Progress is earned, not assumed.** Scheduled dates and time spent alone do not count as learning completed.", "",
"## Overall progress", "",
f"**Six-month objectives:** {bar(pct)} **{pct*100:.1f}%**", "",
f"**Daily wins:** {wins}/{len(days)}", "",
f"**SQL source bank:** {bar(sql_pct)} **{sql_done}/205** — includes {base['sql_previously_solved']} previously solved questions", "",
f"**Python PDF:** {bar(pdf_pct)} **{pdf_done}/80 pages**", "",
f"**Actually logged focused learning:** SQL {sql_h:.1f}h · Python {py_h:.1f}h (daily 10h is a target, not proof of learning)", "",
"**Daily score:** 25% SQL source task + 25% reviewed SQL learning + 25% Python source task + 25% reviewed Python learning. For days with multiple questions or pages, credit is proportional. After original material finishes, source-task credit comes from the day's applied assignment. An official **daily win** additionally requires the learning reflection.", "",
"[Daily integrated timetable](INTEGRATED-10H-DAILY-PLAN.md) · [205 question inventory](SQL-SOURCE-INVENTORY.md) · [80-page Python index](PYTHON-PDF-COVERAGE.md) · [Progress data](progress/daily-progress.json)", "",
"## Weekly performance", "",
"| Week | Dates | Learning objectives | Daily wins |",
"|---|---|---|---|"
]
for week in range(26):
    ds = days[1+week*6:1+week*6+6]
    ss = scores[1+week*6:1+week*6+6]
    p = sum(s[0] for s in ss)/6
    w = sum(s[0]==1 and d["reflection_completed"] for d,s in zip(ds,ss))
    out.append(f"| {week+1:02d} | {ds[0]['date']} to {ds[-1]['date']} | {bar(p,8)} {p*100:.0f}% | {w}/6 |")
out += [
    "", "## Day 1 — 2026-11-06 · Verified kickoff practice", "",
    "**SQL tutor questions reviewed:** 7 (Q1–Q7). **Independently correct/corrected:** 3 (Q1, Q2, Q7).",
    "**PNP source questions newly completed:** 0 verified. **Python PDF pages:** 0 verified. **Actual focused minutes:** not recorded.",
    "**Learning:** SQL-R001 through SQL-R006; ON vs WHERE, NULL logic, anti-joins, and submission review.",
    "[Full Nov 6 study archive](10-learning-journal/sessions/2026-11-06/slot-01-sql.md) · [Q7 closing checkpoint](10-learning-journal/sessions/2026-11-06/Q7-CLOSED.md) · [SQL new-learning bank](01-sql/revision/LEARNED-RULES-AND-SYNTAX.md)",
    "", "## Daily progress bars", "", "The November 6 kickoff is Day 1; the original 156-day curriculum continues from November 7 as Days 2–157.", "",
]
kickoff = days[0]
out += [
    "<details><summary>Day 1 kickoff: 2026-11-06</summary>", "",
    "| Day | Date | SQL source | Python source | Guided practice | Result |",
    "|---:|---|---|---|---|---|",
    f"| 001 | {kickoff['date']} | 0 newly verified PNP IDs | 0 verified PDF pages | 7 reviewed tutor questions · 3 independently correct/corrected | Kickoff documented; daily win not earned |",
    "", "</details>", ""
]
for week in range(26):
    ds = days[week*6:week*6+6]
    ss = scores[week*6:week*6+6]
    out += [f"<details><summary>Week {week+1:02d}: {ds[0]['date']} – {ds[-1]['date']}</summary>", "", "| Day | Date | SQL | Python | Combined | Result |", "|---:|---|---|---|---|---|"]
    for d,s in zip(ds,ss):
        label = "🏆 Win" if s[0]==1 and d["reflection_completed"] else ("In progress" if s[0]>0 else "Not started")
        out.append(f"| {d['day']:03d} | {d['date']} | {bar(s[1],6)} {s[1]*100:.0f}% | {bar(s[2],6)} {s[2]*100:.0f}% | {bar(s[0],8)} **{s[0]*100:.0f}%** | {label} |")
    out += ["", "</details>", ""]
out += [
"## How to record a daily win", "",
"1. Complete and review that day's source SQL question IDs or applied SQL assignment.",
"2. Practice the assigned PDF pages and their original exercises, or complete the applied Python task.",
"3. Pass a guided SQL review and a guided Python review.",
"4. Record a learning reflection and mistakes.",
"",
"Update only the corresponding record in progress/daily-progress.json: completed_ids, completed_pages, guided_reviewed, applied_task_done (later days), reflection_completed, actual focus_minutes, notes and evidence_links. The workflow renders this dashboard on each JSON update; or run the script locally.", "",
"Never mark a task completed just because you spent its scheduled time. The old 20 solved questions remain a baseline, not new daily wins.", ""
]
(root / "PROGRESS-DASHBOARD.md").write_text("\n".join(out), encoding="utf-8")
print(f"Rendered {len(days)} daily progress bars")
