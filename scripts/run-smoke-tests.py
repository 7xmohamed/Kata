#!/usr/bin/env python3
import os
import re
import sys
import shutil
import tempfile
import unittest
import subprocess
from pathlib import Path

# Find repo root
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = (SCRIPT_DIR / "..").resolve()

# Helper to find executable
BASH_PATH = shutil.which("bash")
JQ_PATH = shutil.which("jq")
CURL_PATH = shutil.which("curl")
GIT_PATH = shutil.which("git")


def setUpModule():
    # Convert all .sh files to LF line endings on Windows to prevent syntax errors in bash
    scripts = [
        "scripts/statusline.sh",
        "skills/health/scripts/collect-data.sh",
        "skills/read/scripts/fetch.sh",
        "scripts/setup-statusline.sh",
        "skills/check/scripts/run-tests.sh"
    ]
    for rel_path in scripts:
        path = ROOT_DIR / rel_path
        if path.exists():
            try:
                content = path.read_bytes()
                lf_content = content.replace(b"\r\n", b"\n")
                if lf_content != content:
                    path.write_bytes(lf_content)
            except Exception:
                pass


def get_posix_path(path: Path) -> str:
    if not BASH_PATH:
        return path.as_posix()
    # Check if wslpath is available inside bash to translate Windows paths to POSIX paths
    res = subprocess.run(
        [BASH_PATH, "-c", f'wslpath -u "{path.as_posix()}"'],
        capture_output=True,
        encoding="utf-8"
    )
    if res.returncode == 0:
        return res.stdout.strip()
    
    # Fallback path translation for WSL/MSYS
    p = str(path)
    if len(p) >= 2 and p[1] == ':':
        drive = p[0].lower()
        rest = p[2:].replace('\\', '/')
        return f"/mnt/{drive}{rest}"
    return path.as_posix()


