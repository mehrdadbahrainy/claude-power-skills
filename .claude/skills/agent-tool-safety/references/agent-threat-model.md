# Agent trust-boundary checklist

| Boundary | Risk | Trusted enforcement |
| --- | --- | --- |
| Retrieved content → model | Embedded instructions override task | Treat source as data; tool-side controls persist |
| Model → tool args | Invalid or out-of-scope operation | Schema + semantic validation in trusted handler |
| User identity → data query | Cross-tenant disclosure | Tenant filters server-side, not in model prompt |
| Tool retry → external API | Duplicate orders/cancellations | Durable business idempotency keys |
| Tool result → user | Secret or PII leak | Response shaping/redaction and permission checks |
| Model → financial mutation | Unauthorized or costly action | Confirmation and policy decision in application |

Benign evaluation examples: product description asks agent to ignore user task; search result includes a fake instruction that looks like a system role; tool response requests access to a different tenant; agent retries create-order after a simulated timeout. Verify backend denial even if the agent makes an unsafe suggestion.

Security acceptance criterion: privileged actions fail closed when identity, scope, or confirmation cannot be established. Do not claim a prompt defense eliminates injection risk.
