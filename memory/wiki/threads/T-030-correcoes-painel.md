# T-030 — Correções do painel de três revisores sobre as releases 0.14.0–0.16.0

> **Origem:** `/orq:revisar` em 2026-08-02, primeiro painel de **três** revisores independentes
> (Opus interno · Codex `gpt-5.6-sol` read-only · Kimi K3 em worktree descartável).
> **Os três reprovaram, independentemente.** Alvo revisado: `git diff 4f3c113~1 HEAD -- orq/ README.md`.
>
> **Este card bloqueia `T-020`, `T-025` e `T-023`**, que estão em VALIDATE e não podem fechar como estão.

## Por que este card existe separado dos três

Os defeitos estão espalhados por três releases e vários deles se cruzam no mesmo arquivo
(`elenco.md` aparece em quatro achados). Corrigir card a card faria três edições concorrentes nos
mesmos parágrafos — que é exatamente a mecânica que produziu os defeitos originais. Um card, um
plano, um review.

## Precedente que o plano DEVE respeitar

**Nas três releases anteriores, o defeito veio da CORREÇÃO, não da implementação original.**
Na 0.14.0 a correção criou contradição entre `orq/stack.md` e `orq/commands/stack.md`; na 0.15.0
duas correções interagiram e produziram uma exceção inalcançável; na 0.16.0 a correção de um
ponteiro auto-referente plantou o único caminho relativo do plugin.

**Consequência para este plano:** cada correção abaixo é uma mudança como outra qualquer e precisa
de review próprio. Nenhuma delas é "ajuste de texto".

---

## ACHADOS

### 🔴 A1 — O teto do N2 se contradiz, e a contradição está DUPLICADA

**Onde:** `orq/skills/orq/SKILL.md:225` **e** `orq/skills/orq/SKILL.md:101-105`
**Quem achou:** Codex + Kimi, independentes. Verificado nos dois pontos pelo Manager.

A regra declara **"Teto: 1 proposta não solicitada por bloco de trabalho, contado por assunto"**.
Sete linhas depois, a exceção de recusa-de-momento autoriza **"pode ser reproposta no mesmo bloco,
a cada piora material (ex.: recusou aos 52%, reproponha perto de 75%, de novo perto de 90%)"**.

São **três propostas do mesmo assunto no mesmo bloco**, num nível cujo título é
*"N2 — propõe uma vez, nunca insiste"*.

**A duplicação é o que torna isso perigoso.** O parágrafo do ~50% (linhas 101-105) repete a mesma
regra, e ali a contradição fica ainda mais nua: *"proponha 1× por bloco de trabalho"* e *"pode
voltar a propor no mesmo bloco"* na mesma frase. **Uma correção que toque só um dos dois lugares
deixa o defeito vivo** — e foi assim que ele chegou à terceira rodada.

**Este é o bloqueador B2 que o card `T-025` declara resolvido em três rodadas de correção.**
A correção anterior mudou o teto de "por bloco" para "por assunto" — o que resolve *assuntos
diferentes competindo pelo mesmo teto*, e **não** a contradição entre "teto 1" e "repropõe 2× mais".
Corrigiu-se a parte errada do problema.

**Saídas sugeridas pelos revisores (o plano escolhe e justifica):**
- (a) redefinir o teto como "1 proposta por assunto **por nível da condição** — piora material
  rearma o teto", espelhando nos dois lugares; ou
- (b) remover a exceção e fazer qualquer recusa encerrar o assunto no bloco.

⚠️ **Terceira volta do mesmo defeito. O plano tem que explicar por que a saída escolhida não admite
uma quarta.**

---

### 🔴 A2 — `--rapido` mudou três consumidores que o `T-020` exigia que não mudassem

**Onde:** `orq/commands/revisar.md:96-98` · `orq/commands/implement-next.md:33-35` ·
`README.md:237-238` (+ `orq/commands/elenco.md:112-113`)
**Quem achou:** os três, por ângulos diferentes.

O requisito duro do `T-020` era **"nenhum consumidor muda"**. Três mudaram.

Três problemas distintos, no mesmo lugar:
1. **Contradição literal** (Codex): a mesma instrução diz *"só o revisor interno"* e *"mantenha
   pelo menos um externo"*.
2. **Preso ao nome do perfil, não ao modelo real** (Opus): a regra diz "no perfil `economia` o
   revisor interno está rebaixado" — mas o próprio template declara que os modelos do preset são
   *"ponto de partida, não contrato fixo"*. Perfil `economia` que mantenha `reviewer opus` recebe
   uma afirmação falsa; perfil chamado `barato` que rebaixe o reviewer escapa da regra.
3. **Pressupõe que existe externo ativo** (Kimi): num projeto solo-Claude — e o template de fábrica
   nasce com `kimi-k2 inativo` — a instrução exige um revisor que não existe e **não dá saída**.
   O `ajuda.md:32-33` mostra que o caso é conhecido em outro lugar do plugin.

---

### 🔴 A3 — O `T-023` não sobreviveu: a regra binária vive fora do lugar canônico

**Onde:** `orq/commands/stack.md:146` · `orq/stack.md:218-220`
**Quem achou:** Opus + Kimi. Verificado pelo Manager.

`orq/commands/stack.md:146` afirma categoricamente *"é preciso reiniciar a sessão"*, e
`orq/stack.md:218` cita como evidência o `update --help` que **a tabela canônica criada pela própria
0.14.0 declara conservador e não confiável** (`README.md:391-407`).

**Cenário:** o dono instala uma ferramenta; uma janela afirma "exige restart" como fato, outra
(lendo o canônico) diz "não testado — presuma restart". Dois discursos incompatíveis sobre o mesmo
evento — o defeito exato que o `T-023` existia para eliminar, pela segunda vez.

⚠️ **Cuidado do plano:** `orq/commands/stack.md` trata de **instalar ferramenta nova**, que é caso
diferente de **update de cache do plugin**. A revisão da 0.14.0 concluiu explicitamente
*"manter — ali é regra operacional correta"*. A correção provavelmente é de **vocabulário e
procedência** (trocar "exige" por "presuma restart — não testado" + ponteiro para a tabela), não de
regra. **Não inverter a regra: foi inverter que produziu este card duas vezes.**

---

### 🟠 A4 — Ajuste papel-a-papel some sem aviso na volta do perfil

**Onde:** `orq/commands/elenco.md:31-33`
**Quem achou:** os três.

O desvio só é registrado *"se o perfil ativo **não** for o 'padrao'"*.

**Cenário:** com `padrao` ativo o dono diz *"quero o Opus planejando"* → a tabela muda, mas a linha
"Perfil ativo" continua dizendo "sem desvio" → depois `economia` (o passo 2 zera desvios) → depois
volta → o preset **literal** reescreve a tabela → a escolha explícita do dono desaparece, sem aviso.

A regra protege os desvios dos perfis temporários e desprotege justamente o perfil que é **o ponto
de retorno do ciclo**. Contradiz o objetivo declarado do card ("voltar sem depender de memória").

**Correção mínima convergente:** registrar desvio sempre que o ajuste divergir do preset ativo,
inclusive quando o ativo é `padrao`.

---

### 🟠 A5 — O template do `_elenco.md` não tem a seção que o próprio comando manda reescrever

**Onde:** `orq/commands/elenco.md:45` (instrução) vs `orq/commands/elenco.md:63-122` (template)
**Quem achou:** Opus. Verificado pelo Manager.

O passo 2 manda *"Reescreva a tabela ativa **Papéis**"*. O template que o comando entrega **não gera
heading `Papéis` nenhum** — a tabela fica solta sob o H1 — e o arquivo gerado tem **três tabelas com
cabeçalho idêntico** `| Papel | Modelo | Por quê |` (ativa, preset `padrao`, preset `economia`).

**Cenário:** projeto novo instalado pelo `/orq:init` (a FASE 4 item 2b manda gerar deste template) →
*"tô com pouco crédito"* → o agente procura a seção, não acha, e reescreve o **preset `padrao`**.
O time titular é destruído, a tabela ativa não muda (o perfil não tem efeito), e nada acusa.

**Este repo é imune por acidente:** o `memory/wiki/_elenco.md:14` tem
`## Papéis (tabela ativa — é ESTA que os comandos leem)` — heading escrito à mão, que o template não
gera. **Mesma mecânica do `T-029`:** verde aqui porque o repo *é* o plugin.

**Correção mínima:** pôr esse heading no template.

---

### 🟠 A6 — Presets usam ponteiro para os revisores externos

**Onde:** `orq/commands/elenco.md:102` ("os do estado registrado acima") e `:115`
("ativos continuam ativos")
**Quem achou:** Opus + Codex.

As linhas 85-90 do mesmo arquivo declaram que preset é *"tabela literal e completa — nunca uma
referência a 'a tabela acima'"*, e explicam por quê. **Os revisores externos escaparam dessa regra.**

