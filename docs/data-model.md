# DecisionAI Data Model

## 1. Data Model Purpose

The purpose of the DecisionAI data model is to provide a simple, explicit, and reliable data foundation for the MVP.

The initial model is designed to support the primary business question:

> What is affecting revenue performance, and what should I investigate first?

The data model must support deterministic analysis of revenue performance across relevant business dimensions while remaining small enough to understand, validate, test, and evolve safely.

The initial MVP uses three canonical datasets:

- `orders.csv`
- `customers.csv`
- `products.csv`

The data model is intentionally simple. Additional datasets or attributes should only be introduced when a concrete analytical or product requirement justifies them.

---

## 2. Core Datasets

The initial DecisionAI data foundation consists of three datasets.

### `orders.csv`

Represents transactional order activity.

This is the primary fact-like dataset used for revenue analysis.

### `customers.csv`

Represents customer master data.

It provides customer dimensions used to analyze revenue performance across customer characteristics.

### `products.csv`

Represents product master data.

It provides product attributes and cost information used for product-level and category-level analysis.

The primary relationship structure is:

```text
customers
    │
    │ customer_id
    ▼
orders
    ▲
    │ product_id
    │
products
```

---

## 3. Orders Dataset

The `orders.csv` dataset contains one row per order.

### Columns

| Column | Description |
|---|---|
| `order_id` | Unique identifier for the order |
| `customer_id` | Customer associated with the order |
| `product_id` | Product associated with the order |
| `order_date` | Date on which the order occurred |
| `quantity` | Number of product units ordered |
| `unit_price` | Selling price per unit before discount |
| `discount` | Fractional discount applied to the order |
| `sales_channel` | Channel through which the order was placed |

### Example conceptual record

```text
order_id: O00001
customer_id: C0042
product_id: P007
order_date: 2025-07-14
quantity: 3
unit_price: 399.99
discount: 0.10
sales_channel: Partner
```

---

## 4. Customers Dataset

The `customers.csv` dataset contains one row per customer.

### Columns

| Column | Description |
|---|---|
| `customer_id` | Unique identifier for the customer |
| `signup_date` | Date the customer joined |
| `segment` | Business segment assigned to the customer |
| `region` | Geographic business region |
| `acquisition_channel` | Channel through which the customer was acquired |

### Initial customer segments

- `SMB`
- `Mid-Market`
- `Enterprise`

### Initial regions

- `North`
- `South`
- `East`
- `West`

### Initial acquisition channels

- `Organic`
- `Paid Search`
- `Referral`
- `Partner`

---

## 5. Products Dataset

The `products.csv` dataset contains one row per product.

### Columns

| Column | Description |
|---|---|
| `product_id` | Unique identifier for the product |
| `product_name` | Human-readable product name |
| `category` | Product category |
| `unit_cost` | Cost per unit |

### Initial product categories

- `Computing`
- `Networking`
- `Accessories`
- `Office`

---

## 6. Relationships

The initial data model contains two core relationships.

### Customer relationship

```text
orders.customer_id
    →
customers.customer_id
```

Each order must reference an existing customer.

### Product relationship

```text
orders.product_id
    →
products.product_id
```

Each order must reference an existing product.

These relationships are validated before data is considered trustworthy for downstream analytics.

---

## 7. Revenue Definition

Revenue is derived deterministically from order-level fields.

### Gross revenue

```text
gross_revenue = quantity × unit_price
```

### Net revenue

```text
net_revenue = quantity × unit_price × (1 - discount)
```

For the initial MVP, the KPI named `revenue` refers to:

```text
net_revenue
```

Revenue is not stored as an authoritative raw-data column.

It must be derived deterministically from the underlying order fields.

This avoids duplication of business logic and reduces the risk of inconsistent revenue values.

---

## 8. Initial Data Grain

The initial grain of each dataset is:

### Orders

```text
one row = one order
```

### Customers

