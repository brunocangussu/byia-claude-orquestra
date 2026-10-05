---
description: Loop B — implementa o próximo card aprovado, com review independente e documentação, até deixá-lo pronto para você validar
argument-hint: "[T-NNN para escolher um card específico]"
---

Você é o **Manager** (leia a skill `orq`). Rode o **Loop B — Implementação**.

Antes de qualquer uso, comprove `ORQ_PACKAGE_ROOT` absoluto, existente e com `scripts/kanban-status.sh` disponível.
**BOARD_CANONICO:** antes de validar ou mover o card, resolva
`sh "${ORQ_PACKAGE_ROOT}/scripts/kanban-status.sh" --resolver .` na frente atual, sem `cd` para o principal, e use exclusivamente o caminho `board` do JSON
completo. `state: erro` é bloqueio visível, não licença para ler cópia local. THREAD_ROOT é o `thread_root` absoluto devolvido pelo resolver: `memory/wiki` da raiz do projeto/worktree que iniciou a operação, nunca do `BOARD_CANONICO`. O ponteiro `threads/...` do card só identifica a thread: leia/escreva exclusivamente `THREAD_ROOT/threads/...`. Somente a frente dona pode criar a thread: ela criou o card agora, ou, para card legado do BACKLOG sem ponteiro/thread, o reivindica e marca com `@frente-<slug>`. Card já marcado para outra frente, ou card existente com ponteiro cuja thread falta em `THREAD_ROOT`, deve parar: não crie, duplique, troque de frente nem use fallback.
Se a chamada tiver `exit != 0`, stdout vazio, JSON inválido, `state` diferente de `ok`, `exists` não booleano, ou `board`/`thread_root` ausentes ou não absolutos, trate como `state: erro`, declare indisponível e não use cópia local. Sem JSON, informe `exit` e `stderr`; com JSON de erro, informe `code`.
Com `state: ok` e `exists: false`, pare e encaminhe para `/orq:init`: não há board para ler, validar ou mover neste loop.
Passe `BOARD_CANONICO=<board>` e `THREAD_ROOT=<thread_root>` como caminhos absolutos em cada briefing; o Manager resolve uma vez, e os papéis despachados não re-resolvem nem mudam a raiz de memória.

## 0. Pré-condições (não negociáveis)
- O card precisa estar **READY** (`[~]`) com plano **aprovado**. Se não estiver, pare e diga que
  falta passar pelo `/orq:plan-next`.
- Card que escreve código roda em **worktree isolado** (`isolation: "worktree"` no spawn) quando
  essa etapa local estiver no escopo aprovado e não houver proibição expressa de mutação Git,
  branch ou worktree; esta pré-condição não autoriza criar worktree ou entregar Git por si só.

## 0a. Registro durável da aprovação

Antes de escolher o writer, leia o registro da thread dona e verifique que a
ação local pretendida cabe no escopo permitido, não cruza as proibições e não
consome orçamento reservado a outro gate. Plano, READY ou commit não são
evidência humana. O registro precisa conter a fonte humana literal e seu
ponteiro verificável — citação ou referência verificável da evidência humana —,
escopo, proibições e orçamento de chamadas separado por gate, com limite e
consumo. O registro da thread é transcrição, não fonte: a captura registra a
verificação da fonte real, não uma nota autodeclarada.

Se o registro estiver ausente ou incompatível, recupere a fonte humana original
na conversa ou em documento humano explicitamente endossado e transcreva-a
quando ela provar a aprovação. Nunca invente a aprovação. Se houver prova
irrecuperável, pause somente a ação sem autoridade e continue as ações locais
elegíveis do escopo; se ainda faltar autoridade, peça somente a autoridade
realmente ausente, sem pedir novo aval para cada subpasso já incluído na
aprovação contínua.

Para cada operação de entrega Git, o leitor exige no mesmo registro a citação
ou referência verificável da autorização humana original que a nomeie. Operação
de entrega Git é stage, commit, push, merge, tag ou publicação; leitura Git não
é operação de entrega Git. Aprovação local, review, plano, READY ou nota do
Manager não substituem esse gate; sem a referência original, a operação de
entrega Git permanece proibida. Worktree isolado só é etapa local quando já
estiver no escopo aprovado e não houver proibição expressa de mutação Git,
branch ou worktree; este comando não transforma essa condição em autorização de
entrega.

> **Elenco:** antes de cada despacho, **identifique o host**, leia `## Times por host`, resolva o
> papel (`implementer` **na faixa do card**, `reviewer`, `docs`) e só então aplique
> `## Matriz de invocação`. Sem elenco, use o template completo de
> `ORQ_PACKAGE_ROOT/commands/elenco.md` **somente para leitura dos candidatos**. O template não é
> fallback executável: aplique o gate canônico de capacidade naquela seção. **Padrão legado comprovado** é uma
> combinação já usada e autorizada neste projeto, com recibo real consultável na thread. O Manager verifica a
> origem e a compatibilidade antes do despacho. É reaproveitamento de prova existente válida, nunca isenção de
> prova. Default, alias ou cache não certificam. Sem recibo ou se o contexto mudou, não despache essa operação.
> Não há sonda ou retry automáticos; prossiga com outras ações locais elegíveis. Quando o recibo válido ainda é
> compatível, o reuso não exige nova sonda a cada uso. Sem essa prova, pare antes do spawn e peça a escolha/gate
> do dono. A skill já precisa ter resolvido `ORQ_PACKAGE_ROOT` para o host atual.
> Configurado não significa rodando: registre o executor real.

