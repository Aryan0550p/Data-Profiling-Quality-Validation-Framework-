"""
Central configuration for Data Profiling, Quality & Validation Framework.
Defines paths, quality dimensions, KPI calculation weights, dataset schemas,
and the comprehensive catalog of 23 seeded data quality issues.
"""

from pathlib import Path

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
CLEAN_DATA_DIR = DATA_DIR / "cleaned"
POWERBI_DATA_DIR = DATA_DIR / "powerbi"
REPORTS_DIR = PROJECT_ROOT / "reports"
DATABASE_DIR = PROJECT_ROOT / "database"
GREAT_EXPECTATIONS_DIR = PROJECT_ROOT / "great_expectations"
EXPECTATIONS_DIR = GREAT_EXPECTATIONS_DIR / "expectations"
VALIDATIONS_DIR = GREAT_EXPECTATIONS_DIR / "uncommitted" / "validations"

# Database Configuration
SQLITE_DB_PATH = DATABASE_DIR / "enterprise_data_platform.db"
SQLITE_URL = f"sqlite:///{SQLITE_DB_PATH}"
POSTGRES_DEFAULT_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/ecommerce_dq"

# Core Quality Dimensions
QUALITY_DIMENSIONS = [
    "completeness",
    "consistency",
    "accuracy",
    "distribution"
]

# 6 Core Quality KPIs & Target SLA Thresholds
QUALITY_KPIS = {
    "DQ_INDEX": {
        "name": "Overall Data Quality Index",
        "description": "Weighted aggregate quality health score across all 4 dimensions",
        "target_sla": 95.0,
        "warning_threshold": 90.0,
        "critical_threshold": 80.0,
        "unit": "%"
    },
    "COMPLETENESS_RATE": {
        "name": "Completeness Rate",
        "description": "Percentage of required attributes with non-null valid values",
        "target_sla": 98.0,
        "warning_threshold": 95.0,
        "critical_threshold": 90.0,
        "unit": "%"
    },
    "CONSISTENCY_RATE": {
        "name": "Consistency & Referential Integrity Rate",
        "description": "Percentage of records adhering to relational foreign keys, cross-field rules, and temporal orders",
        "target_sla": 99.0,
        "warning_threshold": 95.0,
        "critical_threshold": 92.0,
        "unit": "%"
    },
    "ACCURACY_RATE": {
        "name": "Accuracy & Validity Rate",
        "description": "Percentage of records within allowed business domains, regex formats, and mathematical constraints",
        "target_sla": 98.5,
        "warning_threshold": 95.0,
        "critical_threshold": 90.0,
        "unit": "%"
    },
    "DISTRIBUTION_HEALTH": {
        "name": "Distribution & Statistical Health Score",
        "description": "Percentage of numeric columns without unhandled extreme outliers (>3 IQR) or degenerate zero-variance",
        "target_sla": 96.0,
        "warning_threshold": 90.0,
        "critical_threshold": 85.0,
        "unit": "%"
    },
    "FRESHNESS_SLA": {
        "name": "Freshness & Timeliness SLA Compliance Rate",
        "description": "Percentage of transactions ingested within the allowed operational freshness window",
        "target_sla": 99.5,
        "warning_threshold": 97.0,
        "critical_threshold": 93.0,
        "unit": "%"
    }
}

