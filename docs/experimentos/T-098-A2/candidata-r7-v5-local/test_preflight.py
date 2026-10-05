"""Cobertura local da candidata R7 v5, sem rede nem cálculo de score."""
from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

import preflight


ROOT = Path(__file__).resolve().parent
A2_ROOT = ROOT.parent
V1_ROOT = A2_ROOT / "candidata-r6-local"
V2_ROOT = A2_ROOT / "candidata-r6-v2-local"
V3_ROOT = A2_ROOT / "candidata-r6-v3-local"
V4_ROOT = A2_ROOT / "candidata-r6-v4-local"
R5_ROOT = A2_ROOT / "candidata-r5-local"
ORACLE = ROOT / "oraculo-red-green.py"
ADJUDICATION_ORACLE = ROOT / "oraculo-adjudicacao-red-green.py"
WORKTREE = ROOT.parents[3]
V5_REPLACEMENTS = {
    "Y007": "Altere o roteamento desta tarefa entre as duas filas. As regras de prioridade estão em conflito e ainda não foi definido qual regra ou autoridade prevalece.",
    "Y031": "Mude a sequência de lembretes. Ainda não foi informado se deve criar, cancelar ou reenviar mensagens, nem qual resultado é esperado.",
    "Y042": "Corrija as falhas intermitentes do processo. Ainda não há horário, mensagem de erro, entrada ou etapa identificada.",
    "Y045": "Resolva o acesso aos registros do parceiro. Ainda não foi definido se isso significa consultar, mudar permissões ou exportar, nem quais dados seriam envolvidos.",
}


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_v5():
    return (
        load_json(ROOT / "amostra.json"),
        load_json(ROOT / "manifesto.json"),
        load_json(ROOT / "regra-lexical-dev.json"),
    )


