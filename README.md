# Orquestra (`orq`)

Plugin do Claude Code para **desenvolvimento orientado a board**: time de agentes efêmeros,
memória-wiki durável, painel de revisores e gates humanos.

Nasceu da arquitetura que o Alison montou no app **Terminals** (canvas de terminais multi-agente),
redesenhada para as primitivas nativas do Claude Code — sem canvas, sem agentes residentes, sem
`bypassPermissions`.

---

## A ideia em uma frase

> **Contexto é descartável. O estado do trabalho vive no board e nos artefatos.**

A janela pode morrer a qualquer momento — e vai. Se o estado só existe no chat, ele se perde. Por
isso todo passo termina gravando no board (`memory/wiki/KANBAN.md`) e na wiki (`memory/wiki/`).

Isso elimina a necessidade de ficar compactando conversa pra "não perder o raciocínio".

---

## Você não digita comandos

O plugin foi feito pra ser usado **conversando**. Você fala; o Claude reconhece a intenção e executa.

| Você diz | Acontece |
|---|---|
| *"onde paramos?"* · *"o que falta?"* | mostra o board, começando pelo que espera você |
| *"terminamos, pode limpar"* | salva tudo na memória e libera compactação nativa no Codex ou `/clear` no Claude |
| *"vamos planejar isso"* | planeja e **para** pra você aprovar |
| *"pode implementar"* · *"manda ver"* | implementa + revisa + documenta |
| *"anota isso"* · *"não esquece disso"* | vira card no backlog |
| *"revisa isso aí"* | painel de revisores (Claude + Codex + Kimi) |
| *"lembra o que decidimos sobre X?"* | busca primeiro na wiki e complementa só com memória elegível do host |
| *"vou dormir, adianta o que der"* | modo noturno |
| *"bom dia"* | relatório do que rodou à noite |
| *"tá lento"* · *"o que falta instalar?"* | detecta a stack que falta e instala o que você aprovar |
| *"quais as possibilidades?"* · *"o que dá pra fazer?"* | mostra o cardápio por situação — esta mesma tabela, adaptada ao projeto |

Os comandos `/orq:*` existem como mecanismo. Use se quiser, mas não precisa.

### Interface por host

- **Claude Code:** conversa natural ou comandos `/orq:*`.
- **Codex:** linguagem natural ou `/skills`. A pasta `commands/` do plugin não cria `/orq:*` no
  Codex; a ausência desse comando no menu não significa plugin ausente.

No Codex, “instalado e habilitado”, “skill carregada” e “smoke comportamental aprovado” são estados
diferentes. O diagnóstico e o instalador mostram os três separadamente. Um atalho local
`/prompts:orq` pode ser criado manualmente como compatibilidade depreciada, mas não integra a
instalação padrão e exige nova conversa/reinício.

---

## Instalar

```bash
# 1. registrar o marketplace (uma vez por máquina)
/plugin marketplace add brunocangussu/byia-claude-orquestra

# 2. instalar (escopo de usuário = vale em todos os projetos)
/plugin install orq@orquestra
/reload-plugins    # se um comando não aparecer, reinicie a sessão

# 3. montar no projeto (uma vez por projeto)
/orq:init
```

### O que o `/orq:init` faz

Ele **se adapta ao projeto** — não despeja estrutura genérica:

1. **Investiga** (agentes em paralelo): stack, domínio, convenções, o que quebra o deploy, docs que
   já existem, TODO/FIXME espalhados, testes quebrados.
2. **Detecta o ferramental real**: MCPs conectados, se o repo já está indexado para busca semântica,
   se há claude-mem / context-mode.
3. **Decide o time sob medida** — *"tem 90 migrations e RLS → vale um agente de dados"*. Se o projeto
   já tem agentes bons, **reaproveita** em vez de duplicar.
4. **Propõe e espera** sua aprovação. Nada é escrito antes.
5. **Monta**: memória + board com o **backlog real que encontrou** + agentes + bloco no `CLAUDE.md`
   e no `AGENTS.md`.

