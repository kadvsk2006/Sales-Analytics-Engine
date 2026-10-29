DROP TABLE IF EXISTS fact_sales CASCADE;
DROP TABLE IF EXISTS dim_customer CASCADE;
DROP TABLE IF EXISTS dim_product CASCADE;
DROP TABLE IF EXISTS dim_date CASCADE;
DROP TABLE IF EXISTS dim_region CASCADE;

CREATE TABLE dim_customer (
    customer_id VARCHAR(30) PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL
);

CREATE TABLE dim_product (
    product_id VARCHAR(30) PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL,
    category VARCHAR(100) NOT NULL
);

CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,
    order_date DATE UNIQUE NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    quarter INTEGER NOT NULL
);

CREATE TABLE dim_region (
    region_key SERIAL PRIMARY KEY,
    region VARCHAR(50) NOT NULL,
    city VARCHAR(100) NOT NULL,
    UNIQUE(region, city)
);

CREATE TABLE fact_sales (
    sales_key BIGSERIAL PRIMARY KEY,
    order_id VARCHAR(30) UNIQUE NOT NULL,
    date_key INTEGER REFERENCES dim_date(date_key),
    customer_id VARCHAR(30) REFERENCES dim_customer(customer_id),
    product_id VARCHAR(30) REFERENCES dim_product(product_id),
    region_key INTEGER REFERENCES dim_region(region_key),
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(12,2) NOT NULL,
    discount NUMERIC(5,2) NOT NULL,
    revenue NUMERIC(14,2) NOT NULL,
    payment_method VARCHAR(50)
);

CREATE INDEX idx_fact_date ON fact_sales(date_key);
CREATE INDEX idx_fact_customer ON fact_sales(customer_id);
CREATE INDEX idx_fact_product ON fact_sales(product_id);
