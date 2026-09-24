"""A minimal nested-span tracer (context manager). Run:  python3 tracing.py"""
import time
from contextlib import contextmanager


class Tracer:
    def __init__(self):
        self.spans = []
        self._stack = []

    @contextmanager
    def span(self, name, **attrs):
        rec = {"name": name, "attrs": attrs, "children": [], "ms": None}
        (self._stack[-1]["children"] if self._stack else self.spans).append(rec)
        self._stack.append(rec)
        start = time.perf_counter()
        try:
            yield rec
        finally:
            rec["ms"] = round((time.perf_counter() - start) * 1000, 1)
            self._stack.pop()


if __name__ == "__main__":
    t = Tracer()
    with t.span("run"):
        with t.span("model_call", tokens=120):
            pass
        with t.span("tool_call", tool="bash"):
            pass
    run = t.spans[0]
    print(run["name"], "->", [c["name"] for c in run["children"]])
