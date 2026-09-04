# Decisão sobre a `b′` — e duas coisas antes de implementar

**Contexto:** fecha a discussão de `docs/discussao-board-vs-worktrees.md` +
`docs/replica-board-vs-worktrees.md`. **Ainda não é "pode implementar".**

---

## As duas decisões que você pediu

**1. O lint segue a mesma raiz do board — o principal.** Sua inclinação está certa e é a minha:
`distribuicao.md` e `arquitetura.md` são instrução viva do projeto, não do branch. Um gate que
valida o produto contra uma cópia congelada da wiki é um gate que aprova o errado. Escreva a
decisão no card, com a razão em uma linha, para não ser re-litigada.

**2. A regra do branch base vira requisito, não costume.** Aceito sua correção: o repo já pratica
isso. O que muda é o status — e o que eu quero é a **falha visível** que você mesmo mencionou. Se
o principal sair do branch base com frente em execução, alguém tem que ser avisado. Sem isso, a
regra é costume outra vez, só que agora com uma dependência técnica pendurada nela.

---

## O que eu quero resolvido ANTES da `b′` — e não é implementação

**Os 7 worktrees com edições de `memory/` não commitadas são trabalho pendente, não só evidência.**

Você os apresentou como prova de que a bifurcação já ocorreu, e a prova é boa. Mas repare no que
a `b′` faz com eles: a partir dela, todo script passa a ler o board do principal, e essas cópias
locais deixam de ser lidas — continuam no disco, rastreadas pelo git, **invisíveis**. O defeito
muda de "divergente" para "órfão silencioso", que é pior de achar.

E há o passo seguinte, que é o que me preocupa de verdade: no Orca, encerrar uma tarefa é
*"um clique remove o worktree e o branch"*. Aplicada a `b′` sem triagem, o primeiro clique
desses **destrói permanentemente** edições de `KANBAN.md`, `MEMORY.md`, `fixes-history.md` e
threads que ninguém mais lê e por isso ninguém mais lembra que existem.

**Então a ordem é: triagem primeiro, `b′` depois.** Quero um inventário — por worktree, quais
arquivos de `memory/` estão sujos e o que o diff diz — e uma recomendação por item: recuperar
para a wiki/board do principal, ou descartar com o motivo. Isso é card próprio, `leve` ou
`normal`, e ele **bloqueia** o `T-076`. Não é preciosismo: é o único momento em que esse
trabalho ainda é recuperável sem arqueologia.

---

## O buraco que nós dois deixamos passar: os scripts resolvem, o Manager não

A sua conta de superfície executável está certa — e é justamente por isso que ela não é a
superfície toda. Os scripts vão resolver o board pelo `--git-common-dir`. Mas **quem mais escreve
no board é o Manager**, e ele escreve por caminho: a `SKILL.md`, o `checkpoint.md` e o `_schema.md`
dizem `memory/wiki/KANBAN.md`, caminho relativo. Um Manager rodando dentro de um worktree resolve
isso contra o cwd dele e edita a cópia local — em silêncio, exatamente como hoje.

Ou seja: a `b′` conserta a **leitura** (statusline, quadro, lint) e deixa a **escrita** como está.
Meio conserto é pior que nenhum, porque o quadro passa a mostrar o board certo enquanto o card foi
movido no errado.

Não vou escolher o mecanismo por você — quero seu parecer sobre estes três, com custo:

- **(i) Texto:** as instruções deixam de citar caminho relativo e passam a nomear a resolução
  canônica (um helper, ex.: `orq/scripts/board-path.sh`, que devolve o caminho absoluto). Barato,
  mas depende de o Manager obedecer — e a lição do `T-025` é que gatilho por texto falha.
- **(ii) Guarda mecânica:** hook `PreToolUse` que recusa `Edit`/`Write` em `memory/` quando o cwd é
  worktree, dizendo o caminho certo. Determinístico, mas é bloqueio — e a `0.25.0` acabou de tirar
  todos os `decision: block` do guardião. Reintroduzir um exige justificar por que este é diferente
  (minha leitura: o guardião bloqueava *conversa*; este bloquearia *destino de escrita errado*, que
  é da mesma família dos gates, não da fluidez).
- **(iii) Ausência física:** `sparse-checkout` por worktree, para `memory/` nem existir lá. Elegante
  em teoria; quero saber se na prática o `Write` só recria a pasta e devolve o problema, e o que
  isso faz com `git status` do worktree.

---

## Estado do que já está fechado (não re-litigar)

- `b′` vence — sem symlink, com a memória versionada.
- `.worktreeinclude` não é do git → `gotchas.md`, com o crédito da correção.
- (c) descartada pelo `T-052`.
- `--git-common-dir` normalizado para absoluto, com o fallback atual preservado.
- Critério de teste: duas frentes em worktrees distintos + contraprova obrigatória + o passo do
  lint (registrar qual wiki ele leu).

## O que eu quero de você agora

1. Parecer sobre (i)/(ii)/(iii) da escrita, com custo — e a sua recomendação.
2. O card de **triagem dos 7 worktrees**, marcado como bloqueador do `T-076`.
3. `T-076` atualizado com as duas decisões do topo. Faixa: reavalie — se a escrita entrar no
   mesmo card, `normal` pode não segurar.
4. Continua valendo: **não implemente** antes do meu "pode implementar".
