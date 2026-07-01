"""Create portfolio KPIs, anomaly flags, charts, and a business report."""

from __future__ import annotations

from pathlib import Path
import json

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data" / "processed"
OUTPUT_DIR = ROOT / "outputs"
CHART_DIR = OUTPUT_DIR / "charts"
DASHBOARD_DIR = ROOT / "dashboard"


def money(value: float) -> str:
    return f"${value:,.0f}"


def write_gmv_svg(monthly: pd.DataFrame, target: Path) -> None:
    """Write a dependency-free SVG line chart for the README preview."""
    width, height = 960, 420
    left, right, top, bottom = 80, 30, 45, 70
    values = monthly["gmv"].astype(float).to_numpy()
    minimum, maximum = float(values.min()), float(values.max())
    span = maximum - minimum or 1.0
    x_step = (width - left - right) / max(len(values) - 1, 1)
    points = []
    labels = []
    for index, (month, value) in enumerate(zip(monthly["order_month"], values)):
        x = left + index * x_step
        y = top + (maximum - value) / span * (height - top - bottom)
        points.append(f"{x:.1f},{y:.1f}")
        labels.append(
            f'<text x="{x:.1f}" y="{height - 35}" text-anchor="middle" '
            f'font-size="12" fill="#52525b">{month[5:]}</text>'
        )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" fill="#ffffff"/>
