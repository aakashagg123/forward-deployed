# Use it: OpenTelemetry for agents

> **Motto** — Emit your spans in a standard format and any observability backend can read them.

*Part of Phase 16 — Observability & Cost. Completes the phase.*

## The Problem

Your hand-built tracer (lesson 01) is great for understanding tracing, but production needs
more. You want spans in your existing dashboards — Grafana, Honeycomb, Datadog — not a
bespoke format. **OpenTelemetry (OTel)** is the industry standard for this. You emit spans
with attributes via the OTel SDK, and you can export them anywhere. This is the production
end-state of the phase.

## The Concept

<style>
.dgm-otel{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-otel-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-otel h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-otel-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-otel-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-otel-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-otel-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-otel-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-otel-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-otel-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-otel-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-otel-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-otel{padding:20px 16px 18px}.dgm-otel-row{flex-direction:column}}
</style>
<div class="dgm-otel">
  <span class="dgm-otel-chip">One SDK, any backend</span>
  <h4>Agent spans go through the OpenTelemetry SDK, which exports to whatever's downstream</h4>
  <p class="dgm-otel-sub">Swapping Grafana for Honeycomb or Datadog never touches the agent's instrumentation code.</p>
  <div class="dgm-otel-row">
    <div class="dgm-otel-n accent">Agent spans (model/tool calls)</div>
    <span class="dgm-otel-arr">→</span>
    <div class="dgm-otel-n blue">OpenTelemetry SDK</div>
    <span class="dgm-otel-arr">→</span>
    <div class="dgm-otel-n green">Exporter → Grafana / Honeycomb / Datadog</div>
  </div>
</div>


You instrument once with OTel. The backend is then a config choice.

## Build It / Use It

OTel is a library, so this is **Use It**. `code/otel_tracing.py` shows the shape (install
`opentelemetry-sdk` to run) — the same nested spans as lesson 01, now standard:

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter

trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
tracer = trace.get_tracer("harness")

def run(query):
    with tracer.start_as_current_span("agent.run") as run_span:
        run_span.set_attribute("query", query)
        with tracer.start_as_current_span("model.call") as s:
            s.set_attribute("gen_ai.usage.input_tokens", 120)   # semantic conventions
            s.set_attribute("gen_ai.request.model", "claude-opus-5")
        with tracer.start_as_current_span("tool.call") as s:
            s.set_attribute("tool.name", "bash")
```

The structure mirrors your scratch tracer. OTel adds standard **semantic conventions** — for
example, `gen_ai.*` attributes for LLM calls — so backends understand your agent spans out
of the box.

## Use It

Instrument the harness's model and tool calls with OTel spans and `gen_ai.*` attributes.
Point the exporter at your backend, and you get latency (lesson 03), token/cost (lesson 02),
and drift (lesson 04) signals in dashboards you already run. The Agent SDK and many MCP
servers emit OTel-compatible telemetry, so you consume it the same way. This is
observability you don't have to build from scratch, because you understand what's
underneath.

## Ship It

[`code/otel_tracing.py`](../../05-opentelemetry/code/otel_tracing.py) — agent spans via the
OpenTelemetry SDK.

## Check Yourself

**Q1.** Why use OpenTelemetry instead of a custom trace format?

- A) it's trendy
- B) standard spans + semantic conventions export to any backend you already run
- C) it's faster to type
- D) no reason

<details><summary>Answer</summary>B — portability to standard backends.</details>

**Q2.** What do `gen_ai.*` semantic conventions provide?

- A) nothing
- B) a standard vocabulary for LLM-call attributes (model, tokens) backends understand
- C) faster models
- D) lower cost

<details><summary>Answer</summary>B — standardized LLM telemetry attributes.</details>

**Challenge.** Swap `ConsoleSpanExporter` for an OTLP exporter pointed at a local collector,
and add `gen_ai.usage.output_tokens` + cost as span attributes.

## Related

- Builds on: the whole phase
- Phase complete → next: Phase 17 — [Security & Alignment](../../../../ROADMAP.md)
- [Roadmap](../../../../ROADMAP.md)
