"""Testes unitários locais da candidata R6 v2, sem modelos nem rede."""
from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import unittest

import preflight

ROOT = Path(__file__).resolve().parent
A2_ROOT = ROOT.parent
R5_ROOT = A2_ROOT / "candidata-r5-local"
R6_V1_ROOT = A2_ROOT / "candidata-r6-local"


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_r5_module():
    module_name = "r5_preflight_for_r6_v2_tests"
    spec = importlib.util.spec_from_file_location(module_name, R5_ROOT / "preflight.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def load_v2():
    return load_json(ROOT / "amostra.json"), load_json(ROOT / "manifesto.json"), load_json(ROOT / "regra-lexical-dev.json")


class R6V2PreflightTest(unittest.TestCase):
    def test_preflight_completo_local(self):
        result = preflight.run_local_preflight(ROOT)
        self.assertEqual(result["totals"], {name: 8 for name in ("trivial", "pequeno", "normal", "consulta", "alto_risco", "abster")})
        self.assertEqual(result["questions"]["abster"], 3)
        self.assertEqual(result["questions"]["consulta"], 6)

    def test_oraculo_independente_confirma_formato_r6_v1_e_diversidade_v2(self):
        v1_sample = load_json(R6_V1_ROOT / "amostra.json")
        v1_manifest = load_json(R6_V1_ROOT / "manifesto.json")
        v1_labels = {entry["id"]: entry["gold"] for entry in v1_manifest["adjudications"]}
        v1_abster = [case["text"] for case in v1_sample["cases"] if v1_labels[case["id"]] == "abster"]
        v1_other = [case["text"] for case in v1_sample["cases"] if v1_labels[case["id"]] != "abster"]
        self.assertEqual(sum("?" in text for text in v1_abster), 8)
        self.assertEqual(sum("?" in text for text in v1_other), 0)

        sample, manifest, _ = load_v2()
        labels = {entry["id"]: entry["gold"] for entry in manifest["adjudications"]}
        v2_abster = [case["text"] for case in sample["cases"] if labels[case["id"]] == "abster"]
        v2_other = [case["text"] for case in sample["cases"] if labels[case["id"]] != "abster"]
        self.assertEqual(sum("?" in text for text in v2_abster), 3)
        self.assertEqual(sum("?" in text for text in v2_other), 6)
        self.assertEqual(preflight.validate_format_diversity(sample["cases"], labels)[1]["consulta"], 6)

    def test_consulta_e_abster_sao_definidos_por_escopo_e_saida(self):
        _, manifest, _ = load_v2()
        preflight.validate_policy_boundary(manifest)
        by_id = {entry["id"]: entry for entry in manifest["adjudications"]}
        self.assertEqual(by_id["Y023"]["gold"], "consulta")
        self.assertEqual(by_id["Y023"]["response_behavior"], "answer_information")
        self.assertNotIn("missing_decisive_scope", by_id["Y023"]["facts"])
        self.assertEqual(by_id["Y028"]["gold"], "abster")
        self.assertEqual(by_id["Y028"]["response_behavior"], "ask_clarifying_question")
        self.assertIn("missing_decisive_scope", by_id["Y028"]["facts"])

    def test_fit_tiny_hand_checked(self):
        cases = [
            {"id": "A1", "text": "alfa comum"},
            {"id": "A2", "text": "alfa sol"},
            {"id": "B1", "text": "beta comum"},
            {"id": "B2", "text": "beta lua"}
        ]
        labels = {"A1": "a", "A2": "a", "B1": "b", "B2": "b"}
        rows = preflight.derive_rule_rows(cases, labels, ["a", "b"], {"top_k": 2, "smoothing": 1})
        self.assertEqual(rows, [
            {"class": "a", "features": [
                {"word": "alfa", "positive": 2, "negative": 0, "weight": 1.098612},
                {"word": "sol", "positive": 1, "negative": 0, "weight": 0.693147}
            ]},
            {"class": "b", "features": [
                {"word": "beta", "positive": 2, "negative": 0, "weight": 1.098612},
                {"word": "lua", "positive": 1, "negative": 0, "weight": 0.693147}
            ]}
        ])

    def test_r5_aceita_texto_alterado_v2_rejeita_com_erro_nomeado(self):
        r5 = load_r5_module()
        r5_sample, _, _ = r5.verify_frozen_inputs(R5_ROOT)
        r5_batches = r5.classifier_batches(r5_sample)
        r5_batches[0][0]["text"] += " [gold=trivial]"
        self.assertIsNone(r5.validate_projection(r5_batches, r5_sample))

        sample, manifest, _ = load_v2()
        batches = preflight.classifier_batches(sample, manifest)
        batches[0][0]["text"] += " [gold=trivial]"
        with self.assertRaisesRegex(ValueError, "projeção texto divergente"):
            preflight.validate_projection(batches, sample, manifest)

    def test_r5_acessa_tipo_antes_do_campo_v2_rejeita_com_erro_nomeado(self):
        r5 = load_r5_module()
        r5_sample, _, _ = r5.verify_frozen_inputs(R5_ROOT)
        r5_batches = r5.classifier_batches(r5_sample)
        r5_batches[0][0] = "Y002"
        with self.assertRaises(AttributeError):
            r5.validate_projection(r5_batches, r5_sample)

        sample, manifest, _ = load_v2()
        batches = preflight.classifier_batches(sample, manifest)
        batches[0][0] = "Y002"
        with self.assertRaisesRegex(ValueError, "item de projeção não é objeto"):
            preflight.validate_projection(batches, sample, manifest)

    def test_r5_aceita_regra_numerica_forjada_v2_rejeita_derivacao(self):
        r5 = load_r5_module()
        _, r5_rule, _ = r5.verify_frozen_inputs(R5_ROOT)
        r5_forged = deepcopy(r5_rule)
        r5_forged["rules"][0]["features"][0]["weight"] = 999999
        r5_forged["rules"][0]["features"][0]["positive"] = -1
        self.assertIsNone(r5.validate_rule(r5_forged))

        sample, manifest, rule = load_v2()
        forged = deepcopy(rule)
        forged["rules"][0]["features"][0]["weight"] = 999999
        with self.assertRaisesRegex(ValueError, "derivação da regra divergente"):
            preflight.validate_rule(forged, sample, manifest)

    def test_fixtures_preservam_y009_y011_y041(self):
        _, manifest, _ = load_v2()
        preflight.validate_fixtures(manifest)

