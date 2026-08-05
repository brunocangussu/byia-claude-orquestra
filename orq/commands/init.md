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
5. **Trabalho em aberto** — TODO/FIXME no código, issues, itens não concluídos nos docs, testes
   quebrados. Vira o backlog inicial (com IDs `T-NNN`).
6. **Ferramental disponível** (checar de verdade, não presumir):
   - **Rode as verificações de `${CLAUDE_PLUGIN_ROOT}/stack.md`** — é o catálogo da stack
     complementar (contexto, memória, busca semântica, revisor externo), com como detectar cada uma.
   - MCPs conectados além dessas (banco, deploy, observabilidade, design…)
   - Subagentes que o projeto **já** tem em `.claude/agents/`
   - Se houver busca semântica: **o repo já está indexado?**

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
(seção "Perfis", ver FASE 4).

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
- backlog inicial que você encontrou.

**Faça as decisões dele em UMA interação, não em três.** Use `AskUserQuestion` com as perguntas
juntas:

1. **Instalar o Orquestra** com esse time e essa memória? (ajustes do time entram aqui)
2. **Revisores no painel** — só Claude, ou Claude + os externos **que já existem nesta máquina**?
3. **Instalar a stack complementar** que falta? — listada à parte, e ele pode recusar inteira sem
   afetar o resto.

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
   (traz de fábrica a linha "Perfil ativo" e a seção "Perfis" com `padrao`/`economia` prontos —
   ajuste só os modelos e a nota de "o que se perde" à realidade deste projeto). Não crie um
   `_elenco.md` só com a tabela de papéis: o projeto nasce **já** com o conceito de perfil, não como
   um recurso que só aparece se alguém pedir depois. É esse arquivo que os comandos leem na hora de
   spawnar.
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
4. **Statusline** (opcional, perguntar): apontar o `statusLine` do settings para o
   `kanban-status.sh`. Se já houver statusline customizada, **não sobrescreva** — mostre a linha a
   acrescentar.
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
- **Nunca** `git commit`/`push`. Nunca tocar em código de produção.
- **Nunca** inventar estado: se não sabe se algo funciona, põe em VALIDATE, não em DONE.
- Projeto pequeno merece estrutura pequena — `MEMORY.md` + `fixes-history.md` + board já bastam.
