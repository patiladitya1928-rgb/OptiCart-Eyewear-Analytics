
import logging
import pandas as pd
from sqlalchemy import create_engine, text
from config import Config


logger = logging.getLogger(__name__)

CSV_PATH = "dataset/processed/Lenskart_India_processed.csv"


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


NUMERIC_COLUMNS = {
    "quantity",
    "unit_price",
    "discount_percent",
    "customer_age",
}


def normalize_value(column, value):
    """Normalize values before comparing CSV and MySQL records."""

    if pd.isna(value):
        return None

    if column == "order_id":
        return str(value).strip()

    if column == "order_date":
        return pd.Timestamp(value).date().isoformat()

    if column == "unit_price":
        return f"{float(value):.2f}"

    if column in NUMERIC_COLUMNS:
        number = float(value)
        return int(number) if number.is_integer() else number

    return str(value).strip()


def compare_csv_with_database(engine_override=None):

    owns_engine = engine_override is None
    engine = engine_override

    try:
        if engine is None:
            engine = create_engine(
                Config.SQLALCHEMY_DATABASE_URI,
                pool_pre_ping=True,
            )

        print("Reading CSV...")

        df = pd.read_csv(
            CSV_PATH,
            dtype={"order_id": "string"},
        )

        # Preserve the original CSV row count.
        original_csv_rows = len(df)

        # Normalize column names.
        df.columns = [
            str(col).strip().lower()
            for col in df.columns
        ]

        # Check duplicate column names.
        if len(df.columns) != len(set(df.columns)):
            raise ValueError(
                "Duplicate column names after normalization."
            )

        # Check required columns.
        missing_columns = [
            column
            for column in REQUIRED_COLUMNS
            if column not in df.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Missing required columns: {missing_columns}"
            )

        # Select required columns.
        df = df[REQUIRED_COLUMNS].copy()

        df["order_id"] = df["order_id"].str.strip()

        # Check blank order IDs.
        if (
            df["order_id"].isna().any()
            or df["order_id"].eq("").any()
        ):
            raise ValueError(
                "Blank order IDs found. Run validation first."
            )

        # Identify repeated order IDs.
        repeated_ids = df.loc[
            df["order_id"].duplicated(keep=False),
            "order_id",
        ].unique()

        if len(repeated_ids) > 0:

            print(
                f"WARNING: Found {len(repeated_ids):,} "
                "repeated order IDs in the CSV."
            )

            print(
                "Repeated IDs will be excluded from "
                "database comparison."
            )

            # Exclude every row belonging to repeated IDs.
            df = df.loc[
                ~df["order_id"].isin(repeated_ids)
            ].copy()

        print("Checking existing MySQL records...")

        # Count existing rows, then fetch only IDs present in this CSV.
        # This avoids loading the entire sales table into application memory.
        existing_by_id = {}
        incoming_ids = df["order_id"].dropna().astype(str).unique().tolist()
        select_columns = ", ".join(REQUIRED_COLUMNS)
        batch_size = 500

        with engine.connect() as connection:
            existing_count = connection.execute(
                text("SELECT COUNT(*) FROM sales")
            ).scalar_one()

            for offset in range(0, len(incoming_ids), batch_size):
                batch = incoming_ids[offset:offset + batch_size]
                bind_names = {f"id_{i}": value for i, value in enumerate(batch)}
                placeholders = ", ".join(f":{name}" for name in bind_names)
                result = connection.execute(
                    text(f"SELECT {select_columns} FROM sales WHERE order_id IN ({placeholders})"),
                    bind_names,
                )
                for record in result.mappings():
                    existing_by_id[str(record["order_id"]).strip()] = record

        # Comparison result collections.
        new_ids = []
        exact_duplicate_ids = []
        conflict_details = []

        # Compare incoming CSV records with MySQL.
        for _, row in df.iterrows():

            order_id = row["order_id"]

            # Record does not exist in MySQL.
            if order_id not in existing_by_id:
                new_ids.append(order_id)
                continue

            stored = existing_by_id[order_id]

            differing_fields = []

            # Compare all required columns.
            for column in REQUIRED_COLUMNS:

                incoming_value = normalize_value(
                    column,
                    row[column],
                )

                stored_value = normalize_value(
                    column,
                    stored[column],
                )

                if incoming_value != stored_value:

                    differing_fields.append({
                        "field": column,
                        "stored_value": stored_value,
                        "incoming_value": incoming_value,
                    })

            # Classify matching records.
            if not differing_fields:

                exact_duplicate_ids.append(order_id)

            else:

                conflict_details.append({
                    "order_id": order_id,
                    "differing_fields": differing_fields,
                })

        # Print comparison summary.
        print("\n--- Full Record Comparison Preview ---")

        print(f"CSV rows: {original_csv_rows:,}")
        print(f"Compared rows: {len(df):,}")
        print(f"Existing MySQL rows: {existing_count:,}")
        print(f"Repeated IDs: {len(repeated_ids):,}")
        print(f"New records: {len(new_ids):,}")
        print(
            f"Exact existing duplicates: "
            f"{len(exact_duplicate_ids):,}"
        )
        print(
            f"Data conflicts: {len(conflict_details):,}"
        )

        # Display first five new records.
        if new_ids:

            print("\nFirst 5 new records:")

            print(
                df[df["order_id"].isin(new_ids)]
                .head()
                .to_string(index=False)
            )

        # Display first five conflicts.
        if conflict_details:

            print("\nFirst 5 data conflicts:")

            for conflict in conflict_details[:5]:

                print(
                    f"\nOrder ID: {conflict['order_id']}"
                )

                for difference in conflict["differing_fields"]:

                    print(
                        f"  {difference['field']}: "
                        f"stored={difference['stored_value']!r}, "
                        f"incoming={difference['incoming_value']!r}"
                    )

        print("\nComparison complete.")
        print(
            "No database records were inserted, "
            "updated, or deleted."
        )

        # Return comparison results.
        return {
            "comparison_failed": False,
            "error_message": None,

            "csv_rows": original_csv_rows,
            "compared_rows": len(df),

            "repeated_ids": repeated_ids.tolist(),
            "repeated_id_count": len(repeated_ids),

            "existing_rows": existing_count,

            "new_records": len(new_ids),
            "exact_duplicates": len(exact_duplicate_ids),
            "data_conflicts": len(conflict_details),

            "new_ids": new_ids,
            "exact_duplicate_ids": exact_duplicate_ids,
            "conflict_details": conflict_details,
        }

    except Exception:

        logger.exception("CSV/database comparison failed")

        return {
            "comparison_failed": True,
            "error_message": "The database comparison could not be completed. Check the application log and try again.",

            "csv_rows": 0,
            "compared_rows": 0,

            "repeated_ids": [],
            "repeated_id_count": 0,

            "existing_rows": 0,

            "new_records": 0,
            "exact_duplicates": 0,
            "data_conflicts": 0,

            "new_ids": [],
            "exact_duplicate_ids": [],
            "conflict_details": [],
        }

    finally:

        if owns_engine and engine is not None:
            engine.dispose()


# Run comparison directly.
if __name__ == "__main__":

    results = compare_csv_with_database()

    if results is not None:

        print("\n--- Returned Results ---")

        if results["comparison_failed"]:

            print("Comparison failed:")
            print(results["error_message"])

        else:

            print("CSV rows:", results["csv_rows"])
            print("Compared rows:", results["compared_rows"])

            print(
                "Repeated ID count:",
                results["repeated_id_count"],
            )

            print(
                "Repeated IDs:",
                results["repeated_ids"][:10],
            )

            print("New records:", results["new_records"])

            print(
                "Exact duplicates:",
                results["exact_duplicates"],
            )

            print(
                "Data conflicts:",
                results["data_conflicts"],
            )
