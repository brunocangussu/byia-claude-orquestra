#!/usr/bin/env python3
"""Guardião preventivo da janela de contexto do Codex."""

from __future__ import annotations

from dataclasses import dataclass
import errno
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile
import time
from typing import BinaryIO, Mapping
import unicodedata

try:
    import fcntl
except ImportError:  # pragma: no cover - fallback para Windows
    fcntl = None


DEFAULT_TAIL_BYTES = 4 * 1024 * 1024
MAX_TAIL_BYTES = 32 * 1024 * 1024
STATE_LOCK_WAIT_SECONDS = 0.75
STATE_VERSION = 2
STATE_KEYS = (
    "state_version",
    "phase",
    "pre_alert_sent",
    "checkpoint_started",
    "checkpoint_verified",
    "recovery_required",
    "last_percent",
    "updated_at",
)


@dataclass(frozen=True)
class UsageSnapshot:
    """Uso do último request concluído contra a janela efetiva."""

    used_tokens: int
    context_window: int

    @property
    def percent(self) -> float:
        return self.used_tokens * 100.0 / self.context_window


@dataclass
class StateLock:
    path: Path
    handle: BinaryIO | None = None
    directory: bool = False


def _is_positive_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _read_tail_lines(path: Path, tail_bytes: int) -> list[bytes]:
    if tail_bytes <= 0:
        return []
    try:
        with path.open("rb") as handle:
            handle.seek(0, 2)
            size = handle.tell()
            start = max(0, size - tail_bytes)
            handle.seek(start)
            data = handle.read(tail_bytes)
    except OSError:
        return []

    lines = data.splitlines()
    if start > 0 and lines:
        lines = lines[1:]
    return lines


def read_latest_usage(
    path: Path,
    tail_bytes: int = DEFAULT_TAIL_BYTES,
) -> UsageSnapshot | None:
    """Lê o token_count completo mais recente sem carregar o transcript inteiro."""

    scan_bytes = tail_bytes
    max_scan_bytes = max(tail_bytes, MAX_TAIL_BYTES)
    while scan_bytes > 0:
        for raw_line in reversed(_read_tail_lines(path, scan_bytes)):
            if b'"token_count"' not in raw_line:
                continue
            try:
                event = json.loads(raw_line)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            if not isinstance(event, dict):
                continue
            payload = event.get("payload")
            if not isinstance(payload, dict) or payload.get("type") != "token_count":
                continue
            info = payload.get("info")
            if not isinstance(info, dict):
                continue
            usage = info.get("last_token_usage")
            if not isinstance(usage, dict):
                continue
            used_tokens = usage.get("total_tokens")
            context_window = info.get("model_context_window")
            if not _is_positive_int(used_tokens) or not _is_positive_int(context_window):
                continue
            return UsageSnapshot(
                used_tokens=used_tokens,
                context_window=context_window,
            )
        try:
            if path.stat().st_size <= scan_bytes or scan_bytes >= max_scan_bytes:
                return None
        except OSError:
            return None
        scan_bytes = min(scan_bytes * 2, max_scan_bytes)
    return None


def band_for(percent: float) -> str:
    if percent >= 70.0:
        return "emergency"
    if percent >= 60.0:
        return "checkpoint_required"
    if percent >= 55.0:
        return "pre_alert"
    return "normal"


def default_state() -> dict:
    return {
        "state_version": STATE_VERSION,
        "phase": "normal",
        "pre_alert_sent": False,
        "checkpoint_started": False,
        "checkpoint_verified": False,
        "recovery_required": False,
        "last_percent": None,
        "updated_at": None,
    }


def state_path(data_dir: Path, session_id: str) -> Path:
    digest = hashlib.sha256(session_id.encode("utf-8", errors="replace")).hexdigest()
    return data_dir / "context-guard" / f"{digest}.json"


def _state_lock_path(data_dir: Path, session_id: str) -> Path:
    return state_path(data_dir, session_id).with_suffix(".lock")


def _state_reset_path(data_dir: Path, session_id: str) -> Path:
    return state_path(data_dir, session_id).with_suffix(".reset")


def _mark_state_reset(data_dir: Path, session_id: str) -> bool:
    marker = _state_reset_path(data_dir, session_id)
    try:
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.touch(exist_ok=True)
    except OSError:
        return False
    try:
        state_path(data_dir, session_id).unlink(missing_ok=True)
    except OSError:
        pass
    return True


def _apply_pending_reset(data_dir: Path, session_id: str) -> None:
    if not _state_reset_path(data_dir, session_id).exists():
        return
    try:
        state_path(data_dir, session_id).unlink(missing_ok=True)
    except OSError:
        pass


