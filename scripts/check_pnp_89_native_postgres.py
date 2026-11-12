#!/usr/bin/env python3
"""Forensic native PostgreSQL 16 replay of the immutable PNP Q089 supplied key.

All writes occur on disposable session-local TEMP tables. Executes the archived
key literally first; if native parsing rejects it, records that rejection and
runs a separately labeled, single-WHERE-TRUE parser-disambiguation control.
This is NOT authenticated provider grading or independently solved coursework.
"""
import hashlib
import os
import re
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ("99. Reference Materials/Original Mastery Snapshot/"
               "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice")
SOURCE = BASE / ("14. Data Quality and Deduplication/"
                 "P089. Incremental load with a watermark and lookback.md")
KEY = BASE / "Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql"
SOURCE_BLOB = "dc820d26afb08381d923f2cd215a0d64297a8d91"
KEY_BLOB = "7912c8e676621c513e0b635a40c6ee299404676e"
COLUMNS = ("OrderID", "CustomerID", "PaymentID", "OrderDate", "ShipperID",
           "Total_Order_Amount", "ShipDate", "DeliveryDate")
CREATE_SOURCE = """CREATE TEMP TABLE Orders (
 OrderID integer PRIMARY KEY, CustomerID integer, PaymentID integer,
 OrderDate date, ShipperID integer, Total_Order_Amount numeric,
 ShipDate date, DeliveryDate date
) ON COMMIT DROP"""
INSERT_SOURCE = "INSERT INTO Orders (" + ", ".join(COLUMNS) + ") VALUES (" + ", ".join(["%s"]*8) + ")"
INSERT_TARGET = ("INSERT INTO orders_target (" + ", ".join(COLUMNS) +
                 ", etl_updated_at) VALUES (" + ", ".join(["%s"]*9) + ")")


def blob_sha(path):
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def extract():
    assert blob_sha(SOURCE) == SOURCE_BLOB, "original P089 question mutated"
    assert blob_sha(KEY) == KEY_BLOB, "original supplier SQL mutated"
    src = SOURCE.read_text(encoding="utf-8")
    for token in ("# PNP Q089.", "21-day lookback", "NULL OrderDate",
                  "NOT SOLVED YET", "## Official solution", "Pending",
                  "inserted", "updated", "unchanged"):
        assert token in src, ("question no longer matches source", token)
    key = KEY.read_text(encoding="utf-8")
    match = re.search(r"(?ms)^-- Q89\.[^\n]*\n(.*?)(?=^-- Q90\.)", key)
    assert match, "archived Q89 answer section not found"
    section = match.group(1)
    assert section.count("-- Tonight's incremental load.") == 1
    prepare, load = section.split("-- Tonight's incremental load.")
    ddl = re.search(r"(?s)(CREATE TEMP TABLE orders_target \(.*?;)", prepare)
    seed = re.search(r"(?s)(INSERT INTO orders_target\s*\(.*?;)", prepare)
    assert ddl and seed and load.strip().startswith("WITH params AS (")
    assert load.strip().endswith(";") and "ON CONFLICT (OrderID) DO UPDATE" in load
    for token in ("LIKE Orders INCLUDING ALL", "MAX(src.OrderDate) - 14 AS run_date",
                  "MAX(t.OrderDate)", "21 AS lookback_days", "OR o.OrderDate IS NULL",
                  "IS DISTINCT FROM", "RETURNING t.OrderID",
                  "WHEN u.OrderID IS NULL THEN 'unchanged'"):
        assert token in section, ("key section drift", token)
    print("INSPECTED P089 original question " + SOURCE_BLOB +
          "; supplied key " + KEY_BLOB + "; learner NOT SOLVED YET / Pending")
    return ddl.group(1), seed.group(1), load.strip()


def order(number, date, amount, customer=10):
    return (number, customer, None, date, None, amount, None, None)


def target_row(order_data, stamp="2026-01-01T00:00:00+00:00"):
    return (*order_data, stamp)


def connect():
    return psycopg.connect(
        host=os.environ.get("PGHOST", "127.0.0.1"),
        port=os.environ.get("PGPORT", "5432"),
        dbname=os.environ.get("PGDATABASE", "audit"),
        user=os.environ.get("PGUSER", "audit"),
        password=os.environ.get("PGPASSWORD", "audit"),
        autocommit=True)


def load_rows(conn, source, target=(), seeded=False, ddl=None, seed=None):
    conn.execute(CREATE_SOURCE)
    with conn.cursor() as cur:
        if source:
            cur.executemany(INSERT_SOURCE, source)
    conn.execute(ddl)
    if seeded:
        conn.execute(seed)
    elif target:
        with conn.cursor() as cur:
            cur.executemany(INSERT_TARGET, target)


def snapshot(conn):
    query = ("SELECT OrderID, CustomerID, PaymentID, OrderDate, ShipperID, "
             "Total_Order_Amount, ShipDate, DeliveryDate, etl_updated_at "
             "FROM orders_target ORDER BY OrderID")
    return {r[0]: r[1:] for r in conn.execute(query).fetchall()}


def actions(rows):
    return [(str(label), int(count)) for label, count in rows]


