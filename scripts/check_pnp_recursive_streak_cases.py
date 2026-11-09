"""Independent, auditor-authored SQLite *synthetic* cases for PNP recursive/streak source contracts.

DOES NOT run preserved official MySQL answers or modify learner attempts.
Each fixture uses a disposable in-memory SQLite database.
"""
import sqlite3


def rows(db, sql):
    return db.execute(sql).fetchall()


def verify(name, sql, expected, setup=None):
    with sqlite3.connect(':memory:') as db:
        if setup:
            db.executescript(setup)
        actual = rows(db, sql)
        assert actual == expected, f'{name}: expected {expected!r}, got {actual!r}'
    print(f'PASS {name}')


verify('A046 January inclusive 31 days', '''
WITH RECURSIVE days(d) AS (
  SELECT date('2026-01-01')
  UNION ALL SELECT date(d, '+1 day') FROM days WHERE d < '2026-01-31'
)
SELECT COUNT(*), MIN(d), MAX(d) FROM days;
''', [(31, '2026-01-01', '2026-01-31')])

employees = '''
CREATE TABLE employees(emp_id INTEGER PRIMARY KEY, emp_name TEXT, manager_id INTEGER);
INSERT INTO employees VALUES
  (1,'CEO',NULL),(5,'Mira',1),(6,'Ana',5),(7,'Ben',6),(8,'Cy',5),
  (9,'Dev',1),(12,'Cycle A',13),(13,'Cycle B',12);
'''
verify('A047 report hierarchy levels; manager and unrelated excluded', '''
WITH RECURSIVE descendants(emp_id, emp_name, lvl, path) AS (
  SELECT emp_id, emp_name, 1, ',5,' || emp_id || ','
  FROM employees WHERE manager_id = 5
  UNION ALL
  SELECT e.emp_id, e.emp_name, d.lvl + 1, d.path || e.emp_id || ','
  FROM employees e JOIN descendants d ON e.manager_id = d.emp_id
  WHERE d.lvl < 100 AND instr(d.path, ',' || e.emp_id || ',') = 0
)
SELECT emp_id, emp_name, lvl FROM descendants ORDER BY lvl, emp_id;
''', [(6, 'Ana', 1), (8, 'Cy', 1), (7, 'Ben', 2)], employees)

verify('A048 paths from rooted tree, root first', '''
WITH RECURSIVE paths(emp_id, path) AS (
  SELECT emp_id, CAST(emp_id AS TEXT) FROM employees WHERE manager_id IS NULL
  UNION ALL
  SELECT e.emp_id, p.path || ' > ' || e.emp_id
  FROM employees e JOIN paths p ON e.manager_id = p.emp_id
  WHERE instr(' > ' || p.path || ' > ', ' > ' || e.emp_id || ' > ') = 0
)
SELECT emp_id, path FROM paths WHERE emp_id IN (1,5,6) ORDER BY emp_id;
''', [(1, '1'), (5, '1 > 5'), (6, '1 > 5 > 6')], employees)

verify('A049 deepest rooted org level, root=0', '''
WITH RECURSIVE depth(emp_id, lvl) AS (
  SELECT emp_id, 0 FROM employees WHERE manager_id IS NULL
  UNION ALL SELECT e.emp_id, d.lvl + 1 FROM employees e
  JOIN depth d ON e.manager_id = d.emp_id WHERE d.lvl < 100
)
SELECT MAX(lvl) FROM depth;
''', [(3,)], employees)  # CEO -> Mira -> Ana -> Ben

verify('A050 ordered literal text split', '''
WITH RECURSIVE pieces(rest, value, pos) AS (
  SELECT 'a,b,c,', '', 0
  UNION ALL
  SELECT substr(rest, instr(rest, ',') + 1),
         substr(rest, 1, instr(rest, ',') - 1), pos + 1
  FROM pieces WHERE rest <> ''
)
SELECT value FROM pieces WHERE pos > 0 ORDER BY pos;
''', [('a',), ('b',), ('c',)])

verify('A080 only interior missing IDs; boundaries and duplicates', '''
WITH ids AS (SELECT DISTINCT id FROM ord WHERE id IS NOT NULL),
lagged AS (SELECT id, LAG(id) OVER(ORDER BY id) AS prev_id FROM ids)
SELECT prev_id + 1, id - 1 FROM lagged
WHERE prev_id IS NOT NULL AND id > prev_id + 1 ORDER BY prev_id;
''', [(3, 4), (6, 7)], '''
CREATE TABLE ord(id INTEGER);
INSERT INTO ord VALUES (1),(2),(2),(5),(8);
''')

orders = '''
CREATE TABLE orders(order_id INTEGER, cust_id INTEGER, order_date TEXT);
INSERT INTO orders VALUES
 (1,10,'2026-01-01'),(2,10,'2026-01-01 15:00:00'),
 (3,10,'2026-01-02'),(4,10,'2026-01-03'),(5,10,'2026-01-05'),
 (6,20,'2026-02-10'),(7,20,'2026-02-11');
'''
cte_days = '''
WITH unique_days AS (
 SELECT DISTINCT cust_id, date(order_date) AS d
 FROM orders WHERE cust_id IS NOT NULL AND order_date IS NOT NULL
),
numbered AS (
 SELECT cust_id, d, ROW_NUMBER() OVER(PARTITION BY cust_id ORDER BY d) AS rn
 FROM unique_days
),
islands AS (
 SELECT cust_id, d, date(d, '-' || rn || ' days') AS island_key
 FROM numbered
),
ranges AS (
 SELECT cust_id, MIN(d) AS first_day, MAX(d) AS last_day, COUNT(*) AS days
 FROM islands GROUP BY cust_id, island_key
)
'''
verify('A081 distinct ordering days into intervals', cte_days + '''
SELECT cust_id, first_day, last_day FROM ranges ORDER BY cust_id, first_day;
''', [(10,'2026-01-01','2026-01-03'),(10,'2026-01-05','2026-01-05'),
      (20,'2026-02-10','2026-02-11')], orders)
