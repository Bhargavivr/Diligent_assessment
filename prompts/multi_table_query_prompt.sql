You are an analytics engineer preparing a flagship insights deck for the ecommerce.db SQLite database populated with the expanded synthetic dataset (customers, products, orders, order_items, inventory_events, marketing_campaigns, support_tickets). Author a SQL script that:

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

2. Joins the relevant tables (customers, orders, order_items, products, marketing_campaigns) and derives campaign influence (percentage of orders tied to campaigns) plus days_since_last_order.

3. Filters to customers with at least one order and orders by net_revenue descending, limiting to the top 50 customers.

4. Adds supporting sections:
   - Order status summary with counts and total net_revenue per status.
   - Campaign performance summary (campaign name, attributed orders, attributed revenue, conversion rate based on campaign spend).
   - Support ticket impact summary (tickets per customer, CSAT averages, share of escalated tickets for top customers).

5. Uses well-named CTEs with explanatory comments for each stage (e.g., customer_activity, campaign_influence, ticket_health).

6. Ends with a final SELECT that joins the key CTE outputs into a presentation-ready result set, followed by separate SELECT statements for the supplementary summaries.

Return a single SQL file named customer_ltv_report.sql containing the queries. No additional commentary.
