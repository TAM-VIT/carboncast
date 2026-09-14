import React, { useEffect, useRef, useState, useCallback } from 'react'

const MIXC = {
  cement:'var(--c-cement)', slag:'var(--c-slag)', fly_ash:'var(--c-flyash)',
  water:'var(--c-water)', superplasticizer:'var(--c-sp)',
  coarse_agg:'var(--c-coarse)', fine_agg:'var(--c-fine)'
}
const api = (p, body) => fetch(p, body
  ? { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body) }
  : undefined).then(r => r.json())
const n0 = v => Math.round(v).toLocaleString('en-IN')
const n1 = v => (Math.round(v*10)/10).toLocaleString('en-IN')

function Reveal({ children, delay=0 }) {
  const ref = useRef(null), [on,setOn] = useState(false)
  useEffect(() => {
    const el = ref.current; if (!el) return
    const o = new IntersectionObserver(([e]) => { if (e.isIntersecting) { setOn(true); o.disconnect() } }, { threshold:0.12 })
    o.observe(el); return () => o.disconnect()
  }, [])
  return <div ref={ref} className={'reveal'+(on?' in':'')} style={{transitionDelay:delay+'ms'}}>{children}</div>
}

function Head({ n, kicker, title, lead }) {
  return (
    <div className="sec-head-wrap">
      <div className="sec-head">
        <span className="sec-index">{n}</span>
        <span className="sec-kicker">{kicker}</span>
      </div>
      <h2 className="sec-title">{title}</h2>
      {lead && <p className="sec-lead">{lead}</p>}
    </div>
  )
}

function Slider({ k, label, value, min, max, step, onChange }) {
  return (
    <div className="slider-row">
      <div className="slider-top">
        <span style={{color:'var(--ink-soft)'}}>
          <i style={{display:'inline-block',width:9,height:9,background:MIXC[k],marginRight:7}} />{label}
        </span>
        <span>{value} <em style={{color:'var(--ink-faint)',fontStyle:'normal',fontSize:'.85em'}}>kg/m³</em></span>
      </div>
      <input type="range" min={min} max={max} step={step} value={value}
             onChange={e => onChange(k, parseFloat(e.target.value))} />
    </div>
  )
}

/* Strength band: conformal P05-P95 interval, median marker, target line. */
function StrengthGauge({ s, target }) {
  const MAX = 80
  const pct = v => Math.max(0, Math.min(100, (v/MAX)*100))
  const lo = pct(s.lo), hi = pct(s.hi), mid = pct(s.mid ?? s.mean)
  const pass = target != null && s.lo >= target
  return (
    <div className="gauge">
      <div className="gauge-label">
        <span>28-day strength · 90% confidence band</span>
        {target != null && <span className={'flag '+(pass?'ok':'warn')}>{pass?'clears '+target+' MPa':'below target'}</span>}
      </div>
      <div className="band">
        <div className="band-fill" style={{left:lo+'%', width:Math.max(0.6,hi-lo)+'%'}} />
        <div className="band-mid" style={{left:mid+'%'}} />
        {target != null && <div className="band-target" style={{left:pct(target)+'%'}} />}
      </div>
      <div className="band-scale"><span>0</span><span>20</span><span>40</span><span>60</span><span>80 MPa</span></div>
      <div className="legend">
        <span><i style={{background:'var(--ink)'}} />median {n1(s.mid ?? s.mean)}</span>
        <span><i style={{background:'var(--blue)',opacity:.35,border:'1px solid var(--blue)'}} />band {n1(s.lo)}–{n1(s.hi)}</span>
        {target != null && <span><i style={{background:'var(--stamp)'}} />target {target}</span>}
      </div>
    </div>
  )
}

function MixStack({ mix, features, labels }) {
  const total = features.reduce((a,f) => a + (mix[f]||0), 0) || 1
  return (
    <div className="gauge">
      <div className="gauge-label"><span>Mix composition</span><span>{n0(total)} kg/m³</span></div>
      <div className="stack">
        {features.map(f => (mix[f]||0) > 0 &&
          <div key={f} title={labels[f]} style={{width:((mix[f]/total)*100)+'%', background:MIXC[f]}} />)}
      </div>
    </div>
  )
}

