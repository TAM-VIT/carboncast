"""Build print-ready HTML for the A3 booth poster and the A4 pitch handout."""
import json, io, os
import pandas as pd
import qrcode, qrcode.image.svg
import markdown

B = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend")
pre = json.load(open(os.path.join(B, "artifacts", "precomputed.json")))
met = json.load(open(os.path.join(B, "artifacts", "metrics.json")))
REPO = "https://github.com/TAM-VIT/carboncast"

# ---------- QR ----------
buf = io.BytesIO()
qrcode.make(REPO, image_factory=qrcode.image.svg.SvgPathImage, box_size=10, border=0).save(buf)
qr_svg = buf.getvalue().decode()
qr_svg = qr_svg[qr_svg.index("<svg"):].replace("<svg", '<svg style="width:100%;height:100%"', 1)

# ---------- Pareto ----------
df = pd.read_csv(os.path.join(B, "data", "concrete.csv"))
df = df[df["age"] == 28]
EF = {"cement":0.912,"slag":0.079,"fly_ash":0.008,"water":0.000344,
      "superplasticizer":1.88,"coarse_agg":0.0048,"fine_agg":0.0051}
cloud = [(float(r["strength"]), sum(float(r[k])*v for k,v in EF.items())) for _,r in df.iterrows()]
fr = sorted(pre["pareto"], key=lambda d: d["strength_lo"])

W,H,P = 1000, 420, dict(t=26,r=20,b=42,l=66)
x1 = max(max(s for s,_ in cloud), max(d["strength_lo"] for d in fr))*1.04
y1 = max(max(c for _,c in cloud), max(d["co2"] for d in fr))*1.05
X = lambda v: P["l"] + (v/x1)*(W-P["l"]-P["r"])
Y = lambda v: H-P["b"] - (v/y1)*(H-P["t"]-P["b"])
g = []
for t in (0,.25,.5,.75,1):
    v = y1*t
    g.append(f'<line x1="{P["l"]}" x2="{W-P["r"]}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="#c5c9cf" stroke-width="1"/>')
    g.append(f'<text x="{P["l"]-9}" y="{Y(v)+4:.1f}" text-anchor="end" font-family="Space Mono,monospace" font-size="13" fill="#848a93">{v:.0f}</text>')
for v in (0,20,40,60,80):
    if v <= x1:
        g.append(f'<text x="{X(v):.1f}" y="{H-P["b"]+20}" text-anchor="middle" font-family="Space Mono,monospace" font-size="13" fill="#848a93">{v}</text>')
g.append(f'<line x1="{P["l"]}" x2="{W-P["r"]}" y1="{H-P["b"]}" y2="{H-P["b"]}" stroke="#191b1f" stroke-width="1.8"/>')
g.append(f'<line x1="{P["l"]}" x2="{P["l"]}" y1="{P["t"]}" y2="{H-P["b"]}" stroke="#191b1f" stroke-width="1.8"/>')
for s,c in cloud:
    g.append(f'<circle cx="{X(s):.1f}" cy="{Y(c):.1f}" r="3" fill="#191b1f" opacity="0.22"/>')
g.append('<path d="'+" ".join(("M" if i==0 else "L")+f"{X(d['strength_lo']):.1f} {Y(d['co2']):.1f}" for i,d in enumerate(fr))+'" fill="none" stroke="#2540d9" stroke-width="3"/>')
for d in fr:
    g.append(f'<circle cx="{X(d["strength_lo"]):.1f}" cy="{Y(d["co2"]):.1f}" r="5.5" fill="#f5f6f8" stroke="#2540d9" stroke-width="3"/>')
g.append(f'<text x="{P["l"]-9}" y="16" text-anchor="end" font-family="Space Mono,monospace" font-size="13" fill="#848a93">kg CO₂e/m³</text>')
g.append(f'<text x="{W-P["r"]}" y="{H-6}" text-anchor="end" font-family="Space Mono,monospace" font-size="13" fill="#848a93">STRENGTH (MPa) →</text>')
pareto_svg = f'<svg viewBox="0 0 {W} {H}" style="width:100%;display:block">' + "".join(g) + "</svg>"

rows = "".join(
    f"<tr><td><b>{g}</b></td><td>{pre['grades'][g]['baseline']['co2']:.0f}</td>"
    f"<td>{pre['grades'][g]['co2']:.0f}</td>"
    f"<td class='cut'>{pre['grades'][g]['savings']['co2_pct']:.0f}%</td>"
    f"<td>{pre['grades'][g]['stats']['scm_fraction']*100:.0f}%</td></tr>"
    for g in ["M20","M25","M30","M40"])