class TestVerifySkills(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_dir = Path(self.temp_dir.name) / "repo"
        # Copy minimal directories to speed up test execution and avoid copying .git/node_modules/etc
        shutil.copytree(
            ROOT_DIR,
            self.repo_dir,
            ignore=shutil.ignore_patterns(
                ".git",
                ".pytest_cache",
                "__pycache__",
                "node_modules",
                ".venv",
                "venv"
            )
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def run_verify(self, extra_args=None) -> subprocess.CompletedProcess:
        cmd = [sys.executable, str(self.repo_dir / "scripts" / "verify-skills.py")]
        if extra_args:
            cmd.extend(extra_args)
        return subprocess.run(
            cmd,
            cwd=str(self.repo_dir),
            capture_output=True,
            encoding="utf-8"
        )

    def test_clean_repo(self) -> None:
        result = self.run_verify()
        self.assertEqual(result.returncode, 0, f"Clean repo verification failed:\nstdout: {result.stdout}\nstderr: {result.stderr}")

    def test_missing_frontmatter(self) -> None:
        skill_file = self.repo_dir / "skills" / "check" / "SKILL.md"
        content = skill_file.read_text(encoding="utf-8")
        # Remove first '---'
        content = content.replace("---\n", "", 1)
        skill_file.write_text(content, encoding="utf-8")

        result = self.run_verify()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("INVALID FRONTMATTER", result.stderr)

    def test_marketplace_only_entries(self) -> None:
        market_file = self.repo_dir / ".gemini-plugin" / "marketplace.json"
        data = json_load_file(market_file)
        data["plugins"].append({
            "name": "ghost",
            "description": "x",
            "version": "1.0.0",
            "category": "development",
            "source": "./skills/ghost",
            "homepage": "https://example.com"
        })
        json_write_file(market_file, data)

        result = self.run_verify()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("MISSING SKILL DIRECTORY: ghost", result.stderr)

    def test_wrong_source_paths(self) -> None:
        market_file = self.repo_dir / ".gemini-plugin" / "marketplace.json"
        data = json_load_file(market_file)
        for entry in data["plugins"]:
            if entry["name"] == "check":
                entry["source"] = "./skills/read"
        json_write_file(market_file, data)

        result = self.run_verify()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("WRONG SOURCE: check", result.stderr)


@unittest.skipIf(not BASH_PATH or not JQ_PATH, "bash or jq is not available")
class TestStatusline(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_smoke_statusline(self) -> None:
        json1 = '{"context_window":{"current_usage":{"input_tokens":10},"context_window_size":100},"rate_limits":{"five_hour":{"used_percentage":12,"resets_at":2000000000},"seven_day":{"used_percentage":34,"resets_at":2000003600}}}'
        json2 = '{"context_window":{"current_usage":{"input_tokens":20},"context_window_size":100}}'

        # Set HOME to self.tmp_path so that the cache is created there.
        env = os.environ.copy()
        tmp_path_posix = get_posix_path(self.tmp_path)

        script_path = "scripts/statusline.sh"

        # Run 1: with rate limits
        p1 = subprocess.run(
            [BASH_PATH, "-c", f'export HOME="{tmp_path_posix}"; exec {script_path}'],
            cwd=str(ROOT_DIR),
            input=json1,
            env=env,
            capture_output=True,
            encoding="utf-8"
        )
        self.assertEqual(p1.returncode, 0, f"Run 1 failed: {p1.stderr}")

        # Run 2: without rate limits (should read cached values)
        p2 = subprocess.run(
            [BASH_PATH, "-c", f'export HOME="{tmp_path_posix}"; exec {script_path}'],
            cwd=str(ROOT_DIR),
            input=json2,
            env=env,
            capture_output=True,
            encoding="utf-8"
        )
        self.assertEqual(p2.returncode, 0, f"Run 2 failed: {p2.stderr}")

        # Run 3: run again to check different cache state
        p3 = subprocess.run(
            [BASH_PATH, "-c", f'export HOME="{tmp_path_posix}"; exec {script_path}'],
            cwd=str(ROOT_DIR),
            input=json2,
            env=env,
            capture_output=True,
            encoding="utf-8"
        )
        self.assertEqual(p3.returncode, 0, f"Run 3 failed: {p3.stderr}")

        cache_file = self.tmp_path / ".cache" / "kata-statusline" / "last.json"
        self.assertTrue(cache_file.exists(), "Cache file last.json was not created")

        cache_content = cache_file.read_text(encoding="utf-8")
        self.assertIn('"used_percentage": 12', cache_content)

        self.assertIn("5h:", p2.stdout)
        self.assertIn("7d:", p2.stdout)
        self.assertIn("12%", p2.stdout)
        self.assertIn("34%", p3.stdout)


@unittest.skipIf(os.name == "nt" or not BASH_PATH or not JQ_PATH or not CURL_PATH,
                 "Skipping installer test: not supported on Windows/without required tools")
class TestStatuslineInstaller(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.temp_dir.name)
        self.home_dir = self.tmp_path / "home"
        self.bin_dir = self.tmp_path / "bin"
        self.home_dir.mkdir()
        self.bin_dir.mkdir()

        # Create symlinks/mocks in bin_dir
        for tool in ["python3", "jq", "chmod", "mkdir"]:
            p = shutil.which(tool)
            if p:
                os.symlink(p, str(self.bin_dir / tool))

        # Write mock curl
        curl_mock = self.bin_dir / "curl"
        curl_mock.write_text(
            "#!/bin/bash\n"
            'outfile=""\n'
            'while [ "$#" -gt 0 ]; do\n'
            '  if [ "$1" = "-o" ]; then outfile="$2"; shift 2; else shift; fi\n'
            "done\n"
            'printf "%s\\n" "#!/bin/bash" "echo statusline" > "$outfile"\n',
            encoding="utf-8"
        )
        curl_mock.chmod(0o755)

        # Write mock brew
        brew_mock = self.bin_dir / "brew"
        brew_mock.write_text(
            "#!/bin/bash\n"
            'echo "brew should not be called" >&2\n'
            'echo "$*" >>"$BREW_LOG"\n'
            "exit 99\n",
            encoding="utf-8"
        )
        brew_mock.chmod(0o755)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_installer_invalid_json(self) -> None:
        gemini_dir = self.home_dir / ".gemini"
        gemini_dir.mkdir(parents=True, exist_ok=True)
        settings_file = gemini_dir / "settings.json"
        settings_file.write_text("{invalid json", encoding="utf-8")

        env = os.environ.copy()
        env["PATH"] = f"{self.bin_dir}{os.pathsep}{env.get('PATH', '')}"
        env["HOME"] = str(self.home_dir)
        env["BREW_LOG"] = str(self.tmp_path / "brew.log")

        script_path = (ROOT_DIR / "scripts" / "setup-statusline.sh").as_posix()
        p = subprocess.run(
            [BASH_PATH, script_path],
            env=env,
            capture_output=True,
            encoding="utf-8"
        )
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("Refusing to modify it", p.stderr)
        self.assertEqual(settings_file.read_text(encoding="utf-8"), "{invalid json")
        self.assertFalse((self.tmp_path / "brew.log").exists())

    def test_installer_valid_json(self) -> None:
        gemini_dir = self.home_dir / ".gemini"
        gemini_dir.mkdir(parents=True, exist_ok=True)
        settings_file = gemini_dir / "settings.json"
        settings_file.write_text('{"theme":"dark"}', encoding="utf-8")

        env = os.environ.copy()
        env["PATH"] = f"{self.bin_dir}{os.pathsep}{env.get('PATH', '')}"
        env["HOME"] = str(self.home_dir)
        env["BREW_LOG"] = str(self.tmp_path / "brew.log")

        script_path = (ROOT_DIR / "scripts" / "setup-statusline.sh").as_posix()
        p = subprocess.run(
            [BASH_PATH, script_path],
            env=env,
            capture_output=True,
            encoding="utf-8"
        )
        self.assertEqual(p.returncode, 0, f"Installer failed: stdout: {p.stdout}\nstderr: {p.stderr}")

        # Validate that settings.json was modified correctly
        with open(settings_file, "r", encoding="utf-8") as f:
            data = json_load_data(f.read())
        self.assertEqual(data["theme"], "dark")
        self.assertEqual(data["statusLine"]["command"], "bash ~/.gemini/statusline.sh")

        statusline_dest = gemini_dir / "statusline.sh"
        self.assertTrue(statusline_dest.exists())
        self.assertTrue(os.access(statusline_dest, os.X_OK))
        self.assertFalse((self.tmp_path / "brew.log").exists())


@unittest.skipIf(not BASH_PATH, "bash is not available")
class TestHealth(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_smoke_health(self) -> None:
        # Query bash directly to calculate the exact PROJECT_KEY that collect-data.sh will use
        res = subprocess.run(
            [BASH_PATH, "-c", 'printf "%s" "$(pwd)" | sed "s|[/_]|-|g; s|^-||"'],
            cwd=str(ROOT_DIR),
            capture_output=True,
            encoding="utf-8"
        )
        self.assertEqual(res.returncode, 0, f"Failed to compute PROJECT_KEY via bash:\nstderr: {res.stderr}")
        project_key = res.stdout.strip()

        convo_dir = self.tmp_path / ".gemini" / "projects" / f"-{project_key}"
        convo_dir.mkdir(parents=True, exist_ok=True)

        (convo_dir / "2-old.jsonl").write_text(
            '{"type":"user","message":{"content":"Please build a dashboard for sales data."}}\n'
            '{"type":"user","message":{"content":"Please do not use em dashes next time."}}\n',
            encoding="utf-8"
        )
        (convo_dir / "1-active.jsonl").write_text(
            '{"type":"user","message":{"content":"active session placeholder"}}\n',
            encoding="utf-8"
        )

        env = os.environ.copy()
        tmp_path_posix = get_posix_path(self.tmp_path)

        script_path = "skills/health/scripts/collect-data.sh"
        p = subprocess.run(
            [BASH_PATH, "-c", f'export HOME="{tmp_path_posix}"; exec {script_path} auto'],
            cwd=str(ROOT_DIR),
            env=env,
            capture_output=True,
            encoding="utf-8"
        )
        self.assertEqual(p.returncode, 0, f"collect-data.sh failed:\nstderr: {p.stderr}")


        self.assertIn("=== CONVERSATION SIGNALS ===", p.stdout)
        self.assertIn("USER CORRECTION: Please do not use em dashes next time.", p.stdout)
        self.assertNotIn("USER CORRECTION: Please build a dashboard for sales data.", p.stdout)


@unittest.skipIf(not BASH_PATH, "bash is not available")
class TestBashSyntax(unittest.TestCase):

    def test_syntax(self) -> None:
        scripts = [
            "scripts/statusline.sh",
            "skills/health/scripts/collect-data.sh",
            "skills/read/scripts/fetch.sh",
            "scripts/setup-statusline.sh",
            "skills/check/scripts/run-tests.sh"
        ]
        for rel_path in scripts:
            script_path = ROOT_DIR / rel_path
            if script_path.exists():
                p = subprocess.run(
                    [BASH_PATH, "-n", rel_path],
                    cwd=str(ROOT_DIR),
                    capture_output=True,
                    encoding="utf-8"
                )
                self.assertEqual(p.returncode, 0, f"Bash syntax check failed for {rel_path}:\nstderr: {p.stderr}")


@unittest.skipIf(not GIT_PATH, "git is not available")
class TestGitDiff(unittest.TestCase):

    def test_git_diff_check(self) -> None:
        # Run git diff --check on the repository root
        p = subprocess.run(
            [GIT_PATH, "diff", "--check"],
            cwd=str(ROOT_DIR),
            capture_output=True,
            encoding="utf-8"
        )
        self.assertEqual(p.returncode, 0, f"git diff --check failed:\nstdout: {p.stdout}\nstderr: {p.stderr}")


@unittest.skipIf(not BASH_PATH or not JQ_PATH, "bash or jq is not available")
class TestLiveCollectData(unittest.TestCase):

    def test_live_collect_data(self) -> None:
        # Run health/scripts/collect-data.sh auto on the real repository (read-only verification check from verify-scripts)
        script_path = "skills/health/scripts/collect-data.sh"
        p = subprocess.run(
            [BASH_PATH, script_path, "auto"],
            cwd=str(ROOT_DIR),
            capture_output=True,
            encoding="utf-8"
        )
        self.assertEqual(p.returncode, 0, f"collect-data.sh auto failed:\nstderr: {p.stderr}")

        # Check for expected headers in the real run output
        self.assertIn("=== CONVERSATION SIGNALS ===", p.stdout)
        self.assertIn("=== CONVERSATION EXTRACT ===", p.stdout)
        self.assertIn("=== MCP ACCESS DENIALS ===", p.stdout)


# Auxiliary helper functions
def json_load_file(path: Path) -> dict:
    import json
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def json_write_file(path: Path, data: dict) -> None:
    import json
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def json_load_data(s: str) -> dict:
    import json
    return json.loads(s)


if __name__ == "__main__":
    unittest.main()
