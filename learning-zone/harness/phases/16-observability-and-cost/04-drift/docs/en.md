# Drift detection

> **Motto** — Quality erodes silently — watch the metric over time and alert when it slips.

*Part of Phase 16 — Observability & Cost.*

## The Problem

Even with regression gates (Phase 15), production quality can **drift**. A model update, a
changing input distribution, or a stale retrieval index can slowly degrade results over days
or weeks, with no single PR to blame. Drift detection watches a live metric — eval score,
success rate, user thumbs — over rolling windows. It alerts when the recent window falls
below the baseline.

## The Concept

<style>
.dgm-drft{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-drft-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-drft h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-drft-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-drft-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-drft-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-drft-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-drft-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-drft-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-drft-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-drft-b.accent h6{color:#0d5c0d}
.dgm-drft-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-drft-b.blue h6{color:#0550ae}
.dgm-drft-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-drft-b.green h6{color:#1a614f}
.dgm-drft-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-drft-b.red h6{color:#82061e}
.dgm-drft-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-drft-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-drft{padding:20px 16px 18px}.dgm-drft-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-drft">
  <span class="dgm-drft-chip">A rolling window compared against a baseline</span>
  <h4>Recent performance well below the baseline window triggers an alert</h4>
  <p class="dgm-drft-sub">Drift detection catches slow degradation that a single bad run wouldn't.</p>
  <div class="dgm-drft-q">Metric stream over time — rolling window vs. baseline window — recent ≪ baseline?</div>
  <div class="dgm-drft-branches">
    <div class="dgm-drft-b red">
      <h6>Yes</h6>
      <p>Alert: drift</p>
    </div>
    <div class="dgm-drft-b green">
      <h6>No</h6>
      <p>Healthy</p>
    </div>
  </div>
</div>


## Build It

`code/drift.py` — compare a recent window to a baseline window:

```python
def detect_drift(history, window=5, threshold=0.05):
    """history: list of metric values over time (oldest→newest)."""
    if len(history) < window * 2:
        return {"drift": False, "reason": "not enough data"}
    baseline = history[-window * 2:-window]
    recent = history[-window:]
    b, r = sum(baseline) / window, sum(recent) / window
    drift = (b - r) > threshold
    return {"drift": drift, "baseline": round(b, 3), "recent": round(r, 3),
            "delta": round(r - b, 3)}
```

```python
healthy = [0.9, 0.91, 0.9, 0.92, 0.9, 0.91, 0.9, 0.9, 0.91, 0.9]
drifting = [0.9, 0.9, 0.91, 0.9, 0.9, 0.82, 0.8, 0.81, 0.79, 0.8]
print(detect_drift(healthy))    # drift False
print(detect_drift(drifting))   # drift True (recent window dropped)
```

The detector flags a drop when the recent average falls a threshold below the prior
baseline. It looks for a trend, not a single bad data point, so you investigate before
users complain.

## Use It

Feed drift detection a live signal — periodic eval-set runs, task success rate, or user
feedback — tagged in your traces (lesson 01) and cost/quality dashboards. For a Claude Code
or Codex user, the practical version is this: you notice your agent's success rate slipping
after a model or prompt change, then re-run the eval suite (Phase 15) to localize it.
Regression gates catch drift *at merge*. Drift detection catches it *in production*.

## Ship It

[`code/drift.py`](../../04-drift/code/drift.py) — a rolling-window drift detector.

## Check Yourself

**Q1.** How is drift different from a regression caught by a CI gate?

- A) same thing
- B) drift is gradual degradation in production over time, with no single PR to blame
- C) drift is faster
- D) drift is about cost only

<details><summary>Answer</summary>B — gates catch it at merge; drift is the slow
production slide.</details>

**Q2.** Drift detection compares…

- A) one data point to zero
- B) a recent window's average to a baseline window's average
- C) tokens to dollars
- D) nothing

<details><summary>Answer</summary>B — windowed trend comparison.</details>

**Challenge.** Add a minimum-sample and a statistical test (e.g. a simple t-test) so small
noisy windows don't trigger false drift alerts.

## Related

- Builds on: [Tracing](../../01-tracing/docs/en.md); Phase 15 — [Evals](../../../15-evals-and-testing-the-harness/06-eval-harness/docs/en.md)
- Next: [Use It: OpenTelemetry for agents](../../05-opentelemetry/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
