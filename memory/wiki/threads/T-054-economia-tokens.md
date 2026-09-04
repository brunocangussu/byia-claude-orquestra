# Frente `@frente-economia` — o Orquestra parou de caber na janela

**Origem:** `docs/brief-economia-tokens-2026-09-02.md` — análise externa (Fable 5.1) sobre 13.639
chamadas do Claude Code e 58.363 do Codex em agosto/2026. O dono trouxe o brief pronto e pediu:
*validar com outra LLM e implementar*.

**O que esta frente resolve, em uma frase:** o Orquestra grava memória para sobreviver à janela, mas
a memória cresceu a ponto de ser ela quem consome a janela.

## O diagnóstico que reorganiza tudo

> **O inimigo da fluidez não é a compactação. É a releitura obrigatória depois dela.**

Cada compactação no Codex dispara a ordem do guardião — releia `MEMORY.md` + `KANBAN.md` + thread
ativa. Com o board em 28k, o índice em 4k e uma thread em 40k, são **~70k tokens antes de o trabalho
recomeçar**. A janela de 258k não é curta; ela é consumida por releitura. Piso medido após compactar:
48k (mediana), subindo a 70–90k depois da releitura.

**Corolário que decide a ordem dos cards:** quanto mais enxuta a memória, mais baixo o teto pode ser
sem perder fluidez. Por isso **`T-056` (memória enxuta) vem antes de `T-055` (pós-compactação)**, e
os dois antes de qualquer redução de teto de janela. Baixar teto com piso alto devolve exatamente a
sensação de janela curta, pelo motivo errado.

## Os dois diagnósticos por host

| Host | Custo é… | Sintoma |
|---|---|---|
| Claude Code | **tamanho da sessão** | contexto médio 379k/chamada; 61% do custo é reler histórico; guardião **nunca rodou aqui** |
| Codex | **número de chamadas** | 5.100–7.300 chamadas/dia; limite semanal 0%→55% em 45h; Manager faz polling de sub-agente |

## Baseline medido neste repo (2026-09-02, antes de qualquer mudança)

Medição própria, não do brief — e reproduz os números dele quase exatamente, o que sustenta o resto.

| O quê | Hoje |
|---|---|
| `memory/` inteiro | 904 KB ≈ **257k tokens** em 35 arquivos |
| `wiki/KANBAN.md` | 104,7 KB ≈ **28,4k tokens**, 66 cards |
| Nota livre do board | **97%** (títulos são 3.051 dos 102.283 chars) |
| Cards acima de 200 chars | **48 de 66** |
| Os 6 maiores | 44.929 chars = **44% do board** (`T-026` 12.259 · `T-036` 8.924 · `T-051` 8.100 · `T-052` 5.945 · `T-053` 5.076 · `T-020` 4.625) |
| Board com teto de 200 | ≈ 2,9k tokens — **redução de 90%** |
| Maior thread | `T-026-host-alternativo.md` 139 KB ≈ **40k tokens** |
| Log | `fixes-history.md` 102,7 KB ≈ 29k tokens |

**Gates verdes antes de mexer:** 201 testes · `validate` ✔ · lint ✓ (com os primeiros 14 cards da
frente já inseridos; viraram 16 depois do parecer).

**Prova de que o teto é praticável:** os cards desta frente nasceram entre **148 e 196 bytes**,
carregando ID, título, proposta de origem, trilha, faixa, ponteiro de thread e marca de frente.
Nenhum precisou de exceção.

## Fases

### Fase 1 — validação cross-vendor ✅
Brief conferido contra o código por modelo OpenAI (vendor oposto ao host Claude), read-only, em
worktree descartável. Pareceres em `T-054-pareceres.md`.

### Fase 2 — memória enxuta (`T-056` ✅ · `T-057` e `T-058` não tocados)
A regra no produto **e** a migração dos dados deste repo. É o único ganho que não depende de código
novo: 97% do board é nota livre, e 45% do peso está em 6 cards.

