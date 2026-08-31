# Thread — Timeout operacional do runner Opus (`T-050`)

**Estado:** validada pelo dono e fechada em 2026-08-31.

## Pedido do dono

Investigar por que o reviewer Opus do Orquestra expirava e resolver a causa, sem mascarar falha de
autenticação, modelo ou processo.

## Diagnóstico reproduzido — 30-Ago-2026

- runner instalado e fonte 0.22.5 eram byte a byte idênticos;
- Claude Code CLI `2.1.246` estava disponível;
- sonda `Responda somente: OK` concluiu em 6,0s, exit 0, com
  `OPUS_MODEL=claude-opus-5`;
- briefing real T-102 de 5.558 bytes expirou duas vezes no default de 240s;
- o mesmo arquivo, executado com `--timeout 600`, concluiu em 267,1s, exit 0, com
  `claude-opus-5` e parecer não vazio.

**Causa raiz:** o default fixo de 240s tinha margem insuficiente para a cauda real do Opus. A
resposta válida chegou 27,1s depois do encerramento imposto pelo runner.

## Correção candidata 0.22.6

- `DEFAULT_TIMEOUT_SECONDS`: 240 → 600;
- `--timeout` continua disponível para override;
- limite de 16 KiB, stdin, JSON, `modelUsage`, saída não vazia, kill do grupo e códigos de erro são
  preservados;
- comando, arquitetura e lint passam a exigir 600s;
- teste RED→GREEN prova o novo default.

## ✅ Validação final

Checkpoint de recuperação após compactação, 30-Ago-2026. Os gates da candidata 0.22.6 foram
repetidos no worktree isolado `codex/t050-opus-timeout`: 185 testes verdes, lint de coerência com
20 nomes, `git diff --check`, `py_compile` e manifestos/versão coerentes. O smoke real sem
`--timeout` anunciou `TIMEOUT=600s`, comprovou `claude-opus-5` e concluiu em 4,8s com exit 0. O
escopo funcional permanece mínimo: somente o default 240 → 600; override, limite de 16 KiB,
comprovação do modelo, fail-closed e kill do grupo foram preservados.

O parecer recuperado do T-102 foi registrado no projeto de produto como `REPROVADO` e permanece
pendente de verificação contra o código antes de alterar o plano.

Release autorizada e concluída no commit `fbaff1c`, publicado por fast-forward em `origin/main`.
Codex e Claude registram `orq@orquestra 0.22.6` habilitada; os dois caches têm 35/35 arquivos
byte-idênticos ao pacote. O instalador removeu a 0.22.5 ainda referenciada por esta sessão durante o
upgrade, mas o backup preventivo foi restaurado antes de continuar, preservando 0.22.5 e 0.22.6 lado
a lado. O smoke pelo runner instalado do Codex, sem `--timeout`, anunciou `TIMEOUT=600s`, comprovou
`claude-opus-5` e concluiu em 5,3s com exit 0.

Em 31-Ago-2026, uma task Codex nova carregou naturalmente a 0.22.7, release que preserva o default
de 600s. A fonte e o cache instalado mantêm `DEFAULT_TIMEOUT_SECONDS = 600.0`, e o pacote `orq/`
permanece sem diff no SHA `41ed5da`. O dono confirmou explicitamente que a T-050 está resolvida.
Não houve nova chamada Opus: o parecer real de 267,1s sob o teto de 600s e o smoke do runner
instalado já provavam o caminho comportamental. O fechamento não incluiu commit, push ou restart.
