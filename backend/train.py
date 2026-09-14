"""Train conformally-calibrated quantile strength models for CarbonCast.

Plain quantile regression overfits here: the raw P05-P95 band covered only ~58% of
held-out data instead of 90%, which would make our "5th percentile" safety margin a
fiction. We fix it with split-conformal quantile regression (CQR, Romano et al. 2019):
fit quantile models on a proper-training split, measure conformity scores on a held-out
calibration split, and widen the band by the resulting offset. That buys a
distribution-free, finite-sample coverage guarantee.

The calibrated LOWER bound is what the optimiser constrains against, so the safety
margin is engineered in rather than assumed.
"""
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from carbon import FEATURES

MODEL_FEATURES = FEATURES + ["age"]
ALPHA = 0.10  # target 90% coverage -> 5th/95th percentile band
HP = dict(max_iter=300, learning_rate=0.06, max_leaf_nodes=31,
          min_samples_leaf=20, l2_regularization=1.0, random_state=42)

df = pd.read_csv("data/concrete.csv")
X, y = df[MODEL_FEATURES].values, df["strength"].values
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
# carve a calibration split out of train for conformal prediction
Xpro, Xcal, ypro, ycal = train_test_split(Xtr, ytr, test_size=0.3, random_state=42)

lo_m = HistGradientBoostingRegressor(loss="quantile", quantile=ALPHA / 2, **HP).fit(Xpro, ypro)
hi_m = HistGradientBoostingRegressor(loss="quantile", quantile=1 - ALPHA / 2, **HP).fit(Xpro, ypro)

# Conformity score: how far outside the band each calibration point fell.
E = np.maximum(lo_m.predict(Xcal) - ycal, ycal - hi_m.predict(Xcal))
n = len(E)
level = min(1.0, np.ceil((n + 1) * (1 - ALPHA)) / n)
offset = float(np.quantile(E, level))

# Point estimate + median trained on the full training set.
mean_m = HistGradientBoostingRegressor(loss="squared_error", **HP).fit(Xtr, ytr)
# P50 must share the lo/hi training split, otherwise the three quantiles come from
# different models and can cross - we saw a median land BELOW its own lower bound.
p50_m = HistGradientBoostingRegressor(loss="quantile", quantile=0.5, **HP).fit(Xpro, ypro)

pred = mean_m.predict(Xte)
r2 = r2_score(yte, pred)
rmse = float(np.sqrt(mean_squared_error(yte, pred)))

raw_cov = float(np.mean((yte >= lo_m.predict(Xte)) & (yte <= hi_m.predict(Xte))))
cal_cov = float(np.mean((yte >= lo_m.predict(Xte) - offset) & (yte <= hi_m.predict(Xte) + offset)))

bounds = {f: [float(df[f].quantile(0.05)), float(df[f].quantile(0.95))] for f in FEATURES}
scaler = StandardScaler().fit(df[FEATURES].values)
Xs = scaler.transform(df[FEATURES].values)
# The UCI set contains duplicate rows, so the MEDIAN kNN distance is 0 and any ratio
# against it explodes. Use the 90th percentile of the kNN distance distribution as the
# reference scale instead: "as isolated as the loneliest 10% of real mixes".
nn = NearestNeighbors(n_neighbors=6).fit(Xs)
_d = nn.kneighbors(Xs)[0][:, 1:].mean(axis=1)
typical_dist = float(np.quantile(_d, 0.90))
assert typical_dist > 1e-3, f"degenerate novelty scale: {typical_dist}"

joblib.dump({"models": {"lo": lo_m, "hi": hi_m, "mean": mean_m, "p50": p50_m},
             "offset": offset, "scaler": scaler, "nn": nn, "bounds": bounds,
             "typical_dist": typical_dist, "features": MODEL_FEATURES}, "artifacts/models.pkl")

metrics = {"r2": round(r2, 4), "rmse": round(rmse, 2),
           "coverage_raw": round(raw_cov, 3), "coverage_calibrated": round(cal_cov, 3),
           "conformal_offset_mpa": round(offset, 2), "target_coverage": 1 - ALPHA,
           "novelty_scale": round(typical_dist, 4), "n_train": len(Xpro), "n_calib": len(Xcal), "n_test": len(Xte), "n_total": len(df)}
json.dump(metrics, open("artifacts/metrics.json", "w"), indent=2)
print(json.dumps(metrics))
