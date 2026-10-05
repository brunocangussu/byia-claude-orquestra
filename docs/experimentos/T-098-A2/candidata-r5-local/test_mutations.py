"""Mutações estruturais da bancada R5; todas devem morrer por asserção contratual."""

import copy
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent
R4_ROOT = ROOT.parent / "candidata-r4"


def load_preflight(root):
    spec = importlib.util.spec_from_file_location(
        f"mutation_preflight_{root.name}", root / "preflight.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class MutationTest(unittest.TestCase):
    def setUp(self):
        self.preflight = load_preflight(ROOT)
        self.sample = json.loads((ROOT / "amostra.json").read_text())
        self.r4_sample = json.loads((R4_ROOT / "amostra.json").read_text())

    def reject(self, change):
        sample = copy.deepcopy(self.sample)
        change(sample)
        with self.assertRaises(ValueError):
            self.preflight.classifier_batches(sample)

    def old_text(self, identifier):
        return next(
            case["text"] for case in self.r4_sample["cases"] if case["id"] == identifier
        )

    def test_texto_antigo_no_dev_morre(self):
        self.reject(
            lambda sample: next(
                case for case in sample["cases"] if case["id"] == "Y006"
            ).update(text=self.old_text("Y006"))
        )

    def test_texto_antigo_no_reserved_morre(self):
        identifier = next(case["id"] for case in self.sample["cases"] if case["split"] == "reserved")
        self.reject(
            lambda sample: next(
                case for case in sample["cases"] if case["id"] == identifier
            ).update(text=self.old_text(identifier))
        )

    def test_y006_sem_contrato_observavel_morre(self):
        self.reject(
            lambda sample: next(
                case for case in sample["cases"] if case["id"] == "Y006"
            ).update(text="Corrija o incremento da sequência.")
        )

    def test_gold_trocado_preservando_contagens_morre(self):
        def change(sample):
            first, second = next(
                (left, right)
                for left in sample["cases"]
                for right in sample["cases"]
                if left["split"] == right["split"]
                and left["gold"] != right["gold"]
            )
            first["gold"], second["gold"] = second["gold"], first["gold"]

        self.reject(change)

    def test_y038_sem_rejeicoes_contratuais_morre(self):
        self.reject(
            lambda sample: next(
                case for case in sample["cases"] if case["id"] == "Y038"
            ).update(
                text=next(case for case in sample["cases"] if case["id"] == "Y038")["text"].replace(
                    "rejeições previstas no contrato", "casos existentes"
                )
            )
        )

    def test_y047_sem_isolamento_da_prosa_morre(self):
        self.reject(
            lambda sample: next(
                case for case in sample["cases"] if case["id"] == "Y047"
            ).update(
                text=next(case for case in sample["cases"] if case["id"] == "Y047")["text"].replace(
                    "prosa estática fora dos exemplos gerados", "texto de exemplos"
                )
            )
        )

    def test_familia_alterada_morre(self):
        self.reject(lambda sample: sample["cases"][0].update(family="familia-inventada"))

    def test_particao_trocada_preservando_contagens_morre(self):
        def change(sample):
            first, second = next(
                (left, right)
                for left in sample["cases"]
                for right in sample["cases"]
                if left["gold"] == right["gold"]
                and left["split"] == "dev"
                and right["split"] == "reserved"
            )
            first["split"], second["split"] = second["split"], first["split"]

        self.reject(change)

    def test_projecao_com_gold_morre(self):
        batches = self.preflight.classifier_batches(self.sample)
        batches[0][0]["gold"] = "trivial"
        with self.assertRaises(ValueError):
            self.preflight.validate_projection(batches, self.sample)

    def test_selo_tampered_de_cada_artefato_morre_antes_da_pontuacao(self):
        with tempfile.TemporaryDirectory() as directory:
            copied = Path(directory)
            for name in self.preflight.FROZEN_HASHES:
                shutil.copy2(ROOT / name, copied / name)
            for name in self.preflight.FROZEN_HASHES:
                with self.subTest(name=name):
                    changed = copied / name
                    original = changed.read_bytes()
                    changed.write_bytes(original + b"\n")
                    with self.assertRaises(ValueError):
                        self.preflight.run_local_bench(copied)
                    changed.write_bytes(original)


if __name__ == "__main__":
    unittest.main()
