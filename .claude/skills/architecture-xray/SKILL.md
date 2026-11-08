---
name: architecture-xray
description: Map a real codebase's architecture and runtime paths using file-level evidence. Use for onboarding, architecture reviews, microservice boundaries, CQRS flows, unexplained dependencies, or refactor planning.
license: MIT
---

# Architecture X-Ray

Build an **evidence-backed map of the actual system**, not an idealized architecture diagram. Default to **analysis only** unless implementation is explicitly requested.

## Inputs

Identify the user's target feature, workflow, service, or question. Ask one question only if the requested boundary is impossible to infer; otherwise state the scope you chose.

## Workflow

1. Inspect top-level projects, entry points, DI/container setup, routing/handlers, database access, message producers/consumers, jobs, and tests. Use repo search to trace **one end-to-end flow** first. In .NET, inspect solution/project files, `Program.cs`, controllers/minimal APIs, handlers, repositories, EF Core mappings, and messaging registrations where present.
2. Record each architectural claim against a path and, if available, line number. Follow references rather than assuming names imply behavior.
3. Draw a compact Mermaid `flowchart` showing **observed** call/data/message edges. Mark suspected or unverified edges explicitly (`?` or `unverified`). If a diagram would be misleading, use an adjacency table instead.
4. Identify ownership and boundaries: validation, authentication/authorization, transaction scope, persistence authority, cache/search projections, queues, external calls, and error handling. Explain what happens on a timeout and retry when evidence permits.
5. Surface at most five **decision-relevant** concerns ranked by impact and evidence strength. Distinguish design intent from implementation and note test coverage gaps.
6. Recommend a minimal set of next inspections or smallest refactor slice; avoid proposing a rewrite based on directory names alone.

## Output contract

- **Scope and confidence** — examined modules, exclusions, missing access.
- **Observed architecture** — 5-10 lines plus diagram; cite files for edges.
- **Flow trace** — trigger → processing → data side effects → response/events.
- **Risk register** — finding, evidence, failure consequence, confidence, next check (max five).
- **Practical next step** — one low-risk validation or change with acceptance criteria.

## Guardrails

Never assert services communicate, data is authoritative, or transactions are atomic without source/config evidence. If source files or execution access are missing, present a **provisional** map and list exact verification steps. Do not execute migrations or edit code unless requested.

See [evidence grid](references/evidence-grid.md) for a compact source-tracing template.
