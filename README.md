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
| *"terminamos, pode limpar"* | salva tudo na memória e libera o `/clear` |
| *"vamos planejar isso"* | planeja e **para** pra você aprovar |
| *"pode implementar"* · *"manda ver"* | implementa + revisa + documenta |
| *"anota isso"* · *"não esquece disso"* | vira card no backlog |
| *"revisa isso aí"* | painel de revisores (Claude + Codex) |
| *"lembra o que decidimos sobre X?"* | busca na memória de longo prazo |
| *"vou dormir, adianta o que der"* | modo noturno |
| *"bom dia"* | relatório do que rodou à noite |

Os comandos `/orq:*` existem como mecanismo. Use se quiser, mas não precisa.

---

## Instalar

```bash
# 1. registrar o marketplace (uma vez por máquina)
/plugin marketplace add brunocangussu/byia-claude-orquestra

# 2. instalar (escopo de usuário = vale em todos os projetos)
/plugin install orq@orquestra
/reload-plugins

# 3. montar no projeto (uma vez por projeto)
/orq:init
```

### O que o `/orq:init` faz

Ele **se adapta ao projeto** — não despeja estrutura genérica:

1. **Investiga** (agentes em paralelo): stack, domínio, convenções, o que quebra o deploy, docs que
   já existem, TODO/FIXME espalhados, testes quebrados.
2. **Detecta o ferramental real**: MCPs conectados, se o repo já está indexado para busca semântica,
   se há claude-mem / context-mode / Supermemory.
3. **Decide o time sob medida** — *"tem 90 migrations e RLS → vale um agente de dados"*. Se o projeto
   já tem agentes bons, **reaproveita** em vez de duplicar.
4. **Propõe e espera** sua aprovação. Nada é escrito antes.
5. **Monta**: memória + board com o **backlog real que encontrou** + agentes + bloco no `CLAUDE.md`
   e no `AGENTS.md`.

É idempotente: rodar de novo completa o que falta e relata o que ignorou.

---

## O ciclo

```
  planejar  ──→  [ VOCÊ APROVA ]  ──→  implementar  ──→  [ VOCÊ VALIDA ]  ──→  feito
     ↑                                       │
     └───────────  checkpoint + /clear  ←────┘
```

| Comando | O que faz |
|---|---|
| `/orq:init` | Instala e **adapta** o Orquestra ao projeto |
| `/orq:plan-next` | **Loop A** — planeja o próximo card e para no gate |
| `/orq:implement-next` | **Loop B** — implementa + painel de revisão + documentação |
| `/orq:revisar` | Painel de revisores sobre a mudança atual |
| `/orq:quadro` | Mostra o board e o progresso |
| `/orq:checkpoint` | Fecha o bloco de trabalho na memória (antes do `/clear`) |
| `/orq:wiki-lint` | Health-check da wiki: contradições, órfãs, afirmações vencidas |
| `/orq:lembrar` | Busca na memória de longo prazo (Supermemory) |
| `/orq:dormir` | Modo noturno — adianta planejamento |
| `/orq:acordar` | Relatório do modo noturno |

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

### Acrescentar um revisor (ex.: Kimi K2)

Crie `memory/wiki/_revisores.md` no projeto:

```markdown
# Revisores do painel

## kimi-k2
- como chamar: <comando CLI ou ferramenta MCP>
- perfil: <no que ele é bom — ex.: raciocínio longo, código de sistema>
- read-only: sim
```

O `/orq:revisar` lê esse arquivo e inclui os revisores registrados. **Kimi K2 ainda não está
instalado** nesta máquina (sem CLI e sem MCP) — quando estiver, basta registrar aqui.

Em card pequeno e de baixo risco, use `--rapido` (só o revisor interno). Painel em mudança trivial
é desperdício.

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

Ao editar: `claude plugin validate ./orq --strict`, depois
`/plugin marketplace update orquestra` + `/reload-plugins`.

**Estrutura:**
```
.claude-plugin/marketplace.json   catálogo
orq/
├── .claude-plugin/plugin.json    manifesto
├── commands/                     os /orq:*
├── agents/                       o time
├── skills/orq/SKILL.md           a disciplina (gatilhos naturais + regras)
└── scripts/                      helpers (busca na memória, progresso do board)
```

A **skill** é onde se mexe no comportamento geral (quando agir, o que é inviolável). Os **commands**
são cada passo do fluxo. Os **agents** são os papéis.

---

## Status

`0.3.0` — board · time · dois loops · memória-wiki · interface natural · modo noturno (planejamento)
· painel de revisores.

**Roadmap:** enforcement por hooks (bloquear tecnicamente pular review) · workflows determinísticos ·
implementação noturna limitada (só após pilotos do modo planejamento) · mais revisores no painel.

## Licença

MIT
