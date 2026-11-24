import hashlib
import json
import sys
import pandas as pd

from pathlib import Path
from sqlalchemy import create_engine, text

from compare_database import compare_csv_with_database
from config import Config


BASE_DIR = Path(__file__).resolve().parent

CSV_PATH = BASE_DIR / "dataset" / "processed" / "Lenskart_India_processed.csv"
REPORTS_DIR = BASE_DIR / "reports"
MANIFEST_PATH = REPORTS_DIR / "validation_manifest.json"

def calculate_sha256(file_path):

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def verify_validation_manifest(preview_path):

    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(
            f"Validation manifest not found: {MANIFEST_PATH}"
        )

    with open(MANIFEST_PATH, "r", encoding="utf-8") as file:
        manifest = json.load(file)

    if manifest.get("csv_file") != CSV_PATH.name:
        raise ValueError("Manifest CSV filename does not match.")

    if manifest.get("preview_file") != preview_path.name:
        raise ValueError("Preview report does not match the manifest.")

    actual_csv_hash = calculate_sha256(CSV_PATH)
    actual_preview_hash = calculate_sha256(preview_path)

    if actual_csv_hash != manifest.get("csv_sha256"):
        raise ValueError("Processed CSV integrity verification failed.")

    if actual_preview_hash != manifest.get("preview_sha256"):
        raise ValueError("Preview report integrity verification failed.")

    print("\n========== FILE INTEGRITY VERIFICATION ==========")
    print("Processed CSV: VERIFIED")
    print("Preview report: VERIFIED")
    print("SHA-256 verification successful.")

    return manifest

BATCH_SIZE = 1000

DB_COLUMNS = [
    "order_id",
    "order_date",
    "city",
    "state",
    "sales_channel",
    "store_type",
    "product_category",
    "quantity",
    "unit_price",
    "discount_percent",
    "payment_mode",
    "customer_gender",
    "customer_age",
]

INSERT_SQL = text("""
    INSERT INTO sales (
        order_id, order_date, city, state, sales_channel,
        store_type, product_category, quantity, unit_price,
        discount_percent, payment_mode, customer_gender, customer_age
    )
    VALUES (
        :order_id, :order_date, :city, :state, :sales_channel,
        :store_type, :product_category, :quantity, :unit_price,
        :discount_percent, :payment_mode, :customer_gender, :customer_age
    )
""")


def get_latest_preview_report():
    reports = sorted(
        REPORTS_DIR.glob("preview_*.csv"),
        key=lambda path: path.stat().st_mtime,
        reverse=True
    )

    if not reports:
        raise FileNotFoundError("No validation preview report found.")

    return reports[0]


def load_eligible_records():

    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Processed CSV not found: {CSV_PATH}")

    preview_path = get_latest_preview_report()

    manifest = verify_validation_manifest(preview_path)

    if len(pd.read_csv(CSV_PATH)) != manifest.get("total_rows"):
        raise ValueError("CSV row count does not match manifest.")

    if manifest.get("valid_candidates") != 150000:
        raise ValueError("Unexpected valid candidate count in manifest.")

    print("Processed CSV:", CSV_PATH.name)
    print("Validation report:", preview_path.name)

    csv_df = pd.read_csv(
        CSV_PATH,
        dtype={"order_id": "string"}
    )

    preview_df = pd.read_csv(
        preview_path,
        dtype={"order_id": "string"}
    )

    csv_df.columns = csv_df.columns.str.strip().str.lower()
    preview_df.columns = preview_df.columns.str.strip().str.lower()

    required_report_columns = {"order_id", "preview_status"}

    if not required_report_columns.issubset(preview_df.columns):
        raise ValueError(
            "Validation report must contain order_id and preview_status."
        )

    missing_columns = [
        column for column in DB_COLUMNS
        if column not in csv_df.columns
    ]

    if missing_columns:
        raise ValueError(f"CSV is missing database columns: {missing_columns}")

    csv_df = csv_df[DB_COLUMNS].copy()

    csv_df["order_id"] = csv_df["order_id"].str.strip()
    preview_df["order_id"] = preview_df["order_id"].str.strip()

    if csv_df["order_id"].isna().any() or csv_df["order_id"].eq("").any():
        raise ValueError("Blank order IDs found in CSV.")

    if len(csv_df) != len(preview_df):
        raise ValueError("CSV and validation report row counts do not match.")

    if set(csv_df["order_id"]) != set(preview_df["order_id"]):
        raise ValueError("CSV and validation report order IDs do not match.")

    if preview_df["order_id"].duplicated().any():
        raise ValueError("Duplicate order IDs found in validation report.")

    valid_ids = set(
        preview_df.loc[
            preview_df["preview_status"].eq("Valid candidate"),
            "order_id"
        ]
    )

    # Verify CSV row count against the manifest.
    if len(csv_df) != manifest.get("total_rows"):
        raise ValueError(
            "CSV row count does not match validation manifest."
        )

    # Verify valid candidate count against the manifest.
    if len(valid_ids) != manifest.get("valid_candidates"):
        raise ValueError(
            "Valid candidate count does not match validation manifest."
        )

    print("\nManifest row-count verification: PASSED")
    print("Manifest valid-candidate verification: PASSED")

    print("\nValid candidates:", len(valid_ids))

    print("\nComparing records with MySQL...")

    comparison = compare_csv_with_database()

    if comparison is None or comparison.get("comparison_failed"):
        error = (
            comparison.get("error_message")
            if comparison else "Comparison returned no results."
        )
        raise RuntimeError(f"Database comparison failed: {error}")

    new_ids = set(comparison["new_ids"])

    eligible_ids = valid_ids.intersection(new_ids)

    eligible_df = csv_df[
        csv_df["order_id"].isin(eligible_ids)
    ].copy()

    # Preserve the original CSV order.
    eligible_df = eligible_df.reset_index(drop=True)

    print("\n========== IMPORT SUMMARY ==========")
    print("Total CSV records:", len(csv_df))
    print("Valid candidates:", len(valid_ids))
    print("New database records:", len(new_ids))
    print("Eligible for import:", len(eligible_df))
    print("Exact duplicates:", comparison["exact_duplicates"])
    print("Data conflicts:", comparison["data_conflicts"])
    print("Repeated IDs excluded:", comparison["repeated_id_count"])

    return eligible_df


