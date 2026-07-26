# Arquitetura do Orquestra

> Como o plugin funciona **hoje**. Reescrever esta página quando o desenho mudar — não acumular
> histórico aqui (isso é `fixes-history.md`).

## O princípio

> **Contexto é descartável. O estado do trabalho vive no board e nos artefatos.**

A janela pode morrer a qualquer momento — e vai. Se o estado só existe no chat, perde-se. Por isso
todo passo termina gravando no board e na wiki. É isso que elimina a necessidade de encadear
`/compact` para "não perder o raciocínio".

## Control plane vs. workers

O núcleo não é "multi-agente" — é a **separação entre quem decide e quem executa**.

| Papel | Quem é | Contexto |
|---|---|---|
| **Manager** | a **sessão principal** | persistente — retém o fio da meada |
| Planner · Implementer · Reviewer · Docs · Scout | subagentes | **fresco a cada card** |

**Por que o Manager não é subagente:** existe exatamente um lugar que move cards e fala com o dono.
Se fosse spawn, haveria duas fontes de verdade sobre "onde estamos". Veio direto da fonte original —
no Terminals o Manager é separado do canvas.

**Por que os workers nascem frescos:** contexto contaminado faz o agente arrastar premissas da tarefa
anterior. No Claude Code cada spawn é contexto novo, então isso é de graça.

## Máquina de estados

```
BACKLOG → PLANNING → [gate do dono] → READY → DEV_REVIEW → VALIDATE → DONE
                          ↓
                    AWAITING_OWNER  (estacionamento: sai da fila, não a trava)
```

| Marcador | Estado | Significa |
|---|---|---|
| `[ ]` | BACKLOG | esperando entrar na fila |
| `[>]` | PLANNING | Planner trabalhando |
| `[!]` | AWAITING_OWNER | precisa de decisão do dono — **a pergunta exata fica escrita no card** |
| `[~]` | READY / DEV_REVIEW | aprovado e em implementação |
| `[?]` | VALIDATE | implementado, aguardando validação prática |
| `[x]` | DONE | validado e fechado |

**`[!]` é a peça que sustenta o desenho.** Card que precisa de decisão sai da fila em vez de travá-la.
Sem ele o modo noturno seria uma fila que morre no primeiro card ambíguo.

O board é a fonte da verdade — **não** a TaskList nativa, que só tem pending/in-progress/completed e
não representa os gates.

## As regras invioláveis

1. **Handoff antes de encerrar** — objetivo · escopo · decisões com o porquê · o que faltou · dúvidas.
2. **Causa raiz, nunca sintoma** — catch silencioso e retry cego são rejeitados no review.
3. **Autocrítica antes de entregar** — "o que estou assumindo sem verificar?"
4. **Escopo tem borda** — mesma causa raiz e mesmo subsistema: pode. Schema, API pública, segurança
   ou outro módulo: card novo.
5. **Documentação é atemporal** — descreve como é agora, nunca "mudamos de X para Y".
6. **Review é read-only** — quem revisa aponta; quem implementou aplica.
7. **Um dono por arquivo** — tarefa que escreve roda em worktree próprio.
8. **Nada de `bypassPermissions`** — nem de dia, nem de noite.
9. **Commit não é critério de pronto** — card fecha em VALIDATE; o dono confirma usando o produto.

⚠️ **Estado atual do enforcement: nenhum.** As nove regras acima são texto de prompt, não ACL. Não há
um único hook declarado no plugin. É o que os cards `T-001` e `T-002` atacam.

## O que foi deliberadamente recusado

O desenho nasceu do app **Terminals** (canvas de terminais multi-agente, do Alison) e passou por
revisão adversarial do Codex, cujo veredito foi *"aprovar com redesenho"*: ~80-90% do comportamento
útil é reproduzível nas primitivas nativas, mas **não** se copia:

| Recusado | Por quê |
|---|---|
| O canvas visual | a perda é só cosmética |
| Agentes residentes | contradiz o worker fresco por card |
| `bypassPermissions` | o gate humano é o produto, não um obstáculo |
| Implementação autônoma sem supervisão | idem |
| Fechar card por commit | commit não prova que funciona |

## Limitações conhecidas — não prometer o que não dá

- **Cron é session-scoped.** Não existe execução desacompanhada dentro do CLI. O modo noturno exige
  sessão aberta e máquina ligada; se ela suspender, o trabalho pausa e retoma depois.
- **`manager` não é configurável** pelo elenco — é a sessão principal, definida pelo `/model`.
- **Agent teams são experimentais**, mais caros e não isolam arquivos automaticamente.
- **"Só o Manager move cards" pode não ser enforçável por hook** como o parecer supõe: depende de o
  payload distinguir subagente da sessão principal, o que ainda não foi verificado (ver `T-002`).
