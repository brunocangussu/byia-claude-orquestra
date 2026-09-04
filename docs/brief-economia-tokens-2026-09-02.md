# Brief para o Manager do Orquestra — economia de tokens (medida, não estimada)

**Versão do brief:** 4 — revisado contra o Orquestra **0.25.0** (`cb9e729`); proposta 5 substituída pela decisão do dono de MANTER e ajustar o claude-mem.
**Origem:** análise externa dos transcripts locais de agosto/2026 — `~/.claude/projects/*/*.jsonl` (13.639 chamadas à API do Claude, deduplicadas por `message.id`) e `~/.codex/sessions` + `archived_sessions` (563 rollouts, 58.363 chamadas deduplicadas por `turn_id` + índice da chamada, porque fork e retomada regravam o histórico do pai). O percentual do limite semanal do Codex vem do campo `rate_limits` que o próprio Codex grava em cada chamada.

**Pedido do dono:** isto é insumo para cards. Nada foi editado. Cada achado tem número e arquivo de origem; onde é estimativa, está dito.

---

## POR ONDE COMEÇAR — leia isto primeiro

Se for criar só três cards, são estes. Eles se reforçam e cobrem as duas causas dominantes (tamanho do contexto no Claude, número de chamadas no Codex) mais o multiplicador comum aos dois:

| Prioridade | Proposta | Por que primeiro | Esforço |
|---|---|---|---|
| **1º** | **12 — card com teto de 200 chars**, começando pelos 6 maiores | É o único que o dono pode fazer **hoje, sem tocar em código**. 97% do board é nota livre; 45% do ganho está em 6 cards, cinco deles em `[?]` VALIDATE. Derruba o piso pós-compactação nos dois hosts | ~30 min de edição de dados |
| **2º** | **8 — pós-compactação injeta estado, não ordem de releitura** | É onde fluidez e economia são a mesma correção. Hoje cada compactação puxa ~70k de memória de volta antes de o trabalho recomeçar — é isto que faz a janela de 258k *parecer* curta | 1 função no `context-guard.py` + texto |
| **3º** | **7 — guardião com parser do Claude Code e faixas absolutas** | Sem ele, a disciplina do Orquestra simplesmente não existe no Claude Code — nem para avisar. A 0.25.0 não tocou nisso | 1 parser novo + faixas em tokens |

**Ordem importa:** o 12 antes do 8, porque o 8 rende mais com a memória já enxuta; e o 12 antes de baixar qualquer teto de janela (`/autocompact`), porque baixar teto com piso alto devolve exatamente a sensação de janela curta.

**Fora do ciclo, decisão direta do dono (não precisa de card):** `/autocompact 400k` no Claude, `/effort high`, e o ajuste de configuração do claude-mem (proposta 5). Ver Nível 0.

**Duas decisões que só o dono resolve** (não roteie sozinho): se o superpowers sai do Codex ou se o `orq` declara que a Matriz vence qualquer skill de spawn (proposta 10); e qual camada de compressão e qual grafo de código ficam (propostas 18–19).

---

## 0. O que a 0.25.0 já resolveu — e o que ela não tocou

Diff verificado: `08cb879` (0.24.0) → `cb9e729` (HEAD).

### Resolveu (e é bom)
- **Guardião virou consultivo.** Saíram todos os `decision: block`; o guardião não bloqueia mais prompt, ferramenta, `Stop`, compactação nem o modo Goal. Nova frase de handshake no Codex: **"Checkpoint verificado; conversa continua."** — a compactação passou a ser sempre livre e a mesma conversa segue. Rearme consultivo após +10 pontos percentuais (`CHECKPOINT_REARM_DELTA`). **Isto responde diretamente à queixa de fluidez.**
- **Supermemory saiu de vez.** Passo 4 do `checkpoint.md` removido, `sm-search.py` e `lembrar.md` deletados, catálogo do `stack.md` limpo. Cada checkpoint deixou de fazer uma chamada MCP externa.
- **claude-mem rebaixado — e isso agora precisa ser REVERTIDO.** A 0.25.0 tirou o claude-mem da lista de ferramentas da `SKILL.md` (virou "wiki do projeto + memória local/confiável realmente disponível no host") e no `stack.md` o marcou como "opcional; não propor no Codex". Com a decisão do dono de **mantê-lo nos dois hosts** (proposta 5), esses dois textos ficaram desalinhados e precisam voltar — com o papel correto: complemento da wiki, não substituto.
- `/orq:lembrar` agora consulta a wiki primeiro e só usa busca do host se ela não estiver como Dispensada no `_stack.md`.

