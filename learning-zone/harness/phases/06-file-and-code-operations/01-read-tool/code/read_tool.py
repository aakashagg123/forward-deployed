"""A numbered, range-bounded read tool. Run:  python3 read_tool.py"""


def read(path, offset=1, limit=2000):
    """Return lines [offset, offset+limit) prefixed with 1-based line numbers."""
    with open(path) as f:
        lines = f.readlines()
    start = max(0, offset - 1)
    chunk = lines[start:start + limit]
    width = len(str(start + len(chunk))) or 1
    return "".join(f"{start+i+1:>{width}}  {ln}" for i, ln in enumerate(chunk))


if __name__ == "__main__":
    import tempfile
    import os
    p = tempfile.mktemp()
    open(p, "w").write("\n".join(f"content {i}" for i in range(1, 21)) + "\n")
    print(read(p, offset=5, limit=3))
    os.remove(p)
