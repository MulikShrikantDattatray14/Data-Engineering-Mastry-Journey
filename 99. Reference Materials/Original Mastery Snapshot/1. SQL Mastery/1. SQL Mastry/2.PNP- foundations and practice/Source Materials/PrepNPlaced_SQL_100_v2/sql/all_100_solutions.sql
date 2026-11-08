-- 100 SQL interview questions: final solutions (Step 4 of each question)
-- PostgreSQL 16. Load the data first with data/load_dataset_v2.sql.

-- Q1. Brand directory (Easy)
SELECT DISTINCT p.Brand
FROM Products AS p
WHERE NULLIF(TRIM(p.Brand), '') IS NOT NULL
ORDER BY p.Brand;

-- Q2. Ten highest-priced products (Easy)
SELECT p.ProductID,
       p.Product,
       p.Brand,
       p.Sale_Price
FROM Products AS p
WHERE p.Sale_Price IS NOT NULL
ORDER BY p.Sale_Price DESC,
         p.ProductID
LIMIT 10;

-- Q3. Customers in metro cities (Easy)
SELECT c.CustomerID,
       c.FirstName,
       c.LastName,
       TRIM(c.City) AS City,
       c.State
FROM Customers AS c
WHERE LOWER(TRIM(c.City)) IN ('bengaluru', 'bangalore', 'mumbai', 'bombay',
                                'delhi', 'new delhi', 'hyderabad', 'chennai')
ORDER BY TRIM(c.City), c.CustomerID;

-- Q4. Customer emails that cannot be delivered (Easy)
SELECT c.CustomerID,
       c.FirstName,
       c.LastName,
       c.Email,
       CASE WHEN c.Email IS NULL OR TRIM(c.Email) = '' THEN 'Missing'
            WHEN c.Email LIKE '% %'                    THEN 'Contains a space'
            ELSE 'Not in name@domain.tld form'
       END AS issue
FROM Customers AS c
WHERE c.Email IS NULL
   OR TRIM(c.Email) = ''
   OR c.Email LIKE '% %'
   OR c.Email NOT LIKE '%_@_%._%'
ORDER BY c.CustomerID;

-- Q5. Orders placed in Q1 2025 (Easy)
SELECT o.OrderID,
       o.CustomerID,
       o.OrderDate,
       o.Total_Order_Amount
FROM Orders AS o
WHERE o.OrderDate >= DATE '2025-01-01'
  AND o.OrderDate <  DATE '2025-04-01'
ORDER BY o.OrderDate, o.OrderID;

-- Q6. Most expensive products that are never discounted (Easy)
SELECT p.ProductID,
       p.Product,
       p.Brand,
       p.Sale_Price,
       p.Market_Price,
       COALESCE(NULLIF(p.Market_Price - p.Sale_Price, 0)::text, 'Full price') AS discount_display
FROM Products AS p
WHERE p.Sale_Price IS NOT NULL
  AND p.Market_Price IS NOT NULL
  AND NULLIF(p.Market_Price - p.Sale_Price, 0) IS NULL
ORDER BY p.Sale_Price DESC, p.ProductID
LIMIT 10;

-- Q7. Discount amount and percentage per product (Easy)
SELECT p.ProductID,
       p.Product,
       p.Market_Price,
       p.Sale_Price,
       NULLIF(p.Market_Price, 0) - p.Sale_Price                                      AS discount_amount,
       ROUND(100.0 * (p.Market_Price - p.Sale_Price) / NULLIF(p.Market_Price, 0), 2) AS discount_pct
FROM Products AS p
ORDER BY discount_pct DESC NULLS LAST,
         p.ProductID;

-- Q8. Price band labels (Easy)
SELECT p.ProductID,
       p.Product,
       p.Sale_Price,
       CASE
           WHEN p.Sale_Price IS NULL THEN 'Unknown'
           WHEN p.Sale_Price < 200   THEN 'Budget'
           WHEN p.Sale_Price < 700   THEN 'Mid'
           ELSE 'Premium'
       END AS price_band
FROM Products AS p
ORDER BY p.ProductID;

-- Q9. Check how Active and Allowed are encoded (Easy)
SELECT 'Category'                  AS source_table,
       'Active'                    AS flag_column,
       CAST(cat.Active AS VARCHAR) AS raw_value,
       COUNT(*)                    AS row_count
FROM Category AS cat
GROUP BY CAST(cat.Active AS VARCHAR)
UNION ALL
SELECT 'Payments',
       'Allowed',
       CAST(pay.Allowed AS VARCHAR),
       COUNT(*)
FROM Payments AS pay
GROUP BY CAST(pay.Allowed AS VARCHAR)
ORDER BY source_table, raw_value NULLS LAST;

-- Q10. Headline order KPIs (Easy)
SELECT COUNT(*)                            AS total_orders,
       COUNT(DISTINCT o.CustomerID)        AS ordering_customers,
       SUM(o.Total_Order_Amount)           AS total_order_value,
       ROUND(AVG(o.Total_Order_Amount), 2) AS avg_order_value,
       MIN(o.OrderDate)                    AS first_order_date,
       MAX(o.OrderDate)                    AS last_order_date
FROM Orders AS o;

-- Q11. How much of the catalogue has ever sold? (Easy)
SELECT COUNT(*)                                       AS rows_after_join,
       COUNT(od.OrderDetailID)                        AS sale_lines,
       COUNT(DISTINCT p.ProductID)                    AS listed_products,
       COUNT(DISTINCT od.ProductID)                   AS products_sold,
       ROUND(100.0 * COUNT(DISTINCT od.ProductID)
             / NULLIF(COUNT(DISTINCT p.ProductID), 0), 2) AS pct_sold
FROM Products AS p
LEFT JOIN OrderDetails AS od ON od.ProductID = p.ProductID;

-- Q12. Price and discount statistics per category ID (Easy)
SELECT p.CategoryID,
       COUNT(*)                                                  AS products,
       MIN(p.Sale_Price)                                         AS min_price,
       MAX(p.Sale_Price)                                         AS max_price,
       ROUND(AVG(p.Sale_Price), 2)                               AS avg_price,
       COUNT(*) FILTER (WHERE p.Sale_Price = p.Market_Price)     AS full_price_products,
       ROUND(AVG(100.0 * (p.Market_Price - p.Sale_Price)
                 / NULLIF(p.Market_Price, 0)), 2)                AS avg_discount_pct
FROM Products AS p
GROUP BY p.CategoryID
ORDER BY p.CategoryID NULLS LAST;

-- Q13. States with at least five customers (Easy)
SELECT COALESCE(TRIM(c.State), 'Unknown') AS State,
       COUNT(*)                           AS customer_count
FROM Customers AS c
GROUP BY COALESCE(TRIM(c.State), 'Unknown')
HAVING COUNT(*) >= 5
ORDER BY customer_count DESC, State;

-- Q14. Orders per month in 2025 (Easy)
SELECT DATE_TRUNC('month', o.OrderDate)::date AS order_month,
       COUNT(*)                               AS orders,
       SUM(o.Total_Order_Amount)              AS order_value
FROM Orders AS o
WHERE o.OrderDate >= DATE '2025-01-01'
  AND o.OrderDate <  DATE '2026-01-01'
GROUP BY DATE_TRUNC('month', o.OrderDate)::date
ORDER BY order_month;

-- Q15. Product count for every category (Easy)
SELECT cat.CategoryID,
       cat.CategoryName,
       COUNT(p.ProductID) AS product_count
FROM Category AS cat
LEFT JOIN Products AS p ON p.CategoryID = cat.CategoryID
GROUP BY cat.CategoryID, cat.CategoryName
ORDER BY product_count, cat.CategoryID;

-- Q16. December 2025 orders with customer names (Easy)
SELECT o.OrderID,
       o.OrderDate,
       CONCAT_WS(' ', c.FirstName, c.LastName) AS customer_name,
       TRIM(c.City)                            AS City,
       o.Total_Order_Amount
FROM Orders AS o
JOIN Customers AS c ON c.CustomerID = o.CustomerID
WHERE o.OrderDate >= DATE '2025-12-01'
  AND o.OrderDate <  DATE '2026-01-01'
ORDER BY o.OrderDate, o.OrderID;

-- Q17. Orders with payment type and shipper (Easy)
SELECT o.OrderID,
       o.OrderDate,
       COALESCE(pay.PaymentType, 'Unknown') AS payment_type,
       COALESCE(sh.CompanyName, 'Unknown')  AS shipper_name
FROM Orders AS o
LEFT JOIN Payments AS pay ON pay.PaymentID = o.PaymentID
LEFT JOIN Shippers AS sh  ON sh.ShipperID  = o.ShipperID
WHERE o.OrderDate >= (SELECT MAX(latest.OrderDate)::date - 6 FROM Orders AS latest)
ORDER BY o.OrderDate DESC, o.OrderID DESC;

-- Q18. Customers with no order in the last 90 days (Easy)
SELECT c.CustomerID,
       CONCAT_WS(' ', c.FirstName, c.LastName) AS customer_name,
       c.Email,
       c.DateEntered
FROM Customers AS c
LEFT JOIN Orders AS o
       ON o.CustomerID = c.CustomerID
      AND o.OrderDate >= (SELECT MAX(OrderDate) FROM Orders) - 89
WHERE o.OrderID IS NULL
ORDER BY c.DateEntered, c.CustomerID;

-- Q19. Units sold per product (Easy)
SELECT p.ProductID,
       p.Product,
       SUM(od.Quantity)           AS units_sold,
       COUNT(*)                   AS order_lines,
       COUNT(DISTINCT od.OrderID) AS orders
FROM OrderDetails AS od
JOIN Products AS p ON p.ProductID = od.ProductID
GROUP BY p.ProductID, p.Product
ORDER BY units_sold DESC NULLS LAST, p.ProductID;

-- Q20. Days to ship and days to deliver (Easy)
SELECT o.OrderID,
       o.OrderDate,
       o.ShipDate,
       o.DeliveryDate,
       o.ShipDate::date     - o.OrderDate::date AS days_to_ship,
       o.DeliveryDate::date - o.OrderDate::date AS days_to_deliver
FROM Orders AS o
WHERE o.OrderDate >= DATE '2025-11-01'
  AND o.OrderDate <  DATE '2025-12-01'
ORDER BY o.OrderDate, o.OrderID;

-- Q21. Top five customers by number of orders (Easy)
SELECT top5.CustomerID,
       top5.customer_name,
       top5.orders_placed
FROM (
    SELECT o.CustomerID,
           CASE WHEN c.CustomerID IS NULL THEN 'Unknown customer'
                ELSE CONCAT_WS(' ', c.FirstName, c.LastName)
           END      AS customer_name,
           COUNT(*) AS orders_placed
    FROM Orders AS o
    LEFT JOIN Customers AS c ON c.CustomerID = o.CustomerID
    GROUP BY o.CustomerID, c.CustomerID, c.FirstName, c.LastName
    ORDER BY orders_placed DESC
    FETCH FIRST 5 ROWS WITH TIES
) AS top5
ORDER BY top5.orders_placed DESC, top5.CustomerID;

-- Q22. Orders with more than eight line items (Easy)
SELECT od.OrderID,
       COUNT(*)                     AS line_items,
       COUNT(DISTINCT od.ProductID) AS distinct_products,
       SUM(od.Quantity)             AS total_units
FROM OrderDetails AS od
GROUP BY od.OrderID
HAVING COUNT(*) > 8
ORDER BY line_items DESC, od.OrderID;

-- Q23. Chocolate or cookie products under 250, excluding sugar-free (Easy)
SELECT p.ProductID,
       p.Product,
       p.Sub_Category,
       p.Sale_Price
FROM Products AS p
WHERE (p.Sub_Category ILIKE '%chocolate%' OR p.Sub_Category ILIKE '%cookie%')
  AND p.Sale_Price < 250
  AND p.Product NOT ILIKE '%sugar%free%'
ORDER BY p.Sale_Price, p.ProductID;

-- Q24. Suppliers outside India or with no email (Easy)
SELECT s.SupplierID,
       s.CompanyName,
       s.Country,
       s.Email,
       CONCAT_WS('; ',
           CASE WHEN s.Country IS NULL                 THEN 'Country missing'
                WHEN UPPER(TRIM(s.Country)) <> 'INDIA' THEN 'Outside India'
           END,
           CASE WHEN s.Email IS NULL OR TRIM(s.Email) = '' THEN 'No email'
           END) AS issue
FROM Suppliers AS s
WHERE s.Country IS NULL
   OR UPPER(TRIM(s.Country)) <> 'INDIA'
   OR s.Email IS NULL
   OR TRIM(s.Email) = ''
ORDER BY s.SupplierID;

-- Q25. Customer sign-ups by year and quarter (Easy)
SELECT EXTRACT(YEAR FROM c.DateEntered)::int    AS signup_year,
       EXTRACT(QUARTER FROM c.DateEntered)::int AS signup_quarter,
       COUNT(*)                                 AS new_customers
FROM Customers AS c
GROUP BY EXTRACT(YEAR FROM c.DateEntered)::int,
         EXTRACT(QUARTER FROM c.DateEntered)::int
ORDER BY signup_year NULLS LAST, signup_quarter NULLS LAST;

-- Q26. List-price value by category (Medium)
SELECT CASE
           WHEN p.ProductID IS NULL    THEN 'Unknown product'
           WHEN cat.CategoryID IS NULL THEN 'Unmapped'
           ELSE cat.CategoryName
       END                               AS category_name,
       COUNT(DISTINCT od.OrderID)        AS orders,
       SUM(od.Quantity)                  AS units_sold,
       SUM(od.Quantity * p.Sale_Price)   AS list_price_value
FROM OrderDetails AS od
LEFT JOIN Products AS p   ON p.ProductID    = od.ProductID
LEFT JOIN Category AS cat ON cat.CategoryID = p.CategoryID
GROUP BY category_name
ORDER BY list_price_value DESC NULLS LAST, category_name;

-- Q27. Average order value by customer state (Medium)
SELECT COALESCE(NULLIF(TRIM(c.State), ''), 'Unknown')            AS state,
       COUNT(DISTINCT o.CustomerID)                               AS customers,
       COUNT(*)                                                   AS orders,
       SUM(o.Total_Order_Amount)                                  AS order_value,
       ROUND(SUM(o.Total_Order_Amount)
             / NULLIF(COUNT(o.Total_Order_Amount), 0), 2)        AS avg_order_value
FROM Orders AS o
LEFT JOIN Customers AS c ON c.CustomerID = o.CustomerID
GROUP BY COALESCE(NULLIF(TRIM(c.State), ''), 'Unknown')
HAVING COUNT(*) >= 10
ORDER BY avg_order_value DESC NULLS LAST, state;

-- Q28. Payment mix: share of orders and value (Medium)
SELECT COALESCE(pay.PaymentType, 'Unknown')                          AS payment_type,
       COUNT(*)                                                       AS orders,
       ROUND(100.0 * COUNT(*)
             / NULLIF((SELECT COUNT(*) FROM Orders), 0), 2)          AS pct_of_orders,
       SUM(o.Total_Order_Amount)                                      AS order_value,
       ROUND(100.0 * SUM(o.Total_Order_Amount)
             / NULLIF((SELECT SUM(Total_Order_Amount) FROM Orders), 0), 2) AS pct_of_value
FROM Orders AS o
LEFT JOIN Payments AS pay ON pay.PaymentID = o.PaymentID
GROUP BY COALESCE(pay.PaymentType, 'Unknown')
ORDER BY orders DESC, payment_type;

-- Q29. Order value and units by shipper without double counting (Medium)
WITH order_units AS (
    SELECT od.OrderID,
           SUM(od.Quantity) AS units
    FROM OrderDetails AS od
    GROUP BY od.OrderID
)
SELECT COALESCE(sh.CompanyName, 'Unknown shipper') AS shipper_name,
       COUNT(*)                                     AS orders,
       SUM(o.Total_Order_Amount)                    AS order_value,
       COALESCE(SUM(ou.units), 0)                   AS units_shipped
