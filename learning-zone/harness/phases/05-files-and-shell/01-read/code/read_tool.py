"""A numbered, bounded read tool. Run:  python3 code/read_tool.py"""
import os
import tempfile


def read(path, offset=1, limit=2000, max_line_chars=200):
    """Return lines [offset, offset+limit) with 1-based line numbers.

    Long lines are cut with a marker. A footer tells the model how to continue.
    """
    if not os.path.isfile(path):
        return f"error: no such file: {path}"
    with open(path, "rb") as f:
        if b"\0" in f.read(8192):
            return f"error: {path} looks binary; read refused"
    with open(path, encoding="utf-8", errors="replace") as f:
        lines = f.read().splitlines()
    total = len(lines)
    if total == 0:
        return f"(file exists but is empty: {path})"
    if offset > total:
        return f"error: offset {offset} is past the end ({total} lines)"
    start = max(0, offset - 1)
    end = min(total, start + limit)
    width = len(str(end))
    out = []
    for i in range(start, end):
        text = lines[i]
        if len(text) > max_line_chars:
            text = text[:max_line_chars] + f"...[line cut, {len(lines[i])} chars]"
        out.append(f"{i + 1:>{width}}  {text}")
    if end < total:
        out.append(f"[showing lines {start + 1}-{end} of {total}; call read with offset={end + 1}]")
    return "\n".join(out)


if __name__ == "__main__":
    d = tempfile.mkdtemp()
    p = os.path.join(d, "f.txt")
    with open(p, "w") as f:
        f.write("\n".join(f"content {i}" for i in range(1, 21)) + "\n")
    print(read(p, offset=5, limit=3))

    # Numbers are real, 1-based file positions, not positions in the slice.
    out = read(p, offset=5, limit=3).splitlines()
    assert out[0].endswith("content 5") and out[0].lstrip().startswith("5")
    assert out[2].endswith("content 7")
    # The footer tells the model exactly how to page on.
    assert out[3] == "[showing lines 5-7 of 20; call read with offset=8]"
    # A read that reaches the end has no footer.
    assert "[showing" not in read(p, offset=18, limit=10)
    # Long lines are cut so one minified line cannot fill the budget.
    long_path = os.path.join(d, "min.js")
    with open(long_path, "w") as f:
        f.write("x" * 5000 + "\n")
    cut = read(long_path)
    assert len(cut) < 300 and "line cut, 5000 chars" in cut
    # Error paths return text, not exceptions.
    assert read(os.path.join(d, "nope")).startswith("error: no such file")
    assert read(p, offset=99).startswith("error: offset 99")
    bin_path = os.path.join(d, "b.bin")
    with open(bin_path, "wb") as f:
        f.write(b"\x00\x01\x02")
    assert "binary" in read(bin_path)
    print("ok")