É idempotente: rodar de novo completa o que falta e relata o que ignorou.

---

## Stack recomendada (opcional)

**O Orquestra funciona sozinho.** Board, agentes, wiki e gates não dependem de mais nada. Mas ele
convive com um problema vizinho — *o contexto acaba* — e existe um conjunto de ferramentas que ataca
exatamente isso. Elas não são requisito; são o que separa "funciona" de "rende".

| Camada | Ferramentas | O que muda |
|---|---|---|
| **Economia de contexto** | [`context-mode`](https://github.com/mksglu/context-mode) · [`rtk`](https://github.com/rtk-ai/rtk) | um `npm test` de 4.000 linhas entra como as 12 que interessam |
| **Memória entre sessões** | [`claude-mem`](https://github.com/thedotmack/claude-mem) | complementa a wiki ao reinjetar contexto de conversa; `checkpoint` continua canônico e independente dela |
| **Entender o código** | [`codebase-memory`](https://github.com/DeusData/codebase-memory-mcp) · [Serena](https://github.com/oraios/serena) | só valem em repo grande — ver a comparação abaixo |
| **Revisão independente** | [`codex`](https://github.com/openai/codex) · [`kimi`](https://github.com/MoonshotAI/kimi-code) | fornecedores diferentes erram de forma menos correlacionada |

**Serena e codebase-memory são redundantes?** Não, mas se sobrepõem: os dois acham símbolo por nome, e
a semelhança acaba aí. Serena é **LSP + edição** ("me dê o corpo disto e edite com precisão");
codebase-memory é **grafo de relações** ("quem chama isto, o que quebra se eu mudar"). No Orquestra a
sinergia é por papel — planner e reviewer rendem com o grafo, implementer rende com o LSP. Se for
escolher um só: gargalo em *entender* → codebase-memory; em *editar* → Serena. Projeto com menos de
~50 arquivos → nenhum dos dois.

O catálogo completo — o que cada uma resolve, por que importa *neste* fluxo, como detectar e qual o
custo honesto — está em [`orq/stack.md`](orq/stack.md). Ele é escrito para ser lido **por uma IA**:
rodando `/orq:stack` (ou o `/orq:init`), o Claude verifica o que já existe na máquina, corta o que não
se paga neste projeto, e propõe o resto com ganho e custo lado a lado.

**O catálogo não traz comando de instalação, de propósito** — comando envelhece, repositório não. Ele
aponta o repo oficial de cada ferramenta; na hora de instalar, o Claude vai lá, lê as instruções
atuais e mostra a você o que pretende rodar antes de rodar.

> **Nada é instalado sem o seu "pode instalar".** Nada que exija chave de API é instalado sem você
> fornecer a chave. E o que você dispensar fica registrado em `memory/wiki/_stack.md` para **não ser
> reproposto** toda sessão.

---

## O ciclo

```
  planejar  ──→  [ VOCÊ APROVA ]  ──→  implementar  ──→  [ VOCÊ VALIDA ]  ──→  feito
     ↑                                       │
     └── checkpoint + compactação nativa (Codex) / /clear (Claude) ←──┘
```

| Comando | O que faz |
|---|---|
| `/orq:init` | Instala e **adapta** o Orquestra ao projeto |
| `/orq:instalar` | Instala **o plugin em si** nos hosts alternativos do dono (Codex, Kimi) |
| `/orq:plan-next` | **Loop A** — planeja o próximo card e para no gate |
| `/orq:implement-next` | **Loop B** — implementa + painel de revisão + documentação |
| `/orq:revisar` | Painel de revisores sobre a mudança atual |
| `/orq:auditar` | Ledger de remoção ou prova graph-first a partir de trace explícito, offline e sem hooks |
| `/orq:elenco` | Ver/trocar qual LLM toca cada papel |
| `/orq:stack` | Detecta ferramentas de contexto/memória que faltam e instala o que você aprovar |
| `/orq:quadro` | Mostra o board e o progresso |
| `/orq:checkpoint` | Fecha o bloco de trabalho na memória; libera compactação nativa no Codex e antecede `/clear` no Claude |
| `/orq:wiki-lint` | Health-check da wiki: contradições, órfãs, afirmações vencidas |
| `/orq:dormir` | Modo noturno — adianta planejamento |
| `/orq:acordar` | Relatório do modo noturno |
| `/orq:ajuda` | Cardápio por situação — o que dizer pra cada coisa acontecer |

---

## O time

Todos são **spawns frescos** — nunca reaproveitados entre cards. Contexto contaminado faz o agente
arrastar premissas da tarefa anterior.

| Agente | Papel | Escreve? |
|---|---|---|
| `orq-scout` | Investiga território novo e relata | ❌ read-only |
| `orq-planner` | Acha a **causa raiz** e desenha o plano | só o arquivo do plano |
| `orq-implementer` | Implementa o plano aprovado | ✅ |
| `orq-reviewer` | Revisa de forma adversarial | ❌ read-only (aponta, não corrige) |
| `orq-docs` | Documenta o código **final** + atualiza a wiki | ✅ docs |

**O Manager é a sessão principal** — não é um subagente. Só ele move cards e fala com você.

---

## Elenco — escolher a LLM de cada papel

Qual modelo interpreta cada papel é **configurável por projeto**, em `memory/wiki/_elenco.md`.
Os comandos leem esse arquivo antes de spawnar e passam o modelo como override — o `model:` do
arquivo do agente é só o padrão de fábrica.

```bash
/orq:elenco                    # mostra a escalação atual
/orq:elenco planner fable      # troca o planner pro Fable 5
/orq:elenco reviewer opus      # revisor interno em Opus
/orq:elenco codex off          # tira o GPT do painel (só Claude)
/orq:elenco codex xhigh        # ajusta o esforço do Codex
/orq:elenco perfil economia    # fim do ciclo: troca o time inteiro pelo preset de crédito curto
/orq:elenco perfil padrao      # crédito voltou: time titular de volta
```

Ou simplesmente fale: *"quero o Fable planejando"* · *"tira o GPT da revisão"* · *"quem tá revisando?"*

**Perfis** — além do ajuste papel a papel, o `_elenco.md` pode ter **times nomeados** (seção
"Perfis"): `padrao` (o titular) e `economia` (crédito Claude curto). Trocar o perfil reescreve a
tabela ativa; os comandos continuam lendo a mesma tabela. Honesto: perfil de economia muda a
**garantia**, não só o custo — reconciliação mais fraca, mais peso em revisor sem sandbox — e o
preset lista isso com todas as letras. O `manager` nunca entra em perfil: é o
`/model` da sessão, e só o dono troca.

**Padrões de fábrica:**

| Papel | Modelo | Por quê |
|---|---|---|
| `manager` | *sessão principal* | definido pelo `/model` — não é spawn, não muda por aqui |
| `planner` | `opus` | achar causa raiz e desenhar solução é o trabalho mais difícil |
| `implementer` | `inherit` | acompanha o modelo da sessão |
| `reviewer` | `opus` | revisão adversarial exige raciocínio forte |
| `docs` | `sonnet` | escrita objetiva sobre código já pronto |
| `scout` | `sonnet` | leitura ampla e barata |

Valores aceitos: `opus` · `sonnet` · `haiku` · `fable` · `inherit` · ou um id específico
(`claude-opus-5`).

**Onde modelo forte se paga:** planner e reviewer. Um erro de plano custa a implementação inteira;
um review fraco deixa passar o que vai quebrar depois. Docs e scout resolvem com modelo menor.

**Quer só Claude, sem GPT?** `/orq:elenco codex off` e deixe o reviewer em `opus`. Você perde a
diversidade do painel (modelos diferentes erram diferente), mas ganha um fornecedor só.

---

## Painel de revisores

Revisores diferentes erram de formas diferentes: um acha o bug de lógica, outro acha o vazamento de
escopo. O valor está na **interseção** (alta confiança) e na **divergência** (onde vale investigar).

**Hoje:**
- `orq-reviewer` — Claude, adversarial, sempre roda
- **Codex** (GPT-5.6 Sol, `--effort xhigh`) — se o plugin `codex` estiver instalado

**Reconciliação obrigatória** — nunca despejar dois pareceres um embaixo do outro:

| Situação | O que o Manager faz |
|---|---|
| Confirmado por 2+ revisores | alta confiança, vai no topo |
| Achado por só um | **verifica no código** antes de aceitar |
| Revisores discordam | **desempata olhando o código** e explica |
| Sem cenário de falha concreto | descarta ou marca como opinião de estilo |

### Revisores externos (Codex + Kimi K3)

Registre na seção **Revisores externos** do mesmo `memory/wiki/_elenco.md`:

```markdown
## Revisores externos
| Revisor | Estado | Config |
|---|---|---|
| codex | ativo | `--model gpt-5.6-sol --effort xhigh` (read-only) |
| kimi | ativo | `kimi-code/k3` · CLI com `-m` antes de `-p` · read-only, sem `--yolo`/`--auto` |
```

O `/orq:revisar` lê esse arquivo e inclui todo revisor marcado como **ativo**. Aqui, ativo significa
política habilitada, não saúde de runtime: CLI, autenticação, modelo e saída são verificados a cada
parecer. No Host Codex, o painel é exatamente Opus 5 + Kimi K3 e não inclui uma diagonal OpenAI;
no Host Kimi, o parecer Moonshot fresco entra pela diagonal da Matriz. Capacidade ausente vira
**PAINEL PARCIAL** com a causa nomeada; nunca é tratada como parecer entregue nem substituída.
O Opus roda por `orq/scripts/run-opus-reviewer.py`: briefings acima de 16 KiB são divididos por
arquivo/hunk sem truncamento; cada lote tem timeout e só vale se o JSON comprovar
`claude-opus-5`. Timeout, modelo errado ou saída vazia deixam diagnóstico explícito.

Em card pequeno e de baixo risco, use `--rapido` (só o revisor interno). Painel em mudança trivial
é desperdício. Se o revisor interno estiver rebaixado, quem decide o painel mínimo é o
`/orq:revisar` — regra lá.

---

## O board

`memory/wiki/KANBAN.md`. O estado de cada card é o marcador da linha:

| | |
|---|---|
| `[ ]` | backlog |
| `[>]` | planejando |
| `[!]` | **esperando você** — estacionamento |
| `[~]` | aprovado / implementando |
| `[?]` | aguardando sua validação |
| `[x]` | feito |

O `[!]` é a peça mais importante do desenho: um card que precisa de decisão **sai da fila em vez de
travá-la**. É o que permite o modo noturno funcionar sem você.

**Regras do board:** só o Manager move cards · `PLANNING → READY` exige sua aprovação explícita ·
**commit não é critério de pronto** (card fecha em `VALIDATE`; você confirma usando o produto).

---

## Iniciativa própria

O Manager também age **sem você pedir**, dentro de limites — mas nunca escreve o produto por conta
própria: toda mudança continua entrando pelo ciclo. Os três níveis, as condições de cada um e o
teto ficam só na skill `orq` (`orq/skills/orq/SKILL.md`), seção "Decisões que o Manager toma
sozinho" — este README não os repete, pra não divergir dela.

---

## A memória (wiki)

O board diz *onde estamos*; a wiki diz *o que o sistema é*.

| Arquivo | Papel |
|---|---|
| `memory/MEMORY.md` | **Índice** — leia primeiro |
| `memory/wiki/<tópico>.md` | Como funciona **hoje** (reescrita quando muda) |
| `memory/wiki/threads/` | Trabalho em curso, com **"RETOMAR AQUI"** |
| `memory/fixes-history.md` | Log cronológico, append-only |
| `memory/gotchas.md` | Armadilhas que já causaram bug |

**A distinção que faz funcionar:** o log responde *"o que aconteceu naquele dia"* (append, imutável);
a página de tópico responde *"como funciona hoje"* (**reescrita**). Sem a página, a segunda pergunta
vira arqueologia no log.

---

## Modo noturno

*"Vou dormir, adianta o que der"* → o Orquestra **planeja** os próximos cards do backlog e
**estaciona** o que precisar de decisão sua, com a pergunta exata escrita no card. De manhã,
*"bom dia"* traz o relatório com as perguntas **numeradas**: você responde *"1-sim, 2-a segunda
opção"* e destrava a fila inteira.

**Limites duros:** 3 cards e 4 horas por padrão · para após 2 rodadas sem progresso · **só
planejamento, nunca implementação** · recusa qualquer card de schema, segurança, deploy, dependência
nova ou irreversível.

**Proibido, sem exceção, com você dormindo:** implementar · `push`/merge/deploy · migration ou SQL de
escrita · ler ou expor segredo · instalar dependência · mandar mensagem pra fora · decidir no seu
lugar.

> ⚠️ **Limitação honesta:** a sessão do Claude Code precisa ficar **aberta** (máquina ligada, sem
> suspender). Cron no Claude Code é *session-scoped* — não existe execução realmente desacompanhada
> dentro do CLI. Se a máquina dormir, o trabalho pausa e retoma quando ela voltar.

---

## O que este plugin deliberadamente NÃO faz

- **Não** implementa de forma autônoma sem supervisão.
- **Não** usa `bypassPermissions`.
- **Não** faz `push`, deploy ou migration sozinho.
- **Não** marca card como feito porque houve commit.
- **Não** clona o canvas visual do Terminals — a perda é só cosmética.

---

## Desenvolver o plugin

```bash
git clone https://github.com/brunocangussu/byia-claude-orquestra.git
cd byia-claude-orquestra

# apontar o Claude Code pro clone local em vez do GitHub
/plugin marketplace add .
/plugin install orq@orquestra
```

Ao editar, as duas verificações — `claude plugin validate ./orq --strict` (manifesto) e
`python3 orq/scripts/lint-coerencia.py .` (coerência: todo comando/agente/skill citado existe?) —
depois `/plugin marketplace update orquestra` + `/plugin update orq@orquestra`. Para iterar numa
skill, `/reload-plugins` comprovadamente aplica o update na sessão viva (verificado em 2026-07-29);
teste que fecha card exige **reiniciar** — comando, agente, hook, MCP e PATH seguem sem teste (ver
"Problemas conhecidos" abaixo).

**Estrutura:**
```
.claude-plugin/marketplace.json   catálogo
orq/
├── .claude-plugin/plugin.json    manifesto
├── commands/                     os /orq:*
├── agents/                       o time
├── skills/orq/SKILL.md           a disciplina (gatilhos naturais + regras)
├── stack.md                      catálogo da stack complementar (lido por IA)
└── scripts/                      helpers (lint de coerência, guardiões, runners, board)
```

A **skill** é onde se mexe no comportamento geral (quando agir, o que é inviolável). Os **commands**
são cada passo do fluxo. Os **agents** são os papéis.

---

## Status

`0.22.6` — board · time · dois loops · memória-wiki · interface natural · modo noturno (planejamento)
· painel de **três** revisores (Claude + Codex + Kimi) · elenco configurável de LLM por papel · stack complementar
auto-detectada · **auditores offline de remoção e adoção graph-first** · contrato de formato (`_schema.md`) + smoke test na instalação · **protocolo de várias janelas**
· reload vs restart documentado por **evidência por componente**, não regra binária · gatilhos medidos por
corpus real (não inventados) · cardápio por situação (`/orq:ajuda`) · política de iniciativa própria em
**três níveis** (age e relata · propõe, nunca insiste · sempre pergunta) · **perfis de elenco** (`padrao` ·
`economia`) pra trocar o time inteiro por contexto de crédito · correções do painel de três revisores
sobre 0.14.0–0.16.0: teto do N2 numa **cláusula única** (sem regra duplicada) · painel mínimo do
`--rapido` decidido num lugar só (`/orq:revisar`, pela propriedade real — reviewer rebaixado — não
pelo nome do perfil) · template do elenco com heading `Papéis`, revisores externos literais e
auto-cura da seção Perfis em arquivo pré-0.16.0 (ao trocar de perfil ou ajustar um papel — não migra
nota de preset) · **`AGENTS.md` = `CLAUDE.md`, byte-idênticos** (identidade vira gate mecânico no
lint, não mais "dever de sincronizar") · `/orq:init` grava o mesmo bloco `orquestra:start` nos dois
· `/orq:instalar` novo — instala o plugin em si (não só o projeto) nos hosts alternativos do dono,
Codex e Kimi, a partir da mesma fonte já registrada no Claude (`T-026`, passos 1–4) · **elenco
host-agnóstico** (`T-026`, passo 8): `## Times por host` resolve o time de Codex e Kimi na leitura,
sem preset ativável; `## Matriz de invocação` documenta o template por vendor × host com
procedência; o template do `init` gera as duas seções e migra arquivo antigo de forma aditiva;
consumidores resolvem host→papel→executor; no Codex, Manager Sol/high, Planner Sol/ultra,
Implementer Terra/xhigh e painel Opus 5 + Kimi K3; diagnóstico separa plugin instalado/habilitado,
skill carregada e smoke comportamental; painel do Kimi corrigido para a ordem de flags segura
(`-m` antes, `-p` por último) ·
**contratos de contexto para Claude Code e Codex** (`T-043`): no Codex, hooks empacotados observam a telemetria por
sessão, pré-alertam em 55%, recomendam checkpoint durável em 60% e reforçam o alerta em 70%; são
consultivos e nunca bloqueiam a continuação, inclusive no modo Goal; `additionalContext` reafirma
essa regra nas conversas Codex já carregadas. Depois do handshake
`Checkpoint verificado; conversa continua.`, a mesma conversa pode continuar e a **compactação é sempre livre**,
manual ou automática; `SessionStart(source=compact)` reidrata memória, board e
thread. Depois de mais 10 pontos percentuais de uso, outro checkpoint é rearmado consultivamente.
O estado legado `clear_required` migra sem bloquear. Compactação sem checkpoint pede
recuperação sem impedir trabalho, e o modo Goal não depende de banco privado do App; o backstop de
90% continua opt-in. No Claude, o contrato permanece
checkpoint → `Seguro dar /clear.` → `/clear` manual ·
**statusline distribuída** (`T-036`): novo asset `orq/scripts/statusline.sh` — a barra completa do
dono (modelo · effort · contexto · custo · rate-limit 5h · diretório · worktree · branch · board),
achando o `kanban-status.sh` por vizinhança em vez de caminho fixo e degradando para só o board sem
`jq` — e o `init` passa a checar os **três escopos** de settings (local do projeto, compartilhado do
projeto, global do usuário) antes de propor, nunca sobrescrevendo statusline existente em nenhum
deles; a cópia instalada leva marca de versão para re-sync detectável.

**Roadmap:** enforcement por hooks (bloquear tecnicamente pular review) · workflows determinísticos ·
implementação noturna limitada (só após pilotos do modo planejamento) · mais revisores no painel.

## Problemas conhecidos (leia se algo "não funciona")

Todos estes já custaram tempo de verdade. O padrão comum: **a falha é silenciosa** — nada dá erro,
a coisa só não acontece.

### O plugin não reflete o que eu editei

Editar o repositório **não** atualiza o plugin em uso, mesmo com o marketplace apontando para um
diretório local: o que roda é uma cópia em `~/.claude/plugins/cache/`. Feche o ciclo:

```bash
claude plugin marketplace update <marketplace>
claude plugin update <plugin>@<marketplace>
claude plugin list          # confirme versão E escopo
diff -rq ~/.claude/plugins/cache/<mkt>/<plugin>/<versão>/ <dir-fonte-do-plugin>/   # TEM que voltar vazio
```

`claude plugin list` compara **versão**, e o cache é indexado por versão: **versão igual não prova
conteúdo igual** — quem edita sem bumpar deixa o cache stale com o `list` dizendo que está tudo
certo. Com marketplace local (`Source: Directory`, visível em `claude plugin marketplace list`), o
`diff` fecha esse buraco: não-vazio = bump e repita o ciclo.

O que o `/reload-plugins` aplica numa sessão viva, por componente — a doc já errou aqui nos dois
sentidos (0.10.0 afirmou demais, 0.11.0 negou demais), então o vocabulário é de evidência, não de
regra:

| Componente | `/reload-plugins` aplica o update de cache? |
|---|---|
| skill | ✅ **observado 1×** (2026-07-29) — após `claude plugin update`, a sessão viva passou a servir a skill nova, sem restart |
| comando · agente | ❓ **não testado** — presuma restart até alguém repetir o teste acima com eles |
| hook · MCP server · PATH | ❓ **não testado** — presuma restart; o `claude plugin update --help` manda reiniciar, mas o caso da skill provou que esse aviso é conservador |
| arquivo lido em runtime (`stack.md`, `scripts/`) | ❓ **não testado** — presuma restart |

**A regra operacional não muda:** teste comportamental que fecha card só vale após **restart** +
`diff` vazio — enquanto comando e agente não forem testados, a sessão pós-reload pode estar mista
(skill nova, resto indeterminado). Novo dado? Atualize **uma célula** desta tabela, não a regra
inteira. Um plugin em **escopo `project`** não vale nos outros projetos: reinstale com escopo de
usuário.

Sonda pendente (custo: uma invocação): no próximo release que alterar `orq/commands/*` ou
`orq/agents/*`, rodar `/reload-plugins` na sessão viva e invocar o comando/agente alterado
procurando o texto novo. Apareceu → a célula vira ✅; não apareceu → vira "exige restart".

### Um revisor sumiu do painel sem avisar

Quase sempre é o binário fora do PATH, não ausência. `which` responde sobre o PATH **daquela
sessão** — instaladores costumam escrever no `.zshrc`, o que só alcança shell aberto depois. Detecte
com fallback:

```bash
KIMI=$(command -v kimi || echo "$HOME/.kimi-code/bin/kimi")
```

O `/orq:revisar` avisa quando o painel fica parcial. Se ele entregar parecer de um revisor **sem**
dizer que faltou alguém, é bug — reporte.

### O revisor externo trava e nunca responde

Falta `< /dev/null`. Sem TTY, tanto `codex exec` quanto `kimi -p` **bloqueiam lendo stdin** e travam
até o timeout — mesmo com o prompt passado como argumento. Com o stdin fechado, respondem em
segundos.

### A statusline está muda / o progresso não aparece

Card fora do formato do board. O parser lê **por posição** e é estrito de propósito:

```
- [ ] `T-001` Título curto — nota livre
```

O ID **precisa** das crases — são elas que distinguem card de item de checklist. O que quebra é
**envolver**: negrito/itálico em volta do marcador (`**- [ ]**`) ou negrito/crase por fora do ID
já com crases. Rode
`sh <plugin>/scripts/kanban-status.sh .` e confira **três sinais**: saída vazia · `⚠N` no fim ·
denominador diferente do número de cards que você escreveu. **Saída não-vazia não prova que está
certo.** O contrato completo fica em `memory/wiki/_schema.md`.

### Ele implementa direto em vez de planejar

O ciclo dispara por reconhecimento de intenção. Se um pedido seu não for reconhecido como pedido de
mudança, ele vai direto ao código — sem plano e sem gate. Diga *"planeja isso primeiro"* e, se
repetir, o gatilho está faltando: vale abrir issue com a frase exata que você usou.

### Não confie em `--help | head` para concluir que algo não existe

Listas de comando são alfabéticas e `head` corta no meio. Verifique o comando específico
(`claude plugin update --help`) antes de afirmar ausência — especialmente se a conclusão levar a
desligar uma capacidade ou instalar algo.

---

## Licença

MIT
