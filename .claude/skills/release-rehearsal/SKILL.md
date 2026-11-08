---
name: release-rehearsal
description: Prepare a production release readiness and rollback rehearsal grounded in code, migrations, infrastructure, and operations. Use before risky deploys, database migrations, worker upgrades, feature flags, or go/no-go decisions.
license: MIT
---

# Release Rehearsal

Create an **executable release plan**, not a generic checklist. Never deploy, modify live infrastructure, or run production migrations without explicit authorization.

## Workflow

1. Identify release scope (commits, services, migrations, flags), dependencies, environment, owners, and availability/traffic constraints. Inspect deployment config, migrations, compatibility expectations, monitoring, and documented recovery where accessible.
2. Separate changes into **reversible**, **conditionally reversible**, and **irreversible**. Examine expand/contract DB strategy, rolling versions, delayed events, queue backlogs, and schema compatibility under mixed versions.
3. Define preflight checks with exact commands or queries only when verified as appropriate for this environment. Mark missing permissions, backups, and restore tests as blockers rather than guessing.
4. Sequence steps and checkpoints: backup/restore readiness → deploy-safe schema → compatible services → worker/replay coordination → feature enablement → verification. Include owner, observation, expected result, and abort trigger per phase.
5. Write a rollback or roll-forward strategy for each failure stage; be explicit when data changes cannot be undone. Note RPO/RTO **only if actually established**.
6. Define a 15/30/60-minute verification plan with technical and business signals (5xx, p95 latency, queue age, error rate, transaction outcome). These are suggested checkpoints, not claims of existing SLOs.

## Output contract

- **Go/no-go:** `go`, `conditional`, or `no-go`, with evidence and blocking unknowns.
- **Risk matrix:** irreversible effects, compatibility, operational dependencies.
- **Release timeline:** ordered steps, owners, verification, abort criteria.
- **Recovery playbook:** roll back vs roll forward by phase and data recovery limits.
- **Post-release watchlist:** signals, thresholds where known, escalation path.

Use [rollback checklist](references/rollback-checklist.md). On missing environment access, prepare a dry-run plan, never claim a release is safe or that a rehearsal was executed.
