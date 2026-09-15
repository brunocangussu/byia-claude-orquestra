# T-076 — board pelo checkout principal

## Histórico — situação em 2026-09-13

Card em planejamento, posse `@codex`; **nenhuma implementação aprovada**. O checkout principal
mostrou 93 cards enquanto o worktree T-076 mostrou 92 com a mesma versão de código. A causa é a
resolução por `git rev-parse --show-toplevel` em `kanban-status.sh` e caminhos relativos nos
comandos. O gotcha do projeto já registra que `memory/` versionado se bifurca entre worktrees.

O plano está em `docs/superpowers/plans/2026-09-13-t076-board-principal.md`. Recomenda board-only,
resolver único e fail-closed quando Git existe mas o principal não pode ser identificado. O par
copiado da statusline é uma restrição de empacotamento; `lint-coerencia.py` sob raiz explícita deve
continuar validando aquela fonte. O T-062 tem estado local pendente de reconciliação, que a mera
resolução do caminho não transporta para a main.

Verificação do planejamento: os 14 testes existentes de `kanban-status.sh` passaram, mas todos
usam projetos sem Git; não provam worktree. `git diff --check` saiu 0 e a linha do card tem 210
bytes, dentro do teto de 240. O lint ainda aponta a falha preexistente do T-081 em `[?]` com
marcador de host. A linha T-076 deste plano foi movida apenas no worktree isolado; a main
compartilhada, com alterações paralelas de outras frentes, continua com o card antigo em backlog.
Isso é parte do problema que o T-076 pretende resolver, não um estado global já reconciliado.

## Decisão do dono — 2026-09-14

O dono respondeu “prossiga com sua recomendacao” ao pedido específico de
aprovação do escopo **board-only**. O T-076 pode entrar em implementação no
worktree isolado; centralização integral de `memory/` e migração de estados
órfãos seguem fora deste card. Não houve bump, commit, push, publicação,
instalação ou restart.

## Histórico da retomada anterior — 2026-09-14

O Manager releu o plano e a decisão, moveu apenas a linha T-076 para `[~]
@codex` no board canônico e neste worktree, preservando as alterações paralelas
da `main`. Próximo passo: baseline, RED/implementação no worktree T-076,
revisão e docs. Não migrar `memory/` por inferência; bump, commit, push e
release permanecem em gates separados.

## Histórico — checkpoint de recuperação de 2026-09-14

Após compactação, o Manager releu `memory/MEMORY.md`, o board canônico e esta thread.
O pedido vigente autoriza somente a implementação board-only do T-076. A CLI Codex
em `workspace-write` continua trabalhando neste worktree; o resolver já tem REDs
para checkout antigo, Git ausente e `--separate-git-dir`, mas ainda não há GREEN
final nem revisão. As alterações paralelas do Claude na `main` permanecem fora
do escopo. Não fazer bump, commit, push, instalação, publicação ou restart.

## Histórico do candidato local após implementação

O T-076 board-only está implementado somente neste worktree. Em uso real, o modo
estruturado apontou ao `KANBAN.md` da main (`provenance: principal`) e o modo
normal mostrou os mesmos 93 cards da main; a cópia local tinha 92. Foram
adicionados testes de Git/worktree real, falhas sem fallback stale, par copiado
da statusline e contrato dos consumidores. Dois REDs da auditoria (link `.git`
quebrado e comando resolver sem caminho) foram corrigidos; o caminho do plugin
passou a ser citado entre aspas para aceitar espaços. O timeout Git ficou
limitado a 0,75 s por chamada.

Verificação independente do Manager: 23/23 testes do resolver e 5/5 do
contrato passaram; `git diff --check` e manifesto estrito passaram. A suíte
completa executou 346 testes, com quatro falhas já observadas fora do T-076
(`test_elenco_perfis`, `test_observation_types_guard` e dois
`test_write_flag_guard`). O lint ainda acusa o marcador preexistente do
T-081 e a divergência fonte/cache 0.27.6 esperada antes de bump e instalação.
Nada foi staged, commitado, enviado, publicado, instalado ou reiniciado.

