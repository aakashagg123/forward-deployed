# Signals vs messages: broadcast vs point-to-point

> **Motto** — A message finds *the one* instance that owns the conversation; a signal
> reaches *everyone* who cares — confuse them and you either drop deliveries or stampede
> your engine.

*Part of Phase 07 — Events, timers & messaging. Concept lesson — no code required.*

## The Problem

Two events land in your loan platform on the same afternoon. First, the bureau's
callback for application APP-002: exactly one instance must receive it, and
delivering it twice or to a sibling would be a correctness bug. Second, RBI revises
the repo rate: *every* in-flight application holding a floating-rate offer must
recalculate. Same engine, same "something happened outside" shape, but opposite
delivery semantics. BPMN gives each its own primitive. Models that use the wrong one
work fine in the demo, then fail at the first duplicate or the first
thousand-instance broadcast.

## The Concept

<style>
.dgm-svm{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #a63d40;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-svm-chip{position:absolute;top:-11px;left:24px;background:#a63d40;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(166,61,64,.28)}
.dgm-svm h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-svm-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-svm-cols{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}
.dgm-svm-col{border-radius:12px;padding:12px 13px;border:1.5px solid}
.dgm-svm-col.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-svm-col.accent{background:#faeceb;border-color:#e3b3ad}
.dgm-svm-col.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-svm-col.green{background:#dafbe1;border-color:#aceebb}
.dgm-svm-col h6{margin:0 0 8px;font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.3px}
.dgm-svm-col.neutral h6{color:#59636e}
.dgm-svm-col.accent h6{color:#7a2c2e}
.dgm-svm-col.blue h6{color:#0550ae}
.dgm-svm-col.green h6{color:#1a614f}
.dgm-svm-item{background:#ffffff;border:1px solid #e5e9ef;border-radius:8px;padding:6px 9px;font-size:10px;
  color:#1f2328;line-height:1.35;margin-bottom:5px}
.dgm-svm-item:last-child{margin-bottom:0}
.dgm-svm-link{display:flex;justify-content:center;color:#8c959f;font-size:9.5px;font-weight:700;
  text-transform:uppercase;letter-spacing:.3px;padding:6px 0}
@media (max-width:640px){.dgm-svm{padding:20px 16px 18px}.dgm-svm-cols{grid-template-columns:1fr}}
</style>
<div class="dgm-svm">
  <span class="dgm-svm-chip">Point-to-point vs. broadcast</span>
  <h4>One subscription wakes, or every subscription wakes</h4>
  <p class="dgm-svm-sub">Pick signal when 0 or N listeners is normal; pick message when exactly one must exist.</p>
  <div class="dgm-svm-cols">
    <div class="dgm-svm-col accent">
      <h6>Message — point-to-point</h6>
      <div class="dgm-svm-item">Delivery {name + correlation key}</div>
      <div class="dgm-svm-item">Exactly ONE subscription — 0 matches is an error to surface, 2 matches is ambiguity to refuse</div>
    </div>
    <div class="dgm-svm-col blue">
      <h6>Signal — broadcast</h6>
      <div class="dgm-svm-item">Signal {name}</div>
      <div class="dgm-svm-item">EVERY waiting catch fires — 0 listeners is fine, N listeners moves N tokens</div>
    </div>
  </div>
</div>


| | Message | Signal |
| :-- | :-- | :-- |
| Addressing | name **+ correlation key** | name only |
| Receivers | exactly one | zero to N — all of them |
| Zero receivers means | a problem (late/mis-keyed) — surface it | nothing to do — normal |
| Carries payload | yes, into the one instance's variables | engine-level: use sparingly; receivers usually re-read state |
| Scope | always engine-wide, keyed | engine-wide, or *instance-scoped* (a signal thrown and caught within one instance) |
| Typical use | bureau callback, e-sign webhook, payment confirmation | rate change, "compliance freeze all onboarding", cache invalidation between branches |

Two design rules fall out:

1. **If you need a correlation key, it's a message.** The moment "which instance?"
   has an answer, broadcast is wrong. A signal named `bureauCallback-APP-002` — a
   real anti-pattern found in real models — is a message wearing a signal costume,
   and it defeats duplicate detection.
2. **If zero listeners is fine, it's a signal.** Messages *must* land; signals are
   fire-and-forget by design. Here is the operational warning too: a signal caught
   by 10,000 instances moves 10,000 tokens, on a synchronous throw, in one
   transaction. Broadcast to large populations needs async continuations (Phase 2)
   between the catch and any heavy work.

Both also come as **event subprocess** triggers (lesson 05) — "while this scope is
active, react to X." This is where signals shine: a `complianceFreeze` signal event
subprocess in every onboarding process is one drawn element per model, not a
boundary on every task.

## Ship It

This lesson ships
[`outputs/signal-message-cheatsheet.md`](../outputs/signal-message-cheatsheet.md) —
the decision table plus the model-review flags.

## Check Yourself

**Q1.** "When the checker approves batch B-77, continue that batch's process." Message
or signal?

- A) signal — approvals are broadcasts
- B) message — there's a correlation key (B-77) and exactly one intended receiver
- C) either works
- D) timer

<details><summary>Answer</summary>B — "that batch's" is a correlation key wearing
prose. One intended receiver always means a message.</details>

**Q2.** A signal is thrown and no instance is waiting. What should happen?

- A) an error — deliveries must land
- B) nothing, by design — zero listeners is a normal outcome for broadcast
- C) the signal is queued until someone subscribes
- D) a new instance starts

<details><summary>Answer</summary>B — this is the semantic core of the split. If
zero receivers worries you, you wanted a message — or a signal *start* event, which
does create instances.</details>

**Q3.** The model review finds `<signal name="paymentConfirmed-${orderId}"/>`. The
verdict?

- A) fine — dynamic names are expressive
- B) an anti-pattern: a keyed, single-receiver event is a message; the costume defeats correlation-error detection
- C) fine if orders are unique
- D) prefer a timer

<details><summary>Answer</summary>B — per-key signal names re-implement correlation
without its safety rails: no ambiguity refusal, no unmatched-delivery
surface.</details>

**Challenge.** Sweep a process model you own (or the capstone, next phase) and label
every external interaction M or S using the two rules. Then find the one that's
neither — a *conditional* event or a polling loop — and write down why it resisted
classification. That's usually where an event registry (next lesson) belongs.

## Related

- Next: [The event registry](../../04-event-registry/docs/en.md)
- Previous: [Message events](../../02-message-events/docs/en.md)
