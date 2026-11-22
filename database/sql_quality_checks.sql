-- =============================================================================
-- SQL Data Quality & Validation Test Suite
-- Comprehensive queries auditing Completeness, Consistency, Accuracy, and Distribution
-- Across all 8 enterprise datasets, targeting the 23 cataloged issues.
-- =============================================================================

-- =============================================================================
-- SECTION 1: COMPLETENESS QUERIES (Issues 01 - 06)
-- =============================================================================

-- ISSUE-01: Null Customer Emails
SELECT 'ISSUE-01' AS issue_id, 'dim_customers' AS dataset, 'email' AS column_name,
       COUNT(*) AS violation_count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM dim_customers), 2) AS violation_pct
FROM dim_customers
WHERE email IS NULL;

-- ISSUE-02: Orders with Missing Customer IDs
SELECT 'ISSUE-02' AS issue_id, 'fct_orders' AS dataset, 'customer_id' AS column_name,
       COUNT(*) AS violation_count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM fct_orders), 2) AS violation_pct
FROM fct_orders
WHERE customer_id IS NULL;

-- ISSUE-03: Delivered Shipments Missing Delivered Timestamp
SELECT 'ISSUE-03' AS issue_id, 'fct_shipments' AS dataset, 'delivered_date' AS column_name,
       COUNT(*) AS violation_count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM fct_shipments WHERE shipping_status = 'Delivered'), 2) AS violation_pct
FROM fct_shipments
WHERE shipping_status = 'Delivered' AND delivered_date IS NULL;

-- ISSUE-04: Inventory Records Missing Reorder Point Threshold
SELECT 'ISSUE-04' AS issue_id, 'fct_inventory' AS dataset, 'reorder_point' AS column_name,
       COUNT(*) AS violation_count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM fct_inventory), 2) AS violation_pct
FROM fct_inventory
WHERE reorder_point IS NULL;

-- ISSUE-05: Missing Phone Numbers for High-Value Customers (VIP / Corporate)
SELECT 'ISSUE-05' AS issue_id, 'dim_customers' AS dataset, 'phone' AS column_name,
       COUNT(*) AS violation_count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM dim_customers WHERE customer_segment IN ('VIP', 'Corporate')), 2) AS violation_pct
FROM dim_customers
WHERE customer_segment IN ('VIP', 'Corporate') AND phone IS NULL;

-- ISSUE-06: Settled Payments Missing Gateway Transaction ID
SELECT 'ISSUE-06' AS issue_id, 'fct_payments' AS dataset, 'gateway_transaction_id' AS column_name,
       COUNT(*) AS violation_count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM fct_payments WHERE payment_status = 'Success'), 2) AS violation_pct
FROM fct_payments
WHERE payment_status = 'Success' AND gateway_transaction_id IS NULL;


-- =============================================================================
-- SECTION 2: CONSISTENCY & REFERENTIAL INTEGRITY (Issues 07 - 12)
-- =============================================================================

-- ISSUE-07: Orphan Order Items (Product ID not in dim_products)
SELECT 'ISSUE-07' AS issue_id, 'fct_order_items' AS dataset, 'product_id' AS column_name,
       COUNT(*) AS violation_count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM fct_order_items), 2) AS violation_pct
FROM fct_order_items oi
LEFT JOIN dim_products p ON oi.product_id = p.product_id
WHERE p.product_id IS NULL;

-- ISSUE-08: Order Status vs Shipment Status Discordance (Cancelled Order Marked Delivered)
SELECT 'ISSUE-08' AS issue_id, 'fct_orders' AS dataset, 'order_status' AS column_name,
       COUNT(*) AS violation_count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM fct_orders), 2) AS violation_pct
FROM fct_orders o
JOIN fct_shipments s ON o.order_id = s.order_id
WHERE o.order_status = 'Cancelled' AND s.shipping_status = 'Delivered';

-- ISSUE-09: Non-Standard Currency Code Formatting in Orders
SELECT 'ISSUE-09' AS issue_id, 'fct_orders' AS dataset, 'currency' AS column_name,
       COUNT(*) AS violation_count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM fct_orders), 2) AS violation_pct
FROM fct_orders
WHERE currency != 'USD';

-- ISSUE-10: Temporal Ordering Violation (Shipped Date Earlier Than Order Date)
SELECT 'ISSUE-10' AS issue_id, 'fct_shipments' AS dataset, 'shipped_date' AS column_name,
       COUNT(*) AS violation_count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM fct_shipments), 2) AS violation_pct
FROM fct_shipments s
JOIN fct_orders o ON s.order_id = o.order_id
WHERE s.shipped_date < o.order_date;

-- ISSUE-11: Financial Payment Reconciliation Variance (Amount Paid != Order Total)
SELECT 'ISSUE-11' AS issue_id, 'fct_payments' AS dataset, 'amount_paid' AS column_name,
       COUNT(*) AS violation_count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM fct_payments WHERE payment_status = 'Success'), 2) AS violation_pct
FROM fct_payments p
JOIN fct_orders o ON p.order_id = o.order_id
WHERE p.payment_status = 'Success' AND ABS(p.amount_paid - o.total_amount) > 0.01;

