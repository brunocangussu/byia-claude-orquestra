"""Mutações isoladas das causas confirmadas na candidata R6 v4."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

import preflight


ROOT = Path(__file__).resolve().parent
V1_ROOT = ROOT.parent / "candidata-r6-local"
V2_ROOT = ROOT.parent / "candidata-r6-v2-local"
V3_ROOT = ROOT.parent / "candidata-r6-v3-local"


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_v4():
    return (
        load_json(ROOT / "amostra.json"),
        load_json(ROOT / "manifesto.json"),
        load_json(ROOT / "regra-lexical-dev.json"),
    )


class R6V4MutationTest(unittest.TestCase):
    def test_atalho_original_8_por_8_versus_0_por_40_morre_na_guarda_de_formato(self):
        cases = load_json(V1_ROOT / "amostra.json")["cases"]
        _, manifest, _ = load_v4()
        with self.assertRaisesRegex(ValueError, "formato exclusivo de abster"):
            preflight.validate_format_diversity(cases, manifest)

    def test_atalho_de_frase_v3_morre_na_guarda_lexical_especifica(self):
        cases = load_json(V3_ROOT / "amostra.json")["cases"]
        _, manifest, _ = load_v4()
        with self.assertRaisesRegex(ValueError, "atalho lexical de frase exclusivo de abster"):
            preflight.lexical_shortcut_profile(cases, manifest)

    def test_texto_editorial_y028_da_v2_morre_antes_do_selo(self):
        sample, manifest, _ = load_v4()
        v2 = {case["id"]: case["text"] for case in load_json(V2_ROOT / "amostra.json")["cases"]}
        mutated = deepcopy(sample)
        next(case for case in mutated["cases"] if case["id"] == "Y028")["text"] = v2["Y028"]
        with self.assertRaisesRegex(ValueError, "texto do corpus divergente: Y028"):
            preflight.validate_corpus_lineage(ROOT, mutated, manifest)

    def test_troca_y041_e_um_dos_37_textos_protegidos_morrem_antes_do_selo(self):
        sample, manifest, _ = load_v4()
        v2 = {case["id"]: case["text"] for case in load_json(V2_ROOT / "amostra.json")["cases"]}

        y041 = deepcopy(sample)
        next(case for case in y041["cases"] if case["id"] == "Y041")["text"] = v2["Y041"]
        with self.assertRaisesRegex(ValueError, "cenário protegido divergente: Y041"):
            preflight.validate_fixture_scenarios(y041, manifest)
        with self.assertRaisesRegex(ValueError, "texto do corpus divergente: Y041"):
            preflight.validate_corpus_lineage(ROOT, y041, manifest)

        y009 = deepcopy(sample)
        next(case for case in y009["cases"] if case["id"] == "Y009")["text"] = v2["Y009"]
        with self.assertRaisesRegex(ValueError, "cenário protegido divergente: Y009"):
            preflight.validate_fixture_scenarios(y009, manifest)
        with self.assertRaisesRegex(ValueError, "texto do corpus divergente: Y009"):
            preflight.validate_corpus_lineage(ROOT, y009, manifest)

    def test_consulta_com_lacuna_decisiva_morre_no_limite_sem_gramatica(self):
        _, manifest, _ = load_v4()
        mutated = deepcopy(manifest)
        entry = next(item for item in mutated["adjudications"] if item["id"] == "Y004")
        entry["facts"].append("missing_decisive_scope")
        with self.assertRaisesRegex(ValueError, "consulta marcada com escopo ausente: Y004"):
            preflight.validate_consulta_abster_boundary(mutated)

    def test_mutacao_formula_float_legada_morre_na_politica(self):
        _, manifest, rule = load_v4()
        legacy = deepcopy(rule)
        legacy["algorithm"] = "presence_top5_log_odds_v2"
        with self.assertRaisesRegex(ValueError, "origem declarada da regra inválida"):
            preflight.validate_rule_schema(legacy, manifest)

    def test_mutacao_ranking_float_legado_morre_no_schema_exato(self):
        _, manifest, rule = load_v4()
        legacy = deepcopy(rule)
        feature = legacy["rules"][0]["features"][0]
        feature.pop("weight_ratio")
        feature["weight"] = 999999.0
        with self.assertRaisesRegex(ValueError, "feature inválida"):
            preflight.validate_rule_schema(legacy, manifest)

    def test_troca_da_ordem_de_empate_morre_na_ordenacao_exata(self):
        _, manifest, rule = load_v4()
        mutated = deepcopy(rule)
        features = mutated["rules"][0]["features"]
        features[1], features[2] = features[2], features[1]
        with self.assertRaisesRegex(ValueError, "ordem de desempate inválida"):
            preflight.validate_rule_schema(mutated, manifest)

    def test_inventario_inexistente_e_escape_de_raiz_morrem_com_erro_nomeado(self):
        _, manifest, _ = load_v4()
        old_relative_path = "../../reviews/T-098-r5-gold-preparacao-local/inventario.json"
        for bad_path in (old_relative_path, "../fora.json", "/tmp/fake.json"):
            mutated = deepcopy(manifest)
            mutated["historical_r5"]["inventory"] = bad_path
            with self.assertRaisesRegex(ValueError, "inventário R5 inválido"):
                preflight.validate_manifest(mutated)

    def test_relaxamentos_estruturais_relevantes_morrem_antes_de_indexar(self):
        _, manifest, _ = load_v4()
        mutations = (
            (
                lambda value: value["rule"].pop("algorithm"),
                "schema da política da regra inválido",
            ),
            (
                lambda value: value["historical_r5"].pop("state"),
                "schema histórico R5 inválido",
            ),
            (
                lambda value: value.__setitem__("classes", ["abster", "alto_risco", "consulta", "normal", "pequeno", 7]),
                "classes literais inválidas",
            ),
            (
                lambda value: value["rule"].__setitem__("sha256", "bad"),
                "selo da regra inválido",
            ),
        )
        for mutate, message in mutations:
            candidate = deepcopy(manifest)
            mutate(candidate)
            with self.assertRaisesRegex(ValueError, message):
                preflight.validate_manifest(candidate)


if __name__ == "__main__":
    unittest.main()
