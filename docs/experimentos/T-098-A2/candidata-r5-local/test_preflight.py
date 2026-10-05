"""Contrato persistente da candidata R5, preservando R4 apenas como referência."""

import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
R4_ROOT = ROOT.parent / "candidata-r4"


def load_preflight(root):
    spec = importlib.util.spec_from_file_location(
        f"preflight_{root.name}", root / "preflight.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class PreflightTest(unittest.TestCase):
    """As lacunas antes aceitas por R4 agora devem reprovar por asserção."""

    def setUp(self):
        self.sample = json.loads((ROOT / "amostra.json").read_text())
        self.r4_sample = json.loads((R4_ROOT / "amostra.json").read_text())
        self.preflight = load_preflight(ROOT)

    def reject(self, change):
        sample = copy.deepcopy(self.sample)
        change(sample)
        with self.assertRaises(ValueError):
            self.preflight.classifier_batches(sample)

    def test_gold_trocado_preservando_contagens_deve_reprovar(self):
        def change(sample):
            cases = [
                case
                for case in sample["cases"]
            ]
            first, second = next(
                (left, right)
                for left in cases
                for right in cases
                if left["split"] == right["split"]
                and left["gold"] != right["gold"]
            )
            first["gold"], second["gold"] = second["gold"], first["gold"]

        self.reject(change)

    def test_texto_antigo_no_dev_deve_reprovar(self):
        old_text = next(
            case["text"]
            for case in self.r4_sample["cases"]
            if case["id"] == "Y006"
        )
        self.reject(
            lambda sample: next(
                case for case in sample["cases"] if case["id"] == "Y006"
            ).update(text=old_text)
        )

    def test_texto_antigo_no_reserved_deve_reprovar(self):
        identifier = next(
            case["id"]
            for case in self.sample["cases"]
            if case["split"] == "reserved"
        )
        old_text = next(
            case["text"] for case in self.r4_sample["cases"] if case["id"] == identifier
        )
        self.reject(
            lambda sample: next(
                case for case in sample["cases"] if case["id"] == identifier
            ).update(text=old_text)
        )

    def test_y006_sem_cenario_observavel_deve_reprovar(self):
        self.reject(
            lambda sample: next(
                case for case in sample["cases"] if case["id"] == "Y006"
            ).update(text="Corrija o incremento da sequência.")
        )

    def test_bancada_congelada_reproduz_o_diagnostico_local(self):
        report = self.preflight.run_local_bench()
        self.assertEqual(report["scores"], {"dev": (24, 23), "reserved": (24, 16)})
        self.assertEqual(len(report["batches"]), 4)

    def test_lotes_transportam_somente_id_e_texto(self):
        batches = self.preflight.classifier_batches(self.sample)
        self.assertEqual([len(batch) for batch in batches], [12, 12, 12, 12])
        self.assertTrue(
            all(set(case) == {"id", "text"} for batch in batches for case in batch)
        )


if __name__ == "__main__":
    unittest.main()