verify('A082 unique-day streak length (not order count)', cte_days + '''
SELECT cust_id, MAX(days) FROM ranges GROUP BY cust_id ORDER BY cust_id;
''', [(10,3),(20,2)], orders)

month_orders = '''
CREATE TABLE orders(order_id INTEGER, cust_id INTEGER, order_date TEXT);
INSERT INTO orders VALUES
 (1,10,'2026-01-10'),(2,10,'2026-02-10'),(3,10,'2026-02-15'),
 (4,10,'2026-03-10'),(5,20,'2026-01-10'),(6,20,'2026-03-10'),
 (7,20,'2026-04-10'),(8,30,'2025-11-01'),(9,30,'2025-12-01'),
 (10,30,'2026-01-01');
'''
months_cte = '''
WITH months AS (
 SELECT DISTINCT cust_id, substr(order_date, 1, 7) AS ym,
    CAST(substr(order_date,1,4) AS INT)*12 + CAST(substr(order_date,6,2) AS INT) AS month_index
 FROM orders WHERE cust_id IS NOT NULL AND order_date IS NOT NULL
), numbered AS (
 SELECT *, ROW_NUMBER() OVER(PARTITION BY cust_id ORDER BY month_index) AS rn
 FROM months
), runs AS (
 SELECT cust_id, COUNT(*) AS n FROM numbered
 GROUP BY cust_id, month_index - rn
)
'''
verify('A083 three calendar months, even crossing a year', months_cte + '''
SELECT DISTINCT cust_id FROM runs WHERE n >= 3 ORDER BY cust_id;
''', [(10,),(30,)], month_orders)

verify('A084 missing source seat_bookings: synthetic compact ranges', '''
WITH ids AS (SELECT DISTINCT id FROM seat_bookings WHERE id IS NOT NULL),
numbers AS (
  SELECT id, ROW_NUMBER() OVER(ORDER BY id) AS rn FROM ids
)
SELECT MIN(id), MAX(id) FROM numbers GROUP BY id-rn ORDER BY MIN(id);
''', [(1,3),(7,8),(10,10)], '''
CREATE TABLE seat_bookings(id INTEGER);
INSERT INTO seat_bookings VALUES (1),(2),(3),(7),(8),(8),(10);
''')

p065_query = '''
WITH month_rows AS (
  SELECT DISTINCT cust_id, substr(order_date,1,7) AS ym,
    CAST(substr(order_date,1,4) AS INT)*12+CAST(substr(order_date,6,2) AS INT) AS mi
  FROM orders WHERE cust_id IS NOT NULL AND order_date IS NOT NULL
), numbered AS (
  SELECT *, ROW_NUMBER() OVER(PARTITION BY cust_id ORDER BY mi) AS rn FROM month_rows
), streaks AS (
  SELECT cust_id, MIN(ym) || '-01' AS start_month, MAX(ym) || '-01' AS end_month,
         COUNT(*) AS n FROM numbered GROUP BY cust_id, mi-rn
), best AS (
  SELECT *, ROW_NUMBER() OVER(PARTITION BY cust_id ORDER BY n DESC, end_month DESC) AS pick
  FROM streaks
), ranked AS (
  SELECT *, RANK() OVER(ORDER BY n DESC) AS global_rank FROM best WHERE pick=1
)
SELECT cust_id, start_month, end_month, n FROM ranked WHERE global_rank <= 10
ORDER BY n DESC, cust_id;
'''
verify('P065 recent streak selected on equal lengths', p065_query, [
    (20,'2025-01-01','2025-03-01',3), (10,'2025-04-01','2025-05-01',2)
], '''
CREATE TABLE orders(cust_id INTEGER, order_date TEXT);
INSERT INTO orders VALUES
  (10,'2025-01-01'),(10,'2025-02-01'),(10,'2025-04-01'),(10,'2025-05-01'),
  (20,'2025-01-01'),(20,'2025-02-01'),(20,'2025-03-01');
''')
with sqlite3.connect(':memory:') as db:
    db.execute('CREATE TABLE orders(cust_id INTEGER, order_date TEXT)')
    for cust in range(1,13):
        count = 4 if cust <= 9 else 3 if cust <= 11 else 2
        db.executemany('INSERT INTO orders VALUES (?,?)',
                       [(cust, f'2026-{i:02d}-01') for i in range(1,count+1)])
    result = rows(db,p065_query)
    assert len(result)==11 and {r[0] for r in result} == set(range(1,12)), result
    assert result[-2][3] == 3 and result[-1][3] == 3, result
print('PASS P065 include all customers tied at tenth-place rank')
print('12 source-aligned synthetic verifications PASS; NOT official answers or learner solutions')
