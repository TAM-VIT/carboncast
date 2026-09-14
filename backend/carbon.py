"""Carbon + cost accounting for concrete mixes.

Emission factors: ICE database v3 (Circular Ecology / Univ. of Bath), kg CO2e per kg.
Fly ash and GGBS carry only transport/processing burden because they are industrial
wastes - the emissions are allocated to the coal plant and steel furnace that made them.
Costs are indicative Indian market rates (Rs/kg, Tamil Nadu, 2025) and are clearly
labelled as approximate in the UI.
"""

FEATURES = ["cement", "slag", "fly_ash", "water", "superplasticizer", "coarse_agg", "fine_agg"]

LABELS = {
    "cement": "Cement (OPC)", "slag": "GGBS slag", "fly_ash": "Fly ash",
    "water": "Water", "superplasticizer": "Superplasticizer",
    "coarse_agg": "Coarse aggregate", "fine_agg": "Fine aggregate (sand)",
}

# kg CO2e per kg of material
EF = {
    "cement": 0.912, "slag": 0.079, "fly_ash": 0.008, "water": 0.000344,
    "superplasticizer": 1.88, "coarse_agg": 0.0048, "fine_agg": 0.0051,
}

# Rs per kg (indicative)
COST = {
    "cement": 8.0, "slag": 4.0, "fly_ash": 1.5, "water": 0.05,
    "superplasticizer": 90.0, "coarse_agg": 1.0, "fine_agg": 1.2,
}

# Typical site mixes (kg/m3) in the IS 10262 style. This is what we are beating.
BASELINES = {
    "M20": {"cement": 320, "slag": 0, "fly_ash": 0, "water": 186, "superplasticizer": 0.0,
            "coarse_agg": 1210, "fine_agg": 650},
    "M25": {"cement": 340, "slag": 0, "fly_ash": 0, "water": 180, "superplasticizer": 0.0,
            "coarse_agg": 1195, "fine_agg": 660},
    "M30": {"cement": 380, "slag": 0, "fly_ash": 0, "water": 175, "superplasticizer": 2.0,
            "coarse_agg": 1180, "fine_agg": 660},
    "M40": {"cement": 430, "slag": 0, "fly_ash": 0, "water": 165, "superplasticizer": 4.3,
            "coarse_agg": 1170, "fine_agg": 640},
}
GRADE_TARGET = {"M20": 20.0, "M25": 25.0, "M30": 30.0, "M40": 40.0}


def co2(mix):
    """kg CO2e per m3, plus per-ingredient breakdown."""
    parts = {k: round(mix.get(k, 0.0) * EF[k], 3) for k in FEATURES}
    return round(sum(parts.values()), 1), parts


def cost(mix):
    """Rs per m3, plus per-ingredient breakdown."""
    parts = {k: round(mix.get(k, 0.0) * COST[k], 2) for k in FEATURES}
    return round(sum(parts.values()), 0), parts


def mix_stats(mix):
    """Engineering ratios a civil engineer will immediately look for."""
    binder = mix["cement"] + mix["slag"] + mix["fly_ash"]
    total = sum(mix.get(k, 0.0) for k in FEATURES)
    return {
        "binder": round(binder, 1),
        "total_mass": round(total, 1),
        "w_b_ratio": round(mix["water"] / binder, 3) if binder > 0 else None,
        "scm_fraction": round((mix["slag"] + mix["fly_ash"]) / binder, 3) if binder > 0 else None,
    }
