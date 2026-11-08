# Planted data issues (instructor key)

Every issue below was put in on purpose. Counts are exact for this build.

| Table | Issue | Rows | How to find it |
|---|---|---:|---|
| Category | Active stored in six spellings: Yes, yes, 'Yes ' (trailing space), Y, 1 for active; No, 0 for inactive | 12 | `SELECT Active, COUNT(*) FROM Category GROUP BY Active` |
| Category | Category 5013 Electronics Accessories exists but has no products | 1 | `LEFT JOIN Products, COUNT(p.ProductID) = 0` |
| Products | CategoryID 5012 (a category never added to Category) | 40 | `LEFT JOIN Category ... WHERE cat.CategoryID IS NULL` |
| Products | Market_Price below Sale_Price | 12 | `WHERE Market_Price < Sale_Price` |
| Products | Market_Price = 0 | 6 | `WHERE Market_Price = 0` |
| Products | Sale_Price missing | 4 | `WHERE Sale_Price IS NULL` |
| Products | Brand blank or NULL | 10 | `WHERE NULLIF(TRIM(Brand), '') IS NULL` |
| Products | Product name with trailing spaces | 8 | `WHERE Product <> TRIM(Product)` |
| Products | Rating missing (unrated products) | 4360 | `WHERE Rating IS NULL` |
| Suppliers | Country spelled India / INDIA / 'india ' (case and trailing space) | 3 | `SELECT Country, COUNT(*) FROM Suppliers GROUP BY Country` |
| Suppliers | Email missing | 1 | `WHERE Email IS NULL` |
| Suppliers | Email with no domain suffix (farms@konkanfresh) | 1 | `WHERE Email NOT LIKE '%_@_%._%'` |
| Suppliers | Supplier 18 duplicates supplier 1 (same address and email, name has a trailing space) | 1 | `GROUP BY LOWER(TRIM(CompanyName)) HAVING COUNT(*) > 1` |
| Suppliers | Supplier 17 has no order lines | 1 | `NOT EXISTS in OrderDetails` |
| Payments | Allowed stored as Yes / No / N | 10 | `SELECT Allowed, COUNT(*) FROM Payments GROUP BY Allowed` |
| Shippers | Coastal Cargo Lines and Konkan Express Couriers never used | 2 | `LEFT JOIN Orders ... COUNT(o.OrderID) = 0` |
| Customers | City spelling variants: Bengaluru / Bangalore / 'bangalore ' / BENGALURU, Gurugram / Gurgaon, Delhi / New Delhi, Mumbai / Bombay, stray trailing spaces |  | `SELECT City, COUNT(*) ... ORDER BY LOWER(TRIM(City))` |
| Customers | Phone in five formats (10 digits, +91 with spaces, +91-, leading 0) or missing |  | `SELECT LEFT(Phone, 4), COUNT(*) GROUP BY 1` |
| Customers | Email with a space inside | 3 | `WHERE Email LIKE '% %'` |
| Customers | Duplicate accounts: same person re-registered with an email that differs only in case or spaces | 72 | `GROUP BY LOWER(TRIM(Email)) HAVING COUNT(*) > 1` |
| Customers | Registered but never ordered | 647 | `LEFT JOIN Orders ... WHERE o.OrderID IS NULL` |
| Orders | Never shipped although placed more than 14 days before the extract (cancelled in practice; no status column) | 320 | `ShipDate IS NULL AND OrderDate <= MAX(OrderDate) - 14` |
| Orders | Shipped before ordered | 12 | `WHERE ShipDate < OrderDate` |
| Orders | Delivered before shipped | 9 | `WHERE DeliveryDate < ShipDate` |
| Orders | Delivered with no ship date | 6 | `WHERE DeliveryDate IS NOT NULL AND ShipDate IS NULL` |
| Orders | PaymentID missing | 20 | `WHERE PaymentID IS NULL` |
| Orders | ShipperID missing | 25 | `WHERE ShipperID IS NULL` |
| Orders | ShipperID 11 does not exist in Shippers | 3 | `LEFT JOIN Shippers ... WHERE sh.ShipperID IS NULL` |
| Orders | CustomerID not in Customers (deleted accounts 99001-99003) | 8 | `NOT EXISTS in Customers` |
| Orders | Total_Order_Amount inflated by 50% (keying error) | 6 | `Reconciliation status 'Header above lines' (Q86)` |
| Orders | Total_Order_Amount = 0 | 4 | `WHERE Total_Order_Amount = 0` |
| Orders | Total_Order_Amount missing | 5 | `WHERE Total_Order_Amount IS NULL` |
| Orders | Paid with Pay Later after it was switched off on 1 Jul 2025 | 12 | `Q37 status VIOLATION` |
| Orders | Order header with no lines | 10 | `NOT EXISTS in OrderDetails` |
| Customers | DateEntered later than the customer's first order (sign-up date overwritten on profile update) | 15 | `o.OrderDate < c.DateEntered` |
| Orders | Duplicate submissions: a second order with the same customer, date and basket (most also copy payment and amount) | 45 | `Q93` |
| OrderDetails | Exact duplicate lines (reloaded rows with a new OrderDetailID) | 60 | `GROUP BY OrderID, ProductID, Quantity, SupplierID HAVING COUNT(*) > 1` |
| OrderDetails | Same product added on a second line (29 from a different supplier, so split sourcing; 1 from the same supplier) | 30 | `Q72` |
| OrderDetails | Quantity missing | 10 | `WHERE Quantity IS NULL` |
| OrderDetails | Quantity = 0 | 5 | `WHERE Quantity = 0` |
| OrderDetails | Lines whose OrderID is not in Orders | 12 | `NOT EXISTS in Orders` |
| OrderDetails | Lines whose ProductID is not in Products | 15 | `NOT EXISTS in Products` |
| OrderDetails | Lines whose SupplierID is not in Suppliers | 5 | `NOT EXISTS in Suppliers` |
| Customers | DateEntered stored as text in three formats (YYYY/MM/DD, DD-MM-YYYY, YYYY-MM-DD) or blank | 40 | `Parse with a CASE on the pattern (load script)` |
