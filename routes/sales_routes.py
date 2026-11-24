
from flask import Blueprint, current_app, render_template, request
from sqlalchemy import text

from analytics import (
    previous_period,
    percentage_change,
    revenue_contributions,
    calculate_average_order_value,
)

from repositories.sales_repository import (
    build_sales_filters,
    REVENUE_EXPRESSION,
)

from charts import (
    monthly_sales_chart,
    product_revenue_chart,
    sales_channel_chart,
    store_type_chart,
    render_chart,
)


sales_bp = Blueprint("sales", __name__)


@sales_bp.route("/sales")
def sales_analytics():

    engine = current_app.extensions["db_engine"]
    validate_sales_date_range = current_app.extensions[
        "validate_sales_date_range"
    ]

    # ----------------------------------------------
    # READ SELECTED FILTERS
    # ----------------------------------------------

    start_date = request.args.get("start_date") or None
    end_date = request.args.get("end_date") or None
    selected_state = request.args.get("state") or None
    selected_city = request.args.get("city") or None

    # ----------------------------------------------
    # VALIDATE DATE RANGE
    # ----------------------------------------------

    try:
        validate_sales_date_range(start_date, end_date)

    except ValueError:

        return (
            "Invalid date range. Please select valid dates.",
            400
        )

    # ----------------------------------------------
    # LOAD STATE AND CITY OPTIONS FROM DATABASE
    # ----------------------------------------------

    location_query = text("""
        SELECT DISTINCT
            state,
            city
        FROM sales
        ORDER BY state, city
    """)

    with engine.connect() as connection:

        location_results = connection.execute(
            location_query
        ).mappings().all()

    # Create state-city mapping
    city_options_by_state = {}

    for row in location_results:

        state_name = row["state"]
        city_name = row["city"]

        if state_name not in city_options_by_state:
            city_options_by_state[state_name] = []

        city_options_by_state[state_name].append(city_name)

    # Get all available states
    state_options = sorted(city_options_by_state.keys())

    # ----------------------------------------------
    # VALIDATE SELECTED STATE AND CITY
    # ----------------------------------------------

    if selected_state and selected_state not in city_options_by_state:

        return (
            "Invalid state selection.",
            400
        )

    if selected_city:

        if selected_state:

            valid_cities = city_options_by_state[selected_state]

        else:

            valid_cities = [
                city
                for cities in city_options_by_state.values()
                for city in cities
            ]

        if selected_city not in valid_cities:

            return (
                "Invalid city selection.",
                400
            )

    # ----------------------------------------------
    # SHARED PARAMETERS FOR ALL SALES QUERIES
    # ----------------------------------------------

    filter_params = {
        "start_date": start_date,
        "end_date": end_date,
        "state": selected_state,
        "city": selected_city
    }

    # ----------------------------------------------
    # COMMON FILTER CONDITIONS
    # ----------------------------------------------

    filter_conditions, filter_params = build_sales_filters(
        start_date=start_date,
        end_date=end_date,
        state=selected_state,
        city=selected_city,
    )

    # ----------------------------------------------
    # 1. KPI SUMMARY
    # ----------------------------------------------

    sales_query = text(f"""
        SELECT

            COALESCE(
                SUM(
                    {REVENUE_EXPRESSION}
                ), 0
            ) AS total_revenue,

            COUNT(DISTINCT order_id) AS total_orders,

            COALESCE(SUM(quantity), 0) AS units_sold

        FROM sales

        WHERE {filter_conditions}
    """)

    with engine.connect() as connection:

        result = connection.execute(
            sales_query,
            filter_params
        ).mappings().one()

    total_revenue = float(result["total_revenue"])
    total_orders = int(result["total_orders"])
    units_sold = int(result["units_sold"])

    average_order_value = calculate_average_order_value(
        total_revenue, total_orders
    )

    kpis = {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "units_sold": units_sold,
        "average_order_value": average_order_value
    }

    # Compare only when the user explicitly selects a complete date range.
    # The comparison window is the immediately preceding equal-length period.
    period_comparison = None

    if start_date and end_date:

        parsed_start, parsed_end = validate_sales_date_range(
            start_date, end_date
        )

        previous_start, previous_end = previous_period(
            parsed_start, parsed_end
        )

        previous_query = text(f"""
            SELECT COALESCE(SUM({REVENUE_EXPRESSION}), 0) AS revenue,
                   COUNT(DISTINCT order_id) AS orders,
                   COALESCE(SUM(quantity), 0) AS units
            FROM sales
            WHERE order_date >= :previous_start AND order_date <= :previous_end
              AND (:state IS NULL OR state = :state)
              AND (:city IS NULL OR city = :city)
        """)

        with engine.connect() as connection:

            previous_result = connection.execute(
                previous_query,
                {
                    "previous_start": previous_start,
                    "previous_end": previous_end,
                    "state": selected_state,
                    "city": selected_city,
                }
            ).mappings().one()

        period_comparison = {
            "start": previous_start.isoformat(),
            "end": previous_end.isoformat(),
            "revenue": float(previous_result["revenue"] or 0),
            "revenue_change": percentage_change(
                total_revenue,
                previous_result["revenue"]
            ),
            "orders_change": percentage_change(
                total_orders,
                previous_result["orders"]
            ),
        }

    # ----------------------------------------------
    # 2. MONTHLY SALES TREND
    # ----------------------------------------------

    monthly_query = text(f"""
        SELECT

            DATE_FORMAT(order_date, '%Y-%m') AS sales_month,

            SUM(
                {REVENUE_EXPRESSION}
            ) AS monthly_revenue

        FROM sales

        WHERE {filter_conditions}

        GROUP BY DATE_FORMAT(order_date, '%Y-%m')

        ORDER BY sales_month
    """)

    with engine.connect() as connection:

        monthly_results = connection.execute(
            monthly_query,
            filter_params
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
    # 3. SALES BY PRODUCT CATEGORY
    # ----------------------------------------------

    product_query = text(f"""
        SELECT

            product_category,

            SUM(
                {REVENUE_EXPRESSION}
            ) AS category_revenue

        FROM sales

        WHERE {filter_conditions}

        GROUP BY product_category

        ORDER BY category_revenue DESC
    """)

    with engine.connect() as connection:

        product_results = connection.execute(
            product_query,
            filter_params
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
    # 4. SALES BY SALES CHANNEL
    # ----------------------------------------------

    channel_query = text(f"""
        SELECT

            sales_channel,

            SUM(
                {REVENUE_EXPRESSION}
            ) AS channel_revenue

        FROM sales

        WHERE {filter_conditions}

        GROUP BY sales_channel

        ORDER BY channel_revenue DESC
    """)

    with engine.connect() as connection:

        channel_results = connection.execute(
            channel_query,
            filter_params
        ).mappings().all()

    channel_labels = [
        row["sales_channel"]
        for row in channel_results
    ]

    channel_revenue = [
        float(row["channel_revenue"] or 0)
        for row in channel_results
    ]

    # ----------------------------------------------
    # 5. SALES BY STORE TYPE
    # ----------------------------------------------

    store_query = text(f"""
        SELECT

            store_type,

            SUM(
                {REVENUE_EXPRESSION}
            ) AS store_revenue

        FROM sales

        WHERE {filter_conditions}

        GROUP BY store_type

        ORDER BY store_revenue DESC
    """)

    with engine.connect() as connection:

        store_results = connection.execute(
            store_query,
            filter_params
        ).mappings().all()

    store_labels = [
        row["store_type"]
        for row in store_results
    ]

    store_revenue = [
        float(row["store_revenue"] or 0)
        for row in store_results
    ]

    category_contributions = revenue_contributions(
        product_labels, product_revenue
    )

    channel_contributions = revenue_contributions(
        channel_labels, channel_revenue
    )

    top_category = (
        category_contributions[0]
        if category_contributions else None
    )

    top_channel = (
        channel_contributions[0]
        if channel_contributions else None
    )

    charts = {
        "monthly_sales": render_chart(
            monthly_sales_chart(monthly_labels, monthly_revenue),
            "salesMonthlyPlot"
        ),
        "product_sales": render_chart(
            product_revenue_chart(product_labels, product_revenue),
            "salesProductPlot"
        ),
        "channel_sales": render_chart(
            sales_channel_chart(channel_labels, channel_revenue),
            "salesChannelPlot"
        ),
        "store_sales": render_chart(
            store_type_chart(store_labels, store_revenue),
            "storeSalesPlot"
        ),
    }

    # ----------------------------------------------
    # RENDER SALES ANALYTICS PAGE
    # ----------------------------------------------

    return render_template(
        "sales.html",

        # KPI values
        kpis=kpis,

        # Monthly sales
        monthly_labels=monthly_labels,
        monthly_revenue=monthly_revenue,

        # Product analytics
        product_labels=product_labels,
        product_revenue=product_revenue,

        # Sales channel
        channel_labels=channel_labels,
        channel_revenue=channel_revenue,

        # Store analytics
        store_labels=store_labels,
        store_revenue=store_revenue,

        # Location dropdown options
        state_options=state_options,
        city_options_by_state=city_options_by_state,

        # Selected filters
        selected_state=selected_state,
        selected_city=selected_city,
        period_comparison=period_comparison,
        category_contributions=category_contributions,
        channel_contributions=channel_contributions,
        top_category=top_category,
        top_channel=top_channel,
        charts=charts
    )
