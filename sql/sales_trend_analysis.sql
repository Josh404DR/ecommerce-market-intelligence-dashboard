-- Monthly GMV, completed orders, and AOV.
WITH order_value AS (
    SELECT
        o.order_id,
        o.order_date,
        SUM(oi.quantity * oi.unit_price) AS order_value
    FROM orders AS o
    JOIN order_items AS oi ON oi.order_id = o.order_id
    WHERE o.order_status = 'completed'
    GROUP BY o.order_id, o.order_date
)
SELECT
    SUBSTR(order_date, 1, 7) AS order_month,
    ROUND(SUM(order_value), 2) AS gmv,
    COUNT(DISTINCT order_id) AS order_count,
    ROUND(AVG(order_value), 2) AS aov
FROM order_value
GROUP BY SUBSTR(order_date, 1, 7)
ORDER BY order_month;
