# Data Quality Rules, Thresholds & SLA Governance Framework

This document outlines the enterprise governance rules, evaluation thresholds, and SLA standards implemented within the Data Profiling, Quality & Validation Framework.

---

## 1. Governance Principles & Quality Dimensions

Data quality is evaluated continuously across **4 Core Dimensions**:

1. **Completeness**: Data is populated without missing, null, or blank values in required business attributes.
2. **Consistency**: Data adheres to referential integrity constraints, relational cross-table contracts, and chronological causality.
3. **Accuracy & Validity**: Values reside strictly within legitimate domain ranges, conforms to regex patterns, and respects mathematical invariants.
4. **Distribution & Statistical Health**: Numeric attributes are free of unhandled extreme outliers (>3 IQR / z > 3.5), zero-variance degeneracies, and spurious frequency spikes.

---

## 2. Global Quality KPI Thresholds

| KPI Code | KPI Description | Target SLA | Warning Threshold | Critical Breach | Evaluation Frequency | Action on Critical |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| `DQ_INDEX` | Weighted overall quality score | `>= 95.0%` | `90.0% - 94.9%` | `< 90.0%` | Daily Post-ETL | Page Data Engineering On-Call |
| `COMPLETENESS_RATE` | Required non-null attributes rate | `>= 98.0%` | `95.0% - 97.9%` | `< 95.0%` | Every Ingestion Batch | Halt downstream mart loading |
| `CONSISTENCY_RATE` | Foreign keys & causality compliance | `>= 99.0%` | `95.0% - 98.9%` | `< 95.0%` | Every Ingestion Batch | Quarantine orphan records |
| `ACCURACY_RATE` | Domain bounds & regex compliance | `>= 98.5%` | `95.0% - 98.4%` | `< 95.0%` | Every Ingestion Batch | Route to error staging table |
| `DISTRIBUTION_HEALTH`| Non-outlier numeric column health | `>= 96.0%` | `90.0% - 95.9%` | `< 90.0%` | Daily Summary Batch | Notify Analytics Leads |
| `FRESHNESS_SLA` | Timely data arrival within SLA | `>= 99.5%` | `97.0% - 99.4%` | `< 97.0%` | Hourly Pipeline Probe | Trigger source CDC retry |

---

## 3. Severity Classification & Response Matrix

| Severity Level | Definition | Impact on Downstream Reporting | Response Time SLA | Remediation Ownership |
| :--- | :--- | :--- | :---: | :--- |
| **CRITICAL** | Systemic failure breaking financial reports, primary keys, or orphan foreign keys. | Downstream dashboards paused; ETL halted. | `< 2 Hours` | Data Engineering & Source System Owner |
| **HIGH** | Significant business logic violation (e.g. inverted margins, retroactive shipments). | Downstream metrics distorted; interim filter applied. | `< 8 Hours` | Domain Data Steward |
| **MEDIUM** | Non-standard formats, minor duplicate profiles, or localized survey scale mixing. | Aesthetic or minor statistical variance in reports. | `< 24 Hours` | Analytics Engineering |
| **LOW** | Minor demographic nulls (e.g. non-critical telephone numbers, postal formats). | Minimal analytics impact; cosmetic cleansing. | `< 72 Hours` | Downstream Analytics Team |

---

## 4. Rule Definition Catalog (Summary across 8 Datasets)

### 4.1 Master Dimension Tables (`dim_customers`, `dim_products`)
- `RULE-CUST-01`: `customer_id` must be non-null and uniquely indexed (`CRITICAL`).
- `RULE-CUST-02`: `email` must be populated and follow standard RFC-5322 regex (`HIGH`).
- `RULE-CUST-03`: `email` must be globally unique across active customer accounts (`MEDIUM`).
- `RULE-CUST-04`: `phone` must not be null for VIP and Corporate tiers (`LOW`).
- `RULE-CUST-05`: `postal_code` must match `^\d{5}(-\d{4})?$` for US customers (`LOW`).
- `RULE-PROD-01`: `product_id` must be non-null and unique (`CRITICAL`).
- `RULE-PROD-02`: `unit_price` must be strictly greater than or equal to `unit_cost` (`HIGH`).
- `RULE-PROD-03`: `weight_kg` must not exceed 50.0 kg for consumer catalog items (`HIGH`).

### 4.2 Transactional Fact Tables (`fct_orders`, `fct_order_items`, `fct_payments`, `fct_shipments`)
- `RULE-ORD-01`: `order_id` must be non-null and unique (`CRITICAL`).
- `RULE-ORD-02`: `customer_id` must be non-null and exist in `dim_customers` (`CRITICAL`).
- `RULE-ORD-03`: `currency` must be normalized to uppercase ISO-4217 code `USD` (`MEDIUM`).
- `RULE-ORD-04`: `total_amount` must be between $0.01 and $25,000.00 (`CRITICAL`).
- `RULE-ORD-05`: `order_status` 'Cancelled' must not have corresponding 'Delivered' in `fct_shipments` (`HIGH`).
- `RULE-ITEM-01`: `quantity` must be strictly positive integer (`CRITICAL`).
- `RULE-ITEM-02`: `discount_rate` must be between 0.00 and 1.00 (`HIGH`).
- `RULE-ITEM-03`: `product_id` must exist in active `dim_products` catalog (`CRITICAL`).
- `RULE-PAY-01`: `gateway_transaction_id` must not be null for 'Success' payments (`CRITICAL`).
- `RULE-PAY-02`: `amount_paid` must match `fct_orders.total_amount` within $0.01 (`CRITICAL`).
- `RULE-SHIP-01`: `delivered_date` must not be null when `shipping_status` is 'Delivered' (`HIGH`).
- `RULE-SHIP-02`: `shipped_date` must be chronologically greater than or equal to `order_date` (`HIGH`).

### 4.3 Operational Fact Tables (`fct_inventory`, `fct_customer_interactions`)
- `RULE-INV-01`: `reorder_point` must not be null (`MEDIUM`).
- `RULE-INV-02`: `warehouse_id` must have distinct count >= 2 (non-degenerate) (`LOW`).
- `RULE-INT-01`: `interaction_date` must not be in the future (`MEDIUM`).
- `RULE-INT-02`: `rating_score` must be between 1 and 5 (`MEDIUM`).
- `RULE-INT-03`: `resolution_time_mins` must not exceed 2,880 minutes (`MEDIUM`).
