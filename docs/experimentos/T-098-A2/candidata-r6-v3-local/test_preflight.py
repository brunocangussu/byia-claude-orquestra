"""Cobertura da R6 v3: corpus v1, limites e regressões R5 sem rede."""
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
V1_ROOT = A2_ROOT / "candidata-r6-local"
V2_ROOT = A2_ROOT / "candidata-r6-v2-local"
R5_ROOT = A2_ROOT / "candidata-r5-local"
EXPECTED_REPLACEMENTS = {
    "Y004": "Quais verificações de expiração e assinatura o fluxo atual aplica antes de aceitar um token de acesso? Explique sem alterar arquivos.",
    "Y007": "Altere o roteamento desta tarefa entre as duas filas. As regras de prioridade estão em conflito e ainda não foi definido qual regra ou autoridade prevalece.",
    "Y016": "Quais opções de largura e formato o renderer atual aceita para produzir o comprovante? Não altere a composição nem gere um novo arquivo.",
    "Y023": "Qual conjunto de entradas e qual fórmula a métrica de tempo médio atual usa para chegar ao valor exibido? Não edite o cálculo.",
    "Y028": "Você pode ajustar o pacote para ficar certo antes da próxima janela? Ainda não foram definidos o artefato, a operação concreta e o destino.",
    "Y031": "Mude a sequência de lembretes. Ainda não foi informado se deve criar, cancelar ou reenviar mensagens, nem qual resultado é esperado.",
    "Y032": "Ajuste a compatibilidade da integração do parceiro. Sei apenas que ela mudou; ainda não há versão, campo afetado ou exemplo de mensagem.",
    "Y042": "Corrija as falhas intermitentes do processo. Ainda não há horário, mensagem de erro, entrada ou etapa identificada.",
    "Y043": "Trate o histórico antigo. O pedido ainda não define se deve consultar, arquivar, excluir ou restaurar, nem o período.",
    "Y044": "Você pode liberar a tarefa bloqueada? Ainda não foi informado quem pode autorizar, qual é o bloqueio e qual efeito deve ocorrer.",
    "Y045": "Resolva o acesso aos registros do parceiro. Ainda não foi definido se isso significa consultar, mudar permissões ou exportar, nem quais dados seriam envolvidos.",
}


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_v3():
    return load_json(ROOT / "amostra.json"), load_json(ROOT / "manifesto.json"), load_json(ROOT / "regra-lexical-dev.json")


