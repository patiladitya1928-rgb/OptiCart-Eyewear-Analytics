# 👓 OptiCart – Eyewear Sales and Customer Analytics System

**A Flask-based Business Intelligence and Sales Analytics Application**

OptiCart is a web-based sales analytics system developed as a CDAC PG-DBDA mini project. It focuses on analyzing eyewear retail sales data and presenting meaningful business insights through interactive dashboards, visualizations, and data validation.

The application uses Python, Flask, MySQL, Pandas, SQLAlchemy, and Plotly to process, manage, analyze, and visualize sales information.

---

## 📌 Project Overview

The project analyzes an eyewear retail sales dataset containing information about orders, products, customers, sales channels, locations, pricing, and discounts.

It helps users understand business performance through key performance indicators (KPIs), sales trends, product performance, regional revenue, and customer demographic analysis.

**Project Type:** Business Intelligence & Data Analytics
**Domain:** Retail / E-commerce – Eyewear Industry
**Architecture:** Flask-based Web Application
**Machine Learning:** Not used

---

## 🚀 Key Features

### 1. Overview Dashboard

- Total Revenue
- Total Orders
- Total Units Sold
- Average Order Value (AOV)
- Monthly Revenue Trends
- Product Category Revenue
- State-wise Revenue
- Customer Demographic Analysis

### 2. Sales Analytics

- Date-based filtering
- State and city filtering
- Revenue analysis
- Product category performance
- Sales channel analysis
- Store type analysis
- Previous-period revenue comparison
- Revenue contribution analysis

### 3. Data Preprocessing

- Dataset inspection
- Data type analysis
- Date conversion
- Missing value inspection
- Numerical range checks
- Processed dataset generation

### 4. Data Validation

- Column validation
- Date validation
- Numeric value validation
- Duplicate order ID detection
- Existing database record comparison
- Import validation reports

### 5. Preprocessing Visualizations

Four graphs are generated using Matplotlib and Seaborn:

- Missing Values Analysis
- Numerical Data Distribution
- Outlier Analysis
- Correlation Heatmap

Generated graphs are saved in `reports/preprocessing_graphs/`.

### 6. Import Preview

- Dataset import preview
- Validation status
- Duplicate detection
- Database comparison
- Pagination of dataset records

---

## 🛠️ Technology Stack

| Category                | Technologies          |
| ----------------------- | --------------------- |
| Backend                 | Python, Flask         |
| Database                | MySQL                 |
| Database Connectivity   | SQLAlchemy, PyMySQL   |
| Data Processing         | Pandas                |
| Data Visualization      | Plotly                |
| Preprocessing Graphs    | Matplotlib, Seaborn   |
| Frontend                | HTML, CSS, JavaScript |
| Template Engine         | Jinja2                |
| Testing                 | Pytest                |
| Development Environment | PyCharm               |

---

## 📂 Project Structure

```text
VisionTrack_Final/
│
├── app.py
├── config.py
├── extensions.py
├── analytics.py
├── charts.py
├── compare_database.py
├── preprocess_data.py
├── import_sales.py
│
├── repositories/
│   └── sales_repository.py
│
├── routes/
│   ├── dashboard_routes.py
│   ├── sales_routes.py
│   └── import_routes.py
│
├── validation/
│   ├── validate_columns.py
│   ├── validate_dates.py
│   └── validate_numeric.py
│
├── dataset/
│   ├── Lenskart India.csv
│   └── processed/
│       └── Lenskart_India_processed.csv
│
├── reports/
│   ├── DATASET_REPORT.md
│   ├── validation_manifest.json
│   ├── preprocessing_graphs.py
│   └── preprocessing_graphs/
│       ├── missing_values.png
│       ├── numerical_distribution.png
│       ├── outlier_analysis.png
│       └── correlation_heatmap.png
│
├── templates/
│   ├── index.html
│   ├── sales.html
│   ├── import_preview.html
│   └── error.html
│
├── static/
│   └── css/
│       └── style.css
│
├── tests/
│
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 📊 Dataset Information

**Dataset:** Lenskart India Sales and Customer Analytics Dataset

**Source:** Kaggle

Dataset Link: [https://www.kaggle.com/datasets/datamonkresearch/lenskart-india-sales-and-customer-analytics-dataset](https://www.kaggle.com/datasets/datamonkresearch/lenskart-india-sales-and-customer-analytics-dataset)

| Dataset Information |     Value |
| ------------------- | --------: |
| Total Records       |   150,000 |
| Total Columns       |        14 |
| Data Period         | 2022–2025 |
| Duplicate Rows      |         0 |
| Missing Values      |         0 |

### Dataset Attributes

- `order_id`
- `order_date`
- `city`
- `state`
- `sales_channel`
- `store_type`
- `product_category`
- `quantity`
- `unit_price`
- `discount_percent`
- `net_sales_amount`
- `payment_mode`
- `customer_gender`
- `customer_age`

---

## 📈 Business Metrics

The application calculates important sales metrics using SQL queries.

**Total Revenue**

```sql
SUM(quantity * unit_price * (100 - discount_percent) / 100)
```

**Total Orders**

```sql
COUNT(DISTINCT order_id)
```

**Total Units Sold**

```sql
SUM(quantity)
```

**Average Order Value**

```text
Average Order Value = Total Revenue / Total Orders
```

---

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/OptiCart-Eyewear-Analytics.git
```

### 2. Navigate to Project Directory

```bash
cd OptiCart-Eyewear-Analytics
```

### 3. Create Virtual Environment

```bash
python -m venv .venv
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the project root.

Example:

```env
SECRET_KEY=your-secret-key
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/your_database
```

Replace the database credentials and database name with your own configuration.

### 6. Database Setup

- Install and start MySQL.
- Create your database.
- Prepare the required `sales` table using the project's expected columns.
- Configure the database connection in `.env`.

**Note:** The repository does not currently include a database schema or SQL migration script. The required table must be prepared separately.

### 7. Run the Application

```bash
python app.py
```

Open your browser:

```text
http://127.0.0.1:5000/
```

---

## 🧪 Testing

The project includes automated tests for:

- Application reliability
- Analytics calculations
- Chart generation
- Database connectivity checks
- Import preview functionality
- Sales metrics

Run tests using:

```bash
pytest
```

Live MySQL integration testing is optional and requires the appropriate database configuration.

---

## 🔮 Future Enhancements

- Advanced customer segmentation
- City-level sales visualizations
- Payment mode analytics
- Discount analysis
- Automated database schema setup
- Exportable business reports
- Additional business performance metrics

---

## 🎓 Academic Project

**Course:** CDAC PG Diploma in Big Data Analytics (PG-DBDA)

**Project:** OptiCart – Eyewear Sales and Customer Analytics System

**Objective:** To develop a data-driven business intelligence application that transforms retail sales data into meaningful business insights through data processing, validation, SQL analytics, and interactive visualization.

---

## 👨‍💻 Author

**Aditya Patil**

CDAC PG-DBDA Student

GitHub: [https://github.com/patiladitya1928-rgb](https://github.com/patiladitya1928-rgb)

---

*OptiCart – Transforming Eyewear Sales Data into Business Insights.*
