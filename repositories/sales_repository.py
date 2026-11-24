"""Shared SQL fragments and database access helpers for sales reporting."""

REVENUE_EXPRESSION = "quantity * unit_price * (100 - discount_percent) / 100.0"


def build_sales_filters(start_date=None, end_date=None, state=None, city=None):
    clauses = []
    params = {}

    filter_mapping = [
        ("start_date", start_date, "order_date", ">="),
        ("end_date", end_date, "order_date", "<="),
        ("state", state, "state", "="),
        ("city", city, "city", "="),
    ]

    for key, value, column, operator in filter_mapping:
        if value is not None and value != "":
            clauses.append(f"{column} {operator} :{key}")
            params[key] = value

    where_clause = " AND ".join(clauses) if clauses else "1=1"

    return where_clause, params


