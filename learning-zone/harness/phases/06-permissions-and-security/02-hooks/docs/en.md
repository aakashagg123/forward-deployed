# Hooks: Rules That Run as Code

> **Motto** — A hook is a script the harness runs around a tool call, so a rule holds even when the model ignores a prompt.

*Part of Phase 06 — Permissions and Security.*

*Last reviewed: 2026-10 · Volatility: fast*

## The Problem

Some rules must be guaranteed, not requested. "Never touch `.env`." "Check the lint result after every write." A line in the prompt only asks the model. A **hook** is code the harness runs before and after each tool call. It does not depend on what the model decides.

Secrets are the first case. A key hard-coded in source is already leaked once it reaches git history. An agent that edits `.env` can print the key into a transcript. Hygiene must be structural: keep secrets in the environment, git-ignore `.env`, and block the agent from the file with a hook.

## The Concept

<style>
.dgm-hk{background:var(--color-surface);border:1px solid var(--color-border);border-top:3px solid var(--color-border-success-outline);
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgb(var(--shadow-color) / 0.04),0 8px 24px rgb(var(--shadow-color) / 0.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-hk-chip{position:absolute;top:-11px;left:24px;background:var(--color-background-success-solid);color:var(--white);
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px color-mix(in oklab, var(--color-background-success-solid) 28%, transparent)}
.dgm-hk h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:var(--color-text-secondary)}
.dgm-hk-sub{font-size:12px;color:var(--color-text-secondary);margin:0 0 16px}
.dgm-hk-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-hk-n{background:var(--color-surface-tertiary);border:1px solid var(--color-border);border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:var(--color-text);line-height:1.3}
.dgm-hk-n.accent{background:var(--color-background-success-surface);border-color:var(--color-border-success-outline);color:var(--color-text-success)}
.dgm-hk-n.blue{background:var(--color-background-info-surface);border-color:var(--color-border-info-surface);color:var(--color-text-info)}
.dgm-hk-n.green{background:var(--color-background-success-surface);border-color:var(--color-border-success-surface);color:var(--color-text-success)}
.dgm-hk-n.red{background:var(--color-background-danger-surface);border-color:var(--color-border-danger-surface);color:var(--color-text-danger)}
.dgm-hk-arr{color:var(--color-text-tertiary);font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-hk-arr .lbl{font-size:8.5px;font-weight:700;color:var(--color-text-tertiary);text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-hk{padding:20px 16px 18px}.dgm-hk-row{flex-direction:column}}
.dgm-hk-q{background:var(--color-surface-tertiary);border:1px dashed var(--color-border);border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:var(--color-text);margin-bottom:10px}
.dgm-hk-branches{display:grid;grid-template-columns:repeat(1,1fr);gap:10px}
.dgm-hk-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-hk-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-hk-b p{margin:0;font-size:10px;color:var(--color-text-secondary);line-height:1.35}
.dgm-hk-b.accent{background:var(--color-background-success-surface);border-color:var(--color-border-success-outline)}
.dgm-hk-b.accent h6{color:var(--color-text-success)}
.dgm-hk-b.blue{background:var(--color-background-info-surface);border-color:var(--color-border-info-surface)}
.dgm-hk-b.blue h6{color:var(--color-text-info)}
.dgm-hk-b.green{background:var(--color-background-success-surface);border-color:var(--color-border-success-surface)}
.dgm-hk-b.green h6{color:var(--color-text-success)}
.dgm-hk-b.red{background:var(--color-background-danger-surface);border-color:var(--color-border-danger-surface)}
.dgm-hk-b.red h6{color:var(--color-text-danger)}
.dgm-hk-b.neutral{background:var(--color-surface-tertiary);border-color:var(--color-border)}
.dgm-hk-b.neutral h6{color:var(--color-text)}
@media (max-width:640px){.dgm-hk{padding:20px 16px 18px}.dgm-hk-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-hk">
  <span class="dgm-hk-chip">Two hook points bracket every tool call</span>
  <h4>PreToolUse can block or modify; PostToolUse can augment the result</h4>
  <p class="dgm-hk-sub">PreToolUse runs before the tool ever executes — it's the only hook that can stop it.</p>
  <div class="dgm-hk-row">
    <div class="dgm-hk-n neutral">Tool call</div>
    <span class="dgm-hk-arr">→</span>
    <div class="dgm-hk-n accent">PreToolUse hook(s)</div>
  </div>
  <div class="dgm-hk-branches">
    <div class="dgm-hk-b red">
      <h6>Block</h6>
      <p>Denied</p>
    </div>
  </div>
  <div class="dgm-hk-row">
    <div class="dgm-hk-n blue">Allow / modify → execute tool</div>
    <span class="dgm-hk-arr">→</span>
    <div class="dgm-hk-n accent">PostToolUse hook(s)</div>
    <span class="dgm-hk-arr">→</span>
    <div class="dgm-hk-n green">Result (maybe augmented)</div>
  </div>
</div>


A hook is a command. The harness sends it one JSON object on stdin. A PreToolUse event carries `tool_name`, `tool_input`, `cwd` and `permission_mode`, among other fields. The hook answers in one of two ways:

- **Exit code 2.** The call is blocked. The text on stderr becomes the reason.
- **Exit 0 with JSON.** A `hookSpecificOutput` object with `permissionDecision` set to `deny` blocks the call.

Exit 0 with no output means "no opinion". The call goes on through the normal permission flow. Any other exit code, such as 1, is a non-blocking error, so the call still runs. A hook that fails by crashing therefore fails open. Make your own hooks exit 2 when they cannot parse their input.

A PostToolUse hook runs after the tool. It cannot undo the call. It can send feedback to the model.

## Build It

`code/hooks.py` is a model of this contract. It runs real hook commands, feeds them JSON, and reads the exit code. It is a model of the idea, not Claude Code.

```python
class HookRunner:
    def __init__(self):
        self.hooks = {"PreToolUse": [], "PostToolUse": []}     # (matcher, argv)

    def add(self, event, matcher, argv):
        self.hooks[event].append((matcher, argv))

    def _run(self, argv, payload):
        p = subprocess.run(argv, input=json.dumps(payload), capture_output=True,
                           text=True, timeout=30)
        return p.returncode, p.stdout, p.stderr

    def pre(self, tool, tool_input):
        """Return ("deny", reason) or ("none", ""). A hook never needs to say allow."""
        event = {"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": tool_input}
        for matcher, argv in self.hooks["PreToolUse"]:
            if not matches(matcher, tool):
                continue
            code, out, err = self._run(argv, event)
            if code == 2:                                       # blocking error
                return "deny", err.strip()
            if code == 0 and out.strip().startswith("{"):
                decision = json.loads(out).get("hookSpecificOutput", {})
                if decision.get("permissionDecision") == "deny":
                    return "deny", decision.get("permissionDecisionReason", "")
            # any other exit code is a non-blocking error: the call goes on
        return "none", ""

    def post(self, tool, tool_input, result):
        """The tool already ran. Exit 2 cannot undo it, but stderr goes back to the model."""
        event = {"hook_event_name": "PostToolUse", "tool_name": tool,
                 "tool_input": tool_input, "tool_response": result}
        for matcher, argv in self.hooks["PostToolUse"]:
            if matches(matcher, tool):
                code, _, err = self._run(argv, event)
                if code == 2:
                    result += f"\n[hook feedback] {err.strip()}"
        return result

    def call(self, tool, tool_input, execute, rules=None):
        verdict, reason = self.pre(tool, tool_input)
        if verdict == "deny":
            return f"blocked by hook: {reason}"
        if rules and rules(tool, tool_input) == "deny":         # a hook cannot override deny rules
            return "blocked by rule"
        return self.post(tool, tool_input, execute(tool, tool_input))
```

`outputs/block_env_hook.py` is a working PreToolUse hook. It denies Read, Edit, Write and Bash calls that name a `.env` file. It lets `.env.example` through. This is its core:

```python
def main():
    try:
        event = json.load(sys.stdin)
        if not isinstance(event, dict):
            raise ValueError("event is not an object")
        bad = [p for p in paths_in(event) if is_secret_env(p)]
    except Exception as exc:                           # any failure blocks the call
        print(f"env hook: cannot read the event ({exc})", file=sys.stderr)
        return 2                                       # fail closed
    if not bad:
        return 0                                       # no opinion
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": f"{bad[0]} holds secrets; the agent may not touch it",
    }}))
    return 0
```

The asserts in `hooks.py` run that hook. They show that a blocked call never executes, that a PostToolUse hook adds feedback, that exit 1 does not block, and that exit 2 does. They also show that a deny rule still wins when no hook objects. You can test the hook by hand: `echo '{"tool_name":"Edit","tool_input":{"file_path":".env"}}' | python3 outputs/block_env_hook.py`.

## Use It

Claude Code hooks live in `settings.json` in three levels: an event, a matcher group, and a list of handlers. A handler has `"type": "command"` and a `command`. The matcher filters on the tool name. `Edit|Write` is an exact list. Anything with other characters is a regex. `*` or an empty matcher matches all.

Facts to rely on:

- PreToolUse hooks run before the permission prompt, for every tool except `EndConversation`.
- Exit 2 blocks the call before permission rules are checked. A blocking hook beats an allow rule.
- A hook that returns `allow` does not bypass a deny rule or an ask rule.
- `permissionDecision` can be `allow`, `deny`, `ask` or `defer`. `updatedInput` can rewrite the arguments.
- Hooks run outside the sandbox with your full access. Review them like code.

The [Settings.json](../../03-settings-json/docs/en.md) lesson wires `block_env_hook.py` and the egress hook into one file.

## Challenge

Write a PostToolUse hook that reads `tool_response`, finds a string shaped like `AKIA` plus 16 capital letters or digits, and exits 2 with a warning. Add it to `hooks.py` with an assert. Then say why this hook can warn but cannot block.

## Sources

Claude Code docs, "Hooks reference" and "Configure permissions", section "Extend permissions with hooks" (code.claude.com/docs/en).

Next: [Settings.json](../../03-settings-json/docs/en.md)
