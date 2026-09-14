# CarbonCast: the pitch

**For anyone staffing the booth. You do not need to know anything about concrete or
machine learning to use this. Read the first two sections and you can run the demo.**

---

## 1. The thing you need to understand first

Concrete is the most used material on earth after water. It is made of sand, gravel,
water, and **cement**. Cement is the grey powder that glues it all together.

Cement is also an environmental disaster. Making one kilogram of cement releases close to
one kilogram of CO2. Cement alone is about **8% of all human carbon emissions**. If cement
were a country, it would be the third largest emitter on the planet, behind only China and
the USA.

Here is the part most people do not know. About half those emissions do not come from
burning fuel. They come from the chemical reaction itself. You heat limestone, it breaks
down, and CO2 comes out. That means **you cannot fix cement with solar panels or wind
power**. The carbon is baked into the chemistry.

So we need to use less cement. And there is an obvious way to do it.

Two industrial waste products, **fly ash** (left over from coal power plants) and **GGBS
slag** (left over from steel furnaces), can replace a large share of the cement in
concrete. They are waste. Nobody burned anything extra to make them. Their carbon cost is
almost zero.

**So why doesn't every construction site already do this?**

Because getting it wrong means a building falls down. Concrete must hit a strength target,
measured in MPa, and predicting the strength of a mix before you pour it is genuinely
hard. There are seven ingredients and they interact in complicated ways. So engineers play
it safe and add extra cement as insurance.

That insurance is invisible, it is enormous, and it is poured into every structure in the
country.

**CarbonCast finds the insurance and gives it back.**

---

## 2. The 30-second version

> "Concrete is 8% of global CO2, and cement is the reason. Half of that is the chemical
> reaction itself, so you can't fix it with renewable energy, you have to use less cement.
> Engineers already know that industrial waste can replace cement, but they over-dose
> cement anyway because predicting concrete strength is hard and being wrong means a
> building fails.
>
> We trained a model on 1,030 real lab tests to predict strength from a mix, then searched
> for the lowest-carbon mix that still hits the target. For standard M30 structural
> concrete we cut carbon by 54% at the same strength, and it comes out cheaper.
>
> On one new academic block on this campus, that's 977 tonnes of CO2."

That is the whole pitch. If you say nothing else, say that.

---

## 3. The 90-second demo, step by step

**Step 1. Point at the headline.**
"Concrete is 8% of global CO2. Most of the cement in it is insurance."
Let them read it. Do not talk over it.

**Step 2. Hand them the sliders. This is the important bit.**
"These are the seven ingredients in concrete. Try to design a mix that hits 30 MPa."

Then **stop talking and let them do it.** Almost everyone reaches for the cement slider,
because more cement means more strength and that is the intuition. Watch the carbon number
climb as they drag it.

That moment, where they personally cause the carbon to go up, is the demo. Do not narrate
over it. Do not rush them.

**Step 3. Hit "Optimise M30".**
"Same 30 MPa target. Our mix. 54% less carbon, and about 1,200 rupees cheaper per cubic
metre."

Point at the two panels side by side. Red bar is the conventional mix. Green bar is ours.
Point at the "What changed" table: 225 kg less cement per cubic metre, replaced with slag
and fly ash.

**Step 4. Answer the safety question before they ask it.**
This is the single most important sentence in the whole pitch:

> "You're about to ask what happens if the model is wrong. So we don't design against the
> model's average guess. We design against the bottom of its confidence range, the 5th
> percentile. The safety margin is engineered in, not hoped for."

Say this **before** they raise it. It changes how the rest of the conversation goes,
because it shows you already thought about the thing they were about to challenge you on.

**Step 5. Scale it to something they can feel.**
Scroll to the campus section.
"One new academic block on this campus. 977 tonnes of CO2. That's 444 Chennai to London
return flights."

Numbers in MPa mean nothing to most people. Flights do.

---