FROM Orders AS o
LEFT JOIN Shippers    AS sh ON sh.ShipperID = o.ShipperID
LEFT JOIN order_units AS ou ON ou.OrderID   = o.OrderID
GROUP BY COALESCE(sh.CompanyName, 'Unknown shipper')
ORDER BY order_value DESC NULLS LAST;

-- Q30. Repeat versus one-time customers (Medium)
WITH orders_per_customer AS (
    SELECT o.CustomerID,
           COUNT(*) AS orders_placed
    FROM Orders AS o
    WHERE o.CustomerID IS NOT NULL
    GROUP BY o.CustomerID
)
SELECT CASE WHEN opc.orders_placed = 1 THEN 'One-time'
            ELSE 'Repeat' END                                            AS customer_type,
       COUNT(*)                                                          AS customers,
       ROUND(100.0 * COUNT(*)
             / NULLIF((SELECT COUNT(*) FROM orders_per_customer), 0), 2) AS pct_of_customers
FROM orders_per_customer AS opc
GROUP BY CASE WHEN opc.orders_placed = 1 THEN 'One-time' ELSE 'Repeat' END
ORDER BY customer_type;

-- Q31. Customers who spend more than the average customer (Medium)
WITH customer_spend AS (
    SELECT o.CustomerID,
           SUM(o.Total_Order_Amount) AS total_spend
    FROM Orders AS o
    WHERE o.CustomerID IS NOT NULL
    GROUP BY o.CustomerID
),
benchmark AS (
    SELECT AVG(cs.total_spend) AS avg_customer_spend
    FROM customer_spend AS cs
)
SELECT cs.CustomerID,
       CASE WHEN c.CustomerID IS NULL THEN 'Unknown customer'
            ELSE CONCAT_WS(' ', c.FirstName, c.LastName) END                  AS customer_name,
       cs.total_spend,
       ROUND(b.avg_customer_spend, 2)                                         AS avg_customer_spend,
       ROUND(100.0 * (cs.total_spend - b.avg_customer_spend)
             / NULLIF(b.avg_customer_spend, 0), 2)                            AS pct_above_avg
FROM customer_spend AS cs
CROSS JOIN benchmark AS b
LEFT JOIN Customers AS c ON c.CustomerID = cs.CustomerID
WHERE cs.total_spend > (SELECT avg_customer_spend FROM benchmark)
ORDER BY cs.total_spend DESC, cs.CustomerID;

-- Q32. Products priced above their category average (Medium)
SELECT p.ProductID,
       p.Product,
       p.CategoryID,
       p.Sale_Price,
       ROUND((SELECT AVG(p2.Sale_Price)
              FROM Products AS p2
              WHERE p2.CategoryID = p.CategoryID), 2) AS category_avg_price
FROM Products AS p
WHERE p.CategoryID = 5009
  AND p.Sale_Price > (SELECT AVG(p2.Sale_Price)
                      FROM Products AS p2
                      WHERE p2.CategoryID = p.CategoryID)
ORDER BY p.CategoryID, p.Sale_Price DESC, p.ProductID;

-- Q33. Products that have never been ordered (Medium)
SELECT p.ProductID,
       p.Product,
       p.Brand,
       p.CategoryID,
       p.Sale_Price
FROM Products AS p
WHERE NOT EXISTS (
    SELECT 1
    FROM OrderDetails AS od
    WHERE od.ProductID = p.ProductID
)
ORDER BY p.CategoryID, p.ProductID;

-- Q34. Each supplier's share of units supplied (Medium)
SELECT COALESCE(s.SupplierID, od.SupplierID)                         AS SupplierID,
       COALESCE(s.CompanyName, 'Unknown supplier')                   AS CompanyName,
       COALESCE(SUM(od.Quantity), 0)                                 AS units_supplied,
       ROUND(100.0 * COALESCE(SUM(od.Quantity), 0)
             / NULLIF(SUM(SUM(od.Quantity)) OVER (), 0), 2)          AS pct_of_units
FROM Suppliers AS s
FULL OUTER JOIN OrderDetails AS od ON od.SupplierID = s.SupplierID
GROUP BY COALESCE(s.SupplierID, od.SupplierID), s.CompanyName
ORDER BY units_supplied DESC, SupplierID NULLS LAST;

-- Q35. Late-delivery rate by shipper (Medium)
WITH classified AS (
    SELECT COALESCE(sh.CompanyName, 'Unknown shipper') AS shipper_name,
           CASE
               WHEN o.DeliveryDate IS NULL                       THEN 'Not delivered'
               WHEN o.DeliveryDate < o.OrderDate
                 OR o.ShipDate     < o.OrderDate
                 OR o.DeliveryDate < o.ShipDate                  THEN 'Invalid dates'
               WHEN o.DeliveryDate::date - o.OrderDate::date > 7 THEN 'Late'
               ELSE 'On time'
           END AS delivery_status
    FROM Orders AS o
    LEFT JOIN Shippers AS sh ON sh.ShipperID = o.ShipperID
)
SELECT shipper_name,
       COUNT(*) FILTER (WHERE delivery_status IN ('Late', 'On time')) AS delivered_orders,
       COUNT(*) FILTER (WHERE delivery_status = 'Late')               AS late_orders,
       ROUND(100.0 * COUNT(*) FILTER (WHERE delivery_status = 'Late')
             / NULLIF(COUNT(*) FILTER (WHERE delivery_status IN ('Late', 'On time')), 0), 2)
                                                                      AS late_rate_pct,
       COUNT(*) FILTER (WHERE delivery_status = 'Not delivered')      AS not_delivered,
       COUNT(*) FILTER (WHERE delivery_status = 'Invalid dates')      AS invalid_dates
FROM classified
GROUP BY shipper_name
ORDER BY late_rate_pct DESC NULLS LAST, shipper_name;

-- Q36. Payment method mix by month as columns (Medium)
SELECT DATE_TRUNC('month', o.OrderDate)::date                               AS order_month,
       COUNT(*) FILTER (WHERE pay.PaymentType = 'UPI')                      AS upi,
       COUNT(*) FILTER (WHERE pay.PaymentType = 'Credit Card')              AS credit_card,
       COUNT(*) FILTER (WHERE pay.PaymentType = 'Debit Card')               AS debit_card,
       COUNT(*) FILTER (WHERE pay.PaymentType = 'Net Banking')              AS net_banking,
       COUNT(*) FILTER (WHERE pay.PaymentType = 'Cash on Delivery')         AS cash_on_delivery,
       COUNT(*) FILTER (WHERE pay.PaymentType = 'Wallet')                   AS wallet,
       COUNT(*) FILTER (WHERE pay.PaymentType IS NULL
                           OR pay.PaymentType NOT IN ('UPI', 'Credit Card', 'Debit Card',
                                                      'Net Banking', 'Cash on Delivery', 'Wallet'))
                                                                            AS other_or_unknown,
       COUNT(*)                                                             AS total_orders
FROM Orders AS o
LEFT JOIN Payments AS pay ON pay.PaymentID = o.PaymentID
WHERE o.OrderDate IS NOT NULL
GROUP BY DATE_TRUNC('month', o.OrderDate)
ORDER BY order_month DESC;

-- Q37. Prove no order was paid with a method that is not allowed (Medium)
WITH usage AS (
    SELECT o.PaymentID,
           COUNT(*)                  AS orders,
           SUM(o.Total_Order_Amount) AS order_value
    FROM Orders AS o
    GROUP BY o.PaymentID
),
checked AS (
    SELECT pay.PaymentID,
           pay.PaymentType,
           pay.Allowed                                                         AS allowed_raw,
           COALESCE(UPPER(TRIM(CAST(pay.Allowed AS VARCHAR)))
                    IN ('1', 'TRUE', 'T', 'Y', 'YES'), FALSE)                  AS is_allowed,
           COALESCE(u.orders, 0)                                               AS orders,
           COALESCE(u.order_value, 0)                                          AS order_value
    FROM Payments AS pay
    LEFT JOIN usage AS u ON u.PaymentID = pay.PaymentID
)
SELECT ch.PaymentID,
       ch.PaymentType,
       ch.allowed_raw,
       ch.is_allowed,
       ch.orders,
       ch.order_value,
       CASE WHEN NOT ch.is_allowed AND ch.orders > 0 THEN 'VIOLATION: not allowed but used'
            WHEN NOT ch.is_allowed                   THEN 'Not allowed, unused'
            WHEN ch.orders = 0                       THEN 'Allowed, unused'
            ELSE 'OK'
       END AS status
FROM checked AS ch
ORDER BY (NOT ch.is_allowed AND ch.orders > 0) DESC, ch.PaymentID;

-- Q38. Products from inactive categories that still sold in the latest year (Medium)
WITH latest_year AS (
    SELECT DATE_TRUNC('year', MAX(o.OrderDate))::date AS year_start
    FROM Orders AS o
)
SELECT p.ProductID,
       p.Product,
       cat.CategoryName,
       SUM(od.Quantity)  AS units_latest_year,
       MAX(o.OrderDate)  AS last_order_date
FROM OrderDetails AS od
JOIN Orders       AS o   ON o.OrderID      = od.OrderID
JOIN Products     AS p   ON p.ProductID    = od.ProductID
JOIN Category     AS cat ON cat.CategoryID = p.CategoryID
CROSS JOIN latest_year AS ly
WHERE (UPPER(TRIM(CAST(cat.Active AS VARCHAR))) IN ('1', 'TRUE', 'T', 'Y', 'YES')) IS NOT TRUE
  AND o.OrderDate >= ly.year_start
  AND o.OrderDate <  ly.year_start + INTERVAL '1 year'
GROUP BY p.ProductID, p.Product, cat.CategoryName
ORDER BY units_latest_year DESC NULLS LAST, p.ProductID;

-- Q39. Categories with no products, and categories with products but no sales (Medium)
SELECT cat.CategoryID,
       cat.CategoryName,
       COUNT(DISTINCT p.ProductID)    AS product_count,
       COUNT(DISTINCT od.ProductID)   AS products_sold,
       COALESCE(SUM(od.Quantity), 0)  AS units_sold,
       CASE
           WHEN COUNT(DISTINCT p.ProductID) = 0                           THEN 'No products'
           WHEN COUNT(DISTINCT od.ProductID) = 0                          THEN 'Products but no sales'
           WHEN COUNT(DISTINCT od.ProductID) < COUNT(DISTINCT p.ProductID) THEN 'Some products unsold'
           ELSE 'All products sold'
       END                            AS status
FROM Category AS cat
LEFT JOIN Products     AS p  ON p.CategoryID = cat.CategoryID
LEFT JOIN OrderDetails AS od ON od.ProductID = p.ProductID
GROUP BY cat.CategoryID, cat.CategoryName
ORDER BY COUNT(DISTINCT od.ProductID)::numeric
         / NULLIF(COUNT(DISTINCT p.ProductID), 0) NULLS FIRST,
         cat.CategoryID;

-- Q40. Days from sign-up to first order (Medium)
WITH first_orders AS (
    SELECT o.CustomerID,
           MIN(o.OrderDate) AS first_order_date
    FROM Orders AS o
    GROUP BY o.CustomerID
)
SELECT c.CustomerID,
       c.DateEntered,
       fo.first_order_date,
       fo.first_order_date::date - c.DateEntered::date            AS days_to_first_order,
       CASE WHEN fo.first_order_date::date < c.DateEntered::date
            THEN 'Order before sign-up' END                       AS data_flag
FROM Customers AS c
JOIN first_orders AS fo ON fo.CustomerID = c.CustomerID
ORDER BY days_to_first_order NULLS LAST, c.CustomerID;

-- Q41. Most expensive product in each category (Medium)
WITH ranked AS (
    SELECT p.ProductID,
           p.Product,
           p.CategoryID,
           p.Sale_Price,
           RANK() OVER (PARTITION BY p.CategoryID
                        ORDER BY p.Sale_Price DESC NULLS LAST) AS price_rank
    FROM Products AS p
    WHERE p.Sale_Price IS NOT NULL
)
SELECT COALESCE(cat.CategoryName, 'Unmapped') AS CategoryName,
       r.ProductID,
       r.Product,
       r.Sale_Price
FROM ranked AS r
LEFT JOIN Category AS cat ON cat.CategoryID = r.CategoryID
WHERE r.price_rank = 1
ORDER BY CategoryName, r.ProductID;

-- Q42. RANK vs DENSE_RANK vs ROW_NUMBER on order counts (Medium)
WITH customer_orders AS (
    SELECT o.CustomerID,
           COUNT(*) AS orders_placed
    FROM Orders AS o
    WHERE o.CustomerID IS NOT NULL
    GROUP BY o.CustomerID
)
SELECT co.CustomerID,
       co.orders_placed,
       ROW_NUMBER() OVER (ORDER BY co.orders_placed DESC, co.CustomerID) AS row_num,
       RANK()       OVER (ORDER BY co.orders_placed DESC)                AS rank_num,
       DENSE_RANK() OVER (ORDER BY co.orders_placed DESC)                AS dense_rank_num
FROM customer_orders AS co
ORDER BY row_num;

