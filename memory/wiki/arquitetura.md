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

⚠️ **Enforcement: quase nenhum.** As nove regras são texto de prompt, não ACL — o plugin não declara
um único hook (`T-001`, `T-002`). O que existe de verificação **determinística** hoje:

| Verificação | Pega |
|---|---|
| `claude plugin validate --strict` | manifesto malformado |
| `orq/scripts/lint-coerencia.py` | comando/agente/skill/arquivo citado que não existe · versão divergindo entre os **quatro** lugares (manifesto, README, `MEMORY.md`, `marketplace.json`) · **edição sem bump com o cache já publicado** |
| `orq/scripts/kanban-status.sh` | card fora do contrato do board (sinaliza `⚠N`) — cobre negrito, itálico, crase e tachado em volta do marcador, e os três bullets do CommonMark |
| `/orq:stack --verificar` | plugin desatualizado **ou cache stale** (versão *e* conteúdo), escopo errado, revisor ausente, board ilegível (três sinais) |

Nenhuma delas **impede** nada — todas só relatam. Bloquear de verdade continua sendo o `T-001`.

**O cache é indexado por versão.** `~/.claude/plugins/cache/<mkt>/<plugin>/<versão>/` — editar `orq/`
sem bumpar **não muda o que roda**, e o `claude plugin list` continua dizendo que está tudo certo.
Aconteceu no `5b75296` e invalidou retroativamente todo teste comportamental feito depois. Por isso
o guarda no lint e o `diff -rq` como fecho do ciclo de release: **versão igual não prova conteúdo
igual**. Comparar versão é fonte única, e fonte única foi o padrão de erro mais caro deste projeto.

**Só o Codex tem sandbox.** `codex exec -s read-only` é garantia; o Kimi **não tem flag equivalente**
e o prompt "não edite nada" é pedido, não ACL — ele rodou `git checkout -- .` numa revisão read-only
e destruiu o working tree (2026-07-28). Revisor sem sandbox precisa de **worktree descartável**, não
de instrução (`T-019`). É a mesma lição do `T-001`, cobrada no próprio repo.

## Roteamento automático (o dono não digita comando)

**Todo pedido de mudança entra pelo ciclo.** *"quero X"*, *"vamos acrescentar Y"*, *"tem um problema
em Z"* não são pedidos de código — são pedidos de **plano**. A escala dimensiona pelo risco: trivial
vai direto; pequeno leva revisor interno; normal roda o ciclo completo; alto risco ganha gate extra.
Na dúvida, sobe um nível.

**O modo de falha é conhecido e nomeado:** o pedido chega em linguagem natural, parece pequeno, e o
Manager começa a editar — sem plano, sem gate, com o painel entrando só depois, revisando o que já
está pronto. Aconteceu em toda a sessão de 26-28/jul, incluindo features inteiras, porque a
`description` da skill tinha **0% de cobertura** sobre a fala real do dono.

## Trabalho em várias janelas

O dono abre uma janela por frente. Como o desenho pressupõe **um** Manager, N janelas se
sobrescreviam em silêncio. O protocolo (em `_schema.md`): uma janela = uma frente · releia antes de
escrever · **edite a linha, nunca o arquivo** · card em curso leva `@frente`.

**O diagnóstico que definiu a solução:** a concorrência não é o problema — **a reescrita é**. Duas
janelas alterando linhas diferentes, cada uma relendo antes, praticamente não colidem. Por isso não
há lock: lock mataria o paralelismo que motiva as N janelas.

E o ganho maior não é a trava: **pendência de decisão vira card `[!]` e a janela pode fechar.** Antes
ela ficava viva só como memória de pendência.

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
