from pathlib import Path

import numpy as np
import pandas as pd

RANDOM_SEED = 42
SCENARIO_NAME = "revenue_decline_v1"

OUTPUT_DIR = Path("data")

PRODUCT_CATEGORIES = [
    "Computing",
    "Networking",
    "Accessories",
    "Office",
]

PRODUCTS_PER_CATEGORY = 5

PRODUCT_COST_RANGES = {
    "Computing": (300.0, 1200.0),
    "Networking": (80.0, 500.0),
    "Accessories": (10.0, 120.0),
    "Office": (30.0, 300.0),
}

CUSTOMER_COUNT = 300

CUSTOMER_SEGMENTS = [
    "SMB",
    "Mid-Market",
    "Enterprise",
]

CUSTOMER_REGIONS = [
    "North",
    "South",
    "East",
    "West",
]

ACQUISITION_CHANNELS = [
    "Organic",
    "Paid Search",
    "Referral",
    "Partner",
]

CUSTOMER_SIGNUP_START = "2023-01-01"
CUSTOMER_SIGNUP_END = "2025-06-30"

BASELINE_START = "2025-07-01"
BASELINE_END = "2025-07-31"

COMPARISON_START = "2025-08-01"
COMPARISON_END = "2025-08-31"

BASELINE_ORDER_COUNT = 1200
COMPARISON_ORDER_COUNT = 1050

SALES_CHANNELS = [
    "Web",
    "Direct",
    "Partner",
]

BASE_DISCOUNT_RANGE = (0.0, 0.12)
PARTNER_AUGUST_DISCOUNT_RANGE = (0.08, 0.22)

PRICE_MARKUP_RANGE = (1.25, 1.75)


def generate_products(rng: np.random.Generator) -> pd.DataFrame:
    products = []
    product_id = 1

    for category in PRODUCT_CATEGORIES:
        min_cost, max_cost = PRODUCT_COST_RANGES[category]

        for product_number in range(1, PRODUCTS_PER_CATEGORY + 1):
            products.append(
                {
                    "product_id": f"P{product_id:03d}",
                    "product_name": f"{category} Product {product_number:02d}",
                    "category": category,
                    "unit_cost": round(rng.uniform(min_cost, max_cost), 2),
                }
            )

            product_id += 1

    return pd.DataFrame(products)


def generate_customers(rng: np.random.Generator) -> pd.DataFrame:
    customers = []

    signup_start = pd.Timestamp(CUSTOMER_SIGNUP_START)
    signup_end = pd.Timestamp(CUSTOMER_SIGNUP_END)
    signup_range_days = (signup_end - signup_start).days

    for customer_number in range(1, CUSTOMER_COUNT + 1):
        signup_offset_days = rng.integers(0, signup_range_days + 1)
        signup_date = signup_start + pd.Timedelta(days=int(signup_offset_days))

        customers.append(
            {
                "customer_id": f"C{customer_number:04d}",
                "signup_date": signup_date.date(),
                "segment": rng.choice(CUSTOMER_SEGMENTS),
                "region": rng.choice(CUSTOMER_REGIONS),
                "acquisition_channel": rng.choice(ACQUISITION_CHANNELS),
            }
        )

    return pd.DataFrame(customers)


def random_date(
    rng: np.random.Generator,
    start_date: str,
    end_date: str,
) -> pd.Timestamp:
    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date)

    date_range_days = (end - start).days
    offset_days = rng.integers(0, date_range_days + 1)

    return start + pd.Timedelta(days=int(offset_days))


def choose_customer(
    rng: np.random.Generator,
    customers: pd.DataFrame,
    period: str,
) -> pd.Series:
    if period == "comparison":
        weights = np.where(customers["region"] == "South", 0.45, 1.0)
        probabilities = weights / weights.sum()

        index = rng.choice(
            customers.index.to_numpy(),
            p=probabilities,
        )

        return customers.loc[index]

    index = rng.choice(customers.index.to_numpy())
    return customers.loc[index]


def choose_product(
    rng: np.random.Generator,
    products: pd.DataFrame,
    period: str,
) -> pd.Series:
    if period == "comparison":
        weights = np.where(products["category"] == "Computing", 0.65, 1.0)
        probabilities = weights / weights.sum()

        index = rng.choice(
            products.index.to_numpy(),
            p=probabilities,
        )

        return products.loc[index]

    index = rng.choice(products.index.to_numpy())
    return products.loc[index]


