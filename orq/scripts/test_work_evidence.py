"""Contratos observáveis do apoio consultivo, sem modelo, rede ou credenciais."""
import json
import hashlib
from contextlib import contextmanager
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import work_evidence as support
from test_continuidade_aprovada import extrair_secao, normalizar


class InstructionSnapshot:
    """Cópia descartável das instruções; nunca muda fonte, main ou cache."""

    def __init__(self, test, relatives):
        temporary = tempfile.TemporaryDirectory(prefix="orq-t151-")
        test.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        source = Path(__file__).resolve().parents[2]
        for relative in relatives:
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source / relative, destination)

    def read(self, relative, heading=None):
        text = (self.root / relative).read_text(encoding="utf-8")
        return normalizar(extrair_secao(text, heading) if heading else text)

    @contextmanager
    def mutate(self, relative, old, new):
        path = self.root / relative
        original = path.read_text(encoding="utf-8")
        pattern = r"\s+".join(re.escape(word) for word in old.split())
        changed, count = re.subn(pattern, lambda match: new, original, flags=re.IGNORECASE)
        if count != 1:
            raise AssertionError(f"âncora de mutação ambígua/ausente: {old} ({count})")
        try:
            path.write_text(changed, encoding="utf-8")
            yield
        finally:
            path.write_text(original, encoding="utf-8")


GOAL_POLICY = "orq/skills/orq/SKILL.md"
GOAL_HEADING = "### Acordo inicial por meta"
DISPATCH_HEADING = "### Despacho por entregas e dependências"
PLAN_COMMAND = "orq/commands/plan-next.md"
IMPLEMENT_COMMAND = "orq/commands/implement-next.md"
PLANNER_AGENT = "orq/agents/orq-planner.md"


