#!/usr/bin/env python3
"""Read-only Git diff triage; lexical risk signals are NOT bug findings."""
import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

# Patterns match only added lines. Deliberately broad: manual verification required.
SIGNALS = {
    "authorization": (4, re.compile(r"\b(auth|authoriz\w*|permission|tenant|claim\w*|role)\b", re.I)),
    "state_change": (3, re.compile(r"\b(savechanges|commit|rollback|delete|insert|update|transaction|execute)\b", re.I)),
    "retry_or_delivery": (3, re.compile(r"\b(retry|redeliver|outbox|publish|acknowledge|idempot\w*)\b", re.I)),
    "concurrency": (3, re.compile(r"\b(lock|semaphore|parallel|concurrent|interlocked|async|await)\b", re.I)),
    "external_effect": (2, re.compile(r"\b(httpclient|webhook|payment|charge|sendasync|externalapi)\b", re.I)),
    "schema_change": (3, re.compile(r"\b(migrat\w*|alter table|drop table|drop column|schema)\b", re.I)),
}
HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=False
    )


def scan(diff):
    results = defaultdict(lambda: {"added_lines": 0, "removed_lines": 0, "signals": defaultdict(list)})
    current = None
    old_path = None
    lineno = 0
    for raw in diff.splitlines():
        if raw.startswith("diff --git "):
            current, old_path = None, None
        elif raw.startswith("--- a/"):
            old_path = raw[6:]
        elif raw.startswith("+++ b/"):
            current = raw[6:]
            if current == "/dev/null":
                current = old_path
            if current:
                _ = results[current]
        else:
            match = HUNK.match(raw)
            if match:
                lineno = int(match.group(1))
            elif current and raw.startswith("+") and not raw.startswith("+++"):
                results[current]["added_lines"] += 1
                for name, (_, pattern) in SIGNALS.items():
                    if pattern.search(raw[1:]) and len(results[current]["signals"][name]) < 8:
                        results[current]["signals"][name].append(lineno)
                lineno += 1
            elif current and raw.startswith("-") and not raw.startswith("---"):
                results[current]["removed_lines"] += 1
            elif current and raw.startswith(" "):
                lineno += 1
    candidates = []
    for path, info in results.items():
        signals = {k: v for k, v in sorted(info["signals"].items()) if v}
        score = sum(SIGNALS[k][0] for k in signals)
        candidates.append({
            "path": path,
            "added_lines": info["added_lines"],
            "removed_lines": info["removed_lines"],
            "priority_score": score,
            "signals": signals,
        })
    return sorted(candidates, key=lambda x: (-x["priority_score"], x["path"]))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", type=Path, default=Path("."), help="Git worktree")
    p.add_argument("--base", default="HEAD", help="Git revision to compare with current worktree")
    p.add_argument("--max-bytes", type=int, default=2_000_000)
    args = p.parse_args()
    if args.max_bytes < 1024 or args.max_bytes > 20_000_000:
        p.error("--max-bytes must be between 1024 and 20000000")
    root = args.repo.resolve()
    check = git(root, "rev-parse", "--show-toplevel")
    if check.returncode:
        p.error("not an accessible Git repository")
    # No shell, no external command supplied by user, no file writes.
    diff = git(root, "diff", "--no-ext-diff", "--no-textconv", "--unified=0", args.base, "--")
    if diff.returncode:
        p.error("cannot compare base revision; check --base and repository state")
    if len(diff.stdout.encode("utf-8")) > args.max_bytes:
        p.error("diff is too large; narrow the scope before analysis")
    untracked = git(root, "ls-files", "--others", "--exclude-standard")
    skipped = len(untracked.stdout.splitlines()) if untracked.returncode == 0 else None
    print(json.dumps({
        "base": args.base,
        "changed_files": len(scan(diff.stdout)),
        "candidates": scan(diff.stdout),
        "untracked_files_not_scanned": skipped,
        "limitations": [
            "Heuristic matches do not prove defects.",
            "Only tracked worktree changes relative to base are inspected.",
            "Deletions and changes in untracked files require separate manual review.",
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
