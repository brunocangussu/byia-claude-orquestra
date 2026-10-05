# Handoff para a conciliação na `main` — T-144/T-146 (medidor de progresso)

> Frente `@frente-mods` · janela Claude · 2026-10-04. Este arquivo existe só no checkout principal e
> não está rastreado. Thread completa: `memory/wiki/threads/T-144-mods-claude-code.md`.

## Mensagem para encaminhar ao chat da conciliação

```text
Conciliar na main a branch claude/t144-medidor-progresso (frente @frente-mods, cards T-144 e T-146).
Leia antes: docs/handoff-claude-T-144-T-146-conciliacao-2026-10-04.md.
- Base: main em 4e58e7f. Dois commits locais, nunca publicados: ba523e9 (0.28.0, fase 1) e 064e726 (0.29.0, fase 2).
- Worktree limpa em ../byia-claude-orquestra-worktrees/t144-medidor-progresso.
- A versão 0.29.0 é CANDIDATA. Renumere na ordem de merge que você definir. São 4 âncoras mais arquitetura.md:3,
  e o ContextGuardReleaseVersionTest exige que as 4 batam entre si.
- Preserve os contratos da seção "Contratos". Depois de cada merge, rode os 3 gates: suíte descoberta, validate --strict e lint.
- Os cards T-144 e T-146 estão em [?]. Nenhum push, publicação ou instalação foi feito.
```

## O que a branch traz

**Fase 1 — `ba523e9` (T-144):**
- `orq/scripts/progress.py` (stdlib): ledger por card ou goal em `<front_root>/.orq/progress/v1/`,
  autoignorado pelo Git.
  - CLI: `begin`/`plan`/`start`/`done`/`drop`/`reopen`/`phase`/`pause`/`resume`/`close`/`claim`/`show`/`watch`.
  - Lock canônico e troca atômica.
- `orq/scripts/kanban-status.sh --card-state`.
- Schema `progress-ledger-v1.json`.
- Procedimento em `orq/skills/orq/references/progress.md`.
- `plan-next.md` passa a exigir uma tabela de passos.
- `implement-next.md` §0b define os marcos do Manager.
- `checkpoint.md` grava ledger e chave na thread.

**Fase 2 — `064e726` (T-146):**
- Recibo com `view`.
- `bind --native-key`, com `v1/sessions/`.
- `orq/scripts/progress-hook.py`: hook consultivo com anúncio único e lembrete único. Nunca bloqueia.
- 2 grupos próprios no `hooks.json`.
- Segmento do medidor na `statusline.sh`.
- `init.md` instala o trio `statusline.sh` + `kanban-status.sh` + `progress.py`, com rollback por
  hash.
- `get_goal` opcional no Codex.
- Schema `progress-binding-v1.json`.

**Docs:** `arquitetura.md` (seção "Medidor de progresso" e riscos aceitos), README e
`distribuicao.md`.

**Números:** 27 arquivos, +8.299/−56. Suíte 447 → 730. `validate --strict`, lint e `diff --check`
verdes na branch.

**Revisão:** cross-vendor, Astra e depois Sol 6.1 `@xhigh`, APROVADO_COM_RESSALVAS nas duas fases.
Os riscos aceitos estão documentados em `arquitetura.md`.

## Sobreposição com as outras branches (base `4e58e7f`)

| Branch | Arquivos em comum com a T-144 |
|---|---|
| `codex/t098-jev-candidata-r5` | nenhum |
| `claude/t089-companion-identidade` | `memory/wiki/arquitetura.md`, `orq/commands/plan-next.md`, `orq/skills/orq/SKILL.md` |
| `codex/t131-elenco-sol61-luna6` | `orq/commands/implement-next.md`, `init.md`, `plan-next.md`, `orq/skills/orq/SKILL.md`, `README.md` |
| `codex/t143-continuidade-aprovada` | `memory/wiki/arquitetura.md`, `orq/commands/checkpoint.md`, `implement-next.md`, `plan-next.md`, `orq/skills/orq/SKILL.md` |
| worktree T-139 (HEAD desanexado em `a82a35f`, base antiga) | as **4 âncoras de versão**, `checkpoint.md`, `init.md`, `plan-next.md`, `test_canonical_board_contract.py`, `hosts/codex.md`, `SKILL.md`, `README.md` |

