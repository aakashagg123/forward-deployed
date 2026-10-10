"""Build a five-section system prompt, lint it, and back a rule with real enforcement.

Run:  python3 code/prompt_builder.py
"""
import re

SECTIONS = ["Role", "Constraints", "Tools", "Workflow", "Output contract"]   # stable order

# Reusable steering lines: name -> (section, text). Steering is advice, not enforcement.
STEERING = {
    "terse": ("Output contract", "Be terse. No preamble or postamble. Lead with the answer."),
    "ask_first": ("Workflow", "Make reversible, in-scope changes directly. Before an irreversible "
                              "or out-of-scope action, state a one-line plan and wait."),
    "refuse_well": ("Constraints", "If you cannot or should not do something, say so in one sentence "
                                   "and offer the nearest safe alternative."),
    "honest_report": ("Output contract", "If tests fail, say so and show the output. Do not claim "
                                         "success you did not verify."),
}

VOLATILE = [r"\b20\d\d-\d\d-\d\d\b", r"\b\d{1,2}:\d{2}(:\d{2})?\b", r"/(home|Users)/\w+",
            r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", r"(?i)\btoday is\b"]
MUST = ("Never", "Always", "Do not", "Before", "If")


def build_prompt(role, constraints, tools, workflow, output, steering=()):
    body = {"Role": [role], "Constraints": list(constraints), "Tools": list(tools),
            "Workflow": list(workflow), "Output contract": list(output)}
    for name in steering:
        section, text = STEERING[name]
        body[section].append(text)
    return "\n\n".join(f"## {s}\n" + "\n".join(f"- {line}" for line in body[s]) for s in SECTIONS)


def lint(prompt, max_words=400):
    problems = []
    heads = re.findall(r"^## (.+)$", prompt, re.M)
    if heads != SECTIONS:
        problems.append(f"sections must be {SECTIONS} in order, got {heads}")
    for pat in VOLATILE:
        if re.search(pat, prompt):
            problems.append(f"volatile data breaks the cached prefix: /{pat}/")
    block = re.search(r"## Constraints\n(.*?)\n\n## Tools", prompt, re.S)
    for line in (block.group(1).splitlines() if block else []):
        if not line[2:].startswith(MUST):
            problems.append(f"constraint is not an imperative: {line[2:]!r}")
    if len(prompt.split()) > max_words:
        problems.append("prompt is too long: it buries the rules that matter")
    return problems


def guard(tool, args):
    """A model of a PreToolUse hook: code that enforces the rule whatever the model says."""
    if tool in ("edit", "write") and args.get("path", "").split("/")[-1].startswith(".env"):
        return "deny", "never edit .env files"
    return "allow", ""


SPEC = dict(
    role="You are a coding agent that edits this repository and runs its tests.",
    constraints=["Never edit .env files or commit secrets.",
                 "Always run the test suite before you say a task is done."],
    tools=["Use grep to find code; use read once you know the file.",
           "Do not use bash for file edits; use the edit tool."],
    workflow=["Understand, plan, make the smallest change, verify."],
    output=["Cite code as path:line."],
    steering=["terse", "ask_first", "refuse_well", "honest_report"])


if __name__ == "__main__":
    prompt = build_prompt(**SPEC)
    print(prompt)

    # 1. The prompt is deterministic, so the cached prefix is byte-identical on every call.
    assert prompt == build_prompt(**SPEC)
    assert lint(prompt) == [], lint(prompt)
    # 2. Each steering line lands in the section it belongs to.
    assert prompt.index("Be terse") > prompt.index("## Output contract")
    assert prompt.index("wait.") < prompt.index("## Output contract")        # ask_first is in Workflow
    # 3. The lint catches the defects the lesson warns about.
    assert any("volatile" in p for p in lint(prompt + "\nToday is 2026-10-02."))
    swapped = prompt.replace("## Tools", "## TMP").replace("## Workflow", "## Tools").replace("## TMP", "## Workflow")
    assert any("sections must be" in p for p in lint(swapped))
    assert any("imperative" in p for p in lint(prompt.replace("- Never edit .env", "- Try not to edit .env")))
    assert any("too long" in p for p in lint(prompt, max_words=50))
    # 4. The prompt only asks. The guard enforces.
    assert "Never edit .env" in prompt
    assert guard("edit", {"path": "app/.env"})[0] == "deny"
    assert guard("write", {"path": ".env.local"})[0] == "deny"
    assert guard("edit", {"path": "src/app.py"})[0] == "allow"
    print("prompt ok")