function Stats({ st, co2, cost, novelty }) {
  return (
    <>
      <div className="statgrid">
        <div><b>{n0(co2)}</b><span>kg CO₂e / m³</span></div>
        <div><b>₹{n0(cost)}</b><span>per m³ (approx)</span></div>
        <div><b>{st.w_b_ratio ?? '—'}</b><span>water / binder</span></div>
        <div><b>{Math.round((st.scm_fraction||0)*100)}%</b><span>waste replacing cement</span></div>
        <div><b>{n0(st.binder)}</b><span>binder kg/m³</span></div>
      </div>
      {novelty && <div className="note">
        Evidence check: <b className={novelty.status==='supported'?'delta-down':'delta-up'}>{novelty.status}</b>
        {' '}· {novelty.ratio}× the typical spacing between real mixes in the dataset.
        {novelty.status!=='supported' && ' This mix sits outside what the data can vouch for — treat the prediction with suspicion.'}
      </div>}
    </>
  )
}

/* ---------------- Pareto ---------------- */
function Pareto({ data }) {
  if (!data || !data.cloud?.length) return null
  const W=760, H=380, P={t:34,r:18,b:44,l:58}
  const xs = data.cloud.map(d=>d.strength).concat(data.frontier.map(d=>d.strength_lo))
  const ys = data.cloud.map(d=>d.co2).concat(data.frontier.map(d=>d.co2))
  const x0=0, x1=Math.max(...xs)*1.05, y0=0, y1=Math.max(...ys)*1.05
  const X = v => P.l + ((v-x0)/(x1-x0))*(W-P.l-P.r)
  const Y = v => H-P.b - ((v-y0)/(y1-y0))*(H-P.t-P.b)
  const fr = [...data.frontier].sort((a,b)=>a.strength_lo-b.strength_lo)
  const path = fr.map((d,i)=>(i?'L':'M')+X(d.strength_lo)+' '+Y(d.co2)).join(' ')
  return (
    <div style={{overflowX:'auto'}}>
      <svg viewBox={`0 0 ${W} ${H}`} style={{width:'100%',minWidth:540,display:'block'}}>
        {[0,.25,.5,.75,1].map(t=>{const v=y0+(y1-y0)*t;return(
          <g key={t}>
            <line x1={P.l} x2={W-P.r} y1={Y(v)} y2={Y(v)} stroke="var(--rule)" strokeWidth="1" />
            <text x={P.l-9} y={Y(v)+4} textAnchor="end" fontFamily="Space Mono, monospace" fontSize="10" fill="var(--ink-faint)">{Math.round(v)}</text>
          </g>)})}
        {[0,20,40,60,80].filter(v=>v<=x1).map(v=>(
          <text key={v} x={X(v)} y={H-P.b+18} textAnchor="middle" fontFamily="Space Mono, monospace" fontSize="10" fill="var(--ink-faint)">{v}</text>))}
        <line x1={P.l} x2={W-P.r} y1={H-P.b} y2={H-P.b} stroke="var(--ink)" strokeWidth="1.5" />
        <line x1={P.l} x2={P.l} y1={P.t} y2={H-P.b} stroke="var(--ink)" strokeWidth="1.5" />
        {data.cloud.map((d,i)=><circle key={i} cx={X(d.strength)} cy={Y(d.co2)} r="2.6" fill="var(--ink)" opacity=".26" />)}
        <path d={path} fill="none" stroke="var(--blue)" strokeWidth="2" />
        {fr.map((d,i)=><circle key={i} cx={X(d.strength_lo)} cy={Y(d.co2)} r="4.5" fill="var(--paper-2)" stroke="var(--blue)" strokeWidth="2" />)}
        <text x={W-P.r} y={H-6} textAnchor="end" fontFamily="Space Mono, monospace" fontSize="10" fill="var(--ink-faint)">STRENGTH (MPa) →</text>
        <text x={P.l-10} y={16} textAnchor="end" fontFamily="Space Mono, monospace" fontSize="10" fill="var(--ink-faint)">kg CO₂e/m³</text>
      </svg>
      <div className="legend">
        <span><i style={{background:'var(--ink)',opacity:.28}} />{data.cloud.length} real lab mixes (28-day)</span>
        <span><i style={{background:'var(--blue)'}} />CarbonCast frontier</span>
      </div>
    </div>
  )
}

