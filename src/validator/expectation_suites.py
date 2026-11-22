"""
Expectation Suites Catalog and Builder for Great Expectations.
Defines official Great Expectations suites for all 8 enterprise tables,
incorporating comprehensive validation checks across all 4 quality dimensions.
"""

from typing import Dict, List, Any
from src.config import ISSUES_CATALOG, DOWNSTREAM_TEAMS


def get_all_expectation_suites() -> Dict[str, Dict[str, Any]]:
    """Returns Great Expectations suite definitions for all 8 datasets."""

    suites = {
        # -------------------------------------------------------------
        # SUITE: dim_customers (10 columns)
        # -------------------------------------------------------------
        "dim_customers": {
            "dataset_name": "dim_customers",
            "suite_name": "dim_customers_quality_suite",
            "expectations": [
                {
                    "expectation_type": "expect_column_values_to_not_be_null",
                    "kwargs": {"column": "customer_id"},
                    "meta": {"dimension": "completeness", "severity": "CRITICAL", "description": "Customer ID must not be null"}
                },
                {
                    "expectation_type": "expect_column_values_to_be_unique",
                    "kwargs": {"column": "customer_id"},
                    "meta": {"dimension": "consistency", "severity": "CRITICAL", "description": "Customer ID must be primary key unique"}
                },
                {
                    "expectation_type": "expect_column_values_to_not_be_null",
                    "kwargs": {"column": "email"},
                    "meta": {
                        "dimension": "completeness",
                        "severity": "HIGH",
                        "issue_id": "ISSUE-01",
                        "impacted_team": DOWNSTREAM_TEAMS["MARKETING"],
                        "description": "Customer contact email must be populated"
                    }
                },
                {
                    "expectation_type": "expect_column_values_to_be_unique",
                    "kwargs": {"column": "email"},
                    "meta": {
                        "dimension": "consistency",
                        "severity": "MEDIUM",
                        "issue_id": "ISSUE-12",
                        "impacted_team": DOWNSTREAM_TEAMS["MARKETING"],
                        "description": "Customer email addresses must be globally unique across profiles"
                    }
                },
                {
                    "expectation_type": "expect_conditional_column_values_to_not_be_null",
                    "kwargs": {
                        "column": "phone",
                        "condition_column": "customer_segment",
                        "condition_values": ["VIP", "Corporate"]
                    },
                    "meta": {
                        "dimension": "completeness",
                        "severity": "LOW",
                        "issue_id": "ISSUE-05",
                        "impacted_team": DOWNSTREAM_TEAMS["MARKETING"],
                        "description": "VIP and Corporate customers must have telephone numbers"
                    }
                },
                {
                    "expectation_type": "expect_column_values_to_match_regex",
                    "kwargs": {
                        "column": "postal_code",
                        "regex": r"^\d{5}(-\d{4})?$",
                        "condition_column": "country_code",
                        "condition_value": "US"
                    },
                    "meta": {
                        "dimension": "accuracy",
                        "severity": "LOW",
                        "issue_id": "ISSUE-16",
                        "impacted_team": DOWNSTREAM_TEAMS["MARKETING"],
                        "description": "US postal codes must conform to standard 5-digit or 9-digit ZIP regex"
                    }
                },
                {
                    "expectation_type": "expect_column_values_to_be_in_set",
                    "kwargs": {"column": "customer_segment", "value_set": ["Consumer", "Corporate", "Small Business", "VIP"]},
                    "meta": {"dimension": "accuracy", "severity": "MEDIUM", "description": "Segment must belong to allowed business categories"}
                },
                {
                    "expectation_type": "expect_column_values_to_be_in_set",
                    "kwargs": {"column": "status", "value_set": ["Active", "Inactive", "Suspended"]},
                    "meta": {"dimension": "accuracy", "severity": "MEDIUM", "description": "Customer status must be within allowed enum values"}
                }
            ]
        },

        # -------------------------------------------------------------
        # SUITE: dim_products (10 columns)
        # -------------------------------------------------------------
        "dim_products": {
            "dataset_name": "dim_products",
            "suite_name": "dim_products_quality_suite",
            "expectations": [
                {
                    "expectation_type": "expect_column_values_to_not_be_null",
                    "kwargs": {"column": "product_id"},
                    "meta": {"dimension": "completeness", "severity": "CRITICAL", "description": "Product ID must not be null"}
                },
                {
                    "expectation_type": "expect_column_values_to_be_unique",
                    "kwargs": {"column": "product_id"},
                    "meta": {"dimension": "consistency", "severity": "CRITICAL", "description": "Product ID must be unique primary key"}
                },
                {
                    "expectation_type": "expect_column_values_to_not_be_null",
                    "kwargs": {"column": "product_name"},
                    "meta": {"dimension": "completeness", "severity": "HIGH", "description": "Product name cannot be null"}
                },
                {
                    "expectation_type": "expect_column_pair_values_a_to_be_greater_than_b",
                    "kwargs": {"column_a": "unit_price", "column_b": "unit_cost", "or_equal": True},
                    "meta": {
                        "dimension": "accuracy",
                        "severity": "HIGH",
                        "issue_id": "ISSUE-17",
                        "impacted_team": DOWNSTREAM_TEAMS["FINANCE"],
                        "description": "Product unit_price must exceed unit_cost (positive gross margin)"
                    }
                },
                {
                    "expectation_type": "expect_column_values_to_be_between",
                    "kwargs": {"column": "unit_price", "min_value": 0.01, "max_value": 5000.0},
                    "meta": {"dimension": "accuracy", "severity": "MEDIUM", "description": "Unit price must be positive and within reasonable catalog limits"}
                },
                {
                    "expectation_type": "expect_column_quantile_values_to_be_between",
                    "kwargs": {"column": "weight_kg", "min_value": 0.01, "max_value": 50.0},
                    "meta": {
                        "dimension": "distribution",
                        "severity": "HIGH",
                        "issue_id": "ISSUE-22",
                        "impacted_team": DOWNSTREAM_TEAMS["SUPPLY_CHAIN"],
                        "description": "Product weight must not contain extreme anomalies (> 50kg for retail)"
                    }
                },
                {
                    "expectation_type": "expect_column_values_to_be_in_set",
                    "kwargs": {"column": "category", "value_set": ["Electronics", "Home & Kitchen", "Apparel", "Books", "Sports"]},
                    "meta": {"dimension": "accuracy", "severity": "MEDIUM", "description": "Category must conform to official merchandising taxonomy"}
                }
            ]
        },

        # -------------------------------------------------------------
        # SUITE: fct_orders (11 columns)
        # -------------------------------------------------------------
        "fct_orders": {
            "dataset_name": "fct_orders",
            "suite_name": "fct_orders_quality_suite",
            "expectations": [
                {
                    "expectation_type": "expect_column_values_to_not_be_null",
                    "kwargs": {"column": "order_id"},
                    "meta": {"dimension": "completeness", "severity": "CRITICAL", "description": "Order ID must not be null"}
                },
                {
                    "expectation_type": "expect_column_values_to_be_unique",
                    "kwargs": {"column": "order_id"},
                    "meta": {"dimension": "consistency", "severity": "CRITICAL", "description": "Order ID must be unique primary key"}
                },
                {
                    "expectation_type": "expect_column_values_to_not_be_null",
                    "kwargs": {"column": "customer_id"},
                    "meta": {
                        "dimension": "completeness",
                        "severity": "CRITICAL",
                        "issue_id": "ISSUE-02",
                        "impacted_team": DOWNSTREAM_TEAMS["MARKETING"],
                        "description": "Orders must be associated with a valid customer_id"
                    }
                },
                {
                    "expectation_type": "expect_foreign_key_to_exist",
                    "kwargs": {"column": "customer_id", "reference_dataset": "dim_customers", "reference_column": "customer_id"},
                    "meta": {"dimension": "consistency", "severity": "CRITICAL", "description": "Order customer_id must exist in dim_customers master"}
                },
                {
                    "expectation_type": "expect_column_values_to_be_in_set",
                    "kwargs": {"column": "currency", "value_set": ["USD"]},
                    "meta": {
                        "dimension": "consistency",
                        "severity": "MEDIUM",
                        "issue_id": "ISSUE-09",
                        "impacted_team": DOWNSTREAM_TEAMS["FINANCE"],
                        "description": "Order currency must be standardized to ISO-4217 uppercase 'USD'"
                    }
                },
                {
                    "expectation_type": "expect_column_values_to_be_between",
                    "kwargs": {"column": "total_amount", "min_value": 0.01, "max_value": 25000.0},
                    "meta": {
                        "dimension": "distribution",
                        "severity": "CRITICAL",
                        "issue_id": "ISSUE-19",
                        "impacted_team": DOWNSTREAM_TEAMS["FINANCE"],
                        "description": "Order total must be free of extreme synthetic QA test amounts ($9,999,999)"
                    }
                },
                {
                    "expectation_type": "expect_column_distribution_anomaly_check",
                    "kwargs": {"column": "discount_amount", "anomaly_value": 0.01, "max_allowed_ratio": 0.02},
                    "meta": {
                        "dimension": "distribution",
                        "severity": "MEDIUM",
                        "issue_id": "ISSUE-23",
                        "impacted_team": DOWNSTREAM_TEAMS["FINANCE"],
                        "description": "Discount amount must not exhibit rounding clusters of $0.01"
                    }
                },
                {
                    "expectation_type": "expect_cross_table_status_concordance",
                    "kwargs": {
                        "order_status_column": "order_status",
                        "shipment_dataset": "fct_shipments",
                        "disallowed_order_status": "Cancelled",
                        "conflicting_shipping_status": "Delivered"
                    },
                    "meta": {
                        "dimension": "consistency",
                        "severity": "HIGH",
                        "issue_id": "ISSUE-08",
                        "impacted_team": DOWNSTREAM_TEAMS["SUPPLY_CHAIN"],
                        "description": "Cancelled orders must not have conflicting Delivered status in shipments"
                    }
                },
                {
                    "expectation_type": "expect_column_values_to_be_in_set",
                    "kwargs": {"column": "order_status", "value_set": ["Delivered", "Shipped", "Processing", "Pending", "Cancelled", "Refunded"]},
                    "meta": {"dimension": "accuracy", "severity": "HIGH", "description": "Order status must be within the supported lifecycle states"}
                }
            ]
        },

        # -------------------------------------------------------------
        # SUITE: fct_order_items (8 columns)
        # -------------------------------------------------------------
        "fct_order_items": {
            "dataset_name": "fct_order_items",
            "suite_name": "fct_order_items_quality_suite",
            "expectations": [
                {
                    "expectation_type": "expect_column_values_to_not_be_null",
                    "kwargs": {"column": "item_id"},
                    "meta": {"dimension": "completeness", "severity": "CRITICAL", "description": "Line Item ID cannot be null"}
                },
                {
                    "expectation_type": "expect_column_values_to_be_unique",
                    "kwargs": {"column": "item_id"},
                    "meta": {"dimension": "consistency", "severity": "CRITICAL", "description": "Item ID must be unique primary key"}
                },
                {
                    "expectation_type": "expect_foreign_key_to_exist",
                    "kwargs": {"column": "product_id", "reference_dataset": "dim_products", "reference_column": "product_id"},
                    "meta": {
                        "dimension": "consistency",
                        "severity": "CRITICAL",
                        "issue_id": "ISSUE-07",
                        "impacted_team": DOWNSTREAM_TEAMS["FINANCE"],
                        "description": "Order items product_id must exist in active product catalog master"
                    }
                },
                {
                    "expectation_type": "expect_column_values_to_be_between",
                    "kwargs": {"column": "quantity", "min_value": 1, "max_value": 100},
                    "meta": {
                        "dimension": "accuracy",
                        "severity": "CRITICAL",
                        "issue_id": "ISSUE-13",
                        "impacted_team": DOWNSTREAM_TEAMS["FINANCE"],
                        "description": "Item quantity must be strictly positive (no negative returns in sales ledger)"
                    }
                },
                {
                    "expectation_type": "expect_column_values_to_be_between",
                    "kwargs": {"column": "discount_rate", "min_value": 0.0, "max_value": 1.0},
                    "meta": {
                        "dimension": "accuracy",
                        "severity": "HIGH",
                        "issue_id": "ISSUE-14",
                        "impacted_team": DOWNSTREAM_TEAMS["FINANCE"],
                        "description": "Discount rate must be bounded between 0% and 100% (0.0 to 1.0)"
                    }
                },
                {
                    "expectation_type": "expect_column_values_to_be_in_set",
                    "kwargs": {"column": "fulfillment_status", "value_set": ["Fulfilled", "Backordered", "Cancelled"]},
                    "meta": {"dimension": "accuracy", "severity": "MEDIUM", "description": "Fulfillment status must match allowed lifecycle codes"}
                }
            ]
        },

        # -------------------------------------------------------------
        # SUITE: fct_payments (9 columns)
        # -------------------------------------------------------------
        "fct_payments": {
            "dataset_name": "fct_payments",
            "suite_name": "fct_payments_quality_suite",
            "expectations": [
                {
                    "expectation_type": "expect_column_values_to_not_be_null",
                    "kwargs": {"column": "payment_id"},
                    "meta": {"dimension": "completeness", "severity": "CRITICAL", "description": "Payment ID must not be null"}
                },
                {
                    "expectation_type": "expect_column_values_to_be_unique",
                    "kwargs": {"column": "payment_id"},
                    "meta": {"dimension": "consistency", "severity": "CRITICAL", "description": "Payment ID must be unique primary key"}
                },
                {
                    "expectation_type": "expect_conditional_column_values_to_not_be_null",
                    "kwargs": {
                        "column": "gateway_transaction_id",
                        "condition_column": "payment_status",
                        "condition_values": ["Success"]
                    },
                    "meta": {
                        "dimension": "completeness",
                        "severity": "CRITICAL",
                        "issue_id": "ISSUE-06",
                        "impacted_team": DOWNSTREAM_TEAMS["FINANCE"],
                        "description": "Settled payments with status 'Success' must have gateway transaction ID"
                    }
                },
                {
                    "expectation_type": "expect_payment_amount_to_match_order_total",
                    "kwargs": {"payment_amount_col": "amount_paid", "order_dataset": "fct_orders", "order_total_col": "total_amount"},
                    "meta": {
                        "dimension": "consistency",
                        "severity": "CRITICAL",
                        "issue_id": "ISSUE-11",
                        "impacted_team": DOWNSTREAM_TEAMS["FINANCE"],
                        "description": "Settled payment amount must reconcile identically with order total"
                    }
                },
                {
                    "expectation_type": "expect_column_values_to_be_in_set",
                    "kwargs": {"column": "payment_status", "value_set": ["Success", "Pending", "Failed", "Refunded"]},
                    "meta": {"dimension": "accuracy", "severity": "HIGH", "description": "Payment status must match allowed gateway statuses"}
                }
            ]
        },

        # -------------------------------------------------------------
        # SUITE: fct_shipments (10 columns)
        # -------------------------------------------------------------
        "fct_shipments": {
            "dataset_name": "fct_shipments",
            "suite_name": "fct_shipments_quality_suite",
            "expectations": [
                {
                    "expectation_type": "expect_column_values_to_not_be_null",
                    "kwargs": {"column": "shipment_id"},
                    "meta": {"dimension": "completeness", "severity": "CRITICAL", "description": "Shipment ID must not be null"}
                },
                {
                    "expectation_type": "expect_column_values_to_be_unique",
                    "kwargs": {"column": "shipment_id"},
                    "meta": {"dimension": "consistency", "severity": "CRITICAL", "description": "Shipment ID must be unique primary key"}
                },
                {
                    "expectation_type": "expect_conditional_column_values_to_not_be_null",
                    "kwargs": {
                        "column": "delivered_date",
                        "condition_column": "shipping_status",
                        "condition_values": ["Delivered"]
                    },
                    "meta": {
                        "dimension": "completeness",
                        "severity": "HIGH",
                        "issue_id": "ISSUE-03",
                        "impacted_team": DOWNSTREAM_TEAMS["SUPPLY_CHAIN"],
                        "description": "Shipments marked 'Delivered' must record delivered_date timestamp"
                    }
                },
                {
                    "expectation_type": "expect_cross_table_temporal_order",
                    "kwargs": {
                        "shipment_date_col": "shipped_date",
                        "order_dataset": "fct_orders",
                        "order_date_col": "order_date"
                    },
                    "meta": {
                        "dimension": "consistency",
                        "severity": "HIGH",
                        "issue_id": "ISSUE-10",
                        "impacted_team": DOWNSTREAM_TEAMS["SUPPLY_CHAIN"],
                        "description": "Temporal causality: shipped_date must occur chronologically after order_date"
                    }
                },
                {
                    "expectation_type": "expect_column_values_to_be_in_set",
                    "kwargs": {"column": "shipping_status", "value_set": ["Delivered", "In Transit", "Failed Delivery", "Returned"]},
                    "meta": {"dimension": "accuracy", "severity": "HIGH", "description": "Shipping status must belong to standard carrier milestones"}
                },
                {
                    "expectation_type": "expect_column_values_to_be_in_set",
                    "kwargs": {"column": "carrier", "value_set": ["FedEx", "UPS", "DHL", "USPS"]},
                    "meta": {"dimension": "accuracy", "severity": "MEDIUM", "description": "Carrier must be an approved logistics provider"}
                }
            ]
        },

        # -------------------------------------------------------------
        # SUITE: fct_inventory (7 columns)
        # -------------------------------------------------------------
        "fct_inventory": {
            "dataset_name": "fct_inventory",
            "suite_name": "fct_inventory_quality_suite",
            "expectations": [
                {
                    "expectation_type": "expect_column_values_to_not_be_null",
                    "kwargs": {"column": "inventory_id"},
                    "meta": {"dimension": "completeness", "severity": "CRITICAL", "description": "Inventory ID must not be null"}
                },
                {
                    "expectation_type": "expect_column_values_to_be_unique",
                    "kwargs": {"column": "inventory_id"},
                    "meta": {"dimension": "consistency", "severity": "CRITICAL", "description": "Inventory ID must be unique primary key"}
                },
                {
                    "expectation_type": "expect_column_values_to_not_be_null",
                    "kwargs": {"column": "reorder_point"},
                    "meta": {
                        "dimension": "completeness",
                        "severity": "MEDIUM",
                        "issue_id": "ISSUE-04",
                        "impacted_team": DOWNSTREAM_TEAMS["SUPPLY_CHAIN"],
                        "description": "Inventory stock records must define an active reorder_point threshold"
                    }
                },
                {
                    "expectation_type": "expect_column_unique_value_count_to_be_greater_than",
                    "kwargs": {"column": "warehouse_id", "min_unique": 2},
                    "meta": {
                        "dimension": "distribution",
                        "severity": "LOW",
                        "issue_id": "ISSUE-20",
                        "impacted_team": DOWNSTREAM_TEAMS["SUPPLY_CHAIN"],
                        "description": "Warehouse location must not be a zero-variance degenerate constant ('WH-DEFAULT')"
                    }
                },
                {
                    "expectation_type": "expect_column_values_to_be_between",
                    "kwargs": {"column": "stock_on_hand", "min_value": 0, "max_value": 100000},
                    "meta": {"dimension": "accuracy", "severity": "HIGH", "description": "Stock on hand cannot be negative"}
                }
            ]
        },

        # -------------------------------------------------------------
        # SUITE: fct_customer_interactions (8 columns)
        # -------------------------------------------------------------
        "fct_customer_interactions": {
            "dataset_name": "fct_customer_interactions",
            "suite_name": "fct_customer_interactions_quality_suite",
            "expectations": [
                {
                    "expectation_type": "expect_column_values_to_not_be_null",
                    "kwargs": {"column": "interaction_id"},
                    "meta": {"dimension": "completeness", "severity": "CRITICAL", "description": "Interaction ID must not be null"}
                },
                {
                    "expectation_type": "expect_column_values_to_be_unique",
                    "kwargs": {"column": "interaction_id"},
                    "meta": {"dimension": "consistency", "severity": "CRITICAL", "description": "Interaction ID must be unique primary key"}
                },
                {
                    "expectation_type": "expect_column_values_to_be_past_or_current",
                    "kwargs": {"column": "interaction_date"},
                    "meta": {
                        "dimension": "accuracy",
                        "severity": "MEDIUM",
                        "issue_id": "ISSUE-15",
                        "impacted_team": DOWNSTREAM_TEAMS["MARKETING"],
                        "description": "Interaction timestamps must not be set to future dates"
                    }
                },
                {
                    "expectation_type": "expect_column_values_to_be_between",
                    "kwargs": {"column": "rating_score", "min_value": 1, "max_value": 5},
                    "meta": {
                        "dimension": "accuracy",
                        "severity": "MEDIUM",
                        "issue_id": "ISSUE-18",
                        "impacted_team": DOWNSTREAM_TEAMS["MARKETING"],
                        "description": "CSAT rating scores must fall strictly within the 1 to 5 scale"
                    }
                },
                {
                    "expectation_type": "expect_column_values_to_be_between",
                    "kwargs": {"column": "resolution_time_mins", "min_value": 0.0, "max_value": 2880.0},
                    "meta": {
                        "dimension": "distribution",
                        "severity": "MEDIUM",
                        "issue_id": "ISSUE-21",
                        "impacted_team": DOWNSTREAM_TEAMS["MARKETING"],
                        "description": "Ticket resolution time must not have idle extreme outliers (> 48 hours / 2880 mins)"
                    }
                },
                {
                    "expectation_type": "expect_column_values_to_be_in_set",
                    "kwargs": {"column": "channel", "value_set": ["Email", "Chat", "Phone", "Social Media"]},
                    "meta": {"dimension": "accuracy", "severity": "LOW", "description": "Support channel must match accepted CRM communication avenues"}
                }
            ]
        }
    }

    return suites