-- Q43. Month-to-date order value for the latest three months (Medium)
WITH bounds AS (
    SELECT (DATE_TRUNC('month', MAX(o.OrderDate)) - INTERVAL '2 months')::date AS start_month,
           (DATE_TRUNC('month', MAX(o.OrderDate)) + INTERVAL '1 month')::date  AS end_month
    FROM Orders AS o
),
daily AS (
    SELECT o.OrderDate::date             AS order_date,
           SUM(o.Total_Order_Amount)     AS daily_order_value
    FROM Orders AS o
    CROSS JOIN bounds AS b
    WHERE o.OrderDate >= b.start_month
      AND o.OrderDate <  b.end_month
    GROUP BY o.OrderDate::date
)
SELECT d.order_date,
       d.daily_order_value,
       SUM(d.daily_order_value) OVER (
           PARTITION BY DATE_TRUNC('month', d.order_date)
           ORDER BY d.order_date
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS month_to_date_value
FROM daily AS d
ORDER BY d.order_date;

-- Q44. Month-over-month growth in order value (Medium)
WITH monthly AS (
    SELECT DATE_TRUNC('month', o.OrderDate)::date AS order_month,
           SUM(o.Total_Order_Amount)              AS order_value
    FROM Orders AS o
    WHERE o.OrderDate IS NOT NULL
    GROUP BY DATE_TRUNC('month', o.OrderDate)::date
),
with_prev AS (
    SELECT m.order_month,
           m.order_value,
           CASE WHEN LAG(m.order_month) OVER w = m.order_month - INTERVAL '1 month'
                THEN LAG(m.order_value) OVER w
           END AS prev_month_value
    FROM monthly AS m
    WINDOW w AS (ORDER BY m.order_month)
)
SELECT wp.order_month,
       wp.order_value,
       wp.prev_month_value,
       wp.order_value - wp.prev_month_value AS mom_change,
       ROUND(100.0 * (wp.order_value - wp.prev_month_value)
             / NULLIF(wp.prev_month_value, 0), 2) AS mom_growth_pct
FROM with_prev AS wp
ORDER BY wp.order_month;

-- Q45. Typical gap between a customer's orders (Medium)
WITH order_gaps AS (
    SELECT o.CustomerID,
           o.OrderID,
           o.OrderDate::date
             - LAG(o.OrderDate::date) OVER (PARTITION BY o.CustomerID
                                            ORDER BY o.OrderDate, o.OrderID) AS gap_days
    FROM Orders AS o
    WHERE o.OrderDate IS NOT NULL
)
SELECT og.CustomerID,
       COUNT(*)                  AS orders,
       ROUND(AVG(og.gap_days), 2) AS avg_gap_days,
       MAX(og.gap_days)          AS max_gap_days
FROM order_gaps AS og
GROUP BY og.CustomerID
HAVING COUNT(*) >= 3
ORDER BY avg_gap_days, og.CustomerID;

-- Q46. Same-brand products where one costs at least twice the other (Medium)
SELECT cheap.Brand,
       cheap.Sub_Category,
       cheap.Product     AS cheaper_product,
       cheap.Sale_Price  AS cheaper_price,
       pricey.Product    AS pricier_product,
       pricey.Sale_Price AS pricier_price,
       ROUND(pricey.Sale_Price / NULLIF(cheap.Sale_Price, 0), 2) AS price_ratio
FROM Products AS cheap
JOIN Products AS pricey
  ON  pricey.Brand        = cheap.Brand
  AND pricey.Sub_Category = cheap.Sub_Category
  AND pricey.Sale_Price  >= 2 * cheap.Sale_Price
WHERE cheap.Sale_Price > 0
  AND NULLIF(TRIM(cheap.Brand), '') IS NOT NULL
ORDER BY price_ratio DESC, cheap.Brand, cheap.ProductID, pricey.ProductID;

-- Q47. Brands with at least three products, and how much they sold (Medium)
SELECT COALESCE(NULLIF(TRIM(p.Brand), ''), 'Unbranded')               AS Brand,
       COUNT(DISTINCT p.ProductID)                  AS products_listed,
       COUNT(DISTINCT od.ProductID)                 AS products_sold,
       COALESCE(SUM(od.Quantity), 0)                AS units_sold,
       COALESCE(SUM(od.Quantity * p.Sale_Price), 0) AS list_price_value
FROM Products AS p
LEFT JOIN OrderDetails AS od ON od.ProductID = p.ProductID
GROUP BY COALESCE(NULLIF(TRIM(p.Brand), ''), 'Unbranded')
HAVING COUNT(DISTINCT p.ProductID) >= 3
ORDER BY list_price_value DESC, Brand;

-- Q48. Do discounted products sell more? (Medium)
WITH product_units AS (
    SELECT od.ProductID,
           SUM(od.Quantity) AS units
    FROM OrderDetails AS od
    GROUP BY od.ProductID
),
priced AS (
    SELECT p.ProductID,
           100.0 * (p.Market_Price - p.Sale_Price) / NULLIF(p.Market_Price, 0) AS discount_pct,
           pu.units
    FROM Products AS p
    LEFT JOIN product_units AS pu ON pu.ProductID = p.ProductID
),
banded AS (
    SELECT pr.ProductID,
           CASE WHEN pr.discount_pct IS NULL THEN 'Unknown'
                WHEN pr.discount_pct <= 0    THEN 'Full price'
                WHEN pr.discount_pct <= 10   THEN 'Up to 10%'
                WHEN pr.discount_pct <= 25   THEN '10% to 25%'
                ELSE 'Over 25%'
           END AS discount_band,
           CASE WHEN pr.discount_pct IS NULL THEN 5
                WHEN pr.discount_pct <= 0    THEN 1
                WHEN pr.discount_pct <= 10   THEN 2
                WHEN pr.discount_pct <= 25   THEN 3
                ELSE 4
           END AS band_order,
           pr.units IS NOT NULL      AS has_sold,
           COALESCE(pr.units, 0)     AS units
    FROM priced AS pr
)
SELECT b.discount_band,
       COUNT(*)                         AS products,
       COUNT(*) FILTER (WHERE b.has_sold) AS products_sold,
       ROUND(AVG(b.units), 2)           AS avg_units_per_product,
       SUM(b.units)                     AS total_units
FROM banded AS b
GROUP BY b.discount_band, b.band_order
ORDER BY b.band_order;

-- Q49. Top three products by units in each category (Medium)
WITH product_units AS (
    SELECT p.CategoryID,
           p.ProductID,
           p.Product,
           SUM(od.Quantity) AS units_sold
    FROM OrderDetails AS od
    JOIN Products     AS p ON p.ProductID = od.ProductID
    GROUP BY p.CategoryID, p.ProductID, p.Product
),
ranked AS (
    SELECT pu.CategoryID,
           pu.ProductID,
           pu.Product,
           pu.units_sold,
           DENSE_RANK() OVER (PARTITION BY pu.CategoryID
                              ORDER BY pu.units_sold DESC NULLS LAST) AS product_rank
    FROM product_units AS pu
)
SELECT COALESCE(cat.CategoryName, 'Unmapped') AS CategoryName,
       r.product_rank,
       r.ProductID,
       r.Product,
       r.units_sold
FROM ranked AS r
LEFT JOIN Category AS cat ON cat.CategoryID = r.CategoryID
WHERE r.product_rank <= 3
ORDER BY CategoryName, r.product_rank, r.ProductID;

-- Q50. Customers who buy across at least ten categories (Medium)
SELECT o.CustomerID,
       COUNT(DISTINCT p.CategoryID) AS categories_bought,
       ARRAY_TO_STRING(ARRAY_AGG(DISTINCT p.CategoryID ORDER BY p.CategoryID), ', ') AS category_ids,
       COUNT(DISTINCT o.OrderID)    AS orders
FROM Orders       AS o
JOIN OrderDetails AS od ON od.OrderID  = o.OrderID
JOIN Products     AS p  ON p.ProductID = od.ProductID
WHERE p.CategoryID IS NOT NULL
GROUP BY o.CustomerID
HAVING COUNT(DISTINCT p.CategoryID) >= 10
ORDER BY categories_bought DESC, orders DESC, o.CustomerID;

-- Q51. Orders fulfilled by one supplier vs several (Medium)
WITH order_suppliers AS (
    SELECT od.OrderID,
           COUNT(DISTINCT od.SupplierID) AS suppliers
    FROM OrderDetails AS od
    GROUP BY od.OrderID
)
SELECT CASE WHEN os.suppliers = 0 THEN 'No supplier recorded'
            WHEN os.suppliers = 1 THEN 'Single supplier'
            WHEN os.suppliers = 2 THEN '2 suppliers'
            ELSE '3+ suppliers'
       END                                                   AS supplier_mix,
       COUNT(*)                                              AS orders,
       ROUND(100.0 * COUNT(*) / NULLIF(SUM(COUNT(*)) OVER (), 0), 2) AS pct_of_orders
FROM order_suppliers AS os
GROUP BY 1
ORDER BY MIN(os.suppliers);

-- Q52. Where shipping time goes: dispatch vs transit by shipper (Medium)
WITH order_timing AS (
    SELECT o.OrderID,
           o.ShipperID,
           o.ShipDate::date     - o.OrderDate::date AS days_to_ship,
           o.DeliveryDate::date - o.ShipDate::date  AS days_in_transit,
           o.DeliveryDate::date - o.OrderDate::date AS days_total,
           (o.OrderDate IS NOT NULL AND o.ShipDate IS NOT NULL AND o.DeliveryDate IS NOT NULL
            AND o.ShipDate >= o.OrderDate AND o.DeliveryDate >= o.ShipDate) AS is_measurable
    FROM Orders AS o
)
SELECT COALESCE(sh.CompanyName, 'Unknown shipper')                        AS shipper_name,
       COUNT(*) FILTER (WHERE ot.is_measurable)                           AS orders_measured,
       ROUND(AVG(ot.days_to_ship)    FILTER (WHERE ot.is_measurable), 2)  AS avg_days_to_ship,
       ROUND(AVG(ot.days_in_transit) FILTER (WHERE ot.is_measurable), 2)  AS avg_days_in_transit,
       ROUND(AVG(ot.days_total)      FILTER (WHERE ot.is_measurable), 2)  AS avg_days_total,
       COUNT(*) FILTER (WHERE NOT ot.is_measurable)                       AS orders_excluded
FROM order_timing AS ot
LEFT JOIN Shippers AS sh ON sh.ShipperID = ot.ShipperID
GROUP BY COALESCE(sh.CompanyName, 'Unknown shipper')
ORDER BY avg_days_total DESC NULLS LAST, shipper_name;

-- Q53. Thirty-day sign-up to purchase conversion by country (Medium)
WITH first_orders AS (
    SELECT o.CustomerID,
           MIN(o.OrderDate) AS first_order_date
    FROM Orders AS o
    GROUP BY o.CustomerID
)
SELECT COALESCE(NULLIF(TRIM(c.Country), ''), 'Unknown')                AS country,
       COUNT(*)                                                         AS customers,
       COUNT(*) FILTER (WHERE fo.first_order_date::date - c.DateEntered::date
                              BETWEEN 0 AND 30)                         AS converted_30d,
       ROUND(100.0 * COUNT(*) FILTER (WHERE fo.first_order_date::date - c.DateEntered::date
                                            BETWEEN 0 AND 30)
             / NULLIF(COUNT(*), 0), 2)                                  AS conversion_30d_pct
FROM Customers AS c
LEFT JOIN first_orders AS fo ON fo.CustomerID = c.CustomerID
GROUP BY COALESCE(NULLIF(TRIM(c.Country), ''), 'Unknown')
ORDER BY conversion_30d_pct, country;

-- Q54. Weighted vs simple average discount by sub-category (Medium)
WITH product_units AS (
    SELECT od.ProductID,
           SUM(od.Quantity) AS units
    FROM OrderDetails AS od
    GROUP BY od.ProductID
),
product_discount AS (
    SELECT COALESCE(p.Sub_Category, 'Unknown')                  AS Sub_Category,
           100.0 * (p.Market_Price - p.Sale_Price) / p.Market_Price AS discount_pct,
           COALESCE(pu.units, 0)                                 AS units
    FROM Products AS p
    LEFT JOIN product_units AS pu ON pu.ProductID = p.ProductID
    WHERE p.Market_Price > 0
      AND p.Sale_Price <= p.Market_Price
),
by_sub AS (
    SELECT pd.Sub_Category,
           COUNT(*)                     AS products,
           ROUND(AVG(pd.discount_pct), 2) AS simple_avg_discount_pct,
           SUM(pd.units)                AS units_sold,
           ROUND(SUM(pd.discount_pct * pd.units) / NULLIF(SUM(pd.units), 0), 2)
                                        AS unit_weighted_discount_pct
    FROM product_discount AS pd
    GROUP BY pd.Sub_Category
)
SELECT bs.Sub_Category,
       bs.products,
       bs.simple_avg_discount_pct,
       bs.units_sold,
       bs.unit_weighted_discount_pct
FROM by_sub AS bs
ORDER BY ABS(bs.unit_weighted_discount_pct - bs.simple_avg_discount_pct) DESC NULLS LAST,
         bs.Sub_Category;

-- Q55. Category list-price value: latest year vs previous year (Medium)
WITH anchor AS (
    SELECT DATE_TRUNC('year', MAX(o.OrderDate))::date AS latest_year_start
    FROM Orders AS o
),
line_values AS (
    SELECT COALESCE(cat.CategoryName, 'Unmapped') AS CategoryName,
           o.OrderDate >= a.latest_year_start     AS is_latest_year,
           od.Quantity * p.Sale_Price             AS list_price_value
    FROM Orders AS o
    CROSS JOIN anchor AS a
    JOIN OrderDetails  AS od  ON od.OrderID    = o.OrderID
    JOIN Products      AS p   ON p.ProductID   = od.ProductID
    LEFT JOIN Category AS cat ON cat.CategoryID = p.CategoryID
    WHERE o.OrderDate >= a.latest_year_start - INTERVAL '1 year'
      AND o.OrderDate <  a.latest_year_start + INTERVAL '1 year'
),
by_category AS (
    SELECT lv.CategoryName,
           COALESCE(SUM(lv.list_price_value) FILTER (WHERE NOT lv.is_latest_year), 0) AS prev_year_value,
           COALESCE(SUM(lv.list_price_value) FILTER (WHERE lv.is_latest_year), 0)     AS latest_year_value
    FROM line_values AS lv
    GROUP BY lv.CategoryName
)
SELECT bc.CategoryName,
       bc.prev_year_value,
       bc.latest_year_value,
       ROUND(100.0 * (bc.latest_year_value - bc.prev_year_value)
             / NULLIF(bc.prev_year_value, 0), 2) AS yoy_growth_pct
FROM by_category AS bc
ORDER BY yoy_growth_pct DESC NULLS LAST, bc.CategoryName;

-- Q56. Customers who ordered last year but not this year (Medium)
WITH anchor AS (
    SELECT DATE_TRUNC('year', MAX(o.OrderDate))::date AS latest_year_start
    FROM Orders AS o
),
lapsed AS (
    SELECT o.CustomerID
    FROM Orders AS o
    CROSS JOIN anchor AS a
    WHERE o.OrderDate >= a.latest_year_start - INTERVAL '1 year'
      AND o.OrderDate <  a.latest_year_start
    EXCEPT
    SELECT o.CustomerID
    FROM Orders AS o
    CROSS JOIN anchor AS a
    WHERE o.OrderDate >= a.latest_year_start
)
SELECT l.CustomerID,
       COALESCE(NULLIF(CONCAT_WS(' ', c.FirstName, c.LastName), ''), 'Unknown customer') AS customer_name,
       MAX(o.OrderDate)                                                                  AS last_order_date,
       COUNT(*) FILTER (WHERE o.OrderDate >= a.latest_year_start - INTERVAL '1 year')    AS orders_prev_year
FROM lapsed AS l
CROSS JOIN anchor AS a
JOIN Orders         AS o ON o.CustomerID = l.CustomerID
LEFT JOIN Customers AS c ON c.CustomerID = l.CustomerID
GROUP BY l.CustomerID, c.FirstName, c.LastName
ORDER BY last_order_date DESC, l.CustomerID;

-- Q57. One contact directory for suppliers and shippers (Medium)
SELECT 'Supplier'    AS partner_type,
       s.SupplierID  AS partner_id,
       s.CompanyName AS company_name,
       s.Phone       AS phone,
       s.Email       AS email,
       s.Country     AS country
FROM Suppliers AS s
UNION ALL
SELECT 'Shipper',
       sh.ShipperID,
       sh.CompanyName,
       sh.Phone,
       CAST(NULL AS VARCHAR(120)),
       CAST(NULL AS VARCHAR(60))
FROM Shippers AS sh
ORDER BY company_name, partner_type, partner_id;

-- Q58. Each customer's latest order (Medium)
WITH numbered AS (
    SELECT o.CustomerID,
           o.OrderID,
           o.OrderDate,
           o.Total_Order_Amount,
           ROW_NUMBER() OVER (PARTITION BY o.CustomerID
                              ORDER BY o.OrderDate DESC NULLS LAST, o.OrderID DESC) AS rn
    FROM Orders AS o
)
SELECT n.CustomerID,
       COALESCE(NULLIF(CONCAT_WS(' ', c.FirstName, c.LastName), ''), 'Unknown customer') AS customer_name,
       n.OrderID            AS latest_order_id,
       n.OrderDate          AS latest_order_date,
       n.Total_Order_Amount AS latest_order_amount
FROM numbered AS n
LEFT JOIN Customers AS c ON c.CustomerID = n.CustomerID
WHERE n.rn = 1
ORDER BY n.OrderDate DESC NULLS LAST, n.CustomerID;

-- Q59. Basket size by month (Medium)
WITH order_baskets AS (
    SELECT od.OrderID,
           SUM(od.Quantity)             AS units,
           COUNT(DISTINCT od.ProductID) AS distinct_products
    FROM OrderDetails AS od
    GROUP BY od.OrderID
)
SELECT DATE_TRUNC('month', o.OrderDate)::date      AS order_month,
       COUNT(*)                                    AS orders_with_lines,
       ROUND(AVG(ob.units), 2)                     AS avg_units_per_order,
       ROUND(AVG(ob.distinct_products), 2)         AS avg_distinct_products_per_order
FROM Orders AS o
JOIN order_baskets AS ob ON ob.OrderID = o.OrderID
WHERE o.OrderDate IS NOT NULL
GROUP BY DATE_TRUNC('month', o.OrderDate)::date
ORDER BY order_month;

-- Q60. Sub-category share of its category (Medium)
SELECT COALESCE(cat.CategoryName, 'Unmapped') AS CategoryName,
       COALESCE(p.Sub_Category, 'Unknown')    AS Sub_Category,
       SUM(od.Quantity * p.Sale_Price)        AS list_price_value,
       ROUND(100.0 * SUM(od.Quantity * p.Sale_Price)
             / NULLIF(SUM(SUM(od.Quantity * p.Sale_Price))
                      OVER (PARTITION BY COALESCE(cat.CategoryName, 'Unmapped')), 0), 2)
                                              AS pct_of_category
FROM OrderDetails AS od
JOIN Products      AS p   ON p.ProductID    = od.ProductID
LEFT JOIN Category AS cat ON cat.CategoryID = p.CategoryID
GROUP BY COALESCE(cat.CategoryName, 'Unmapped'), COALESCE(p.Sub_Category, 'Unknown')
ORDER BY CategoryName, pct_of_category DESC NULLS LAST, Sub_Category;

-- Q61. Monthly cohort retention (Hard)
WITH customer_month AS (
    SELECT DISTINCT o.CustomerID,
           DATE_TRUNC('month', o.OrderDate)::date AS activity_month
    FROM Orders AS o
    WHERE o.CustomerID IS NOT NULL
      AND o.OrderDate  IS NOT NULL
),
cohort AS (
    SELECT cm.CustomerID,
           MIN(cm.activity_month) AS cohort_month
    FROM customer_month AS cm
    GROUP BY cm.CustomerID
),
activity AS (
    SELECT co.cohort_month,
           cm.CustomerID,
           (EXTRACT(YEAR  FROM cm.activity_month) - EXTRACT(YEAR  FROM co.cohort_month)) * 12
         + (EXTRACT(MONTH FROM cm.activity_month) - EXTRACT(MONTH FROM co.cohort_month)) AS month_number
    FROM customer_month AS cm
    JOIN cohort         AS co ON co.CustomerID = cm.CustomerID
),
cohort_counts AS (
    SELECT a.cohort_month,
           COUNT(*) FILTER (WHERE a.month_number = 0) AS cohort_size,
           COUNT(*) FILTER (WHERE a.month_number = 1) AS m1_customers,
           COUNT(*) FILTER (WHERE a.month_number = 2) AS m2_customers,
           COUNT(*) FILTER (WHERE a.month_number = 3) AS m3_customers,
           COUNT(*) FILTER (WHERE a.month_number = 6) AS m6_customers
    FROM activity AS a
    GROUP BY a.cohort_month
),
anchor AS (
    -- first month the data does not fully cover
    SELECT DATE_TRUNC('month', MAX(o.OrderDate)::date + 1)::date AS first_open_month
    FROM Orders AS o
)
SELECT cc.cohort_month,
       cc.cohort_size,
       CASE WHEN cc.cohort_month + INTERVAL '1 month'  < an.first_open_month
            THEN ROUND(100.0 * cc.m1_customers / NULLIF(cc.cohort_size, 0), 2) END AS m1_pct,
       CASE WHEN cc.cohort_month + INTERVAL '2 months' < an.first_open_month
            THEN ROUND(100.0 * cc.m2_customers / NULLIF(cc.cohort_size, 0), 2) END AS m2_pct,
       CASE WHEN cc.cohort_month + INTERVAL '3 months' < an.first_open_month
            THEN ROUND(100.0 * cc.m3_customers / NULLIF(cc.cohort_size, 0), 2) END AS m3_pct,
       CASE WHEN cc.cohort_month + INTERVAL '6 months' < an.first_open_month
            THEN ROUND(100.0 * cc.m6_customers / NULLIF(cc.cohort_size, 0), 2) END AS m6_pct
FROM cohort_counts AS cc
CROSS JOIN anchor  AS an
ORDER BY cc.cohort_month;

-- Q62. Which products make up 80% of list-price value (Pareto) (Hard)
WITH product_value AS (
    SELECT p.ProductID,
           p.Product,
           SUM(od.Quantity * p.Sale_Price) AS list_price_value
    FROM OrderDetails AS od
    JOIN Products     AS p ON p.ProductID = od.ProductID
    GROUP BY p.ProductID, p.Product
    HAVING SUM(od.Quantity * p.Sale_Price) > 0
),
running AS (
    SELECT pv.ProductID,
           pv.Product,
           pv.list_price_value,
           SUM(pv.list_price_value) OVER () AS total_value,
           SUM(pv.list_price_value) OVER (
               ORDER BY pv.list_price_value DESC, pv.ProductID
               ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
           )                                AS running_value
    FROM product_value AS pv
)
SELECT r.ProductID,
       r.Product,
       r.list_price_value,
       ROUND(100.0 * r.list_price_value / NULLIF(r.total_value, 0), 2) AS pct_of_total,
       ROUND(100.0 * r.running_value    / NULLIF(r.total_value, 0), 2) AS cumulative_pct,
       CASE WHEN r.running_value - r.list_price_value < 0.8 * r.total_value
            THEN 'Top 80%'
            ELSE 'Long tail'
       END                                                             AS pareto_group
FROM running AS r
ORDER BY r.list_price_value DESC, r.ProductID;

-- Q63. RFM segmentation (Hard)
WITH anchor AS (
    SELECT MAX(o.OrderDate)::date AS as_of_date
    FROM Orders AS o
),
customer_stats AS (
    SELECT c.CustomerID,
           a.as_of_date - MAX(o.OrderDate)::date  AS recency_days,
           COUNT(*)                               AS frequency,
           COALESCE(SUM(o.Total_Order_Amount), 0) AS monetary
    FROM Orders    AS o
    JOIN Customers AS c ON c.CustomerID = o.CustomerID
    CROSS JOIN anchor AS a
    WHERE o.OrderDate IS NOT NULL
    GROUP BY c.CustomerID, a.as_of_date
),
raw_scores AS (
    SELECT cs.CustomerID,
           cs.recency_days,
           cs.frequency,
           cs.monetary,
           NTILE(5) OVER (ORDER BY cs.recency_days DESC, cs.CustomerID) AS r_raw,
           NTILE(5) OVER (ORDER BY cs.frequency,         cs.CustomerID) AS f_raw,
           NTILE(5) OVER (ORDER BY cs.monetary,          cs.CustomerID) AS m_raw
    FROM customer_stats AS cs
),
scores AS (
    SELECT rs.CustomerID,
           rs.recency_days,
           rs.frequency,
           rs.monetary,
           MIN(rs.r_raw) OVER (PARTITION BY rs.recency_days) AS r_score,
           MIN(rs.f_raw) OVER (PARTITION BY rs.frequency)    AS f_score,
           MIN(rs.m_raw) OVER (PARTITION BY rs.monetary)     AS m_score
    FROM raw_scores AS rs
)
SELECT s.CustomerID,
       s.recency_days,
       s.frequency,
       s.monetary,
       s.r_score,
       s.f_score,
       s.m_score,
       CASE
           WHEN s.r_score >= 4 AND s.f_score >= 4 AND s.m_score >= 4 THEN 'Champions'
           WHEN s.r_score >= 3 AND s.f_score >= 4                    THEN 'Loyal'
           WHEN s.r_score >= 4 AND s.f_score <= 2                    THEN 'New or promising'
           WHEN s.r_score <= 2 AND s.f_score >= 3                    THEN 'At risk'
           WHEN s.r_score <= 2 AND s.f_score <= 2                    THEN 'Hibernating'
           ELSE 'Needs attention'
       END AS segment
FROM scores AS s
ORDER BY s.r_score + s.f_score + s.m_score DESC, s.monetary DESC, s.CustomerID;

-- Q64. Three-month moving average of order value, with no missing months (Hard)
WITH bounds AS (
    SELECT DATE_TRUNC('month', MIN(o.OrderDate))::date AS first_month,
           DATE_TRUNC('month', MAX(o.OrderDate))::date AS last_month
    FROM Orders AS o
),
month_spine AS (
    SELECT gs::date AS order_month
    FROM bounds AS b
    CROSS JOIN generate_series(b.first_month, b.last_month, INTERVAL '1 month') AS gs
),
monthly AS (
    SELECT DATE_TRUNC('month', o.OrderDate)::date AS order_month,
           SUM(o.Total_Order_Amount)               AS order_value
    FROM Orders AS o
    WHERE o.OrderDate IS NOT NULL
    GROUP BY DATE_TRUNC('month', o.OrderDate)::date
),
filled AS (
    SELECT ms.order_month,
           COALESCE(m.order_value, 0) AS order_value
    FROM month_spine AS ms
    LEFT JOIN monthly AS m ON m.order_month = ms.order_month
)
SELECT f.order_month,
       f.order_value,
       CASE WHEN COUNT(*) OVER w = 3
            THEN ROUND(AVG(f.order_value) OVER w, 2)
       END AS moving_avg_3m
FROM filled AS f
WINDOW w AS (ORDER BY f.order_month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)
ORDER BY f.order_month;

-- Q65. Longest run of consecutive months with an order (Hard)
WITH customer_months AS (
    SELECT DISTINCT o.CustomerID,
           DATE_TRUNC('month', o.OrderDate)::date AS order_month
    FROM Orders AS o
    WHERE o.CustomerID IS NOT NULL
      AND o.OrderDate  IS NOT NULL
),
numbered AS (
    SELECT cm.CustomerID,
           cm.order_month,
           (EXTRACT(YEAR FROM cm.order_month) * 12 + EXTRACT(MONTH FROM cm.order_month))::int AS month_index,
           ROW_NUMBER() OVER (PARTITION BY cm.CustomerID ORDER BY cm.order_month)             AS rn
    FROM customer_months AS cm
),
streaks AS (
    SELECT n.CustomerID,
           MIN(n.order_month) AS streak_start_month,
           MAX(n.order_month) AS streak_end_month,
           COUNT(*)           AS streak_months
    FROM numbered AS n
    GROUP BY n.CustomerID, n.month_index - n.rn
),
longest AS (
    SELECT s.CustomerID,
           s.streak_start_month,
           s.streak_end_month,
           s.streak_months,
           ROW_NUMBER() OVER (PARTITION BY s.CustomerID
                              ORDER BY s.streak_months DESC, s.streak_start_month DESC) AS pick
    FROM streaks AS s
),
ranked AS (
    SELECT l.CustomerID,
           l.streak_start_month,
           l.streak_end_month,
           l.streak_months,
           RANK() OVER (ORDER BY l.streak_months DESC) AS streak_rank
    FROM longest AS l
    WHERE l.pick = 1
)
SELECT r.CustomerID,
       r.streak_start_month,
       r.streak_end_month,
       r.streak_months
FROM ranked AS r
WHERE r.streak_rank <= 10
ORDER BY r.streak_months DESC, r.streak_end_month DESC, r.CustomerID;

-- Q66. How fast do customers come back for a second order? (Hard)
WITH order_days AS (
    SELECT DISTINCT o.CustomerID,
           o.OrderDate::date AS order_date
    FROM Orders AS o
    WHERE o.CustomerID IS NOT NULL
      AND o.OrderDate  IS NOT NULL
),
sequenced AS (
    SELECT od.CustomerID,
           od.order_date,
           ROW_NUMBER() OVER (PARTITION BY od.CustomerID ORDER BY od.order_date)        AS day_seq,
           LEAD(od.order_date) OVER (PARTITION BY od.CustomerID ORDER BY od.order_date) AS next_order_date
    FROM order_days AS od
),
first_orders AS (
    SELECT s.CustomerID,
           s.order_date                     AS first_order_date,
           s.next_order_date                AS second_order_date,
           s.next_order_date - s.order_date AS days_to_second
    FROM sequenced AS s
    WHERE s.day_seq = 1
)
SELECT EXTRACT(YEAR FROM fo.first_order_date)::int                          AS first_order_year,
       COUNT(*)                                                             AS customers,
       COUNT(fo.second_order_date)                                          AS customers_with_second_order,
       ROUND(100.0 * COUNT(fo.second_order_date) / NULLIF(COUNT(*), 0), 2)  AS pct_repeating,
       ROUND((PERCENTILE_CONT(0.5)  WITHIN GROUP (ORDER BY fo.days_to_second))::numeric, 1) AS median_days_to_second,
       ROUND((PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY fo.days_to_second))::numeric, 1) AS p75_days_to_second
