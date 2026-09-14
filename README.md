# CarbonCast

**Low-carbon concrete mix design, constrained on calibrated uncertainty.**
VIT AIML Club · Engineer's Day 2026 · Theme: Smart Engineering for a Sustainable Future

Cement is ~8% of global CO₂ and roughly half of that comes from calcination itself, so
renewables cannot fix it. Fly ash and GGBS slag — industrial wastes — can replace much of
the cement, but site engineers over-dose cement as insurance because predicting strength
from a mix is hard. CarbonCast learns that relationship from 1,030 real lab mixes and
searches for the lowest-carbon mix that clears the strength target **at the calibrated
5th percentile, not the mean**.

Run it: `./start.sh` → http://localhost:8000 · See `RUNBOOK.md` for the booth guide.

## Results

| Grade | Typical site mix | CarbonCast | Cut | Note |
|---|---|---|---|---|
| M20 | 301 kg CO₂e/m³ | 150 | **50.1%** | |
| M25 | 319 | 156 | **51.2%** | |
| M30 | 359 | 166 | **54.0%** | ₹1,227/m³ cheaper |
| M40 | 409 | 255 | **37.6%** | baseline P05 is only 38.6 MPa — it misses its own grade |

One new VIT academic block (5,040 m³): **977 tonnes CO₂e avoided.**

## How it works

1. **Strength model** — gradient-boosted trees on the UCI Concrete Compressive Strength
   dataset (Yeh 1998). R² 0.92, RMSE 4.46 MPa on 206 held-out mixes.
2. **Calibrated uncertainty** — raw quantile models covered only 69% of held-out data
   against a 90% target. Split-conformal quantile regression (Romano et al. 2019) widens
   the band by 2.97 MPa for 87% empirical coverage with a distribution-free guarantee.
   Quantile crossing is corrected post-hoc.
3. **Carbon + cost** — ICE v3 emission factors (Univ. of Bath); indicative Tamil Nadu prices.
4. **Constrained optimisation** — differential evolution minimising CO₂ subject to:
   calibrated P05 ≥ target · ingredient bounds from data percentiles · density 2300–2600
   kg/m³ · w/b 0.28–0.70 · SCM ≤ 70% of binder · binder ≥ 300 kg/m³ · coarse:fine 1.2–2.2 ·
   kNN novelty ≤ 2× typical spacing.
5. **Evidence guard** — every mix is scored for distance to real data and labelled
   `supported` or `extrapolating`. The UI reports when the model is guessing.

## Limits (stated on the site, not buried)

Taiwanese data, not Indian · 28-day strength only · strength ≠ durability (no chloride
ingress, carbonation, freeze-thaw) · costs indicative, not quotations.

## Layout
```
backend/   carbon.py (emission factors) · train.py (models + conformal calibration)
           optimizer.py (constrained DE search) · precompute.py · app.py (FastAPI + SPA)
frontend/  Vite + React 18, hand-written CSS. No Tailwind, no chart library.
start.sh   one command, fully offline
```
