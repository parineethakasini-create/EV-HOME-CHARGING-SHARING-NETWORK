"""Demand forecasting -> artifacts/demand.joblib.  Swap GradientBoostingRegressor for XGBoost/Prophet/LSTM as needed."""
import joblib
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

df = pd.read_csv("demand.csv")
X, y = df[["hour", "dow", "temp_c"]].values, df["demand"].values
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=0)
m = GradientBoostingRegressor(n_estimators=150, max_depth=3, random_state=0).fit(Xtr, ytr)
print("MAE:", round(mean_absolute_error(yte, m.predict(Xte)), 4))
joblib.dump(m, "artifacts/demand.joblib")
print("saved artifacts/demand.joblib")
