# Idempotency and recovery checklist

- Does the key identify a **business operation** (not merely a random retry attempt)?
- Is the dedupe record committed atomically with the state it protects, or can a crash split them?
- If an external API cannot join a local transaction, is a stable idempotency key passed and is reconciliation possible?
- Is dedupe retained at least as long as the broker's possible redelivery window?
- Can old event schemas be deserialized after a rollback or delayed message?
- Can outbox publishing be retried without losing events? Are relay duplicates expected?
- Is there a DLQ owner, alert, retention limit, privacy policy, replay procedure, and observable backlog?
- Are event order assumptions documented and enforced by key/partition or application logic?
- Can a saga resume or compensate after process death, including repeated compensation?

Useful crash matrix:

| Window | Expected recovery |
| --- | --- |
| DB commit succeeded; relay not published | Outbox retry/reconciliation |
| Broker delivered; handler committed; ack lost | Redelivery is harmless |
| External side effect succeeded; local status write failed | Stable idempotency key + reconciliation |
