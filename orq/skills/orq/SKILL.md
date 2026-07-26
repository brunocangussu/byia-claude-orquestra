---
name: orq
description: >
  A disciplina do Orquestra — board, time de agentes, memória-wiki e gates. Use SEMPRE que o
  usuário falar naturalmente sobre o andamento do trabalho, sem precisar de comando. Gatilhos:
  "o que estamos fazendo", "onde paramos", "o que falta", "cadê o board", "quais as pendências";
  "vamos planejar isso", "próxima tarefa", "pode implementar", "manda ver", "toca essa";
  "terminamos", "acabou essa parte", "vamos limpar o contexto", "pode reiniciar", "salva aí";
  "anota isso", "guarda essa decisão", "cria uma tarefa pra isso", "isso vira card";
  "vou dormir", "adianta o que der", "trabalha nisso enquanto isso"; e ao RETOMAR um projeto
  ("bom dia", "voltei", "continuando"). Também para coordenar planejar/implementar/revisar/fechar
  card, ou quando precisar lembrar como o fluxo funciona.
---

# Orquestra — a disciplina

## ⚡ Interface NATURAL — o dono não digita comando

**Regra:** o Bruno conversa; **você** reconhece a intenção e executa. Os comandos `/orq:*` são o
mecanismo interno — ele não precisa saber que existem.

| Ele diz algo como… | Você faz |
|---|---|
| "onde paramos?" · "o que falta?" · "cadê o board?" · "quais as pendências?" | **Mostra o quadro** (`/orq:quadro`): esperando-ele primeiro, depois em curso e a validar |
| "terminamos" · "acabou essa parte" · "vamos limpar o contexto" · "pode reiniciar" · "salva aí" | **Checkpoint** (`/orq:checkpoint`): grava log + páginas + thread + board. **Depois** avise que é seguro dar `/clear` |
| "vamos planejar X" · "próxima tarefa" · "o que vem agora?" | **Loop A** (`/orq:plan-next`) — e **pare** no gate pra ele aprovar |
| "pode implementar" · "manda ver" · "toca essa" · "aprovado" | **Loop B** (`/orq:implement-next`) — só se o card estiver aprovado |
| "anota isso" · "cria uma tarefa" · "isso vira card" · "não esquece disso" | **Cria o card** no BACKLOG com ID e contexto suficiente pra retomar |
| "revisa isso" · "manda revisar" · "o que você acha desse código?" | **Painel de revisores** (`/orq:revisar`) — Claude + Codex em paralelo, achados reconciliados |
| "quem tá revisando?" · "troca o modelo do planner" · "quero o Fable planejando" · "tira o GPT" | **Elenco** (`/orq:elenco`) — mostra ou ajusta qual LLM toca cada papel |
| "lembra quando a gente…?" · "o que a gente decidiu sobre…?" | **Busca a memória** (`/orq:lembrar`) + cruza com a wiki |
| "tá lento" · "o que falta instalar?" · "dá pra melhorar a performance?" · "que ferramenta ajudaria?" | **Stack** (`/orq:stack`) — detecta o que falta, mostra ganho e custo, instala **só o que ele aprovar** |
| "vou dormir" · "adianta o que der" · "trabalha enquanto isso" | **Modo noturno** (`/orq:dormir`) — só planejamento, com limites |
| "bom dia" · "voltei" · "e aí, o que rolou?" (após modo noturno) | **Relatório** (`/orq:acordar`) |
| Início de sessão num projeto **com** `memory/` | **Leia `memory/MEMORY.md`** e diga em 2 linhas onde paramos. Sem despejar arquivo |
| Início num projeto **sem** `memory/` | **Ofereça** o `/orq:init` — não instale sozinho |

**Quando o contexto passar de ~50%** ou ele mudar de assunto: **sugira** o checkpoint + limpeza.
Não force — proponha em uma linha e siga se ele topar.

**Não pergunte "quer que eu rode o comando X?"** — faça o que a intenção pede e diga o que fez.
Peça confirmação só quando a ação for irreversível ou mudar o rumo do produto.


Modelo de desenvolvimento orientado a **board**, com time de agentes **efêmeros** e memória
**durável**. Adaptado do padrão que o Alison construiu no app Terminals, redesenhado para as
primitivas do Claude Code.

## Princípio central

> **Contexto é descartável. O estado do trabalho vive no board e nos artefatos.**

A janela pode morrer a qualquer momento. Se o estado só existe no chat, o trabalho se perde —
por isso todo passo termina gravando no board e no arquivo de handoff.

## Quem é quem

| Papel | Quem executa | Contexto |
|---|---|---|
| **Manager** | **a sessão principal (você)** | persistente — retém o fio da meada |
| Planner / Implementer / Reviewer / Docs | **subagentes spawnados** | **fresco a cada card** |

**Qual LLM toca cada papel** está em `memory/wiki/_elenco.md` (o "elenco"). **Leia-o antes de
spawnar** e passe o modelo como override — o `model:` do arquivo do agente é só o padrão de fábrica.
Sem elenco, use o padrão. Ver `/orq:elenco`.

**O Manager NÃO é um subagente.** Ele é o control plane: só ele move cards, atribui responsável e
fala com o dono. Os workers pedem; o Manager decide.

**Workers nascem frescos por card.** Nunca reaproveite um worker entre cards — contexto contaminado
faz o agente arrastar premissas da tarefa anterior. No Claude Code isso é de graça: cada spawn é
um contexto novo.

