"""A pre/post tool-use hook runner. Run:  python3 hooks.py

Pre-hooks return ("deny", message) to block or ("allow", args) to permit/rewrite.
Post-hooks take (tool, args, result) and return a (possibly augmented) result.
"""


class HookRunner:
    def __init__(self):
        self.pre, self.post = [], []

    def on_pre(self, fn):
        self.pre.append(fn)

    def on_post(self, fn):
        self.post.append(fn)

    def call(self, tool, args, execute):
        for hook in self.pre:
            verdict = hook(tool, args)
            if verdict[0] == "deny":
                return f"blocked: {verdict[1]}"
            args = verdict[1]
        result = execute(tool, args)
        for hook in self.post:
            result = hook(tool, args, result)
        return result


if __name__ == "__main__":
    hr = HookRunner()
    hr.on_pre(lambda t, a: ("deny", ".env is protected")
              if a.get("path", "").endswith(".env") else ("allow", a))
    hr.on_post(lambda t, a, r: r + "  [lint: ok]" if t == "write" else r)
    print(hr.call("write", {"path": ".env"}, execute=lambda t, a: "wrote"))
    print(hr.call("write", {"path": "app.py"}, execute=lambda t, a: "wrote"))
