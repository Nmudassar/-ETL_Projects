Below is the **clean, rewritten, final README.md** with **all “customers” dataset sections removed**, rewritten professionally and structured for a real project.

---

# 📘 ETL Project: S3 → Airbyte → MotherDuck

### End-to-End Retail Data Ingestion Pipeline

This project demonstrates a complete ETL workflow that:

1. **Ingests datasets** (sales and products)
2. **Uploads data to AWS S3** in a structured, versioned layout
3. **Uses Airbyte Cloud** to extract new files daily
4. **Loads datasets into MotherDuck** as the cloud data warehouse
5. **Validates data quality**, completeness, and schema correctness

This README includes **AWS setup, Python ETL, Airbyte connections, warehouse configuration, and validation logic**.

---

# 🧱 Project Structure

```
ETL_Projects/
│
└── retail-elt/
    ├── data/                 # sales.csv, products.csv
    ├── myenv/                # Python virtual environment
    ├── src/                  # Python upload scripts
    │   └── extract.py
    ├── .env                  # AWS credentials
    ├── .gitignore
    ├── README.md
    └── requirements.txt
```

---

# 📦 Project Scope & Deliverables

## **1. Data Simulation & Upload to AWS S3**

### Datasets Provided

* `sales.csv`
* `products.csv`
  Each includes **10,000+ records**.

### Upload Requirements

✔ Upload datasets to **AWS S3** using Python (boto3 + awswrangler)
✔ Structured raw zone layout:

```
s3://retail-elt-bucket/raw/sales/
s3://retail-elt-bucket/raw/products/
```

✔ Enable:

* **Bucket Versioning**
* **Lifecycle Policies** (e.g., delete old versions after 30 days)

---

## **2. Airbyte Cloud Configuration**

### Source: AWS S3

* Connector: **S3 (CSV/Parquet)**
* Configure:

  * Bucket name: `retail-elt-bucket`
  * Region: `eu-central-1`
  * Path prefix: `raw/`
  * Pattern: `*.csv` or `*.parquet`
* Setup a **daily scheduled sync**

### Destination: MotherDuck

* Authenticate using **MotherDuck token**
* Set default target schema: `retail_data`
* Ensure **schema evolution** is enabled (optional)
* Load results into **staging tables**

Airbyte will create:

* `retail_data.sales`
* `retail_data.products`

---

## **3. MotherDuck Warehouse Setup**

1. Connect to MotherDuck
2. Create schema:

```sql
CREATE SCHEMA IF NOT EXISTS retail_data;
```

3. Run first sync in Airbyte
4. Verify tables:

```sql
SHOW TABLES IN retail_data;
```

5. Inspect schema:

```sql
DESCRIBE retail_data.sales;
DESCRIBE retail_data.products;
```

---

# 🧪 Data Validation & Quality Checks

### **1. Record Count Matching**

```sql
SELECT COUNT(*) FROM retail_data.sales;
```

Compare to row count in original CSV.

### **2. Null & Missing Value Checks**

```sql
SELECT *
FROM retail_data.sales
WHERE order_id IS NULL OR quantity IS NULL;
```

### **3. Schema Consistency Checks**

* All expected columns exist
* Data types match source
* Timestamps correctly parsed

### **4. Data Profiling**

```sql
SELECT 
    MIN(quantity) AS min_qty,
    MAX(quantity) AS max_qty,
    AVG(quantity) AS avg_qty
FROM retail_data.sales;
```

### **5. Analytical Queries**

Example: Daily sales summary

```sql
SELECT order_date, SUM(total_price) AS total_sales
FROM retail_data.sales
GROUP BY order_date
ORDER BY order_date;
```

---

# ⚙️ Local Setup (Python ETL)

## Step 1: Create Project Directory

```bash
mkdir retail-elt
cd retail-elt
mkdir data src
```

## Step 2: Virtual Environment

```bash
python3 -m venv myenv
source myenv/bin/activate     # macOS/Linux
myenv\Scripts\activate        # Windows
```

## Step 3: Install Dependencies

`requirements.txt`:

```
boto3
awswrangler
pandas
python-dotenv
chardet
```

Install:

```bash
pip install -r requirements.txt
```

---

# 🔐 AWS Setup

### IAM User

* Programmatic access enabled
* Policy: **AmazonS3FullAccess** (or least-privilege custom)

### S3 Bucket

* Create: `retail-elt-bucket`
* Enable:
  ✔ Versioning
  ✔ Default encryption
  ✔ Lifecycle rules

---

# 🧑‍💻 Python Script (Upload CSV → S3 as Parquet)

**File: `src/extract.py`**

```python
import os
import boto3
import pandas as pd
import awswrangler as wr
import chardet
from dotenv import load_dotenv

load_dotenv()

access = os.getenv("ACCESS_KEY")
secret = os.getenv("SECRET_KEY")
region = os.getenv("REGION")
bucket = "retail-elt-bucket"

session = boto3.Session(
    aws_access_key_id=access,
    aws_secret_access_key=secret,
    region_name=region
)

datasets = {
    "products": "data/products.csv",
    "sales": "data/sales.csv"
}

for name, path in datasets.items():
    if os.path.exists(path):
        print(f"\nProcessing {name} dataset ...")

        with open(path, 'rb') as file:
            detected = chardet.detect(file.read())['encoding']

        df = pd.read_csv(path, encoding=detected or "utf-8")

        wr.s3.to_parquet(
            df=df,
            path=f"s3://{bucket}/raw/{name}/",
            dataset=True,
            mode="overwrite",
            index=False,
            boto3_session=session
        )

        print(f"✔ Uploaded: s3://{bucket}/raw/{name}/")
    else:
        print(f"⚠ Missing file: {path}")
```

---

# 🚨 Troubleshooting & Common Errors

| Issue                | Cause                   | Fix                            |
| -------------------- | ----------------------- | ------------------------------ |
| `NoCredentialsError` | `.env` missing keys     | Add ACCESS_KEY & SECRET_KEY    |
| `AccessDenied`       | IAM policy insufficient | Attach S3FullAccess            |
| `FileNotFoundError`  | Wrong file path         | Confirm files exist in `/data` |
| Encoding issues      | Non-UTF8 CSV            | Auto-detection via `chardet`   |
| Airbyte mismatch     | Type inference changes  | Enable schema evolution        |

---

# 🧠 Best Practices

* Never commit credentials
* Use Parquet for all raw storage
* Enforce folder naming conventions
* Monitor Airbyte logs for failed syncs
* Validate data after each load

---

# 🏁 Completion Checklist

✔ Datasets prepared
✔ Uploaded to S3 with versioning
✔ Airbyte S3 → MotherDuck connection configured
✔ Daily sync enabled
✔ Tables created in `retail_data` schema
✔ Data validated (counts, nulls, schema)
✔ Analytical queries executed successfully

---

# 🎯 Summary

This project implements a full **production-style ETL pipeline**:

**Local CSV → AWS S3 → Airbyte Cloud → MotherDuck Warehouse → Data Validation & Analytics**

It provides:

* Reliable ingestion
* Automated recurring syncs
* Versioned cloud storage
* Structured warehouse tables
* Validation for trustworthy analytics

---

If you'd like, I can also generate:

📌 A full **diagram** of the architecture
📌 A **Terraform file** for S3 + IAM setup
📌 An **Airbyte connection JSON template**
📌 A **MotherDuck SQL validation script pack**

Just let me know!
