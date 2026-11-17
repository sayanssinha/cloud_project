# IoT Data Analytics Using AWS (S3 → ETL → RDS → Dashboard)

## 1. Objective
Build a small cloud pipeline: store IoT sensor data in Amazon S3, move it into Amazon RDS (MySQL)
through a Python ETL job, analyse it with SQL/Python, and present it on a dashboard.

## 2. Architecture
```
Python simulator -> sensor_data.csv -> Amazon S3 -> Python ETL (extract/clean/load) -> Amazon RDS MySQL -> SQL + Python dashboard
```

## 3. Files
| File | Purpose |
|---|---|
| `generate_data.py` | Simulates 5 sensors x 100 readings (temperature, humidity, timestamp); adds a few nulls/duplicates on purpose |
| `sensor_data.csv` | Generated dataset (502 raw rows) |
| `upload_to_s3.py` | Creates a private bucket and uploads the CSV |
| `rds_setup.sql` | Creates database and table |
| `etl.py` | Extract from S3, transform with pandas, load into RDS |
| `queries.sql` | Descriptive analytics queries |
| `dashboard.py` | Reads from RDS, writes `dashboard.png` and `analytics_results.txt` |
| `config.py` | Bucket, region and RDS settings |

## 4. Step-by-step on AWS
1. **Install and configure:** `pip install -r requirements.txt`, then `aws configure` (use an IAM user with S3 access only, not root).
2. **Dataset:** `python generate_data.py`
3. **S3:** edit `S3_BUCKET` in `config.py` (must be globally unique), run `python upload_to_s3.py`. Take a screenshot of the bucket in the S3 console showing `raw/sensor_data.csv`.
4. **RDS:** Console -> RDS -> Create database -> MySQL -> **Free tier** template, `db.t3.micro`/`db.t4g.micro`, 20 GB storage, set master username/password, turn off Multi-AZ, disable storage autoscaling.
   - Connectivity: Public access **Yes** only for the demo, and set the security group inbound rule for MySQL (3306) to **My IP only**, never 0.0.0.0/0.
   - Copy the endpoint into `RDS_HOST` in `config.py`. Set the password via env var: `export RDS_PASSWORD=...`
5. **Create table:** `mysql -h <endpoint> -u admin -p < rds_setup.sql` (or paste into MySQL Workbench). Screenshot the table.
6. **ETL:** `python etl.py`. Expected output: `Transform: 502 rows in -> 496 rows out`, then `Rows now in sensor_readings: 496`.
7. **Analytics:** run `queries.sql` in Workbench, screenshot the results (sample records plus aggregates).
8. **Dashboard:** `python dashboard.py` produces `dashboard.png`. For Tableau instead, connect Tableau to MySQL with the RDS endpoint and rebuild the same charts.
9. **Clean up (important):** delete the RDS instance (skip final snapshot), empty and delete the S3 bucket, and remove the security-group rule.

## 5. ETL transformations
- Dropped 2 duplicate rows
- Dropped 4 rows with missing temperature or humidity
- Converted types (timestamp, float, int), normalised sensor IDs
- Range check: temperature -40 to 85 C, humidity 0 to 100 %

## 6. Results (from the generated dataset)
| Metric | Value |
|---|---|
| Total clean readings | 496 |
| Average temperature | 28.90 C |
| Average humidity | 62.88 % |
| Temperature min / max | 22.8 / 35.0 C |
| Humidity min / max | 46 / 79 % |

| Sensor | Readings | Avg Temp | Min | Max | Avg Humidity |
|---|---|---|---|---|---|
| S01 | 98 | 27.80 | 24.1 | 31.8 | 65.32 |
| S02 | 100 | 29.98 | 26.0 | 33.7 | 60.27 |
| S03 | 100 | 26.38 | 22.8 | 29.8 | 69.93 |
| S04 | 98 | 31.38 | 27.5 | 35.0 | 55.33 |
| S05 | 100 | 28.99 | 25.3 | 32.8 | 63.47 |

**Findings:** S04 is the warmest and driest sensor, S03 the coolest and most humid. Temperature follows a daily cycle (lowest near early morning, peak around midday to afternoon), while humidity moves in the opposite direction.

## 7. Conclusion
The pipeline shows how cloud storage (S3), a managed relational database (RDS) and a scripted ETL work together to turn raw IoT readings into analysable data and a dashboard. Possible extensions: AWS Glue for the ETL, S3 event triggers with Lambda, and live data via AWS IoT Core.

## 8. Presentation outline (7 slides)
1. Title and objective  2. Architecture diagram  3. Dataset and S3 screenshot  4. RDS config and sample records  5. ETL code and transformations  6. SQL analytics results  7. Dashboard demo, conclusion, cost clean-up