Os trechos que esta branch mexe nesses arquivos são localizados:
- **`SKILL.md`:** um parágrafo de encaminhamento ao `references/progress.md`.
- **`plan-next.md`:** a exigência da tabela de passos.
- **`implement-next.md`:** a seção §0b e os marcos.
- **`checkpoint.md`:** o registro do ledger na thread.
- **`init.md`:** a instalação da statusline passou de par para trio, com o bloco "Conjunto
  indivisível, backup e rollback". Esse é o maior trecho.
- **`arquitetura.md`:** a tabela de assets e a seção nova.

## Contratos que a conciliação deve preservar

1. **`orq/hooks/hooks.json`:**
   - os **6 grupos do `context-guard`** ficam exatamente como na base;
   - os **2 grupos do medidor** (`PostToolUse` sem matcher; `SessionStart` com
     `^(startup|resume|clear|compact|fork)$`) chamam `progress-hook.py`;
   - `test_context_guard` (ajustado para aceitar grupos que sejam só do `progress-hook.py`) e
     `test_progress_hooks` provam os dois lados.
2. **Duas chaves.** `--session-key` é a chave de **dono** e autoriza mutação; `--native-key` só
   serve ao `bind`. Não unificar os nomes: a ambiguidade foi um achado de revisão.
3. **Hook consultivo.** Ele nunca emite `block`, `deny` nem `continue`, e nunca abre transcript,
   `tool_input` ou `tool_response`. A saída rápida acontece antes de importar o núcleo.
4. **`statusline.sh`.** Lê o stdin uma vez só. Sem medidor, sem `jq`, sem `python3` ou sem o
   script ao lado, a barra fica idêntica à da base. O pré-filtro usa `cd -P`/`pwd -P`.
5. **`init.md`.**
   - O trio é indivisível na **instalação**.
   - O rollback é feito **arquivo a arquivo**, contra um hash registrado **antes** de cada
     operação.
   - Alteração concorrente é preservada e relatada.
6. **Percentual.** É sempre "do plano": 100% nunca é DONE, e o medidor nunca move card.
7. **Suíte descoberta**, nunca enumerada: `test_progress*.py` entra sozinho.

## Versão

- **0.28.0 (fase 1) e 0.29.0 (fase 2) são números candidatos desta branch.** Ao renumerar, mude
  juntos:
  - `orq/.claude-plugin/plugin.json`;
  - `.claude-plugin/marketplace.json`;
  - a seção Status do `README.md`;
  - `memory/MEMORY.md` (linha **Versão**);
  - `memory/wiki/arquitetura.md:3`.
- O `memory/MEMORY.md` da branch traz só a linha de versão alterada. O índice operacional
  verdadeiro está no checkout principal (ver abaixo).

## Estado desta frente no checkout principal (não commitado, por regra do projeto)

- **Board:** `T-144` e `T-146` em `[?]`; `T-147` (fase 3) e `T-145` (contagens de testes) no
  backlog.
- **Thread:** `memory/wiki/threads/T-144-mods-claude-code.md`, não rastreada.
- **`memory/fixes-history.md`:** 3 entradas `@frente-mods` no topo.
- **`memory/gotchas.md`:** 2 entradas ao fim.
- **`memory/MEMORY.md`:** parágrafo T-144/T-146 e uma linha na tabela de páginas.
- **`memory/wiki/_elenco.md`:** host Claude `planner·sistema` e `reviewer` em `gpt-6.1-sol@xhigh`,
  como desvio do `padrao`. Já vale para as janelas Claude, porque é lido do disco.
- **`docs/`:** `plano_T-144-medidor-progresso.md` (plano + ERRATA), `parecer_T-144-codex.md` e este
  handoff, todos não rastreados.
- **`.orq/progress/`:** ledger real do T-146, ignorado pelo Git. Não commitar.

Se a conciliação levar esses arquivos para a `main`, eles não conflitam com a branch. A exceção é o
`memory/MEMORY.md`: a branch muda só a linha **Versão**, e o principal tem o parágrafo e a linha de
tabela.

## Pendente depois do merge (do dono)

1. **Release:** versão final, push, publicação e instalação nos dois hosts. Depois, rodar
   `verify_installed_cache.py` a partir da fonte limpa.
   ⚠️ T-093: atualizar o plugin derruba a sessão viva do Codex.
2. **Validação prática dos `[?]`:**
   - **Já agora:** `watch` num terminal ao lado, direto da branch.
   - **Só depois do release e do restart:** o lembrete por hook e o segmento na statusline, porque
     o cache é indexado por versão.
3. **`T-147`:** decidir o espelho opt-in via `update_plan` no Codex (parecer do Codex, item 1) antes
   da fase 3.
4. **`T-145`:** trocar as contagens fixas de testes no README e no `distribuicao.md`.
