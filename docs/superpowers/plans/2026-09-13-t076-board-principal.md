# T-076 — um board operacional entre worktrees

**Estado:** escopo board-only aprovado pelo dono em 2026-09-14 para implementação no worktree
T-076. Nenhum bump, commit, push, publicação, instalação ou restart está incluído.

**Problema observado:** `kanban-status.sh` usa `git rev-parse --show-toplevel`, que aponta ao
worktree atual. Nesta máquina, a mesma versão de código mostrou 93 cards no checkout principal e
92 no worktree T-076. `quadro`, `plan-next` e `checkpoint` também orientam leitura/escrita do
`memory/wiki/KANBAN.md` relativo; corrigir só a statusline deixaria dois boards operacionais.

**Escolha recomendada:** limitar o T-076 ao **board**. Índice, threads, elenco e log continuam com
as regras atuais por frente; sua centralização requer decisão e card próprios. Resolver o caminho
não migra alterações órfãs já feitas em worktrees — em particular, o estado local do T-062 precisa
de reconciliação explícita, sem copiar `memory/` inteiro nem sobrescrever o checkout principal.

## Contrato proposto

1. Separar três raízes: pacote do plugin, worktree que executa código e checkout principal que
   guarda o board operacional. O Manager lê e altera somente o `KANBAN.md` deste último, após
   reler a linha no disco; worker só pede movimento, nunca escreve o board.
2. A partir de um diretório explícito (ou cwd), normalizar a origem com `realpath` e obter
   `git worktree list --porcelain -z`. O primeiro registro é candidato a principal somente depois de
   validar que não é o Git dir de `git init --separate-git-dir`; nesse layout, use a raiz devolvida
   por `git rev-parse --show-toplevel` apenas quando a prova de origem for suficiente, ou falhe
   visivelmente. Processar bytes delimitados por NUL; não inferir a raiz pela branch `main`, pelo
   texto separado por espaços ou pelo pai de `--git-common-dir`. Conferir o mesmo common-dir do
   checkout de origem. Argumentos de subprocesso são lista, nunca `eval`.
3. Ausência de metadado Git e binário `git` indisponível são sinais distintos. Só a ausência de
   metadado `.git` no diretório ou em seus ancestrais permite manter o board local; nesse caso não
   há indício de checkout concorrente para resolver. Se houver metadado e o binário `git` estiver
   indisponível — ou se houver timeout, saída malformada, principal bare, inacessível ou
   inconsistente — mostrar erro distinto de “sem board”; nunca cair silenciosamente no board antigo
   do worktree. Principal válido sem board continua sendo “projeto sem board” (saída vazia), mesmo
   que o worktree tenha uma cópia antiga.
4. `kanban-status.sh <dir>` é o modo normal de resumo, `--resolver <dir>` é o modo estruturado JSON
   e `--board-path <absoluto>` é recursão interna. O resolver fornece caminho absoluto +
   existência/proveniência e também `front_root` e `thread_root` absolutos. Manter o script auto-suficiente:
   a instalação hoje copia somente o par `statusline.sh` + `kanban-status.sh`. Python stdlib embutido
   no segundo script é a proposta para processar NUL; falta de `python3` vira diagnóstico visível,
   não fallback stale. Não criar um terceiro arquivo copiado sem redesenhar F1/F2 e seus testes.
5. `quadro`, `plan-next`, `implement-next`, `checkpoint`, `stack`, `init`, a skill `orq`, o schema e
   os textos de retomada do guardião devem apontar ao board canônico antes de ler, criar ou mover
   card. THREAD_ROOT é o `thread_root` absoluto devolvido pelo resolver: `memory/wiki` da raiz do projeto/worktree que iniciou a operação, nunca do `BOARD_CANONICO`. O ponteiro `threads/...` do card só identifica a thread: leia/escreva exclusivamente `THREAD_ROOT/threads/...`; ausência ali proíbe busca/fallback no principal ou em outra worktree, mas a frente dona pode criar nova thread ali. A validação de fonte/fixtures do
   `lint-coerencia.py` continua respeitando a raiz explícita, sem redirecionamento para a main.

## Plano de implementação aprovado — board-only

1. **RED:** ampliar `test_kanban_status.py` com repositório temporário e worktree Git reais:
   principal com A/B, worktree antigo só A; provar que hoje cada um conta diferente. Testar raiz,
   subpasta, detached, espaços/Unicode/newline, `--separate-git-dir`, sem Git, principal sem board,
   principal indisponível/bare, Git sem `-z`, falta de Python e cópia isolada do par de scripts.
   Falha deve distinguir erro de resolução de ausência legítima de board.
