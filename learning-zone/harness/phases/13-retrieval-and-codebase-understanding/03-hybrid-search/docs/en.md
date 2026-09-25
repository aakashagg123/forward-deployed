# Hybrid search & reranking

> **Motto** — Combine lexical and semantic hits, then rerank — each catches what the other misses.

*Part of Phase 13 — Retrieval & Codebase Understanding.*

## The Problem

Lexical search nails exact identifiers (`parse_config`) but misses paraphrases. Semantic
search nails meaning but can rank a vaguely-related file above the exact one. Using either
alone leaves recall on the table. **Hybrid search** fuses both result lists, and a **rerank**
step reorders the merged set by a sharper relevance signal. The combination beats either
method alone.

## The Concept

<style>
.dgm-hs{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-hs-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-hs h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-hs-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-hs-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-hs-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-hs-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-hs-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-hs-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-hs-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-hs-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-hs-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-hs{padding:20px 16px 18px}.dgm-hs-row{flex-direction:column}}
</style>
<div class="dgm-hs">
  <span class="dgm-hs-chip">Lexical and semantic hits get fused, then reranked</span>
  <h4>One query, two retrieval paths, one fused and reranked result set</h4>
  <p class="dgm-hs-sub">Reciprocal rank fusion is a cheap way to combine two rankings without training a model.</p>
  <div class="dgm-hs-row">
    <div class="dgm-hs-n neutral">Query</div>
  </div>
  <div class="dgm-hs-row" style="margin-top:8px">
    <div class="dgm-hs-n blue">Lexical hits</div>
  </div>
  <div class="dgm-hs-row" style="margin-top:8px">
    <div class="dgm-hs-n accent">Semantic hits</div>
  </div>
  <div class="dgm-hs-row">
    <div class="dgm-hs-n green">Fuse (e.g. reciprocal rank)</div>
    <span class="dgm-hs-arr">→</span>
    <div class="dgm-hs-n ">Rerank top-N</div>
    <span class="dgm-hs-arr">→</span>
    <div class="dgm-hs-n green">Final results</div>
  </div>
</div>


A common, robust fusion is **reciprocal rank fusion (RRF)**. Score each doc by the sum of
`1/(k+rank)` across the lists it appears in. It needs no score calibration.

## Build It

`code/hybrid.py` — RRF fusion over two ranked lists:

```python
def rrf(*ranked_lists, k=60):
    scores = {}
    for lst in ranked_lists:
        for rank, doc in enumerate(lst):
            scores[doc] = scores.get(doc, 0) + 1 / (k + rank + 1)
    return [d for d, _ in sorted(scores.items(), key=lambda kv: kv[1], reverse=True)]
```

```python
lexical  = ["auth.py", "utils.py", "session.py"]
semantic = ["session.py", "auth.py", "login_flow.py"]
print(rrf(lexical, semantic))
# auth.py & session.py rise (appear high in both); singletons rank lower
```

RRF rewards docs that *both* methods rank highly, so the exact match (lexical) and the
meaning match (semantic) reinforce each other. A true reranker — a cross-encoder or an
LLM-as-judge over the top-N — can refine the results further.

## Use It

Production code search and RAG almost always go hybrid plus rerank. It's the single biggest
recall/precision win after basic retrieval. For an agent, this is "find the relevant code"
done well. The reranker is often an LLM scoring the top-N for actual relevance to the task,
connecting to Phase 15's LLM-as-judge.

## Ship It

[`code/hybrid.py`](../../03-hybrid-search/code/hybrid.py) — reciprocal-rank-fusion hybrid
search.

## Check Yourself

**Q1.** Why fuse lexical and semantic results?

- A) redundancy
- B) each catches what the other misses (exact identifiers vs. meaning)
- C) to slow down
- D) no reason

<details><summary>Answer</summary>B — complementary recall.</details>

**Q2.** What does RRF reward?

- A) the longest document
- B) documents ranked highly by multiple methods
- C) random docs
- D) the newest file

<details><summary>Answer</summary>B — agreement across lists, no score calibration
needed.</details>

**Challenge.** Add an LLM-as-judge rerank: take the RRF top-10 and have the model score each
for relevance to the query, then sort by that score (forward ref to Phase 15).

## Related

- Builds on: [Repo maps](../../01-repo-maps/docs/en.md), [Embeddings](../../02-embeddings/docs/en.md)
- Next: [Chunking code without breaking it](../../04-chunking/docs/en.md)
- Related: Phase 15 — LLM-as-judge
- Other tracks: [RAG architecture](../../../../../content/03-rag/rag-architecture.md) · [Storage & querying](../../../../../knowledge-graphs/storage-and-querying.md) — the retrieval stack and the graph query layer this phase mirrors.
- [Roadmap](../../../../ROADMAP.md)
