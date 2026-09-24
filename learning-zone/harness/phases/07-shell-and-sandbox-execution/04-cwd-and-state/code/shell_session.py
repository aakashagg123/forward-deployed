"""A shell session that persists cwd across calls. Run:  python3 shell_session.py"""
import os
import subprocess


class ShellSession:
    def __init__(self, cwd=None, env=None):
        self.cwd = cwd or os.getcwd()
        self.env = dict(os.environ, **(env or {}))

    def run(self, command):
        if command.strip().startswith("cd "):                 # simplified cd handling
            target = command.strip()[3:].strip()
            new = os.path.normpath(os.path.join(self.cwd, target))
            if os.path.isdir(new):
                self.cwd = new
                return {"exit_code": 0, "stdout": f"cwd={self.cwd}", "stderr": ""}
            return {"exit_code": 1, "stdout": "", "stderr": f"no such dir: {target}"}
        p = subprocess.run(command, shell=True, cwd=self.cwd, env=self.env,
                           capture_output=True, text=True)
        return {"exit_code": p.returncode, "stdout": p.stdout, "stderr": p.stderr}


if __name__ == "__main__":
    import tempfile
    d = tempfile.mkdtemp()
    os.mkdir(os.path.join(d, "sub"))
    s = ShellSession(cwd=d)
    s.run("cd sub")
    print("cwd persisted:", s.run("pwd")["stdout"].strip().endswith("/sub"))
