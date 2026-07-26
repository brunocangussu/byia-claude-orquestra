# Orquestra

Plugin do Claude Code para **desenvolvimento orientado a board** com time de agentes efêmeros,
memória-wiki durável e gates humanos.

Nasceu da arquitetura que o Alison montou no app Terminals (canvas de terminais multi-agente),
redesenhada para as primitivas nativas do Claude Code — sem canvas, sem agentes residentes,
sem `bypassPermissions`.

## Você não digita comandos

O plugin foi feito pra ser usado **conversando**. Você fala naturalmente e o Claude reconhece a
intenção:

| Você diz | Acontece |
|---|---|
| *"onde paramos?"* | mostra o board |
| *"terminamos, pode limpar"* | salva tudo na memória e libera o `/clear` |
| *"vamos planejar isso"* | planeja e traz pra você aprovar |
| *"pode implementar"* | implementa, revisa e documenta |
| *"anota isso"* | vira card no backlog |
| *"vou dormir, adianta o que der"* | modo noturno |

Os comandos `/orq:*` existem como mecanismo — use se quiser, mas não precisa.

## A ideia em uma frase

> **Contexto é descartável. O estado do trabalho vive no board e nos artefatos.**

A janela pode morrer a qualquer momento. Se o estado só existe no chat, ele se perde — por isso todo
passo termina gravando no board (`memory/wiki/KANBAN.md`) e na wiki (`memory/wiki/`).

## Instalar

```bash
# 1. registrar o marketplace (uma vez por máquina)
/plugin marketplace add ~/Projetos\ DEV\ -\ Cursor/claude-orquestra

# 2. instalar
/plugin install orq@orquestra
/reload-plugins

# 3. montar no projeto (uma vez por projeto)
/orq:init
```

O `/orq:init` **inspeciona o projeto** — stack, domínio, convenções, docs que já existem,
trabalho em aberto e quais ferramentas estão disponíveis (MCPs, busca semântica, claude-mem,
context-mode) — e **propõe** o time e a estrutura sob medida. Nada é escrito antes da sua aprovação.

Rodar de novo é seguro: ele completa o que falta e relata o que ignorou.

## O ciclo

```
/orq:plan-next      → planeja o próximo card e traz pra você aprovar
        ↓ (você aprova)
/orq:implement-next → implementa + review independente + docs → fica pra você validar
        ↓
/orq:checkpoint     → grava tudo na memória durável
        ↓
/clear                    → esvazia a janela; a próxima retoma pelo board
```

## Comandos

| Comando | O que faz |
|---|---|
| `/orq:init` | Instala e **adapta** o Orquestra a este projeto |
| `/orq:plan-next` | Loop A — planeja o próximo card (gate humano no fim) |
| `/orq:implement-next` | Loop B — implementa com review e documentação |
| `/orq:quadro` | Mostra o board: o que espera você, o que está em curso, o progresso |
| `/orq:checkpoint` | Fecha o bloco de trabalho na memória (rode antes do `/clear`) |
| `/orq:wiki-lint` | Health-check da wiki: contradições, páginas órfãs, afirmações vencidas |
| `/orq:lembrar` | Busca na memória de longo prazo (Supermemory) |
| `/orq:dormir` | Modo noturno — adianta planejamento enquanto você dorme |
| `/orq:acordar` | Relatório do modo noturno, com as perguntas numeradas |

## O time

Todos são **spawns frescos** — nunca reaproveitados entre cards.

| Agente | Papel | Escrita |
|---|---|---|
| `orq-scout` | Investiga território novo e relata | ❌ read-only |
| `orq-planner` | Acha a causa raiz e desenha o plano | só o arquivo do plano |
| `orq-implementer` | Implementa o plano aprovado | ✅ |
| `orq-reviewer` | Revisa de forma adversarial | ❌ read-only (aponta, não corrige) |
| `orq-docs` | Documenta o código final + atualiza a wiki | ✅ docs |

**O Manager é a sessão principal** — não é um subagente. Só ele move cards e fala com você.

## O board

`memory/wiki/KANBAN.md`. O estado de cada card é o marcador da linha:

| | |
|---|---|
| `[ ]` | backlog |
| `[>]` | planejando |
| `[!]` | **esperando você** (estacionamento — sai da fila, não a trava) |
| `[~]` | aprovado / implementando |
| `[?]` | aguardando sua validação |
| `[x]` | feito |

O `[!]` é a peça mais importante: um card que precisa de decisão **não bloqueia os outros**.

## A memória

| Arquivo | Papel |
|---|---|
| `memory/MEMORY.md` | Índice — leia primeiro |
| `memory/wiki/<tópico>.md` | Como funciona **hoje** (reescrita quando muda) |
| `memory/wiki/threads/` | Trabalho em curso, com "RETOMAR AQUI" |
| `memory/fixes-history.md` | Log cronológico, append-only |
| `memory/gotchas.md` | Armadilhas que já causaram bug |

**A distinção que faz funcionar:** o log responde *"o que aconteceu naquele dia"*; a página de tópico
responde *"como funciona hoje"*. Sem a página, responder a segunda pergunta vira arqueologia no log.

## O que este plugin deliberadamente NÃO faz

- **Não** roda implementação autônoma sem supervisão. Trabalho noturno, quando existir, começa só
  por planejamento e triagem, com orçamento e limites.
- **Não** usa `bypassPermissions`.
- **Não** faz `push`, deploy ou migration sozinho.
- **Não** marca card como feito porque houve commit — commit não é critério de pronto.

## Modo noturno

*"Vou dormir, adianta o que der"* → o Orquestra **planeja** os próximos cards do backlog enquanto
você dorme e **estaciona** o que precisar de decisão sua, com a pergunta exata escrita no card.
De manhã, *"bom dia"* traz o relatório com as perguntas numeradas — você responde "1-sim, 2-a
segunda opção" e destrava a fila inteira de uma vez.

**Limites duros:** 3 cards e 4 horas por padrão · para após 2 rodadas sem progresso · **só
planejamento, nunca implementação** · nunca toca em schema, segurança, deploy, dependência ou
qualquer coisa irreversível — esses ficam pra quando você acordar.

⚠️ **Limitação honesta:** a sessão do Claude Code precisa ficar **aberta** (máquina ligada, sem
suspender). Não existe execução realmente desacompanhada dentro do CLI — se a máquina dormir, o
trabalho pausa e retoma quando ela voltar.

## Status

`0.2.0` — núcleo funcional: board, time, dois loops, memória, **interface natural** e **modo
noturno (planejamento)**.
Ainda não implementado: enforcement por hooks, workflows determinísticos e implementação noturna
(só depois de pilotos bem-sucedidos do modo planejamento).

## Licença

MIT