### Não tocou (as propostas continuam válidas)
- **O parser continua só do Codex.** `read_latest_usage()` ainda exige `payload.type == "token_count"` + `info.last_token_usage` + `info.model_context_window` — formato do rollout do Codex. No transcript do Claude Code isso não existe: o snapshot volta `None` e o hook sai em silêncio. **No Claude Code o guardião nunca rodou e continua não rodando** — nem para avisar. → proposta **7**.
- **As faixas continuam em % da janela** (55/60/70). Com 1M isso é 550k/600k/700k — muito além do ponto em que cada chamada já custa caro. → proposta **7**.
- **A ordem de releitura pós-compactação continua** — e agora dispara em mais lugares: além do `SessionStart(compact)`, também em `UserPromptSubmit` e `PostToolUse` enquanto `recovery_required` estiver ligado. O texto é "Releia memory/MEMORY.md, memory/wiki/KANBAN.md e a thread ativa; registre um checkpoint de recuperação no próximo ponto seguro". Não bloqueia mais, mas continua puxando a memória inteira para dentro da janela. → proposta **8**, que segue sendo a de maior ganho no Codex.
- **Efeito líquido da 0.25.0 em tokens: neutro.** Ela melhorou a fluidez tirando os bloqueios — mas os bloqueios eram justamente o que segurava o crescimento do contexto. O que economiza (parser do Claude, faixas absolutas, estado em vez de releitura, memória enxuta) ainda não veio.
- **Custo novo, pequeno:** `/orq:auditar` + `audit-adoption.py` + `audit-removal.py` + `verify_installed_cache.py` + 724 linhas no `lint-coerencia.py`. São offline e sob demanda, mas o comando entra na listagem de skills de toda sessão.

---

## 1. Sobre a fluidez e a autocompactação — o dado que muda a conversa

**Sim, o Claude Code tem autocompactação.** O motivo de você nunca ter visto:

- Medido: **78 sessões de Claude Code desde 01/08; apenas 1 teve compactação.**
- Contexto máximo por sessão: **p50 450k · p75 668k · p90 840k · máximo 940k.** 51 sessões passaram de 200k, 31 de 500k, 3 de 900k.
- `autoCompactWindow` está `null` no `settings.json`, e o modelo tem janela de 1M (no Max, Opus 1M é incluído). Sem janela configurada, o Claude Code compacta **perto do limite do modelo** — ou seja, perto de 1M. Suas sessões morrem por `/clear` antes de chegar lá. A autocompactação existe; o gatilho está longe demais para você vê-la.

**E aqui está o ponto que reorganiza o problema:**

> **O inimigo da fluidez não é a compactação. É a releitura obrigatória depois dela.**

No Codex, cada compactação dispara a ordem do guardião: releia `MEMORY.md` + `KANBAN.md` + thread ativa e registre um checkpoint de recuperação. Com o board em 28k, o `MEMORY.md` em 4k e uma thread em 40k, isso são ~70k tokens e várias chamadas **antes de voltar ao trabalho** — e metade dos ciclos entre compactações tem ≤ 23 chamadas. É por isso que a janela de 258k *parece* curta: ela não é curta, ela é consumida por releitura. Piso medido logo após compactar: 48k (mediana), 62k (p75) — e sobe para 70–90k depois da releitura.

Corolário para o card: **quanto mais enxuta a memória, mais baixo o teto pode ser sem perder fluidez.** Board de 4k + thread de 10k em vez de 28k + 40k derruba o piso pós-compactação de ~70k para ~20k — o que devolve 50k de janela útil a cada ciclo, nos dois hosts.

### Recomendação de teto para o Claude Code (simulação sobre as 13.639 chamadas reais)

