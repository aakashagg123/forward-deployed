# Forms: form properties, form keys, external form apps

> **Motto** — The engine owns the *contract* of a form — fields, types, required,
> writable. Who renders the pixels is a separate decision with three answers.

*Part of Phase 03 — User tasks, identity & forms.*

## The Problem

A task inbox without forms is just a list of names, like "Approve leave request."
Approve *what*, based on *which* data, answering *which* questions? Every user task
implies a small data contract: show these values, collect those answers, validate
them, and write them as variables. Teams that skip modelling this contract end up
with UI code that knows secret variable names (the frontend sets `apprvd`,
stringly-typed). Their processes break when a form field is renamed — the same drift
the diagram was supposed to prevent, reintroduced at the UI layer.

## The Concept

Three strategies, one axis: *where does the form definition live?*

| Strategy | Definition lives | Rendering | Use when |
| :-- | :-- | :-- | :-- |
| **Form properties** | in the model, on the task (`flowable:formProperty`) | yours — any client that reads the contract | small structured forms; API-first teams; this course |
| **Form key** | `flowable:formKey="kyc-review-v2"` — an opaque pointer | your form app resolves the key to its own screen | rich existing UI; the engine only stores which screen |
| **Flowable Form engine** | separate deployable `.form` JSON artifacts | Flowable's renderer or yours | Flowable Work / all-in platform setups |

Form properties are the instructive one because the *engine* enforces the contract:

<style>
.dgm-frm{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #a63d40;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-frm-chip{position:absolute;top:-11px;left:24px;background:#a63d40;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(166,61,64,.28)}
.dgm-frm h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-frm-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-frm-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-frm-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-frm-n.accent{background:#faeceb;border-color:#e3b3ad;color:#7a2c2e}
.dgm-frm-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-frm-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-frm-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-frm-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-frm-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-frm{padding:20px 16px 18px}.dgm-frm-row{flex-direction:column}}
</style>
<div class="dgm-frm">
  <span class="dgm-frm-chip">The form is a contract, not a UI</span>
  <h4>The engine validates and writes variables — the UI is just a renderer</h4>
  <p class="dgm-frm-sub">Any client that speaks the form-data contract can drive the task.</p>
  <div class="dgm-frm-row">
    <div class="dgm-frm-n ">Model declares: approved (bool, required), coverage (enum), employee (read-only)</div>
    <span class="dgm-frm-arr">→</span>
    <div class="dgm-frm-n blue">GET form-data → contract as JSON</div>
    <span class="dgm-frm-arr">→</span>
    <div class="dgm-frm-n ">Any UI renders it</div>
    <span class="dgm-frm-arr">→</span>
    <div class="dgm-frm-n accent">POST form-data → engine validates, writes variables, completes task</div>
  </div>
</div>


Submitting through the form endpoint is the point. Type checks, required checks, and
enum membership all run **engine-side** before the task completes. The UI can't
invent `apprvd`, skip a mandatory answer, or send `coverage=cousin`. Read-only
expression properties (`expression="${employee}" writable="false"`) cover the other
half of every form: show context, but don't let the user change it.

Here's the honest scope: form properties handle flat, structured questions.
Multi-step wizards, conditional sections, and file uploads belong to form-key
territory, where the engine stores *which* screen and your form app owns the rest.
Avoid the middle ground — half the contract in properties, half in UI code, drifting
independently.

## Use It

The model —
[`outputs/leave-request-form.bpmn20.xml`](../outputs/leave-request-form.bpmn20.xml) —
declares the contract on the task:

```xml
<userTask id="approve" name="Approve leave request"
    flowable:candidateGroups="managers">
  <extensionElements>
    <flowable:formProperty id="approved" name="Approve?" type="boolean" required="true"/>
    <flowable:formProperty id="coverage" name="Coverage arranged by" type="enum">
      <flowable:value id="peer" name="A peer"/>
      <flowable:value id="manager" name="The manager"/>
      <flowable:value id="none" name="Not needed"/>
    </flowable:formProperty>
    <flowable:formProperty id="employee" name="Employee" type="string"
        expression="${employee}" writable="false"/>
  </extensionElements>
</userTask>
```

[`code/form_client.py`](../code/form_client.py) deploys it, reads the contract, and
submits through the validating endpoint:

```
$ python3 form_client.py
the task asks for:
  approved (boolean, required)
  comment (string)
  coverage (enum) one of ['peer', 'manager', 'none']
  employee (string)
submitted; task gone: True
```

Change `"approved": "true"` to `"approved": "maybe"`, and the submit fails
engine-side. The contract holding against a bad client is the demo's real payload.

## Ship It

This lesson ships both halves of the pattern:
[`leave-request-form.bpmn20.xml`](../outputs/leave-request-form.bpmn20.xml), the
contract in the model, and [`form_client.py`](../code/form_client.py), a
contract-driven client any UI team can crib from.

## Check Yourself

**Q1.** What does submitting via `POST /form/form-data` add over completing the task
with raw variables?

- A) nothing; it's an alias
- B) engine-side validation of the declared contract — types, required, enum membership — before completion
- C) it renders HTML
- D) it skips the task lifecycle

<details><summary>Answer</summary>B — the form endpoint is the enforced version of
the contract. Raw completion trusts the client.</details>

**Q2.** `flowable:formKey="kyc-review-v2"` means the engine…

- A) renders screen v2
- B) stores an opaque pointer your form application resolves — the engine knows *which* form, not *what's on it*
- C) validates against form v2's fields
- D) rejects tasks without matching variables

<details><summary>Answer</summary>B — form keys delegate everything but the
reference. Contract enforcement becomes your form app's job.</details>

**Q3.** "Show the employee name, don't let the approver edit it" is modelled as…

- A) a comment in the form
- B) a form property with `expression="${employee}"` and `writable="false"`
- C) CSS
- D) a separate read-only task

<details><summary>Answer</summary>B — read-only expression properties are the
display half of the contract, and they keep even *context* out of UI-side variable
name guessing.</details>

**Challenge.** Add a `days` property (`type="long"`, required) and make the client
submit `days: "ten"`. Observe the engine-side rejection. Then write the twenty-line
generic renderer: fetch any task's form-data and produce a text-mode form (prompt per
property, enum menus, skip read-only). That renderer working against *both* demo
tasks unmodified is the portability argument for contracts-in-the-model.

## Related

- Next: [Task queries & the inbox pattern](../../05-task-queries-and-inbox/docs/en.md)
- Previous: [Identity management](../../03-identity-management/docs/en.md)