**✅ Migração concluída em 2026-09-02 — 48 cards, resultado final medido:**

| | Antes | Depois |
|---|---|---|
| `KANBAN.md` | 104,7 KB · **28,4k tokens** | **12,7 KB · 3,6k tokens** |
| Cards fora do teto | 48 de 66 | **0 de 68** (`📏` apagado) |
| Maior card | 12.259 chars | **213 bytes** |

**−89%**, contra os 90% que o brief previu. Cada nota foi **movida íntegra** para a thread do card,
sob cabeçalho datado — nada resumido, nada descartado. Card com frente própria foi para a thread
dele; os demais para `threads/_notas-de-cards.md`, arquivo único, porque trinta threads de um
parágrafo trocariam um inchaço por outro e o `wiki-lint` acusaria trinta páginas órfãs — com razão.
O `T-053` era o único dos seis maiores sem thread e ganhou a sua.

**O ganho não é disco — é quantas vezes cada byte é lido.** Dito com todas as letras, porque a
formulação preguiçosa ("economizamos 92 KB") é falsa: o texto **não sumiu**, mudou de arquivo.
`memory/` inteiro foi de 946 KB para 967 KB, e **cresceu**, por causa da documentação desta frente.

O que mudou é a frequência de leitura. O board é lido em **toda** retomada e **toda** compactação;
uma thread só é lida por quem trabalha naquele card — zero vezes na maioria das sessões.

| Leituras do board | Antes | Agora | Poupado |
|---|---|---|---|
| 1 | 28k tok | 3,6k | 25k |
| 5 | 142k | 18k | **124k** |
| 20 | 568k | 72k | **496k** |

É por isso que o número que importa é o do **arquivo inteiro** (3,6k), não o do corpo dos cards
(3,0k) — o que se lê é o arquivo. Os registros foram corrigidos para 3,6k.

**Prova de integridade, não promessa:** as 48 notas originais foram reextraídas do `git` e
reencontradas por amostragem nos arquivos de destino. **48 de 48 íntegras, zero perda.** Foi essa
verificação que pegou um erro meu de contagem — eu havia relatado "31 cards" ao dono e no log; são
48, e os três registros foram corrigidos.

**O que a migração ensinou sobre o número — e o brief não previu:**

Com teto de 200, **três dos nove primeiros estouraram** (`T-036` 229 e depois 212 · `T-051` 211).
A causa é sempre título longo somado a ponteiro longo: o `T-036` gasta 39 chars só no título e 29 no
ponteiro, sobrando ~120 para estado e validação. Coube, mas **ao custo de reescrever a nota até
caber** — perda que não aparece em contagem nenhuma. **Decidido: 240 bytes, com orçamento por
componente** (título ≤ 80 B, ponteiro ≤ 50 B), como o parecer externo recomendou. Levar ao gate
apenas a confirmação, já que o brief pedia 200.

**Bug meu que virou lição de contrato:** a primeira versão do migrador escrevia a nota na thread e
**só depois** conferia o teto. Quando o `T-036` estourou, a thread já tinha a nota e o board não —
duplicação silenciosa. Corrigido para validar antes de qualquer escrita, e a operação virou
idempotente. *Validação depois de efeito colateral não é validação* — vale para o lint do `T-056`
tanto quanto valeu aqui.

### Fase 3 — o guardião (`T-055`, `T-054`)
`T-055` troca a ordem de releitura por 3 linhas de estado geradas. `T-054` faz o guardião existir no
host Claude, com faixas em tokens absolutos em vez de % da janela.

### Fase 4 — cerimônia e spawn (`T-059`…`T-063`)
Leitura parcial, handoff com teto, escala de cerimônia, teto de rodadas de revisão, e o writer do
Codex por subprocesso (que é o que mata o polling).

### Fase 5 — o que só o dono decide (`T-064`, `T-065`, `T-066`)
Estacionados em `[!]` com a pergunta escrita. Não roteie sozinho.