class GoalAgreementInstructionTest(unittest.TestCase):
    """Guardas T-151 de instrução, sem inferência nem prova de economia."""

    def setUp(self):
        self.snapshot = InstructionSnapshot(self, (
            GOAL_POLICY, PLAN_COMMAND, IMPLEMENT_COMMAND, PLANNER_AGENT,
            "orq/references/continuidade-evidencias.md", "AGENTS.md", "CLAUDE.md",
        ))

    def require(self, text, clauses, invariant):
        for clause in clauses:
            self.assertTrue(normalizar(clause) in text,
                            f"{invariant}: cláusula ausente: {clause}")

    def assert_human_agreement(self):
        self.require(self.snapshot.read(GOAL_POLICY, GOAL_HEADING), (
            "fonte humana literal e ponteiro verificável",
            "propósito, frente dona, card e critérios de aceite",
            "escopo permitido e exclusões",
            "delegação técnica ao Manager",
            "operações locais permitidas",
            "operações externas e de entrega discriminadas",
            "proibições, limites e consumo por gate",
            "Aprovação de agente não substitui autoridade humana",
            "Somente a fonte humana verificada comprova a delegação e as operações cobertas",
        ), "autoridade humana")

    def assert_same_agreement(self):
        self.require(self.snapshot.read(GOAL_POLICY, GOAL_HEADING), (
            "O Manager aceita ou devolve subplanos técnicos necessários ao mesmo objetivo",
            "mesmo propósito, frente, card e aceite",
            "dentro do escopo e das operações permitidas, sem cruzar exclusões ou limites",
            "registra na thread o vínculo ao mesmo acordo e à fonte humana original",
            "sem nova pergunta por subpasso coberto",
        ), "mesmo acordo")
        self.require(self.snapshot.read(PLAN_COMMAND, "## 4. Receber e avaliar"), (
            "complemento necessário",
            "vínculo ao mesmo acordo",
            "decisão técnica do Manager",
        ), "mesmo acordo")
        self.require(self.snapshot.read(PLAN_COMMAND, "## 5. Levar ao dono (o gate)"), (
            "Complemento coberto segue pelo aceite técnico do Manager",
            "sem repetir o gate humano",
        ), "mesmo acordo")
        self.require(self.snapshot.read(PLAN_COMMAND, "## 1. Escolher o card"), (
            "não crie card nem reinicie PLANNING por um subplano",
        ), "mesmo acordo")
        self.require(self.snapshot.read(PLAN_COMMAND, "## 6. Fechar o loop"), (
            "Complemento devolvido ao Planner preserva o estado do card",
        ), "mesmo acordo")
        self.require(self.snapshot.read(PLAN_COMMAND, "## 3. Despachar o Planner"), (
            "Em complemento coberto, falha de capacidade estaciona somente o despacho dependente",
            "Menções a manter PLANNING neste passo valem para planejamento inicial",
        ), "mesmo acordo")

    def assert_no_inheritance(self):
        self.require(self.snapshot.read(GOAL_POLICY, GOAL_HEADING), (
            "Sem meta ou delegação verificável, não presuma cobertura",
            "Propósito novo, frente alheia ou card novo não herdam autoridade silenciosamente",
            "mudança material exige decisão humana",
            "Nunca crie aprovação, saldo ou permissão por aceite técnico",
        ), "fronteira de autoridade")

    def assert_balance_and_operations(self):
        contract = self.snapshot.read(GOAL_POLICY, "## Contrato de continuidade aprovada")
        self.require(contract, (
            "permissões local, externa e Git são independentes",
            "Registrar digest novo não renova saldo",
            "Saldo é o limite menos as tentativas já iniciadas",
            "gate externo consumido não se reabre sozinho",
            "Tentativa incerta ou falha preserva consumo e handle",
            "Aceite técnico não autoriza envio externo, produção ou entrega Git ausentes do acordo",
        ), "saldo e operações")

    def assert_recovery(self):
        self.require(self.snapshot.read(GOAL_POLICY, GOAL_HEADING), (
            "Reutilize a thread e o medidor existentes",
            "não crie ledger ou sistema de aprovação adicional",
            "recupere o acordo, a fonte humana, o plano, o ownership, o consumo e os handles",
            "sem zerar limites, trocar modelo ou buscar outra thread como fallback",
        ), "recuperação sem novo ledger")
        self.require(self.snapshot.read(IMPLEMENT_COMMAND, "## 0b. Abrir o medidor de progresso"), (
            "Em retomada ou complemento, reutilize o run e os passos existentes",
            "não repita `begin` ou `plan` para reiniciar o trabalho",
        ), "recuperação sem novo ledger")

    def test_initial_agreement_consolidates_human_purpose_scope_and_limits(self):
        self.assert_human_agreement()

    def test_necessary_subplan_uses_same_agreement_without_repeated_owner_gate(self):
        self.assert_same_agreement()

    def test_absent_goal_or_new_purpose_front_card_does_not_inherit_authority(self):
        self.assert_no_inheritance()

    def test_technical_acceptance_and_new_digest_do_not_renew_balance_or_operations(self):
        self.assert_balance_and_operations()

    def test_recovery_preserves_one_thread_meter_ownership_consumption_and_handle(self):
        self.assert_recovery()

    def test_consumers_refer_to_one_policy_and_planner_separates_human_decisions(self):
        for relative in (PLAN_COMMAND, IMPLEMENT_COMMAND, PLANNER_AGENT, "AGENTS.md", "CLAUDE.md"):
            with self.subTest(consumer=relative):
                self.require(self.snapshot.read(relative), (
                    "Contrato de continuidade aprovada", "Acordo inicial por meta",
                ), "remissão única")
        self.require(self.snapshot.read(PLAN_COMMAND, "## 0. Acordo inicial ou complemento técnico"), (
            "fonte humana", "delegação", "sem inventar cobertura",
        ), "acordo antes do despacho")
        self.require(self.snapshot.read(PLANNER_AGENT, "## Handoff (obrigatório)"), (
            "vínculo ao acordo original", "necessidade para o mesmo objetivo",
            "dúvidas técnicas", "decisões humanas novas",
        ), "handoff do Planner")

    def test_mutations_break_the_specific_authority_agreement_balance_or_recovery_guard(self):
        mutations = (
            (GOAL_POLICY, "fonte humana literal e ponteiro verificável",
             "nota do Manager como única fonte", self.assert_human_agreement, "autoridade humana"),
            (GOAL_POLICY, "Aprovação de agente não substitui autoridade humana",
             "Aprovação de agente substitui autoridade humana", self.assert_human_agreement, "autoridade humana"),
            (GOAL_POLICY, "Somente a fonte humana verificada comprova a delegação e as operações cobertas",
             "A proposta do Manager comprova a delegação e as operações cobertas", self.assert_human_agreement, "autoridade humana"),
            (GOAL_POLICY, "subplanos técnicos necessários ao mesmo objetivo",
             "subplanos técnicos de qualquer objetivo", self.assert_same_agreement, "mesmo acordo"),
            (GOAL_POLICY, "mesmo propósito, frente, card e aceite",
             "qualquer propósito, frente, card e aceite", self.assert_same_agreement, "mesmo acordo"),
            (PLAN_COMMAND, "Complemento coberto segue pelo aceite técnico do Manager",
             "Complemento coberto exige aprovação humana repetida", self.assert_same_agreement, "mesmo acordo"),
            (PLAN_COMMAND, "não crie card nem reinicie PLANNING por um subplano",
             "crie card e reinicie PLANNING por um subplano", self.assert_same_agreement, "mesmo acordo"),
            (PLAN_COMMAND, "Complemento devolvido ao Planner preserva o estado do card",
             "Complemento devolvido ao Planner volta o card inteiro ao BACKLOG", self.assert_same_agreement, "mesmo acordo"),
            (PLAN_COMMAND, "Em complemento coberto, falha de capacidade estaciona somente o despacho dependente",
             "Em complemento coberto, falha de capacidade estaciona a meta inteira", self.assert_same_agreement, "mesmo acordo"),
            (GOAL_POLICY, "Sem meta ou delegação verificável, não presuma cobertura",
             "Sem meta ou delegação verificável, presuma cobertura", self.assert_no_inheritance, "fronteira de autoridade"),
            (GOAL_POLICY, "card novo não herdam autoridade silenciosamente",
             "card novo herdam autoridade silenciosamente", self.assert_no_inheritance, "fronteira de autoridade"),
            (GOAL_POLICY, "Registrar digest novo não renova saldo",
             "Registrar digest novo renova saldo", self.assert_balance_and_operations, "saldo e operações"),
            (GOAL_POLICY, "Tentativa incerta ou falha preserva consumo e handle",
             "Tentativa incerta ou falha zera consumo e descarta handle", self.assert_balance_and_operations, "saldo e operações"),
            (GOAL_POLICY, "Aceite técnico não autoriza envio externo, produção ou entrega Git ausentes do acordo",
             "Aceite técnico autoriza envio externo, produção e entrega Git", self.assert_balance_and_operations, "saldo e operações"),
            (GOAL_POLICY, "não crie ledger ou sistema de aprovação adicional",
             "crie ledger e sistema de aprovação adicional", self.assert_recovery, "recuperação sem novo ledger"),
            (GOAL_POLICY, "sem zerar limites, trocar modelo ou buscar outra thread como fallback",
             "zerando limites, trocando modelo e buscando outra thread como fallback", self.assert_recovery, "recuperação sem novo ledger"),
            (IMPLEMENT_COMMAND, "não repita `begin` ou `plan` para reiniciar o trabalho",
             "repita `begin` e `plan` para reiniciar o trabalho", self.assert_recovery, "recuperação sem novo ledger"),
        )
        for _, _, _, guard, _ in mutations:
            guard()
        for relative, old, new, guard, invariant in mutations:
            with self.subTest(mutation=new), self.snapshot.mutate(relative, old, new):
                with self.assertRaisesRegex(AssertionError, invariant):
                    guard()


