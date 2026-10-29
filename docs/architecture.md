# System Architecture

```mermaid
flowchart LR
    A[Raw sales.csv] --> B[Extract\nPython + Pandas]
    B --> C[Validate\nnulls • duplicates • schema • values]
    C --> D[Transform\nclean types • derive revenue/date fields]
    D --> E[Load\nSQLAlchemy + psycopg2]
    E --> F[(PostgreSQL\nStar Schema)]
    F --> G[SQL Analytics\nJOIN • CTE • Window Functions]
    G --> H[Streamlit Dashboard]

    F --> I[dim_date]
    F --> J[dim_customer]
    F --> K[dim_product]
    F --> L[dim_region]
    F --> M[fact_sales]
```

## Star schema

```mermaid
erDiagram
    DIM_DATE ||--o{ FACT_SALES : date_key
    DIM_CUSTOMER ||--o{ FACT_SALES : customer_id
    DIM_PRODUCT ||--o{ FACT_SALES : product_id
    DIM_REGION ||--o{ FACT_SALES : region_key

    DIM_DATE {
      int date_key PK
      date order_date
      int year
      int month
      string month_name
      int quarter
    }
    DIM_CUSTOMER {
      string customer_id PK
      string customer_name
    }
    DIM_PRODUCT {
      string product_id PK
      string product_name
      string category
    }
    DIM_REGION {
      int region_key PK
      string region
      string city
    }
    FACT_SALES {
      bigint sales_key PK
      string order_id UK
      int date_key FK
      string customer_id FK
      string product_id FK
      int region_key FK
      int quantity
      decimal unit_price
      decimal discount
      decimal revenue
      string payment_method
    }
```

## Data flow

1. **Extract** reads the raw CSV.
2. **Validate** checks required columns, nulls, duplicates, types and business-rule values.
3. **Transform** standardizes dates/numerics and prepares dimension/fact attributes.
4. **Load** truncates the warehouse tables and reloads the current dataset through SQLAlchemy.
5. **Analytics SQL** uses joins, CTEs, aggregation and window functions.
6. **Dashboard** queries PostgreSQL and exposes filters and KPIs through Streamlit.
