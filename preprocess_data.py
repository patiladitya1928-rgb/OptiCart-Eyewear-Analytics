
from pathlib import Path
import pandas as pd

# 1. Locate the project directory
PROJECT_DIR = Path(__file__).resolve().parent

# 2. Define the original CSV file path
INPUT_FILE = PROJECT_DIR / "dataset" / "Lenskart India.csv"

# 3. Load the CSV into a Pandas DataFrame
df = pd.read_csv(INPUT_FILE)

# 4. Display dataset dimensions
print("===== DATASET INFORMATION =====")
print("Dataset loaded successfully!")
print("Total rows:", df.shape[0])
print("Total columns:", df.shape[1])

# 5. Display all column names
print("\n===== COLUMN NAMES =====")
print(df.columns.tolist())

# 6. Display the first five records
print("\n===== FIRST FIVE RECORDS =====")
print(df.head())

# 7. Display data types
print("\n===== DATA TYPES =====")
print(df.dtypes)



# Convert order_date to datetime
df["order_date"] = pd.to_datetime(
    df["order_date"],
    errors="coerce"
)

# Verify the conversion
print("\n===== DATE CONVERSION =====")
print("Data type:", df["order_date"].dtype)
print("Invalid dates:", df["order_date"].isna().sum())

print("\nFirst five dates:")
print(df["order_date"].head())

# Verify date conversion
print("\n===== DATE VALIDATION =====")

print("Date column data type:", df["order_date"].dtype)

print("Missing or invalid dates:",
      df["order_date"].isna().sum())

print("Earliest date:", df["order_date"].min())

print("Latest date:", df["order_date"].max())


# Check missing values in the dataset
print("\n===== MISSING VALUE CHECK =====")

print(df.isna().sum())



# Define the output directory for processed data
OUTPUT_DIR = PROJECT_DIR / "dataset" / "processed"

# Create the directory if it does not exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("\n===== OUTPUT DIRECTORY =====")
print("Processed data directory:", OUTPUT_DIR)
print("Directory exists:", OUTPUT_DIR.exists())



# Define the processed CSV output path
OUTPUT_FILE = OUTPUT_DIR / "Lenskart_India_processed.csv"

# Save the processed DataFrame
df.to_csv(OUTPUT_FILE, index=False)

print("\n===== DATA EXPORT =====")
print("Processed dataset saved successfully!")
print("Output file:", OUTPUT_FILE)
print("Rows exported:", len(df))
print("Columns exported:", len(df.columns))



# Verify the exported CSV
print("\n===== EXPORTED FILE VERIFICATION =====")

df_check = pd.read_csv(OUTPUT_FILE)

print("File exists:", OUTPUT_FILE.exists())
print("Rows in exported file:", df_check.shape[0])
print("Columns in exported file:", df_check.shape[1])

print("\nExported column names:")
print(df_check.columns.tolist())

print("\nFirst 5 exported records:")
print(df_check.head())



# Compare original and exported data
print("\n===== DATA INTEGRITY CHECK =====")

print("Same number of rows:", len(df) == len(df_check))
print("Same number of columns:", len(df.columns) == len(df_check.columns))
print("Same column names:", df.columns.tolist() == df_check.columns.tolist())

# Compare values after normalizing the date column
df_compare = df.copy()
df_compare["order_date"] = (
    df_compare["order_date"].dt.strftime("%Y-%m-%d")
)

print(
    "All values match:",
    df_compare.equals(df_check)
)


# Step 102: Validate maximum text lengths

print("\n===== MAXIMUM TEXT LENGTHS =====")

text_columns = [
    "order_id",
    "city",
    "state",
    "sales_channel",
    "store_type",
    "product_category",
    "payment_mode",
    "customer_gender"
]

for column in text_columns:
    max_length = df[column].astype(str).str.len().max()
    print(f"{column}: {max_length}")


# Step 104: Validate numeric column ranges

print("\n===== NUMERIC COLUMN RANGES =====")

numeric_columns = [
    "quantity",
    "unit_price",
    "discount_percent",
    "net_sales_amount",
    "customer_age"
]

for column in numeric_columns:
    print(f"\n{column}")
    print("Minimum:", df[column].min())
    print("Maximum:", df[column].max())