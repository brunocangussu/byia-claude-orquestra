# Stack recomendada — ferramentas que fazem o Orquestra render mais

> **Catálogo canônico.** O `/orq:stack` e a FASE 1 do `/orq:init` leem este arquivo para detectar o
> que falta e propor. Uma IA lendo este repositório deve conseguir, só com o que está aqui, verificar
> o que já existe e ir buscar o resto — **sempre pedindo consentimento antes**.

## Leia isto primeiro

**Nada aqui é dependência.** O Orquestra funciona sozinho: board, agentes, wiki e gates não precisam
de nenhuma destas ferramentas. Elas atacam um problema vizinho — **o contexto acaba** — e é por isso
que se somam bem a um plugin cujo princípio é *"contexto é descartável, o estado vive no board"*.

**Este catálogo não traz comando de instalação, de propósito.** Comando envelhece; repositório não.
Cada ferramenta abaixo aponta para o repo oficial, onde as instruções estão sempre atualizadas e
corretas para a plataforma de quem instala. **Vá ao repositório, leia o README de lá, e só então
proponha ao dono o que pretende rodar.** Não reproduza aqui o que você encontrar — este arquivo
responde *o que é e por que importa*; o upstream responde *como instalar*.

**Regras para quem for instalar (humano ou IA):**

1. **Nunca instale sem consentimento explícito do dono.** Mostre o que vai rodar, e de onde tirou.
2. **Nunca instale o que exige chave de API** sem que ele forneça a chave. Não invente credencial e
   não reaproveite chave de outro serviço.
3. **Projeto pequeno merece stack pequena.** Abaixo de ~50 arquivos, a camada 3 não se paga. **A
   camada 4 é exceção** — revisor externo se decide por *criticidade*, não por tamanho: um script
   pequeno que mexe com dinheiro ou dados de terceiros merece painel.
4. **Registre o que ele recusou** em `memory/wiki/_stack.md`, para não ser reproposto a cada sessão.
5. **Repositório oficial, não fork.** Vários destes têm forks populares com nome parecido. Confira o
   dono do repo antes.
6. **Como detectar plugin do Claude Code:** o marketplace aparece em
   `~/.claude/plugins/known_marketplaces.json` e o plugin em `~/.claude/plugins/installed_plugins.json`.
   **Não procure plugin no PATH** — ele não é binário; `which <nome>` sempre falha e você concluiria
   "ausente" para algo já instalado. MCP: procure em `~/.claude.json` (chave `mcpServers`) e confirme
   que **responde**, não só que está configurado.

---

## Camada 1 — Economia de contexto

Atacam o custo por operação. Ganho imediato, sem mudar como você trabalha.

### `context-mode` — sandboxa saída gigante de ferramenta

