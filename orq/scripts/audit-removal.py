#!/usr/bin/env python3
"""Cria e verifica ledgers offline de remoção de código/configuração."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import fnmatch
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
from typing import Any, Iterable


SCHEMA_VERSION = "orq.audit-removal.v1"
MAX_TEXT_BYTES = 2 * 1024 * 1024
DEFAULT_EXCLUSIONS = (
    ".git",
    ".codebase-memory",
    ".next",
    ".venv",
    "build",
    "coverage",
    "dist",
    "memory/audits",
    "node_modules",
    "vendor",
    "venv",
)


class AuditInputError(ValueError):
    """Entrada inválida que deve produzir exit code 2."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def target_variants(target: str) -> list[str]:
    raw = target.strip()
    if not raw:
        raise AuditInputError("o alvo não pode ser vazio")
    words = re.findall(r"[A-Za-z0-9]+", raw)
    candidates = [raw]
    if words:
        lower = [word.lower() for word in words]
        candidates.extend(
            [
                "-".join(lower),
                "_".join(lower),
                "_".join(lower).upper(),
                " ".join(lower),
                lower[0] + "".join(word.title() for word in lower[1:]),
                "".join(word.title() for word in lower),
            ]
        )
    return list(dict.fromkeys(item for item in candidates if item))


def normalized_relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def path_matches(relative: str, patterns: Iterable[str]) -> bool:
    folded_relative = relative.casefold()
    folded_parts = tuple(part.casefold() for part in Path(relative).parts)
    for raw_pattern in patterns:
        pattern = raw_pattern.strip().replace("\\", "/").strip("/")
        if not pattern:
            continue
        folded_pattern = pattern.casefold()
        if "/" not in pattern and not any(char in pattern for char in "*?["):
            if folded_pattern in folded_parts:
                return True
        if folded_relative == folded_pattern or folded_relative.startswith(folded_pattern + "/"):
            return True
        if fnmatch.fnmatch(folded_relative, folded_pattern):
            return True
    return False


def should_prune(relative: str, exclusions: Iterable[str], ledger_relative: str | None) -> bool:
    if ledger_relative and relative == ledger_relative:
        return True
    return path_matches(relative, exclusions)


def first_variant(text: str, variants: list[str]) -> tuple[str, int] | None:
    folded = text.casefold()
    matches = ((variant, folded.find(variant.casefold())) for variant in variants)
    found = [(variant, index) for variant, index in matches if index >= 0]
    if not found:
        return None
    variant, index = min(found, key=lambda item: (item[1], -len(item[0])))
    return variant, index + 1


def encoded_variants(variants: list[str]) -> list[tuple[str, bytes]]:
    encoded: list[tuple[str, bytes]] = []
    for variant in variants:
        for encoding in ("utf-8", "latin-1", "utf-16-le", "utf-16-be", "utf-32-le", "utf-32-be"):
            try:
                value = variant.encode(encoding).lower()
            except UnicodeEncodeError:
                continue
            if value and (variant, value) not in encoded:
                encoded.append((variant, value))
    return encoded


def first_variant_bytes(raw: bytes, variants: list[str]) -> tuple[str, int] | None:
    lowered = raw.lower()
    found = []
    for variant, encoded in encoded_variants(variants):
        index = lowered.find(encoded)
        if index >= 0:
            found.append((variant, index))
    if not found:
        return None
    variant, index = min(found, key=lambda item: (item[1], -len(item[0])))
    return variant, index + 1


def first_variant_in_large_file(path: Path, variants: list[str]) -> tuple[str, int] | None:
    candidates = encoded_variants(variants)
    overlap = max((len(value) for _, value in candidates), default=1) - 1
    tail = b""
    offset = 0
    with path.open("rb") as handle:
        while chunk := handle.read(64 * 1024):
            combined = tail + chunk
            lowered = combined.lower()
            found = []
            for variant, encoded in candidates:
                index = lowered.find(encoded)
                if index >= 0:
                    found.append((variant, offset - len(tail) + index))
            if found:
                variant, index = min(found, key=lambda item: (item[1], -len(item[0])))
                return variant, index + 1
            offset += len(chunk)
            tail = combined[-overlap:] if overlap else b""
    return None


