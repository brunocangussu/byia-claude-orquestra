# Notas herdadas de cards sem thread própria

> **Por que este arquivo existe.** Quando o board ganhou teto por linha (`T-056`), a nota longa de
> cada card precisou de destino. Card com frente própria mandou a nota para a thread dele. Card sem
> thread — quase sempre um `[?]` esperando validação, ou um `[ ]` antigo — mandaria para uma thread
> nova, e **trinta threads de um parágrafo cada** trocariam um inchaço por outro: o `wiki-lint`
> acusaria trinta páginas órfãs, com razão.
>
> Então a nota vem para cá, **íntegra**, sob o ID do card. Nada foi resumido nem descartado. O card
> guarda título, estado, como validar e o ponteiro para a seção correspondente aqui.
>
> **Isto não é uma thread** — não tem "RETOMAR AQUI" e não representa uma frente de trabalho. É
> arquivo de notas, consultável por ID. Card que voltar a ser trabalhado ganha thread de verdade, e
> a nota migra para lá.

## Índice — como achar a nota de um card

**O endereço é o ID**, não a posição: procure a linha exata
`` ## Nota herdada do card `T-NNN` `` neste arquivo. O ID nunca muda, então o endereço
sobrevive a reordenação, a renomeação de título e a novas notas inseridas no meio.

**39 cards aqui:** `T-001` · `T-002` · `T-003` · `T-004` · `T-007` · `T-008` · `T-009` · `T-010` · `T-011` · `T-012` · `T-013` · `T-014` · `T-015` · `T-016` · `T-017` · `T-019` · `T-021` · `T-022` · `T-024` · `T-027` · `T-028` · `T-029` · `T-031` · `T-032` · `T-033` · `T-034` · `T-035` · `T-037` · `T-038` · `T-039` · `T-040` · `T-041` · `T-042` · `T-043` · `T-044` · `T-045` · `T-046` · `T-047` · `T-048`

## Nota herdada do card `T-039` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** Projeto com memória preexistente em OUTRO formato é tratado como virgem

🔴 **flagrado em 2026-08-08** pelo dono, rodando o Codex em `Bruno Vascular - Gestão Dados Marketing`. Aquele projeto tem memória viva **do padrão anterior**: `MEMORY.md` na **raiz** (223 linhas, "Diário Vivo") + `memory/` com 14 itens (snapshots datados, `fixes-history.md`, `gotchas.md`, `README.md`). O que **não** existe é a forma do Orquestra: `memory/MEMORY.md`, `memory/wiki/`, `memory/wiki/KANBAN.md`. **O diagnóstico do Codex estava tecnicamente certo** ("o Orquestra não foi inicializado aqui") — mas ele testou **só os arquivos do Orquestra** e comunicou como ausência de memória, o que fez o dono concluir que o Codex "não detectou" a pasta. **O defeito é nosso:** `init.md` e `stack.md` perguntam "existe `memory/wiki/KANBAN.md`?" e derivam "projeto virgem" do não. Um projeto pode ter memória madura em **outro formato** — e o dono tem vários assim, porque o padrão anterior era `MEMORY.md` na raiz. ⚠️ **CORREÇÃO do Manager (2026-08-09) — a afirmação original deste card estava EXAGERADA e foi verificada no arquivo:** o `init.md:174-187` **já protege** este caso — *"Memória (só o que faltar — **nunca sobrescrever o que existe**)"* e *"já existe algo com essa função em OUTRO caminho? → **preserve o conteúdo onde está** e crie `memory/MEMORY.md` como **ponteiro**"*. Ou seja: rodar o init num projeto assim **não destrói nada**. **O defeito real é mais brando e continua valendo:** (a) a **classificação** da FASE 1 pergunta só por `memory/wiki/KANBAN.md` e comunica "não inicializado" de um jeito que soa como "não há memória" — foi o que confundiu o dono com o Codex; (b) o desfecho é um **ponteiro**, não migração: o projeto fica com o índice na raiz misturando os quatro papéis (índice + decisões + linha do tempo + backlog) e **sem páginas de tópico vivas**, que é onde está o valor. **Requisito de origem, não melhoria:** o dono declarou no início do projeto que queria instalar em projetos **já em andamento** e que o init deveria **acrescentar, nunca alterar** — o princípio foi implementado para `CLAUDE.md`/`AGENTS.md` (bloco delimitado, conteúdo externo preservado) e **esquecido onde a destruição é indireta**: memória (aqui) e statusline (o `T-036`, por precedência). É dívida, não feature. **Isso já aconteceu:** em `IVA - App System` convivem `wiki/memory/MEMORY.md` (SPECKIT) e `memory/wiki/KANBAN.md` (Orquestra), e o `AGENTS.md` de lá **abre** apontando para a do SPECKIT, com o bloco do Orquestra 60+ linhas abaixo num arquivo de 345 — quem lê de cima para baixo encontra a memória errada primeiro. **Correção proposta:** a detecção procura **sinais de memória**, não os nossos arquivos (`MEMORY.md` em qualquer nível, `memory/` com conteúdo, `fixes-history.md`, `gotchas.md`, `wiki/`); achando, o init **para e propõe migração** — nunca instala por cima em silêncio. **Segundo achado, mesma origem:** `Bruno Vascular` tem `CLAUDE.md` e **não tem `AGENTS.md`** — o Codex entra ali **sem as instruções do projeto**, só com a skill global. A 0.18.0 exige os dois byte-idênticos, mas isso só vale onde o `init` rodou; **projeto que nunca rodou fica cego no Codex e nada acusa**.

## Nota herdada do card `T-019` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** 🔴 **O Kimi rodou `git checkout -- .` numa tarefa read-only e destruiu o working tree**

2026-07-28, durante a revisão do diff da 0.11.0. Ele restaurou por conta própria (cópia em `/tmp` + hunks do transcript) e **avisou no relatório**, mas a restauração perdeu os marcadores `[~]` dos cards `T-015/016/017` — as edições feitas por script não estavam no transcript para replay. O conteúdo das notas, o `_elenco.md` e a contagem sobreviveram. **O que dói:** `_elenco.md` **já dizia** "o Kimi não tem flag de sandbox — garantia dura só em worktree descartável", e o `revisar.md:87` repete. A instrução existia, estava certa, e não segurou nada — porque instrução não é enforcement. É o argumento do `T-001` provado na prática, contra o próprio repo. **Opções:** (a) `isolation: "worktree"` obrigatório para revisor externo sem sandbox; (b) rodar o Kimi sobre um clone descartável em vez do repo vivo; (c) hook `PreToolUse` negando `git checkout`/`restore`/`reset` — mas o Kimi roda fora do Claude Code, então o hook não o alcança. **(a) e (b) são as únicas que funcionam.** **⚠️ Premissa corrigida em 2026-07-30 (achado do `T-026`, doc oficial do Kimi 0.29.2):** a opção (c) foi descartada aqui com o argumento de que "o Kimi roda fora do Claude Code, então o hook não o alcança" — mas **o Kimi tem hooks próprios**: bloco `[[hooks]]` no `config.toml`, com `PreToolUse` **bloqueável** (exit 2 nega a chamada). Dá para negar `git checkout`/`reset` do lado dele. **Falta verificar** se o hook vale por projeto — a doc só mostra escopo de usuário. **(c) volta à mesa** e deixa de ser "as únicas que funcionam são (a) e (b)". **🟢 EVIDÊNCIA NOVA — a opção (b) foi exercitada de verdade em 2026-08-02:** o dono cobrou que o Kimi revisasse **tudo**, não só o Codex — deixar ele de fora "por segurança" era exclusão, não isolamento, e contrariava o `_elenco.md`, que o marca **ativo**. Rodou-se `git worktree add --detach` num diretório descartável + prompt reforçando "não edite, não rode `git checkout`/`restore`/`reset`". Resultado: parecer completo no formato exigido, com **1 bloqueador e 5 riscos**, e `git status` do worktree **vazio no fim** — nada tocado. Foi o revisor que mais achou coisa nova naquele painel (a duplicação da contradição em `SKILL.md:101-105`, que Opus e Codex não viram). **Isso não prova que o Kimi é seguro** — prova que o worktree torna a pergunta irrelevante, que era o ponto da opção (b). **Padrão adotado na prática desde já:** revisor sem sandbox entra no painel **sempre**, em worktree descartável.

## Nota herdada do card `T-022` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** Relatório final do `/orq:checkpoint` fala com a pessoa errada

🟡 pedido do dono em 2026-07-29, **e o achado principal veio da pergunta dele, não da minha leitura**: ele perguntou se *precisa dizer o que o checkpoint pediu* ao voltar. Não precisa — a frase *"na próxima janela: leia `memory/MEMORY.md` → thread X"* é instrução para o **próximo assistente**, não para o dono, mas o relatório entrega isso a ele como se fosse tarefa. **Defeito de audiência, e é o mais grave**: cria trabalho onde não havia e faz o dono achar que a retomada depende dele decorar uma frase. O que ele quer, tudo confirmado no gate: (1) **efeito no board** — progresso antes/depois, cards que mudaram de estado, cards que nasceram; (2) **bloco separado do que espera decisão dele**, no topo; (3) **auto-verificação antes de afirmar "seguro limpar"** — contagem do parser vs manual, `_schema.md` presente, thread com RETOMAR AQUI escrito (hoje afirma sem checar nada); (4) **o que NÃO foi feito** — pendências, tentado-e-falhou, deixado de fora. **Decisão de tamanho — REVERTIDA no mesmo dia:** ele primeiro escolheu "curto, 3–6 linhas"; a 0.12.0 entregou isso e ele reprovou a leitura (*"textos bem embolados"*). A compressão **era** a causa: teto de 6 linhas força 120 caracteres por linha, e isso é prosa corrida. Otimizou-se "poucas linhas" quando o requisito era "leitura rápida". Na 0.13.0 ele escolheu, comparando mockups, **seções com título e espaçamento** — sem teto de linhas, com teto de densidade (bullet de uma linha). Junto, um defeito pré-existente: `checkpoint.md:19-20` tem o exemplo do card colado no parágrafo seguinte (vem da 0.2.0). **Implementado e revisado em 2026-07-29** (Fable planejou · Sonnet implementou · revisor interno REPROVOU com 3 bloqueadores · todos corrigidos e verificados). **Como validar (pós-release + restart):** trabalhe um bloco e diga *"salva aí"* — o relatório tem que vir em **seções com título** (⏸️ Espera você · 📋 Board · 💾 Gravado · ⛔ Não entrou · ✅ Verificação), com espaçamento entre elas, evidência do parser na Verificação (números, não só ✓), e a última linha dizendo que você não precisa fazer nada. **O formato de 3–6 linhas comprimidas foi REPROVADO pelo dono em 2026-07-29** — ele leu o primeiro relatório real e achou embolado; a compressão era a causa. Não voltar atrás. Depois estrague o board de propósito (`**- [ ]** \`T-900\` teste`) e repita: ele **não** pode afirmar "seguro".

