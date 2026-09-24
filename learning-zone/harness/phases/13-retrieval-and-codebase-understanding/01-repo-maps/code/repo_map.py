"""Build a symbol repo map (via ast) and lexical-search it. Run: python3 repo_map.py"""
import ast
import os


def build_map(root):
    repo = {}
    for dp, _, files in os.walk(root):
        for fn in files:
            if fn.endswith(".py"):
                path = os.path.join(dp, fn)
                try:
                    tree = ast.parse(open(path).read())
                except SyntaxError:
                    continue
                repo[path] = [n.name for n in ast.walk(tree)
                              if isinstance(n, (ast.FunctionDef, ast.ClassDef))]
    return repo


def search(repo, query):
    q = query.lower()
    return [(path, syms) for path, syms in repo.items()
            if q in path.lower() or any(q in s.lower() for s in syms)]


if __name__ == "__main__":
    import tempfile
    d = tempfile.mkdtemp()
    open(os.path.join(d, "auth.py"), "w").write("def login(): pass\nclass Session: pass\n")
    m = build_map(d)
    print([(os.path.basename(p), s) for p, s in search(m, "login")])
