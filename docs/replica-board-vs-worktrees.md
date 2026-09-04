# Réplica ao parecer — o board resolvido pelo checkout principal (`b′`)

**Contexto:** resposta ao seu parecer sobre `docs/discussao-board-vs-worktrees.md`.
**Status:** ainda em discussão. **Nada a implementar antes do meu "pode implementar".**

---

## Aceito, sem ressalva

**A `b′` vence.** Resolver o board pelo `--git-common-dir` é melhor que as duas opções que eu
tinha listado: não precisa de symlink, não tira a memória do git, e a superfície executável é
mínima. A (b) por symlink foi corretamente derrubada — as três variantes que você testou são as
três que existem, e nenhuma serve num repo público.

**O erro do `.worktreeinclude` é meu, e obrigado por devolvê-lo.** Ele é recurso do Claude Code
(copia arquivos ignorados para worktrees que *o Claude Code* cria), não do git — worktree criado
pelo Orca não passa por ele. Eu o citei como se fosse uma primitiva compartilhada pelos dois
vendors. Vale um registro no `gotchas.md`: **"`.worktreeinclude` não é do git"** — é o tipo de
suposição plausível que custaria uma implementação inteira antes de aparecer.

**Concordo com a faixa `normal`** e com a descartada da (c) pelo motivo do `T-052`.

**Concordo que o problema é presente**, e o dado dos 10 worktrees com 41–74 cards é o argumento
mais forte do parecer: não é risco futuro do Orca, é divergência já instalada.

---

## Três acréscimos verificados na máquina — nenhum derruba a `b′`

### 1. A superfície executável tem um terceiro ponto: o `lint-coerencia.py`

Confirmei os dois que você listou (`kanban-status.sh:10` e `statusline.sh:111`, ambos
`--show-toplevel`). Mas o `lint-coerencia.py` também lê a wiki por caminho, a partir da raiz que
recebe em `argv` — `memory/wiki/distribuicao.md`, `arquitetura.md`, `_elenco.md`, `MEMORY.md`
(linhas 49–50, 713, 1220, 1228, 1305–1315).

Rodado de dentro de um worktree, ele compara o **`orq/` do worktree** contra a **wiki do
worktree**. Com a `b′`, board e wiki passam a ser do principal — e o lint continua lendo local, a
menos que seja mudado junto. Aí os dois discordam: o quadro diz uma coisa, o gate diz outra.

**Decida explicitamente, e escreva a decisão:** o lint deve conferir o produto do worktree contra a
wiki **do principal** (minha inclinação, porque a wiki é uma só) ou contra a cópia local? Deixar
implícito é criar a próxima divergência silenciosa.

### 2. `--git-common-dir` devolve caminho **relativo ao cwd** — normalize antes de guardar

Medido aqui: da raiz devolve `.git`; de `orq/scripts` devolve `../../.git`. A concatenação
`"$(git rev-parse --git-common-dir)/../memory/…"` resolve certo **enquanto ninguém mudar de
diretório entre resolver e usar** — e o `kanban-status.sh` faz exatamente isso: resolve dentro de
um subshell com `cd "$dir"`. Resolver relativo lá dentro e usar fora quebra em silêncio.

Normalize para absoluto sem depender de flag nova (`--path-format=absolute` exige git ≥ 2.31, e a
versão do Mac não está verificada):

```sh
root=$(cd "$dir" 2>/dev/null && cd "$(git rev-parse --git-common-dir)/.." 2>/dev/null && pwd) \
  || root="$dir"
```

Mantém o fallback atual (`|| root="$dir"`) para diretório sem git, que hoje existe e não pode
regredir.

### 3. O risco que a `b′` introduz, e que o parecer não nomeia: acoplamento ao branch do principal

A `b′` troca "bifurcação por worktree" por outra dependência: board e wiki passam a ser **os
arquivos do checkout principal**, no branch que estiver lá. Três consequências:

- o `git status` do principal fica permanentemente sujo com `memory/`;
- o commit do card acontece no branch do principal, **não** no branch da frente — bom para não
  bifurcar, mas significa que o commit do implementer deixa de carregar o movimento do board;
- se eu (ou um agente) der `git checkout` no principal, `memory/` **muda debaixo das frentes que
  estão rodando** — inclusive o board que elas acabaram de ler.

O terceiro é o único novo, e é o que merece regra escrita: **o checkout principal fica sempre no
branch base; trabalho de frente acontece em worktree.** Se essa regra não for viável, diga — ela é
condição da `b′`, não um detalhe de operação.

---

## Sobre o critério de teste

O seu critério serve, com a contraprova — que é a parte que eu não teria pedido e que evita o teste
passar por acidente. Acrescento **um passo**: rodar também o `lint-coerencia.py` de dentro de um
worktree e registrar **qual wiki ele leu**, para que o item 1 acima não fique decidido por omissão.

---

## O que eu quero agora

1. Sua resposta ao item 1 (o lint) e ao item 3 (a regra do branch base no principal).
2. Se ambos couberem sem crescer, atualize o `T-076` com os três acréscimos e mantenha `normal`.
3. Se o item 3 exigir mudar texto de protocolo (`_schema.md`, "Várias janelas"), diga agora — não
   depois, no meio da implementação.
4. Continua valendo: **não implemente** antes do meu "pode implementar".
