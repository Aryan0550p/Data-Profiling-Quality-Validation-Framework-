-- =============================================================================
-- Enterprise E-Commerce Data Platform: Relational DDL & Constraints
-- Database Target: PostgreSQL 14+ / SQL Compliant
-- Profiled Across 8 Datasets and 73 Total Columns
-- =============================================================================

-- Enable UUID extension if required
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Clean existing objects
DROP TABLE IF EXISTS fct_customer_interactions CASCADE;
DROP TABLE IF EXISTS fct_inventory CASCADE;
DROP TABLE IF EXISTS fct_shipments CASCADE;
DROP TABLE IF EXISTS fct_payments CASCADE;
DROP TABLE IF EXISTS fct_order_items CASCADE;
DROP TABLE IF EXISTS fct_orders CASCADE;
DROP TABLE IF EXISTS dim_products CASCADE;
DROP TABLE IF EXISTS dim_customers CASCADE;

-- -----------------------------------------------------------------------------
-- 1. Master Customer Profile Dimension (10 Columns)
-- -----------------------------------------------------------------------------
CREATE TABLE dim_customers (
    customer_id         VARCHAR(32)     PRIMARY KEY,
    first_name          VARCHAR(64)     NOT NULL,
    last_name           VARCHAR(64)     NOT NULL,
    email               VARCHAR(128)    NULL, -- Quality check: expect_not_null
    phone               VARCHAR(32)     NULL, -- Quality check: conditional non-null for VIP
    registration_date   DATE            NOT NULL,
    customer_segment    VARCHAR(32)     NOT NULL CHECK (customer_segment IN ('Consumer', 'Corporate', 'Small Business', 'VIP')),
    country_code        VARCHAR(2)      NOT NULL CHECK (country_code IN ('US', 'CA', 'GB', 'DE')),
    postal_code         VARCHAR(16)     NOT NULL, -- Quality check: regex format for US
    status              VARCHAR(16)     NOT NULL CHECK (status IN ('Active', 'Inactive', 'Suspended'))
);

CREATE INDEX idx_dim_customers_email ON dim_customers(email);
CREATE INDEX idx_dim_customers_segment ON dim_customers(customer_segment);

-- -----------------------------------------------------------------------------
-- 2. Master Product Dimension (10 Columns)
-- -----------------------------------------------------------------------------
CREATE TABLE dim_products (
    product_id          VARCHAR(32)     PRIMARY KEY,
    sku                 VARCHAR(64)     NOT NULL UNIQUE,
    product_name        VARCHAR(128)    NOT NULL,
    category            VARCHAR(64)     NOT NULL CHECK (category IN ('Electronics', 'Home & Kitchen', 'Apparel', 'Books', 'Sports')),
    sub_category        VARCHAR(64)     NOT NULL,
    unit_cost           NUMERIC(10, 2)  NOT NULL,
    unit_price          NUMERIC(10, 2)  NOT NULL, -- Quality check: unit_price >= unit_cost
    weight_kg           NUMERIC(10, 2)  NOT NULL CHECK (weight_kg > 0), -- Quality check: outlier upper bound
    supplier_id         VARCHAR(32)     NOT NULL,
    is_active           BOOLEAN         NOT NULL DEFAULT TRUE
);

CREATE INDEX idx_dim_products_category ON dim_products(category);
CREATE INDEX idx_dim_products_supplier ON dim_products(supplier_id);

