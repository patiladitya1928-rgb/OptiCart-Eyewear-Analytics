import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# --------------------------------------------------
# 1. PATH CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_PATH = BASE_DIR / "dataset" / "processed" / "Lenskart_India_processed.csv"

OUTPUT_DIR = BASE_DIR / "reports" / "preprocessing_graphs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# 2. LOAD DATASET
# --------------------------------------------------

df = pd.read_csv(DATASET_PATH)

sns.set_theme(style="whitegrid")

numeric_columns = [
    col for col in [
        "quantity",
        "unit_price",
        "discount_percent",
        "net_sales_amount",
        "customer_age"
    ]
    if col in df.columns
]

# --------------------------------------------------
# GRAPH 1: MISSING VALUES ANALYSIS
# --------------------------------------------------

plt.figure(figsize=(12, 6))

missing_values = df.isnull().sum()

sns.barplot(
    x=missing_values.index,
    y=missing_values.values
)

plt.title("Missing Values Analysis", fontsize=16)
plt.xlabel("Dataset Columns")
plt.ylabel("Number of Missing Values")
plt.xticks(rotation=45, ha="right")

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "missing_values.png", dpi=300)
plt.close()

# --------------------------------------------------
# GRAPH 2: NUMERICAL DATA DISTRIBUTION
# --------------------------------------------------

df[numeric_columns].hist(
    figsize=(14, 10),
    bins=30,
    edgecolor="black"
)

plt.suptitle(
    "Numerical Data Distribution",
    fontsize=18
)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "numerical_distribution.png", dpi=300)
plt.close()

# --------------------------------------------------
# GRAPH 3: OUTLIER DETECTION USING BOXPLOTS
# --------------------------------------------------

plt.figure(figsize=(13, 7))

sns.boxplot(
    data=df[numeric_columns],
    orient="h"
)

plt.title("Outlier Analysis of Numerical Features", fontsize=16)
plt.xlabel("Values")

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "outlier_analysis.png", dpi=300)
plt.close()

# --------------------------------------------------
# GRAPH 4: CORRELATION HEATMAP
# --------------------------------------------------

correlation = df[numeric_columns].corr()

plt.figure(figsize=(10, 7))

sns.heatmap(
    correlation,
    annot=True,
    cmap="coolwarm",
    fmt=".2f",
    linewidths=0.5
)

plt.title("Correlation Heatmap", fontsize=16)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "correlation_heatmap.png", dpi=300)
plt.close()

# --------------------------------------------------
# COMPLETION MESSAGE
# --------------------------------------------------

print("\nPreprocessing Graphs Generated Successfully!")

print(f"\nSaved Location: {OUTPUT_DIR}")

for file in OUTPUT_DIR.iterdir():
    if file.suffix == ".png":
        print(f"Generated: {file.name}")