SHARED = """
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=Space+Mono:wght@400;700&display=swap');
:root{--paper:#e9eaed;--paper-3:#cdd0d5;--ink:#191b1f;--ink-soft:#474c54;--ink-faint:#848a93;
 --rule:#c5c9cf;--blue:#2540d9;--green:#15795c;--stamp:#c0392b;
 --steel:linear-gradient(180deg,#f5f6f8 0%,#eaecef 46%,#e1e4e8 100%);}
*{box-sizing:border-box;-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{margin:0;background:var(--paper);color:var(--ink);font-family:'Fraunces',Georgia,serif;line-height:1.5}
.mono{font-family:'Space Mono',monospace}
.kick{font-family:'Space Mono',monospace;font-size:8.5pt;letter-spacing:.18em;text-transform:uppercase;color:var(--ink-faint)}
.card{border:1.5px solid var(--ink);background:var(--steel);box-shadow:5px 5px 0 var(--paper-3),inset 0 1px 0 rgba(255,255,255,.9);padding:12px 14px}
h1,h2,h3{font-weight:600;letter-spacing:-.02em;margin:0}
em{font-style:italic;color:var(--blue)}
"""

poster = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@page{{size:A3 portrait;margin:0}}
{SHARED}
body{{width:297mm;height:420mm;padding:13mm 14mm;overflow:hidden;
 background-image:linear-gradient(rgba(25,27,31,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(25,27,31,.045) 1px,transparent 1px);
 background-size:34px 34px}}
.top{{display:flex;justify-content:space-between;align-items:baseline;
 border-bottom:2px solid var(--ink);padding-bottom:7px;margin-bottom:13px}}
.brand{{font-family:'Space Mono',monospace;font-weight:700;font-size:15pt;letter-spacing:.14em;text-transform:uppercase}}
.brand b{{color:var(--blue)}}
h1{{font-size:38pt;line-height:1.03;max-width:19ch;margin-bottom:9px}}
.lead{{font-size:11.5pt;color:var(--ink-soft);max-width:60ch;margin:0}}
.hero{{display:grid;grid-template-columns:1.32fr .68fr;gap:13px;align-items:stretch;margin-bottom:13px}}
.bignum{{font-family:'Space Mono',monospace;font-weight:700;font-size:52pt;line-height:.88;
 letter-spacing:-.05em;color:var(--blue)}}
.bignum.sm{{font-size:31pt;color:var(--ink)}}
.unit{{font-family:'Space Mono',monospace;font-size:8pt;letter-spacing:.13em;text-transform:uppercase;color:var(--ink-faint);margin-top:5px}}
.cols{{display:grid;grid-template-columns:1fr 1fr;gap:13px;margin-bottom:13px}}
h3{{font-size:13pt;margin-bottom:7px}}
p{{margin:0 0 7px;font-size:10pt}}
ol{{margin:0;padding-left:16px;font-size:9.5pt;line-height:1.75}}
ol b{{color:var(--blue)}}
table{{width:100%;border-collapse:collapse;font-family:'Space Mono',monospace;font-size:9.5pt}}
th{{text-align:right;font-size:7.5pt;letter-spacing:.11em;text-transform:uppercase;color:var(--ink-faint);
 font-weight:400;padding:4px 0;border-bottom:1px solid var(--rule)}}
th:first-child,td:first-child{{text-align:left}}
td{{text-align:right;padding:4.5px 0;border-bottom:1px solid var(--rule)}}
.cut{{color:var(--green);font-weight:700}}
.foot{{display:grid;grid-template-columns:1fr 128px;gap:13px;align-items:center}}
.lim{{font-size:8.5pt;color:var(--ink-soft);line-height:1.6}}
.qr{{width:112px;height:112px;background:#fff;padding:6px;border:1.5px solid var(--ink)}}
</style></head><body>

<div class="top">
  <div class="brand">Carbon<b>Cast</b></div>
  <div class="kick">VIT AIML Club &nbsp;·&nbsp; Engineer's Day 2026 &nbsp;·&nbsp; Smart Engineering for a Sustainable Future</div>
</div>

<div class="hero">
  <div>
    <h1>Concrete is 8% of global CO<sub>2</sub>. Most of the cement in it is <em>insurance.</em></h1>
    <p class="lead">Half of cement's emissions come from the chemical reaction itself, so renewables
    cannot abate them. Industrial wastes can replace much of the cement, but site engineers over-dose
    it anyway, because predicting concrete strength is hard and being wrong is unthinkable. CarbonCast
    learns that relationship from 1,030 real lab mixes and finds the lowest-carbon mix that still
    clears the target at the <b>calibrated 5th percentile, not the average</b>.</p>
  </div>
  <div class="card" style="display:flex;flex-direction:column;justify-content:center">
    <div class="bignum">54%</div><div class="unit">less CO&#8322; at identical M30 strength</div>
    <div style="height:1px;background:var(--rule);margin:11px 0"></div>
    <div class="bignum sm">977 t</div><div class="unit">CO&#8322;e saved on one VIT academic block</div>
  </div>
</div>

<div class="cols">
  <div class="card">
    <div class="kick">The problem</div>
    <h3>Invisible insurance, poured into everything</h3>
    <p>Cement is ~8% of all human CO<sub>2</sub>. If it were a country it would rank third.
    Fly ash and slag, waste from coal plants and steel furnaces, can replace much of it at
    near-zero carbon cost.</p>
    <p>They are under-used because strength prediction is hard, so engineers add cement as a
    safety buffer. That buffer is never measured. It is just poured.</p>
  </div>
  <div class="card">
    <div class="kick">The method</div>
    <h3>Optimise the margin, don't assume it</h3>
    <ol>
      <li>Learn strength from mix on <b>1,030</b> real lab results</li>
      <li><b>Calibrate</b> the uncertainty so the confidence band is honest</li>
      <li>Search for minimum carbon, constrained on the <b>lower bound</b></li>
      <li><b>Refuse</b> any mix the training data cannot vouch for</li>
    </ol>
  </div>
</div>

<div class="card" style="margin-bottom:13px">
  <div class="kick">Evidence &nbsp;·&nbsp; every grey dot is a real 28-day lab mix; the blue line is the best carbon achievable at each strength. The gap is waste.</div>
  {pareto_svg}
</div>

<div class="cols">
  <div class="card">
    <div class="kick">Results</div>
    <table><thead><tr><th>Grade</th><th>Typical</th><th>CarbonCast</th><th>Cut</th><th>Waste used</th></tr></thead>
    <tbody>{rows}</tbody></table>
    <p style="font-size:8.5pt;color:var(--ink-soft);margin-top:7px">kg CO<sub>2</sub>e per m&#179;.
    M30 is also <b>₹1,227/m&#179; cheaper</b>. The typical M40 mix has a 5th-percentile strength of
    just 38.6 MPa: it does not reliably make its own grade. Ours clears 40.1 with 38% less carbon.</p>
  </div>
  <div class="card">
    <div class="kick">The model</div>
    <table><tbody>
      <tr><td>R&#178; on {met['n_test']} unseen mixes</td><td><b>{met['r2']}</b></td></tr>
      <tr><td>RMSE</td><td><b>±{met['rmse']} MPa</b></td></tr>
      <tr><td>Raw interval coverage</td><td>{met['coverage_raw']*100:.0f}%</td></tr>
      <tr><td>After conformal calibration</td><td><b>{met['coverage_calibrated']*100:.0f}%</b> (target {met['target_coverage']*100:.0f}%)</td></tr>
    </tbody></table>
    <p style="font-size:8.5pt;color:var(--ink-soft);margin-top:7px">Gradient-boosted trees. Raw quantile
    models were overconfident, which would have made our safety margin fiction. Split-conformal quantile
    regression widened the band by {met['conformal_offset_mpa']} MPa for a distribution-free guarantee.</p>
  </div>
</div>

<div class="foot" style="margin-top:13px">
  <div class="lim">
    <span class="kick">Stated limits</span><br>
    Training data is Taiwanese, not Indian: hydration chemistry transfers, but local fly ash and
    aggregates differ, and validating against VIT's materials lab is the next step. 28-day strength only.
    Strength is not durability; chloride ingress, carbonation and freeze-thaw are not modelled. Costs are
    indicative Tamil Nadu rates. This is a mix-design aid, not a specification.<br>
    <span class="mono" style="font-size:8pt">Data: UCI Concrete Compressive Strength (Yeh 1998) · Emission factors: ICE v3, Univ. of Bath · {REPO.replace('https://','')}</span>
  </div>
  <div class="qr">{qr_svg}</div>
</div>
</body></html>"""

open("poster.html","w").write(poster)

# ---------- pitch handout ----------
body = markdown.markdown(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","PITCH.md")).read(),
                         extensions=["tables","sane_lists"])
pitch = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@page{{size:A4 portrait;margin:15mm 16mm}}
{SHARED}
body{{font-size:10.5pt;max-width:none}}
h1{{font-size:21pt;margin:0 0 4px;border-bottom:2px solid var(--ink);padding-bottom:7px}}
h2{{font-size:14pt;margin:20px 0 7px;padding-top:9px;border-top:1.5px solid var(--ink);
   page-break-after:avoid;break-after:avoid}}
h3{{font-size:11.5pt;margin:13px 0 4px;page-break-after:avoid}}
p,li{{font-size:10pt;line-height:1.58}}
blockquote{{margin:10px 0;padding:11px 15px;border-left:3px solid var(--blue);
 background:var(--steel);font-size:10.5pt}}
blockquote p{{margin:0 0 6px}} blockquote p:last-child{{margin:0}}
code{{font-family:'Space Mono',monospace;font-size:9pt;background:#dfe2e6;padding:1px 4px}}
strong{{font-weight:700}}
table{{width:100%;border-collapse:collapse;font-family:'Space Mono',monospace;font-size:9pt;margin:10px 0}}
th{{text-align:left;font-size:7.5pt;letter-spacing:.11em;text-transform:uppercase;color:var(--ink-faint);
 font-weight:400;padding:5px 6px;border-bottom:1px solid var(--rule)}}
td{{padding:5px 6px;border-bottom:1px solid var(--rule)}}
hr{{border:0;border-top:1.5px solid var(--rule);margin:18px 0}}
ul,ol{{padding-left:19px}}
li{{margin-bottom:3px}}
</style></head><body>{body}</body></html>"""
open("pitch.html","w").write(pitch)
print("html written | cloud pts:", len(cloud), "| frontier:", len(fr))
