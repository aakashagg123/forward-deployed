# needs: pip install opentelemetry-sdk   (no API key; spans print to the console)
"""The same span tree as tracing.py, emitted through OpenTelemetry. Not run offline.

Attribute names follow the OpenTelemetry GenAI conventions, which are still marked
"Development" (they can change). Check the current spec before you depend on them.
"""
import os

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

MODEL = os.environ.get("HARNESS_MODEL", "claude-opus-5-5")

provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
tracer = provider.get_tracer("harness")


def run(task):
    with tracer.start_as_current_span("invoke_agent harness") as agent:
        agent.set_attribute("gen_ai.operation.name", "invoke_agent")
        agent.set_attribute("gen_ai.provider.name", "anthropic")
        with tracer.start_as_current_span(f"chat {MODEL}") as model_call:
            model_call.set_attribute("gen_ai.operation.name", "chat")
            model_call.set_attribute("gen_ai.provider.name", "anthropic")
            model_call.set_attribute("gen_ai.request.model", MODEL)
            model_call.set_attribute("gen_ai.usage.input_tokens", 120)    # read these from response.usage
            model_call.set_attribute("gen_ai.usage.output_tokens", 40)
        with tracer.start_as_current_span("execute_tool bash") as tool:
            tool.set_attribute("gen_ai.operation.name", "execute_tool")
            tool.set_attribute("gen_ai.tool.name", "bash")


if __name__ == "__main__":
    run("add a health-check route")
