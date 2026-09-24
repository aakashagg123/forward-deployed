"""Hit policies: what happens when several rules match — or none do.

Extends lesson 01's engine with the policies you'll actually meet:
  UNIQUE   at most one rule may match; overlap is a TABLE BUG -> error
  FIRST    row order is load-bearing; first match wins
  ANY      overlaps allowed only if all matching rules agree
  COLLECT  return ALL matches (optionally aggregated: SUM/MIN/MAX/COUNT)

Run: python3 hit_policies.py
"""
from dataclasses import dataclass


@dataclass
class Rule:
    when: list
    then: dict


@dataclass
class DecisionTable:
    key: str
    inputs: list
    rules: list
    hit_policy: str = "UNIQUE"
    aggregation: str = None            # for COLLECT: SUM | MIN | MAX | COUNT

    def _matching(self, context):
        out = []
        for rule in self.rules:
            if all(p is None or p(context[n])
                   for n, p in zip(self.inputs, rule.when)):
                out.append(rule.then)
        return out

    def evaluate(self, context):
        hits = self._matching(context)

        if self.hit_policy == "UNIQUE":
            if len(hits) > 1:
                raise ValueError(
                    f"{self.key}: UNIQUE violated — {len(hits)} rules match {context}")
            return hits[0] if hits else None

        if self.hit_policy == "FIRST":
            return hits[0] if hits else None

        if self.hit_policy == "ANY":
            if hits and any(h != hits[0] for h in hits):
                raise ValueError(
                    f"{self.key}: ANY violated — matching rules disagree: {hits}")
            return hits[0] if hits else None

        if self.hit_policy == "COLLECT":
            if self.aggregation is None:
                return hits                                   # the full list
            (field,) = {k for h in hits for k in h}           # single-output tables
            values = [h[field] for h in hits]
            return {
                "SUM": sum(values),
                "MIN": min(values, default=None),
                "MAX": max(values, default=None),
                "COUNT": len(values),
            }[self.aggregation]

        raise ValueError(f"unknown hit policy {self.hit_policy}")


# A UNIQUE table with a subtle overlap bug: rows 1 and 2 both cover score 750.
RISK_BAND = DecisionTable(
    key="riskBand", inputs=["score"], hit_policy="UNIQUE",
    rules=[
        Rule([lambda s: s >= 750], {"band": "prime"}),
        Rule([lambda s: 700 <= s <= 750], {"band": "near-prime"}),   # bug: <= 750
        Rule([lambda s: s < 700], {"band": "subprime"}),
    ],
)

# COLLECT+SUM: processing fee = sum of every applicable component.
FEES = DecisionTable(
    key="processingFees", inputs=["channel", "amount"],
    hit_policy="COLLECT", aggregation="SUM",
    rules=[
        Rule([None, None], {"fee": 500}),                             # base, always
        Rule([lambda c: c == "branch", None], {"fee": 250}),          # branch surcharge
        Rule([None, lambda a: a > 1_000_000], {"fee": 1000}),         # big-ticket diligence
    ],
)


if __name__ == "__main__":
    print("clean input :", RISK_BAND.evaluate({"score": 800}))
    try:
        RISK_BAND.evaluate({"score": 750})
    except ValueError as e:
        print("overlap bug :", e)

    print("fees online :", FEES.evaluate({"channel": "online", "amount": 300_000}))
    print("fees branch :", FEES.evaluate({"channel": "branch", "amount": 2_000_000}))

    # Same rows under FIRST would silently return 'prime' for 750 — the bug
    # ships instead of failing. That is the real difference between policies:
    first = DecisionTable(RISK_BAND.key, RISK_BAND.inputs, RISK_BAND.rules, "FIRST")
    print("same table, FIRST:", first.evaluate({"score": 750}), "(bug hidden)")
