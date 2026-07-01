# Dashboard Specification

## Audience

Marketplace growth manager, category manager, and marketing analyst.

## Page 1 — Executive Market Overview

- KPI cards: GMV, completed orders, AOV, campaign lift, anomaly count.
- Monthly GMV and order trend with campaign-period annotations.
- Category growth matrix: H1 GMV, H2 GMV, growth rate.
- Top 10 products ranked by GMV with units sold and revenue share.
- Filters: date, category, region, acquisition channel, campaign.

## Page 2 — Campaign Intelligence

- Before-versus-during daily GMV comparison.
- Incremental GMV and estimated incremental ROAS.
- Campaign AOV and completed orders.
- Caveat label: observational comparison, not causal attribution.

## Page 3 — Product Watchlist

- Product-day anomaly table with z-score and date.
- Product GMV trend around each anomaly.
- Analyst review fields: campaign overlap, stock issue, price change, data quality.

## Metric Definitions

| Metric | Definition |
|---|---|
| GMV | Sum of quantity × transaction unit price for completed orders |
| Orders | Distinct completed order IDs |
| AOV | GMV ÷ completed orders |
| Category growth | H2 category GMV ÷ H1 category GMV − 1 |
| Campaign lift | During-campaign daily GMV ÷ prior equal-period daily GMV − 1 |
| Anomaly | Product-day GMV with absolute z-score ≥ 3 |

## Design Principles

- One-screen executive summary before drill-down.
- Explicit synthetic-data label on every page.
- Use color for exceptions and changes, not decoration.
- Keep metric definitions accessible from tooltips.
