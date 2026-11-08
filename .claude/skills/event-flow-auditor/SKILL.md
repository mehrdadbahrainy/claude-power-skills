---
name: event-flow-auditor
description: Audit asynchronous workflows, message brokers, outbox/inbox, sagas, and retries for delivery, idempotency, ordering, and recovery. Use for Kafka, RabbitMQ, event-driven .NET systems, or duplicate/late events.
license: MIT
---

# Event-Flow Auditor

Find **where the business workflow becomes inconsistent under real delivery semantics**. Never assume exactly-once delivery because a framework uses that phrase.

## Workflow

1. Define the business outcome, event envelope (ID, type, version, correlation/causation IDs), broker, producer/consumer, and persistent stores. Trace registration/configuration, publication, handling, retry/DLQ, and acknowledgments.
2. Sketch an ordered timeline with relevant boundaries: producer DB transaction, outbox insert, relay publish, broker ack, consumer side effect, inbox/dedupe record, consumer ack. Cite evidence for each.
3. Explicitly examine crash windows: before/after commit, publish-before-ack, handle-before-ack, retry after irreversible effect, redelivery after restart, broker reorder, stale event version.
4. Check each business invariant under duplicates, concurrency, reordering, poison messages, schema evolution, and compensation failure. Differentiate broker delivery from **business effect** guarantees.
5. Give an idempotency key strategy (business operation vs transport ID), dedupe storage scope and retention, transaction boundaries, and reconciliation/replay procedure. Explain assumptions about partition keys and ordering.
6. Recommend minimal tests using duplicate/redelivery, restart, delayed messages, and partial outages. If asked to change code, implement one bounded fix and run permitted tests.

## Output contract

- **Topology:** producer → outbox/transport → consumers → durable side effects (with cited paths).
- **Guarantee table:** possible duplicates, ordering, durability, retries, and what remains unverified.
- **Top failure windows:** specific state/timeline/effect/repro test.
- **Recovery:** DLQ, replay, compensation, and reconciliation plan (or identified gaps).
- **Minimal correction:** smallest safe next change and an observable success criterion.

See [idempotency checklist](references/idempotency-checklist.md). Do not trigger replays, purge queues, or modify production messages without explicit authorization.
