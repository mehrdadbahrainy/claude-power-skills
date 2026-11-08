# Contributing

Add skills that turn a recurring engineering task into a repeatable, testable workflow.

## Checklist

- Place a skill in `.claude/skills/<kebab-case-name>/SKILL.md`.
- Provide standards-compliant YAML frontmatter with `name` matching its folder and a specific `description` saying **what** it does and **when** to invoke it.
- State inputs, a bounded workflow, evidence requirements, output format, and what to do if tools/files are unavailable.
- Distinguish observation, hypothesis, and recommendation. Avoid unjustified confidence and auto-destructive actions.
- Use relative links for optional `references/` and keep main files focused.
- Include at least two realistic evaluation prompts and expected outcomes in `EVALS.md`.
- Run `python3 scripts/validate_skills.py` and, where possible, exercise the skill on a representative repository.
- Don't add secrets, private code, tokens, internal endpoints, or production data to fixtures.

## Review questions

Does this workflow produce a useful artifact? Can an engineer verify its assertions? Would it work on a repo with little documentation or no test runner? Is the trigger distinct from other skills? Can it be invoked without granting surprising permissions?