-- -----------------------------------------------------------------------------
-- 3. Header-Level Order Transactions Fact (11 Columns)
-- -----------------------------------------------------------------------------
CREATE TABLE fct_orders (
    order_id            VARCHAR(32)     PRIMARY KEY,
    customer_id         VARCHAR(32)     NULL, -- Quality check: expect_not_null & foreign_key
    order_date          TIMESTAMP       NOT NULL,
    order_status        VARCHAR(32)     NOT NULL CHECK (order_status IN ('Delivered', 'Shipped', 'Processing', 'Pending', 'Cancelled', 'Refunded')),
    payment_method      VARCHAR(32)     NOT NULL CHECK (payment_method IN ('Credit Card', 'PayPal', 'Wire Transfer', 'Gift Card')),
    currency            VARCHAR(16)     NOT NULL, -- Quality check: standardized to 'USD'
    subtotal_amount     NUMERIC(12, 2)  NOT NULL CHECK (subtotal_amount >= 0),
    discount_amount     NUMERIC(12, 2)  NOT NULL DEFAULT 0.00 CHECK (discount_amount >= 0),
    tax_amount          NUMERIC(12, 2)  NOT NULL DEFAULT 0.00 CHECK (tax_amount >= 0),
    total_amount        NUMERIC(12, 2)  NOT NULL, -- Quality check: range check & QA outlier filter
    channel             VARCHAR(32)     NOT NULL CHECK (channel IN ('Web', 'Mobile App', 'In-Store', 'Marketplace')),
    CONSTRAINT fk_fct_orders_customer FOREIGN KEY (customer_id) REFERENCES dim_customers(customer_id) ON DELETE RESTRICT
);

CREATE INDEX idx_fct_orders_customer ON fct_orders(customer_id);
CREATE INDEX idx_fct_orders_date ON fct_orders(order_date);
CREATE INDEX idx_fct_orders_status ON fct_orders(order_status);

-- -----------------------------------------------------------------------------
-- 4. Line-Item Level Order Details Fact (8 Columns)
-- -----------------------------------------------------------------------------
CREATE TABLE fct_order_items (
    item_id             VARCHAR(32)     PRIMARY KEY,
    order_id            VARCHAR(32)     NOT NULL,
    product_id          VARCHAR(32)     NOT NULL, -- Quality check: foreign key referential integrity
    quantity            INTEGER         NOT NULL, -- Quality check: quantity > 0
    unit_price          NUMERIC(10, 2)  NOT NULL CHECK (unit_price >= 0),
    discount_rate       NUMERIC(5, 4)   NOT NULL, -- Quality check: discount_rate BETWEEN 0.0 AND 1.0
    total_item_price    NUMERIC(12, 2)  NOT NULL,
    fulfillment_status  VARCHAR(32)     NOT NULL CHECK (fulfillment_status IN ('Fulfilled', 'Backordered', 'Cancelled')),
    CONSTRAINT fk_fct_order_items_order FOREIGN KEY (order_id) REFERENCES fct_orders(order_id) ON DELETE CASCADE,
    CONSTRAINT fk_fct_order_items_product FOREIGN KEY (product_id) REFERENCES dim_products(product_id) ON DELETE RESTRICT
);

CREATE INDEX idx_fct_order_items_order ON fct_order_items(order_id);
CREATE INDEX idx_fct_order_items_product ON fct_order_items(product_id);

-- -----------------------------------------------------------------------------
-- 5. Payment Transaction Settlement Fact (9 Columns)
-- -----------------------------------------------------------------------------
CREATE TABLE fct_payments (
    payment_id              VARCHAR(32)     PRIMARY KEY,
    order_id                VARCHAR(32)     NOT NULL,
    payment_date            TIMESTAMP       NOT NULL,
    payment_method          VARCHAR(32)     NOT NULL,
    payment_status          VARCHAR(32)     NOT NULL CHECK (payment_status IN ('Success', 'Pending', 'Failed', 'Refunded')),
    amount_paid             NUMERIC(12, 2)  NOT NULL, -- Quality check: matches order total_amount
    gateway_transaction_id  VARCHAR(64)     NULL,     -- Quality check: required if payment_status == 'Success'
    fee_amount              NUMERIC(10, 2)  NOT NULL DEFAULT 0.00 CHECK (fee_amount >= 0),
    currency                VARCHAR(16)     NOT NULL,
    CONSTRAINT fk_fct_payments_order FOREIGN KEY (order_id) REFERENCES fct_orders(order_id) ON DELETE RESTRICT
);

CREATE INDEX idx_fct_payments_order ON fct_payments(order_id);
CREATE INDEX idx_fct_payments_status ON fct_payments(payment_status);

