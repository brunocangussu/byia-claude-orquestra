# Thread — T-026 · Orquestra fora do Claude Code — Codex ou Kimi como host

**Frente:** portabilidade da disciplina · matriz de paridade Codex/Kimi · estratégia de host alternativo.
**Aberta em** 2026-07-30 · **estado: PLANO PRONTO — aguarda gate do dono** · planner `fable`.
**Nada em `orq/` foi editado** — este arquivo é o único artefato.

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
equivalente: **subagente no Codex**, **elenco multi-modelo por papel** fora do Claude,
**statusline**, **sandbox no Kimi** — e, mais importante, a **combinação testada**: o produto só
foi provado comportamentalmente num host, e teste comportamental é o único gate que pega defeito
aqui (lição do `T-012`).

## Matriz de paridade (verificado nesta máquina em 2026-07-30, salvo indicação)

Versões: Codex CLI `0.145.0-alpha.4` (`/usr/local/bin/codex`) · Kimi Code `0.29.2`
(`~/.kimi-code/bin/kimi`, symlink em `~/.local/bin/kimi`).

| Primitiva que o orq usa | Claude Code | Codex CLI | Kimi Code |
|---|---|---|---|
| Instrução persistente por projeto | `CLAUDE.md` | `AGENTS.md` — **verificado** global (`~/.codex/AGENTS.md` existe, 19.9K); projeto = comportamento documentado do produto | `AGENTS.md` — **verificado por strings do binário**: o system prompt injeta `{{ KIMI_AGENTS_MD }}` ("The applicable AGENTS.md instructions are"), com AGENTS.md por diretório; fluxo de import menciona `AGENTS.md`/`CLAUDE.md`. Doc oficial não achada (página "context" = 404) |
| Skill carregada por intenção | `skills/orq` | skills existem — **verificado** `~/.codex/skills/` com ~25 skills instaladas; invocação automática por description = **suposição** (doc de plugins cita "skills" sem detalhar gatilho) | **verificado (doc oficial)**: `SKILL.md` + frontmatter (`whenToUse` extra), auto-invocação pelo modelo via description; descoberta em `~/.kimi-code/skills/`, `~/.agents/skills/`, projeto `.kimi-code/skills/` e `.agents/skills/` |
| Comando nomeado (`/orq:*`) | 12 commands | **não verificado**: `~/.codex/prompts/` não existe nesta máquina; doc de plugins **não** lista commands como componente | **verificado (doc)**: `/skill:nome` para skill explícita + plugins registram `commands` de arquivos markdown |
| Subagente com contexto próprio | Task tool + 5 agents | **não existe** (verificado por ausência: nenhuma flag, `enable_fanout` under-development/off, `collaboration_modes` removed) | **verificado (doc)**: sub-agents automáticos com contexto isolado; agents em markdown **compatíveis com o formato Claude Code** (campo `tools` em vírgulas carrega) |
| Override de modelo por papel (elenco) | spawn com `model:` | só por sessão (`-m`); sem subagente não há "por papel" | **limitado**: `model_preference` = `primary`/`secondary` apenas — não há "planner no X, implementer no Y" |
| Hook | primitiva existe (orq não declara — `T-001` pendente) | existe — **verificado**: `features` mostra `hooks`/`plugin_hooks` stable+true, `~/.codex/hooks.json` presente; semântica de eventos **não verificada** | **verificado (doc)**: `[[hooks]]` no `config.toml`; `PreToolUse`/`Stop`/`UserPromptSubmit` **bloqueáveis** (exit 2 nega) — dá para negar `git checkout/reset`, o que o `T-019` pediu. Escopo por projeto **não verificado** (doc só mostra user-scope) |
| Sandbox | permissões nativas | **verificado**: `-s read-only`/`workspace-write`/`danger-full-access` + execpolicy `.rules` de usuário **e projeto** (`--ignore-rules` confirma) | **não existe** — só `-y`/`--auto`, que REDUZEM proteção. Confirma o `_elenco.md` |
| Modo não-interativo | `claude -p` | **verificado**: `codex exec` + `--json`, `-o <file>`, `--output-schema`, `resume`; `< /dev/null` obrigatório (conhecido) | **verificado**: `kimi -p --output-format text\|stream-json`; `< /dev/null` obrigatório (conhecido) |
| Plugin / empacotamento | `.claude-plugin/` | **verificado nesta máquina**: `codex plugin marketplace add` aceita marketplace **formato Claude** (o `claude-plugins-official` aponta `.claude-plugin/marketplace.json`; `superpowers` instalado por ele). Doc oficial: plugin = skills + MCP + hooks + connectors; **agents e commands não citados** → presumo ignorados | formato próprio: `kimi.plugin.json` ou `.kimi-plugin/plugin.json` — **sem conversão do formato Claude (doc)**, mas componentes quase 1:1: skills, agents, commands, hooks, MCP, instruções de system-prompt, skill auto-carregada no início |
| `${CLAUDE_PLUGIN_ROOT}` | sim | equivalente **não verificado** | equivalente **não verificado** |
| Statusline | comando de statusline | não encontrado — **suposição de ausência** | não encontrado (`tui.toml` não tem campo) — **suposição de ausência** |
| Agendado / modo noturno | session-scoped (limitação conhecida) | "scheduled task templates" em plugins (doc; **não verificado**) | não encontrado |

