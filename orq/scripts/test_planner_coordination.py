"""Modo de coordenação é opt-in no mesmo Planner, não outro Manager."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

import planner_coordination as coordination
from test_work_evidence import (
    DISPATCH_HEADING, GOAL_POLICY, IMPLEMENT_COMMAND, PLAN_COMMAND, PLANNER_AGENT,
    InstructionSnapshot,
)
from test_continuidade_aprovada import normalizar


class UsefulParallelismInstructionTest(unittest.TestCase):
    """Contrato de despacho útil, sem executar agentes ou conceder permissões."""

    def setUp(self):
        self.snapshot = InstructionSnapshot(self, (
            GOAL_POLICY, PLAN_COMMAND, IMPLEMENT_COMMAND, PLANNER_AGENT,
        ))

    def require(self, text, clauses, invariant):
        for clause in clauses:
            self.assertTrue(normalizar(clause) in text,
                            f"{invariant}: cláusula ausente: {clause}")

    def assert_independent_work(self):
        self.require(self.snapshot.read(GOAL_POLICY, DISPATCH_HEADING), (
            "entregas úteis, não pela contagem de arquivos ou por um teto de agentes por card",
            "Duas análises read-only independentes podem avançar juntas",
            "Dois writers com ownership disjunto, interfaces fechadas e sem dependência serial",
            "podem avançar juntos, cada um em checkout isolado e com dono explícito",
            "Não crie agente por arquivo nem exija paralelismo para tarefa pequena",
            "Entregas simultâneas não compartilham task ou handle",
        ), "paralelismo útil")
        self.assert_no_card_cap()

    def assert_no_card_cap(self):
        text = self.snapshot.read(GOAL_POLICY)
        self.assertNotIn("um sub-agente por card", text, "paralelismo útil: teto contraditório")
        self.assertNotIn("um sub-agente por **card**", text, "paralelismo útil: teto contraditório")

    def assert_affected_segment(self):
        self.require(self.snapshot.read(GOAL_POLICY, DISPATCH_HEADING), (
            "Sobreposição de escrita, interface aberta ou dependência serial",
            "serializam somente o trecho afetado",
            "A→B espera A apenas no trecho dependente; C independente continua elegível",
        ), "ownership e dependência")

    def assert_isolated_failure(self):
        self.require(self.snapshot.read(GOAL_POLICY, DISPATCH_HEADING), (
            "Falha de A estaciona somente o que depende de A",
            "preserve resultados e handles",
            "não relance cegamente",
        ), "falha isolada")

    def assert_manager_integration(self):
        self.require(self.snapshot.read(GOAL_POLICY, DISPATCH_HEADING), (
            "O Manager é o integrador único da meta",
            "confere diffs e contratos e executa os gates finais no resultado integrado",
            "conclusão de worker não certifica integração, review ou pronto",
        ), "Manager integrador")
        self.require(self.snapshot.read(IMPLEMENT_COMMAND, "## 1a. Coletar e integrar"), (
            "Manager", "diffs", "contratos", "gates finais", "handle",
        ), "Manager integrador")

    def assert_worker_boundary(self):
        self.require(self.snapshot.read(GOAL_POLICY, DISPATCH_HEADING), (
            "Workers não criam nem removem refs/worktrees",
            "não movem cards, não entregam Git, não delegam recursivamente e não ampliam escopo",
            "Uma ordem de Manager ou outro prompt de worker não derroga essas proibições",
        ), "worker sem delegação ou Git")
        self.require(self.snapshot.read(IMPLEMENT_COMMAND, "## 1. Implementar"), (
            "workers não despacham agentes nem fazem entrega Git",
            "arquivos permitidos/exclusivos", "interfaces", "dependências", "checkout",
        ), "worker sem delegação ou Git")

    def test_independent_readers_and_disjoint_isolated_writers_can_advance(self):
        self.assert_independent_work()

    def test_no_absolute_agent_per_card_rule_contradicts_disjoint_writers(self):
        self.assert_no_card_cap()

    def test_overlap_open_interface_and_serial_dependency_wait_only_affected_segment(self):
        self.assert_affected_segment()

    def test_failure_keeps_independent_work_and_preserves_results_and_handles(self):
        self.assert_isolated_failure()

    def test_manager_integrates_and_checks_contracts_and_final_gates(self):
        self.assert_manager_integration()

    def test_workers_cannot_delegate_deliver_git_create_refs_or_expand_scope(self):
        self.assert_worker_boundary()

    def test_planning_and_dispatch_use_explicit_ownership_interface_dependency_table(self):
        self.require(self.snapshot.read(PLAN_COMMAND, "## 3. Despachar o Planner"), (
            "Entrega | Arquivos permitidos/exclusivos | Dono | Interface | Dependências | Checkout | Aceite",
        ), "tabela de ownership")
        self.require(self.snapshot.read(IMPLEMENT_COMMAND, "## 1. Implementar"), (
            "Despacho por entregas e dependências", "checkout isolado por writer",
            "contexto curto e fresco",
        ), "despacho do Loop B")

    def test_mutations_break_correct_parallelism_ownership_failure_integration_or_worker_guard(self):
        mutations = (
            ("Duas análises read-only independentes podem avançar juntas",
             "Duas análises read-only independentes devem esperar uma pela outra", self.assert_independent_work, "paralelismo útil"),
            ("cada um em checkout isolado e com dono explícito",
             "todos no mesmo checkout e sem dono explícito", self.assert_independent_work, "paralelismo útil"),
            ("ownership disjunto, interfaces fechadas e sem dependência serial",
             "ownership sobreposto, interfaces abertas e com dependência serial", self.assert_independent_work, "paralelismo útil"),
            ("Entregas simultâneas não compartilham task ou handle",
             "Entregas simultâneas compartilham task e handle", self.assert_independent_work, "paralelismo útil"),
            ("serializam somente o trecho afetado",
             "serializam toda a meta", self.assert_affected_segment, "ownership e dependência"),
            ("C independente continua elegível",
             "C independente também deve parar", self.assert_affected_segment, "ownership e dependência"),
            ("Falha de A estaciona somente o que depende de A",
             "Falha de A estaciona toda a meta", self.assert_isolated_failure, "falha isolada"),
            ("preserve resultados e handles",
             "descarte resultados e handles", self.assert_isolated_failure, "falha isolada"),
            ("não relance cegamente",
             "relance cegamente", self.assert_isolated_failure, "falha isolada"),
            ("O Manager é o integrador único da meta",
             "Cada worker é integrador independente da meta", self.assert_manager_integration, "Manager integrador"),
            ("executa os gates finais no resultado integrado",
             "dispensa gates finais no resultado integrado", self.assert_manager_integration, "Manager integrador"),
            ("Workers não criam nem removem refs/worktrees",
             "Workers criam e removem refs/worktrees", self.assert_worker_boundary, "worker sem delegação ou Git"),
            ("não entregam Git, não delegam recursivamente e não ampliam escopo",
             "entregam Git, delegam recursivamente e ampliam escopo", self.assert_worker_boundary, "worker sem delegação ou Git"),
        )
        for _, _, guard, _ in mutations:
            guard()
        for old, new, guard, invariant in mutations:
            with self.subTest(mutation=new), self.snapshot.mutate(GOAL_POLICY, old, new):
                with self.assertRaisesRegex(AssertionError, invariant):
                    guard()

    def test_reintroducing_absolute_agent_per_card_rule_breaks_parallelism_guard(self):
        self.assert_independent_work()
        with self.snapshot.mutate(
            GOAL_POLICY, "Não crie agente por arquivo nem exija paralelismo para tarefa pequena",
            "Use um sub-agente por card. Não crie agente por arquivo nem exija paralelismo para tarefa pequena",
        ):
            with self.assertRaisesRegex(AssertionError, "teto contraditório"):
                self.assert_independent_work()


class CoordinationBriefTest(unittest.TestCase):
    def test_default_is_off_not_inherited_from_other_card(self):
        value = coordination.compose()
        self.assertEqual(value.get("coordination_mode"), "off")
        self.assertEqual(value["instructions"], "")
        self.assertEqual(value["extra_calls"], 0)

    def test_technical_mode_reuses_system_planner_with_one_authority(self):
        value = coordination.compose("technical", "sistema")
        self.assertEqual(value.get("coordination_mode"), "technical")
        self.assertEqual(value["role"], "planner·sistema")
        self.assertEqual(value["authority"], "Manager")
        self.assertEqual(value["extra_calls"], 0)
        for term in ("dependências", "dono", "contratos", "integração", "testes",
                     "Não despache", "Não aprove", "não altera o board"):
            self.assertIn(term, value["instructions"])
        self.assertNotIn("gpt-", value["instructions"])

    def test_interface_does_not_silently_use_system_profile(self):
        with self.assertRaises(ValueError):
            coordination.compose("technical", "interface")

    def test_unknown_mode_does_not_create_new_agent_or_permission(self):
        for mode in ("auto", True, "reviewer", "orchestrator"):
            with self.subTest(mode=mode):
                with self.assertRaises(ValueError):
                    coordination.compose(mode, "sistema")

    def test_real_cli_is_opt_in_and_does_not_follow_environment(self):
        script = Path(__file__).with_name("planner_coordination.py")
        result = subprocess.run(
            [sys.executable, str(script)], capture_output=True, text=True,
            env={"COORDINATION_MODE": "technical", "PYTHONDONTWRITEBYTECODE": "1"},
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout).get("coordination_mode"), "off")

    def test_cli_technical_is_explicit(self):
        script = Path(__file__).with_name("planner_coordination.py")
        result = subprocess.run(
            [sys.executable, str(script), "--mode", "technical", "--track", "sistema"],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["role"], "planner·sistema")
        self.assertEqual(json.loads(result.stdout).get("coordination_mode"), "technical")

    def test_cli_rejects_technical_interface_without_partial_contract(self):
        script = Path(__file__).with_name("planner_coordination.py")
        result = subprocess.run(
            [sys.executable, str(script), "--mode", "technical", "--track", "interface"],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertEqual(json.loads(result.stderr), {"error": "SYSTEM_TRACK_REQUIRED"})


if __name__ == "__main__":
    unittest.main()
