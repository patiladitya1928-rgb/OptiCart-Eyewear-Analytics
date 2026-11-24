# VisionTrack — Dataset Inspection Report

## 1. Dataset Information

- **Dataset:** Lenskart India Sales and Customer Analytics Dataset
- **Source:** [Kaggle](https://www.kaggle.com/datasets/datamonkresearch/lenskart-india-sales-and-customer-analytics-dataset)
- **File:** `dataset/Lenskart India.csv`
- **Total records:** 150,000
- **Total columns:** 14
- **Date range:** 2022-01-01 to 2025-12-31

## 2. Data Quality Results

- Missing values: 0
- Duplicate rows: 0
- Duplicate order IDs: 0
- Invalid dates: 0
- Non-positive quantities: 0
- Non-positive unit prices: 0
- Non-positive net sales amounts: 0
- Discounts outside 0–100%: 0
- Customer ages less than or equal to zero: 0

## 3. Available Columns

`order_id`, `order_date`, `city`, `state`, `sales_channel`, `store_type`, `product_category`, `quantity`, `unit_price`, `discount_percent`, `net_sales_amount`, `payment_mode`, `customer_gender`, `customer_age`.

## 4. Revenue Validation

Expected net sales:

`quantity × unit_price × (1 - discount_percent / 100)`

- Records checked: 150,000
- Records matching within 0.02: 150,000
- Records with differences above 0.02: 0
- Maximum absolute difference: approximately 1.82 × 10⁻¹²

The stored net-sales values are consistent with the calculated values within the selected tolerance.

## 5. Supported Analytics

- Sales trends over time
- Sales by product category
- Regional sales by city and state
- Sales-channel and store-type comparisons
- Payment-mode distribution
- Customer age and gender analysis
- Discount analysis


## 6. Numeric Range and Date Distribution

- Quantity values: 1, 2, and 3.
- Discount values: 0%, 5%, 10%, 15%, 20%, and 25%.
- Customer age range: 18–64 years.
- Unit price range: ₹799–₹4,998.
- Net sales range per record: ₹599.25–₹14,994.00.

### Records by Year

| Year | Records |
|---|---:|
| 2022 | 37,306 |
| 2023 | 37,791 |
| 2024 | 37,532 |
| 2025 | 37,371 |
| **Total** | **150,000** |

These checks found no unexpected values within the numeric ranges inspected.
The business validity and provenance of the dataset still require separate verification.

## 7. Initial Data-Cleaning Decision

Based on the initial dataset inspection, no missing values,
duplicate rows, duplicate order IDs, or invalid dates were detected.

The net sales amount was validated against the formula:

Net Sales Amount = Quantity × Unit Price × (1 − Discount Percentage / 100)

All records matched the formula within the selected tolerance.

No records will be deleted, and no numeric values will be
modified at this stage. The original CSV will remain unchanged.

The order_date column will be converted to a proper datetime
type during data processing.

Dataset licensing terms have been identified. Dataset provenance and business-rule validation remain pending.

## 8. Dataset Source and License

- **Dataset:** Lenskart India Sales and Customer Analytics Dataset
- **Platform:** Kaggle
- **Dataset URL:** https://www.kaggle.com/datasets/datamonkresearch/lenskart-india-sales-and-customer-analytics-dataset
- **License:** Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)
- **License URL:** https://creativecommons.org/licenses/by-sa/4.0/

### License Compliance

The dataset may be shared and adapted subject to the license terms.
Appropriate attribution, a link to the license, and disclosure of
changes must be provided. Adapted material covered by the license
must comply with its ShareAlike requirements.

### Provenance Note

The dataset is being used for an educational analytics project.
Its status as actual Lenskart transaction data has not been verified.