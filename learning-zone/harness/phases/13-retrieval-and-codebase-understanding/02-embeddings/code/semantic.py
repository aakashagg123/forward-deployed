"""Toy bag-of-words embedder + cosine semantic search. Run: python3 semantic.py

A real embedding model replaces `embed`; the embed/index/cosine-rank pipeline is the same.
"""
import math
from collections import Counter


def embed(text):                       # toy: word-count vector
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


if __name__ == "__main__":
    ix = SemanticIndex()
    for doc in ["def login(): authenticate the user",
                "def add(a, b): return a + b",
                "class Session: user session state"]:
        ix.add(doc)
    print("top hit:", ix.search("authenticate user")[0])
