#!/usr/bin/env python3
"""Guardião preventivo da janela de contexto do Codex."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import time
from typing import Mapping
import unicodedata


DEFAULT_TAIL_BYTES = 4 * 1024 * 1024
STATE_KEYS = (
    "phase",
    "pre_alert_sent",
    "checkpoint_started",
    "clear_required",
    "telemetry_warning_sent",
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

    for raw_line in reversed(_read_tail_lines(path, tail_bytes)):
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
        "phase": "normal",
        "pre_alert_sent": False,
        "checkpoint_started": False,
        "clear_required": False,
        "telemetry_warning_sent": False,
        "last_percent": None,
        "updated_at": None,
    }


def state_path(data_dir: Path, session_id: str) -> Path:
    digest = hashlib.sha256(session_id.encode("utf-8", errors="replace")).hexdigest()
    return data_dir / "context-guard" / f"{digest}.json"


def _quarantine_corrupt_state(path: Path) -> None:
    try:
        path.replace(path.with_name(f"{path.name}.corrupt-{time.time_ns()}"))
    except OSError:
        pass


def load_state(data_dir: Path, session_id: str) -> dict:
    path = state_path(data_dir, session_id)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default_state()
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        _quarantine_corrupt_state(path)
        return default_state()
    if not isinstance(raw, dict):
        _quarantine_corrupt_state(path)
        return default_state()
    state = default_state()
    state.update({key: raw[key] for key in STATE_KEYS if key in raw})
    return state


def save_state(data_dir: Path, session_id: str, state: dict) -> None:
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
    except OSError:
        if tmp_path is not None:
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass


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


def _has_safe_clear_phrase(message: object) -> bool:
    if not isinstance(message, str):
        return False
    return re.search(r"seguro dar\s+[`\"']?/clear[`\"']?\s*\.", message, re.I) is not None


def _session_context(event_name: str, source: object) -> dict | None:
    if source == "clear":
        return _additional_context(
            event_name,
            "Novo chat após /clear: antes de trabalhar, leia memory/MEMORY.md, "
            "memory/wiki/KANBAN.md e a thread ativa; confirme o contexto carregado.",
        )
    if source == "compact":
        return _additional_context(
            event_name,
            "Houve compactação em vez do fluxo checkpoint → /clear. Recarregue board/wiki/memória "
            "e execute um checkpoint de recuperação antes de iniciar trabalho novo.",
        )
    return None


def handle_event(event: dict, env: Mapping[str, str]) -> dict | None:
    """Converte um evento Codex numa decisão curta de hook, sempre fail-open."""

    if not isinstance(event, dict) or not env.get("PLUGIN_ROOT"):
        return None
    event_name = event.get("hook_event_name")
    if not isinstance(event_name, str):
        return None

    if event_name == "SessionStart":
        return _session_context(event_name, event.get("source"))
    if event_name in {"PreCompact", "PostCompact"}:
        return {
            "systemMessage": (
                "Orquestra: compactação detectada como contingência; não substitui checkpoint + /clear."
            )
        }

    session_id = event.get("session_id")
    transcript_path = event.get("transcript_path")
    plugin_data = env.get("PLUGIN_DATA")
    if not isinstance(session_id, str) or not session_id or not isinstance(plugin_data, str):
        return None
    if not isinstance(transcript_path, str) or not transcript_path:
        return None

    data_dir = Path(plugin_data)
    state = load_state(data_dir, session_id)

    if event_name == "Stop" and _has_safe_clear_phrase(event.get("last_assistant_message")):
        state["phase"] = "clear_required"
        state["clear_required"] = True
        state["updated_at"] = int(time.time())
        save_state(data_dir, session_id, state)
        return {
            "systemMessage": (
                "Checkpoint verificado. Não inicie trabalho novo nesta sessão; execute /clear."
            )
        }

    snapshot = read_latest_usage(Path(transcript_path))
    if snapshot is None:
        return None
    percent = snapshot.percent
    band = band_for(percent)
    state["last_percent"] = round(percent, 2)
    state["updated_at"] = int(time.time())
    if not state.get("clear_required"):
        state["phase"] = band

    if event_name == "UserPromptSubmit":
        if state.get("clear_required"):
            save_state(data_dir, session_id, state)
            return {
                "decision": "block",
                "reason": "Checkpoint já verificado. Execute /clear antes de iniciar trabalho novo.",
            }
        if band == "emergency" and not _is_checkpoint_intent(event.get("prompt")):
            save_state(data_dir, session_id, state)
            return {
                "decision": "block",
                "reason": (
                    f"Contexto em {percent:.1f}%. Peça o checkpoint agora; trabalho novo está bloqueado "
                    "até ser seguro executar /clear."
                ),
            }
        if band in {"checkpoint_required", "emergency"}:
            state["checkpoint_started"] = True
            save_state(data_dir, session_id, state)
            return _additional_context(
                event_name,
                f"Contexto em {percent:.1f}%. Antes de atender trabalho novo, execute somente o "
                "checkpoint do Orquestra e finalize com a verificação para /clear.",
            )
        if band == "pre_alert" and not state.get("pre_alert_sent"):
            state["pre_alert_sent"] = True
            save_state(data_dir, session_id, state)
            return _additional_context(
                event_name,
                f"Contexto em {percent:.1f}%: conclua apenas a unidade atômica atual e prepare checkpoint.",
            )

    if event_name == "PostToolUse":
        if band in {"checkpoint_required", "emergency"}:
            save_state(data_dir, session_id, state)
            return _additional_context(
                event_name,
                f"Contexto em {percent:.1f}%. Pare antes de outra ferramenta e execute o checkpoint.",
            )
        if band == "pre_alert" and not state.get("pre_alert_sent"):
            state["pre_alert_sent"] = True
            save_state(data_dir, session_id, state)
            return _additional_context(
                event_name,
                f"Contexto em {percent:.1f}%: prepare o fechamento atômico e o checkpoint.",
            )

    if event_name == "Stop":
        if state.get("clear_required"):
            save_state(data_dir, session_id, state)
            return {"systemMessage": "Checkpoint concluído; execute /clear."}
        if band == "pre_alert" and not state.get("pre_alert_sent"):
            state["pre_alert_sent"] = True
            save_state(data_dir, session_id, state)
            return {
                "systemMessage": (
                    f"Orquestra: contexto em {percent:.1f}%; prepare checkpoint antes de 60%."
                )
            }
        if band in {"checkpoint_required", "emergency"}:
            if event.get("stop_hook_active") or state.get("checkpoint_started"):
                save_state(data_dir, session_id, state)
                return {
                    "systemMessage": (
                        f"Orquestra: contexto em {percent:.1f}%; checkpoint continua obrigatório."
                    )
                }
            state["checkpoint_started"] = True
            save_state(data_dir, session_id, state)
            return {
                "decision": "block",
                "reason": (
                    f"Contexto em {percent:.1f}%. Execute agora o checkpoint completo do Orquestra; "
                    "não faça trabalho novo e termine informando se é seguro dar /clear."
                ),
            }

    save_state(data_dir, session_id, state)
    return None


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
