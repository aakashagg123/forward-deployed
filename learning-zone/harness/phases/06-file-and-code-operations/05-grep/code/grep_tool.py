"""Regex content search with line numbers and optional context. Run: python3 grep_tool.py"""
import re
from pathlib import Path


def grep(pattern, root=".", glob="**/*", context=0):
    rx = re.compile(pattern)
    hits = []
    for p in Path(root).glob(glob):
        if not p.is_file():
            continue
        try:
            lines = p.read_text().splitlines()
        except (UnicodeDecodeError, PermissionError):
            continue
        for i, line in enumerate(lines):
            if rx.search(line):
                lo, hi = max(0, i - context), min(len(lines), i + context + 1)
                for j in range(lo, hi):
                    mark = ":" if j == i else "-"
                    hits.append(f"{p}{mark}{j+1}: {lines[j]}")
    return hits


if __name__ == "__main__":
    import tempfile
    import os
    d = tempfile.mkdtemp()
    open(os.path.join(d, "x.py"), "w").write("def parse_config():\n    return {}\n")
    for h in grep(r"parse_config", root=d):
        print(h)
