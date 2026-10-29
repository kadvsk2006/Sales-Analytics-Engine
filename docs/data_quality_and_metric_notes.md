# Analytics review and data-quality notes

These observations are based on the bundled `data/raw/sales.csv` sample (15,000 rows). It is synthetic demonstration data, so the results should not be presented as real-world company performance.

## Sample data checks

| Check | Result in bundled CSV | Interpretation |
|---|---:|---|
| Rows / unique order IDs | 15,000 / 15,000 | One row per order in this sample |
| Unique customers | 1,500 | Generated customer IDs |
| Unique products | 20 | Product catalogue in the sample |
| Missing values | 0 across the 13 columns | No nulls in the raw sample |
| Duplicate order IDs | 0 | Order identifier is unique |
| Quantity <= 0 | 0 | No invalid quantities detected |
| Negative unit prices | 0 | No negative prices detected |
| Discounts outside 0–1 | 0 | Discounts use decimal fractions, e.g. 0.10 = 10% |
| Revenue arithmetic matches | 100% | `quantity × unit_price × (1 − discount)`, rounded to 2 decimals, matches the provided revenue |
| Total revenue | ₹6,645,301.19 | Approximately ₹66.45 lakh for the full sample period |
| Average revenue per order | ₹443.02 | Total revenue divided by 15,000 distinct orders |
| Repeat-customer rate | 99.93% | 1,499 of 1,500 generated customers have more than one order |

## Important interpretation caveats

1. **Repeat-customer rate is unusually high.** The generator creates 15,000 orders across 1,500 customers, so most customers necessarily appear multiple times. The 99.93% result is mathematically consistent with the sample but should not be described as a typical retail benchmark.
2. **Order grain is one row per order.** The fact table has a unique `order_id` and each sample order has one product. In a real multi-line order system, use a distinct order-line key and calculate AOV by aggregating all line revenue per order first.
3. **Revenue is net of discount.** The ETL recomputes revenue from quantity, unit price, and discount. Keep this definition consistent across SQL, dashboard labels, and interviews.
4. **Warehouse health is not the same as raw-file validation.** Dashboard health metrics inspect loaded fact rows, arithmetic consistency, and dimension references. The ETL validator also checks raw/load-ready data. A production pipeline should additionally persist a run ID, row counts, rejected-row details, load timestamp, and pass/fail status.
5. **Current loader is a full refresh.** It truncates the warehouse tables and reloads the sample. That is acceptable for a learning project, but an incremental production pipeline would need idempotent upserts, transaction strategy, and late-arriving-data handling.

## Suggested interview wording

> “I built a reproducible ETL workflow using synthetic retail data. The pipeline validates fields and business rules, recalculates net revenue, and loads a PostgreSQL star schema. SQL queries and a Streamlit dashboard report sales trends and product/customer metrics. I also added warehouse-level checks for invalid measures, revenue mismatches, and broken dimension references. I call out the synthetic-data limitation, especially the high repeat-customer rate, rather than presenting it as a real business benchmark.”
