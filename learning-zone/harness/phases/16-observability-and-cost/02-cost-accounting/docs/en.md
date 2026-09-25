# Token & cost accounting

> **Motto** — Every call has a price — attribute it per session, feature, and tenant.

*Part of Phase 16 — Observability & Cost.*

## The Problem

Agents spend money per token, and a coding agent can burn a lot of tokens. Without **cost
accounting** you can't answer basic questions: what did this run cost, which feature is
expensive, is this tenant profitable. You also can't enforce budgets (Phase 14) in any
meaningful way. The harness must convert token usage into dollars, then attribute that cost
along the dimensions you care about.

## The Concept

<style>
.dgm-ca{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-ca-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-ca h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-ca-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-ca-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-ca-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-ca-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-ca-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-ca-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-ca-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-ca-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-ca-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-ca{padding:20px 16px 18px}.dgm-ca-row{flex-direction:column}}
</style>
<div class="dgm-ca">
  <span class="dgm-ca-chip">Tokens become dollars, dollars become attribution</span>
  <h4>Usage → price → cost per call → attributed to session, feature, or tenant</h4>
  <p class="dgm-ca-sub">Attribution is what turns a total cost number into an actionable one.</p>
  <div class="dgm-ca-row">
    <div class="dgm-ca-n neutral">Usage: input/output tokens per call</div>
    <span class="dgm-ca-arr">→</span>
    <div class="dgm-ca-n accent">Price by model</div>
    <span class="dgm-ca-arr">→</span>
    <div class="dgm-ca-n blue">Cost per call</div>
    <span class="dgm-ca-arr">→</span>
    <div class="dgm-ca-n green">Attribute: session / feature / tenant</div>
  </div>
</div>


Pricing is per-model and per-direction — input, output, and cache reads each have their own
rate. Attribution tags each cost with who or what it was for.

## Build It

`code/cost.py` — a cost accountant with per-model pricing and attribution:

```python
PRICES = {  # USD per 1M tokens (illustrative — verify current pricing)
    "claude-opus-5": {"in": 5.0, "out": 25.0},
    "claude-haiku-4-5-20251001": {"in": 0.8, "out": 4.0},
}

class CostMeter:
    def __init__(self):
        self.by_tag = {}

    def record(self, model, in_tokens, out_tokens, tag="default"):
        p = PRICES[model]
        cost = (in_tokens * p["in"] + out_tokens * p["out"]) / 1_000_000
        self.by_tag[tag] = self.by_tag.get(tag, 0.0) + cost
        return cost

    def report(self):
        return {tag: round(c, 6) for tag, c in self.by_tag.items()}
```

```python
m = CostMeter()
m.record("claude-opus-5", 10_000, 2_000, tag="feature:refactor")
m.record("claude-haiku-4-5-20251001", 50_000, 5_000, tag="feature:search")
print(m.report())     # cost attributed per feature
```

Tagging each `record` call lets you slice spend by feature, session, or tenant. That
breakdown feeds pricing decisions and per-tenant budgets.

## Use It

The SDK returns real `usage` data (input, output, and cache tokens) on every response. Feed
that data to a meter like this one, tagged by session, feature, or tenant. For a Claude Code
or Codex user, this is why long autonomous runs cost what they do. It's also why model
routing (Phase 14) matters — a cheaper model on routine work is a direct line-item saving.
Always verify current prices.

## Ship It

[`code/cost.py`](../../02-cost-accounting/code/cost.py) — a token→cost meter with attribution.

## Check Yourself

**Q1.** Cost depends on…

- A) total tokens only
- B) model + direction (input vs. output, cache reads), times token counts
- C) wall-clock time
- D) number of tools

<details><summary>Answer</summary>B — per-model, per-direction pricing.</details>

**Q2.** Why attribute cost by tag (feature/tenant)?

- A) decoration
- B) to answer which feature/tenant is expensive and enforce per-tenant budgets
- C) it's required
- D) no reason

<details><summary>Answer</summary>B — attribution drives pricing and budgets.</details>

**Challenge.** Add cache-read pricing (cheaper than fresh input) and show the savings when a
big stable prefix is cached (Phase 1 L8).

## Related

- Builds on: Phase 1 — [Tokens](../../../01-llm-io-foundations/02-tokens-and-context-window/docs/en.md), Phase 14 — [Budgets](../../../14-reliability-engineering/04-budgets/docs/en.md)
- Next: [Latency](../../03-latency/docs/en.md)
- Other tracks: [Cost attribution](../../../../../content/04-evals-observability/cost-attribution.md) · [Incidents & postmortems](../../../../../technical-product-management/incidents-and-postmortems.md) — attributing spend and operating what you measure.
- [Roadmap](../../../../ROADMAP.md)