-- ISSUE-12: Duplicate Customer Email Profiles (Entity Resolution Collisions)
SELECT 'ISSUE-12' AS issue_id, 'dim_customers' AS dataset, 'email' AS column_name,
       COUNT(*) AS violation_count,
       0.0 AS violation_pct
FROM (
    SELECT email, COUNT(*) AS cnt
    FROM dim_customers
    WHERE email IS NOT NULL
    GROUP BY email
    HAVING COUNT(*) > 1
) dup;


-- =============================================================================
-- SECTION 3: ACCURACY & VALIDITY QUERIES (Issues 13 - 18)
-- =============================================================================

-- ISSUE-13: Negative Line Item Quantities
SELECT 'ISSUE-13' AS issue_id, 'fct_order_items' AS dataset, 'quantity' AS column_name,
       COUNT(*) AS violation_count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM fct_order_items), 2) AS violation_pct
FROM fct_order_items
WHERE quantity < 1;

-- ISSUE-14: Impossible Line Item Discount Rates (> 100%)
SELECT 'ISSUE-14' AS issue_id, 'fct_order_items' AS dataset, 'discount_rate' AS column_name,
       COUNT(*) AS violation_count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM fct_order_items), 2) AS violation_pct
FROM fct_order_items
WHERE discount_rate > 1.0;

-- ISSUE-15: Future Event Timestamps in Customer Support Interactions
SELECT 'ISSUE-15' AS issue_id, 'fct_customer_interactions' AS dataset, 'interaction_date' AS column_name,
       COUNT(*) AS violation_count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM fct_customer_interactions), 2) AS violation_pct
FROM fct_customer_interactions
WHERE interaction_date > CURRENT_TIMESTAMP;

-- ISSUE-16: Malformed US Postal Code Strings (Non-standard digits)
SELECT 'ISSUE-16' AS issue_id, 'dim_customers' AS dataset, 'postal_code' AS column_name,
       COUNT(*) AS violation_count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM dim_customers WHERE country_code = 'US'), 2) AS violation_pct
FROM dim_customers
WHERE country_code = 'US' AND (LENGTH(postal_code) < 5 OR postal_code LIKE '%?%' OR postal_code LIKE '%ABC%');

-- ISSUE-17: Inverted Pricing Economics (Unit Cost Exceeds Unit Price)
SELECT 'ISSUE-17' AS issue_id, 'dim_products' AS dataset, 'unit_cost' AS column_name,
       COUNT(*) AS violation_count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM dim_products), 2) AS violation_pct
FROM dim_products
WHERE unit_cost > unit_price;

-- ISSUE-18: Out-of-Bounds CSAT Ratings (Rating > 5)
SELECT 'ISSUE-18' AS issue_id, 'fct_customer_interactions' AS dataset, 'rating_score' AS column_name,
       COUNT(*) AS violation_count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM fct_customer_interactions), 2) AS violation_pct
FROM fct_customer_interactions
WHERE rating_score < 1 OR rating_score > 5;


-- =============================================================================
-- SECTION 4: DISTRIBUTION & STATISTICAL ANOMALY QUERIES (Issues 19 - 23)
-- =============================================================================

-- ISSUE-19: Extreme Monetary Outlier in Orders ($9,999,999 QA test transaction)
SELECT 'ISSUE-19' AS issue_id, 'fct_orders' AS dataset, 'total_amount' AS column_name,
       COUNT(*) AS violation_count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM fct_orders), 2) AS violation_pct
FROM fct_orders
WHERE total_amount > 50000.00;

-- ISSUE-20: Degenerate Zero-Variance Warehouse Location in Inventory
SELECT 'ISSUE-20' AS issue_id, 'fct_inventory' AS dataset, 'warehouse_id' AS column_name,
       COUNT(DISTINCT warehouse_id) AS distinct_warehouses,
       CASE WHEN COUNT(DISTINCT warehouse_id) <= 1 THEN 'DEGENERATE_CONSTANT' ELSE 'HEALTHY_VARIANCE' END AS status
FROM fct_inventory;

-- ISSUE-21: Extreme Support Ticket Resolution Duration Outliers (> 48 Hours)
SELECT 'ISSUE-21' AS issue_id, 'fct_customer_interactions' AS dataset, 'resolution_time_mins' AS column_name,
       COUNT(*) AS violation_count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM fct_customer_interactions), 2) AS violation_pct
FROM fct_customer_interactions
WHERE resolution_time_mins > 2880.0;

-- ISSUE-22: Extreme Physical Product Weight Outliers (> 50 kg)
SELECT 'ISSUE-22' AS issue_id, 'dim_products' AS dataset, 'weight_kg' AS column_name,
       COUNT(*) AS violation_count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM dim_products), 2) AS violation_pct
FROM dim_products
WHERE weight_kg > 50.0;

-- ISSUE-23: Bimodal Penny Discount Cluster Spike ($0.01)
SELECT 'ISSUE-23' AS issue_id, 'fct_orders' AS dataset, 'discount_amount' AS column_name,
       COUNT(*) AS violation_count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM fct_orders), 2) AS violation_pct
FROM fct_orders
WHERE discount_amount = 0.01;
