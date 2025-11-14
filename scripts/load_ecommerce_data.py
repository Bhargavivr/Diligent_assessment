"""SQLite loader for synthetic e-commerce dataset."""
from __future__ import annotations

import argparse
import csv
import sqlite3
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

LOYALTY_TIERS = ("bronze", "silver", "gold", "platinum")
LIFETIME_BUCKETS = ("low", "medium", "high")
ORDER_STATUSES = ("pending", "shipped", "delivered", "cancelled", "returned")
CHANNELS = ("email", "sms", "social", "paid_search", "affiliate", "organic")
SENTIMENTS = ("positive", "neutral", "negative")
EVENT_TYPES = ("restock", "sale", "return", "adjustment")
ACTORS = ("system", "warehouse_bot", "associate", "vendor")


def parse_bool(value: str) -> int:
    return 1 if str(value).strip().lower() in {"1", "true", "t", "yes"} else 0


def parse_float(value: str) -> float:
    return float(value) if value not in (None, "") else 0.0


def parse_int(value: str) -> int:
    return int(float(value)) if value not in (None, "") else 0


def load_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        return list(reader)


def ensure_foreign_keys(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA foreign_keys = ON;")


def drop_tables(conn: sqlite3.Connection) -> None:
    tables = [
        "customer_kpis",
        "inventory_events",
        "order_items",
        "orders",
        "products",
        "customers",
    ]
    for tbl in tables:
        conn.execute(f"DROP TABLE IF EXISTS {tbl};")


def create_tables(conn: sqlite3.Connection) -> None:
    conn.executescript(
        f"""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            created_at TEXT NOT NULL,
            marketing_opt_in INTEGER NOT NULL,
            loyalty_tier TEXT NOT NULL CHECK (loyalty_tier IN {LOYALTY_TIERS}),
            lifetime_value_bucket TEXT NOT NULL CHECK (lifetime_value_bucket IN {LIFETIME_BUCKETS})
        );

        CREATE TABLE IF NOT EXISTS products (
            product_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            brand TEXT NOT NULL,
            price REAL NOT NULL,
            created_at TEXT NOT NULL,
            inventory_count INTEGER NOT NULL,
            active_flag INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL REFERENCES customers(customer_id),
            order_date TEXT NOT NULL,
            order_status TEXT NOT NULL CHECK (order_status IN {ORDER_STATUSES}),
            shipping_address TEXT NOT NULL,
            shipping_city TEXT NOT NULL,
            shipping_state TEXT NOT NULL,
            shipping_postal_code TEXT NOT NULL,
            shipping_country TEXT NOT NULL,
            subtotal REAL NOT NULL,
            shipping_cost REAL NOT NULL,
            tax_amount REAL NOT NULL,
            total_amount REAL NOT NULL,
            coupon_code TEXT,
            acquisition_channel TEXT NOT NULL CHECK (acquisition_channel IN {CHANNELS}),
            customer_sentiment TEXT NOT NULL CHECK (customer_sentiment IN {SENTIMENTS})
        );

        CREATE TABLE IF NOT EXISTS order_items (
            order_item_id TEXT PRIMARY KEY,
            order_id TEXT NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
            product_id TEXT NOT NULL REFERENCES products(product_id),
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            discount_amount REAL NOT NULL,
            line_total REAL NOT NULL,
            tax_rate REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS inventory_events (
            event_id TEXT PRIMARY KEY,
            product_id TEXT NOT NULL REFERENCES products(product_id),
            event_type TEXT NOT NULL CHECK (event_type IN {EVENT_TYPES}),
            quantity_change INTEGER NOT NULL,
            event_timestamp TEXT NOT NULL,
            note TEXT,
            actor TEXT NOT NULL CHECK (actor IN {ACTORS})
        );

        CREATE TABLE IF NOT EXISTS customer_kpis (
            customer_id TEXT PRIMARY KEY REFERENCES customers(customer_id),
            total_orders INTEGER NOT NULL,
            first_order_date TEXT,
            last_order_date TEXT,
            gross_revenue REAL NOT NULL,
            discount_total REAL NOT NULL,
            net_revenue REAL NOT NULL,
            avg_order_value REAL,
            dominant_channel TEXT,
            sentiment_score REAL
        );
        """
    )


def transform_customers(rows: Iterable[Dict[str, str]]) -> List[Tuple]:
    return [
        (
            row["customer_id"],
            row["first_name"],
            row["last_name"],
            row["email"],
            row.get("phone"),
            row["created_at"],
            parse_bool(row.get("marketing_opt_in", "false")),
            row["loyalty_tier"],
            row["lifetime_value_bucket"],
        )
        for row in rows
    ]


def transform_products(rows: Iterable[Dict[str, str]]) -> List[Tuple]:
    return [
        (
            row["product_id"],
            row["name"],
            row["category"],
            row["brand"],
            parse_float(row["price"]),
            row["created_at"],
            parse_int(row["inventory_count"]),
            parse_bool(row.get("active_flag", "true")),
        )
        for row in rows
    ]


def transform_orders(rows: Iterable[Dict[str, str]]) -> List[Tuple]:
    transformed = []
    for row in rows:
        subtotal = parse_float(row["subtotal"])
        shipping = parse_float(row["shipping_cost"])
        tax = parse_float(row["tax_amount"])
        total = parse_float(row["total_amount"])
        if abs((subtotal + shipping + tax) - total) > 1.0:
            raise ValueError(f"Order {row['order_id']} totals do not reconcile")
        transformed.append(
            (
                row["order_id"],
                row["customer_id"],
                row["order_date"],
                row["order_status"],
                row["shipping_address"],
                row["shipping_city"],
                row["shipping_state"],
                row["shipping_postal_code"],
                row["shipping_country"],
                subtotal,
                shipping,
                tax,
                total,
                row.get("coupon_code", ""),
                row["acquisition_channel"],
                row["customer_sentiment"],
            )
        )
    return transformed


def transform_order_items(rows: Iterable[Dict[str, str]]) -> List[Tuple]:
    return [
        (
            row["order_item_id"],
            row["order_id"],
            row["product_id"],
            parse_int(row["quantity"]),
            parse_float(row["unit_price"]),
            parse_float(row["discount_amount"]),
            parse_float(row["line_total"]),
            parse_float(row["tax_rate"]),
        )
        for row in rows
    ]


def transform_inventory(rows: Iterable[Dict[str, str]]) -> List[Tuple]:
    return [
        (
            row["event_id"],
            row["product_id"],
            row["event_type"],
            parse_int(row["quantity_change"]),
            row["event_timestamp"],
            row.get("note"),
            row["actor"],
        )
        for row in rows
    ]


def insert_many(conn: sqlite3.Connection, sql: str, rows: List[Tuple], label: str) -> None:
    if not rows:
        print(f"[WARN] No rows for {label}")
        return
    conn.executemany(sql, rows)
    print(f"[INFO] Loaded {len(rows):>6} rows into {label}")


def populate_customer_kpis(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM customer_kpis;")
    conn.execute(
        """
        INSERT INTO customer_kpis (
            customer_id, total_orders, first_order_date, last_order_date,
            gross_revenue, discount_total, net_revenue, avg_order_value,
            dominant_channel, sentiment_score
        )
        WITH order_fact AS (
            SELECT
                o.customer_id,
                o.order_id,
                o.order_date,
                o.acquisition_channel,
                o.customer_sentiment,
                o.subtotal,
                SUM(oi.discount_amount) AS discount_total
            FROM orders o
            JOIN order_items oi ON oi.order_id = o.order_id
            GROUP BY o.order_id
        ), sentiment AS (
            SELECT
                customer_id,
                AVG(CASE customer_sentiment WHEN 'positive' THEN 1 WHEN 'neutral' THEN 0 ELSE -1 END) AS score
            FROM orders
            GROUP BY customer_id
        ), channel_counts AS (
            SELECT customer_id, acquisition_channel, COUNT(*) AS cnt,
                   ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY COUNT(*) DESC) AS rn
            FROM orders
            GROUP BY customer_id, acquisition_channel
        )
        SELECT
            c.customer_id,
            COUNT(of.order_id) AS total_orders,
            MIN(of.order_date),
            MAX(of.order_date),
            COALESCE(SUM(of.subtotal), 0),
            COALESCE(SUM(of.discount_total), 0),
            COALESCE(SUM(of.subtotal) - SUM(of.discount_total), 0),
            CASE WHEN COUNT(of.order_id) = 0 THEN NULL ELSE AVG(of.subtotal) END,
            (SELECT acquisition_channel FROM channel_counts WHERE customer_id = c.customer_id AND rn = 1),
            (SELECT score FROM sentiment WHERE customer_id = c.customer_id)
        FROM customers c
        LEFT JOIN order_fact of ON of.customer_id = c.customer_id
        GROUP BY c.customer_id;
        """
    )
    print("[INFO] customer_kpis materialized")


def summarize_inventory(conn: sqlite3.Connection) -> None:
    rows = conn.execute(
        """
        SELECT
            p.product_id,
            p.name,
            SUM(CASE WHEN ie.event_type = 'restock' THEN ie.quantity_change ELSE 0 END) AS restocked,
            SUM(CASE WHEN ie.event_type = 'sale' THEN ie.quantity_change ELSE 0 END) AS sold
        FROM products p
        LEFT JOIN inventory_events ie ON ie.product_id = p.product_id
        GROUP BY p.product_id
        LIMIT 5;
        """
    ).fetchall()
    print("[INFO] Sample inventory deltas (top 5):")
    for row in rows:
        print(f"       {row[0][:8]}... restocked={row[2] or 0} sold={row[3] or 0}")


def collect_stats(conn: sqlite3.Connection, tables: Iterable[str]) -> Dict[str, Dict[str, float]]:
    stats: Dict[str, Dict[str, float]] = {}
    for tbl in tables:
        cur = conn.execute(
            f"SELECT COUNT(*) AS cnt, MIN(rowid) AS min_id, MAX(rowid) AS max_id FROM {tbl};"
        )
        cnt, min_id, max_id = cur.fetchone()
        stats[tbl] = {"rows": cnt, "min_rowid": min_id, "max_rowid": max_id}
    return stats


def dry_run_validate(data_dir: Path) -> None:
    expected_files = [
        "customers.csv",
        "products.csv",
        "orders.csv",
        "order_items.csv",
        "inventory_events.csv",
    ]
    for name in expected_files:
        path = data_dir / name
        if not path.exists():
            raise FileNotFoundError(f"Missing required file: {path}")
        rows = load_csv(path)
        print(f"[DRY-RUN] {name}: {len(rows)} rows, columns={list(rows[0].keys())}")
    print("[DRY-RUN] Validation complete")


def load_data(conn: sqlite3.Connection, data_dir: Path) -> None:
    print(f"[INFO] Loading data from {data_dir}")
    customers = transform_customers(load_csv(data_dir / "customers.csv"))
    products = transform_products(load_csv(data_dir / "products.csv"))
    orders = transform_orders(load_csv(data_dir / "orders.csv"))
    order_items = transform_order_items(load_csv(data_dir / "order_items.csv"))
    inventory = transform_inventory(load_csv(data_dir / "inventory_events.csv"))

    with conn:
        insert_many(conn, "INSERT INTO customers VALUES (?,?,?,?,?,?,?,?,?)", customers, "customers")
        insert_many(conn, "INSERT INTO products VALUES (?,?,?,?,?,?,?,?)", products, "products")
        insert_many(conn, "INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", orders, "orders")
        insert_many(conn, "INSERT INTO order_items VALUES (?,?,?,?,?,?,?,?)", order_items, "order_items")
        insert_many(conn, "INSERT INTO inventory_events VALUES (?,?,?,?,?,?,?)", inventory, "inventory_events")
        populate_customer_kpis(conn)
    summarize_inventory(conn)


def main() -> None:
    parser = argparse.ArgumentParser(description="Load synthetic e-commerce data into SQLite")
    parser.add_argument("--data-dir", type=Path, default=Path("../data"), help="Directory with CSV files")
    parser.add_argument("--database", type=Path, default=Path("../ecommerce.db"), help="SQLite DB path")
    parser.add_argument("--drop-tables", action="store_true", help="Drop existing tables before load")
    parser.add_argument("--vacuum", action="store_true", help="Run VACUUM after load")
    parser.add_argument("--dry-run", action="store_true", help="Validate files without loading")
    args = parser.parse_args()

    if args.dry_run:
        dry_run_validate(args.data_dir)
        return

    conn = sqlite3.connect(args.database)
    ensure_foreign_keys(conn)
    if args.drop_tables:
        drop_tables(conn)
    create_tables(conn)
    load_data(conn, args.data_dir)

    stats = collect_stats(conn, [
        "customers", "products", "orders", "order_items", "inventory_events", "customer_kpis"
    ])
    for table, info in stats.items():
        print(f"[STATS] {table:15} rows={info['rows']:>5}")

    if args.vacuum:
        print("[INFO] Running VACUUM")
        conn.execute("VACUUM;")

    conn.close()
    print(f"[DONE] Loaded data into {args.database}")


if __name__ == "__main__":
    main()

README = """
# load_ecommerce_data.py

## Usage
python scripts/load_ecommerce_data.py --data-dir data --database ecommerce.db --drop-tables --vacuum

## Features
- Strict schema with FK + CHECK constraints.
- Derived customer_kpis materialization for reporting.
- Dry-run validation and structured logging to catch issues early.
- Inventory sanity preview for confidence.

## Troubleshooting
- Use --dry-run if CSV validation fails.
- Delete ecommerce.db or pass --drop-tables when schema drifts.
- Ensure Python 3.9+ with sqlite3 enabled.
"""
