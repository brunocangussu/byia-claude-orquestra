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
   pequeno que mexe com dinheiro ou dados de terceiros merece revisão independente.
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

Esta camada é opcional e **resolvida por host**. Não recomende plugin exclusivo de outro cliente e
nunca trate memória externa como requisito para o checkpoint.

### `claude-mem` — captura a sessão e reinjeta na próxima

📦 [`thedotmack/claude-mem`](https://github.com/thedotmack/claude-mem) · plugin do Claude Code, com
`.codex-plugin/` e `hooks/codex-hooks.json` no pacote — **o Codex também é alvo suportado**

Comprime o que aconteceu na sessão e injeta o resumo no início da seguinte.

**O papel, e por que ele não colide com a wiki:** o plugin recomenda `checkpoint` + `/clear` em vez
de `/compact` encadeado — e o `/clear` só é seguro porque alguma coisa devolve o contexto depois.
São duas memórias com funções distintas, e confundi-las é o erro a evitar:

| | Guarda | Como nasce |
|---|---|---|
| **wiki + checkpoint** | o **porquê** e as consequências — a fonte da verdade | escrita deliberadamente, curada |
| **claude-mem** | a **rede de segurança** do que não chegou ao checkpoint: gotcha de meio de sessão, decisão não registrada, sessão que morreu antes | captura automática |

**Complemento, nunca substituto.** Se as duas discordarem, a wiki vence. Sem ele o `/clear` continua
seguro, só mais seco.

**Ligue a busca, ou ele não se paga.** O valor não está na injeção automática — está em **conseguir
perguntar**. Uma instalação em que ninguém chama `mem-search`/`get_observations` paga o custo e não
colhe nada; o gatilho *"lembra quando a gente…"* tem que **nomear a ferramenta**, não dizer "alguma
busca do host".

**Regule por TIPO, não por quantidade.** A captura é dominada por narração de sessão — medido num
projeto real: **80% das observações são `discovery` + `change`** ("testes verdes", "gate ok"), que é
exatamente o que a wiki chama de derivável. Filtrar a injeção por `decision, bugfix, gotcha,
security_alert, security_note` corta o ruído na raiz; baixar a contagem só corta ruído e sinal na
mesma proporção. ⚠️ **Só filtre depois de ligar a busca:** quem atribui o tipo é um modelo, não uma
regra, e o que for classificado errado sai da injeção — se a busca não estiver ligada, fica
inalcançável pelos dois caminhos.

**Detectar:** marketplace `thedotmack` registrado. **Custo:** roda um worker local, e o observer faz
uma chamada de modelo barato por observação — **medir antes de instalar em host cujo gargalo seja
número de chamadas**.

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

Modelos diferentes erram diferente — e **fornecedores** diferentes erram de forma menos
correlacionada que duas instâncias do mesmo modelo. Por isso o revisor do Orquestra é **um só, e
sempre do vendor oposto ao host**: no host Claude, quem revisa é o GPT; no host Codex, o Opus. Sem a
via para o outro vendor, **não há revisão independente nenhuma** — não existe cair num revisor do
mesmo vendor do host.

⚠️ **Esta camada é host-aware: resolva o host ANTES de propor.** A ferramenta a instalar é a do
**vendor oposto** ao do host — a do próprio vendor do host não entrega revisão nenhuma, por mais
bem instalada que esteja.

| Host | O que provisionar | Papel que ela cumpre |
|---|---|---|
| **Claude Code** | a CLI `codex` (OpenAI) | é o revisor |
| **Codex** | a CLI `claude` (Anthropic) + o `run-opus-reviewer.py`, que já vem no pacote | é o revisor |

Propor `codex` no host Codex — ou `claude` no host Claude — é propor o vendor do próprio host: o
diagnóstico fica verde e o projeto continua **sem revisor independente**. Se o titular do host
atual não estiver instalado, essa é a lacuna a reportar, e ela tem rota executável nos dois casos.

### `codex` — o revisor do host Claude

📦 [`openai/codex`](https://github.com/openai/codex) · **a CLI** (pacote npm `@openai/codex`)

**Por que importa no Orquestra:** no host Claude ele **é** o revisor — o único parecer independente
de quem escreveu. Sem ele, toda revisão vira degradada: o Manager audita o diff ele mesmo e declara
a ausência.

**É a CLI que o `/orq:revisar` usa** (`codex exec … < /dev/null`), não o plugin
[`openai/codex-plugin-cc`](https://github.com/openai/codex-plugin-cc), que é outro artefato e serve a
outro fluxo. Instalar um não instala o outro — não confunda os dois na hora de detectar.

**Ativar depois de instalar:** marcar `ativo` na seção *Revisores externos* de
`memory/wiki/_elenco.md`.

**Detectar:** `codex` no PATH, com fallback para o bin global do npm —
`CODEX=$(command -v codex || echo "$(npm prefix -g 2>/dev/null)/bin/codex")` — e `"$CODEX" --version`
respondendo. A sonda viva (`"$CODEX" exec -s read-only "responda OK" < /dev/null`) é **chamada
paga**: use-a só quando o sintoma for revisor mudo — e nunca sem o `< /dev/null`, senão ela trava
esperando stdin e você concluiria "quebrado" por engano.

**Custo:** conta OpenAI, cobrança à parte.

### `claude` + `run-opus-reviewer.py` — o revisor do host Codex

📦 [`anthropics/claude-code`](https://github.com/anthropics/claude-code) · **a CLI** (pacote npm
`@anthropic-ai/claude-code`). O runner **não** se instala: `orq/scripts/run-opus-reviewer.py` já vem
no pacote do Orquestra — o que falta provisionar é a CLI que ele invoca.

**Por que importa no Orquestra:** no host Codex ele **é** o revisor. Sem a CLI no PATH, o host Codex
fica sem parecer independente e toda revisão sai degradada — o mesmo buraco que o `codex` ausente
abre no host Claude, na direção oposta.

**Ativar depois de instalar:** marcar `ativo` na linha `runner-opus` da seção *Revisores externos* de
`memory/wiki/_elenco.md`.

**Detectar:** `claude` no PATH, com fallback para o bin global do npm —
`CLAUDE=$(command -v claude || echo "$(npm prefix -g 2>/dev/null)/bin/claude")` — e
`"$CLAUDE" --version` respondendo. Checar só o PATH **dá falso negativo**: instaladores escrevem no
`.zshrc`, que não alcança sessão já aberta.

⚠️ **CLI respondendo não é revisor funcionando.** O runner só imprime parecer quando o JSON comprova
`claude-opus-5`; conta sem acesso ao Opus 5 devolve **revisão degradada**, não um parecer mais fraco.
A sonda viva é o próprio runner (16 KiB por lote, timeout 600s) e é **chamada paga** — use-a só
quando o sintoma for revisor mudo, sempre com `< /dev/null`.

**Custo:** conta Anthropic com acesso ao Opus 5, cobrança à parte.

---

## Perfis sugeridos

**Os perfis não são cumulativos** — combine só o que se aplica. Um dono com cinco repositórios
pequenos continua no perfil mínimo; quantidade de repositórios, sozinha, não justifica serviço
externo de memória nem arrasta a camada 3.

| Perfil | Acrescenta |
|---|---|
| **Mínimo** (qualquer host) | ferramentas compatíveis da Camada 1; nenhuma memória externa obrigatória |
| **Memória de conversa** (qualquer host com suporte) | `claude-mem` — rede de segurança do que não chegou ao checkpoint. O pacote traz `.codex-plugin/` e `hooks/codex-hooks.json`, então **o Codex também é alvo**; medir o custo dos 5 hooks antes de instalar lá |
| **Repo grande** (≳50 arquivos) | `codebase-memory` e/ou Serena |
| **Trabalho crítico** (dinheiro, dados de terceiros, segurança) | o revisor do **vendor oposto ao host**: `codex` se o host é o Claude Code; a CLI `claude` (+ o runner Opus já empacotado) se o host é o Codex |

Depois de instalar: **presuma restart** — não testado por componente para instalação de ferramenta
nova. O `claude plugin update --help` diz "(restart required to apply)"; trate como **aviso
conservador**, não como prova — para **skill**, esse mesmo tipo de aviso já foi desmentido 1× (a
sessão viva passou a servir a skill nova sem restart, noutro contexto). O `install --help` não
menciona restart, o que reforça a leitura de aviso conservador, não confirmação. Instalação por
slash command dentro do cliente, peça o `/reload-plugins` ao dono. Em qualquer caso, confirme que a
ferramenta **responde** antes de dizer que está pronta. Instalado ≠ funcionando.
