"""Output contracts: extract, validate, and re-prompt until the reply conforms (or give up).

Run:  python3 code/contract.py
"""
import json
import re


def extract_blob(text):
    """First balanced {...} block. Braces inside JSON strings do not count."""
    start = text.find("{")
    if start < 0:
        return None
    depth, in_str, esc = 0, False, False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        elif ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    return None


def repair(blob):
    return re.sub(r",\s*([}\]])", r"\1", blob.strip().strip("`"))      # trailing commas


def check_json(text, schema):
    """schema maps key -> Python type. Returns a list of problems; empty means it conforms."""
    blob = extract_blob(text)
    if blob is None:
        return ["no JSON object found"]
    for candidate in (blob, repair(blob)):
        try:
            obj = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        problems = [f"missing key: {k}" for k in schema if k not in obj]
        problems += [f"{k} must be {t.__name__}" for k, t in schema.items()
                     if k in obj and not isinstance(obj[k], t)]
        return problems
    return ["unparseable JSON"]


def check_sections(text, required, max_chars=None):
    """Required headings must appear, in order."""
    problems, pos = [], 0
    for heading in required:
        m = re.compile(rf"^#+\s*{re.escape(heading)}", re.M | re.I).search(text, pos)
        if m is None:
            problems.append(f"missing or out-of-order section: {heading}")
        else:
            pos = m.end()
    if max_chars and len(text) > max_chars:
        problems.append(f"too long: {len(text)} > {max_chars} chars")
    return problems


def repair_prompt(problems):
    return ("Your previous response did not meet the format contract:\n- "
            + "\n- ".join(problems) + "\nReformat to satisfy all requirements.")


def enforce(ask, prompt, check, max_retries=2):
    """Ask, check, and re-prompt with the violation. Bounded: never loops forever."""
    for attempt in range(1, max_retries + 2):
        reply = ask(prompt)
        problems = check(reply)
        if not problems:
            return reply, attempt, []
        prompt = prompt + "\n\n" + repair_prompt(problems)
    return None, max_retries + 1, problems


if __name__ == "__main__":
    schema = {"name": str, "age": int}
    messy = 'Sure! Here you go:\n```json\n{"name": "ada", "age": 36,}\n```'
    assert check_json(messy, schema) == []                           # prose, fence, trailing comma
    assert check_json('{"name": "a } b", "age": 1}', schema) == []   # brace inside a string
    assert check_json('{"name": "ada"}', schema) == ["missing key: age"]
    assert check_json('{"name": "ada", "age": "36"}', schema) == ["age must be int"]
    assert check_json("no json here", schema) == ["no JSON object found"]

    good = "## Summary\nDid it.\n## Files\n- a.py\n## Diff\n+x"
    sections = ["Summary", "Files", "Diff"]
    assert check_sections(good, sections) == []
    assert check_sections("## Summary\nx\n## Files\ny", sections) == ["missing or out-of-order section: Diff"]
    assert check_sections("## Diff\nx\n## Summary\n## Files", sections) != []     # order matters

    # A scripted model: first reply breaks the contract, second obeys it.
    seen, replies = [], iter(["## Summary\nDid it.\n## Files\n- a.py", good])

    def model(prompt):
        seen.append(prompt)
        return next(replies)

    reply, attempts, problems = enforce(model, "Report your work.", lambda t: check_sections(t, sections))
    assert reply == good and attempts == 2 and problems == []
    repaired_in = attempts
    assert "missing or out-of-order section: Diff" in seen[1]        # the violation is fed back

    # A model that never complies stops after the retry budget instead of looping.
    stubborn = lambda prompt: "no headings at all"
    reply, attempts, problems = enforce(stubborn, "Report.", lambda t: check_sections(t, sections), max_retries=2)
    assert reply is None and attempts == 3 and problems
    print(f"contract ok: repaired on attempt {repaired_in}; stubborn model stopped after {attempts} attempts")
