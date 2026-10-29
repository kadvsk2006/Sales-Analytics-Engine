"""Sales Intelligence dashboard backed by the PostgreSQL sales warehouse."""

import os

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

load_dotenv()

st.set_page_config(
    page_title="Sales Intelligence | Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# A clean, responsive layout. Plotly charts use a matching neutral canvas.
st.markdown(
    """
    <style>
      .block-container {padding-top: 1.35rem; padding-bottom: 2.2rem; max-width: 1500px;}
      [data-testid="stSidebar"] {border-right: 1px solid rgba(128,128,128,.18);}
      [data-testid="stMetric"] {
        background: var(--secondary-background-color);
        border: 1px solid rgba(128,128,128,.20);
        border-radius: 14px; padding: 15px 17px; min-height: 108px;
      }
      [data-testid="stMetricLabel"] {font-size: .84rem;}
      [data-testid="stMetricValue"] {font-size: clamp(1.25rem, 2vw, 1.9rem);}
      .hero {
        padding: 22px 25px; border-radius: 18px;
        background: linear-gradient(115deg, rgba(59,130,246,.14), rgba(16,185,129,.08));
        border: 1px solid rgba(128,128,128,.22); margin-bottom: 18px;
      }
      .eyebrow {font-size:.76rem; text-transform:uppercase; letter-spacing:.13em; opacity:.72; font-weight:700;}
      .hero h1 {margin: 5px 0 5px 0; font-size:2rem;}
      .muted {opacity:.72; font-size:.91rem;}
      div[data-testid="stPlotlyChart"] {border: 1px solid rgba(128,128,128,.15); border-radius: 14px; padding: 5px;}
      .section-label {font-size: .77rem; text-transform: uppercase; letter-spacing: .1em; opacity:.68; font-weight:700;}
    </style>
    """,
    unsafe_allow_html=True,
)


def get_engine():
    """Build a safe SQLAlchemy URL, including passwords with special characters."""
    url = URL.create(
        drivername="postgresql+psycopg2",
        username=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "sales_analytics"),
    )
    return create_engine(url, pool_pre_ping=True)


@st.cache_data(ttl=300, show_spinner=False)
def query(sql, params=None):
    with get_engine().connect() as conn:
        return pd.read_sql(text(sql), conn, params=params or {})


def money(value):
    """Compact INR formatting keeps KPI values readable on narrower screens."""
    value = float(value or 0)
    if abs(value) >= 10_000_000:
        return f"₹{value / 10_000_000:.2f}Cr"
    if abs(value) >= 100_000:
        return f"₹{value / 100_000:.2f}L"
    return f"₹{value:,.0f}"


