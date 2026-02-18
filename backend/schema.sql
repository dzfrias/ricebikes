-- ============================================
-- Rice Bikes Repair Database Setup & Seed
-- PostgreSQL Version
-- ============================================

-- Drop tables if they exist (safe to re-run)
DROP TABLE IF EXISTS repair_transactions;
DROP TABLE IF EXISTS bikes;
DROP TABLE IF EXISTS customers;

-- ============================================
-- Create Tables
-- ============================================

CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone_number TEXT
);

CREATE TABLE bikes (
    bike_id SERIAL PRIMARY KEY,
    make TEXT NOT NULL,
    model TEXT NOT NULL
);

CREATE TABLE repair_transactions (
    transaction_id SERIAL PRIMARY KEY,
    bike_id INT NOT NULL,
    customer_id INT NOT NULL,
    total_cost NUMERIC(10,2) NOT NULL,
    transaction_date DATE NOT NULL,
    CONSTRAINT fk_bike
        FOREIGN KEY (bike_id)
        REFERENCES bikes(bike_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
);

-- ============================================
-- Seed Customers
-- ============================================

INSERT INTO customers (first_name, last_name, email, phone_number) VALUES
('Alex', 'Nguyen', 'alex.nguyen@email.com', '7135550101'),
('Maria', 'Lopez', 'maria.lopez@email.com', '7135550102'),
('James', 'Carter', 'james.carter@email.com', '7135550103'),
('Sophie', 'Kim', 'sophie.kim@email.com', '7135550104'),
('Daniel', 'Reed', 'daniel.reed@email.com', '7135550105');

-- ============================================
-- Seed Bikes
-- ============================================

INSERT INTO bikes (make, model) VALUES
('Trek', 'Domane'),
('Specialized', 'Allez'),
('Giant', 'Defy'),
('Cannondale', 'Synapse'),
('Santa Cruz', 'Hightower');

-- ============================================
-- Seed Repair Transactions (10 total)
-- ============================================

INSERT INTO repair_transactions (bike_id, customer_id, total_cost, transaction_date) VALUES
(1, 1, 89.99, '2026-01-05'),
(2, 2, 120.00, '2026-01-08'),
(3, 3, 45.50, '2026-01-10'),
(4, 4, 200.00, '2026-01-12'),
(5, 5, 75.25, '2026-01-15'),
(1, 1, 150.00, '2026-01-18'),
(2, 3, 60.00, '2026-01-20'),
(3, 2, 95.75, '2026-01-22'),
(4, 5, 180.00, '2026-01-25'),
(5, 4, 55.00, '2026-01-28');

-- ============================================
-- Verification Query (Sorted by Date Desc)
-- ============================================

SELECT 
    rt.transaction_id,
    rt.transaction_date,
    rt.total_cost,
    c.first_name,
    c.last_name,
    b.make,
    b.model
FROM repair_transactions rt
JOIN customers c ON rt.customer_id = c.customer_id
JOIN bikes b ON rt.bike_id = b.bike_id
