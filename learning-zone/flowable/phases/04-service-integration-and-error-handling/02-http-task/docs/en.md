# The HTTP task: calling REST APIs from a process

> **Motto** — Most integrations are one HTTP call. The HTTP task lets the model make
> it declaratively — URL, headers, timeout, and failure routing all visible in the
> diagram.

*Part of Phase 04 — Service integration & error handling.*

## The Problem

Writing a JavaDelegate for every REST call means a Java class, a deployment, and a
code review — for what is really just configuration: method, URL, headers, timeout.
On a standalone engine (Phase 1's Docker container), you can't even ship delegates
without building a custom image. For plain request/response integrations, you want
the call *in the model*: versioned with it, reviewable next to the flow it serves,
deployable to a stock engine.

## The Concept

Setting `flowable:type="http"` on a service task swaps its behaviour for a built-in
HTTP client configured by fields:

<style>
.dgm-ht{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #a63d40;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-ht-chip{position:absolute;top:-11px;left:24px;background:#a63d40;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(166,61,64,.28)}
.dgm-ht h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-ht-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-ht-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-ht-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-ht-n.accent{background:#faeceb;border-color:#e3b3ad;color:#7a2c2e}
.dgm-ht-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-ht-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-ht-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-ht-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-ht-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-ht{padding:20px 16px 18px}.dgm-ht-row{flex-direction:column}}
.dgm-ht-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-ht-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-ht-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-ht-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-ht-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-ht-b.accent{background:#faeceb;border-color:#e3b3ad}
.dgm-ht-b.accent h6{color:#7a2c2e}
.dgm-ht-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-ht-b.blue h6{color:#0550ae}
.dgm-ht-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-ht-b.green h6{color:#1a614f}
.dgm-ht-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-ht-b.red h6{color:#82061e}
.dgm-ht-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-ht-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-ht{padding:20px 16px 18px}.dgm-ht-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-ht">
  <span class="dgm-ht-chip">HTTP task as a BPMN error source</span>
  <h4>A 4xx/5xx response becomes a named error the diagram can branch on</h4>
  <p class="dgm-ht-sub">2xx moves on normally; anything else throws a BPMN error the flow can catch.</p>
  <div class="dgm-ht-row">
    <div class="dgm-ht-n blue">● start</div>
    <span class="dgm-ht-arr">→</span>
    <div class="dgm-ht-n accent">HTTP task ⚙️🌐 — GET /v1/score?pan=…</div>
  </div>
  <div class="dgm-ht-branches">
    <div class="dgm-ht-b green">
      <h6>2xx</h6>
      <p>Review score 👤 → end</p>
    </div>
    <div class="dgm-ht-b red">
      <h6>4xx / 5xx → BPMN error</h6>
      <p>Pull report manually 👤 → end</p>
    </div>
  </div>
</div>


The fields that matter, and what each buys you:

| Field | Role |
| :-- | :-- |
| `requestMethod`, `requestUrl`, `requestHeaders`, `requestBody` | the call itself; `${var}` expressions everywhere |
| `requestTimeout` | never let a slow API hold the transaction hostage |
| `resultVariablePrefix` + `saveResponseParameters` | response status/headers/body land as process variables (`bureauResponseStatusCode`, `bureauResponseBody`) |
| `failStatusCodes` / `handleStatusCodes` | which statuses count as failure, and turn them into **catchable BPMN errors** instead of raw exceptions |

That last row is the bridge to the rest of this phase. With `failStatusCodes` set, a
404 from the bureau isn't a stack trace in a log — it's an error event the diagram
routes, exactly like a delegate throwing `BpmnError` (lesson 01). Phase 2 still
applies unchanged: mark the HTTP task `flowable:async="true"`, and slow or flaky
calls retry through the job executor instead of failing the caller's transaction.

When not to use it: anything needing OAuth token refresh, response parsing beyond
"grab the JSON", idempotency keys, or circuit breakers. That logic belongs in a
delegate or a dedicated gateway service. The HTTP task is for calls that are truly
just calls.

## Use It

The full model is
[`outputs/bureau-check.bpmn20.xml`](../outputs/bureau-check.bpmn20.xml). It deploys
to the stock `flowable/flowable-rest` container with zero custom code. Its core:

```xml
<serviceTask id="fetchScore" name="Fetch bureau score" flowable:type="http">
  <extensionElements>
    <flowable:field name="requestUrl">
      <flowable:expression><![CDATA[https://bureau.example.com/v1/score?pan=${pan}]]></flowable:expression>
    </flowable:field>
    <flowable:field name="requestTimeout">
      <flowable:string><![CDATA[5000]]></flowable:string>
    </flowable:field>
    <flowable:field name="resultVariablePrefix">
      <flowable:string><![CDATA[bureau]]></flowable:string>
    </flowable:field>
    <flowable:field name="failStatusCodes">
      <flowable:string><![CDATA[400, 404, 5XX]]></flowable:string>
    </flowable:field>
  </extensionElements>
</serviceTask>

<boundaryEvent id="bureauFailed" attachedToRef="fetchScore">
  <errorEventDefinition errorRef="HTTP_FAULT"/>
</boundaryEvent>
```

Deploy and drive it with Phase 1's client
([`flowable_client.py`](../../../01-bpmn-and-the-token-model/04-run-it-on-flowable/outputs/flowable_client.py)).
Start an instance with a `pan` variable. Since `bureau.example.com` doesn't exist,
watch the failure path do its job: the boundary event fires, and the instance parks
at *Pull bureau report manually* instead of dying. That's integration failure as a
designed path, not an incident.

## Ship It

This lesson ships
[`outputs/bureau-check.bpmn20.xml`](../outputs/bureau-check.bpmn20.xml), a reusable
HTTP-integration pattern: a call, a timeout, response variables, and failure routed
to a human fallback. The capstone's bureau step reuses it.

## Check Yourself

**Q1.** Without `failStatusCodes`, a 500 from the API causes…

- A) the error boundary to fire
- B) a technical exception — rollback, and job retries if the task is async
- C) the response to be stored with status 500
- D) the instance to complete

<details><summary>Answer</summary>B — by default non-2xx is a technical failure like
any thrown exception. `failStatusCodes` (+ handling) is what promotes chosen statuses
to catchable BPMN errors.</details>

**Q2.** Where does the response body end up with `resultVariablePrefix` = `bureau`?

- A) discarded
- B) in `bureauResponseBody` (plus status/headers variables) on the instance
- C) in the history tables only
- D) in a file

<details><summary>Answer</summary>B — the prefix + `saveResponseParameters` maps the
whole response into process variables the next tasks can read.</details>

**Q3.** The bureau call needs an OAuth refresh flow and a circuit breaker. Best home?

- A) more HTTP-task fields
- B) a script task
- C) a delegate (or a gateway service the HTTP task calls internally)
- D) the process can't do this

<details><summary>Answer</summary>C — the HTTP task is deliberately dumb. Protocol
logic belongs in code, and the task stays for calls that are just calls.</details>

**Challenge.** Point `requestUrl` at a real public API (for example, a status
endpoint you trust), deploy to your local engine, and run it twice — once against the
real URL, once against a garbage domain. Diff the two instances' variables and
history. You should see the happy path store `bureauResponseStatusCode=200` and the
failure path route through `bureauFailed`, without a single line of code.

## Related

- Next: [BPMN errors vs technical errors](../../03-bpmn-errors-vs-technical/docs/en.md)
- Previous: [Service tasks & delegates](../../01-service-tasks-and-delegates/docs/en.md)
