#!/usr/bin/env python3
"""Strictly compare an Orquestra source tree with an installed host cache."""

from __future__ import annotations

import argparse
import os
import stat
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Literal, Sequence

Host = Literal["claude", "codex"]
Kind = Literal["missing", "extra", "type", "bytes"]


@dataclass(frozen=True)
class Divergence:
    """One deterministic difference between source and installed trees."""

    kind: Kind
    path: str
    detail: str = ""


@dataclass(frozen=True)
class _Entry:
    kind: str
    payload: bytes | str | None = None


def _entry_kind(mode: int) -> str:
    if stat.S_ISREG(mode):
        return "file"
    if stat.S_ISDIR(mode):
        return "directory"
    if stat.S_ISLNK(mode):
        return "symlink"
    return "other"


def _is_allowed_installed_metadata(
    relative: PurePosixPath,
    kind: str,
    host: Host,
) -> bool:
    parts = relative.parts
    if host == "claude":
        return (
            parts == (".in_use",) and kind in {"file", "directory"}
        ) or (parts == (".orphaned_at",) and kind == "file")
    return (
        parts == (".codex-plugin", "migrated-command-skills")
        and kind == "directory"
    )


def _read_regular_file(path: Path) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        with os.fdopen(descriptor, "rb", closefd=False) as handle:
            return handle.read()
    finally:
        os.close(descriptor)


def _walk_tree(
    root: Path,
    *,
    host: Host,
    installed: bool,
) -> tuple[dict[str, _Entry], set[str]]:
    try:
        root_mode = root.lstat().st_mode
    except OSError as exc:
        raise OSError(f"cannot inspect root {root}: {exc}") from exc
    if not stat.S_ISDIR(root_mode):
        raise OSError(f"root is not a directory: {root}")

    found: dict[str, _Entry] = {}
    allowed_ancestors: set[str] = set()

    def visit(directory: Path, prefix: PurePosixPath | None = None) -> None:
        try:
            with os.scandir(directory) as iterator:
                entries = sorted(iterator, key=lambda item: item.name)
        except OSError as exc:
            raise OSError(f"cannot read directory {directory}: {exc}") from exc

        for entry in entries:
            relative = (
                PurePosixPath(entry.name)
                if prefix is None
                else prefix / entry.name
            )
            try:
                mode = entry.stat(follow_symlinks=False).st_mode
            except OSError as exc:
                raise OSError(f"cannot inspect {entry.path}: {exc}") from exc
            kind = _entry_kind(mode)

            if installed and _is_allowed_installed_metadata(relative, kind, host):
                ancestor = relative.parent
                while ancestor != PurePosixPath("."):
                    allowed_ancestors.add(ancestor.as_posix())
                    ancestor = ancestor.parent
                continue

            relative_text = relative.as_posix()
            path = Path(entry.path)
            if kind == "file":
                payload: bytes | str | None = _read_regular_file(path)
            elif kind == "symlink":
                payload = os.readlink(path)
            else:
                payload = None
            found[relative_text] = _Entry(kind=kind, payload=payload)

            if kind == "directory":
                visit(path, relative)

    visit(root)
    return found, allowed_ancestors


def find_installation_divergences(
    source: Path,
    installed: Path,
    host: Host,
) -> list[Divergence]:
    """Compare entry types and bytes without following symlinks."""

    if host not in {"claude", "codex"}:
        raise ValueError(f"unsupported host: {host}")

    source_entries, _ = _walk_tree(Path(source), host=host, installed=False)
    installed_entries, allowed_ancestors = _walk_tree(
        Path(installed),
        host=host,
        installed=True,
    )

    # O Codex pode criar o diretório-pai apenas para abrigar a subárvore
    # allowlisted. O pai é metadado implícito somente quando a fonte não o tem e
    # um descendente permitido foi realmente observado; diretório vazio ou
    # outros filhos continuam aparecendo como divergência.
    for ancestor in sorted(allowed_ancestors, reverse=True):
        installed_entry = installed_entries.get(ancestor)
        descendant_prefix = f"{ancestor}/"
        has_visible_descendant = any(
            path.startswith(descendant_prefix) for path in installed_entries
        )
        if (
            ancestor not in source_entries
            and installed_entry is not None
            and installed_entry.kind == "directory"
            and not has_visible_descendant
        ):
            installed_entries.pop(ancestor)
    divergences: list[Divergence] = []

    for path in sorted(source_entries.keys() | installed_entries.keys()):
        source_entry = source_entries.get(path)
        installed_entry = installed_entries.get(path)
        if source_entry is None:
            divergences.append(Divergence("extra", path))
            continue
        if installed_entry is None:
            divergences.append(Divergence("missing", path))
            continue
        if source_entry.kind != installed_entry.kind:
            divergences.append(
                Divergence(
                    "type",
                    path,
                    f"source={source_entry.kind}, installed={installed_entry.kind}",
                )
            )
            continue
        if source_entry.kind == "other":
            divergences.append(
                Divergence("type", path, "unsupported entry type: other")
            )
            continue
        if source_entry.payload != installed_entry.payload:
            detail = (
                "symlink target differs"
                if source_entry.kind == "symlink"
                else ""
            )
            divergences.append(Divergence("bytes", path, detail))

    return divergences


class _ArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise ValueError(message)


def _parser() -> argparse.ArgumentParser:
    parser = _ArgumentParser(
        description="Compare an Orquestra source tree with an installed cache.",
    )
    parser.add_argument("--host", required=True, choices=("claude", "codex"))
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--installed", required=True, type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = _parser().parse_args(argv)
        divergences = find_installation_divergences(
            args.source,
            args.installed,
            args.host,
        )
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if divergences:
        for divergence in divergences:
            suffix = f" ({divergence.detail})" if divergence.detail else ""
            print(f"{divergence.kind}: {divergence.path}{suffix}")
        return 1

    print(f"ok: installed cache matches source (host={args.host})")
    return 0


__all__ = ["Divergence", "find_installation_divergences", "main"]


if __name__ == "__main__":
    raise SystemExit(main())
