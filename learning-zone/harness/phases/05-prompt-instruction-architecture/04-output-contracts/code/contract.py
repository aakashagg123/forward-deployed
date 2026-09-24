"""Response-contract checker + repair-prompt builder. Run: python3 contract.py"""
import re


def check_contract(text, required_sections, max_chars=None):
    problems = []
    for heading in required_sections:
        if not re.search(rf"^#+\s*{re.escape(heading)}", text, re.MULTILINE | re.IGNORECASE):
            problems.append(f"missing section: {heading}")
    if max_chars and len(text) > max_chars:
        problems.append(f"too long: {len(text)} > {max_chars} chars")
    return problems            # empty list == conforms


def repair_prompt(problems):
    return ("Your previous response did not meet the format contract:\n- "
            + "\n- ".join(problems) + "\nReformat to satisfy all requirements.")


if __name__ == "__main__":
    resp = "## Summary\nDid the thing.\n## Files\n- a.py"
    probs = check_contract(resp, ["Summary", "Files", "Diff"])
    print(probs)
    if probs:
        print(repair_prompt(probs))