def load_r5_module():
    name = "r5_preflight_for_r6_v3_tests"
    spec = importlib.util.spec_from_file_location(name, R5_ROOT / "preflight.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class R6V3PreflightTest(unittest.TestCase):
    def test_preflight_local_revalida_todos_os_baselines_sem_score(self):
        result = preflight.run_local_preflight(ROOT)
        self.assertEqual(result["candidate"], "T-098-A2-R6-v3-local")
        self.assertEqual(len(result["historical_r5"]), 14)
        self.assertEqual(len(result["historical_r6_v1"]), 9)
        self.assertEqual(len(result["historical_r6_v2"]), 10)
        self.assertEqual(result["scores"], "not_evaluated")
        self.assertEqual(result["questions"]["abster"], 2)
        self.assertEqual(sum(count for gold, count in result["questions"].items() if gold != "abster"), 3)

    def test_textos_derivam_da_v1_com_exatas_onze_trocas_e_37_protegidos(self):
        v1 = {case["id"]: case["text"] for case in load_json(V1_ROOT / "amostra.json")["cases"]}
        v3_sample, v3_manifest, _ = load_v3()
        v3 = {case["id"]: case["text"] for case in v3_sample["cases"]}
        changed = {identifier for identifier in v1 if v1[identifier] != v3[identifier]}
        self.assertEqual(changed, set(EXPECTED_REPLACEMENTS))
        self.assertEqual(len(set(v1) - changed), 37)
        for identifier, text in EXPECTED_REPLACEMENTS.items():
            self.assertEqual(v3[identifier], text)
        for identifier in set(v1) - changed:
            self.assertEqual(v3[identifier].encode("utf-8"), v1[identifier].encode("utf-8"))
        self.assertIsNotNone(preflight.validate_corpus_lineage(ROOT, v3_sample, v3_manifest))

    def test_gold_split_e_familia_sao_exatamente_os_da_v1(self):
        v1 = {entry["id"]: (entry["gold"], entry["split"], entry["family"]) for entry in load_json(V1_ROOT / "manifesto.json")["adjudications"]}
        _, manifest, _ = load_v3()
        v3 = {entry["id"]: (entry["gold"], entry["split"], entry["family"]) for entry in manifest["adjudications"]}
        self.assertEqual(v3, v1)

    def test_oraculo_independente_mata_atalho_de_formato_v1(self):
        v1_cases = load_json(V1_ROOT / "amostra.json")["cases"]
        _, manifest, _ = load_v3()
        totals, questions = preflight.format_profile(v1_cases, manifest)
        self.assertEqual((questions["abster"], sum(value for gold, value in questions.items() if gold != "abster")), (8, 0))
        with self.assertRaisesRegex(ValueError, "formato exclusivo de abster"):
            preflight.validate_format_diversity(v1_cases, manifest)

    def test_consulta_e_abster_olham_escopo_e_comportamento_nao_pontuacao(self):
        sample, manifest, _ = load_v3()
        preflight.validate_consulta_abster_boundary(manifest)
        by_id = {entry["id"]: entry for entry in manifest["adjudications"]}
        for identifier in ("Y004", "Y016", "Y023"):
            self.assertEqual(by_id[identifier]["gold"], "consulta")
            self.assertIn("specified_scope", by_id[identifier]["facts"])
        for identifier in ("Y007", "Y028", "Y031", "Y032", "Y042", "Y043", "Y044", "Y045"):
            self.assertEqual(by_id[identifier]["gold"], "abster")
            self.assertIn("missing_decisive_scope", by_id[identifier]["facts"])

        punctuation_changed = deepcopy(sample["cases"])
        for case in punctuation_changed:
            if case["id"] == "Y028":
                case["text"] = case["text"].replace("?", ".")
        self.assertEqual(preflight.validate_format_diversity(punctuation_changed, manifest)[1]["abster"], 1)

    def test_y009_y011_y041_preservam_os_cenarios_concretos_v1(self):
        sample, manifest, _ = load_v3()
        preflight.validate_fixture_scenarios(sample, manifest)
        text = {case["id"]: case["text"] for case in sample["cases"]}
        self.assertIn("etapa de prévia", text["Y009"])
        self.assertIn("assets/roteador-legenda.svg", text["Y011"])
        self.assertIn("[2,4]", text["Y041"])
        self.assertIn("[]", text["Y041"])
        self.assertIn("null", text["Y041"])

    def test_projecao_rejeita_texto_divergente_e_tipo_antes_do_campo(self):
        sample, manifest, _ = load_v3()
        batches = preflight.classifier_batches(sample, manifest)
        contaminated = deepcopy(batches)
        contaminated[0][0]["text"] += " alteração"
        with self.assertRaisesRegex(ValueError, "projeção texto divergente"):
            preflight.validate_projection(contaminated, sample, manifest)
        bad_type = deepcopy(batches)
        bad_type[0][0] = "Y002"
        with self.assertRaisesRegex(ValueError, "item de projeção não é objeto"):
            preflight.validate_projection(bad_type, sample, manifest)

    def test_receita_lexical_tiny_e_desempate_sao_calculados(self):
        rows = [
            {"id": "A1", "text": "alfa comum", "gold": "a"},
            {"id": "A2", "text": "alfa sol", "gold": "a"},
            {"id": "B1", "text": "beta comum", "gold": "b"},
            {"id": "B2", "text": "beta lua", "gold": "b"},
        ]
        rule = preflight.fit_rule_from_rows(rows, ["a", "b"], top_k=2, smoothing=1, minimum_token_length=2)
        self.assertEqual(rule["rules"], [
            {"class": "a", "features": [
                {"word": "alfa", "positive": 2, "negative": 0, "weight": 1.0986122886681096},
                {"word": "sol", "positive": 1, "negative": 0, "weight": 0.6931471805599453},
            ]},
            {"class": "b", "features": [
                {"word": "beta", "positive": 2, "negative": 0, "weight": 1.0986122886681096},
                {"word": "lua", "positive": 1, "negative": 0, "weight": 0.6931471805599453},
            ]},
        ])

    def test_r5_aceita_texto_contaminado_e_v3_rejeita_com_erro_nomeado(self):
        r5 = load_r5_module()
        r5_sample, _, _ = r5.verify_frozen_inputs(R5_ROOT)
        r5_batches = r5.classifier_batches(r5_sample)
        r5_batches[0][0]["text"] += " [gold=trivial]"
        self.assertIsNone(r5.validate_projection(r5_batches, r5_sample))

        sample, manifest, _ = load_v3()
        batches = preflight.classifier_batches(sample, manifest)
        batches[0][0]["text"] += " [gold=trivial]"
        with self.assertRaisesRegex(ValueError, "projeção texto divergente"):
            preflight.validate_projection(batches, sample, manifest)

    def test_r5_da_attributeerror_com_string_e_v3_da_erro_nomeado(self):
        r5 = load_r5_module()
        r5_sample, _, _ = r5.verify_frozen_inputs(R5_ROOT)
        r5_batches = r5.classifier_batches(r5_sample)
        r5_batches[0][0] = "Y002"
        with self.assertRaises(AttributeError):
            r5.validate_projection(r5_batches, r5_sample)

        sample, manifest, _ = load_v3()
        batches = preflight.classifier_batches(sample, manifest)
        batches[0][0] = "Y002"
        with self.assertRaisesRegex(ValueError, "item de projeção não é objeto"):
            preflight.validate_projection(batches, sample, manifest)

    def test_r5_aceita_regra_numerica_forjada_e_v3_rejeita_derivacao(self):
        r5 = load_r5_module()
        _, r5_rule, _ = r5.verify_frozen_inputs(R5_ROOT)
        forged_r5 = deepcopy(r5_rule)
        forged_r5["rules"][0]["features"][0]["weight"] = 999999
        forged_r5["rules"][0]["features"][0]["positive"] = -1
        self.assertIsNone(r5.validate_rule(forged_r5))

        sample, manifest, rule = load_v3()
        forged = deepcopy(rule)
        forged["rules"][0]["features"][0]["weight"] = 999999
        with self.assertRaisesRegex(ValueError, "derivação da regra divergente"):
            preflight.validate_rule(forged, sample, manifest)
