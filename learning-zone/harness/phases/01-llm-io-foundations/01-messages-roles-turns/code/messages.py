"""Message constructors + an alternation validator. Run:  python3 messages.py"""


def system(text):
    return text                                       # passed as top-level system=


def user(text):
    return {"role": "user", "content": text}


def assistant(text):
    return {"role": "assistant", "content": text}


def validate(messages):
    if not messages or messages[0]["role"] != "user":
        return "conversation must start with a user message"
    for a, b in zip(messages, messages[1:]):
        if a["role"] == b["role"]:
            return f"two {a['role']} messages in a row — turns must alternate"
    return None


def build(*turns):
    msgs = [user(t) if role == "user" else assistant(t) for role, t in turns]
    err = validate(msgs)
    if err:
        raise ValueError(err)
    return msgs


if __name__ == "__main__":
    msgs = build(("user", "hi"), ("assistant", "hello"), ("user", "2+2?"))
    print("valid:", validate(msgs) is None)
    bad = [user("a"), user("b")]
    print("bad case:", validate(bad))
