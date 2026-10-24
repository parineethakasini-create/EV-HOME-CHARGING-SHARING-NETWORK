"""Meter tampering / fake-session detection with Isolation Forest -> artifacts/anomaly.joblib.
Features must match backend/app/anomaly.py: [power_w, voltage, current, power/(V*I)]."""
import joblib
import numpy as np
from sklearn.ensemble import IsolationForest

rng = np.random.default_rng(0)
n = 5000
voltage = rng.normal(230, 4, n)
current = rng.uniform(6, 32, n)
power = voltage * current * rng.normal(0.98, 0.01, n)          # P ~ V*I
def feats(p, v, i):
    return np.c_[p, v, i, p / np.maximum(v * i, 1e-6)]   # ratio exposes P != V*I tampering


normal = feats(power, voltage, current)

m = IsolationForest(n_estimators=200, contamination=0.01, random_state=0).fit(normal)

fake = feats(rng.uniform(100, 400, 50), rng.normal(230, 4, 50), rng.uniform(20, 32, 50))   # high current, tiny power
print("normal flagged:", round((m.predict(normal) == -1).mean(), 4), "| tampered flagged:", round((m.predict(fake) == -1).mean(), 2))
joblib.dump(m, "artifacts/anomaly.joblib")
print("saved artifacts/anomaly.joblib")
