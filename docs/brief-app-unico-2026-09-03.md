# Brief para o dono do Orquestra — um app só para Claude Max + Codex Max

**Data:** 2026-09-03 · **Orquestra de referência:** `0.26.0` (working tree em `byia-claude-orquestra`)
**Pedido:** parar de alternar entre o Claude Code e o app do Codex; trabalhar num app só, com as duas assinaturas, várias threads do mesmo projeto e, se possível, uma sessão que roteie entre os dois vendors.
**Regra deste brief:** análise + recomendação. **Nada em `orq/` foi editado.** O que virar mudança está listado como card na seção 4, com esforço e risco declarados. Toda afirmação sobre ferramenta externa foi verificada em 2026-09-03 na fonte oficial (lista no fim); onde não deu para verificar, está dito.

---

## Resposta curta

1. **O "app único" existe e é gratuito — o que ele NÃO pode ser é um app que fale com os modelos por você.** As duas assinaturas só valem dentro dos binários dos próprios vendors (`claude` e `codex`). Portanto o app certo é um **hospedeiro de terminais/threads** que abre o Claude Code e o Codex de verdade, lado a lado, cada um logado na própria assinatura. Candidatos que fazem exatamente isso hoje: **Orca** (o que você baixou), **Superset**, **Conductor**, **Zed** e **VS Code com as duas extensões oficiais**. Cursor não serve para isso (o painel de agentes dele só roda o harness do Cursor); Warp serve como terminal melhorado, mas sem worktree por thread.

2. **"Uma sessão que roteia entre os dois" já existe de forma oficial — só numa direção.** A OpenAI publicou o **`codex-plugin-cc`** (plugin oficial do Codex *para dentro do Claude Code*, ~32k estrelas): `/codex:review`, `/codex:adversarial-review`, `/codex:rescue --model … --effort …`, `/codex:transfer`, jobs em background. Ele usa o seu login ChatGPT e o app-server do Codex — sem `codex exec` cru por Bash (que é o que a Matriz do Orquestra manda hoje e a sua regra global proíbe: `T-067`). Na direção inversa (Codex chamando o Opus), continua sendo `claude -p` — tolerado pela Anthropic hoje, mas com uma mudança de cobrança **anunciada e pausada** (detalhe na seção 1).

3. **O que você chamou de "perfeito" — uma sessão só, roteando, com várias threads por projeto — se resolve combinando os dois pontos acima, e o Orquestra já está quase pronto para isso.** Cada thread do app é uma *frente* do Orquestra; a **trilha** do card decide em qual host a thread abre (`interface` → Claude, `sistema` → Codex); dentro da thread, o Manager alcança o outro vendor pelos mecanismos sancionados. O que falta no Orquestra são **quatro ajustes** (seção 4), e o mais importante deles é estrutural: **o board (`memory/`) é versionado no git, e app que abre uma frente por worktree vai bifurcar o board** — isso precisa ser decidido antes de adotar qualquer um desses apps.

---

## 1. A restrição que decide tudo: onde cada assinatura pode ser usada

| | Claude Max (Anthropic) | ChatGPT Pro/Max (OpenAI) |
|---|---|---|
| Uso interativo no binário oficial (`claude`, extensão VS Code, app Claude) | ✅ coberto pela assinatura | — |
| `claude -p` / Agent SDK / apps de terceiros via SDK (Zed, Conductor, ACP) | ✅ **hoje** desconta dos limites do plano. Anthropic anunciou em 13/mai que a partir de 15/jun isso passaria a um pote separado de "créditos Agent SDK" (**US$ 200/mês no Max 20x**, cobrado a preço de API) — e **pausou a mudança em 15/jun, sem nova data**. | — |
| OAuth da assinatura replicado por harness de terceiro (OpenCode antigo, Pi) | ⛔ proibido pela Anthropic (bloqueio jan/2026; texto legal fev/2026; enforcement abr/2026) | — |
| `codex` CLI, `codex exec`, Codex SDK, app-server, plugin para Claude Code | — | ✅ a página oficial de preços lista "Codex SDK, `codex exec` e workflows scriptáveis" como **incluídos** no Plus/Pro. A OpenAI nomeia OpenCode, pi e OpenClaw como clientes bem-vindos. |
| Proxies/pools de conta (sub2api) | ⛔ | ⛔ (OpenAI trata como fraude) |
| Modelo do outro vendor como *subagente nativo* | ⛔ subagente do Claude Code só aceita modelo Claude (doc: "para envolver outra ferramenta, exponha-a como MCP") | ⛔ `model_providers` custom do Codex só autentica por **API key** — nunca pela assinatura Claude |

