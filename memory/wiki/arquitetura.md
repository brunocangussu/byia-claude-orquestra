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

## Interface e execução por host

O núcleo é único; a interface e o executor variam pelo host:

| Host | Interface explícita | Resolução do trabalho |
|---|---|---|
| Claude Code | linguagem natural + `/orq:*` | subagente nativo quando suporta o papel; CLIs externas para diversidade |
| Codex | linguagem natural + `/skills` | time `Host Codex` e Matriz; CLI explícita quando a primitiva não aceita modelo/effort |
| Kimi | linguagem natural pela skill instalada | time `Host Kimi` e Matriz; escrita só com contenção comprovada |

`commands/` é a superfície de slash commands do Claude e a descrição canônica das operações; o
Codex não a converte em `/orq:*`. Ausência de `/orq` no menu do Codex não é falha de instalação.

Todo consumidor resolve na mesma ordem: **host → papel → vendor → mecanismo**. O template de
`_elenco.md` gera `## Times por host` e `## Matriz de invocação`; projeto existente é migrado de
forma aditiva. “Configurado” descreve o próximo despacho, não prova qual processo está rodando.

No host Codex, o titular é Manager `gpt-5.6-sol@high`, Planner `gpt-5.6-sol@ultra` e Implementer
`gpt-5.6-terra@xhigh`. O painel independente obrigatório é Opus 5 + Kimi K3; o Manager reconcilia,
mas não conta como parecer.

O reviewer Opus não é uma chamada `claude -p` crua. `orq/scripts/run-opus-reviewer.py` recebe o
briefing sanitizado pelo stdin, limita cada lote a 16 KiB, anuncia o início e aplica timeout de
600s; só libera a saída quando `modelUsage` comprova `claude-opus-5`. O teto foi ampliado após uma
resposta válida levar 267,1s e ser morta pelo limite anterior de 240s. Diff maior é dividido por arquivo/hunk, cobrindo
todos os lotes sem truncamento; falha em qualquer lote produz painel parcial com diagnóstico.

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

## O que o plugin distribui além de instruções (0.20.0)

Até a 0.19.0 o plugin era **só texto** — comandos, skill, agentes — mais dois scripts de leitura
(`kanban-status.sh`, `lint-coerencia.py`). A 0.20.0 acrescentou o primeiro **asset de runtime**:
`orq/scripts/statusline.sh`, a barra de status completa, instalada no projeto ou no usuário.

Três propriedades que o desenho garante, e que valem para qualquer asset futuro:

1. **Nada em settings aponta para dentro do plugin.** O caminho do cache muda a cada versão — uma
   chave apontando para lá quebra no próximo update. O que vai para settings é sempre uma **cópia**
   instalada fora do plugin, e a cópia acha a irmã **por vizinhança** (`$(dirname "$0")`).
2. **O par é indivisível.** `statusline.sh` e `kanban-status.sh` são copiados juntos, sempre. O
   primeiro degrada para board-only se faltar `jq`, e **se completa sozinho** quando `jq` aparecer.
3. **Instalar nunca é alterar.** Havendo statusline em qualquer escopo, o init **não grava chave** —
   relata, e oferece **remover** a chave que estiver sombreando outra barra. Foi a ausência disso que
   causou o `T-036`.

**A lição que generaliza, e que já vale para a memória também:** *em configuração com precedência,
adicionar É sobrescrever*. Um diff aditivo (`+N -0`) pode desligar comportamento global sem tocar em
arquivo nenhum do usuário — e nenhuma verificação do tipo "sobrescrevi algo?" acusa.

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

## Guardião preventivo do contexto Codex

O pacote traz `hooks/hooks.json` e `scripts/context-guard.py`. O guardião lê somente o último evento
`token_count` do `transcript_path`, limita a leitura ao fim do arquivo e persiste em `PLUGIN_DATA`
apenas faixa, percentual, timestamps e estado do checkpoint, isolados por `session_id`.

- 55%: pré-alerta único;
- primeiro valor observado ≥60%: `Stop` cria uma continuação única e consultiva para o checkpoint;
- ≥70%: aviso consultivo reforçado; o guardião nunca bloqueia trabalho, `Stop`, compactação ou modo Goal;
- **Codex — Checkpoint verificado; conversa continua.**: handshake que grava
  `checkpoint_verified`; a mesma conversa continua e a compactação nativa substitui a obrigação de
  limpar a sessão; após mais 10 pontos percentuais de uso, um novo checkpoint é rearmado de forma
  consultiva; o estado legado `clear_required` migra sem reativar bloqueio;
- `SessionStart(source=compact)`: reidrata memória, board e thread; sem checkpoint anterior, exige
  checkpoint de recuperação consultivo, sem impedir trabalho novo;
- modo Goal: continuação normal do pedido, sem dependência de banco privado do App;
- **Claude — Seguro dar `/clear`.**: contrato preservado, com `/clear` manual;
- `PreCompact` e `PostCompact`: nunca bloqueiam o núcleo nem duplicam a reidratação.

O transcript não é uma interface estável. Parser, estado e hooks falham abertos; nenhum erro do
guardião ou falha de persistência pode impedir compactação nem persistir conteúdo da conversa. Em
`UserPromptSubmit`, `additionalContext` reafirma a política consultiva para a conversa já carregada.
O script só atua no ambiente
nativo `PLUGIN_ROOT` do Codex; variáveis somente `CLAUDE_*` não ativam o guardião.
