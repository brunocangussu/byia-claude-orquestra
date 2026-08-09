---
description: Loop A — pega o próximo card do backlog, planeja com o Planner e traz o plano para sua aprovação
argument-hint: "[T-NNN para escolher um card específico, ou descrição de uma tarefa nova]"
---

Você é o **Manager** (leia a skill `orq`). Rode o **Loop A — Planejamento**.

## 1. Escolher o card
- `$ARGUMENTS` com `T-NNN` → esse card.
- `$ARGUMENTS` com texto livre → **crie** o card no BACKLOG primeiro (ID novo) e planeje ele.
- Vazio → o primeiro `[ ]` do BACKLOG (respeitando 🔴 e a ordem).
- Nada no backlog → diga isso e ofereça criar um card. **Não invente trabalho.**

Marque o card como `[>]` PLANNING no `memory/wiki/KANBAN.md`.

## 2. Despachar o Planner

Antes de despachar, **identifique o host** da sessão atual: Claude, Codex ou Kimi. Leia
`memory/wiki/_elenco.md`, resolva a linha `planner` em `## Times por host` e só então aplique a
célula vendor×host de `## Matriz de invocação`. Sem elenco, use o template de fábrica completo de
`ORQ_PACKAGE_ROOT/commands/elenco.md` — a skill já precisa ter resolvido `ORQ_PACKAGE_ROOT` para o
host atual; não improvise um modelo a partir da tabela do host Claude.

- **Host Claude:** spawn **fresco** do agente `orq-planner`, com o modelo resolvido como override.
- **Host Codex:** use o modelo/effort da linha `planner` em `## Times por host` e copie o comando da
  célula OpenAI×Codex da Matriz, com sandbox `read-only`. `codex exec` é o caminho padrão; só use a
  primitiva nativa se o `_elenco.md` registrar que o override foi comprovado por chamada real.
- **Host Kimi:** siga a célula Moonshot×Kimi da Matriz e mantenha o papel read-only.

Modelo, CLI ou override indisponível → não troque de modelo em silêncio. Mantenha o card em
PLANNING, registre a capacidade ausente e peça ao dono a escolha do fallback.

No prompt, inclua:
- o card (ID, título, notas) e **por que ele existe**;
- os arquivos-âncora e páginas de wiki relevantes que você já conhece — poupa a investigação dele;
- restrições do projeto (build, testes, o que quebra deploy, o que é intocável);
- o que **não** está no escopo;
- **exigência de handoff**: o plano precisa terminar com passos verificáveis, riscos, critério de
  aceite e as decisões que precisam de você.

## 3. Receber e avaliar
Quando o plano voltar, **não repasse cru**. Avalie:
- resolve a causa raiz ou só o sintoma?
- o escopo tem borda, ou virou reforma geral?
- os critérios de aceite são verificáveis?
- há suposição não verificada?

Se estiver fraco, **devolva ao Planner com o apontamento** antes de levar ao dono.

## 4. Levar ao dono (o gate)
Apresente **condensado** (o plano completo fica no arquivo):
- o que será feito e por quê, em linguagem direta;
- o que muda pro usuário do produto;
- riscos e o que pode quebrar;
- **as decisões que precisam dele** — numeradas, com sua recomendação em cada uma.

Se a mudança for **visual**, o plano precisa vir com mockup antes da aprovação.

**PARE aqui.** Plano não aprovado não vira implementação.

## 5. Fechar o loop
- Aprovado → grave o caminho do plano no card, marque `[~]` READY, defina o responsável.
- Precisa de mais informação → `[!]` AWAITING_OWNER **com a pergunta exata escrita no card**.
- Rejeitado → volta a `[ ]` BACKLOG com o motivo registrado (pra não repetir o erro depois).

Termine dizendo qual é o próximo passo concreto (normalmente `/orq:implement-next`).
