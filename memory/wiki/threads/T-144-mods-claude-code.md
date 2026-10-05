# T-144 — Mods do Claude Code: o que serve ao Orquestra sem ferir a portabilidade

**Frente:** `@frente-mods` · **Host:** `@claude` · **Trilha:** sistema · **Estado:** `[!]` — análise pronta, decisão do dono

## Objetivo

O dono trouxe a doc oficial de mods (`code.claude.com/docs/en/plugins/mods`) e dois vídeos
(*"Claude Code Mods Are Game Changers. Set Up These 5 NOW."* e *"Claude Mods — The Biggest Claude
Code Upgrade!"*) e pediu para avaliar se dá para melhorar o Orquestra nesse sentido, **lembrando que
o Orquestra é para qualquer LLM**.

Fontes: doc de mods (overview, reference, events) lida integralmente. Dos vídeos só o título foi
acessível — sem transcrição; a análise se apoia na doc oficial.

## O que é um mod (fatos verificados na doc, 2026-10-04)

- Plugin com funções JS/TS que rodam **dentro** do processo do Claude Code: `register(on)` em
  `hooks/register.js`, apontado por `"modules": [...]` **no mesmo `hooks/hooks.json`** dos settings hooks.
- Pode: desenhar painel/faixa acima do prompt; reescrever a interface; interceptar `tool.call`
  (negar, responder sem rodar, **segurar e perguntar ao usuário com botões** via `$.ui.ask`);
  `/comando` que roda sem turno do modelo; ler uso por requisição (`turn.step`) e
  `$.session.usage()` → `context.percent`, `rateLimits`; `.catch` para falhar fechado.
- `turn.step`/`turn.complete` trazem `e.agentId` quando é subagente; `tool.call` dispara também
  para subagente, mas a doc **não** diz se traz `agentId` — a pergunta aberta do `T-002` continua aberta.
- **Exige Claude Code ≥ 2.1.287.** A máquina do dono está em **2.1.280** → hoje um mod nem carrega.
- Desenha só no terminal e na aba Code do Desktop; no VS Code, `claude -p` e nuvem os hooks rodam,
  mas nada aparece. Não há equivalente em Codex, Gemini, Pi ou Orca.
- Não é sandboxed, roda com as permissões do usuário, e pode aprovar tool call que um `ask` pediria.

## Análise contra o Orquestra

**Restrição central:** mod é exclusivo do Claude Code. Logo, **nenhuma regra do Orquestra pode
morar só num mod**. O padrão que o produto já usa (`context-guard.py`, `kanban-status.sh`) é o
certo: a lógica fica num script portátil e cada host tem uma "boca" fina.

**Risco concreto de empacotamento:** o `modules` entra no `hooks/hooks.json` do `orq`, que o
Codex também lê. Comportamento do Codex diante da chave desconhecida não foi testado, e atualizar
plugin já derruba a sessão Codex (`T-093`). Por isso o mod deve ser **plugin separado** no mesmo
marketplace, opt-in, e o `orq` que o Codex instala não muda.

### Candidatos, por valor/risco

| # | Ideia | Lacuna que fecha | Precisa de mod? | Risco |
|---|---|---|---|---|
| A | Guardião de contexto no Claude: mod lê `$.session.usage()` e aplica as faixas 55/60/70 **consultivas** | `T-054` — hoje o guardião só age no Codex; no Claude resta "~50% sem telemetria" | **Sim** — settings hook do Claude não recebe o uso de contexto; mod troca parsing de transcript (instável) por API oficial | baixo: nunca bloqueia, não toca no Codex |
| B | Bloqueios de segurança (`push`, merge, deploy, SQL de escrita) | `T-001` (e destrava `T-006`); arquitetura: "Enforcement: quase nenhum" | **Não** para o núcleo — script portátil + `PreToolUse` nos dois hosts. Mod só acrescenta a pergunta com botões no lugar do "negado" seco | alto (segurança): piso `pesada`, gate extra; `PreToolUse` no Codex ainda sem prova |
| C | Faixa "Esperando você" acima do prompt | — | Sim | não recomendado agora: a statusline já mostra o board e o canvas visual foi recusado como cosmético |

### O que não fazer com mods

- Interceptar a frase do dono (`prompt.submit`) para rotear sem o modelo: sequestra a interface natural.
- Aprovar tool call automaticamente (`tool.check` → `allow`): é `bypassPermissions` com outro nome.
- Trocar o modelo por requisição (`turn.step`) fora do `_elenco.md`.

### Achado lateral

O Claude Code ≥ 2.1.277 lê `AGENTS.md` nativamente (built-in `cc-plugin-agents-md`). Com
`CLAUDE.md` presente, por padrão só o `CLAUDE.md` carrega, então **não há duplicação hoje** neste
repo (os dois são idênticos, 7169 bytes). Abre uma opção futura, fora deste card: o `/orq:init`
tratar `AGENTS.md` como fonte única cross-vendor. Decisão de `AGENTS.md`/`CLAUDE.md` é do dono.

## Recomendação do Manager

1. **Planejar A primeiro**: risco baixo, fecha lacuna conhecida, não toca no Codex.
2. **B como card próprio depois**, reaproveitando o `T-001`: núcleo portátil primeiro, mod de
   pergunta com botões opcional por último.
3. **C fica de fora.**
4. Pré-requisito de qualquer mod: atualizar o Claude Code para ≥ 2.1.287 (mudança global, do dono).

## Escopo revisto pelo dono (2026-10-04, segunda mensagem)

O dono trouxe os exemplos do vídeo (`~/Downloads/nateherk-claude-code-mods`: Cache Keeper,
Recording Mode, Goal Meter, Collision Guard — MIT, Nate Herk) e redirecionou o card: **o que mais
importa é o Goal Meter**. Dor literal: no `/goal` ele se perde — não sabe em que nível do
desenvolvimento está nem o que já foi feito nos objetivos. Quer algo parecido funcionando **no
Claude e no Codex**, e visível também na IDE (Orca, `T-141`).

O card passou de "avaliar mods" para **medidor de progresso portátil**. Os candidatos A/B/C acima
ficam registrados como ideias, sem card; não foram aprovados nem recusados.

**Goal Meter, em uma frase:** ferramenta `tasks` (plan/add/start/done/drop, pesos S/M/L 1/2/3),
estado JSON por sessão em `~/.claude/mods-data/goal-meter/`, faixa + rodapé + painel, lembrete
após 4 chamadas sem plano. Tudo dentro de um mod — portanto só Claude ≥ 2.1.287.

**Hipótese do Manager levada ao planner (não é decisão):** o núcleo é um ledger portátil + CLI;
as vistas são bocas por host. O Orquestra já tem dois níveis que o Goal Meter não tem — fase do
ciclo e passos verificáveis do plano aprovado —, então o ledger pode nascer do plano.

**Roteamento:** Normal · trilha `sistema` (misto → sistema) · faixa inicial `pesada` (desenho aberto).
Planner·sistema = `gpt-6-astra@xhigh` via Codex Companion, read-only, `--fresh`.

## Vínculo do Companion (planner)

`{card: T-144, papel: planner·sistema, jobId: task-mutuafj8-6cws86, threadId:
01a1070a-4151-7de1-8213-5420a79b1b6b, status: 0 (terminal, exit 0)}` · `touchedFiles: []`.
A chamada passou de 600 s e o harness a moveu para background; terminou sozinha, sem retry.
Continuação do planner neste card: `--resume-thread 01a1070a-4151-7de1-8213-5420a79b1b6b`.
Plano íntegro em `docs/plano_T-144-medidor-progresso.md`.

## Auditoria do Manager (antes do gate)

O plano é sólido: núcleo `orq/scripts/progress.py` (stdlib), ledger por card/goal em
`<frente>/.orq/progress/` autoignorado, fase vinda do board e % dos passos do plano aprovado,
lembrete consultivo por hook, segmento na statusline do Claude, `watch` para o Orca, mod
separado só na fase 4, ETA e goal check fora. Pontos que levo ao dono:

1. **Atrito de escrita.** Toda mutação exige `--ledger ABS --session-key KEY --expect-revision N`.
   O Goal Meter funciona porque marcar tarefa custa uma chamada de um argumento; se custar três
   identificadores a cada passo, o Manager pula atualização e a barra mente. Proposta: com dono
   único, lock + troca atômica bastam; `--expect-revision` vira opcional e o ledger é achado por
   `--card T-NNN`/`--run` dentro da raiz da frente.
2. **Codex não ganha barra fixa.** A statusline do Codex só aceita itens nativos e não roda script
   (comprovado em `codex.md:26` e na referência de config). No Codex a vista contínua é o `watch`
   num terminal ao lado (Orca ou outro). Dizer isso ao dono sem rodeio.
3. **A fase 1 sozinha não resolve a dor** — só dá `show` sob demanda. Proposta: subir o `watch`
   (leitor puro, barato e independente de host) para a fase 1; é a única vista contínua que vale
   para Claude, Codex e Orca ao mesmo tempo.
4. **Errata factual:** o plano põe o schema em `orq/scripts/schemas/`; o diretório existente é
   `orq/schemas/` (`audit-ledger-v1.json`). Corrigir para `orq/schemas/progress-ledger-v1.json`.
5. Faixa: desenho fechado e não é Alto risco → rebaixa a `normal` na aprovação (no host Claude as
   três faixas são `sonnet`, então muda só a cerimônia).

Fatos novos registrados pelo planner: há dois Codex na máquina (`/usr/local/bin/codex` 0.156.1 e o
primeiro do PATH 0.160.0); MCP de plugin existe no Codex, mas não foi exercitado.

## Aprovação (2026-10-04)

O dono aprovou: *"Perfeito, aprovado. Siga com as recomendações"* — fases 1–3, os três ajustes,
`.orq/progress/`, sem ETA, Codex com `watch` no lugar de barra fixa. Exigiu **worktree paralela
numa branch isolada**, porque há outras threads abertas no Codex e no Claude.

- Branch `claude/t144-medidor-progresso`, a partir da `main` em `4e58e7f`.
- Worktree `/Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra-worktrees/t144-medidor-progresso`,
  **fora** do checkout principal, porque worktree aninhada em `.claude/worktrees/` quebra a suíte da
  `main` (`T-142`).
- ERRATA no topo do plano, que vence o corpo. Faixa rebaixada `pesada → normal`: o desenho está fechado
  e o card não é Alto risco.
- O board e esta thread ficam no checkout principal; a worktree recebe só código.
- Sem commit em `orq/` até o dono atribuir a versão.

O dono também pediu um prompt para consultar o Codex sobre como tornar o medidor mais efetivo
naquele host. O parecer vai para `docs/parecer_T-144-codex.md`, que é arquivo novo de dono único;
o Codex não escreve na worktree nem no board.

## Fase 1 — handoff do implementer e auditoria do Manager (2026-10-04)

O implementer·normal (`sonnet`) entregou no working tree da worktree, sem commit:
- **Novos:** `progress.py` (1563 linhas), `orq/schemas/progress-ledger-v1.json`,
  `test_progress.py` (102 testes) e `references/progress.md`.
- **Alterados:** `kanban-status.sh` (modo `--card-state`), `test_kanban_status.py` (+14),
  `SKILL.md`, `plan-next.md`, `implement-next.md` (seção 0b) e `checkpoint.md`.

Gates reconferidos pelo Manager **na worktree**: suíte 563 OK, `validate --strict` ok, lint ok.
O checkout principal ficou sem nenhuma mudança em `orq/`.

**Smoke manual do Manager** (repo descartável, ciclo `begin → plan → start → done → show/watch`):
funciona, e o git do consumidor fica limpo. **Defeito de UX encontrado:** com uma tarefa em
execução, a fase continua "pronto para iniciar", porque a atividade só muda por `phase` explícito.
É a contradição que o card existe para eliminar.

**Desvios de contrato decididos pelo implementer**, a confirmar na revisão:
- campo `closure` no ledger;
- goal sem título (`goal <8 do run_id>`);
- `add` só com `scope_change`.

## Revisão R1 da fase 1 (2026-10-04)

`{card: T-144, papel: reviewer, jobId: task-mutygupo-0nsd17, threadId:
01a10775-57a7-7713-91b9-aa1cd74f3e3a, status: 0}` · `touchedFiles: []`. O revisor rodou a suíte
em Python 3.9.6: 563 OK. **Veredito: REPROVADO.**

O Manager conferiu cada achado no código; os cinco foram aceitos.
- **B1** `progress.py:427`: sob `[~]`, a atividade `ready` com passo ativo ou concluído mostra
  "pronto para iniciar". O Manager já tinha reproduzido no smoke.
- **B2** `:1097`: a checagem de ignore testa só `v1/cards/probe.json`. Um `.gitignore` parcial deixa
  goal e lock visíveis no Git, contrariando um critério de aceite.
- **R1** `:1459`: a ajuda do `claim` chama a chave de "do dono", enquanto o `progress.md` pede chave
  nova; seguindo a ajuda, o escritor antigo continua autorizado.
- **R2** `:1087`: a contenção verifica só `.orq/progress`; um symlink em `v1` grava fora da frente.
- **R3** `:1443`: erro de argumento sai em texto de usage, sem a linha JSON prometida.

Também aceitos pelo revisor: `closure`, goal identificado pelo UUID, `add` só com
`scope_change` (a referência explica a origem), a chave de 64 hex e os códigos de saída 2/3/4.

## Correções da R1 aplicadas (2026-10-04)

O implementer corrigiu os cinco itens em RED/GREEN, com 18 testes novos (`test_progress.py` agora
tem 120). O Manager reconferiu na worktree:
- **Gates:** suíte 581 OK, `validate` 0, lint 0. O checkout principal segue com 0 arquivos alterados
  em `orq/`.
- **Smoke B1:** `implementação · 1/3 · 50%`.
- **R3:** o erro de uso sai como uma linha JSON, com exit 2.

Rechecagem pelo mesmo reviewer (`--resume-thread 01a10775-…`) disparada: rodada 2 de 2.

## Revisão R2 da fase 1 (2026-10-04) — teto de rodadas atingido

`{card: T-144, papel: reviewer, jobId: task-mutz5p69-cayg23, threadId:
01a10775-57a7-7713-91b9-aa1cd74f3e3a, status: 0}` · `touchedFiles: []`. O revisor rodou a suíte em
Python 3.9.6: 581 OK. **Veredito: REPROVADO.**

Resolvidos: B1, R1 e R3. A auditoria do Manager no código confirmou os três que sobraram:

1. **Lock por alias** (`progress.py:896` `lock_path_for`): um `--ledger` passado por um diretório
   symlink para `goals` cai no lock lateral, não no `v1/locks/`. Duas mutações com a mesma revisão
   esperada passaram e a segunda apagou a primeira. Correção mínima: canonicalizar com realpath
   antes de inferir layout e lock, e recusar mutação fora do layout padrão.
2. **Sondas com nomes fictícios** (`:1123` `storage_probes`): um `.gitignore` com `*` e exceções
   para o nome real do ledger escapa. Isso exige configuração adversária, então o risco é baixo;
   corrigir é barato, sondando o destino real antes de cada escrita.
3. **Contradição de instrução** (`references/progress.md:163`): a doc diz que o `begin` recusa "sem
   escrever nada", mas o código cria o `.gitignore` antes de checar o symlink em `v1`. Correção:
   checar a contenção de todos os componentes antes de qualquer escrita.

## 3ª rodada autorizada e troca de elenco (2026-10-04)

- **Rodada final:** o dono escreveu *"autorizado, segue com a 3ª rodada"*. Os três itens foram ao
  mesmo implementer: lock canônico com recusa de mutação fora do layout, sondas nos destinos reais e
  nenhuma escrita antes da contenção.
- **Troca de elenco:** na mesma mensagem, o dono trocou `planner·sistema` e `reviewer` do host
  Claude para `gpt-6.1-sol@xhigh`, como desvio do `padrao`, comprovado no rollout. Detalhes em
  `_elenco.md` e no log.
- **Efeito no card:** a rechecagem final retoma a MESMA thread do reviewer
  (`01a10775-57a7-7713-91b9-aa1cd74f3e3a`) com `--model gpt-6.1-sol --effort xhigh`. O papel e o
  histórico R1/R2 continuam; muda só o modelo. Se o Companion recusar a troca de modelo no resume,
  declarar e abrir uma task `--fresh` com o histórico no briefing.

## Correções da 3ª rodada (2026-10-04)

O implementer corrigiu os três itens em RED/GREEN (19 vermelhos na rodada RED):
- lock canônico por realpath; mutação fora do layout sai 4 (`destino-fora-do-layout`); lock lateral
  removido;
- sondas nos destinos reais, repetidas em toda mutação;
- `ensure_storage` só lê antes da primeira escrita.

O Manager reconferiu na worktree:
- **Gates:** suíte 587 OK, `validate` 0, lint 0, `git diff --check` 0.
- **Checkout principal:** sem mudança em `orq/`.
- **Smoke do alias:** `pause` via diretório symlink gravou no caminho canônico, sem lock lateral.

Limitações declaradas: TOCTOU local entre a conferência e o `mkdir`, só POSIX exercitado, Apple Git
2.50.1. Rechecagem final disparada: mesma thread do reviewer, agora com `gpt-6.1-sol@xhigh`.

## Rechecagem final R3 (2026-10-04) — reviewer agora em Sol 6.1

`{card: T-144, papel: reviewer, jobId: task-muu55pej-5xoee8, threadId:
01a10775-57a7-7713-91b9-aa1cd74f3e3a, status: 0}` · `touchedFiles: []`.

O resume aceitou a troca de modelo. O rollout da thread registra `gpt-6.1-sol` nesta rodada e
`gpt-6-astra` nas anteriores, com effort `xhigh`. O wrapper informou que `--wait` é controle do lado
Claude, removido antes do `task`; isso explica a "inconsistência" anotada no log.

**Veredito: REPROVADO.**
- Itens 1 (lock canônico) e 3 (nenhuma escrita antes da contenção): RESOLVIDOS.
- TOCTOU local e cobertura de plataforma: aceitos para a fase 1.
- **Resíduo do item 2:** `destination_probes` (`progress.py:1144`) sonda o temporário com o token
  fixo `TEMPORARY_PROBE_TOKEN`, mas `write_ledger` (`:964`) cria o nome com trecho aleatório pelo
  `NamedTemporaryFile`. Um `.gitignore` com `*`, `!v1/`, `!v1/cards/`, `!v1/cards/*.tmp` e
  `v1/cards/*.probe*.tmp` passa na sonda, e o temporário real aparece `??` durante a escrita ou
  depois de um crash.

**Auditoria do Manager — RISCO, não bloqueador:**
- O cenário exige um `.gitignore` escrito para derrotar a sonda; o `begin` gera `*`, e não há caminho
  orgânico até ele.
- O temporário vive milissegundos, ou sobra só após um crash.
- O ledger guarda apenas títulos genéricos, por desenho.
- As três rodadas foram estreitando o mesmo item até casos cada vez mais artificiais.
- A correção é pequena (conferir o nome realmente reservado antes de escrever o JSON) e cabe na
  fase 2, que já reabre o `progress.py`.

## 4ª rodada autorizada + parecer do Codex (2026-10-04)

O dono disse: *"pode rodar a 4ª rodada. restante prossiga."* O resíduo do temporário foi ao mesmo
implementer: conferir o nome realmente reservado antes de escrever o JSON. "Restante" = docs e,
depois, o commit; o número da versão ainda depende do ok dele.

**Parecer do Codex** em `docs/parecer_T-144-codex.md`. Arquivo único; a worktree, o board e a
config ficaram preservados. Auditoria do Manager:

| # | Sugestão | Decisão |
|---|---|---|
| 1 | Não espelhar o ledger no plano nativo; um espelho **unidirecional e opt-in** via `update_plan` alimentaria o item nativo `task-progress` da statusline do Codex | Confirma o plano. O espelho opt-in é a **única via para barra nativa no Codex** → decisão do dono antes da fase 3 |
| 2 | `get_goal` existe no Codex; o Manager pode consultá-lo para vincular o ledger ao Goal nativo; não existe hook de Goal | Adotar como consulta **opcional** no procedimento, com o fallback atual |
| 3 | Dedupe do `PostToolUse` por `(session_id, turn_id, tool_use_id, hook_event_name)`; `SessionStart` sem ID de evento, `source` inclui `fork`; schemas iguais em 0.156.1/0.159.2/0.160.0 | Adotar na fase 2 (já prevista; agora com as chaves exatas) |
| 4 | Escrita em `.orq/progress` sob `workspace-write` é compatível, mas sem prova prática | Mantém-se como aceite da validação no Codex |
| 5 | MCP como piloto só se o shell causar omissões | Fora até haver evidência de atrito |
| 6 | `watch` em terminal dedicado; Activity e notificações não mostram percentual | Confirma a ERRATA |
| 7 | **Recibo de mutação com projeção compacta** (`T-144 · revisão · 5/8 · 69%`), para dispensar um `show` extra | Ganho barato contra o modo de falha "Manager pula marcação" → **1º item da fase 2** |

Achado lateral do parecer: há um **terceiro** Codex na máquina, o do App
(`/Applications/ChatGPT.app/.../codex-cli` 0.159.2).

**Versão:** nenhuma branch subiu além de `0.27.11`. Proposta ao dono: `0.28.0` (feature nova).

## Rechecagem R4 (2026-10-04) — APROVADO_COM_RESSALVAS

`{card: T-144, papel: reviewer, jobId: task-muu77ya1-pzxzrk, threadId:
01a10775-57a7-7713-91b9-aa1cd74f3e3a, status: 0}` · `touchedFiles: []`. O rollout dos últimos
`turn_context` registra `gpt-6.1-sol` / `xhigh`.

O resíduo do item 2 foi RESOLVIDO (`progress.py:974`): o revisor reproduziu `pause` e `begin`, os dois
saíram com exit 4 citando o temporário real, e nenhum `.tmp` sobrou. Não houve regressão nos itens
1 e 3, em B1, R1 e R3, nem nas instruções. Ele também rodou 593 testes em Python 3.9.

O Manager confirmou antes, na worktree: 593 OK, `validate`, lint e `diff --check` com 0. No smoke
do cenário adversarial, o `pause` saiu com exit 4 sem deixar `.tmp`.

**Ressalvas aceitas como risco conhecido:**
- `:969`: com um `.gitignore` parcial e adversário, um `git add -A` concorrente de outro host pode
  indexar o temporário **vazio** no instante entre a reserva e a consulta. A combinação é rara, e o
  conteúdo é vazio.
- `progress.md:181`: um `begin` recusado pode deixar diretórios vazios e o lock, ignorados e
  documentados.

**Resultado das rodadas:** R1 reprovou com 5 achados; R2 resolveu 3; R3, já em Sol 6.1, resolveu
mais 2; R4 fechou o resíduo. Suíte 563 → 593.

## Docs da fase 1 (2026-10-04)

O `orq-docs` (sonnet), na worktree:
- **`arquitetura.md`:** seção "Medidor de progresso" e `progress.py` na tabela de scripts;
  contagens fixas de testes trocadas por "a suíte descoberta".
- **`README.md`:** parágrafo curto no board e linha `scripts/`.
- **`distribuicao.md`:** árvore com `progress.py` e `schemas/`.
- **`references/progress.md`:** duas omissões completadas — `ledger-grande` na gravação sai com
  exit 2; `escopo-divergente` no `begin`, e o que o Manager faz.

Gates conferidos pelo Manager: suíte 593 OK, `validate`, lint e `diff --check` com 0. Working tree
com 13 arquivos (9 alterados, 4 novos); checkout principal sem nada em `orq/`.

As contagens envelhecidas fora do escopo viraram o card `T-145` no backlog. O `arquitetura.md:3`
("hoje `0.25.0`") entra junto do bump.

## Fechamento da fase 1 (2026-10-04)

O dono escreveu: *"confirmado, pode usar a 0.28.0 e commitar"*.
- **Bump nos 4 lugares, na worktree:** `plugin.json`, `marketplace.json`, Status do README e
  `memory/MEMORY.md`. O `arquitetura.md:3` também foi atualizado.
- **Gates:** suíte 593 OK, `validate --strict` OK, lint OK, `diff --check` 0.
- **Commit local `ba523e9`** `feat(0.28.0): medidor de progresso portatil — fase 1` na branch
  `claude/t144-medidor-progresso`, com 16 arquivos. **Sem push, publicação nem instalação.**
- **Board:** `T-144` foi para `[?]`, já sem marcador de host. As fases seguintes viraram cards próprios
  no backlog, ambos com o plano já aprovado aqui: `T-146` (fase 2) e `T-147` (fase 3).
  - O 1º item da fase 2 é o recibo com projeção compacta (parecer do Codex, item 7).
  - Antes da fase 3, o dono decide se quer o espelho opt-in via `update_plan` no Codex.
- **Fora do commit:** `docs/plano_T-144-medidor-progresso.md`, `docs/parecer_T-144-codex.md` e esta
  thread continuam não rastreados no checkout principal. Board e thread pertencem ao principal, e
  copiá-los para a branch conflitaria com os arquivos não rastreados no merge.

**Como o dono valida a fase 1:** durante a fase 2 (`T-146`), o Manager registra o plano dela no
medidor e entrega a linha do `watch`. O dono a abre num terminal ao lado (Claude, Codex ou Orca) e
confere quatro coisas:
- a fase mostrada acompanha o trabalho;
- os passos mudam conforme as marcações;
- o percentual se apresenta como "do plano";
- 100% não aparece como "pronto".

## T-146 — fase 2 em Loop B (2026-10-04)

O dono escreveu *"pode implementar a fase 2"*. O `T-146` entrou em `[~]` `@claude`, na mesma
worktree e branch. O plano é o do T-144, mais a ERRATA e os itens adotados do parecer do Codex
(recibo com projeção; dedupe por `session_id`/`turn_id`/`tool_use_id`/`hook_event_name`; `get_goal`
opcional). O resíduo do temporário saiu do escopo: foi resolvido na R4 da fase 1.

**Medidor do próprio card** (`progress.py` da branch, porque o plugin instalado é o 0.27.10):
- `ledger_path`: `/Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/.orq/progress/v1/cards/T-146.json`
- `run_id`: `d391006d-eb4b-42d5-8730-07cf1d65dc20` · `session_key`: `CHAVE_LOCAL_PRESERVADA_NO_LEDGER_IGNORADO`
- Passos P01–P09, pesos M M L S M S S M S: recibo, bind, hook, `hooks.json`, statusline, init,
  procedimento, revisão e docs. Fase `implementation`.
- O implementer trabalha **em blocos** (P01+P02 → P03+P04 → P05+P06+P07), sempre o mesmo agente,
  para o medidor ter granularidade. O Manager marca `start` no despacho e `done` depois de conferir
  cada bloco.

Fatos dos payloads, da doc oficial do Claude e do parecer do Codex:
- `SessionStart` traz `session_id` e `source` (startup, resume, clear, compact, fork).
- `PostToolUse` traz `tool_use_id`; o Codex também traz `turn_id`.
- `agent_id` só aparece em subagente.

### T-146 bloco 1 aceito (2026-10-04)

P01 (recibo com `view`/`view_revision`) e P02 (`bind` + `sessions/` + schema
`progress-binding-v1.json`) foram entregues. O Manager conferiu a suíte (628), `validate`, lint e
`diff --check`: todos 0. Marcou `done` com `--evidence-ref T-146-bloco1-suite628`, e o recibo já veio
com `view` `◎ T-146 · implementação · 2/9 · 27%`. As 9 decisões do implementer foram aceitas.

**Decisão do Manager para o bloco 2 — duas chaves:**
- A *chave de dono* (do `begin`, na thread) autoriza as mutações e sobrevive a `/clear`.
- A *chave da sessão nativa* (`sha256(host\0session_id)`) só serve ao `bind`.
- O `SessionStart` emite a chave nativa, nunca o ID bruto, e o `bind` ganha `--session-key`.

### T-146 bloco 2 (2026-10-04)

O implementer entregou `progress-hook.py` (adaptador fino, com a regra em `progress.py:handle_hook`)
e duas entradas próprias no `hooks.json`, `PostToolUse` e `SessionStart`, para as 5 fontes. As 6
entradas do guardião ficaram intactas. Na suíte, o único teste preexistente alterado foi um do
`test_context_guard`, que fixava "1 grupo por evento".

Conferência do Manager: suíte 669, `validate`, lint e `diff --check`, todos com exit 0. **P04 `done`**
(evidência `T-146-bloco2-suite669`); 3/9 = 33%.

**P03 fica aberto, com três correções do Manager:**
- **C1:** sem medidor, o hook custa ~0,13 s por chamada de ferramenta em qualquer projeto. Fazer a
  saída rápida antes de importar o núcleo; alvo abaixo de 50 ms.
- **C2:** a sessão que roda o `begin` nunca recebe a chave nativa. Anunciar uma vez no `PostToolUse`,
  com um marcador `.anunciada-<chave>`.
- **C3:** no `bind`, `--session-key` passa a `--native-key`, para não confundir com a chave de dono.

Limitação aceita e a documentar: o `cwd` da sessão fora de `front_root` não encontra o binding.

### T-146 bloco 3 e correções do P03 (2026-10-04)

**Entregue:**
- **C1:** saída rápida antes de importar o núcleo. O Manager mediu 36 ms sem medidor, com
  `/usr/bin/python3`; antes eram ~130 ms.
- **C2:** anúncio único da chave nativa no `PostToolUse`, com o marcador `.anunciada-<chave>.json`.
- **C3:** `bind --native-key`.
- **P05:** subcomando `statusline` e segmento no `statusline.sh`, com pré-filtro em shell; custa
  +110 ms por render quando a sessão está vinculada.
- **P06:** o `init.md` instala o trio indivisível, com backup e rollback.
- **P07:** `get_goal` opcional, `bind` depois do `begin`, `view` nos marcos; `codex.md` registra que
  não há espelho.

**Conferência do Manager:** suíte 715 (+46), `validate`, lint e `diff --check` com 0; o principal
segue sem mudança em `orq/`. Passos P03, P05, P06 e P07 em `done` (`T-146-bloco3-suite715`), fase
`review` e P08 em `start` (reviewer `gpt-6.1-sol`). Está em 7/9 = 80%.

**Revisão:** disparada com `--fresh` (card novo), Sol 6.1 `@xhigh`.

### T-146 revisão R1 (2026-10-04) — REPROVADO

`{card: T-146, papel: reviewer, jobId: task-muuci9ty-k9b9np, threadId:
01a108dd-27fd-7e21-ac45-d912f70f3984, status: 0}` · `touchedFiles: []`. O rollout confirma
`gpt-6.1-sol` e `xhigh`. O revisor reproduziu os 715 testes e confirmou dois pontos: o contrato dos
hooks nos dois hosts (as 6 entradas do guardião iguais às do commit-base) e Python 3.9 com os shells.

**Bloqueadores aceitos pelo Manager:**
- **B1** `progress.py:1804/:1860`: hook e statusline leem o `ledger_path` do binding sem contenção.
  Um binding adulterado abriu um arquivo de fora.
- **B2** `:1756`: a elegibilidade é checada antes do lock do binding. Um `plan` no meio do caminho
  ainda dispara o lembrete.
- **B3** `init.md:655`: o rollback apaga ou restaura sem conferir alteração concorrente.
- **B4** `progress.md:257`: o texto diz "planejamento nunca conta", mas goal conta em `planning`.

**Riscos corrigidos:**
- **R1** `statusline.sh:133`: o pré-filtro é lexical, então um alias some da barra.
- **R3** `progress.md:255`: a doc promete contadores preservados com chave nativa nova.

**Riscos aceitos:**
- custo de render numa sessão não vinculada em frente com `sessions/` (~+100 ms);
- anúncio duplicado `SessionStart` + `PostToolUse`;
- T-093, preexistente.

### T-146 correções da R1 (2026-10-04)

**Correções aplicadas, com RED/GREEN:**
- **B1:** `_read_bound_ledger` com contenção antes de abrir. Residual: TOCTOU entre o realpath e o
  `open`.
- **B2:** reconferência da elegibilidade dentro da seção crítica do binding, sem pegar o lock do
  ledger (snapshot via `os.replace`).
- **B3:** rollback do `init.md` por hash por arquivo, preservando e relatando divergência.
- **B4 e R3:** texto do `progress.md`.
- **R1:** `cd -P`/`pwd -P` na statusline.

O Manager conferiu: suíte 730 (+15), `validate`, lint e `diff --check` com 0; o principal segue
intocado. Rechecagem R2 disparada no mesmo thread do reviewer.

### T-146 rechecagem R2 (2026-10-04) — REPROVADO, teto de rodadas atingido

`{card: T-146, papel: reviewer, jobId: task-muue21sl-jfb0mg, threadId:
01a108dd-27fd-7e21-ac45-d912f70f3984, status: 0}` · rollout confirma `gpt-6.1-sol`/`xhigh`.

- **Resolvidos:** B1, B2, B4, R1 e R3. O residual de TOCTOU do B1 foi aceito pelo revisor, com o
  mesmo critério da fase 1.
- **Não resolvido — B3:** o `init.md` (`:652`) coleta o hash do arquivo instalado **depois** do `mv`.
  Um terceiro que troque o arquivo nessa janela contamina a referência, e o rollback apaga o
  arquivo dele.
  - Correção: registrar o hash do `.orq_new` **antes** da promoção.
- **Ambiguidade nova:** `init.md:644` ("nunca restaure um sozinho") contra `:665` (decisão por
  arquivo).
  - Correção: explicitar a exceção para preservar a alteração concorrente.
- **Auditoria do Manager:** é texto de instrução no `init.md`, num procedimento raro e interativo.
  O cenário é estreito, mas a correção é trivial e bem delimitada.

### T-146 rechecagem R3 (2026-10-04) — APROVADO_COM_RESSALVAS

`{card: T-146, papel: reviewer, jobId: task-muuj60ej-87kik0, threadId:
01a108dd-27fd-7e21-ac45-d912f70f3984, status: 0}` · rollout `gpt-6.1-sol`/`xhigh`.

- **(a) B3 resolvido** (`init.md:660`): o revisor trocou o `progress.py` entre o `mv` e a comparação;
  a referência pré-`mv` detectou a troca e o arquivo do terceiro ficou intacto.
- **(b) Ambiguidade resolvida** (`init.md:644/:685`).
- **Ressalva aceita:** a janela entre a conferência e o `mv`/`rm`, pelo mesmo critério do TOCTOU.
- **Saldo das rodadas:** R1 com 4 bloqueadores + 5 riscos; R2 resolveu 5 de 6; R3 fechou o `init.md`.
  Suíte em 730.

**Ledger:** P08 `done`, fase `docs`, P09 em `start` → 8/9 = 93%. O `orq-docs` (sonnet) foi
disparado. Versão proposta ao dono: `0.29.0`, por trazer feature nova (hook e statusline) sobre a
0.28.0 não publicada.

### T-146 docs (2026-10-04)

O `orq-docs` atualizou `arquitetura.md` (medidor completo e riscos aceitos), o `README` e o
`distribuicao.md`. O Manager desfez uma ambiguidade apontada pelo docs: o `progress.md` dizia "logo
depois do `begin`", e o §0b vincula depois de gravar a chave. O texto passou a "antes ou depois do
`plan`, tanto faz", e o teste de doc foi atualizado.

⚠️ **Erro do Manager, corrigido:** marquei P09 `done` no mesmo comando que rodou os gates, e a suíte
tinha falhado (teste de doc fixando a frase antiga). Depois fiz `reopen`, a correção, os gates
verdes (730), `start` e `done`, com `T-146-docs-suite730-verde`. O medidor registrou a sequência,
e a `reopen` exigiu um novo `start`, como o contrato manda. **Lição:** nunca encadear `done` no mesmo
comando dos gates.

Ledger: 9/9 = 100% do plano, fase `docs`. O card **não** está DONE: falta a versão, o commit e a
validação do dono.

## Checkpoint e handoff para a conciliação (2026-10-04)

O dono pediu checkpoint e handoff: ele vai unificar na `main`, em outro chat, as branches que
correm em paralelo. Antes, ele confirmou que o bump fica **só na branch**: a versão de uma branch é
candidata, e o número final é dado na ordem de merge.

- **Commit `064e726`** `feat(0.29.0): medidor de progresso — fase 2, hook consultivo e statusline`,
  na branch, com o bump nos 4 lugares e em `arquitetura.md:3`. Suíte 730, `validate`, lint e
  `diff --check` com 0. Worktree limpa.
- **`T-146` → `[?]`**, sem marca de host. O ledger T-146 foi para `validate` e `pause` e mostra
  "validação do dono · 9/9 · 100% do plano · pausado".
- **Handoff:** `docs/handoff-claude-T-144-T-146-conciliacao-2026-10-04.md` no checkout principal,
  não rastreado.
- **Sobreposição com as branches paralelas** (base `4e58e7f`):
  - T-131: `implement-next`, `init`, `plan-next`, `SKILL.md`, README.
  - T-143: `arquitetura.md`, `checkpoint`, `implement-next`, `plan-next`, `SKILL.md`.
  - T-089: `arquitetura.md`, `plan-next`, `SKILL.md`.
  - T-139 (desanexado e de base antiga): as 4 âncoras de versão, além de `checkpoint`, `init`,
    `plan-next`, `test_canonical_board_contract`, `codex.md`, `SKILL.md` e README.
  - T-098: nenhuma.

### Status das fases

- ✅ **Fase 1** (T-144): núcleo, CLI, `show`/`watch`, recibo. `ba523e9` · 0.28.0 · aguarda o dono.
- ✅ **Fase 2** (T-146): `bind`, hook, statusline, trio no `init`. `064e726` · 0.29.0 · aguarda o dono.
- ⬜ **Fase 3** (T-147): procedimento do Orca e `watch` multi-raiz. Antes, decidir se haverá espelho
  opt-in via `update_plan` no Codex.
- ⬜ **T-145**: trocar as contagens fixas de testes por "a suíte descoberta".

## ⏭️ RETOMAR AQUI

A frente `@frente-mods` está **em espera**, sem card em curso. A próxima ação é do dono, em uma de
três frentes:
1. **Conciliação na `main`:** usar o handoff
   `docs/handoff-claude-T-144-T-146-conciliacao-2026-10-04.md`. A versão final, o push e a
   publicação são dele.
2. **Validação dos `[?]`:** o `watch` funciona direto da branch. O lembrete por hook e a statusline
   só podem ser validados depois de release, instalação e restart, porque o cache é indexado por
   versão. Cuidado com o T-093: atualizar o plugin derruba a sessão Codex viva.
3. **"Pode implementar a fase 3"** → `T-147`, mas antes a decisão do espelho `update_plan`.

O ledger real do T-146 (9/9, pausado em `validate`) fica em `.orq/progress/` do checkout principal,
ignorado pelo git; a fase 1 não teve ledger. A chave de dono do T-146 está acima, na seção
"T-146 — fase 2 em Loop B". O histórico de cada passo está nas seções datadas desta thread.

