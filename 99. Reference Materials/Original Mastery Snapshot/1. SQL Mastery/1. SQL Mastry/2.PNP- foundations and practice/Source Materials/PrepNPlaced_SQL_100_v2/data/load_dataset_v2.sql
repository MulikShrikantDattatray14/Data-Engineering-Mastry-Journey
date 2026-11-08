-- Load the PrepNPlaced Commerce Dataset v2 into PostgreSQL.
--
-- Run from the folder that holds the CSV files:
--     createdb ecomm
--     psql -d ecomm -f load_dataset_v2.sql
--
-- Every file is staged as text first, then typed. Two columns need care:
--   * Orders dates are DD-MM-YYYY text. PostgreSQL's default date style would read 12-01-2025
--     as 1 December 2025 without complaint, so they are parsed with TO_DATE(..., 'DD-MM-YYYY').
--   * Customers.DateEntered arrives in three formats (YYYY/MM/DD, DD-MM-YYYY, YYYY-MM-DD) or blank.
--     A CASE on the pattern picks the right format for each row.
-- Nothing else is cleaned: the data-quality problems are part of the course.
-- Identifiers are unquoted, so PostgreSQL stores them in lower case.

\set ON_ERROR_STOP on

DROP SCHEMA IF EXISTS stg CASCADE;
CREATE SCHEMA stg;
CREATE TABLE stg.suppliers    (supplierid text, companyname text, address text, city text, state text, postalcode text, country text, phone text, email text);
CREATE TABLE stg.payments     (paymentid text, paymenttype text, allowed text);
CREATE TABLE stg.shippers     (shipperid text, companyname text, phone text);
CREATE TABLE stg.category     (categoryid text, categoryname text, active text);
CREATE TABLE stg.customers    (customerid text, firstname text, lastname text, city text, state text, country text, postalcode text, phone text, email text, dateentered text);
CREATE TABLE stg.products     (productid text, product text, categoryid text, sub_category text, brand text, sale_price text, market_price text, type text, rating text);
CREATE TABLE stg.orders       (orderid text, customerid text, paymentid text, orderdate text, shipperid text, total_order_amount text, shipdate text, deliverydate text);
CREATE TABLE stg.orderdetails (orderdetailid text, orderid text, productid text, quantity text, supplierid text);

\copy stg.suppliers    FROM 'Suppliers.csv'    WITH (FORMAT csv, HEADER true)
\copy stg.payments     FROM 'Payments.csv'     WITH (FORMAT csv, HEADER true)
\copy stg.shippers     FROM 'Shippers.csv'     WITH (FORMAT csv, HEADER true)
\copy stg.category     FROM 'Category.csv'     WITH (FORMAT csv, HEADER true)
\copy stg.customers    FROM 'Customers.csv'    WITH (FORMAT csv, HEADER true)
\copy stg.products     FROM 'Products.csv'     WITH (FORMAT csv, HEADER true)
\copy stg.orders       FROM 'Orders.csv'       WITH (FORMAT csv, HEADER true)
\copy stg.orderdetails FROM 'OrderDetails.csv' WITH (FORMAT csv, HEADER true)

DROP TABLE IF EXISTS OrderDetails, Orders, Customers, Payments, Shippers, Products, Category, Suppliers;

