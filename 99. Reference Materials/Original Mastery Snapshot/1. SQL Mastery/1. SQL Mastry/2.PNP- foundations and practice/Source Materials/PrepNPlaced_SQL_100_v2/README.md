# PrepNPlaced: 100 SQL Interview Questions, v2 dataset

A complete SQL practice kit for product-based company interviews: 100 questions from Easy to Expert, each with a business scenario, the final query, a line-by-line explanation, the real output, common mistakes and an interview follow-up. Every query was executed on the dataset in this folder, so your results should match the book.

## What's in the zip

| Path | What it is |
|---|---|
| `100_SQL_Interview_Questions.pdf` | The book: dataset guide, question index, all 100 questions, topic coverage and quality audit |
| `data/*.csv` | The 8 tables of the PrepNPlaced Commerce Dataset v2 |
| `data/load_dataset_v2.sql` | Creates the tables and loads the CSVs into PostgreSQL |
| `sql/all_100_solutions.sql` | The final query of every question, in one file |
| `schema/Ecomm_schema.xlsx` | The original schema design the dataset follows |
| `instructor/planted_issues.md` | Answer key: every data-quality problem planted in the data, with exact counts. Don't open it until you have tried Q87 to Q93 |

## Load the data (PostgreSQL 14 or newer)

```bash
cd data
createdb ecomm
psql -d ecomm -f load_dataset_v2.sql
```

The script prints a row count per table at the end. You should see:

| Table | Rows |
|---|---:|
| Suppliers | 18 |
| Products | 22,088 |
| Category | 12 |
| Shippers | 10 |
| Payments | 10 |
| Customers | 5,072 |
| Orders | 46,438 |
| OrderDetails | 168,567 |

With pgAdmin or DBeaver, run the script from the `data` folder, or change the file paths in the `\copy` lines to full paths. On MySQL, the PDF's dataset guide has a table of PostgreSQL-to-MySQL equivalents; import the CSVs with your tool's wizard and parse `Orders` dates as `DD-MM-YYYY`.

## What's real and what's generated

- **Real:** the product catalogue. All 22,088 products, with their names, brands, sub-categories, sale prices and printed prices, come from a real Indian online grocery and household store.
- **Generated:** customers, orders, order lines, suppliers, couriers and product ratings. Real customer orders are never public, so these were generated to behave like a growing Indian e-commerce business: three years of orders (2023 to 2025), festive peaks every October and November, UPI overtaking other payment methods, popular products and long tails, repeat buyers and one-time buyers. Supplier and courier names are fictional, and ratings say nothing about the real brands.
- **Deliberately messy:** like production data, the tables contain NULLs, broken keys, duplicate accounts, reloaded rows, impossible dates, inconsistent flags and spelling variants. Writing queries that survive this is the skill interviews test.

## How to study with it

1. Read the dataset guide at the front of the PDF (Deliverable A). It lists the assumptions every question uses, such as late delivery meaning more than 7 days.
2. Work through the questions in order. For each one, read the scenario and problem, write your own query, run it, and only then compare with Steps 4 to 6.
3. Read Step 8 (common mistakes) even when you got it right. Most of them run without an error and return a wrong number, which is exactly what interviewers probe.
4. Answer the Step 9 follow-up out loud, as you would in an interview.
5. Before the Hard and Expert sections, run Q87 to Q93 to discover the data-quality problems yourself, then check your findings against `instructor/planted_issues.md`.

## Extra practice: product ratings

`Products.Rating` (out of 5, NULL when unrated) is in the dataset, but none of the 100 questions is built around it. Try these on your own; there is no answer key, so check your results by reasoning about them:

1. The share of products that are rated, by category, including products whose category is missing from `Category`.
2. Average rating by brand, only for brands with at least 20 rated products. Why does the minimum matter?
3. Within each sub-category, the products rated above the sub-category's average rating but selling below its median units.
4. Do higher-rated products sell more? Compare average units sold per product across rating bands (below 3, 3 to 4, 4 and above, unrated).
5. Rated products that have never been ordered. What does that suggest about where ratings come from?
