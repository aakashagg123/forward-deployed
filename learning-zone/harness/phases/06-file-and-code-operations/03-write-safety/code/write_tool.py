"""Read-gated write tool: only overwrite files read this session. Run: python3 write_tool.py"""
import os


class FileWriter:
    def __init__(self):
        self.read_files = set()

    def read(self, path):
        self.read_files.add(os.path.abspath(path))
        with open(path) as f:
            return f.read()

    def write(self, path, content):
        ap = os.path.abspath(path)
        if os.path.exists(ap) and ap not in self.read_files:
            return "error: refusing to overwrite a file you haven't read this session"
        with open(ap, "w") as f:
            f.write(content)
        self.read_files.add(ap)
        return "ok: wrote " + path


if __name__ == "__main__":
    import tempfile
    fw = FileWriter()
    p = tempfile.mktemp()
    print(fw.write(p, "v1"))                 # new: ok
    open(p, "w").write("changed out-of-band")
    print(fw.write(p, "v2"))                 # exists, not read -> denied
    fw.read(p)
    print(fw.write(p, "v2"))                 # now allowed
    os.remove(p)
