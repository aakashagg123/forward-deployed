"""Validate tool arguments, run the tool, and shape the outcome as a tool_result block.

Runs offline:  python3 code/results.py
"""
MAX_RESULT_CHARS = 2000        # example value: tune it against your context budget

TYPES = {"string": str, "number": (int, float), "integer": int,
         "boolean": bool, "object": dict, "array": list}


def validate(value, schema, path="args"):
    """Return None if valid, else a message that names the field and what to change."""
    t = schema.get("type")
    if t:
        is_num = t in ("number", "integer")
        if not isinstance(value, TYPES[t]) or (is_num and isinstance(value, bool)):
            return f"{path}: expected {t}, got {type(value).__name__}"
    if "enum" in schema and value not in schema["enum"]:
        return f"{path}: {value!r} is not allowed; choose one of {schema['enum']}"
    if t in ("number", "integer"):
        if "minimum" in schema and value < schema["minimum"]:
            return f"{path}: {value} is below the minimum {schema['minimum']}"
        if "maximum" in schema and value > schema["maximum"]:
            return f"{path}: {value} is above the maximum {schema['maximum']}"
    if t == "object":
        props = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in value:
                return f"{path}: missing required field {key!r}"
        for key, item in value.items():
            if key not in props:
                return f"{path}: unexpected field {key!r}; allowed: {sorted(props)}"
            err = validate(item, props[key], f"{path}.{key}")
            if err:
                return err
    if t == "array" and "items" in schema:
        for n, item in enumerate(value):
            err = validate(item, schema["items"], f"{path}[{n}]")
            if err:
                return err
    return None


def result(call_id, content, is_error=False, limit=MAX_RESULT_CHARS):
    """Wrap an outcome: pair it to the call id, flag errors, cap the size with a visible note."""
    text = str(content)
    if len(text) > limit:
        text = (f"{text[:limit]}\n...[truncated {len(text) - limit} of {len(text)} chars; "
                "ask for a narrower range]")
    return {"type": "tool_result", "tool_use_id": call_id, "content": text, "is_error": is_error}


def run_tool(call, impls, schemas):
    """validate -> run -> wrap. Never raises, and never runs a call that failed validation."""
    schema = schemas.get(call["name"])
    if schema is None:
        return result(call["id"], f"no tool named {call['name']!r}; have {sorted(schemas)}", True)
    problem = validate(call["input"], schema["input_schema"])
    if problem:
        return result(call["id"], problem, True)
    try:
        return result(call["id"], impls[call["name"]](**call["input"]))
    except Exception as exc:
        return result(call["id"], f"{type(exc).__name__}: {exc}", True)


if __name__ == "__main__":
    ran = []
    def read_lines(path, count=10):
        ran.append(path)
        if path == "big.txt":
            return "x" * 5000
        raise FileNotFoundError(f"{path} does not exist")

    schemas = {"read_lines": {"input_schema": {
        "type": "object", "required": ["path"],
        "properties": {"path": {"type": "string"},
                       "count": {"type": "integer", "minimum": 1, "maximum": 100},
                       "mode": {"type": "string", "enum": ["head", "tail"]}}}}}
    impls = {"read_lines": read_lines}
    call = lambda **kw: {"id": "t1", "name": "read_lines", "input": kw}

    # bad calls become precise errors and the function never runs
    cases = [(call(count=5), "missing required field 'path'"),
             (call(path="a", count="5"), "expected integer, got str"),
             (call(path="a", count=True), "expected integer, got bool"),   # bool is not a number
             (call(path="a", mode="middle"), "choose one of ['head', 'tail']"),
             (call(path="a", count=500), "above the maximum 100"),
             (call(path="a", lines=3), "unexpected field 'lines'")]
    for c, expect in cases:
        r = run_tool(c, impls, schemas)
        assert r["is_error"] and expect in r["content"], (r, expect)
    assert ran == []

    # a crash is an error result, not an exception
    r = run_tool(call(path="missing.txt"), impls, schemas)
    assert r["is_error"] and r["content"].startswith("FileNotFoundError")

    # a huge result is cut, and the cut is visible
    r = run_tool(call(path="big.txt"), impls, schemas)
    assert not r["is_error"] and len(r["content"]) < 2100
    assert "truncated 3000 of 5000 chars" in r["content"] and r["tool_use_id"] == "t1"

    nested = {"type": "array", "items": {"type": "object", "required": ["id"],
                                         "properties": {"id": {"type": "integer"}}}}
    assert validate([{"id": 1}, {"id": 2}], nested) is None
    assert validate([{"id": 1}, {"id": "x"}], nested) == "args[1].id: expected integer, got str"
    print("ok: validation, error results and truncation behave")
