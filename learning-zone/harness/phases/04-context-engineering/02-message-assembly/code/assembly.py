"""Deterministic context assembler: stable-first, the ask last. Run: python3 assembly.py"""


def assemble(system, memory, history, files, user_msg):
    system_block = "\n\n".join(filter(None, [system, memory]))    # stable, cacheable
    messages = list(history)                                       # semi-stable
    if files:                                                      # this-turn context
        joined = "\n\n".join(f'<file path="{p}">\n{c}\n</file>' for p, c in files)
        messages.append({"role": "user", "content": f"Relevant files:\n{joined}"})
    messages.append({"role": "user", "content": user_msg})         # the ask, last
    return system_block, messages


if __name__ == "__main__":
    sys_block, msgs = assemble(
        system="You are a coding agent.",
        memory="Project: use the public API barrel.",
        history=[{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"}],
        files=[("api.py", "def add(a,b): ...")],
        user_msg="Add a subtract function.")
    print("system head:", sys_block.splitlines()[0])
    print("messages:", len(msgs), "last role:", msgs[-1]["role"])
