"""RED semântico do lote local 2, contra a R6 v1 imutável."""

from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent
R6_V1 = ROOT.parent / "candidata-r6-local"


def load_r6_v1():
    sample = json.loads((R6_V1 / "amostra.json").read_text(encoding="utf-8"))
    manifest = json.loads((R6_V1 / "manifesto.json").read_text(encoding="utf-8"))
    gold_by_id = {case["id"]: case["gold"] for case in manifest["adjudications"]}
    return sample["cases"], gold_by_id


def punctuation_profile(cases, gold_by_id):
    totals, questions = {}, {}
    for case in cases:
        gold = gold_by_id[case["id"]]
        totals[gold] = totals.get(gold, 0) + 1
        questions[gold] = questions.get(gold, 0) + int("?" in case["text"])
    return totals, questions


class SemanticRedTest(unittest.TestCase):
    def test_r6_v1_nao_pode_monopolizar_interrogacao_em_abster(self):
        cases, gold_by_id = load_r6_v1()
        totals, questions = punctuation_profile(cases, gold_by_id)
        self.assertEqual(questions["abster"], totals["abster"])
        self.assertEqual(sum(value for gold, value in questions.items() if gold != "abster"), 0)


if __name__ == "__main__":
    unittest.main()