def generate_order_batch(
    rng: np.random.Generator,
    customers: pd.DataFrame,
    products: pd.DataFrame,
    order_count: int,
    start_date: str,
    end_date: str,
    period: str,
    starting_order_number: int,
) -> list[dict]:
    orders = []

    for offset in range(order_count):
        order_number = starting_order_number + offset

        customer = choose_customer(
            rng=rng,
            customers=customers,
            period=period,
        )

        product = choose_product(
            rng=rng,
            products=products,
            period=period,
        )

        sales_channel = rng.choice(SALES_CHANNELS)

        quantity = int(rng.integers(1, 6))

        unit_price = round(
            float(product["unit_cost"] * rng.uniform(*PRICE_MARKUP_RANGE)),
            2,
        )

        if period == "comparison" and sales_channel == "Partner":
            discount = round(
                float(rng.uniform(*PARTNER_AUGUST_DISCOUNT_RANGE)),
                4,
            )
        else:
            discount = round(
                float(rng.uniform(*BASE_DISCOUNT_RANGE)),
                4,
            )

        orders.append(
            {
                "order_id": f"O{order_number:05d}",
                "customer_id": customer["customer_id"],
                "product_id": product["product_id"],
                "order_date": random_date(
                    rng,
                    start_date,
                    end_date,
                ).date(),
                "quantity": quantity,
                "unit_price": unit_price,
                "discount": discount,
                "sales_channel": sales_channel,
            }
        )

    return orders


def generate_orders(
    rng: np.random.Generator,
    customers: pd.DataFrame,
    products: pd.DataFrame,
) -> pd.DataFrame:
    baseline_orders = generate_order_batch(
        rng=rng,
        customers=customers,
        products=products,
        order_count=BASELINE_ORDER_COUNT,
        start_date=BASELINE_START,
        end_date=BASELINE_END,
        period="baseline",
        starting_order_number=1,
    )

    comparison_orders = generate_order_batch(
        rng=rng,
        customers=customers,
        products=products,
        order_count=COMPARISON_ORDER_COUNT,
        start_date=COMPARISON_START,
        end_date=COMPARISON_END,
        period="comparison",
        starting_order_number=BASELINE_ORDER_COUNT + 1,
    )

    return pd.DataFrame(baseline_orders + comparison_orders)


def write_datasets(
    products: pd.DataFrame,
    customers: pd.DataFrame,
    orders: pd.DataFrame,
) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    products.to_csv(
        OUTPUT_DIR / "products.csv",
        index=False,
    )

    customers.to_csv(
        OUTPUT_DIR / "customers.csv",
        index=False,
    )

    orders.to_csv(
        OUTPUT_DIR / "orders.csv",
        index=False,
    )


def print_summary(
    products: pd.DataFrame,
    customers: pd.DataFrame,
    orders: pd.DataFrame,
) -> None:
    print(f"Scenario: {SCENARIO_NAME}")
    print(f"Random seed: {RANDOM_SEED}")
    print()

    print("Products")
    print(f"Rows: {len(products)}")
    print(f"Unique product IDs: {products['product_id'].nunique()}")
    print(products["category"].value_counts())
    print()

    print("Customers")
    print(f"Rows: {len(customers)}")
    print(f"Unique customer IDs: {customers['customer_id'].nunique()}")
    print(f"Earliest signup: {customers['signup_date'].min()}")
    print(f"Latest signup: {customers['signup_date'].max()}")
    print(customers["region"].value_counts())
    print()

    print("Orders")
    print(f"Rows: {len(orders)}")
    print(f"Unique order IDs: {orders['order_id'].nunique()}")
    print(f"Earliest order: {orders['order_date'].min()}")
    print(f"Latest order: {orders['order_date'].max()}")
    print()

    orders_with_context = orders.merge(
        customers[["customer_id", "region"]],
        on="customer_id",
        how="left",
    ).merge(
        products[["product_id", "category"]],
        on="product_id",
        how="left",
    )

    orders_with_context["month"] = pd.to_datetime(
        orders_with_context["order_date"]
    ).dt.to_period("M")

    orders_with_context["net_revenue"] = (
        orders_with_context["quantity"]
        * orders_with_context["unit_price"]
        * (1 - orders_with_context["discount"])
    )

    print("Orders by month")
    print(orders_with_context["month"].value_counts().sort_index())
    print()

    print("Net revenue by month")
    print(orders_with_context.groupby("month")["net_revenue"].sum().round(2))
    print()

    print("Orders by month and region")
    print(orders_with_context.groupby(["month", "region"]).size())
    print()

    print("Orders by month and category")
    print(orders_with_context.groupby(["month", "category"]).size())
    print()

    print("Average discount by month and sales channel")
    print(
        orders_with_context.groupby(["month", "sales_channel"])["discount"]
        .mean()
        .round(4)
    )


def main() -> None:
    rng = np.random.default_rng(RANDOM_SEED)

    products = generate_products(rng)
    customers = generate_customers(rng)
    orders = generate_orders(
        rng=rng,
        customers=customers,
        products=products,
    )

    write_datasets(
        products=products,
        customers=customers,
        orders=orders,
    )

    print_summary(
        products=products,
        customers=customers,
        orders=orders,
    )


if __name__ == "__main__":
    main()
