---
name: orq
description: >
  Use when a project contains `memory/wiki/KANBAN.md` and the user requests any work change,
  implementation, fix, improvement, refactor, review, validation, or continuation. Also use for
  project status and resumption, recording decisions/cards, checkpoints and context cleanup, model
  roster or LLM-credit changes, memory recall, tool/setup diagnosis, capability discovery, and
  night-mode delegation. Trigger from natural language such as "quero", "vamos mudar", "tem um
  problema", "pode seguir", "onde paramos", "anota isso", "revisa", "quem está revisando",
  "lembra quando", "o que falta instalar", "vou dormir", "voltei" or equivalent phrasing, even
  when the user does not type `/orq`.
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

**No Codex, a interface oficial é linguagem natural ou `/skills`.** A pasta `commands/` não cria
`/orq:*` nesse host; esses slash commands pertencem ao Claude Code. Ausência de `/orq` no menu do
Codex não significa plugin ausente.

⚠️ **Fora do Claude Code (Kimi, ou Codex sem os commands instalados), os `/orq:*` citados na tabela
abaixo não existem como comando.** O procedimento é o mesmo: leia o arquivo `commands/<nome>.md`
(ex.: a linha "pode implementar" → `commands/implement-next.md`) — **não presuma que ele mora no
mesmo diretório desta skill**, isso só vale no Kimi.

Antes de ler qualquer command, resolva uma vez a **raiz do pacote instalado** e chame-a de
`ORQ_PACKAGE_ROOT`: no Claude é `${CLAUDE_PLUGIN_ROOT}`; no Kimi, use o diretório desta skill **só
se `commands/` existir ao lado** (o instalador cria esse layout); se não existir, suba como no
Codex até o ancestral do pacote. No Codex, suba a partir desta skill até o ancestral do pacote que
contém `.claude-plugin/plugin.json`, onde `skills/` e `commands/` são irmãos — nunca use
`skills/orq/commands/`. Se o diretório adjacente ou o ancestral do pacote não puder ser comprovado,
pare e declare a raiz ausente; não invente caminho. Toda referência
`ORQ_PACKAGE_ROOT/commands/<nome>.md` nos commands usa essa raiz já resolvida. Quando um command
legado citar `${CLAUDE_PLUGIN_ROOT}`, substitua pelo `ORQ_PACKAGE_ROOT` comprovado antes de executar;
fora do Claude, nunca passe a variável literal ao shell.

Siga o arquivo como se você tivesse acabado de "rodar o comando" — **até onde o host permitir, nunca
além disso**. Vários passos exigem primitiva que nem todo host tem: spawn de subagente com override
de modelo (`plan-next.md`, `revisar.md`), `isolation: "worktree"` (`implement-next.md`), spawn sem
`name`, `AskUserQuestion` e caminhos `.claude/agents/`/`statusLine` (`init.md`), `/clear`
(`checkpoint.md`). **Sem a primitiva, nunca finja**: não simule que houve subagente, painel ou
worktree — declare a degradação ao dono numa frase e faça o passo você mesmo, dizendo o que se
perdeu. Onde houver equivalente, use-o: no lugar de spawn em sessão, invoque o papel como
**subprocesso de CLI** do vendor daquele modelo (vendor do modelo == vendor do host → mecanismo
nativo; senão → CLI do vendor do modelo). Se existir, o projeto `memory/wiki/_elenco.md` governa o
time e a Matriz; sem ele, use o template em `ORQ_PACKAGE_ROOT/commands/elenco.md`. O comando do Opus
vem do runner nessa Matriz, nunca de memória do modelo. Gotchas específicos permanecem no elenco do
projeto; não repita nem improvise a regra aqui.

Fora do Claude, antes de executar qualquer papel: **identifique o host**, leia `## Times por host`,
resolva o papel e só então aplique a célula da `## Matriz de invocação`. “Configurado” não significa
“rodando agora”. Sem executor comprovado, declare a degradação e preserve o gate do card.

