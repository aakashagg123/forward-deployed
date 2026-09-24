"""A model router + fallback chain. Run:  python3 routing.py"""


def route(task, simple_model, strong_model, is_hard):
    return [strong_model, simple_model] if is_hard(task) else [simple_model, strong_model]


def with_fallback(chain, call):
    """Try each option in order; return first success, else raise the last error."""
    last = None
    for option in chain:
        try:
            return {"model": option, "result": call(option)}
        except Exception as e:
            last = e
    raise RuntimeError(f"all options failed: {last}")


if __name__ == "__main__":
    def call(model):
        if model == "strong":
            raise RuntimeError("overloaded")
        return f"answer from {model}"

    print(route("simple task", "haiku", "strong", is_hard=lambda t: "complex" in t))
    print(with_fallback(["strong", "haiku"], call))
