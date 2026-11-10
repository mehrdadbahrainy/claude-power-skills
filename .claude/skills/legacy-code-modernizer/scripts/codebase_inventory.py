#!/usr/bin/env python3
"""Read-only, dependency-free inventory of likely modernization boundaries."""
import argparse
import json
import os
import re
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
    ".aspx": "ASP.NET WebForms", ".ascx": "ASP.NET WebForms", ".asmx": "ASP.NET WebForms",
    ".cshtml": "Razor", ".vbhtml": "Razor", ".sql": "SQL",
}
PROJECT_EXTS = {".csproj", ".vbproj", ".fsproj"}
BUILD_FILES = {
    "package.json", "pom.xml", "build.gradle", "build.gradle.kts",
    "requirements.txt", "pyproject.toml", "go.mod", "Cargo.toml",
    "Dockerfile", "docker-compose.yml", "compose.yml",
    "global.json", "directory.build.props", "directory.packages.props", "nuget.config",
}
# Files that usually indicate classic .NET Framework-era technology (matched case-insensitively).
LEGACY_MARKER_NAMES = {"packages.config", "web.config", "app.config", "global.asax"}
LEGACY_MARKER_EXTS = {".edmx": "Entity Framework EDMX model", ".svc": "WCF service endpoint"}
BUILD_FILES_LOWER = {name.lower() for name in BUILD_FILES}
TEST_DIR = re.compile(r"((^|[._\-]|unit|integration|functional|acceptance)tests?|__tests__)$", re.I)


def project_info(path, root):
    result = {
        "path": path.relative_to(root).as_posix(),
        "sdk_style": False,
        "target_frameworks": [],
        "project_references": 0,
        "package_references": 0,
    }
    try:
        tree = ET.parse(path)
        result["sdk_style"] = "Sdk" in tree.getroot().attrib
        for element in tree.iter():
            tag = element.tag.rsplit("}", 1)[-1]
            if tag in ("TargetFramework", "TargetFrameworks", "TargetFrameworkVersion"):
                for value in (element.text or "").split(";"):
                    value = value.strip()
                    if value and value not in result["target_frameworks"]:
                        result["target_frameworks"].append(value)
            elif tag == "ProjectReference":
                result["project_references"] += 1
            elif tag == "PackageReference":
                result["package_references"] += 1
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
    legacy = defaultdict(list)
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
            lower = filename.lower()
            if (lower in BUILD_FILES_LOWER or suffix in {".sln", ".slnx"}) and len(manifests) < 200:
                manifests.append(rel.as_posix())
            if lower in LEGACY_MARKER_NAMES:
                legacy[lower].append(rel.as_posix())
            elif suffix in LEGACY_MARKER_EXTS:
                legacy[LEGACY_MARKER_EXTS[suffix]].append(rel.as_posix())
            if any(TEST_DIR.search(p) for p in rel.parts[:-1]):
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
        "legacy_markers": {
            name: {"count": len(paths), "examples": sorted(paths)[:10]}
            for name, paths in sorted(legacy.items())
        },
        "limitations": [
            "Legacy markers are file-name signals; a web.config or packages.config can also exist in a modernized app.",
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
