"""Agent spans via the OpenTelemetry SDK.

Requires:  pip install opentelemetry-sdk
Illustrative of the OTel shape; compare to the scratch tracer in lesson 01.
"""
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
            s.set_attribute("gen_ai.request.model", "claude-opus-5")
            s.set_attribute("gen_ai.usage.input_tokens", 120)   # semantic conventions
        with tracer.start_as_current_span("tool.call") as s:
            s.set_attribute("tool.name", "bash")


if __name__ == "__main__":
    run("add a health-check route")
