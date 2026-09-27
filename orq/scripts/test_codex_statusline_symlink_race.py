from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PLUGIN_ROOT.parent
REFERENCE = REPO_ROOT / "orq/skills/orq/references/hosts/codex.md"
CONSUMERS = (
    REPO_ROOT / "orq/skills/orq/SKILL.md",
    REPO_ROOT / "orq/commands/init.md",
    REPO_ROOT / "orq/commands/stack.md",
)
LINT_PATH = Path(__file__).with_name("lint-coerencia.py")


def _fixture_root(directory: str) -> Path:
    return Path(directory).resolve(strict=True) / "fixture"

lint_spec = importlib.util.spec_from_file_location("orq_lint_coerencia_t128_race", LINT_PATH)
assert lint_spec is not None and lint_spec.loader is not None
lint = importlib.util.module_from_spec(lint_spec)
lint_spec.loader.exec_module(lint)


class CodexStatuslineSymlinkRaceTest(unittest.TestCase):
    def test_rejeita_referencia_trocada_por_link_apos_a_prechecagem(self) -> None:
        """A leitura deve falhar mesmo se o estado do caminho mudar entre checagem e abertura."""
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            for source in (REFERENCE, *CONSUMERS):
                target = root / source.relative_to(REPO_ROOT)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

            reference = root / REFERENCE.relative_to(REPO_ROOT)
            outside = Path(tmp) / "outside-statusline.md"
            outside.write_text(REFERENCE.read_text(encoding="utf-8"), encoding="utf-8")
            reference.unlink()
            reference.symlink_to(outside)

            # Simula a troca logo após a pré-checagem; a abertura ainda deve recusar o link real.
            with patch.object(Path, "is_symlink", return_value=False):
                problems = lint.validate_codex_statusline_contract(root, root / "orq")

        self.assertTrue(
            any(path == REFERENCE.relative_to(REPO_ROOT) for path, _, _ in problems),
            problems,
        )


if __name__ == "__main__":
    unittest.main()
