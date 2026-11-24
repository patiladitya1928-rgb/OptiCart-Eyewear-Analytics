"""Pure sales metric helpers used by dashboard and sales routes."""

from datetime import date, timedelta


def previous_period(start: date, end: date):
    """Return the immediately preceding period with the same inclusive length."""
    days = (end - start).days + 1
    previous_end = start - timedelta(days=1)
    return previous_end - timedelta(days=days - 1), previous_end


def percentage_change(current, previous):
    """Return percentage change; None when a zero baseline makes it undefined."""
    current, previous = float(current or 0), float(previous or 0)

    if previous == 0:
        return 0.0 if current == 0 else None

    return ((current - previous) / abs(previous)) * 100.0


def revenue_contributions(labels, values):
    """Build sorted contribution rows from already-aggregated revenue values."""
    rows = [
        (str(label or "Unknown"), float(value or 0))
        for label, value in zip(labels, values)
    ]

    total = sum(value for _, value in rows)
    rows.sort(key=lambda item: item[1], reverse=True)

    return [
        {
            "label": label,
            "revenue": value,
            "share": (value / total * 100.0) if total else 0.0,
        }
        for label, value in rows
    ]


def calculate_average_order_value(total_revenue, total_orders):
    """Return average revenue per order, safely handling an empty dataset."""
    return float(total_revenue) / int(total_orders) if total_orders else 0.0