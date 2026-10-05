# Arquitetura do Orquestra

> Como o plugin funciona **hoje** (`0.30.0`). Página de consulta — organizada por pergunta, não por
> ordem de leitura. Reescrever quando o desenho mudar; histórico é `fixes-history.md`, não aqui.

## O princípio

> **Contexto é descartável. O estado do trabalho vive no board e nos artefatos.**

A janela pode morrer a qualquer momento — e vai. Se o estado só existe no chat, perde-se. Por isso
todo passo termina gravando no board e na wiki. É isso que elimina a necessidade de encadear
`/compact` para "não perder o raciocínio".

## Quem é quem

| Papel | Quem é | Contexto | Escreve? |
|---|---|---|---|
| **Manager** | a **sessão principal** | persistente — retém o fio da meada | board + memória |
| `orq-scout` | subagente | fresco a cada uso | ❌ read-only, investiga território novo |
| `orq-planner` | subagente | fresco a cada card | só o arquivo do plano |
| `orq-implementer` | subagente | fresco a cada card | ✅ código, em worktree isolado |
| `orq-reviewer` | subagente | fresco a cada revisão | ❌ read-only, aponta e não corrige |
| `orq-docs` | subagente | fresco a cada card | ✅ docs sobre o código já pronto |

**Por que o Manager não é subagente:** existe exatamente um lugar que move cards e fala com o dono.
Se fosse spawn, haveria duas fontes de verdade sobre "onde estamos". Veio direto da fonte original —
no Terminals o Manager é separado do canvas.

**Por que os workers nascem frescos:** contexto contaminado faz o agente arrastar premissas da tarefa
anterior. No Claude Code cada spawn é contexto novo, então isso é de graça.

**Os dois loops:** Loop A (`/orq:plan-next`) é Manager ⇄ Planner e termina no gate do dono. Loop B
(`/orq:implement-next`) é Manager ⇄ Implementer ⇄ Reviewer ⇄ Docs; não termina em VALIDATE por si
só: só fica elegível quando houver review fechado, alvo de validação e entrega correspondente
autorizados. Os dois podem alternar: enquanto um card espera aprovação, outro avança.

## Interface e execução por host

O núcleo é único; a interface e o executor variam pelo host:

| Host | Interface explícita | Resolução do trabalho |
|---|---|---|
| Claude Code | linguagem natural + `/orq:*` | subagente nativo quando suporta o papel; CLIs externas para diversidade |
| Codex | linguagem natural + `/skills` | time do host Codex (`_elenco.md`) + Matriz de invocação; CLI explícita quando a primitiva não aceita modelo/effort |

`commands/` é a superfície de slash commands do Claude e a descrição canônica das operações; o
Codex não a converte em `/orq:*`. Ausência de `/orq` no menu do Codex não é falha de instalação —
fora do Claude, siga o arquivo `commands/<nome>.md` como procedimento, até onde o host permitir.

Todo consumidor resolve na mesma ordem: **host → papel → vendor → mecanismo**. `_elenco.md` tem
`## Times por host` (o time de cada host, a única fonte ativa) e `## Matriz de invocação` (o
template por vendor × host). “Configurado” descreve o próximo despacho, não prova qual processo
está rodando — o Manager confirma binário/modelo/saída antes de anunciar um papel como resolvido.

## Os comandos (`/orq:*`)

14 arquivos em `orq/commands/`. No Codex a interface é natural language / `/skills`; o arquivo é
lido como procedimento mesmo sem o slash command existir naquele host.

| Comando | O que faz | Dispara quando |
|---|---|---|
| `/orq:acordar` | Encerra o modo noturno: relatório do que foi planejado, o que ficou estacionado (com pergunta numerada) e o que foi pulado. | "bom dia" depois do modo noturno |
| `/orq:ajuda` | Cardápio por situação — frase natural → o que acontece, comando entre parênteses só como referência. | "quais as possibilidades", "o que dá pra fazer" |
| `/orq:auditar` | Ledger **offline** de remoção de código/config (`scan`/`verify`), ou verificação de que uma descoberta seguiu grafo/índice antes de busca textual, a partir de um trace explícito. Nunca cria hook, nunca captura sessão viva. | "audite a remoção de X", "prove que X saiu", "começamos pelo grafo?" |
| `/orq:checkpoint` | Fecha o bloco de trabalho: grava log + páginas de tópico + thread + board, releva antes de escrever (várias janelas), emite o handshake exato do host. | "terminamos", "salva aí" |
| `/orq:dormir` | Modo noturno — só **planejamento** dos próximos cards do backlog, estacionando em `[!]` o que precisar de decisão. Limites duros e proibições absolutas (nunca implementa, nunca `push`/deploy/migration). | "vou dormir, adianta o que der" |
| `/orq:elenco` | Mostra ou ajusta qual LLM interpreta cada papel **neste host**: papel a papel, via cross-vendor `on`/`off`, ou o time inteiro por `perfil <nome>`. | "quem tá revisando", "troca o modelo do planner", "modo economia" |
| `/orq:implement-next` | **Loop B** — implementa um card `READY` em worktree isolado, roda a revisão independente e documenta o código final; só fica elegível a VALIDATE quando o review estiver fechado e a entrega ao alvo estiver autorizada. | "pode implementar", "manda ver" (card já aprovado) |
| `/orq:init` | Investiga o projeto (scouts em paralelo), detecta ferramental real, propõe um time sob medida e só escreve depois da aprovação: memória + board com backlog real + agentes + bloco no `CLAUDE.md`/`AGENTS.md`. Idempotente. | primeira vez do Orquestra num projeto, ou para completar o que falta |
| `/orq:instalar` | Instala **o plugin em si** (não o projeto) no host alternativo do dono, a partir da mesma fonte já registrada; no host onde já roda, só confere. | "quero o Orquestra no Codex também" |
| `/orq:plan-next` | **Loop A** — escolhe o próximo card (ou cria um a partir de texto livre), classifica trilha/faixa, despacha o planner certo, **para no gate**. | qualquer pedido de mudança ("quero X", "tem um problema em Y") |
| `/orq:quadro` | Mostra o board formatado, começando pelo que espera o dono (`[!]`), depois em curso, a validar, backlog, feito. | "onde paramos", "o que falta" |
| `/orq:revisar` | Dispara a revisão independente (**um** revisor, vendor oposto ao host) sobre a mudança atual e audita os achados antes de repassar. | "revisa isso aí"; também roda dentro do Loop B |
| `/orq:stack` | Diagnostica o ambiente (plugin desatualizado/cache stale, revisor mudo, board ilegível, escopo errado) e detecta/instala a stack complementar de contexto e memória aprovada pelo dono. `--verificar` só diagnostica. | "tá lento", "o revisor sumiu", "o que falta instalar" |
| `/orq:wiki-lint` | Health-check da wiki: contradições entre páginas, afirmações vencidas, páginas órfãs, threads mortas. | sob pedido; também por iniciativa do Manager (N1) em checkpoint de marco |

