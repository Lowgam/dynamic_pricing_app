-- Module: schema.sql
-- This file will create the tabs we will need for all the products and rules. It isn't automatically executed by python.
-- =========================
-- Tab: products
-- =========================
CREATE TABLE if NOT EXISTS products (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    shopify_id BIGINT NULL,
    sku VARCHAR(100) NULL,
    name VARCHAR(255) NULL,
    price DECIMAL(10,2) NULL,
    cost_price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    stock INT NULL,
    category VARCHAR(100) NULL,
    expiry_date DATE NULL
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
