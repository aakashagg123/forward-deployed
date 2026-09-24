# Capstone 02 — The credit decision table

> **Motto** — The policy axis nobody hard-codes twice: score × amount × employment,
> owned by credit, deployed like code.

*Part of Phase 11 — Capstone. Combines Phase 5.*

## The Project

[`outputs/loan-decision.dmn`](../outputs/loan-decision.dmn) — Phase 5's
`creditDecision` grown a third input, which is exactly how real tables evolve:

| Score | Amount | Employment | → Decision | → Rate |
| :-- | :-- | :-- | :-- | :-- |
| ≥ 750 | ≤ 10,00,000 | salaried | auto-approve | 10.5 |
| ≥ 700 | ≤ 5,00,000 | salaried | auto-approve | 11.5 |
| ≥ 750 | ≤ 5,00,000 | self-employed | auto-approve | 12.0 |
| ≥ 650 | – | – | manual-review | 13.5 |
| – | – | – | decline | 0 |

Design notes, all cash-outs of earlier lessons:

- **`hitPolicy="FIRST"`, deliberately.** The rows are exception-then-default
  (Phase 5, lesson 02's criterion), and the self-employed tightening *depends* on
  more-specific-first ordering. A salaried 760/₹8L file hits row 1. A
  self-employed 760/₹8L file falls past row 3's cap into manual review.
  Reordering these rows is a policy change, and it must be reviewed as one.
- **The catch-all decline is the completeness guarantee.** No input combination
  returns nothing, so the process's default gateway path is belt-and-braces, not
  a load-bearing hole-plug.
- **The employment axis came from governance, not engineering.** The committee's
  "self-employed needs tighter caps" lands as two rows and a new input. No Java,
  no BPMN change — just one `.dmn` redeploy. That's the asymmetry that justified
  Phase 5.

## Verify It

Transcribe the table into Phase 5's toy engine and run the golden cases before ever
deploying — the toy is the oracle:

```python
# with lesson 5.02's DecisionTable/Rule and hit_policy="FIRST"
golden = [
    ({"score": 760, "amount": 800_000, "employment": "salaried"},      "auto-approve"),
    ({"score": 760, "amount": 800_000, "employment": "self-employed"}, "manual-review"),
    ({"score": 710, "amount": 400_000, "employment": "salaried"},      "auto-approve"),
    ({"score": 660, "amount": 200_000, "employment": "self-employed"}, "manual-review"),
    ({"score": 600, "amount": 100_000, "employment": "salaried"},      "decline"),
]
```

The second case is the one that catches transcription errors — it *only* passes if
row order survived the copy.

**Challenge.** Fill in the governance card
([Phase 5, lesson 04's checklist](../../../05-dmn-decisions/04-decision-governance/outputs/decision-governance-checklist.md))
for this table: owner, ritual, the five golden cases above, and the impact-replay
query for the next band change. The capstone isn't done until the card is.