## O elenco — quem interpreta cada papel

**A regra em uma frase:** *domínio decide quem pensa; host decide quem escreve.* Dois eixos
independentes, aplicados por card:

- **Trilha** (`interface` | `sistema`) — escolhe o **vendor do planner**. Critério de aceite
  **perceptual** (o dono valida olhando/usando) → Anthropic; **comportamental** (valida-se
  verificando) → OpenAI. Card misto ou ambíguo → `sistema`. Não é frontend/backend: um CLI é
  `sistema`, um brand book é `interface`.
- **Faixa** (`pesada` | `normal` | `leve`) — escolhe o **degrau do implementer**, sempre no vendor
  do **host**. `pesada` = alto risco **ou** desenho ainda por decidir; `leve` = resultado
  determinado e verificação mecânica; senão `normal`. Card **Trivial** não tem faixa — não há
  implementer, o Manager escreve direto na sessão.

O Manager grava `trilha: … · faixa: …` na nota do card. **Card sem registro → `sistema · normal`.**
A faixa é reavaliada no gate do Loop A, com **piso**: card Alto risco continua `pesada` mesmo com o
plano fechado — rebaixar só vale quando a `pesada` veio exclusivamente de desenho aberto e o plano
fechou esse desenho. A definição canônica das duas réguas mora em `orq/commands/elenco.md`, seção
"As duas réguas" — esta página resume, não redefine.

**Escala de risco → cerimônia** (fonte: `orq/skills/orq/SKILL.md`), o que decide o roteamento antes
mesmo de classificar trilha/faixa:

| Nível | O que é | O que roda |
|---|---|---|
| Trivial | typo, renomear variável local, texto sem efeito | direto, sem cerimônia — sem implementer |
| Pequeno | 1 arquivo, sem decisão de desenho, reversível | implementa + revisão independente (briefing enxuto) |
| Normal | feature, correção com causa raiz, contrato entre partes | ciclo completo: plano → gate → implementação → revisão → docs → `VALIDATE` |
| Alto risco | schema, segurança, dependência nova, dado de terceiro, irreversível | ciclo completo **+ gate extra antes de tocar** |

**Quem pode vir de outro vendor:** só `planner` (pelo domínio) e `reviewer` (pela independência,
obrigatoriamente do vendor oposto ao host). `implementer`, `docs` e `scout` ficam sempre no vendor
do host — os dois primeiros porque escrevem (escrita cross-vendor está fora do desenho), o `scout`
porque leitura ampla e barata não compra aptidão de domínio.

**Onde estão os valores vivos:** esta página descreve a *forma* do elenco, não os modelos
concretos — eles mudam sem alterar o desenho. A fonte é `memory/wiki/_elenco.md`, seção
`## Times por host` (única tabela ativa, uma por host — uma janela Codex nunca escreve na tabela do
Claude e vice-versa) mais `## Matriz de invocação` (o mecanismo real por vendor × host) e
`## Perfis` (times nomeados por contexto de crédito, só do host Claude hoje; ativar um preset
reescreve a tabela do host e nunca toca `manager` nem o estado das vias cross-vendor).

No host Claude, papéis read-only OpenAI passam pelo `codex:codex-rescue`/Codex Companion. A unidade
de isolamento e reúso é `card+papel`: primeira chamada fresca, continuação pela `threadId` exata;
mudou card ou papel, nasce outra task. O handoff durável guarda `card`, `papel`, `jobId`,
`threadId` e `status`, e o resultado vem de `rawOutput`. Isso evita uma task por mensagem sem
misturar Planner e Reviewer nem depender da ambiguidade de "última task".

No Companion, ausência de `--write` não prova limitação de leituras, ferramentas ou egress. A rota
de pacote congelado só é elegível com capacidade preventiva sem ferramentas e isolamento comprovados
para o envelope real; sem isso, o digest é **INVERIFICÁVEL / CAPACIDADE AUSENTE**, a chamada não
ocorre e somente a dependência externa estaciona. Não se inventa `--no-tools`, fallback ou probe.

A continuação só vale se a chamada terminar com `status: 0`, `jobId` e `threadId` presentes e o
`threadId` devolvido for igual ao solicitado. Divergência ou recibo incompleto degrada a
continuação: o vínculo anterior é preservado e nada é repetido, substituído por outra task ou
recolhido pela "última" automaticamente. O `--wait` é do envelope enviado ao `codex-rescue`, que o
remove antes de invocar o `task`; o runtime não o recebe.

## A revisão independente

Contrato canônico em `orq/commands/revisar.md` — aqui só o que muda o desenho:

- **Um revisor só, sempre do vendor oposto ao host.** Host Claude → OpenAI; host Codex → Anthropic
  (pelo `orq/scripts/run-opus-reviewer.py --model <alias>`, via Anthropic parametrizada pelo alias
  do elenco, sem hardcode de modelo na chamada: alias ou ID da linha `reviewer` do host;
  o default legado do runner continua `opus`, mas o host sempre passa `--model`). Não existe painel, não existe
  "confirmado por 2+", e o Manager não conta como parecer — ele **audita**.
- **Todo achado é solitário por construção (N=1).** O Manager verifica cada um no código antes de
  aceitar, descarta o que não tem cenário de falha concreto, e desempata sozinho quando discorda.
  Segundo parecer só existe sob pedido explícito do dono, e obedece à mesma regra de vendor — um
  parecer do vendor do host **nunca** conta como "segundo parecer".