Limitação comprovada: worktree derivada de repositório criado com
`--separate-git-dir` não permite recuperar o checkout principal pelo inventário
Git usado; o resolver devolve erro visível, sem board stale. Errata no plano.
Revisão local encontrou e corrigiu ainda a contradição de `init.md`: os passos
antigos mandavam criar `memory/wiki/KANBAN.md` relativo apesar do preâmbulo
canônico. A guarda agora usa mutação do corpo da instrução com o preâmbulo
preservado e distingue `state: erro` de ausência verdadeira do board.
Próximo gate: revisão independente do diff/instruções, conciliação cirúrgica
do board e da thread com a main compartilhada, depois decisão do dono sobre
bump/commit/push. O teste comportamental pós-release continua pendente.

## Histórico — checkpoint de recuperação e revisão Fable R1 — 2026-09-14

Após a compactação, o Manager releu `memory/MEMORY.md`, o board e esta thread.
O worktree T-076 continua isolado e sujo; nenhum arquivo da janela Claude na
`main` foi alterado nesta retomada. A revisão independente R1 usou seis lotes
sanitizados do diff, todos respondidos pelo Fable 5.1 com `exit 0`; o veredito
do conjunto é **REPROVADO**. Não houve correção de código após esse snapshot.

Bloqueadores confirmados para corrigir com RED/GREEN: timeout de
`git worktree list` sem tratar o sentinela; retomada do guardião que resolve o
board mas não manda lê-lo e ler a thread ativa; lint que aceita instrução de
leitura/edição do board relativo; consumidores que não tratam stdout vazio,
JSON inválido ou exit não zero do resolvedor; linha antiga de `quadro.md`
que ainda aponta a thread relativa; plano que usa “sem Git comprovado” de
forma ambígua; dois marcadores de retomada nesta thread; e teste contratual
que deriva a lista de consumidores da mesma lista que pretende vigiar. O
marcador antigo foi rebaixado a histórico neste checkpoint.

**Decisão necessária antes de corrigir `init` e o contrato das threads:** o
escopo aprovado diz que índice e threads permanecem por frente, mas o item 5
do mesmo plano exige procurar threads ao lado do board principal e declarar
ausência ali como indisponibilidade. Na worktree atual a thread T-076 só existe
localmente. Criar threads no principal centraliza parte de `memory/`; mantê-las
locais torna a regra do item 5 incorreta. O Manager não escolherá nem migrará
threads por inferência. A R2 Fable só faz sentido após essa decisão e as
correções do snapshot; nenhuma nova rodada foi executada.

## Contraprova do host Codex — raiz do pacote

Nesta sessão Codex, `printenv CLAUDE_PLUGIN_ROOT` saiu `1` e não devolveu
valor. Executar literalmente a instrução distribuída
`sh "${CLAUDE_PLUGIN_ROOT}/scripts/kanban-status.sh" --resolver .` saiu `127`:
`sh: /scripts/kanban-status.sh: No such file or directory`. Os consumidores
novos de `BOARD_CANONICO` ainda prescrevem essa variável; portanto o erro não
é só uma hipótese do Fable neste host. A skill instalada do Orquestra já manda
resolver `ORQ_PACKAGE_ROOT` no Codex e substituir a variável Claude antes de
executar comandos legados. A correção do T-076 precisa tornar essa regra
explícita e testável nos novos consumidores, mantendo o erro fail-closed se a
raiz do pacote não puder ser comprovada. Isto não decide onde as threads moram.
Como controle, chamar o script candidato por caminho absoluto no mesmo cwd saiu
`0` com `state: ok`, `provenance: principal` e `board` apontando à `main`.

## Histórico — checkpoint de recuperação e correções da R1 — 2026-09-14