## 4. Questions you will get

**"How accurate is the model?"**
R-squared of 0.92 on 206 mixes it had never seen, about 4.5 MPa of error. But accuracy
alone is not the point. The point is that we know **how uncertain** it is, and we design
to the pessimistic end of that.

**"What if the model is wrong and the building fails?"**
We never use the average prediction. We use the calibrated 5th percentile, so 95% of the
time reality is better than what we designed for. And when we first built this, the
uncertainty was overconfident. The model claimed a 90% confidence range that actually
only contained 69% of real results. We fixed it with a technique called conformal
prediction, which widened the range by about 3 MPa and brought it to 87%, with a
mathematical guarantee that does not depend on the data being nicely behaved.

*(If they look impressed by that answer, they are probably a good judge. Keep going.)*

**"Couldn't the optimiser just invent a mix that doesn't work?"**
That is exactly what it did the first time we ran it. It found mixes with almost no cement
that the model claimed were fine, because it had wandered into territory no lab has ever
tested. So we added a guard: every mix is checked against how close it is to the 1,030
real mixes, and the optimiser is penalised for straying. The screen tells you whether a
mix is "supported" or "extrapolating". It reports on itself.

**"Is this Indian data?"**
No. It is the UCI concrete dataset, which is Taiwanese. We say that on the site rather
than hiding it. The chemistry of cement hydration transfers, but Indian fly ash and local
aggregates genuinely differ, so validating against VIT's own materials lab is the honest
next step. **Say this before they catch it.** Naming your own limitation is the strongest
move available to you.

**"Is strength the only thing that matters in concrete?"**
No, and we do not claim otherwise. Durability matters too: chloride ingress, carbonation,
freeze-thaw. We do not model any of that. This is a mix design aid, not a specification.

**"Why does M40 only save 38% when M30 saves 54%?"**
Higher strength needs more real cement, so there is less waste to cut. But notice the
optimiser worked that out by itself. For M40 it lowered the waste replacement to 47%,
dropped the water ratio, and added superplasticiser, which is exactly what a professional
mix designer does for high strength concrete. Nobody programmed that in. It learned it
from the data.

**The best question anyone can ask: "your conventional M40 doesn't even hit 40 MPa."**
Correct, and it is our favourite result. The typical site M40 mix has a 5th percentile
strength of 38.6 MPa, so it does not reliably make its own grade. Ours clears 40.1 with
38% less carbon. The conventional mix is over-carbonised **and** under-performing at the
same time.

---

## 5. If you get asked something you don't know

Say: **"I don't know, that's a good question."** Then either bring over a teammate, or
say "here's how we'd find out."

Do not guess. Do not bluff. A judge who catches you making something up will discount
everything else you said, including the parts that were true. Admitting a gap costs you
almost nothing. Getting caught costs you the whole booth.

---

## 6. Things not to say

- **Do not say it is "AI".** Say what it actually is: a model trained on 1,030 lab tests
  plus a constrained search. "AI" makes a technical judge suspicious.
- **Do not claim it is ready for construction.** It is a design aid that needs lab
  validation. Overclaiming is the fastest way to lose a civil engineer.
- **Do not say "we used machine learning to solve climate change."** Say the specific
  thing: 54% less carbon in one concrete mix, validated on held-out data, with stated limits.
- **Do not read the screen aloud.** They can read. Add the thing that is not written down.

---

## 7. The numbers, memorised

| Thing | Number |
|---|---|
| Cement's share of global CO2 | ~8% |
| Lab mixes trained on | 1,030 |
| Model accuracy | R² 0.92, ±4.5 MPa |
| M30 carbon cut | **54%** |
| M30 cost saving | ₹1,227 per m³ |
| Cement removed (M30) | 225 kg per m³ |
| One VIT academic block | **977 tonnes CO2** |
| That equals | 444 Chennai-London return flights |

If you remember only two: **54%** and **977 tonnes**.