- **Titular indisponível → REVISÃO DEGRADADA**, causa nomeada, card não avança sozinho. **Nunca**
  substituído por um revisor do vendor do host.
- **Dado sensível no diff → não há revisor nenhum** (a regra de dados impede a transferência para o
  vendor oposto). O Manager audita o diff ele mesmo e declara "sem revisão independente por
  restrição de dados" — proibido tapar o buraco com revisor do mesmo vendor do host.
- `--rapido` encolhe só o **briefing** em card pequeno/baixo risco — nunca troca de revisor nem
  dispensa a revisão.

O runner Anthropic (`run-opus-reviewer.py --model <alias>`) sanitiza o briefing, limita 16 KiB por
lote (dividindo por arquivo/hunk acima disso), anuncia `OPUS_STARTED` no stderr e aplica timeout de
600s — teto que acomoda a latência real observada em revisão arquitetural (267,1s), sem remover a
proteção contra processo órfão. Só libera saída quando `modelUsage` comprova o prefixo do alias
pedido (hoje, `fable` exige `claude-fable-5-1`).

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
não representa os gates. Só o Manager muda o marcador de um card; worker que quiser mover, pede.
`PLANNING → READY` exige aprovação explícita do dono; `DEV_REVIEW → VALIDATE` exige review fechado,
alvo de validação e entrega correspondente autorizados; VALIDATE não é prometido sem entrega
autorizada ao alvo. `VALIDATE → DONE` é do dono, salvo delegação explícita.

## As regras invioláveis

1. **Handoff antes de encerrar** — objetivo · escopo · decisões com o porquê · o que faltou · dúvidas.
2. **Causa raiz, nunca sintoma** — catch silencioso e retry cego são rejeitados no review.
3. **Autocrítica antes de entregar** — "o que estou assumindo sem verificar?"
4. **Escopo tem borda** — mesma causa raiz e mesmo subsistema: pode, mas só dentro de um card já
   aprovado. Schema, API pública, segurança ou outro módulo: card novo.
5. **Documentação é atemporal** — descreve como é agora, nunca "mudamos de X para Y".
6. **Review é read-only** — quem revisa aponta; quem implementou aplica.
7. **Um dono por arquivo** — tarefa que escreve roda em worktree próprio.
8. **Nada de `bypassPermissions`** — nem de dia, nem de noite.
9. **Commit não é critério de pronto** — card só pode ir a VALIDATE após a entrega autorizada ao alvo;
o dono confirma usando o produto.

⚠️ **Enforcement: quase nenhum.** As nove regras são texto de prompt, não ACL — o plugin não declara
um único hook de bloqueio (`T-001`, `T-002` continuam em backlog). O que existe de verificação
**determinística** hoje:

| Verificação | Pega |
|---|---|
| `claude plugin validate --strict` | manifesto malformado |
| `orq/scripts/lint-coerencia.py` | comando/agente/skill/arquivo citado que não existe · versão divergindo entre os **quatro** lugares · edição sem bump com o cache já publicado |
| `orq/scripts/kanban-status.sh` | card fora do contrato do board (sinaliza `⚠N`) |
| `/orq:stack --verificar` | plugin desatualizado **ou** cache stale (versão *e* conteúdo), escopo errado, revisor ausente, board ilegível |

Nenhuma delas **impede** nada — todas só relatam. Bloquear de verdade continua sendo o `T-001`.

**Revisor sem sandbox precisa de worktree descartável, não de instrução.** No host Codex,
`codex exec -s read-only` é garantia. No host Claude, o Companion precisa receber pedido
READ-ONLY e nunca a flag `--write`; ainda assim, use worktree descartável como contenção. O prompt
"não edite nada" sozinho é pedido, não ACL. Um host que já esteve neste projeto (removido do
produto desde a `0.24.0`) não tinha flag equivalente e rodou `git checkout -- .` numa revisão
read-only, destruindo o working tree (`T-019`) — a lição é a mesma do `T-001`, e segue registrada
no `gotchas.md`.

## Os três gates automatizados (release e review de instruções)

Nesta ordem, todos obrigatórios ao editar `orq/`:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s orq/scripts -p 'test_*.py'   # suíte
claude plugin validate ./orq --strict          # manifesto
python3 orq/scripts/lint-coerencia.py .        # coerência entre as instruções
```

**A suíte vem primeiro** porque os outros dois leem texto e manifesto — uma regressão no
verificador de cache, no runner Opus ou no guardião de contexto passa pelos outros dois **inteira**.
A lista de módulos é **descoberta**, nunca enumerada: enumerar já custou caro (a instrução citava
três dos cinco, e quem seguia rodava 119 dos 201 achando que rodara tudo).

**O que o lint prova** (não como — os mecanismos mudam, as garantias não):

- **papel por célula de tabela** — toda linha de `## Times por host`/perfil tem um papel reconhecido;
- **heading ancorado em linha exata** — seção citada por nome (`## Times por host`, `## Perfis`…)
  existe de verdade no arquivo apontado;
- **host aposentado** — varre `orq/` inteiro + `README.md`/`CLAUDE.md`/`AGENTS.md` + as duas páginas
  vivas fora do plugin (`arquitetura.md`, `distribuicao.md` — **esta página incluída**) atrás de
  menção a vendor/host que o produto não suporta mais;
- **teto do runner derivado** — o timeout citado como limite do runner Opus tem que bater com a
  constante `DEFAULT_TIMEOUT_SECONDS` real em `run-opus-reviewer.py`, nunca um número hardcoded à
  parte que pode divergir em silêncio;
- **vocabulário extinto** — termos de um desenho anterior (ex.: linguagem de painel de N revisores)
  não podem reaparecer depois que o desenho os aposentou;
- **bump como passo do procedimento** — release sem bump nos quatro lugares é pego quando o cache
  daquela versão já existe no disco;
- **seções únicas** — heading que só devia aparecer uma vez não duplica.

⚠️ **Esta própria página é varrida pelo lint** (exceção nominal a `memory/`, junto com
`distribuicao.md`) — porque é instrução viva sobre como o sistema funciona hoje, não registro
histórico. Um nome de comando/agente/skill errado aqui reprova o gate 3.