FROM first_orders AS fo
GROUP BY EXTRACT(YEAR FROM fo.first_order_date)
ORDER BY first_order_year;

-- Q67. Median vs mean order value by payment type (Hard)
WITH payment_stats AS (
    SELECT COALESCE(pay.PaymentType, 'Unknown')                         AS payment_type,
           COUNT(o.Total_Order_Amount)                                   AS orders,
           AVG(o.Total_Order_Amount)                                     AS mean_value,
           (PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY o.Total_Order_Amount))::numeric AS median_value
    FROM Orders AS o
    LEFT JOIN Payments AS pay ON pay.PaymentID = o.PaymentID
    GROUP BY COALESCE(pay.PaymentType, 'Unknown')
)
SELECT ps.payment_type,
       ps.orders,
       ROUND(ps.mean_value, 2)                                  AS mean_order_value,
       ROUND(ps.median_value, 2)                                AS median_order_value,
       ROUND(ps.mean_value / NULLIF(ps.median_value, 0), 2)     AS mean_to_median_ratio
FROM payment_stats AS ps
WHERE ps.orders > 0
ORDER BY mean_to_median_ratio DESC NULLS LAST, ps.payment_type;

-- Q68. Second-highest spender in each state, counting delivered orders only (Hard)
WITH order_rows AS (
    SELECT o.OrderID,
           o.CustomerID,
           CASE WHEN c.CustomerID IS NULL THEN 'Unmapped customer'
                ELSE COALESCE(NULLIF(TRIM(c.State), ''), 'Unknown')
           END                                                         AS state,
           COALESCE(NULLIF(CONCAT_WS(' ', c.FirstName, c.LastName), ''), 'Unknown customer') AS customer_name,
           o.Total_Order_Amount,
           (o.DeliveryDate IS NOT NULL
            AND o.DeliveryDate::date >= o.OrderDate::date)            AS is_delivered
    FROM Orders AS o
    LEFT JOIN Customers AS c ON c.CustomerID = o.CustomerID
),
ranked AS (
    SELECT r.state,
           r.CustomerID,
           r.customer_name,
           SUM(r.Total_Order_Amount) FILTER (WHERE r.is_delivered)     AS delivered_spend,
           DENSE_RANK() OVER (
               PARTITION BY r.state
               ORDER BY SUM(r.Total_Order_Amount) FILTER (WHERE r.is_delivered) DESC
           )                                                           AS spend_rank
    FROM order_rows AS r
    GROUP BY r.state, r.CustomerID, r.customer_name
    HAVING SUM(r.Total_Order_Amount) FILTER (WHERE r.is_delivered) > 0
)
SELECT rk.state AS State,
       rk.CustomerID,
       rk.customer_name,
       rk.delivered_spend,
       rk.spend_rank
FROM ranked AS rk
WHERE rk.spend_rank = 2
ORDER BY rk.state, rk.CustomerID;

