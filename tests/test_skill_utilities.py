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


if __name__ == "__main__":
    unittest.main()
