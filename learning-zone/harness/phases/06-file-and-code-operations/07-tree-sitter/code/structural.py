"""Structural code queries. Uses stdlib `ast` (Python-only) as a runnable stand-in for
tree-sitter, which generalizes the same idea to many languages.

Run:  python3 structural.py
"""
import ast


def list_functions(source):
    tree = ast.parse(source)
    return [(n.name, n.lineno) for n in ast.walk(tree)
            if isinstance(n, ast.FunctionDef)]


def functions_missing_docstring(source):
    tree = ast.parse(source)
    return [n.name for n in ast.walk(tree)
            if isinstance(n, ast.FunctionDef) and ast.get_docstring(n) is None]


if __name__ == "__main__":
    src = "def a():\n    'doc'\n    pass\ndef b():\n    pass\n"
    print("functions:", list_functions(src))
    print("missing docstring:", functions_missing_docstring(src))