Após nova compactação, o Manager releu `memory/MEMORY.md`, o board canônico e
esta thread. O worker do mesmo card corrigiu somente os bloqueadores inequívocos
da R1, sem escolher onde as threads moram: timeout de `git worktree list` agora
vira JSON `git-timeout` sem traceback; falta de `python3` devolve JSON completo
em stdout com exit 2; os consumidores usam `ORQ_PACKAGE_ROOT`, tratam exit não
zero, stdout vazio, JSON inválido e campo `board` ausente como erro; o guardião
manda reler o board devolvido e a thread ativa; e o lint passou a cobrir
leitura, edição ou movimento do board relativo, invocação nua e invocação sem
aspas, sem confundir negação com prescrição.

O Manager encontrou depois duas chamadas normais sem aspas, que quebrariam no
próprio caminho deste projeto por conter espaços. Um RED contratual reproduziu
o falso verde e a correção eliminou todas as invocações variáveis desprotegidas
de `kanban-status.sh` no escopo do card. Verificação independente com o Python
Homebrew 3.12: resolver 24/24 e contrato 10/10 verdes; manifesto estrito e
`git diff --check` verdes. A suíte descoberta executou 351 testes e manteve só
as quatro falhas basais já atribuídas ao T-081. O lint manteve apenas o marcador
preexistente do T-081 e a divergência fonte/cache esperada antes de bump.

Nota de ambiente: o `python3` desta sessão Codex resolve para o Python Apple
3.9.6 e não importa os testes que usam `str | None`; as verificações acima
usaram explicitamente `/opt/homebrew/bin/python3` 3.12.11. Nenhum arquivo da
janela Claude na `main` foi alterado, e não houve bump, stage, commit, push,
Fable R2, publicação, instalação ou restart.

## Decisão do dono — opção B aprovada em 2026-09-14

O dono aprovou a recomendação registrada no gate: somente o board operacional
fica no checkout principal; as threads permanecem na worktree/frente que é dona
do card. O contrato e os consumidores devem resolver a thread a partir da frente,
sem procurá-la ao lado do `BOARD_CANONICO` e sem fallback silencioso para outra
worktree. Esta aprovação autoriza o ajuste correspondente e a R2 Fable; bump,
commit, push, publicação, instalação e restart continuam fora do escopo.

## Revisão Fable R2 — 2026-09-14

A R2 cobriu os 105.015 bytes do diff integral em dez lotes sanitizados, todos
abaixo de 16 KiB e todos executados pelo `claude-fable-5-1` com exit 0. O
conjunto foi **REPROVADO**. A auditoria do Manager confirmou seis bloqueadores:
referências prescritivas restantes a `KANBAN.md` relativo no checkpoint; caminhos
do pacote sem aspas no init; lint que verificava somente a primeira ocorrência
de três padrões; verbos de mutação que escapavam do lint; e os dois trechos
desatualizados desta thread após a aprovação/implementação da opção B.

Riscos confirmados para a mesma correção: derivação ambígua de `THREAD_ROOT`
quando a operação começa numa subpasta; validação incompleta de `state`, `exists`
e `code`; ausência de regra explícita para criar thread nova apenas na frente;
`plan-next` sem parada em `exists: false`; uso prematuro de `ORQ_PACKAGE_ROOT` no
contexto do guardião; comentário contratual sem comportamento em `statusline.sh`;
normalização desigual de symlink; e testes novos incompatíveis com o `python3`
3.9 prescrito nesta sessão. O modo normal do statusline já resolve o board
canônico e imprime erro em stdout; esses dois riscos do parecer foram descartados
por verificação direta.

O contador está em `revisões: 2/2`. Corrigir os achados confirmados continua
dentro da fase de correção desta R2; uma R3 não está autorizada pelo comando
instalado. Não houve bump, commit, push, publicação, instalação ou restart.

## Histórico — checkpoint de recuperação pós-compactação — 2026-09-14