def _finish_pending_reset(data_dir: Path, session_id: str) -> None:
    try:
        _state_reset_path(data_dir, session_id).unlink(missing_ok=True)
    except OSError:
        pass


def _acquire_state_lock(data_dir: Path, session_id: str) -> StateLock | None:
    lock_path = _state_lock_path(data_dir, session_id)
    deadline = time.monotonic() + STATE_LOCK_WAIT_SECONDS
    try:
        lock_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        return None

    if fcntl is not None:
        try:
            handle = lock_path.open("a+b")
        except OSError:
            return None
        while True:
            try:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                return StateLock(path=lock_path, handle=handle)
            except OSError as error:
                if error.errno not in {errno.EACCES, errno.EAGAIN}:
                    handle.close()
                    return None
                if time.monotonic() >= deadline:
                    handle.close()
                    return None
                time.sleep(0.01)

    directory_path = lock_path.with_suffix(".lockdir")
    while True:
        try:
            directory_path.mkdir()
            return StateLock(path=directory_path, directory=True)
        except FileExistsError:
            if time.monotonic() >= deadline:
                return None
            time.sleep(0.01)
        except OSError:
            return None


def _release_state_lock(lock: StateLock) -> None:
    if lock.handle is not None:
        try:
            fcntl.flock(lock.handle.fileno(), fcntl.LOCK_UN)
        except OSError:
            pass
        lock.handle.close()
        return
    if not lock.directory:
        return
    try:
        lock.path.rmdir()
    except OSError:
        pass


def _quarantine_corrupt_state(path: Path) -> None:
    try:
        path.replace(path.with_name(f"{path.name}.corrupt-{time.time_ns()}"))
    except OSError:
        pass


def _recovered_state(warning: str) -> dict:
    state = default_state()
    state["_state_warning"] = warning
    return state


def _has_valid_state_types(raw: dict) -> bool:
    legacy = "state_version" not in raw
    if not legacy and raw.get("state_version") != STATE_VERSION:
        return False
    phases = {
        "normal",
        "pre_alert",
        "checkpoint_required",
        "emergency",
        "clear_required" if legacy else "checkpoint_verified",
        "recovery_required" if not legacy else "normal",
    }
    if "phase" in raw and raw["phase"] not in phases:
        return False
    bool_keys = ["pre_alert_sent", "checkpoint_started"]
    if legacy:
        bool_keys.extend(["clear_required", "telemetry_warning_sent"])
    else:
        bool_keys.extend(["checkpoint_verified", "recovery_required"])
    for key in bool_keys:
        if key in raw and not isinstance(raw[key], bool):
            return False
    if "last_percent" in raw and raw["last_percent"] is not None:
        value = raw["last_percent"]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return False
        if not math.isfinite(value) or value < 0:
            return False
    if "updated_at" in raw and raw["updated_at"] is not None:
        if not _is_positive_int(raw["updated_at"]):
            return False
    return True


def load_state(data_dir: Path, session_id: str) -> dict:
    path = state_path(data_dir, session_id)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default_state()
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        _quarantine_corrupt_state(path)
        return _recovered_state(
            "Estado do guardião corrompido ou ilegível; foi isolado e reiniciado."
        )
    if not isinstance(raw, dict) or not _has_valid_state_types(raw):
        _quarantine_corrupt_state(path)
        return _recovered_state(
            "Estado do guardião inválido; foi isolado e reiniciado."
        )
    state = default_state()
    if "state_version" not in raw:
        checkpoint_verified = bool(raw.get("clear_required", False))
        legacy_phase = raw.get("phase", "normal")
        if legacy_phase == "clear_required":
            legacy_phase = "checkpoint_required"
        state.update(
            {
                "phase": (
                    "checkpoint_verified"
                    if checkpoint_verified
                    else legacy_phase
                ),
                "pre_alert_sent": raw.get("pre_alert_sent", False),
                "checkpoint_started": (
                    False
                    if checkpoint_verified
                    else raw.get("checkpoint_started", False)
                ),
                "checkpoint_verified": checkpoint_verified,
                "last_percent": raw.get("last_percent"),
                "updated_at": raw.get("updated_at"),
            }
        )
        return state
    state.update({key: raw[key] for key in STATE_KEYS if key in raw})
    return state