📦 [`mksglu/context-mode`](https://github.com/mksglu/context-mode) · plugin do Claude Code

Roda o comando num sandbox, indexa a saída e devolve só o trecho que responde à pergunta. Um
`npm test` de 4.000 linhas entra na janela como as 12 linhas que interessam.

**Por que importa no Orquestra:** os workers rodam build, teste e `git log` o tempo todo. Sem isso um
único card queima a janela do implementer antes de o review começar — e aí o handoff sai pobre
justamente no momento em que ele mais importa.

**Detectar:** marketplace `context-mode` registrado. **Custo:** nenhum — sem chave, sem serviço externo.

### `rtk` — proxy de CLI que comprime comandos comuns

📦 [`rtk-ai/rtk`](https://github.com/rtk-ai/rtk) · binário Rust único

Intercepta `git`, `cargo`, `pytest`, `docker` e ~100 outros, devolvendo saída filtrada e deduplicada.
60-90% de economia nas operações de desenvolvimento, com overhead de milissegundos.

**Por que importa no Orquestra:** o Manager vive lendo estado do repositório para decidir. É a
ferramenta mais barata da lista em relação ao que devolve.

**Detectar:** `rtk` no PATH — e `rtk gain` deve responder. **Custo:** nenhum.

⚠️ **Existe outro projeto chamado `rtk`** (Rust Type Kit), e forks com nome parecido. Se `rtk gain`
falhar, você instalou o errado.

---

## Camada 2 — Memória entre sessões

Atacam a perda ao trocar de janela. **É a camada mais alinhada com o Orquestra:** a wiki `memory/`
resolve *"o que estamos construindo"*; estas resolvem *"o que já tentamos, e por quê"*.

### `claude-mem` — captura a sessão e reinjeta na próxima

📦 [`thedotmack/claude-mem`](https://github.com/thedotmack/claude-mem) · plugin do Claude Code

Comprime o que aconteceu na sessão e injeta o resumo no início da seguinte.

**Por que importa no Orquestra:** o plugin recomenda `checkpoint` + `/clear` em vez de `/compact`
encadeado — e o `/clear` só é seguro porque alguma coisa devolve o contexto depois. A wiki cobre o
**estado do trabalho**; o claude-mem cobre a **textura da conversa** (o que foi tentado e descartado,
o tom da decisão). Sem ele o `/clear` continua seguro, mas mais seco.

**Detectar:** marketplace `thedotmack` registrado. **Custo:** roda um worker local.

### Supermemory — fatos de longo prazo, entre projetos

📦 [`supermemoryai/supermemory`](https://github.com/supermemoryai/supermemory) · MCP em
[`supermemoryai/supermemory-mcp`](https://github.com/supermemoryai/supermemory-mcp)

Memória que atravessa repositórios: decisões que valem além de um projeto ("por que abandonamos X").

**Por que importa no Orquestra:** a wiki é por projeto. Quem trabalha em vários repos acaba
redecidindo a mesma coisa em cada um.

**Detectar:** MCP `api-supermemory-ai` configurado. **Custo:** **serviço externo — os dados saem da
máquina, e exige conta e chave.** Precisa de consentimento informado, não só um "pode instalar".

⚠️ **Gotcha conhecido:** a busca via MCP oficial devolve 0 resultados — o endpoint de busca ignora o
header de escopo do projeto. A **gravação funciona**. O `/orq:lembrar` contorna via
`orq/scripts/sm-search.py`. Se a busca vier vazia, **não é falta de dados**.

---

## Camada 3 — Entender o código

Só valem em repositório grande. Em projeto pequeno o custo de indexar não se paga.

### A pergunta que sempre aparece: Serena e codebase-memory são redundantes?

**Não, mas se sobrepõem** — os dois acham símbolo por nome, e é aí que a semelhança acaba.

| | Serena | codebase-memory |
|---|---|---|
| **Trabalha com** | LSP — o símbolo exato e suas referências | grafo — as relações entre símbolos |
| **Responde** | "me dê o corpo disto e edite com precisão" | "quem chama isto, o que quebra se eu mudar" |
| **Ferramentas-chave** | `find_symbol` · `replace_symbol_body` · `rename_symbol` | `trace_path` · `query_graph` · `get_architecture` |
| **Escreve?** | **sim** — edição simbólica | não — só leitura |

**No Orquestra a sinergia é por papel:** **planner** e **reviewer** rendem com o grafo (causa raiz e
análise de impacto); o **implementer** rende com o LSP (editar sem carregar arquivo inteiro). São
papéis diferentes, então os dois se pagam num repo grande.

**Se for escolher um só:** gargalo em *entender* → codebase-memory. Gargalo em *editar com precisão*
→ Serena. **Menos de ~50 arquivos → nenhum dos dois**, `grep` resolve.

### Serena

📦 [`oraios/serena`](https://github.com/oraios/serena) · MCP

**Detectar:** MCP `serena` configurado e respondendo. **Custo:** indexação por projeto.

### codebase-memory

📦 [`DeusData/codebase-memory-mcp`](https://github.com/DeusData/codebase-memory-mcp) · MCP, binário
estático único

Indexa o repositório num grafo persistente de funções, classes, cadeias de chamada e rotas. 158
linguagens, consultas em menos de 1 ms.

**Detectar:** `codebase-memory-mcp` no PATH ou MCP configurado. **Custo:** binário grande (~255 MB)
mais o tempo de indexação. Existem **forks populares** — confira que é o repo do DeusData.

---

## Camada 4 — Revisão independente

### `codex` — GPT no painel de revisores

📦 [`openai/codex`](https://github.com/openai/codex) · **a CLI** (pacote npm `@openai/codex`)

**Por que importa no Orquestra:** modelos diferentes erram diferente. O valor está na **interseção**
(alta confiança) e na **divergência** (onde vale investigar). Sem ele o painel roda só com o revisor
Claude — funciona, você perde a diversidade.

**É a CLI que o `/orq:revisar` usa** (`codex exec … < /dev/null`), não o plugin
[`openai/codex-plugin-cc`](https://github.com/openai/codex-plugin-cc), que é outro artefato e serve a
outro fluxo. Instalar um não instala o outro — não confunda os dois na hora de detectar.

**Ativar depois de instalar:** marcar `ativo` na seção *Revisores externos* de
`memory/wiki/_elenco.md`. **Detectar:** `codex` no PATH **e** responder a um teste trivial
(`codex exec -s read-only "responda OK" < /dev/null`) — sem o `< /dev/null` ele trava esperando stdin
e você concluiria "quebrado" por engano. **Custo:** conta OpenAI, cobrança à parte.

---

## Perfis sugeridos

**Os perfis não são cumulativos** — combine só o que se aplica. Um dono com cinco repositórios de 20
arquivos é "mínimo + Supermemory", **não** arrasta a camada 3.

| Perfil | Acrescenta |
|---|---|
| **Mínimo** (qualquer projeto) | `context-mode` + `claude-mem` |
| **Repo grande** (≳50 arquivos) | `codebase-memory` e/ou Serena |
| **Trabalho crítico** (dinheiro, dados de terceiros, segurança) | `codex` no painel |
| **Multi-projeto** | Supermemory |

Depois de instalar qualquer plugin ou MCP: **`/reload-plugins`** e confirmar que a ferramenta
**responde** antes de dizer ao dono que está pronta. Instalado ≠ funcionando.