## Nota herdada do card `T-014` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** Roteamento automático pelo ciclo

**a interface natural não funcionava.** Medi 10 frases reais do dono contra os 25 gatilhos da skill: **0 de 10**. Por isso a skill `orq` nunca foi invocada nesta sessão e tudo foi implementado direto, sem plano e sem gate — inclusive a feature do Kimi. Causa raiz: os gatilhos foram escritos imaginando como ele falaria, não observando como fala, e faltava o padrão mais comum (o **pedido de mudança**). Corrigido em dois níveis: `description` reescrita da fala real (**cobertura 0% → 100%**) e seção **ROTEAMENTO AUTOMÁTICO** no topo da skill, com escala por risco (trivial → direto · pequeno → revisor interno · normal → ciclo completo · alto risco → gate extra) e a regra "na dúvida, suba um nível". **Como validar:** numa sessão nova, diga algo como *"queria melhorar X"* e veja se ele **anuncia** que vai planejar antes (em vez de já editar arquivo, ou de perguntar se pode rodar um comando). **✅ TESTE 1 DE 3 PASSOU (2026-07-29, contra a 0.11.0 já ativa na sessão):** o dono disse *"queria melhorar o relatório do checkpoint"* e o comportamento foi anunciar o roteamento, criar o card (`T-022`), **não tocar em arquivo do produto** e parar no gate. **✅ TESTE 2 DE 3 PASSOU (2026-07-29):** o dono disse *"o painel de revisão não está funcionando"* e o comportamento foi invocar a skill **antes de abrir o board**, aplicar o desempate e **criar card (`T-024`) roteando pelo ciclo** — nada de encerrar em "ambiente ok". **✅ TESTE 3 DE 3 — O CONTROLE — PASSOU (2026-07-29):** *"o Kimi sumiu do PATH"* virou **diagnóstico, sem card**, e a checagem não parou no `which`: o binário está em `~/.kimi-code/bin/kimi` (v0.29.2, 152 MB) e o PATH o alcança por symlink em `~/.local/bin/kimi` (mesmo sha256), OAuth renovado no mesmo dia. Ambiente ok, nada criado no board. **Os dois lados do desempate se comportaram diferente, que era exatamente o ponto** — um virou card, o outro não. Os três testes estão cumpridos; dá para fechar se você concordar. **Só o dono pode rodar estes testes** — o Manager sabe o que a instrução manda e acertaria de memória; aqui o viés é explícito, já que a frase do teste está escrita neste próprio card.

## Nota herdada do card `T-016` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** Colisão de roteamento na skill

🔴 regressão do `T-014` (que está em VALIDATE). `SKILL.md:63` roteia *"não funciona"* para o **ciclo**; `SKILL.md:74` roteia *"não está funcionando"* para o **diagnóstico**. Mesma frase, dois destinos, sem desempate. Cenário: *"o painel de revisão não está funcionando"* sobre bug real → roda diagnóstico, responde "ambiente ok", **o bug nunca vira card**. Junto: `SKILL.md:70` ainda descreve o painel como "Claude + Codex" — o Kimi entrou na 0.8.0. **Implementado e revisado em 2026-07-29** (Fable planejou · Sonnet implementou · Claude+Codex+Kimi revisaram · 7 achados aplicados). **Como validar (pós-release + restart):** diga *"o painel de revisão não está funcionando"* — tem que **criar card e planejar**, não encerrar em "ambiente ok". Depois diga *"o Kimi sumiu do PATH"* — tem que ser diagnóstico, sem card. O segundo é o controle: se os dois virarem card, o desempate ficou frouxo. **✅ TESTE 1 DE 3 PASSOU (2026-07-29, contra a 0.11.0 já ativa na sessão):** o dono disse *"queria melhorar o relatório do checkpoint"* e o comportamento foi anunciar o roteamento, criar o card (`T-022`), **não tocar em arquivo do produto** e parar no gate. **✅ TESTE 2 DE 3 PASSOU (2026-07-29):** o dono disse *"o painel de revisão não está funcionando"* e o comportamento foi invocar a skill **antes de abrir o board**, aplicar o desempate e **criar card (`T-024`) roteando pelo ciclo** — nada de encerrar em "ambiente ok". **✅ TESTE 3 DE 3 — O CONTROLE — PASSOU (2026-07-29):** *"o Kimi sumiu do PATH"* virou **diagnóstico, sem card**, e a checagem não parou no `which`: o binário está em `~/.kimi-code/bin/kimi` (v0.29.2, 152 MB) e o PATH o alcança por symlink em `~/.local/bin/kimi` (mesmo sha256), OAuth renovado no mesmo dia. Ambiente ok, nada criado no board. **Os dois lados do desempate se comportaram diferente, que era exatamente o ponto** — um virou card, o outro não. Os três testes estão cumpridos; dá para fechar se você concordar. **Só o dono pode rodar estes testes** — o Manager sabe o que a instrução manda e acertaria de memória; aqui o viés é explícito, já que a frase do teste está escrita neste próprio card.

## Nota herdada do card `T-017` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** Release sem bump deixa o cache stale em silêncio

o cache do plugin é indexado por versão (`cache/<mkt>/<plugin>/<versão>/`), então editar sem bumpar **não muda o que roda**, e `claude plugin list` segue dizendo que está tudo certo. Foi o que aconteceu no `5b75296`. Isso invalida qualquer teste comportamental feito depois de editar sem bumpar — inclusive a validação dos cards em VALIDATE. É processo, não texto. **Achado na revisão do plano (Kimi, verificado):** a versão vive em **quatro** lugares, não três — `.claude-plugin/marketplace.json:12` declara `"version": "0.4.0"`, sete releases atrás, e o lint não confere esse arquivo (só README e MEMORY.md). **Implementado e revisado em 2026-07-29** (Fable planejou · Sonnet implementou · Claude+Codex+Kimi revisaram · 7 achados aplicados). **Como validar:** edite qualquer linha de `orq/` **sem** bumpar a versão e rode `python3 orq/scripts/lint-coerencia.py .` — tem que falhar dizendo que o que roda não é o que você editou. Depois do release, `diff -rq ~/.claude/plugins/cache/orquestra/orq/0.11.0/ ./orq/` tem que voltar **vazio**. ✅ **OS DOIS CRITÉRIOS PASSARAM EM 2026-08-07, medidos pelo Manager (teste mecânico, sem viés de roteamento):** criado `orq/_teste-t017.md` sem bumpar → o lint falhou com exit 1 e **nomeou o arquivo** (*"versão 0.19.0 já existe no cache com conteúdo diferente (ex.: `_teste-t017.md`)"*); removido o arquivo, voltou verde. E o `diff -rq` do cache `0.19.0` contra `./orq/` voltou vazio logo após o release. **Falta só o seu de-acordo para fechar.** @release-validacao

## Nota herdada do card `T-024` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** O painel de revisão não está funcionando

⚠️ **nasceu de uma frase de teste de roteamento (`T-014`/`T-016`), não de uma falha observada** — confirmar com o dono antes de planejar: se foi só o teste, este card fecha sem trabalho nenhum. Mantido no board de propósito, porque engolir o card é justamente o defeito que o desempate existe para evitar. 🟡 relato do dono em 2026-07-29, **sem sintoma detalhado ainda**: falta saber se não roda, se roda e volta vazio, se só um parecer volta, ou se trava. Entrou pelo **ciclo** e não pelo diagnóstico de ambiente porque o painel é o que o **produto** faz (`/orq:revisar`) — pelo desempate da skill, o card nasce antes da investigação, e o diagnóstico, se rodar, serve ao plano. **Cruzamento obrigatório:** `T-010` (painel consertado — duas causas raiz: `codex exec` bloqueia lendo stdin sem TTY, resolvido com `< /dev/null`; e subagente spawnado **com `name`** vira teammate e nunca devolve resultado) e `T-007` (Kimi em `~/.kimi-code/bin/kimi`, fora do PATH) estão **os dois em VALIDATE, nunca validados pelo dono na prática** — se a falha se confirmar, os dois voltam reprovados e a causa raiz é provavelmente regressão de um deles, não defeito novo. **Terceira hipótese, com precedente:** em 2026-07-28 os pareceres de Codex e Kimi **estouraram o tempo** no meio de uma revisão real e voltaram parciais, sem veredito. **Próximo passo:** planner reproduz `/orq:revisar` numa mudança pequena e localiza onde quebra — invocação, execução do CLI externo, retorno do subagente ou reconciliação. **✅ FECHADO EM 2026-07-31 SEM TRABALHO — o dono confirmou que era a frase de teste**, o painel não falhou. O card existiu de propósito: engoli-lo teria sido o defeito que o desempate do `T-016` existe para evitar. **Fica pendente em outro lugar:** o painel continua sem validação prática do dono — isso é o `T-010`, em VALIDATE.

## Nota herdada do card `T-007` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** Kimi como terceiro revisor do painel

