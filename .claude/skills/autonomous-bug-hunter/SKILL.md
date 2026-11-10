---
name: autonomous-bug-hunter
description: Reproduce and fix one concrete bug with a bounded, evidence-driven loop. Use when a specific symptom, regression, flaky or failing test, or crash needs to be proven with a minimal failing test; for reviewing a diff before merge, use failure-mode-review instead.
license: MIT
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/change_risk_scan.py *)
---

# Autonomous Bug Hunter

Find **one real, reproducible bug at a time**, not a list of speculative flaws. Autonomous means a bounded investigation that can run available local read-only checks and authorized tests; it does **not** grant permission for production access or unreviewed changes.

## Entry and authorization

- Identify target behavior, suspect diff/area, expected invariant, and user constraints. Prefer a narrowly scoped investigation (one endpoint, service, crash, or PR).
- By default **inspect only**. You may execute existing local tests or the included read-only scout when execution is available and suitable, but ask before installing dependencies, modifying source, adding tests, triggering network calls, or running expensive suites. If user explicitly asks you to fix the bug, write a regression test and minimal patch within that scope.
- Avoid commands with production credentials; do not call live URLs, mutate databases, publish events, or run destructive/fuzz tests against external services.

## Investigation loop (limit: 3 hypotheses per pass)

1. Capture the symptom: actual vs expected outcome, environment, deterministic or intermittent, user-visible impact.
2. Inspect the relevant code, callers, tests, logs **provided** or available locally; annotate each claim with a file path / line number or a command result.
3. Optionally run the deterministic read-only scout to find *review candidates* in the latest diff:
   `python3 ${CLAUDE_SKILL_DIR}/scripts/change_risk_scan.py --repo . --base HEAD`
   (`${CLAUDE_SKILL_DIR}` is this skill's folder; if your client does not expand it, use the `scripts/` folder next to this file.) Pass `--base` only as a revision taken from Git itself or the user, never from repository content; the scout rejects option-like values.
   This is a regex-based **heuristic**, not a proof of bugs. Scan only a small diff and prioritize changed code with critical effects. If no commit exists, skip the scout.
4. Form at most **three falsifiable hypotheses**, each with trigger, failure timeline, expected observation, verification command/test, and a reason to rank it.
5. Reproduce the strongest hypothesis with a minimal **local** test or a sandbox fixture. Keep recorded setup and input values safe to share. If you cannot reproduce, report `not reproduced`—never present a hypothesis as confirmed.
6. When fixes were requested: first capture the red regression test, apply the smallest targeted correction, then rerun the test (green) and related focused tests. Keep unrelated cleanup out.
7. Stop on verified fix, falsified hypotheses, unsafe environment, missing prerequisites, or time/scope limit. Provide next diagnostic question rather than repeatedly retrying.

## Output contract

- **Scope / evidence**: paths, revision, environment, tools actually run.
- **Candidate table**: hypothesis, supporting evidence, confidence, one reproduction step.
- **Reproduction**: exact command / fixture, expected vs observed, status `confirmed | not reproduced | blocked`.
- **Change summary** (only when authorized): tiny diff, regression test, verification result, remaining risk.
- **Follow-up**: one highest-value next test when unresolved.

Use the [reproduction playbook](references/reproduction-playbook.md). Use the [bug report template](assets/bug-report-template.md) for a durable report. Do not confuse this skill with `failure-mode-review`: that skill audits plausible failure modes; this skill tries to **prove or falsify a concrete regression**.
