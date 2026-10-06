"""Consumidores T-149: padrão único, explícito e sem ativação por fallback."""
from pathlib import Path
import importlib.util
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("lint_elenco_t149", ROOT / "scripts/lint-coerencia.py")
lint = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lint)


class ConsumidoresTest(unittest.TestCase):
    def test_consumidores_resolvem_modelo_e_effort_do_perfil(self):
        for name in ("elenco", "init", "plan-next", "implement-next", "revisar"):
            text = (ROOT / "commands" / (name + ".md")).read_text()
            with self.subTest(command=name):
                self.assertIn("elenco_padrao.py", text)
                self.assertIn("modelo e effort", text)
        skill = (ROOT / "skills/orq/SKILL.md").read_text()
        self.assertIn("padrão desta versão", skill)
        self.assertIn("elenco_padrao.py", skill)

    def test_agentes_nao_tem_modelo_fixo_que_contorne_o_elenco(self):
        for name in ("planner", "implementer", "reviewer", "docs", "scout"):
            text = (ROOT / "agents" / ("orq-" + name + ".md")).read_text()
            with self.subTest(agent=name):
                self.assertIn("model: inherit", text.split("---")[1])
                self.assertIn("modelo e effort", text)
                self.assertIn("elenco_padrao.py", text)
                self.assertIn("não autoriza", text)

    def test_guarda_catalogo_e_consumidores(self):
        self.assertEqual(lint.validate_versioned_roster(ROOT.parent, ROOT), [])

    def test_mutacoes_fabrica_alias_effort_e_consumidor_sem_resolvedor(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp) / "repo"
            shutil.copytree(ROOT, repo / "orq")
            root = repo / "orq"
            self.assertEqual(lint.validate_versioned_roster(repo, root), [])
            for file, old, new in (
                ("commands/elenco.md", "`gpt-6-luna@low`", "`gpt-6-luna@high`"),
                ("commands/elenco.md", "`claude-opus-5-5@high`", "`opus@high`"),
                ("commands/revisar.md", "elenco_padrao.py", "sem-resolvedor.py"),
                ("agents/orq-docs.md", "model: inherit", "model: sonnet"),
            ):
                path = root / file
                original = path.read_text()
                self.assertIn(old, original)
                path.write_text(original.replace(old, new, 1))
                with self.subTest(file=file):
                    self.assertTrue(lint.validate_versioned_roster(repo, root))
                path.write_text(original)


if __name__ == "__main__":
    unittest.main()
