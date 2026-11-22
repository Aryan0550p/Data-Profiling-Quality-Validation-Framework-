# Downstream Remediation Playbook: Financial & Revenue Analytics Team

**Target Stakeholders**: Financial Analysts, Revenue Operations Engineers, Corporate Controllers, Accounting Auditors  
**Governed Data Domains**: Sales Orders (`fct_orders`), Order Items (`fct_order_items`), Payments (`fct_payments`), Product Pricing (`dim_products`)

---

## 1. Executive Summary & Impact Analysis

Financial and Revenue analytics governs Gross Merchandise Value (GMV), Net Revenue, Gross Margins, Ledger Reconciliations, and compliance with GAAP revenue recognition standards.

The framework identified **9 data quality issues** impacting the Finance domain:

| Issue ID | Entity & Column | Dimension | Severity | Business Risk |
| :--- | :--- | :--- | :---: | :--- |
| **ISSUE-06** | `fct_payments.gateway_transaction_id` | Completeness | CRITICAL | 234 settled wire payments lack clearing reference; un-auditable ledger. |
| **ISSUE-07** | `fct_order_items.product_id` | Consistency | CRITICAL | Orphan items referencing deleted SKUs; financial margin joins drop sales lines. |
| **ISSUE-09** | `fct_orders.currency` | Consistency | MEDIUM | Mixed currency strings ('usd', 'US_DOLLAR') cause foreign exchange conversion failures. |
| **ISSUE-11** | `fct_payments.amount_paid` | Consistency | CRITICAL | 65 settled payments have monetary variance from order total ($14,500 variance). |
| **ISSUE-13** | `fct_order_items.quantity` | Accuracy | CRITICAL | Negative quantities (-1 to -5) in active sales table corrupt volume metrics. |
| **ISSUE-14** | `fct_order_items.discount_rate` | Accuracy | HIGH | Discount rates exceeding 100% (up to 250%) calculate negative net revenue. |
| **ISSUE-17** | `dim_products.unit_cost` | Accuracy | HIGH | Procurement cost and MSRP swapped; false negative gross margins (-35%). |
| **ISSUE-19** | `fct_orders.total_amount` | Distribution | CRITICAL | $9,999,999 QA synthetic orders inflate reported daily revenue by $30M. |
| **ISSUE-23** | `fct_orders.discount_amount` | Distribution | MEDIUM | 480 spurious $0.01 penny-rounding discount entries skew promotion analyses. |

---

## 2. Immediate Analytics Filters (Interim Reporting)

Finance analysts and corporate auditors must execute the following SQL sanitization filters for financial month-end close reports:

```sql
-- Sanitized Revenue & Gross Margin Reconciliation Query
SELECT 
    DATE(o.order_date) AS sales_date,
    COUNT(DISTINCT o.order_id) AS net_order_count,
    SUM(o.total_amount) AS audited_gross_revenue,
    SUM(oi.quantity * CASE 
        -- Swap inverted unit_cost and unit_price (ISSUE-17)
        WHEN p.unit_cost > p.unit_price THEN p.unit_price 
        ELSE p.unit_cost 
    END) AS audited_cogs,
    SUM(o.total_amount) - SUM(oi.quantity * CASE 
        WHEN p.unit_cost > p.unit_price THEN p.unit_price 
        ELSE p.unit_cost 
    END) AS audited_gross_profit
FROM fct_orders o
JOIN fct_order_items oi ON o.order_id = oi.order_id
JOIN dim_products p ON oi.product_id = p.product_id
WHERE o.total_amount < 50000.00                   -- Exclude synthetic QA orders (ISSUE-19)
  AND oi.quantity > 0                             -- Exclude misrouted return lines (ISSUE-13)
  AND oi.discount_rate <= 1.0                     -- Filter impossible discounts (ISSUE-14)
GROUP BY DATE(o.order_date);

-- Payment Ledger Reconciliation Discrepancy Finder
SELECT 
    p.payment_id,
    p.order_id,
    p.amount_paid AS recorded_payment,
    o.total_amount AS order_billed_amount,
    (p.amount_paid - o.total_amount) AS ledger_variance
FROM fct_payments p
JOIN fct_orders o ON p.order_id = o.order_id
WHERE p.payment_status = 'Success'
  AND ABS(p.amount_paid - o.total_amount) > 0.01   -- Flag ISSUE-11 variances for manual audit
ORDER BY ABS(p.amount_paid - o.total_amount) DESC;
```

---

## 3. Permanent Accounting Controls & Engineering Actions

1. **JIRA-FIN-301 (Two-Phase Payment Capture Commit)**:
   - Synchronize shopping cart discount application with payment gateway authorization to prevent amount mismatches between hold and capture.
2. **JIRA-FIN-310 (Dedicated Returns Sub-Ledger)**:
   - Route negative inventory adjustments and customer return credits to dedicated `fct_returns` table; apply database `CHECK (quantity > 0)` on sales items.
3. **JIRA-FIN-325 (Promotional Discount Cap Policy)**:
   - Hardcode maximum promotional stacking limit (50% max discount) in checkout microservice to eliminate impossible discount rates.
4. **JIRA-FIN-340 (Wire Clearing Reference Validation)**:
   - Restrict ERP manual payment posting permissions; require banking reference code before marking offline payment as 'Success'.
