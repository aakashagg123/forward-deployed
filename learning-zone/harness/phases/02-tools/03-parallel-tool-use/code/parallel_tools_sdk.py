# needs: pip install anthropic and ANTHROPIC_API_KEY
"""The tool loop with batched tool calls on the real SDK. Run:  python3 code/parallel_tools_sdk.py"""
import os

import anthropic

from parallel_tools import run_batch, user_turn

MODEL = os.environ.get("HARNESS_MODEL", "claude-opus-5-5")
client = anthropic.Anthropic()
SYSTEM = ("For maximum efficiency, whenever you need to perform multiple independent "
          "operations, invoke all relevant tools simultaneously rather than sequentially.")
IMPLS = {"add": lambda a, b: a + b}
SCHEMAS = [{"name": "add",
            "description": "Add two numbers. Use it for any sum. Returns the sum as text.",
            "input_schema": {"type": "object",
                             "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
                             "required": ["a", "b"]}}]


def run(query, max_steps=6):
    history = [{"role": "user", "content": query}]
    for _ in range(max_steps):
        msg = client.messages.create(model=MODEL, max_tokens=1024, system=SYSTEM,
                                     tools=SCHEMAS, messages=history)
        history.append({"role": "assistant", "content": msg.content})
        calls = [{"id": b.id, "name": b.name, "input": b.input}
                 for b in msg.content if b.type == "tool_use"]
        if not calls:
            return "".join(b.text for b in msg.content if b.type == "text")
        history.append(user_turn(run_batch(calls, IMPLS, read_only={"add"})))
    return "stopped: hit max_steps"


if __name__ == "__main__":
    print(run("Use add to compute 2+3 and 10+20."))
