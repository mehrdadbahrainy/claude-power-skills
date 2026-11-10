---
name: legacy-code-modernizer
description: Plan and implement low-risk, incremental modernization of legacy codebases. Use when asked to migrate old .NET apps, split monoliths, update frameworks, or replace old architecture safely.
license: MIT
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/codebase_inventory.py *)
---

# Legacy Code Modernizer

Modernize a **small vertical slice with protected behavior**. Prefer a strangler/branch-by-abstraction path to a big-bang rewrite. Do not infer obsolescence or security support status from a version number without checking the vendor's current lifecycle documentation.

## Entry and permissions

- Identify what the user wants improved (runtime, architecture, framework, deploy model, performance), release constraints, and what cannot change (public contracts, output shape, timing, business rules).
- Start with **read-only inventory and planning**. Do not modify build files, upgrade dependencies, replace authentication or databases, install SDKs, or run migrations until the user requests implementation and the environment can be controlled.
- For modernization implementation, choose **one small slice** per iteration with a rollback path; change more only after acceptance tests pass.

## Workflow

1. Inventory code, project files, target frameworks, dependencies, test locations and build entry points. Optionally run:
   `python3 ${CLAUDE_SKILL_DIR}/scripts/codebase_inventory.py --root .`
   (`${CLAUDE_SKILL_DIR}` is this skill's folder; if your client does not expand it, use the `scripts/` folder next to this file.) This tool makes a local file inventory, including legacy .NET signals such as `packages.config`, `web.config`/`app.config` and WebForms pages; project metadata can be inherited or computed, so verify findings against build files and docs.
2. Map actual dependencies and runtime behavior with source evidence. Identify one user/business workflow that crosses the legacy boundary.
3. Create a **characterization baseline** before edits: golden output fixture, contract test, snapshot with stable fields, or end-to-end smoke check. Record known nondeterministic fields and external dependencies; avoid capturing production PII.
4. Build a tradeoff matrix for (A) keep and stabilize, (B) in-place upgrade, (C) extract behind an abstraction/adapter, (D) replace a vertical slice. Choose based on risk, team ownership, tested parity, and rollback, not trends.
5. Define a **thin seam** (interface, routing façade, anti-corruption layer, feature flag, read-only shadow run) preserving the observable old contract. For DB changes, use compatible expand/migrate/contract phases; never assume rollback of destructive data transformations is possible.
6. If implementation was requested, write the characterization test first, make one bounded change, run available verification, compare old/new behavior, and pause before the next slice. Do not silently mix framework upgrade with wide refactoring.
7. Plan the next two milestones with explicit rollback triggers, metrics, owner and evidence gaps. Avoid assigning an unverified time estimate.

## Output contract

- **Inventory** — observed runtimes, project/module boundaries, tests and constraints (mark unknowns).
- **Preservation contract** — behavior to keep and how to assert it.
- **Options** — 2-4 approaches with cost/risk/reversibility.
- **First migration slice** — exact files/contract, seam, test and deployment/rollback.
- **Evidence** — commands executed vs proposed, test results, leftover risks.
- **Next milestone** — one bounded step and objective pass/fail criterion.

See the [migration patterns](references/migration-patterns.md) and [slice plan](assets/slice-plan-template.md). Pair with `contract-drift-check` or `release-rehearsal` when a migration changes external contracts or deployment sequencing.
