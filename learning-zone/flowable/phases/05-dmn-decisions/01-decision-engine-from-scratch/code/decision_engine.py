"""A decision engine in ~80 lines: inputs, rules, outputs.

A decision table is data, not code: each rule is a row of predicates over the
inputs plus the outputs to return when they all match. The engine is just
"find the matching rows". Everything else DMN adds — hit policies, types,
governance — sits on top of this core (lesson 02 onward).

Run: python3 decision_engine.py
"""
from dataclasses import dataclass


@dataclass
class Rule:
    when: list       # one predicate per input column; None = any value ("-")
    then: dict       # output name -> value


@dataclass
class DecisionTable:
    key: str
    inputs: list     # input variable names, in column order
    rules: list      # ordered Rule rows

    def matches(self, rule, context):
        return all(
            pred is None or pred(context[name])
            for name, pred in zip(self.inputs, rule.when)
        )

    def evaluate(self, context):
        """FIRST hit policy for now: the first matching row wins (lesson 02
        builds the full family)."""
        for rule in self.rules:
            if self.matches(rule, context):
                return dict(rule.then)
        return None                       # no rule fired: the caller must decide


# The credit decision the loan-triage process has been hard-coding since
# Phase 1 (${score >= 700} on a gateway) — now a table the business can read:
CREDIT = DecisionTable(
    key="creditDecision",
    inputs=["score", "amount"],
    rules=[
        # score              amount                        -> decision, rate %
        Rule([lambda s: s >= 750, lambda a: a <= 1_000_000],
             {"decision": "auto-approve", "rate": 10.5}),
        Rule([lambda s: s >= 700, lambda a: a <= 500_000],
             {"decision": "auto-approve", "rate": 11.5}),
        Rule([lambda s: s >= 650, None],
             {"decision": "manual-review", "rate": 13.0}),
        Rule([lambda s: s < 650, None],
             {"decision": "decline", "rate": None}),
    ],
)


if __name__ == "__main__":
    cases = [
        {"score": 780, "amount": 800_000},    # strong file, mid ticket
        {"score": 720, "amount": 800_000},    # good file, ticket too big for auto
        {"score": 660, "amount": 200_000},    # thin file -> human
        {"score": 610, "amount": 100_000},    # decline
    ]
    for ctx in cases:
        out = CREDIT.evaluate(ctx)
        print(f"score={ctx['score']:>3} amount={ctx['amount']:>9,} -> {out}")

    # The property that makes tables reviewable: the WHOLE policy is one
    # data structure. Questions like "which inputs can ever auto-approve?"
    # are queries, not code archaeology:
    autos = [r.then for r in CREDIT.rules if r.then["decision"] == "auto-approve"]
    print(f"\n{len(autos)} auto-approve row(s); best rate {min(r['rate'] for r in autos)}%")
