# A tool registry & discovery layer

> **Motto** — As tools multiply, the harness needs a registry it can list, filter, and expose.

*Part of Phase 03 — Tool Engineering. Completes the phase.*

## The Problem

One tool is a dict entry. Fifty tools — across files, plugins, and MCP servers (Phase
12) — need a single place that knows them all. That place produces the `tools=` schema
list, dispatches by name, filters which tools a given agent or role may see (bounded
roles, Phase 10), and adds tools at runtime. Without a registry, tool wiring sprawls and
you can't scope what an agent can do.

## The Concept

<style>
.dgm-tr{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-tr-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-tr h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-tr-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-tr-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-tr-branches{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.dgm-tr-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-tr-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-tr-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-tr-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-tr-b.accent h6{color:#0d5c0d}
.dgm-tr-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-tr-b.blue h6{color:#0550ae}
.dgm-tr-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-tr-b.green h6{color:#1a614f}
.dgm-tr-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-tr-b.red h6{color:#82061e}
.dgm-tr-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-tr-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-tr{padding:20px 16px 18px}.dgm-tr-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-tr">
  <span class="dgm-tr-chip">One registry, four responsibilities</span>
  <h4>Schemas, dispatch, registration, and visibility all live in one place</h4>
  <p class="dgm-tr-sub">visible_to(role) is what makes bounded roles (Phase 10) possible at all.</p>
  <div class="dgm-tr-q">The registry</div>
  <div class="dgm-tr-branches">
    <div class="dgm-tr-b blue">
      <h6>schemas(filter)</h6>
      <p>→ model</p>
    </div>
    <div class="dgm-tr-b accent">
      <h6>dispatch(name, args)</h6>
    </div>
    <div class="dgm-tr-b green">
      <h6>register(tool)</h6>
      <p>at runtime</p>
    </div>
    <div class="dgm-tr-b neutral">
      <h6>visible_to(role)</h6>
      <p>bounded access</p>
    </div>
  </div>
</div>


## Build It

`code/registry.py` — a registry with registration, filtered schema export, dispatch, and
role scoping:

```python
class Registry:
    def __init__(self):
        self._tools = {}                       # name -> {fn, schema, tags}

    def register(self, name, fn, schema, tags=()):
        self._tools[name] = {"fn": fn, "schema": {**schema, "name": name}, "tags": set(tags)}

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
```

```python
r = Registry()
r.register("add", lambda a, b: a + b,
           {"description": "Add.", "input_schema": {}}, tags=["math"])
r.register("rm", lambda path: f"removed {path}",
           {"description": "Delete a file.", "input_schema": {}}, tags=["danger"])
print([s["name"] for s in r.visible_to({"add"})])     # ['add'] — reviewer can't see rm
print(r.dispatch("rm", {"path": "x"}, allow={"add"})) # error: not permitted
```

The `allow` set is the seam where permissions (Phase 8) and bounded roles (Phase 10)
plug in. The same registry exposes different tools to different agents.

## Use It

The registry produces `tools=` for the SDK and routes `tool_use` calls to
implementations. MCP servers (Phase 12) register their tools here on connect, so
discovered tools and local tools share one dispatch path.

## Ship It

[`code/registry.py`](../code/registry.py) — a tool registry with
runtime registration, filtered schemas, dispatch, and role scoping.

## Check Yourself

**Q1.** Why route all tools through one registry?

- A) style
- B) single place to list schemas, dispatch, and scope which tools an agent can see
- C) speed
- D) no reason

<details><summary>Answer</summary>B — central wiring + scoping.</details>

**Q2.** How does the registry support bounded roles (Phase 10)?

- A) it doesn't
- B) `schemas(allow=…)`/`dispatch(allow=…)` expose only permitted tools per role
- C) by renaming tools
- D) by deleting tools

<details><summary>Answer</summary>B — the allow-set scopes visibility and dispatch.</details>

**Challenge.** Add `tags`-based filtering (e.g. exclude all `danger`-tagged tools for a
low-trust agent) and a `describe()` that prints the catalog.

## Related

- Builds on: [SDK parallel tools](../../07-sdk-parallel-tools/docs/en.md)
- Used by: Phase 8 — Permissions, Phase 10 — Bounded roles, Phase 12 — MCP
- Phase complete → next: Phase 4 — [Context Engineering](../../../../ROADMAP.md)
- [Roadmap](../../../../ROADMAP.md)
