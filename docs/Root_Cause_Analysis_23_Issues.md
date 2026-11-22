# Root Cause Analysis: Comprehensive Catalog of 23 Flagged Data Quality Issues

This document provides in-depth technical Root Cause Analysis (RCA), downstream business impact assessments, and remediation procedures for all **23 flagged data quality anomalies** discovered across the 8 enterprise datasets.

---

## Summary Matrix of 23 Flagged Issues

| Issue ID | Dataset | Target Column | Dimension | Severity | Violations | Downstream Analytics Team | Upstream Origin |
| :--- | :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| **ISSUE-01** | `dim_customers` | `email` | Completeness | HIGH | 125 (5.0%) | Marketing & Growth | Guest checkout migration dropped email field |
| **ISSUE-02** | `fct_orders` | `customer_id` | Completeness | CRITICAL | 200 (4.0%) | Marketing & Growth | Microservice dropped session token during 1-click checkout |
| **ISSUE-03** | `fct_shipments` | `delivered_date` | Completeness | HIGH | 210 (6.2%) | Supply Chain & Ops | Carrier webhook dropped ISO-8601 delivery date |
| **ISSUE-04** | `fct_inventory` | `reorder_point` | Completeness | MEDIUM | 112 (7.0%) | Supply Chain & Ops | New SKU onboarding form allowed null safety stocks |
| **ISSUE-05** | `dim_customers` | `phone` | Completeness | LOW | 160 (8.0%) | Marketing & Growth | Social login OAuth bypassed secondary contact step |
| **ISSUE-06** | `fct_payments` | `gateway_transaction_id` | Completeness | CRITICAL | 234 (4.5%) | Financial & Revenue | Manual offline B2B bank wire entered without txn reference |
| **ISSUE-07** | `fct_order_items`| `product_id` | Consistency | CRITICAL | 35 (0.3%) | Financial & Revenue | Hard deletion in staging DB instead of soft-delete |
| **ISSUE-08** | `fct_orders` | `order_status` | Consistency | HIGH | 42 (0.8%) | Supply Chain & Ops | Cancelled order fulfilled due to 3PL queue lag |
| **ISSUE-09** | `fct_orders` | `currency` | Consistency | MEDIUM | 185 (3.7%) | Financial & Revenue | Non-standard frontend currency strings ('usd', 'US_DOLLAR') |
| **ISSUE-10** | `fct_shipments` | `shipped_date` | Consistency | HIGH | 38 (0.8%) | Supply Chain & Ops | Warehouse scanner clock in UTC vs Order service in EST |
| **ISSUE-11** | `fct_payments` | `amount_paid` | Consistency | CRITICAL | 65 (1.3%) | Financial & Revenue | Cart discount applied after payment authorization hold |
| **ISSUE-12** | `dim_customers` | `email` | Consistency | MEDIUM | 28 (1.1%) | Marketing & Growth | Case-sensitive CRM upsert allowed duplicate profiles |
| **ISSUE-13** | `fct_order_items`| `quantity` | Accuracy | CRITICAL | 45 (0.4%) | Financial & Revenue | Customer returns appended to sales line items table |
| **ISSUE-14** | `fct_order_items`| `discount_rate` | Accuracy | HIGH | 25 (0.2%) | Financial & Revenue | Stacked coupon promo codes exceeded 100% discount |
| **ISSUE-15** | `fct_customer_interactions`| `interaction_date` | Accuracy | MEDIUM | 32 (1.0%) | Marketing & Growth | Client browser clock drift recorded future timestamps |
| **ISSUE-16** | `dim_customers` | `postal_code` | Accuracy | LOW | 78 (3.1%) | Marketing & Growth | Missing client-side regex mask on legacy portal |
| **ISSUE-17** | `dim_products` | `unit_cost` | Accuracy | HIGH | 24 (3.0%) | Financial & Revenue | ERP CSV upload swapped unit_cost and unit_price fields |
| **ISSUE-18** | `fct_customer_interactions`| `rating_score` | Accuracy | MEDIUM | 36 (1.1%) | Marketing & Growth | Vendor 10-point NPS survey loaded directly into 5-star CSAT |
| **ISSUE-19** | `fct_orders` | `total_amount` | Distribution | CRITICAL | 3 (0.1%) | Financial & Revenue | Simulated $9,999,999 QA test orders in production DW |
| **ISSUE-20** | `fct_inventory` | `warehouse_id` | Distribution | LOW | 1,600 (100%) | Supply Chain & Ops | Inventory sync pipeline defaulted warehouse to 'WH-DEFAULT' |
| **ISSUE-21** | `fct_customer_interactions`| `resolution_time_mins`| Distribution | MEDIUM | 18 (0.6%) | Marketing & Growth | Abandoned tickets left open 30+ days without auto-close |
| **ISSUE-22** | `dim_products` | `weight_kg` | Distribution | HIGH | 15 (1.9%) | Supply Chain & Ops | EDI feed transmitted weights in grams instead of kilograms |
| **ISSUE-23** | `fct_orders` | `discount_amount`| Distribution | MEDIUM | 480 (9.6%) | Financial & Revenue | Penny-rounding logic generated spurious $0.01 discounts |