**Leitura da matriz:** a disciplina (board, wiki, gates, handoff, escala de risco, multi-janela) é
markdown lido por qualquer um dos três — os scripts `kanban-status.sh` e `lint-coerencia.py` são
bash/python genéricos e rodam em qualquer host. O que morre fora do Claude Code: os 12 comandos
como estão, o elenco por papel, a statusline, e (só no Codex) o worker de contexto fresco.

## Solução — três estratégias, custo honesto

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
multiplicado, e paridade central impossível no Codex (sem subagente). Se o A provar demanda real,
um "port Kimi" vira card futuro — o Kimi é o único onde faria sentido.

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

1. Criar `portatil/AGENTS-orquestra.md` — template derivado da `SKILL.md` 0.13.0: roteamento por
   intenção, máquina de estados, marcadores, regras 1–9, checkpoint manual (o que gravar e onde),
   protocolo multi-janela, contrato do board (referência ao `_schema.md` do projeto). **Sem** uma
   única citação a `/orq:*`, spawn, elenco ou statusline. Verificável: `grep -c "orq:" = 0`.
2. Criar `portatil/skills/orq-portatil/SKILL.md` — formato Agent Skills (`name` + `description`;
   `whenToUse` extra para o Kimi), corpo apontando para o `AGENTS.md` e o board. Verificável:
   frontmatter carrega nos dois hosts (`kimi doctor` ok; skill listada).
3. Criar `portatil/README.md` — instalação por host: Codex (referenciar no `AGENTS.md` do projeto;
   skill em `~/.codex/skills/` ou `~/.agents/skills/`), Kimi (idem; **nunca `-y`/`--auto`**, aviso
   T-019 explícito), e o **disclaimer de paridade** (o que não existe fora do Claude Code).
4. *(condicionado à decisão 5)* Implementer roda o experimento: `codex plugin marketplace add`
   deste repo + `codex plugin add orq` e **documenta o que o Codex efetivamente aproveitou**
   (reversível com `remove`; não é dependência do A).
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

## Decisões do dono (numeradas — responda "1a, 2…" que destrava tudo)

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
6. **Card futuro "port Kimi" (`kimi.plugin.json`):** criar no backlog condicionado a uso real do
   A — **recomendo**; criar já seria engordar o board com aposta.

## Riscos

