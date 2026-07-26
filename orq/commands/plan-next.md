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
Spawn **fresco** do agente `orq-planner`. **Antes de spawnar, leia `memory/wiki/_elenco.md`** e passe
o modelo do papel `planner` como override (o `model:` do arquivo do agente é só o padrão de fábrica).
Sem elenco, use o padrão.

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
