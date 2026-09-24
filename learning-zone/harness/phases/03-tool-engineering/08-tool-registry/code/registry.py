"""A tool registry: runtime registration, filtered schemas, dispatch, role scoping.

Run:  python3 registry.py
"""


class Registry:
    def __init__(self):
        self._tools = {}                       # name -> {fn, schema, tags}

    def register(self, name, fn, schema, tags=()):
        self._tools[name] = {"fn": fn, "schema": {**schema, "name": name},
                             "tags": set(tags)}

    def schemas(self, allow=None):
        return [t["schema"] for n, t in self._tools.items()
                if allow is None or n in allow]

    def visible_to(self, role_allow):
        """Schemas a role may use (bounded roles, Phase 10)."""
        return self.schemas(allow=role_allow)

    def dispatch(self, name, args, allow=None):
        if allow is not None and name not in allow:
            return f"error: tool {name!r} not permitted for this role"
        t = self._tools.get(name)
        if not t:
            return f"error: unknown tool {name!r}"
        return str(t["fn"](**args))


if __name__ == "__main__":
    r = Registry()
    r.register("add", lambda a, b: a + b,
               {"description": "Add.", "input_schema": {}}, tags=["math"])
    r.register("rm", lambda path: f"removed {path}",
               {"description": "Delete a file.", "input_schema": {}}, tags=["danger"])
    print("reviewer sees:", [s["name"] for s in r.visible_to({"add"})])   # ['add']
    print(r.dispatch("rm", {"path": "x"}, allow={"add"}))                  # not permitted
    print(r.dispatch("add", {"a": 2, "b": 3}))                            # 5
