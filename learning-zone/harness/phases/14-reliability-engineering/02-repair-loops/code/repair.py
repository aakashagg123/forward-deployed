"""A bounded validate-and-repair loop. Run:  python3 repair.py"""


def repair_loop(generate, validate, max_attempts=3):
    """generate(feedback)->output; validate(output)->None|error_message."""
    feedback, err = None, None
    for attempt in range(max_attempts):
        out = generate(feedback)
        err = validate(out)
        if err is None:
            return {"ok": True, "output": out, "attempts": attempt + 1}
        feedback = f"Your output was invalid: {err}. Fix it and return only the corrected output."
    return {"ok": False, "error": err, "attempts": max_attempts}


if __name__ == "__main__":
    import json
    state = {"n": 0}

    def gen(feedback):
        state["n"] += 1
        return '{"name": "ada"}' if state["n"] == 1 else '{"name": "ada", "age": 36}'

    def val(o):
        return None if "age" in json.loads(o) else "missing 'age'"

    print(repair_loop(gen, val))
