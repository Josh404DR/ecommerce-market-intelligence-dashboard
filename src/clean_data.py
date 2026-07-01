"""Validate and transform raw synthetic data into analysis-ready CSV files."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"


def require_columns(frame: pd.DataFrame, columns: list[str], name: str) -> None:
    missing = sorted(set(columns) - set(frame.columns))
    if missing:
        raise ValueError(f"{name} missing columns: {missing}")


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    tables = {
        name: pd.read_csv(RAW_DIR / f"{name}.csv")
        for name in ["orders", "order_items", "products", "categories", "campaigns", "customers"]
    }

    require_columns(tables["orders"], ["order_id", "customer_id", "order_date", "order_status"], "orders")
    require_columns(tables["order_items"], ["order_id", "product_id", "quantity", "unit_price"], "order_items")

    for column in ["order_date"]:
        tables["orders"][column] = pd.to_datetime(tables["orders"][column], errors="raise")
    for column in ["start_date", "end_date"]:
        tables["campaigns"][column] = pd.to_datetime(tables["campaigns"][column], errors="raise")
    tables["products"]["launch_date"] = pd.to_datetime(tables["products"]["launch_date"], errors="raise")
    tables["customers"]["signup_date"] = pd.to_datetime(tables["customers"]["signup_date"], errors="raise")

    for name, frame in tables.items():
        if frame.duplicated().any():
            tables[name] = frame.drop_duplicates().copy()

    items = tables["order_items"]
    if (items["quantity"] <= 0).any() or (items["unit_price"] < 0).any():
        raise ValueError("order_items contains invalid quantity or price")
    items["line_revenue"] = (items["quantity"] * items["unit_price"]).round(2)

    orders = tables["orders"]
    valid_orders = orders.loc[orders["order_status"] == "completed"].copy()
    order_totals = (
        items.groupby("order_id", as_index=False)["line_revenue"]
        .sum()
        .rename(columns={"line_revenue": "order_value"})
    )
    valid_orders = valid_orders.merge(order_totals, on="order_id", how="inner")
    valid_orders["order_month"] = valid_orders["order_date"].dt.to_period("M").astype(str)

    sales_detail = (
        valid_orders.merge(items, on="order_id", how="inner")
        .merge(tables["products"], on="product_id", how="left")
        .merge(tables["categories"], on="category_id", how="left")
        .merge(tables["customers"], on="customer_id", how="left")
    )

    output_tables = {
        **tables,
        "order_items": items,
        "valid_orders": valid_orders,
        "sales_detail": sales_detail,
    }
    for name, frame in output_tables.items():
        frame.to_csv(PROCESSED_DIR / f"{name}.csv", index=False, date_format="%Y-%m-%d")

    print(f"Cleaned {len(valid_orders):,} completed orders into {PROCESSED_DIR}")


if __name__ == "__main__":
    main()
