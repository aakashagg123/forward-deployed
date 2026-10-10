"""A tool registry: schemas for the model, dispatch for the harness, and a description lint.

Runs offline:  python3 code/tools.py
"""
import os
import re
import tempfile

NAME_RE = re.compile(r"^[a-zA-Z0-9_-]{1,128}$")        # the API's rule for tool names


class Registry:
    def __init__(self):
        self._tools = {}                                # name -> {"fn", "schema"}

    def tool(self, name, description, properties, required=()):
        """Decorator: register the function and its schema together so they cannot drift."""
        if not NAME_RE.match(name):
            raise ValueError(f"bad tool name {name!r}")
        schema = {"name": name, "description": description,
                  "input_schema": {"type": "object", "properties": properties,
                                   "required": list(required)}}

        def deco(fn):
            self._tools[name] = {"fn": fn, "schema": schema}
            return fn
        return deco

    def schemas(self, allow=None):
        """The list you pass as tools=. `allow` hides tools from a role."""
        return [t["schema"] for n, t in self._tools.items() if allow is None or n in allow]

    def dispatch(self, name, args, allow=None):
        """Map the model's chosen name + args to a function. Hiding is not enough: enforce here."""
        if allow is not None and name not in allow:
            raise PermissionError(f"tool {name!r} is not permitted for this role")
        if name not in self._tools:
            raise LookupError(f"no tool named {name!r}; have {sorted(self._tools)}")
        return str(self._tools[name]["fn"](**args))


def lint(schema):
    """Rough check of the rubric. A lint finds gaps. It cannot judge quality."""
    problems, desc = [], schema["description"]
    if len(re.findall(r"[.!?](?:\s|$)", desc)) < 3:
        problems.append("description has fewer than 3 sentences")
    if "use when" not in desc.lower():
        problems.append("say when to use it (and when not to)")
    if "return" not in desc.lower():
        problems.append("say what it returns")
    for key, spec in schema["input_schema"]["properties"].items():
        if not spec.get("description"):
            problems.append(f"parameter {key!r} has no description")
    return problems


reg = Registry()


@reg.tool("read_file",
          "Read a text file from the project and return its contents. "
          "Use when you need to see code or config. Do not use it to list a folder. "
          "Returns the file text, or an error if the path does not exist.",
          {"path": {"type": "string", "description": "Path relative to the project root, e.g. src/app.py"}},
          required=["path"])
def read_file(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


@reg.tool("delete_file", "Delete a file.", {"path": {"type": "string"}}, required=["path"])
def delete_file(path):
    os.remove(path)
    return f"deleted {path}"


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        target = os.path.join(tmp, "a.txt")
        open(target, "w").write("hello")
        assert reg.dispatch("read_file", {"path": target}) == "hello"

        # a reviewer role sees and may call only the read tool
        reviewer = {"read_file"}
        assert [s["name"] for s in reg.schemas(allow=reviewer)] == ["read_file"]
        try:
            reg.dispatch("delete_file", {"path": target}, allow=reviewer)
            raise SystemExit("hidden tool was still callable")
        except PermissionError:
            assert os.path.exists(target)               # the file survived

    s = reg.schemas()[0]
    assert set(s) == {"name", "description", "input_schema"}
    assert lint(s) == []                                # the 4-part description passes
    poor = lint(reg.schemas()[1])
    assert len(poor) == 4, poor                         # "Delete a file." fails every check

    for call in [("nope", {}), ("read_file", {"path": "/no/such/file"})]:
        try:
            reg.dispatch(*call)
            raise SystemExit("expected an error")
        except (LookupError, FileNotFoundError):
            pass
    try:
        reg.tool("bad name!", "x", {})
        raise SystemExit("bad name accepted")
    except ValueError:
        pass
    print("ok: registry, scoping and lint behave;", len(reg.schemas()), "tools")
