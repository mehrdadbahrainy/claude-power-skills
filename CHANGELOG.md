# Changelog

## v0.3.0 — unreleased

### Fixed
- Helper scripts are now referenced through `${CLAUDE_SKILL_DIR}` instead of a repository-relative `.claude/skills/...` path, which broke the recommended personal install in `~/.claude/skills`.
- `change_risk_scan.py`: `--base` is resolved to a commit SHA before it reaches `git diff`, so an option-like value (e.g. `--output=<file>`) can no longer make the "read-only" scout write files.
- `change_risk_scan.py`: deleted files were silently dropped (the `+++ /dev/null` branch was unreachable); they are now reported and prioritized.
- `change_risk_scan.py`: the diff was scanned twice; it is now scanned once.
- `validate_skills.py`: folded/literal YAML descriptions (`description: >`) were read as a single character and passed.

### Changed
- `change_risk_scan.py` also scans **removed** lines (`removed_signals`), so a deleted authorization or transaction check is surfaced; comment lines are skipped; plain `async`/`await` no longer counts as a concurrency signal.
- `codebase_inventory.py` reports SDK-style vs classic projects, `PackageReference` counts, legacy markers (`packages.config`, `web.config`/`app.config`, `Global.asax`, EDMX, WCF `.svc`), WebForms/Razor/SQL files, `global.json` and `Directory.*.props`; test-directory detection now covers names like `Shop.UnitTest` and `Foo.Test` without matching `latest`.
- `validate_skills.py` checks every relative link (not only `references/`), scripts referenced via `${CLAUDE_SKILL_DIR}`, hard-coded `.claude/skills/` paths, a required `license`, and frontmatter keys outside the portable Agent Skills set.
- `autonomous-bug-hunter` and `failure-mode-review` descriptions now point to each other to reduce trigger overlap.
- Both helper-bearing skills declare `license: MIT` and an `allowed-tools` rule that pre-approves only their own helper.
- CI runs on Linux, Windows and macOS with Python 3.9 and 3.12.

## v0.2.0
- Added `autonomous-bug-hunter` and `legacy-code-modernizer` with read-only helpers and tests.

## v0.1.0
- Initial seven skills, evidence checklists, validator and evaluation rubric.