| `/autocompact` | chamadas acima do teto | economia de contexto | leitura prática |
|---|---|---|---|
| 600k | 14% | −4% | quase nada muda |
| **500k** | 27% | **−10%** | conservador; mal se percebe |
| **400k** | 42% | **−19%** | **ponto de equilíbrio sugerido** — o dobro do padrão de 200k |
| 300k | 59% | −32% | bom, se a memória já estiver enxuta |
| 200k | 79% | −51% | padrão do produto; hoje seria apertado pelo piso alto |
| 150k | 89% | −62% | só depois das propostas 12–15 |

Sugestão: **começar em 400k**, fazer as propostas 8 e 12–15, e então descer para 300k. Descer direto para 200k hoje traria de volta exatamente a sensação de janela curta — pelo motivo errado (piso alto), não pelo teto.

---

## 2. Diagnóstico em uma linha por host

- **Claude Code:** custo = tamanho da sessão. Contexto médio **379k por chamada** (mediana 353k); 61% do custo ponderado é reler o histórico; 83% do cache write são ~420 regravações completas, 298 delas após pausa > 1 h (a vida do cache no plano é 1 h). Sem guardião neste host e sem teto de compactação.
- **Codex:** custo = número de chamadas × piso por chamada. Compactação funciona (pico mediano 217k, janela 258k), mas são **5.100–7.300 chamadas/dia** (76 por mensagem do dono), contexto médio 141k, e o limite semanal foi de **0% → 55% em 45 h** (31/08 01h → 01/09 21h).
- **Memória/wiki (a hipótese do colega):** leituras diretas são ~3,5% dos resultados de ferramenta no Claude — mas entram como **multiplicador**: no Claude, o que é lido fica na janela e é relido em cada chamada seguinte; no Codex, é relido inteiro a cada compactação por ordem do hook. O colega está certo no diagnóstico do formato, não no peso direto.

---

## 3. Achados com evidência

### A. Codex — o Manager faz polling dos sub-agentes
- Turno "pode iniciar o T-002" (bruno-brain, 20/08): **1.433 chamadas, 194 M tokens, 6 compactações**. Dessas, **601 chamadas não produziram nada** (nenhuma ferramenta, nenhuma mensagem; saída alternando 31 e 46 tokens) e 352 só raciocínio. Dois terços do turno foi o Manager perguntando "já terminou?" a ~180k tokens por pergunta enquanto `t002_task4` trabalhava.
- Mesma assinatura: Agente Pessoal 31/08 10h (1.502 chamadas, 213 M) e bruno-brain 31/08 22h (1.389 chamadas, 199 M, atravessou a madrugada).
- Composição das 8,2 B de entrada do Codex: 50% sessão principal sem sub-agente · **30% turnos do Manager com sub-agentes** · 18% trabalho dos próprios sub-agentes · ~4% revisor externo via `codex exec`.

### B. Codex — sub-agente por tarefa, revisor por rodada, forks, sem teto
- 256 threads de sub-agente desde 01/08. Nomes (`agent_path`): por tarefa do plano há `writer`, `impl`, `review`, `rereview1`, `rereview2`, `rereview3` — o padrão *subagent-driven-development* do superpowers, instalado também no Codex (`hooks.state."superpowers@claude-plugins-official:hooks/hooks-codex.json"`). A maioria dos revisores é **fork** do pai (herda 150–200k de histórico que não usa).
- Um único `t002_task0_writer`: 147 chamadas, 16 M tokens, de 29k a 197k de contexto.
- Revisor externo: 111 sessões, 331 M; o card T-152 chegou à **rodada 29**, com três disparos na mesma rodada (12:51 e 13:49 de 01/09).
- **Contradiz o plugin, inclusive na 0.25.0:** `implement-next.md` e a Matriz de invocação dizem "Host Codex: `codex exec` é obrigatório; primitiva nativa só quando `_elenco.md` registrar override comprovado por chamada real"; `revisar.md` diz "máximo 2 rodadas; persistindo, escale pro dono". O `_elenco.md` do bruno-brain diz "subagente nativo quando houver override comprovado" e nunca registra a comprovação. Na prática o Manager segue a skill do superpowers, não a Matriz.

