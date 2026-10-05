"""Mutações específicas do corpus R6 v3 e das guardas de limite."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

import preflight

ROOT = Path(__file__).resolve().parent
V1_ROOT = ROOT.parent / "candidata-r6-local"
V2_ROOT = ROOT.parent / "candidata-r6-v2-local"


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_v3():
    return (
        load_json(ROOT / "amostra.json"),
        load_json(ROOT / "manifesto.json"),
        load_json(ROOT / "regra-lexical-dev.json"),
    )


class R6V3MutationTest(unittest.TestCase):
    def test_atalho_original_8_por_8_versus_0_por_40_morre_na_guarda_de_formato(self):
        cases = load_json(V1_ROOT / "amostra.json")["cases"]
        _, manifest, _ = load_v3()
        with self.assertRaisesRegex(ValueError, "formato exclusivo de abster"):
            preflight.validate_format_diversity(cases, manifest)

    def test_texto_editorial_y028_da_v2_morre_antes_do_selo(self):
        sample, manifest, _ = load_v3()
        v2 = {case["id"]: case["text"] for case in load_json(V2_ROOT / "amostra.json")["cases"]}
        mutated = deepcopy(sample)
        next(case for case in mutated["cases"] if case["id"] == "Y028")["text"] = v2["Y028"]
        with self.assertRaisesRegex(ValueError, "texto do corpus divergente: Y028"):
            preflight.validate_corpus_lineage(ROOT, mutated, manifest)

    def test_troca_do_cenario_y041_morre_na_guarda_especifica_e_na_linhagem(self):
        sample, manifest, _ = load_v3()
        v2 = {case["id"]: case["text"] for case in load_json(V2_ROOT / "amostra.json")["cases"]}
        mutated = deepcopy(sample)
        next(case for case in mutated["cases"] if case["id"] == "Y041")["text"] = v2["Y041"]
        with self.assertRaisesRegex(ValueError, "cenário protegido divergente: Y041"):
            preflight.validate_fixture_scenarios(mutated, manifest)
        with self.assertRaisesRegex(ValueError, "texto do corpus divergente: Y041"):
            preflight.validate_corpus_lineage(ROOT, mutated, manifest)

    def test_alteracao_de_um_dos_37_textos_protegidos_morre_antes_do_selo(self):
        sample, manifest, _ = load_v3()
        v2 = {case["id"]: case["text"] for case in load_json(V2_ROOT / "amostra.json")["cases"]}
        mutated = deepcopy(sample)
        next(case for case in mutated["cases"] if case["id"] == "Y009")["text"] = v2["Y009"]
        with self.assertRaisesRegex(ValueError, "texto do corpus divergente: Y009"):
            preflight.validate_corpus_lineage(ROOT, mutated, manifest)

    def test_consulta_com_lacuna_decisiva_morre_na_guarda_de_limite(self):
        _, manifest, _ = load_v3()
        mutated = deepcopy(manifest)
        entry = next(item for item in mutated["adjudications"] if item["id"] == "Y023")
        entry["facts"].append("missing_decisive_scope")
        with self.assertRaisesRegex(ValueError, "consulta marcada com escopo ausente: Y023"):
            preflight.validate_consulta_abster_boundary(mutated)

    def test_contagem_negativa_morre_antes_da_derivacao(self):
        sample, manifest, rule = load_v3()
        mutated = deepcopy(rule)
        mutated["rules"][0]["features"][0]["positive"] = -1
        with self.assertRaisesRegex(ValueError, "contagem fora do intervalo"):
            preflight.validate_rule_schema(mutated, manifest)
        self.assertIsNotNone(sample)

