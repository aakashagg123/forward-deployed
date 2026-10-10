"""Trim and compact a tool-using history without ever splitting a tool pair.

Messages use the Anthropic shape: an assistant message holds tool_use blocks, and the
next user message holds the matching tool_result blocks.  Run: python3 code/compaction.py
"""
import json


def size(messages):
    return sum(len(json.dumps(m["content"])) // 4 for m in messages)    # ~4 chars/token


def is_prompt(m):
    """A real user prompt: a user message that holds no tool_result."""
    return m["role"] == "user" and not (
        isinstance(m["content"], list) and any(b["type"] == "tool_result" for b in m["content"]))


def turns(messages):
    """Split into turns. Each turn starts at a real prompt and keeps its tool pairs inside."""
    out = []
    for m in messages:
        if is_prompt(m) or not out:
            out.append([])
        out[-1].append(m)
    return out


def check_pairs(messages):
    """Return a list of problems. An empty list means the history is valid."""
    problems, pending = [], set()
    if messages and not is_prompt(messages[0]):
        problems.append("history must start with a user prompt")
    for m in messages:
        blocks = m["content"] if isinstance(m["content"], list) else []
        used = {b["id"] for b in blocks if b["type"] == "tool_use"}
        done = {b["tool_use_id"] for b in blocks if b["type"] == "tool_result"}
        if done - pending:
            problems.append(f"orphan tool_result {sorted(done - pending)}")
        if pending - done:
            problems.append(f"tool_use without result {sorted(pending - done)}")
        pending = used
    return problems + ([f"tool_use without result {sorted(pending)}"] if pending else [])


def clear_results(turn, note="[old tool output cleared]"):
    """Shrink tool_result bodies but keep every block, so each pair stays intact."""
    out = []
    for m in turn:
        c = m["content"]
        if isinstance(c, list):
            c = [dict(b, content=note) if b["type"] == "tool_result" else b for b in c]
        out.append({"role": m["role"], "content": c})
    return out


def trim(messages, max_tokens, keep_turns=1):
    """Stage 1: clear old tool output. Stage 2: drop the oldest whole turns."""
    ts = turns(messages)
    flat = lambda xs: [m for t in xs for m in t]
    if size(flat(ts)) > max_tokens:
        ts = [clear_results(t) for t in ts[:-keep_turns]] + ts[-keep_turns:]
    while size(flat(ts)) > max_tokens and len(ts) > keep_turns:
        ts.pop(0)                                    # a whole turn, never a half pair
    return flat(ts)


def compact(messages, max_tokens, summarize, keep_turns=2):
    """Replace old turns with a synopsis merged into the first kept prompt."""
    ts = turns(messages)
    if size(messages) <= max_tokens or len(ts) <= keep_turns:
        return messages
    old = [m for t in ts[:-keep_turns] for m in t]
    kept = [m for t in ts[-keep_turns:] for m in t]
    note = f"[summary of earlier conversation]\n{summarize(old)}\n\n"
    first = dict(kept[0], content=note + kept[0]["content"])
    return [first] + kept[1:]


def stub_summarize(old):
    """Stand-in for a model call. Production asks for decisions, plan, files and open questions."""
    said = [b["text"] for m in old if m["role"] == "assistant" and isinstance(m["content"], list)
            for b in m["content"] if b["type"] == "text"]
    return f"{len(old)} earlier messages. Key points: " + " | ".join(said)


def make_history(n_turns):
    h = []
    for i in range(n_turns):
        h += [{"role": "user", "content": f"task {i}: read file_{i}.py"},
              {"role": "assistant", "content": [
                  {"type": "text", "text": f"decided: patch file_{i}"},
                  {"type": "tool_use", "id": f"tu_{i}", "name": "read", "input": {"path": f"file_{i}.py"}}]},
              {"role": "user", "content": [
                  {"type": "tool_result", "tool_use_id": f"tu_{i}", "content": "x" * 800}]},
              {"role": "assistant", "content": [{"type": "text", "text": f"done {i}"}]}]
    return h


if __name__ == "__main__":
    history = make_history(6)
    budget = 600
    assert check_pairs(history) == [] and size(history) > budget

    # The bug: drop the oldest MESSAGE until it fits. Some budgets cut between a pair.
    def naive_trim(messages, max_tokens):
        out = list(messages)
        while size(out) > max_tokens:
            out.pop(0)
        return out

    budgets = range(300, 3000, 100)
    broken = [check_pairs(naive_trim(history, b)) for b in budgets]
    assert any("orphan" in p for probs in broken for p in probs)
    assert all(check_pairs(trim(history, b)) == [] for b in budgets)    # pair-aware: always valid
    assert all(check_pairs(compact(history, b, stub_summarize)) == [] for b in budgets)

    trimmed = trim(history, budget)
    assert check_pairs(trimmed) == [] and size(trimmed) <= budget
    assert trimmed[-4:] == history[-4:]              # the newest turn is untouched

    cleared = trim(history[:8], 400)                 # stage 1 alone keeps both blocks of each pair
    assert check_pairs(cleared) == [] and "[old tool output cleared]" in json.dumps(cleared)

    compacted = compact(history, budget, stub_summarize, keep_turns=2)
    assert check_pairs(compacted) == [] and size(compacted) < size(history)
    assert compacted[0]["content"].startswith("[summary of earlier conversation]")
    assert "decided: patch file_0" in compacted[0]["content"]       # an old decision survives
    assert compacted[-4:] == history[-4:]            # recent turns stay word for word
    print("kept", len(trimmed), "messages after trim;", len(compacted), "after compact")
    print("naive trim breaks:", next(p for probs in broken for p in probs if "orphan" in p))
