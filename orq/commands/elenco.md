---
description: Mostra e ajusta o elenco — qual LLM toca cada papel (planner por trilha, implementer por faixa, reviewer, docs, scout) no host em que você está, quais vias cross-vendor estão habilitadas, e perfis nomeados para trocar o time inteiro
argument-hint: "[papel modelo | perfil nome — ex: 'planner interface <modelo>' | 'implementer leve <modelo>' | 'codex off' | 'perfil economia']"
---

O **elenco** define qual modelo interpreta cada papel **neste projeto**. Fica em
`memory/wiki/_elenco.md` e vale como override no momento do spawn — o `model:` do arquivo do agente
é só o padrão de fábrica.

**A regra que organiza tudo:** *domínio decide quem pensa; host decide quem escreve.* Dois eixos
independentes, definidos canonicamente aqui e apenas referenciados nos outros comandos.

## ⚠️ Onde o modelo é resolvido — a única frase normativa

**Identifique o host, leia a tabela DELE em `## Times por host`, e aplique a célula da
`## Matriz de invocação`. Não existe outra tabela ativa.**

Isto vale para ler e para escrever: `/orq:elenco` (ajuste papel a papel e `perfil <nome>`) grava na
tabela do **host resolvido**, nunca numa tabela compartilhada. É o que impede uma janela Codex de
trocar, em silêncio, o time de uma janela Claude aberta no mesmo repositório — cada host mexe só na
sua seção.

> **Arquivo com um heading `## Papéis`** (formato anterior à 0.24.0) — aquela tabela era, na
> prática, o time do host Claude, mas nada dizia isso, e consumidor nenhum a lê mais. Trate-a como
> **legada: não leia, não grave**. Proponha a migração (regra em "Migração de arquivo legado"), com
> gate. Enquanto a migração não acontecer, o time vem de `## Times por host`.

## As duas réguas (definição canônica — os outros comandos apontam para cá)

### Trilha (`interface` | `sistema`) — escolhe o **vendor de quem pensa**

Aplicável por um modelo lendo o card, sem o dono no meio:

| Trilha | Critério | Vendor do `planner` |
|---|---|---|
| `interface` | o critério de aceite é **perceptual**: o dono valida olhando/usando — aparência, texto voltado a humano, fluxo de interação, experiência, marca | **Anthropic** |
| `sistema` | o critério de aceite é **comportamental**: valida-se verificando — lógica, dados, contrato, infra, CLI, build, desempenho | **OpenAI** |

**Desempate:** card misto ou ambíguo → `sistema`. `interface` exige critério de aceite perceptual
explícito. Não é frontend/backend: um CLI é `sistema`, um brand book é `interface`, uma migração de
banco é `sistema`. Projeto sem UI simplesmente não usa a linha de interface.

### Faixa (`pesada` | `normal` | `leve`) — escolhe o **degrau de quem escreve**

**Pré-condição, antes da pergunta 1:** o card é **Trivial** na escala de roteamento da skill `orq`
(typo, renomear variável local, ajuste de texto sem efeito)? → **não há faixa.** Em Trivial não há
implementer spawnado — o Manager escreve na sessão —, e faixa é o degrau de **quem foi spawnado**.
Encerre a classificação aqui e não anuncie faixa nenhuma. A faixa só existe de **Pequeno** para
cima.

Havendo implementer, três perguntas, nesta ordem:

1. O card é **Alto risco** na escala de roteamento, **ou** resta decisão de desenho por tomar (mais
   de uma solução defensável)? → `pesada`
2. Senão: o resultado está **completamente determinado** e a verificação é mecânica (rename
   mecânico, aplicar diff já aprovado, doc sobre código pronto, ajuste de texto **já classificado
   Pequeno** — 1 arquivo, sem decisão de desenho)? → `leve`
3. Senão → `normal`

Na dúvida, sobe uma faixa (mesma regra da escala).

**Reavaliação no gate do Loop A — com piso.** A faixa é default inicial, não veredito, e muda nos
dois sentidos quando o plano é aprovado:

