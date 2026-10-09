# Elenco — qual LLM toca cada papel

> **Os comandos leem este arquivo antes de spawnar** e passam o modelo como override.
> O `model:` do arquivo do agente é só o padrão de fábrica. Ajuste papel a papel com
> `/orq:elenco <papel> <modelo>`, ou troque o **time inteiro** com `/orq:elenco perfil <nome>` —
> ou fale naturalmente: *"quero o Fable planejando"*, *"tô com pouco crédito"*, *"modo economia"*.

> **Onde o modelo é resolvido — a única frase normativa:** identifique o host, leia a tabela DELE
> em `## Times por host`, e aplique a célula da `## Matriz de invocação`. **Não existe outra tabela
> ativa.** Vale para ler e para gravar: o `/orq:elenco` escreve na seção do host onde está rodando,
> nunca numa tabela compartilhada — é o que impede uma janela Codex de trocar, em silêncio, o time
> de uma janela Claude aberta no mesmo repositório.
>
> **Presets (`## Perfis`) são por host.** Os desta página valem para o host Claude; o host Codex
> ainda não tem presets — lá o ajuste é papel a papel, e criar um preset é pedido do dono.

## A regra em uma frase (decisão do dono, 2026-09-01)

**Domínio decide quem pensa; host decide quem escreve.** Dois eixos independentes:

- **Trilha** (`interface` | `sistema`) — escolhe o **vendor do planner**. Critério de aceite
  **perceptual** (o dono valida olhando/usando) → Anthropic; critério **comportamental** (valida-se
  verificando) → OpenAI. Card misto ou ambíguo → `sistema`. Não é frontend/backend: um CLI é
  `sistema`, um brand book é `interface`.
- **Faixa** (`pesada` | `normal` | `leve`) — escolhe o **degrau do implementer**, sempre no vendor
  do host. `pesada` = alto risco **ou** desenho ainda por decidir; `leve` = resultado determinado e
  verificação mecânica; senão `normal`. **Card Trivial não tem faixa** (não há implementer: o
  Manager escreve).
  ⛔ **Reavaliada no gate, com piso: card Alto risco continua `pesada` mesmo com o plano fechado.**
  Só rebaixa a `pesada` que veio **exclusivamente** de desenho aberto, e só depois que o plano
  fechou esse desenho — o plano muda a incerteza, não a consequência do erro. Rebaixar um card de
  schema ou segurança mandaria a mudança mais perigosa do board para o modelo mais fraco.

