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
célula Anthropic×Codex é o runner de Opus fixo, então lá só entra `opus`. **`implementer`, `docs`
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
- **Toda invocação por CLI exige `< /dev/null`** — sem TTY, os CLIs bloqueiam lendo stdin e travam
  até o timeout.

| Via | Vendor | Consumida por | Estado | Registro |
|---|---|---|---|---|
| codex | OpenAI | **host Claude**: `planner·sistema` e `reviewer`. No host Codex não é via — é o vendor nativo | **ativo** | binário `/usr/local/bin/codex` (`codex` no PATH) · modelo `gpt-5.6-sol` @ `xhigh` · comando completo: ver **Matriz de invocação** |
| runner-opus | Anthropic | **host Codex**: `planner·interface` e `reviewer`. No host Claude não é via — é o vendor nativo | **ativo** | `orq/scripts/run-opus-reviewer.py` · comprova `claude-opus-5` · 16 KiB por lote · timeout 600s · sonda real em repo + diretório externo passou em 2026-08-09 |

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
- **`codex`:** prompt posicional no fim (`codex exec ... "<briefing>"`) — ordem já em uso.

**`< /dev/null` em TODA invocação por CLI** — sem TTY, os dois bloqueiam lendo stdin e travam até
o timeout.

**Briefing:** `codex exec` **lê o repositório sozinho** → isolamento em worktree/clone descartável
(nunca diretório vazio — repo ausente faz o briefing explodir; nunca o repo vivo — dano sem
contenção) + briefing curto + `git add -N .` antes de gerar o patch, para arquivo novo não sumir do
diff. `claude -p` invocado de dentro de outro agente **não lê arquivos** → o briefing carrega o
conteúdo **verbatim, numerado por linha**; o parecer é sobre o texto colado, e quem audita declara
essa natureza.

**Saída conferida antes de virar parecer** (tamanho + formato) — 51 bytes não é parecer, é revisor
que não rodou.

**Procedência por célula:** `comprovado` (testado de ponta a ponta) · `observado 1×` (funcionou
uma vez, não repetido) · `não testado`.

| Vendor do modelo | host Claude | host Codex |
|---|---|---|
| **Anthropic** | spawn nativo (Task + `model:`) — comprovado | `printf '%s' "$BRIEFING_SANITIZADO" \| python3 "<ORQ_PACKAGE_ROOT-resolvido>/scripts/run-opus-reviewer.py" --model <alias>` — aliases `opus`·`fable`·`sonnet`·`haiku`, **prova o prefixo do alias pedido** (pedir `fable` e receber Opus reprova com exit 7), limita 16 KiB/lote e aplica timeout. `opus` comprovado em 2026-08-09; **`fable` habilitado no `T-077` (2026-09-04) e ainda sem chamada real — comprovar no primeiro uso** |
| **OpenAI** | `codex exec -m gpt-5.6-sol -c model_reasoning_effort=<e> -s read-only "<briefing>" < /dev/null` — **comprovado como revisor**; **como planner, não exercitado** (o primeiro Loop A de trilha `sistema` no host Claude é o teste real). Escrita cross-vendor: fora do desenho | a primitiva exposta na sessão não aceita override de modelo/effort; use `codex exec` com modelo, effort e sandbox explícitos |

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
3. **A comprovação do alias `opus`** (que ele resolve para Opus 5) é obrigatória antes de todo
   parecer que dependa dele; sem comprovação, trate como ausente e não troque de modelo.
4. **Docs e scout seguem o vendor do host**, no degrau barato — leitura/escrita objetiva não se
   paga em domínio.

### Host Claude

| Papel | Modelo | Por quê |
|---|---|---|
| manager | modelo da sessão (`/model`) | sessão principal; **sempre escolha do dono**, em qualquer host |
| planner·interface | `fable` | spawn nativo, read-only |
| planner·sistema | `gpt-5.6-sol@max` | `codex exec … -s read-only`; mecanismo comprovado como revisor, não como planner |
| implementer·pesada | `sonnet` | worktree dedicado, writer único |
| implementer·normal | `sonnet` | worktree dedicado, writer único |
| implementer·leve | `sonnet` | worktree quando houver trabalho paralelo |
| reviewer | `gpt-5.6-sol@max` | vendor oposto ao host; `codex exec … -s read-only` |
| docs | `sonnet` | arquivos de documentação autorizados |
| scout | `sonnet` | read-only |

