You are an analytics engineer preparing a flagship insights deck for the ecommerce.db SQLite database populated with the five-table synthetic dataset (customers, products, orders, order_items, inventory_events). Author a SQL script that:

1. Produces a report of customer lifetime value with these columns:
   - customer_id
   - full_name (first + last)
   - first_order_date
   - last_order_date
   - total_orders (count of distinct orders)
   - total_items (sum of quantities across all order_items)
   - gross_revenue (sum of subtotal)
   - discount_total (sum of discount_amount per order_items)
   - net_revenue (gross_revenue - discount_total)
   - avg_order_value
   - loyalty_tier
   - dominant_category (most frequent product category purchased)
   - last_order_status

2. Joins the relevant tables (customers, orders, order_items, products, inventory_events) and derives:
   - days_since_last_order
   - acquisition_channel_mix (percent of orders per channel)
   - inventory_pressure_score (ratio of sale events to restocks for purchased products)

3. Filters to customers with at least one order and orders by net_revenue descending, limiting to the top 50 customers.

4. Adds supporting sections:
   - Order status summary with counts and total net_revenue per status.
   - Product category contribution summary (category, orders, revenue share, avg discount).
   - Inventory health summary (product_id, category, net inventory delta, days since last restock).

5. Uses well-named CTEs with explanatory comments for each stage (e.g., customer_activity, channel_mix, inventory_health).

6. Ends with a final SELECT that joins the key CTE outputs into a presentation-ready result set, followed by separate SELECT statements for the supplementary summaries.

Return a single SQL file named customer_ltv_report.sql containing the queries. No additional commentary.
