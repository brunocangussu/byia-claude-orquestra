---
name: orquestra
description: A disciplina do Orquestra — máquina de estados do board, papéis do time, regras de handoff e gates. Use ao coordenar trabalho com o board (planejar, implementar, revisar, concluir card) ou quando precisar lembrar como o fluxo funciona.
---

# Orquestra — a disciplina

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

**Loop A — Planejar** (`/orquestra:plan-next`): Manager ⇄ Planner
pega o 1º do BACKLOG → Planner investiga e escreve o plano → mudança visual pede mockup →
**leva ao dono** → aprovado vira READY com responsável definido.

**Loop B — Implementar** (`/orquestra:implement-next`): Manager ⇄ Implementer
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

Nunca guarde na memória o que é **derivável** (diff, git log, schema): guarde o *porquê*.
