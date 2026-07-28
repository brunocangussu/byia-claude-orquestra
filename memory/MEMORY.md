# MEMORY — índice da wiki

> **Leia esta página primeiro ao retomar.** Cada linha diz onde a verdade mora.
> Contexto é descartável; isto aqui não é.

**Projeto:** Orquestra (`orq`) — plugin do Claude Code para desenvolvimento orientado a board.
**Versão:** 0.10.0 · **board instalado em** 2026-07-26 · **último checkpoint:** 2026-07-28.

## Onde paramos

**O que já foi provado em uso real:**
- O `/orq:init` rodou em **projeto de terceiro** (outra LLM, sem ninguém daqui) e voltou com 10
  atritos — 4 bugs de contrato. Fechou o `T-003`, gerou o `T-011`.
- O **painel de três revisores** (Claude · Codex · Kimi) funciona e já se pagou três vezes: achou a
  brecha de instalação por slash command, o parser permissivo do board, e — na mesma rodada — Codex e
  Kimi acharam bugs **diferentes** no mesmo arquivo.
- O ciclo de release está fechado: `validate` → `lint` → `marketplace update` → `plugin update`.

**O buraco maior, e ele é de método, não de código:** a interface natural tinha **0% de cobertura**
sobre a fala real do dono. Por isso a skill `orq` nunca foi invocada em toda a sessão de 26-28/jul, os
Loops A e B nunca rodaram, e **tudo foi implementado direto, sem plano e sem gate** — inclusive
features inteiras. Corrigido na 0.9.0 (cobertura 0→100% + seção "Roteamento automático"), **mas a
correção ainda não foi exercitada numa sessão real**.

**O que continua sem teste:** `/orq:plan-next` e `/orq:implement-next` nunca foram invocados de
verdade (`T-012`). As 9 regras invioláveis seguem sendo texto de prompt — nenhum hook (`T-001`,
`T-002`).

⚠️ **9 cards em VALIDATE esperando o dono usar o produto.** Card fecha quando ele confirma, não
quando o commit passa — a pilha crescer tanto é sinal de que a validação não está acontecendo.

Ver `wiki/KANBAN.md` para o estado exato de cada card.

## Páginas

| Página | Responde |
|---|---|
| [`wiki/KANBAN.md`](wiki/KANBAN.md) | **O board.** Onde cada card está e o que espera o dono |
| [`wiki/arquitetura.md`](wiki/arquitetura.md) | Como o Orquestra funciona hoje e **por que** cada recusa de desenho |
| [`wiki/distribuicao.md`](wiki/distribuicao.md) | Como empacotar, validar, testar e publicar o plugin |
| [`wiki/_schema.md`](wiki/_schema.md) | **O contrato**: formato do board (lido por parser) e regras da wiki |
| [`wiki/_elenco.md`](wiki/_elenco.md) | Qual LLM toca cada papel + revisores externos ativos |
| [`wiki/_stack.md`](wiki/_stack.md) | Ferramentas ativas aqui + **o que o dono dispensou** (não repropor) |
| [`fixes-history.md`](fixes-history.md) | **Log** cronológico, append-only — "o que aconteceu naquele dia" |
| [`gotchas.md`](gotchas.md) | Armadilhas que já custaram tempo |
| [`wiki/threads/desenvolvimento-do-plugin.md`](wiki/threads/desenvolvimento-do-plugin.md) | **Thread ativa** — fases, decisões a não re-litigar e **⏭️ RETOMAR AQUI** |

## A distinção que faz isto funcionar

O **log** é imutável e responde *"o que aconteceu em tal dia"*. A **página de tópico** é reescrita e
responde *"como funciona hoje"*. Sem a página, a segunda pergunta vira arqueologia no log.

Nunca guarde aqui o que é **derivável** (diff, `git log`, lista de arquivos, o código atual) — a fonte
já tem. Guarde o *porquê* e as *consequências*.
