# ETL Project: Upload CSV Files to AWS S3

A complete guide combining **project setup**, **AWS IAM & S3 configuration**, **virtual environment & dependencies**, and **Python upload logic** using both **boto3** and **awswrangler** for CSV-to-Parquet transformation — plus a dedicated **Error Handling & Troubleshooting** section.

---

## 📘 Overview

This project demonstrates how to ingest CSV datasets into an **AWS S3** bucket using **Python**. It uses a modular folder structure (data, source, env) and follows **Medallion Architecture** principles — beginning with clean data ingestion and progressing toward optimized cloud storage and analytics.

---

## 🧱 Project Structure

```
ETL_Projects/
│
└── retailio-elt/
    ├── data/                 # CSV datasets (products, sales, etc.)
    ├── myenv/                # Virtual environment
    ├── src/                  # Python source files
    │   └── extract.py        # ETL script for uploading to AWS S3
    ├── .env                  # AWS credentials & configuration
    ├── .gitignore            # Excludes env & sensitive files
    ├── README.md             # Project documentation
    └── requirements.txt      # Dependencies
```

---

## ⚙️ Local Setup

### Step 1: Create Project Directory

```bash
mkdir etl_project
cd etl_project
```

### Step 2: Initialize Project Files

```bash
mkdir data src
touch .env requirements.txt README.md
```

### Step 3: Virtual Environment Setup

```bash
python3 -m venv myenv
source myenv/bin/activate      # macOS/Linux
myenv\Scripts\activate         # Windows
```

### Step 4: Install Dependencies

Add to `requirements.txt`:

```
boto3
awswrangler
pandas
chardet
python-dotenv
```

Then install:

```bash
pip install -r requirements.txt
```

---

## 🧾 Datasets

The datasets provided:

- `products.csv`
- `sales.csv`
- (Optional) `customers.csv` or `orders.csv`

Extract and move into the `data/` folder:

```bash
mv ~/Downloads/products.csv data/
mv ~/Downloads/sales.csv data/
```

---

## 🔐 Environment Variables

Create a `.env` file in the root directory:

```
ACCESS_KEY=your_access_key
SECRET_KEY=your_secret_key
REGION=eu-central-1
```

---

## 🧑‍💻 AWS Setup (IAM & S3)

### Create an IAM User

1. Go to **AWS Console → IAM → Users → Create user**
2. Enable **Programmatic Access**
3. Attach **AmazonS3FullAccess** or custom policy
4. Save **Access Key ID** & **Secret Access Key** securely

### Create an S3 Bucket

1. Go to **AWS Console → S3 → Create bucket**
2. Enter a **unique bucket name** (e.g., `retailio-elt-s3`)
3. Select **Region** (e.g., `eu-central-1`)
4. Enable **Block all public access**
5. Turn on **Versioning**
6. Keep **Default Encryption**
7. Create the bucket

---

## 💻 Python Script: Upload CSVs as Parquet

### File: `src/extract.py`

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
bucket = "retailio-elt-s3"

session = boto3.Session(
    aws_access_key_id=access,
    aws_secret_access_key=secret,
    region_name=region
)

datasets = {
    "products": "data/products.csv",
    "sales": "data/sales.csv",
}

for name, path in datasets.items():
    if os.path.exists(path):
        print(f"Processing {name} from {path} ...")

        with open(path, 'rb') as file:
            encoding_detected = chardet.detect(file.read())['encoding']

        df = pd.read_csv(path, encoding=encoding_detected or "latin1")

        wr.s3.to_parquet(
            df=df,
            path=f"s3://{bucket}/{name}/",
            dataset=True,
            mode="overwrite",
            index=False,
            boto3_session=session
        )
        print(f"✅ {name} uploaded successfully to s3://{bucket}/{name}/")
    else:
        print(f"⚠️ File not found: {path}")
