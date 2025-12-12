-- Module: schema.sql
-- This file will create the tabs we will need for all the products and rules. It isn't automatically executed by python.

-- =========================
-- Tab: products
-- =========================
CREATE TABLE IF NOT EXISTS products (
  id                   INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

  -- Shopify reference
  shopify_product_id   BIGINT UNSIGNED NOT NULL,
  shopify_variant_id   BIGINT UNSIGNED NOT NULL,
  sku                  VARCHAR(64) DEFAULT NULL,

  -- Description
  name                 VARCHAR(255) NOT NULL,
  category             VARCHAR(255) DEFAULT NULL,

  -- Prices
  base_price           DECIMAL(10,2) NOT NULL,
  current_price        DECIMAL(10,2) NOT NULL,
  cost_price           DECIMAL(10,2) DEFAULT NULL,
  currency             CHAR(3) NOT NULL DEFAULT 'EUR',

  -- Stock & expiration
  stock                INT NOT NULL DEFAULT 0,
  expiry_date          DATE DEFAULT NULL,
  expiry_source        ENUM('metafield','manual','none')
                       NOT NULL DEFAULT 'none',

  -- Status
  status               ENUM('active','archived','draft')
                       NOT NULL DEFAULT 'active',

  -- Tracking synchronisations
  last_sync_at         DATETIME DEFAULT NULL,

  -- Timestamps local
  created_at           DATETIME NOT NULL
                       DEFAULT CURRENT_TIMESTAMP,
  updated_at           DATETIME NOT NULL
                       DEFAULT CURRENT_TIMESTAMP
                       ON UPDATE CURRENT_TIMESTAMP,

  -- Useful index
  INDEX idx_shopify_variant (shopify_variant_id),
  INDEX idx_sku (sku),
  INDEX idx_expiry (expiry_date),
  INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--------------- Routing shopify --------------------------
 --id                    (autoincrement interno MySQL)
 --shopify_product_id    (da product.id)
 --shopify_variant_id    (da variant.id)
 --sku                   (da variant.sku)
 --name                  (da product.title)
 --category              (da product.product_type)
 --base_price            (da variant.price)
 --current_price         (inizialmente uguale a base_price)
 --cost_price            (da inventory_item.cost, se presente)
 --stock                 (da variant.inventory_quantity o Inventory API)
 --expiry_date           (da metafield expiry_date o NULL)
 --expiry_source         ("metafield" / "manual" / "none")
 --status                (da product.status)
 --last_sync_at          (timestamp di quando hai fatto l’import)
 --created_at / updated_at (gestiti da MySQL)



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



-- =========================
-- Tab: change_price_events
-- =========================
CREATE TABLE change_price_events (
  id INT AUTO_INCREMENT PRIMARY KEY,
  product_id INT NOT NULL,

  old_price DECIMAL(10,2) NOT NULL,
  new_price DECIMAL(10,2) NOT NULL,

  changed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  source VARCHAR(50) NOT NULL DEFAULT 'dashboard',

  status ENUM('OPEN','CLOSED') NOT NULL DEFAULT 'OPEN',

  -- outcome
  units_before INT NULL,
  units_after INT NULL,
  window_days INT NULL,
  closed_at DATETIME NULL,

  weights_snapshot_id INT NULL,

  INDEX idx_cpe_product_time (product_id, changed_at),
  INDEX idx_cpe_status (status),

  CONSTRAINT fk_cpe_product
    FOREIGN KEY (product_id) REFERENCES products(id)
    ON DELETE CASCADE
);

