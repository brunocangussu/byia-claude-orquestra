"""T-149: fábrica única, consulta pura e proposta de adoção sem efeitos."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parent
PACKAGE = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))
import elenco_padrao as elenco


class CatalogoTest(unittest.TestCase):
    def setUp(self):
        self.catalog = elenco.load_catalog(PACKAGE)

    def test_completo_sem_manager_spawnavel_nem_quinta_ancora(self):
        self.assertEqual(self.catalog["version"], json.loads(
            (PACKAGE / ".claude-plugin/plugin.json").read_text())["version"])
        self.assertEqual(set(self.catalog["hosts"]), {"claude", "codex"})
        for roles in self.catalog["hosts"].values():
            self.assertEqual(set(roles), set(elenco.ROLES))
            self.assertNotIn("manager", roles)
        raw = json.loads((PACKAGE / "references/elenco-padrao.json").read_text())
        self.assertNotIn("version", raw)
        self.assertEqual(raw["manager"], "sessao_do_dono")

    def test_faixas_aprovadas_e_reviewer_oposto(self):
        for role, model, effort in (
            ("implementer·leve", "gpt-6-luna", "medium"),
            ("implementer·normal", "gpt-6.1-sol", "high"),
            ("implementer·pesada", "gpt-6.1-sol", "xhigh"),
            ("docs", "gpt-6-luna", "low"),
            ("scout", "gpt-6-luna", "medium"),
        ):
            profile = self.catalog["hosts"]["codex"][role]
            self.assertEqual((profile["model_id"], profile["effort"]), (model, effort))
        for host, model, effort in (
            ("codex", "claude-opus-5-5", "high"),
            ("claude", "gpt-6.1-sol", "xhigh"),
        ):
            p = self.catalog["hosts"][host]["reviewer"]
            self.assertEqual((p["model_id"], p["effort"]), (model, effort))
        for band, effort in (("leve", "low"), ("normal", "medium"), ("pesada", "high")):
            p = self.catalog["hosts"]["claude"]["implementer·" + band]
            self.assertEqual((p["model_id"], p["effort"]), ("claude-sonnet-5-5", effort))

    def test_schema_fechado_e_erro_nao_vira_fallback(self):
        raw = json.loads((PACKAGE / "references/elenco-padrao.json").read_text())
        mutations = []
        for path, value in (
            (("schema",), True), (("version",), "9.9.9"),
            (("hosts", "codex", "docs", "model_id"), "opus"),
            (("hosts", "claude", "reviewer", "model_id"), "claude-opus-5-5"),
            (("hosts", "codex", "docs", "effort"), "automatic"),
            (("hosts", "codex", "docs", "mechanisms"), ["claude-cli"]),
            (("hosts", "claude", "docs", "effort"), "xhigh"),
        ):
            item = copy.deepcopy(raw)
            node = item
            for key in path[:-1]:
                node = node[key]
            node[path[-1]] = value
            mutations.append(item)
        item = copy.deepcopy(raw)
        del item["hosts"]["codex"]["docs"]
        mutations.append(item)
        for item in mutations:
            with self.subTest(item=item), self.assertRaises(ValueError):
                elenco.validate_catalog(item)

    def test_digest_canonico_e_tabela_gerada_do_mesmo_dado(self):
        raw = json.loads((PACKAGE / "references/elenco-padrao.json").read_text())
        self.assertEqual(elenco.catalog_digest(raw), elenco.catalog_digest(
            json.loads(json.dumps(raw, sort_keys=True))))
        table = elenco.render_host_table(self.catalog, "codex")
        self.assertIn("`gpt-6-luna@medium`", table)
        changed = copy.deepcopy(self.catalog)
        changed["hosts"]["codex"]["docs"]["effort"] = "medium"
        self.assertIn("| docs | `gpt-6-luna@medium` |", elenco.render_host_table(changed, "codex"))
        self.assertNotEqual(table, elenco.render_host_table(changed, "codex"))

    def test_intencao_versionada_nao_reinterpreta_perfil_local(self):
        for text in ("siga o elenco padrão desta versão", "padrão da versão", "padrão Orquestra"):
            self.assertEqual(elenco.classify_intent(text), "versioned-default")
        for text in ("perfil padrao", "perfil padrão", "perfil economia"):
            self.assertEqual(elenco.classify_intent(text), "local-preset")
        self.assertIsNone(elenco.classify_intent("troque apenas o reviewer"))

    def test_consulta_cli_sem_elenco_nem_rede_com_alerta_de_versao(self):
        with tempfile.TemporaryDirectory() as temp:
            before = list(Path(temp).iterdir())
            r = subprocess.run([sys.executable, str(SCRIPTS / "elenco_padrao.py"),
                "--package-root", str(PACKAGE), "--host", "codex",
                "--installed-version", "999.0.0"], cwd=temp, capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            payload = json.loads(r.stdout)
            self.assertEqual(payload["version"], self.catalog["version"])
            self.assertEqual(payload["state"], "proposal")
            self.assertIn("carregada", payload["warnings"][0])
            self.assertEqual(list(Path(temp).iterdir()), before)
            self.assertNotIn("adopted_at", r.stdout)

    def test_raiz_de_pacote_incompleta_nao_resolve_latest(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                elenco.load_catalog(Path(temp))


class AdocaoTest(unittest.TestCase):
    def setUp(self):
        self.catalog = elenco.load_catalog(PACKAGE)
        self.active = {"hosts": {"codex": {}, "claude": {"docs": {"model_id": "legado"}}},
            "presets": {"padrao": {"docs": "legado"}}, "overrides": {"codex": {}},
            "disabled_mechanisms": ["codex-native"], "manager": "escolha-do-dono"}
        self.contexts = {role: {route: {"account": "conta-local", "client_version": "fixture-1",
            "sandbox": "workspace-write" if role.startswith("implementer") or role == "docs" else "read-only"}
            for route in ("codex-cli", "claude-cli")} for role in elenco.ROLES}
        self.receipts = [self.receipt(role, profile) for role, profile in
            self.catalog["hosts"]["codex"].items()]

    def receipt(self, role, profile):
        route = "claude-cli" if profile["model_id"].startswith("claude-") else "codex-cli"
        return {"role": role, "success": True, "model_id": profile["model_id"],
            "effort": profile["effort"], "sent_model_id": profile["model_id"],
            "sent_effort": profile["effort"], "observed_model_id": profile["model_id"],
            "observed_effort": None, "mechanism": route, "evidence_ref": "fixture:real-boundary",
            **self.contexts[role][route]}

    def preview(self, receipts=None):
        return elenco.preview_adoption(self.active, self.catalog, "codex", self.contexts,
            self.receipts if receipts is None else receipts, adopted_at="2026-10-05T12:00:00Z")

    def test_proposta_atomica_preserva_outro_host_presets_manager_e_vias(self):
        original = copy.deepcopy(self.active)
        result = self.preview()
        self.assertEqual(result["state"], "ready")
        proposed = result["proposal"]
        self.assertEqual(self.active, original)
        for key in ("presets", "manager", "disabled_mechanisms"):
            self.assertEqual(proposed[key], original[key])
        self.assertEqual(proposed["hosts"]["claude"], original["hosts"]["claude"])
        for role, p in proposed["hosts"]["codex"].items():
            expected_route = "claude-cli" if role in ("planner·interface", "reviewer") else "codex-cli"
            self.assertEqual(p["mechanisms"], [expected_route])
            self.assertEqual(p["model_id"], self.catalog["hosts"]["codex"][role]["model_id"])
            self.assertEqual(p["effort"], self.catalog["hosts"]["codex"][role]["effort"])
        self.assertEqual(proposed["provenance"]["codex"]["version"], self.catalog["version"])
        self.assertEqual(proposed["provenance"]["codex"]["catalog_sha256"], self.catalog["catalog_sha256"])
        self.assertEqual(result["previous_host"], {})

    def test_falta_prova_nao_produz_adocao_parcial_nem_probe(self):
        result = self.preview(self.receipts[:-1])
        self.assertEqual(result["state"], "needs-proof")
        self.assertIsNone(result["proposal"])
        self.assertEqual(result["missing_roles"], [self.receipts[-1]["role"]])
        self.assertEqual(self.active["hosts"]["codex"], {})

    def test_recibo_precisa_de_contexto_modelo_effort_e_identidade(self):
        for key, value in (("success", 1), ("effort", "low"), ("sent_effort", "low"),
            ("observed_model_id", "gpt-6-astra"), ("observed_effort", "low"),
            ("account", "outra"), ("client_version", "outra"), ("sandbox", "write"),
            ("mechanism", "codex-native"), ("evidence_ref", "")):
            receipts = copy.deepcopy(self.receipts)
            receipts[0][key] = value
            with self.subTest(key=key):
                result = self.preview(receipts)
                self.assertEqual(result["state"], "needs-proof")
                self.assertIn(receipts[0]["role"], result["missing_roles"])

    def test_override_explicito_sobrevive_sem_exigir_prova_do_padrao(self):
        custom = {"model_id": "escolha-local", "effort": "low"}
        self.active["hosts"]["codex"]["docs"] = custom.copy()
        self.active["overrides"]["codex"]["docs"] = custom.copy()
        result = self.preview([r for r in self.receipts if r["role"] != "docs"])
        self.assertEqual(result["state"], "ready")
        self.assertEqual(result["proposal"]["hosts"]["codex"]["docs"], custom)
        self.assertEqual(result["proposal"]["overrides"], self.active["overrides"])

    def test_inalterado_nao_exige_repetir_prova_nem_apaga_origem(self):
        self.active = self.preview()["proposal"]
        self.assertEqual(self.preview([])["state"], "ready")

    def test_via_markdown_runner_opus_off_bloqueia_somente_anthropic_no_codex(self):
        self.active["disabled_mechanisms"].append("runner-opus")
        result = self.preview()
        self.assertEqual(result["state"], "needs-proof")
        self.assertEqual(result["missing_roles"], ["planner·interface", "reviewer"])
        self.assertIsNone(result["proposal"])

    def test_via_markdown_codex_off_bloqueia_companion_no_claude(self):
        contexts, receipts = {}, []
        for role, p in self.catalog["hosts"]["claude"].items():
            route = p["mechanisms"][0]
            context = {"account": "conta-local", "client_version": "fixture-1",
                "sandbox": "workspace-write" if role.startswith("implementer") or role == "docs" else "read-only"}
            contexts[role] = {route: context}
            receipts.append({"role": role, "success": True, "model_id": p["model_id"],
                "effort": p["effort"], "sent_model_id": p["model_id"], "sent_effort": p["effort"],
                "observed_model_id": p["model_id"], "observed_effort": None,
                "mechanism": route, "evidence_ref": "fixture:boundary", **context})
        active = {"hosts": {"claude": {}}, "disabled_mechanisms": ["codex"]}
        result = elenco.preview_adoption(active, self.catalog, "claude", contexts, receipts,
            adopted_at="2026-10-06T15:00:00Z")
        self.assertEqual(result["state"], "needs-proof")
        self.assertEqual(result["missing_roles"], ["planner·sistema", "reviewer"])

    def test_somente_mecanismo_comprovado_e_gravado_e_reutilizado(self):
        result = self.preview()
        p = result["proposal"]
        self.assertEqual(p["hosts"]["codex"]["implementer·normal"]["mechanisms"], ["codex-cli"])
        self.assertEqual(p["provenance"]["codex"]["mechanisms"]["implementer·normal"], "codex-cli")
        self.active = p
        again = self.preview([])
        self.assertEqual(again["state"], "ready")
        self.assertEqual(again["proposal"]["hosts"]["codex"], p["hosts"]["codex"])

    def test_candidatos_iguais_sem_via_selecionada_nao_contornam_prova(self):
        self.active["hosts"]["codex"] = copy.deepcopy(self.catalog["hosts"]["codex"])
        result = self.preview([])
        self.assertEqual(result["state"], "needs-proof")
        self.assertIn("implementer·normal", result["missing_roles"])

    def test_prova_reutilizada_nao_sobrevive_a_contexto_diferente(self):
        adopted = self.preview()["proposal"]
        for key in ("account", "client_version", "sandbox"):
            self.active = copy.deepcopy(adopted)
            original = self.contexts["docs"]["codex-cli"][key]
            self.contexts["docs"]["codex-cli"][key] = "contexto-diferente"
            with self.subTest(context=key):
                result = self.preview([])
                self.assertEqual(result["state"], "needs-proof")
                self.assertEqual(result["missing_roles"], ["docs"])
            self.contexts["docs"]["codex-cli"][key] = original

    def test_release_novo_propoe_sem_migrar_snapshot_antigo(self):
        adopted = self.preview()["proposal"]
        self.active = adopted
        original = copy.deepcopy(adopted)
        self.catalog = copy.deepcopy(self.catalog)
        self.catalog["version"] = "999.0.0"
        self.catalog["hosts"]["codex"]["docs"]["effort"] = "high"
        self.catalog["catalog_sha256"] = elenco.catalog_digest(
            {k: self.catalog[k] for k in ("schema", "manager", "hosts")})
        result = self.preview([])
        self.assertEqual(result["state"], "needs-proof")
        self.assertEqual(result["missing_roles"], ["docs"])
        self.assertEqual(self.active, original)

    def test_via_desligada_nao_e_reativada(self):
        self.active["disabled_mechanisms"].append("claude-cli")
        self.assertEqual(self.preview()["state"], "needs-proof")

    def test_legado_sem_marca_nao_e_convertido_em_override(self):
        self.active["hosts"]["codex"]["docs"] = {"model_id": "legado", "effort": "low"}
        result = self.preview([])
        self.assertIn("docs", result["missing_roles"])
        self.assertEqual(result["origin"], "legacy")

    def test_sonda_readonly_nao_comprova_writer_mesmo_contexto_igual(self):
        role = "implementer·normal"
        self.contexts[role]["codex-cli"]["sandbox"] = "read-only"
        next(r for r in self.receipts if r["role"] == role)["sandbox"] = "read-only"
        self.assertIn(role, self.preview()["missing_roles"])

    def test_override_divergente_e_metadado_fabricado_sao_recusados(self):
        self.active["overrides"]["codex"]["docs"] = {"model_id": "novo-nao-ativo"}
        with self.assertRaises(ValueError):
            self.preview()
        self.active["overrides"]["codex"] = {}
        self.catalog["catalog_sha256"] = "f" * 64
        with self.assertRaises(ValueError):
            self.preview()

    def test_snapshot_malformado_falha_sem_proposta(self):
        self.active["hosts"] = []
        with self.assertRaises(ValueError):
            self.preview()

    def test_host_claude_adota_sem_tocar_codex(self):
        before = copy.deepcopy(self.active)
        contexts = {role: {route: {"account": "conta-local", "client_version": "fixture-1",
            "sandbox": "workspace-write" if role.startswith("implementer") or role == "docs" else "read-only"}
            for route in profile["mechanisms"]}
            for role, profile in self.catalog["hosts"]["claude"].items()}
        receipts = []
        for role, p in self.catalog["hosts"]["claude"].items():
            route = p["mechanisms"][0]
            receipts.append({"role": role, "success": True, "model_id": p["model_id"],
                "effort": p["effort"], "sent_model_id": p["model_id"], "sent_effort": p["effort"],
                "observed_model_id": p["model_id"], "observed_effort": None,
                "mechanism": route, "evidence_ref": "fixture:real-boundary", **contexts[role][route]})
        result = elenco.preview_adoption(self.active, self.catalog, "claude", contexts, receipts,
                                         adopted_at="2026-10-05T12:00:00Z")
        self.assertEqual(result["state"], "ready")
        self.assertEqual(result["proposal"]["hosts"]["codex"], before["hosts"]["codex"])
        self.assertEqual(self.active, before)


if __name__ == "__main__":
    unittest.main()
