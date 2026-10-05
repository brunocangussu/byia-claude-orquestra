#!/usr/bin/env python3
"""Medidor de progresso portátil do Orquestra: ledger por execução, cálculo e vistas.

O ledger guarda os passos aprovados de UMA execução (um card ou um goal avulso) na frente dona,
em `<raiz>/.orq/progress/v1/`, diretório ignorado pelo Git. A fase vem do board; o percentual vem
dos passos concluídos. Só o Manager escreve o ledger; `show` e `watch` são leitores estritos. `bind`
liga a sessão nativa do host a um ledger num arquivo próprio (`sessions/`), sem tocar no ledger.

Saída: 0 sucesso ou repetição idempotente · 2 argumento, entrada ou transição inválidos ·
3 revisão ou dono divergentes · 4 estado, lock, board ou persistência indisponíveis.
"""

from __future__ import annotations

import argparse
import contextlib
import copy
from datetime import datetime, timezone
import errno
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys
import tempfile
import time
from typing import Any, Callable, Iterator, Mapping, Optional, Tuple
import unicodedata
import uuid

try:
    import fcntl
except ImportError:  # pragma: no cover - fallback para Windows
    fcntl = None

try:
    import msvcrt
except ImportError:  # pragma: no cover - indisponível fora do Windows
    msvcrt = None


SCHEMA_VERSION = 1
MAX_LEDGER_BYTES = 1024 * 1024
MAX_INPUT_BYTES = 1024 * 1024
MAX_TASKS = 200
MAX_TITLE_CHARS = 160
MAX_REF_CHARS = 200
MAX_EVIDENCE_REFS = 20
MAX_BINDING_BYTES = 64 * 1024
MAX_SESSION_ID_CHARS = 256
MAX_RECENT_EVENTS = 128
MAX_EVENT_ID_CHARS = 200
NUDGE_AFTER_CALLS = 4
LOCK_WAIT_SECONDS = 5.0
HOOK_LOCK_WAIT_SECONDS = 1.0
MAX_FRONT_ANCESTORS = 64
MAX_STATUSLINE_BYTES = 1024 * 1024
STATUSLINE_SUBPROCESS_SECONDS = 1.5
LOCK_POLL_SECONDS = 0.01
SUBPROCESS_TIMEOUT_SECONDS = 5.0
NEXT_PREVIEW = 3

KINDS = ("card", "goal")
HOSTS = ("claude", "codex", "other")
BINDING_HOSTS = ("claude", "codex")  # os hosts com adaptador de hooks; "other" não tem ID nativo a ligar
SESSION_START_SOURCES = ("startup", "resume", "clear", "compact", "fork")
LIFECYCLES = ("active", "paused", "closed")
CARD_ACTIVITIES = ("planning", "gate", "ready", "implementation", "review", "docs", "validate", "done")
GOAL_ACTIVITIES = ("planning", "execution", "verification")
SIZE_WEIGHTS = {"S": 1, "M": 2, "L": 3}
STATUSES = ("pending", "active", "done", "dropped")
DROP_REASONS = ("obsolete", "duplicate", "scope_change")
CHANGE_REASONS = DROP_REASONS + ("reopened",)
ADD_REASONS = ("scope_change",)
OUTCOMES = ("reported_complete", "cancelled")
BOARD_MARKERS = (" ", ">", "!", "~", "?", "x")
EXECUTING_ACTIVITIES = ("ready", "implementation", "review", "docs")

LEDGER_KEYS = (
    "schema_version",
    "run_id",
    "revision",
    "kind",
    "scope",
    "owner",
    "lifecycle",
    "activity",
    "plan",
    "tasks",
    "closure",
    "created_at",
    "updated_at",
)
SCOPE_KEYS = ("front_root", "front", "card_id", "board_path", "thread_root")
OWNER_KEYS = ("host", "session_key")
PLAN_KEYS = ("source_ref", "approval_ref", "seed_sha256", "baseline_count", "baseline_weight", "registered_at")
TASK_KEYS = (
    "id",
    "title",
    "size",
    "status",
    "acceptance_ref",
    "executor",
    "evidence_refs",
    "change_reason",
    "created_at",
    "started_at",
    "finished_at",
)
EXECUTOR_KEYS = ("host", "role", "label")
CLOSURE_KEYS = ("outcome", "evidence_ref", "closed_at")
BINDING_KEYS = (
    "schema_version",
    "session_key",
    "host",
    "ledger_path",
    "run_id",
    "calls_without_plan",
    "nudged",
    "recent_event_ids",
)

PHASE_LABELS = {
    "backlog": "backlog",
    "planning": "planejamento",
    "gate": "gate do dono",
    "ready": "pronto para iniciar",
    "implementation": "implementação",
    "review": "revisão",
    "docs": "documentação",
    "validate": "validação do dono",
    "done": "concluído",
    "execution": "execução",
    "verification": "verificação",
}
BOARD_PHASES = {" ": "backlog", ">": "planning", "!": "gate", "?": "validate", "x": "done"}

CARD_RE = re.compile(r"^T-[0-9]+$")
FRONT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
TASK_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,32}$")
SESSION_KEY_RE = re.compile(r"^[0-9a-f]{64}$")
TIMESTAMP_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")
LABEL_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/@+·-]{0,59}$")
CODE_RE = re.compile(r"[^a-z0-9-]")
# Controles bidirecionais reescrevem a ordem visual do texto num terminal.
BIDI_CONTROLS = frozenset("‎‏‪‫‬‭‮⁦⁧⁨⁩")
GIT_TIMEOUT_SECONDS = 5.0
LEDGER_DIRECTORIES = ("cards", "goals")
BINDING_DIRECTORY = "sessions"
STORAGE_DIRECTORIES = LEDGER_DIRECTORIES + (BINDING_DIRECTORY, "locks")
TEMPORARY_SUFFIX = ".tmp"
TEMPORARY_PROBE_TOKEN = "probe000"  # trecho fictício da pré-checagem barata; a prova é o nome reservado em write_ledger


class ProgressError(Exception):
    """Falha esperada; o código de saída vem da subclasse."""

    exit_code = 2

    def __init__(self, message: str, code: str = "erro") -> None:
        super().__init__(message)
        self.code = code


class InputError(ProgressError):
    """Argumento, entrada ou transição inválidos."""

    exit_code = 2


class ConflictError(ProgressError):
    """Revisão ou dono divergentes: reler, nunca repetir cegamente."""

    exit_code = 3

    def __init__(self, message: str, code: str = "conflito", revision: Optional[int] = None) -> None:
        super().__init__(message, code)
        self.revision = revision


class UnavailableError(ProgressError):
    """Estado, lock, board ou persistência indisponíveis."""

    exit_code = 4


class LedgerValidationError(ValueError):
    """Conteúdo do ledger fora do contrato v1."""

    def __init__(self, message: str, code: str = "ledger-invalido") -> None:
        super().__init__(message)
        self.code = code


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ── Validação ───────────────────────────────────────────────────────────────


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _fail(where: str, message: str) -> None:
    raise LedgerValidationError(f"{where}: {message}")


def _exact_keys(where: str, value: Any, required: tuple, optional: tuple = ()) -> None:
    if not isinstance(value, dict):
        _fail(where, "deve ser um objeto")
    missing = [key for key in required if key not in value]
    extra = [str(key) for key in value if key not in required and key not in optional]
    if missing:
        _fail(where, "campos ausentes: " + ", ".join(sorted(missing)))
    if extra:
        _fail(where, "campos não permitidos: " + ", ".join(sorted(extra)))


def _check_enum(where: str, value: Any, allowed: tuple) -> None:
    if not isinstance(value, str) or value not in allowed:
        _fail(where, "valor fora de " + "|".join(allowed))


def has_terminal_controls(text: str) -> bool:
    return any(
        unicodedata.category(char) in ("Cc", "Cs", "Zl", "Zp") or char in BIDI_CONTROLS for char in text
    )


def _check_text(where: str, value: Any, max_chars: int) -> None:
    if not isinstance(value, str) or not value.strip():
        _fail(where, "deve ser texto não vazio")
    if len(value) > max_chars:
        _fail(where, f"excede {max_chars} caracteres")
    if has_terminal_controls(value):
        _fail(where, "contém caractere de controle de terminal")


def _check_ref(where: str, value: Any, nullable: bool = False) -> None:
    if value is None and nullable:
        return
    if not isinstance(value, str) or not value:
        _fail(where, "deve ser uma referência (identificador ou caminho local)")
    if len(value) > MAX_REF_CHARS:
        _fail(where, f"excede {MAX_REF_CHARS} caracteres")
    if has_terminal_controls(value) or any(char.isspace() for char in value):
        _fail(where, "referência não pode conter espaço nem controle; guarde o identificador, não a evidência")


def _check_timestamp(where: str, value: Any, nullable: bool = False) -> None:
    if value is None and nullable:
        return
    if not isinstance(value, str) or not TIMESTAMP_RE.match(value):
        _fail(where, "timestamp UTC esperado (AAAA-MM-DDTHH:MM:SSZ)")
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        _fail(where, "timestamp inexistente")


def _check_absolute_path(where: str, value: Any, nullable: bool = False) -> None:
    if value is None and nullable:
        return
    if not isinstance(value, str) or not value or "\0" in value or not os.path.isabs(value):
        _fail(where, "deve ser um caminho absoluto")


def _check_session_key(where: str, value: Any) -> None:
    if not isinstance(value, str) or not SESSION_KEY_RE.match(value):
        _fail(where, "deve ter 64 hexadecimais minúsculos")


def _check_run_id(value: Any) -> None:
    try:
        parsed = uuid.UUID(str(value))
    except ValueError:
        _fail("run_id", "UUID esperado")
    if str(parsed) != value:
        _fail("run_id", "UUID em forma canônica minúscula esperado")


def _check_executor(where: str, value: Any) -> None:
    _exact_keys(where, value, EXECUTOR_KEYS)
    _check_enum(f"{where}.host", value["host"], HOSTS)
    for field in ("role", "label"):
        if not isinstance(value[field], str) or not LABEL_RE.match(value[field]):
            _fail(f"{where}.{field}", "identificador genérico esperado (letras, dígitos e ._/@+·-, até 60)")


def _validate_task(where: str, task: Any) -> None:
    _exact_keys(where, task, TASK_KEYS)
    if not isinstance(task["id"], str) or not TASK_ID_RE.match(task["id"]):
        _fail(f"{where}.id", "use letras ASCII, dígitos, _ e -, até 32 caracteres")
    _check_text(f"{where}.title", task["title"], MAX_TITLE_CHARS)
    _check_enum(f"{where}.size", task["size"], tuple(SIZE_WEIGHTS))
    _check_enum(f"{where}.status", task["status"], STATUSES)
    _check_ref(f"{where}.acceptance_ref", task["acceptance_ref"], nullable=True)
    if task["executor"] is not None:
        _check_executor(f"{where}.executor", task["executor"])
    refs = task["evidence_refs"]
    if not isinstance(refs, list) or len(refs) > MAX_EVIDENCE_REFS:
        _fail(f"{where}.evidence_refs", f"lista de até {MAX_EVIDENCE_REFS} referências")
    for index, ref in enumerate(refs):
        _check_ref(f"{where}.evidence_refs[{index}]", ref)
    if task["change_reason"] is not None:
        _check_enum(f"{where}.change_reason", task["change_reason"], CHANGE_REASONS)
    _check_timestamp(f"{where}.created_at", task["created_at"])
    _check_timestamp(f"{where}.started_at", task["started_at"], nullable=True)
    _check_timestamp(f"{where}.finished_at", task["finished_at"], nullable=True)

    status = task["status"]
    if status == "pending" and (task["started_at"] or task["finished_at"] or task["executor"]):
        _fail(where, "tarefa pendente não tem início, fim nem executor")
    if status == "active" and (not task["started_at"] or task["finished_at"] or not task["executor"]):
        _fail(where, "tarefa ativa exige início e executor, sem fim")
    if status == "done" and (not task["started_at"] or not task["finished_at"] or not refs):
        _fail(where, "tarefa concluída exige início, fim e referência de evidência")
    if status == "dropped" and (
        not task["finished_at"] or task["change_reason"] not in DROP_REASONS or not refs
    ):
        _fail(where, "tarefa descartada exige fim, motivo e referência")


