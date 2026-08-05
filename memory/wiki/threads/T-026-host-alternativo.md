# Thread — T-026 · Orquestra fora do Claude Code — Codex ou Kimi como host

**Frente:** portabilidade da disciplina · matriz de paridade Codex/Kimi · estratégia de host alternativo.
**Aberta em** 2026-07-30 · **REABERTA em 2026-08-04 com motivo novo** · **AMPLIADA em 2026-08-04
(elenco host-agnóstico — seção 🟣)** · **estado: as 7 decisões seguem fechadas; aguarda as decisões
8–10 da seção 🟣 + o "pode implementar"** · planner `fable`.
**Nada em `orq/` foi editado** — este arquivo é o único artefato. A seção de 30/jul abaixo é o
registro do que se sabia antes; o que envelheceu está **marcado**, não apagado.

## O pedido, verbatim (2026-07-30)

> "Outra questão que eu pedi foi em relação ao uso de outra LLM como principal. No caso, ao invés
> de trabalhar no ClaudeCode, trabalhar, por exemplo, no Codex ou direto no Kimi 3, se existe essa
> possibilidade."

**Fronteira com o `T-021` (vizinho, não é o mesmo):** o `T-021` migra papéis internos para CLI
externa **mantendo** o Claude Code como host; este card **troca o host inteiro**. A sobreposição
real é uma só: a Estratégia C abaixo (híbrido) **é** o `T-021` — este plano a reconhece e não a
detalha. O mecanismo de invocação (`codex exec -s read-only`, `kimi -p`, `< /dev/null`) é
compartilhado e vive no `_elenco.md`.

## Problema (a causa raiz, não o sintoma)

O sintoma é "o orq só roda no Claude Code". A causa raiz: **o Orquestra empacota a disciplina
(markdown portátil) dentro do mecanismo de distribuição de um único host.** O roteamento vive na
`description` de uma skill Claude; os loops vivem em 12 commands `/orq:*`; o time vive em
subagentes spawnados com override de modelo; o progresso vive numa statusline — todas chamadas de
API do Claude Code.

**Mas a premissa do card ("não roda no Codex nem no Kimi, ponto") envelheceu parcialmente** — a
investigação em máquina real mostrou que as primitivas convergiram mais do que se supunha:
skills `SKILL.md` viraram padrão de facto multi-host; o Codex desta máquina **já consome um
marketplace em formato Claude** (`.claude-plugin/marketplace.json` — o `claude-plugins-official`
está adicionado e com plugin instalado); o Kimi carrega **agents em formato Claude Code** e tem
sistema de plugin quase 1:1 (skills, agents, commands, hooks, MCP). O que continua sem
equivalente: **subagente no Codex** *(⚠️ envelhecido — ver 2026-08-04: existe, feature
`multi_agent` stable)*, **elenco multi-modelo por papel** fora do Claude *(⚠️ parcialmente
envelhecido — ver 2026-08-04)*, **statusline** *(⚠️ envelhecido no Codex — existe)*, **sandbox no
Kimi** — e, mais importante, a **combinação testada**: o produto só foi provado
comportamentalmente num host, e teste comportamental é o único gate que pega defeito aqui (lição
do `T-012`).

## Matriz de paridade (verificado nesta máquina em 2026-07-30, salvo indicação)

> ⚠️ **2026-08-04: esta matriz está parcialmente vencida.** As linhas "Subagente", "Override de
> modelo por papel", "Hook", "Plugin/empacotamento", "Skill (Kimi)" e "Statusline (Codex)" foram
> corrigidas ou promovidas de suposição a fato — ver **"Matriz corrigida"** na seção de
> 2026-08-04. O restante segue válido. Mantida aqui como registro do que se sabia.

Versões: Codex CLI `0.145.0-alpha.4` (`/usr/local/bin/codex`) · Kimi Code `0.29.2`
(`~/.kimi-code/bin/kimi`, symlink em `~/.local/bin/kimi`).

| Primitiva que o orq usa | Claude Code | Codex CLI | Kimi Code |
|---|---|---|---|
| Instrução persistente por projeto | `CLAUDE.md` | `AGENTS.md` — **verificado** global (`~/.codex/AGENTS.md` existe, 19.9K); projeto = comportamento documentado do produto | `AGENTS.md` — **verificado por strings do binário**: o system prompt injeta `{{ KIMI_AGENTS_MD }}` ("The applicable AGENTS.md instructions are"), com AGENTS.md por diretório; fluxo de import menciona `AGENTS.md`/`CLAUDE.md`. Doc oficial não achada (página "context" = 404) |
| Skill carregada por intenção | `skills/orq` | skills existem — **verificado** `~/.codex/skills/` com ~25 skills instaladas; invocação automática por description = **suposição** (doc de plugins cita "skills" sem detalhar gatilho) | **verificado (doc oficial)**: `SKILL.md` + frontmatter (`whenToUse` extra), auto-invocação pelo modelo via description; descoberta em `~/.kimi-code/skills/`, `~/.agents/skills/`, projeto `.kimi-code/skills/` e `.agents/skills/` *(2026-08-04: promovido a **comprovado empiricamente**, inclusive o roteamento)* |
| Comando nomeado (`/orq:*`) | 12 commands | **não verificado**: `~/.codex/prompts/` não existe nesta máquina; doc de plugins **não** lista commands como componente | **verificado (doc)**: `/skill:nome` para skill explícita + plugins registram `commands` de arquivos markdown |
| Subagente com contexto próprio | Task tool + 5 agents | **não existe** (verificado por ausência: nenhuma flag, `enable_fanout` under-development/off, `collaboration_modes` removed) *(⚠️ ERRADO — ver 2026-08-04: `multi_agent` stable=true e ferramenta `spawn_agent` no binário; a investigação de 30/jul olhou as flags erradas e parou cedo)* | **verificado (doc)**: sub-agents automáticos com contexto isolado; agents em markdown **compatíveis com o formato Claude Code** (campo `tools` em vírgulas carrega) *(2026-08-04: formato Claude comprovado empiricamente via `--agent-file`)* |
| Override de modelo por papel (elenco) | spawn com `model:` | só por sessão (`-m`); sem subagente não há "por papel" *(⚠️ envelhecido — `spawn_agent` resolve modelo por filho; ver 2026-08-04)* | **limitado**: `model_preference` = `primary`/`secondary` apenas — não há "planner no X, implementer no Y" *(confirmado em 2026-08-04, com nuance nova)* |
| Hook | primitiva existe (orq não declara — `T-001` pendente) | existe — **verificado**: `features` mostra `hooks`/`plugin_hooks` stable+true, `~/.codex/hooks.json` presente; semântica de eventos **não verificada** *(2026-08-04: semântica verificada — `PreToolUse` bloqueável, escopo por projeto existe, trust por hash)* | **verificado (doc)**: `[[hooks]]` no `config.toml`; `PreToolUse`/`Stop`/`UserPromptSubmit` **bloqueáveis** (exit 2 nega) — dá para negar `git checkout/reset`, o que o `T-019` pediu. Escopo por projeto **não verificado** (doc só mostra user-scope) *(2026-08-04: escopo por projeto = ausente também nas strings do binário; e hooks são fail-open)* |
| Sandbox | permissões nativas | **verificado**: `-s read-only`/`workspace-write`/`danger-full-access` + execpolicy `.rules` de usuário **e projeto** (`--ignore-rules` confirma) | **não existe** — só `-y`/`--auto`, que REDUZEM proteção. Confirma o `_elenco.md` |
| Modo não-interativo | `claude -p` | **verificado**: `codex exec` + `--json`, `-o <file>`, `--output-schema`, `resume`; `< /dev/null` obrigatório (conhecido) | **verificado**: `kimi -p --output-format text\|stream-json`; `< /dev/null` obrigatório (conhecido) |
| Plugin / empacotamento | `.claude-plugin/` | **verificado nesta máquina**: `codex plugin marketplace add` aceita marketplace **formato Claude** (o `claude-plugins-official` aponta `.claude-plugin/marketplace.json`; `superpowers` instalado por ele). Doc oficial: plugin = skills + MCP + hooks + connectors; **agents e commands não citados** → presumo ignorados *(2026-08-04: o experimento com o PRÓPRIO orq foi rodado — instala e habilita como está; ver seção nova)* | formato próprio: `kimi.plugin.json` ou `.kimi-plugin/plugin.json` — **sem conversão do formato Claude (doc)**, mas componentes quase 1:1: skills, agents, commands, hooks, MCP, instruções de system-prompt, skill auto-carregada no início |
| `${CLAUDE_PLUGIN_ROOT}` | sim | equivalente **não verificado** | equivalente **não verificado** |
| Statusline | comando de statusline | não encontrado — **suposição de ausência** *(⚠️ ERRADO — existe `[tui] status_line` configurável; ver 2026-08-04)* | não encontrado (`tui.toml` não tem campo) — **suposição de ausência** |
| Agendado / modo noturno | session-scoped (limitação conhecida) | "scheduled task templates" em plugins (doc; **não verificado**) | não encontrado |

**Leitura da matriz:** a disciplina (board, wiki, gates, handoff, escala de risco, multi-janela) é
markdown lido por qualquer um dos três — os scripts `kanban-status.sh` e `lint-coerencia.py` são
bash/python genéricos e rodam em qualquer host. O que morre fora do Claude Code: os 12 comandos
como estão, o elenco por papel, a statusline, e (só no Codex) o worker de contexto fresco.
*(⚠️ 2026-08-04: das quatro perdas listadas, duas caíram parcialmente — ver seção nova.)*

## Solução — três estratégias, custo honesto

> ⚠️ **2026-08-04: a recomendação foi revisada** — continua A + C, mas o "A" ganhou um degrau
> (instalar também o mecanismo nos hosts que o aceitam) e o motivo mudou. Ver seção nova.

### A — "Orquestra portátil": a disciplina em markdown host-agnóstico ✅ RECOMENDADA
Extrair da `SKILL.md` um **template de `AGENTS.md`** (a seção Orquestra: princípio, máquina de
estados e marcadores, interface natural SEM citar `/orq:*`, regras invioláveis, checkpoint manual,
protocolo multi-janela) + uma **skill portátil** em formato Agent Skills (funciona nos dois hosts;
`whenToUse` para o Kimi). O dono coloca o `AGENTS.md` no projeto e abre `codex` ou `kimi` — a
disciplina vale; board e wiki funcionam idênticos porque são só arquivos.
**Ganha:** board, gates, checkpoint, cards, wiki em qualquer host — hoje.
**Perde (dizer com todas as letras):** loops A/B como comandos, elenco por papel, statusline,
worker fresco garantido (mitigação parcial: o "Manager" no Codex pode chamar `codex exec -s
read-only` para um planner de contexto limpo — mesmo truque do painel; **suposição**, não
testado), enforcement (que hoje também não existe no Claude — `T-001`; a paridade aqui é
irônica: em nenhum host os gates são ACL).
**Custo:** baixo-médio — 2 arquivos + doc de instalação + teste comportamental em 2 hosts.

### B — Port real por host ❌ NÃO RECOMENDADA agora
Codex: mesmo aceitando o marketplace Claude, ele aproveitaria ~1 dos 18 componentes do orq (a
skill; commands e agents ficam fora por doc). Kimi: um `kimi.plugin.json` sobre os mesmos arquivos
é plausível (primitivas quase 1:1), mas sem elenco multi-modelo e sem sandbox. Nos dois casos o
repo passa a manter **três produtos** com três ciclos de release, o defeito de cache×versão
multiplicado, e paridade central impossível no Codex (sem subagente) *(⚠️ premissa corrigida em
2026-08-04 — subagente existe no Codex; o argumento da manutenção tripla continua de pé)*. Se o A
provar demanda real, um "port Kimi" vira card futuro — o Kimi é o único onde faria sentido.