**Perfil ativo:** `padrao` — desde 2026-09-01, sem desvio.
*(A linha vale por host. Trocar o perfil reescreve a tabela acima e vale a partir do **próximo
spawn, em todas as janelas deste host** — crédito é da conta, não da frente. Agente já em execução
termina no modelo antigo; não se refaz nada. Ajuste papel a papel que diverge do preset ativo —
inclusive com `padrao` ativo — vira `padrao · desvio: papel→modelo`; devolvido ao preset, remove-se
o desvio. Ver passo 3 de "Com argumento — ajustar" em `/orq:elenco`.)*
**Procedência dos valores:** revisão completa do dono em **2026-09-03** — as três faixas de
`implementer` unificadas em `sonnet`, `planner·sistema` e `reviewer` promovidos a `@max`.
⚠️ **Com as três faixas no mesmo modelo, a faixa deixa de escolher executor neste host** e passa a
medir só cerimônia. A régua continua válida (ela também governa o gate e o piso de Alto risco), mas
não espere que `pesada` traga um modelo mais forte aqui — não traz mais.

### Host Codex

Motor: a sessão Codex. A linha `manager` é expectativa verificável, não comando de troca da sessão.

| Papel | Modelo | Por quê |
|---|---|---|
| manager | modelo da sessão (`/model`) | sessão principal; **sempre escolha do dono** — verificar o modelo real antes de anunciar |
| planner·interface | `fable` | decisão do dono em 2026-09-03, **destravada pelo `T-077`**: o runner passou a aceitar `--model` e a provar o prefixo do alias pedido. Invocar com `--model fable`; a prova exige `claude-fable-5` no `modelUsage` |
| planner·sistema | `gpt-5.6-sol@max` | decisão do dono em 2026-09-03; read-only |
| implementer·pesada | `gpt-5.6-terra@xhigh` | `workspace-write`, writer único em worktree |
| implementer·normal | `gpt-5.6-terra@xhigh` | decisão do dono em 2026-08-09; writer único em worktree |
| implementer·leve | `gpt-5.6-terra@xhigh` | decisão do dono em 2026-09-03: as três faixas no mesmo modelo. O smoke do `gpt-5.6-luna` fica no histórico, mas o degrau não o usa mais |
| reviewer | `fable` | vendor oposto ao host; runner Anthropic, read-only, sem ferramentas. Invocar com `--model fable` |
| docs | `gpt-5.6-terra@xhigh` | decisão do dono em 2026-09-03 |
| scout | `gpt-5.6-terra@xhigh` | decisão do dono em 2026-09-03 |

**Perfil ativo:** — este host não tem presets; o ajuste aqui é papel a papel, e criar um `## Perfis`
para ele é pedido do dono, não iniciativa. Os presets de `## Perfis` são do host Claude e **não** se
aplicam aqui: trariam modelos Anthropic para `implementer`/`docs`, que só aceitam o vendor do host.

### Pendências comprováveis (não prometer antes de rodar)

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
- **`codex exec -s read-only` produzindo plano** — comprovado como revisor, não como planner.
- **`haiku` na faixa leve** — precedente indireto (docs/scout no `economia`), sem medição.

## Custo

Cada papel cobra a conta do vendor do SEU modelo. Na prática: implementer, docs, scout e manager
cobram a conta do host; o `planner` da trilha cruzada e o `reviewer` cobram a do outro vendor —
gasto deliberado, é o que compra o plano de domínio e a revisão independente. Trocar de host move o
bloco de escrita inteiro para a outra assinatura.

O preset `economia`, na seção `## Perfis` abaixo, é a variante de crédito curto **do host Claude**.
Equivalente no Codex nasce sob demanda, quando o dono pedir.

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
| planner·interface | fable | trilha perceptual pensa com Anthropic |
| planner·sistema | gpt-5.6-sol@ultra | trilha comportamental pensa com OpenAI |
| implementer·pesada | opus | alto risco ou desenho ainda aberto |
| implementer·normal | sonnet | executar plano já aprovado é trabalho dirigido |
| implementer·leve | haiku | resultado determinado, verificação mecânica |
| reviewer | gpt-5.6-sol@xhigh | vendor oposto ao host — a independência não se rebaixa |
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
| planner·sistema | gpt-5.6-sol@high | effort rebaixado dentro do mesmo vendor |
| implementer·pesada | sonnet | rebaixado um degrau — evita herdar Opus no perfil de economia |
| implementer·normal | sonnet | já era o econômico |
| implementer·leve | haiku | já era o mais barato |
| reviewer | gpt-5.6-sol@high | effort rebaixado; **vendor não muda** |
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
