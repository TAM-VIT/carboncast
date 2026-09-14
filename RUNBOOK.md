# CarbonCast — booth runbook

## Start it

```bash
cd ~/Desktop/PROJECTS/carboncast && ./start.sh
```

Opens `http://localhost:8000`. One process, fully offline. **No venue WiFi needed.**
Stop with Ctrl+C.

If something is broken, full rebuild from scratch:
```bash
cd ~/Desktop/PROJECTS/carboncast/frontend && npm install && npm run build
cd ../backend && python3 train.py && python3 precompute.py
cd .. && ./start.sh
```

## Before you leave tonight
- [ ] Run `./start.sh` on the **actual demo laptop**, not just this one
- [ ] Drag a slider, confirm numbers move
- [ ] Click each of M20 / M25 / M30 / M40
- [ ] Set laptop to never sleep. Disable notifications. Close Slack/WhatsApp.
- [ ] Browser at 80–90% zoom so a whole section fits the screen
- [ ] Charge the laptop. Bring the charger.

## The 90-second demo

1. **Point at the headline.** "Concrete is 8% of global CO₂. Cement is the reason, and
   about half of that is the chemical reaction itself, so renewables can't fix it."
2. **Hand them the sliders.** "Design a mix. Try to hit 30 MPa." They will push cement up.
   Watch the carbon number climb. *This is the moment — let them do it, don't narrate.*
3. **Hit Optimise.** "Same 30 MPa. 54% less carbon, ₹1,227 cheaper per cubic metre."
4. **The safety answer, before they ask it.** "You're about to ask what happens if the
   model is wrong. We don't optimise against the average prediction. We optimise against
   the calibrated 5th percentile — the margin is engineered in."
5. **Scale it.** "One new academic block on this campus: 977 tonnes of CO₂. That's 444
   Chennai–London return flights."

## Questions you will get, and the answers

**"How do I know the model isn't wrong?"**
R² 0.92 on 206 unseen mixes, ±4.5 MPa. More importantly the uncertainty is *calibrated*:
raw quantile models only covered 69% of held-out data instead of 90%, so we applied
split-conformal quantile regression, widened the band by 2.97 MPa, and got 87% coverage
with a distribution-free guarantee. We design to the bottom of that band.

**"Couldn't it invent a mix that doesn't exist?"**
That was the first thing that went wrong when we built it. Every candidate is checked by
kNN distance against the 1,030 real mixes, and the optimiser is penalised for wandering
outside them. The UI says "supported" or "extrapolating" — it will tell on itself.

**"Is this Indian data?"**
No, and we say so on the site. UCI dataset, Taiwanese. Hydration chemistry transfers but
Indian fly ash and local aggregates differ. Validating against VIT's own materials lab is
the obvious next step. *Saying this first is stronger than being caught by it.*

**"Is strength enough to specify concrete?"**
No. We don't model durability — chloride ingress, carbonation, freeze-thaw. This is a mix
design aid, not a specification.

**"Why does M40 only save 38% when M30 saves 54%?"**
Higher grades need more real cement; there's less fat to cut. Note the optimiser figured
that out itself — for M40 it drops replacement to 47%, cuts the water/binder ratio to 0.35
and leans on superplasticiser. Nobody taught it that. It came from the data.

**The sharp one — "your M40 baseline fails its own target."**
Correct, and it's the best thing in the demo. The typical site M40 mix has a 5th-percentile
strength of 38.6 MPa — it doesn't reliably make its own grade. Ours clears 40.1 with 38%
less carbon. The conventional mix is over-carbonised *and* under-performing.

## If it breaks at the booth
- Page blank → hard refresh (Cmd+Shift+R)
- Numbers stuck → check the terminal is still running, rerun `./start.sh`
- Total failure → screenshots in `screenshots/`, talk over those. Don't debug in front
  of a judge; demo from the images and fix it after.