**Cenário:** projeto cria um terceiro preset que desliga o `codex`; ativa; depois `perfil padrao` →
"o estado registrado acima" já é o mutado → o `codex` continua desligado e o painel cai para um
revisor **em silêncio**. É a mesma família do ponteiro auto-referente que a 0.16.0 alegou ter
matado — sobrevivendo na metade do arquivo que a correção não olhou.

O `memory/wiki/_elenco.md:69` já faz certo (lista literal). O template, não.

---

### 🟠 A7 — Template grava "Perfil ativo" sem data

**Onde:** `orq/commands/elenco.md:75` vs `:46`
**Quem achou:** os três.

O template gera `**Perfil ativo:** \`padrao\`` — sem data, sem estado de desvio — enquanto o passo 2
exige "nome + data" e o card pede "nome, data e desvios". Todo projeto novo nasce fora do formato
que o próprio comando manda manter. (Este repo usa um terceiro formato:
`` `padrao` — desde 2026-07-28, sem desvio ``.)

---

### 🟡 A8 — `/orq:elenco perfil` é inalcançável em projeto anterior à 0.16.0

**Onde:** `orq/commands/elenco.md:43-44`
**Quem achou:** Opus. **Atenuação encontrada pelo Manager, que o revisor não citou.**

`_elenco.md` gerado até a 0.15.0 não tem seção "Perfis". A instrução manda *"liste os que existem e
pergunte; não crie perfil novo sem pedido explícito"* → a lista sai vazia e criar está proibido.
**O plugin está em escopo `user`** — vale em todos os projetos do dono.

**Atenuação:** a regra de idempotência do `init` ("detecta o que existe, completa o que falta") dá
saída via `--reinstalar`. Ela só não está apontada no ponto onde a feature falha.

**Correção mínima:** um passo 0 no bloco `perfil <nome>` — seção "Perfis" ausente → semeie do
template e avise, antes de aplicar.

---

### 🟡 A9 — O gatilho N1 depende de um argumento que o dono nunca digita

**Onde:** `orq/skills/orq/SKILL.md:219-221`
**Quem achou:** Opus.

O gatilho (a) do N1 dispara com *"`$ARGUMENTS` do `/orq:checkpoint`"*. Mas **a premissa do produto é
que o dono não digita comando** — a rota natural é *"terminamos"* / *"salva aí"* (`SKILL.md:70`), que
não passa argumento nenhum, e nada manda derivar o rótulo da conversa.

**Cenário:** *"terminamos, fechamos a 0.16.0"* → há marco, não há `$ARGUMENTS` → o gatilho (a) nunca
dispara. Na prática só o (b) funciona. **Meia política inalcançável por construção** — mesma família
do A1.

Note que a tabela da própria skill (`SKILL.md:85`) descreve o gatilho **sem** mencionar
`$ARGUMENTS`, e portanto é alcançável: os dois lugares discordam.

---

### 🟡 A10 — Colisão de "última linha" entre o N1 e o formato do checkpoint

**Onde:** `orq/skills/orq/SKILL.md:85` vs `orq/commands/checkpoint.md:98-165`
**Quem achou:** Opus.

O N1 manda relatar o achado do `wiki-lint` *"em uma linha no fim da resposta em curso"*. A resposta
em curso é o relatório do checkpoint, cujo formato é contrato fechado — seções nomeadas, nesta
ordem, terminando no bloco `💡`, com *"nunca junte seções"*.

**Cenário:** checkpoint de marco com achado de lint → duas instruções disputam a última linha da
mesma resposta; se o Manager escolher o contrato do checkpoint, o achado do N1 evapora.

---

### 🟡 A11 — `ajuda.md` diz "13 situações"; a tabela tem 16

**Onde:** `orq/commands/ajuda.md:38`
**Quem achou:** Opus + Kimi. Contado pelo Manager: 16 linhas (15-30).

**Cenário:** o modelo lê "as 13 situações" como tamanho-alvo e poda 3 linhas para obedecer — as
candidatas naturais são as três sem frase entre aspas.
**Correção mínima:** "as situações da tabela acima", sem número.

---

## Fora do escopo deste card

- **`README.md:231-234`** ("Kimi K2 não está instalado") — achado independente por Opus, mas **já é
  o card `T-028`**. Vale registrar que o painel confirmou um card que existia sem ninguém apontar.
- **`orq/commands/init.md:161`** (caminho relativo `orq/scripts/kanban-status.sh`) — **pré-existente
  ao diff**, confirmado por `git diff`. É o card `T-029`.

## Achados descartados na reconciliação — e por quê

- **Codex, "os níveis N0/N1/N2 estão quebrados"**: artefato do **briefing do Manager**, que usou uma
  numeração errada ("N0/N1/N2") ao descrever a entrega. O produto usa `N0` + `N1-N3` e desambigua
  isso explicitamente no texto. **Defeito do briefing, não do plugin.** Lição: briefing impreciso
  gera achado fantasma — o painel gasta rodada com ele.
- **Codex, `memory/wiki/distribuicao.md:32` "espelho parcial"**: o espelho cobre os cinco componentes
  de plugin e aponta para a tabela canônica; o que ele queria ver ali (PATH, scripts) não é
  componente de plugin.

---

## Evidência de método que este painel produziu

1. **Três revisores acharam coisas diferentes.** O Kimi foi o único a ver a **duplicação** em
   `SKILL.md:101-105` e o único a ver o caso **solo-Claude** do A2. O Codex foi o único a ver o A1.
   O Opus foi o único a ver o A5, A8, A9, A10. **A interseção validou 5 achados; a divergência
   produziu os mais graves.**
2. **O worktree descartável funcionou** — `git status` vazio no fim. Registrado no `T-019`.
3. **O painel confirmou um card que já existia** (`T-028`) sem ninguém contar ao revisor.

---

## 📐 PLANO — Planner, 2026-08-02

> Escrito com os 11 achados reverificados no código em disco (linhas conferidas uma a uma), mais um
> cruzamento que a thread não citava: a regra LGPD de `revisar.md:42-44` **usa o `--rapido` para
> excluir os externos** — qualquer correção do A2 que mande "incluir um externo" colide com ela se
> não houver precedência explícita. Está tratado abaixo.

### Problema (a causa raiz, por achado — não o sintoma)

A tese que atravessa os 11: **quase todos são o mesmo defeito estrutural — uma regra enunciada em
mais de um lugar, ou condicionada a um proxy em vez da propriedade real.** As três rodadas
anteriores falharam porque corrigiram o *enunciado* num dos lugares, não a *estrutura* que permite
aos lugares divergirem.

- **A1** — o teto e a exceção usam a palavra "proposta" com **unidades diferentes** (o teto conta
  falas; a exceção conta assuntos-recusados-por-enquanto), e a regra completa está **duplicada**
  (N2 normativo + parágrafo do ~50%). Rodada 1 corrigiu a unidade errada; rodada 2, o lugar errado.
  Enquanto existirem *duas cláusulas* (regra + exceção) em *dois lugares*, a 4ª rodada é questão de
  tempo.
- **A2** — a regra foi condicionada ao **nome do perfil** (proxy) em vez da propriedade real
  (reviewer interno rebaixado), e **replicada por copy-paste em 4 consumidores** — o oposto do
  requisito do `T-020`. Cada réplica divergiu um pouco; daí a contradição literal.
- **A3** — as duas frases **pré-datam a tabela canônica** que a 0.14.0 criou; a release criou o
  canônico mas não varreu os enunciados antigos para subordiná-los. Sobrou modalidade de fato
  ("é preciso") onde o canônico só autoriza modalidade de evidência ("presuma — não testado"), e uma
  citação (`update --help`) que o próprio canônico rebaixou a "aviso conservador".
- **A4** — a condição de registro usa o nome `padrao` como proxy de "não há o que registrar",
  tratando-o como estado-zero — quando `padrao` é um preset como outro qualquer **e** é o ponto de
  retorno do ciclo. A propriedade real é "o valor gravado diverge do preset ativo".
- **A5/A6/A7** — causa comum: **produtor e consumidor sem contrato** (o mesmo padrão do gotcha do
  `kanban-status.sh`). O passo 2 nomeia uma seção que o template não gera (A5); o template viola a
  regra de literalidade que ele mesmo enuncia 15 linhas antes (A6); a linha "Perfil ativo" existe em
  três formatos porque nunca foi definida uma única vez (A7). O repo é imune porque a instância
  daqui foi escrita à mão — verde por acidente, mecânica do `T-029`.
- **A8** — feature da 0.16.0 assumiu arquivo da 0.16.0: **não há caminho de migração** para
  `_elenco.md` anterior, e a saída que existe (idempotência do `init`) não está apontada no ponto da
  falha.
