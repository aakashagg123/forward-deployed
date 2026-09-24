"""Exact-string edit with a uniqueness guard. Run:  python3 edit_tool.py"""


def edit(path, old, new, replace_all=False):
    with open(path) as f:
        text = f.read()
    count = text.count(old)
    if count == 0:
        return "error: old_string not found"
    if count > 1 and not replace_all:
        return f"error: old_string is ambiguous ({count} matches) — add surrounding context"
    with open(path, "w") as f:
        f.write(text.replace(old, new))
    return f"ok: {count if replace_all else 1} replacement(s)"


if __name__ == "__main__":
    import tempfile
    import os
    p = tempfile.mktemp()
    open(p, "w").write("def add(a, b):\n    return a + b\n")
    print(edit(p, "return a + b", "return a + b  # sum"))
    print(edit(p, "nope", "x"))
    os.remove(p)
