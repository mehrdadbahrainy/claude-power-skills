# Release / rollback checklist

**Before deploy**
- Exact artifact/version and dependency inventory known?
- Backup taken and **restore tested**, not merely scheduled?
- New and old code compatible with intermediate schema?
- Worker/event formats compatible with delayed queue messages?
- Feature flags and rollback authority identified?
- Monitoring dashboard, alerts, and operator contact available?

**At each checkpoint**
- Is the observed metric from production, staging, or a proposed probe?
- Is there a specific abort trigger, not just "monitor errors"?
- Are current writes reversible? If not, is roll-forward the primary recovery route?
- What happens if API succeeds but consumer processing lags or stops?

**After deploy**
- Compare key business outcomes as well as health endpoints.
- Verify logs do not expose secrets or customer data.
- Track queue age, outbox backlog, error rate, latency, and a representative successful business transaction.
- Record deviations, actual command outcomes, decision time and owner.

Never offer a "one-command rollback" for non-reversible schema/data changes.