O Manager releu `memory/MEMORY.md`, o quadro canônico e esta thread após a
compactação. A decisão vigente continua sendo a opção B: board operacional no
checkout principal e threads na frente proprietária. O worker exclusivo do
T-076 segue corrigindo os achados da R2 dentro deste worktree; nenhuma R3 foi
executada. Os arquivos paralelos da janela Claude na `main` permanecem fora do
escopo e não foram alterados nesta retomada. Continuam sem autorização: bump,
commit, push, publicação, instalação e restart.

## Correções da R2 e verificação do Manager — 2026-09-14

O candidato agora devolve `front_root` e `thread_root` absolutos, normaliza
symlinks, preserva campos nulos em erro e separa o board canônico da thread da
frente. Consumidores validam o JSON completo, exibem `code` e não fazem fallback;
thread ausente pode ser criada somente pela frente proprietária. O lint percorre
todas as ocorrências e cobre os verbos e ferramentas auditados. `statusline.sh`
deixou de ser tratado como consumidor textual.

Verificação fresca do Manager: Python 3.9 e 3.12 passaram em 25/25 testes do
resolvedor e 16/16 do contrato; o guardião passou 103/103. A suíte descoberta fez
359 testes e manteve somente quatro falhas basais externas já conhecidas, ligadas
ao T-081 e à documentação da `main`. Manifesto estrito e `git diff --check`
saíram verdes. O lint apontou somente os dois residuais basais: marcador do T-081
e divergência esperada entre a fonte candidata 0.27.6 e o cache instalado.

## Histórico do gate da R3 — 2026-09-14

O Manager moveu o T-076 no board canônico para `[!] @codex`, com
`revisões: 2/2`. Decisão necessária: autorizar uma extensão de **+1** para uma
única R3 Fable do snapshot corrigido. Não executar R3, bump, commit, push,
publicação, instalação ou restart sem o gate correspondente. Nenhum candidato
de código foi integrado na `main`.

## Autorização e revisão Fable R3 — 2026-09-15

O dono aprovou a extensão delimitada de +1. A única R3 cobriu 178.533 bytes
sanitizados do diff integral, em 19 lotes de no máximo 16.384 bytes. Os 19
runners saíram `0` e provaram `claude-fable-5-1`; nenhum hunk foi omitido. O
parecer conjunto foi **REPROVADO**.

A auditoria do Manager confirmou: o mesmo `THREAD_ROOT` precisa ser propagado
a writer/reviewer/docs; o template do `init` não define BOARD/THREAD_ROOT; a
posse de frente admite leitura literal; consumidores ainda usam a raiz do pacote
antes de comprová-la e não explicam erro sem JSON; origem inexistente recebe
falso `state: ok`; e o lint ainda aceita negação que engloba violação posterior,
conjunção adversativa e invocação não cotada por `bash`/execução direta. Também
foram aceitos para a mesma correção: schema uniforme com `code`, proveniência
distinta de worktree, recusa de `--board-path` relativo e isolamento das variáveis
Git que podem redirecionar `git -C`.

Foi descartada como bloqueador a mera existência de checkpoints históricos:
o contrato operacional exige um único `RETOMAR AQUI`, não apagar o histórico.
Os títulos antigos foram rebaixados para “Histórico” para impedir leitura como
estado vigente. O contador agora é `revisões: 3/3 · extensão: +1`.

## Checkpoint de recuperação pós-compactação — 2026-09-15

O Manager releu `memory/MEMORY.md`, o board canônico e esta thread. O contexto
foi recuperado sem mudar o escopo: o worker exclusivo do T-076 continua
corrigindo somente os achados auditados da R3 neste worktree. A `main` segue
compartilhada com alterações paralelas da janela Claude e deve ser preservada.
Continuam fora deste gate: R4, bump, commit, push, publicação, instalação e
restart.

## Correções da R3 e verificação do Manager — 2026-09-15

