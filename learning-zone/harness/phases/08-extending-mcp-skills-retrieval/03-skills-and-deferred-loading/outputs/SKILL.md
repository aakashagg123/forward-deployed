---
name: pr-description
description: Write a pull request description from the current branch's changes. Use when the user asks for a PR description, PR summary or PR body.
when_to_use: "Examples: 'write the PR description', 'summarize this branch for a pull request'"
allowed-tools: Bash(git diff *) Bash(git log *)
---

# PR description

Write a description a reviewer can read in one minute.

1. Run `git log --oneline main..HEAD` to list the commits on this branch.
2. Run `git diff main...HEAD --stat` to see which files changed.
3. Read only the files that carry the main change. Skip generated files.
4. Write three short parts: **What changed**, **Why**, **How to test**.
5. List anything a reviewer should check twice, such as a migration or a new dependency.

Do not invent test results. If you did not run the tests, say so.
