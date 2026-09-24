---
name: harness-security-review
description: >
  Review a diff for harness security threats. Trigger with /security-review, "review
  this for security", "check for vulnerabilities", before merging changes to tool
  dispatch, network, auth, caching, or untrusted-input handling.
version: 1.0.0
kind: skill
phase: 17
lesson: 6
---

# Harness security review

Review the diff for the following threats. Report each finding with severity
(critical/high/low), the location, and a concrete fix. Advise "do not merge" on any
critical finding.

## Checklist
1. **Model output as control flow** — is any model/LLM output `eval`'d, exec'd, or passed
   as a shell string? It must go through an allowlist + validation. (critical)
2. **Prompt injection** — is untrusted content (files, tool results, web) labeled as data
   and never treated as instructions? (high)
3. **Egress / exfiltration** — any network call to a non-allowlisted host? Default-deny
   outbound; watch for metadata endpoints (169.254.169.254) and encoded payloads. (critical)
4. **Secrets** — hardcoded keys/tokens? Secrets read into context or written to logs without
   redaction? `.env` reachable? (critical)
5. **Tenant isolation** — are caches/memory/indexes keyed by tenant id? Any shared store that
   could leak across tenants? (critical for multi-tenant)
6. **Permissions** — do dangerous actions (write, bash, network, delete) pass through the
   permission gate with least privilege? (high)
7. **Idempotency** — are retried side-effecting actions idempotent? (medium)

## Output
For each finding: `[severity] location — issue — fix`. End with a ship/hold verdict.
