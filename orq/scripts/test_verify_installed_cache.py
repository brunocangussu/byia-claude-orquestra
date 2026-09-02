#!/usr/bin/env python3
"""Regression tests for strict cross-host installed-cache verification."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

from orq.scripts.verify_installed_cache import find_installation_divergences, main


class InstallationComparatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = Path(tempfile.mkdtemp(prefix="orq-cache-verify-"))
        self.source = self.tempdir / "source"
        self.installed = self.tempdir / "installed"
        self.source.mkdir()
        self.installed.mkdir()

    def tearDown(self) -> None:
        shutil.rmtree(self.tempdir)

    def compare(self, host: str) -> list[tuple[str, str, str]]:
        divergences = find_installation_divergences(
            self.source,
            self.installed,
            host,
        )
        return [(item.kind, item.path, item.detail) for item in divergences]

    @staticmethod
    def write(root: Path, relative: str, content: bytes = b"same\n") -> None:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)

    def write_both(self, relative: str, content: bytes = b"same\n") -> None:
        self.write(self.source, relative, content)
        self.write(self.installed, relative, content)

    def test_identical_trees_pass_for_both_hosts(self) -> None:
        self.write_both(".claude-plugin/plugin.json")
        self.write_both("scripts/check.py")

        self.assertEqual(self.compare("claude"), [])
        self.assertEqual(self.compare("codex"), [])

    def test_claude_allows_only_installed_top_level_runtime_metadata(self) -> None:
        self.write_both("manifest.txt")
        (self.installed / ".in_use").mkdir()
        self.write(self.installed, ".in_use/4242", b"")
        self.write(self.installed, ".orphaned_at", b"2026-08-30\n")

        self.assertEqual(self.compare("claude"), [])

        shutil.rmtree(self.installed / ".in_use")
        self.write(self.installed, ".in_use", b"")
        self.assertEqual(self.compare("claude"), [])

    def test_codex_allows_only_exact_migrated_command_skills_subtree(self) -> None:
        self.write_both(".codex-plugin/plugin.json")
        self.write(
            self.installed,
            ".codex-plugin/migrated-command-skills/orq/SKILL.md",
        )

        self.assertEqual(self.compare("codex"), [])

    def test_codex_allows_runtime_parent_when_source_has_no_codex_plugin(self) -> None:
        self.write_both("manifest.txt")
        self.write(
            self.installed,
            ".codex-plugin/migrated-command-skills/orq/SKILL.md",
        )

        self.assertEqual(self.compare("codex"), [])

    def test_source_homonyms_are_never_ignored(self) -> None:
        self.write(self.source, ".in_use", b"product\n")
        self.write(self.source, ".orphaned_at", b"product\n")
        self.write(
            self.source,
            ".codex-plugin/migrated-command-skills/orq/SKILL.md",
        )

        self.assertEqual(
            self.compare("claude"),
            [
                ("missing", ".codex-plugin", ""),
                ("missing", ".codex-plugin/migrated-command-skills", ""),
                (
                    "missing",
                    ".codex-plugin/migrated-command-skills/orq",
                    "",
                ),
                (
                    "missing",
                    ".codex-plugin/migrated-command-skills/orq/SKILL.md",
                    "",
                ),
                ("missing", ".in_use", ""),
                ("missing", ".orphaned_at", ""),
            ],
        )
        self.assertEqual(
            self.compare("codex"),
            [
                ("missing", ".codex-plugin", ""),
                ("missing", ".codex-plugin/migrated-command-skills", ""),
                (
                    "missing",
                    ".codex-plugin/migrated-command-skills/orq",
                    "",
                ),
                (
                    "missing",
                    ".codex-plugin/migrated-command-skills/orq/SKILL.md",
                    "",
                ),
                ("missing", ".in_use", ""),
                ("missing", ".orphaned_at", ""),
            ],
        )

    def test_wrong_host_prefix_lookalikes_and_ds_store_fail(self) -> None:
        self.write(self.installed, ".in_use/1", b"")
        self.write(self.installed, ".orphaned_at", b"runtime\n")
        self.write(self.installed, "nested/.in_use/2", b"")
        self.write(self.installed, ".in_use-x", b"")
        self.write(self.installed, ".DS_Store", b"finder\n")
        self.write(
            self.installed,
            ".codex-plugin/migrated-command-skills/x.md",
        )
        self.write(self.installed, ".codex-plugin/other.txt", b"extra\n")
        self.write(
            self.installed,
            ".codex-plugin/migrated-command-skills-x/evil.md",
        )
        self.write(
            self.installed,
            "nested/.codex-plugin/migrated-command-skills/evil.md",
        )

        claude_paths = [path for _, path, _ in self.compare("claude")]
        self.assertNotIn(".in_use", claude_paths)
        self.assertNotIn(".in_use/1", claude_paths)
        self.assertIn(".codex-plugin/migrated-command-skills", claude_paths)
        self.assertIn(".DS_Store", claude_paths)
        self.assertIn("nested/.in_use/2", claude_paths)
        self.assertIn(".in_use-x", claude_paths)
        self.assertNotIn(".orphaned_at", claude_paths)

        codex_paths = [path for _, path, _ in self.compare("codex")]
        self.assertNotIn(".codex-plugin/migrated-command-skills", codex_paths)
        self.assertNotIn(
            ".codex-plugin/migrated-command-skills/x.md",
            codex_paths,
        )
        self.assertIn(".in_use/1", codex_paths)
        self.assertIn(".orphaned_at", codex_paths)
        self.assertIn(".in_use-x", codex_paths)
        self.assertIn(".codex-plugin", codex_paths)
        self.assertIn(".codex-plugin/other.txt", codex_paths)
        self.assertIn(
            ".codex-plugin/migrated-command-skills-x/evil.md",
            codex_paths,
        )
        self.assertIn(
            "nested/.codex-plugin/migrated-command-skills/evil.md",
            codex_paths,
        )
        self.assertIn(".DS_Store", codex_paths)

    def test_metadata_with_unexpected_type_is_not_allowed(self) -> None:
        (self.installed / ".orphaned_at").mkdir()
        (self.installed / ".in_use").symlink_to("outside")
        self.write(self.installed, ".codex-plugin/migrated-command-skills", b"file\n")

        claude_paths = [path for _, path, _ in self.compare("claude")]
        self.assertIn(".in_use", claude_paths)
        self.assertIn(".orphaned_at", claude_paths)

        codex_paths = [path for _, path, _ in self.compare("codex")]
        self.assertIn(".codex-plugin/migrated-command-skills", codex_paths)

    def test_extra_missing_empty_directory_type_and_bytes_are_reported(self) -> None:
        self.write(self.source, "missing.txt")
        self.write(self.installed, "extra.txt")
        (self.installed / "empty-extra").mkdir()
        self.write(self.source, "changed.txt", b"source\n")
        self.write(self.installed, "changed.txt", b"installed\n")
        self.write(self.source, "type-change", b"file\n")
        (self.installed / "type-change").mkdir()

        self.assertEqual(
            self.compare("claude"),
            [
                ("bytes", "changed.txt", ""),
                ("extra", "empty-extra", ""),
                ("extra", "extra.txt", ""),
                ("missing", "missing.txt", ""),
                ("type", "type-change", "source=file, installed=directory"),
            ],
        )

    def test_allowed_metadata_does_not_hide_real_divergence(self) -> None:
        self.write(self.installed, ".in_use/4242", b"")
        self.write(self.installed, "real-extra.txt", b"extra\n")

        self.assertEqual(
            self.compare("claude"),
            [("extra", "real-extra.txt", "")],
        )

    def test_symlinks_are_compared_without_following_targets(self) -> None:
        outside = self.tempdir / "outside-secret"
        outside.write_text("must not be read\n", encoding="utf-8")
        (self.source / "link").symlink_to(outside)
        (self.installed / "link").symlink_to("different-target")

        self.assertEqual(
            self.compare("claude"),
            [("bytes", "link", "symlink target differs")],
        )


class InstallationVerifierCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = Path(tempfile.mkdtemp(prefix="orq-cache-cli-"))
        self.source = self.tempdir / "source"
        self.installed = self.tempdir / "installed"
        self.source.mkdir()
        self.installed.mkdir()

    def tearDown(self) -> None:
        shutil.rmtree(self.tempdir)

    def run_cli(self, *args: str) -> tuple[int, str, str]:
        stdout = StringIO()
        stderr = StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            result = main(list(args))
        return result, stdout.getvalue(), stderr.getvalue()

    def default_args(self, host: str = "claude") -> tuple[str, ...]:
        return (
            "--host",
            host,
            "--source",
            str(self.source),
            "--installed",
            str(self.installed),
        )

    def test_cli_returns_one_and_prints_sorted_divergences(self) -> None:
        (self.installed / "z-extra.txt").write_text("z\n", encoding="utf-8")
        (self.installed / "a-extra.txt").write_text("a\n", encoding="utf-8")

        result, stdout, stderr = self.run_cli(*self.default_args())

        self.assertEqual(result, 1)
        self.assertEqual(
            stdout.splitlines(),
            ["extra: a-extra.txt", "extra: z-extra.txt"],
        )
        self.assertEqual(stderr, "")

    def test_cli_returns_two_for_missing_or_non_directory_root(self) -> None:
        missing = self.tempdir / "missing"
        result, stdout, stderr = self.run_cli(
            "--host",
            "claude",
            "--source",
            str(missing),
            "--installed",
            str(self.installed),
        )
        self.assertEqual(result, 2)
        self.assertEqual(stdout, "")
        self.assertTrue(stderr.startswith("error:"), stderr)

        not_directory = self.tempdir / "not-directory"
        not_directory.write_text("file\n", encoding="utf-8")
        result, stdout, stderr = self.run_cli(
            "--host",
            "claude",
            "--source",
            str(self.source),
            "--installed",
            str(not_directory),
        )
        self.assertEqual(result, 2)
        self.assertEqual(stdout, "")
        self.assertIn("root is not a directory", stderr)

    def test_cli_rejects_unknown_host_with_exit_two(self) -> None:
        result, stdout, stderr = self.run_cli(*self.default_args("other"))

        self.assertEqual(result, 2)
        self.assertEqual(stdout, "")
        self.assertIn("error:", stderr)
        self.assertIn("other", stderr)

    def test_cli_returns_zero_for_each_host_with_only_allowed_metadata(self) -> None:
        (self.installed / ".in_use").mkdir()
        (self.installed / ".in_use" / "4242").write_text("", encoding="utf-8")

        result, stdout, stderr = self.run_cli(*self.default_args("claude"))
        self.assertEqual(result, 0)
        self.assertEqual(stdout, "ok: installed cache matches source (host=claude)\n")
        self.assertEqual(stderr, "")

        shutil.rmtree(self.installed / ".in_use")
        for root in (self.source, self.installed):
            plugin_dir = root / ".codex-plugin"
            plugin_dir.mkdir()
            (plugin_dir / "plugin.json").write_text("{}\n", encoding="utf-8")
        migrated = self.installed / ".codex-plugin" / "migrated-command-skills"
        migrated.mkdir()
        (migrated / "orq.md").write_text("generated\n", encoding="utf-8")

        result, stdout, stderr = self.run_cli(*self.default_args("codex"))
        self.assertEqual(result, 0)
        self.assertEqual(stdout, "ok: installed cache matches source (host=codex)\n")
        self.assertEqual(stderr, "")

    def test_cli_applies_runtime_metadata_allowlist_only_to_selected_host(self) -> None:
        (self.installed / ".in_use").mkdir()
        result, stdout, stderr = self.run_cli(*self.default_args("codex"))
        self.assertEqual(result, 1)
        self.assertIn("extra: .in_use", stdout)
        self.assertEqual(stderr, "")

        shutil.rmtree(self.installed / ".in_use")
        migrated = self.installed / ".codex-plugin" / "migrated-command-skills"
        migrated.mkdir(parents=True)
        (migrated / "orq.md").write_text("generated\n", encoding="utf-8")
        result, stdout, stderr = self.run_cli(*self.default_args("claude"))
        self.assertEqual(result, 1)
        self.assertIn("extra: .codex-plugin/migrated-command-skills", stdout)
        self.assertEqual(stderr, "")


class VerifierImportSideEffectTests(unittest.TestCase):
    def test_direct_lint_execution_does_not_create_verifier_pycache(self) -> None:
        with tempfile.TemporaryDirectory(prefix="orq-lint-import-") as tempdir:
            root = Path(tempdir)
            scripts = root / "orq" / "scripts"
            scripts.mkdir(parents=True)
            source_scripts = Path(__file__).resolve().parent
            for name in ("lint-coerencia.py", "verify_installed_cache.py"):
                shutil.copy2(source_scripts / name, scripts / name)

            import_marker = root / "verifier-imported"
            verifier = scripts / "verify_installed_cache.py"
            verifier.write_text(
                verifier.read_text(encoding="utf-8")
                + f"\nPath({str(import_marker)!r}).write_text('ok', encoding='utf-8')\n",
                encoding="utf-8",
            )

            env = os.environ.copy()
            env.pop("PYTHONDONTWRITEBYTECODE", None)
            completed = subprocess.run(
                [
                    sys.executable,
                    "-X",
                    "pycache_prefix=",
                    str(scripts / "lint-coerencia.py"),
                    str(root),
                ],
                cwd=root,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )

            pycache = scripts / "__pycache__"
            self.assertEqual(completed.returncode, 2, completed.stderr)
            self.assertNotIn("Traceback", completed.stderr)
            self.assertEqual(import_marker.read_text(encoding="utf-8"), "ok")
            self.assertFalse(
                pycache.exists(),
                "o lint não pode criar divergência de cache ao importar o verificador",
            )


class VerifierCommandContractTests(unittest.TestCase):
    def test_installer_and_diagnosis_use_shared_verifier_for_host_caches(self) -> None:
        plugin_root = Path(__file__).resolve().parents[1]
        installer = (plugin_root / "commands" / "instalar.md").read_text(
            encoding="utf-8"
        )
        stack = (plugin_root / "commands" / "stack.md").read_text(encoding="utf-8")

        self.assertIn("verify_installed_cache.py", installer)
        self.assertIn("--host codex", installer)
        self.assertNotIn("O cache do Claude só pode substituir esse clone", installer)
        self.assertNotIn(
            "quando `<fonte-local>` veio do cache do Claude",
            installer,
        )
        self.assertIn("Exit `2`", installer)
        self.assertNotIn(
            "diff -rq ~/.codex/plugins/cache/orquestra/orq/<versão>/",
            installer,
        )
        self.assertIn("verify_installed_cache.py", stack)
        self.assertIn("--host claude", stack)
        self.assertNotIn("corrige com bump", stack)
        self.assertIn("Exit `2`", stack)
        self.assertNotIn("diff -rq ~/.claude/plugins/cache/", stack)

    def test_living_docs_and_agent_contract_use_shared_verifier(self) -> None:
        plugin_root = Path(__file__).resolve().parents[1]
        repo_root = plugin_root.parent
        readme = (repo_root / "README.md").read_text(encoding="utf-8")
        distribution = (repo_root / "memory/wiki/distribuicao.md").read_text(
            encoding="utf-8"
        )
        architecture = (repo_root / "memory/wiki/arquitetura.md").read_text(
            encoding="utf-8"
        )
        agents = (repo_root / "AGENTS.md").read_text(encoding="utf-8")
        claude = (repo_root / "CLAUDE.md").read_text(encoding="utf-8")

        for text in (readme, distribution, architecture, agents):
            self.assertIn("verify_installed_cache.py", text)
        self.assertNotIn("exit `1` = bump", readme)
        self.assertIn("<clean-source>", readme)
        self.assertIn("<clean-source>", distribution)
        self.assertNotIn("open('orq/.claude-plugin/plugin.json')", distribution)
        self.assertIn("ORQ_CLEAN_SOURCE", distribution)
        self.assertNotIn(
            "diff -rq ~/.claude/plugins/cache/orquestra/orq/$V/ ./orq/",
            distribution,
        )
        self.assertEqual(agents, claude)
        # A asserção original exigia o nome de UM módulo. Ela era satisfeita por
        # uma lista enumerada de três dos cinco — quem seguisse a instrução
        # rodaria 119 dos 201 testes achando que rodara tudo. Provar a
        # descoberta é mais forte: cobre todo `test_*.py`, inclusive os que
        # ainda não existem, e proíbe a enumeração que envelhece calada.
        self.assertIn("PYTHONDONTWRITEBYTECODE=1 python3 -m unittest", agents)
        self.assertIn(
            "python3 -m unittest discover -s orq/scripts -p 'test_*.py'", agents
        )
        self.assertNotRegex(agents, r"python3 -m unittest\s+orq\.scripts\.")
        self.assertIn("--host codex", agents)
        self.assertIn("checkout detached", agents)


if __name__ == "__main__":
    unittest.main()
