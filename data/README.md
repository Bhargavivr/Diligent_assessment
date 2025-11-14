# Synthetic E-Commerce Dataset

Generated via scripts/generate_data.py. All timestamps fall within the last three years.

## Files & Row Counts
- customers.csv: ~750 rows
- products.csv: ~180 rows
- orders.csv: ~1150 rows
- order_items.csv: ~2915 rows
- inventory_events.csv: ~1611 rows

## Validation Highlights
- Referentials: orders -> customers, order_items -> (orders, products).
- Financials: total_amount = subtotal + shipping + tax (rounded).
- Inventory: sale events reflect item quantities sold; periodic restocks added.
- Loyalty: tiers and lifetime value buckets derive from cumulative spend.
