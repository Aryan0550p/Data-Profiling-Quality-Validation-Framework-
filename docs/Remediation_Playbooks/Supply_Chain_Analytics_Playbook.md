# Downstream Remediation Playbook: Supply Chain & Operations Analytics Team

**Target Stakeholders**: Supply Chain Analysts, Logistics Operations Engineers, Inventory Planners, Fulfillment Managers  
**Governed Data Domains**: Logistics & Shipments (`fct_shipments`), Inventory (`fct_inventory`), Orders Status (`fct_orders`), Product Catalog (`dim_products`)

---

## 1. Executive Summary & Impact Analysis

Supply Chain and Operations analytics drives On-Time In-Full (OTIF) fulfillment rates, carrier SLA compliance, inventory replenishment modeling, and warehouse capacity planning.

The framework identified **6 data quality issues** impacting the Supply Chain domain:

| Issue ID | Entity & Column | Dimension | Severity | Business Risk |
| :--- | :--- | :--- | :---: | :--- |
| **ISSUE-03** | `fct_shipments.delivered_date` | Completeness | HIGH | OTIF calculation failure for 210 delivered shipments; cannot enforce carrier SLAs. |
| **ISSUE-04** | `fct_inventory.reorder_point` | Completeness | MEDIUM | 112 SKUs missing reorder triggers, risking stockouts during peak demand. |
| **ISSUE-08** | `fct_orders.order_status` | Consistency | HIGH | 42 cancelled orders were physically shipped and delivered (unbilled goods leakage). |
| **ISSUE-10** | `fct_shipments.shipped_date` | Consistency | HIGH | 38 shipments show negative fulfillment times due to warehouse terminal UTC/EST mismatch. |
| **ISSUE-20** | `fct_inventory.warehouse_id` | Distribution | LOW | 100% of rows defaulted to 'WH-DEFAULT', preventing regional facility allocation. |
| **ISSUE-22** | `dim_products.weight_kg` | Distribution | HIGH | 5,000 kg weights on phone accessories abort automated freight rate quotes. |

---

## 2. Immediate Analytics Filters (Interim Reporting)

Operations analysts must apply the following SQL logic for operational reports and daily replenishment calculations:

```sql
-- Safe Fulfillment & Lead-Time KPI Query
SELECT 
    s.carrier,
    COUNT(s.shipment_id) AS total_shipments,
    -- Reconcile missing delivery date with estimated 3-day turnaround
    AVG(CASE 
        WHEN s.delivered_date IS NULL AND s.shipping_status = 'Delivered' 
            THEN 3.0 * 24.0
        ELSE (JULIANDAY(s.delivered_date) - JULIANDAY(s.shipped_date)) * 24.0 
    END) AS avg_delivery_hours,
    -- Filter out retro-causal shipments (ISSUE-10) for pure lead time calculations
    AVG(CASE 
        WHEN s.shipped_date >= o.order_date 
            THEN (JULIANDAY(s.shipped_date) - JULIANDAY(o.order_date)) * 24.0 
        ELSE 24.0 
    END) AS avg_fulfillment_hours
FROM fct_shipments s
JOIN fct_orders o ON s.order_id = o.order_id
GROUP BY s.carrier;

-- Corrected Product Weight & Freight Cost Estimation
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    -- Cleanse gram-to-kg outlier (ISSUE-22)
    CASE 
        WHEN p.weight_kg > 50.0 AND p.category IN ('Electronics', 'Accessories') 
            THEN ROUND(p.weight_kg / 1000.0, 2)
        ELSE p.weight_kg 
    END AS sanitized_weight_kg
FROM dim_products p;
```

---

## 3. Permanent Operational Playbooks & Engineering Actions

1. **JIRA-OPS-201 (3PL Carrier Webhook Resiliency)**:
   - Patch logistics ingestion microservice to parse alternative delivery date fields (`actual_delivery_date`, `delivered_timestamp`) in carrier JSON webhooks.
2. **JIRA-OPS-215 (NTP Time Synchronization across Hubs)**:
   - Reconfigure warehouse barcode scanning terminals to sync with corporate UTC NTP servers every 15 minutes.
3. **JIRA-OPS-220 (Inventory Safety Stock Defaulting)**:
   - Mandate `reorder_point` in the merchant product portal; deploy automated fallback formula `(2 * lead_time_days * avg_daily_sales)` when blank.
4. **JIRA-OPS-235 (Fulfillment Cutoff Synchronization)**:
   - Implement real-time cancellation broadcast to 3PL logistics dispatch queues to prevent physical shipping of cancelled orders (halt ISSUE-08).
