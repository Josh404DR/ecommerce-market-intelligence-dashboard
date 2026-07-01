"""Generate reproducible synthetic e-commerce data.

All names, transactions, prices, and campaign results are fictional.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
SEED = 42


def main() -> None:
    rng = np.random.default_rng(SEED)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    categories = pd.DataFrame(
        [
            (1, "Electronics"),
            (2, "Home & Living"),
            (3, "Beauty"),
            (4, "Sports"),
            (5, "Fashion"),
            (6, "Food & Beverage"),
        ],
        columns=["category_id", "category_name"],
    )

    product_rows = []
    product_id = 1
    category_price = {
        1: (35, 420),
        2: (12, 180),
        3: (8, 95),
        4: (15, 230),
        5: (10, 160),
        6: (4, 60),
    }
    for category_id, category_name in categories.itertuples(index=False):
        low, high = category_price[category_id]
        for index in range(1, 11):
            price = round(float(rng.uniform(low, high)), 2)
            cost = round(price * float(rng.uniform(0.42, 0.70)), 2)
            product_rows.append(
                (
                    product_id,
                    f"{category_name.split()[0]} Product {index:02d}",
                    category_id,
                    price,
                    cost,
                    pd.Timestamp("2024-01-01") + pd.Timedelta(days=int(rng.integers(0, 300))),
                )
            )
            product_id += 1
    products = pd.DataFrame(
        product_rows,
        columns=["product_id", "product_name", "category_id", "list_price", "unit_cost", "launch_date"],
    )

    regions = ["North", "Central", "South", "East"]
    channels = ["Organic", "Paid Search", "Social", "Referral", "Email"]
    customers = pd.DataFrame(
        {
            "customer_id": range(1, 1501),
            "signup_date": pd.to_datetime("2023-01-01")
            + pd.to_timedelta(rng.integers(0, 700, 1500), unit="D"),
            "region": rng.choice(regions, 1500, p=[0.34, 0.28, 0.30, 0.08]),
            "acquisition_channel": rng.choice(channels, 1500, p=[0.28, 0.25, 0.22, 0.10, 0.15]),
        }
    )

    campaigns = pd.DataFrame(
        [
            (1, "Spring Refresh", "2024-03-10", "2024-03-24", "Social", 15000, 0.12),
            (2, "Mid-Year Sale", "2024-06-15", "2024-06-30", "Paid Search", 26000, 0.18),
            (3, "Back to Routine", "2024-09-01", "2024-09-14", "Email", 12000, 0.10),
            (4, "Holiday Mega Sale", "2024-11-20", "2024-12-05", "Multi-channel", 42000, 0.22),
        ],
        columns=[
            "campaign_id",
            "campaign_name",
            "start_date",
            "end_date",
            "channel",
            "budget",
            "discount_rate",
        ],
    )
    campaigns["start_date"] = pd.to_datetime(campaigns["start_date"])
    campaigns["end_date"] = pd.to_datetime(campaigns["end_date"])

    dates = pd.date_range("2024-01-01", "2024-12-31", freq="D")
    seasonal_multiplier = {
        1: 0.82,
        2: 0.86,
        3: 0.95,
        4: 0.98,
        5: 1.02,
        6: 1.10,
        7: 1.05,
        8: 1.00,
        9: 1.04,
        10: 1.10,
        11: 1.38,
        12: 1.52,
    }
    category_weights = np.array([0.21, 0.18, 0.16, 0.14, 0.18, 0.13])
    product_weights = np.repeat(category_weights / 10, 10)

    order_rows: list[tuple] = []
    item_rows: list[tuple] = []
    order_id = 1
    order_item_id = 1

    for date in dates:
        active = campaigns[
            (campaigns["start_date"] <= date) & (campaigns["end_date"] >= date)
        ]
        campaign_id = int(active.iloc[0]["campaign_id"]) if not active.empty else None
        campaign_boost = 1.42 if campaign_id else 1.0
        weekend_boost = 1.12 if date.dayofweek >= 5 else 1.0
        expected_orders = 17 * seasonal_multiplier[date.month] * campaign_boost * weekend_boost
        daily_orders = int(rng.poisson(expected_orders))

        for _ in range(daily_orders):
            customer_id = int(rng.integers(1, 1501))
            status = rng.choice(["completed", "cancelled", "refunded"], p=[0.94, 0.04, 0.02])
            payment_method = rng.choice(["credit_card", "digital_wallet", "bank_transfer"], p=[0.55, 0.32, 0.13])
            order_rows.append(
                (order_id, customer_id, date, status, payment_method, campaign_id)
            )

            item_count = int(rng.choice([1, 2, 3, 4], p=[0.60, 0.25, 0.11, 0.04]))
            chosen_products = rng.choice(products["product_id"], size=item_count, replace=False, p=product_weights)
            campaign_discount = float(active.iloc[0]["discount_rate"]) if campaign_id else 0.0
            for chosen_id in chosen_products:
                product = products.loc[products["product_id"] == chosen_id].iloc[0]
                quantity = int(rng.choice([1, 2, 3], p=[0.78, 0.18, 0.04]))
                noise_discount = float(rng.choice([0, 0.05, 0.08], p=[0.72, 0.20, 0.08]))
                discount_rate = min(0.35, campaign_discount + noise_discount)
                unit_price = round(float(product["list_price"]) * (1 - discount_rate), 2)
                item_rows.append(
                    (
                        order_item_id,
                        order_id,
                        int(chosen_id),
                        quantity,
                        unit_price,
                        round(discount_rate, 2),
                    )
                )
                order_item_id += 1
            order_id += 1

    orders = pd.DataFrame(
        order_rows,
        columns=["order_id", "customer_id", "order_date", "order_status", "payment_method", "campaign_id"],
    )
    order_items = pd.DataFrame(
        item_rows,
        columns=["order_item_id", "order_id", "product_id", "quantity", "unit_price", "discount_rate"],
    )

    for name, frame in {
        "categories": categories,
        "products": products,
        "customers": customers,
        "campaigns": campaigns,
        "orders": orders,
        "order_items": order_items,
    }.items():
        frame.to_csv(RAW_DIR / f"{name}.csv", index=False, date_format="%Y-%m-%d")

    print(f"Generated {len(orders):,} orders and {len(order_items):,} order items in {RAW_DIR}")


if __name__ == "__main__":
    main()
