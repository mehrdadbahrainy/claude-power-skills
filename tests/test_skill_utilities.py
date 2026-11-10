"""Local, deterministic tests of new skill helper scripts (not LLM behavioral tests)."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCOUT = ROOT / ".claude/skills/autonomous-bug-hunter/scripts/change_risk_scan.py"
INVENTORY = ROOT / ".claude/skills/legacy-code-modernizer/scripts/codebase_inventory.py"


def run(*args, cwd=None):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=False)


class BugScoutTests(unittest.TestCase):
    def test_detects_changed_line_and_signal_without_running_project(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.assertEqual(run("git", "init", "-q", str(root)).returncode, 0)
            self.assertEqual(run("git", "config", "user.email", "fixture@example.invalid", cwd=root).returncode, 0)
            self.assertEqual(run("git", "config", "user.name", "Fixture", cwd=root).returncode, 0)
            file = root / "order.cs"
            file.write_text("class Order { }\n", encoding="utf-8")
            self.assertEqual(run("git", "add", "order.cs", cwd=root).returncode, 0)
            self.assertEqual(run("git", "commit", "-q", "-m", "baseline", cwd=root).returncode, 0)
            file.write_text("class Order { void RetryPayment() { SaveChanges(); } }\n", encoding="utf-8")
            completed = run(sys.executable, str(SCOUT), "--repo", str(root), cwd=root)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            data = json.loads(completed.stdout)
            self.assertEqual(data["changed_files"], 1)
            candidate = data["candidates"][0]
            self.assertEqual(candidate["path"], "order.cs")
            self.assertIn("state_change", candidate["signals"])
            self.assertIn(1, candidate["signals"]["state_change"])
            self.assertGreater(candidate["priority_score"], 0)

    def _repo_with_baseline(self, temp, files):
        root = Path(temp)
        self.assertEqual(run("git", "init", "-q", str(root)).returncode, 0)
        run("git", "config", "user.email", "fixture@example.invalid", cwd=root)
        run("git", "config", "user.name", "Fixture", cwd=root)
        for name, text in files.items():
            (root / name).write_text(text, encoding="utf-8")
        self.assertEqual(run("git", "add", ".", cwd=root).returncode, 0)
        self.assertEqual(run("git", "commit", "-q", "-m", "baseline", cwd=root).returncode, 0)
        return root

    def _scan(self, root, *extra):
        completed = run(sys.executable, str(SCOUT), "--repo", str(root), *extra, cwd=root)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads(completed.stdout)

    def test_rejects_option_like_base_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self._repo_with_baseline(temp, {"a.cs": "class A {}\n"})
            target = root / "injected.txt"
            completed = run(sys.executable, str(SCOUT), "--repo", str(root), f"--base=--output={target}")
            self.assertNotEqual(completed.returncode, 0)
            self.assertFalse(target.exists())

    def test_reports_deleted_file_and_removed_authorization_check(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self._repo_with_baseline(temp, {
                "guard.cs": "class Guard { void Check() { Authorize(user); } }\n",
                "keep.cs": "class Keep {}\n",
            })
            (root / "guard.cs").unlink()
            data = self._scan(root)
            candidate = next(c for c in data["candidates"] if c["path"] == "guard.cs")
            self.assertTrue(candidate["deleted_file"])
            self.assertIn("authorization", candidate["removed_signals"])
            self.assertEqual(data["candidates"][0]["path"], "guard.cs")

    def test_ignores_comments_and_plain_async_await(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self._repo_with_baseline(temp, {"svc.cs": "class Svc {}\n"})
            (root / "svc.cs").write_text(
                "class Svc {\n// retry and delete everything later\nasync Task Run() { await Next(); }\n}\n",
                encoding="utf-8",
            )
            data = self._scan(root)
            self.assertEqual(data["candidates"][0]["signals"], {})
            self.assertEqual(data["candidates"][0]["priority_score"], 0)

    def test_rejects_unborn_repository_without_claiming_findings(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.assertEqual(run("git", "init", "-q", str(root)).returncode, 0)
            completed = run(sys.executable, str(SCOUT), "--repo", str(root))
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("cannot compare base revision", completed.stderr)


class InventoryTests(unittest.TestCase):
    def test_reads_project_frameworks_and_excludes_build_artifacts(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = root / "src" / "Legacy"
            project.mkdir(parents=True)
            (project / "Legacy.csproj").write_text(
                '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup>'
                '<TargetFramework>net8.0</TargetFramework></PropertyGroup>'
                '<ItemGroup><ProjectReference Include="../Shared/Shared.csproj" />'
                '</ItemGroup></Project>', encoding="utf-8"
            )
            (project / "Order.cs").write_text("public class Order {}", encoding="utf-8")
            (root / "bin").mkdir()
            (root / "bin" / "generated.cs").write_text("class Generated{}", encoding="utf-8")
            tests = root / "tests"
            tests.mkdir()
            (tests / "TestOrder.cs").write_text("class TestOrder{}", encoding="utf-8")
            completed = run(sys.executable, str(INVENTORY), "--root", str(root))
            self.assertEqual(completed.returncode, 0, completed.stderr)
            data = json.loads(completed.stdout)
            self.assertEqual(data["languages_by_file_count"]["C#"], 2)
            self.assertFalse(data["truncated_at_limit"])
            self.assertEqual(data["project_files"][0]["target_frameworks"], ["net8.0"])
            self.assertEqual(data["project_files"][0]["project_references"], 1)
            self.assertEqual(data["files_in_test_named_directories"], 1)

    def test_reports_legacy_dotnet_markers_and_singular_test_dirs(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            web = root / "src" / "Shop.Web"
            web.mkdir(parents=True)
            (web / "Shop.Web.csproj").write_text(
                '<Project ToolsVersion="15.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">'
                '<PropertyGroup><TargetFrameworkVersion>v4.7.2</TargetFrameworkVersion></PropertyGroup>'
                '</Project>', encoding="utf-8"
            )
            (web / "packages.config").write_text("<packages />", encoding="utf-8")
            (web / "Web.config").write_text("<configuration />", encoding="utf-8")
            (web / "Default.aspx").write_text("<%@ Page %>", encoding="utf-8")
            unit = root / "Shop.UnitTest"
            unit.mkdir()
            (unit / "CartTest.cs").write_text("class CartTest{}", encoding="utf-8")
            (root / "latest").mkdir()
            (root / "latest" / "note.cs").write_text("class Note{}", encoding="utf-8")
            completed = run(sys.executable, str(INVENTORY), "--root", str(root))
            self.assertEqual(completed.returncode, 0, completed.stderr)
            data = json.loads(completed.stdout)
            project = data["project_files"][0]
            self.assertFalse(project["sdk_style"])
            self.assertEqual(project["target_frameworks"], ["v4.7.2"])
            self.assertIn("packages.config", data["legacy_markers"])
            self.assertIn("web.config", data["legacy_markers"])
            self.assertEqual(data["languages_by_file_count"]["ASP.NET WebForms"], 1)
            self.assertEqual(data["files_in_test_named_directories"], 1)

    def test_limit_is_explicit(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "a.py").write_text("pass\n", encoding="utf-8")
            (root / "b.py").write_text("pass\n", encoding="utf-8")
            completed = run(sys.executable, str(INVENTORY), "--root", str(root), "--max-files", "1")
            self.assertEqual(completed.returncode, 0, completed.stderr)
            data = json.loads(completed.stdout)
            self.assertTrue(data["truncated_at_limit"])
            self.assertEqual(data["files_scanned"], 1)


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_skills", ROOT / "scripts/validate_skills.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BODY = "# Skill\n\n" + ("Inspect evidence before concluding. " * 20) + "\n"


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.validator = load_validator()

    def _skill(self, temp, frontmatter, body=BODY, name="demo-skill"):
        folder = Path(temp) / name
        folder.mkdir()
        (folder / "SKILL.md").write_text(f"---\n{frontmatter}\n---\n{body}", encoding="utf-8")
        return folder

    def test_repository_skills_pass(self):
        completed = run(sys.executable, str(ROOT / "scripts/validate_skills.py"))
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_folded_description_is_read_in_full(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = self._skill(temp, "name: demo-skill\ndescription: >\n  Short\nlicense: MIT")
            errors = self.validator.validate_skill(folder)
            self.assertTrue(any("description must be" in e for e in errors), errors)

    def test_reports_broken_asset_link_and_missing_script(self):
        with tempfile.TemporaryDirectory() as temp:
            body = BODY + "\nSee [template](assets/missing.md). Run `${CLAUDE_SKILL_DIR}/scripts/gone.py`.\n"
            folder = self._skill(temp, "name: demo-skill\ndescription: A sufficiently long description.\nlicense: MIT", body)
            errors = self.validator.validate_skill(folder)
            self.assertTrue(any("broken link assets/missing.md" in e for e in errors), errors)
            self.assertTrue(any("scripts/gone.py does not exist" in e for e in errors), errors)

    def test_rejects_non_portable_key_hardcoded_path_and_missing_license(self):
        with tempfile.TemporaryDirectory() as temp:
            body = BODY + "\nRun `python3 .claude/skills/demo-skill/scripts/x.py`.\n"
            folder = self._skill(temp, "name: demo-skill\ndescription: A sufficiently long description.\nargument-hint: x", body)
            errors = self.validator.validate_skill(folder)
            self.assertTrue(any("non-portable frontmatter key argument-hint" in e for e in errors), errors)
            self.assertTrue(any("missing required frontmatter key license" in e for e in errors), errors)
            self.assertTrue(any("hard-coded" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