**desbloqueado**: o CLI existe (`~/.kimi-code/bin/kimi`, v0.29.2, OAuth), só não estava no PATH — por isso o agente global `kimi-revisor` nunca revisou nada. Testado de ponta a ponta: 2min12s, formato exato, 5 riscos concretos, worktree intacto (read-only confirmado na prática, já que ele não tem flag de sandbox). O painel agora é **Claude + Codex + Kimi**, e "confirmado por 2+" deixou de exigir unanimidade. Adotados do prompt do dono: **formato único** (BLOQUEADORES/RISCOS/VEREDITO) e a **regra LGPD** — nenhum dado de paciente, PII ou credencial vai para revisor externo. **Como validar:** rode `/orq:revisar` numa mudança real e confira que os **três** pareceres voltam, que a reconciliação separa confirmado-por-2 de achado-solitário, e que ele avisa se algum revisor falhou. ✅ **RODADO DE VERDADE EM 2026-08-07, sobre o diff da própria 0.19.0 (`8bef7f9`):** os três pareceres voltaram no formato exigido — Kimi 83 KB (1 bloqueador + 3 riscos), Codex 64 KB, Opus interno (4 bloqueadores + 6 riscos) — e os três **reprovaram** independentemente. A reconciliação separou confirmado-por-3 (procedência inflada em `_elenco.md:110`), confirmado-por-2 (template v2; `spawn_agent`; heading sem escopo de host) e solitário-verificado. O Kimi rodou em worktree descartável e o `git status` ficou **vazio** no fim. **Nasceram `T-033`/`T-034`/`T-035`.** ⚠️ **Gotcha pago na primeira tentativa:** em foreground os dois externos morreram no teto de 10 min do shell — em background entregaram; ver `gotchas.md`. @release-validacao

## Nota herdada do card `T-038` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** Compor o board dentro de uma statusline alheia (a folha F4, extraída do `T-036`)

🟡 **desenho pedido pelo dono em 2026-08-08**: *"o script pesquisaria se já existe uma board, veria qual é a arquitetura dessa board, e incluiria nela a parte das tasks"*. Separado do `T-036` em 2026-08-08 porque **prendia o conserto**: 3 rodadas de painel, 8 pareceres, **8 reprovações** — e os defeitos encolheram a cada rodada sem zerar. **O material já existe e não se perde:** `orq/compor-statusline.md` (procedimento T1-T6/P0-P7) está escrito e no working tree, com **9 fixtures executáveis** já exercitadas (5 compuseram com prefixo byte-idêntico; 3 caíram em fallback antes de escrever, com motivo nomeado; 1 escreveu, reprovou, reverteu e o `cmp` provou restauração byte-idêntica). A tese está validada — o que falta é o **acabamento das bordas**. **Achados abertos da rodada 3, todos com cenário concreto:** interseção F2×F3 (wrapper alheio que chama nosso script satisfaz os dois ramos → a barra da pessoa é descartada) · P2 declarado read-only mas mandando copiar (confirmado por **3 revisores**; numa leitura escreve antes da aprovação, na outra a folha nunca funciona) · T2 com prosa divergindo da ilustração e relatando causa errada · **guarda de metacaracteres sem `>`/`<`/`&` + `eval echo`** → conteúdo de settings podia disparar processo na fase read-only (🔴 segurança) · T6 e P5 usando interpretadores diferentes → barra Bash/Zsh reprova sem motivo real · publica antes de validar, sem rename atômico · append quebra alvo sem newline final · fallback prometendo bloco "preenchido" quando não há valores resolvidos. **Não recomeçar do zero** — a rodada de correção destes achados estava em curso quando o card foi separado; ver a thread do `T-036` (seção `# PLANO v3`) e este board.

## Nota herdada do card `T-034` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** Os consumidores não resolvem o time por host

o painel fora do Claude fecha 2 vendors, e o Loop A escolhe um planner cego — 🔴 **dois achados com a mesma causa raiz, confirmados por 2 revisores cada e verificados no arquivo em 2026-08-07**. A 0.19.0 criou `## Times por host`, mas os consumidores continuam lendo `## Papéis` sem saber em que host estão. **(a) Painel:** o `T-026` manda conferir que "no Codex o painel fecha **três** vendors, não dois" — pelo `revisar.md` atual **não fecha**: não há passo que invoque o revisor Anthropic pelo time do host (as duas menções a `opus`, `:49` e `:111`, são padrão-sem-elenco e ordem de rebaixamento, nenhuma é disparador); `_elenco.md:65-69` garante **de propósito** que não há linha `claude` na tabela de externos, então o catch-all não o alcança; e `revisar.md:63` dispara `codex exec` sempre que `codex` estiver no PATH — no host Codex, sempre. Resultado: **OpenAI duplicado, zero Anthropic**, violando o princípio 3 do próprio `_elenco.md`. **(b) Loops:** o heading `## Papéis (é ESTA que os comandos leem)` (`_elenco.md:26`) não tem escopo de host e é falso em 2 dos 3 hosts; `plan-next.md:17-18` e `implement-next.md:14-15` mandam ler o papel sem passo de resolução. Cenário: Loop A no host Codex → planner `fable` → a célula Anthropic×Codex é `claude -p`, que a própria Matriz marca **"não lê arquivos"** — um planner cego, falhando em silêncio. **Divergência de severidade resolvida pelo Manager:** Opus disse bloqueador e Kimi disse risco para (b); fica **bloqueador**, porque a falha é silenciosa. **Correção proposta:** passo "revisor `opus` do time do host via célula Anthropic×host" + cláusula "pule a linha do SEU vendor" + escopar o heading + uma linha de resolução por host em `plan-next`/`implement-next`.

## Nota herdada do card `T-032` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** O protocolo de várias janelas ficou incompleto onde o projeto cresceu depois dele

🟡 pedido do dono em 2026-08-05, a partir da pergunta *"como está a questão do gerenciamento dos checkpoints em múltiplas janelas do mesmo repositório?"*. **O `T-013` funciona** — foi validado hoje **entre hosts diferentes** (o Codex detectou uma edição do Manager em `gotchas.md`, reconheceu que não era da frente dele e excluiu do escopo sem sobrescrever). **Mas três buracos apareceram ao responder a pergunta, e dois são erro do Manager:** **(1) o log tem duas instruções contraditórias** — `memory/wiki/_schema.md` manda *"append no **fim**, entrada carimbada com a frente"* e `orq/commands/checkpoint.md` manda *"append no **TOPO**"*. É a mesma família de defeito que a 0.17.0 inteira combateu (regra em dois lugares, uma falsa), e estava aqui desde antes. **(2) nenhuma entrada de log do Manager é carimbada com a frente**, embora o schema exija — com três janelas escrevendo, daqui a um mês não se sabe quem fez o quê. **(3) a seção `⏸️ O que espera o dono` do `memory/MEMORY.md` nasceu em 2026-08-04 sem regra de concorrência** — o schema não a lista na tabela de "quem escreve o quê", então **duas janelas dando checkpoint se sobrescrevem ali em silêncio**, e é justamente a seção que o dono lê primeiro ao voltar. **Nenhuma quebrou nada ainda** — a (3) só morde com dois checkpoints quase simultâneos. **Decidir também:** o append no fim vs. topo tem o mesmo ponto de disputa nos dois casos; talvez a saída seja outra (uma seção por frente? arquivo por frente?) em vez de escolher entre os dois. **Não confundir com o `T-013`**, que está em VALIDATE e cobre o board — este é sobre **log, índice e a marca de frente**.

## Nota herdada do card `T-015` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** Diagnóstico de ambiente dá **falso all-clear**

🔴 **voltou de VALIDATE: reprovado por 3/3 revisores** (Claude+Codex+Kimi, 2026-07-28). O card afirmava "atritos diagnosticáveis" e o diagnóstico erra no primeiro item. **Confirmado empiricamente:** (a) checagem de plugin desatualizado compara *versão*, mas o cache é indexado por versão — `diff -rq ~/.claude/plugins/cache/orquestra/orq/0.10.0/ ./orq/` acusa `lint-coerencia.py` divergente **agora**, e o diagnóstico diz "tudo certo"; (b) "board legível" só manda rodar o script — 7 cards escritos, 4 com marcador em negrito → `📋 33% (1/3)` sem `⚠`, reportaria ✓; (c) `README.md:389` ("marcador ou ID **dentro de** negrito/crase não casa") contradiz `_schema.md:15` e o exemplo logo acima — quem seguir tira as crases do ID e perde o board inteiro; (d) `/reload-plugins` vs restart contradiz `distribuicao.md:26` e o `--help` da CLI; (e) `_schema.md` ausente acusado como defeito, mas `checkpoint` e `wiki-lint` degradam de boa; (f) fallback de caminho conhecido existe só pro Kimi, não pro Codex. **Implementado e revisado em 2026-07-29** (Fable planejou · Sonnet implementou · Claude+Codex+Kimi revisaram · 7 achados aplicados). **Como validar (pós-release + restart):** rode `/orq:stack --verificar` e confira que ele compara **conteúdo** do cache (`diff -rq`), não só a versão; que "board legível" mostra os três sinais; e que num projeto sem `memory/` ele **não** acusa `_schema.md` como defeito nem propõe criar a árvore.

## Nota herdada do card `T-035` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** Procedência inflada e a fumaça do `instalar.md` usando a forma que a 0.19.0 declarou insegura

