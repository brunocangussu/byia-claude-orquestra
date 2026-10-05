#!/usr/bin/env python3
"""RED/GREEN da guarda de adjudicações versus a R6 v1.

A mutação troca duas adjudicações dev por pares coerentes de política/fatos e
refaz a regra em memória. Assim, não depende de hash antigo, regra antiga ou
erro estrutural para demonstrar a ausência/presença da guarda de baseline.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import importlib.util
import json
from pathlib import Path


def _load_module(candidate: Path):
    spec = importlib.util.spec_from_file_location(
        f"t098_{candidate.name.replace('-', '_')}", candidate / "preflight.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _mutated_manifest(manifest):
    value = deepcopy(manifest)
    left = next(case for case in value["adjudications"] if case["id"] == "Y007")
    right = next(
        case
        for case in value["adjudications"]
        if case["split"] == "dev"
        and case["gold"] == "normal"
        and case["id"] not in {"Y009", "Y011", "Y041"}
    )
    for field in ("gold", "policy_code", "facts", "rationale"):
        left[field], right[field] = deepcopy(right[field]), deepcopy(left[field])
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--expect", choices=("red", "green"), required=True)
    args = parser.parse_args()

    candidate = args.candidate.resolve()
    module = _load_module(candidate)
    sample = json.loads((candidate / "amostra.json").read_text(encoding="utf-8"))
    manifest = _mutated_manifest(
        json.loads((candidate / "manifesto.json").read_text(encoding="utf-8"))
    )
    rule = module.fit_rule(sample, manifest)

    # Simula a reemissão legítima dos selos dependentes da adjudicação mutada.
    module.load_inputs = lambda _root: (sample, manifest, rule)
    module.verify_frozen_snapshot = lambda *_args: None

    try:
        module.run_local_preflight(candidate)
    except ValueError as exc:
        if args.expect == "green" and str(exc).startswith("metadados v1 divergentes:"):
            print(json.dumps({"rejection": str(exc)}, ensure_ascii=False))
            return
        raise
    if args.expect == "red":
        raise AssertionError(
            "guarda de adjudicação v1 ausente: preflight aceitou gold/split/família alterados"
        )
    raise AssertionError("preflight v5 aceitou adjudicação alterada")


if __name__ == "__main__":
    main()