### C — Híbrido (status quo): Claude host, Codex/Kimi por CLI — continua por padrão
É o que já existe (painel) e o que o `T-021` expande. Não responde ao pedido literal ("trabalhar
NO Codex"), mas é o caminho sem custo e sem perda. **A recomendação final é A + C**: A dá ao dono
o host alternativo com a disciplina valendo; C continua sendo o modo normal com o Claude
disponível.

**Por que A e não B:** o valor do Orquestra, dito pelo próprio card, está na disciplina — e ela é
portátil de graça. B compra manutenção tripla para recuperar mecanismos que degradam de qualquer
jeito (sem elenco, sem statusline). **Sem promessa de paridade:** fora do Claude Code sobrevivem a
disciplina e o board; os loops automáticos, o time e a telemetria ficam.

## Passos (após o gate — nenhum foi executado)

> ⚠️ 2026-08-04: o passo 4 (experimento do marketplace) **foi executado** na reconferência —
> resultado na seção nova. Os demais passos seguem válidos como base, a serem re-sequenciados
> quando o dono responder as decisões novas. *(🟣 a ampliação de 2026-08-04 acrescenta um passo
> novo ANTES destes e altera o conteúdo dos passos 1–3 — ver "Passos revisados" na seção 🟣.)*

1. Criar `portatil/AGENTS-orquestra.md` — template derivado da `SKILL.md` 0.13.0: roteamento por
   intenção, máquina de estados, marcadores, regras 1–9, checkpoint manual (o que gravar e onde),
   protocolo multi-janela, contrato do board (referência ao `_schema.md` do projeto). **Sem** uma
   única citação a `/orq:*`, spawn, elenco ou statusline. Verificável: `grep -c "orq:" = 0`.
   *(🟣 ajustado: a citação ao ELENCO passa a existir — ver Passos revisados.)*
2. Criar `portatil/skills/orq-portatil/SKILL.md` — formato Agent Skills (`name` + `description`;
   `whenToUse` extra para o Kimi), corpo apontando para o `AGENTS.md` e o board. Verificável:
   frontmatter carrega nos dois hosts (`kimi doctor` ok; skill listada).
3. Criar `portatil/README.md` — instalação por host: Codex (referenciar no `AGENTS.md` do projeto;
   skill em `~/.codex/skills/` ou `~/.agents/skills/`), Kimi (idem; **nunca `-y`/`--auto`**, aviso
   T-019 explícito), e o **disclaimer de paridade** (o que não existe fora do Claude Code).
4. *(executado em 2026-08-04 — ver seção nova)* Implementer roda o experimento: `codex plugin
   marketplace add` deste repo + `codex plugin add orq` e **documenta o que o Codex efetivamente
   aproveitou** (reversível com `remove`; não é dependência do A).
5. `README.md` do repo: seção curta "Fora do Claude Code" apontando `portatil/` com o disclaimer.
   **Sem bump**: nada em `orq/` muda (regra: mexeu em `orq/` → bump; aqui não mexe).
6. Rodar os dois gates de sempre (`validate --strict` + `lint-coerencia.py`) — devem passar
   inalterados, já que `orq/` não foi tocado; se o lint acusar `portatil/`, é achado, não ajuste
   silencioso.
7. Teste comportamental **pelo dono** (critérios abaixo) — o Manager conhece as instruções e
   acertaria de memória; o viés é o mesmo já registrado no `T-014`/`T-016`.
8. Pós-validação (dever de checkpoint): `arquitetura.md` ganha seção "hosts alternativos" com a
   matriz resumida; log; esta thread.

## Critérios de aceite — o dono usando o produto

> ⚠️ 2026-08-04: critérios mantidos como **fumaça inicial**, mas o critério de sucesso do card
> mudou com o motivo novo — ver "Critério da semana" na seção de 2026-08-04.

Num projeto com `memory/` e o `AGENTS.md` portátil instalado (este repo serve):

1. Abrir `codex` (interativo) e dizer **"onde paramos?"** → ele lê `memory/MEMORY.md` +
   `KANBAN.md` e mostra o board com os estados certos — sem comando digitado.
2. Dizer **"queria acrescentar X"** → cria card no BACKLOG no formato do `_schema.md`, anuncia o
   roteamento e **para no gate** — sem editar arquivo de produto.
3. Dizer **"salva aí"** → append no `fixes-history.md`, thread atualizada, board consistente
   (`bash orq/scripts/kanban-status.sh` sem `⚠`).
4. Repetir 1–3 no `kimi` interativo **sem `-y`** — aceitando que ele peça aprovação por tool call.
5. Contra-testes: (a) o portátil não menciona `/orq:*` em lugar nenhum; (b) no Claude Code nada
   regride — o plugin segue idêntico (nenhum arquivo de `orq/` no diff).

## Decisões do dono (numeradas — 2026-07-30)

> ⚠️ **SUBSTITUÍDAS em 2026-08-04** — a verificação respondeu a decisão 5 e o motivo novo criou
> outras. Responder pelas **decisões 1–7 da seção nova**, não por estas. Mantidas como registro.

1. **Estratégia:** (a) A + C — **recomendo**: host alternativo real com custo baixo, sem
   prometer paridade; (b) B port completo — manutenção tripla por mecanismo que degrada; (c) só C
   — registrar "não dá" como limitação e fechar (é defensável, mas a investigação mostrou que dá).
2. **Forma do portátil:** (i) só template `AGENTS.md`; (ii) template + skill portátil —
   **recomendo (ii)**: o `AGENTS.md` garante a disciplina sempre carregada; a skill adiciona o
   gatilho por intenção onde houver suporte. Trade-off: um artefato a mais para sincronizar.
3. **Onde mora:** `portatil/` novo na raiz — **recomendo** (não infla o plugin, não força bump);
   alternativa: dentro de `orq/` (viraria parte do produto Claude — contradição conceitual).
4. **Kimi como host de ESCRITA:** (a) só leitura/planejamento até hooks de bloqueio serem testados
   — **recomendo** (T-019: instrução não segurou; hook bloqueável é a primeira garantia dura que o
   Kimi oferece, mas está por testar); (b) liberar já, com hooks `PreToolUse` negando git
   destrutivo + worktree descartável.
5. **Experimento Codex-marketplace (passo 4):** rodar? — **recomendo sim**: barato, reversível, e
   responde empiricamente o que a doc deixa vago (o que o Codex aproveita de um plugin Claude).
   *(→ executado em 2026-08-04; decisão obsoleta)*
6. **Card futuro "port Kimi" (`kimi.plugin.json`):** criar no backlog condicionado a uso real do
   A — **recomendo**; criar já seria engordar o board com aposta.

## Riscos (2026-07-30 — seguem válidos, ver adendos na seção nova)

- **Duas fontes da disciplina** (SKILL.md do plugin + template portátil) vão divergir — é o padrão
  "vocabulário espalhado" que já custou 4 correções numa sessão. Mitigação: o template declara no
  cabeçalho "derivado da SKILL.md vX.Y.Z"; release que mexer na SKILL ganha o dever de sincronizar
  (linha no checkpoint do release, não sistema novo).
- **Roteamento por intenção não testado em GPT/K3.** *(⚠️ 2026-08-04: no K3 foi testado e
  FUNCIONOU — "onde paramos?" invocou a skill sem comando. No GPT/Codex segue por testar.)* A
  description funciona no Claude após o `T-014`; nada garante que outro modelo leia igual. Se o
  teste 1 falhar, o ajuste é no texto do template — por isso o teste é critério, não suposição.
- **Kimi sem sandbox**: qualquer sessão de escrita no Kimi carrega o risco `T-019` inteiro até a
  decisão 4 ser resolvida — o template precisa carregar esse aviso no próprio corpo.
- **Multi-janela cross-host**: dono com Claude numa janela e Codex noutra sobre o mesmo repo — o
  protocolo (releia antes de escrever, edite a linha) vale, mas nunca foi exercitado entre hosts
  diferentes. O template carrega a seção; o risco residual fica anotado.
- **Codex alpha**: `0.145.0-alpha.4` — flags e comportamento de plugin podem mudar sob os pés.

## Escopo — fica de fora (2026-07-30; ver ajuste na seção nova)

- `T-021` (papéis via CLI com Claude de host) — a Estratégia C é ele; não detalhado aqui.
- `T-020` (perfis de elenco) — o "modo economia" extremo pode um dia apontar para o host
  alternativo, mas é decisão daquele card.
- Port completo por host (Estratégia B) — só como card futuro condicionado (decisão 6).
- Enforcement (`T-001`/`T-002`) em qualquer host; statusline fora do Claude; modo noturno fora do
  Claude; mover cards; editar `orq/` ou `memory/` além desta thread.

## O que NÃO investiguei em 30/jul (e por quê)

> ⚠️ 2026-08-04: vários itens desta lista foram resolvidos na reconferência — marcados abaixo.

- **Sessão interativa real do Codex e do Kimi** — a investigação foi `--help`, configs, cache e
  doc oficial, tudo em leitura. O roteamento por intenção nos dois hosts é o que o teste
  comportamental do dono vai provar; afirmar antes seria o erro do `T-014`. *(2026-08-04: no Kimi
  o roteamento foi provado em modo `-p`; sessão interativa e Codex seguem pendentes.)*
- **`codex plugin marketplace add` do orq** — muta a config do Codex; fora do modo leitura deste
  planejamento. Virou o passo 4 / decisão 5. *(2026-08-04: EXECUTADO, com backup e reversão.)*
- **Custom prompts do Codex** (`~/.codex/prompts/`) — o diretório não existe nesta máquina e a doc
  atual de plugins não os cita; não afirmo que existam nesta versão.
- **Hooks do Codex em detalhe** (eventos, bloqueio) — a feature está ativa (`hooks=true`), mas a
  semântica não foi verificada; irrelevante para a Estratégia A. *(2026-08-04: VERIFICADA por
  strings do binário e pela config real — bloqueável, com escopo de projeto e trust.)*
- **Hooks do Kimi em escopo de projeto** — a doc só mostra `~/.kimi-code/config.toml`; se hook de
  bloqueio por projeto existir, muda a decisão 4b. Fica para o card do `T-019`/port Kimi.
  *(2026-08-04: strings do binário também não mostram hooks por projeto — user-scope só.)*
- **Doc oficial do AGENTS.md no Kimi** — a página "context" é 404; a evidência é forte (template
  de system prompt no binário injeta `{{ KIMI_AGENTS_MD }}`), mas é engenharia reversa, não doc.
- **Equivalentes de `${CLAUDE_PLUGIN_ROOT}` e statusline** nos dois hosts — sem doc encontrada;
  marcados como suposição de ausência na matriz. *(2026-08-04: statusline do Codex EXISTE —
  corrigido; `${CLAUDE_PLUGIN_ROOT}` segue sem equivalente confirmado.)*

---

# 🔵 REABERTURA — 2026-08-04

## O motivo novo, verbatim

> "o que eu quero trabalhar agora é na possibilidade de usar esse framework independente do Claude
> como LLM principal. Uma alternativa é usar o codex como LLM principal ou o Kimi K3 como LLM
> principal. Eu quero testar todas essas como LLM principal para **alternar as assinaturas que eu
> tenho**."

**Isso reposiciona o card.** Não é mais portabilidade conceitual — é **rodízio de custo entre três
contas pagas** (Claude, OpenAI, Moonshot). O critério de sucesso muda junto: não é prova de
conceito, é o dono conseguir **trabalhar uma semana inteira noutro host sem perder a disciplina**
(board consistente, gates respeitados, checkpoint no fim de cada bloco).

## Verificação empírica de 2026-08-04 — o que foi feito

Versões **inalteradas** desde 30/jul (Codex `0.145.0-alpha.4`, Kimi `0.29.2`) — logo, tudo abaixo
não é software novo: é **investigação incompleta da primeira vez** (as flags erradas foram olhadas
no Codex; o `--agent`/`--skills-dir` do Kimi não foram exercitados). Testes desta rodada, todos
declarados e reversíveis:

1. `--help` completo dos dois CLIs + `codex features list` + strings dos dois binários.
2. **Experimento do marketplace no Codex** (o passo 4 do plano antigo): backup da config →
   `codex plugin marketplace add <este repo>` → `codex plugin add orq@orquestra` → inspeção →
   `remove` dos dois → diff da config **limpo** (0 menções restantes; cache órfão apagado).
3. **Teste vivo no Kimi** (em diretório de scratch, fora do repo, sem `-y`): skill sintética em
   formato Claude Code via `--skills-dir` + agent sintético em formato Claude Code via
   `--agent-file`, três rodadas de `kimi -p`.
4. Doc oficial do Kimi (páginas de agents e hooks, que em 30/jul estavam parcialmente 404).

## Matriz corrigida — só as linhas que mudaram, e por quê

| Primitiva | Dizia em 30/jul | Verificado em 04/ago | Evidência |
|---|---|---|---|
| **Subagente no Codex** | "não existe (verificado por ausência)" | **EXISTE.** Feature `multi_agent` = **stable, true**; ferramentas `spawn_agent` / `wait` / `close_agent` / `send_message` / `assign_agent_task`; config `agents.max_threads`, `agents.max_depth`, `agents.job_max_runtime_seconds` | `codex features list` + strings do binário nativo ("This spawn_agent tool provides you access to sub…"). A investigação de 30/jul olhou `enable_fanout`/`collaboration_modes` e parou cedo. **Comportamento em sessão real: não testado** |
| **Modelo por papel no Codex** | "só por sessão (`-m`)" | `spawn_agent` **resolve modelo por filho** — elenco por papel dentro do catálogo OpenAI é plausível | strings: "for spawn_agent. Available models:", "could not resolve the child model", `find_spawn_agent_model_name` |
| **Modelo por papel no Kimi** | "`model_preference` primary/secondary apenas" | **Confirmado** (2 faixas, atrás de `KIMI_CODE_EXPERIMENTAL_SECONDARY_MODEL=1` + `[secondary_model]` na config). Nuance nova: o catálogo de modelos aceita protocolo **`anthropic`** além de `kimi` — o secundário poderia, em tese, ser de outro vendor (não testado) | doc oficial de agents + strings (`protocol === "anthropic"`, mensagens de erro de `[secondary_model].model`) |
| **Skill no Kimi** | verificado só por doc | **COMPROVADO EMPIRICAMENTE**: `SKILL.md` em formato Claude (`name` + `description`) carrega via `--skills-dir`, aparece no índice da sessão com a description exata, e o **roteamento por intenção funciona**: `kimi -p "onde paramos?"` invocou a skill sozinho, leu o corpo (sentinela apareceu) e foi procurar `memory/wiki/KANBAN.md` | teste vivo em scratch, K3, 3 rodadas |
| **Agent formato Claude no Kimi** | verificado só por doc | **COMPROVADO**: `--agent-file` com frontmatter Claude (`name`/`description`/`tools` em vírgula) carrega; o corpo vira system prompt (sentinela veio, regras seguidas); a allowlist `tools` **é respeitada** (só Glob/Grep disponíveis). ⚠️ `--agent`/`--agent-file` em modo `-p` **exigem engine v2** (`KIMI_CODE_EXPERIMENTAL_FLAG=1`) | teste vivo; a mensagem de erro literal do CLI documenta a exigência |
| **Interação agent×skill no Kimi** | — (não previsto) | no teste combinado (agent-file + skills-dir), a skill **não apareceu** para o modelo — hipótese: o perfil substitui o system prompt e sem a variável `${skills}` no corpo a seção de skills some. **Suposição a confirmar** — o template portátil de agent precisa incluir `${skills}` | teste vivo + doc (variáveis `${skills}`, `${base_prompt}`) |
| **Hook no Codex** | "semântica não verificada" | **Bloqueável**: `PreToolUse` aceita `permissionDecision: "deny"` + reason, e **exit code 2** nega; formato do `hooks.json` é **idêntico ao do Claude Code** (matcher/hooks/type/command). **Escopo por projeto EXISTE**: `<projeto>/.codex/hooks.json` (há um registrado na config real desta máquina). Sistema de **trust por hash persistido** (`[hooks.state]`; flag `--dangerously-bypass-hook-trust`) — hook novo/alterado exige re-trust | strings do binário + `~/.codex/config.toml` real |
| **Hook no Kimi** | "escopo por projeto não verificado" | Escopo por projeto **ausente** (doc e strings — só `~/.kimi-code/config.toml`). Bloqueio confirmado na doc: exit 2 ou JSON `permissionDecision: deny` (mesmo contrato do Claude). ⚠️ **fail-open**: script que falha/expira = ação PERMITIDA | doc oficial de hooks |
| **Statusline no Codex** | "suposição de ausência" | **EXISTE**: `[tui] status_line` configurável por itens pré-definidos (modelo, contexto restante/usado, limites 5h/semana, branch, git summary…). Item de **comando custom não encontrado** → o % do kanban não entra (por ora) | config real desta máquina + strings (`status_line_branch`, `status_line_git_summary`…) |
| **Plugin orq no Codex** | presumido "aproveitaria ~1 de 18 componentes" | **O experimento rodou**: `codex plugin marketplace add` aceitou o `.claude-plugin/marketplace.json` **como está**; `codex plugin add orq@orquestra` instalou `0.17.0` **enabled**, copiando **todos os 25 arquivos** para `~/.codex/plugins/cache/orquestra/orq/0.17.0/` — **cache indexado por versão, o MESMO gotcha do bump do Claude vale lá**. O que ele efetivamente ATIVA (skill? commands? agents?) **não foi testado em sessão viva**; a doc sugere skills+hooks+MCP; hooks de plugin Codex moram em `.codex-plugin/hooks.json` (evidência: plugin context-mode) — o orq não tem esse diretório. Reversão limpa comprovada por diff | experimento executado e revertido em 04/ago |
| **Dirs de projeto no Kimi** | parcial | o binário referencia `.kimi-code/skills`, `.kimi-code/agents`, `.kimi-code/mcp.json` e `.agents/skills` no projeto — **a skill portátil pode viajar DENTRO do repo**, sem instalação por máquina | strings do binário |

**O que a verificação NÃO mudou:** AGENTS.md nos dois hosts (continua o veículo da disciplina);
**sem sandbox no Kimi** (T-019 de pé); `${CLAUDE_PLUGIN_ROOT}` sem equivalente; modo noturno só
session-scoped; statusline com % do board segue exclusiva do Claude; os 12 comandos `/orq:*` não
existem fora; e **nenhum host alternativo foi testado em sessão interativa real**.

## Leitura à luz do motivo novo

A premissa central do plano de 30/jul — "subagente e elenco não existem fora do Claude, logo só a
disciplina viaja" — **caiu pela metade**:

- **No Codex**, subagente existe (`multi_agent` stable) com modelo por filho — um "elenco
  intra-OpenAI" (planner num modelo, implementer noutro) é plausível, por confirmar em sessão.
- **No Kimi**, o formato Claude carrega **inteiro** (skill + agent), o roteamento por intenção
  **está provado com o K3**, e sub-agents automáticos existem — o que falta é elenco além de
  primário/secundário (experimental) e sandbox.
- **Elenco cross-vendor não existe em NENHUM host — nem no Claude Code** (subagente só aceita
  modelo Claude; o cross-vendor daqui é via CLI, o painel). A paridade real é maior do que a
  matriz de 30/jul sugeria. *(⚠️ CORRIGIDO na seção 🟣 de 2026-08-04: a frase só vale para spawn
  NATIVO. Por CLI, o elenco cross-vendor existe nos três sentidos e este projeto já o pratica todo
  dia no painel — a própria parentética o dizia; a conclusão errada foi tirar dela "não existe" em
  vez de "existe, por outro método". Ver "Correção de uma conclusão" na seção 🟣.)*

**A recomendação continua sendo a Estratégia A + C, mas o "A" sobe um degrau — "A ampliado":**

1. O núcleo segue igual: `portatil/AGENTS-orquestra.md` + skill portátil. O AGENTS.md é lido pelos
   dois hosts e garante a disciplina mesmo se a skill falhar. **A skill portátil continua
   necessária** — a `SKILL.md` real tem **23 referências** a `/orq:*` e `${CLAUDE_PLUGIN_ROOT}`
   que fora do Claude carregariam mas mandariam rodar o que não existe (o mesmo defeito que o
   lint pega no plugin).
2. **Novo:** onde o host aceita, instalar também o mecanismo — no Kimi, a skill portátil no
   próprio repo (`.agents/skills/` viaja no git); no Codex, `codex plugin marketplace add` +
   `plugin add` funciona **hoje** com o repo como está (o que ativa, o teste da semana dirá).
3. Por que não B (port por host): o custo caiu (o formato Claude é aceito quase as-is), mas o
   argumento decisivo continua — três ciclos de release e o gotcha cache×versão **triplicado**
   (agora comprovadamente: o Codex também indexa por versão). B só se o A rodar uma semana e
   deixar saudade de algo específico.

### Board e wiki funcionam noutro host? — RESPONDIDA: sim

São arquivos markdown lidos por ferramenta genérica — e o teste provou na prática: a skill de
teste no Kimi foi atrás do `memory/wiki/KANBAN.md` por conta própria. `kanban-status.sh` e
`lint-coerencia.py` são bash/python — rodam em qualquer host, **na mão ou por hook**. O que se
perde é a *exibição automática* do progresso (statusline do Claude; a do Codex existe mas não
aceita comando custom até onde se viu).

### Como o dono alterna — protocolo proposto (a validar com ele)

- **Mesmo repo, outro CLI.** Sem migração de nada: o estado inteiro (board, wiki, threads) mora em
  `memory/`, que é o ponto do desenho.
- **Setup por host, uma vez:** `AGENTS.md` na raiz do projeto (Codex e Kimi leem; o Claude segue
  no `CLAUDE.md` — coexistem) + skill portátil (`.agents/skills/` no repo cobre o Kimi;
  Codex: `plugin add` ou `~/.codex/skills/`).
- **Regra de ouro: um host escrevendo por vez.** Trocar de host = **checkpoint antes** (a wiki é o
  handoff — exatamente o mesmo protocolo do `/clear`, que já é treinado). O protocolo multi-janela
  do `T-013` vale na teoria (é markdown, não API), mas **nunca foi exercitado cross-host** — na
  primeira semana, não rodar dois hosts simultâneos no mesmo repo.

### O que ele perde em cada host — com todas as letras

**No Codex como host:** os 12 comandos `/orq:*` (interface natural cobre parte); elenco
cross-vendor *(⚠️ corrigido na seção 🟣 — por CLI é viável; o que não há é spawn nativo
cross-vendor)*; % do board na statusline (a statusline dele mostra modelo/contexto/limites/git, não
o kanban); modo noturno; gatilho automático da skill **não comprovado** (o risco nº 1 da semana
Codex); claude-mem/captura de sessão da stack pessoal.
**No Kimi como host:** **sandbox** (o risco T-019 inteiro — mitigação: hook user-scope negando
`git checkout/restore/reset` + worktree para tarefa grande); statusline; elenco além de
primário/secundário experimental; comandos; `--agent` em `-p` atrás de flag experimental;
claude-mem idem.
**Nos dois:** o lastro de teste comportamental — só o Claude tem meses de uso provado; toda
garantia nos outros hosts começa do zero na semana de teste.

## Decisões do dono — SUBSTITUEM as de 30/jul (responda "1a, 2ii…" que destrava)

1. **Estratégia:** (a) **A ampliado + C** — recomendo: disciplina portátil + mecanismo onde o
   host aceita, sem prometer paridade; (b) B port completo — o custo caiu mas a manutenção tripla
   e o cache×versão triplicado continuam; (c) só C — ignora o motivo novo (rodízio de assinatura
   exige host alternativo de verdade).
2. **Forma do portátil:** (i) só `AGENTS.md`; (ii) **`AGENTS.md` + skill portátil** — recomendo:
   comprovou-se que a skill carrega e roteia no Kimi; o AGENTS.md é a rede se o gatilho falhar.
   Trade-off: dois artefatos para sincronizar com a SKILL.md a cada release.
3. **Onde mora:** **`portatil/` na raiz** — recomendo (não infla `orq/`, não força bump); a skill
   portátil ganha cópia/symlink em `.agents/skills/` do projeto para o Kimi achar sozinha.
   Trade-off: mais um diretório fora do produto.
4. **Kimi como host de ESCRITA:** (a) **liberar com guarda dupla** — hook `PreToolUse` user-scope
   negando `git checkout/restore/reset` (existência confirmada; instalar e **testar vivo** antes
   da semana, lembrando que é fail-open) + a regra "um host por vez" — recomendo: "só leitura"
   inviabiliza uma semana de trabalho real, que é o critério novo; (b) manter só
   leitura/planejamento no Kimi e fazer a semana de escrita no Codex (que tem sandbox).
   Trade-off de (a): o hook é global da máquina — vale para toda sessão Kimi, inclusive as de
   revisor (o que, para o `T-019`, é feature e não bug).
5. **Qual host testa a primeira "semana inteira":** (a) **Codex primeiro** — recomendo: sandbox
   nativo (`-s workspace-write`), plugin instala como está, spawn_agent existe; o risco é o
   gatilho da skill não comprovado — se falhar, o AGENTS.md segura e anotamos; (b) Kimi primeiro
   — roteamento já provado, mas sem sandbox a semana inteira depende do hook. Trade-off em 1
   linha: Codex = segurança comprovada com gatilho incerto; Kimi = gatilho comprovado com
   segurança incerta.
6. **Critério de aceite da semana** (proposto — aprovar ou ajustar): 5 dias úteis de trabalho
   real num host alternativo com (i) board consistente no fim (`kanban-status.sh` sem `⚠`),
   (ii) checkpoint no `fixes-history.md` a cada bloco, (iii) zero card movido sem seu ok,
   (iv) lista honesta do que fez falta — que vira o insumo da decisão 7.
7. **Card futuro "port Kimi"** (`kimi.plugin.json` ou skill+agents em `.agents/` do repo): manter
   **condicionado** ao resultado da semana — recomendo; a barreira técnica caiu (formato Claude
   carrega as-is), mas continua aposta até a semana medir a falta real.

## Riscos novos (além dos de 30/jul, que seguem valendo)

- **Flag experimental no caminho crítico do Kimi**: `--agent`/`--agent-file` em `-p` exigem
  `KIMI_CODE_EXPERIMENTAL_FLAG=1` (engine v2). Mitigação: no dia-a-dia usar descoberta por
  diretório (`.agents/skills/` no repo), que dispensa flag — **suposição em modo interativo, a
  confirmar no primeiro dia da semana**.
- **Hook fail-open no Kimi**: a única guarda dura contra o T-019 permite a ação se o script
  falhar. O teste vivo do hook (negar um `git checkout` de verdade) é pré-requisito da decisão 4a,
  não opcional.
- **Trust de hooks no Codex**: hook novo/alterado exige re-trust (hash persistido) — se a semana
  Codex usar hooks, o primeiro run pede confirmação; não automatizar com
  `--dangerously-bypass-hook-trust`.
- **Cache×versão também no Codex**: comprovado hoje que o layout é o mesmo do Claude. Se um dia
  o plugin for instalado lá "de verdade", editar sem bump não muda o que roda — o gotcha migra
  junto.
- **`spawn_agent`/multi_agent do Codex é observação de binário**, não de sessão: pode estar
  atrás de rollout server-side mesmo com a flag stable. Não prometer elenco no Codex até ver.

## O que NÃO foi verificado em 04/ago (honestidade de fronteira)

- **Sessão interativa** de qualquer um dos dois hosts (todo teste Kimi foi `-p`; nenhum
  `codex exec`/TUI foi aberto — regra do dono: o binário do Codex não se invoca por Bash para
  sessões de trabalho; os subcomandos de plugin/inspeção não criam job).
- **O que o Codex ativa** do plugin orq instalado (skill listada? gatilho? commands?): exige
  sessão viva — é o primeiro item da semana Codex.
- **`spawn_agent` em uso real** e a lista efetiva de modelos por filho.
- **Hook do Kimi bloqueando de verdade** (só doc); **hook por projeto no Codex bloqueando de
  verdade** (só evidência de registro na config).
- **`${skills}` no agent-file do Kimi** restaurando a seção de skills (hipótese da interação
  agent×skill).
- **Modo interativo do Kimi sem a flag experimental** carregando skills de `.agents/skills/`.
- **Secundário cross-vendor no Kimi** (protocolo `anthropic` no catálogo — em tese).
- **Multi-janela cross-host** — segue nunca exercitado.

## ✅ AS SETE DECISÕES ESTÃO FECHADAS (2026-08-04) — não repergunte nenhuma

*(🟣 ampliação de 2026-08-04: nenhuma reaberta; a 4 ganha alcance maior e a 6 um subitem
proposto — ver "Efeito sobre as sete decisões" na seção 🟣.)*

**Decididas pelo dono, na conversa:**

- **5 — o primeiro host da "semana inteira" é o CODEX.** Razão que ele pesou: sandbox comprovado e
  hooks bloqueáveis **por projeto**, então erro sai contido. A incerteza aceita junto: **o gatilho
  por frase natural ainda não foi testado no Codex** — no Kimi foi provado vivo, no Codex não. Se
  falhar, o ajuste é no texto do portátil, e isso é critério do teste, não surpresa.
- **4 — o Kimi PODE escrever como host, condicionado a hook testado vivo ANTES.** `PreToolUse`
  negando git destrutivo, e **o teste de bloqueio tem que passar antes de liberar**: os hooks do
  Kimi são **fail-open**, então "configurei" não é o mesmo que "funciona". Sem o teste passar, ele
  não escreve. (Precedente que sustenta a exigência: `T-019` — a instrução do `_elenco.md` mandava
  não escrever e ele rodou `git checkout -- .` mesmo assim.)

**Decididas pelo Manager, seguindo a recomendação do planner (decisões técnicas, sem trade-off para
o dono):**

- **1 — Estratégia A ampliada + C.** Disciplina portátil **e** instalar o mecanismo onde o host
  aceita. Port completo (B) segue recusado.
- **2 — `AGENTS.md` + skill portátil.** A `SKILL.md` real tem 23 referências a `/orq:*` e
  `${CLAUDE_PLUGIN_ROOT}` que quebram fora do Claude: é versão portátil, não cópia.
- **3 — mora em `portatil/`** na raiz. Não infla o plugin, não força bump.
- **6 — critério de aceite: uma semana real.** 5 dias de trabalho no host, board sem `⚠`,
  checkpoints em dia, zero card fechado sem o ok do dono.
- **7 — card "port Kimi" fica condicionado** ao resultado da semana; não nasce agora.

## Próxima ação *(⚠️ substituída — ver "Próxima ação" da seção 🟣 abaixo; mantida como registro)*

**Com o "pode implementar" do dono**, o card vai a READY e o implementer executa: passos 1–3 e 5–8
do plano de 30/jul (o 4 já foi feito hoje) **mais** os itens novos — `${skills}` no template de
agent do Kimi, cópia da skill em `.agents/skills/`, hook user-scope do Kimi **com teste vivo de
bloqueio** (decisão 4), e o roteiro da semana no **Codex** (decisão 5).

⚠️ **Ordem que a decisão 4 impõe:** o teste vivo do hook do Kimi é **pré-requisito**, não passo
final. Enquanto ele não passar, nada de escrita no Kimi.

**Sem o "pode implementar", nada é criado.**

Artefatos da verificação: nenhum fora desta thread (config do Codex restaurada com diff limpo;
testes do Kimi em scratch descartável; nenhum arquivo do repo tocado além deste).

---

# 🟣 AMPLIAÇÃO DE ESCOPO — 2026-08-04 · elenco host-agnóstico

## O pedido novo, verbatim

> "A ideia é que a gente consiga configurar todos os agentes. Por exemplo, rodando como motor
> principal o GPT, eu poderia configurar o Opus como revisor, o Sonnet como implementador, ou o
> próprio GPT em diferentes efforts. Instalando usando o Codex, seria essa também."

O que isso adiciona ao card: não basta o host trocar — **o elenco viaja junto**, papel a papel,
com modelo de qualquer vendor, configurável a partir de qualquer host. O `_elenco.md` deixa de ser
"papel → modelo" e passa a ser **"papel → modelo + método de invocação no host corrente"**.

## Correção de uma conclusão da seção 🔵 (acima)

A seção de reabertura afirmou: *"Elenco cross-vendor não existe em NENHUM host — nem no Claude
Code"*. **Enunciada assim, está errada.** O correto, separado por método:

- **Por spawn nativo**, não existe mesmo: o subagente do Claude só aceita modelo Claude; o
  `spawn_agent` do Codex resolve modelo no catálogo OpenAI (presumido); o Kimi só tem
  primário/secundário.
- **Por CLI, existe nos três sentidos — e este projeto o pratica todo dia.** O `/orq:revisar`
  invoca Opus por spawn, GPT por `codex exec` e K3 por `kimi -p` no mesmo painel; o painel de três
  rodou três vezes só hoje. A própria frase corrigida admitia o mecanismo na parentética ("o
  cross-vendor daqui é via CLI") — o erro foi concluir "não existe" em vez de "existe, por outro
  método".
- **Verificado pelo Manager hoje**: `claude -p --model sonnet "qual modelo você é?"` respondeu
  "Sonnet 5 (claude-sonnet-5)" — o Claude é invocável de fora com modelo escolhido por invocação;
  `claude --help` mostra ainda `--agents <json>` e `--append-system-prompt`.
- **Reverificado por mim nesta rodada** (probes abaixo): as flags existem e a pergunta "escreve?"
  foi respondida empiricamente.

Consequência: o pedido do dono é viável **com mecanismo que já existe e já é usado**. O que falta
não é capacidade — é **um lugar normativo** que diga, por papel, qual modelo e como invocá-lo a
partir do host em que se está.

## Verificação empírica desta rodada (read-only + scratchpad descartável, já apagado)

1. **`claude --help`** — confirmados: `--agents <json>` (agentes customizados por invocação),
   `--append-system-prompt`, `--permission-mode <mode>`, `--allowedTools`/`--disallowedTools`,
   `--tools`, `--add-dir`, `-r/--resume` e `-c/--continue`, `--settings`,
   `--dangerously-skip-permissions`.
2. **Probe 1 — `claude -p` com permissões padrão** (haiku, diretório de scratch, `< /dev/null`):
   pedi a criação de um arquivo. **Negado e nada escrito** — resposta literal: *"Claude requested
   permissions to write to …/probe.txt, but you haven't granted it yet"*; `ls` confirmou o
   diretório vazio. **`claude -p` default é, na prática, read-only para escrita de arquivo.**
3. **Probe 2 — `claude -p --permission-mode acceptEdits`** (mesmo setup): o **Write passou**
   (arquivo criado com o conteúdo pedido) e o **Bash foi negado** (`git init` → *"This command
   requires approval"*). `acceptEdits` libera edição de arquivo **sem** liberar execução de
   comando — granularidade real, por ferramenta.
4. **`codex exec --help`** — reconfirmados `-s read-only|workspace-write|danger-full-access`,
   `-m`, `-c` (ex.: `model_reasoning_effort`), `resume` — os mesmos já em uso no painel.
5. **`kimi --help`** — reconfirmados `-m` (alias de modelo por invocação), `--skills-dir`,
   `--agent`/`--agent-file` (engine v2), `-y`/`--auto` — consistente com o teste vivo da seção 🔵.
6. **`grep -rln "_elenco" orq/`** → **9 arquivos** consomem o elenco hoje (`SKILL.md`, `stack.md`
   e os commands `ajuda`, `elenco`, `implement-next`, `init`, `plan-next`, `revisar`, `stack`) —
   é o tamanho do impacto de mudar o formato, e o motivo do desenho **aditivo** abaixo.

Artefatos: probes em scratchpad de sessão, **apagados ao fim**; nenhum arquivo do repo tocado além
desta thread.

## O desenho — `_elenco.md` v2: o QUEM numa tabela, o COMO numa matriz

São **duas regras de natureza diferente**, e cada uma ganha exatamente **um** lugar normativo — os
dois no mesmo arquivo (`memory/wiki/_elenco.md`), que já é o lugar que todos os consumidores leem:

**Regra 1 — QUEM toca cada papel** (decisão do dono; muda com crédito/perfil). A tabela "Papéis"
continua sendo a única fonte, com uma mudança: o **modelo carrega o vendor no nome e, quando
existir, o effort** — `opus`/`sonnet`/`haiku`/`fable` (Anthropic, como hoje);
`gpt-5.6-sol@xhigh`/`gpt-5.6-sol@low` (OpenAI, effort embutido na identidade); `k3` (Moonshot;
alias exato a confirmar na implementação). Exemplo — a configuração verbatim do dono, host Codex:

| Papel | Modelo |
|---|---|
| manager | *a sessão principal — é o próprio host, não se configura aqui (regra de hoje, mantida)* |
| planner | `gpt-5.6-sol@xhigh` |
| implementer | `sonnet` |
| reviewer | `opus` |
| scout | `gpt-5.6-sol@low` |

**Regra 2 — COMO invocar o modelo X estando no host H** (fato técnico; muda quando os CLIs mudam,
não quando o dono muda de ideia). Seção nova "**Matriz de invocação**" no mesmo arquivo. Uma regra
só a gera — **vendor do modelo == vendor do host → mecanismo nativo; senão → CLI do vendor do
modelo** — e a matriz materializa os templates com os gotchas já pagos (`< /dev/null`, fallback do
binário do Kimi, flags por papel):

| Vendor do modelo | host Claude Code | host Codex | host Kimi |
|---|---|---|---|
| Anthropic | spawn nativo (Task + `model:`) — como hoje | `claude -p --model <m>` + flags do papel (abaixo) | idem coluna Codex |
| OpenAI | `codex exec -m <m> -c model_reasoning_effort=<e>` — já em uso no painel | `spawn_agent` com modelo por filho (**não comprovado em sessão**; fallback `codex exec` aninhado — **também não comprovado**) | `codex exec -m <m> -c model_reasoning_effort=<e>` |
| Moonshot | `kimi -p [-m <alias>]` — já em uso no painel | idem coluna Claude | sub-agent nativo, ou `kimi -p` para contexto limpo |

Mais duas colunas/anotações por linha no arquivo real: **flags de leitura** (read-only garantível)
e **flags de escrita** (a tabela de garantias abaixo) — para o consumidor nunca decidir sozinho
qual flag "parece" segura.

**Por que assim, e não as alternativas óbvias:**

- **Uma tabela por host** — triplicaria a decisão do dono (reviewer=opus escrito três vezes, uma
  por host) e divergiria na primeira troca de perfil. É exatamente o defeito "regra enunciada em
  dois lugares" que custou cinco rodadas de correção nesta semana. Recusada.
- **Resolvido no consumidor** (cada skill/command hard-coda os comandos de invocação) — espalha o
  mecanismo por N arquivos; cada gotcha (`< /dev/null`, fallback do Kimi) teria N cópias a
  sincronizar. O `revisar.md` de hoje já mostra o custo de carregar isso em prosa. Recusada.
- **Tabela única + matriz no mesmo arquivo** — a decisão do dono mora numa linha; o mecanismo mora
  numa célula; trocar perfil não toca a matriz, atualizar um CLI não toca os papéis. E o arquivo é
  **o mesmo nos três hosts, sem estado por host**: quem lê sabe em que host está e usa a sua
  coluna.

**Compatibilidade com os 9 consumidores atuais — o formato é ADITIVO:** a tabela "Papéis" mantém
as colunas de hoje; a matriz é seção nova que os commands do Claude simplesmente ignoram. Enquanto
os papéis apontarem modelos Anthropic, **nada muda no host Claude** — zero risco de regressão.
Papel com modelo não-Anthropic **no host Claude** exige que os commands aprendam a ler a matriz —
isso **é o `T-021`** (a fronteira declarada no topo desta thread continua exata: a matriz é o
mecanismo compartilhado; este card entrega a matriz + os consumidores portáteis; o `T-021` entrega
o consumo pelos commands do Claude). Nos hosts alternativos o consumidor é novo (a skill portátil
deste card), então não há legado a quebrar.

## O que degrada em cada método — sem promessa de paridade

**Spawn nativo** (modelo do mesmo vendor do host): herda contexto do projeto
(`CLAUDE.md`/`AGENTS.md`), ferramentas, sistema de permissões e working dir do host; briefing
curto; steering possível durante a execução.

**CLI cross-vendor**: processo novo com **contexto zero** — o briefing precisa carregar tudo
(card, plano, convenções, caminhos) e o modelo **relê o repo do zero**, pagando tokens da outra
conta e tempo de parede; é one-shot (sem steering no meio — `codex exec resume` e
`claude -p --resume` existem, mas nunca foram testados neste fluxo); as permissões do host **não
alcançam** o processo filho — cada CLI traz as suas próprias garantias, listadas abaixo.

Por papel:

- **reviewer** — contexto zero é o PONTO (independência do parecer). É o painel de hoje, provado
  três vezes só hoje. Perda relevante: nenhuma. **É o papel onde cross-vendor via CLI já é o
  estado da arte deste repo.**
- **planner / scout** — aceitável: leitura ampla do zero faz parte do papel; o custo é a releitura
  paga em tokens. Read-only é garantível nos três métodos (probe 1; `-s read-only`; Kimi sem `-y`
  não aplica).
- **implementer** — é onde o método CLI **mais degrada**: briefing grande, releitura completa,
  escrita exige liberação explícita e **perde o gate interativo de permissão** (em `-p`/`exec`
  ninguém aprova chamada a chamada: ou nega tudo, ou libera de antemão). Custo real; não prometer
  paridade com o spawn nativo.
- **docs** — mesmo perfil do implementer, superfície menor.

## Implementer via CLI escreve arquivo? — verificado, com a garantia dura de cada método

| Método | Comportamento default | Como se libera escrita | Garantia dura disponível |
|---|---|---|---|
| `claude -p` | **nega Write** — probe 1: permissão pedida, não concedida, arquivo não criado | `--permission-mode acceptEdits` → Write/Edit sim, **Bash continua negado** (probe 2); `--allowedTools` para granularidade; `--add-dir` limita diretórios; `--dangerously-skip-permissions` libera tudo (não usar) | permissão por ferramenta (app-level) — forte para edição; **não é sandbox de OS**; para o implementer rodar teste, Bash exigiria allowlist explícita |
| `codex exec` | sandbox ativo | `-s workspace-write` | **sandbox de OS** — a mais forte das três |
| `kimi -p` | sem `-y` não aplica mudança (comportamento **observado**, não contrato) | `-y`/`--auto` | **nenhuma** (`T-019`); hook `PreToolUse` é fail-open; garantia real só em worktree |

Leitura honesta: **dá para escrever pelos três métodos, com garantias muito desiguais.** A
recomendação (decisão 8): na primeira fase, implementer cross-vendor **só em worktree
descartável**, qualquer que seja o método — inclusive o Codex: o sandbox protege o filesystem de
sair do workspace, mas **não protege de um plano mal aplicado sem steering**; o worktree devolve o
gate que o modo one-shot tira (diff review antes do merge). O Kimi já está coberto pela decisão 4
(hook testado vivo ANTES), que com o escopo novo passa a valer também para ele como **implementer
invocado de outro host** — mesma regra, alcance maior.

## Os efforts do GPT como papéis — o elenco mais barato de todos

O dono citou explicitamente, e é o caminho mais simples do rodízio: `model_reasoning_effort` já é
passado por invocação no painel (`xhigh` hoje). A notação `modelo@effort` torna cada effort um
"modelo" distinto na tabela de papéis — planner `gpt-5.6-sol@xhigh`, implementer
`gpt-5.6-sol@medium`, scout/docs `gpt-5.6-sol@low` (valores válidos além de `xhigh`: enumerar da
doc na implementação, não inventar aqui).

No **host Codex** isso é elenco **intra-vendor**: uma conta só, sem CLI externa, sem briefing
cross-vendor, sem contexto zero desnecessário. Mecanismo: `spawn_agent` com modelo por filho
(strings do binário; **effort por filho não confirmado**) ou `codex exec` aninhado (**não
testado**) — os dois são itens do roteiro da semana. No **host Claude**, os efforts já funcionam
hoje via `codex exec -c model_reasoning_effort=…`. É o degrau de menor risco e menor custo de toda
a ampliação — vale destacar para o dono como o primeiro a exercitar.

## Custo por configuração — onde o rodízio economiza e onde NÃO

A regra de bolso que **precisa estar escrita no próprio `_elenco.md` v2** (senão o dono troca de
host achando que parou de gastar Claude e continua gastando):

> **Cada papel cobra a conta do vendor do SEU modelo, independente do host. Trocar de host só
> muda quem paga o Manager** — que é o maior consumo individual, mas não o único.

| Configuração | Conta Anthropic | Conta OpenAI | Conta Moonshot |
|---|---|---|---|
| Hoje (host Claude, perfil `padrao`, painel completo) | manager + planner + implementer + reviewer + docs/scout | revisor externo | revisor externo |
| **O exemplo verbatim do dono** (host Codex; reviewer `opus`, implementer `sonnet`, resto GPT) | reviewer + implementer — **continua gastando Claude** | manager + planner + scout | — |
| Host Codex, tudo `gpt@efforts`, reviewer `k3` | **zero** | tudo menos o reviewer | reviewer |
| Host Kimi, tudo `k3`, reviewer `gpt@xhigh` | zero | reviewer | tudo menos o reviewer |

O aviso central: **no arranjo que o dono deu como exemplo, o rodízio DESLOCA o gasto Claude (sai o
manager, ficam reviewer e implementer) — não o zera.** Zerar uma conta num período = nenhum papel
com modelo daquele vendor no período. E o painel de revisão completo, por desenho, sempre cobra as
três contas — é o preço da descorrelação de erro, e a decisão 10 pergunta se ele quer pagá-lo na
semana de rodízio.

## Como o `_elenco.md` sobrevive à troca de host — respondida

- **É o mesmo arquivo nos três hosts**: `memory/wiki/_elenco.md` do projeto, markdown no git —
  entra no mesmo regime já provado do board e da wiki. Nenhuma conversão, nenhuma cópia por host.
- **Zero estado por host dentro do arquivo**: a matriz tem as três colunas; o consumidor usa a do
  host em que roda (ele sabe quem é — não precisa de campo "host ativo", que seria estado a
  dessincronizar).
- **Consumidores por host**: no Claude, os 9 arquivos de hoje (sem mudança neste card); no
  Codex/Kimi, a **skill portátil** e o **AGENTS-orquestra.md** ganham o dever explícito: "papéis e
  invocação: leia `memory/wiki/_elenco.md`; use a coluna do seu host na Matriz de invocação".
- **O template v2 mora em `portatil/`** (decisão 3, inalterada); o `_elenco.md` vivo deste repo
  migra para v2 de forma aditiva (passo abaixo). Levar o template ao `/orq:init` (isto é, a
  `orq/`) fica para o release que fechar o `T-021` — fora deste card.
- **Perfis (`padrao`/`economia`) continuam funcionando como estão** (só modelos Claude). Preset de
  rodízio nomeado — decisão 9.

## Efeito sobre as sete decisões fechadas — nenhuma reaberta, nenhuma obsoleta

- **1 (A ampliada + C)** — **reforçada**: o mecanismo que o escopo novo pede é exatamente o que o
  "A ampliado" instala; o elenco v2 entra como mais um artefato do A.
- **2 (AGENTS.md + skill portátil)** — vale; os dois artefatos ganham o dever de ler elenco +
  matriz (mudança de conteúdo, não de forma).
- **3 (`portatil/`)** — vale; o template do elenco v2 mora lá.
- **4 (Kimi escreve só com hook testado vivo antes)** — vale e **amplia o próprio alcance**: passa
  a cobrir o Kimi como host E como implementer invocado por CLI de outro host. Mesma regra.
- **5 (Codex primeiro)** — vale; a semana ganha itens novos de roteiro (lista nos passos).
- **6 (critério = 5 dias reais)** — vale; **um subitem proposto**: "(v) pelo menos uma invocação
  cross-vendor por papel usado na semana" — sem isso a semana pode passar inteira sem exercitar o
  que este escopo novo pede. (Ajuste, não reabertura — o dono confirma junto com as decisões 8–10.)
- **7 (port Kimi condicionado)** — vale, inalterada.

## Passos revisados (delta sobre os passos 1–8 de 30/jul; ordem de execução)

0. *(pré-requisito, inalterado — decisão 4)* Hook `PreToolUse` do Kimi instalado e **testado vivo**
   negando `git checkout` de verdade. Sem passar, o Kimi não escreve em nenhum papel.
1. **(novo — vem antes dos demais)** Criar `portatil/elenco-template.md` — o `_elenco.md` v2:
   tabela "Papéis" com modelo qualificado (`@effort` para OpenAI), seção "Matriz de invocação" com
   os templates **verificados** (incluindo `< /dev/null`, fallback do binário do Kimi, flags de
   leitura e de escrita por papel — a tabela de garantias desta seção) e a seção "Custo por
   configuração" com a regra de bolso. Verificável: os comandos da matriz batem 1:1 com os
   testados nesta thread; `grep -c "orq:"` = 0.
2. Passo 1 antigo (`AGENTS-orquestra.md`) **ajustado**: além do que já previa, ganha a regra
   "papéis e invocação moram em `memory/wiki/_elenco.md` — use a coluna do seu host". O
   verificável antigo (`grep -c "orq:" = 0`) continua; a proibição de citar "elenco" cai — o
   elenco agora é portátil por desenho.
3. Passo 2 antigo (skill portátil) idem: o corpo instrui ler elenco + matriz.
4. **(novo)** Migrar o `_elenco.md` **deste repo** para o formato v2 — mudança **aditiva** (a
   tabela "Papéis" e a seção "Revisores externos" de hoje continuam válidas; a matriz absorve os
   comandos que hoje vivem em "Revisores externos", que passa a apontar para ela — um lugar só).
   Verificável: `lint-coerencia.py` passa; nenhum arquivo de `orq/` no diff (mexer em
   `memory/wiki/` não é `orq/` → **sem bump**).
5. Passos 3 e 5–8 antigos seguem, com dois acréscimos: o `portatil/README.md` carrega a tabela de
   garantias de escrita e o aviso de custo; o README do repo idem em uma linha.
6. **(novo)** O roteiro da semana Codex (decisão 5) ganha os itens: (a) gatilho da skill portátil
   por frase; (b) **reviewer Opus via `claude -p --model opus`** com briefing completo — comparar
   o parecer com o que o painel dá hoje no host Claude; (c) **implementer `sonnet` via
   `claude -p --permission-mode acceptEdits`** em worktree descartável (decisão 8) — tarefa
   pequena real, diff review antes do merge; (d) `spawn_agent` vivo: existe na sessão? lista de
   modelos? effort por filho?; (e) `codex exec` aninhado de dentro da sessão; (f) statusline e
   limites de conta na prática.

## Riscos novos (além de todos os anteriores, que seguem valendo)

- **`claude -p` chamado de DENTRO de uma sessão Codex/Kimi viva nunca foi testado** — os probes
  desta rodada saíram de uma sessão Claude. Auth OAuth, env herdado e nesting podem se comportar
  diferente. Primeiro dia da semana Codex, antes de depender disso.
- **Effort por filho no `spawn_agent` não confirmado** — se não existir, o elenco intra-OpenAI no
  host Codex cai para `codex exec` aninhado (não testado) ou uma sessão por effort.
- **Briefing de implementer cross-vendor não tem formato padronizado** — só o de revisão tem (o
  formato do painel). Se o briefing de escrita ficar grande demais, o custo por tarefa come a
  economia do rodízio; medir na semana e padronizar depois, com dado.
- **Rodízio parcial invisível** — sem a seção de custo no elenco, o dono acha que trocou de conta
  e não trocou (é o exemplo dele: Opus + Sonnet no host Codex mantêm a conta Claude ativa). A
  seção de custo é mitigação de primeira classe, não apêndice.
- **Duas fontes de comandos de invocação durante a transição** — até o passo 4 rodar, os comandos
  vivem em "Revisores externos" (formato atual); depois, na matriz. O passo 4 tem que deixar UM
  normativo e o outro apontando — nunca os dois enunciando.

## O que NÃO foi verificado nesta rodada (honestidade de fronteira)

- `claude -p` invocado a partir de sessão Codex/Kimi real (auth/env/nesting) — ver risco acima.
- `--agents <json>` combinado com `-p` (subagentes custom numa invocação externa): a flag existe,
  a semântica não foi exercitada.
- `spawn_agent` em sessão viva; effort por filho; `codex exec` aninhado.
- Escrita de implementer cross-vendor numa **tarefa real** (o probe 2 foi um Write unitário em
  scratch — prova a permissão, não o fluxo).
- Custo real por invocação (tokens/limites das três contas) — a tabela de custo desta seção é
  estrutural (quem cobra), não medida (quanto cobra).
- Tudo o que a lista da seção 🔵 já marcava como não verificado e não entrou acima.

## Decisões novas do dono (8–10 — as sete anteriores seguem fechadas)

> Sem resposta explícita, valem as recomendações — as três são as opções conservadoras.

8. **Onde o implementer cross-vendor escreve:** (a) **worktree descartável obrigatório na
   primeira fase, qualquer método** — recomendo: sem steering interativo, o único gate que sobra
   é o diff review antes do merge; (b) direto no working tree, confiando na garantia do método
   (`workspace-write` no Codex, `acceptEdits` no Claude). Trade-off em 1 linha: (a) paga fricção
   de worktree+merge por tarefa; (b) troca essa fricção por confiança num sandbox que não julga o
   conteúdo do que escreve.
9. **Preset de rodízio "zerar Claude"** (ex.: `codex-solo` — tudo `gpt@efforts` + `k3` revisor):
   (a) **só documentar a configuração no template agora; preset nomeado vira card se a semana
   mostrar uso** — recomendo: preset é território do `T-020`, e criar antes da demanda é engordar;
   (b) criar o preset já. Trade-off: (a) na semana ele configura papel a papel na mão; (b) mais um
   preset a sincronizar antes de saber se será usado.
10. **Reviewer durante o rodízio:** (a) **manter reviewer cross-vendor sempre** (Opus quando o
    host não for Claude — o exemplo que o próprio dono deu) — recomendo: diversidade de vendor no
    papel mais crítico é o valor mais comprovado deste repo; custa manter a conta Anthropic ativa
    mesmo na "semana OpenAI"; (b) reviewer do mesmo vendor do host (`gpt@xhigh` na semana Codex) —
    zera Claude de verdade, aceitando revisão menos descorrelacionada. Trade-off em 1 linha: (a)
    paga pela qualidade provada; (b) economiza no papel onde o erro custa mais caro.

## Próxima ação (substitui a da seção 🔵)

**Com o "pode implementar" do dono** (e as decisões 8–10, ou o silêncio = recomendações), o card
vai a READY e o implementer executa os **Passos revisados** desta seção, na ordem — o teste vivo
do hook do Kimi continua sendo o passo 0, pré-requisito, não passo final. **Sem o "pode
implementar", nada é criado.**

Pendências fora desta thread, para o Manager (não executadas por mim — só o Manager move board e
índice): a linha do `T-026` no `KANBAN.md` e a linha desta thread no `MEMORY.md` ainda carregam a
conclusão corrigida acima ("elenco cross-vendor não existe em nenhum host") e o estado antigo —
anotar quando o card se mover.

## 🗄️ RETOMAR AQUI — SUPERADO (ver o do fim do arquivo)

> Congelado em 2026-08-04, antes da implementação da 0.18.0. Mantido como registro do que se sabia
> naquele ponto. **O RETOMAR AQUI vivo é o último do arquivo.**


**Estado: REDESENHADO em 2026-08-04 pela decisão do dono (seção 🟢, no fim do arquivo) — e JÁ
AUTORIZADO ("prossiga com essa instalação para a gente testar"). Nada foi implementado ainda;
investigação read-only concluída.**

- **A linha "portátil" morreu**: não há cópia adaptada, não há sincronização, não há
  apodrecimento. `AGENTS.md` = `CLAUDE.md` (byte-idênticos, guardados por diff no lint) e o que
  se instala nos outros hosts é **o próprio plugin** — Codex via `codex plugin add` (user-scope,
  comprovado), Kimi via cópia para diretórios auto-descobertos (`~/.agents/skills/` existe;
  agents user-scope é o não-verificado nº 2).
- O card entrega: AGENTS.md unificado + guarda no lint + init gravando o mesmo bloco nos dois +
  **comando novo `/orq:instalar`** (instala nos hosts) + smoke test por host + elenco v2
  (migração do `_elenco.md` mantida da seção 🟣). Tudo em `orq/` → **bump 0.18.0**, depois do
  0.17.0/T-030 fechar — o Manager ordena a fila.
- Critério: os passos 1–9 da seção 🟢, cada um com verificação embutida; a "semana de 5 dias"
  morreu — o smoke test (passo 7, com ≥1 invocação cross-vendor por papel usado) a substitui.
- As 10 decisões: nenhuma reaberta; 6 substituída pelo smoke, 2 e 3 reinterpretadas (ver "Efeito"
  na seção 🟢). Decisões 11–13 de rodadas intermediárias **não existem mais** (linha morta).
- **Próxima ação: executar o passo 1** (unificar `AGENTS.md`/`CLAUDE.md` neste repo) e seguir a
  ordem. Não-verificados 1–5 da seção 🟢 se resolvem nos passos 5 e 7 — registrar resultado aqui.
- Pendências de board/índice para o Manager: ver nota ao fim da seção 🟣.

## ✅ DECISÕES 8, 9 e 10 — FECHADAS EM 2026-08-04

- **10 — decisão do dono: o revisor continua cross-vendor (Opus), mesmo na semana rodando no
  Codex.** Verbatim dele, e é ele quem reenquadra o card inteiro: *"manter o opus por enquanto — a
  ideia é trocar como LLM principal. Exemplo: hoje eu pago a assinatura 20x no Claude e 5x na
  OpenAI, aí às vezes alternar a depender de qual LLM esteja melhor naquele momento."*
- **8 — Manager, seguindo o planner e o precedente do `T-019`:** implementer cross-vendor escreve
  **só em worktree descartável** na primeira fase. Reversível; revisita quando houver evidência.
- **9 — Manager:** o preset "zerar Claude" fica **documentado, não criado**. O esclarecimento do
  dono na decisão 10 reforça: **ele não quer zerar nada.**
- **Subitem da 6, aceito:** o critério da semana ganha *"(v) ≥1 invocação cross-vendor por papel
  usado na semana"*.

## ⚠️ O OBJETIVO DO CARD FOI REENQUADRADO PELO DONO — e isso corrige o card e este plano

O `T-026` vinha escrito como **rodízio de custo entre assinaturas**. Não é isso.

**O objetivo real, na fala dele: poder trocar o LLM principal conforme qual estiver melhor naquele
momento.** Custo é contexto, não meta — ele mantém as duas assinaturas ativas de propósito
(**Claude 20x · OpenAI 5x**) e quer liberdade de escolher o motor, não economia.

**O que isso corrige:**
- A frase "desloca o gasto, não zera" era um **alerta correto respondendo à pergunta errada**.
  Deslocar é o objetivo; zerar nunca foi.
- O critério de sucesso deixa de ser "quanto poupou" e passa a ser **"consegui trabalhar a semana
  inteira no outro motor sem perder a disciplina"** — que é o que a decisão 6 já mede. A decisão 6
  estava certa por acidente; agora está certa por construção.
- A tabela "Custo por configuração" continua no template, mas com outra função: **informar a
  escolha**, não perseguir economia.

## ⚠️ SEGUNDO REENQUADRAMENTO DO DONO (2026-08-04) — a cadência é POR CICLO DE MERCADO, não semanal

Verbatim: *"Eu não vou ficar trocando por semana, mas apenas por ciclo. Existem épocas em que, após
algum lançamento de uma LLM nova, a OpenAI fica melhor que a Anthropic. Nesse período, eu aumento a
mensalidade da OpenAI e diminuo da Anthropic. Vice-versa, quando acontece o contrário. Não é por
semana, é simplesmente alternar entre assinaturas maiores e menores para aproveitar os melhores
modelos sempre."*

**A troca é um evento RARO** — disparado por lançamento de modelo, não por calendário. Entre uma
troca e outra podem passar **meses**. Isso reposiciona três coisas:

**1. O que o teste de 5 dias mede muda de função.** Não é mais "provar que dá para trabalhar uma
semana no outro motor" — é **provar que o setup funciona no dia em que ele precisar**. Quando o
momento chegar (modelo novo lançado, assinatura já trocada), ele não vai querer passar dois dias
configurando: vai querer abrir o outro CLI e continuar. A métrica de valor passa a ser **"quanto
tempo leva para trocar"**, não "quanto aguentei fora do Claude".

**2. O risco de apodrecimento vira O problema central do card.** O plugin evolui — 7 releases em 9
dias. Se o portátil for escrito hoje e usado daqui a três meses, ele estará **três meses atrasado**
em relação à `SKILL.md`, e o dono descobre isso no pior momento: no dia da troca, com a assinatura
já migrada.

**3. E aqui a conexão que o `T-030` acabou de pagar caro para ensinar:** o plano de 30/jul propunha
que o portátil declarasse *"derivado da SKILL.md vX.Y.Z"* e que todo release ganhasse **o dever de
sincronizar**. Isso é **processo manual de sincronização entre dois lugares** — exatamente o defeito
que custou **cinco rodadas de painel** esta semana, e que falhou mesmo com gate, `grep` e três
revisores olhando. Com **meses** entre as sincronizações e nenhuma pressão de uso no meio, a chance
de sobreviver é menor ainda.

**Hipótese que o plano precisa avaliar: gerar o portátil a partir da `SKILL.md` no release, em vez
de mantê-lo sincronizado à mão.** Um só lugar normativo — o mesmo princípio que a 0.17.0 adotou para
resolver o A1. Se gerar não for viável, a alternativa honesta é o portátil **declarar sua defasagem
em voz alta** (versão de origem no cabeçalho + o `lint-coerencia.py` falhando quando a `SKILL.md`
mudou e o portátil não), nunca um "dever de sincronizar" confiado à disciplina humana.

⚠️ **Dado que o plano precisa carregar, e que a proporção 20x/5x torna concreto:** o **motor é o
papel que mais gasta** — o próprio `_elenco.md` já registra isso (*"o Manager não muda: o maior
consumo é a sessão principal"*). Mover o motor para o Codex consome a assinatura **menor** (5x) no
papel mais caro, enquanto a maior (20x) fica ociosa. Isso não desaconselha nada — a meta é escolher
o melhor motor do momento —, mas **a semana no Codex provavelmente esbarra no teto da conta OpenAI
antes de completar 5 dias**. O roteiro da semana deve prever isso: se o teto chegar antes do fim, o
resultado do teste **não é "falhou"** — é "a assinatura 5x não sustenta uma semana de motor", que é
uma resposta útil e diferente.

---

# 🟢 REDESENHO FINAL — 2026-08-04 · instalação global por host; `AGENTS.md` = `CLAUDE.md`

> **Supera a hipótese da seção ⚠️ acima (gerar/sincronizar um "portátil").** O dono decidiu, e a
> decisão elimina a premissa que criava o problema. Planner `fable` · investigação **read-only**
> desta rodada: nenhum arquivo tocado além desta thread, nada instalado.

## A decisão do dono, verbatim — encerra a linha "portátil"

> "Eu acho que esse negócio de ler um outro arquivo não serve. Eu acho que o agent MD tem que ter
> o mesmo conteúdo do Claude MD, no caso do Claude. O framework tem que ficar bem estabilizado e
> completo, de forma que possa ser instalado globalmente em Claude, Kimi e Codex, ou ter um
> comando. Por exemplo, aqui já está instalado globalmente. Eu não sei se está instalado em Codex
> e Kimi. Tem um comando para instalar neles especificamente."

E antes, sobre a complexidade: *"Isso era para funcionar em qualquer LLM, apenas adaptado aos
motores de cada uma. Hoje todas as LLMs têm um agent MD, Claude MD ou sistema de multiagentes,
então eu não vejo qual a dificuldade de implementar isso."* **Ele está certo** — ver "O que sobrou
de difícil" no fim.

**O que muda:** não existe "portátil" como cópia adaptada. O que se instala nos outros hosts é
**o próprio plugin** (o Codex aceita o formato Claude as-is — comprovado em 04/ago; o Kimi carrega
skill e agent em formato Claude — comprovado vivo). `AGENTS.md` carrega **o mesmo conteúdo** do
`CLAUDE.md`, byte a byte — identidade é verificável por `diff`, então sincronização deixa de ser
disciplina e vira gate mecânico. Já autorizado pelo dono: *"prossiga com essa instalação para a
gente testar"* — os passos abaixo vão direto para execução.

### Linha morta — registro do desvio (tem valor, não reabrir)

1. *"Release que mexer na SKILL ganha o dever de sincronizar"* (30/jul) — morta: era o defeito do
   `T-030` (regra em dois lugares, sync manual).
2. *Gerar o portátil no release / lint quebrando por hash* (hipóteses da seção ⚠️) — analisadas e
   mortas: a transformação da `SKILL.md` exigia julgamento (das 23 refs a `/orq:*`, ~13 saíam por
   remoção mecânica, ~10 estavam tecidas na prosa), e o fail-loud taxava toda release. Mas ambas
   resolviam um problema que **só existia porque se assumiu cópia adaptada**.
3. *`AGENTS.md`-ponteiro ("leia o arquivo X e siga")* — proposto pelo Manager, **recusado pelo
   dono**: conteúdo igual, não ponteiro.

## Verificado nesta rodada (read-only, 2026-08-04)

- **Raiz do repo**: `AGENTS.md` **já existe (1,0K) e é ponteiro + briefing de revisor** — diverge
  do `CLAUDE.md` (4,5K) por desenho antigo. É o alvo do passo 1.
- **Codex — instalação é user-scope e persiste**: `codex plugin` tem `add · list · marketplace ·
  remove`; o instalado vive em `~/.codex/config.toml` (`[plugins."<nome>@<marketplace>"]`) +
  cache `~/.codex/plugins/cache/<mkt>/<plugin>/<versão>/`. O experimento de 04/ago instalou o orq
  0.17.0 `enabled` com os 25 arquivos e reverteu limpo — o mecanismo está comprovado ponta a
  ponta. `codex plugin list` desta máquina hoje: orq **não** instalado (a reversão ficou).
- **Kimi — NÃO tem subcomando de instalação** (help: nada de plugin/install; só `migrate`/
  `upgrade` do próprio CLI). Instalar = **copiar arquivos para diretórios auto-descobertos**. O
  próprio `--help` confirma que existem: `--skills-dir` diz *"instead of auto-discovered **user
  and project directories**"*; `--agent` diz *"discovered from **agent directories**"*.
- **Nesta máquina**: `~/.agents/skills/` **existe** (3 skills de outros CLIs — é o diretório
  compartilhado padrão); `~/.kimi-code/skills/` e `~/.kimi-code/agents/` **não existem ainda**;
  não há `~/.kimi-code/AGENTS.md` global (o AGENTS.md do Kimi é por diretório de projeto —
  `{{ KIMI_AGENTS_MD }}`, verificado por strings).
- **Claude**: instalado user-scope; cache vai até `0.16.0` — a 0.17.0 (T-030) é release em curso,
  ainda não instalada aqui.
- **`/orq:init` hoje** (`init.md:178-181`): grava bloco `<!-- orquestra:start -->` no `CLAUDE.md`
  e, no `AGENTS.md`, *"se existir, ponteiro equivalente de poucas linhas"* — é exatamente o que a
  decisão do dono muda.

## NÃO verificado — marcado, com o teste que decide (não assumir)

1. **O que o Codex ATIVA do plugin instalado em sessão viva** (skill listada? gatilho por frase?
   commands? agents?) — só sessão interativa responde. Decide-se no smoke test (passo 7).
2. **Qual diretório user-scope o Kimi descobre para AGENTS (perfis)** — `~/.kimi-code/agents/` é
   hipótese (strings citam o equivalente de projeto); o dir não existe hoje. Testar no passo 5;
   fallback declarado: `--agent-file` / `.kimi-code/agents/` do projeto.
3. **Formato de agente que o `spawn_agent` do Codex consome** — a doc de plugin não cita `agents/`
   como componente; o plugin copia os 5 arquivos, mas usar é outra história. Smoke test.
4. **As 23 refs `/orq:*` da `SKILL.md` dentro do Kimi** — lá os commands não existem; a tabela de
   intenções descreve **o que fazer** além do nome do comando, então um modelo capaz segue a ação
   e ignora o nome — **suposição**, o smoke test decide. Se atrapalhar: card futuro (fraseado
   host-neutro na SKILL — mexe no produto de todos, entra pelo ciclo).
5. **Gatilho por frase no Codex** — risco nº 1 desde a seção 🔵, inalterado.

## Passos de execução (autorizados; ordem de dependência)

1. **`AGENTS.md` = `CLAUDE.md` neste repo.** Unificar: o briefing de revisor externo que hoje só
   está no `AGENTS.md` entra no conteúdo comum como seção condicional por identidade ("Se você é
   um revisor externo entrando pelo painel…") — **zero exceções por host**, os dois arquivos
   byte-idênticos. Verificável: `diff CLAUDE.md AGENTS.md` vazio.
2. **Guarda no lint** (`orq/scripts/lint-coerencia.py`): na raiz varrida, se `AGENTS.md` e
   `CLAUDE.md` existem e diferem → **erro** (mesma família dos guardas de versão). Divergência
   deixa de ser possível em silêncio. (Se um dia precisar de trecho por host: exceção **declarada**
   em marcador que o lint entende — hoje não há nenhuma.)
3. **`/orq:init`**: o passo do `AGENTS.md` muda de "ponteiro se existir" para "**grave o mesmo
   bloco `<!-- orquestra:start -->` nos dois, criando o `AGENTS.md` se não existir**"; a
   verificação do init ganha "diff dos blocos = vazio". Projetos novos já nascem certos.
4. **Comando novo `/orq:instalar`** (o `init` instala no projeto; este instala **nos hosts**,
   escopo usuário — é o comando que o dono pediu):
   - **Codex**: `codex plugin marketplace add <caminho-deste-repo>` +
     `codex plugin add orq@orquestra`. Verificação embutida: `codex plugin list` mostra
     `installed, enabled` + `diff -rq ~/.codex/plugins/cache/orquestra/orq/<versão>/ ./orq/`
     vazio. Reversão documentada: `codex plugin remove` + `marketplace remove` (comprovada limpa).
   - **Kimi**: copiar `orq/skills/orq/` → `~/.agents/skills/orq/` (diretório compartilhado, já
     existe) e `orq/agents/*.md` → `~/.kimi-code/agents/` (**criar; descoberta é o não-verificado
     nº 2** — o comando testa e cai no fallback se falhar). Verificação: `diff -rq` das cópias +
     fumaça `kimi -p` listando a skill.
   - **Claude**: já instalado — o comando só confere versão×cache (o que o `--verificar` já faz).
   - O comando **carrega o gotcha cache×versão dos dois lados** (Claude e Codex, ambos
     comprovados): *release novo → rodar `/orq:instalar` de novo*; e **avisa**: no Kimi a cópia é
     snapshot — sem re-rodar, fica velha (mesma regra, terceiro host).
5. **Teste de descoberta no Kimi** (resolve o não-verificado nº 2): fumaça `kimi -p` **sem**
   `--skills-dir`, fora do repo → a skill `orq` aparece? perfil de agent descoberto? Registrar
   resultado; se `~/.kimi-code/agents/` não descobrir, o fallback do passo 4 vira o oficial.
6. **Release** — passos 2–4 mexem em `orq/` → **bump 0.18.0 nos quatro lugares** + os dois gates +
   `marketplace update` + `plugin update` + restart + `diff -rq` vazio no Claude; em seguida
   `/orq:instalar` re-instala nos outros hosts. *(Sequência com o release 0.17.0/T-030, que ainda
   não fechou: o Manager ordena — este card não fura a fila.)*
7. **Smoke test por host** (substitui a "semana de 5 dias"; subitem *(v) ≥1 invocação
   cross-vendor por papel usado* — mantido): em cada host, sessão interativa neste repo:
   "onde paramos?" → board sem comando digitado; criar card de teste → **para no gate**; board e
   thread editados (`kanban-status.sh` sem `⚠`); ≥1 invocação cross-vendor pela Matriz do elenco.
   No **Codex**, registrar o que o plugin ativou (não-verificados 1, 3 e 5). No **Kimi**, sem
   `-y`; escrita continua condicionada ao hook testado vivo (decisão 4, intacta).
8. **Elenco v2** — inalterado da seção 🟣: `portatil/elenco-template.md`… **corrigindo o
   endereço**: com o fim do "portátil", o template do elenco v2 passa a morar junto do produto ou
   da wiki — decidir na implementação entre `orq/` (vira produto, já há bump no passo 6) e
   `memory/wiki/` (só instância). A **migração aditiva do `_elenco.md` deste repo** (Papéis +
   Matriz de invocação + custo) segue como estava — os probes de escrita e a matriz continuam
   válidos e são o que o passo 7 usa.
9. **Checkpoint**: `arquitetura.md` ganha "instalação por host"; log; board; esta thread.

## Como o dono verifica que instalou (resposta direta)

| Host | Verificação |
|---|---|
| Claude | `claude plugin list` + `diff -rq ~/.claude/plugins/cache/orquestra/orq/<v>/ ./orq/` vazio (como hoje) |
| Codex | `codex plugin list` → orq `installed, enabled` + `diff -rq ~/.codex/plugins/cache/orquestra/orq/<v>/ ./orq/` vazio |
| Kimi | `diff -rq ~/.agents/skills/orq/ ./orq/skills/orq/` vazio (+ agents idem) e a skill aparecendo numa fumaça `kimi -p` |
| AGENTS.md | `diff CLAUDE.md AGENTS.md` vazio — e o lint quebra sozinho se divergir |

## O que sobrou de genuinamente difícil — com franqueza

**Instalar não é difícil.** Os formatos convergiram e está tudo comprovado: o Codex consome o
marketplace Claude como está; o Kimi carrega skill e agent em formato Claude; `AGENTS.md` os dois
leem. A suspeita do dono estava certa — **a complexidade era do plano, não do problema**. O que
resta de verdade, e é pouco:

1. **O que o Codex ativa** do plugin (gatilho, commands, agents) — incerteza real, só sessão viva
   responde; o smoke test é o teste.
2. **Elenco multi-modelo fora do Claude** — spawn nativo não é cross-vendor em host nenhum; a
   Matriz de invocação por CLI cobre, e este repo já a pratica todo dia no painel.
3. **Kimi sem sandbox** — decisão 4 (hook testado vivo antes de escrever) de pé; não é deste card
   resolver.
4. **Os 12 commands `/orq:*` fora do Claude** — no Kimi não existem; a interface natural via
   skill/AGENTS.md cobre a intenção (não-verificado nº 4). Se o smoke mostrar atrito, card futuro.

## Efeito sobre as 10 decisões — nenhuma reaberta

- **6 (semana de 5 dias)** — morre como critério; o **smoke test por host** (passo 7) a substitui,
  mantendo o subitem (v). Se o dono quiser dias seguidos noutro host, é uso real, não gate.
- **2 (AGENTS.md + skill portátil)** — reinterpretada pela decisão do dono: a skill instalada nos
  hosts é **a do próprio plugin**, não uma versão portátil; o AGENTS.md é o mesmo conteúdo do
  CLAUDE.md, não um template derivado.
- **3 (`portatil/`)** — esvaziada quase toda: sem artefatos portáteis, resta decidir o endereço do
  template do elenco v2 (passo 8).
- **1, 4, 5, 7, 8, 9, 10** — intactas (5 ordena os smoke tests: Codex primeiro).

---

# 🔍 REVIEW DA 0.18.0 — painel de três, 2026-08-04

**Opus REPROVADO (4 bloq.) · Codex REPROVADO (4 bloq.) · Kimi REPROVADO (3 bloq.)**

⚠️ **Erro de PROCEDIMENTO do Manager, e vira gotcha:** a primeira passada do Kimi rodou sobre um
worktree **sem o `orq/commands/instalar.md`** — arquivo novo é **untracked**, e `git diff` não
inclui untracked. O parecer dele estava certo para o que via; a premissa é que estava furada.
Corrigido com `git add -N` e rerodado. **Toda release que cria arquivo tem esse ponto cego** — o
patch do painel precisa de `git add -N` antes. Só apareceu porque um revisor foi **conferir se o
arquivo existia** em vez de assumir.

## Achados

### 🔴 B1 — `<fonte>` remoto é aceito e depois tratado como caminho local *(os TRÊS)*
`instalar.md:24` × `:45`, `:64-65`, `:70-71`. O passo 0 autoriza referência remota
(`brunocangussu/byia-claude-orquestra`); todo uso posterior espera caminho de filesystem.
**Cenário:** máquina de terceiro, ou a do dono com o marketplace registrado pelo slug →
`cp -r brunocangussu/byia-claude-orquestra/orq/… ` → *No such file or directory* → e a regra
"Falhou? pare esse host" deixa **o Kimi impossível de instalar**, justamente no caso que o passo 0
convida. **Correção:** para fonte remota, derivar do cache (`~/.claude/plugins/cache/orquestra/orq/<versão>/`,
que o próprio arquivo já cita) ou clonar para temp — e declarar isso no passo 0.

### 🔴 B2 — A instalação no Kimi NÃO entrega o framework completo *(Codex)*
`instalar.md:64`. Copia **skill e agents, nenhum comando**. Mas a skill **aponta** para os comandos:
*"pode implementar"* → `/orq:implement-next`, cuja instrução não existe no host.
**Vai direto contra o pedido do dono** (*"o framework tem que ficar bem estabilizado e completo"*):
é subconjunto, e o comando não declara isso. O planner tinha marcado a incerteza supondo que "o
modelo segue a ação descrita" — mas a skill **não descreve** a ação, ela aponta para quem descreve.
**Duas saídas:** copiar os procedimentos junto (cada comando vira skill no Kimi, ou um arquivo único)
ou declarar subconjunto experimental com todas as letras. **A primeira é o que o dono pediu.**

### 🔴 B3 — `cp -r` aninha na reinstalação e deixa a versão velha rodando *(Opus + Codex)*
`instalar.md:63-66` × `:95`. A seção manda re-rodar a cada release; na 2ª execução o destino já
existe e `cp -r` copia **para dentro** → `~/.agents/skills/orq/orq/SKILL.md`, enquanto o arquivo que
o Kimi carrega segue na versão antiga. **É o gotcha do cache stale reencarnado em `cp -r`.**
**Correção:** `rm -rf` antes, ou `cp -r <fonte>/orq/skills/orq/. <destino>/`.

### 🔴 B4 — Contradição: bloco idêntico × arquivo inteiro idêntico *(Kimi 2×, Opus)*
`init.md:182-184` e `:213-215` × `lint-coerencia.py:138-147`. O `init` sanciona *"fora do bloco cada
um pode ter conteúdo próprio"* e a FASE 5 confere só **o bloco**; o lint exige **arquivo inteiro**
byte-idêntico. Duas instruções do mesmo plugin, vereditos opostos sobre o mesmo estado.
**Sexta ocorrência do defeito da semana.** **Decisão do Manager:** vence o lint — o dono foi
explícito (*"o agent MD tem que ter o mesmo conteúdo do Claude MD"*). Alinhar o `init.md`, não
afrouxar o guarda. E a regra forte precisa estar em **prosa** — hoje só existe em comentário de
Python e numa nota de release.

### 🔴 B5 — Guarda do lint é cego quando um dos arquivos some *(Codex bloq. + Opus risco)*
`lint-coerencia.py:138`: `if claude_md.exists() and agents_md.exists()`. Apagar o `AGENTS.md` passa
calado — troca "divergiu" por "sumiu", que é o mesmo silêncio que o gate veio eliminar.
**Correção:** falhar quando existir exatamente um dos dois.

### 🔴 B6 — `init.md:70` aponta para o item errado *(Kimi 2×, verificado)*
*"Do que faltou no item 5"* — a linha está na FASE 2 e referencia a lista da **FASE 1**, onde o item
5 é *Trabalho em aberto* e o ferramental é o **6**. A renumeração valia para a FASE 4.
**Correção:** voltar a "item 6", ou **nomear** em vez de numerar.

### 🟠 B7 — Gatilhos novos colidem, e o erro é do Manager *(Opus + Kimi)*
`SKILL.md:80`. Escrevi a linha e errei em dois pontos:
- *"quero testar em outra LLM"* casa com `/orq:elenco` (`:75` é literalmente "qual LLM toca cada
  papel"). Declarei desempate só contra o `/orq:stack`. **`T-016` reencenado.**
- *"prossiga com essa instalação"* é a **frase de aprovação no gate** — dispararia o comando em vez
  do Loop B, pulando painel e docs. E o `/orq:stack` termina exatamente numa proposta de instalação.
- **"instala isso no Codex" foi inventada por mim** — as atestadas são *"tem um comando para instalar
  neles"* e *"testar em outras LLMs"*. **Quarta reincidência do `T-014`, desta vez pelo Manager.**
**Correção:** só frases que nomeiem **host ou Orquestra**, e desempate contra `elenco` **e** `stack`.
*(O Kimi registrou que o desempate por objeto é bom — baseado na propriedade real, não em proxy,
"melhor que o T-016". O defeito é a frase, não o critério.)*

### 🟠 Riscos confirmados
- `instalar.md:31` manda **executar** `/orq:stack --verificar` — contra `init.md:191`
  (*"nunca pelo slash command, que você não invoca"*). Apontar o arquivo. *(Opus)*
- `diff -rq ~/.kimi-code/agents/ …` compara diretório **compartilhado** do usuário → falso negativo
  no dia em que houver agente próprio ali. Comparar arquivo a arquivo. *(Opus + Kimi)*
- **Seção do Kimi sem reversão documentada** — o Codex tem; o Kimi só instala, e sobra snapshot
  envelhecendo sem aviso. *(Kimi)*
- Comando distribuído cita `memory/wiki/threads/T-026…` e seção do `gotchas.md` **deste** repo —
  em projeto de terceiro não existem. *(Opus + Codex)*
- `/orq:instalar` **não aparece** no cardápio do `/orq:ajuda`. *(Opus)*

### ⚖️ Divergência que o Manager desempatou
`AGENTS.md:1` se identifica como `CLAUDE.md` e prescreve `/clear`, que não existe nos outros hosts.
**Codex** classificou como risco de confusão; **Kimi** — que é outro host e leu o arquivo inteiro —
verificou e disse que *"o que é específico de Claude degrada inerte"*. **Desempate: o Kimi tem a
evidência mais forte** (leu como o host real, não especulou). Fica como risco baixo, tratável com
seção condicional dentro do conteúdo comum, no mesmo padrão do briefing de revisor externo.

### ✅ Verificado e aprovado pelo Kimi (não são achados)
Identidade `AGENTS.md`=`CLAUDE.md` byte a byte · guarda do lint exercitado · bump nos quatro lugares
· hipótese do `~/.kimi-code/agents/` honestamente marcada com fallback · caminho de cache e reversão
do Codex **atestados** pelo experimento de 04/ago · todas as referências internas do `instalar.md`
existem · fallback de binário fora do PATH.


---

## ⏭️ RETOMAR AQUI (atualizado 2026-08-04, fim do dia)

**Estado: 0.18.0 implementada, revisada por TRÊS painéis e corrigida em duas rodadas. Gates verdes.
Tudo no working tree, NÃO COMMITADA.** Bump nos quatro lugares. Nada instalado de verdade em host
nenhum.

**Convergência dos painéis:** 6 bloqueadores + 5 riscos → 2 bloqueadores + 5 riscos → corrigidos.
Todo o resto foi auditado item a item pelos três e está correto, **incluindo a dúvida central do
desenho**: todo `${CLAUDE_PLUGIN_ROOT}` dos comandos copiados resolve, e nenhum referencia arquivo
que ficou de fora (verificado por simulação em diretório descartável, com `cp` rodado duas vezes).

### As dez decisões do dono continuam fechadas — não repergunte nenhuma

Codex como primeiro host · Kimi escreve só com hook `PreToolUse` **testado vivo antes** (fail-open:
"configurei" ≠ "funciona") · revisor segue Opus mesmo na semana OpenAI · estratégia A ampliada + C ·
`AGENTS.md` = `CLAUDE.md` **mesmo conteúdo, não ponteiro** · mora em `portatil/` (superado: o que se
instala é o próprio plugin) · implementer cross-vendor só em worktree · preset "zerar Claude" só
documentado · card port-Kimi condicionado · smoke test no lugar da "semana de 5 dias".

### Próxima ação, em ordem

1. **Commit da 0.18.0** — só com o ok do dono.
2. **Release na máquina dele:** `claude plugin marketplace update orquestra` +
   `claude plugin update orq@orquestra` + **reiniciar a sessão** + `diff -rq` do cache vazio.
   ⚠️ Este release entrega **0.17.0 e 0.18.0 juntas** — o dono nunca rodou o release da 0.17.0.
3. **Passos 5–9 do redesenho:** teste de descoberta vivo no Kimi · smoke test por host (≥1 invocação
   cross-vendor por papel usado) · elenco v2 (Matriz de invocação — **hoje ela só existe como plano
   nesta thread, não como artefato vivo**; o implementer corretamente se recusou a apontar a skill
   para ela e apontou para `_elenco.md`, que existe) · checkpoint.

### Aberto, e é do dono

**A instalação no Kimi tem uma hipótese não confirmada:** `~/.kimi-code/agents/` como diretório de
perfis de agente. O `~/.agents/skills/` **existe** nesta máquina e é o caminho provável da skill; o
de agents, não. **Só o teste vivo decide** — está marcado como hipótese dentro do próprio comando,
com fallback.

### Card pequeno que nasceu e não foi aberto

O `description` do frontmatter da `SKILL.md` — o texto que faz a skill disparar sozinha — **não
menciona instalação**. A tabela interna está correta, mas o gatilho de entrada não cobre o assunto
novo. Não é bloqueador (a skill dispara por outros gatilhos e a tabela roteia dentro), mas se o dono
disser *"instala o orq no Codex"* numa sessão fria, a skill pode não ser invocada.
