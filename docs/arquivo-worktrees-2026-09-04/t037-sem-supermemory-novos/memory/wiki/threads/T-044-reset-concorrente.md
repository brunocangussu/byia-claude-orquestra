# T-044 — Endurecer reset concorrente do guardião de contexto

## Estado

PLANNING reaberto em 2026-08-17 sobre a release publicada `0.22.3`. Nenhuma implementação desta
rodada foi iniciada.

## Motivo da reabertura

A revisão anterior demonstrou duas fragilidades: uma transação antiga pode consumir um reset mais
novo, e o fallback Windows baseado em `lockdir` não recupera lock órfão. Uma candidata experimental
`0.22.2` chegou a testes verdes, mas Opus 5 encontrou uma corrida adicional porque
`PreCompact`/`PostCompact` ainda podiam escrever estado fora do lock.

Essa candidata não foi publicada e não deve ser reaplicada sobre a `0.22.3`. A base atual incorporou
outras mudanças relevantes, incluindo a integração do guardião consultivo e contratos de upgrade
seguro.

## Próxima investigação

1. Reproduzir as corridas na fonte `origin/main` atual.
2. Traçar todas as leituras e escritas do estado, incluindo `PreCompact` e `PostCompact`.
3. Confirmar as invariantes fail-open, zero bloqueio no Codex e preservação do `/clear` no Claude.
4. Regenerar plano RED → GREEN e revisar impacto de compatibilidade antes do gate do dono.

⏭️ RETOMAR AQUI: criar worktree isolado a partir de `origin/main`, executar somente investigação e
testes RED na `0.22.3`, escrever o plano atualizado e parar no gate antes de qualquer implementação.