Os sete blocos auditados da R3 foram corrigidos com RED/GREEN: resolução
fail-closed e schema uniforme; handoff único de `BOARD_CANONICO`/`THREAD_ROOT`;
contrato de frente e posse `@frente-<slug>`; prova prévia de `ORQ_PACKAGE_ROOT`;
distinção entre erro e `exists: false`; e lint contra negação/adversativa e
invocação desprotegida. A auditoria do Manager encontrou ainda um caminho de
`OSError` não tratado em `git worktree list`; um RED reproduziu o traceback e a
correção passou a devolver `git-indisponivel` estruturado.

Verificação fresca final: resolvedor 29/29 em Python 3.9.6 e 29/29 em 3.12.11;
contrato 21/21 e guardião 103/103; manifesto estrito e `git diff --check`
verdes. A suíte descoberta executou 368 testes e manteve somente quatro falhas
basais externas já conhecidas: marcador do T-081, prescrição em
`memory/MEMORY.md` e duas derivações do write-flag. O lint manteve somente T-081
e a divergência fonte/cache causada por `checkpoint.md` sem bump/reinstalação,
ações vedadas neste gate. No worktree real, o resolvedor apontou o board da
`main`, preservou a raiz de threads da frente, retornou `code: null` e
`provenance: worktree`.

## Autorização da R4 — 2026-09-15

O dono autorizou extensão delimitada de **+1** para uma única R4 Fable do
snapshot corrigido. O contador passa a `revisões: 4/4 · extensão: +2`. A revisão
foi iniciada com diff integral sanitizado; permanecem fora do gate bump, commit,
push, publicação, instalação e restart.

## Checkpoint de recuperação pós-compactação — 2026-09-15

O Manager releu `memory/MEMORY.md`, o quadro canônico e esta thread. A única
R4 Fable continua no mesmo processo já iniciado, com 18 arquivos, 24 lotes e
cobertura declarada de 222.128/222.128 bytes; ela não foi reiniciada nem
duplicada. T-070 segue limitado à correção documental e à revisão no worktree,
e T-071 permanece sem implementação até a integração autorizada do T-076. A
`main` compartilhada e os arquivos paralelos da janela Claude permanecem fora
do escopo. Continuam vedados bump, commit, push, publicação, instalação e
restart.

## Revisão Fable R4 e auditoria do Manager — 2026-09-15

A única R4 terminou sem falha operacional. O manifesto cobriu 222.128/222.128
bytes do diff sanitizado de 18 arquivos em 24 lotes; todos saíram `0`,
devolveram veredito e provaram `claude-fable-5-1`. O parecer conjunto foi
**REPROVADO**.

O Manager auditou os achados contra o snapshot e confirmou oito bloqueios
distintos, embora vários lotes tenham repetido a mesma causa:

- o contrato replicado nos nove consumidores ainda permite que a “frente dona”
  crie thread ausente, sem limitar a exceção a card novo nem definir a posse;
- o checkpoint autoriza handshake positivo para qualquer thread ausente,
  inclusive quando há card ativo cuja thread obrigatória desapareceu;
- o template do init manda usar `threads/<slug>.md`, em conflito com o ponteiro
  e a thread por card `threads/T-NNN.md`;
- o mesmo template descreve `thread_root` como “raiz da frente”, permitindo
  confundi-lo com `front_root` apesar do campo estruturado do resolver;
- `plan-next` só bloqueia card de outra frente **com** thread ausente, deixando
  passar a posse alheia quando o arquivo existe; “card novo” também não separa
  criação nova de reivindicação de backlog legado;
- `stack` manda continuar a medição depois da política de falha, sem uma parada
  operacional explícita para `state: erro` ou encaminhamento para
  `state: ok` + `exists: false`;
- o lint consome, no primeiro match negado, a instrução violadora depois de
  adversativa; a contraprova real retornou um único match negado tanto para
  `Não leia ..., mas edite ...` quanto para `Não use fallback, mas procure ...`;