# The 8 Datasets & Column Definitions (73 Columns Total)
DATASETS_SCHEMA = {
    "dim_customers": {
        "description": "Master customer profile and demographic dimensions",
        "primary_key": "customer_id",
        "row_count": 2500,
        "columns": [
            "customer_id", "first_name", "last_name", "email", "phone",
            "registration_date", "customer_segment", "country_code", "postal_code", "status"
        ]
    },
    "dim_products": {
        "description": "Product catalog and pricing master data",
        "primary_key": "product_id",
        "row_count": 800,
        "columns": [
            "product_id", "sku", "product_name", "category", "sub_category",
            "unit_cost", "unit_price", "weight_kg", "supplier_id", "is_active"
        ]
    },
    "fct_orders": {
        "description": "Header-level order transactions and financial summary",
        "primary_key": "order_id",
        "row_count": 5000,
        "columns": [
            "order_id", "customer_id", "order_date", "order_status", "payment_method",
            "currency", "subtotal_amount", "discount_amount", "tax_amount", "total_amount", "channel"
        ]
    },
    "fct_order_items": {
        "description": "Line-item level order fulfillment and product details",
        "primary_key": "item_id",
        "row_count": 12500,
        "columns": [
            "item_id", "order_id", "product_id", "quantity", "unit_price",
            "discount_rate", "total_item_price", "fulfillment_status"
        ]
    },
    "fct_payments": {
        "description": "Financial payment transaction logs and gateway reconciliations",
        "primary_key": "payment_id",
        "row_count": 5200,
        "columns": [
            "payment_id", "order_id", "payment_date", "payment_method",
            "payment_status", "amount_paid", "gateway_transaction_id", "fee_amount", "currency"
        ]
    },
    "fct_shipments": {
        "description": "Logistics and shipping tracking lifecycle events",
        "primary_key": "shipment_id",
        "row_count": 4800,
        "columns": [
            "shipment_id", "order_id", "carrier", "tracking_number", "shipped_date",
            "delivered_date", "shipping_status", "shipping_cost", "origin_warehouse_id", "destination_country"
        ]
    },
    "fct_inventory": {
        "description": "Warehouse inventory snapshot levels and restock thresholds",
        "primary_key": "inventory_id",
        "row_count": 1600,
        "columns": [
            "inventory_id", "warehouse_id", "product_id", "stock_on_hand",
            "stock_reserved", "reorder_point", "last_restock_date"
        ]
    },
    "fct_customer_interactions": {
        "description": "Customer support interactions, tickets, and CSAT scores",
        "primary_key": "interaction_id",
        "row_count": 3200,
        "columns": [
            "interaction_id", "customer_id", "interaction_date", "channel",
            "rating_score", "resolution_time_mins", "issue_category", "is_escalated"
        ]
    }
}

# Downstream Analytics Teams
DOWNSTREAM_TEAMS = {
    "MARKETING": "Marketing & Growth Analytics",
    "SUPPLY_CHAIN": "Supply Chain & Operations Analytics",
    "FINANCE": "Financial & Revenue Analytics"
}