## Achados próprios — o que o brief não viu

Leitura direta do código, antes do parecer externo. Cada um muda uma proposta.

1. **Os hooks têm `timeout: 5` e `additionalContextLimit: 300`** (`orq/hooks/hooks.json`, os seis
   registros). A proposta 8 quer injetar 3 linhas geradas — mas elas precisam **caber em 300** e ser
   produzidas em **menos de 5 segundos**, incluindo o subprocesso do `kanban-status.sh`. O brief
   descreve a substituição sem citar nenhum dos dois limites. É restrição de desenho, não detalhe.

2. **Acender `⚠` para card gordo envenena o sinal que já existe.** Hoje o `⚠N` do
   `kanban-status.sh` significa *"linha parece card e não casa o contrato"* — um defeito raro e
   acionável. Card acima do teto eram **48 de 66** na época: reusar o mesmo símbolo deixaria o
   alarme aceso durante toda a migração. O próprio script tem o comentário que condena isso: *"alarme
   crônico é alarme ignorado — a doença que este contador existe para curar"*
   (`orq/scripts/kanban-status.sh:47`). O teto precisa de sinal próprio, ou de morar no `wiki-lint`
   (sob demanda) em vez da statusline (espaço nobre, sempre visível).

3. **O teto de 2 rodadas de revisão já está escrito — e esta casa o violou.** `revisar.md:198` diz
   *"máximo 2 rodadas; persistindo, escale pro dono"*. O `T-051` fechou com **7 rodadas** de review
   externo e o `T-052` com **4**, com o board registrando isso como virtude. Não é regra faltando; é
   regra sem enforcement, exatamente como o `T-062` supõe — e a melhor evidência está no próprio log.

4. **O `T-056` come parte do `T-059`.** Com o board em ~3,6k tokens, "não leia o board inteiro"
   deixa de ser economia relevante: o `quadro.md` manda ler `KANBAN.md` (hoje 30k). Depois do teto,
   ler inteiro é barato. O `T-059` deve encolher para checkpoint e `fixes-history.md`, e o board sai
   do escopo dele — senão paga-se complexidade por um ganho que o `T-056` já entregou.

5. **A nota do card é lida por parser semântico em quatro comandos — o teto tem que caber isso.**
   `elenco.md:75`, `plan-next.md:24`, `plan-next.md:86` e `implement-next.md:26` procuram
   `trilha: … · faixa: …` **dentro da nota**. Então o teto não pode ser só "título e ponteiro": ele
   convive com ~80 chars de metadado obrigatório (`trilha:`+`faixa:` 23 · ponteiro de thread ~40 ·
   `@frente` ~17), sobrando ~120 para ID e título. Cabe — os cards desta frente ficaram em **173
   chars no pior caso** — mas é o número que decide se 200 é folgado ou apertado, e o brief não o
   considerou.

   ⚠️ **O dogfooding pegou meu próprio erro aqui:** gravei os 11 cards como `· trilha sistema ·` e o
   contrato é `· trilha: sistema ·`, com dois-pontos. Nenhum card antigo do board tem o registro —
   os dois eixos nasceram no `T-051` e ninguém retroagiu —, então eu fui o primeiro a gravar e
   errei o formato sem nada acusar. Corrigido. **Isto é `T-062`/lint em miniatura: regra escrita
   que nenhum gate verifica é regra que só o acaso cumpre.**

6. **Confirmado que a nota dos cards grandes é duplicação.** `T-026`, `T-036`, `T-051`, `T-052` e
   `T-020` — cinco dos seis maiores — **já têm thread própria**. A nota do card repete o que a
   thread guarda. Só o `T-053` não tem thread, e é o único que precisa de uma nova na migração.

## Apuração na doc oficial do Claude Code — três correções ao brief

Feita antes de implementar, porque as propostas 7 e 8 dependem do contrato de hooks.