def evidence():
    return {
        "schema": 1,
        "snapshot_sha256": "c" * 64,
        "risk": "pesada",
        "review_rounds": 3,
        "stalled_rounds": 0,
        "blockers": 1,
        "snapshot_changed": True,
        "defect_class": "contract",
        "evidence_gap": "regression",
        "progress": [{"kind": "red_green", "receipt_sha256": "a" * 64}],
        "verification": {"targeted": "passed", "suite": "passed", "mutations": "passed"},
        "review": {"state": "blocked", "snapshot_current": False},
        "authority": {"local_work": True, "external_remaining": 0, "external_covered": False},
    }


def ready():
    value = evidence()
    value["blockers"] = 0
    value["evidence_gap"] = "none"
    value["review"]["state"] = "missing"
    return value


def receipt(value, choice, confidence=0.9):
    request = support.prepare_jev(value)
    keys = request["questions"]["next_action"]["criteria"]
    return {
        "schema": 1,
        "request_sha256": support.request_digest(request),
        "response": {
            "model": "jev-1.13.0",
            "answers": {
                "next_action": {
                    "type": "choice", "choice": choice, "confidence": confidence,
                    "probabilities": {key: int(key == choice) for key in keys},
                },
                "additional_tests": {"type": "noul", "noul": 0.8},
                "further_review": {"type": "noul", "noul": 0.7},
            },
        },
    }


