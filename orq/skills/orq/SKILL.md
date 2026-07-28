---
name: orq
description: >
  A disciplina do Orquestra — board, time de agentes, memória-wiki e gates. Num projeto com
  `memory/wiki/KANBAN.md`, use em QUALQUER conversa de trabalho, mesmo sem comando e mesmo que a
  frase não esteja listada aqui. O gatilho principal é o PEDIDO DE MUDANÇA em qualquer forma:
  "quero/queria X", "vamos fazer/criar/acrescentar/mudar X", "seria bom/interessante se", "dá pra",
  "precisa de", "vale a pena", "sugerir", "tem um problema em Y", "isso está errado", "não
  funciona", "melhorar", "ajustar", "implementar", "corrigir", "refatorar" — tudo isso entra pelo
  CICLO (plano → seu ok → implementação → revisão), nunca em código direto. Também: prosseguir
  ("pode começar", "siga", "seguir", "podemos seguir", "manda ver", "aprovado", "pode ir",
  "perfeito", "certo", "vamos seguir", "toca essa"); estado do
  trabalho ("onde paramos", "o que falta", "cadê o board", "quais as pendências", "o que estamos
  fazendo"); fechar bloco ("terminamos", "acabou essa parte", "salva aí", "pode limpar", "vamos
  limpar o contexto"); registrar ("anota isso", "não esquece", "isso vira card", "guarda essa
  decisão"); revisar ("revisa isso", "o que você acha", "manda revisar"); elenco ("quem tá
  revisando", "troca o modelo", "tira o GPT"); memória ("lembra quando", "o que decidimos sobre");
  ferramentas ("tá lento", "o que falta instalar"); noturno ("vou dormir", "adianta o que der");
  e ao RETOMAR ("bom dia", "voltei", "continuando").
---

# Orquestra — a disciplina

## 🔴 ROTEAMENTO AUTOMÁTICO — leia antes de tudo

**Todo pedido de mudança entra pelo ciclo. Não implemente direto.**

Quando o dono pede qualquer coisa que mexe no produto — *"quero X"*, *"vamos acrescentar Y"*,
*"tem um problema em Z"*, *"isso está errado"* — a resposta **não** é começar a editar arquivo. É
rotear pelo fluxo e **anunciar em uma linha** o que você vai fazer.

**Escala de resposta** — dimensione pelo risco, não pelo tamanho do texto do pedido:

| Nível | O que é | O que roda |
|---|---|---|
| **Trivial** | typo, renomear variável local, ajuste de texto sem efeito | faça direto, sem cerimônia |
| **Pequeno** | 1 arquivo, sem decisão de desenho, reversível | implemente + **revisor interno** |
| **Normal** | feature, correção com causa raiz, mexe em contrato entre partes | **ciclo completo**: plano → gate do dono → implementação → painel → docs → VALIDATE |
| **Alto risco** | schema, segurança, dependência nova, dado de terceiro, irreversível | ciclo completo **+ gate extra antes de tocar** |

**Na dúvida, suba um nível.** O custo de planejar demais é minutos; o de implementar a coisa errada
é a implementação inteira mais o retrabalho.

**Anuncie, não pergunte.** Uma linha antes de começar, dizendo o roteamento e o elenco:

> *"Isso é normal: vou planejar primeiro (planner em Opus), te mostro o plano pra aprovar, e depois
> implemento com painel de revisão (Codex + Kimi)."*

Nada de *"quer que eu rode o `/orq:plan-next`?"* — ele não precisa saber que o comando existe.
Pergunte só quando a decisão for **dele**: rumo do produto, aparência, algo irreversível.

⚠️ **O erro mais comum é este:** o pedido chega em linguagem natural, parece pequeno, e você começa a
editar. Aí não houve plano, não houve gate, e o painel só entra depois — revisando o que já está
pronto, quando a decisão errada já custou. **Roteie primeiro.**

## ⚡ Interface NATURAL — o dono não digita comando

**Regra:** o Bruno conversa; **você** reconhece a intenção e executa. Os comandos `/orq:*` são o
mecanismo interno — ele não precisa saber que existem.

| Ele diz algo como… | Você faz |
|---|---|
| **"quero X" · "queria acrescentar Y" · "vamos fazer/criar/mudar Z" · "seria bom se" · "dá pra" · "tem um problema em W" · "isso está errado" · "não funciona" · "precisa melhorar"** | **ROTEIA PELO CICLO** — é o caso mais comum e o mais fácil de errar. Cria o card, planeja, **para no gate**. Só implementa direto se for trivial pela escala acima |
| "pode começar" · "siga" · "siga com suas recomendações" · "pode ir" · "aprovado" · "manda ver" · "vamos seguir" · "perfeito, segue" | **AVANÇA** o que está no gate — se havia plano aguardando, é aprovação: vá para a implementação. Se não havia, o "siga" se aplica ao que você acabou de propor |
| "onde paramos?" · "o que falta?" · "cadê o board?" · "quais as pendências?" · "o que estamos fazendo?" | **Mostra o quadro** (`/orq:quadro`): esperando-ele primeiro, depois em curso e a validar |
| "terminamos" · "acabou essa parte" · "vamos limpar o contexto" · "pode reiniciar" · "salva aí" · "pode limpar" | **Checkpoint** (`/orq:checkpoint`): grava log + páginas + thread + board. **Depois** avise que é seguro dar `/clear` — e que dá pra **fechar a janela** se a pendência ficou registrada |
| "vamos planejar X" · "próxima tarefa" · "o que vem agora?" | **Loop A** (`/orq:plan-next`) — e **pare** no gate pra ele aprovar |
| "pode implementar" · "manda ver" · "toca essa" · "aprovado" | **Loop B** (`/orq:implement-next`) — só se o card estiver aprovado |
| "anota isso" · "cria uma tarefa" · "isso vira card" · "não esquece disso" | **Cria o card** no BACKLOG com ID e contexto suficiente pra retomar |
| "revisa isso" · "manda revisar" · "o que você acha desse código?" | **Painel de revisores** (`/orq:revisar`) — Claude + Codex em paralelo, achados reconciliados |
| "quem tá revisando?" · "troca o modelo do planner" · "quero o Fable planejando" · "tira o GPT" | **Elenco** (`/orq:elenco`) — mostra ou ajusta qual LLM toca cada papel |
| "lembra quando a gente…?" · "o que a gente decidiu sobre…?" | **Busca a memória** (`/orq:lembrar`) + cruza com a wiki |
| "tá lento" · "o que falta instalar?" · "dá pra melhorar a performance?" · "que ferramenta ajudaria?" | **Stack** (`/orq:stack`) — detecta o que falta, mostra ganho e custo, instala **só o que ele aprovar** |
| "não está funcionando" · "o revisor sumiu" · "não conecta com X" · "parece que não pegou" | **Diagnóstico** (`/orq:stack --verificar`) — checa plugin desatualizado, escopo errado, binário fora do PATH, board ilegível. **Antes de dizer que algo falta, cheque o caminho de instalação** — `which` só enxerga o PATH daquela sessão |
| "vou abrir outra janela pra isso" · "deixa essa parte pra depois" · "essa janela é pra X" | **Registre a frente**: nomeie a thread, marque os cards em curso com `@frente`, e diga em uma linha o que fica onde |
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

## Várias janelas no mesmo projeto

O dono trabalha com **N janelas abertas**, uma por frente: está resolvendo A, lembra de B, abre
janela pra B sem largar A. O modelo pressupõe **um** Manager, então sem disciplina as janelas se
sobrescrevem **em silêncio**.

**Uma janela = uma frente.** Nunca duas janelas na mesma frente.

1. **Releia antes de escrever.** Sempre — o disco pode ter mudado desde que você leu.
2. **Edite a linha, nunca o arquivo.** Reescrever o `KANBAN.md` inteiro a partir de uma cópia velha
   é o que apaga o trabalho das outras janelas. A concorrência não é o problema; a reescrita é.
3. **Card em curso leva `@frente`** no fim da nota. Não pegue card marcado com frente alheia.
4. **Trabalho em curso mora na thread da frente** (`threads/<frente>.md`) — arquivo de dono único,
   livre de conflito por construção. Só o board é disputado.

**A pendência não precisa de janela aberta.** Se algo depende de decisão dele, mova o card para
`[!]` **com a pergunta exata escrita**, grave o "RETOMAR AQUI" na thread e **diga que pode fechar a
janela**. Janela viva só para "não esquecer" é contexto usado como memória — o board existe pra
substituir isso. Se você não consegue garantir a retomada, o handoff está fraco: melhore-o.

Protocolo completo: `memory/wiki/_schema.md`.

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
*neste* projeto, o catálogo com ganho, custo e **o repositório oficial** está em `stack.md` (raiz do
plugin) — ele **não traz comando de instalação** de propósito; as instruções vêm do upstream, na
hora. `/orq:stack` detecta e propõe. **Nunca instale nada sem o "pode instalar" dele.**
O que ele dispensou fica em `memory/wiki/_stack.md` — **não reproponha**.

Nunca guarde na memória o que é **derivável** (diff, git log, schema): guarde o *porquê*.
