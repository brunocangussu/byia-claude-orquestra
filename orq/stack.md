# Stack recomendada — ferramentas que fazem o Orquestra render mais

> **Catálogo canônico.** O `/orq:stack` e a FASE 1 do `/orq:init` leem este arquivo para detectar o
> que falta e propor a instalação. Uma IA lendo este repositório deve conseguir, só com o que está
> aqui, verificar o que já existe e instalar o resto — **sempre pedindo consentimento antes**.

## Leia isto primeiro

**Nada aqui é dependência.** O Orquestra funciona sozinho: board, agentes, wiki e gates não precisam
de nenhuma destas ferramentas. Elas atacam um problema diferente — **o contexto acaba** — e é por isso
que se somam bem a um plugin cujo princípio é *"contexto é descartável, o estado vive no board"*.

**Regras para quem for instalar (humano ou IA):**

1. **Nunca instale sem consentimento explícito do dono.** Mostre o comando exato antes de rodar.
2. **Nunca instale o que exige chave de API** sem que ele forneça a chave. Não invente credencial.
3. **Projeto pequeno merece stack pequena.** Abaixo de ~50 arquivos, camadas 3 e 4 não se pagam.
4. **Registre o que ele recusou** em `memory/wiki/_stack.md`, para não ser reproposto a cada sessão.

---

## Camada 1 — Economia de contexto

Atacam o custo por operação. Ganho imediato, sem mudar como você trabalha.

### `context-mode` — sandboxa saída gigante de ferramenta

**Resolve:** roda o comando num sandbox, indexa a saída e devolve só o trecho que responde à pergunta.
Um `npm test` de 4.000 linhas entra como as 12 linhas que interessam.

**Por que casa com o Orquestra:** os workers rodam build, teste e `git log` o tempo todo. Sem isso, um
único card queima a janela do implementer antes do review.

| | |
|---|---|
| **Detectar** | `ls ~/.claude/plugins/marketplaces/ \| grep -q context-mode` |
| **Instalar** | `/plugin marketplace add mksglu/context-mode` → `/plugin install context-mode@context-mode` |
| **Custo** | nenhum — sem chave, sem serviço externo |

### `rtk` — proxy de CLI que reescreve comandos comuns

**Resolve:** intercepta `git`, `ls` e afins e devolve a saída comprimida. 60-90% de economia nas
operações de desenvolvimento.

| | |
|---|---|
| **Detectar** | `which rtk` |
| **Instalar** | `brew install rtk` (macOS/Linux) · site: `https://www.rtk-ai.app/` |
| **Custo** | nenhum |
| **Cuidado** | existe outro projeto chamado `rtk` (Rust Type Kit). Se `rtk gain` falhar, é o errado |

---

## Camada 2 — Memória entre sessões

Atacam a perda ao trocar de janela. **É a camada mais alinhada com o Orquestra** — a wiki `memory/`
resolve o *"o que estamos construindo"*; estas resolvem o *"o que já tentamos e por quê"*.

### `claude-mem` — captura a sessão e reinjeta na próxima

**Resolve:** comprime o que aconteceu e injeta o resumo no início da sessão seguinte.

**Por que casa:** o Orquestra recomenda `checkpoint` + `/clear` em vez de `/compact` encadeado. O
`/clear` só é seguro porque alguma coisa reinjeta o contexto — a wiki cobre o estado do trabalho, e o
claude-mem cobre a textura da conversa.

| | |
|---|---|
| **Detectar** | `ls ~/.claude/plugins/marketplaces/ \| grep -q thedotmack` |
| **Instalar** | `/plugin marketplace add thedotmack/claude-mem` → `/plugin install claude-mem@thedotmack` |
| **Custo** | roda um worker local (`localhost:37777`) |
| **Opcional** | `/learn-codebase` ingere o repo inteiro de uma vez — uma vez por projeto |

### `Supermemory` — fatos de longo prazo, entre projetos

**Resolve:** decisões que valem além de um repositório ("por que a gente abandonou X").

