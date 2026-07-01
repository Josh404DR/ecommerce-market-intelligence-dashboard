# E-commerce Market Intelligence Summary

> Portfolio analysis based entirely on reproducible synthetic data. Results demonstrate the analytical workflow and are not claims about a real company.

## Executive Summary

The mock marketplace generated **$1,503,182 in GMV** from **7,061 completed orders**, with an overall **AOV of $213**. Demand strengthened in the second half of the year, with **2024-12** producing the highest monthly GMV. Campaign periods created measurable demand lift, but incremental ROAS varies enough to justify budget reallocation rather than uniform expansion.

## Insight 1 — GMV and Order Trend

- **Observation:** GMV peaked in **2024-12 at $175,560**, supported by 834 completed orders. AOV was $211.
- **Possible Cause:** Holiday seasonality and the synthetic Holiday Mega Sale overlap, increasing both traffic and conversion volume.
- **Recommended Action:** Prepare inventory and campaign capacity six to eight weeks before the peak period; compare margin-adjusted GMV against baseline before increasing budget.

## Insight 2 — Product Concentration

- **Observation:** **Electronics Product 10** ranked first with $111,060 GMV and 307 units sold.
- **Possible Cause:** The product combines a relatively high selling price with consistent category demand.
- **Recommended Action:** Protect availability for the top 10 products, but monitor concentration risk and attach complementary products to lift basket size.

## Insight 3 — Category Growth

- **Observation:** **Sports** had the strongest H2 versus H1 GMV growth at **27.6%**.
- **Possible Cause:** Seasonal multipliers and campaign exposure increased second-half demand across the simulated market.
- **Recommended Action:** Expand tests in the fastest-growing category while tracking contribution margin, stock turnover, and repeat purchase—not GMV alone.

## Insight 4 — Campaign Effectiveness

- **Observation:** **Spring Refresh** delivered the strongest daily GMV lift at **54.6%** versus its equal-length pre-campaign period, with estimated incremental ROAS of **1.65x**.
- **Possible Cause:** Discount depth, seasonal timing, and channel reach jointly increased short-term purchasing.
- **Recommended Action:** Reallocate budget toward campaigns with positive incremental ROAS and validate with holdout or geo tests before treating the lift as causal.

## Insight 5 — Sales Anomalies

- **Observation:** The z-score rule flagged **141 product-day sales anomalies** at |z| ≥ 3.
- **Possible Cause:** Campaign spikes, low-volume product volatility, data issues, or genuine shifts in demand may produce extreme observations.
- **Recommended Action:** Send anomaly alerts to an analyst queue and require checks for campaign overlap, stock status, price changes, and data completeness before acting.

## Insight 6 — Customer / Region Segment

- **Observation:** **North** led all regions with $526,663 GMV, while **North** recorded the most completed orders (2,414). Across acquisition channels, **Email** customers had the highest AOV at $218.
- **Possible Cause:** Regional demand concentration and channel-specific customer quality (for example, referral or organic customers tend to arrive with higher purchase intent than paid-channel customers) likely drive the AOV gap between segments.
- **Recommended Action:** Prioritize marketing tests on segments that combine above-average AOV with below-median order volume — in this run: **Central / Email, South / Referral**. These segments show spending power but limited reach, making them efficient candidates for incremental budget versus scaling already-saturated segments.

## Decision Notes

- Prioritize peak-season inventory planning around high-GMV products and fast-growing categories.
- Judge campaigns on incremental value and margin, not topline lift alone.
- Use anomaly detection as a triage mechanism, not an autonomous business decision.
- Add margin, inventory, traffic, and conversion data in a production version to improve causal interpretation.

## Method and Limitations

The workflow uses Python/Pandas for cleaning and KPI generation, SQL templates for reusable analysis, and CSV outputs for BI ingestion. Campaign lift uses a simple equal-length before-versus-during comparison; it does not control for seasonality or establish causality. All records are mock data generated with seed 42.
