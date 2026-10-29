# Interview Preparation

## 1. Explain the project in 60 seconds.
I built a Python-based ETL pipeline for retail sales analytics. It extracts raw CSV data, validates data quality, transforms the fields with Pandas, and loads the cleaned data into a PostgreSQL star schema. The warehouse has one sales fact table and four dimensions: date, customer, product and region. I then wrote SQL using joins, CTEs and window functions for revenue trends, product rankings, average order value and repeat-customer analysis. Finally, I connected the database to a Streamlit dashboard for interactive reporting.

## 2. Why did you use a star schema?
A star schema separates measurable business events from descriptive attributes. `fact_sales` stores transaction-level measures while dimensions provide reusable context. It makes analytical queries easier to understand and is well suited to aggregation-heavy reporting.

## 3. Why PostgreSQL?
PostgreSQL provides strong relational integrity, indexing, SQL analytics and compatibility with Python tools such as SQLAlchemy and psycopg2. It is also widely used in data engineering and analytics workloads.

## 4. Why Pandas in the ETL layer?
Pandas is convenient for tabular data cleaning, type conversion, duplicate detection and feature derivation before loading into the warehouse.

## 5. What data-quality checks did you implement?
The pipeline checks schema expectations, missing values, duplicate records, date/numeric conversions and invalid business values such as non-positive quantities and invalid prices/discounts.

## 6. What is a CTE?
A Common Table Expression is a named temporary result set defined with `WITH`. I used CTEs to make multi-step analytical queries easier to read, such as calculating customer order counts before calculating repeat-customer rate.

## 7. Where did you use a window function?
I used `LAG()` to compare monthly revenue with the previous month and `SUM() OVER()` for a running revenue total. I also used `RANK() OVER(PARTITION BY category ...)` to rank products within each category.

## 8. What is AOV?
Average Order Value is total revenue divided by the number of distinct orders.

## 9. How would you scale this project?
I would move from local CSV processing to object storage and scheduled ingestion, use incremental loads instead of full reloads, partition large fact tables by date, add orchestration such as Airflow, and monitor pipeline runs and data-quality metrics.

## 10. What would you improve next?
I would add incremental/upsert loading, a pipeline run metadata table, automated tests in CI, database indexes based on query plans, and role-based database access.
