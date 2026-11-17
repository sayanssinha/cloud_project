"""Edit these values, or set them as environment variables."""
import os

AWS_REGION   = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET    = os.getenv("S3_BUCKET", "iot-mini-project-arghadeep-2026")  # must be globally unique
S3_KEY       = "raw/sensor_data.csv"

RDS_HOST     = os.getenv("RDS_HOST", "your-db.xxxxxxxx.ap-south-1.rds.amazonaws.com")
RDS_PORT     = int(os.getenv("RDS_PORT", "3306"))
RDS_USER     = os.getenv("RDS_USER", "admin")
RDS_PASSWORD = os.getenv("RDS_PASSWORD", "change-me")
RDS_DB       = os.getenv("RDS_DB", "iot_db")
RDS_TABLE    = "sensor_readings"
