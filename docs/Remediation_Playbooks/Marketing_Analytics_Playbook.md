# Downstream Remediation Playbook: Marketing & Growth Analytics Team

**Target Stakeholders**: Marketing Data Analysts, Growth Analytics Engineers, CRM Ops, Lifecycle Marketing Managers  
**Governed Data Domains**: Customer Profiles (`dim_customers`), Acquisition & Orders (`fct_orders`), Support & CSAT (`fct_customer_interactions`)

---

## 1. Executive Summary & Impact Analysis

Marketing and Growth analytics relies on accurate identity resolution, contact reachability, customer lifetime value (LTV), attribution modeling, and customer satisfaction (CSAT) scoring.

The framework identified **8 data quality issues** impacting the Marketing domain:

| Issue ID | Entity & Column | Dimension | Severity | Business Risk |
| :--- | :--- | :--- | :---: | :--- |
| **ISSUE-01** | `dim_customers.email` | Completeness | HIGH | Email marketing deliverability drops; 125 customers unreachable. |
| **ISSUE-02** | `fct_orders.customer_id` | Completeness | CRITICAL | $48,200 in sales unlinked to customers, distorting CAC and LTV models. |
| **ISSUE-05** | `dim_customers.phone` | Completeness | LOW | High-value VIP tier accounts lack SMS contact channel. |
| **ISSUE-12** | `dim_customers.email` | Consistency | MEDIUM | Split customer purchase histories; duplicated audience reach counts. |
| **ISSUE-15** | `fct_customer_interactions.interaction_date` | Accuracy | MEDIUM | Client clock drift records future tickets in campaign attribution windows. |
| **ISSUE-16** | `dim_customers.postal_code` | Accuracy | LOW | Geo-targeted campaigns fail for malformed US zip codes. |
| **ISSUE-18** | `fct_customer_interactions.rating_score` | Accuracy | MEDIUM | 10-point NPS survey loaded into 5-star CSAT artificially inflates satisfaction. |
| **ISSUE-21** | `fct_customer_interactions.resolution_time_mins` | Distribution | MEDIUM | Hanging open tickets (30+ days) inflate average resolution SLA metrics. |

---

## 2. Immediate Analytics Filters (Interim Reporting)

While upstream engineering patches are deployed, marketing analysts should apply the following SQL filters to ensure production reporting accuracy:

```sql
-- Safe Marketing Attribution & Cohort Query
SELECT 
    c.customer_id,
    COALESCE(c.email, 'guest_' || LOWER(c.customer_id) || '@unregistered.internal') AS sanitized_email,
    c.customer_segment,
    COUNT(o.order_id) AS total_orders,
    SUM(o.total_amount) AS customer_spend
FROM dim_customers c
INNER JOIN fct_orders o ON c.customer_id = o.customer_id
WHERE o.customer_id IS NOT NULL                  -- Filter ISSUE-02
  AND o.total_amount < 50000.00                  -- Filter ISSUE-19 (QA outliers)
GROUP BY c.customer_id, sanitized_email, c.customer_segment;

-- Normalized CSAT Metric Query
SELECT 
    DATE(interaction_date) AS interaction_day,
    channel,
    AVG(CASE 
        WHEN rating_score > 5 THEN CEIL(rating_score / 2.0) -- Normalize ISSUE-18 (10-pt scale)
        ELSE rating_score 
    END) AS normalized_csat_score,
    MEDIAN(CASE 
        WHEN resolution_time_mins > 2880 THEN 65.0           -- Cap ISSUE-21 (hanging tickets)
        ELSE resolution_time_mins 
    END) AS median_resolution_minutes
FROM fct_customer_interactions
WHERE interaction_date <= CURRENT_TIMESTAMP                  -- Exclude ISSUE-15 (future dates)
GROUP BY DATE(interaction_date), channel;
```

---

## 3. Permanent Remediation Actions & Upstream Tickets

1. **JIRA-MKT-104 (Guest Checkout Backfill)**:
   - Configure customer service to backfill guest checkout emails from payment authorization payloads.
2. **JIRA-MKT-112 (Entity Resolution Pipeline)**:
   - Schedule weekly deduplication job running `LOWER(TRIM(email))` matching and merging secondary profiles into the earliest created customer UUID.
3. **JIRA-MKT-125 (Survey Schema Separation)**:
   - Split CSAT (5-star scale) and NPS (10-point scale) into distinct database columns in `fct_customer_interactions`.
4. **JIRA-MKT-130 (Auto-Close Timeout)**:
   - Configure CRM helpdesk to trigger automatic resolution on tickets inactive for 72 hours in 'Pending Customer' status.