🟡 **três achados do painel de 2026-08-07, mesma família: o texto promete mais garantia do que tem**. **(1)** `_elenco.md:109` — a célula OpenAI×Codex dá `spawn_agent` como "observado 1×", mas a thread `T-026` registra que isso é observação de **binário**, não de sessão viva (*"não prometer elenco no Codex até ver"*); confirmado por 2 (Opus risco · Codex bloqueador). **(2)** `orq/commands/instalar.md:120-121` manda a fumaça do Kimi como `"$KIMI" -p "onde paramos?" --output-format text` — **sem `-m` e com `-p` primeiro**, as duas formas que a própria 0.19.0 declarou inseguras. Em 2026-08-07 só não mordeu porque o Manager seguiu a Matriz e não o `instalar.md`; seguindo o arquivo, a instalação teria sido dada como boa rodando o `default_model` de terceiro. **(3)** `_elenco.md:14-15` garante que o `/orq:elenco` "só pode escrever a tabela do host Claude (`## Papéis`, `Perfil ativo`, `## Perfis`)", mas `elenco.md:22` documenta `codex off`/`codex xhigh`, que gravam em `## Revisores externos` — **estado compartilhado entre hosts**: uma janela Claude com `/orq:elenco kimi off` faz a janela Codex montar o painel seguinte sem Moonshot, exatamente a interferência que `## Times por host` promete impossível. ✅ **A célula Moonshot×Kimi já foi corrigida** no checkpoint de 07/ago, com medição real (CLI comprovada, sub-agent não testado) — as três acima seguem abertas.

## Nota herdada do card `T-033` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** O template do `_elenco.md` não ganhou as seções da 0.19.0

projeto novo nasce apontando para o vazio — 🔴 **confirmado por 2 revisores (Opus + Codex) e verificado por `grep` em 2026-08-07**. O template "Modelo do arquivo" em `orq/commands/elenco.md`, usado pelo `orq/commands/init.md`, gera um elenco v1 — `## Papéis` + `## Revisores externos` + `## Perfis`, e nada mais. Mas `orq/commands/revisar.md:56` e `orq/skills/orq/SKILL.md:85` passaram a mandar consultar `## Matriz de invocação` e `## Times por host`. O `grep` confirma: as duas seções existem **só** em `memory/wiki/_elenco.md` deste repo, **zero** ocorrências em `orq/`. **Cenário:** `/orq:init` num projeto Y com a 0.19.0 → host Codex → `/orq:revisar` manda entrar "pela célula-diagonal da `## Matriz de invocação`" → seção inexistente → o modelo improvisa, e o próprio texto do plugin descreve o desfecho: *"o painel fecha só dois vendors e ninguém avisa"*. O `README` vende "elenco host-agnóstico" como entrega da 0.19.0, então o dono espera isso em qualquer projeto. **Correção proposta:** as duas seções no template + migração aditiva para elenco já existente + cláusula "seção ausente → declare a degradação" nos dois ponteiros. ⚠️ **Este repo é imune por acidente** — as seções foram escritas à mão aqui, então nenhum gate acusa; é a mesma mecânica do `T-029`.

## Nota herdada do card `T-027` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** CLI do Codex direto vs subagente `codex:codex-rescue`

**decisão do dono, não do Manager** — 🟡 achado da auditoria da wiki em 2026-07-30. A regra global dele (`~/.claude/CLAUDE.md`) diz: *"NUNCA invoque o binário `codex` diretamente via Bash de dentro do Claude Code — use sempre o subagente/comando, porque o binário direto perde o rastreamento de job (status/result/cancel/resume)"*. Este projeto instrui o contrário em dois lugares vivos: `memory/wiki/_elenco.md:25` e `orq/commands/revisar.md` mandam `codex exec … < /dev/null` por Bash. **A justificativa registrada venceu:** o `gotchas.md` dizia que `codex:codex-rescue` "não aparece como agent type" — ele aparece desde 29/jul, reconfirmado em 30/jul. **Não é o mesmo que dizer que a escolha está errada:** a CLI direta é o caminho que o `T-010` provou funcionar (o subagente spawnado **com `name`** nunca devolve resultado, e o `< /dev/null` resolveu o bloqueio em stdin), e o painel de revisão depende disso hoje. **As duas saídas honestas:** (a) documentar no projeto uma **exceção deliberada** à regra global, com o motivo; ou (b) migrar o painel para o subagente e medir se ele devolve parecer completo. Enquanto não decidir, o `gotchas.md` já carrega o aviso de premissa vencida para ninguém citar a versão velha.

## Nota herdada do card `T-011` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** Atritos do primeiro `/orq:init` em projeto de terceiro

10 achados aplicados, **depois reprovados pelo painel e corrigidos de novo**. O painel (Claude + Codex) mostrou que a 0.6.0 documentou o contrato mas deixou o **parser permissivo**: item de checklist solto contava como card, `## Arquivo` não encerrava a contagem, card sem crases vazava. Corrigido na 0.6.1 endurecendo o regex e fazendo o desvio aparecer como `⚠N` — falha visível em vez de silenciosa. **Os 4 bugs de contrato:** (1) produtor e consumidor do board não compartilhavam spec, e card fora do formato deixa a statusline **muda sem erro**; (2) `checkpoint` e `wiki-lint` liam um `_schema.md` que o `init` nunca criava; (3) nenhuma regra sobre colisão entre agente local e os `orq-*` do plugin; (4) nada verificava a instalação no fim. **Correção estrutural:** o `_schema.md` virou o contrato compartilhado — o `init` cria, o `checkpoint` e o `wiki-lint` leem, e a FASE 5 exige smoke test de **três sinais** (vazio · `⚠N` · denominador ≠ contagem manual). **Como validar:** rode `/orq:init` num projeto novo e confira que o `_schema.md` nasce e que o smoke test compara a contagem, não só "saiu alguma coisa". **Fechado em 2026-07-29:** o `_schema.md` existe e o parser estrito foi exercitado em 4 cenários.

## Nota herdada do card `T-013` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** Protocolo de várias janelas

o dono trabalha com N janelas Claude, uma por frente, e o modelo pressupunha UM Manager: as janelas se sobrescreviam em silêncio. **Regra base:** uma janela = uma frente. **Três regras que dispensam lock:** releia antes de escrever · edite só as linhas dos seus cards (nunca reescreva o board inteiro a partir de cópia velha — é a reescrita que apaga, não a concorrência) · card em curso leva `@frente` no fim da nota. **O ganho maior não é a trava:** pendência de decisão vira card `[!]` com a pergunta exata + "RETOMAR AQUI" na thread, e aí a janela **pode fechar** — antes ela ficava viva só como memória de pendência. Escrito em `_schema.md`, no `checkpoint`, na skill e no template que o `init` gera. **Como validar:** abra duas janelas, mexa em cards diferentes nas duas, dê checkpoint nas duas e confira que nenhum movimento sumiu; depois deixe uma pendência em `[!]`, feche a janela e veja se outra retoma sem você explicar nada.

## Nota herdada do card `T-029` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** O lint não enxerga caminho relativo entre arquivos do plugin

🟡 achado no review do `T-020` (2026-07-31), e a mecânica é a mesma que deixou `/orquestra:*` sobreviver a três releases. `orq/scripts/lint-coerencia.py` valida referências no formato `${CLAUDE_PLUGIN_ROOT}/…`, mas **ignora caminho relativo cru** (`orq/commands/elenco.md`). Isso é pior que não validar: dentro **deste** repo o caminho relativo resolve por acidente — o repo **é** o plugin — então o gate fica **verde** enquanto a instrução está quebrada para qualquer outro projeto, onde o arquivo mora em `~/.claude/plugins/cache/…`. Foi exatamente o defeito que o `T-020` introduziu no `init.md:171` e que só o revisor pegou. **Proposta:** o lint acusa qualquer `orq/…` relativo dentro de `orq/`, mandando trocar por `${CLAUDE_PLUGIN_ROOT}/…`. Cuidado com falso positivo: `README.md` e `memory/` **devem** usar caminho relativo, porque falam do repositório, não do plugin instalado.

## Nota herdada do card `T-010` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** Painel de revisores consertado

**duas causas raiz, ambas corrigidas.** (a) `codex exec` bloqueia lendo stdin sem TTY: `< /dev/null` resolve, resposta em segundos. (b) Subagente spawnado **com `name`** vira teammate e nunca devolve resultado; sem nome, entregou em 231 s. O `/orq:revisar` foi reescrito para usar a CLI direto (era o plugin `codex:codex-rescue` com forwarder) e para proibir `name` no spawn. **Como validar:** rode `/orq:revisar` numa mudança real e confirme que **os dois** pareceres voltam e que a reconciliação separa confirmado-por-dois de achado-por-um. ✅ **PASSOU EM 2026-08-07 — e com três, não dois** (ver `T-007`): nenhum revisor travou, nenhum voltou vazio, e as duas causas raiz deste card seguem resolvidas — o `codex exec` respondeu com `< /dev/null`, e o `orq-reviewer` spawnado **sem `name`** devolveu o parecer normalmente (25 min, 22 tool uses). **Falta só o seu de-acordo para fechar.** @release-validacao

## Nota herdada do card `T-021` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** Motor alternativo quando o Claude está no limite

🟡 pedido do dono em 2026-07-29, **e tem teto técnico que o plano precisa respeitar**: subagente do Claude Code só aceita modelo Claude (`opus`/`sonnet`/`haiku`/`fable`/`inherit`), então Codex e Kimi **não podem ser spawnados** como planner ou implementer — só invocados por CLI, como o painel de revisão já faz. E o Manager (a sessão principal) é sempre Claude, por construção. Então a pergunta real do card é: **quais papéis podem migrar para CLI externa e com que garantia?** Planejamento por `codex exec -s read-only` é viável e barato. Implementação é o problema: exigiria escrita, o Codex precisaria sair do `read-only` e o Kimi **não tem sandbox nenhum** (ver `T-019` — ele destruiu o working tree em 2026-07-28). Considerar worktree descartável obrigatório. Regra LGPD continua: código e arquitetura vão, dado de paciente não.

## Nota herdada do card `T-012` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** Piloto dos loops A e B

o `/orq:init` já foi validado em projeto real (`T-003`), mas `/orq:plan-next` e `/orq:implement-next` **continuam sem nunca terem sido invocados de verdade** — todo o trabalho até aqui foi feito pelo Manager na mão. É o mesmo tipo de ponto cego que o `T-003` expôs no `init`: contrato entre partes que ninguém exercitou. Rodar um card do backlog pelo fluxo formal, sem atalho. **Fechado em 2026-07-29 — cumprido pelo ciclo da 0.11.0:** Fable planejou (16 passos), o dono aprovou no gate, Sonnet implementou, três revisores auditaram, 7 achados voltaram como correção. O contrato entre as partes foi exercitado e **achou defeito que `validate` e `lint` não pegam**. Ressalva honesta: os agentes foram spawnados direto, não pelos comandos `/orq:plan-next` e `/orq:implement-next` — o fluxo está provado, os dois comandos literais não.