```text
one row = one customer
```

### Products

```text
one row = one product
```

The MVP does not currently model separate order headers and order-line tables.

That additional complexity is not required for the current business question.

---

## 9. Data Types

The logical data types expected after loading and normalization are:

### Products

| Column | Logical type |
|---|---|
| `product_id` | string |
| `product_name` | string |
| `category` | string |
| `unit_cost` | float |

### Customers

| Column | Logical type |
|---|---|
| `customer_id` | string |
| `signup_date` | datetime |
| `segment` | string |
| `region` | string |
| `acquisition_channel` | string |

### Orders

| Column | Logical type |
|---|---|
| `order_id` | string |
| `customer_id` | string |
| `product_id` | string |
| `order_date` | datetime |
| `quantity` | integer |
| `unit_price` | float |
| `discount` | float |
| `sales_channel` | string |

The logical schema intentionally describes semantic types rather than requiring unnecessary storage-specific details such as a particular datetime resolution.

---

## 10. Nullability

All current MVP fields are required.

The canonical datasets should not contain null values in the defined schema columns.

Required non-null fields include all columns in:

- `orders.csv`
- `customers.csv`
- `products.csv`

Missing required values are treated as data-validation failures rather than being silently imputed.

---

## 11. Referential Integrity

The following referential-integrity rules apply:

```text
orders.customer_id
must exist in
customers.customer_id
```

and:

```text
orders.product_id
must exist in
products.product_id
```

Orders containing unknown customer or product identifiers are considered invalid.

Referential-integrity violations must be detected before the datasets are passed to downstream analytical components.

---

## 12. Data-Model Principle

The initial DecisionAI data model follows these principles:

- Keep the model simple and explicit.
- Prefer deterministic derivation over duplicated calculated fields.
- Keep raw data separate from derived analytical metrics.
- Validate structure before relying on business rules.
- Treat external or loaded data as untrusted until validated.
- Preserve clear dataset grain.
- Maintain explicit primary and foreign key relationships.
- Avoid adding entities, columns, or abstractions without a real analytical requirement.
- Keep scenario ground truth separate from downstream analytical logic.
- Do not encode the expected analytical answer directly into production analytics.

The data model should evolve only when product requirements, analytical requirements, evaluation results, or production constraints justify a change.

---

## 13. Data Foundation Implementation

The MVP data foundation is implemented as a small and explicit pipeline:

```text
CSV datasets
    ↓
Loading
    ↓
Normalization
    ↓
Schema validation
    ↓
Business-rule validation
    ↓
Referential-integrity validation
    ↓
Trusted DataFrames
```

This separates data access, normalization, validation, profiling, and downstream analytical responsibilities.

---

## 14. Synthetic Data Generation

Synthetic datasets are generated by:

```text
scripts/generate_dataset.py
```

The generator produces:

```text
data/products.csv
data/customers.csv
data/orders.csv
```

The synthetic-data strategy uses:

- a fixed random seed,
- fixed historical dates,
- reproducible generation,
- controlled business signals,
- bounded random variation,
- canonical clean datasets.

The current synthetic scenario is:

```text
revenue_decline_v1
```

### Scenario periods

Baseline:

```text
July 2025
```

Comparison:

```text
August 2025
```

### Expected scenario behavior

The scenario is designed so that August net revenue is lower than July net revenue.

### Primary signal

South-region volume weakness.

### Secondary signal

Computing-category weakness.

### Additional smaller signal

Higher discounts in the Partner sales channel during the comparison period.

### Important separation

The scenario's expected behavior is not consumed by downstream analytics.

The analytics layer must infer relevant patterns from the generated data.

Scenario ground truth exists to support later evaluation and verification, not to provide answers to the analytical engine.

---

## 15. Synthetic Dataset Scale

The current generated dataset contains:

### Products

```text
20 products
```

with:

```text
5 products per category
```

### Customers

```text
300 customers
```

