# Blue-green for processes: strategies that survive audits

> **Motto** — Stateless services cut over; stateful processes *coexist* — your real
> choices are drain, migrate, or route, and each writes a different audit story.

*Part of Phase 08 — Versioning & migration. Concept lesson — no code required.*

## The Problem

Your platform team blue-greens services: stand up green, shift traffic, kill blue,
done in an afternoon. Then they ask why the process tier can't work the same way.
The answer is Phase 2: instances are *state with a lifespan*. A mortgage
application mid-flight is "traffic" that lasts nine months. You cannot cut it
over by flipping a load balancer. You can only decide, deliberately, which
definition each cohort of live state follows, and be able to tell an auditor,
for any given application, *which rules it ran under and why*.

## The Concept

Three strategies, all built from lesson 01's version rules and lesson 02's
migration:

<style>
.dgm-bg{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #a63d40;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-bg-chip{position:absolute;top:-11px;left:24px;background:#a63d40;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(166,61,64,.28)}
.dgm-bg h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-bg-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-bg-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-bg-branches{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.dgm-bg-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-bg-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-bg-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-bg-b.accent{background:#faeceb;border-color:#e3b3ad}
.dgm-bg-b.accent h6{color:#7a2c2e}
.dgm-bg-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-bg-b.blue h6{color:#0550ae}
.dgm-bg-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-bg-b.green h6{color:#1a614f}
.dgm-bg-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-bg-b.red h6{color:#82061e}
.dgm-bg-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-bg-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-bg{padding:20px 16px 18px}.dgm-bg-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-bg">
  <span class="dgm-bg-chip">Three options for the pinned population</span>
  <h4>New starts bind the new version automatically — what about instances already running?</h4>
  <p class="dgm-bg-sub">Drain, migrate, or route — pick per how risky the change is.</p>
  <div class="dgm-bg-q">New version v(N+1) deployed</div>
  <div class="dgm-bg-branches">
    <div class="dgm-bg-b accent">
      <h6>Drain</h6>
      <p>Old instances finish on old logic</p>
    </div>
    <div class="dgm-bg-b blue">
      <h6>Migrate</h6>
      <p>Move cohorts to the new version</p>
    </div>
    <div class="dgm-bg-b green">
      <h6>Route</h6>
      <p>New parallel key; the entry point chooses</p>
    </div>
  </div>
</div>


| Strategy | Mechanics | Choose when | Audit story |
| :-- | :-- | :-- | :-- |
| **Drain** (default) | deploy; do nothing else; old versions empty out on their own | change is an improvement, not a correction; instance lifetimes are bounded | "policy X applied to applications started after date D" — clean cohort line |
| **Migrate** | lesson 02's ritual, usually in cohorts (validate → canary batch → rest) | old logic is *wrong* and in-flight cases must pick up the fix | "instances A…N moved to v5 on date D by change ticket T" — needs the migration log kept |
| **Route** | new *key* (`loanOriginationV2`); a start-level router (gateway, call activity, or caller config) picks per case | structural rewrites too different to map; A/B trials; per-segment rollout | two products running side by side — simplest to explain, costliest to operate (double dashboards, double fixes) |

Decision discipline that keeps this survivable:

1. **Drain is the default; justify anything else.** Migration is risk (lesson
   02), and routing means double operations. The question is never "can we move
   them," but "what breaks if we don't."
2. **Suspend is your brake, not a strategy.** After a bad deploy, suspend that
   definition version — this stops new starts while live instances continue —
   and decide from there. Suspending *instances* freezes real customers. That
   is an incident action with a comms plan, not a rollout tool.
3. **Rollback means roll forward.** There is no un-deploy. If v5 is defective,
   deploy v6 (fixed, or a copy of v4) and apply the same three-way choice to
   v5's brief population. Deleting a version with live instances is how you
   orphan state.
4. **The cohort line is the compliance artifact.** Whichever strategy you pick,
   the deliverable an audit accepts is a statement per application of *which
   version decided it*. Lesson 01's history pinning gives you that for free,
   **if** history retention (Phase 9) outlives the question.

## Ship It

This lesson ships
[`outputs/rollout-decision-guide.md`](../outputs/rollout-decision-guide.md) — the
three strategies as a decision path, plus the canary-cohort migration sequence.

## Check Yourself

**Q1.** Why doesn't service-style blue-green transfer to the process tier?

- A) engines are too slow
- B) instances are long-lived state pinned to definitions — there's no stateless "traffic" to cut over, only cohorts to drain, migrate, or route
- C) load balancers can't see BPMN
- D) it does transfer

<details><summary>Answer</summary>B — the unit of rollout is the instance cohort,
not the request. Everything else in the lesson follows from that.</details>

**Q2.** A pricing *improvement* ships mid-quarter. In-flight applications should
normally…

- A) be migrated immediately
- B) drain on the old pricing — improvements apply forward; the clean cohort line is itself worth keeping
- C) be suspended
- D) be cancelled and restarted

<details><summary>Answer</summary>B — reserve migration for corrections. "Started
before D → old terms" is an audit story that writes itself.</details>

**Q3.** v5 turns out defective an hour after deploy. First move?

- A) delete v5
- B) suspend the v5 definition (new starts stop), deploy the fix as v6, then decide drain-vs-migrate for v5's small population
- C) migrate everything to v4
- D) restart the engine

<details><summary>Answer</summary>B — brake, roll forward, then cohort decision.
Deleting a version with live instances orphans them.</details>

**Challenge.** Write the rollout plan (one page) for the capstone's "compliance
step added" scenario: strategy per cohort, the suspend trigger, the canary batch
size, and the exact sentence you'd give an auditor for an application started the
day before the deploy. Check it against the shipped decision guide.

## Related

- Next: [Backward-compatible model changes](../../04-compatibility-checklist/docs/en.md)
- The brake and the pin: [Definition versions](../../01-definition-versions/docs/en.md)