| Ele diz algo como… | Você faz |
|---|---|
| **"quero X" · "queria acrescentar Y" · "vamos fazer/criar/mudar Z" · "seria bom se" · "dá pra" · "tem um problema em W" · "isso está errado" · "não funciona" · "não gostei" · "precisa melhorar"** | **ROTEIA PELO CICLO** — é o caso mais comum e o mais fácil de errar. Cria o card, planeja, **para no gate**. Só implementa direto se for trivial pela escala acima |
| "pode começar" · "siga" · "siga com suas recomendações" · "pode ir" · "aprovado" · "manda ver" · "vamos seguir" · "perfeito, segue" | **AVANÇA** o que está no gate — se havia plano aguardando, é aprovação: vá para a implementação. Se não havia, o "siga" se aplica ao que você acabou de propor |
| "onde paramos?" · "o que falta?" · "cadê o board?" · "quais as pendências?" · "o que estamos fazendo?" · "o que preciso decidir?" | **Mostra o quadro** (`/orq:quadro`): esperando-ele primeiro, depois em curso e a validar |
| "terminamos" · "acabou essa parte" · "vamos limpar o contexto" · "pode reiniciar" · "salva aí" · "pode limpar" · "checkpoint" | **Checkpoint** (`/orq:checkpoint`): grava log + páginas + thread + board e verifica o board; no Codex libera a compactação nativa e a mesma conversa pode continuar, enquanto no Claude avisa que é seguro dar `/clear` |
| "vamos planejar X" · "próxima tarefa" · "o que vem agora?" | **Loop A** (`/orq:plan-next`) — e **pare** no gate pra ele aprovar |
| "pode implementar" · "manda ver" · "toca essa" · "aprovado" | **Loop B** (`/orq:implement-next`) — só se o card estiver aprovado |
| "anota isso" · "cria uma tarefa" · "isso vira card" · "não esquece disso" | **Cria o card** no BACKLOG com ID e contexto suficiente pra retomar |
| "revisa isso" · "manda revisar" · "valida isso" · "o que você acha desse código?" | **Painel de revisores** (`/orq:revisar`) — o revisor interno + os externos **ativos no `_elenco.md`**, em paralelo, achados reconciliados |
| "quem tá revisando?" · "troca o modelo do planner" · "quero o Fable planejando" · "tira o GPT" · "tô com pouco crédito" · "acabando os créditos" · "final do ciclo semanal" · "modo economia" · e qualquer pedido de sair do perfil ou voltar ao time normal | **Elenco** (`/orq:elenco`) — mostra ou ajusta qual LLM toca cada papel; frase de contexto de crédito troca o **time inteiro** pelo perfil nomeado (`perfil economia` / `perfil padrao`), anunciando o que muda, **o que se perde** e **como reverter** — sem depender de uma frase fixa de volta, que ele pede naturalmente quando o crédito voltar |
| "lembra quando a gente…?" · "o que a gente decidiu sobre…?" | **Busca a memória** (`/orq:lembrar`) + cruza com a wiki |
| "tá lento" · "o que falta instalar?" · "dá pra melhorar a performance?" · "que ferramenta ajudaria?" | **Stack** (`/orq:stack`) — detecta o que falta, mostra ganho e custo, instala **só o que ele aprovar** |
| "o revisor sumiu" · "a statusline está muda" · "não conecta com X" · "parece que o plugin não pegou" — queixa sobre o **ferramental** (plugin, revisor, statusline, MCP, PATH), nunca sobre o que o produto faz | **Diagnóstico** (`/orq:stack --verificar`) — checa plugin desatualizado (versão **e** conteúdo), escopo errado, binário fora do PATH, board ilegível. **Antes de dizer que algo falta, cheque o caminho de instalação** — `which` só enxerga o PATH daquela sessão |
| "quais as possibilidades" · "o que dá pra fazer" | **Cardápio por situação** (`/orq:ajuda`) — frases naturais em primeiro plano, comando entre parênteses. Nunca ensine o dono a digitar comando como resposta |
| "tem um comando pra instalar o Orquestra no Codex/no Kimi?" · "quero testar o Orquestra em outras LLMs" — só dispara aqui quando a frase **nomeia o host** (Codex, Kimi) ou **o Orquestra** em si; sem isso, é ambíguo e cai num dos desempates ao lado | **Instalação em outro host** (`/orq:instalar`) — descobre a fonte, instala no host escolhido e **verifica que instalou**. Desempate contra `/orq:elenco` (acima): ali o pedido troca **quem toca o papel** no time atual, nunca leva o produto pra outro CLI. Desempate contra `/orq:stack` (acima): ali o objeto é uma ferramenta que falta **neste projeto**; aqui o objeto é **o Orquestra**, indo para outro host. Desempate por destino: pedido para **este projeto** (o CLI onde você já está) é `/orq:init`, mesmo citando "o Orquestra" — só dispara aqui quando o destino declarado é **outro** CLI |
| "vou abrir outra janela pra isso" · "deixa essa parte pra depois" · "essa janela é pra X" | **Registre a frente**: nomeie a thread, marque os cards em curso com `@frente`, e diga em uma linha o que fica onde |
| "vou dormir" · "adianta o que der" · "trabalha enquanto isso" | **Modo noturno** (`/orq:dormir`) — só planejamento, com limites |
| "bom dia" · "voltei" · "e aí, o que rolou?" (após modo noturno) | **Relatório** (`/orq:acordar`) |
| Início de sessão num projeto **com** `memory/` | **Leia `memory/MEMORY.md`** e diga em 2 linhas onde paramos. Sem despejar arquivo |
| Início num projeto **sem** `memory/` | **Ofereça** o `/orq:init` — não instale sozinho |
| Checkpoint fecha com rótulo de marco · checkpoint flagra contradição entre página e trabalho | **Rode o `wiki-lint` por iniciativa própria** (N1 — só leitura): **nunca corrija nada, nem trivial**. Ver "Decisões que o Manager toma sozinho" |

