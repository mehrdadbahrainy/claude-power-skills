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
errors = []

if not SKILLS.is_dir():
    errors.append('Missing .claude/skills directory')
else:
    folders = sorted(path for path in SKILLS.iterdir() if path.is_dir())
    if not folders:
        errors.append('No skills found')
    for folder in folders:
        path = folder / 'SKILL.md'
        if not path.exists():
            errors.append(f'{folder.name}: missing SKILL.md')
            continue
        content = path.read_text(encoding='utf-8')
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not match:
            errors.append(f'{folder.name}: missing YAML frontmatter')
            continue
        metadata = {}
        for line in match.group(1).splitlines():
            if not line.strip() or line.lstrip().startswith('#'):
                continue
            if ':' not in line:
                errors.append(f'{folder.name}: malformed frontmatter line {line!r}')
                continue
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key in metadata:
                errors.append(f'{folder.name}: duplicate frontmatter key {key}')
            metadata[key] = value
        name = metadata.get('name', '')
        desc = metadata.get('description', '')
        if name != folder.name or not NAME_RE.fullmatch(name) or len(name) > 64:
            errors.append(f'{folder.name}: name must match folder and use kebab-case (max 64)')
        if not 1 <= len(desc) <= 1024:
            errors.append(f'{folder.name}: description must be 1-1024 characters')
        body = content[match.end():]
        if len(body.strip()) < 400:
            errors.append(f'{folder.name}: instructions look too short')
        for link in re.findall(r'\]\((references/[^)#]+)\)', body):
            if not (folder / link).is_file():
                errors.append(f'{folder.name}: broken reference {link}')
        print(f'checked {folder.name}')

if errors:
    for error in errors:
        print('ERROR:', error, file=sys.stderr)
    sys.exit(1)
print('All skill structures passed. Behavioral evaluation is still required.')