-- Q69. Customers whose spend grew every active quarter of the latest year (Hard)
WITH anchor AS (
    SELECT DATE_TRUNC('year', MAX(o.OrderDate))::date AS year_start
    FROM Orders AS o
),
quarterly AS (
    SELECT o.CustomerID,
           DATE_TRUNC('quarter', o.OrderDate)::date AS order_quarter,
           SUM(o.Total_Order_Amount)                AS quarter_spend
    FROM Orders AS o
    CROSS JOIN anchor AS a
    WHERE o.CustomerID IS NOT NULL
      AND o.OrderDate >= a.year_start
      AND o.OrderDate <  a.year_start + INTERVAL '1 year'
    GROUP BY o.CustomerID, DATE_TRUNC('quarter', o.OrderDate)::date
),
compared AS (
    SELECT q.CustomerID,
           q.order_quarter,
           q.quarter_spend,
           ROW_NUMBER() OVER w_order                AS quarter_seq,
           LAG(q.quarter_spend) OVER w_order        AS prev_spend,
           FIRST_VALUE(q.quarter_spend) OVER w_all  AS first_quarter_spend,
           LAST_VALUE(q.quarter_spend)  OVER w_all  AS last_quarter_spend
    FROM quarterly AS q
    WINDOW w_order AS (PARTITION BY q.CustomerID ORDER BY q.order_quarter),
           w_all   AS (PARTITION BY q.CustomerID ORDER BY q.order_quarter
                       ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
)
SELECT c.CustomerID,
       COUNT(*)                   AS active_quarters,
       MAX(c.first_quarter_spend) AS first_quarter_spend,
       MAX(c.last_quarter_spend)  AS last_quarter_spend
FROM compared AS c
GROUP BY c.CustomerID
HAVING COUNT(*) >= 3
   AND BOOL_AND(COALESCE(c.quarter_spend > c.prev_spend, FALSE)) FILTER (WHERE c.quarter_seq > 1)
ORDER BY last_quarter_spend DESC, c.CustomerID;

-- Q70. Sub-categories most often bought together (Hard)
WITH order_subcats AS (
    SELECT DISTINCT od.OrderID,
           p.Sub_Category
    FROM OrderDetails AS od
    JOIN Products AS p ON p.ProductID = od.ProductID
    WHERE p.Sub_Category IS NOT NULL
),
pairs AS (
    SELECT a.Sub_Category                       AS sub_category_a,
           b.Sub_Category                       AS sub_category_b,
           COUNT(*)                             AS orders_together,
           RANK() OVER (ORDER BY COUNT(*) DESC) AS pair_rank
    FROM order_subcats AS a
    JOIN order_subcats AS b
      ON b.OrderID      = a.OrderID
     AND b.Sub_Category > a.Sub_Category
    GROUP BY a.Sub_Category, b.Sub_Category
)
SELECT pr.sub_category_a,
       pr.sub_category_b,
       pr.orders_together
FROM pairs AS pr
WHERE pr.pair_rank <= 10
ORDER BY pr.orders_together DESC, pr.sub_category_a, pr.sub_category_b;

-- Q71. Deduplicate customer accounts by email (Hard)
WITH keyed AS (
    SELECT c.CustomerID,
           LOWER(TRIM(c.Email)) AS normalized_email,
           c.DateEntered,
           ROW_NUMBER() OVER (
               PARTITION BY LOWER(TRIM(c.Email))
               ORDER BY c.DateEntered NULLS LAST, c.CustomerID
           )                    AS account_rank
    FROM Customers AS c
    WHERE NULLIF(TRIM(c.Email), '') IS NOT NULL
)
SELECT d.normalized_email,
       s.CustomerID  AS survivor_customer_id,
       d.CustomerID  AS duplicate_customer_id,
       s.DateEntered AS survivor_date_entered,
       d.DateEntered AS duplicate_date_entered
FROM keyed AS d
JOIN keyed AS s
  ON s.normalized_email = d.normalized_email
 AND s.account_rank     = 1
WHERE d.account_rank > 1
ORDER BY d.normalized_email, d.CustomerID;

-- Q72. Same product on several lines of one order: split or duplicate? (Hard)
WITH repeated AS (
    SELECT od.OrderID,
           od.ProductID,
           COUNT(DISTINCT od.SupplierID) AS suppliers_in_group
    FROM OrderDetails AS od
    GROUP BY od.OrderID, od.ProductID
    HAVING COUNT(*) > 1
),
numbered AS (
    SELECT od.OrderDetailID,
           od.OrderID,
           od.ProductID,
           od.Quantity,
           od.SupplierID,
           r.suppliers_in_group,
           ROW_NUMBER() OVER (PARTITION BY od.OrderID, od.ProductID ORDER BY od.OrderDetailID) AS line_number,
           COUNT(*)     OVER (PARTITION BY od.OrderID, od.ProductID)                          AS lines_in_group,
           SUM(od.Quantity) OVER (PARTITION BY od.OrderID, od.ProductID)                      AS group_quantity
    FROM OrderDetails AS od
    JOIN repeated AS r
      ON r.OrderID   = od.OrderID
     AND r.ProductID = od.ProductID
)
SELECT n.OrderDetailID,
       n.OrderID,
       n.ProductID,
       n.Quantity,
       n.SupplierID,
       n.line_number,
       n.lines_in_group,
       n.group_quantity,
       CASE WHEN n.suppliers_in_group > 1 THEN 'Split across suppliers'
            ELSE 'Same supplier: consolidate'
       END AS verdict,
       CASE WHEN n.suppliers_in_group > 1 THEN 'keep'
            WHEN n.line_number = 1        THEN 'keep, set quantity to total'
            ELSE 'remove'
       END AS action
FROM numbered AS n
ORDER BY n.OrderID, n.ProductID, n.line_number;

-- Q73. Category share of list-price value: latest vs previous year (Hard)
WITH anchor AS (
    SELECT EXTRACT(YEAR FROM MAX(o.OrderDate))::int AS latest_year
    FROM Orders AS o
),
line_value AS (
    SELECT CASE WHEN EXTRACT(YEAR FROM o.OrderDate) = a.latest_year
                THEN 'latest' ELSE 'prev' END        AS period,
           COALESCE(cat.CategoryName, 'Unmapped')    AS category_name,
           od.Quantity * p.Sale_Price                AS list_price_value
    FROM OrderDetails  AS od
    JOIN Orders        AS o   ON o.OrderID      = od.OrderID
    JOIN Products      AS p   ON p.ProductID    = od.ProductID
    LEFT JOIN Category AS cat ON cat.CategoryID = p.CategoryID
    CROSS JOIN anchor  AS a
    WHERE o.OrderDate >= MAKE_DATE(a.latest_year - 1, 1, 1)
      AND o.OrderDate <  MAKE_DATE(a.latest_year + 1, 1, 1)
),
category_period AS (
    SELECT lv.period,
           lv.category_name,
           SUM(lv.list_price_value) AS list_price_value
    FROM line_value AS lv
    GROUP BY lv.period, lv.category_name
),
shares AS (
    SELECT cp.period,
           cp.category_name,
           100.0 * cp.list_price_value
                 / NULLIF(SUM(cp.list_price_value) OVER (PARTITION BY cp.period), 0) AS share_pct
    FROM category_period AS cp
),
pivoted AS (
    SELECT s.category_name,
           COALESCE(MAX(s.share_pct) FILTER (WHERE s.period = 'prev'),   0) AS prev_share,
           COALESCE(MAX(s.share_pct) FILTER (WHERE s.period = 'latest'), 0) AS latest_share
    FROM shares AS s
    GROUP BY s.category_name
)
SELECT pv.category_name                              AS CategoryName,
       ROUND(pv.prev_share, 2)                       AS prev_share_pct,
       ROUND(pv.latest_share, 2)                     AS latest_share_pct,
       ROUND(pv.latest_share - pv.prev_share, 2)     AS share_change_pp
FROM pivoted AS pv
ORDER BY share_change_pp DESC, pv.category_name;

-- Q74. Customers whose latest order is below their own average (Hard)
WITH anchor AS (
    SELECT MAX(o.OrderDate)::date AS last_day
    FROM Orders AS o
),
order_history AS (
    SELECT o.CustomerID,
           o.OrderID,
           o.OrderDate,
           o.Total_Order_Amount,
           ROW_NUMBER() OVER (PARTITION BY o.CustomerID
                              ORDER BY o.OrderDate DESC, o.OrderID DESC) AS recency_rank,
           COUNT(o.Total_Order_Amount) OVER earlier_orders               AS prior_orders,
           AVG(o.Total_Order_Amount)   OVER earlier_orders               AS avg_prior
    FROM Orders AS o
    WHERE o.CustomerID IS NOT NULL
      AND o.OrderDate  IS NOT NULL
    WINDOW earlier_orders AS (
        PARTITION BY o.CustomerID
        ORDER BY o.OrderDate, o.OrderID
        ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
    )
)
SELECT oh.CustomerID,
       oh.OrderDate                  AS latest_order_date,
       oh.Total_Order_Amount         AS latest_amount,
       oh.prior_orders,
       ROUND(oh.avg_prior, 2)        AS avg_prior_amount,
       ROUND(100.0 * (oh.avg_prior - oh.Total_Order_Amount)
             / NULLIF(oh.avg_prior, 0), 2) AS pct_below_avg
FROM order_history AS oh
CROSS JOIN anchor AS a
WHERE oh.recency_rank = 1
  AND oh.prior_orders >= 3
  AND oh.OrderDate >= a.last_day - 89
  AND oh.Total_Order_Amount < oh.avg_prior
ORDER BY pct_below_avg DESC, oh.CustomerID;

-- Q75. Rolling 28-day active customers, week by week (Hard)
WITH bounds AS (
    SELECT MIN(o.OrderDate)::date AS first_day,
           MAX(o.OrderDate)::date AS last_day
    FROM Orders AS o
),
week_ends AS (
    SELECT b.last_day - 7 * g.n AS week_end
    FROM bounds AS b
    CROSS JOIN generate_series(0, 11) AS g(n)
    WHERE b.last_day - 7 * g.n - 27 >= b.first_day
)
SELECT we.week_end,
       COUNT(DISTINCT o.CustomerID)
           FILTER (WHERE o.OrderDate >= we.week_end - 6) AS weekly_active_customers,
       COUNT(DISTINCT o.CustomerID)                      AS rolling_28d_active_customers
FROM week_ends AS we
LEFT JOIN Orders AS o
       ON o.OrderDate >= we.week_end - 27
      AND o.OrderDate <  we.week_end + 1
GROUP BY we.week_end
ORDER BY we.week_end;

-- Q76. Order value from new vs returning customers by month (Hard)
WITH anchor AS (
    SELECT DATE_TRUNC('month', MAX(o.OrderDate))::date AS last_month
    FROM Orders AS o
),
tagged AS (
    SELECT o.OrderID,
           o.Total_Order_Amount,
           DATE_TRUNC('month', o.OrderDate)::date AS order_month,
           DATE_TRUNC('month', MIN(o.OrderDate) OVER (PARTITION BY o.CustomerID))::date
                                                  AS first_order_month
    FROM Orders AS o
    WHERE o.CustomerID IS NOT NULL
      AND o.OrderDate  IS NOT NULL
),
monthly AS (
    SELECT t.order_month,
           COUNT(*) FILTER (WHERE t.order_month = t.first_order_month) AS new_customer_orders,
           COUNT(*) FILTER (WHERE t.order_month > t.first_order_month) AS returning_orders,
           COALESCE(SUM(t.Total_Order_Amount)
                    FILTER (WHERE t.order_month = t.first_order_month), 0) AS new_customer_value,
           COALESCE(SUM(t.Total_Order_Amount)
                    FILTER (WHERE t.order_month > t.first_order_month), 0) AS returning_value
    FROM tagged AS t
    CROSS JOIN anchor AS a
    WHERE t.order_month >= (a.last_month - INTERVAL '11 months')::date
    GROUP BY t.order_month
)
SELECT m.order_month,
       m.new_customer_orders,
       m.returning_orders,
       m.new_customer_value,
       m.returning_value,
       ROUND(100.0 * m.returning_value
             / NULLIF(m.new_customer_value + m.returning_value, 0), 2) AS returning_value_pct
FROM monthly AS m
ORDER BY m.order_month;

-- Q77. Single-source products and the value at risk (Hard)
WITH product_supply AS (
    SELECT od.ProductID,
           COUNT(DISTINCT od.SupplierID)                 AS suppliers_used,
           COUNT(*) FILTER (WHERE od.SupplierID IS NULL) AS lines_without_supplier,
           MIN(od.SupplierID)                            AS only_supplier_id,
           SUM(od.Quantity * p.Sale_Price)               AS list_price_value
    FROM OrderDetails AS od
    LEFT JOIN Products AS p ON p.ProductID = od.ProductID
    GROUP BY od.ProductID
),
with_share AS (
    SELECT ps.*,
           SUM(ps.list_price_value) OVER () AS total_value
    FROM product_supply AS ps
)
SELECT ws.ProductID,
       COALESCE(p.Product, 'Unknown product')      AS Product,
       COALESCE(s.CompanyName, 'Unknown supplier') AS sole_supplier,
       COALESCE(s.Country, 'Unknown')              AS supplier_country,
       ws.list_price_value,
       ROUND(100.0 * ws.list_price_value / NULLIF(ws.total_value, 0), 2) AS pct_of_total_value
FROM with_share AS ws
LEFT JOIN Products  AS p ON p.ProductID  = ws.ProductID
LEFT JOIN Suppliers AS s ON s.SupplierID = ws.only_supplier_id
WHERE ws.suppliers_used = 1
  AND ws.lines_without_supplier = 0
ORDER BY ws.list_price_value DESC NULLS LAST, ws.ProductID;

-- Q78. Expensive within their sub-category but selling below its median (Hard)
WITH product_units AS (
    SELECT od.ProductID,
           SUM(od.Quantity) AS units
    FROM OrderDetails AS od
    GROUP BY od.ProductID
),
scored AS (
    SELECT p.Sub_Category,
           p.ProductID,
           p.Product,
           p.Sale_Price,
           COALESCE(pu.units, 0)                                                   AS units_sold,
           PERCENT_RANK() OVER (PARTITION BY p.Sub_Category ORDER BY p.Sale_Price) AS price_pct_rank,
           COUNT(*)       OVER (PARTITION BY p.Sub_Category)                       AS subcat_products
    FROM Products AS p
    LEFT JOIN product_units AS pu ON pu.ProductID = p.ProductID
    WHERE p.Sale_Price   IS NOT NULL
      AND p.Sub_Category IS NOT NULL
),
subcat_median AS (
    SELECT s.Sub_Category,
           PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY s.units_sold) AS subcat_median_units
    FROM scored AS s
    GROUP BY s.Sub_Category
)
SELECT s.Sub_Category,
       s.ProductID,
       s.Product,
       s.Sale_Price,
       ROUND(s.price_pct_rank::numeric, 2) AS price_pct_rank,
       s.units_sold,
       sm.subcat_median_units
FROM scored AS s
JOIN subcat_median AS sm ON sm.Sub_Category = s.Sub_Category
WHERE s.subcat_products >= 20
  AND s.price_pct_rank  >= 0.75
  AND s.units_sold       < sm.subcat_median_units
ORDER BY s.Sub_Category, s.price_pct_rank DESC, s.ProductID;

