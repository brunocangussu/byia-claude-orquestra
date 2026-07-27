# MEMORY — índice da wiki

> **Leia esta página primeiro ao retomar.** Cada linha diz onde a verdade mora.
> Contexto é descartável; isto aqui não é.

**Projeto:** Orquestra (`orq`) — plugin do Claude Code para desenvolvimento orientado a board.
**Versão:** 0.6.1 · **board instalado em** 2026-07-26.

## Onde paramos

O `/orq:init` **já rodou em projeto de terceiro** (2026-07-27, outra LLM, sem ninguém daqui por
perto) e voltou com 10 atritos — 4 bugs de contrato reais. Isso fechou o `T-003` e gerou o `T-011`.
O painel de revisores **funciona desde a 0.5.1** e já se pagou duas vezes: achou tanto a brecha de
instalação por slash command quanto o parser permissivo do board.

**O que ainda não foi exercitado:** `/orq:plan-next` e `/orq:implement-next` nunca foram invocados de
verdade — todo o trabalho até aqui foi feito pelo Manager na mão (`T-012`). E as 9 "regras
invioláveis" continuam sendo texto de prompt: não há um único hook (`T-001`, `T-002`).

**Aberto e sem resposta:** como coordenar checkpoint entre **várias janelas** no mesmo projeto
(`T-013`) — hoje o modelo pressupõe um Manager só, e N janelas se sobrescrevem em silêncio.

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
| `wiki/threads/` | Trabalho em curso, com "RETOMAR AQUI" (vazio por ora) |

## A distinção que faz isto funcionar

O **log** é imutável e responde *"o que aconteceu em tal dia"*. A **página de tópico** é reescrita e
responde *"como funciona hoje"*. Sem a página, a segunda pergunta vira arqueologia no log.

Nunca guarde aqui o que é **derivável** (diff, `git log`, lista de arquivos, o código atual) — a fonte
já tem. Guarde o *porquê* e as *consequências*.
