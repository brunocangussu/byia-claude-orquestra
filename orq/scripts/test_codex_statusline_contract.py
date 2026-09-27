#!/usr/bin/env python3
"""Contrato somente leitura da statusline nativa da TUI do Codex (T-128)."""

from __future__ import annotations

import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PLUGIN_ROOT.parent
REFERENCE = REPO_ROOT / "orq/skills/orq/references/hosts/codex.md"
CONSUMERS = (
    REPO_ROOT / "orq/skills/orq/SKILL.md",
    REPO_ROOT / "orq/commands/init.md",
    REPO_ROOT / "orq/commands/stack.md",
)
LINT_PATH = Path(__file__).with_name("lint-coerencia.py")


def _fixture_root(directory: str, name: str = "fixture") -> Path:
    return Path(directory).resolve(strict=True) / name

lint_spec = importlib.util.spec_from_file_location("orq_lint_coerencia_t128", LINT_PATH)
assert lint_spec is not None and lint_spec.loader is not None
lint = importlib.util.module_from_spec(lint_spec)
lint_spec.loader.exec_module(lint)


class CodexStatuslineReferenceContractTest(unittest.TestCase):
    def test_reference_exists_and_declares_read_only_scope(self) -> None:
        self.assertTrue(REFERENCE.is_file())
        text = REFERENCE.read_text(encoding="utf-8")
        for fragment in (
            "TUI do Codex CLI",
            "Codex Desktop",
            "[tui].status_line",
            "não é o board do Orquestra",
            "não exibe nem persiste valores",
            "ID presumido",
            "nova TUI",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, text)

    def test_live_consumers_delegate_to_the_single_host_reference(self) -> None:
        for consumer in CONSUMERS:
            with self.subTest(consumer=consumer):
                self.assertTrue(
                    "references/hosts/codex.md"
                    in consumer.read_text(encoding="utf-8"),
                    f"{consumer.relative_to(REPO_ROOT)} must delegate to the Codex host reference",
                )

    def test_commands_use_package_root_for_host_reference(self) -> None:
        reference = "${ORQ_PACKAGE_ROOT}/skills/orq/references/hosts/codex.md"
        for consumer in CONSUMERS:
            if consumer.parent.name != "commands":
                continue
            with self.subTest(consumer=consumer):
                self.assertTrue(
                    reference in consumer.read_text(encoding="utf-8"),
                    f"referência não ancorada em {consumer.relative_to(REPO_ROOT)}",
                )

    def test_lint_guards_the_reference_and_each_live_consumer(self) -> None:
        self.assertTrue(
            hasattr(lint, "validate_codex_statusline_contract"),
            "lint-coerencia.py must expose the T-128 statusline contract validator",
        )

        self.assertEqual(
            [],
            lint.validate_codex_statusline_contract(REPO_ROOT, PLUGIN_ROOT),
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            for source in (REFERENCE, *CONSUMERS):
                target = root / source.relative_to(REPO_ROOT)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

            stack = root / "orq/commands/stack.md"
            stack.write_text(
                stack.read_text(encoding="utf-8").replace(
                    "references/hosts/codex.md",
                    "references/hosts/ausente.md",
                    1,
                ),
                encoding="utf-8",
            )
            manual = root / "orq/commands/manual.md"
            manual.write_text("Use [tui].status_line diretamente.\n", encoding="utf-8")
            manual_sem_colchetes = root / "orq/commands/manual-sem-colchetes.md"
            manual_sem_colchetes.write_text(
                "Use tui.status_line diretamente.\n",
                encoding="utf-8",
            )

            problems = lint.validate_codex_statusline_contract(root, root / "orq")

        self.assertTrue(
            any(path.name == "stack.md" for path, _, _ in problems),
            problems,
        )
        self.assertTrue(
            any(path.name == "manual.md" for path, _, _ in problems),
            problems,
        )
        self.assertTrue(
            any(path.name == "manual-sem-colchetes.md" for path, _, _ in problems),
            problems,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            for source in (REFERENCE, *CONSUMERS):
                target = root / source.relative_to(REPO_ROOT)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

            reference = root / REFERENCE.relative_to(REPO_ROOT)
            reference.write_text(
                reference.read_text(encoding="utf-8").replace("ID presumido", "ID indireto", 1),
                encoding="utf-8",
            )

            problems = lint.validate_codex_statusline_contract(root, root / "orq")

        self.assertTrue(
            any(path == REFERENCE.relative_to(REPO_ROOT) for path, _, _ in problems),
            problems,
        )

    def test_lint_does_not_follow_symlink_in_parent_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            for source in (REFERENCE, *CONSUMERS):
                target = root / source.relative_to(REPO_ROOT)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

            parent = root / "orq/skills/orq/references/hosts"
            outside = Path(tmp) / "outside-hosts"
            os.replace(parent, outside)
            parent.symlink_to(outside, target_is_directory=True)

            problems = lint.validate_codex_statusline_contract(root, root / "orq")

        self.assertTrue(
            any(path == REFERENCE.relative_to(REPO_ROOT) for path, _, _ in problems),
            problems,
        )

    def test_lint_rejects_symlinked_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            real_root = _fixture_root(tmp, "real-fixture")
            for source in (REFERENCE, *CONSUMERS):
                target = real_root / source.relative_to(REPO_ROOT)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

            root = _fixture_root(tmp)
            root.symlink_to(real_root, target_is_directory=True)
            problems = lint.validate_codex_statusline_contract(root, root / "orq")

        self.assertTrue(
            any(path == REFERENCE.relative_to(REPO_ROOT) for path, _, _ in problems),
            problems,
        )

    def test_lint_fails_closed_without_nofollow(self) -> None:
        with mock.patch.object(lint.os, "O_NOFOLLOW", new=None):
            problems = lint.validate_codex_statusline_contract(REPO_ROOT, PLUGIN_ROOT)

        self.assertTrue(
            any(path == REFERENCE.relative_to(REPO_ROOT) for path, _, _ in problems),
            problems,
        )

    def test_lint_rejects_statusline_markdown_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            for source in (REFERENCE, *CONSUMERS):
                target = root / source.relative_to(REPO_ROOT)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

            outside = Path(tmp) / "outside-statusline.md"
            outside.write_text("Use tui.status_line diretamente.\n", encoding="utf-8")
            link = root / "orq/commands/statusline-external.md"
            link.symlink_to(outside)

            problems = lint.validate_codex_statusline_contract(root, root / "orq")

        self.assertTrue(
            any(path.name == "statusline-external.md" and "simbólico" in message for path, _, message in problems),
            problems,
        )

    def test_delegation_inside_fenced_example_does_not_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            for source in (REFERENCE, *CONSUMERS):
                target = root / source.relative_to(REPO_ROOT)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

            stack = root / "orq/commands/stack.md"
            stack.write_text(
                stack.read_text(encoding="utf-8").replace(
                    "references/hosts/codex.md", "references/hosts/ausente.md"
                )
                + "\n```text\nreferences/hosts/codex.md\n```\n",
                encoding="utf-8",
            )
            problems = lint.validate_codex_statusline_contract(root, root / "orq")

        self.assertTrue(any(path.name == "stack.md" for path, _, _ in problems), problems)

    def test_command_relative_reference_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            for source in (REFERENCE, *CONSUMERS):
                target = root / source.relative_to(REPO_ROOT)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

            stack = root / "orq/commands/stack.md"
            stack.write_text(
                stack.read_text(encoding="utf-8").replace(
                    "${ORQ_PACKAGE_ROOT}/skills/orq/references/hosts/codex.md",
                    "references/hosts/codex.md",
                ),
                encoding="utf-8",
            )
            problems = lint.validate_codex_statusline_contract(root, root / "orq")

        self.assertTrue(any(path.name == "stack.md" for path, _, _ in problems), problems)

    def test_new_command_cannot_delegate_by_unresolved_relative_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            for source in (REFERENCE, *CONSUMERS):
                target = root / source.relative_to(REPO_ROOT)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

            doctor = root / "orq/commands/doctor.md"
            doctor.write_text(
                "Leia references/hosts/codex.md antes de diagnosticar [tui].status_line.\n",
                encoding="utf-8",
            )
            problems = lint.validate_codex_statusline_contract(root, root / "orq")

        self.assertTrue(any(path.name == "doctor.md" for path, _, _ in problems), problems)

    def test_symbolic_directory_under_commands_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            for source in (REFERENCE, *CONSUMERS):
                target = root / source.relative_to(REPO_ROOT)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

            outside = Path(tmp) / "outside"
            outside.mkdir()
            (outside / "doctor.md").write_text("Use [tui].status_line diretamente.\n", encoding="utf-8")
            (root / "orq/commands/linked").symlink_to(outside, target_is_directory=True)
            problems = lint.validate_codex_statusline_contract(root, root / "orq")

        self.assertTrue(any(path.name == "linked" and "simbólico" in message for path, _, message in problems), problems)

    def test_lint_ignores_statusline_mentions_in_fenced_examples(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            for source in (REFERENCE, *CONSUMERS):
                target = root / source.relative_to(REPO_ROOT)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

            example = root / "orq/commands/exemplo-statusline.md"
            example.write_text(
                "```toml\n[tui].status_line = [\"example\"]\n```\n",
                encoding="utf-8",
            )

            problems = lint.validate_codex_statusline_contract(root, root / "orq")

        self.assertFalse(
            any(path.name == "exemplo-statusline.md" for path, _, _ in problems),
            problems,
        )

    def test_lint_rejects_symlinked_required_contract_files(self) -> None:
        for contract_file in (REFERENCE, *CONSUMERS):
            with self.subTest(contract_file=contract_file):
                with tempfile.TemporaryDirectory() as tmp:
                    root = _fixture_root(tmp)
                    for source in (REFERENCE, *CONSUMERS):
                        target = root / source.relative_to(REPO_ROOT)
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

                    outside = Path(tmp) / "outside.md"
                    outside.write_text(
                        "TUI do Codex CLI\nCodex Desktop\n[tui].status_line\n"
                        "não é o board do Orquestra\nnão exibe nem persiste valores\n"
                        "ID presumido\nnova TUI\nreferences/hosts/codex.md\n",
                        encoding="utf-8",
                    )
                    target = root / contract_file.relative_to(REPO_ROOT)
                    target.unlink()
                    target.symlink_to(outside)

                    problems = lint.validate_codex_statusline_contract(root, root / "orq")

                self.assertTrue(
                    any(
                        path == contract_file.relative_to(REPO_ROOT) and "simbólico" in message
                        for path, _, message in problems
                    ),
                    problems,
                )


if __name__ == "__main__":
    unittest.main()