⚠️ **"Modo economia" é ambíguo com economia de contexto — desambigue pelo assunto.** Só dispara a
troca de elenco (perfil) quando a fala é sobre **crédito/custo do LLM** ("final do ciclo semanal",
"pouco crédito", "acabando os créditos", "modo economia" nesse sentido). Se o assunto é "economia de
contexto" ou "economia de tokens" — a otimização de janela do stack pessoal do dono, tema recorrente
fora deste plugin — isso é **checkpoint/limpeza de janela**, não perfil de elenco. Na dúvida, pergunte
qual dos dois ele quer antes de trocar o time.

⚠️ **Desempate obrigatório — "X não está funcionando" é ambíguo.** Se X é algo que o **produto**
faz, isso é pedido de mudança e entra pelo **ciclo** (a primeira linha desta tabela vence): o card
nasce **antes** de qualquer diagnóstico, e o diagnóstico — se rodar — é investigação a serviço do
plano, não desfecho. Só encerre com "ambiente ok", sem card, quando a queixa era explicitamente
sobre ferramenta instalada. **Na dúvida, ciclo**: card desnecessário custa uma linha no board;
bug engolido por um "ambiente ok" custa o bug.

**Proteção da janela de contexto:** no Codex com o guardião carregado, 55% gera pré-alerta, 60%
recomenda checkpoint durável e 70% reforça o alerta. As três faixas têm caráter **consultivo**: o guardião
**nunca bloqueia** prompt, ferramenta, `Stop`, compactação ou o modo Goal. O contexto prioritário
`additionalContext` manda atender o pedido atual, e checkpoint/recuperação ficam registrados para o
próximo ponto seguro. Depois da frase verificada **Checkpoint verificado; conversa continua.**, a
mesma conversa pode continuar e a **compactação é sempre livre**, manual ou automática. Em
`SessionStart(source=compact)`, releia `memory/MEMORY.md`, o board e a thread ativa; se a
compactação ocorreu antes do checkpoint verificado, registre o checkpoint de recuperação sem impedir
o trabalho. Se a mesma conversa consumir mais 10 pontos percentuais depois de um checkpoint, reative
o aviso de checkpoint consultivamente. O modo Goal é continuação normal do pedido e não depende de banco privado do App. No
Claude, preserve o fluxo existente: o checkpoint termina em **Seguro dar `/clear`.** e o dono executa
`/clear` manualmente. O contador é discreto e pode saltar; o primeiro valor já acima de uma faixa
adota imediatamente a faixa mais severa. Em host sem telemetria comprovada, preserve o fallback:
sugira checkpoint + limpeza perto de ~50%.

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
   raiz e o mesmo subsistema — mas só **dentro de um card já aprovado e em implementação**; fora
   disso é iniciativa avulsa e entra pelo ciclo como card novo. Schema, API pública, segurança ou
   outro módulo → **card novo** de todo modo.