- **Duas fontes da disciplina** (SKILL.md do plugin + template portátil) vão divergir — é o padrão
  "vocabulário espalhado" que já custou 4 correções numa sessão. Mitigação: o template declara no
  cabeçalho "derivado da SKILL.md vX.Y.Z"; release que mexer na SKILL ganha o dever de sincronizar
  (linha no checkpoint do release, não sistema novo).
- **Roteamento por intenção não testado em GPT/K3.** A description funciona no Claude após o
  `T-014`; nada garante que outro modelo leia igual. Se o teste 1 falhar, o ajuste é no texto do
  template — por isso o teste é critério, não suposição.
- **Kimi sem sandbox**: qualquer sessão de escrita no Kimi carrega o risco `T-019` inteiro até a
  decisão 4 ser resolvida — o template precisa carregar esse aviso no próprio corpo.
- **Multi-janela cross-host**: dono com Claude numa janela e Codex noutra sobre o mesmo repo — o
  protocolo (releia antes de escrever, edite a linha) vale, mas nunca foi exercitado entre hosts
  diferentes. O template carrega a seção; o risco residual fica anotado.
- **Codex alpha**: `0.145.0-alpha.4` — flags e comportamento de plugin podem mudar sob os pés.

## Escopo — fica de fora

- `T-021` (papéis via CLI com Claude de host) — a Estratégia C é ele; não detalhado aqui.
- `T-020` (perfis de elenco) — o "modo economia" extremo pode um dia apontar para o host
  alternativo, mas é decisão daquele card.
- Port completo por host (Estratégia B) — só como card futuro condicionado (decisão 6).
- Enforcement (`T-001`/`T-002`) em qualquer host; statusline fora do Claude; modo noturno fora do
  Claude; mover cards; editar `orq/` ou `memory/` além desta thread.

## O que NÃO investiguei (e por quê)

- **Sessão interativa real do Codex e do Kimi** — a investigação foi `--help`, configs, cache e
  doc oficial, tudo em leitura. O roteamento por intenção nos dois hosts é o que o teste
  comportamental do dono vai provar; afirmar antes seria o erro do `T-014`.
- **`codex plugin marketplace add` do orq** — muta a config do Codex; fora do modo leitura deste
  planejamento. Virou o passo 4 / decisão 5.
- **Custom prompts do Codex** (`~/.codex/prompts/`) — o diretório não existe nesta máquina e a doc
  atual de plugins não os cita; não afirmo que existam nesta versão.
- **Hooks do Codex em detalhe** (eventos, bloqueio) — a feature está ativa (`hooks=true`), mas a
  semântica não foi verificada; irrelevante para a Estratégia A.
- **Hooks do Kimi em escopo de projeto** — a doc só mostra `~/.kimi-code/config.toml`; se hook de
  bloqueio por projeto existir, muda a decisão 4b. Fica para o card do `T-019`/port Kimi.
- **Doc oficial do AGENTS.md no Kimi** — a página "context" é 404; a evidência é forte (template
  de system prompt no binário injeta `{{ KIMI_AGENTS_MD }}`), mas é engenharia reversa, não doc.
- **Equivalentes de `${CLAUDE_PLUGIN_ROOT}` e statusline** nos dois hosts — sem doc encontrada;
  marcados como suposição de ausência na matriz.

## ⏭️ RETOMAR AQUI

**O plano está pronto e nada foi implementado.** Próxima ação: o **Manager leva as 6 decisões ao
dono**. Com "1a, 2ii, 3 portatil/, 4a, 5 sim, 6 sim" (as recomendações), o card vai a READY e o
implementer executa os passos 1–8 — os passos 1–3 são o núcleo; o 4 depende da decisão 5. Sem
resposta, o card vira `[!]` com a pergunta exata: "responda as decisões 1–6 da thread
T-026-host-alternativo". A matriz de paridade acima é reutilizável pelo `T-021` e pelo `T-020`
(convenções de invocação CLI já vivem no `_elenco.md`).