## Nota herdada do card `T-028` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** `README.md` afirma que o Kimi não está instalado

e ele é revisor ativo desde 28/jul — 🟡 achado de raspão no review do `T-020` (2026-07-31), **contradição pré-existente**, não introduzida por aquele card. `README.md:232-234` diz *"Kimi K2 ainda não está instalado nesta máquina (sem CLI e sem MCP)"*, enquanto `memory/wiki/_elenco.md:33` registra o Kimi **ativo** desde 2026-07-28 (v0.29.2, OAuth, symlink em `~/.local/bin/kimi`) e o `/orq:revisar` conta com ele para o "confirmado por 2+" virar maioria em vez de unanimidade. Note que o nome também envelheceu: **K2** virou K3 na fala do dono. **Efeito:** quem lê o README para decidir se o painel tem três revisores conclui que tem dois. **Nenhum dos dois gates pega isso** — é afirmação de fato sobre o ambiente, não referência quebrada.

## Nota herdada do card `T-008` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** Lint de coerência interna

`orq/scripts/lint-coerencia.py`. Confere `/orq:x`, `` `orq-agente` ``, `` skill `nome` `` e `${CLAUDE_PLUGIN_ROOT}/arquivo` contra o que existe; ignora `memory/`. Testado nos dois sentidos: passa no estado atual e pega os 4 tipos de defeito quando injetados. **Como validar:** renomeie mentalmente um comando (ou rode `python3 orq/scripts/lint-coerencia.py .` depois de editar qualquer coisa) e veja se ele aponta `arquivo:linha`. Documentado no `CLAUDE.md` como verificação obrigatória junto do `validate`. **Fechado em 2026-07-29:** validado injetando os 4 tipos de defeito numa cópia — pegou os 4 com `arquivo:linha` e `exit=1`.

## Nota herdada do card `T-037` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** Tirar o SuperMemory do sistema de desenvolvimento

**`0.22.3` PUBLICADA E INSTALADA**: `origin/main` em `3bb1a24`, Codex e Claude na mesma versão e Kimi no mesmo snapshot. Não há SuperMemory, `sm-search` ou `/orq:lembrar` ativos no produto nem nas instruções globais; resíduos foram movidos para backup recuperável em `~/.codex/backups/orquestra-0.22.3-b84bc51`. Suíte de 113 testes, gates, comparação dos caches e smokes em processos novos passaram. A task atual ainda carregava o hook `0.22.2`; o cache antigo foi restaurado sem tocar na `0.22.3`. Aguarda validação prática do dono após reabrir a task; T-044 permanece fora. @frente-supermemory

## Nota herdada do card `T-003` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** Piloto end-to-end

**cumprido em 2026-07-27, e melhor do que o card pedia:** o `/orq:init` rodou em repositório de terceiro, por outra LLM, sem eu por perto. O relatório de atrito veio com 10 achados (4 bugs de contrato reais) e virou o `T-011`. Também validou o que **funciona**: a regra "este comando se ADAPTA ao projeto" cortou 6 agentes genéricos que seriam criados sem ela, e o `_stack.md` com "Dispensadas" evitou repropor ferramenta já recusada. **Como validar:** nada a testar — o card era o próprio experimento. Feche se concordar que o piloto respondeu a pergunta. **Fechado em 2026-07-29:** o piloto respondeu a pergunta.

## Nota herdada do card `T-043` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** Proteção preventiva da janela de contexto no Codex

guardião consultivo publicado na `0.22.3`: Codex não bloqueia, recuperação sem telemetria e rearme em +10 p.p.; Claude preserva `/clear`. Suíte combinada de 113 testes, parecer final aprovado, smoke Codex consultivo e smoke Claude-only fail-open passaram. Aguarda validação prática do dono em task reaberta. O aviso global `_managedBy` é preexistente e segue separado da release. @frente-protecao-contexto

## Nota herdada do card `T-046` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** Lint de coerência separa `.in_use/<PID>` de divergência real

`0.22.4` publicada no commit de produto `676846a` e instalada no Claude/Codex. Os 29 arquivos do pacote são byte-idênticos nos dois caches; o lint real passou com dois marcadores Claude ativos, enquanto extras e bytes divergentes continuam cobertos por teste. 105 + 14 testes, Ruff, painel Kimi K3 + Opus 5 e gates verdes. Cache `0.22.3` preservado nos dois hosts. @frente-protecao-contexto

## Nota herdada do card `T-031` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** Comando para listar agentes ativos

🟡 pedido do dono em 2026-08-05. O `/orq:elenco` já lista o time **configurado** para os próximos spawns e os revisores externos marcados como ativos, mas não responde necessariamente quais agentes estão **rodando agora**. **Decisão 1 fechada:** mostrar ambos em blocos separados — execução atual e elenco configurado. Planejamento em `memory/wiki/threads/T-031-agentes-ativos.md`. @frente-agentes-ativos

## Nota herdada do card `T-044` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** Endurecer reset concorrente do guardião de contexto

Opus 5 e Kimi K3 concordaram que uma transação anterior pode apagar o marcador `.reset` criado por `SessionStart(clear)`, causando over-enforcement recuperável (pedir um segundo `/clear`), e que o fallback Windows `lockdir` não recupera lock órfão. Follow-up da revisão final do `T-043`; sem bypass silencioso no alvo macOS/Linux. @frente-protecao-contexto

## Nota herdada do card `T-048` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** Auditores nativos de remoção e adoção graph-first

0.22.5 publicada em `origin/main` no commit `0cefa97` e instalada em Codex, Claude e Kimi. 184 testes, gates, validação prática 10/10 e painel Opus 5 + Kimi K3 verdes. Smokes em processos novos dos três hosts carregaram a skill e retomaram a memória/board; caches antigos preservados e nenhum hook protegido alterado. @frente-auditoria-nativa

## Nota herdada do card `T-047` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** Compatibilidade de sessões antigas após upgrades

inventário prévio à 0.22.4 encontrou referências absolutas a caches `0.18.0`–`0.22.2` já ausentes; `0.22.3` foi preservado/restaurado e a `0.22.4` instalada, mas as versões anteriores não podem ser declaradas recuperadas sem fonte verificável. Planejar catálogo/shim durável sem sobrescrever versões atuais. @frente-protecao-contexto

## Nota herdada do card `T-009` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** Stack complementar auto-detectada

catálogo `orq/stack.md` + comando `/orq:stack` + integração no `init` + seção no README. **Como validar:** numa sessão nova, diga *"o que falta instalar aqui?"* e veja se ele detecta sem você citar comando; depois confirme que ele **não instala nada** antes do seu ok e que respeita `_stack.md` (não repropõe a indexação já dispensada).

## Nota herdada do card `T-002` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** Hooks de processo

`PreToolUse` em `Edit`/`Write` sobre `KANBAN.md`: mover card para `[?]` sem artefato de review existente é bloqueado. Gate no **conteúdo do diff**, não em quem chamou. Camada 2 do roadmap#1. ⚠️ Verificar antes: o payload do hook distingue subagente da sessão principal? Se não, "só o Manager move cards" não é enforçável como o parecer supõe.

## Nota herdada do card `T-041` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** Paridade core do Codex

`0.21.0` instalada e validada em Claude/Codex, caches idênticos e smoke externo com `OPUS_MODEL=claude-opus-5` + Kimi exit 0. Push autorizado e confirmado no GitHub: `main` contém a versão e o runner. **Aguarda validação prática do dono no projeto real que antes falhava, em nova sessão Codex.** @frente-paridade-codex

## Nota herdada do card `T-040` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** Paridade operacional do Orquestra no Codex

coordena `T-041` (core `0.21.0`), `T-043` (guardião `0.22.3`, agora em VALIDATE) e `T-042` (statusline opt-in `0.23.0`). A `0.22.3` foi publicada e instalada com paridade em Codex, Claude e Kimi; esta frente continua aberta para a validação prática do dono e a futura `T-042`. @frente-paridade-codex

## Nota herdada do card `T-001` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** Hooks de segurança

🔴 `PreToolUse` em `Bash` negando `git push`, merge, deploy, migration e SQL de escrita. Camada 1 do roadmap#1. Autocontida: não depende de saber quem chamou. **É o que transforma as promessas do modo noturno de disciplina em garantia — sem isso o T-006 não sai do papel.**

## Nota herdada do card `T-004` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** Workflows determinísticos em JS

3 separados (plan-card / implement-card / finalize-card), nunca um só: workflow não aceita input humano no meio e há gate do dono entre as etapas. Roadmap#2. Só depois do T-003 — workflow sobre fluxo que ainda vai mudar é retrabalho garantido.

## Nota herdada do card `T-045` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** Piloto Cartographer

validado pelo dono em 2026-08-29 com “prossiga”. Microbench congelado: stack atual 13/13, Cartographer 11/13; `adoption` foi o único ganho exclusivo. Decisão: **PORTAR IDEIAS**, sem instalar/integrar Cartographer. @frente-cartographer

## Nota herdada do card `T-042` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** Statusline nativa do Codex

perfil opt-in, backup/merge/rollback e limite explícito sem board em release local `0.23.0`; plano em `docs/superpowers/plans/2026-08-09-statusline-nativa-codex.md`. Executar somente depois de `T-043`. @frente-paridade-codex


## Nota do card `T-082` (nasceu em 2026-09-07)

**O sintoma:** com os caches `0.27.2` recém-sincronizados e corretos, o lint de coerência acusou
`versão 0.27.2 diverge do cache instalado (missing:scripts/__pycache__)`. A fonte tinha
`orq/scripts/__pycache__/` com três `.pyc` gerados na véspera; os caches instalados, corretamente,
não tinham. O `.gitignore` já ignora `__pycache__/`, então o diretório nunca esteve no repositório —
é artefato do host, exatamente a classe de problema que o `T-049` tratou no instalador.

