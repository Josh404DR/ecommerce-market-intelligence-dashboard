# E-commerce Market Intelligence Dashboard

An end-to-end data analytics portfolio project that converts synthetic e-commerce transactions into market intelligence, campaign evaluation, product monitoring, and practical business recommendations.

> **Data disclaimer:** Every record is generated mock data. No real company, customer, or platform data is used.

## What This Project Demonstrates

- **E-commerce sales performance analysis** — GMV, completed orders, AOV, top-10 product ranking, and H2-vs-H1 category growth from raw relational data.
- **Campaign effectiveness analysis** — equal-length pre-period comparison and incremental ROAS to judge which campaigns actually created demand lift.
- **Product-level sales anomaly monitoring** — a z-score rule flags unusual product-day GMV so analysts can triage pricing, stock, or data issues.
- **Dashboard-ready datasets, business reports, and a BI dashboard specification** — clean CSV outputs, a stakeholder-facing Markdown report, and a documented dashboard spec/mockup an analyst could hand to a BI developer.

## Live Dashboard

**[Open Interactive BI Dashboard](https://josh404dr.github.io/ecommerce-market-intelligence-dashboard/dashboard/index.html)** (dependency-free portfolio dashboard, supporting GMV, completed orders, and AOV trend switching, category growth, product anomaly tracking, and campaign lift views).

The proposed BI layout, definitions, and interactive specifications are documented in:
- [`dashboard/dashboard_spec.md`](dashboard/dashboard_spec.md)
- [`dashboard/dashboard_mockup.md`](dashboard/dashboard_mockup.md)

![Dashboard preview](assets/dashboard_preview.png)
![Summary report preview](assets/summary_report_preview.png)

> **TODO (manual step):** The two screenshots above are referenced but not yet captured. Open `dashboard/index.html` in a browser, take a screenshot, and save it as `assets/dashboard_preview.png`; do the same for `outputs/summary_report.md` (rendered view) and save as `assets/summary_report_preview.png`. See `assets/README.md` for exact instructions.

## Project Overview

This one-day MVP demonstrates how an analyst can move from raw relational data to decision-ready outputs using Python, Pandas, SQL, CSV, and a BI dashboard specification. The project emphasizes transparent metric definitions and recommendations that business stakeholders can act on.

## Business Problem

An e-commerce team needs a repeatable view of:

- whether GMV and order volume are growing;
- which products and categories drive performance;
- whether campaigns create meaningful incremental value;
- where unusual product sales require investigation;
- which actions should be prioritized by growth, category, and marketing teams.

## Dataset

Six synthetic relational tables are generated with a fixed random seed:

| Table | Grain | Example fields |
|---|---|---|
| `orders` | One row per order | date, customer, status, campaign |
| `order_items` | One row per product in an order | quantity, unit price, discount |
| `products` | One row per product | category, list price, cost |
| `categories` | One row per category | category name |
| `campaigns` | One row per campaign | period, channel, budget, discount |
| `customers` | One row per customer | region, signup date, acquisition channel |

## Analysis Questions

1. How do monthly GMV, completed orders, and AOV change over time?
2. Which 10 products contribute the most GMV?
3. Which categories grew fastest in H2 versus H1?
4. How did daily GMV change before and during each campaign?
5. Which product-day observations are statistically unusual?
6. How does performance differ by customer region and acquisition channel, and which segments deserve a marketing test?
7. What inventory, campaign, and monitoring actions follow from the evidence?

## Methodology

1. Generate reproducible synthetic transactions and dimensions.
2. Validate schemas, dates, duplicates, quantities, and prices.
3. Restrict commercial KPIs to completed orders.
4. Build monthly, product, category, campaign, and customer-segment datasets.
5. Flag product-day GMV anomalies using an absolute z-score threshold of 3.
6. Translate results into observation → possible cause → recommended action.

Campaign lift uses an equal-length pre-period comparison. It is useful for triage but does not prove causality; a production study should add holdouts or a causal design.

## Key Findings

Running the pipeline generates current figures in:

- [`outputs/summary_report.md`](outputs/summary_report.md)
- [`outputs/kpi_summary.csv`](outputs/kpi_summary.csv)
- [`outputs/monthly_performance.csv`](outputs/monthly_performance.csv)
- [`outputs/campaign_effectiveness.csv`](outputs/campaign_effectiveness.csv)
- [`outputs/customer_segment_performance.csv`](outputs/customer_segment_performance.csv)

The generated scenario typically shows a strong holiday-season peak, product revenue concentration, uneven campaign efficiency, a manageable product anomaly watchlist, and a small set of high-AOV, lower-volume region/channel segments worth testing further.

## Business Recommendations

- Protect inventory availability for high-GMV products before seasonal peaks.
- Allocate campaign budget using incremental value and margin—not gross ROAS alone.
- Test growth investment in fast-growing categories while monitoring stock turnover.
- Route anomaly flags to analysts for campaign, pricing, stock, and data-quality checks.
- Prioritize marketing tests on region/channel segments with above-average AOV but below-median order volume.
- Add traffic, conversion, inventory, and contribution-margin data before production use.

## Tech Stack

- Python
- Pandas and NumPy
- SQL
- CSV
- Dependency-free SVG chart output
- BI dashboard specification

## How to Run

```bash
python -m venv .venv
```

Windows:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src/generate_mock_data.py
python src/clean_data.py
python src/analyze_data.py
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
python src/generate_mock_data.py
python src/clean_data.py
python src/analyze_data.py
```

## Dashboard Preview

![Monthly GMV trend](outputs/charts/monthly_gmv_trend.svg)

Open the local [`dashboard/index.html`](dashboard/index.html) file in a browser to run the interactive dashboard locally.

## Repository Structure

```text
data/raw/          generated source tables
data/processed/    validated analysis-ready tables
sql/               reusable KPI queries
src/               data generation, cleaning, and analysis
outputs/           reports, KPI tables, and chart
dashboard/         dashboard specification and mockup
assets/            README preview images (see assets/README.md)
```

## Resume Highlight

> Built an end-to-end e-commerce market intelligence project using Python, Pandas, and SQL; generated and cleaned six relational mock datasets, analyzed GMV/AOV/product/category/campaign/customer-segment performance, designed anomaly monitoring, and translated findings into a stakeholder-ready dashboard and commercial recommendations.

## Notes for Reviewers

This repository is intentionally scoped as a readable one-day MVP. It favors reproducibility, business interpretation, and clear analytical limitations over unnecessary infrastructure.

## 作品集摘要（中文）

本專案模擬電商市場情報分析流程，使用 Python、Pandas、SQL 與 Dashboard 分析 GMV、訂單數、AOV、商品排名、品類成長、行銷活動成效與銷售異常。作品展示我能將電商交易資料轉換為 dashboard-ready datasets、商業分析報告與可執行建議，支援商品經營、活動預算分配與異常追蹤。
