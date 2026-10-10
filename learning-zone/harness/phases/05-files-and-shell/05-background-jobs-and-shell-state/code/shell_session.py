"""Shell state across calls: keep cwd, drop env, like Claude Code's Bash tool.

Run:  python3 code/shell_session.py
"""
import os
import subprocess
import tempfile


class ShellSession:
    def __init__(self, project_dir, env_file=None):
        self.root = os.path.realpath(project_dir)
        self.cwd = self.root
        self.env_file = env_file            # sourced before every command (like CLAUDE_ENV_FILE)

    def run(self, command, timeout=10):
        fd, state = tempfile.mkstemp()
        os.close(fd)
        script = f"trap 'pwd -P > {state}' EXIT\n"        # record where the command ended
        if self.env_file:
            script += f". {self.env_file}\n"
        script += command + "\n"
        p = subprocess.run(["bash", "-c", script], cwd=self.cwd, capture_output=True,
                           text=True, timeout=timeout, stdin=subprocess.DEVNULL)
        with open(state) as f:
            end = f.read().strip()
        os.remove(state)
        note = ""
        if end == self.root or end.startswith(self.root + os.sep):
            self.cwd = end                                # cd inside the project sticks
        else:
            self.cwd = self.root                          # cd outside the project is undone
            note = f"\nShell cwd was reset to {self.root}"
        return {"exit_code": p.returncode, "stdout": p.stdout + note, "stderr": p.stderr}


if __name__ == "__main__":
    root = tempfile.mkdtemp()
    os.makedirs(os.path.join(root, "backend", "src"))
    s = ShellSession(root)
    real = s.root

    # One subprocess.run per call forgets everything. This session keeps cwd.
    assert subprocess.run("cd backend", shell=True, cwd=real).returncode == 0
    assert subprocess.run("pwd", shell=True, cwd=real, capture_output=True,
                          text=True).stdout.strip() == real     # plain run: cwd lost
    s.run("cd backend")
    assert s.run("pwd")["stdout"].strip() == real + "/backend"
    s.run("cd src && true")                                     # compound commands work too
    assert s.cwd == real + "/backend/src"

    # export does not persist, as in Claude Code.
    s.run("export TOKEN=abc")
    assert s.run("echo [$TOKEN]")["stdout"].strip() == "[]"

    # An env file does persist, because it is sourced on every call.
    envf = os.path.join(root, "env.sh")
    with open(envf, "w") as f:
        f.write("export TOKEN=abc\n")
    s2 = ShellSession(root, env_file=envf)
    assert s2.run("echo [$TOKEN]")["stdout"].strip() == "[abc]"

    # cd outside the project is reset, with a note the model can read.
    r = s.run("cd /")
    assert s.cwd == real and "Shell cwd was reset to" in r["stdout"]

    # The exit code survives the state capture.
    assert s.run("exit 4")["exit_code"] == 4
    print("ok: cwd kept, env dropped, env file kept")
