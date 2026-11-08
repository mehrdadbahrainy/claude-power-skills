---
name: contract-drift-check
description: Compare API DTOs, OpenAPI contracts, and event schemas for backward/forward compatibility. Use before changing REST endpoints, JSON serialization, enums, required fields, event versions, or multi-service deployments.
license: MIT
---

# Contract Drift Check

Decide compatibility in the context of **real producers and consumers**, not only type definitions.

## Workflow

1. Establish baseline (tag/main/released schema) and proposed contract, language/runtime, wire format, and known consumers. If unavailable, clearly mark comparison provisional instead of inventing a diff.
2. Extract the external shape: method/path, parameter names, status codes, headers, JSON field names, nullability/requiredness, enum representation, defaults, event names/versions, validation and error bodies.
3. Build a field-by-field **old vs new matrix**. Check how old clients parse new responses and how new services parse old messages. Inspect serializer settings and consumer code; assume strict clients exist until shown otherwise.
4. Assess changes to both syntax and behavior: removed/renamed field, changed type, narrower validation, optional→required, default shifts, meaning changes, ordering, pagination, auth or status-code behavior. State whether risk is known, conditional, or unknown.
5. Recommend a safe transition: additive change, tolerant consumer, dual-read/dual-write, upcaster, feature flag, endpoint/event versioning, backfill, compatibility test, and deprecation window as appropriate.
6. If asked for implementation, make the minimal change and add contract tests using **serialized wire examples**; report executed vs proposed tests honestly.

## Output contract

- Compared versions/sources and consumer assumptions.
- Compatibility table with change, old-producer/new-consumer and new-producer/old-consumer outcomes, evidence, severity.
- Safe rollout order and rollback constraints.
- Concrete golden-payload/consumer test cases.
- Explicit missing consumers and verification gaps.

See [compatibility matrix](references/compatibility-matrix.md). Avoid calling a change "safe" just because it compiles or OpenAPI validates.
