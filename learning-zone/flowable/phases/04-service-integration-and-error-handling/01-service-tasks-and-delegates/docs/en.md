# Service tasks: delegates, expressions, delegate expressions

> **Motto** — A service task is a seam, not a place. The model names *what* happens,
> and one of three wiring styles decides *where* the code lives.

*Part of Phase 04 — Service integration & error handling. Concept reading:
[Principle 6 — separate the flow from the work](../../../../foundations/process-automation-principles.md).*

## The Problem

Phase 1's service tasks used inline expressions
(`${execution.setVariable('decision', ...)}`). That's fine for demos, but
unacceptable for a bureau call with authentication, timeouts, and logging. That
logic belongs in real classes in your codebase. Every team then argues the same
question: how does a box in the diagram find your Java code? Flowable gives three
answers, and choosing the wrong one costs you testability or Spring injection.

## The Concept

<style>
.dgm-std{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #a63d40;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-std-chip{position:absolute;top:-11px;left:24px;background:#a63d40;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(166,61,64,.28)}
.dgm-std h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-std-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-std-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-std-branches{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.dgm-std-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-std-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-std-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-std-b.accent{background:#faeceb;border-color:#e3b3ad}
.dgm-std-b.accent h6{color:#7a2c2e}
.dgm-std-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-std-b.blue h6{color:#0550ae}
.dgm-std-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-std-b.green h6{color:#1a614f}
.dgm-std-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-std-b.red h6{color:#82061e}
.dgm-std-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-std-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-std{padding:20px 16px 18px}.dgm-std-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-std">
  <span class="dgm-std-chip">Three ways to wire a service task</span>
  <h4>class, delegateExpression, or expression — pick one binding style</h4>
  <p class="dgm-std-sub">All three end up calling your code; they differ in how Spring resolves the bean.</p>
  <div class="dgm-std-q">serviceTask 'bureauCall'</div>
  <div class="dgm-std-branches">
    <div class="dgm-std-b accent">
      <h6>flowable:class</h6>
      <p>Engine instantiates the class directly</p>
    </div>
    <div class="dgm-std-b blue">
      <h6>flowable:delegateExpression</h6>
      <p>Resolves a Spring bean implementing JavaDelegate</p>
    </div>
    <div class="dgm-std-b green">
      <h6>flowable:expression</h6>
      <p>Calls any bean method, stores the return value</p>
    </div>
  </div>
</div>


| Wiring | Gets Spring injection? | Needs JavaDelegate? | Use when |
| :-- | :-- | :-- | :-- |
| `flowable:class` | no — engine calls `new` | yes | plain-engine (non-Spring) setups, simple stateless glue |
| `flowable:delegateExpression` | **yes** — it *is* a bean | yes | the default in Spring Boot apps |
| `flowable:expression` | yes | **no** — any method | wrapping existing services untouched: `${bureauGateway.score(pan)}` |

Whichever style you choose, two contracts hold:

1. **The delegate runs inside the engine's transaction** (Phase 2, lesson 03). Throw,
   and the segment rolls back. Mark the task async, and the throw becomes a
   retrying job instead.
2. **Failures come in two kinds, and the *type* you throw decides the routing.** A
   `BpmnError` is a *business* outcome the diagram should show, like no bureau
   record routing to a reject path. Error boundary events catch it (lesson 04). Any
   other exception is a *technical* failure that triggers rollback and retry
   (lesson 05). Mixing these up is the single most common Flowable design bug.

## Use It

All three styles side by side in
[`code/Delegates.java`](../code/Delegates.java). The Spring-bean style you'll use most:

```java
@Component("bureauDelegate")
public static class SpringBureauDelegate implements JavaDelegate {
    private final BureauGateway gateway;

    public SpringBureauDelegate(BureauGateway gateway) {
        this.gateway = gateway;
    }

    @Override
    public void execute(DelegateExecution execution) {
        execution.setVariable("score",
                gateway.score((String) execution.getVariable("pan")));
    }
}
```

This wires up as
`<serviceTask id="bureauCall" flowable:delegateExpression="${bureauDelegate}"/>`.
Here's the business-vs-technical failure contract, in code:

```java
if (score == -1) {
    throw new BpmnError("NO_BUREAU_RECORD", "PAN has no bureau file");  // route on it
}
// bureau down? just let the IOException/RuntimeException fly -> rollback + retry
```

Testing is the quiet win of the expression style. `${bureauGateway.score(pan)}` calls
a plain method, so your existing unit tests already cover it, and the process test
only has to assert the wiring.

## Ship It

This lesson ships [`code/Delegates.java`](../code/Delegates.java), a reference file
showing all three wirings with the failure contract annotated. Copy it into a Spring
Boot service alongside Phase 2's starter.

## Check Yourself

**Q1.** Your delegate needs a repository injected. Which wiring?

- A) `flowable:class` — add a setter
- B) `flowable:delegateExpression` — the delegate is a Spring bean with normal injection
- C) `flowable:expression` on a static method
- D) any; injection always works

<details><summary>Answer</summary>B — `flowable:class` bypasses Spring entirely (the
engine calls `new`), so nothing is injected. Delegate-expression resolves a managed
bean.</details>

**Q2.** The bureau returns "no record exists for this PAN". You should…

- A) throw `RuntimeException` so the job retries
- B) return normally and hope a gateway checks
- C) throw `BpmnError("NO_BUREAU_RECORD")` so the model routes it explicitly
- D) log and continue

<details><summary>Answer</summary>C — "no record" is a business outcome, not a
malfunction, and retrying won't change it. It belongs on the diagram as an error
boundary path.</details>

**Q3.** A delegate writes a variable, then throws a plain exception. The variable is…

- A) saved — writes are immediate
- B) rolled back with the rest of the transaction segment
- C) saved only if the task was async
- D) moved to history

<details><summary>Answer</summary>B — Phase 2's rules apply: the delegate runs inside
the segment's transaction, and everything in it rolls back together.</details>

**Challenge.** Wrap an existing class you own with the expression style — no
JavaDelegate, no engine imports. Write down what you'd lose versus a delegate:
access to `DelegateExecution`, local variables, BpmnError codes. That trade-off is
the real decision between styles 2 and 3.

## Related

- Next: [The HTTP task](../../02-http-task/docs/en.md)
- Failure routing: [BPMN errors vs technical errors](../../03-bpmn-errors-vs-technical/docs/en.md)