**O cache é indexado por versão.** `~/.claude/plugins/cache/<mkt>/<plugin>/<versão>/` (e o
equivalente em `~/.codex/`) — editar `orq/` sem bumpar **não muda o que roda**, e `claude/codex
plugin list` continua dizendo que está tudo certo. Aconteceu no `5b75296` e invalidou
retroativamente todo teste comportamental feito depois. `verify_installed_cache.py` é o fecho que
prova conteúdo, não só versão — comparador compartilhado pelo lint, diagnóstico e instalador, com
allowlist estrita por host aplicada só ao lado instalado. Procedimento completo de release,
publicação e verificação de cache: `memory/wiki/distribuicao.md`.

## Roteamento — o dono não digita comando

**Todo pedido de mudança entra pelo ciclo.** *"quero X"*, *"vamos acrescentar Y"*, *"tem um problema
em Z"* não são pedidos de código — são pedidos de **plano**. A escala de risco (tabela acima)
dimensiona a cerimônia; na dúvida, sobe um nível — o custo de planejar demais é minutos, o de
implementar a coisa errada é a implementação inteira mais o retrabalho.

**O modo de falha é conhecido e nomeado:** o pedido chega em linguagem natural, parece pequeno, e o
Manager começa a editar — sem plano, sem gate, com o revisor entrando só depois, revisando o que já
está pronto. Aconteceu em toda a sessão de 26-28/jul, incluindo features inteiras, porque a
`description` da skill tinha **0% de cobertura** sobre a fala real do dono — hoje o gatilho da
skill é medido contra corpus real, não inventado.

## Decisões que o Manager toma sozinho — iniciativa própria

Para não interromper o dono a cada passo — sempre registrada no board/memória. Dois grupos, com
regras diferentes:

- **N0 — decisão de board.** Não é "mudar o produto": bug pequeno achado no meio de um card entra
  no card atual; bug grande vira card novo no BACKLOG; ordenar a fila quando não há prioridade
  explícita.
- **N1 (age sozinho, só leitura) — N2 (propõe, nunca insiste) — N3 (sempre pergunta):**

| Nível | Quando age | O que faz |
|---|---|---|
| N1 | checkpoint fecha com rótulo de marco, ou flagra contradição entre página e trabalho | roda `/orq:wiki-lint` sozinho e **relata** o achado; **nunca corrige nada**, nem trivial |
| N2 | o mesmo atrito aparece 2× no mesmo bloco de trabalho; contexto perto de ~50% sem telemetria | sugere `/orq:stack` ou checkpoint — **teto de 1 proposta por assunto e por estado da condição**; recusa de política congela o assunto, recusa de momento rearma quando a condição piora |
| N3 | aparência/UX, mudança de rumo, schema, segurança, dependência nova, deploy, irreversível | **sempre pergunta**, nunca decide |

Transversal aos três: **iniciativa nunca escreve no produto** — toda mudança continua entrando pelo
ciclo normal. Registrar a recusa do N2 ou o achado do N1 na memória/board é escrita permitida; editar
código ou instrução por iniciativa própria não é.

## Trabalho em várias janelas

O dono abre uma janela por frente. Como o desenho pressupõe **um** Manager, N janelas se
sobrescreveriam em silêncio sem disciplina. O protocolo (completo em `memory/wiki/_schema.md`): uma
janela = uma frente · releia antes de escrever · **edite a linha, nunca o arquivo** · card em curso
leva `@frente` · trabalho em curso mora na thread da frente, arquivo de dono único.

**O diagnóstico que definiu a solução:** a concorrência não é o problema — **a reescrita é**. Duas
janelas alterando linhas diferentes, cada uma relendo antes, praticamente não colidem. Por isso não
há lock: lock mataria o paralelismo que motiva as N janelas.

E o ganho maior não é a trava: **pendência de decisão vira card `[!]` e a janela pode fechar.**
Janela viva só para "não esquecer" é contexto usado como memória — o board existe pra substituir isso.

## O que o plugin distribui além de instruções

Comandos, skill e agentes são texto. Estes são os assets de runtime, todos em `orq/scripts/` (mais
`orq/hooks/hooks.json` e os contratos JSON de `orq/schemas/`):

| Arquivo | Faz |
|---|---|
| `context-guard.py` | guardião preventivo de contexto do Codex — o `hooks.json` o encaixa em 6 eventos (`PostToolUse`, `Stop`, `UserPromptSubmit`, `SessionStart`, `PreCompact`, `PostCompact`), um grupo por evento; só age no ambiente nativo do Codex (ver seção própria abaixo) |
| `run-opus-reviewer.py` | roda revisor/planner num modelo **Anthropic escolhido por `--model`** (`opus`·`fable`·`sonnet`·`haiku`; padrão `opus`) pela via cross-vendor, **comprova no `modelUsage` o prefixo do alias pedido** — pedir um e receber outro reprova —, 16 KiB/lote, timeout 600s |
| `verify_installed_cache.py` | compara byte a byte a fonte do plugin com o cache instalado num host — o fecho de todo release e de todo `/orq:instalar` |
| `audit-removal.py` | ledger offline de remoção de código/config (`scan`/`verify`), evidência reproduzível sem chamar LLM nenhuma |
| `audit-adoption.py` | verifica offline, a partir de um trace explícito (`schemas/audit-ledger-v1.json`), se a descoberta seguiu grafo/índice antes de busca textual |
| `lint-coerencia.py` | o lint de coerência — guardas descritos na seção dos gates |
| `kanban-status.sh` | lê `KANBAN.md` por posição e emite `📋 X% (feitos/total) · fazendo: …` pra statusline; com `--card-state T-NNN --board-path <absoluto>` emite o marcador de **um** card em JSON — a pergunta que o medidor faz ao board, pelo mesmo parser |
| `statusline.sh` | a barra completa (modelo · effort · contexto · custo · rate-limit 5h · diretório · worktree · branch · board · segmento do medidor); acha `kanban-status.sh` e `progress.py` **por vizinhança**, nunca caminho fixo, e degrada para só-board sem `jq` |
| `progress.py` | medidor de progresso portátil (Python stdlib): ledger por card ou goal em `<front_root>/.orq/progress/v1/`, contratos em `orq/schemas/progress-ledger-v1.json` e `orq/schemas/progress-binding-v1.json`; subcomandos de escrita só para o Manager, vistas `show`/`watch`, vínculo de sessão (`bind`), a regra dos hooks e o segmento da statusline (`statusline`) — ver "Medidor de progresso" |
| `progress-hook.py` | adaptador fino dos hooks do medidor: liga o stdin do host a `progress.py` e garante exit `0`. O `hooks.json` o encaixa em dois eventos, em grupos próprios ao lado dos do guardião: `SessionStart` (fontes `startup`, `resume`, `clear`, `compact`, `fork`) e `PostToolUse` (toda ferramenta). **Não** entra na cópia da statusline: vem com o bundle do plugin |

