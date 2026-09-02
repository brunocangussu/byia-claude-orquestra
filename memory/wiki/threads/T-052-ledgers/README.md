# Ledgers de prova da reconciliação (T-052)

Estes cinco scripts são a **evidência executável** de que a fusão não perdeu regra nenhuma.
Persistidos aqui em 2026-09-01 porque viviam só no scratchpad da sessão — o mesmo modo de perda
que quase travou este card (ver `T-051-pareceres.md`, e o gotcha "identificador de job fantasma").

| Script | O que prova |
|---|---|
| `ledger_t051.py` | os **25 bloqueadores** corrigidos nas 7 rodadas de review da `0.24.0` continuam valendo |
| `ledger_remoto.py` | as **4 obrigações** que vieram da `0.22.x` publicada continuam valendo |
| `ledger_revisao_t052.py` | rodada 1 da revisão externa: os **3 bloqueadores + 2 riscos** continuam corrigidos, e os dois guardas novos do lint funcionam |
| `ledger_revisao2_t052.py` | rodada 2: os **3 + 2** seguintes — três gates na doc de release, camada 4 host-aware, fonte limpa no ramo Claude, fronteira do `memory/`, elenco em dois eixos |
| `ledger_revisao3_t052.py` | rodada 3: o bump coordenado é **passo** da seção `Desenvolver o plugin`, e o guarda **ancora na seção** (nos DOIS procedimentos ordenados) em vez de procurar no arquivo inteiro |

**O que torna isto prova e não teatro: os ledgers DISCRIMINAM.**

| árvore | `t051` | `remoto` | `revisao` | `revisao2` | `revisao3` |
|---|---|---|---|---|---|
| `dcc350b` — golden local (`0.24.0`) | **25/25** | 0/4 | — | — | — |
| `6fde3e3` — remoto publicado (`0.22.7`) | **0/25** | **4/4** | — | — | — |
| reconciliada, antes da rodada 1 | 25/25 | 4/4 | **0/12** | — | — |
| reconciliada, antes da rodada 2 | 25/25 | 4/4 | 12/12 | **1/8** | — |
| reconciliada, antes da rodada 3 | 25/25 | 4/4 | 12/12 | 8/8 | **0/6** |
| reconciliada, **estado atual** | **25/25** | **4/4** | **12/12** | **8/8** | **6/6** |

O `1/8` da penúltima linha é o probe `B1-x`, que mede uma **capacidade** (o `discover` já achava os
cinco módulos) e não o texto — passar antes é o comportamento correto dele. Os outros sete só passam
depois das correções.

Um probe que passa em qualquer árvore não prova nada. Estes reprovam exatamente onde a regra
não existe — foi assim que se validou o próprio ledger antes de usá-lo como prova.

⚠️ 8 dos 25 são **contraprovas negativas** (mutação + lint). Foram endurecidas depois de se
descobrir que 3 passavam no remoto **pelo motivo errado** — divergência colateral de cache, não o
guarda certo. Hoje exigem a **mensagem específica** do guarda, não apenas `exit != 0`.

**Limite declarado:** a rodada 1 é a única sem saída bruta hashada — foi transcrita do relatório do
subagente. O `25/25` é honesto sobre o que está no ledger; para aquela rodada a fonte é a
transcrição, não um artefato com hash.

## Como rodar

```bash
python3 memory/wiki/threads/T-052-ledgers/ledger_t051.py .          # 25/25
python3 memory/wiki/threads/T-052-ledgers/ledger_remoto.py .        # 4/4
python3 memory/wiki/threads/T-052-ledgers/ledger_revisao_t052.py .  # 12/12
python3 memory/wiki/threads/T-052-ledgers/ledger_revisao2_t052.py . # 8/8
python3 memory/wiki/threads/T-052-ledgers/ledger_revisao3_t052.py . # 6/6
```

A raiz vem por argumento — nenhum script tem caminho desta máquina embutido, então dá para apontar
para um clone limpo, para um worktree ou para uma árvore exportada por `git archive`.

⚠️ **Armadilha para quem for endurecer o lint:** as contraprovas negativas carregam *fixtures* com
strings proibidas de propósito (`Kimi`, `Moonshot`, `PAINEL PARCIAL`, `diff -rq`). Hoje elas não
disparam nada, porque o guarda de host aposentado varre `orq/`, os três arquivos da raiz e só as
**duas páginas vivas nominais** de `memory/wiki/`. Se algum dia alguém estender a varredura a
`memory/wiki/threads/`, este diretório passa a reprovar o lint — e a correção certa é **excluir os
ledgers nominalmente**, nunca afrouxar o guarda.