**A causa raiz, e ela é sutil.** O `lint-coerencia.py` **já conhece** o risco: nas linhas 24-25 ele
declara `sys.dont_write_bytecode = True` justamente para não criar `__pycache__` no lado comparado e
produzir um falso vermelho autoinfligido. Essa guarda cobre a **geração durante a própria execução**
— e não a **comparação**. Um `__pycache__` deixado por qualquer execução anterior (teste rodado sem
`PYTHONDONTWRITEBYTECODE=1`, importação manual, IDE) sobrevive à guarda e vira divergência.
`verify_installed_cache.py`, que é quem compara, tem **zero** menções a `pycache` ou `.pyc`.

**Por que é vermelho caro:** a divergência é indistinguível, na saída, de um cache realmente stale —
que é o defeito real que o `T-017` e o `T-080` existem para pegar. Um lint que grita por artefato
gerado treina o leitor a ignorar o grito; foi assim que o `/orquestra:*` sobreviveu a três releases.

**A correção não é exclusão ad hoc.** O `CLAUDE.md` é explícito: as normalizações moram nas
allowlists de `verify_installed_cache.py`, e artefato de bytecode se qualifica pelo mesmo critério
das que já existem (gerado pelo host, nunca conteúdo do plugin). O paliativo desta sessão foi
`rm -rf orq/scripts/__pycache__`, que deixa o lint verde e não impede a reincidência.

## Atualização do card `T-019` (2026-09-07) — a premissa mudou de ator, não de natureza

**O Kimi saiu; o buraco ficou.** O `T-051` aposentou o Kimi do produto — hoje ele só aparece em
`orq/scripts/lint-coerencia.py`, como guarda que impede o retorno. As opções (a)/(b)/(c) da nota
original foram escritas contra um ator que não existe mais. **O card não está obsoleto:** o defeito
que ele descreve — *instrução não é enforcement* — reaparece inteiro no revisor de hoje.

**Verificado nesta sessão, com o cache instalado:**

- **Host Codex → reviewer `fable`: protegido de verdade.** `run-opus-reviewer.py:104-119` monta a
  CLI com `--permission-mode plan`, `--tools ""`, `--setting-sources ""` e
  `--disable-slash-commands`. Não é promessa textual: o processo não recebe ferramenta de escrita.
- **Host Claude → reviewer `gpt-6-astra@max`: protegido por interpretação, não por flag.** O
  `codex-companion.mjs:491` resolve `sandbox: request.write ? "workspace-write" : "read-only"` — a
  garantia dura existe e depende de **uma ausência**: ninguém passar `--write`. Só que o agente do
  Companion instrui o contrário (`agents/codex-rescue.md:35`): *"Default to a write-capable Codex
  run by adding `--write` unless the user explicitly asks for read-only behavior or only wants
  review, diagnosis, or research"*. Quem decide se a exceção se aplica é o subagente, lendo o
  briefing.
