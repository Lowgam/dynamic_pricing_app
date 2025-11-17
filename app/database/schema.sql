-- Module: schema.sql
-- This file will create the tabs we will need for all the products and rules. It isn't automatically executed by python.
-- =========================
-- Tab: products
-- =========================
CREATE TABLE IF NOT EXISTS products (
    id INT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    current_price DECIMAL(10,2) NOT NULL,
    expiration_date DATE NULL,
    category VARCHAR(100),
    stock INT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =========================
-- Tab: pricing_rules
-- =========================
CREATE TABLE IF NOT EXISTS pricing_rules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rule_name VARCHAR(100) NOT NULL,
    factor_a DOUBLE NOT NULL,
    factor_b DOUBLE NOT NULL,
    threshold DOUBLE NOT NULL,
    active BOOLEAN NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