O Manager grava `trilha: … · faixa: …` na nota do card. **Card sem registro → `sistema · normal`.**
A definição canônica das duas réguas mora no produto (`orq/commands/elenco.md`, seção "As duas
réguas") — aqui ela é resumida, não redefinida.

**Quem pode vir de outro vendor:** só **`planner`** (pelo domínio) e **`reviewer`** (pela
independência, e obrigatoriamente do vendor oposto). Aceitam qualquer vendor com célula na
`## Matriz de invocação`, **desde que o mecanismo daquela célula execute aquele modelo** — a
célula Anthropic×Codex é o runner Anthropic parametrizado por `--model <alias-ou-id>`: só entra
valor presente no mapa de prova (`claude-opus-5-5`·`opus`·`fable`·`sonnet`·`haiku`), com identidade
exata para o ID completo ou prefixo do alias comprovado no `modelUsage` antes de virar parecer.
Modelo e effort seguem a linha ativa do papel. **`implementer`, `docs`
e `scout` ficam no vendor do host**: os dois primeiros porque escrevem; o `scout` porque leitura
ampla e barata não compra aptidão de domínio e ainda pagaria transferência para terceiro.
Scout cross-vendor é recusa com motivo. A metade de **escrita** cross-vendor do `T-021` segue fora do
desenho; a metade **read-only** foi decidida aqui.

## Revisores externos

**Não é composição de painel** — o revisor é **um só**, resolvido pela tabela do host. Esta seção é
o **registro de capacidade das vias cross-vendor**: por onde um papel read-only alcança o vendor
oposto, com o que foi comprovado e quando.

Regras, cada uma escrita 1×:

- **Nunca dependa de default de config de terceiro** — declare o modelo aqui, não confie no que o
  binário do vendor assume sozinho. Já custou um parecer rodado no modelo errado em 2026-08-05,
  decidido por omissão pelo `default_model` de um config de terceiro.
- **O vendor do host nunca revisa a si mesmo.** É a razão de existir da via: no host Claude o
  revisor é OpenAI; no host Codex, Anthropic.
- **Toda CLI chamada diretamente exige `< /dev/null`** — sem TTY, ela bloqueia lendo stdin e trava
  até o timeout. O host Claude não chama o binário Codex diretamente: usa o Companion.

| Via | Vendor | Consumida por | Estado | Registro |
|---|---|---|---|---|
| codex | OpenAI | **host Claude**: `planner·sistema` e `reviewer`. No host Codex não é via — é o vendor nativo | **ativo** | subagente `codex:codex-rescue` → `codex-companion.mjs task` · modelo e effort conforme `## Times por host` (hoje `gpt-6.1-sol` @ `xhigh`, desde 2026-10-04) · `jobId` + `threadId` sustentam o reúso exato, aceito só com `threadId` devolvido igual ao solicitado · ver **Matriz de invocação** |
| runner-opus | Anthropic | **host Codex**: `planner·interface` e `reviewer`. No host Claude não é via — é o vendor nativo | **ativo** | `<ORQ_PACKAGE_ROOT-resolvido>/scripts/run-opus-reviewer.py --model claude-opus-5-5 --effort high` · identidade exata no `modelUsage` · 16 KiB/lote por padrão; teto maior exige gate delimitado · timeout 600s · provas e limites em `docs/T-150-adocao-elenco.md`; capacidade CLI não aprova o produto |

A coluna **Consumida por** existe para o efeito de ligar/desligar ser anunciável sem chute: a via
só afeta os papéis listados, nos hosts listados.

**Ativo é política habilitada, não capacidade comprovada.** O Manager confirma binário,
autenticação, modelo e saída em cada parecer. Falha **não autoriza trocar de vendor**: vira
`REVISÃO DEGRADADA`, com a ausência nomeada, e o card não avança sozinho.

**A via nunca recebe dado sensível** (regra em `/orq:revisar`, passo 1b). Diff com dado sensível →
**não há revisor nenhum**: o Manager audita ele mesmo e declara "sem revisão independente por
restrição de dados". **Proibido** spawnar revisor do mesmo vendor do host para tapar o buraco —
decisão do dono em 2026-09-01, contra a recomendação do planner, com o custo lido e aceito.

**Não há linha `claude` nesta tabela — de propósito:** uma via `claude -p` no host Claude produziria
um revisor Anthropic revisando trabalho Anthropic, que é exatamente o que o desenho recusa. O
caminho do `opus` como revisor existe só em host que **não** é Claude: time do host
(`## Times por host`) → papel `reviewer` → célula Anthropic×host da `## Matriz de invocação`.

**O que se perdeu ao virar N=1, dito com todas as letras:** "confirmado por 2+" deixou de existir —
todo achado é solitário **por construção**. Sem interseção, o erro do revisor único não tem
contrapeso: a **auditoria do Manager contra o código** é a única defesa, e "segundo parecer sob
demanda do dono" é válvula, nunca padrão — **e obedece à mesma regra de vendor**: o parecer extra
também vem do vendor oposto ao host, nunca do vendor do host com o rótulo de "avulso".

## Matriz de invocação

**Origem:** a regra que gera esta tabela mora na skill do plugin (`SKILL.md`, parágrafo "Onde houver
equivalente…"). **Aqui moram só os templates** — esta seção não reescreve a regra, materializa-a.

**Ordem das flags — regra por CLI, não generalizável** (a mesma família de erro derrubou a revisão
duas vezes em 2026-08-05, por causas opostas — ver `gotchas.md`):
- **`claude`:** prompt **antes** das flags — a `--tools` é variádica e engole o que vem depois dela.
- **`codex` direto, somente no host Codex:** prompt posicional no fim
  (`codex exec ... "<briefing>"`) — ordem já em uso.

**`< /dev/null` em TODA CLI chamada diretamente** — sem TTY, ela bloqueia lendo stdin e trava até
o timeout. No host Claude, o subagente do Companion encapsula a chamada e não autoriza montar
`codex exec` à mão.

**Briefing:** no host Codex, `codex exec` **lê o repositório sozinho** → isolamento em
worktree/clone descartável (nunca diretório vazio — repo ausente faz o briefing explodir; nunca o
repo vivo — dano sem contenção) + briefing curto + `git add -N .` antes de gerar o patch, para
arquivo novo não sumir do diff. No host Claude, o Companion recebe o mesmo diretório isolado e um
briefing READ-ONLY explícito. `claude -p` invocado de dentro de outro agente **não lê arquivos** →
o briefing carrega o conteúdo **verbatim, numerado por linha**; o parecer é sobre o texto colado, e
quem audita declara essa natureza.

**Saída conferida antes de virar parecer** (tamanho + formato) — 51 bytes não é parecer, é revisor
que não rodou.

**Procedência por célula:** `comprovado` (testado de ponta a ponta) · `observado 1×` (funcionou
uma vez, não repetido) · `não testado`.

| Vendor do modelo | host Claude | host Codex |
|---|---|---|
| **Anthropic** | spawn nativo (Task + `model:`) — comprovado | `printf '%s' "$BRIEFING_SANITIZADO" \| python3 "<ORQ_PACKAGE_ROOT-resolvido>/scripts/run-opus-reviewer.py" --model <alias-ou-id> --effort <effort-resolvido>` — identidade exata para `claude-opus-5-5`, prefixo para aliases legados do mapa. Limite padrão 16 KiB/lote, timeout 600s; `--max-input-bytes` maior só com gate explícito para os bytes reais. Perfis atuais Opus 5.5/high comprovados em 2026-10-07 pela CLI, sem ferramentas/customizações/MCP, cwd vazio e sem retry. Modelo observado no `modelUsage`; effort enviado, não observado no servidor |
| **OpenAI** | **OpenAI × host Claude:** subagente `codex:codex-rescue` → `codex-companion.mjs task --model <modelo> --effort <effort>`; primeira chamada por `card+papel` usa `--fresh --json`, continuação usa `--resume-thread <threadId> --json`; persistir `rawOutput`, `jobId`, `threadId` e `status`; continuação só é aceita com `threadId` devolvido igual ao solicitado. O modelo e o effort foram comprovados como revisor; como planner, o Loop A completo ainda é o teste real. Escrita cross-vendor: fora do desenho | `codex exec` com modelo, effort e sandbox explícitos é obrigatório; primitiva nativa só com override efetivo comprovado e registrado. Os recibos atuais comprovam a CLI, não o Companion ou spawn nativo |

⚠️ **Nunca acrescente `--write`.** O read-only desta chamada vem da ausência dessa flag: com ela, o sandbox do Companion vira `workspace-write` e o papel deixa de ser read-only.

Continuação exige sucesso e `threadId` devolvido igual ao solicitado. Divergência ou recibo
incompleto: registrar degradação, preservar o vínculo anterior e não repetir nem substituir a
thread automaticamente. Aplicar o contrato "Reúso durável do Codex Companion" (skill `orq`).

## Times por host

**Esta é a fonte ativa do elenco** — a única. Cada host resolve o próprio time lendo a seção dele,
e o `/orq:elenco` grava **na seção do host onde está rodando**: uma janela Codex nunca toca na
tabela do Claude, e vice-versa. É assim que as duas convivem no mesmo repositório sem uma pisar no
time da outra.

**Princípios, escritos 1× — valem para os dois times abaixo:**

1. **Domínio decide quem pensa; host decide quem escreve.** O `planner` segue a trilha do card
   (pode cruzar vendor, é read-only); `implementer` e `docs` ficam no vendor do host.
2. **O `reviewer` é único e sempre do vendor oposto ao host** — sem contingência interna, sem
   exceção. Ausência se declara, não se substitui.
3. **A comprovação do alias do runner Anthropic** (que ele resolve para o prefixo esperado — `opus`
   para `claude-opus-5`, `fable` para `claude-fable-5-1`) é obrigatória antes de todo parecer que
   dependa dele; sem comprovação, trate como ausente e não troque de modelo.
4. **Docs e scout seguem o vendor do host**, no degrau barato — leitura/escrita objetiva não se
   paga em domínio.

### Host Claude

| Papel | Modelo | Por quê |
|---|---|---|
| manager | modelo da sessão (`/model`) | sessão principal; **sempre escolha do dono**, em qualquer host |
| planner·interface | `fable` | spawn nativo, read-only — Fable 5.1 (id `claude-fable-5-1`), comprovado |
| planner·sistema | `gpt-6.1-sol@xhigh` | Codex Companion read-only; task fresca por card+papel e retomada pelo `threadId` exato — decisão do dono em 2026-10-04, comprovado no rollout do Companion |
| implementer·pesada | `sonnet` | worktree dedicado, writer único |
| implementer·normal | `sonnet` | worktree dedicado, writer único |
| implementer·leve | `sonnet` | worktree quando houver trabalho paralelo |
| reviewer | `gpt-6.1-sol@xhigh` | vendor oposto ao host; Codex Companion read-only e retomada pelo `threadId` exato — decisão do dono em 2026-10-04, comprovado no rollout do Companion |
| docs | `sonnet` | arquivos de documentação autorizados |
| scout | `sonnet` | read-only |

**Perfil ativo:** `padrao` — desde 2026-09-01 · desvio: planner·sistema→gpt-6.1-sol@xhigh; reviewer→gpt-6.1-sol@xhigh
*(A linha vale por host. Trocar o perfil reescreve a tabela acima e vale a partir do **próximo
spawn, em todas as janelas deste host** — crédito é da conta, não da frente. Agente já em execução
termina no modelo antigo; não se refaz nada. Ajuste papel a papel que diverge do preset ativo —
inclusive com `padrao` ativo — vira `padrao · desvio: papel→modelo` (mais de um desvio, separe por
`;`); devolvido ao preset, remove-se o desvio. Gramática completa (as duas formas, o que o valor
depois de `→` significa) mora em `/orq:elenco`, não aqui — ver passo 3 de "Com argumento —
ajustar".)*
**Procedência dos valores:** revisão completa do dono em **2026-09-03** — as três faixas de
`implementer` unificadas em `sonnet`, `planner·sistema` e `reviewer` promovidos a `@max`. Em
**2026-09-05** (`T-079`), `planner·sistema` e `reviewer` migraram de `gpt-5.6-sol@max` para
`gpt-6-astra@max`; o efeito de faixa/cerimônia descrito abaixo continua valendo. Em
**2026-09-07** (`T-083`), os dois caíram para `@xhigh`: a CLI do Companion recusa `max`
(`Unsupported reasoning effort "max". Use one of: none, minimal, low, medium, high, xhigh`), então
`@max` era intenção declarada e nunca effort exercitado. **A tabela do host Codex não foi tocada** —
lá a via é `codex exec`, onde essa recusa não foi comprovada, e cada host só edita a própria seção.
Em **2026-10-04**, o dono trocou `planner·sistema` e `reviewer` deste host de `gpt-6-astra@xhigh`
para `gpt-6.1-sol@xhigh`, no dia do lançamento do Sol 6.1: *"prefiro que seja usado o GPT 6.1 Sol
no Xhigh do que usar o GPT 6 Astra no momento"*. A troca está registrada como **desvio** do
`padrao`, que segue com Astra. **Prova:** sonda única pelo Companion
(`task --fresh --json --model gpt-6.1-sol --effort xhigh`), com resposta literal `SOL61_OK`, exit 0
e thread `01a10816-9f6a-7ff0-a425-124db286f606`; o rollout dessa thread em `~/.codex/sessions/`
registra `"model":"gpt-6.1-sol"` e `"effort":"xhigh"`. A saída JSON do Companion não expõe o modelo;
a prova vem do rollout. Tasks já abertas com Astra (T-144 planner/reviewer) terminam nele. A tabela
do host Codex segue com `gpt-6-astra@max`.
⚠️ **Com as três faixas no mesmo modelo, a faixa deixa de escolher executor neste host** e passa a
medir só cerimônia. A régua continua válida (ela também governa o gate e o piso de Alto risco), mas
não espere que `pesada` traga um modelo mais forte aqui — não traz mais.

### Host Codex

Motor: a sessão Codex. A linha `manager` é expectativa verificável, não comando de troca da sessão.

| Papel | Modelo | Por quê |
|---|---|---|
| manager | modelo da sessão (`/model`) | sessão principal; **sempre escolha do dono** — verificar o modelo real antes de anunciar |
| planner·interface | `claude-opus-5-5@high` | read-only via Claude CLI; domínio perceptual, pacote autocontido e plano persistido pelo Manager |
| planner·sistema | `gpt-6.1-sol@xhigh` | read-only via Codex CLI; domínio comportamental, perfil condicionado à prova contextual |
| implementer·pesada | `gpt-6.1-sol@xhigh` | alto risco/desenho aberto; writer único em worktree, escrita sintética comprovada |
| implementer·normal | `gpt-6.1-sol@high` | implementação e testes usuais; writer único em worktree, escrita sintética comprovada |
| implementer·leve | `gpt-6-luna@medium` | resultado determinado/verificação mecânica; escrita sintética comprovada |
| reviewer | `claude-opus-5-5@high` | vendor oposto; Claude CLI sem ferramentas, identidade exata exigida antes de aceitar o parecer |
| docs | `gpt-6-luna@low` | escrita objetiva no vendor do host; escrita sintética comprovada |
| scout | `gpt-6-luna@medium` | investigação delimitada, read-only no vendor do host |

**Origem:** `orquestra-version` · versão `0.31.0` · adoção local candidata em
no candidato T-150 · `catalog_sha256`:
`5996dab63533113049c15ee6778110b4b99a9248ed3b6f3beebc1b0221d70bd3`.
As oito linhas são uma **substituição candidata** do perfil Codex anterior,
autorizada localmente no T-150; integrar/adotar na raiz principal ainda depende
da validação/gate do dono. Não declarar que faltavam decisões humanas: Astra
dos planners (T-079/T-083), Terra dos implementers (`2026-08-09`/`2026-09-03`)
e docs/scout (`2026-09-03`), além do reviewer Opus legado (`2026-08-09`), permanecem documentados na
origem e no rollback. Detalhes e fonte humana: `docs/T-150-adocao-elenco.md`.
Nenhum override fora dessas oito linhas, via desligada, Manager, Host Claude
ou preset foi alterado. Relatos históricos da seção Claude sobre o Codex
não substituem a tabela candidata deste host. Recibos e rollback usam o
caminho durável `docs/T-150-adocao-elenco.md`, relativo à raiz do projeto.

**Capacidade contextual:** seis provas Codex CLI 0.160.1, uma sonda planner interface
e uma R1 reviewer Claude CLI 2.1.290; ambas Anthropic em Opus 5.5/high. No Codex,
modelo/effort/sandbox foram observados no cliente; no Anthropic, modelo em
`modelUsage` e effort enviado, não observado no servidor. Não é prova de qualidade,
economia, spawn nativo ou ativação de outros chats. Workers já vivos mantêm o
perfil anterior. A raiz principal não foi migrada nesta adoção local candidata.

**Perfil ativo:** — este host não tem presets; o ajuste aqui é papel a papel, e criar um `## Perfis`
para ele é pedido do dono, não iniciativa. Os presets de `## Perfis` são do host Claude e **não** se
aplicam aqui: trariam modelos Anthropic para `implementer`/`docs`, que só aceitam o vendor do host.

### Pendências comprováveis (não prometer antes de rodar)

- **Astra (`gpt-6-astra`) como planner e reviewer** — o modelo e os efforts `low|medium|high|xhigh|
  max` estão comprovados via CLI Codex. Em 2026-09-07 (`T-083`), a sonda real
  `codex exec -c 'model_reasoning_effort="max"' --model gpt-6-astra --sandbox read-only` anunciou
  `reasoning effort: max`, respondeu corretamente e saiu `0`. A flag literal `--effort` não existe
  na CLI 0.153.4; isso é sintaxe diferente da via Companion, não recusa de `max`. A rejeição de
  `none` também foi comprovada no `T-079`.
  `ultra` está disponível no catálogo do host mas não foi adotado — escolha do dono, não limitação.
  O que falta é o **comportamento num Loop A completo** (plano de ponta a ponta, revisão de um diff
  real): a sonda comprovou que o modelo responde, não que o ciclo inteiro funciona.
- **`gpt-5.6-luna` em `workspace-write`, e o effort suportado, seguem sem medição.** O smoke de
  2026-09-01 destravou o degrau e provou **só** o que segue: o modelo existe no catálogo, está
  autenticado nesta máquina e responde quando endereçado por `--model gpt-5.6-luna` — chamada
  trivial pelo runtime do Codex (`codex-companion.mjs task --model gpt-5.6-luna`, prompt *"responda
  somente LUNA_OK"*), devolvendo `LUNA_OK`, thread `01a05e0d-309c-7a92-839c-09f6c418a974`, **sem
  leitura de arquivo e sem execução de comando**. Continua **não medido**: (a) quais reasoning
  efforts ele aceita — o catálogo não expõe e o smoke não testou, por isso o degrau vai **sem
  effort declarado**; (b) o comportamento em `-s workspace-write`, que é o modo real do
  implementer — o smoke foi read-only. *Responder a uma chamada trivial* não é *escrever código
  confiável em worktree*: o primeiro card `leve` real no Codex é que diz.
- **Codex Companion produzindo plano read-only** — modelo e runtime estão comprovados como
  revisor; o Loop A completo como planner ainda não foi exercitado.
- **`haiku` na faixa leve** — precedente indireto (docs/scout no `economia`), sem medição.

## Custo

Cada papel cobra a conta do vendor do SEU modelo. Na prática: implementer, docs, scout e manager
cobram a conta do host; o `planner` da trilha cruzada e o `reviewer` cobram a do outro vendor —
gasto deliberado, é o que compra o plano de domínio e a revisão independente. Trocar de host move o
bloco de escrita inteiro para a outra assinatura.

O preset `economia`, na seção `## Perfis` abaixo, é a variante de crédito curto **do host Claude**.
Equivalente no Codex nasce sob demanda, quando o dono pedir.

**Preços comprovados (tabela do vendor, não custo total do card):** GPT-6 Astra cobra US$ 10/MTok
de entrada e US$ 50/MTok de saída — mesma tabela do Fable 5. Claude Fable 5.1 fica cerca de 25%
abaixo do Fable 5 em workloads típicos; não há fonte verificada para um preço absoluto do 5.1, e
nenhum arquivo deste projeto deriva um.

`economia` é perfil de **crédito e esforço**, não garantia de menor custo total: o Astra cai de
`@max` para `@high` (mesmo modelo, effort menor), `implementer·leve`, `docs` e `scout` usam degraus
mais baratos, e `planner·interface` continua trocando de Fable 5.1 para Opus — decisão anterior do
dono, preservada aqui.

## Perfis — times nomeados por contexto de crédito (host Claude)

Perfil é um preset do time inteiro **de um host**. Ativar = reescrever a tabela do host resolvido em
`## Times por host` a partir do preset e atualizar a linha **Perfil ativo** daquela seção. Os
consumidores (`plan-next`, `implement-next`, `revisar`, `stack`) não mudam: continuam lendo a tabela
do host. Os presets abaixo são do **host Claude** — aplicá-los rodando no Codex traria modelos do
vendor errado para os papéis de escrita, e por isso o comando recusa.

**Frases de gatilho — atestadas vs. paráfrase** (medido no transcript de 2026-07-29, não
imaginado): *"final do ciclo semanal"*, *"pouco crédito"* e *"acabando os créditos"* são falas
verbatim do dono. *"Modo economia"* é **paráfrase** — nasceu do card, não da fala dele — mas vira o
nome de apelo do perfil porque ele reconhece e usa a frase depois de lida. Não existe frase
atestada para "voltar": a reversão não é um gatilho fixo à espera de adivinhação — o Manager diz,
no próprio anúncio da troca, como reverter (ex.: "quando o crédito voltar, é só pedir"), e o pedido
de volta é reconhecido como o pedido de mudança que é, na hora em que ele vier.

**O `manager` não entra em perfil nenhum** — é a sessão principal, definida pelo `/model` do dono.
Ao ativar `economia`, sugerir em uma linha que ele avalie trocar o `/model` também: é onde mora o
maior consumo, e só ele troca.

**Perfil nunca troca o vendor do `reviewer`** — só o effort, dentro do mesmo vendor. Rebaixá-lo para
o vendor do host acabaria com a única coisa que ele entrega.

### `padrao` — o time titular (vale por default)

| Papel | Modelo | Por quê |
|---|---|---|
| planner·interface | fable | trilha perceptual pensa com Anthropic — Fable 5.1 |
| planner·sistema | gpt-6-astra@xhigh | trilha comportamental pensa com OpenAI |
| implementer·pesada | sonnet | executar plano já aprovado é trabalho dirigido — reconciliado com a tabela ativa |
| implementer·normal | sonnet | executar plano já aprovado é trabalho dirigido |
| implementer·leve | sonnet | executar plano já aprovado é trabalho dirigido — reconciliado com a tabela ativa |
| reviewer | gpt-6-astra@xhigh | vendor oposto ao host — a independência não se rebaixa |
| docs | sonnet | escrita objetiva sobre código já pronto |
| scout | sonnet | leitura ampla e barata |

Vias cross-vendor: `codex` **ativa** · `runner-opus` **ativa** — estado informativo, o perfil não
aplica isto (ver passo 2 de "Com argumento `perfil <nome>`" em `/orq:elenco`); vale o que está de
fato registrado acima.

### `economia` — fim do ciclo semanal, crédito Claude curto

Composição derivada da palavra do dono (2026-07-29): *"diminuo o planejamento com o Fable e faço só
com o Opus"* — relida para os dois eixos.

| Papel | Modelo | Por quê |
|---|---|---|
| planner·interface | opus | escolha verbatim do dono para este contexto |
| planner·sistema | gpt-6-astra@high | effort rebaixado dentro do mesmo vendor |
| implementer·pesada | sonnet | rebaixado um degrau — evita herdar Opus no perfil de economia |
| implementer·normal | sonnet | já era o econômico |
| implementer·leve | haiku | já era o mais barato |
| reviewer | gpt-6-astra@high | effort rebaixado; **vendor não muda** |
| docs | haiku | escrita objetiva; rebaixar aqui custa pouco |
| scout | haiku | leitura ampla e barata |

Vias cross-vendor: `codex` **ativa** · `runner-opus` **ativa** — mesmo estado informativo do preset
`padrao`, não aplicado pelo perfil. Quem decide o briefing enxuto do `--rapido` é o `/orq:revisar` —
regra lá.

**O que se perde neste perfil — dito com todas as letras:**
- o **único** parecer independente vem com menos effort, e não há segundo revisor para compensar: a
  auditoria do Manager contra o código carrega mais peso;
- a escrita rebaixada erra mais justamente na faixa `pesada`, que é onde ou o desenho ainda está
  aberto ou a consequência do erro é a maior do board (Alto risco, que **não** rebaixa nunca) — se
  o card for pesado de verdade, prefira adiar a economia;
- Codex read-only: a implementação continua queimando crédito Claude — o perfil **reduz, não zera**;
- o Manager não muda: o maior consumo é a sessão principal, e só o `/model` do dono a troca.

## Por que a revisão independente importa neste projeto

O produto aqui são **instruções**, não código. O modo de falha nº 1 é **contradição entre arquivos**
e **referência a algo que não existe** — defeitos que quem escreveu o texto tem a maior dificuldade
de ver, porque leu com a intenção na cabeça. Um leitor de **outro fornecedor** chega sem essa
intenção: é essa a assimetria que o parecer compra, não a força do modelo.

Com N=1 a reconciliação virou **auditoria**: o Manager verifica cada achado no código, descarta o
que não tem cenário de falha concreto, e diz onde discordou. É o passo que substitui a interseção
que existia com dois pareceres — e, como não há contrapeso, ele não é opcional.

Em card pequeno e de baixo risco, `--rapido` encolhe o **briefing** — nunca troca o revisor nem
dispensa a revisão. Regra no `/orq:revisar`.
