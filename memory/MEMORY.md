# MEMORY — índice da wiki

> **Leia esta página primeiro ao retomar.** Cada linha diz onde a verdade mora.
> Contexto é descartável; isto aqui não é.

**Projeto:** Orquestra (`orq`) — plugin do Claude Code para desenvolvimento orientado a board.
**Versão:** 0.24.0 · **board instalado em** 2026-07-26 · **último checkpoint:** 2026-09-01 · **host padrão a partir de 2026-08-09: Codex** (decisão do dono).

## 🟢 Trabalho mais recente (2026-09-01) — @frente-elenco · `T-051`

**RELEASADA em 2026-09-01, aguardando o teste comportamental do dono.** Implementação + **7 rodadas
de review externo** (25 bloqueadores, contagem 5→8→4→5→2→1→**0 APROVADO**). 18 arquivos, `0.24.0`
nos quatro lugares, gates verdes conferidos pelo Manager. Merge de `feat/t051-elenco-por-tarefa` na
`main`, commitada e **com push feito** — quem instalar do GitHub recebe a 0.24.0.

**O que a 0.24.0 muda, em uma frase cada:**
- **Elenco em dois eixos** — `trilha` (`interface`|`sistema`) escolhe o **vendor de quem pensa**;
  `faixa` (`pesada`|`normal`|`leve`) escolhe o **degrau de quem escreve**. Síntese aprovada pelo
  dono: *"domínio decide quem pensa; host decide quem escreve"*.
- **Revisor único, vendor oposto ao host, SEM exceção** — decisão do dono **contra** a recomendação
  do planner. O painel acabou; *"confirmado por 2+"* não existe mais. **Diff com dado sensível fica
  sem revisor** (LGPD impede o vendor oposto): o Manager audita e **declara a ausência** — é
  proibido spawnar revisor do mesmo vendor para tapar o buraco.
- **Kimi aposentado** do produto inteiro. A limpeza na máquina do dono é **dele, depois** do release
  validado e do cancelamento da assinatura: `~/.claude/agents/kimi-revisor.md` · a seção de delegação
  do `~/.claude/CLAUDE.md` · `~/.agents/skills/orq/` · `~/.kimi-code/`.
- **`## Papéis` eliminada** — `## Times por host` é a única fonte, para ler e gravar. Antes, `perfil
  economia` no Codex reescrevia uma tabela que **nenhum consumidor lia**.

**Estado honesto: *instalado, não validado*.** Falta o passo 12 — `marketplace update` +
`plugin update` + **restart** + `diff -rq` vazio + os 6 critérios de aceite em conversa natural.
Retomar em `wiki/threads/T-051-elenco-por-tarefa.md`.

## 🟡 Trabalho anterior (2026-08-09) — @frente-paridade-codex

**⚡ ESTADO EM 2026-08-13 — leia isto primeiro:**

- **T-045 concluído e T-048 aprovado em 2026-08-29:** o dono validou **PORTAR IDEIAS** e aprovou a
  implementação do ledger de remoção e do verificador graph-first nativos, offline e host-agnósticos.
  A fase 1 não toca hooks nem bloqueia sessões. A implementação ocorre no worktree isolado
  `codex/t046-auditores-nativos`; retomar em `wiki/threads/T-048-auditores-nativos.md`.

- **`T-043` com plano consultivo aprovado e em implementação:** incidente recorrente confirmou que o
  bloqueio vinha do guardião instalado, não do `/goal`. Sete threads detectadas foram liberadas
  por marcadores `.allow` recuperáveis; a sessão informada pelo dono passou smoke com zero
  `decision:block`. Após compactação durante o Loop B, o checkpoint de recuperação confirmou o
  estado no board/thread. O worktree `feat/t043-compactacao-reidratada` implementa na fonte a
  política “checkpoint registra e continua”, mantendo 55/60/70 como alertas e deixando a
  compactação nativa trabalhar.

- **0.22.0 LOCAL — `T-043` em implementação/review:** guardião Codex empacotado em seis hooks,
  parser/estado por sessão, faixas 55%/60%/70%, handshake “Seguro dar `/clear`” e backstop de 90%
  documentado como opt-in. Testes e validadores locais passam; ainda faltam instalação Codex,
  smoke externo, painel Opus 5 + Kimi K3 e gates de configuração/publicação.
- **0.21.0 PUBLICADA — `T-041` em VALIDATE:** template/migração do elenco host-aware,
  resolução host→papel→executor, interface Codex por linguagem natural + `/skills`, diagnóstico em
  sete camadas e memória legada diferenciada de projeto virgem. Runner Opus 5 comprovado em nova
  sessão Codex de projeto externo; Claude/Codex instalados em `0.21.0`, caches idênticos. GitHub
  atualizado e verificado; falta o dono repetir a revisão no projeto real que originou o bug.
- **`T-042` permanece no backlog para 0.23.0:** statusline nativa Codex opt-in começa depois do
  guardião `T-043`.

- **0.20.0 RELEASADA E PUBLICADA** (commit `164387c`, push feito). Instalada e verificada no Claude
  **e** no Codex, cache idêntico ao repo nos dois. O `T-036` está em **VALIDATE**, aguardando só o
  teste do dono: projeto de rascunho → `/orq:init` → tem que dizer *"sua statusline já mostra o
  board"* e **não gravar chave nenhuma**.
- **O dono adotou o Codex como host padrão.** O time do host Codex está em `_elenco.md`,
  `## Times por host` — planner e implementer OpenAI, **revisor `opus` de fora** (a diversidade do
  painel depende disso). ⚠️ **Subagente nativo no Codex é "observado 1×", não comprovado** — se não
  funcionar, **declare a degradação**, não finja que houve painel.
