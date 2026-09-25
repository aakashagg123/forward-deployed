# Plugins & deferred tool loading

> **Motto** — Load a tool's full definition only when it's about to be used — names up front, schemas on demand.

*Part of Phase 12 — MCP & Extensibility.*

## The Problem

With many MCP servers and plugins connected, the agent could face *hundreds* of tool
schemas. That bloats the context and slows tool selection. **Deferred loading** fixes this.
Keep a lightweight index of tool *names*, and fetch a tool's full schema only when it's
selected or searched for. It's progressive disclosure (lesson 04) applied to tools.

## The Concept

<style>
.dgm-plg{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-plg-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-plg h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-plg-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-plg-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-plg-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-plg-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-plg-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-plg-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-plg-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-plg-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-plg-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-plg{padding:20px 16px 18px}.dgm-plg-row{flex-direction:column}}
.dgm-plg-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-plg-branches{display:grid;grid-template-columns:repeat(1,1fr);gap:10px}
.dgm-plg-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-plg-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-plg-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-plg-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-plg-b.accent h6{color:#0d5c0d}
.dgm-plg-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-plg-b.blue h6{color:#0550ae}
.dgm-plg-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-plg-b.green h6{color:#1a614f}
.dgm-plg-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-plg-b.red h6{color:#82061e}
.dgm-plg-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-plg-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-plg{padding:20px 16px 18px}.dgm-plg-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-plg">
  <span class="dgm-plg-chip">Search the index, load only what matches</span>
  <h4>A cheap name-only index gets searched; only the matched tool's full schema loads</h4>
  <p class="dgm-plg-sub">This is the same shape as skills — an index that's cheap, and a body that isn't.</p>
  <div class="dgm-plg-row">
    <div class="dgm-plg-n neutral">Tool index: names only (cheap)</div>
  </div>
  <div class="dgm-plg-q">Agent needs a tool?</div>
  <div class="dgm-plg-branches" style="grid-template-columns:repeat(1,1fr)">
    <div class="dgm-plg-b accent">
      <h6>Search / select</h6>
      <p>Load that tool's full schema → use it</p>
    </div>
  </div>
</div>


## Build It

`code/deferred.py` — a registry that defers schema loading:

```python
class DeferredRegistry:
    def __init__(self):
        self._loaders = {}        # name -> () -> full schema
        self._cache = {}

    def register(self, name, loader):
        self._loaders[name] = loader      # cheap: just the name + a thunk

    def index(self):
        return list(self._loaders)        # names only — what's always in context

    def load(self, name):
        if name not in self._cache:
            self._cache[name] = self._loaders[name]()   # fetch full schema on demand
        return self._cache[name]

    def search(self, term):
        return [n for n in self._loaders if term in n]
```

```python
reg = DeferredRegistry()
reg.register("github_create_pr", lambda: {"name": "github_create_pr", "input_schema": {"...": "big"}})
reg.register("github_list_issues", lambda: {"name": "github_list_issues", "input_schema": {}})
print(reg.index())                    # ['github_create_pr', 'github_list_issues'] (cheap)
print(reg.search("pr"))               # ['github_create_pr']
print(reg.load("github_create_pr"))   # full schema fetched only now
```

Only names sit in context. A heavy schema is materialized just-in-time when the agent
searches for or selects the tool.

## Use It

This is exactly the **deferred tool / tool-search** pattern you've seen. Large tool sets —
many MCP servers, plugin bundles — are presented as names. The agent fetches a tool's full
schema through a search step before calling it. Claude Code plugins and big MCP fleets rely
on this so connecting many servers doesn't drown the context window.

## Ship It

[`code/deferred.py`](../../05-plugins/code/deferred.py) — a deferred-loading tool registry.

## Check Yourself

**Q1.** What stays in context with deferred loading?

- A) every tool's full schema
- B) just tool names (the index); full schemas load on demand
- C) nothing
- D) only resources

<details><summary>Answer</summary>B — names always, schemas just-in-time.</details>

**Q2.** Why does this matter with many MCP servers?

- A) it doesn't
- B) hundreds of full schemas would bloat context and slow selection
- C) servers require it
- D) to save disk

<details><summary>Answer</summary>B — deferral keeps the window lean at scale.</details>

**Challenge.** Add an LRU cap to the schema cache so even loaded schemas are evicted when not
recently used.

## Related

- Builds on: [Skills](../../04-skills/docs/en.md), [MCP client](../../03-mcp-client/docs/en.md)
- Next: [Use It: the official MCP SDK](../../06-official-sdk/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