## 0b. Abrir o medidor de progresso

Com o plano aprovado e **antes de despachar**, abra o medidor. Leia
`ORQ_PACKAGE_ROOT/skills/orq/references/progress.md`: ele traz os comandos, o ownership e os códigos
de saída.

1. `begin --kind card` com `--root` igual ao `front_root` devolvido pelo resolver (nunca o worktree
   do implementer), `--board` com `BOARD_CANONICO`, `--thread-root` com `THREAD_ROOT`, `--card`,
   `--front` (o slug da frente) e o `--host` real.
2. `plan` com a **tabela de passos** do plano aprovado. Plano antigo é o aprovado antes da adoção do medidor.
   Plano antigo sem tabela: você atribui ID,
   tamanho e critério mantendo correspondência com os passos já aprovados; mudança material do plano
   volta ao gate do dono, não vira ajuste silencioso.
3. Na thread pública, registre só caminho, run_id e revisão; nunca a chave de dono.
   Recupere a `session_key` constante somente do ledger local ignorado da frente dona, conforme a
   referência do medidor; não a copie para Git, briefing, parecer externo ou resumo público.
4. Vincule a sessão ao ledger com `bind`, usando a **chave da sessão nativa** que o hook entregou no
   contexto — outra chave, que não é a `session_key` de dono do passo 3. Nos marcos, leia o `view` do
   recibo da marcação em vez de rodar `show`. O procedimento mora em
   `ORQ_PACKAGE_ROOT/skills/orq/references/progress.md` ("Vínculo de sessão" e "Recibo"); não o repita.

Só o Manager escreve o ledger. Ao despachar um worker, marque `start` nos passos que cabem a ele,
**antes** do despacho, com o papel e o rótulo genéricos dele (`--executor-role implementer`,
`reviewer` ou `docs`); marque `done` passo a passo **depois** de conferir resultado e evidência.
`phase` acompanha a etapa: `implementation` ao despachar o writer, `review` na revisão, `docs` na
documentação. Passo novo, descartado ou reaberto (`add`, `drop`, `reopen`) só depois que o ciclo
normal autorizou a mudança. Apresente um resumo do medidor nos marcos e quando o dono pedir.
Exit `2` é chamada inválida: corrija-a. Exit `3` ou `4` não bloqueia o loop, mas não é sucesso:
reporte o marco como progresso não registrado.

## 1. Implementar

Confirme primeiro que existe **worktree dedicado** ao card. Nunca execute o writer no checkout do
Manager.

**Quem escreve é sempre do vendor do host** — escrita cross-vendor está fora do desenho. O que varia
é o **degrau**, dado pela **faixa** do card (`pesada` | `normal` | `leve`), registrada na nota em
`trilha: … · faixa: …`. A régua da faixa é definida **uma única vez**, em
`ORQ_PACKAGE_ROOT/commands/elenco.md`, seção "As duas réguas" — leia lá; não a reescreva aqui. Card
sem registro vale `normal`. A reavaliação da faixa depois do gate está na mesma seção — aplique-a
de lá, **inclusive o piso: card Alto risco continua `pesada` mesmo com o plano fechado**. Se
rebaixou, diga em uma linha por quê.

- **Host Claude:** spawn fresco do `orq-implementer` no worktree, com o override da faixa resolvido.
- **Host Codex:** use o modelo/effort da linha `implementer` da faixa em `## Times por host` e copie
  o comando da célula OpenAI×Codex da Matriz, com sandbox `workspace-write`, executado dentro do
  worktree. `codex exec` é o caminho padrão; a primitiva nativa só é permitida quando o `_elenco.md`
  registrar override comprovado por chamada real.

Sem modelo, CLI, worktree ou sandbox exigido → **não escreva**. Devolva o card com a degradação
nomeada.

O briefing inclui: `BOARD_CANONICO=<board>` e `THREAD_ROOT=<thread_root>` absolutos, o card, o **plano aprovado**, os critérios de aceite, as convenções do projeto
(build/teste), o que está fora de escopo, os **IDs dos passos** que cabem ao worker, a fonte humana literal e ponteiro
verificável, o escopo permitido, proibições e limites consumidos por gate. Diga
explicitamente: **Git não está autorizado neste gate** salvo a referência humana
original específica já verificada; workers não movem o board, não re-resolvem a
raiz e não alargam o escopo.
O worker **não escreve o ledger** do medidor e não recebe o `session_key`.
O worker não lê nem usa a chave de dono, mesmo se encontrar o ledger local. Essa é uma fronteira de
instrução e ownership, não uma ACL contra outro processo com o mesmo usuário.