- ⛔ **Piso: card Alto risco continua `pesada`, sempre.** Schema, segurança, dependência nova,
  dado de terceiro, irreversível: **plano fechado não rebaixa.** O que torna esse card caro é a
  **consequência do erro**, e o plano muda a incerteza, não a consequência. Rebaixar aqui mandaria
  a mudança mais perigosa do board para o modelo mais fraco.
- **Rebaixa** só quando a `pesada` veio **exclusivamente** da segunda metade da pergunta 1
  (desenho aberto) e o plano aprovado fechou esse desenho.
- **Sobe** quando o desenho continua aberto depois do plano.

### Registro no card

O Manager grava `trilha: … · faixa: …` na nota do card, na criação e revalidado no gate. **Card sem
registro → `sistema · normal`** — o default seguro. Card Trivial: `trilha: … · faixa: —`.

## Quem pode vir de outro vendor

**Só dois papéis cruzam vendor, e cada um por uma razão própria** — não é "read-only pode":

- **`planner`** cruza pelo **domínio**: a trilha do card escolhe quem pensa melhor naquele tipo de
  problema. Aceita modelo de qualquer vendor com célula na `## Matriz de invocação`, **desde que o
  mecanismo daquela célula execute aquele modelo** (a célula Anthropic×Codex é o runner de Opus
  fixo: lá só entra `opus`).
- **`reviewer`** cruza pela **independência**, e é obrigado a cruzar: sempre o vendor **oposto** ao
  do host, com a mesma checagem de mecanismo.
- **`implementer`, `docs` e `scout` ficam no vendor do host.** Nos dois primeiros porque **escrevem**
  — escrita cross-vendor está fora do desenho. No `scout` porque **domínio não se paga em leitura
  ampla e barata**: ele varre território e relata, não decide nem julga. Cruzar vendor ali compra
  zero aptidão e cobra caro — transferência de dados para terceiro, uma via a mais para verificar
  antes de cada spawn, e um papel que some da coluna `Consumida por` das vias, ficando fora do
  cálculo de impacto quando o dono desliga uma via. `scout` cross-vendor é **recusa com motivo**.
- **No `reviewer`, a independência ganha do domínio, sempre.** Ele é **um só e sempre do vendor
  oposto ao host**, inclusive em card de `interface` no host Claude. A razão de existir do revisor é
  ser independente de quem escreveu, não ser apto no domínio; a trilha modula o *planner* (e, quando
  útil, a ênfase do briefing), **nunca o vendor do revisor**. Regra completa em `/orq:revisar`.

## Sem argumento — mostrar

Identifique o host, leia `memory/wiki/_elenco.md` e apresente **a tabela daquele host** (papel ·
modelo · por quê), mais as vias cross-vendor habilitadas e o `Perfil ativo` daquela seção. Diga qual
host você resolveu — sem isso o dono não sabe qual das tabelas está vendo. Se o arquivo não existir,
mostre os **padrões de fábrica** e ofereça criá-lo.

