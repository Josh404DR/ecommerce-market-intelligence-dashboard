-- Customer / region / acquisition-channel segment performance.
-- GMV by region, AOV by acquisition channel, completed orders by region,
-- and a combined region x channel view for spotting under-tested segments.

WITH completed_orders AS (
    SELECT
        o.order_id,
        c.region,
        c.acquisition_channel,
        SUM(oi.quantity * oi.unit_price) AS order_value
    FROM orders AS o
    JOIN order_items AS oi ON oi.order_id = o.order_id
    JOIN customers AS c ON c.customer_id = o.customer_id
    WHERE o.order_status = 'completed'
    GROUP BY o.order_id, c.region, c.acquisition_channel
)

-- 1. GMV and completed orders by region
SELECT
    region,
    COUNT(DISTINCT order_id) AS completed_orders,
    ROUND(SUM(order_value), 2) AS gmv,
    ROUND(SUM(order_value) / NULLIF(COUNT(DISTINCT order_id), 0), 2) AS aov
FROM completed_orders
GROUP BY region
ORDER BY gmv DESC;

-- 2. AOV by acquisition channel
SELECT
    acquisition_channel,
    COUNT(DISTINCT order_id) AS completed_orders,
    ROUND(SUM(order_value), 2) AS gmv,
    ROUND(SUM(order_value) / NULLIF(COUNT(DISTINCT order_id), 0), 2) AS aov
FROM completed_orders
GROUP BY acquisition_channel
ORDER BY aov DESC;

-- 3. Combined region x channel segment view, flagging segments that are
--    high-value (AOV above the overall average) but low-volume (order count
--    at or below the median segment) -- good candidates for a marketing test.
WITH segment AS (
    SELECT
        region,
        acquisition_channel,
        COUNT(DISTINCT order_id) AS completed_orders,
        ROUND(SUM(order_value), 2) AS gmv,
        ROUND(SUM(order_value) / NULLIF(COUNT(DISTINCT order_id), 0), 2) AS aov
    FROM completed_orders
    GROUP BY region, acquisition_channel
),
benchmark AS (
    SELECT
        SUM(gmv) / NULLIF(SUM(completed_orders), 0) AS overall_aov
    FROM segment
)
SELECT
    s.region,
    s.acquisition_channel,
    s.completed_orders,
    s.gmv,
    s.aov,
    CASE
        WHEN s.aov > b.overall_aov THEN 'above_average_aov'
        ELSE 'at_or_below_average_aov'
    END AS aov_flag
FROM segment AS s, benchmark AS b
ORDER BY s.gmv DESC;
