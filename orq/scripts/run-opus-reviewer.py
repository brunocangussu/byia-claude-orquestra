#!/usr/bin/env python3
"""Executa um papel read-only num modelo Anthropic e só entrega saída comprovada.

O nome do arquivo e o prefixo `OPUS_` das mensagens são **contrato de fio estável**,
preservados de quando o Opus era o único modelo Anthropic alcançável fora de spawn.
Toda mensagem nomeia o modelo real, então o prefixo é rótulo de código, não afirmação
sobre qual modelo rodou.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time
import uuid


DEFAULT_MAX_INPUT_BYTES = 16_384
DEFAULT_TIMEOUT_SECONDS = 600.0
DEFAULT_MODEL_ALIAS = "opus"
POSIX = os.name == "posix"
TERMINATION_GRACE_SECONDS = 0.2

# Alias/ID solicitado → identidade esperada em `modelUsage`.
# O ID explícito exige igualdade; os aliases legados preservam os prefixos
# de release existentes. Fable solicitado nunca é redirecionado para Opus.
MODEL_ALIASES = {
    "claude-opus-5-5": "claude-opus-5-5",
    "opus": "claude-opus-5",
    "fable": "claude-fable-5-1",
    "sonnet": "claude-sonnet-5",
    "haiku": "claude-haiku-4-5",
}

# Somente valores estruturados conhecidos podem sair de streams de erro.
# Texto livre pode conter prompt, token ou PII: não é seguro só truncá-lo.
ERROR_CODES = frozenset({
    "authentication_error", "permission_error", "rate_limit_error",
    "invalid_request_error", "not_found_error", "overloaded_error", "api_error",
})
RESULT_SUBTYPES = frozenset({
    "success", "error_during_execution", "error_max_turns", "error_max_budget_usd",
})


def stream_bytes(value: bytes | str | None) -> bytes | None:
    if value is None:
        return None
    return value if isinstance(value, bytes) else value.encode("utf-8")


def fingerprint(value: bytes | str | None) -> dict:
    raw = stream_bytes(value)
    return {"bytes": len(raw) if raw is not None else None,
            "sha256": hashlib.sha256(raw).hexdigest() if raw is not None else None}


def read_payload(stdout: bytes | str | None) -> tuple[dict | None, str]:
    try:
        payload = json.loads(stdout or b"")
    except (ValueError, UnicodeDecodeError, RecursionError):
        return None, "invalid_json"
    return (payload, "json_object") if isinstance(payload, dict) else (None, "json_non_object")


def diagnostic_metadata(stdout: bytes | str | None) -> dict:
    payload, shape = read_payload(stdout)
    result = {"format": shape, "is_error": None, "subtype": None,
              "error_code": None, "free_text_suppressed": True}
    if payload is None:
        return result
    result["is_error"] = payload.get("is_error") if isinstance(payload.get("is_error"), bool) else None
    subtype = payload.get("subtype")
    result["subtype"] = subtype if isinstance(subtype, str) and subtype in RESULT_SUBTYPES else None
    error = payload.get("error")
    candidates = [payload.get("error_code")]
    if isinstance(error, dict):
        candidates.extend((error.get("type"), error.get("code")))
    result["error_code"] = next((x for x in candidates if isinstance(x, str) and x in ERROR_CODES), None)
    return result


def execution_metadata(command: list[str]) -> dict:
    entry = Path(command[0])
    try:
        digest = hashlib.sha256()
        with entry.open("rb") as source:
            for chunk in iter(lambda: source.read(1_048_576), b""):
                digest.update(chunk)
        entry_sha = digest.hexdigest()
    except OSError:
        entry_sha = None
    try:
        resolved_name = entry.resolve().name
        cwd = Path.cwd()
        cwd_empty = not any(cwd.iterdir())
        cwd_sha = hashlib.sha256(os.fsencode(str(cwd))).hexdigest()
    except OSError:
        resolved_name, cwd_empty, cwd_sha = "", None, None
    return {
        "entry_sha256": entry_sha,
        "entry_path_sha256": hashlib.sha256(os.fsencode(str(entry))).hexdigest(),
        # Rótulo do caminho, não versão comprovada por --version. Wrapper:
        # desconhecido; não fingir que seu digest identifica a CLI folha.
        "entry_version_from_path": resolved_name if re.fullmatch(r"\d+\.\d+\.\d+", resolved_name) else None,
        "args": command[1:], "cwd_path_sha256": cwd_sha, "cwd_empty": cwd_empty,
        "claudecode_present": "CLAUDECODE" in os.environ,
    }


def emit_process_receipt(attempt: dict, stdout: bytes | str | None,
                         stderr: bytes | str | None, cli_exit: int | None,
                         elapsed: float, *, timed_out: bool = False) -> None:
    receipt = {**attempt, "cli_exit": cli_exit, "timed_out": timed_out,
               "elapsed_seconds": round(elapsed, 3), "stdout": fingerprint(stdout),
               "stderr": fingerprint(stderr), "diagnostic": diagnostic_metadata(stdout),
               "observed_model": None, "cost_usd": None, "provider_request_sent": None}
    print("OPUS_PROCESS_RECEIPT " + json.dumps(receipt, sort_keys=True), file=sys.stderr, flush=True)


def matches_model_identity(name: object, expected: str, *, exact: bool = False) -> bool:
    if not isinstance(name, str):
        return False
    if exact:
        return name == expected
    return re.fullmatch(re.escape(expected) + r"(?:-\d+)*", name) is not None


def safe_model_name(name: object) -> str:
    return name if any(matches_model_identity(name, prefix) for prefix in MODEL_ALIASES.values()) \
        else "<nao-reconhecido>"


def emit_outcome(attempt_id: str, runner_exit: int, *, has_verdict: bool = False) -> None:
    print("OPUS_OUTCOME " + json.dumps({"attempt_id": attempt_id,
          "runner_exit": runner_exit, "has_verdict": has_verdict}), file=sys.stderr, flush=True)


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
        description="Lê briefing no stdin e retorna somente parecer comprovado do modelo Anthropic."
    )
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--max-input-bytes", type=int, default=DEFAULT_MAX_INPUT_BYTES)
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL_ALIAS,
        help=f"alias ou ID Anthropic a executar; um de {', '.join(sorted(MODEL_ALIASES))}",
    )
    parser.add_argument("--effort", choices=("low", "medium", "high"),
                        help="effort explícito do perfil; ausência conserva a chamada legada, sem prova de effort")
    return parser.parse_args()


def latest_stream(previous: bytes | str | None, current: bytes | str | None) -> bytes | str | None:
    """Conserva a captura mais completa quando communicate expira mais de uma vez."""
    if current is None:
        return previous
    if previous is None or len(current) >= len(previous):
        return current
    return previous


def timeout_streams(exc: subprocess.TimeoutExpired) -> tuple[bytes | str | None, bytes | str | None]:
    return (
        getattr(exc, "output", getattr(exc, "stdout", None)),
        getattr(exc, "stderr", None),
    )


def owned_process_group_id(process: subprocess.Popen[bytes]) -> int | None:
    """Deriva o grupo da sessão POSIX criada para este Popen, sem consultar o líder."""
    if not POSIX or process.pid is None:
        return None
    # `start_new_session=POSIX` na criação torna o PID o líder do grupo próprio.
    # A identidade continua válida para killpg mesmo se o líder já tiver saído.
    return process.pid


def signal_owned_process_group(
    process: subprocess.Popen[bytes], group_id: int, sig: signal.Signals,
) -> bool:
    """Sinaliza o grupo já comprovado, sem depender do líder após seu reap."""
    try:
        os.killpg(group_id, sig)
        return True
    except (PermissionError, ProcessLookupError):
        return False


def close_process_pipes(process: subprocess.Popen[bytes]) -> None:
    for stream in (process.stdin, process.stdout, process.stderr):
        if stream is not None:
            try:
                stream.close()
            except OSError:
                pass


def collect_timed_out_process(
    process: subprocess.Popen[bytes], exc: subprocess.TimeoutExpired,
) -> tuple[bytes | str | None, bytes | str | None]:
    """Encerra o grupo próprio e coleta sem esperar indefinidamente por pipe herdado."""
    stdout, stderr = timeout_streams(exc)
    group_id = owned_process_group_id(process)
    if group_id is not None:
        signal_owned_process_group(process, group_id, signal.SIGTERM)
        # TERM pode encerrar só o pai e liberar EOF; KILL ainda precisa atingir
        # o grupo comprovado antes de communicate/reap perder a identidade dele.
        signal_owned_process_group(process, group_id, signal.SIGKILL)
    else:
        try:
            process.terminate()
        except ProcessLookupError:
            pass
        try:
            process.kill()
        except ProcessLookupError:
            pass
    try:
        collected_stdout, collected_stderr = process.communicate(timeout=TERMINATION_GRACE_SECONDS)
        return latest_stream(stdout, collected_stdout), latest_stream(stderr, collected_stderr)
    except subprocess.TimeoutExpired as grace:
        collected_stdout, collected_stderr = timeout_streams(grace)
        stdout = latest_stream(stdout, collected_stdout)
        stderr = latest_stream(stderr, collected_stderr)

    # Um descendente que saiu voluntariamente da sessão ainda pode reter os
    # pipes. Fechar somente os descritores locais evita que isso prolongue o
    # retorno do runner; não promete alcançar processo fora do grupo próprio.
    close_process_pipes(process)
    try:
        process.wait(timeout=TERMINATION_GRACE_SECONDS)
    except subprocess.TimeoutExpired:
        try:
            process.kill()
        except ProcessLookupError:
            pass
        try:
            process.wait(timeout=TERMINATION_GRACE_SECONDS)
        except subprocess.TimeoutExpired:
            pass
    return stdout, stderr


def main() -> int:
    args = parse_args()
    effort = getattr(args, "effort", None)
    if effort is not None and effort not in ("low", "medium", "high"):
        return fail(2, "OPUS_INVALID_EFFORT: effort recusado antes da chamada")
    if args.timeout <= 0 or args.max_input_bytes <= 0:
        return fail(2, "OPUS_INVALID_LIMITS: timeout e max-input-bytes devem ser positivos")

    # Fail-closed ANTES de qualquer efeito: alias sem prefixo conhecido não roda.
    expected_prefix = MODEL_ALIASES.get(args.model)
    if expected_prefix is None:
        return fail(
            2,
            f"MODEL_ALIAS_DESCONHECIDO: {args.model!r} não está no mapa de prova; "
            f"conhecidos: {', '.join(sorted(MODEL_ALIASES))}",
        )

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
        raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        return fail(2, f"BRIEFING_INVALID_UTF8: {exc}")
    # Nome estável do contrato de stdin; bytes evitam normalizar os streams
    # capturados (CRLF/UTF-8 inválido devem manter tamanhos/digests exatos).
    briefing = raw

    claude = resolve_claude()
    if not claude:
        if os.environ.get("CLAUDE_BIN"):
            return fail(3, f"CLAUDE_BIN_INVALID: {os.environ['CLAUDE_BIN']}")
        return fail(3, "OPUS_CLI_MISSING: claude não encontrado no PATH nem em ~/.local/bin/claude")

    command = [
        claude,
        "-p",
        "--model",
        args.model,
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

    if effort is not None:
        command[4:4] = ["--effort", effort]

    attempt = {"schema": 1, "attempt_id": uuid.uuid4().hex,
               "started_unix": time.time(), "briefing": fingerprint(raw),
               "execution": execution_metadata(command)}
    if effort is not None:
        attempt["effort"] = {"requested": effort, "sent": effort, "observed": None}
    try:
        attempt["source_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    except (OSError, NameError):
        attempt["source_sha256"] = None
    print("OPUS_ATTEMPT " + json.dumps(attempt, sort_keys=True, separators=(",", ":")), file=sys.stderr, flush=True)
    started = time.monotonic()
    print(
        f"OPUS_STARTED MODEL_ALIAS={args.model} TIMEOUT={args.timeout:g}s BRIEFING_BYTES={len(raw)}",
        file=sys.stderr,
        flush=True,
    )
    try:
        completed = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=POSIX,
        )
    except OSError:
        emit_process_receipt(attempt, None, None, None, time.monotonic() - started)
        emit_outcome(attempt["attempt_id"], 3)
        return fail(3, "OPUS_PROCESS_START_FAILED: sem diagnóstico livre; ver recibo")

    try:
        stdout, stderr = completed.communicate(input=briefing, timeout=args.timeout)
    except subprocess.TimeoutExpired as exc:
        stdout, stderr = collect_timed_out_process(completed, exc)
        elapsed = time.monotonic() - started
        emit_process_receipt(attempt, stdout, stderr, None, elapsed, timed_out=True)
        emit_outcome(attempt["attempt_id"], 4)
        return fail(4, f"OPUS_TIMEOUT: sem parecer após {elapsed:.1f}s")

    elapsed = time.monotonic() - started
    # Recibo dos DOIS streams antes de decidir sucesso/falha. Nada livre é
    # ecoado; o envelope pode persistir stderr mesmo quando stdout fica vazio.
    emit_process_receipt(attempt, stdout, stderr, completed.returncode, elapsed)

    def finish(code: int, message: str) -> int:
        emit_outcome(attempt["attempt_id"], code)
        return fail(code, message)

    if completed.returncode != 0:
        return finish(
            5,
            f"OPUS_PROCESS_FAILED: exit={completed.returncode}; diagnóstico sanitizado no recibo",
        )

    payload, shape = read_payload(stdout)
    if payload is None:
        return finish(6, f"OPUS_INVALID_JSON: {shape}")

    subtype = payload.get("subtype")
    if "subtype" in payload and (not isinstance(subtype, str) or subtype not in RESULT_SUBTYPES):
        return finish(5, "OPUS_INVALID_SUBTYPE: diagnóstico sanitizado no recibo")
    structured_error = (payload.get("error") or payload.get("errors") or payload.get("error_code") or
                        (isinstance(subtype, str) and subtype in RESULT_SUBTYPES - {"success"}))
    if payload.get("is_error") or structured_error:
        return finish(5, "OPUS_API_ERROR: diagnóstico sanitizado no recibo")

    usage_fields = [payload[key] for key in ("modelUsage", "model_usage") if key in payload]
    model_usage = usage_fields[0] if len(usage_fields) == 1 else None
    model_names = list(model_usage) if isinstance(model_usage, dict) else []
    exact_identity = args.model == "claude-opus-5-5"
    matching_models = [name for name in model_names
                       if matches_model_identity(name, expected_prefix, exact=exact_identity)]
    # Um parecer precisa de uma única identidade comprovada. Chaves extras,
    # mesmo de famílias conhecidas, tornam a procedência ambígua; desconhecidas
    # nunca são ecoadas no diagnóstico.
    if len(model_names) != 1 or len(matching_models) != 1:
        observed = ",".join(safe_model_name(name) for name in model_names) if model_names else "<ausente>"
        return finish(7, f"OPUS_MODEL_MISMATCH: esperado {expected_prefix}; observado {observed}")

    result = payload.get("result")
    if not isinstance(result, str) or not result.strip():
        return finish(8, "OPUS_EMPTY_RESULT: processo terminou sem parecer")

    emit_outcome(attempt["attempt_id"], 0, has_verdict=True)
    print(
        f"OPUS_MODEL={safe_model_name(matching_models[0])} OPUS_SECONDS={elapsed:.1f} "
        f"BRIEFING_BYTES={len(raw)} OPUS_MODEL_USAGE={','.join(sorted(safe_model_name(name) for name in model_names))}",
        file=sys.stderr,
    )
    print(result.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
