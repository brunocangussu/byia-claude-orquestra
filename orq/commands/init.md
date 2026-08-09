---
description: Instala o Orquestra neste projeto — inspeciona o código, detecta as ferramentas disponíveis, propõe o time de agentes sob medida e monta a memória. Funciona em projeto novo ou já em andamento.
argument-hint: "[--reinstalar para refazer a análise]"
---

Você vai instalar o **Orquestra** neste projeto. Leia a skill `orq` primeiro (a disciplina).

**Regra de ouro: este comando se ADAPTA ao projeto.** Não despeje uma estrutura genérica — investigue,
decida o que faz sentido *aqui*, e só então proponha. Um script Python de 200 linhas não precisa do
mesmo time que um monorepo com backend, CRM e workflows.

---

## FASE 1 — Investigar (paralelo, read-only)

**Antes de disparar qualquer scout: use o que você já sabe.** Se você trabalhou neste projeto nesta
sessão, você já tem o mapa — **não gaste subagente pra confirmar o que já leu**. Liste o que já sabe,
identifique só as **lacunas**, e dispare scout apenas para elas. Num projeto pequeno que você acabou
de ler inteiro, o número certo de scouts é **zero**.

Para o que faltar, dispare `orq-scout` **em paralelo** (um por frente) e, enquanto isso, olhe você
mesmo a raiz. Não leia arquivos inteiros: use busca semântica e amostragem.

Levante:

1. **Stack e forma** — linguagens, frameworks, gerenciadores de pacote, monorepo vs único, onde
   ficam código/testes/migrations/infra. Tamanho (arquivos, LOC aproximado).
2. **Domínio** — do que o projeto TRATA (README, docs, nomes de módulos, modelos). Isso define os
   papéis: um projeto com banco e multi-tenant pede agente de dados; um site estático não.
3. **Como se trabalha aqui** — `CLAUDE.md`/`AGENTS.md` existentes, convenções, comando de build e
   de teste, o que **quebra o deploy** (regras de CI), estilo de commit no `git log` recente.
4. **Memória e docs que já existem** — `memory/`, `docs/`, `NOTES.md`, `TODO.md`, `ROADMAP.md`,
   snapshots, planos. **Tudo isso é matéria-prima** — a wiki nasce com a verdade que já existe.
   Anote **em que caminho** cada coisa está: um índice já existente pode não estar onde você espera.

   Classifique o estado sem reduzir “não tem board” a “não tem memória”:
   - **VIRGEM:** não há memória nem equivalente funcional;
   - **MEMÓRIA LEGADA:** há `MEMORY.md`, `memory/`, `NOTES.md` ou equivalente, mas não há board do
     Orquestra;
   - **ORQUESTRA PARCIAL:** existe ao menos um artefato do Orquestra, mas faltam obrigatórios;
   - **ORQUESTRA COMPLETO:** board, índice, schema e elenco existem.

   No segundo caso, diga exatamente: **“Memória preexistente detectada em outro formato; o
   Orquestra ainda não foi inicializado.”** Preserve tudo e siga a migração aditiva da FASE 4.
5. **Trabalho em aberto** — TODO/FIXME no código, issues, itens não concluídos nos docs, testes
   quebrados. Vira o backlog inicial (com IDs `T-NNN`).
6. **Ferramental disponível** (checar de verdade, não presumir):
   - **Rode as verificações de `${CLAUDE_PLUGIN_ROOT}/stack.md`** — é o catálogo da stack
     complementar (contexto, memória, busca semântica, revisor externo), com como detectar cada uma.
   - MCPs conectados além dessas (banco, deploy, observabilidade, design…)
   - Subagentes que o projeto **já** tem em `.claude/agents/`
   - Se houver busca semântica: **o repo já está indexado?**
   - **Statusline:** leia `statusLine` nos três escopos de settings — `.claude/settings.local.json`,
     `.claude/settings.json`, `~/.claude/settings.json` — e monte a visão completa: qual escopo tem
     a chave, qual é o **efetivo** (Local > Projeto > Usuário), quais ficam **sombreados**. Para
     **cada arquivo presente** (mesmo sem `statusLine`), registre também o **conjunto de chaves de
     topo** (`jq 'keys' <arquivo>`, ou leitura direta sem `jq`) — é essa lista, não só a visão de
     `statusLine`, que a FASE 5 usa como baseline ao provar que um merge preservou as chaves alheias;
     um arquivo que caiu em F1 justamente por não ter `statusLine` só tem baseline se ela for
     capturada aqui, antes de qualquer escrita.
     **Registre essa visão no relatório desta fase** — é o "antes" que a FASE 5 compara contra o
     estado pós-`/orq:init`, em vez de tentar capturar um "antes" depois de a FASE 4 já ter escrito.
     Com a visão em mãos, classifique o projeto em **exatamente uma** das três folhas da árvore da
     FASE 4, passo 4 (F1: nenhuma chave em escopo nenhum · F2: a efetiva aponta para dentro do
     plugin, instalação nossa defeituosa · F3: qualquer outra barra efetiva — mostra o board, ou
     não) — o critério completo de cada folha mora lá; rode a classificação **aqui**, nesta
     investigação, para que a pergunta certa já esteja pronta na FASE 3.

     ⚠️ **F3 depende de o board existir, e nesta fase ele pode ainda não existir** (projeto novo é o
     caso mais comum — quem cria `memory/wiki/KANBAN.md` é a FASE 4, passo 1, que roda **depois**
     desta investigação). Se `memory/wiki/KANBAN.md` **já existe** (projeto que já usa o Orquestra,
     `--reinstalar`), rode o critério completo de F3 aqui mesmo — sinal textual (a) e confirmação por
     execução (b), ver FASE 4, passo 4. **Se ainda não existe, o que fica em aberto é só quando o
     sinal textual (a) já passa:** rodar (b) agora sempre daria saída vazia (o `kanban-status.sh` sai
     sem imprimir nada quando o arquivo do board ainda não existe) e classificaria como "não mostra"
     um caso que, depois de a FASE 4 criar o board, mostraria — duas conclusões opostas na mesma
     execução do comando. Nesse caso (a passa, b pendente), registre a classificação com **só o
     sinal textual (a)**, marcada como **provisória**, e diga à FASE 3 para relatar como pendente de
     reconfirmação — não cravar "já mostra" nem "não mostra" ainda. A confirmação por execução (b)
     roda de novo na FASE 4, passo 4, **depois** de o passo 1 já ter criado o board — só esse
     resultado entra no relato final. **Se (a) já falha** (nenhum sinal de `kanban-status`/`KANBAN.md`
     no `command`, ou no que ele invoca), a conclusão já está decidida sem esperar o board existir —
     os dois critérios de F3 são obrigatórios (achado C7, ver FASE 4, passo 4), e falhando o
     primeiro a barra já **não mostra o board**: registre "não mostra" direto, sem marcar como
     provisória.

     Nenhuma escrita acontece nesta fase — gravar ou copiar: só depois da FASE 3, com aprovação.

## FASE 2 — Decidir (o julgamento)

**Time.** O núcleo — Planner · Implementer · Reviewer · Docs · Scout — **já vem pronto no plugin**
(`orq-planner`, `orq-implementer`, `orq-reviewer`, `orq-docs`, `orq-scout`). Você **não recria** esses
cinco: eles existem, e o que muda por projeto é só o **modelo**, via `_elenco.md`.

Agente local em `.claude/agents/` só para papel **adicional** que este projeto justifique — e com
**nome próprio, nunca `orq-*`** (ex.: `dados`, `infra`, `frontend`), para não colidir com os do
plugin. Justifique com fato do projeto: *"tem 90 migrations e RLS → vale um agente de dados"*.
**Menos agentes bem definidos > muitos genéricos.** Se o projeto já tem agentes bons, **reaproveite**:
mapeie-os aos papéis em vez de duplicar.

