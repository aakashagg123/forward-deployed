# JSW One Finance — lending origination platform

*Commercial lending, 100% digital, lead to disbursement.*

**Role:** SPM (AI) · **Company:** JSW One Finance (JOFL) · **Timeline:** November 2024 – present

## Overview

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

Running an AI-native product function means owning the operating model for how the team uses AI to build, not just the roadmap for what gets built. I designed and govern a multi-agent AI development harness that the LOS team uses for day-to-day feature work.

**The learning curve was earned, not assumed.** The first sprints ran without a shared rulebook — AI workers operating in isolation, guessing at data mappings, occasionally introducing their own bugs. Every failure mode became a documented rule: mandatory pre-flight checks before UI work, bounded file lanes so a worker can't wander outside its assigned scope, human checkpoints between build waves, and a security review gate before any feature ships. Each rule eliminated a specific class of error; together they took delivery accuracy from an unguided 82% to a sustained 90%+ band.

**Plan before you build, always.** The team runs roughly 2.6 discovery-and-spec passes for every build pass — close to the opposite of how most people use AI coding tools. That discipline shows up directly in the output: a 4.5:1 feature-to-fix commit ratio, against an industry norm closer to a 10% net productivity gain once rework is subtracted out. Across 130+ skill-driven planning, build, and verification passes a month, the ratio holds because nothing ships without first passing a spec review and a verification gate.

**The harness is measured, not assumed to work.** I track the same rigor for the AI development practice that I'd expect for any product: sprint-by-sprint accuracy, cost per session, cost per line, and cache efficiency, published and reviewed the way any other product's KPIs would be. That measurement discipline is what separates a governed, audited multi-agent system from ad hoc single-agent chat use — and it's the basis for placing this practice in the top 1–3% of the global AI-developer population by governance maturity.

**The numbers, over 131 days:** 360+ sessions, 560K+ lines of production code shipped across the LOS platform, 94%+ context-cache efficiency across 17B+ tokens processed, and roughly 14.7x return on the tooling spend versus API-equivalent compute cost. This is governed, elite-tier AI-native engineering practice — not casual chat-based "AI assistance."
