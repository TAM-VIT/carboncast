"""CarbonCast API. Serves the built React app too, so the booth runs one process."""
import json, os, functools
import pandas as pd
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Dict, Optional

from carbon import FEATURES, LABELS, EF, COST, BASELINES, GRADE_TARGET, co2
from optimizer import optimize, evaluate, BOUNDS

app = FastAPI(title="CarbonCast")
HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(HERE, "..", "frontend", "dist")

# A new VIT academic block. RCC framed structures use roughly 0.35 m3 of concrete per m2
# of built-up area; 8 floors over a 1800 m2 footprint is a typical new block.
VIT_BLOCK = {"name": "New academic block", "floors": 8, "footprint_m2": 1800,
             "concrete_per_m2": 0.35}
VIT_BLOCK["built_up_m2"] = VIT_BLOCK["floors"] * VIT_BLOCK["footprint_m2"]
VIT_BLOCK["volume_m3"] = round(VIT_BLOCK["built_up_m2"] * VIT_BLOCK["concrete_per_m2"])

# tonnes CO2e per unit, for making a big number feel like something
EQUIV = {"flight_chennai_london_rt": 2.2, "car_year": 2.0, "tree_year": 0.022}


@functools.lru_cache(maxsize=1)
def precomputed():
    p = os.path.join(HERE, "artifacts", "precomputed.json")
    return json.load(open(p)) if os.path.exists(p) else {"grades": {}, "pareto": []}


@functools.lru_cache(maxsize=1)
def metrics():
    return json.load(open(os.path.join(HERE, "artifacts", "metrics.json")))


@functools.lru_cache(maxsize=1)
def dataset_cloud():
    """Every real 28-day mix plotted as CO2 vs measured strength - the backdrop that
    shows how much room the industry leaves on the table."""
    df = pd.read_csv(os.path.join(HERE, "data", "concrete.csv"))
    df = df[df["age"] == 28]
    pts = []
    for _, r in df.iterrows():
        c, _ = co2({f: float(r[f]) for f in FEATURES})
        pts.append({"co2": c, "strength": round(float(r["strength"]), 1)})
    return pts


class Mix(BaseModel):
    cement: float; slag: float; fly_ash: float; water: float
    superplasticizer: float; coarse_agg: float; fine_agg: float
    age: int = 28


class OptReq(BaseModel):
    target: Optional[float] = None
    grade: Optional[str] = None


class ImpactReq(BaseModel):
    co2_saved_per_m3: float
    volume_m3: Optional[float] = None


@app.get("/api/meta")
def meta():
    return {"features": FEATURES, "labels": LABELS, "bounds": BOUNDS,
            "ef": EF, "cost": COST, "baselines": BASELINES, "grades": GRADE_TARGET,
            "metrics": metrics(), "vit_block": VIT_BLOCK,
            "defaults": BASELINES["M30"]}


@app.post("/api/predict")
def predict(m: Mix):
    d = m.model_dump(); age = d.pop("age")
    return evaluate(d, age=age)


@app.post("/api/optimize")
def do_optimize(req: OptReq):
    pre = precomputed()
    if req.grade and req.grade in pre.get("grades", {}):
        return pre["grades"][req.grade]          # instant, precomputed
    target = req.target if req.target is not None else GRADE_TARGET.get(req.grade or "M30", 30.0)
    r = optimize(float(target))
    grade = req.grade or min(GRADE_TARGET, key=lambda g: abs(GRADE_TARGET[g] - target))
    b = evaluate(BASELINES[grade])
    r["baseline"] = b
    r["savings"] = {"co2_abs": round(b["co2"] - r["co2"], 1),
                    "co2_pct": round(100 * (1 - r["co2"] / b["co2"]), 1),
                    "cost_abs": round(b["cost"] - r["cost"], 0),
                    "cement_abs": round(b["mix"]["cement"] - r["mix"]["cement"], 1)}
    return r


@app.get("/api/pareto")
def pareto():
    return {"frontier": precomputed().get("pareto", []), "cloud": dataset_cloud()}


@app.post("/api/impact")
def impact(req: ImpactReq):
    vol = req.volume_m3 or VIT_BLOCK["volume_m3"]
    tonnes = req.co2_saved_per_m3 * vol / 1000.0
    return {"volume_m3": vol, "tonnes": round(tonnes, 1), "block": VIT_BLOCK,
            "equivalents": {
                "flights": round(tonnes / EQUIV["flight_chennai_london_rt"]),
                "car_years": round(tonnes / EQUIV["car_year"]),
                "tree_years": round(tonnes / EQUIV["tree_year"]),
            }}


if os.path.isdir(DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(DIST, "assets")), name="assets")

    @app.get("/{full_path:path}")
    def spa(full_path: str):
        f = os.path.join(DIST, full_path)
        if full_path and os.path.isfile(f):
            return FileResponse(f)
        return FileResponse(os.path.join(DIST, "index.html"))
