"""Regressões executáveis em memória; sem escrever ou executar modelo externo."""

import types
import unittest
from pathlib import Path
from unittest import mock

import test_preflight


class MutationTest(unittest.TestCase):
    def test_oito_regressoes_sao_detectadas_sem_erros_de_bancada(self):
        source = Path(__file__).with_name("preflight.py").read_text()
        mutations = (
            ("validação removida", (("    validate_sample(sample)", "    # removido"),)),
            ("payload contaminado", (('{"id": c["id"], "text": c["text"]}', "dict(c)"),)),
            ("campo extra", (("set(case) == FIELDS", "True"),)),
            # Uma guarda isolada é redundante com a outra: remoção conjunta é o
            # contrafactual que realmente permite IDs duplicados passar.
            ("IDs duplicados", (("case[\"id\"] not in ids", "True"),
                                ('ids == {f"Y{i:03d}" for i in range(1, 49)}', "True"))),
            ("família cruzada", (('FAMILY_SPLIT.get(case["family"]) == case["split"]',
                                  'case["family"] in FAMILY_SPLIT'),)),
            ("pedido duplicado", (("normalized not in texts", "True"),)),
            ("controle contrastivo", (('case["gold"] == gold and all(t in case["text"].casefold() for t in terms)', "True"),)),
            ("justificativa vazia", (("isinstance(value, str) and value.strip()", "isinstance(value, str)"),)),
        )
        for label, changes in mutations:
            with self.subTest(mutante=label):
                mutant = source
                for old, new in changes:
                    self.assertEqual(mutant.count(old), 1, "mutação não aplicável")
                    mutant = mutant.replace(old, new, 1)
                module = types.ModuleType("preflight_mutante")
                exec(compile(mutant, "preflight_mutante", "exec"), module.__dict__)
                with mock.patch.object(test_preflight, "preflight", module):
                    suite = unittest.defaultTestLoader.loadTestsFromTestCase(test_preflight.PreflightTest)
                    result = unittest.TestResult()
                    suite.run(result)
                self.assertEqual(result.testsRun, 13)
                self.assertEqual(result.errors, [], "erro de bancada não mata mutante")
                self.assertTrue(result.failures, "regressão sobreviveu")


if __name__ == "__main__":
    unittest.main()