def convert_records_for_mysql(dataframe):

    dataframe = dataframe.copy()

    dataframe["order_date"] = pd.to_datetime(
        dataframe["order_date"],
        errors="raise"
    ).dt.date

    integer_columns = [
        "quantity",
        "discount_percent",
        "customer_age",
    ]

    for column in integer_columns:
        dataframe[column] = dataframe[column].astype(int)

    dataframe["unit_price"] = dataframe["unit_price"].astype(float)

    return dataframe.to_dict(orient="records")


def insert_records(records):

    engine = create_engine(
        Config.SQLALCHEMY_DATABASE_URI,
        pool_pre_ping=True
    )

    inserted_count = 0

    try:
        # One transaction for the complete import.
        # Any error causes the entire transaction to roll back.
        with engine.begin() as connection:

            for start in range(0, len(records), BATCH_SIZE):

                batch = records[start:start + BATCH_SIZE]

                connection.execute(INSERT_SQL, batch)

                inserted_count += len(batch)

                print(
                    f"Inserted within transaction: "
                    f"{inserted_count:,}/{len(records):,}"
                )

        # Reaching here means the transaction committed successfully.
        print("\nTransaction committed successfully.")

        return inserted_count

    finally:
        engine.dispose()


def verify_import(expected_count):

    engine = create_engine(
        Config.SQLALCHEMY_DATABASE_URI,
        pool_pre_ping=True
    )

    try:
        with engine.connect() as connection:

            actual_count = connection.execute(
                text("SELECT COUNT(*) FROM sales")
            ).scalar_one()

        print("\n========== DATABASE VERIFICATION ==========")
        print("Expected inserted records:", expected_count)
        print("Total records currently in sales table:", actual_count)

        if actual_count != expected_count:
            print("WARNING: Database count differs from expected count.")
        else:
            print("Verification successful.")

    finally:
        engine.dispose()


def main():

    execute_mode = "--execute" in sys.argv

    print("\n========== VISIONTRACK IMPORT PROCESS ==========")

    eligible_df = load_eligible_records()

    if eligible_df.empty:
        print("\nNo eligible records found. Nothing to import.")
        return

    print("\nFirst 5 eligible order IDs:")
    print(eligible_df["order_id"].head().to_string(index=False))

    if not execute_mode:
        print("\nDRY RUN COMPLETE.")
        print("No database records were inserted or modified.")
        print("Use --execute only when you are ready to import.")
        return

    print("\nEXECUTION MODE ENABLED.")

    records = convert_records_for_mysql(eligible_df)

    inserted_count = insert_records(records)

    print("\nRecords inserted successfully:", inserted_count)

    verify_import(inserted_count)


if __name__ == "__main__":

    try:
        main()

    except Exception as error:
        print("\nIMPORT PROCESS FAILED.")
        print("Error:", error)
        print("If insertion failed during the transaction, it was rolled back.")
