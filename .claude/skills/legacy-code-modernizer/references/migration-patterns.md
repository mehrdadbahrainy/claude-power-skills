# Practical modernization patterns

| Pattern | Works best when | Watch for |
| --- | --- | --- |
| Characterization tests | Business behavior is undocumented | Snapshot brittleness, mutable clocks, secrets |
| Branch by abstraction | Many callers rely on one legacy implementation | Parallel behavior drift; awkward adapters |
| Strangler façade | Traffic can be routed per endpoint or tenant | Auth/session parity and rollback routing |
| Anti-corruption layer | Old and new domain models differ | Mapping errors, duplicated business rules |
| Read-only shadow | New queries can run without side effects | PII in logs, divergence alerts, load costs |
| Expand → migrate → contract | DB schemas must support mixed versions | Old writers, irreversible migrations, delayed events |
| Feature flag | A reversible activation seam exists | Data migration and async effects survive rollback |

## Guardrails

- Protect behavior with tests **before** rewriting; use representative *synthetic* data when real customer data is sensitive.
- Separate syntax/framework updates from behavioral change, schema change, and deployment change when practical.
- Verify published supported runtimes and library compatibility before recommending a version target.
- Treat "no tests found" as an inventory observation, not proof that a system has no tests.
- Don't refactor every layer just because one dependency looks old.
- Pay attention to long-running jobs, stale consumer messages, database shared writers, and authentication transitions.

## Slice acceptance example

One endpoint is served by the new implementation behind a reversible switch. It returns equivalent authorized results for characterization fixtures; old and new can be deployed concurrently; telemetry captures divergence; rollback does not require restoring changed data. Mark these conditions as a **target**, not an achieved state.
