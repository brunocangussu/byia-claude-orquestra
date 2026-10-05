"""Guardas de preparação; não substituem revisão semântica independente."""

import copy
import json
import unittest
from pathlib import Path

import preflight


class PreflightTest(unittest.TestCase):
    def setUp(self):
        self.sample = json.loads(Path(__file__).with_name("amostra.json").read_text())

    def reject(self, change):
        sample = copy.deepcopy(self.sample)
        change(sample)
        with self.assertRaises(ValueError):
            preflight.classifier_batches(sample)

    def test_controle_original_valido(self):
        preflight.validate_sample(self.sample)
        self.assertEqual(sum(map(len, preflight.classifier_batches(self.sample))), 48)

    def test_payload_so_tem_id_text_e_nao_muda_a_fonte(self):
        original = copy.deepcopy(self.sample)
        batches = preflight.classifier_batches(self.sample)
        for batch in batches:
            self.assertEqual(len(batch), 12)
            for case in batch:
                self.assertEqual(set(case), {"id", "text"})
        self.assertEqual(self.sample, original)
        batches[0][0]["text"] = "alterado na cópia"
        self.assertEqual(self.sample, original)

    def test_lotes_nao_misturam_as_particoes_locais(self):
        batches = preflight.classifier_batches(self.sample)
        splits = {c["id"]: c["split"] for c in self.sample["cases"]}
        for i, batch in enumerate(batches):
            self.assertEqual({splits[c["id"]] for c in batch}, {"dev" if i < 2 else "reserved"})
        self.assertEqual(len({c["id"] for b in batches for c in b}), 48)

    def test_caso_faltante_reprova(self):
        self.reject(lambda s: s["cases"].pop())

    def test_id_duplicado_reprova(self):
        # Não usar os controles contrastivos: a guarda de ID tem de valer sozinha.
        self.reject(lambda s: s["cases"][2].update(id=s["cases"][1]["id"]))

    def test_classe_ausente_reprova(self):
        self.reject(lambda s: s["cases"][0].update(gold="consulta"))

    def test_particao_cruzada_preservando_contagens_reprova(self):
        def change(s):
            # Duas consultas: a contagem por classe/split continua igual.
            s["cases"][1]["split"] = "reserved"
            s["cases"][25]["split"] = "dev"
        self.reject(change)

    def test_familia_desconhecida_reprova(self):
        self.reject(lambda s: s["cases"][0].update(family="dominio-inventado"))

    def test_pedido_repetido_entre_particoes_reprova(self):
        self.reject(lambda s: s["cases"][24].update(text=s["cases"][0]["text"]))

    def test_justificativa_vazia_reprova(self):
        self.reject(lambda s: s["cases"][0].update(reason=" "))

    def test_campo_extra_reprova(self):
        self.reject(lambda s: s["cases"][0].update(credencial="placeholder-proibido"))

    def test_id_com_classe_reprova(self):
        self.reject(lambda s: s["cases"][0].update(id="alto_risco-037"))

    def test_troca_contrastiva_de_gold_com_contagens_iguais_reprova(self):
        def change(s):
            # Texto que expõe PII não pode virar trivial por dizer "só leitura".
            a = next(c for c in s["cases"] if c["id"] == "Y012")
            b = next(c for c in s["cases"] if c["id"] == "Y027")
            a["gold"], b["gold"] = b["gold"], a["gold"]
        self.reject(change)


if __name__ == "__main__":
    unittest.main()