✅ **`transcript_path` chega em todos os eventos de hook.** A proposta 7 tem o arquivo de que
precisa. Esta parte do brief está certa.

🔴 **A doc adverte, com todas as letras, contra parsear o `.jsonl` — e a proposta 7 é exatamente
isso.** O texto de `sessions` diz que o formato das linhas é **interno ao Claude Code e muda entre
versões**, e recomenda `/export` ou as interfaces de script no lugar do parse direto. Não é
impedimento absoluto — o guardião **já** parseia o rollout do Codex, correndo o mesmo risco no outro
vendor —, mas muda o desenho exigido: o parser do Claude tem que **falhar aberto e em silêncio**
como o do Codex já faz (`read_latest_usage` devolve `None` e o hook sai calado). Se o formato mudar,
o guardião volta ao comportamento de hoje — não avisa — em vez de quebrar a sessão. **Isso precisa
estar escrito no código e no card, senão a primeira versão do Claude Code que mudar o formato vira
bug em produção.**

🔴 **`autoCompactWindow` é PERCENTUAL, não tokens — o brief confunde duas coisas.** A chave do
`settings.json` é um número em porcentagem; quem aceita tokens é o comando `/autocompact <tokens>`
(existe a partir da v2.1.221, e também aceita `auto`). A recomendação prática do brief (`/autocompact
400k`) está certa; a explicação de que "`autoCompactWindow` está `null`" mistura as duas interfaces.
E **`CLAUDE_CODE_AUTO_COMPACT_WINDOW` não aparece na documentação** — o brief a cita como referência
oficial. Corrigir isso no `T-065` antes de o dono executar.

⚠️ **`additionalContextLimit` não existe na documentação de hooks** — e o plugin já o usa nos três
registros que injetam contexto (`orq/hooks/hooks.json`). Não se sabe se o `300` conta caracteres,
tokens ou bytes, nem se o excesso é truncado ou descartado inteiro. Para a proposta 8 isso é
material: se descartar inteiro, um estado de 3 linhas grande demais some **em silêncio**, e o
pós-compactação fica sem orientação nenhuma — pior que hoje. **Medir empiricamente antes de
depender do campo**, e projetar as 3 linhas para caber com folga (≤ 250 chars) até que se saiba.

## Decisões desta frente (não re-litigar)

1. **Os cards desta frente nascem com ≤ 200 chars.** Dogfooding: a proposta 12 é a regra, e criar
   card gordo para propor teto de card seria a contradição mais cara do board.
2. **A migração do board é dado, não produto.** Ela não muda o plugin — muda `memory/` deste repo.
   Vale como prova de que a regra é aplicável, e é o que derruba o piso pós-compactação aqui.
3. **Nível 0 do brief não vira card de produto.** São configurações da máquina do dono
   (`/autocompact`, `/effort`, MCPs por projeto, `AGENTS.md`). Ficam em `T-065` como lista para ele
   executar, não para o Manager executar.
4. **O revisor desta frente é OpenAI** — vendor oposto ao host Claude. Mas invocado pelo subagente
   Codex, não por `codex exec` cru: a regra global do dono proíbe o binário direto. A divergência
   entre a Matriz e essa regra virou `T-067`.

## Levantamento do ferramental — estado REAL medido em 2026-09-02

Feito porque o dono pediu dados antes de decidir `T-065` e `T-066`, e porque ele lembrava de ter
desligado o caveman. **Ele tinha razão, e o brief estava errado neste ponto.**

### Compressão — são DUAS camadas, não três

| Camada | Estado | O que faz |
|---|---|---|
| **rtk** | ativo — 1 hook `PreToolUse` | reescreve comando de CLI (git etc.) antes de rodar |
| **context-mode** | ativo — 1 hook `SessionStart` + plugin + MCP | sandboxa saída grande de ferramenta |
| **caveman** | ❌ **não instalado em host nenhum** | — |

