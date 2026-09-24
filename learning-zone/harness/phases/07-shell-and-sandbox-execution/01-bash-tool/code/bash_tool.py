"""A bash tool: capture stdout, stderr, and exit code. Run:  python3 bash_tool.py"""
import subprocess


def run(command, cwd=None):
    proc = subprocess.run(command, shell=True, cwd=cwd,
                          capture_output=True, text=True)
    return {"stdout": proc.stdout, "stderr": proc.stderr, "exit_code": proc.returncode}


def format_result(r, max_chars=4000):
    out = r["stdout"] + (("\n[stderr]\n" + r["stderr"]) if r["stderr"] else "")
    if len(out) > max_chars:
        out = out[:max_chars] + "\n…[truncated]"
    return f"exit={r['exit_code']}\n{out}".rstrip()


if __name__ == "__main__":
    print(format_result(run("echo hello && echo oops 1>&2")))
    print(format_result(run("exit 3")))
