"""A `search_code` retrieval tool composing the phase (chunk + embed + search).

Self-contained with a toy embedder so it runs; swap in a real model + RRF hybrid for
production. Run:  python3 retrieval_tool.py
"""
import ast
import math
from collections import Counter


def chunk_code(source):                    # lesson 04
    tree = ast.parse(source)
    lines = source.splitlines()
    out = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            start = node.lineno - 1
            end = getattr(node, "end_lineno", start + 1)
            out.append({"name": node.name, "lines": (node.lineno, end),
                        "code": "\n".join(lines[start:end])})
    return out


def _embed(text):                          # lesson 02 (toy)
    return Counter(text.lower().split())


def _cosine(a, b):
    dot = sum(a[k] * b.get(k, 0) for k in a)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    return dot / (na * nb) if na and nb else 0.0


class CodeSearch:
    def __init__(self):
        self.entries = []                  # (vector, meta)

    def add_file(self, path, source):
        for ch in chunk_code(source):
            self.entries.append((_embed(ch["code"]),
                                 {"path": path, "name": ch["name"], "lines": ch["lines"]}))

    def search_code(self, query, k=3):
        qv = _embed(query)
        ranked = sorted(self.entries, key=lambda e: _cosine(qv, e[0]), reverse=True)
        return [f"{m['path']}:{m['lines'][0]}  {m['name']}" for _, m in ranked[:k]]


if __name__ == "__main__":
    cs = CodeSearch()
    cs.add_file("auth.py", "def login(u):\n    'authenticate the user'\n    return u\n")
    cs.add_file("math.py", "def add(a, b):\n    return a + b\n")
    print(cs.search_code("authenticate user", k=1))
