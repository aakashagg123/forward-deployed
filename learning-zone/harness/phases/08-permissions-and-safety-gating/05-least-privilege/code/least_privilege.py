"""Role -> capability scoping for agents. Run:  python3 least_privilege.py"""

ROLE_CAPS = {
    "reader": {"read", "grep", "glob"},
    "coder": {"read", "grep", "glob", "edit", "write", "bash"},
    "reviewer": {"read", "grep", "glob"},            # never write/bash
    "summarizer": {"read"},
}


class ScopedAgent:
    def __init__(self, role, registry_dispatch):
        self.caps = ROLE_CAPS[role]
        self.dispatch = registry_dispatch

    def call(self, tool, args):
        if tool not in self.caps:
            return f"denied: role lacks capability '{tool}'"
        return self.dispatch(tool, args)


if __name__ == "__main__":
    dispatch = lambda t, a: f"ran {t}"
    rev = ScopedAgent("reviewer", dispatch)
    print("reviewer read  ->", rev.call("read", {}))
    print("reviewer write ->", rev.call("write", {}))
    coder = ScopedAgent("coder", dispatch)
    print("coder write    ->", coder.call("write", {}))
