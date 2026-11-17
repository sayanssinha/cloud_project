"""Step 4: ETL  S3 (CSV) --> pandas transform --> RDS MySQL.
Run:  python etl.py            (real AWS)
      python etl.py --local    (offline test: reads local CSV, loads into SQLite)
"""
import io
import sys
import pandas as pd
from config import *

LOCAL = "--local" in sys.argv


# ---------- EXTRACT ----------
def extract() -> pd.DataFrame:
    if LOCAL:
        return pd.read_csv("sensor_data.csv")
    import boto3
    body = boto3.client("s3", region_name=AWS_REGION).get_object(
        Bucket=S3_BUCKET, Key=S3_KEY)["Body"].read()
    return pd.read_csv(io.BytesIO(body))


# ---------- TRANSFORM ----------
def transform(df: pd.DataFrame) -> pd.DataFrame:
    n0 = len(df)
    df = df.drop_duplicates()                                   # remove duplicates
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")   # types
    df["temperature"] = pd.to_numeric(df["temperature"], errors="coerce")
    df["humidity"] = pd.to_numeric(df["humidity"], errors="coerce")
    df["sensor_id"] = df["sensor_id"].astype(str).str.strip().str.upper()
    df = df.dropna()                                            # handle nulls
    df = df[df["temperature"].between(-40, 85) & df["humidity"].between(0, 100)]  # sanity
    df["humidity"] = df["humidity"].astype(int)
    print(f"Transform: {n0} rows in -> {len(df)} rows out")
    return df.reset_index(drop=True)


# ---------- LOAD ----------
def load(df: pd.DataFrame):
    if LOCAL:                                   # offline test with SQLite (stdlib)
        import sqlite3
        conn = sqlite3.connect("iot_local.db")
        conn.execute(f"DROP TABLE IF EXISTS {RDS_TABLE}")
        df.to_sql(RDS_TABLE, conn, index=False)
        count = conn.execute(f"SELECT COUNT(*) FROM {RDS_TABLE}").fetchone()[0]
        conn.close()
    else:                                       # real RDS MySQL
        from sqlalchemy import create_engine, text
        eng = create_engine(
            f"mysql+pymysql://{RDS_USER}:{RDS_PASSWORD}@{RDS_HOST}:{RDS_PORT}/{RDS_DB}")
        with eng.begin() as conn:
            conn.execute(text(f"TRUNCATE TABLE {RDS_TABLE}"))   # idempotent re-runs
        df.to_sql(RDS_TABLE, eng, if_exists="append", index=False)
        with eng.connect() as conn:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {RDS_TABLE}")).scalar()
    print(f"Loaded. Rows now in {RDS_TABLE}: {count}")


if __name__ == "__main__":
    load(transform(extract()))
