#!/usr/bin/env python3
"""Read-only, dependency-free inventory of likely modernization boundaries."""
import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET

SKIP_DIRS = {
    ".git", ".svn", ".hg", ".idea", ".vs", ".venv", "venv",
    "node_modules", "bin", "obj", "dist", "build", "coverage",
    "__pycache__", ".next", ".nuxt", "vendor",
}
LANGUAGES = {
    ".cs": "C#", ".vb": "Visual Basic", ".fs": "F#",
    ".java": "Java", ".kt": "Kotlin", ".py": "Python",
    ".js": "JavaScript", ".jsx": "JavaScript",
    ".ts": "TypeScript", ".tsx": "TypeScript",
    ".go": "Go", ".rs": "Rust", ".php": "PHP", ".rb": "Ruby",
}
PROJECT_EXTS = {".csproj", ".vbproj", ".fsproj"}
BUILD_FILES = {
    "package.json", "pom.xml", "build.gradle", "build.gradle.kts",
    "requirements.txt", "pyproject.toml", "go.mod", "Cargo.toml",
    "Dockerfile", "docker-compose.yml", "compose.yml",
}


def project_info(path, root):
    result = {"path": path.relative_to(root).as_posix(), "target_frameworks": [], "project_references": 0}
    try:
        tree = ET.parse(path)
        for element in tree.iter():
            tag = element.tag.rsplit("}", 1)[-1]
            if tag in ("TargetFramework", "TargetFrameworks", "TargetFrameworkVersion"):
                for value in (element.text or "").split(";"):
                    value = value.strip()
                    if value and value not in result["target_frameworks"]:
                        result["target_frameworks"].append(value)
            elif tag == "ProjectReference":
                result["project_references"] += 1
    except (ET.ParseError, OSError, UnicodeError) as exc:
        result["parse_warning"] = type(exc).__name__
    return result


def inventory(root, limit):
    counts = Counter()
    modules = Counter()
    projects, manifests = [], []
    files_seen = 0
    truncated = False
    test_like = 0
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not (Path(current) / d).is_symlink())
        for filename in sorted(files):
            path = Path(current) / filename
            if path.is_symlink() or not path.is_file():
                continue
            if files_seen >= limit:
                truncated = True
                break
            files_seen += 1
            rel = path.relative_to(root)
            module = rel.parts[0] if len(rel.parts) > 1 else "(root)"
            modules[module] += 1
            suffix = path.suffix.lower()
            if suffix in LANGUAGES:
                counts[LANGUAGES[suffix]] += 1
            if suffix in PROJECT_EXTS and len(projects) < 200:
                projects.append(project_info(path, root))
            if (filename in BUILD_FILES or suffix in {".sln", ".slnx"}) and len(manifests) < 200:
                manifests.append(rel.as_posix())
            if any(p.lower() in {"test", "tests", "__tests__"} or p.lower().endswith("tests") for p in rel.parts[:-1]):
                test_like += 1
        if truncated:
            break
    return {
        "root": str(root),
        "files_scanned": files_seen,
        "truncated_at_limit": truncated,
        "languages_by_file_count": dict(sorted(counts.items())),
        "top_level_areas_by_file_count": dict(sorted(modules.items(), key=lambda pair: (-pair[1], pair[0]))[:30]),
        "project_files": projects,
        "build_manifests": sorted(manifests),
        "files_in_test_named_directories": test_like,
        "limitations": [
            "File counts and names do not establish software quality or runtime behavior.",
            "Target framework values may be imported or computed from external MSBuild properties.",
            "Test counts are directory-name heuristics, not proof of coverage.",
            "Generated/ignored directories and symbolic links are excluded.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--max-files", type=int, default=30000)
    args = parser.parse_args()
    if not 1 <= args.max_files <= 200000:
        parser.error("--max-files must be between 1 and 200000")
    root = args.root.resolve()
    if not root.is_dir():
        parser.error("--root must be an accessible directory")
    try:
        print(json.dumps(inventory(root, args.max_files), indent=2))
    except (OSError, PermissionError) as exc:
        print(f"inventory failed: {exc}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