def perform(conn, original, expected_failure):
    # Nested transaction creates a SAVEPOINT: syntax failure cannot poison the
    # outer fixture and cannot be mistaken for an original-key successful replay.
    try:
        with conn.transaction():
            result = conn.execute(original).fetchall()
        assert not expected_failure, "original SQL unexpectedly parsed after earlier native failure"
        return result, original, "ORIGINAL_KEY"
    except psycopg.Error as exc:
        assert exc.sqlstate == "42601", ("unexpected native SQL runtime error", exc.sqlstate, str(exc))
        assert "FROM batch AS b\n    ON CONFLICT" in original, "source JOIN/ON ambiguity cannot be pinpointed"
        assert original.count("FROM batch AS b\n    ON CONFLICT") == 1
        print("REPRODUCED P089 NATIVE_POSTGRES original SQLSTATE 42601 syntax rejection: " +
              " ".join(str(exc).splitlines()[:1]))
        guarded = original.replace("FROM batch AS b\n    ON CONFLICT",
                                   "FROM batch AS b\n    WHERE TRUE\n    ON CONFLICT")
        assert guarded.count("WHERE TRUE\n    ON CONFLICT") == 1
        with conn.transaction():
            result = conn.execute(guarded).fetchall()
        return result, guarded, "AUDITOR_WHERE_TRUE_CONTROL"


def check_case(label, source, target, seeded, expected, ddl, seed, original,
               expected_failure=False, rerun=None, check=None):
    with connect() as conn:
        version = int(conn.execute("SHOW server_version_num").fetchone()[0])
        assert 160000 <= version < 170000, version
        with conn.transaction():
            load_rows(conn, source, target, seeded, ddl, seed)
            got, runnable, mode = perform(conn, original, expected_failure)
            assert actions(got) == expected, (label, mode, got, expected)
            if check is not None:
                check(conn)
            if rerun is not None:
                before = snapshot(conn)
                again = actions(conn.execute(runnable).fetchall())
                assert again == rerun, (label, "rerun", again, rerun)
                assert snapshot(conn) == before, (label, "rerun changed target or timestamps")
            print("PASS P089 NATIVE_POSTGRES " + label + "; " + mode +
                  "; counts=" + str(actions(got)))


def main():
    ddl, seed, sql = extract()
    with connect() as conn:
        version = int(conn.execute("SHOW server_version_num").fetchone()[0])
        assert 160000 <= version < 170000, version
        print("NATIVE PostgreSQL server_version_num=" + str(version) +
              "; no changes to immutable source key")

    original = [order(1,"2026-01-10",100),order(2,"2026-01-11",200),
                order(3,None,50),order(4,"2025-12-01",30)]
    seeded_target = [target_row(order(1,"2026-01-10",100)),
                     target_row(order(2,"2026-01-11",150)),
                     target_row(order(4,"2025-12-01",30))]
    def check_explicit(conn):
        rows = snapshot(conn)
        assert set(rows) == {1,2,3,4}, rows
        assert rows[1][-1].year == 2026 and rows[1][-1].month == 1 and rows[1][-1].day == 1
        assert rows[4][-1] == rows[1][-1], rows
        assert rows[2][4] == 200 and rows[2][-1] != rows[1][-1], rows
        assert rows[3][-1] != rows[1][-1], rows

    # The original statement is attempted before any compatibility control.
    # A failed native parse is an adverse audit finding, not a clean key pass.
    check_case("explicit_question_illustration", original, seeded_target, False,
               [("inserted",1),("updated",1),("unchanged",1)], ddl, seed, sql,
               check=check_explicit, rerun=[("inserted",0),("updated",0),("unchanged",3)])

    def check_auto_seed(conn):
        assert set(snapshot(conn)) == {1,2,3,4}
        # Seed has no illustration's pre-existing Jan records; they insert anew.
    check_case("supplier_14day_demo_seed_mismatch", original, (), True,
               [("inserted",3),("updated",0),("unchanged",1)], ddl, seed, sql,
               rerun=[("inserted",0),("updated",0),("unchanged",3)],
               check=check_auto_seed)

    boundary_src = [order(10,"2026-01-22",22),order(11,"2026-01-01",101),
                    order(12,"2026-01-01",12),order(13,"2025-12-31",13),
                    order(14,None,14),order(15,None,15)]
    boundary_tgt = [target_row(order(10,"2026-01-22",22)),
                    target_row(order(11,"2026-01-01",100)),
                    target_row(order(15,None,15))]
    def check_boundary(conn):
        rows = snapshot(conn)
        assert set(rows) == {10,11,12,14,15} and 13 not in rows, rows
        assert rows[10][-1] == rows[15][-1] and rows[11][-1] != rows[10][-1]
    check_case("inclusive_21day_NULL_noop_timestamps", boundary_src,
               boundary_tgt, False,
               [("inserted",2),("updated",1),("unchanged",2)], ddl, seed, sql,
               check=check_boundary, rerun=[("inserted",0),("updated",0),("unchanged",5)])
    check_case("empty_source", [], (), True,
               [("inserted",0),("updated",0),("unchanged",0)], ddl, seed, sql)

    print("PARTIAL P089: source parse status and bounded native scratch-table "
          "results must be interpreted separately. No original PDF/full dataset, "
          "provider grade, learner solve or final audit signoff.")


if __name__=="__main__":
    main()
