"""Tests for the Import Preview route."""

import pytest

import app as app_module


@pytest.fixture()
def client():
    app_module.app.config.update(TESTING=True)
    with app_module.app.test_client() as test_client:
        yield test_client


def test_import_preview_renders_successfully(client, tmp_path, monkeypatch):
    import routes.import_routes as import_routes

    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()

    csv_path = tmp_path / "sales.csv"
    csv_path.write_text(
        "order_id,city,net_sales_amount\n"
        "ORD001,Pune,1500.00\n"
        "ORD002,Mumbai,2000.00\n"
        "ORD003,Nashik,2500.00\n",
        encoding="utf-8",
    )

    summary_path = reports_dir / "summary_test.csv"
    summary_path.write_text(
        "status,count\n"
        "Total rows,3\n"
        "Valid candidates,3\n"
        "Rejected,0\n"
        "Repeated IDs,0\n"
        "Needs Review,0\n",
        encoding="utf-8",
    )

    preview_path = reports_dir / "preview_test.csv"
    preview_path.write_text(
        "order_id,preview_status\n"
        "ORD001,Valid candidate\n"
        "ORD002,Valid candidate\n"
        "ORD003,Valid candidate\n",
        encoding="utf-8",
    )

    monkeypatch.setitem(
        app_module.app.config,
        "REPORTS_DIR",
        reports_dir,
    )
    monkeypatch.setitem(
        app_module.app.config,
        "CSV_PATH",
        csv_path,
    )

    monkeypatch.setattr(
        import_routes,
        "compare_csv_with_database",
        lambda engine_override=None: {
            "comparison_failed": False,
            "error_message": None,
            "csv_rows": 3,
            "compared_rows": 3,
            "existing_rows": 2,
            "new_records": 0,
            "exact_duplicates": 1,
            "data_conflicts": 1,
            "new_ids": [],
            "exact_duplicate_ids": ["ORD001"],
            "conflict_details": [
                {"order_id": "ORD002", "differing_fields": []}
            ],
            "repeated_ids": [],
            "repeated_id_count": 0,
        },
    )

    response = client.get("/import-preview")

    assert response.status_code == 200
    assert b"ORD001" in response.data
    assert b"ORD002" in response.data
    assert b"ORD003" in response.data
    assert b"Exact existing duplicate" in response.data
    assert b"Data conflict" in response.data
    assert b"Valid candidates" in response.data

def test_import_preview_displays_second_page(client, tmp_path, monkeypatch):
    import routes.import_routes as import_routes

    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()

    summary_path = reports_dir / "summary_test.csv"
    summary_path.write_text(
        "status,count\n"
        "Total rows,20\n"
        "Valid candidates,20\n"
        "Rejected,0\n"
        "Repeated IDs,0\n"
        "Needs Review,0\n",
        encoding="utf-8",
    )

    csv_path = tmp_path / "sales.csv"

    rows = ["order_id,city,net_sales_amount"]
    for number in range(1, 21):
        rows.append(f"ORD{number:03d},Pune,{number * 100}.00")

    csv_path.write_text("\n".join(rows), encoding="utf-8")

    monkeypatch.setitem(app_module.app.config, "REPORTS_DIR", reports_dir)
    monkeypatch.setitem(app_module.app.config, "CSV_PATH", csv_path)

    monkeypatch.setattr(
        import_routes,
        "compare_csv_with_database",
        lambda engine_override=None: {
            "comparison_failed": False,
            "error_message": None,
            "csv_rows": 20,
            "compared_rows": 20,
            "existing_rows": 0,
            "new_records": 20,
            "exact_duplicates": 0,
            "data_conflicts": 0,
            "new_ids": [],
            "exact_duplicate_ids": [],
            "conflict_details": [],
            "repeated_ids": [],
            "repeated_id_count": 0,
        },
    )

    response = client.get("/import-preview?page=2")

    assert response.status_code == 200
    assert b"ORD011" in response.data
    assert b"ORD020" in response.data
    assert b"ORD001" not in response.data
    assert b"ORD010" not in response.data