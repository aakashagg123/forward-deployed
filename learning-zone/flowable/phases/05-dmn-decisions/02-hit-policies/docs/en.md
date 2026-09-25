# Hit policies: FIRST, UNIQUE, COLLECT and why they matter

> **Motto** — The hit policy is the table's contract about overlap. UNIQUE makes
> overlaps a caught bug, and FIRST makes them silent policy. Choose like it matters,
> because it does.

*Part of Phase 05 — DMN: decisions as tables.*

## The Problem

Lesson 01 ended on a cliff: score 780, amount ₹4 lakh, two rows match. Multiply that
by a real table — forty rows, five input columns, edited quarterly by three
different analysts — and overlaps stop being an edge case. They become a certainty.
The question is never "will rows overlap" but "what happens when they do": error,
first wins, or all of them? The DMN answer is a single declared setting on the table
— the **hit policy**. Tables copied from examples with an unconsidered `FIRST` are
how banks end up pricing the same customer two different ways depending on row
order.

## The Concept

<style>
.dgm-hp{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #a63d40;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-hp-chip{position:absolute;top:-11px;left:24px;background:#a63d40;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(166,61,64,.28)}
.dgm-hp h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-hp-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-hp-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-hp-branches{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.dgm-hp-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-hp-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-hp-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-hp-b.accent{background:#faeceb;border-color:#e3b3ad}
.dgm-hp-b.accent h6{color:#7a2c2e}
.dgm-hp-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-hp-b.blue h6{color:#0550ae}
.dgm-hp-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-hp-b.green h6{color:#1a614f}
.dgm-hp-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-hp-b.red h6{color:#82061e}
.dgm-hp-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-hp-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-hp{padding:20px 16px 18px}.dgm-hp-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-hp">
  <span class="dgm-hp-chip">Four hit policies</span>
  <h4>Which rows match the input decides what ‘hit policy’ even means</h4>
  <p class="dgm-hp-sub">The same overlapping table is a bug under UNIQUE and perfectly fine under COLLECT.</p>
  <div class="dgm-hp-q">Rules matching the input</div>
  <div class="dgm-hp-branches">
    <div class="dgm-hp-b accent">
      <h6>UNIQUE</h6>
      <p>0 or 1 may match — 2+ is an ERROR (table bug)</p>
    </div>
    <div class="dgm-hp-b blue">
      <h6>FIRST</h6>
      <p>Row order decides — reordering rows is a policy change</p>
    </div>
    <div class="dgm-hp-b green">
      <h6>ANY</h6>
      <p>Overlaps are fine if all agree — disagreement is an error</p>
    </div>
    <div class="dgm-hp-b neutral">
      <h6>COLLECT</h6>
      <p>Return all matches, optionally SUM / MIN / MAX / COUNT</p>
    </div>
  </div>
</div>


| Policy | Overlap is… | Result | Reach for it when |
| :-- | :-- | :-- | :-- |
| **UNIQUE** | a bug, caught at evaluation | the one match (or none) | classification: risk bands, eligibility — rows *should* partition the space |
| **FIRST** | intentional; order is the tie-break | first matching row | exception-then-default tables ("specific offers first, catch-all last") |
| **ANY** | tolerable redundancy | the agreed value | denormalised tables where several rows restate one truth |
| **COLLECT** | the whole point | all matches, or an aggregate | accumulation: fee components, applicable checks, SUM/COUNT pricing |

Two consequences people learn the hard way:

1. **UNIQUE is the strictest, and therefore the safest default.** It turns analyst
   mistakes (a `<=` where `<` was meant) into loud evaluation errors instead of quiet
   misclassification. Use FIRST only when "specific rules shadow general ones" is
   genuinely the mental model. Then treat *row reordering as a policy change*,
   requiring the same review as an edit.
2. **No-match is part of the contract too.** UNIQUE and FIRST returning nothing means
   the table has a hole. COLLECT returning an empty list may be perfectly normal,
   like no surcharges applied. Decide which your table means, and make the process
   route the empty case explicitly.

## Build It

[`code/hit_policies.py`](../code/hit_policies.py) extends lesson 01's engine — the
whole family is one method:

```python
if self.hit_policy == "UNIQUE":
    if len(hits) > 1:
        raise ValueError(
            f"{self.key}: UNIQUE violated — {len(hits)} rules match {context}")
    return hits[0] if hits else None
```

The demo plants a real analyst bug — a risk-band table where one row says `>= 750`
and the next says `700 <= s <= 750` — and evaluates score 750 under both policies:

```
$ python3 hit_policies.py
clean input : {'band': 'prime'}
overlap bug : riskBand: UNIQUE violated — 2 rules match {'score': 750}
fees online : 500
fees branch : 1750
same table, FIRST: {'band': 'prime'} (bug hidden)
```

Same rows, same input. UNIQUE **catches** the boundary overlap, while FIRST silently
ships whichever band happens to sit higher in the file. The COLLECT+SUM fee table
shows the accumulation case — base fee, branch surcharge, and big-ticket diligence
sum to 1750, three rows contributing to one number.

## Use It

In DMN XML the policy is one attribute (lesson 03 writes the full file):

```xml
<decisionTable id="riskBandTable" hitPolicy="UNIQUE">     <!-- default -->
<decisionTable id="feeTable" hitPolicy="COLLECT" aggregation="SUM">
```

Flowable evaluates exactly these semantics, with one operational note. A UNIQUE
violation or a no-match surfaces as an evaluation failure in the calling process — a
*technical* error on the decision task, landing in the Phase 4 pipeline (retry,
dead-letter). Retrying won't fix a table bug, which is exactly why UNIQUE violations
should page the table's owner, not ops (lesson 04).

## Ship It

This lesson ships [`code/hit_policies.py`](../code/hit_policies.py): the complete
toy DMN engine, with tables and UNIQUE/FIRST/ANY/COLLECT plus aggregation. It's
small enough to use as an oracle when a production table misbehaves.

## Check Yourself

**Q1.** A risk-band table should assign every score exactly one band. Best policy?

- A) FIRST — simplest
- B) UNIQUE — partitioning is the intent, so overlaps must be errors
- C) COLLECT — return all candidate bands
- D) ANY

<details><summary>Answer</summary>B — when rows are meant to partition the input
space, UNIQUE turns any accidental overlap into a caught bug instead of an
order-dependent answer.</details>

**Q2.** Under FIRST, an analyst drags a row up "for readability". What just happened?

- A) nothing — order is cosmetic
- B) a policy change: inputs matched by both rows now get the moved row's outputs
- C) the table becomes invalid
- D) the engine re-sorts rows anyway

<details><summary>Answer</summary>B — under FIRST, order *is* semantics. That review
burden is the hidden cost that makes UNIQUE the better default.</details>

**Q3.** Which is a natural COLLECT+SUM use?

- A) choosing an applicant's risk band
- B) totalling every fee component whose condition applies
- C) picking an interest rate
- D) validating a PAN

<details><summary>Answer</summary>B — accumulation across all applicable rows is what
COLLECT exists for. Classification and pricing pick *one* answer.</details>

**Challenge.** Write a static overlap checker for UNIQUE tables. For each pair of
rows, decide whether some input could satisfy both — for interval predicates, this
is just interval intersection. Run it on `RISK_BAND`: it should flag rows 1–2
*without evaluating anything*. You've built the validation Flowable's model editor
runs on save.

## Related

- Next: [DMN XML & the decision task](../../03-dmn-xml-and-decision-task/docs/en.md)
- Previous: [A decision engine in 80 lines](../../01-decision-engine-from-scratch/docs/en.md)