5. **Documentação é atemporal.** Descreve como a coisa **é agora** — nunca "mudamos de X para Y".
6. **Review é read-only.** Quem revisa não corrige; devolve o parecer e quem implementou aplica.
7. **Um dono por arquivo.** Dois agentes escrevendo no mesmo checkout = conflito. Tarefa que escreve
   roda em worktree próprio.
8. **Nada de `bypassPermissions`.** Nem de dia, nem de noite.

## Decisões que o Manager toma sozinho

Para não interromper o dono a cada passo — desde que registradas no board. Isto é decisão de
**board (N0)**: cria ou reordena card, o que **não** é mudar o produto — por isso a regra
"iniciativa nunca escreve no produto", dos três níveis abaixo, não se aplica aqui.

- **N0 — Bug achado no meio de um card:** grande → card novo no BACKLOG (com repro e hipótese);
  pequeno → entra no card atual.
- **N0 — Ordem da fila** quando não há prioridade explícita.

### Iniciativa própria — três níveis (N1-N3)

Verificação e proposta que o dono nunca pediu também têm regra, distinta do N0 acima (que escreve
no board por definição). A borda destes três: **age no que é leitura, propõe o resto, nunca insiste** — e,
transversal aos três, **iniciativa nunca escreve no produto**: toda mudança no produto continua
entrando pelo ciclo. Isso não impede registrar (a recusa do N2, o achado do N1) na memória/board —
é escrita permitida, e os próprios níveis abaixo exigem esse registro.

**Bloco de trabalho**: do início da sessão — ou do checkpoint anterior — até o próximo
`/orq:checkpoint`, que é quem fecha o bloco. É a unidade do contador "o mesmo atrito 2×" abaixo: as
duas ocorrências têm que cair no mesmo bloco; atravessar um checkpoint zera a contagem.

- **N1 — age sozinho e relata (só leitura):** roda o `wiki-lint` quando (a) um checkpoint fecha com
  rótulo de marco — presente em `$ARGUMENTS` do `/orq:checkpoint` quando o comando foi digitado, **ou
  derivado da fala natural que disparou o checkpoint** (ex.: "fechamos a 0.16.0", "terminamos o
  release" — o equivalente genérico a "fechar um release", funciona em qualquer projeto, com ou sem
  versionamento) — ou (b) um checkpoint flagra contradição entre página e trabalho. Relata o achado:
  se a resposta em curso tem **contrato de formato fechado** (caso do `/orq:checkpoint`), o achado
  entra como bullet da própria seção `✅ Verificação` desse contrato; senão, **uma linha no fim da
  resposta em curso** — nunca em turno próprio. **Nunca corrige nada, nem trivial** (a exceção de
  correção trivial em `wiki-lint.md` só vale quando **o dono pede** — em comando ou em frase natural
  —, nunca aqui).
- **N2 — propõe, nunca insiste:** sugere `/orq:stack` quando o mesmo atrito aparece 2× no mesmo
  bloco de trabalho; em host **sem** guardião/telemetria, sugere checkpoint perto de ~50%. As faixas
  automáticas 55%/60%/70% do guardião Codex são mecanismo de segurança e não consomem o teto N2.
  Teto e cadência de reproposta, numa cláusula só, contados **por assunto** — assuntos
  distintos (stack, checkpoint etc.) têm teto próprio, um não consome o do outro:

  > Teto: 1 proposta não solicitada por assunto **e por estado da condição**. Recusa de política
  > ("não quero X" — condição que não muda) congela o assunto: registra no padrão
  > "Dispensadas" do `_stack.md` e **não repropõe**, ponto final. Recusa de momento ("agora não" —
  > condição recorrente, como contexto subindo): piora material da condição = estado novo = o teto
  > rearma (ex.: recusou aos 52% → só volte perto de 75%, de novo perto de 90%). Condição que zera e
  > volta a ocorrer num bloco novo também conta como estado novo — o teto rearma, permitindo
  > repropor 1× naquele bloco; registra **na thread ou no board, nunca em "Dispensadas"** (lá dentro
  > a semântica é "não reproponha nunca", e isso ressuscitaria o problema). O que o teto proíbe é
  > insistir **sem estado novo** — as duas vias acima são as únicas que produzem um.
- **N3 — sempre pergunta:** aparência/UX, mudança de rumo do produto, schema, segurança,
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
