# Evidence grid

Use a table while tracing paths:

| Claim | Source location | Observation | Confidence | Missing verification |
| --- | --- | --- | --- | --- |
| API enters handler H | `src/...:line` | Route maps to H | High | Integration routing test |
| Search reads an index | `src/...:line` | Client queries index X | High | Alias/index deployment mapping |
| Index is rebuildable | No confirmed source | Hypothesis only | Low | Identify rebuild/replay job |

Trace one path at a time:

`entry point → authorization → request mapping → handler → transaction → storage/outbox → consumer → read model`.

Watch for cross-cutting behavior in middleware, decorators, interceptors, background workers, DI registrations, and deployment configuration. Distinguish runtime edges from type dependencies. When citing a Mermaid edge, put corresponding file references in the explanation; the diagram is a summary, not proof.
