---
name: query-performance-detective
description: Diagnose slow SQL and EF Core data access using evidence, query-shape analysis, and measurement-driven fixes. Use for N+1 queries, slow endpoints, missing indexes, pagination, excessive allocations, or query-plan reviews.
license: MIT
---

# Query Performance Detective

Treat performance claims as hypotheses until supported by measurements. Avoid changing correctness for speed.

## Workflow

1. Locate the affected request/job, its repository/ORM query, relevant schema/indexes, and current observable symptoms (latency, throughput, query count, CPU/IO, row count). State which are user-reported vs measured.
2. Trace the generated SQL when available (`ToQueryString`, logged command text, prepared statements); inspect EF Core projections, tracking, client evaluation, `Include`, split/single queries, pagination, and materialization. Never claim generated SQL without seeing it.
3. Check likely causes: N+1 round trips, missing predicates, wide payloads, row multiplication, non-sargable filters, unsuitable indexes, large `OFFSET`, poor cardinality estimates, parameter sensitivity, connection starvation, unnecessary serialization.
4. Select **one bottleneck hypothesis at a time**, with a repeatable test and before/after metrics: SQL duration, logical reads/plan, calls per request, allocation, p50/p95 latency, and result equivalence. Make recommendations specific to the DB engine.
5. Propose the minimum safe fix: query/projection change, batching, keyset pagination, index with key order and included columns, or caching with invalidation rationale. Note write cost and storage/index tradeoffs.
6. If implementation is requested, add correctness coverage, change code in a small diff, run authorized benchmarks/tests, and present measurements or explicitly mark them unavailable.

## Output contract

- **Baseline:** query path and measured/user-reported symptoms.
- **Hypotheses:** each with supporting source and a falsifiable measurement.
- **Recommended experiment:** exact collection method and success criteria.
- **Safe patch proposal:** pseudocode or diff only if useful; preserve ordering, filters, authorization, and transaction behavior.
- **Evidence status:** `measured`, `source-supported`, or `unverified` for each improvement claim.

Read [the EF Core playbook](references/ef-core-playbook.md) when the repository uses EF Core. Never run `UPDATE`, `DELETE`, DDL, or migrations against a real database without explicit authorization.
