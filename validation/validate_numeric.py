
import pandas as pd
from pathlib import Path

CSV_PATH = Path("dataset/processed/Lenskart_India_processed.csv")

df = pd.read_csv(CSV_PATH)

# Fields that must contain whole numbers
INTEGER_FIELDS = {
    "quantity": (1, None),
    "discount_percent": (0, 100),
    "customer_age": (18, 120),
}

# Fields that must contain positive decimal numbers
DECIMAL_FIELDS = {
    "unit_price": (0, None),
}


def check_numeric_field(series, field_name, minimum, maximum=None,
                        whole_number=False):
    text_values = series.astype("string").str.strip()

    missing = text_values.isna() | text_values.eq("")
    numeric_values = pd.to_numeric(text_values, errors="coerce")

    invalid_format = ~missing & numeric_values.isna()

    if whole_number:
        invalid_format = invalid_format | (
            numeric_values.notna()
            & (numeric_values % 1 != 0)
        )

    invalid_rule = numeric_values.notna() & (numeric_values < minimum)

    if maximum is not None:
        invalid_rule = invalid_rule | (
            numeric_values.notna() & (numeric_values > maximum)
        )

    # Don't count malformed or missing values as business-rule errors.
    invalid_rule = invalid_rule & ~missing & ~invalid_format

    print(f"\n{field_name}")
    print(f"  Missing values: {int(missing.sum())}")
    print(f"  Invalid numeric formats: {int(invalid_format.sum())}")
    print(f"  Business-rule violations: {int(invalid_rule.sum())}")


def main():
    print("Checking numeric fields...")

    for field, (minimum, maximum) in INTEGER_FIELDS.items():
        check_numeric_field(
            df[field],
            field,
            minimum,
            maximum,
            whole_number=True,
        )

    for field, (minimum, maximum) in DECIMAL_FIELDS.items():
        check_numeric_field(
            df[field],
            field,
            minimum,
            maximum,
            whole_number=False,
        )

    print("\nNumeric validation test complete.")
    print("No CSV or database records were changed.")


if __name__ == "__main__":
    main()