class ContinuityTest(unittest.TestCase):
    def test_third_or_later_round_does_not_stop_authorized_local_work(self):
        for rounds in (2, 3, 4, 13, 100):
            with self.subTest(rounds=rounds):
                value = evidence()
                value["review_rounds"] = rounds
                self.assertEqual(support.recommend(value)["action"], "fix_and_test")

    def test_two_stalled_rounds_change_strategy_not_global_shutdown(self):
        value = evidence()
        value.update(stalled_rounds=2, progress=[])
        self.assertEqual(support.recommend(value)["action"], "diagnose_and_change_strategy")

    def test_progress_requires_receipt_and_closed_kind(self):
        for progress in ([{"kind": "edited_file", "receipt_sha256": "a" * 64}],
                         [{"kind": "red_green", "receipt_sha256": "not-a-digest"}],
                         [{"kind": "red_green"}]):
            with self.subTest(progress=progress):
                value = evidence()
                value["progress"] = progress
                with self.assertRaises(ValueError):
                    support.recommend(value)

    def test_stalled_counter_cannot_be_reset_by_claiming_progress(self):
        value = evidence()
        value["stalled_rounds"] = 2
        self.assertEqual(support.recommend(value)["action"], "diagnose_and_change_strategy")

    def test_old_stagnation_does_not_hide_current_approved_snapshot(self):
        for local_work in (True, False):
            with self.subTest(local_work=local_work):
                value = ready()
                value["stalled_rounds"] = 2
                value["review"] = {"state": "approved", "snapshot_current": True}
                value["authority"]["local_work"] = local_work
                result = support.recommend(value)
                self.assertEqual(result["action"], "await_owner_validation")
                self.assertFalse(result["ready_for_done"])

    def test_stagnation_without_local_pending_work_preserves_external_gate(self):
        for local_work in (True, False):
            with self.subTest(local_work=local_work):
                value = ready()
                value["stalled_rounds"] = 2
                value["authority"]["local_work"] = local_work
                self.assertEqual(support.recommend(value)["action"], "prepare_review_gate")

    def test_stagnation_with_pending_work_cannot_grant_local_authority(self):
        value = evidence()
        value["stalled_rounds"] = 2
        value["authority"]["local_work"] = False
        self.assertEqual(support.recommend(value)["action"], "prepare_local_gate")

    def test_audited_consecutive_counter_reset_preserves_total_and_external_gate(self):
        value = ready()
        value.update(review_rounds=13, stalled_rounds=0)
        value["progress"] = [{"kind": "blocker_closed", "receipt_sha256": "d" * 64}]
        self.assertEqual(support.recommend(value)["action"], "prepare_review_gate")
        self.assertEqual(value["review_rounds"], 13)
        self.assertEqual(value["authority"]["external_remaining"], 0)

    def test_zero_external_budget_does_not_block_local_fixes(self):
        self.assertEqual(support.recommend(evidence())["action"], "fix_and_test")

    def test_no_local_authorization_yields_gate_not_permission(self):
        value = evidence()
        value["authority"]["local_work"] = False
        result = support.recommend(value)
        self.assertEqual(result["action"], "prepare_local_gate")
        self.assertFalse(result["permissions_granted"])

    def test_failed_targeted_test_is_not_reviewer_ready(self):
        value = ready()
        value["verification"]["targeted"] = "failed"
        self.assertEqual(support.recommend(value)["action"], "fix_and_test")

    def test_each_missing_local_gate_is_preserved(self):
        for field, action in (("targeted", "run_targeted_tests"),
                              ("suite", "run_full_suite"),
                              ("mutations", "run_mutation_checks")):
            value = ready()
            value["verification"][field] = "not_run"
            self.assertEqual(support.recommend(value)["action"], action)

    def test_external_review_needs_covered_budget_not_round_count(self):
        for covered, remaining, expected in (
                (True, 1, "request_independent_review"),
                (False, 1, "prepare_review_gate"),
                (True, 0, "prepare_review_gate")):
            value = ready()
            value["review_rounds"] = 13
            value["authority"].update(external_covered=covered, external_remaining=remaining)
            self.assertEqual(support.recommend(value)["action"], expected)

    def test_old_review_is_not_approval_of_new_snapshot(self):
        value = ready()
        value["review"] = {"state": "approved", "snapshot_current": False}
        self.assertEqual(support.recommend(value)["action"], "prepare_review_gate")

    def test_current_failed_review_does_not_spend_generic_external_balance(self):
        for state, local, expected in (
                ("blocked", True, "audit_review_findings"),
                ("blocked", False, "prepare_local_gate"),
                ("unavailable", True, "prepare_review_gate"),
                ("unavailable", False, "prepare_review_gate")):
            with self.subTest(state=state, local=local):
                value = ready()
                value["review"] = {"state": state, "snapshot_current": True}
                value["authority"].update(
                    local_work=local, external_covered=True, external_remaining=1)
                result = support.recommend(value)
                self.assertEqual(result["action"], expected)
                self.assertFalse(result["permissions_granted"])
                self.assertEqual(value["authority"]["external_remaining"], 1)

    def test_blocked_current_review_with_confirmed_blocker_keeps_local_fix(self):
        value = evidence()
        value["review"]["snapshot_current"] = True
        value["authority"].update(external_covered=True, external_remaining=1)
        self.assertEqual(support.recommend(value)["action"], "fix_and_test")

    def test_repeated_current_review_audit_changes_strategy_not_external_retry(self):
        value = ready()
        value.update(stalled_rounds=2, progress=[])
        value["review"] = {"state": "blocked", "snapshot_current": True}
        value["authority"].update(external_covered=True, external_remaining=1)
        self.assertEqual(support.recommend(value)["action"], "diagnose_and_change_strategy")

    def test_jev_cannot_recommend_retry_after_current_transport_failure(self):
        value = ready()
        value["review"] = {"state": "unavailable", "snapshot_current": True}
        value["authority"].update(external_covered=True, external_remaining=1)
        response = receipt(value, "prepare_review_gate")
        response["response"]["answers"]["next_action"]["choice"] = "request_independent_review"
        observed = support.interpret_jev(value, response)
        self.assertEqual(observed["action"], "prepare_review_gate")
        self.assertEqual(observed["advice_status"], "rejected")

    def test_review_and_tests_never_close_card_without_owner(self):
        value = ready()
        value["review"] = {"state": "approved", "snapshot_current": True}
        result = support.recommend(value)
        self.assertEqual(result["action"], "await_owner_validation")
        self.assertFalse(result["ready_for_done"])
        self.assertFalse(result["permissions_granted"])
        self.assertEqual(result["network"], "disabled")

    def test_invalid_metadata_is_rejected_without_echoing_it(self):
        bad = []
        for field, value in (("risk", "low"), ("review_rounds", True),
                             ("blockers", -1), ("stalled_rounds", 1.5)):
            item = evidence()
            item[field] = value
            bad.append(item)
        extra = evidence()
        extra["raw_prompt"] = "patient or credential"
        bad.append(extra)
        for item in bad:
            with self.subTest(item=item):
                with self.assertRaises(ValueError):
                    support.recommend(item)

    def test_unhashable_enum_values_are_normalized_to_invalid_input(self):
        for field in ("risk", "defect_class", "evidence_gap"):
            value = evidence()
            value[field] = []
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    support.recommend(value)

    def test_duplicate_keys_are_rejected_even_in_otherwise_valid_evidence(self):
        with self.assertRaises(ValueError):
            support._unique([("schema", 1), ("schema", 1)])