- **A9** — a política N1 foi escrita do ponto de vista do **mecanismo** (`$ARGUMENTS`) e não da
  **interface do produto** (fala natural) — a inversão exata que a skill existe para impedir.
  Agravante estrutural: a *forma do relato* também está duplicada (tabela linha 85 + regra N1) —
  o mesmo padrão do A1, ainda sem contradição, esperando a próxima correção parcial.
- **A10** — duas normas de releases diferentes **reivindicam a mesma posição** ("última linha da
  resposta") sem cláusula de precedência; o N1 (0.15.0) não consultou o contrato de formato do
  checkpoint.
- **A11** — **contador duplicado**: o tamanho da tabela vive na prosa E na tabela; a tabela cresceu,
  a prosa não. Mesma família da versão em quatro lugares — só que este contador nenhum lint guarda.

### Solução — e por que essa

**Cada regra passa a ter exatamente um lugar normativo e a condicionar-se à propriedade real, nunca
ao proxy. Os demais lugares resumem e apontam.** É isso — e não a escolha de palavras — que fecha a
porta da 4ª rodada: a alternativa "corrigir os enunciados nos lugares onde estão" é literalmente o
que as rodadas 1-3 fizeram.

**A1 — escolhida a (a), reformulada, com desduplicação obrigatória. A (b) foi rejeitada** porque
amputa comportamento que o dono quer: o rearme em piora material (52→75→90%) pré-data os níveis
(era a regra do ~50% original) e removê-lo produziria o pedido de volta — a 4ª rodada por outra
porta. A reformulação funde teto e exceção numa **cláusula única**:

> *Teto: 1 proposta não solicitada por assunto **e por estado da condição**. Recusa de política
> ("não quero X") congela o assunto até o fim do bloco. Recusa de momento ("agora não"): piora
> material da condição = estado novo = o teto rearma (ex.: recusou aos 52% → só volte perto de 75%,
> de novo perto de 90%). O que o teto proíbe é insistir sem a condição ter piorado.*

E o título do N2 muda de *"propõe uma vez, nunca insiste"* para *"propõe, nunca insiste"* — o
"uma vez" do título era um terceiro enunciado do teto, e também contradizia a exceção.

**Por que não admite a 4ª rodada:** as rodadas 1-3 foram, todas, variações de "dois textos, uma
correção". A saída remove as duas condições de existência do defeito: **(i)** deixa de existir o par
regra+exceção — o rearme é parte da *definição* do teto, não cláusula concorrente; não há duas
frases para divergir; **(ii)** deixa de existir o par de lugares — o parágrafo do ~50% vira exemplo
com ponteiro ("é o exemplo canônico do N2; teto e cadência moram na regra N2"), sem números e sem
"1×"; correção futura só tem um texto para tocar. E **(iii)** o critério de aceite ganha um guarda
mecânico: `grep` provando que "Teto:" e o exemplo 52/75/90 aparecem **uma única vez** em `orq/`.
Uma 4ª rodada exigiria a frase única contradizendo a si mesma — defeito que review de uma frase pega.

**A2 — a regra sai dos consumidores e volta para o dono do `--rapido` (`revisar.md`).** Regra
canônica única, condicionada à propriedade real: *"o reviewer interno da tabela ativa está num
modelo mais fraco que o do preset `padrao` do mesmo `_elenco.md`"* (ordem haiku < sonnet < opus;
`fable`/`inherit`/sem seção Perfis → **trate como não rebaixado** — na dúvida, comportamento
antigo). Três saídas explícitas, sem beco:
1. rebaixado + externo ativo → o `--rapido` inclui **um** externo;
2. rebaixado + **nenhum** externo ativo (solo-Claude) → roda só o interno **e anuncia em uma linha
   que o painel está no mínimo** (resolve o achado do Kimi);
3. **dado sensível no diff → a regra LGPD do passo 1 do próprio arquivo vence tudo**: só o interno,
   mesmo rebaixado, dizendo por quê (sem esta precedência, as duas regras do mesmo arquivo se
   contradizem — seria a 0.15.0 de novo).

Os outros três consumidores (`implement-next.md`, `README.md`, preset `economia` do template) voltam
ao enunciado simples pré-`T-020` + meia-linha de ponteiro ("quem decide o painel mínimo é o
`/orq:revisar`"), **sem re-enunciar condição e sem citar nome de perfil**.

**A3 — vocabulário e procedência; a regra não inverte.** Continua mandando reiniciar. Muda a
modalidade ("é preciso" → "presuma restart — não testado") e a procedência (o `--help` deixa de ser
citado como prova; vira "aviso conservador — para skill já foi desmentido 1×"). **Sem ponteiro de
arquivo para o README**: a tabela canônica vive no README do *repo*, que **não é copiado para o
cache do plugin** — um ponteiro seria referência quebrada em todo projeto instalado (a família
exata do `T-029`). O vocabulário vai inline, autossuficiente.

**A4** — registrar desvio sempre que o valor gravado divergir do preset ativo, **inclusive
`padrao`**; ajuste que devolve o papel ao valor do preset **remove** o desvio da linha; sem seção
"Perfis" para comparar, registra do mesmo jeito (informação a mais não destrói nada). Complemento
que fecha o cenário de ponta a ponta: **ao trocar de perfil com desvio registrado, dizer em uma
linha que ele foi descartado** — sem isso, o registro só muda *onde* a escolha some, não o silêncio.

**A5/A6/A7 — um contrato, um template.** Verificado: só existe um template (o `init.md:170-172`
gera do "Modelo do arquivo" do `elenco.md`), então as três correções são no mesmo bloco:
- heading `## Papéis (a tabela ativa — é esta que os comandos leem)` antes da tabela ativa — o
  formato que a instância deste repo já provou (A5);
- linha canônica `**Perfil ativo:** \`padrao\` — desde <data de hoje>, sem desvio` (com a variante
  `· desvio: papel→modelo` documentada ao lado); os dois pontos de instrução que hoje re-enunciam o
  formato (`:33` e `:46`) passam a dizer "no formato da linha do template" (A7 — formato definido
  **uma** vez);
- os dois presets ganham **lista literal** de revisores externos (`codex ativo · kimi-k2 inativo`,
  o estado de fábrica do próprio template), zero ponteiros (A6);
- **migração dos arquivos antigos (o buraco que a correção mínima do A5 deixaria):** o passo 2 ganha
  a regra de auto-cura — *"a tabela ativa é a que está sob `## Papéis`; se o arquivo (gerado por
  versão anterior) não tiver o heading, é a **primeira tabela do arquivo** — acrescente o heading ao
  regravar"*. Sem isso, o A5 continuaria vivo em todo projeto já instalado.

**A8** — passo 0 no bloco `perfil <nome>`: seção "Perfis" ausente → semear + avisar + só então
aplicar. **Divergência deliberada da correção mínima da thread** ("semeie do template"): o preset
`padrao` semeado nasce **da tabela ativa atual** (sem a linha `manager`), não da fábrica — num
arquivo pré-0.16.0 a tabela ativa *é* o time titular do projeto, e semear da fábrica plantaria a
próxima bomba: `perfil padrao` devolvendo um time que o projeto nunca teve, em silêncio (o desastre
do A5 por outra porta). `economia` semeia da fábrica (o projeto nunca teve um). → decisão nº 2.

**A9** — o gatilho (a) passa a ser definido pelo **rótulo de marco**, venha de onde vier: presente
em `$ARGUMENTS` quando o comando foi digitado, **ou derivado da fala natural que disparou o
checkpoint** ("fechamos a 0.16.0", "terminamos o release"). A tabela (linha 85) já descreve o
gatilho certo e não muda nesse ponto.

**A10** — cláusula de precedência em vez de disputa: em resposta com contrato de formato fechado, o
achado do N1 entra como **bullet da seção `✅ Verificação`** do próprio contrato — é evidência de
verificação, o lugar semanticamente correto, e a seção é a única sempre presente. `checkpoint.md`
autoriza o bullet do lado dele (o contrato *absorve* o N1). E a linha 85 da tabela para de
re-enunciar a forma ("uma linha no fim…") — desduplicação preventiva: é o par A1 ainda sem
contradição.

**A11** — remover o contador: "cobrir as situações reais da tabela acima". Nenhum número de linhas
em prosa.

**Instância deste repo (`memory/wiki/_elenco.md`)** — a nota do `economia` daqui contradiz a própria
tabela três linhas acima (`:90` "plano mais raso… alto risco não se planeja em economia", com
`planner opus` em `:79`). Corrigir a nota da instância neste card — deixá-la divergente do template
recém-corrigido recria os "dois discursos" do A3. A **tabela** já está como o dono decidiu: não muda.

### Passos (ordenados; um arquivo por passo — zero edições concorrentes)

