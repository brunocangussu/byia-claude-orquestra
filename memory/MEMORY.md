# MEMORY — índice da wiki

> **Leia esta página primeiro ao retomar.** Cada linha diz onde a verdade mora.
> Contexto é descartável; isto aqui não é.

**Projeto:** Orquestra (`orq`) — plugin do Claude Code para desenvolvimento orientado a board.
**Versão:** 0.19.0 · **board instalado em** 2026-07-26 · **último checkpoint:** 2026-08-04.

## ⏸️ O que espera o dono AGORA (2026-08-05, fim do dia)

1. **Release da 0.19.0** — `claude plugin marketplace update orquestra` + `claude plugin update
   orq@orquestra` + **restart**. Ela está commitada mas **não instalada**; a versão ativa é a 0.18.0.
2. **Testar os cinco cards em VALIDATE** — `T-020`, `T-023`, `T-025`, `T-030` (a 0.18.0 já está
   ativa, então esses três primeiros podem ser testados **agora**) e `T-026`. As frases:
   *"quais as possibilidades"* · *"instala o Serena aqui"* · *"tô com pouco crédito"* seguido de
   *"chegamos ao final do ciclo"* (a segunda **não** pode trocar o elenco).
3. **Instalar no Kimi** — nunca foi feito. `/orq:instalar` tem os comandos; o `~/.agents/skills/`
   existe, o `~/.kimi-code/agents/` é **hipótese não confirmada**, com fallback documentado.
4. **Decidir os 6 riscos menores** que o painel da 0.19.0 achou e que viraram candidatos a card
   (listados no `T-026` no board) — nenhum tinha correção óbvia de uma frase.

**Commitado e no GitHub:** 0.17.0 (`10ecef2`) · 0.18.0 (`7674cab`) · board (`7c14aa9`).
**Commitado, falta push:** 0.19.0 (`8bef7f9`).

## ✅ O que foi provado em 2026-08-05 — o framework roda fora do Claude Code

O Codex, com o plugin instalado, passou nos quatro testes comportamentais: **invocou a skill sozinho**
por frase natural · **achou e leu os `commands/`** · roteou um pedido pelo ciclo e **parou no gate**
sem tocar no produto · e, ao ser mandado revisar, **declarou a degradação** (*"este host não oferece
override de modelo no subagente nativo"*) em vez de fingir painel — a regra escrita na 0.18.0 indo a
campo. Ele ainda **cruzou o board com o `git log`** e flagrou dois defeitos do checkpoint anterior.

**O protocolo de várias janelas (`T-013`) foi validado entre hosts diferentes:** o Codex detectou uma
edição do Manager em `gotchas.md` que não era dele, e a excluiu do escopo sem sobrescrever.

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

⚠️ **12 cards em VALIDATE** (0.14.0, 0.15.0 e 0.16.0 entraram em 2026-07-31). Card fecha quando o dono confirma, não quando o commit passa. Os
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
| [`wiki/threads/T-025-gatilhos.md`](wiki/threads/T-025-gatilhos.md) | **Implementado na 0.15.0** — descoberta (`/orq:ajuda`), gatilhos atestados e a política de iniciativa em três níveis |
| [`wiki/threads/T-026-host-alternativo.md`](wiki/threads/T-026-host-alternativo.md) | **Ativo** — o Orquestra rodando fora do Claude Code. Instalação multi-host (0.18.0, entregue e provada no Codex) e elenco host-agnóstico (0.19.0, aguardando painel). **A thread é longa: o `⏭️ RETOMAR AQUI` vivo é o último do arquivo** — os anteriores estão marcados como superados |
| [`wiki/threads/T-023-reload-vs-restart.md`](wiki/threads/T-023-reload-vs-restart.md) | **Implementado na 0.14.0**, reprovado no review e corrigido — evidência por componente no lugar de regra binária |
| [`wiki/threads/T-020-perfis-elenco.md`](wiki/threads/T-020-perfis-elenco.md) | **Entregue na 0.16.0** — perfis de elenco (`padrao` · `economia`) trocados por frase |
| [`wiki/threads/_noturno.md`](wiki/threads/_noturno.md) | Manifesto **expirado** + relatório do modo noturno de 2026-07-30 — não abrir run novo a partir dele |
| [`snapshot-2026-07-31-releases-0.14-0.16.md`](snapshot-2026-07-31-releases-0.14-0.16.md) | **Marco**: estado exato ao fim das três entregas do dia + as três lições de método |

## A distinção que faz isto funcionar

O **log** é imutável e responde *"o que aconteceu em tal dia"*. A **página de tópico** é reescrita e
responde *"como funciona hoje"*. Sem a página, a segunda pergunta vira arqueologia no log.

Nunca guarde aqui o que é **derivável** (diff, `git log`, lista de arquivos, o código atual) — a fonte
já tem. Guarde o *porquê* e as *consequências*.
