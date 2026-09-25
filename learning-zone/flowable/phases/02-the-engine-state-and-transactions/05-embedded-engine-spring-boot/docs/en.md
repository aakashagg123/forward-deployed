# Use It: the embedded engine in Spring Boot

> **Motto** — "Embedded" means the engine is a library inside your service — same
> JVM, same datasource, same transaction. That one fact decides most of your
> architecture.

*Part of Phase 02 — The engine: state & transactions. This is the phase's **Use It**
lesson. Concept reading:
[Principle 10](../../../../foundations/process-automation-principles.md).*

## The Problem

Phase 1 drove Flowable as a separate server over REST. That's one topology. The
other — and the more common one inside product teams — is the engine
**embedded** in your own Spring Boot service: no second deployment, process
state in *your* database, service tasks calling *your* beans directly, and, the
part that changes everything, engine operations joining *your* transactions.
You need to have seen both to make the Phase 10 topology decision consciously,
rather than by default.

## The Concept

<style>
.dgm-ees{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #a63d40;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-ees-chip{position:absolute;top:-11px;left:24px;background:#a63d40;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(166,61,64,.28)}
.dgm-ees h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-ees-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-ees-cols{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}
.dgm-ees-col{border-radius:12px;padding:12px 13px;border:1.5px solid}
.dgm-ees-col.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-ees-col.accent{background:#faeceb;border-color:#e3b3ad}
.dgm-ees-col.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-ees-col.green{background:#dafbe1;border-color:#aceebb}
.dgm-ees-col h6{margin:0 0 8px;font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.3px}
.dgm-ees-col.neutral h6{color:#59636e}
.dgm-ees-col.accent h6{color:#7a2c2e}
.dgm-ees-col.blue h6{color:#0550ae}
.dgm-ees-col.green h6{color:#1a614f}
.dgm-ees-item{background:#ffffff;border:1px solid #e5e9ef;border-radius:8px;padding:6px 9px;font-size:10px;
  color:#1f2328;line-height:1.35;margin-bottom:5px}
.dgm-ees-item:last-child{margin-bottom:0}
.dgm-ees-link{display:flex;justify-content:center;color:#8c959f;font-size:9.5px;font-weight:700;
  text-transform:uppercase;letter-spacing:.3px;padding:6px 0}
@media (max-width:640px){.dgm-ees{padding:20px 16px 18px}.dgm-ees-cols{grid-template-columns:1fr}}
</style>
<div class="dgm-ees">
  <span class="dgm-ees-chip">Two deployment shapes, same engine</span>
  <h4>Standalone talks over REST; embedded shares your process and your database</h4>
  <p class="dgm-ees-sub">Same Flowable engine — the difference is the network hop and who owns the schema.</p>
  <div class="dgm-ees-cols">
    <div class="dgm-ees-col neutral">
      <h6>Standalone (Phase 1)</h6>
      <div class="dgm-ees-item">Your service — REST → flowable-rest server</div>
      <div class="dgm-ees-item">Engine DB (separate)</div>
    </div>
    <div class="dgm-ees-col accent">
      <h6>Embedded (this lesson)</h6>
      <div class="dgm-ees-item">Your Spring Boot service + flowable-spring-boot-starter</div>
      <div class="dgm-ees-item">Your DB — app tables + ACT_* tables, together</div>
    </div>
  </div>
</div>


| | Embedded | Standalone (REST) |
| :-- | :-- | :-- |
| Deployment | one artifact — yours | separate engine service |
| Transactions | engine joins your `@Transactional` — process state and domain writes commit **atomically** | two systems, eventual consistency between them |
| Service tasks | direct calls to Spring beans | expressions/HTTP only, or engine-side JARs |
| Polyglot callers | JVM only | any language |
| Upgrades / scaling | coupled to your service | independent |
| Best for | one product team, JVM shop, transactional integrity matters | many consumers, non-JVM callers, central platform team |

The atomic-commit property is the headline: an embedded service task writing to
your domain tables and the engine advancing the token are **one** database
transaction. Lesson 03's rollback rules now span your business data too — a
failed segment rolls back your domain writes along with the token. Over REST,
you must engineer that consistency yourself.

## Use It

Everything Spring needs is one starter dependency:
`org.flowable:flowable-spring-boot-starter-process`. It auto-configures the
engine against your datasource and auto-deploys every model in
`src/main/resources/processes/`. The full app is
[`code/LoanApplication.java`](../code/LoanApplication.java); here are the two
pieces that matter:

A service task as a Spring bean (compare it to the toy engine's `handler`
lambda):

```java
@Component("creditCheckDelegate")
public static class CreditCheckDelegate implements JavaDelegate {
    @Override
    public void execute(DelegateExecution execution) {
        long amount = (Long) execution.getVariable("amount");
        execution.setVariable("score", amount < 1_000_000 ? 720 : 640);
    }
}
```

wired in the model with
`<serviceTask id="creditCheck" flowable:delegateExpression="${creditCheckDelegate}"/>`.
Because it's a normal bean, it can inject your repositories, and it runs inside
the engine's transaction.

Here is how you drive an instance — the same two operations you built in Phase 1
and persisted in lesson 01:

```java
String id = runtimeService.startProcessInstanceByKey(
        "loanTriage", Map.of("applicant", "meera", "amount", 2_000_000L)).getId();
Task review = taskService.createTaskQuery().processInstanceId(id).singleResult();
taskService.complete(review.getId(), Map.of("decision", "approved"));
```

Settings live in
[`outputs/application.properties`](../outputs/application.properties) —
datasource, schema auto-update, the async executor toggle (lesson 04), and the
history level (Phase 9).

Run it the standard Spring way:

```bash
mvn spring-boot:run
# waiting at: Manual credit review
# instance ended: true
```

## Ship It

This lesson ships a starter you can copy into any Spring Boot service:
[`code/LoanApplication.java`](../code/LoanApplication.java) plus
[`outputs/application.properties`](../outputs/application.properties).

## Check Yourself

**Q1.** In an embedded setup, a delegate writes a row to your `disbursals` table, and a
later task in the same segment throws. Your row is…

- A) committed — it was a separate concern
- B) rolled back — delegate writes share the engine's transaction
- C) moved to a staging table
- D) undefined

<details><summary>Answer</summary>B — one datasource, one transaction. This
atomicity is embedded mode's biggest gift, and the thing you must consciously
replace if you move to standalone.</details>

**Q2.** Your platform must serve process starts from Python and Node services. Which
topology fits with least friction?

- A) embedded in each service
- B) standalone engine consumed over REST
- C) embedded in one Java service that proxies for the others
- D) no engine

<details><summary>Answer</summary>B — embedded is JVM-only. (C is a real pattern
too, but it makes one team's service everyone's bottleneck — that's a Phase 10
discussion.)</details>

**Q3.** Where do the engine's tables live in embedded mode?

- A) an internal H2 the engine hides from you
- B) in your application's datasource, alongside your domain tables
- C) in files
- D) in memory only

<details><summary>Answer</summary>B — `ACT_*` tables in your schema. Your DBA will
have opinions; Phase 9 gives you the answers.</details>

**Challenge.** Wire lesson 03's `loan-triage.bpmn20.xml` into
`src/main/resources/processes/`, replace the expression-based `creditCheck` with
the delegate above, and make the delegate throw for amounts over ₹50 lakh.
Observe: does the start call fail, or does a job dead-letter? Explain the answer
using lesson 03's boundary rules, then add `flowable:async="true"` and watch the
behaviour flip.

## Related

- Phase README: [The engine: state & transactions](../../README.md)
- Topology decision in depth: Phase 10, lesson 01 (see [`ROADMAP.md`](../../../../ROADMAP.md))