### C. Codex — cada compactação dispara releitura completa da memória
- 477 compactações no mês; **372 ordens** do `context-guard.py` com o texto de releitura. Na 0.25.0 a ordem deixou de bloquear, mas passou a disparar também em `UserPromptSubmit` e `PostToolUse` durante `recovery_required`.
- Piso após compactar: 48k (mediana; p75 62k); após a releitura, 70–90k. As 30 chamadas seguintes a cada compactação somam **7.858 chamadas e 678 M tokens desde 27/08** (~15% do período). Metade dos ciclos entre compactações tem ≤ 23 chamadas.

### D. Codex — piso alto em toda chamada
- `~/.codex/AGENTS.md`: 20 KB (~5,5k tokens), em toda sessão e todo sub-agente. `AGENTS.md` de projeto: 11–14 KB (New ByIA, Gestão Dados Marketing).
- `config.toml` declara **14 servidores MCP** (code-review-graph, context7, node_repl, plaud, playwright, serena, railway, codebase-memory-mcp, computer-use, pipeboard ×2, supabase, cua_repl, meta-ads). O Codex não difere schemas: todos entram em toda chamada.
- Primeira chamada de sessão nova: 33k (mediana) antes de qualquer trabalho. Saídas de ferramenta de 100k–316k tokens truncadas no meio do turno (seis avisos num só turno).

### E. Claude Code — sessões sem freio nenhum
- Simulação sobre as 13.639 chamadas reais na tabela da seção 1. As 8 sessões mais pesadas acumularam 206–297 M cada.
- Guardião não roda neste host (achado 0) e `autoCompactWindow` não está configurado.
- `~/.claude/settings.json`: `effortLevel: xhigh` + `alwaysThinkingEnabled: true` — 15 M tokens de saída no mês (9% do custo ponderado). Padrão do Opus 5 é `high`.
- Baseline de 66–107k tokens já na 1ª chamada: listagem de 116 skills (8,3k tok), `using-superpowers` inteira (4,8k), skill `orq` 26 KB (7,3k quando dispara), instruções de 6 MCPs globais + Remote Control (3,1k), claude-mem 50 obs + 10 sessões (2,6k), CLAUDE.md global 8,7 KB + projeto 5,1 KB (3,8k), 633 ferramentas deferidas. Baseline × 13.639 chamadas ≈ 1,1 B = 21% do contexto do mês.

### F. Memória do Orquestra — o formato, não o volume
- `wiki/KANBAN.md` do repo do plugin: 103 KB ≈ 28k tokens; 48 cards com **média de 2.075 chars por linha**, o maior com 12.257. Lido 34× no mês e relido duas vezes por checkpoint.
- `MEMORY.md`: 14 KB ≈ 4k — índice que virou narrativa ("Trabalho mais recente", "Trabalho anterior", blocos de 13/08 ainda vivos). O do bruno-brain tem "Estado atual" de ~40 linhas.
- `threads/T-026-host-alternativo.md`: 142 KB ≈ 40k, com RETOMAR AQUI superados mantidos. `fixes-history.md`: 79 KB, lido com `cat` (396 `cat memory/` no mês).
- Total de `memory/`: 1,25 MB ≈ 350k tokens. A regra "~150 linhas por página" está no `checkpoint.md`; nada a faz valer.

### G. Ferramental empilhado (ambos os hosts)
- Compressão de saída: rtk (hook em todo Bash) + context-mode (plugin + hooks) + caveman (`full`). Conhecimento de código: codebase-memory-mcp (+ hooks `cbm-*` que bloqueiam Grep/Glob) + serena + code-review-graph + graphify + cartographer. Memória: claude-mem (observer Haiku em todo tool use, injeção no SessionStart, hook em todo Read) + a wiki. Screenshots: 160 no mês (~20 M chars) presas no contexto.

---

## 4. Propostas — para virar cards (ordem = ganho ÷ esforço)