def save_state(data_dir: Path, session_id: str, state: dict) -> bool:
    path = state_path(data_dir, session_id)
    filtered = default_state()
    filtered.update({key: state[key] for key in STATE_KEYS if key in state})
    tmp_path: Path | None = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            delete=False,
        ) as handle:
            json.dump(filtered, handle, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
            tmp_path = Path(handle.name)
        os.replace(tmp_path, path)
        return True
    except OSError:
        if tmp_path is not None:
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass
        return False


def _persist_response(
    data_dir: Path,
    session_id: str,
    state: dict,
    response: dict | None,
) -> dict | None:
    state_warning = state.get("_state_warning")
    saved = save_state(data_dir, session_id, state)
    if saved:
        _finish_pending_reset(data_dir, session_id)
    if saved and not state_warning:
        return response
    warnings: list[str] = []
    if isinstance(state_warning, str):
        warnings.append(f"Orquestra: {state_warning}")
    if not saved:
        warnings.append(
            "Orquestra: telemetria de contexto indisponível; o hook falhou aberto e não "
            "bloqueará esta ação."
        )
    result = dict(response or {})
    result.pop("decision", None)
    result.pop("reason", None)
    previous = result.get("systemMessage")
    warning = " ".join(warnings)
    result["systemMessage"] = f"{previous} {warning}" if previous else warning
    return result


def _additional_context(event_name: str, text: str) -> dict:
    return {
        "hookSpecificOutput": {
            "hookEventName": event_name,
            "additionalContext": text,
        }
    }


def _normalize_text(value: object) -> str:
    if not isinstance(value, str):
        return ""
    decomposed = unicodedata.normalize("NFKD", value.casefold())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def _is_checkpoint_intent(prompt: object) -> bool:
    normalized = _normalize_text(prompt)
    return any(
        phrase in normalized
        for phrase in (
            "checkpoint",
            "salva",
            "salvar",
            "seguro limpar",
            "corrigir verificacao",
            "retomar checkpoint",
        )
    )


def _has_verified_checkpoint_phrase(message: object) -> bool:
    if not isinstance(message, str):
        return False
    patterns = (
        r"^\s*(?:\*\*)?checkpoint verificado;\s*compactação liberada\.\s*(?:\*\*)?\s*$",
        r"^\s*(?:\*\*)?seguro dar\s+[`\"']?/clear[`\"']?\s*\.\s*(?:\*\*)?\s*$",
    )
    return any(re.search(pattern, message, re.I | re.M) is not None for pattern in patterns)


def _has_failed_checkpoint_phrase(message: object) -> bool:
    normalized = _normalize_text(message)
    return "nao afirmo que e seguro limpar" in normalized


def _session_context(
    event_name: str,
    source: object,
    *,
    checkpoint_verified: bool = False,
) -> dict | None:
    if source == "clear":
        return _additional_context(
            event_name,
            "Novo chat após /clear: antes de trabalhar, leia memory/MEMORY.md, "
            "memory/wiki/KANBAN.md e a thread ativa; confirme o contexto carregado.",
        )
    if source == "compact":
        if checkpoint_verified:
            return _additional_context(
                event_name,
                "Compactação concluída depois de checkpoint verificado. Antes de continuar, "
                "releia memory/MEMORY.md, memory/wiki/KANBAN.md e a thread ativa; confirme "
                "o contexto carregado.",
            )
        return _additional_context(
            event_name,
            "Houve compactação sem checkpoint verificado. Releia memory/MEMORY.md, "
            "memory/wiki/KANBAN.md e a thread ativa; execute um checkpoint de recuperação "
            "antes de iniciar trabalho novo.",
        )
    return None


def _plugin_env(env: Mapping[str, str], name: str) -> str | None:
    value = env.get(name) or env.get(f"CLAUDE_{name}")
    return value if isinstance(value, str) and value else None


def _handle_event_unlocked(event: dict, env: Mapping[str, str]) -> dict | None:
    """Converte um evento Codex numa decisão curta de hook, sempre fail-open."""

    if not isinstance(event, dict) or not env.get("PLUGIN_ROOT"):
        return None
    event_name = event.get("hook_event_name")
    if not isinstance(event_name, str):
        return None

    if event_name == "SessionStart":
        source = event.get("source")
        session_id = event.get("session_id")
        plugin_data = _plugin_env(env, "PLUGIN_DATA")
        if source == "clear":
            if isinstance(session_id, str) and session_id and isinstance(plugin_data, str):
                return _persist_response(
                    Path(plugin_data),
                    session_id,
                    default_state(),
                    _session_context(event_name, source),
                )
        if (
            source == "compact"
            and isinstance(session_id, str)
            and session_id
            and isinstance(plugin_data, str)
        ):
            data_dir = Path(plugin_data)
            previous = load_state(data_dir, session_id)
            checkpoint_verified = bool(previous.get("checkpoint_verified"))
            next_state = default_state()
            if not checkpoint_verified:
                next_state["phase"] = "recovery_required"
                next_state["recovery_required"] = True
            next_state["updated_at"] = int(time.time())
            return _persist_response(
                data_dir,
                session_id,
                next_state,
                _session_context(
                    event_name,
                    source,
                    checkpoint_verified=checkpoint_verified,
                ),
            )
        return _session_context(event_name, source)
    if event_name in {"PreCompact", "PostCompact"}:
        return None

    session_id = event.get("session_id")
    transcript_path = event.get("transcript_path")
    plugin_data = _plugin_env(env, "PLUGIN_DATA")
    if not isinstance(session_id, str) or not session_id or not isinstance(plugin_data, str):
        return None
    if not isinstance(transcript_path, str) or not transcript_path:
        return None

    data_dir = Path(plugin_data)
    state = load_state(data_dir, session_id)

    if event_name == "Stop" and _has_failed_checkpoint_phrase(
        event.get("last_assistant_message")
    ):
        state["checkpoint_started"] = False
        state["checkpoint_verified"] = False
        state["updated_at"] = int(time.time())
        return _persist_response(
            data_dir,
            session_id,
            state,
            {
                "systemMessage": (
                    "Checkpoint não foi verificado. Corrija o sinal quebrado; uma nova tentativa "
                    "será exigida antes de continuar."
                )
            },
        )
    if event_name == "Stop" and _has_verified_checkpoint_phrase(
        event.get("last_assistant_message")
    ):
        state["phase"] = "checkpoint_verified"
        state["checkpoint_started"] = False
        state["checkpoint_verified"] = True
        state["recovery_required"] = False
        state["updated_at"] = int(time.time())
        return _persist_response(
            data_dir,
            session_id,
            state,
            {
                "systemMessage": (
                    "Checkpoint verificado; a compactação manual ou automática do Codex está liberada."
                )
            },
        )
    if (
        event_name == "Stop"
        and event.get("stop_hook_active")
        and state.get("checkpoint_started")
        and isinstance(event.get("last_assistant_message"), str)
        and event.get("last_assistant_message")
    ):
        state["checkpoint_started"] = False
        state["checkpoint_verified"] = False
        state["updated_at"] = int(time.time())
        return _persist_response(
            data_dir,
            session_id,
            state,
            {
                "systemMessage": (
                    "Checkpoint terminou sem a frase contratual de verificação. Corrija o sinal; "
                    "uma nova tentativa será exigida antes de continuar."
                )
            },
        )

    snapshot = read_latest_usage(Path(transcript_path))
    if snapshot is None:
        return None
    percent = snapshot.percent
    band = band_for(percent)
    state["last_percent"] = round(percent, 2)
    state["updated_at"] = int(time.time())
    if not state.get("checkpoint_verified") and not state.get("recovery_required"):
        state["phase"] = band

    if event_name == "UserPromptSubmit":
        if state.get("checkpoint_verified"):
            return _persist_response(data_dir, session_id, state, None)
        if state.get("recovery_required"):
            if _is_checkpoint_intent(event.get("prompt")):
                state["checkpoint_started"] = True
                return _persist_response(
                    data_dir,
                    session_id,
                    state,
                    _additional_context(
                        event_name,
                        "A sessão foi compactada sem checkpoint verificado. Execute agora o "
                        "checkpoint de recuperação antes de trabalho novo.",
                    ),
                )
            return _persist_response(
                data_dir,
                session_id,
                state,
                {
                    "decision": "block",
                    "reason": (
                        "Compactação ocorreu sem checkpoint verificado. Execute o checkpoint "
                        "de recuperação antes de iniciar trabalho novo."
                    ),
                },
            )
        if band == "emergency" and not _is_checkpoint_intent(event.get("prompt")):
            return _persist_response(
                data_dir,
                session_id,
                state,
                {
                    "decision": "block",
                    "reason": (
                        f"Contexto em {percent:.1f}%. Peça o checkpoint agora; trabalho novo está bloqueado "
                        "até a verificação durável terminar."
                    ),
                },
            )
        if band in {"checkpoint_required", "emergency"}:
            state["checkpoint_started"] = True
            return _persist_response(
                data_dir,
                session_id,
                state,
                _additional_context(
                    event_name,
                    f"Contexto em {percent:.1f}%. Antes de atender trabalho novo, execute somente o "
                    "checkpoint do Orquestra e finalize com a verificação para compactação.",
                ),
            )
        if band == "pre_alert" and not state.get("pre_alert_sent"):
            state["pre_alert_sent"] = True
            return _persist_response(
                data_dir,
                session_id,
                state,
                _additional_context(
                    event_name,
                    f"Contexto em {percent:.1f}%: conclua apenas a unidade atômica atual e prepare checkpoint.",
                ),
            )

    if event_name == "PostToolUse":
        if state.get("checkpoint_verified"):
            return _persist_response(data_dir, session_id, state, None)
        if state.get("recovery_required"):
            return _persist_response(
                data_dir,
                session_id,
                state,
                _additional_context(
                    event_name,
                    "Pare antes de outra ferramenta e execute o checkpoint de recuperação.",
                ),
            )
        if band in {"checkpoint_required", "emergency"}:
            return _persist_response(
                data_dir,
                session_id,
                state,
                _additional_context(
                    event_name,
                    f"Contexto em {percent:.1f}%. Pare antes de outra ferramenta e execute o checkpoint.",
                ),
            )
        if band == "pre_alert" and not state.get("pre_alert_sent"):
            state["pre_alert_sent"] = True
            return _persist_response(
                data_dir,
                session_id,
                state,
                _additional_context(
                    event_name,
                    f"Contexto em {percent:.1f}%: prepare o fechamento atômico e o checkpoint.",
                ),
            )

    if event_name == "Stop":
        if state.get("checkpoint_verified"):
            return _persist_response(data_dir, session_id, state, None)
        if state.get("recovery_required"):
            if event.get("stop_hook_active") or state.get("checkpoint_started"):
                return _persist_response(
                    data_dir,
                    session_id,
                    state,
                    {
                        "systemMessage": (
                            "Orquestra: checkpoint de recuperação continua obrigatório."
                        )
                    },
                )
            state["checkpoint_started"] = True
            return _persist_response(
                data_dir,
                session_id,
                state,
                {
                    "decision": "block",
                    "reason": (
                        "A sessão foi compactada sem checkpoint verificado. Execute agora o "
                        "checkpoint de recuperação e verifique os artefatos duráveis."
                    ),
                },
            )
        if band == "pre_alert" and not state.get("pre_alert_sent"):
            state["pre_alert_sent"] = True
            return _persist_response(
                data_dir,
                session_id,
                state,
                {
                    "systemMessage": (
                        f"Orquestra: contexto em {percent:.1f}%; prepare checkpoint antes de 60%."
                    )
                },
            )
        if band in {"checkpoint_required", "emergency"}:
            if event.get("stop_hook_active") or state.get("checkpoint_started"):
                return _persist_response(
                    data_dir,
                    session_id,
                    state,
                    {
                        "systemMessage": (
                            f"Orquestra: contexto em {percent:.1f}%; checkpoint continua obrigatório."
                        )
                    },
                )
            state["checkpoint_started"] = True
            return _persist_response(
                data_dir,
                session_id,
                state,
                {
                    "decision": "block",
                    "reason": (
                        f"Contexto em {percent:.1f}%. Execute agora o checkpoint completo do Orquestra; "
                        "não faça trabalho novo e emita a frase contratual somente após verificar o board."
                    ),
                },
            )

    return _persist_response(data_dir, session_id, state, None)


def handle_event(event: dict, env: Mapping[str, str]) -> dict | None:
    """Serializa a transação de estado por sessão e falha aberto se o lock não vier."""

    if not isinstance(event, dict) or not env.get("PLUGIN_ROOT"):
        return None
    event_name = event.get("hook_event_name")
    if event_name in {"PreCompact", "PostCompact"}:
        return _handle_event_unlocked(event, env)
    session_id = event.get("session_id")
    plugin_data = _plugin_env(env, "PLUGIN_DATA")
    if not isinstance(session_id, str) or not session_id or not isinstance(plugin_data, str):
        return _handle_event_unlocked(event, env)

    data_dir = Path(plugin_data)
    if event_name == "SessionStart" and event.get("source") == "clear":
        _mark_state_reset(data_dir, session_id)

    lock_path = _acquire_state_lock(data_dir, session_id)
    if lock_path is None:
        response = (
            _session_context("SessionStart", event.get("source"))
            if event_name == "SessionStart"
            else None
        )
        result = dict(response or {})
        result["systemMessage"] = (
            "Orquestra: telemetria de contexto ocupada ou indisponível; o hook falhou aberto."
        )
        return result
    try:
        _apply_pending_reset(data_dir, session_id)
        return _handle_event_unlocked(event, env)
    finally:
        _release_state_lock(lock_path)


def main() -> int:
    try:
        event = json.loads(sys.stdin.read())
        result = handle_event(event, os.environ)
        if result is not None:
            print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
