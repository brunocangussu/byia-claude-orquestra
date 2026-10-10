"""Guardas de instrução do worker; não medem o comportamento geral da LLM."""

import unittest
from pathlib import Path


class ImplementerWorkerBoundaryTest(unittest.TestCase):
    def setUp(self):
        self.text = (Path(__file__).resolve().parents[1] / "agents/orq-implementer.md").read_text(
            encoding="utf-8"
        )

    def test_git_delivery_stays_with_the_manager(self):
        self.assertIn("Entrega Git é do Manager", self.text)
        self.assertIn("não faça stage, commit, push ou integração", self.text)
        self.assertNotIn("Commit\n  local só se o Manager mandar", self.text)

    def test_worker_cannot_expand_scope_or_delegate_recursively(self):
        self.assertIn("Não crie refs/worktrees nem delegue a outros agentes", self.text)
        self.assertIn("ownership de arquivos definido no briefing", self.text)
        self.assertIn("ORQ_PACKAGE_ROOT/skills/orq/SKILL.md", self.text)

    def test_failure_preserves_handle_and_reports_only_the_affected_delivery(self):
        self.assertIn("relate ao Manager somente a entrega afetada", self.text)
        self.assertIn("preserve o handle e as evidências", self.text)
        self.assertIn("não relance a chamada cegamente", self.text)

    def test_repo_gate_has_an_explicit_covered_complement_exception(self):
        root = Path(__file__).resolve().parents[2]
        for name in ("AGENTS.md", "CLAUDE.md"):
            with self.subTest(consumer=name):
                text = (root / name).read_text(encoding="utf-8")
                self.assertIn("Pedido novo ou fora do acordo entra pelo ciclo", text)
                self.assertIn("Complemento coberto pela meta aprovada segue pelo aceite técnico", text)
                self.assertNotIn("Todo pedido de mudança entra pelo ciclo", text)


if __name__ == "__main__":
    unittest.main()
