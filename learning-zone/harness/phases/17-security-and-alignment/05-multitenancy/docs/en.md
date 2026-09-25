# Multi-tenant isolation & cache contamination

> **Motto** — Never let one tenant's data — or cache entry — leak into another's session.

*Part of Phase 17 — Security & Alignment.*

## The Problem

If your harness serves multiple users or tenants, the worst failure is **cross-tenant
leakage** — tenant A's data appears in tenant B's session. The sneakiest vector is the
**cache**. A semantic or prompt cache keyed without the tenant id can serve A's cached
response to B. The fix is to scope every cache key, memory store, and retrieval index by
tenant, so isolation is structural, not hopeful.

## The Concept

<style>
.dgm-mten{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-mten-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-mten h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-mten-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-mten-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-mten-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-mten-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-mten-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-mten-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-mten-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-mten-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-mten-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-mten{padding:20px 16px 18px}.dgm-mten-row{flex-direction:column}}
</style>
<div class="dgm-mten">
  <span class="dgm-mten-chip">Every cache key and every memory namespace includes the tenant</span>
  <h4>hash(tenant + query) keys the cache; memory and retrieval are namespaced by tenant</h4>
  <p class="dgm-mten-sub">Without tenant in the key, one tenant's cache hit can leak another tenant's answer.</p>
  <div class="dgm-mten-row">
    <div class="dgm-mten-n neutral">Request (tenant, query)</div>
    <span class="dgm-mten-arr">→</span>
    <div class="dgm-mten-n accent">Cache key = hash(tenant + query)</div>
    <span class="dgm-mten-arr">→</span>
    <div class="dgm-mten-n green">Per-tenant cache</div>
  </div>
  <div class="dgm-mten-row" style="margin-top:8px">
    <div class="dgm-mten-n neutral">Memory / retrieval</div>
    <span class="dgm-mten-arr">→</span>
    <div class="dgm-mten-n green">Namespaced by tenant</div>
  </div>
</div>


Every shared resource (cache, memory, index) gets the tenant id baked into its key/namespace.

## Build It

`code/isolation.py` — a tenant-scoped cache that can't cross-contaminate:

```python
import hashlib

class TenantCache:
    def __init__(self):
        self._store = {}

    def _key(self, tenant, query):
        return hashlib.sha256(f"{tenant}::{query}".encode()).hexdigest()

    def get(self, tenant, query):
        return self._store.get(self._key(tenant, query))

    def set(self, tenant, query, value):
        self._store[self._key(tenant, query)] = value
```

```python
c = TenantCache()
c.set("tenantA", "secret report", "A's data")
print(c.get("tenantB", "secret report"))   # None — B cannot see A's cached entry
print(c.get("tenantA", "secret report"))   # 'A's data'
```

Because the tenant id is part of the key, the *same* query from a different tenant produces
a *different* key. A's cached value stays unreachable by B. Apply the same namespacing to
memory (Phase 9) and retrieval indexes (Phase 13).

## Use It

For a single-developer Claude Code or Codex user this risk is less acute. But the moment you
build a multi-user product on the harness, it becomes critical — this is the exact "cache
contamination" failure from the AI-engineering conceptual track. Audit every shared store
and ask: is the tenant id in the key? If not, that's a leak waiting to happen.

## Ship It

[`code/isolation.py`](../../05-multitenancy/code/isolation.py) — a tenant-scoped cache.

## Check Yourself

**Q1.** The sneakiest cross-tenant leak vector is…

- A) the system prompt
- B) a cache keyed without the tenant id, serving one tenant's response to another
- C) the model name
- D) latency

<details><summary>Answer</summary>B — unkeyed caches cross-contaminate.</details>

**Q2.** The structural fix for cross-tenant leakage is…

- A) a longer prompt
- B) bake the tenant id into every cache key / memory / index namespace
- C) a bigger model
- D) hope

<details><summary>Answer</summary>B — namespace every shared resource by tenant.</details>

**Challenge.** Extend isolation to the retrieval index (Phase 13): ensure a tenant's
`search_code` can only return chunks from that tenant's files.

## Related

- Builds on: Phase 9 — Memory, Phase 13 — Retrieval; Phase 1 — [Caching](../../../01-llm-io-foundations/08-prompt-caching/docs/en.md)
- Next: [Use It: a security-review skill](../../06-security-review/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