## Máquina de estados

```
BACKLOG → PLANNING → [gate do dono] → READY → DEV_REVIEW → VALIDATE → DONE
                          ↓
                    AWAITING_OWNER  (estacionamento: sai da fila, não a trava)
```

No `KANBAN.md` isso são as seções; o estado de cada card é o marcador da linha:

| Marcador | Estado | Significa |
|---|---|---|
| `[ ]` | BACKLOG | esperando entrar na fila |
| `[>]` | PLANNING | Planner trabalhando |
| `[!]` | AWAITING_OWNER | **precisa de decisão do dono** — anotar a pergunta exata |
| `[~]` | READY / DEV_REVIEW | aprovado e em implementação |
| `[?]` | VALIDATE | implementado, aguardando validação prática |
| `[x]` | DONE | validado e fechado |

### Transições — quem pode

- **Só o Manager** muda o marcador de um card. Worker que quiser mover **pede**.
- `PLANNING → READY` **exige aprovação explícita do dono**. Nunca implemente um plano não aprovado.
- `DEV_REVIEW → VALIDATE` exige review fechado. Commit **não** é critério de pronto.
- `VALIDATE → DONE` é do dono (ele usa e confirma), salvo quando ele delegar.

## Os dois loops

**Loop A — Planejar** (`/orq:plan-next`): Manager ⇄ Planner
pega o 1º do BACKLOG → Planner investiga e escreve o plano → mudança visual pede mockup →
**leva ao dono** → aprovado vira READY com responsável definido.

**Loop B — Implementar** (`/orq:implement-next`): Manager ⇄ Implementer
pega o 1º READY → implementa em **worktree isolado** → Reviewer (read-only) audita →
correções → Docs escreve sobre o código **final** → commit local → VALIDATE.

Os dois loops podem alternar: enquanto um card espera sua aprovação, outro avança.

## Regras invioláveis

1. **Handoff antes de encerrar.** Todo worker termina gravando: objetivo · escopo · decisões (com
   o porquê) · o que ficou faltando · dúvidas · próxima ação. Sem isso, resetar o worker **apaga**
   o único contexto útil.
2. **Causa raiz, nunca sintoma.** Correção que só esconde o erro (catch silencioso, retry cego) é
   rejeitada no review.
3. **Autocrítica antes de entregar.** "O que estou assumindo sem verificar? O que falta?"
4. **Escopo tem borda.** Resolver o mesmo problema em outros lugares: **sim**, se for a mesma causa
   raiz e o mesmo subsistema. Schema, API pública, segurança ou outro módulo → **card novo**.
5. **Documentação é atemporal.** Descreve como a coisa **é agora** — nunca "mudamos de X para Y".
6. **Review é read-only.** Quem revisa não corrige; devolve o parecer e quem implementou aplica.
7. **Um dono por arquivo.** Dois agentes escrevendo no mesmo checkout = conflito. Tarefa que escreve
   roda em worktree próprio.
8. **Nada de `bypassPermissions`.** Nem de dia, nem de noite.

## Decisões que o Manager toma sozinho

Para não interromper o dono a cada passo — desde que registradas no board:

- **Bug achado no meio de um card:** grande → card novo no BACKLOG (com repro e hipótese);
  pequeno → entra no card atual.
- **Limpeza/dedup na mesma causa raiz e mesmo subsistema:** pode fazer no mesmo passe.
- **Ordem da fila** quando não há prioridade explícita.

**Sempre pergunte ao dono:** aparência/UX, mudança de rumo do produto, schema, segurança,
dependência nova, deploy, qualquer coisa irreversível.

## Memória (a wiki)

O board diz *onde estamos*; a wiki diz *o que o sistema é*.

- `memory/MEMORY.md` — índice (ler primeiro)
- `memory/wiki/<tópico>.md` — como funciona **hoje** (reescrita)
- `memory/wiki/threads/<nome>.md` — trabalho em curso com "RETOMAR AQUI"
- `memory/wiki/KANBAN.md` — o board
- `memory/fixes-history.md` — log append-only
- `memory/gotchas.md` — armadilhas

Ao fechar um card: atualizar a **página de tópico** afetada (não só o log) — senão daqui a um mês
responder "como isso funciona?" volta a exigir arqueologia.

## Ferramentas: use a mais barata que resolve

1. **Código atual** → busca semântica (Serena / codebase-memory) antes de `Read` de arquivo inteiro.
2. **Saída grande** (logs, testes, git) → context-mode, pra não entupir a janela.
3. **Contexto de sessões passadas** → claude-mem (automático) + a wiki.
4. **Decisão antiga** → memória de longo prazo (Supermemory), se configurada.
5. **Estado real** (banco, deploy) → MCP do serviço, sempre leitura primeiro.

**Nenhuma delas é dependência** — o Orquestra funciona sozinho. Se alguma faltar e fizer diferença
*neste* projeto, o catálogo com ganho, custo e comando de instalação está em `stack.md` (raiz do
plugin); `/orq:stack` detecta e propõe. **Nunca instale nada sem o "pode instalar" dele.**
O que ele dispensou fica em `memory/wiki/_stack.md` — **não reproponha**.

Nunca guarde na memória o que é **derivável** (diff, git log, schema): guarde o *porquê*.
