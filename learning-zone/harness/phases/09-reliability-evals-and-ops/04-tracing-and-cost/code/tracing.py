"""Nested spans for an agent run, plus cost rolled up from the tokens each span records.

Run:  python3 code/tracing.py
"""
import time
from contextlib import contextmanager

# EXAMPLE prices in USD per 1M tokens. These are made-up numbers for the demo.
# In a real harness, load the current price list from your provider and version it.
EXAMPLE_PRICES = {
    "example-large": {"in": 10.0, "out": 50.0},
    "example-small": {"in": 1.0, "out": 5.0},
}


class Tracer:
    def __init__(self, clock=time.perf_counter):
        self.roots, self._stack, self.clock = [], [], clock

    @contextmanager
    def span(self, name, **attrs):
        rec = {"name": name, "attrs": attrs, "children": [], "ms": None}
        (self._stack[-1]["children"] if self._stack else self.roots).append(rec)
        self._stack.append(rec)
        start = self.clock()
        try:
            yield rec
        except Exception as e:
            rec["attrs"]["error"] = repr(e)           # a failed span still lands in the trace
            raise
        finally:
            rec["ms"] = round((self.clock() - start) * 1000, 1)
            self._stack.pop()

    def render(self, spans=None, depth=0):
        lines = []
        for s in spans if spans is not None else self.roots:
            lines.append(f"{'  ' * depth}{s['name']}  {s['ms']}ms")
            lines += self.render(s["children"], depth + 1)
        return lines if depth else "\n".join(lines)


def cost_usd(model, in_tokens, out_tokens, prices=EXAMPLE_PRICES):
    p = prices[model]
    return (in_tokens * p["in"] + out_tokens * p["out"]) / 1_000_000


def cost_by_tag(spans, prices=EXAMPLE_PRICES):
    """Add up the cost of every span that has token counts. A child inherits its parent's tag."""
    totals = {}

    def walk(nodes, inherited):
        for s in nodes:
            a = s["attrs"]
            tag = a.get("tag", inherited)
            if "model" in a:
                totals[tag] = totals.get(tag, 0.0) + cost_usd(a["model"], a["in_tokens"], a["out_tokens"], prices)
            walk(s["children"], tag)

    walk(spans, "untagged")
    return {tag: round(total, 6) for tag, total in totals.items()}


if __name__ == "__main__":
    ticks = iter([0.0, 0.0, 0.4, 0.4, 0.5, 0.5])      # fake clock: start/end of run, model, tool
    t = Tracer(clock=lambda: next(ticks))
    with t.span("run", tag="feature:refactor"):
        with t.span("model_call", model="example-large", in_tokens=10_000, out_tokens=2_000):
            pass
        with t.span("tool_call", tool="bash"):
            pass
    run = t.roots[0]
    assert [c["name"] for c in run["children"]] == ["model_call", "tool_call"]
    assert [run["ms"], run["children"][0]["ms"], run["children"][1]["ms"]] == [500.0, 400.0, 100.0]
    assert t.render().splitlines()[1] == "  model_call  400.0ms"
    print(t.render())

    # A span that raises is closed, tagged with the error, and the stack is clean afterwards.
    t2 = Tracer()
    try:
        with t2.span("run"):
            with t2.span("tool_call"):
                raise RuntimeError("boom")
    except RuntimeError:
        pass
    assert "boom" in t2.roots[0]["children"][0]["attrs"]["error"] and t2._stack == []

    # Cost: 10k in + 2k out on the large model = (10000*10 + 2000*50) / 1e6 = 0.20.
    assert cost_usd("example-large", 10_000, 2_000) == 0.2
    t3 = Tracer()
    with t3.span("run", tag="feature:refactor"):
        with t3.span("model_call", model="example-large", in_tokens=10_000, out_tokens=2_000):
            pass
        with t3.span("model_call", model="example-small", in_tokens=40_000, out_tokens=0):
            pass
    with t3.span("run", tag="feature:search"):
        with t3.span("model_call", model="example-small", in_tokens=50_000, out_tokens=5_000):
            pass
    # refactor: 0.20 + 40000*1/1e6 = 0.24.  search: (50000*1 + 5000*5)/1e6 = 0.075.
    assert cost_by_tag(t3.roots) == {"feature:refactor": 0.24, "feature:search": 0.075}
    print(cost_by_tag(t3.roots))
