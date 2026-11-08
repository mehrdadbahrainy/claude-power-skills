# Modernization slice plan

**Business workflow:** [one narrow user journey]
**Observed starting state:** [repo paths, tests, deployed version where known]
**Invariant:** [behavior or contract that cannot change]
**Candidate seam:** [adapter/routing/abstraction]
**Options considered:** [stabilize, in-place, extraction, replacement]

| Phase | Exact scope | Evidence / test | Rollback | Owner |
| --- | --- | --- | --- | --- |
| Baseline | [paths] | [characterization fixture] | no changes | [name] |
| Seam | [paths] | [old behavior preserved] | old path selected | [name] |
| New behavior | [paths] | [contract parity] | switch/roll-forward | [name] |
| Activate | [deployment/flag] | [observability gates] | [safe condition] | [name] |

**No-go conditions:** [unavailable rollback, unknown contract consumer, data loss risk]
**Tests actually run:** [commands, outcomes]
**Tests not run:** [reasons, owners]
**Next small step:** [one objective checkpoint]