- **Outras frentes preservadas:** `T-037` continua planejado/aprovado; `T-038` continua separado;
  esta janela pertence exclusivamente à paridade Codex.
- **Fora deste repo, mapeado e não executado:** a migração de memória do projeto
  `Bruno Vascular - Gestão Dados Marketing` (relatório completo do scout na conversa de 09/ago;
  6 dos 11 snapshots de lá **já são páginas vivas**; 7 páginas de tópico e 14 cards propostos).
  ⚠️ Achado de segurança **fora do escopo do Orquestra**, reportado ao dono: `workflow_secretaria.json`
  daquele projeto tem PII de paciente e token em texto puro.

**Da noite de 07→08 (frente statusline, `T-036`/`T-037`/`T-038`):**

0. **Reiniciar as sessões** do `IVA - App System` e do `prompts-byia-clientes` — é o que faz a barra
   completa voltar naqueles dois projetos. A correção já está no disco (o segundo, commitada em
   `41fa1f9`); só falta a sessão reler o settings.
1. **Tirar o conector Supermemory** em **claude.ai → Settings → Connectors**. ⚠️ Verificado em
   2026-08-08: ele **não está** em `~/.claude.json`, nem em `~/.claude/settings.json`, nem em
   `.mcp.json` de projeto algum — `claude mcp list` não o lista. É conector **da conta**, e nenhuma
   mudança no plugin alcança isso. O `T-037` tira o Supermemory do produto; **o erro de conexão que
   você vê só para aqui.**
2. **Decidir o release da 0.20.0** — está bumpada nos quatro lugares e **não commitada**. O `T-036`
   ficou com escopo reduzido (conserto + F1/F2/F3 + asset saneado); falta a rodada de correção
   terminar e um painel final antes de qualquer publicação.

**Do bloco anterior (@release-validacao, segue valendo):**



1. **Dar o de-acordo em três cards já testados** — `T-017`, `T-007` e `T-010` passaram em 07/ago,
   com a evidência escrita em cada card. São testes mecânicos, sem viés; falta só você concordar.
2. **Rodar os testes que só você pode rodar** — `T-014`, `T-016`, `T-009`, `T-022`, `T-025`, `T-020`,
   `T-023`, `T-030`. Todos dependem de **frase natural sua**: o Manager lê a frase do teste e a
   resposta esperada no próprio card, então acertaria de memória e não provaria nada. As frases:
   *"quais as possibilidades"* · *"instala o Serena aqui"* · *"tô com pouco crédito"* seguido de
   *"chegamos ao final do ciclo"* (a segunda **não** pode trocar o elenco) · *"agora não"* a uma
   sugestão de ferramenta, repetida numa sessão seguinte.
3. **Decidir os três cards que nasceram do painel de 07/ago** — `T-033` (template v2 não é gerado),
   `T-034` (painel não fecha 3 vendors fora do Claude; Loop A escolhe planner cego), `T-035`
   (procedência inflada + a fumaça do `instalar.md` na forma insegura).
4. **`T-013`** — exige duas janelas simultâneas suas; nada a fazer sozinho aqui.

**Distribuição:** 0.19.0 **instalada e no GitHub** (`b62b39c`) e presente nos **três hosts** —
Claude (cache `0.19.0`), Codex (`plugin add`, enabled) e Kimi (cópia em `~/.agents/skills/orq/`).
Quem instalar do repositório público recebe a 0.19.0.

**Commitado e no GitHub:** 0.17.0 (`10ecef2`) · 0.18.0 (`7674cab`) · 0.19.0 (`8bef7f9`) ·
board (`7c14aa9`) · `T-032` (`b62b39c`). **Nada pendente de push.**

⚠️ **O checkpoint de 07/ago tem mudanças ainda NÃO commitadas** (este índice, log, gotchas,
`_elenco.md`, board) — o dono não pediu commit.

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
| [`wiki/threads/T-026-host-alternativo.md`](wiki/threads/T-026-host-alternativo.md) | **Ativo** — o Orquestra rodando fora do Claude Code. Instalação multi-host (0.18.0, provada no Codex) e elenco host-agnóstico (0.19.0 — **liberada, instalada nos três hosts e revisada pelo painel em 07/ago; reprovada 3/3, achados em `T-033`/`T-034`/`T-035`**). **A thread é longa: o `⏭️ RETOMAR AQUI` vivo é o último do arquivo** — os anteriores estão marcados como superados |
| [`wiki/threads/T-023-reload-vs-restart.md`](wiki/threads/T-023-reload-vs-restart.md) | **Implementado na 0.14.0**, reprovado no review e corrigido — evidência por componente no lugar de regra binária |
| [`wiki/threads/T-020-perfis-elenco.md`](wiki/threads/T-020-perfis-elenco.md) | **Entregue na 0.16.0** — perfis de elenco (`padrao` · `economia`) trocados por frase |
| [`wiki/threads/_noturno.md`](wiki/threads/_noturno.md) | Manifesto **expirado** + relatório do modo noturno de 2026-07-30 — não abrir run novo a partir dele |
| [`snapshot-2026-07-31-releases-0.14-0.16.md`](snapshot-2026-07-31-releases-0.14-0.16.md) | **Marco**: estado exato ao fim das três entregas do dia + as três lições de método |

## A distinção que faz isto funcionar

O **log** é imutável e responde *"o que aconteceu em tal dia"*. A **página de tópico** é reescrita e
responde *"como funciona hoje"*. Sem a página, a segunda pergunta vira arqueologia no log.

Nunca guarde aqui o que é **derivável** (diff, `git log`, lista de arquivos, o código atual) — a fonte
já tem. Guarde o *porquê* e as *consequências*.