---

## Detailed Root Cause Analysis by Issue

### ISSUE-01: Null Customer Emails (`dim_customers.email`)
- **Root Cause**: During the Q3 legacy customer database migration, guest checkout profiles that lacked registered emails were migrated with `NULL` instead of a standardized guest pseudo-identifier.
- **Downstream Impact**: Marketing email nurture sequences and automated order confirmation delivery dropped for 125 customers.
- **Remediation**: Implemented fallback deterministic formatting `guest_<cust_id>@unregistered.internal`. Updated migration schema constraint to `NOT NULL`.

### ISSUE-02: Missing Customer IDs (`fct_orders.customer_id`)
- **Root Cause**: Express one-click checkout microservice had a race condition where the auth session token expired during payment authorization, dropping the customer UUID before writing to the Kafka order-created event.
- **Downstream Impact**: Marketing attribution, cohort retention calculations, and Customer Lifetime Value (LTV) models were corrupted by unattributed orders ($48,200 GMV unlinked).
- **Remediation**: Backfilled `customer_id` via credit card token and billing email cross-reference. Added schema-level message validation in Kafka topic schema registry.

### ISSUE-03: Null Delivered Date for Delivered Shipments (`fct_shipments.delivered_date`)
- **Root Cause**: Carrier webhook payload parser for USPS delivered notifications failed on a JSON key mismatch (`actual_delivery_date` vs `delivery_timestamp`), resulting in `NULL` insertions.
- **Downstream Impact**: Logistics KPI On-Time In-Full (OTIF) could not be calculated for 210 deliveries; downstream carrier SLA penalty claims failed.
- **Remediation**: Patched webhook parser with resilient multi-key JSON fallback; backfilled delivery dates using carrier tracking API bulk lookup.

### ISSUE-04: Null Reorder Point in Inventory (`fct_inventory.reorder_point`)
- **Root Cause**: New SKU onboarding portal did not mandate inventory safety stock parameters, allowing merchant procurement specialists to save records without setting replenishment thresholds.
- **Downstream Impact**: Automated warehouse replenishment purchasing script skipped 112 SKUs, resulting in preventable stockouts.
- **Remediation**: Defaulted missing reorder points to category median safety formula: `(2 * lead_time_days * avg_daily_demand)`. Added frontend form validation requirement.

### ISSUE-05: Missing Phone Numbers for VIP / Corporate Customers (`dim_customers.phone`)
- **Root Cause**: Social authentication (Google & Apple Sign-In) bypassed the mobile number collection step without triggering the post-registration profile completion modal for upgraded accounts.
- **Downstream Impact**: VIP concierge support team and SMS delivery dispatch could not contact high-value clients.
- **Remediation**: Implemented in-app notification prompt for VIP tier accounts; added fallback retrieval from billing gateway customer records.

### ISSUE-06: Missing Gateway Transaction ID on Settled Payments (`fct_payments.gateway_transaction_id`)
- **Root Cause**: Accounting operations team manually logged high-value B2B bank wire payments in the ERP without entering the banking clearance reference code.
- **Downstream Impact**: Financial reconciliation between ERP and corporate banking statements had 234 unverified transactions ($182,400 variance).
- **Remediation**: Added constraint requiring wire clearance reference for manual transaction entries; backfilled wire reference from banking daily reconciliation file.