### Nível 0 — configuração do dono (fora do plugin; hoje)
1. Claude: **`/autocompact 400k`** agora; **300k** depois das propostas 8 e 12–15. Ver tabela da seção 1. **−19% a −32% de contexto, mantendo fluidez.**
2. Claude: checkpoint + `/clear` antes de fechar o dia; nunca retomar sessão > 150k na manhã seguinte (cache vive 1 h). **−80% cache write.**
3. Claude: `/effort high`; remover `"effortLevel": "xhigh"` do settings global; `xhigh` só por sessão. **−20–40% saída.**
4. Ambos: MCPs por projeto (Claude: composio/magic/plaud/railway fora da sessão de código; Codex: 14 → 2–3, marketing só via `.codex/config.toml` do projeto). `remoteControlAtStartup: false`. **−10–20k por chamada.**
5. **claude-mem: MANTER nos dois hosts e ajustar o que ele injeta** (decisão do dono, 02/09).
    **O custo é desprezível — medido:** a injeção no `SessionStart` custa ~2,3k tokens por sessão e, presente em todas as chamadas daquela sessão, soma ~31 M de 5,22 B no mês = **0,60% do contexto**. Os hooks `PreToolUse` dispararam 36× no mês inteiro (1,5k chars cada). O custo de escrita (123 sessões de observador, ~1,1 M de saída em Haiku) roda fora do contexto do dono. **Desligar não é onde está a economia** — a proposta anterior de excluir projetos foi retirada.
    **O problema não é custo, é sinal.** Em agosto, no projeto do Orquestra: 546 `discovery` + 382 `change` = **79% das observações são narração de sessão** ("215 tests green", "fix verification passed", "final gate status"). Contra 81 `decision`, 81 `bugfix`, 7 `security_alert`, 1 `gotcha`. O `_schema.md` do próprio Orquestra classifica o primeiro grupo como **derivável** e manda não guardar.
    **Fiação que nunca existiu:** a `SKILL.md` da 0.24 descrevia claude-mem como "(automático)" — o que diz ao agente que não precisa fazer nada — e o gatilho "lembra quando" ia para `/orq:lembrar`, que consultava **Supermemory**, nunca a busca do claude-mem. Resultado medido: 3 chamadas às ferramentas MCP do claude-mem em 79 sessões no mês, e zero invocações da skill `mem-search`. A 0.25.0 removeu `/orq:lembrar` e tirou o claude-mem da lista de ferramentas da `SKILL.md` — o que agora está **desalinhado com a decisão de mantê-lo**.
    **Cobertura hoje é pela metade:** não está instalado no Codex (marketplace `thedotmack` ausente de `~/.codex/plugins/`). `bruno-brain` tem 11.777 chamadas no Codex e **zero** observações. O plugin traz `hooks/codex-hooks.json` (SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, Stop) e `.codex-plugin/plugin.json` — instalar é viável, e o custo por hook medido no Claude é baixo.
    **Divisão de trabalho a adotar** (é o que torna os dois complementares em vez de redundantes):
    - **wiki/checkpoint** = o *porquê* e as *consequências*, escrita deliberada no fim do bloco. Continua sendo a fonte da verdade.
    - **claude-mem** = rede de segurança para o que **não** chegou ao checkpoint: gotcha operacional de meio de sessão, decisão tomada e não registrada, sessão que morreu sem checkpoint.
    **Configuração alvo (mesma nos dois hosts):** `CLAUDE_MEM_CONTEXT_OBSERVATION_TYPES=decision,bugfix,gotcha,security_alert,security_note` · `CLAUDE_MEM_CONTEXT_OBSERVATIONS=25` · `CLAUDE_MEM_CONTEXT_SESSION_COUNT=5` · `CLAUDE_MEM_EXCLUDED_PROJECTS` vazio. Injeção cai de ~2,3k para ~0,6k tokens **e passa a carregar sinal em vez de diário**.

6. `~/.codex/AGENTS.md` 20 KB → ≤ 3 KB; `~/.claude/CLAUDE.md` 8,7 KB → ≤ 3 KB (regra de projeto vai para o projeto; procedimento vai para skill).