def _validate_scope(scope: Any, kind: str) -> None:
    _exact_keys("scope", scope, SCOPE_KEYS)
    _check_absolute_path("scope.front_root", scope["front_root"])
    if kind == "goal":
        for field in ("front", "card_id", "board_path", "thread_root"):
            if scope[field] is not None:
                _fail(f"scope.{field}", "goal avulso não tem card, board, thread nem frente")
        return
    if not isinstance(scope["front"], str) or not FRONT_RE.match(scope["front"]):
        _fail("scope.front", "slug da frente inválido")
    if not isinstance(scope["card_id"], str) or not CARD_RE.match(scope["card_id"]):
        _fail("scope.card_id", "esperado T-NNN")
    _check_absolute_path("scope.board_path", scope["board_path"])
    _check_absolute_path("scope.thread_root", scope["thread_root"])


def _validate_plan(plan: Any, kind: str, task_count: int) -> None:
    _exact_keys("plan", plan, PLAN_KEYS)
    _check_ref("plan.source_ref", plan["source_ref"], nullable=kind == "goal")
    _check_ref("plan.approval_ref", plan["approval_ref"], nullable=kind == "goal")
    if not isinstance(plan["seed_sha256"], str) or not SESSION_KEY_RE.match(plan["seed_sha256"]):
        _fail("plan.seed_sha256", "deve ter 64 hexadecimais minúsculos")
    count, weight = plan["baseline_count"], plan["baseline_weight"]
    if not _is_int(count) or not 1 <= count <= task_count:
        _fail("plan.baseline_count", "inteiro entre 1 e o total de tarefas")
    if not _is_int(weight) or weight < count:
        _fail("plan.baseline_weight", "inteiro não menor que baseline_count")
    _check_timestamp("plan.registered_at", plan["registered_at"])


def validate_ledger(raw: object) -> dict:
    """Valida o ledger v1 sem biblioteca de JSON Schema; devolve o próprio objeto."""
    if not isinstance(raw, dict):
        _fail("ledger", "deve ser um objeto JSON")
    version = raw.get("schema_version")
    if not _is_int(version) or version != SCHEMA_VERSION:
        raise LedgerValidationError(
            f"schema_version desconhecida ({version!r}); este programa só lê a versão {SCHEMA_VERSION}",
            code="versao-desconhecida",
        )
    _exact_keys("ledger", raw, LEDGER_KEYS)
    _check_run_id(raw["run_id"])
    if not _is_int(raw["revision"]) or raw["revision"] < 1:
        _fail("revision", "inteiro maior ou igual a 1")
    _check_enum("kind", raw["kind"], KINDS)
    kind = raw["kind"]
    _validate_scope(raw["scope"], kind)
    _exact_keys("owner", raw["owner"], OWNER_KEYS)
    _check_enum("owner.host", raw["owner"]["host"], HOSTS)
    _check_session_key("owner.session_key", raw["owner"]["session_key"])
    _check_enum("lifecycle", raw["lifecycle"], LIFECYCLES)
    _check_enum("activity", raw["activity"], CARD_ACTIVITIES if kind == "card" else GOAL_ACTIVITIES)
    tasks = raw["tasks"]
    if not isinstance(tasks, list) or len(tasks) > MAX_TASKS:
        _fail("tasks", f"lista de até {MAX_TASKS} tarefas")
    seen = set()
    for index, task in enumerate(tasks):
        _validate_task(f"tasks[{index}]", task)
        if task["id"] in seen:
            _fail(f"tasks[{index}].id", f"ID repetido: {task['id']}")
        seen.add(task["id"])
    if raw["plan"] is None:
        if tasks:
            _fail("tasks", "há tarefas sem plano registrado")
    else:
        _validate_plan(raw["plan"], kind, len(tasks))
    closure = raw["closure"]
    if closure is not None:
        _exact_keys("closure", closure, CLOSURE_KEYS)
        _check_enum("closure.outcome", closure["outcome"], OUTCOMES)
        _check_ref("closure.evidence_ref", closure["evidence_ref"])
        _check_timestamp("closure.closed_at", closure["closed_at"])
    if (raw["lifecycle"] == "closed") != (closure is not None):
        _fail("closure", "lifecycle closed e closure devem coexistir")
    _check_timestamp("created_at", raw["created_at"])
    _check_timestamp("updated_at", raw["updated_at"])
    return raw


def _validate_binding_fields(raw: object) -> None:
    if not isinstance(raw, dict):
        _fail("binding", "deve ser um objeto JSON")
    version = raw.get("schema_version")
    if not _is_int(version) or version != SCHEMA_VERSION:
        raise LedgerValidationError(
            f"schema_version desconhecida ({version!r}); este programa só lê a versão {SCHEMA_VERSION}",
            code="versao-desconhecida",
        )
    _exact_keys("binding", raw, BINDING_KEYS)
    _check_session_key("session_key", raw["session_key"])
    _check_enum("host", raw["host"], BINDING_HOSTS)
    _check_absolute_path("ledger_path", raw["ledger_path"])
    _check_run_id(raw["run_id"])
    if not _is_int(raw["calls_without_plan"]) or raw["calls_without_plan"] < 0:
        _fail("calls_without_plan", "inteiro maior ou igual a 0")
    if not isinstance(raw["nudged"], bool):
        _fail("nudged", "deve ser booleano")
    events = raw["recent_event_ids"]
    if not isinstance(events, list) or len(events) > MAX_RECENT_EVENTS:
        _fail("recent_event_ids", f"lista de até {MAX_RECENT_EVENTS} identificadores")
    for index, event_id in enumerate(events):
        _check_text(f"recent_event_ids[{index}]", event_id, MAX_EVENT_ID_CHARS)


def validate_binding(raw: object) -> dict:
    """Valida o binding de sessão v1; devolve o próprio objeto. Falha com `binding-invalido`."""
    try:
        _validate_binding_fields(raw)
    except LedgerValidationError as error:
        code = error.code if error.code == "versao-desconhecida" else "binding-invalido"
        raise LedgerValidationError(str(error), code=code) from error
    return raw


# ── Cálculo e projeção ──────────────────────────────────────────────────────


def calculate_progress(ledger: dict) -> dict:
    """Contagem e percentual dos passos; função pura, sem leitura de board."""
    tasks = ledger["tasks"]
    counted = [task for task in tasks if task["status"] != "dropped"]
    done = [task for task in counted if task["status"] == "done"]
    total = sum(SIZE_WEIGHTS[task["size"]] for task in counted)
    finished = sum(SIZE_WEIGHTS[task["size"]] for task in done)
    open_tasks = len(counted) - len(done)
    percent = None
    if ledger["plan"] is None:
        state = "sem-plano"
    elif total == 0:
        state = "sem-passos-ativos"
    else:
        # Meio para cima em inteiros: round() de Python arredonda x,5 para o par.
        percent = (200 * finished + total) // (2 * total)
        if open_tasks:
            percent = min(percent, 99)
        state = "em-andamento" if open_tasks else "completo"
    return {
        "state": state,
        "percent": percent,
        "tasks_total": len(counted),
        "tasks_done": len(done),
        "tasks_active": sum(1 for task in counted if task["status"] == "active"),
        "tasks_pending": sum(1 for task in counted if task["status"] == "pending"),
        "tasks_dropped": len(tasks) - len(counted),
        "weight_total": total,
        "weight_done": finished,
    }


def _phase(key: Optional[str], source: str, marker: Optional[str], warning: Optional[str]) -> dict:
    label = PHASE_LABELS[key] if key else "fase indisponível"
    return {"key": key, "label": label, "source": source, "marker": marker, "warning": warning}


def project_phase(ledger: dict, board_state: Optional[dict]) -> dict:
    """Fase exibida. O board manda; a atividade do ledger só desempata o que o board não distingue."""
    activity = ledger["activity"]
    if ledger["kind"] == "goal":
        return _phase(activity, "activity", None, None)
    marker = board_state.get("marker") if isinstance(board_state, dict) else None
    if not isinstance(board_state, dict) or board_state.get("state") != "ok" or marker not in BOARD_MARKERS:
        code = board_state.get("code") if isinstance(board_state, dict) else None
        reason = CODE_RE.sub("", str(code or "nao-consultado"))
        return _phase(None, "indisponivel", None, f"board indisponível ({reason}); fase não confirmada")
    if marker == "~":
        if activity == "ready" and any(task["status"] in ("active", "done") for task in ledger["tasks"]):
            # Passo iniciado ou concluído é execução em curso; a projeção corrige também ledgers já gravados.
            return _phase("implementation", "board", marker, None)
        if activity in EXECUTING_ACTIVITIES:
            return _phase(activity, "board", marker, None)
        # O card do board descreve `[~]` como "aprovado e em implementação".
        return _phase(
            "implementation", "board", marker, f"atividade '{activity}' incompatível com [~]; vale o board"
        )
    if marker == ">" and activity == "gate":
        return _phase("gate", "activity", marker, None)
    key = BOARD_PHASES[marker]
    allowed = (key, "gate") if marker == ">" else (key,)
    warning = None if activity in allowed else f"atividade '{activity}' diverge do board; vale o board"
    return _phase(key, "board", marker, warning)


def build_view(ledger: dict, board_state: Optional[dict], ledger_path: Optional[str] = None) -> dict:
    """Projeção única consumida por `show` e `watch`; nada é recalculado nas vistas."""
    progress = calculate_progress(ledger)
    tasks = ledger["tasks"]

    def brief(task: dict) -> dict:
        return {"id": task["id"], "title": task["title"], "size": task["size"], "executor": task["executor"]}

    plan = ledger["plan"]
    return {
        "ledger_path": ledger_path,
        "run_id": ledger["run_id"],
        "kind": ledger["kind"],
        "card_id": ledger["scope"]["card_id"],
        "revision": ledger["revision"],
        "lifecycle": ledger["lifecycle"],
        "closure": ledger["closure"],
        "owner": dict(ledger["owner"]),
        "activity": ledger["activity"],
        "phase": project_phase(ledger, board_state),
        "progress": progress,
        "plan": None
        if plan is None
        else {"baseline_count": plan["baseline_count"], "current_count": progress["tasks_total"]},
        "active": [brief(task) for task in tasks if task["status"] == "active"],
        "next": [brief(task) for task in tasks if task["status"] == "pending"],
        "tasks": [{**brief(task), "status": task["status"]} for task in tasks],
        "updated_at": ledger["updated_at"],
    }


def _clean(text: str) -> str:
    """Defesa final na saída: nada que mexa no terminal chega ao usuário."""
    return "".join("?" if has_terminal_controls(char) else char for char in text)


def _view_name(view: dict) -> str:
    return view["card_id"] if view["kind"] == "card" else f"goal {view['run_id'][:8]}"


def _lifecycle_text(view: dict) -> Optional[str]:
    if view["lifecycle"] == "paused":
        return "pausado"
    if view["lifecycle"] == "closed":
        if view["closure"]["outcome"] == "cancelled":
            return "execução cancelada"
        return "execução encerrada pelo Manager"
    return None


def _progress_text(progress: dict, verbose: bool) -> str:
    if progress["state"] == "sem-plano":
        return "sem plano registrado"
    if progress["state"] == "sem-passos-ativos":
        return "sem passos ativos"
    counts = f"{progress['tasks_done']}/{progress['tasks_total']}"
    if verbose:
        return f"{counts} passos concluídos · {progress['percent']}% do plano"
    return f"{counts} · {progress['percent']}%"