### ISSUE-07: Orphan Order Items Referencing Non-Existent Products (`fct_order_items.product_id`)
- **Root Cause**: Staging database cleanup script executed `DELETE FROM dim_products` for test SKUs that had already been referenced in active sales order items.
- **Downstream Impact**: Financial product line revenue reporting and gross margin calculations threw SQL join errors or omitted 35 line items.
- **Remediation**: Enforced `ON DELETE RESTRICT` foreign key constraint in PostgreSQL. Restored soft-delete flag `is_active = FALSE` for archived products.

### ISSUE-08: Cancelled Order with Delivered Shipment (`fct_orders.order_status` vs `fct_shipments.shipping_status`)
- **Root Cause**: Customer service cancellation webhook arrived after warehouse picking cutoff. Cancellation was recorded in orders database, but 3PL dispatch queue failed to halt physical shipment.
- **Downstream Impact**: Double inventory depletion and uncollected payments (goods delivered for cancelled, unbilled orders).
- **Remediation**: Automated status reconciliation: updated order status to `Return_Pending`, dispatched automated return shipping label, and billed account upon non-return.

### ISSUE-09: Non-Standard Currency Codes (`fct_orders.currency`)
- **Root Cause**: Mobile app versions 2.1 and web checkout checkout endpoints sent unvalidated currency strings (`usd`, `US_DOLLAR`, `$`) instead of ISO-4217 code `USD`.
- **Downstream Impact**: Multi-currency conversion microservice treated non-standard strings as foreign exchange tokens, triggering conversion errors in financial audits.
- **Remediation**: Implemented centralized API gateway string sanitization: `UPPER(TRIM(currency))` and mapped legacy aliases to `USD`.

### ISSUE-10: Retroactive Shipped Date (`fct_shipments.shipped_date` < `fct_orders.order_date`)
- **Root Cause**: Warehouse dispatch scanning terminals operated on UTC timezone clock, whereas order capture microservices logged in US Eastern Standard Time (EST = UTC-5).
- **Downstream Impact**: Fulfillment lead-time analytics reported negative fulfillment durations (-5 hours) for 38 orders.
- **Remediation**: Synchronized all warehouse IoT scanning devices to NTP servers and standardized all backend timestamp columns to UTC.

### ISSUE-11: Payment Amount Mismatch with Order Total (`fct_payments.amount_paid` != `fct_orders.total_amount`)
- **Root Cause**: Promotional cart discount coupon was applied asynchronously after the credit card authorization hold was created, but before capture settlement, causing a variance between captured payment and order ledger.
- **Downstream Impact**: General ledger imbalances across 65 accounts, creating variance between accounts receivable and payment gateway balances.
- **Remediation**: Introduced distributed two-phase commit on cart checkout; automated differential ledger refund or invoice adjustment for past variances.

### ISSUE-12: Duplicate Customer Email Profiles (`dim_customers.email`)
- **Root Cause**: Customer profile upsert logic did not perform case-insensitive normalization, treating `John.Doe@example.com` and `john.doe@example.com` as distinct entities.
- **Downstream Impact**: Marketing attribution double-counted unique customer reach and split customer order history across duplicate profiles.
- **Remediation**: Enforced `LOWER(TRIM(email))` in customer ingestion service; executed entity resolution merge combining order histories into primary customer ID.

### ISSUE-13: Negative Line Item Quantities (`fct_order_items.quantity` < 1)
- **Root Cause**: Return credit transactions and merchandise allowances were incorrectly appended to the active sales transactions line table rather than the returns sub-ledger.
- **Downstream Impact**: Sales volume counts were distorted; units sold metrics were inaccurate in financial reporting.
- **Remediation**: Split returns into dedicated `fct_returns` ledger; applied database `CHECK (quantity > 0)` constraint on sales order items.

### ISSUE-14: Impossible Discount Rate (`fct_order_items.discount_rate` > 1.0)
- **Root Cause**: Promotional coupon service additively stacked a 100% gift voucher with a 25% category discount, yielding `discount_rate = 1.25` (125%).
- **Downstream Impact**: Line item total price calculated negative revenue, requiring manual accounting interventions.
- **Remediation**: Capped compound promotional discount logic at 0.50 (50% max promotional cap); recomputed line totals.

### ISSUE-15: Future Event Timestamps (`fct_customer_interactions.interaction_date`)
- **Root Cause**: Support representative client machine clock had drifted forward by months, and ticket creation API trusted client-side timestamp payload.
- **Downstream Impact**: Daily active ticket volume charts and SLA resolution metrics showed anomalous future tickets in dashboard projections.
- **Remediation**: Configured PostgreSQL `DEFAULT CURRENT_TIMESTAMP` for interaction dates and rejected client-provided timestamp headers.

