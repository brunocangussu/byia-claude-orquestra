#!/usr/bin/env python3
"""Testes do medidor de progresso (`progress.py`).

O medidor é o contrato entre Manager, hosts e vistas: se ele mente, a barra mente. Os testes cobrem
o cálculo puro, as transições, a persistência transacional (lock, revisão, dono, troca atômica), os
leitores estritos (`show`/`watch`), o armazenamento ignorado pelo Git e o parser do board. Tudo roda
em diretórios temporários e repositórios Git temporários, nunca no repositório real.
"""

from __future__ import annotations

import copy
from datetime import datetime, timedelta
import errno
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import queue
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest import mock

SCRIPT = Path(__file__).resolve().with_name("progress.py")
SCHEMA = Path(__file__).resolve().parents[1] / "schemas" / "progress-ledger-v1.json"

_spec = importlib.util.spec_from_file_location("orq_progress", SCRIPT)
progress = importlib.util.module_from_spec(_spec)
sys.modules["orq_progress"] = progress
_spec.loader.exec_module(progress)

KEY_A = "a" * 64
KEY_B = "b" * 64
NOW = "2026-10-04T13:00:00Z"
RUN = "11111111-1111-4111-8111-111111111111"
EXECUTOR = {"host": "codex", "role": "implementer", "label": "normal"}
BOARD_READY = {"state": "ok", "card": "T-144", "marker": "~"}


def task(task_id: str, size: str = "M", title: str = "", acceptance: str = "A01") -> dict:
    return {"id": task_id, "title": title or f"Entrega {task_id}", "size": size, "acceptance_ref": acceptance}


def plan_op(tasks: list, **extra) -> dict:
    data = {"source_ref": "docs/plano.md#passos", "approval_ref": "threads/T-144.md#aprovacao", "tasks": tasks}
    data.update(extra)
    return {"op": "plan", "input": data, "board_state": BOARD_READY}


def goal_ledger() -> dict:
    scope = {"front_root": "/tmp/frente", "front": None, "card_id": None, "board_path": None, "thread_root": None}
    return progress.new_ledger("goal", "claude", KEY_A, scope, NOW, RUN)


def card_ledger() -> dict:
    scope = {
        "front_root": "/tmp/frente",
        "front": "frente-mods",
        "card_id": "T-144",
        "board_path": "/tmp/principal/memory/wiki/KANBAN.md",
        "thread_root": "/tmp/frente/memory/wiki",
    }
    return progress.new_ledger("card", "claude", KEY_A, scope, NOW, RUN)


def step(ledger: dict, *operations: dict) -> dict:
    """Aplica operações em sequência com relógio crescente, como o Manager faria."""
    base = datetime(2026, 10, 4, 13, 0, 0)
    for index, operation in enumerate(operations, 1):
        ledger = progress.apply_operation(ledger, operation, (base + timedelta(seconds=index)).strftime("%Y-%m-%dT%H:%M:%SZ"))
    return ledger


def start(task_id: str) -> dict:
    return {"op": "start", "task": task_id, "executor": dict(EXECUTOR)}


def done(task_id: str, ref: str = "suite-ok") -> dict:
    return {"op": "done", "task": task_id, "evidence_ref": ref}


def finish(*ids: str) -> list:
    operations = []
    for task_id in ids:
        operations.extend([start(task_id), done(task_id)])
    return operations


def percent_of(ledger: dict):
    return progress.calculate_progress(ledger)["percent"]


class ProgressCalculoTest(unittest.TestCase):
    def test_exemplo_do_plano_11_de_16_unidades_da_69_por_cento(self):
        # Pesos 3+3+3+2+2+1+1+1 = 16; concluídos L,L,M,M,S = 11 unidades em 5 de 8 tarefas.
        sizes = ["L", "L", "L", "M", "M", "S", "S", "S"]
        ledger = step(goal_ledger(), plan_op([task(f"P0{i + 1}", s) for i, s in enumerate(sizes)]))
        ledger = step(ledger, *finish("P01", "P02", "P04", "P05", "P06"))
        result = progress.calculate_progress(ledger)
        self.assertEqual((result["weight_done"], result["weight_total"]), (11, 16))
        self.assertEqual((result["tasks_done"], result["tasks_total"]), (5, 8))
        self.assertEqual(result["percent"], 69)

    def test_pesos_s_m_l_sao_1_2_3(self):
        self.assertEqual(progress.SIZE_WEIGHTS, {"S": 1, "M": 2, "L": 3})
        ledger = step(goal_ledger(), plan_op([task("P01", "S"), task("P02", "L")]), *finish("P02"))
        self.assertEqual(percent_of(ledger), 75)

    def test_arredondamento_e_meio_para_cima_e_nao_para_o_par(self):
        # 1 de 8 unidades = 12,5%: round() de Python daria 12; o medidor arredonda para 13.
        ledger = step(goal_ledger(), plan_op([task(f"P0{i}", "S") for i in range(1, 9)]), *finish("P01"))
        self.assertEqual(percent_of(ledger), 13)

    def test_sem_plano_nao_tem_percentual_nem_zero_ficticio(self):
        result = progress.calculate_progress(goal_ledger())
        self.assertIsNone(result["percent"])
        self.assertEqual(result["state"], "sem-plano")
        self.assertIn("sem plano registrado", progress.render_text(progress.build_view(goal_ledger(), None)))

    def test_todas_descartadas_nunca_vira_100_por_cento(self):
        ledger = step(goal_ledger(), plan_op([task("P01"), task("P02")]))
        ledger = step(
            ledger,
            {"op": "drop", "task": "P01", "reason": "obsolete", "evidence_ref": "r1"},
            {"op": "drop", "task": "P02", "reason": "duplicate", "evidence_ref": "r2"},
        )
        result = progress.calculate_progress(ledger)
        self.assertIsNone(result["percent"])
        self.assertEqual(result["state"], "sem-passos-ativos")
        text = progress.render_text(progress.build_view(ledger, None))
        self.assertIn("sem passos ativos", text)
        self.assertNotIn("100%", text)

    def test_teto_de_99_enquanto_houver_tarefa_nao_concluida(self):
        sizes = ["L"] * 67 + ["S"]
        ledger = step(goal_ledger(), plan_op([task(f"P{i:03d}", size) for i, size in enumerate(sizes)]))
        ledger = step(ledger, *finish(*[f"P{i:03d}" for i in range(67)]))
        # 201/202 = 99,5% arredondaria para 100; falta uma tarefa, então o teto vale.
        self.assertEqual(percent_of(ledger), 99)
        ledger = step(ledger, *finish("P067"))
        self.assertEqual(percent_of(ledger), 100)

    def test_tarefas_paralelas_ficam_todas_em_execucao(self):
        ledger = step(goal_ledger(), plan_op([task("P01"), task("P02"), task("P03")]), start("P01"), start("P02"))
        view = progress.build_view(ledger, None)
        self.assertEqual([item["id"] for item in view["active"]], ["P01", "P02"])
        self.assertIn("Em execução: P01 — Entrega P01 · implementer/normal; P02", progress.render_text(view))

    def test_acrescentar_trabalho_derruba_o_percentual_e_mostra_o_crescimento_do_plano(self):
        ledger = step(goal_ledger(), plan_op([task("P01"), task("P02")]), *finish("P01"))
        before = percent_of(ledger)
        ledger = step(
            ledger,
            {
                "op": "add",
                "input": {"reason": "scope_change", "evidence_ref": "threads/T-144.md#ajuste", "tasks": [task("P03", "L")]},
            },
        )
        self.assertLess(percent_of(ledger), before)
        text = progress.render_text(progress.build_view(ledger, None))
        self.assertIn("Plano: 2 → 3 passos", text)

    def test_reabrir_tarefa_concluida_reduz_o_progresso_e_preserva_as_referencias(self):
        ledger = step(goal_ledger(), plan_op([task("P01"), task("P02")]), *finish("P01", "P02"))
        self.assertEqual(percent_of(ledger), 100)
        ledger = step(ledger, {"op": "reopen", "task": "P02", "evidence_ref": "falha-na-revisao"})
        self.assertEqual(percent_of(ledger), 50)
        reopened = ledger["tasks"][1]
        self.assertEqual(reopened["status"], "pending")
        self.assertEqual(reopened["evidence_refs"], ["suite-ok", "falha-na-revisao"])
        self.assertIsNone(reopened["finished_at"])

    def test_descartar_tira_o_peso_do_denominador_e_preserva_a_tarefa(self):
        ledger = step(goal_ledger(), plan_op([task("P01", "S"), task("P02", "L")]), *finish("P01"))
        self.assertEqual(percent_of(ledger), 25)
        ledger = step(ledger, {"op": "drop", "task": "P02", "reason": "scope_change", "evidence_ref": "threads/T-144.md#x"})
        self.assertEqual(len(ledger["tasks"]), 2)
        self.assertEqual(ledger["tasks"][1]["status"], "dropped")
        self.assertEqual(ledger["tasks"][1]["change_reason"], "scope_change")
        self.assertEqual(percent_of(ledger), 100)


