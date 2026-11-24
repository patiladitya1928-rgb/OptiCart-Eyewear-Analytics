
import pandas as pd
from pathlib import Path

CSV_PATH = Path("dataset/processed/Lenskart_India_processed.csv")

REQUIRED_COLUMNS = [
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


def normalize_column_name(column_name):
    """Trim whitespace and ignore capitalization."""
    return str(column_name).strip().lower()


def main():
    print("Reading CSV file...")

    df = pd.read_csv(CSV_PATH, dtype={"order_id": "string"})

    print(f"Rows: {len(df):,}")
    print(f"Original columns: {len(df.columns)}")

    # Normalize column names
    normalized_columns = [
        normalize_column_name(column)
        for column in df.columns
    ]

    # Detect ambiguous names, such as 'City' and ' city '
    normalized_names = pd.Series(normalized_columns)
    duplicate_names = normalized_names[
        normalized_names.duplicated(keep=False)
    ].unique()

    if len(duplicate_names) > 0:
        print("\nERROR: Ambiguous duplicate column names found:")
        print(list(duplicate_names))
        return

    # Apply normalized names
    df.columns = normalized_columns

    # Verify required columns
    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        print("\nERROR: Required columns are missing:")
        for column in missing_columns:
            print(f"- {column}")
        return

    print("\nColumn validation: PASSED")
    print("All required columns are present.")
    print("Column names are normalized.")

    # Identify missing values and blank text
    print("\nMissing or blank values in required columns:")

    for column in REQUIRED_COLUMNS:
        values = df[column]

        missing = values.isna()

        if pd.api.types.is_object_dtype(values) or \
                pd.api.types.is_string_dtype(values):
            missing = missing | values.astype("string").str.strip().eq("")

        count = int(missing.sum())

        if count > 0:
            print(f"{column}: {count}")
        else:
            print(f"{column}: 0")

    print("\nSample normalized column names:")
    print(df.columns.tolist())

    print("\nColumn validation test complete.")
    print("No files were modified and no database records were changed.")


if __name__ == "__main__":
    main()