<text x="{left}" y="26" font-family="Arial" font-size="20" font-weight="bold" fill="#18181b">Monthly GMV Trend (Synthetic Data)</text>
<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" stroke="#d4d4d8"/>
<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" stroke="#d4d4d8"/>
<polyline points="{' '.join(points)}" fill="none" stroke="#5B4BCE" stroke-width="4" stroke-linejoin="round"/>
{''.join(f'<circle cx="{point.split(",")[0]}" cy="{point.split(",")[1]}" r="5" fill="#5B4BCE"/>' for point in points)}
{''.join(labels)}
<text x="18" y="{top}" font-family="Arial" font-size="12" fill="#52525b">${maximum:,.0f}</text>
<text x="18" y="{height-bottom}" font-family="Arial" font-size="12" fill="#52525b">${minimum:,.0f}</text>
<text x="{width/2}" y="{height-8}" text-anchor="middle" font-family="Arial" font-size="11" fill="#71717a">Month (2024)</text>
</svg>"""
    target.write_text(svg, encoding="utf-8")


def campaign_lift(orders: pd.DataFrame, campaigns: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for campaign in campaigns.itertuples(index=False):
        start = pd.Timestamp(campaign.start_date)
        end = pd.Timestamp(campaign.end_date)
        duration = (end - start).days + 1
        before_start = start - pd.Timedelta(days=duration)
        before_end = start - pd.Timedelta(days=1)
        during = orders[(orders["order_date"] >= start) & (orders["order_date"] <= end)]
        before = orders[(orders["order_date"] >= before_start) & (orders["order_date"] <= before_end)]
        before_daily = before["order_value"].sum() / duration
        during_daily = during["order_value"].sum() / duration
        lift = (during_daily / before_daily - 1) if before_daily else np.nan
        incremental_gmv = max(0.0, (during_daily - before_daily) * duration)
        roas = incremental_gmv / campaign.budget if campaign.budget else np.nan
        rows.append(
            {
                "campaign_name": campaign.campaign_name,
                "before_daily_gmv": before_daily,
                "during_daily_gmv": during_daily,
                "gmv_lift_pct": lift,
                "incremental_gmv": incremental_gmv,
                "budget": campaign.budget,
                "incremental_roas": roas,
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CHART_DIR.mkdir(parents=True, exist_ok=True)

    orders = pd.read_csv(PROCESSED_DIR / "valid_orders.csv", parse_dates=["order_date"])
    sales = pd.read_csv(PROCESSED_DIR / "sales_detail.csv", parse_dates=["order_date"])
    campaigns = pd.read_csv(PROCESSED_DIR / "campaigns.csv", parse_dates=["start_date", "end_date"])

    monthly = (
        orders.groupby("order_month")
        .agg(gmv=("order_value", "sum"), order_count=("order_id", "nunique"))
        .reset_index()
    )
    monthly["aov"] = monthly["gmv"] / monthly["order_count"]
    monthly["gmv_growth_pct"] = monthly["gmv"].pct_change()

    products = (
        sales.groupby(["product_id", "product_name"], as_index=False)
        .agg(gmv=("line_revenue", "sum"), units_sold=("quantity", "sum"))
        .sort_values("gmv", ascending=False)
    )
    categories = (
        sales.groupby(["order_month", "category_name"], as_index=False)["line_revenue"]
        .sum()
        .rename(columns={"line_revenue": "gmv"})
    )
    category_pivot = categories.pivot(index="category_name", columns="order_month", values="gmv").fillna(0)
    category_growth = pd.DataFrame(
        {
            "category_name": category_pivot.index,
            "h1_gmv": category_pivot.iloc[:, :6].sum(axis=1).values,
            "h2_gmv": category_pivot.iloc[:, 6:].sum(axis=1).values,
        }
    )
    category_growth["h2_vs_h1_growth_pct"] = (
        category_growth["h2_gmv"] / category_growth["h1_gmv"] - 1
    )
    category_growth = category_growth.sort_values("h2_vs_h1_growth_pct", ascending=False)

    daily_product = (
        sales.groupby(["order_date", "product_id", "product_name"], as_index=False)["line_revenue"]
        .sum()
        .rename(columns={"line_revenue": "daily_gmv"})
    )
    product_stats = daily_product.groupby("product_id")["daily_gmv"].agg(["mean", "std"]).reset_index()
    anomalies = daily_product.merge(product_stats, on="product_id")
    anomalies["z_score"] = (anomalies["daily_gmv"] - anomalies["mean"]) / anomalies["std"].replace(0, np.nan)
    anomalies = anomalies.loc[anomalies["z_score"].abs() >= 3].sort_values("z_score", ascending=False)

    campaign_results = campaign_lift(orders, campaigns)

    total_gmv = float(monthly["gmv"].sum())
    total_orders = int(monthly["order_count"].sum())
    overall_aov = total_gmv / total_orders
    best_month = monthly.loc[monthly["gmv"].idxmax()]
    top_product = products.iloc[0]
    fastest_category = category_growth.iloc[0]
    best_campaign = campaign_results.loc[campaign_results["gmv_lift_pct"].idxmax()]

    kpis = pd.DataFrame(
        [
            ("Total GMV", round(total_gmv, 2), "USD"),
            ("Completed Orders", total_orders, "orders"),
            ("Average Order Value", round(overall_aov, 2), "USD"),
            ("Best Month GMV", round(float(best_month["gmv"]), 2), str(best_month["order_month"])),
            ("Top Product GMV", round(float(top_product["gmv"]), 2), str(top_product["product_name"])),
            (
                "Best Campaign Lift",
                round(float(best_campaign["gmv_lift_pct"]) * 100, 2),
                f"percent ({best_campaign['campaign_name']})",
            ),
            ("Detected Product-Day Anomalies", len(anomalies), "flags"),
        ],
        columns=["kpi", "value", "context"],
    )
    kpis.to_csv(OUTPUT_DIR / "kpi_summary.csv", index=False)
    monthly.to_csv(OUTPUT_DIR / "monthly_performance.csv", index=False)
    products.head(10).to_csv(OUTPUT_DIR / "top_10_products.csv", index=False)
    category_growth.to_csv(OUTPUT_DIR / "category_growth.csv", index=False)
    campaign_results.to_csv(OUTPUT_DIR / "campaign_effectiveness.csv", index=False)
    anomalies.to_csv(OUTPUT_DIR / "product_sales_anomalies.csv", index=False)

    write_gmv_svg(monthly, CHART_DIR / "monthly_gmv_trend.svg")

    dashboard_data = {
        "kpis": {
            "total_gmv": round(total_gmv, 2),
            "completed_orders": total_orders,
            "aov": round(overall_aov, 2),
            "best_month": str(best_month["order_month"]),
            "anomaly_count": int(len(anomalies)),
        },
        "monthly": monthly.fillna(0).round(4).to_dict(orient="records"),
        "top_products": products.head(10).round(2).to_dict(orient="records"),
        "categories": category_growth.round(4).to_dict(orient="records"),
        "campaigns": campaign_results.round(4).to_dict(orient="records"),
        "anomalies": (
            anomalies.head(25)[["order_date", "product_name", "daily_gmv", "z_score"]]
            .assign(order_date=lambda frame: frame["order_date"].dt.strftime("%Y-%m-%d"))
            .round(2)
            .to_dict(orient="records")
        ),
    }
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    (DASHBOARD_DIR / "dashboard_data.js").write_text(
        "window.DASHBOARD_DATA = "
        + json.dumps(dashboard_data, ensure_ascii=False, allow_nan=False)
        + ";\n",
        encoding="utf-8",
    )

    report = f"""# E-commerce Market Intelligence Summary

