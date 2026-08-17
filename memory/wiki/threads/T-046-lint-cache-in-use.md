# T-046 — Lint do cache e `.in_use`

## Estado

CANDIDATA `0.22.4` IMPLEMENTADA E REVISADA no worktree `codex/t044-reset-concurrency-0223`, base
`0ad1deb`. Release e instalação ainda não executadas.

## Causa raiz comprovada

O lint compara por bytes o plugin fonte com `~/.claude/plugins/cache/orquestra/orq/<versão>`. A enumeração ignora apenas `.DS_Store` e `.orphaned_at`; por isso inclui `.in_use/<PID>`, metadado operacional criado pelo Claude para proteger caches usados por sessões vivas.

Reprodução controlada em três HOME temporários:

- cache byte-idêntico: exit 0;
- mesmo cache + `.in_use/4242`: exit 1, falso positivo;
- mesmo cache + `real-extra.txt`: exit 1, comportamento correto a preservar.

Na máquina real, os marcadores `20472` e `30288` pertencem a processos Claude vivos. Eles não serão apagados nem alterados.

## Desenho aprovado

- Filtrar `.in_use` e seus descendentes somente ao enumerar o cache runtime.
- Não filtrar `.in_use` no repositório fonte.
- Manter `.DS_Store` e `.orphaned_at` como metadados ignorados.
- Manter falha para qualquer outro arquivo extra ou conteúdo divergente.
- Cobrir marcador em diretório, marcador legado como arquivo, extra real e `.in_use` indevido no fonte.

## Gates

- RED observado antes de alterar `lint-coerencia.py`.
- GREEN selecionado e suíte completa de `test_context_guard.py`.
- `lint-coerencia.py`, `test_run_opus_reviewer.py`, `cmp AGENTS.md CLAUDE.md` e `git diff --check` verdes.
- Marcadores de PIDs vivos preservados.

## RETOMAR AQUI

Esperar o dono autorizar commit, publicação em `origin/main` e instalação segura da 0.22.4 no
Claude/Codex. Só depois do release validado retomar T-044 sobre a nova base; T-044 continua fora.