### Orders

```text
2250 orders
```

split into:

```text
July 2025:   1200 orders
August 2025: 1050 orders
```

This scale is intentionally small enough for fast local development while large enough to contain meaningful variation for analytical testing.

---

## 16. Data Loading

Dataset loading is implemented in:

```text
app/data/loaders.py
```

The loader boundary is responsible for reading canonical datasets into Pandas DataFrames.

The loading layer also performs basic structural parsing where appropriate.

For example:

- `signup_date` is parsed as a datetime.
- `order_date` is parsed as a datetime.

The loading layer does not apply business-rule corrections.

---

## 17. Data Schemas

Expected columns and logical types are defined in:

```text
app/data/schemas.py
```

Schema definitions cover:

- required column names,
- logical data types.

Schema concerns are intentionally kept separate from business rules.

For example:

```text
quantity exists
```

is a schema concern.

```text
quantity is an integer
```

is a type concern.

```text
quantity > 0
```

is a business-rule concern.

---

## 18. Data Normalization

Safe structural normalization is implemented in:

```text
app/data/cleaning.py
```

The current normalization layer removes accidental leading and trailing whitespace from known string columns.

Examples:

```text
" South "
→
"South"
```

Normalization is deliberately conservative.

It does not silently convert invalid business values into valid values.

For example, it does not automatically transform:

```text
discount = 1.5
```

into:

```text
discount = 1.0
```

Invalid business values should be surfaced by validation instead of hidden through cleaning.

---

## 19. Schema Validation

Schema validation is implemented in:

```text
app/data/validation.py
```

It verifies:

- required columns,
- unexpected columns,
- expected logical data types.

Datetime validation checks whether a field is semantically a datetime rather than requiring a specific NumPy/Pandas datetime resolution.

This avoids unnecessary dependence on internal representation details.

---

## 20. Business-Rule Validation

The initial business rules are:

### Products

```text
unit_cost >= 0
```

### Orders

```text
quantity > 0
unit_price >= 0
0 <= discount <= 1
```

### Required fields

All defined schema columns must be non-null.

Business-rule failures are surfaced explicitly.

The normalization layer must not silently hide them.

---

## 21. Referential-Integrity Validation

Referential-integrity validation verifies that:

```text
orders.customer_id
```

references an existing:

```text
customers.customer_id
```

and:

```text
orders.product_id
```

references an existing:

```text
products.product_id
```

Unknown references make the dataset invalid for downstream analytics.

---

## 22. Validation Result Contract

Structured validation results are defined in:

```text
app/data/contracts.py
```

The current contract is:

```python
ValidationResult(
    is_valid=...,
    errors=[...],
)
```

It contains:

### `is_valid`

Indicates whether the complete validation succeeded.

### `errors`

Contains human-readable validation errors discovered during validation.

This allows callers to inspect validation results without relying solely on exceptions.

---

## 23. Data Error Handling

Data-specific validation failures use:

```text
DataValidationError
```

defined in:

```text
app/data/errors.py
```

The data layer provides two related behaviors:

```text
validate_datasets()
```

returns a structured `ValidationResult`.

```text
ensure_valid_datasets()
```

enforces validity and raises `DataValidationError` when validation fails.

The application must not continue into trusted analytics when required data validation has failed.

---

## 24. Data Profiling

Basic profiling is implemented in:

```text
app/data/profiling.py
```

The current profiling output includes:

- row count,
- column count,
- null counts,
- duplicate row count,
- unique-value counts,
- numeric minimum and maximum values,
- date minimum and maximum values.

Profiling is used to understand the dataset and detect unexpected characteristics.

Profiling is observational and does not silently modify data.

---

## 25. Current Dataset Profile

The canonical synthetic datasets currently show the following structural profile.

### Products

```text
20 rows
4 columns
20 unique product IDs
4 product categories
0 null values
0 duplicate rows
```

### Customers