> Portfolio analysis based entirely on reproducible synthetic data. Results demonstrate the analytical workflow and are not claims about a real company.

## Executive Summary

The mock marketplace generated **{money(total_gmv)} in GMV** from **{total_orders:,} completed orders**, with an overall **AOV of {money(overall_aov)}**. Demand strengthened in the second half of the year, with **{best_month['order_month']}** producing the highest monthly GMV. Campaign periods created measurable demand lift, but incremental ROAS varies enough to justify budget reallocation rather than uniform expansion.

## Insight 1 — GMV and Order Trend

- **Observation:** GMV peaked in **{best_month['order_month']} at {money(float(best_month['gmv']))}**, supported by {int(best_month['order_count']):,} completed orders. AOV was {money(float(best_month['aov']))}.
- **Possible Cause:** Holiday seasonality and the synthetic Holiday Mega Sale overlap, increasing both traffic and conversion volume.
- **Recommended Action:** Prepare inventory and campaign capacity six to eight weeks before the peak period; compare margin-adjusted GMV against baseline before increasing budget.

## Insight 2 — Product Concentration

- **Observation:** **{top_product['product_name']}** ranked first with {money(float(top_product['gmv']))} GMV and {int(top_product['units_sold']):,} units sold.
- **Possible Cause:** The product combines a relatively high selling price with consistent category demand.
- **Recommended Action:** Protect availability for the top 10 products, but monitor concentration risk and attach complementary products to lift basket size.

## Insight 3 — Category Growth

- **Observation:** **{fastest_category['category_name']}** had the strongest H2 versus H1 GMV growth at **{float(fastest_category['h2_vs_h1_growth_pct']):.1%}**.
- **Possible Cause:** Seasonal multipliers and campaign exposure increased second-half demand across the simulated market.
- **Recommended Action:** Expand tests in the fastest-growing category while tracking contribution margin, stock turnover, and repeat purchase—not GMV alone.

## Insight 4 — Campaign Effectiveness

- **Observation:** **{best_campaign['campaign_name']}** delivered the strongest daily GMV lift at **{float(best_campaign['gmv_lift_pct']):.1%}** versus its equal-length pre-campaign period, with estimated incremental ROAS of **{float(best_campaign['incremental_roas']):.2f}x**.
- **Possible Cause:** Discount depth, seasonal timing, and channel reach jointly increased short-term purchasing.
- **Recommended Action:** Reallocate budget toward campaigns with positive incremental ROAS and validate with holdout or geo tests before treating the lift as causal.

## Insight 5 — Sales Anomalies

- **Observation:** The z-score rule flagged **{len(anomalies)} product-day sales anomalies** at |z| ≥ 3.
- **Possible Cause:** Campaign spikes, low-volume product volatility, data issues, or genuine shifts in demand may produce extreme observations.
- **Recommended Action:** Send anomaly alerts to an analyst queue and require checks for campaign overlap, stock status, price changes, and data completeness before acting.

## Decision Notes

- Prioritize peak-season inventory planning around high-GMV products and fast-growing categories.
- Judge campaigns on incremental value and margin, not topline lift alone.
- Use anomaly detection as a triage mechanism, not an autonomous business decision.
- Add margin, inventory, traffic, and conversion data in a production version to improve causal interpretation.

## Method and Limitations

The workflow uses Python/Pandas for cleaning and KPI generation, SQL templates for reusable analysis, and CSV outputs for BI ingestion. Campaign lift uses a simple equal-length before-versus-during comparison; it does not control for seasonality or establish causality. All records are mock data generated with seed {SEED if 'SEED' in globals() else 42}.
"""
    (OUTPUT_DIR / "summary_report.md").write_text(report, encoding="utf-8")
    print(f"Analysis outputs written to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
