"""Lint a memory file (CLAUDE.md / AGENTS.md) and model how Claude Code loads one.

Run:  python3 code/memory_lint.py
"""
import os
import re
import tempfile

MAX_LINES = 200                      # Claude Code docs: aim under 200 lines per file
MAX_IMPORT_DEPTH = 4                 # imports can chain at most four hops
VAGUE = ["format code properly", "test your changes", "keep files organized", "write clean code"]
SCOPES = ["managed", "user", "project", "local"]      # broadest first; the last one read wins


def strip_comments(text):
    """HTML comments are removed before the file reaches the model. Code fences are kept."""
    parts = re.split(r"(```.*?```)", text, flags=re.S)
    return "".join(p if i % 2 else re.sub(r"<!--.*?-->", "", p, flags=re.S)
                   for i, p in enumerate(parts))


def expand(text, files, depth=0):
    """Add every @imported file. Imports organize a file; they do not make it cheaper."""
    text = strip_comments(text)
    prose = re.sub(r"`[^`]*`", "", text)                      # an import in backticks is literal
    names = re.findall(r"(?<![\w`])@([\w./~-]+)", prose)
    extra = [expand(files[n], files, depth + 1) for n in names
             if n in files and depth < MAX_IMPORT_DEPTH]
    return "\n".join([text] + extra)


def lint(text, files=None, root=None):
    problems = []
    full = expand(text, files or {})
    lines = [line for line in full.splitlines() if line.strip()]
    if len(lines) > MAX_LINES:
        problems.append(f"{len(lines)} lines after imports; keep under {MAX_LINES}")
    for phrase in VAGUE:
        if phrase in full.lower():
            problems.append(f"vague instruction: {phrase!r}")
    if re.search(r"\b20\d\d-\d\d-\d\d\b", full):
        problems.append("date in a memory file goes stale")
    for ref in re.findall(r"`((?:docs|src)/[\w./-]+)`", full):   # a pointer to a missing file is a trap
        if root and not os.path.exists(os.path.join(root, ref)):
            problems.append(f"pointer to a missing file: {ref}")
    return problems


def which_files(files):
    """Project files Claude Code reads. AGENTS.md is read only when no CLAUDE.md exists."""
    claude = [n for n in files if n in ("CLAUDE.md", "CLAUDE.local.md")]
    return ["AGENTS.md"] if "AGENTS.md" in files and not claude else claude


def load_order(layers):
    """Concatenate layers broadest first, so the most specific text is read last."""
    return "\n\n".join(layers[s] for s in SCOPES if s in layers)


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    lean = open(os.path.join(here, "..", "outputs", "CLAUDE.md")).read()
    root = tempfile.mkdtemp()
    os.mkdir(os.path.join(root, "docs"))
    for name in ("architecture", "pricing", "testing"):
        open(os.path.join(root, "docs", f"{name}.md"), "w").write("# " + name)

    # 1. The shipped example is lean, concrete, and every pointer resolves.
    n = len([line for line in strip_comments(lean).splitlines() if line.strip()])
    print(f"outputs/CLAUDE.md: {n} lines, problems: {lint(lean, root=root)}")
    assert lint(lean, root=root) == [] and n < 40
    assert "Maintainer note" not in strip_comments(lean)                  # comments cost nothing
    # 2. The lint catches the failure modes.
    assert any("missing file" in p for p in lint(lean, root=tempfile.mkdtemp()))
    assert any("vague" in p for p in lint("- Test your changes.\n- Keep files organized."))
    assert any("lines" in p for p in lint("\n".join(f"- rule {i}" for i in range(250))))
    # 3. Moving text behind an @import does not hide it from the budget.
    big = "\n".join(f"- rule {i}" for i in range(250))
    assert any("lines" in p for p in lint("See @docs/rules.md for rules.", {"docs/rules.md": big}))
    assert not any("lines" in p for p in lint("See `@docs/rules.md` for rules.", {"docs/rules.md": big}))
    # 4. AGENTS.md is read alone, ignored beside CLAUDE.md, or pulled in by an import.
    assert which_files({"AGENTS.md": ""}) == ["AGENTS.md"]
    assert which_files({"AGENTS.md": "", "CLAUDE.md": ""}) == ["CLAUDE.md"]
    assert "use pnpm" in expand("@AGENTS.md", {"AGENTS.md": "use pnpm"})
    # 5. The closest file is read last.
    order = load_order({"project": "PROJECT", "user": "USER", "local": "LOCAL"})
    assert order.index("USER") < order.index("PROJECT") < order.index("LOCAL")
    print("memory lint ok")
