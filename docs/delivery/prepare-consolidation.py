#!/usr/bin/env python3
"""Prepara união determinística local; stdout é plano para apply_patch, nunca egress."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile


def git(root, *args):
    result = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr)
    return result.stdout


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--base", default="4e58e7f")
    parser.add_argument("--card", required=True)
    parser.add_argument("--include-untracked", action="store_true")
    parser.add_argument("--metadata-only", action="store_true")
    parser.add_argument("--only", nargs="*", help="allowlist de arquivos por etapa")
    options = parser.parse_args()
    source, target = options.source.resolve(), options.target.resolve()
    changed = git(source, "diff", "--name-only", options.base).splitlines()
    if options.include_untracked:
        changed += git(source, "ls-files", "--others", "--exclude-standard").splitlines()
    paths = sorted(set(changed))
    if options.only is not None:
        paths = [path for path in paths if path in options.only]
    rows, conflicts, patch = [], [], ["*** Begin Patch"]
    for relative in paths:
        if not (relative.startswith("orq/") or relative.startswith("docs/")
                or relative in {"README.md", "memory/wiki/_schema.md",
                                "memory/wiki/arquitetura.md", "memory/wiki/_elenco.md",
                                "memory/wiki/distribuicao.md"}
                or relative == f"memory/wiki/threads/{options.card}"):
            continue
        # Âncoras e board pertencem ao lote final, não ao candidato de cada frente.
        if relative == "orq/.claude-plugin/plugin.json":
            continue
        src, dst = source / relative, target / relative
        if not src.is_file() or src.is_symlink():
            raise RuntimeError(f"fonte não regular: {relative}")
        incoming = src.read_bytes()
        current = dst.read_bytes() if dst.is_file() else None
        if current == incoming:
            rows.append({"path": relative, "state": "identical", "sha256": digest(incoming)})
            continue
        result = subprocess.run(["git", "show", f"{options.base}:{relative}"],
                                cwd=source, capture_output=True)
        base = result.stdout if result.returncode == 0 else None
        merged = incoming
        if current is not None and current != base:
            if base is None:
                if incoming.startswith(current):
                    merged = incoming
                elif current.startswith(incoming):
                    rows.append({"path": relative, "state": "target_superset",
                                 "source_sha256": digest(incoming), "sha256": digest(current)})
                    continue
                else:
                    conflicts.append({"path": relative, "kind": "add_add",
                                      "source_sha256": digest(incoming),
                                      "target_sha256": digest(current)})
                    continue
            else:
                with tempfile.TemporaryDirectory(prefix="orq-merge-analysis-") as tmp:
                    files = [Path(tmp) / name for name in ("ours", "base", "theirs")]
                    for file, data in zip(files, (current, base, incoming)):
                        file.write_bytes(data)
                    process = subprocess.run(["git", "merge-file", "--stdout",
                                              "-L", "integration", "-L", options.base,
                                              "-L", options.card, *map(str, files)],
                                             capture_output=True)
                    if process.returncode:
                        conflicts.append({"path": relative, "kind": "three_way",
                                          "source_sha256": digest(incoming),
                                          "target_sha256": digest(current),
                                          "merged_preview": process.stdout.decode("utf-8")})
                        continue
                    merged = process.stdout
        text = merged.decode("utf-8")
        if not options.metadata_only:
            if current is None:
                patch += [f"*** Add File: {dst}"] + ["+" + line for line in text.removesuffix("\n").split("\n")]
            else:
                diff = list(difflib.unified_diff(current.decode("utf-8").removesuffix("\n").split("\n"),
                                               text.removesuffix("\n").split("\n"), n=3, lineterm=""))
                patch += [f"*** Update File: {dst}"]
                patch += ["@@" if line.startswith("@@ ") else line for line in diff[2:]]
        rows.append({"path": relative, "state": "apply", "source_sha256": digest(incoming),
                     "target_sha256_before": digest(current) if current is not None else None,
                     "sha256_after": digest(merged)})
    patch.append("*** End Patch")
    print(json.dumps({"card": options.card, "source": str(source), "target": str(target),
                      "base": options.base, "files": rows, "conflicts": conflicts,
                      "patch": "\n".join(patch) + "\n"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