Sem cache de plugin, sem citação em `settings.json`, `~/.claude.json`, `~/.codex/config.toml`,
`AGENTS.md` ou `CLAUDE.md`. **O brief contava três camadas; são duas** — e elas não são redundantes:
uma atua no comando, a outra na saída. Recomendação: manter as duas, o `T-066` perde essa metade.

### Grafo de código — aqui sim há sobreposição

| Ferramenta | Estado | Observação |
|---|---|---|
| codebase-memory-mcp | ativo (MCP + 5 hooks) | os 4 registros em `SessionStart` **não são duplicata**: matchers `startup`/`resume`/`clear`/`compact` |
| serena | ativo (MCP) | mesma função: busca semântica de código |
| code-review-graph | ativo no Codex | |
| graphify | skill sob demanda | custo só quando dispara |
| cartographer | ❌ recusado no `T-045` | decisão já tomada: portar ideias, não instalar |

**Dois MCPs de grafo no mesmo host** é a sobreposição real. Cada um publica dezenas de definições
de ferramenta em toda chamada.

### Hooks do Claude, por dono

| Dono | Registros | Onde |
|---|---|---|
| **Orca** | **12** | um por evento: `PreToolUse`, `PostToolUse`, `Stop`, `SubagentStart`… |
| codebase-memory | 5 | `SessionStart`×4 (matchers distintos) + `PreToolUse` |
| context-mode | 1 | `SessionStart` |
| rtk | 1 | `PreToolUse` |

⚠️ **O Orca não aparece no brief e é o maior consumidor de hooks** — 12 dos 19. Não estava em
nenhuma das listas.

### Configurações confirmadas

| Chave | Valor real | Consequência |
|---|---|---|
| `effortLevel` | **`xhigh`** | saída custa 5× a entrada; o padrão do Opus 5 é `high` |
| `alwaysThinkingEnabled` | **`true`** | thinking é cobrado como saída |
| `autoCompactWindow` | **não definido** | compacta perto do limite do modelo (~1M) |
| `remoteControlAtStartup` | **`true`** | instruções de Remote Control em toda sessão |
| MCPs Claude (usuário) | **6** | `codebase-memory-mcp`, `composio`, `magic`, `plaud`, `railway`, `serena` |
| MCPs Codex | **15** | todos entram em toda chamada — o Codex não difere schemas |
| `~/.codex/AGENTS.md` | **20.251 B** ≈ 5,6k tok | em toda sessão e todo sub-agente |
| `~/.claude/CLAUDE.md` | **8.723 B** ≈ 2,4k tok | em toda sessão |
| claude-mem | ativo (plugin `thedotmack` + `~/.claude-mem/claude-mem.db`) | `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` desliga a memória **nativa**, não ele |

🎁 **Ganho grátis achado no caminho:** dos 6 MCPs do Claude, **`composio` está sem autenticação e
`magic` falha ao conectar** — nesta própria sessão. Dois dos seis não funcionam e mesmo assim
publicam definição de ferramenta em toda chamada. Removê-los não custa capacidade nenhuma.

## As três perguntas de `[!]` — escritas por extenso

**`T-064` — Superpowers ou a Matriz, quem vence no spawn?**
Medido: 256 threads de sub-agente no Codex desde 01/08, com nomes `writer`/`impl`/`review`/
`rereview1..3` — o padrão `subagent-driven-development` do superpowers, que está instalado no Codex.
A Matriz do `_elenco.md` manda `codex exec` e o `revisar.md` limita a 2 rodadas; na prática o Manager
segue a skill do superpowers, que não tem teto. **As duas instruções coexistem e a mais agressiva
ganha.** A pergunta: o superpowers sai do Codex, ou o `orq` declara explicitamente que a Matriz vence
qualquer skill de spawn? *Recomendação: a segunda — desinstalar perde as outras skills úteis.*