A suíte descoberta roda todo `test_*.py` de `orq/scripts/`, inclusive os do medidor
(`test_progress.py`, `test_progress_hooks.py`, `test_progress_statusline.py`, `test_progress_docs.py`) e
`test_kanban_status.py` (que cobre também o modo `--card-state`).

Três propriedades valem para qualquer asset de runtime futuro:

1. **Nada em settings aponta para dentro do plugin.** O caminho do cache muda a cada versão — uma
   chave apontando para lá quebra no próximo update. O que vai para settings é sempre uma **cópia**
   instalada fora do plugin, achando as irmãs por vizinhança.
2. **Conjuntos indivisíveis são copiados juntos** (ex.: o trio `statusline.sh` + `kanban-status.sh` +
   `progress.py`) — nunca um sem os outros. A barra degrada sozinha quando falta a irmã; o conjunto
   completo é o estado que o `/orq:init` instala e que o `--reinstalar` propõe recompor.
3. **Instalar nunca é alterar.** Havendo algo já configurado em qualquer escopo, quem instala
   **relata e oferece remover** o que estiver sombreando, em vez de sobrescrever em silêncio.

**A lição que generaliza, e que já vale para a memória também:** *em configuração com precedência,
adicionar É sobrescrever*. Um diff aditivo (`+N -0`) pode desligar comportamento global sem tocar em
arquivo nenhum do usuário — e nenhuma verificação do tipo "sobrescrevi algo?" acusa.

## Guardião preventivo do contexto (Codex)

`orq/hooks/hooks.json` + `orq/scripts/context-guard.py`. O guardião lê somente o último evento
`token_count` do `transcript_path`, limita a leitura ao fim do arquivo e persiste em `PLUGIN_DATA`
apenas faixa, percentual, timestamps e estado do checkpoint, isolados por `session_id`.

- 55%: pré-alerta único;
- primeiro valor observado ≥60%: `Stop` cria uma continuação única e consultiva para o checkpoint;
- ≥70%: aviso consultivo reforçado; o guardião **nunca bloqueia** trabalho, `Stop`, compactação ou
  modo Goal;
- **"Checkpoint verificado; conversa continua."**: handshake que grava `checkpoint_verified`; a
  mesma conversa continua e a compactação nativa substitui a obrigação de limpar a sessão; após mais
  10 pontos percentuais de uso, um novo checkpoint é rearmado de forma consultiva. O estado legado
  `clear_required`, de quando o guardião ainda bloqueava, **migra sem reativar bloqueio**;
- `SessionStart(source=compact)`: reidrata memória, board e thread; sem checkpoint anterior, exige
  checkpoint de recuperação consultivo, sem impedir trabalho novo;
- No Claude, o contrato permanece **"Seguro dar `/clear`."**, com `/clear` manual.

O transcript não é uma interface estável. Parser, estado e hooks **falham abertos**: nenhum erro do
guardião — nem uma **falha de persistência** do estado — pode impedir a compactação ou persistir
conteúdo da conversa. Em `UserPromptSubmit`, o `additionalContext` reafirma a política consultiva
para a conversa já carregada. O script só atua no ambiente nativo `PLUGIN_ROOT` do Codex; variáveis
somente `CLAUDE_*` não ativam o guardião.

Pedidos de reset do estado são marcadores vazios: o caminho fixo `<hash>.reset` continua sendo
reconhecido para upgrades, e novos pedidos usam gerações exclusivas `<hash>.reset.*`. Dentro do lock
da sessão, o marcador legado é reivindicado por renomeação atômica para uma geração exclusiva antes
da fotografia; assim, uma sessão antiga que voltar a criar `<hash>.reset` depois dessa reivindicação
deixa um novo pedido para a próxima transação. A transação captura os marcadores presentes, remove o
JSON de estado, processa o evento e só remove aquela captura depois de persistir o novo estado com
sucesso. Um marcador de geração criado depois da fotografia permanece para a próxima transação; se
a remoção do JSON, a persistência ou a remoção de um marcador falhar, o pedido fica pendente e o
resultado é reset repetido, não reconhecimento falso. O estado e seus marcadores não guardam prompt,
transcript ou conteúdo da conversa.

O lock é do kernel: macOS/Linux usam `fcntl.flock` e Windows usa `msvcrt.locking` não bloqueante de
um byte na posição zero. O descritor é fechado ao liberar e também pelo sistema operacional quando
o processo termina. Se o host não oferecer nenhum desses backends, o hook retorna sem executar a
transação: a ação do host continua sem tocar no estado, mas a garantia de exclusão mútua fica
indisponível. Nesse caminho fail-open não se cria diretório de lock, lease por PID nem recuperação
por idade.

⚠️ **Os termos `clear_required`, `falha de persistência` e `additionalContext` são exigidos por
teste** (`test_context_guard.py`, `test_guard_contract_is_present_in_live_instructions`): eles são o
contrato do guardião, e a suíte reprova se sumirem desta página ou do `README.md`. Uma reescrita
desta seção em 2026-09-02 os removeu sem querer — o teste pegou.

## Medidor de progresso

`orq/scripts/progress.py` responde "onde a execução está" do mesmo jeito no Claude, no Codex e em
qualquer host com shell — sem depender de `/goal`, MCP ou mod do host. O procedimento de operação do
Manager é `orq/skills/orq/references/progress.md`; os contratos dos dados são
`orq/schemas/progress-ledger-v1.json` (o ledger) e `orq/schemas/progress-binding-v1.json` (o vínculo
de sessão). Esta seção só explica o desenho.

