# Python data for the 80-page notes

[Python index](<../README.md>) | [Start Here](<../00. Start Here.md>) | [Original ZIP](<../Source/Python_Dataset_DE.zip>) | [Original PDF](<../Source/1793477658005.pdf>)

These 11 data files came from the mentor's supplied `Python_Dataset_DE.zip`. Its `README.txt` is preserved here. The original ZIP is saved unchanged in `Source`; these extracted files are the working copy for exercises.

## Run the examples

Open a terminal in the parent `2. Python Mastry` folder. A note that reads `python_de_dataset/orders.csv` works from there. For example:

```python
import csv

with open("python_de_dataset/orders.csv", newline="", encoding="utf-8") as file:
    orders = list(csv.DictReader(file))

print(len(orders))
print(orders[0]["order_id"], orders[0]["amount"])
```

Expected output:

```text
15
101 1198.00
```

The PDF uses short names such as `open("orders.csv")`. To run one of those snippets unchanged, set the terminal's working folder to this `python_de_dataset` folder first. File paths in Python are relative to the **working folder**, not the PDF or Markdown file.

## Files and checks

| File | Records | Use |
|---|---:|---|
| `orders.csv` | 15 | Orders, status, dates, amount |
| `order_items.csv` | 24 | Order lines |
| `products.csv` | 8 | Product lookup |
| `customers.json` | 8 | Customers, nested addresses, tags |
| `events.jsonl` | 12 | Clickstream events |
| `logins.csv` | 12 | Login days |
| `employees.csv` | 9 | Staff, including `hire_date` |
| `app.log` | 14 lines | Pipeline logs |
| `orders_dirty.csv` | 7 | Validation practice |
| `snapshot_day1.csv` | 8 | First customer snapshot |
| `snapshot_day2.csv` | 8 | Second customer snapshot |

The supplied orders have **12 delivered**, **2 cancelled**, and **1 returned**. Delivered revenue by month is January **1,994.00**, February **2,847.00**, March **7,291.00**, and April **6,840.00**, totalling **18,972.00**. These values match the PDF's examples.

[Continue with Part 1](<../1. Python from Zero/README.md>).
