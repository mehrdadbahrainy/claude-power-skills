# Failure catalog: choose relevant cases, not every case

| Failure | Example assertion |
| --- | --- |
| Client retries after timeout | Business side effect occurs once (idempotency key persisted) |
| Worker crashes after DB commit | Event is eventually published or safely reconciled |
| Message redelivery | Consumer produces the same final state without duplicate effects |
| Concurrent updates | Version/concurrency check rejects stale transition |
| Cancellation mid-operation | Commit boundary and cleanup remain consistent |
| Partial dependency outage | Circuit/bounded retry and explicit user-facing failure |
| Malformed/untrusted input | Validation before side effects; no sensitive details leaked |
| Cache lag | Documented freshness behavior; no silent correctness violation |

A hypothetical sequence is not proof. Record whether the behavior was observed in test, established from source, or is a risk to test. Prefer deterministic failure injection over sleeping/flaky timing tests.