**Onde mora.** Um ledger JSON por card (`cards/T-NNN.json`) ou goal avulso (`goals/<uuid>.json`) em
`<front_root>/.orq/progress/v1/`, na frente dona do Manager — nunca no worktree do implementer. O
`begin` cria `.orq/progress/` com um `.gitignore` de `*` (preserva um que já exista lá), então a
telemetria não entra em commit. O ledger não vai para `memory/` porque o estado muda a cada passo e
disputaria com os documentos duráveis; nem para o home, que exigiria escrita fora do workspace, nem
para `PLUGIN_DATA`, que pertence a cada host e não garante compartilhamento entre Claude e Codex.
Guarda só títulos genéricos, IDs e referências de evidência — nunca prompt, saída de ferramenta ou
diff. A fronteira do medidor é a mesma máquina e a mesma frente. Ao lado dos ledgers, `sessions/`
guarda o vínculo de cada sessão nativa com o ledger dela (ver "Vínculo e as duas chaves").

**Fase e percentual são duas fontes.**

- A **fase** vem do board (`kanban-status.sh --card-state`). Como `[~]` não distingue implementação,
  revisão e documentação, o Manager declara a atividade (`phase`) só para essa distinção; a
  atividade nunca vence o board, e `phase` nunca move card.
- O **percentual** vem dos passos da tabela do plano aprovado (`ID | Entrega verificável | Tamanho |
  Critério de aceite`, exigida do Planner pelo `/orq:plan-next`), com S/M/L = 1/2/3. É sempre
  **"do plano"**: 100% não é DONE — com o card em `[?]` a vista diz "validação do dono", e só o dono
  fecha. Sem plano registrado não há percentual; restando passo aberto ele não passa de 99%;
  acrescentar ou reabrir passo pode fazê-lo cair. Não há ETA, de propósito.

**Um escritor: o Manager.** Toda mutação exige a **chave de dono** (`--session-key`, 64 hexadecimais)
gravada no ledger. Workers devolvem resultado e a referência da evidência por ID de passo e nunca
recebem a chave. O `done` só vale depois de o Manager conferir a evidência: o ledger guarda a
referência, não prova que o teste passou. A escrita só muda de mão por `claim` explícito com a chave
anterior — nunca por idade, PID ou "a sessão parece parada". A chave evita colisão entre sessões; não
é credencial nem ACL. `add`, `drop` e `reopen` só registram o que o ciclo normal já autorizou. O
`/orq:implement-next` (§0b) abre o ledger, vincula a sessão e marca os marcos; o `/orq:checkpoint`
grava na thread só caminho, run_id e revisão — nunca a chave de dono ou uma cópia da telemetria, que
contradiria o ledger.

**O que o script garante.**

- Lock de kernel por ledger, com espera limitada, e troca atômica (temporário no mesmo diretório,
  `fsync`, `os.replace`). `--expect-revision` é opcional: ausente, a mutação vale sobre o estado
  atual, ainda sob lock; presente e divergente, sai `3` sem gravar. O atrito de cada marcação é o
  modo de falha do medidor — se custa caro, o Manager pula e a barra mente.
- Mutação só dentro do layout padrão, por realpath. O Git precisa ignorar os destinos reais do
  ledger, do lock e do temporário com o nome reservado; senão sai `4` sem gravar. Nada é escrito
  antes de a contenção ser provada; fora de checkout Git não há conferência de cobertura.
- `plan` de card só com o board em `[~]`; `close --outcome reported_complete` de card só com `[x]`.
- Leituras (`show`, `watch`, `statusline`) não criam diretório, lock nem arquivo.
- **O recibo já traz a vista.** `begin` e toda mutação devolvem `view` (a linha de
  `show --format segment`, pela mesma projeção) e `view_revision` (a revisão projetada). A projeção
  roda depois da gravação, sobre o ledger que acabou de ser confirmado, e **fora do lock** (a consulta
  ao board é um subprocesso e não deve segurar o próximo escritor). O Manager lê o andamento no recibo
  da marcação em vez de pagar um `show` por marco. Se a projeção quebrar depois de gravar, o recibo segue
  `ok: true` e exit `0`, com `view: null` e `view_error`: a marcação **foi gravada** e não se repete,
  porque repetir a escrita por falha de vista seria o erro oposto ao de perder o marco. Erros (exit
  `2`, `3`, `4`) saem só em `stderr`, sem vista.
- Falha do medidor não bloqueia o trabalho, e também não vira sucesso: o marco é relatado como
  "progresso não registrado". Saídas: `0` sucesso ou repetição idempotente, `2` uso ou transição
  inválidos, `3` revisão ou dono divergentes, `4` estado ou armazenamento indisponíveis.

**Vistas.** `show` projeta o ledger como `text`, `json` ou `segment` (uma linha); `show --root <raiz>
--all` lista todos os ledgers de uma frente. `watch` é um leitor puro que redesenha a mesma projeção a
cada `--interval` num terminal ao lado — vale igual no Claude, no Codex e num terminal do Orca, e
encerra com Ctrl-C sem afetar a execução observada. O Manager não o roda no próprio shell (não
termina e prenderia a sessão): entrega ao dono a linha pronta, com os caminhos absolutos. A mesma
projeção alimenta o recibo (`view`) e o segmento da statusline do Claude.

**Vínculo e as duas chaves.** O host conhece a sessão por um ID nativo; o ledger conhece
o dono por uma chave. São duas chaves de propósito, com flags de nomes diferentes:

| | Chave de **dono** | Chave da **sessão nativa** |
|---|---|---|
| O que é | `--session-key`; o `begin` a gera; só em `owner.session_key` do ledger local ignorado, nunca na thread pública | `sha256(host\0session_id)`, derivada do ID nativo; o hook a entrega no contexto |
| Serve para | **autorizar a escrita** — só o dono muda o ledger | **só o vínculo**: `bind --native-key`, que a statusline e o hook usam para achar o ledger da sessão |
| Quando muda | nunca durante a execução: sobrevive a `/clear` e à compactação | quando o host abre outra sessão (`/clear`, `fork`, conversa nova) |

A separação existe porque o ID da sessão muda onde a execução não pode mudar: se a autorização
dependesse da sessão nativa, um `/clear` no meio do card tiraria a escrita do próprio Manager. Mutação
com a chave nativa sai `3` (`dono-divergente`), e o `bind` recusa `--session-key` (exit `2`). O Manager
não conhece o `session_id` bruto: o hook informa a chave derivada, e o ID bruto **nunca vai para o
disco nem para a saída** (`bind --session-id` existe só para quem o tem, e grava apenas o hash).

