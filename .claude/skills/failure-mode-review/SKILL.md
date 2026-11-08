---
name: failure-mode-review
description: Review a code change by constructing concrete failure scenarios and invariants instead of generic style comments. Use before merging risky code, reviewing retries/payments/orders, or finding missing edge-case tests.
license: MIT
---

# Failure-Mode Review

Perform a **failure-first review** of a diff, handler, or workflow. Prioritize plausible regressions with observable consequences. Review only unless asked to implement fixes.

## Workflow

1. Establish the reviewed change (PR/diff/commit/files). Read callers, callees, tests, and surrounding error-handling paths. If no diff is available, explicitly report the scope as a static review.
2. Identify the critical invariants, e.g. "one customer is charged at most once per business operation" or "failed writes never produce a success response". Verify each invariant against the code.
3. Enumerate realistic perturbations: duplicate request/event, timeout after side effect, process restart, partial dependency outage, cancellation, stale read, concurrency, malformed input, permission change. Only pursue those relevant to the path.
4. For each significant issue, provide a **reproducible timeline**: initial state → trigger → interleaving/failure → undesired outcome → supporting code path. Distinguish a demonstrated bug from a plausible hypothesis.
5. Rank findings by impact *and* evidence. Propose a focused test (unit, integration, concurrency, fault injection, property-based) with setup, stimulus, and expected assertion.
6. When the user requests a fix, implement the smallest corrective change with a regression test first where practical, then run authorized checks and report their actual results.

## Severity

- **P0:** likely data loss/security/financial corruption in a common path.
- **P1:** material production defect with a credible trigger.
- **P2:** conditional resilience gap or important missing guard.
- **P3:** low-impact hardening or clarity improvement.

Do **not** assign P0/P1 based purely on possibility without a credible path.

## Output contract

1. Reviewed scope and tools actually run.
2. Invariants and which are enforced vs assumed.
3. Up to five findings, each with **severity, file/line evidence, failure timeline, test, proposed fix, confidence**.
4. Tests performed vs tests proposed, clearly separated.
5. Merge decision: `block`, `review further`, or `no blocking issue observed` (never claim bug-free).

See the [failure catalog](references/failure-catalog.md) for test ideas. If evidence is insufficient, give a targeted verification plan rather than manufacturing bugs.