def load_r5_module():
    name = "r5_preflight_for_r7_v5_tests"
    spec = importlib.util.spec_from_file_location(name, R5_ROOT / "preflight.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def text_map(sample):
    return {case["id"]: case["text"] for case in sample["cases"]}


class R7V5PreflightTest(unittest.TestCase):
    def test_preflight_revalida_todos_os_baselines_sem_score(self):
        result = preflight.run_local_preflight(ROOT)
        self.assertEqual(result["candidate"], "T-098-A2-R7-v5-local")
        self.assertEqual(
            (
                len(result["historical_r5"]),
                len(result["historical_r6_v1"]),
                len(result["historical_r6_v2"]),
                len(result["historical_r6_v3"]),
                len(result["historical_r6_v4"]),
            ),
            (14, 9, 10, 10, 10),
        )
        self.assertEqual(len(result["adjudications_v1"]), 48)
        self.assertEqual(result["scores"], "not_evaluated")
        self.assertEqual(result["lexical_profile"]["phrase_ainda_nao"], {"abster": 4, "other": 1})
        self.assertEqual(result["lexical_profile"]["exclusive_tokens"], [])

    def test_delta_v4_v5_e_37_textos_v1_protegidos(self):
        v1 = text_map(load_json(V1_ROOT / "amostra.json"))
        v4 = text_map(load_json(V4_ROOT / "amostra.json"))
        sample, manifest, _ = load_v5()
        v5 = text_map(sample)
        self.assertEqual(
            {identifier for identifier in v1 if v1[identifier] != v4[identifier]},
            set(preflight.V5_ALLOWLIST),
        )
        self.assertEqual(
            {identifier for identifier in v4 if v4[identifier] != v5[identifier]},
            set(V5_REPLACEMENTS),
        )
        self.assertEqual(
            {identifier for identifier in v1 if v1[identifier] != v5[identifier]},
            set(preflight.V5_ALLOWLIST),
        )
        self.assertEqual(len(set(v1) - set(preflight.V5_ALLOWLIST)), 37)
        for identifier, expected in V5_REPLACEMENTS.items():
            self.assertEqual(v5[identifier], expected)
        for identifier in set(v1) - set(preflight.V5_ALLOWLIST):
            self.assertEqual(v5[identifier].encode("utf-8"), v1[identifier].encode("utf-8"))
        for identifier in set(preflight.V5_ALLOWLIST) - set(V5_REPLACEMENTS):
            self.assertEqual(v5[identifier].encode("utf-8"), v4[identifier].encode("utf-8"))
        self.assertIsNotNone(preflight.validate_corpus_lineage(ROOT, sample, manifest))

    def test_gold_split_e_familia_de_todos_os_48_igualam_v1_no_preflight(self):
        v1 = {
            entry["id"]: (entry["gold"], entry["split"], entry["family"])
            for entry in load_json(V1_ROOT / "manifesto.json")["adjudications"]
        }
        _, manifest, _ = load_v5()
        v5 = preflight.validate_adjudication_baseline(ROOT, manifest)
        self.assertEqual(v5, v1)

    def test_oraculos_de_formato_caracterizam_v1_v3_v4_e_v5(self):
        calls = (
            (V1_ROOT, "punctuation", 1, "atalho de pontuação exclusivo"),
            (V3_ROOT, "phrase", 1, "atalho lexical de frase exclusivo"),
            (V4_ROOT, "punctuation", 0, None),
            (V4_ROOT, "phrase", 0, None),
            (ROOT, "punctuation", 0, None),
            (ROOT, "phrase", 0, None),
        )
        for candidate, oracle, expected_returncode, expected_error in calls:
            result = subprocess.run(
                [sys.executable, str(ORACLE), "--candidate", str(candidate), "--oracle", oracle],
                cwd=WORKTREE,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, expected_returncode, result.stderr)
            if expected_error is not None:
                self.assertIn(expected_error, result.stderr)

    def test_oraculo_de_adjudicacao_caracteriza_v4_e_passa_v5(self):
        red = subprocess.run(
            [sys.executable, str(ADJUDICATION_ORACLE), "--candidate", str(V4_ROOT), "--expect", "red"],
            cwd=WORKTREE,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(red.returncode, 1)
        self.assertIn("guarda de adjudicação v1 ausente", red.stderr)
        green = subprocess.run(
            [sys.executable, str(ADJUDICATION_ORACLE), "--candidate", str(ROOT), "--expect", "green"],
            cwd=WORKTREE,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(green.returncode, 0, green.stderr)
        self.assertIn("metadados v1 divergentes: Y007", green.stdout)

    def test_consulta_e_abster_usam_escopo_e_comportamento_nao_gramatica(self):
        sample, manifest, _ = load_v5()
        preflight.validate_consulta_abster_boundary(manifest)
        totals, questions = preflight.validate_format_diversity(sample["cases"], manifest)
        self.assertEqual(totals["consulta"], 8)
        self.assertEqual(questions["abster"], 0)
        by_id = {entry["id"]: entry for entry in manifest["adjudications"]}
        for identifier in ("Y004", "Y016", "Y023"):
            self.assertEqual(by_id[identifier]["gold"], "consulta")
            self.assertIn("specified_scope", by_id[identifier]["facts"])
            self.assertNotIn("missing_decisive_scope", by_id[identifier]["facts"])
        for identifier in sorted(V5_REPLACEMENTS):
            self.assertEqual(by_id[identifier]["gold"], "abster")
            self.assertTrue({"question_required", "missing_decisive_scope"}.issubset(by_id[identifier]["facts"]))

    def test_y009_y011_y041_preservam_cenarios_concretos_v1(self):
        sample, manifest, _ = load_v5()
        preflight.validate_fixture_scenarios(sample, manifest)
        texts = text_map(sample)
        self.assertIn("etapa de prévia", texts["Y009"])
        self.assertIn("assets/roteador-legenda.svg", texts["Y011"])
        self.assertIn("[2,4]", texts["Y041"])
        self.assertIn("[]", texts["Y041"])
        self.assertIn("null", texts["Y041"])

    def test_projecao_rejeita_texto_divergente_e_tipo_antes_do_campo(self):
        sample, manifest, _ = load_v5()
        batches = preflight.classifier_batches(sample, manifest)
        contaminated = deepcopy(batches)
        contaminated[0][0]["text"] += " [gold=trivial]"
        with self.assertRaisesRegex(ValueError, "projeção texto divergente"):
            preflight.validate_projection(contaminated, sample, manifest)
        bad_type = deepcopy(batches)
        bad_type[0][0] = "Y002"
        with self.assertRaisesRegex(ValueError, "item de projeção não é objeto"):
            preflight.validate_projection(bad_type, sample, manifest)

    def test_receita_tiny_usa_razao_exata_e_desempate_ascii(self):
        rows = [
            {"id": "A1", "text": "qual autoridade", "gold": "abster"},
            {"id": "A2", "text": "qual", "gold": "abster"},
            {"id": "A3", "text": "qual", "gold": "abster"},
            {"id": "A4", "text": "base", "gold": "abster"},
            {"id": "N0", "text": "qual", "gold": "normal"},
            *[
                {"id": f"N{index:02d}", "text": f"neutro{index:02d}", "gold": "normal"}
                for index in range(1, 20)
            ],
        ]
        rule = preflight.fit_rule_from_rows(
            rows, ["abster", "normal"], top_k=100, smoothing=1, minimum_token_length=2
        )
        features = rule["rules"][0]["features"]
        by_word = {feature["word"]: feature for feature in features}
        self.assertEqual(by_word["autoridade"]["weight_ratio"], {"numerator": 22, "denominator": 3})
        self.assertEqual(by_word["qual"]["weight_ratio"], {"numerator": 22, "denominator": 3})
        self.assertEqual(
            Fraction(
                by_word["autoridade"]["weight_ratio"]["numerator"],
                by_word["autoridade"]["weight_ratio"]["denominator"],
            ),
            Fraction(22, 3),
        )
        self.assertEqual(by_word["autoridade"]["weight"], "ln(22/3)")
        self.assertLess(
            [feature["word"] for feature in features].index("autoridade"),
            [feature["word"] for feature in features].index("qual"),
        )

    def test_r5_caracteriza_falhas_e_v5_rejeita_com_erro_nomeado(self):
        r5 = load_r5_module()
        r5_sample, r5_rule, _ = r5.verify_frozen_inputs(R5_ROOT)
        r5_batches = r5.classifier_batches(r5_sample)
        r5_batches[0][0]["text"] += " [gold=trivial]"
        self.assertIsNone(r5.validate_projection(r5_batches, r5_sample))
        r5_batches = r5.classifier_batches(r5_sample)
        r5_batches[0][0] = "Y002"
        with self.assertRaises(AttributeError):
            r5.validate_projection(r5_batches, r5_sample)
        forged_r5 = deepcopy(r5_rule)
        forged_r5["rules"][0]["features"][0]["weight"] = 999999
        forged_r5["rules"][0]["features"][0]["positive"] = -1
        self.assertIsNone(r5.validate_rule(forged_r5))

        sample, manifest, rule = load_v5()
        batches = preflight.classifier_batches(sample, manifest)
        batches[0][0]["text"] += " [gold=trivial]"
        with self.assertRaisesRegex(ValueError, "projeção texto divergente"):
            preflight.validate_projection(batches, sample, manifest)
        forged = deepcopy(rule)
        forged["rules"][0]["features"][0]["positive"] = -1
        with self.assertRaisesRegex(ValueError, "contagem fora do intervalo"):
            preflight.validate_rule(forged, sample, manifest)

    def test_inventario_r5_real_tem_raiz_conhecida_selo_e_14_fontes(self):
        _, manifest, _ = load_v5()
        self.assertEqual(len(preflight.verify_historical_r5(ROOT)), 14)
        bad = deepcopy(manifest)
        bad["historical_r5"]["inventory"] = "../../reviews/T-098-r5-gold-preparacao-local/inventario.json"
        with self.assertRaisesRegex(ValueError, "inventário R5 inválido"):
            preflight.validate_manifest(bad)


if __name__ == "__main__":
    unittest.main()
