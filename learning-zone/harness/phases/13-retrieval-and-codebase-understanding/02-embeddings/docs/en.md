# Embeddings & semantic code search

> **Motto** — Lexical search finds the same words; semantic search finds the same meaning.

*Part of Phase 13 — Retrieval & Codebase Understanding.*

## The Problem

Lexical search (lesson 01) fails when the query and the code use different words. Search
"authenticate user" and you miss `def login()`. **Embeddings** map text to vectors where
similar *meaning* lands nearby, so a semantic search retrieves `login` for "authenticate".
Build the mechanics — embed, store, cosine-rank — with a toy embedder so the idea is
concrete, then swap in a real model.

## The Concept

<style>
.dgm-emb{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-emb-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-emb h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-emb-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-emb-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-emb-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-emb-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-emb-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-emb-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-emb-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-emb-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-emb-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-emb{padding:20px 16px 18px}.dgm-emb-row{flex-direction:column}}
</style>
<div class="dgm-emb">
  <span class="dgm-emb-chip">Two embed steps meet at one index</span>
  <h4>Chunks embed once at index time; the query embeds fresh at search time</h4>
  <p class="dgm-emb-sub">Both land in the same vector space, so cosine similarity can compare them directly.</p>
  <div class="dgm-emb-row">
    <div class="dgm-emb-n neutral">Chunks</div>
    <span class="dgm-emb-arr">→</span>
    <div class="dgm-emb-n accent">Embed → vectors</div>
    <span class="dgm-emb-arr">→</span>
    <div class="dgm-emb-n blue">Vector index</div>
  </div>
  <div class="dgm-emb-row" style="margin-top:8px">
    <div class="dgm-emb-n neutral">Query</div>
    <span class="dgm-emb-arr">→</span>
    <div class="dgm-emb-n accent">Embed</div>
    <span class="dgm-emb-arr">→</span>
    <div class="dgm-emb-n green">Cosine top-k from index</div>
  </div>
</div>


## Build It

`code/semantic.py` — a toy bag-of-words embedder + cosine search (real models replace the
embedder, the rest is identical):

```python
import math
from collections import Counter

def embed(text):                       # toy: word-count vector (a real model: dense vec)
    return Counter(text.lower().split())

def cosine(a, b):
    dot = sum(a[k] * b.get(k, 0) for k in a)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    return dot / (na * nb) if na and nb else 0.0

class SemanticIndex:
    def __init__(self):
        self.items = []                # (text, vector)

    def add(self, text):
        self.items.append((text, embed(text)))

    def search(self, query, k=3):
        qv = embed(query)
        ranked = sorted(self.items, key=lambda it: cosine(qv, it[1]), reverse=True)
        return [t for t, _ in ranked[:k]]
```

```python
ix = SemanticIndex()
for doc in ["def login(): authenticate the user",
            "def add(a, b): return a + b",
            "class Session: user session state"]:
    ix.add(doc)
print(ix.search("authenticate user")[0])    # the login doc ranks first
```

The pipeline — embed corpus, embed query, cosine top-k — is exactly what production vector
search does. Only `embed` changes, to a real embedding model, and the index gets an ANN
structure for scale.

## Use It

Real code search, and RAG, uses an embedding model plus a vector DB. For a coding agent,
this powers "find code related to X" beyond exact strings. There's a cost/latency tradeoff
here: you embed once and search cheaply, but you must keep the index fresh as code changes,
or stale embeddings will retrieve deleted code.

## Ship It

[`code/semantic.py`](../../02-embeddings/code/semantic.py) — a toy embedder + cosine semantic
index.

## Check Yourself

**Q1.** When does semantic search beat lexical?

- A) never
- B) when query and code share meaning but not words ("authenticate" → `login`)
- C) only for exact matches
- D) for numbers

<details><summary>Answer</summary>B — meaning over surface form.</details>

**Q2.** What's the freshness risk with an embedding index?

- A) none
- B) stale embeddings can retrieve code that was changed or deleted
- C) it's too fast
- D) it uses no memory

<details><summary>Answer</summary>B — keep the index in sync with the code.</details>

**Challenge.** Swap `embed` for a real embedding model and compare its top-k to the toy
embedder on the same corpus.

## Related

- Builds on: [Repo maps](../../01-repo-maps/docs/en.md)
- Next: [Hybrid search & reranking](../../03-hybrid-search/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