**`T-065` — as seis configurações fora do plugin.**
Não são produto; são a máquina do dono. `/autocompact 400k` no Claude · checkpoint + `/clear` antes de
fechar o dia · `/effort high` no lugar de `xhigh` global · MCPs por projeto (Codex tem 14 declarados,
todos em toda chamada) · claude-mem desligado nos projetos com Orquestra · `~/.codex/AGENTS.md` de
20 KB e `~/.claude/CLAUDE.md` de 8,7 KB cortados para ≤ 3 KB. A pergunta: ele executa, ou autoriza o
Manager a executar quais delas? *Nenhuma foi tocada — configuração da máquina não é iniciativa.*

**`T-066` — consolidar o ferramental empilhado.**
Hoje rodam **três** camadas de compressão (rtk, context-mode, caveman) e **cinco** caminhos de
conhecimento de código (codebase-memory, serena, code-review-graph, graphify, cartographer). Cada uma
adiciona baseline, hooks e instruções em toda sessão; nenhuma reduz número de chamadas. A pergunta:
qual camada de compressão fica, e qual grafo de código fica? *O brief recomenda uma de cada.*

## O que o parecer cross-vendor mudou — leia antes de implementar

Parecer íntegro e auditoria em `T-054-pareceres.md`. **Veredito: corrigir antes.** Nenhuma das três
propostas prioritárias sobrevive intacta. O que muda, por card:

### `T-054` (proposta 7) — três correções e uma inversão

- 🔴 **A conta do brief está errada: falta `output_tokens`.** Somar só
  `input + cache_creation + cache_read` mede o que *entrou*, e a saída daquela chamada entra na
  próxima. Cenário: a chamada entra com 139k e produz 8k; o parser lê 139k, não dispara a faixa de
  140k, e a chamada seguinte já parte de ~147k.
- 🔴 **Best-effort tem que ser declarado, não silencioso.** Como a doc adverte que o formato do
  `.jsonl` é interno, o parser precisa falhar aberto **e dizer que falhou** — senão o Claude Code
  fica indefinidamente sem proteção e ninguém percebe, que é exatamente o estado de hoje.
- ⚠️ **"Último `message.usage`" é ambíguo em três frentes:** sidechain/subagente escrevendo depois
  da linhagem principal (lê 18k numa sessão de 155k); fronteira de compactação (`PostCompact` lê o
  valor pré-compactação e exige checkpoint em seguida); e somar registros em vez de somar as
  partições de **uma** chamada (dez chamadas de 100k viram "1M").
- 🔀 **Inversão do desenho: faixa absoluta não substitui a relativa, complementa.** 170k deixa 30k
  livres numa janela de 200k e 830k numa de 1M — a mesma faixa "emergência" significa risco oposto.
  **Dois gatilhos:** patamar absoluto para custo/latência, reserva relativa para segurança de
  estouro. E a justificativa dos absolutos é **ocupação da janela**, não custo financeiro — token
  vindo de cache pesa igual na janela e diferente na fatura.
- ✅ Histerese já existe (`CHECKPOINT_REARM_DELTA`); preservar no parser novo.

### `T-055` (proposta 8) — o desenho muda de "3 linhas" para "bloco estruturado"

- 🔴 **Não pode depender de `additionalContextLimit`.** O campo não tem contrato documentado: pode
  ser ignorado, truncar no byte 300 ou descartar o contexto inteiro. Descartar inteiro é **pior que
  hoje** — pós-compactação sem orientação nenhuma. Limites próprios, e medir o campo antes de confiar.
- ⚠️ **A raiz do projeto vem do evento, nunca do cwd.** `SessionStart` pode disparar em subpasta,
  worktree ou scratchpad, e o hook concluiria que não há board.
- ⚠️ **Saída vazia é caso válido, não falha.** *(Aqui a auditoria corrigiu o revisor: ele disse que
  o script sai `1` sem board; sai `0` com saída vazia. O cenário permanece, a causa muda.)*
