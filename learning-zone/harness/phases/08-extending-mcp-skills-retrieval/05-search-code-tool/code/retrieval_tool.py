"""A search_code tool: chunk code, index it with TF-IDF, return path:line hits.

TF-IDF is a lexical scorer, not a semantic embedding. It matches shared words.
Run:  python3 code/retrieval_tool.py
"""
import ast
import math
import os
import re
import tempfile
from collections import Counter
from pathlib import Path

DEFS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


def tokens(text):
    """Lowercase words. Split snake_case and camelCase so `loginUser` matches `login`."""
    spaced = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    return [w for w in re.findall(r"[A-Za-z]+", spaced.lower()) if len(w) > 2]


def chunk_file(path, source):
    """One chunk per top-level def/class (decorators included)."""
    lines, out = source.splitlines(), []
    for node in ast.parse(source).body:
        if isinstance(node, DEFS):
            a = min([node.lineno] + [d.lineno for d in node.decorator_list])
            out.append({"path": path, "name": node.name, "line": a,
                        "text": "\n".join(lines[a - 1:node.end_lineno])})
    return out


class CodeSearch:
    def __init__(self):
        self.chunks, self.df = [], Counter()

    def add_file(self, path, source):
        for ch in chunk_file(path, source):
            ch["tf"] = Counter(tokens(ch["name"]) * 2 + tokens(ch["text"]))   # name counts double
            self.df.update(ch["tf"].keys())
            self.chunks.append(ch)

    def index_dir(self, root):
        for dp, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", ".venv"}]
            for fn in sorted(files):
                if fn.endswith(".py"):
                    p = os.path.join(dp, fn)
                    try:
                        self.add_file(os.path.relpath(p, root), Path(p).read_text(encoding="utf-8"))
                    except (SyntaxError, UnicodeDecodeError):
                        pass                           # unparseable files are skipped

    def search_code(self, query, k=3):
        n, scored = len(self.chunks), []
        for ch in self.chunks:
            score = sum(ch["tf"][w] * math.log(1 + n / self.df[w]) for w in set(tokens(query))
                        if w in ch["tf"])
            if score > 0:                              # no shared word, no hit
                scored.append((score, f"{ch['path']}:{ch['line']}  {ch['name']}"))
        return [h for _, h in sorted(scored, reverse=True)[:k]]


TOOL_SPEC = {"name": "search_code",
             "description": "Find code by words. Returns path:line hits. Read the file to see the code.",
             "inputSchema": {"type": "object", "required": ["query"],
                             "properties": {"query": {"type": "string"},
                                            "k": {"type": "integer", "default": 3}}}}


def tool_call(search, arguments):
    """The tools/call step: MCP-shaped result, isError for bad input."""
    if not arguments.get("query", "").strip():
        return {"content": [{"type": "text", "text": "query is empty"}], "isError": True}
    hits = search.search_code(arguments["query"], arguments.get("k", 3))
    return {"content": [{"type": "text", "text": "\n".join(hits) or "no matches"}], "isError": False}


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as d:
        files = {
            "auth.py": "def login_user(name):\n    'authenticate the user by name'\n    return name\n",
            "calc.py": "def add(a, b):\n    return a + b\n\n@cache\nclass Total:\n    def sum(self):\n        return 0\n",
            "broken.py": "def oops(:\n",
        }
        for rel, text in files.items():
            with open(os.path.join(d, rel), "w") as f:
                f.write(text)
        cs = CodeSearch()
        cs.index_dir(d)
        assert len(cs.chunks) == 3                                  # broken.py skipped
        assert cs.search_code("authenticate user") == ["auth.py:1  login_user"]
        assert cs.search_code("loginUser")[0] == "auth.py:1  login_user"   # camelCase splits
        assert cs.search_code("total", k=1) == ["calc.py:4  Total"]         # decorator line
        assert cs.search_code("kubernetes helm") == []              # nothing shared: no hits
        ok = tool_call(cs, {"query": "kubernetes"})
        assert ok["isError"] is False and ok["content"][0]["text"] == "no matches"
        assert tool_call(cs, {"query": "total"})["content"][0]["text"] == "calc.py:4  Total"
        assert tool_call(cs, {"query": "  "})["isError"] is True
        print(cs.search_code("authenticate user"))
    print("retrieval_tool: all checks passed")
