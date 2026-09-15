# JSW One Finance — lending origination platform

*Commercial lending, 100% digital, lead to disbursement.*

**Role:** SPM (AI) · **Company:** JSW One Finance (JOFL) · **Timeline:** November 2024 – present

JOFL is a digital-first NBFC and wholly owned subsidiary of JSW One Platforms, built to serve the credit needs of India's MSME ecosystem. I lead the lending origination (LOS), CRM, and AI charter as one of the earliest product hires on the team — and, distinctly, I own the operating model for *how* the team builds, not just the roadmap for what gets built.

## What I built

- Channel finance, vendor finance, and term loan origination (LOS)
- The lending API suite, and LOS–LMS governance across the stack
- The customer master that underpins every lending product
- A governed, multi-agent AI development harness for the LOS platform — the team's day-to-day mechanism for shipping feature work with AI
- A measurement system for the harness itself: sprint-level accuracy, cost, and output tracked the same way the team tracks product KPIs

## Outcome

Commercial lending at JOFL runs end to end digitally, and the business has grown 4x in AUM since FY25. Over 131 days, the AI development harness ran 360+ sessions and shipped 560K+ lines of production code at a 4.5:1 feature-to-fix ratio, for roughly 14.7x return on AI tooling spend against API-equivalent compute cost — at 94%+ context-cache efficiency across 17B+ tokens processed.

## The deeper dive

The LOS platform is built inside a governed, multi-agent AI development harness — the operating model for how the team ships, not just what gets built. The workflow, stage by stage:

1. **Spec before build.** Every feature starts as a discovery-and-spec pass, not a prompt. The team runs 2.6 plan passes for every build pass — the inverse of typical AI-assisted coding.
2. **Bounded execution.** Workers run pre-flight checks and operate inside fixed file lanes, so a worker can't wander outside its assigned scope or guess at data mappings.
3. **Human checkpoints between build waves.** Nothing moves to the next wave unblocked; a person reviews the diff at each gate.
4. **Mandatory security review before ship.** Every feature clears a security gate before it merges — no exceptions for scope or deadline.
5. **Measured like a product.** Sprint-by-sprint accuracy, cost per session, cost per line, and cache efficiency are tracked and reviewed the same way the team tracks any other product's KPIs.

**The result, over 131 days:** 360+ sessions, 560K+ lines of production code shipped across the LOS platform, delivery accuracy from an unguided 82% to a sustained 90%+ band, a 4.5:1 feature-to-fix commit ratio, 94%+ context-cache efficiency across 17B+ tokens processed, and roughly 14.7x return on tooling spend versus API-equivalent compute cost.