```

---

## ⚙️ How It Works

1. Loads credentials from `.env`
2. Detects CSV encoding (UTF-8, Latin-1, etc.)
3. Reads CSVs into DataFrames
4. Converts to Parquet format (columnar, compressed)
5. Uploads data to AWS S3 using **AWS Wrangler**

---

## 💡 Why Parquet?

- Compact and compressed
- Faster to query and process
- Columnar format ideal for analytics
- Integrates seamlessly with Glue, Athena, and Redshift Spectrum

Conversion Flow:

```
CSV → DataFrame → Parquet → S3
```

---

## 🚨 Common Errors & Solutions

| Error / Message                                                 | Root Cause                                     | Solution                                                                                                          |
| --------------------------------------------------------------- | ---------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **`NoCredentialsError: Unable to locate credentials`**          | Missing or misnamed variables in `.env`        | Ensure `.env` includes `ACCESS_KEY`, `SECRET_KEY`, and `REGION`, and you’ve run `load_dotenv()` before using them |
| **`AccessDenied`**                                              | IAM user lacks permissions to write to S3      | Attach **AmazonS3FullAccess** or grant the correct bucket policy                                                  |
| **`ClientError: An error occurred (404)`**                      | Wrong bucket name or region mismatch           | Verify the bucket name in S3 and `.env` region are identical                                                      |
| **`FileNotFoundError`**                                         | CSV path incorrect or file missing in `data/`  | Confirm the file exists in `data/` and path names are case-sensitive                                              |
| **`botocore.exceptions.EndpointConnectionError`**               | Invalid region or network issue                | Check your AWS region value (e.g., `eu-central-1`) and ensure internet connection                                 |
| **`UnicodeDecodeError`**                                        | CSV has special characters or unknown encoding | Use `chardet` to detect encoding automatically (`encoding_detected`)                                              |
| **`ValueError: S3 path does not exist`**                        | Bucket not created yet                         | Create the S3 bucket in AWS Console before running the script                                                     |
| **`OSError: [Errno 22] Invalid argument`**                      | Incorrect S3 path format                       | Ensure S3 path is formatted as `s3://bucket-name/folder/`                                                         |
| **`botocore.exceptions.PartialCredentialsError`**               | Incomplete or malformed credentials            | Double-check `.env` values are correct and not empty                                                              |
| **`ImportError: No module named 'awswrangler'`**                | Missing dependency                             | Run `pip install awswrangler` or reinstall from `requirements.txt`                                                |
| **`NameError: name 'session' is not defined`**                  | Session not initialized before use             | Ensure the `boto3.Session()` block appears before uploading logic                                                 |
| **`AttributeError: module 'boto3' has no attribute 'Session'`** | Typo or outdated boto3                         | Reinstall boto3 using `pip install --upgrade boto3`                                                               |

---

## 🧠 Best Practices

- Never commit `.env` or AWS keys to version control.
- Use `mode="overwrite"` or `"append"` carefully when updating S3 files.
- Ensure consistent AWS region configuration across all scripts and S3.
- Use **Parquet** for efficiency — smaller size, faster analytics, schema evolution support.
- Add `try-except` blocks for better error handling and logging.

---

## 🏁 Next Steps

- Add data validation checks before uploading.
- Register datasets in **AWS Glue** for schema discovery.
- Query Parquet files via **Athena** or **Redshift Spectrum**.
- Automate with **Airflow**, **Lambda**, or **Step Functions**.
- Expand from Bronze (raw) → Silver (cleaned) → Gold (analytics) layers.

---

## ✅ Quick Checklist

- [x] Folder structure created
- [x] Virtual environment activated
- [x] Dependencies installed
- [x] AWS IAM user and keys configured
- [x] S3 bucket created and verified
- [x] `.env` properly filled
- [x] CSVs placed in `/data`
- [x] Script runs without errors
- [x] Data successfully uploaded to S3 as Parquet

---

### 🎯 Summary

You’ve successfully created a Python-based ETL pipeline that:

- Reads CSV files dynamically
- Converts them to Parquet format
- Uploads them to AWS S3 with authentication via Boto3
- Handles encoding, connection, and permission issues gracefully

This workflow mirrors a **production-grade data ingestion process**, forming the foundation for advanced cloud-based analytics.
