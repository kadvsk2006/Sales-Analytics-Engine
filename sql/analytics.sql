-- 1. Monthly revenue
SELECT
    d.year,
    d.month,
    d.month_name,
    ROUND(SUM(f.revenue), 2) AS monthly_revenue
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month;

-- 2. Monthly revenue with running total and previous month
WITH monthly AS (
    SELECT
        d.year,
        d.month,
        SUM(f.revenue) AS revenue
    FROM fact_sales f
    JOIN dim_date d ON f.date_key = d.date_key
    GROUP BY d.year, d.month
)
SELECT
    year,
    month,
    ROUND(revenue, 2) AS revenue,
    ROUND(
        LAG(revenue) OVER (ORDER BY year, month), 2
    ) AS previous_month_revenue,
    ROUND(
        revenue - LAG(revenue) OVER (ORDER BY year, month), 2
    ) AS revenue_change,
    ROUND(
        SUM(revenue) OVER (ORDER BY year, month), 2
    ) AS running_revenue
FROM monthly
ORDER BY year, month;

-- 3. Top-selling products
SELECT
    p.product_id,
    p.product_name,
    p.category,
    SUM(f.quantity) AS units_sold,
    ROUND(SUM(f.revenue), 2) AS revenue
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category
ORDER BY revenue DESC
LIMIT 10;

-- 4. Product ranking within category
SELECT
    p.category,
    p.product_name,
    ROUND(SUM(f.revenue), 2) AS revenue,
    RANK() OVER (
        PARTITION BY p.category
        ORDER BY SUM(f.revenue) DESC
    ) AS category_rank
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.category, p.product_name;

-- 5. Repeat-customer rate
WITH customer_orders AS (
    SELECT
        customer_id,
        COUNT(DISTINCT order_id) AS order_count
    FROM fact_sales
    GROUP BY customer_id
)
SELECT ROUND(
    100.0 * COUNT(*) FILTER (WHERE order_count > 1)
    / NULLIF(COUNT(*), 0), 2
) AS repeat_customer_rate_percent
FROM customer_orders;

-- 6. Revenue by category
SELECT
    p.category,
    ROUND(SUM(f.revenue), 2) AS revenue
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.category
ORDER BY revenue DESC;

-- 7. Revenue by region
SELECT
    r.region,
    ROUND(SUM(f.revenue), 2) AS revenue
FROM fact_sales f
JOIN dim_region r ON f.region_key = r.region_key
GROUP BY r.region
ORDER BY revenue DESC;

-- 8. Average order value
SELECT ROUND(
    SUM(revenue) / NULLIF(COUNT(DISTINCT order_id), 0), 2
) AS average_order_value
FROM fact_sales;

-- 9. Top customers
SELECT
    c.customer_id,
    ROUND(SUM(f.revenue), 2) AS customer_revenue,
    COUNT(DISTINCT f.order_id) AS orders
FROM fact_sales f
JOIN dim_customer c ON f.customer_id = c.customer_id
GROUP BY c.customer_id
ORDER BY customer_revenue DESC
LIMIT 10;