### ISSUE-16: Malformed US Postal Codes (`dim_customers.postal_code`)
- **Root Cause**: Legacy web signup form lacked client-side regex mask validation, allowing users to enter non-standard characters (e.g. `ZIP-90210??`, `ABCDE`).
- **Downstream Impact**: Address validation failed during shipping label generation, causing carrier delivery exceptions and address correction surcharges.
- **Remediation**: Cleaned postal codes with regex `^\d{5}$`; integrated address validation API at checkout.

### ISSUE-17: Inverted Pricing Economics (`dim_products.unit_cost` > `dim_products.unit_price`)
- **Root Cause**: Supplier catalog upload batch job accidentally mapped column 5 (MSRP wholesale price) to unit cost and column 6 (procurement cost) to unit price.
- **Downstream Impact**: 24 products reported negative gross margins (-35%), triggering automated pricing alert cancellations.
- **Remediation**: Swapped inverted cost and price columns in product master database; corrected supplier feed mapping configuration.

### ISSUE-18: Out-of-Bounds CSAT Rating Scores (`fct_customer_interactions.rating_score` > 5)
- **Root Cause**: NPS survey vendor (10-point scale) results were directly loaded into 5-star CSAT database column without score normalization.
- **Downstream Impact**: Customer Satisfaction (CSAT) average score inflated from 4.1 to 4.8 across impacted categories.
- **Remediation**: Rescaled 10-point scores using `CEIL(score / 2.0)` to normalize to 1-5 scale; created distinct column for NPS metrics.

### ISSUE-19: Extreme Monetary QA Outlier (`fct_orders.total_amount` = $9,999,999.00)
- **Root Cause**: QA automated load testing scripts used synthetic orders with $9,999,999 totals in staging, which inadvertently replicated to the production data lake due to a misconfigured pipeline filter.
- **Downstream Impact**: Total daily revenue was inflated by $30 million, distorting executive reporting and investor metrics.
- **Remediation**: Added production filter excluding test customer accounts (`is_test = TRUE`); implemented statistical outlier filter isolating records > 4 sigma.

### ISSUE-20: Degenerate Zero-Variance Warehouse Location (`fct_inventory.warehouse_id`)
- **Root Cause**: Warehouse inventory synchronization pipeline defaulted location code to `'WH-DEFAULT'` for all rows during multi-facility ERP cutover.
- **Downstream Impact**: Supply chain distribution planning could not allocate inventory across regional distribution centers (East, West, Central, South).
- **Remediation**: Reprocessed inventory snapshots using location cross-reference table; re-established multi-facility tracking.

### ISSUE-21: Extreme Resolution Time Duration Outliers (`fct_customer_interactions.resolution_time_mins` > 43,200)
- **Root Cause**: Customer service tickets left in 'Awaiting Customer Response' status remained unclosed for over 30 days without an automated inactivity timeout.
- **Downstream Impact**: Average resolution time metric was skewed from 42 minutes to 180 minutes, creating false SLA breach alerts for support leadership.
- **Remediation**: Paused duration timer during customer wait periods; implemented automated 72-hour ticket auto-closure trigger.

### ISSUE-22: Extreme Physical Product Weight Outliers (`dim_products.weight_kg` > 5,000 kg)
- **Root Cause**: Supplier EDI feed transmitted product weights in grams without applying the 1/1000 metric conversion factor to kilograms.
- **Downstream Impact**: Freight logistics calculation estimated $12,000 shipping costs for a smartphone screen protector, aborting automated shipping quotes.
- **Remediation**: Applied conditional conversion `weight_kg = weight_kg / 1000` for consumer accessories exceeding 50 kg; updated carrier rate calculator.

### ISSUE-23: Bimodal Penny-Rounding Discount Spike (`fct_orders.discount_amount` = $0.01)
- **Root Cause**: Currency rounding logic in split-tender checkout (e.g. paying partially with gift card and credit card) generated spurious $0.01 discount line items to balance penny differences.
- **Downstream Impact**: Distribution skew with 480 spurious discount records distorting promo campaign effectiveness analysis.
- **Remediation**: Reallocated fractional penny rounding differences to merchant payment processing fee expense ledger; eliminated artificial discount entries.
