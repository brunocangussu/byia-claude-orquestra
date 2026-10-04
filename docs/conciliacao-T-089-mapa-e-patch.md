# Conciliação T-089 × T-131 × T-143 — mapa e patch proposto

Data: 2026-10-04. Frente `@frente-companion-runtime` · host Claude. **Somente leitura e documento novo:**
nenhuma fonte, board, thread, elenco ou manifesto foi alterado; nada foi aplicado, commitado ou enviado;
nenhuma chamada externa. O patch está em `docs/patches/T-089-sobre-T-131-T-143.patch`, **não aplicado**.

## Estado lido

| Frente | Checkout | Base | Estado |
|---|---|---|---|
| T-089 | branch `claude/t089-companion-identidade` | `4e58e7f` | commit `2a879d9`, preservado |
| T-131 | `~/.codex/worktrees/t131-elenco-sol61-luna6/…` | `4e58e7f` | alterações **não commitadas**; R6 liberada, ainda não despachada |
| T-143 | `~/.codex/worktrees/t143-continuidade-aprovada/…` | `4e58e7f` | alterações **não commitadas**; em desenho |
| `main` | raiz | `4e58e7f` | sem nenhuma das três; versão 0.27.11 |

⚠️ **As duas fontes ainda se movem.** O resultado abaixo vale para o estado de 2026-10-04 15:00; antes de
aplicar, reconfira os hashes da tabela "Drift" e recalcule.

## Mapa dos trechos sobrepostos

Linhas da base `4e58e7f`. "Vizinho" = hunks a ≤ 5 linhas, que o `git merge-file` trata como conflito.

| Arquivo | T-089 | T-131 | T-143 | Resultado da fusão |
|---|---|---|---|---|
| `orq/skills/orq/SKILL.md` | 263 (+10, reúso Companion) | 168 | 441 | **limpo** — três regiões distintas |
| `orq/commands/revisar.md` | 80, 87 (`--wait`; regra curta) | 56, 92, 101, 106, 122, 127 | 50, 213 | **limpo** — 87 e 92 são vizinhos próximos, sem sobreposição de texto |
| `orq/commands/elenco.md` | 179, 358, 386, 389 | 181, 359, 385 (+ outros 14) | — | **2 conflitos**: 358×359 e 386×385 (linhas das tabelas de vias e da Matriz) |
| `orq/commands/plan-next.md` | 60, 66 | — | 107, 114 | **limpo** |
| `memory/wiki/arquitetura.md` | 123 | — | 214, 316, 423 | **limpo** |
| `memory/wiki/_elenco.md` | 67, 125 | não toca | não toca | só T-089 — **elenco vivo continua protegido**: o patch altera só a linha da via `codex`, a célula OpenAI da Matriz e o parágrafo da regra curta logo abaixo dela, nunca `## Times por host` |
| `orq/scripts/test_companion_thread_reuse.py` | +165 | não toca | não toca | só T-089 |

### Os dois conflitos de `elenco.md` e a resolução proposta

Os dois lados reescreveram linhas vizinhas das mesmas tabelas. Texto concorrente não se anula; soma-se.

1. **Tabela de vias (~l.358–359).** Linha `codex`: manter a versão do T-089 (condição de identidade do
   `threadId`). Linha `runner-opus`: manter a do T-131 (`<alias-ou-id>`, identidade exata para ID, prefixo
   para alias legado). São linhas diferentes: nada se perde.
2. **Matriz (~l.385–386).** Linha Anthropic: **a do T-131** (modelo comprovado nessa célula, `claude-opus-5-5`
   e mapa de prova ampliado). Linha OpenAI: **a do T-131 mais a cláusula do T-089** no fim do campo
   host Claude: `; continuação só é aceita com \`threadId\` devolvido igual ao solicitado`.

## Contratos que sobrevivem e testes que os guardam

1. Continuação aceita só com sucesso, JSON válido, `status: 0`, `jobId` e `threadId` não vazios, e `threadId`
   devolvido **igual ao solicitado**.
2. Divergência preserva o vínculo anterior; registra IDs, runtime e motivo; sem `rawOutput` como prova,
   fallback, task nova ou `--resume-last`.
3. `--wait` pertence ao envelope do `codex:codex-rescue`, nunca ao `task`.
4. `--write` segue proibido; frase-âncora literal nas cinco superfícies.
5. A via `codex` do `_elenco.md` obedece a `## Times por host` (`gpt-6-astra@xhigh` no time atual), sem `@ max`.
6. Regra curta nos quatro consumidores: `plan-next`, `revisar`, `elenco`, `_elenco`.

Testes: `test_companion_thread_reuse.py` (6 novos), mais `test_write_flag_guard.py` intacto. Nenhum precisou
de alteração ao conciliar.

## Prova da fusão (árvore temporária, fora do repositório)

Árvore = base `4e58e7f` + arquivos alterados do T-131 e do T-143 + este patch.

- Patch aplica com `git apply --check` sobre a árvore **sem** T-089 e **reproduz byte a byte** a árvore conciliada.
- **535 testes OK**, `claude plugin validate --strict` exit 0, `lint-coerencia.py` exit 0.
- Um primeiro ensaio deu 2 falhas, ambas do meu ensaio, não da fusão: eu não tinha copiado para a árvore a
  mudança do T-143 em `memory/wiki/_schema.md`, que o teste dele exige. Corrigido e reexecutado.

## O que **não** está provado

- **Revisão independente.** O snapshot final do T-089 (rodada 2 corrigida) **nunca** foi re-revisado pelo
  vendor oposto; a pendência está registrada. A fusão **também não** foi revisada. A prova acima é de
  testes e mutações, não de parecer.
- **Fontes em movimento.** T-131 e T-143 não estão commitados e o T-131 ainda aguarda a R6 externa; se o
  snapshot deles mudar, o patch precisa ser recalculado.
- **T-143 em desenho.** O resultado limpo mostra ausência de colisão de texto, não de colisão de política.
  O contrato de continuidade do T-143 (aprovação sem bloqueios redundantes) foi lido só pelos arquivos que
  ele já alterou; não foi decidido aqui.
- A causa das falhas anteriores da CLI do T-131 e a capacidade real de conta não são tema deste documento.

## Sequência sugerida (nada disso foi executado)

1. T-131 e T-143 fecham suas fontes (commit local deles). **O T-089 só entra depois**, por ser o menor e o
   único cujos hunks ficam confinados.
2. Em branch de integração a partir da fonte final, aplicar `git apply --3way` do patch; reresolver os dois
   conflitos de `elenco.md` pela regra acima se a base tiver mudado.
3. Rodar os três comandos obrigatórios e a revisão independente da fusão (vendor oposto, uma rodada).
4. Só então, com autorização do dono: versão única livre nas quatro âncoras, commit, release. A versão
   **não** é reservada aqui.

## Drift — confira antes de aplicar

| Origem | Arquivo | SHA-256 (12) |
|---|---|---|
| T-131 | `orq/skills/orq/SKILL.md` | `7514d671c35b` |
| T-131 | `orq/commands/revisar.md` | `04046fabba95` |
| T-131 | `orq/commands/elenco.md` | `18b799f3202e` |
| T-143 | `orq/skills/orq/SKILL.md` | `aaf99f2535eb` |
| T-143 | `orq/commands/revisar.md` | `f1a5574d420c` |
| T-143 | `orq/commands/plan-next.md` | `1f6bd3a0f042` |
| T-143 | `memory/wiki/arquitetura.md` | `0518e9ee3ea3` |
| patch | `docs/patches/T-089-sobre-T-131-T-143.patch` | `acfff0602b6c` |