class JevAdviceTest(unittest.TestCase):
    def test_frozen_request_digest_covers_exact_utf8_body_not_envelope(self):
        frozen = support.freeze_jev(evidence())
        body = frozen["request_body_utf8"].encode("utf-8")
        self.assertEqual(json.loads(body), frozen["request"])
        self.assertEqual(frozen["request_bytes"], len(body))
        self.assertEqual(frozen["request_sha256"], hashlib.sha256(body).hexdigest())
        self.assertNotEqual(len(body), len(frozen["request_body_utf8"]))
        self.assertEqual(frozen["network"], "disabled")

    def test_payload_is_metadata_only_and_not_permission_to_send(self):
        value = evidence()
        request = support.prepare_jev(value)
        self.assertEqual(request["model"], "jev-1.13.0")
        self.assertEqual(set(request), {"model", "state", "questions"})
        encoded = json.dumps(request)
        self.assertNotIn("receipt_sha256", encoded)
        self.assertNotIn("authority", request["state"])
        self.assertNotIn("API_KEY", encoded)
        self.assertNotIn("approve", request["questions"]["next_action"]["criteria"])

    def test_pinned_model_and_request_hash_are_required(self):
        value = evidence()
        for field in ("model", "request_sha256"):
            result = receipt(value, "fix_and_test")
            if field == "model":
                result["response"][field] = "jev-latest"
            else:
                result[field] = "b" * 64
            observed = support.interpret_jev(value, result)
            self.assertEqual(observed["source"], "local_rules")
            self.assertEqual(observed["advice_status"], "rejected")

    def test_valid_advice_can_change_order_of_local_investigation(self):
        value = evidence()
        observed = support.interpret_jev(value, receipt(value, "add_regression_case"))
        self.assertEqual(observed["source"], "jev_advice")
        self.assertEqual(observed["action"], "add_regression_case")
        self.assertFalse(observed["permissions_granted"])
        self.assertFalse(observed["ready_for_done"])

    def test_jev_cannot_skip_failed_tests_or_request_unbudgeted_review(self):
        value = evidence()
        result = receipt(value, "fix_and_test")
        result["response"]["answers"]["next_action"]["choice"] = "request_independent_review"
        probabilities = result["response"]["answers"]["next_action"]["probabilities"]
        for key in probabilities:
            probabilities[key] = 0
        probabilities["request_independent_review"] = 1
        observed = support.interpret_jev(value, result)
        self.assertEqual(observed["action"], "fix_and_test")
        self.assertEqual(observed["advice_status"], "rejected")

    def test_no_repeat_when_stalled_even_with_confident_advice(self):
        value = evidence()
        value["stalled_rounds"] = 2
        observed = support.interpret_jev(value, receipt(value, "diagnose_and_change_strategy"))
        self.assertEqual(observed["action"], "diagnose_and_change_strategy")

    def test_low_confidence_and_abstention_preserve_baseline(self):
        value = evidence()
        for choice, confidence, status in (("abstain", 0.99, "abstained"),
                                           ("abstain", 0.5, "abstained"),
                                           ("fix_and_test", 0.5, "low_confidence")):
            observed = support.interpret_jev(value, receipt(value, choice, confidence))
            self.assertEqual(observed["action"], "fix_and_test")
            self.assertEqual(observed["source"], "local_rules")
            self.assertEqual(observed["advice_status"], status)

    def test_confidence_boundary_accepts_only_at_or_above_threshold(self):
        value = evidence()
        for confidence, status, action in ((0.749, "low_confidence", "fix_and_test"),
                                           (0.75, "accepted", "add_regression_case")):
            with self.subTest(confidence=confidence):
                result = support.interpret_jev(
                    value, receipt(value, "add_regression_case", confidence))
                self.assertEqual(result["advice_status"], status)
                self.assertEqual(result["action"], action)

    def test_non_finite_probabilities_or_bool_confidence_are_rejected(self):
        value = evidence()
        for field, invalid in (("confidence", True), ("confidence", float("nan"))):
            result = receipt(value, "fix_and_test")
            result["response"]["answers"]["next_action"][field] = invalid
            self.assertEqual(support.interpret_jev(value, result)["advice_status"], "rejected")
        result = receipt(value, "fix_and_test")
        result["response"]["answers"]["next_action"]["probabilities"]["fix_and_test"] = 0.1
        self.assertEqual(support.interpret_jev(value, result)["advice_status"], "rejected")

    def test_new_snapshot_invalidates_previous_advice(self):
        value = evidence()
        old = receipt(value, "fix_and_test")
        value["snapshot_sha256"] = "d" * 64
        self.assertEqual(support.interpret_jev(value, old)["advice_status"], "rejected")