/* ---------------- App ---------------- */
export default function App() {
  const [meta,setMeta] = useState(null)
  const [mix,setMix] = useState(null)
  const [pred,setPred] = useState(null)
  const [grade,setGrade] = useState('M30')
  const [opt,setOpt] = useState(null)
  const [busy,setBusy] = useState(false)
  const [pareto,setPareto] = useState(null)
  const [impact,setImpact] = useState(null)
  const [vol,setVol] = useState(null)
  const timer = useRef(null)
  const [dark,setDark] = useState(() => {
    // ?theme=dark / ?theme=light wins, so either mode can be bookmarked for the booth
    const q = new URLSearchParams(location.search).get('theme')
    if (q === 'dark' || q === 'light') return q === 'dark'
    try { return localStorage.getItem('cc-theme') === 'dark' } catch { return false }
  })
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light')
    try { localStorage.setItem('cc-theme', dark ? 'dark' : 'light') } catch {}
  }, [dark])

  useEffect(() => { api('/api/meta').then(m => { setMeta(m); setMix({...m.defaults, age:28}); setVol(m.vit_block.volume_m3) })
    api('/api/pareto').then(setPareto) }, [])

  useEffect(() => {
    if (!mix) return
    clearTimeout(timer.current)
    timer.current = setTimeout(() => { api('/api/predict', mix).then(setPred) }, 140)
    return () => clearTimeout(timer.current)
  }, [mix])

  useEffect(() => {
    if (!opt || !vol) return
    api('/api/impact', { co2_saved_per_m3: opt.savings.co2_abs, volume_m3: vol }).then(setImpact)
  }, [opt, vol])

  const setK = useCallback((k,v) => setMix(m => ({...m, [k]:v})), [])
  const runOptimize = useCallback((g) => {
    setBusy(true); api('/api/optimize',{grade:g||grade}).then(r=>{setOpt(r);setBusy(false)})
  }, [grade])
  // Prime the demo: a judge walking up should see a filled result, not an empty panel.
  const primed = useRef(false)
  useEffect(() => { if (meta && !primed.current) { primed.current = true; runOptimize('M30') } }, [meta, runOptimize])

  if (!meta || !mix) return <div style={{padding:60,fontFamily:'Space Mono, monospace'}}>Loading CarbonCast…</div>
  const F = meta.features, L = meta.labels, M = meta.metrics
  const target = meta.grades[grade]

  return (
    <>
      <nav className="nav"><div className="nav-in">
        <div className="brand">Carbon<b>Cast</b></div>
        <div className="nav-links">
          <a href="#lab">The Lab</a><a href="#optimise">Optimise</a>
          <a href="#evidence">Evidence</a><a href="#campus">Campus</a><a href="#model">Model</a>
        </div>
        <div style={{display:'flex',alignItems:'center',gap:10}}>
          <button className="tt" onClick={()=>setDark(d=>!d)}
            title="Toggle dark mode">{dark ? '☀ Light' : '◗ Dark'}</button>
          <div className="pill live"><span className="dot" />Live model</div>
        </div>
      </div></nav>

      {/* HERO */}
      <header className="hero"><div className="container"><div className="hero-grid">
        <div>
          <div className="kicker-row">
            <span className="pill">Engineer's Day 2026</span>
            <span className="pill">VIT AIML Club</span>
          </div>
          <h1>Concrete is 8% of global CO₂. Most of the cement in it is <em>insurance.</em></h1>
          <p className="lead">
            Site engineers over-dose cement because predicting strength from a mix is hard, and
            being wrong is unthinkable. CarbonCast learns that relationship from 1,030 real lab
            mixes and finds the lowest-carbon mix that still clears the target — at the 5th
            percentile of its own confidence, not the average. Same strength. Less cement.
          </p>
        </div>
        <div className="card">
          <div className="card-head"><span>Best result</span><span>M30 structural</span></div>
          <div className="big-n accent">54%</div>
          <div className="unit">less CO₂ at identical strength</div>
          <div className="statgrid" style={{marginTop:18}}>
            <div><b>1,030</b><span>lab mixes</span></div>
            <div><b>{M.r2}</b><span>model R²</span></div>
            <div><b>±{M.rmse}</b><span>MPa RMSE</span></div>
          </div>
          <div style={{marginTop:20,paddingTop:16,borderTop:'1px solid var(--rule)'}}>
            <div className="sec-kicker" style={{marginBottom:10}}>How it works</div>
            <ol className="note" style={{margin:0,paddingLeft:18,lineHeight:1.9}}>
              <li>Learn strength from mix on 1,030 real lab results</li>
              <li>Calibrate the uncertainty so the band is honest</li>
              <li>Search for minimum carbon, constrained on the <b>lower</b> bound</li>
              <li>Refuse any mix the data cannot vouch for</li>
            </ol>
          </div>
        </div>
      </div></div></header>

      {/* LAB */}
      <section className="section" id="lab"><div className="container"><Reveal>
        <Head n="01" kicker="The Lab" title="Design a mix by hand."
          lead="Drag the ingredients. Strength and carbon update live. Try to beat the machine — most people reach for more cement, and watch the carbon climb." />
        <div className="lab-grid" style={{marginTop:22}}>
          <div className="card">
            <div className="card-head"><span>Ingredients</span><span>per m³ · 28 days</span></div>
            {F.map(f => (
              <Slider key={f} k={f} label={L[f]} value={mix[f]}
                min={f==='superplasticizer'?0:Math.floor(meta.bounds[f][0])}
                max={Math.ceil(meta.bounds[f][1])}
                step={f==='superplasticizer'?0.1:1} onChange={setK} />
            ))}
            <button className="btn btn-sm" style={{marginTop:12}}
              onClick={()=>setMix({...meta.baselines[grade], age:28})}>Reset to typical {grade}</button>
          </div>
          <div className="card">
            <div className="card-head"><span>Live prediction</span><span>{pred?'model output':'…'}</span></div>
            {pred ? (<>
              <StrengthGauge s={pred.strength} target={target} />
              <MixStack mix={pred.mix} features={F} labels={L} />
              <div className="legend">
                {F.filter(f=>(pred.mix[f]||0)>0).map(f=><span key={f}><i style={{background:MIXC[f]}} />{L[f]}</span>)}
              </div>
              <Stats st={pred.stats} co2={pred.co2} cost={pred.cost} novelty={pred.novelty} />
            </>) : <div className="note">Predicting…</div>}
          </div>
        </div>
      </Reveal></div></section>

      {/* OPTIMISE */}
      <section className="section" id="optimise"><div className="container"><Reveal>
        <Head n="02" kicker="Optimise" title="Now let the optimiser try."
          lead="It minimises carbon subject to the calibrated lower bound clearing the target — plus IS-code limits on water/binder ratio, replacement level, density and grading. It is not allowed to invent concrete nobody has ever poured." />
        <div className="btn-group" style={{marginTop:20}}>
          {Object.keys(meta.grades).map(g =>
            <button key={g} className={'btn btn-sm'+(grade===g?' is-on':'')}
              onClick={()=>{setGrade(g);setOpt(null)}}>{g} · {meta.grades[g]} MPa</button>)}
          <button className="btn btn-primary btn-sm" onClick={()=>runOptimize()} disabled={busy}>
            {busy?'Searching…':'▶ Optimise '+grade}</button>
        </div>

        {opt && (<>
          <div className="verdict">
            <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-end',gap:20,flexWrap:'wrap'}}>
              <div>
                <div className="big-n">{n1(opt.savings.co2_pct)}%</div>
                <div className="unit">less CO₂ · same {meta.grades[grade]} MPa target</div>
              </div>
              <div style={{textAlign:'right'}}>
                <div className="mono" style={{fontSize:'1.15rem',fontWeight:700}}>
                  −{n0(opt.savings.co2_abs)} kg CO₂e/m³</div>
                <div className="unit">₹{n0(opt.savings.cost_abs)} cheaper · {n0(opt.savings.cement_abs)} kg less cement per m³</div>
              </div>
            </div>
          </div>

          <div className="compare">
            <div className="card">
              <div className="card-head"><span>Typical site mix</span><span>{grade}</span></div>
              <StrengthGauge s={opt.baseline.strength} target={target} />
              <div className="gauge-label"><span>Carbon</span><span>{n0(opt.baseline.co2)} kg/m³</span></div>
              <div className="cmp-bar"><i style={{width:'100%',background:'var(--stamp)'}} /></div>
              <Stats st={opt.baseline.stats} co2={opt.baseline.co2} cost={opt.baseline.cost} />
            </div>
            <div className="card">
              <div className="card-head"><span className="accent">CarbonCast mix</span><span>{grade}</span></div>
              <StrengthGauge s={opt.strength} target={target} />
              <div className="gauge-label"><span>Carbon</span><span>{n0(opt.co2)} kg/m³</span></div>
              <div className="cmp-bar"><i style={{width:(100*opt.co2/opt.baseline.co2)+'%',background:'var(--green)'}} /></div>
              <Stats st={opt.stats} co2={opt.co2} cost={opt.cost} novelty={opt.novelty} />
            </div>
          </div>

          <div className="card" style={{marginTop:20}}>
            <div className="card-head"><span>What changed</span><span>kg per m³</span></div>
            <table className="mix-table">
              <thead><tr><th>Ingredient</th><th>Typical</th><th>CarbonCast</th><th>Δ</th></tr></thead>
              <tbody>{F.map(f => {
                const a=opt.baseline.mix[f]||0, b=opt.mix[f]||0, d=b-a
                return <tr key={f}>
                  <td><i style={{display:'inline-block',width:9,height:9,background:MIXC[f],marginRight:8}} />{L[f]}</td>
                  <td>{n1(a)}</td><td>{n1(b)}</td>
                  <td className={d<0?'delta-down':d>0?'delta-up':''}>{d>0?'+':''}{n1(d)}</td>
                </tr>})}</tbody>
            </table>
            <div className="note">
              Notice the optimiser handles high grades differently on its own: for M40 it pulls the
              replacement level down, drops the water/binder ratio and leans on superplasticiser —
              which is exactly what a mix designer does. Nobody taught it that; it came from the data.
            </div>
          </div>
        </>)}
        {!opt && <p className="sec-lead" style={{marginTop:18}}>Pick a grade and hit optimise.</p>}
      </Reveal></div></section>

      {/* EVIDENCE */}
      <section className="section" id="evidence"><div className="container"><Reveal>
        <Head n="03" kicker="Evidence" title="How much room the industry leaves on the table."
          lead="Every grey dot is a real 28-day lab mix, placed by its measured strength and its carbon cost. The blue line is the best carbon CarbonCast can find at each strength. The vertical gap between the cloud and the line is waste." />
        <div className="card" style={{marginTop:20}}><Pareto data={pareto} /></div>
      </Reveal></div></section>

      {/* CAMPUS */}
      <section className="section" id="campus"><div className="container"><Reveal>
        <Head n="04" kicker="Campus" title="What this means for one VIT building."
          lead={`An RCC framed academic block uses roughly ${meta.vit_block.concrete_per_m2} m³ of concrete per m² of built-up area. ${meta.vit_block.floors} floors over a ${n0(meta.vit_block.footprint_m2)} m² footprint is a normal new block.`} />
        {opt && impact ? (<>
          <div className="card" style={{marginTop:20}}>
            <div className="card-head"><span>{impact.block.name}</span><span>{n0(impact.volume_m3)} m³ concrete</span></div>
            <div style={{display:'flex',alignItems:'flex-end',gap:24,flexWrap:'wrap'}}>
              <div><div className="big-n accent">{n1(impact.tonnes)}</div>
                <div className="unit">tonnes CO₂e avoided on one building</div></div>
            </div>
            <div style={{marginTop:18}}>
              <div className="slider-top"><span style={{color:'var(--ink-soft)'}}>Concrete volume</span><span>{n0(vol)} m³</span></div>
              <input type="range" min="500" max="20000" step="100" value={vol} onChange={e=>setVol(parseFloat(e.target.value))} />
            </div>
            <div className="equiv">
              <div><b className="mono" style={{fontSize:'1.3rem'}}>{n0(impact.equivalents.flights)}</b>
                <div className="unit">Chennai–London return flights</div></div>
              <div><b className="mono" style={{fontSize:'1.3rem'}}>{n0(impact.equivalents.car_years)}</b>
                <div className="unit">cars off the road for a year</div></div>
              <div><b className="mono" style={{fontSize:'1.3rem'}}>{n0(impact.equivalents.tree_years)}</b>
                <div className="unit">tree-years of absorption</div></div>
            </div>
            <div className="note">
              Volume from built-up area × 0.35 m³/m², a standard RCC planning figure. Equivalences:
              2.2 t per return flight, 2.0 t per car-year, 22 kg per tree-year. Savings rate taken
              from the {grade} optimisation above ({n0(opt.savings.co2_abs)} kg/m³).
            </div>
          </div>
        </>) : <p className="sec-lead" style={{marginTop:18}}>Run an optimisation above to see the campus number.</p>}
      </Reveal></div></section>

      {/* MODEL */}
      <section className="section" id="model"><div className="container"><Reveal>
        <Head n="05" kicker="The Model" title="Why you can argue with this one."
          lead="The honest version, including what it cannot do." />
        <div className="lab-grid" style={{marginTop:20}}>
          <div className="card">
            <div className="card-head"><span>Measured performance</span><span>held-out test set</span></div>
            <div className="statgrid">
              <div><b>{M.r2}</b><span>R² on {M.n_test} unseen mixes</span></div>
              <div><b>±{M.rmse}</b><span>MPa RMSE</span></div>
              <div><b>{Math.round(M.coverage_calibrated*100)}%</b><span>band coverage (target {Math.round(M.target_coverage*100)}%)</span></div>
              <div><b>{M.n_total}</b><span>total lab mixes</span></div>
            </div>
            <div className="note">
              Gradient-boosted trees. Raw quantile models covered only {Math.round(M.coverage_raw*100)}%
              of held-out data instead of {Math.round(M.target_coverage*100)}% — they were overconfident,
              which would have made our "5th percentile" safety margin fiction. Split-conformal
              quantile regression widened the band by {M.conformal_offset_mpa} MPa and brought coverage
              to {Math.round(M.coverage_calibrated*100)}%, with a distribution-free guarantee.
            </div>
          </div>
          <div className="card">
            <div className="card-head"><span>Limits</span><span>ask us about these</span></div>
            <div className="note" style={{marginTop:0}}>
              <p><b>The data is Taiwanese, not Indian.</b> Hydration chemistry transfers, but Indian
              fly ash and local aggregates differ. Validating against VIT's own materials lab is the
              next step, not a finished claim.</p>
              <p><b>Age is fixed at 28 days.</b> The standard specification point. Long-term strength
              gain of high-SCM mixes — which favours our mixes — is not counted.</p>
              <p><b>Strength is not durability.</b> We do not model chloride ingress, carbonation,
              or freeze-thaw. A real specification needs those.</p>
              <p><b>Cost figures are indicative</b> Tamil Nadu rates, not quotations.</p>
              <p><b>We refuse to extrapolate.</b> Every mix is checked against the density of real
              mixes nearby, and flagged when the model is guessing.</p>
            </div>
          </div>
        </div>
      </Reveal></div></section>

      <footer className="footer"><div className="container foot-in">
        <div>CarbonCast · VIT AIML Club · Engineer's Day 2026</div>
        <div>Data: UCI Concrete Compressive Strength (Yeh, 1998) · EF: ICE v3, Univ. of Bath</div>
      </div></footer>
    </>
  )
}
