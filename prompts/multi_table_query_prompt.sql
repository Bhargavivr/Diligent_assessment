You are an analytics engineer preparing a demonstration SQL query against the ecommerce.db SQLite database populated with the synthetic dataset. Write a SQL script that:

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
   - last_order_status

2. Joins the relevant tables (customers, orders, order_items). Include only customers with at least one order.

3. Orders the result by net_revenue descending and limits to the top 50 customers.

4. Adds a secondary summary query that aggregates by order_status showing counts and total net_revenue per status.

5. Includes comments explaining each CTE or major step.

Return a single SQL file named customer_ltv_report.sql containing the queries. No additional commentary.
