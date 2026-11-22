# Data Profiling, Quality & Validation Framework: Executive Summary

**Generated**: Automatically via Great Expectations & pandas Validation Pipeline
**Total Profiled Datasets**: 8 | **Total Profiled Columns**: 73 | **Total Records Ingested**: 35,600

---

## 1. Executive Quality KPIs Scorecard (6 Core KPIs)

| KPI Metric | Value | Target SLA | Status | Quality Dimension |
| :--- | :---: | :---: | :---: | :--- |
| **Overall Data Quality Index** | `54.17%` | `95.0%` | **CRITICAL** | Composite / Specific |
| **Completeness Rate** | `60.0%` | `98.0%` | **CRITICAL** | Composite / Specific |
| **Consistency & Referential Integrity Rate** | `60.0%` | `99.0%` | **CRITICAL** | Composite / Specific |
| **Accuracy & Validity Rate** | `64.71%` | `98.5%` | **CRITICAL** | Composite / Specific |
| **Distribution & Statistical Health Score** | `0.0%` | `96.0%` | **CRITICAL** | Composite / Specific |
| **Freshness & Timeliness SLA Compliance Rate** | `99.8%` | `99.5%` | **PASS** | Composite / Specific |

---

## 2. Quality Dimension Health Breakdown

| Dimension | Health Score | Passing Expectations | Total Expectations Evaluated |
| :--- | :---: | :---: | :---: |
| **Completeness** | `60.0%` | 9 | 15 |
| **Consistency** | `60.0%` | 9 | 15 |
| **Accuracy** | `64.71%` | 11 | 17 |
| **Distribution** | `0.0%` | 0 | 5 |

---

## 3. Flagged Data Quality Issues Catalog (23 Issues Detected)