1. **`orq/skills/orq/SKILL.md`** (A1 · A9 · A10-parte · dedup) — quatro edições, de cima para baixo:
   a. linha 85 (tabela): remover "relate o achado em uma linha no fim da resposta em curso"; mantém
      gatilho + "nunca corrija" + o ponteiro que já existe para "Decisões que o Manager toma sozinho";
   b. linhas 101-105 (parágrafo ~50%): reduzir a exemplo + ponteiro para o N2 — sem "1× por bloco",
      sem 52/75/90;
   c. linhas 219-224 (N1): gatilho (a) por rótulo de marco (argumento OU derivado da fala); forma do
      relato ganha a precedência do A10 ("resposta com contrato de formato → bullet na
      `✅ Verificação` do próprio contrato; senão, uma linha no fim");
   d. linhas 225-236 (N2): título "propõe, nunca insiste"; teto+exceção substituídos pela cláusula
      única (redação na Solução), preservando intactos a distinção política/momento e os lugares de
      registro (Dispensadas vs. thread/board).
2. **`orq/commands/revisar.md`** (A2): linhas 96-98 viram a regra canônica do painel mínimo —
   propriedade real, as 3 saídas, precedência LGPD citando o passo 1 do próprio arquivo.
3. **`orq/commands/implement-next.md`** (A2): linhas 32-35 → enunciado simples ("card pequeno e de
   baixo risco: `--rapido`") + meia-linha "se o reviewer interno estiver rebaixado, o `/orq:revisar`
   decide o painel mínimo — regra lá". Sem condição própria, sem nome de perfil.
4. **`README.md`** (A2): linhas 236-238 → mesmo tratamento do passo 3.
5. **`orq/commands/elenco.md`** (A2-parte · A4 · A5 · A6 · A7 · A8) — um passo, edições de cima
   para baixo:
   a. `:31-33` (passo 3 do ajuste): regra do A4 — registrar sempre que divergir do preset ativo
      (inclusive `padrao`); devolver ao preset remove o desvio; sem seção Perfis, registra igual;
      formato = "o da linha do template";
   b. bloco `perfil <nome>`: **passo 0 novo** (A8 — semear: `padrao` da tabela ativa sem `manager`,
      `economia` da fábrica; avisar antes de aplicar); passo 2 (`:45-50`) ganha a auto-cura do
      heading (A5-migração) e "formato da linha do template" (A7); passo 3 ganha a linha "desvio
      anterior descartado" (A4-complemento);
   c. template (`:63-122`): heading `## Papéis (…)` (A5); linha "Perfil ativo" canônica com data e
      estado de desvio (A7); preset `padrao` com revisores literais e `--rapido` sem condição
      própria (A6, A2); preset `economia` com a tabela decidida pelo dono — `planner opus` ("um erro
      de plano custa a implementação inteira — não rebaixa"), `implementer sonnet`,
      `reviewer sonnet`, docs/scout conforme decisão nº 1 —, revisores literais (A6) e a **nota
      reescrita**: sem "plano mais raso", sem "alto risco não se planeja"; o que se perde de
      verdade: reconciliação interna mais fraca, desempate deslocado ao painel externo, mais peso em
      revisor sem sandbox.
6. **`orq/commands/stack.md`** (A3): linha 146 → "avise que deve **presumir restart** para aplicar
   (efeito do `/reload-plugins` sobre instalação nova: não testado)". **Linhas 68 e 73 não mudam**
   (revisão da 0.14.0: "regra operacional correta" — fechar card exige restart).
7. **`orq/stack.md`** (A3): linhas 218-221 → vocabulário de evidência ("presuma restart — não
   testado por componente; o aviso do `--help` é conservador: para skill já foi desmentido 1×"),
   mantendo "Instalado ≠ funcionando". Sem ponteiro a arquivo fora de `orq/`.
8. **`orq/commands/checkpoint.md`** (A10): na descrição da `✅ Verificação` (~`:140`), meia-linha
   autorizando o bullet do achado do `wiki-lint` (N1) quando ele tiver rodado.
9. **`orq/commands/ajuda.md`** (A11): linha 38 → "cobrir as situações reais da tabela acima".
10. **`memory/wiki/_elenco.md`** (instância): reescrever a nota "O que se perde" (`:89-97`) —
    remover os dois enunciados falsos, manter os três bullets ainda verdadeiros (sandbox/Kimi,
    read-only, manager). Se a decisão nº 1 for `sonnet`, ajustar docs/scout aqui também.
11. **Release 0.17.0**: bump nos **quatro** lugares (`orq/.claude-plugin/plugin.json`, README
    Status, `memory/MEMORY.md`, `.claude-plugin/marketplace.json`) → `claude plugin validate ./orq
    --strict` → `python3 orq/scripts/lint-coerencia.py .` → `marketplace update` + `plugin update` →
    **restart** → `diff -rq` do cache **vazio**.
12. **Painel de review sobre o diff da correção** (o precedente torna este passo não-opcional):
    `/orq:revisar` com os três revisores, briefing incluindo: *"neste projeto, três releases
    seguidas, o defeito nasceu da correção — procure a contradição NOVA que este diff planta, não a
    antiga que ele remove"*. Só depois o card vai a VALIDATE.

### Critérios de aceite

**Mecânicos (neste repo, antes do commit):**
- `validate --strict` e `lint-coerencia.py` limpos;
- `grep -rn "Teto:" orq/` → **1** ocorrência (N2); `grep -rn "52%" orq/skills/` → **1** (dentro do N2);
- nenhuma condição de painel atada a nome de perfil em `revisar.md`/`implement-next.md`/`README.md`
  (`grep` por "perfil \`economia\`" nesses três → só ponteiros neutros, se tanto);
- `grep -n "é preciso reiniciar" orq/commands/stack.md orq/stack.md` → vazio; `:68`/`:73` intactos;
- template do elenco: heading `## Papéis` presente; **zero** ponteiros nos presets ("estado
  registrado acima"/"continuam ativos" ausentes); "Perfil ativo" com data e desvio;
- `ajuda.md` sem numeral de situações;
- nenhuma referência nova, em `orq/`, a arquivo que não vai no cache (README, `memory/`).

**Comportamentais (neste repo, só após release completo + restart + diff vazio):**
- "contexto subiu, recusei aos 60%… agora 85%" → repropõe **uma** vez, registra na thread;
- "terminamos, fechamos a 0.17.0" (fala natural, sem comando) → N1 dispara e o achado do lint
  aparece **dentro** da `✅ Verificação` do relatório de checkpoint.

**Fora deste repo — A5, A8 e A2-solo são invisíveis aqui (o repo é imune por acidente):** num
projeto de teste descartável, com o plugin 0.17.0 instalado:
- `/orq:init` → `_elenco.md` nasce com `## Papéis`, "Perfil ativo" datado, presets literais; depois
  "tô com pouco crédito" → a tabela **ativa** muda (os presets não), aviso do que se perde sem
  "plano mais raso";
- simular pré-0.16.0 (apagar a seção Perfis) → `perfil economia` → semeia + avisa + aplica; e
  `perfil padrao` em seguida devolve **o time que a tabela ativa tinha antes** (não a fábrica);
- `_elenco.md` com `codex off` e `kimi-k2 inativo` + reviewer rebaixado → review de card pequeno →
  roda só o interno **e** anuncia painel mínimo (não trava, não exige revisor inexistente).

### Decisões do dono

1. **docs/scout no preset `economia`: `haiku` (como está) ou `sonnet`?**
   Pergunta exata: *"No perfil economia, docs e scout ficam em haiku ou sobem para sonnet?"*
   **Recomendação: manter `haiku`** — são papéis de leitura/escrita objetiva, o perfil existe para
   economizar e erro ali é barato (o review pega). Trade-off: documentação e varredura um degrau
   mais pobres enquanto o perfil estiver ativo.
2. **Semeadura do A8: o preset `padrao` semeado nasce da tabela ativa atual ou da fábrica?**
   Pergunta exata: *"Num projeto antigo sem seção Perfis, o preset padrao que o comando cria deve
   copiar o time que o projeto já usa (recomendado) ou o time de fábrica do template?"*
   **Recomendação: da tabela ativa** — ela *é* o titular do projeto; a fábrica faria
   `perfil padrao` devolver um time que o projeto nunca teve, em silêncio. Trade-off: se a ativa
   estiver "errada" naquele momento, o erro é promovido a titular — mas já era o time em uso.

(A escolha (a)×(b) do A1 é do plano, não do dono — está feita e justificada na Solução; o gate
aprova o plano inteiro.)

### Escopo — o que fica de fora

- `README.md:231-234` (Kimi "não instalado") → `T-028`. **Atenção à colisão:** o `T-028` edita
  linhas adjacentes às do passo 4 — ele deve rebasear **depois** do T-030, nunca em paralelo.
- `orq/commands/init.md:161` (caminho relativo) → `T-029`.
- CLI direta × subagente do Codex em `revisar.md` → `T-027`; o passo 2 não toca nada além das
  linhas do A2.
- Guardas novos no lint (ex.: detectar contador numérico em prosa, regra duplicada) → só se o dono
  pedir; viraria card novo.
- A sonda do `/reload-plugins` (README `:408-410`) segue pendente — não é deste card.

### Riscos — o padrão da casa é a correção parir o próximo defeito

1. **A2 × LGPD**: a regra nova ("rebaixado → inclua externo") e a regra do passo 1 de `revisar.md`
   ("dado sensível → `--rapido` para excluir externos") vivem no mesmo arquivo. Sem a precedência
   explícita, é a exceção-inalcançável da 0.15.0 de novo. O review do passo 12 deve atacar
   exatamente esse parágrafo.
2. **A3 × cache**: um ponteiro para o README seria o novo `T-029` (arquivo que não existe no plugin
   instalado). Por isso o inline. O review confere que **nenhum** passo plantou referência a arquivo
   fora de `orq/`.
3. **A2, "mais fraco que o preset `padrao`"** pressupõe ordem entre modelos; `fable`/`inherit` não
   têm ordem óbvia. O default "na dúvida, não rebaixado" falha na direção do comportamento antigo —
   conferir que a redação final o preserva.
4. **A5-migração**: a auto-cura muda como o comando localiza a tabela ativa. Mal redigida, elege a
   tabela errada num arquivo fora do padrão. A regra é "heading primeiro; primeira tabela **só**
   como fallback de arquivo antigo, regravando com o heading".
5. **A8**: semear preset em arquivo velho é a única mudança deste card que **escreve** estrutura
   nova em projeto do dono — o aviso antes de aplicar é parte da correção, não cortesia.
6. **A1**: risco residual de a cláusula única ser lida como "estado novo = teto novo para qualquer
   assunto". A redação amarra "por assunto **e** por estado da condição" — o review lê como modelo
   hostil.
7. **Bump/quatro lugares**: o lint guarda, mas só se rodar — os dois comandos vêm **antes** do
   commit, sempre.

### Suposições que não deu para confirmar daqui

- Que o Manager localiza a tabela ativa pelo heading de forma estável após a mudança — só o teste
  comportamental fora do repo confirma.
- Que derivar o rótulo de marco da fala natural (A9) dispara de forma consistente — hoje o gatilho
  (a) dispara 0% das vezes pela rota natural; a correção o torna alcançável, mas a taxa real só
  aparece no uso.
- A ordem de força haiku < sonnet < opus é convenção; nenhum lugar do plugin a declara — ela passa a
  existir na regra do A2 e vale só ali.

---

## 🔍 REVIEW DA CORREÇÃO — rodada 1, painel de três, 2026-08-02

**REPROVADO pelos três** (Opus interno · Codex `gpt-5.6-sol` · Kimi K3 em worktree). Briefing:
*"este diff É uma correção; procure a contradição NOVA que ele planta, não a antiga que ele remove"*.
**A taxa histórica se manteve: quarta correção seguida a plantar defeito.**

Alvo: `git diff` não commitado, 14 arquivos, +109/−71, bump 0.17.0.

### C1 — 🔴 A cláusula central da release se contradiz por dentro *(Kimi; verificado)*

`orq/skills/orq/SKILL.md:233`. A cláusula única do N2 — **a peça que este card inteiro existe para
consertar** — diz que recusa de política *"congela o assunto **até o fim do bloco**: registra no
padrão 'Dispensadas' … e não repropõe, ponto final"*. Quatro linhas abaixo, a própria cláusula
afirma que em "Dispensadas" *"a semântica é **não reproponha nunca**"*.

**"Até o fim do bloco" é NOVO neste diff** — o texto anterior dizia só "não repropõe, ponto final".
**Cenário:** dono dispensa o Serena em 02/08 ("pare de me oferecer") → registrado em Dispensadas.
Em 03/08, sessão nova = bloco novo → quem aplicar a vigência literal repropõe a ferramenta,
violando o registro permanente e o "ponto final" da mesma frase.

**Correção:** remover "até o fim do bloco" da sentença da recusa de política. Recusa de política é
permanente; só a de momento é que tem vigência de bloco.

### C2 — 🔴 O A2 sobreviveu no arquivo vivo, e o diff plantou uma afirmação falsa sobre isso *(os três)*

`memory/wiki/_elenco.md:85-87` e `:113-114` seguem com a condição do `--rapido` auto-contida e presa
ao **nome** do perfil. **Os três refutaram a hipótese do implementer** ("é dado, não consumidor")
com o mesmo argumento: `revisar.md:48` manda ler esse arquivo antes de montar o painel, e
`elenco.md:61` manda **exibir a nota do preset ao dono em toda troca** — é texto normativo consumido.

**O agravante é do diff, não pré-existente:** `revisar.md:108-109` e `README.md:366` agora **afirmam
como fato** que o preset `economia` *"não re-enuncia a condição, só aponta"* — falso para o arquivo
vivo deste repo.

**Interação achada pelo Codex e pelo Kimi, e é a pior:** em `economia` com diff sensível,
`_elenco.md:85-87` manda **somar um externo** enquanto `revisar.md:104` **proíbe qualquer externo por
LGPD**. Duas instruções vivas e contraditórias no caso em que errar custa mais caro.

**Nada migra isso:** o passo 2 do `elenco.md` reescreve a *tabela ativa*, nunca as notas dos presets,
e o passo 0 só semeia seção **ausente**. A correção do template é **inerte em toda instalação
existente** — e este repo é a prova.

**Correção:** trocar as duas passagens por ponteiro ("quem decide o painel mínimo é o
`/orq:revisar`"), espelhando o template já corrigido, **no mesmo commit**.

### C3 — 🔴 A regra LGPD virou item de lista e perdeu a precedência *(Opus)*

`orq/commands/revisar.md:100-106`. As saídas 1 e 2 são exclusivas entre si (há externo / não há);
a 3 (LGPD) é **ortogonal** e casa junto com a 1. Leitura natural de enumeração: a primeira que casar.

**Cenário:** `economia` + Codex ativo + diff com dado sensível + `--rapido` → a saída 1 casa primeiro
→ *"inclui um externo"* → **briefing sai para a OpenAI**. O "vence tudo" está dentro do item que
precisa vencer, depois dos que ele deveria vetar.

**Correção:** promover a dado-sensível a **guarda antes da lista**, não item dela.

### C4 — 🔴 A correção do A6 desativa o Kimi no perfil que existe para usá-lo *(Opus)*

`orq/commands/elenco.md:56` × `:119-120`. Trocar o ponteiro por lista literal fez os presets
declararem `kimi-k2 | inativo` (herdado do template de fábrica), e o passo 2 manda *"aplique o estado
que o preset declarar"*.

**Cenário:** dono instala o Kimi e marca ativo → *"tô com pouco crédito"* → `perfil economia`
**desativa o Kimi em silêncio**, no perfil cuja razão de existir é *"uso mais o Codex e o Kimi"*.
`perfil padrao` **não devolve** — o `padrao` também diz `inativo`. Perda permanente, a mesma contra a
qual o passo 2 protege a linha `manager`.

**Agravante:** o preset diz `kimi-k2`, a tabela real diz `kimi` → ou no-op mudo, ou segunda linha
contraditória.

**Correção:** preset declara estado de revisor **só quando o projeto o registrou**, ou o passo 2
ganha a mesma cláusula de preservação da linha `manager`.

### C5 — 🔴 O A10 virou deadlock no checkpoint *(Opus)*

`orq/commands/checkpoint.md:142-143` × `:88` × `:151-156`. O achado do `wiki-lint` foi para dentro da
seção que **autoriza o `/clear`**. O contrato diz: falhou um sinal → título vira
`⚠️ Verificação falhou` + *"NÃO afirmo que é seguro limpar"* + *"corrija e verifique de novo"*.
E o N1 diz *"nunca corrige nada, nem trivial"*.

**Cenário:** gatilho (b) do N1 é literalmente "um checkpoint flagra contradição" → o achado entra na
seção → o contrato nega o `/clear` por uma inconsistência de wiki que ninguém pode consertar.
Antes do diff o achado saía **fora** do contrato e não tocava a autorização.

**Correção:** dizer que achado de `wiki-lint` **não** é sinal de verificação falhada, ou devolvê-lo
para fora da seção.

### C6 — 🟠 Ajuste em arquivo pré-0.16.0 fabrica baseline *(os três)*

`orq/commands/elenco.md:31-36`. O passo 3 manda registrar desvio comparando com "o preset ativo",
e o fallback diz *"sem seção Perfis, registre do mesmo jeito"* — mas nesse arquivo **não existe nem
a seção Perfis nem a linha "Perfil ativo"**, e o passo 0 de semeadura só existe no ramo `perfil`.

**O ângulo do Codex é o pior:** baixar `reviewer opus → sonnet` num projeto legado e depois pedir
`perfil economia` faz a semeadura consagrar `padrao.reviewer = sonnet` — **o desvio vira baseline e
o Opus não volta nunca mais**. E o teste de "rebaixado" do `revisar.md` passa a comparar sonnet com
sonnet, liberando `--rapido` solo com reviewer fraco: exatamente o caso que o A2 existe para pegar.

**Correção:** semear a seção Perfis **antes de qualquer ajuste individual** em arquivo legado, não
só no ramo `perfil`.

### C7 — 🟠 `inherit` declarado "não rebaixado" *(Opus + Codex)*

`orq/commands/revisar.md:96`. A regra promete condicionar à **propriedade real** e então trata
`inherit` e "sem seção Perfis" como não rebaixados. `inherit` é justamente o valor em que o rótulo
esconde o modelo: com reviewer `inherit` e o dono seguindo a sugestão de baixar o `/model` da sessão
(que o passo 5 do próprio comando faz), o reviewer real é o mais fraco do projeto e a regra declara
"não rebaixado" → `--rapido` solo, sem aviso.

### C8 — 🟠 Resíduos do A1 e da nota antiga *(Opus)*

- `orq/skills/orq/SKILL.md:207` — a linha-resumo dos níveis ainda diz *"propõe **1×** o resto"*,
  terceiro enunciado do teto, com redação que **contradiz o rearme** da cláusula nova. O guarda
  mecânico (`grep "Teto:"`) não pegou porque a redação é outra.
- `README.md:176` — ainda promete *"plano mais raso"* no `economia`, enunciado que o diff removeu do
  `_elenco.md` e que é falso com `planner: opus`.
- `README.md:368` — anuncia "migração automática de arquivo pré-0.16.0", promessa mais larga que a
  implementação (só o ramo `perfil` migra, e nenhum ramo migra notas de preset).
- `orq/commands/elenco.md:126` — o template genérico atribui `planner: opus` a uma *"escolha do
  dono"*; num projeto novo isso credita ao dono daquele projeto uma decisão que ele nunca tomou.
- `orq/commands/revisar.md:3` — o `argument-hint` ainda promete que `--rapido` usa *"só um revisor"*,
  enquanto a regra nova pode acionar dois *(Codex)*.

### Fora do escopo desta rodada

- `orq/stack.md:105` — caminho relativo cru `orq/scripts/sm-search.py`. **Pré-existente**, é o `T-029`.
- `README.md:232-234` — "Kimi K2 não está instalado". É o `T-028` — mas note que **é a origem** do
  `kimi-k2 | inativo` do template que produziu o C4.

### Evidência de método desta rodada

- **O Kimi achou sozinho o defeito mais grave** (C1), pela segunda rodada seguida — e é o defeito
  dentro da própria solução central. Sem ele no painel, a release teria saído com a cláusula
  contraditória.
- O worktree descartável funcionou de novo: `git status` sem nada além do patch.
- **O guarda mecânico do A1 passou e mesmo assim o A1 sobreviveu** (C8, `SKILL.md:207`): o `grep`
  procurava a string `"Teto:"`, e o resíduo estava com outra redação. **Guarda mecânico prova
  ausência da string, não ausência da regra.**

## 🔍 REVIEW DA CORREÇÃO — rodada 2, painel de três, 2026-08-02

**Opus REPROVADO · Codex REPROVADO · Kimi APROVADO_COM_RESSALVAS (zero bloqueadores).**
Convergência forte: **nenhum achado catastrófico, e todos os sete têm correção de UMA FRASE.**
Comparação com a rodada 1 (cinco bloqueadores, incluindo porta de LGPD e perda permanente de
estado): a correção convergiu.

**Os três auditaram os C1–C8 e confirmaram que foram aplicados corretamente**, incluindo as três
decisões próprias do implementer (C4 coerente na ida e volta de perfil · C6 executável a partir do
passo 3 · C2 confirmado em substância).

### D1 — 🔴 A unidade do teto do N2 ficou enunciada duas vezes, com resultados opostos *(Opus; verificado)*

`orq/skills/orq/SKILL.md:212` × `:232-238`. A cláusula única passou a contar "por assunto **e por
estado da condição**" — sem bloco. Mas a linha 212 continua: *"**Bloco de trabalho** (a unidade do
teto do N2)"*. O texto anterior casava com ela ("Teto: 1 proposta por bloco de trabalho"); o diff
tirou "por bloco" da cláusula e deixou a linha 212 intacta.

**Cenário:** dono recusa `/orq:stack` com "agora não" no bloco 1. Bloco 2, mesmo atrito 2×. Pela
linha 212, o teto rearmou → propõe. Pela cláusula (*"o teto proíbe insistir sem a condição ter
piorado"*), o atrito não piorou, só se repetiu → **nunca mais propõe** — a recusa *de momento* passa
a se comportar como *de política*, que é o colapso que a cláusula existe para impedir.

**Correção:** ou a cláusula diz "…por assunto, por estado da condição **e por bloco**", ou a linha
212 perde o "(a unidade do teto do N2)". **Uma das duas, não as duas.**

### D2 — 🔴 Desvio de revisor externo: passo 3 × passo 2 se cruzaram *(Opus + Codex)*

`orq/commands/elenco.md:31-39` × `:63-66`. O passo 3 manda registrar desvio para **qualquer papel
validado no passo 1** — e o passo 1 aceita revisor externo. Mas o passo 2 (a correção do C4) declara
que estado de revisor externo **não é preset** e que a linha do preset é "só informativa".

**Cenário:** `padrao` ativo, dono diz *"tira o GPT da revisão"* → `codex off`. Leitura A: grava
`padrao · desvio: codex→off`; depois `perfil economia` zera desvios e **anuncia "o desvio foi
descartado" enquanto preserva o Codex desligado** — o dono é informado de uma reversão que não
houve. Leitura B: nada a registrar → a linha fica "sem desvio" com o Codex fora, que é o silêncio
que o A4 existia para eliminar.

**Correção:** uma frase no passo 3 — *"desvio vale só para papéis da tabela `## Papéis`; estado de
revisor externo não é desvio e nenhum perfil o toca"*.

### D3 — 🟠 O parêntese do passo 3 perde o "sem a linha `manager`" *(os TRÊS)*

`orq/commands/elenco.md:33-35`. O passo 3 aponta para o passo 0 ("pela mesma regra") **e
parafraseia** — a paráfrase omite o *"sem a linha `manager`"* que o passo 0 (`:50-51`) carrega.

**Cenário:** projeto legado → `reviewer sonnet` → o agente segue o texto mais próximo e semeia
`padrao` com **6 linhas** → o passo 2 afirma "os presets têm 5 linhas (sem `manager`)", falso para
aquele arquivo, e a instrução "preserve o `manager`" colide com um preset que o declara.

⚠️ **Este achado é o mais instrutivo da rodada.** A correção do C6 seguiu o princípio do card
("uma regra, um lugar; os demais apontam") — e mesmo assim reproduziu o defeito, porque **apontou e
parafraseou**. **Resumir já é reenunciar: a paráfrase que acompanha um ponteiro é uma segunda fonte
da verdade.** Isso vale para o plugin inteiro, não só para este passo.

### D4 — 🟠 A semeadura não grava a linha "Perfil ativo" que os passos seguintes pressupõem *(Opus + Kimi)*

`orq/commands/elenco.md:49-53` × `:38` e `:59`. O passo 0 semeia "a seção Perfis com os dois
presets" — mas arquivo pré-0.16.0 não tem **nem** a linha "Perfil ativo", e os passos seguintes
mandam "atualize a linha Perfil ativo" / "registre o desvio na linha Perfil ativo".

**Cenário:** `_elenco.md` da 0.15.0 → executor literal não tem o que atualizar → pula o registro
(perde data e estado ativo) ou cria a linha em posição arbitrária. No ramo `perfil` o passo 2
resolve; **no ramo do ajuste, não há passo equivalente** — o A4 seguiria vivo em todo projeto legado,
que é o buraco que o C6 mandou fechar.

**Correção:** o passo 0 grava também a linha "Perfil ativo", no formato do template.

### D5 — 🟠 A instância divergiu do template de novo, em dois pontos *(Opus)*

A mecânica do C2 reaparecendo noutros parágrafos do mesmo arquivo:
- `memory/wiki/_elenco.md:9-12` — a nota local ainda diz que ajuste papel a papel é coisa *"depois
  da troca"*, com exemplo só em `economia`, enquanto o template corrigido enfatiza *"inclusive com
  `padrao` ativo"*. **Este repo está com `padrao` ativo desde 2026-07-28 — é o caso exato do A4.**
- `memory/wiki/_elenco.md:69` e `:85` — as linhas de revisores externos dos presets não receberam a
  qualificação que o template ganhou no C4 ("estado de fábrica, informativo: o perfil não aplica
  isto"). Hoje coincidem com o estado real, então não mordem; se o dono desativar o Kimi, o anúncio
  da troca promete um painel que não existe.

### D6 — 🟠 `checkpoint.md:142` é mais largo que a regra que o produz *(Kimi)*

*"Rodou o `wiki-lint` por iniciativa própria (N1) **nesta sessão**?"* vs `SKILL.md:221-224`
(*"a resposta **em curso**"*). **Cenário:** sessão com dois checkpoints; o achado do primeiro é
repetido no segundo como evidência de uma verificação que o segundo não rodou.
**Correção:** "nesta sessão" → "neste checkpoint".

### D7 — 🟠 O preset `economia` promete um desempate impossível em solo-Claude *(Codex)*

`orq/commands/elenco.md:135`. A nota afirma que o desempate passa ao painel externo — mas o C4 agora
**preserva** revisores inativos. Num projeto sem externo ativo, ativar `economia` rebaixa o reviewer
interno e anuncia uma garantia que não existe. **Correção:** condicionar a nota à existência de
externo ativo.

### ⚠️ Achado de MÉTODO — o A1 escorregou TRÊS vezes, sempre pela mesma mecânica

| Rodada | Onde o resíduo estava | Redação |
|---|---|---|
| Review 1 | `SKILL.md:101-105` | "proponha 1× por bloco" |
| Review 2 (C8) | `SKILL.md:207` | "propõe **1×** o resto" |
| Review 3 (D1) | `SKILL.md:212` | "(a unidade do teto do N2)" |

**Sempre a mesma mecânica: a regra é apagada de um lugar e continua viva em outro, com redação
diferente da que se procurou** — por isso o `grep` nunca pega.

**A hipótese que isso sugere, e que o próximo painel deveria testar:** a regra do teto do N2 tem
**três dimensões** (assunto · estado da condição · bloco de trabalho), e cada tentativa de enunciá-la
inteira num lugar deixa uma dimensão órfã enunciada em outro parágrafo. Se a rodada 3 escorregar de
novo no mesmo ponto, **o problema não é redação — é que essa regra pode ser complexa demais para o
formato**, e a saída passa a ser simplificá-la (menos dimensões), não reescrevê-la.

## 🗄️ RETOMAR AQUI — SUPERADO (ver o do fim do arquivo)

> Congelado — mantido como registro do que se sabia neste ponto. **O RETOMAR AQUI vivo é o último do arquivo.**

**Card criado em 2026-08-02, aprovado pelo dono para entrar no ciclo ("sim"). Plano escrito pelo
Planner (`fable`) no mesmo dia. As duas decisões pendentes foram respondidas. Nada foi implementado
— o card está PARADO NO GATE, esperando o "pode implementar" do dono.**

## Decisões fechadas — não repergunte nenhuma delas

1. **Composição do `economia`** (dono, 2026-08-02, também gravada no card `T-020`): *"não usar o
   Fable · usar somente o Opus · talvez direcionar tarefas menores para o Sonnet · usar os outros
   modelos como revisor, que são o ChatGPT e o Kimi"*. Isso **confirma** `planner: opus` e move o
   defeito para a **nota** do preset — *"plano mais raso"* é falso, e *"alto risco não se planeja em
   economia"* perde a premissa que a sustentava.
2. **`docs`/`scout` no `economia`: ficam em `haiku`** (dono, 2026-08-02, seguindo a recomendação do
   plano). Consequência prática: **o passo 10 não mexe em `docs`/`scout`**, e o passo 5c grava
   `haiku` nos dois.
3. **Semeadura do A8: o preset `padrao` nasce da TABELA ATIVA do projeto**, não da fábrica (dono,
   2026-08-02, seguindo a recomendação). A tabela ativa *é* o titular daquele projeto; a fábrica
   faria `perfil padrao` devolver, em silêncio, um time que o projeto nunca usou.
4. **A1 fica com a saída (a) reformulada** — decisão do plano, não do dono, justificada na seção
   Solução. A (b) foi rejeitada porque amputaria o rearme 52→75→90%, que o dono quer e que pré-data
   os níveis: seria a 4ª rodada por outra porta.

## ✅ VERIFICAÇÃO FINAL — 2026-08-02: os TRÊS aprovaram, zero bloqueadores

| Revisor | Rodada 1 | Rodada 2 | Final |
|---|---|---|---|
| Opus (interno) | REPROVADO (4 bloq.) | REPROVADO (2 bloq.) | **APROVADO_COM_RESSALVAS** |
| Codex `gpt-5.6-sol` | REPROVADO (5 bloq.) | REPROVADO (1 bloq.) | **APROVADO_COM_RESSALVAS** |
| Kimi K3 (worktree) | REPROVADO (2 bloq.) | APROVADO_COM_RESSALVAS | **APROVADO_COM_RESSALVAS** |

**Primeiro parecer sem bloqueador em todo o ciclo — e nas últimas quatro releases do projeto.**

Gates verdes (`validate` passed · lint 19 nomes) · bump 0.17.0 nos quatro lugares, conferido pelo
revisor um a um · `grep` das **três** redações do resíduo do A1 (`"unidade do teto"` ·
`"por bloco de trabalho"` · `"1×"`) voltou **vazio**.

**Auditado e confirmado correto pelo revisor interno:** D1 (teto enunciado uma única vez; "Bloco de
trabalho" **não** ficou órfão — segue sendo a unidade do contador "atrito 2×") · D3/D7 (nenhuma
paráfrase nova; os dois trechos do D7 coerentes entre si e com a saída 2 do `revisar.md`) · D6 (os
achados do `wiki-lint` **não** intersectam os sinais do passo 5 do checkpoint, então blindá-los não
suprime falha real) · C1–C8 e A3.

### As quatro ressalvas — nenhuma corrigida, o teto de rodadas acabou

**R1 — 🟡 DECISÃO DO DONO, não defeito.** `orq/skills/orq/SKILL.md:231-237`. O teto perdeu a
dimensão de bloco, e o único mecanismo de rearme virou "piora material da condição" — que só é
definível para **condição escalar**. Para o gatilho `/orq:stack` a condição é **booleana por bloco**
("mesmo atrito 2×", zerada a cada checkpoint): ela nunca *piora*, só se repete.

**Cenário:** dono recusa `/orq:stack` com "agora não" no bloco 1 → bloco 5, mesmo atrito 2× → o
Manager vê que a condição não piorou e **não repropõe nunca mais**; a recusa *de momento* colapsa em
*de política*. Para o gatilho do checkpoint (52→75→90%) a regra funciona.

⚠️ **Observação honesta do revisor interno, e ela importa:** o implementer escolheu **a saída (b)
prescrita pelo próprio painel na rodada 2** — *"ou a linha 212 perde o '(a unidade do teto do N2)'"*.
**Não é deslize de implementação: é a consequência que aquela saída carregava.** O painel ofereceu
duas saídas e nenhuma delas era completa.

O Kimi chegou ao mesmo ponto por outro caminho e registrou o argumento que decide o peso disso:
**as duas leituras falham em direção segura** — sugestão a menos, nunca insistência a mais.

**Isto confirma empiricamente a hipótese registrada no achado de método:** a regra do teto tem três
dimensões e **não cabe num enunciado só**. Quatro tentativas, três resíduos, e agora um buraco na
dimensão que foi removida. **A saída, se o dono quiser fechar, é simplificar a regra — não
reescrevê-la pela quinta vez.** Uma frase possível: *"condição que zera e rearma conta como estado
novo"*.

**R2 — 🟡 uma frase, impacto só neste repo.** `memory/wiki/_elenco.md:92-93` (Opus + Codex): a nota
"O que se perde" da **instância** não recebeu a condicional que o D7 pôs no template — continua
afirmando incondicionalmente que "o desempate desloca para o painel externo". Se o dono desativar
Codex e Kimi e ativar `economia`, o anúncio promete um desempate que não existe. **Este arquivo não
vai para o cache do plugin** — não alcança outros projetos.

**R3 — 🟡 uma frase.** `orq/commands/elenco.md:31-40`: a auto-cura é **assimétrica** — o ramo
`perfil <nome>` acrescenta o heading `## Papéis` em arquivo legado, o ramo "ajustar" semeia só a
seção Perfis + linha "Perfil ativo". Resultado: arquivo meio-migrado, e a última frase do passo 3
("desvio vale só para papéis da tabela `## Papéis`") referencia um heading que aquele arquivo não
tem. Não trava — só existe uma tabela de papéis.

**R4 — 🟡 custo prático ~zero.** `orq/commands/revisar.md:112-113` cita "README" na lista de
consumidores; o README não vai para o cache, então em outro projeto a palavra resolve para o README
**daquele** projeto. Nenhuma ação depende dessa frase.

### Evidência de método do ciclo inteiro

- **Três painéis, nove pareceres.** A convergência foi real: 5 bloqueadores graves → 2 → **0**.
- **O Kimi achou sozinho o defeito mais grave em duas rodadas seguidas** (a duplicação em
  `SKILL.md:101-105`, e a contradição interna da cláusula em `:233`). Sem ele, a release teria saído
  com a cláusula central contraditória. **O dono estava certo em exigir que ele revisasse tudo.**
- **Worktree descartável: três execuções, `git status` limpo nas três.** A opção (b) do `T-019`
  deixou de ser teoria.
- **Guarda mecânico prova ausência de string, não de regra.** O `grep "Teto:"` passou enquanto a
  regra sobrevivia com outra redação — duas vezes.
- **O painel prescreveu uma saída incompleta (R1).** Revisor propor "correção mínima" não garante
  que a correção seja suficiente: a saída (b) resolvia a contradição apontada e abria outro buraco.

## 🗄️ RETOMAR AQUI — SUPERADO (ver o do fim do arquivo)

> Congelado — mantido como registro do que se sabia neste ponto. **O RETOMAR AQUI vivo é o último do arquivo.**

**Estado: a correção está PRONTA e APROVADA pelo painel, no working tree, NÃO COMMITADA.**
Versão 0.17.0 bumpada nos quatro lugares. Nada foi publicado.

### ✅ As quatro ressalvas foram fechadas em 2026-08-02, por decisão do dono

- **R1 — decidido: *"agora não" vale só para aquela sessão*.** A cláusula do N2 ganhou uma **segunda
  via de rearme**, para condição booleana: *"Condição que zera e volta a ocorrer num bloco novo
  também conta como estado novo"*. Entrou **dentro da cláusula única** e em nenhum outro lugar.
- **R2, R3, R4 — decidido: corrigir junto, sem novo painel.** Instância espelhada com o template ·
  auto-cura do heading `## Papéis` também no ramo "ajustar" (por ponteiro, sem paráfrase) ·
  "README" desambiguado para "o README do repositório do plugin".

### ⚠️ A QUINTA reincidência do A1 — pega pelo Manager na releitura, não por gate nem por painel

Ao acrescentar a segunda via de rearme, a **frase de fecho da própria cláusula** ficou desatualizada:
ela dizia *"O que o teto proíbe é insistir **sem a condição ter piorado**"* — mas a via nova rearma
o teto **sem** a condição ter piorado (bloco novo, mesmo atrito). O fecho passaria a proibir
exatamente o que a frase acrescentada autoriza, **dentro do mesmo parágrafo**.

Corrigido pelo Manager para *"insistir **sem estado novo** — as duas vias acima são as únicas que
produzem um"*, usando o termo que a cláusula **já define duas vezes** em vez de repetir uma das
instâncias.

**Por que isso importa mais que a correção em si:** não havia mais painel (decisão do dono), os dois
gates passaram verdes, e o `grep` dos resíduos históricos passou. **O defeito só apareceu porque o
Manager releu o parágrafo inteiro com os próprios olhos**, como havia se comprometido a fazer ao
dispensar o painel. Quinta reincidência, mesma mecânica: a regra mudou num ponto e a frase vizinha,
que a resumia, ficou para trás.

**Regra que sai daqui:** ao acrescentar cláusula a uma regra, **a frase de fecho que a resume é
sempre suspeita** — ela foi escrita para a versão anterior.

## ⏭️ RETOMAR AQUI (atualizado)

**Estado: correção COMPLETA, aprovada pelo painel, com as quatro ressalvas fechadas. Gates verdes.
Tudo no working tree, NÃO COMMITADO.** Versão 0.17.0 bumpada nos quatro lugares.

**Falta, nesta ordem:**

1. **Commit** — só com o ok do dono. Nunca `git push` ou publicar sem ele.
2. **Release na máquina do dono**: `claude plugin marketplace update orquestra` +
   `claude plugin update orq@orquestra` + **reiniciar a sessão** + `diff -rq` do cache contra
   `./orq/` voltando **vazio**.
3. **Teste comportamental do dono, que é o que fecha o card** — conversar em português natural.
   O teste específico desta release: recusar uma sugestão com *"agora não"*, e conferir numa sessão
   seguinte que o assunto **volta uma vez** quando o atrito reaparece (era o que a R1 consertou).

**Este card destrava `T-020`, `T-025` e `T-023`** — os três seguem em VALIDATE e só fecham depois do
release + restart + teste do dono.

**Este card destrava `T-020`, `T-025` e `T-023`** — os três seguem em VALIDATE e só fecham depois do
release + restart + teste do dono.

## Nota herdada do card `T-030` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** Correções do painel de três revisores sobre as releases 0.14.0–0.16.0

✅ **0.17.0 FECHADA, APROVADA PELOS TRÊS E COMMITADA (`10ecef2`, no GitHub) — aguarda seu teste.** As quatro ressalvas foram decididas e aplicadas em 2026-08-02: você escolheu que *"agora não"* vale **só para aquela sessão**, e a cláusula do N2 ganhou a segunda via de rearme. **Como validar (pós-release + restart):** recuse uma sugestão minha de ferramenta com *"agora não"*; numa sessão seguinte, com o mesmo atrito, ela tem que **voltar uma vez** — antes morreria para sempre. ⚠️ **A quinta reincidência do A1 foi pega pelo Manager na releitura manual, com gates verdes e `grep` limpo** — a frase de fecho da cláusula (*"insistir sem a condição ter piorado"*) contradizia a via nova que acabara de ser acrescentada. Virou gotcha: **guarda mecânico prova ausência de string, não de regra**; e **a frase que resume uma regra é sempre suspeita depois de acrescentar cláusula a ela**. **Os três revisores aprovaram com ressalvas, zero bloqueadores** — primeiro parecer sem bloqueador em quatro releases. Convergência: 5 bloqueadores graves → 2 → 0, em três painéis e nove pareceres. Gates verdes, bump 0.17.0 nos quatro lugares, **diff no working tree e NÃO commitado**. Faltam: sua decisão sobre R1, o destino de R2/R3/R4 (três frases, teto de rodadas esgotado), commit+release com seu ok, e o teste comportamental pós-restart. **Achados de método do ciclo, todos na thread:** o Kimi achou sozinho o defeito mais grave em duas rodadas seguidas (sem ele a release sairia com a cláusula central contraditória) · worktree descartável rodou três vezes com `git status` limpo, o que tira a opção (b) do `T-019` do campo teórico · **guarda mecânico prova ausência de string, não de regra** (o `grep` passou duas vezes enquanto a regra sobrevivia com outra redação) · **revisor propor "correção mínima" não garante que ela seja suficiente** — a saída que o painel prescreveu na rodada 2 resolveu a contradição apontada e abriu a R1. As quatro decisões do dono estão fechadas na thread (`docs`/`scout` ficam em `haiku` · o preset `padrao` semeado nasce da **tabela ativa** do projeto, não da fábrica), e estão gravadas na thread; **não repergunte**. Plano de 12 passos na thread, um arquivo por passo, fechando em release 0.17.0 + painel dos três revisores sobre o diff da própria correção. 🔴 **os três revisores reprovaram, independentemente** (Opus interno · Codex `gpt-5.6-sol` read-only · Kimi K3 em worktree descartável), no primeiro painel de três que este projeto rodou de verdade — `memory/wiki/threads/T-030-correcoes-painel.md` com os 11 achados detalhados. **Bloqueia `T-020`, `T-025` e `T-023`**, que estão em VALIDATE e não podem fechar como estão. **O mais grave (A1): o bloqueador B2 que o `T-025` declara resolvido em três rodadas está VIVO** — "teto de 1 proposta por assunto" convive com "recusou aos 52%, repropõe aos 75%, de novo aos 90%", num nível chamado *"propõe uma vez, nunca insiste"*; a correção anterior mudou o teto de "por bloco" para "por assunto", o que resolve assuntos competindo entre si e **não** a contradição. Pior: a mesma regra está **duplicada** em `SKILL.md:101-105`, então corrigir um lugar só deixa o defeito vivo — foi assim que ele chegou à terceira rodada. **A2:** o `--rapido` mudou três consumidores que o `T-020` exigia que não mudassem, e a instrução diz *"só o interno"* e *"mantenha pelo menos um externo"* na mesma frase — que em projeto solo-Claude exige um revisor que não existe. **A3: o `T-023` também não sobreviveu** — `orq/commands/stack.md:146` afirma "é preciso reiniciar" citando o `--help` que a tabela canônica da própria 0.14.0 declara não confiável; ⚠️ a correção é de **vocabulário e procedência**, não de regra: inverter a regra foi o que produziu aquele card duas vezes. **A5 e A8 não aparecem testando aqui** — o template do `_elenco.md` não gera o heading `Papéis` que o próprio comando manda reescrever, e este repo é imune por acidente porque o heading foi escrito à mão; mesma mecânica do `T-029`. **Descartado na reconciliação:** um achado do Codex era artefato do briefing do Manager, que usou numeração errada dos níveis — briefing impreciso gasta rodada do painel. **Método:** a interseção validou 5 achados, mas os **mais graves vieram da divergência** — cada revisor viu algo que os outros dois não viram.

