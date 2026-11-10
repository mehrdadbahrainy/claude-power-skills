#!/usr/bin/env python3
"""Read-only Git diff triage; lexical risk signals are NOT bug findings."""
import argparse
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path

# Patterns match added and removed code lines. Deliberately broad: manual verification required.
SIGNALS = {
    "authorization": (4, re.compile(r"\b(auth|authoriz\w*|permission\w*|tenant\w*|claim\w*|role\w*)\b", re.I)),
    "state_change": (3, re.compile(r"\b(savechanges\w*|commit|rollback|delete|insert|update|transaction\w*|execute\w*)\b", re.I)),
    "retry_or_delivery": (3, re.compile(r"\b(retry\w*|redeliver\w*|outbox|publish\w*|acknowledge\w*|idempot\w*)\b", re.I)),
    # async/await are deliberately excluded: they appear on almost every line of modern C#/JS code.
    "concurrency": (3, re.compile(r"\b(lock|semaphore\w*|mutex|parallel|concurrent\w*|interlocked|volatile|whenall|threadpool)\b", re.I)),
    "external_effect": (2, re.compile(r"\b(httpclient|webhook\w*|payment\w*|charge\w*|sendasync|externalapi)\b", re.I)),
    "schema_change": (3, re.compile(r"\b(migrat\w*|alter table|drop table|drop column|schema)\b", re.I)),
}
DELETED_FILE_WEIGHT = 3
MAX_LINES_PER_SIGNAL = 8
HUNK = re.compile(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@")
COMMENT = re.compile(r"^\s*(//|#|/\*|\*|--|')")


def git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), "-c", "core.quotePath=false", *args],
        capture_output=True, text=True, check=False,
    )


def diff_path(header):
    """Return the path from a '--- a/x' or '+++ b/x' header, or None for /dev/null."""
    value = header[4:].strip()
    if value.startswith('"') and value.endswith('"'):
        value = value[1:-1].encode("utf-8").decode("unicode_escape").encode("latin-1").decode("utf-8")
    if value == "/dev/null":
        return None
    return value[2:] if value[:2] in ("a/", "b/") else value


def new_entry():
    return {
        "added_lines": 0,
        "removed_lines": 0,
        "deleted_file": False,
        "signals": defaultdict(list),
        "removed_signals": defaultdict(list),
    }


def record(bucket, text, lineno):
    if COMMENT.match(text):
        return
    for name, (_, pattern) in SIGNALS.items():
        if pattern.search(text) and len(bucket[name]) < MAX_LINES_PER_SIGNAL:
            bucket[name].append(lineno)


def scan(diff):
    results = defaultdict(new_entry)
    current = old_path = None
    old_line = new_line = 0
    for raw in diff.splitlines():
        if raw.startswith("diff --git "):
            current = old_path = None
        elif raw.startswith("--- "):
            old_path = diff_path(raw)
        elif raw.startswith("+++ "):
            new_path = diff_path(raw)
            current = new_path or old_path
            if current:
                results[current]["deleted_file"] = new_path is None
        elif current is None:
            continue
        elif (match := HUNK.match(raw)):
            old_line, new_line = int(match.group(1)), int(match.group(2))
        elif raw.startswith("+"):
            results[current]["added_lines"] += 1
            record(results[current]["signals"], raw[1:], new_line)
            new_line += 1
        elif raw.startswith("-"):
            results[current]["removed_lines"] += 1
            record(results[current]["removed_signals"], raw[1:], old_line)
            old_line += 1

    candidates = []
    for path, info in results.items():
        signals = {k: v for k, v in sorted(info["signals"].items()) if v}
        removed = {k: v for k, v in sorted(info["removed_signals"].items()) if v}
        score = sum(SIGNALS[k][0] for k in set(signals) | set(removed))
        if info["deleted_file"]:
            score += DELETED_FILE_WEIGHT
        candidates.append({
            "path": path,
            "deleted_file": info["deleted_file"],
            "added_lines": info["added_lines"],
            "removed_lines": info["removed_lines"],
            "priority_score": score,
            "signals": signals,
            "removed_signals": removed,
        })
    return sorted(candidates, key=lambda x: (-x["priority_score"], x["path"]))


def resolve_base(root, base):
    """Resolve --base to a commit SHA so it can never be interpreted as a git option."""
    if not base or base.startswith("-"):
        return None
    resolved = git(root, "rev-parse", "--verify", "--quiet", f"{base}^{{commit}}")
    sha = resolved.stdout.strip()
    if resolved.returncode or not re.fullmatch(r"[0-9a-f]{40,64}", sha):
        return None
    return sha


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
    sha = resolve_base(root, args.base)
    if sha is None:
        p.error("cannot compare base revision; check --base and repository state")
    # No shell, no option-like user input reaches git, no file writes.
    diff = git(root, "diff", "--no-ext-diff", "--no-textconv", "--no-color", "--unified=0", sha, "--")
    if diff.returncode:
        p.error("cannot compare base revision; check --base and repository state")
    if len(diff.stdout.encode("utf-8")) > args.max_bytes:
        p.error("diff is too large; narrow the scope before analysis")
    untracked = git(root, "ls-files", "--others", "--exclude-standard")
    skipped = len(untracked.stdout.splitlines()) if untracked.returncode == 0 else None
    candidates = scan(diff.stdout)
    print(json.dumps({
        "base": args.base,
        "base_commit": sha,
        "changed_files": len(candidates),
        "candidates": candidates,
        "untracked_files_not_scanned": skipped,
        "limitations": [
            "Heuristic matches do not prove defects.",
            "Only tracked worktree changes relative to base are inspected.",
            "removed_signals line numbers refer to the base revision; signals refer to the worktree.",
            "Comment lines are skipped; string literals and identifiers can still cause false positives.",
            "Untracked files require separate manual review.",
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