**Leitura prática:** o app hospedeiro precisa rodar os CLIs **de verdade** (PTY), não "falar Claude" por conta própria. Apps que fazem isso são imunes às duas políticas. Apps que usam o Claude pela via SDK/ACP (Zed, Conductor, painel de agentes do VS Code) funcionam hoje, mas são os que ficam expostos se a Anthropic despausar a cobrança separada. **Isto também vale para o `run-opus-reviewer.py` do Orquestra**, que é `claude -p` — ver card C4.

Um detalhe de doc que vira gotcha: a Anthropic diz que `--bare` (modo que **nunca lê credencial OAuth**, só API key) "vai se tornar o padrão do `-p` numa versão futura". Quando isso acontecer, o runner do Opus no host Codex para de autenticar pela assinatura em silêncio — exatamente o tipo de falha que o Orquestra odeia.

---

## 2. Comparativo dos apps (Mac, as duas assinaturas, mesmo repo, threads paralelas)

| App | Claude Code + Codex na mesma janela, com as assinaturas? | Thread = worktree? | Como fala com o Claude | Custo | O que pesa contra |
|---|---|---|---|---|---|
| **Orca** (Stably, MIT) | ✅ os dois CLIs reais em PTY; lê `~/.claude` e `~/.codex`; troca de conta a quente; **medidor de uso 5h/dia/semana das duas assinaturas** na barra | ✅ nativo: task = worktree + terminal do agente + browser; N agentes por task; subagentes/teams do Claude aparecem como filhos | PTY (seguro) | grátis | (a) lança os CLIs com `--dangerously-skip-permissions`/`--yolo` **por padrão** (há modo *Manual* nas configurações); (b) **issue #9963 aberta desde 22/jul sem resposta**: instala hooks em configs de outros agentes, duplica tokens OAuth para pasta própria, daemon escutando em `0.0.0.0`, telemetria ligada por padrão; (c) release diária (v1.4.195 em 02/set), 400–800 MB ocioso |
| **Superset** (ELv2, ~12k★) | ✅ "qualquer agente com a sua assinatura"; lança os CLIs; não intermedeia chamadas de modelo | ✅ worktree por task; dashboard de status; CLI | PTY (seguro) | grátis local; Pro US$ 15 (remoto/mobile/Linear) | menos recursos que o Orca (sem medidor das duas assinaturas, sem troca de conta); Win/Linux não testados |
| **Conductor** (Melty, fechado) | ✅ Claude via token já na máquina (Pro/Max); Codex via login do CLI | ✅ worktree por workspace | **SDK** (exposto à política pausada; a Conductor foi citada nominalmente pela Anthropic em 13/mai) | grátis local; Pro US$ 50 (cloud) | código fechado; UI nativa (não é o Claude Code "cru" — plugin, hooks e statusline do Orquestra precisam ser testados lá) |
| **Zed 1.0 + ACP** | ✅ "Claude Agent" e "Codex" como threads paralelas na sidebar, cada uma com o próprio login | ✅ seletor de worktree por thread | **ACP/SDK** (mesma exposição; Zed também citado em 13/mai; fallback deles: rodar o `claude` num *terminal thread*) | grátis | sem PTY: sem TUI do Claude Code; thread do Codex não retoma histórico; sem checkpoints/rollback; a Zed nomeia essas lacunas |
| **VS Code + extensão Claude Code + extensão Codex** | ✅ as duas extensões oficiais convivem; login por assinatura nas duas; nenhuma dependência do Copilot | parcial: a extensão Claude cria sessão em worktree; a do Codex, não por thread | PTY/nativo (seguro) | grátis | dois painéis laterais, sem lista unificada de threads — é "um app", não "uma tela". Você já testou e não ficou. |
| **VS Code — painel "Agents" (agent host)** | parcial: harness Codex aceita login ChatGPT; harness Claude aceita `CLAUDE_CODE_OAUTH_TOKEN` (`claude setup-token`) | ✅ checkbox "New Worktree" por sessão (com *Bypass Approvals* automático) | **SDK** (exposto) | grátis, exige login GitHub | risco documentado de cobrança errada via Copilot (issue #314952, ~US$ 300); worktree liga bypass sozinho |
| **Warp** (AGPL desde abr/2026) | ✅ os dois CLIs em abas/painéis, com input rico, notificação "agente precisa de você", painel de gestão de agentes, code review | ❌ worktree manual (`git worktree add`) + "Tab Configs" | PTY (seguro) | grátis para esse uso | o agente próprio do Warp só aceita **API key** (não a assinatura); sem editor; worktree por thread é trabalho seu |
| **Cursor 3** | ❌ o Agents Window só roda o harness do Cursor (staff no fórum, jun/2026: assinatura Claude não serve; "use a extensão Claude Code dentro do Cursor") | ✅ (só para agentes do Cursor) | — | Pro US$ 20+ | paga um IDE para acabar usando as mesmas duas extensões do VS Code |
| **App do Codex / app do Claude** | ❌ cada um roda só o próprio vendor; nenhuma notícia de integração cruzada em 2026 | ✅ nos dois | — | incluso | é o status quo que você quer deixar |
| Vibe Kanban · Crystal · CodeLayer | ⚠️ empresa do Vibe Kanban fechou (abr/2026); Crystal virou Nimbalyst; CodeLayer Pro custa US$ 100/usuário | | | | não recomendados |

**Veredito por perfil de risco:**

- **Mais completo para o seu desenho:** **Orca** — é o único com medidor das duas assinaturas e troca de conta a quente, e o modelo *task = worktree + agente* é a frente do Orquestra materializada. **Mas** o padrão de fábrica dele viola duas regras suas (`bypassPermissions` nunca; nada silencioso) e a issue #9963 toca em LGPD (cópia de credenciais, daemon exposto na LAN). Adotar só com o endurecimento da seção 5 — e desistir se algum item não puder ser desligado.
- **Mais conservador com o mesmo modelo mental:** **Superset**. É o plano B natural se o Orca não passar no checklist.
- **Se você quiser editor + threads na mesma tela:** **Zed**. Aceitando a exposição à política pausada da Anthropic e a perda da TUI.
- **Zero curva:** **Warp**, que você já domina — resolve "um app", não resolve "thread = worktree".

---

## 3. Arquitetura recomendada — duas camadas, e a regra que liga as duas

```
┌─ App hospedeiro (Orca | Superset) ─────────────────────────────────────┐
│  thread A  = frente "interface"  → host CLAUDE (claude, Max)            │
│     Manager Claude ──/codex:adversarial-review──▶ GPT (revisor)         │
│                    ──/codex:rescue --model gpt-5.6-sol──▶ GPT (planner) │
│  thread B  = frente "sistema"    → host CODEX (codex, ChatGPT Max)      │
│     Manager Codex  ──run-opus-reviewer.py (claude -p)──▶ Opus (revisor) │
│  thread C  = frente que estourou a janela 5h do Claude → abre no Codex  │
└─────────────────────────────────────────────────────────────────────────┘
        ▲ board + wiki compartilhados entre as threads (card C2 decide como)
```

**Camada 1 — o app** dá o que você pediu literalmente: uma janela, N threads do mesmo projeto, cada thread com o host que você escolher, as duas assinaturas visíveis.

**Camada 2 — o roteamento dentro da sessão** já é o desenho do Orquestra ("domínio decide quem pensa, host decide quem escreve"). O que muda é o **mecanismo** da célula OpenAI × host Claude: sai `codex exec … < /dev/null` por Bash, entra o plugin oficial (card C1).

**A regra que liga as duas camadas — e que hoje não está escrita em lugar nenhum do Orquestra:** *a trilha do card escolhe o host da thread.* Card `interface` abre thread Claude (Manager + Fable pensando); card `sistema` abre thread Codex (Manager Sol + Terra escrevendo, Opus revisando). Assim as duas assinaturas viram **capacidade de escrita paralela**, e não só "revisor do outro lado". E há um terceiro gatilho, que hoje você resolve na mão: **janela de 5h do Claude esgotada → a próxima frente abre no host Codex**, sem trocar de perfil nem de app. O Orca mostra as duas janelas de uso na barra; o card C3 escreve a regra no `/orq:quadro`.

**O que continua impossível — dito com todas as letras:** um Manager que seja GPT num card e Fable no seguinte *dentro da mesma thread*. Nenhum dos dois vendors permite trocar o modelo da sessão principal para o outro vendor pela assinatura. A troca de Manager é sempre troca de thread — e `/codex:transfer` (Claude → thread persistente do Codex) é o mais perto que existe de "mudar de host sem perder a conversa": faça `/orq:checkpoint` antes, e a thread nova no Codex retoma pelo board (card C5).

---

## 4. O que muda no Orquestra — cards propostos (nenhum executado)

Ordem = prioridade. C2 vem antes de qualquer piloto com worktree por frente.

### C2 — Board compartilhado entre worktrees *(bloqueia a adoção; decisão sua)*
**Problema:** `memory/` está versionado (39 arquivos no git). O protocolo de várias janelas ("edite a linha, nunca o arquivo") pressupõe **um** `KANBAN.md` no disco. Orca/Superset/Conductor abrem cada thread num **worktree** → cada frente passa a ter o seu `KANBAN.md` num branch diferente, e o board bifurca em silêncio — a falha exata que o protocolo foi feito para evitar.
**Opções (escolha uma):**
- **(a) Frente no checkout principal, worktree só para o implementer** — é o status quo do Orquestra (`isolation: "worktree"` no spawn). Exige que o app permita abrir o agente **no diretório principal**, não num worktree. No Orca isso é "N agentes por task" na task raiz; **não verifiquei** se dá para desligar a criação de worktree por task — é o primeiro teste do piloto.
- **(b) `memory/` fora do branch** — o `init` cria `memory/` como *symlink* para um diretório único (`<repo>/.orq-memory/` ignorado pelo git, ou `~/.orq/<projeto>/memory`), e um hook `post-checkout`/`.worktreeinclude` recria o link em cada worktree. Board e wiki ficam **um só** para todas as threads; versionar vira responsabilidade de um commit periódico a partir do principal. Custo: muda o `init`, o `checkpoint` e o verificador de instalação; ganho: resolve para qualquer app.
- **(c) Board por frente com merge no checkpoint** — não recomendo: reintroduz reconciliação manual, que o `T-052` já mostrou o quanto custa.
**Recomendação:** (a) se o app deixar; senão (b). **Esforço:** (a) zero no plugin; (b) `pesada` (toca `init`, `checkpoint`, `verify_installed_cache.py`, docs). **Trilha:** `sistema`.

### C1 — Célula OpenAI × host Claude via `codex-plugin-cc` *(resolve `T-067` e parte do `T-063`)*
**Problema:** a Matriz manda `codex exec … < /dev/null` por Bash; sua regra global proíbe o binário direto (`T-067`). Além disso, `codex mcp-server` — a alternativa que alguém proporia — está **oficialmente depreciado** (doc da OpenAI: "use o app-server; para chamar o Codex do Claude Code, use o plugin"). Não adotar MCP-server.
**Proposta:** registrar na Matriz, célula OpenAI×Claude, o plugin oficial como mecanismo `comprovado` depois de uma sonda real:
- `reviewer` → `/codex:adversarial-review` (read-only, aceita foco; `--background` + `/codex:result` substitui o polling do `T-063`);
- `planner·sistema` → `/codex:rescue --model gpt-5.6-sol --effort ultra` **com briefing que só autoriza escrever o arquivo do plano** — o `rescue` é modo de escrita, então o read-only vira regra de briefing, não sandbox; se você preferir sandbox de verdade, a alternativa é o `codex exec -s read-only` **de dentro do subagente** (o que o `T-054` já faz), e a Matriz passa a dizer isso em vez de "por Bash";
- effort: o plugin usa o `~/.codex/config.toml` quando não recebe `--effort` — o `_elenco.md` continua mandando, e a regra "nunca dependa de default de config de terceiro" (2026-08-05) obriga a passar `--model`/`--effort` explícitos sempre.
**Cuidado:** o *review gate* do plugin (hook `Stop` que dispara revisão a cada resposta) é o que a própria OpenAI avisa que "pode drenar limites rapidamente" — deixar **desligado**; a revisão do Orquestra tem hora certa (fim do Loop B).
**Esforço:** `normal` (Matriz + `revisar.md` + `plan-next.md` + `stack.md`, que hoje diz explicitamente "não é o plugin"). **Trilha:** `sistema`. **Pré-requisito:** confirmar que o plugin está instalado no escopo de usuário (`/plugin list`).

### C3 — Trilha escolhe o host da thread; janela esgotada muda o host *(nova regra, escrita 1×)*
**Problema:** hoje o Orquestra resolve o time **dado o host**; não diz **qual host abrir** para um card. Com um app de threads, essa é a decisão que você toma dez vezes por dia.
**Proposta:** no `/orq:quadro`, cada card `[ ]`/`[>]` ganha a coluna *host sugerido*: `interface` → Claude; `sistema` → Codex; Trivial → o host que já está aberto. Gatilho adicional, consultivo: se o guardião (`context-guard.py`) ou a statusline reportar janela 5h do host ≥ 90%, o quadro sugere abrir a próxima frente no outro host **antes** de sugerir o perfil `economia` — trocar de host preserva a garantia (revisor forte), trocar de perfil rebaixa. Regra mora em `elenco.md`, seção "As duas réguas", como terceira régua.
**Esforço:** `leve`–`normal`. **Trilha:** `sistema`.

### C4 — Runner do Opus resistente à política e ao `--bare` *(defensivo)*
**Problema:** `run-opus-reviewer.py` é `claude -p`. Dois riscos nomeados na seção 1: (i) a Anthropic pode despausar a cobrança separada (US$ 200/mês no seu plano, a preço de API — o revisor do host Codex passaria a ter teto próprio); (ii) `--bare` virando padrão do `-p` quebra a autenticação por assinatura em silêncio.
**Proposta:** (i) o runner passa a detectar erro de autorização/cota e devolver `REVISÃO DEGRADADA — política Anthropic`, com a causa, em vez de saída vazia; a linha `runner-opus` do `_elenco.md` ganha nota "sujeito à política pausada de 15/jun/2026"; (ii) gotcha registrado + teste na suíte que falha se o comando montado contiver `--bare`, e sonda de instalação que confirma que o `-p` ainda lê OAuth (o `verify` já roda sondas). **Esforço:** `leve`. **Trilha:** `sistema`.

### C5 — Mudança de host no meio da frente: `checkpoint` + `/codex:transfer` *(opcional)*
**Proposta:** documentar em `checkpoint.md` a sequência "checkpoint → `/codex:transfer` → abrir a thread do Codex no app → `codex resume <id>`" como o caminho para continuar uma frente no outro host sem perder a conversa. Direção inversa (Codex → Claude) não tem equivalente: é checkpoint + thread nova pelo board. **Esforço:** `leve` (só texto).

### C6 — Statusline e medidor de uso *(só se o app for Orca)*
O Orca já mostra as janelas 5h/dia/semana das duas assinaturas. A statusline do Orquestra (`T-036`) mostra rate-limit 5h só do Claude. Não duplicar: manter na statusline o que o app não mostra (board, worktree, custo da sessão). **Esforço:** `leve`, e só depois do piloto.

**Fora do ciclo — sua decisão direta, sem card:** desligar o *review gate* do plugin; no Orca, modo *Manual* + telemetria off; no `~/.codex/config.toml`, deixar `model`/`model_reasoning_effort` iguais ao `_elenco.md` (defesa em profundidade contra o default de terceiro).

---

## 5. Plano de adoção — uma semana, sem tocar no plugin

**Dia 1 — endurecer o Orca antes de abrir qualquer projeto.** Configurações → Agents → *Manual* (não *Yolo*) para Claude Code **e** Codex; telemetria off; conferir com `lsof -iTCP -sTCP:LISTEN | grep orca` se o daemon escuta em `127.0.0.1` ou `0.0.0.0` (se for `0.0.0.0` e não houver opção, é motivo suficiente para o Superset); conferir se ele gravou hooks em `~/.claude/settings.json`, `~/.codex/config.toml`/`hooks.json` e `~/.cursor` — se gravou, remover e anotar no `gotchas.md`. Só depois: `claude` e `codex` logados fora do Orca, e o Orca reconhecendo as duas contas.

**Dia 2 — teste do C2 (o que bloqueia).** Abrir o `byia-claude-orquestra` no Orca. Tentar abrir uma thread Claude **no checkout principal** (sem worktree). Se der: opção (a) do C2, siga. Se toda thread for worktree: pare, e decida (b) antes de continuar — abrir duas frentes agora bifurcaria o board.

**Dia 3 — duas threads, dois hosts, um board.** Thread 1: host Claude, um card `interface`. Thread 2: host Codex, um card `sistema`. Checkpoint nas duas. Critério de aceite (o mesmo do `T-013`): nada some do `KANBAN.md`.

**Dia 4 — o plugin no lugar do `codex exec`.** Na thread Claude: `/codex:setup`, depois `/codex:adversarial-review` sobre um diff pequeno, com `--background` e `/codex:result`. Comparar o parecer com o que o `/orq:revisar` produz hoje. É a sonda real que o card C1 exige antes de mudar a Matriz.

**Dia 5 — o gatilho de janela.** Trabalhar até a barra do Orca mostrar a janela 5h do Claude alta; abrir a próxima frente no host Codex. Se a experiência for boa, o C3 vira card; se não, fica como regra sua e não do produto.

**Se o Orca falhar no dia 1 ou 2:** repetir os dias 2–5 no **Superset**. Se você quiser editor na mesma tela, **Zed** é a terceira tentativa — com a ressalva da política.

**O que fechar depois do piloto:** o app do Codex e o app do Claude saem do Dock. As duas extensões do VS Code continuam sendo o fallback "seguro por construção" para quando um app de terceiro quebrar numa release.

---

## 6. O que não fazer

- **Não** instalar plugin/harness que "faz login com a conta Claude" fora do binário oficial (OpenCode antigo, Pi com OAuth Anthropic, qualquer "Sign in with Claude" de terceiro) — é violação dos termos, e a Anthropic já bloqueia esse uso no servidor desde jan/2026.
- **Não** usar proxy/pool de contas para o Codex (sub2api) — a OpenAI classifica como fraude.
- **Não** adotar `codex mcp-server` — está depreciado; o caminho é app-server, e o plugin oficial já o encapsula.
- **Não** ligar o *review gate* do plugin da OpenAI — loop Claude↔Codex a cada resposta, drena as duas assinaturas.
- **Não** abrir duas frentes em worktrees antes de decidir o C2.
- **Não** deixar o Orca em *Yolo*: é `--dangerously-skip-permissions` para todos os agentes — o Orquestra existe justamente para não fazer isso.

---

## Fontes (verificadas em 2026-09-03)

Política das assinaturas: [Anthropic — Legal & compliance do Claude Code](https://code.claude.com/docs/en/legal-and-compliance) · [Anthropic — Use the Claude Agent SDK with your Claude plan (pausa de 15/jun)](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan) · [Anthropic — Headless / `--bare`](https://code.claude.com/docs/en/headless) · [Anthropic — Subagents (só modelos Claude)](https://code.claude.com/docs/en/sub-agents) · [OpenAI — Codex pricing (SDK/`exec` incluídos no Plus/Pro)](https://learn.chatgpt.com/docs/pricing.md) · [OpenAI — Codex auth e model providers](https://learn.chatgpt.com/docs/auth.md) · [OpenAI — Codex for Open Source](https://developers.openai.com/community/codex-for-oss) · [Zed — Anthropic subscription changes](https://zed.dev/blog/anthropic-subscription-changes) · [Conductor — Claude subscription update](https://www.conductor.build/blog/claude-subscription-update)

Roteamento: [openai/codex-plugin-cc](https://github.com/openai/codex-plugin-cc) · [OpenAI — `codex mcp-server` depreciado](https://learn.chatgpt.com/docs/mcp-server) · [OpenAI — app-server](https://learn.chatgpt.com/docs/app-server.md) · [Anthropic — `claude mcp serve`](https://code.claude.com/docs/en/mcp) · [claude-agent-acp](https://github.com/agentclientprotocol/claude-agent-acp) · [codex-acp](https://github.com/zed-industries/codex-acp)

Apps: [Orca](https://www.onorca.dev/) · [Orca — Claude Code](https://www.onorca.dev/docs/agents/claude-code) · [Orca — Codex](https://www.onorca.dev/docs/agents/codex) · [Orca — worktrees](https://www.onorca.dev/docs/model/worktrees) · [Orca — issue #9963](https://github.com/stablyai/orca/issues/9963) · [Superset](https://superset.sh/) · [Conductor — FAQ](https://www.conductor.build/docs/faq) · [Zed — External agents](https://zed.dev/docs/ai/external-agents) · [Zed — Parallel agents](https://zed.dev/docs/ai/parallel-agents) · [VS Code — Agent harnesses](https://code.visualstudio.com/docs/agents/run/agent-harnesses) · [VS Code — issue #314952](https://github.com/microsoft/vscode/issues/314952) · [Claude Code — VS Code](https://code.claude.com/docs/en/vs-code) · [Codex — IDE](https://learn.chatgpt.com/docs/codex/ide) · [Warp — CLI agents](https://docs.warp.dev/agents/cli-agents/overview/) · [Warp — múltiplos agentes](https://docs.warp.dev/guides/agent-workflows/how-to-run-multiple-ai-coding-agents/) · [Cursor — fórum sobre assinatura Claude](https://forum.cursor.com/t/allow-claude-max-claude-code-subscription-access-in-cursor/163716) · [Vibe Kanban — shutdown](https://www.vibekanban.com/blog/shutdown)

**Não verificado:** se o Orca permite thread sem worktree (teste do dia 2); data exata da depreciação do `codex mcp-server` (fonte secundária diz v0.149.1, 24/ago); se o plugin `codex-plugin-cc` já está instalado na sua máquina (a regra do `T-054` sugere que sim); se plugin/hooks/statusline do Orquestra carregam inteiros dentro de Conductor e Zed (via SDK/ACP) — em Orca, Superset, Warp e VS Code carregam, porque é o binário em PTY.