| Issue ID | Dataset | Target Column | Dimension | Severity | Violations | Downstream Team | Root Cause & Remediation Summary |
| :--- | :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| `ISSUE-01` | **dim_customers** | `email` | Completeness | `HIGH` | 122 (4.88%) | *Marketing & Growth Analytics* | **Root Cause**: Customer contact email must be populated<br>**Remediation**: Apply deterministic placeholder email format (guest_<cust_id>@unregistered.internal) and enforce email validation at signup UI. |
| `ISSUE-12` | **dim_customers** | `email` | Consistency | `MEDIUM` | 56 (2.35%) | *Marketing & Growth Analytics* | **Root Cause**: Customer email addresses must be globally unique across profiles<br>**Remediation**: Apply LOWER(TRIM(email)) in ETL merge pipeline; merge duplicate customer histories into primary canonical customer UUID. |
| `ISSUE-05` | **dim_customers** | `phone` | Completeness | `LOW` | 160 (25.76%) | *Marketing & Growth Analytics* | **Root Cause**: VIP and Corporate customers must have telephone numbers<br>**Remediation**: Trigger automated in-app profile completion prompt for tier upgrade qualification; fall back to billing telephone record. |
| `ISSUE-16` | **dim_customers** | `postal_code` | Accuracy | `LOW` | 78 (4.15%) | *Marketing & Growth Analytics* | **Root Cause**: US postal codes must conform to standard 5-digit or 9-digit ZIP regex<br>**Remediation**: Cleanse string with regex extraction r'^(\d{5})(-\d{4})?$'; integrate USPS Address Verification API at checkout. |
| `ISSUE-17` | **dim_products** | `` | Accuracy | `HIGH` | 24 (3.0%) | *Financial & Revenue Analytics* | **Root Cause**: Product unit_price must exceed unit_cost (positive gross margin)<br>**Remediation**: Swap inverted cost and price attributes; notify merchant pricing team and halt automated clearance markdown rules. |
| `ISSUE-22` | **dim_products** | `weight_kg` | Distribution | `HIGH` | 15 (1.88%) | *Supply Chain & Operations Analytics* | **Root Cause**: Product weight must not contain extreme anomalies (> 50kg for retail)<br>**Remediation**: Apply conditional conversion (weight_kg = weight_kg / 1000) when category is 'Accessories' and weight > 50kg; update freight rate quotes. |
| `ISSUE-02` | **fct_orders** | `customer_id` | Completeness | `CRITICAL` | 200 (4.0%) | *Marketing & Growth Analytics* | **Root Cause**: Orders must be associated with a valid customer_id<br>**Remediation**: Backfill customer_id from payment gateway payer email lookup; reject order creation events lacking customer UUID in Kafka topic. |
| `ISSUE-09` | **fct_orders** | `currency` | Consistency | `MEDIUM` | 185 (3.7%) | *Financial & Revenue Analytics* | **Root Cause**: Order currency must be standardized to ISO-4217 uppercase 'USD'<br>**Remediation**: Standardize ingestion to ISO-4217 3-letter currency codes via uppercase string transformation and strict enum validation. |
| `ISSUE-19` | **fct_orders** | `total_amount` | Distribution | `CRITICAL` | 3 (0.06%) | *Financial & Revenue Analytics* | **Root Cause**: Order total must be free of extreme synthetic QA test amounts ($9,999,999)<br>**Remediation**: Exclude synthetic test account orders with flag is_test = TRUE; tag and isolate transactions exceeding 4 sigma from executive reporting. |
| `ISSUE-23` | **fct_orders** | `discount_amount` | Distribution | `MEDIUM` | 480 (9.6%) | *Financial & Revenue Analytics* | **Root Cause**: Discount amount must not exhibit rounding clusters of $0.01<br>**Remediation**: Absorb rounding fractions into payment processor fee account; eliminate spurious $0.01 promotional records. |
| `ISSUE-08` | **fct_orders** | `` | Consistency | `HIGH` | 244 (5.08%) | *Supply Chain & Operations Analytics* | **Root Cause**: Cancelled orders must not have conflicting Delivered status in shipments<br>**Remediation**: Reconcile order state to 'Return_Pending'; auto-generate prepaid return label and trigger customer returns notification. |
| `ISSUE-07` | **fct_order_items** | `product_id` | Consistency | `CRITICAL` | 35 (0.28%) | *Financial & Revenue Analytics* | **Root Cause**: Order items product_id must exist in active product catalog master<br>**Remediation**: Implement foreign key constraint with RESTRICT ON DELETE; restore soft-deleted product records with 'Archived' status. |
| `ISSUE-13` | **fct_order_items** | `quantity` | Accuracy | `CRITICAL` | 45 (0.36%) | *Financial & Revenue Analytics* | **Root Cause**: Item quantity must be strictly positive (no negative returns in sales ledger)<br>**Remediation**: Route negative adjustments to dedicated fct_returns table; enforce CHECK (quantity > 0) constraint in sales transaction schema. |
| `ISSUE-14` | **fct_order_items** | `discount_rate` | Accuracy | `HIGH` | 25 (0.2%) | *Financial & Revenue Analytics* | **Root Cause**: Discount rate must be bounded between 0% and 100% (0.0 to 1.0)<br>**Remediation**: Cap discount rate at 1.0 (or max permissible promotional threshold 0.70); recalculate line total item price. |
| `ISSUE-06` | **fct_payments** | `gateway_transaction_id` | Completeness | `CRITICAL` | 234 (4.87%) | *Financial & Revenue Analytics* | **Root Cause**: Settled payments with status 'Success' must have gateway transaction ID<br>**Remediation**: Require accounting clearing reference number for manual B2B transactions; enforce non-null constraint at payment service layer. |
| `ISSUE-11` | **fct_payments** | `` | Consistency | `CRITICAL` | 73 (1.52%) | *Financial & Revenue Analytics* | **Root Cause**: Settled payment amount must reconcile identically with order total<br>**Remediation**: Execute automated differential ledger refund or invoice adjustment; implement two-phase commit on cart checkout settlement. |
| `ISSUE-03` | **fct_shipments** | `delivered_date` | Completeness | `HIGH` | 210 (5.83%) | *Supply Chain & Operations Analytics* | **Root Cause**: Shipments marked 'Delivered' must record delivered_date timestamp<br>**Remediation**: Extract delivery timestamp from carrier tracking raw payload; patch webhook parser to handle carrier-specific status date schemas. |
| `ISSUE-10` | **fct_shipments** | `` | Consistency | `HIGH` | 38 (0.79%) | *Supply Chain & Operations Analytics* | **Root Cause**: Temporal causality: shipped_date must occur chronologically after order_date<br>**Remediation**: Normalize all timestamp ingestions to UTC at API gateway; flag and recalculate shipment lead times with timezone offsets. |
| `ISSUE-04` | **fct_inventory** | `reorder_point` | Completeness | `MEDIUM` | 112 (7.0%) | *Supply Chain & Operations Analytics* | **Root Cause**: Inventory stock records must define an active reorder_point threshold<br>**Remediation**: Default reorder point to category median safety stock formula (2 * lead_time_days * avg_daily_sales) upon SKU activation. |
| `ISSUE-20` | **fct_inventory** | `warehouse_id` | Distribution | `LOW` | 1,600 (100.0%) | *Supply Chain & Operations Analytics* | **Root Cause**: Warehouse location must not be a zero-variance degenerate constant ('WH-DEFAULT')<br>**Remediation**: Reprocess inventory snapshots using location cross-reference table; re-enable multi-facility inventory allocation. |
| `ISSUE-15` | **fct_customer_interactions** | `interaction_date` | Accuracy | `MEDIUM` | 32 (1.0%) | *Marketing & Growth Analytics* | **Root Cause**: Interaction timestamps must not be set to future dates<br>**Remediation**: Overwrite client-provided timestamp with server-side database CURRENT_TIMESTAMP upon ticket creation. |
| `ISSUE-18` | **fct_customer_interactions** | `rating_score` | Accuracy | `MEDIUM` | 36 (1.12%) | *Marketing & Growth Analytics* | **Root Cause**: CSAT rating scores must fall strictly within the 1 to 5 scale<br>**Remediation**: Rescale 10-point NPS scores to 5-star metric: CEIL(nps_score / 2.0); create distinct columns for NPS vs CSAT. |
| `ISSUE-21` | **fct_customer_interactions** | `resolution_time_mins` | Distribution | `MEDIUM` | 18 (0.56%) | *Marketing & Growth Analytics* | **Root Cause**: Ticket resolution time must not have idle extreme outliers (> 48 hours / 2880 mins)<br>**Remediation**: Deduct paused customer-wait time from total duration; implement automated 72-hour ticket auto-close trigger. |

---

## 4. Dataset Profiling Summary (8 Tables)

| Dataset Name | Primary Key | Row Count | Columns | Memory (MB) | Null Cells | Completeness % |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `dim_customers` | `customer_id` | 2,500 | 10 | 1.394 | 282 | `98.87%` |
| `dim_products` | `product_id` | 800 | 10 | 0.305 | 0 | `100.0%` |
| `fct_orders` | `order_id` | 5,000 | 11 | 2.103 | 200 | `99.64%` |
| `fct_order_items` | `item_id` | 12,500 | 8 | 3.197 | 0 | `100.0%` |
| `fct_payments` | `payment_id` | 5,200 | 9 | 2.136 | 234 | `99.5%` |
| `fct_shipments` | `shipment_id` | 4,800 | 10 | 2.47 | 1,405 | `97.07%` |
| `fct_inventory` | `inventory_id` | 1,600 | 7 | 0.394 | 112 | `99.0%` |
| `fct_customer_interactions` | `interaction_id` | 3,200 | 8 | 0.972 | 0 | `100.0%` |

---
*Report generated by Antigravity Data Quality Validation Engine 2025.*