class OfflineCliTest(unittest.TestCase):
    script = Path(__file__).with_name("work_evidence.py")

    def test_helpers_do_not_use_network_or_spawn_external_cli(self):
        value = evidence()
        with patch("socket.socket", side_effect=AssertionError("NETWORK_FORBIDDEN")), \
                patch("urllib.request.urlopen", side_effect=AssertionError("NETWORK_FORBIDDEN")), \
                patch("subprocess.Popen", side_effect=AssertionError("SPAWN_FORBIDDEN")):
            support.recommend(value)
            support.prepare_jev(value)
            support.interpret_jev(value, receipt(value, "fix_and_test"))

    def test_real_cli_prepares_without_credentials_and_keeps_input_intact(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.json"
            path.write_text(json.dumps(evidence()), encoding="utf-8")
            original = path.read_bytes()
            result = subprocess.run(
                [sys.executable, str(self.script), "prepare-jev", str(path)],
                capture_output=True, text=True, check=False,
                env={"PYTHONDONTWRITEBYTECODE": "1", "TYPESAFE_API_KEY": "MUST_NOT_APPEAR"},
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            prepared = json.loads(result.stdout)
            self.assertEqual(prepared["network"], "disabled")
            self.assertEqual(prepared["request_bytes"],
                             len(prepared["request_body_utf8"].encode("utf-8")))
            self.assertEqual(prepared["request_sha256"],
                             support.request_digest(prepared["request"]))
            self.assertEqual(path.read_bytes(), original)
            self.assertNotIn("MUST_NOT_APPEAR", result.stdout + result.stderr)
            self.assertEqual(sorted(p.name for p in Path(directory).iterdir()), ["evidence.json"])

    def test_cli_rejects_duplicate_keys_and_oversize_without_raw_echo(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            duplicate = json.dumps(evidence())[:-1] + ', "schema":1}'
            for raw in (duplicate, "SENSITIVE" * 4096):
                path.write_text(raw, encoding="utf-8")
                result = subprocess.run(
                    [sys.executable, str(self.script), "recommend", str(path)],
                    capture_output=True, text=True, check=False,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("SENSITIVE", result.stdout + result.stderr)

    def test_cli_normalizes_deep_json_in_evidence_and_receipt_without_traceback(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested.json"
            path.write_text("[" * 1200 + "0" + "]" * 1200, encoding="utf-8")
            valid = Path(directory) / "evidence.json"
            valid.write_text(json.dumps(evidence()), encoding="utf-8")
            for args in (("recommend", str(path)),
                         ("interpret-jev", str(valid), str(path))):
                with self.subTest(mode=args[0]):
                    result = subprocess.run(
                        [sys.executable, str(self.script), *args],
                        capture_output=True, text=True, check=False,
                    )
                    if args[0] == "recommend":
                        self.assertEqual(result.returncode, 2)
                        self.assertEqual(result.stdout, "")
                        self.assertEqual(json.loads(result.stderr), {"error": "INVALID_INPUT"})
                    else:
                        self.assertEqual(result.returncode, 0, result.stderr)
                        self.assertEqual(json.loads(result.stdout)["action"], "fix_and_test")
                        self.assertEqual(json.loads(result.stdout)["advice_status"], "rejected")

    def test_cli_bad_receipt_keeps_local_rules_without_echo_or_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            value = ready()
            value["authority"].update(external_covered=True, external_remaining=1)
            valid = Path(directory) / "evidence.json"
            valid.write_text(json.dumps(value), encoding="utf-8")
            bad = Path(directory) / "receipt.json"
            for raw in ('{"schema":1,"schema":1}', "SECRET" * 4096, b"\xff", None):
                with self.subTest(kind=type(raw).__name__):
                    if raw is None:
                        bad.unlink()
                    elif isinstance(raw, bytes):
                        bad.write_bytes(raw)
                    else:
                        bad.write_text(raw, encoding="utf-8")
                    result = subprocess.run(
                        [sys.executable, str(self.script), "interpret-jev", str(valid), str(bad)],
                        capture_output=True, text=True, check=False,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    observed = json.loads(result.stdout)
                    self.assertEqual(observed["action"], "request_independent_review")
                    self.assertEqual(observed["source"], "local_rules")
                    self.assertEqual(observed["advice_status"], "rejected")
                    self.assertFalse(observed["permissions_granted"])
                    self.assertNotIn("SECRET", result.stdout + result.stderr)


class PolicyConsumersTest(unittest.TestCase):
    """Guardas de instrução; não são prova comportamental de uma LLM."""

    root = Path(__file__).resolve().parents[1]

    def test_each_consumer_uses_the_same_continuity_policy(self):
        for relative in ("commands/revisar.md", "commands/implement-next.md",
                         "commands/dormir.md", "skills/orq/SKILL.md"):
            text = (self.root / relative).read_text(encoding="utf-8")
            with self.subTest(consumer=relative):
                self.assertIn("ORQ_PACKAGE_ROOT/references/continuidade-evidencias.md", text)
                if relative.startswith("commands/"):
                    self.assertNotRegex(text, r"Máximo\s+(?:\*\*)?2\s+rodadas")

    def test_stagnation_is_not_in_the_night_global_stop_conditions(self):
        text = (self.root / "commands/dormir.md").read_text(encoding="utf-8")
        self.assertNotIn("qualquer uma destas encerra o modo", text)
        self.assertIn("estacionam a dependência, não a fila inteira", text)
        self.assertIn("orçamento do manifesto", text)
        self.assertIn("parada humana", text)
        self.assertIn("ausência de card elegível", text)


if __name__ == "__main__":
    unittest.main()
