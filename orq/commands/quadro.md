---
description: Mostra o board do projeto — o que está sendo feito, o que espera você, o backlog e o progresso
argument-hint: "[backlog | fazendo | validar | feito | esperando]"
---

## Board canônico — regra operacional

Antes de qualquer uso, comprove `ORQ_PACKAGE_ROOT` absoluto, existente e com `scripts/kanban-status.sh` disponível.
Antes de ler ou mover card, resolva `BOARD_CANONICO` com
`sh "${ORQ_PACKAGE_ROOT}/scripts/kanban-status.sh" --resolver .` na frente atual, sem `cd` para o principal. Decodifique o JSON inteiro (nunca
por linhas): use somente o caminho `board` retornado. `state: erro` interrompe a operação — não use
um `memory/wiki/KANBAN.md` local como fallback — e `exists: false` significa projeto sem board.
Se a chamada tiver `exit != 0`, stdout vazio, JSON inválido, `state` diferente de `ok`, `exists` não booleano, ou `board`/`thread_root` ausentes ou não absolutos, trate como `state: erro`, declare indisponível e não use cópia local. Sem JSON, informe `exit` e `stderr`; com JSON de erro, informe `code`.
THREAD_ROOT é o `thread_root` absoluto devolvido pelo resolver: `memory/wiki` da raiz do projeto/worktree que iniciou a operação, nunca do `BOARD_CANONICO`. O ponteiro `threads/...` do card só identifica a thread: leia/escreva exclusivamente `THREAD_ROOT/threads/...`. Somente a frente dona pode criar a thread: ela criou o card agora, ou, para card legado do BACKLOG sem ponteiro/thread, o reivindica e marca com `@frente-<slug>`. Card já marcado para outra frente, ou card existente com ponteiro cuja thread falta em `THREAD_ROOT`, deve parar: não crie, duplique, troque de frente nem use fallback.

Leia o `BOARD_CANONICO` e **apresente o board de forma escaneável**. Se `$ARGUMENTS` indicar uma
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
- Card com thread própria em `THREAD_ROOT/threads/` → cite o "RETOMAR AQUI" dela.
- Feche com **uma linha** dizendo qual é o próximo passo mais útil agora.
- Sem `BOARD_CANONICO` existente? Diga e ofereça `/orq:init`.
