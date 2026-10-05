"""RED semântico contra a R6 v1: formato não pode identificar abster sozinho."""
from __future__ import annotations

import json
from pathlib import Path
import unittest

import preflight

ROOT = Path(__file__).resolve().parent
V1_ROOT = ROOT.parent / "candidata-r6-local"


class OriginalFormatRedTest(unittest.TestCase):
    def test_r6_v1_nao_pode_ter_formato_exclusivo_de_abster(self):
        cases = json.loads((V1_ROOT / "amostra.json").read_text(encoding="utf-8"))["cases"]
        manifest = json.loads((ROOT / "manifesto.json").read_text(encoding="utf-8"))
        totals, questions = preflight.format_profile(cases, manifest)
        self.assertEqual(questions["abster"], totals["abster"])
        self.assertEqual(sum(value for gold, value in questions.items() if gold != "abster"), 0)
