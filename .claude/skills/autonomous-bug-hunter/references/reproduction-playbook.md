# Reproduction playbook

## Ladder of evidence

1. **Observed**: runtime log, failing test, or reproducible command with an actual result.
2. **Code-established**: exact control flow directly supports the outcome, but not exercised.
3. **Hypothesis**: credible pathway awaiting reproduction.
4. **Speculation**: no traceable path — do not report as a bug.

## Recommended local sequence

- Identify one observable invariant and smallest boundary (function, service, queue consumer, API).
- Preserve an explicit baseline: revision, runtime version, environment flags, test input. Redact secrets.
- Attempt one deterministic negative test. For concurrency, prefer synchronization barriers or fault injection over arbitrary sleep.
- When a real failure occurs, isolate inputs by removing unrelated steps. Record what remains necessary.
- Confirm the fix with the same reproducer; run at least the neighboring tests.
- Do not change production settings, run against live accounts, brute-force credentials, or execute network fuzzers.

## How to use the scout

`python3 .claude/skills/autonomous-bug-hunter/scripts/change_risk_scan.py --repo . --base HEAD`

The scout analyzes *tracked* changes relative to a chosen Git revision; untracked files are counted but not analyzed. Regex matches identify review candidates only. Output contains changed file paths and line numbers, not source code. Common false positives include comments, test fixtures, and generated code. It does not execute the changed project.

## Failure timeline

| Moment | State | Action / failure | Observation |
| --- | --- | --- | --- |
| T0 | Initial state | Setup | Test baseline |
| T1 | In-flight | Fault or competing action | Trace/log |
| T2 | Recovery | Retry / exception | Actual divergence |

Prefer one report with a verified regression over many unactionable suspicions.
