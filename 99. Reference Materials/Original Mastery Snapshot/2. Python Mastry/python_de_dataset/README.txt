Python for Data Engineering: End to End Notes - dataset
Durgesh Yadav | prepnplaced.com

Unzip into a folder, open a terminal there, and run any snippet from the PDF.
Every snippet reads these files by name (for example open("orders.csv")).

orders.csv          15 orders (same store as the SQL End to End Notes)
order_items.csv     24 order lines
products.csv        8 products
customers.json      8 customers, nested address, tags list
events.jsonl        12 clickstream events, one JSON object per line
logins.csv          12 login days
employees.csv       9 employees
app.log             14 pipeline log lines, one malformed on purpose
orders_dirty.csv    7 rows with planted data problems
snapshot_day1.csv   customers on day 1
snapshot_day2.csv   customers on day 2

Tested with Python 3.12, pandas 3.0, pytest 9, PySpark 4.
