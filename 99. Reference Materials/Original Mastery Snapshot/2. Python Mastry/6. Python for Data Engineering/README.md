# Part 6. Python for Data Engineering

**Source:** [Python for Data Engineering Notes, pp. 69–74](<../Source/1793477658005.pdf#page=69>). Follow the store pipeline from pandas analysis to database load, tests, larger-scale processing, and scheduling. Each lesson adds a small example and a **Your turn** exercise. Start the parent [practice runner](<../practice_runner.py>) to use the per-snippet Run and edit links.

| Lesson | Topic | PDF page | Local requirements |
|---:|---|---:|---|
| 01 | [Pandas essentials mapped to SQL](<01. Pandas essentials mapped to SQL.md>) | 69 | pandas, supplied CSV files |
| 02 | [Pandas pitfalls and speed](<02. Pandas pitfalls and speed.md>) | 70 | pandas, NumPy, supplied files |
| 03 | [Python and databases](<03. Python and databases.md>) | 71 | `sqlite3`; final example needs pandas |
| 04 | [Build an idempotent ETL pipeline](<04. Build an idempotent ETL pipeline.md>) | 72 | Standard library and supplied CSV |
| 05 | [Testing and data quality](<05. Testing and data quality.md>) | 73 | pytest and pandas; supplied files |
| 06 | [From pandas to PySpark and Airflow](<06. From pandas to PySpark and Airflow.md>) | 74 | Pandas example runnable; PySpark/Airflow optional |

The local Python used for this project has pandas, NumPy, and pytest. PySpark, Airflow, and the live HTTP `requests` examples require separate packages or services and are labeled in the relevant lessons. The [source dataset](<../python_de_dataset/README.md>) is already saved here.

**Learning flow:** Reconcile values in pandas, spot quiet data bugs, send safe queries to SQLite, load one day idempotently, test both code and data, then translate the ideas to Spark and Airflow. The [Part 1 W3Schools topics](<../1. Python from Zero/README.md#w3schools-topics-inside-the-lessons>) appear at the end of the related lessons as reminders; no separate W3Schools folder interrupts the sequence.

[Previous part](<../5. Coding Round Patterns/README.md>) | [Next part](<../7. Practice Prep Flow and Revision/README.md>) | [Python index](<../README.md>)
