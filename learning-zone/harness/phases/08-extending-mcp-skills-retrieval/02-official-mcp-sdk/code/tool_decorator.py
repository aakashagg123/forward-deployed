"""What an SDK's @tool decorator does, in stdlib: read type hints, build inputSchema.

Run:  python3 code/tool_decorator.py
"""
import inspect

JSON_TYPES = {int: "integer", float: "number", str: "string", bool: "boolean"}
TOOLS = {}                      # name -> {"spec": tools/list entry, "fn": function}


def tool(fn):
    """Register fn as a tool. The schema comes from its signature and docstring."""
    props, required = {}, []
    for name, p in inspect.signature(fn).parameters.items():
        props[name] = {"type": JSON_TYPES[p.annotation]}
        if p.default is inspect.Parameter.empty:
            required.append(name)
        else:
            props[name]["default"] = p.default
    spec = {"name": fn.__name__, "description": inspect.getdoc(fn),
            "inputSchema": {"type": "object", "properties": props, "required": required}}
    TOOLS[fn.__name__] = {"spec": spec, "fn": fn}
    return fn


def call(name, arguments):
    """The tools/call step: check required arguments, run, wrap in a result."""
    t = TOOLS[name]
    missing = [r for r in t["spec"]["inputSchema"]["required"] if r not in arguments]
    if missing:
        return {"content": [{"type": "text", "text": f"missing: {missing}"}], "isError": True}
    return {"content": [{"type": "text", "text": str(t["fn"](**arguments))}], "isError": False}


@tool
def recall(query: str, limit: int = 3) -> list:
    """Return saved notes that match the query."""
    return ["note about " + query][:limit]


if __name__ == "__main__":
    spec = TOOLS["recall"]["spec"]
    assert spec["description"] == "Return saved notes that match the query."
    assert spec["inputSchema"]["required"] == ["query"]            # limit has a default
    assert spec["inputSchema"]["properties"]["limit"] == {"type": "integer", "default": 3}
    assert call("recall", {"query": "x"})["content"][0]["text"] == "['note about x']"
    assert call("recall", {})["isError"] is True                    # missing argument
    print(spec["inputSchema"])
