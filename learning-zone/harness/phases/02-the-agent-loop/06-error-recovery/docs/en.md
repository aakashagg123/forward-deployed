# Error recovery inside the loop

> **Motto** — Errors are messages to the model, not exceptions to the user.

*Part of Phase 02 — The Agent Loop. Builds on lessons 01–05.*

## The Problem

Tools fail: a file doesn't exist, a command times out, an API returns 500, or the model
passes a bad argument. A naive loop lets the exception bubble up, and the whole agent
dies mid-task. The user sees a stack trace instead of a recovery. A robust loop treats
every failure as information the model can act on: read the error, try a different path,
or explain what went wrong. The skill is deciding *which* errors are recoverable and
*how many times* to let the model try.

## The Concept

<style>
.dgm-erec{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-erec-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-erec h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-erec-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-erec-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-erec-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-erec-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-erec-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-erec-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-erec-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-erec-b.accent h6{color:#0d5c0d}
.dgm-erec-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-erec-b.blue h6{color:#0550ae}
.dgm-erec-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-erec-b.green h6{color:#1a614f}
.dgm-erec-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-erec-b.red h6{color:#82061e}
.dgm-erec-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-erec-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-erec{padding:20px 16px 18px}.dgm-erec-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-erec">
  <span class="dgm-erec-chip">Recoverable errors retry; the rest abort cleanly</span>
  <h4>The retry budget decides whether an error becomes a message or an abort</h4>
  <p class="dgm-erec-sub">The model only ever sees an error if there's still budget to act on it.</p>
  <div class="dgm-erec-q">Tool error?</div>
  <div class="dgm-erec-branches">
    <div class="dgm-erec-b green">
      <h6>No</h6>
      <p>Result → model</p>
    </div>
    <div class="dgm-erec-b accent">
      <h6>Yes — recoverable, within retry budget</h6>
      <p>Error message → model, retry</p>
    </div>
  </div>
  <div class="dgm-erec-branches" style="grid-template-columns:repeat(1,1fr)">
    <div class="dgm-erec-b red">
      <h6>Not recoverable / budget spent</h6>
      <p>Abort cleanly, report to user</p>
    </div>
  </div>
</div>


Classify errors into three buckets:

- **Model-fixable** (bad args, wrong tool) → feed the error back; the model corrects.
- **Transient** (timeout, 429, 5xx) → retry with backoff (Phase 14), bounded count.
- **Fatal** (auth failure, out of budget) → stop and report; don't loop forever.

## Build It

`code/recovery.py` — wraps dispatch, classifies, and enforces a per-tool retry budget:

```python
from dataclasses import dataclass, field

TRANSIENT = ("timeout", "429", "503", "connection")

@dataclass
class Recovery:
    max_retries: int = 2
    attempts: dict = field(default_factory=dict)        # tool name -> count

    def dispatch(self, name, args, tools):
        try:
            return {"ok": True, "content": str(tools[name](**args))}
        except KeyError:
            return {"ok": False, "fatal": False,        # model-fixable: unknown tool
                    "content": f"error: no tool {name!r}; available: {list(tools)}"}
        except TypeError as e:
            return {"ok": False, "fatal": False,        # model-fixable: bad args
                    "content": f"error: bad arguments for {name}: {e}"}
        except Exception as e:
            msg = str(e).lower()
            transient = any(t in msg for t in TRANSIENT)
            n = self.attempts.get(name, 0) + 1
            self.attempts[name] = n
            if transient and n <= self.max_retries:
                return {"ok": False, "fatal": False, "retry": True,
                        "content": f"transient error (attempt {n}): {e}"}
            return {"ok": False, "fatal": not transient,
                    "content": f"error: {e}"}
```

```python
def flaky(n=[0]):
    n[0] += 1
    if n[0] < 3:
        raise RuntimeError("connection timeout")
    return "ok"

r = Recovery()
print(r.dispatch("flaky", {}, {"flaky": lambda: flaky()}))   # retry: True (attempt 1)
print(r.dispatch("flaky", {}, {"flaky": lambda: flaky()}))   # retry: True (attempt 2)
print(r.dispatch("flaky", {}, {"flaky": lambda: flaky()}))   # ok: True
print(r.dispatch("nope",  {}, {"flaky": lambda: flaky()}))   # model-fixable: unknown tool
```

The loop reads `fatal` to decide whether to abort. It reads `retry` to decide whether to
re-dispatch without consuming a step. The model only ever sees clean messages.

## Use It

In production the transient bucket becomes a real backoff policy. The `anthropic` library
raises `APIStatusError` with `.status_code`, and you retry 429/5xx errors with
exponential backoff and jitter (Phase 14). The classification you wrote here is the
decision layer that sits on top of any retry library.

## Ship It

[`code/recovery.py`](../../06-error-recovery/code/recovery.py) — a `Recovery` dispatcher
that classifies failures and bounds retries.

## Check Yourself

**Q1.** A tool is called with a missing argument. The right classification is…

- A) fatal — abort
- B) model-fixable — feed the error back so the model retries with correct args
- C) transient — retry with backoff
- D) ignore it

<details><summary>Answer</summary>B — the model produced the bad call, so the model can
fix it from a clear error message.</details>

**Q2.** Why bound the retry count per tool?

- A) to save memory
- B) so a permanently-failing tool can't loop forever burning budget
- C) the API requires it
- D) to reduce tokens

<details><summary>Answer</summary>B — without a ceiling, a transient classification on a
truly-broken tool becomes an infinite retry.</details>

**Challenge.** Add jitter to a (simulated) backoff between transient retries and log each
attempt, so the recovery is observable (a preview of Phase 16).

## Related

- Builds on: [Termination](../../03-termination/docs/en.md), [SDK loop](../../05-sdk-tool-use-loop/docs/en.md)
- Next: [A streaming agent loop](../../07-streaming-loop/docs/en.md)
- Deepens in: Phase 14 — [Reliability Engineering](../../../../ROADMAP.md)