-- -----------------------------------------------------------------------------
-- 6. Logistics & Shipment Tracking Fact (10 Columns)
-- -----------------------------------------------------------------------------
CREATE TABLE fct_shipments (
    shipment_id             VARCHAR(32)     PRIMARY KEY,
    order_id                VARCHAR(32)     NOT NULL,
    carrier                 VARCHAR(32)     NOT NULL CHECK (carrier IN ('FedEx', 'UPS', 'DHL', 'USPS')),
    tracking_number         VARCHAR(64)     NOT NULL,
    shipped_date            TIMESTAMP       NOT NULL, -- Quality check: shipped_date >= order_date
    delivered_date          TIMESTAMP       NULL,     -- Quality check: required if shipping_status == 'Delivered'
    shipping_status         VARCHAR(32)     NOT NULL CHECK (shipping_status IN ('Delivered', 'In Transit', 'Failed Delivery', 'Returned')),
    shipping_cost           NUMERIC(10, 2)  NOT NULL CHECK (shipping_cost >= 0),
    origin_warehouse_id     VARCHAR(32)     NOT NULL,
    destination_country     VARCHAR(2)      NOT NULL,
    CONSTRAINT fk_fct_shipments_order FOREIGN KEY (order_id) REFERENCES fct_orders(order_id) ON DELETE RESTRICT
);

CREATE INDEX idx_fct_shipments_order ON fct_shipments(order_id);
CREATE INDEX idx_fct_shipments_status ON fct_shipments(shipping_status);

-- -----------------------------------------------------------------------------
-- 7. Inventory Levels & Restock Snapshot Fact (7 Columns)
-- -----------------------------------------------------------------------------
CREATE TABLE fct_inventory (
    inventory_id        VARCHAR(32)     PRIMARY KEY,
    warehouse_id        VARCHAR(32)     NOT NULL, -- Quality check: variance check (not constant)
    product_id          VARCHAR(32)     NOT NULL,
    stock_on_hand       INTEGER         NOT NULL CHECK (stock_on_hand >= 0),
    stock_reserved      INTEGER         NOT NULL CHECK (stock_reserved >= 0),
    reorder_point       INTEGER         NULL,     -- Quality check: non-null threshold constraint
    last_restock_date   DATE            NOT NULL,
    CONSTRAINT fk_fct_inventory_product FOREIGN KEY (product_id) REFERENCES dim_products(product_id) ON DELETE CASCADE
);

CREATE INDEX idx_fct_inventory_warehouse ON fct_inventory(warehouse_id);
CREATE INDEX idx_fct_inventory_product ON fct_inventory(product_id);

-- -----------------------------------------------------------------------------
-- 8. Customer Support Interactions Fact (8 Columns)
-- -----------------------------------------------------------------------------
CREATE TABLE fct_customer_interactions (
    interaction_id          VARCHAR(32)     PRIMARY KEY,
    customer_id             VARCHAR(32)     NOT NULL,
    interaction_date        TIMESTAMP       NOT NULL, -- Quality check: <= CURRENT_TIMESTAMP
    channel                 VARCHAR(32)     NOT NULL CHECK (channel IN ('Email', 'Chat', 'Phone', 'Social Media')),
    rating_score            INTEGER         NOT NULL CHECK (rating_score BETWEEN 1 AND 5), -- Quality check: CSAT scale
    resolution_time_mins    NUMERIC(10, 2)  NOT NULL CHECK (resolution_time_mins >= 0),    -- Quality check: extreme outlier filter
    issue_category          VARCHAR(64)     NOT NULL CHECK (issue_category IN ('Billing', 'Shipping', 'Product Inquiry', 'Return Request')),
    is_escalated            BOOLEAN         NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_fct_interactions_customer FOREIGN KEY (customer_id) REFERENCES dim_customers(customer_id) ON DELETE CASCADE
);

CREATE INDEX idx_fct_interactions_customer ON fct_customer_interactions(customer_id);
CREATE INDEX idx_fct_interactions_date ON fct_customer_interactions(interaction_date);
