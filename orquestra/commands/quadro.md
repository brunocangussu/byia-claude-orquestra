---
description: Mostra o board do projeto — o que está sendo feito, o que espera você, o backlog e o progresso
argument-hint: "[backlog | fazendo | validar | feito | esperando]"
---

Leia `memory/wiki/KANBAN.md` e **apresente o board de forma escaneável**. Se `$ARGUMENTS` indicar uma
coluna, mostre só ela (e o total das outras em uma linha).

Ordem de apresentação — do mais acionável pro menos:

1. **Cabeçalho:** `📋 X% concluído (feitos/total)` + quantos aguardam validação.
2. **⏸️ Esperando você** (`[!]` AWAITING_OWNER) — **primeiro de tudo**, porque é o que trava a fila.
   Para cada um: a **pergunta exata** e sua recomendação.
3. **🟡 Fazendo** (`[>]` planejando / `[~]` implementando) — com a trava de cada um, se houver.
4. **🟣 Validar** (`[?]`) — e **o que exatamente** você precisa testar em cada um.
5. **🔵 Backlog** (`[ ]`) — 🔴 primeiro, depois o resto.
6. **✅ Feito** (`[x]`) — só contagem e títulos (detalhe apenas se o filtro pedir `feito`).

Regras:
- IDs (`T-NNN`) sempre visíveis — o dono usa o ID pra falar do item.
- **Não** despeje o markdown cru: sintetize e formate.
- Card com thread própria em `memory/wiki/threads/` → cite o "RETOMAR AQUI" dela.
- Feche com **uma linha** dizendo qual é o próximo passo mais útil agora.
- Sem `memory/wiki/KANBAN.md`? Diga e ofereça `/orquestra:init`.