def chart_layout(fig, *, x_title=None, y_title=None, height=340):
    fig.update_layout(
        height=height,
        margin=dict(l=12, r=18, t=58, b=12),
        title=dict(x=0.03, xanchor="left", font=dict(size=17)),
        font=dict(size=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        hoverlabel=dict(namelength=-1),
    )
    fig.update_xaxes(title=x_title or "", showgrid=False, zeroline=False)
    fig.update_yaxes(title=y_title or "", gridcolor="rgba(128,128,128,.18)", zeroline=False)
    return fig


st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">Sales operations · Data engineering · Business analytics</div>
      <h1>Sales Intelligence</h1>
      <div class="muted">CSV → Python ETL → Data quality checks → PostgreSQL star schema → SQL analytics</div>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    bounds = query("""
        SELECT MIN(d.order_date) AS min_date, MAX(d.order_date) AS max_date
        FROM fact_sales f JOIN dim_date d ON f.date_key = d.date_key
    """)
    if bounds.empty or pd.isna(bounds.loc[0, "min_date"]):
        st.warning("The warehouse is empty. Run `python etl\\pipeline.py` to load the sales dataset.")
        st.stop()

    categories = query("SELECT DISTINCT category FROM dim_product ORDER BY category")
    regions = query("SELECT DISTINCT region FROM dim_region ORDER BY region")
    min_date = pd.to_datetime(bounds.loc[0, "min_date"]).date()
    max_date = pd.to_datetime(bounds.loc[0, "max_date"]).date()

    with st.sidebar:
        st.markdown("## Dashboard filters")
        st.caption("Choose a date window and business segment.")
        selected_dates = st.date_input(
            "Order date range", value=(min_date, max_date), min_value=min_date, max_value=max_date
        )
        selected_categories = st.multiselect(
            "Product categories", categories["category"].tolist(), default=categories["category"].tolist()
        )
        selected_regions = st.multiselect(
            "Sales regions", regions["region"].tolist(), default=regions["region"].tolist()
        )
        if st.button("Reset dashboard cache", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        st.divider()
        st.caption("Data source: PostgreSQL · Cache refresh: 5 minutes")

    if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
        start_date, end_date = selected_dates
    elif isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 1:
        start_date = end_date = selected_dates[0]
    else:
        start_date = end_date = selected_dates

    cat_params = {f"cat{i}": value for i, value in enumerate(selected_categories)}
    reg_params = {f"reg{i}": value for i, value in enumerate(selected_regions)}
    cat_in = ", ".join(f":cat{i}" for i in range(len(selected_categories))) or "NULL"
    reg_in = ", ".join(f":reg{i}" for i in range(len(selected_regions))) or "NULL"
    params = {"start_date": start_date, "end_date": end_date, **cat_params, **reg_params}
    where_clause = f"""
        d.order_date BETWEEN :start_date AND :end_date
        AND p.category IN ({cat_in})
        AND r.region IN ({reg_in})
    """
    joins = """
        FROM fact_sales f
        JOIN dim_date d ON f.date_key = d.date_key
        JOIN dim_product p ON f.product_id = p.product_id
        JOIN dim_region r ON f.region_key = r.region_key
    """

    kpi = query(f"""
        SELECT COALESCE(SUM(f.revenue), 0) AS revenue,
               COUNT(DISTINCT f.order_id) AS orders,
               COUNT(DISTINCT f.customer_id) AS customers,
               COALESCE(SUM(f.revenue) / NULLIF(COUNT(DISTINCT f.order_id), 0), 0) AS aov,
               COALESCE(SUM(f.quantity), 0) AS units
        {joins} WHERE {where_clause}
    """, params).iloc[0]

    st.markdown('<div class="section-label">Performance overview</div>', unsafe_allow_html=True)
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Net sales revenue", money(kpi["revenue"]))
    k2.metric("Orders", f"{int(kpi['orders']):,}")
    k3.metric("Unique customers", f"{int(kpi['customers']):,}")
    k4.metric("Average order value", money(kpi["aov"]))
    k5.metric("Units sold", f"{int(kpi['units']):,}")
    st.caption(
        f"Period: {start_date:%d %b %Y} – {end_date:%d %b %Y}  ·  "
        f"{len(selected_categories)} categories  ·  {len(selected_regions)} regions"
    )

    if not selected_categories or not selected_regions or int(kpi["orders"]) == 0:
        st.info("No sales match these filters. Select at least one category and one region, or widen the date range.")
        st.stop()

    monthly = query(f"""
        SELECT DATE_TRUNC('month', d.order_date) AS month,
               SUM(f.revenue) AS revenue,
               COUNT(DISTINCT f.order_id) AS orders
        {joins} WHERE {where_clause}
        GROUP BY 1 ORDER BY 1
    """, params)
    category = query(f"""
        SELECT p.category, SUM(f.revenue) AS revenue, SUM(f.quantity) AS units
        {joins} WHERE {where_clause}
        GROUP BY p.category ORDER BY revenue DESC
    """, params)
    region = query(f"""
        SELECT r.region, SUM(f.revenue) AS revenue
        {joins} WHERE {where_clause}
        GROUP BY r.region ORDER BY revenue DESC
    """, params)
    top_products = query(f"""
        SELECT p.product_name, p.category,
               SUM(f.quantity) AS units_sold, SUM(f.revenue) AS revenue
        {joins} WHERE {where_clause}
        GROUP BY p.product_name, p.category
        ORDER BY revenue DESC LIMIT 10
    """, params)
    repeat = query(f"""
        WITH customer_orders AS (
            SELECT f.customer_id, COUNT(DISTINCT f.order_id) AS order_count
            {joins} WHERE {where_clause}
            GROUP BY f.customer_id
        )
        SELECT COALESCE(
            100.0 * COUNT(*) FILTER (WHERE order_count > 1) / NULLIF(COUNT(*), 0), 0
        ) AS repeat_rate
        FROM customer_orders
    """, params)

    st.divider()
    left, right = st.columns([1.55, 1])
    with left:
        fig = px.line(monthly, x="month", y="revenue", markers=True, title="Monthly revenue trend")
        fig.update_traces(line_width=3, marker_size=6, hovertemplate="%{x|%b %Y}<br>Revenue: ₹%{y:,.0f}<extra></extra>")
        fig.update_yaxes(tickprefix="₹", tickformat="~s")
        chart_layout(fig, height=360)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    with right:
        cat_plot = category.sort_values("revenue", ascending=True)
        fig = px.bar(cat_plot, x="revenue", y="category", orientation="h", text="revenue", title="Revenue by category")
        fig.update_traces(texttemplate="₹%{x:,.0f}", textposition="outside", cliponaxis=False,
                          hovertemplate="%{y}<br>Revenue: ₹%{x:,.0f}<extra></extra>")
        fig.update_xaxes(tickprefix="₹", tickformat="~s")
        chart_layout(fig, height=360)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    left, right = st.columns(2)
    with left:
        region_plot = region.sort_values("revenue", ascending=True)
        fig = px.bar(region_plot, x="revenue", y="region", orientation="h", text="revenue", title="Revenue by region")
        fig.update_traces(texttemplate="₹%{x:,.0f}", textposition="outside", cliponaxis=False,
                          hovertemplate="%{y}<br>Revenue: ₹%{x:,.0f}<extra></extra>")
        fig.update_xaxes(tickprefix="₹", tickformat="~s")
        chart_layout(fig, height=330)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    with right:
        product_plot = top_products.sort_values("revenue", ascending=True)
        fig = px.bar(product_plot, x="revenue", y="product_name", orientation="h", title="Top 10 products by revenue",
                     hover_data={"category": True, "units_sold": ":,", "revenue": ":,.2f"})
        fig.update_traces(hovertemplate="%{y}<br>Revenue: ₹%{x:,.0f}<extra></extra>")
        fig.update_xaxes(tickprefix="₹", tickformat="~s")
        chart_layout(fig, height=390)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.divider()
    table_col, insight_col = st.columns([1.6, 1])
    with table_col:
        st.subheader("Product leaderboard")
        display = top_products.copy()
        display["revenue"] = display["revenue"].map(lambda v: f"₹{v:,.2f}")
        display = display.rename(columns={
            "product_name": "Product", "category": "Category",
            "units_sold": "Units sold", "revenue": "Revenue"
        })
        st.dataframe(display, use_container_width=True, hide_index=True)
    with insight_col:
        st.subheader("Customer retention signal")
        rate = float(repeat.loc[0, "repeat_rate"] or 0)
        st.metric("Repeat customer rate", f"{rate:.2f}%")
        st.caption("Share of customers with 2+ distinct orders within the selected date, category and region filters.")
        st.info("Interpret this metric in the context of the sample data. The bundled dataset is synthetic, and its customer-order frequency makes the repeat rate unusually high.")

    st.divider()
    st.subheader("Warehouse data-quality checks")
    st.caption("These checks cover the full loaded warehouse, not just the selected dashboard filters.")
    health = query("""
        SELECT
            COUNT(*) AS fact_rows,
            COUNT(DISTINCT order_id) AS unique_orders,
            COUNT(*) FILTER (WHERE revenue IS NULL) AS null_revenue,
            COUNT(*) FILTER (WHERE quantity IS NULL OR quantity <= 0) AS invalid_quantity,
            COUNT(*) FILTER (WHERE unit_price IS NULL OR unit_price < 0) AS invalid_unit_price,
            COUNT(*) FILTER (WHERE discount IS NULL OR discount < 0 OR discount > 1) AS invalid_discount,
            COUNT(*) FILTER (WHERE ABS(revenue - ROUND(quantity * unit_price * (1 - discount), 2)) > 0.02) AS revenue_mismatch,
            COUNT(*) FILTER (WHERE d.date_key IS NULL OR c.customer_id IS NULL OR p.product_id IS NULL OR r.region_key IS NULL) AS broken_dimension_links
        FROM fact_sales f
        LEFT JOIN dim_date d ON f.date_key = d.date_key
        LEFT JOIN dim_customer c ON f.customer_id = c.customer_id
        LEFT JOIN dim_product p ON f.product_id = p.product_id
        LEFT JOIN dim_region r ON f.region_key = r.region_key
    """).iloc[0]
    h1, h2, h3, h4 = st.columns(4)
    h1.metric("Fact rows", f"{int(health['fact_rows']):,}")
    h2.metric("Unique orders", f"{int(health['unique_orders']):,}")
    h3.metric("Null revenue", f"{int(health['null_revenue']):,}")
    h4.metric("Revenue mismatches", f"{int(health['revenue_mismatch']):,}")
    h5, h6, h7, h8 = st.columns(4)
    h5.metric("Invalid quantities", f"{int(health['invalid_quantity']):,}")
    h6.metric("Invalid prices", f"{int(health['invalid_unit_price']):,}")
    h7.metric("Invalid discounts", f"{int(health['invalid_discount']):,}")
    h8.metric("Broken dimension links", f"{int(health['broken_dimension_links']):,}")

    with st.expander("Project architecture and metric definitions"):
        st.markdown("""
        **Pipeline:** raw CSV → extraction → Pandas transformation and validation → PostgreSQL → SQL analytics → Streamlit.

        **Warehouse model:** `fact_sales` links to `dim_date`, `dim_customer`, `dim_product`, and `dim_region`.

        **Metric definitions:**
        - **Revenue:** sum of line-level sales after discount, recalculated as quantity × unit price × (1 − discount).
        - **Average order value:** revenue ÷ distinct order IDs.
        - **Repeat customer rate:** customers with more than one distinct order in the selected slice ÷ all customers in that slice.
        - **Data quality:** warehouse-wide checks for nulls, invalid quantities/prices/discounts, revenue arithmetic mismatches, and broken dimension references.
        """)

except Exception as exc:
    st.error("The dashboard could not connect to PostgreSQL or query the warehouse.")
    st.code(str(exc))
    st.info("Check PostgreSQL is running, the .env credentials are correct, and `python etl\\pipeline.py` has completed successfully.")
