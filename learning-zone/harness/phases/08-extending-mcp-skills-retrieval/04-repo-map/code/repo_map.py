"""A repo map (file -> symbols with line numbers) plus structural code chunks.

Handles top-level and nested definitions, decorators, async defs, syntax errors.
Run:  python3 code/repo_map.py
"""
import ast
import os
import tempfile

DEFS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules"}


def _start(node):
    """First line of a definition, including its decorators."""
    return min([node.lineno] + [d.lineno for d in node.decorator_list])


def symbols(source, prefix="", body=None):
    """List every def/class, nested ones too, with qualified names like Session.open."""
    out = []
    for node in ast.parse(source).body if body is None else body:
        if isinstance(node, DEFS):
            name = prefix + node.name
            kind = "class" if isinstance(node, ast.ClassDef) else "def"
            out.append({"name": name, "kind": kind, "line": _start(node), "end": node.end_lineno})
            out += symbols(source, name + ".", node.body)
    return out


def build_map(root):
    repo, skipped = {}, []
    for dp, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for fn in sorted(files):
            if fn.endswith(".py"):
                path = os.path.join(dp, fn)
                try:
                    with open(path, encoding="utf-8") as f:
                        repo[os.path.relpath(path, root)] = symbols(f.read())
                except (SyntaxError, UnicodeDecodeError):
                    skipped.append(os.path.relpath(path, root))   # report, do not hide
    return repo, skipped


def render(repo):
    """The compact text map that goes into the agent's context."""
    lines = []
    for path, syms in sorted(repo.items()):
        lines.append(path)
        lines += [f"  {s['kind']} {s['name']}:{s['line']}" for s in syms]
    return "\n".join(lines)


def search(repo, query):
    """Lexical search. Exact symbol name beats prefix, prefix beats substring, then path."""
    q, hits = query.lower(), []
    for path, syms in repo.items():
        for s in syms:
            leaf = s["name"].split(".")[-1].lower()
            score = 3 if leaf == q else 2 if leaf.startswith(q) else 1 if q in s["name"].lower() else 0
            if score:
                hits.append((score, f"{path}:{s['line']}  {s['name']}"))
        if q in path.lower() and not any(h[1].startswith(path + ":") for h in hits):
            hits.append((0, f"{path}:1"))
    return [h for _, h in sorted(hits, key=lambda h: (-h[0], h[1]))]


def chunks(source, max_lines=20):
    """One chunk per top-level def/class. A class over max_lines splits into its methods."""
    lines = source.splitlines()

    def make(name, node):
        a, b = _start(node), node.end_lineno
        return {"name": name, "lines": (a, b), "code": "\n".join(lines[a - 1:b])}

    out = []
    for node in ast.parse(source).body:
        if not isinstance(node, DEFS):
            continue
        if isinstance(node, ast.ClassDef) and node.end_lineno - _start(node) + 1 > max_lines:
            out += [make(f"{node.name}.{m.name}", m) for m in node.body if isinstance(m, DEFS)]
        else:
            out.append(make(node.name, node))
    return out


if __name__ == "__main__":
    SRC = ("import os\n\n"
           "def login(u):\n    return u\n\n"
           "@cache\n@trace\nasync def fetch(url):\n    def retry():\n        pass\n    return url\n\n"
           "class Session:\n    def open(self):\n        return True\n    def close(self):\n        pass\n")
    syms = {s["name"]: s for s in symbols(SRC)}
    assert list(syms) == ["login", "fetch", "fetch.retry", "Session", "Session.open", "Session.close"]
    assert syms["fetch"]["line"] == 6 and syms["Session.open"]["line"] == 14   # decorators counted
    c = {x["name"]: x for x in chunks(SRC)}
    assert list(c) == ["login", "fetch", "Session"]
    assert c["fetch"]["code"].startswith("@cache") and c["fetch"]["lines"] == (6, 11)
    split = {x["name"]: x for x in chunks(SRC, max_lines=3)}     # small limit splits the class
    assert "Session.open" in split and split["Session.close"]["code"].lstrip().startswith("def close")

    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "pkg"))
        for rel, text in {"auth.py": SRC, "pkg/util.py": "def login_helper():\n    pass\n",
                          "broken.py": "def oops(:\n"}.items():
            with open(os.path.join(d, rel), "w") as f:
                f.write(text)
        repo, skipped = build_map(d)
        assert skipped == ["broken.py"] and set(repo) == {"auth.py", os.path.join("pkg", "util.py")}
        hits = search(repo, "login")
        assert hits[0] == "auth.py:3  login"                     # exact name ranks first
        assert hits[1].endswith("login_helper")                  # prefix match second
        print(render(repo).splitlines()[0:4])
    print("repo_map: all checks passed")
