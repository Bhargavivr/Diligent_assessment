import csv
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

random.seed(42)
NOW = datetime.utcnow()
THREE_YEARS = 365 * 3

NUM_CUSTOMERS = 750
NUM_PRODUCTS = 180
NUM_ORDERS = 1150
MAX_ITEMS_PER_ORDER = 4

STATES = [
    ("CA", "California"), ("NY", "New York"), ("TX", "Texas"),
    ("WA", "Washington"), ("FL", "Florida"), ("IL", "Illinois"),
    ("GA", "Georgia"), ("PA", "Pennsylvania"), ("CO", "Colorado"), ("NC", "North Carolina"),
]
CITIES = {
    "CA": ["Los Angeles", "San Francisco", "San Diego"],
    "NY": ["New York", "Buffalo", "Rochester"],
    "TX": ["Austin", "Houston", "Dallas"],
    "WA": ["Seattle", "Spokane", "Tacoma"],
    "FL": ["Miami", "Orlando", "Tampa"],
    "IL": ["Chicago", "Springfield", "Naperville"],
    "GA": ["Atlanta", "Savannah", "Augusta"],
    "PA": ["Philadelphia", "Pittsburgh", "Harrisburg"],
    "CO": ["Denver", "Boulder", "Colorado Springs"],
    "NC": ["Charlotte", "Raleigh", "Durham"],
}
COUNTRIES = ["US", "CA", "GB", "AU"]
CHANNELS = ["email", "sms", "social", "paid_search", "affiliate", "organic"]
SENTIMENTS = ["positive", "neutral", "negative"]
LOYALTY_TIERS = ["bronze", "silver", "gold", "platinum"]
LIFETIME_BUCKETS = ["low", "medium", "high"]
EVENT_TYPES = ["restock", "sale", "return", "adjustment"]
ACTORS = ["system", "warehouse_bot", "associate", "vendor"]
CATEGORIES = ["electronics", "apparel", "home", "beauty", "sports"]
BRANDS = {
    "electronics": ["Luminex", "Voltify", "Auraline"],
    "apparel": ["Northwind", "Ardor", "Fleetwear"],
    "home": ["Hearthstone", "Everwood", "Nestico"],
    "beauty": ["Bloomelle", "Variant", "Seren"],
    "sports": ["Pinnacle", "Strive", "Aerolite"],
}

FIRST_NAMES = [
    "Ava", "Liam", "Noah", "Sophia", "Mason", "Isabella", "Logan", "Mia",
    "Ethan", "Olivia", "Lucas", "Harper", "Elijah", "Amelia", "James", "Emma",
]
LAST_NAMES = [
    "Nguyen", "Patel", "Garcia", "Robinson", "Lee", "Kim", "Brown", "Davis",
    "Wilson", "Martinez", "Clark", "Lewis", "Young", "Hall", "Allen", "Torres",
]

def random_date(start_days: int = THREE_YEARS) -> datetime:
    return NOW - timedelta(days=random.randint(0, start_days), hours=random.randint(0, 23), minutes=random.randint(0, 59))


def random_phone() -> str:
    return f"({random.randint(200, 989)})-{random.randint(200, 989):03}-{random.randint(1000, 9999):04}"


def choose_state_city():
    state, _ = random.choice(STATES)
    city = random.choice(CITIES[state])
    return state, city


def make_email(first: str, last: str) -> str:
    domains = ["onelane.com", "novaio.net", "mailarrow.io", "quibly.co"]
    return f"{first.lower()}.{last.lower()}{random.randint(10, 999)}@{random.choice(domains)}"


customers = []
customer_spend = {}
customer_order_counts = {}
customer_negative_events = {}
for _ in range(NUM_CUSTOMERS):
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    created_at = random_date()
    customer_id = str(uuid.uuid4())
    tier = random.choices(LOYALTY_TIERS, weights=[0.55, 0.25, 0.15, 0.05])[0]
    customers.append({
        "customer_id": customer_id,
        "first_name": first,
        "last_name": last,
        "email": make_email(first, last),
        "phone": random_phone(),
        "created_at": created_at.isoformat(),
        "marketing_opt_in": random.choice(["true", "false"]),
        "loyalty_tier": tier,
        "lifetime_value_bucket": "medium",
    })
    customer_spend[customer_id] = 0.0
    customer_order_counts[customer_id] = 0
    customer_negative_events[customer_id] = 0