Para cada papel adicional decida:
- `model` — trabalho difícil (plano, review) pede modelo forte; tarefa mecânica, um menor.
- `tools` — **mínimo necessário**. Quem revisa é **read-only** (sem Edit/Write). Só quem implementa escreve.
- quando é chamado e o que entrega.

**Proponha o ELENCO** (`memory/wiki/_elenco.md`) — qual LLM toca cada papel. Sugira uma escalação e
deixe claro que ele pode mudar depois com `/orq:elenco planner fable`, ou trocar o **time inteiro**
por contexto de crédito com `/orq:elenco perfil economia` — o arquivo já nasce com esse conceito
(seção "Perfis", ver FASE 4). Identifique também o host atual e proponha a linha correspondente em
`## Times por host`; fora do Claude, não use a tabela `## Papéis` como se fosse universal.

**Estratégia de leitura** (o que economiza contexto neste projeto):
- Repo grande → busca semântica primeiro; indexar se ainda não estiver.
- Saída volumosa (testes, logs, git) → context-mode.

**Stack complementar.** Do que faltou no levantamento de ferramental, proponha só o que se paga *neste* projeto — o
`stack.md` traz o filtro (projeto pequeno não precisa de camada 3; o que exige chave só com ganho
claro). Uma linha por ferramenta: o que resolve · ganho aqui · custo · repositório oficial.

⚠️ **Antes de propor qualquer coisa, leia a seção "Dispensadas" de `memory/wiki/_stack.md`** (se
existir) e **corte o que ele já recusou**. Vale principalmente no `--reinstalar`: repropor o que o
dono dispensou é o jeito mais rápido de ele desligar isto.

**Páginas de wiki iniciais:** 1 a 3 dos subsistemas mais quentes. Não faça backfill especulativo —
a wiki cresce com o uso.

## FASE 3 — Propor e ESPERAR

Apresente ao dono, curto e escaneável:
- o que você entendeu do projeto (2–3 linhas — ele corrige se você errou);
- o **time proposto** (papel · modelo · por que existe aqui);
- o que será criado/alterado (com destaque para o que **altera arquivo existente**);
- backlog inicial que você encontrou;
- **statusline:** a folha achada (F1-F3 — ver FASE 4, passo 4) e, se F2, o que exatamente será
  tocado (inclusive se há barra sombreada por baixo — ver pergunta 4); se F3 **confirmada e a barra
  não mostra o board**, mostre o bloco de exemplo e diga que o init não vai editar o script; se F3
  **provisória** (board ainda não existe neste projeto — ver FASE 1), diga que a confirmação
  definitiva só sai depois de a FASE 4 criar o board, e que de qualquer forma nada será escrito — F3
  nunca escreve.

**Faça as decisões dele em UMA interação, não em várias.** Use `AskUserQuestion` com as perguntas
juntas:

1. **Instalar o Orquestra** com esse time e essa memória? (ajustes do time entram aqui)
2. **Revisores no painel** — só Claude, ou Claude + os externos **que já existem nesta máquina**?
3. **Instalar a stack complementar** que falta? — listada à parte, e ele pode recusar inteira sem
   afetar o resto.
4. **Statusline** — só entra na lista se a investigação classificou F1 ou F2. Se caiu em F3, não há
   pergunta: mostrando o board, é "não fazer nada"; não mostrando, é relatar e mostrar o bloco de
   exemplo na FASE 4 — nenhum dos dois precisa de aprovação, porque nenhum escreve nada. Conteúdo por
   folha que pergunta:
   - **F1 (instalar):** pergunte se instala a barra completa do Orquestra e, respondendo sim, em que
     escopo — só este projeto (padrão) ou todos os projetos desta máquina. Escolhendo "todos os
     projetos", a aprovação **tem que nomear os arquivos** que serão tocados
     (`~/.claude/settings.json` e o par `statusline.sh` + `kanban-status.sh` em `~/.claude/orq/`).
   - **F2 (instalação nossa defeituosa):** mostre o caminho exato de hoje (arquivo de settings +
     comando) **e se há barra sombreada por baixo** (escopo de precedência menor com `statusLine`
     próprio, apontando para um script que **não** é do plugin — se a sombreada **também** aponta
     pro plugin, ela não conta para este fim; ver achado 3 na FASE 4). **Havendo sombreada nesse
     sentido:** diga qual é e ofereça as **duas alternativas nominais** — **remover** a chave
     defeituosa (a sombreada volta a valer, e continua acompanhando as edições futuras do dono nela,
     sem virar cópia de projeto) ou **migrar** (a operação exata: substituir o `command` daquele
     mesmo arquivo pela cópia nova de `${CLAUDE_PLUGIN_ROOT}/scripts/statusline.sh`, copiada para o
     destino do escopo, com stamp, no mesmo escopo da chave legada: projeto ou usuário). **Sem
     sombreada nesse sentido** (nenhuma por baixo, ou a que existe também aponta pro plugin), só a
     migração faz sentido — pergunte só ela, com a mesma operação exata. **Sempre nominal**: um "sim"
     geral às perguntas 1-3 não autoriza nenhuma das duas.

   **Nenhuma escrita em F2 sem essa aprovação**, mesmo que as perguntas 1-3 tenham sido aprovadas em
   bloco: um "sim" geral ao instalar o Orquestra não autoriza tocar uma statusline que já existe e
   funciona.

⚠️ **A 2 e a 3 são perguntas distintas, nunca a mesma.** Quem já tem o `codex` instalado e não quer
instalar mais nada responde "não" para a 3 — e isso **não** pode desligar um revisor que ele já
possui. Soldar as duas grava um `_elenco.md` sem painel num ambiente que tinha painel, e o
`/orq:revisar` cai silenciosamente para um revisor só.

⚠️ **A 1 não autoriza a 3.** Instalar arquivos no projeto dele é reversível; instalar software na
máquina dele não é. Se ele não se pronunciou sobre a stack, siga a FASE 4 **sem ela**.

**PARE e espere.** Nada é escrito antes da resposta.

## FASE 4 — Instalar

1. **Memória** (só o que faltar — **nunca sobrescrever o que existe**):
   `memory/MEMORY.md` (índice) · `memory/fixes-history.md` (log) · `memory/gotchas.md` ·
   `memory/wiki/KANBAN.md` (board, com o backlog real que você achou) · `memory/wiki/threads/` ·
   `memory/wiki/_schema.md` (o contrato — passo 1b) · as páginas de tópico aprovadas.

   **Já existe algo com essa função em OUTRO caminho?** (ex.: `MEMORY.md` na raiz, `NOTES.md`,
   `docs/estado.md`) → **preserve o conteúdo onde está** e crie `memory/MEMORY.md` como **ponteiro**
   de poucas linhas para ele ("o índice deste projeto mora em `../MEMORY.md`"), listando o que existe
   em `memory/`.

   ⚠️ **`memory/MEMORY.md` tem que existir de qualquer jeito** — `orq-planner`, `/orq:wiki-lint` e
   `/orq:checkpoint` procuram nesse caminho fixo e falham calados se ele não estiver lá. Ponteiro
   resolve os dois lados: nada é duplicado (dois índices concorrentes é o problema que a wiki existe
   pra evitar) e os consumidores continuam achando o caminho canônico.