-- Q79. At which order does a customer cross 10,000 in spend? (Hard)
WITH running AS (
    SELECT o.CustomerID,
           o.OrderID,
           o.OrderDate,
           ROW_NUMBER() OVER customer_orders AS order_number,
           SUM(COALESCE(o.Total_Order_Amount, 0)) OVER (customer_orders
               ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_spend,
           MIN(o.OrderDate) OVER (PARTITION BY o.CustomerID)   AS first_order_date
    FROM Orders AS o
    WHERE o.CustomerID IS NOT NULL
      AND o.OrderDate  IS NOT NULL
    WINDOW customer_orders AS (PARTITION BY o.CustomerID ORDER BY o.OrderDate, o.OrderID)
),
first_crossing AS (
    SELECT DISTINCT ON (r.CustomerID)
           r.CustomerID,
           r.order_number,
           r.OrderDate,
           r.first_order_date,
           r.running_spend
    FROM running AS r
    WHERE r.running_spend >= 10000
    ORDER BY r.CustomerID, r.order_number
)
SELECT fc.CustomerID,
       fc.order_number                    AS crossing_order_number,
       fc.OrderDate                       AS crossing_order_date,
       fc.OrderDate - fc.first_order_date AS days_from_first_order,
       fc.running_spend                   AS spend_at_crossing
FROM first_crossing AS fc
ORDER BY days_from_first_order, fc.CustomerID;

-- Q80. Sub-category repurchase rate within 90 days (Hard)
WITH anchor AS (
    SELECT MAX(o.OrderDate) AS last_day
    FROM Orders AS o
),
purchase_days AS (
    SELECT DISTINCT o.CustomerID, p.Sub_Category, o.OrderDate AS purchase_date
    FROM OrderDetails AS od
    JOIN Orders   AS o ON o.OrderID   = od.OrderID
    JOIN Products AS p ON p.ProductID = od.ProductID
),
first_buys AS (
    SELECT pd.Sub_Category, pd.CustomerID, MIN(pd.purchase_date) AS first_purchase_date
    FROM purchase_days AS pd
    GROUP BY pd.Sub_Category, pd.CustomerID
),
eligible AS (
    SELECT fb.*
    FROM first_buys AS fb
    CROSS JOIN anchor AS a
    WHERE fb.first_purchase_date <= a.last_day - 90
),
repeaters AS (
    SELECT e.Sub_Category, e.CustomerID
    FROM eligible AS e
    WHERE EXISTS (
        SELECT 1
        FROM purchase_days AS later
        WHERE later.CustomerID     = e.CustomerID
          AND later.Sub_Category   = e.Sub_Category
          AND later.purchase_date  > e.first_purchase_date
          AND later.purchase_date <= e.first_purchase_date + 90
    )
)
SELECT e.Sub_Category,
       COUNT(*)                         AS buyers,
       COUNT(r.CustomerID)              AS repeat_buyers,
       ROUND(100.0 * COUNT(r.CustomerID) / NULLIF(COUNT(*), 0), 2) AS repurchase_rate_pct
FROM eligible AS e
LEFT JOIN repeaters AS r
       ON r.Sub_Category = e.Sub_Category
      AND r.CustomerID   = e.CustomerID
GROUP BY e.Sub_Category
HAVING COUNT(*) >= 30
ORDER BY repurchase_rate_pct DESC, buyers DESC, e.Sub_Category;

-- Q81. Year-to-date vs same period last year (Hard)
WITH anchor AS (
    SELECT MAX(o.OrderDate)::date AS ytd_end
    FROM Orders AS o
),
periods AS (
    SELECT DATE_TRUNC('year', a.ytd_end)::date                       AS ytd_start,
           a.ytd_end,
           (DATE_TRUNC('year', a.ytd_end) - INTERVAL '1 year')::date AS prior_ytd_start,
           (a.ytd_end - INTERVAL '1 year')::date                     AS prior_ytd_end
    FROM anchor AS a
),
totals AS (
    SELECT pr.ytd_start,
           pr.ytd_end,
           pr.prior_ytd_start,
           pr.prior_ytd_end,
           COUNT(o.OrderID) FILTER (WHERE o.OrderDate >= pr.ytd_start
                                      AND o.OrderDate <  pr.ytd_end + 1)       AS ytd_orders,
           COALESCE(SUM(o.Total_Order_Amount) FILTER (WHERE o.OrderDate >= pr.ytd_start
                                                        AND o.OrderDate <  pr.ytd_end + 1), 0) AS ytd_value,
           COUNT(o.OrderID) FILTER (WHERE o.OrderDate >= pr.prior_ytd_start
                                      AND o.OrderDate <  pr.prior_ytd_end + 1) AS prior_ytd_orders,
           COALESCE(SUM(o.Total_Order_Amount) FILTER (WHERE o.OrderDate >= pr.prior_ytd_start
                                                        AND o.OrderDate <  pr.prior_ytd_end + 1), 0) AS prior_ytd_value
    FROM periods AS pr
    LEFT JOIN Orders AS o
           ON o.OrderDate >= pr.prior_ytd_start
          AND o.OrderDate <  pr.ytd_end + 1
    GROUP BY pr.ytd_start, pr.ytd_end, pr.prior_ytd_start, pr.prior_ytd_end
)
SELECT t.ytd_start,
       t.ytd_end,
       t.prior_ytd_start,
       t.prior_ytd_end,
       t.ytd_orders,
       t.ytd_value,
       t.prior_ytd_orders,
       t.prior_ytd_value,
       ROUND(100.0 * (t.ytd_value - t.prior_ytd_value) / NULLIF(t.prior_ytd_value, 0), 2) AS value_growth_pct
FROM totals AS t
ORDER BY t.ytd_start;

-- Q82. Each customer's favourite category (Hard)
WITH customer_category AS (
    SELECT o.CustomerID,
           COALESCE(cat.CategoryName, 'Unmapped') AS category_name,
           SUM(od.Quantity)                       AS units,
           COUNT(DISTINCT o.OrderID)              AS orders_with_category,
           MAX(o.OrderDate)                       AS last_bought
    FROM Orders AS o
    JOIN OrderDetails  AS od  ON od.OrderID     = o.OrderID
    LEFT JOIN Products AS p   ON p.ProductID    = od.ProductID
    LEFT JOIN Category AS cat ON cat.CategoryID = p.CategoryID
    WHERE o.CustomerID IS NOT NULL
    GROUP BY o.CustomerID, COALESCE(cat.CategoryName, 'Unmapped')
),
ranked AS (
    SELECT cc.CustomerID,
           cc.category_name,
           cc.units,
           SUM(cc.units) OVER (PARTITION BY cc.CustomerID) AS customer_units,
           ROW_NUMBER() OVER (PARTITION BY cc.CustomerID
                              ORDER BY cc.units DESC NULLS LAST,
                                       cc.orders_with_category DESC,
                                       cc.last_bought DESC,
                                       cc.category_name) AS category_rank
    FROM customer_category AS cc
)
SELECT r.CustomerID,
       r.category_name AS favourite_category,
       r.units         AS units_in_category,
       ROUND(100.0 * r.units / NULLIF(r.customer_units, 0), 2) AS pct_of_customer_units
FROM ranked AS r
WHERE r.category_rank = 1
ORDER BY r.CustomerID;

-- Q83. Underperforming sub-categories in the last six months (Hard)
WITH bounds AS (
    SELECT MAX(o.OrderDate)                                AS last_day,
           (MAX(o.OrderDate) - INTERVAL '6 months')::date  AS window_start
    FROM Orders AS o
),
recent_units AS (
    SELECT od.ProductID,
           SUM(od.Quantity) AS units
    FROM OrderDetails AS od
    JOIN Orders AS o   ON o.OrderID = od.OrderID
    CROSS JOIN bounds AS b
    WHERE o.OrderDate >  b.window_start
      AND o.OrderDate <= b.last_day
    GROUP BY od.ProductID
),
subcats AS (
    SELECT cat.CategoryName,
           p.Sub_Category,
           COUNT(*)                                        AS listed_products,
           COALESCE(SUM(ru.units), 0)                      AS units_last_6m,
           COALESCE(SUM(ru.units), 0)::numeric / COUNT(*)  AS units_per_product
    FROM Products AS p
    JOIN Category AS cat ON cat.CategoryID = p.CategoryID
    LEFT JOIN recent_units AS ru ON ru.ProductID = p.ProductID
    WHERE COALESCE(UPPER(TRIM(CAST(cat.Active AS VARCHAR))) IN ('1', 'TRUE', 'T', 'Y', 'YES'), FALSE)
    GROUP BY cat.CategoryName, p.Sub_Category
),
thresholds AS (
    SELECT s.CategoryName,
           PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY s.units_per_product) AS category_p25
    FROM subcats AS s
    GROUP BY s.CategoryName
)
SELECT s.CategoryName,
       s.Sub_Category,
       s.listed_products,
       s.units_last_6m,
       ROUND(s.units_per_product, 2)       AS units_per_product,
       ROUND(t.category_p25::numeric, 2)   AS category_p25
FROM subcats AS s
JOIN thresholds AS t ON t.CategoryName = s.CategoryName
WHERE s.units_per_product < t.category_p25
ORDER BY s.CategoryName, s.units_per_product, s.Sub_Category;

-- Q84. Delivery time by state and shipper with subtotals (Hard)
WITH delivered AS (
    SELECT COALESCE(NULLIF(TRIM(c.State), ''), 'Unknown') AS state,
           COALESCE(sh.CompanyName, 'Unknown shipper')     AS shipper_name,
           o.DeliveryDate::date - o.OrderDate::date        AS delivery_days
    FROM Orders AS o
    LEFT JOIN Customers AS c  ON c.CustomerID = o.CustomerID
    LEFT JOIN Shippers  AS sh ON sh.ShipperID = o.ShipperID
    WHERE o.DeliveryDate IS NOT NULL
      AND o.OrderDate    IS NOT NULL
      AND o.DeliveryDate >= o.OrderDate
      AND (o.ShipDate IS NULL
           OR (o.ShipDate >= o.OrderDate AND o.DeliveryDate >= o.ShipDate))
)
SELECT CASE WHEN GROUPING(d.state) = 1 THEN 'All states' ELSE d.state END               AS state,
       CASE WHEN GROUPING(d.shipper_name) = 1 THEN 'All shippers' ELSE d.shipper_name END AS shipper_name,
       CASE GROUPING(d.state, d.shipper_name)
            WHEN 0 THEN 'State x shipper'
            WHEN 1 THEN 'State subtotal'
            ELSE 'Grand total'
       END                                                                              AS row_level,
       COUNT(*)                                                                         AS delivered_orders,
       CASE WHEN COUNT(*) >= 5 THEN ROUND(AVG(d.delivery_days), 2) END                  AS avg_delivery_days
FROM delivered AS d
GROUP BY ROLLUP (d.state, d.shipper_name)
ORDER BY GROUPING(d.state),
         MAX(COUNT(*)) OVER (PARTITION BY d.state) DESC,
         d.state,
         GROUPING(d.shipper_name),
         d.shipper_name;

-- Q85. Win-back customers returning after 180+ days (Hard)
WITH bounds AS (
    SELECT MAX(o.OrderDate)::date AS last_day
    FROM Orders AS o
),
sequenced AS (
    SELECT o.CustomerID,
           o.OrderID,
           o.OrderDate,
           o.Total_Order_Amount,
           LAG(o.OrderDate) OVER (PARTITION BY o.CustomerID
                                  ORDER BY o.OrderDate, o.OrderID) AS previous_order_date
    FROM Orders AS o
    WHERE o.CustomerID IS NOT NULL
      AND o.OrderDate  IS NOT NULL
)
SELECT s.CustomerID,
       s.previous_order_date,
       s.OrderDate                         AS return_order_date,
       s.OrderDate - s.previous_order_date AS gap_days,
       s.Total_Order_Amount                AS return_order_amount
FROM sequenced AS s
CROSS JOIN bounds AS b
WHERE s.OrderDate - s.previous_order_date >= 180
  AND s.OrderDate >= (b.last_day - INTERVAL '1 year')::date + 1
ORDER BY s.OrderDate, s.CustomerID, s.OrderID;

-- Q86. Reconcile order headers with order lines (Expert)
WITH headers AS (
    SELECT o.OrderID,
           o.Total_Order_Amount,
           pay.PaymentType,
           TRUE AS has_header
    FROM Orders AS o
    LEFT JOIN Payments AS pay ON pay.PaymentID = o.PaymentID
),
line_totals AS (
    SELECT od.OrderID,
           TRUE                                         AS has_lines,
           COUNT(*)                                     AS line_rows,
           COALESCE(SUM(od.Quantity * p.Sale_Price), 0) AS line_list_value
    FROM OrderDetails AS od
    LEFT JOIN Products AS p ON p.ProductID = od.ProductID
    GROUP BY od.OrderID
),
classified AS (
    SELECT COALESCE(h.OrderID, lt.OrderID) AS order_key,
           h.Total_Order_Amount            AS header_value,
           h.PaymentType,
           lt.line_rows,
           lt.line_list_value,
           CASE
               WHEN h.has_header IS NULL AND lt.OrderID IS NULL THEN 'Lines with NULL OrderID'
               WHEN h.has_header IS NULL                       THEN 'Lines without header'
               WHEN lt.has_lines IS NULL                       THEN 'Header without lines'
               WHEN h.Total_Order_Amount IS NULL
                 OR h.Total_Order_Amount <= 0                  THEN 'Header zero or NULL'
               WHEN ABS(h.Total_Order_Amount - lt.line_list_value)               <= 0.01 THEN 'Exact match'
               WHEN ABS(h.Total_Order_Amount - ROUND(lt.line_list_value * 0.95, 2)) <= 0.01 THEN 'Discount 5%'
               WHEN ABS(h.Total_Order_Amount - ROUND(lt.line_list_value * 0.90, 2)) <= 0.01 THEN 'Discount 10%'
               WHEN ABS(h.Total_Order_Amount - ROUND(lt.line_list_value * 0.88, 2)) <= 0.01 THEN 'Discount 12%'
               WHEN ABS(h.Total_Order_Amount - ROUND(lt.line_list_value * 0.85, 2)) <= 0.01 THEN 'Discount 15%'
               WHEN h.Total_Order_Amount < lt.line_list_value  THEN 'Other shortfall'
               ELSE 'Header above lines'
           END AS recon_status
    FROM headers AS h
    FULL OUTER JOIN line_totals AS lt ON lt.OrderID = h.OrderID
),
statuses (sort_order, recon_status) AS (
    VALUES (1, 'Exact match'),
           (2, 'Discount 5%'),
           (3, 'Discount 10%'),
           (4, 'Discount 12%'),
           (5, 'Discount 15%'),
           (6, 'Other shortfall'),
           (7, 'Header above lines'),
           (8, 'Header zero or NULL'),
           (9, 'Header without lines'),
           (10, 'Lines without header'),
           (11, 'Lines with NULL OrderID')
)
SELECT st.recon_status,
       COUNT(cl.order_key)                                      AS orders,
       COALESCE(SUM(cl.header_value), 0)                        AS header_value,
       COALESCE(SUM(cl.line_list_value), 0)                     AS line_list_value,
       COALESCE(SUM(ABS(COALESCE(cl.header_value, 0)
                      - COALESCE(cl.line_list_value, 0))), 0)   AS abs_difference,
       STRING_AGG(DISTINCT cl.PaymentType, ', ')                AS payment_types
FROM statuses AS st
LEFT JOIN classified AS cl ON cl.recon_status = st.recon_status
GROUP BY st.sort_order, st.recon_status
ORDER BY st.sort_order;

-- Q87. Referential integrity audit across all seven relationships (Expert)
WITH relationships (rel_id, relationship) AS (
    VALUES (1, 'Products.CategoryID -> Category'),
           (2, 'Orders.CustomerID -> Customers'),
           (3, 'Orders.PaymentID -> Payments'),
           (4, 'Orders.ShipperID -> Shippers'),
           (5, 'OrderDetails.OrderID -> Orders'),
           (6, 'OrderDetails.ProductID -> Products'),
           (7, 'OrderDetails.SupplierID -> Suppliers')
),
child_keys AS (
    SELECT 1 AS rel_id, p.CategoryID AS fk_value,
           NOT EXISTS (SELECT 1 FROM Category AS cat WHERE cat.CategoryID = p.CategoryID) AS no_parent
    FROM Products AS p
    UNION ALL
    SELECT 2, o.CustomerID,
           NOT EXISTS (SELECT 1 FROM Customers AS c WHERE c.CustomerID = o.CustomerID)
    FROM Orders AS o
    UNION ALL
    SELECT 3, o.PaymentID,
           NOT EXISTS (SELECT 1 FROM Payments AS pay WHERE pay.PaymentID = o.PaymentID)
    FROM Orders AS o
    UNION ALL
    SELECT 4, o.ShipperID,
           NOT EXISTS (SELECT 1 FROM Shippers AS sh WHERE sh.ShipperID = o.ShipperID)
    FROM Orders AS o
    UNION ALL
    SELECT 5, od.OrderID,
           NOT EXISTS (SELECT 1 FROM Orders AS o WHERE o.OrderID = od.OrderID)
    FROM OrderDetails AS od
    UNION ALL
    SELECT 6, od.ProductID,
           NOT EXISTS (SELECT 1 FROM Products AS p WHERE p.ProductID = od.ProductID)
    FROM OrderDetails AS od
    UNION ALL
    SELECT 7, od.SupplierID,
           NOT EXISTS (SELECT 1 FROM Suppliers AS s WHERE s.SupplierID = od.SupplierID)
    FROM OrderDetails AS od
)
SELECT r.relationship,
       COUNT(ck.rel_id)                                                         AS child_rows,
       COUNT(ck.rel_id) FILTER (WHERE ck.fk_value IS NULL)                      AS null_fk_rows,
       COUNT(ck.rel_id) FILTER (WHERE ck.fk_value IS NOT NULL AND ck.no_parent) AS orphan_rows,
       ARRAY_TO_STRING(
           (ARRAY_AGG(DISTINCT ck.fk_value ORDER BY ck.fk_value)
                FILTER (WHERE ck.fk_value IS NOT NULL AND ck.no_parent))[1:5],
           ', ')                                                                AS sample_orphan_keys
