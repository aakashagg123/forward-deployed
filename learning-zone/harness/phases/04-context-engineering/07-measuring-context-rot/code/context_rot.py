"""Needle-in-a-haystack context-rot eval. Stub model runs offline; swap for a real call.

Run:  python3 context_rot.py
"""


def make_case(size, depth, needle="The launch code is 4242."):
    filler = "\n".join(f"filler line {i}" for i in range(size))
    lines = filler.splitlines()
    at = int(len(lines) * depth)
    lines.insert(at, needle)
    return "\n".join(lines), needle


def score(answer, needle_value="4242"):
    return 1 if needle_value in answer else 0


def run_grid(ask, sizes=(50, 500), depths=(0.1, 0.5, 0.9)):
    grid = {}
    for s in sizes:
        for d in depths:
            haystack, _ = make_case(s, d)
            grid[(s, d)] = score(ask(haystack, "What is the launch code?"))
    return grid


def stub_ask(haystack, q):
    # Perfect recall for small contexts; "rots" past a threshold (illustrative).
    return "4242" if len(haystack) < 4000 else "I don't know"


if __name__ == "__main__":
    for (s, d), ok in run_grid(stub_ask).items():
        print(f"size={s:4} depth={d}  {'FOUND' if ok else 'miss'}")