1b. **`memory/wiki/_schema.md` — o contrato da memória.** Crie sempre. É o que o `/orq:checkpoint`
   e o `/orq:wiki-lint` procuram, e é o que impede o board de sair num formato que a statusline não
   lê. Deve conter, no mínimo, **o formato exato da linha de card**:

   ```markdown
   ## Formato do board (contrato — não improvise)

   Card, exatamente assim:

       - [ ] `T-001` Título curto — nota livre depois do travessão

   - o marcador é o 4º caractere e só pode ser um destes seis: `[ ]` BACKLOG · `[>]` PLANNING ·
     `[!]` AWAITING_OWNER · `[~]` READY/DEV_REVIEW · `[?]` VALIDATE · `[x]` DONE;
   - o ID vem **entre crases**, logo depois do marcador — é ele que distingue card de checklist;
   - o título vai até o primeiro travessão `—`;
   - **nada de negrito ou crase envolvendo o marcador ou o ID**, e **sem indentação**;
   - **só card usa `- [` na coluna 0** — item de processo solto não é card;
   - uma seção cujo título case com `## …arquiv…` **encerra a contagem** de progresso.

   ## Regras da wiki
   - o LOG (`fixes-history.md`) é append-only: responde "o que aconteceu naquele dia";
   - a PÁGINA de tópico é reescrita: responde "como funciona hoje";
   - não guardar o derivável (diff, git log, schema): guardar o porquê.

   ## Trabalho em várias janelas
   Uma janela = uma FRENTE; nunca duas janelas na mesma frente.
   1. releia antes de escrever — o disco pode ter mudado;
   2. edite só as linhas dos seus cards, nunca reescreva o board inteiro;
   3. card em curso leva `@frente` no fim da nota;
   4. trabalho em curso mora em `threads/<frente>.md` (dono único, sem conflito).
   Pendência de decisão do dono → card `[!]` com a pergunta exata + "RETOMAR AQUI" na thread.
   Aí a janela **pode fechar**: manter janela viva só pra não esquecer é usar contexto como memória.
   ```

   Se o dono trabalha em uma janela só, o bloco "várias janelas" não atrapalha — ele só entra em
   ação quando houver mais de uma frente.

   ⚠️ **O formato acima não é estilo, é contrato.** `orq/scripts/kanban-status.sh` casa
   `` /^- \[[ >!~?x]\] `[^`]+`/ `` — marcador estrito **e** ID entre crases — e extrai o título entre
   a crase do ID e o travessão. Negrito ou crase **envolvendo** o marcador ou o ID não casa: a linha
   sai da contagem e aparece como `⚠N` no fim. O `⚠` é o aviso — **o número que engana é o
   denominador**, que encolhe sem alarde. Por isso o smoke test compara a contagem manual.

2. **Agentes** — os cinco do núcleo vêm do plugin, **não recrie**. Em `.claude/agents/`, só os papéis
   adicionais aprovados, com nome próprio (nunca `orq-*`) e `model`/`tools` decididos. Não duplique o
   que o projeto já tem; complemente.
2b. **Elenco** em `memory/wiki/_elenco.md` — a escalação aprovada (papel → modelo) + os revisores
   externos ativos, **gerado a partir do template "Modelo do arquivo" de
   `${CLAUDE_PLUGIN_ROOT}/commands/elenco.md`**
   (traz de fábrica `## Matriz de invocação`, `## Times por host`, a linha "Perfil ativo" e a seção
   "Perfis" com `padrao`/`economia` prontos — ajuste só os modelos e a nota de "o que se perde" à
   realidade deste projeto). Não crie um `_elenco.md` só com a tabela de papéis: o projeto nasce
   **já** com o conceito de perfil e resolução por host, não como um recurso que só aparece se
   alguém pedir depois. É esse arquivo que os comandos leem na hora de spawnar.

   `_elenco.md` já existe? Leia o arquivo inteiro, preserve modelos/perfis/revisores escolhidos e
   acrescente somente headings obrigatórias ausentes. Se `## Matriz de invocação` ou `## Times por
   host` existe mas está incompleta, mostre o diff e pare no gate; não substitua linha existente sem
   aprovação explícita.
3. **`CLAUDE.md` e `AGENTS.md`** — os dois arquivos saem **byte-idênticos, do primeiro ao último
   caractere — não só o bloco.** É decisão do dono: *"o agent MD tem que ter o mesmo conteúdo do
   Claude MD"*; `diff CLAUDE.md AGENTS.md` tem que voltar vazio, arquivo inteiro, não só o bloco.
   **No repositório deste plugin**, `lint-coerencia.py` também aplica isso como gate mecânico (falha
   se os dois divergirem, ou se só um dos dois existir); em outro projeto-alvo o lint não roda (exige
   `orq/.claude-plugin/plugin.json` na raiz) — o `diff` acima é a própria verificação.
   Grave (ou atualize) o bloco `<!-- orquestra:start -->…<!-- orquestra:end -->` nos dois —
   **criando o `AGENTS.md` se ele não existir**, como cópia do `CLAUDE.md` resultante — com o
   ciclo, onde vive a memória, quem move o board, e as convenções do projeto que você descobriu
   (build, teste, o que quebra o deploy). Se algum dos dois já tinha conteúdo fora do bloco antes
   deste `/orq:init` (ex.: uma instrução pensada só para um host), **não deixe os arquivos
   divergirem por causa disso**: incorpore esse trecho ao texto comum como uma seção que se
   endereça por identidade a quem lê ("Se você é um revisor externo entrando pelo painel…", "Se
   você é o Codex/Kimi rodando este projeto…") — conteúdo condicional na leitura, nunca conteúdo
   que só existe num dos dois arquivos — e grave a mesma versão,
   completa, nos dois arquivos. Nada de ponteiro ("leia o outro arquivo") e nada de "cada um guarda
   o seu resto" — é o mesmo conteúdo, inteiro, nos dois.
4. **Statusline.** A checagem "não sobrescreva" tem que ver os três escopos, não só o do projeto:
   settings de projeto vencem o global por precedência, e gravar chave nova onde já existe uma no
   escopo de cima **é** sobrescrever, mesmo que o diff seja só aditivo — já aconteceu de verdade,
   duas vezes, em projetos deste dono. Este passo executa o que a FASE 1 já investigou e a FASE 3 já
   aprovou — **não abre pergunta nova aqui.**

   **Regras invioláveis desta seção:**
   - **R1** — "existe statusline" = chave `statusLine` presente em **qualquer** um dos três
     arquivos (`.claude/settings.local.json`, `.claude/settings.json`, `~/.claude/settings.json`);
     o de maior precedência presente é o **efetivo** (Local > Projeto > Usuário).
   - **R2 (emendada)** — havendo statusline em qualquer escopo, **nenhuma chave é ADICIONADA em
     escopo nenhum**. As únicas escritas de settings permitidas com statusline já existente
     acontecem **no mesmo arquivo** onde a chave defeituosa mora, só na folha **F2** (abaixo), com
     aprovação nominal, e só depois de testar a cópia nova (ou a barra revelada) isoladamente, com
     backup do settings anterior e restauração atômica se a verificação pós-troca falhar (achado D2,
     rodada 3 — validar o JSON antes do `mv` prova só que o arquivo é JSON válido, não que a
     configuração nova funciona): **substituir o valor** da chave efetiva (procedimento de migração)
     **ou remover a chave inteira** quando há barra sombreada por baixo (procedimento de remoção,
     achado do painel final — ver F2 abaixo). Nunca as duas ao mesmo tempo, e nunca fora de F2. A
     folha **F3 nunca escreve nada** — nem settings, nem script: o que ela faz de mais ativo é
     relatar e mostrar um bloco de exemplo.
   - **R3** — nunca gravar em settings um caminho para dentro do plugin (cache ou repositório). O
     executável referenciado é sempre uma **cópia** instalada fora do plugin.
   - **R4** — este comando escreve dentro do projeto por padrão. `~/.claude/` só é tocado em **dois
     ramos nomeados**, sempre com aprovação nominal citando cada arquivo: (a) F1 no escopo usuário;
     (b) F2 quando a chave legada já vive no escopo usuário (migra no mesmo escopo em que já estava
     — nunca muda escopo por conta própria). **Correção C1 da rodada 3, preservada:** uma versão
     anterior desta regra nomeava só (a) e fechava com "fora deste ramo, `~/.claude/` nunca é escrito
     por este comando" — uma frase absoluta que a folha F2 (abaixo) sempre contrariou na prática,
     sempre que a chave legada já morava no escopo usuário. Nomear F2 aqui fecha a contradição sem
     mudar o que F2 já fazia.

   **Onde checar (sempre, em todo `/orq:init` — não só `--reinstalar`):** leia `statusLine` nos três
   arquivos e monte a visão completa (qual escopo tem a chave, qual é o efetivo, quais ficam
   sombreados) — é o mesmo levantamento que a FASE 1 já fez e registrou como o "antes" da FASE 5;
   este passo só executa o que já foi classificado e aprovado.

   **A árvore — três folhas mutuamente exclusivas, avaliadas nesta ordem, parando na primeira que
   casar. Nenhuma folha é modificador de outra — é essa ausência de interseção que corrige os
   bloqueadores das duas rodadas de painel anteriores.**

   **Guarda de destino ocupado (achado 7 do painel; correção C3 da rodada 3) — vale para TODA cópia
   de `statusline.sh`/`kanban-status.sh` feita por este passo, em qualquer folha que copie (F1, F2),
   não só em F1:** antes de copiar, se o
   destino (`.claude/statusline.sh`, `.claude/kanban-status.sh`, ou os pares em `~/.claude/orq/`) já
   existir **sem** o nosso stamp na linha 2 → pare e relate (é arquivo de alguém — não sobrescreva;
   cai no fallback: mostrar o que faltaria fazer e por quê); **com** stamp → recopiar é re-sync
   legítimo. Destino sob controle de versão do projeto → diga isso na proposta. Esta guarda roda **no
   momento da cópia, dentro de cada folha** — ela não depende de nenhuma outra folha "pegar depois":
   um projeto classificado F2 nunca reavalia F1 no próximo `/orq:init` (a chave legada continua lá
   até alguém migrar), então uma guarda que só existisse em F1 nunca protegeria a cópia que F2 faz.

   - **F1 — Não há `statusLine` em escopo nenhum → instalar.** A aprovação e a escolha de escopo já
     vieram da pergunta 4 da FASE 3. Instale **sempre o par completo**
     `orq/scripts/statusline.sh` + `orq/scripts/kanban-status.sh`, nunca um sem o outro — inclusive
     sem `jq` na máquina: o `statusline.sh` degrada sozinho para board-only sem `jq` (guarda já
     embutido no script) e **se completa sozinho, sem re-run**, quando `jq` aparecer depois (Decisão
     12 — o ramo "sem jq" separado morreu: instalava só o kanban e mandava "instale jq e rode
     `--reinstalar`", mas o `--reinstalar` classificaria isso como F3 e não faria nada — beco sem
     saída do achado 4 do painel).

     Aplique a guarda de destino ocupado (acima) antes de copiar.

     - *Escopo projeto (padrão):* copie o par para `.claude/` do projeto (`chmod +x` nos dois, com
       o stamp de versão — ver abaixo).
     - *Escopo usuário (só quando o dono escolheu "todos os projetos" na pergunta 4 da FASE 3, com
       aprovação separada nomeando os arquivos):* par em `~/.claude/orq/` (diretório próprio, não
       colide com nada que o dono já tem; `chmod +x` nos dois, com o stamp). Este é um dos dois
       ramos nomeados em R4 — o outro (F2 em escopo usuário) está descrito na folha correspondente,
       abaixo.

     **Toda escrita de settings desta folha é merge, nunca overwrite do arquivo inteiro:** o
     arquivo-alvo (`.claude/settings.local.json` ou `~/.claude/settings.json`) pode já existir com
     outras chaves do dono (`permissions`, `hooks`, `env`) sem ter `statusLine` — é justamente por
     não ter `statusLine` que caiu em F1. Leia o JSON existente (se o arquivo existir), acrescente
     **só** a chave `statusLine` preservando as demais intactas, e **aborte e relate — não escreva
     nada** — se o JSON existente for inválido.

     - **Com `jq`** (`command -v jq`): forma **obrigatória** — nunca `jq '...' arquivo > arquivo` (o
       shell abre o redirect antes de o `jq` ler; trunca o arquivo para 0 byte, achado 2 do painel).
       **O ramo é escolhido por `[ -s arquivo ]` (existe E tem conteúdo), nunca só por `[ -f
       arquivo ]`** (achado do painel final: um `arquivo` de 0 byte é exatamente o rastro que o bug
       do achado 2 deixa para trás — quem já apanhou dele tem o arquivo nesse estado. Tratar "existe
       vazio" como "existe com conteúdo" fazia `jq '. + {...}' arquivo` produzir 0 byte com `exit 0`,
       a validação seguinte sobre um `arquivo.tmp` também vazio **também** sair com 0, o `mv` seguir,
       e nenhuma `statusLine` ser criada sem que nada acusasse — o mesmo risco vale para raiz `null`,
       que `. + {...}` converteria em objeto silenciosamente, e para raiz lista ou string, que faz o
       `jq` falhar sem desfecho escrito se isso não for checado à parte):
       ```sh
       if [ -s arquivo ]; then
         jq -e 'type == "object"' arquivo >/dev/null \
           || { echo "abortado: arquivo de settings não pôde ser lido como JSON (malformado) ou a raiz não é um objeto (null/lista/string) — nada escrito. Corrija o arquivo à mão (ou restaure de um backup) e rode /orq:init de novo." >&2; exit 1; }
         modo=$(stat -f%Lp arquivo 2>/dev/null || stat -c%a arquivo)
         jq '. + {statusLine: {"type":"command","command":"sh \"<abs-do-destino>/statusline.sh\"","padding":0}}' arquivo > arquivo.tmp \
           && jq -e 'type == "object" and (.statusLine | type == "object")' arquivo.tmp >/dev/null \
           && mv arquivo.tmp arquivo
         [ -n "$modo" ] && chmod "$modo" arquivo
       else
         # arquivo ausente OU existe vazio (0 byte) — nada a preservar nos dois casos; grava o
         # objeto direto (`>` sobre um arquivo vazio já existente preserva o próprio modo do
         # inode, sem precisar de chmod à parte).
         jq -n '{statusLine: {"type":"command","command":"sh \"<abs-do-destino>/statusline.sh\"","padding":0}}' > arquivo
       fi
       ```
       Valida o JSON resultante **antes** do `mv` com `type == "object" and (.statusLine | type ==
       "object")` — não `jq . arquivo.tmp` sozinho, que só prova "é JSON válido" e passa até com
       saída vazia (achado do painel: exatamente o caso do arquivo de 0 byte tratado como se tivesse
       conteúdo). Arquivo ausente ou vazio → grava direto, sem checagem de raiz (não há nada a
       validar); arquivo **não-vazio** malformado, ou com raiz `null`/lista/string → **aborta e
       relata, não escreve**, com o motivo nomeado e o próximo passo (corrigir à mão ou restaurar
       de um backup); qualquer falha na validação de saída → mesma coisa.
     - **Sem `jq`:** arquivo-alvo ausente ou vazio → grave o objeto completo direto (é JSON
       conhecido, um `cat`/`printf` basta); arquivo existe com conteúdo → **não edite JSON sem
       `jq`** — mostre a chave a acrescentar e relate, mesmo padrão de relato sem escrita de F3.
       **Nunca instale `jq` por conta própria** (regra do `/orq:stack` — política preservada da
       Decisão 9/12).

     Comando gravado: `sh "<abs-do-destino>/statusline.sh"` — o caminho é sempre absoluto e local
     desta máquina; `${CLAUDE_PLUGIN_ROOT}` resolve ao copiar (este passo roda dentro do plugin
     instalado) mas **nunca** entra na chave gravada (o cache muda a cada update — R3).

   - **F2 — A chave efetiva aponta DIRETAMENTE para dentro do plugin → instalação nossa, defeituosa;
     propor reinstalação.** Critério — **só o alvo diretamente invocado pelo `command`** (resolvido
     descartando prefixos de variável — `NOME=valor` — no início do comando, achando o interpretador
     — `sh`, `bash` ou `zsh` — e isolando um único arquivo de script, com symlink resolvido) —
     **nunca o que esse arquivo eventualmente chama por dentro**: o caminho resolvido está dentro de
     `plugins/cache` (cache do plugin) ou é um `orq/scripts/<nome>` fora deste projeto (repositório do
     plugin, em vez de uma cópia).
     ⚠️ **Correção D1, rodada 3 (revisor Codex):** a versão anterior deste critério dizia "o `command`
     (**ou o script que ele invoca**)" — isso fazia uma barra de terceiro que roda seus próprios
     segmentos e, por dentro, chama `plugins/cache/.../kanban-status.sh` para o board casar F2 **e**
     F3 ao mesmo tempo; a ordem escolhia F2 e **descartava a barra alheia inteira** ao substituir o
     `statusLine`. Restringir ao alvo direto fecha a interseção: um wrapper alheio que só referencia
     nosso script por dentro nunca é F2 — cai em F3, que trata tanto "já mostra" quanto "não mostra"
     (o critério de F3, abaixo, esse sim segue o caminho por dentro para confirmar o board).
     Avaliada **antes** de F3 de propósito, para o caso em que o alvo direto É nosso: mostrar o board
     hoje não livra de quebrar no próximo update (o cache é indexado por versão — ver
     `arquitetura.md`) — o script É o nosso próprio `kanban-status.sh` do cache, então esse caso nunca
     cai para F3 mesmo quando o board aparece hoje.

     ⚠️ **Achado do painel final — verifique o que está sombreado por baixo antes de propor.** Releia
     os três escopos (já feito na FASE 1): se existir `statusLine` em escopo de precedência **menor**
     do que o efetivo defeituoso (ex.: a chave de projeto que caiu em F2 está sombreando uma barra
     global legítima do dono, em `~/.claude/settings.json`), **migrar não é a única resposta nem
     necessariamente a certa** — foi exatamente **remover** a chave de projeto, não migrar, que
     resolveu os dois projetos reais que originaram este card (o Manager aplicou à mão). Migrar sem
     avisar deixa o dono aprovar achando que desfaz o estrago, e ele sai com uma **cópia de projeto
     que nunca mais acompanha as edições futuras da barra global dele**.

     ⚠️ **Achado 3 — a sombreada também precisa passar pela checagem de procedência, com o mesmo
     critério de F2** (alvo diretamente invocado, resolvendo prefixo de variável, interpretador e
     symlink): se ela **também** aponta para dentro do plugin, remover não resolve nada — só troca
     uma instalação defeituosa por outra que ainda não foi pega (plausível e já visto: dois projetos
     deste dono chegaram a ter as duas apontando pro cache). Esse caso não conta como "sombreada"
     para efeito da alternativa de remover; ele cai em "Chaves sombreadas apontando para dentro do
     plugin" (abaixo) — pendência relatada, e o caminho aqui é **migrar**, nunca remover.

     Por isso: havendo sombreada **que não aponta pro plugin**, a pergunta 4 da FASE 3 nomeia as
     **duas alternativas** — remover ou migrar (ver FASE 3); sem sombreada por baixo, ou com a
     sombreada também apontando pro plugin, só migrar faz sentido.

     **Procedimento de MIGRAÇÃO (aprovação nominal na pergunta 4 — um "sim" geral às perguntas 1-3
     não autoriza; recusado ou não perguntado → mantém a instalação legada e relata o risco de novo
     no próximo `/orq:init`):**
     1. Copiar o par `${CLAUDE_PLUGIN_ROOT}/scripts/statusline.sh` +
        `${CLAUDE_PLUGIN_ROOT}/scripts/kanban-status.sh` para o destino do **mesmo escopo** em que a
        chave legada vive hoje (`.claude/` do projeto se a chave é de projeto; `~/.claude/orq/` se é
        de usuário — nunca muda o escopo por conta própria), com stamp. Aplique a **guarda de
        destino ocupado** (acima) antes de copiar — a cópia em si é sempre arquivo nosso, conhecido,
        mas o que já pode estar **naquele caminho** não é.
     2. **Testar a cópia nova antes de tocar em settings (achado D2, rodada 3):** `echo
        '{"workspace":{"project_dir":"<abs-do-projeto>"}}' | sh <cópia-nova>/statusline.sh` — exigir
        `exit 0` e saída contendo `📋` ou `⚠`. Falhou → **não mexa em settings**; relate a falha da
        cópia nova e mantenha a instalação legada intacta.
     3. **Backup do settings antes de escrever (achado D2):**
        `cp -p arquivo arquivo.orq_bak.$(date +%Y%m%d-%H%M%S)` — nunca apagado por nós. **Achado do
        painel final — se `arquivo` está sob controle de versão do projeto**
        (`git ls-files --error-unmatch arquivo`), diga isso **na proposta da pergunta 4**, com todas
        as letras: o `command` novo grava um **caminho absoluto local desta máquina** (linha
        "Comando gravado", acima) — nada que sobreviva a um `git pull` de um colega — e o backup
        nasce **no mesmo diretório versionado**, sujeito a acabar commitado junto. A aprovação
        nominal cobre esse risco também, não só a troca do valor.
     4. Substituir — **nunca adicionar** — o **valor inteiro** da chave `statusLine` existente
        **nesse mesmo arquivo** de settings (é a exceção nomeada em R2 emendada), com a mesma forma
        segura de F1 (nunca `jq '...' arquivo > arquivo` — o shell trunca o arquivo antes de o `jq`
        ler, achado 2 — e preservando o modo original, achado C8):
        ```sh
        modo=$(stat -f%Lp arquivo 2>/dev/null || stat -c%a arquivo)
        jq '.statusLine = {"type":"command","command":"sh \"<abs-do-destino>/statusline.sh\"","padding":0}' arquivo > arquivo.tmp \
          && jq . arquivo.tmp >/dev/null \
          && mv arquivo.tmp arquivo
        [ -n "$modo" ] && chmod "$modo" arquivo
        ```
        Valida o JSON resultante **antes** do `mv`; falhou a validação → aborte e relate, não escreva
        — a instalação legada continua valendo até o próximo `/orq:init`.
     5. **Verificação pós-troca, antes de dar por concluído (achado D2):** repita o smoke do passo 2
        contra o arquivo já trocado. Passou → relate o sucesso. **Falhou → restaure atomicamente**:
        `cp -p arquivo.orq_bak.<ts> arquivo.tmp2 && mv arquivo.tmp2 arquivo` (nunca `cp -p` direto por
        cima do arquivo — janela de conteúdo parcial), confirme com
        `cmp arquivo.orq_bak.<ts> arquivo` que a restauração é byte-idêntica, e relate: a cópia nova
        estava funcionando isoladamente (passo 2) mas a troca não se sustentou; a instalação legada
        foi restaurada, nada quebrou.

     **Procedimento de REMOÇÃO (alternativa a migrar, só quando há barra sombreada por baixo, e só
     com aprovação nominal na pergunta 4 — a outra alternativa nomeada acima):**
     1. **Backup do settings antes de escrever:** `cp -p arquivo arquivo.orq_bak.$(date
        +%Y%m%d-%H%M%S)` — nunca apagado por nós; mesma nota do passo 3 da migração se `arquivo`
        estiver sob controle de versão do projeto.
     2. **Remover — nunca zerar o valor** — a chave `statusLine` inteira daquele arquivo, com a
        mesma forma segura (nunca `jq '...' arquivo > arquivo`):
        ```sh
        modo=$(stat -f%Lp arquivo 2>/dev/null || stat -c%a arquivo)
        jq 'del(.statusLine)' arquivo > arquivo.tmp \
          && jq -e 'type == "object" and (has("statusLine") | not)' arquivo.tmp >/dev/null \
          && mv arquivo.tmp arquivo
        [ -n "$modo" ] && chmod "$modo" arquivo
        ```
        Valida o JSON resultante **antes** do `mv`; falhou a validação → aborte e relate, não
        escreva — a instalação legada continua valendo até o próximo `/orq:init`.
     3. **Verificação pós-remoção, antes de dar por concluído — não reutilize o critério da
        migração.** A barra que passa a valer agora é **do dono**, não uma cópia nossa: ela **não
        tem obrigação nenhuma** de mostrar o board, então "`exit 0` e saída com `📋`/`⚠`" (o smoke do
        passo 2 da migração) é o critério errado aqui — foi exatamente essa confusão que, no
        incidente real deste card, devolvia a chave defeituosa depois de uma remoção correta.
        Confira, em vez disso:
        - a chave `statusLine` **não existe mais**: `jq -e '(has("statusLine") | not)' arquivo` sai
          `0`;
        - **as demais chaves continuam intactas**: `jq 'keys' arquivo` antes/depois do passo 2 dá o
          mesmo conjunto **menos** `statusLine`;
        - a barra agora efetiva (a que estava sombreada) **executa**: resolva o interpretador do
          `command` dela (mesma resolução que F2/F3 já fazem — descartar prefixo `NOME=valor`, achar
          `sh`/`bash`/`zsh` no início do comando) e rode **exatamente esse comando** — **nunca force
          `sh <alvo>`** (é a mesma proibição de F3, pelo mesmo motivo: uma barra Bash com arrays
          funciona pelo `command` configurado e falha sob `sh` forçado). Com o mesmo stdin de
          sempre, exigir só `exit 0` **e saída não-vazia**. A presença de `📋`/`⚠` é **relato**,
          nunca condição de sucesso — a barra revelada não tem obrigação de mostrar o board.

        Passou (exit 0, saída não-vazia) → relate o sucesso: "a chave defeituosa foi removida; a
        barra que estava sombreada voltou a valer" — e diga, à parte e sem reprovar nada, se ela
        mostra ou não o board. **Falhou** (a barra revelada não roda, ou o comando não resolve) →
        **isso não desfaz a remoção nem justifica restaurar a chave defeituosa**: a escrita da
        remoção já foi validada no passo 2 (JSON íntegro, chave ausente, `mv` concluído); o defeito é
        da barra do dono, não deste comando, e uma chave que aponta para dentro do plugin nunca volta
        por causa de um script alheio quebrado. Relate o comando que falhou e o motivo, com o backup
        do passo 1 disponível caso o dono prefira agir à mão. Restauração atômica só existiria se a
        **própria escrita do passo 2** não se sustentasse — mas esse caso já aborta **antes** do
        `mv` (validação de JSON), então não há cenário em que este passo precise desfazer um `mv`
        que já rodou.

   - **F3 — Qualquer outra barra efetiva (não é F2) → nunca editar; relatar.** Critério em duas
     partes, as duas obrigatórias (achado C7, rodada 3 — o texto sozinho não prova nada por si:
     sobrevive a alguém apagar a cópia do `kanban-status.sh` meses depois, e a string continua lá):
     **(a) sinal textual** — o `command`, ou o script que ele invoca, contém `kanban-status` ou lê
     `KANBAN.md` (siga o caminho e confira o conteúdo); **e (b) confirmação por execução** — execute
     **exatamente o `command` configurado**, preservando interpretador, argumentos e ambiente
     (reaproveite a resolução de interpretador que F2 já faz — descartar prefixos `NOME=valor`,
     reconhecer `sh`/`bash`/`zsh` no início do comando — em vez de reinventar). **Nunca force `sh
     <alvo>` por conta própria**: uma barra Bash com arrays, por exemplo, funciona pelo `command`
     configurado e falha sob `sh` — o init relataria "não mostra o board" por um motivo que não
     existe. Com o stdin `echo '{"workspace":{"project_dir":"<abs-do-projeto>"}}'`, mesmo `cwd` deste
     projeto, confira que a saída contém `📋` ou `⚠`.

     ⚠️ **Classificação provisória da FASE 1** (o board não existia até aqui): repita (b) agora — o
     passo 1 desta fase já criou `memory/wiki/KANBAN.md`, então esta é a primeira vez que a
     confirmação por execução tem uma saída real para conferir. É só esse resultado, e não o da
     FASE 1, que entra no relato final. Nada é escrito por essa reconfirmação — F3 nunca escreve.

     **Passando nas duas → relate "sua statusline já mostra o board".** Não fazer nada. É a folha em
     que a máquina deste dono cai hoje, em todo projeto dele. (O `--reinstalar` também verifica drift
     dessa cópia — inclusive sem stamp — ver Regras, abaixo.)

     **Falhando qualquer uma das duas** (string ausente, ou presente sem confirmar por execução, ou
     o comando não resolve/não roda) **→ a barra não mostra o board hoje. O init não edita o script
     de terceiros — relate isso, sempre, sem prometer conserto futuro** e mostre o bloco que a pessoa
     pode acrescentar por conta própria, ajustando ao seu script:
     ```sh
     # Kanban do projeto (memory/wiki/KANBAN.md) — vazio se não houver quadro
     kanban_str=""
     if [ -r "<caminho-de-uma-cópia-de-kanban-status.sh>" ]; then
       kanban_str=$(sh "<mesmo-caminho>" "$PWD" 2>/dev/null)
     fi
     [ -n "$kanban_str" ] && kanban_str=" | ${kanban_str}"
     ```
     Diga que `${CLAUDE_PLUGIN_ROOT}/scripts/kanban-status.sh` pode ser copiado para um caminho
     estável fora do plugin (nunca aponte para dentro do plugin no script dela — R3) e usado no lugar
     do placeholder. Cite em uma linha que a barra completa do Orquestra (F1) existe como alternativa
     — **nunca** proponha substituir a statusline dela. Nenhuma escrita acontece neste ramo: nem em
     settings, nem no script.

   **Chaves sombreadas** (um escopo de menor precedência também tem `statusLine`, mas não é o
   efetivo): **relato, nunca ação** — nem editar, nem substituir um script que não está valendo.
   Sombreada apontando para dentro do plugin → relate como pendência, com o comando manual de
   conserto, sem aplicar nada (fecha a interseção "legado que não é o efetivo" que a rodada 2 do
   painel encontraria).

   **Totalidade (por que nenhum estado fica sem folha):** F1 cobre "sem chave em escopo nenhum". Com
   chave, um único predicado binário decide entre F2 e F3 — procedência **do alvo diretamente
   invocado** (aponta para dentro do plugin? — não o que esse alvo chama por dentro, correção D1):
   sim → F2; qualquer outra coisa → F3. Dentro de F3, um segundo teste (sinal textual + confirmação
   por execução, correção C7) decide só **o que relatar** — "já mostra" ou "não mostra, aqui está o
   bloco" — nunca abre uma folha nova: script inexistente, ilegível, comando inline, statusline
   noutra linguagem — tudo isso é F3 (não aponta para dentro do plugin) e recebe o mesmo relato "não
   mostra o board", sem exigir que o init entenda a arquitetura do script alheio. Nenhuma folha
   depende do resultado de outra.

   **Marca de versão, sempre que este passo copiar `statusline.sh` e/ou `kanban-status.sh`** (F1 em
   qualquer escopo, ou F2 aplicado): insira como linha 2, logo após o shebang, em cada cópia:
   `# orq v<versão> — instalado por /orq:init em <AAAA-MM-DD>; fonte: orq/scripts/<nome>. Não editar à mão; re-sync: /orq:init --reinstalar`
   A fonte em `orq/scripts/` **não** leva esse stamp — só a cópia, no momento em que é feita.

   **Idempotência:** rodar de novo cai em F3 (a barra instalada contém `kanban-status`) — nada
   duplica.
5. **Stack complementar.** Instale **só o que ele aprovou explicitamente**, seguindo as regras do
   `/orq:stack` (instruções lidas no repositório oficial e mostradas a ele antes de rodar, nada com
   chave sem ele fornecer; plugin do Claude Code entra pela **CLI** — `claude plugin marketplace add`
   + `claude plugin install <plugin>@<marketplace>` —, nunca pelo slash command, que você não invoca).

   ⚠️ **Grave `memory/wiki/_stack.md` SEMPRE — inclusive quando ele recusa tudo.** Recusar é
   informação tão valiosa quanto aceitar: é ela que vai na seção **Dispensadas** e impede o
   `--reinstalar` de repropor amanhã o que ele acabou de negar. Um `_stack.md` que só nasce quando
   há instalação deixa justamente o caso "não quero nada" sem registro — e esse é o caso em que
   repropor mais irrita.

## FASE 5 — Verificar e confirmar

**Não basta dizer o que fez — prove que funciona.** Rode o smoke test e mostre o resultado:

1. **O board é legível pela statusline?**
   `sh ${CLAUDE_PLUGIN_ROOT}/scripts/kanban-status.sh .` — e confira **os três sinais**, porque
   saída não-vazia **não** prova que está certo:
   - saída **vazia** com cards no board → FALHA: nenhum card foi reconhecido;
   - **`⚠N`** no fim → N linhas parecem card e não casam o contrato;
   - **denominador ≠ número de cards que você escreveu** → alguma linha entrou ou ficou de fora.
     **Conte os cards à mão e compare.** É esse terceiro sinal que pega o erro sutil.

   Qualquer um dos três → corrija o board pelo `_schema.md` e rode de novo antes de seguir.
2. **`CLAUDE.md` e `AGENTS.md` são byte-idênticos?** `diff CLAUDE.md AGENTS.md` tem que voltar
   **vazio** — arquivo inteiro, não só o bloco. (No repositório deste plugin é exatamente o que
   `lint-coerencia.py` confere, inclusive se só um dos dois existir; **neste** projeto-alvo o lint
   não roda — o `diff` acima é a checagem que vale.) O bloco `orquestra:start`/`orquestra:end` está
   fechado corretamente e o conteúdo que existia antes de cada um sobreviveu — mas sobreviveu **nos
   dois**, nunca só num. Divergiu? Corrija antes de seguir.
3. **Os arquivos de memória existem** e o `MEMORY.md` aponta para o que realmente foi criado
   (incluindo índice pré-existente em outro caminho, se for o caso).
4. **Agentes adicionais** (se criou): contagem confere e nenhum tem nome `orq-*`.
5. **Statusline — roda incondicionalmente, em todo `/orq:init`, inclusive em F3.** É o guarda de
   regressão: sem ele, uma classificação errada na FASE 1 (ex.: leu mal um settings e caiu em F1 por
   engano, quando na verdade já havia statusline em outro escopo) não é pega por checagem nenhuma —
   este é o defeito que o card corrige. **A comparação é sempre contra o registro que a FASE 1 já
   gravou** ("antes" dos três escopos) — nunca uma captura nova aqui, depois de a FASE 4 já ter
   escrito. Rode os itens que valem para a folha efetivamente executada; nenhum exige dado que não
   foi mandado capturar antes dele:

   - **Sempre, qualquer folha:**
     - **Se `jq` está disponível** (`command -v jq`): `for f in .claude/settings.local.json
       .claude/settings.json ~/.claude/settings.json; do [ -f "$f" ] && jq '.statusLine' "$f"; done`
       — tolera arquivo ausente (máquina virgem não tem `~/.claude/settings.json`) em vez de abortar
       sem imprimir nada. **Nenhuma chave nova** apareceu em escopo além do que a FASE 1 já
       registrou como existente antes — a única exceção esperada é o próprio escopo que F1 acabou de
       instalar. **Sem `jq`:** confira o mesmo por leitura direta dos três arquivos.
     - **O alvo desta checagem é sempre o `command` EFETIVO** (o que `statusLine` resolve hoje,
       considerando a precedência) — nunca os três arquivos varridos sem distinção: uma chave
       **sombreada** apontando para o plugin nunca é tocada por este comando (a regra é relatar,
       nunca aplicar — ver "Chaves sombreadas", acima) e não pode reprovar o smoke por causa disso.
       - **Se executou F2 (migração):** o `command` efetivo não contém `plugins/cache` nem um
         caminho dentro do repositório deste plugin — é justamente essa substituição que prova o
         item; o comando velho, apontando para o plugin, não pode mais estar lá.
       - **F2 recusada, ou não perguntada porque a chave que apontava para o plugin era sombreada
         (não efetiva):** a proibição acima **não se aplica** — o dono manteve a instalação legada
         de propósito, ou a chave apontando para o plugin nunca foi a que decide. Confira que o
         `command` daquele arquivo permaneceu **byte-idêntico** ao valor que a FASE 1 registrou como
         "antes" e relate o risco de novo (aponta para dentro do plugin, quebra no próximo update)
         — **sem marcar falha do smoke** por isso: uma recusa válida, ou uma sombreada preservada de
         propósito, não pode deixar o caminho feliz vermelho.
   - **Se executou F1 (instalou) — incondicional, testa o arquivo, não só a cópia em disco:**

     **Exceção — a folha instalou mas não escreveu no settings** (mesma ideia da exceção acima para
     "F2 recusada"): o passo 4/F1 manda **não gravar** em três desfechos — (i) sem `jq` e o
     arquivo-alvo já existe **com conteúdo** ("mostre a chave a acrescentar e relate"); (ii) guarda
     de destino ocupado disparada (script já existe sem nosso stamp) — nada copiado, nada gravado,
     por desenho; (iii) abortou por JSON malformado/raiz inválida no arquivo pré-existente. Caindo em
     qualquer um dos três, confira só que **nada foi gravado** (arquivo-alvo igual ao registro da
     FASE 1, ou continua ausente) e relate como **pendência** — nunca como falha do smoke.

     Fora desses três, F1 escreveu de fato (com ou sem `jq` — os dois ramos do passo 4/F1 que
     gravam):
     - **Com `jq`:** `jq -e '.statusLine.command' <arquivo-alvo-do-settings>` sai `0` **e** o valor
       bate, caractere a caractere, com `sh "<abs-do-destino>/statusline.sh"` — o caminho absoluto
       que foi gravado.
     - **Sem `jq`** (o único ramo em que F1 escreve sem `jq`: arquivo-alvo ausente ou vazio, gravado
       direto com `cat`/`printf`): confira **por leitura direta** que o arquivo contém a chave
       `statusLine` com esse mesmo `command`.

     Esta checagem não depende de o arquivo já ter outras chaves (a próxima, abaixo, é que depende);
     ela existe porque o item seguinte só testa a **cópia instalada em disco**, e uma cópia
     funcionando isolada não prova que a chave chegou ao settings — é exatamente essa lacuna que
     deixaria o bloqueador B1 (arquivo de settings continua sem `statusLine`) atravessar o smoke em
     silêncio. Escreveu e falhou esta checagem → falha do smoke, não sucesso parcial.

     `echo '{"workspace":{"project_dir":"<abs-do-projeto>"}}' | sh
     <cópia-instalada>` imprime uma barra que **contém `📋` ou `⚠`** — não-vazia não basta, prova só
     que modelo/diretório/branch apareceram, não que o board renderizou. (O script usa `[ -r ]`, não
     `[ -x ]`, para achar a irmã — não há item de `chmod` a checar aqui.)
   - **Se F1 gravou em arquivo de settings que já existia antes** deste `/orq:init` (com ou sem
     outras chaves — a FASE 1 registra o conjunto sempre, mesmo vazio) — confira que as chaves
     alheias **continuam lá** — `jq 'keys' <arquivo>` do registro da FASE 1 e do arquivo atual tem
     que dar o mesmo conjunto **mais** `statusLine`. Prova que a escrita foi merge, não overwrite do
     arquivo inteiro.
   - **Se executou F2 (migrou instalação legada):** o `command` novo aponta para a cópia recém-feita
     (não mais para dentro do plugin); `jq 'keys'` do arquivo de settings antes/depois dá o mesmo
     conjunto de chaves (só o **valor** de `statusLine.command` mudou — nenhuma chave sumiu ou
     apareceu); `echo '{"workspace":{"project_dir":"<abs-do-projeto>"}}' | sh <cópia-nova>` imprime
     barra com `📋`/`⚠`, mesmo teste do F1 — e é o **mesmo** teste que o passo 2 do procedimento de
     migração já rodou antes de trocar o settings (achado D2, rodada 3): aqui é só reconfirmar. O
     backup do settings (`arquivo.orq_bak.<timestamp>`) existe no caminho dito, mesmo em sucesso —
     F2 não edita script alheio, então não há backup de script a checar aqui; mas usa backup de
     **settings**, porque a troca de valor em JSON agora também passa por verificação pós-escrita com
     restauração atômica se falhar.
   - **Se executou a remoção (F2, alternativa — em vez de migrar):** `jq -e '(has("statusLine") |
     not)' <arquivo>` sai `0`; `jq 'keys'` antes/depois dá o mesmo conjunto **menos** `statusLine` —
     nenhuma outra chave foi tocada; a barra agora efetiva **executa** — mesmo critério do passo 3
     do procedimento de remoção, acima: resolução própria de interpretador (nunca `sh` forçado),
     exigir só `exit 0` e saída não-vazia — `📋`/`⚠` é **relato**, não condição de sucesso, porque a
     barra revelada é do dono e não tem obrigação de mostrar o board; e o **`command` efetivo não
     aponta para dentro do plugin** (nem a barra que sobrou, nem — por já não existir — a chave
     removida), fechando o achado 3: uma sombreada que também apontasse pro plugin não teria virado
     remoção, teria virado migração, então este item nunca deveria achar um efetivo dentro do
     plugin. O backup do settings existe no caminho dito, mesmo em sucesso.

6. **Host Codex — carregamento e comportamento.** Instalação no disco não prova skill carregada.
   Em conversa Codex nova: confirme `/plugins` e `/skills`; diga “onde paramos?” e confira que
   `memory/MEMORY.md` vem antes do board; depois, num fixture sem dado real, diga “quero melhorar
   X” e confirme que nasce um card/plano com parada no gate. Sem essa prova, registre **“instalado,
   não validado”**. A ausência de `/orq` no menu é esperada: a interface é linguagem natural ou
   `/skills`, não slash commands do Claude.

Só então mostre: o que foi criado vs alterado · o board inicial (`/orq:quadro`) · e o ciclo:

> `/orq:plan-next` planeja o próximo card → você aprova → `/orq:implement-next`
> implementa com review → `/orq:checkpoint` grava → `/clear` limpa a janela.

Registre a instalação no log (`fixes-history.md`). Se algum item do smoke test falhou e você não
conseguiu corrigir, **diga isso** em vez de declarar sucesso.

---

## Regras

- **Idempotente.** Rodar de novo não destrói nada: detecta o que existe, completa o que falta,
  relata o que ignorou.
- **`--reinstalar`** refaz a **análise** (não os arquivos): reinvestiga as lacunas, compara com o que
  está instalado e propõe **atualizações** — time que não faz mais sentido, backlog desatualizado,
  ferramenta nova disponível. Continua pedindo ok, continua sem sobrescrever conteúdo que o dono
  escreveu, e continua respeitando a seção "Dispensadas".
  **Verifique também o legado:** instalação anterior à 0.6.0 pode ter deixado `.claude/agents/orq-*.md`
  no projeto, colidindo com os agentes do plugin. Cheque também `~/.claude/agents/orq-*.md` —
  colisão em escopo usuário atinge **todos** os projetos e não aparece no repo. Achou? **Relate e
  proponha renomear ou remover** — não decida sozinho, mas não deixe passar calado: a colisão é
  silenciosa e de resolução indefinida.
  **Re-sync da statusline instalada:** ache a cópia **seguindo o comando efetivo de cada escopo**
  (resolver o `command` — descartando prefixos de variável, achando o interpretador `sh`/`bash`/
  `zsh`, isolando o caminho do script —, resolver symlink, achar o script real) — **nunca só
  enumerando caminhos conhecidos** (achado C9, rodada 3: um layout legítimo fora dos dois abaixo —
  por exemplo a barra global pré-existente do dono, invocando um `kanban-status.sh` ao lado dela que
  nunca foi instalado por este comando — não aparece numa busca que só olha `.claude/`/
  `~/.claude/orq/`, e a cópia fica velha em silêncio quando a fonte do plugin mudar). Os dois layouts
  que **este comando cria** (referência para reconhecer o que é nosso, não os únicos lugares a
  procurar): o par completo em `.claude/` do projeto (F1 escopo projeto) · o par completo em
  `~/.claude/orq/` (F1 escopo usuário).

  Para cada cópia achada — pelos dois layouts **ou** seguindo o comando efetivo —, leia o stamp da
  linha 2 (formato exato: `# orq v<versão> — instalado por /orq:init em <AAAA-MM-DD>; fonte:
  orq/scripts/<nome>. Não editar à mão; re-sync: /orq:init --reinstalar`). **Com stamp:** compare a
  versão do stamp com a versão deste plugin **e** rode `diff` contra a fonte correspondente
  (`${CLAUDE_PLUGIN_ROOT}/scripts/statusline.sh` ou `${CLAUDE_PLUGIN_ROOT}/scripts/kanban-status.sh`)
  **ignorando a linha do stamp** — a fonte no plugin não leva stamp (é a linha 2 dela, código de
  verdade lá; comentário só na cópia), então comparar bruto acusa a linha do stamp em toda cópia,
  sempre, mesmo sem nenhum drift real: `diff <(sed '2d' <cópia>) <fonte>`. **Sem stamp** (achada só
  pelo comando efetivo, como o legado do dono, ou arquivo de terceiros que só coincide de nome):
  ainda assim rode `diff <cópia> <fonte>` — divergiu ou não, é **sempre** relato, nunca ação (script
  sem o nosso stamp não é nosso para consertar). Divergiu, com ou sem stamp → **proponha** re-sync
  (recopiar com stamp novo); **nunca aplique sozinho**.

  ⚠️ Esta seção é sobre **detectar e propor** em cópias que já existem, não sobre escrever. A guarda
  de destino ocupado (achado 7, comum a toda cópia — ver o passo 4, folha F1) é quem protege no
  **momento de copiar**, dentro de cada folha que copia — ela não depende desta varredura encontrar
  nada antes (correção do achado C3, rodada 3: a versão anterior deste texto dizia que uma cópia sem
  stamp "é pega pela guarda de destino ocupado da folha F1 no próximo `/orq:init`", mas um projeto
  classificado F2 nunca reavalia F1 — a chave legada continua apontando para o plugin até alguém
  migrar, então essa frase descrevia uma proteção que nunca rodava). Chave `statusLine` apontando
  **diretamente** para dentro do plugin (instalação nossa legada) é pega pela folha F2, que roda em
  todo `/orq:init` — não precisa repetir aqui.
- **Nunca** `git commit`/`push`. Nunca tocar em código de produção.
- **Nunca** inventar estado: se não sabe se algo funciona, põe em VALIDATE, não em DONE.
- Projeto pequeno merece estrutura pequena — `MEMORY.md` + `fixes-history.md` + board já bastam.
