# needs: pip install anthropic and ANTHROPIC_API_KEY
"""The same loop on the real SDK. Run:  python3 code/agent_loop_sdk.py"""
import os

import anthropic

from agent_loop import MAX_STEPS, TOOLS, act

MODEL = os.environ.get("HARNESS_MODEL", "claude-opus-5-5")
client = anthropic.Anthropic()
SCHEMAS = [{
    "name": "add",
    "description": "Add two numbers. Use it for any arithmetic sum. Returns the sum as text.",
    "input_schema": {"type": "object",
                     "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
                     "required": ["a", "b"]},
}]


def run(query):
    history = [{"role": "user", "content": query}]
    for _ in range(MAX_STEPS):
        msg = client.messages.create(model=MODEL, max_tokens=1024,
                                     tools=SCHEMAS, messages=history)
        history.append({"role": "assistant", "content": msg.content})
        calls = [{"id": b.id, "name": b.name, "input": b.input}
                 for b in msg.content if b.type == "tool_use"]
        if msg.stop_reason != "tool_use" or not calls:
            return "".join(b.text for b in msg.content if b.type == "text")
        history.append({"role": "user", "content": act(calls, TOOLS)})
    return "stopped: hit max_steps"


if __name__ == "__main__":
    print(run("What is 12 + 30? Use the add tool."))
