"""
Synthetic enterprise dataset generator.
Generates 8 realistic relational tables with 73 total columns,
and precisely injects the 23 cataloged data quality issues.
"""

import json
import logging
import random
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
import pandas as pd

from src.config import (
    DATASETS_SCHEMA,
    ISSUES_CATALOG,
    RAW_DATA_DIR,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Deterministic seed for reproducible testing & verification
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


class EnterpriseDataGenerator:
    def __init__(self, raw_dir: Path = RAW_DATA_DIR):
        self.raw_dir = raw_dir
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.datasets = {}
        self.injection_audit = {}

    def generate_all(self):
        """Generate all 8 tables and inject the 23 DQ issues."""
        logger.info("Starting enterprise data generation across 8 datasets...")
        self._generate_dim_customers()
        self._generate_dim_products()
        self._generate_fct_orders()
        self._generate_fct_order_items()
        self._generate_fct_payments()
        self._generate_fct_shipments()
        self._generate_fct_inventory()
        self._generate_fct_customer_interactions()

        logger.info("Injecting the 23 cataloged Data Quality Issues...")
        self._inject_23_data_quality_issues()

        logger.info("Saving generated raw datasets to CSV...")
        for name, df in self.datasets.items():
            out_file = self.raw_dir / f"{name}.csv"
            df.to_csv(out_file, index=False)
            logger.info(f"Saved {name}: {len(df)} rows, {len(df.columns)} columns -> {out_file.name}")

        audit_file = self.raw_dir / "seeded_issues_audit.json"
        with open(audit_file, "w") as f:
            json.dump(self.injection_audit, f, indent=2, default=str)
        logger.info(f"Saved injection audit to {audit_file.name}")

    def _generate_dim_customers(self):
        n = DATASETS_SCHEMA["dim_customers"]["row_count"]
        first_names = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda",
                       "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
                       "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
                       "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
                      "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
                      "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White"]
        segments = ["Consumer", "Corporate", "Small Business", "VIP"]
        countries = ["US", "CA", "GB", "DE"]

        base_date = datetime(2023, 1, 1)
        records = []
        for i in range(1, n + 1):
            fn = random.choice(first_names)
            ln = random.choice(last_names)
            email = f"{fn.lower()}.{ln.lower()}{i}@example.com"
            phone = f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
            reg_date = (base_date + timedelta(days=random.randint(0, 700))).strftime("%Y-%m-%d")
            seg = random.choices(segments, weights=[0.60, 0.20, 0.15, 0.05])[0]
            country = random.choices(countries, weights=[0.75, 0.10, 0.10, 0.05])[0]
            postal = f"{random.randint(10000, 99950)}"
            status = random.choices(["Active", "Inactive", "Suspended"], weights=[0.85, 0.12, 0.03])[0]

            records.append({
                "customer_id": f"CUST-{i:05d}",
                "first_name": fn,
                "last_name": ln,
                "email": email,
                "phone": phone,
                "registration_date": reg_date,
                "customer_segment": seg,
                "country_code": country,
                "postal_code": postal,
                "status": status
            })

        self.datasets["dim_customers"] = pd.DataFrame(records)

    def _generate_dim_products(self):
        n = DATASETS_SCHEMA["dim_products"]["row_count"]
        categories = {
            "Electronics": ["Smartphones", "Laptops", "Audio", "Accessories", "Wearables"],
            "Home & Kitchen": ["Cookware", "Small Appliances", "Bedding", "Furniture", "Lighting"],
            "Apparel": ["Men's Wear", "Women's Wear", "Footwear", "Activewear", "Outerwear"],
            "Books": ["Fiction", "Non-Fiction", "Technical", "Business", "Children"],
            "Sports": ["Fitness Equipment", "Outdoor Gear", "Cycling", "Team Sports", "Water Sports"]
        }

        records = []
        for i in range(1, n + 1):
            cat = random.choice(list(categories.keys()))
            sub = random.choice(categories[cat])
            cost = round(random.uniform(5.0, 450.0), 2)
            margin = random.uniform(1.25, 2.5)
            price = round(cost * margin, 2)
            weight = round(random.uniform(0.1, 15.0), 2)
            supp = f"SUPP-{random.randint(1, 40):03d}"
            active = random.choices([True, False], weights=[0.92, 0.08])[0]

            records.append({
                "product_id": f"PROD-{i:04d}",
                "sku": f"SKU-{cat[:3].upper()}-{sub[:3].upper()}-{i:04d}",
                "product_name": f"{sub} Premium Edition {i}",
                "category": cat,
                "sub_category": sub,
                "unit_cost": cost,
                "unit_price": price,
                "weight_kg": weight,
                "supplier_id": supp,
                "is_active": active
            })

        self.datasets["dim_products"] = pd.DataFrame(records)

    def _generate_fct_orders(self):
        n = DATASETS_SCHEMA["fct_orders"]["row_count"]
        cust_ids = self.datasets["dim_customers"]["customer_id"].tolist()
        statuses = ["Delivered", "Shipped", "Processing", "Pending", "Cancelled", "Refunded"]
        channels = ["Web", "Mobile App", "In-Store", "Marketplace"]
        payment_methods = ["Credit Card", "PayPal", "Wire Transfer", "Gift Card"]

        base_date = datetime(2024, 1, 1, 8, 0, 0)
        records = []
        for i in range(1, n + 1):
            cid = random.choice(cust_ids)
            order_dt = base_date + timedelta(minutes=random.randint(10, 500000))
            status = random.choices(statuses, weights=[0.65, 0.15, 0.08, 0.05, 0.05, 0.02])[0]
            pm = random.choices(payment_methods, weights=[0.55, 0.25, 0.15, 0.05])[0]
            channel = random.choices(channels, weights=[0.50, 0.30, 0.12, 0.08])[0]

            subtotal = round(random.uniform(20.0, 850.0), 2)
            disc_rate = random.choices([0.0, 0.05, 0.10, 0.15, 0.20], weights=[0.4, 0.2, 0.2, 0.1, 0.1])[0]
            discount = round(subtotal * disc_rate, 2)
            tax = round((subtotal - discount) * 0.08, 2)
            total = round(subtotal - discount + tax, 2)

            records.append({
                "order_id": f"ORD-{i:06d}",
                "customer_id": cid,
                "order_date": order_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "order_status": status,
                "payment_method": pm,
                "currency": "USD",
                "subtotal_amount": subtotal,
                "discount_amount": discount,
                "tax_amount": tax,
                "total_amount": total,
                "channel": channel
            })

        self.datasets["fct_orders"] = pd.DataFrame(records)

    def _generate_fct_order_items(self):
        n = DATASETS_SCHEMA["fct_order_items"]["row_count"]
        orders = self.datasets["fct_orders"]["order_id"].tolist()
        products = self.datasets["dim_products"][["product_id", "unit_price"]].to_dict(orient="records")

        records = []
        for i in range(1, n + 1):
            oid = random.choice(orders)
            prod = random.choice(products)
            qty = random.randint(1, 5)
            uprice = prod["unit_price"]
            disc = random.choices([0.0, 0.05, 0.10, 0.15], weights=[0.6, 0.2, 0.1, 0.1])[0]
            total_item = round(qty * uprice * (1.0 - disc), 2)
            fulf = random.choices(["Fulfilled", "Backordered", "Cancelled"], weights=[0.90, 0.07, 0.03])[0]

            records.append({
                "item_id": f"ITEM-{i:07d}",
                "order_id": oid,
                "product_id": prod["product_id"],
                "quantity": qty,
                "unit_price": uprice,
                "discount_rate": disc,
                "total_item_price": total_item,
                "fulfillment_status": fulf
            })

        self.datasets["fct_order_items"] = pd.DataFrame(records)

    def _generate_fct_payments(self):
        n = DATASETS_SCHEMA["fct_payments"]["row_count"]
        orders = self.datasets["fct_orders"][["order_id", "order_date", "total_amount", "payment_method"]].to_dict(orient="records")

        records = []
        for i in range(1, n + 1):
            ord_record = random.choice(orders)
            oid = ord_record["order_id"]
            ord_dt = datetime.strptime(ord_record["order_date"], "%Y-%m-%d %H:%M:%S")
            pay_dt = ord_dt + timedelta(minutes=random.randint(1, 60))
            pm = ord_record["payment_method"]
            status = random.choices(["Success", "Pending", "Failed", "Refunded"], weights=[0.92, 0.04, 0.02, 0.02])[0]
            amt = ord_record["total_amount"]
            fee = round(amt * 0.025 + 0.30, 2)
            gw_id = f"TXN-GW-{random.randint(1000000, 9999999)}"

            records.append({
                "payment_id": f"PAY-{i:06d}",
                "order_id": oid,
                "payment_date": pay_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "payment_method": pm,
                "payment_status": status,
                "amount_paid": amt,
                "gateway_transaction_id": gw_id,
                "fee_amount": fee,
                "currency": "USD"
            })

        self.datasets["fct_payments"] = pd.DataFrame(records)

    def _generate_fct_shipments(self):
        n = DATASETS_SCHEMA["fct_shipments"]["row_count"]
        orders = self.datasets["fct_orders"][["order_id", "order_date", "order_status"]].to_dict(orient="records")
        carriers = ["FedEx", "UPS", "DHL", "USPS"]
        warehouses = ["WH-EAST-01", "WH-WEST-02", "WH-CENTRAL-03", "WH-SOUTH-04"]

        records = []
        for i in range(1, n + 1):
            ord_record = random.choice(orders)
            oid = ord_record["order_id"]
            ord_dt = datetime.strptime(ord_record["order_date"], "%Y-%m-%d %H:%M:%S")
            carrier = random.choice(carriers)
            track_num = f"TRK-{carrier[:3].upper()}-{random.randint(10000000, 99999999)}"

            # Shipped 12 to 72 hours after order
            ship_dt = ord_dt + timedelta(hours=random.randint(12, 72))
            delivered_dt = ship_dt + timedelta(days=random.randint(2, 6))

            status = random.choices(["Delivered", "In Transit", "Failed Delivery", "Returned"],
                                    weights=[0.75, 0.18, 0.04, 0.03])[0]
            cost = round(random.uniform(5.50, 45.00), 2)
            wh = random.choice(warehouses)

            records.append({
                "shipment_id": f"SHIP-{i:06d}",
                "order_id": oid,
                "carrier": carrier,
                "tracking_number": track_num,
                "shipped_date": ship_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "delivered_date": delivered_dt.strftime("%Y-%m-%d %H:%M:%S") if status == "Delivered" else None,
                "shipping_status": status,
                "shipping_cost": cost,
                "origin_warehouse_id": wh,
                "destination_country": "US"
            })

        self.datasets["fct_shipments"] = pd.DataFrame(records)

    def _generate_fct_inventory(self):
        n = DATASETS_SCHEMA["fct_inventory"]["row_count"]
        prod_ids = self.datasets["dim_products"]["product_id"].tolist()
        warehouses = ["WH-EAST-01", "WH-WEST-02", "WH-CENTRAL-03", "WH-SOUTH-04"]
        base_date = datetime(2024, 6, 1)

        records = []
        for i in range(1, n + 1):
            wh = random.choice(warehouses)
            pid = random.choice(prod_ids)
            stock = random.randint(20, 1500)
            reserved = int(stock * random.uniform(0.05, 0.25))
            reorder = random.randint(50, 300)
            restock_dt = (base_date - timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d")

            records.append({
                "inventory_id": f"INV-{i:05d}",
                "warehouse_id": wh,
                "product_id": pid,
                "stock_on_hand": stock,
                "stock_reserved": reserved,
                "reorder_point": reorder,
                "last_restock_date": restock_dt
            })

        self.datasets["fct_inventory"] = pd.DataFrame(records)

    def _generate_fct_customer_interactions(self):
        n = DATASETS_SCHEMA["fct_customer_interactions"]["row_count"]
        cust_ids = self.datasets["dim_customers"]["customer_id"].tolist()
        channels = ["Email", "Chat", "Phone", "Social Media"]
        categories = ["Billing", "Shipping", "Product Inquiry", "Return Request"]
        base_date = datetime(2024, 1, 15, 9, 0, 0)

        records = []
        for i in range(1, n + 1):
            cid = random.choice(cust_ids)
            dt = base_date + timedelta(minutes=random.randint(100, 480000))
            ch = random.choice(channels)
            rating = random.choices([1, 2, 3, 4, 5], weights=[0.08, 0.12, 0.20, 0.35, 0.25])[0]
            res_time = round(float(np.random.exponential(scale=45.0)) + 5.0, 1)
            cat = random.choice(categories)
            esc = random.choices([True, False], weights=[0.12, 0.88])[0]

            records.append({
                "interaction_id": f"INT-{i:06d}",
                "customer_id": cid,
                "interaction_date": dt.strftime("%Y-%m-%d %H:%M:%S"),
                "channel": ch,
                "rating_score": rating,
                "resolution_time_mins": res_time,
                "issue_category": cat,
                "is_escalated": esc
            })

        self.datasets["fct_customer_interactions"] = pd.DataFrame(records)

    def _inject_23_data_quality_issues(self):
        """Inject precisely the 23 cataloged DQ issues into raw tables."""

        # ---------------------------------------------------------
        # ISSUE-01: Null Customer Emails in dim_customers (125 records)
        # ---------------------------------------------------------
        df = self.datasets["dim_customers"]
        idx_01 = np.random.choice(df.index, size=125, replace=False)
        df.loc[idx_01, "email"] = None
        self.injection_audit["ISSUE-01"] = {"count": 125, "dataset": "dim_customers", "col": "email", "indices": idx_01.tolist()[:10]}

        # ---------------------------------------------------------
        # ISSUE-02: Null customer_id in fct_orders (200 records)
        # ---------------------------------------------------------
        df = self.datasets["fct_orders"]
        idx_02 = np.random.choice(df.index, size=200, replace=False)
        df.loc[idx_02, "customer_id"] = None
        self.injection_audit["ISSUE-02"] = {"count": 200, "dataset": "fct_orders", "col": "customer_id", "indices": idx_02.tolist()[:10]}

        # ---------------------------------------------------------
        # ISSUE-03: Null delivered_date in delivered fct_shipments (210 records)
        # ---------------------------------------------------------
        df = self.datasets["fct_shipments"]
        deliv_mask = df["shipping_status"] == "Delivered"
        deliv_idx = df[deliv_mask].index
        idx_03 = np.random.choice(deliv_idx, size=min(210, len(deliv_idx)), replace=False)
        df.loc[idx_03, "delivered_date"] = None
        self.injection_audit["ISSUE-03"] = {"count": len(idx_03), "dataset": "fct_shipments", "col": "delivered_date", "indices": idx_03.tolist()[:10]}

        # ---------------------------------------------------------
        # ISSUE-04: Null reorder_point in fct_inventory (112 records)
        # ---------------------------------------------------------
        df = self.datasets["fct_inventory"]
        idx_04 = np.random.choice(df.index, size=112, replace=False)
        df.loc[idx_04, "reorder_point"] = None
        self.injection_audit["ISSUE-04"] = {"count": 112, "dataset": "fct_inventory", "col": "reorder_point", "indices": idx_04.tolist()[:10]}

        # ---------------------------------------------------------
        # ISSUE-05: Missing phone numbers for VIP/Corporate in dim_customers (160 records)
        # ---------------------------------------------------------
        df = self.datasets["dim_customers"]
        vip_idx = df[df["customer_segment"].isin(["VIP", "Corporate"])].index
        idx_05 = np.random.choice(vip_idx, size=min(160, len(vip_idx)), replace=False)
        df.loc[idx_05, "phone"] = None
        self.injection_audit["ISSUE-05"] = {"count": len(idx_05), "dataset": "dim_customers", "col": "phone", "indices": idx_05.tolist()[:10]}

        # ---------------------------------------------------------
        # ISSUE-06: Null gateway_transaction_id in 'Success' fct_payments (234 records)
        # ---------------------------------------------------------
        df = self.datasets["fct_payments"]
        succ_idx = df[df["payment_status"] == "Success"].index
        idx_06 = np.random.choice(succ_idx, size=min(234, len(succ_idx)), replace=False)
        df.loc[idx_06, "gateway_transaction_id"] = None
        self.injection_audit["ISSUE-06"] = {"count": len(idx_06), "dataset": "fct_payments", "col": "gateway_transaction_id", "indices": idx_06.tolist()[:10]}

        # ---------------------------------------------------------
        # ISSUE-07: Orphan product_ids in fct_order_items (35 orphan records)
        # ---------------------------------------------------------
        df = self.datasets["fct_order_items"]
        idx_07 = np.random.choice(df.index, size=35, replace=False)
        for i, idx in enumerate(idx_07):
            df.loc[idx, "product_id"] = f"PROD-DEL-{9000 + i}"
        self.injection_audit["ISSUE-07"] = {"count": 35, "dataset": "fct_order_items", "col": "product_id", "indices": idx_07.tolist()[:10]}

        # ---------------------------------------------------------
        # ISSUE-08: Status Inconsistency (fct_orders Cancelled vs fct_shipments Delivered) (42 orders)
        # ---------------------------------------------------------
        df_ord = self.datasets["fct_orders"]
        df_ship = self.datasets["fct_shipments"]
        deliv_shipments = df_ship[df_ship["shipping_status"] == "Delivered"]
        shared_orders = df_ord[df_ord["order_id"].isin(deliv_shipments["order_id"])].index
        idx_08 = np.random.choice(shared_orders, size=min(42, len(shared_orders)), replace=False)
        df_ord.loc[idx_08, "order_status"] = "Cancelled"
        self.injection_audit["ISSUE-08"] = {"count": len(idx_08), "dataset": "fct_orders", "col": "order_status", "indices": idx_08.tolist()[:10]}

        # ---------------------------------------------------------
        # ISSUE-09: Mixed currency representation in fct_orders (185 records)
        # ---------------------------------------------------------
        df = self.datasets["fct_orders"]
        idx_09 = np.random.choice(df.index, size=185, replace=False)
        inconsistent_currencies = ["usd", "US_DOLLAR", "$", "Usd"]
        for i, idx in enumerate(idx_09):
            df.loc[idx, "currency"] = inconsistent_currencies[i % len(inconsistent_currencies)]
        self.injection_audit["ISSUE-09"] = {"count": 185, "dataset": "fct_orders", "col": "currency", "indices": idx_09.tolist()[:10]}

        # ---------------------------------------------------------
        # ISSUE-10: Temporal causality: shipped_date before order_date in fct_shipments (38 records)
        # ---------------------------------------------------------
        df_ship = self.datasets["fct_shipments"]
        df_ord = self.datasets["fct_orders"].set_index("order_id")
        idx_10 = np.random.choice(df_ship.index, size=38, replace=False)
        for idx in idx_10:
            oid = df_ship.loc[idx, "order_id"]
            if oid in df_ord.index:
                ord_dt = datetime.strptime(str(df_ord.loc[oid, "order_date"]), "%Y-%m-%d %H:%M:%S")
                # Make shipped_date 24 to 48 hours BEFORE order_date
                retro_ship_dt = ord_dt - timedelta(hours=random.randint(24, 48))
                df_ship.loc[idx, "shipped_date"] = retro_ship_dt.strftime("%Y-%m-%d %H:%M:%S")
        self.injection_audit["ISSUE-10"] = {"count": 38, "dataset": "fct_shipments", "col": "shipped_date", "indices": idx_10.tolist()[:10]}

        # ---------------------------------------------------------
        # ISSUE-11: Payment amount mismatch with fct_orders (65 records)
        # ---------------------------------------------------------
        df_pay = self.datasets["fct_payments"]
        succ_pay = df_pay[df_pay["payment_status"] == "Success"].index
        idx_11 = np.random.choice(succ_pay, size=min(65, len(succ_pay)), replace=False)
        for idx in idx_11:
            current_amt = df_pay.loc[idx, "amount_paid"]
            discrepancy = round(random.choice([-45.0, -15.50, 20.0, 50.0]), 2)
            df_pay.loc[idx, "amount_paid"] = max(1.0, round(current_amt + discrepancy, 2))
        self.injection_audit["ISSUE-11"] = {"count": len(idx_11), "dataset": "fct_payments", "col": "amount_paid", "indices": idx_11.tolist()[:10]}

        # ---------------------------------------------------------
        # ISSUE-12: Duplicate Customer profiles with identical email in dim_customers (28 duplicates)
        # ---------------------------------------------------------
        df_cust = self.datasets["dim_customers"]
        idx_source = np.random.choice(df_cust[df_cust["email"].notnull()].index, size=28, replace=False)
        idx_target = np.random.choice([i for i in df_cust.index if i not in idx_source], size=28, replace=False)
        for s, t in zip(idx_source, idx_target):
            # Duplicate the email to target row while customer_id remains different
            df_cust.loc[t, "email"] = df_cust.loc[s, "email"]
        self.injection_audit["ISSUE-12"] = {"count": 28, "dataset": "dim_customers", "col": "email", "indices": idx_target.tolist()[:10]}

        # ---------------------------------------------------------
        # ISSUE-13: Negative item quantities in fct_order_items (45 records)
        # ---------------------------------------------------------
        df = self.datasets["fct_order_items"]
        idx_13 = np.random.choice(df.index, size=45, replace=False)
        for idx in idx_13:
            df.loc[idx, "quantity"] = random.randint(-5, -1)
        self.injection_audit["ISSUE-13"] = {"count": 45, "dataset": "fct_order_items", "col": "quantity", "indices": idx_13.tolist()[:10]}

        # ---------------------------------------------------------
        # ISSUE-14: Discount rate > 1.0 (100%) in fct_order_items (25 records)
        # ---------------------------------------------------------
        df = self.datasets["fct_order_items"]
        idx_14 = np.random.choice(df.index, size=25, replace=False)
        for idx in idx_14:
            df.loc[idx, "discount_rate"] = round(random.uniform(1.20, 2.50), 2)
        self.injection_audit["ISSUE-14"] = {"count": 25, "dataset": "fct_order_items", "col": "discount_rate", "indices": idx_14.tolist()[:10]}

        # ---------------------------------------------------------
        # ISSUE-15: Future timestamps in fct_customer_interactions (32 records)
        # ---------------------------------------------------------
        df = self.datasets["fct_customer_interactions"]
        idx_15 = np.random.choice(df.index, size=32, replace=False)
        future_base = datetime.now() + timedelta(days=90)
        for idx in idx_15:
            fut_dt = future_base + timedelta(days=random.randint(1, 365), hours=random.randint(1, 12))
            df.loc[idx, "interaction_date"] = fut_dt.strftime("%Y-%m-%d %H:%M:%S")
        self.injection_audit["ISSUE-15"] = {"count": 32, "dataset": "fct_customer_interactions", "col": "interaction_date", "indices": idx_15.tolist()[:10]}

        # ---------------------------------------------------------
        # ISSUE-16: Malformed US postal codes in dim_customers (78 records)
        # ---------------------------------------------------------
        df = self.datasets["dim_customers"]
        us_idx = df[df["country_code"] == "US"].index
        idx_16 = np.random.choice(us_idx, size=min(78, len(us_idx)), replace=False)
        bad_postals = ["ZIP-90210??", "ABCDE", "0000000", "INVALID", "99#$%", "123"]
        for i, idx in enumerate(idx_16):
            df.loc[idx, "postal_code"] = bad_postals[i % len(bad_postals)]
        self.injection_audit["ISSUE-16"] = {"count": len(idx_16), "dataset": "dim_customers", "col": "postal_code", "indices": idx_16.tolist()[:10]}

        # ---------------------------------------------------------
        # ISSUE-17: Cost exceeds Price in dim_products (24 products)
        # ---------------------------------------------------------
        df = self.datasets["dim_products"]
        idx_17 = np.random.choice(df.index, size=24, replace=False)
        for idx in idx_17:
            p = df.loc[idx, "unit_price"]
            df.loc[idx, "unit_cost"] = round(p * random.uniform(1.30, 2.00), 2)
        self.injection_audit["ISSUE-17"] = {"count": 24, "dataset": "dim_products", "col": "unit_cost", "indices": idx_17.tolist()[:10]}

        # ---------------------------------------------------------
        # ISSUE-18: Out-of-bounds rating scores (8-10) in fct_customer_interactions (36 records)
        # ---------------------------------------------------------
        df = self.datasets["fct_customer_interactions"]
        idx_18 = np.random.choice(df.index, size=36, replace=False)
        for idx in idx_18:
            df.loc[idx, "rating_score"] = random.choice([8, 9, 10])
        self.injection_audit["ISSUE-18"] = {"count": 36, "dataset": "fct_customer_interactions", "col": "rating_score", "indices": idx_18.tolist()[:10]}

        # ---------------------------------------------------------
        # ISSUE-19: Extreme monetary outlier in fct_orders (3 records)
        # ---------------------------------------------------------
        df = self.datasets["fct_orders"]
        idx_19 = np.random.choice(df.index, size=3, replace=False)
        for idx in idx_19:
            df.loc[idx, "total_amount"] = 9999999.00
            df.loc[idx, "subtotal_amount"] = 9999000.00
        self.injection_audit["ISSUE-19"] = {"count": 3, "dataset": "fct_orders", "col": "total_amount", "indices": idx_19.tolist()}

        # ---------------------------------------------------------
        # ISSUE-20: Zero-variance degenerate column in fct_inventory (100% constant)
        # ---------------------------------------------------------
        df = self.datasets["fct_inventory"]
        # Overwrite all warehouse_ids to constant 'WH-DEFAULT'
        df["warehouse_id"] = "WH-DEFAULT"
        self.injection_audit["ISSUE-20"] = {"count": len(df), "dataset": "fct_inventory", "col": "warehouse_id", "indices": "ALL_ROWS"}

        # ---------------------------------------------------------
        # ISSUE-21: Extreme resolution time outliers in fct_customer_interactions (18 records)
        # ---------------------------------------------------------
        df = self.datasets["fct_customer_interactions"]
        idx_21 = np.random.choice(df.index, size=18, replace=False)
        for idx in idx_21:
            # 30-45 days in minutes (43,200 to 64,800 mins)
            df.loc[idx, "resolution_time_mins"] = float(random.randint(43200, 64800))
        self.injection_audit["ISSUE-21"] = {"count": 18, "dataset": "fct_customer_interactions", "col": "resolution_time_mins", "indices": idx_21.tolist()[:10]}

        # ---------------------------------------------------------
        # ISSUE-22: Extreme physical weight outlier in dim_products (15 records)
        # ---------------------------------------------------------
        df = self.datasets["dim_products"]
        idx_22 = np.random.choice(df.index, size=15, replace=False)
        for idx in idx_22:
            df.loc[idx, "weight_kg"] = round(random.uniform(4500.0, 5200.0), 1)
        self.injection_audit["ISSUE-22"] = {"count": 15, "dataset": "dim_products", "col": "weight_kg", "indices": idx_22.tolist()[:10]}

        # ---------------------------------------------------------
        # ISSUE-23: Bimodal / dense penny-rounding discount cluster ($0.01) in fct_orders (480 records)
        # ---------------------------------------------------------
        df = self.datasets["fct_orders"]
        # Select 480 non-zero discount records and force discount_amount to $0.01
        idx_23 = np.random.choice(df.index, size=480, replace=False)
        df.loc[idx_23, "discount_amount"] = 0.01
        self.injection_audit["ISSUE-23"] = {"count": 480, "dataset": "fct_orders", "col": "discount_amount", "indices": idx_23.tolist()[:10]}

        logger.info(f"Successfully injected all 23 data quality issues across the 8 datasets.")


if __name__ == "__main__":
    generator = EnterpriseDataGenerator()
    generator.generate_all()
