import os
import boto3
import pandas as pd
import awswrangler as wr
import dotenv
from dotenv import load_dotenv

load_dotenv()

access = os.getenv("ACCESS_KEY")
secret = os.getenv("SECRET_KEY")
region = os.getenv("REGION")
bucket = "retailio-elt-s3"

#create a boto3 session
session = boto3.Session(
    aws_access_key_id = access,
    aws_secret_access_key = secret,
    region_name = region,
    
)

datasets = {
    "products": "data/raw/products.csv",
    "sales": "data/raw/sales.csv"
}

for name, path in datasets.items():
    if os.path.exists(path):
        df = pd.read_csv(path, encoding="latin1")
        wr.s3.to_parquet(    
            df = df,
            path = f"s3://{bucket}/raw/{name}",
            dataset = True,
            mode = "overwrite",
            index = False,
            boto3_session = session 
    )
    else:
        print("there is error")