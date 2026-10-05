"""Mutações em memória da R6; as fontes congeladas não são regravadas."""

from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent


def load_preflight():
    spec = importlib.util.spec_from_file_location("t098_r6_preflight_mutations", ROOT / "preflight.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class MutationTest(unittest.TestCase):
    def setUp(self):
        self.preflight = load_preflight()
        self.sample, self.manifest, self.rule = self.preflight.load_inputs(ROOT)

    def reject(self, message, callback):
        with self.assertRaisesRegex(ValueError, message):
            callback()

    def test_texto_projetado_alterado_e_rejeitado_antes_de_qualquer_score(self):
        batches = self.preflight.classifier_batches(self.sample, self.manifest)
        batches[2][4]["text"] = batches[2][4]["text"] + " [gold=trivial]"
        self.reject("projeção texto divergente", lambda: self.preflight.validate_projection(batches, self.sample, self.manifest))

    def test_objeto_projetado_com_campo_extra_e_rejeitado(self):
        batches = self.preflight.classifier_batches(self.sample, self.manifest)
        batches[3][1]["reason"] = "não deve cruzar a fronteira"
        self.reject("campos da projeção inválidos", lambda: self.preflight.validate_projection(batches, self.sample, self.manifest))

    def test_swap_de_gold_e_family_tem_causas_distintas(self):
        gold = copy.deepcopy(self.manifest)
        by_id = {case["id"]: case for case in gold["adjudications"]}
        by_id["Y012"]["gold"], by_id["Y009"]["gold"] = by_id["Y009"]["gold"], by_id["Y012"]["gold"]
        self.reject("adjudicação Y009 diverge da política", lambda: self.preflight.validate_adjudications(gold))

        family = copy.deepcopy(self.manifest)
        next(case for case in family["adjudications"] if case["id"] == "Y041")["family"] = "protocolo"
        self.reject("família divergente: Y041", lambda: self.preflight.validate_manifest(family))

    def test_swap_de_split_tem_guarda_de_lote_sem_usar_digest(self):
        manifest = copy.deepcopy(self.manifest)
        by_id = {case["id"]: case for case in manifest["adjudications"]}
        by_id["Y006"]["split"], by_id["Y013"]["split"] = by_id["Y013"]["split"], by_id["Y006"]["split"]
        self.reject("split incompatível com lote: Y006", lambda: self.preflight.validate_manifest(manifest))

    def test_regra_com_nan_e_contagem_negativa_falham_por_schema(self):
        nan_rule = copy.deepcopy(self.rule)
        nan_rule["rules"][1]["features"][0]["weight"] = float("nan")
        self.reject("peso não finito", lambda: self.preflight.validate_rule_schema(nan_rule, self.manifest))

        negative = copy.deepcopy(self.rule)
        negative["rules"][1]["features"][0]["negative"] = -1
        self.reject("contagem fora do intervalo", lambda: self.preflight.validate_rule_schema(negative, self.manifest))

    def test_snapshot_e_ultima_linha_de_defesa_de_arquivo(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["sample"]["sha256"] = "0" * 64
        self.reject("snapshot da amostra divergente", lambda: self.preflight.verify_frozen_snapshot(ROOT, self.sample, manifest, self.rule))


if __name__ == "__main__":
    unittest.main()
