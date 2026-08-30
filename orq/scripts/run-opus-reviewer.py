#!/usr/bin/env python3
"""Executa reviewer Claude e só entrega saída comprovadamente gerada por Opus 5."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time


DEFAULT_MAX_INPUT_BYTES = 16_384
DEFAULT_TIMEOUT_SECONDS = 600.0
EXPECTED_MODEL_PREFIX = "claude-opus-5"


def fail(code: int, message: str) -> int:
    print(message, file=sys.stderr)
    return code


def resolve_claude() -> str | None:
    override = os.environ.get("CLAUDE_BIN")
    if override:
        candidate = Path(override).expanduser()
        return str(candidate) if candidate.is_file() and os.access(candidate, os.X_OK) else None

    discovered = shutil.which("claude")
    if discovered:
        return discovered

    fallback = Path.home() / ".local" / "bin" / "claude"
    return str(fallback) if fallback.is_file() and os.access(fallback, os.X_OK) else None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Lê briefing no stdin e retorna somente parecer comprovado do Opus 5."
    )
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--max-input-bytes", type=int, default=DEFAULT_MAX_INPUT_BYTES)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.timeout <= 0 or args.max_input_bytes <= 0:
        return fail(2, "OPUS_INVALID_LIMITS: timeout e max-input-bytes devem ser positivos")

    raw = sys.stdin.buffer.read(args.max_input_bytes + 1)
    if len(raw) > args.max_input_bytes:
        return fail(
            2,
            f"BRIEFING_TOO_LARGE: {len(raw)} bytes lidos; limite {args.max_input_bytes}. "
            "Envie diff focado ou trechos verbatim numerados.",
        )
    if not raw.strip():
        return fail(2, "BRIEFING_EMPTY: nenhum conteúdo recebido no stdin")
    try:
        briefing = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        return fail(2, f"BRIEFING_INVALID_UTF8: {exc}")

    claude = resolve_claude()
    if not claude:
        if os.environ.get("CLAUDE_BIN"):
            return fail(3, f"CLAUDE_BIN_INVALID: {os.environ['CLAUDE_BIN']}")
        return fail(3, "OPUS_CLI_MISSING: claude não encontrado no PATH nem em ~/.local/bin/claude")

    command = [
        claude,
        "-p",
        "--model",
        "opus",
        "--permission-mode",
        "plan",
        "--tools",
        "",
        "--setting-sources",
        "",
        "--disable-slash-commands",
        "--no-session-persistence",
        "--output-format",
        "json",
    ]

    started = time.monotonic()
    print(
        f"OPUS_STARTED MODEL_ALIAS=opus TIMEOUT={args.timeout:g}s BRIEFING_BYTES={len(raw)}",
        file=sys.stderr,
        flush=True,
    )
    try:
        completed = subprocess.run(
            command,
            input=briefing,
            text=True,
            capture_output=True,
            timeout=args.timeout,
        )
    except subprocess.TimeoutExpired:
        elapsed = time.monotonic() - started
        return fail(4, f"OPUS_TIMEOUT: sem parecer após {elapsed:.1f}s")

    elapsed = time.monotonic() - started
    if completed.returncode != 0:
        stderr_tail = completed.stderr[-2_000:].strip()
        return fail(
            5,
            f"OPUS_PROCESS_FAILED: exit={completed.returncode}; stderr={stderr_tail or '<vazio>'}",
        )

    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        return fail(6, f"OPUS_INVALID_JSON: {exc}")

    if payload.get("is_error"):
        detail = str(payload.get("result") or payload.get("subtype") or "sem detalhe")[:2_000]
        return fail(5, f"OPUS_API_ERROR: {detail}")

    model_usage = payload.get("modelUsage") or payload.get("model_usage") or {}
    model_names = list(model_usage) if isinstance(model_usage, dict) else []
    opus_models = [name for name in model_names if name.startswith(EXPECTED_MODEL_PREFIX)]
    if not opus_models:
        observed = ",".join(model_names) if model_names else "<ausente>"
        return fail(7, f"OPUS_MODEL_MISMATCH: esperado {EXPECTED_MODEL_PREFIX}; observado {observed}")

    result = payload.get("result")
    if not isinstance(result, str) or not result.strip():
        return fail(8, "OPUS_EMPTY_RESULT: processo terminou sem parecer")

    print(
        f"OPUS_MODEL={opus_models[0]} OPUS_SECONDS={elapsed:.1f} "
        f"BRIEFING_BYTES={len(raw)} OPUS_MODEL_USAGE={','.join(sorted(model_names))}",
        file=sys.stderr,
    )
    print(result.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
