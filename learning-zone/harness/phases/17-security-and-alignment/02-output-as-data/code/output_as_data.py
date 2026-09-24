"""Output-as-data: dispatch model proposals through an allowlist, never eval.

Run:  python3 output_as_data.py
"""
ALLOWED = {"read_file", "list_dir"}        # safe, allowlisted actions


def safe_dispatch(proposed_action, args, tools):
    if proposed_action not in ALLOWED:
        return f"denied: '{proposed_action}' is not an allowed action"
    return tools[proposed_action](**args)  # only allowlisted actions ever run


def NEVER_do_this(model_text):
    # eval(model_text)  # <- arbitrary code execution from untrusted text. Never.
    raise RuntimeError("never execute model output as code")


if __name__ == "__main__":
    tools = {"read_file": lambda path: f"contents of {path}"}
    print(safe_dispatch("read_file", {"path": "a.py"}, tools))
    print(safe_dispatch("delete_everything", {}, tools))
