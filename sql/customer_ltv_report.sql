-- customer_ltv_report.sql
-- Generates customer lifetime value insights plus supporting summaries

WITH last_order AS (
    SELECT customer_id, order_status, customer_sentiment
    FROM (
        SELECT o.*, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC, order_id DESC) AS rn
        FROM orders o
    ) ranked
    WHERE rn = 1
),
customer_activity AS (
    -- Aggregate customer order behavior
    SELECT
        c.customer_id,
        c.first_name || ' ' || c.last_name AS full_name,
        MIN(o.order_date) AS first_order_date,
        MAX(o.order_date) AS last_order_date,
        COUNT(DISTINCT o.order_id) AS total_orders,
        SUM(oi.quantity) AS total_items,
        SUM(o.subtotal) AS gross_revenue,
        SUM(oi.discount_amount) AS discount_total,
        SUM(o.subtotal) - SUM(oi.discount_amount) AS net_revenue,
        AVG(o.subtotal) AS avg_order_value,
        c.loyalty_tier,
        lo.order_status AS last_order_status,
        lo.customer_sentiment AS last_sentiment
    FROM customers c
    JOIN orders o ON o.customer_id = c.customer_id
    JOIN order_items oi ON oi.order_id = o.order_id
    LEFT JOIN last_order lo ON lo.customer_id = c.customer_id
    GROUP BY c.customer_id
),
channel_mix AS (
    -- Calculate percent of orders by acquisition channel
    SELECT
        o.customer_id,
        o.acquisition_channel,
        COUNT(*) AS channel_orders,
        COUNT(*) * 1.0 / SUM(COUNT(*)) OVER (PARTITION BY o.customer_id) AS channel_share
    FROM orders o
    GROUP BY o.customer_id, o.acquisition_channel
),
inventory_health AS (
    -- Gauge inventory pressure for products a customer purchased
    SELECT
        o.customer_id,
        AVG(CASE WHEN ie.event_type = 'sale' THEN -ie.quantity_change END) AS avg_sale_qty,
        AVG(CASE WHEN ie.event_type = 'restock' THEN ie.quantity_change END) AS avg_restock_qty
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN inventory_events ie ON ie.product_id = oi.product_id
    GROUP BY o.customer_id
)
SELECT
    ca.customer_id,
    ca.full_name,
    ca.first_order_date,
    ca.last_order_date,
    ca.total_orders,
    ca.total_items,
    ca.gross_revenue,
    ca.discount_total,
    ca.net_revenue,
    ca.avg_order_value,
    ca.loyalty_tier,
    SUM(CASE WHEN cm.acquisition_channel = 'organic' THEN cm.channel_share ELSE 0 END) AS organic_mix,
    SUM(CASE WHEN cm.acquisition_channel <> 'organic' THEN cm.channel_share ELSE 0 END) AS paid_mix,
    CASE WHEN ih.avg_restock_qty IS NULL OR ih.avg_restock_qty = 0 THEN NULL
         ELSE ih.avg_sale_qty / ih.avg_restock_qty END AS inventory_pressure_score,
    ca.last_order_status,
    ca.last_sentiment
FROM customer_activity ca
LEFT JOIN channel_mix cm ON cm.customer_id = ca.customer_id
LEFT JOIN inventory_health ih ON ih.customer_id = ca.customer_id
GROUP BY ca.customer_id
ORDER BY ca.net_revenue DESC
LIMIT 50;

-- Order status summary
SELECT
    o.order_status,
    COUNT(*) AS orders,
    SUM(o.subtotal) AS gross_revenue,
    SUM(o.subtotal) - SUM(oi.discount_amount) AS net_revenue
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY o.order_status
ORDER BY orders DESC;

-- Product category contribution summary
SELECT
    p.category,
    COUNT(DISTINCT o.order_id) AS orders,
    SUM(oi.line_total) AS revenue,
    AVG(oi.discount_amount) AS avg_discount
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
JOIN orders o ON o.order_id = oi.order_id
GROUP BY p.category
ORDER BY revenue DESC;

-- Inventory health summary
SELECT
    p.product_id,
    p.name,
    p.category,
    SUM(CASE WHEN ie.event_type = 'restock' THEN ie.quantity_change ELSE 0 END) +
    SUM(CASE WHEN ie.event_type = 'sale' THEN ie.quantity_change ELSE 0 END) AS net_delta,
    MAX(CASE WHEN ie.event_type = 'restock' THEN ie.event_timestamp END) AS last_restock
FROM products p
LEFT JOIN inventory_events ie ON ie.product_id = p.product_id
GROUP BY p.product_id
ORDER BY net_delta ASC
LIMIT 25;