| | |
|---|---|
| **Detectar** | MCP `api-supermemory-ai` configurado |
| **Instalar** | MCP HTTP em `https://api.supermemory.ai/mcp` — **exige conta e chave do dono** |
| **Custo** | serviço externo, dados saem da máquina — **precisa de consentimento informado** |

⚠️ **Gotcha conhecido:** a busca via MCP oficial devolve 0 resultados (o endpoint `/v3/search` ignora o
header de escopo). A gravação funciona. O `/orq:lembrar` contorna isso via
`orq/scripts/sm-search.py`. Se você instalar o MCP e a busca vier vazia, **não é falta de dados**.

---

## Camada 3 — Entender o código

Só valem em repositório grande. Em projeto pequeno o custo de indexar não se paga.

### A pergunta que sempre aparece: Serena e codebase-memory são redundantes?

**Não, mas há sobreposição real** — os dois acham símbolo por nome, e isso é onde a semelhança acaba.

| | `Serena` | `codebase-memory` |
|---|---|---|
| **Trabalha com** | LSP — o símbolo exato e suas referências | grafo — as relações entre símbolos |
| **Responde** | "me dê o corpo disto e edite-o com precisão" | "quem chama isto, e o que quebra se eu mudar" |
| **Ferramentas-chave** | `find_symbol` · `replace_symbol_body` · `rename_symbol` | `trace_path` · `query_graph` · `get_architecture` |
| **Escreve?** | **sim** — edição simbólica | não — só leitura |

**No Orquestra a sinergia é por papel:** o **planner** e o **reviewer** rendem com codebase-memory
(causa raiz e análise de impacto); o **implementer** rende com Serena (editar sem carregar arquivo
inteiro). São papéis diferentes, então os dois se pagam num repo grande.

**Se for escolher só um:** o gargalo é *entender* → codebase-memory. O gargalo é *editar com
precisão* → Serena. **Projeto com menos de ~50 arquivos → nenhum dos dois**, `grep` resolve.

| | Serena | codebase-memory |
|---|---|---|
| **Detectar** | MCP `serena` configurado | `which codebase-memory-mcp` |
| **Instalar** | MCP stdio: `uvx --from git+https://github.com/oraios/serena serena start-mcp-server --context=claude-code --project-from-cwd --open-web-dashboard false` (exige `uv`) | ⚠️ **origem não confirmada** — ver abaixo |
| **Custo** | indexação por projeto | binário grande (~255 MB) + indexação |

⚠️ **`codebase-memory-mcp`:** nesta máquina é um binário em `~/.local/bin/`, e **não foi possível
determinar o projeto upstream** a partir dela — não veio de npm nem de pipx. Antes de recomendar a
instalação a terceiros, **confirme a fonte oficial**. Não invente um comando de instalação aqui.

---

## Camada 4 — Revisão independente

### `codex` — GPT no painel de revisores

**Resolve:** modelos diferentes erram diferente. O valor está na **interseção** (alta confiança) e na
**divergência** (onde vale investigar).

| | |
|---|---|
| **Detectar** | `which codex` |
| **Instalar** | `/plugin marketplace add openai/codex-plugin-cc` — **exige conta OpenAI** |
| **Ativar** | marcar `ativo` na seção *Revisores externos* de `memory/wiki/_elenco.md` |
| **Custo** | segundo fornecedor, cobrança à parte |

Sem ele o painel roda só com o revisor Claude — funciona, você só perde a diversidade.

---

## Perfis sugeridos

| Perfil | Instalar |
|---|---|
| **Mínimo** (qualquer projeto) | `context-mode` + `claude-mem` |
| **Repo grande** | mínimo + `codebase-memory` e/ou `Serena` |
| **Trabalho crítico** | acima + `codex` no painel |
| **Multi-projeto** | acima + `Supermemory` |

Depois de instalar qualquer MCP ou plugin: **`/reload-plugins`** e confirmar que a ferramenta responde
antes de dizer ao dono que está pronto.
