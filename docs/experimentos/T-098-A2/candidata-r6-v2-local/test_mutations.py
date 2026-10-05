"""Mutações locais das guardas de formato, limite e regra."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

import preflight

ROOT = Path(__file__).resolve().parent


def load_v2():
    return (
        json.loads((ROOT / "amostra.json").read_text(encoding="utf-8")),
        json.loads((ROOT / "manifesto.json").read_text(encoding="utf-8")),
        json.loads((ROOT / "regra-lexical-dev.json").read_text(encoding="utf-8"))
    )


class R6V2MutationTest(unittest.TestCase):
    def test_formato_rejeita_todos_os_abster_com_interrogacao(self):
        sample, manifest, _ = load_v2()
        labels = preflight.gold_by_id(manifest)
        mutated = deepcopy(sample["cases"])
        for case in mutated:
            if labels[case["id"]] == "abster" and "?" not in case["text"]:
                case["text"] += "?"
        with self.assertRaisesRegex(ValueError, "formato exclusivo de abster"):
            preflight.validate_format_diversity(mutated, labels)

    def test_formato_rejeita_ausencia_total_de_interrogacao_fora_de_abster(self):
        sample, manifest, _ = load_v2()
        labels = preflight.gold_by_id(manifest)
        mutated = deepcopy(sample["cases"])
        for case in mutated:
            if labels[case["id"]] != "abster":
                case["text"] = case["text"].replace("?", ".")
        with self.assertRaisesRegex(ValueError, "formato exclusivo de abster"):
            preflight.validate_format_diversity(mutated, labels)

    def test_question_required_e_comportamento_de_saida_nao_gramatica(self):
        sample, manifest, _ = load_v2()
        labels = preflight.gold_by_id(manifest)
        mutated = deepcopy(sample["cases"])
        for case in mutated:
            if case["id"] == "Y031":
                case["text"] = case["text"].replace("?", ".")
        preflight.validate_policy_boundary(manifest)
        self.assertEqual(preflight.validate_format_diversity(mutated, labels)[1]["abster"], 2)

    def test_consulta_com_escopo_ausente_e_rejeitada_pela_guarda_de_limite(self):
        _, manifest, _ = load_v2()
        mutated = deepcopy(manifest)
        entry = next(item for item in mutated["adjudications"] if item["id"] == "Y023")
        entry["facts"].append("missing_decisive_scope")
        with self.assertRaisesRegex(ValueError, "consulta delimitada marcada como sem escopo"):
            preflight.validate_policy_boundary(mutated)

    def test_contagem_negativa_morre_na_guarda_de_schema(self):
        sample, manifest, rule = load_v2()
        mutated = deepcopy(rule)
        mutated["rules"][0]["features"][0]["positive"] = -1
        with self.assertRaisesRegex(ValueError, "contagem fora do intervalo"):
            preflight.validate_rule_schema(mutated, manifest)
        self.assertIsNotNone(sample)