products = []
product_prices = {}
product_created = {}
product_inventory = {}
for _ in range(NUM_PRODUCTS):
    category = random.choice(CATEGORIES)
    product_id = str(uuid.uuid4())
    price = round(random.uniform(10, 600), 2)
    created_at = random_date()
    inventory_count = random.randint(50, 500)
    products.append({
        "product_id": product_id,
        "name": f"{random.choice(['Nova', 'Echo', 'Pulse', 'Axis', 'Terra'])} {random.choice(['One', 'Pro', 'Max', 'Mini', 'Air'])}",
        "category": category,
        "brand": random.choice(BRANDS[category]),
        "price": f"{price:.2f}",
        "created_at": created_at.isoformat(),
        "inventory_count": inventory_count,
        "active_flag": random.choice(["true", "true", "false"]),
    })
    product_prices[product_id] = price
    product_created[product_id] = created_at
    product_inventory[product_id] = inventory_count


def random_address():
    state, city = choose_state_city()
    return {
        "shipping_address": f"{random.randint(100, 9999)} {random.choice(['Oak', 'Maple', 'Cedar', 'Pine', 'Elm'])} {random.choice(['Ave', 'St', 'Rd', 'Blvd'])}",
        "shipping_city": city,
        "shipping_state": state,
        "shipping_postal_code": f"{random.randint(10000, 99999)}",
        "shipping_country": random.choice(COUNTRIES),
    }

orders = []
order_items = []
inventory_events = []
product_sales = {pid: 0 for pid in product_prices}

for _ in range(NUM_ORDERS):
    customer = random.choice(customers)
    order_date = random_date()
    address = random_address()
    status = random.choices(
        ["pending", "shipped", "delivered", "cancelled", "returned"],
        weights=[0.1, 0.25, 0.45, 0.15, 0.05],
    )[0]
    acquisition_channel = random.choices(CHANNELS, weights=[0.2, 0.1, 0.25, 0.25, 0.1, 0.1])[0]
    coupon_code = random.choice(["WELCOME10", "FREESHIP", "LOYAL20", None, None])

    order_id = str(uuid.uuid4())
    line_items = []
    subtotal = 0.0
    for _ in range(random.randint(1, MAX_ITEMS_PER_ORDER)):
        product = random.choice(products)
        product_id = product["product_id"]
        quantity = random.randint(1, 4)
        unit_price = product_prices[product_id]
        discount = round(random.choice([0, 0, 0, unit_price * 0.1]), 2)
        line_total = round(quantity * (unit_price - discount), 2)
        tax_rate = random.choice([0.05, 0.07, 0.08])
        line_items.append({
            "order_item_id": str(uuid.uuid4()),
            "order_id": order_id,
            "product_id": product_id,
            "quantity": quantity,
            "unit_price": f"{unit_price:.2f}",
            "discount_amount": f"{discount:.2f}",
            "line_total": f"{line_total:.2f}",
            "tax_rate": f"{tax_rate:.2f}",
        })
        subtotal += line_total
        product_sales[product_id] += quantity
    shipping_cost = round(random.uniform(0, 25), 2)
    tax_amount = round(subtotal * 0.0825, 2)
    total_amount = round(subtotal + shipping_cost + tax_amount, 2)

    customer_spend[customer["customer_id"]] += total_amount
    customer_order_counts[customer["customer_id"]] += 1
    if status in {"cancelled", "returned"}:
        customer_negative_events[customer["customer_id"]] += 1

    sentiment_score = customer_negative_events[customer["customer_id"]] / max(1, customer_order_counts[customer["customer_id"]])
    if sentiment_score > 0.25:
        sentiment = "negative"
    elif sentiment_score > 0.1:
        sentiment = "neutral"
    else:
        sentiment = "positive"

    orders.append({
        "order_id": order_id,
        "customer_id": customer["customer_id"],
        "order_date": order_date.isoformat(),
        "order_status": status,
        **address,
        "subtotal": f"{subtotal:.2f}",
        "shipping_cost": f"{shipping_cost:.2f}",
        "tax_amount": f"{tax_amount:.2f}",
        "total_amount": f"{total_amount:.2f}",
        "coupon_code": coupon_code or "",
        "acquisition_channel": acquisition_channel,
        "customer_sentiment": sentiment,
    })
    order_items.extend(line_items)

