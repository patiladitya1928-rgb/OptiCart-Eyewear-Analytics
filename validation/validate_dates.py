
import pandas as pd
from pathlib import Path
from datetime import date

CSV_PATH = Path("dataset/processed/Lenskart_India_processed.csv")


def main():
    df = pd.read_csv(CSV_PATH, dtype={"order_date": "string"})

    raw_dates = df["order_date"].str.strip()

    # Require exactly YYYY-MM-DD and a valid calendar date.
    format_matches = raw_dates.str.fullmatch(
        r"\d{4}-\d{2}-\d{2}",
        na=False,
    )

    parsed_dates = pd.to_datetime(
        raw_dates.where(format_matches),
        format="%Y-%m-%d",
        errors="coerce",
    )

    missing = raw_dates.isna() | raw_dates.eq("")
    invalid_dates = ~missing & (
        ~format_matches | parsed_dates.isna()
    )

    today = pd.Timestamp(date.today())
    future_dates = parsed_dates.notna() & (parsed_dates > today)

    print("Date validation results")
    print("-----------------------")
    print(f"Total rows: {len(df):,}")
    print(f"Missing dates: {int(missing.sum())}")
    print(f"Invalid date formats or dates: {int(invalid_dates.sum())}")
    print(f"Future-date warnings: {int(future_dates.sum())}")

    if invalid_dates.any():
        print("\nExamples of invalid dates:")
        print(df.loc[invalid_dates, ["order_id", "order_date"]].head(10))

    if future_dates.any():
        print("\nExamples of future dates:")
        print(
            df.loc[future_dates, ["order_id", "order_date"]]
            .head(10)
        )

    print("\nDate validation test complete.")
    print("No CSV or database records were changed.")


if __name__ == "__main__":
    main()