class ProgressOperacoesTest(unittest.TestCase):
    def test_apply_operation_nao_altera_a_entrada_nem_acessa_disco(self):
        ledger = step(goal_ledger(), plan_op([task("P01")]))
        frozen = copy.deepcopy(ledger)
        with mock.patch("builtins.open", side_effect=AssertionError("acesso a disco")), mock.patch.object(
            progress.os, "replace", side_effect=AssertionError("acesso a disco")
        ):
            updated = progress.apply_operation(ledger, start("P01"), "2026-10-04T14:00:00Z")
        self.assertEqual(ledger, frozen)
        self.assertEqual(updated["revision"], ledger["revision"] + 1)
        self.assertEqual(updated["updated_at"], "2026-10-04T14:00:00Z")

    def test_plano_repetido_com_a_mesma_semente_e_idempotente(self):
        ledger = step(goal_ledger(), plan_op([task("P01"), task("P02")]), *finish("P01"))
        again = progress.apply_operation(ledger, plan_op([task("P01"), task("P02")]), "2026-10-04T15:00:00Z")
        self.assertEqual(again, ledger)  # nem duplica tarefa, nem desfaz conclusão, nem sobe a revisão

    def test_plano_com_outra_semente_e_rejeitado_sem_substituir_o_existente(self):
        ledger = step(goal_ledger(), plan_op([task("P01")]))
        with self.assertRaises(progress.InputError) as caught:
            progress.apply_operation(ledger, plan_op([task("P01"), task("P02")]), NOW)
        self.assertEqual(caught.exception.code, "plano-divergente")

    def test_semente_e_o_sha256_do_json_canonico_e_a_ordem_importa(self):
        tasks = [task("P01"), task("P02")]
        ledger = step(goal_ledger(), plan_op(tasks))
        seed = {"source_ref": "docs/plano.md#passos", "approval_ref": "threads/T-144.md#aprovacao", "tasks": tasks}
        expected = hashlib.sha256(
            json.dumps(seed, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        ).hexdigest()
        self.assertEqual(ledger["plan"]["seed_sha256"], expected)
        swapped = step(goal_ledger(), plan_op(list(reversed(tasks))))
        self.assertNotEqual(swapped["plan"]["seed_sha256"], expected)
        self.assertEqual([item["id"] for item in ledger["tasks"]], ["P01", "P02"])
        self.assertEqual((ledger["plan"]["baseline_count"], ledger["plan"]["baseline_weight"]), (2, 4))

    def test_plano_de_card_exige_referencias_e_board_ready(self):
        with self.assertRaises(progress.InputError):
            step(card_ledger(), {"op": "plan", "input": {"source_ref": "x", "approval_ref": None, "tasks": [task("P01")]}, "board_state": BOARD_READY})
        for marker in (" ", ">", "!", "?", "x"):
            with self.subTest(marker=marker), self.assertRaises(progress.InputError) as caught:
                step(card_ledger(), {**plan_op([task("P01")]), "board_state": {"state": "ok", "card": "T-144", "marker": marker}})
            self.assertEqual(caught.exception.code, "board-incompativel")
        for board_state in (None, {"state": "erro", "code": "card-ausente"}):
            with self.subTest(board_state=board_state), self.assertRaises(progress.UnavailableError):
                step(card_ledger(), {**plan_op([task("P01")]), "board_state": board_state})
        self.assertEqual(len(step(card_ledger(), plan_op([task("P01")]))["tasks"]), 1)

    def test_plano_de_goal_aceita_aprovacao_nula_e_nao_consulta_board(self):
        data = {"source_ref": None, "approval_ref": None, "tasks": [task("P01")]}
        ledger = step(goal_ledger(), {"op": "plan", "input": data})
        self.assertIsNone(ledger["plan"]["approval_ref"])

    def test_add_exige_plano_motivo_e_evidencia_e_ids_novos(self):
        add = {"op": "add", "input": {"reason": "scope_change", "evidence_ref": "t#x", "tasks": [task("P02")]}}
        with self.assertRaises(progress.InputError) as caught:
            step(goal_ledger(), add)
        self.assertEqual(caught.exception.code, "sem-plano")
        ledger = step(goal_ledger(), plan_op([task("P01")]), add)
        self.assertEqual(ledger["tasks"][1]["change_reason"], "scope_change")
        self.assertEqual(ledger["tasks"][1]["evidence_refs"], ["t#x"])
        for broken in ({"reason": "outro", "evidence_ref": "t#x", "tasks": [task("P03")]}, {"reason": "scope_change", "tasks": [task("P03")]}):
            with self.subTest(broken=broken), self.assertRaises(progress.InputError):
                step(ledger, {"op": "add", "input": broken})

    def test_add_repetido_e_idempotente_mas_id_conflitante_ou_descartado_e_erro(self):
        ledger = step(goal_ledger(), plan_op([task("P01")]))
        add = {"op": "add", "input": {"reason": "scope_change", "evidence_ref": "t#x", "tasks": [task("P02", "S", "Novo")]}}
        ledger = step(ledger, add)
        self.assertEqual(step(ledger, add), ledger)  # mesmo conteúdo: nada muda
        different = {"op": "add", "input": {"reason": "scope_change", "evidence_ref": "t#x", "tasks": [task("P02", "L", "Novo")]}}
        with self.assertRaises(progress.InputError) as caught:
            step(ledger, different)
        self.assertEqual(caught.exception.code, "id-conflitante")
        ledger = step(ledger, {"op": "drop", "task": "P02", "reason": "duplicate", "evidence_ref": "r"})
        with self.assertRaises(progress.InputError):
            step(ledger, add)  # tarefa descartada não é reutilizada; ID novo

    def test_id_repetido_dentro_da_mesma_entrada_e_rejeitado(self):
        with self.assertRaises(progress.InputError) as caught:
            step(goal_ledger(), plan_op([task("P01"), task("P01", "S")]))
        self.assertEqual(caught.exception.code, "id-repetido")

    def test_limite_de_200_passos_vale_no_plano_e_no_add(self):
        with self.assertRaises(progress.InputError) as caught:
            step(goal_ledger(), plan_op([task(f"P{i:03d}", "S") for i in range(201)]))
        self.assertEqual(caught.exception.code, "limite-tarefas")
        full = step(goal_ledger(), plan_op([task(f"P{i:03d}", "S") for i in range(200)]))
        add = {"op": "add", "input": {"reason": "scope_change", "evidence_ref": "t#x", "tasks": [task("EXTRA", "S")]}}
        with self.assertRaises(progress.InputError):
            step(full, add)

    def test_entrada_com_campo_de_prompt_ou_transcript_e_rejeitada(self):
        for field in ("prompt", "transcript", "stdout", "diff", "notes", "command"):
            with self.subTest(field=field):
                with self.assertRaises(progress.InputError):
                    step(goal_ledger(), plan_op([{**task("P01"), field: "texto livre"}]))
                with self.assertRaises(progress.InputError):
                    step(goal_ledger(), plan_op([task("P01")], **{field: "texto livre"}))

    def test_transicoes_validas_e_invalidas(self):
        ledger = step(goal_ledger(), plan_op([task("P01"), task("P02")]))
        with self.assertRaises(progress.InputError):  # done sem start
            step(ledger, done("P01"))
        with self.assertRaises(progress.InputError):  # reopen de tarefa não concluída
            step(ledger, {"op": "reopen", "task": "P01", "evidence_ref": "r"})
        with self.assertRaises(progress.InputError):  # tarefa inexistente
            step(ledger, start("P99"))
        ledger = step(ledger, start("P01"), done("P01"))
        with self.assertRaises(progress.InputError):  # start em tarefa concluída
            step(ledger, start("P01"))
        with self.assertRaises(progress.InputError):  # drop de tarefa concluída
            step(ledger, {"op": "drop", "task": "P01", "reason": "obsolete", "evidence_ref": "r"})

    def test_conclusao_exige_evidencia_e_a_evidencia_e_referencia_nao_conteudo(self):
        ledger = step(goal_ledger(), plan_op([task("P01")]), start("P01"))
        for ref in (None, "", "testes passaram 447 de 447", "linha\nquebrada", "x" * 201):
            with self.subTest(ref=ref), self.assertRaises(progress.InputError):
                step(ledger, {"op": "done", "task": "P01", "evidence_ref": ref})

    def test_repeticao_exata_e_idempotente_e_conteudo_incompativel_e_erro(self):
        ledger = step(goal_ledger(), plan_op([task("P01")]), start("P01"))
        self.assertEqual(step(ledger, start("P01")), ledger)
        with self.assertRaises(progress.InputError):  # outro executor sobre tarefa já ativa
            step(ledger, {"op": "start", "task": "P01", "executor": {**EXECUTOR, "label": "outro"}})
        finished = step(ledger, done("P01", "ev-1"))
        self.assertEqual(step(finished, done("P01", "ev-1")), finished)
        with self.assertRaises(progress.InputError):
            step(finished, done("P01", "ev-2"))

    def test_fase_pausa_e_encerramento(self):
        ledger = step(card_ledger(), plan_op([task("P01")]))
        self.assertEqual(step(ledger, {"op": "phase", "value": "review"})["activity"], "review")
        with self.assertRaises(progress.InputError):
            step(ledger, {"op": "phase", "value": "execution"})  # atividade de goal em card
        with self.assertRaises(progress.InputError):
            step(goal_ledger(), {"op": "phase", "value": "review"})
        paused = step(ledger, {"op": "pause"})
        self.assertEqual(step(paused, {"op": "pause"}), paused)
        with self.assertRaises(progress.InputError) as caught:
            step(paused, start("P01"))
        self.assertEqual(caught.exception.code, "ledger-pausado")
        self.assertEqual(step(paused, {"op": "resume"})["lifecycle"], "active")

    def test_close_de_card_concluido_exige_x_no_board_e_encerrado_e_terminal(self):
        ledger = step(card_ledger(), plan_op([task("P01")]))
        close = {"op": "close", "outcome": "reported_complete", "evidence_ref": "threads/T-144.md#validado"}
        with self.assertRaises(progress.InputError):
            step(ledger, {**close, "board_state": {"state": "ok", "card": "T-144", "marker": "?"}})
        with self.assertRaises(progress.UnavailableError):
            step(ledger, close)
        closed = step(ledger, {**close, "board_state": {"state": "ok", "card": "T-144", "marker": "x"}})
        self.assertEqual(closed["lifecycle"], "closed")
        self.assertEqual(closed["closure"]["outcome"], "reported_complete")
        self.assertEqual(step(closed, {**close, "board_state": {"state": "ok", "card": "T-144", "marker": "x"}}), closed)
        with self.assertRaises(progress.InputError):
            step(closed, start("P01"))
        with self.assertRaises(progress.InputError):
            step(closed, {"op": "close", "outcome": "cancelled", "evidence_ref": "outro"})
        cancelled = step(ledger, {"op": "close", "outcome": "cancelled", "evidence_ref": "t#cancelado"})
        self.assertEqual(cancelled["closure"]["outcome"], "cancelled")

    def test_close_de_goal_registra_so_a_declaracao_do_manager(self):
        closed = step(goal_ledger(), {"op": "close", "outcome": "reported_complete", "evidence_ref": "t#fim"})
        view = progress.build_view(closed, None)
        self.assertIn("execução encerrada pelo Manager", progress.render_text(view))
        self.assertNotIn("aprovad", progress.render_text(view))

    def test_claim_transfere_o_dono_somente_com_o_dono_esperado(self):
        ledger = goal_ledger()
        claim = {"op": "claim", "host": "codex", "expected_owner": KEY_A, "new_session_key": KEY_B}
        claimed = step(ledger, claim)
        self.assertEqual(claimed["owner"], {"host": "codex", "session_key": KEY_B})
        self.assertEqual(step(claimed, claim), claimed)  # repetição pelo mesmo novo dono
        with self.assertRaises(progress.ConflictError):
            step(claimed, {**claim, "new_session_key": "c" * 64})  # dono esperado já não é o atual


class ProgressValidacaoTest(unittest.TestCase):
    def valid(self) -> dict:
        return step(goal_ledger(), plan_op([task("P01")]))

    def assertInvalid(self, ledger: dict, fragment: str = "") -> None:
        with self.assertRaises(progress.LedgerValidationError) as caught:
            progress.validate_ledger(ledger)
        self.assertIn(fragment, str(caught.exception))

    def test_ledger_valido_passa(self):
        ledger = self.valid()
        self.assertIs(progress.validate_ledger(ledger), ledger)

    def test_versao_desconhecida_gera_erro_explicito(self):
        ledger = self.valid()
        ledger["schema_version"] = 2
        with self.assertRaises(progress.LedgerValidationError) as caught:
            progress.validate_ledger(ledger)
        self.assertEqual(caught.exception.code, "versao-desconhecida")
        self.assertIn("schema_version desconhecida", str(caught.exception))

    def test_campos_de_prompt_transcript_stdout_e_diff_sao_proibidos_em_qualquer_nivel(self):
        for field in ("prompt", "goal_condition", "notes", "command", "stdout", "diff", "transcript"):
            with self.subTest(field=field):
                top = self.valid()
                top[field] = "x"
                self.assertInvalid(top, "campos não permitidos")
                nested = self.valid()
                nested["tasks"][0][field] = "x"
                self.assertInvalid(nested, "campos não permitidos")

    def test_titulo_sem_controles_de_terminal_e_com_limite(self):
        for title in ("a\x1b[31mvermelho", "linha\nquebrada", "tab\taqui", "nul\x00", "bidi‮oculto", "sep linha", "x" * 161, "   "):
            with self.subTest(title=title):
                ledger = self.valid()
                ledger["tasks"][0]["title"] = title
                self.assertInvalid(ledger, "title")
        ledger = self.valid()
        ledger["tasks"][0]["title"] = "Título com acentuação, ü e 日本語 " + "x" * 120
        progress.validate_ledger(ledger)

    def test_limite_de_200_tarefas_e_ids_unicos_e_ascii(self):
        ledger = self.valid()
        ledger["tasks"] = [{**copy.deepcopy(ledger["tasks"][0]), "id": f"P{i:03d}"} for i in range(201)]
        self.assertInvalid(ledger, "200")
        ledger = self.valid()
        ledger["tasks"].append(copy.deepcopy(ledger["tasks"][0]))
        self.assertInvalid(ledger, "ID repetido")
        for bad in ("P 01", "P/01", "Pç1", "", "P" * 33):
            with self.subTest(task_id=bad):
                ledger = self.valid()
                ledger["tasks"][0]["id"] = bad
                self.assertInvalid(ledger, "id")

    def test_invariantes_de_estado_da_tarefa(self):
        done_ledger = step(goal_ledger(), plan_op([task("P01")]), *finish("P01"))
        broken = copy.deepcopy(done_ledger)
        broken["tasks"][0]["evidence_refs"] = []
        self.assertInvalid(broken, "evidência")
        broken = copy.deepcopy(done_ledger)
        broken["tasks"][0]["status"] = "active"
        self.assertInvalid(broken)
        pending = self.valid()
        pending["tasks"][0]["executor"] = dict(EXECUTOR)
        self.assertInvalid(pending, "pendente")

    def test_plano_nulo_com_tarefas_e_closure_sem_lifecycle_sao_invalidos(self):
        ledger = self.valid()
        ledger["plan"] = None
        self.assertInvalid(ledger, "sem plano")
        ledger = self.valid()
        ledger["closure"] = {"outcome": "cancelled", "evidence_ref": "x", "closed_at": NOW}
        self.assertInvalid(ledger, "closure")

    def test_goal_nao_carrega_card_board_thread_nem_frente(self):
        ledger = self.valid()
        ledger["scope"]["card_id"] = "T-144"
        self.assertInvalid(ledger, "goal avulso")

    def test_card_exige_escopo_completo_com_caminhos_absolutos(self):
        ledger = card_ledger()
        progress.validate_ledger(ledger)
        for field, value in (("board_path", "relativo/KANBAN.md"), ("thread_root", None), ("card_id", "T-14x"), ("front", "frente com espaço")):
            with self.subTest(field=field):
                broken = copy.deepcopy(ledger)
                broken["scope"][field] = value
                self.assertInvalid(broken, "scope")

    def test_booleano_nao_vale_como_inteiro_e_timestamp_inexistente_e_rejeitado(self):
        ledger = self.valid()
        ledger["revision"] = True
        self.assertInvalid(ledger, "revision")
        ledger = self.valid()
        ledger["created_at"] = "2026-13-45T25:61:61Z"
        self.assertInvalid(ledger, "created_at")

    def test_executor_so_aceita_identificadores_genericos(self):
        ledger = step(goal_ledger(), plan_op([task("P01")]), start("P01"))
        progress.validate_ledger(ledger)
        for label in ("João da Silva", "x" * 61, "a;b", "$(ls)"):
            with self.subTest(label=label):
                broken = copy.deepcopy(ledger)
                broken["tasks"][0]["executor"]["label"] = label
                self.assertInvalid(broken, "label")

    def test_schema_documental_concorda_com_o_validador(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(set(schema["required"]), set(progress.LEDGER_KEYS))
        self.assertEqual(set(schema["properties"]), set(progress.LEDGER_KEYS))
        self.assertEqual(schema["properties"]["schema_version"], {"const": progress.SCHEMA_VERSION})
        defs = schema["$defs"]
        self.assertEqual(set(defs["task"]["required"]), set(progress.TASK_KEYS))
        self.assertEqual(set(defs["scope"]["required"]), set(progress.SCOPE_KEYS))
        self.assertEqual(set(defs["executor"]["required"]), set(progress.EXECUTOR_KEYS))
        self.assertEqual(set(schema["properties"]["owner"]["required"]), set(progress.OWNER_KEYS))
        plan = next(item for item in schema["properties"]["plan"]["oneOf"] if item.get("type") == "object")
        self.assertEqual(set(plan["required"]), set(progress.PLAN_KEYS))
        closure = next(item for item in schema["properties"]["closure"]["oneOf"] if item.get("type") == "object")
        self.assertEqual(set(closure["required"]), set(progress.CLOSURE_KEYS))
        self.assertEqual(set(schema["properties"]["kind"]["enum"]), set(progress.KINDS))
        self.assertEqual(set(schema["properties"]["lifecycle"]["enum"]), set(progress.LIFECYCLES))
        self.assertEqual(
            set(schema["properties"]["activity"]["enum"]), set(progress.CARD_ACTIVITIES) | set(progress.GOAL_ACTIVITIES)
        )
        self.assertEqual(set(defs["host"]["enum"]), set(progress.HOSTS))
        self.assertEqual(set(defs["task"]["properties"]["size"]["enum"]), set(progress.SIZE_WEIGHTS))
        self.assertEqual(set(defs["task"]["properties"]["status"]["enum"]), set(progress.STATUSES))
        self.assertEqual(
            set(defs["task"]["properties"]["change_reason"]["enum"]) - {None}, set(progress.CHANGE_REASONS)
        )
        self.assertEqual(set(closure["properties"]["outcome"]["enum"]), set(progress.OUTCOMES))
        self.assertEqual(defs["task"]["properties"]["title"]["maxLength"], progress.MAX_TITLE_CHARS)
        self.assertEqual(schema["properties"]["tasks"]["maxItems"], progress.MAX_TASKS)
        self.assertEqual(defs["task"]["properties"]["evidence_refs"]["maxItems"], progress.MAX_EVIDENCE_REFS)
        self.assertEqual(defs["ref"]["maxLength"], progress.MAX_REF_CHARS)
        self.assertNotIn("jsonschema", Path(SCRIPT).read_text(encoding="utf-8"))


class ProgressFaseTest(unittest.TestCase):
    def phase(self, activity: str, marker, state: str = "ok") -> dict:
        ledger = card_ledger()
        ledger["activity"] = activity
        board = None if marker is None else {"state": state, "card": "T-144", "marker": marker}
        return progress.project_phase(ledger, board)

    def test_o_marcador_do_board_define_a_fase(self):
        expected = {" ": "backlog", ">": "planning", "!": "gate", "?": "validate", "x": "done"}
        for marker, key in expected.items():
            with self.subTest(marker=marker):
                result = self.phase(key, marker)
                self.assertEqual((result["key"], result["source"], result["warning"]), (key, "board", None))

    def test_marcador_til_distingue_ready_implementacao_revisao_e_docs_pela_atividade(self):
        for activity in ("ready", "implementation", "review", "docs"):
            with self.subTest(activity=activity):
                self.assertEqual(self.phase(activity, "~")["key"], activity)

    def test_ready_sob_til_vira_implementacao_quando_ha_passo_ativo_ou_concluido(self):
        board = {"state": "ok", "card": "T-144", "marker": "~"}
        sem_inicio = step(card_ledger(), plan_op([task("P01"), task("P02")]))
        self.assertEqual(sem_inicio["activity"], "ready")
        self.assertEqual(progress.project_phase(sem_inicio, board)["key"], "ready")
        dropped = step(sem_inicio, {"op": "drop", "task": "P02", "reason": "obsolete", "evidence_ref": "r"})
        self.assertEqual(progress.project_phase(dropped, board)["key"], "ready")  # descartar não é executar
        ativo = step(sem_inicio, start("P01"))
        concluido = step(ativo, done("P01"))
        for ledger in (ativo, concluido, step(concluido, start("P02"))):
            with self.subTest(status=[t["status"] for t in ledger["tasks"]]):
                result = progress.project_phase(ledger, board)
                self.assertEqual((result["key"], result["source"], result["warning"]), ("implementation", "board", None))
                self.assertEqual(ledger["activity"], "ready")  # a correção é da projeção: a atividade gravada não muda

    def test_review_docs_e_os_gates_do_board_nao_sao_alterados_pela_derivacao_de_ready(self):
        ledger = step(card_ledger(), plan_op([task("P01"), task("P02")]), start("P01"), done("P01"), start("P02"))
        for activity in ("review", "docs"):
            declared = {**ledger, "activity": activity}
            self.assertEqual(progress.project_phase(declared, {"state": "ok", "card": "T-144", "marker": "~"})["key"], activity)
        for marker, key in ((" ", "backlog"), (">", "planning"), ("!", "gate"), ("?", "validate"), ("x", "done")):
            with self.subTest(marker=marker):
                result = progress.project_phase(ledger, {"state": "ok", "card": "T-144", "marker": marker})
                self.assertEqual(result["key"], key)

    def test_atividade_incompativel_nao_vence_o_board(self):
        for activity in ("planning", "validate", "done"):
            result = self.phase(activity, "~")
            self.assertEqual(result["key"], "implementation")
            self.assertIn("vale o board", result["warning"])
        result = self.phase("implementation", "?")
        self.assertEqual(result["key"], "validate")
        self.assertIn("diverge do board", result["warning"])

    def test_gate_e_so_indicacao_consultiva_em_planejamento(self):
        self.assertEqual(self.phase("gate", ">")["key"], "gate")
        self.assertEqual(self.phase("gate", ">")["source"], "activity")
        self.assertEqual(self.phase("gate", "~")["key"], "implementation")  # com [~] o gate não vale mais

    def test_board_ilegivel_ausente_ou_ambiguo_deixa_a_fase_indisponivel_sem_esconder_o_percentual(self):
        ledger = step(card_ledger(), plan_op([task("P01"), task("P02")]), *finish("P01"))
        for board in (None, {"state": "erro", "code": "card-ausente"}, {"state": "erro", "code": "card-duplicado"}, {"state": "ok", "marker": "Z"}):
            with self.subTest(board=board):
                view = progress.build_view(ledger, board)
                self.assertIsNone(view["phase"]["key"])
                self.assertEqual(view["phase"]["source"], "indisponivel")
                text = progress.render_text(view)
                self.assertIn("fase indisponível", text)
                self.assertIn("1/2 passos concluídos · 50% do plano", text)
                self.assertIn("Aviso:", text)

    def test_validate_aparece_mesmo_com_100_por_cento_e_100_nao_e_done(self):
        ledger = step(card_ledger(), plan_op([task("P01"), task("P02")]), *finish("P01", "P02"), {"op": "phase", "value": "validate"})
        view = progress.build_view(ledger, {"state": "ok", "card": "T-144", "marker": "?"})
        text = progress.render_text(view)
        self.assertEqual(view["progress"]["percent"], 100)
        self.assertIn("T-144 · validação do dono · 2/2 passos concluídos · 100% do plano", text)
        self.assertIn("o card só fecha quando o dono validar", text)
        self.assertEqual(progress.render_segment(view), "◎ T-144 · validação do dono · 2/2 · 100%")
        done_view = progress.build_view(ledger, {"state": "ok", "card": "T-144", "marker": "x"})
        self.assertNotIn("o card só fecha", progress.render_text(done_view))

    def test_goal_usa_as_fases_de_goal_sem_board(self):
        for activity in progress.GOAL_ACTIVITIES:
            ledger = goal_ledger()
            ledger["activity"] = activity
            self.assertEqual(progress.project_phase(ledger, None)["key"], activity)
        self.assertTrue(progress.render_text(progress.build_view(goal_ledger(), None)).startswith("goal 11111111 · planejamento"))

    def test_render_segmento_e_texto_do_plano(self):
        ledger = step(card_ledger(), plan_op([task("P06", "M", "conferir retomada"), task("P07", "S", "documentar")]), start("P06"))
        ledger["activity"] = "review"
        view = progress.build_view(ledger, {"state": "ok", "card": "T-144", "marker": "~"})
        lines = progress.render_text(view).splitlines()
        self.assertEqual(lines[0], "T-144 · revisão · 0/2 passos concluídos · 0% do plano")
        self.assertEqual(lines[1], "Em execução: P06 — conferir retomada · implementer/normal")
        self.assertEqual(lines[2], "Próximos: P07 — documentar")
        self.assertEqual(progress.render_segment(view), "◎ T-144 · revisão · 0/2 · 0%")
        paused = copy.deepcopy(ledger)
        paused["lifecycle"] = "paused"
        self.assertTrue(progress.render_segment(progress.build_view(paused, None)).endswith("pausado"))

    def test_saida_nunca_carrega_controle_de_terminal_mesmo_com_ledger_adulterado(self):
        ledger = step(goal_ledger(), plan_op([task("P01")]))
        ledger["tasks"][0]["title"] = "\x1b[2Jlimpa tela"
        view = progress.build_view(ledger, None)
        self.assertNotIn("\x1b", progress.render_text(view))
        self.assertNotIn("\x1b", progress.render_segment(view))


class ProgressPersistenciaTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="orq-progress-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "frente"
        self.root.mkdir()
        result = progress.begin_ledger("goal", self.root, "claude", KEY_A, NOW)
        self.path = Path(result["ledger_path"])
        progress.mutate_ledger(self.path, KEY_A, None, plan_op([task("P01"), task("P02")]), NOW)

    def mutate(self, operation: dict, key: str = KEY_A, expected=None) -> dict:
        return progress.mutate_ledger(self.path, key, expected, operation, "2026-10-04T14:00:00Z")

    def test_revisao_esperada_divergente_gera_conflito_sem_gravar(self):
        before = self.path.read_bytes()
        with self.assertRaises(progress.ConflictError) as caught:
            self.mutate(start("P01"), expected=1)
        self.assertEqual(caught.exception.code, "revisao-divergente")
        self.assertEqual(caught.exception.revision, 2)
        self.assertEqual(self.path.read_bytes(), before)

    def test_revisao_esperada_igual_grava_e_ausente_tambem(self):
        self.assertEqual(self.mutate(start("P01"), expected=2)["revision"], 3)
        self.assertEqual(self.mutate(start("P02"))["revision"], 4)

    def test_repeticao_idempotente_nao_grava_nem_sobe_a_revisao(self):
        self.mutate(start("P01"))
        before = self.path.read_bytes()
        result = self.mutate(start("P01"))
        self.assertFalse(result["changed"])
        self.assertEqual(self.path.read_bytes(), before)

    def test_so_o_dono_muda_e_claim_transfere_a_escrita(self):
        with self.assertRaises(progress.ConflictError) as caught:
            self.mutate(start("P01"), key=KEY_B)
        self.assertEqual(caught.exception.code, "dono-divergente")
        self.mutate({"op": "claim", "host": "codex", "expected_owner": KEY_A}, key=KEY_B)
        self.mutate(start("P01"), key=KEY_B)
        with self.assertRaises(progress.ConflictError):  # o escritor antigo perdeu a autorização
            self.mutate(start("P02"), key=KEY_A)
        with self.assertRaises(progress.ConflictError):  # claim com dono esperado errado
            self.mutate({"op": "claim", "host": "claude", "expected_owner": KEY_A}, key="c" * 64)

    def test_chave_de_sessao_malformada_e_erro_de_entrada(self):
        with self.assertRaises(progress.InputError):
            self.mutate(start("P01"), key="curta")

    def test_ledger_inexistente_nao_deixa_lock_nem_diretorio_para_tras(self):
        ghost = self.path.parent.parent / "cards" / "T-1.json"
        antes = sorted(p.name for p in (ghost.parent.parent / "locks").iterdir())
        with self.assertRaises(progress.UnavailableError) as caught:
            progress.mutate_ledger(ghost, KEY_A, None, start("P01"), NOW)
        self.assertEqual(caught.exception.code, "ledger-ausente")
        self.assertEqual(sorted(p.name for p in (ghost.parent.parent / "locks").iterdir()), antes)  # nenhum lock novo
        outside = self.root / "nada" / "T-1.json"
        with self.assertRaises(progress.UnavailableError) as caught:
            progress.mutate_ledger(outside, KEY_A, None, start("P01"), NOW)
        self.assertEqual(caught.exception.code, "destino-fora-do-layout")
        self.assertFalse(outside.parent.exists())

    def test_falha_antes_do_replace_preserva_o_snapshot_anterior_e_nao_deixa_temporario(self):
        before = self.path.read_bytes()
        with mock.patch.object(progress.os, "replace", side_effect=OSError(errno.EIO, "disco falhou")):
            with self.assertRaises(progress.UnavailableError) as caught:
                self.mutate(start("P01"))
        self.assertEqual(caught.exception.code, "persistencia-falhou")
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(progress.read_ledger(self.path)["revision"], 2)
        self.assertEqual(sorted(p.name for p in self.path.parent.iterdir()), [self.path.name])
        self.assertEqual(self.mutate(start("P01"))["revision"], 3)  # e o próximo ciclo funciona

    def test_o_destino_so_muda_no_replace_e_o_temporario_ja_esta_completo_e_valido(self):
        before = self.path.read_bytes()
        real_replace = os.replace
        observed = {}

        def inspect_then_replace(source, destination):
            observed["destination_untouched"] = Path(destination).read_bytes() == before
            observed["same_directory"] = Path(source).parent == Path(destination).parent
            observed["temporary_valid"] = progress.validate_ledger(json.loads(Path(source).read_bytes()))["revision"] == 3
            real_replace(source, destination)

        with mock.patch.object(progress.os, "replace", side_effect=inspect_then_replace):
            self.mutate(start("P01"))
        self.assertEqual(observed, {"destination_untouched": True, "same_directory": True, "temporary_valid": True})
        self.assertEqual(progress.read_ledger(self.path)["revision"], 3)

    def git_root(self) -> Path:
        return Path(os.path.realpath(self.root))

    def test_temporario_reservado_e_consultado_no_git_com_o_nome_exato_antes_de_receber_o_json(self):
        before = self.path.read_bytes()
        ledger = progress.read_ledger(self.path)
        consultas = []

        def git_falso(root, *args, stdin=None):
            consultas.append((args, stdin))
            nomes = [n for n in self.path.parent.iterdir() if n.name.endswith(progress.TEMPORARY_SUFFIX)]
            consultas.append(("reservado", [(n.name, n.stat().st_size) for n in nomes]))
            nomes_ignorados = stdin  # eco: tudo o que foi perguntado está ignorado
            return subprocess.CompletedProcess(args, 0, stdout=nomes_ignorados, stderr=b"")

        with mock.patch.object(progress, "_git", side_effect=git_falso):
            progress.write_ledger(self.path, {**ledger, "revision": 3}, git_root=self.git_root())
        (args, stdin), (_, reservados) = consultas
        self.assertEqual(args, ("check-ignore", "--no-index", "-z", "--stdin"))
        (nome_reservado, tamanho), = reservados
        self.assertEqual(tamanho, 0)  # o JSON ainda não foi escrito quando o Git é consultado
        perguntado = stdin.decode().rstrip("\0")
        self.assertEqual(perguntado, (self.path.parent / nome_reservado).relative_to(self.git_root()).as_posix())
        self.assertTrue(nome_reservado.startswith(progress.temporary_prefix(self.path.name)))
        self.assertNotIn(progress.TEMPORARY_PROBE_TOKEN, nome_reservado)  # nome real, não a sonda fictícia
        self.assertNotEqual(self.path.read_bytes(), before)
        self.assertEqual(sorted(p.name for p in self.path.parent.iterdir()), [self.path.name])

    def test_temporario_nao_ignorado_ou_consulta_falha_remove_o_temporario_e_preserva_o_ledger(self):
        before = self.path.read_bytes()
        ledger = progress.read_ledger(self.path)
        casos = {
            "nao ignorado": (subprocess.CompletedProcess([], 1, stdout=b"", stderr=b""), "armazenamento-nao-ignorado"),
            "git falhou": (subprocess.CompletedProcess([], 128, stdout=b"", stderr=b"fatal"), "git-indisponivel"),
            "git sumiu": (None, "git-indisponivel"),
        }
        for nome, (resposta, codigo) in casos.items():
            with self.subTest(nome), mock.patch.object(progress, "_git", return_value=resposta):
                with self.assertRaises(progress.UnavailableError) as caught:
                    progress.write_ledger(self.path, {**ledger, "revision": 9}, git_root=self.git_root())
                self.assertEqual(caught.exception.code, codigo)
                self.assertEqual(self.path.read_bytes(), before)
                self.assertEqual(sorted(p.name for p in self.path.parent.iterdir()), [self.path.name])

    def test_interrupcao_durante_a_gravacao_tambem_remove_o_temporario(self):
        before = self.path.read_bytes()
        with mock.patch.object(progress.os, "fsync", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.mutate(start("P01"))
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(sorted(p.name for p in self.path.parent.iterdir()), [self.path.name])

    def test_falha_no_fsync_tambem_preserva_o_snapshot(self):
        before = self.path.read_bytes()
        with mock.patch.object(progress.os, "fsync", side_effect=OSError(errno.EIO, "sem fsync")):
            with self.assertRaises(progress.UnavailableError):
                self.mutate(start("P01"))
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(sorted(p.name for p in self.path.parent.iterdir()), [self.path.name])

    def test_ledger_que_passaria_de_1_mib_e_recusado_em_vez_de_gravar_arquivo_ilegivel(self):
        before = self.path.read_bytes()
        with mock.patch.object(progress, "MAX_LEDGER_BYTES", len(before) + 5):
            with self.assertRaises(progress.InputError) as caught:
                self.mutate(start("P01"))
        self.assertEqual(caught.exception.code, "ledger-grande")
        self.assertEqual(self.path.read_bytes(), before)

    def test_leitor_concorrente_ve_sempre_o_snapshot_anterior_ou_o_novo_nunca_json_parcial(self):
        writes = 40
        failures: list = []
        finished = threading.Event()

        def writer():
            try:
                for index in range(writes):
                    operation = {
                        "op": "add",
                        "input": {"reason": "scope_change", "evidence_ref": f"t#{index}", "tasks": [task(f"X{index:03d}", "S")]},
                    }
                    progress.mutate_ledger(self.path, KEY_A, None, operation, NOW)
            except BaseException as error:  # noqa: BLE001 - o teste precisa ver qualquer falha
                failures.append(error)
            finally:
                finished.set()

        thread = threading.Thread(target=writer)
        thread.start()
        seen, reads = 2, 0
        while not finished.is_set() or reads < 5:
            ledger = progress.read_ledger(self.path)  # nunca levanta: JSON parcial seria erro de validação
            json.loads(self.path.read_bytes())
            self.assertGreaterEqual(ledger["revision"], seen)
            seen = ledger["revision"]
            reads += 1
        thread.join()
        self.assertEqual(failures, [])
        self.assertEqual(progress.read_ledger(self.path)["revision"], 2 + writes)
        self.assertEqual(len(progress.read_ledger(self.path)["tasks"]), 2 + writes)

    def test_lock_ocupado_vira_indisponibilidade_com_espera_limitada(self):
        with progress.ledger_lock(self.path):
            started = time.monotonic()
            with self.assertRaises(progress.UnavailableError) as caught:
                with progress.ledger_lock(self.path, wait_seconds=0.15):
                    self.expect_error("o lock não podia ser adquirido duas vezes")
            self.assertLess(time.monotonic() - started, 3)
        self.assertEqual(caught.exception.code, "lock-ocupado")
        with progress.ledger_lock(self.path, wait_seconds=0.15):  # solto, volta a adquirir
            pass

    def test_sem_backend_de_lock_a_mutacao_falha_visivelmente(self):
        with mock.patch.object(progress, "fcntl", None), mock.patch.object(progress, "msvcrt", None):
            with self.assertRaises(progress.UnavailableError) as caught:
                self.mutate(start("P01"))
        self.assertEqual(caught.exception.code, "lock-indisponivel")

    def test_backend_msvcrt_e_exercitado_quando_fcntl_nao_existe(self):
        calls = []
        fake = mock.Mock(LK_NBLCK=1, LK_UNLCK=0)
        fake.locking.side_effect = lambda fd, mode, size: calls.append(mode)
        with mock.patch.object(progress, "fcntl", None), mock.patch.object(progress, "msvcrt", fake):
            self.assertEqual(self.mutate(start("P01"))["revision"], 3)
        self.assertEqual(calls, [1, 0])  # trava e destrava uma vez

    def test_ledger_corrompido_ilegivel_grande_ou_de_versao_nova_nao_vira_zero_por_cento(self):
        newer = json.loads(self.path.read_text(encoding="utf-8"))
        newer["schema_version"] = 99
        duplicated = self.path.read_text(encoding="utf-8").replace('"revision": 2', '"revision": 2, "revision": 3')
        cases = [
            ("ledger-invalido", b"{ nao e json"),
            ("ledger-invalido", duplicated.encode("utf-8")),
            ("ledger-grande", b" " * (progress.MAX_LEDGER_BYTES + 1)),
            ("versao-desconhecida", json.dumps(newer).encode("utf-8")),
        ]
        for code, payload in cases:
            with self.subTest(code=code, size=len(payload)):
                self.path.write_bytes(payload)
                with self.assertRaises(progress.UnavailableError) as caught:
                    progress.read_ledger(self.path)
                self.assertEqual(caught.exception.code, code)
                with self.assertRaises(progress.UnavailableError):
                    self.mutate(start("P01"))
        self.path.write_bytes(b'{"schema_version": 1, "n": NaN}')
        with self.assertRaises(progress.UnavailableError):
            progress.read_ledger(self.path)

    def test_leitura_nao_cria_diretorio_lock_nem_arquivo(self):
        locks = self.path.parent.parent / "locks"
        for item in locks.iterdir():
            item.unlink()
        locks.rmdir()
        before = tree_snapshot(self.root)
        progress.read_ledger(self.path)
        progress.build_view(progress.read_ledger(self.path), None)
        self.assertEqual(tree_snapshot(self.root), before)
        self.assertFalse(locks.exists())


def tree_snapshot(root: Path) -> dict:
    """Nome, tamanho, mtime e hash de tudo sob a raiz, diretórios incluídos."""
    result = {}
    for current, directories, files in os.walk(root):
        for name in directories + files:
            path = Path(current) / name
            info = path.lstat()
            digest = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
            result[str(path.relative_to(root))] = (info.st_size, info.st_mtime_ns, digest)
    return result


class CliTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="orq-progress-cli-")
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.sandbox_home = self.base / "home"
        self.sandbox_home.mkdir()
        self.sandbox_tmp = self.base / "systmp"
        self.sandbox_tmp.mkdir()

    def env(self, **extra) -> dict:
        environment = dict(os.environ)
        environment.update({"HOME": str(self.sandbox_home), "TMPDIR": str(self.sandbox_tmp), "PYTHONDONTWRITEBYTECODE": "1"})
        environment.update(extra)
        return environment

    def cli(self, *args: str, stdin=None, env=None, cwd=None) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            input=stdin,
            capture_output=True,
            text=True,
            timeout=60,
            env=env or self.env(),
            cwd=cwd or self.base,
            check=False,
        )

    def ok(self, *args: str, stdin=None, env=None) -> dict:
        result = self.cli(*args, stdin=stdin, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def expect_error(self, expected_exit: int, *args: str, stdin=None, env=None) -> dict:
        result = self.cli(*args, stdin=stdin, env=env)
        self.assertEqual(result.returncode, expected_exit, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "")
        payload = json.loads(result.stderr.strip().splitlines()[-1])
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["exit"], expected_exit)
        return payload

    def make_front(self, name: str = "frente", board: str = "- [~] `T-144` Medidor — nota\n") -> Path:
        root = self.base / name
        (root / "memory" / "wiki").mkdir(parents=True)
        if board is not None:
            (root / "memory" / "wiki" / "KANBAN.md").write_text(board, encoding="utf-8")
        return root

    def begin_card(self, root: Path, card: str = "T-144", host: str = "claude", key=None, board=None) -> dict:
        board = board or root / "memory" / "wiki" / "KANBAN.md"
        args = [
            "begin", "--kind", "card", "--root", str(root), "--board", str(board),
            "--thread-root", str(root / "memory" / "wiki"), "--card", card, "--front", "frente-mods", "--host", host,
        ]
        if key:
            args += ["--session-key", key]
        return self.ok(*args)

    def begin_goal(self, root: Path, host: str = "claude", key=None) -> dict:
        args = ["begin", "--kind", "goal", "--root", str(root), "--host", host]
        if key:
            args += ["--session-key", key]
        return self.ok(*args)

    def target(self, begun: dict) -> list:
        return ["--ledger", begun["ledger_path"]]

    def mutate(self, command: str, begun: dict, *args: str, stdin=None, key=None, expect=None) -> dict:
        extra = ["--session-key", key or begun["session_key"]]
        if expect is not None:
            extra += ["--expect-revision", str(expect)]
        return self.ok(command, *self.target(begun), *extra, *args, stdin=stdin)

    def plan(self, begun: dict, tasks: list) -> dict:
        data = {"source_ref": "docs/plano.md#passos", "approval_ref": "threads/T-144.md#aprovacao", "tasks": tasks}
        return self.mutate("plan", begun, "--input", "-", stdin=json.dumps(data))

    def show_json(self, begun: dict) -> dict:
        return self.ok("show", *self.target(begun), "--format", "json")

    def hold_lock(self, ledger: Path, seconds: float) -> subprocess.Popen:
        """Outro processo segura o lock do ledger por `seconds`; devolve quando o lock já está preso."""
        holder = subprocess.Popen(
            [sys.executable, "-c",
             "import sys,time\nimport importlib.util\n"
             "s=importlib.util.spec_from_file_location('p',sys.argv[1]);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)\n"
             "from pathlib import Path\nwith m.ledger_lock(Path(sys.argv[2])):\n print('preso',flush=True)\n time.sleep(float(sys.argv[3]))\n",
             str(SCRIPT), str(ledger), str(seconds)],
            stdout=subprocess.PIPE, text=True, env=self.env(),
        )
        self.addCleanup(holder.kill)
        self.assertEqual(holder.stdout.readline().strip(), "preso")
        return holder

    def start_task(self, begun: dict, task_id: str, **kwargs) -> dict:
        return self.mutate(
            "start", begun, "--task", task_id, "--executor-host", "codex", "--executor-role", "implementer",
            "--executor-label", "normal", **kwargs,
        )

    def done_task(self, begun: dict, task_id: str, ref: str = "suite-ok", **kwargs) -> dict:
        return self.mutate("done", begun, "--task", task_id, "--evidence-ref", ref, **kwargs)


class ProgressCliFluxoTest(CliTestCase):
    def test_fluxo_de_card_do_begin_ao_close_com_saidas_e_projecoes(self):
        root = self.make_front()
        begun = self.begin_card(root)
        self.assertTrue(begun["changed"])
        self.assertEqual(begun["revision"], 1)
        self.assertRegex(begun["session_key"], r"^[0-9a-f]{64}$")
        self.assertEqual(set(begun), {"ok", "run_id", "ledger_path", "revision", "session_key", "changed"})
        self.assertEqual(begun["ledger_path"], os.path.realpath(root / ".orq/progress/v1/cards/T-144.json"))  # canônico

        planned = self.plan(begun, [task("P01", "L", "Núcleo"), task("P02", "S", "Docs")])
        self.assertEqual(planned["revision"], 2)
        self.assertEqual(self.start_task(begun, "P01")["revision"], 3)
        self.mutate("phase", begun, "--value", "implementation")
        text = self.cli("show", *self.target(begun)).stdout
        self.assertIn("T-144 · implementação · 0/2 passos concluídos · 0% do plano", text)
        self.assertIn("Em execução: P01 — Núcleo · implementer/normal", text)
        self.done_task(begun, "P01")
        self.assertEqual(self.cli("show", *self.target(begun), "--format", "segment").stdout.strip(), "◎ T-144 · implementação · 1/2 · 75%")

        (root / "memory/wiki/KANBAN.md").write_text("- [?] `T-144` Medidor — n\n", encoding="utf-8")
        self.mutate("phase", begun, "--value", "validate")
        self.start_task(begun, "P02")
        self.done_task(begun, "P02", "suite-ok-2")
        view = self.show_json(begun)
        self.assertEqual(view["phase"]["key"], "validate")
        self.assertEqual(view["progress"]["percent"], 100)
        self.mutate("pause", begun)
        self.assertIn("pausado", self.cli("show", *self.target(begun)).stdout)
        self.mutate("resume", begun)

        close = ["--outcome", "reported_complete", "--evidence-ref", "threads/T-144.md#validado"]
        self.expect_error(2, "close", *self.target(begun), "--session-key", begun["session_key"], *close)  # board ainda [?]
        (root / "memory/wiki/KANBAN.md").write_text("- [x] `T-144` Medidor — n\n", encoding="utf-8")
        closed = self.mutate("close", begun, *close)
        self.assertTrue(closed["changed"])
        self.assertIn("execução encerrada pelo Manager", self.cli("show", *self.target(begun)).stdout)

    def test_enderecamento_por_root_card_e_root_run_equivale_a_ledger(self):
        root = self.make_front()
        begun = self.begin_card(root)
        by_card = self.ok("show", "--root", str(root), "--card", "T-144", "--format", "json")
        self.assertEqual(by_card, self.show_json(begun))
        goal = self.begin_goal(root)
        by_run = self.ok("show", "--root", str(root), "--run", goal["run_id"], "--format", "json")
        self.assertEqual(by_run["kind"], "goal")
        mutated = self.ok(
            "plan", "--root", str(root), "--run", goal["run_id"], "--session-key", goal["session_key"], "--input", "-",
            stdin=json.dumps({"tasks": [task("P01")]}),
        )
        self.assertEqual(mutated["revision"], 2)
        for bad in (["--root", str(root)], ["--root", str(root), "--card", "T-1", "--run", goal["run_id"]], ["--ledger", begun["ledger_path"], "--root", str(root)]):
            with self.subTest(bad=bad):
                self.expect_error(2, "show", *bad)
        self.expect_error(2, "show", "--root", str(root), "--run", "NAO-E-UUID")
        self.expect_error(2, "show", "--root", str(root), "--card", "../T-144")
        self.expect_error(2, "show", "--ledger", "relativo.json")

    def test_ready_com_passo_em_execucao_nao_mostra_pronto_para_iniciar(self):
        begun = self.begin_card(self.make_front())
        self.plan(begun, [task("P01"), task("P02"), task("P03")])
        self.assertIn("pronto para iniciar", self.cli("show", *self.target(begun)).stdout)  # nada iniciado
        self.start_task(begun, "P01")
        self.done_task(begun, "P01")
        self.start_task(begun, "P02")
        text = self.cli("show", *self.target(begun)).stdout
        self.assertIn("T-144 · implementação · 1/3 passos concluídos · 33% do plano", text)
        self.assertIn("Em execução: P02", text)
        self.assertNotIn("pronto para iniciar", text)
        self.assertEqual(
            self.cli("show", *self.target(begun), "--format", "segment").stdout.strip(), "◎ T-144 · implementação · 1/3 · 33%"
        )

    def test_expect_revision_e_opcional_e_session_key_e_obrigatoria(self):
        begun = self.begin_goal(self.make_front())
        self.plan(begun, [task("P01"), task("P02")])
        self.assertEqual(self.start_task(begun, "P01")["revision"], 3)  # sem --expect-revision
        self.assertEqual(self.start_task(begun, "P02", expect=3)["revision"], 4)  # presente e igual
        payload = self.expect_error(
            3, "done", *self.target(begun), "--session-key", begun["session_key"], "--expect-revision", "3",
            "--task", "P01", "--evidence-ref", "x",
        )
        self.assertEqual((payload["code"], payload["revision"]), ("revisao-divergente", 4))
        result = self.cli("pause", *self.target(begun))  # sem --session-key
        self.assertEqual(result.returncode, 2)
        self.assertEqual(self.show_json(begun)["revision"], 4)
        self.expect_error(2, "pause", *self.target(begun), "--session-key", "curta")
        self.assertEqual(
            self.cli("pause", *self.target(begun), "--session-key", begun["session_key"], "--expect-revision", "zero").returncode, 2
        )

    def test_erro_de_uso_sai_2_com_exatamente_uma_linha_json_no_stderr_e_stdout_vazio(self):
        begun = self.begin_goal(self.make_front())
        casos = {
            "falta --session-key": ["pause", *self.target(begun)],
            "host invalido": ["begin", "--kind", "goal", "--root", str(self.base), "--host", "gemini"],
            "inteiro invalido": ["pause", *self.target(begun), "--session-key", KEY_A, "--expect-revision", "zero"],
            "subcomando desconhecido": ["nao-existe"],
            "sem subcomando": [],
            "opcao desconhecida": ["show", *self.target(begun), "--cor", "azul"],
        }
        for nome, argumentos in casos.items():
            with self.subTest(nome):
                resultado = self.cli(*argumentos)
                self.assertEqual(resultado.returncode, 2)
                self.assertEqual(resultado.stdout, "")
                linhas = resultado.stderr.splitlines()
                self.assertEqual(len(linhas), 1, resultado.stderr)
                payload = json.loads(linhas[0])
                self.assertEqual((payload["ok"], payload["exit"], payload["code"]), (False, 2, "uso-invalido"))
                self.assertTrue(payload["message"])
                self.assertEqual(set(payload), {"ok", "exit", "code", "message"})
        ajuda = self.cli("--help")
        self.assertEqual(ajuda.returncode, 0)
        self.assertTrue(ajuda.stdout.startswith("usage:"))
        self.assertEqual(ajuda.stderr, "")

    def test_codigos_de_saida_2_3_e_4(self):
        root = self.make_front()
        begun = self.begin_goal(root)
        self.assertEqual(self.expect_error(2, "start", *self.target(begun), "--session-key", begun["session_key"], "--task", "P01",
                                   "--executor-host", "codex", "--executor-role", "r", "--executor-label", "l")["code"], "tarefa-inexistente")
        self.assertEqual(self.expect_error(3, "pause", *self.target(begun), "--session-key", KEY_B)["code"], "dono-divergente")
        ghost = root / ".orq/progress/v1/goals/00000000-0000-4000-8000-000000000000.json"
        self.assertEqual(self.expect_error(4, "pause", "--ledger", str(ghost), "--session-key", KEY_B)["code"], "ledger-ausente")
        self.assertEqual(self.cli("nao-existe").returncode, 2)
        self.assertEqual(self.cli().returncode, 2)

    def test_begin_repetido_e_idempotente_e_outro_dono_e_conflito(self):
        root = self.make_front()
        first = self.begin_card(root)
        again = self.begin_card(root, key=first["session_key"])
        self.assertFalse(again["changed"])
        self.assertEqual(again["run_id"], first["run_id"])
        self.assertEqual(self.cli(
            "begin", "--kind", "card", "--root", str(root), "--board", str(root / "memory/wiki/KANBAN.md"),
            "--thread-root", str(root / "memory/wiki"), "--card", "T-144", "--front", "frente-mods", "--host", "codex",
        ).returncode, 3)  # sem chave: não dá para provar que é o dono
        self.expect_error(3, "begin", "--kind", "card", "--root", str(root), "--board", str(root / "memory/wiki/KANBAN.md"),
                  "--thread-root", str(root / "memory/wiki"), "--card", "T-144", "--front", "frente-mods", "--host", "codex",
                  "--session-key", KEY_B)
        self.expect_error(2, "begin", "--kind", "card", "--root", str(root), "--board", str(root / "memory/wiki/KANBAN.md"),
                  "--thread-root", str(root / "memory/wiki"), "--card", "T-144", "--front", "outra-frente", "--host", "claude",
                  "--session-key", first["session_key"])  # escopo divergente
        for _ in range(2):
            self.assertNotEqual(self.begin_goal(root)["run_id"], first["run_id"])  # goal: um UUID por execução
        self.assertEqual(len(self.ok("show", "--root", str(root), "--all", "--format", "json")["ledgers"]), 3)

    def test_begin_valida_argumentos_por_tipo(self):
        root = self.make_front()
        self.expect_error(2, "begin", "--kind", "goal", "--root", str(root), "--host", "claude", "--card", "T-144")
        self.expect_error(2, "begin", "--kind", "card", "--root", str(root), "--host", "claude")
        self.expect_error(2, "begin", "--kind", "goal", "--root", "relativo", "--host", "claude")
        self.expect_error(2, "begin", "--kind", "goal", "--root", str(root / "inexistente"), "--host", "claude")
        self.expect_error(2, "begin", "--kind", "goal", "--root", str(root), "--host", "claude", "--session-key", "curta")
        self.assertEqual(self.cli("begin", "--kind", "goal", "--root", str(root), "--host", "gemini").returncode, 2)

    def test_claim_pela_cli_transfere_a_escrita(self):
        begun = self.begin_goal(self.make_front())
        self.plan(begun, [task("P01")])
        claimed = self.ok(
            "claim", *self.target(begun), "--host", "codex", "--session-key", KEY_B, "--expected-owner", begun["session_key"]
        )
        self.assertEqual(claimed["session_key"], KEY_B)
        self.expect_error(3, "pause", *self.target(begun), "--session-key", begun["session_key"])  # o antigo perdeu
        self.ok("pause", *self.target(begun), "--session-key", KEY_B)
        self.assertEqual(self.show_json(begun)["owner"], {"host": "codex", "session_key": KEY_B})
        self.expect_error(3, "claim", *self.target(begun), "--host", "claude", "--session-key", "c" * 64, "--expected-owner", begun["session_key"])

    def test_ajuda_do_claim_diz_que_session_key_e_a_nova_chave_e_a_anterior_vai_em_expected_owner(self):
        texto = " ".join(self.cli("claim", "--help").stdout.split())
        self.assertIn("NOVA chave do novo dono", texto)
        self.assertIn("a chave anterior do dono atual vai em --expected-owner", texto)
        self.assertIn("diferente de --session-key", texto)
        outras = " ".join(self.cli("pause", "--help").stdout.split())
        self.assertIn("chave de sessão do dono", outras)  # nas demais mutações continua sendo a chave do dono atual

    def test_claim_com_session_key_igual_ao_expected_owner_e_exit_2_e_nao_transfere_nada(self):
        begun = self.begin_goal(self.make_front())
        self.plan(begun, [task("P01")])
        before = Path(begun["ledger_path"]).read_bytes()
        payload = self.expect_error(
            2, "claim", *self.target(begun), "--host", "codex", "--session-key", begun["session_key"],
            "--expected-owner", begun["session_key"],
        )
        self.assertEqual(payload["code"], "claim-sem-transferencia")
        self.assertIn("NOVA", payload["message"])
        self.assertEqual(Path(begun["ledger_path"]).read_bytes(), before)
        # a prioridade é do erro de uso: nem uma revisão divergente o esconde
        masked = self.expect_error(
            2, "claim", *self.target(begun), "--host", "codex", "--session-key", begun["session_key"],
            "--expected-owner", begun["session_key"], "--expect-revision", "99",
        )
        self.assertEqual(masked["code"], "claim-sem-transferencia")
        self.assertEqual(self.show_json(begun)["owner"]["session_key"], begun["session_key"])
        self.ok("pause", *self.target(begun), "--session-key", begun["session_key"])  # o dono segue sendo o mesmo

    def test_claim_puro_com_nova_chave_igual_a_esperada_e_erro_de_entrada(self):
        claim = {"op": "claim", "host": "codex", "expected_owner": KEY_A, "new_session_key": KEY_A}
        with self.assertRaises(progress.InputError) as caught:
            progress.apply_operation(goal_ledger(), claim, NOW)
        self.assertEqual(caught.exception.code, "claim-sem-transferencia")

    def test_entrada_do_plano_invalida_ou_acima_de_1_mib_e_exit_2(self):
        begun = self.begin_goal(self.make_front())
        self.expect_error(2, "plan", *self.target(begun), "--session-key", begun["session_key"], "--input", "-", stdin="{ nao e json")
        self.expect_error(2, "plan", *self.target(begun), "--session-key", begun["session_key"], "--input", "-", stdin='{"tasks": [], "prompt": "x"}')
        self.expect_error(2, "plan", *self.target(begun), "--session-key", begun["session_key"], "--input", "-", stdin='{"tasks": [{"id": "P01", "title": "t", "size": "M"}], "tasks": []}')
        self.expect_error(2, "plan", *self.target(begun), "--session-key", begun["session_key"], "--input", "-", stdin=" " * (progress.MAX_INPUT_BYTES + 1))
        self.expect_error(2, "plan", *self.target(begun), "--session-key", begun["session_key"], "--input", "arquivo.json")
        self.assertEqual(self.show_json(begun)["revision"], 1)

    def test_mesma_sequencia_em_claude_e_codex_produz_projecoes_equivalentes(self):
        views = []
        for host in ("claude", "codex"):
            root = self.make_front(f"frente-{host}")
            begun = self.begin_card(root, host=host)
            self.plan(begun, [task("P01", "L"), task("P02", "S")])
            self.start_task(begun, "P01")
            self.done_task(begun, "P01")
            self.mutate("phase", begun, "--value", "review")
            view = self.show_json(begun)
            for volatile in ("ledger_path", "run_id", "owner", "updated_at"):
                view.pop(volatile)
            for item in view["tasks"]:
                item.pop("executor")
            views.append(view)
        self.assertEqual(views[0], views[1])
        self.assertEqual(views[0]["progress"]["percent"], 75)

    def test_cards_hosts_e_sessoes_nao_se_contaminam(self):
        root = self.make_front(board="- [~] `T-1` Um — n\n- [~] `T-2` Dois — n\n")
        one = self.begin_card(root, "T-1", host="claude")
        two = self.begin_card(root, "T-2", host="codex")
        goal = self.begin_goal(root, host="codex")
        other_root = self.make_front("outra-frente", "- [~] `T-1` Um — n\n")
        elsewhere = self.begin_card(other_root, "T-1", host="codex")
        for begun in (one, two, goal, elsewhere):
            self.plan(begun, [task("P01"), task("P02")])
        before = {name: Path(item["ledger_path"]).read_bytes() for name, item in (("two", two), ("goal", goal), ("else", elsewhere))}
        self.expect_error(3, "start", *self.target(one), "--session-key", two["session_key"], "--task", "P01",
                  "--executor-host", "codex", "--executor-role", "r", "--executor-label", "l")
        self.start_task(one, "P01")
        self.done_task(one, "P01")
        after = {name: Path(item["ledger_path"]).read_bytes() for name, item in (("two", two), ("goal", goal), ("else", elsewhere))}
        self.assertEqual(before, after)
        self.assertEqual(self.show_json(one)["progress"]["percent"], 50)
        self.assertEqual(self.show_json(two)["progress"]["percent"], 0)
        self.assertEqual(self.show_json(two)["owner"]["host"], "codex")

    def test_show_all_lista_cards_e_goals_e_sinaliza_ledger_ilegivel(self):
        root = self.make_front(board="- [~] `T-1` Um — n\n- [?] `T-2` Dois — n\n")
        self.begin_card(root, "T-1")
        self.begin_card(root, "T-2")
        self.begin_goal(root)
        text = self.cli("show", "--root", str(root), "--all")
        self.assertEqual(text.returncode, 0)
        self.assertEqual(text.stdout.count("sem plano registrado"), 3)
        self.assertEqual(self.cli("show", "--root", str(root), "--all", "--format", "segment").returncode, 2)
        empty = self.cli("show", "--root", str(self.make_front("vazia")), "--all")
        self.assertEqual((empty.returncode, empty.stdout.strip()), (0, "Nenhum medidor de progresso nesta raiz."))
        (root / ".orq/progress/v1/cards/T-2.json").write_text("{ quebrado", encoding="utf-8")
        broken = self.cli("show", "--root", str(root), "--all", "--format", "json")
        self.assertEqual(broken.returncode, 4)
        payload = json.loads(broken.stdout)
        self.assertEqual((len(payload["ledgers"]), len(payload["errors"])), (2, 1))
        self.assertEqual(payload["errors"][0]["code"], "ledger-invalido")


class ProgressCliConcorrenciaTest(CliTestCase):
    def collect(self, proc: subprocess.Popen) -> tuple:
        out, err = proc.communicate(timeout=60)
        return proc.returncode, out, err

    def spawn(self, *args: str) -> subprocess.Popen:
        return subprocess.Popen(
            [sys.executable, str(SCRIPT), *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=self.env()
        )

    def test_dois_processos_com_a_mesma_revisao_um_vence_e_o_outro_recebe_conflito(self):
        begun = self.begin_goal(self.make_front())
        self.plan(begun, [task("P01"), task("P02")])
        base = ["--ledger", begun["ledger_path"], "--session-key", begun["session_key"], "--expect-revision", "2"]
        procs = [
            self.spawn("start", *base, "--task", task_id, "--executor-host", "codex", "--executor-role", "impl", "--executor-label", "n")
            for task_id in ("P01", "P02")
        ]
        outcomes = [self.collect(proc) for proc in procs]
        self.assertEqual(sorted(code for code, _, _ in outcomes), [0, 3])
        loser = next(err for code, _, err in outcomes if code == 3)
        self.assertEqual(json.loads(loser)["code"], "revisao-divergente")
        view = self.show_json(begun)
        self.assertEqual(view["revision"], 3)  # exatamente uma atualização aplicada, nenhuma perdida em silêncio
        self.assertEqual(len(view["active"]), 1)

    def test_oito_processos_sem_expect_revision_nao_perdem_atualizacao(self):
        begun = self.begin_goal(self.make_front())
        self.plan(begun, [task("P01")])
        procs = []
        for index in range(8):
            data = {"reason": "scope_change", "evidence_ref": f"t#{index}", "tasks": [task(f"X{index}", "S")]}
            entrada = self.base / f"entrada-{index}.json"
            entrada.write_text(json.dumps(data), encoding="utf-8")
            with open(entrada, encoding="utf-8") as handle:
                procs.append(
                    subprocess.Popen(
                        [sys.executable, str(SCRIPT), "add", "--ledger", begun["ledger_path"], "--session-key", begun["session_key"], "--input", "-"],
                        stdin=handle, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=self.env(),
                    )
                )
        for proc in procs:
            code, _, err = self.collect(proc)
            self.assertEqual(code, 0, err)
        view = self.show_json(begun)
        self.assertEqual(view["revision"], 2 + 8)
        self.assertEqual(sorted(item["id"] for item in view["tasks"]), sorted(["P01"] + [f"X{i}" for i in range(8)]))
        self.assertEqual(sorted(p.name for p in Path(begun["ledger_path"]).parent.iterdir()), [Path(begun["ledger_path"]).name])

    def test_mutacao_espera_o_lock_ser_solto_em_vez_de_falhar_na_hora(self):
        begun = self.begin_goal(self.make_front())
        path = Path(begun["ledger_path"])
        holder = self.hold_lock(path, 1.0)
        started = time.monotonic()
        self.assertEqual(self.cli("pause", "--ledger", str(path), "--session-key", begun["session_key"]).returncode, 0)
        self.assertGreater(time.monotonic() - started, 0.3)  # esperou o lock em vez de falhar na hora
        holder.communicate(timeout=10)
        self.assertEqual(self.show_json(begun)["lifecycle"], "paused")

    def test_ledger_por_alias_de_diretorio_espera_o_mesmo_lock_do_caminho_real(self):
        root = self.make_front()
        begun = self.begin_goal(root)
        real = Path(begun["ledger_path"])
        atalho = self.base / "atalho"
        os.symlink(real.parent, atalho)  # o apelido aponta para o diretório goals
        holder = self.hold_lock(real, 1.5)
        started = time.monotonic()
        result = self.cli("pause", "--ledger", str(atalho / real.name), "--session-key", begun["session_key"])
        waited = time.monotonic() - started
        holder.communicate(timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertGreater(waited, 0.7)  # lock lateral próprio do apelido não esperaria nada
        self.assertEqual(sorted(p.name for p in real.parent.iterdir()), [real.name])  # e nenhum lock lateral nasceu

    def test_alias_e_caminho_real_disputando_a_mesma_revisao_nunca_vencem_os_dois(self):
        root = self.make_front()
        begun = self.begin_goal(root)
        real = Path(begun["ledger_path"])
        atalho = self.base / "atalho"
        os.symlink(real.parent, atalho)
        holder = self.hold_lock(real, 1.0)
        base = ["--session-key", begun["session_key"], "--expect-revision", "1"]
        procs = [
            self.spawn("pause", "--ledger", str(real), *base),
            self.spawn("phase", "--ledger", str(atalho / real.name), *base, "--value", "execution"),
        ]
        outcomes = [self.collect(proc) for proc in procs]
        holder.communicate(timeout=10)
        self.assertEqual(sorted(code for code, _, _ in outcomes), [0, 3])
        self.assertEqual(self.show_json(begun)["revision"], 2)  # exatamente uma atualização aplicada


class ProgressCliPathsTest(CliTestCase):
    def test_caminhos_com_espaco_unicode_e_metacaracteres_de_shell_nao_viram_codigo(self):
        hostile = 'proj; touch PWNED-1 $(touch PWNED-2) `touch PWNED-3` "aspas" \'simples\' ü\nquebra'
        root = self.base / hostile
        (root / "memory" / "wiki").mkdir(parents=True)
        (root / "memory" / "wiki" / "KANBAN.md").write_text("- [~] `T-144` Medidor — n\n", encoding="utf-8")
        begun = self.begin_card(root)
        self.assertTrue(Path(begun["ledger_path"]).is_file())
        hostile_title = "Título; touch PWNED-4 $(touch PWNED-5) `x`"
        self.plan(begun, [task("P01", "M", hostile_title)])
        self.start_task(begun, "P01")
        text = self.cli("show", "--root", str(root), "--card", "T-144").stdout
        self.assertIn(hostile_title, text)
        self.assertEqual(self.cli("show", "--root", str(root), "--all").returncode, 0)
        created = [p for p in Path(self.tmp.name).rglob("PWNED*")]
        self.assertEqual(created, [])
        self.assertEqual(list(root.rglob("PWNED*")), [])

    def test_nada_e_escrito_fora_do_root_nem_no_home_nem_no_tmp_do_sistema(self):
        root = self.make_front()
        outside = tree_snapshot(self.base)
        outside = {key: value for key, value in outside.items() if not key.startswith("frente")}
        begun = self.begin_card(root)
        self.plan(begun, [task("P01")])
        self.start_task(begun, "P01")
        self.done_task(begun, "P01")
        self.cli("show", *self.target(begun))
        after = {key: value for key, value in tree_snapshot(self.base).items() if not key.startswith("frente")}
        self.assertEqual(outside, after)
        self.assertEqual(list(self.sandbox_home.iterdir()), [])
        self.assertEqual(list(self.sandbox_tmp.iterdir()), [])


class ProgressCliGitTest(CliTestCase):
    def git(self, root: Path, *args: str) -> subprocess.CompletedProcess:
        environment = self.env(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.com", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.com")
        for inherited in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR"):
            environment.pop(inherited, None)
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, env=environment, check=False)

    def repo(self, name: str = "repo", board: str = "- [~] `T-144` Medidor — n\n") -> Path:
        root = self.make_front(name, board)
        self.assertEqual(self.git(root, "init", "-q").returncode, 0)
        self.git(root, "add", "-A")
        self.assertEqual(self.git(root, "commit", "-q", "-m", "board").returncode, 0)
        return root

    def test_o_diretorio_e_ignorado_de_fato_e_o_git_do_consumidor_nao_ganha_alteracao(self):
        root = self.repo()
        begun = self.begin_card(root)
        self.plan(begun, [task("P01")])
        self.start_task(begun, "P01")
        self.assertEqual((root / ".orq/progress/.gitignore").read_text(encoding="utf-8"), "*\n")
        self.assertEqual(self.git(root, "check-ignore", "-q", begun["ledger_path"]).returncode, 0)
        self.assertEqual(self.git(root, "check-ignore", "-q", str(root / ".orq/progress/v1/locks/cards-T-144.lock")).returncode, 0)
        self.assertEqual(self.git(root, "status", "--porcelain").stdout, "")
        self.assertEqual(self.git(root, "ls-files", "--others", "--exclude-standard").stdout, "")
        self.assertEqual(self.git(root, "add", "-A").returncode, 0)
        self.assertEqual(self.git(root, "diff", "--cached", "--name-only").stdout, "")

    def test_ignorado_tambem_quando_o_root_e_subpasta_do_repositorio_e_em_worktree(self):
        root = self.repo("principal")
        front = self.base / "worktree-da-frente"
        self.assertEqual(self.git(root, "worktree", "add", "-q", str(front)).returncode, 0)
        begun = self.begin_goal(front)
        self.assertEqual(self.git(front, "check-ignore", "-q", begun["ledger_path"]).returncode, 0)
        self.assertEqual(self.git(front, "status", "--porcelain").stdout, "")
        sub = root / "pacote"
        sub.mkdir()
        nested = self.begin_goal(sub)
        self.assertEqual(self.git(root, "check-ignore", "-q", nested["ledger_path"]).returncode, 0)
        self.assertEqual(self.git(root, "status", "--porcelain").stdout, "")

    def test_destino_com_arquivo_versionado_e_recusado_sem_criar_nem_sobrescrever_nada(self):
        root = self.make_front("versionado")
        self.assertEqual(self.git(root, "init", "-q").returncode, 0)
        tracked = root / ".orq" / "progress" / "notas.txt"
        tracked.parent.mkdir(parents=True)
        tracked.write_text("conteúdo versionado\n", encoding="utf-8")
        self.git(root, "add", "-A")
        self.assertEqual(self.git(root, "commit", "-q", "-m", "versionou o destino").returncode, 0)
        before = tree_snapshot(root / ".orq")
        payload = self.expect_error(4, "begin", "--kind", "goal", "--root", str(root), "--host", "claude")
        self.assertEqual(payload["code"], "destino-versionado")
        self.assertEqual(tree_snapshot(root / ".orq"), before)
        self.assertFalse((root / ".orq/progress/.gitignore").exists())
        self.assertFalse((root / ".orq/progress/v1").exists())

    def test_gitignore_existente_e_preservado_e_verificado(self):
        root = self.repo()
        ignore = root / ".orq" / "progress" / ".gitignore"
        ignore.parent.mkdir(parents=True)
        original = "# regra própria\n.gitignore\nv1/\n!nao-mexe\n"
        ignore.write_text(original, encoding="utf-8")
        begun = self.begin_goal(root)
        self.assertEqual(ignore.read_text(encoding="utf-8"), original)
        self.assertEqual(self.git(root, "check-ignore", "-q", begun["ledger_path"]).returncode, 0)

    def test_gitignore_existente_que_nao_ignora_o_armazenamento_recusa_sem_alterar_o_arquivo(self):
        root = self.repo()
        ignore = root / ".orq" / "progress" / ".gitignore"
        ignore.parent.mkdir(parents=True)
        ignore.write_text("# nada ignorado aqui\n", encoding="utf-8")
        payload = self.expect_error(4, "begin", "--kind", "goal", "--root", str(root), "--host", "claude")
        self.assertEqual(payload["code"], "armazenamento-nao-ignorado")
        self.assertEqual(ignore.read_text(encoding="utf-8"), "# nada ignorado aqui\n")
        self.assertFalse((root / ".orq/progress/v1").exists())

    def test_gitignore_que_cobre_so_parte_do_armazenamento_recusa_sem_criar_ledger_nem_lock(self):
        parciais = {
            "so cards e o proprio .gitignore": ".gitignore\nv1/cards/*.json\n",
            "cards e goals, sem locks": ".gitignore\nv1/cards/*.json\nv1/goals/*.json\n",
            "json e locks, sem temporarios": ".gitignore\nv1/*/*.json\nv1/locks/*.lock\n",
            "tudo em v1/, sem o proprio .gitignore": "v1/\n",
        }
        for nome, conteudo in parciais.items():
            with self.subTest(nome):
                root = self.repo(f"parcial-{abs(hash(nome))}")
                ignore = root / ".orq" / "progress" / ".gitignore"
                ignore.parent.mkdir(parents=True)
                ignore.write_text(conteudo, encoding="utf-8")
                payload = self.expect_error(4, "begin", "--kind", "goal", "--root", str(root), "--host", "claude")
                self.assertEqual(payload["code"], "armazenamento-nao-ignorado")
                self.assertEqual(ignore.read_text(encoding="utf-8"), conteudo)
                self.assertEqual(sorted(p.name for p in (root / ".orq/progress").rglob("*")), [".gitignore"])  # nada de ledger, lock ou v1

    def test_gitignore_que_ignora_nomes_ficticios_mas_expoe_o_destino_real_e_recusado(self):
        root = self.repo("expoe-real", board="- [~] `T-999` Medidor — n\n")
        ignore = root / ".orq" / "progress" / ".gitignore"
        ignore.parent.mkdir(parents=True)
        conteudo = "*\n!v1/\n!v1/cards/\n!v1/cards/T-999.json\n"
        ignore.write_text(conteudo, encoding="utf-8")
        payload = self.expect_error(
            4, "begin", "--kind", "card", "--root", str(root), "--board", str(root / "memory/wiki/KANBAN.md"),
            "--thread-root", str(root / "memory/wiki"), "--card", "T-999", "--front", "f", "--host", "claude",
        )
        self.assertEqual(payload["code"], "armazenamento-nao-ignorado")
        self.assertIn("T-999.json", payload["message"])
        self.assertEqual(ignore.read_text(encoding="utf-8"), conteudo)
        self.assertEqual(sorted(p.name for p in (root / ".orq/progress").rglob("*")), [".gitignore"])  # sem ledger, lock nem v1
        # outro card, cujo nome real continua ignorado por `*`, passa
        outro = self.repo("expoe-real-ok", board="- [~] `T-1` Outro — n\n")
        (outro / ".orq/progress").mkdir(parents=True)
        (outro / ".orq/progress/.gitignore").write_text(conteudo, encoding="utf-8")
        self.begin_card(outro, "T-1")

    GITIGNORE_COM_TEMPORARIO_EXPOSTO = "*\n!v1/\n!v1/cards/\n!v1/cards/*.tmp\nv1/cards/*.probe*.tmp\n"

    def test_gitignore_que_ignora_a_sonda_do_temporario_mas_expoe_o_temporario_real_recusa_a_mutacao(self):
        root = self.repo()
        begun = self.begin_card(root)
        self.plan(begun, [task("P01")])
        ledger = Path(begun["ledger_path"])
        antes = ledger.read_bytes()
        ignore = root / ".orq/progress/.gitignore"
        ignore.write_text(self.GITIGNORE_COM_TEMPORARIO_EXPOSTO, encoding="utf-8")
        # o ledger, o lock e a sonda fictícia do temporário continuam ignorados; o temporário real não
        self.assertEqual(self.git(root, "check-ignore", "-q", str(ledger)).returncode, 0)
        payload = self.expect_error(4, "pause", *self.target(begun), "--session-key", begun["session_key"])
        self.assertEqual(payload["code"], "armazenamento-nao-ignorado")
        self.assertEqual(ledger.read_bytes(), antes)
        self.assertEqual(sorted(p.name for p in ledger.parent.iterdir()), ["T-144.json"])  # nenhum temporário sobrou
        self.assertEqual(self.git(root, "status", "--porcelain", "--untracked-files=all").stdout, "")
        ignore.write_text("*\n", encoding="utf-8")
        self.ok("pause", *self.target(begun), "--session-key", begun["session_key"])

    def test_gitignore_que_expoe_o_temporario_real_recusa_o_begin_sem_ledger_nem_temporario(self):
        root = self.repo()
        ignore = root / ".orq/progress/.gitignore"
        ignore.parent.mkdir(parents=True)
        ignore.write_text(self.GITIGNORE_COM_TEMPORARIO_EXPOSTO, encoding="utf-8")
        payload = self.expect_error(
            4, "begin", "--kind", "card", "--root", str(root), "--board", str(root / "memory/wiki/KANBAN.md"),
            "--thread-root", str(root / "memory/wiki"), "--card", "T-144", "--front", "f", "--host", "claude",
        )
        self.assertEqual(payload["code"], "armazenamento-nao-ignorado")
        cards = root / ".orq/progress/v1/cards"
        self.assertEqual(sorted(p.name for p in cards.iterdir()), [])  # sem ledger e sem temporário
        self.assertEqual(ignore.read_text(encoding="utf-8"), self.GITIGNORE_COM_TEMPORARIO_EXPOSTO)

    def test_gravacao_com_gitignore_padrao_funciona_e_git_status_fica_vazio(self):
        root = self.repo()
        begun = self.begin_card(root)
        self.plan(begun, [task("P01"), task("P02")])
        self.start_task(begun, "P01")
        self.done_task(begun, "P01")
        self.assertEqual(self.git(root, "status", "--porcelain", "--untracked-files=all").stdout, "")
        self.assertEqual(sorted(p.name for p in Path(begun["ledger_path"]).parent.iterdir()), ["T-144.json"])

    def test_mutacao_confere_o_destino_real_antes_de_gravar(self):
        root = self.repo()
        begun = self.begin_card(root)
        self.plan(begun, [task("P01")])
        antes = Path(begun["ledger_path"]).read_bytes()
        ignore = root / ".orq/progress/.gitignore"
        ignore.write_text("*\n!v1/\n!v1/cards/\n!v1/cards/T-144.json\n", encoding="utf-8")  # o ledger real deixa de ser ignorado
        payload = self.expect_error(4, "pause", *self.target(begun), "--session-key", begun["session_key"])
        self.assertEqual(payload["code"], "armazenamento-nao-ignorado")
        self.assertEqual(Path(begun["ledger_path"]).read_bytes(), antes)
        self.assertEqual(sorted(p.name for p in Path(begun["ledger_path"]).parent.iterdir()), ["T-144.json"])  # nem temporário
        self.assertEqual(self.cli("show", *self.target(begun)).returncode, 0)  # leitura segue livre
        ignore.write_text("*\n", encoding="utf-8")
        self.ok("pause", *self.target(begun), "--session-key", begun["session_key"])

    def test_gitignore_que_cobre_todos_os_destinos_efetivos_e_aceito(self):
        cobertura = {
            "estrela": "*\n",
            "v1 e o proprio arquivo": ".gitignore\nv1/\n",
            "so os destinos reais": ".gitignore\nv1/*/*.json\nv1/*/*.tmp\nv1/locks/*.lock\n",
        }
        for nome, conteudo in cobertura.items():
            with self.subTest(nome):
                root = self.repo(f"total-{abs(hash(nome))}")
                ignore = root / ".orq" / "progress" / ".gitignore"
                ignore.parent.mkdir(parents=True)
                ignore.write_text(conteudo, encoding="utf-8")
                begun = self.begin_goal(root)
                self.mutate("plan", begun, "--input", "-", stdin=json.dumps({"tasks": [task("P01")]}))
                self.assertEqual(self.git(root, "status", "--porcelain", "--untracked-files=all").stdout, "")

    def test_fora_de_repositorio_o_gitignore_e_criado_e_nenhum_git_e_exigido(self):
        root = self.make_front("sem-git")
        begun = self.begin_goal(root)
        self.assertEqual((root / ".orq/progress/.gitignore").read_text(encoding="utf-8"), "*\n")
        empty_bin = self.base / "sem-git-no-path"
        empty_bin.mkdir()
        # Sem Git instalado e sem metadado Git no caminho, nada a verificar; o begin segue.
        self.ok("begin", "--kind", "goal", "--root", str(root), "--host", "claude", env=self.env(PATH=str(empty_bin)))
        self.assertTrue(Path(begun["ledger_path"]).is_file())

    def test_git_ausente_com_metadado_git_nao_aceita_o_destino_sem_prova(self):
        root = self.repo("com-git")
        empty_bin = self.base / "bin-vazio"
        empty_bin.mkdir()
        payload = self.expect_error(4, "begin", "--kind", "goal", "--root", str(root), "--host", "claude", env=self.env(PATH=str(empty_bin)))
        self.assertEqual(payload["code"], "git-indisponivel")
        self.assertFalse((root / ".orq").exists())

    def test_goal_nao_toca_no_board_nem_na_thread(self):
        root = self.repo()
        before = tree_snapshot(root / "memory")
        begun = self.begin_goal(root)
        self.mutate("plan", begun, "--input", "-", stdin=json.dumps({"tasks": [task("P01")]}))
        self.start_task(begun, "P01")
        self.done_task(begun, "P01")
        self.mutate("phase", begun, "--value", "verification")
        self.mutate("close", begun, "--outcome", "reported_complete", "--evidence-ref", "t#fim")
        self.assertEqual(tree_snapshot(root / "memory"), before)
        view = self.show_json(begun)
        self.assertEqual(view["phase"]["key"], "verification")
        self.assertEqual(view["lifecycle"], "closed")


class ProgressCliContencaoTest(CliTestCase):
    """Todo destino de escrita (diretórios, ledger, lock) tem de ficar dentro de realpath(root)."""

    def outside(self) -> Path:
        fora = self.base / "fora"
        fora.mkdir(exist_ok=True)
        return fora

    def assert_nada_fora(self) -> None:
        self.assertEqual(sorted(self.outside().rglob("*")), [])

    def test_v1_symlink_para_fora_recusa_o_begin_sem_gravar_fora(self):
        root = self.make_front()
        (root / ".orq/progress").mkdir(parents=True)
        os.symlink(self.outside(), root / ".orq/progress/v1")
        payload = self.expect_error(4, "begin", "--kind", "goal", "--root", str(root), "--host", "claude")
        self.assertEqual(payload["code"], "destino-fora-do-root")
        self.assert_nada_fora()

    def test_subdiretorio_symlink_para_fora_recusa_o_begin_para_cards_goals_e_locks(self):
        for nome in ("cards", "goals", "locks"):
            with self.subTest(nome):
                root = self.make_front(f"frente-{nome}")
                (root / ".orq/progress/v1").mkdir(parents=True)
                os.symlink(self.outside(), root / ".orq/progress/v1" / nome)
                payload = self.expect_error(4, "begin", "--kind", "goal", "--root", str(root), "--host", "claude")
                self.assertEqual(payload["code"], "destino-fora-do-root")
                self.assert_nada_fora()

    def test_symlink_pendurado_para_fora_tambem_e_recusado_antes_de_criar_o_alvo(self):
        root = self.make_front()
        (root / ".orq/progress").mkdir(parents=True)
        os.symlink(self.outside() / "ainda-nao-existe", root / ".orq/progress/v1")
        self.expect_error(4, "begin", "--kind", "goal", "--root", str(root), "--host", "claude")
        self.assertFalse((self.outside() / "ainda-nao-existe").exists())

    def test_orq_ou_progress_symlink_para_fora_e_recusado_antes_de_criar_diretorio(self):
        root = self.make_front()
        os.symlink(self.outside(), root / ".orq")
        payload = self.expect_error(4, "begin", "--kind", "goal", "--root", str(root), "--host", "claude")
        self.assertEqual(payload["code"], "destino-fora-do-root")
        self.assert_nada_fora()

    def test_mutacao_recusa_ledger_ou_lock_resolvidos_fora_do_root(self):
        root = self.make_front()
        begun = self.begin_goal(root)
        goals = root / ".orq/progress/v1/goals"
        shutil_move = self.outside() / "goals"
        goals.rename(shutil_move)
        os.symlink(shutil_move, goals)  # o diretório de goals agora vive fora, com o ledger dentro
        antes = sorted((p.name, p.read_bytes()) for p in shutil_move.iterdir())
        casos = (
            (["--ledger", begun["ledger_path"]], "destino-fora-do-layout"),  # o caminho canônico já não está no layout
            (["--root", str(root), "--run", begun["run_id"]], "destino-fora-do-root"),
        )
        for alvo, codigo in casos:
            with self.subTest(alvo=alvo[0]):
                payload = self.expect_error(4, "pause", *alvo, "--session-key", begun["session_key"])
                self.assertEqual(payload["code"], codigo)
        self.assertEqual(sorted((p.name, p.read_bytes()) for p in shutil_move.iterdir()), antes)

    def test_mutacao_recusa_lock_resolvido_fora_do_root(self):
        root = self.make_front()
        begun = self.begin_goal(root)
        locks = root / ".orq/progress/v1/locks"
        fora = self.outside() / "locks"
        locks.rename(fora)
        os.symlink(fora, locks)
        payload = self.expect_error(4, "pause", "--ledger", begun["ledger_path"], "--session-key", begun["session_key"])
        self.assertEqual(payload["code"], "destino-fora-do-root")
        self.assertEqual(sorted(p.name for p in fora.iterdir()), [f"goals-{begun['run_id']}.lock"])  # nenhum arquivo novo fora
        self.assertEqual(self.show_json(begun)["lifecycle"], "active")

    def test_ledger_com_ponto_ponto_e_canonicalizado_e_usa_o_mesmo_lock(self):
        root = self.make_front()
        begun = self.begin_goal(root)
        real = Path(begun["ledger_path"])
        torto = str(real.parent / ".." / "goals" / real.name)
        holder = self.hold_lock(real, 1.0)
        started = time.monotonic()
        self.ok("pause", "--ledger", torto, "--session-key", begun["session_key"])
        self.assertGreater(time.monotonic() - started, 0.4)
        holder.communicate(timeout=10)
        self.assertEqual(self.show_json(begun)["lifecycle"], "paused")

    def test_mutacao_fora_do_layout_e_recusada_e_a_leitura_continua_permitida(self):
        root = self.make_front()
        begun = self.begin_goal(root)
        real = Path(begun["ledger_path"])
        fora = self.outside()
        copia = fora / "copia.json"
        copia.write_bytes(real.read_bytes())
        (real.parent.parent / "outro").mkdir()
        (real.parent / "sub").mkdir()
        alvos = {
            "diretorio qualquer": copia,
            "v1/outro": real.parent.parent / "outro" / real.name,
            "subdiretorio de goals": real.parent / "sub" / real.name,
            "sem sufixo .json": real.parent / (real.stem + ".txt"),
        }
        for destino in list(alvos.values())[1:]:
            destino.write_bytes(real.read_bytes())
        antes = {nome: destino.read_bytes() for nome, destino in alvos.items()}
        for nome, destino in alvos.items():
            for comando in (
                ["pause", "--ledger", str(destino), "--session-key", begun["session_key"]],
                ["claim", "--ledger", str(destino), "--host", "codex", "--session-key", KEY_B, "--expected-owner", begun["session_key"]],
            ):
                with self.subTest(nome, comando=comando[0]):
                    payload = self.expect_error(4, *comando)
                    self.assertEqual(payload["code"], "destino-fora-do-layout")
        self.assertEqual({nome: destino.read_bytes() for nome, destino in alvos.items()}, antes)
        self.assertEqual(sorted(p.name for p in fora.iterdir()), ["copia.json"])  # nenhum lock lateral ao lado
        shown = self.cli("show", "--ledger", str(copia), "--format", "json")  # leitura não usa lock e segue permitida
        self.assertEqual(shown.returncode, 0, shown.stderr)

    def test_begin_recusado_por_symlink_em_v1_ou_em_cards_nao_escreve_nada(self):
        for alvo in ("v1", "cards"):
            with self.subTest(alvo):
                root = self.make_front(f"frente-{alvo}")
                progress_dir = root / ".orq/progress"
                (progress_dir / "v1").mkdir(parents=True) if alvo == "cards" else progress_dir.mkdir(parents=True)
                os.symlink(self.outside(), progress_dir / "v1" if alvo == "v1" else progress_dir / "v1" / "cards")
                antes = tree_snapshot(self.base)
                payload = self.expect_error(4, "begin", "--kind", "goal", "--root", str(root), "--host", "claude")
                self.assertEqual(payload["code"], "destino-fora-do-root")
                self.assertEqual(tree_snapshot(self.base), antes)  # nem .gitignore, nem diretório, nem lock
                self.assertFalse((progress_dir / ".gitignore").exists())

    def test_sondas_sao_os_destinos_reais_e_o_temporario_segue_o_padrao_do_write_ledger(self):
        root = self.make_front()
        begun = self.begin_goal(root)
        usados = []
        real_replace = os.replace

        def registra(source, destination):
            usados.append((Path(source).name, Path(destination).name))
            real_replace(source, destination)

        ledger = Path(os.path.realpath(begun["ledger_path"]))
        with mock.patch.object(progress.os, "replace", side_effect=registra):
            progress.mutate_ledger(ledger, begun["session_key"], None, {"op": "pause"}, NOW)
        (temporario, destino), = usados
        raiz = Path(os.path.realpath(root))
        sondas = progress.destination_probes(raiz, ledger)
        base = ".orq/progress/v1"
        self.assertEqual(sondas[:3], [".orq/progress/.gitignore", f"{base}/goals/{ledger.name}", f"{base}/locks/goals-{ledger.stem}.lock"])
        sonda_temporaria = Path(sondas[3])
        self.assertEqual(sonda_temporaria.parent.as_posix(), f"{base}/goals")
        self.assertTrue(temporario.startswith(progress.temporary_prefix(destino)))
        self.assertTrue(sonda_temporaria.name.startswith(progress.temporary_prefix(destino)))
        self.assertTrue(temporario.endswith(progress.TEMPORARY_SUFFIX))
        self.assertTrue(sonda_temporaria.name.endswith(progress.TEMPORARY_SUFFIX))
        self.assertEqual(len(sondas), 4)  # sem lock lateral: nenhuma mutação o usa

    def test_caminho_normal_continua_funcionando_com_root_que_e_symlink(self):
        real = self.make_front("real")
        link = self.base / "atalho"
        os.symlink(real, link)
        begun = self.begin_goal(link)
        self.ok("pause", "--ledger", begun["ledger_path"], "--session-key", begun["session_key"])
        self.assertEqual(self.show_json(begun)["lifecycle"], "paused")


class ProgressCliBoardTest(CliTestCase):
    def test_board_canonico_diferente_da_worktree_define_a_fase_e_nada_e_criado_na_worktree(self):
        primary = self.make_front("principal", "- [~] `T-144` Medidor — n\n")
        front = self.base / "worktree"
        front.mkdir()
        board = primary / "memory" / "wiki" / "KANBAN.md"
        begun = self.ok(
            "begin", "--kind", "card", "--root", str(front), "--board", str(board), "--thread-root", str(front / "memory/wiki"),
            "--card", "T-144", "--front", "frente-mods", "--host", "codex",
        )
        self.assertEqual(Path(begun["ledger_path"]).parent.parent.parent.parent.parent, Path(os.path.realpath(front)))
        self.mutate("plan", begun, "--input", "-", stdin=json.dumps({
            "source_ref": "p#1", "approval_ref": "t#1", "tasks": [task("P01")],
        }))
        self.mutate("phase", begun, "--value", "review")
        self.assertEqual(self.show_json(begun)["phase"]["key"], "review")
        board.write_text("- [?] `T-144` Medidor — n\n", encoding="utf-8")
        view = self.show_json(begun)
        self.assertEqual((view["phase"]["key"], view["phase"]["source"]), ("validate", "board"))
        self.assertEqual(view["phase"]["warning"], "atividade 'review' diverge do board; vale o board")
        self.assertFalse((front / "memory").exists())  # nenhuma cópia local do board nasceu

    def test_plan_de_card_exige_ready_no_board_e_close_x(self):
        root = self.make_front(board="- [?] `T-144` Medidor — n\n")
        begun = self.begin_card(root)
        payload = self.expect_error(
            2, "plan", *self.target(begun), "--session-key", begun["session_key"], "--input", "-",
            stdin=json.dumps({"source_ref": "p#1", "approval_ref": "t#1", "tasks": [task("P01")]}),
        )
        self.assertEqual(payload["code"], "board-incompativel")
        self.assertEqual(self.show_json(begun)["progress"]["state"], "sem-plano")

    def test_board_com_card_ausente_duplicado_em_cerca_ou_arquivado(self):
        cases = {
            "card-ausente": "- [ ] `T-1` outro — n\n",
            "card-duplicado": "- [~] `T-144` a — n\n- [~] `T-144` b — n\n",
        }
        for code, board in cases.items():
            with self.subTest(code=code):
                root = self.make_front(f"b-{code}", board)
                payload = self.expect_error(
                    4, "begin", "--kind", "card", "--root", str(root), "--board", str(root / "memory/wiki/KANBAN.md"),
                    "--thread-root", str(root / "memory/wiki"), "--card", "T-144", "--front", "f", "--host", "claude",
                )
                self.assertEqual(payload["code"], "board-indisponivel")
                self.assertIn(code, payload["message"])
                self.assertFalse((root / ".orq").exists())
        fenced = self.make_front("b-cerca", "```\n- [~] `T-144` em cerca — n\n```\n")
        archived = self.make_front("b-arquivo", "# b\n## Arquivado\n- [x] `T-144` velho — n\n")
        for root in (fenced, archived):
            self.expect_error(
                4, "begin", "--kind", "card", "--root", str(root), "--board", str(root / "memory/wiki/KANBAN.md"),
                "--thread-root", str(root / "memory/wiki"), "--card", "T-144", "--front", "f", "--host", "claude",
            )

    def test_board_que_some_depois_deixa_a_fase_indisponivel_e_o_percentual_visivel(self):
        root = self.make_front()
        begun = self.begin_card(root)
        self.plan(begun, [task("P01"), task("P02")])
        self.start_task(begun, "P01")
        self.done_task(begun, "P01")
        (root / "memory/wiki/KANBAN.md").unlink()
        text = self.cli("show", *self.target(begun))
        self.assertEqual(text.returncode, 0)
        self.assertIn("fase indisponível", text.stdout)
        self.assertIn("1/2 passos concluídos · 50% do plano", text.stdout)
        self.assertIn("board-ausente", text.stdout)

    def test_o_medidor_nunca_move_card_nem_altera_o_board(self):
        root = self.make_front()
        board = root / "memory/wiki/KANBAN.md"
        before = board.read_bytes()
        begun = self.begin_card(root)
        self.plan(begun, [task("P01")])
        self.start_task(begun, "P01")
        self.done_task(begun, "P01")
        self.mutate("phase", begun, "--value", "done")
        self.mutate("pause", begun)
        self.assertEqual(board.read_bytes(), before)
        view = self.show_json(begun)
        self.assertEqual(view["phase"]["key"], "implementation")  # `done` na atividade não vence o `[~]`
        self.assertEqual(view["progress"]["percent"], 100)
        self.assertNotIn("[x]", self.cli("show", *self.target(begun)).stdout)


class ProgressCliLeitoresTest(CliTestCase):
    def prepared(self) -> tuple:
        root = self.make_front()
        begun = self.begin_card(root)
        self.plan(begun, [task("P01"), task("P02")])
        self.start_task(begun, "P01")
        return root, begun

    def test_show_em_todos_os_formatos_nao_escreve_nada(self):
        root, begun = self.prepared()
        before = tree_snapshot(root)
        for fmt in ("text", "json", "segment"):
            self.assertEqual(self.cli("show", *self.target(begun), "--format", fmt).returncode, 0)
        self.assertEqual(self.cli("show", "--root", str(root), "--all").returncode, 0)
        self.assertEqual(self.cli("show", "--root", str(root), "--card", "T-144").returncode, 0)
        self.assertEqual(tree_snapshot(root), before)

    def test_show_nao_cria_diretorio_lock_nem_arquivo_quando_nada_existe(self):
        root = self.make_front()
        before = tree_snapshot(root)
        for args in (("--root", str(root), "--card", "T-144"), ("--root", str(root), "--all")):
            self.cli("show", *args)
        self.assertEqual(self.cli("watch", "--root", str(root), "--card", "T-144", "--count", "2", "--interval", "0.1").returncode, 0)
        self.assertEqual(tree_snapshot(root), before)
        self.assertFalse((root / ".orq").exists())

    def test_ledger_inexistente_ou_corrompido_no_show_e_exit_4_sem_percentual(self):
        root, begun = self.prepared()
        Path(begun["ledger_path"]).write_text("{ quebrado", encoding="utf-8")
        result = self.cli("show", *self.target(begun))
        self.assertEqual((result.returncode, result.stdout), (4, ""))
        self.assertNotIn("%", result.stdout)
        self.assertEqual(json.loads(result.stderr)["code"], "ledger-invalido")
        Path(begun["ledger_path"]).write_text(json.dumps({"schema_version": 2}), encoding="utf-8")
        self.assertEqual(json.loads(self.cli("show", *self.target(begun)).stderr)["code"], "versao-desconhecida")
        Path(begun["ledger_path"]).write_bytes(b" " * (progress.MAX_LEDGER_BYTES + 1))
        self.assertEqual(json.loads(self.cli("show", *self.target(begun)).stderr)["code"], "ledger-grande")

    def test_watch_emite_o_quadro_atual_e_sem_escrever(self):
        root, begun = self.prepared()
        before = tree_snapshot(root)
        result = self.cli("watch", *self.target(begun), "--count", "3", "--interval", "0.1")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.count("T-144 · "), 1)  # quadro igual não é reimpresso
        self.assertIn("Em execução: P01", result.stdout)
        self.assertEqual(tree_snapshot(root), before)

    def test_watch_usa_a_mesma_projecao_do_show(self):
        root, begun = self.prepared()
        shown = self.cli("show", *self.target(begun)).stdout.rstrip("\n")
        watched = self.cli("watch", *self.target(begun), "--count", "1").stdout.rstrip("\n")
        self.assertEqual(watched, shown)

    def test_watch_valida_argumentos(self):
        root, begun = self.prepared()
        for extra in (["--interval", "0"], ["--interval", "99999"], ["--count", "-1"], ["--interval", "abc"]):
            with self.subTest(extra=extra):
                self.assertEqual(self.cli("watch", *self.target(begun), *extra).returncode, 2)
        self.assertEqual(self.cli("watch").returncode, 2)

    def test_watch_acompanha_a_mudanca_e_sai_limpo_com_sigint_sem_afetar_o_observado(self):
        root, begun = self.prepared()
        proc = subprocess.Popen(
            [sys.executable, str(SCRIPT), "watch", *self.target(begun), "--interval", "0.1"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=self.env(),
            preexec_fn=lambda: signal.signal(signal.SIGINT, signal.SIG_DFL),
        )
        self.addCleanup(lambda: proc.poll() is None and proc.kill())
        lines: "queue.Queue[str]" = queue.Queue()
        reader = threading.Thread(target=lambda: [lines.put(line) for line in proc.stdout], daemon=True)
        reader.start()

        def wait_for(fragment: str, timeout: float = 15.0) -> str:
            seen = ""
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                try:
                    seen += lines.get(timeout=0.2)
                except queue.Empty:
                    continue
                if fragment in seen:
                    return seen
            raise AssertionError(f"watch não mostrou {fragment!r} a tempo; viu {seen!r}")

        wait_for("0/2 passos concluídos")
        self.done_task(begun, "P01")  # o Manager atualiza enquanto o leitor observa
        wait_for("1/2 passos concluídos · 50% do plano")
        before = tree_snapshot(root)
        proc.send_signal(signal.SIGINT)
        self.assertEqual(proc.wait(timeout=15), 0)
        reader.join(timeout=5)
        err = proc.stderr.read()
        proc.stdout.close()
        proc.stderr.close()
        self.assertNotIn("Traceback", err)
        self.assertEqual(tree_snapshot(root), before)  # encerrar o leitor não mexe em nada
        self.assertEqual(self.show_json(begun)["revision"], 4)  # e o ledger observado segue utilizável
        self.assertFalse(self.done_task(begun, "P01")["changed"])

    def test_watch_mostra_indisponibilidade_enquanto_o_ledger_nao_existe_e_continua(self):
        root = self.make_front()
        result = self.cli("watch", "--root", str(root), "--card", "T-144", "--count", "2", "--interval", "0.1")
        self.assertEqual(result.returncode, 0)
        self.assertIn("indisponível:", result.stdout)
        self.assertEqual(result.stdout.count("indisponível:"), 1)


if __name__ == "__main__":
    unittest.main()
