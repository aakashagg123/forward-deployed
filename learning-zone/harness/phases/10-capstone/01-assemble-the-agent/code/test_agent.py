"""Tests for agent.py. They use a real temp repo and a scripted model. Run:  python3 code/test_agent.py"""
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from agent import Agent, clip, decide, scripted_model, trim_history

BUGGY = "def add(a, b):\n    return a - b\n"
TEST = ("import unittest\nfrom calc import add\n\n\nclass T(unittest.TestCase):\n"
        "    def test_add(self):\n        self.assertEqual(add(2, 3), 5)\n\n\nif __name__ == '__main__':\n    unittest.main()\n")


# "a - b" and "a + b" have the same length. A .pyc written by the red run could look fresh
# to the green run in the same second, so no subprocess may write bytecode.
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"


def repo_tests_pass(root):
    r = subprocess.run([sys.executable, "-m", "unittest"], cwd=root, capture_output=True, text=True)
    return r.returncode == 0


def approve_edits_only(name, args):
    return name == "edit"


class AgentTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        (self.root / "calc.py").write_text(BUGGY)
        (self.root / "test_calc.py").write_text(TEST)
        (self.root / "keep.txt").write_text("precious")          # the denied rm -rf must not touch this

    def tearDown(self):
        self.tmp.cleanup()

    def test_fixes_the_bug_and_the_repo_tests_pass(self):
        self.assertFalse(repo_tests_pass(self.root))             # red first
        agent = Agent(self.root, scripted_model, approve=approve_edits_only)
        result = agent.run("Fix add() in calc.py")
        self.assertEqual(result["status"], "done")
        self.assertIn("a + b", (self.root / "calc.py").read_text())
        self.assertTrue(repo_tests_pass(self.root))              # judged by the repo, not the agent's words
        self.assertTrue(all(i["status"] == "done" for i in agent.todos) and len(agent.todos) == 3)

    def test_denied_command_is_blocked_and_reported(self):
        agent = Agent(self.root, scripted_model, approve=approve_edits_only)
        result = agent.run("Fix add() in calc.py")
        results = [b for m in result["history"] if m["role"] == "user" and isinstance(m["content"], list)
                   for b in m["content"]]
        blocked = [b for b in results if b["is_error"] and b["content"].startswith("denied")]
        self.assertEqual(len(blocked), 1)
        self.assertEqual((self.root / "keep.txt").read_text(), "precious")
        self.assertEqual(decide("bash", {"cmd": "rm -rf ."}), "deny")
        self.assertEqual(decide("bash", {"cmd": "python3 -m unittest && rm -rf ."}), "deny")   # deny wins
        self.assertEqual(decide("bash", {"cmd": "python3 -m unittest"}), "allow")
        self.assertEqual(decide("bash", {"cmd": "python3 -m unittest && python3 evil.py"}), "ask")
        self.assertEqual(decide("edit", {"path": "calc.py"}), "ask")

    def test_ask_is_denied_when_nobody_approves(self):
        agent = Agent(self.root, scripted_model)                 # default approver says no
        agent.run("Fix add() in calc.py")
        self.assertIn("a - b", (self.root / "calc.py").read_text())

    def test_paths_outside_the_repo_are_refused(self):
        agent = Agent(self.root, scripted_model)
        out, is_error = agent.call_tool("read", {"path": "../secret.txt"})
        self.assertTrue(is_error and "outside the repo" in out)

    def test_step_budget_stops_a_looping_model(self):
        calls = []

        def looping_model(history):
            calls.append(len(history))
            return [{"type": "tool_use", "id": f"toolu_{len(calls)}", "name": "read", "input": {"path": "calc.py"}}]

        result = Agent(self.root, looping_model, max_steps=5).run("loop forever")
        self.assertEqual((result["status"], len(calls)), ("budget", 5))
        history = result["history"]
        self.assertEqual(len(history), 1 + 2 * 5)                # every tool_use got its tool_result

    def test_trim_keeps_tool_pairs_together(self):
        history = [{"role": "user", "content": "task"}]
        for i in range(10):
            history.append({"role": "assistant", "content": [
                {"type": "tool_use", "id": f"t{i}", "name": "read", "input": {"path": "x"}}]})
            history.append({"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": f"t{i}", "content": "x" * 500}]})
        for limit in range(1000, 6000, 250):                     # every limit, so no lucky even count
            trimmed = trim_history(history, limit)
            self.assertLess(len(trimmed), len(history))
            self.assertEqual(trimmed[0]["role"], "user")
            self.assertIn("earlier steps trimmed", trimmed[0]["content"])
            uses = [b["id"] for m in trimmed[1:] if m["role"] == "assistant" for b in m["content"]]
            results = [b["tool_use_id"] for m in trimmed[1:] if m["role"] == "user" for b in m["content"]]
            self.assertEqual(uses, results)                      # no orphan on either side
            self.assertEqual(uses[-1], "t9")                     # the newest pair always survives
            self.assertEqual([m["role"] for m in trimmed[1:]], ["assistant", "user"] * len(uses))
        self.assertEqual(trim_history(history, 10**6), history)  # under the limit: nothing changes

    def test_clip_keeps_head_and_tail(self):
        out = clip("A" * 100 + "B" * 5000 + "Z" * 100, limit=400)
        self.assertTrue(out.startswith("A" * 100) and out.endswith("Z" * 100) and "chars cut" in out)
        self.assertEqual(clip("short"), "short")


if __name__ == "__main__":
    unittest.main()
