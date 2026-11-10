#!/usr/bin/env python3
"""Dependency-free structural validation for this repository's SKILL.md files.

This does not evaluate skill usefulness or model behavior. For full YAML parsing,
use an Agent Skills reference validator as well.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / '.claude' / 'skills'
NAME_RE = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
# Fields accepted by the open Agent Skills specification. Claude Code accepts more
# (argument-hint, disable-model-invocation, ...), but those make claude.ai / Skills API
# uploads fail, and this collection promises portability.
PORTABLE_KEYS = {'name', 'description', 'license', 'compatibility', 'metadata', 'allowed-tools'}
REQUIRED_KEYS = {'name', 'description', 'license'}
BLOCK_SCALAR = re.compile(r'^[|>][+-]?$')
LINK_RE = re.compile(r'\]\(([^)\s]+)\)')
SKILL_DIR_PATH_RE = re.compile(r'\$\{CLAUDE_SKILL_DIR\}/([\w./-]+)')
HARDCODED_PATH_RE = re.compile(r'\.claude/skills/[\w-]+/')


def parse_frontmatter(text):
    """Parse the flat subset of YAML used in SKILL.md frontmatter.

    Supports `key: value`, quoted values, `|`/`>` block scalars and indented
    continuation lines (used by `metadata` mappings and folded descriptions).
    Returns (metadata, problems).
    """
    metadata, problems = {}, []
    key = None
    block = False
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        if line[0] in ' \t':
            if key is None:
                problems.append(f'indented line without a key: {line!r}')
            elif block or isinstance(metadata[key], str):
                joiner = ' ' if metadata[key] else ''
                metadata[key] = (metadata[key] + joiner + line.strip()).strip()
            continue
        if ':' not in line:
            problems.append(f'malformed frontmatter line {line!r}')
            key = None
            continue
        key, value = (part.strip() for part in line.split(':', 1))
        if key in metadata:
            problems.append(f'duplicate frontmatter key {key}')
        block = bool(BLOCK_SCALAR.match(value))
        if block:
            value = ''
        elif len(value) >= 2 and value[0] == value[-1] and value[0] in '"\'':
            value = value[1:-1]
        metadata[key] = value
    return metadata, problems


def is_local_link(target):
    return not re.match(r'^[a-z][a-z0-9+.-]*:', target, re.I) and not target.startswith('#')


def validate_skill(folder):
    errors = []
    path = folder / 'SKILL.md'
    if not path.exists():
        return [f'{folder.name}: missing SKILL.md']
    content = path.read_text(encoding='utf-8')
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return [f'{folder.name}: missing YAML frontmatter']
    metadata, problems = parse_frontmatter(match.group(1))
    errors += [f'{folder.name}: {p}' for p in problems]

    name = metadata.get('name', '')
    desc = metadata.get('description', '')
    if name != folder.name or not NAME_RE.fullmatch(name) or len(name) > 64:
        errors.append(f'{folder.name}: name must match folder and use kebab-case (max 64)')
    if not 20 <= len(desc) <= 1024:
        errors.append(f'{folder.name}: description must be 20-1024 characters (found {len(desc)})')
    for key in sorted(REQUIRED_KEYS - metadata.keys()):
        errors.append(f'{folder.name}: missing required frontmatter key {key}')
    for key in sorted(metadata.keys() - PORTABLE_KEYS):
        errors.append(f'{folder.name}: non-portable frontmatter key {key} (breaks claude.ai/API upload)')

    body = content[match.end():]
    if len(body.strip()) < 400:
        errors.append(f'{folder.name}: instructions look too short')
    for target in LINK_RE.findall(body):
        target = target.split('#', 1)[0]
        if target and is_local_link(target) and not (folder / target).resolve().is_file():
            errors.append(f'{folder.name}: broken link {target}')
    referenced = SKILL_DIR_PATH_RE.findall(body) + SKILL_DIR_PATH_RE.findall(metadata.get('allowed-tools', ''))
    for target in referenced:
        if not (folder / target).is_file():
            errors.append(f'{folder.name}: ${{CLAUDE_SKILL_DIR}}/{target} does not exist')
    if HARDCODED_PATH_RE.search(body):
        errors.append(f'{folder.name}: hard-coded .claude/skills/ path; use ${{CLAUDE_SKILL_DIR}} so personal installs work')
    return errors


def main():
    errors = []
    if not SKILLS.is_dir():
        errors.append('Missing .claude/skills directory')
    else:
        folders = sorted(path for path in SKILLS.iterdir() if path.is_dir())
        if not folders:
            errors.append('No skills found')
        for folder in folders:
            errors += validate_skill(folder)
            print(f'checked {folder.name}')
    if errors:
        for error in errors:
            print('ERROR:', error, file=sys.stderr)
        return 1
    print('All skill structures passed. Behavioral evaluation is still required.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
