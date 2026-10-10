"""Progressive disclosure for skills and for tool schemas, in stdlib.

Names and descriptions load at startup. Bodies and full schemas load on demand.
Run:  python3 code/skills.py
"""
import tempfile
from pathlib import Path


def parse_skill(text):
    """Split a SKILL.md into (frontmatter dict, body). Handles `key: value` lines."""
    assert text.startswith("---\n"), "frontmatter must be the first thing in the file"
    head, body = text[4:].split("\n---\n", 1)
    meta = {}
    for line in head.splitlines():
        key, _, val = line.partition(":")
        meta[key.strip()] = val.strip().strip("\"'")
    return meta, body.strip()


class SkillIndex:
    def __init__(self, root):
        self.paths, self.index, self.body_reads = {}, {}, 0
        for p in sorted(Path(root).glob("*/SKILL.md")):
            meta, _ = parse_skill(p.read_text())     # startup: only the header is kept
            name = meta.get("name", p.parent.name)
            self.paths[name] = p
            self.index[name] = (meta.get("description", "") + " " + meta.get("when_to_use", "")).lower()

    def match(self, task):
        """Stand-in for the model reading descriptions: count shared words."""
        words = {w for w in task.lower().split() if len(w) > 3}
        scored = [(len(words & set(d.split())), n) for n, d in self.index.items()]
        best = max(scored, default=(0, None))
        return best[1] if best[0] >= 2 else None

    def load(self, name):
        self.body_reads += 1                         # the expensive step
        return parse_skill(self.paths[name].read_text())[1]


class DeferredTools:
    """Tool names in context; a full schema is fetched only when needed."""
    def __init__(self):
        self.loaders, self.cache, self.fetches = {}, {}, 0

    def register(self, name, loader):
        self.loaders[name] = loader

    def search(self, term):
        return [n for n in self.loaders if term in n]

    def load(self, name):
        if name not in self.cache:
            self.fetches += 1
            self.cache[name] = self.loaders[name]()
        return self.cache[name]


def cost(text):
    return len(text) // 4                            # rough token estimate


if __name__ == "__main__":
    real = (Path(__file__).parent.parent / "outputs" / "SKILL.md").read_text()
    meta, body = parse_skill(real)
    assert meta["name"] == "pr-description" and "git log" in body

    with tempfile.TemporaryDirectory() as d:
        for name, desc, filler in [("pr-description", None, ""),
                                   ("rotate-keys", "Rotate API keys on a schedule. Use when keys expire.", "x " * 4000),
                                   ("release-notes", "Draft release notes from merged changes.", "y " * 4000)]:
            (Path(d) / name).mkdir()
            text = real if desc is None else f"---\nname: {name}\ndescription: {desc}\n---\n{filler}"
            (Path(d) / name / "SKILL.md").write_text(text)

        skills = SkillIndex(d)
        assert skills.body_reads == 0                # startup read no bodies
        index_cost = sum(cost(t) for t in skills.index.values())
        full_cost = sum(cost(p.read_text()) for p in skills.paths.values())
        assert index_cost * 10 < full_cost           # the index is far cheaper
        assert skills.match("write a pull request description for this branch") == "pr-description"
        assert skills.match("what is the weather") is None   # no match, nothing loaded
        assert skills.body_reads == 0
        assert "How to test" in skills.load("pr-description") and skills.body_reads == 1
        print(f"index ~{index_cost} tokens vs all bodies ~{full_cost} tokens")

    tools = DeferredTools()
    tools.register("github_create_pr", lambda: {"name": "github_create_pr", "inputSchema": {"big": "schema"}})
    tools.register("github_list_issues", lambda: {"name": "github_list_issues", "inputSchema": {}})
    assert tools.search("pr") == ["github_create_pr"] and tools.fetches == 0
    tools.load("github_create_pr")
    tools.load("github_create_pr")
    assert tools.fetches == 1                        # fetched once, then cached
    print("skills: all checks passed")
