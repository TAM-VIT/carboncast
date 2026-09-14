"""Precompute optimiser results so the booth demo is instant, not a 4-second spinner."""
import json
from optimizer import optimize, evaluate
from carbon import BASELINES, GRADE_TARGET

out = {"grades": {}, "pareto": []}
for g, t in GRADE_TARGET.items():
    r = optimize(t)
    b = evaluate(BASELINES[g])
    r["baseline"] = b
    r["savings"] = {
        "co2_abs": round(b["co2"] - r["co2"], 1),
        "co2_pct": round(100 * (1 - r["co2"] / b["co2"]), 1),
        "cost_abs": round(b["cost"] - r["cost"], 0),
        "cement_abs": round(b["mix"]["cement"] - r["mix"]["cement"], 1),
    }
    out["grades"][g] = r
    print("done", g, r["savings"]["co2_pct"], "%", flush=True)

for t in [20, 25, 30, 35, 40, 45, 50]:
    r = optimize(float(t))
    out["pareto"].append({"target": t, "co2": r["co2"], "strength_lo": r["strength"]["lo"],
                          "feasible": r["feasible"], "binder": r["stats"]["binder"],
                          "scm": r["stats"]["scm_fraction"]})
    print("pareto", t, flush=True)

json.dump(out, open("artifacts/precomputed.json", "w"), indent=1)
print("WROTE artifacts/precomputed.json")