def _executor_text(executor: Optional[dict]) -> str:
    return f" · {executor['role']}/{executor['label']}" if executor else ""


def render_text(view: dict) -> str:
    head = [_view_name(view), view["phase"]["label"], _progress_text(view["progress"], verbose=True)]
    lifecycle = _lifecycle_text(view)
    if lifecycle:
        head.append(lifecycle)
    lines = [" · ".join(head)]
    if view["active"]:
        running = (f"{task['id']} — {task['title']}{_executor_text(task['executor'])}" for task in view["active"])
        lines.append("Em execução: " + "; ".join(running))
    pending = view["next"]
    if pending:
        preview = "; ".join(f"{task['id']} — {task['title']}" for task in pending[:NEXT_PREVIEW])
        more = len(pending) - NEXT_PREVIEW
        lines.append("Próximos: " + preview + (f" (+{more})" if more > 0 else ""))
    plan = view["plan"]
    if plan and plan["baseline_count"] != plan["current_count"]:
        lines.append(f"Plano: {plan['baseline_count']} → {plan['current_count']} passos")
    if view["kind"] == "card" and view["progress"]["state"] == "completo" and view["phase"]["key"] != "done":
        lines.append("Plano completo; o card só fecha quando o dono validar.")
    if view["phase"]["warning"]:
        lines.append("Aviso: " + view["phase"]["warning"])
    lines.append(f"Atualizado: {view['updated_at']} · revisão {view['revision']}")
    return "\n".join(_clean(line) for line in lines)


def render_segment(view: dict) -> str:
    parts = [_view_name(view), view["phase"]["label"], _progress_text(view["progress"], verbose=False)]
    lifecycle = _lifecycle_text(view)
    if lifecycle:
        parts.append(lifecycle)
    return _clean("◎ " + " · ".join(parts))


# ── Operações (puras) ───────────────────────────────────────────────────────


def _check_input(check: Callable[..., None], *args: Any, **kwargs: Any) -> None:
    try:
        check(*args, **kwargs)
    except LedgerValidationError as error:
        raise InputError(str(error), code="entrada-invalida") from error


def _find_task(ledger: dict, task_id: Any) -> dict:
    for task in ledger["tasks"]:
        if task["id"] == task_id:
            return task
    raise InputError(f"tarefa inexistente: {task_id!r}", code="tarefa-inexistente")


def _append_ref(task: dict, ref: str) -> None:
    if task["evidence_refs"] and task["evidence_refs"][-1] == ref:
        return
    if len(task["evidence_refs"]) >= MAX_EVIDENCE_REFS:
        raise InputError(f"tarefa {task['id']} já tem {MAX_EVIDENCE_REFS} referências", code="limite-referencias")
    task["evidence_refs"].append(ref)


def _repeats(task: dict, status: str, ref: str) -> bool:
    return task["status"] == status and bool(task["evidence_refs"]) and task["evidence_refs"][-1] == ref


def _normalize_new_tasks(raw_tasks: Any, where: str) -> list:
    if not isinstance(raw_tasks, list) or not raw_tasks:
        raise InputError(f"{where}: lista de tarefas não vazia esperada", code="entrada-invalida")
    if len(raw_tasks) > MAX_TASKS:
        raise InputError(f"{where}: no máximo {MAX_TASKS} tarefas", code="limite-tarefas")
    tasks, seen = [], set()
    for index, raw in enumerate(raw_tasks):
        label = f"{where}[{index}]"
        if not isinstance(raw, dict):
            raise InputError(f"{label}: deve ser um objeto", code="entrada-invalida")
        extra = sorted(str(key) for key in raw if key not in ("id", "title", "size", "acceptance_ref"))
        if extra:
            raise InputError(f"{label}: campos não permitidos: {', '.join(extra)}", code="entrada-invalida")
        for field in ("id", "title", "size"):
            if field not in raw:
                raise InputError(f"{label}: campo ausente: {field}", code="entrada-invalida")
        task = {
            "id": raw["id"],
            "title": raw["title"],
            "size": raw["size"],
            "acceptance_ref": raw.get("acceptance_ref"),
        }
        if not isinstance(task["id"], str) or not TASK_ID_RE.match(task["id"]):
            raise InputError(f"{label}.id: use letras ASCII, dígitos, _ e -, até 32", code="entrada-invalida")
        _check_input(_check_text, f"{label}.title", task["title"], MAX_TITLE_CHARS)
        _check_input(_check_enum, f"{label}.size", task["size"], tuple(SIZE_WEIGHTS))
        _check_input(_check_ref, f"{label}.acceptance_ref", task["acceptance_ref"], True)
        if task["id"] in seen:
            raise InputError(f"{label}.id: ID repetido na entrada: {task['id']}", code="id-repetido")
        seen.add(task["id"])
        tasks.append(task)
    return tasks


def _pending_task(new: dict, now: str, reason: Optional[str], refs: list) -> dict:
    return {
        "id": new["id"],
        "title": new["title"],
        "size": new["size"],
        "status": "pending",
        "acceptance_ref": new["acceptance_ref"],
        "executor": None,
        "evidence_refs": list(refs),
        "change_reason": reason,
        "created_at": now,
        "started_at": None,
        "finished_at": None,
    }


def _object_input(operation: dict, allowed: tuple) -> dict:
    data = operation.get("input")
    if not isinstance(data, dict):
        raise InputError("entrada deve ser um objeto JSON", code="entrada-invalida")
    extra = sorted(str(key) for key in data if key not in allowed)
    if extra:
        raise InputError(f"campos não permitidos na entrada: {', '.join(extra)}", code="entrada-invalida")
    return data


def _require_board_marker(board_state: Any, expected: str, purpose: str) -> None:
    if not isinstance(board_state, dict) or board_state.get("state") != "ok":
        code = CODE_RE.sub("", str(board_state.get("code") if isinstance(board_state, dict) else "nao-consultado"))
        raise UnavailableError(f"board indisponível ({code}); não dá para {purpose}", code="board-indisponivel")
    if board_state.get("marker") != expected:
        raise InputError(
            f"o board marca [{board_state.get('marker')}]; {purpose} exige [{expected}]", code="board-incompativel"
        )


