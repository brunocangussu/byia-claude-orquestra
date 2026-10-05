"""Contratos locais da candidata R6; não executam rede nem modelos."""

from __future__ import annotations

import importlib.util
import copy
import math
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent


def load_preflight():
    spec = importlib.util.spec_from_file_location("t098_r6_preflight", ROOT / "preflight.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class PreflightTest(unittest.TestCase):
    def test_projecao_tem_contrato_dedicado(self):
        self.assertTrue(callable(load_preflight().validate_projection))

    def setUp(self):
        self.preflight = load_preflight()
        self.sample, self.manifest, self.rule = self.preflight.load_inputs(ROOT)

    def reject(self, message, callback):
        with self.assertRaisesRegex(ValueError, message):
            callback()

    def test_preflight_local_valida_sem_score_de_reserved(self):
        result = self.preflight.run_local_preflight(ROOT)
        self.assertEqual(result["candidate"], "T-098-A2-R6-local")
        self.assertEqual(result["scores"], "not_evaluated")
        self.assertEqual([len(batch) for batch in result["batches"]], [12, 12, 12, 12])

    def test_projecao_e_igual_ao_texto_fonte_em_utf8(self):
        batches = self.preflight.classifier_batches(self.sample, self.manifest)
        batches[0][0]["text"] += " [gold=trivial]"
        self.reject("projeção texto divergente", lambda: self.preflight.validate_projection(batches, self.sample, self.manifest))

    def test_projecao_rejeita_item_nao_objeto_sem_attribute_error(self):
        batches = self.preflight.classifier_batches(self.sample, self.manifest)
        batches[0][0] = "Y002"
        self.reject("item de projeção não é objeto", lambda: self.preflight.validate_projection(batches, self.sample, self.manifest))

    def test_projecao_rejeita_gold_ou_razao_no_transporte(self):
        batches = self.preflight.classifier_batches(self.sample, self.manifest)
        batches[0][0]["gold"] = "trivial"
        self.reject("campos da projeção inválidos", lambda: self.preflight.validate_projection(batches, self.sample, self.manifest))

    def test_projecao_rejeita_ordem_e_identidade_trocadas(self):
        batches = self.preflight.classifier_batches(self.sample, self.manifest)
        batches[0][0], batches[0][1] = batches[0][1], batches[0][0]
        self.reject("ordem ou identidade da projeção divergente", lambda: self.preflight.validate_projection(batches, self.sample, self.manifest))

    def test_adjudicacao_trocada_mantendo_contagens_falha_na_politica(self):
        manifest = copy.deepcopy(self.manifest)
        by_id = {case["id"]: case for case in manifest["adjudications"]}
        by_id["Y003"]["gold"], by_id["Y001"]["gold"] = by_id["Y001"]["gold"], by_id["Y003"]["gold"]
        self.reject("adjudicação Y001 diverge da política", lambda: self.preflight.validate_adjudications(manifest))

    def test_taxonomia_e_split_sao_guardas_antes_do_snapshot(self):
        family_manifest = copy.deepcopy(self.manifest)
        next(case for case in family_manifest["adjudications"] if case["id"] == "Y002")["family"] = "schema-persistente"
        self.reject("família divergente: Y002", lambda: self.preflight.validate_manifest(family_manifest))

        split_manifest = copy.deepcopy(self.manifest)
        by_id = {case["id"]: case for case in split_manifest["adjudications"]}
        by_id["Y002"]["split"], by_id["Y014"]["split"] = by_id["Y014"]["split"], by_id["Y002"]["split"]
        self.reject("split incompatível com lote: Y002", lambda: self.preflight.validate_manifest(split_manifest))

    def test_texto_da_amostra_tem_guarda_por_id_antes_do_selo_geral(self):
        sample = copy.deepcopy(self.sample)
        next(case for case in sample["cases"] if case["id"] == "Y006")["text"] = "texto histórico substituído"
        self.reject("texto da amostra diverge do manifesto: Y006", lambda: self.preflight.validate_sample(sample, self.manifest))

    def test_receita_lexical_tiny_e_desempate_sao_calculados(self):
        rows = [
            {"id": "A1", "text": "alfa comum", "gold": "x"},
            {"id": "A2", "text": "alfa", "gold": "x"},
            {"id": "B1", "text": "beta comum", "gold": "y"},
            {"id": "B2", "text": "beta", "gold": "y"},
        ]
        rule = self.preflight.fit_rule_from_rows(rows, ["x", "y"], top_k=2)
        x_features = rule["rules"][0]["features"]
        self.assertEqual([feature["word"] for feature in x_features], ["alfa", "comum"])
        self.assertEqual((x_features[0]["positive"], x_features[0]["negative"]), (2, 0))
        self.assertAlmostEqual(x_features[0]["weight"], math.log(3), places=12)
        self.assertAlmostEqual(x_features[1]["weight"], 0.0, places=12)

    def test_regra_real_e_recomputada_somente_do_dev(self):
        dev = self.preflight.training_projection(self.sample, self.manifest)
        self.assertEqual(len(dev), 24)
        records = {case["id"]: case for case in self.manifest["adjudications"]}
        self.assertTrue(all(records[row["id"]]["split"] == "dev" for row in dev))
        self.assertEqual(self.preflight.fit_rule(self.sample, self.manifest), self.rule)

    def test_schema_lexical_rejeita_numeros_forjados_e_tokens_invalidos(self):
        forged = copy.deepcopy(self.rule)
        forged["rules"][0]["features"][0]["weight"] = 999999
        self.reject("derivação da regra divergente", lambda: self.preflight.validate_rule(forged, self.sample, self.manifest))

        negative = copy.deepcopy(self.rule)
        negative["rules"][0]["features"][0]["positive"] = -1
        self.reject("contagem fora do intervalo", lambda: self.preflight.validate_rule_schema(negative, self.manifest))

        single_letter = copy.deepcopy(self.rule)
        single_letter["rules"][0]["features"][0]["word"] = "a"
        self.reject("token inválido", lambda: self.preflight.validate_rule_schema(single_letter, self.manifest))

    def test_historico_r5_tem_quatorze_fontes_intactas(self):
        historical = self.preflight.verify_historical_r5(ROOT)
        self.assertEqual(len(historical), 14)


if __name__ == "__main__":
    unittest.main()
