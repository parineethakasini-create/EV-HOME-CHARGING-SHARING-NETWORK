# ML pipeline

```
meter_readings (Timescale) ─► features (hour, dow, temp, location, price) ─► models ─► backend /pricing/suggest
```
| Use case | Model here | Alternatives | Used by |
|---|---|---|---|
| Demand forecasting | GradientBoostingRegressor | XGBoost, Prophet, LSTM | `backend/app/pricing.py` |
| Dynamic pricing | demand → price multiplier (0.8×–1.5×) | regression / RL | `GET /pricing/suggest` |
| Anomaly / fraud | IsolationForest | rules | `backend/app/anomaly.py` (+ built-in rules) |
| Recommendation | distance/price/rating ranking | learning-to-rank | `GET /chargers` |

```bash
cd ml && pip install -r requirements.txt
python generate_data.py && python train_demand.py && python train_anomaly.py
cp artifacts/*.joblib ../backend/ml_artifacts/      # backend falls back to heuristics if absent
```
Docker Compose mounts `ml/artifacts` into the backend automatically.
