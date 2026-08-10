#!/usr/bin/env python3
"""Guardião preventivo da janela de contexto do Codex."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import tempfile
import time


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
