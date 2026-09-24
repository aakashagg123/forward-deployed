"""A session scratchpad: structured working memory. Run:  python3 scratchpad.py"""


class Scratchpad:
    def __init__(self):
        self._d = {}

    def set(self, key, value):
        self._d[key] = value
        return f"noted {key}"

    def get(self, key, default=None):
        return self._d.get(key, default)

    def summary(self):
        return "\n".join(f"- {k}: {v}" for k, v in self._d.items()) or "(empty)"


if __name__ == "__main__":
    sp = Scratchpad()
    sp.set("editing", "api/routes.py")
    sp.set("tests_pass", False)
    print(sp.get("editing"))
    print(sp.summary())