2. Implementar o resolver no `kanban-status.sh` sem alterar o parser awk de cards. Expor modo
   estruturado para os comandos; checar o mesmo caminho nos dois modos. `statusline.sh` deve
   transmitir a degradação sem travar o host. Repetir os testes GREEN.
3. Atualizar só os consumidores operacionais listados no contrato. Testes de instrução/lint
   devem reprovar referência que volte ao board do worktree. O `lint-coerencia.py` com raiz de
   fixture deve continuar lendo a fixture, não a main. `init.md` não pode criar board duplicado
   num worktree quando o principal já o tem.
4. Fazer revisão independente read-only do diff e auditar cenários de falha. Só então atualizar
   documentação atemporal e executar os três gates do projeto: suíte completa por `discover` com
   `PYTHONDONTWRITEBYTECODE=1`, manifesto estrito e lint de coerência. Regressões basais de outros
   cards devem ser reportadas separadamente.
5. Para validar após release autorizado: abrir duas frentes em worktrees, consultar o quadro nas
   duas, mover um card de teste pelo Manager em uma e confirmar a mudança na outra, sem alterar o
   board local antigo. Checar também erro visível se o principal ficar inacessível. Instalação,
   caches e restart exigem autorização própria.

**Risco residual declarado:** board comum não fornece transação/exclusão mútua entre Managers,
nem centraliza as outras páginas de `memory/`. A edição de linha exige releitura e verificação;
conciliar estados órfãos é trabalho separado. Nunca dar `git add .` ou incluir alterações da
janela Claude ao integrar o card.

**Gate do dono:** board-only aprovado em 2026-09-14 pela resposta “prossiga com sua recomendacao”
ao pedido explícito de confirmar esse escopo. Migração das cópias antigas e memória integral ficam
para decisões separadas. Bump, commit, push e release continuam sem autorização.

## Nota de execução — 2026-09-14

O item 2 do contrato trata o primeiro registro de `git worktree list --porcelain -z` apenas como
candidato ao checkout principal. `git init --separate-git-dir` pode listar o diretório
de metadados como primeiro registro. No checkout que aponta diretamente a esse Git dir, o
resolvedor consegue validar a origem; numa worktree derivada, o Git não forneceu `core.worktree`
nem outro caminho comprovável ao checkout principal. O comportamento implementado nessa borda
é erro explícito, sem fallback ao board antigo. Não interpretar esse caso como paridade funcional
entre todas as formas de worktree; exigir nova prova antes de ampliar a resolução.

## Adendo de contrato R3 — 2026-09-15

- O resolver normaliza a origem com `realpath`; origem inexistente ou que não seja diretório é
  `origem-inexistente`. Ele limpa `GIT_DIR`, `GIT_WORK_TREE`, `GIT_COMMON_DIR` e
  `GIT_INDEX_FILE` dos subprocessos Git, captura `OSError` como erro estruturado, retorna
  `code: null` no sucesso e distingue a proveniência `local`, `principal` e `worktree`.
  `--board-path` aceita somente caminho absoluto. Em frente sem Git, a raiz da frente é o
  diretório de origem fornecido, não um `cd` ao checkout principal.
- O Manager resolve uma vez na frente atual e só então passa `BOARD_CANONICO=<board>` e
  `THREAD_ROOT=<thread_root>` absolutos aos papéis de writer, reviewer e docs. Papéis
  despachados não re-resolvem nem mudam a raiz de memória. `state: ok` com `exists: false`
  encaminha ao init e não autoriza ler um board inexistente; erro do resolver não permite um
  handshake positivo de checkpoint.
- No template criado por init, `board` é `BOARD_CANONICO`, `thread_root` é `THREAD_ROOT` e o
  ponteiro do card permanece `threads/...`, relativo a `THREAD_ROOT`. Uma frente só cria uma
  thread nova na sua própria `THREAD_ROOT`; card existente já marcado cuja thread não exista
  nela para e relata, sem cópia. Ao reivindicar card novo, a frente escolhe um identificador
  conceitual estável `@frente-<slug>`; não o deriva do basename da worktree.
- Antes de qualquer chamada, consumidores comprovam `ORQ_PACKAGE_ROOT` absoluto, existente e
  com `scripts/kanban-status.sh`. Sem JSON, relatam `exit` e `stderr`; só usam `code` quando
  houver JSON estruturado de erro. Esta errata substitui qualquer redação anterior que misture
  ausência de Git, indisponibilidade do binário Git ou raiz do board com a raiz da frente.
