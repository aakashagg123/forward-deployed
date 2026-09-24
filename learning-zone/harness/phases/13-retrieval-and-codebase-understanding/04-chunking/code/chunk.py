"""Structural (function/class) code chunking via ast. Run: python3 chunk.py"""
import ast


def chunk_code(source):
    tree = ast.parse(source)
    lines = source.splitlines()
    chunks = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            start = node.lineno - 1
            end = getattr(node, "end_lineno", start + 1)
            chunks.append({"name": node.name, "lines": (node.lineno, end),
                           "code": "\n".join(lines[start:end])})
    return chunks


if __name__ == "__main__":
    src = ("import os\n\n"
           "def login(u):\n    return u\n\n"
           "class Session:\n    def open(self):\n        return True\n")
    for c in chunk_code(src):
        print(c["name"], c["lines"])