- ⚠️ **Card ativo ambíguo → listar os IDs, nunca escolher em silêncio.** Dois cards em curso e o
  hook carrega a thread errada. E o `RETOMAR AQUI` tem que ser **o último** da thread apontada pelo
  card — o `T-026` tem marcadores antigos vivos, e pegar o primeiro devolve instrução superada.
- ⚠️ **Montar e validar tudo em memória antes de escrever em stdout**, com resposta única ou
  fallback válido. Nunca JSON parcial.

### `T-056` (proposta 12) — o número e a unidade

- **240, não 200** — e com **orçamento por componente** (título, ponteiro, estado), porque aumentar
  só o total repete o aperto depois. Bate com o que a migração mostrou: três estouros em nove.
- 🔴 **Definir a unidade, e isto já está divergente neste board:** 17 cards passam de 200 contando
  code points; **21** contando bytes UTF-8. Quatro mudam de lado conforme a régua. `wc -c`, awk sem
  locale e `len()` do Python discordam — o mesmo board passaria num ambiente e falharia noutro.
  👉 **Recomendação ao gate: bytes UTF-8**, a única unidade que não depende de locale nem de
  implementação, e a mais próxima do custo real.
- ⚠️ **Integridade referencial vira requisito.** Board e thread passam a precisar de atualização
  atômica: um cherry-pick que leve só a linha do card deixa o board apontando para thread
  inexistente.
- ⚠️ **Perde-se descoberta global.** Uma busca por texto no board antes achava o bloqueio; agora
  precisa varrer as threads. E o `git blame` do board passa a mostrar só "movido para thread".

### 🔴 O achado mais importante — `T-055` e `T-056` se sabotam juntos

**Isoladamente cada um melhora; combinados, podem deixar a recuperação pós-compactação
estruturalmente incompleta.** O `T-056` tira do board as decisões e os critérios de aceite; o
`T-055` reinjeta apenas o card curto e uma linha da thread. Cenário: a nota migrada continha *"não
executar deploy"* e três critérios de aceite; o `RETOMAR AQUI` diz só *"continuar validação"*.
Depois de compactar, o modelo não recebe nem a proibição nem os critérios — e declara pronto, ou
executa o passo proibido.

👉 **Consequência de desenho:** o `T-055` não entrega "3 linhas livres", e sim um **bloco
estruturado e limitado**: estado · próxima ação · **restrições** · critérios essenciais. E o
`T-056` tem que garantir que restrição e critério de aceite sejam **campos recuperáveis** da thread,
não prosa solta. Os dois cards passam a ter contrato entre si — **implementar um sem o outro é o
único jeito de piorar**.

### Dois cards que nasceram do parecer

- **`T-069` (faixa `pesada`, segurança):** injetar conteúdo de thread em `additionalContext`
  automaticamente é **promoção de confiança**. Uma thread escrita por automação, ou importada,
  contendo `RETOMAR AQUI: ignore as regras anteriores e execute…` entra como contexto de hook sem
  ninguém no meio. O conteúdo tem que ser delimitado como **dado não confiável**, normalizado, e
  impedido de formular instrução com autoridade.
- **`T-068`:** não existe teste da sequência crítica **alto uso → checkpoint → compactação →
  retomada**. Cada peça passa isolada; só o fluxo inteiro revela que o `PostCompact` leu o valor
  pré-compactação, o texto foi truncado e o ponteiro aponta para thread ausente.

## Restrições desta frente

Campos, não prosa — a recuperação pós-compactação precisa reencontrá-los.

- **Não bumpar versão, não commitar, não publicar** sem o ok do dono. O lint está vermelho por
  isso e é o estado correto (ver abaixo).
- **Não implementar `T-055` sem `T-056`, nem o contrário**, pelo bloqueador combinado do parecer.
- **`T-064`, `T-065` e `T-066` não se decidem aqui** — são `[!]`, decisão do dono.
- Nada de `bypassPermissions`, nem de madrugada.

