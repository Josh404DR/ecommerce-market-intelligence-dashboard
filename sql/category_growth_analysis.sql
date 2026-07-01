-- H2 vs H1 category growth.
WITH category_sales AS (
    SELECT
        c.category_name,
        CASE
            WHEN CAST(SUBSTR(o.order_date, 6, 2) AS INTEGER) <= 6 THEN 'H1'
            ELSE 'H2'
        END AS half_year,
        SUM(oi.quantity * oi.unit_price) AS gmv
    FROM orders AS o
    JOIN order_items AS oi ON oi.order_id = o.order_id
    JOIN products AS p ON p.product_id = oi.product_id
    JOIN categories AS c ON c.category_id = p.category_id
    WHERE o.order_status = 'completed'
    GROUP BY c.category_name, half_year
),
pivoted AS (
    SELECT
        category_name,
        SUM(CASE WHEN half_year = 'H1' THEN gmv ELSE 0 END) AS h1_gmv,
        SUM(CASE WHEN half_year = 'H2' THEN gmv ELSE 0 END) AS h2_gmv
    FROM category_sales
    GROUP BY category_name
)
SELECT
    category_name,
    ROUND(h1_gmv, 2) AS h1_gmv,
    ROUND(h2_gmv, 2) AS h2_gmv,
    ROUND(100.0 * (h2_gmv / NULLIF(h1_gmv, 0) - 1), 2) AS growth_pct
FROM pivoted
ORDER BY growth_pct DESC;