O vínculo é um arquivo por sessão, `v1/sessions/<chave nativa>.json` (contrato em
`orq/schemas/progress-binding-v1.json`): host, caminho canônico e `run_id` do ledger e os contadores do
lembrete. O `bind` não transfere ownership e não toca no ledger; tem as mesmas garantias de gravação
(realpath e contenção, Git ignorando o destino real, lock próprio, troca atômica). Mesma sessão e mesmo
ledger é idempotente; mesma sessão e outro ledger **substitui** o vínculo e zera os contadores; binding
de `schema_version` desconhecida não é refeito (outro host pode ter um plugin mais novo na mesma
frente). Só `claude` e `codex` têm sessão nativa a ligar.

**Hooks consultivos.** `orq/scripts/progress-hook.py` é só o adaptador; a regra mora em
`progress.py`. Os dois hooks só acrescentam contexto para o modelo:

- **Quando falam.** `SessionStart` entrega a chave da sessão nativa e a instrução de vincular — só
  quando a frente já tem `sessions/`. Como a sessão que roda o primeiro `begin` já passou do
  `SessionStart` (`sessions/` ainda não existia), o **primeiro `PostToolUse`** da sessão principal sem
  vínculo anuncia a chave uma vez e grava `sessions/.anunciada-<chave>.json`. Depois do vínculo, o
  `PostToolUse` conta chamadas de ferramenta enquanto o ledger está ativo e **sem plano**; no **4º**
  evento emite UM lembrete para registrar o `plan` e grava `nudged`. Card só conta com o board em
  `[~]` — em planejamento, gate ou validação não registrar plano é o esperado, e quem decide isso é o
  board, nunca a atividade declarada no ledger; goal não tem board e conta sempre, até o plano
  existir. Pausa, execução encerrada e chamada de subagente (`agent_id`) nunca contam; a elegibilidade
  é conferida de novo dentro do lock do binding, para que um `plan` que termina no meio do caminho
  também impeça o lembrete. A contagem deduplica por hash (nunca guarda o ID bruto), numa janela de 128.
- **Por que nunca bloqueiam.** O hook roda em toda chamada de ferramenta de todo projeto com o plugin
  instalado, e o medidor é telemetria que não decide nada: qualquer falha (payload, lock, permissão,
  Git, núcleo ausente) sai `0` sem saída, e a resposta é sempre só `additionalContext` — nunca
  negação, bloqueio nem continuação forçada. O lembrete é contexto, não prova de que falta plano: com
  o plano ainda em aprovação, o Manager o ignora.
- **O que não leem.** Nem o transcript, nem `tool_input`, `tool_response` ou o texto do prompt; só
  `session_id`, `cwd`, nome do evento, fonte do `SessionStart`, `agent_id` e os identificadores da
  chamada. Sem `PLUGIN_ROOT` nem `CLAUDE_PLUGIN_ROOT` no ambiente o host é desconhecido e nada acontece.
- **Contenção.** O hook e a statusline só abrem o `ledger_path` do binding depois de resolvê-lo por
  realpath e provar que é um ledger **desta frente**, no layout padrão. Binding adulterado, ou ledger
  trocado por symlink depois do `bind`, não é aberto: o hook cala e a statusline mostra a
  indisponibilidade com o código.
- **Custo.** O adaptador faz a saída rápida **antes de importar** o núcleo: sem medidor só `json`, `os`
  e `sys` são carregados e a decisão sai de `stat` nos ancestrais do `cwd`, porque importar o núcleo
  custa mais (~130 ms) que o resto do processo. Medido em 2026-10-04 com `/usr/bin/python3`: ~36 ms por
  chamada sem medidor. Com medidor, o núcleo é importado e Git e board são consultados com timeout
  curto (1 s), e o lock do vínculo espera no máximo 1 s.

**Statusline do Claude.** O `statusline.sh` acrescenta ao fim da segunda linha o segmento
da sessão (`◎ T-146 · revisão · 7/9 · 80%`): a mesma linha do `show --format segment`, calculada por
`progress.py statusline --host claude --input -`, que só lê e sempre sai `0`. A sessão é achada pelo
`session_id` do JSON da barra — o programa deriva a chave nativa e procura o binding nas frentes do
`cwd`, de `workspace.current_dir` e de `workspace.project_dir`. **Não escolhe "o ledger mais
recente"** nem adivinha por horário ou título: mostrar o andamento de outra execução da frente seria
um percentual inventado. Sem `session_id` ou sem vínculo, o segmento some; binding ou ledger que
existem mas não servem aparecem como `◎ medidor indisponível (<código>)`.

- **A barra fica idêntica à de antes do medidor** sem `jq`, sem `python3`, sem o `progress.py` ao lado
  ou fora de um projeto com `.orq/progress/v1/sessions/`. O pré-filtro é em shell, com leitura única do
  stdin (o JSON é reenviado ao Python) e **caminho físico** (`cd -P`/`pwd -P`): o `cwd` do payload pode
  ser um alias cujo pai lexical não é o da frente, e o pré-filtro tem de concordar com o `realpath` do
  Python.
- **Custo:** ~+110 ms por render com a sessão vinculada (medido em 2026-10-04).
- **Codex:** a statusline nativa segue independente. O plano nativo (`update_plan`) não é espelhado
  pelo ledger; a decisão de um espelho opt-in é do dono e vai com a fase 3 (`T-147`).

**Instalação da statusline.** A barra instalada por `/orq:init` é uma **cópia fora do plugin**, e o
segmento do medidor depende de arquivos irmãos: o `/orq:init` instala sempre o trio indivisível
`statusline.sh` + `kanban-status.sh` + `progress.py` (o `progress.py` acha o `kanban-status.sh` do
mesmo jeito, por vizinhança). O `progress-hook.py` não entra nessa cópia: os hooks vêm do bundle
`hooks/hooks.json` do plugin. A cópia leva o stamp de versão na linha 2 (no `progress.py` ela fica
entre o shebang e o docstring: é comentário). Cada operação que toca os três registra **antes** o hash
de referência — do original (para o backup) e do conteúdo novo (antes do `mv`) — e o rollback decide
arquivo a arquivo, contra essa referência: o que ainda é exatamente o que a operação instalou é
restaurado ou removido; o que divergiu (conteúdo, link simbólico ou ausente) é **preservado e
relatado**, e o conjunto pode ficar misto. A razão: o conteúdo que se encontra no disco depois de uma
operação não prova autoria, e restaurar ou apagar por cima de uma alteração concorrente destruiria
arquivo que não é nosso. Instalação anterior ao medidor tem só o par: o `--reinstalar` propõe o trio,
nunca o recompleta sozinho.