### Nível 1 — o plugin (cards do Orquestra)
7. **Guardião que funcione no Claude Code, com faixas absolutas.** `read_latest_usage()` ganha um segundo parser: no transcript do Claude, o contexto atual é `input_tokens + cache_creation_input_tokens + cache_read_input_tokens` do último `message.usage` de assistente. Faixas em **tokens absolutos** (ex.: 110k pré-alerta · 140k checkpoint · 170k reforço), não em % da janela — o custo por chamada é linear no tamanho, não na fração. Manter o parser e as faixas do Codex. **Sem isso, a disciplina do Orquestra simplesmente não existe no Claude Code.**
8. **Pós-compactação injeta estado, não ordem de releitura.** Em `_session_context` (ramo `compact`) e nos ramos `recovery_required` de `UserPromptSubmit`/`PostToolUse`, trocar "releia MEMORY, KANBAN e a thread; registre checkpoint de recuperação" por **3 linhas geradas**: saída do `kanban-status.sh` + card ativo + `⏭️ RETOMAR AQUI` da thread. O resumo da compactação já preserva o resto. Checkpoint de recuperação só a pedido do dono. **É a proposta que devolve fluidez E economiza: −10–15% da entrada do Codex e piso pós-compactação de ~70k para ~20k.**
9. **Host Codex obedece a Matriz: `codex exec`, sem sub-agente nativo, sem fork.** Criar o simétrico do `run-opus-reviewer.py` para o writer — `run-codex-writer.py`: worktree + `codex exec -s workspace-write -m <faixa> -c model_reasoning_effort=<effort>` + handoff com teto (40 linhas, formato fixo: objetivo · decisões · o que falta · próxima ação) + timeout. Manager bloqueado no subprocesso, **zero chamadas enquanto espera**. Sub-agente por **card**, não por tarefa. **−20–30% das chamadas do Codex.**
10. **Superpowers fora do fluxo do Orquestra.** `subagent-driven-development` e `using-superpowers` não podem sobrepor a Matriz: ou desinstala o superpowers no Codex, ou o `orq` declara explicitamente que a Matriz vence qualquer skill de spawn. Hoje as duas instruções coexistem e a mais agressiva ganha. **Decisão do dono.**
11. **Teto de rodadas de revisão, aplicado.** `revisar.md` já diz 2 rodadas; falta enforcement: contador na nota do card (`revisões: N`), e na terceira sem convergir o card vai para `[!]` com os bloqueadores listados. Uma rodada = um disparo (lotes só se o briefing > 16 KiB, e registrados).
12. **Card = uma linha com teto.** `_schema.md`: card ≤ 200 chars (título + estado + `→ threads/T-NNN.md`); decisões, rodadas e citações vão para a thread. `kanban-status.sh`/`wiki-lint` acusam card acima do teto como `⚠`.
    **Medição do board atual (52 cards ativos):** corpo total 99.301 chars ≈ **27,6k tokens**, dos quais os títulos são **2.320 chars (0,6k tokens)** e a nota livre é **96.825 chars — 97% do board**. 48 dos 52 cards passam de 200 chars. Com o teto: 27,6k → **2,9k tokens, redução de 90%**.
    **Onde está concentrado:** os 6 maiores cards somam 44.833 chars (45% do board) — `T-026` 12.243 · `T-036` 8.906 · `T-051` 8.085 · `T-052` 5.928 · `T-053` 5.061 · `T-020` 4.610. **Cinco dos seis estão em `[?]` VALIDATE** — o estado em que a única coisa que importa é *como o dono testa*; a nota carrega o histórico inteiro da implementação. É exatamente o caso que o colega do dono descreveu.
    Só 9 dos 52 cards citam uma thread; nesses, a nota é duplicação do que já está na thread. **Migração sugerida:** começar pelos 6 maiores (45% do ganho em 6 edições), movendo a nota para `threads/T-NNN.md` e deixando no card título + estado + ponteiro + como validar.
    **−24,7k por leitura do board, e derruba o piso pós-compactação nos dois hosts.**
13. **`MEMORY.md` só índice, ≤ 60 linhas.** "Trabalho mais recente" = 5 linhas (versão · último checkpoint · thread ativa · próxima ação · espera o dono). O resto é log ou snapshot.
14. **Thread ≤ ~150 linhas e um único RETOMAR AQUI.** Checkpoint apaga os superados; acima do teto, sintetiza na página de tópico e move para `_concluidas/`. `T-026` (142 KB) é o caso-teste. Lint verifica.
15. **Leitura parcial por padrão.** `/orq:quadro` roda `kanban-status.sh` e mostra só ⏸️ e 🟡; checkpoint edita linhas (Edit/sed) em vez de reler o board duas vezes; `fixes-history.md` só com `head -n 40`; SessionStart após `/clear` injeta as 3 linhas da proposta 8.
16. **Worker devolve resumo, não transcrição.** Handoff com teto; o Manager não lê o output-file inteiro, só quando contesta um achado. (No Claude, as `task-notification` de teammates estão em 6–10k chars cada.)
17. **Escala de cerimônia aplicada.** Card `Pequeno` = 1 writer + 1 revisão `--rapido`, sem planner separado, sem docs separado. Hoje tudo roda como `Alto risco`.