Exija de volta: o que foi feito, como testou, o que **não** conseguiu fazer, e as decisões tomadas
no caminho — e, por ID de passo, a referência da evidência (caminho de arquivo, nome de teste:
identificador, nunca saída colada).

## 2. Revisar (parecer independente, read-only)
Antes de disparar a revisão, confira o gate externo específico: citação ou
referência verificável da autorização humana original, procedência, modo e
cobertura válidos para o snapshot/envelope, além do saldo disponível da
tentativa. Sem esse gate, não inicie a chamada; registre a pendência e avance a
ação local elegível dentro do escopo aprovado. Não faça retry automático nem
reinicie o consumo.

Rode a **revisão** (`/orq:revisar`): **um** revisor, sempre do **vendor oposto ao host**, com o
briefing do diff, `BOARD_CANONICO=<board>` e `THREAD_ROOT=<thread_root>` absolutos, os critérios de aceite, o que está fora de escopo, fonte humana literal e ponteiro verificável, escopo permitido, proibições, limites consumidos por gate e a indicação de que Git não está autorizado neste gate. O reviewer não re-resolve nem muda a raiz de memória; workers não movem o board.

**Audite antes de agir:** com um revisor só, todo achado é solitário por construção — você
**verifica cada um no código** antes de aceitar, e descarta o que não tiver cenário de falha
concreto. Discordou do parecer? Desempate olhando o código e explique.

Em card pequeno e de baixo risco, `--rapido` encolhe o **briefing** — nunca troca de revisor nem
dispensa a revisão. Titular indisponível ou dado sensível no diff mudam o desfecho (revisão
degradada, ou ausência de revisor declarada): quem decide isso é o `/orq:revisar` — regra lá.

**Aplicar as correções é do implementer**, não do reviewer. Achado grave → devolva ao implementer e
revise de novo. Máximo 2 rodadas; persistindo, escale pro dono. Achado que desfaz um passo já
concluído: `reopen` desse passo; trabalho novo dentro do escopo aprovado: passo novo (`add`).

## 3. Documentar (sobre o código FINAL)
Só depois do review fechado, spawn do `orq-docs` com `BOARD_CANONICO=<board>` e `THREAD_ROOT=<thread_root>` absolutos, fonte humana literal e ponteiro verificável, escopo permitido, proibições, limites consumidos por gate e a indicação de que Git não está autorizado neste gate — senão a documentação descreve algo que mudou. O papel não re-resolve nem muda a raiz de memória; workers não movem o board nem alargam o escopo.
Documentação é **atemporal**: descreve como é agora, não a história da mudança.

Atualize também a **página de tópico** da wiki afetada (é aqui que a memória se paga).

## 4. Fechar
- Antes de cada operação de entrega Git, confira a citação ou referência
  verificável da autorização humana original específica que a nomeie. Sem esse
  gate, não faça ações Git de entrega: mantenha a pendência da entrega na thread
  e conclua somente o trabalho local elegível; não trate o bloqueio de Git como
  bloqueio da meta inteira. Implementação local, plano, READY, review ou gate
  externo não autorizam stage, commit, push, merge, tag ou publicação.
- Sem entrega autorizada para o alvo de validação, não prometa VALIDATE no
  checkout principal nem DONE. Commit sozinho não prova pronto; o Manager só
  move a `[?]` quando a entrega e a transição correspondentes estiverem autorizadas;
  `[x]` exige validação positiva do dono, não só autorização para validar.
- Se a entrega Git ainda estiver pendente, mantenha o medidor aberto em `docs`, registre a pendência
  na thread e continue outras etapas locais autorizadas; não use `validate`, `pause` ou `close` só por
  chegar a 100%.
- Somente depois da entrega e da passagem autorizadas a `[?]`: no medidor,
  `phase --value validate` e `pause`. A vista mostra "validação do dono", mesmo
  com 100% dos passos; 100% do plano não é DONE. Se o dono reprovar e o card
  voltar a `[~]`, `resume`. `close` só quando o card estiver em `[x]` ou for cancelado.
- Escreva no card **como o dono valida**: passos práticos de usar o produto (abrir X → clicar Y →
  observar Z). Nada de git/logs/teste automatizado — isso é trabalho do time, não dele.

## 5. Reportar
Em poucas linhas: o que mudou · o que o review pegou · o que falta o dono testar · o que ficou
pendente. Se algo precisa de decisão dele, destaque.

## Regras
- Falhou o build ou o teste → **não** feche o card. Reporte com o erro real.
- Descobriu um bug fora do escopo → card novo no BACKLOG (você decide) ou inclua se for pequeno e
  da mesma causa raiz. Registre no board de qualquer jeito.
- Nunca marque DONE sozinho, salvo se o dono tiver delegado explicitamente aquele card.

## Continuidade de execução aprovada

Consulte o `Contrato de continuidade aprovada` em
`ORQ_PACKAGE_ROOT/skills/orq/SKILL.md`.
Com evidência humana durável na thread dona, aplique a correção local dentro do
escopo aprovado sem pedir nova aprovação por cada ajuste da mesma causa. Isso
não autoriza ações externas ou de Git; preserve limites consumidos, não tome
card de outra frente e, se não houver ação elegível, registre o impedimento real.