- o teste contratual ancora e exige o próprio texto permissivo da criação de
  thread, de modo que hoje protege a ambiguidade em vez da regra aprovada.

Não houve correção depois do snapshot. O teto autorizado está consumido em
`revisões: 4/4 · extensão: +2`.

## Autorização das correções e R5 — 2026-09-15

O dono autorizou corrigir exatamente os oito bloqueios auditados da R4 e
executar uma única R5 Fable do novo snapshot. O contador passa a
`revisões: 5/5 · extensão: +3`. Continuam fora do gate bump, commit, push,
publicação, instalação, integração e restart.

## Correções da R4 e verificação do Manager — 2026-09-15

Os oito bloqueios auditados foram corrigidos com RED/GREEN. O contrato único
dos nove consumidores agora limita criação de thread ao card criado nesta
invocação ou ao backlog legado sem ponteiro/thread que a frente reivindica e
marca. Posse alheia e thread ausente de card existente interrompem sempre. O
checkpoint diferencia projeto sem card ativo de thread obrigatória ausente; o
init usa `thread_root` do JSON e `threads/T-NNN.md`; `plan-next` separa posse,
legado e criação; `stack` para em erro/ausência; e o lint procura ocorrências
sobrepostas depois de negação/adversativa. O teste contratual protege esses
ramos em vez do texto permissivo anterior.

Prova fresca do Manager: contrato 25/25 e guardião 103/103 em Python 3.12; os
128 testes conjuntos também passaram no Python 3.9.6 de `/usr/bin/python3`.
Manifesto estrito e `git diff --check` verdes. A suíte descoberta executou 372
testes e manteve somente as quatro falhas basais externas conhecidas. O lint
manteve somente T-081 e a divergência fonte/cache 0.27.6 esperada antes de
bump/instalação, ações fora deste gate. No worktree real, o resolvedor retornou
`state: ok`, `exists: true`, `provenance: worktree`, board na `main` e
`thread_root` na frente.

## Checkpoint de recuperação pós-compactação — 2026-09-15

O Manager releu `memory/MEMORY.md`, o quadro canônico e esta thread. Os oito
bloqueios da R4 já foram corrigidos e a única R5 autorizada já terminou; ela
não será reiniciada nem duplicada. A execução cobriu 235.225/235.225 bytes em
27 lotes, todos com exit `0` e identidade `claude-fable-5-1` comprovada. Falta
auditar contra o snapshot os bloqueadores declarados nos pareceres. A `main`
compartilhada e as alterações paralelas da janela Claude permanecem fora do
escopo. Continuam vedados bump, commit, push, publicação, instalação,
integração e restart.

## Revisão Fable R5 e auditoria do Manager — 2026-09-15

A única R5 terminou sem falha operacional: o manifesto cobriu
235.225/235.225 bytes do diff sanitizado de 18 arquivos em 27 lotes; todos
saíram `0`, devolveram veredito e provaram `claude-fable-5-1`. Quatro lotes
foram marcados como **REPROVADO**.

O Manager auditou os pareceres contra o snapshot. As três denúncias dos lotes
2 e 3 sobre `kanban-status.sh .` eram falsos positivos: o modo normal usa `.`
somente como origem do resolvedor e então executa a medição com o caminho
absoluto do board canônico. Na contraprova real, a saída normal foi idêntica à
medição explícita da `main` e diferente da cópia local da worktree.

Dois bloqueios distintos são reais:

- o fim de `checkpoint.md` diz genericamente que thread inexistente não se
  verifica e mostra um handshake positivo para “thread ausente”, contradizendo
  a regra anterior que proíbe o handshake quando um card ativo aponta para uma
  thread obrigatória ausente;
- a seção de várias janelas da skill ainda nomeia o arquivo como
  `THREAD_ROOT/threads/<frente>.md`, em conflito com a thread `T-NNN.md`
  apontada pelo card e com a frente identificada por `@frente-<slug>`.

