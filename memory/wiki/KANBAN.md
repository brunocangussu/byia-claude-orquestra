# KANBAN — Orquestra (`orq`)

> Fonte da verdade do trabalho. **Só o Manager (a sessão principal) move cards.**
> Marcadores: `[ ]` backlog · `[>]` planejando · `[!]` esperando o dono · `[~]` implementando ·
> `[?]` aguardando validação · `[x]` feito.

---

## ⏸️ Esperando você

_(vazio)_

---

## 🟡 Fazendo

_(vazio)_

---

## 🟣 Validar

_(vazio)_

---

## 🔵 Backlog

- [ ] `T-008` Lint de coerência interna — 🔴 script que falha se um comando/skill citado não existir. Teria pego o `/orquestra:*` que sobreviveu 3 releases. Barato e determinístico: `grep` das referências `/orq:*` e `` `skill` `` contra o que existe em `commands/` e `skills/`. Roda no `validate`.
- [ ] `T-001` Hooks de segurança — 🔴 `PreToolUse` em `Bash` negando `git push`, merge, deploy, migration e SQL de escrita. Camada 1 do roadmap#1. Autocontida: não depende de saber quem chamou. **É o que transforma as promessas do modo noturno de disciplina em garantia — sem isso o T-006 não sai do papel.**
- [ ] `T-003` Piloto end-to-end — rodar o T-008 pelo fluxo completo (`plan-next` → gate → `implement-next` → painel → validate) e registrar **onde o fluxo travou**. Entregável é o relatório de atrito, não o código. Pré-requisito honesto do T-002 e do T-006.
- [ ] `T-002` Hooks de processo — `PreToolUse` em `Edit`/`Write` sobre `KANBAN.md`: mover card para `[?]` sem artefato de review existente é bloqueado. Gate no **conteúdo do diff**, não em quem chamou. Camada 2 do roadmap#1. ⚠️ Verificar antes: o payload do hook distingue subagente da sessão principal? Se não, "só o Manager move cards" não é enforçável como o parecer supõe.
- [ ] `T-004` Workflows determinísticos em JS — 3 separados (plan-card / implement-card / finalize-card), nunca um só: workflow não aceita input humano no meio e há gate do dono entre as etapas. Roadmap#2. Só depois do T-003 — workflow sobre fluxo que ainda vai mudar é retrabalho garantido.
- [ ] `T-005` Worktree obrigatório em card que escreve — hoje é instrução (`isolation: "worktree"`), não imposição. Roadmap#5.
- [ ] `T-006` Implementação noturna limitada — só cards pré-aprovados, worktree próprio, commit local no máximo, sem merge/push/deploy. Roadmap#3. **Bloqueado por T-001 e T-003.**
- [ ] `T-007` Mais revisores no painel (Kimi K2) — slot já existe no `_elenco.md`. Roadmap#4. **Bloqueado:** sem CLI e sem MCP nesta máquina.

---

## ✅ Feito

_(vazio — o board nasceu em 2026-07-26)_

---

## 📦 Arquivado

_(nada abaixo desta linha conta no progresso da statusline)_