**Fora desta fase (`T-147`, fase 3).** O procedimento do Orca e o `watch` multi-raiz; antes deles, a
decisão do espelho opt-in do plano nativo do Codex. O mod de barra do Claude Code e a estimativa de
tempo ficam fora do medidor.

**Riscos aceitos e limites conhecidos.**

- Só POSIX foi exercitado. O lock do Windows (`msvcrt.locking`) tem teste apenas com backend
  simulado, sem prova em Windows real; sistema de arquivos remoto também não foi testado.
- A prova de cobertura usa `git check-ignore --no-index` e só foi exercitada com o Apple Git
  2.50.1.
- Com um `.gitignore` de `.orq/progress` **parcial** (preexistente, que ignora o ledger mas não o
  temporário real), o temporário nasce vazio antes de o Git ser consultado. Se o Git não o ignora, é
  removido e nada é gravado, mas nesse instante um `git add -A` concorrente poderia indexar o
  arquivo vazio. O `.gitignore` de `*` que o `begin` cria não abre essa janela.
- Um `begin` recusado nessa prova final pode deixar vazios os diretórios `v1`, `cards`, `goals`,
  `sessions`, `locks` e o arquivo de lock, todos ignorados; nunca sobra ledger nem temporário.
- **TOCTOU local, em dois pontos.** (1) Entre a conferência de contenção (realpath) e a criação dos
  diretórios ou o `open` do ledger e do vínculo, um symlink trocado por outro processo escaparia da
  checagem — o `open` é comum, sem `O_NOFOLLOW`. (2) No rollback do `init`, entre a conferência do hash
  e o `mv`/`rm` sobra uma janela mínima; por isso a conferência vem imediatamente antes de cada
  operação e nada é sobrescrito ou apagado sem ela. Os dois pressupõem outro processo local com
  permissão de escrita na frente ou no destino da cópia; a chave de dono não é ACL.
- **Python por render numa sessão não vinculada.** O pré-filtro da barra só olha se há `sessions/` no
  diretório ou acima; numa frente que o tem, toda sessão sem vínculo (inclusive a que acabou de dar
  `/clear`, antes do novo `bind`) paga o Python a cada render e não mostra segmento (~+100 ms,
  medido em 2026-10-04).
- **Anúncio duplicado.** Numa frente que já tem `sessions/` no `SessionStart`, a chave nativa chega
  nele e de novo no primeiro `PostToolUse` sem vínculo, porque o `SessionStart` não grava o marcador
  `.anunciada-<chave>`. São no máximo dois avisos iguais, não um erro; o `bind` os encerra.
- **`cwd` fora de `front_root`.** O hook acha o vínculo subindo a partir do `cwd` do payload (a
  statusline também olha `workspace.current_dir` e `workspace.project_dir`). Sessão cujo `cwd` não
  está dentro da frente dona do ledger — por exemplo, num worktree irmão — não encontra o vínculo: o
  hook cala e a barra não mostra segmento. Não há busca fora da frente, de propósito.
- **Atualizar o plugin com sessão Codex viva (`T-093`, preexistente).** O Codex resolve o caminho do
  hook no boot, com a versão instalada então, e a atualização apaga essa versão do cache: o comando do
  hook falha **antes** do adaptador (`can't open file`), então o exit `0` garantido por
  `progress-hook.py` não vale nesse caso — vale para todo hook do plugin, o do medidor inclusive. Não
  atualize o plugin no Codex com trabalho rodando lá (ver `memory/gotchas.md`).
- Remover a frente apaga o ledger e os vínculos; por isso o checkpoint registra o resultado na thread
  antes.

## A memória (wiki)

Papel de cada arquivo — regras completas em `memory/wiki/_schema.md`:

| Arquivo | Papel |
|---|---|
| `memory/MEMORY.md` | índice — leia primeiro |
| `memory/wiki/<tópico>.md` | como funciona **hoje**, reescrita quando muda |
| `memory/wiki/threads/` | trabalho em curso, com "RETOMAR AQUI" |
| `memory/wiki/KANBAN.md` | o board |
| `memory/fixes-history.md` | log cronológico, append-only |
| `memory/gotchas.md` | armadilhas que já causaram bug |

**A distinção que faz funcionar:** o log responde *"o que aconteceu naquele dia"* (append, imutável);
a página de tópico responde *"como funciona hoje"* (**reescrita**). Sem a página, a segunda pergunta
vira arqueologia no log.

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
  sessão aberta e máquina ligada; se ela suspender, o trabalho pausa e retoma depois. Implementação
  noturna (não só planejamento) segue fora — só entra depois de pilotos do modo planejamento.
- **`manager` não é configurável** pelo elenco — é a sessão principal, definida pelo `/model`.
- **Agent teams são experimentais**, mais caros e não isolam arquivos automaticamente.
- **"Só o Manager move cards" pode não ser enforçável por hook** como as regras invioláveis supõem:
  depende de o payload distinguir subagente da sessão principal, o que ainda não foi verificado
  (`T-002`, em backlog).
- **O degrau barato do host Codex em escrita real segue sem medição.** Um smoke comprovou só que o
  modelo responde a uma chamada trivial; comportamento em `workspace-write` (o modo real do
  implementer) e os reasoning efforts aceitos são pendência registrada em `_elenco.md`.

## Continuidade de execução aprovada

O contrato canônico está em `orq/skills/orq/SKILL.md`, na seção
`Contrato de continuidade aprovada`. As permissões local, externa e Git são
independentes: o registro humano durável por card sustenta somente a execução
local no escopo aprovado. Checkpoint e compactação preservam o registro e seus
limites; não transformam plano, READY, reviewer, log ou pacote em autoridade.
