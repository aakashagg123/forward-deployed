"""A @tool decorator that registers a function with its schema, plus dispatch.

Run:  python3 tools.py
"""
REGISTRY = {}


def tool(name, description, schema):
    def deco(fn):
        REGISTRY[name] = {"fn": fn, "schema": {
            "name": name, "description": description, "input_schema": schema}}
        return fn
    return deco


@tool("add", "Add two numbers.",
      {"type": "object",
       "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
       "required": ["a", "b"]})
def add(a, b):
    return a + b


def schemas():
    return [t["schema"] for t in REGISTRY.values()]


def dispatch(name, args):
    entry = REGISTRY.get(name)
    if not entry:
        return f"error: unknown tool {name!r}"
    return str(entry["fn"](**args))


if __name__ == "__main__":
    print("schemas:", [s["name"] for s in schemas()])
    print("add ->", dispatch("add", {"a": 2, "b": 3}))
    print("nope ->", dispatch("nope", {}))
