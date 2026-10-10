# Orders service

Python 3.12 service that stores and prices customer orders. You fix bugs and add features here.

## Commands
- Test: `pytest -q`
- Lint: `ruff check .`
- Run locally: `python -m orders.server`

## Conventions
- Import from the public package `orders`, never from `orders._internal`.
- One API route per file in `orders/routes/`. Name the file after the resource.
- Money is an integer number of cents. Never use float for money.

## Approach
- Make the smallest change that meets the task. Run `pytest -q` before you say it is done.
- Ask before you touch `migrations/` or anything under `deploy/`.

## Where to look
- Architecture and data flow: `docs/architecture.md`
- Pricing rules: `docs/pricing.md`
- How to write tests here: `docs/testing.md`

<!-- Maintainer note: keep this file short. Detail goes in docs/. Comments like this one
     are removed before the file is sent to the model, so they cost no tokens. -->