def scan_repository(
    root: Path,
    variants: list[str],
    exclusions: list[str],
    retained: list[str],
    ledger_path: Path | None,
) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    ledger_relative: str | None = None
    if ledger_path is not None:
        try:
            ledger_relative = normalized_relative(root, ledger_path.resolve())
        except ValueError:
            ledger_relative = None

    def record_walk_error(error: OSError) -> None:
        raw_path = getattr(error, "filename", None)
        try:
            relative = normalized_relative(root, Path(raw_path).resolve()) if raw_path else "."
        except (OSError, ValueError):
            relative = "."
        evidence.append(
            {
                "path": relative,
                "line": None,
                "column": None,
                "match": variants[0],
                "class": "directory-unreadable",
                "status": "ambiguous",
            }
        )

    for current, directories, filenames in os.walk(
        root, topdown=True, followlinks=False, onerror=record_walk_error
    ):
        current_path = Path(current)
        kept_directories = []
        for directory in directories:
            candidate = current_path / directory
            relative = normalized_relative(root, candidate)
            if should_prune(relative, exclusions, ledger_relative):
                continue
            if candidate.is_symlink():
                evidence.append(
                    {
                        "path": relative,
                        "line": None,
                        "column": None,
                        "match": variants[0],
                        "class": "symlink",
                        "status": "ambiguous",
                    }
                )
            else:
                kept_directories.append(directory)
        directories[:] = kept_directories

        for filename in filenames:
            path = current_path / filename
            relative = normalized_relative(root, path)
            if should_prune(relative, exclusions, ledger_relative):
                continue
            if path.is_symlink():
                evidence.append(
                    {
                        "path": relative,
                        "line": None,
                        "column": None,
                        "match": variants[0],
                        "class": "symlink",
                        "status": "ambiguous",
                    }
                )
                continue
            path_hit = first_variant(relative, variants)
            try:
                metadata = path.lstat()
                if not stat.S_ISREG(metadata.st_mode):
                    evidence.append(
                        {
                            "path": relative,
                            "line": None,
                            "column": path_hit[1] if path_hit else None,
                            "match": path_hit[0] if path_hit else variants[0],
                            "class": "non-regular",
                            "status": "ambiguous",
                        }
                    )
                    continue
                if metadata.st_size > MAX_TEXT_BYTES:
                    content_hit = first_variant_in_large_file(path, variants)
                    if path_hit or content_hit:
                        hit = content_hit or path_hit
                        evidence.append(
                            {
                                "path": relative,
                                "line": None,
                                "column": hit[1],
                                "match": hit[0],
                                "class": "content-large-file" if content_hit else "path-large-file",
                                "status": "ambiguous",
                            }
                        )
                    continue
                raw = path.read_bytes()
                bom_encoding = None
                if raw.startswith((b"\xff\xfe\x00\x00", b"\x00\x00\xfe\xff")):
                    bom_encoding = "utf-32"
                elif raw.startswith((b"\xff\xfe", b"\xfe\xff")):
                    bom_encoding = "utf-16"
                if bom_encoding:
                    try:
                        content = raw.decode(bom_encoding)
                    except UnicodeDecodeError:
                        evidence.append(
                            {
                                "path": relative,
                                "line": None,
                                "column": None,
                                "match": variants[0],
                                "class": f"content-{bom_encoding}-invalid",
                                "status": "ambiguous",
                            }
                        )
                        continue
                    content_found = False
                    for number, line in enumerate(content.splitlines(), start=1):
                        hit = first_variant(line, variants)
                        if not hit:
                            continue
                        content_found = True
                        evidence.append(
                            {
                                "path": relative,
                                "line": number,
                                "column": hit[1],
                                "match": hit[0],
                                "class": f"content-{bom_encoding.replace('-', '')}",
                                "status": "retained-historical"
                                if path_matches(relative, retained)
                                else "active",
                            }
                        )
                    if path_hit and not content_found:
                        evidence.append(
                            {
                                "path": relative,
                                "line": None,
                                "column": path_hit[1],
                                "match": path_hit[0],
                                "class": "path",
                                "status": "retained-historical"
                                if path_matches(relative, retained)
                                else "active",
                            }
                        )
                    continue
                if b"\x00" in raw:
                    content_hit = first_variant_bytes(raw, variants)
                    if path_hit or content_hit:
                        hit = content_hit or path_hit
                        evidence.append(
                            {
                                "path": relative,
                                "line": None,
                                "column": hit[1],
                                "match": hit[0],
                                "class": "content-binary" if content_hit else "path-binary",
                                "status": "ambiguous",
                            }
                        )
                    continue
                try:
                    content = raw.decode("utf-8")
                except UnicodeDecodeError:
                    content_hit = first_variant_bytes(raw, variants)
                    if path_hit or content_hit:
                        hit = content_hit or path_hit
                        evidence.append(
                            {
                                "path": relative,
                                "line": None,
                                "column": hit[1],
                                "match": hit[0],
                                "class": "content-non-utf8" if content_hit else "path-unreadable",
                                "status": "ambiguous",
                            }
                        )
                    continue
            except OSError:
                evidence.append(
                    {
                        "path": relative,
                        "line": None,
                        "column": path_hit[1] if path_hit else None,
                        "match": path_hit[0] if path_hit else variants[0],
                        "class": "path-unreadable",
                        "status": "ambiguous",
                    }
                )
                continue

            for number, line in enumerate(content.splitlines(), start=1):
                hit = first_variant(line, variants)
                if not hit:
                    continue
                evidence.append(
                    {
                        "path": relative,
                        "line": number,
                        "column": hit[1],
                        "match": hit[0],
                        "class": "content",
                        "status": "retained-historical" if path_matches(relative, retained) else "active",
                    }
                )
            if path_hit and not first_variant(content, variants):
                evidence.append(
                    {
                        "path": relative,
                        "line": None,
                        "column": path_hit[1],
                        "match": path_hit[0],
                        "class": "path",
                        "status": "retained-historical" if path_matches(relative, retained) else "active",
                    }
                )
    return sorted(evidence, key=lambda item: (item["path"], item["line"] or 0, item["column"] or 0))


