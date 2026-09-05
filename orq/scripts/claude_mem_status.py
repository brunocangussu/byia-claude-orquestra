#!/usr/bin/env python3
"""Classifica a captura do claude-mem por metadados do SQLite, sem ler conteúdo."""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import sqlite3
import time
from pathlib import Path
from typing import Any, Sequence


HEALTHY_STATES = {"CAPTURANDO", "OCIOSO", "EXCLUÍDO"}


def _result(state: str, reason: str, **details: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {"state": state, "reason": reason}
    payload.update(details)
    return payload


def _patterns_from_settings(
    settings_path: Path,
    extra_patterns: Sequence[str],
) -> tuple[list[str], str | None]:
    patterns = [pattern.strip() for pattern in extra_patterns if pattern.strip()]
    if not settings_path.exists():
        return patterns, None
    try:
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return patterns, "settings_unavailable"
    raw = settings.get("CLAUDE_MEM_EXCLUDED_PROJECTS", "")
    if not isinstance(raw, str):
        return patterns, "settings_exclusion_invalid"
    patterns.extend(part.strip() for part in raw.split(",") if part.strip())
    return patterns, None


def _project_matches(project: str, patterns: Sequence[str]) -> bool:
    normalized = project.replace("\\", "/")
    basename = Path(normalized).name
    return any(
        fnmatch.fnmatchcase(normalized, pattern)
        or fnmatch.fnmatchcase(basename, pattern)
        for pattern in patterns
    )


def _inside_slo(now_epoch_ms: int, anchor_epoch_ms: int, stale_ms: int) -> bool:
    return max(0, now_epoch_ms - anchor_epoch_ms) < stale_ms


def _pending_or_stopped(
    *,
    now_epoch_ms: int,
    anchor_epoch_ms: int,
    stale_ms: int,
    pending_reason: str,
    stopped_reason: str,
    metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    age_ms = max(0, now_epoch_ms - anchor_epoch_ms)
    if _inside_slo(now_epoch_ms, anchor_epoch_ms, stale_ms):
        return _result(
            "ATRASADO",
            pending_reason,
            age_ms=age_ms,
            stale_after_ms=stale_ms,
            **({"metrics": metrics} if metrics is not None else {}),
        )
    return _result(
        "PARADO",
        stopped_reason,
        age_ms=age_ms,
        stale_after_ms=stale_ms,
        **({"metrics": metrics} if metrics is not None else {}),
    )


def _open_read_only(db_path: Path) -> sqlite3.Connection:
    uri = db_path.expanduser().resolve().as_uri() + "?mode=ro"
    return sqlite3.connect(uri, uri=True)


def evaluate_status(
    *,
    db_path: Path,
    settings_path: Path,
    platform: str,
    project: str | None,
    content_session_id: str | None,
    since_epoch_ms: int | None,
    stale_after_minutes: float,
    expect_summary: bool,
    now_epoch_ms: int | None,
    extra_excluded_patterns: Sequence[str],
) -> dict[str, Any]:
    """Avalia uma sessão sem selecionar colunas de conteúdo do banco."""

    now_ms = now_epoch_ms if now_epoch_ms is not None else int(time.time() * 1000)
    stale_ms = max(1, int(stale_after_minutes * 60_000))
    patterns, settings_error = _patterns_from_settings(
        settings_path.expanduser(), extra_excluded_patterns
    )
    if settings_error:
        return _result("INDETERMINADO", settings_error)
    if project and _project_matches(project, patterns):
        return _result(
            "EXCLUÍDO",
            "project_matches_exclusion",
            platform=platform,
            project=project,
        )

    try:
        connection = _open_read_only(db_path)
    except (OSError, sqlite3.Error):
        return _result("INDETERMINADO", "database_unavailable")

    try:
        where = ["platform_source = ?"]
        values: list[Any] = [platform]
        if project:
            where.append("project = ?")
            values.append(project)
        if content_session_id:
            where.append("content_session_id = ?")
            values.append(content_session_id)
        session = connection.execute(
            f"""
            SELECT id, content_session_id, memory_session_id, project, status,
                   started_at_epoch, completed_at_epoch
              FROM sdk_sessions
             WHERE {' AND '.join(where)}
             ORDER BY started_at_epoch DESC, id DESC
             LIMIT 1
            """,
            values,
        ).fetchone()
        if session is None:
            if since_epoch_ms is None:
                return _result(
                    "OCIOSO",
                    "no_session_in_scope",
                    platform=platform,
                    project=project,
                )
            return _pending_or_stopped(
                now_epoch_ms=now_ms,
                anchor_epoch_ms=since_epoch_ms,
                stale_ms=stale_ms,
                pending_reason="session_not_created_yet",
                stopped_reason="session_not_created",
            )

        (
            session_db_id,
            stored_content_session_id,
            memory_session_id,
            stored_project,
            status,
            started_at_epoch,
            completed_at_epoch,
        ) = session
        prompt_count, latest_prompt = connection.execute(
            """
            SELECT count(*), max(created_at_epoch)
              FROM user_prompts
             WHERE session_db_id = ? OR content_session_id = ?
            """,
            (session_db_id, stored_content_session_id),
        ).fetchone()
        if memory_session_id:
            observation_count, latest_observation = connection.execute(
                """
                SELECT count(*), max(created_at_epoch)
                  FROM observations
                 WHERE memory_session_id = ?
                """,
                (memory_session_id,),
            ).fetchone()
            summary_count, latest_summary = connection.execute(
                """
                SELECT count(*), max(created_at_epoch)
                  FROM session_summaries
                 WHERE memory_session_id = ?
                """,
                (memory_session_id,),
            ).fetchone()
        else:
            observation_count, latest_observation = 0, None
            summary_count, latest_summary = 0, None
    except sqlite3.Error:
        return _result("INDETERMINADO", "database_schema_or_query_error")
    finally:
        connection.close()

    metrics = {
        "session_db_id": session_db_id,
        "status": status,
        "started_at_epoch": started_at_epoch,
        "completed_at_epoch": completed_at_epoch,
        "prompts": prompt_count,
        "latest_prompt_epoch": latest_prompt,
        "observations": observation_count,
        "latest_observation_epoch": latest_observation,
        "summaries": summary_count,
        "latest_summary_epoch": latest_summary,
    }
    event_epochs = [
        value
        for value in (latest_prompt, latest_observation, latest_summary)
        if value is not None
    ]
    if completed_at_epoch is not None and any(
        value > completed_at_epoch for value in event_epochs
    ):
        return _result(
            "PARADO",
            "event_after_session_completion",
            platform=platform,
            project=stored_project,
            metrics=metrics,
        )

    anchor = since_epoch_ms if since_epoch_ms is not None else started_at_epoch
    if memory_session_id is None:
        return _pending_or_stopped(
            now_epoch_ms=now_ms,
            anchor_epoch_ms=anchor,
            stale_ms=stale_ms,
            pending_reason="memory_session_id_pending",
            stopped_reason="memory_session_id_missing",
            metrics=metrics,
        )
    if prompt_count == 0:
        return _pending_or_stopped(
            now_epoch_ms=now_ms,
            anchor_epoch_ms=anchor,
            stale_ms=stale_ms,
            pending_reason="prompt_not_committed_yet",
            stopped_reason="prompt_not_committed",
            metrics=metrics,
        )
    if observation_count == 0:
        observation_anchor = latest_prompt if latest_prompt is not None else anchor
        return _pending_or_stopped(
            now_epoch_ms=now_ms,
            anchor_epoch_ms=observation_anchor,
            stale_ms=stale_ms,
            pending_reason="observation_not_committed_yet",
            stopped_reason="observation_not_committed",
            metrics=metrics,
        )
    if latest_prompt is not None and (
        latest_observation is None or latest_observation < latest_prompt
    ):
        return _pending_or_stopped(
            now_epoch_ms=now_ms,
            anchor_epoch_ms=latest_prompt,
            stale_ms=stale_ms,
            pending_reason="latest_prompt_not_observed_yet",
            stopped_reason="latest_prompt_not_observed",
            metrics=metrics,
        )
    if expect_summary and summary_count == 0:
        summary_anchor = latest_observation if latest_observation is not None else anchor
        return _pending_or_stopped(
            now_epoch_ms=now_ms,
            anchor_epoch_ms=summary_anchor,
            stale_ms=stale_ms,
            pending_reason="summary_not_committed_yet",
            stopped_reason="summary_not_committed",
            metrics=metrics,
        )
    return _result(
        "CAPTURANDO",
        "metadata_advanced",
        platform=platform,
        project=stored_project,
        metrics=metrics,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--db",
        type=Path,
        default=Path("~/.claude-mem/claude-mem.db"),
        help="SQLite do claude-mem (aberto em mode=ro)",
    )
    parser.add_argument(
        "--settings",
        type=Path,
        default=Path("~/.claude-mem/settings.json"),
        help="Configuração usada apenas para ler exclusões",
    )
    parser.add_argument("--platform", choices=("claude", "codex"), required=True)
    parser.add_argument(
        "--project",
        help="Projeto exato do banco; por padrão usa o basename do diretório atual",
    )
    parser.add_argument("--content-session-id")
    parser.add_argument("--since-epoch-ms", type=int)
    parser.add_argument("--stale-after-minutes", type=float, default=15)
    parser.add_argument("--expect-summary", action="store_true")
    parser.add_argument("--now-epoch-ms", type=int, help=argparse.SUPPRESS)
    parser.add_argument("--excluded-pattern", action="append", default=[])
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    result = evaluate_status(
        db_path=args.db,
        settings_path=args.settings,
        platform=args.platform,
        project=args.project or Path.cwd().name,
        content_session_id=args.content_session_id,
        since_epoch_ms=args.since_epoch_ms,
        stale_after_minutes=args.stale_after_minutes,
        expect_summary=args.expect_summary,
        now_epoch_ms=args.now_epoch_ms,
        extra_excluded_patterns=args.excluded_pattern,
    )
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    if result["state"] == "INDETERMINADO":
        return 2
    return 0 if result["state"] in HEALTHY_STATES else 1


if __name__ == "__main__":
    raise SystemExit(main())
