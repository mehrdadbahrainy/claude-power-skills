# EF Core / SQL playbook

Start with **query count per request**, returned row count, and shape; then investigate plan and IO. Suggested safe local probes:

- `query.ToQueryString()` for inspecting generated SQL where supported. It is a diagnostic view, not a fully executed query plan.
- `AsNoTracking()` for read-only projections when identity and change tracking are unnecessary.
- `Select(...)` to avoid loading large graphs; compare output shape and serialization.
- `AsSplitQuery()` only after understanding extra round trips and consistency implications; compare against join row multiplication.
- For pagination, enforce deterministic ordering; consider seek/keyset when offsets grow.
- For indexes, verify filter selectivity, sort order, included columns, update costs, and actual plan usage.
- SQL Server: inspect actual/estimated plans, statistics, logical reads and parameter effects; do not conflate estimated cost with elapsed time.

Avoid common false fixes: adding an index to every filter column, blanket caching with no invalidation strategy, changing transactions for a benchmark, or claiming a faster method after one noisy request.