def _op_plan(ledger: dict, operation: dict, now: str) -> None:
    data = _object_input(operation, ("source_ref", "approval_ref", "tasks"))
    kind = ledger["kind"]
    seed_refs = {}
    for field in ("source_ref", "approval_ref"):
        value = data.get(field)
        if value is None and kind == "card":
            raise InputError(f"{field} é obrigatório em card", code="entrada-invalida")
        _check_input(_check_ref, field, value, kind == "goal")
        seed_refs[field] = value
    tasks = _normalize_new_tasks(data.get("tasks"), "tasks")
    seed = {"source_ref": seed_refs["source_ref"], "approval_ref": seed_refs["approval_ref"], "tasks": tasks}
    digest = hashlib.sha256(
        json.dumps(seed, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    if ledger["plan"] is not None:
        if ledger["plan"]["seed_sha256"] == digest:
            return
        raise InputError("plano já registrado com outra semente; use add, drop ou reopen", code="plano-divergente")
    if kind == "card":
        _require_board_marker(operation.get("board_state"), "~", "registrar a semente do plano")
    ledger["plan"] = {
        "source_ref": seed["source_ref"],
        "approval_ref": seed["approval_ref"],
        "seed_sha256": digest,
        "baseline_count": len(tasks),
        "baseline_weight": sum(SIZE_WEIGHTS[task["size"]] for task in tasks),
        "registered_at": now,
    }
    ledger["tasks"] = [_pending_task(task, now, None, []) for task in tasks]


def _op_add(ledger: dict, operation: dict, now: str) -> None:
    if ledger["plan"] is None:
        raise InputError("registre o plano (plan) antes de acrescentar passos", code="sem-plano")
    data = _object_input(operation, ("reason", "evidence_ref", "tasks"))
    if data.get("reason") not in ADD_REASONS:
        raise InputError("reason deve ser " + "|".join(ADD_REASONS), code="entrada-invalida")
    _check_input(_check_ref, "evidence_ref", data.get("evidence_ref"))
    new_tasks = _normalize_new_tasks(data.get("tasks"), "tasks")
    existing = {task["id"]: task for task in ledger["tasks"]}
    for new in new_tasks:
        current = existing.get(new["id"])
        if current is None:
            ledger["tasks"].append(_pending_task(new, now, data["reason"], [data["evidence_ref"]]))
        elif current["status"] == "dropped" or any(
            current[field] != new[field] for field in ("title", "size", "acceptance_ref")
        ):
            raise InputError(
                f"o ID {new['id']} já existe com outro conteúdo ou foi descartado; use um ID novo",
                code="id-conflitante",
            )


def _op_start(ledger: dict, operation: dict, now: str) -> None:
    task = _find_task(ledger, operation.get("task"))
    executor = operation.get("executor")
    _check_input(_check_executor, "executor", executor)
    if task["status"] == "active" and task["executor"] == executor:
        return
    if task["status"] != "pending":
        raise InputError(
            f"start exige tarefa pendente; {task['id']} está {task['status']}", code="transicao-invalida"
        )
    task["status"], task["executor"], task["started_at"] = "active", dict(executor), now


def _op_done(ledger: dict, operation: dict, now: str) -> None:
    task = _find_task(ledger, operation.get("task"))
    ref = operation.get("evidence_ref")
    _check_input(_check_ref, "evidence_ref", ref)
    if _repeats(task, "done", ref):
        return
    if task["status"] != "active":
        raise InputError(
            f"done exige tarefa ativa (use start antes); {task['id']} está {task['status']}", code="transicao-invalida"
        )
    _append_ref(task, ref)
    task["status"], task["finished_at"] = "done", now


def _op_drop(ledger: dict, operation: dict, now: str) -> None:
    task = _find_task(ledger, operation.get("task"))
    reason, ref = operation.get("reason"), operation.get("evidence_ref")
    _check_input(_check_enum, "reason", reason, DROP_REASONS)
    _check_input(_check_ref, "evidence_ref", ref)
    if _repeats(task, "dropped", ref) and task["change_reason"] == reason:
        return
    if task["status"] not in ("pending", "active"):
        raise InputError(
            f"drop exige tarefa pendente ou ativa; {task['id']} está {task['status']}", code="transicao-invalida"
        )
    _append_ref(task, ref)
    task["status"], task["change_reason"], task["finished_at"] = "dropped", reason, now


def _op_reopen(ledger: dict, operation: dict, now: str) -> None:
    task = _find_task(ledger, operation.get("task"))
    ref = operation.get("evidence_ref")
    _check_input(_check_ref, "evidence_ref", ref)
    if _repeats(task, "pending", ref) and task["change_reason"] == "reopened":
        return
    if task["status"] != "done":
        raise InputError(
            f"reopen exige tarefa concluída; {task['id']} está {task['status']}", code="transicao-invalida"
        )
    _append_ref(task, ref)
    task["status"], task["change_reason"] = "pending", "reopened"
    task["executor"] = task["started_at"] = task["finished_at"] = None


def _op_phase(ledger: dict, operation: dict, now: str) -> None:
    allowed = CARD_ACTIVITIES if ledger["kind"] == "card" else GOAL_ACTIVITIES
    _check_input(_check_enum, "value", operation.get("value"), allowed)
    ledger["activity"] = operation["value"]


def _op_pause(ledger: dict, operation: dict, now: str) -> None:
    ledger["lifecycle"] = "paused"


def _op_resume(ledger: dict, operation: dict, now: str) -> None:
    ledger["lifecycle"] = "active"


def _op_close(ledger: dict, operation: dict, now: str) -> None:
    outcome, ref = operation.get("outcome"), operation.get("evidence_ref")
    _check_input(_check_enum, "outcome", outcome, OUTCOMES)
    _check_input(_check_ref, "evidence_ref", ref)
    closure = ledger["closure"]
    if closure is not None:
        if closure["outcome"] == outcome and closure["evidence_ref"] == ref:
            return
        raise InputError("ledger já encerrado com outro desfecho", code="transicao-invalida")
    if ledger["kind"] == "card" and outcome == "reported_complete":
        _require_board_marker(operation.get("board_state"), "x", "encerrar como concluído")
    ledger["lifecycle"] = "closed"
    ledger["closure"] = {"outcome": outcome, "evidence_ref": ref, "closed_at": now}


CLAIM_SAME_KEY_MESSAGE = (
    "claim não transfere nada com a mesma chave: --session-key é a NOVA chave do novo dono e "
    "--expected-owner é a chave anterior do dono atual"
)


def _op_claim(ledger: dict, operation: dict, now: str) -> None:
    host, expected = operation.get("host"), operation.get("expected_owner")
    _check_input(_check_enum, "host", host, HOSTS)
    _check_input(_check_session_key, "expected_owner", expected)
    new_key = operation.get("new_session_key")
    _check_input(_check_session_key, "session_key", new_key)
    if new_key == expected:
        raise InputError(CLAIM_SAME_KEY_MESSAGE, code="claim-sem-transferencia")
    owner = ledger["owner"]
    if owner["session_key"] == new_key:
        owner["host"] = host
        return
    if owner["session_key"] != expected:
        raise ConflictError(
            "dono atual diferente do esperado; releia o ledger", code="dono-divergente", revision=ledger["revision"]
        )
    ledger["owner"] = {"host": host, "session_key": new_key}


_OPERATIONS = {
    "plan": _op_plan,
    "add": _op_add,
    "start": _op_start,
    "done": _op_done,
    "drop": _op_drop,
    "reopen": _op_reopen,
    "phase": _op_phase,
    "pause": _op_pause,
    "resume": _op_resume,
    "close": _op_close,
    "claim": _op_claim,
}
_ALLOWED_WHEN_PAUSED = ("pause", "resume", "close", "claim")


def apply_operation(ledger: dict, operation: dict, now: str) -> dict:
    """Aplica uma operação sobre uma cópia, sem acessar disco; repetição exata devolve o ledger igual."""
    handler = _OPERATIONS.get(operation.get("op")) if isinstance(operation, dict) else None
    if handler is None:
        raise InputError(f"operação desconhecida: {operation!r}"[:200], code="operacao-desconhecida")
    _check_input(_check_timestamp, "now", now)
    op = operation["op"]
    if ledger["lifecycle"] == "closed" and op != "close":
        raise InputError("ledger encerrado: não aceita novas operações", code="ledger-encerrado")
    if ledger["lifecycle"] == "paused" and op not in _ALLOWED_WHEN_PAUSED:
        raise InputError("execução pausada: use resume antes de alterar passos", code="ledger-pausado")
    updated = copy.deepcopy(ledger)
    handler(updated, operation, now)
    if updated == ledger:
        return updated
    updated["revision"] = ledger["revision"] + 1
    updated["updated_at"] = now
    try:
        validate_ledger(updated)
    except LedgerValidationError as error:
        raise InputError(f"a operação produziria estado inválido: {error}", code="estado-invalido") from error
    return updated


# ── Persistência ────────────────────────────────────────────────────────────


def _reject_duplicate_keys(pairs: list) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"chave repetida: {key}")
        result[key] = value
    return result


def _reject_constant(name: str) -> Any:
    raise ValueError(f"constante não permitida: {name}")


def parse_json(data: bytes) -> Any:
    try:
        return json.loads(
            data.decode("utf-8"), object_pairs_hook=_reject_duplicate_keys, parse_constant=_reject_constant
        )
    except (UnicodeDecodeError, ValueError, RecursionError) as error:
        raise ValueError(str(error)[:160]) from error


def read_ledger(path: Path) -> dict:
    """Leitor estrito: abre só para leitura, não cria diretório, lock nem arquivo."""
    try:
        with open(path, "rb") as handle:
            data = handle.read(MAX_LEDGER_BYTES + 1)
    except FileNotFoundError as error:
        raise UnavailableError(f"ledger inexistente: {path}", code="ledger-ausente") from error
    except OSError as error:
        raise UnavailableError(
            f"ledger ilegível: {path} ({error.strerror or error})", code="ledger-ilegivel"
        ) from error
    if len(data) > MAX_LEDGER_BYTES:
        raise UnavailableError(f"ledger acima de {MAX_LEDGER_BYTES} bytes: {path}", code="ledger-grande")
    try:
        raw = parse_json(data)
        return validate_ledger(raw)
    except LedgerValidationError as error:
        raise UnavailableError(f"ledger inválido: {path}: {error}", code=error.code) from error
    except ValueError as error:
        raise UnavailableError(f"ledger com JSON inválido: {path}: {error}", code="ledger-invalido") from error


def lock_path_for(path: Path) -> Path:
    """Lock do ledger (ou do binding) em `v1/locks/`. Só existe para o layout padrão: fora dele é recusado."""
    if storage_root_of(path, LEDGER_DIRECTORIES + (BINDING_DIRECTORY,)) is None:
        raise UnavailableError(
            f"ledger fora do layout <frente>/.orq/progress/v1/<cards|goals>/<arquivo>.json: {path}",
            code="destino-fora-do-layout",
        )
    return path.parent.parent / "locks" / f"{path.parent.name}-{path.stem}.lock"


@contextlib.contextmanager
def ledger_lock(path: Path, wait_seconds: float = LOCK_WAIT_SECONDS) -> Iterator[None]:
    """Lock de kernel por ledger, com espera limitada. Só mutações o criam."""
    if fcntl is None and msvcrt is None:
        raise UnavailableError("plataforma sem lock de kernel (fcntl/msvcrt)", code="lock-indisponivel")
    lock_path = lock_path_for(path)
    try:
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        handle = lock_path.open("a+b")
    except OSError as error:
        raise UnavailableError(
            f"lock inacessível: {lock_path} ({error.strerror or error})", code="lock-indisponivel"
        ) from error
    deadline = time.monotonic() + wait_seconds
    try:
        while True:
            try:
                if fcntl is not None:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                else:
                    handle.seek(0)
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                break
            except OSError as error:
                if error.errno not in (errno.EACCES, errno.EAGAIN, errno.EDEADLK):
                    raise UnavailableError(
                        f"lock falhou: {error.strerror or error}", code="lock-indisponivel"
                    ) from error
                if time.monotonic() >= deadline:
                    raise UnavailableError(
                        f"lock ocupado por mais de {wait_seconds:g}s: {lock_path}", code="lock-ocupado"
                    ) from error
                time.sleep(LOCK_POLL_SECONDS)
        yield
    finally:
        try:
            if fcntl is not None:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
            else:
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        except OSError:
            pass
        handle.close()


def temporary_prefix(name: str) -> str:
    return f".{name}."


def write_ledger(path: Path, ledger: dict, git_root: Optional[Path] = None) -> None:
    """Temporário no mesmo diretório, flush, fsync e `os.replace`: o leitor vê o antes ou o depois.

    Também grava o binding de sessão, pelo mesmo caminho atômico e com a mesma sonda do nome reservado.
    Com `git_root` (checkout Git; root e `path` canônicos), o Git é consultado sobre o nome EXATO do
    temporário reservado, antes de o JSON ser escrito nele; não ignorado, o temporário é removido e
    nada é gravado. Qualquer falha ou interrupção remove o temporário e preserva o ledger anterior.
    """
    data = (json.dumps(ledger, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if len(data) > MAX_LEDGER_BYTES:
        raise InputError(f"o ledger passaria de {MAX_LEDGER_BYTES} bytes", code="ledger-grande")
    temporary: Optional[Path] = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=path.parent, prefix=temporary_prefix(path.name), suffix=TEMPORARY_SUFFIX, delete=False
        ) as handle:
            temporary = Path(handle.name)
            if git_root is not None:
                _ensure_ignored(git_root, [temporary.relative_to(git_root).as_posix()])
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException as error:  # limpeza em qualquer falha, Ctrl-C inclusive
        if temporary is not None:
            try:
                temporary.unlink()
            except OSError:
                pass
        if isinstance(error, OSError):
            raise UnavailableError(
                f"falha ao gravar {path}: {error.strerror or error}", code="persistencia-falhou"
            ) from error
        raise
    try:  # a durabilidade do rename depende do diretório; best effort fora do POSIX
        descriptor = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    except OSError:
        pass


def _mutation_result(path: Path, ledger: dict, session_key: str, changed: bool) -> dict:
    return {
        "ok": True,
        "run_id": ledger["run_id"],
        "ledger_path": str(path),
        "revision": ledger["revision"],
        "session_key": session_key,
        "changed": changed,
    }


def ensure_inside(root: Path, target: Path, what: str) -> None:
    """Recusa `target` cujo realpath (symlinks resolvidos, mesmo dangling) escapa de realpath(root)."""
    base = os.path.realpath(root)
    resolved = os.path.realpath(target)
    try:
        inside = os.path.commonpath([base, resolved]) == base
    except ValueError:
        inside = False
    if not inside:
        raise UnavailableError(f"{what} resolve para fora do root: {resolved}", code="destino-fora-do-root")


def storage_root_of(path: Path, directories: tuple = LEDGER_DIRECTORIES) -> Optional[Path]:
    """Root da frente quando `path` segue o layout `<root>/.orq/progress/v1/<directories>/<arquivo>.json`."""
    parent = path.parent
    layout = (path.suffix == ".json", parent.name in directories, parent.parent.name == "v1")
    if all(layout) and parent.parent.parent.name == "progress" and parent.parent.parent.parent.name == ".orq":
        return parent.parent.parent.parent.parent
    return None


def resolve_ledger_target(
    path: Path, root: Optional[Path] = None, directories: tuple = LEDGER_DIRECTORIES
) -> Tuple[Path, Path]:
    """Caminho canônico do ledger e root da frente, provando layout e contenção. Só mutações passam aqui.

    O caminho é canonicalizado (realpath) ANTES de inferir layout, root e lock, e todo acesso usa o
    resultado: dois apelidos do mesmo ledger caem no mesmo lock. Fora do layout padrão, recusa.
    `directories` escolhe o subdiretório de `v1/`: o `bind` resolve assim o arquivo de binding, e um
    binding nunca passa por aqui como ledger (nem o contrário).
    """
    noun = "binding" if directories == (BINDING_DIRECTORY,) else "ledger"
    if root is not None:
        ensure_inside(root, path, noun)
    canonical = Path(os.path.realpath(path))
    inferred = storage_root_of(canonical, directories)
    if inferred is None or (root is not None and inferred != Path(os.path.realpath(root))):
        raise UnavailableError(
            f"{noun} fora do layout <frente>/.orq/progress/v1/<{'|'.join(directories)}>/<arquivo>.json: {canonical}",
            code="destino-fora-do-layout",
        )
    ensure_inside(inferred, lock_path_for(canonical), "lock")
    return canonical, inferred


def commit_mutation(
    path: Path,
    session_key: str,
    expected_revision: Optional[int],
    operation: dict,
    now: str,
    root: Optional[Path] = None,
) -> Tuple[dict, dict]:
    """Leitura, validação, comparação e gravação sob o mesmo lock. Devolve (recibo, ledger confirmado).

    `expected_revision` ausente: a mutação vale sobre o estado atual, ainda sob lock, troca atômica
    e verificação de dono. Presente e divergente: conflito, sem gravar. O caminho é canonicalizado e
    tem de estar no layout padrão de `root` (ou do root inferido); `ledger_path` devolvido é o canônico.
    """
    _check_input(_check_session_key, "session_key", session_key)
    if expected_revision is not None and (not _is_int(expected_revision) or expected_revision < 1):
        raise InputError("expect-revision deve ser um inteiro maior ou igual a 1", code="entrada-invalida")
    if operation.get("op") == "claim" and operation.get("expected_owner") == session_key:
        raise InputError(CLAIM_SAME_KEY_MESSAGE, code="claim-sem-transferencia")
    path, root = resolve_ledger_target(path, root)
    if not path.is_file():  # antes do lock: mutar ledger inexistente não deixa diretório de lock
        raise UnavailableError(f"ledger inexistente: {path}", code="ledger-ausente")
    in_repository = ensure_destinations_ignored(root, path)
    with ledger_lock(path):
        current = read_ledger(path)
        if expected_revision is not None and current["revision"] != expected_revision:
            raise ConflictError(
                f"revisão esperada {expected_revision}, atual {current['revision']}; releia o ledger",
                code="revisao-divergente",
                revision=current["revision"],
            )
        is_claim = operation.get("op") == "claim"
        if not is_claim and current["owner"]["session_key"] != session_key:
            raise ConflictError(
                "session_key não é a do dono do ledger; releia e, se for o caso, faça claim",
                code="dono-divergente",
                revision=current["revision"],
            )
        if is_claim:
            operation = {**operation, "new_session_key": session_key}
        updated = apply_operation(current, operation, now)
        changed = updated != current
        if changed:
            write_ledger(path, updated, git_root=root if in_repository else None)
        return _mutation_result(path, updated, session_key, changed), updated


def mutate_ledger(
    path: Path,
    session_key: str,
    expected_revision: Optional[int],
    operation: dict,
    now: str,
    root: Optional[Path] = None,
) -> dict:
    """`commit_mutation` só com o recibo, sem a vista compacta (que o CLI acrescenta fora do lock)."""
    return commit_mutation(path, session_key, expected_revision, operation, now, root)[0]


# ── Armazenamento e begin ───────────────────────────────────────────────────


def _git_environment() -> dict:
    environment = os.environ.copy()
    for inherited in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE"):
        environment.pop(inherited, None)
    return environment


def _git(root: Path, *args: str, stdin: Optional[bytes] = None) -> Optional[subprocess.CompletedProcess]:
    try:
        return subprocess.run(
            ["git", "-C", str(root), *args],
            input=stdin,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=GIT_TIMEOUT_SECONDS,
            env=_git_environment(),
        )
    except (subprocess.TimeoutExpired, OSError):
        return None


def _has_git_metadata(path: Path) -> bool:
    current = os.path.abspath(path)
    while True:
        if os.path.lexists(os.path.join(current, ".git")):
            return True
        parent = os.path.dirname(current)
        if parent == current:
            return False
        current = parent


def _inside_git_repository(root: Path) -> bool:
    """True em checkout Git comprovado; False só se não há metadado Git algum no caminho."""
    inside = _git(root, "rev-parse", "--is-inside-work-tree")
    if inside is not None and inside.returncode == 0:
        if inside.stdout.strip() == b"true":
            return True
        raise UnavailableError(
            "o root está dentro do diretório Git, não da árvore de trabalho", code="git-inconsistente"
        )
    if _has_git_metadata(root):
        raise UnavailableError("Git indisponível ou inconsistente neste checkout", code="git-indisponivel")
    return False


def destination_probes(root: Path, ledger: Path) -> list:
    """Destinos de escrita desta operação, relativos ao root: `.gitignore`, ledger, lock e um temporário.

    `root` e `ledger` são canônicos. O temporário daqui só tem o prefixo e o sufixo reais de `write_ledger`
    (o trecho do meio é fictício): é pré-checagem barata, antes de criar qualquer coisa. A prova vale para o
    nome reservado de verdade, consultado dentro de `write_ledger`.
    """
    temporary = ledger.parent / f"{temporary_prefix(ledger.name)}{TEMPORARY_PROBE_TOKEN}{TEMPORARY_SUFFIX}"
    destinations = (ledger.parent.parent.parent / ".gitignore", ledger, lock_path_for(ledger), temporary)
    return [destination.relative_to(root).as_posix() for destination in destinations]


def _ensure_ignored(root: Path, probes: list) -> None:
    """O Git ignora todos os caminhos de `probes` (relativos ao root)? Senão, exit 4 sem alterar o `.gitignore`."""
    payload = ("\0".join(probes) + "\0").encode("utf-8")
    result = _git(root, "check-ignore", "--no-index", "-z", "--stdin", stdin=payload)
    if result is None or result.returncode not in (0, 1):
        raise UnavailableError("não foi possível confirmar que o armazenamento é ignorado", code="git-indisponivel")
    ignored = set(os.fsdecode(result.stdout).split("\0"))
    missing = [probe for probe in probes if probe not in ignored]
    if missing:
        raise UnavailableError(
            "o .gitignore de .orq/progress não ignora o destino de escrita: "
            + ", ".join(missing)
            + "; não vou alterá-lo",
            code="armazenamento-nao-ignorado",
        )


def ensure_destinations_ignored(root: Path, ledger: Path) -> bool:
    """Antes de gravar: o Git ignora os destinos desta operação? Devolve se `root` é checkout Git."""
    in_repository = _inside_git_repository(root)
    if in_repository:
        _ensure_ignored(root, destination_probes(root, ledger))
    return in_repository


def ensure_storage(root: Path, ledger: Path) -> bool:
    """Prepara `<root>/.orq/progress/` para gravar `ledger` (canônico), sem escrever antes de provar tudo.

    Primeiro só lê: arquivo versionado no destino e a contenção de TODOS os componentes (`.orq`,
    `progress`, `v1`, `cards`, `goals`, `sessions`, `locks`), existentes ou não. Só então cria `progress` e, se
    faltar, o `.gitignore` de `*`. A pré-checagem de cobertura do Git vem antes de criar `v1`. Devolve se
    `root` é checkout Git, para `write_ledger` provar o temporário real. `ledger` pode ser o arquivo de
    binding de uma sessão: as sondas são as mesmas (`.gitignore`, o arquivo, o lock e um temporário).
    """
    canonical_root = Path(os.path.realpath(root))
    in_repository = _inside_git_repository(root)
    if in_repository:
        tracked = _git(root, "ls-files", "-z", "--", ".orq/progress")
        if tracked is None or tracked.returncode != 0:
            raise UnavailableError(
                "não foi possível listar os arquivos versionados do destino", code="git-indisponivel"
            )
        if tracked.stdout:
            raise UnavailableError(
                "há arquivo versionado em .orq/progress; o medidor não inicializa sobre ele", code="destino-versionado"
            )
    progress = root / ".orq" / "progress"
    storage = progress / "v1"
    components = (root / ".orq", progress, storage, *(storage / name for name in STORAGE_DIRECTORIES))
    try:
        for directory in components:  # realpath não estrito: pega symlink preexistente, mesmo dangling
            ensure_inside(root, directory, str(directory.relative_to(root)))
        progress.mkdir(parents=True, exist_ok=True)
        ensure_inside(root, progress, ".orq/progress")
        try:
            descriptor = os.open(progress / ".gitignore", os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        except FileExistsError:
            pass  # um .gitignore existente é preservado; a checagem abaixo diz se ele basta
        else:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                handle.write("*\n")
        if in_repository:
            _ensure_ignored(canonical_root, destination_probes(canonical_root, ledger))
        for directory in components[2:]:
            directory.mkdir(exist_ok=True)
            ensure_inside(root, directory, str(directory.relative_to(root)))
    except OSError as error:
        raise UnavailableError(
            f"não foi possível preparar {progress}: {error.strerror or error}", code="persistencia-falhou"
        ) from error
    return in_repository


def storage_dir(root: Path) -> Path:
    return root / ".orq" / "progress" / "v1"


def ledger_path_for(root: Path, card: Optional[str] = None, run: Optional[str] = None) -> Path:
    if card is not None:
        if not CARD_RE.match(card):
            raise InputError("--card deve ser T-NNN", code="entrada-invalida")
        return storage_dir(root) / "cards" / f"{card}.json"
    try:
        canonical = str(uuid.UUID(str(run)))
    except ValueError as error:
        raise InputError("--run deve ser um UUID", code="entrada-invalida") from error
    if canonical != run:
        raise InputError("--run deve estar em forma canônica minúscula", code="entrada-invalida")
    return storage_dir(root) / "goals" / f"{canonical}.json"


def query_board_state(card_id: str, board_path: str) -> dict:
    """Estado do card no board canônico, pelo parser único do `kanban-status.sh`."""
    script = Path(__file__).resolve().parent / "kanban-status.sh"
    if not script.is_file():
        return {"state": "erro", "code": "kanban-status-ausente"}
    try:
        result = subprocess.run(
            ["sh", str(script), "--card-state", card_id, "--board-path", board_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=SUBPROCESS_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return {"state": "erro", "code": "board-timeout"}
    except OSError:
        return {"state": "erro", "code": "sh-indisponivel"}
    try:
        data = json.loads(result.stdout.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return {"state": "erro", "code": "resposta-invalida"}
    if not isinstance(data, dict):
        return {"state": "erro", "code": "resposta-invalida"}
    if data.get("state") == "ok" and data.get("card") == card_id and data.get("marker") in BOARD_MARKERS:
        return {"state": "ok", "card": card_id, "marker": data["marker"]}
    return {"state": "erro", "code": CODE_RE.sub("", str(data.get("code") or "desconhecido")) or "desconhecido"}


def ledger_board_state(ledger: dict) -> Optional[dict]:
    if ledger["kind"] != "card":
        return None
    scope = ledger["scope"]
    return query_board_state(scope["card_id"], scope["board_path"])


def attach_view(receipt: dict, ledger: dict) -> dict:
    """Acrescenta ao recibo a vista compacta: a linha do `show --format segment`, pela mesma projeção.

    Roda DEPOIS da gravação e fora do lock, sobre o ledger que acabou de ser confirmado (`view_revision`
    é a revisão projetada). A escrita já aconteceu: se a projeção falhar, o recibo segue `ok` com `view`
    nulo e `view_error`, e a gravação nunca é repetida nem dada como falha por causa da vista.
    """
    try:
        view = build_view(ledger, ledger_board_state(ledger), receipt["ledger_path"])
        line = render_segment(view)
    except Exception as error:  # a escrita já está confirmada; o erro vai no recibo, não é engolido
        if isinstance(error, ProgressError):
            detail = {"code": error.code, "message": str(error)}
        else:
            detail = {"code": "projecao-falhou", "message": f"{type(error).__name__}: {error}"}
        detail["message"] = _clean(detail["message"])[:200]
        return {**receipt, "view": None, "view_revision": None, "view_error": detail}
    return {**receipt, "view": line, "view_revision": view["revision"]}


def new_ledger(kind: str, host: str, session_key: str, scope: dict, now: str, run_id: str) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "revision": 1,
        "kind": kind,
        "scope": scope,
        "owner": {"host": host, "session_key": session_key},
        "lifecycle": "active",
        "activity": "ready" if kind == "card" else "planning",
        "plan": None,
        "tasks": [],
        "closure": None,
        "created_at": now,
        "updated_at": now,
    }


def commit_begin(
    kind: str,
    root: Path,
    host: str,
    session_key: Optional[str],
    now: str,
    board: Optional[str] = None,
    thread_root: Optional[str] = None,
    card: Optional[str] = None,
    front: Optional[str] = None,
) -> Tuple[dict, dict]:
    """Cria o ledger de um card (reutilizável ao retomar) ou de um goal avulso (um UUID por execução).

    Devolve (recibo, ledger): o criado agora ou o existente que a retomada reaproveitou.
    """
    if not root.is_absolute() or not root.is_dir():
        raise InputError("--root deve ser um diretório absoluto existente", code="entrada-invalida")
    _check_input(_check_enum, "host", host, HOSTS)
    if session_key is not None:
        _check_input(_check_session_key, "session_key", session_key)
    card_fields = {"board": board, "thread-root": thread_root, "card": card, "front": front}
    if kind == "goal":
        extra = sorted(name for name, value in card_fields.items() if value is not None)
        if extra:
            raise InputError(
                "goal avulso não aceita " + ", ".join(f"--{name}" for name in extra), code="entrada-invalida"
            )
        scope = {
            "front_root": os.path.realpath(root),
            "front": None,
            "card_id": None,
            "board_path": None,
            "thread_root": None,
        }
    else:
        missing = sorted(name for name, value in card_fields.items() if value is None)
        if missing:
            raise InputError(
                "begin --kind card exige " + ", ".join(f"--{name}" for name in missing), code="entrada-invalida"
            )
        scope = {
            "front_root": os.path.realpath(root),
            "front": front,
            "card_id": card,
            "board_path": board,
            "thread_root": thread_root,
        }
        _check_input(_validate_scope, scope, "card")
        board_state = query_board_state(card, board)
        if board_state["state"] != "ok":
            raise UnavailableError(
                f"board não confirma o card {card} ({board_state['code']})", code="board-indisponivel"
            )
    run_id = str(uuid.uuid4())
    path = ledger_path_for(root, card=card) if kind == "card" else ledger_path_for(root, run=run_id)
    path, canonical_root = resolve_ledger_target(path, root)
    in_repository = ensure_storage(root, path)
    key = session_key or secrets.token_hex(32)
    with ledger_lock(path):
        if path.exists():
            existing = read_ledger(path)
            if existing["lifecycle"] == "closed":
                raise InputError(
                    "o ledger deste card está encerrado e não é reutilizável", code="ledger-encerrado"
                )
            if existing["scope"] != scope:
                raise InputError(
                    "o ledger existente tem outro escopo (frente, board ou thread); confira o resolver",
                    code="escopo-divergente",
                )
            if existing["owner"]["session_key"] != key:
                raise ConflictError(
                    "o ledger já tem outro dono; informe a session_key do dono ou faça claim",
                    code="dono-divergente",
                    revision=existing["revision"],
                )
            return _mutation_result(path, existing, key, False), existing
        ledger = new_ledger(kind, host, key, scope, now, run_id)
        write_ledger(path, ledger, git_root=canonical_root if in_repository else None)
        return _mutation_result(path, ledger, key, True), ledger


def begin_ledger(
    kind: str,
    root: Path,
    host: str,
    session_key: Optional[str],
    now: str,
    board: Optional[str] = None,
    thread_root: Optional[str] = None,
    card: Optional[str] = None,
    front: Optional[str] = None,
) -> dict:
    """`commit_begin` só com o recibo, sem a vista compacta (que o CLI acrescenta fora do lock)."""
    return commit_begin(kind, root, host, session_key, now, board, thread_root, card, front)[0]


# ── Vínculo de sessão (bind) ────────────────────────────────────────────────


def derive_session_key(host: str, session_id: str) -> str:
    """Chave opaca da sessão nativa: sha256(host + NUL + session_id). O ID bruto nunca é persistido."""
    _check_input(_check_enum, "host", host, BINDING_HOSTS)
    if (
        not isinstance(session_id, str)
        or not session_id
        or len(session_id) > MAX_SESSION_ID_CHARS
        or has_terminal_controls(session_id)
    ):
        raise InputError(
            f"--session-id deve ser o ID nativo da sessão: texto de 1 a {MAX_SESSION_ID_CHARS} caracteres, "
            "sem controles de terminal",
            code="entrada-invalida",
        )
    return hashlib.sha256(f"{host}\0{session_id}".encode("utf-8")).hexdigest()


def new_binding(host: str, session_key: str, ledger_path: str, run_id: str) -> dict:
    """Binding recém-criado: contadores zerados, nenhum lembrete dado, nenhum evento visto."""
    return {
        "schema_version": SCHEMA_VERSION,
        "session_key": session_key,
        "host": host,
        "ledger_path": ledger_path,
        "run_id": run_id,
        "calls_without_plan": 0,
        "nudged": False,
        "recent_event_ids": [],
    }


def binding_path_for(root: Path, session_key: str) -> Path:
    return storage_dir(root) / BINDING_DIRECTORY / f"{session_key}.json"


def read_binding(path: Path) -> dict:
    """Leitor estrito do binding: só abre para leitura. O nome do arquivo tem de ser a `session_key` dele."""
    try:
        with open(path, "rb") as handle:
            data = handle.read(MAX_BINDING_BYTES + 1)
    except FileNotFoundError as error:
        raise UnavailableError(f"binding inexistente: {path}", code="binding-ausente") from error
    except OSError as error:
        raise UnavailableError(
            f"binding ilegível: {path} ({error.strerror or error})", code="binding-ilegivel"
        ) from error
    if len(data) > MAX_BINDING_BYTES:
        raise UnavailableError(f"binding acima de {MAX_BINDING_BYTES} bytes: {path}", code="binding-grande")
    try:
        raw = validate_binding(parse_json(data))
    except LedgerValidationError as error:
        raise UnavailableError(f"binding inválido: {path}: {error}", code=error.code) from error
    except ValueError as error:
        raise UnavailableError(f"binding com JSON inválido: {path}: {error}", code="binding-invalido") from error
    if raw["session_key"] != path.stem:
        raise UnavailableError(f"binding com session_key diferente do nome do arquivo: {path}", code="binding-invalido")
    return raw


def _binding_receipt(path: Path, binding: dict, changed: bool) -> dict:
    return {
        "ok": True,
        "session_key": binding["session_key"],
        "host": binding["host"],
        "run_id": binding["run_id"],
        "ledger_path": binding["ledger_path"],
        "binding_path": str(path),
        "changed": changed,
    }


def _resolve_session_file(front_root: Path, expected: Path) -> Path:
    """Caminho canônico de um arquivo de `sessions/`, provando contenção, layout e o nome exato esperado."""
    target, _ = resolve_ledger_target(expected, front_root, (BINDING_DIRECTORY,))
    if target != expected:  # symlink para outro arquivo de `sessions/`
        raise UnavailableError(f"binding resolve para outro arquivo: {target}", code="destino-fora-do-layout")
    return target


def _resolve_binding(front_root: Path, session_key: str) -> Path:
    return _resolve_session_file(front_root, binding_path_for(front_root, session_key))


def bind_session(
    ledger: Path,
    host: str,
    session_id: Optional[str],
    root: Optional[Path] = None,
    native_key: Optional[str] = None,
) -> dict:
    """Liga a sessão nativa do host a um ledger, em `<front_root>/.orq/progress/v1/sessions/<session_key>.json`.

    A sessão vem de `session_id` (o ID nativo, de que só o hash é gravado) OU de `native_key` (a chave
    nativa já derivada, que o hook informa; o Manager não conhece o ID bruto). Exatamente um dos dois.
    A chave nativa NÃO é a de dono do ledger (`--session-key` das mutações): o `bind` não a lê nem muda.

    Não transfere ownership e não toca no ledger. As garantias são as do `begin`: realpath e contenção do
    ledger, do binding e dos locks, Git ignorando o destino REAL (o binding e o temporário dele, pelo mesmo
    `write_ledger`) e lock do binding. Só lê até provar tudo isso. Mesmo ledger: idempotente, os contadores
    ficam; outro ledger substitui o binding daquela sessão e os zera. Binding corrompido é refeito; de
    versão desconhecida, não: outro host pode ter um plugin mais novo na mesma frente.
    """
    if (session_id is None) == (native_key is None):
        raise InputError("informe exatamente um de --session-id e --native-key", code="entrada-invalida")
    if native_key is None:
        key = derive_session_key(host, session_id)
    else:
        _check_input(_check_enum, "host", host, BINDING_HOSTS)
        _check_input(_check_session_key, "native_key", native_key)
        key = native_key
    ledger, front_root = resolve_ledger_target(ledger, root)
    run_id = read_ledger(ledger)["run_id"]
    target = _resolve_binding(front_root, key)
    in_repository = ensure_storage(front_root, target)
    binding = new_binding(host, key, str(ledger), run_id)
    with ledger_lock(target):
        try:
            existing = read_binding(target)
        except UnavailableError as error:
            if error.code not in ("binding-ausente", "binding-invalido", "binding-grande"):
                raise
            existing = None
        if existing is not None and all(existing[field] == binding[field] for field in ("ledger_path", "run_id")):
            return _binding_receipt(target, existing, False)
        write_ledger(target, binding, git_root=front_root if in_repository else None)
    return _binding_receipt(target, binding, True)


# ── Hooks consultivos (SessionStart e PostToolUse) ──────────────────────────
#
# Só lembram: nunca bloqueiam, negam, interrompem nem decidem. Não abrem o transcript e não leem
# `tool_input`, `tool_response` nem o texto do prompt: só session_id, cwd, o nome do evento, a fonte do
# SessionStart, `agent_id` e os identificadores da chamada. O adaptador `progress-hook.py` só liga o
# stdin a `handle_hook` e garante o exit 0.


def hook_host(env: Mapping[str, str]) -> Optional[str]:
    """Host que disparou o hook, pelo ambiente nativo (mesmo critério do context-guard).

    `PLUGIN_ROOT` é do Codex; `CLAUDE_PLUGIN_ROOT`, do Claude. Nenhum dos dois: host desconhecido.
    """
    if env.get("PLUGIN_ROOT"):
        return "codex"
    if env.get("CLAUDE_PLUGIN_ROOT"):
        return "claude"
    return None


def _session_fronts(cwd: str) -> list:
    """Raízes com `.orq/progress/v1/sessions/`, da mais próxima do cwd para cima. Só consulta o disco, não abre nada."""
    current = os.path.realpath(cwd)
    fronts = []
    for _ in range(MAX_FRONT_ANCESTORS):
        if os.path.isdir(os.path.join(current, ".orq", "progress", "v1", BINDING_DIRECTORY)):
            fronts.append(Path(current))
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return fronts


def _hook_output(event_name: str, text: str) -> dict:
    return {"hookSpecificOutput": {"hookEventName": event_name, "additionalContext": text}}


def _session_start_text(host: str, session_key: str) -> str:
    return (
        f"Medidor de progresso — chave da sessão nativa ({host}): {session_key}. Havendo medidor ativo nesta "
        f"frente, vincule-a com `bind --host {host} --native-key <essa chave>`; as mutações seguem com a "
        "chave de dono gravada na thread."
    )


def _nudge_text(calls: int) -> str:
    return (
        f"Medidor de progresso (aviso consultivo): {calls} chamadas de ferramenta nesta execução e nenhum plano "
        "registrado. Se o plano já foi aprovado, registre-o com `plan`; em planejamento ou gate do dono, "
        "ignore este aviso."
    )


def _event_fingerprint(host: str, event: dict) -> Optional[str]:
    """Hash da identidade da chamada, para não contar duas vezes a mesma entrega. Os IDs brutos não são guardados.

    Claude: (session_id, tool_use_id, evento). Codex: (session_id, turn_id, tool_use_id, evento). Faltando
    algum identificador, devolve None e a contagem passa a ser por entrega de evento.
    """
    names = ("session_id", "tool_use_id") if host == "claude" else ("session_id", "turn_id", "tool_use_id")
    parts = [event.get(name) for name in names] + [event.get("hook_event_name")]
    if not all(isinstance(part, str) and part for part in parts):
        return None
    try:
        return hashlib.sha256("\0".join([host, *parts]).encode("utf-8")).hexdigest()
    except UnicodeEncodeError:
        return None


def _counts_toward_nudge(ledger: dict) -> bool:
    """Execução ativa, ainda sem plano e que já admite execução: card só em `[~]`; goal, sempre."""
    if ledger["lifecycle"] != "active" or ledger["plan"] is not None:
        return False
    if ledger["kind"] == "goal":
        return True
    board_state = ledger_board_state(ledger)
    return isinstance(board_state, dict) and board_state.get("state") == "ok" and board_state.get("marker") == "~"


def _locate_binding(fronts: list, session_key: str, host: str) -> Tuple[Optional[Tuple[Path, Path, dict]], Optional[str]]:
    """Binding da sessão na frente mais próxima que o tem: (achado, problema).

    `problema` é o `code` do primeiro defeito que não seja a simples ausência do arquivo (ilegível, inválido,
    versão desconhecida, fora da frente...), ou None. Quem chama distingue "sem vínculo" de "vínculo ruim".
    """
    problem = None
    for front in fronts:
        try:
            target = _resolve_binding(front, session_key)
            binding = read_binding(target)
        except UnavailableError as error:
            if error.code != "binding-ausente" and problem is None:
                problem = error.code
            continue
        if binding["host"] == host:
            return (front, target, binding), None
        problem = problem or "binding-invalido"
    return None, problem


def _read_bound_ledger(front: Path, binding: dict) -> dict:
    """Ledger ligado a um binding, lido só depois de provar que o `ledger_path` ainda é um ledger DESTA frente.

    O caminho vem de um arquivo que pode ter sido adulterado, e o alvo pode ter virado symlink depois do
    `bind`. Por isso, antes de abrir qualquer coisa: realpath, contenção na frente onde o binding foi achado
    e layout `<frente>/.orq/progress/v1/<cards|goals>/<arquivo>.json` (`resolve_ledger_target`). O que se abre
    é o caminho canônico, e a conferência de `run_id` continua valendo. Falha: `UnavailableError`, sem abrir
    o arquivo (o hook cala; a statusline mostra a indisponibilidade com o código).
    """
    path, _ = resolve_ledger_target(Path(binding["ledger_path"]), front)
    ledger = read_ledger(path)
    if ledger["run_id"] != binding["run_id"]:
        raise UnavailableError("o binding é de outra execução do ledger", code="vinculo-obsoleto")
    return ledger


def _announce_native_key(front: Path, session_key: str, host: str) -> Optional[dict]:
    """Primeiro PostToolUse de uma sessão principal sem binding: informa a chave nativa UMA vez.

    A sessão que roda o `begin` já passou do SessionStart (`sessions/` não existia): sem isto ela nunca
    saberia a chave. O marcador `sessions/.anunciada-<chave>.json` impede a repetição e segue as garantias
    do binding: contenção, Git ignorando o destino real, lock e escrita atômica. Se a gravação falhar,
    silêncio (e tenta de novo no próximo evento): sem o marcador, anunciar repetiria.
    """
    marker = _resolve_session_file(front, binding_path_for(front, f".anunciada-{session_key}"))
    if os.path.lexists(marker):
        return None
    in_repository = ensure_destinations_ignored(front, marker)
    with ledger_lock(marker, wait_seconds=HOOK_LOCK_WAIT_SECONDS):
        if os.path.lexists(marker):
            return None
        write_ledger(marker, {"schema_version": SCHEMA_VERSION, "announced": True}, git_root=front if in_repository else None)
    return _hook_output("PostToolUse", _session_start_text(host, session_key))


def _count_tool_event(front: Path, target: Path, binding: dict, fingerprint: Optional[str]) -> Optional[dict]:
    """Conta um evento elegível sob o lock do binding e, no quarto, emite o lembrete (uma vez só)."""
    in_repository = ensure_destinations_ignored(front, target)
    with ledger_lock(target, wait_seconds=HOOK_LOCK_WAIT_SECONDS):
        current = read_binding(target)
        if current["nudged"] or (current["run_id"], current["ledger_path"]) != (binding["run_id"], binding["ledger_path"]):
            return None
        if fingerprint is not None and fingerprint in current["recent_event_ids"]:
            return None
        # A consulta feita antes do lock já pode estar velha: um `plan`, uma pausa ou o board mudaram nesse
        # intervalo. A elegibilidade é conferida de novo AQUI, com o estado de agora, logo antes de contar e de
        # emitir. Não toma o lock do ledger: o escritor troca o arquivo por `os.replace`, então a leitura é um
        # snapshot consistente, e um `plan` que termina depois dela é ordenado depois do lembrete (legítimo).
        # Assim também não existe ordem de locks (binding -> ledger) a manter: nenhum outro código a usa.
        if not _counts_toward_nudge(_read_bound_ledger(front, current)):
            return None
        recent = current["recent_event_ids"] + ([fingerprint] if fingerprint is not None else [])
        updated = {**current, "calls_without_plan": current["calls_without_plan"] + 1}
        updated["recent_event_ids"] = recent[-MAX_RECENT_EVENTS:]
        nudge = updated["calls_without_plan"] >= NUDGE_AFTER_CALLS
        if nudge:
            updated["nudged"] = True
        write_ledger(target, updated, git_root=front if in_repository else None)
    return _hook_output("PostToolUse", _nudge_text(updated["calls_without_plan"])) if nudge else None


def handle_hook(event: Any, env: Mapping[str, str]) -> Optional[dict]:
    """Resposta consultiva a um evento de hook, ou None. Falha esperada (disco, lock, Git, JSON) vira None.

    SessionStart informa a chave da sessão nativa, sem gravar nada. PostToolUse conta eventos de uma
    sessão vinculada cujo ledger está ativo e sem plano; no quarto emite UM lembrete e grava `nudged`. Na
    sessão principal ainda sem binding (nem arquivo ruim no lugar), o primeiro PostToolUse anuncia a chave
    nativa uma vez. Chamada de subagente (`agent_id`), host ou evento desconhecidos não fazem nada.
    """
    host = hook_host(env)
    if host is None or not isinstance(event, dict):
        return None
    name = event.get("hook_event_name")
    cwd = event.get("cwd")
    if name not in ("SessionStart", "PostToolUse") or not isinstance(cwd, str) or "\0" in cwd or not os.path.isabs(cwd):
        return None
    try:
        session_key = derive_session_key(host, event.get("session_id"))
        fronts = _session_fronts(cwd)
        if not fronts:
            return None
        if name == "SessionStart":
            if event.get("source") not in SESSION_START_SOURCES:
                return None
            return _hook_output(name, _session_start_text(host, session_key))
        if event.get("agent_id") not in (None, ""):
            return None
        found, problem = _locate_binding(fronts, session_key, host)
        if found is None:
            return None if problem else _announce_native_key(fronts[0], session_key, host)
        if found[2]["nudged"]:
            return None
        front, target, binding = found
        if not _counts_toward_nudge(_read_bound_ledger(front, binding)):  # filtro barato: sem lock, sem Git
            return None
        fingerprint = _event_fingerprint(host, event)
        if fingerprint is not None and fingerprint in binding["recent_event_ids"]:
            return None
        return _count_tool_event(front, target, binding, fingerprint)
    except (ProgressError, OSError, ValueError):
        return None


# ── Statusline do Claude ────────────────────────────────────────────────────
#
# Vista pura: lê o binding da sessão nativa, carrega o ledger ligado a ele e imprime a MESMA linha do
# `show --format segment`. Nunca escolhe "o ledger mais recente" nem adivinha por horário ou título: sem
# `session_id` ou sem binding não há segmento. Não escreve nada e nunca faz a barra falhar.


def _payload_directories(payload: dict) -> list:
    """Diretórios absolutos que o JSON da statusline do Claude informa, na ordem: cwd, current_dir, project_dir."""
    workspace = payload.get("workspace")
    workspace = workspace if isinstance(workspace, dict) else {}
    candidates = [payload.get("cwd"), workspace.get("current_dir"), workspace.get("project_dir")]
    directories = []
    for candidate in candidates:
        if isinstance(candidate, str) and "\0" not in candidate and os.path.isabs(candidate) and candidate not in directories:
            directories.append(candidate)
    return directories


def _unavailable_segment(code: str) -> str:
    return f"◎ medidor indisponível ({CODE_RE.sub('', code) or 'erro'})"


def statusline_segment(payload: Any) -> Optional[str]:
    """Segmento do medidor para a statusline do Claude, ou None quando não há o que mostrar.

    Sem `session_id`, sem medidor na frente ou sem binding desta sessão: None. Binding ou ledger que existem
    mas não servem: uma indisponibilidade curta, nunca um percentual inventado.
    """
    if not isinstance(payload, dict):
        return None
    try:
        session_key = derive_session_key("claude", payload.get("session_id"))
    except InputError:
        return None
    fronts = []
    for directory in _payload_directories(payload):
        fronts.extend(front for front in _session_fronts(directory) if front not in fronts)
    if not fronts:
        return None
    found, problem = _locate_binding(fronts, session_key, "claude")
    if found is None:
        return _unavailable_segment(problem) if problem else None
    front, _, binding = found
    try:
        ledger = _read_bound_ledger(front, binding)
        return render_segment(build_view(ledger, ledger_board_state(ledger), binding["ledger_path"]))
    except ProgressError as error:
        return _unavailable_segment(error.code)
    except Exception:  # a barra nunca falha: a causa vira indisponibilidade, não silêncio
        return _unavailable_segment("erro")


# ── CLI ─────────────────────────────────────────────────────────────────────


def _absolute(label: str, value: Optional[str]) -> Path:
    if value is None or "\0" in value or not os.path.isabs(value):
        raise InputError(f"{label} deve ser um caminho absoluto", code="entrada-invalida")
    return Path(value)


def _selected_ledger(args: argparse.Namespace) -> Path:
    if args.ledger is not None:
        if args.root or args.card or args.run:
            raise InputError("use --ledger OU --root com --card/--run, não os dois", code="entrada-invalida")
        return _absolute("--ledger", args.ledger)
    if not args.root or bool(args.card) == bool(args.run):
        raise InputError("informe --ledger ou --root com exatamente um de --card/--run", code="entrada-invalida")
    return ledger_path_for(_absolute("--root", args.root), card=args.card, run=args.run)


def _read_input(args: argparse.Namespace) -> Any:
    if args.input != "-":
        raise InputError("--input aceita somente '-' (JSON pela entrada padrão)", code="entrada-invalida")
    data = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
    if len(data) > MAX_INPUT_BYTES:
        raise InputError(f"entrada acima de {MAX_INPUT_BYTES} bytes", code="entrada-grande")
    try:
        return parse_json(data)
    except ValueError as error:
        raise InputError(f"JSON de entrada inválido: {error}", code="entrada-invalida") from error


def _print_json(payload: dict, readable: bool = False) -> None:
    """Uma linha JSON. `readable` mantém os acentos (a `view` do recibo é para ler); controles vão escapados.

    Se o stdout não codifica o texto, cai para ASCII escapado: a escrita do recibo já aconteceu, e um
    traceback agora faria o Manager repetir uma marcação que foi gravada.
    """
    text = json.dumps(payload, ensure_ascii=True, separators=(",", ":"))
    if readable:
        candidate = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        candidate = "".join(f"\\u{ord(char):04x}" if has_terminal_controls(char) else char for char in candidate)
        try:
            candidate.encode(sys.stdout.encoding or "utf-8")
            text = candidate
        except (UnicodeEncodeError, LookupError):
            pass
    print(text)


def _emit_error(error: ProgressError) -> None:
    payload = {"ok": False, "exit": error.exit_code, "code": error.code, "message": str(error)}
    if isinstance(error, ConflictError) and error.revision is not None:
        payload["revision"] = error.revision
    print(json.dumps(payload, ensure_ascii=True, separators=(",", ":")), file=sys.stderr)


def _operation_from_args(args: argparse.Namespace) -> dict:
    name = args.command
    if name in ("plan", "add"):
        return {"op": name, "input": _read_input(args)}
    if name == "start":
        return {
            "op": name,
            "task": args.task,
            "executor": {"host": args.executor_host, "role": args.executor_role, "label": args.executor_label},
        }
    if name in ("done", "reopen"):
        return {"op": name, "task": args.task, "evidence_ref": args.evidence_ref}
    if name == "drop":
        return {"op": name, "task": args.task, "reason": args.reason, "evidence_ref": args.evidence_ref}
    if name == "phase":
        return {"op": name, "value": args.value}
    if name == "close":
        return {"op": name, "outcome": args.outcome, "evidence_ref": args.evidence_ref}
    if name == "claim":
        return {"op": name, "host": args.host, "expected_owner": args.expected_owner}
    return {"op": name}  # pause, resume


def _needs_board(args: argparse.Namespace) -> bool:
    return args.command == "plan" or (args.command == "close" and args.outcome == "reported_complete")


def cmd_begin(args: argparse.Namespace) -> int:
    receipt, ledger = commit_begin(
        args.kind,
        _absolute("--root", args.root),
        args.host,
        args.session_key,
        utc_now(),
        board=None if args.board is None else str(_absolute("--board", args.board)),
        thread_root=None if args.thread_root is None else str(_absolute("--thread-root", args.thread_root)),
        card=args.card,
        front=args.front,
    )
    _print_json(attach_view(receipt, ledger), readable=True)
    return 0


def cmd_bind(args: argparse.Namespace) -> int:
    root = _absolute("--root", args.root) if args.root else None
    receipt = bind_session(_selected_ledger(args), args.host, args.session_id, root, native_key=args.native_key)
    _print_json(receipt, readable=True)
    return 0


def cmd_statusline(args: argparse.Namespace) -> int:
    """Consultivo: sempre sai 0 e só imprime o segmento (ou nada). Lê o JSON da statusline do Claude no stdin."""
    global GIT_TIMEOUT_SECONDS, SUBPROCESS_TIMEOUT_SECONDS
    previous = (GIT_TIMEOUT_SECONDS, SUBPROCESS_TIMEOUT_SECONDS)
    GIT_TIMEOUT_SECONDS = SUBPROCESS_TIMEOUT_SECONDS = STATUSLINE_SUBPROCESS_SECONDS  # a barra não espera um Git travado
    try:
        if args.input == "-":
            data = sys.stdin.buffer.read(MAX_STATUSLINE_BYTES + 1)
            if len(data) <= MAX_STATUSLINE_BYTES:
                segment = statusline_segment(parse_json(data))
                if segment:
                    print(segment)
    except Exception:  # entrada que não é JSON, stdout fechado, qualquer defeito: a barra segue sem o segmento
        pass
    finally:
        GIT_TIMEOUT_SECONDS, SUBPROCESS_TIMEOUT_SECONDS = previous
    return 0


def cmd_mutation(args: argparse.Namespace) -> int:
    path, root = resolve_ledger_target(
        _selected_ledger(args), _absolute("--root", args.root) if args.root else None
    )
    operation = _operation_from_args(args)
    if _needs_board(args):
        # O escopo do ledger é imutável; ler antes do lock só localiza o board.
        scope = read_ledger(path)["scope"]
        if scope["card_id"] is not None:
            operation["board_state"] = query_board_state(scope["card_id"], scope["board_path"])
    receipt, ledger = commit_mutation(path, args.session_key, args.expect_revision, operation, utc_now(), root=root)
    _print_json(attach_view(receipt, ledger), readable=True)
    return 0


def _all_ledger_paths(root: Path) -> list:
    base = storage_dir(root)
    paths = []
    for name in ("cards", "goals"):
        try:
            paths.extend(sorted(path for path in (base / name).glob("*.json") if path.is_file()))
        except OSError:
            continue
    return paths


def _load_view(path: Path) -> dict:
    ledger = read_ledger(path)
    return build_view(ledger, ledger_board_state(ledger), os.path.realpath(path))


def cmd_show(args: argparse.Namespace) -> int:
    if args.all:
        if args.ledger or args.card or args.run or not args.root:
            raise InputError("show --all exige somente --root", code="entrada-invalida")
        if args.format == "segment":
            raise InputError("show --all aceita --format text|json", code="entrada-invalida")
        views, errors = [], []
        for path in _all_ledger_paths(_absolute("--root", args.root)):
            try:
                views.append(_load_view(path))
            except ProgressError as error:
                errors.append({"ledger_path": str(path), "code": error.code, "message": str(error)})
        if args.format == "json":
            _print_json({"root": args.root, "ledgers": views, "errors": errors})
        else:
            blocks = [render_text(view) for view in views]
            blocks.extend(_clean(f"indisponível: {item['ledger_path']} — {item['message']}") for item in errors)
            print("\n\n".join(blocks) if blocks else "Nenhum medidor de progresso nesta raiz.")
        return 4 if errors else 0
    view = _load_view(_selected_ledger(args))
    if args.format == "json":
        _print_json(view)
    elif args.format == "segment":
        print(render_segment(view))
    else:
        print(render_text(view))
    return 0


def _watch_frame(path: Path) -> str:
    try:
        return render_text(_load_view(path))
    except ProgressError as error:
        return _clean(f"indisponível: {error}")


def cmd_watch(args: argparse.Namespace) -> int:
    path = _selected_ledger(args)
    if not 0.1 <= args.interval <= 3600:
        raise InputError("--interval deve ficar entre 0,1 e 3600 segundos", code="entrada-invalida")
    if args.count < 0:
        raise InputError("--count não pode ser negativo", code="entrada-invalida")
    interactive = sys.stdout.isatty()
    previous, cycles = None, 0
    try:
        while True:
            frame = _watch_frame(path)
            if frame != previous:
                if interactive:
                    sys.stdout.write("\x1b[H\x1b[2J")
                sys.stdout.write(frame + "\n" + ("Ctrl-C encerra o acompanhamento.\n" if interactive else "\n"))
                sys.stdout.flush()
                previous = frame
            cycles += 1
            if args.count and cycles >= args.count:
                return 0
            time.sleep(args.interval)
    except KeyboardInterrupt:
        return 0


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        """Erro de uso no mesmo formato dos demais: uma linha JSON no stderr e exit 2."""
        _emit_error(InputError(message, code="uso-invalido"))
        raise SystemExit(2)


def _add_target(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--ledger", help="caminho absoluto do ledger")
    parser.add_argument("--root", help="front_root absoluto (com --card ou --run)")
    parser.add_argument("--card", help="T-NNN do ledger de card")
    parser.add_argument("--run", help="UUID do ledger de goal")


def _add_mutation_target(parser: argparse.ArgumentParser, key_help: Optional[str] = None) -> None:
    _add_target(parser)
    parser.add_argument(
        "--session-key", required=True, help=key_help or "chave de sessão do dono (64 hexadecimais)"
    )
    parser.add_argument("--expect-revision", type=int, help="opcional; divergente => exit 3 sem gravar")


def build_parser() -> argparse.ArgumentParser:
    root = _Parser(prog="progress.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = root.add_subparsers(dest="command", required=True, parser_class=_Parser)

    begin = commands.add_parser("begin", help="cria (ou retoma) o ledger de um card ou de um goal avulso")
    begin.add_argument("--kind", required=True, choices=KINDS)
    begin.add_argument("--root", required=True, help="front_root absoluto devolvido pelo resolver")
    begin.add_argument("--host", required=True, choices=HOSTS)
    begin.add_argument("--session-key", help="64 hexadecimais; ausente => o programa gera e devolve")
    begin.add_argument("--board", help="board canônico absoluto (card)")
    begin.add_argument("--thread-root", help="thread_root absoluto (card)")
    begin.add_argument("--card", help="T-NNN (card)")
    begin.add_argument("--front", help="slug da frente dona (card)")
    begin.set_defaults(handler=cmd_begin)

    bind = commands.add_parser("bind", help="liga a sessão nativa do host a um ledger (não transfere ownership)")
    _add_target(bind)
    bind.add_argument("--host", required=True, choices=BINDING_HOSTS)
    native = bind.add_mutually_exclusive_group(required=True)
    native.add_argument("--session-id", help="ID nativo da sessão no host; só o hash é gravado")
    native.add_argument(
        "--native-key",
        help="chave da sessão NATIVA (64 hexadecimais), a que o hook informa; NÃO é a chave de dono "
        "do ledger (a `--session-key` das mutações)",
    )
    bind.set_defaults(handler=cmd_bind)

    statusline = commands.add_parser(
        "statusline", help="segmento do medidor para a statusline do Claude (consultivo: sempre sai 0)"
    )
    statusline.add_argument("--host", required=True, choices=("claude",))
    statusline.add_argument("--input", required=True, help="'-' lê o JSON que a statusline recebe, pela entrada padrão")
    statusline.set_defaults(handler=cmd_statusline)

    claim = commands.add_parser("claim", help="transfere o ownership de forma explícita")
    _add_mutation_target(
        claim,
        key_help="NOVA chave do novo dono (64 hexadecimais); a chave anterior do dono atual vai em --expected-owner",
    )
    claim.add_argument("--host", required=True, choices=HOSTS, help="host do novo dono")
    claim.add_argument(
        "--expected-owner", required=True, help="session_key do dono atual (a anterior); diferente de --session-key"
    )
    claim.set_defaults(handler=cmd_mutation)

    for name, help_text in (("plan", "registra a semente do plano aprovado"), ("add", "acrescenta passos ao plano")):
        sub = commands.add_parser(name, help=help_text)
        _add_mutation_target(sub)
        sub.add_argument("--input", required=True, help="'-' lê o JSON da entrada padrão")
        sub.set_defaults(handler=cmd_mutation)

    start = commands.add_parser("start", help="pending -> active")
    _add_mutation_target(start)
    start.add_argument("--task", required=True)
    start.add_argument("--executor-host", required=True, choices=HOSTS)
    start.add_argument("--executor-role", required=True)
    start.add_argument("--executor-label", required=True)
    start.set_defaults(handler=cmd_mutation)

    for name, help_text in (
        ("done", "active -> done, com evidência"),
        ("reopen", "done -> pending, com evidência"),
    ):
        sub = commands.add_parser(name, help=help_text)
        _add_mutation_target(sub)
        sub.add_argument("--task", required=True)
        sub.add_argument("--evidence-ref", required=True)
        sub.set_defaults(handler=cmd_mutation)

    drop = commands.add_parser("drop", help="pending|active -> dropped, com motivo e referência")
    _add_mutation_target(drop)
    drop.add_argument("--task", required=True)
    drop.add_argument("--reason", required=True, choices=DROP_REASONS)
    drop.add_argument("--evidence-ref", required=True)
    drop.set_defaults(handler=cmd_mutation)

    phase = commands.add_parser("phase", help="declara a atividade (a fase exibida obedece ao board)")
    _add_mutation_target(phase)
    phase.add_argument("--value", required=True)
    phase.set_defaults(handler=cmd_mutation)

    for name, help_text in (("pause", "pausa a execução"), ("resume", "retoma a execução pausada")):
        sub = commands.add_parser(name, help=help_text)
        _add_mutation_target(sub)
        sub.set_defaults(handler=cmd_mutation)

    close = commands.add_parser("close", help="encerra o ledger")
    _add_mutation_target(close)
    close.add_argument("--outcome", required=True, choices=OUTCOMES)
    close.add_argument("--evidence-ref", required=True)
    close.set_defaults(handler=cmd_mutation)

    show = commands.add_parser("show", help="projeção somente leitura")
    _add_target(show)
    show.add_argument("--all", action="store_true", help="todos os ledgers de --root")
    show.add_argument("--format", choices=("text", "json", "segment"), default="text")
    show.set_defaults(handler=cmd_show)

    watch = commands.add_parser("watch", help="acompanha um ledger em terminal (somente leitura)")
    _add_target(watch)
    watch.add_argument("--interval", type=float, default=2.0, help="segundos entre leituras (0,1 a 3600)")
    watch.add_argument("--count", type=int, default=0, help="encerra após N leituras (testes e scripts)")
    watch.set_defaults(handler=cmd_watch)
    return root


def main(argv: Optional[list] = None) -> int:
    try:
        args = build_parser().parse_args(argv)
    except SystemExit as exit_request:
        return exit_request.code if isinstance(exit_request.code, int) else 2
    try:
        return args.handler(args)
    except ProgressError as error:
        _emit_error(error)
        return error.exit_code
    except OSError as error:
        _emit_error(UnavailableError(f"falha de E/S: {error.strerror or error}", code="io"))
        return 4
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
