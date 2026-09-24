"""Atomic multi-hunk patch applier: validate every hunk, then apply all or none.

Run:  python3 patch.py
"""


def apply_patch(hunks, read, write):
    """hunks: [(path, old, new)]. read(path)->str, write(path,str). Atomic."""
    staged = {}
    for path, old, new in hunks:
        text = staged.get(path, read(path))
        if text.count(old) != 1:
            return f"reject: hunk for {path} matches {text.count(old)}x (need exactly 1)"
        staged[path] = text.replace(old, new)
    for path, text in staged.items():        # only reached if every hunk validated
        write(path, text)
    return f"applied {len(hunks)} hunk(s) across {len(staged)} file(s)"


if __name__ == "__main__":
    files = {"a.py": "x = 1\n", "b.py": "y = 2\n"}
    res = apply_patch(
        [("a.py", "x = 1", "x = 10"), ("b.py", "y = 2", "y = 20")],
        read=lambda p: files[p], write=lambda p, t: files.__setitem__(p, t))
    print(res)
    print(files)
    # A failing hunk rejects the whole patch:
    print(apply_patch([("a.py", "nope", "z")], lambda p: files[p], lambda p, t: None))
