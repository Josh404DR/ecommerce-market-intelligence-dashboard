-- Top products and revenue contribution.
WITH product_sales AS (
    SELECT
        p.product_id,
        p.product_name,
        SUM(oi.quantity) AS units_sold,
        SUM(oi.quantity * oi.unit_price) AS gmv
    FROM order_items AS oi
    JOIN orders AS o ON o.order_id = oi.order_id
    JOIN products AS p ON p.product_id = oi.product_id
    WHERE o.order_status = 'completed'
    GROUP BY p.product_id, p.product_name
)
SELECT
    product_id,
    product_name,
    units_sold,
    ROUND(gmv, 2) AS gmv,
    ROUND(100.0 * gmv / SUM(gmv) OVER (), 2) AS gmv_share_pct
FROM product_sales
ORDER BY gmv DESC
LIMIT 10;
