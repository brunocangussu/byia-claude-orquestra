#!/usr/bin/env python3
"""Verifica offline se um trace normalizado adotou descoberta por grafo primeiro."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shlex
import stat
from typing import Any


TRACE_SCHEMA_VERSION = "orq.audit-trace.v1"
MAX_TRACE_BYTES = 2 * 1024 * 1024
MAX_NESTED_SHELL_DEPTH = 32
CODEBASE_GRAPH_ACTIONS = {
    "get_architecture",
    "get_code_snippet",
    "index_repository",
    "query_graph",
    "search_code",
    "search_graph",
    "trace_path",
}
SERENA_GRAPH_ACTIONS = {"find_symbol", "get_symbols_overview"}
TEXT_SEARCH_TOOLS = {
    "find",
    "glob",
    "grep",
    "list_files",
    "ripgrep",
    "search",
    "search_code",
    "search_for_pattern",
}
DIRECT_READ_TOOLS = {
    "get_file_contents",
    "read",
    "read_file",
}
MUTATION_TOOLS = {
    "apply_patch",
    "edit",
    "edit_file",
    "multi_edit",
    "multiedit",
    "notebook_edit",
    "write",
    "write_file",
}
TEXT_SEARCH_COMMANDS = {"find", "grep", "ls", "rg", "tree"}
DIRECT_READ_COMMANDS = {"bat", "cat", "head", "less", "sed", "tail"}
MUTATION_COMMANDS = {"apply_patch", "cp", "mkdir", "mv", "rm", "rmdir", "touch"}
INTERPRETER_COMMANDS = {"awk", "node", "perl", "python", "python3", "ruby"}
CATEGORY_PRIORITY = ("mutation", "direct-read", "text-search", "unverified", "graph")
SHELL_TOOL_ACTIONS = {"bash", "execute_command", "exec_command", "run_command", "shell", "sh", "zsh"}
SUSPICIOUS_SHELL_SYNTAX = ("$(", "`", ">|", "(", ")", "{", "}")
IRRELEVANT_TOOL_ACTIONS = {"update_plan"}


def snake_identifier(value: str) -> str:
    base = value.strip().replace("-", "_")
    base = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", base)
    return base.casefold()


def identifier_parts(value: str) -> list[str]:
    return [snake_identifier(part) for part in re.split(r"__+|[.:/]", value) if part]


def tool_category(value: str) -> str | None:
    parts = identifier_parts(value)
    if not parts:
        return None
    action = parts[-1]
    namespace = set(parts[:-1])
    is_bare = len(parts) == 1
    is_codebase_memory = bool(namespace & {"codebase_memory", "codebase_memory_mcp"})
    is_serena = "serena" in namespace
    if action in CODEBASE_GRAPH_ACTIONS and is_codebase_memory:
        return "graph"
    if action in SERENA_GRAPH_ACTIONS and is_serena:
        return "graph"
    if is_bare and action in CODEBASE_GRAPH_ACTIONS | SERENA_GRAPH_ACTIONS:
        return "unverified"
    if action in MUTATION_TOOLS:
        return "mutation"
    if action in DIRECT_READ_TOOLS:
        return "direct-read"
    if action in TEXT_SEARCH_TOOLS:
        return "text-search"
    return None


def field_strings(value: Any, *, command: bool) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        if command:
            return [shlex.join(value)]
        if value:
            return list(value)
    raise ValueError("campo canônico deve ser string ou lista de strings")


def is_shell_tool(value: str) -> bool:
    parts = identifier_parts(value)
    return bool(parts) and parts[-1] in SHELL_TOOL_ACTIONS


def is_irrelevant_tool(value: str) -> bool:
    parts = identifier_parts(value)
    return bool(parts) and parts[-1] in IRRELEVANT_TOOL_ACTIONS


def event_fields(event: dict[str, Any]) -> list[tuple[str, str]]:
    """Extrai somente campos canônicos; metadados como hook.name não entram."""
    fields: list[tuple[str, str]] = []

    def add_from(container: dict[str, Any]) -> None:
        for key, value in container.items():
            normalized = key.casefold()
            if normalized in {"tool", "name"}:
                fields.extend(("tool", item) for item in field_strings(value, command=False))
            elif normalized == "command":
                fields.extend(("command", item) for item in field_strings(value, command=True))

    add_from(event)
    item = event.get("item")
    if isinstance(item, dict):
        add_from(item)
    data = event.get("data")
    if isinstance(data, dict):
        nested_item = data.get("item")
        if isinstance(nested_item, dict):
            add_from(nested_item)
    return fields


def shell_segments(command: str) -> list[list[str]]:
    segments: list[list[str]] = [[]]
    for line in command.splitlines() or [command]:
        try:
            lexer = shlex.shlex(line, posix=True, punctuation_chars=";&|<>")
            lexer.whitespace_split = True
            lexer.commenters = ""
            tokens = list(lexer)
        except ValueError:
            # Um fallback aproximado pode apagar operadores colados ao alvo e transformar
            # escrita/leitura em um falso grafo. Shell inválido é sempre não verificável.
            tokens = ["__orq_unparseable_shell__"]
        for token in tokens:
            if token and set(token) <= {";", "&", "|"}:
                if segments[-1]:
                    segments.append([])
                continue
            segments[-1].append(token)
        if segments[-1]:
            segments.append([])
    return [segment for segment in segments if segment]


def unwrap_command(tokens: list[str]) -> tuple[list[str], str | None]:
    remaining = list(tokens)
    for _ in range(16):
        while remaining and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", remaining[0]):
            remaining.pop(0)
        if not remaining:
            return remaining, None
        executable = Path(remaining[0]).name.casefold()
        if executable in {"bash", "sh", "zsh"}:
            command_index = next(
                (
                    index
                    for index, option in enumerate(remaining[1:], start=1)
                    if option == "-c"
                    or (option.startswith("-") and not option.startswith("--") and "c" in option[1:])
                ),
                None,
            )
            if command_index is not None and len(remaining) > command_index + 1:
                return remaining, remaining[command_index + 1]
            return remaining, None
        if executable in {"env", "sudo", "time", "command", "nohup", "xargs"}:
            remaining.pop(0)
            option_arguments = {
                "env": {"-C", "--chdir", "-S", "--split-string", "-u", "--unset"},
                "sudo": {"-C", "--close-from", "-g", "--group", "-h", "--host", "-p", "--prompt", "-u", "--user"},
                "xargs": {"-a", "--arg-file", "-E", "--eof", "-I", "--replace", "-n", "--max-args", "-P", "--max-procs", "-s", "--max-chars"},
            }.get(executable, set())
            while remaining:
                option = remaining[0]
                if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", option):
                    remaining.pop(0)
                    continue
                if option == "--":
                    remaining.pop(0)
                    break
                if not option.startswith("-"):
                    break
                remaining.pop(0)
                if option in option_arguments and remaining:
                    remaining.pop(0)
            continue
        if executable == "timeout":
            remaining.pop(0)
            while remaining and remaining[0].startswith("-"):
                option = remaining.pop(0)
                if option in {"-k", "--kill-after", "-s", "--signal"} and remaining:
                    remaining.pop(0)
            if remaining:
                remaining.pop(0)
            continue
        if executable == "uv" and len(remaining) > 1 and remaining[1] == "run":
            remaining = remaining[2:]
            option_arguments = {
                "--directory",
                "--env-file",
                "--index",
                "--python",
                "--with",
                "--with-editable",
                "--with-requirements",
            }
            while remaining and remaining[0].startswith("-"):
                option = remaining.pop(0)
                if option in option_arguments and remaining:
                    remaining.pop(0)
            continue
        break
    return remaining, None


def redirection_category(tokens: list[str]) -> str | None:
    input_redirection = False
    for index, token in enumerate(tokens):
        if token in {"&>", "&>>", ">|"}:
            return "mutation"
        if not token or not set(token) <= {">", "<", "&"}:
            continue
        previous = tokens[index - 1] if index else ""
        target = tokens[index + 1] if index + 1 < len(tokens) else ""
        if previous == "2" and target in {"&1", "1", "/dev/null", "/dev/stderr"}:
            continue
        if ">" in token:
            return "mutation"
        if "<" in token:
            input_redirection = True
    return "direct-read" if input_redirection else None


def simple_command_category(tokens: list[str]) -> str | None:
    redirection = redirection_category(tokens)
    if redirection:
        return redirection
    tokens, nested_command = unwrap_command(tokens)
    if nested_command is not None:
        nested = command_categories(nested_command)
        return nested[0] if nested else None
    if not tokens:
        return None
    executable_raw = Path(tokens[0]).name
    executable = snake_identifier(executable_raw)
    lowered = [snake_identifier(token) for token in tokens]
    namespaced = tool_category(executable_raw)
    parts = identifier_parts(executable_raw)
    has_graph_namespace = any("codebase_memory" in part for part in parts[:-1]) or "serena" in parts[:-1]
    if namespaced == "graph" and has_graph_namespace:
        return "graph"
    if executable in {"codebase_memory_mcp", "codebase_memory"} and len(lowered) > 1:
        if lowered[1] in CODEBASE_GRAPH_ACTIONS:
            return "graph"
    if executable == "serena" and len(lowered) > 1:
        action_category = tool_category(f"serena.{lowered[1]}")
        if action_category:
            return action_category
    if executable == "git" and len(lowered) > 1:
        action_index = 1
        while action_index < len(lowered) and lowered[action_index].startswith("_"):
            option = lowered[action_index]
            action_index += 2 if option in {"_c", "_git_dir", "_work_tree"} else 1
        action = lowered[action_index] if action_index < len(lowered) else ""
        if action in {"checkout", "clean", "commit", "merge", "mv", "rebase", "reset", "restore", "switch"}:
            return "mutation"
        if action in {"grep", "log"}:
            return "text-search"
        if action in {"cat_file", "diff", "show"}:
            return "direct-read"
    if executable == "find" and any(token in {"_delete", "_exec", "_execdir"} for token in lowered[1:]):
        return "mutation"
    if executable in MUTATION_COMMANDS or executable == "tee":
        return "mutation"
    if executable in DIRECT_READ_COMMANDS or executable in INTERPRETER_COMMANDS:
        return "direct-read"
    if executable in TEXT_SEARCH_COMMANDS:
        return "text-search"
    return None


def command_categories(command: str, depth: int = 0) -> list[str]:
    if depth >= MAX_NESTED_SHELL_DEPTH:
        return ["unverified"]
    categories = ["unverified"] if any(marker in command for marker in SUSPICIOUS_SHELL_SYNTAX) else []
    for segment in shell_segments(command):
        outer_redirection = redirection_category(segment)
        _, nested_command = unwrap_command(segment)
        if nested_command is not None:
            if outer_redirection:
                categories.append(outer_redirection)
            nested_categories = command_categories(nested_command, depth + 1)
            categories.extend(nested_categories or ["unverified"])
            continue
        category = simple_command_category(segment)
        categories.append(category or "unverified")
    return categories


def classify_event(event: dict[str, Any], position: int, sequence: int) -> dict[str, Any]:
    observed = []
    field_kinds = []
    shell_tool_seen = False
    command_seen = False
    for kind, value in event_fields(event):
        field_kinds.append(kind)
        if kind == "tool":
            shell_tool_seen = shell_tool_seen or is_shell_tool(value)
            category = tool_category(value)
            if category:
                observed.append(category)
            elif not is_shell_tool(value) and not is_irrelevant_tool(value):
                observed.append("unverified")
        else:
            command_seen = True
            categories = command_categories(value)
            observed.extend(categories or ["unverified"])
    if shell_tool_seen and not command_seen:
        observed.append("unverified")
    observed = list(dict.fromkeys(observed))
    category = next((candidate for candidate in CATEGORY_PRIORITY if candidate in observed), "other")
    return {
        "sequence": sequence,
        "position": position,
        "category": category,
        "observedCategories": observed,
        "fieldKinds": list(dict.fromkeys(field_kinds)),
    }


def validated_sequences(events: list[dict[str, Any]]) -> tuple[list[int] | None, str | None]:
    present = ["sequence" in event for event in events]
    if any(present) and not all(present):
        return None, "sequence deve existir em todos os eventos ou em nenhum"
    if not any(present):
        return list(range(1, len(events) + 1)), None
    values = [event["sequence"] for event in events]
    if not all(isinstance(value, int) and not isinstance(value, bool) and value >= 0 for value in values):
        return None, "sequence deve ser inteiro não negativo"
    if len(set(values)) != len(values):
        return None, "sequence deve ser única"
    return values, None


def audit_trace(payload: Any) -> tuple[dict[str, Any], int]:
    if not isinstance(payload, dict) or payload.get("schemaVersion") != TRACE_SCHEMA_VERSION:
        return {"status": "invalid-trace", "reason": "schemaVersion incompatível"}, 2
    events = payload.get("events")
    if not isinstance(events, list):
        return {"status": "invalid-trace", "reason": "events deve ser uma lista"}, 2
    if not all(isinstance(event, dict) for event in events):
        return {"status": "invalid-trace", "reason": "cada evento deve ser um objeto"}, 2
    sequences, sequence_error = validated_sequences(events)
    if sequence_error or sequences is None:
        return {"status": "invalid-trace", "reason": sequence_error}, 2
    try:
        classified = [
            classify_event(event, index, sequences[index]) for index, event in enumerate(events)
        ]
    except ValueError:
        return {"status": "invalid-trace", "reason": "campo canônico inválido"}, 2
    if any(not event["fieldKinds"] for event in classified):
        return {"status": "invalid-trace", "reason": "evento sem campo canônico reconhecido"}, 2
    classified.sort(key=lambda event: (event["sequence"], event["position"]))
    relevant = [event for event in classified if event["category"] != "other"]
    graph = next((event for event in relevant if "graph" in event["observedCategories"]), None)
    first = relevant[0] if relevant else None
    categories = ("graph", "text-search", "direct-read", "mutation", "unverified", "other")
    counts = {
        category: sum(
            event["category"] == "other"
            if category == "other"
            else category in event["observedCategories"]
            for event in classified
        )
        for category in categories
    }
    if graph is None:
        status, reason, exit_code = "not-observed", "nenhum evento de grafo/índice foi observado", 1
    elif first and first["category"] == "graph":
        status, reason, exit_code = "pass", "o primeiro acesso relevante foi grafo/índice", 0
    else:
        status, reason, exit_code = "fail", "um acesso relevante ocorreu antes do primeiro grafo/índice", 1
    return {
        "status": status,
        "reason": reason,
        "eventCount": len(classified),
        "counts": counts,
        "firstRelevant": first,
        "firstGraph": graph,
    }, exit_code


def reject_nonstandard_number(value: str) -> None:
    raise ValueError(f"número JSON inválido: {value}")


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("chave JSON duplicada")
        result[key] = value
    return result


def safe_input_error(error: Exception) -> str:
    if isinstance(error, OSError):
        return "não foi possível ler o trace"
    if isinstance(error, UnicodeDecodeError):
        return "trace não é UTF-8 válido"
    if isinstance(error, json.JSONDecodeError):
        return "JSON inválido"
    if isinstance(error, RecursionError):
        return "estrutura JSON profunda demais"
    return "trace inválido"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace", help="arquivo JSON v1 com events[]")
    args = parser.parse_args()
    try:
        path = Path(args.trace).expanduser()
        metadata = path.stat()
        if not stat.S_ISREG(metadata.st_mode):
            raise ValueError("trace deve ser arquivo regular")
        if metadata.st_size > MAX_TRACE_BYTES:
            raise ValueError(f"trace excede {MAX_TRACE_BYTES} bytes")
        payload = json.loads(
            path.read_text(encoding="utf-8"),
            parse_constant=reject_nonstandard_number,
            object_pairs_hook=reject_duplicate_keys,
        )
    except (
        OSError,
        UnicodeDecodeError,
        json.JSONDecodeError,
        ValueError,
        RecursionError,
        RuntimeError,
    ) as error:
        result = {"status": "invalid-trace", "reason": safe_input_error(error)}
        print(json.dumps(result, ensure_ascii=True))
        return 2
    result, exit_code = audit_trace(payload)
    print(json.dumps(result, ensure_ascii=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
