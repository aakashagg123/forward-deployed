"""Recency-sorted glob file discovery. Run:  python3 glob_tool.py"""
from pathlib import Path


def glob(pattern, root="."):
    paths = [p for p in Path(root).glob(pattern) if p.is_file()]
    paths.sort(key=lambda p: p.stat().st_mtime, reverse=True)   # recent first
    return [str(p) for p in paths]


if __name__ == "__main__":
    import tempfile
    import os
    import time
    d = tempfile.mkdtemp()
    for n in ["a.py", "b.py", "c.txt"]:
        open(os.path.join(d, n), "w").write("x")
        time.sleep(0.01)
    print([os.path.basename(p) for p in glob("*.py", root=d)])