### Nível 2 — consolidar ferramental (decisão do dono)
18. Uma camada de compressão (context-mode **ou** rtk); caveman só se gostar do estilo.
19. Um grafo de código por host (serena **ou** codebase-memory-mcp); graphify e cartographer como skill sob demanda; hooks `cbm-*` saem junto com o MCP.
20. Memória: **wiki + claude-mem, com papéis distintos** (ver proposta 5) — a wiki guarda o porquê e as consequências; o claude-mem é a rede de segurança do que não chegou ao checkpoint. Não somar uma terceira camada. Headroom **não** (proxy quebra o prompt cache e intermedia a assinatura). Ferramenta de memória externa não reduz chamadas nem piso — ganho realista 5–10%; memória boa é índice curto + busca que devolve trecho (bruno-brain `brain_search` → `brain_get` é o desenho certo).
21. Screenshots só quando o visual é o ponto; `get_page_text`/`read_page` por padrão.

---

## 5. Estimativa combinada (simulação sobre chamadas reais; medir com `/usage` uma semana depois)
- Claude Code: **−45–60% tokens de contexto, −20–30% de saída** (itens 1–3, 7, 12–15).
- Codex: **−40–55% de entrada** (itens 4, 6, 8, 9, 11, 17) — o grosso vem de parar o polling e a releitura pós-compactação.
- Em horas de desenvolvimento por janela de limite: algo entre 2× e 2,5× em cada host, **com mais fluidez, não menos** — porque o que devolve fluidez (proposta 8 + memória enxuta) é o mesmo que economiza.

## 6. O que NÃO fazer
- Instalar mais uma camada de compressão ou mais um grafo: cada uma adiciona baseline, hooks e instruções, e nenhuma reduz chamadas ou tamanho de sessão.
- Baixar o teto de compactação (Codex ou `/autocompact` no Claude) **antes** da proposta 8: mais compactações com a ordem de releitura ativa = mais releitura, e é exatamente aí que nasce a sensação de janela curta.
- Recolocar bloqueios no guardião: a 0.25.0 fez certo em torná-lo consultivo. O freio deve vir de teto de janela e memória enxuta, não de bloqueio de prompt.

## 7. Ressalvas de método
- Chars → tokens em português ≈ 3,6 chars/token (estimativa). Ponderação de custo do Claude pela tabela pública do Opus (cache read 0,1×, cache write 1,25×, saída 5×); a fórmula exata dos limites do Max não é publicada, mas a doc confirma que histórico relido e cache miss contam, e que `/usage` os sinaliza.
- Codex: vida do cache e contagem de cached tokens no limite do Pro não são públicas; o que é medido é o `used_percent` gravado pelo próprio Codex.
- "Chamadas vazias" = ≤ 80 tokens de saída e nenhum item visível entre duas chamadas no rollout; 2.262 no mês (270 M), concentradas nos turnos com sub-agente.
- A coluna "economia de contexto" das tabelas é recorte do contexto no teto sobre as chamadas reais — não considera o ganho adicional de cache write nem o custo das compactações extras.
- Nenhum conteúdo de conversa foi lido além de tamanhos, nomes de ferramentas, cabeçalhos de hooks e primeiras linhas de prompts de sub-agente.

---

## 8. Referências oficiais citadas
- `code.claude.com/docs/en/model-config` — `/autocompact`, `autoCompactWindow`, `CLAUDE_CODE_AUTO_COMPACT_WINDOW`, `CLAUDE_CODE_DISABLE_1M_CONTEXT`, effort levels e defaults por modelo.
- `code.claude.com/docs/en/costs` — por que o uso sobe em sessão longa, vida do cache (1 h na assinatura), custo de agent teams, thinking cobrado como saída.
- `platform.claude.com/docs/en/build-with-claude/effort` — o que muda entre `high`, `xhigh` e `max`.