FROM relationships AS r
LEFT JOIN child_keys AS ck ON ck.rel_id = r.rel_id
GROUP BY r.rel_id, r.relationship
ORDER BY r.rel_id;

-- Q88. Date validity audit (Expert)
WITH anchor AS (
    SELECT MAX(o.OrderDate) AS max_order_date
    FROM Orders AS o
),
order_checks AS (
    SELECT r.rule_id, r.rule, r.severity, o.OrderID AS record_id, r.violated
    FROM Orders AS o
    LEFT JOIN Customers AS c ON c.CustomerID = o.CustomerID
    CROSS JOIN anchor AS a
    CROSS JOIN LATERAL (
        VALUES
            (1, 'Order date missing',               'error',   o.OrderDate IS NULL),
            (2, 'Shipped before ordered',           'error',   o.ShipDate < o.OrderDate),
            (3, 'Delivered before shipped',         'error',   o.DeliveryDate < o.ShipDate),
            (4, 'Delivered before ordered',         'error',   o.DeliveryDate < o.OrderDate),
            (5, 'Delivered with no ship date',      'error',   o.DeliveryDate IS NOT NULL AND o.ShipDate IS NULL),
            (6, 'Ordered before customer sign-up',  'warning', o.OrderDate < c.DateEntered),
            (7, 'Delivered after 7-day promise',    'warning', o.DeliveryDate::date - o.OrderDate::date > 7),
            (8, 'Not shipped 14+ days after order', 'warning', o.ShipDate IS NULL AND o.DeliveryDate IS NULL
                                                               AND a.max_order_date::date - o.OrderDate::date >= 14)
    ) AS r(rule_id, rule, severity, violated)
),
customer_checks AS (
    SELECT 9                               AS rule_id,
           'Customer sign-up date missing' AS rule,
           'warning'                       AS severity,
           c.CustomerID                    AS record_id,
           c.DateEntered IS NULL           AS violated
    FROM Customers AS c
),
all_checks AS (
    SELECT * FROM order_checks
    UNION ALL
    SELECT * FROM customer_checks
)
SELECT ac.rule_id,
       ac.rule,
       ac.severity,
       COUNT(*)                                                                  AS records_checked,
       COUNT(*) FILTER (WHERE ac.violated)                                       AS violations,
       ROUND(100.0 * COUNT(*) FILTER (WHERE ac.violated) / NULLIF(COUNT(*), 0), 2) AS violation_pct,
       (ARRAY_AGG(ac.record_id ORDER BY ac.record_id) FILTER (WHERE ac.violated))[1:5] AS example_ids
FROM all_checks AS ac
GROUP BY ac.rule_id, ac.rule, ac.severity
ORDER BY ac.rule_id;

