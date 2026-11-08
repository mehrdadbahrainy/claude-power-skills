# Compatibility guide

| Change | Typical risk | Investigate |
| --- | --- | --- |
| Add optional response field | Low with tolerant clients; breaks strict schemas | Real client parsers and schema validators |
| Remove/rename field | High for existing consumers | Usage search and golden payload tests |
| Optional → required request field | High for older callers | Validation rollout, defaults |
| Add enum value | Conditional for exhaustive switches | Client fallback behavior |
| Change number ↔ string | High wire-format break | Serializer converters and typed clients |
| Change semantics without schema change | Often high | Domain expectations and contract tests |
| Version an event while old messages remain | Conditional | DLQ/replay/deserializer support |

Use two-direction reasoning:

- **Backward compatibility:** can the new producer/server serve existing consumers?
- **Forward compatibility:** can older services safely encounter newer optional information or delayed events?

For event-driven systems, explicitly test old event → new consumer **and** new event → old consumer during rolling deployment. Consider delayed events after rollback.
