
from flask import Blueprint, current_app, render_template
from sqlalchemy import text
from analytics import calculate_average_order_value
from repositories.sales_repository import REVENUE_EXPRESSION
from charts import (
    monthly_sales_chart,
    product_revenue_chart,
    regional_revenue_chart,
    customer_gender_chart,
    customer_age_chart,
    render_chart,
)


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def home():

    # Get the existing application database engine.
    engine = current_app.extensions["db_engine"]

    # ----------------------------------------------
    # KPI SUMMARY - FULL DATASET
    # ----------------------------------------------

    query = text(f"""
        SELECT
            COALESCE(
                SUM(
                    {REVENUE_EXPRESSION}
                ), 0
            ) AS total_net_sales,

            COUNT(DISTINCT order_id) AS total_orders,

            COALESCE(SUM(quantity), 0) AS units_sold

        FROM sales
    """)

    with engine.connect() as connection:
        result = connection.execute(
            query
        ).mappings().one()

    total_net_sales = float(result["total_net_sales"])
    total_orders = int(result["total_orders"])
    units_sold = int(result["units_sold"])

    average_order_value = calculate_average_order_value(
        total_net_sales, total_orders
    )

    kpis = {
        "total_net_sales": total_net_sales,
        "total_orders": total_orders,
        "units_sold": units_sold,
        "average_order_value": average_order_value
    }

    # ----------------------------------------------
    # MONTHLY SALES TREND - FULL DATASET
    # ----------------------------------------------

    monthly_query = text(f"""
        SELECT
            DATE_FORMAT(order_date, '%Y-%m') AS sales_month,

            SUM(
                {REVENUE_EXPRESSION}
            ) AS monthly_revenue

        FROM sales

        GROUP BY DATE_FORMAT(order_date, '%Y-%m')

        ORDER BY sales_month
    """)

    with engine.connect() as connection:
        monthly_results = connection.execute(
            monthly_query
        ).mappings().all()

    monthly_labels = [
        row["sales_month"]
        for row in monthly_results
    ]

    monthly_revenue = [
        float(row["monthly_revenue"] or 0)
        for row in monthly_results
    ]

    # ----------------------------------------------
    # PRODUCT CATEGORY ANALYTICS
    # ----------------------------------------------

    product_query = text(f"""
        SELECT
            product_category,

            SUM(
                {REVENUE_EXPRESSION}
            ) AS category_revenue

        FROM sales

        GROUP BY product_category

        ORDER BY category_revenue DESC
    """)

    with engine.connect() as connection:
        product_results = connection.execute(
            product_query
        ).mappings().all()

    product_labels = [
        row["product_category"]
        for row in product_results
    ]

    product_revenue = [
        float(row["category_revenue"] or 0)
        for row in product_results
    ]

    # ----------------------------------------------
    # REGIONAL SALES ANALYTICS
    # ----------------------------------------------

    regional_query = text(f"""
        SELECT
            state,

            SUM(
                {REVENUE_EXPRESSION}
            ) AS state_revenue

        FROM sales

        GROUP BY state

        ORDER BY state_revenue DESC
    """)

    with engine.connect() as connection:
        regional_results = connection.execute(
            regional_query
        ).mappings().all()

    regional_labels = [
        row["state"]
        for row in regional_results
    ]

    regional_revenue = [
        float(row["state_revenue"] or 0)
        for row in regional_results
    ]

    # ----------------------------------------------
    # CUSTOMER GENDER ANALYTICS
    # ----------------------------------------------

    gender_query = text("""
        SELECT
            customer_gender,
            COUNT(*) AS total_orders

        FROM sales

        GROUP BY customer_gender

        ORDER BY total_orders DESC
    """)

    with engine.connect() as connection:
        gender_results = connection.execute(
            gender_query
        ).mappings().all()

    gender_labels = [
        row["customer_gender"]
        for row in gender_results
    ]

    gender_counts = [
        int(row["total_orders"])
        for row in gender_results
    ]

    # ----------------------------------------------
    # CUSTOMER AGE GROUP ANALYTICS
    # ----------------------------------------------

    age_query = text("""
        SELECT
            CASE
                WHEN customer_age < 20 THEN 'Below 20'
                WHEN customer_age BETWEEN 20 AND 29 THEN '20-29'
                WHEN customer_age BETWEEN 30 AND 39 THEN '30-39'
                WHEN customer_age BETWEEN 40 AND 49 THEN '40-49'
                WHEN customer_age BETWEEN 50 AND 59 THEN '50-59'
                ELSE '60 and above'
            END AS age_group,

            COUNT(*) AS total_customers

        FROM sales

        GROUP BY age_group

        ORDER BY MIN(customer_age)
    """)

    with engine.connect() as connection:
        age_results = connection.execute(
            age_query
        ).mappings().all()

    age_labels = [
        row["age_group"]
        for row in age_results
    ]

    age_counts = [
        int(row["total_customers"])
        for row in age_results
    ]

    # ----------------------------------------------
    # CHART GENERATION
    # ----------------------------------------------

    charts = {
        "monthly_sales": render_chart(
            monthly_sales_chart(monthly_labels, monthly_revenue),
            "monthlySalesPlot"
        ),
        "product_sales": render_chart(
            product_revenue_chart(product_labels, product_revenue),
            "productSalesPlot"
        ),
        "regional_sales": render_chart(
            regional_revenue_chart(regional_labels, regional_revenue),
            "regionalSalesPlot"
        ),
        "gender": render_chart(
            customer_gender_chart(gender_labels, gender_counts),
            "genderPlot"
        ),
        "age": render_chart(
            customer_age_chart(age_labels, age_counts),
            "agePlot"
        ),
    }

    # ----------------------------------------------
    # RENDER HOME DASHBOARD
    # ----------------------------------------------

    return render_template(
        "index.html",
        kpis=kpis,
        monthly_labels=monthly_labels,
        monthly_revenue=monthly_revenue,
        product_labels=product_labels,
        product_revenue=product_revenue,
        regional_labels=regional_labels,
        regional_revenue=regional_revenue,
        gender_labels=gender_labels,
        gender_counts=gender_counts,
        age_labels=age_labels,
        age_counts=age_counts,
        charts=charts
    )
