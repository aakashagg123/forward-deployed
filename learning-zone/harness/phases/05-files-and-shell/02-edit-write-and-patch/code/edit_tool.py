"""Exact-string edit, read-gated write, atomic patch. Run:  python3 code/edit_tool.py"""
import hashlib
import os
import tempfile


def _digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def _write_atomic(path, text):
    """Write to a temp file in the same folder, then rename over the target."""
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(path)))
    with os.fdopen(fd, "w") as f:
        f.write(text)
    os.replace(tmp, path)


class Workspace:
    def __init__(self):
        self.seen = {}                       # abs path -> digest at last read

    def read(self, path):
        with open(path) as f:
            text = f.read()
        self.seen[os.path.abspath(path)] = _digest(text)
        return text

    def edit(self, path, old, new, replace_all=False):
        ap = os.path.abspath(path)
        if ap not in self.seen:
            return "error: read the file before you edit it"
        with open(ap) as f:
            text = f.read()
        n = text.count(old)
        if n == 0:
            return "error: old_string not found"
        if n > 1 and not replace_all:
            return f"error: old_string matches {n} times; add surrounding context"
        _write_atomic(ap, text.replace(old, new))
        self.seen[ap] = _digest(text.replace(old, new))
        return f"ok: {n if replace_all else 1} replacement(s)"

    def write(self, path, content):
        ap = os.path.abspath(path)
        if os.path.exists(ap):
            if ap not in self.seen:
                return "error: file exists and was not read this session"
            with open(ap) as f:
                if _digest(f.read()) != self.seen[ap]:
                    return "error: file changed since you read it; read it again"
        _write_atomic(ap, content)
        self.seen[ap] = _digest(content)
        return "ok: wrote " + path

    def apply_patch(self, hunks):
        """hunks: [(path, old, new)]. Validate every hunk, then write all or none."""
        staged = {}
        for path, old, new in hunks:
            ap = os.path.abspath(path)
            if ap not in self.seen:
                return f"reject: {path} was not read"
            if ap not in staged:
                with open(ap) as f:
                    staged[ap] = f.read()
            n = staged[ap].count(old)
            if n != 1:
                return f"reject: hunk for {path} matches {n} times (need 1); nothing written"
            staged[ap] = staged[ap].replace(old, new)
        for ap, text in staged.items():      # reached only if every hunk passed
            _write_atomic(ap, text)
            self.seen[ap] = _digest(text)
        return f"applied {len(hunks)} hunk(s) in {len(staged)} file(s)"


if __name__ == "__main__":
    d = tempfile.mkdtemp()
    a, b = os.path.join(d, "a.py"), os.path.join(d, "b.py")
    open(a, "w").write("x = 1\ny = 1\n")
    open(b, "w").write("z = 2\n")
    ws = Workspace()

    # Edit needs a prior read, then needs exactly one match.
    assert ws.edit(a, "x = 1", "x = 10").startswith("error: read the file")
    ws.read(a)
    assert ws.edit(a, "nope", "q") == "error: old_string not found"
    assert "matches 2 times" in ws.edit(a, " = 1", " = 5")
    assert ws.edit(a, " = 1", " = 5", replace_all=True) == "ok: 2 replacement(s)"
    assert open(a).read() == "x = 5\ny = 5\n"

    # Write: new files are fine. Existing files need a fresh read.
    new = os.path.join(d, "new.txt")
    assert ws.write(new, "v1").startswith("ok")
    assert ws.write(b, "clobber").startswith("error: file exists and was not read")
    assert open(b).read() == "z = 2\n"                 # untouched
    ws.read(b)
    open(b, "w").write("changed outside\n")            # someone else edits it
    assert ws.write(b, "clobber").startswith("error: file changed")
    ws.read(b)
    assert ws.write(b, "v2").startswith("ok")

    # Patch is atomic: one bad hunk means no file changes.
    ws.read(a)
    before = (open(a).read(), open(b).read())
    res = ws.apply_patch([(a, "x = 5", "x = 11"), (b, "missing", "zzz")])
    assert res.startswith("reject") and (open(a).read(), open(b).read()) == before
    res = ws.apply_patch([(a, "x = 5", "x = 11"), (a, "x = 11", "x = 12"), (b, "v2", "v3")])
    assert res == "applied 3 hunk(s) in 2 file(s)"
    assert open(a).read() == "x = 12\ny = 5\n" and open(b).read() == "v3"
    print("ok:", res)
