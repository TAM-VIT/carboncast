"""Carbon-minimising mix design under IS-code engineering constraints.

We minimise kg CO2e per m3 subject to the CONFORMALLY CALIBRATED LOWER BOUND of
predicted strength clearing the target - not the mean prediction. A mean-constrained
optimiser would hand you a mix that fails half the time by construction.

Constraints encoded as penalties (more robust for differential evolution than
NonlinearConstraint, and lets us trade off softly during the search):
  - calibrated P05 strength >= target            (the safety margin)
  - each ingredient within the 5th-95th pct of observed data  (anti-extrapolation)
  - fresh density 2300-2600 kg/m3                (mass balance - it must be real concrete)
  - water/binder 0.28-0.70                       (workability and hydration limits)
  - SCM replacement <= 70% of binder             (IS 456 practical ceiling)
  - binder >= 300 kg/m3                          (IS 456 durability floor)
  - coarse/fine aggregate ratio 1.2-2.2          (realistic grading)
  - kNN novelty <= 2x typical spacing            (stay where the data supports us)

That last one matters. Without it the search happily walks into regions no lab ever
tested and reports a fantasy carbon saving. We would rather report a smaller number
we can actually defend.
"""
import warnings
warnings.filterwarnings("ignore", message=".*vectorized.*")
import numpy as np
import joblib
from scipy.optimize import differential_evolution
from carbon import FEATURES, EF, co2, cost, mix_stats

_A = joblib.load("artifacts/models.pkl")
LO, HI, MEAN = _A["models"]["lo"], _A["models"]["hi"], _A["models"]["mean"]
P50 = _A["models"]["p50"]
OFFSET, BOUNDS, SCALER, NN = _A["offset"], _A["bounds"], _A["scaler"], _A["nn"]
TYPICAL_DIST = _A["typical_dist"]
EF_VEC = np.array([EF[f] for f in FEATURES])
IDX = {f: i for i, f in enumerate(FEATURES)}


def _prep(V, age):
    """V: (n,7) ingredient matrix -> (n,8) model input with age appended."""
    return np.column_stack([V, np.full(len(V), age, dtype=float)])


def strength_lo(V, age=28):
    """Conformally calibrated lower bound on 28-day strength."""
    return LO.predict(_prep(V, age)) - OFFSET


def strength_all(mix, age=28):
    """Returns the calibrated band. Quantile models can cross on unusual mixes, so we
    sort the three estimates - the standard post-hoc fix - to guarantee lo <= mid <= hi
    rather than displaying a median that sits outside its own interval."""
    V = np.array([[mix[f] for f in FEATURES]], dtype=float)
    Z = _prep(V, age)
    lo = float(LO.predict(Z)[0] - OFFSET)
    mid = float(P50.predict(Z)[0])
    hi = float(HI.predict(Z)[0] + OFFSET)
    lo, mid, hi = sorted([lo, mid, hi])
    return {"lo": round(lo, 2), "mid": round(mid, 2), "hi": round(hi, 2),
            "mean": round(float(MEAN.predict(Z)[0]), 2)}


def novelty(mix):
    """How far is this mix from anything in the training data? Guards extrapolation."""
    V = np.array([[mix[f] for f in FEATURES]], dtype=float)
    d = float(NN.kneighbors(SCALER.transform(V))[0].mean())
    ratio = d / max(TYPICAL_DIST, 1e-9)
    return {"distance": round(d, 3), "ratio": round(ratio, 2),
            "status": "supported" if ratio <= 3.0 else "extrapolating"}


def _penalised(V, target, age):
    """Vectorised objective: CO2 + constraint penalties. V is (n,7)."""
    co2_v = V @ EF_VEC
    binder = V[:, IDX["cement"]] + V[:, IDX["slag"]] + V[:, IDX["fly_ash"]]
    binder_safe = np.maximum(binder, 1e-6)
    water = V[:, IDX["water"]]
    total = V.sum(axis=1)
    wb = water / binder_safe
    scm = (V[:, IDX["slag"]] + V[:, IDX["fly_ash"]]) / binder_safe

    cf_ratio = V[:, IDX["coarse_agg"]] / np.maximum(V[:, IDX["fine_agg"]], 1e-6)
    nov = NN.kneighbors(SCALER.transform(V))[0].mean(axis=1) / max(TYPICAL_DIST, 1e-9)

    short = np.maximum(0.0, target - strength_lo(V, age))
    pen = 500.0 * short + 200.0 * short ** 2           # strength dominates everything
    pen += 0.5 * np.maximum(0.0, 2300.0 - total) ** 2
    pen += 0.5 * np.maximum(0.0, total - 2600.0) ** 2
    pen += 1e4 * np.maximum(0.0, 0.28 - wb) ** 2
    pen += 1e4 * np.maximum(0.0, wb - 0.70) ** 2
    pen += 1e4 * np.maximum(0.0, scm - 0.70) ** 2
    pen += 2.0 * np.maximum(0.0, 300.0 - binder) ** 2
    pen += 300.0 * np.maximum(0.0, 1.2 - cf_ratio) ** 2
    pen += 300.0 * np.maximum(0.0, cf_ratio - 2.2) ** 2
    pen += 150.0 * np.maximum(0.0, nov - 2.0) ** 2      # stay inside the evidence
    return co2_v + pen


def optimize(target, age=28, seed=42, maxiter=80):
    blist = [tuple(BOUNDS[f]) for f in FEATURES]

    def obj(x):
        V = np.atleast_2d(x.T) if x.ndim > 1 else np.atleast_2d(x)
        return _penalised(V, target, age)

    res = differential_evolution(obj, blist, seed=seed, maxiter=maxiter, popsize=24,
                                 tol=0.01, mutation=(0.5, 1.0), recombination=0.7,
                                 polish=True, vectorized=True, init="sobol")
    mix = {f: round(float(v), 1) for f, v in zip(FEATURES, res.x)}
    s = strength_all(mix, age)
    c, cparts = co2(mix)
    rs, rparts = cost(mix)
    return {"mix": mix, "strength": s, "co2": c, "co2_parts": cparts,
            "cost": rs, "cost_parts": rparts, "stats": mix_stats(mix),
            "novelty": novelty(mix), "feasible": s["lo"] >= target - 0.05,
            "target": target, "age": age}


def evaluate(mix, age=28):
    c, cparts = co2(mix)
    rs, rparts = cost(mix)
    return {"mix": mix, "strength": strength_all(mix, age), "co2": c, "co2_parts": cparts,
            "cost": rs, "cost_parts": rparts, "stats": mix_stats(mix),
            "novelty": novelty(mix), "age": age}
