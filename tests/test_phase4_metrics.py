from datetime import date
from analytics import previous_period, percentage_change, revenue_contributions
from repositories.sales_repository import build_sales_filters


def test_previous_period_has_same_inclusive_length():
    assert previous_period(date(2026, 3, 1), date(2026, 3, 31)) == (date(2026, 1, 29), date(2026, 2, 28))


def test_percentage_change_handles_zero_baseline():
    assert percentage_change(0, 0) == 0.0
    assert percentage_change(10, 0) is None
    assert percentage_change(120, 100) == 20.0


def test_revenue_contributions_sorted_and_calculated():
    rows = revenue_contributions(["A", "B"], [25, 75])
    assert rows[0]["label"] == "B"
    assert rows[0]["share"] == 75.0


def test_filter_builder_omits_unselected_filters():
    where, params = build_sales_filters(start_date="2026-01-01", state="Karnataka")
    assert where == "order_date >= :start_date AND state = :state"
    assert params == {"start_date": "2026-01-01", "state": "Karnataka"}


def test_filter_builder_includes_all_selected_filters():
    where, params = build_sales_filters(
        start_date="2026-01-01",
        end_date="2026-01-31",
        state="Karnataka",
        city="Bengaluru",
    )

    assert where == (
        "order_date >= :start_date AND "
        "order_date <= :end_date AND "
        "state = :state AND "
        "city = :city"
    )

    assert params == {
        "start_date": "2026-01-01",
        "end_date": "2026-01-31",
        "state": "Karnataka",
        "city": "Bengaluru",
    }


def test_filter_builder_returns_true_condition_when_no_filters():
    where, params = build_sales_filters()

    assert where == "1=1"
    assert params == {}