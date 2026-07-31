# MEMORY — índice da wiki

> **Leia esta página primeiro ao retomar.** Cada linha diz onde a verdade mora.
> Contexto é descartável; isto aqui não é.

**Projeto:** Orquestra (`orq`) — plugin do Claude Code para desenvolvimento orientado a board.
**Versão:** 0.13.0 · **board instalado em** 2026-07-26 · **último checkpoint:** 2026-07-29.

## Onde paramos

**O que já foi provado em uso real:**
- O `/orq:init` rodou em **projeto de terceiro** (outra LLM, sem ninguém daqui) e voltou com 10
  atritos — 4 bugs de contrato. Fechou o `T-003`, gerou o `T-011`.
- O **painel de três revisores** (Claude · Codex · Kimi) funciona e já se pagou três vezes: achou a
  brecha de instalação por slash command, o parser permissivo do board, e — na mesma rodada — Codex e
  Kimi acharam bugs **diferentes** no mesmo arquivo.
- O ciclo de release está fechado: `validate` → `lint` → `marketplace update` → `plugin update`.

- **O ciclo inteiro rodou pela primeira vez** (0.11.0, 29/jul): Fable planejou 16 passos → dono
  aprovou no gate → Sonnet implementou → Claude+Codex+Kimi revisaram → 7 achados voltaram como
  correção. **Achou defeito que `validate` e `lint` não pegam.** Fechou o `T-012`.

**O que o ciclo revelou, e é o achado mais consequente até aqui:** o cache do plugin é indexado por
**versão**. Editar sem bumpar não muda o que roda, e `claude plugin list` segue dizendo que está tudo
certo. Aconteceu no `5b75296` e **invalidou retroativamente** todo teste comportamental feito depois.
Agora há guarda no lint. A versão vive em **quatro** lugares — o `marketplace.json` estava em `0.4.0`,
sete releases atrás.

**A lição de método:** instrução não é enforcement. O `_elenco.md` **já dizia** que o Kimi não tem
sandbox e exigia worktree descartável; o Kimi rodou `git checkout -- .` numa revisão read-only e
destruiu o working tree (`T-019`). É o argumento do `T-001` provado contra o próprio repo.

**O que continua sem teste:** os comandos `/orq:plan-next` e `/orq:implement-next` literais (o fluxo
foi provado, os comandos não). As 9 regras invioláveis seguem sendo texto — nenhum hook (`T-001`,
`T-002`).

⚠️ **9 cards em VALIDATE.** Card fecha quando o dono confirma, não quando o commit passa. Os
comportamentais só são testáveis **depois do release e do restart** — antes disso testam a versão
anterior, pelo motivo acima.

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
| [`wiki/threads/T-025-gatilhos.md`](wiki/threads/T-025-gatilhos.md) | Plano pronto **esperando 6 decisões do dono** — cobertura de gatilho medida, descoberta e política de iniciativa |
| [`wiki/threads/T-026-host-alternativo.md`](wiki/threads/T-026-host-alternativo.md) | Plano pronto **esperando 6 decisões do dono** — rodar a disciplina fora do Claude Code (matriz de paridade Codex × Kimi) |
| [`wiki/threads/T-023-reload-vs-restart.md`](wiki/threads/T-023-reload-vs-restart.md) | Plano pronto **esperando 5 decisões do dono** — evidência por componente no lugar de regra binária |
| [`wiki/threads/_noturno.md`](wiki/threads/_noturno.md) | Manifesto e relatório do **modo noturno** — limites, cards escolhidos, o que foi pulado e por quê |

## A distinção que faz isto funcionar

O **log** é imutável e responde *"o que aconteceu em tal dia"*. A **página de tópico** é reescrita e
responde *"como funciona hoje"*. Sem a página, a segunda pergunta vira arqueologia no log.

Nunca guarde aqui o que é **derivável** (diff, `git log`, lista de arquivos, o código atual) — a fonte
já tem. Guarde o *porquê* e as *consequências*.
