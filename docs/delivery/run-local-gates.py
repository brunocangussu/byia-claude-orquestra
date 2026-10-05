#!/usr/bin/env python3
"""Executa gates completos e devolve recibo compacto, sem escrever artefatos."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time


def source_hash(root):
    paths = sorted(p for p in (root / "orq").rglob("*") if p.is_file()
                   and "__pycache__" not in p.parts and p.suffix not in {".pyc", ".pyo"})
    rows = [f"{p.relative_to(root)} {hashlib.sha256(p.read_bytes()).hexdigest()}" for p in paths]
    return hashlib.sha256("\n".join(rows).encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", required=True)
    options = parser.parse_args()
    root = Path.cwd().resolve()
    before = source_hash(root)
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    commands = [
        ("suite", [sys.executable, "-m", "unittest", "discover", "-s", "orq/scripts", "-p", "test_*.py"]),
        ("manifest", ["claude", "plugin", "validate", "./orq", "--strict"]),
        ("lint", [sys.executable, "orq/scripts/lint-coerencia.py", "."]),
        ("diff", ["git", "diff", "--check"]),
    ]
    rows = []
    for label, args in commands:
        started = time.monotonic()
        result = subprocess.run(args, cwd=root, env=env, capture_output=True,
                                text=True, timeout=300)
        output = result.stdout + result.stderr
        count = re.search(r"Ran (\d+) tests", output)
        rows.append({"gate": label, "exit": result.returncode,
                     "tests": int(count[1]) if count else None,
                     "seconds": round(time.monotonic() - started, 3),
                     "output_sha256": hashlib.sha256(output.encode()).hexdigest(),
                     "diagnostic": output[-8000:] if result.returncode else output[-350:]})
    after = source_hash(root)
    print(json.dumps({"label": options.label, "root": str(root),
                      "utc": datetime.now(timezone.utc).isoformat(),
                      "source_sha256_before": before, "source_sha256_after": after,
                      "source_unchanged": before == after, "gates": rows}, ensure_ascii=False))
    return 0 if before == after and all(row["exit"] == 0 for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
