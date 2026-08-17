# T-046 — Lint do cache e `.in_use`

## Estado

FECHADA. A `0.22.4` foi publicada em `origin/main` no commit de produto `676846a` e instalada no
Claude e no Codex. Os caches reais foram comparados ao pacote publicado sem divergências.

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
- `orq@orquestra 0.22.4` aparece habilitado nos dois hosts.
- Os 29 arquivos distribuídos são byte-idênticos nos dois caches; metadados próprios do host foram
  classificados separadamente.
- O lint real passou com dois marcadores `.in_use` ativos no Claude.
- O cache `0.22.3` foi preservado/restaurado para sessões já abertas.

## Checkpoint de recuperação pós-compactação — 2026-08-17

- Pedido atual preservado: concluir publicação/instalação da `0.22.4` e fechar a T-046.
- Código já publicado em `origin/main` no commit `676846a`.
- Claude e Codex já apontam para `0.22.4`; o cache Codex `0.22.3` foi restaurado após a janela de upgrade para não quebrar sessões que ainda o referenciam.
- Próximo ponto seguro: comparar os bytes instalados com o pacote publicado, ignorando somente metadados gerados pelo host; depois atualizar board, memória e histórico.
- T-044 continua fora desta mudança e só será retomada depois do fechamento verificável da T-046.

## RETOMAR AQUI

T-046 fechada. Retomar T-044 sobre a base publicada `0.22.4`; tratar a recuperação durável de
caches `0.18.0`–`0.22.2` somente pela T-047, sem sobrescrever as versões atuais.
