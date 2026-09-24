"""The agent loop on the real Anthropic SDK.

Requires:  pip install anthropic   and   ANTHROPIC_API_KEY in the environment.
Run:       python3 sdk_loop.py

Defaults to the latest model, Claude Opus 5 (claude-opus-5).
"""
import anthropic

client = anthropic.Anthropic()
MAX_STEPS = 10

TOOLS = {"add": lambda a, b: a + b}
SCHEMA = [{
    "name": "add",
    "description": "Add two numbers.",
    "input_schema": {
        "type": "object",
        "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
        "required": ["a", "b"],
    },
}]


def run(query):
    messages = [{"role": "user", "content": query}]
    for _ in range(MAX_STEPS):
        msg = client.messages.create(
            model="claude-opus-5", max_tokens=1024, tools=SCHEMA, messages=messages)
        messages.append({"role": "assistant", "content": msg.content})
        calls = [b for b in msg.content if b.type == "tool_use"]
        if msg.stop_reason != "tool_use" or not calls:            # termination
            return "".join(b.text for b in msg.content if b.type == "text")
        results = []
        for call in calls:                                         # act step
            try:
                out = str(TOOLS[call.name](**call.input))
            except Exception as e:
                out = f"error: {e}"                                # errors are data
            results.append({"type": "tool_result", "tool_use_id": call.id, "content": out})
        messages.append({"role": "user", "content": results})      # pairing invariant
    return "stopped: hit MAX_STEPS"


if __name__ == "__main__":
    print(run("What is 12 + 30? Use the add tool."))
