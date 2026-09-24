"""Map a model stop_reason to the harness's next action. Run: python3 stop_reasons.py"""


def next_action(stop_reason, has_tool_calls):
    if stop_reason == "tool_use" and has_tool_calls:
        return "run_tools"
    if stop_reason == "end_turn":
        return "return"
    if stop_reason == "max_tokens":
        return "continue"          # response was truncated — generate more
    if stop_reason == "stop_sequence":
        return "return"
    return "return"                # unknown -> safest is to return what we have


def continue_generation(messages, partial):
    """For max_tokens: append the partial assistant text and ask it to keep going."""
    return messages + [
        {"role": "assistant", "content": partial},
        {"role": "user", "content": "continue"},
    ]


if __name__ == "__main__":
    for sr, has in [("max_tokens", False), ("tool_use", True), ("end_turn", False),
                    ("stop_sequence", False), ("weird", False)]:
        print(f"{sr:14} -> {next_action(sr, has)}")
