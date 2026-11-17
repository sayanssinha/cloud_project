"""Step 1: simulate IoT sensor readings and save as CSV."""
import numpy as np
import pandas as pd

np.random.seed(42)
SENSORS = ["S01", "S02", "S03", "S04", "S05"]
N_PER_SENSOR = 100                       # 5 x 100 = 500 rows
START = pd.Timestamp("2026-10-01 00:00:00")
INTERVAL_MIN = 15

# each sensor gets its own baseline so sensor-wise analysis is interesting
base_temp = {"S01": 28.0, "S02": 30.0, "S03": 26.5, "S04": 31.5, "S05": 29.0}
base_hum  = {"S01": 65,   "S02": 60,   "S03": 70,   "S04": 55,   "S05": 63}

rows = []
for sid in SENSORS:
    for i in range(N_PER_SENSOR):
        ts = START + pd.Timedelta(minutes=INTERVAL_MIN * i)
        hour = ts.hour + ts.minute / 60
        daily = 3.0 * np.sin((hour - 9) / 24 * 2 * np.pi)          # day/night cycle
        temp = base_temp[sid] + daily + np.random.normal(0, 0.6)
        hum  = base_hum[sid] - 2.0 * daily + np.random.normal(0, 2.0)
        rows.append([ts, sid, round(temp, 1), int(round(np.clip(hum, 20, 100)))])

df = pd.DataFrame(rows, columns=["timestamp", "sensor_id", "temperature", "humidity"])

# inject a few dirty rows so the ETL "clean" step has real work to do
dirty = df.sample(6, random_state=1).index
df.loc[dirty[:2], "temperature"] = np.nan          # missing values
df.loc[dirty[2:4], "humidity"] = np.nan
df = pd.concat([df, df.iloc[[10, 250]]])           # 2 duplicate rows

df = df.sort_values(["timestamp", "sensor_id"]).reset_index(drop=True)
df.to_csv("sensor_data.csv", index=False)
print(f"Saved sensor_data.csv with {len(df)} rows")
print(df.head())