-- Q89. Incremental load with a watermark and lookback (Expert)
-- Target table: same columns and primary key as Orders, plus a load timestamp.
CREATE TEMP TABLE orders_target (
    LIKE Orders INCLUDING ALL,
    etl_updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Seed it as the previous run left it: that run happened 14 days before the
-- latest order, so it held no later orders and no later ship/delivery dates.
INSERT INTO orders_target
       (OrderID, CustomerID, PaymentID, OrderDate, ShipperID,
        Total_Order_Amount, ShipDate, DeliveryDate)
SELECT o.OrderID, o.CustomerID, o.PaymentID, o.OrderDate, o.ShipperID,
       o.Total_Order_Amount,
       CASE WHEN o.ShipDate     <= prev.run_date THEN o.ShipDate     END,
       CASE WHEN o.DeliveryDate <= prev.run_date THEN o.DeliveryDate END
FROM Orders AS o
CROSS JOIN (SELECT MAX(src.OrderDate) - 14 AS run_date FROM Orders AS src) AS prev
WHERE o.OrderDate <= prev.run_date;

-- Tonight's incremental load.
WITH params AS (
    SELECT 21 AS lookback_days
),
watermark AS (
    SELECT COALESCE(MAX(t.OrderDate), DATE '1900-01-01') AS high_water_date
    FROM orders_target AS t
),
batch AS (
    SELECT o.*,
           EXISTS (SELECT 1 FROM orders_target AS t
                   WHERE t.OrderID = o.OrderID) AS already_loaded
    FROM Orders AS o
    CROSS JOIN watermark AS w
    CROSS JOIN params    AS p
    WHERE o.OrderDate >= w.high_water_date - p.lookback_days
       OR o.OrderDate IS NULL
),
upserted AS (
    INSERT INTO orders_target AS t
           (OrderID, CustomerID, PaymentID, OrderDate, ShipperID,
            Total_Order_Amount, ShipDate, DeliveryDate)
    SELECT b.OrderID, b.CustomerID, b.PaymentID, b.OrderDate, b.ShipperID,
           b.Total_Order_Amount, b.ShipDate, b.DeliveryDate
    FROM batch AS b
    ON CONFLICT (OrderID) DO UPDATE
       SET CustomerID         = EXCLUDED.CustomerID,
           PaymentID          = EXCLUDED.PaymentID,
           OrderDate          = EXCLUDED.OrderDate,
           ShipperID          = EXCLUDED.ShipperID,
           Total_Order_Amount = EXCLUDED.Total_Order_Amount,
           ShipDate           = EXCLUDED.ShipDate,
           DeliveryDate       = EXCLUDED.DeliveryDate,
           etl_updated_at     = now()
     WHERE (t.CustomerID, t.PaymentID, t.OrderDate, t.ShipperID,
            t.Total_Order_Amount, t.ShipDate, t.DeliveryDate)
           IS DISTINCT FROM
           (EXCLUDED.CustomerID, EXCLUDED.PaymentID, EXCLUDED.OrderDate, EXCLUDED.ShipperID,
            EXCLUDED.Total_Order_Amount, EXCLUDED.ShipDate, EXCLUDED.DeliveryDate)
    RETURNING t.OrderID
),
outcome AS (
    SELECT CASE WHEN u.OrderID IS NULL THEN 'unchanged'
                WHEN b.already_loaded  THEN 'updated'
                ELSE 'inserted'
           END AS action
    FROM batch AS b
    LEFT JOIN upserted AS u ON u.OrderID = b.OrderID
),
actions (sort_order, action) AS (
    VALUES (1, 'inserted'), (2, 'updated'), (3, 'unchanged')
)
SELECT a.action,
       COUNT(oc.action) AS rows
FROM actions AS a
LEFT JOIN outcome AS oc ON oc.action = a.action
GROUP BY a.sort_order, a.action
ORDER BY a.sort_order;

-- Q90. Column-by-column completeness profile of Orders (Expert)
WITH anchor AS (
    SELECT MAX(o.OrderDate) AS max_order_date
    FROM Orders AS o
),
unpivoted AS (
    SELECT v.column_position,
           v.column_name,
           v.column_value,
           o.OrderDate > a.max_order_date - 30 AS is_recent
    FROM Orders AS o
    CROSS JOIN anchor AS a
    CROSS JOIN LATERAL (
        VALUES (1, 'OrderID',            o.OrderID::text),
               (2, 'CustomerID',         o.CustomerID::text),
               (3, 'PaymentID',          o.PaymentID::text),
               (4, 'OrderDate',          o.OrderDate::text),
               (5, 'ShipperID',          o.ShipperID::text),
               (6, 'Total_Order_Amount', o.Total_Order_Amount::text),
               (7, 'ShipDate',           o.ShipDate::text),
               (8, 'DeliveryDate',       o.DeliveryDate::text)
    ) AS v(column_position, column_name, column_value)
)
SELECT u.column_name,
       COUNT(*)                                                AS total_rows,
       COUNT(*) FILTER (WHERE u.column_value IS NULL)          AS null_rows,
       ROUND(100.0 * COUNT(*) FILTER (WHERE u.column_value IS NULL)
             / NULLIF(COUNT(*), 0), 2)                         AS null_pct,
       ROUND(100.0 * COUNT(*) FILTER (WHERE u.column_value IS NULL AND u.is_recent)
             / NULLIF(COUNT(*) FILTER (WHERE u.is_recent), 0), 2) AS null_pct_last_30d,
       COUNT(DISTINCT u.column_value)                          AS distinct_values
FROM unpivoted AS u
GROUP BY u.column_position, u.column_name
ORDER BY u.column_position;

-- Q91. Cumulative value per customer by cohort (LTV curve) (Expert)
WITH anchor AS (
    SELECT (DATE_TRUNC('month', MAX(o.OrderDate) + 1) - INTERVAL '1 month')::date AS last_full_month
    FROM Orders AS o
),
first_orders AS (
    SELECT o.CustomerID,
           DATE_TRUNC('month', MIN(o.OrderDate))::date AS first_month
    FROM Orders AS o
    WHERE o.CustomerID IS NOT NULL
      AND o.OrderDate IS NOT NULL
    GROUP BY o.CustomerID
),
cohorts AS (
    SELECT DATE_TRUNC('quarter', fo.first_month)::date AS cohort_quarter,
           COUNT(*)                                     AS cohort_customers
    FROM first_orders AS fo
    GROUP BY DATE_TRUNC('quarter', fo.first_month)::date
),
order_offsets AS (
    SELECT DATE_TRUNC('quarter', fo.first_month)::date AS cohort_quarter,
           (EXTRACT(YEAR  FROM o.OrderDate) - EXTRACT(YEAR  FROM fo.first_month)) * 12
         + (EXTRACT(MONTH FROM o.OrderDate) - EXTRACT(MONTH FROM fo.first_month)) AS month_offset,
           o.Total_Order_Amount
    FROM Orders AS o
    JOIN first_orders AS fo ON fo.CustomerID = o.CustomerID
),
offset_value AS (
    SELECT oo.cohort_quarter,
           oo.month_offset::int              AS month_offset,
           SUM(oo.Total_Order_Amount)        AS order_value
    FROM order_offsets AS oo
    WHERE oo.month_offset <= 12
    GROUP BY oo.cohort_quarter, oo.month_offset
),
spine AS (
    SELECT c.cohort_quarter,
           c.cohort_customers,
           m.month_offset
    FROM cohorts AS c
    CROSS JOIN generate_series(0, 12) AS m(month_offset)
),
curve AS (
    SELECT s.cohort_quarter,
           s.cohort_customers,
           s.month_offset,
           SUM(COALESCE(ov.order_value, 0)) OVER (
               PARTITION BY s.cohort_quarter
               ORDER BY s.month_offset
               ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
           ) AS cumulative_value,
           -- the youngest customer in the cohort joined in its third month
           (s.cohort_quarter + INTERVAL '2 months'
                             + s.month_offset * INTERVAL '1 month')::date
               <= a.last_full_month AS is_complete
    FROM spine AS s
    CROSS JOIN anchor AS a
    LEFT JOIN offset_value AS ov
           ON ov.cohort_quarter = s.cohort_quarter
          AND ov.month_offset   = s.month_offset
)
SELECT cv.cohort_quarter,
       cv.cohort_customers,
       ROUND(MAX(cv.cumulative_value) FILTER (WHERE cv.month_offset = 0  AND cv.is_complete)
             / cv.cohort_customers, 2) AS value_per_customer_m0,
       ROUND(MAX(cv.cumulative_value) FILTER (WHERE cv.month_offset = 3  AND cv.is_complete)
             / cv.cohort_customers, 2) AS value_per_customer_m3,
       ROUND(MAX(cv.cumulative_value) FILTER (WHERE cv.month_offset = 6  AND cv.is_complete)
             / cv.cohort_customers, 2) AS value_per_customer_m6,
       ROUND(MAX(cv.cumulative_value) FILTER (WHERE cv.month_offset = 12 AND cv.is_complete)
             / cv.cohort_customers, 2) AS value_per_customer_m12
FROM curve AS cv
GROUP BY cv.cohort_quarter, cv.cohort_customers
ORDER BY cv.cohort_quarter;

-- Q92. How duplicate accounts distort the repeat-customer rate (Expert)
WITH customer_map AS (
    SELECT c.CustomerID,
           MIN(c.CustomerID) OVER (
               PARTITION BY COALESCE(NULLIF(LOWER(TRIM(c.Email)), ''),
                                     'no-email:' || c.CustomerID::text)
           ) AS person_id
    FROM Customers AS c
),
attributed_orders AS (
    SELECT o.OrderID,
           o.CustomerID,
           COALESCE(cm.person_id, o.CustomerID) AS person_id
    FROM Orders AS o
    LEFT JOIN customer_map AS cm ON cm.CustomerID = o.CustomerID
    WHERE o.CustomerID IS NOT NULL
),
per_unit AS (
    SELECT 1 AS sort_order, 'Raw CustomerID' AS method,
           ao.CustomerID AS unit_id, COUNT(*) AS orders
    FROM attributed_orders AS ao
    GROUP BY ao.CustomerID
    UNION ALL
    SELECT 2, 'Merged by email',
           ao.person_id, COUNT(*)
    FROM attributed_orders AS ao
    GROUP BY ao.person_id
)
SELECT pu.method,
       COUNT(*)                                          AS customers,
       COUNT(*) FILTER (WHERE pu.orders >= 2)            AS repeat_customers,
       ROUND(100.0 * COUNT(*) FILTER (WHERE pu.orders >= 2)
             / NULLIF(COUNT(*), 0), 2)                   AS repeat_rate_pct,
       SUM(pu.orders)                                    AS orders
FROM per_unit AS pu
GROUP BY pu.sort_order, pu.method
ORDER BY pu.sort_order;

-- Q93. Possible duplicate order submissions (Expert)
WITH product_lines AS (
    SELECT od.OrderID,
           od.ProductID,
           SUM(od.Quantity)                                           AS quantity,
           od.ProductID IS NOT NULL AND COUNT(od.Quantity) = COUNT(*) AS is_known
    FROM OrderDetails AS od
    WHERE od.OrderID IS NOT NULL
    GROUP BY od.OrderID, od.ProductID
),
signatures AS (
    SELECT pl.OrderID,
           STRING_AGG(pl.ProductID::text || 'x' || pl.quantity::text, '|'
                      ORDER BY pl.ProductID)                          AS line_signature,
           BOOL_AND(pl.is_known)                                      AS basket_known
    FROM product_lines AS pl
    GROUP BY pl.OrderID
),
order_sig AS (
    SELECT o.OrderID, o.CustomerID, o.OrderDate, o.PaymentID, o.ShipperID,
           o.Total_Order_Amount, sg.line_signature
    FROM Orders AS o
    JOIN signatures AS sg ON sg.OrderID = o.OrderID
    WHERE sg.basket_known
      AND o.CustomerID IS NOT NULL
      AND o.OrderDate  IS NOT NULL
),
same_day_pairs AS (
    SELECT a.OrderID                                          AS first_order_id,
           b.OrderID                                          AS second_order_id,
           a.line_signature = b.line_signature                AS same_basket,
           a.Total_Order_Amount = b.Total_Order_Amount        AS same_amount,
           (a.Total_Order_Amount, a.PaymentID, a.ShipperID)
               IS NOT DISTINCT FROM
           (b.Total_Order_Amount, b.PaymentID, b.ShipperID)   AS same_header
    FROM order_sig AS a
    JOIN order_sig AS b
      ON b.CustomerID = a.CustomerID
     AND b.OrderDate  = a.OrderDate
     AND b.OrderID    > a.OrderID
)
SELECT COUNT(*)                                                 AS same_day_pairs,
       COUNT(*) FILTER (WHERE sp.same_basket)                   AS same_basket_pairs,
       COUNT(*) FILTER (WHERE sp.same_amount)                   AS same_amount_pairs,
       COUNT(*) FILTER (WHERE sp.same_basket AND sp.same_header) AS exact_copies,
       CASE WHEN COUNT(*) FILTER (WHERE sp.same_basket) = 0
            THEN 'No duplicate submissions'
            ELSE 'Review: send same-basket pairs to support'
       END                                                      AS verdict
FROM same_day_pairs AS sp;

-- Q94. Supplier concentration per category (HHI) (Expert)
WITH supplier_value AS (
    SELECT cat.CategoryID,
           COALESCE(cat.CategoryName, 'Unmapped') AS category_name,
           od.SupplierID,
           SUM(od.Quantity * p.Sale_Price)        AS list_price_value
    FROM OrderDetails  AS od
    JOIN Products      AS p   ON p.ProductID    = od.ProductID
    LEFT JOIN Category AS cat ON cat.CategoryID = p.CategoryID
    WHERE od.SupplierID IS NOT NULL
      AND od.Quantity   IS NOT NULL
      AND p.Sale_Price  IS NOT NULL
    GROUP BY cat.CategoryID, COALESCE(cat.CategoryName, 'Unmapped'), od.SupplierID
),
supplier_share AS (
    SELECT sv.CategoryID,
           sv.category_name,
           sv.SupplierID,
           sv.list_price_value,
           100.0 * sv.list_price_value
                 / NULLIF(SUM(sv.list_price_value) OVER (PARTITION BY sv.CategoryID), 0) AS share_pct
    FROM supplier_value AS sv
),
category_stats AS (
    SELECT ss.CategoryID,
           ss.category_name,
           ss.SupplierID,
           ss.share_pct,
           COUNT(*)                         OVER (PARTITION BY ss.CategoryID) AS suppliers_used,
           SUM(ss.share_pct * ss.share_pct) OVER (PARTITION BY ss.CategoryID) AS hhi,
           ROW_NUMBER() OVER (PARTITION BY ss.CategoryID
                              ORDER BY ss.list_price_value DESC, ss.SupplierID) AS supplier_rank
    FROM supplier_share AS ss
)
SELECT cs.category_name                                               AS CategoryName,
       cs.suppliers_used,
       COALESCE(s.CompanyName, CONCAT('Unknown supplier ', cs.SupplierID))  AS top_supplier,
       ROUND(cs.share_pct, 2)                                         AS top_supplier_share_pct,
       ROUND(cs.hhi, 0)                                               AS hhi,
       CASE
           WHEN cs.suppliers_used = 1 THEN 'Single source'
           WHEN cs.hhi > 2500         THEN 'Highly concentrated'
           WHEN cs.hhi >= 1500        THEN 'Moderately concentrated'
           ELSE                            'Unconcentrated'
       END                                                            AS concentration_band
FROM category_stats AS cs
LEFT JOIN Suppliers AS s ON s.SupplierID = cs.SupplierID
WHERE cs.supplier_rank = 1
ORDER BY cs.hhi DESC, cs.category_name;

-- Q95. Debug a revenue-by-category query that gives wrong numbers (Expert)
WITH latest_year AS (
    SELECT DATE_TRUNC('year', MAX(o.OrderDate))::date                      AS year_start,
           (DATE_TRUNC('year', MAX(o.OrderDate)) + INTERVAL '1 year')::date AS next_year_start
    FROM Orders AS o
),
year_lines AS (
    SELECT od.OrderID,
           cat.CategoryID,
           od.Quantity * p.Sale_Price AS list_price_value
    FROM Orders        AS o
    JOIN latest_year   AS ly  ON o.OrderDate >= ly.year_start
                             AND o.OrderDate <  ly.next_year_start
    JOIN OrderDetails  AS od  ON od.OrderID     = o.OrderID
    LEFT JOIN Products AS p   ON p.ProductID    = od.ProductID
    LEFT JOIN Category AS cat ON cat.CategoryID = p.CategoryID
),
category_sales AS (
    SELECT yl.CategoryID,
           COUNT(DISTINCT yl.OrderID) AS orders,
           SUM(yl.list_price_value)   AS list_price_value
    FROM year_lines AS yl
    GROUP BY yl.CategoryID
)
SELECT COALESCE(cat.CategoryName, 'Unmapped') AS CategoryName,
       COALESCE(cs.orders, 0)                 AS orders,
       COALESCE(cs.list_price_value, 0)       AS list_price_value
FROM Category AS cat
FULL JOIN category_sales AS cs ON cs.CategoryID = cat.CategoryID
ORDER BY list_price_value, CategoryName;

-- Q96. Make a slow order report sargable and index it (Expert)
WITH month_bounds AS (
    SELECT DATE_TRUNC('month', MAX(o.OrderDate))::date                       AS month_start,
           (DATE_TRUNC('month', MAX(o.OrderDate)) + INTERVAL '1 month')::date AS next_month_start
    FROM Orders AS o
)
SELECT o.OrderID,
       o.OrderDate,
       o.CustomerID,
       o.Total_Order_Amount,
       COUNT(od.OrderID)             AS line_items,
       COALESCE(SUM(od.Quantity), 0) AS units
FROM Orders AS o
CROSS JOIN month_bounds AS mb
LEFT JOIN OrderDetails AS od ON od.OrderID = o.OrderID
WHERE o.OrderDate >= mb.month_start
  AND o.OrderDate <  mb.next_month_start
  AND o.Total_Order_Amount >= 2000
GROUP BY o.OrderID, o.OrderDate, o.CustomerID, o.Total_Order_Amount
ORDER BY o.Total_Order_Amount DESC, o.OrderID;

-- Q97. What do customers buy on their second order? (Expert)
WITH order_seq AS (
    SELECT o.OrderID,
           o.CustomerID,
           ROW_NUMBER() OVER (PARTITION BY o.CustomerID
                              ORDER BY o.OrderDate, o.OrderID) AS order_number
    FROM Orders AS o
    WHERE o.CustomerID IS NOT NULL
      AND o.OrderDate  IS NOT NULL
),
first_two AS (
    SELECT os.OrderID, os.CustomerID, os.order_number
    FROM order_seq AS os
    WHERE os.order_number <= 2
),
order_category_value AS (
    SELECT ft.OrderID,
           COALESCE(cat.CategoryName, 'Unmapped') AS category_name,
           SUM(od.Quantity * p.Sale_Price)        AS list_price_value,
           SUM(od.Quantity)                       AS units
    FROM first_two AS ft
    JOIN OrderDetails  AS od  ON od.OrderID     = ft.OrderID
    LEFT JOIN Products AS p   ON p.ProductID    = od.ProductID
    LEFT JOIN Category AS cat ON cat.CategoryID = p.CategoryID
    GROUP BY ft.OrderID, COALESCE(cat.CategoryName, 'Unmapped')
),
dominant AS (
    SELECT ocv.OrderID,
           ocv.category_name,
           ROW_NUMBER() OVER (PARTITION BY ocv.OrderID
                              ORDER BY ocv.list_price_value DESC NULLS LAST,
                                       ocv.units DESC NULLS LAST,
                                       ocv.category_name) AS category_rank
    FROM order_category_value AS ocv
),
customer_path AS (
    SELECT ft.CustomerID,
           MAX(COALESCE(d.category_name, 'No line items')) FILTER (WHERE ft.order_number = 1) AS first_order_category,
           MAX(COALESCE(d.category_name, 'No line items')) FILTER (WHERE ft.order_number = 2) AS second_order_category
    FROM first_two AS ft
    LEFT JOIN dominant AS d
           ON d.OrderID       = ft.OrderID
          AND d.category_rank = 1
    GROUP BY ft.CustomerID
)
SELECT cp.first_order_category,
       COALESCE(cp.second_order_category, 'No second order') AS second_order_category,
       COUNT(*)                                               AS customers,
       ROUND(100.0 * COUNT(*)
             / SUM(COUNT(*)) OVER (PARTITION BY cp.first_order_category), 2) AS pct_of_first_category
FROM customer_path AS cp
GROUP BY cp.first_order_category,
         COALESCE(cp.second_order_category, 'No second order')
ORDER BY SUM(COUNT(*)) OVER (PARTITION BY cp.first_order_category) DESC,
         cp.first_order_category,
         customers DESC,
         second_order_category;

-- Q98. Category association rules: support, confidence, lift (Expert)
WITH params AS (
    SELECT 2.0 AS min_support_pct
),
baskets AS (
    SELECT DISTINCT
           od.OrderID,
           COALESCE(cat.CategoryName, 'Unmapped') AS category_name
    FROM OrderDetails  AS od
    JOIN Products      AS p   ON p.ProductID    = od.ProductID
    LEFT JOIN Category AS cat ON cat.CategoryID = p.CategoryID
),
basket_total AS (
    SELECT COUNT(DISTINCT b.OrderID) AS total_orders
    FROM baskets AS b
),
category_orders AS (
    SELECT b.category_name,
           COUNT(*) AS orders_with_category
    FROM baskets AS b
    GROUP BY b.category_name
),
pair_orders AS (
    SELECT a.category_name AS category_a,
           b.category_name AS category_b,
           COUNT(*)        AS orders_with_both
    FROM baskets AS a
    JOIN baskets AS b
      ON b.OrderID        = a.OrderID
     AND b.category_name <> a.category_name
    GROUP BY a.category_name, b.category_name
)
SELECT po.category_a,
       po.category_b,
       po.orders_with_both,
       ROUND(100.0 * po.orders_with_both / bt.total_orders, 2)          AS support_pct,
       ROUND(100.0 * po.orders_with_both / ca.orders_with_category, 2)  AS confidence_a_to_b_pct,
       ROUND(1.0 * po.orders_with_both * bt.total_orders
             / (ca.orders_with_category * cb.orders_with_category), 3)  AS lift
FROM pair_orders AS po
JOIN category_orders AS ca ON ca.category_name = po.category_a
JOIN category_orders AS cb ON cb.category_name = po.category_b
CROSS JOIN basket_total AS bt
CROSS JOIN params       AS pr
WHERE 100.0 * po.orders_with_both / bt.total_orders >= pr.min_support_pct
ORDER BY lift DESC, confidence_a_to_b_pct DESC, po.category_a, po.category_b;

-- Q99. Flag unusual weeks in order volume (Expert)
WITH bounds AS (
    SELECT DATE_TRUNC('week', MIN(o.OrderDate) + 6)::date AS first_full_week,
           DATE_TRUNC('week', MAX(o.OrderDate) - 6)::date AS last_full_week
    FROM Orders AS o
),
week_spine AS (
    SELECT gs::date AS week_start
    FROM bounds AS b
    CROSS JOIN generate_series(b.first_full_week, b.last_full_week, INTERVAL '7 days') AS gs
),
week_counts AS (
    SELECT DATE_TRUNC('week', o.OrderDate)::date AS week_start,
           COUNT(*)                              AS orders
    FROM Orders AS o
    WHERE o.OrderDate IS NOT NULL
    GROUP BY DATE_TRUNC('week', o.OrderDate)::date
),
weekly AS (
    SELECT ws.week_start,
           COALESCE(wc.orders, 0) AS orders
    FROM week_spine AS ws
    LEFT JOIN week_counts AS wc ON wc.week_start = ws.week_start
),
baseline AS (
    SELECT w.week_start,
           w.orders,
           COUNT(*)              OVER prior_8w AS baseline_weeks,
           AVG(w.orders)         OVER prior_8w AS trailing_mean,
           STDDEV_SAMP(w.orders) OVER prior_8w AS trailing_stddev
    FROM weekly AS w
    WINDOW prior_8w AS (ORDER BY w.week_start
                        ROWS BETWEEN 8 PRECEDING AND 1 PRECEDING)
),
scored AS (
    SELECT b.week_start,
           b.orders,
           b.trailing_mean,
           b.trailing_stddev,
           CASE WHEN b.baseline_weeks = 8
                THEN (b.orders - b.trailing_mean) / NULLIF(b.trailing_stddev, 0)
           END AS z_score
    FROM baseline AS b
)
SELECT s.week_start,
       s.orders,
       ROUND(s.trailing_mean, 2)   AS trailing_mean,
       ROUND(s.trailing_stddev, 2) AS trailing_stddev,
       ROUND(s.z_score, 2)         AS z_score,
       ABS(s.z_score) >= 3         AS is_anomaly
FROM scored AS s
ORDER BY is_anomaly DESC NULLS LAST, s.week_start DESC;

-- Q100. Monthly KPI scorecard with month-over-month change (Expert)
WITH anchor AS (
    SELECT MAX(o.OrderDate) AS last_day
    FROM Orders AS o
),
windows AS (
    SELECT 'latest'                               AS period,
           DATE_TRUNC('month', a.last_day)::date  AS start_day,
           a.last_day                             AS end_day
    FROM anchor AS a
    UNION ALL
    SELECT 'prior',
           (DATE_TRUNC('month', a.last_day) - INTERVAL '1 month')::date,
           LEAST((DATE_TRUNC('month', a.last_day) - INTERVAL '1 month')::date
                     + (EXTRACT(DAY FROM a.last_day)::int - 1),
                 (DATE_TRUNC('month', a.last_day) - INTERVAL '1 day')::date)
    FROM anchor AS a
),
first_orders AS (
    SELECT o.CustomerID, MIN(o.OrderDate) AS first_order_date
    FROM Orders AS o
    GROUP BY o.CustomerID
),
period_orders AS (
    SELECT w.period, w.start_day, o.OrderID, o.CustomerID, o.OrderDate,
           o.DeliveryDate, o.Total_Order_Amount, fo.first_order_date
    FROM windows AS w
    JOIN Orders AS o        ON o.OrderDate BETWEEN w.start_day AND w.end_day
    LEFT JOIN first_orders AS fo ON fo.CustomerID = o.CustomerID
),
period_units AS (
    SELECT po.period, SUM(od.Quantity) AS units
    FROM period_orders AS po
    JOIN OrderDetails AS od ON od.OrderID = po.OrderID
    GROUP BY po.period
),
kpis AS (
    SELECT po.period,
           COUNT(*)::numeric                                                          AS orders,
           SUM(po.Total_Order_Amount)                                                 AS order_value,
           ROUND(AVG(po.Total_Order_Amount), 2)                                       AS aov,
           COUNT(DISTINCT po.CustomerID)::numeric                                     AS active_customers,
           COUNT(DISTINCT po.CustomerID) FILTER (WHERE po.first_order_date >= po.start_day)::numeric AS new_customers,
           ROUND(100.0 * COUNT(*) FILTER (WHERE po.first_order_date < po.start_day)
                 / NULLIF(COUNT(*), 0), 2)                                            AS repeat_order_share_pct,
           ROUND(100.0 * COUNT(*) FILTER (WHERE po.DeliveryDate >= po.OrderDate
                                            AND po.DeliveryDate - po.OrderDate <= 7)
                 / NULLIF(COUNT(*) FILTER (WHERE po.DeliveryDate >= po.OrderDate), 0), 2) AS on_time_pct,
           MAX(pu.units)::numeric                                                     AS units
    FROM period_orders AS po
    JOIN period_units AS pu ON pu.period = po.period
    GROUP BY po.period
),
labels AS (
    SELECT MAX(w.start_day || ' to ' || w.end_day) FILTER (WHERE w.period = 'prior')  AS prior_window,
           MAX(w.start_day || ' to ' || w.end_day) FILTER (WHERE w.period = 'latest') AS latest_window
    FROM windows AS w
)
SELECT v.kpi,
       v.unit,
       v.prior_value,
       v.latest_value,
       v.latest_value - v.prior_value                                          AS change,
       CASE WHEN v.unit = '%' THEN NULL
            ELSE ROUND(100.0 * (v.latest_value - v.prior_value) / NULLIF(v.prior_value, 0), 2)
       END                                                                     AS change_pct,
       lb.prior_window,
       lb.latest_window
FROM kpis AS p
JOIN kpis AS l ON p.period = 'prior' AND l.period = 'latest'
CROSS JOIN labels AS lb
CROSS JOIN LATERAL (
    VALUES (1, 'Orders',                     'count', p.orders,                 l.orders),
           (2, 'Order value',                'money', p.order_value,            l.order_value),
           (3, 'Average order value',        'money', p.aov,                    l.aov),
           (4, 'Active customers',           'count', p.active_customers,       l.active_customers),
           (5, 'New customers',              'count', p.new_customers,          l.new_customers),
           (6, 'Repeat-customer order share','%',     p.repeat_order_share_pct, l.repeat_order_share_pct),
           (7, 'On-time delivery (<= 7 days)', '%',   p.on_time_pct,            l.on_time_pct),
           (8, 'Units',                      'count', p.units,                  l.units)
) AS v(sort_order, kpi, unit, prior_value, latest_value)
ORDER BY v.sort_order;
