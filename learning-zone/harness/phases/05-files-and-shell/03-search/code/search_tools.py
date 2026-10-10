"""Find files by name (glob) and by content (grep). Run:  python3 code/search_tools.py"""
import os
import re
import tempfile
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv"}


def _files(root, pattern):
    root = Path(root)
    for p in root.glob(pattern):
        if p.is_file() and not (set(p.relative_to(root).parts) & SKIP_DIRS):
            yield p


def find_files(pattern, root=".", limit=100):
    """Glob by name. Newest first, capped, so recent files surface."""
    paths = sorted(_files(root, pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    out = [str(p.relative_to(root)) for p in paths[:limit]]
    if len(paths) > limit:
        out.append(f"[truncated: {len(paths)} files match, showing {limit}; narrow the pattern]")
    return out


def grep(pattern, root=".", glob="**/*", context=0, mode="content", limit=50):
    """Regex search by content. mode: content | files_with_matches | count."""
    rx = re.compile(pattern)
    hits, files, counts = [], [], {}
    for p in sorted(_files(root, glob)):
        try:
            lines = p.read_text().splitlines()
        except (UnicodeDecodeError, PermissionError):
            continue                                   # binary or unreadable
        name = str(p.relative_to(root))
        for i, line in enumerate(lines):
            if not rx.search(line):
                continue
            counts[name] = counts.get(name, 0) + 1
            for j in range(max(0, i - context), min(len(lines), i + context + 1)):
                mark = ":" if j == i else "-"
                hits.append(f"{name}{mark}{j + 1}: {lines[j]}")
        if name in counts:
            files.append(name)
    if mode == "files_with_matches":
        return files
    if mode == "count":
        return [f"{n}:{counts[n]}" for n in files]
    if len(hits) > limit:
        return hits[:limit] + [f"[truncated: {len(hits)} lines, showing {limit}]"]
    return hits


if __name__ == "__main__":
    d = tempfile.mkdtemp()
    for rel, body, mtime in [
        ("old.py", "def parse_config():\n    pass\n", 1000),
        ("new.py", "import old\nparse_config()\nparse_config()\n", 2000),
        ("notes.txt", "parse_config is documented here\n", 1500),
        (".git/HEAD", "parse_config in git internals\n", 1500),
        ("node_modules/lib/index.js", "parse_config()\n", 1500),
    ]:
        p = Path(d, rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body)
        os.utime(p, (mtime, mtime))

    # Glob: name filter, newest first, vendored folders skipped.
    assert find_files("**/*.py", d) == ["new.py", "old.py"]
    assert find_files("**/*", d) == ["new.py", "notes.txt", "old.py"]
    assert find_files("**/*", d, limit=1)[-1].startswith("[truncated: 3 files")

    # Grep: path:line locations, context lines use "-", skip dirs are never searched.
    hits = grep(r"def parse_config", d)
    assert hits == ["old.py:1: def parse_config():"]
    ctx = grep(r"import old", d, context=1)
    assert ctx == ["new.py:1: import old", "new.py-2: parse_config()"]
    assert grep("parse_config", d, mode="files_with_matches") == ["new.py", "notes.txt", "old.py"]
    assert grep("parse_config", d, mode="count") == ["new.py:2", "notes.txt:1", "old.py:1"]
    assert not any(".git" in h or "node_modules" in h for h in grep("parse_config", d))
    assert grep("parse_config", d, limit=2)[-1].startswith("[truncated: 4 lines")
    print("ok:", hits[0])
