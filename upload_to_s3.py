"""Step 2: upload the CSV to Amazon S3. Needs `aws configure` (or an IAM role) first."""
import boto3
from botocore.exceptions import ClientError
from config import AWS_REGION, S3_BUCKET, S3_KEY

s3 = boto3.client("s3", region_name=AWS_REGION)

try:
    s3.head_bucket(Bucket=S3_BUCKET)
except ClientError:
    kwargs = {"Bucket": S3_BUCKET}
    if AWS_REGION != "us-east-1":
        kwargs["CreateBucketConfiguration"] = {"LocationConstraint": AWS_REGION}
    s3.create_bucket(**kwargs)
    s3.put_public_access_block(
        Bucket=S3_BUCKET,
        PublicAccessBlockConfiguration={
            "BlockPublicAcls": True, "IgnorePublicAcls": True,
            "BlockPublicPolicy": True, "RestrictPublicBuckets": True})
    print(f"Created private bucket: {S3_BUCKET}")

s3.upload_file("sensor_data.csv", S3_BUCKET, S3_KEY)
print(f"Uploaded to s3://{S3_BUCKET}/{S3_KEY}")

for obj in s3.list_objects_v2(Bucket=S3_BUCKET).get("Contents", []):
    print(" -", obj["Key"], obj["Size"], "bytes")   # screenshot the S3 console too
