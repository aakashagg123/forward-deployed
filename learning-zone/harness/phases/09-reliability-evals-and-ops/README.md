# Phase 09 — Reliability, evals, and ops
*Part of [Harness engineering](../../README.md).*

This phase turns a working agent into one you can run in production. You will handle failures in order of cost, cap the worst case, and report partial results honestly. You will measure the agent with a gate that can fail, see each run as a trace with a price, and ship changes to a few users first.

## Lessons
1. [The failure ladder: retry, repair, fall back](./01-failure-ladder/docs/en.md) — Match each failure to the cheapest fix.
2. [Budgets, idempotency, and degraded mode](./02-budgets-idempotency-degraded-mode/docs/en.md) — Cap the worst case, never act twice, stop honestly.
3. [The eval harness and its regression gate](./03-eval-harness/docs/en.md) — One command scores the agent and exits 1 on a regression.
4. [Tracing and cost](./04-tracing-and-cost/docs/en.md) — Nested spans, priced and tagged.
5. [Rollout, kill switches, and the CI gate](./05-rollout-and-ci-gate/docs/en.md) — Canary, one switch to undo it, and a workflow that blocks bad merges.

## Where the depth lives
| If you want | Read |
| --- | --- |
| The product view of reliability and failure | [Reliability and failure](../../../technical-product-sense/reliability-and-failure.md) |
| The eval stack and how to order it | [Evals](../../../content/04-evals-observability/evals.md) |
| Why eval investment is the job | [Evaluation and observability](../../../evaluation-and-observability/README.md) |
| Spend attribution and budgets | [Cost attribution](../../../content/04-evals-observability/cost-attribution.md) |
| Incident handling | [Incidents and postmortems](../../../technical-product-management/incidents-and-postmortems.md) |
| Launch and rollout practice | [Launches, rollouts, and migrations](../../../technical-product-management/launches-rollouts-and-migrations.md) |

## Test yourself
1. **A model call returns 429 once, then valid JSON with a missing field. Which rungs of the ladder run, in what order?**
   <details><summary>Answer</summary>Retry runs first, because 429 is a transport error. The retry waits with backoff and jitter and gets the reply. Then repair runs, because the content is invalid: the validator error goes back to the model. Fallback runs only if both rungs spend their budgets. (<a href="./01-failure-ladder/docs/en.md">Lesson 1</a>)</details>
2. **Why is retrying a call that sends an email dangerous, and what makes it safe?**
   <details><summary>Answer</summary>A retry can repeat a side effect that already happened. An idempotency key built from the tool and its arguments makes a repeat return the stored result. If the outcome is unknown after a timeout, pass the key to the remote service too. (<a href="./02-budgets-idempotency-degraded-mode/docs/en.md">Lesson 2</a>)</details>
3. **A run stops because the token meter hit its limit after 3 of 5 steps. What must the result contain?**
   <details><summary>Answer</summary>It must say `degraded`, not `complete`. It lists the 3 verified steps, the 2 that remain, the reason, what was spent, and a next step. It never claims success it did not verify. (<a href="./02-budgets-idempotency-degraded-mode/docs/en.md">Lesson 2</a>)</details>
4. **Your eval gate has never failed. Why is that a warning sign, and how does this phase test for it?**
   <details><summary>Answer</summary>A gate that cannot fail protects nothing. The harness includes a regressed candidate and asserts that it exits 1. The CI workflow runs that same check. (<a href="./03-eval-harness/docs/en.md">Lesson 3</a>)</details>
5. **What can a trajectory check catch that a golden check cannot?**
   <details><summary>Answer</summary>A right answer reached the wrong way: tests skipped, a forbidden tool called, too many steps. A golden check only compares the final output. (<a href="./03-eval-harness/docs/en.md">Lesson 3</a>)</details>
6. **Why does cost belong on spans, and why must the price table be labelled as an example?**
   <details><summary>Answer</summary>A span that holds model and token counts lets you roll cost up by feature or tenant, and a child inherits its parent's tag. Prices change, so a real harness loads and versions the current price list instead of hard-coding it. (<a href="./04-tracing-and-cost/docs/en.md">Lesson 4</a>)</details>
7. **Why does the rollout check the kill switch before the canary percent?**
   <details><summary>Answer</summary>During an incident, the responder flips one switch and everyone gets the stable version. They never have to reason about percentages or buckets. (<a href="./05-rollout-and-ci-gate/docs/en.md">Lesson 5</a>)</details>
8. **You raise a canary from 10% to 50%. Why do users not flicker between versions?**
   <details><summary>Answer</summary>The bucket comes from a hash of the flag name and the user id, so it is stable. A unit is on the canary when its bucket is below the percent. Raising the percent only adds units. (<a href="./05-rollout-and-ci-gate/docs/en.md">Lesson 5</a>)</details>
