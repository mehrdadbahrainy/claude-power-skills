# Claude Power Skills

**Nine evidence-driven, practical skills for Claude Code** — designed for people shipping real software, not for generating generic advice.

[فارسی](#راهنمای-سریع-فارسی) · [Skills](#skill-catalog) · [Install](#installation) · [Evaluation](#quality-and-evaluation)

## Why these skills?

Each skill requires Claude to inspect relevant files before drawing conclusions, separate facts from hypotheses, define testable acceptance criteria, and report what it could not verify. Skills are reusable workflows, **not** permission to make destructive changes.

## Skill catalog

| Command | Best used when | Delivers |
| --- | --- | --- |
| `/architecture-xray` | Onboarding, refactoring, design reviews | Evidence-linked system map, data flows, risks, decisions |
| `/failure-mode-review` | Reviewing high-risk changes | Concrete failure scenarios, invariants, targeted tests |
| `/query-performance-detective` | Slow endpoints, EF Core, SQL | Query hypotheses, measurement plan, minimal safe optimization |
| `/event-flow-auditor` | Outbox, queues, sagas, retries | Delivery guarantees, idempotency and replay failure analysis |
| `/agent-tool-safety` | Agents that retrieve data or invoke tools | Trust-boundary map, attack cases, guardrails, evaluation cases |
| `/contract-drift-check` | REST/event schema changes | Compatibility matrix, consumer impact, rollout plan |
| `/release-rehearsal` | Before a risky production release | Go/no-go checks, rollback and verification playbook |
| `/autonomous-bug-hunter` | Bug reproduction and narrow regression fixes | Hypothesis loop, local diff scout, reproducible test |
| `/legacy-code-modernizer` | Incremental modernization of existing systems | Read-only code inventory, preservation contract, thin migration slice |

All skill prompts are written in English for portability. They work with any repository; several contain .NET/EF Core and event-driven examples.

## Installation

### Personal installation (available across projects)

Clone or download this repository, then copy its skill directories:

**macOS / Linux**
```bash
mkdir -p ~/.claude/skills
cp -R .claude/skills/* ~/.claude/skills/
```

**PowerShell**
```powershell
New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
Copy-Item -Recurse -Force .claude\skills\* "$HOME\.claude\skills\"
```

### One project only

Copy the folders from `.claude/skills/` into `<your-project>/.claude/skills/`. Keep this repository itself cloned when you want to maintain the collection: Claude Code also loads these skills when used in **this** repository.

> Do not clone this repository *inside* a production codebase and expect a nested `.claude` folder to be globally loaded. Copy or symlink each skill into the supported location.

## Usage examples

```text
/architecture-xray Map checkout, inventory, and their message flows. Cite files.
/failure-mode-review Review my last commit for failure paths and missing tests.
/query-performance-detective Investigate why the product search endpoint is slow.
/event-flow-auditor Audit the OrderPlaced consumer for duplicate deliveries.
/agent-tool-safety Threat-model the product-search and order-creation agent tools.
/contract-drift-check Compare our proposed DTO/event changes to the current main branch.
/release-rehearsal Prepare a release plan for this migration and API rollout.
/autonomous-bug-hunter Reproduce a regression introduced by my latest change.
/legacy-code-modernizer Plan a safe first slice for migrating this legacy .NET application.
```

Claude may also select a skill automatically if your request matches its description. Use `/skill-name` to invoke a specific workflow. No extra packages, MCP servers, secrets, or hooks are required by these skills. Two skills include optional Python 3 standard-library helpers; the bug scout additionally requires a local Git executable.

## Operating principles

1. **Evidence first:** cite paths and line ranges, or identify where evidence is missing.
2. **No imaginary execution:** label commands, tests, and measurements as *proposed* unless actually run.
3. **Safe by default:** don't modify production data, call live systems, deploy, or perform destructive actions without explicit user permission.
4. **Smallest useful next step:** give prioritized remediation and verification, not an overwhelming wishlist.
5. **Human control:** distinguish review-only work from requested implementation; ask approval before risky changes.

## Quality and evaluation

Run the dependency-free structural validator:

```bash
python3 scripts/validate_skills.py
python3 -m unittest discover -s tests -v
```

Read [EVALS.md](EVALS.md) for scenario prompts and success criteria. The CI workflow validates structure, **not** model behavior: you still need to run scenario evaluations with Claude Code on representative projects.

## Executable, read-only helpers

Two skills bundle Python 3 standard-library helpers. Skills reference them through `${CLAUDE_SKILL_DIR}`, which Claude Code expands to the skill's own folder, so the helpers work for both personal (`~/.claude/skills`) and per-project installs. Each skill's `allowed-tools` pre-approves only its own helper.

- `/autonomous-bug-hunter` runs `python3 ${CLAUDE_SKILL_DIR}/scripts/change_risk_scan.py --repo . --base HEAD` to prioritize changed lines for manual review — including deleted files and removed authorization/transaction code. `--base` is resolved to a commit SHA before use, so option-like values are rejected. It does not run the application or prove bugs.
- `/legacy-code-modernizer` runs `python3 ${CLAUDE_SKILL_DIR}/scripts/codebase_inventory.py --root .` to inventory project files, language mix, target frameworks, SDK-style vs classic projects, package references and legacy .NET markers (`packages.config`, `web.config`, WebForms, EDMX, WCF). It does not upgrade code.
- Deterministic helper tests run in GitHub Actions on Linux, Windows and macOS, separate from the manual Claude Code evaluations in EVALS.md.

See [CHANGELOG.md](CHANGELOG.md) for release notes.

## راهنمای سریع فارسی

این مخزن شامل ۹ مهارت (Skill) برای Claude Code است. هر Skill یک فایل `SKILL.md` دارد و با دستور `/<name>` اجرا می‌شود؛ Claude هم اگر درخواست شما با توضیح یک Skill جور باشد، خودش آن را انتخاب می‌کند.

| دستور | کاربرد |
| --- | --- |
| `/architecture-xray` | نقشه‌ی معماری واقعی سیستم با ارجاع به فایل‌ها |
| `/failure-mode-review` | بررسی یک diff قبل از merge با سناریوهای خرابی مشخص |
| `/query-performance-detective` | عیب‌یابی کندی SQL و EF Core بر پایه‌ی اندازه‌گیری |
| `/event-flow-auditor` | بررسی صف‌ها، Outbox، Saga، تکرار و idempotency |
| `/agent-tool-safety` | مدل‌سازی تهدید برای Agentهایی که ابزار صدا می‌زنند |
| `/contract-drift-check` | سازگاری قرارداد API و رویدادها بین نسخه‌ها |
| `/release-rehearsal` | آمادگی انتشار، تصمیم go/no-go و برنامه‌ی بازگشت |
| `/autonomous-bug-hunter` | بازتولید و اصلاح یک باگ مشخص با تست حداقلی |
| `/legacy-code-modernizer` | مدرن‌سازی تدریجی و کم‌ریسک کد قدیمی |

**نصب سراسری:** پوشه‌های داخل `.claude/skills/` را در `~/.claude/skills/` کپی کنید. اسکریپت‌های کمکی با `${CLAUDE_SKILL_DIR}` آدرس‌دهی شده‌اند و در هر دو حالت نصب (سراسری یا داخل یک پروژه) کار می‌کنند.

**بررسی ساختار:** `python3 scripts/validate_skills.py` و `python3 -m unittest discover -s tests -v`. این‌ها فقط ساختار را می‌سنجند، نه کیفیت پاسخ مدل؛ برای آن [EVALS.md](EVALS.md) را ببینید.

## Reference

- [Claude Code skills guide](https://code.claude.com/docs/en/skills)
- [Open Agent Skills specification](https://agentskills.io/specification)

## License

MIT — see [LICENSE](LICENSE). This is an independent, community-created collection; it is not affiliated with or endorsed by Anthropic.
