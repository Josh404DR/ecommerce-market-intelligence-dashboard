-- Campaign-period KPIs. For causal decisions, add a holdout group.
SELECT
    c.campaign_name,
    c.channel,
    c.budget,
    COUNT(DISTINCT o.order_id) AS completed_orders,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS campaign_gmv,
    ROUND(
        SUM(oi.quantity * oi.unit_price) / NULLIF(COUNT(DISTINCT o.order_id), 0),
        2
    ) AS campaign_aov,
    ROUND(SUM(oi.quantity * oi.unit_price) / NULLIF(c.budget, 0), 2) AS gross_roas
FROM campaigns AS c
LEFT JOIN orders AS o
    ON o.campaign_id = c.campaign_id
    AND o.order_status = 'completed'
LEFT JOIN order_items AS oi ON oi.order_id = o.order_id
GROUP BY c.campaign_id, c.campaign_name, c.channel, c.budget
ORDER BY campaign_gmv DESC;