for product in products:
    product_id = product["product_id"]
    sold_qty = product_sales[product_id]
    # ensure at least one restock prior
    first_event_time = product_created[product_id] - timedelta(days=random.randint(5, 30))
    inventory_events.append({
        "event_id": str(uuid.uuid4()),
        "product_id": product_id,
        "event_type": "restock",
        "quantity_change": str(random.randint(100, 400)),
        "event_timestamp": first_event_time.isoformat(),
        "note": "Initial load",
        "actor": random.choice(ACTORS),
    })
    # sale events derived from order items
    for _ in range(max(3, sold_qty // 5)):
        qty = random.randint(1, 5)
        event_time = product_created[product_id] + timedelta(days=random.randint(1, THREE_YEARS))
        event_time = min(event_time, NOW)
        inventory_events.append({
            "event_id": str(uuid.uuid4()),
            "product_id": product_id,
            "event_type": "sale",
            "quantity_change": str(-qty),
            "event_timestamp": event_time.isoformat(),
            "note": "order fulfillment",
            "actor": random.choice(ACTORS),
        })
    if random.random() < 0.3:
        inventory_events.append({
            "event_id": str(uuid.uuid4()),
            "product_id": product_id,
            "event_type": "restock",
            "quantity_change": str(random.randint(20, 80)),
            "event_timestamp": random_date().isoformat(),
            "note": "mid-season",
            "actor": random.choice(ACTORS),
        })

for c in customers:
    spend = customer_spend[c["customer_id"]]
    if spend < 500:
        bucket = "low"
    elif spend < 2000:
        bucket = "medium"
    else:
        bucket = "high"
    if spend > 4000:
        tier = "platinum"
    elif spend > 2000:
        tier = "gold"
    elif spend > 1000:
        tier = "silver"
    else:
        tier = c["loyalty_tier"]
    c["lifetime_value_bucket"] = bucket
    c["loyalty_tier"] = tier


def write_csv(filename: str, rows, fieldnames):
    path = DATA_DIR / filename
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path

paths = {}
paths['customers.csv'] = write_csv(
    "customers.csv",
    customers,
    [
        "customer_id", "first_name", "last_name", "email", "phone",
        "created_at", "marketing_opt_in", "loyalty_tier", "lifetime_value_bucket",
    ],
)
paths['products.csv'] = write_csv(
    "products.csv",
    products,
    [
        "product_id", "name", "category", "brand", "price",
        "created_at", "inventory_count", "active_flag",
    ],
)
paths['orders.csv'] = write_csv(
    "orders.csv",
    orders,
    [
        "order_id", "customer_id", "order_date", "order_status",
        "shipping_address", "shipping_city", "shipping_state", "shipping_postal_code", "shipping_country",
        "subtotal", "shipping_cost", "tax_amount", "total_amount",
        "coupon_code", "acquisition_channel", "customer_sentiment",
    ],
)
paths['order_items.csv'] = write_csv(
    "order_items.csv",
    order_items,
    [
        "order_item_id", "order_id", "product_id", "quantity", "unit_price",
        "discount_amount", "line_total", "tax_rate",
    ],
)
paths['inventory_events.csv'] = write_csv(
    "inventory_events.csv",
    inventory_events,
    [
        "event_id", "product_id", "event_type", "quantity_change",
        "event_timestamp", "note", "actor",
    ],
)

summary = {
    name: sum(1 for _ in path.open()) - 1 for name, path in paths.items()
}

readme_path = DATA_DIR / "README.md"
with readme_path.open("w", encoding="utf-8") as f:
    f.write("# Synthetic E-Commerce Dataset\n\n")
    f.write("Generated via scripts/generate_data.py. All timestamps fall within the last three years.\n\n")
    f.write("## Files & Row Counts\n")
    for name, count in summary.items():
        f.write(f"- {name}: ~{count} rows\n")
    f.write("\n## Validation Highlights\n")
    f.write("- Referentials: orders -> customers, order_items -> (orders, products).\n")
    f.write("- Financials: total_amount = subtotal + shipping + tax (rounded).\n")
    f.write("- Inventory: sale events reflect item quantities sold; periodic restocks added.\n")
    f.write("- Loyalty: tiers and lifetime value buckets derive from cumulative spend.\n")

print("Generated dataset:")
for name, path in paths.items():
    print(f"- {name}: {summary[name]} rows -> {path}")