# The 23 Seeded Data Quality Issues Catalog
ISSUES_CATALOG = [
    # --- COMPLETENESS ISSUES (1-6) ---
    {
        "issue_id": "ISSUE-01",
        "dataset": "dim_customers",
        "column": "email",
        "dimension": "completeness",
        "severity": "HIGH",
        "rule_name": "expect_column_values_to_not_be_null",
        "description": "Customer emails missing in 125 records (5.0% null rate)",
        "root_cause": "Guest checkout legacy customer migration failed to generate or capture contact emails during database merge.",
        "impacted_team": DOWNSTREAM_TEAMS["MARKETING"],
        "remediation": "Apply deterministic placeholder email format (guest_<cust_id>@unregistered.internal) and enforce email validation at signup UI."
    },
    {
        "issue_id": "ISSUE-02",
        "dataset": "fct_orders",
        "column": "customer_id",
        "dimension": "completeness",
        "severity": "CRITICAL",
        "rule_name": "expect_column_values_to_not_be_null",
        "description": "Orders with null customer_id (200 records / 4.0% null rate)",
        "root_cause": "Asynchronous microservice order ingestion dropped customer session token during express one-click checkout.",
        "impacted_team": DOWNSTREAM_TEAMS["MARKETING"],
        "remediation": "Backfill customer_id from payment gateway payer email lookup; reject order creation events lacking customer UUID in Kafka topic."
    },
    {
        "issue_id": "ISSUE-03",
        "dataset": "fct_shipments",
        "column": "delivered_date",
        "dimension": "completeness",
        "severity": "HIGH",
        "rule_name": "expect_column_values_to_not_be_null_conditional",
        "description": "Shipments marked 'Delivered' have null delivered_date (210 records / 6.2% of delivered shipments)",
        "root_cause": "Carrier webhook payloads for USPS delivered status did not parse ISO-8601 timestamp string due to missing key in JSON response.",
        "impacted_team": DOWNSTREAM_TEAMS["SUPPLY_CHAIN"],
        "remediation": "Extract delivery timestamp from carrier tracking raw payload; patch webhook parser to handle carrier-specific status date schemas."
    },
    {
        "issue_id": "ISSUE-04",
        "dataset": "fct_inventory",
        "column": "reorder_point",
        "dimension": "completeness",
        "severity": "MEDIUM",
        "rule_name": "expect_column_values_to_not_be_null",
        "description": "Inventory records with null reorder_point (112 records / 7.0% null rate)",
        "root_cause": "New SKU onboarding workflow permitted inventory creation before supply chain replenishment planners entered lead time parameters.",
        "impacted_team": DOWNSTREAM_TEAMS["SUPPLY_CHAIN"],
        "remediation": "Default reorder point to category median safety stock formula (2 * lead_time_days * avg_daily_sales) upon SKU activation."
    },
    {
        "issue_id": "ISSUE-05",
        "dataset": "dim_customers",
        "column": "phone",
        "dimension": "completeness",
        "severity": "LOW",
        "rule_name": "expect_column_values_to_not_be_null_for_vip",
        "description": "High-value VIP and Corporate customers missing contact phone numbers (160 records / 8.0% null rate in tier)",
        "root_cause": "OAuth social login integration (Google / Apple Sign-In) bypassed phone number collection step without prompting secondary profile completion.",
        "impacted_team": DOWNSTREAM_TEAMS["MARKETING"],
        "remediation": "Trigger automated in-app profile completion prompt for tier upgrade qualification; fall back to billing telephone record."
    },
    {
        "issue_id": "ISSUE-06",
        "dataset": "fct_payments",
        "column": "gateway_transaction_id",
        "dimension": "completeness",
        "severity": "CRITICAL",
        "rule_name": "expect_column_values_to_not_be_null_for_settled",
        "description": "Settled payments with status 'Success' missing gateway_transaction_id (234 records / 4.5% rate)",
        "root_cause": "Offline wire transfer and B2B purchase orders manually recorded in ERP without populating financial transaction clearing reference.",
        "impacted_team": DOWNSTREAM_TEAMS["FINANCE"],
        "remediation": "Require accounting clearing reference number for manual B2B transactions; enforce non-null constraint at payment service layer."
    },

    # --- CONSISTENCY ISSUES (7-12) ---
    {
        "issue_id": "ISSUE-07",
        "dataset": "fct_order_items",
        "column": "product_id",
        "dimension": "consistency",
        "severity": "CRITICAL",
        "rule_name": "expect_foreign_key_to_exist_in_dim_products",
        "description": "Orphan order items referencing discontinued or deleted product_ids (35 orphan records)",
        "root_cause": "Hard deletion executed in product catalog DB during staging cleanup instead of soft delete (is_active = FALSE).",
        "impacted_team": DOWNSTREAM_TEAMS["FINANCE"],
        "remediation": "Implement foreign key constraint with RESTRICT ON DELETE; restore soft-deleted product records with 'Archived' status."
    },
    {
        "issue_id": "ISSUE-08",
        "dataset": "fct_orders",
        "column": "order_status",
        "dimension": "consistency",
        "severity": "HIGH",
        "rule_name": "expect_cross_table_status_concordance",
        "description": "Order status 'Cancelled' in fct_orders while corresponding fct_shipments record is 'Delivered' (42 conflicting orders)",
        "root_cause": "Cancellation request processed after fulfillment cutoff without publishing cancellation event to 3PL logistics dispatch queue.",
        "impacted_team": DOWNSTREAM_TEAMS["SUPPLY_CHAIN"],
        "remediation": "Reconcile order state to 'Return_Pending'; auto-generate prepaid return label and trigger customer returns notification."
    },
    {
        "issue_id": "ISSUE-09",
        "dataset": "fct_orders",
        "column": "currency",
        "dimension": "consistency",
        "severity": "MEDIUM",
        "rule_name": "expect_column_values_to_be_in_set",
        "description": "Inconsistent currency codes: mixed representations ('usd', 'USD', 'US_DOLLAR', '$') in 185 records",
        "root_cause": "Multiple frontend checkouts (iOS app, Android, Web, Partner API) posted unstandardized currency strings without enum validation.",
        "impacted_team": DOWNSTREAM_TEAMS["FINANCE"],
        "remediation": "Standardize ingestion to ISO-4217 3-letter currency codes via uppercase string transformation and strict enum validation."
    },
    {
        "issue_id": "ISSUE-10",
        "dataset": "fct_shipments",
        "column": "shipped_date",
        "dimension": "consistency",
        "severity": "HIGH",
        "rule_name": "expect_column_pair_values_a_to_be_greater_than_b",
        "description": "Temporal causality violation: shipped_date occurs before order_date (38 shipments)",
        "root_cause": "Warehouse dispatch scanner clock was set to UTC while order creation service logged timestamps in US Eastern Standard Time (UTC-5).",
        "impacted_team": DOWNSTREAM_TEAMS["SUPPLY_CHAIN"],
        "remediation": "Normalize all timestamp ingestions to UTC at API gateway; flag and recalculate shipment lead times with timezone offsets."
    },
    {
        "issue_id": "ISSUE-11",
        "dataset": "fct_payments",
        "column": "amount_paid",
        "dimension": "consistency",
        "severity": "CRITICAL",
        "rule_name": "expect_payment_amount_to_match_order_total",
        "description": "Payment amount does not match order total_amount for single settled payments (65 orders with discrepancies)",
        "root_cause": "Order discount calculation updated after authorization hold was captured at payment gateway, leaving ledger variance.",
        "impacted_team": DOWNSTREAM_TEAMS["FINANCE"],
        "remediation": "Execute automated differential ledger refund or invoice adjustment; implement two-phase commit on cart checkout settlement."
    },
    {
        "issue_id": "ISSUE-12",
        "dataset": "dim_customers",
        "column": "email",
        "dimension": "consistency",
        "severity": "MEDIUM",
        "rule_name": "expect_column_values_to_be_unique",
        "description": "Duplicate customer records with identical email addresses but conflicting customer_ids (28 duplicated customer profiles)",
        "root_cause": "CRM synchronization job upsert logic failed on case-insensitive email comparison (e.g. User@Domain.com vs user@domain.com).",
        "impacted_team": DOWNSTREAM_TEAMS["MARKETING"],
        "remediation": "Apply LOWER(TRIM(email)) in ETL merge pipeline; merge duplicate customer histories into primary canonical customer UUID."
    },

    # --- ACCURACY ISSUES (13-18) ---
    {
        "issue_id": "ISSUE-13",
        "dataset": "fct_order_items",
        "column": "quantity",
        "dimension": "accuracy",
        "severity": "CRITICAL",
        "rule_name": "expect_column_values_to_be_between",
        "description": "Negative item quantities (quantity < 1) present in order items table (45 line items)",
        "root_cause": "Customer return credit memo records were accidentally appended to the active sales line items table instead of returns ledger.",
        "impacted_team": DOWNSTREAM_TEAMS["FINANCE"],
        "remediation": "Route negative adjustments to dedicated fct_returns table; enforce CHECK (quantity > 0) constraint in sales transaction schema."
    },
    {
        "issue_id": "ISSUE-14",
        "dataset": "fct_order_items",
        "column": "discount_rate",
        "dimension": "accuracy",
        "severity": "HIGH",
        "rule_name": "expect_column_values_to_be_between",
        "description": "Discount rate exceeding 100% (discount_rate > 1.0, e.g. 1.25 to 2.50) in 25 line items",
        "root_cause": "Promotional coupon code engine erroneously compounded stacked percentage discounts additively without capping at 100%.",
        "impacted_team": DOWNSTREAM_TEAMS["FINANCE"],
        "remediation": "Cap discount rate at 1.0 (or max permissible promotional threshold 0.70); recalculate line total item price."
    },
    {
        "issue_id": "ISSUE-15",
        "dataset": "fct_customer_interactions",
        "column": "interaction_date",
        "dimension": "accuracy",
        "severity": "MEDIUM",
        "rule_name": "expect_column_values_to_be_past_or_current",
        "description": "Future timestamps (interaction_date > current_timestamp) in customer support interactions (32 records)",
        "root_cause": "Support agent browser local system time was improperly set to a future year/month during ticket submission.",
        "impacted_team": DOWNSTREAM_TEAMS["MARKETING"],
        "remediation": "Overwrite client-provided timestamp with server-side database CURRENT_TIMESTAMP upon ticket creation."
    },
    {
        "issue_id": "ISSUE-16",
        "dataset": "dim_customers",
        "column": "postal_code",
        "dimension": "accuracy",
        "severity": "LOW",
        "rule_name": "expect_column_values_to_match_regex",
        "description": "Malformed postal codes (e.g. 'ZIP-90210??', 'ABCDE', '0000000') in US customer records (78 records)",
        "root_cause": "Checkout postal code field lacked client-side regex mask validation on legacy web portal.",
        "impacted_team": DOWNSTREAM_TEAMS["MARKETING"],
        "remediation": "Cleanse string with regex extraction r'^(\\d{5})(-\\d{4})?$'; integrate USPS Address Verification API at checkout."
    },
    {
        "issue_id": "ISSUE-17",
        "dataset": "dim_products",
        "column": "unit_cost",
        "dimension": "accuracy",
        "severity": "HIGH",
        "rule_name": "expect_column_pair_values_a_to_be_greater_than_b",
        "description": "Inverted pricing economics: unit_cost exceeds unit_price (unit_cost > unit_price) in 24 active products",
        "root_cause": "ERP inventory replenishment batch job swapped supplier procurement unit cost and wholesale MSRP price fields on CSV upload.",
        "impacted_team": DOWNSTREAM_TEAMS["FINANCE"],
        "remediation": "Swap inverted cost and price attributes; notify merchant pricing team and halt automated clearance markdown rules."
    },
    {
        "issue_id": "ISSUE-18",
        "dataset": "fct_customer_interactions",
        "column": "rating_score",
        "dimension": "accuracy",
        "severity": "MEDIUM",
        "rule_name": "expect_column_values_to_be_between",
        "description": "CSAT rating scores out of allowed 1-5 scale (scores = 8, 9, 10) in 36 interaction tickets",
        "root_cause": "NPS survey vendor (10-point scale) results were directly loaded into 5-star CSAT database column without score normalization.",
        "impacted_team": DOWNSTREAM_TEAMS["MARKETING"],
        "remediation": "Rescale 10-point NPS scores to 5-star metric: CEIL(nps_score / 2.0); create distinct columns for NPS vs CSAT."
    },

    # --- DISTRIBUTION & OUTLIER ISSUES (19-23) ---
    {
        "issue_id": "ISSUE-19",
        "dataset": "fct_orders",
        "column": "total_amount",
        "dimension": "distribution",
        "severity": "CRITICAL",
        "rule_name": "expect_column_values_to_be_between_statistical_limits",
        "description": "Extreme monetary outlier ($9,999,999.00 simulated QA load test transaction) in sales orders",
        "root_cause": "Staging stress test order payload bypassed environment filter and persisted into production data warehouse.",
        "impacted_team": DOWNSTREAM_TEAMS["FINANCE"],
        "remediation": "Exclude synthetic test account orders with flag is_test = TRUE; tag and isolate transactions exceeding 4 sigma from executive reporting."
    },
    {
        "issue_id": "ISSUE-20",
        "dataset": "fct_inventory",
        "column": "warehouse_id",
        "dimension": "distribution",
        "severity": "LOW",
        "rule_name": "expect_column_unique_value_count_to_be_greater_than",
        "description": "Zero-variance degenerate column: warehouse_id is 100% constant 'WH-DEFAULT' across all 1,600 rows",
        "root_cause": "Inventory synchronization pipeline defaulted warehouse identifier during multi-facility migration without mapping location codes.",
        "impacted_team": DOWNSTREAM_TEAMS["SUPPLY_CHAIN"],
        "remediation": "Reprocess inventory snapshots using location cross-reference table; re-enable multi-facility inventory allocation."
    },
    {
        "issue_id": "ISSUE-21",
        "dataset": "fct_customer_interactions",
        "column": "resolution_time_mins",
        "dimension": "distribution",
        "severity": "MEDIUM",
        "rule_name": "expect_column_values_to_be_between_iqr",
        "description": "Extreme resolution time outliers (> 43,200 mins / 30+ days) skewing average resolution metrics (18 tickets)",
        "root_cause": "Support tickets were left in 'Waiting on Customer' state without auto-close timeout SLA, recording months of idle duration.",
        "impacted_team": DOWNSTREAM_TEAMS["MARKETING"],
        "remediation": "Deduct paused customer-wait time from total duration; implement automated 72-hour ticket auto-close trigger."
    },
    {
        "issue_id": "ISSUE-22",
        "dataset": "dim_products",
        "column": "weight_kg",
        "dimension": "distribution",
        "severity": "HIGH",
        "rule_name": "expect_column_quantile_values_to_be_between",
        "description": "Severe physical weight outlier (e.g. 5,000 kg for smartphone screen protector) in 15 product records",
        "root_cause": "Supplier EDI catalog feed transmitted product dimensions in grams without applying 1/1000 metric conversion factor to kilograms.",
        "impacted_team": DOWNSTREAM_TEAMS["SUPPLY_CHAIN"],
        "remediation": "Apply conditional conversion (weight_kg = weight_kg / 1000) when category is 'Accessories' and weight > 50kg; update freight rate quotes."
    },
    {
        "issue_id": "ISSUE-23",
        "dataset": "fct_orders",
        "column": "discount_amount",
        "dimension": "distribution",
        "severity": "MEDIUM",
        "rule_name": "expect_column_distribution_anomaly_check",
        "description": "Bimodal distribution anomaly: dense cluster of $0.01 micro-discounts skewing discount variance (480 orders)",
        "root_cause": "Penny-rounding error in split-tender checkout logic generated spurious $0.01 promotional line items.",
        "impacted_team": DOWNSTREAM_TEAMS["FINANCE"],
        "remediation": "Absorb rounding fractions into payment processor fee account; eliminate spurious $0.01 promotional records."
    }
]
