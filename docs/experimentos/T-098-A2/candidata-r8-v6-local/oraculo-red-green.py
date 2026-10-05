#!/usr/bin/env python3
"""Oráculos auxiliares das regressões de formato histórico já confirmadas.

Este arquivo é chamado por testes ``test_*.py`` contra snapshots históricos.
Ele registra RED reexecutável sem alegar qualidade, holdout ou ausência de
atalhos além dos padrões estreitos verificados.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def _load(candidate: Path):
    sample = json.loads((candidate / "amostra.json").read_text(encoding="utf-8"))
    manifest = json.loads((candidate / "manifesto.json").read_text(encoding="utf-8"))
    labels = {item["id"]: item["gold"] for item in manifest["adjudications"]}
    return sample["cases"], labels


def _by_class(cases, labels, predicate):
    totals = Counter()
    for case in cases:
        totals[labels[case["id"]]] += bool(predicate(case["text"]))
    return totals


def _assert_punctuation(cases, labels):
    marks = _by_class(cases, labels, lambda text: "?" in text)
    abster = marks["abster"]
    others = sum(value for name, value in marks.items() if name != "abster")
    assert not (abster == 8 and others == 0), (
        "atalho de pontuação exclusivo: 8/8 abster e 0/40 outras classes"
    )
    return {"abster": abster, "outras_classes": others}


def _assert_phrase(cases, labels):
    phrases = _by_class(cases, labels, lambda text: "ainda não" in text.casefold())
    abster = phrases["abster"]
    others = sum(value for name, value in phrases.items() if name != "abster")
    assert not (abster == 8 and others <= 1), (
        "atalho lexical de frase exclusivo: 8/8 abster e no máximo 1/40 outras classes"
    )
    return {"abster": abster, "outras_classes": others}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--oracle", choices=("punctuation", "phrase"), required=True)
    args = parser.parse_args()
    cases, labels = _load(args.candidate)
    profile = (
        _assert_punctuation(cases, labels)
        if args.oracle == "punctuation"
        else _assert_phrase(cases, labels)
    )
    print(json.dumps({"oracle": args.oracle, "profile": profile}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
