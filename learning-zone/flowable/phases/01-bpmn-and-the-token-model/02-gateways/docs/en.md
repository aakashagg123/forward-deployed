# Gateways: exclusive, parallel, inclusive

> **Motto** — Gateways don't do work; they route tokens — choose one path, take all
> paths, or wait for paths to come back together.

*Part of Phase 01 — BPMN & the token model. Concept reading:
[Principle 1](../../../../foundations/process-automation-principles.md).*

## The Problem

Yesterday's engine could only walk a straight line. Real processes branch —
"auto-approve if the score clears 700, otherwise send to manual review" — and
they parallelise — "run the credit check and the KYC check at the same time, then
continue when *both* are done." You can't model either of those with
single-outgoing-flow nodes. Branching is ambiguous (which flow does the token
take?) and joining is impossible (how do you know both branches finished?).

## The Concept

BPMN's answer is a small family of routing nodes. The three you'll actually use:

<style>
.dgm-gwx{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #a63d40;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-gwx-chip{position:absolute;top:-11px;left:24px;background:#a63d40;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(166,61,64,.28)}
.dgm-gwx h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-gwx-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-gwx-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-gwx-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-gwx-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-gwx-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-gwx-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-gwx-b.accent{background:#faeceb;border-color:#e3b3ad}
.dgm-gwx-b.accent h6{color:#7a2c2e}
.dgm-gwx-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-gwx-b.blue h6{color:#0550ae}
.dgm-gwx-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-gwx-b.green h6{color:#1a614f}
.dgm-gwx-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-gwx-b.red h6{color:#82061e}
.dgm-gwx-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-gwx-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-gwx{padding:20px 16px 18px}.dgm-gwx-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-gwx">
  <span class="dgm-gwx-chip">Exclusive gateway (XOR)</span>
  <h4>Pick exactly one path</h4>
  <p class="dgm-gwx-sub">The token takes yes or no — never both.</p>
  <div class="dgm-gwx-q">score ≥ 700?</div>
  <div class="dgm-gwx-branches">
    <div class="dgm-gwx-b green">
      <h6>Yes</h6>
      <p>Auto approve</p>
    </div>
    <div class="dgm-gwx-b accent">
      <h6>No</h6>
      <p>Manual review</p>
    </div>
  </div>
</div>


<style>
.dgm-gwp{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #a63d40;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-gwp-chip{position:absolute;top:-11px;left:24px;background:#a63d40;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(166,61,64,.28)}
.dgm-gwp h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-gwp-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-gwp-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-gwp-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-gwp-n.accent{background:#faeceb;border-color:#e3b3ad;color:#7a2c2e}
.dgm-gwp-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-gwp-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-gwp-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-gwp-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-gwp-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-gwp{padding:20px 16px 18px}.dgm-gwp-row{flex-direction:column}}
.dgm-gwp-cols{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}
.dgm-gwp-col{border-radius:12px;padding:12px 13px;border:1.5px solid}
.dgm-gwp-col.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-gwp-col.accent{background:#faeceb;border-color:#e3b3ad}
.dgm-gwp-col.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-gwp-col.green{background:#dafbe1;border-color:#aceebb}
.dgm-gwp-col h6{margin:0 0 8px;font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.3px}
.dgm-gwp-col.neutral h6{color:#59636e}
.dgm-gwp-col.accent h6{color:#7a2c2e}
.dgm-gwp-col.blue h6{color:#0550ae}
.dgm-gwp-col.green h6{color:#1a614f}
.dgm-gwp-item{background:#ffffff;border:1px solid #e5e9ef;border-radius:8px;padding:6px 9px;font-size:10px;
  color:#1f2328;line-height:1.35;margin-bottom:5px}
.dgm-gwp-item:last-child{margin-bottom:0}
.dgm-gwp-link{display:flex;justify-content:center;color:#8c959f;font-size:9.5px;font-weight:700;
  text-transform:uppercase;letter-spacing:.3px;padding:6px 0}
@media (max-width:640px){.dgm-gwp{padding:20px 16px 18px}.dgm-gwp-cols{grid-template-columns:1fr}}
</style>
<div class="dgm-gwp">
  <span class="dgm-gwp-chip">Parallel gateway (AND)</span>
  <h4>Fork now, wait for every branch before continuing</h4>
  <p class="dgm-gwp-sub">Both paths run; the join doesn't fire until credit check AND KYC check complete.</p>
  <div class="dgm-gwp-row"><div class="dgm-gwp-n accent">⥂ Fork</div></div>
  <div class="dgm-gwp-cols">
    <div class="dgm-gwp-col blue">
      <h6>Credit check</h6>
    </div>
    <div class="dgm-gwp-col green">
      <h6>KYC check</h6>
    </div>
  </div>
  <div class="dgm-gwp-row" style="margin-top:8px"><div class="dgm-gwp-n accent">⥃ Join — waits for both</div><span class="dgm-gwp-arr">→</span><div class="dgm-gwp-n">Continue</div></div>
</div>


| Gateway | Split behaviour | Join behaviour | Token count |
| :-- | :-- | :-- | :-- |
| **Exclusive (XOR)** | first flow whose condition is true (else the default flow) | pass-through — any arriving token continues | unchanged |
| **Parallel (AND)** | one token per outgoing flow, no conditions | wait until a token has arrived on *every* incoming flow, merge to one | 1 → n, then n → 1 |
| **Inclusive (OR)** | one token per *true* condition (1..n paths) | wait for every token that could still arrive | 1 → k, then k → 1 |

Two rules save you hours of debugging:

1. **Conditions live on the flows, not in the gateway.** The exclusive gateway is
   just the point where flow guards are evaluated, in order, with one flow marked
   as the guardless default. No matching flow and no default means a dead
   instance.
2. **A parallel join is a counter.** It fires when the number of tokens that
   arrived equals the number of incoming flows. Draw a parallel fork with three
   branches into a join with two incoming flows, and you've built a process that
   never completes. That's the most common modelling bug in BPMN.

## Build It

Flows grow a guard — `(source, target, guard)` — and the engine grows two routing
functions. [`code/gateways.py`](../code/gateways.py):

```python
def take_exclusive(inst, node):
    """Exactly one way out: first flow whose guard passes; guardless flow = default."""
    conditional = [(t, g) for t, g in inst.process.outgoing(node.name) if g]
    default = [t for t, g in inst.process.outgoing(node.name) if g is None]
    for target, guard in conditional:
        if guard(inst.variables):
            return [target]
    assert default, f"{node.name}: no condition matched and no default flow"
    return [default[0]]

def take_parallel(inst, node):
    """Fork: token per outgoing flow. Join: wait until all incoming tokens arrive."""
    arrived = inst.tokens.count(node.name)
    if arrived < inst.process.incoming_count(node.name):
        return None                                   # join still waiting
    for _ in range(arrived - 1):                      # merge: n tokens become 1
        inst.tokens.remove(node.name)
    return [t for t, _ in inst.process.outgoing(node.name)]
```

The demo is a loan triage: parallel credit + KYC checks, join, then an exclusive route
on the score:

```
$ python3 gateways.py
score 720 -> auto-approved
score 640 -> waiting at ['review']
after review -> manually-approved
```

Watch the token count in the log: 1 token forks to 2, and the join merges 2 back
to 1. "Parallel" here means *both branches will be walked before the join fires*
— not threads. Real engines work the same way: parallel gateways are about token
bookkeeping, and actual concurrency only appears with async continuations
([Phase 2, lesson 03](../../../02-the-engine-state-and-transactions/03-transactions-and-async/docs/en.md)).

## Use It

The same loan triage in Flowable's XML dialect — conditions are
[UEL](https://www.flowable.com/open-source/docs/bpmn/ch04-API#expressions) expressions
on the flows, and the default flow is an attribute on the gateway:

```xml
<exclusiveGateway id="route" default="toReview"/>
<sequenceFlow id="toAuto" sourceRef="route" targetRef="auto">
  <conditionExpression xsi:type="tFormalExpression">${score >= 700}</conditionExpression>
</sequenceFlow>
<sequenceFlow id="toReview" sourceRef="route" targetRef="review"/>

<parallelGateway id="fork"/>
<parallelGateway id="join"/>
```

You'll write a full deployable model with exactly this shape in
[lesson 03](../../03-bpmn-xml-by-hand/docs/en.md).

## Ship It

This lesson ships the gateway-aware engine as a module:
[`code/gateways.py`](../code/gateways.py) — a drop-in successor to lesson 01's
`token_engine.py`. Phase 2 builds persistence on top of it.

## Check Yourself

**Q1.** An exclusive gateway has three conditional flows; none of their conditions is
true and no default flow is set. What happens?

- A) the token takes the first flow anyway
- B) the token takes all three flows
- C) the instance is stuck/errors — there is no legal way forward
- D) the instance completes

<details><summary>Answer</summary>C — no matching condition and no default means the
token has nowhere to go. Flowable throws an error; our toy engine asserts. Always
model a default flow.</details>

**Q2.** A parallel join has 2 incoming flows. One branch's token has arrived; the other
branch is parked at a user task. The join…

- A) fires with the one token after a timeout
- B) waits — it fires only when tokens have arrived on all incoming flows
- C) cancels the other branch
- D) duplicates the arrived token

<details><summary>Answer</summary>B — a parallel join is a counter over incoming flows.
Until every branch delivers its token, the tokens that already arrived sleep at
the join.</details>

**Q3.** How many tokens exist right after a parallel fork with 3 outgoing flows?

- A) 1
- B) 2
- C) 3
- D) depends on conditions

<details><summary>Answer</summary>C — one per outgoing flow, unconditionally. (An
*inclusive* gateway is the one that forks per true condition.)</details>

**Challenge.** Implement the inclusive gateway: fork a token per *true* guard, and
make the join wait only for the branches that were actually taken. You'll need to
remember, at fork time, how many tokens the join should expect. That bookkeeping
is exactly why inclusive joins are the hairiest code in every real BPM engine.

## Related

- Next: [BPMN 2.0 XML by hand](../../03-bpmn-xml-by-hand/docs/en.md)
- Previous: [Tokens & sequence flow](../../01-tokens-and-sequence-flow/docs/en.md)