def run_git(root: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            text=True,
            capture_output=True,
            timeout=3,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def repository_state(root: Path) -> dict[str, Any]:
    commit = run_git(root, "rev-parse", "HEAD")
    status = run_git(root, "status", "--porcelain=v1")
    return {
        "root": str(root),
        "commit": commit,
        "dirty": None if status is None else bool(status),
    }


def safe_relative_path(root: Path, raw: str, label: str) -> tuple[str, Path]:
    portable = raw.replace("\\", "/")
    if portable.startswith("/") or re.match(r"^[A-Za-z]:/", portable):
        raise AuditInputError(f"{label} deve permanecer dentro da raiz: {raw!r}")
    normalized = portable.strip("/")
    candidate = Path(normalized)
    if not normalized or candidate.is_absolute() or ".." in candidate.parts:
        raise AuditInputError(f"{label} deve permanecer dentro da raiz: {raw!r}")
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as error:
        raise AuditInputError(f"{label} deve permanecer dentro da raiz: {raw!r}") from error
    return normalized, resolved


def critical_anchor_states(root: Path, critical: list[str]) -> list[dict[str, Any]]:
    states = []
    for relative in critical:
        normalized, resolved = safe_relative_path(root, relative, "critical anchor")
        states.append({"path": normalized, "exists": resolved.exists()})
    return states


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def ledger_path_for_root(root: Path, raw: str) -> Path:
    path = Path(raw).expanduser().resolve()
    try:
        path.relative_to(root)
    except ValueError as error:
        raise AuditInputError("ledger deve permanecer dentro da raiz") from error
    if path == root or (path.exists() and not path.is_file()):
        raise AuditInputError("ledger deve apontar para arquivo regular dentro da raiz")
    return path


def build_ledger(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        raise AuditInputError(f"raiz inexistente: {root}")
    ledger_path = ledger_path_for_root(root, args.ledger)
    variants = target_variants(args.target)
    exclusions = list(dict.fromkeys([*DEFAULT_EXCLUSIONS, *normalized_list(args.exclude)]))
    retained = normalized_list(args.retain)
    critical_paths = list(
        dict.fromkeys(safe_relative_path(root, value, "critical anchor")[0] for value in args.critical)
    )
    required = list(dict.fromkeys(args.require))
    evidence = scan_repository(root, variants, exclusions, retained, ledger_path)
    critical = critical_anchor_states(root, critical_paths)
    blockers = [item for item in evidence if item["status"] in {"active", "ambiguous"}]
    missing_critical = [item["path"] for item in critical if not item["exists"]]
    status = "needs-removal" if blockers else "needs-verification"
    ledger = {
        "schemaVersion": SCHEMA_VERSION,
        "audit": "removal",
        "createdAt": utc_now(),
        "updatedAt": utc_now(),
        "target": {"raw": args.target, "variants": variants},
        "repository": repository_state(root),
        "exclusions": exclusions,
        "retainedPaths": retained,
        "criticalAnchors": critical,
        "requiredValidations": required,
        "validationReceipts": [],
        "graphReceipts": parse_graph_receipts(args.graph_receipt),
        "evidence": evidence,
        "verification": {
            "status": status,
            "checkedAt": utc_now(),
            "blockingEvidence": len(blockers),
            "missingCriticalAnchors": missing_critical,
            "missingReceipts": required,
        },
    }
    write_json(ledger_path, ledger)
    summary = {
        "status": status,
        "ledger": str(ledger_path),
        "evidence": len(evidence),
        "blockingEvidence": len(blockers),
        "missingCriticalAnchors": missing_critical,
    }
    print(json.dumps(summary, ensure_ascii=True))
    return ledger, 1 if blockers or missing_critical or required else 0


def parse_receipts(values: list[str]) -> dict[str, str]:
    receipts: dict[str, str] = {}
    for raw in values:
        if "=" not in raw:
            raise AuditInputError(f"recibo inválido: {raw!r}; use NOME=pass|fail")
        name, result = raw.split("=", 1)
        name, result = name.strip(), result.strip().lower()
        if not name or result not in {"pass", "fail"}:
            raise AuditInputError(f"recibo inválido: {raw!r}; use NOME=pass|fail")
        if name in receipts:
            raise AuditInputError(f"recibo duplicado: {name!r}")
        receipts[name] = result
    return receipts


def parse_graph_receipts(values: list[str]) -> list[dict[str, str]]:
    receipts = []
    for raw in values:
        if "=" not in raw:
            raise AuditInputError(f"recibo de grafo inválido: {raw!r}; use FERRAMENTA=CONSULTA")
        tool, query = raw.split("=", 1)
        tool, query = tool.strip(), query.strip()
        if not tool or not query:
            raise AuditInputError(f"recibo de grafo inválido: {raw!r}; use FERRAMENTA=CONSULTA")
        receipts.append({"tool": tool, "query": query, "recordedAt": utc_now()})
    return receipts


def load_ledger(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise AuditInputError(f"INVALID_LEDGER: {error}") from error
    required = {
        "schemaVersion", "audit", "createdAt", "updatedAt", "target", "repository",
        "exclusions", "retainedPaths", "criticalAnchors", "requiredValidations",
        "validationReceipts", "graphReceipts", "evidence", "verification",
    }
    if not isinstance(payload, dict) or payload.get("schemaVersion") != SCHEMA_VERSION:
        raise AuditInputError("INVALID_LEDGER: schemaVersion incompatível")
    if not required.issubset(payload):
        raise AuditInputError("INVALID_LEDGER: campos obrigatórios ausentes")
    target = payload.get("target")
    repository = payload.get("repository")
    verification = payload.get("verification")
    if not isinstance(target, dict) or not isinstance(target.get("raw"), str):
        raise AuditInputError("INVALID_LEDGER: target inválido")
    if not isinstance(target.get("variants"), list) or not all(
        isinstance(item, str) for item in target["variants"]
    ):
        raise AuditInputError("INVALID_LEDGER: target.variants inválido")
    if not isinstance(repository, dict) or not isinstance(repository.get("root"), str):
        raise AuditInputError("INVALID_LEDGER: repository inválido")
    list_fields = (
        "exclusions", "retainedPaths", "criticalAnchors", "requiredValidations",
        "validationReceipts", "graphReceipts", "evidence",
    )
    if any(not isinstance(payload.get(field), list) for field in list_fields):
        raise AuditInputError("INVALID_LEDGER: campo de lista inválido")
    if not all(isinstance(item, str) for item in payload["exclusions"] + payload["retainedPaths"]):
        raise AuditInputError("INVALID_LEDGER: exclusões/históricos inválidos")
    if not all(isinstance(item, str) for item in payload["requiredValidations"]):
        raise AuditInputError("INVALID_LEDGER: validações obrigatórias inválidas")
    if not all(
        isinstance(item, dict) and isinstance(item.get("path"), str) and isinstance(item.get("exists"), bool)
        for item in payload["criticalAnchors"]
    ):
        raise AuditInputError("INVALID_LEDGER: criticalAnchors inválido")
    evidence_fields = {"path", "line", "column", "match", "class", "status"}
    valid_statuses = {"active", "retained-historical", "removed", "ambiguous"}
    if not all(
        isinstance(item, dict)
        and evidence_fields.issubset(item)
        and isinstance(item.get("path"), str)
        and isinstance(item.get("match"), str)
        and isinstance(item.get("class"), str)
        and item.get("status") in valid_statuses
        and (item.get("line") is None or isinstance(item.get("line"), int))
        and (item.get("column") is None or isinstance(item.get("column"), int))
        for item in payload["evidence"]
    ):
        raise AuditInputError("INVALID_LEDGER: evidence inválido")
    if not isinstance(verification, dict) or not isinstance(verification.get("status"), str):
        raise AuditInputError("INVALID_LEDGER: verification inválido")
    return payload


def evidence_key(item: dict[str, Any]) -> tuple[Any, ...]:
    return item.get("path"), item.get("line"), item.get("match"), item.get("class")


def normalized_list(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value.replace("\\", "/").strip("/") for value in values))


def assert_scope_matches(args: argparse.Namespace, ledger: dict[str, Any]) -> tuple[Path, list[str], list[str]]:
    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        raise AuditInputError(f"raiz inexistente: {root}")
    variants = target_variants(args.target)
    exclusions = list(dict.fromkeys([*DEFAULT_EXCLUSIONS, *normalized_list(args.exclude)]))
    retained = normalized_list(args.retain)
    critical = list(
        dict.fromkeys(safe_relative_path(root, value, "critical anchor")[0] for value in args.critical)
    )
    required = list(dict.fromkeys(args.require))
    recorded_critical = [item["path"] for item in ledger["criticalAnchors"]]
    comparisons = {
        "repository.root": (str(root), ledger["repository"]["root"]),
        "target.raw": (args.target, ledger["target"]["raw"]),
        "target.variants": (variants, ledger["target"]["variants"]),
        "exclusions": (exclusions, ledger["exclusions"]),
        "retainedPaths": (retained, ledger["retainedPaths"]),
        "criticalAnchors": (critical, recorded_critical),
        "requiredValidations": (required, ledger["requiredValidations"]),
    }
    mismatches = [name for name, (expected, recorded) in comparisons.items() if expected != recorded]
    if mismatches:
        raise AuditInputError("SCOPE_MISMATCH: " + ", ".join(mismatches))
    critical_anchor_states(root, critical)
    return root, exclusions, retained


def verify_ledger(args: argparse.Namespace) -> int:
    requested_root = Path(args.root).expanduser().resolve()
    if not requested_root.is_dir():
        raise AuditInputError(f"raiz inexistente: {requested_root}")
    ledger_path = ledger_path_for_root(requested_root, args.ledger)
    ledger = load_ledger(ledger_path)
    root, exclusions, retained = assert_scope_matches(args, ledger)
    variants = target_variants(args.target)
    current = scan_repository(
        root,
        variants,
        exclusions,
        retained,
        ledger_path,
    )
    current_keys = {evidence_key(item) for item in current}
    removed = []
    for old in ledger.get("evidence", []):
        if evidence_key(old) in current_keys:
            continue
        if old.get("status") == "removed":
            removed.append(dict(old))
        elif old.get("status") in {"active", "ambiguous", "retained-historical"}:
            retired = dict(old)
            retired["status"] = "removed"
            removed.append(retired)
    evidence = current + removed
    critical_paths = normalized_list(args.critical)
    critical = critical_anchor_states(root, critical_paths)
    receipts = parse_receipts(args.receipt)
    required = list(dict.fromkeys(args.require))
    missing_receipts = [name for name in required if name not in receipts]
    failed_receipts = [name for name in required if receipts.get(name) == "fail"]
    missing_critical = [item["path"] for item in critical if not item["exists"]]
    blockers = [item for item in current if item["status"] in {"active", "ambiguous"}]
    status = "pass" if not blockers and not missing_critical and not missing_receipts and not failed_receipts else "fail"
    ledger["repository"] = repository_state(root)
    ledger["criticalAnchors"] = critical
    ledger["validationReceipts"] = [
        {"name": name, "status": receipts[name], "recordedAt": utc_now()} for name in sorted(receipts)
    ]
    ledger["evidence"] = sorted(
        evidence, key=lambda item: (item["path"], item["line"] or 0, item["column"] or 0, item["status"])
    )
    ledger["updatedAt"] = utc_now()
    ledger["verification"] = {
        "status": status,
        "checkedAt": utc_now(),
        "blockingEvidence": len(blockers),
        "missingCriticalAnchors": missing_critical,
        "missingReceipts": missing_receipts,
        "failedReceipts": failed_receipts,
    }
    write_json(ledger_path, ledger)
    summary = {
        "status": status,
        "ledger": str(ledger_path),
        "blockingEvidence": len(blockers),
        "missingCriticalAnchors": missing_critical,
        "missingReceipts": missing_receipts,
        "failedReceipts": failed_receipts,
    }
    print(json.dumps(summary, ensure_ascii=True))
    return 0 if status == "pass" else 1


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    subcommands = root.add_subparsers(dest="command", required=True)
    scan = subcommands.add_parser("scan", help="escaneia e cria um ledger")
    scan.add_argument("--root", required=True)
    scan.add_argument("--target", required=True)
    scan.add_argument("--ledger", required=True)
    scan.add_argument("--retain", action="append", default=[])
    scan.add_argument("--critical", action="append", default=[])
    scan.add_argument("--require", action="append", default=[])
    scan.add_argument("--exclude", action="append", default=[])
    scan.add_argument("--graph-receipt", action="append", default=[])
    verify = subcommands.add_parser("verify", help="reescaneia e verifica um ledger")
    verify.add_argument("--ledger", required=True)
    verify.add_argument("--root", required=True)
    verify.add_argument("--target", required=True)
    verify.add_argument("--retain", action="append", default=[])
    verify.add_argument("--critical", action="append", default=[])
    verify.add_argument("--require", action="append", default=[])
    verify.add_argument("--exclude", action="append", default=[])
    verify.add_argument("--receipt", action="append", default=[])
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        if args.command == "scan":
            _, exit_code = build_ledger(args)
            return exit_code
        return verify_ledger(args)
    except AuditInputError as error:
        print(str(error), file=sys.stderr)
        return 2
    except OSError:
        print("AUDIT_IO_ERROR: operação de arquivo falhou", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
