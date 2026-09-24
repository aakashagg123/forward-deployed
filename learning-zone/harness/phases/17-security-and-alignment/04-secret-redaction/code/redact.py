"""A secret-redaction filter (patterns + known values). Run:  python3 redact.py"""
import re

PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9]{16,}"),                  # API-key-ish
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),                 # GitHub token
    re.compile(r"-----BEGIN[ A-Z]+PRIVATE KEY-----[\s\S]+?-----END[ A-Z]+PRIVATE KEY-----"),
    re.compile(r"AKIA[0-9A-Z]{16}"),                     # AWS access key id
]


def redact(text, known_values=()):
    for v in known_values:
        if v:
            text = text.replace(v, "[REDACTED]")
    for rx in PATTERNS:
        text = rx.sub("[REDACTED]", text)
    return text


if __name__ == "__main__":
    s = "key=sk-abc123def456ghi789 and token=ghp_0123456789abcdef01234"
    print(redact(s, known_values=["hunter2"]))
