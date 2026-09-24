"""Recovery: classify tool failures (model-fixable / transient / fatal) and bound retries.

Run:  python3 recovery.py
"""
from dataclasses import dataclass, field

TRANSIENT = ("timeout", "429", "503", "connection")


@dataclass
class Recovery:
    max_retries: int = 2
    attempts: dict = field(default_factory=dict)         # tool name -> count

    def dispatch(self, name, args, tools):
        try:
            return {"ok": True, "content": str(tools[name](**args))}
        except KeyError:
            return {"ok": False, "fatal": False,         # model-fixable: unknown tool
                    "content": f"error: no tool {name!r}; available: {list(tools)}"}
        except TypeError as e:
            return {"ok": False, "fatal": False,         # model-fixable: bad args
                    "content": f"error: bad arguments for {name}: {e}"}
        except Exception as e:
            msg = str(e).lower()
            transient = any(t in msg for t in TRANSIENT)
            n = self.attempts.get(name, 0) + 1
            self.attempts[name] = n
            if transient and n <= self.max_retries:
                return {"ok": False, "fatal": False, "retry": True,
                        "content": f"transient error (attempt {n}): {e}"}
            return {"ok": False, "fatal": not transient, "content": f"error: {e}"}


if __name__ == "__main__":
    counter = [0]

    def flaky():
        counter[0] += 1
        if counter[0] < 3:
            raise RuntimeError("connection timeout")
        return "ok"

    tools = {"flaky": flaky}
    r = Recovery()
    print(r.dispatch("flaky", {}, tools))    # retry: True (attempt 1)
    print(r.dispatch("flaky", {}, tools))    # retry: True (attempt 2)
    print(r.dispatch("flaky", {}, tools))    # ok: True
    print(r.dispatch("nope", {}, tools))     # model-fixable: unknown tool
