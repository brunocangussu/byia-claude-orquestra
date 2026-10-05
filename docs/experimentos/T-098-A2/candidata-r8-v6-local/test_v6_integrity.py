"""Regressões da candidata R8 v6: baseline integral e selagem local."""
from __future__ import annotations

from copy import deepcopy
import inspect
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import preflight


ROOT = Path(__file__).resolve().parent
V1_ROOT = ROOT.parent / "candidata-r6-local"


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


class R8V6IntegrityTest(unittest.TestCase):
    def test_adjudicacoes_integrais_dos_48_igualam_o_baseline_v1(self):
        manifest = load_json(ROOT / "manifesto.json")
        expected = {
            entry["id"]: tuple(
                entry[field]
                for field in ("gold", "split", "family", "policy_code", "facts", "rationale")
            )
            for entry in load_json(V1_ROOT / "manifesto.json")["adjudications"]
        }
        self.assertEqual(preflight.validate_full_metadata_baseline(ROOT, manifest)["adjudications"], expected)

    def test_mutacoes_de_metadata_integral_morrem_sem_reanotar(self):
        manifest = load_json(ROOT / "manifesto.json")
        cases = {
            "policy_code": lambda item: item.__setitem__("policy_code", "consulta_delimitada"),
            "facts": lambda item: item.__setitem__("facts", item["facts"] + ["mutacao_sem_reanotar"]),
            "rationale": lambda item: item.__setitem__("rationale", item["rationale"] + " Mutação."),
        }
        for field, mutate in cases.items():
            with self.subTest(field=field):
                changed = deepcopy(manifest)
                mutate(next(item for item in changed["adjudications"] if item["id"] == "Y007"))
                with self.assertRaisesRegex(ValueError, "metadados completos v1 divergentes: Y007"):
                    preflight.validate_full_metadata_baseline(ROOT, changed)

    def test_mutacoes_de_policy_taxonomy_e_lotes_morrem_no_baseline(self):
        manifest = load_json(ROOT / "manifesto.json")
        mutations = {
            "policy_codes": lambda value: value["policy_codes"]["consulta_delimitada"]["required_facts"].append("mutacao_sem_reanotar"),
            "taxonomy": lambda value: value["taxonomy"][next(iter(value["taxonomy"]))].reverse(),
            "batches": lambda value: value["batches"]["dev"][0].reverse(),
        }
        for field, mutate in mutations.items():
            with self.subTest(field=field):
                changed = deepcopy(manifest)
                mutate(changed)
                with self.assertRaisesRegex(ValueError, f"metadados globais v1 divergentes: {field}"):
                    preflight.validate_full_metadata_baseline(ROOT, changed)

    def test_selo_local_cobre_runtime_testes_e_documentacao(self):
        manifest = load_json(ROOT / "manifesto.json")
        seal = preflight.verify_v6_local_seal(ROOT, manifest)
        self.assertEqual(set(seal["files"]), set(manifest["local_seal"]["covered_paths"]))
        self.assertTrue({"preflight.py", "test_preflight.py", "test_mutations.py", "test_v6_integrity.py"}.issubset(seal["files"]))
        self.assertTrue({"evidencias-bancada-local.md", "politica-e-limites.md", "recibo-congelamento-r8-v6.md"}.issubset(seal["files"]))

    def test_selo_rejeita_documentacao_mutada_em_copia_descartavel(self):
        with tempfile.TemporaryDirectory(prefix="t098-v6-seal-") as temporary:
            candidate = Path(temporary) / "candidata-r8-v6-local"
            shutil.copytree(ROOT, candidate)
            policy = candidate / "politica-e-limites.md"
            policy.write_text(policy.read_text(encoding="utf-8") + "\nmutação descartável\n", encoding="utf-8")
            manifest = load_json(candidate / "manifesto.json")
            with self.assertRaisesRegex(ValueError, "arquivo selado divergente: politica-e-limites.md"):
                preflight.verify_v6_local_seal(candidate, manifest)


class ProjectFileV6MutationTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="t098-v6-project-file-")
        self.addCleanup(self.temp.cleanup)
        self.fixture = Path(self.temp.name).resolve()
        self.project = self.fixture / "project"
        self.candidate = self.project / "docs/experimentos/T-098-A2/candidata-r8-v6-local"
        self.candidate.mkdir(parents=True)
        self.target = self.project / "target.txt"
        self.target.write_text("fixture sintética regular\n", encoding="utf-8")
        (self.project / "dir").mkdir()
        (self.project / "directory").mkdir()

    def assert_rejected(self, callback, relative):
        with self.assertRaisesRegex(ValueError, "projeto inválido"):
            callback(self.candidate, relative, "projeto inválido")

    def mutant(self, old, new):
        source = inspect.getsource(preflight._project_file)
        self.assertEqual(source.count(old), 1)
        namespace = dict(preflight.__dict__)
        exec(compile(source.replace(old, new, 1), "<t098-v6-mutant>", "exec"), namespace)
        return namespace["_project_file"]

    def test_arquivo_regular_tem_controle_positivo_e_todos_os_ramos_rejeitam(self):
        self.assertEqual(preflight._project_file(self.candidate, "target.txt", "projeto inválido"), self.target)
        link = self.project / "inside-link.txt"
        link.symlink_to(self.target)
        self.assertTrue(link.is_file())
        self.assertTrue(link.is_symlink())
        for relative in (str(self.target.resolve()), "dir/../target.txt", "missing.txt", "directory", link.name):
            with self.subTest(relative=relative):
                self.assert_rejected(preflight._project_file, relative)

    def test_mutacoes_remover_symlink_relativo_e_is_file_sao_detectadas(self):
        link = self.project / "inside-link.txt"
        link.symlink_to(self.target)
        no_symlink = self.mutant("path.is_file() and not path.is_symlink()", "path.is_file()")
        self.assertEqual(no_symlink(self.candidate, link.name, "projeto inválido"), link)

        no_relative = self.mutant('not relative.is_absolute() and ".." not in relative.parts', "True")
        self.assertEqual(no_relative(self.candidate, str(self.target.resolve()), "projeto inválido"), self.target)
        self.assertTrue(no_relative(self.candidate, "dir/../target.txt", "projeto inválido").is_file())

        no_is_file = self.mutant("path.is_file() and not path.is_symlink()", "not path.is_symlink()")
        missing = no_is_file(self.candidate, "missing.txt", "projeto inválido")
        self.assertFalse(missing.is_file())


if __name__ == "__main__":
    unittest.main()