- **`orq/commands/revisar.md` não fecha esse elo.** Ele lista as flags da chamada
  (`--wait --fresh --json --model … --effort …`) e exige *"prompt READ-ONLY explícito"*, mas **em
  nenhum ponto proíbe `--write`** — a palavra não aparece no arquivo. `worktree`, `clone` e
  `descartável` também não: o isolamento que o `_elenco.md` deste projeto descreve (*"o Companion
  recebe o mesmo diretório isolado"*) **não existe no produto distribuído**, então um projeto de
  terceiro roda o revisor no repo vivo.

**Cenário de falha concreto:** a rodada 2 do próprio `revisar.md` se chama *"correção e nova
checagem pelo mesmo Reviewer"*. Um briefing que diga "aplique o apontamento e recheque" satisfaz,
ao pé da letra, a condição que o `codex-rescue.md:35` usa para acrescentar `--write` — o sandbox
vira `workspace-write` e o revisor passa a poder editar o checkout vivo. É o `T-019` com o Codex no
lugar do Kimi: a instrução textual não segura, porque o elo de decisão é o subagente, não uma flag.

**Correção candidata (barata, textual):** `revisar.md` passa a declarar a flag negativa —
*"nunca acrescente `--write`; a chamada do Reviewer é read-only por ausência dessa flag"* — e o
lint ganha guarda que falha se `--write` aparecer no caminho do revisor. O worktree descartável
para o revisor no host Claude é decisão separada, de custo maior.

⚠️ **Decisão do dono (segurança, N3):** reescopar o `T-019` para este ator, fechá-lo como superado
pelo `T-051`, ou mantê-lo como está. Nada foi implementado.


## Nota do card `T-082` (implementado e revisado em 2026-09-07)

**Correção:** `verify_installed_cache.py` ganhou `_is_bytecode_artifact` + `_strip_bytecode_noise`,
aplicados **simetricamente** às duas árvores dentro de `find_installation_divergences`, antes da
lógica de ancestrais allowlisted do Codex. É a primeira normalização **bilateral e não host-aware**
do verificador — as anteriores são installed-only —, e a justificativa é a natureza do artefato:
bytecode é ruído do interpretador nos dois lados, não metadado de um host.

**O parecer (`gpt-6-astra`, read-only, sem `--write`) trouxe dois achados, os dois aceitos:**

- **P1 — falso verde para `.pyc`/`.pyo` distribuído.** O predicado casa por sufixo e não pergunta a
  origem; um bytecode versionado sumindo do cache passaria despercebido. Hoje é hipotético
  (`git ls-files -- orq/` não devolve nenhum), mas a garantia era **presumida**. Virou guarda:
  `BytecodeDistributionGuardTests` falha se algum `.pyc`/`.pyo` estiver rastreado dentro de `orq/`
  (pula fora de checkout git, porque a árvore instalada não tem índice).
- **P2 — contradição com `orq/commands/instalar.md`.** Ele prometia normalizar *somente*
  `migrated-command-skills/`. ⚠️ **A frase já era falsa antes desta mudança:** as allowlists do host
  Claude (`.in_use`, `.orphaned_at`) nunca foram citadas ali. Reconciliado descrevendo os dois tipos
  reais. `CLAUDE.md` e `AGENTS.md` receberam o mesmo tratamento e seguem byte-idênticos.

Acrescentado ainda o caso de symlink com nome de bytecode, lacuna que o revisor apontou: symlink
continua comparado pelo alvo, porque pode apontar para fora da árvore.

**Verificação:** 302 testes, `validate --strict` ✔. O lint segue vermelho por
`bytes:commands/instalar.md` — é o alarme de `orq/` editado sem bump (`T-017`/`T-080` funcionando),
e só fecha com bump + reinstalação.

⚠️ **Handoff do Companion parcialmente comprovado:** `threadId 01a07cb8-dcc7-7880-8b91-4d3f8a5dbe27`,
`status 0`, **`jobId` ausente** no JSON devolvido. Pela regra do reúso `card+papel`, vínculo sem
`jobId` não está comprovado — uma continuação desta revisão nasce `--fresh`, nunca por
`--resume-last`.

⚠️ **Degradação declarada:** as correções do parecer foram aplicadas **pelo Manager**, não pelo
implementer — este host não expõe `SendMessage` para reabrir o subagente com o contexto dele. Perde-se
o contexto fresco de quem escreveu o código, e a auditoria das correções passou a ser do Manager.

## Nota do card `T-083` (nasceu em 2026-09-07, durante a revisão do `T-082`)

**O elenco promete um effort que a CLI recusa.** `_elenco.md` declara `gpt-6-astra@max` para
`reviewer` e `planner·sistema` no host Claude. A chamada com `--effort max` voltou:
`Unsupported reasoning effort "max". Use one of: none, minimal, low, medium, high, xhigh.` A revisão
do `T-082` rodou em `xhigh`.

**Por que é card e não nota de rodapé:** o `MEMORY.md` já registrava, no `T-079`, que *"uma das
revisões rodou em `xhigh`, não no `@max` que o elenco declara"* — atribuído então a "o runtime não
expôs a variante". Agora há a mensagem literal do erro: **`max` não existe nessa CLI**. Enquanto o
elenco declarar `@max`, toda invocação por essa via ou falha na primeira tentativa ou cai em `xhigh`
sem ninguém registrar a degradação — que é a definição de configurado-mas-não-exercitado.

**Escopo candidato:** decidir entre corrigir o elenco para `@xhigh` (honesto com a CLI) ou manter
`@max` como intenção e exigir que quem invoca traduza e **declare** a queda. Guarda no lint que
recuse effort inexistente para a via do Companion.

### Resultado do host Codex — 2026-09-07

A sintaxe literal `codex exec --effort max` saiu `2` porque `--effort` não é uma flag da CLI
0.153.4. Isso não é recusa do valor. A via real, explícita e isolada,
`codex exec --ephemeral --ignore-user-config --ignore-rules -c 'model_reasoning_effort="max"'
--model gpt-6-astra --sandbox read-only`, anunciou `reasoning effort: max`, respondeu
`CODEX_MAX_OK` e saiu `0`. Portanto `planner·interface` e `planner·sistema` do **Host Codex**
permanecem em `gpt-6-astra@max`. Como nenhum valor mudou nesse host, os quatro anchors de guarda e
fixture não precisaram de alteração. O card fecha com `@xhigh` somente na via Companion/Claude e
`@max` comprovado na via nativa Codex.


## `T-019` reescopado (2026-09-07, autorizado pelo dono) — e a superfície é maior que a apurada

**Título novo:** o read-only do Codex Companion é garantido só pela **ausência** de `--write`.

A nota de mais cedo hoje apontou `revisar.md`. Ao desenhar a correção, apareceram **três** pontos do
produto que montam a chamada do Companion, e **nenhum** proíbe a flag:

- `orq/commands/revisar.md:76-77` — Reviewer, primeira chamada e retomada;
- `orq/commands/plan-next.md:47-48` — `planner·sistema`, mesma dupla de linhas;
- `orq/commands/elenco.md:386` — a Matriz de invocação, que é de onde os outros dois copiam a forma.

Os três dizem *"briefing read-only"* e listam as flags **sem** `--write`. Nenhum diz que a flag é
proibida. Do outro lado, `agents/codex-rescue.md:35` manda acrescentá-la por padrão, salvo quando o
subagente **julgar** que o pedido é só revisão ou diagnóstico. O enforcement real existe
(`codex-companion.mjs:491` → `sandbox: request.write ? "workspace-write" : "read-only"`), mas quem o
aciona é uma omissão, não uma regra escrita.

**Cenário de falha, com as palavras do próprio produto:** a rodada 2 do `revisar.md` se chama
*"correção e nova checagem pelo mesmo Reviewer"*, e a linha manda enviar um *"apontamento"*. Um
briefing assim satisfaz ao pé da letra a condição que o `codex-rescue.md` usa para virar
write-capable. O sandbox abre e o revisor passa a poder escrever no checkout vivo — que é
literalmente o `T-019` de 2026-07-28, com o Codex no lugar do Kimi.

### Plano proposto (aguardando o gate do dono)

1. **Proibição explícita nos três pontos.** Cada um passa a declarar, junto da lista de flags, que
   `--write` é proibido e que o read-only vem da ausência dela. Texto igual nos três, para o lint
   poder exigi-lo como string.
2. **Guarda no lint.** `lint-coerencia.py` já mantém tuplas de strings obrigatórias por arquivo
   (`revisar.md` na linha 1667, `elenco.md` na 1687). Acrescentar a frase da proibição às tuplas de
   `revisar.md`, `plan-next.md` e `elenco.md`, mais uma regra que **falhe** se `--write` aparecer no
   caminho de um papel read-only. Sem isso, a proibição é mais uma instrução sem enforcement — que é
   o defeito que este card existe para matar.
3. **Teste.** Caso vermelho: remover a frase de um dos três → lint falha; injetar `--write` numa das
   linhas de invocação → lint falha. Controle negativo: os arquivos reais passam.

**Fora deste escopo, deliberadamente:** worktree descartável para o revisor no host Claude. É a
defesa em profundidade (vale mesmo se a flag vazar), mas custa mais e muda o fluxo — merece card
próprio, decidido separadamente.

**Critério de aceite:** os três comandos verdes; e a prova de que a guarda morde, exibindo o lint
vermelho nos dois casos do passo 3 antes de voltar ao verde.

## `T-019` — o parecer REPROVOU a rodada 1, e os dois bloqueadores procediam (2026-09-07)

O revisor (`gpt-6-astra@xhigh`, read-only, `write: false` confirmado no job) reprovou com dois
bloqueadores. Auditei os dois contra o código instalado antes de aceitar; **os dois procedem**:

- **A grafia procurada não era a única.** O parser do Companion (`lib/args.mjs`) trata token de
  hífen único por `token.slice(1)`, então **`-write`** resolve para a mesma chave booleana e abre
  `workspace-write` igual. A guarda buscava o literal `--write` e não via essa porta. Corrigido com
  regex das duas grafias e fronteira `(?<![\w-])`, que impede o falso positivo dentro de
  `workspace-write` — provado nos dois sentidos.
- **Os três comandos não eram todos os produtores de argumento.** `orq/skills/orq/SKILL.md`
  especifica a chamada e é **produto distribuído**; `memory/wiki/_elenco.md` é a matriz que os
  próprios comandos mandam consultar. Injetar a flag em qualquer uma das duas passava com o lint
  retornando 0. As duas entraram na guarda, e a política de `memory/` no `CLAUDE.md`/`AGENTS.md`
  passou de duas para três exceções nominais.

**Aceito como limitação declarada, não corrigido:**

- **A proibição é textual, não é enforcement de execução.** Quem decide passar a flag continua sendo
  o agente do Companion (`codex-rescue.md:35`, que manda acrescentá-la por padrão). A guarda impede
  que o **produto** ensine a flag; não impede que a chamada real a receba. Vincular tecnicamente o
  papel a read-only é a defesa em profundidade, e é o card do worktree descartável — deliberadamente
  fora deste escopo desde o plano.
- **Presença literal não prova normatividade** (achado médio): transformar a âncora em citação
  rotulada "exemplo obsoleto" ou enterrá-la em comentário HTML mantém os bytes e o lint retorna 0.
  Exigir "contexto normativo" é caro e vago; fica registrado como limitação conhecida.
- **A guarda é conservadora e gera falso positivo em prosa legítima** sobre a flag (inclusive
  `--write=false`). Decisão: manter, porque documentar a flag também é ensiná-la — a mensagem do
  lint passou a dizer isso, em vez de afirmar que toda ocorrência habilita escrita.

**Verificação da rodada 2:** 307 testes (302 + 5 da guarda), `validate --strict` ✔, lint acusando só
a divergência de cache por edição sem bump. Dois testes novos: a grafia de hífen único reprova, e
`workspace-write` fora da âncora **não** reprova — este último cai se alguém afrouxar a fronteira.

⚠️ **Degradação declarada (segunda vez):** as correções do parecer foram aplicadas pelo Manager. Sem
`SendMessage` neste host não dá para reabrir o implementer, e um worktree novo nasceria do HEAD, sem
o trabalho não commitado.


## Evidência nova para o `T-047` (medida em 2026-09-07, no preflight da 0.27.4)

O preflight obrigatório do `instalar.md` — que existe justamente para preservar caches que tasks
abertas ainda carregam por caminho absoluto — mediu o seguinte:

- **19 versões** aparecem referenciadas em `~/.codex/sessions` e `~/.codex/archived_sessions`,
  de `0.18.0` a `0.27.4`;
- no cache do Codex sobrou **1** diretório (`0.27.4`);
- no cache do Claude sobraram **11** (`0.22.4` … `0.27.4`).

**Os dois hosts não se comportam igual, e isso é o achado.** O `T-047` estava escrito como
"sessões antigas apontam para caches já ausentes", no genérico. A assimetria diz onde o defeito
mora: o caminho de instalação do Codex **remove** as versões anteriores, enquanto o do Claude as
**preserva**. As 18 versões referenciadas que sumiram do Codex já não podem ser restauradas por
backup — o backup desta sessão foi tirado depois, e só tinha a `0.27.4` para copiar.

Consequência prática: qualquer task Codex antiga reaberta hoje aponta para um diretório inexistente.
O preflight do `instalar.md` só protege quem o executa — e quem instalou desta vez não o executou,
ou não restaurou depois.


## Nota do card `T-085` (nasceu em 2026-09-07, do incômodo do dono)

**O sintoma, na palavra dele:** "ficam aparecendo chats no mesmo projeto lá dentro do Codex quando
você aqui chama o Codex como revisor, como implementador".

**A causa é estrutural, não um descuido.** `codex-companion.mjs:493` passa `persistThread: true`
**fixo** no subcomando `task` — não há flag para desligar. E a thread persistida é exatamente o que
dá o `--resume-thread <threadId>`, que o Orquestra usa desde a `0.27.2` (`T-081`) para o reúso
determinístico por `card+papel`. **A poluição e o reúso são o mesmo mecanismo**: matar um mata o
outro.

**O que o companion NÃO oferece:** não existe `archive` nem `delete` na CLI (os subcomandos são
`setup`, `review`, `adversarial-review`, `task`, `transfer`, `status`, `result`, `cancel`). Então
"eu mesmo fecho depois" não é executável hoje pelo caminho suportado — e a `SKILL.md` proíbe
explicitamente cancelar task concluída ou deletar task do Companion.

**Quatro saídas, e a escolha é do dono porque cada uma perde algo diferente:**

1. **Aceitar a thread e limpar depois**, apagando a sessão do Codex quando o handoff já estiver
   registrado na wiki. Custo: contraria a regra "nunca delete uma task do Companion" da `SKILL.md`,
   que existe para não perder contexto — a regra teria que ser revisitada, não burlada.
2. **Trocar `task` por `review`/`adversarial-review` no papel Reviewer.** Esses não persistem thread
   (`codex-companion.mjs:411` chama `runAppServerTurn` sem `persistThread`). Custo alto: o prompt é
   construído internamente, então **acaba o briefing sob medida**, e não há `--effort`.
3. **Manter e organizar**: nomear as threads por `card+papel` para ficarem agrupadas e óbvias.
   Não elimina, só torna legível.
4. **Pedir upstream** uma flag `--no-persist` no `task`. Sem prazo, e some o reúso quando usada.

⚠️ **Nenhuma delas é gratuita.** A pergunta para o dono é qual ele prefere perder: o reúso
determinístico, o briefing sob medida, ou a tela limpa.

## Nota do card `T-086` (nasceu em 2026-09-07, do incômodo do dono)

**O sintoma, na palavra dele:** trabalhando com Claude e Codex no mesmo repositório, "eventualmente
tem alguma task que tem interseção com outra e acaba surgindo a possibilidade de ter que editar,
mesmo que não seja a ação principal" — e isso "quase gerou problemas previamente".

**Não é hipótese: aconteceu duas vezes hoje, nesta janela.**

1. Uma edição do `MEMORY.md` falhou porque a outra janela reescreveu a linha entre a minha leitura e
   a minha escrita.
2. No mesmo comando, commitei junto o trabalho não commitado da outra janela, sem intenção.

**O que existe hoje e por que não basta:** o `@frente` do protocolo (`T-013`, `T-032`) separa
**assunto**, não **executor**. Duas janelas de hosts diferentes podem pegar cards distintos da mesma
frente, ou tocar o mesmo arquivo compartilhado (board, índice, log) sem nada acusar. O protocolo
manda "releia antes de escrever" e "edite a linha, nunca o arquivo" — as duas regras seguradas por
disciplina, não por mecanismo.

**Desenho candidato (a decidir):** marcar o **host** no card em curso, não só a frente — algo como
`@claude` / `@codex` junto do `@frente`, escrito quando o card sai de `[ ]` e apagado quando entra
em `[?]`. Some a isso uma guarda no lint que recuse dois hosts no mesmo card. O ponto de atenção é
que marcador em arquivo disputado **também** é disputado: se as duas janelas escreverem o marcador
ao mesmo tempo, o marcador não protege nada. Um arquivo por card (dono único por construção, como as
threads já são) resolve isso sem depender de disciplina — e é a alternativa que o plano precisa
comparar.


## Nota do card `T-087` (nasceu em 2026-09-07, durante a validação do `T-019`)

**Medido, não suposto.** Ao validar o `T-019` com uma chamada real, pedi ao subagente
`codex:codex-rescue` exatamente `--wait --fresh --json --model gpt-6-astra --effort low`. A linha
que ele executou, que ele mesmo devolveu:

```
node ".../codex/1.0.5/scripts/codex-companion.mjs" task "<briefing>" --wait --json --model gpt-6-astra --effort low
```

**`--fresh` não está lá.** Duas consequências, e a segunda é a que assusta:

1. **O contrato do reúso `card+papel` (`T-081`, `0.27.2`) não foi cumprido.** A primeira chamada de
   um par card+papel tem que levar `--fresh`; sem ela, o companion pode encadear numa thread
   anterior e misturar contextos — exatamente o que o `T-081` existe para impedir.
2. **É a prova empírica da limitação declarada no aceite do `T-019`.** Quem monta a linha de comando
   é o subagente. Se ele **omite** uma flag pedida, nada garante que não **acrescente** uma não
   pedida — e a flag não pedida perigosa é `--write`. A proibição textual reduz a chance; não
   elimina o elo.

**Terceiro fato, colateral:** ele usou o cache `codex/1.0.5` do companion, não o `1.0.6` que também
está instalado. Duas versões coexistem e a escolha não é declarada em lugar nenhum.

**Direção candidata:** parar de depender do subagente para montar a linha. Ou o Orquestra passa a
verificar, no handoff, que as flags exigidas estavam presentes (o `jobId`/`threadId` já são exigidos
— faltam as flags), ou a chamada deixa de ser encaminhada em prosa e passa a ser um contrato
verificável. O `T-085` toca no mesmo ponto por outro lado.


## Nota do card `T-088` (nasceu em 2026-09-07, durante a validação do `T-020`)

**Achado pelo próprio teste, o que é o melhor tipo de achado.** Ao validar o `T-020`, o agente
trocou o perfil ativo para `economia` — o caminho que o produto oferece — e a suíte ficou vermelha
em 1 de 307: `test_elenco_perfis.py:113`,
`test_implementer_pesada_alterado_so_no_preset_reprova`.

**Causa:** o teste chama `mutar_preset_padrao(...)` e espera que o lint acuse divergência entre o
preset e a tabela ativa. Isso só vale enquanto **`padrao` for o perfil ativo**. Com `economia`
ativo, o lint compara contra `economia`, a mutação em `padrao` não gera diagnóstico, `rc` vira 0 e
o teste quebra.

**Por que importa:** a guarda do `T-080` e o teste dela estão **acoplados ao estado vivo deste
repositório**. Como o Orquestra é desenvolvido com o próprio Orquestra, uma troca de perfil
legítima — que é exatamente o que o `T-020` existe para permitir, e que o dono faz quando o crédito
aperta — derruba a suíte do projeto. O defeito não é do `T-020` nem da troca: é do teste presumir
um estado que o produto permite mudar.

**Correção candidata:** mutar o preset que a linha `Perfil ativo` **declara**, em vez de `padrao`
fixo. O `lint-coerencia.py` já lê essa linha para comparar, então o dado está disponível.

⚠️ **A troca para `economia` foi descartada** junto com o worktree do teste: era exercício de
validação, não pedido do dono. O elenco vivo permanece em `padrao`.


## `T-087` reescrito, `T-089` e `T-090` abertos (2026-09-07, corrida noturna)

⚠️ **O `T-087` como eu o escrevi estava errado, e o erro era meu.** Registrei que o subagente
"omitiu uma flag pedida" ao não passar `--fresh`. Auditando o plugin instalado:
`codex-cli-runtime/SKILL.md:34` manda **remover** esse token, e `codex-rescue.md:39` o define como
controle de roteamento do lado Claude ("não adicione `--resume-last`"), não como flag a repassar.
**O subagente fez o certo.**

O defeito real continua de pé, e é outro: **três contratos divergem sobre as mesmas flags** — o
Orquestra documenta uma linha, a skill do plugin manda transformá-la, o parser aceita um terceiro
conjunto — e **ninguém verifica o que chegou**. Por isso o card foi reescrito, não fechado.

**`T-089` é o achado grave da noite.** `--resume-thread` **não existe** no cache `codex/1.0.5`
(`grep -c` → 0; no `1.0.6` → 6), e o subagente escolheu o `1.0.5` nas duas chamadas observadas,
havendo três caches instalados. Onde o produto manda continuar com `--resume-thread <threadId>`, a
flag vira texto do briefing e a chamada nasce nova: **o reúso `card+papel` que a `0.27.2` entregou
não está funcionando, e nada acusa.** Foi validado por teste unitário e nunca exercitado contra o
cache real — que é exatamente a lacuna que o `T-017` descreve em outro contexto.

**`T-090`:** `--wait` não é opção do `task`. O `handleTask` aceita `model, effort, cwd, prompt-file,
resume-thread` e os booleanos `json, write, resume-last, resume, fresh, background`; `wait` pertence
ao `handleReviewCommand`. Ainda assim `revisar.md`, `plan-next.md` e o `_elenco.md` mandam passá-la.

⚠️ **Consequência para o `T-019`, que dei por validado hoje:** o JSON do `task` não devolve
argumentos, modelo, effort nem sandbox efetivo. O `write: false` que li prova o que foi **lançado**,
não o que o runtime **reconheceu**. A validação continua de pé — a linha de comando não tinha a flag
—, mas a evidência é mais fraca do que afirmei, e isso fica escrito em vez de corrigido em silêncio.

## `T-086` — a revisão REPROVOU a rodada 1, e o bloqueador era um comentário mentindo (2026-09-08)

O revisor (`gpt-6-astra@xhigh`, read-only) reprovou. Auditei cada achado reproduzindo o regex; **os
principais procedem**.

**🔴 P1 — texto incidental satisfazia a declaração de posse.** A guarda usava `@(claude|codex)\b`, e
o comentário ao lado afirmava que isso excluía `@claude-legado`. **É falso:** entre `e` e `-` existe
fronteira de palavra, então o token casava. Passavam também `x@claude`, `` `@claude` `` entre crases
e `<!-- @claude -->` num comentário HTML. Um card sem responsável visível terminava o lint em 0 —
falso verde, que é pior que acusar falta, porque parece conferido.
Corrigido: `(?<![\w@])@(claude|codex)(?![\w-])`, e trechos citados (crase, comentário HTML, link)
são removidos antes da busca — posse se declara na prosa da linha, não em citação.

**P2 — um título com "Arquiv" desligava a guarda até o fim do arquivo.** `[Aa]rquiv` casava em
`## Arquivos compartilhados`. Corrigido para `[Aa]rquivad[oa]s?` com fronteira, e blocos cercados
por crases passaram a ser ignorados — `## Arquivado` dentro de um exemplo não é a seção real.

**P2 — linha que parecia card escapava inteira.** Indentada, com outro bullet, ID sem crase ou
espaço a mais: o regex estrito não casava e a linha sumia da verificação. Agora ela é **denunciada**
como fora do contrato, em vez de silenciosamente ignorada.

**P2 — os testes não travavam o que prometiam.** A mutação do revisor provou: tirar `[?]` e `[x]` da
proibição deixava os quatro testes verdes. Agora cada estado proibido é exercitado separadamente, e
os falsos verdes acima viraram teste. São 11 casos na guarda, contra 4.

**Decisão que estava pendente e agora tem regra:** em `[!]` a marca **permanece** — a pausa preserva
a posse de quem estacionou —, a guarda ali só recusa os dois hosts juntos, e **quem retoma reafirma
ou transfere explicitamente**. Sem isso, o cenário do revisor se realiza: uma janela estaciona
`[!] @claude`, a outra retoma lendo a marca como histórica, e o lint aprova posse alheia.

**Duas correções de instrução que o parecer cobrou, e que valem além deste card:**

- a regra agora diz que **quem está marcado no card commita aquele trabalho** — a decisão do dono de
  não ter integrador fixo não estava escrita em lugar nenhum operacional;
- a afirmação *"só o board é disputado"* saiu da `SKILL.md`. Era falsa: `MEMORY.md`, `_elenco.md`, o
  log e o manifesto de versão também são escritos pelas duas janelas.

**Sobre os cards que estacionei:** o revisor confirmou que foi honesto não inventar host para
`T-040` e `T-031`, mas apontou que `[ ]` apaga a informação de que já tinham sido iniciados. Cada um
passou a registrar o estado anterior.

⚠️ **Degradação declarada (terceira vez):** as correções do parecer foram aplicadas pelo Manager.
Este host não expõe `SendMessage` para reabrir o implementer com o contexto dele, e um worktree novo
nasceria do HEAD, sem o trabalho não commitado.


## `T-047` — a assimetria se repetiu na instalação da 0.27.5 (2026-09-08)

Segunda medição, mesmo resultado: instalar a `0.27.5` deixou o cache do **Claude com 12 versões**
(`0.22.4` … `0.27.5`) e o do **Codex com 1** (`0.27.5` apenas) — a `0.27.4` que estava lá **sumiu**.

Não é evento isolado nem efeito de quem executou: ontem foram 19 versões referenciadas por sessões
Codex contra 1 sobrevivente; hoje, com uma instalação limpa e o preflight de backup rodado antes, o
comportamento se repetiu. **O caminho de instalação do Codex substitui; o do Claude acumula.**

O preflight desta vez tinha backup — mas ele só protege o que ainda existia no momento em que rodou.
As versões antigas já haviam sido removidas em instalações anteriores, então não há o que restaurar.