CREATE TABLE Suppliers (
    SupplierID   INT PRIMARY KEY,
    CompanyName  VARCHAR(60),
    Address      VARCHAR(100),
    City         VARCHAR(50),
    State        VARCHAR(30),
    PostalCode   VARCHAR(20),
    Country      VARCHAR(50),
    Phone        VARCHAR(25),
    Email        VARCHAR(60)
);
CREATE TABLE Payments (
    PaymentID    INT PRIMARY KEY,
    PaymentType  VARCHAR(50),
    Allowed      VARCHAR(3)
);
CREATE TABLE Shippers (
    ShipperID    INT PRIMARY KEY,
    CompanyName  VARCHAR(60),
    Phone        VARCHAR(25)
);
CREATE TABLE Category (
    CategoryID   INT PRIMARY KEY,
    CategoryName VARCHAR(50),
    Active       VARCHAR(5)
);
CREATE TABLE Customers (
    CustomerID   INT PRIMARY KEY,
    FirstName    VARCHAR(50),
    LastName     VARCHAR(50),
    City         VARCHAR(50),
    State        VARCHAR(30),
    Country      VARCHAR(60),
    PostalCode   VARCHAR(20),
    Phone        VARCHAR(20),
    Email        VARCHAR(80),
    DateEntered  DATE
);
CREATE TABLE Products (
    ProductID    INT PRIMARY KEY,
    Product      VARCHAR(200),
    CategoryID   INT,
    Sub_Category VARCHAR(50),
    Brand        VARCHAR(50),
    Sale_Price   NUMERIC(10,2),
    Market_Price NUMERIC(10,2),
    Type         VARCHAR(50),
    Rating       NUMERIC(2,1)
);
CREATE TABLE Orders (
    OrderID            INT PRIMARY KEY,
    CustomerID         INT,
    PaymentID          INT,
    OrderDate          DATE,
    ShipperID          INT,
    Total_Order_Amount NUMERIC(12,2),
    ShipDate           DATE,
    DeliveryDate       DATE
);
CREATE TABLE OrderDetails (
    OrderDetailID INT PRIMARY KEY,
    OrderID       INT,
    ProductID     INT,
    Quantity      INT,
    SupplierID    INT
);

INSERT INTO Suppliers SELECT supplierid::int, companyname, address, city, state, postalcode, country, phone, email FROM stg.suppliers;
INSERT INTO Payments  SELECT paymentid::int, paymenttype, allowed FROM stg.payments;
INSERT INTO Shippers  SELECT shipperid::int, companyname, phone FROM stg.shippers;
INSERT INTO Category  SELECT categoryid::int, categoryname, active FROM stg.category;
INSERT INTO Customers
SELECT customerid::int, firstname, lastname, city, state, country, postalcode, phone, email,
       CASE WHEN dateentered ~ '^\d{4}/\d{2}/\d{2}$' THEN TO_DATE(dateentered, 'YYYY/MM/DD')
            WHEN dateentered ~ '^\d{2}-\d{2}-\d{4}$' THEN TO_DATE(dateentered, 'DD-MM-YYYY')
            WHEN dateentered ~ '^\d{4}-\d{2}-\d{2}$' THEN TO_DATE(dateentered, 'YYYY-MM-DD')
       END
FROM stg.customers;
INSERT INTO Products
SELECT productid::int, product, NULLIF(categoryid, '')::int, sub_category, brand,
       NULLIF(sale_price, '')::numeric, NULLIF(market_price, '')::numeric, type, NULLIF(rating, '')::numeric
FROM stg.products;
INSERT INTO Orders
SELECT orderid::int, NULLIF(customerid, '')::int, NULLIF(paymentid, '')::int,
       TO_DATE(NULLIF(orderdate, ''), 'DD-MM-YYYY'), NULLIF(shipperid, '')::int,
       NULLIF(total_order_amount, '')::numeric,
       TO_DATE(NULLIF(shipdate, ''), 'DD-MM-YYYY'), TO_DATE(NULLIF(deliverydate, ''), 'DD-MM-YYYY')
FROM stg.orders;
INSERT INTO OrderDetails
SELECT orderdetailid::int, NULLIF(orderid, '')::int, NULLIF(productid, '')::int,
       NULLIF(quantity, '')::int, NULLIF(supplierid, '')::int
FROM stg.orderdetails;

SELECT 'Suppliers' AS table_name, COUNT(*) AS row_count FROM Suppliers UNION ALL
SELECT 'Payments', COUNT(*) FROM Payments UNION ALL
SELECT 'Shippers', COUNT(*) FROM Shippers UNION ALL
SELECT 'Category', COUNT(*) FROM Category UNION ALL
SELECT 'Customers', COUNT(*) FROM Customers UNION ALL
SELECT 'Products', COUNT(*) FROM Products UNION ALL
SELECT 'Orders', COUNT(*) FROM Orders UNION ALL
SELECT 'OrderDetails', COUNT(*) FROM OrderDetails;

DROP SCHEMA stg CASCADE;