Feche sugerindo, em uma linha, o que costuma valer a pena ajustar (ex.: *"plano difícil rende mais
com um modelo mais forte no planner da trilha que você mais usa"*).

## Com argumento — ajustar

`$ARGUMENTS` no formato `<papel> <valor>`. Exemplos (**do host Claude** — no Codex os modelos são
outros, e a trilha `interface` só aceita `opus`): `planner interface fable` ·
`implementer leve haiku` · `implementer normal gpt-5.6-terra@xhigh` · `codex off` ·
`runner-opus on`. O effort **não** se ajusta por aqui: ele mora no modelo do papel
(`reviewer gpt-5.6-sol@xhigh`), não na via.

**`$ARGUMENTS` começando com `perfil ` (ex.: `perfil economia`) não é papel** — vá direto para a
seção "Com argumento `perfil <nome>` — trocar o time inteiro" abaixo, em vez desta.

0. **Resolva o host primeiro.** Todo o resto deste passo a passo depende dele: quais modelos são
   aceitos, quais vias existem e **em qual tabela você vai gravar**. Host não identificado → pare e
   diga; não escolha uma tabela por presunção.
1. **É via ou é papel?** Compare o primeiro token com a coluna **Via** da seção
   `## Revisores externos` **deste** `_elenco.md` (de fábrica: `codex` e `runner-opus`), lida na
   hora, nunca uma lista decorada.

   **É via → este é o ramo, e ele termina aqui; não caia na validação de modelo do passo 2.**
   - O único valor aceito é `on` ou `off`. Qualquer outro (um effort, um modelo) → **recuse
     dizendo o que a via aceita**, e diga onde se muda o que ele provavelmente queria: o modelo e o
     effort ficam na linha do **papel**, na tabela do host.
   - Grave o valor na coluna **Estado** daquela linha (`ativo` / `inativo`) — é a coluna que
     existe para isso; sem essa escrita, o "desliguei" seria só uma frase.
   - **Antes de gravar, leia a coluna `Consumida por` daquela via e derive o efeito real dali** —
     não presuma que a via mexida é a do seu host. Confirme **o efeito, não o ato**, nomeando
     **quais hosts e quais papéis** mudam:
     - **A via é cross-vendor para o SEU host** (ela aparece com o seu host em `Consumida por`) →
       desligar deixa este projeto **sem revisor independente neste host**: toda revisão passa a ser
       degradada e o Manager audita o diff ele mesmo. Se ela também alimenta um `planner`, diga que
       aquela trilha perde o planner do outro vendor.
     - **A via é do vendor do SEU host, ou só serve a outro host** → diga isso **explicitamente**:
       *"isto não muda nada nesta sessão; afeta o host X, nos papéis Y"*. Continue aceitando o
       comando — o dono pode estar numa janela e querer desligar a via da outra —, mas **nunca
       anuncie uma consequência que não vai acontecer aqui**. Foi esse o defeito: `codex off` rodado
       no host Codex anunciava "ficamos sem revisor", enquanto o revisor daquele host é o
       `runner-opus`, intacto.
   - Via desligada **não** muda a tabela do host: a linha do `reviewer` continua registrada. O que
     muda é que ela não pode ser executada — quem resolve isso é o consumidor, na hora do spawn.

   **É papel** → siga para o passo 2. Válidos: `manager` · `planner` · `implementer` · `reviewer` ·
   `docs` · `scout`. **Papéis com sufixo** aceitam as duas grafias, ponto-médio ou espaço:
   `planner·interface` = `planner interface`; `implementer·leve` = `implementer leve`.
   - **`planner` sem sufixo** → aplique **às duas trilhas** e **avise em uma linha** que o fez
     (colapsar as trilhas apaga o eixo de domínio; ele precisa saber que foi isso que pediu).
   - **`implementer` sem sufixo** → ajuste **só a faixa `normal`** e **avise em uma linha** que
     `pesada` e `leve` ficaram como estavam.
2. Valide o modelo **contra o vendor do host resolvido no passo 0** — não contra uma lista fixa:
   - **`implementer`, `docs` e `scout`: só modelos do vendor do host.** No host Claude, `opus` ·
     `sonnet` · `haiku` · `fable` · `inherit` ou um id (`claude-opus-5`); no host Codex, um modelo
     OpenAI com effort opcional (`gpt-5.6-sol@xhigh`, `gpt-5.6-terra@xhigh`). Modelo de outro vendor
     aqui é **recusa com motivo**, não pergunta: nos dois primeiros porque escrita cross-vendor está
     fora do desenho; no `scout` porque leitura ampla e barata não se paga em domínio — diga isso ao
     recusar, e ofereça o modelo barato do host no lugar.
   - **`planner`**: qualquer vendor **com célula na `## Matriz de invocação`** para este host.
   - **`reviewer`**: idem, com o vendor obrigatoriamente **oposto ao do host** — pedido de revisor do
     vendor do host é recusa com motivo (a independência é a única coisa que ele entrega).
   - ⛔ **Vendor certo não basta: o MECANISMO daquela célula tem que conseguir executar o modelo.**
     Leia a célula antes de aceitar, e recuse o que ela não roda:
     - **Anthropic × host Codex** — a célula é o `run-opus-reviewer.py`, que invoca o modelo
       **`opus` fixo** e só imprime parecer se o JSON comprovar `claude-opus-5`. Logo, no host Codex
       o único modelo Anthropic aceito é **`opus`** (ou um id comprovadamente equivalente).
       `fable`, `sonnet`, `haiku` → **recuse citando a limitação**: *"o runner só executa Opus 5;
       registrar outro modelo aqui gravaria um elenco que a execução não honra"*. Parametrizar o
       runner é **card novo**, não improviso deste comando.
     - **OpenAI × qualquer host** — a célula é `codex exec -m <modelo>`, que aceita o modelo como
       argumento: qualquer modelo OpenAI do catálogo serve, com effort opcional.
     **Por que isto é regra e não zelo:** sem ela o arquivo registra Fable e a execução entrega
     Opus, calada. Elenco que mente sobre quem trabalhou é pior que elenco ausente — some a
     procedência, que é justamente o que este arquivo existe para guardar.
   - Valor que não se encaixa em nenhuma dessas → **pergunte** em vez de gravar errado.
3. Grave **na tabela do host resolvido**, dentro de `## Times por host` (crie o arquivo a partir do
   modelo abaixo se não existir). **Host sem seção `## Perfis` própria** (é o caso de fábrica fora do
   host Claude): grave o ajuste e diga em uma linha que este host não tem presets — não invente um.
   **Host com presets e sem a linha `Perfil ativo`**: grave-a antes do ajuste — `padrao`, data de
   hoje, sem desvio, no formato da linha do template. Semear **depois** do ajuste faria o valor
   recém-alterado virar baseline permanente do `padrao`, e a divergência nunca mais apareceria como
   desvio. Só então: compare o valor novo ao preset **ativo** — inclusive quando o ativo é `padrao`,
   que não é estado-zero, é um preset como outro qualquer: divergiu → registre o desvio na linha
   **Perfil ativo** daquele host; voltou a bater com o preset → **remova** o desvio. Desvio vale só
   para papéis da tabela do host; estado de via cross-vendor não é desvio e nenhum perfil o toca.
4. Confirme o que mudou, **em qual host**, e **a partir de quando vale** (próximo spawn — não afeta
   agente em execução).

**Migração aditiva obrigatória:** antes de qualquer ajuste, leia o `_elenco.md` inteiro. Preserve
modelos, perfis e vias escolhidos pelo projeto; acrescente somente headings obrigatórias ausentes.
Se `## Matriz de invocação` ou `## Times por host` existir mas estiver incompleta, mostre o diff
proposto e pare no gate — não substitua uma linha já escolhida sem aprovação explícita.

**Migração de arquivo legado (anterior à 0.24.0)** — proposta com gate, nunca reescrita silenciosa.
Arquivo sem migração continua funcionando: o time vem de `## Times por host`, e onde essa seção não
existir valem os padrões de fábrica deste template.

⚠️ **Migre por SEÇÃO, não só a tabela ativa.** Um arquivo legado tem tabelas de papel em mais de um
lugar: a tabela ativa **e cada preset** de `## Perfis`. Converter só a ativa deixa presets de 5
linhas no arquivo; no primeiro `perfil economia`, a tabela do host é reescrita a partir de um preset
com **papéis faltando e eixos colapsados** — o defeito só aparece muito depois da migração, quando
ninguém mais liga uma coisa à outra. **Aplique as conversões de papel abaixo em todas as tabelas**, e
valide a aritmética antes de propor: preset legado de 5 linhas (`planner`, `implementer`, `reviewer`,
`docs`, `scout`) vira **exatamente 8** (planner +1, implementer +2); tabela de host vira **9** (as 8
mais `manager`). Contagem diferente disso = migração incompleta, não proponha.

**Conversões de papel — valem para a tabela ativa e para cada preset:**

- linha `planner` única → as **duas trilhas** naquele mesmo modelo, e diga que o eixo de domínio
  ficou desligado até ele escolher o par;
- linha `implementer` única → as **três faixas** naquele mesmo modelo;
- linha `reviewer (interno)` → o **reviewer único do vendor oposto ao host**, com a perda nomeada:
  o revisor do mesmo vendor do host saiu do fluxo padrão. **Num preset**, é a linha que mais engana:
  o modelo legado ali é do vendor do host, e mantê-lo devolveria o revisor interno pela porta do
  perfil.

**Conversões de estrutura:**

- **`## Papéis` presente** → era o time do host Claude sem dizê-lo. Proponha copiá-la para
  `### Host Claude` (preservando os modelos escolhidos) e **remover** o heading `## Papéis`, para não
  restar duas fontes. Enquanto o dono não aprovar, ela fica lá, **legada e não lida**.
  **`### Host Claude` já existe?** Então há duas versões do mesmo time e **não existe regra implícita
  de sobrescrita** — nem "o mais novo vence", nem "o `## Papéis` vence por ser o que era lido".
  Monte a **reconciliação linha a linha** (papel · valor em `## Papéis` · valor em `### Host Claude` ·
  o que você propõe · por quê), mostre no gate e espere a escolha dele. Divergência é informação:
  costuma ser um ajuste feito numa das duas e perdido na outra.
- **`## Perfis` presente** → declare de qual host aquele preset é (nos arquivos legados, sempre o
  Claude): o heading passa a nomear o host, como no template (`## Perfis — times nomeados do host
  Claude`). A seção continua no topo do arquivo, **não** vai para dentro de `### Host Claude` —
  aninhar preset dentro da tabela que ele reescreve confunde fonte com cópia.
- **linha de revisor externo de um vendor que este elenco não suporta mais** (host aposentado numa
  release anterior) → proponha a **remoção**, mostrando o diff, e espere o "pode" — apagar em
  silêncio some com o registro de por que ele existia. Vale também dentro dos presets, onde essa
  linha costuma sobreviver esquecida.

**`manager` é caso especial:** é a sessão principal, definida pelo `/model` do host — não dá pra
trocar por aqui. Se ele pedir, explique e sugira o `/model`.

## Com argumento `perfil <nome>` — trocar o time inteiro

`$ARGUMENTS` no formato `perfil <nome>`. Exemplos: `perfil economia` · `perfil padrao`.

0. **Resolva o host primeiro** (mesma razão do passo 0 acima) e vá à seção `## Perfis` **daquele
   host**. Host sem presets → diga isso e ofereça o ajuste papel a papel; **não** aplique preset de
   outro host, que traria modelos do vendor errado para os papéis de escrita.
   **Seção "Perfis" ausente num host que a tinha** (arquivo pré-0.16.0)? Semeie antes de aplicar, e
   avise em uma linha: preset `padrao` = a **tabela atual daquele host**, sem a linha `manager`
   (ela é o titular deste projeto — semear da fábrica devolveria, em silêncio, um time que o projeto
   nunca usou); preset `economia` = o time de fábrica. Arquivo sem a linha **Perfil ativo**?
   Grave-a também — `padrao`, com a data de hoje, sem desvio.
1. Leia a seção **Perfis** daquele host. Perfil inexistente → liste os que existem e **pergunte**;
   não crie perfil novo sem pedido explícito.
2. **Reescreva a tabela do host resolvido** dentro de `## Times por host`, a partir do preset
   (modelos e "Por quê"), e atualize a linha **Perfil ativo** daquela seção — nome + data, zerando
   desvios anteriores. **A linha `manager` não faz parte de preset nenhum — preserve-a como está.**
   Os presets têm 8 linhas (sem `manager`); a tabela do host tem 9. Reescrever "as 8 linhas do
   preset" apagaria o `manager`, e `perfil padrao` não o devolve — é perda permanente. **O estado
   das vias cross-vendor (seção "Revisores externos") também não é preset — não aplique o que o
   preset declarar; preserve o que está registrado agora**, pela mesma razão do `manager`: é o que
   está de fato instalado e ativo no projeto, não uma escolha do time. A linha "Revisores externos"
   dentro de cada preset é só informativa (estado de fábrica, de leitura).
3. Confirme mostrando o time novo, **em qual host**, **e o que se perde** — resuma a nota do preset
   em até 3 linhas. Havia desvio registrado na linha Perfil ativo? **Diga em uma linha que ele foi
   descartado** — sem isso, o registro só muda onde a escolha some, não o silêncio. **Anuncie, não
   pergunte**, e diga **na hora como reverter** (ex.: "quando o crédito voltar, é só dizer" ou
   `/orq:elenco perfil padrao`) — não invente nem espere que ele decore uma frase fixa de volta; o
   pedido de reverter é reconhecido como o pedido de mudança que é, na hora em que ele vier.
4. A troca vale a partir do **próximo spawn, nas janelas daquele host** — crédito é da conta, não da
   frente. Agente já em execução termina no modelo antigo; não refaça nada. Se houver card `[~]`
   no board, diga em uma linha que ele termina com elenco misto, e que isso é esperado.
5. **`manager` não muda por perfil.** Ao ativar um perfil de economia, sugira em uma linha que o
   dono avalie o `/model` da sessão — é onde mora o maior consumo, e só ele troca.
6. **Perfil nunca troca o vendor do `reviewer`.** Ele rebaixa degrau/effort **dentro do mesmo
   vendor**: rebaixar o revisor para o vendor do host acabaria com a independência, que é a única
   coisa que ele entrega.

## Modelo do arquivo

```markdown
# Elenco — quem toca cada papel

**Onde o modelo é resolvido:** identifique o host, leia a tabela dele em `## Times por host`, e
aplique a célula da `## Matriz de invocação`. **Não existe outra tabela ativa** — nem para ler, nem
para gravar.

## Times por host

Cada host resolve o próprio time **na leitura** desta seção. `/orq:elenco` grava aqui, sempre na
seção do host onde está rodando — uma janela nunca reescreve o time da outra. “Configurado” não
significa “rodando agora”: o Manager verifica a sessão/CLI real antes de anunciar o papel.

### Host Claude

| Papel | Modelo | Sandbox / mecanismo |
|---|---|---|
| manager | modelo da sessão (`/model`) | sessão principal |
| planner·interface | `fable` | spawn nativo, read-only |
| planner·sistema | `gpt-5.6-sol@ultra` | `codex exec … -s read-only` — comprovado como revisor; como planner, ainda não exercitado |
| implementer·pesada | `opus` | worktree dedicado, writer único |
| implementer·normal | `sonnet` | worktree dedicado, writer único |
| implementer·leve | `haiku` | worktree se houver trabalho paralelo |
| reviewer | `gpt-5.6-sol@xhigh` | `codex exec … -s read-only` — vendor oposto ao host |
| docs | `sonnet` | arquivos de documentação autorizados |
| scout | `sonnet` | read-only |

**Perfil ativo:** `padrao` — desde <data de hoje>, sem desvio.
*(É o formato canônico da linha — a única vez que ele é definido, e vale por host. Ajuste papel a
papel que diverge do preset ativo — inclusive com `padrao` ativo — vira `padrao · desvio:
papel→modelo`; devolvido ao preset, remove-se o desvio. Ver passo 3 de "Com argumento — ajustar".)*

### Host Codex

| Papel | Modelo | Sandbox / mecanismo |
|---|---|---|
| manager | `gpt-5.6-sol@high` | sessão principal; verificar, não trocar silenciosamente |
| planner·interface | `opus` (exigir comprovação de que o alias resolve para Opus 5) | runner Anthropic, read-only |
| planner·sistema | `gpt-5.6-sol@ultra` | `read-only` |
| implementer·pesada | `gpt-5.6-sol@xhigh` | `workspace-write`, em worktree dedicado |
| implementer·normal | `gpt-5.6-terra@xhigh` | `workspace-write`, em worktree dedicado |
| implementer·leve | `gpt-5.6-luna` (sem effort declarado — ver nota) | `workspace-write`, em worktree dedicado |
| reviewer | `opus` (exigir comprovação de que o alias resolve para Opus 5) | runner Anthropic, read-only, sem ferramentas |
| docs | `gpt-5.6-sol@low` | arquivos de documentação autorizados |
| scout | `gpt-5.6-sol@low` | read-only |

**Nota do `implementer·leve`:** o degrau vai **sem effort declarado** de propósito — o smoke que
liberou o modelo provou que ele responde quando endereçado, não quais reasoning efforts aceita nem
como se comporta em `workspace-write`. Declarar um effort aqui seria inventar procedência. Registre
a medição no `_elenco.md` do projeto quando ela existir.

**Perfil ativo:** — este host não tem presets de fábrica; ajuste papel a papel. Criar um `## Perfis`
para ele é pedido do dono, não iniciativa.

## Revisores externos

Esta seção **não é composição de painel** — o revisor é **um só**, resolvido pela tabela do host.
Aqui mora o **registro de capacidade das vias cross-vendor**: por onde um papel read-only alcança o
vendor oposto, com o que já foi comprovado e quando. O nome na coluna **Via** é o que se digita em
`/orq:elenco <via> on|off`.

| Via | Vendor | Consumida por | Estado | Registro |
|---|---|---|---|---|
| codex | OpenAI | **host Claude**: `planner·sistema` e `reviewer`. No host Codex **não é via** — é o vendor nativo | ativo | CLI `codex` no PATH · `codex exec … -s read-only … < /dev/null` · modelo e effort vêm da tabela do host |
| runner-opus | Anthropic | **host Codex**: `planner·interface` e `reviewer`. No host Claude **não é via** — é o vendor nativo | ativo | runner Anthropic `scripts/run-opus-reviewer.py` · comprova `claude-opus-5` · 16 KiB por lote · timeout 600s |

A coluna **Consumida por** é o que torna o efeito de ligar/desligar anunciável sem chute: uma via só
afeta os papéis listados, nos hosts listados. Via cujo vendor é o do próprio host não é via nenhuma
ali — é o mecanismo nativo, e desligá-la não muda nada naquele host.

Aqui, **ativo significa política habilitada, não capacidade comprovada** — são duas checagens
distintas e **as duas são obrigatórias antes de usar a via**:

1. **Política** — a coluna `Estado` diz `ativo`? `inativo` é decisão do dono: **não use a via**, nem
   "só desta vez". Consumidor que ignora o `Estado` faz a transferência cross-vendor que o dono
   desligou.
2. **Capacidade** — binário, autenticação, modelo e saída não vazia, verificados no momento do uso.

Falhar em qualquer uma **não autoriza trocar de vendor**: no reviewer, as duas produzem
`REVISÃO DEGRADADA`, com a causa nomeada (política desligada **ou** capacidade ausente — são
diagnósticos diferentes e o dono precisa saber qual dos dois foi).

## Matriz de invocação

Resolva sempre **host → papel → vendor → mecanismo**. Toda CLI recebe `< /dev/null`; sem TTY os
dois vendors podem bloquear lendo stdin. O briefing para terceiro é sanitizado e nunca leva dado
de paciente, PII, prontuário ou credencial.

| Vendor do modelo | Host Claude | Host Codex |
|---|---|---|
| Anthropic | spawn nativo com override | `printf '%s' "$BRIEFING_SANITIZADO" \| python3 "<ORQ_PACKAGE_ROOT-resolvido>/scripts/run-opus-reviewer.py"` — limite 16 KiB/lote, timeout e comprovação `claude-opus-5`; o runner só comprova `claude-opus-5`, então a trilha `interface` aqui pensa com Opus |
| OpenAI | `codex exec -m <modelo> -c model_reasoning_effort=<effort> -s <sandbox> "<briefing>" < /dev/null` | **Host Codex: `codex exec` é obrigatório**; primitiva nativa só quando `_elenco.md` registrar override comprovado por chamada real |

## Perfis — times nomeados do host Claude

Presets são **por host**: os dois abaixo valem para `### Host Claude` e são aplicados por
`/orq:elenco perfil <nome>` **rodando naquele host**. Cada preset é uma tabela **literal e
completa** — nunca uma referência a "a tabela acima". É isso que permite voltar (`perfil padrao`)
sem depender de memória: se `padrao` fosse só um ponteiro para a tabela do host, ativar `economia`
reescreveria a tabela e `padrao` passaria a apontar para o próprio `economia` — o time titular
sumiria do arquivo. `manager` e o estado das vias cross-vendor ficam fora dos dois presets: nenhum
perfil os toca, e aplicar um preset **preserva a linha `manager` e a seção "Revisores externos"**.

### `padrao` — o time titular

| Papel | Modelo | Por quê |
|---|---|---|
| planner·interface | fable | trilha perceptual pensa com Anthropic |
| planner·sistema | gpt-5.6-sol@ultra | trilha comportamental pensa com OpenAI |
| implementer·pesada | opus | alto risco ou decisão de desenho ainda aberta |
| implementer·normal | sonnet | plano fechado, execução dirigida |
| implementer·leve | haiku | resultado determinado, verificação mecânica |
| reviewer | gpt-5.6-sol@xhigh | vendor oposto ao host — a independência não se rebaixa |
| docs | sonnet | escrita objetiva sobre código já pronto |
| scout | sonnet | leitura ampla e barata |

Revisores externos: via `codex` ativa · via `runner-opus` ativa — estado de fábrica, informativo: o
perfil não aplica isto (ver passo 2 de "Com argumento `perfil <nome>`"), vale o que está registrado.

### `economia` — crédito curto

| Papel | Modelo | Por quê |
|---|---|---|
| planner·interface | opus | um planner só de Anthropic, sem o degrau extra de raciocínio |
| planner·sistema | gpt-5.6-sol@high | effort rebaixado dentro do mesmo vendor |
| implementer·pesada | sonnet | rebaixado um degrau — evita herdar o modelo caro da sessão |
| implementer·normal | sonnet | já era o degrau econômico |
| implementer·leve | haiku | já era o mais barato |
| reviewer | gpt-5.6-sol@high | effort rebaixado; **vendor não muda** — sem ele, não há revisão independente |
| docs | haiku | escrita objetiva; rebaixar aqui custa pouco |
| scout | haiku | leitura ampla e barata |

Revisores externos: via `codex` ativa · via `runner-opus` ativa — mesmo estado de fábrica do preset
`padrao`, também informativo, não aplicado pelo perfil (ver passo 2 acima). Quem decide o briefing
enxuto do `--rapido` é o `/orq:revisar` — regra lá.

**O que se perde — registre com todas as letras ao criar este perfil neste projeto:** o parecer
único fica com menos effort, e como ele é o **único** parecer independente, não há segundo revisor
para compensar — a auditoria do Manager contra o código passa a carregar mais peso; a escrita
rebaixada erra mais em card `pesada`, que é justamente onde ou o desenho ainda está aberto ou a
consequência do erro é a maior do board.
Ajuste os modelos e a nota à realidade do projeto — os valores acima são ponto de partida, não
contrato fixo.
```

## Como isso é aplicado

Ao spawnar um papel, os comandos (`plan-next`, `implement-next`, `revisar`, `init`) **leem o elenco**
pela frase normativa do topo: host → tabela do host → Matriz. Sem elenco, valem os padrões de
fábrica deste template; o `model:` dos arquivos em `agents/` é o último recurso.

## Orientação (quando ele pedir recomendação)

- **Planner e Reviewer** são onde modelo forte mais se paga: um erro de plano custa a implementação
  inteira; um review fraco deixa passar o que vai quebrar depois.
- **Docs e Scout** são leitura/escrita objetiva — modelo menor resolve e sai mais barato.
- **Implementer** se dimensiona pela faixa, não pelo gosto: `pesada` só quando resta desenho por
  decidir; `leve` só quando a verificação é mecânica.
- **Só Claude, sem GPT?** `codex off` desliga a via externa — e, com ela, **o único revisor
  independente que existe** naquele host. Toda revisão passa a ser **degradada**: o Manager audita o
  diff ele mesmo e declara a ausência. Diga isso com todas as letras antes de desligar; não existe
  cair num revisor do mesmo vendor do host para tapar o buraco.
- Trocar modelo **não** troca a disciplina: as regras dos agentes valem igual.
- **Fim do ciclo de crédito?** `perfil economia` troca o time inteiro do host Claude — e o preset
  diz, com todas as letras, o que se perde. `perfil padrao` desfaz.