```text
300 rows
5 columns
300 unique customer IDs
3 customer segments
4 regions
4 acquisition channels
0 null values
0 duplicate rows
```

Observed signup-date range:

```text
2023-01-04
to
2025-06-29
```

### Orders

```text
2250 rows
8 columns
2250 unique order IDs
300 referenced customers
20 referenced products
3 sales channels
0 null values
0 duplicate rows
```

Observed order-date range:

```text
2025-07-01
to
2025-08-31
```

Observed quantity range:

```text
1 to 5
```

Observed discount range:

```text
approximately 0.00 to 0.22
```

---

## 26. Scenario Verification

The generated `revenue_decline_v1` dataset has been manually profiled to verify that the intended synthetic signals are present.

Observed order volume:

```text
July 2025:   1200
August 2025: 1050
```

Observed net revenue:

```text
July 2025:   approximately 1.77M
August 2025: approximately 1.28M
```

The comparison period therefore contains the intended overall revenue decline.

### Regional signal

Observed South order volume:

```text
July:   308
August: 135
```

This provides the intended primary South-region weakness.

### Category signal

Observed Computing order volume:

```text
July:   299
August: 195
```

This provides the intended secondary category-level weakness.

### Partner discount signal

Observed average Partner discount:

```text
July:   approximately 0.058
August: approximately 0.153
```

This provides the intended smaller discount-pressure signal.

These observations verify the synthetic scenario.

They do not establish causal relationships.

Downstream analytics must describe contribution or association appropriately unless a causal methodology is explicitly introduced.

---

## 27. Testing Strategy

The data foundation is covered by automated tests under:

```text
tests/data/
```

The current test suite covers:

- schema validation,
- dtype validation,
- required-field validation,
- business-rule validation,
- referential integrity,
- validation-result construction,
- data-error handling,
- dataset loading,
- normalization,
- profiling,
- end-to-end data pipeline integration.

The current data-layer test suite contains:

```text
27 passing tests
```

at the time of this phase verification.

Test counts may increase as the system evolves, so the number itself is not a permanent architectural contract.

---

## 28. Integration Flow

The current integration test verifies the complete data-foundation flow:

```text
canonical CSV files
        ↓
load
        ↓
normalize
        ↓
validate
        ↓
trusted DataFrames
```

The integration test verifies that the canonical:

- products dataset,
- customers dataset,
- orders dataset

can pass through the complete pipeline successfully.

The trusted DataFrames produced by this boundary are intended to become the input to the Deterministic Analytics Engine.

---

## 29. Data Trust Boundary

DecisionAI treats loaded external data as untrusted until the data foundation has processed it.

The trust transition is:

```text
UNTRUSTED DATA
      ↓
loading
      ↓
normalization
      ↓
validation
      ↓
TRUSTED DATA
      ↓
deterministic analytics
```

Downstream analytical components should not independently bypass this boundary by reading raw datasets directly.

This keeps data-quality responsibilities explicit and reduces the risk that invalid data silently affects business conclusions.

---

## 30. Current Limitations

The initial data model intentionally does not include:

- separate order headers and order lines,
- inventory,
- refunds,
- cancellations,
- taxes,
- shipping,
- currencies,
- customer lifetime value,
- marketing spend,
- product inventory levels,
- multiple companies or tenants,
- streaming data,
- slowly changing dimensions,
- causal intervention data.

These may be introduced later only if product requirements or evaluation results justify them.

---

## 31. Evolution Principle

The data model and data foundation should evolve according to evidence from:

- product requirements,
- analytical needs,
- evaluation results,
- error analysis,
- real user feedback,
- production constraints.

Changes should preserve clear responsibilities between:

```text
generation
loading
normalization
validation
profiling
analytics
AI interpretation
```

The goal is not to maximize the number of abstractions.

The goal is to maintain a simple, trustworthy data foundation that supports reliable evidence-backed decisions.