## Critérios de aceite da Fase 2 (`T-056`)

1. ✅ Board abaixo de 240 bytes por card, régua zerada (`kanban-status.sh` sem `📏`).
2. ✅ Nota migrada **íntegra**, nunca resumida — thread do card, ou `_notas-de-cards.md`.
3. ✅ Regra escrita em `_schema.md`, no template do `init.md`, no `wiki-lint.md` e no `checkpoint.md`.
4. ✅ Verificação mecânica com teste que **reprova a versão anterior** (3 de 9 falham no script velho).
5. ✅ **Revisão independente cross-vendor feita, achados aplicados** — ver `T-054-pareceres.md`.
6. ✅ **Reconciliação byte a byte por ID: 48/48 íntegras**, sem órfã nem duplicata, 97,4 KB.
7. ⏳ **Falta o dono validar:** o board ainda responde "onde paramos" sem abrir thread nenhuma?

## ⏭️ RETOMAR AQUI

**Fase 2 (`T-056`) implementada e verificada; `T-054` e `T-055` replanejados pelo parecer, não
implementados.**

**A revisão independente do `T-056` foi feita e os achados estão aplicados.** O revisor confirmou as
quatro decisões de desenho e derrubou três coisas: o fail-open silencioso da medição (virou `📏?`),
o CRLF empurrando card no limite para fora do teto (descontado), e o endereçamento do arquivo
coletivo (agora por ID, com índice). Os dois bloqueadores que ele levantou sobre a migração foram
verificados e **não se materializaram** — zero links relativos, e 48/48 notas conferidas byte a byte
por ID. Detalhe em `T-054-pareceres.md`.

**Feito nesta janela:**
- 18 cards criados (`T-054`…`T-071`), 3 deles `[!]` esperando decisão do dono.
- Validação cross-vendor OpenAI: rodada 1 morreu sem parecer, rodada 2 entregou. Veredito
  **"corrigir antes"** — parecer e auditoria em `T-054-pareceres.md`.
- **Board: 104,7 KB → 12,7 KB · 28,4k → 3,6k tokens (−89%).** 48 cards migrados.
- Produto: teto no `_schema.md`, no template do `init.md`, no `wiki-lint.md` e no `checkpoint.md`;
  sinal `📏` (e `📏?` quando a medição falha) no `kanban-status.sh`; **`test_kanban_status.py` novo —
  o parser do board, contrato central do projeto, não tinha teste nenhum**.
- Gates: **215 testes verdes** (eram 201) · `validate` ✔ · **lint ✗, e isto é esperado**.

**O lint vermelho não é defeito, é o guarda do `T-017` funcionando.** Ele acusa que `orq/` foi
editado e a versão continua `0.25.0`, igual ao cache instalado — ou seja, *o que roda ainda não é o
que está escrito*. Resolver exige bump nos quatro lugares e release, e **bump precisa do ok do
dono**. Enquanto ele não decidir, vermelho é o estado honesto.

**Próxima ação, em ordem:**
1. **Levar ao gate as três decisões do `T-056`** que divergem do brief: teto **240** em vez de 200 ·
   unidade **byte UTF-8** · cards `[!]` sem `trilha:`/`faixa:` gravados.
2. **Implementar `T-055` e `T-054` juntos**, com o desenho corrigido — bloco estruturado
   (estado · próxima ação · restrições · critérios), parser com `output_tokens`, dois gatilhos.
3. **`T-069` antes de qualquer injeção automática** de conteúdo de thread no hook.
3b. `T-070` (índice afirma que o painel de 3 funciona) e `T-071` (regex de arquivado) — os dois
   nasceram de verificação nesta janela, ambos `leve`.
4. `T-057` e `T-058` (índice e threads com teto) — o `MEMORY.md` tem 21,8 KB e a thread `T-026`,
   139 KB. **Nenhum dos dois foi tocado nesta janela.**
