"""SDK tool loop with parallel dispatch, composing this phase's pieces.

Requires the `anthropic` package + ANTHROPIC_API_KEY to run live.
Defaults to Claude Opus 5 (claude-opus-5). This is illustrative wiring; the
validate()/ok()/err()/dispatch() helpers are the ones built earlier in the phase.
"""
import anthropic
from concurrent.futures import ThreadPoolExecutor

client = anthropic.Anthropic()

# --- stand-ins for the phase's modules (lesson 01/02/03) ---
SCHEMA_BY_NAME = {
    "add": {"type": "object",
            "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
            "required": ["a", "b"]},
}
TOOLS = [{"name": "add", "description": "Add two numbers.",
          "input_schema": SCHEMA_BY_NAME["add"]}]
IMPL = {"add": lambda a, b: a + b}


def validate(args, schema):                       # lesson 02 (trimmed)
    for k in schema.get("required", []):
        if k not in args:
            return f"missing required field {k!r}"
    return None


def ok(tid, content):
    return {"type": "tool_result", "tool_use_id": tid, "content": str(content)}


def err(tid, msg):
    return {"type": "tool_result", "tool_use_id": tid, "content": f"error: {msg}",
            "is_error": True}


def run_call(call):
    bad = validate(call.input, SCHEMA_BY_NAME[call.name])
    if bad:
        return err(call.id, bad)
    try:
        return ok(call.id, IMPL[call.name](**call.input))
    except Exception as e:
        return err(call.id, str(e))


def step(messages):
    msg = client.messages.create(model="claude-opus-5", max_tokens=1024,
                                 tools=TOOLS, messages=messages)
    messages.append({"role": "assistant", "content": msg.content})
    calls = [b for b in msg.content if b.type == "tool_use"]
    if not calls:
        return messages, "".join(b.text for b in msg.content if b.type == "text")
    with ThreadPoolExecutor() as pool:            # independent tools run in parallel
        results = list(pool.map(run_call, calls))
    messages.append({"role": "user", "content": results})
    return messages, None


if __name__ == "__main__":
    msgs = [{"role": "user", "content": "Use add to compute 2+3 and 10+20."}]
    while True:
        msgs, final = step(msgs)
        if final is not None:
            print(final)
            break
