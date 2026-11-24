import pytest
from sqlalchemy.exc import OperationalError

import app as app_module


@pytest.fixture()
def client():
    app_module.app.config.update(TESTING=True)
    with app_module.app.test_client() as test_client:
        yield test_client


def test_average_order_value_with_orders():
    assert app_module.calculate_average_order_value(1200, 3) == 400.0


def test_average_order_value_without_orders():
    assert app_module.calculate_average_order_value(0, 0) == 0.0


def test_average_order_value_handles_numeric_strings():
    assert app_module.calculate_average_order_value("99.90", "2") == 49.95


@pytest.mark.parametrize(
    "start_date,end_date",
    [
        ("2026-01-01", "2026-01-31"),
        (None, "2026-01-31"),
        ("2026-01-01", None),
        (None, None),
    ],
)
def test_valid_optional_date_ranges(start_date, end_date):
    app_module.validate_sales_date_range(start_date, end_date)


@pytest.mark.parametrize(
    "start_date,end_date",
    [
        ("not-a-date", "2026-01-31"),
        ("2026-02-30", None),
        ("2026-02-01", "2026-01-31"),
    ],
)
def test_invalid_date_ranges_raise_value_error(start_date, end_date):
    with pytest.raises(ValueError):
        app_module.validate_sales_date_range(start_date, end_date)


def test_sales_route_rejects_invalid_date_without_database_access(client):
    response = client.get("/sales?start_date=not-a-date")
    assert response.status_code == 400
    assert b"Invalid date range" in response.data


def test_sales_route_rejects_reversed_date_range_without_database_access(client):
    response = client.get("/sales?start_date=2026-02-01&end_date=2026-01-01")
    assert response.status_code == 400
    assert b"Invalid date range" in response.data


def test_database_error_returns_safe_service_unavailable_page(client, monkeypatch):
    def fail_connect():
        raise OperationalError("SELECT 1", {}, Exception("database offline"))

    monkeypatch.setattr(app_module.engine, "connect", fail_connect)
    response = client.get("/")

    assert response.status_code == 503
    assert b"Dashboard temporarily unavailable" in response.data
    assert b"database offline" not in response.data

def test_dashboard_renders_successfully(client, monkeypatch):
    query_results = [
        {
            "total_net_sales": 10000.0,
            "total_orders": 5,
            "units_sold": 12,
        },
        [
            {"sales_month": "2026-01", "monthly_revenue": 5000.0},
            {"sales_month": "2026-02", "monthly_revenue": 5000.0},
        ],
        [
            {"product_category": "Frames", "category_revenue": 6000.0},
            {"product_category": "Lenses", "category_revenue": 4000.0},
        ],
        [
            {"state": "Karnataka", "state_revenue": 7000.0},
            {"state": "Maharashtra", "state_revenue": 3000.0},
        ],
        [
            {"customer_gender": "Female", "total_orders": 3},
            {"customer_gender": "Male", "total_orders": 2},
        ],
        [
            {"age_group": "20-29", "total_customers": 2},
            {"age_group": "30-39", "total_customers": 3},
        ],
    ]

    class FakeResult:
        def __init__(self, data):
            self.data = data

        def mappings(self):
            return self

        def one(self):
            return self.data

        def all(self):
            return self.data

    class FakeConnection:
        def execute(self, query):
            return FakeResult(query_results.pop(0))

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

    monkeypatch.setattr(
        app_module.engine,
        "connect",
        lambda: FakeConnection(),
    )

    response = client.get("/")

    assert response.status_code == 200
    assert b"Total Net Sales" in response.data
    assert b"10,000.00" in response.data
    assert b"Average Order Value" in response.data
    assert b"2,000.00" in response.data
    assert b"Monthly Sales Trend" in response.data
    assert b"Product Analytics" in response.data
    assert b"Regional Analytics" in response.data
    assert b"Sales-record Demographics" in response.data
    assert len(query_results) == 0