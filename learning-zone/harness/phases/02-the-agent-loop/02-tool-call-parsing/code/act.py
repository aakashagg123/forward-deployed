"""The act step: parse a model message into typed calls, validate, dispatch.

Handles structured tool_calls and a text fallback (weaker models). Every path
returns a result dict — failures are data, never exceptions.

Run:  python3 act.py
"""
import json
import re


def parse_calls(message):
    """Return [(name, args), ...] from a model message (blocks or text fallback)."""
    if isinstance(message, dict) and message.get("tool_calls"):
        return [(c["name"], c["args"]) for c in message["tool_calls"]]
    text = message if isinstance(message, str) else message.get("text", "")
    calls = []
    for m in re.finditer(r"(\w+)\((\{.*?\})\)", text):       # e.g. add({"a":2,"b":3})
        try:
            calls.append((m.group(1), json.loads(m.group(2))))
        except json.JSONDecodeError:
            pass                                             # skip junk, don't crash
    return calls


def validate(name, args, schema):
    spec = schema.get(name)
    if spec is None:
        return f"error: unknown tool {name!r}"
    missing = [k for k in spec["required"] if k not in args]
    if missing:
        return f"error: {name} missing args {missing}"
    return None                                              # None == valid


def act(message, tools, schema):
    results = []
    for name, args in parse_calls(message):
        err = validate(name, args, schema)
        if err:
            results.append({"name": name, "ok": False, "content": err})
            continue
        try:
            out = str(tools[name](**args))
            results.append({"name": name, "ok": True, "content": out})
        except Exception as e:
            results.append({"name": name, "ok": False, "content": f"error: {e}"})
    return results


if __name__ == "__main__":
    tools = {"add": lambda a, b: a + b}
    schema = {"add": {"required": ["a", "b"]}}
    print(act('add({"a": 2, "b": 3})', tools, schema))
    print(act('add({"a": 2})', tools, schema))
    print(act('subtract({"a": 2, "b": 3})', tools, schema))
