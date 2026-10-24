"""Synthetic charging-demand data (replace with real session logs from meter_readings / bookings)."""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
HOURLY = np.array([.1,.05,.05,.05,.1,.2,.4,.7,.9,.8,.6,.5,.5,.5,.5,.55,.6,.75,1.0,1.0,.9,.6,.35,.2])

rows = []
for _ in range(20000):
    hour, dow = int(rng.integers(24)), int(rng.integers(7))
    temp = float(rng.normal(28, 6))
    demand = HOURLY[hour] * (0.85 if dow >= 5 else 1.0) + 0.01 * max(0, temp - 32) + rng.normal(0, 0.05)
    rows.append((hour, dow, temp, float(np.clip(demand, 0, 1))))

pd.DataFrame(rows, columns=["hour", "dow", "temp_c", "demand"]).to_csv("demand.csv", index=False)
print("wrote demand.csv", len(rows))
