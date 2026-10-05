#!/usr/bin/env python3
"""Adaptador consultivo de hooks do medidor de progresso (SessionStart e PostToolUse).

Liga o stdin do host a `progress.py:handle_hook` e imprime a resposta; toda a regra mora no núcleo. Aqui
só existem a saída rápida e o contrato de falha.

**Saída rápida antes de importar o núcleo.** Este hook roda em TODA chamada de ferramenta de TODO projeto com
o plugin instalado, e importar o `progress.py` custa mais do que o resto do processo. Por isso, sem medidor
nada é importado: só `json`, `os` e `sys`, e a decisão sai de `stat` nos ancestrais do `cwd` do payload
(`.orq/progress/v1/sessions/`). O núcleo só é carregado quando o medidor existe.

O hook é consultivo e NUNCA bloqueia o host: payload inválido, núcleo ausente, lock ocupado, permissão, Git
indisponível ou qualquer erro saem 0, sem saída. A resposta, quando existe, é só `additionalContext`; nunca
negação, bloqueio nem continuação forçada. Não abre o transcript nem lê o conteúdo de ferramentas ou do prompt.
"""

from __future__ import annotations

import json
import os
import sys

MAX_STDIN_BYTES = 4 * 1024 * 1024
MAX_ANCESTORS = 64
HOOK_SUBPROCESS_SECONDS = 1.0  # consultas ao Git e ao board: o host espera o hook, e o timeout dele é curto
HOOK_EVENTS = ("SessionStart", "PostToolUse")


def _has_meter(cwd: str) -> bool:
    """Há `.orq/progress/v1/sessions/` no `cwd` ou acima dele? Só `stat`; nada é aberto nem importado."""
    current = os.path.realpath(cwd)
    for _ in range(MAX_ANCESTORS):
        if os.path.isdir(os.path.join(current, ".orq", "progress", "v1", "sessions")):
            return True
        parent = os.path.dirname(current)
        if parent == current:
            return False
        current = parent
    return False


def _may_need_core(event: object) -> bool:
    """Saída rápida: o evento é do medidor, o host é conhecido e existe um medidor para consultar."""
    if not isinstance(event, dict):
        return False
    if not (os.environ.get("PLUGIN_ROOT") or os.environ.get("CLAUDE_PLUGIN_ROOT")):
        return False
    cwd = event.get("cwd")
    if event.get("hook_event_name") not in HOOK_EVENTS or not isinstance(cwd, str):
        return False
    return "\0" not in cwd and os.path.isabs(cwd) and _has_meter(cwd)


def _load_core():
    import importlib.util
    from pathlib import Path

    path = Path(__file__).resolve().with_name("progress.py")
    spec = importlib.util.spec_from_file_location("orq_progress_core", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    try:
        raw = sys.stdin.buffer.read(MAX_STDIN_BYTES + 1)
        if len(raw) > MAX_STDIN_BYTES:
            return 0
        event = json.loads(raw.decode("utf-8"))
        if not _may_need_core(event):
            return 0
        core = _load_core()
        core.GIT_TIMEOUT_SECONDS = HOOK_SUBPROCESS_SECONDS
        core.SUBPROCESS_TIMEOUT_SECONDS = HOOK_SUBPROCESS_SECONDS
        result = core.handle_hook(event, os.environ)
        if result is not None:
            print(json.dumps(result, ensure_ascii=True, separators=(",", ":")))
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