Assim, o parecer auditado da R5 é **REPROVADO por dois bloqueios reais**. Eles
não foram corrigidos porque o gate autorizava apenas as oito correções da R4 e
uma única R5. O contador permanece `revisões: 5/5 · extensão: +3`.

## Autorização das correções e R6 — 2026-09-15

O dono autorizou uma extensão delimitada `+1` para corrigir somente os dois
bloqueios auditados da R5 e executar uma única R6 Fable do novo snapshot. O
contador passa a `revisões: 6/6 · extensão: +4`. Continuam fora do gate bump,
commit, push, publicação, instalação, integração e restart.

## Correções da R5 e verificação do Manager — 2026-09-15

Os dois bloqueios foram protegidos por testes específicos que falharam antes
da correção. O checkpoint agora limita o caso sem thread ao projeto sem card
ativo desta frente e torna explícito que card ativo com thread obrigatória
ausente falha o sinal; o exemplo de handshake usa a mesma condição. A skill
agora aponta para `THREAD_ROOT/threads/T-NNN.md` e identifica a frente somente
por `@frente-<slug>`.

Depois da correção, os dois testes passaram. Contrato + guardião fecharam
130/130 no Python 3.12 e 130/130 no Python 3.9.6. A suíte descoberta executou
374 testes e manteve somente as quatro falhas basais externas conhecidas.
Manifesto estrito e `git diff --check` ficaram verdes; o lint manteve apenas
T-081 e a divergência fonte/cache 0.27.6 esperada antes de bump/instalação.

## Revisão Fable R6 e auditoria do Manager — 2026-09-15

A única R6 terminou sem falha operacional. O manifesto cobriu
240.137/240.137 bytes do diff sanitizado de 18 arquivos em 28 lotes; todos
saíram `0`, devolveram veredito e provaram `claude-fable-5-1`. O resultado foi
6 `APROVADO` e 22 `APROVADO_COM_RESSALVAS`, sem lote reprovado.

A auditoria programática dos 28 pareceres confirmou que nenhum declarou
bloqueador. O lote 20 escreveu “nenhum” e depois explicou positivamente por
que a correção da skill atende ao contrato; não era achado oculto. As
ressalvas restantes tratam de manutenção de testes, cobertura adicional,
redação histórica ou endurecimentos futuros e não demonstram quebra atual do
board canônico, do `THREAD_ROOT` nem do handshake corrigido.

O parecer reconciliado da R6 é **APROVADO COM RESSALVAS**. O review do T-076
está fechado; não executar R7. Não houve bump, commit, push, publicação,
instalação, integração ou restart.

## Checkpoint de recuperação pós-compactação — 2026-09-15

O Manager releu `memory/MEMORY.md`, o quadro canônico e esta thread antes de
retomar. O dono destinou a versão 0.27.7 ao T-076 e autorizou bump, commit,
push e integração allowlistados; o T-047 usará a próxima versão livre quando
for retomado. O T-070 também pode ser commitado, enviado e integrado, mas em
commit separado. Publicação, instalação e restart continuam fora do gate.

## Preparação da candidata 0.27.7 — 2026-09-15

Os quatro anchors foram atualizados para 0.27.7, com distinção explícita entre
a fonte candidata e a 0.27.6 ainda carregada nos hosts. O teste contratual da
versão passou. A suíte descoberta executou 374 testes e manteve somente as três
falhas basais externas causadas pelo marcador antigo do T-081; manifesto
estrito e `git diff --check` passaram. O lint apontou unicamente o mesmo T-081.
Nenhum arquivo paralelo da `main` entrou no snapshot.

## ⏭️ RETOMAR AQUI — integrar T-076 e T-070, depois iniciar T-071

Commitar e enviar o T-076 com allowlist, integrar em fonte limpa e repetir os
gates no resultado. Integrar o T-070 em commit separado, preservando a
documentação concorrente. Somente depois da integração comprovada iniciar a
implementação já aprovada do T-071. Publicação, instalação e restart continuam
fora do gate.
