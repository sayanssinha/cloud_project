"""Step 6: descriptive analytics + dashboard (matplotlib).
Run:  python dashboard.py            (reads from RDS)
      python dashboard.py --local    (reads iot_local.db)
Outputs: dashboard.png and analytics_results.txt
"""
import sys
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from config import *

LOCAL = "--local" in sys.argv

if LOCAL:
    import sqlite3
    df = pd.read_sql("SELECT * FROM sensor_readings", sqlite3.connect("iot_local.db"),
                     parse_dates=["timestamp"])
else:
    from sqlalchemy import create_engine
    eng = create_engine(
        f"mysql+pymysql://{RDS_USER}:{RDS_PASSWORD}@{RDS_HOST}:{RDS_PORT}/{RDS_DB}")
    df = pd.read_sql("SELECT * FROM sensor_readings", eng, parse_dates=["timestamp"])

df["temperature"] = df["temperature"].astype(float)

# ---------- descriptive analytics ----------
by_sensor = df.groupby("sensor_id").agg(
    readings=("temperature", "size"),
    avg_temp=("temperature", "mean"), min_temp=("temperature", "min"),
    max_temp=("temperature", "max"), avg_hum=("humidity", "mean")).round(2)
hourly = df.set_index("timestamp").resample("h")[["temperature", "humidity"]].mean()

with open("analytics_results.txt", "w") as f:
    f.write(f"Total readings : {len(df)}\n")
    f.write(f"Avg temperature: {df.temperature.mean():.2f} C\n")
    f.write(f"Avg humidity   : {df.humidity.mean():.2f} %\n")
    f.write(f"Temp min / max : {df.temperature.min()} / {df.temperature.max()}\n")
    f.write(f"Humidity min / max: {df.humidity.min()} / {df.humidity.max()}\n\n")
    f.write("Sensor-wise summary\n" + by_sensor.to_string() + "\n")
print(open("analytics_results.txt").read())

# ---------- dashboard ----------
NAVY, ORANGE = "#14407a", "#e8730c"
colors = ["#1f77b4", "#2ca02c", "#e8730c", "#9467bd", "#d62728"]
fig = plt.figure(figsize=(16, 9), facecolor="#f4f7fb")
fig.suptitle("IoT Sensor Analytics Dashboard  |  S3 → ETL → RDS → Python",
             fontsize=18, fontweight="bold", color=NAVY, y=0.97)

# KPI cards
kpis = [("Total Readings", f"{len(df)}"), ("Avg Temperature", f"{df.temperature.mean():.1f} °C"),
        ("Avg Humidity", f"{df.humidity.mean():.0f} %"), ("Sensors", f"{df.sensor_id.nunique()}")]
for i, (label, val) in enumerate(kpis):
    ax = fig.add_axes([0.04 + i * 0.235, 0.80, 0.21, 0.10])
    ax.set_facecolor("white"); ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values(): sp.set_color("#c9d6e8")
    ax.text(0.5, 0.68, val, ha="center", va="center", fontsize=24, fontweight="bold",
            color=ORANGE if i == 1 else NAVY, transform=ax.transAxes)
    ax.text(0.5, 0.20, label, ha="center", va="center", fontsize=11, color="#555",
            transform=ax.transAxes)

gs = fig.add_gridspec(2, 3, left=0.05, right=0.97, bottom=0.07, top=0.74, hspace=0.45, wspace=0.28)

ax1 = fig.add_subplot(gs[0, :2])                       # temperature trend per sensor
for c, (sid, g) in zip(colors, df.groupby("sensor_id")):
    ax1.plot(g["timestamp"], g["temperature"], lw=1.2, color=c, label=sid)
ax1.set_title("Temperature trend over time", loc="left", fontweight="bold", color=NAVY)
ax1.set_ylabel("°C"); ax1.legend(ncol=5, fontsize=8, frameon=False)
ax1.xaxis.set_major_formatter(mdates.DateFormatter("%d %b %H:%M"))

ax2 = fig.add_subplot(gs[0, 2])                        # avg temp by sensor
ax2.bar(by_sensor.index, by_sensor["avg_temp"], color=colors)
ax2.set_title("Avg temperature by sensor", loc="left", fontweight="bold", color=NAVY)
ax2.set_ylim(by_sensor["avg_temp"].min() - 3, by_sensor["avg_temp"].max() + 1.5)
for x, v in zip(by_sensor.index, by_sensor["avg_temp"]):
    ax2.text(x, v + 0.1, f"{v:.1f}", ha="center", fontsize=8)

ax3 = fig.add_subplot(gs[1, 0])                        # humidity share pie
ax3.pie(by_sensor["avg_hum"], labels=by_sensor.index, colors=colors, autopct="%1.0f%%",
        textprops={"fontsize": 8}, startangle=90)
ax3.set_title("Avg humidity share by sensor", loc="left", fontweight="bold", color=NAVY)

ax4 = fig.add_subplot(gs[1, 1])                        # hourly humidity
ax4.plot(hourly.index, hourly["humidity"], color="#2a9d8f", lw=1.6)
ax4.fill_between(hourly.index, hourly["humidity"], alpha=0.15, color="#2a9d8f")
ax4.set_title("Hourly avg humidity", loc="left", fontweight="bold", color=NAVY)
ax4.set_ylim(hourly["humidity"].min() - 5, hourly["humidity"].max() + 5); ax4.set_ylabel("%"); ax4.xaxis.set_major_formatter(mdates.DateFormatter("%d %H:%M"))
ax4.tick_params(axis="x", labelsize=7)

ax5 = fig.add_subplot(gs[1, 2])                        # table of recent readings
ax5.axis("off")
recent = df.sort_values("timestamp", ascending=False).head(6)
cell = [[r.timestamp.strftime("%m-%d %H:%M"), r.sensor_id, f"{r.temperature:.1f}", r.humidity]
        for r in recent.itertuples()]
t = ax5.table(cellText=cell, colLabels=["Time", "Sensor", "Temp", "Hum"], loc="center")
t.auto_set_font_size(False); t.set_fontsize(8); t.scale(1, 1.4)
for (r, c), cl in t.get_celld().items():
    if r == 0: cl.set_facecolor(NAVY); cl.set_text_props(color="white", fontweight="bold")
ax5.set_title("Recent readings", loc="left", fontweight="bold", color=NAVY)

for a in (ax1, ax2, ax4):
    a.set_facecolor("white"); a.grid(alpha=0.25)
    for sp in ("top", "right"): a.spines[sp].set_visible(False)
fig.savefig("dashboard.png", dpi=130)
print("Saved dashboard.png")
